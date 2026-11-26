import io
import os
from datetime import datetime
import requests
import streamlit as st

st.set_page_config(page_title="CareerMate AI", page_icon="✦", layout="wide")

# Streamlit Cloud Secrets are preferred. Environment variables work for local testing.
OPENAI_API_KEY = ""
try:
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = ""
try:
    OPENAI_MODEL = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")
except Exception:
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_MODEL = OPENAI_MODEL or "gpt-4o-mini"

st.markdown("""
<style>
:root { color-scheme: light; }
.stApp { background: linear-gradient(135deg,#fbf8f4 0%,#f4eee7 55%,#fffaf5 100%); }
.block-container { max-width: 1180px; padding-top: 2rem; }
.brand { font-size: 1.25rem; font-weight: 800; color: #4b2b24; letter-spacing: .02em; }
.brand span { color: #b58a4a; }
.kicker { color:#9a7442; font-size:.78rem; font-weight:700; letter-spacing:.18em; }
.hero { padding: 1.8rem 2rem; border-radius: 24px; background: #4b2b24; color:#fffaf4; margin: 1rem 0 1.5rem; }
.hero h1 { font-size: clamp(2.2rem,5vw,3.5rem); line-height:1.05; margin:.4rem 0; color:#fffaf4; }
.hero em { color:#e5c58e; font-style:normal; }
.hero p { color:#e9ddd2; max-width:650px; }
div[data-testid="stMetric"] { background:#fffaf5; border:1px solid #e8dccc; border-radius:16px; padding:14px; }
.job-card { background:#fffdf9; border:1px solid #eadfce; border-radius:16px; padding:18px 20px; margin:10px 0; }
.job-card h3 { color:#4b2b24; margin:0 0 6px; font-size:1.1rem; }
.job-meta { color:#78685b; font-size:.9rem; }
.small-note { color:#76685d; font-size:.85rem; }
.stButton>button[kind="primary"] { background:#6b3e30; border-color:#6b3e30; color:white; border-radius:10px; }
a { color:#946a31 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="brand">✦ CareerMate <span>AI</span></div><div class="kicker">YOUR PERSONAL CAREER AGENT</div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero">
  <div class="kicker">CAREER, MADE CLEAR</div>
  <h1>Find your next<br><em>opportunity.</em></h1>
  <p>Search real job listings, review your resume, and prepare stronger applications with AI-powered career support.</p>
</div>
""", unsafe_allow_html=True)

def get_ai_client():
    if not OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Could not initialize AI client: {e}")
        return None

def ask_ai(system_prompt, user_prompt):
    client = get_ai_client()
    if client is None:
        raise RuntimeError("AI is not configured yet. The app owner needs to add OPENAI_API_KEY in Streamlit Cloud → Settings → Secrets.")
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0.3,
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_prompt}
        ]
    )
    return (response.choices[0].message.content or "").strip()

def extract_resume(uploaded):
    name = uploaded.name.lower()
    data = uploaded.getvalue()
    if name.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Please upload PDF, DOCX, or TXT.")

def load_jobs(query, location):
    params = {"search": query or "entry level"}
    if location and "pakistan" in location.lower():
        params["location"] = "Pakistan"
    response = requests.get("https://remotive.com/api/remote-jobs", params=params, timeout=25,
                            headers={"User-Agent":"CareerMateAI/1.0"})
    response.raise_for_status()
    data = response.json()
    jobs = []
    for j in (data.get("jobs") or [])[:30]:
        jobs.append({
            "title": j.get("title") or "Untitled role",
            "company": j.get("company_name") or "Company not specified",
            "location": j.get("candidate_required_location") or "Remote",
            "type": j.get("job_type") or "Not specified",
            "description": j.get("description") or "",
            "posted": (j.get("publication_date") or "")[:10],
            "url": j.get("url") or "",
            "source": "Remotive"
        })
    return jobs

tab_jobs, tab_resume, tab_ai = st.tabs(["🔎 Live Jobs", "📄 Resume Analysis", "✦ AI Career Assistant"])

with tab_jobs:
    st.subheader("Find live remote jobs")
    st.caption("Listings are retrieved from Remotive's real remote-job feed. Vacancies may expire; confirm on the employer's original page.")
    c1, c2, c3 = st.columns([2,1.5,1])
    with c1: query = st.text_input("Job title or skill", placeholder="e.g. Python, graphic designer")
    with c2: location = st.text_input("Location preference", placeholder="Remote, Pakistan")
    with c3:
        st.write("")
        st.write("")
        search = st.button("Search jobs", type="primary", use_container_width=True)
    if search:
        with st.spinner("Searching live listings..."):
            try:
                st.session_state["jobs"] = load_jobs(query, location)
                st.session_state["job_query"] = query or "entry level"
            except Exception as e:
                st.error(f"Could not fetch jobs right now. Please try again later. Details: {e}")
                st.session_state["jobs"] = []
    jobs = st.session_state.get("jobs", [])
    if jobs:
        st.success(f"{len(jobs)} listing(s) returned by Remotive.")
        for j in jobs:
            with st.container(border=True):
                st.markdown(f"### {j['title']}")
                st.markdown(f"**{j['company']}** · {j['location']} · {j['type']}")
                if j["posted"]: st.caption(f"Posted: {j['posted']} · Source: {j['source']}")
                if j["url"]: st.link_button("View / Apply ↗", j["url"])
                with st.expander("Job description"):
                    st.markdown(j["description"][:12000] or "Description not provided.")
                if st.button("Prepare application for this job", key="prepare_"+str(j["title"])+str(j["company"])):
                    st.session_state["selected_job"] = j
                    st.info("Selected. Open the AI Career Assistant tab to draft application materials.")
    elif search:
        st.info("No matching listings found. Try a broader keyword such as 'developer' or 'marketing'.")

with tab_resume:
    st.subheader("AI resume analysis")
    st.caption("Upload a text-based PDF, DOCX, or TXT resume. Scanned image PDFs may not extract correctly. Your resume text is sent to the configured AI provider when you click Analyze.")
    resume_file = st.file_uploader("Choose your resume", type=["pdf","docx","txt"], key="resume_upload")
    role = st.text_input("Target role", placeholder="e.g. Junior Python Developer")
    resume_location = st.text_input("Preferred location", placeholder="e.g. Remote, Pakistan")
    if st.button("Analyze resume", type="primary"):
        if not resume_file:
            st.warning("Please choose a resume file first.")
        elif not OPENAI_API_KEY:
            st.error("AI is not configured. Ask the app owner to add the OpenAI key in Streamlit Cloud Secrets.")
        else:
            try:
                resume_text = extract_resume(resume_file)[:24000].strip()
                if len(resume_text) < 80:
                    st.error("Not enough text could be extracted. Try a text-based PDF or DOCX, not a scanned image.")
                else:
                    with st.spinner("Analyzing resume..."):
                        result = ask_ai(
                            "You are a careful career coach. Analyze only the supplied resume. Do not invent skills, qualifications, metrics, or experience. Be supportive and practical. ATS compatibility is a qualitative estimate, never guaranteed.",
                            f"Target role: {role or 'suitable entry-level role'}\nPreferred location: {resume_location}\nResume text:\n{resume_text}\n\nReturn: 1) short profile summary 2) evidenced skills 3) strengths 4) improvement opportunities 5) suggested resume bullet rewrites without fabricated achievements 6) role alignment low/medium/high with explanation 7) missing keywords to consider only if truthful."
                        )
                    st.markdown("### Resume analysis")
                    st.markdown(result)
            except Exception as e:
                st.error(f"Resume analysis failed: {e}")

with tab_ai:
    st.subheader("CareerMate AI assistant")
    selected = st.session_state.get("selected_job")
    if selected:
        st.info(f"Selected job: {selected['title']} at {selected['company']}")
    default_prompt = ""
    if selected:
        default_prompt = f"Write a truthful, tailored cover letter for {selected['title']} at {selected['company']}. Job description:\n{selected['description'][:8000]}"
    prompt = st.text_area("Ask for a cover letter, interview practice, resume improvements, or a skill-gap plan", value=default_prompt, height=180,
                          placeholder="Example: Create 5 interview questions for a junior data analyst role and provide sample answers.")
    if st.button("Generate AI answer", type="primary"):
        if not prompt.strip():
            st.warning("Please enter a request.")
        elif not OPENAI_API_KEY:
            st.error("AI is not configured. The app owner needs to add OPENAI_API_KEY in Streamlit Cloud Secrets.")
        else:
            try:
                with st.spinner("Generating helpful career guidance..."):
                    answer = ask_ai(
                        "You are CareerMate AI, a truthful career assistant. Help with job search strategy, resumes, cover letters, and interview practice. Never invent achievements, credentials, or job listings. Do not claim to apply for jobs. Keep advice actionable.",
                        prompt.strip()[:24000]
                    )
                st.markdown("### Your AI response")
                st.markdown(answer)
            except Exception as e:
                st.error(f"AI generation failed: {e}")

st.divider()
st.caption("CareerMate AI · Remote job listings provided by Remotive · AI features require the app owner's securely configured API key. Never upload sensitive information unless you consent to AI processing.")
