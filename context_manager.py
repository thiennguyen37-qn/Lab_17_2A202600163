import tiktoken

class ContextManager:
    def __init__(self, max_tokens=1000):
        # Đặt giới hạn token (1000 cho ví dụ lab này, thực tế có thể là 4000-8000)
        self.max_tokens = max_tokens
        
        # Sử dụng tokenizer chuẩn để đếm (chỉ mang tính ước lượng cho các model Non-OpenAI)
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Hàm đếm số lượng token của một đoạn văn bản"""
        return len(self.encoding.encode(str(text)))

    def build_context(self, system_prompt: str, current_query: str, 
                      short_term_history: list, retrieved_memory: str) -> str:
        """
        Xây dựng prompt cuối cùng. Cắt tỉa theo thứ tự ưu tiên:
        Level 1 (Ưu tiên cao nhất): System Prompt + Câu hỏi hiện tại (Không bao giờ xóa)
        Level 2: Short-term history (Lịch sử chat gần nhất)
        Level 3 (Ưu tiên thấp nhất): Thông tin truy xuất từ Router (Retrieved Memory)
        """
        
        # 1. Tính toán Token cho Level 1 (Bắt buộc phải giữ)
        level_1_text = f"SYSTEM: {system_prompt}\nUSER: {current_query}\n"
        level_1_tokens = self.count_tokens(level_1_text)
        
        # Quỹ token còn lại cho các bộ nhớ
        available_tokens = self.max_tokens - level_1_tokens
        
        # 2. Xử lý Level 2: Short-term history
        # (Chuyển list message thành chuỗi text)
        history_text = "\n".join([f"{msg.type}: {msg.content}" for msg in short_term_history])
        history_tokens = self.count_tokens(history_text)
        
        # 3. Xử lý Level 3: Retrieved Memory (Data từ Chroma/Redis/JSON)
        memory_text = f"MEMORY CONTEXT: {retrieved_memory}\n"
        memory_tokens = self.count_tokens(memory_text)
        
        # --- THUẬT TOÁN CẮT TỈA (AUTO-TRIM) ---
        final_memory = memory_text
        final_history = history_text
        
        total_needed = history_tokens + memory_tokens
        
        if total_needed > available_tokens:
            print(f"[Cảnh báo Token] Vượt ngưỡng {self.max_tokens}. Bắt đầu cắt tỉa...")
            
            # Bước cắt 1: Ưu tiên hi sinh Retrieved Memory (Level 3) trước
            if history_tokens <= available_tokens:
                # Giữ nguyên history, cắt bớt memory
                final_memory = "MEMORY CONTEXT: [Đã bị cắt bỏ do giới hạn token]\n"
            else:
                # Bước cắt 2: Nếu chỉ riêng history đã vượt quá, cắt cả memory và lấy 1 phần history
                final_memory = "MEMORY CONTEXT: [Đã bị cắt bỏ]\n"
                final_history = "[Lịch sử hội thoại đã bị rút ngắn]\n" 
                # (Ở bản nâng cao, bạn có thể cắt list message dần từ cũ đến mới, 
                # ở đây ta làm đơn giản cho Lab)
                
        # --- RÁP LẠI PROMPT CUỐI CÙNG ---
        final_prompt = f"""
{system_prompt}

{final_memory}
--- Lịch sử hội thoại gần nhất ---
{final_history}
----------------------------------
Người dùng: {current_query}
Trợ lý AI:
"""
        return final_prompt

# if __name__ == "__main__":
#     # Test thử thuật toán cắt tỉa
#     manager = ContextManager(max_tokens=100) # Cố tình đặt mốc cực thấp (100) để ép nó phải cắt
    
#     # Tạo dữ liệu giả
#     from collections import namedtuple
#     Msg = namedtuple('Msg', ['type', 'content'])
#     fake_history = [Msg("Human", "Chào bạn"), Msg("AI", "Xin chào!")]
#     fake_memory = "Đây là một đoạn kiến thức rất dài từ ChromaDB..." * 20
    
#     prompt = manager.build_context(
#         system_prompt="Bạn là trợ lý ảo.",
#         current_query="Bạn có nhớ tên tôi không?",
#         short_term_history=fake_history,
#         retrieved_memory=fake_memory
#     )
    
#     print(prompt)