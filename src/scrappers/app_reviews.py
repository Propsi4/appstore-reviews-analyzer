"""App reviews scrapper class."""

# Standart library imports
import re

# Thirdparty imports
import httpx
from loguru import logger
from pydantic import PrivateAttr, field_validator

# Local imports
from src.interfaces.app_reviews import IAppReviews
from src.schemas.app_reviews import Review
from src.scrappers.base import BaseScrapper


class AppReviewsScrapper(IAppReviews, BaseScrapper):
    """App reviews scrapper class."""

    _num_pages: int | None = PrivateAttr(default=None)
    _app_name: str | None = PrivateAttr(default=None)

    @property
    def num_pages(self) -> int:
        """Return the maximum number of pages allowed by the App Store RSS feed."""
        if self._num_pages is None:
            # If not yet fetched, fetch page 1 to discover the total page count
            self.review(page=1)
        return self._num_pages or 1

    @property
    def app_name(self) -> str:
        """Return the app name from the iTunes Lookup API."""
        if self._app_name is None:
            self._app_name = self._fetch_app_name()
        return self._app_name

    def _fetch_app_name(self) -> str:
        """
        Fetch the app name from the iTunes Lookup API.

        Args:
            app_id: App Store ID.
            country: Country code.

        Returns:
            The official app name.
        """
        url = f"https://itunes.apple.com/lookup?id={self.app_id}&country={self.country}"
        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            if not results:
                logger.warning(f"No app found for id={self.app_id} in country={self.country}")
                return "Unknown"
            return results[0].get("trackName", "Unknown")
        except Exception as e:
            logger.error(f"Failed to fetch app name for {self.app_id}: {e}")
            return "Unknown"

    def _extract_num_pages(self, feed_links: list[dict]) -> int:
        """Extract the total number of pages from the feed links."""
        for link in feed_links:
            if link.get("attributes", {}).get("rel") == "last":
                href = link.get("attributes", {}).get("href", "")
                match = re.search(r"page=(\d+)", href)
                if match:
                    return int(match.group(1))
        return 1

    def review(self, limit: int = 50, page: int = 1) -> list[Review]:
        """
        Fetch reviews for a specific page.

        Args:
            limit: Number of reviews to fetch (max 50 per page in RSS).
            page: Page number to fetch.

        Returns:
            List of Review objects.
        """
        if self._num_pages is not None and page > self._num_pages:
            logger.warning(f"Page {page} exceeds the maximum available pages ({self._num_pages})")
            return []

        url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/page={page}/id={self.app_id}/sortby=mostrecent/json"

        try:
            response = httpx.get(url, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            feed = data.get("feed", {})

            # Update dynamic page count from links if not already set
            links = feed.get("link", [])
            self._num_pages = self._extract_num_pages(links)

            entries = feed.get("entry", [])

            # If entry is a single dict instead of a list (happens if only one review)
            if isinstance(entries, dict):
                entries = [entries]

            # Filter out the first entry if it's the app info (standard for this RSS feed)
            reviews = []
            for entry in entries:
                if "author" in entry:
                    try:
                        review_obj = Review(
                            id=entry.get("id", {}).get("label"),
                            author=entry.get("author", {}).get("name", {}).get("label"),
                            version=entry.get("im:version", {}).get("label"),
                            rating=int(entry.get("im:rating", {}).get("label", 0)),
                            title=entry.get("title", {}).get("label"),
                            content=entry.get("content", {}).get("label"),
                            vote_count=int(entry.get("im:voteCount", {}).get("label", 0)),
                            vote_sum=int(entry.get("im:voteSum", {}).get("label", 0)),
                            created_at=entry.get("updated", {}).get("label"),
                        )
                        reviews.append(review_obj)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Skipping malformed review entry: {e}")

            return reviews[:limit]

        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error occurred while fetching reviews: {e.response.status_code} - Make sure that the country code '{self.country}' and app id '{self.app_id}' are correct."
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting reviews: {e}")
            raise
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Failed to parse review data: {e}")
            raise

    def execute(self, limit: int | None = None) -> list[Review]:
        """
        Execute the scrapper to retrieve reviews.

        Args:
            limit: Maximum number of reviews to fetch. If None, fetch all.

        Returns:
            List of retrieved Review objects.
        """
        all_reviews = []
        logger.info(f"Starting review scraping for {self.app_name} (ID: {self.app_id}) in {self.country}")

        p = 1
        while True:
            try:
                page_reviews = self.review(page=p)
                if not page_reviews:
                    break

                if limit is not None:
                    remaining = limit - len(all_reviews)
                    if remaining <= 0:
                        break
                    all_reviews.extend(page_reviews[:remaining])
                else:
                    all_reviews.extend(page_reviews)

                logger.debug(f"Fetched {len(page_reviews)} reviews from page {p}")

                if limit is not None and len(all_reviews) >= limit:
                    break

                # After page 1, we should have self._num_pages set
                if self._num_pages is not None and p >= self._num_pages:
                    break

                p += 1
            except Exception as e:
                logger.error(f"Stopping execution due to error on page {p}: {e}")
                break

        logger.info(f"Successfully scraped {len(all_reviews)} reviews for {self.app_name}")
        return all_reviews

    @field_validator("app_id")
    def _verify_app_id(cls, v):
        """Verify app id."""
        if not re.match(r"^-?[0-9]+$", v):
            raise ValueError("App ID must contain digits only")
        if int(v) < 0:
            raise ValueError("App ID must be a positive integer")
        return v
