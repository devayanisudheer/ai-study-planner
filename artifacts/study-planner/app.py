"""
app.py — AI-Powered Personalized Study Planner
Rainbow UI, full dark/light mode support.
"""

import streamlit as st
from datetime import date, timedelta

st.set_page_config(
    page_title="Study Planner AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/icon?family=Material+Icons+Sharp');

html, body, [class*="css"], [class*="st-"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 920px; }

/* ── Rainbow hero ── */
.hero {
    background: linear-gradient(135deg,
        #FF0080 0%, #FF4500 15%, #FF8C00 28%,
        #FFD700 42%, #00C851 57%, #00BFFF 72%,
        #7B2FFF 85%, #FF0080 100%);
    background-size: 200% 200%;
    animation: rainbowShift 6s ease infinite;
    border-radius: 22px;
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 2rem;
    color: #fff !important;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(123,47,255,0.25);
}
@keyframes rainbowShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.hero::before {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -30px; left: 60px;
    width: 120px; height: 120px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.hero h1 {
    font-size: 2.1rem; font-weight: 800;
    margin: 0 0 0.4rem 0;
    color: #fff !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.hero p {
    font-size: 1rem; opacity: 0.92;
    margin: 0; color: #fff !important;
}

/* ── Step cards — solid bg so readable in both modes ── */
.step-card {
    background: var(--card-bg, #1a1a2e);
    border: 2px solid var(--card-border, #2e2e50);
    border-radius: 18px;
    padding: 1.6rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
}

/* Step badges — each a different rainbow color */
.badge {
    display: inline-flex; align-items: center;
    border-radius: 24px; padding: 0.3rem 1rem;
    font-size: 0.78rem; font-weight: 800;
    letter-spacing: 0.06em; text-transform: uppercase;
    margin-bottom: 0.85rem; color: #fff !important;
    text-shadow: 0 1px 4px rgba(0,0,0,0.2);
}
.badge-1 { background: linear-gradient(135deg, #FF0080, #FF4500); }
.badge-2 { background: linear-gradient(135deg, #FF8C00, #FFD700); color: #1a1a1a !important; text-shadow: none !important; }
.badge-3 { background: linear-gradient(135deg, #00C851, #00E5A0); }
.badge-4 { background: linear-gradient(135deg, #00BFFF, #7B2FFF); }
.badge-5 { background: linear-gradient(135deg, #7B2FFF, #FF0080); }

/* Card text — always visible */
.step-card p, .step-card span, .step-card label,
.step-card div:not([class*="stButton"]) {
    color: var(--text-main, #e0e0f0) !important;
}
.card-title {
    font-size: 1rem; font-weight: 700;
    color: var(--text-main, #e0e0f0) !important;
    margin-bottom: 0.5rem;
}

/* ── Progress bar ── */
.prog-wrap {
    background: rgba(255,255,255,0.1);
    border-radius: 50px; height: 12px;
    overflow: hidden; margin: 0.6rem 0;
    border: 1px solid rgba(255,255,255,0.08);
}
.prog-fill {
    height: 100%; border-radius: 50px;
    background: linear-gradient(90deg, #FF0080, #FF8C00, #FFD700, #00C851, #00BFFF, #7B2FFF);
    background-size: 200% 100%;
    animation: rainbowShift 3s linear infinite;
    transition: width 0.5s ease;
}
.prog-label {
    font-size: 0.85rem; font-weight: 800;
    background: linear-gradient(90deg, #FF0080, #7B2FFF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ── Stat boxes ── */
.stat-box {
    background: var(--card-bg, #1a1a2e);
    border: 2px solid var(--card-border, #2e2e50);
    border-radius: 14px; padding: 1rem;
    text-align: center;
}
.stat-num {
    font-size: 1.9rem; font-weight: 800;
    display: block;
}
.stat-lbl {
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: #aaa !important; display: block;
}
.num-purple { color: #b47fff !important; }
.num-green  { color: #00E5A0 !important; }
.num-red    { color: #FF6B8A !important; }

/* ── Day plan cards ── */
.day-card {
    border-radius: 14px; padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    background: var(--card-bg, #1a1a2e);
    border: 1.5px solid var(--card-border, #2e2e50);
}
.day-card-study    { border-left: 5px solid #7B2FFF; }
.day-card-revision { border-left: 5px solid #FF8C00; }
.day-card-buffer   { border-left: 5px solid #00C851; }
.day-type {
    font-size: 0.72rem; font-weight: 800;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 0.2rem;
}
.day-type-study    { color: #b47fff !important; }
.day-type-revision { color: #FFB347 !important; }
.day-type-buffer   { color: #00E5A0 !important; }
.day-heading {
    font-size: 1rem; font-weight: 700;
    color: var(--text-main, #e0e0f0) !important;
    margin-bottom: 0.4rem;
}
.day-topic {
    font-size: 0.875rem;
    color: var(--text-sub, #b0b0cc) !important;
    padding: 0.12rem 0;
}

/* ── Fix for Material Icons text-ligature overlap ──
   Streamlit renders icons as Material Icons font ligatures.
   When the font loads, the text (e.g. "upload", "_arrow_right") becomes
   an icon glyph. If the font is slow to load, the raw text shows briefly.
   We force the Material Icons font and hide the raw text spans cleanly. */

/* File uploader icon — hides the "upload" ligature text */
[data-testid="stFileUploaderDropzone"] [data-testid*="Icon"],
[data-testid="stFileUploaderDropzone"] .material-icons,
[data-testid="stFileUploaderDropzone"] .material-icons-sharp,
[data-testid="stFileUploaderDropzone"] span[data-testid="stIconMaterial"] {
    font-family: 'Material Icons Sharp', 'Material Icons' !important;
    font-size: 1.2rem !important;
    overflow: hidden !important;
    display: inline-block !important;
    width: 1.2rem !important;
    line-height: 1 !important;
}

/* Button icons inside file uploader and primary/secondary buttons */
[data-testid="stBaseButton-secondary"] span[data-testid="stIconMaterial"],
[data-testid="stBaseButton-primary"] span[data-testid="stIconMaterial"],
button span[data-testid="stIconMaterial"] {
    font-family: 'Material Icons Sharp', 'Material Icons' !important;
    font-size: 1rem !important;
    overflow: hidden !important;
    display: inline-block !important;
    width: 1rem !important;
    line-height: 1 !important;
}

/* Expander arrow icon — hides the "_arrow_right" ligature text */
[data-testid="stExpanderToggleIcon"],
.stExpander summary [data-testid="stIconMaterial"],
.stExpander summary span.material-icons,
.stExpander summary span.material-icons-sharp {
    font-family: 'Material Icons Sharp', 'Material Icons' !important;
    font-size: 1.1rem !important;
    overflow: hidden !important;
    display: inline-block !important;
    width: 1.1rem !important;
    line-height: 1 !important;
    vertical-align: middle !important;
}

/* Nuclear fallback: hide any remaining raw icon ligature text that bleeds */
[data-testid="stFileUploaderDropzoneInstructions"] svg,
[data-testid="stBaseButton-secondary"] svg,
[data-testid="stBaseButton-primary"] svg,
button[kind] svg,
.stExpander summary svg { display: none !important; }
summary span[data-testid] { gap: 0 !important; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
    border: none !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(123,47,255,0.3) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #7B2FFF, #FF0080) !important;
    color: white !important;
}

/* ── Light mode overrides ── */
@media (prefers-color-scheme: light) {
    :root {
        --card-bg: #ffffff;
        --card-border: #e0e0f0;
        --text-main: #1a1a2e;
        --text-sub: #444466;
    }
    .step-card { box-shadow: 0 4px 20px rgba(123,47,255,0.08); }
    .prog-wrap { background: #f0eeff; border-color: #d4cfff; }
}

/* ── Dark mode ── */
@media (prefers-color-scheme: dark) {
    :root {
        --card-bg: #16162a;
        --card-border: #2a2a4a;
        --text-main: #e8e8ff;
        --text-sub: #9999bb;
    }
}

/* Streamlit widget label fix */
.stCheckbox label, .stSlider label, .stDateInput label,
.stTextInput label, .stSelectbox label, .stTextArea label,
.stFileUploader label {
    color: var(--text-main, #e0e0f0) !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {"raw_text": "", "topics": [], "completed": {}, "plan": [], "step": 1}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📚 AI Study Planner</h1>
    <p>Upload your syllabus → extract every topic → tick what you've studied → get a rainbow study plan 🌈</p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    subject      = st.text_input("Subject / Course name", value="University Exam", key="subject")
    hours_per_day = st.slider("Study hours per day", 1, 12, 3, key="hours")
    st.markdown("---")
    st.markdown("### 🤖 AI *(optional)*")
    api_key      = st.text_input("Gemini API key", type="password", key="gemini_key",
                                  help="Leave blank — built-in planner still works great.")
    gemini_model = st.selectbox("Model", ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"], key="model")
    st.caption("No API key needed for a good plan.")
    st.markdown("---")
    if st.button("🔄 Reset everything", use_container_width=True):
        for k in ["raw_text", "topics", "completed", "plan", "step"]:
            del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Upload
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<div class="badge badge-1">📁 Step 1 · Upload Syllabus</div>', unsafe_allow_html=True)
st.markdown('<p class="card-title">Upload your syllabus as a <b>PDF</b> or <b>plain text file</b> — or paste the text directly.</p>', unsafe_allow_html=True)

col_up, col_paste = st.columns(2, gap="large")

with col_up:
    uploaded = st.file_uploader("Drop file here", type=["pdf","txt"], label_visibility="collapsed")
    if uploaded and st.button("Extract text from file", use_container_width=True):
        with st.spinner("Reading your syllabus…"):
            try:
                from extractor import extract_from_file
                text = extract_from_file(uploaded)
                st.session_state.update({"raw_text": text, "topics": [], "completed": {}, "plan": []})
                st.success(f"✅ Extracted {len(text):,} characters")
            except Exception as e:
                st.error(f"❌ {e}")

with col_paste:
    pasted = st.text_area("Paste syllabus text here", height=160, placeholder="Paste copied syllabus text…", label_visibility="collapsed")
    if st.button("Use pasted text", use_container_width=True):
        if pasted.strip():
            st.session_state.update({"raw_text": pasted.strip(), "topics": [], "completed": {}, "plan": []})
            st.success(f"✅ Got {len(pasted):,} characters")
        else:
            st.warning("Please paste some text first.")

if st.session_state["raw_text"]:
    with st.expander("👁️ Preview extracted text"):
        st.text(st.session_state["raw_text"][:1500] + ("…" if len(st.session_state["raw_text"]) > 1500 else ""))

st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Extract topics
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state["raw_text"]:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="badge badge-2">🔍 Step 2 · Extract Topics</div>', unsafe_allow_html=True)
    st.markdown('<p class="card-title">AI reads every line of your syllabus and pulls out each individual topic.</p>', unsafe_allow_html=True)

    max_topics = st.slider("Max topics to extract", 10, 100, 80, key="max_topics")

    if st.button("Extract all topics", use_container_width=True, type="primary"):
        with st.spinner("Extracting topics…"):
            try:
                from topic_parser import extract_topics
                topics = extract_topics(
                    st.session_state["raw_text"],
                    api_key=st.session_state.get("gemini_key", ""),
                    model=st.session_state.get("model", "gemini-1.5-flash"),
                    max_topics=max_topics,
                )
                if not topics:
                    st.warning("⚠️ No topics found. Try pasting the syllabus text directly.")
                else:
                    for t in topics:
                        if t not in st.session_state["completed"]:
                            st.session_state["completed"][t] = False
                    st.session_state["topics"] = topics
                    st.session_state["plan"] = []
                    st.success(f"✅ Found **{len(topics)}** topics!")
            except Exception as e:
                st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Mark completed
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("topics"):
    topics    = st.session_state["topics"]
    completed = st.session_state["completed"]

    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="badge badge-3">✅ Step 3 · Mark Completed Topics</div>', unsafe_allow_html=True)
    st.markdown('<p class="card-title">Tick every topic you\'ve <b>already studied</b>. Unticked ones go into your plan.</p>', unsafe_allow_html=True)

    n_done = sum(1 for v in completed.values() if v)
    pct    = int(n_done / len(topics) * 100) if topics else 0

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
        <div class="prog-wrap" style="flex:1;">
            <div class="prog-fill" style="width:{pct}%;"></div>
        </div>
        <span class="prog-label">{n_done}/{len(topics)} done</span>
    </div>
    """, unsafe_allow_html=True)

    qa, qb = st.columns(2)
    with qa:
        if st.button("✅ Mark all done", use_container_width=True):
            for t in topics: st.session_state["completed"][t] = True
            st.rerun()
    with qb:
        if st.button("↩️ Clear all", use_container_width=True):
            for t in topics: st.session_state["completed"][t] = False
            st.rerun()

    half  = (len(topics) + 1) // 2
    ca, cb = st.columns(2, gap="medium")
    for i, topic in enumerate(topics):
        col = ca if i < half else cb
        with col:
            val = st.checkbox(topic, value=completed.get(topic, False), key=f"chk_{i}")
            st.session_state["completed"][topic] = val

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Generate plan
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("topics"):
    topics    = st.session_state["topics"]
    completed = st.session_state["completed"]
    remaining = [t for t, done in completed.items() if not done]
    n_done    = len(topics) - len(remaining)

    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="badge badge-4">🚀 Step 4 · Generate Study Plan</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-purple">{len(topics)}</span><span class="stat-lbl">Total Topics</span></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-green">{n_done}</span><span class="stat-lbl">Completed</span></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-red">{len(remaining)}</span><span class="stat-lbl">Remaining</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    exam_date = st.date_input("📅 Exam date", value=date.today() + timedelta(days=7),
                               min_value=date.today(), key="exam_date")
    days_left = (exam_date - date.today()).days
    st.caption(f"Planning from **{date.today()}** · **{days_left}** day(s) until exam")

    if days_left == 0:
        st.warning("⚠️ Exam is today — all topics will be scheduled for today.")

    if len(remaining) == 0:
        st.success("🎉 All topics completed! Good luck in your exam!")
    else:
        if st.button(f"🌈 Generate plan for {len(remaining)} topic(s)", use_container_width=True, type="primary"):
            with st.spinner("Building your personalized rainbow study plan…"):
                try:
                    from planner import generate_plan
                    plan = generate_plan(
                        remaining_topics=remaining,
                        exam_date=exam_date,
                        hours_per_day=st.session_state.get("hours", 3),
                        subject=st.session_state.get("subject", "University Exam"),
                        api_key=st.session_state.get("gemini_key", ""),
                        model=st.session_state.get("model", "gemini-1.5-flash"),
                    )
                    st.session_state["plan"] = plan
                except Exception as e:
                    st.error(f"❌ {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Show plan
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get("plan"):
    plan = st.session_state["plan"]

    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="badge badge-5">🌈 Your Study Plan</div>', unsafe_allow_html=True)

    total_topics_in_plan = sum(len(d.get("topics", [])) for d in plan)
    total_hours = sum(d.get("hours", 0) for d in plan)

    ps1, ps2, ps3 = st.columns(3)
    with ps1:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-purple">{len(plan)}</span><span class="stat-lbl">Study Days</span></div>', unsafe_allow_html=True)
    with ps2:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-green">{total_topics_in_plan}</span><span class="stat-lbl">Topics Scheduled</span></div>', unsafe_allow_html=True)
    with ps3:
        st.markdown(f'<div class="stat-box"><span class="stat-num num-red">{round(total_hours,1)}h</span><span class="stat-lbl">Total Study Time</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    RAINBOW = ["#FF0080","#FF4500","#FF8C00","#FFD700","#00C851","#00BFFF","#7B2FFF"]

    for idx, day in enumerate(plan):
        dtype  = day.get("type", "study")
        color  = RAINBOW[idx % len(RAINBOW)] if dtype == "study" else ("#FF8C00" if dtype == "revision" else "#00C851")
        label  = {"study": "📘 Study", "revision": "🔄 Revision", "buffer": "🎯 Exam Day"}.get(dtype, "📘 Study")
        topics_html = "".join(f'<div class="day-topic">• {t}</div>' for t in day.get("topics", []))

        st.markdown(f"""
        <div class="day-card day-card-{dtype}" style="border-left-color:{color};">
            <div class="day-type day-type-{dtype}">{label} · {day.get('hours',0)}h</div>
            <div class="day-heading">{day.get('day','')}, {day.get('date','')}</div>
            {topics_html}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📄 Download your plan")
    try:
        from pdf_export import generate_pdf
        pdf_bytes = generate_pdf(
            plan=plan,
            subject=st.session_state.get("subject", "University Exam"),
            exam_date=st.session_state.get("exam_date", date.today()),
        )
        st.download_button(
            "⬇️ Download as PDF", data=pdf_bytes,
            file_name=f"study_plan_{st.session_state.get('subject','exam').replace(' ','_')}.pdf",
            mime="application/pdf", use_container_width=True, type="primary",
        )
    except Exception as e:
        st.error(f"PDF export failed: {e}")

    st.markdown('</div>', unsafe_allow_html=True)
