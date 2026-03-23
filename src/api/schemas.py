"""API response models."""

# Standart library imports
from typing import Dict, List

# Thirdparty imports
from pydantic import BaseModel, Field


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


class ProcessedReviewResponse(BaseModel):
    """Processed review schema."""

    sentiment_label: str | None = Field(None, description="Sentiment label (e.g., positive, negative, neutral)")
    sentiment_score: float | None = Field(None, description="Sentiment score")

    model_config = {"from_attributes": True}


class ReviewResponse(BaseModel):
    """Review schema for API responses."""

    id: str = Field(..., validation_alias="external_id", description="External review ID")
    author: str | None = Field(None, description="Author name")
    version: str | None = Field(None, description="App version")
    rating: int = Field(..., description="Review rating")
    title: str | None = Field(None, description="Review title")
    content: str | None = Field(None, description="Review content")
    created_at: str | None = Field(None, description="Review timestamp")

    processed_review: ProcessedReviewResponse | None = Field(None, description="Processed analysis for the review")

    model_config = {"from_attributes": True, "populate_by_name": True}


class ReviewListResponse(BaseModel):
    """Paginated list of reviews."""

    app_id: str = Field(..., description="App Store ID")
    country: str = Field(..., description="Country code")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of reviews per page")
    count: int = Field(..., description="Number of reviews returned in current response")
    reviews: List[ReviewResponse] = Field(..., description="List of reviews with their processed analysis")


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
