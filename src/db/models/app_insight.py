"""App insight model definition."""

# Standart library imports
from datetime import datetime
from typing import TYPE_CHECKING

# Thirdparty imports
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local folder imports
from .base import Base

if TYPE_CHECKING:
    # Local folder imports
    from .app import App


class AppInsight(Base):
    """Model representing aggregated app insights and metrics."""

    __tablename__ = "app_insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[int] = mapped_column(Integer, ForeignKey("apps.id"), nullable=False)
    avg_rating: Mapped[float] = mapped_column(Float, nullable=True)
    rating_distribution: Mapped[dict] = mapped_column(JSON, nullable=True)
    top_negative_keywords: Mapped[list] = mapped_column(JSON, nullable=True)
    developer_insights: Mapped[str] = mapped_column(Text, nullable=True)
    actionable_recommendations: Mapped[str] = mapped_column(Text, nullable=True)
    last_processed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    app: Mapped["App"] = relationship("App", back_populates="insights")
