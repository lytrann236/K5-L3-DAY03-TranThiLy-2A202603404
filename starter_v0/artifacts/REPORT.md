# Báo cáo Research Agent

## Thông tin nhóm

- Team:TRANTHILY
- Nhà cung cấp/model: Gemini / `gemini-3.5-flash`.
- **Thành viên nhóm:**

  | STT | Họ và tên | Mã sinh viên |
  |---|---|---|
  | 1 | Trần Thị Lý | 2A202603404 |
  | 2 | Nguyễn Thị Hương Giang | 2A202603538 |
  | 3 | Nguyễn Thuỳ Dương | 2A202603388 |
  | 4 | Nguyễn Quỳnh Trang | 2A202603477 |

# PHẦN A — Giới thiệu agent

## A1. Khả năng của agent

Trợ lý nghiên cứu hỗ trợ tìm tin tức trên web, tìm bài đăng trên X, đọc nội dung từ URL và trình bày dữ liệu thành bản tin tổng hợp.

Tool mới `deduplicate` loại các bài viết có URL trùng nhau trong danh sách được cung cấp, không cần API key.

Giao diện được xây dựng bằng Streamlit tại `app.py`, chạy cục bộ ở địa chỉ `http://localhost:8501`. Link demo công khai: chưa triển khai. Hướng dẫn khởi chạy nằm trong `UI-README.md`.

## A2. Các tool của agent

| Tool | Chức năng | Tool mới tự thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu thông tin hoặc cần xác nhận | Không |
| timeline | Lấy bài đăng gần đây của một tài khoản cụ thể | Không |
| social_search | Tìm bài đăng trên mạng xã hội theo chủ đề | Không |
| lookup | Tìm kiếm thông tin và tin tức trên web | Không |
| fetch | Đọc nội dung từ một URL cụ thể | Không |
| format | Trình bày dữ liệu đã thu thập thành bản tin | Không |
| deduplicate | Giữ bài đầu tiên cho mỗi URL giống nhau sau khi bỏ khoảng trắng ở hai đầu | Có |
| send | Gửi lên Telegram; cần cấu hình và xác nhận | Không |
| policy | Tìm kiếm trong tài liệu chính sách nội bộ | Không |
| papers | Tìm bài báo khoa học trên arXiv | Không |
| paper_text | Trích xuất văn bản từ một bài báo arXiv | Không |

Tool `stock_quote` được nhóm bổ sung trên nhánh `main` và giữ lại sau khi hợp nhất; xem phần cuối báo cáo. Giao diện v1–v3 sử dụng cấu hình lịch sử, chưa bao gồm `deduplicate` hoặc `stock_quote`.

## A3. Câu hỏi mẫu để thử

1. Lấy 2 bài đăng mới nhất của karpathy.
2. Đọc bài viết tại `https://example.com/research`.
3. Loại URL trùng trong danh sách: `[{"url":"https://example.com/a"},{"url":"https://example.com/a"}]`.
4. Trình bày các bài viết đã cung cấp thành danh sách gạch đầu dòng.

Yêu cầu số 3 dùng để thử cấu hình có tool `deduplicate`, không áp dụng cho các cấu hình lịch sử v1–v3 trên UI.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Bằng chứng theo phiên bản

Nguồn: `artifacts/version_log.csv` và các file JSON kết quả chạy Gemini v0–v3 trong `runs/`.

| Phiên bản | Case đúng | Độ chính xác toàn case | Độ chính xác chọn tool | Độ chính xác nhiều lượt |
|---|---:|---:|---:|---:|
| v0 | 11/20 | 55% | 65% | 83.33% |
| v1 | 11/20 | 55% | 60% | 66.67% |
| v2 | 13/20 | 65% | 75% | 83.33% |
| v3 | 14/20 | 70% | 85% | 83.33% |

- **v1:** thay việc tự đoán bằng hỏi lại khi thiếu thông tin. R10 và R11 đạt, nhưng agent hỏi lại quá mức ở các yêu cầu đã nêu rõ tên người. Điểm tổng vẫn là 55%.
- **v2:** phân biệt đối tượng chưa được cung cấp hoặc còn mơ hồ với người đã được xác định rõ. Độ chính xác tăng lên 65%.
- **v3:** yêu cầu xác nhận trước khi gửi. R12 đã gọi `clarify` thay vì `send`, nhưng dùng `text` thay vì `yes_no`, nên case này vẫn chưa đạt. Điểm tổng 70% chưa chứng minh giả thuyết về xác nhận đã thành công.
- Việc thêm `deduplicate` làm thay đổi `tools.yaml` sau v3. Bộ eval của nhóm chạy với nhãn `v4-deduplicate`; điểm base của v3 không phải kết quả đo của bộ tool đã mở rộng.

## B2. Các lỗi còn lại ở v3

- `R03_web_news_routing`: `wrong_tool`; tham số `query` yêu cầu `AI`, thực tế là `latest AI news highlights`.
- `R08_out_of_scope`: `out_of_scope`; yêu cầu không gọi tool nhưng agent vẫn gọi.
- `R09_no_tool_capability`: `unnecessary_tool`; yêu cầu không gọi tool nhưng agent vẫn gọi.
- `R12_confirm_before_send`: `wrong_boundary`; `response_type` yêu cầu `yes_no`, thực tế là `text`.
- `R13_parallel_web_and_tweets`: `wrong_tool`; `query` yêu cầu `AI`, thực tế là `AI news`; thiếu lời gọi `social_search`.
- `M02_carryover_timeframe`: `wrong_arg_value`; `query` yêu cầu `robotics`, thực tế là `robotics news`.

## B3. Bộ eval của nhóm

File `data/eval_group.json` có 10 case, gồm đúng 5 case một lượt và 5 case nhiều lượt.

Các nội dung được kiểm tra: chọn tool mới, thiếu URL, số lượng kết quả, cách sắp xếp bài đăng, định dạng dữ liệu đã có, sửa tài khoản, giữ URL qua nhiều lượt, sửa cách sắp xếp, giữ danh sách bài viết và sửa mẫu trình bày.

Kết quả: **10/10 case đạt**; độ chính xác toàn case, chọn tool, tham số và nhiều lượt đều là 100%; không có lỗi nhà cung cấp.

Bằng chứng: `runs/v4-deduplicate_B_group_gemini_20261110T112216163771.json`.

Đây là bộ dữ liệu riêng của nhóm, không thể so sánh trực tiếp điểm 100% này với điểm 70% của bộ base.

## B4. Bằng chứng chat

Đã chạy demo CLI qua API thật với 3 đầu vào theo kịch bản; đây không phải phiên tương tác trực tiếp do người dùng nhập từng lượt.

Bằng chứng: `transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json`.

| Lượt | Yêu cầu | Tool thực tế | Trạng thái |
|---|---|---|---|
| 1 | Tóm tắt bài viết nhưng chưa cung cấp URL | clarify | Chờ người dùng (`waiting_for_user`) |
| 2 | Cung cấp `https://example.com` | fetch | Đã trả lời (`answered`) |
| 3 | Loại URL trùng trong danh sách hai bài viết | deduplicate | Đã trả lời (`answered`) |

Demo sử dụng Gemini thật và đọc trang bằng Firecrawl thật, không dùng kết quả giả lập. Các kiểm tra tương tác UI tự động đã đạt. Cần tiếp tục diễn tập demo với người dùng và triển khai link công khai.

## B5. Triển khai và kiểm thử đơn vị

- Tool mới nằm tại `tools/deduplicate/tool.py`, có `TOOL.md`, đăng ký trong danh sách tool và khai báo schema.
- Có 14 trường hợp kiểm thử cho tool mới: loại trùng, giữ thông tin và thứ tự, không sửa đầu vào, giữ các URL khác nhau, danh sách rỗng và đầu vào không hợp lệ.
- Phát hiện lỗi trong bộ chấm: `normalize_value` sắp xếp trực tiếp các dictionary, gây `TypeError` với mảng `items`. Đã sửa bằng cách sắp xếp theo biểu diễn JSON xác định, giữ quy ước so sánh không phụ thuộc thứ tự vốn có. Có kiểm thử hồi quy cho việc so sánh danh sách object.
- Kết quả kiểm thử trước khi thêm chọn phiên bản và hợp nhất: **104 đạt, 0 bỏ qua, 0 lỗi**. Các test TODO của starter đã được triển khai bằng HTTP giả lập và dữ liệu chính sách cục bộ. Kết quả sau hợp nhất được ghi ở phần cuối báo cáo.
- UI tại `app.py` có lịch sử chat, chọn model, xem kết quả tool, tạo cuộc trò chuyện mới, lưu transcript và tải JSON. Kiểm tra Streamlit AppTest đã đạt cho luồng chat, lưu dữ liệu, tạo lại hội thoại và xử lý lỗi nhà cung cấp. Kiểm tra trạng thái máy chủ cục bộ trả về HTTP 200.

## B6. Nhận xét và hướng cải thiện

Quy tắc hỏi lại khi thiếu thông tin và quy tắc xác nhận nên nằm trong system prompt. Mô tả chức năng tool và quy ước tham số nên nằm trong `tools.yaml`.

R12 cần đánh giá thủ công: hỏi nội dung còn thiếu bằng `text` giúp tránh gửi ngay, nhưng bộ chấm tự động yêu cầu `yes_no`. Cần giữ rõ sự khác biệt này, không báo cáo case là thành công hoàn toàn.

Các bước tiếp theo: tạo link demo công khai, để người dùng thử hội thoại và rà soát các lỗi chọn tool/tham số còn lại.

## B7. Thử thách model nhỏ chạy cục bộ

Chưa thực hiện. Báo cáo không công bố kết quả model chạy cục bộ.

## B8. Sửa lỗi mã hóa UI trên Windows

Log chẩn đoán tool đã được chuyển sang đầu ra an toàn với ASCII; nội dung transcript vẫn giữ Unicode. Kiểm thử hồi quy với console mã hóa `cp1252` và một lượt UI gọi Gemini thật đều đạt. Khởi chạy Streamlit bằng `python -X utf8`.

## B9. Hợp nhất với nhánh main của nhóm

Đã hợp nhất commit `40d802b` trên nhánh `main`, giữ prompt/mô tả tool hiện tại của nhóm cùng phần triển khai và test `stock_quote`, đồng thời giữ `deduplicate` và UI.

Các cấu hình Gemini lịch sử và bằng chứng v3 đạt 70% được giữ riêng với kết quả OpenRouter do nhóm bổ sung trên `main`. UI v1–v3 vẫn chọn các cấu hình Gemini lịch sử.

Kết quả kiểm tra sau hợp nhất: **115 test đạt, không có test bị bỏ qua**.
