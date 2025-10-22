"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NakshaClient = void 0;
exports.createClient = createClient;
const axios_1 = __importDefault(require("axios"));
const ws_1 = __importDefault(require("ws"));
const events_1 = require("events");
class NakshaClient {
    constructor(baseUrl, token) {
        // Realtime
        this.realtime = {
            connect: (params) => {
                const emitter = new events_1.EventEmitter();
                const ws = new ws_1.default(`${this.baseUrl.replace('http', 'ws')}:4000?token=${params.token}&workspace=${params.workspace}`);
                ws.on('open', () => {
                    emitter.emit('connected');
                });
                ws.on('message', (data) => {
                    const msg = JSON.parse(data);
                    emitter.emit('event', msg);
                });
                ws.on('error', (err) => {
                    emitter.emit('error', err);
                });
                ws.on('close', () => {
                    emitter.emit('disconnected');
                });
                emitter.on('subscribe', (channel) => {
                    ws.send(JSON.stringify({ type: 'subscribe', channel }));
                });
                return emitter;
            }
        };
        this.baseUrl = baseUrl;
        this.token = token;
        this.http = axios_1.default.create({
            baseURL: baseUrl,
            headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
    }
    // Auth methods
    async register(email, password) {
        const res = await this.http.post('/auth/register', { email, password });
        return res.data;
    }
    async login(email, password) {
        const res = await this.http.post('/auth/login', { email, password });
        this.token = res.data.token;
        this.http.defaults.headers.Authorization = `Bearer ${this.token}`;
        return res.data;
    }
    async me() {
        const res = await this.http.get('/auth/me');
        return res.data;
    }
    // Storage methods
    async presignUpload(params) {
        const res = await this.http.post('/storage/presign', params);
        return res.data;
    }
    async listArtifacts(workspace_id) {
        const res = await this.http.get(`/storage/${workspace_id}/list`);
        return res.data;
    }
    // Generic CRUD (would use GraphQL in full implementation)
    from(table) {
        return {
            select: (where) => ({
                insert: async (obj) => {
                    // Mock - in real app, use GraphQL mutation
                    console.log(`Insert into ${table}`, obj);
                    return obj;
                },
                update: async (obj) => {
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
exports.NakshaClient = NakshaClient;
function createClient(baseUrl, token) {
    return new NakshaClient(baseUrl, token);
}
//# sourceMappingURL=index.js.map