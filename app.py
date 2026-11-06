from pathlib import Path
from datetime import datetime
import base64

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# ==========================================
# LERCHNOLIMIT – virtuelle Trading-Lernplattform
# ==========================================
BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "file_000000006f2c81f5a5097c657e3366d1.png"
BACKGROUND_PATH = BASE_DIR / "file_000000006b8081f4bbe2c991f86ba04a.png"


def image_data_uri(path):
    """Return a local image as a browser-ready data URI for CSS/HTML."""
    if not path.exists():
        return ""
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


LOGO_URI = image_data_uri(LOGO_PATH)
BACKGROUND_URI = image_data_uri(BACKGROUND_PATH)
st.set_page_config(
    page_title="LerchnoLimit",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🍄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Use the supplied mushroom-world image as a darkened, full-page backdrop.
background_css = (
    f'url("{BACKGROUND_URI}")' if BACKGROUND_URI else "none"
)
st.markdown(f"""
<style>
:root {{
    --pink: #ff4da6;
    --pink-light: #ff83c2;
    --ink: #100a12;
    --panel: rgba(15, 10, 17, .82);
    --line: rgba(255, 77, 166, .35);
}}
.stApp {{
    color: #fff;
    background-color: #080608;
    background-image: linear-gradient(rgba(8, 6, 8, .78), rgba(8, 6, 8, .88)), {background_css};
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
[data-testid="stHeader"], [data-testid="stMain"],
[data-testid="stAppViewContainer"], [data-testid="stAppViewBlockContainer"] {{
    background: transparent !important;
}}
.block-container {{
    max-width: 1180px;
    padding: 2rem clamp(1rem, 4vw, 3rem) 3rem;
}}
h1, h2, h3, p, label, [data-testid="stCaptionContainer"] {{
    color: #fff;
}}
h1, h2, h3 {{ letter-spacing: -.025em; }}
.hero {{
    max-width: 940px;
    margin: 1.5rem auto 1rem;
    padding: clamp(1.5rem, 5vw, 3.5rem);
    border: 1px solid var(--line);
    border-radius: 28px;
    text-align: center;
    background: linear-gradient(145deg, rgba(20, 10, 20, .84), rgba(8, 6, 8, .91));
    box-shadow: 0 18px 70px rgba(0,0,0,.4), 0 0 30px rgba(255,77,166,.12);
    backdrop-filter: blur(8px);
}}
.hero-logo, .dashboard-logo {{
    display: block;
    width: min(100%, 300px);
    height: auto;
    margin: 0 auto 1.3rem;
    border-radius: 24px;
    box-shadow: 0 0 28px rgba(255,77,166,.28);
}}
.neon {{
    color: var(--pink-light) !important;
    text-shadow: 0 0 22px rgba(255,77,166,.46);
}}
.dashboard-brand {{
    text-align: center;
    margin: .25rem auto 1.5rem;
    padding: 1.25rem 1rem;
}}
.dashboard-brand img {{
    display: block;
    width: clamp(150px, 30vw, 230px);
    height: auto;
    margin: 0 auto 1rem;
    border-radius: 22px;
    box-shadow: 0 0 32px rgba(255,77,166,.28);
}}
.dashboard-brand h1 {{
    color: var(--pink-light) !important;
    margin: 0;
    text-shadow: 0 0 18px rgba(255,77,166,.35);
}}
.dashboard-brand p {{ margin: .35rem 0 0; color: rgba(255,255,255,.82); }}
.stButton > button {{
    min-height: 2.8rem;
    background: linear-gradient(135deg, #351027, var(--pink)) !important;
    color: white !important;
    border: 1px solid var(--pink) !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    transition: transform .18s ease, box-shadow .18s ease !important;
}}
.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 0 22px rgba(255,77,166,.48);
}}
[data-testid="stImage"] img {{
    border: 2px solid var(--pink);
    border-radius: 22px;
    box-shadow: 0 0 22px rgba(255,77,166,.32);
}}
.notice {{
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 14px 18px;
    background: rgba(15, 10, 17, .82);
    color: rgba(255,255,255,.94);
}}
div[data-testid="stMetric"], div[data-testid="stTabs"] {{
    background: rgba(10, 8, 12, .68);
    border: 1px solid rgba(255,255,255,.08);
    border-radius: 14px;
    padding: .65rem;
}}
[data-baseweb="tab-list"] {{ gap: .35rem; }}
[data-baseweb="tab"] {{ color: white; }}
[data-testid="stDataFrame"], [data-testid="stTable"] {{
    border: 1px solid var(--line);
    border-radius: 12px;
    overflow: hidden;
}}
@media (max-width: 700px) {{
    .block-container {{ padding: 1rem .75rem 2rem; }}
    .hero {{ margin: .5rem auto 1rem; border-radius: 20px; }}
    .hero-logo {{ width: min(72vw, 250px); }}
    .dashboard-brand {{ padding: .5rem 0 1rem; }}
    .dashboard-brand img {{ width: min(62vw, 190px); }}
    h1 {{ font-size: 2rem !important; }}
    [data-testid="stMetric"] {{ padding: .45rem !important; }}
    .stApp {{ background-attachment: scroll; }}
}}
@media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{ scroll-behavior: auto !important; transition: none !important; }}
}}
</style>
""", unsafe_allow_html=True)

# ==========================================
# VIRTUELLES DEPOT
# ==========================================
if "started" not in st.session_state:
    st.session_state.started = False
if "cash" not in st.session_state:
    st.session_state.cash = 10000.0
if "positions" not in st.session_state:
    st.session_state.positions = {}
if "trades" not in st.session_state:
    st.session_state.trades = []

# ==========================================
# MARKTDATEN
# ==========================================
@st.cache_data(ttl=300, show_spinner=False)
def load_market_data(symbol, period):
    data = yf.download(
        symbol, period=period, interval="1d", auto_adjust=True,
        progress=False, threads=False
    )
    if data is None or data.empty:
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.reset_index()
    if "Date" not in data.columns and "Datetime" in data.columns:
        data = data.rename(columns={"Datetime": "Date"})
    return data


def latest_price(symbol):
    data = load_market_data(symbol, "5d")
    if data.empty or "Close" not in data:
        return None
    values = data["Close"].dropna()
    return float(values.iloc[-1]) if not values.empty else None


def money(value):
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def render_lou_comment(symbol, data):
    if data.empty or len(data) < 50:
        st.info("Lou: Für eine Einschätzung brauche ich mehr Kursdaten.")
        return
    close = data["Close"].dropna()
    sma20, sma50, last = close.rolling(20).mean().iloc[-1], close.rolling(50).mean().iloc[-1], float(close.iloc[-1])
    if pd.isna(sma20) or pd.isna(sma50):
        st.info("Lou: Die Trendindikatoren sind noch nicht vollständig.")
    elif last > sma20 > sma50:
        st.success(f"Lou: {symbol} liegt über SMA20 und SMA50. Das ist ein positives Trend-Signal, aber keine Kaufempfehlung.")
    elif last < sma20 < sma50:
        st.warning(f"Lou: {symbol} liegt unter SMA20 und SMA50. Das ist ein schwaches Trend-Signal.")
    else:
        st.info(f"Lou: {symbol} zeigt aktuell ein gemischtes Signal.")

# ==========================================
# DASHBOARD
# ==========================================
def show_dashboard():
    logo_markup = f'<img src="{LOGO_URI}" alt="LerchnoLimit-Pilzlogo mit Krone">' if LOGO_URI else '<div style="font-size:4rem">🍄👑</div>'
    st.markdown(
        f'<div class="dashboard-brand">{logo_markup}<h1>LerchnoLimit</h1>'
        '<p>Dein virtueller Trading-Lernplatz mit Lou</p></div>',
        unsafe_allow_html=True,
    )
    st.caption("Virtuelles Trading · echte Marktdaten · kein Echtgeld")
    st.markdown(
        '<div class="notice">Alle Käufe und Verkäufe sind ausschließlich simuliert. '
        'Es werden keine echten Börsenorders gesendet.</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Dein virtuelles Depot")
        st.metric("Freies virtuelles Kapital", money(st.session_state.cash))
        st.caption("Spielgeld · Startkapital: 10.000 €")
        if st.button("Virtuelles Depot zurücksetzen", use_container_width=True):
            st.session_state.cash = 10000.0
            st.session_state.positions = {}
            st.session_state.trades = []
            st.rerun()

    tabs = st.tabs(["📈 Markt & Lou", "💹 Virtuell traden", "🧾 Depot & Verlauf"])

    # Markt & Lou
    with tabs[0]:
        col1, col2 = st.columns([2, 1])
        with col1:
            symbol = st.text_input("Börsenkürzel", value="AAPL").strip().upper()
            period_label = st.selectbox("Zeitraum", ["1 Monat", "3 Monate", "6 Monate", "1 Jahr", "2 Jahre", "5 Jahre"], index=3)
        periods = {"1 Monat": "1mo", "3 Monate": "3mo", "6 Monate": "6mo", "1 Jahr": "1y", "2 Jahre": "2y", "5 Jahre": "5y"}
        if symbol:
            with st.spinner("Marktdaten werden geladen ..."):
                data = load_market_data(symbol, periods[period_label])
            if data.empty or "Close" not in data:
                st.error("Keine Kursdaten gefunden. Bitte prüfe das Börsenkürzel.")
            else:
                close = data["Close"].dropna()
                current = float(close.iloc[-1])
                previous = float(close.iloc[-2]) if len(close) > 1 else current
                with col2:
                    st.metric(f"Letzter Kurs · {symbol}", f"{current:,.2f}", f"{current - previous:+.2f}")
                data["SMA20"] = data["Close"].rolling(20).mean()
                data["SMA50"] = data["Close"].rolling(50).mean()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Kurs", line=dict(color="#FF4DA6", width=2)))
                fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA20"], name="SMA 20", line=dict(color="#FFFFFF")))
                fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA50"], name="SMA 50", line=dict(color="#888888")))
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor="rgba(8,6,8,0.82)",
                    plot_bgcolor="rgba(16,5,9,0.82)", height=430,
                    autosize=True, margin=dict(l=12, r=12, t=35, b=12),
                )
                st.plotly_chart(fig, use_container_width=True)
                render_lou_comment(symbol, data)
                st.caption("Historische Indikatoren sind keine Vorhersage zukünftiger Kurse.")

    # Virtuelles Trading
    with tabs[1]:
        st.subheader("Virtuelle Order")
        st.write("Teste Käufe und Verkäufe mit Spielgeld.")
        c1, c2, c3 = st.columns(3)
        with c1:
            trade_symbol = st.text_input("Kürzel", value="AAPL", key="trade_symbol").strip().upper()
        with c2:
            side = st.selectbox("Aktion", ["Kaufen", "Verkaufen"])
        with c3:
            shares = st.number_input("Stückzahl", min_value=0.001, max_value=1000000.0, value=1.0, step=1.0)
        if trade_symbol:
            with st.spinner("Kurs wird geprüft ..."):
                price = latest_price(trade_symbol)
            if price is None:
                st.error("Kein Kurs abrufbar.")
            else:
                order_value = price * shares
                st.metric("Ungefährer Orderwert", f"{order_value:,.2f} (Kurswährung)")
                st.caption("Marktdaten können verzögert sein. Es erfolgt keine Währungsumrechnung.")
                if side == "Kaufen":
                    if st.button("Virtuell kaufen", type="primary", use_container_width=True):
                        if order_value > st.session_state.cash:
                            st.error("Nicht genug virtuelles Guthaben.")
                        else:
                            pos = st.session_state.positions.get(trade_symbol, {"shares": 0.0, "cost": 0.0})
                            pos["shares"] += shares
                            pos["cost"] += order_value
                            st.session_state.positions[trade_symbol] = pos
                            st.session_state.cash -= order_value
                            st.session_state.trades.insert(0, {
                                "Zeit": datetime.now().strftime("%d.%m.%Y %H:%M"), "Kürzel": trade_symbol,
                                "Aktion": "Kauf", "Stück": shares, "Kurs": price, "Wert": order_value,
                            })
                            st.success("Virtueller Kauf ausgeführt.")
                            st.rerun()
                else:
                    owned = st.session_state.positions.get(trade_symbol, {}).get("shares", 0.0)
                    st.caption(f"Im Depot: {owned:g} Stück")
                    if st.button("Virtuell verkaufen", type="primary", use_container_width=True):
                        if owned <= 0 or shares > owned:
                            st.error("Nicht genügend Stücke vorhanden.")
                        else:
                            pos = st.session_state.positions[trade_symbol]
                            proceeds = price * shares
                            remaining = owned - shares
                            if remaining <= 1e-9:
                                del st.session_state.positions[trade_symbol]
                            else:
                                pos["shares"] = remaining
                                pos["cost"] *= remaining / owned
                            st.session_state.cash += proceeds
                            st.session_state.trades.insert(0, {
                                "Zeit": datetime.now().strftime("%d.%m.%Y %H:%M"), "Kürzel": trade_symbol,
                                "Aktion": "Verkauf", "Stück": shares, "Kurs": price, "Wert": proceeds,
                            })
                            st.success("Virtueller Verkauf ausgeführt.")
                            st.rerun()

    # Depot & Verlauf
    with tabs[2]:
        st.subheader("Dein virtuelles Depot")
        rows, total_market_value = [], 0.0
        for symbol, pos in st.session_state.positions.items():
            price = latest_price(symbol)
            if price is not None:
                value = pos["shares"] * price
                total_market_value += value
                rows.append({
                    "Kürzel": symbol, "Stück": round(pos["shares"], 6), "Letzter Kurs": round(price, 4),
                    "Marktwert": round(value, 2), "Einstand gesamt": round(pos["cost"], 2),
                    "Unrealisierte Differenz": round(value - pos["cost"], 2),
                })
        c1, c2, c3 = st.columns(3)
        c1.metric("Freies virtuelles Guthaben", money(st.session_state.cash))
        c2.metric("Wert der Positionen", money(total_market_value))
        c3.metric("Virtueller Depotwert", money(st.session_state.cash + total_market_value))
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("Dein virtuelles Depot ist noch leer.")
        st.subheader("Letzte Transaktionen")
        if st.session_state.trades:
            st.dataframe(pd.DataFrame(st.session_state.trades), use_container_width=True, hide_index=True)
        else:
            st.caption("Noch keine virtuellen Trades.")

    st.divider()
    st.caption("LerchnoLimit ist eine Lernsimulation. Keine Anlageberatung und keine Gewinnversprechen.")

# ==========================================
# STARTSEITE / APP
# ==========================================
if not st.session_state.started:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    if LOGO_URI:
        st.markdown(f'<img class="hero-logo" src="{LOGO_URI}" alt="LerchnoLimit-Logo: Pilz mit Krone">', unsafe_allow_html=True)
    else:
        st.markdown("🍄👑")
    st.markdown('<h1 class="neon">LerchnoLimit</h1>', unsafe_allow_html=True)
    st.markdown("### Deine Zukunft. Deine Möglichkeiten.")
    st.markdown("**Dein virtueller Trading-Lernplatz mit Lou**")
    st.markdown('</div>', unsafe_allow_html=True)
    _, center, _ = st.columns([1, 2, 1])
    with center:
        if st.button("🚀 Jetzt starten", use_container_width=True):
            st.session_state.started = True
            st.rerun()
    st.caption("Echte, möglicherweise verzögerte Marktdaten · ausschließlich virtuelles Trading · kein Echtgeld")
else:
    if st.button("← Zur Startseite"):
        st.session_state.started = False
        st.rerun()
    show_dashboard()
