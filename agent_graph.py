import os
import json
from typing import TypedDict
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

from memory_backends import MemoryManager
from memory_router import MemoryRouter
from context_manager import ContextManager

load_dotenv()

class MemoryState(TypedDict):
    messages: list          
    user_profile: dict      
    episodes: list          
    semantic_hits: list     
    memory_budget: int      
    user_input: str
    response: str

memory_manager = MemoryManager()
memory_router = MemoryRouter(memory_manager)
context_manager = ContextManager(max_tokens=4000)
client = OpenAI(
    api_key=os.environ.get("NVIDIA_API_KEY"),
    base_url="https://integrate.api.nvidia.com/v1"
)
MODEL_NAME = "openai/gpt-oss-120b" 

# ==========================================
# THÊM MỚI: HÀM TRÍCH XUẤT VÀ XỬ LÝ XUNG ĐỘT
# ==========================================
def extract_and_update_profile(user_input: str):
    """
    Dùng LLM để "đọc" xem user có đang cung cấp thông tin cá nhân không.
    Nếu user đính chính (conflict), LLM sẽ trả về giá trị mới nhất.
    """
    system_prompt = """
    Bạn là một hệ thống trích xuất dữ liệu cá nhân. 
    Nhiệm vụ: Đọc câu của người dùng. Nếu họ nói về sở thích, đặc điểm cá nhân, hoặc đính chính thông tin (ví dụ: dị ứng, màu yêu thích...), hãy trích xuất dưới định dạng JSON: {"key": "tên_đặc_điểm_bằng_tiếng_anh", "value": "giá_trị"}. 
    Nếu họ đính chính, hãy lấy giá trị MỚI NHẤT.
    Nếu không có thông tin cá nhân nào, CHỈ trả về chữ: NONE.
    KHÔNG trả về gì khác ngoài JSON hoặc NONE.
    """
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User nói: '{user_input}'"}
        ],
        temperature=0,
        max_tokens=100
    )
    
    content = response.choices[0].message.content
    if content and content.strip() != "NONE":
        try:
            # Tìm và parse JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                data = json.loads(content[start:end])
                key = data.get("key")
                value = data.get("value")
                if key and value:
                    # Ghi đè vào Redis (Giải quyết mâu thuẫn)
                    memory_manager.save_preference(key, value)
                    print(f"💾 [Auto-Update Profile] Đã cập nhật/ghi đè: {key} = {value}")
        except json.JSONDecodeError:
            pass

# ==========================================
# CÁC NODES (HÀNH ĐỘNG CỦA GRAPH)
# ==========================================

def retrieve_node(state: MemoryState):
    user_input = state["user_input"]
    
    # 1. Tự động kiểm tra và cập nhật Profile trước
    extract_and_update_profile(user_input)
    
    # 2. Kéo dữ liệu vào State
    new_state = {
        "messages": memory_manager.get_short_term_context(),
        "user_profile": {"retrieved_info": memory_manager.get_preference("*")}, # Kéo toàn bộ profile ra
        "episodes": [],
        "semantic_hits": [],
        "memory_budget": context_manager.max_tokens
    }
    
    router_result = memory_router.retrieve_memory(user_input)
    intent = router_result["intent"]
    data = router_result["data"]
    
    if intent == "EPISODIC" and data:
        new_state["episodes"] = [{"summary": data}]
    elif intent == "FACTUAL" and data:
        new_state["semantic_hits"] = [data]
        
    return new_state

def generate_node(state: MemoryState):
    user_input = state["user_input"]
    
    memory_injection = f"""
[USER PROFILE (Long-term)]: {state['user_profile'] if state['user_profile'] else 'None'}
[EPISODIC MEMORY (Past events)]: {state['episodes'] if state['episodes'] else 'None'}
[SEMANTIC KNOWLEDGE (Facts)]: {state['semantic_hits'] if state['semantic_hits'] else 'None'}
"""
    
    system_prompt = "Bạn là trợ lý AI thông minh. Hãy sử dụng các bộ nhớ được cung cấp để trả lời người dùng một cách tự nhiên."
    
    final_prompt = context_manager.build_context(
        system_prompt=system_prompt,
        current_query=user_input,
        short_term_history=state["messages"],
        retrieved_memory=memory_injection
    )
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": final_prompt}],
        temperature=0.7,
        max_tokens=500
    )
    
    ai_response = response.choices[0].message.content
    if ai_response is None:
        ai_response = "Xin lỗi, tôi gặp chút vấn đề khi kết nối."
        
    memory_manager.add_short_term(user_input, ai_response)
    
    # Ghi Episodic Memory nếu AI nhận diện hoàn thành task (Ví dụ đơn giản: khi cung cấp xong Factual)
    if state['semantic_hits']:
        memory_manager.log_episode(f"Đã giải đáp thông tin cho user về: {user_input}")
    
    return {"response": ai_response}

# ==========================================
# LẮP RÁP GRAPH VÀ CHẠY
# ==========================================
workflow = StateGraph(MemoryState)
workflow.add_node("Retrieve_Data", retrieve_node)
workflow.add_node("Generate_Answer", generate_node)
workflow.add_edge(START, "Retrieve_Data")
workflow.add_edge("Retrieve_Data", "Generate_Answer")
workflow.add_edge("Generate_Answer", END)
agent_app = workflow.compile()

if __name__ == "__main__":
    print("Agent (Full Memory Stack + Auto Update) đã khởi động!")
    while True:
        user_text = input("\n👤 Bạn: ")
        if user_text.lower() == 'exit':
            memory_manager.log_episode("User đã kết thúc phiên làm việc.")
            break
        result = agent_app.invoke({"user_input": user_text, "memory_budget": 4000})
        print(f"AI: {result['response']}")