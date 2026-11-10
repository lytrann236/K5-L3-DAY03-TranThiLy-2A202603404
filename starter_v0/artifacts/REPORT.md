# Báo cáo Day 03 Lab v2 — Research Agent

## Thông tin nhóm

- Team:TRANTHILY
- Nhà cung cấp/model: Gemini / `gemini-3.5-flash`.
- **Thành viên nhóm:**

  | STT | Họ và tên              | Mã sinh viên |
  | --- | ---------------------- | ------------ |
  | 1   | Trần Thị Lý            | 2A202603404  |
  | 2   | Nguyễn Thị Hương Giang | 2A202603538  |
  | 3   | Nguyễn Thuỳ Dương      | 2A202603388  |
  | 4   | Nguyễn Quỳnh Trang     | 2A202603477  |

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent tìm tin tức trên web và bài đăng X, đọc URL, loại bài trùng URL rồi trình bày thành bản tin có nguồn. Khi thiếu thông tin, agent hỏi lại thay vì tự chọn một tài khoản hoặc bài viết.

**Link dùng thử (triển khai):** https://tranthily-research-agent.vercel.app

Link demo được triển khai trên Vercel, không cần giữ máy tính hoặc Cloudflare Tunnel bật. Bản Streamlit vẫn có thể chạy cục bộ theo hướng dẫn trong `UI-README.md`.

## A2. Tool agent có

| Tên tool      | Làm được gì                                                    | Tool mới nhóm thêm? |
| ------------- | -------------------------------------------------------------- | ------------------- |
| clarify       | Hỏi lại khi thiếu thông tin hoặc cần xác nhận                  | không               |
| timeline      | Lấy bài đăng gần đây của một tài khoản X                       | không               |
| social_search | Tìm bài đăng X theo chủ đề, mới nhất hoặc phổ biến             | không               |
| lookup        | Tìm thông tin và tin tức web theo khoảng thời gian             | không               |
| fetch         | Đọc nội dung một URL cụ thể                                    | không               |
| format        | Trình bày dữ liệu đã có thành bản tin                          | không               |
| send          | Gửi Telegram sau xác nhận; chỉ cung cấp qua CLI                | không               |
| policy        | Tìm trong chính sách nội bộ                                    | không               |
| papers        | Tìm bài báo khoa học trên arXiv                                | không               |
| paper_text    | Trích văn bản từ bài báo arXiv                                 | không               |
| deduplicate   | Loại bài trùng URL, giữ bài đầu tiên và thứ tự                 | có                  |
| stock_quote   | Trả dữ liệu cổ phiếu minh họa cố định; không phải giá hiện tại | có                  |

UI chỉ có v1, v2, v3. V1/v2 dùng cấu hình lịch sử; v3 dùng bản hoàn thiện có tool mới. UI không bật `send`, nên v3 có 11 tool được cung cấp cho model.

## A3. Câu hỏi mẫu để thử

1. Lấy 2 bài mới nhất của karpathy.
2. Tin AI hôm nay có gì nổi bật?
3. Tóm tắt bài này: https://example.com
4. Loại URL trùng, giữ bài đầu tiên: `[{"title":"A","url":"https://example.com/a"},{"title":"B","url":"https://example.com/a"}]`.
5. Cho tôi dữ liệu cổ phiếu minh họa của mã AAPL, không cần giá hiện tại.

---

# PHẦN B — Chi tiết / Bằng chứng

## B1. Bằng chứng phiên bản

Nguồn: `artifacts/version_log.csv` và `runs/*.json`. Chỉ tiêu trước/sau trong bảng là tỷ lệ case đúng. V0–v3 là chuỗi tối ưu Gemini lịch sử; `v3-final` là bản tích hợp được đo lại riêng, không thay thế số liệu cũ. UI chọn v3 nhưng transcript ghi `v3-final` và hash cấu hình thực tế.

| Phiên bản       | File thay đổi                          | Giả thuyết                                                             | Chỉ số trước | Chỉ số sau | File kết quả chạy                                         |
| --------------- | -------------------------------------- | ---------------------------------------------------------------------- | -----------: | ---------: | --------------------------------------------------------- |
| v0              | Bản gốc                                | Đo chất lượng ban đầu                                                  |            — |        55% | `runs/v0_B_base_gemini_20261110T102151789910.json`        |
| v1              | `artifacts/system_prompt.md`           | Hỏi lại khi thiếu tài khoản/URL sẽ sửa R10, R11                        |          55% |        55% | `runs/v1_B_base_gemini_20261110T104455968698.json`        |
| v2              | `artifacts/system_prompt.md`           | Phân biệt thiếu đối tượng với tên người rõ ràng sẽ giảm hỏi lại thừa   |          55% |        65% | `runs/v2_B_base_gemini_20261110T105314645987.json`        |
| v3              | `artifacts/system_prompt.md`           | Xin xác nhận trước gửi sẽ sửa R12                                      |          65% |        70% | `runs/v3_B_base_gemini_20261110T105833327686.json`        |
| v3-final / base | Prompt, khai báo tool, UI, stock_quote | Tích hợp quy tắc chọn tool, tham số và xác nhận để sửa các lỗi còn lại |          70% |       100% | `runs/v3-final_B_base_gemini_20261110T154117007662.json`  |
| v3-final / nhóm | Cùng cấu hình hoàn thiện               | Kiểm tra lại cùng 10 case nhóm với bộ tool mở rộng                     |         100% |       100% | `runs/v3-final_B_group_gemini_20261110T154026976389.json` |

V1 sửa R10/R11 nhưng gây hỏi lại quá mức nên tổng điểm giữ 55%; v2 đạt 65%; v3 lịch sử tránh gửi ngay nhưng R12 còn sai `response_type`, nên giả thuyết xác nhận chưa đạt ở vòng đó. Bản hoàn thiện sửa các vấn đề còn lại và có run riêng. Điểm base và điểm nhóm thuộc hai bộ dữ liệu khác nhau; không dùng điểm nhóm để thay thế điểm base. Run OpenRouter của nhóm được giữ riêng, không trộn với chuỗi Gemini.

## B2. Phân tích lỗi

Các dòng sau lấy từ `results[*].result.failures` của baseline Gemini v0. Giữ nguyên mã loại lỗi của bộ chấm; nội dung dài trong tham số `text` được rút gọn để bảng dễ đọc, xem đầy đủ trong run JSON gốc.

| Mã case                     | Loại lỗi         | Lời gọi tool thực tế                                                                                                                                                                       | Nội dung sai                                                                            | Cách sửa                                    |
| --------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------------- |
| R03_web_news_routing        | wrong_tool       | [{"name": "lookup", "args": {"query": "latest AI news today", "topic": "news", "max_results": 5, "timeframe": "day"}}]                                                                     | query: kỳ vọng 'AI', thực tế 'latest AI news today'                                     | Làm rõ chọn nguồn/tool và query theo chủ đề |
| R08_out_of_scope            | out_of_scope     | [{"name": "send", "args": {"confirmed": true, "text": "Nguyên hàm của hàm số f(x) = x^2 là:\n\n∫ x^2 dx = (x^3 / 3) + C\n\ntrong đó C là hằng số tích phân."}}]                            | Yêu cầu không gọi tool nhưng agent vẫn gọi                                              | Từ chối ngoài phạm vi, không gọi tool       |
| R09_no_tool_capability      | unnecessary_tool | [{"name": "policy", "args": {"query": "vai trò và khả năng của trợ lý"}}]                                                                                                                  | Yêu cầu không gọi tool nhưng agent vẫn gọi                                              | Trả lời năng lực trực tiếp                  |
| R10_missing_handle          | missing_info     | [{"name": "timeline", "args": {"limit": 5, "screenname": "sama"}}]                                                                                                                         | Thiếu lời gọi clarify; Thừa lời gọi timeline                                            | Hỏi tài khoản hoặc URL còn thiếu            |
| R11_missing_url             | missing_info     | [{"name": "fetch", "args": {"url": "https://openai.com/index/hello-gpt-4o/"}}]                                                                                                             | Thiếu lời gọi clarify; Thừa lời gọi fetch                                               | Hỏi tài khoản hoặc URL còn thiếu            |
| R12_confirm_before_send     | wrong_boundary   | [{"name": "send", "args": {"confirmed": true, "text": "Bản tin cập nhật tin tức mới nhất trong ngày."}}]                                                                                   | Thiếu lời gọi clarify; Thừa lời gọi send                                                | Xin xác nhận bằng yes_no trước gửi          |
| R13_parallel_web_and_tweets | wrong_tool       | [{"name": "lookup", "args": {"timeframe": "day", "query": "tin tức AI mới nhất hôm nay", "topic": "news"}}]                                                                                | query: kỳ vọng 'AI', thực tế 'tin tức AI mới nhất hôm nay'; Thiếu lời gọi social_search | Làm rõ chọn nguồn/tool và query theo chủ đề |
| R14_out_of_scope_coding     | out_of_scope     | [{"name": "send", "args": {"confirmed": true, "text": "Dưới đây là hàm Python tính số Fibonacci bằng phương pháp đệ quy (recursion):\n\n```python\ndef fibonac… [rút gọn; xem log gốc]"}}] | Yêu cầu không gọi tool nhưng agent vẫn gọi                                              | Từ chối ngoài phạm vi, không gọi tool       |
| M06_switch_tool             | wrong_tool       | [{"name": "lookup", "args": {"topic": "news", "query": "OpenAI news"}}]                                                                                                                    | query: kỳ vọng 'OpenAI', thực tế 'OpenAI news'                                          | Làm rõ chọn nguồn/tool và query theo chủ đề |

Bản hoàn thiện đạt 20/20 case base trong lần đo đã lưu. Kết quả này không bảo đảm mọi câu hỏi thực tế đều đúng.

## B3. Các case eval của nhóm

`data/eval_group.json` có 10 case, gồm 5 một lượt và 5 nhiều lượt. Mỗi case có mã, pha B, loại lỗi, đầu vào, kỳ vọng và mục tiêu kiểm tra. Không sửa `data/eval_base.json`.

| Mã case                            | Nội dung kiểm tra                            | Tool/hành vi kỳ vọng                                                                                                                                                                      | Kết quả |
| ---------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| G01_deduplicate_urls               | Một lượt: loại URL trùng từ danh sách có sẵn | deduplicate({"items": [{"title": "First", "url": "https://example.com/a"}, {"title": "Duplicate", "url": "https://example.com/a"}, {"title": "Second", "url": "https://example.com/b"}]}) | Đạt     |
| G02_missing_article_url            | Một lượt: hỏi URL còn thiếu                  | clarify({"response_type": "text"})                                                                                                                                                        | Đạt     |
| G03_explicit_timeline              | Một lượt: dùng đúng handle và giới hạn 2 bài | timeline({"screenname": "karpathy", "limit": 2})                                                                                                                                          | Đạt     |
| G04_top_social_posts               | Một lượt: tìm bài X phổ biến theo chủ đề     | social_search({"search_type": "Top", "limit": 3})                                                                                                                                         | Đạt     |
| G05_format_supplied_items          | Một lượt: định dạng bài đã cung cấp          | format({"template": "bullets", "items": [{"title": "Lab update", "url": "https://example.com/lab", "summary": "Evaluation is complete."}]})                                               | Đạt     |
| G06_correct_account_and_limit      | Nhiều lượt: sửa tài khoản và số bài          | timeline({"screenname": "karpathy", "limit": 2})                                                                                                                                          | Đạt     |
| G07_supply_url_after_clarification | Nhiều lượt: giữ URL đã được bổ sung          | fetch({"url": "https://example.com/research"})                                                                                                                                            | Đạt     |
| G08_switch_social_sort             | Nhiều lượt: đổi cách sắp xếp và giữ số lượng | social_search({"search_type": "Top", "limit": 4})                                                                                                                                         | Đạt     |
| G09_deduplicate_carry_items        | Nhiều lượt: lọc trùng danh sách ở lượt trước | deduplicate({"items": [{"title": "A", "url": "https://example.com/a"}, {"title": "Copy", "url": "https://example.com/a"}]})                                                               | Đạt     |
| G10_correct_digest_template        | Nhiều lượt: đổi mẫu trình bày, giữ dữ liệu   | format({"template": "bullets", "items": [{"title": "Research", "url": "https://example.com/research"}]})                                                                                  | Đạt     |

Kết quả: 10/10, không lỗi nhà cung cấp. Bằng chứng: `runs/v3-final_B_group_gemini_20261110T154026976389.json`.

Case bổ sung riêng cho `stock_quote`: `data/eval_stock_quote.json`, đạt 1/1; bằng chứng `runs/v3-final-stock-demo_B_extension_gemini_20261110T154310124497.json`. Case này không thay đổi cơ cấu 10 case nhóm.

## B4. Bằng chứng chat trực tiếp

Bảng dưới dùng phiên UI gọi Gemini thật qua Streamlit AppTest với 3 đầu vào theo kịch bản, không dùng phản hồi giả lập. Đây là kiểm tra tự động, không phải người nhập trực tiếp từng lượt. Nội dung yêu cầu được diễn giải lại bằng tiếng Việt vì đầu vào phiên này bị mất dấu khi truyền qua terminal Windows; giữ nguyên transcript gốc.

| Lượt | Yêu cầu người dùng (diễn giải)                                                                  | Lời gọi tool | Bằng chứng phiên bản                                  | Kết quả                    |
| ---- | ----------------------------------------------------------------------------------------------- | ------------ | ----------------------------------------------------- | -------------------------- |
| 1    | Tóm tắt bài viết nhưng chưa cung cấp URL                                                        | clarify      | v3-final; prompt `3e5d8372b1ce`; tools `b4142a36d220` | Đã hỏi lại, chờ người dùng |
| 2    | Bổ sung URL https://example.com                                                                 | fetch        | v3-final; prompt `3e5d8372b1ce`; tools `b4142a36d220` | Đã trả lời                 |
| 3    | Loại bài trùng URL https://example.com/a trong danh sách A, B; giữ bài đầu tiên, không tìm kiếm | deduplicate  | v3-final; prompt `3e5d8372b1ce`; tools `b4142a36d220` | Đã trả lời                 |

Transcript UI: `transcripts/ui_v3_gemini_20261110T154007632059.transcript.json`. Hash đầy đủ nằm trong file này.

Các bằng chứng bổ sung:

- CLI gọi API thật, 3 lượt: `transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json`.
- Phiên người dùng thử UI, 4 lượt thành công: `transcripts/ui_gemini_20261110T122056694086.transcript.json`. Phiên này thuộc cấu hình trước khi có nhãn `v3-final`.

## B5. Bằng chứng bonus

| Bonus                   | File bằng chứng                                                                                                      | Phần đã hoạt động                                                               | Giới hạn / quy tắc kiểm soát                                                                         |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| send (Telegram)         | `tests/test_tools_examples.py`, `tests/test_tools_todo.py`                                                           | Đã kiểm tra bằng HTTP giả lập việc không gửi khi thiếu xác nhận                 | Chưa có transcript gửi Telegram thật sau xác nhận; chưa nhận hoàn thành bonus này; UI không bật send |
| arXiv/chính sách nội bộ | `tools/papers/`, `tools/paper_text/`, `tools/policy/`; test policy trong `tests/test_tools_todo.py`                  | Có tool và test tìm chính sách, lọc nội dung chỉ dẫn không đáng tin             | Chưa có run demo arXiv thật được dẫn chứng trong báo cáo; không nhận hoàn thành bonus arXiv          |
| UI                      | `app.py`, `tests/test_streamlit_app.py`, `UI-README.md` và transcript ở B4                                           | Có chọn v1/v2/v3, lịch sử chat, xem tool, lưu/tải JSON; đã kiểm tra link public | V1/v2 là bản lịch sử; Vercel áp dụng hạn mức hosting và API                                               |
| Unit test tool          | `artifacts/pytest-results.txt`, `tests/test_deduplicate.py`, `tests/test_stock_quote.py`, `tests/test_tools_todo.py` | Hoàn thành test TODO, không bỏ qua test; có test cho hai tool mới               | Unit test dùng mạng giả lập; không thay thế kiểm tra API thật                                        |

Kết quả pytest đã lưu: **122 test đạt, 0 lỗi, 0 bỏ qua** tại `artifacts/pytest-results.txt`.

Chi tiết kiểm thử và lỗi được phát hiện:

- `deduplicate`: 14 trường hợp trong `test_deduplicate.py` và 3 test qua registry; kiểm tra lọc trùng, thứ tự, metadata, không sửa đầu vào và lỗi dữ liệu.
- `stock_quote`: 3 test ban đầu và 7 trường hợp bổ sung. Phát hiện và sửa 2 vấn đề trong tool được nhóm thêm: đầu vào sai kiểu gây lỗi thay vì trả error dict; mã không hỗ trợ được trả giá mặc định. Kết quả nay có `is_demo=true`, `source=static_demo`, `as_of=null`, không giả làm giá thị trường.
- Chưa ghi nhận lỗi mới trong các tool có sẵn của starter. Có 2 lỗi ở hạ tầng được sửa và giữ regression test: bộ chấm sắp xếp dictionary gây TypeError (`test_eval_normalization.py`), và log Unicode gây lỗi console Windows (`test_chat_encoding.py`). Không tính hai lỗi này thành lỗi của tool có sẵn.
- Ví dụ lỗi unit test phát hiện mà eval định tuyến không phát hiện: model gọi đúng `stock_quote(symbol="UNKNOWN")` nhưng implementation cũ vẫn bịa giá mặc định; `test_unknown_symbol_does_not_invent_price` kiểm tra không được trả trường `price`.
- Có UI và 2 tool mới, chưa đạt bonus yêu cầu hơn 3 tool mới. Poster HTML/SVG là tùy chọn, chưa thực hiện.

## B6. Nhận xét và rút kinh nghiệm

**Những sửa đổi thuộc system prompt:** quy tắc hỏi lại, xác nhận trước gửi, phân biệt nguồn web/X, giữ ngữ cảnh và sửa tham số qua nhiều lượt; bỏ ép một bước ở bản hoàn thiện. V1/v2 và v3 lịch sử được giữ nguyên để so sánh.

**Những sửa đổi thuộc tools.yaml:** mô tả lúc dùng/không dùng, handle không có @, tin tức dùng topic=news, khoảng thời gian, Top/Latest và ranh giới dữ liệu demo của stock_quote. V3 UI dùng cùng prompt/tool với run v3-final; chỉ loại send khỏi các tool UI cho phép.

**Những lỗi cần đánh giá thủ công:** R03 và M06 có query gần nghĩa nhưng bị chấm sai do yêu cầu giá trị cụ thể; R12 ở v3 lịch sử đã hỏi lại thay vì gửi nhưng dùng text thay cho yes_no. Cần xem hành vi thực tế bên cạnh điểm tự động. Bộ chấm định tuyến/tham số không bảo đảm chất lượng nội dung nguồn hoặc API ngoài luôn hoạt động.

**Hướng cải thiện tiếp theo:** bổ sung case kiểm tra nội dung và nguồn trích dẫn, thử thêm câu hỏi ngoài bộ eval, tạo link triển khai ổn định và kiểm tra xác nhận Telegram qua phiên demo riêng. Không sửa bộ base để nâng điểm.

**Lưu ý nộp bài:** link Vercel không phụ thuộc máy local, nhưng vẫn áp dụng hạn mức hosting và API. Không nộp .env hoặc API key. Người nộp tự đối chiếu thời hạn 16:30 theo lịch lớp; báo cáo không tự xác nhận tiêu chí thời gian này.

## B7. Thử thách model nhỏ chạy cục bộ (bonus)

Chưa thực hiện. Chưa chạy ít nhất 2 model local, chưa có 2 vòng tối ưu local và chưa kiểm tra ngược trên cloud. Vì chưa có bằng chứng nên không điền bảng điểm hoặc kết luận cho phần này.
