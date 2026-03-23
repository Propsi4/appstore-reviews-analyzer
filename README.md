# App Store Reviews Analyzer

A professional-grade FastAPI application designed to scrape, analyze, and provide deep insights into App Store reviews using state-of-the-art NLP models (RoBERTa) and Large Language Models (Gemini).

## Features

- **Automated Scraping**: Efficiently retrieves reviews from any App Store country and application.
- **Sentiment Analysis**: Leverages RoBERTa-base-sentiment for precise sentiment classification.
- **Insight Generation**: Uses Google's Gemini Flash to generate actionable developer insights and recommendations from negative feedback.
- **Job Orchestration**: Asynchronous background jobs for processing large volumes of reviews without blocking the API.
- **Database Persistence**: Robust PostgreSQL integration with Alembic for managed migrations.
- **Comprehensive API**: RESTful endpoints for review collection, metrics retrieval, and data export.
- **High Test Coverage**: 95%+ test coverage ensuring reliability and stability.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy + Alembic)
- **Scraping (RSS)**: httpx
- **NLP**: Transformers (RoBERTa)
- **LLM**: Google GenAI (Gemini)
- **Environment**: Poetry, Docker

## Getting Started

### Prerequisites

- Python 3.11.11+
- Poetry
- PostgreSQL (or Docker for containerized setup)
- Google Gemini API Key

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd appstore-reviews-analyzer
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Set up environment variables:
   ```bash
   cp example.env .env
   # Edit .env with your credentials and API keys
   ```

4. Run migrations:
   ```bash
   poetry run alembic upgrade head
   ```

5. Start the application locally:
   ```bash
   poetry run api
   ```

## Docker Setup

### Building the Image

Standard build (defaults to port 8000):
```bash
docker build -t appstore-analyzer .
```

### Running the Container

```bash
docker run -p 8000:8000 --env-file .env appstore-analyzer
```

## Useful Commands

### Alembic Migrations

- **Create a new migration**:
  ```bash
  poetry run alembic revision --autogenerate -m "description"
  ```
- **Apply migrations**:
  ```bash
  poetry run alembic upgrade head
  ```
- **Rollback migration**:
  ```bash
  poetry run alembic downgrade -1
  ```

### Testing and Linting

- **Run tests with coverage**:
  ```bash
  poetry run pytest --cov=src --cov-report=term-missing src/tests/
  ```
- **Lint code**:
  ```bash
  poetry run flake8 src/
  poetry run black src/ --check
  ```

## API Documentation

Once the application is running, you can access the interactive API documentation at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Core Components

- `scripts`: Entrypoint scripts for Docker.
- `src/api`: FastAPI routers and application definition.
- `src/config`: Configuration management.
- `src/db`: Database models and session management.
- `src/interfaces`: Interfaces for data sources and services.
- `src/jobs`: Logic for background review analysis jobs.
- `src/prompts`: Prompt templates for LLM.
- `src/schemas`: Pydantic models for data validation.
- `src/scrappers`: RSS feed scraping implementation.
- `src/services`: Core services for NLP and App Store interaction.
- `src/tests`: Tests for the application.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
