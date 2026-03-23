"""Schemas for NLP service outputs."""

# Standart library imports
from typing import List

# Thirdparty imports
from pydantic import BaseModel, Field


class AppInsightsResponse(BaseModel):
    """Structured response for app insights from Gemini."""

    insights: str = Field(..., description="High-level summary of the main issues discovered in reviews.")
    recommendations: List[str] = Field(
        ..., description="List of specific, actionable recommendations for the developer."
    )


class KeywordsResponse(BaseModel):
    """Structured response for extracted keywords from Gemini."""

    keywords: List[str] = Field(..., description="List of the most relevant keywords extracted from the reviews.")
