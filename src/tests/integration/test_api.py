"""Integration tests for the API."""

# Standart library imports
from unittest.mock import patch

# Local imports
from src.db.models import App, AppInsight
from src.services.app_reviews import AppReviewsService


def test_parse_app_url_endpoint(api_client):
    """Test app URL parsing endpoint."""
    url = "https://apps.apple.com/us/app/roblox/id431946152"
    response = api_client.get(f"/reviews/parse-url?url={url}")
    assert response.status_code == 200
    assert response.json() == {"country": "us", "app_id": "431946152", "app_name": "roblox"}


def test_collect_reviews_endpoint(api_client):
    """Test review collection endpoint."""
    # Mock ReviewAnalysisJob.run to avoid actual background job execution
    with patch("src.jobs.review_analysis.ReviewAnalysisJob.run"):
        response = api_client.post("/reviews/collect/123456789?country=us&app_name=TestApp")
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"


def test_get_app_pages_endpoint(api_client):
    """Test app pages endpoint."""
    with patch.object(AppReviewsService, "get_num_pages", return_value=10):
        response = api_client.get("/reviews/pages/123456789?country=us")
        assert response.status_code == 200
        assert response.json()["num_pages"] == 10


def test_list_reviews_endpoint(api_client):
    """Test list reviews endpoint."""
    with patch.object(AppReviewsService, "get_reviews", return_value=[]):
        response = api_client.get("/reviews/list/123456789?country=us&page=1&limit=50")
        assert response.status_code == 200
        assert response.json()["count"] == 0


def test_get_metrics_endpoint(api_client, db_session):
    """Test get metrics endpoint."""
    # Setup: Add app and insights to DB
    app = App(external_id="123456789", name="TestApp", country="us")
    db_session.add(app)
    db_session.commit()

    insight = AppInsight(
        app_id=app.id,
        avg_rating=4.5,
        rating_distribution={"5": 10},
        top_negative_keywords=["slow"],
        developer_insights="Keep going",
        actionable_recommendations="- Do more",
    )
    db_session.add(insight)
    db_session.commit()

    response = api_client.get("/reviews/metrics/123456789")
    assert response.status_code == 200
    assert response.json()["app_name"] == "TestApp"
    assert response.json()["avg_rating"] == 4.5


def test_download_reviews_endpoint(api_client, db_session):
    """Test download reviews endpoint."""
    response = api_client.get("/reviews/download/123456789")
    assert response.status_code == 404
