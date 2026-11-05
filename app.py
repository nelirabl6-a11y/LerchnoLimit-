
import base64
from pathlib import Path

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --------------------------------------------------
# LERCHNOLIMIT – EINSTELLUNGEN
# --------------------------------------------------

BASE_DIR = Path(__file__).parent

LOGO_PATH = BASE_DIR / "file_000000006f2c81f5a5097c657e3366d1.png"
BACKGROUND_PATH = BASE_DIR / "file_000000006b8081f4bbe2c991f86ba04a.png"

st.set_page_config(
    page_title="LerchnoLimit",
    page_icon=str(LOGO_PATH),
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False

# Vorhandenes Landschaftsbild laden
background_css = ""

if BACKGROUND_PATH.exists():
    encoded = base64.b64encode(
        BACKGROUND_PATH.read_bytes()
    ).decode("utf-8")

    background_css = f"""
    background-image:
        linear-gradient(
            rgba(8, 6, 8, 0.42),
            rgba(8, 6, 8, 0.72)
        ),
        url("data:image/png;base64,{encoded}");
    """

# --------------------------------------------------
# DESIGN
# --------------------------------------------------

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-color: #080608;
        {background_css}
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}

    [data-testid="stMain"] {{
        background: transparent;
    }}

    [data-testid="stHeader"] {{
        background: rgba(8, 6, 8, 0.35);
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }}

    h1, h2, h3, p, label {{
        color: white !important;
    }}

    .hero {{
        min-height: 68vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        animation: fadeIn 1.1s ease;
    }}

    .hero-tag {{
        color: #ffd6eb;
        background: rgba(8, 6, 8, 0.65);
        border: 1px solid #ff4da6;
        border-radius: 30px;
        padding: 9px 20px;
        margin: 18px 0;
    }}

    .hero-subtitle {{
        color: #ffe8f4;
        font-size: 1.3rem;
        text-shadow: 0 2px 12px #080608;
    }}

    .stButton > button {{
        background: linear-gradient(100deg, #ff168f, #a90065);
        color: white !important;
        border: 1px solid #ff78c0;
        border-radius: 40px;
        min-height: 3.5rem;
        font-size: 1.15rem;
        font-weight: bold;
        box-shadow: 0 0 22px rgba(255, 35, 153, 0.5);
        transition: all 0.3s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-3px);
        box-shadow: 0 0 35px rgba(255, 35, 153, 0.8);
    }}

    [data-testid="stMetricValue"] {{
        color: #ff4da6;
    }}

    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(18px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    @media (max-width: 640px) {{
        .hero {{
            min-height: 60vh;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# STARTSEITE
# --------------------------------------------------

if not st.session_state.show_dashboard:

    st.markdown('<div class="hero">', unsafe_allow_html=True)

    # Original-Pilzlogo – unverändert
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=245)
    else:
        st.warning("Das Logo wurde nicht gefunden.")

    st.markdown(
        """
        <div class="hero-tag">
            ✦ KI-Assistent Lou · LerchnoLimit
        </div>

        <h1 style="font-size:clamp(2.5rem,6vw,4.5rem);">
            LerchnoLimit
        </h1>

        <div class="hero-subtitle">
            Deine Zukunft. Deine Möglichkeiten.
        </div>

        <p style="margin-top:20px;">
            Entdecke. Analysiere. Lerne.
            In deiner virtuellen Finanzwelt.
        </p>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

    links, mitte, rechts = st.columns([1, 2, 1])

    with mitte:
        if st.button("Jetzt starten  →", use_container_width=True):
            st.session_state.show_dashboard = True
            st.rerun()

    st.caption(
        "Virtuelle Lern- und Demo-Anwendung · "
        "Kein echtes Geld · Keine garantierten Gewinne"
    )

# --------------------------------------------------
# DASHBOARD NACH DEM START
# --------------------------------------------------

else:

    links, rechts = st.columns([4, 1])

    with links:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=145)

        st.title("LerchnoLimit")
        st.markdown("**Deine Zukunft. Deine Möglichkeiten.**")

    with rechts:
        if st.button("← Startseite"):
            st.session_state.show_dashboard = False
            st.rerun()

    st.info(
        "Rein virtuelle Lern- und Demo-Anwendung. "
        "Es werden keine echten Käufe oder Verkäufe ausgeführt. "
        "Gewinne sind nicht garantiert."
    )

    st.subheader("Virtuelles Markt-Dashboard")

    ticker = st.text_input(
        "Aktien-Symbol",
        value="AAPL"
    ).upper().strip()

    capital = st.number_input(
        "Virtuelles Startkapital in Euro",
        min_value=1.0,
        value=50.0,
        step=5.0
    )

    if st.button("Marktdaten laden"):

        with st.spinner("Lou lädt die Marktdaten ..."):

            try:
                data = yf.download(
                    ticker,
                    period="1y",
                    interval="1d",
                    auto_adjust=True,
                    progress=False
                )

                if data.empty:
                    st.error("Keine Marktdaten gefunden.")
                    st.stop()

                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.get_level_values(0)

                data = data.dropna(subset=["Close"]).copy()

                data["SMA20"] = data["Close"].rolling(20).mean()
                data["SMA50"] = data["Close"].rolling(50).mean()

                data = data.dropna().copy()

                if data.empty:
                    st.error("Nicht genügend Daten vorhanden.")
                    st.stop()

                data["Tagesrendite"] = (
                    data["Close"].pct_change().fillna(0)
                )

                data["Signal"] = (
                    data["SMA20"] > data["SMA50"]
                ).astype(int)

                data["Einsatz"] = data["Signal"] * 0.5

                data["StrategieRendite"] = (
                    data["Tagesrendite"]
                    * data["Einsatz"].shift(1).fillna(0)
                )

                data["VirtuellesKapital"] = (
                    capital
                    * (1 + data["StrategieRendite"]).cumprod()
                )

                latest_price = float(data["Close"].iloc[-1])
                final_capital = float(
                    data["VirtuellesKapital"].iloc[-1]
                )

                st.subheader("Deine Übersicht")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Letzter Kurs",
                    f"{latest_price:.2f}"
                )

                col2.metric(
                    "Startkapital",
                    f"{capital:.2f} €"
                )

                col3.metric(
                    "Virtueller Kontostand",
                    f"{final_capital:.2f} €",
                    f"{final_capital - capital:+.2f} €"
                )

                st.subheader("Virtuelle Kapitalentwicklung")

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["VirtuellesKapital"],
                        mode="lines",
                        name="Virtuelles Kapital",
                        line=dict(
                            color="#FF4DA6",
                            width=3
                        )
                    )
                )

                fig.update_layout(
                    paper_bgcolor="rgba(8,6,8,0.25)",
                    plot_bgcolor="rgba(8,6,8,0.25)",
                    font=dict(color="white"),
                    xaxis=dict(
                        title="Datum",
                        gridcolor="rgba(255,77,166,0.18)"
                    ),
                    yaxis=dict(
                        title="Virtuelles Kapital (€)",
                        gridcolor="rgba(255,77,166,0.18)"
                    ),
                    margin=dict(l=20, r=20, t=30, b=20)
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.caption(
                    "Vereinfachte historische Simulation. "
                    "Keine Anlageempfehlung und keine Vorhersage "
                    "zukünftiger Ergebnisse."
                )

            except Exception as error:
                st.error(
                    f"Fehler beim Laden: {error}"
                )

    st.markdown("---")

    st.markdown(
        "<center style='color:#FF4DA6;'>"
        "LerchnoLimit · Deine Zukunft. Deine Möglichkeiten."
        "</center>",
        unsafe_allow_html=True
    )
