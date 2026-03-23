"""Unit tests for the schemas module."""

# Local imports
from src.schemas.app_reviews import Review
from src.schemas.nlp import AppInsightsResponse


def test_review_schema():
    """Test review schema."""
    data = {
        "id": "1",
        "author": "User",
        "version": "1.0",
        "rating": 5,
        "title": "Great",
        "content": "Awesome app",
        "vote_count": 0,
        "vote_sum": 0,
        "created_at": "2023-10-01",
    }
    review = Review(**data)
    assert review.id == "1"
    assert review.rating == 5


def test_app_insights_response_schema():
    """Test app insights response schema."""
    data = {"insights": "Good", "recommendations": ["Keep it up"]}
    insights = AppInsightsResponse(**data)
    assert insights.insights == "Good"
    assert "Keep it up" in insights.recommendations
