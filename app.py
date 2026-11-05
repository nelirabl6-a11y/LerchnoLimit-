
from pathlib import Path
from datetime import datetime

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# ==========================================
# LERCHNOLIMIT
# Virtuelle Trading- und Lernplattform
# ==========================================

BASE_DIR = Path(__file__).parent

LOGO_PATH = BASE_DIR / "file_000000006f2c81f5a5097c657e3366d1.png"
BACKGROUND_PATH = BASE_DIR / "file_000000006b8081f4bbe2c991f86ba04a.png"

st.set_page_config(
    page_title="LerchnoLimit",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🍄",
    layout="wide"
)

# ==========================================
# DESIGN
# ==========================================

st.markdown("""
<style>
:root {
    --pink: #FF4DA6;
    --black: #080608;
}

.stApp {
    background: #080608;
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

.hero {
    padding: 4rem 2rem;
    border-radius: 24px;
    text-align: center;
    background:
        linear-gradient(
            180deg,
            rgba(8,6,8,.35),
            rgba(8,6,8,.94)
        ),
        url("file_000000006b8081f4bbe2c991f86ba04a.png");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(255,77,166,.65);
    box-shadow: 0 0 28px rgba(255,77,166,.18);
}

.neon {
    color: #FF4DA6 !important;
    text-shadow: 0 0 14px rgba(255,77,166,.8);
}

.stButton > button {
    background: linear-gradient(
        135deg,
        #351027,
        #FF4DA6
    ) !important;
    color: white !important;
    border: 1px solid #FF4DA6 !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    transition: all .2s ease !important;
}

.stButton > button:hover {
    transform: scale(1.035) translateY(-2px);
    box-shadow: 0 0 22px rgba(255,77,166,.65);
}

[data-testid="stImage"] img {
    border: 3px solid #080608;
    outline: 2px solid #FF4DA6;
    border-radius: 22px;
    padding: 4px;
    background: #080608;
    box-shadow: 0 0 22px rgba(255,77,166,.45);
}

.notice {
    border: 1px solid #FF4DA6;
    border-radius: 12px;
    padding: 12px 16px;
    background: rgba(255,77,166,.08);
}
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
        symbol,
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False
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

    if values.empty:
        return None

    return float(values.iloc[-1])


def money(value):

    return (
        f"€ {value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ==========================================
# DEPOTWERT
# ==========================================

def portfolio_value():

    total = float(st.session_state.cash)

    for symbol, position in st.session_state.positions.items():

        price = latest_price(symbol)

        if price is not None:
            total += position["shares"] * price

    return total


# ==========================================
# LOU – ANALYSEASSISTENT
# ==========================================

def render_lou_comment(symbol, data):

    if data.empty or len(data) < 50:

        st.info(
            "Lou: Für eine Einschätzung brauche ich mehr Kursdaten."
        )

        return

    close = data["Close"].dropna()

    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1]

    last = float(close.iloc[-1])

    if pd.isna(sma20) or pd.isna(sma50):

        st.info(
            "Lou: Die Trendindikatoren sind noch nicht vollständig."
        )

    elif last > sma20 > sma50:

        st.success(
            f"Lou: {symbol} liegt über SMA20 und SMA50. "
            "Das ist ein positives Trend-Signal, "
            "aber keine Kaufempfehlung."
        )

    elif last < sma20 < sma50:

        st.warning(
            f"Lou: {symbol} liegt unter SMA20 und SMA50. "
            "Das ist ein schwaches Trend-Signal."
        )

    else:

        st.info(
            f"Lou: {symbol} zeigt aktuell ein gemischtes Signal."
        )


# ==========================================
# DASHBOARD
# ==========================================

def show_dashboard():

    st.title("🍄 LerchnoLimit")

    st.caption(
        "Virtuelles Trading · echte Marktdaten · kein Echtgeld"
    )

    st.markdown(
        '<div class="notice">'
        'Alle Käufe und Verkäufe sind ausschließlich simuliert. '
        'Es werden keine echten Börsenorders gesendet.'
        '</div>',
        unsafe_allow_html=True
    )

    with st.sidebar:

        st.header("Dein virtuelles Depot")

        st.metric(
            "Freies virtuelles Kapital",
            money(st.session_state.cash)
        )

        st.caption("Startkapital: 10.000 €")

        if st.button(
            "Virtuelles Depot zurücksetzen",
            use_container_width=True
        ):

            st.session_state.cash = 10000.0
            st.session_state.positions = {}
            st.session_state.trades = []

            st.rerun()

    tabs = st.tabs([
        "📈 Markt & Lou",
        "💹 Virtuell traden",
        "🧾 Depot & Verlauf"
    ])

    # ======================================
    # MARKT & LOU
    # ======================================

    with tabs[0]:

        col1, col2 = st.columns([2, 1])

        with col1:

            symbol = st.text_input(
                "Börsenkürzel",
                value="AAPL"
            ).strip().upper()

            period_label = st.selectbox(
                "Zeitraum",
                [
                    "1 Monat",
                    "3 Monate",
                    "6 Monate",
                    "1 Jahr",
                    "2 Jahre",
                    "5 Jahre"
                ],
                index=3
            )

        periods = {
            "1 Monat": "1mo",
            "3 Monate": "3mo",
            "6 Monate": "6mo",
            "1 Jahr": "1y",
            "2 Jahre": "2y",
            "5 Jahre": "5y"
        }

        if symbol:

            with st.spinner("Marktdaten werden geladen ..."):

                data = load_market_data(
                    symbol,
                    periods[period_label]
                )

            if data.empty or "Close" not in data:

                st.error(
                    "Keine Kursdaten gefunden. "
                    "Bitte prüfe das Börsenkürzel."
                )

            else:

                close = data["Close"].dropna()

                current = float(close.iloc[-1])

                previous = (
                    float(close.iloc[-2])
                    if len(close) > 1
                    else current
                )

                change = current - previous

                with col2:

                    st.metric(
                        f"Letzter Kurs · {symbol}",
                        f"{current:,.2f}",
                        f"{change:+.2f}"
                    )

                data["SMA20"] = (
                    data["Close"].rolling(20).mean()
                )

                data["SMA50"] = (
                    data["Close"].rolling(50).mean()
                )

                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data["Close"],
                        name="Kurs",
                        line=dict(
                            color="#FF4DA6",
                            width=2
                        )
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data["SMA20"],
                        name="SMA 20",
                        line=dict(color="#FFFFFF")
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data["SMA50"],
                        name="SMA 50",
                        line=dict(color="#888888")
                    )
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#080608",
                    plot_bgcolor="#100509",
                    height=430
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                render_lou_comment(symbol, data)

                st.caption(
                    "Historische Indikatoren sind keine "
                    "Vorhersage zukünftiger Kurse."
                )

    # ======================================
    # VIRTUELLES TRADING
    # ======================================

    with tabs[1]:

        st.subheader("Virtuelle Order")

        st.write(
            "Teste Käufe und Verkäufe mit Spielgeld."
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            trade_symbol = st.text_input(
                "Kürzel",
                value="AAPL",
                key="trade_symbol"
            ).strip().upper()

        with c2:

            side = st.selectbox(
                "Aktion",
                ["Kaufen", "Verkaufen"]
            )

        with c3:

            shares = st.number_input(
                "Stückzahl",
                min_value=0.001,
                max_value=1000000.0,
                value=1.0,
                step=1.0
            )

        if trade_symbol:

            with st.spinner("Kurs wird geprüft ..."):

                price = latest_price(trade_symbol)

            if price is None:

                st.error("Kein Kurs abrufbar.")

            else:

                order_value = price * shares

                st.metric(
                    "Ungefährer Orderwert",
                    f"{order_value:,.2f} (Kurswährung)"
                )

                st.caption(
                    "Marktdaten können verzögert sein. "
                    "Es erfolgt keine Währungsumrechnung."
                )

                if side == "Kaufen":

                    if st.button(
                        "Virtuell kaufen",
                        type="primary",
                        use_container_width=True
                    ):

                        if order_value > st.session_state.cash:

                            st.error(
                                "Nicht genug virtuelles Guthaben."
                            )

                        else:

                            pos = st.session_state.positions.get(
                                trade_symbol,
                                {
                                    "shares": 0.0,
                                    "cost": 0.0
                                }
                            )

                            pos["shares"] += shares
                            pos["cost"] += order_value

                            st.session_state.positions[
                                trade_symbol
                            ] = pos

                            st.session_state.cash -= order_value

                            st.session_state.trades.insert(
                                0,
                                {
                                    "Zeit": datetime.now().strftime(
                                        "%d.%m.%Y %H:%M"
                                    ),
                                    "Kürzel": trade_symbol,
                                    "Aktion": "Kauf",
                                    "Stück": shares,
                                    "Kurs": price,
                                    "Wert": order_value
                                }
                            )

                            st.success(
                                "Virtueller Kauf ausgeführt."
                            )

                            st.rerun()

                else:

                    owned = st.session_state.positions.get(
                        trade_symbol,
                        {}
                    ).get("shares", 0.0)

                    st.caption(
                        f"Im Depot: {owned:g} Stück"
                    )

                    if st.button(
                        "Virtuell verkaufen",
                        type="primary",
                        use_container_width=True
                    ):

                        if shares > owned:

                            st.error(
                                "Nicht genügend Stücke vorhanden."
                            )

                        elif owned <= 0:

                            st.error(
                                "Diese Position ist nicht vorhanden."
                            )

                        else:

                            pos = st.session_state.positions[
                                trade_symbol
                            ]

                            proceeds = price * shares

                            remaining = owned - shares

                            pos["shares"] = remaining

                            if remaining <= 1e-9:

                                del st.session_state.positions[
                                    trade_symbol
                                ]

                            else:

                                st.session_state.positions[
                                    trade_symbol
                                ] = pos

                            st.session_state.cash += proceeds

                            st.session_state.trades.insert(
                                0,
                                {
                                    "Zeit": datetime.now().strftime(
                                        "%d.%m.%Y %H:%M"
                                    ),
                                    "Kürzel": trade_symbol,
                                    "Aktion": "Verkauf",
                                    "Stück": shares,
                                    "Kurs": price,
                                    "Wert": proceeds
                                }
                            )

                            st.success(
                                "Virtueller Verkauf ausgeführt."
                            )

                            st.rerun()

    # ======================================
    # DEPOT UND VERLAUF
    # ======================================

    with tabs[2]:

        st.subheader("Dein virtuelles Depot")

        rows = []
        total_market_value = 0.0

        for symbol, pos in st.session_state.positions.items():

            price = latest_price(symbol)

            if price is not None:

                value = pos["shares"] * price

                total_market_value += value

                rows.append({
                    "Kürzel": symbol,
                    "Stück": round(pos["shares"], 6),
                    "Letzter Kurs": round(price, 4),
                    "Marktwert": round(value, 2),
                    "Einstand gesamt": round(pos["cost"], 2),
                    "Unrealisierte Differenz": round(
                        value - pos["cost"],
                        2
                    )
                })

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Freies Guthaben",
            money(st.session_state.cash)
        )

        c2.metric(
            "Wert der Positionen",
            money(total_market_value)
        )

        c3.metric(
            "Depotwert gesamt",
            money(
                st.session_state.cash + total_market_value
            )
        )

        if rows:

            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Dein virtuelles Depot ist noch leer."
            )

        st.subheader("Letzte Transaktionen")

        if st.session_state.trades:

            st.dataframe(
                pd.DataFrame(st.session_state.trades),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.caption(
                "Noch keine virtuellen Trades."
            )

    st.divider()

    st.caption(
        "LerchnoLimit ist eine Lernsimulation. "
        "Keine Anlageberatung und keine Gewinnversprechen."
    )


# ==========================================
# STARTSEITE
# ==========================================

if not st.session_state.started:

    st.markdown(
        '<div class="hero">',
        unsafe_allow_html=True
    )

    if LOGO_PATH.exists():

        st.image(
            str(LOGO_PATH),
            width=230
        )

    else:

        st.markdown("🍄")

    st.markdown(
        '<h1 class="neon">LerchnoLimit</h1>',
        unsafe_allow_html=True
    )

    st.markdown(
        "### Deine Zukunft. Deine Möglichkeiten."
    )

    st.markdown(
        "**Dein virtueller Trading-Lernplatz mit Lou**"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    st.write("")

    _, center, _ = st.columns([1, 2, 1])

    with center:

        if st.button(
            "🚀 Jetzt starten",
            use_container_width=True
        ):

            st.session_state.started = True
            st.rerun()

    st.caption(
        "Echte, möglicherweise verzögerte Marktdaten · "
        "ausschließlich virtuelles Trading · kein Echtgeld"
    )

else:

    if st.button("← Zur Startseite"):

        st.session_state.started = False
        st.rerun()

    show_dashboard()
