"""FastAPI application entry point."""

# Thirdparty imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.api.routers import reviews
from src.config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="REST API for analyzing App Store reviews using NLP and Gemini.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost",
        "http://127.0.0.1:5173",
        "http://127.0.0.1",
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(reviews.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "operational"}


def main():
    """Run main entry point for the API."""
    # Thirdparty imports
    import uvicorn

    uvicorn.run("src.api.main:app", host=settings.api.host, port=settings.api.port, reload=settings.api.reload)


if __name__ == "__main__":
    main()
