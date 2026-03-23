"""Interface for app reviews retrieval module."""

# Standart library imports
from abc import ABC, abstractmethod

# Thirdparty imports
from pydantic import BaseModel, Field

# Local imports
from src.schemas.app_reviews import Review


class IAppReviews(ABC, BaseModel):
    """Interface for app reviews retrieval module."""

    country: str = Field(..., description="Country code")
    app_id: str = Field(..., description="App ID")

    @abstractmethod
    def review(self, limit: int = 100, page: int = 1) -> list[Review]:
        """Abstract method to be implemented by subclasses."""
        ...

    @property
    @abstractmethod
    def num_pages(self) -> int:
        """Abstract property to be implemented by subclasses."""
        ...
