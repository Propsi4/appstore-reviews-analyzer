"""Job for orchestrating app review collection and analysis."""

# Standart library imports
from datetime import datetime

# Thirdparty imports
from loguru import logger
from pydantic import ConfigDict, Field
from sqlalchemy.orm import Session

# Local imports
from src.db.models import App, AppInsight, ProcessedReview, Review
from src.jobs.base import BaseJob
from src.services.app_reviews import AppReviewsService
from src.services.nlp import NLPService


class ReviewAnalysisJob(BaseJob):
    """Job that orchestrates the scraping, analyzing, and persisting of app reviews."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    db: Session = Field(...)
    review_service: AppReviewsService = Field(default_factory=AppReviewsService)
    nlp_service: NLPService = Field(default_factory=NLPService)

    def run(self, app_id: str, country: str):
        """
        Execute the full analysis flow for a given app.

        Args:
            app_id: Apple App Store ID.
            country: Country code.
        """
        try:
            app_name = self.review_service.get_app_name(app_id, country)
            logger.info(f"Starting analysis job for App: {app_name} ({app_id}) in {country}")

            # 1. Ensure App exists in DB
            app = self.db.query(App).filter(App.external_id == app_id).first()
            if not app:
                app = App(external_id=app_id, name=app_name, country=country)
                self.db.add(app)
                self.db.commit()
                self.db.refresh(app)

            # 2. Scrape reviews (collecting 100 as per requirements)
            raw_reviews = self.review_service.get_reviews_by_limit(app_id=app_id, country=country, limit=100)

            new_reviews_count = 0
            negative_review_texts = []
            ratings = []

            for raw in raw_reviews:
                ratings.append(raw.rating)

                # Check for duplicates using external_id
                existing_review = self.db.query(Review).filter(Review.external_id == str(raw.id)).first()
                if existing_review:
                    continue

                # 3. Save raw review
                review = Review(
                    app_id=app.id,
                    external_id=str(raw.id),
                    rating=raw.rating,
                    title=raw.title,
                    content=raw.content,
                    author=raw.author,
                    version=raw.version,
                    created_at=(
                        datetime.fromisoformat(raw.created_at.replace("Z", "+00:00")) if raw.created_at else None
                    ),
                )
                self.db.add(review)
                self.db.flush()  # Get review.id

                # 4. NLP Analysis (Sentiment)
                sentiment_label, sentiment_score = self.nlp_service.analyze_sentiment(raw.content)
                processed = ProcessedReview(
                    review_id=review.id, sentiment_label=sentiment_label, sentiment_score=sentiment_score
                )
                self.db.add(processed)

                if sentiment_label == "negative":
                    negative_review_texts.append(raw.content)

                new_reviews_count += 1

            self.db.commit()
            logger.info(f"Saved {new_reviews_count} new reviews and analysis results.")

            # 5. Metrics Calculation
            if not ratings:
                logger.warning("No reviews collected, skipping metrics calculation.")
                return

            avg_rating = sum(ratings) / len(ratings)
            distribution = {str(i): ratings.count(i) for i in range(1, 6)}

            # 6. Keyword Extraction & Gemini Insights
            top_keywords = self.nlp_service.extract_keywords(negative_review_texts, top_n=10)
            nlp_response = self.nlp_service.generate_insights(negative_review_texts, top_keywords)
            insights = nlp_response.insights
            recommendations = "\n".join([f"- {r}" for r in nlp_response.recommendations])

            # 7. Update AppInsights
            app_insight = self.db.query(AppInsight).filter(AppInsight.app_id == app.id).first()
            if not app_insight:
                app_insight = AppInsight(app_id=app.id)
                self.db.add(app_insight)

            app_insight.avg_rating = avg_rating
            app_insight.rating_distribution = distribution
            app_insight.top_negative_keywords = top_keywords
            app_insight.developer_insights = insights
            app_insight.actionable_recommendations = recommendations
            app_insight.last_processed_at = datetime.utcnow()

            self.db.commit()
            logger.info(f"Successfully finalized job for app {app_id}.")

        except Exception as e:
            logger.error(f"Analysis job failed for app {app_id}: {e}")
            self.db.rollback()
            raise
