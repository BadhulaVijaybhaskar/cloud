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
export declare class NakshaClient {
    private http;
    private token?;
    private baseUrl;
    constructor(baseUrl: string, token?: string);
    register(email: string, password: string): Promise<{
        token: string;
        user: User;
    }>;
    login(email: string, password: string): Promise<{
        token: string;
        user: User;
    }>;
    me(): Promise<User>;
    presignUpload(params: {
        workspace_id: string;
        key: string;
        contentType: string;
        size: number;
    }): Promise<{
        upload_url: string;
        download_url: string;
        expires_at: string;
    }>;
    listArtifacts(workspace_id: string): Promise<any[]>;
    realtime: {
        connect: (params: {
            token: string;
            workspace: string;
        }) => EventEmitter;
    };
    from(table: string): {
        select: (where?: any) => {
            insert: (obj: any) => Promise<any>;
            update: (obj: any) => Promise<any>;
            delete: () => Promise<void>;
        };
    };
}
export declare function createClient(baseUrl: string, token?: string): NakshaClient;
//# sourceMappingURL=index.d.ts.map