# BÁO CÁO BENCHMARK

| # | Scenario | Group | No-memory | With-memory | Pass |
|---|---|---|---|---|---|
| 1 | Recall user name after turns | Profile Recall | Có, tên bạn là Tuấn. | Chắc chắn rồi, anh Tuấn! 😄   Có việc gì mình có thể hỗ trợ t... | ✅ Pass |
| 2 | Allergy conflict update | Conflict update | Bạn bị dị ứng với đậu nành. | **Tóm lại:** Bạn **không phải dị ứng sữa bò** mà **dị ứng đậ... | ✅ Pass |
| 3 | Update living location | Conflict update | Bạn hiện đang ở Hà Nội. | Bạn hiện đang ở **Hà Nội** ạ. 🎉   Nếu cần gợi ý địa điểm yên... | ❌ Fail |
| 4 | Recall favorite food | Profile Recall | Bạn có thể thử **bún chả** – món ăn truyền thống mà bạn yêu ... | Chào bạn! 🌞   Dựa trên những gì bạn vừa chia sẻ (bún chả là ... | ❌ Fail |
| 5 | Recall previous debug lesson | Episodic Recall | Bạn đã khắc phục lỗi Docker bằng cách **đổi cổng (port) sử d... | Bạn đã **đổi cổng (port) mà Docker đang publish** để tránh x... | ✅ Pass |
| 6 | Summarize past events | Episodic Recall | Bạn đã tham dự một buổi họp dự án AI vào buổi sáng. | Bạn vừa chia sẻ rằng sáng nay mình đã **đi họp dự án AI**.  ... | ✅ Pass |
| 7 | Retrieve FAQ chunk | Semantic Retrieval | Công thức: **Diện tích = chiều dài × chiều rộng** ( \(A = a ... | Đúng rồi, công thức tính diện tích của một hình chữ nhật rất... | ❌ Fail |
| 8 | Retrieve specific fact | Semantic Retrieval | Thủ đô của Pháp là Paris. | Thủ đô của nước Pháp là **Paris**. Đây là thành phố lớn nhất... | ✅ Pass |
| 9 | Token Budget / Trim | Trim/Token budget | Đúng, tôi đã thấy đoạn văn bản rất dài và chứa nhiều từ “spa... | Đúng vậy, bạn vừa gửi cho mình một đoạn văn rất dài chỉ chứa... | ✅ Pass |
| 10 | Cross-memory reasoning | Mixed (Profile + Factual) | Bạn nên chọn trà đá, vì sữa đậu nành có thể gây phản ứng dị ... | Chào bạn! 😊    Với **dị ứng đậu nành**, việc tránh mọi sản p... | ✅ Pass |
