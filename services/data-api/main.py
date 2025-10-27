from fastapi import FastAPI, HTTPException
import sqlite3
import os
from prometheus_client import Counter, generate_latest
from schema import router as schema_router
from crud import router as crud_router

app = FastAPI(title="ATOM Data API", version="1.0.0")

app.include_router(schema_router, prefix="/api/data")
app.include_router(crud_router, prefix="/api/data")

# Metrics
query_counter = Counter('data_queries_total', 'Total data queries')

# Database setup
DB_PATH = "/tmp/atom_sim.db" if os.name != 'nt' else "atom_sim.db"
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "true").lower() == "true"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            active BOOLEAN DEFAULT 1
        )
    """)
    # Insert sample data
    cursor.execute("INSERT OR IGNORE INTO projects (id, name, status) VALUES (1, 'E-commerce Platform', 'autonomous')")
    cursor.execute("INSERT OR IGNORE INTO projects (id, name, status) VALUES (2, 'Analytics Dashboard', 'learning')")
    cursor.execute("INSERT OR IGNORE INTO users (id, username, email) VALUES (1, 'admin', 'admin@atom.cloud')")
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "data-api"}

@app.post("/query")
async def execute_query(query_data: dict):
    query_counter.inc()
    sql = query_data.get("sql", "")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        
        if sql.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            conn.close()
            return {"rows": rows, "columns": columns}
        else:
            conn.commit()
            conn.close()
            return {"affected_rows": cursor.rowcount}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tables")
async def get_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"tables": tables}

@app.get("/metrics")
async def metrics():
    return generate_latest()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)