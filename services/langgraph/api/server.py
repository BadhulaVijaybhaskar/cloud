from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import os
import psycopg2
import redis
from main import orchestrator
from .routes import jobs, graphs

app = FastAPI(title="LangGraph Orchestration Service")
app.include_router(jobs.router)
app.include_router(graphs.router)

# Metrics
job_counter = Counter('langgraph_jobs_total', 'Total jobs processed')
job_duration = Histogram('langgraph_job_duration_seconds', 'Job duration')

# Database connection
def get_db():
    return psycopg2.connect(os.getenv('DATABASE_URL'))

# Redis connection
redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")

@app.on_event("startup")
async def startup():
    print("LangGraph Orchestration Service started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)