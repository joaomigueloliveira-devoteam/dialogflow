"""Langserve API."""
from fastapi import FastAPI
from fastapi import Response
import os
from pydantic import BaseModel

app = FastAPI(
    title="Basic LLM API",
    description="Basic API for testing purposes",
    version="0.0.0",
)

PROJECT_ID = os.environ.get("_PROJECT_ID", "poc-lamp")
LOCATION = os.environ.get("_LOCATION", "europe-west4")


# generate a / endpoint and say hello world
@app.get("/")
async def home():
    """Home endpoint."""
    return {
        "message": "Hello this is the home endpoint, go to /docs if you want to try the api!"
    }


class Speaker(BaseModel):
    """
    Represents the user request.

    Attributes:
        request (str): The request string for the initial content generation.
        history (list): List of user-model interactions.
        attributes (Attributes): The attributes related to the user input for the content generation.
        documents (list): A list of documents related to the content generation. Provided by Rag.
        generation (str): Output of the model
    """

    query: str


@app.post("/speaker")
async def speaker(message: Speaker) -> Response:
    """Handle invoke request for generic article."""
    return {
        "topic": "memeology and the world",
        "bio": "Brian likes potato and memes",
        "topic_description": "memes about potato, and the world",
    }


if __name__ == "__main__":

    # run fastapi
    import uvicorn

    uvicorn.run("api:app", host="localhost", port=8000, reload=True)
