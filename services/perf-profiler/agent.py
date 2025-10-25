#!/usr/bin/env python3
"""
Performance Profiler Agent - Phase C.2
Benchmarks service endpoints and stores metrics
"""

import asyncio
import aiohttp
import time
import statistics
import sqlite3
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class BenchmarkResult:
    service: str
    endpoint: str
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput: float
    error_rate: float
    test_duration_sec: int
    concurrent_users: int

class PerformanceProfiler:
    def __init__(self, db_path: str = "perf_metrics.db"):
        self.db_path = db_path
        self.services = {
            "registry": "http://localhost:8001",
            "runtime": "http://localhost:8002", 
            "insight": "http://localhost:8003",
            "predictive": "http://localhost:8010"
        }
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for fallback"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS perf_metrics (
                id TEXT PRIMARY KEY,
                service TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                p95_ms REAL NOT NULL,
                throughput REAL NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                p50_ms REAL,
                p99_ms REAL,
                error_rate REAL,
                test_duration_sec INTEGER DEFAULT 30,
                concurrent_users INTEGER DEFAULT 10
            )
        """)
        conn.commit()
        conn.close()
    
    async def benchmark_endpoint(self, service: str, base_url: str, endpoint: str = "/healthz", 
                                duration: int = 30, concurrent: int = 10) -> BenchmarkResult:
        """Benchmark a single endpoint"""
        url = f"{base_url}{endpoint}"
        response_times = []
        errors = 0
        total_requests = 0
        
        async def make_request(session: aiohttp.ClientSession):
            nonlocal errors, total_requests
            try:
                start_time = time.time()
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    await response.text()
                    end_time = time.time()
                    response_times.append((end_time - start_time) * 1000)
                    total_requests += 1
                    if response.status >= 400:
                        errors += 1
            except Exception:
                errors += 1
                total_requests += 1
        
        # Run benchmark
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration:
                tasks = [make_request(session) for _ in range(concurrent)]
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.1)  # Brief pause between batches
        
        # Calculate metrics
        if not response_times:
            return BenchmarkResult(
                service=service, endpoint=endpoint, p50_ms=999999, p95_ms=999999, 
                p99_ms=999999, throughput=0, error_rate=100, 
                test_duration_sec=duration, concurrent_users=concurrent
            )
        
        response_times.sort()
        p50 = statistics.median(response_times)
        p95 = response_times[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0]
        p99 = response_times[int(len(response_times) * 0.99)] if len(response_times) > 1 else response_times[0]
        
        throughput = total_requests / duration
        error_rate = (errors / total_requests * 100) if total_requests > 0 else 100
        
        return BenchmarkResult(
            service=service, endpoint=endpoint, p50_ms=p50, p95_ms=p95, p99_ms=p99,
            throughput=throughput, error_rate=error_rate,
            test_duration_sec=duration, concurrent_users=concurrent
        )
    
    def store_result(self, result: BenchmarkResult) -> str:
        """Store benchmark result in database"""
        import uuid
        result_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO perf_metrics 
            (id, service, endpoint, p95_ms, throughput, p50_ms, p99_ms, error_rate, 
             test_duration_sec, concurrent_users)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result_id, result.service, result.endpoint, result.p95_ms, result.throughput,
            result.p50_ms, result.p99_ms, result.error_rate, 
            result.test_duration_sec, result.concurrent_users
        ))
        conn.commit()
        conn.close()
        
        return result_id
    
    def check_performance_budget(self, result: BenchmarkResult) -> bool:
        """Check if result violates P-6 performance budget (p95 < 800ms)"""
        return result.p95_ms <= 800.0
    
    async def send_to_insight_engine(self, result: BenchmarkResult):
        """Send metrics to Insight Engine if available"""
        try:
            insight_url = "http://localhost:8003/metrics/import"
            payload = {
                "source": "perf-profiler",
                "metrics": {
                    "service": result.service,
                    "endpoint": result.endpoint,
                    "p95_latency_ms": result.p95_ms,
                    "throughput_rps": result.throughput,
                    "error_rate_percent": result.error_rate
                },
                "timestamp": datetime.now().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(insight_url, json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        print(f"✓ Sent metrics to Insight Engine for {result.service}")
                    else:
                        print(f"⚠ Failed to send to Insight Engine: {response.status}")
        except Exception as e:
            print(f"⚠ Insight Engine unavailable: {e}")
    
    async def profile_all_services(self, duration: int = 30) -> List[BenchmarkResult]:
        """Profile all configured services"""
        results = []
        
        for service_name, base_url in self.services.items():
            print(f"🔍 Profiling {service_name} at {base_url}")
            
            # Test health endpoint
            result = await self.benchmark_endpoint(service_name, base_url, "/healthz", duration)
            results.append(result)
            
            # Store result
            result_id = self.store_result(result)
            
            # Send to Insight Engine
            await self.send_to_insight_engine(result)
            
            # Check performance budget
            budget_ok = self.check_performance_budget(result)
            status = "✓ PASS" if budget_ok else "✗ FAIL"
            
            print(f"  {status} p95: {result.p95_ms:.1f}ms, throughput: {result.throughput:.1f} req/s, errors: {result.error_rate:.1f}%")
            
            if not budget_ok:
                print(f"  ⚠ Performance budget violation! p95 {result.p95_ms:.1f}ms > 800ms")
        
        return results
    
    def get_latest_metrics(self, limit: int = 50) -> List[Dict]:
        """Get latest performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT service, endpoint, p95_ms, throughput, error_rate, timestamp
            FROM perf_metrics 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "service": row[0],
                "endpoint": row[1], 
                "p95_ms": row[2],
                "throughput": row[3],
                "error_rate": row[4],
                "timestamp": row[5]
            })
        
        conn.close()
        return results

async def main():
    """Main profiler execution"""
    profiler = PerformanceProfiler()
    
    print("🚀 Starting Performance Profiler Agent")
    print("=" * 50)
    
    # Profile all services
    results = await profiler.profile_all_services(duration=10)  # Shorter for demo
    
    # Summary
    print("\n📊 Performance Summary")
    print("=" * 50)
    
    violations = [r for r in results if not profiler.check_performance_budget(r)]
    
    print(f"Services tested: {len(results)}")
    print(f"Budget violations: {len(violations)}")
    
    if violations:
        print("\n⚠ Performance Budget Violations:")
        for v in violations:
            print(f"  {v.service}: {v.p95_ms:.1f}ms > 800ms")
        return 1
    else:
        print("✓ All services within performance budget")
        return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)