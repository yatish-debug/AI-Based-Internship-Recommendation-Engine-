from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from models import RecommendRequest, InternshipOut, RecommendResponse, HealthOut
from utils import InternshipRecommender, load_internships_safe

# Initialize app
app = FastAPI(
    title="Internship Recommender API",
    version="1.0.0",
    description="Recommends internships based on user skills, education, and location."
)

# Configure CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://your-frontend.example.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data and initialize recommender at startup
DATA_PATH = "internship_data.json"
internships_df = load_internships_safe(DATA_PATH)
recommender = InternshipRecommender()
recommender.fit(internships_df)

@app.get("/health", response_model=HealthOut, tags=["System"])
def health() -> HealthOut:
    return HealthOut(status="ok")

@app.post("/recommend", response_model=RecommendResponse, tags=["Recommend"])
def recommend(payload: RecommendRequest) -> RecommendResponse:
    # Basic validation
    if not payload.skills and not payload.education:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="At least one of 'skills' or 'education' must be provided."
        )

    try:
        results = recommender.recommend(
            user_skills=payload.skills,
            user_education=payload.education,
            user_location=payload.location,
            top_k=payload.top_k or 5,
        )
    except ValueError as ve:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as ex:  # noqa: BLE001
        # Log in real-world apps
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating recommendations."
        ) from ex

    # Build response
    items: List[InternshipOut] = []
    for row in results:
        items.append(
            InternshipOut(
                title=row["title"],
                description=row["description"],
                location=row["location"],
                skills=row["skills"],
                duration=row["duration"],
                score=float(row["score"]),
            )
        )

    return RecommendResponse(
        count=len(items),
        items=items,
        note="Scores are cosine similarity values on a 0–1 scale."
    )

# Optional root
@app.get("/", tags=["System"])
def root() -> Dict[str, Any]:
    return {"message": "Internship Recommender API. See /docs for usage."}
