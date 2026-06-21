from pathlib import Path
import logging
import re

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
REPORTS_DIR = Path("reports")
AI_OUTPUTS_DIR = REPORTS_DIR / "ai_outputs"
FIGURES_DIR = REPORTS_DIR / "figures"

AI_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MAX_REVIEWS_FOR_TFIDF = 100000

POSITIVE_WORDS = [
    "amazing",
    "beautiful",
    "clean",
    "comfortable",
    "convenient",
    "easy",
    "excellent",
    "friendly",
    "good",
    "great",
    "helpful",
    "lovely",
    "nice",
    "perfect",
    "quiet",
    "recommend",
    "spacious",
    "wonderful",
]

NEGATIVE_WORDS = [
    "bad",
    "broken",
    "cold",
    "dirty",
    "difficult",
    "disappointing",
    "hot",
    "issue",
    "late",
    "noisy",
    "poor",
    "problem",
    "rude",
    "small",
    "smell",
    "unclean",
    "uncomfortable",
    "unsafe",
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def clean_text(value):
    if pd.isna(value):
        return ""

    text = str(value).lower()
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def load_reviews():
    reviews_path = RAW_DIR / "reviews.csv.gz"

    if not reviews_path.exists():
        raise FileNotFoundError(f"Missing file: {reviews_path}")

    reviews = pd.read_csv(
        reviews_path,
        usecols=["listing_id", "id", "date", "comments"],
        low_memory=False,
    )

    reviews = reviews.rename(columns={"id": "review_id"})
    reviews["clean_comments"] = reviews["comments"].apply(clean_text)
    reviews = reviews[reviews["clean_comments"].str.len() >= 10].copy()

    return reviews


def load_listing_master():
    listing_master_path = PROCESSED_DIR / "listing_master.csv"

    if not listing_master_path.exists():
        raise FileNotFoundError(f"Missing file: {listing_master_path}")

    listing_master = pd.read_csv(listing_master_path, low_memory=False)

    selected_columns = [
        column
        for column in [
            "id",
            "neighbourhood_cleansed",
            "room_type",
            "review_scores_rating",
            "availability_365",
            "occupancy_rate_estimate",
        ]
        if column in listing_master.columns
    ]

    listing_master = listing_master[selected_columns].copy()
    listing_master = listing_master.rename(columns={"id": "listing_id"})

    return listing_master


def count_words(text, words):
    tokens = set(text.split())
    return sum(1 for word in words if word in tokens)


def add_sentiment_scores(reviews):
    reviews["positive_word_count"] = reviews["clean_comments"].apply(
        lambda text: count_words(text, POSITIVE_WORDS)
    )
    reviews["negative_word_count"] = reviews["clean_comments"].apply(
        lambda text: count_words(text, NEGATIVE_WORDS)
    )

    reviews["sentiment_score"] = (
        reviews["positive_word_count"] - reviews["negative_word_count"]
    )

    reviews["sentiment_label"] = "neutral"
    reviews.loc[reviews["sentiment_score"] > 0, "sentiment_label"] = "positive"
    reviews.loc[reviews["sentiment_score"] < 0, "sentiment_label"] = "negative"

    return reviews


def create_sentiment_summary(reviews):
    sentiment_summary = (
        reviews
        .groupby("sentiment_label")
        .agg(
            review_count=("review_id", "count"),
            average_sentiment_score=("sentiment_score", "mean"),
            average_positive_word_count=("positive_word_count", "mean"),
            average_negative_word_count=("negative_word_count", "mean"),
        )
        .reset_index()
        .sort_values("review_count", ascending=False)
    )

    total_reviews = sentiment_summary["review_count"].sum()
    sentiment_summary["review_share"] = sentiment_summary["review_count"] / total_reviews

    return sentiment_summary


def create_listing_sentiment(reviews, listing_master):
    listing_sentiment = (
        reviews
        .groupby("listing_id")
        .agg(
            review_count=("review_id", "count"),
            average_sentiment_score=("sentiment_score", "mean"),
            positive_reviews=("sentiment_label", lambda values: (values == "positive").sum()),
            negative_reviews=("sentiment_label", lambda values: (values == "negative").sum()),
            neutral_reviews=("sentiment_label", lambda values: (values == "neutral").sum()),
        )
        .reset_index()
    )

    listing_sentiment["positive_review_share"] = (
        listing_sentiment["positive_reviews"] / listing_sentiment["review_count"]
    )

    listing_sentiment["negative_review_share"] = (
        listing_sentiment["negative_reviews"] / listing_sentiment["review_count"]
    )

    listing_sentiment = listing_sentiment.merge(
        listing_master,
        on="listing_id",
        how="left",
    )

    return listing_sentiment


def create_grouped_sentiment(listing_sentiment, group_column):
    if group_column not in listing_sentiment.columns:
        return pd.DataFrame()

    grouped = (
        listing_sentiment
        .dropna(subset=[group_column])
        .groupby(group_column)
        .agg(
            listing_count=("listing_id", "count"),
            total_reviews=("review_count", "sum"),
            average_sentiment_score=("average_sentiment_score", "mean"),
            average_positive_review_share=("positive_review_share", "mean"),
            average_negative_review_share=("negative_review_share", "mean"),
        )
        .reset_index()
        .sort_values("total_reviews", ascending=False)
    )

    return grouped


def create_top_review_terms(reviews):
    tfidf_reviews = reviews[["clean_comments"]].copy()

    if len(tfidf_reviews) > MAX_REVIEWS_FOR_TFIDF:
        tfidf_reviews = tfidf_reviews.sample(MAX_REVIEWS_FOR_TFIDF, random_state=42)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50,
        min_df=20,
        max_df=0.80,
        ngram_range=(1, 2),
    )

    matrix = vectorizer.fit_transform(tfidf_reviews["clean_comments"])
    terms = vectorizer.get_feature_names_out()
    scores = matrix.mean(axis=0).A1

    top_terms = (
        pd.DataFrame(
            {
                "term": terms,
                "average_tfidf_score": scores,
            }
        )
        .sort_values("average_tfidf_score", ascending=False)
        .head(30)
    )

    return top_terms


def create_sentiment_distribution_figure(reviews):
    sentiment_counts = (
        reviews["sentiment_label"]
        .value_counts()
        .reset_index()
    )

    sentiment_counts.columns = ["sentiment_label", "review_count"]

    plt.figure(figsize=(8, 5))
    plt.bar(
        sentiment_counts["sentiment_label"],
        sentiment_counts["review_count"],
    )
    plt.title("Review Sentiment Distribution")
    plt.xlabel("Sentiment Label")
    plt.ylabel("Review Count")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "review_sentiment_distribution.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def create_top_terms_figure(top_terms):
    plot_df = top_terms.sort_values("average_tfidf_score", ascending=True).tail(15)

    plt.figure(figsize=(10, 6))
    plt.barh(
        plot_df["term"],
        plot_df["average_tfidf_score"],
    )
    plt.title("Top Review Terms by Average TF-IDF Score")
    plt.xlabel("Average TF-IDF Score")
    plt.ylabel("Review Term")
    plt.tight_layout()
    plt.savefig(
        FIGURES_DIR / "top_review_terms.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


def save_outputs(
    sentiment_summary,
    listing_sentiment,
    sentiment_by_neighbourhood,
    sentiment_by_room_type,
    top_terms,
):
    sentiment_summary.to_csv(
        AI_OUTPUTS_DIR / "review_sentiment_summary.csv",
        index=False,
    )

    listing_sentiment.to_csv(
        AI_OUTPUTS_DIR / "review_sentiment_by_listing.csv",
        index=False,
    )

    if not sentiment_by_neighbourhood.empty:
        sentiment_by_neighbourhood.to_csv(
            AI_OUTPUTS_DIR / "sentiment_by_neighbourhood.csv",
            index=False,
        )

    if not sentiment_by_room_type.empty:
        sentiment_by_room_type.to_csv(
            AI_OUTPUTS_DIR / "sentiment_by_room_type.csv",
            index=False,
        )

    top_terms.to_csv(
        AI_OUTPUTS_DIR / "top_review_terms.csv",
        index=False,
    )


def main():
    logging.info("Creating AI/NLP review analysis outputs")

    reviews = load_reviews()
    listing_master = load_listing_master()

    reviews = add_sentiment_scores(reviews)

    sentiment_summary = create_sentiment_summary(reviews)
    listing_sentiment = create_listing_sentiment(reviews, listing_master)

    sentiment_by_neighbourhood = create_grouped_sentiment(
        listing_sentiment,
        "neighbourhood_cleansed",
    )

    sentiment_by_room_type = create_grouped_sentiment(
        listing_sentiment,
        "room_type",
    )

    top_terms = create_top_review_terms(reviews)

    save_outputs(
        sentiment_summary,
        listing_sentiment,
        sentiment_by_neighbourhood,
        sentiment_by_room_type,
        top_terms,
    )

    create_sentiment_distribution_figure(reviews)
    create_top_terms_figure(top_terms)

    logging.info("AI/NLP review analysis outputs created")


if __name__ == "__main__":
    main()