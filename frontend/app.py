"""
app.py  –  StockPulse · Enhanced Streamlit Dashboard v3
Premium dark-theme AI Sentiment × Price Intelligence UI
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config (MUST be first) ───────────────────────────────────────────────
st.set_page_config(
    page_title            = "StockPulse · AI Dashboard",
    page_icon             = "📈",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

# ── Premium Dark Theme CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&display=swap');

:root {
    --bg-base       : #080c12;
    --bg-surface    : #0e1420;
    --bg-elevated   : #131b28;
    --bg-card       : #111827;
    --border-subtle : rgba(255,255,255,0.06);
    --border-active : rgba(88,166,255,0.4);
    --text-primary  : #f0f6ff;
    --text-secondary: #7d8fa8;
    --text-muted    : #4a5568;
    --accent-blue   : #4a90e8;
    --accent-green  : #22c55e;
    --accent-red    : #ef4444;
    --accent-amber  : #f59e0b;
    --accent-purple : #a78bfa;
    --glow-blue     : rgba(74,144,232,0.15);
    --glow-green    : rgba(34,197,94,0.12);
    --glow-red      : rgba(239,68,68,0.12);
    --radius-sm     : 8px;
    --radius-md     : 12px;
    --radius-lg     : 18px;
}

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1a 0%, #0d1322 100%) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] * { font-family: 'DM Sans', sans-serif !important; }

[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: var(--accent-blue) !important;
    box-shadow: 0 0 0 3px var(--glow-blue) !important;
}

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background    : var(--bg-card) !important;
    border        : 1px solid var(--border-subtle) !important;
    border-radius : var(--radius-md) !important;
    padding       : 20px 22px !important;
    transition    : transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    position      : relative !important;
    overflow      : hidden !important;
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
    opacity: 0;
    transition: opacity 0.2s;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px) !important;
    border-color: var(--border-active) !important;
    box-shadow: 0 8px 32px var(--glow-blue) !important;
}
[data-testid="metric-container"]:hover::before { opacity: 1; }

[data-testid="stMetricLabel"] {
    color         : var(--text-secondary) !important;
    font-size     : 0.7rem !important;
    font-weight   : 600 !important;
    font-family   : 'Space Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stMetricValue"] {
    color      : var(--text-primary) !important;
    font-size  : 1.8rem !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] {
    font-size  : 0.78rem !important;
    font-family: 'Space Mono', monospace !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background-color: var(--bg-elevated) !important;
    border          : 1px solid var(--border-subtle) !important;
    border-radius   : var(--radius-sm) !important;
    color           : var(--text-primary) !important;
    transition      : border-color 0.2s !important;
}
[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--border-active) !important;
}

/* ── Buttons ── */
.stButton > button {
    background    : linear-gradient(135deg, #1d4ed8, #4a90e8) !important;
    color         : #fff !important;
    border        : none !important;
    border-radius : var(--radius-sm) !important;
    font-family   : 'DM Sans', sans-serif !important;
    font-weight   : 600 !important;
    font-size     : 0.85rem !important;
    padding       : 8px 20px !important;
    letter-spacing: 0.02em !important;
    transition    : all 0.2s ease !important;
    box-shadow    : 0 2px 12px rgba(74,144,232,0.3) !important;
}
.stButton > button:hover {
    transform  : translateY(-1px) !important;
    box-shadow : 0 6px 20px rgba(74,144,232,0.45) !important;
    background : linear-gradient(135deg, #2563eb, #60a5fa) !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] { border-bottom: 1px solid var(--border-subtle); }
[data-testid="stTabs"] button {
    color        : var(--text-secondary) !important;
    font-family  : 'DM Sans', sans-serif !important;
    font-weight  : 500 !important;
    font-size    : 0.875rem !important;
    border-bottom: 2px solid transparent !important;
    padding      : 10px 16px !important;
    border-radius: 0 !important;
    transition   : color 0.2s !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color        : var(--accent-blue) !important;
    border-bottom: 2px solid var(--accent-blue) !important;
}
[data-testid="stTabs"] button:hover { color: var(--text-primary) !important; }

/* ── DataFrame ── */
[data-testid="stDataFrame"] {
    background-color: var(--bg-elevated) !important;
    border-radius   : var(--radius-md) !important;
    border          : 1px solid var(--border-subtle) !important;
    overflow        : hidden !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background   : var(--bg-card) !important;
    border       : 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
}

hr {
    border    : none !important;
    height    : 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-subtle) 20%,
                var(--border-subtle) 80%, transparent) !important;
    margin    : 2rem 0 !important;
}

[data-testid="stCheckbox"] span {
    color      : var(--text-secondary) !important;
    font-size  : 0.85rem !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stRadio"] label {
    color    : var(--text-secondary) !important;
    font-size: 0.85rem !important;
}
[data-testid="stSpinner"]  { color: var(--accent-blue) !important; }
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border       : 1px solid var(--border-subtle) !important;
    background   : var(--bg-elevated) !important;
}
[data-testid="stCaptionContainer"] {
    color      : var(--text-muted) !important;
    font-family: 'Space Mono', monospace !important;
    font-size  : 0.72rem !important;
}

/* ── Custom components ── */
.pulse-header {
    font-family   : 'Syne', sans-serif;
    font-size     : 2rem;
    font-weight   : 800;
    color         : var(--text-primary);
    letter-spacing: -0.02em;
    line-height   : 1.1;
    margin-bottom : 2px;
}
.pulse-header span {
    background             : linear-gradient(135deg, #4a90e8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip        : text;
}

.sub-caption {
    font-family   : 'Space Mono', monospace;
    font-size     : 0.72rem;
    color         : var(--text-muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.section-label {
    font-family   : 'Space Mono', monospace;
    font-size     : 0.68rem;
    font-weight   : 700;
    color         : var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom : 14px;
    display       : flex;
    align-items   : center;
    gap           : 8px;
}
.section-label::after {
    content   : '';
    flex      : 1;
    height    : 1px;
    background: var(--border-subtle);
}

/* ── Score card ── */
.score-card {
    background   : var(--bg-card);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding      : 28px 24px;
    text-align   : center;
    position     : relative;
    overflow     : hidden;
    transition   : transform 0.3s ease, box-shadow 0.3s ease;
    height       : 100%;
}
.score-card::before {
    content   : '';
    position  : absolute;
    top: -40px; left: -40px; right: -40px;
    height    : 120px;
    filter    : blur(40px);
    opacity   : 0.25;
    transition: opacity 0.3s;
}
.score-card:hover { transform: translateY(-3px); }
.score-card:hover::before { opacity: 0.4; }
.score-card.bullish::before { background: var(--accent-green); }
.score-card.bearish::before { background: var(--accent-red); }
.score-card.neutral::before { background: var(--accent-amber); }

.score-label {
    font-family   : 'Space Mono', monospace;
    font-size     : 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color         : var(--text-muted);
    margin-bottom : 12px;
}
.score-value {
    font-family: 'Syne', sans-serif;
    font-size  : 3.2rem;
    font-weight: 800;
    line-height: 1;
    margin     : 8px 0;
}
.score-tag {
    font-family   : 'DM Sans', sans-serif;
    font-size     : 0.82rem;
    font-weight   : 600;
    letter-spacing: 0.04em;
    margin-top    : 10px;
}
.score-meta {
    font-family: 'Space Mono', monospace;
    font-size  : 0.65rem;
    color      : var(--text-muted);
    margin-top : 14px;
    padding-top: 14px;
    border-top : 1px solid var(--border-subtle);
}

/* ── Signal verdict card ── */
.verdict-card {
    background   : var(--bg-card);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding      : 24px;
    position     : relative;
    overflow     : hidden;
}
.verdict-card.buy  { border-color: rgba(34,197,94,0.3); }
.verdict-card.sell { border-color: rgba(239,68,68,0.3); }
.verdict-card.hold { border-color: rgba(245,158,11,0.3); }

/* ── News feed ── */
.news-item {
    background   : var(--bg-elevated);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding      : 14px 16px;
    margin-bottom: 10px;
    transition   : border-color 0.2s, transform 0.2s;
    position     : relative;
    overflow     : hidden;
}
.news-item::before {
    content      : '';
    position     : absolute;
    left: 0; top: 0; bottom: 0;
    width        : 3px;
    border-radius: 0 2px 2px 0;
}
.news-item.positive::before { background: var(--accent-green); }
.news-item.negative::before { background: var(--accent-red); }
.news-item.neutral::before  { background: var(--accent-amber); }
.news-item:hover {
    border-color: var(--border-active);
    transform   : translateX(2px);
}
.news-headline {
    font-family: 'DM Sans', sans-serif;
    font-size  : 0.9rem;
    font-weight: 500;
    color      : var(--text-primary);
    line-height: 1.4;
    margin-top : 8px;
}

/* ── Reason item ── */
.reason-item {
    background   : var(--bg-elevated);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding      : 10px 14px;
    margin-bottom: 8px;
    font-family  : 'Space Mono', monospace;
    font-size    : 0.72rem;
    color        : var(--text-secondary);
    display      : flex;
    align-items  : center;
    gap          : 10px;
}

/* ── Polymarket market row ── */
.signal-summary {
    background   : linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding      : 20px 22px;
    margin-bottom: 16px;
}
.signal-summary-title {
    font-family  : 'Syne', sans-serif;
    font-size    : 1.25rem;
    font-weight  : 700;
    color        : var(--text-primary);
    line-height  : 1.2;
    margin-bottom: 8px;
}
.signal-summary-copy {
    font-family: 'DM Sans', sans-serif;
    font-size  : 0.95rem;
    line-height: 1.65;
    color      : var(--text-secondary);
}
.signal-summary-copy strong {
    color      : var(--text-primary);
    font-weight: 600;
}
.signal-grid {
    display              : grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap                  : 12px;
    margin-bottom        : 18px;
}
.signal-driver {
    background   : var(--bg-elevated);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding      : 14px 16px;
}
.signal-driver-label {
    font-family   : 'Space Mono', monospace;
    font-size     : 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color         : var(--text-muted);
    margin-bottom : 10px;
}
.signal-driver-value {
    font-family  : 'Syne', sans-serif;
    font-size    : 1.15rem;
    font-weight  : 700;
    color        : var(--text-primary);
    margin-bottom: 4px;
}
.signal-driver-meta {
    font-family: 'DM Sans', sans-serif;
    font-size  : 0.8rem;
    color      : var(--text-secondary);
    line-height: 1.45;
}
.signal-evidence {
    display      : flex;
    align-items  : flex-start;
    gap          : 10px;
    padding      : 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.signal-evidence:last-child {
    border-bottom: none;
}
.signal-evidence-key {
    min-width     : 108px;
    font-family   : 'Space Mono', monospace;
    font-size     : 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color         : var(--text-muted);
    padding-top   : 2px;
}
.signal-evidence-copy {
    font-family: 'DM Sans', sans-serif;
    font-size  : 0.9rem;
    line-height: 1.55;
    color      : var(--text-secondary);
}
@media (max-width: 900px) {
    .signal-grid {
        grid-template-columns: 1fr;
    }
    .signal-evidence {
        flex-direction: column;
        gap: 4px;
    }
    .signal-evidence-key {
        min-width: auto;
    }
}

.poly-row {
    background   : var(--bg-elevated);
    border       : 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding      : 12px 16px;
    margin-bottom: 8px;
    display      : flex;
    align-items  : center;
    gap          : 14px;
    transition   : border-color 0.2s, transform 0.2s;
}
.poly-row:hover {
    border-color: var(--border-active);
    transform   : translateX(2px);
}
.poly-prob {
    font-family: 'Syne', sans-serif;
    font-size  : 1.4rem;
    font-weight: 800;
    min-width  : 60px;
    text-align : right;
}
.poly-question {
    font-family: 'DM Sans', sans-serif;
    font-size  : 0.85rem;
    color      : var(--text-primary);
    flex       : 1;
    line-height: 1.35;
}
.poly-vol {
    font-family  : 'Space Mono', monospace;
    font-size    : 0.62rem;
    color        : var(--text-muted);
    text-align   : right;
    min-width    : 72px;
}

/* ── Pills ── */
.pill {
    display      : inline-flex;
    align-items  : center;
    gap          : 5px;
    padding      : 3px 10px;
    border-radius: 20px;
    font-family  : 'Space Mono', monospace;
    font-size    : 0.65rem;
    font-weight  : 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.pill-pos  { background: rgba(34,197,94,0.12);  color: #22c55e; border: 1px solid rgba(34,197,94,0.25); }
.pill-neg  { background: rgba(239,68,68,0.12);  color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }
.pill-neu  { background: rgba(245,158,11,0.12); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
.pill-info { background: rgba(74,144,232,0.12); color: #4a90e8; border: 1px solid rgba(74,144,232,0.25); }
.pill-pur  { background: rgba(167,139,250,0.12);color: #a78bfa; border: 1px solid rgba(167,139,250,0.25); }

/* ── Sidebar brand ── */
.sidebar-brand {
    font-family   : 'Syne', sans-serif;
    font-size     : 1.35rem;
    font-weight   : 800;
    letter-spacing: -0.01em;
    margin-bottom : 4px;
}
.sidebar-brand span {
    background             : linear-gradient(135deg, #4a90e8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip        : text;
}
.sb-label {
    font-family   : 'Space Mono', monospace;
    font-size     : 0.62rem;
    font-weight   : 700;
    color         : var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin        : 16px 0 8px;
}
.chart-title {
    font-family  : 'Syne', sans-serif;
    font-size    : 1.25rem;
    font-weight  : 700;
    color        : var(--text-primary);
    margin-bottom: 4px;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4a5568; }

[data-testid="stSidebarNav"] { display: none; }
.block-container { padding-top: 4.5rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

if "analysis_config" not in st.session_state:
    st.session_state["analysis_config"] = None

POPULAR_TICKERS = {
    "AAPL" : "Apple Inc.",
    "GOOG" : "Alphabet (Google)",
    "GOOGL": "Alphabet Class A",
    "MSFT" : "Microsoft",
    "AMZN" : "Amazon",
    "TSLA" : "Tesla",
    "META" : "Meta Platforms",
    "NVDA" : "NVIDIA",
    "AMD"  : "AMD",
    "NFLX" : "Netflix",
    "SPY"  : "S&P 500 ETF",
    "QQQ"  : "NASDAQ-100 ETF",
    "BRK-B": "Berkshire Hathaway",
    "JPM"  : "JPMorgan Chase",
    "BAC"  : "Bank of America",
    "GS"   : "Goldman Sachs",
    "V"    : "Visa",
    "MA"   : "Mastercard",
    "DIS"  : "Walt Disney",
    "BABA" : "Alibaba",
    "TSM"  : "TSMC",
    "INTC" : "Intel",
    "CRM"  : "Salesforce",
    "UBER" : "Uber",
    "COIN" : "Coinbase",
    "PLTR" : "Palantir",
    "SQ"   : "Block (Square)",
    "SHOP" : "Shopify",
    "NET"  : "Cloudflare",
    "SNOW" : "Snowflake",
    "BTC"  : "Bitcoin (Crypto)",
    "ETH"  : "Ethereum (Crypto)",
}

PERIOD_OPTIONS = {
    "1 Month" : 30,
    "3 Months": 90,
    "6 Months": 180,
    "1 Year"  : 365,
}

CHART_TYPES  = ["Candle", "Area", "Line"]
INTERVAL_MAP = {"1d": "Daily", "1h": "Hourly"}


# ── API helpers ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_sentiment(ticker: str) -> dict:
    try:
        r = requests.get(
            f"{API_BASE}/api/sentiment",
            params={"ticker": ticker},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=60)
def get_kpis(ticker: str) -> dict:
    try:
        r = requests.get(
            f"{API_BASE}/api/kpis",
            params={"ticker": ticker},
            timeout=15,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=60)
def get_price_history(ticker: str, period_days: int, interval: str) -> list[dict]:
    try:
        r = requests.get(
            f"{API_BASE}/api/price-history",
            params={
                "ticker"      : ticker,
                "period_days" : period_days,
                "interval"    : interval,
                "indicators"  : True,
            },
            timeout=20,
        )
        r.raise_for_status()
        return r.json().get("records", [])
    except Exception as e:
        st.error(f"❌ Price history error: {e}")
        return []


@st.cache_data(ttl=300)
def get_polymarket(ticker: str) -> dict:
    """
    FIX: Always pass ticker so we get sentiment for the correct stock,
    not the default SPY.
    """
    try:
        r = requests.get(
            f"{API_BASE}/api/polymarket",
            params={"ticker": ticker},
            timeout=20,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@st.cache_data(ttl=120)
def get_signal(ticker: str) -> dict:
    """NEW: Fetch combined BUY/SELL/HOLD signal from /api/signal."""
    try:
        r = requests.get(
            f"{API_BASE}/api/signal",
            params={"ticker": ticker},
            timeout=35,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='sidebar-brand'>Stock<span>Pulse</span></div>
    <div style='font-size:0.7rem;color:#4a5568;font-family:Space Mono,monospace;
                letter-spacing:0.08em;margin-bottom:20px;'>
        AI · PRICE · SENTIMENT
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sb-label'>Search Stock</div>", unsafe_allow_html=True)

    search_input = st.text_input(
        "ticker",
        value="",
        placeholder="e.g. AAPL, Tesla, NVDA…",
        label_visibility="collapsed",
    ).strip().upper()

    if search_input:
        matches = {
            k: v for k, v in POPULAR_TICKERS.items()
            if search_input in k.upper() or search_input in v.upper()
        }
    else:
        matches = POPULAR_TICKERS

    options_list = [f"{k} – {v}" for k, v in matches.items()]
    if not options_list:
        options_list = [f"{search_input} – Custom"]

    selected_option = st.selectbox(
        "Select ticker",
        options_list,
        label_visibility="collapsed",
    )

    selected_ticker = selected_option.split(" – ")[0].strip()
    selected_company = selected_option.split(" – ")[1].strip() if " – " in selected_option else ""

    st.markdown("<div class='sb-label' style='margin-top:20px;'>Chart Settings</div>",
                unsafe_allow_html=True)

    period_label = st.selectbox("Time Period", list(PERIOD_OPTIONS.keys()), index=2)
    period_days  = PERIOD_OPTIONS[period_label]
    interval     = st.selectbox(
        "Bar Interval", list(INTERVAL_MAP.keys()),
        format_func=lambda x: INTERVAL_MAP[x],
    )
    chart_type = st.radio("Chart Type", CHART_TYPES, horizontal=True)

    st.markdown("<div class='sb-label' style='margin-top:20px;'>Overlays</div>",
                unsafe_allow_html=True)
    show_bb    = st.checkbox("Bollinger Bands", value=True)
    show_sma7  = st.checkbox("SMA 7",           value=True)
    show_sma21 = st.checkbox("SMA 21",          value=True)
    show_sma50 = st.checkbox("SMA 50",          value=True)
    show_vol   = st.checkbox("Volume",          value=True)

    st.markdown("<br>", unsafe_allow_html=True)
    run_analysis = st.button("Analyze Stock", use_container_width=True)
    refresh_data = st.button("⟳  Refresh Data", use_container_width=True)

    pending_config = {
        "ticker": selected_ticker,
        "company": selected_company,
        "period_label": period_label,
        "period_days": period_days,
        "interval": interval,
        "chart_type": chart_type,
        "show_bb": show_bb,
        "show_sma7": show_sma7,
        "show_sma21": show_sma21,
        "show_sma50": show_sma50,
        "show_vol": show_vol,
    }

    if run_analysis:
        st.session_state["analysis_config"] = pending_config
        st.cache_data.clear()
        st.rerun()

    if refresh_data and st.session_state.get("analysis_config"):
        st.session_state["analysis_config"] = pending_config
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style='margin-top:24px;padding:12px;background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.04);border-radius:8px;'>
        <div style='font-family:Space Mono,monospace;font-size:0.6rem;
                    color:#4a5568;text-transform:uppercase;letter-spacing:0.1em;'>
            Data Sources
        </div>
        <div style='font-family:DM Sans,sans-serif;font-size:0.75rem;
                    color:#7d8fa8;margin-top:6px;line-height:1.6;'>
            Yahoo Finance · Polymarket<br>FinBERT NLP · Gemini AI
        </div>
    </div>
    """, unsafe_allow_html=True)

analysis_config = st.session_state.get("analysis_config")

if not analysis_config:
    st.markdown("""
    <div style='max-width:760px;margin:80px auto 0;padding:28px 30px;
                background:rgba(255,255,255,0.02);
                border:1px solid rgba(255,255,255,0.06);
                border-radius:18px;'>
        <div style='font-family:Space Mono,monospace;font-size:0.72rem;
                    color:#4a5568;text-transform:uppercase;letter-spacing:0.14em;'>
            Ready When You Are
        </div>
        <div style='font-family:Syne,sans-serif;font-size:2.2rem;font-weight:800;
                    color:#f0f6ff;line-height:1.1;margin-top:12px;'>
            Configure the stock and analysis settings first
        </div>
        <div style='font-family:DM Sans,sans-serif;font-size:0.98rem;color:#7d8fa8;
                    line-height:1.7;margin-top:14px;'>
            Choose the ticker, timeframe, chart mode, and overlays in the sidebar.
            Then click <strong style='color:#f0f6ff;'>Analyze Stock</strong> to load the dashboard.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

ticker = analysis_config["ticker"]
company = analysis_config["company"]
period_label = analysis_config["period_label"]
period_days = analysis_config["period_days"]
interval = analysis_config["interval"]
# Visual controls should respond immediately without requiring another
# "Analyze Stock" click. Data-selection controls still follow the last
# committed analysis config until the user refreshes or re-runs.
chart_type = pending_config["chart_type"]
show_bb = pending_config["show_bb"]
show_sma7 = pending_config["show_sma7"]
show_sma21 = pending_config["show_sma21"]
show_sma50 = pending_config["show_sma50"]
show_vol = pending_config["show_vol"]


# ── Page Header ───────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown(
        f"<div class='pulse-header'>{ticker} <span>·</span> {company}</div>"
        f"<div class='sub-caption'>{period_label} · {INTERVAL_MAP[interval]}"
        f" · AI Sentiment &amp; Price Intelligence</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# FETCH ALL DATA (single pass so spinner is accurate)
# ════════════════════════════════════════════════════════════════════════════
with st.spinner(f"Loading {ticker} data…"):
    kpi_data   = get_kpis(ticker)
    poly_data  = get_polymarket(ticker)      # FIX: passes ticker correctly
    sig_data   = get_signal(ticker)          # NEW


# ════════════════════════════════════════════════════════════════════════════
# KPI CARDS  ── row 1
# ════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-label'>Live Market Data</div>", unsafe_allow_html=True)

k1, k2, k3, k4, k5, k6 = st.columns(6)

price      = kpi_data.get("price", 0) or 0
change_pct = kpi_data.get("change_pct", 0) or 0
rsi_val    = kpi_data.get("rsi")
rsi_sig    = kpi_data.get("rsi_signal", "—")
macd_val   = kpi_data.get("macd")
poly_score = kpi_data.get("polymarket_score")
poly_label_kpi = kpi_data.get("polymarket_label", "—")

# Final signal from /api/signal (richer than the blended KPI one)
final_signal = sig_data.get("final_signal", "HOLD") if not sig_data.get("error") else "—"
sig_conf     = sig_data.get("confidence", 0.0)

with k1:
    direction = "▲" if change_pct >= 0 else "▼"
    st.metric(
        label = f"Price · {ticker}",
        value = f"${price:,.2f}" if price else "—",
        delta = f"{direction} {abs(change_pct):.2f}% today",
    )

with k2:
    st.metric(
        label       = "RSI · 14",
        value       = f"{rsi_val:.1f}" if rsi_val else "—",
        delta       = rsi_sig,
        delta_color = "off",
    )

with k3:
    macd_dir   = "↑ Bullish" if macd_val and macd_val > 0 else "↓ Bearish"
    macd_color = "normal" if macd_val and macd_val > 0 else "inverse"
    st.metric(
        label       = "MACD",
        value       = f"{macd_val:.4f}" if macd_val is not None else "—",
        delta       = macd_dir,
        delta_color = macd_color,
    )

with k4:
    # FIX: polymarket_score is now for the selected ticker (not always SPY)
    score_valid = poly_score is not None
    st.metric(
        label       = f"Polymarket · {ticker}",
        value       = f"{poly_score:.0%}" if score_valid else "—",
        delta       = poly_label_kpi if score_valid else "No data",
        delta_color = "off",
    )

with k5:
    bb_upper = kpi_data.get("bb_upper")
    bb_lower = kpi_data.get("bb_lower")
    if bb_upper and bb_lower and price:
        bb_pct = (price - bb_lower) / (bb_upper - bb_lower) * 100
        bb_tag = "Near Upper" if bb_pct > 75 else ("Near Lower" if bb_pct < 25 else "Mid Band")
        st.metric(
            label       = "BB Position",
            value       = f"{bb_pct:.0f}%",
            delta       = bb_tag,
            delta_color = "off",
        )
    else:
        st.metric(label="BB Position", value="—", delta="No data", delta_color="off")

with k6:
    if final_signal == "BUY":
        sig_delta_color = "normal"
    elif final_signal == "SELL":
        sig_delta_color = "inverse"
    else:
        sig_delta_color = "off"

    st.metric(
        label       = "AI Signal",
        value       = final_signal,
        delta       = f"Confidence: {sig_conf:.0%}",
        delta_color = sig_delta_color,
    )

st.markdown("<hr>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TABS:  Chart · Polymarket · News Analysis · Public Opinion · AI Signal
# ════════════════════════════════════════════════════════════════════════════
tab_chart, tab_poly, tab_news, tab_public, tab_signal = st.tabs([
    "📈  Price Chart",
    "🎲  Polymarket",
    "📰  News Analysis",
    "👥  Public Opinion",
    "🤖  AI Signal",
])


# ────────────────────────────────────────────────────────────────────────────
# TAB 1 — PRICE CHART
# ────────────────────────────────────────────────────────────────────────────
with tab_chart:
    st.markdown(
        f"<div class='chart-title'>{ticker} — {chart_type} View · {period_label}</div>",
        unsafe_allow_html=True,
    )

    records = get_price_history(ticker, period_days, interval)

    if not records:
        st.warning("⚠️ No price data. Check the backend is running at localhost:8000")
    else:
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])

        rows   = [0.52, 0.16, 0.18, 0.14] if show_vol else [0.58, 0.22, 0.20]
        n_rows = len(rows)
        vol_row  = 2 if show_vol else None
        macd_row = 3 if show_vol else 2
        rsi_row  = 4 if show_vol else 3

        subplot_titles = [f"{ticker} Price"]
        if show_vol:
            subplot_titles.append("Volume")
        subplot_titles += ["MACD", "RSI (14)"]

        fig = make_subplots(
            rows             = n_rows,
            cols             = 1,
            shared_xaxes     = True,
            row_heights      = rows,
            vertical_spacing = 0.025,
            subplot_titles   = subplot_titles,
        )

        # ── Price trace ───────────────────────────────────────────────────
        if chart_type == "Candle":
            fig.add_trace(go.Candlestick(
                x          = df["date"],
                open       = df["open"],
                high       = df["high"],
                low        = df["low"],
                close      = df["close"],
                name       = "OHLC",
                increasing = dict(line=dict(color="#22c55e", width=1.2),
                                  fillcolor="rgba(34,197,94,0.25)"),
                decreasing = dict(line=dict(color="#ef4444", width=1.2),
                                  fillcolor="rgba(239,68,68,0.25)"),
            ), row=1, col=1)
        elif chart_type == "Area":
            fig.add_trace(go.Scatter(
                x         = df["date"],
                y         = df["close"],
                name      = "Price",
                mode      = "lines",
                line      = dict(color="#4a90e8", width=2.5),
                fill      = "tozeroy",
                fillcolor = "rgba(74,144,232,0.07)",
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x    = df["date"],
                y    = df["close"],
                name = "Price",
                mode = "lines",
                line = dict(color="#4a90e8", width=2.5),
            ), row=1, col=1)

        # ── Bollinger Bands ───────────────────────────────────────────────
        if show_bb and "bb_upper" in df.columns:
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["bb_upper"],
                name="BB Upper",
                line=dict(color="rgba(167,139,250,0.45)", dash="dot", width=1),
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["bb_lower"],
                name="BB Lower",
                line=dict(color="rgba(167,139,250,0.45)", dash="dot", width=1),
                fill="tonexty",
                fillcolor="rgba(167,139,250,0.05)",
            ), row=1, col=1)
            if "bb_mid" in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["bb_mid"],
                    name="BB Mid",
                    line=dict(color="rgba(167,139,250,0.3)", width=1),
                ), row=1, col=1)

        # ── SMAs ──────────────────────────────────────────────────────────
        for col_name, show, color, label in [
            ("sma_7",  show_sma7,  "#f59e0b", "SMA 7"),
            ("sma_21", show_sma21, "#fb923c", "SMA 21"),
            ("sma_50", show_sma50, "#a78bfa", "SMA 50"),
        ]:
            if show and col_name in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df[col_name],
                    name=label,
                    line=dict(color=color, width=1.5),
                ), row=1, col=1)

        # ── Volume ────────────────────────────────────────────────────────
        if show_vol and "volume" in df.columns:
            vol_colors = [
                "rgba(34,197,94,0.55)" if c >= o else "rgba(239,68,68,0.55)"
                for c, o in zip(df["close"], df["open"])
            ]
            fig.add_trace(go.Bar(
                x=df["date"], y=df["volume"],
                name="Volume",
                marker_color=vol_colors,
                showlegend=False,
            ), row=vol_row, col=1)

        # ── MACD ──────────────────────────────────────────────────────────
        if "macd" in df.columns:
            hist_col = df.get("macd_hist", pd.Series(dtype=float)).fillna(0)
            hist_colors = [
                "rgba(34,197,94,0.6)" if v >= 0 else "rgba(239,68,68,0.6)"
                for v in hist_col
            ]
            fig.add_trace(go.Bar(
                x=df["date"], y=hist_col,
                name="Histogram",
                marker_color=hist_colors,
                showlegend=False,
            ), row=macd_row, col=1)
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["macd"],
                name="MACD",
                line=dict(color="#4a90e8", width=1.8),
            ), row=macd_row, col=1)
            if "macd_signal" in df.columns:
                fig.add_trace(go.Scatter(
                    x=df["date"], y=df["macd_signal"],
                    name="Signal",
                    line=dict(color="#fb923c", width=1.8),
                ), row=macd_row, col=1)

        # ── RSI ───────────────────────────────────────────────────────────
        if "rsi" in df.columns:
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["rsi"],
                name="RSI",
                line=dict(color="#a78bfa", width=2),
            ), row=rsi_row, col=1)
            fig.add_hrect(y0=70, y1=100,
                          fillcolor="rgba(239,68,68,0.07)", line_width=0,
                          row=rsi_row, col=1)
            fig.add_hrect(y0=0, y1=30,
                          fillcolor="rgba(34,197,94,0.07)", line_width=0,
                          row=rsi_row, col=1)
            fig.add_hline(y=70, line_color="rgba(239,68,68,0.4)",
                          line_dash="dot", row=rsi_row, col=1)
            fig.add_hline(y=30, line_color="rgba(34,197,94,0.4)",
                          line_dash="dot", row=rsi_row, col=1)

        # ── Layout ────────────────────────────────────────────────────────
        axis_style = dict(
            gridcolor    = "rgba(255,255,255,0.035)",
            zerolinecolor= "rgba(255,255,255,0.06)",
            tickfont     = dict(color="#4a5568", size=10),
            linecolor    = "rgba(255,255,255,0.04)",
        )

        fig.update_layout(
            height                    = 840,
            paper_bgcolor             = "#080c12",
            plot_bgcolor              = "#080c12",
            font                      = dict(color="#7d8fa8", size=11,
                                             family="Space Mono, monospace"),
            xaxis_rangeslider_visible = False,
            legend                    = dict(
                orientation="h", yanchor="bottom", y=1.01,
                xanchor="left", x=0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#7d8fa8", size=10),
            ),
            margin    = dict(l=0, r=0, t=60, b=0),
            hovermode = "x unified",
            hoverlabel= dict(
                bgcolor    = "#0e1420",
                bordercolor= "#2d3748",
                font       = dict(color="#f0f6ff", size=11,
                                  family="Space Mono, monospace"),
            ),
        )

        for i in range(1, n_rows + 1):
            fig.update_xaxes(axis_style, row=i, col=1)
            fig.update_yaxes(axis_style, row=i, col=1)

        for ann in fig.layout.annotations:
            ann.font = dict(color="#4a5568", size=10, family="Space Mono, monospace")
            ann.x    = 0

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("🔍 Raw Data · Last 10 rows"):
            show_cols = ["date", "open", "high", "low", "close",
                         "volume", "rsi", "macd", "bb_upper", "bb_lower"]
            show_cols = [c for c in show_cols if c in df.columns]
            st.dataframe(
                df[show_cols].tail(10).set_index("date"),
                use_container_width=True,
            )


# ────────────────────────────────────────────────────────────────────────────
# TAB 2 — POLYMARKET
# ────────────────────────────────────────────────────────────────────────────
with tab_poly:
    st.markdown(
        f"<div class='chart-title'>🎲 Polymarket Prediction Markets — {ticker}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if poly_data.get("error"):
        st.error(f"⚠️ Polymarket error: {poly_data['error']}")
    else:
        score  = poly_data.get("score", 0.5)
        label  = poly_data.get("label", "Neutral")
        source = poly_data.get("source", "")
        mkts   = poly_data.get("markets", [])
        fetched = poly_data.get("fetched_at", "")

        # Sentiment class
        if score >= 0.55:
            sent_class  = "bullish"
            score_color = "#22c55e"
        elif score <= 0.45:
            sent_class  = "bearish"
            score_color = "#ef4444"
        else:
            sent_class  = "neutral"
            score_color = "#f59e0b"

        col_score, col_markets = st.columns([1, 2.8])

        # ── Score card ────────────────────────────────────────────────────
        with col_score:
            # Gauge-style bar
            bar_pct   = int(score * 100)
            bar_filled = "█" * (bar_pct // 5)
            bar_empty  = "░" * (20 - bar_pct // 5)

            st.markdown(
                f"<div class='score-card {sent_class}'>"
                f"<div class='score-label'>{ticker} · Crowd Sentiment</div>"
                f"<div class='score-value' style='color:{score_color};'>{score:.0%}</div>"
                f"<div class='score-tag' style='color:{score_color};'>{label}</div>"
                f"<div style='margin:16px 0 8px;font-family:Space Mono,monospace;"
                f"font-size:0.7rem;color:{score_color};letter-spacing:0.05em;'>"
                f"{bar_filled}<span style='color:#2d3748;'>{bar_empty}</span></div>"
                f"<div class='score-meta'>"
                f"<div style='margin-bottom:4px;'>"
                f"<span class='pill pill-info'>Source</span>"
                f"</div>"
                f"{source}"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if fetched:
                st.caption(f"⏱ Fetched: {fetched[:19]} UTC")

        # ── Market rows ───────────────────────────────────────────────────
        with col_markets:
            if not mkts:
                st.info(
                    f"No active prediction markets found for **{ticker}**. "
                    "Polymarket has limited individual stock coverage — "
                    "macro tickers like SPY, BTC have more markets."
                )
            else:
                st.markdown(
                    "<div class='section-label'>Active Markets</div>",
                    unsafe_allow_html=True,
                )
                for m in mkts:
                    yes_p  = m.get("yes_prob", 0) or 0
                    sent_v = m.get("sentiment")
                    vol    = m.get("volume_usd", 0) or 0
                    q      = m.get("question", "")
                    end    = m.get("end_date", "")
                    url    = m.get("url", "#")

                    # Color by yes probability
                    if yes_p >= 0.6:
                        prob_color = "#22c55e"
                    elif yes_p <= 0.4:
                        prob_color = "#ef4444"
                    else:
                        prob_color = "#f59e0b"

                    sent_badge = ""
                    if sent_v is not None:
                        if sent_v >= 0.55:
                            sent_badge = f"<span class='pill pill-pos'>↑ Bullish {sent_v:.0%}</span>"
                        elif sent_v <= 0.45:
                            sent_badge = f"<span class='pill pill-neg'>↓ Bearish {sent_v:.0%}</span>"
                        else:
                            sent_badge = f"<span class='pill pill-neu'>→ Neutral {sent_v:.0%}</span>"

                    vol_str = f"${vol:,.0f}" if vol >= 1000 else f"${vol:.0f}"
                    end_str = f"Ends {end}" if end else ""

                    st.markdown(
                        f"<div class='poly-row'>"
                        f"<div class='poly-prob' style='color:{prob_color};'>{yes_p:.0%}</div>"
                        f"<div class='poly-question'>"
                        f"<div>{q}</div>"
                        f"<div style='margin-top:5px;display:flex;gap:6px;align-items:center;'>"
                        f"{sent_badge}"
                        f"<span class='pill pill-info'>{vol_str} vol</span>"
                        f"<span style='font-family:Space Mono,monospace;font-size:0.6rem;"
                        f"color:#4a5568;'>{end_str}</span>"
                        f"</div>"
                        f"</div>"
                        f"<a href='{url}' target='_blank' style='font-family:Space Mono,monospace;"
                        f"font-size:0.6rem;color:#4a5568;text-decoration:none;"
                        f"white-space:nowrap;'>View ↗</a>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                # ── Sentiment breakdown table ──────────────────────────────
                with st.expander("📊 Full Market Data Table"):
                    mdf = pd.DataFrame(mkts)

                    def fmt_prob(x):
                        return f"{x:.0%}" if x is not None else "—"
                    def fmt_vol(x):
                        return f"${x:,.0f}" if x else "$0"

                    for c in ["yes_prob", "no_prob", "sentiment"]:
                        if c in mdf.columns:
                            mdf[c] = mdf[c].apply(fmt_prob)
                    if "volume_usd" in mdf.columns:
                        mdf["volume_usd"] = mdf["volume_usd"].apply(fmt_vol)

                    col_map = {
                        "question"  : "Market Question",
                        "yes_prob"  : "YES %",
                        "sentiment" : "Sentiment",
                        "volume_usd": "Volume",
                        "end_date"  : "Ends",
                    }
                    show_cols = [c for c in col_map if c in mdf.columns]
                    st.dataframe(
                        mdf[show_cols].rename(columns=col_map),
                        use_container_width=True,
                        hide_index=True,
                    )


# ────────────────────────────────────────────────────────────────────────────
# TAB 3 — AI SIGNAL  (NEW)
# ────────────────────────────────────────────────────────────────────────────
with tab_signal:
    st.markdown(
        f"<div class='chart-title'>🤖 Combined AI Signal — {ticker}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if sig_data.get("error"):
        st.error(f"⚠️ Signal error: {sig_data['error']}")
    else:
        final   = sig_data.get("final_signal", "HOLD")
        conf    = sig_data.get("confidence", 0.0)
        reasons = sig_data.get("reasons", [])
        tech_s  = sig_data.get("technical_signal")
        news_s  = sig_data.get("news_signal")
        p_score = sig_data.get("polymarket_score")
        p_label = sig_data.get("polymarket_label")

        if final == "BUY":
            v_class = "buy"
            v_color = "#22c55e"
            v_icon  = "↑"
        elif final == "SELL":
            v_class = "sell"
            v_color = "#ef4444"
            v_icon  = "↓"
        else:
            v_class = "hold"
            v_color = "#f59e0b"
            v_icon  = "→"

        col_verdict, col_breakdown = st.columns([1, 2])

        # ── Verdict card ─────────────────────────────────────────────────
        with col_verdict:
            conf_pct  = int(conf * 100)
            conf_fill = int(conf_pct / 5)
            conf_bar  = "█" * conf_fill + "░" * (20 - conf_fill)

            st.markdown(
                f"<div class='score-card {v_class}'>"
                f"<div class='score-label'>AI Verdict · {ticker}</div>"
                f"<div style='font-size:3rem;'>{v_icon}</div>"
                f"<div class='score-value' style='color:{v_color};font-size:2.6rem;'>{final}</div>"
                f"<div style='margin:16px 0 8px;font-family:Space Mono,monospace;"
                f"font-size:0.7rem;color:{v_color};'>{conf_bar}</div>"
                f"<div class='score-tag' style='color:{v_color};'>Confidence: {conf_pct}%</div>"
                f"<div class='score-meta'>Technical · News · Crowd</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # ── Signal breakdown ─────────────────────────────────────────────
        with col_breakdown:
            st.markdown(
                "<div class='section-label'>Signal Sources</div>",
                unsafe_allow_html=True,
            )
            tech_score = sig_data.get("technical_score")
            news_score = sig_data.get("news_score")
            final_score = sig_data.get("final_score", 0.5)

            def _signal_pill(sig: str | None) -> str:
                if not sig:
                    return "<span class='pill pill-neu'>—</span>"
                s = sig.upper()
                if "BUY" in s:
                    return f"<span class='pill pill-pos'>{sig}</span>"
                if "SELL" in s:
                    return f"<span class='pill pill-neg'>{sig}</span>"
                return f"<span class='pill pill-neu'>{sig}</span>"

            def _score_pill(score: float | None, label: str | None) -> str:
                if score is None:
                    return "<span class='pill pill-neu'>—</span>"
                if score >= 0.55:
                    cls = "pill-pos"
                elif score <= 0.45:
                    cls = "pill-neg"
                else:
                    cls = "pill-neu"
                lbl = label or f"{score:.0%}"
                return f"<span class='pill {cls}'>{lbl} ({score:.0%})</span>"

            def _driver_tone(score: float | None) -> tuple[str, str]:
                if score is None:
                    return "#7d8fa8", "No clear read"
                if score >= 0.60:
                    return "#22c55e", "Bullish bias"
                if score <= 0.40:
                    return "#ef4444", "Bearish bias"
                return "#f59e0b", "Balanced / mixed"

            def _explain_reason(text: str) -> tuple[str, str]:
                clean = text.replace("->", "→")
                if clean.startswith("Technical composite="):
                    return "Verdict", clean.replace("Technical composite=", "Technical model score ")
                if clean.startswith("RSI "):
                    return "RSI", clean.replace("→", "suggests")
                if clean.startswith("MACD spread"):
                    return "MACD", clean.replace("→", "suggests")
                if clean.startswith("News sentiment="):
                    return "News", clean.replace("normalized=", "normalized to ").replace("→", "which maps to")
                if clean.startswith("Polymarket="):
                    return "Crowd", clean.replace("→", "which reads as")
                return "Detail", clean

            conflict_note = ""
            if news_score is not None and p_score is not None:
                if news_score >= 0.60 and p_score <= 0.40:
                    conflict_note = "News is bullish while crowd positioning is bearish, so the model stays cautious."
                elif news_score <= 0.40 and p_score >= 0.60:
                    conflict_note = "News is bearish while crowd positioning is bullish, so the model avoids a strong directional call."

            summary_copy = (
                f"The model ends at <strong>{final}</strong> with a composite score of "
                f"<strong>{final_score:.0%}</strong> and confidence of <strong>{int(conf * 100)}%</strong>. "
                f"Technicals currently read <strong>{tech_s or 'unavailable'}</strong>, "
                f"news sentiment reads <strong>{news_s or 'unavailable'}</strong>, and "
                f"Polymarket reads <strong>{p_label or 'unavailable'}</strong>."
            )
            if conflict_note:
                summary_copy += f" {conflict_note}"

            st.markdown(
                f"<div class='signal-summary'>"
                f"<div class='signal-summary-title'>Why the model reached this conclusion</div>"
                f"<div class='signal-summary-copy'>{summary_copy}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            sources = [
                ("Technical", tech_s, tech_score, "RSI, MACD, and moving-average trend"),
                ("News", news_s, news_score, "FinBERT sentiment across recent headlines"),
                ("Polymarket", p_label or "—", p_score, "Crowd probability from active prediction markets"),
            ]

            driver_cards = []
            for src_label, signal_label, score_value, meta_copy in sources:
                tone_color, tone_copy = _driver_tone(score_value)
                score_text = "—" if score_value is None else f"{score_value:.0%}"
                pill_html = (
                    _score_pill(score_value, signal_label)
                    if src_label == "Polymarket"
                    else _signal_pill(signal_label)
                )
                driver_cards.append(
                    f"<div class='signal-driver'>"
                    f"<div class='signal-driver-label'>{src_label}</div>"
                    f"<div class='signal-driver-value' style='color:{tone_color};'>{score_text}</div>"
                    f"<div style='margin-bottom:10px;'>{pill_html}</div>"
                    f"<div class='signal-driver-meta'>{tone_copy}. {meta_copy}.</div>"
                    f"</div>"
                )

            st.markdown(
                f"<div class='signal-grid'>{''.join(driver_cards)}</div>",
                unsafe_allow_html=True,
            )

            if reasons:
                st.markdown(
                    "<div class='section-label' style='margin-top:4px;'>Evidence Trail</div>",
                    unsafe_allow_html=True,
                )
                for r in reasons:
                    reason_key, reason_copy = _explain_reason(r)
                    st.markdown(
                        f"<div class='signal-evidence'>"
                        f"<div class='signal-evidence-key'>{reason_key}</div>"
                        f"<div class='signal-evidence-copy'>{reason_copy}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

            # ── Mini gauge chart ──────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<div class='section-label'>Signal Components</div>",
                unsafe_allow_html=True,
            )

            source_scores = []
            source_labels = []

            if tech_s:
                ts = 0.8 if "BUY" in tech_s.upper() else (0.2 if "SELL" in tech_s.upper() else 0.5)
                source_scores.append(ts)
                source_labels.append("Technical")
            if news_s:
                ns = 0.8 if "BUY" in news_s.upper() else (0.2 if "SELL" in news_s.upper() else 0.5)
                source_scores.append(ns)
                source_labels.append("News")
            if p_score is not None:
                source_scores.append(p_score)
                source_labels.append("Polymarket")

            if source_scores:
                bar_colors = [
                    "#22c55e" if s >= 0.55 else ("#ef4444" if s <= 0.45 else "#f59e0b")
                    for s in source_scores
                ]
                fig_sig = go.Figure(go.Bar(
                    x           = source_labels,
                    y           = source_scores,
                    marker_color= bar_colors,
                    text        = [f"{s:.0%}" for s in source_scores],
                    textposition= "auto",
                    textfont    = dict(color="#fff", family="Space Mono, monospace",
                                       size=11),
                ))
                fig_sig.add_hline(
                    y=0.5,
                    line_color="rgba(255,255,255,0.2)",
                    line_dash="dot",
                    annotation_text="Neutral",
                    annotation_font_color="#4a5568",
                )
                fig_sig.update_layout(
                    height        = 220,
                    paper_bgcolor = "#080c12",
                    plot_bgcolor  = "#080c12",
                    font          = dict(color="#7d8fa8", size=10,
                                        family="Space Mono, monospace"),
                    margin        = dict(l=0, r=0, t=20, b=0),
                    yaxis         = dict(range=[0, 1], gridcolor="rgba(255,255,255,0.04)",
                                        tickformat=".0%", tickfont=dict(size=9)),
                    xaxis         = dict(gridcolor="rgba(255,255,255,0.04)"),
                    showlegend    = False,
                )
                st.plotly_chart(fig_sig, use_container_width=True)


# ────────────────────────────────────────────────────────────────────────────
# TAB 4 — NEWS ANALYSIS
# ────────────────────────────────────────────────────────────────────────────
with tab_news:
    st.markdown(
        f"<div class='chart-title'>📰 Official News Analysis — {ticker}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner(f"Running FinBERT analysis on {ticker} headlines…"):
        sentiment_data = get_sentiment(ticker)

    if sentiment_data.get("error"):
        st.error(f"⚠️ Failed to load sentiment data: {sentiment_data['error']}")
    else:
        official_analysis = sentiment_data.get("official_analysis", {})
        public_opinion = sentiment_data.get("public_opinion", {})
        official_summary = official_analysis.get("summary", {})
        official_articles = official_analysis.get("articles", [])
        top_discussions = public_opinion.get("top_discussions", [])

        source_badges = {
            "news": ("NEWS", "pill-info"),
            "yahoo": ("YAHOO", "pill-info"),
            "reddit": ("REDDIT", "pill-neu"),
            "stocktwits": ("STOCKTWITS", "pill-pur"),
        }

        def render_source_feed(items: list[dict], empty_copy: str):
            if not items:
                st.info(empty_copy)
                return

            for item in items:
                title = item.get("title", "Untitled")
                sent = (item.get("sentiment") or "neutral").lower()
                item_score = item.get("score", 0.0) or 0.0
                source_key = (item.get("source") or "news").lower()
                source_label, source_class = source_badges.get(
                    source_key,
                    (source_key.upper(), "pill-info"),
                )
                url = item.get("url", "")

                if sent == "positive":
                    pill_class, item_class, icon = "pill-pos", "positive", "↑"
                elif sent == "negative":
                    pill_class, item_class, icon = "pill-neg", "negative", "↓"
                else:
                    pill_class, item_class, icon = "pill-neu", "neutral", "→"

                view_link = (
                    f"<a href='{url}' target='_blank' style='font-family:Space Mono,monospace;"
                    f"font-size:0.6rem;color:#4a5568;text-decoration:none;"
                    f"white-space:nowrap;'>View Source &#8599;</a>"
                    if url else ""
                )

                st.markdown(
                    f"<div class='news-item {item_class}'>"
                    f"<div style='display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;'>"
                    f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
                    f"<span class='pill {pill_class}'>{icon} {sent.upper()} {item_score:+.2f}</span>"
                    f"<span class='pill {source_class}'>{source_label}</span>"
                    f"</div>"
                    f"{view_link}"
                    f"</div>"
                    f"<div class='news-headline'>{title}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        st.markdown("<div class='section-label'>📰 Official News Analysis</div>", unsafe_allow_html=True)

        signal = official_summary.get("signal", "NEUTRAL")
        score  = official_summary.get("score", 0.0)
        conf   = official_summary.get("confidence", 0.0)
        reason = official_summary.get("reason", "")

        if "BUY" in signal:
            sig_class = "bullish"
            sig_color = "#22c55e"
        elif "SELL" in signal:
            sig_class = "bearish"
            sig_color = "#ef4444"
        else:
            sig_class = "neutral"
            sig_color = "#f59e0b"
        signal_font_size = "1.7rem" if len(signal) >= 8 else "2.2rem"

        col_sent_score, col_sent_news = st.columns([1, 2.5])

        with col_sent_score:
            conf_pct = int(conf * 100)
            st.markdown(
                f"<div class='score-card {sig_class}'>"
                f"<div class='score-label'>Official Yahoo Signal</div>"
                f"<div class='score-value' style='color:{sig_color};font-size:{signal_font_size};line-height:1.05;'>"
                f"{signal}</div>"
                f"<div class='score-tag' style='color:{sig_color};'>Score: {score:+.2f}</div>"
                f"<div style='margin:18px 0 6px;'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"font-family:Space Mono,monospace;font-size:0.6rem;color:#4a5568;"
                f"margin-bottom:6px;'>"
                f"<span>CONFIDENCE</span><span>{conf_pct}%</span>"
                f"</div>"
                f"<div style='background:rgba(255,255,255,0.04);border-radius:4px;height:4px;'>"
                f"<div style='width:{conf_pct}%;height:100%;border-radius:4px;"
                f"background:{sig_color};box-shadow:0 0 8px {sig_color};'></div>"
                f"</div>"
                f"</div>"
                f"<div class='score-meta' style='font-style:italic;color:#7d8fa8;'>"
                f"\"{reason}\"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # ── Sentiment distribution mini chart ──────────────────────
            pos = sum(1 for a in official_articles if a.get("sentiment") == "positive")
            neg = sum(1 for a in official_articles if a.get("sentiment") == "negative")
            neu = sum(1 for a in official_articles if a.get("sentiment") == "neutral")

            if official_articles:
                fig_dist = go.Figure(go.Pie(
                    labels    = ["Positive", "Negative", "Neutral"],
                    values    = [pos, neg, neu],
                    hole      = 0.65,
                    marker    = dict(colors=["#22c55e", "#ef4444", "#f59e0b"],
                                     line=dict(color="#080c12", width=2)),
                    textinfo  = "percent",
                    textfont  = dict(color="#fff", size=10,
                                     family="Space Mono, monospace"),
                    showlegend= True,
                ))
                fig_dist.update_layout(
                    height        = 200,
                    paper_bgcolor = "#080c12",
                    plot_bgcolor  = "#080c12",
                    font          = dict(color="#7d8fa8", size=9,
                                        family="Space Mono, monospace"),
                    margin        = dict(l=0, r=0, t=10, b=0),
                    legend        = dict(
                        font    = dict(color="#7d8fa8", size=9),
                        bgcolor = "rgba(0,0,0,0)",
                        orientation="h",
                        y=-0.1,
                    ),
                    annotations=[dict(
                        text     = f"{len(official_articles)}<br><span style='font-size:8px'>articles</span>",
                        x=0.5, y=0.5,
                        font     = dict(color="#7d8fa8", size=11,
                                        family="Space Mono, monospace"),
                        showarrow= False,
                    )],
                )
                st.plotly_chart(fig_dist, use_container_width=True)

        with col_sent_news:
            st.markdown(
                "<div class='section-label'>Yahoo Finance Articles</div>",
                unsafe_allow_html=True,
            )
            for art in official_articles:
                title     = art.get("title", "Untitled")
                sent      = (art.get("sentiment") or "neutral").lower()
                art_score = art.get("score", 0.0) or 0.0
                source_key = (art.get("source") or "news").lower()
                source_label, source_class = source_badges.get(
                    source_key,
                    (source_key.upper(), "pill-info"),
                )
                url = art.get("url", "")

                if sent == "positive":
                    pill_class, item_class, icon = "pill-pos", "positive", "↑"
                elif sent == "negative":
                    pill_class, item_class, icon = "pill-neg", "negative", "↓"
                else:
                    pill_class, item_class, icon = "pill-neu", "neutral",  "→"

                view_link = (
                    f"<a href='{url}' target='_blank' style='font-family:Space Mono,monospace;"
                    f"font-size:0.6rem;color:#4a5568;text-decoration:none;"
                    f"white-space:nowrap;'>View Source &#8599;</a>"
                    if url else ""
                )

                st.markdown(
                    f"<div class='news-item {item_class}'>"
                    f"<div style='display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;'>"
                    f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
                    f"<span class='pill {pill_class}'>"
                    f"{icon} {sent.upper()} {art_score:+.2f}</span>"
                    f"<span class='pill {source_class}'>{source_label}</span>"
                    f"</div>"
                    f"{view_link}"
                    f"</div>"
                    f"<div class='news-headline'>{title}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# ────────────────────────────────────────────────────────────────────────────
# TAB 5 — PUBLIC OPINION
# ────────────────────────────────────────────────────────────────────────────
with tab_public:
    st.markdown(
        f"<div class='chart-title'>👥 Public Opinion — {ticker}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    with st.spinner(f"Loading public opinion for {ticker}…"):
        sentiment_data = get_sentiment(ticker)

    if sentiment_data.get("error"):
        st.error(f"⚠️ Failed to load public opinion: {sentiment_data['error']}")
    else:
        public_opinion = sentiment_data.get("public_opinion", {})
        top_discussions = public_opinion.get("top_discussions", [])

        source_badges = {
            "reddit": ("REDDIT", "pill-neu"),
            "stocktwits": ("STOCKTWITS", "pill-pur"),
        }

        def render_public_feed(items: list[dict], empty_copy: str):
            if not items:
                st.info(empty_copy)
                return

            for item in items:
                title = item.get("title", "Untitled")
                sent = (item.get("sentiment") or "neutral").lower()
                item_score = item.get("score", 0.0) or 0.0
                source_key = (item.get("source") or "public").lower()
                source_label, source_class = source_badges.get(
                    source_key,
                    (source_key.upper(), "pill-info"),
                )
                url = item.get("url", "")

                if sent == "positive":
                    pill_class, item_class, icon = "pill-pos", "positive", "↑"
                elif sent == "negative":
                    pill_class, item_class, icon = "pill-neg", "negative", "↓"
                else:
                    pill_class, item_class, icon = "pill-neu", "neutral", "→"

                view_link = (
                    f"<a href='{url}' target='_blank' style='font-family:Space Mono,monospace;"
                    f"font-size:0.6rem;color:#4a5568;text-decoration:none;"
                    f"white-space:nowrap;'>View Source &#8599;</a>"
                    if url else ""
                )

                st.markdown(
                    f"<div class='news-item {item_class}'>"
                    f"<div style='display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;'>"
                    f"<div style='display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>"
                    f"<span class='pill {pill_class}'>{icon} {sent.upper()} {item_score:+.2f}</span>"
                    f"<span class='pill {source_class}'>{source_label}</span>"
                    f"</div>"
                    f"{view_link}"
                    f"</div>"
                    f"<div class='news-headline'>{title}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        public_score = public_opinion.get("public_sentiment_score", 0.0)
        public_signal = public_opinion.get("public_signal", "NEUTRAL")
        public_conf = public_opinion.get("confidence", 0.0)
        public_volume = public_opinion.get("volume", 0)

        if public_signal == "BULLISH":
            public_class = "bullish"
            public_color = "#22c55e"
        elif public_signal == "BEARISH":
            public_class = "bearish"
            public_color = "#ef4444"
        else:
            public_class = "neutral"
            public_color = "#f59e0b"
        public_signal_font_size = "1.7rem" if len(public_signal) >= 8 else "2.2rem"

        col_pub_score, col_pub_feed = st.columns([1, 2.5])

        with col_pub_score:
            public_conf_pct = int(public_conf * 100)
            st.markdown(
                f"<div class='score-card {public_class}'>"
                f"<div class='score-label'>Retail/Public Mood</div>"
                f"<div class='score-value' style='color:{public_color};font-size:{public_signal_font_size};line-height:1.05;'>{public_signal}</div>"
                f"<div class='score-tag' style='color:{public_color};'>Score: {public_score:+.2f}</div>"
                f"<div style='margin:18px 0 6px;'>"
                f"<div style='display:flex;justify-content:space-between;"
                f"font-family:Space Mono,monospace;font-size:0.6rem;color:#4a5568;"
                f"margin-bottom:6px;'>"
                f"<span>CONFIDENCE</span><span>{public_conf_pct}%</span>"
                f"</div>"
                f"<div style='background:rgba(255,255,255,0.04);border-radius:4px;height:4px;'>"
                f"<div style='width:{public_conf_pct}%;height:100%;border-radius:4px;"
                f"background:{public_color};box-shadow:0 0 8px {public_color};'></div>"
                f"</div>"
                f"</div>"
                f"<div class='score-meta'>Retail posts analyzed: {public_volume}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_pub_feed:
            st.markdown(
                "<div class='section-label'>Reddit Discussions & StockTwits Posts</div>",
                unsafe_allow_html=True,
            )
            render_public_feed(
                top_discussions,
                f"ℹ️ No recent Reddit or StockTwits discussions found for **{ticker}**.",
            )


