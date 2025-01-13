from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import httpx
import json
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.pipeline.health_rag import HealthRAGPipeline

app = FastAPI(
    title="Your Health Companion",
    description="A friendly health monitoring system that helps you understand your health metrics better",
    version="1.0.0"
)

rag_pipeline = HealthRAGPipeline()

class HealthMetrics(BaseModel):
    heart_rate: int = Field(
        ..., 
        description="Your heart rate in beats per minute",
        example=75,
        ge=30,
        le=220
    )
    spo2: int = Field(
        ..., 
        description="Your blood oxygen level in percentage",
        example=98,
        ge=70,
        le=100
    )
    steps: int = Field(
        ..., 
        description="Number of steps you've taken today",
        example=8000,
        ge=0
    )

@app.post("/metrics", 
         summary="Share your health metrics",
         description="Send us your current health metrics, and we'll give you personalized insights!")
async def process_metrics(metrics: HealthMetrics):
    """
    Let's look at your health metrics and give you some helpful insights!
    
    We'll check:
    - How your heart's doing
    - Your oxygen levels
    - Your activity level
    
    And give you personalized recommendations based on trusted health guidelines.
    """
    try:
        # Add timestamp to track when the metrics were recorded
        metrics_dict = {
            **metrics.dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Get personalized insights
        insights = rag_pipeline.generate_insights(metrics_dict)
        
        return {
            "message": "Thanks for sharing your health metrics! Here's what we found.",
            "data": {
                "metrics": metrics_dict,
                "insights": insights
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Oops! Something went wrong while processing your health metrics. Please try again!"
        )

@app.get("/health")
async def health_check():
    """Quick check to make sure everything's running smoothly!"""
    return {
        "status": "All systems go!",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
