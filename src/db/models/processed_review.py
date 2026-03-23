"""Processed review model definition."""

# Standart library imports
from datetime import datetime
from typing import TYPE_CHECKING

# Thirdparty imports
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local folder imports
from .base import Base

if TYPE_CHECKING:
    # Local folder imports
    from .review import Review


class ProcessedReview(Base):
    """Model representing analyzed review results."""

    __tablename__ = "processed_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    review_id: Mapped[int] = mapped_column(Integer, ForeignKey("reviews.id"), unique=True, nullable=False)
    sentiment_label: Mapped[str] = mapped_column(String, nullable=True)  # positive, negative, neutral
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    review: Mapped["Review"] = relationship("Review", back_populates="processed_review")
