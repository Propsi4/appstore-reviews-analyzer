"""Unit tests for the services."""

# Standart library imports
from unittest.mock import MagicMock, PropertyMock, patch

# Thirdparty imports
import pytest

# Local imports
from src.services.app_reviews import AppReviewsService
from src.services.nlp import NLPService


def test_app_reviews_service_parse_url():
    """Test parsing a valid App Store URL."""
    service = AppReviewsService()
    url = "https://apps.apple.com/us/app/example-app/id123456789"
    res = service.parse_app_url(url)
    assert res["app_id"] == "123456789"
    assert res["country"] == "us"


def test_app_reviews_service_parse_url_invalid():
    """Test parsing an invalid App Store URL."""
    service = AppReviewsService()
    url = "https://invalid.url"
    with pytest.raises(ValueError, match="Invalid App Store URL format"):
        service.parse_app_url(url)


def test_app_reviews_service_num_pages(mock_scraper):
    """Test getting page count through the service."""
    mock_scraper.return_value.num_pages = 10
    service = AppReviewsService()
    res = service.get_num_pages("123", "us")
    assert res == 10


def test_app_reviews_service_get_reviews(mock_scraper):
    """Test getting a single page of reviews."""
    mock_scraper.return_value.review.return_value = ["review"]
    service = AppReviewsService()
    res = service.get_reviews("123", "us")
    assert res == ["review"]


def test_nlp_service_init_coverage():
    """Test NLPService initialization coverage (NLTK download and init error)."""
    # Test NLTK download trigger
    with patch("src.services.nlp.nltk_find", side_effect=LookupError), patch("nltk.download") as mock_download, patch(
        "src.services.nlp.pipeline"
    ):
        _ = NLPService()
        assert mock_download.call_count >= 2

    # Test init error
    with patch("src.services.nlp.pipeline", side_effect=Exception("Init Fail")):
        with pytest.raises(Exception, match="Init Fail"):
            _ = NLPService()


def test_nlp_service_analyze_sentiment():
    """Test sentiment analysis with mocked pipeline."""
    with patch("src.services.nlp.pipeline") as mock_pipeline:
        mock_pipe = MagicMock()
        mock_pipe.return_value = [{"label": "LABEL_2", "score": 0.99}]
        mock_pipeline.return_value = mock_pipe

        service = NLPService()
        label, score = service.analyze_sentiment("I love this!")
        assert label == "positive"
        assert score == 0.99


def test_nlp_service_analyze_sentiment_empty():
    """Test sentiment analysis with empty input."""
    service = NLPService()
    label, score = service.analyze_sentiment("")
    assert label == "neutral"
    assert score == 0.0


def test_app_reviews_service_num_pages_error(mock_scraper):
    """Test service handling of scrapper error for page count."""
    type(mock_scraper.return_value).num_pages = PropertyMock(side_effect=Exception("Scrapper error"))
    service = AppReviewsService()
    with pytest.raises(Exception, match="Scrapper error"):
        service.get_num_pages("123", "us")


def test_app_reviews_service_get_reviews_error(mock_scraper):
    """Test service handling of scrapper error for review fetching."""
    mock_scraper.return_value.review.side_effect = Exception("Review error")
    service = AppReviewsService()
    with pytest.raises(Exception, match="Review error"):
        service.get_reviews("123", "us")


def test_app_reviews_service_execute_errors(mock_scraper):
    """Test service handling of scrapper error for multi-page execution."""
    mock_scraper.return_value.execute.side_effect = Exception("Execute error")
    service = AppReviewsService()
    with pytest.raises(Exception, match="Execute error"):
        service.get_reviews_by_limit("123", "us")
    with pytest.raises(Exception, match="Execute error"):
        service.get_all_reviews("123", "us")


def test_nlp_service_analyze_sentiment_error():
    """Test sentiment analysis error handling (returns neutral)."""
    with patch("src.services.nlp.pipeline") as mock_pipeline:
        mock_pipe = MagicMock()
        mock_pipe.side_effect = Exception("Pipeline error")
        mock_pipeline.return_value = mock_pipe
        service = NLPService()
        label, score = service.analyze_sentiment("text")
        assert label == "neutral"
        assert score == 0.0


def test_nlp_service_generate_insights_success():
    """Test successful insight generation with Gemini."""
    service = NLPService()
    with patch.object(service, "_client") as mock_client:
        mock_response = MagicMock()
        mock_response.text = '{"insights": "Excellent app", "recommendations": ["Keep it up"]}'
        mock_client.models.generate_content.return_value = mock_response

        res = service.generate_insights(["text"], ["kw"])
        assert res.insights == "Excellent app"
        assert res.recommendations == ["Keep it up"]


def test_nlp_service_generate_insights_error():
    """Test insight generation error handling."""
    service = NLPService()
    with patch.object(service, "_client") as mock_client:
        mock_client.models.generate_content.side_effect = Exception("Gemini error")
        res = service.generate_insights(["text"], ["kw"])
        assert res.insights == "Failed to generate insights."


def test_nlp_service_empty_inputs():
    """Test insight generation with empty inputs."""
    service = NLPService()
    assert service.extract_keywords([]) == []
    res = service.generate_insights([], [])
    assert res.insights == "No negative feedback to analyze."
    assert res.recommendations == ["N/A"]
