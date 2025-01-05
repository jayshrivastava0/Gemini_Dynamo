# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

from services.genai import YoutubeProcessor, GeminiProcessor

class VideoAnalysisRequest(BaseModel):
    youtube_link: HttpUrl

class VideoAnalysisResponse(BaseModel):
    key_concepts: List[Dict[str, str]]

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

genai_processor = GeminiProcessor(
    model_name="gemini-1.5-flash-002",
    project="spry-tesla-437903-t1"
)

@app.post('/analyze_video', response_model=VideoAnalysisResponse)
async def analyze_video(request: VideoAnalysisRequest):
    try:
        processor = YoutubeProcessor(genai_processor=genai_processor)
        
        # Retrieve documents
        result = processor.retrieve_youtube_documents(str(request.youtube_link), verbose=True)
        if not result:
            raise HTTPException(status_code=404, detail="Failed to retrieve video content")

        # Find key concepts
        key_concepts = processor.find_key_concepts(result, verbose=True)
        if not key_concepts:
            raise HTTPException(status_code=404, detail="Failed to extract key concepts")

        return VideoAnalysisResponse(key_concepts=key_concepts)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))