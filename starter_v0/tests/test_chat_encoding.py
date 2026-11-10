import io

from chat import run_model_tool_loop
from providers.base import ModelResponse, ToolCall


def test_unicode_tool_arguments_work_with_windows_console_encoding(monkeypatch):
    output = io.BytesIO()
    console = io.TextIOWrapper(output, encoding="cp1252")
    monkeypatch.setattr("sys.stdout", console)

    class Provider:
        def complete(self, *args, **kwargs):
            return ModelResponse(text=None, tool_calls=[ToolCall("clarify", {
                "question": "Bạn muốn đọc bài viết nào?", "response_type": "text",
            })])

    result = run_model_tool_loop(provider=Provider(), messages=[], tools=[],
                                 model=None, max_tool_rounds=1)
    console.flush()
    assert result["status"] == "waiting_for_user"
    assert result["assistant_text"] == "Bạn muốn đọc bài viết nào?"
    assert output.getvalue().decode("ascii").startswith("Tool clarify(")
