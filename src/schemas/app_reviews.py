"""App reviews schema."""

# Thirdparty imports
from pydantic import BaseModel, Field


class Review(BaseModel):
    """App review schema."""

    id: str = Field(..., description="Review ID")
    author: str = Field(..., description="Author name")
    version: str = Field(..., description="App version")
    rating: int = Field(..., description="Review rating")
    title: str = Field(..., description="Review title")
    content: str = Field(..., description="Review content")
    vote_count: int = Field(..., description="Number of votes", alias="vote_count")
    vote_sum: int = Field(..., description="Sum of votes", alias="vote_sum")
    created_at: str = Field(..., description="Review timestamp from the RSS field")

    model_config = {"populate_by_name": True}
