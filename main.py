from fastapi import FastAPI

from src.routes import generate

app = FastAPI(
    title="Narrative Markdown API",
    version="0.1.0",
    description="This is an API for the Narrative Markdown.",
)

app.include_router(generate.router, prefix="/generate", tags=["generate"])


@app.get("/")
async def root():
    """
    Root endpoint for the API.

    Returns:
        dict: A dictionary with a message and a success flag.
    """
    return {"message": "NM API Working!", "success": True}
