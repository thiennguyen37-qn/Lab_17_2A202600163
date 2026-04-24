import os
from dotenv import load_dotenv
from openai import OpenAI
from memory_backends import MemoryManager

load_dotenv()

class MemoryRouter:
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
        # 1. Khởi tạo client kết nối tới NVIDIA API
        self.client = OpenAI(
            api_key=os.environ.get("NVIDIA_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )
        
        # 2. Khai báo model NVIDIA bạn muốn dùng 
        self.model_name = "openai/gpt-oss-120b"

    def classify_intent(self, user_query: str) -> str:
        """Sử dụng LLM (NVIDIA) để phân loại câu hỏi của user thành 1 trong 4 loại"""
        
        # Viết prompt dạng string thông thường
        prompt = f"""
        Bạn là một trợ lý ảo thông minh. Nhiệm vụ của bạn là phân tích câu hỏi của người dùng 
        và phân loại nó vào MỘT trong 4 danh mục sau. CHỈ trả về đúng 1 từ tiếng Anh đại diện cho danh mục, không giải thích gì thêm.

        Danh mục:
        1. PREFERENCE: Người dùng hỏi về sở thích cá nhân, thông tin profile của họ (VD: Tôi thích màu gì? Tên tôi là gì?).
        2. FACTUAL: Người dùng hỏi về kiến thức chung, sự thật, hoặc thông tin đã học (VD: Công thức tính diện tích là gì? Thủ đô nước nào?).
        3. EPISODIC: Người dùng hỏi về các sự kiện trong quá khứ, tóm tắt các cuộc trò chuyện trước đây (VD: Hôm trước chúng ta đã bàn về gì? Lần trước tôi hỏi gì?).
        4. GENERAL: Câu chào hỏi bình thường hoặc câu hỏi không cần tra cứu lịch sử (VD: Xin chào! Thời tiết hôm nay thế nào?).

        Câu hỏi của người dùng: {user_query}
        Phân loại (chỉ 1 từ):
        """
        
        # Gọi trực tiếp qua client của OpenAI
        # Gọi trực tiếp qua client của OpenAI (NVIDIA API)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "Bạn là một AI phân loại dữ liệu. Chỉ trả về 1 từ duy nhất."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100 # Tăng nhẹ token lên để tránh model bị ngắt ngang
        )
        
        # --- ĐOẠN CODE FIX LỖI NONETYPE ---
        raw_content = response.choices[0].message.content
        
        # Nếu API trả về rỗng, mặc định là GENERAL
        if raw_content is None:
            print("[Cảnh báo] API trả về None. Tự động chuyển về GENERAL.")
            intent = "GENERAL"
        else:
            intent = raw_content.strip().upper()
        
        # Rà soát lại kết quả cho an toàn
        if "PREFERENCE" in intent: intent = "PREFERENCE"
        elif "FACTUAL" in intent: intent = "FACTUAL"
        elif "EPISODIC" in intent: intent = "EPISODIC"
        else: intent = "GENERAL" 
            
        return intent

    def retrieve_memory(self, user_query: str):
        """Dựa vào Intent để gọi đúng loại Memory Backend"""
        
        intent = self.classify_intent(user_query)
        retrieved_data = None
        
        print(f"[Router] Đã nhận diện Intent: {intent}")
        
        if intent == "PREFERENCE":
            # Tạm thời fix cứng key 'favorite_color' để test. 
            retrieved_data = self.memory.get_preference("favorite_color") 
            
        elif intent == "FACTUAL":
            retrieved_data = self.memory.search_knowledge(user_query)
            
        elif intent == "EPISODIC":
            episodes = self.memory.get_past_episodes()
            if episodes:
                retrieved_data = episodes[-1]['summary']
            else:
                retrieved_data = "Chưa có lịch sử phiên làm việc nào."
                
        elif intent == "GENERAL":
            retrieved_data = "Không cần truy xuất bộ nhớ dài hạn."

        return {
            "intent": intent,
            "data": retrieved_data
        }

# if __name__ == "__main__":
#     # Test thử
#     memory = MemoryManager()
#     router = MemoryRouter(memory)
    
#     test_queries = [
#         "Xin chào, dạo này bạn khỏe không?", 
#         "Hôm trước chúng ta đã nói chuyện về chủ đề gì nhỉ?",
#         "Bạn có nhớ tôi thích màu gì không?",
#         "Làm sao để tính diện tích hình chữ nhật?"
#     ]
    
#     for q in test_queries:
#         print(f"\n👤 User: {q}")
#         result = router.retrieve_memory(q)
#         print(f"💾 Dữ liệu truy xuất được: {result['data']}")