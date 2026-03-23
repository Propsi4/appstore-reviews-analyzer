"""Review model definition."""

# Standart library imports
from datetime import datetime
from typing import TYPE_CHECKING

# Thirdparty imports
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local folder imports
from .base import Base

if TYPE_CHECKING:
    # Local folder imports
    from .app import App
    from .processed_review import ProcessedReview


class Review(Base):
    """Model representing a raw app review."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[int] = mapped_column(Integer, ForeignKey("apps.id"), nullable=False)
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    author: Mapped[str] = mapped_column(String, nullable=True)
    version: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    app: Mapped["App"] = relationship("App", back_populates="reviews")
    processed_review: Mapped["ProcessedReview"] = relationship(
        "ProcessedReview", back_populates="review", uselist=False, cascade="all, delete-orphan"
    )
