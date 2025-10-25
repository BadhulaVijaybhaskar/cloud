from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Vector Search Service")
Instrumentator().instrument(app).expose(app)

class QueryRequest(BaseModel):
    query: str
    collection: str = "documents"
    top_k: int = 5

class QueryResponse(BaseModel):
    results: List[dict]

@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "vector"}

@app.post("/v1/vector/query", response_model=QueryResponse)
async def query_vectors(request: QueryRequest):
    # Simplified mock response for now
    mock_results = [
        {"text": f"Mock result {i} for query: {request.query}", "score": 0.9 - i*0.1, "id": i}
        for i in range(min(request.top_k, 3))
    ]
    return QueryResponse(results=mock_results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)