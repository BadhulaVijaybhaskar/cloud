from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymilvus import connections, Collection
from ingestion.embed import EmbeddingService
import os

app = FastAPI(title="Vector Search Service")

embedding_service = EmbeddingService()
connections.connect("default", host=os.getenv("MILVUS_HOST", "localhost"), port="19530")

class QueryRequest(BaseModel):
    query: str
    collection: str = "documents"
    top_k: int = 5

class QueryResponse(BaseModel):
    results: List[dict]

@app.post("/v1/vector/query", response_model=QueryResponse)
async def query_vectors(request: QueryRequest):
    try:
        collection = Collection(request.collection)
        query_embedding = embedding_service.get_embedding(request.query)
        
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            [query_embedding], 
            "embedding", 
            search_params, 
            limit=request.top_k,
            output_fields=["text"]
        )
        
        response_results = []
        for hits in results:
            for hit in hits:
                response_results.append({
                    "text": hit.entity.get("text"),
                    "score": hit.score,
                    "id": hit.id
                })
        
        return QueryResponse(results=response_results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}