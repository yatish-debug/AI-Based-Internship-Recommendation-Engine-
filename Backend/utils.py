from __future__ import annotations
from typing import List, Dict, Any
import json
import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize_tokens(tokens: List[str]) -> List[str]:
    """Normalize list of tokens (skills) by lowercasing and stripping."""
    return [t.strip().lower() for t in tokens if t and t.strip()]


def load_internships_safe(path: str) -> pd.DataFrame:
    """
    Load internships JSON into a pandas DataFrame with basic validation.
    Expected fields: title, description, location, skills (list), duration.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("internship_data.json must contain a list of internship entries.")

    # Validate and normalize
    normalized: List[Dict[str, Any]] = []
    for i, item in enumerate(data):
        try:
            title = str(item["title"]).strip()
            description = str(item["description"]).strip()
            location = str(item["location"]).strip()
            skills = item.get("skills", [])
            if not isinstance(skills, list):
                raise ValueError("skills must be a list")
            skills = _normalize_tokens([str(s) for s in skills])
            duration = str(item["duration"]).strip()
        except Exception as e:  # noqa: BLE001
            raise ValueError(f"Invalid entry at index {i}: {e}") from e

        if not title or not description or not location or not duration:
            raise ValueError(f"Missing required fields in entry at index {i}")

        normalized.append({
            "title": title,
            "description": description,
            "location": location,
            "skills": skills,
            "duration": duration,
        })

    df = pd.DataFrame(normalized)
    # Create helper text fields
    df["skills_text"] = df["skills"].apply(lambda lst: " ".join(lst))
    # Optionally include description to improve matching
    df["full_text"] = (df["skills_text"] + " " + df["description"].str.lower().str.replace(r"[^a-z0-9 ]", " ", regex=True))
    return df


class InternshipRecommender:
    """
    Simple, extensible recommender using TF-IDF + cosine similarity.
    Currently emphasizes skills; can be extended to multi-field or model-based approaches.
    """

    def __init__(self, use_description: bool = True, location_boost: float = 0.05) -> None:
        """
        use_description: If True, include description text in vectorization.
        location_boost: Small additive score for location matches (0–1).
        """
        self.use_description = use_description
        self.location_boost = float(location_boost)
        self.vectorizer: TfidfVectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=1,
            stop_words="english"
        )
        self._fitted = False
        self._matrix = None
        self._df: pd.DataFrame | None = None

    def fit(self, df: pd.DataFrame) -> None:
        """Fit TF-IDF on the internship corpus."""
        if df.empty:
            raise ValueError("Training DataFrame is empty.")
        self._df = df.copy()
        corpus = df["full_text"] if self.use_description else df["skills_text"]
        self._matrix = self.vectorizer.fit_transform(corpus.values)
        self._fitted = True

    def _make_query_text(self, skills: List[str], education: str | None) -> str:
        """Build query text from skills and education."""
        tokens = _normalize_tokens(skills)
        edu = (education or "").strip().lower()
        query_parts: List[str] = tokens.copy()
        if edu:
            # Lightweight inclusion of education keywords
            query_parts.extend(edu.split())
        return " ".join(query_parts)

    def recommend(
        self,
        user_skills: List[str],
        user_education: str | None,
        user_location: str | None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Return top-k internships with scores."""
        if not self._fitted or self._df is None or self._matrix is None:
            raise ValueError("Recommender is not fitted.")

        query_text = self._make_query_text(user_skills, user_education)
        if not query_text.strip():
            raise ValueError("Provide at least one skill or education keyword.")

        query_vec = self.vectorizer.transform([query_text])
        sim: np.ndarray = cosine_similarity(query_vec, self._matrix)  # shape (1, N)
        scores = sim.ravel()

        # Optional location preference: small boost for exact (case-insensitive) matches
        if user_location:
            user_loc_norm = user_location.strip().lower()
            loc_matches = self._df["location"].str.lower().eq(user_loc_norm).to_numpy()
            scores = scores + (loc_matches.astype(float) * self.location_boost)

        # Build results
        results = []
        for idx, score in enumerate(scores):
            row = self._df.iloc[idx]
            results.append({
                "title": row["title"],
                "description": row["description"],
                "location": row["location"],
                "skills": row["skills"],
                "duration": row["duration"],
                "score": float(score),
            })

        # Sort by score descending and return top_k (3–5 recommended by default)
        results.sort(key=lambda x: x["score"], reverse=True)
        k = max(3, min(top_k, 10))  # enforce at least 3 and at most 10
        return results[:k]
