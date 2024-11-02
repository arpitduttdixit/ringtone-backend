# main.py (FastAPI application)
from fastapi import FastAPI, HTTPException
from rq import Queue
from redis import Redis
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uuid
import os
from dotenv import load_dotenv

class JobData(BaseModel):
    low: int
    high: int
    
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "random"
    preset: Optional[str] = "ultra_fast"

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_conn = Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=False  # Important: Set to False for job serialization
)
task_queue = Queue(
    "task_queue",
    connection=redis_conn,
    job_timeout='10m'  # Add timeout to prevent jobs from being killed too early
)

@app.get("/")
def index():
    return {
        "responseCode": 200,
        "responseMessage": "success"
    }
    
@app.post("/job")
def post_job(job: JobData):
    low = job.low
    high = job.high
    try:
        job_instance = task_queue.enqueue(
            'tasks.print_num',
            args=(low, high),
            job_timeout='10m'
        )
        return {
            "success": True,
            "jobID": job_instance.id
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Add a test endpoint
@app.get("/test-redis")
def test_redis():
    try:
        redis_conn.ping()
        return {"status": "Connected to Redis successfully"}
    except Exception as e:
        return {"status": "Redis connection failed", "error": str(e)}
    
@app.post("/tts")
async def create_tts(request: TTSRequest):
    try:
        # Enqueue the TTS job
        from tts_job import run_tts_command
        job_id = uuid()
        job = task_queue.enqueue(
            'tts_job.run_tts_command',
            args=(
                request.text,
                job_id,
                request.voice,
                request.preset
            ),
            job_timeout='30m'  # Adjust timeout as needed
        )
        job = task_queue.enqueue(
            'copy.upload_to_drive',
            args=(
                job_id
            ),
            job_timeout='30m'
        )
        
        return {
            "status": "success",
            "job_id": job.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/tts/{job_id}")
async def get_tts_status(job_id: str):
    job = task_queue.fetch_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job.is_finished:
        return {
            "status": "completed",
            "result": job.result
        }
    elif job.is_failed:
        return {
            "status": "failed",
            "error": str(job.exc_info)
        }
    else:
        return {
            "status": "processing"
        }