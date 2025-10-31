#!/usr/bin/env python3
"""
Phase I.5 - Consensus Bus
Message broker for agent coordination and consensus building
"""

import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
MESSAGES_PUBLISHED = Counter('consensus_messages_published_total', 'Total messages published', ['topic'])
MESSAGES_CONSUMED = Counter('consensus_messages_consumed_total', 'Total messages consumed', ['topic'])
ACTIVE_CONNECTIONS = Counter('consensus_active_connections', 'Active WebSocket connections')

app = FastAPI(title="Consensus Bus", version="1.0.0")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SIMULATION_MODE = os.getenv('SIMULATION_MODE', 'true').lower() == 'true'

# In-memory message store for simulation
message_store = {}
active_connections = {}
topic_subscribers = {}

class Message(BaseModel):
    message_id: str
    topic: str
    payload: Dict[str, Any]
    timestamp: str
    source: str
    metadata: Optional[Dict[str, Any]] = {}

class PublishRequest(BaseModel):
    topic: str
    payload: Dict[str, Any]
    source: str
    metadata: Optional[Dict[str, Any]] = {}

class SubscribeRequest(BaseModel):
    topics: List[str]
    agent_id: str
    filters: Optional[Dict[str, Any]] = {}

def generate_message_id() -> str:
    """Generate unique message ID"""
    return f"msg-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(message_store)}"

async def store_message(message: Message):
    """Store message in topic"""
    topic = message.topic
    if topic not in message_store:
        message_store[topic] = []
    
    message_store[topic].append(message)
    
    # Keep only last 1000 messages per topic
    if len(message_store[topic]) > 1000:
        message_store[topic] = message_store[topic][-1000:]

async def notify_subscribers(message: Message):
    """Notify all subscribers of new message"""
    topic = message.topic
    
    if topic in topic_subscribers:
        for connection_id, websocket in topic_subscribers[topic].items():
            try:
                await websocket.send_json({
                    "type": "message",
                    "message": message.dict()
                })
            except Exception as e:
                logger.warning(f"Failed to send message to {connection_id}: {e}")
                # Remove dead connection
                if connection_id in topic_subscribers[topic]:
                    del topic_subscribers[topic][connection_id]

@app.post("/v1/publish")
async def publish_message(request: PublishRequest):
    """Publish message to topic"""
    message_id = generate_message_id()
    
    message = Message(
        message_id=message_id,
        topic=request.topic,
        payload=request.payload,
        timestamp=datetime.utcnow().isoformat(),
        source=request.source,
        metadata=request.metadata or {}
    )
    
    # Store message
    await store_message(message)
    
    # Notify subscribers
    await notify_subscribers(message)
    
    MESSAGES_PUBLISHED.labels(topic=request.topic).inc()
    
    logger.info(f"Published message {message_id} to topic {request.topic}")
    
    return {
        "message_id": message_id,
        "topic": request.topic,
        "status": "published",
        "timestamp": message.timestamp
    }

@app.get("/v1/topics/{topic}/messages")
async def get_topic_messages(
    topic: str,
    limit: int = 100,
    since: Optional[str] = None
):
    """Get messages from topic"""
    if topic not in message_store:
        return {"topic": topic, "messages": [], "count": 0}
    
    messages = message_store[topic]
    
    # Filter by timestamp if provided
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            messages = [
                msg for msg in messages 
                if datetime.fromisoformat(msg.timestamp.replace('Z', '+00:00')) > since_dt
            ]
        except ValueError:
            pass
    
    # Apply limit
    messages = messages[-limit:]
    
    return {
        "topic": topic,
        "messages": [msg.dict() for msg in messages],
        "count": len(messages)
    }

@app.get("/v1/topics")
async def list_topics():
    """List all available topics"""
    topics = []
    for topic, messages in message_store.items():
        topics.append({
            "topic": topic,
            "message_count": len(messages),
            "last_message": messages[-1].timestamp if messages else None
        })
    
    return {"topics": topics}

@app.websocket("/v1/subscribe")
async def websocket_subscribe(websocket: WebSocket):
    """WebSocket endpoint for real-time message subscription"""
    await websocket.accept()
    connection_id = f"conn-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{len(active_connections)}"
    active_connections[connection_id] = websocket
    ACTIVE_CONNECTIONS.inc()
    
    try:
        # Wait for subscription request
        data = await websocket.receive_json()
        subscribe_req = SubscribeRequest(**data)
        
        # Subscribe to topics
        for topic in subscribe_req.topics:
            if topic not in topic_subscribers:
                topic_subscribers[topic] = {}
            topic_subscribers[topic][connection_id] = websocket
        
        logger.info(f"Agent {subscribe_req.agent_id} subscribed to topics: {subscribe_req.topics}")
        
        # Send confirmation
        await websocket.send_json({
            "type": "subscription_confirmed",
            "topics": subscribe_req.topics,
            "connection_id": connection_id
        })
        
        # Keep connection alive
        while True:
            try:
                # Send periodic heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                await asyncio.sleep(30)
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
    finally:
        # Cleanup connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        
        # Remove from topic subscriptions
        for topic_subs in topic_subscribers.values():
            if connection_id in topic_subs:
                del topic_subs[connection_id]
        
        ACTIVE_CONNECTIONS.dec()
        logger.info(f"Connection {connection_id} closed")

@app.post("/v1/consensus/start")
async def start_consensus_round(
    topic: str,
    proposal: Dict[str, Any],
    participants: List[str],
    timeout_minutes: int = 10
):
    """Start consensus round among participants"""
    round_id = f"consensus-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    consensus_message = {
        "round_id": round_id,
        "proposal": proposal,
        "participants": participants,
        "timeout_at": (datetime.utcnow() + timedelta(minutes=timeout_minutes)).isoformat(),
        "votes": {},
        "status": "active"
    }
    
    # Publish consensus start message
    await publish_message(PublishRequest(
        topic=f"consensus-{topic}",
        payload=consensus_message,
        source="consensus-bus",
        metadata={"type": "consensus_start"}
    ))
    
    return {
        "round_id": round_id,
        "status": "started",
        "participants": participants,
        "timeout_at": consensus_message["timeout_at"]
    }

@app.post("/v1/consensus/{round_id}/vote")
async def submit_consensus_vote(
    round_id: str,
    voter_id: str,
    vote: str,
    rationale: Optional[str] = None
):
    """Submit vote for consensus round"""
    vote_message = {
        "round_id": round_id,
        "voter_id": voter_id,
        "vote": vote,
        "rationale": rationale,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Publish vote message
    await publish_message(PublishRequest(
        topic=f"consensus-votes",
        payload=vote_message,
        source=voter_id,
        metadata={"type": "consensus_vote", "round_id": round_id}
    ))
    
    return {
        "round_id": round_id,
        "voter_id": voter_id,
        "vote": vote,
        "status": "recorded"
    }

@app.get("/v1/status")
async def get_bus_status():
    """Get consensus bus status"""
    return {
        "service": "consensus-bus",
        "status": "healthy",
        "simulation_mode": SIMULATION_MODE,
        "active_connections": len(active_connections),
        "topics": len(message_store),
        "total_messages": sum(len(msgs) for msgs in message_store.values()),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "consensus-bus",
        "timestamp": datetime.utcnow().isoformat(),
        "simulation_mode": SIMULATION_MODE
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return JSONResponse(
        content=generate_latest().decode('utf-8'),
        media_type="text/plain"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)