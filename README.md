# 📄 AI Resume Analyzer

A Streamlit web app that compares a resume (PDF) against a job description
and returns a match score, a skill gap analysis, and improvement
suggestions — using classic, fully local NLP and machine learning. No
paid APIs, no external services, no API keys required.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-ff4b4b)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 📤 **Upload a PDF resume** and extract its text automatically (PyMuPDF).
- 🧠 **NLP-powered parsing** (spaCy) to clean and normalize resume text.
- 🔍 **Automatic detection** of skills, education, experience, projects,
  and certifications.
- 📋 **Paste any job description** to compare against.
- 📊 **Resume–JD Match Score (0–100)**, blending skill overlap with
  TF-IDF text similarity (scikit-learn).
- ✅❌ **Matched vs. missing skills**, broken down by category.
- 💡 **Actionable suggestions** for improving the resume.
- 📈 **Clean, interactive charts** (Plotly) — score gauge, skills bar
  chart, category breakdown.
- 📥 **Downloadable Markdown report** of the full analysis.
- 🧪 **Sample resume & job description included** — try the app with one
  click, no files needed.
- 🔒 **100% local processing** — nothing leaves your machine, no paid APIs.

## 🖼️ Screenshots

> Run the app locally (see [Installation](#-installation)) and drop your
> own screenshots into `assets/`, then update the paths below — e.g.
> `assets/overview.png`, `assets/skills.png`.

```
assets/
├── overview.png     ← Match score + charts tab
├── skills.png       ← Matched vs missing skills tab
└── suggestions.png  ← Suggestions tab
```

## 🧰 Tech Stack

| Purpose                    | Library         |
|-----------------------------|-----------------|
| Web UI                      | Streamlit       |
| PDF text extraction         | PyMuPDF (fitz)  |
| NLP (cleaning, lemmatizing) | spaCy           |
| Matching / scoring          | scikit-learn (TF-IDF + cosine similarity) |
| Data handling               | pandas          |
| Charts                      | Plotly          |

## 📁 Project Structure

```
resume-analyzer/
├── app.py                          # Streamlit UI — ties every module together
├── requirements.txt
├── .gitignore
├── LICENSE
├── README.md
├── modules/
│   ├── pdf_extractor.py            # PDF → raw text (PyMuPDF)
│   ├── text_processor.py           # Text cleaning + spaCy normalization
│   ├── resume_parser.py            # Section splitting + skill/education/
│   │                                 experience/project/certification extraction
│   ├── matcher.py                  # TF-IDF similarity, skill-gap analysis,
│   │                                 suggestion generation
│   └── visualizations.py           # Plotly chart builders
├── data/
│   └── skills_database.py          # Curated skills list, grouped by category
├── sample_data/
│   ├── sample_resume.txt
│   ├── sample_job_description.txt
│   └── generate_sample_pdf.py      # Turns the sample resume into a real PDF
├── tests/
│   └── test_core.py                # Self-test for parsing & matching logic
└── assets/                         # Put your screenshots here
```

## ⚙️ How It Works

1. **PDF extraction** (`modules/pdf_extractor.py`) — PyMuPDF opens the
   uploaded PDF in memory and pulls raw text from every page.
2. **Cleaning & NLP** (`modules/text_processor.py`) — whitespace is
   normalized, and spaCy lemmatizes the text for more forgiving matching.
   If spaCy's model isn't downloaded, the app **degrades gracefully** to
   plain lowercase text instead of crashing.
3. **Parsing** (`modules/resume_parser.py`) — the resume is split into
   sections (Education, Experience, Projects, Certifications, Skills)
   using header patterns, then each section is parsed with rules suited
   to it (e.g. date ranges signal a new job entry under Experience).
   Skills are detected across the *whole* resume using a curated skills
   database (`data/skills_database.py`) so skills mentioned inside
   project descriptions still count.
4. **Matching** (`modules/matcher.py`) — the same skill detection runs on
   the job description. The final score blends:
   - **Skill overlap** (60%): the percentage of the JD's required skills
     that also appear in the resume.
   - **Text similarity** (40%): TF-IDF cosine similarity between the two
     documents, which captures overlap beyond the fixed skills list.
   Rule-based suggestions are then generated from missing skills, resume
   length, presence of quantifiable achievements, and missing sections.
5. **Visualization** (`modules/visualizations.py`) — Plotly renders the
   score as a gauge, and skills as bar charts, inside `app.py`'s tabs.

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/resume-analyzer.git
cd resume-analyzer

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download the spaCy language model (one-time, ~13 MB)
python -m spacy download en_core_web_sm

# 5. (Optional) Generate a sample PDF resume for testing
python sample_data/generate_sample_pdf.py

# 6. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

> **Note:** Step 4 is optional — the app still works without it (skill
> detection and scoring don't require the model), but lemmatization-based
> matching improves with it installed.

## 🖱️ Usage

1. Upload a PDF resume, or check **"Use the sample resume instead"**.
2. Paste a job description, or check **"Use the sample job description
   instead"**.
3. Click **Analyze Resume**.
4. Explore the **Overview**, **Skills**, **Resume Details**, and
   **Suggestions** tabs.
5. Click **Download Report** to save the analysis as Markdown.

## 🧪 Sample Data

`sample_data/` contains a fictional resume and a matching job posting so
you (or anyone cloning the repo) can try the app immediately:

- `sample_resume.txt` — a fictional BCA graduate's resume.
- `sample_job_description.txt` — a Junior Python Developer role.
- `generate_sample_pdf.py` — converts the sample resume into an actual
  PDF using PyMuPDF, for testing the upload flow end-to-end.

## ✅ Running the Tests

A lightweight, dependency-light self-test checks that parsing, skill
detection, and scoring behave as expected:

```bash
python tests/test_core.py
```

## 🔭 Limitations & Future Improvements

- Section detection relies on common header wording — resumes with very
  unconventional formatting may parse less accurately.
- The skills database is a curated list (`data/skills_database.py`);
  extending it with more roles/domains improves detection coverage.
- Scanned/image-only PDFs aren't supported — the text layer must be
  extractable (an OCR step could be added for these).
- Possible next steps: multi-resume batch comparison, exportable PDF
  reports, and a broader/expandable skills taxonomy.

## 📄 License

Released under the [MIT License](LICENSE).
