from pathlib import Path

from streamlit.testing.v1 import AppTest

import chat


def test_chat_turn_persists_transcript_and_reset_starts_fresh(monkeypatch):
    saved = []
    monkeypatch.setattr(chat, "write_transcript", lambda path, transcript: saved.append((path, len(transcript["turns"]))))
    monkeypatch.setattr(chat, "run_model_tool_loop", lambda **kwargs: {
        "status": "waiting_for_user", "assistant_text": "Which URL?",
        "rounds": [], "tool_events": [{"tool": "clarify", "result": {"awaiting_user": True}}],
    })
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    assert not app.exception
    app.chat_input[0].set_value("Summarize this article").run()
    assert not app.exception
    assert len(app.chat_message) == 2
    assert saved[0][1] == 1
    assert saved[0][0].suffix == ".json"
    assert app.session_state["history"][-1]["content"] == "Which URL?"
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert app.session_state["transcript"]["turns"] == []


def test_provider_error_is_shown_without_leaking_exception_details(monkeypatch):
    monkeypatch.setattr(chat, "write_transcript", lambda *args: None)
    def fail(**kwargs):
        raise RuntimeError("secret-value-do-not-display")
    monkeypatch.setattr(chat, "run_model_tool_loop", fail)
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
    app.chat_input[0].set_value("Research").run()
    assert not app.exception
    turn = app.session_state["transcript"]["turns"][0]
    assert turn["status"] == "provider_error"
    assert "secret-value" not in turn["assistant_text"]
