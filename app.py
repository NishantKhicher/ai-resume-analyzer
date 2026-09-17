"""AI Resume Analyzer — Streamlit entry point.

Ties together PDF extraction, NLP normalization, resume parsing, and
resume-vs-job-description matching. Every step runs locally: no paid
APIs are used anywhere in this app.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from data.skills_database import SKILL_TO_CATEGORY
from modules.matcher import compare_skill_sets, compute_match_score, generate_suggestions
from modules.pdf_extractor import PDFExtractionError, extract_text_from_pdf
from modules.resume_parser import extract_skills, parse_resume
from modules.text_processor import clean_text, nlp_status_message, normalize_for_matching
from modules.visualizations import category_breakdown_chart, score_gauge_chart, skills_bar_chart

SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_data")

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

CUSTOM_CSS = """
<style>
.stApp { background-color: #f8fafc; }
.main-title { font-size: 2.1rem; font-weight: 700; color: #1e293b; margin-bottom: 0; }
.sub-title { color: #64748b; font-size: 1rem; margin-top: 0.2rem; }
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 14px 18px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def read_sample(filename: str) -> str:
    with open(os.path.join(SAMPLE_DIR, filename), encoding="utf-8") as f:
        return f.read()


def build_report_text(results: dict) -> str:
    data = results["resume_data"]
    lines = [
        "# Resume Analysis Report",
        "",
        f"**Match Score:** {results['score']}%",
        "",
        "## Matched Skills",
        ", ".join(results["matched"]) or "None detected",
        "",
        "## Missing Skills",
        ", ".join(results["missing"]) or "None — full coverage",
        "",
        "## Suggestions",
    ]
    lines += [f"- {tip}" for tip in results["suggestions"]]
    lines += ["", "## Education"]
    lines += [f"- {item}" for item in data["education"]] or ["- Not detected"]
    lines += ["", "## Experience"]
    lines += [f"- {e['description']}" for e in data["experience"]] or ["- Not detected"]
    lines += ["", "## Projects"]
    lines += [f"- {item}" for item in data["projects"]] or ["- Not detected"]
    lines += ["", "## Certifications"]
    lines += [f"- {item}" for item in data["certifications"]] or ["- Not detected"]
    return "\n".join(lines)


if "results" not in st.session_state:
    st.session_state.results = None

st.markdown('<p class="main-title">📄 AI Resume Analyzer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Upload a resume, paste a job description, and get an instant '
    "match score — 100% local processing, no paid APIs.</p>",
    unsafe_allow_html=True,
)
st.divider()

col_resume, col_jd = st.columns(2)

with col_resume:
    st.subheader("1. Upload Resume (PDF)")
    uploaded_file = st.file_uploader("Choose a PDF resume", type=["pdf"])
    use_sample_resume = st.checkbox("Use the sample resume instead", key="use_sample_resume")

with col_jd:
    st.subheader("2. Paste Job Description")
    jd_input = st.text_area(
        "Job description text",
        height=220,
        placeholder="Paste the job description here...",
    )
    use_sample_jd = st.checkbox("Use the sample job description instead", key="use_sample_jd")

analyze_clicked = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)

if analyze_clicked:
    if not use_sample_resume and uploaded_file is None:
        st.error("Please upload a resume PDF, or check 'Use the sample resume instead'.")
    elif not use_sample_jd and not jd_input.strip():
        st.error("Please paste a job description, or check 'Use the sample job description instead'.")
    else:
        try:
            if use_sample_resume:
                resume_raw_text = read_sample("sample_resume.txt")
            else:
                uploaded_file.seek(0)
                resume_raw_text = extract_text_from_pdf(uploaded_file.read())

            jd_raw_text = read_sample("sample_job_description.txt") if use_sample_jd else jd_input

            resume_text = clean_text(resume_raw_text)
            jd_text = clean_text(jd_raw_text)

            resume_data = parse_resume(resume_text)
            jd_skills = extract_skills(jd_text)
            matched, missing, extra = compare_skill_sets(resume_data["skills"], jd_skills)

            resume_norm = normalize_for_matching(resume_text)
            jd_norm = normalize_for_matching(jd_text)
            score = compute_match_score(resume_norm, jd_norm, resume_data["skills"], jd_skills)

            suggestions = generate_suggestions(resume_text, resume_data, missing, score)

            st.session_state.results = {
                "resume_data": resume_data,
                "jd_skills": jd_skills,
                "matched": matched,
                "missing": missing,
                "extra": extra,
                "score": score,
                "suggestions": suggestions,
            }
        except PDFExtractionError as exc:
            st.error(f"Couldn't read the PDF: {exc}")
            st.session_state.results = None
        except Exception as exc:  # noqa: BLE001 - surface any unexpected failure to the user
            st.error(f"Something went wrong while analyzing the resume: {exc}")
            st.session_state.results = None

results = st.session_state.results
if results:
    st.divider()
    score = results["score"]
    resume_data = results["resume_data"]
    matched, missing = results["matched"], results["missing"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Match Score", f"{score}%")
    m2.metric("Skills Matched", len(matched))
    m3.metric("Skills Missing", len(missing))
    m4.metric("Skills Detected in Resume", len(resume_data["skills"]))

    tab_overview, tab_skills, tab_details, tab_suggestions = st.tabs(
        ["📊 Overview", "🧩 Skills", "📄 Resume Details", "💡 Suggestions"]
    )

    with tab_overview:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(score_gauge_chart(score), use_container_width=True)
        with c2:
            st.plotly_chart(skills_bar_chart(matched, missing), use_container_width=True)
        category_chart = category_breakdown_chart(matched, missing, SKILL_TO_CATEGORY)
        if category_chart:
            st.plotly_chart(category_chart, use_container_width=True)

    with tab_skills:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Matched Skills**")
            for skill in matched:
                st.markdown(f"- {skill}")
            if not matched:
                st.caption("No overlapping skills detected.")
        with c2:
            st.markdown("**❌ Missing Skills**")
            for skill in missing:
                st.markdown(f"- {skill}")
            if not missing:
                st.caption("No missing skills — great coverage!")

    with tab_details:
        with st.expander(f"🎓 Education ({len(resume_data['education'])})", expanded=True):
            for item in resume_data["education"] or ["No education section detected."]:
                st.markdown(f"- {item}")
        with st.expander(f"💼 Experience ({len(resume_data['experience'])})"):
            entries = resume_data["experience"]
            if entries:
                for entry in entries:
                    duration = f" ({entry['duration']})" if entry["duration"] else ""
                    st.markdown(f"- {entry['description']}{duration}")
            else:
                st.caption("No experience section detected.")
        with st.expander(f"🚀 Projects ({len(resume_data['projects'])})"):
            for item in resume_data["projects"] or ["No projects section detected."]:
                st.markdown(f"- {item}")
        with st.expander(f"📜 Certifications ({len(resume_data['certifications'])})"):
            for item in resume_data["certifications"] or ["No certifications section detected."]:
                st.markdown(f"- {item}")

    with tab_suggestions:
        for tip in results["suggestions"]:
            st.info(tip)

    st.download_button(
        "⬇️ Download Report (Markdown)",
        data=build_report_text(results),
        file_name="resume_analysis_report.md",
        mime="text/markdown",
        use_container_width=True,
    )

st.divider()
st.caption(f"🔒 100% local processing — no paid APIs used. {nlp_status_message()}")
