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

2. Set up environment variables:
   ```bash
   cp example.env .env
   # Edit .env with your credentials and API keys
   ```

### Instructions for running the API locally (Docker Compose)

The recommended way to run the API and database locally is using Docker Compose:

```bash
docker compose up --build
```
*This will start a PostgreSQL database container and the FastAPI application container on port 8000, and automatically apply Alembic migrations.*

### Instructions for running the API locally (Manual)

If you prefer to run the API without Docker:

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run migrations (requires a running PostgreSQL instance):
   ```bash
   poetry run alembic upgrade head
   ```

3. Start the application:
   ```bash
   poetry run api
   ```

## Approach and Key Design Decisions

- **Job-Driven Monolith**: The application is structured as a monolith that orchestrates complex workflows (scraping, NLP analysis, and Gemini generation) through asynchronous background tasks (`ReviewAnalysisJob`). This prevents long-running tasks from blocking API responses and allows for robust processing of large review volumes.
- **Hybrid NLP/LLM Pipeline**: We utilize a local, specialized model (`RoBERTa-base-sentiment`) for rapid, cost-effective sentiment classification of individual reviews. We reserve the more powerful Large Language Model (Google Gemini Flash) for generating aggregated, high-level developer insights and actionable recommendations from the processed data.
- **Robust Storage and Deduplication**: PostgreSQL is used to store both raw and processed review data. We enforce deduplication based on the external App Store ID to ensure data integrity across multiple scraping runs.
- **Separation of Concerns**: The project follows a modular structure, clearly separating API routing schemas, background job logic, database models, and external service integrations.

## Sample Report

Here is a sample JSON report showcasing insights for a chosen app (Bitget), obtained from the insights API endpoint:

```json
{
  "app_id": "1482454273",
  "app_name": "Bitget: Crypto Crypto Exchange",
  "country": "us",
  "avg_rating": 2.4,
  "rating_distribution": {
    "1": 45,
    "2": 5,
    "3": 10,
    "4": 20,
    "5": 20
  },
  "top_negative_keywords": [
    "withdrawal",
    "fee",
    "support",
    "verification",
    "scam"
  ],
  "developer_insights": "A significant portion of users are experiencing critical issues with the withdrawal process, citing long delays and unexpected, high fees. Furthermore, the customer support experience is frequently described as unhelpful or unresponsive when users attempt to resolve these withdrawal issues. The KYC verification process is also a pain point, with users finding it complex and prone to failure.",
  "actionable_recommendations": [
    "1. Investigation and Optimization of Withdrawal Pipeline: Conduct an immediate technical audit of the withdrawal infrastructure to identify and fix bottlenecks causing delays.",
    "2. Transparent Fee Structure: Clarify the fee structure for all transactions, particularly withdrawals, within the app UI before the user initiates the transaction.",
    "3. Customer Support Overhaul: Dedicate more resources to customer support, prioritizing tickets related to locked funds and withdrawals."
  ],
  "last_processed_at": "2026-03-24T10:00:00Z"
}
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
