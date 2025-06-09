import pandas as pd
import streamlit as st

# === PAGE CONFIG ===
st.set_page_config(page_title="Golf Dashboard", page_icon="⛳", layout="wide")

# === GOLF AESTHETIC ===
st.markdown(
    """
    <style>
    body {
        background-color: #f0f8f0;
    }
    .stApp {
        background-color: #e6f2e6;
    }
    h1, h2, h3 {
        color: #2c5f2d;
    }
    .stMetric {
        color: #1e441e;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === LOAD DATA ===
df = pd.read_csv("golf_stats.csv")

# === CLEANING ===
df["Penalty"] = pd.to_numeric(df["Penalty"], errors="coerce").fillna(0)
df["Putts"] = pd.to_numeric(df["Putts"], errors="coerce")
df["Scrambling"] = pd.to_numeric(df["Scrambling"], errors="coerce")
df["RoundID"] = df["Date"] + " - " + df["Course"]

# === CREATE TABS ===
tab1, tab2 = st.tabs(["📊 All Rounds Summary", "📅 Individual Round Viewer"])

# === TAB 1: ALL ROUNDS ===
with tab1:
    st.header("📊 All Rounds Summary")

    # Compute scores vs par for each round
    round_stats = df.groupby("RoundID").agg(
        total_score=("Score", "sum"),
        total_par=("Par", "sum")
    )
    round_stats["holes"] = df.groupby("RoundID")["Hole"].count()
    round_stats["over_par"] = round_stats["total_score"] - round_stats["total_par"]

    # Separate 9-hole and 18-hole rounds
    nine_hole_rounds = round_stats[round_stats["holes"] == 9]
    eighteen_hole_rounds = round_stats[round_stats["holes"] == 18]

    # Calculate averages
    avg_9hole_over_par = nine_hole_rounds["over_par"].mean()
    avg_18hole_over_par = eighteen_hole_rounds["over_par"].mean()

    # Display results
    st.subheader("⛳ Average Scores Over Par")
    col1, col2 = st.columns(2)
    col1.metric("9-hole Rounds", f"{'+' if avg_9hole_over_par >= 0 else ''}{avg_9hole_over_par:.0f}")
    col2.metric("18-hole Rounds", f"{'+' if avg_18hole_over_par >= 0 else ''}{avg_18hole_over_par:.0f}")

    st.subheader("🧠 Playing Stats")

    # GIR %
    gir_pct_all = df["GIR"].map({"Y": 1, "R": 0, "L": 0, "F": 0, "S": 0}).mean()
    avg_putts_all = df["Putts"].mean()
    drive_counts_all = df["Drive"].value_counts(normalize=True)
    gir_location_counts_all = df["GIR"].value_counts(normalize=True)

    scramble_valid_all = df["Scrambling"].dropna()
    scramble_pct_all = (scramble_valid_all == 1).sum() / len(scramble_valid_all) if len(scramble_valid_all) > 0 else 0

    penalties_by_round = df.groupby("RoundID")["Penalty"].mean()
    avg_penalties_all = penalties_by_round.mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("GIR %", f"{gir_pct_all:.0%}")
    col2.metric("Avg Putts", f"{avg_putts_all:.2f}")
    col3.metric("Scrambling %", f"{scramble_pct_all:.0%}")

    col4, _ = st.columns(2)
    col4.metric("Avg Penalties per Round", f"{avg_penalties_all:.2f}")

    st.subheader("🏌️ Drive Direction Breakdown (All Rounds)")
    st.bar_chart(drive_counts_all)

    st.subheader("🎯 GIR Location Breakdown (All Rounds)")
    st.bar_chart(gir_location_counts_all)

# === TAB 2: INDIVIDUAL ROUND VIEWER ===
with tab2:
    st.header("📅 Individual Round Viewer")

    st.sidebar.title("🏌️ Select Round")
    rounds = df["RoundID"].unique()
    selected_round = st.sidebar.selectbox("Round", rounds)
    df_round = df[df["RoundID"] == selected_round]

    # Round Score and Par
    round_score = df_round["Score"].sum()
    round_par = df_round["Par"].sum()
    score_diff = round_score - round_par
    st.subheader(f"Par / Score: {round_par} / {round_score} ({'+' if score_diff >= 0 else ''}{score_diff})")

    # Stats
    gir_pct = df_round["GIR"].map({"Y": 1, "R": 0, "L": 0, "F": 0, "S": 0}).mean()
    avg_putts = df_round["Putts"].mean()
    drive_counts = df_round["Drive"].value_counts(normalize=True)
    gir_location_counts = df_round["GIR"].value_counts(normalize=True)
    scramble_valid = df_round["Scrambling"].dropna()
    scramble_pct = (scramble_valid == 1).sum() / len(scramble_valid) if len(scramble_valid) > 0 else 0
    avg_penalties = df_round["Penalty"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("GIR %", f"{gir_pct:.0%}")
    col2.metric("Avg Putts", f"{avg_putts:.2f}")
    col3.metric("Scrambling %", f"{scramble_pct:.0%}")

    col4, _ = st.columns(2)
    col4.metric("Avg Penalties", f"{avg_penalties:.2f}")

    # Charts
    st.subheader("🏌️ Drive Direction Breakdown")
    st.bar_chart(drive_counts)

    st.subheader("🎯 GIR Location Breakdown")
    st.bar_chart(gir_location_counts)

    st.subheader("📈 Cumulative Over Par by Hole")
    df_round = df_round.copy()
    df_round["Over Par"] = df_round["Score"] - df_round["Par"]
    df_round["Cumulative Over Par"] = df_round["Over Par"].cumsum()
    st.line_chart(df_round.set_index("Hole")["Cumulative Over Par"])

    with st.expander("🔍 View Raw Data"):
        st.dataframe(df_round)
