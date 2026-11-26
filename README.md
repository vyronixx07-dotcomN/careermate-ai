# CareerMate AI — Streamlit Cloud version

This is the Streamlit conversion of the provided CareerMate AI Advanced project.

## Included
- Live remote job search through Remotive's public job feed (no job API key needed for the default feed).
- PDF, DOCX, and TXT resume text extraction.
- AI resume analysis and career assistant / cover-letter drafting through OpenAI.
- Responsive browser interface with tabs.

## Deploy online (no localhost for visitors)

1. Create/sign in to GitHub: https://github.com/
2. Create a new repository, for example `careermate-ai`.
3. Upload these project files to the repository root (`app.py`, `requirements.txt`, `.streamlit/` and this README).
4. Open https://share.streamlit.io/ and sign in with GitHub.
5. Click **Create app**, choose your repository, branch, and `app.py` as the main file.
6. Click **Deploy**. Streamlit will build the app and provide a public `*.streamlit.app` URL.
7. To enable AI, open the deployed app's **Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "paste-your-secret-key-here"
OPENAI_MODEL = "gpt-4o-mini"
```

Save secrets and reboot/redeploy the app. Do not commit the real API key into GitHub or place it in frontend code.

## API key and costs
- Live Remotive job search works without an OpenAI key.
- Resume analysis and AI answer generation require an OpenAI API key and API billing/credits. ChatGPT subscription and API billing are separate.
- The key is held in Streamlit Cloud Secrets, not shown to website visitors.
- Never share the secret key or upload it in a public repository.

## Run locally (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```
Local running is optional; after cloud deployment visitors open the public URL in Chrome without installing anything.

## Notes
- Remotive listings are real remote job postings, but availability can change. Verify each role on its original employer/application page.
- This app does not auto-apply to jobs.
- Text-based PDFs are supported; scanned image PDFs may need OCR.
- Resume text is sent to OpenAI when the user clicks AI analysis. Use only a resume you consent to process.
- Add authentication, usage limits, retention controls, and a database before using this as a production multi-user service.
