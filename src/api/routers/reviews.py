"""FastAPI routers for app reviews."""

# Standart library imports
from typing import List, Optional, Union

# Thirdparty imports
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

# Local imports
from src.api.schemas import (
    AppMetricsResponse,
    AppPagesResponse,
    AppURLResponse,
    BaseResponse,
    ReviewDownloadResponse,
    ReviewListResponse,
)
from src.db.models import App, AppInsight, Review
from src.db.session import get_db
from src.jobs.review_analysis import ReviewAnalysisJob
from src.services.app_reviews import AppReviewsService

router = APIRouter(prefix="/reviews", tags=["reviews"])
service = AppReviewsService()


@router.post("/collect/{app_id}", response_model=BaseResponse)
def collect_reviews(app_id: str, background_tasks: BackgroundTasks, country: str = "us", db: Session = Depends(get_db)):
    """Trigger a background job to collect and analyze reviews for a specific app."""
    try:
        # Start a background task
        job = ReviewAnalysisJob(db=db)
        background_tasks.add_task(job.run, app_id=app_id, country=country)
        return {"status": "accepted", "message": f"Review analysis job for app {app_id} started in background."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parse-url", response_model=AppURLResponse)
def parse_app_url(url: str):
    """Extract app_id and country from an Apple App Store URL."""
    try:
        return service.parse_app_url(url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pages/{app_id}", response_model=AppPagesResponse)
def get_app_pages(app_id: str, country: str = "us"):
    """Get the total number of pages available for an app."""
    try:
        num_pages = service.get_num_pages(app_id, country)
        return AppPagesResponse(app_id=app_id, country=country, num_pages=num_pages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{app_id}", response_model=ReviewListResponse)
def list_reviews(
    app_id: str,
    page: int = 1,
    limit: int = 50,
    country: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Fetch reviews for a specific app and country (paginated)."""
    try:
        query = db.query(App).filter(App.external_id == app_id)
        if country:
            query = query.filter(App.country == country)

        app = query.first()
        if not app:
            raise HTTPException(status_code=404, detail="App not found.")

        reviews = (
            db.query(Review)
            .options(joinedload(Review.processed_review))
            .filter(Review.app_id == app.id)
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        return {
            "app_id": app_id,
            "country": app.country,
            "page": page,
            "limit": limit,
            "count": len(reviews),
            "reviews": reviews,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/{app_id}", response_model=Union[AppMetricsResponse, dict])
def get_metrics(app_id: str, db: Session = Depends(get_db)):
    """Get aggregated metrics and insights for a specific app."""
    app = db.query(App).filter(App.external_id == app_id).first()
    if not app:
        return {
            "app_id": app_id,
            "status": "processing",
            "message": "App is being registered and insights are being generated.",
        }

    insight = db.query(AppInsight).filter(AppInsight.app_id == app.id).first()
    if not insight:
        return {"app_id": app_id, "status": "processing", "message": "Insights are still being generated."}

    recommendations = [item.strip() for item in insight.actionable_recommendations.split('- ') if item.strip()]

    return {
        "app_id": app_id,
        "app_name": app.name,
        "country": app.country,
        "avg_rating": insight.avg_rating,
        "rating_distribution": insight.rating_distribution,
        "top_negative_keywords": insight.top_negative_keywords,
        "developer_insights": insight.developer_insights,
        "actionable_recommendations": recommendations,
        "last_processed_at": str(insight.last_processed_at),
    }


@router.get("/download/{app_id}", response_model=List[ReviewDownloadResponse])
def download_reviews(app_id: str, db: Session = Depends(get_db)):
    """Provide raw review data for download."""
    app = db.query(App).filter(App.external_id == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found.")

    reviews = db.query(Review).filter(Review.app_id == app.id).all()

    # Format reviews for JSON download
    return [
        ReviewDownloadResponse(
            id=r.external_id,
            author=r.author,
            rating=r.rating,
            title=r.title,
            content=r.content,
            version=r.version,
            created_at=r.created_at,
        )
        for r in reviews
    ]
