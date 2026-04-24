import fakeredis
import chromadb
import os

# --- 1. CẤU HÌNH REDIS (Sử dụng fakeredis) ---
# fakeredis sẽ tạo một server ảo chạy trên RAM.
# Không cần cài đặt phần mềm Redis, không cần Docker.
redis_client = fakeredis.FakeStrictRedis()
print("✅ Đã khởi tạo Redis (Virtual via fakeredis)")


# --- 2. CẤU HÌNH CHROMADB (Sử dụng Local Persistent) ---
# Chúng ta chọn chế độ Persistent thay vì In-memory hoàn toàn 
# để dữ liệu được lưu vào 1 thư mục, giúp bạn có thể kiểm tra dữ liệu sau khi chạy.
db_path = "./chroma_db"
if not os.path.exists(db_path):
    os.makedirs(db_path)

chroma_client = chromadb.PersistentClient(path=db_path)
print(f"✅ Đã khởi tạo ChromaDB tại thư mục: {db_path}")

# Tạo hoặc lấy ra một collection để dùng cho Semantic Memory
# (Collection giống như một "bảng" trong database thông thường)
collection = chroma_client.get_or_create_collection(name="semantic_memory")