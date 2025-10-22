from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import json
from main import orchestrator

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])

class JobRequest(BaseModel):
    graph_name: str
    input_data: Dict[str, Any]

class JobResponse(BaseModel):
    job_id: str
    status: str
    result: Dict[str, Any] = None

jobs_store = {}

@router.post("/", response_model=JobResponse)
async def create_job(job_request: JobRequest):
    """Enqueue a new workflow job"""
    job_id = str(uuid.uuid4())
    
    try:
        graph = orchestrator.create_graph(job_request.graph_name)
        result = graph.invoke(job_request.input_data)
        
        job_response = JobResponse(
            job_id=job_id,
            status="completed",
            result=result
        )
        jobs_store[job_id] = job_response
        
        return job_response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get job status and result"""
    if job_id not in jobs_store:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return jobs_store[job_id]