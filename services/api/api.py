from fastapi import FastAPI
from typing import Optional

app = FastAPI()

@app.get("/speaker")
async def get_speaker(query: Optional[str] = None):
    return {"topic": "memes about potato",
            "bio": query,
            "topic_description": "he like potato and memes"}

if __name__ == "__main__":

    # run fastapi
    import uvicorn

    uvicorn.run("api:app", host="localhost", port=8000, reload=True)
