from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sqlite3
import os
import json

router = APIRouter(prefix="/crud", tags=["crud"])

class TableRow(BaseModel):
    data: Dict[str, Any]

def get_db_connection():
    """Get SQLite connection with simulation fallback"""
    if os.getenv("SIMULATION_MODE", "false").lower() == "true":
        return None
    try:
        return sqlite3.connect("data/app.db")
    except:
        return None

@router.get("/tables/{table_name}/rows")
def get_table_rows(
    table_name: str,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=1000)
):
    """Get paginated table rows"""
    conn = get_db_connection()
    
    if not conn:
        # Simulation mode
        mock_data = {
            "users": [
                {"id": 1, "username": "admin", "email": "admin@atom.cloud", "active": True},
                {"id": 2, "username": "user1", "email": "user1@atom.cloud", "active": True}
            ],
            "projects": [
                {"id": 1, "name": "E-commerce Platform", "status": "autonomous"},
                {"id": 2, "name": "Analytics Dashboard", "status": "learning"}
            ]
        }
        
        data = mock_data.get(table_name, [])
        offset = (page - 1) * limit
        
        return {
            "rows": data[offset:offset + limit],
            "total": len(data),
            "page": page,
            "limit": limit
        }
    
    try:
        cursor = conn.cursor()
        offset = (page - 1) * limit
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        
        # Get paginated data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit} OFFSET {offset}")
        columns = [desc[0] for desc in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return {
            "rows": rows,
            "total": total,
            "page": page,
            "limit": limit
        }
    finally:
        conn.close()

@router.post("/tables/{table_name}/rows")
def create_table_row(table_name: str, row: TableRow):
    """Create new table row"""
    conn = get_db_connection()
    
    if not conn:
        # Simulation mode
        return {"id": 999, "message": "Row created (simulation)", **row.data}
    
    try:
        cursor = conn.cursor()
        columns = list(row.data.keys())
        values = list(row.data.values())
        placeholders = ",".join(["?" for _ in values])
        
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        cursor.execute(query, values)
        conn.commit()
        
        return {"id": cursor.lastrowid, "message": "Row created successfully"}
    finally:
        conn.close()

@router.put("/tables/{table_name}/rows/{row_id}")
def update_table_row(table_name: str, row_id: int, row: TableRow):
    """Update existing table row"""
    conn = get_db_connection()
    
    if not conn:
        # Simulation mode
        return {"message": "Row updated (simulation)", **row.data}
    
    try:
        cursor = conn.cursor()
        set_clause = ",".join([f"{col} = ?" for col in row.data.keys()])
        values = list(row.data.values()) + [row_id]
        
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Row not found")
        
        return {"message": "Row updated successfully"}
    finally:
        conn.close()

@router.delete("/tables/{table_name}/rows/{row_id}")
def delete_table_row(table_name: str, row_id: int):
    """Delete table row"""
    conn = get_db_connection()
    
    if not conn:
        # Simulation mode
        return {"message": "Row deleted (simulation)"}
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Row not found")
        
        return {"message": "Row deleted successfully"}
    finally:
        conn.close()