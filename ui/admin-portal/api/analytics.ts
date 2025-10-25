/**
 * Admin Portal Analytics API - E.5
 * Business intelligence and analytics endpoints
 */
import { FastAPI } from 'fastapi';
import sqlite3 from 'sqlite3';
import { Request, Response } from 'express';

// Simulated FastAPI-style endpoints for TypeScript
interface RevenueData {
  month: string;
  revenue: number;
  transactions: number;
}

interface UsageData {
  tenant_id: string;
  service: string;
  usage_total: number;
  cost: number;
}

interface AnalyticsResponse {
  revenue: RevenueData[];
  usage: UsageData[];
  summary: {
    total_revenue: number;
    active_tenants: number;
    total_transactions: number;
  };
}

class AnalyticsAPI {
  private dbPath: string;
  
  constructor(dbPath: string = '/tmp/analytics.db') {
    this.dbPath = dbPath;
    this.initDB();
  }
  
  private initDB(): void {
    // Initialize analytics database
    const db = new sqlite3.Database(this.dbPath);
    
    db.serialize(() => {
      db.run(`
        CREATE TABLE IF NOT EXISTS revenue_data (
          id TEXT PRIMARY KEY,
          month TEXT NOT NULL,
          revenue REAL NOT NULL,
          transactions INTEGER NOT NULL,
          created_at INTEGER NOT NULL
        )
      `);
      
      db.run(`
        CREATE TABLE IF NOT EXISTS usage_analytics (
          id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL,
          service TEXT NOT NULL,
          usage_total REAL NOT NULL,
          cost REAL NOT NULL,
          period_start INTEGER NOT NULL,
          period_end INTEGER NOT NULL
        )
      `);
      
      // Insert sample data for simulation
      this.insertSampleData(db);
    });
    
    db.close();
  }
  
  private insertSampleData(db: sqlite3.Database): void {
    const sampleRevenue = [
      { month: '2024-10', revenue: 15420.50, transactions: 342 },
      { month: '2024-11', revenue: 18750.25, transactions: 428 },
      { month: '2024-12', revenue: 22100.75, transactions: 515 }
    ];
    
    const sampleUsage = [
      { tenant_id: 'tenant-001', service: 'marketplace', usage_total: 150.5, cost: 75.25 },
      { tenant_id: 'tenant-002', service: 'analytics', usage_total: 89.2, cost: 44.60 },
      { tenant_id: 'tenant-003', service: 'storage', usage_total: 1024.8, cost: 102.48 }
    ];
    
    sampleRevenue.forEach(item => {
      db.run(`
        INSERT OR REPLACE INTO revenue_data (id, month, revenue, transactions, created_at)
        VALUES (?, ?, ?, ?, ?)
      `, [`rev_${item.month}`, item.month, item.revenue, item.transactions, Date.now()]);
    });
    
    sampleUsage.forEach(item => {
      db.run(`
        INSERT OR REPLACE INTO usage_analytics (id, tenant_id, service, usage_total, cost, period_start, period_end)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `, [`usage_${item.tenant_id}_${item.service}`, item.tenant_id, item.service, 
           item.usage_total, item.cost, Date.now() - 86400000, Date.now()]);
    });
  }
  
  async getRevenue(): Promise<RevenueData[]> {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(this.dbPath);
      
      db.all(`
        SELECT month, revenue, transactions 
        FROM revenue_data 
        ORDER BY month DESC 
        LIMIT 12
      `, (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => ({
            month: row.month,
            revenue: row.revenue,
            transactions: row.transactions
          })));
        }
      });
      
      db.close();
    });
  }
  
  async getUsage(): Promise<UsageData[]> {
    return new Promise((resolve, reject) => {
      const db = new sqlite3.Database(this.dbPath);
      
      db.all(`
        SELECT tenant_id, service, usage_total, cost
        FROM usage_analytics
        ORDER BY cost DESC
        LIMIT 50
      `, (err, rows: any[]) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows.map(row => ({
            tenant_id: row.tenant_id,
            service: row.service,
            usage_total: row.usage_total,
            cost: row.cost
          })));
        }
      });
      
      db.close();
    });
  }
  
  async getAnalytics(): Promise<AnalyticsResponse> {
    const revenue = await this.getRevenue();
    const usage = await this.getUsage();
    
    const summary = {
      total_revenue: revenue.reduce((sum, item) => sum + item.revenue, 0),
      active_tenants: new Set(usage.map(item => item.tenant_id)).size,
      total_transactions: revenue.reduce((sum, item) => sum + item.transactions, 0)
    };
    
    return { revenue, usage, summary };
  }
}

// Export for use in Next.js API routes
export const analyticsAPI = new AnalyticsAPI();

// Simulated API endpoints
export async function GET_analytics_revenue(req: Request, res: Response) {
  try {
    const revenue = await analyticsAPI.getRevenue();
    res.json({ revenue, status: 'success' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch revenue data' });
  }
}

export async function GET_analytics_usage(req: Request, res: Response) {
  try {
    const usage = await analyticsAPI.getUsage();
    res.json({ usage, status: 'success' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch usage data' });
  }
}

export async function GET_analytics_summary(req: Request, res: Response) {
  try {
    const analytics = await analyticsAPI.getAnalytics();
    res.json(analytics);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch analytics' });
  }
}

// Health check
export async function GET_health(req: Request, res: Response) {
  res.json({
    status: 'ok',
    service: 'admin-portal-api',
    timestamp: Date.now()
  });
}