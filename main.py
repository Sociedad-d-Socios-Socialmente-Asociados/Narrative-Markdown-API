from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routes import generate

app = FastAPI(
    title="Narrative Markdown API",
    version="0.1.0",
    description="This is an API for the Narrative Markdown.",
)

# Add CORS middleware to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
