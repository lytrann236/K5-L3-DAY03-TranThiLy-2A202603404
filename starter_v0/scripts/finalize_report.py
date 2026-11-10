"""Dựng report tiếng Việt theo mẫu chính thức, chỉ đọc bằng chứng đã có."""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_URL = "https://tranthily-research-agent.vercel.app"
TEMPLATE_URL = "https://github.com/VinUni-AI20k/K5-L3-DAY03-ResearchAgentToolEval/blob/main/starter_v0/artifacts/REPORT.md"


def latest(pattern):
    path = sorted((ROOT / "runs").glob(pattern))[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def cell(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", "")


def brief_calls(calls):
    """Rút gọn nội dung dài khi trình bày, không sửa lời gọi trong log gốc."""
    items = []
    for call in calls:
        args = dict(call["args"])
        if isinstance(args.get("text"), str) and len(args["text"]) > 100:
            args["text"] = args["text"][:100] + "… [rút gọn; xem log gốc]"
        items.append({"name": call["name"], "args": args})
    return cell(items)


def explain(failures):
    translated = []
    for failure in failures:
        value = failure.replace("expected no tool call", "Yêu cầu không gọi tool nhưng agent vẫn gọi")
        value = value.replace("missing tool call ", "Thiếu lời gọi ").replace("extra tool call ", "Thừa lời gọi ")
        value = value.replace(": expected ", ": kỳ vọng ").replace(", got ", ", thực tế ")
        translated.append(value)
    return cell("; ".join(translated))


def build():
    historical = [latest(f"v{i}_B_base_gemini_*.json") for i in range(4)]
    base_path, base = latest("v3-final_B_base_gemini_*.json")
    group_path, group = latest("v3-final_B_group_gemini_*.json")
    stock_path, stock = latest("v3-final-stock-demo_B_extension_gemini_*.json")
    with (ROOT / "artifacts/version_log.csv").open(encoding="utf-8-sig", newline="") as stream:
        version_rows = {row["run_file"]: row for row in csv.DictReader(stream)}
    transcript_path = ROOT / "transcripts/ui_v3_gemini_20261110T154007632059.transcript.json"
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    test_output = (ROOT / "artifacts/pytest-results.txt").read_text(encoding="utf-8-sig")
    passed_tests = int(re.search(r"(\d+) passed", test_output).group(1))

    text = """# Báo cáo Day 03 Lab v2 — Research Agent

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

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Agent tìm tin tức trên web và bài đăng X, đọc URL, loại bài trùng URL rồi trình bày thành bản tin có nguồn. Khi thiếu thông tin, agent hỏi lại thay vì tự chọn một tài khoản hoặc bài viết.

"""
    text += f"**Link dùng thử (triển khai):** [TRANTHILY]({DEMO_URL}/)\n\n"
    text += """Link demo được triển khai trên Vercel, không cần giữ máy tính hoặc Cloudflare Tunnel bật. Bản Streamlit vẫn có thể chạy cục bộ theo hướng dẫn trong `UI-README.md`.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu thông tin hoặc cần xác nhận | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X | không |
| social_search | Tìm bài đăng X theo chủ đề, mới nhất hoặc phổ biến | không |
| lookup | Tìm thông tin và tin tức web theo khoảng thời gian | không |
| fetch | Đọc nội dung một URL cụ thể | không |
| format | Trình bày dữ liệu đã có thành bản tin | không |
| send | Gửi Telegram sau xác nhận; chỉ cung cấp qua CLI | không |
| policy | Tìm trong chính sách nội bộ | không |
| papers | Tìm bài báo khoa học trên arXiv | không |
| paper_text | Trích văn bản từ bài báo arXiv | không |
| deduplicate | Loại bài trùng URL, giữ bài đầu tiên và thứ tự | có |
| stock_quote | Trả dữ liệu cổ phiếu minh họa cố định; không phải giá hiện tại | có |

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

| Phiên bản | File thay đổi | Giả thuyết | Chỉ số trước | Chỉ số sau | File kết quả chạy |
|---|---|---|---:|---:|---|
"""
    hypotheses = ["Đo chất lượng ban đầu", "Hỏi lại khi thiếu tài khoản/URL sẽ sửa R10, R11", "Phân biệt thiếu đối tượng với tên người rõ ràng sẽ giảm hỏi lại thừa", "Xin xác nhận trước gửi sẽ sửa R12"]
    for index, (path, run) in enumerate(historical):
        row = version_rows[relative(path)]
        before = "—" if index == 0 else f"{float(row['metric_before']):.0%}"
        changed = "Bản gốc" if index == 0 else "`artifacts/system_prompt.md`"
        text += f"| v{index} | {changed} | {hypotheses[index]} | {before} | {run['summary']['case_accuracy']:.0%} | `{relative(path)}` |\n"
    text += f"| v3-final / base | Prompt, khai báo tool, UI, stock_quote | Tích hợp quy tắc chọn tool, tham số và xác nhận để sửa các lỗi còn lại | 70% | {base['summary']['case_accuracy']:.0%} | `{relative(base_path)}` |\n"
    text += f"| v3-final / nhóm | Cùng cấu hình hoàn thiện | Kiểm tra lại cùng 10 case nhóm với bộ tool mở rộng | 100% | {group['summary']['case_accuracy']:.0%} | `{relative(group_path)}` |\n"
    text += """
V1 sửa R10/R11 nhưng gây hỏi lại quá mức nên tổng điểm giữ 55%; v2 đạt 65%; v3 lịch sử tránh gửi ngay nhưng R12 còn sai `response_type`, nên giả thuyết xác nhận chưa đạt ở vòng đó. Bản hoàn thiện sửa các vấn đề còn lại và có run riêng. Điểm base và điểm nhóm thuộc hai bộ dữ liệu khác nhau; không dùng điểm nhóm để thay thế điểm base. Run OpenRouter của nhóm được giữ riêng, không trộn với chuỗi Gemini.

## B2. Phân tích lỗi

Các dòng sau lấy từ `results[*].result.failures` của baseline Gemini v0. Giữ nguyên mã loại lỗi của bộ chấm; nội dung dài trong tham số `text` được rút gọn để bảng dễ đọc, xem đầy đủ trong run JSON gốc.

| Mã case | Loại lỗi | Lời gọi tool thực tế | Nội dung sai | Cách sửa |
|---|---|---|---|---|
"""
    fixes = {"wrong_tool": "Làm rõ chọn nguồn/tool và query theo chủ đề", "out_of_scope": "Từ chối ngoài phạm vi, không gọi tool", "unnecessary_tool": "Trả lời năng lực trực tiếp", "missing_info": "Hỏi tài khoản hoặc URL còn thiếu", "wrong_boundary": "Xin xác nhận bằng yes_no trước gửi"}
    for case in historical[0][1]["results"]:
        result = case["result"]
        if not result["passed"]:
            kind = result["failure_type"]
            text += f"| {case['id']} | {kind} | {brief_calls(result['actual_tool_calls'])} | {explain(result['failures'])} | {fixes.get(kind, 'Kiểm tra tham số')} |\n"
    text += f"\nBản hoàn thiện đạt {base['summary']['passed_cases']}/{base['summary']['total_cases']} case base trong lần đo đã lưu. Kết quả này không bảo đảm mọi câu hỏi thực tế đều đúng.\n"
    text += """

## B3. Các case eval của nhóm

`data/eval_group.json` có 10 case, gồm 5 một lượt và 5 nhiều lượt. Mỗi case có mã, pha B, loại lỗi, đầu vào, kỳ vọng và mục tiêu kiểm tra. Không sửa `data/eval_base.json`.

| Mã case | Nội dung kiểm tra | Tool/hành vi kỳ vọng | Kết quả |
|---|---|---|---|
"""
    descriptions = ["Một lượt: loại URL trùng từ danh sách có sẵn", "Một lượt: hỏi URL còn thiếu", "Một lượt: dùng đúng handle và giới hạn 2 bài", "Một lượt: tìm bài X phổ biến theo chủ đề", "Một lượt: định dạng bài đã cung cấp", "Nhiều lượt: sửa tài khoản và số bài", "Nhiều lượt: giữ URL đã được bổ sung", "Nhiều lượt: đổi cách sắp xếp và giữ số lượng", "Nhiều lượt: lọc trùng danh sách ở lượt trước", "Nhiều lượt: đổi mẫu trình bày, giữ dữ liệu"]
    dataset = json.loads((ROOT / "data/eval_group.json").read_text(encoding="utf-8"))
    results = {case["id"]: case["result"] for case in group["results"]}
    for case, description in zip(dataset["cases"], descriptions):
        calls = case["expect"]["tool_calls"]
        expected = "; ".join(f"{call['name']}({json.dumps(call['args'], ensure_ascii=False)})" for call in calls)
        text += f"| {case['id']} | {description} | {cell(expected)} | {'Đạt' if results[case['id']]['passed'] else 'Chưa đạt'} |\n"
    text += f"\nKết quả: {group['summary']['passed_cases']}/10, không lỗi nhà cung cấp. Bằng chứng: `{relative(group_path)}`.\n"
    text += f"\nCase bổ sung riêng cho `stock_quote`: `data/eval_stock_quote.json`, đạt {stock['summary']['passed_cases']}/{stock['summary']['total_cases']}; bằng chứng `{relative(stock_path)}`. Case này không thay đổi cơ cấu 10 case nhóm.\n"
    text += """

## B4. Bằng chứng chat trực tiếp

Bảng dưới dùng phiên UI gọi Gemini thật qua Streamlit AppTest với 3 đầu vào theo kịch bản, không dùng phản hồi giả lập. Đây là kiểm tra tự động, không phải người nhập trực tiếp từng lượt. Nội dung yêu cầu được diễn giải lại bằng tiếng Việt vì đầu vào phiên này bị mất dấu khi truyền qua terminal Windows; giữ nguyên transcript gốc.

| Lượt | Yêu cầu người dùng (diễn giải) | Lời gọi tool | Bằng chứng phiên bản | Kết quả |
|---|---|---|---|---|
"""
    requests = {1: "Tóm tắt bài viết nhưng chưa cung cấp URL", 2: "Bổ sung URL https://example.com", 3: "Loại bài trùng URL https://example.com/a trong danh sách A, B; giữ bài đầu tiên, không tìm kiếm"}
    states = {"waiting_for_user": "Đã hỏi lại, chờ người dùng", "answered": "Đã trả lời", "provider_error": "Lỗi nhà cung cấp", "max_tool_rounds": "Chạm giới hạn vòng gọi tool"}
    evidence = f"{transcript['version']}; prompt `{transcript['prompt_hash'][:12]}`; tools `{transcript['tools_hash'][:12]}`"
    for turn in transcript["turns"]:
        names = ", ".join(event["tool"] for event in turn.get("tool_events", [])) or "Không gọi tool"
        text += f"| {turn['turn_index']} | {cell(requests.get(turn['turn_index'], turn['user']))} | {names} | {evidence} | {states.get(turn['status'], turn['status'])} |\n"
    text += f"\nTranscript UI: `{relative(transcript_path)}`. Hash đầy đủ nằm trong file này.\n"
    text += """
Các bằng chứng bổ sung:

- CLI gọi API thật, 3 lượt: `transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json`.
- Phiên người dùng thử UI, 4 lượt thành công: `transcripts/ui_gemini_20261110T122056694086.transcript.json`. Phiên này thuộc cấu hình trước khi có nhãn `v3-final`.

## B5. Bằng chứng bonus

| Bonus | File bằng chứng | Phần đã hoạt động | Giới hạn / quy tắc kiểm soát |
|---|---|---|---|
| send (Telegram) | `tests/test_tools_examples.py`, `tests/test_tools_todo.py` | Đã kiểm tra bằng HTTP giả lập việc không gửi khi thiếu xác nhận | Chưa có transcript gửi Telegram thật sau xác nhận; chưa nhận hoàn thành bonus này; UI không bật send |
| arXiv/chính sách nội bộ | `tools/papers/`, `tools/paper_text/`, `tools/policy/`; test policy trong `tests/test_tools_todo.py` | Có tool và test tìm chính sách, lọc nội dung chỉ dẫn không đáng tin | Chưa có run demo arXiv thật được dẫn chứng trong báo cáo; không nhận hoàn thành bonus arXiv |
| UI | `app.py`, `tests/test_streamlit_app.py`, `UI-README.md` và transcript ở B4 | Có chọn v1/v2/v3, lịch sử chat, xem tool, lưu/tải JSON; có link demo Vercel | V1/v2 là bản lịch sử; link Vercel vẫn áp dụng hạn mức hosting và API |
| Unit test tool | `artifacts/pytest-results.txt`, `tests/test_deduplicate.py`, `tests/test_stock_quote.py`, `tests/test_tools_todo.py` | Hoàn thành test TODO, không bỏ qua test; có test cho hai tool mới | Unit test dùng mạng giả lập; không thay thế kiểm tra API thật |

"""
    text += f"Kết quả pytest đã lưu: **{passed_tests} test đạt, 0 lỗi, 0 bỏ qua** tại `artifacts/pytest-results.txt`.\n\n"
    text += """Chi tiết kiểm thử và lỗi được phát hiện:

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
"""
    text += f"\nCấu trúc đối chiếu theo [mẫu báo cáo chính thức]({TEMPLATE_URL}); các phần mô tả và nhận xét được viết bằng tiếng Việt, giữ tên tool, mã lỗi và hash để đối chiếu log.\n"
    (ROOT / "artifacts/REPORT.md").write_text(text, encoding="utf-8")
    print("Generated Vietnamese report following sections A1-A3 and B1-B7.")


if __name__ == "__main__":
    build()
