# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    curl \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only requirements to cache them in docker layer
COPY pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --without dev

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('punkt_tab')"

# Download sentiment analysis model
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='cardiffnlp/twitter-xlm-roberta-base-sentiment')"

# Copy project (this will NOT copy .env because of .dockerignore)
COPY . /app/

# Install project
RUN poetry install --no-interaction --no-ansi --without dev

# Make scripts executable
RUN chmod +x /app/scripts/*.sh

# Expose the API port
EXPOSE 8000

# Run the application
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["api"]
