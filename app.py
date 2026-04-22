import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="F1 Reddit Demand Dashboard", layout="wide")

@st.cache_data
def load_data():
    race_scores = pd.read_csv("race_scores.csv")
    category_summary = pd.read_csv("category_summary.csv")
    race_summary = pd.read_csv("race_summary.csv")
    return race_scores, category_summary, race_summary

race_scores, category_summary, race_summary = load_data()

st.title("2025 F1 Reddit Sentiment & Demand Dashboard")
st.write(
    "A simple dashboard using ABSA-derived demand signals from top Reddit posts by race weekend."
)

# Sidebar
race_list = ["All"] + sorted(race_scores["Race"].dropna().unique().tolist())
selected_race = st.sidebar.selectbox("Select Race", race_list)

if selected_race != "All":
    race_scores_filtered = race_scores[race_scores["Race"] == selected_race]
    category_filtered = category_summary[category_summary["Race"] == selected_race]
    race_summary_filtered = race_summary[race_summary["Race"] == selected_race]
else:
    race_scores_filtered = race_scores.copy()
    category_filtered = category_summary.copy()
    race_summary_filtered = race_summary.copy()

# Top metrics
col1, col2, col3 = st.columns(3)

col1.metric(
    "Max Demand Score",
    round(race_scores["Demand_Score"].max(), 3)
)

col2.metric(
    "Highest Hype Race",
    race_scores.loc[race_scores["Hype_Score"].idxmax(), "Race"]
)

col3.metric(
    "Highest Controversy Race",
    race_scores.loc[race_scores["Controversy_Score"].idxmax(), "Race"]
)

st.subheader("Demand Signal by Race")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(race_scores["Race"], race_scores["Demand_Score"], marker="o")
ax1.set_title("Demand Signal by Race Weekend")
ax1.tick_params(axis="x", rotation=90)
st.pyplot(fig1)

st.subheader("Hype vs Controversy")
fig2, ax2 = plt.subplots(figsize=(8, 5))
ax2.scatter(race_scores["Hype_Score"], race_scores["Controversy_Score"])

for _, row in race_scores.iterrows():
    ax2.text(row["Hype_Score"], row["Controversy_Score"], row["Race"], fontsize=8)

ax2.set_xlabel("Hype Score")
ax2.set_ylabel("Controversy Score")
ax2.set_title("Race Positioning: Hype vs Controversy")
st.pyplot(fig2)

st.subheader("Category Breakdown")

if selected_race == "All":
    cat_pivot = category_summary.pivot(index="Race", columns="Category", values="Weighted_Score").fillna(0)
    fig3, ax3 = plt.subplots(figsize=(12, 5))
    cat_pivot.plot(kind="bar", stacked=True, ax=ax3)
    ax3.set_title("Category Breakdown by Race")
    ax3.tick_params(axis="x", rotation=90)
    st.pyplot(fig3)
else:
    st.dataframe(category_filtered, use_container_width=True)

st.subheader("Aspect Summary")
st.dataframe(race_summary_filtered, use_container_width=True)