# 📄 FreeAI CV Maker

**100% Free • AI-Powered • ATS-Optimized Resume & CV Builder**

No subscription. No paywall. No watermarks. No account required. Privacy-first.

A complete free alternative to BetterCV, Resume.io, Kickresume, Enhancv and similar tools — built entirely in Python with Streamlit.

---

## ✨ Features (All Free Forever)

| Feature | Description |
|---------|-------------|
| **AI Writing Assistant** | Generate professional summaries, rewrite bullets, suggest skills |
| **ATS Score Checker** | Paste any job description → get keyword match score + missing terms |
| **Job Tailoring** | Optimize content against specific job postings |
| **Cover Letter Generator** | AI-written personalized cover letters |
| **6 Professional Templates** | Modern, Classic, Minimal, Executive, Technical, Creative |
| **6 Color Schemes** | Indigo, Teal, Slate, Rose, Emerald, Amber |
| **Live Preview** | See your resume update as you type |
| **Instant PDF Export** | Clean, ATS-friendly PDF — zero watermarks |
| **Multiple Sections** | Personal, Summary, Experience, Education, Skills, Projects, Certifications |
| **Save / Load** | Export & import your data as JSON |
| **Privacy First** | Data stays in your browser session. No server storage. |
| **Optional Real AI** | Use free Groq API (Llama 3.3) or built-in smart fallbacks |

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🤖 AI Setup (Optional but Recommended)

1. Go to [https://console.groq.com](https://console.groq.com)
2. Create a free account
3. Generate an API key (free tier is very generous)
4. Paste the key in the sidebar of the app

Without a key the app still works using high-quality template-based generation.

---

## 📁 Project Structure

```
free_ai_cv_maker/
├── app.py              # Main Streamlit application (complete)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🎯 How it compares to BetterCV

| Feature | BetterCV | FreeAI CV Maker |
|---------|----------|-----------------|
| Price | Subscription required for download | **100% Free forever** |
| PDF Download | Paywall | **Free, no watermark** |
| AI Suggestions | Yes (limited free) | **Unlimited (with free Groq key)** |
| ATS Checker | Limited | **Full keyword analysis** |
| Cover Letter | Yes | **Yes, free** |
| Templates | 40+ | 6 high-quality ATS-safe |
| Privacy | Account required | **No account, local session** |
| Open Source | No | **Yes (this code)** |

---

## 🔒 Privacy & Safety

- No user accounts
- No data stored on any server
- No tracking / analytics
- AI calls only happen if **you** provide an API key
- Your resume data lives only in the current browser session (or the JSON you download)

---

## 🛠️ Tech Stack

- **Frontend / UI**: Streamlit
- **PDF Generation**: ReportLab (pure Python)
- **AI**: Groq (Llama 3.3 70B) — free tier + smart rule-based fallbacks
- **Language**: Python 3.10+

---

## 📄 License

MIT — free to use, modify, and distribute.

---

Built with ❤️ so everyone can have a professional CV without paying.
