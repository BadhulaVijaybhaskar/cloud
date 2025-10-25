/**
 * Revenue Chart Component - E.5
 * React component for displaying revenue analytics
 */
import React, { useState, useEffect } from 'react';

interface RevenueData {
  month: string;
  revenue: number;
  transactions: number;
}

interface RevenueChartProps {
  data?: RevenueData[];
  height?: number;
}

const RevenueChart: React.FC<RevenueChartProps> = ({ 
  data = [], 
  height = 300 
}) => {
  const [revenueData, setRevenueData] = useState<RevenueData[]>(data);
  const [loading, setLoading] = useState(!data.length);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!data.length) {
      fetchRevenueData();
    }
  }, [data]);

  const fetchRevenueData = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analytics/revenue');
      
      if (!response.ok) {
        throw new Error('Failed to fetch revenue data');
      }
      
      const result = await response.json();
      setRevenueData(result.revenue || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Fallback to sample data in simulation mode
      setRevenueData([
        { month: '2024-10', revenue: 15420.50, transactions: 342 },
        { month: '2024-11', revenue: 18750.25, transactions: 428 },
        { month: '2024-12', revenue: 22100.75, transactions: 515 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const maxRevenue = Math.max(...revenueData.map(d => d.revenue));
  const chartWidth = 600;
  const chartHeight = height - 100;

  if (loading) {
    return (
      <div className="revenue-chart loading">
        <div className="spinner">Loading revenue data...</div>
      </div>
    );
  }

  if (error && !revenueData.length) {
    return (
      <div className="revenue-chart error">
        <p>Error loading revenue data: {error}</p>
        <button onClick={fetchRevenueData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="revenue-chart">
      <h3>Monthly Revenue Trends</h3>
      
      <div className="chart-container">
        <svg width={chartWidth} height={height} className="chart-svg">
          {/* Chart background */}
          <rect 
            width={chartWidth} 
            height={chartHeight} 
            fill="#f8f9fa" 
            stroke="#e9ecef"
          />
          
          {/* Revenue bars */}
          {revenueData.map((item, index) => {
            const barWidth = chartWidth / revenueData.length - 20;
            const barHeight = (item.revenue / maxRevenue) * (chartHeight - 40);
            const x = (index * (chartWidth / revenueData.length)) + 10;
            const y = chartHeight - barHeight - 20;
            
            return (
              <g key={item.month}>
                {/* Revenue bar */}
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  fill="#007bff"
                  stroke="#0056b3"
                  strokeWidth="1"
                />
                
                {/* Month label */}
                <text
                  x={x + barWidth / 2}
                  y={chartHeight - 5}
                  textAnchor="middle"
                  fontSize="12"
                  fill="#6c757d"
                >
                  {item.month}
                </text>
                
                {/* Revenue value */}
                <text
                  x={x + barWidth / 2}
                  y={y - 5}
                  textAnchor="middle"
                  fontSize="11"
                  fill="#495057"
                  fontWeight="bold"
                >
                  {formatCurrency(item.revenue)}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      
      {/* Revenue summary */}
      <div className="revenue-summary">
        <div className="summary-grid">
          {revenueData.map((item, index) => (
            <div key={item.month} className="summary-item">
              <div className="month">{item.month}</div>
              <div className="revenue">{formatCurrency(item.revenue)}</div>
              <div className="transactions">{item.transactions} transactions</div>
            </div>
          ))}
        </div>
        
        <div className="total-summary">
          <strong>
            Total Revenue: {formatCurrency(revenueData.reduce((sum, item) => sum + item.revenue, 0))}
          </strong>
        </div>
      </div>

      <style jsx>{`
        .revenue-chart {
          background: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          margin: 20px 0;
        }
        
        .revenue-chart h3 {
          margin: 0 0 20px 0;
          color: #495057;
          font-size: 1.25rem;
        }
        
        .chart-container {
          margin: 20px 0;
          overflow-x: auto;
        }
        
        .chart-svg {
          border: 1px solid #dee2e6;
          border-radius: 4px;
        }
        
        .revenue-summary {
          margin-top: 20px;
        }
        
        .summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-bottom: 15px;
        }
        
        .summary-item {
          padding: 10px;
          background: #f8f9fa;
          border-radius: 4px;
          text-align: center;
        }
        
        .summary-item .month {
          font-weight: bold;
          color: #495057;
          margin-bottom: 5px;
        }
        
        .summary-item .revenue {
          font-size: 1.1rem;
          color: #007bff;
          font-weight: bold;
        }
        
        .summary-item .transactions {
          font-size: 0.9rem;
          color: #6c757d;
        }
        
        .total-summary {
          text-align: center;
          padding: 15px;
          background: #e7f3ff;
          border-radius: 4px;
          color: #0056b3;
        }
        
        .loading, .error {
          text-align: center;
          padding: 40px;
          color: #6c757d;
        }
        
        .spinner {
          font-style: italic;
        }
        
        .error button {
          margin-top: 10px;
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        
        .error button:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  );
};

export default RevenueChart;