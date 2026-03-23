"""Unit tests for the scrappers module."""

# Standart library imports
from unittest.mock import MagicMock, patch

# Thirdparty imports
import httpx
import pytest

# Local imports
from src.schemas.app_reviews import Review
from src.scrappers.app_reviews import AppReviewsScrapper


def test_verify_app_id():
    """Test AppReviewsScrapper app_id validation."""
    # Valid ID
    AppReviewsScrapper(app_id="123456789", country="us")

    # Invalid IDs
    # Pydantic 2 wraps ValueErrors in ValidationError
    with pytest.raises(Exception) as excinfo:
        AppReviewsScrapper(app_id="-12345678", country="us")
    assert "positive" in str(excinfo.value).lower()

    with pytest.raises(Exception) as excinfo:
        AppReviewsScrapper(app_id="12345678a", country="us")
    assert "digits" in str(excinfo.value).lower()


def test_extract_num_pages():
    """Test extracting page count from Feed API links."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    links = [{"attributes": {"rel": "first", "href": "page=1"}}, {"attributes": {"rel": "last", "href": "page=10"}}]
    assert scrapper._extract_num_pages(links) == 10

    # No last link
    assert scrapper._extract_num_pages([{"attributes": {"rel": "first"}}]) == 1


def test_extract_num_pages_no_match():
    """Test extract_num_pages with malformed links."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    # Invalid Link header (pass list of dicts as expected)
    res = scrapper._extract_num_pages([{"not_attributes": {}}])
    assert res == 1


def test_review_success(mock_httpx_get):
    """Test successful review fetching."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "feed": {
            "link": [{"attributes": {"rel": "last", "href": "page=5"}}],
            "entry": [
                {
                    "author": {"name": {"label": "User"}},
                    "im:version": {"label": "1.0"},
                    "im:rating": {"label": "5"},
                    "title": {"label": "Title"},
                    "content": {"label": "Content"},
                    "im:voteCount": {"label": "0"},
                    "im:voteSum": {"label": "0"},
                    "id": {"label": "rev1"},
                    "updated": {"label": "2023-10-01T12:00:00Z"},
                }
            ],
        }
    }
    mock_response.status_code = 200
    mock_httpx_get.return_value = mock_response

    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    # Test property access for coverage
    assert scrapper.num_pages == 5

    reviews = scrapper.review(page=1)
    assert len(reviews) == 1
    assert reviews[0].id == "rev1"


def test_review_http_error(mock_httpx_get):
    """Test review fetching with HTTP error."""
    mock_httpx_get.side_effect = httpx.HTTPStatusError(
        "Error", request=MagicMock(), response=MagicMock(status_code=404)
    )

    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    with pytest.raises(httpx.HTTPStatusError):
        scrapper.review()


def test_num_pages_error(mock_httpx_get):
    """Test num_pages property error handling."""
    mock_httpx_get.side_effect = Exception("Failed to fetch")
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    with pytest.raises(Exception, match="Failed to fetch"):
        _ = scrapper.num_pages


def test_execute_error(mock_httpx_get):
    """Test execute method error handling (breaks loop)."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    with patch.object(AppReviewsScrapper, "review", side_effect=Exception("Execute error")):
        # execute() catches the exception and breaks the loop
        res = scrapper.execute(limit=10)
        assert res == []


def test_execute_multi_page():
    """Test multi-page review execution."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")

    def mock_review(limit=50, page=1):
        return [
            Review(
                id=f"id{page}",
                author="A",
                version="1",
                rating=1,
                title="T",
                content="C",
                vote_count=0,
                vote_sum=0,
                created_at="2023-10-01",
            )
        ]

    with patch.object(AppReviewsScrapper, "review", side_effect=mock_review):
        scrapper._num_pages = 2
        reviews = scrapper.execute(limit=10)
        assert len(reviews) == 2


def test_scrapper_page_exceeded():
    """Test review returning empty list if page > num_pages."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    scrapper._num_pages = 1
    assert scrapper.review(page=2) == []


def test_scrapper_entry_as_dict(mock_httpx_get):
    """Test handling of single entry as dict."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "feed": {
            "entry": {
                "author": {"name": {"label": "U"}},
                "im:rating": {"label": "5"},
                "id": {"label": "1"},
                "im:version": {"label": "1.0"},
                "title": {"label": "T"},
                "content": {"label": "C"},
                "im:voteCount": {"label": "0"},
                "im:voteSum": {"label": "0"},
                "updated": {"label": "2023-10-01"},
            }
        }
    }
    mock_response.status_code = 200
    mock_httpx_get.return_value = mock_response
    res = scrapper.review(page=1)
    assert len(res) == 1


def test_scrapper_malformed_rating(mock_httpx_get):
    """Test handling of malformed rating in entry."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "feed": {"entry": [{"author": {"name": {"label": "U"}}, "im:rating": {"label": "inv"}, "id": {"label": "1"}}]}
    }
    mock_response.status_code = 200
    mock_httpx_get.return_value = mock_response
    res = scrapper.review(page=1)
    assert len(res) == 0


def test_execute_limit_already_reached():
    """Test execute when limit is already reached."""
    scrapper = AppReviewsScrapper(app_id="123456789", country="us")
    with patch.object(
        AppReviewsScrapper,
        "review",
        return_value=[
            Review(
                id="1",
                author="A",
                version="1",
                rating=1,
                title="T",
                content="C",
                vote_count=0,
                vote_sum=0,
                created_at="2023",
            )
        ],
    ) as mock_review:
        # If limit is 0, should break immediately
        res = scrapper.execute(limit=0)
        assert res == []
        # Still calls once for page 1 to discover num_pages if needed
        assert mock_review.call_count == 1
