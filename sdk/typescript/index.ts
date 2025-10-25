/**
 * ATOM SDK - TypeScript Client Library
 * Provides easy access to ATOM Cloud marketplace and services
 */
import axios, { AxiosInstance, AxiosResponse } from 'axios';

export interface WPKData {
  name: string;
  version: string;
  content: any;
}

export interface WPKResponse {
  id?: string;
  status: string;
  message?: string;
  error?: string;
}

export interface MarketplaceResponse {
  wpks: Array<{
    id: string;
    name: string;
    version: string;
    status: string;
    created_at: number;
  }>;
  count: number;
  error?: string;
}

export class AtomClient {
  private client: AxiosInstance;
  
  constructor(baseUrl: string = 'http://localhost:8050', apiKey?: string) {
    this.client = axios.create({
      baseURL: baseUrl,
      headers: apiKey ? { Authorization: `Bearer ${apiKey}` } : {}
    });
  }
  
  async publishWPK(wpkData: WPKData, signature?: string): Promise<WPKResponse> {
    try {
      const payload = {
        name: wpkData.name,
        version: wpkData.version,
        content: wpkData.content,
        signature: signature || `sim-sig-${Date.now()}`
      };
      
      const response = await this.client.post('/wpk/upload', payload);
      return response.data;
    } catch (error: any) {
      return { status: 'failed', error: error.message };
    }
  }
  
  async listWorkflows(status?: string): Promise<MarketplaceResponse> {
    try {
      const params = status ? { status } : {};
      const response = await this.client.get('/wpk/list', { params });
      return response.data;
    } catch (error: any) {
      return { wpks: [], count: 0, error: error.message };
    }
  }
  
  async approveWPK(id: string, reason: string = 'Approved via SDK'): Promise<WPKResponse> {
    try {
      const response = await this.client.post(`/wpk/review/${id}`, {
        status: 'approved',
        reason
      });
      return response.data;
    } catch (error: any) {
      return { status: 'failed', error: error.message };
    }
  }
  
  async rejectWPK(id: string, reason: string = 'Rejected via SDK'): Promise<WPKResponse> {
    try {
      const response = await this.client.post(`/wpk/review/${id}`, {
        status: 'rejected',
        reason
      });
      return response.data;
    } catch (error: any) {
      return { status: 'failed', error: error.message };
    }
  }
  
  async health(): Promise<any> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error: any) {
      return { status: 'unhealthy', error: error.message };
    }
  }
}

export function createClient(baseUrl?: string, apiKey?: string): AtomClient {
  return new AtomClient(baseUrl, apiKey);
}

// Test function for CLI usage
if (process.argv.includes('--test')) {
  console.log('ATOM SDK TypeScript - Test Mode');
  const client = createClient();
  
  client.health().then(result => {
    console.log('Health check:', JSON.stringify(result, null, 2));
  }).catch(err => {
    console.log('Health check failed:', err.message);
  });
  
  const testWPK = {
    name: 'test-workflow-ts',
    version: '1.0.0',
    content: { steps: ['init', 'process', 'cleanup'] }
  };
  
  client.publishWPK(testWPK).then(result => {
    console.log('Publish result:', JSON.stringify(result, null, 2));
  }).catch(err => {
    console.log('Publish failed:', err.message);
  });
}