"""App reviews service class."""

# Standart library imports
import re

# Thirdparty imports
from loguru import logger
from pydantic import BaseModel

# Local imports
from src.schemas.app_reviews import Review
from src.scrappers.app_reviews import AppReviewsScrapper


class AppReviewsService(BaseModel):
    """
    Stateless app reviews service class.

    This service provides a clean interface to fetch reviews from App Store.
    It does not maintain any internal state regarding app_id or country.
    """

    @staticmethod
    def parse_app_url(url: str) -> dict[str, str]:
        """
        Extract app_id, country, and app_name from an Apple App Store URL.

        Args:
            url: App Store URL (e.g., https://apps.apple.com/ru/app/roblox/id431946152).

        Returns:
            Dictionary containing 'app_id', 'country', and 'app_name'.

        Raises:
            ValueError: If the URL format is invalid.
        """
        # Pattern: https://apps.apple.com/{country}/app/{name}/id{app_id}
        # Name is now optional in the pattern to support .../app/id123
        pattern = r"https?://(?:apps|itunes)\.apple\.com/([a-z]{2})/app/(?:([^/]+)/)?id(\d+)"
        match = re.search(pattern, url)
        if not match:
            raise ValueError(f"Invalid App Store URL format: {url}")

        country = match.group(1)
        app_name = match.group(2) or ""
        app_id = match.group(3)

        if not app_name:
            logger.info(f"App name missing in URL, fetching for id={app_id}")
            app_name = AppReviewsService.get_app_name(app_id, country)

        return {"country": country, "app_id": app_id, "app_name": app_name}

    def get_app_name(self, app_id: str, country: str) -> str:
        """
        Get the app name for a specific app and country.

        Args:
            app_id: Apple App Store ID.
            country: Country code.

        Returns:
            The official app name.
        """
        try:
            logger.info(f"Fetching app name for app_id={app_id}, country={country}")
            scraper = AppReviewsScrapper(app_id=app_id, country=country)
            return scraper.app_name
        except ValueError as e:
            logger.error(f"Failed to fetch app name for app {app_id}: {e}")
            raise

    def get_num_pages(self, app_id: str, country: str) -> int:
        """
        Get the total number of pages available for an app.

        Args:
            app_id: Apple App Store ID.
            country: Country code.

        Returns:
            Total number of pages.
        """
        try:
            logger.info(f"Checking page count for app_id={app_id}, country={country}")
            scraper = AppReviewsScrapper(app_id=app_id, country=country)
            return scraper.num_pages
        except Exception as e:
            logger.error(f"Failed to get page count for app {app_id}: {e}")
            raise

    def get_reviews(self, app_id: str, country: str, limit: int = 50, page: int = 1) -> list[Review]:
        """
        Fetch reviews for a specific app and country (single page).

        Args:
            app_id: Apple App Store ID.
            country: Country code (e.g., 'us', 'ua').
            limit: Number of reviews per page (max 50).
            page: Page number.

        Returns:
            List of Review schemas from a specific page.
        """
        try:
            logger.info(f"Fetching reviews for app_id={app_id}, country={country}, page={page}")
            scraper = AppReviewsScrapper(app_id=app_id, country=country)
            reviews = scraper.review(limit=limit, page=page)
            return reviews
        except Exception as e:
            logger.error(f"Failed to fetch reviews for app {app_id}: {e}")
            raise

    def get_reviews_by_limit(self, app_id: str, country: str, limit: int = 100) -> list[Review]:
        """
        Fetch reviews until a specified limit is reached or all pages are fetched.

        Args:
            app_id: Apple App Store ID.
            country: Country code.
            limit: Total number of reviews to fetch.

        Returns:
            List of Review schemas.
        """
        try:
            logger.info(f"Fetching up to {limit} reviews for app_id={app_id}, country={country}")
            scraper = AppReviewsScrapper(app_id=app_id, country=country)
            reviews = scraper.execute(limit=limit)
            return reviews
        except Exception as e:
            logger.error(f"Failed to fetch {limit} reviews for app {app_id}: {e}")
            raise

    def get_all_reviews(self, app_id: str, country: str) -> list[Review]:
        """
        Fetch all available reviews for a specific app and country.

        Args:
            app_id: Apple App Store ID.
            country: Country code.

        Returns:
            List of all available Review schemas.
        """
        try:
            logger.info(f"Fetching all reviews for app_id={app_id}, country={country}")
            scraper = AppReviewsScrapper(app_id=app_id, country=country)
            reviews = scraper.execute()
            return reviews
        except Exception as e:
            logger.error(f"Failed to fetch all reviews for app {app_id}: {e}")
            raise
