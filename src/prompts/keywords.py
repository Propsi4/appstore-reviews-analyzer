"""System prompt for extracting keywords from app reviews using Gemini."""

SYSTEM_PROMPT = """
Analyze the following app reviews and extract the top {top_n} keywords or short phrases.
These keywords should represent the main themes, common user complaints, or highly-praised features mentioned in the reviews.

Reviews:
{reviews_context}

Return only the keywords that are most characteristic of this specific collection of reviews.
"""
