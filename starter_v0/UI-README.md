# Chạy giao diện Research Agent

Từ thư mục `starter_v0`, kích hoạt môi trường và chạy:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -X utf8 -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Mở http://localhost:8501. API key được đọc từ `.env` trên máy chủ.

## Các phiên bản

- **v1, v2:** cấu hình Gemini lịch sử, giữ nguyên hash để so sánh kết quả.
- **v3:** cấu hình hoàn thiện tại `artifacts/system_prompt.md` và `artifacts/tools.yaml`, có `deduplicate` và `stock_quote`. Transcript dùng nhãn `v3-final` để phân biệt với kết quả v3 lịch sử 70%.
- UI chỉ hiển thị v1/v2/v3, không có v4. Đổi phiên bản, model hoặc cấu hình sẽ bắt đầu hội thoại mới. File transcript cũ vẫn được lưu.
- Telegram không được bật trên UI. `stock_quote` chỉ trả dữ liệu minh họa, không phải giá hiện tại.

## Demo 3 lượt

1. Nhập “Tóm tắt bài viết này giúp mình.” để agent hỏi URL.
2. Bổ sung `https://example.com`.
3. Nhập: `Loại URL trùng: [{"title":"A","url":"https://example.com/a"},{"title":"B","url":"https://example.com/a"}].`

Xem kết quả tool trong mục mở rộng. Transcript được lưu sau mỗi lượt tại `transcripts/*.transcript.json` và có nút tải JSON.

## Link public

Link đã kiểm tra: https://groups-teams-veterinary-citysearch.trycloudflare.com

Công cụ cloudflared chính thức được đặt ngoài repo tại `E:\AI\labday3\tools\cloudflared.exe`. Để khởi động lại tunnel, mở terminal khác và chạy:

```powershell
E:\AI\labday3\tools\cloudflared.exe tunnel --url http://127.0.0.1:8501 --protocol http2 --no-autoupdate
```

Mỗi lần khởi động tunnel có thể nhận URL mới. Giữ Streamlit và tunnel chạy trong buổi demo; cập nhật link mới vào `artifacts/REPORT.md` và tài liệu này. Không commit `.env` hoặc API key.

## Kiểm tra và bằng chứng

```powershell
python -m pytest -q -p no:cacheprovider
python -X utf8 run_eval.py --provider gemini --version v3-final --suite base --eval-cases data/eval_base.json
python -X utf8 run_eval.py --provider gemini --version v3-final --suite group --eval-cases data/eval_group.json
```

`scripts/finalize_report.py` dựng report từ log thật và ghi version log. Nếu tunnel đổi URL, cập nhật URL trong script trước khi dựng lại report. Kết quả eval và demo Gemini dùng API thật; unit test và kiểm tra UI tự động thông thường dùng dữ liệu giả lập.
