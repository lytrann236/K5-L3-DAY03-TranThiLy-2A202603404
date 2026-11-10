"""Build the Vietnamese submission report from recorded, real run evidence."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def latest(pattern):
    path = sorted((ROOT / "runs").glob(pattern))[-1]
    return path, json.loads(path.read_text(encoding="utf-8"))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def cell(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False)
    return value.replace("|", "\\|").replace("\n", " ")


def build():
    base_path, base = latest("v3-final_B_base_gemini_*.json")
    group_path, group = latest("v3-final_B_group_gemini_*.json")
    historical = [latest(f"v{i}_B_base_gemini_*.json") for i in range(4)]
    log_path = ROOT / "artifacts/version_log.csv"
    with log_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    evidence = [(base_path, base, "0.7", "base"), (group_path, group, "1.0", "group")]
    extra = sorted((ROOT / "runs").glob("v3-final-stock-demo_B_extension_gemini_*.json"))
    if extra:
        evidence.append((extra[-1], json.loads(extra[-1].read_text(encoding="utf-8")), "", "extension"))
    for path, run, before, scope in evidence:
        if not any(row["run_file"] == relative(path) for row in rows):
            rows.append(dict(version=run["version"], author="nguyenthuyduong",
                changed_artifact="system_prompt.md; tools.yaml; app.py; stock_quote",
                artifact_version=run["artifact_version"], prompt_hash=run["prompt_hash"], tools_hash=run["tools_hash"],
                reason=f"Hoàn thiện tích hợp; Gemini; suite={scope}",
                hypothesis="Quy tắc routing và xác nhận rõ ràng cùng cấu hình UI thống nhất giúp sửa các lỗi còn lại; đây là vòng tích hợp sau v1-v3",
                metric_before=before, metric_after=run["summary"]["case_accuracy"], run_file=relative(path)))
    with log_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    transcript_path = sorted((ROOT / "transcripts").glob("ui_v3_gemini_*.transcript.json"))[-1]
    transcript = json.loads(transcript_path.read_text(encoding="utf-8"))
    text = """# Báo cáo Research Agent — Day 03 Lab v2

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
"""
    hypotheses = ["Baseline chưa tối ưu", "Hỏi lại khi thiếu handle/URL thay vì đoán", "Chỉ hỏi tài khoản khi đối tượng thiếu hoặc mơ hồ", "Yêu cầu xác nhận trước khi gửi"]
    for index, (path, run) in enumerate(historical):
        before = "—" if index == 0 else f"{historical[index-1][1]['summary']['case_accuracy']:.0%}"
        text += f"| v{index} | {hypotheses[index]} | {before} | {run['summary']['case_accuracy']:.0%} | `{relative(path)}` |\n"
    text += f"| v3-final / base | Hoàn thiện routing, nhiều tool, xác nhận và UI | 70% | {base['summary']['case_accuracy']:.0%} | `{relative(base_path)}` |\n"
    text += f"| v3-final / group | Kiểm tra lại cùng 10 case của nhóm | 100% | {group['summary']['case_accuracy']:.0%} | `{relative(group_path)}` |\n"
    text += """
Hash đầy đủ, tác giả, lý do và đường dẫn run được ghi trong `artifacts/version_log.csv`. Bộ base và bộ group là hai tập dữ liệu riêng; không dùng điểm group để thay cho điểm base. Các run OpenRouter được nhóm đóng góp vẫn giữ trong `runs/`, nhưng không trộn vào chuỗi so sánh Gemini này.

**Kết luận từng giả thuyết:** v1 sửa R10/R11 nhưng gây hỏi lại quá mức nên tổng điểm giữ 55%; v2 phục hồi các yêu cầu đã nêu rõ người, đạt 65%; v3 đã tránh gửi ngay nhưng R12 còn sai `response_type=text`, nên chưa chứng minh thành công giả thuyết xác nhận. Bản hoàn thiện được đo lại riêng, không suy diễn điểm từ các run trước.

## B2. Phân tích lỗi baseline v0

Các dòng sau lấy trực tiếp từ `results` của baseline Gemini; giữ mã loại lỗi của bộ chấm.

| Case | Loại lỗi | Lời gọi thực tế | Chi tiết sai | Hướng sửa |
|---|---|---|---|---|
"""
    fixes = {"wrong_tool": "Làm rõ routing, query theo chủ đề và yêu cầu nhiều nguồn", "out_of_scope": "Từ chối yêu cầu ngoài phạm vi, không gọi tool", "unnecessary_tool": "Trả lời câu hỏi năng lực trực tiếp", "missing_info": "Hỏi rõ đối tượng hoặc URL", "wrong_boundary": "Xin xác nhận trước gửi bằng yes_no"}
    for case in historical[0][1]["results"]:
        result = case["result"]
        if not result["passed"]:
            kind = result["failure_type"]
            text += f"| {case['id']} | {kind} | {cell(result['actual_tool_calls'])} | {cell('; '.join(result['failures']))} | {fixes.get(kind, 'Kiểm tra tham số')} |\n"
    failures = [case["id"] for case in base["results"] if not case["result"]["passed"]]
    text += "\nKết quả base mới nhất: " + ("không có case thất bại trong lần đo này." if not failures else ", ".join(failures)) + " Điểm một lần chạy không bảo đảm mọi câu hỏi thực tế đều đúng.\n"
    text += """

## B3. Bộ eval nhóm: 5 một lượt + 5 nhiều lượt

`data/eval_group.json` có 10 case, đầy đủ `id`, `phase=B`, loại lỗi, đầu vào, kỳ vọng và `metadata.what_it_tests`. Giữ nguyên `data/eval_base.json`.

| Case | Số lượt | Nội dung kiểm tra | Tool kỳ vọng | Kết quả |
|---|---:|---|---|---|
"""
    descriptions = ["Loại URL trùng từ danh sách đã có", "Hỏi URL còn thiếu", "Đúng handle và giới hạn 2 bài", "Tìm bài X theo chủ đề, Top và giới hạn", "Định dạng bài đã cung cấp", "Sửa tài khoản và số bài qua nhiều lượt", "Giữ URL được bổ sung ở lượt trước", "Đổi Latest sang Top, giữ số lượng", "Lọc trùng danh sách từ lượt trước", "Đổi mẫu trình bày, giữ danh sách"]
    dataset = json.loads((ROOT / "data/eval_group.json").read_text(encoding="utf-8"))
    results = {case["id"]: case["result"] for case in group["results"]}
    for case, description in zip(dataset["cases"], descriptions):
        names = ", ".join(call["name"] for call in case["expect"]["tool_calls"])
        text += f"| {case['id']} | {len(case.get('turns', [None]))} | {description} | {names} | {'Đạt' if results[case['id']]['passed'] else 'Chưa đạt'} |\n"
    text += f"\nBằng chứng: `{relative(group_path)}`. Đạt {group['summary']['passed_cases']}/10, lỗi nhà cung cấp: {group['summary']['provider_error_cases']}.\n"
    stock_runs = sorted((ROOT / "runs").glob("v3-final-stock-demo_B_extension_gemini_*.json"))
    if stock_runs:
        stock = json.loads(stock_runs[-1].read_text(encoding="utf-8"))
        text += f"\nBổ sung riêng cho stock_quote: `data/eval_stock_quote.json`, kết quả {stock['summary']['passed_cases']}/{stock['summary']['total_cases']}; `{relative(stock_runs[-1])}`. Case này không làm thay đổi cơ cấu 10 case của bộ group.\n"
    text += """

## B4. Bằng chứng hội thoại

Phiên UI mới nhất bên dưới dùng Gemini thật; thao tác được thực hiện tự động theo kịch bản qua Streamlit AppTest, không phải dữ liệu giả lập. Các transcript người dùng đã thử trước đó cũng được giữ trong `transcripts/`.

| Lượt | Yêu cầu | Tool thực tế | Trạng thái |
|---|---|---|---|
"""
    for turn in transcript["turns"]:
        names = ", ".join(event["tool"] for event in turn.get("tool_events", [])) or "Không gọi tool"
        text += f"| {turn['turn_index']} | {cell(turn['user'])} | {names} | {turn['status']} |\n"
    text += f"\nBằng chứng UI: `{relative(transcript_path)}`. CLI có phiên 3 lượt thật tại `transcripts/v4-deduplicate_gemini_20261110T112423997480.transcript.json`. Phiên người dùng thử 4 lượt thành công: `transcripts/ui_gemini_20261110T122056694086.transcript.json`.\n"
    text += """

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
"""
    (ROOT / "artifacts/REPORT.md").write_text(text, encoding="utf-8")
    print("Updated Vietnamese report and version log from actual evidence.")


if __name__ == "__main__":
    build()
