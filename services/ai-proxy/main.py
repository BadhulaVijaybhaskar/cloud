from fastapi import FastAPI
import os
import random
from prometheus_client import Counter, generate_latest

app = FastAPI(title="ATOM AI Proxy", version="1.0.0")

# Metrics
ai_counter = Counter('ai_requests_total', 'Total AI requests', ['type'])

SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

# Canned AI responses for simulation
SQL_SUGGESTIONS = [
    {
        "suggestion": "SELECT COUNT(*) FROM users WHERE active = true",
        "explanation": "Count all active users in the system"
    },
    {
        "suggestion": "SELECT name, status, created_at FROM projects ORDER BY created_at DESC LIMIT 10",
        "explanation": "Get the 10 most recently created projects"
    },
    {
        "suggestion": "SELECT AVG(performance_score) FROM projects WHERE status = 'active'",
        "explanation": "Calculate average performance score for active projects"
    }
]

OPTIMIZATION_SUGGESTIONS = [
    {
        "type": "performance",
        "title": "Database Query Optimization",
        "description": "Add index on frequently queried columns",
        "impact": "High",
        "confidence": 94
    },
    {
        "type": "security", 
        "title": "Enable Rate Limiting",
        "description": "Implement API rate limiting for better security",
        "impact": "Medium",
        "confidence": 87
    },
    {
        "type": "cost",
        "title": "Resource Right-sizing",
        "description": "Optimize container resource allocation",
        "impact": "Medium", 
        "confidence": 91
    }
]

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-proxy"}

@app.post("/sql/suggest")
async def sql_suggest(context: dict):
    ai_counter.labels(type="sql_suggest").inc()
    
    if SIMULATION_MODE:
        suggestion = random.choice(SQL_SUGGESTIONS)
        return {
            "suggestion": suggestion["suggestion"],
            "explanation": suggestion["explanation"],
            "confidence": random.randint(85, 99),
            "simulation": True
        }
    
    # In live mode, would call OpenAI/HuggingFace
    return {"error": "AI service not configured", "simulation": False}

@app.post("/optimize/suggest")
async def optimization_suggest(context: dict):
    ai_counter.labels(type="optimize").inc()
    
    suggestions = random.sample(OPTIMIZATION_SUGGESTIONS, 2)
    return {
        "suggestions": suggestions,
        "simulation": SIMULATION_MODE
    }

@app.post("/query-ai")
async def query_ai(query: dict):
    ai_counter.labels(type="query").inc()
    
    natural_query = query.get("query", "")
    
    responses = {
        "user count": "SELECT COUNT(*) FROM users",
        "active projects": "SELECT * FROM projects WHERE status = 'active'",
        "performance": "SELECT AVG(performance_score) FROM projects"
    }
    
    for key, sql in responses.items():
        if key in natural_query.lower():
            return {
                "sql": sql,
                "explanation": f"Generated SQL for: {natural_query}",
                "confidence": 92
            }
    
    return {
        "sql": "SELECT 1",
        "explanation": "Default query - please be more specific",
        "confidence": 50
    }

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8017)