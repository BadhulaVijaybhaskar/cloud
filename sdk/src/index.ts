import axios, { AxiosInstance } from 'axios';
import WebSocket from 'ws';
import { EventEmitter } from 'events';

export interface User {
  id: string;
  email: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  created_by?: string;
  created_at: string;
}

export interface Item {
  id: string;
  project_id: string;
  data?: any;
  created_at: string;
}

export class NakshaClient {
  private http: AxiosInstance;
  private token?: string;
  private baseUrl: string;

  constructor(baseUrl: string, token?: string) {
    this.baseUrl = baseUrl;
    this.token = token;
    this.http = axios.create({
      baseURL: baseUrl,
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  }

  // Auth methods
  async register(email: string, password: string): Promise<{ token: string; user: User }> {
    const res = await this.http.post('/auth/register', { email, password });
    return res.data;
  }

  async login(email: string, password: string): Promise<{ token: string; user: User }> {
    const res = await this.http.post('/auth/login', { email, password });
    this.token = res.data.token;
    this.http.defaults.headers.Authorization = `Bearer ${this.token}`;
    return res.data;
  }

  async me(): Promise<User> {
    const res = await this.http.get('/auth/me');
    return res.data;
  }

  // Storage methods
  async presignUpload(params: { workspace_id: string; key: string; contentType: string; size: number }): Promise<{ upload_url: string; download_url: string; expires_at: string }> {
    const res = await this.http.post('/storage/presign', params);
    return res.data;
  }

  async listArtifacts(workspace_id: string): Promise<any[]> {
    const res = await this.http.get(`/storage/${workspace_id}/list`);
    return res.data;
  }

  // Realtime
  realtime = {
    connect: (params: { token: string; workspace: string }): EventEmitter => {
      const emitter = new EventEmitter();
      const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}:4000?token=${params.token}&workspace=${params.workspace}`);

      ws.on('open', () => {
        emitter.emit('connected');
      });

      ws.on('message', (data: string) => {
        const msg = JSON.parse(data);
        emitter.emit('event', msg);
      });

      ws.on('error', (err) => {
        emitter.emit('error', err);
      });

      ws.on('close', () => {
        emitter.emit('disconnected');
      });

      emitter.on('subscribe', (channel: string) => {
        ws.send(JSON.stringify({ type: 'subscribe', channel }));
      });

      return emitter;
    }
  };

  // Generic CRUD (would use GraphQL in full implementation)
  from(table: string) {
    return {
      select: (where?: any) => ({
        insert: async (obj: any) => {
          // Mock - in real app, use GraphQL mutation
          console.log(`Insert into ${table}`, obj);
          return obj;
        },
        update: async (obj: any) => {
          console.log(`Update ${table}`, obj);
          return obj;
        },
        delete: async () => {
          console.log(`Delete from ${table}`);
        }
      })
    };
  }
}

export function createClient(baseUrl: string, token?: string): NakshaClient {
  return new NakshaClient(baseUrl, token);
}
