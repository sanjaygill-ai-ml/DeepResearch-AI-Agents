import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ─── CSS Variables ─── */
:root {
    --gold:          #c9a96e;
    --gold-light:    #e8d5a3;
    --gold-dim:      #8a6f42;
    --ivory:         #f2ece0;
    --ivory-dim:     #b8b0a0;
    --ivory-muted:   #706860;
    --bg-deep:       #080810;
    --bg-mid:        #0e0e1a;
    --bg-card:       rgba(255,255,255,0.028);
    --bg-card-hover: rgba(255,255,255,0.045);
    --border:        rgba(201,169,110,0.12);
    --border-bright: rgba(201,169,110,0.35);
    --green:         #6ec99a;
    --green-dim:     rgba(110,201,154,0.15);
    --radius-lg:     20px;
    --radius-md:     14px;
    --radius-sm:     8px;
    --transition:    0.25s cubic-bezier(0.4,0,0.2,1);
}

/* ─── Base Reset ─── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    color: var(--ivory);
}

.stApp {
    background-color: var(--bg-deep);
    background-image:
        radial-gradient(ellipse 90% 55% at 15% -5%,  rgba(201,169,110,0.09) 0%, transparent 65%),
        radial-gradient(ellipse 70% 45% at 85% 105%, rgba(110,120,201,0.06) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 50%  50%, rgba(14,14,26,0.95)    0%, transparent 100%);
    min-height: 100vh;
}

/* ─── Grain overlay ─── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 3.5rem 5rem;
    max-width: 1280px;
    position: relative;
    z-index: 1;
}

/* ─── HERO ─── */
.hero {
    text-align: center;
    padding: 4.5rem 0 3rem;
    position: relative;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(201,169,110,0.08);
    border: 1px solid rgba(201,169,110,0.2);
    border-radius: 100px;
    padding: 0.35rem 1rem;
    margin-bottom: 1.8rem;
}
.hero-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--gold);
    box-shadow: 0 0 8px var(--gold);
    animation: pulse-dot 2.5s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity: 1; transform: scale(1); }
    50%      { opacity: 0.5; transform: scale(0.7); }
}
.hero-badge-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 400;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
}

.hero h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(3.5rem, 7vw, 6.5rem);
    font-weight: 300;
    line-height: 0.95;
    letter-spacing: -0.01em;
    color: var(--ivory);
    margin: 0 0 0.2rem;
}
.hero h1 em {
    font-style: italic;
    color: var(--gold-light);
    font-weight: 300;
}
.hero-wordmark {
    display: block;
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(3.5rem, 7vw, 6.5rem);
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 40%, var(--gold-dim) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.05;
}

.hero-rule {
    width: 40px;
    height: 1px;
    background: var(--gold);
    margin: 1.6rem auto;
    opacity: 0.5;
}

.hero-sub {
    font-size: 1rem;
    font-weight: 300;
    color: var(--ivory-dim);
    max-width: 460px;
    margin: 0 auto;
    line-height: 1.75;
    letter-spacing: 0.01em;
}

/* ─── Full-bleed divider ─── */
.divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(201,169,110,0.08) 15%,
        rgba(201,169,110,0.3) 50%,
        rgba(201,169,110,0.08) 85%,
        transparent 100%);
    margin: 2.5rem 0;
    position: relative;
}
.divider::after {
    content: '◈';
    position: absolute;
    left: 50%; top: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.6rem;
    color: var(--gold);
    background: var(--bg-deep);
    padding: 0 0.6rem;
    letter-spacing: 0;
}

/* ─── INPUT CARD ─── */
.input-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 2.2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 10%; right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,169,110,0.4), transparent);
}

/* ─── Streamlit widget overrides ─── */
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    color: var(--gold) !important;
    font-weight: 400 !important;
    margin-bottom: 0.5rem !important;
}
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(201,169,110,0.2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--ivory) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.98rem !important;
    font-weight: 300 !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color var(--transition), box-shadow var(--transition) !important;
    letter-spacing: 0.01em !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--ivory-muted) !important;
    font-style: italic !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(201,169,110,0.5) !important;
    box-shadow: 0 0 0 3px rgba(201,169,110,0.08), 0 0 20px rgba(201,169,110,0.06) !important;
    outline: none !important;
}

/* ─── Run Button ─── */
.stButton > button {
    background: linear-gradient(135deg, rgba(201,169,110,0.15) 0%, rgba(201,169,110,0.08) 100%) !important;
    color: var(--gold-light) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border: 1px solid rgba(201,169,110,0.35) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.8rem 2rem !important;
    cursor: pointer !important;
    transition: all var(--transition) !important;
    position: relative !important;
    overflow: hidden !important;
    width: 100% !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(201,169,110,0.2), transparent);
    opacity: 0;
    transition: opacity var(--transition);
}
.stButton > button:hover {
    border-color: rgba(201,169,110,0.65) !important;
    box-shadow: 0 0 28px rgba(201,169,110,0.18), inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transform: translateY(-1px) !important;
    color: #fff !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: none !important;
}

/* ─── PIPELINE CARDS ─── */
.pipeline-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.pipeline-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

.step-card {
    background: var(--bg-card);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: var(--radius-md);
    padding: 1.3rem 1.6rem;
    margin-bottom: 0.9rem;
    position: relative;
    overflow: hidden;
    transition: all var(--transition);
}
.step-card::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 2px;
    border-radius: var(--radius-md) 0 0 var(--radius-md);
    background: rgba(255,255,255,0.04);
    transition: background var(--transition), box-shadow var(--transition);
}
.step-card.active {
    border-color: rgba(201,169,110,0.22);
    background: rgba(201,169,110,0.04);
}
.step-card.active::after {
    background: var(--gold);
    box-shadow: 0 0 12px rgba(201,169,110,0.6);
}
.step-card.done {
    border-color: rgba(110,201,154,0.18);
    background: rgba(110,201,154,0.025);
}
.step-card.done::after {
    background: var(--green);
    box-shadow: 0 0 10px rgba(110,201,154,0.4);
}

.step-inner {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.step-index {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    color: var(--ivory-muted);
    flex-shrink: 0;
    transition: all var(--transition);
}
.step-card.active .step-index {
    border-color: rgba(201,169,110,0.4);
    color: var(--gold);
    background: rgba(201,169,110,0.08);
}
.step-card.done .step-index {
    border-color: rgba(110,201,154,0.4);
    color: var(--green);
    background: rgba(110,201,154,0.08);
}
.step-info { flex: 1; min-width: 0; }
.step-name {
    font-family: 'Outfit', sans-serif;
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--ivory-dim);
    margin-bottom: 0.15rem;
    transition: color var(--transition);
}
.step-card.active .step-name,
.step-card.done .step-name { color: var(--ivory); }
.step-desc {
    font-size: 0.72rem;
    color: var(--ivory-muted);
    font-weight: 300;
}
.step-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.12em;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    flex-shrink: 0;
}
.badge-waiting { color: #3a3a4a; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); }
.badge-running {
    color: var(--gold);
    background: rgba(201,169,110,0.08);
    border: 1px solid rgba(201,169,110,0.25);
    animation: badge-pulse 1.8s ease-in-out infinite;
}
@keyframes badge-pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.5; }
}
.badge-done { color: var(--green); background: rgba(110,201,154,0.08); border: 1px solid rgba(110,201,154,0.25); }

/* ─── Example pills ─── */
.pill-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.2rem;
}
.pill-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: var(--ivory-muted);
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.pill {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 100px;
    padding: 0.25rem 0.8rem;
    font-size: 0.73rem;
    font-weight: 300;
    color: var(--ivory-dim);
    letter-spacing: 0.01em;
    cursor: default;
    transition: all var(--transition);
}
.pill:hover {
    border-color: rgba(201,169,110,0.25);
    color: var(--gold-light);
    background: rgba(201,169,110,0.05);
}

/* ─── RESULT PANELS ─── */
.result-wrap { margin-top: 0.8rem; }

.result-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem 1.8rem;
    margin-bottom: 1rem;
    transition: border-color var(--transition);
}
.result-card:hover { border-color: rgba(201,169,110,0.22); }
.result-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin-bottom: 0.9rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--border);
}
.result-body {
    font-size: 0.87rem;
    line-height: 1.85;
    color: #9a9288;
    white-space: pre-wrap;
    font-family: 'Outfit', sans-serif;
    font-weight: 300;
}

/* ─── REPORT PANEL ─── */
.report-wrap {
    position: relative;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
}
.report-panel {
    background: rgba(255,255,255,0.022);
    border: 1px solid rgba(201,169,110,0.18);
    border-radius: var(--radius-lg);
    padding: 2.5rem 3rem;
    position: relative;
    overflow: hidden;
}
.report-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 8%; right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,169,110,0.5), transparent);
}
.report-panel::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(201,169,110,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.report-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.8rem;
    padding-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
}
.report-icon {
    font-size: 1rem;
    color: var(--gold);
}
.report-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--gold);
}
.report-content {
    font-family: 'Outfit', sans-serif;
    font-weight: 300;
    color: var(--ivory-dim);
    line-height: 1.9;
    font-size: 0.95rem;
}
/* ─── Markdown inside report ─── */
.report-panel h1,
.report-panel h2,
.report-panel h3 {
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 400 !important;
    color: var(--ivory) !important;
    letter-spacing: 0 !important;
}
.report-panel h2 { font-size: 1.55rem !important; margin-top: 1.8rem !important; }
.report-panel h3 { font-size: 1.2rem !important; }
.report-panel p  { font-size: 0.95rem !important; font-weight: 300 !important; }
.report-panel a  { color: var(--gold) !important; text-decoration: none !important; }
.report-panel a:hover { text-decoration: underline !important; }

/* ─── FEEDBACK PANEL ─── */
.feedback-panel {
    background: rgba(255,255,255,0.022);
    border: 1px solid rgba(110,201,154,0.15);
    border-radius: var(--radius-lg);
    padding: 2rem 2.5rem;
    position: relative;
    overflow: hidden;
    margin-top: 1.2rem;
}
.feedback-panel::before {
    content: '';
    position: absolute;
    top: 0; left: 8%; right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(110,201,154,0.4), transparent);
}
.feedback-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 1.4rem;
    padding-bottom: 0.9rem;
    border-bottom: 1px solid rgba(110,201,154,0.12);
}
.feedback-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--green);
}

/* ─── Section label ─── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: var(--gold-dim);
    margin: 2.5rem 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.7rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--border), transparent);
}

/* ─── Expander ─── */
details {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    margin-bottom: 0.8rem !important;
    overflow: hidden !important;
    transition: border-color var(--transition) !important;
}
details:hover { border-color: rgba(201,169,110,0.22) !important; }
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    color: var(--ivory-muted) !important;
    letter-spacing: 0.12em !important;
    padding: 0.85rem 1.2rem !important;
    cursor: pointer !important;
    list-style: none !important;
    transition: color var(--transition) !important;
}
details summary:hover { color: var(--gold-light) !important; }

/* ─── Download button ─── */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--ivory-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.14em !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.6rem 1.4rem !important;
    transition: all var(--transition) !important;
    margin-top: 1rem !important;
    width: auto !important;
}
.stDownloadButton > button:hover {
    border-color: rgba(201,169,110,0.35) !important;
    color: var(--gold-light) !important;
    transform: none !important;
}

/* ─── Spinner ─── */
.stSpinner > div { color: var(--gold) !important; }

/* ─── Warning ─── */
.stAlert {
    background: rgba(201,169,110,0.06) !important;
    border: 1px solid rgba(201,169,110,0.2) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--gold-light) !important;
}

/* ─── Footer ─── */
.footer {
    text-align: center;
    margin-top: 5rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.footer-inner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
}
.footer-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #2e2e3e;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.footer-dot {
    width: 3px; height: 3px;
    border-radius: 50%;
    background: #2e2e3e;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render pipeline step card ────────────────────────────────────────
def step_card(num: str, title: str, desc: str, state: str):
    badge_map = {
        "waiting": ("—", "badge-waiting"),
        "running": ("● Live",  "badge-running"),
        "done":    ("✓ Done",  "badge-done"),
    }
    label, badge_cls = badge_map.get(state, ("—", "badge-waiting"))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    icon_text = "✓" if state == "done" else num
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-inner">
            <div class="step-index">{icon_text}</div>
            <div class="step-info">
                <div class="step-name">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>
            <span class="step-badge {badge_cls}">{label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">
        <span class="hero-badge-dot"></span>
        <span class="hero-badge-text">Multi-Agent AI System</span>
    </div>
    <h1>
        <em>Intelligent</em>
        <span class="hero-wordmark">ResearchMind</span>
    </h1>
    <div class="hero-rule"></div>
    <p class="hero-sub">
        Four specialized agents — searching, scraping, writing, and critiquing —
        collaborating in sequence to deliver a polished research brief.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────
col_input, col_gap, col_pipe = st.columns([5, 0.6, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("Run Research Pipeline  ›", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress", "Neuromorphic chips"]
    pills_html = '<div class="pill-row"><span class="pill-label">Try</span>'
    for ex in examples:
        pills_html += f'<span class="pill">{ex}</span>'
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)

with col_pipe:
    st.markdown('<div class="pipeline-label">Pipeline Stages</div>', unsafe_allow_html=True)

    r = st.session_state.results

    def s(step):
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  "Gathers recent web intelligence",     s("search"))
    step_card("02", "Reader Agent",  "Deep-scrapes top source content",      s("reader"))
    step_card("03", "Writer Chain",  "Drafts structured research report",    s("writer"))
    step_card("04", "Critic Chain",  "Scores, annotates & refines output",   s("critic"))


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic to proceed.")
    else:
        st.session_state.results  = {}
        st.session_state.running  = True
        st.session_state.done     = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results   = {}
    topic_val = st.session_state.topic_input

    with st.spinner("Search Agent · gathering intelligence…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("Reader Agent · extracting deep content…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    with st.spinner("Writer Chain · composing the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    with st.spinner("Critic Chain · reviewing & scoring…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done    = True
    st.rerun()


# ── Results ───────────────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("◎  Search Agent — raw output", expanded=False):
            st.markdown(
                f'<div class="result-card">'
                f'<div class="result-label">Search Agent Output</div>'
                f'<div class="result-body">{r["search"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if "reader" in r:
        with st.expander("◎  Reader Agent — scraped content", expanded=False):
            st.markdown(
                f'<div class="result-card">'
                f'<div class="result-label">Reader Agent Output</div>'
                f'<div class="result-body">{r["reader"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="report-header">
                <span class="report-icon">◈</span>
                <span class="report-title">Final Research Report</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="↓  Download report  (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="feedback-header">
                <span style="color:var(--green);font-size:0.9rem;">◉</span>
                <span class="feedback-title">Critic Feedback &amp; Score</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-inner">
        <span class="footer-text">ResearchMind</span>
        <span class="footer-dot"></span>
        <span class="footer-text">LangChain Multi-Agent</span>
        <span class="footer-dot"></span>
        <span class="footer-text">Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)