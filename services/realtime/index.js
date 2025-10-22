const WebSocket = require('ws');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');
require('dotenv').config();

const pool = new Pool({
  host: process.env.POSTGRES_HOST,
  port: process.env.POSTGRES_PORT,
  user: process.env.POSTGRES_USER,
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB,
});

const JWT_SECRET = process.env.AUTH_JWT_SECRET;

const wss = new WebSocket.Server({ port: 4000 });

wss.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const token = url.searchParams.get('token');
  const workspace = url.searchParams.get('workspace');

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    ws.userId = decoded.sub;
    ws.workspaceId = workspace;
    console.log(`Client connected: ${ws.userId} for workspace ${workspace}`);
  } catch (err) {
    ws.close();
    return;
  }

  ws.on('message', (message) => {
    const data = JSON.parse(message);
    if (data.type === 'subscribe') {
      ws.channel = data.channel;
      console.log(`Subscribed to ${data.channel}`);
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Listen for NOTIFY
pool.connect((err, client) => {
  if (err) throw err;
  client.on('notification', (msg) => {
    const payload = JSON.parse(msg.payload);
    wss.clients.forEach((ws) => {
      if (ws.readyState === WebSocket.OPEN && ws.channel === payload.channel && ws.workspaceId === payload.workspace_id) {
        ws.send(JSON.stringify({ type: 'event', channel: payload.channel, payload: payload.data }));
      }
    });
  });
  client.query('LISTEN projects_changes');
});

console.log('Realtime service running on port 4000');
