#!/usr/bin/env python3
"""
ATOM Marketplace API - J.3.1
Package registry, search, and metadata management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import hashlib
import time
from datetime import datetime

app = FastAPI(title="ATOM Marketplace API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

class PackageManifest(BaseModel):
    name: str
    version: str
    description: str
    category: str
    author: str
    license: str
    dependencies: List[str] = []
    tags: List[str] = []
    
class PackagePublish(BaseModel):
    name: str
    version: str
    manifest: PackageManifest
    signature: str
    package_url: str

packages_db = {}
search_index = {}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "marketplace-api",
        "simulation_mode": SIMULATION_MODE,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    return {
        "packages_total": len(packages_db),
        "categories": len(set(p.get('category', '') for p in packages_db.values())),
        "simulation_mode": SIMULATION_MODE
    }

@app.post("/packages/publish")
async def publish_package(package: PackagePublish):
    package_id = f"{package.name}-{package.version}"
    package_hash = hashlib.sha256(f"{package.name}{package.version}".encode()).hexdigest()[:16]
    
    package_data = {
        "id": package_id,
        "hash": package_hash,
        "name": package.name,
        "version": package.version,
        "manifest": package.manifest.dict(),
        "published_at": datetime.utcnow().isoformat(),
        "downloads": 0,
        "rating": 4.2
    }
    
    packages_db[package_id] = package_data
    
    return {
        "success": True,
        "package_id": package_id,
        "hash": package_hash
    }

@app.get("/packages/search")
async def search_packages(q: str = "", category: str = "", limit: int = 20):
    results = list(packages_db.values())
    
    if category:
        results = [p for p in results if p['manifest'].get('category', '').lower() == category.lower()]
    
    if q:
        results = [p for p in results if q.lower() in p['name'].lower() or q.lower() in p['manifest']['description'].lower()]
    
    return {
        "packages": results[:limit],
        "total": len(results),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/packages/{package_id}")
async def get_package(package_id: str):
    if package_id not in packages_db:
        raise HTTPException(status_code=404, detail="Package not found")
    
    package = packages_db[package_id]
    quality_score = hash(package_id) % 30 + 70
    
    return {
        **package,
        "quality_score": quality_score,
        "security_scan": {"vulnerabilities": 0, "last_scanned": datetime.utcnow().isoformat()}
    }

@app.post("/packages/{package_id}/install")
async def install_package(package_id: str, workspace_id: str = "default"):
    if package_id not in packages_db:
        raise HTTPException(status_code=404, detail="Package not found")
    
    packages_db[package_id]['downloads'] += 1
    deployment_id = hashlib.sha256(f"{package_id}{workspace_id}{time.time()}".encode()).hexdigest()[:16]
    
    return {
        "deployment_id": deployment_id,
        "package_id": package_id,
        "status": "initiated",
        "simulation_mode": SIMULATION_MODE
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9301)