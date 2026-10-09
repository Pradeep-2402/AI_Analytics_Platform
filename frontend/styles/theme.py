def load_css():
    return """
@import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
 
/* ─── ROOT TOKENS ──────────────────────────────── */
:root {
    --bg-base:       #0a0e1a;
    --bg-card:       #0f1629;
    --bg-card2:      #131c35;
    --bg-hover:      #1a2444;
    --cyan:          #00d4ff;
    --cyan-dim:      #00a8cc;
    --cyan-glow:     rgba(0,212,255,0.18);
    --purple:        #7c3aed;
    --purple-dim:    #5b21b6;
    --green:         #10b981;
    --amber:         #f59e0b;
    --red:           #ef4444;
    --text-primary:  #e2e8f0;
    --text-muted:    #64748b;
    --text-dim:      #94a3b8;
    --border:        rgba(0,212,255,0.12);
    --border-bright: rgba(0,212,255,0.35);
    --radius:        12px;
    --radius-lg:     18px;
}
 
/* ─── GLOBAL RESET ──────────────────────────────── */
html, body, .stApp {
    background: var(--bg-base) !important;
    font-family: 'Exo 2', sans-serif !important;
    color: var(--text-primary) !important;
}
 
/* ─── ANIMATED TITLE ───────────────────────────── */
@keyframes titleGlow {
    0%   { text-shadow: 0 0 10px var(--cyan), 0 0 30px var(--cyan); }
    50%  { text-shadow: 0 0 25px var(--cyan), 0 0 60px var(--cyan-dim), 0 0 100px rgba(0,212,255,0.3); }
    100% { text-shadow: 0 0 10px var(--cyan), 0 0 30px var(--cyan); }
}
@keyframes titleSlide {
    from { opacity: 0; transform: translateY(-28px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes subtitleFade {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 0.7; transform: translateY(0); }
}
@keyframes borderPulse {
    0%, 100% { opacity: 0.4; }
    50%       { opacity: 1; }
}
 
/* ─── MAIN HEADER BLOCK ────────────────────────── */
.main-header {
    text-align: center;
    padding: 48px 24px 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}
.main-title {
    font-family: 'Exo 2', sans-serif;
    font-size: clamp(2rem, 5vw, 3.4rem);
    font-weight: 900;
    letter-spacing: -0.5px;
    color: var(--cyan);
    animation: titleSlide 0.7s cubic-bezier(.16,1,.3,1) both,
               titleGlow  3s ease-in-out 0.7s infinite;
    margin: 0 0 10px;
}
.main-subtitle {
    font-family: 'Exo 2', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-dim);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    animation: subtitleFade 0.8s ease 0.4s both;
}
.header-line {
    display: block;
    width: 80px;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    margin: 18px auto 0;
    animation: borderPulse 2.5s ease-in-out infinite;
}
 
/* ─── NAV PILLS ────────────────────────────────── */
.nav-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    padding: 0 0 28px;
    justify-content: center;
}
.nav-pill {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 50px;
    padding: 8px 22px;
    font-family: 'Exo 2', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--text-dim);
    cursor: pointer;
    transition: all 0.22s ease;
}
.nav-pill:hover, .nav-pill.active {
    background: var(--cyan-glow);
    border-color: var(--cyan);
    color: var(--cyan);
    box-shadow: 0 0 18px var(--cyan-glow);
}
 
/* ─── PAGE SECTION HEADING ─────────────────────── */
.section-title {
    font-family: 'Exo 2', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--cyan);
    border-left: 4px solid var(--cyan);
    padding-left: 14px;
    margin: 32px 0 18px;
    letter-spacing: -0.3px;
}
.section-desc {
    font-size: 0.88rem;
    color: var(--text-dim);
    margin: -10px 0 20px 18px;
    font-weight: 400;
}
 
/* ─── KPI CARDS ────────────────────────────────── */
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
}
.kpi-card:hover { border-color: var(--border-bright); }
.kpi-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--cyan);
}
.kpi-value.green  { color: var(--green); }
.kpi-value.amber  { color: var(--amber); }
.kpi-value.red    { color: var(--red); }
.kpi-value.purple { color: #a78bfa; }
 
/* ─── UPLOAD ZONE ──────────────────────────────── */
.upload-zone {
    border: 2px dashed var(--border-bright);
    border-radius: var(--radius-lg);
    padding: 48px 24px;
    text-align: center;
    background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-card2) 100%);
    margin: 24px 0;
    transition: border-color 0.2s, background 0.2s;
}
.upload-zone:hover {
    border-color: var(--cyan);
    background: var(--cyan-glow);
}
.upload-icon { font-size: 2.8rem; margin-bottom: 12px; }
.upload-title {
    font-size: 1.1rem; font-weight: 700;
    color: var(--text-primary);
}
.upload-hint {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 6px;
}
 
/* ─── DATA TABLE — BLACK BG / WHITE TEXT ─────────── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}

/* Header row */
.stDataFrame thead th,
[data-testid="stDataFrame"] thead th,
[data-testid="stDataFrame"] th {
    background: #000000 !important;
    color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-bright) !important;
}

/* Body cells */
.stDataFrame tbody td,
[data-testid="stDataFrame"] tbody td,
[data-testid="stDataFrame"] td {
    background: #000000 !important;
    color: #ffffff !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.82rem !important;
}

/* Alternating rows */
.stDataFrame tbody tr:nth-child(even) td,
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
    background: #0d0d0d !important;
    color: #ffffff !important;
}

/* Hover row */
.stDataFrame tbody tr:hover td,
[data-testid="stDataFrame"] tbody tr:hover td {
    background: #1a1a1a !important;
    color: #ffffff !important;
}

/* Streamlit internal dataframe wrapper */
[data-testid="stDataFrame"] > div,
[data-testid="stDataFrame"] iframe {
    background: #000000 !important;
}

/* Sticky index / row numbers */
[data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
    background: #000000 !important;
    color: #ffffff !important;
}
 
/* ─── BUTTONS ──────────────────────────────────── */
.stButton > button {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    border: 1.5px solid var(--cyan) !important;
    color: var(--cyan) !important;
    border-radius: 8px !important;
    padding: 10px 24px !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: var(--cyan-glow) !important;
    box-shadow: 0 0 22px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
 
/* ─── SELECTBOX / INPUT ────────────────────────── */
.stSelectbox > div > div,
.stTextInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-family: 'Exo 2', sans-serif !important;
}
.stSelectbox > div > div:focus-within,
.stTextInput > div > div > input:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 2px var(--cyan-glow) !important;
}
.stSelectbox label, .stTextInput label {
    color: var(--text-dim) !important;
    font-size: 0.8rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
}
 
/* ─── FILE UPLOADER ────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-bright) !important;
    border-radius: var(--radius-lg) !important;
    padding: 32px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--cyan) !important;
    background: var(--cyan-glow) !important;
}
[data-testid="stFileUploader"] label {
    color: var(--cyan) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text-dim) !important;
}
 
/* ─── METRICS — YELLOW LABEL TEXT ──────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 18px 20px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 2px;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
}

/* ── YELLOW metric label (was --text-muted, invisible) ── */
[data-testid="metric-container"] [data-testid="stMetricLabel"],
[data-testid="metric-container"] [data-testid="stMetricLabel"] p,
[data-testid="metric-container"] label {
    font-family: 'Exo 2', sans-serif !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #fde047 !important;   /* ← bright yellow */
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--cyan) !important;
}
 
/* ─── SUCCESS / ERROR / WARNING ────────────────── */
.stSuccess {
    background: rgba(16,185,129,0.1) !important;
    border: 1px solid rgba(16,185,129,0.35) !important;
    border-radius: 8px !important;
    color: var(--green) !important;
}
.stError {
    background: rgba(239,68,68,0.1) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    border-radius: 8px !important;
}
.stWarning {
    background: rgba(245,158,11,0.1) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 8px !important;
}
 
/* ─── HIDE SIDEBAR COMPLETELY ───────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
}
 
/* ─── TOP NAV BUTTONS ───────────────────────────── */
.stButton > button[kind="secondary"] {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-dim) !important;
    border-radius: 8px !important;
    padding: 10px 6px !important;
    transition: all 0.2s ease !important;
    white-space: nowrap !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--cyan-glow) !important;
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    box-shadow: 0 0 14px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    background: var(--cyan-glow) !important;
    border: 1.5px solid var(--cyan) !important;
    color: var(--cyan) !important;
    border-radius: 8px !important;
    padding: 10px 6px !important;
    box-shadow: 0 0 16px var(--cyan-glow) !important;
    white-space: nowrap !important;
}
 
/* ─── JSON VIEWER ──────────────────────────────── */
.stJson {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
 
/* ─── CODE BLOCK ───────────────────────────────── */
.stCode {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
 
/* ─── DOWNLOAD BUTTON ──────────────────────────── */
.stDownloadButton > button {
    font-family: 'Exo 2', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(124,58,237,0.12)) !important;
    border: 1px solid var(--border-bright) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    border-color: var(--cyan) !important;
    color: var(--cyan) !important;
    box-shadow: 0 0 18px var(--cyan-glow) !important;
    transform: translateY(-1px) !important;
}
 
/* ─── PLOTLY CHARTS ────────────────────────────── */
.js-plotly-plot {
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
 
/* ─── SCROLLBAR ────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb {
    background: var(--border-bright);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--cyan-dim); }
 
/* ─── PAGE BADGE ───────────────────────────────── */
.page-badge {
    display: inline-block;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 12px;
    border-radius: 50px;
    background: var(--cyan-glow);
    color: var(--cyan);
    border: 1px solid var(--border-bright);
    margin-bottom: 10px;
}
 
/* ─── DIVIDER ──────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 28px 0 !important;
}
 
/* ─── HIDE STREAMLIT DEFAULT UI ────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 24px !important;
    max-width: 1280px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin-left: 0 !important;
}
"""