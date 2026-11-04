import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="LerchnoLimit",
    page_icon="🍄",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #080608;
    color: white;
}
h1, h2, h3, p, label {
    color: #FF4DA6 !important;
}
.stButton button {
    background: #FF4DA6;
    color: black;
    border: 1px solid #FF4DA6;
    border-radius: 12px;
    font-weight: bold;
}
[data-testid="stMetricValue"] {
    color: #FF4DA6;
}
</style>
""", unsafe_allow_html=True)

st.image("file_000000006f2c81f5a5097c657e3366d1.png", width=350)
st.title("🍄 LerchnoLimit")
st.subheader("Deine Zukunft. Deine Möglichkeiten.")

st.markdown("### 🖤 Dein virtuelles Trading-Dashboard")

startkapital = 50.00

st.info(
    "Demomodus: Alle Berechnungen sind virtuell. "
    "Es werden keine echten Trades ausgeführt."
)

aktie = st.text_input("Aktien-Symbol", "AAPL")

if st.button("Virtuelle Analyse starten"):
    with st.spinner("Lade Marktdaten ..."):
        daten = yf.download(
            aktie,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

    if daten.empty:
        st.error("Keine Daten gefunden. Bitte Symbol prüfen.")
    else:
        if isinstance(daten.columns, pd.MultiIndex):
            kurs = daten["Close"].iloc[:, 0]
        else:
            kurs = daten["Close"]

        kurs = kurs.dropna()

        sma20 = kurs.rolling(20).mean()
        sma50 = kurs.rolling(50).mean()

        kapital = startkapital
        werte = []

        for i in range(1, len(kurs)):
            if pd.notna(sma20.iloc[i-1]) and pd.notna(sma50.iloc[i-1]):
                if sma20.iloc[i-1] > sma50.iloc[i-1]:
                    rendite = kurs.iloc[i] / kurs.iloc[i-1] - 1
                    kapital *= (1 + rendite * 0.5)

            werte.append(kapital)

        endkapital = werte[-1] if werte else startkapital

        st.markdown("### 💗 Dein virtuelles Ergebnis")

        c1, c2, c3 = st.columns(3)

        c1.metric("Startkapital", f"{startkapital:.2f} €")
        c2.metric("Virtuelles Kapital", f"{endkapital:.2f} €")
        c3.metric("Virtueller Gewinn", f"{endkapital-startkapital:+.2f} €")

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=kurs.index,
            y=kurs.values,
            name="Aktienkurs",
            line=dict(color="#FF4DA6", width=2)
        ))

        fig.add_trace(go.Scatter(
            x=sma20.index,
            y=sma20.values,
            name="SMA 20",
            line=dict(color="#FFFFFF", width=1)
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#080608",
            plot_bgcolor="#100509",
            font=dict(color="#FF4DA6"),
            title="LerchnoLimit – Marktverlauf"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Historische Daten sind keine Garantie für zukünftige Ergebnisse."
        )

st.divider()
st.caption("👑 LerchnoLimit | Virtuelle Testversion")
st.caption("Keine Anlageberatung. Kein echtes Trading.")
