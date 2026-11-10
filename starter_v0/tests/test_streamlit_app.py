from pathlib import Path

from streamlit.testing.v1 import AppTest

import chat
import pytest


@pytest.mark.parametrize("version", ["v1", "v2", "v3"])
def test_version_selection_uses_snapshot_and_resets_history(monkeypatch, version):
    captured = []
    monkeypatch.setattr(chat, "write_transcript", lambda *args: None)
    def complete(**kwargs):
        captured.append(kwargs)
        return {"status": "answered", "assistant_text": "Done", "rounds": [], "tool_events": []}
    monkeypatch.setattr(chat, "run_model_tool_loop", complete)
    root = Path(__file__).resolve().parents[1]
    app = AppTest.from_file(str(root / "app.py")).run()
    assert app.sidebar.selectbox[0].options == ["v1", "v2", "v3"]
    assert app.sidebar.selectbox[0].value == "v3"
    if version == "v3":
        app.sidebar.selectbox[0].select("v1").run()
    app.chat_input[0].set_value("Original conversation").run()
    app.sidebar.selectbox[0].select(version).run()
    assert not app.exception
    assert app.session_state["history"] == []
    assert app.session_state["transcript"]["version"] == ("v3-final" if version == "v3" else version)
    app.chat_input[0].set_value("New conversation").run()
    folder = root / "artifacts" if version == "v3" else root / "artifacts/versions" / version
    assert captured[-1]["messages"][0]["content"] == (folder / "system_prompt.md").read_text(encoding="utf-8")
    assert len(captured[-1]["messages"]) == 2
    names = [tool["function"]["name"] for tool in captured[-1]["tools"]]
    assert ("deduplicate" in names) == (version == "v3")
    assert ("stock_quote" in names) == (version == "v3")
    from versioning import build_artifact_version
    expected = build_artifact_version(version, folder / "system_prompt.md", folder / "tools.yaml")
    assert app.session_state["transcript"]["prompt_hash"] == expected.prompt_hash
    assert app.session_state["transcript"]["tools_hash"] == expected.tools_hash
    app.sidebar.button[0].click().run()
    assert app.sidebar.selectbox[0].value == version
    assert app.session_state["transcript"]["turns"] == []


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
