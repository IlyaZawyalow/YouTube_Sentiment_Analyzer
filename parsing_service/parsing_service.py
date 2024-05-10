from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from worker import Worker

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class VideoInput(BaseModel):
    video_url: str
    key: str = 'AIzaSyDAUsif0K6XxybhWdmQ3XgNGzonyJB-63w'

@app.post("/parse/", response_model=dict)
async def parse_video(video: VideoInput):
    video_id = parse_youtube_url(video.video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
 
    parse_comments(video_id, video.key)
    return {"video_id": video_id}

def parse_comments(video_id: str, key: str):
    worker = Worker(key)
    worker.run(video_id)

def parse_youtube_url(url: str) -> str:
    pattern = re.compile(
        r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})')
    match = pattern.search(url)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
