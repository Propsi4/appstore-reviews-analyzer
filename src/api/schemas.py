"""API response models."""

# Standart library imports
from typing import Dict, List

# Thirdparty imports
from pydantic import BaseModel, Field

# Local imports
from src.schemas.app_reviews import Review


class BaseResponse(BaseModel):
    """Common response structure."""

    status: str = Field(..., description="Response status (e.g., 'accepted', 'success')")
    message: str = Field(..., description="Informational message about the result")


class AppURLResponse(BaseModel):
    """Response for App Store URL parsing."""

    country: str = Field(..., description="Country code (e.g., 'us', 'ru')")
    app_id: str = Field(..., description="App Store ID digits")
    app_name: str = Field(..., description="Extracted app name from the URL or Store")


class AppPagesResponse(BaseModel):
    """Response for App Store page count."""

    app_id: str = Field(..., description="App Store ID")
    country: str = Field(..., description="Country code")
    num_pages: int = Field(..., description="Total number of pages available in RSS feed")


class ReviewListResponse(BaseModel):
    """Paginated list of reviews."""

    app_id: str = Field(..., description="App Store ID")
    country: str = Field(..., description="Country code")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of reviews per page")
    count: int = Field(..., description="Number of reviews returned in current response")
    reviews: List[Review] = Field(..., description="List of reviews")


class AppMetricsResponse(BaseModel):
    """Aggregated app metrics and insights."""

    app_id: str = Field(..., description="App Store ID")
    app_name: str = Field(..., description="App name")
    country: str = Field(..., description="Country code")
    avg_rating: float = Field(..., description="Average star rating (0.0 to 5.0)")
    rating_distribution: Dict[str, int] = Field(..., description="Count of reviews per star rating")
    top_negative_keywords: List[str] = Field(..., description="Most frequent keywords found in negative reviews")
    developer_insights: str = Field(..., description="AI-generated insights about app performance and user feedback")
    actionable_recommendations: List[str] = Field(
        ..., description="Specific, prioritized recommendations for developers"
    )
    last_processed_at: str = Field(..., description="Timestamp of when these insights were last generated")


class ReviewDownloadResponse(BaseModel):
    """Individual review for download."""

    id: str = Field(..., description="External review ID")
    author: str = Field(..., description="Reviewer name")
    rating: int = Field(..., description="Star rating")
    title: str = Field(..., description="Review title")
    content: str = Field(..., description="Full text content of the review")
    version: str = Field(..., description="App version when the review was written")
    created_at: str = Field(..., description="Review creation timestamp")
