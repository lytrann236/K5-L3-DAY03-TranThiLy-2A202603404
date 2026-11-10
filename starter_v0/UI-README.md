# Run the Streamlit UI

From starter_v0 with the virtual environment activated:

```powershell
pip install -r requirements.txt
python -X utf8 -m streamlit run app.py --server.address 127.0.0.1
```

Open http://localhost:8501. Keys are read from the server-side .env file.
The UI uses Gemini, supports follow-up turns, shows tool results, and saves each
turn to transcripts/*.transcript.json. Download the current transcript from the UI.
Use the sidebar to start a new conversation or choose a model available to your account.
Telegram delivery is not exposed by this demo UI.

For a public demo, follow the Cloudflare Tunnel section in the parent README.
A localhost URL is not a public deployment link. Do not upload .env.

Demo sequence:
1. Ask to summarize an article without supplying a URL.
2. Supply https://example.com when the agent asks for it.
3. Ask to remove duplicate links from a supplied list.

The recorded CLI demo transcript is agent-driven scripted input against the real
Gemini API; a human should also try the UI before the classroom demonstration.
