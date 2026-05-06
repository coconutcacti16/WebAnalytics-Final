# Hannah Huang
# absa_pipeline.py
# Runs aspect-based sentiment analysis on F1 Reddit post titles
# and creates dashboard-ready CSV outputs

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from advanced_sentiment_analysis import AdvancedSentimentAnalyzer


# Categorize each aspect into a broader dashboard bucket
def categorize_aspect(aspect):
    if aspect in ["win", "pole", "podium", "pace", "overtake"]:
        return "Performance"
    elif aspect in ["crash", "penalty", "disqualification", "retirement"]:
        return "Risk"
    elif aspect in ["driver", "team", "livery", "media", "hype"]:
        return "Brand"
    else:
        return "Commercial"


def main():
    # Load the CSV file
    df = pd.read_csv("F1_2025_Reddit_Data.csv")

    # Clean up column names just in case
    df.columns = df.columns.str.strip()

    # Convert Upvotes to numeric
    # This helps if values include commas or text
    df["Upvotes"] = (
        df["Upvotes"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("K", "", regex=False)
    )

    df["Upvotes"] = pd.to_numeric(df["Upvotes"], errors="coerce").fillna(0)

    # Initialize the analyzer
    analyzer = AdvancedSentimentAnalyzer()

    # Option C: hybrid aspect schema
    aspects = [
        "win", "pole", "podium", "pace", "overtake",
        "crash", "penalty", "disqualification", "retirement",
        "driver", "team", "livery", "media", "hype",
        "merchandise", "promotion", "price"
    ]

    rows = []

    # Normalize upvotes so one viral post does not dominate everything
    max_upvotes = df["Upvotes"].max()
    if max_upvotes == 0:
        max_upvotes = 1

    # Run ABSA for each Reddit title
    for _, row in df.iterrows():
        race = row["Race"]
        subreddit = row["Subreddit"]
        title = str(row["Title"])
        upvotes = row["Upvotes"]

        absa_result = analyzer.aspect_based_sentiment_analysis(title, aspects)

        for aspect, data in absa_result.items():
            polarity = data["average_polarity"]
            sentiment = data["overall_sentiment"]

            # Normalize upvotes to a 0-1 scale
            normalized_upvotes = upvotes / max_upvotes

            # Weighted score for dashboard use
            weighted_score = polarity * normalized_upvotes

            rows.append({
                "Race": race,
                "Subreddit": subreddit,
                "Title": title,
                "Aspect": aspect,
                "Category": categorize_aspect(aspect),
                "Sentiment": sentiment,
                "Polarity": polarity,
                "Upvotes": upvotes,
                "Normalized_Upvotes": normalized_upvotes,
                "Weighted_Score": weighted_score
            })

    # Create detailed ABSA output
    absa_df = pd.DataFrame(rows)
    absa_df.to_csv("absa_detailed_output.csv", index=False)

    # Race + aspect summary
    race_summary = absa_df.groupby(["Race", "Aspect"], as_index=False).agg({
        "Polarity": "mean",
        "Weighted_Score": "sum",
        "Upvotes": "sum"
    })
    race_summary.to_csv("race_summary.csv", index=False)

    # Race + category summary
    category_summary = absa_df.groupby(["Race", "Category"], as_index=False).agg({
        "Weighted_Score": "sum"
    })
    category_summary.to_csv("category_summary.csv", index=False)

    # Dashboard-ready race scores
    def score_race(group):
        hype_score = group[group["Aspect"].isin(
            ["win", "podium", "driver", "team", "hype"]
        )]["Weighted_Score"].sum()

        controversy_score = group[group["Aspect"].isin(
            ["penalty", "crash", "disqualification"]
        )]["Weighted_Score"].abs().sum()

        performance_score = group[group["Aspect"].isin(
            ["win", "pole", "pace", "overtake"]
        )]["Weighted_Score"].sum()

        return pd.Series({
            "Hype_Score": hype_score,
            "Controversy_Score": controversy_score,
            "Performance_Score": performance_score,
            "Demand_Score": hype_score + controversy_score
        })

    race_scores = absa_df.groupby("Race").apply(score_race).reset_index()
    race_scores.to_csv("race_scores.csv", index=False)

    # ----------------------------
    # Charts
    # ----------------------------

    # Chart 1: Demand Score by Race
    plt.figure(figsize=(12, 6))
    plt.plot(race_scores["Race"], race_scores["Demand_Score"], marker="o")
    plt.xticks(rotation=90)
    plt.title("Demand Signal by Race Weekend")
    plt.tight_layout()
    plt.savefig("demand_signal_by_race.png")
    plt.close()

    # Chart 2: Hype vs Controversy
    plt.figure(figsize=(8, 6))
    plt.scatter(race_scores["Hype_Score"], race_scores["Controversy_Score"])

    for _, row in race_scores.iterrows():
        plt.text(row["Hype_Score"], row["Controversy_Score"], row["Race"], fontsize=8)

    plt.xlabel("Hype Score")
    plt.ylabel("Controversy Score")
    plt.title("Race Positioning: Hype vs Controversy")
    plt.tight_layout()
    plt.savefig("hype_vs_controversy.png")
    plt.close()

    # Chart 3: Average Sentiment by Aspect
    aspect_avg = absa_df.groupby("Aspect")["Polarity"].mean().sort_values()

    plt.figure(figsize=(10, 6))
    aspect_avg.plot(kind="barh")
    plt.title("Average Sentiment by Aspect")
    plt.tight_layout()
    plt.savefig("average_sentiment_by_aspect.png")
    plt.close()

    print("ABSA pipeline complete.")
    print("Created files:")
    print("- absa_detailed_output.csv")
    print("- race_summary.csv")
    print("- category_summary.csv")
    print("- race_scores.csv")
    print("- demand_signal_by_race.png")
    print("- hype_vs_controversy.png")
    print("- average_sentiment_by_aspect.png")


main()