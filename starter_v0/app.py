"""Streamlit interface using the same model/tool loop as chat.py."""
from datetime import datetime
import json
from pathlib import Path

import streamlit as st

from chat import run_model_tool_loop, trim_history, write_transcript, now_iso
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="Research Agent", page_icon="🔎")
st.title("🔎 Research Agent")
st.caption("Tìm tin, đọc bài viết, loại liên kết trùng và tạo bản tin.")

with st.sidebar:
    st.header("Cuộc trò chuyện")
    if st.session_state.get("selected_version") not in (None, "v1", "v2", "v3"):
        st.session_state.selected_version = "v3"
    selected_version = st.selectbox("Phiên bản agent", ["v1", "v2", "v3"], index=2, key="selected_version")
    st.caption("Đổi phiên bản sẽ bắt đầu cuộc trò chuyện mới.")
    if selected_version == "v3":
        st.caption("Bản hoàn thiện: có lọc URL trùng và dữ liệu cổ phiếu minh họa.")
    model = st.text_input("Model Gemini", value="gemini-3.5-flash")
    st.caption("API key được đọc từ file .env trên máy chủ.")
    if st.button("Cuộc trò chuyện mới"):
        st.session_state.pop("transcript", None)
        st.session_state.pop("history", None)
        st.rerun()
    st.markdown("**Thử hỏi:**\n- Lấy 2 bài mới nhất của karpathy.\n- Tóm tắt bài viết này giúp mình.")
    if selected_version == "v3":
        st.markdown('- Loại URL trùng: [{"url":"https://example.com/a"},{"url":"https://example.com/a"}].')

artifact_dir = ROOT / "artifacts" / "versions" / selected_version
if selected_version == "v3":
    artifact_dir = ROOT / "artifacts"
artifact_label = "v3-final" if selected_version == "v3" else selected_version
prompt_path = artifact_dir / "system_prompt.md"
tools_path = artifact_dir / "tools.yaml"
configuration = (artifact_label, model, prompt_path.read_bytes(), tools_path.read_bytes())
if st.session_state.get("configuration") != configuration:
    st.session_state.pop("transcript", None)
    st.session_state.pop("history", None)
    st.session_state.configuration = configuration

if "transcript" not in st.session_state:
    version = build_artifact_version(artifact_label, prompt_path, tools_path)
    session_id = "ui_" + selected_version + "_gemini_" + datetime.now().strftime("%Y%m%dT%H%M%S%f")
    st.session_state.transcript = {
        "transcript_id": session_id, **artifact_version_dict(version),
        "provider": "gemini", "model": model, "created_at": now_iso(),
        "selected_version": selected_version,
        "system_prompt": str(prompt_path), "tools": str(tools_path),
        "history_window": 5, "max_tool_rounds": 4, "turns": [],
    }
    st.session_state.history = []

transcript = st.session_state.transcript
for turn in transcript["turns"]:
    with st.chat_message("user"):
        st.write(turn["user"])
    with st.chat_message("assistant"):
        st.write(turn.get("assistant_text") or "Không hoàn thành được yêu cầu. Hãy kiểm tra cấu hình hoặc thử lại.")
        if turn.get("tool_events"):
            with st.expander("Nguồn và kết quả công cụ"):
                st.json(turn["tool_events"])

if prompt := st.chat_input("Bạn muốn tìm hiểu điều gì?"):
    record = {"turn_index": len(transcript["turns"]) + 1, "user": prompt, "started_at": now_iso(), "model": model}
    messages = [
        {"role": "system", "content": prompt_path.read_text(encoding="utf-8")},
        *trim_history(st.session_state.history, 5), {"role": "user", "content": prompt},
    ]
    # Delivery is excluded from this demo UI; the CLI retains the optional action tool.
    declarations = [tool for tool in load_tool_declarations(tools_path) if tool["name"] != "send"]
    record["enabled_tools"] = [tool["name"] for tool in declarations]
    try:
        with st.spinner("Đang xử lý yêu cầu…"):
            result = run_model_tool_loop(provider=make_provider("gemini"), messages=messages,
                tools=to_openai_tools(declarations), model=model, max_tool_rounds=4)
        record.update(result)
        st.session_state.history.extend([
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": result["assistant_text"]},
        ])
    except Exception as exc:
        record.update(status="provider_error", assistant_text=f"Kết nối thất bại ({type(exc).__name__}). Kiểm tra API key, model và hạn mức rồi thử lại.")
    record["ended_at"] = now_iso()
    transcript["turns"].append(record)
    write_transcript(ROOT / "transcripts" / f"{transcript['transcript_id']}.transcript.json", transcript)
    st.rerun()

if transcript["turns"]:
    st.download_button("Tải transcript JSON", json.dumps(transcript, ensure_ascii=False, indent=2, default=str),
        file_name=f"{transcript['transcript_id']}.transcript.json", mime="application/json")
