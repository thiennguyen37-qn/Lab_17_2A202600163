import json
import os
from datetime import datetime
from langchain_classic.memory.buffer import ConversationBufferMemory

# Import các client từ file config.py của Giai đoạn 1
from config import redis_client, collection

class MemoryManager:
    def __init__(self, session_id="session_01", user_id="user_001"):
        self.session_id = session_id
        self.user_id = user_id
        
        # 1. Khởi tạo Short-term Memory (LangChain)
        # return_messages=True để trả về dạng danh sách message thay vì string cục bộ
        self.short_term = ConversationBufferMemory(return_messages=True)
        
        # 4. Khởi tạo Episodic Memory (JSON Log)
        self.episodic_file = f"episodic_log_{self.user_id}.json"
        if not os.path.exists(self.episodic_file):
            with open(self.episodic_file, 'w', encoding='utf-8') as f:
                json.dump([], f) # Tạo file JSON rỗng nếu chưa có

    # ==========================================
    # 1. SHORT-TERM MEMORY METHODS
    # ==========================================
    def add_short_term(self, user_message, ai_message):
        """Lưu lượt hỏi-đáp vào bộ nhớ ngắn hạn"""
        self.short_term.save_context({"input": user_message}, {"output": ai_message})
        
    def get_short_term_context(self):
        """Lấy lịch sử hội thoại hiện tại"""
        return self.short_term.load_memory_variables({})['history']

    # ==========================================
    # 2. LONG-TERM MEMORY METHODS (Redis)
    # ==========================================
    def save_preference(self, key, value):
        """Lưu sở thích/thông tin cá nhân vào Redis. VD: key='food', value='Phở'"""
        redis_key = f"{self.user_id}:{key}"
        redis_client.set(redis_key, value)
        
    def get_preference(self, key):
        """Lấy sở thích từ Redis"""
        redis_key = f"{self.user_id}:{key}"
        value = redis_client.get(redis_key)
        return value.decode('utf-8') if value else "Không có thông tin"

    # ==========================================
    # 3. SEMANTIC MEMORY METHODS (ChromaDB)
    # ==========================================
    def save_factual_knowledge(self, fact_text, fact_id):
        """Lưu kiến thức vào ChromaDB (VD: 'Dự án AI của cty ra mắt tháng 5')"""
        collection.add(
            documents=[fact_text],
            metadatas=[{"user_id": self.user_id, "timestamp": str(datetime.now())}],
            ids=[fact_id]
        )
        
    def search_knowledge(self, query, top_k=1):
        """Tìm kiếm kiến thức liên quan dựa trên câu hỏi"""
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        # Trả về document đầu tiên tìm thấy, nếu không có trả về list rỗng
        return results['documents'][0] if results['documents'] else []

    # ==========================================
    # 4. EPISODIC MEMORY METHODS (JSON Log)
    # ==========================================
    def log_episode(self, summary):
        """Ghi tóm tắt của một phiên làm việc vào file JSON"""
        # Đọc dữ liệu cũ
        with open(self.episodic_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
            
        # Thêm log mới
        logs.append({
            "timestamp": str(datetime.now()),
            "session_id": self.session_id,
            "summary": summary
        })
        
        # Ghi đè lại file
        with open(self.episodic_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
            
    def get_past_episodes(self):
        """Lấy toàn bộ lịch sử các phiên làm việc cũ"""
        with open(self.episodic_file, 'r', encoding='utf-8') as f:
            return json.load(f)

# if __name__ == "__main__":
#     # Khởi tạo Memory Manager
#     memory = MemoryManager()

#     # Test 1: Short-term
#     memory.add_short_term("Chào bạn, mình tên là Tuấn", "Chào Tuấn, mình giúp gì được cho bạn?")
#     print("Short-term:", memory.get_short_term_context())

#     # Test 2: Long-term (Redis)
#     memory.save_preference("favorite_color", "Màu xanh dương")
#     print("Long-term (Sở thích):", memory.get_preference("favorite_color"))

#     # Test 3: Semantic (ChromaDB)
#     memory.save_factual_knowledge("Công thức tính diện tích hình chữ nhật là Dài x Rộng", "math_fact_01")
#     print("Semantic (Kiến thức):", memory.search_knowledge("Làm sao để tính diện tích hình chữ nhật?"))

#     # Test 4: Episodic (JSON)
#     memory.log_episode("User hỏi về toán học và cách thiết lập bộ nhớ.")
#     print("Episodic (Log):", memory.get_past_episodes())