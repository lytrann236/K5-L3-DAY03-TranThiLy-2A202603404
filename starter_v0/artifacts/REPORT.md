# Báo cáo Research Agent — Day 03 Lab v2

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

## A1. Agent làm được gì và link dùng thử

Agent tìm tin tức web và bài đăng X, đọc URL, lọc các bài trùng URL và trình bày bản tin có nguồn. Khi thiếu thông tin, agent hỏi lại thay vì tự chọn một tài khoản hoặc bài viết.

**Link demo:** https://groups-teams-veterinary-citysearch.trycloudflare.com

Đã kiểm tra trang chính và `/_stcore/health` qua link công khai: HTTP 200; kết nối WebSocket của Streamlit qua tunnel cũng thành công. Đây là link Cloudflare Tunnel tạm thời, chỉ hoạt động khi máy chủ Streamlit và tiến trình tunnel còn chạy. Link cục bộ: http://localhost:8501. Hướng dẫn khởi chạy lại: `UI-README.md`.

UI chỉ có v1, v2, v3. V1 và v2 dùng cấu hình lịch sử; v3 dùng bản hoàn thiện với 12 tool khai báo. UI không cung cấp hành động gửi Telegram nên có 11 tool thực thi được từ lựa chọn v3. Transcript ghi nhãn `v3-final` và hash thực tế để phân biệt với v3 lịch sử.

## A2. Các tool

| Tool | Chức năng | Nguồn |
|---|---|---|
| clarify | Hỏi thông tin còn thiếu hoặc xin xác nhận | Có sẵn |
| timeline | Lấy bài đăng gần đây của tài khoản X | Có sẵn |
| social_search | Tìm bài đăng X theo chủ đề, Top hoặc Latest | Có sẵn |
| lookup | Tìm web và tin tức theo khoảng thời gian | Có sẵn |
| fetch | Đọc nội dung một URL | Có sẵn |
| format | Trình bày dữ liệu đã có thành bản tin | Có sẵn |
| send | Gửi Telegram khi có cấu hình và xác nhận; chỉ dùng qua CLI | Có sẵn |
| policy | Tìm chính sách nội bộ | Có sẵn |
| papers | Tìm bài báo arXiv | Có sẵn |
| paper_text | Trích văn bản bài báo arXiv | Có sẵn |
| deduplicate | Giữ bài đầu tiên cho mỗi URL trùng, giữ thứ tự | Nguyễn Thuỳ Dương bổ sung |
| stock_quote | Trả dữ liệu cổ phiếu minh họa cố định cho AAPL, NVDA, VHM; không phải giá hiện tại | Nhóm bổ sung trên main |

## A3. Câu hỏi mẫu

1. Lấy 2 bài mới nhất của karpathy.
2. Tin AI hôm nay có gì nổi bật?
3. Tóm tắt bài này: https://example.com
4. Loại URL trùng, giữ bài đầu tiên: `[{"title":"A","url":"https://example.com/a"},{"title":"B","url":"https://example.com/a"}]`.
5. Cho tôi dữ liệu cổ phiếu minh họa của mã AAPL, không cần giá hiện tại.

# PHẦN B — Chi tiết / Bằng chứng

## B1. Phiên bản và kết quả thực tế

V0–v3 lịch sử dùng cùng model Gemini. Mỗi vòng tối ưu v1–v3 kiểm chứng một giả thuyết; các bản gốc được giữ trong `artifacts/versions/`. Bản `v3-final` là vòng tích hợp nhiều sửa đổi sau đó, không thay thế hay viết lại kết quả lịch sử.

| Phiên bản | Thay đổi / giả thuyết | Điểm trước | Điểm sau | File bằng chứng |
|---|---|---:|---:|---|
| v0 | Baseline chưa tối ưu | — | 55% | `runs/v0_B_base_gemini_20261110T102151789910.json` |
| v1 | Hỏi lại khi thiếu handle/URL thay vì đoán | 55% | 55% | `runs/v1_B_base_gemini_20261110T104455968698.json` |
| v2 | Chỉ hỏi tài khoản khi đối tượng thiếu hoặc mơ hồ | 55% | 65% | `runs/v2_B_base_gemini_20261110T105314645987.json` |
| v3 | Yêu cầu xác nhận trước khi gửi | 65% | 70% | `runs/v3_B_base_gemini_20261110T105833327686.json` |
| v3-final / base | Hoàn thiện routing, nhiều tool, xác nhận và UI | 70% | 100% | `runs/v3-final_B_base_gemini_20261110T154117007662.json` |
| v3-final / group | Kiểm tra lại cùng 10 case của nhóm | 100% | 100% | `runs/v3-final_B_group_gemini_20261110T154026976389.json` |

Hash đầy đủ, tác giả, lý do và đường dẫn run được ghi trong `artifacts/version_log.csv`. Bộ base và bộ group là hai tập dữ liệu riêng; không dùng điểm group để thay cho điểm base. Các run OpenRouter được nhóm đóng góp vẫn giữ trong `runs/`, nhưng không trộn vào chuỗi so sánh Gemini này.

**Kết luận từng giả thuyết:** v1 sửa R10/R11 nhưng gây hỏi lại quá mức nên tổng điểm giữ 55%; v2 phục hồi các yêu cầu đã nêu rõ người, đạt 65%; v3 đã tránh gửi ngay nhưng R12 còn sai `response_type=text`, nên chưa chứng minh thành công giả thuyết xác nhận. Bản hoàn thiện được đo lại riêng, không suy diễn điểm từ các run trước.

## B2. Phân tích lỗi baseline v0

Các dòng sau lấy trực tiếp từ `results` của baseline Gemini; giữ mã loại lỗi của bộ chấm.

| Case | Loại lỗi | Lời gọi thực tế | Chi tiết sai | Hướng sửa |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool | [{"name": "lookup", "args": {"query": "latest AI news today", "topic": "news", "max_results": 5, "timeframe": "day"}}] | query: expected 'AI', got 'latest AI news today' | Làm rõ routing, query theo chủ đề và yêu cầu nhiều nguồn |
| R08_out_of_scope | out_of_scope | [{"name": "send", "args": {"confirmed": true, "text": "Nguyên hàm của hàm số f(x) = x^2 là:\n\n∫ x^2 dx = (x^3 / 3) + C\n\ntrong đó C là hằng số tích phân."}}] | expected no tool call | Từ chối yêu cầu ngoài phạm vi, không gọi tool |
| R09_no_tool_capability | unnecessary_tool | [{"name": "policy", "args": {"query": "vai trò và khả năng của trợ lý"}}] | expected no tool call | Trả lời câu hỏi năng lực trực tiếp |
| R10_missing_handle | missing_info | [{"name": "timeline", "args": {"limit": 5, "screenname": "sama"}}] | missing tool call clarify; extra tool call timeline | Hỏi rõ đối tượng hoặc URL |
| R11_missing_url | missing_info | [{"name": "fetch", "args": {"url": "https://openai.com/index/hello-gpt-4o/"}}] | missing tool call clarify; extra tool call fetch | Hỏi rõ đối tượng hoặc URL |
| R12_confirm_before_send | wrong_boundary | [{"name": "send", "args": {"confirmed": true, "text": "Bản tin cập nhật tin tức mới nhất trong ngày."}}] | missing tool call clarify; extra tool call send | Xin xác nhận trước gửi bằng yes_no |
| R13_parallel_web_and_tweets | wrong_tool | [{"name": "lookup", "args": {"timeframe": "day", "query": "tin tức AI mới nhất hôm nay", "topic": "news"}}] | query: expected 'AI', got 'tin tức AI mới nhất hôm nay'; missing tool call social_search | Làm rõ routing, query theo chủ đề và yêu cầu nhiều nguồn |
| R14_out_of_scope_coding | out_of_scope | [{"name": "send", "args": {"confirmed": true, "text": "Dưới đây là hàm Python tính số Fibonacci bằng phương pháp đệ quy (recursion):\n\n```python\ndef fibonacci(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    return fibonacci(n - 1) + fibonacci(n - 2)\n\n# Ví dụ sử dụng:\nprint(fibonacci(10))  # Kết quả: 55\n```\n\n**Lưu ý:** Cách đệ quy cơ bản này có độ phức tạp thời gian là $O(2^n)$. Nếu cần tính với $n$ lớn, bạn nên sử dụng **memoization** (`@functools.lru_cache`) để tối ưu hiệu năng:\n\n```python\nfrom functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fibonacci_fast(n):\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)\n```"}}] | expected no tool call | Từ chối yêu cầu ngoài phạm vi, không gọi tool |
| M06_switch_tool | wrong_tool | [{"name": "lookup", "args": {"topic": "news", "query": "OpenAI news"}}] | query: expected 'OpenAI', got 'OpenAI news' | Làm rõ routing, query theo chủ đề và yêu cầu nhiều nguồn |

Kết quả base mới nhất: không có case thất bại trong lần đo này. Điểm một lần chạy không bảo đảm mọi câu hỏi thực tế đều đúng.


## B3. Bộ eval nhóm: 5 một lượt + 5 nhiều lượt

`data/eval_group.json` có 10 case, đầy đủ `id`, `phase=B`, loại lỗi, đầu vào, kỳ vọng và `metadata.what_it_tests`. Giữ nguyên `data/eval_base.json`.

| Case | Số lượt | Nội dung kiểm tra | Tool kỳ vọng | Kết quả |
|---|---:|---|---|---|
| G01_deduplicate_urls | 1 | Loại URL trùng từ danh sách đã có | deduplicate | Đạt |
| G02_missing_article_url | 1 | Hỏi URL còn thiếu | clarify | Đạt |
| G03_explicit_timeline | 1 | Đúng handle và giới hạn 2 bài | timeline | Đạt |
| G04_top_social_posts | 1 | Tìm bài X theo chủ đề, Top và giới hạn | social_search | Đạt |
| G05_format_supplied_items | 1 | Định dạng bài đã cung cấp | format | Đạt |
| G06_correct_account_and_limit | 3 | Sửa tài khoản và số bài qua nhiều lượt | timeline | Đạt |
| G07_supply_url_after_clarification | 3 | Giữ URL được bổ sung ở lượt trước | fetch | Đạt |
| G08_switch_social_sort | 3 | Đổi Latest sang Top, giữ số lượng | social_search | Đạt |
| G09_deduplicate_carry_items | 3 | Lọc trùng danh sách từ lượt trước | deduplicate | Đạt |
| G10_correct_digest_template | 3 | Đổi mẫu trình bày, giữ danh sách | format | Đạt |

Bằng chứng: `runs/v3-final_B_group_gemini_20261110T154026976389.json`. Đạt 10/10, lỗi nhà cung cấp: 0.

Bổ sung riêng cho stock_quote: `data/eval_stock_quote.json`, kết quả 1/1; `runs/v3-final-stock-demo_B_extension_gemini_20261110T154310124497.json`. Case này không làm thay đổi cơ cấu 10 case của bộ group.


## B4. Bằng chứng hội thoại

Phiên UI mới nhất bên dưới dùng Gemini thật; thao tác được thực hiện tự động theo kịch bản qua Streamlit AppTest, không phải dữ liệu giả lập. Các transcript người dùng đã thử trước đó cũng được giữ trong `transcripts/`.

| Lượt | Yêu cầu | Tool thực tế | Trạng thái |
|---|---|---|---|
| 1 | T?m t?t b?i vi?t n?y gi?p m?nh. | clarify | waiting_for_user |
| 2 | https://example.com | fetch | answered |
| 3 | Lo?i c?c URL tr?ng trong danh s?ch n?y, gi? b?i ??u ti?n: [{"title":"A","url":"https://example.com/a"},{"title":"B","url":"https://example.com/a"}]. Ch? l?c tr?ng, kh?ng t?m ki?m. | deduplicate | answered |

Bằng chứng UI: `transcripts/ui_v3_gemini_20261110T154007632059.transcript.json`. CLI có phiên 3 lượt thật tại `transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json`. Phiên người dùng thử 4 lượt thành công: `transcripts/ui_gemini_20261110T122056694086.transcript.json`.


## B5. Tool mới, test và các lỗi đã sửa

- `deduplicate`: chạy cục bộ; so URL chính xác sau khi bỏ khoảng trắng, giữ bài đầu tiên và thứ tự, không so nghĩa nội dung. Có TOOL.md đầy đủ, khai báo schema, đăng ký implementation, 14 test trong `test_deduplicate.py` và 3 test qua registry trong `test_tools_todo.py`.
- `stock_quote`: dữ liệu **minh họa cố định**, không phải giá thị trường. TOOL.md đã đủ frontmatter. Kết quả có `is_demo=true`, `source=static_demo`, `as_of=null`. Đầu vào rỗng/sai kiểu trả error dict; mã không hỗ trợ không còn được gán giá mặc định. Có 3 test ban đầu và 7 trường hợp kiểm thử bổ sung.
- Bộ chấm từng sắp xếp trực tiếp dictionary trong danh sách, gây TypeError; đã sửa dùng biểu diễn JSON xác định và giữ regression test.
- Log tool có emoji/tiếng Việt gây UnicodeEncodeError trên console Windows cp1252; đã chuyển log chẩn đoán sang ASCII và thêm regression test. Transcript vẫn giữ Unicode.
- UI có test đổi phiên bản, dùng đúng prompt/tool, giữ lịch sử đúng phạm vi, lưu transcript, reset và xử lý lỗi nhà cung cấp.
- Kết quả kiểm thử hoàn thiện: **122 test đạt, 0 lỗi, 0 bỏ qua**. Các HTTP trong unit test đều giả lập; eval và demo riêng dùng API thật.

## B6. Nhận xét và giới hạn

Quy tắc routing, hỏi lại, ngữ cảnh và xác nhận nằm trong system prompt. Mô tả tool và quy ước tham số nằm trong tools.yaml. V3 UI đã dùng cùng cấu hình được đo ở run `v3-final`; v1/v2 và bản v3 lịch sử được giữ nguyên để so sánh.

Bộ chấm đo tên tool và tham số, không bảo đảm nội dung nguồn luôn đúng hoặc API ngoài luôn thành công. Các sai khác query gần nghĩa và câu hỏi xác nhận cần được xem thủ công bên cạnh điểm tự động. Link demo phụ thuộc tiến trình local và tunnel. Thời điểm nộp/hoàn tất trước mốc 16:30 cần người nộp đối chiếu lịch lớp; báo cáo không tự xác nhận tiêu chí thời gian này.

## B7. Bonus

- Đã hoàn thành thử thách unit test không skipped và sửa lỗi có regression test.
- Chưa có bằng chứng gửi Telegram thật sau xác nhận; không nhận hoàn thành bonus này. UI không bật send.
- Chưa làm Small Local Model Challenge: chưa chạy 2 model local và 2 vòng tối ưu local.
- Có UI và 2 tool mới; **chưa đạt** bonus yêu cầu hơn 3 tool mới (ít nhất 4).
- Poster HTML/SVG là tùy chọn, chưa làm; report Markdown là tài liệu nộp chính.

## B8. Kiểm tra nộp bài

- Có prompt/tool, version log v0–v3 và các run JSON thật.
- Có 10 eval case đúng cơ cấu, tool mới và unit test xanh.
- Có UI v1/v2/v3, tool mới dùng được ở v3, transcript và link public đã kiểm tra.
- Không đưa .env hoặc API key vào bài nộp. Công cụ cloudflared được lưu ngoài repo.
- Giữ máy chủ/tunnel chạy trong buổi demo; nếu khởi động tunnel mới phải cập nhật URL trong report.
