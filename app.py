
import base64
from pathlib import Path

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go


# --------------------------------------------------
# SEITENEINSTELLUNGEN
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "file_000000006f2c81f5a5097c657e3366d1.png"

st.set_page_config(
    page_title="LerchnoLimit",
    page_icon=str(LOGO_PATH),
    layout="wide"
)

BACKGROUND_PATH = BASE_DIR / "file_000000006b8081f4bbe2c991f86ba04a.png"


# --------------------------------------------------
# DESIGN: SCHWARZ UND NEONPINK
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background: #080608;
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.stButton > button {
    background-color: #FF4DA6;
    color: #080608;
    border: none;
    border-radius: 12px;
    font-weight: bold;
}

[data-testid="stMetricValue"] {
    color: #FF4DA6;
}

[data-testid="stHeader"] {
    background: #080608;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# LOGO UND TITEL
# --------------------------------------------------

if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=300)
else:
    st.warning("Logo-Datei wurde nicht gefunden.")

st.title("LerchnoLimit")
st.markdown("**Deine Zukunft. Deine Möglichkeiten.**")
st.markdown("---")


# --------------------------------------------------
# SICHERHEITSHINWEIS
# --------------------------------------------------

st.info(
    "Dies ist eine rein virtuelle Lern- und Demo-Anwendung. "
    "Es werden keine echten Käufe oder Verkäufe ausgeführt. "
    "Gewinne sind nicht garantiert."
)


# --------------------------------------------------
# EINGABEN
# --------------------------------------------------

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

    with st.spinner("Lade Marktdaten ..."):

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

            # Falls yfinance mehrere Spaltenebenen liefert
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            data = data.dropna(subset=["Close"]).copy()

            data["SMA20"] = data["Close"].rolling(20).mean()
            data["SMA50"] = data["Close"].rolling(50).mean()

            data = data.dropna().copy()

            if data.empty:
                st.error("Nicht genügend Daten für die Berechnung.")
                st.stop()

            # --------------------------------------------------
            # VIRTUELLE BEISPIEL-KAPITALKURVE
            # --------------------------------------------------

            data["Tagesrendite"] = data["Close"].pct_change().fillna(0)

            data["Signal"] = (
                data["SMA20"] > data["SMA50"]
            ).astype(int)

            # Nur beispielhaft: maximal 50 % virtuelles Kapital
            data["Einsatz"] = data["Signal"] * 0.5

            data["StrategieRendite"] = (
                data["Tagesrendite"] * data["Einsatz"].shift(1).fillna(0)
            )

            data["VirtuellesKapital"] = (
                capital * (1 + data["StrategieRendite"]).cumprod()
            )

            # --------------------------------------------------
            # KENNZAHLEN
            # --------------------------------------------------

            latest_price = float(data["Close"].iloc[-1])
            final_capital = float(data["VirtuellesKapital"].iloc[-1])

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

            # --------------------------------------------------
            # CHART MIT DEINEM HINTERGRUNDBILD
            # --------------------------------------------------

            st.subheader("Virtuelle Kapitalentwicklung")

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=data.index,
                y=data["VirtuellesKapital"],
                mode="lines",
                name="Virtuelles Kapital",
                line=dict(
                    color="#FF4DA6",
                    width=3
                )
            ))

            # Hintergrundbild hinter der Kurve
            if BACKGROUND_PATH.exists():

                image_bytes = BACKGROUND_PATH.read_bytes()

                encoded_image = base64.b64encode(
                    image_bytes
                ).decode("utf-8")

                image_source = (
                    "data:image/png;base64," + encoded_image
                )

                fig.add_layout_image(
                    dict(
                        source=image_source,
                        xref="paper",
                        yref="paper",
                        x=0,
                        y=1,
                        sizex=1,
                        sizey=1,
                        sizing="stretch",
                        opacity=0.28,
                        layer="below"
                    )
                )

            fig.update_layout(
                paper_bgcolor="#080608",
                plot_bgcolor="rgba(8,6,8,0)",
                font=dict(color="white"),
                xaxis=dict(
                    title="Datum",
                    gridcolor="rgba(255,77,166,0.18)"
                ),
                yaxis=dict(
                    title="Virtuelles Kapital (€)",
                    gridcolor="rgba(255,77,166,0.18)"
                ),
                legend=dict(
                    font=dict(color="white")
                ),
                margin=dict(l=20, r=20, t=30, b=20)
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.caption(
                "Die Kurve ist eine vereinfachte historische Simulation. "
                "Sie ist keine Anlageempfehlung und sagt nichts über "
                "zukünftige Ergebnisse aus."
            )

        except Exception as error:
            st.error(
                f"Beim Laden ist ein Fehler aufgetreten: {error}"
            )


# --------------------------------------------------
# ABSCHLUSS
# --------------------------------------------------

st.markdown("---")
st.markdown(
    "<center style='color:#FF4DA6;'>"
    "LerchnoLimit · Deine Zukunft. Deine Möglichkeiten."
    "</center>",
    unsafe_allow_html=True
)
