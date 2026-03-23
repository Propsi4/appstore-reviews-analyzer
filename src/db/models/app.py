"""App model definition."""

# Standart library imports
from typing import TYPE_CHECKING, List

# Thirdparty imports
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local folder imports
from .base import Base

if TYPE_CHECKING:
    # Local folder imports
    from .app_insight import AppInsight
    from .review import Review


class App(Base):
    """Model representing an App Store application."""

    __tablename__ = "apps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    country: Mapped[str] = mapped_column(String, nullable=True)

    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="app", cascade="all, delete-orphan")
    insights: Mapped[List["AppInsight"]] = relationship(
        "AppInsight", back_populates="app", cascade="all, delete-orphan"
    )
