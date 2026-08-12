"""
FreeAI CV Maker - 100% Free AI-Powered Resume & CV Builder
No subscription • No paywall • No watermarks • Privacy-first
Inspired by BetterCV and other premium builders, but completely free forever.
Built with Python + Streamlit + ReportLab
"""

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
import requests
import os

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="FreeAI CV Maker — 100% Free AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0.5rem 0 0 0;
    }
    
    .feature-badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.3rem;
        backdrop-filter: blur(10px);
    }
    
    .section-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .template-card {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        background: white;
    }
    
    .template-card:hover, .template-card.selected {
        border-color: #667eea;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    .preview-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1.5rem;
        min-height: 600px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    
    .ai-box {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
        border: 1px solid #c7d2fe;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .success-banner {
        background: linear-gradient(90deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
    }
    
    .free-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%);
    }
    
    div[data-testid="stSidebar"] * {
        color: #e0e7ff !important;
    }
    
    div[data-testid="stSidebar"] .stSelectbox label,
    div[data-testid="stSidebar"] .stRadio label {
        color: #c7d2fe !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE INIT ====================
def init_session_state():
    defaults = {
        "personal": {
            "full_name": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "website": "",
            "github": "",
            "job_title": ""
        },
        "summary": "",
        "experiences": [],
        "education": [],
        "skills": {"technical": [], "soft": [], "languages": []},
        "projects": [],
        "certifications": [],
        "template": "modern",
        "color_scheme": "indigo",
        "font_size": "medium",
        "ai_api_key": "",
        "ai_provider": "groq",
        "job_description": "",
        "ats_score": None,
        "cover_letter": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ==================== COLOR SCHEMES ====================
COLOR_SCHEMES = {
    "indigo": {"primary": "#4f46e5", "secondary": "#6366f1", "accent": "#818cf8", "text": "#1e1b4b"},
    "teal": {"primary": "#0d9488", "secondary": "#14b8a6", "accent": "#5eead4", "text": "#134e4a"},
    "slate": {"primary": "#334155", "secondary": "#475569", "accent": "#64748b", "text": "#0f172a"},
    "rose": {"primary": "#e11d48", "secondary": "#f43f5e", "accent": "#fb7185", "text": "#4c0519"},
    "emerald": {"primary": "#059669", "secondary": "#10b981", "accent": "#34d399", "text": "#064e3b"},
    "amber": {"primary": "#d97706", "secondary": "#f59e0b", "accent": "#fbbf24", "text": "#451a03"},
}

# ==================== AI HELPERS ====================
def call_ai(prompt: str, system: str = "You are an expert professional resume writer and career coach. Be concise, use strong action verbs, quantify achievements when possible, and keep language ATS-friendly.") -> str:
    """Call free AI provider (Groq recommended - free tier with Llama models)"""
    api_key = st.session_state.get("ai_api_key", "").strip()
    provider = st.session_state.get("ai_provider", "groq")
    
    if not api_key:
        return generate_fallback_ai(prompt)
    
    try:
        if provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = "llama-3.3-70b-versatile"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            else:
                return f"[AI Error {resp.status_code}] Using fallback. Check your Groq API key."
        else:
            return generate_fallback_ai(prompt)
    except Exception as e:
        return f"[Connection error] {str(e)[:100]}. Using smart fallback generator."

def generate_fallback_ai(prompt: str) -> str:
    """Smart rule-based + template AI when no API key (still useful)"""
    prompt_lower = prompt.lower()
    
    if "summary" in prompt_lower or "professional summary" in prompt_lower:
        return (
            "Results-driven professional with proven expertise in delivering high-impact solutions. "
            "Skilled in strategic planning, cross-functional collaboration, and process optimization. "
            "Passionate about driving measurable business outcomes and continuous improvement. "
            "Eager to contribute strong analytical and leadership abilities to a forward-thinking organization."
        )
    
    if "bullet" in prompt_lower or "experience" in prompt_lower or "rewrite" in prompt_lower:
        return (
            "• Spearheaded key initiatives that improved operational efficiency by 20% and reduced costs through data-driven process optimization.\n"
            "• Collaborated with cross-functional teams to deliver projects on time and under budget, resulting in enhanced stakeholder satisfaction.\n"
            "• Implemented innovative solutions that increased productivity and supported strategic business objectives."
        )
    
    if "skill" in prompt_lower:
        return "Python, Data Analysis, Project Management, Communication, Problem Solving, Leadership, Agile Methodologies, Microsoft Office, SQL, Team Collaboration"
    
    if "cover letter" in prompt_lower:
        return (
            "Dear Hiring Manager,\n\n"
            "I am excited to apply for this position. With my background and skills, I am confident I can make a strong contribution to your team.\n\n"
            "Throughout my career I have developed a solid foundation in the required areas and consistently delivered results. "
            "I am particularly drawn to this opportunity because of the chance to apply my expertise in a dynamic environment.\n\n"
            "I would welcome the opportunity to discuss how my experience aligns with your needs. Thank you for your consideration.\n\n"
            "Sincerely,\n[Your Name]"
        )
    
    return (
        "• Delivered high-quality results through careful planning and execution.\n"
        "• Demonstrated strong problem-solving skills and attention to detail.\n"
        "• Contributed to team success by sharing knowledge and supporting colleagues."
    )

def improve_text_with_ai(text: str, context: str = "resume bullet point") -> str:
    if not text.strip():
        return ""
    prompt = f"Rewrite and improve this {context} to be more impactful, professional, and ATS-friendly. Use strong action verbs and quantify if possible. Keep it concise (1-2 lines max). Return ONLY the improved version:\n\n{text}"
    return call_ai(prompt)

def generate_summary_ai(job_title: str, experiences: List, skills: Dict) -> str:
    exp_text = "\n".join([f"- {e.get('title','')} at {e.get('company','')}" for e in experiences[:3]])
    skills_text = ", ".join(skills.get("technical", [])[:8])
    prompt = f"""Write a powerful 3-4 sentence professional summary for a resume.
Job Title target: {job_title or 'Professional'}
Recent experience: {exp_text or 'Various roles'}
Key skills: {skills_text or 'Multiple professional skills'}
Make it achievement-oriented, confident, and ATS-optimized. No fluff."""
    return call_ai(prompt)

def generate_bullets_ai(title: str, company: str, description: str = "") -> str:
    prompt = f"""Generate 3-4 strong, quantified achievement-oriented bullet points for a resume experience entry.
Role: {title}
Company: {company}
Extra context: {description}
Use action verbs (Led, Developed, Optimized, Achieved...). Start each with • 
Return ONLY the bullet points."""
    return call_ai(prompt)

def generate_cover_letter_ai(personal: Dict, summary: str, job_desc: str) -> str:
    prompt = f"""Write a professional, concise cover letter (max 250 words).
Candidate: {personal.get('full_name','')} applying as {personal.get('job_title','')}
Summary: {summary[:300]}
Job description / requirements: {job_desc[:800] if job_desc else 'General professional role'}
Tone: confident, warm, professional. Structure: greeting, why interested + fit, key achievements, call to action, sign-off.
Return ONLY the letter body."""
    return call_ai(prompt)

def calculate_ats_score(resume_text: str, job_desc: str) -> Dict:
    """Simple but effective ATS keyword matching"""
    if not job_desc.strip():
        return {"score": 0, "matched": [], "missing": [], "message": "Paste a job description to get ATS score"}
    
    # Extract keywords (simple)
    stop = {"and", "the", "to", "of", "a", "in", "for", "with", "on", "at", "by", "an", "be", "is", "are", "as", "or", "from"}
    jd_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_desc.lower())) - stop
    resume_words = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower()))
    
    # Common important keywords
    important = [w for w in jd_words if len(w) > 4][:40]
    matched = [w for w in important if w in resume_words]
    missing = [w for w in important if w not in resume_words][:15]
    
    score = int((len(matched) / max(len(important), 1)) * 100) if important else 50
    score = min(98, max(15, score))
    
    return {
        "score": score,
        "matched": matched[:12],
        "missing": missing,
        "message": f"Matched {len(matched)} of {len(important)} key terms"
    }

# ==================== PDF GENERATION ====================
def create_pdf(data: Dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15*mm,
        leftMargin=15*mm,
        topMargin=12*mm,
        bottomMargin=12*mm
    )
    
    colors = COLOR_SCHEMES.get(data.get("color_scheme", "indigo"), COLOR_SCHEMES["indigo"])
    primary = HexColor(colors["primary"])
    text_color = HexColor(colors["text"])
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='Name',
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=primary,
        spaceAfter=2*mm,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='JobTitle',
        fontName='Helvetica',
        fontSize=11,
        textColor=HexColor("#475569"),
        spaceAfter=3*mm,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='Contact',
        fontName='Helvetica',
        fontSize=8.5,
        textColor=HexColor("#64748b"),
        spaceAfter=4*mm,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=primary,
        spaceBefore=4*mm,
        spaceAfter=2*mm,
        borderPadding=1
    ))
    styles.add(ParagraphStyle(
        name='BodyText2',
        fontName='Helvetica',
        fontSize=9,
        textColor=text_color,
        leading=12,
        spaceAfter=1.5*mm,
        alignment=TA_JUSTIFY
    ))
    styles.add(ParagraphStyle(
        name='JobHeader',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=text_color,
        spaceBefore=2*mm,
        spaceAfter=0.5*mm
    ))
    styles.add(ParagraphStyle(
        name='CompanyDate',
        fontName='Helvetica',
        fontSize=8.5,
        textColor=HexColor("#64748b"),
        spaceAfter=1*mm
    ))
    styles.add(ParagraphStyle(
        name='Bullet',
        fontName='Helvetica',
        fontSize=9,
        textColor=text_color,
        leftIndent=4*mm,
        leading=11.5,
        spaceAfter=0.8*mm
    ))
    styles.add(ParagraphStyle(
        name='Skill',
        fontName='Helvetica',
        fontSize=9,
        textColor=text_color,
        leading=12
    ))
    
    story = []
    personal = data.get("personal", {})
    
    # Header
    name = personal.get("full_name") or "Your Name"
    story.append(Paragraph(name.upper(), styles['Name']))
    
    job_title = personal.get("job_title") or ""
    if job_title:
        story.append(Paragraph(job_title, styles['JobTitle']))
    
    contact_parts = []
    if personal.get("email"): contact_parts.append(personal["email"])
    if personal.get("phone"): contact_parts.append(personal["phone"])
    if personal.get("location"): contact_parts.append(personal["location"])
    if personal.get("linkedin"): contact_parts.append(personal["linkedin"])
    if personal.get("website"): contact_parts.append(personal["website"])
    if personal.get("github"): contact_parts.append(personal["github"])
    
    if contact_parts:
        story.append(Paragraph("  •  ".join(contact_parts), styles['Contact']))
    
    # Divider
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary, spaceAfter=3*mm))
    
    # Summary
    if data.get("summary"):
        story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        story.append(Paragraph(data["summary"].replace("\n", "<br/>"), styles['BodyText2']))
    
    # Experience
    experiences = data.get("experiences", [])
    if experiences:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        
        for exp in experiences:
            title = exp.get("title", "")
            company = exp.get("company", "")
            location = exp.get("location", "")
            start = exp.get("start", "")
            end = exp.get("end", "Present")
            desc = exp.get("description", "")
            
            header = f"{title}"
            if company:
                header += f"  |  {company}"
            story.append(Paragraph(header, styles['JobHeader']))
            
            date_line = f"{start} – {end}"
            if location:
                date_line += f"  |  {location}"
            story.append(Paragraph(date_line, styles['CompanyDate']))
            
            # Bullets
            for line in desc.split("\n"):
                line = line.strip()
                if line:
                    if not line.startswith("•") and not line.startswith("-"):
                        line = "• " + line
                    story.append(Paragraph(line.replace("•", "•"), styles['Bullet']))
    
    # Education
    education = data.get("education", [])
    if education:
        story.append(Paragraph("EDUCATION", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        
        for edu in education:
            degree = edu.get("degree", "")
            school = edu.get("school", "")
            year = edu.get("year", "")
            details = edu.get("details", "")
            
            header = f"{degree}"
            if school:
                header += f"  |  {school}"
            story.append(Paragraph(header, styles['JobHeader']))
            if year:
                story.append(Paragraph(year, styles['CompanyDate']))
            if details:
                story.append(Paragraph(details, styles['BodyText2']))
    
    # Skills
    skills = data.get("skills", {})
    tech = skills.get("technical", [])
    soft = skills.get("soft", [])
    langs = skills.get("languages", [])
    
    if tech or soft or langs:
        story.append(Paragraph("SKILLS", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        
        if tech:
            story.append(Paragraph(f"<b>Technical:</b> {', '.join(tech)}", styles['Skill']))
        if soft:
            story.append(Paragraph(f"<b>Soft Skills:</b> {', '.join(soft)}", styles['Skill']))
        if langs:
            story.append(Paragraph(f"<b>Languages:</b> {', '.join(langs)}", styles['Skill']))
    
    # Projects
    projects = data.get("projects", [])
    if projects:
        story.append(Paragraph("PROJECTS", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        
        for proj in projects:
            name = proj.get("name", "")
            desc = proj.get("description", "")
            link = proj.get("link", "")
            header = name
            if link:
                header += f"  |  {link}"
            story.append(Paragraph(header, styles['JobHeader']))
            if desc:
                for line in desc.split("\n"):
                    line = line.strip()
                    if line:
                        if not line.startswith("•"):
                            line = "• " + line
                        story.append(Paragraph(line, styles['Bullet']))
    
    # Certifications
    certs = data.get("certifications", [])
    if certs:
        story.append(Paragraph("CERTIFICATIONS", styles['SectionHeader']))
        story.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#e2e8f0"), spaceAfter=2*mm))
        for cert in certs:
            story.append(Paragraph(f"• {cert}", styles['Bullet']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ==================== UI COMPONENTS ====================
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>📄 FreeAI CV Maker</h1>
        <p>100% Free • AI-Powered • ATS-Optimized • No Subscription • No Watermarks</p>
        <div style="margin-top:1rem;">
            <span class="feature-badge">🚀 AI Writing</span>
            <span class="feature-badge">🎯 ATS Score</span>
            <span class="feature-badge">📑 6 Templates</span>
            <span class="feature-badge">🔒 Privacy First</span>
            <span class="feature-badge">📥 Instant PDF</span>
            <span class="feature-badge">✉️ Cover Letter</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        st.session_state.template = st.selectbox(
            "Template Style",
            ["modern", "classic", "minimal", "executive", "technical", "creative"],
            index=["modern", "classic", "minimal", "executive", "technical", "creative"].index(st.session_state.template)
        )
        
        st.session_state.color_scheme = st.selectbox(
            "Color Scheme",
            list(COLOR_SCHEMES.keys()),
            index=list(COLOR_SCHEMES.keys()).index(st.session_state.color_scheme)
        )
        
        st.markdown("---")
        st.markdown("### 🤖 AI Configuration (Optional)")
        st.caption("Get a **free** Groq API key at console.groq.com — unlimited free tier with Llama 3.3")
        
        st.session_state.ai_provider = st.selectbox("AI Provider", ["groq", "fallback (no key)"], index=0)
        st.session_state.ai_api_key = st.text_input(
            "Groq API Key (optional)",
            value=st.session_state.ai_api_key,
            type="password",
            help="Leave empty to use built-in smart templates. Add free Groq key for real AI."
        )
        
        st.markdown("---")
        st.markdown("### 💾 Data")
        
        # Export JSON
        data_export = {
            "personal": st.session_state.personal,
            "summary": st.session_state.summary,
            "experiences": st.session_state.experiences,
            "education": st.session_state.education,
            "skills": st.session_state.skills,
            "projects": st.session_state.projects,
            "certifications": st.session_state.certifications,
            "template": st.session_state.template,
            "color_scheme": st.session_state.color_scheme
        }
        
        st.download_button(
            "⬇️ Download Resume Data (JSON)",
            data=json.dumps(data_export, indent=2),
            file_name="my_resume_data.json",
            mime="application/json",
            use_container_width=True
        )
        
        uploaded = st.file_uploader("⬆️ Load Resume Data (JSON)", type=["json"])
        if uploaded:
            try:
                loaded = json.load(uploaded)
                for k, v in loaded.items():
                    if k in st.session_state:
                        st.session_state[k] = v
                st.success("Data loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; font-size:0.8rem; opacity:0.8;">
            <p><span class="free-badge">100% FREE FOREVER</span></p>
            <p>No account • No tracking • Data stays in your browser</p>
            <p>Built with ❤️ in Python</p>
        </div>
        """, unsafe_allow_html=True)

def personal_info_section():
    st.subheader("👤 Personal Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.personal["full_name"] = st.text_input("Full Name *", st.session_state.personal["full_name"])
        st.session_state.personal["email"] = st.text_input("Email *", st.session_state.personal["email"])
        st.session_state.personal["phone"] = st.text_input("Phone", st.session_state.personal["phone"])
        st.session_state.personal["location"] = st.text_input("Location (City, Country)", st.session_state.personal["location"])
    
    with col2:
        st.session_state.personal["job_title"] = st.text_input("Target Job Title", st.session_state.personal["job_title"], help="e.g. Senior Software Engineer")
        st.session_state.personal["linkedin"] = st.text_input("LinkedIn URL", st.session_state.personal["linkedin"])
        st.session_state.personal["website"] = st.text_input("Portfolio / Website", st.session_state.personal["website"])
        st.session_state.personal["github"] = st.text_input("GitHub", st.session_state.personal["github"])

def summary_section():
    st.subheader("📝 Professional Summary")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✨ Generate with AI", key="gen_summary", use_container_width=True):
            with st.spinner("AI is writing your summary..."):
                st.session_state.summary = generate_summary_ai(
                    st.session_state.personal.get("job_title", ""),
                    st.session_state.experiences,
                    st.session_state.skills
                )
    
    st.session_state.summary = st.text_area(
        "Summary",
        st.session_state.summary,
        height=120,
        placeholder="Write a compelling 3-4 sentence professional summary highlighting your key strengths and career goals..."
    )
    
    if st.session_state.summary:
        if st.button("🔄 Improve with AI", key="improve_summary"):
            with st.spinner("Improving..."):
                st.session_state.summary = improve_text_with_ai(st.session_state.summary, "professional summary")
                st.rerun()

def experience_section():
    st.subheader("💼 Work Experience")
    
    if st.button("➕ Add Experience", key="add_exp"):
        st.session_state.experiences.append({
            "title": "", "company": "", "location": "",
            "start": "", "end": "Present", "description": ""
        })
        st.rerun()
    
    for i, exp in enumerate(st.session_state.experiences):
        with st.expander(f"Experience #{i+1}: {exp.get('title') or 'New Role'} @ {exp.get('company') or 'Company'}", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                exp["title"] = st.text_input("Job Title", exp["title"], key=f"title_{i}")
                exp["company"] = st.text_input("Company", exp["company"], key=f"company_{i}")
                exp["location"] = st.text_input("Location", exp["location"], key=f"loc_{i}")
            with c2:
                exp["start"] = st.text_input("Start Date", exp["start"], key=f"start_{i}", placeholder="Jan 2022")
                exp["end"] = st.text_input("End Date", exp["end"], key=f"end_{i}", placeholder="Present")
            
            exp["description"] = st.text_area(
                "Description / Achievements (one per line)",
                exp["description"],
                key=f"desc_{i}",
                height=100,
                placeholder="• Led a team of 5 to deliver...\n• Increased revenue by 25%..."
            )
            
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("✨ AI Generate Bullets", key=f"ai_bullets_{i}"):
                    with st.spinner("Generating strong bullets..."):
                        exp["description"] = generate_bullets_ai(exp["title"], exp["company"], exp["description"])
                        st.rerun()
            with b2:
                if st.button("🔄 AI Improve", key=f"ai_improve_{i}"):
                    with st.spinner("Improving..."):
                        exp["description"] = improve_text_with_ai(exp["description"], "resume experience bullets")
                        st.rerun()
            with b3:
                if st.button("🗑️ Remove", key=f"remove_exp_{i}"):
                    st.session_state.experiences.pop(i)
                    st.rerun()

def education_section():
    st.subheader("🎓 Education")
    
    if st.button("➕ Add Education", key="add_edu"):
        st.session_state.education.append({
            "degree": "", "school": "", "year": "", "details": ""
        })
        st.rerun()
    
    for i, edu in enumerate(st.session_state.education):
        with st.expander(f"Education #{i+1}: {edu.get('degree') or 'Degree'}", expanded=True):
            c1, c2 = st.columns(2)
            with c1:
                edu["degree"] = st.text_input("Degree / Certificate", edu["degree"], key=f"degree_{i}")
                edu["school"] = st.text_input("School / University", edu["school"], key=f"school_{i}")
            with c2:
                edu["year"] = st.text_input("Year / Duration", edu["year"], key=f"year_{i}", placeholder="2018 – 2022")
            edu["details"] = st.text_input("Details (GPA, honors, relevant coursework)", edu["details"], key=f"edetails_{i}")
            
            if st.button("🗑️ Remove", key=f"remove_edu_{i}"):
                st.session_state.education.pop(i)
                st.rerun()

def skills_section():
    st.subheader("🛠️ Skills")
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        tech_str = st.text_area(
            "Technical Skills (comma separated)",
            ", ".join(st.session_state.skills.get("technical", [])),
            key="tech_skills",
            height=80
        )
        st.session_state.skills["technical"] = [s.strip() for s in tech_str.split(",") if s.strip()]
    
    with c2:
        soft_str = st.text_area(
            "Soft Skills (comma separated)",
            ", ".join(st.session_state.skills.get("soft", [])),
            key="soft_skills",
            height=80
        )
        st.session_state.skills["soft"] = [s.strip() for s in soft_str.split(",") if s.strip()]
    
    with c3:
        lang_str = st.text_area(
            "Languages (comma separated)",
            ", ".join(st.session_state.skills.get("languages", [])),
            key="lang_skills",
            height=80
        )
        st.session_state.skills["languages"] = [s.strip() for s in lang_str.split(",") if s.strip()]
    
    if st.button("✨ AI Suggest Skills", key="ai_skills"):
        with st.spinner("Suggesting relevant skills..."):
            title = st.session_state.personal.get("job_title", "Professional")
            prompt = f"Suggest 12 relevant technical skills, 6 soft skills, and 3 languages for a {title} resume. Format as:\nTechnical: skill1, skill2, ...\nSoft: ...\nLanguages: ..."
            result = call_ai(prompt)
            # Parse simple
            for line in result.split("\n"):
                if "technical" in line.lower():
                    parts = line.split(":")[-1]
                    st.session_state.skills["technical"] = [s.strip() for s in parts.split(",") if s.strip()]
                elif "soft" in line.lower():
                    parts = line.split(":")[-1]
                    st.session_state.skills["soft"] = [s.strip() for s in parts.split(",") if s.strip()]
                elif "language" in line.lower():
                    parts = line.split(":")[-1]
                    st.session_state.skills["languages"] = [s.strip() for s in parts.split(",") if s.strip()]
            st.rerun()

def projects_section():
    st.subheader("🚀 Projects")
    
    if st.button("➕ Add Project", key="add_proj"):
        st.session_state.projects.append({"name": "", "description": "", "link": ""})
        st.rerun()
    
    for i, proj in enumerate(st.session_state.projects):
        with st.expander(f"Project #{i+1}: {proj.get('name') or 'New Project'}", expanded=True):
            proj["name"] = st.text_input("Project Name", proj["name"], key=f"pname_{i}")
            proj["link"] = st.text_input("Link (GitHub, live demo)", proj["link"], key=f"plink_{i}")
            proj["description"] = st.text_area("Description", proj["description"], key=f"pdesc_{i}", height=80)
            
            if st.button("🗑️ Remove", key=f"remove_proj_{i}"):
                st.session_state.projects.pop(i)
                st.rerun()

def certifications_section():
    st.subheader("🏅 Certifications & Awards")
    certs_str = st.text_area(
        "One per line",
        "\n".join(st.session_state.certifications),
        height=80,
        placeholder="AWS Certified Solutions Architect – 2024\nGoogle Data Analytics Certificate"
    )
    st.session_state.certifications = [c.strip() for c in certs_str.split("\n") if c.strip()]

def ats_and_tailor_section():
    st.subheader("🎯 ATS Optimizer & Job Tailoring")
    
    st.session_state.job_description = st.text_area(
        "Paste Job Description here",
        st.session_state.job_description,
        height=150,
        placeholder="Paste the full job description to get keyword match score and suggestions..."
    )
    
    if st.button("📊 Calculate ATS Score", use_container_width=True):
        # Build full text
        text_parts = [
            st.session_state.summary,
            " ".join([e.get("description", "") for e in st.session_state.experiences]),
            " ".join(st.session_state.skills.get("technical", [])),
            " ".join(st.session_state.skills.get("soft", [])),
            " ".join([p.get("description", "") for p in st.session_state.projects])
        ]
        full_text = " ".join(text_parts)
        st.session_state.ats_score = calculate_ats_score(full_text, st.session_state.job_description)
    
    if st.session_state.ats_score:
        score = st.session_state.ats_score["score"]
        color = "#10b981" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
        
        st.markdown(f"""
        <div style="background:#f8fafc; border-radius:12px; padding:1.5rem; border-left:6px solid {color};">
            <h2 style="margin:0; color:{color};">{score}% ATS Match</h2>
            <p style="margin:0.5rem 0;">{st.session_state.ats_score["message"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**✅ Matched Keywords**")
            st.write(", ".join(st.session_state.ats_score["matched"]) or "None yet")
        with c2:
            st.markdown("**⚠️ Missing Keywords** (consider adding)")
            st.write(", ".join(st.session_state.ats_score["missing"]) or "Great coverage!")

def cover_letter_section():
    st.subheader("✉️ AI Cover Letter Generator")
    
    if st.button("✨ Generate Cover Letter", use_container_width=True):
        with st.spinner("Writing a personalized cover letter..."):
            st.session_state.cover_letter = generate_cover_letter_ai(
                st.session_state.personal,
                st.session_state.summary,
                st.session_state.job_description
            )
    
    st.session_state.cover_letter = st.text_area(
        "Cover Letter",
        st.session_state.cover_letter,
        height=250,
        placeholder="Your AI-generated cover letter will appear here..."
    )
    
    if st.session_state.cover_letter:
        st.download_button(
            "⬇️ Download Cover Letter (TXT)",
            data=st.session_state.cover_letter,
            file_name="cover_letter.txt",
            mime="text/plain"
        )

def preview_and_download():
    st.subheader("👀 Live Preview & Download")
    
    # Simple text preview
    personal = st.session_state.personal
    st.markdown(f"""
    <div class="preview-box">
        <h2 style="color:#4f46e5; text-align:center; margin-bottom:0.2rem;">{personal.get('full_name') or 'Your Name'}</h2>
        <p style="text-align:center; color:#64748b; margin:0;">{personal.get('job_title') or ''}</p>
        <p style="text-align:center; font-size:0.85rem; color:#94a3b8;">
            {personal.get('email','')} • {personal.get('phone','')} • {personal.get('location','')}
        </p>
        <hr>
        <h4 style="color:#4f46e5;">PROFESSIONAL SUMMARY</h4>
        <p style="font-size:0.9rem;">{st.session_state.summary or '<i>Add a summary...</i>'}</p>
        
        <h4 style="color:#4f46e5;">EXPERIENCE</h4>
        {"".join([f"<p><b>{e.get('title','')}</b> — {e.get('company','')}<br><small>{e.get('start','')} – {e.get('end','')}</small><br>{e.get('description','')[:200].replace(chr(10), '<br>')}...</p>" for e in st.session_state.experiences[:2]]) or "<p><i>Add experience...</i></p>"}
        
        <h4 style="color:#4f46e5;">SKILLS</h4>
        <p style="font-size:0.9rem;">{', '.join(st.session_state.skills.get('technical', [])[:10]) or 'Add skills...'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📄 Generate PDF Resume", type="primary", use_container_width=True):
            with st.spinner("Creating beautiful PDF..."):
                pdf_bytes = create_pdf({
                    "personal": st.session_state.personal,
                    "summary": st.session_state.summary,
                    "experiences": st.session_state.experiences,
                    "education": st.session_state.education,
                    "skills": st.session_state.skills,
                    "projects": st.session_state.projects,
                    "certifications": st.session_state.certifications,
                    "color_scheme": st.session_state.color_scheme,
                    "template": st.session_state.template
                })
                st.session_state.pdf_bytes = pdf_bytes
                st.success("✅ PDF ready! Download below.")
    
    if "pdf_bytes" in st.session_state:
        st.download_button(
            label="⬇️ Download PDF (No Watermark)",
            data=st.session_state.pdf_bytes,
            file_name=f"{st.session_state.personal.get('full_name','Resume').replace(' ', '_')}_CV.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    st.info("💡 **Tip:** Your data never leaves this session unless you use the optional AI API key. Everything is 100% free and private.")

# ==================== MAIN APP ====================
def main():
    render_header()
    render_sidebar()
    
    # Tabs for organization
    tabs = st.tabs([
        "👤 Personal", 
        "📝 Summary", 
        "💼 Experience", 
        "🎓 Education", 
        "🛠️ Skills", 
        "🚀 Projects", 
        "🏅 Certs",
        "🎯 ATS Score",
        "✉️ Cover Letter",
        "📄 Preview & PDF"
    ])
    
    with tabs[0]:
        personal_info_section()
    with tabs[1]:
        summary_section()
    with tabs[2]:
        experience_section()
    with tabs[3]:
        education_section()
    with tabs[4]:
        skills_section()
    with tabs[5]:
        projects_section()
    with tabs[6]:
        certifications_section()
    with tabs[7]:
        ats_and_tailor_section()
    with tabs[8]:
        cover_letter_section()
    with tabs[9]:
        preview_and_download()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#64748b; font-size:0.85rem;">
        <p><strong>FreeAI CV Maker</strong> — Completely free alternative to BetterCV, Resume.io, Kickresume & others.</p>
        <p>All features unlocked • No credit card • No limits • Open & private • Built with Python</p>
        <p>Get free Groq API key for real AI: <a href="https://console.groq.com" target="_blank">console.groq.com</a></p>
    </div>
    
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
