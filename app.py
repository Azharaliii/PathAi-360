import streamlit as st
import time
import datetime

# ════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PathAi 360",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════
#  MONGODB — multi-collection, env-var URI, proper indexes
#  Set MONGO_URI env var for Atlas/remote. Defaults to localhost.
# ════════════════════════════════════════════════════════════
import os

@st.cache_resource(show_spinner=False)
def init_db():
    """Returns dict of collections {users, answers, results} or {_error: msg}."""
    try:
        from pymongo import MongoClient
        uri    = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
        client = MongoClient(uri, serverSelectionTimeoutMS=2500)
        client.admin.command("ping")               # raises if unreachable
        db = client[os.environ.get("DB_NAME", "pathai360")]
        # Create indexes once (idempotent)
        db["users"].create_index("email",             unique=True, background=True)
        db["answers"].create_index("user_id",                      background=True)
        db["results"].create_index("user_id",                      background=True)
        db["results"].create_index("personality_type",             background=True)
        return {"users": db["users"], "answers": db["answers"], "results": db["results"]}
    except Exception as e:
        return {"_error": str(e)}

_db = init_db()

def db_available():
    return _db is not None and "_error" not in _db

def db_error():
    return _db.get("_error", "MongoDB unreachable") if _db else "MongoDB unreachable"


# ════════════════════════════════════════════════════════════
#  FULL REDESIGNED THEME
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background: #060d0a !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #d8f0e8 !important;
}

.block-container {
    max-width: 1200px !important;
    padding: 0 2rem 6rem !important;
    margin: 0 auto !important;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="stToolbar"] { display: none; }

/* ── GLOBAL BACKGROUND ── */
.stApp::before {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background:
        radial-gradient(ellipse 80% 55% at 10% 5%, rgba(0,212,122,0.10) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 90%, rgba(0,200,232,0.08) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 50% 50%, rgba(157,111,255,0.05) 0%, transparent 65%);
}
.stApp::after {
    content: '';
    position: fixed; inset: 0; z-index: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(0,212,122,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,122,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: radial-gradient(ellipse 80% 70% at 50% 50%, black 20%, transparent 100%);
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #060d0a; }
::-webkit-scrollbar-thumb { background: #00d47a; border-radius: 10px; }

/* ── GLOBAL: prevent all buttons from wrapping text ── */
.stButton > button {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
}

/* ════════════════════════════════════════════════
   TOP NAVBAR
════════════════════════════════════════════════ */
.topnav {
    position: sticky; top: 0; z-index: 999;
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 0 0 0;
    height: 68px;
    background: rgba(6,13,10,0.85);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid rgba(0,212,122,0.10);
    margin-bottom: 0;
    border-radius: 0 0 20px 20px;
}
.topnav-brand {
    display: flex; align-items: center; gap: 14px;
}
.topnav-title {
    font-family: 'Syne', sans-serif;
    font-size: 22px; font-weight: 800; letter-spacing: -0.5px;
    background: linear-gradient(120deg, #00d47a, #00c8e8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.topnav-sub {
    font-size: 11px; color: rgba(180,230,205,0.4);
    letter-spacing: 0.3px; margin-top: 1px;
}
.topnav-chips {
    display: flex; gap: 8px; align-items: center;
}

/* ════════════════════════════════════════════════
   CHIPS
════════════════════════════════════════════════ */
.chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 0.5px;
    padding: 5px 13px; border-radius: 100px;
    display: inline-flex; align-items: center; gap: 7px;
    font-weight: 500;
}
.chip-green {
    background: rgba(0,212,122,0.10);
    border: 1px solid rgba(0,212,122,0.30);
    color: #00d47a;
}
.chip-blue {
    background: rgba(0,200,232,0.09);
    border: 1px solid rgba(0,200,232,0.25);
    color: #00c8e8;
}
.chip-purple {
    background: rgba(157,111,255,0.09);
    border: 1px solid rgba(157,111,255,0.22);
    color: #9d6fff;
}
.blink { animation: blink 2s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.2} }
.dot { display:inline-block; width:6px; height:6px; border-radius:50%; }
.dot-green { background:#00d47a; box-shadow:0 0 7px #00d47a; }

/* ════════════════════════════════════════════════
   HOME HERO SECTION
════════════════════════════════════════════════ */
.home-hero {
    min-height: 88vh;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center;
    padding: 60px 20px 40px;
    position: relative; overflow: hidden;
}
.home-hero::before {
    content: '';
    position: absolute; top: -100px; left: 50%; transform: translateX(-50%);
    width: 700px; height: 700px; border-radius: 50%;
    background: radial-gradient(circle, rgba(0,212,122,0.07) 0%, transparent 65%);
    pointer-events: none;
}
.home-badge {
    display: inline-flex; align-items: center; gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
    color: #00d47a; font-weight: 600;
    background: rgba(0,212,122,0.08);
    border: 1px solid rgba(0,212,122,0.25);
    padding: 7px 18px; border-radius: 100px;
    margin-bottom: 30px;
    animation: fadeUp .6s ease both;
}
.home-h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(42px, 6vw, 82px);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -2.5px;
    color: #ecfaf3;
    margin-bottom: 8px;
    animation: fadeUp .7s .08s ease both;
}
.home-h1 .grad {
    background: linear-gradient(110deg, #00d47a 0%, #00c8e8 45%, #9d6fff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.home-sub {
    font-size: 17px; font-weight: 400; line-height: 1.75;
    color: rgba(180,230,205,0.6);
    max-width: 580px; margin: 16px auto 44px;
    animation: fadeUp .7s .16s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(22px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* home action buttons */
.home-actions {
    display: flex; gap: 14px; justify-content: center; flex-wrap: wrap;
    margin-bottom: 56px;
    animation: fadeUp .7s .24s ease both;
}
.btn-hero-primary {
    font-family: 'DM Sans', sans-serif;
    font-size: 16px; font-weight: 700;
    background: linear-gradient(90deg, #00d47a, #00c8e8);
    color: #041a0d;
    border: none; border-radius: 14px;
    padding: 16px 40px; cursor: pointer;
    transition: all .2s; letter-spacing: 0.2px;
    box-shadow: 0 4px 20px rgba(0,212,122,0.25);
}
.btn-hero-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 16px 44px rgba(0,212,122,0.45);
}
.btn-hero-outline {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px; font-weight: 600;
    background: transparent;
    color: rgba(216,240,232,0.85);
    border: 1.5px solid rgba(0,212,122,0.25);
    border-radius: 14px;
    padding: 14px 34px; cursor: pointer;
    transition: all .2s;
}
.btn-hero-outline:hover {
    border-color: #00d47a;
    color: #00d47a;
    background: rgba(0,212,122,0.06);
}

/* home stats row */
.home-stats-row {
    display: flex; gap: 0;
    border: 1px solid rgba(0,212,122,0.15);
    border-radius: 20px; overflow: hidden;
    background: rgba(12,28,20,0.92);
    backdrop-filter: blur(20px);
    max-width: 680px; width: 100%; margin: 0 auto 56px;
    animation: fadeUp .7s .32s ease both;
}
.hstat {
    flex: 1; padding: 22px 18px; text-align: center;
    border-right: 1px solid rgba(0,212,122,0.08);
    transition: .2s;
}
.hstat:last-child { border-right: none; }
.hstat:hover { background: rgba(0,212,122,0.04); }
.hstat-num {
    font-family: 'Syne', sans-serif;
    font-size: 30px; font-weight: 800;
    background: linear-gradient(120deg, #00d47a, #00c8e8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1;
}
.hstat-lbl {
    font-size: 11px; color: rgba(140,200,170,0.4);
    margin-top: 5px; letter-spacing: .5px;
    text-transform: uppercase; font-weight: 600;
}

/* feature cards on home */
.home-feat-grid {
    display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;
    max-width: 980px; width: 100%;
    animation: fadeUp .7s .40s ease both;
}
.home-feat-card {
    background: rgba(12,28,20,0.92);
    border: 1px solid rgba(0,212,122,0.10);
    border-radius: 20px; padding: 26px 22px;
    text-align: left; transition: .25s; cursor: pointer;
}
.home-feat-card:hover {
    border-color: rgba(0,212,122,0.30);
    transform: translateY(-4px);
    background: rgba(14,32,22,0.98);
}
.hfc-icon { font-size: 26px; margin-bottom: 14px; }
.hfc-title {
    font-family: 'Syne', sans-serif;
    font-size: 14px; font-weight: 700; color: #d8f0e8; margin-bottom: 7px;
}
.hfc-desc { font-size: 12px; line-height: 1.65; color: rgba(180,230,205,0.5); }
.hfc-arrow { font-size: 12px; color: #00d47a; margin-top: 14px; font-weight: 600; }

/* ════════════════════════════════════════════════
   SECTION PAGE HEADER
════════════════════════════════════════════════ */
.page-header {
    margin-bottom: 28px;
    padding: 32px 0 24px;
    border-bottom: 1px solid rgba(0,212,122,0.08);
}
.page-header-h {
    font-family: 'Syne', sans-serif;
    font-size: 28px; font-weight: 800; letter-spacing: -1px;
    color: #ecfaf3; margin-bottom: 6px;
}
.page-header-sub {
    font-size: 13px; color: rgba(140,200,170,0.45); font-weight: 400;
}
.page-header-chips {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px;
}

/* ════════════════════════════════════════════════
   SECTION CARDS
════════════════════════════════════════════════ */
.card {
    background: rgba(12,28,20,0.94);
    border: 1px solid rgba(0,212,122,0.12);
    border-radius: 20px;
    padding: 24px 24px 22px;
    margin-bottom: 18px;
    position: relative; overflow: hidden;
    transition: border-color .2s;
}
.card:hover { border-color: rgba(0,212,122,0.22); }
.card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,122,0.3), transparent);
    opacity: 0;
    transition: opacity .2s;
}
.card:hover::before { opacity: 1; }
.card-header {
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 18px; padding-bottom: 14px;
    border-bottom: 1px solid rgba(0,212,122,0.08);
}
.card-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    background: rgba(0,212,122,0.09);
    border: 1px solid rgba(0,212,122,0.18);
    flex-shrink: 0;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 15px; font-weight: 700; color: #d8f0e8;
    line-height: 1.2;
}
.card-subtitle {
    font-size: 11px; color: rgba(140,200,170,0.4);
    margin-top: 2px; font-weight: 400;
}

/* ════════════════════════════════════════════════
   STAT CARDS
════════════════════════════════════════════════ */
.stat-box {
    background: rgba(12,28,20,0.92);
    border: 1px solid rgba(0,212,122,0.14);
    border-radius: 18px;
    padding: 20px 18px 18px;
    text-align: center;
    position: relative; overflow: hidden;
    transition: border-color .2s, transform .2s;
}
.stat-box:hover {
    border-color: rgba(0,212,122,0.38);
    transform: translateY(-3px);
}
.stat-box::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00d47a, transparent);
    opacity: .35;
}
.stat-icon { font-size: 24px; margin-bottom: 8px; display: block; }
.stat-number {
    font-family: 'Syne', sans-serif;
    font-size: 32px; font-weight: 800; line-height: 1;
    background: linear-gradient(120deg, #00d47a, #00c8e8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-number-p {
    font-family: 'Syne', sans-serif;
    font-size: 32px; font-weight: 800; line-height: 1;
    background: linear-gradient(120deg, #9d6fff, #00c8e8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-label {
    font-size: 11px; font-weight: 600; color: rgba(180,230,205,0.5);
    margin-top: 5px; text-transform: uppercase; letter-spacing: 1px;
}
.stat-detail {
    font-size: 10px; color: rgba(0,212,122,0.35); margin-top: 4px;
    font-family: 'JetBrains Mono', monospace;
}

/* ════════════════════════════════════════════════
   FORM INPUTS
════════════════════════════════════════════════ */
.stTextInput label,
.stSelectbox label,
.stRadio label,
.stNumberInput label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: rgba(160,210,185,0.7) !important;
    letter-spacing: 0.3px !important;
    margin-bottom: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
}

div[data-baseweb="input"] {
    background: rgba(0,212,122,0.05) !important;
    border: 1.5px solid rgba(0,212,122,0.18) !important;
    border-radius: 12px !important;
    transition: border-color .2s, box-shadow .2s !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #00d47a !important;
    box-shadow: 0 0 0 3px rgba(0,212,122,0.10) !important;
    background: rgba(0,212,122,0.08) !important;
}
div[data-baseweb="input"] input {
    color: #d8f0e8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
}

div[data-baseweb="select"] > div {
    background: rgba(0,212,122,0.05) !important;
    border: 1.5px solid rgba(0,212,122,0.18) !important;
    border-radius: 12px !important;
    color: #d8f0e8 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #00d47a !important;
    box-shadow: 0 0 0 3px rgba(0,212,122,0.10) !important;
}
[data-baseweb="popover"] { background: #0b1812 !important; }
[data-baseweb="menu"] {
    background: #0b1812 !important;
    border: 1px solid rgba(0,212,122,0.18) !important;
    border-radius: 12px !important;
}
[role="option"] { color: #c8e8d8 !important; font-family: 'DM Sans', sans-serif !important; }
[role="option"]:hover { background: rgba(0,212,122,0.10) !important; }

/* multiselect */
[data-baseweb="tag"] {
    background: rgba(0,212,122,0.15) !important;
    border: 1px solid rgba(0,212,122,0.35) !important;
    border-radius: 8px !important;
    color: #00d47a !important;
}

/* ════════════════════════════════════════════════
   BUTTONS  (non-nav — forms, CTA, submit)
════════════════════════════════════════════════ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(90deg, #00d47a 0%, #00c8e8 100%) !important;
    color: #041a0d !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 1.6rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    letter-spacing: 0.2px !important;
    white-space: nowrap !important;
    transition: transform .15s, box-shadow .15s !important;
    cursor: pointer !important;
    box-shadow: 0 4px 16px rgba(0,212,122,0.20) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 32px rgba(0,212,122,0.38) !important;
}
.stButton > button:active { transform: scale(0.99) !important; }

/* ── CUSTOM HTML NAV BAR ── */
.pathai-nav {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px;
    background: rgba(10,22,16,0.92);
    border: 1px solid rgba(0,212,122,0.10);
    border-radius: 16px;
    backdrop-filter: blur(16px);
    margin-bottom: 4px;
    flex-wrap: nowrap;
    overflow-x: auto;
}
.pathai-nav::-webkit-scrollbar { height: 0; }

.nav-btn {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 8px 16px;
    border-radius: 10px;
    border: 1px solid transparent;
    background: transparent;
    color: rgba(160,210,185,0.55);
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
    cursor: pointer;
    transition: all .18s ease;
    text-decoration: none;
    flex-shrink: 0;
    letter-spacing: 0.1px;
}
.nav-btn svg {
    width: 15px; height: 15px;
    flex-shrink: 0;
    opacity: 0.7;
    transition: opacity .18s;
}
.nav-btn:hover {
    background: rgba(0,212,122,0.07);
    border-color: rgba(0,212,122,0.22);
    color: #d8f0e8;
}
.nav-btn:hover svg { opacity: 1; }

.nav-btn.active {
    background: rgba(0,212,122,0.14);
    border-color: rgba(0,212,122,0.38);
    color: #00d47a;
    box-shadow: 0 0 16px rgba(0,212,122,0.12);
}
.nav-btn.active svg { opacity: 1; stroke: #00d47a; }

.nav-timer {
    margin-left: auto;
    flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: rgba(0,212,122,0.55);
    padding: 6px 12px;
    border-radius: 8px;
    border: 1px solid rgba(0,212,122,0.10);
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.nav-sep {
    width: 1px; height: 20px;
    background: rgba(0,212,122,0.10);
    flex-shrink: 0;
    margin: 0 2px;
}

/* ════════════════════════════════════════════════
   RADIO (LIKERT SCALE)
════════════════════════════════════════════════ */
.stRadio > div { gap: 8px !important; }
div[role="radiogroup"] {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
}
div[role="radiogroup"] > label {
    flex: 1 !important;
    min-width: 100px !important;
    background: rgba(0,212,122,0.03) !important;
    border: 1.5px solid rgba(0,212,122,0.13) !important;
    border-radius: 12px !important;
    padding: 10px 8px !important;
    cursor: pointer !important;
    transition: all .2s !important;
    text-align: center !important;
    color: rgba(180,230,205,0.65) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}
div[role="radiogroup"] > label:hover {
    border-color: rgba(0,212,122,0.45) !important;
    color: #00d47a !important;
    background: rgba(0,212,122,0.07) !important;
}
div[role="radiogroup"] > label:has(input:checked) {
    border-color: #00d47a !important;
    color: #00d47a !important;
    background: rgba(0,212,122,0.12) !important;
    box-shadow: 0 0 14px rgba(0,212,122,0.16) !important;
}
div[role="radiogroup"] input[type="radio"] { display: none !important; }

/* ════════════════════════════════════════════════
   PROGRESS BAR
════════════════════════════════════════════════ */
.stProgress { height: 7px !important; border-radius: 100px !important; overflow: hidden !important; }
.stProgress > div { background: rgba(0,212,122,0.08) !important; border-radius: 100px !important; }
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #00d47a, #00c8e8) !important;
    box-shadow: 0 0 10px rgba(0,212,122,0.45) !important;
    border-radius: 100px !important;
}

/* ════════════════════════════════════════════════
   STEP ITEMS (Roadmap)
════════════════════════════════════════════════ */
.step-item {
    display: flex; align-items: center; gap: 13px;
    background: rgba(0,212,122,0.02);
    border: 1px solid rgba(0,212,122,0.10);
    border-radius: 12px;
    padding: 11px 14px; margin-bottom: 7px;
    transition: all .2s; cursor: default;
}
.step-item:hover {
    border-color: rgba(0,212,122,0.32);
    background: rgba(0,212,122,0.06);
    transform: translateX(5px);
}
.step-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 600; color: #00d47a;
    background: rgba(0,212,122,0.10); border-radius: 7px;
    padding: 3px 8px; flex-shrink: 0; min-width: 32px; text-align: center;
}
.step-text { font-size: 13px; font-weight: 500; color: rgba(200,232,218,0.85); line-height: 1.4; }
.step-check {
    margin-left: auto; width: 16px; height: 16px; border-radius: 50%;
    border: 1.5px solid rgba(0,212,122,0.20); flex-shrink: 0;
}

/* ════════════════════════════════════════════════
   QUESTION CARD
════════════════════════════════════════════════ */
.question-text {
    font-family: 'DM Sans', sans-serif;
    font-size: 18px; font-weight: 600;
    color: #ecfaf3; line-height: 1.55;
    margin: 16px 0 20px;
    padding: 20px 22px;
    background: rgba(0,212,122,0.04);
    border-left: 3px solid #00d47a;
    border-radius: 0 14px 14px 0;
}
.q-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.q-counter { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600; color: #00d47a; }
.q-pct { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: rgba(0,212,122,0.4); }

/* ════════════════════════════════════════════════
   MBTI RESULT HEADER
════════════════════════════════════════════════ */
.mbti-hero {
    background: linear-gradient(135deg, rgba(0,212,122,0.08), rgba(0,200,232,0.05), rgba(157,111,255,0.05));
    border: 1px solid rgba(0,212,122,0.20);
    border-radius: 20px;
    padding: 28px 28px 24px;
    margin-bottom: 20px; position: relative; overflow: hidden;
}
.mbti-hero::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #00d47a 30%, #00c8e8 70%, transparent);
}
.mbti-badge {
    display: inline-flex; align-items: center; gap: 7px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; letter-spacing: 2px; color: #00d47a;
    background: rgba(0,212,122,0.10); border: 1px solid rgba(0,212,122,0.28);
    padding: 5px 14px; border-radius: 100px; margin-bottom: 12px; font-weight: 600;
}
.mbti-type-name {
    font-family: 'Syne', sans-serif;
    font-size: 26px; font-weight: 800; color: #ecfaf3;
    margin-bottom: 6px; letter-spacing: -0.5px;
}
.mbti-desc { font-size: 14px; color: rgba(180,230,205,0.65); line-height: 1.75; font-weight: 400; }

/* ════════════════════════════════════════════════
   MATCH CARDS
════════════════════════════════════════════════ */
.match-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 22px; }
.match-card { border-radius: 16px; padding: 18px 14px; text-align: center; transition: .2s; cursor: default; }
.match-card:hover { transform: translateY(-4px); }
.match-card-1 {
    background: linear-gradient(145deg, rgba(0,212,122,0.10), rgba(0,212,122,0.03));
    border: 1.5px solid rgba(0,212,122,0.38);
}
.match-card-2 {
    background: linear-gradient(145deg, rgba(0,200,232,0.08), rgba(0,200,232,0.02));
    border: 1px solid rgba(0,200,232,0.28);
}
.match-card-3 {
    background: linear-gradient(145deg, rgba(157,111,255,0.08), rgba(157,111,255,0.02));
    border: 1px solid rgba(157,111,255,0.22);
}
.match-rank { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 2px; margin-bottom: 8px; font-weight: 600; }
.rank-1 { color: #00d47a; } .rank-2 { color: #00c8e8; } .rank-3 { color: #9d6fff; }
.match-name { font-size: 13px; font-weight: 700; color: #d8f0e8; margin-bottom: 10px; line-height: 1.35; }
.match-pts { font-family: 'Syne', sans-serif; font-size: 28px; font-weight: 800; }
.pts-1 { color: #00d47a; } .pts-2 { color: #00c8e8; } .pts-3 { color: #9d6fff; }
.match-pts-label { font-size: 10px; opacity: .4; font-family: 'JetBrains Mono', monospace; }
.match-medal { font-size: 22px; margin-bottom: 6px; display: block; }

/* ════════════════════════════════════════════════
   TRAIT BARS
════════════════════════════════════════════════ */
.trait-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; }
.trait-label { font-size: 11px; font-weight: 600; color: rgba(140,200,170,0.55); width: 105px; flex-shrink: 0; text-transform: capitalize; }
.trait-bar-track { flex: 1; height: 5px; background: rgba(0,212,122,0.07); border-radius: 100px; overflow: hidden; }
.trait-bar-fill { height: 100%; border-radius: 100px; background: linear-gradient(90deg, #00d47a, #00c8e8); transition: width .6s ease; }
.trait-score-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: rgba(0,212,122,0.45); width: 24px; text-align: right; flex-shrink: 0; }

/* ════════════════════════════════════════════════
   EXPANDER
════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: rgba(0,212,122,0.05) !important;
    border: 1px solid rgba(0,212,122,0.14) !important;
    border-radius: 12px !important;
    color: rgba(160,210,185,0.75) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: rgba(8,18,12,0.9) !important;
    border: 1px solid rgba(0,212,122,0.08) !important;
    border-radius: 0 0 12px 12px !important;
    padding: 16px !important;
}

/* ════════════════════════════════════════════════
   ALERTS / INFO BOXES
════════════════════════════════════════════════ */
.stSuccess > div {
    background: rgba(0,212,122,0.07) !important;
    border-left: 3px solid #00d47a !important;
    border-radius: 10px !important; color: #c8e8d8 !important;
}
.stWarning > div {
    background: rgba(157,111,255,0.07) !important;
    border-left: 3px solid #9d6fff !important;
    border-radius: 10px !important; color: #c8c8e8 !important;
}
.stInfo > div {
    background: rgba(0,200,232,0.07) !important;
    border-left: 3px solid #00c8e8 !important;
    border-radius: 10px !important; color: #c8e8f8 !important;
}
div[data-testid="stCaptionContainer"] p {
    color: rgba(0,212,122,0.38) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
}

.info-box {
    background: rgba(0,200,232,0.06); border: 1px solid rgba(0,200,232,0.18);
    border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;
    color: rgba(180,228,248,0.85); font-size: 13px; line-height: 1.65;
}
.tip-box {
    background: rgba(157,111,255,0.06); border: 1px solid rgba(157,111,255,0.18);
    border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;
    color: rgba(210,195,255,0.82); font-size: 13px; line-height: 1.65;
}
.success-box {
    background: rgba(0,212,122,0.06); border: 1px solid rgba(0,212,122,0.18);
    border-radius: 12px; padding: 14px 18px; margin-bottom: 14px;
    color: rgba(180,240,215,0.88); font-size: 13px; line-height: 1.65;
}

/* ════════════════════════════════════════════════
   DOMAIN COMPARISON ROW
════════════════════════════════════════════════ */
.domain-row {
    display: flex; align-items: center; gap: 12px;
    padding: 9px 12px; border-radius: 10px; margin-bottom: 5px;
    background: rgba(0,212,122,0.02);
    border: 1px solid rgba(0,212,122,0.07);
    transition: all .2s;
}
.domain-row:hover { background: rgba(0,212,122,0.05); border-color: rgba(0,212,122,0.20); }
.domain-rank-num { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600; color: rgba(0,212,122,0.45); width: 26px; flex-shrink: 0; text-align: center; }
.domain-name { font-size: 13px; font-weight: 600; color: #c8e8d8; flex: 1; }
.domain-bar-wrap { width: 110px; }
.domain-bar { height: 4px; border-radius: 100px; background: linear-gradient(90deg,#00d47a,#00c8e8); }
.domain-pts { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: rgba(0,212,122,0.45); width: 38px; text-align: right; }

/* ════════════════════════════════════════════════
   TABS (Streamlit)
════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(12,28,20,0.8) !important;
    border-radius: 14px !important;
    padding: 6px !important;
    border: 1px solid rgba(0,212,122,0.10) !important;
    margin-bottom: 20px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    color: rgba(160,210,185,0.55) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important; font-weight: 600 !important;
    padding: 8px 18px !important;
    border: none !important;
    transition: all .2s !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #00d47a !important; background: rgba(0,212,122,0.06) !important; }
.stTabs [aria-selected="true"] {
    background: rgba(0,212,122,0.12) !important;
    color: #00d47a !important;
    border: none !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ════════════════════════════════════════════════
   DIVIDERS
════════════════════════════════════════════════ */
.neon-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,212,122,0.25), transparent);
    margin: 20px 0; border: none;
}
.section-gap { margin-bottom: 18px; }

/* ═══════════════════════════════════════════════
   HOW IT WORKS
════════════════════════════════════════════════ */
.how-step-card {
    display: flex; gap: 16px; align-items: flex-start;
    padding: 18px; border-radius: 14px;
    background: rgba(0,212,122,0.02);
    border: 1px solid rgba(0,212,122,0.08);
    margin-bottom: 12px; transition: .2s;
}
.how-step-card:hover { background: rgba(0,212,122,0.05); border-color: rgba(0,212,122,0.20); }
.how-step-num {
    width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
    background: linear-gradient(135deg, #00d47a, #00c8e8);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 800; color: #041a0d;
}
.how-step-title { font-family: 'Syne', sans-serif; font-size: 14px; font-weight: 700; color: #d8f0e8; margin-bottom: 5px; }
.how-step-desc { font-size: 13px; color: rgba(180,230,205,0.6); line-height: 1.7; }

</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
#  DATA
# ════════════════════════════════════════════════════════════
MBTI_DATA = {
    "INTJ": ("The Architect",     "Strategic mastermind — you see the big picture and build systems to get there. Natural fit for complex technical roles."),
    "INTP": ("The Logician",      "Brilliant problem-solver who loves deep theory. You thrive where curiosity meets complexity."),
    "ENTJ": ("The Commander",     "Born leader with unstoppable drive. You build teams, systems, and companies."),
    "ENTP": ("The Debater",       "Restless innovator who loves challenging assumptions. You turn ideas into disruption."),
    "ENFP": ("The Campaigner",    "Creative visionary with contagious energy. You connect people, ideas, and possibilities."),
    "ENFJ": ("The Protagonist",   "Inspiring leader who brings out the best in others. You lead with empathy and vision."),
    "INFJ": ("The Advocate",      "Deep thinker with a mission. You combine creativity with purpose to make lasting impact."),
    "INFP": ("The Mediator",      "Values-driven creator who works best on meaningful projects. Design and storytelling energize you."),
    "ESTJ": ("The Executive",     "Master organizer and implementer. You bring order, efficiency, and results to any team."),
    "ISTJ": ("The Inspector",     "Reliable, detail-obsessed, and methodical. The backbone of every high-performing system."),
    "ESFJ": ("The Consul",        "Warm, organized, and people-focused. You excel in roles that blend coordination with care."),
    "ISFJ": ("The Defender",      "Loyal and practical with a sharp eye for detail. You protect quality and support others."),
    "ESTP": ("The Entrepreneur",  "Bold, action-oriented, and adaptable. You thrive in fast-paced environments."),
    "ISTP": ("The Virtuoso",      "Hands-on problem solver with sharp technical instincts. You prefer doing over theorizing."),
    "ESFP": ("The Entertainer",   "Energetic and creative — you make work feel alive. Marketing and UX are your arenas."),
    "ISFP": ("The Adventurer",    "Artistic and empathetic. You bring beauty and meaning to everything you create."),
}

ROADMAPS = {
    "Data Science":          ["Python Mastery", "Statistics & Probability", "Pandas & NumPy", "Machine Learning", "Data Visualization", "SQL & Databases", "Model Deployment & MLOps"],
    "Machine Learning":      ["Linear Algebra & Calculus", "Probability Theory", "Scikit-learn", "PyTorch / TensorFlow", "Deep Learning Basics", "NLP & Computer Vision", "MLOps & Deployment"],
    "Deep Learning":         ["Neural Network Fundamentals", "CNNs for Vision", "RNNs & Transformers", "PyTorch Advanced", "Hyperparameter Tuning", "Generative AI", "Research Paper Implementation"],
    "AI Engineering":        ["Python & APIs", "LLM Fundamentals", "Prompt Engineering", "LangChain & Agents", "Vector Databases", "RAG Systems", "Production Deployment"],
    "Cybersecurity":         ["Networking Fundamentals", "Linux & Bash", "Ethical Hacking", "Penetration Testing", "Cryptography", "Cloud Security", "Incident Response & Forensics"],
    "Blockchain":            ["Blockchain Concepts", "Solidity Programming", "Smart Contracts", "DeFi Protocols", "Web3 & dApps", "Security Auditing", "Layer 2 & Scaling"],
    "Web Dev — Frontend":    ["HTML5 & Semantics", "CSS & Tailwind", "JavaScript ES6+", "React & Next.js", "State Management", "Performance & SEO", "Testing & Deployment"],
    "Web Dev — Backend":     ["Node.js & Express", "REST & GraphQL APIs", "Databases (SQL + NoSQL)", "Authentication & Auth", "Caching & Redis", "System Scaling", "Microservices"],
    "Full Stack Dev":        ["Frontend Fundamentals", "Backend & APIs", "Database Design", "Authentication", "DevOps Basics", "Cloud Deployment", "System Architecture"],
    "Mobile App Dev":        ["React Native / Flutter", "Mobile UI/UX", "State Management", "Native APIs", "Push Notifications", "Offline Support", "App Store Publishing"],
    "Game Development":      ["C# & Unity Basics", "Game Physics", "3D Modeling Intro", "Shader Programming", "AI in Games", "Multiplayer Networking", "Publishing & Monetization"],
    "Cloud Computing":       ["Cloud Fundamentals", "AWS / Azure / GCP", "Infrastructure as Code", "Containerization", "Kubernetes", "Cloud Security", "Cost Optimization"],
    "DevOps & SRE":          ["Linux Systems", "Git & CI/CD", "Docker", "Kubernetes", "Monitoring & Alerting", "Infrastructure as Code", "Site Reliability Engineering"],
    "Software Engineering":  ["Data Structures", "Algorithms", "OOP & Design Patterns", "System Design", "Testing Strategies", "Code Review", "Agile & Team Workflows"],
    "UI/UX Design":          ["Design Principles", "Figma Mastery", "User Research", "Wireframing", "Prototyping", "Usability Testing", "Design Systems"],
    "Data Engineering":      ["Python & SQL", "ETL Pipelines", "Apache Spark", "Data Warehousing", "Airflow Orchestration", "Streaming (Kafka)", "Data Quality & Governance"],
    "Embedded Systems":      ["C / C++", "Microcontroller Programming", "Real-Time OS", "Sensors & Actuators", "Communication Protocols", "PCB Design Basics", "Debugging & Testing"],
    "IoT Development":       ["IoT Architecture", "Edge Computing", "MQTT & LoRa", "Sensor Integration", "Cloud IoT", "IoT Security", "Device Management"],
    "AR/VR Development":     ["Unity & C#", "3D Spatial Design", "VR SDKs (Meta / OpenXR)", "Spatial Audio", "Interaction Design", "Performance for XR", "Deployment & Publishing"],
    "Digital Marketing":     ["SEO & Content Strategy", "Social Media Marketing", "Google Ads & PPC", "Email Automation", "Analytics & GA4", "Conversion Optimization", "Marketing Funnels"],
    "Product Management":    ["Market Research", "Product Strategy", "Agile & Scrum", "User Story Mapping", "Roadmapping", "Stakeholder Communication", "Data-Driven Decisions"],
    "Business Intelligence": ["SQL for Analytics", "Power BI / Tableau", "Data Modeling", "KPI Design", "Reporting Automation", "Predictive Analytics", "Business Strategy"],
    "Quantitative Finance":  ["Financial Mathematics", "Python for Finance", "Time Series Analysis", "Risk Modeling", "Algorithmic Trading", "Portfolio Optimization", "Quant Research"],
}

DOMAIN_WEIGHTS = {
    "Data Science":          {"analytical": 3, "structured": 2, "detail_oriented": 2, "theoretical": 1},
    "Machine Learning":      {"analytical": 3, "theoretical": 2, "structured": 2, "practical": 1},
    "Deep Learning":         {"analytical": 3, "theoretical": 3, "practical": 1},
    "AI Engineering":        {"analytical": 3, "practical": 2, "independent": 2},
    "Cybersecurity":         {"analytical": 3, "introvert": 2, "careful_decision": 2, "detail_oriented": 1},
    "Blockchain":            {"analytical": 2, "risk_taking": 2, "independent": 2, "theoretical": 1},
    "Web Dev — Frontend":    {"creative": 3, "flexible": 2, "big_picture": 2, "practical": 1},
    "Web Dev — Backend":     {"analytical": 3, "structured": 2, "practical": 2},
    "Full Stack Dev":        {"analytical": 2, "flexible": 2, "practical": 3},
    "Mobile App Dev":        {"creative": 2, "practical": 3, "flexible": 2},
    "Game Development":      {"creative": 3, "practical": 2, "big_picture": 2, "risk_taking": 1},
    "Cloud Computing":       {"structured": 3, "analytical": 2, "stable": 2, "practical": 1},
    "DevOps & SRE":          {"structured": 3, "analytical": 2, "practical": 2, "stable": 1},
    "Software Engineering":  {"analytical": 3, "structured": 2, "practical": 2, "detail_oriented": 1},
    "UI/UX Design":          {"creative": 3, "big_picture": 2, "flexible": 2, "extrovert": 1},
    "Data Engineering":      {"analytical": 3, "structured": 3, "detail_oriented": 2},
    "Embedded Systems":      {"analytical": 2, "practical": 3, "detail_oriented": 2, "structured": 1},
    "IoT Development":       {"practical": 3, "analytical": 2, "flexible": 2},
    "AR/VR Development":     {"creative": 3, "practical": 2, "big_picture": 2},
    "Digital Marketing":     {"creative": 3, "extrovert": 2, "flexible": 2, "big_picture": 1},
    "Product Management":    {"leadership": 3, "extrovert": 2, "big_picture": 3, "analytical": 1},
    "Business Intelligence": {"analytical": 3, "structured": 2, "detail_oriented": 2},
    "Quantitative Finance":  {"analytical": 3, "theoretical": 3, "detail_oriented": 2},
}

QUESTIONS = [
    ("I solve complex problems step-by-step using logic and reasoning.",    {"analytical": 2},   {"creative": 1}),
    ("I love coming up with new ideas and thinking outside the box.",        {"creative": 2},     {"analytical": 1}),
    ("I prefer working quietly on my own rather than in a group.",           {"introvert": 2},    {"extrovert": 1}),
    ("I feel more energized when working with and talking to people.",       {"extrovert": 2},    {"introvert": 1}),
    ("I enjoy taking charge and leading projects or teams.",                 {"leadership": 2},   {"supportive": 1}),
    ("I prefer being the one who executes rather than directs.",             {"supportive": 2},   {"leadership": 1}),
    ("I like having a clear plan and schedule before starting anything.",    {"structured": 2},   {"flexible": 1}),
    ("I adapt quickly and am comfortable changing plans on the go.",         {"flexible": 2},     {"structured": 1}),
    ("I enjoy taking calculated risks if the reward is worth it.",           {"risk_taking": 2},  {"stable": 1}),
    ("I prefer a stable, predictable path over uncertain opportunities.",    {"stable": 2},       {"risk_taking": 1}),
    ("I enjoy analyzing data, numbers, and finding patterns.",               {"analytical": 2},   {"creative": 1}),
    ("I am drawn to artistic, visual, or design-oriented work.",             {"creative": 2},     {"analytical": 1}),
    ("I work best when collaborating closely with others.",                   {"extrovert": 2},    {"introvert": 1}),
    ("I do my best thinking when I have uninterrupted solo focus time.",     {"introvert": 2},    {"extrovert": 1}),
    ("I naturally take initiative and start things without being asked.",    {"leadership": 2},   {"supportive": 1}),
    ("I prefer clear instructions and defined responsibilities.",             {"supportive": 2},   {"leadership": 1}),
    ("I feel comfortable and confident in structured environments.",          {"structured": 2},   {"flexible": 1}),
    ("I thrive in ambiguous, open-ended projects with no fixed blueprint.",  {"flexible": 2},     {"structured": 1}),
    ("I am energized by uncertainty — it makes work exciting.",              {"risk_taking": 2},  {"stable": 1}),
    ("I prefer knowing exactly what outcome to expect from my efforts.",     {"stable": 2},       {"risk_taking": 1}),
    ("I enjoy puzzles, brain teasers, and optimizing systems.",              {"analytical": 2},   {"creative": 1}),
    ("I enjoy writing, storytelling, illustration, or visual expression.",   {"creative": 2},     {"analytical": 1}),
    ("I gain energy from brainstorming sessions and group collaboration.",   {"extrovert": 2},    {"introvert": 1}),
    ("I prefer making decisions independently without needing consensus.",   {"independent": 2},  {"collaborative": 1}),
]

TRAITS = [
    "analytical", "creative", "introvert", "extrovert", "structured", "flexible",
    "leadership", "supportive", "risk_taking", "stable", "independent", "collaborative",
    "theoretical", "practical", "fast_decision", "careful_decision",
    "money_oriented", "passion_oriented", "detail_oriented", "big_picture",
]

DOMAIN_CATEGORIES = {
    "🤖 AI & Data":       ["Data Science", "Machine Learning", "Deep Learning", "AI Engineering", "Data Engineering", "Business Intelligence", "Quantitative Finance"],
    "💻 Software":         ["Software Engineering", "Web Dev — Frontend", "Web Dev — Backend", "Full Stack Dev", "Mobile App Dev", "DevOps & SRE", "Cloud Computing"],
    "⚡ Emerging Tech":   ["Cybersecurity", "Blockchain", "IoT Development", "Embedded Systems", "AR/VR Development", "Game Development"],
    "🎨 Creative & Biz":  ["UI/UX Design", "Digital Marketing", "Product Management"],
}

# ════════════════════════════════════════════════════════════
#  SESSION STATE
# ════════════════════════════════════════════════════════════
defaults = {
    "traits":        {t: 0 for t in TRAITS},
    "q_index":       0,
    "is_analyzed":   False,
    "start_time":    time.time(),
    "user_name":     "Your Name",
    "active_page":   "home",   # home | assess | explore | compare | how | arch
    "saved_results": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ════════════════════════════════════════════════════════════
def render_steps(steps):
    html = ""
    for i, s in enumerate(steps, 1):
        html += f"""
        <div class="step-item">
          <span class="step-num">{i:02d}</span>
          <span class="step-text">{s}</span>
          <span class="step-check"></span>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_trait_bars(traits_dict, top_n=10):
    top = sorted([(k, v) for k, v in traits_dict.items() if v > 0],
                 key=lambda x: x[1], reverse=True)[:top_n]
    if not top:
        st.markdown(
            '<p style="color:rgba(0,212,122,0.28);font-size:12px;'
            'font-family:\'JetBrains Mono\',monospace;">Answer questions to reveal your traits...</p>',
            unsafe_allow_html=True,
        )
        return
    max_v = top[0][1] or 1
    html = ""
    for k, v in top:
        pct = round(v / max_v * 100)
        label = k.replace("_", " ").title()
        html += f"""
        <div class="trait-row">
          <span class="trait-label">{label}</span>
          <div class="trait-bar-track">
            <div class="trait-bar-fill" style="width:{pct}%"></div>
          </div>
          <span class="trait-score-val">{v}</span>
        </div>"""
    st.markdown(html, unsafe_allow_html=True)


def compute_scores():
    ft = st.session_state.traits
    return sorted(
        {d: sum(ft.get(t, 0) * w for t, w in wts.items())
         for d, wts in DOMAIN_WEIGHTS.items()}.items(),
        key=lambda x: x[1], reverse=True
    )


def get_ml_confidence():
    """Simulate ML Random Forest confidence based on trait score spread."""
    ft = st.session_state.traits
    total = sum(v for v in ft.values() if v > 0)
    if total == 0:
        return 78.0, "Analytical Thinker"
    analytical = ft.get("analytical", 0) + ft.get("structured", 0)
    creative   = ft.get("creative", 0)   + ft.get("flexible", 0)
    social     = ft.get("extrovert", 0)  + ft.get("leadership", 0)
    practical  = ft.get("practical", 0)  + ft.get("detail_oriented", 0)
    clusters   = {"Analytical Thinker": analytical, "Creative Visionary": creative,
                  "Social Connector": social, "Practical Builder": practical}
    top_style  = max(clusters, key=clusters.get)
    max_score  = max(clusters.values()) or 1
    confidence = min(98.0, round(55 + (max_score / (total / len(ft) + 1)) * 22, 1))
    return confidence, top_style


def get_mbti():
    ft = st.session_state.traits
    return (
        ("E" if ft["extrovert"] >= ft["introvert"] else "I") +
        ("N" if ft["creative"]  >= ft["structured"] else "S") +
        ("T" if ft["analytical"] >= ft["supportive"] else "F") +
        ("J" if ft["structured"] >= ft["flexible"]   else "P")
    )


def card_open(icon, title, subtitle=""):
    sub_html = f'<div class="card-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div class="card">
      <div class="card-header">
        <div class="card-icon">{icon}</div>
        <div>
          <div class="card-title">{title}</div>
          {sub_html}
        </div>
      </div>
    """, unsafe_allow_html=True)


def card_close():
    st.markdown("</div>", unsafe_allow_html=True)


def nav_to(page):
    st.session_state.active_page = page
    st.rerun()


# ════════════════════════════════════════════════════════════
#  TOP NAVBAR
# ════════════════════════════════════════════════════════════
q_done   = st.session_state.q_index
q_total  = len(QUESTIONS)
pct_done = round(q_done / q_total * 100)
page     = st.session_state.active_page
import streamlit as st

# 1. Custom CSS inside style tag
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500&display=swap');

    .topnav-brand {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .topnav-title {
        font-family: 'Sora', sans-serif !important;
        font-weight: 700 !important;
        font-size: 22px !important;
        line-height: 1.1;
        background: linear-gradient(90deg, #00d47a, #00c8e8, #9d6fff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .topnav-sub {
        font-family: 'Inter', sans-serif !important;
        font-weight: 400 !important;
        font-size: 12px !important;
        color: #888;
        letter-spacing: 0.5px;
    }

    .chip-green {
        font-family: 'Inter', sans-serif !important;
        background: rgba(0, 212, 122, 0.1);
        color: #00d47a;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        border: 1px solid rgba(0, 212, 122, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 2. Your existing Navbar code (unchanged structure)
st.markdown(f"""
<div class="topnav" style="display: flex; justify-content: space-between; align-items: center;">
  <div class="topnav-brand">
    <svg width="38" height="38" viewBox="0 0 38 38" fill="none">
      <defs>
        <linearGradient id="nlg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#00d47a"/>
          <stop offset="50%" stop-color="#00c8e8"/>
          <stop offset="100%" stop-color="#9d6fff"/>
        </linearGradient>
      </defs>
      <polygon points="19,2 34,11 34,27 19,36 4,27 4,11"
               fill="none" stroke="url(#nlg)" stroke-width="1"
               stroke-dasharray="2 2.2" opacity=".5"/>
      <polygon points="19,6 30,13 30,25 19,32 8,25 8,13"
               fill="rgba(0,212,122,0.06)" stroke="url(#nlg)" stroke-width=".8"/>
      <path d="M21.5 7.5L15 19H19L16.5 30.5L23 19H19L21.5 7.5Z" fill="url(#nlg)"/>
    </svg>
    <div>
      <div class="topnav-title">PathAi 360</div>
      <div class="topnav-sub">Find Your Future Career Free</div>
    </div>
  </div>
  <div class="topnav-chips">
    {"<span class='chip-green'>✓ Analysis Complete</span>" if st.session_state.get('is_analyzed', False) else ""}
  </div>
</div>
<div style="height:16px"></div>
""", unsafe_allow_html=True)
# ════════════════════════════════════════════════════════════
#  PAGE-LEVEL NAVIGATION — clean pill buttons, SVG icons
# ════════════════════════════════════════════════════════════
elapsed = round(time.time() - st.session_state.start_time)
mins, secs = elapsed // 60, elapsed % 60

_pages  = ["home",   "assess",     "explore",      "compare",    "how",          "arch"]
_labels = ["Home",   "Assessment", "Career Paths",  "Comparison", "How It Works", "Architecture"]

_nav_cols = st.columns(len(_pages), gap="small")

for _ci, (_pg, _lbl) in enumerate(zip(_pages, _labels)):
    with _nav_cols[_ci]:
        _is_active = (page == _pg)
        _bg  = "rgba(0,212,122,0.13)" if _is_active else "rgba(255,255,255,0.02)"
        _clr = "#00d47a" if _is_active else "rgba(180,220,200,0.55)"
        _bdr = "1px solid rgba(0,212,122,0.40)" if _is_active else "1px solid rgba(0,212,122,0.10)"
        _fw  = "700" if _is_active else "500"
        _shd = "0 0 18px rgba(0,212,122,0.12) inset" if _is_active else "none"
        st.markdown(
            "<style>"
            f"div[data-testid='stHorizontalBlock']>div:nth-child({_ci+1}) .stButton>button{{"
            f"background:{_bg}!important;color:{_clr}!important;border:{_bdr}!important;"
            "border-radius:10px!important;font-family:'DM Sans',sans-serif!important;"
            f"font-size:12.5px!important;font-weight:{_fw}!important;"
            "padding:8px 10px!important;white-space:nowrap!important;overflow:hidden!important;"
            "text-overflow:ellipsis!important;height:38px!important;min-height:38px!important;"
            f"box-shadow:{_shd}!important;letter-spacing:0.1px!important;}}"
            f"div[data-testid='stHorizontalBlock']>div:nth-child({_ci+1}) .stButton>button:hover{{"
            "background:rgba(0,212,122,0.08)!important;border-color:rgba(0,212,122,0.28)!important;"
            "color:#c8e8d8!important;transform:none!important;box-shadow:none!important;}}"
            "</style>",
            unsafe_allow_html=True,
        )
        if st.button(_lbl, use_container_width=True, key=f"nav_{_pg}"):
            nav_to(_pg)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.markdown("<hr class='neon-divider'/>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  ██  HOME PAGE
# ════════════════════════════════════════════════════════════
if page == "home":

    st.markdown(f"""
    <div class="home-hero">
      <div class="home-badge">
        ✦ Free for students  no signup needed
      </div>
      <div class="home-h1">
        Find the Right Career<br/>
        <span class="grad">Made for You</span>
      </div>
      <div class="home-sub">
        Answer 24 quick questions and discover which tech career matches your personality, strengths, and working style.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA buttons
    hc1, hc2, hc3 = st.columns([1, 1, 2], gap="small")
    with hc1:
        if st.button("🚀 Start Free Test", use_container_width=True):
            nav_to("assess")
    with hc2:
        if st.button("🗺️ Browse Careers", use_container_width=True):
            nav_to("explore")

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # Stats row
    st.markdown("""
    <div class="home-stats-row">
      <div class="hstat"><div class="hstat-num">24</div><div class="hstat-lbl">Questions</div></div>
      <div class="hstat"><div class="hstat-num">23</div><div class="hstat-lbl">Career Paths</div></div>
      <div class="hstat"><div class="hstat-num">16</div><div class="hstat-lbl">Personality Types</div></div>
      <div class="hstat"><div class="hstat-num">5</div><div class="hstat-lbl">Learning Styles</div></div>
      <div class="hstat"><div class="hstat-num">Free</div><div class="hstat-lbl">Always</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)

    # Feature cards
    st.markdown("""
    <div class="home-feat-grid" style="grid-template-columns:repeat(4,1fr)">
      <div class="home-feat-card">
        <div class="hfc-icon">🧠</div>
        <div class="hfc-title">Know Your Personality</div>
        <div class="hfc-desc">Answer 24 quick questions to discover how you think, work, and make decisions.</div>
        <div class="hfc-arrow">Take the test →</div>
      </div>
      <div class="home-feat-card">
        <div class="hfc-icon">🎯</div>
        <div class="hfc-title">Get Your Best Career Matches</div>
        <div class="hfc-desc">We rank 23 tech careers by how well they fit your unique strengths and style.</div>
        <div class="hfc-arrow">See your results →</div>
      </div>
      <div class="home-feat-card">
        <div class="hfc-icon">🗺️</div>
        <div class="hfc-title">Explore Career Paths</div>
        <div class="hfc-desc">Browse all 23 tech careers with step-by-step learning roadmaps to get started.</div>
        <div class="hfc-arrow">Browse paths →</div>
      </div>
      <div class="home-feat-card">
        <div class="hfc-icon">📊</div>
        <div class="hfc-title">Compare Side by Side</div>
        <div class="hfc-desc">Not sure between two careers? Compare them directly to pick the right one for you.</div>
        <div class="hfc-arrow">Compare now →</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    # How it works teaser
    st.markdown('<div class="page-header"><div class="page-header-h">How PathAI 360 Works</div><div class="page-header-sub">Three simple steps from questions to your career match</div></div>', unsafe_allow_html=True)

    hw1, hw2, hw3 = st.columns(3, gap="medium")
    with hw1:
        st.markdown("""
        <div class="how-step-card">
          <div class="how-step-num">1</div>
          <div>
            <div class="how-step-title">Answer 24 Questions</div>
            <div class="how-step-desc">Simple questions about how you think, work, and make decisions. No right or wrong answers.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with hw2:
        st.markdown("""
        <div class="how-step-card">
          <div class="how-step-num">2</div>
          <div>
            <div class="how-step-title">Discover Your Profile</div>
            <div class="how-step-desc">We identify your personality type and natural strengths from your responses.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with hw3:
        st.markdown("""
        <div class="how-step-card">
          <div class="how-step-num">3</div>
          <div>
            <div class="how-step-title">Get Your Career Matches</div>
            <div class="how-step-desc">We rank 23 tech careers by how well they suit your personality and learning style.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  ██  ASSESSMENT PAGE
# ════════════════════════════════════════════════════════════
elif page == "assess":

    st.markdown(f"""
    <div class="page-header">
      <div class="page-header-h">🧠 Personality Assessment</div>
      <div class="page-header-sub">Answer all 24 questions honestly for the most accurate career match</div>
      <div class="page-header-chips">
        <span class="chip chip-purple">{q_done}/{q_total} Complete · {pct_done}%</span>
        {"<span class='chip chip-green'>✓ Analysis Complete</span>" if st.session_state.is_analyzed else ""}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Stat cards
    s1, s2, s3, s4 = st.columns(4, gap="small")
    with s1:
        st.markdown(f"""
        <div class="stat-box">
          <span class="stat-icon">🎯</span>
          <div class="stat-number">{q_done}</div>
          <div class="stat-label">Questions Done</div>
          <div class="stat-detail">of {q_total} total</div>
        </div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class="stat-box">
          <span class="stat-icon">🗂️</span>
          <div class="stat-number-p">{len(ROADMAPS)}</div>
          <div class="stat-label">Career Paths</div>
          <div class="stat-detail">mapped & indexed</div>
        </div>""", unsafe_allow_html=True)
    with s3:
        if st.session_state.is_analyzed:
            top = compute_scores()[0]
            st.markdown(f"""
            <div class="stat-box">
              <span class="stat-icon">🏆</span>
              <div class="stat-number" style="font-size:18px;-webkit-text-fill-color:#00d47a">{top[0].split()[0]}</div>
              <div class="stat-label">Top Career Match</div>
              <div class="stat-detail">{top[1]} pts scored</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stat-box">
              <span class="stat-icon">🏆</span>
              <div class="stat-number" style="-webkit-text-fill-color:rgba(0,212,122,0.18)">—</div>
              <div class="stat-label">Top Career Match</div>
              <div class="stat-detail">awaiting analysis</div>
            </div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""
        <div class="stat-box">
          <span class="stat-icon">🌟</span>
          <div class="stat-number" style="font-size:24px">23</div>
          <div class="stat-label">Career Paths</div>
          <div class="stat-detail">waiting to be explored</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 2], gap="large")

    with col_main:
        # ── IDENTITY ──
        card_open("👤", "Your Profile", "Enter your name to personalize your results")
        st.session_state.user_name = st.text_input(
            "Full Name", value=st.session_state.user_name,
            placeholder="e.g. Azhar Ali",
        )
        card_close()

        # ── ASSESSMENT OR RESULTS ──
        if not st.session_state.is_analyzed:
            idx = st.session_state.q_index

            if idx < len(QUESTIONS):
                card_open("🧠", "Personality Assessment", f"Question {idx+1} of {len(QUESTIONS)}")

                pct = (idx + 1) / len(QUESTIONS)
                c1, c2 = st.columns([5, 1])
                with c1:
                    st.markdown(f'<div class="q-counter">Question {idx+1} / {len(QUESTIONS)}</div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="q-pct">{round(pct*100)}%</div>', unsafe_allow_html=True)

                st.progress(pct)

                question, pos_w, neg_w = QUESTIONS[idx]
                st.markdown(f'<div class="question-text">{question}</div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size:12px;color:rgba(0,212,122,0.5);margin-bottom:10px;font-weight:500;">How much does this describe you?</p>', unsafe_allow_html=True)

                choice = st.radio(
                    "Your answer",
                    options=["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
                    index=2,
                    key=f"q_{idx}",
                    horizontal=True,
                    label_visibility="collapsed",
                )

                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

                n1, n2, n3 = st.columns([1, 1, 1])
                with n1:
                    if idx > 0:
                        with st.container():
                            st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
                            if st.button("← Previous", key="prev", use_container_width=True):
                                st.session_state.q_index -= 1
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                with n3:
                    if st.button(
                        "Next Question →" if idx < len(QUESTIONS) - 1 else "✅ Submit & Analyze",
                        key="next", use_container_width=True
                    ):
                        if choice != "Neutral":
                            scale = 2 if "Strongly" in choice else 1
                            target = pos_w if "Agree" in choice else neg_w
                            for trait, val in target.items():
                                st.session_state.traits[trait] += val * scale
                        st.session_state.q_index += 1
                        if st.session_state.q_index >= len(QUESTIONS):
                            st.session_state.is_analyzed = True
                        st.rerun()

                card_close()

                remaining = len(QUESTIONS) - idx - 1
                if remaining > 0:
                    st.markdown(
                        f'<div class="info-box">💡 <strong>{remaining} questions remaining.</strong> '
                        f'There are no right or wrong answers — choose what feels most natural.</div>',
                        unsafe_allow_html=True,
                    )

            else:
                st.session_state.is_analyzed = True
                st.rerun()

        else:
            # ── RESULTS ──
            scores = compute_scores()
            top3   = scores[:3]
            mbti   = get_mbti()
            title, desc = MBTI_DATA.get(mbti, ("Specialist", "A unique, multi-faceted professional profile."))
            confidence, learning_style = get_ml_confidence()

            # MBTI Hero
            st.markdown(f"""
            <div class="mbti-hero">
              <div class="mbti-badge">
                <span style="width:6px;height:6px;border-radius:50%;background:#00d47a;
                             display:inline-block;box-shadow:0 0 7px #00d47a;
                             animation:blink 2s infinite"></span>
                ANALYSIS COMPLETE
              </div>
              <div class="mbti-type-name">{mbti} &nbsp;·&nbsp; {title}</div>
              <div class="mbti-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

            # Results Intelligence Panel
            st.markdown(f"""
            <div class="card" style="margin-bottom:18px">
              <div class="card-header">
                <div class="card-icon">🎯</div>
                <div>
                  <div class="card-title">Your Analysis Results</div>
                  <div class="card-subtitle">Based on your answers — here's what we found about you</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-top:4px">
                <div style="background:rgba(0,212,122,0.05);border:1px solid rgba(0,212,122,0.15);border-radius:12px;padding:14px;text-align:center">
                  <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(0,212,122,0.5);text-transform:uppercase;margin-bottom:6px">Match Confidence</div>
                  <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;background:linear-gradient(120deg,#00d47a,#00c8e8);-webkit-background-clip:text;-webkit-text-fill-color:transparent">{confidence}%</div>
                  <div style="font-size:10px;color:rgba(140,200,170,0.4);margin-top:3px;font-family:'JetBrains Mono',monospace">how well it fits you</div>
                </div>
                <div style="background:rgba(0,200,232,0.05);border:1px solid rgba(0,200,232,0.15);border-radius:12px;padding:14px;text-align:center">
                  <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(0,200,232,0.5);text-transform:uppercase;margin-bottom:6px">How You Learn</div>
                  <div style="font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#00c8e8;line-height:1.2">{learning_style}</div>
                  <div style="font-size:10px;color:rgba(140,200,170,0.4);margin-top:3px;font-family:'JetBrains Mono',monospace">your learning style</div>
                </div>
                <div style="background:rgba(157,111,255,0.05);border:1px solid rgba(157,111,255,0.15);border-radius:12px;padding:14px;text-align:center">
                  <div style="font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(157,111,255,0.5);text-transform:uppercase;margin-bottom:6px">Traits Analyzed</div>
                  <div style="font-family:'Syne',sans-serif;font-size:28px;font-weight:800;background:linear-gradient(120deg,#9d6fff,#00c8e8);-webkit-background-clip:text;-webkit-text-fill-color:transparent">20</div>
                  <div style="font-size:10px;color:rgba(140,200,170,0.4);margin-top:3px;font-family:'JetBrains Mono',monospace">personality traits</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Top 3 Matches
            card_open("🏆", "Your Top Career Matches", "Based on your personality traits and strengths")
            medals      = ["🥇", "🥈", "🥉"]
            rank_labels = ["#1 Best Match", "#2 Strong Match", "#3 Good Match"]
            rank_classes = ["match-card-1", "match-card-2", "match-card-3"]
            rank_colors  = ["pts-1", "pts-2", "pts-3"]
            rank_txt     = ["rank-1", "rank-2", "rank-3"]

            html = '<div class="match-grid">'
            for i, (name, pts) in enumerate(top3):
                html += f"""
                <div class="match-card {rank_classes[i]}">
                  <span class="match-medal">{medals[i]}</span>
                  <div class="match-rank {rank_txt[i]}">{rank_labels[i]}</div>
                  <div class="match-name">{name}</div>
                  <div class="match-pts {rank_colors[i]}">{pts}<span class="match-pts-label"> pts</span></div>
                </div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            card_close()

            # Primary Learning Roadmap
            primary = top3[0][0]
            card_open("📍", f"Your Personalized Roadmap: {primary}", "7-step learning path for your top career match")
            render_steps(ROADMAPS[primary])
            card_close()

            # Full ranking
            with st.expander("📋 See All Career Domain Rankings"):
                st.markdown('<p style="color:rgba(160,210,185,0.55);font-size:13px;margin-bottom:14px;">All 23 domains ranked by compatibility with your personality profile:</p>', unsafe_allow_html=True)
                max_pts = scores[0][1] if scores[0][1] > 0 else 1
                html = ""
                for rank, (name, pts) in enumerate(scores, 1):
                    bar_pct = round(pts / max_pts * 100) if max_pts > 0 else 0
                    html += f"""
                    <div class="domain-row">
                      <span class="domain-rank-num">{rank}</span>
                      <span class="domain-name">{name}</span>
                      <div class="domain-bar-wrap">
                        <div class="domain-bar" style="width:{bar_pct}%"></div>
                      </div>
                      <span class="domain-pts">{pts} pts</span>
                    </div>"""
                st.markdown(html, unsafe_allow_html=True)

            # ── SAVE TO MONGODB (once per session via db_saved guard) ──
            duration = round(time.time() - st.session_state.start_time)
            if not st.session_state.get("db_saved", False):
                if db_available():
                    try:
                        import uuid as _uuid
                        confidence_val, ls = get_ml_confidence()
                        user_name_clean = (st.session_state.user_name or "").strip()
                        if not user_name_clean or user_name_clean == "Your Name":
                            user_name_clean = "Anonymous"

                        user_id = str(_uuid.uuid4())

                        # 1. users collection
                        _db["users"].insert_one({
                            "_id":        user_id,
                            "name":       user_name_clean,
                            "grade":      10,
                            "role":       "student",
                            "created_at": datetime.datetime.utcnow().isoformat() + "Z",
                        })

                        # 2. answers collection — raw trait scores
                        _db["answers"].insert_one({
                            "_id":          str(_uuid.uuid4()),
                            "user_id":      user_id,
                            "traits":       st.session_state.traits,
                            "time_secs":    duration,
                            "submitted_at": datetime.datetime.utcnow().isoformat() + "Z",
                        })

                        # 3. results collection — full ML + MBTI result
                        total_ei = max(
                            st.session_state.traits.get("extrovert", 0) +
                            st.session_state.traits.get("introvert", 0), 1
                        )
                        e_pct = round(st.session_state.traits.get("extrovert", 0) / total_ei * 100)
                        _db["results"].insert_one({
                            "_id":              str(_uuid.uuid4()),
                            "user_id":          user_id,
                            "personality_type": mbti,
                            "description":      desc,
                            "sub_scores":       {"E_pct": e_pct, "I_pct": 100 - e_pct},
                            "career_interests": [d for d, _ in scores[:3]],
                            "ml_predictions": {
                                "mbti_type":      mbti,
                                "confidence":     confidence_val,
                                "learning_style": ls,
                            },
                            "top_match":        primary,
                            "all_scores":       [{"domain": d, "pts": p} for d, p in scores],
                            "duration_seconds": duration,
                            "created_at":       datetime.datetime.utcnow().isoformat() + "Z",
                        })

                        st.session_state["db_saved"] = True
                        saved_at = datetime.datetime.now().strftime("%H:%M:%S")
                        st.markdown(
                            f'<div class="success-box">✅ <strong>Profile saved to database</strong> &nbsp;·&nbsp; '                            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px">'                            f'users · answers · results &nbsp;·&nbsp; {saved_at}</span></div>',
                            unsafe_allow_html=True,
                        )

                    except Exception as save_err:
                        st.markdown(
                            f'<div class="tip-box">⚠️ <strong>DB save failed:</strong> '                            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px">{save_err}</span></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f'<div class="info-box">🔌 <strong>Offline mode</strong> — set <code>MONGO_URI</code> env var to enable saves.'                        f'<br><span style="font-size:11px;opacity:.6">Reason: {db_error()}</span></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="success-box">✅ <strong>Already saved</strong> — profile recorded in database this session.</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("🔄 Start New Analysis", use_container_width=True):
                for k in ["traits", "q_index", "is_analyzed", "start_time", "db_saved"]:
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

    # ── SIDEBAR PANEL ──
    with col_side:
        card_open("⚡", "Your Strengths Profile", "Updates live as you answer questions")
        render_trait_bars(st.session_state.traits)
        card_close()

        card_open("🗺️", "Quick Roadmap Preview", "Explore any career path instantly")
        with st.form("quick_roadmap"):
            chosen = st.selectbox("Select a domain", list(ROADMAPS.keys()), label_visibility="visible")
            go = st.form_submit_button("Show Roadmap", use_container_width=True)
        if go:
            st.markdown(f'<p style="font-size:12px;font-weight:700;color:#00d47a;margin-bottom:10px">{chosen}</p>', unsafe_allow_html=True)
            render_steps(ROADMAPS[chosen])
        card_close()

        st.markdown("""
        <div class="tip-box">
          <strong style="color:#c4a0f8">💡 Tips for best results</strong><br><br>
          • Answer based on your <strong>natural tendencies</strong>, not what you wish were true.<br><br>
          • There are <strong>no right or wrong</strong> answers — every profile leads to great careers.<br><br>
          • Complete all 24 questions for the most accurate match.
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  ██  EXPLORE CAREER PATHS PAGE
# ════════════════════════════════════════════════════════════
elif page == "explore":

    st.markdown("""
    <div class="page-header">
      <div class="page-header-h">🗺️ Explore Career Paths</div>
      <div class="page-header-sub">Browse all 23 tech career domains — expand any card to see the full 7-step roadmap</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="success-box">
      <strong>🗺️ 23 Career Domains</strong> — Browse every path, see the full roadmap, and find what excites you most.
    </div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Search career domains", placeholder="e.g. AI, Design, Security...", label_visibility="visible")

    for category, domains in DOMAIN_CATEGORIES.items():
        filtered = [d for d in domains if not search or search.lower() in d.lower()]
        if not filtered:
            continue

        st.markdown(
            f'<p style="font-size:10px;font-weight:700;letter-spacing:2px;'
            f'color:rgba(0,212,122,0.40);text-transform:uppercase;'
            f'margin-bottom:10px;margin-top:20px">{category}</p>',
            unsafe_allow_html=True,
        )

        cols = st.columns(min(len(filtered), 3), gap="small")
        for ci, domain in enumerate(filtered):
            with cols[ci % 3]:
                with st.expander(f"  {domain}"):
                    render_steps(ROADMAPS[domain])
                    if st.session_state.is_analyzed:
                        scores_dict = {
                            d: sum(st.session_state.traits.get(t, 0) * w for t, w in wts.items())
                            for d, wts in DOMAIN_WEIGHTS.items()
                        }
                        all_sorted = sorted(scores_dict.values(), reverse=True)
                        my_score = scores_dict.get(domain, 0)
                        my_rank  = all_sorted.index(my_score) + 1
                        st.markdown(
                            f'<p style="font-size:11px;color:#00d47a;font-weight:600;margin-top:10px">'
                            f'Your compatibility rank: #{my_rank} of {len(ROADMAPS)} &nbsp;·&nbsp; {my_score} pts</p>',
                            unsafe_allow_html=True,
                        )


# ════════════════════════════════════════════════════════════
#  ██  DOMAIN COMPARISON PAGE
# ════════════════════════════════════════════════════════════
elif page == "compare":

    st.markdown("""
    <div class="page-header">
      <div class="page-header-h">📊 Domain Comparison</div>
      <div class="page-header-sub">Select up to 4 domains and compare roadmaps & compatibility scores side by side</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
      <strong>📊 Side-by-Side Comparison</strong> — Select up to 4 domains below.
      Complete the assessment first to see your personal compatibility score for each domain.
    </div>
    """, unsafe_allow_html=True)

    selected_domains = st.multiselect(
        "Choose domains to compare (up to 4)",
        list(ROADMAPS.keys()),
        default=list(ROADMAPS.keys())[:2],
        max_selections=4,
    )

    if selected_domains:
        compare_cols = st.columns(len(selected_domains), gap="small")
        scores_dict = (
            {d: sum(st.session_state.traits.get(t, 0) * w for t, w in wts.items())
             for d, wts in DOMAIN_WEIGHTS.items()}
            if st.session_state.is_analyzed else {}
        )

        for ci, dom in enumerate(selected_domains):
            with compare_cols[ci]:
                score_html = (
                    f'<p style="font-size:12px;color:#00d47a;font-weight:700;margin-bottom:12px">'
                    f'Your score: {scores_dict.get(dom, "—")} pts</p>'
                    if st.session_state.is_analyzed else ""
                )
                st.markdown(f"""
                <div class="card">
                  <div style="font-family:\'Syne\',sans-serif;font-size:14px;font-weight:800;
                              color:#d8f0e8;margin-bottom:6px">{dom}</div>
                  {score_html}
                """, unsafe_allow_html=True)
                render_steps(ROADMAPS[dom])
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<p style="color:rgba(140,200,170,0.35);font-size:14px">Select at least one domain above to start comparing.</p>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════
#  ██  HOW IT WORKS PAGE
# ════════════════════════════════════════════════════════════
elif page == "how":

    st.markdown("""
    <div class="page-header">
      <div class="page-header-h">ℹ️ How It Works</div>
      <div class="page-header-sub">The science and methodology behind PathAi 360's career matching algorithm</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        card_open("🔬", "How the Analysis Works", "The science behind PathAI 360")
        st.markdown("""
        <p style="font-size:13px;color:rgba(180,230,205,0.70);line-height:1.85">
        PathAI 360 uses a <strong style="color:#00d47a">personality-matching system</strong>
        to recommend tech career paths that align with
        your natural tendencies and the way you like to work and learn.
        </p>
        """, unsafe_allow_html=True)

        steps = [
            ("1", "#00d47a", "You Answer 24 Questions",
             "Each answer tells us something about how you think and work. "
             "Stronger answers (Strongly Agree / Strongly Disagree) carry more weight in your profile."),
            ("2", "#00c8e8", "We Build Your Personality Profile",
             "Your answers reveal patterns in how you think — for example, whether you prefer "
             "working with data or with people, or working alone vs. in a team."),
            ("3", "#9d6fff", "You Get Ranked Career Matches",
             "We compare your profile against 23 tech careers and rank them from best fit to least fit — "
             "giving you a clear list of where you're most likely to thrive."),
        ]
        for num, color, title_s, desc_s in steps:
            st.markdown(f"""
            <div class="how-step-card" style="margin-top:14px">
              <div class="how-step-num" style="background:linear-gradient(135deg,{color},rgba(0,212,122,0.5))">{num}</div>
              <div>
                <div class="how-step-title">{title_s}</div>
                <div class="how-step-desc">{desc_s}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        card_close()

        card_open("🚀", "What PathAI 360 Offers", "Everything built for students")
        features = [
            ("🧠", "24 personality questions",      "Clear, relatable questions for accurate results"),
            ("🗺️", "Explore tab",                   "Browse all 23 career paths with full roadmaps"),
            ("📊", "Career comparison tool",        "Compare up to 4 careers side-by-side"),
            ("⚡", "Live personality profile",      "Your profile builds in real time as you answer"),
            ("🏆", "Full career ranking",            "See all 23 careers ranked by your compatibility"),
            ("🔬", "Clear explanations",             "Understand exactly how your results are calculated"),
            ("🌐", "Saves your results",             "Results saved automatically when connected"),
        ]
        html = ""
        for icon, feat, detail in features:
            html += f"""
            <div class="domain-row">
              <span style="font-size:18px;width:26px;flex-shrink:0">{icon}</span>
              <div>
                <div style="font-size:13px;font-weight:700;color:#c8e8d8">{feat}</div>
                <div style="font-size:11px;color:rgba(140,200,170,0.45);margin-top:1px">{detail}</div>
              </div>
            </div>"""
        st.markdown(html, unsafe_allow_html=True)
        card_close()

    with c2:
        card_open("📐", "What We Measure About You", "The personality traits behind your results")
        dimensions = [
            ("🧮", "Analytical ↔ Creative",        "Logic & systems vs. imagination & design"),
            ("🤫", "Introvert ↔ Extrovert",         "Solo deep work vs. collaborative energy"),
            ("📐", "Structured ↔ Flexible",         "Planning & order vs. adaptability"),
            ("👑", "Leadership ↔ Supportive",       "Directing others vs. executing tasks"),
            ("🎲", "Risk-taking ↔ Stable",          "Embracing uncertainty vs. reliable paths"),
            ("💡", "Theoretical ↔ Practical",       "Abstract thinking vs. hands-on building"),
            ("🔍", "Detail-oriented ↔ Big-picture", "Precision focus vs. strategic vision"),
            ("🤝", "Independent ↔ Collaborative",   "Self-directed vs. team-reliant work style"),
        ]
        for icon_d, label, desc in dimensions:
            st.markdown(f"""
            <div class="domain-row">
              <span style="font-size:18px;width:24px;flex-shrink:0">{icon_d}</span>
              <div>
                <div style="font-size:13px;font-weight:700;color:#c8e8d8">{label}</div>
                <div style="font-size:11px;color:rgba(140,200,170,0.40);margin-top:2px">{desc}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        card_close()

# ════════════════════════════════════════════════════════════
#  ██  ARCHITECTURE PAGE
# ════════════════════════════════════════════════════════════
elif page == "arch":

    st.markdown("""
    <div class="page-header">
      <div class="page-header-h">🏗️ System Architecture</div>
      <div class="page-header-sub">Full-stack technical design — ML pipeline, REST API, and database schema</div>
      <div class="page-header-chips">
        <span class="chip chip-green">FastAPI · Python 3.11</span>
        <span class="chip chip-blue">MongoDB 7 · Motor</span>
        <span class="chip chip-purple">scikit-learn · Random Forest</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tier Overview ──
    st.markdown("""
    <div class="card">
      <div class="card-header">
        <div class="card-icon">🏛️</div>
        <div>
          <div class="card-title">Three-Tier Decoupled Architecture</div>
          <div class="card-subtitle">Each tier communicates over HTTP/JSON — independently testable and replaceable</div>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:4px">
        <div style="background:rgba(0,212,122,0.05);border:1px solid rgba(0,212,122,0.18);border-radius:14px;padding:18px">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#00d47a;margin-bottom:8px">Tier 1 — Frontend</div>
          <div style="font-size:12px;color:rgba(180,230,205,0.65);line-height:1.75">React 18 SPA — renders the assessment form, displays Recharts visualizations, and streams downloadable PDF reports. Hosted as a static build via Vercel / Netlify.</div>
          <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">
            <span class="chip chip-green" style="font-size:9px">React 18</span>
            <span class="chip chip-green" style="font-size:9px">Recharts</span>
            <span class="chip chip-green" style="font-size:9px">Axios</span>
          </div>
        </div>
        <div style="background:rgba(0,200,232,0.05);border:1px solid rgba(0,200,232,0.18);border-radius:14px;padding:18px">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#00c8e8;margin-bottom:8px">Tier 2 — Backend API</div>
          <div style="font-size:12px;color:rgba(180,230,205,0.65);line-height:1.75">FastAPI on port 8000 handles all business logic — MBTI scoring, career mapping, ML inference via joblib, and PDF generation with WeasyPrint. JWT-protected routes.</div>
          <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">
            <span class="chip chip-blue" style="font-size:9px">FastAPI</span>
            <span class="chip chip-blue" style="font-size:9px">Uvicorn</span>
            <span class="chip chip-blue" style="font-size:9px">Pydantic</span>
          </div>
        </div>
        <div style="background:rgba(157,111,255,0.05);border:1px solid rgba(157,111,255,0.18);border-radius:14px;padding:18px">
          <div style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#9d6fff;margin-bottom:8px">Tier 3 — Database</div>
          <div style="font-size:12px;color:rgba(180,230,205,0.65);line-height:1.75">MongoDB 7 Atlas — schema-flexible NoSQL stores users, raw answers, computed MBTI results, and ML prediction logs. Motor (async driver) for non-blocking I/O.</div>
          <div style="margin-top:10px;display:flex;gap:6px;flex-wrap:wrap">
            <span class="chip chip-purple" style="font-size:9px">MongoDB 7</span>
            <span class="chip chip-purple" style="font-size:9px">Motor</span>
            <span class="chip chip-purple" style="font-size:9px">Atlas</span>
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    a1, a2 = st.columns(2, gap="large")

    with a1:
        # ML Pipeline
        card_open("🤖", "ML Pipeline — Two-Model Approach", "Trained offline · served via joblib at inference time")
        ml_steps = [
            ("📐", "Feature Engineering", "40 raw answers → 55-dim vector: 8 MBTI sub-scores, 5 domain tallies, response variance, completion time."),
            ("🌲", "Model 1 — Random Forest Classifier", "Predicts MBTI type (16 classes) with n_estimators=200, max_depth=12, class_weight='balanced' for rare types."),
            ("🔵", "Model 2 — K-Means Clustering", "Groups students into 5 learning archetypes: Analytical Thinker, Creative Visionary, Social Connector, Practical Builder, Balanced Explorer."),
            ("⚡", "Inference Pipeline", "Models load once at startup via joblib. build_feature_vector() → scaler.transform() → clf.predict() + kmeans.predict()."),
        ]
        for icon_ml, t_ml, d_ml in ml_steps:
            st.markdown(f"""
            <div class="how-step-card">
              <div style="font-size:22px;width:36px;flex-shrink:0;text-align:center">{icon_ml}</div>
              <div>
                <div class="how-step-title">{t_ml}</div>
                <div class="how-step-desc">{d_ml}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        card_close()

        # REST API Endpoints
        card_open("🌐", "REST API Endpoints", "/api/v1 prefix · JWT Bearer auth on protected routes")
        endpoints = [
            ("POST", "/auth/register",   "None",  "Create student account (name, email, password)"),
            ("POST", "/auth/login",      "None",  "Returns JWT access_token on valid credentials"),
            ("GET",  "/test/questions",  "JWT",   "Fetch all 40 test questions (randomized order)"),
            ("POST", "/test/submit",     "JWT",   "Submit answers; triggers full scoring pipeline"),
            ("GET",  "/results/{id}",   "JWT",   "Retrieve stored results for a user"),
            ("GET",  "/results/report",  "JWT",   "Stream PDF report for authenticated user"),
            ("GET",  "/admin/stats",     "Admin", "Aggregate stats: top types, avg STEM score"),
        ]
        method_colors = {"POST": "#00d47a", "GET": "#00c8e8"}
        html = ""
        for method, endpoint, auth, desc_ep in endpoints:
            mc = method_colors.get(method, "#9d6fff")
            html += f"""
            <div class="domain-row" style="align-items:flex-start;padding:10px 12px">
              <span style="font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:800;
                           color:{mc};background:rgba(0,0,0,0.25);border:1px solid {mc}44;
                           border-radius:6px;padding:2px 6px;flex-shrink:0;margin-top:1px">{method}</span>
              <div style="flex:1">
                <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:600;color:#c8e8d8">{endpoint}</div>
                <div style="font-size:11px;color:rgba(140,200,170,0.45);margin-top:2px">{desc_ep}</div>
              </div>
              <span style="font-size:9px;color:rgba(157,111,255,0.55);font-family:'JetBrains Mono',monospace;flex-shrink:0">{auth}</span>
            </div>"""
        st.markdown(html, unsafe_allow_html=True)
        card_close()

    with a2:
        # MongoDB Collections
        card_open("🗄️", "MongoDB Collections", "4 collections · UUID string _id · Motor async driver")
        collections_info = [
            ("users",   "#00d47a", "name, email, password_hash (bcrypt), grade, role, created_at", "Index: email (unique)"),
            ("answers", "#00c8e8", "user_id, answers {q01..q40}, time_secs, submitted_at", "Index: user_id"),
            ("results", "#9d6fff", "user_id, personality_type, sub_scores, ml_predictions, recommendations", "Index: user_id, personality_type"),
        ]
        for coll, color, fields, idx in collections_info:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.2);border:1px solid {color}22;border-radius:12px;padding:14px;margin-bottom:10px">
              <div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:{color};margin-bottom:6px">db.{coll}</div>
              <div style="font-size:11px;color:rgba(180,230,205,0.6);line-height:1.6;margin-bottom:6px">{fields}</div>
              <div style="font-size:10px;color:rgba(140,200,170,0.35);font-family:'JetBrains Mono',monospace">{idx}</div>
            </div>
            """, unsafe_allow_html=True)
        card_close()

        # Auth
        card_open("🔐", "Authentication — JWT / bcrypt", "HS256 · 24 hr token expiry · cost factor 12")
        auth_items = [
            ("🔑", "JWT Signing",       "HS256 algorithm · tokens expire in 24 hours · signed with JWT_SECRET env var"),
            ("🔒", "Password Hashing",  "bcrypt with cost factor 12 via passlib.CryptContext — stored as hash, never plaintext"),
            ("🛡️", "Protected Routes",  "get_current_user() dependency decodes Bearer token on every protected FastAPI route"),
            ("💾", "Token Storage",     "React stores token in window.__pathai_token (in-memory) to minimize XSS risk vs localStorage"),
        ]
        for icon_a, title_a, desc_a in auth_items:
            st.markdown(f"""
            <div class="domain-row">
              <span style="font-size:18px;width:24px;flex-shrink:0">{icon_a}</span>
              <div>
                <div style="font-size:13px;font-weight:700;color:#c8e8d8">{title_a}</div>
                <div style="font-size:11px;color:rgba(140,200,170,0.40);margin-top:2px">{desc_a}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        card_close()

        # Future Roadmap
        card_open("🚀", "Technical Roadmap", "Planned phases from the Architecture v2.0 spec")
        phases = [
            ("Phase 2", "#00d47a", "Intelligence", "Fine-tuned DistilBERT for open-text questions · MLflow monthly retraining · confidence intervals per type"),
            ("Phase 3", "#00c8e8", "Scale",        "WebSocket peer comparison dashboard · Teacher admin portal · SMS via Twilio (Pakistan numbers)"),
            ("Phase 4", "#9d6fff", "Integration",  "Pakistan HEC university API feed · WhatsApp Business bot · IELTS readiness prediction"),
        ]
        for phase, color, name, desc_ph in phases:
            st.markdown(f"""
            <div style="background:rgba(0,0,0,0.15);border-left:3px solid {color};border-radius:0 12px 12px 0;padding:12px 14px;margin-bottom:10px">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:5px">
                <span style="font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;
                             color:{color};background:{color}18;border:1px solid {color}33;
                             border-radius:6px;padding:2px 8px">{phase}</span>
                <span style="font-family:'Syne',sans-serif;font-size:13px;font-weight:800;color:#d8f0e8">{name}</span>
              </div>
              <div style="font-size:11px;color:rgba(180,230,205,0.55);line-height:1.65">{desc_ph}</div>
            </div>
            """, unsafe_allow_html=True)
        card_close()