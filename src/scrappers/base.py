"""Base class for scrappers."""

# Standart library imports
from abc import ABC, abstractmethod

# Thirdparty imports
from pydantic import BaseModel


class BaseScrapper(ABC, BaseModel):
    """Base class for scrappers."""

    @abstractmethod
    def execute(self):
        """Abstract method to be implemented by subclasses."""
        ...
