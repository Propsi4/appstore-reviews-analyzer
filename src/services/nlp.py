"""NLP service for sentiment analysis and keyword extraction."""

# Standart library imports
from typing import List, Tuple

# Thirdparty imports
import nltk
import torch
from google import genai
from google.genai import types
from loguru import logger
from nltk.corpus import stopwords
from nltk.data import find as nltk_find
from nltk.tokenize import word_tokenize
from pydantic import BaseModel, Field, PrivateAttr
from transformers import pipeline

# Local imports
from src.config.settings import settings
from src.prompts.insights import SYSTEM_PROMPT as INSIGHTS_PROMPT
from src.prompts.keywords import SYSTEM_PROMPT as KEYWORDS_PROMPT
from src.schemas.nlp import AppInsightsResponse, KeywordsResponse


class NLPService(BaseModel):
    """Service for processing text data using NLP techniques."""

    sentiment_analysis_model_name: str = Field(default="cardiffnlp/twitter-xlm-roberta-base-sentiment")
    gemini_model_name: str = Field(default=settings.gemini.model)

    _sentiment_pipe: pipeline = PrivateAttr(default=None)
    _client: genai.Client = PrivateAttr(default=None)

    def model_post_init(self, __context):
        """Post-initialize the NLPService."""
        try:
            device = 0 if torch.cuda.is_available() else -1
            logger.info(
                f"Initializing sentiment analysis model: {self.sentiment_analysis_model_name} on device: {device}"
            )
            self._sentiment_pipe = pipeline(
                "sentiment-analysis", model=self.sentiment_analysis_model_name, device=device
            )

            try:
                nltk_find("corpora/stopwords")
                nltk_find("tokenizers/punkt")
                nltk_find("tokenizers/punkt_tab")
            except LookupError:
                logger.info("Downloading necessary NLTK data...")
                nltk.download("stopwords")
                nltk.download("punkt")
                nltk.download("punkt_tab")

            logger.info(f"Initializing Gemini model: {self.gemini_model_name}")
            self._client = genai.Client(api_key=settings.gemini.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize NLPService: {e}")
            raise

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of a given text.

        Returns:
            Tuple of (label, score). Labels for RoBERTa are usually LABEL_0 (neg), LABEL_1 (neu), LABEL_2 (pos).
        """
        if not text:
            return "neutral", 0.0

        try:
            # RoBERTa base sentiment labels: LABEL_0 -> negative, LABEL_1 -> neutral, LABEL_2 -> positive
            text = self._preprocess_text(text)
            result = self._sentiment_pipe(text, truncation=True, max_length=512)[0]
            label_map = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
            label = result["label"]
            if label in label_map:
                label = label_map[label]

            score = result["score"]

            return label, score
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return "neutral", 0.0

    def _preprocess_text(self, text: str) -> str:
        """
        Remove stopwords and punctuation from the text using NLTK.

        Args:
            text: Raw input text.

        Returns:
            Preprocessed (cleaned) text.
        """
        if not text:
            return ""

        try:
            # Tokenize and filter
            stop_words = set(stopwords.words("english"))
            tokens = word_tokenize(text.lower())
            filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]
            return " ".join(filtered_tokens)
        except Exception as e:
            logger.warning(f"Preprocessing failed for text snippet: {e}")
            return text  # Return original if preprocessing fails

    def extract_keywords(self, texts: List[str], top_n: int = 10) -> List[str]:
        """
        Extract top keywords from a list of texts using Gemini.

        Args:
            texts: List of strings (e.g., negative reviews).
            top_n: Number of keywords to return.

        Returns:
            List of top extracted keywords/phrases.
        """
        if not texts:
            return []

        try:
            logger.info("Extracting keywords via Gemini (Structured Output)...")

            # Combine reviews for context (limit to avoid token overflow)
            reviews_context = "\n".join([f"- {r}" for r in texts[:50]])

            prompt = KEYWORDS_PROMPT.format(top_n=top_n, reviews_context=reviews_context)

            response = self._client.models.generate_content(
                model=self.gemini_model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=KeywordsResponse,
                ),
            )

            return KeywordsResponse.model_validate_json(response.text).keywords
        except Exception as e:
            logger.error(f"Gemini keyword extraction failed: {e}")
            return []

    def generate_insights(self, negative_reviews: List[str], keywords: List[str]) -> AppInsightsResponse:
        """
        Generate developer insights and recommendations using Gemini with structured output.

        Returns:
            AppInsightsResponse object containing summary and recommendations.
        """
        if not negative_reviews:
            return AppInsightsResponse(insights="No negative feedback to analyze.", recommendations=["N/A"])

        try:
            logger.info("Generating developer insights via Gemini (Structured Output)...")

            # Combine reviews for context (limit to avoid token overflow)
            reviews_context = "\n".join([f"- {r}" for r in negative_reviews[:50]])
            keywords_context = ", ".join(keywords)

            prompt = INSIGHTS_PROMPT.format(keywords_context=keywords_context, reviews_context=reviews_context)

            response = self._client.models.generate_content(
                model=self.gemini_model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AppInsightsResponse,
                ),
            )

            # The response.text will be a JSON string that matches the Pydantic schema
            return AppInsightsResponse.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"Gemini insight generation failed: {e}")
            return AppInsightsResponse(
                insights="Failed to generate insights.", recommendations=["Check logs for errors."]
            )
