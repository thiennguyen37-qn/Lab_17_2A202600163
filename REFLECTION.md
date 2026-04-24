## BÁO CÁO PHÂN TÍCH: PRIVACY & LIMITATIONS (REFLECTION)

### 1. Phân tích rủi ro quyền riêng tư (Privacy Risks)
Việc hệ thống hóa trí nhớ cho AI mang lại trải nghiệm cá nhân hóa nhưng đồng thời tạo ra các rủi ro về dữ liệu cá nhân (PII - Personally Identifiable Information):

**Rủi ro PII/Privacy:** Hệ thống đang lưu trữ các thông tin cực kỳ nhạy cảm như tên người dùng, sở thích, và đặc biệt là tình trạng sức khỏe (ví dụ: dị ứng đậu nành trong bài test). Nếu các file log JSON (Episodic) hoặc database Redis (Profile) không được mã hóa, kẻ tấn công có thể dễ dàng trích xuất hồ sơ cá nhân hoàn chỉnh của người dùng.

**Loại Memory nhạy cảm nhất:** Long-term Profile và Episodic Memory là hai loại nhạy cảm nhất. Trong khi Semantic memory chỉ chứa kiến thức chung, Profile và Episodic chứa "dấu vết" và đặc điểm nhận dạng của một cá nhân cụ thể.

### 2. Quản lý dữ liệu và Truy xuất (Data Management & Retrieval)
Dựa trên gợi ý về cơ chế Reflection:

- Memory giúp Agent nhiều nhất: Episodic Memory kết hợp với Short-term Memory giúp Agent duy trì sự liền mạch trong hội thoại (Contextual awareness). Tuy nhiên, Long-term Profile lại là yếu tố tạo nên sự khác biệt trong việc ra quyết định cá nhân hóa.

- Rủi ro khi Retrieval sai: Nếu hệ thống Semantic (ChromaDB) hoặc Profile (Redis) trả về kết quả sai (nhầm lẫn giữa người dùng này với người dùng khác), Agent có thể đưa ra lời khuyên nguy hiểm. Ví dụ: Nếu hệ thống nhớ nhầm "dị ứng đậu nành" thành "dị ứng sữa bò", AI có thể khuyến khích người dùng ăn thực phẩm chứa đậu nành, gây nguy cơ sốc phản vệ.

- Quyền được lãng quên (Deletion): Nếu người dùng yêu cầu xóa bộ nhớ, hệ thống cần thực hiện lệnh xóa tại Redis backend (xóa Key-Value profile) và JSON file backend (xóa các dòng log liên quan đến session ID của người dùng đó).

### 3. Giới hạn kỹ thuật và Khả năng mở rộng (Limitations & Scalability)
Giải pháp hiện tại có một số hạn chế kỹ thuật cần được khắc phục khi triển khai thực tế:

- Limitation về lưu trữ: Việc sử dụng fakeredis (chạy trên RAM) dẫn đến việc mất sạch dữ liệu Profile khi server khởi động lại. Ngoài ra, lưu trữ Episodic bằng file .json nội bộ sẽ gây ra tình trạng nghẽn I/O (Input/Output) khi có hàng ngàn người dùng truy cập đồng thời.

- Điểm yếu khi Scale (Mở rộng):

    - Chi phí API: Cơ chế Auto-Extractor (dùng LLM để trích xuất profile mỗi khi user chat) rất tốn kém và làm tăng độ trễ (latency) của hệ thống.

    - Quản lý Vector Store: Khi dữ liệu Semantic lên đến hàng triệu chunk, việc tìm kiếm vector cần các giải pháp chuyên dụng như Pinecone hoặc Milvus thay vì lưu cục bộ bằng ChromaDB để đảm bảo tốc độ.

    - Token Budget: Thuật toán cắt tỉa (Trim) hiện tại chỉ dựa trên số lượng tin nhắn đơn giản, chưa tối ưu hóa để giữ lại các thông tin quan trọng nhất trong những chuỗi hội thoại cực dài.
