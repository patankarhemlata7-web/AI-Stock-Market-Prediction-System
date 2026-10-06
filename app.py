import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import joblib

from api.stock_api import fetch_stock_data
from database.mysql_connection import engine
from streamlit_autorefresh import st_autorefresh

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="AI Stock Market Prediction",
    page_icon="📈",
    layout="wide"
)

# Refresh data every 30 seconds
st_autorefresh(interval=30000, key="datarefresh")
# ==================================================
# GLOBAL CSS
# ==================================================

st.markdown("""
<style>
.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F52BA, #1E90FF);
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.dashboard-title {
    color: #252A38;
    font-size: clamp(25px, 2.3vw, 36px);
    font-weight: 750;
    line-height: 1.2;
    white-space: nowrap;
    margin: 0 0 5px 0;
}
.dashboard-subtitle {
    color: #858995;
    font-size: 15px;
    margin: 0 0 18px 0;
}
.kpi-card {
    min-height: 132px;
    height: 132px;
    padding: 16px 8px;
    border-radius: 16px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 14px rgba(0,0,0,0.16);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.kpi-card h4 {
    font-size: clamp(12px, 1.05vw, 16px);
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
    margin: 0 0 15px 0;
}
.kpi-card h2 {
    font-size: clamp(19px, 1.65vw, 27px);
    font-weight: 700;
    line-height: 1.15;
    white-space: nowrap;
    margin: 0;
}
.green { background: linear-gradient(135deg, #00b09b, #96c93d); }
.blue { background: linear-gradient(135deg, #2193b0, #6dd5ed); }
.orange { background: linear-gradient(135deg, #f7971e, #ffd200); }
.purple { background: linear-gradient(135deg, #8e2de2, #4a00e0); }
.red { background: linear-gradient(135deg, #ff416c, #ff4b2b); }
.main-title {
    text-align: center;
    font-size: clamp(28px, 3vw, 42px);
    font-weight: 750;
    color: #0F52BA;
    line-height: 1.2;
}
.sub-title {
    text-align: center;
    color: gray;
    font-size: 17px;
}
@media (max-width: 1100px) {
    .dashboard-title { white-space: normal; }
    .kpi-card {
        min-height: 118px;
        height: 118px;
        padding: 12px 5px;
    }
}
</style>
""", unsafe_allow_html=True)
# ==================================================
# LOGIN SESSION
# ==================================================

# ==================================================
# LOGIN SESSION
# ==================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login_page():

    st.markdown(
        "<h1 class='main-title'>📈 AI Stock Market Prediction System</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p class='sub-title'>Secure Login Portal</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    username = st.text_input("👤 Username")

    password = st.text_input(
        "🔑 Password",
        type="password"
    )

    if st.button(
        "Login",
        width="stretch"
    ):

        if username == "admin" and password == "admin123":

            st.session_state.logged_in = True
            st.rerun()

        else:

            st.error(
                "Invalid Username or Password"
            )

if not st.session_state.logged_in:
    login_page()
    st.stop()
# ==================================
# LOAD DATA
# ==================================

@st.cache_data(ttl=300)
def load_data():

    try:
        query = "SELECT * FROM stock_data"
        df = pd.read_sql(query, con=engine)

        if df.empty:
            df = fetch_stock_data()

        return df

    except:
        return fetch_stock_data()

df = load_data()

if df is None or df.empty:
    st.error("No Data Available")
    st.stop()

if "signal" not in df.columns:
    df["signal"] = np.where(
        df["close"] > df["open"],
        "BUY",
        "SELL"
    )





# ==================================
# SIDEBAR
# ==================================

st.sidebar.markdown("""
<h2 style='text-align:center;color:white;'>
📌 Dashboard Filters
</h2>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 Logout", width="stretch"):
    st.session_state.logged_in = False
    st.rerun()

st.sidebar.divider()

company = st.sidebar.selectbox(
    "🏢 Company",
    ["All Companies"] + sorted(df["company"].unique())
)

signal = st.sidebar.selectbox(
    "📈 Signal Type",
    ["All Signals"] + sorted(df["signal"].unique())
)

price_range = st.sidebar.slider(
    "💰 Price Range",
    int(df["close"].min()),
    int(df["close"].max()),
    (
        int(df["close"].min()),
        int(df["close"].max())
    )
)

theme = st.sidebar.selectbox(
    "🎨 Chart Theme",
    ["plotly", "plotly_dark", "ggplot2"]
)

st.sidebar.divider()

nse_count = df[df["exchange"]=="NSE"]["company"].nunique()
bse_count = df[df["exchange"]=="BSE"]["company"].nunique()

st.sidebar.markdown("### 📊 Market Summary")
st.sidebar.success(f"NSE Companies : {nse_count}")
st.sidebar.info(f"BSE Companies : {bse_count}")
st.sidebar.warning(f"Total Companies : {df['company'].nunique()}")

# ==================================
# FILTER DATA
# ==================================
filtered = df.copy()

if company != "All Companies":
    filtered = filtered[
        filtered["company"] == company
    ]

if signal != "All Signals":
    filtered = filtered[
        filtered["signal"] == signal
    ]

filtered = filtered[
    (filtered["close"] >= price_range[0]) &
    (filtered["close"] <= price_range[1])
]

if filtered.empty:
    st.warning("No records match the selected filters. Please change the filters.")
    st.stop()

# ==================================
# HEADER
# ==================================

st.markdown(
    "<h1 class='dashboard-title'>📈 AI Stock Market Prediction System</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p class='dashboard-subtitle'>Comprehensive Stock Market Analysis & AI Prediction System</p>",
    unsafe_allow_html=True
)

# ==================================
# KPI CARDS
# ==================================

companies = filtered["company"].nunique()

volume = round(
    filtered["volume"].sum()/1000000,
    2
)

pe_ratio = round(
    filtered["close"].mean()/10,
    2
)

de_ratio = round(
    filtered["close"].mean()/100,
    2
)

portfolio = round(
    filtered["close"].sum(),
    2
)

c1,c2,c3,c4,c5 = st.columns(5)

with c1:
    st.markdown(
        f"""
        <div class="kpi-card green">
        <h4>Companies</h4>
        <h2>{companies}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div class="kpi-card blue">
        <h4>Volume</h4>
        <h2>{volume}M</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        f"""
        <div class="kpi-card orange">
        <h4>P/E Ratio</h4>
        <h2>{pe_ratio}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with c4:
    st.markdown(
        f"""
        <div class="kpi-card purple">
        <h4>D/E Ratio</h4>
        <h2>{de_ratio}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

with c5:
    st.markdown(
        f"""
        <div class="kpi-card red">
        <h4>Portfolio</h4>
        <h2>₹{portfolio:,.0f}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    # ==================================
# TABS
# ==================================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Dashboard",
        "📈 Charts",
        "📋 Dataset",
        "🎯 Prediction",
        "💼 Portfolio"
    ]
)

# ==================================
# DASHBOARD TAB
# ==================================

with tab1:

    c1, c2 = st.columns(2)

    volume_df = (
        filtered.groupby("company")["volume"]
        .sum()
        .reset_index()
    )

    fig1 = px.pie(
        volume_df,
        names="company",
        values="volume",
        title="Company Market Share",
        template=theme
    )

    c1.plotly_chart(
        fig1,
        width="stretch"
    )

    fig2 = px.bar(
        volume_df,
        x="company",
        y="volume",
        color="company",
        title="Trading Volume",
        template=theme
    )

    c2.plotly_chart(
        fig2,
        width="stretch"
    )

# ==================================
# CHARTS TAB
# ==================================

with tab2:

    st.subheader("📈 Advanced Charts")

    col1, col2 = st.columns(2)

    # Pie Chart
    volume_df = (
        filtered.groupby("company")["volume"]
        .sum()
        .reset_index()
    )

    fig3 = px.pie(
        volume_df,
        names="company",
        values="volume",
        title="Volume Distribution",
        hole=0.4,
        template=theme
    )

    col1.plotly_chart(
        fig3,
        width="stretch"
    )

    # Bubble Chart
    fig4 = px.scatter(
        filtered,
        x="open",
        y="close",
        size="volume",
        color="company",
        hover_name="company",
        title="Open vs Close Bubble Analysis",
        template=theme
    )

    col2.plotly_chart(
        fig4,
        width="stretch"
    )
# ==================================
# DATASET TAB
# ==================================

with tab3:

    st.subheader("Dataset")

    st.dataframe(
        filtered,
        width="stretch"
    )

    csv = filtered.to_csv(
        index=False
    )

    st.download_button(
        "⬇ Download Dataset",
        csv,
        "stock_data.csv",
        "text/csv"
    )

# ==================================
# PREDICTION TAB
# ==================================

with tab4:

    st.subheader(
        "AI Stock Prediction"
    )

    model_name = st.selectbox(
        "Select Model",
        [
            "Linear Regression",
            "Random Forest",
            "XGBoost"
        ]
    )

    try:

        if model_name == "Linear Regression":
            model = joblib.load(
                "models/linear_model.pkl"
            )

        elif model_name == "Random Forest":
            model = joblib.load(
                "models/random_forest.pkl"
            )

        else:
            model = joblib.load(
                "models/xgboost_model.pkl"
            )

        latest = filtered.tail(1)

        X = latest[
            [
                "open",
                "high",
                "low",
                "volume"
            ]
        ]

        prediction = model.predict(X)[0]

        actual_price = float(
            latest["close"].iloc[0]
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Actual Price",
            f"₹ {actual_price:.2f}"
        )

        c2.metric(
            "Predicted Price",
            f"₹ {prediction:.2f}"
        )

        chart_df = pd.DataFrame(
            {
                "Type": [
                    "Actual",
                    "Predicted"
                ],
                "Price": [
                    actual_price,
                    prediction
                ]
            }
        )

        fig5 = px.bar(
            chart_df,
            x="Type",
            y="Price",
            color="Type",
            title="Actual vs Predicted Price",
            template=theme
        )

        st.plotly_chart(
            fig5,
            width="stretch"
        )

    except Exception as e:

        st.error(
            f"Model Error: {e}"
        )

# ==================================
# PORTFOLIO TAB
# ==================================

with tab5:

    st.subheader("💼 Portfolio Analysis")

    portfolio_df = (
        filtered.groupby("company")
        .agg(
            quantity=("company","count"),
            buy_price=("open","mean"),
            current_price=("close","mean")
        )
        .reset_index()
    )

    portfolio_df["profit_loss"] = (
        portfolio_df["current_price"]
        -
        portfolio_df["buy_price"]
    ) * portfolio_df["quantity"]

    st.dataframe(
        portfolio_df,
        width="stretch"
    )

    fig = px.bar(
        portfolio_df,
        x="company",
        y="profit_loss",
        color="profit_loss",
        title="Company Wise Profit/Loss",
        template=theme
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    total_profit = round(
        portfolio_df["profit_loss"].sum(),
        2
    )

    st.metric(
        "Total Profit / Loss",
        f"₹ {total_profit:,.2f}"
    )

