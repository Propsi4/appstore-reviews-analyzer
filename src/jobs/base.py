"""Base job class."""

# Standart library imports
from abc import ABC, abstractmethod

# Thirdparty imports
from pydantic import BaseModel


class BaseJob(ABC, BaseModel):
    """Base job class."""

    @abstractmethod
    def run(self, *args, **kwargs) -> None:
        """Run the job."""
        ...
