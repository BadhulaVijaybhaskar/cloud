#!/usr/bin/env python3
"""
Backtest Evaluator - Offline validation using historical telemetry
Phase I.6.2 - Evaluator implementation
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class BacktestEvaluator:
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.eval_window = int(os.getenv("AOL_EVAL_WINDOW_S", "300"))
        
        # Synthetic historical data for simulation
        self.historical_metrics = self._generate_synthetic_history()
    
    def _generate_synthetic_history(self) -> Dict[str, List[Dict]]:
        """Generate synthetic historical metrics for simulation"""
        metrics = {}
        base_time = time.time() - (24 * 3600)  # 24 hours ago
        
        # Generate CPU utilization history
        cpu_data = []
        for i in range(288):  # 5-minute intervals for 24 hours
            timestamp = base_time + (i * 300)  # 5 minutes apart
            # Simulate daily pattern with some noise
            hour = (timestamp % 86400) / 3600
            base_cpu = 0.3 + 0.4 * np.sin((hour - 6) * np.pi / 12)  # Peak at 6 PM
            noise = np.random.normal(0, 0.1)
            cpu_util = max(0.1, min(0.9, base_cpu + noise))
            
            cpu_data.append({
                "timestamp": timestamp,
                "value": cpu_util,
                "metric": "cpu_utilization"
            })
        
        metrics["cpu_utilization"] = cpu_data
        
        # Generate memory utilization history
        memory_data = []
        for i in range(288):
            timestamp = base_time + (i * 300)
            hour = (timestamp % 86400) / 3600
            base_memory = 0.4 + 0.3 * np.sin((hour - 8) * np.pi / 12)
            noise = np.random.normal(0, 0.05)
            memory_util = max(0.2, min(0.85, base_memory + noise))
            
            memory_data.append({
                "timestamp": timestamp,
                "value": memory_util,
                "metric": "memory_utilization"
            })
        
        metrics["memory_utilization"] = memory_data
        
        # Generate latency history
        latency_data = []
        for i in range(288):
            timestamp = base_time + (i * 300)
            hour = (timestamp % 86400) / 3600
            base_latency = 150 + 100 * np.sin((hour - 6) * np.pi / 12)
            noise = np.random.normal(0, 20)
            latency = max(50, min(800, base_latency + noise))
            
            latency_data.append({
                "timestamp": timestamp,
                "value": latency,
                "metric": "latency_p95"
            })
        
        metrics["latency_p95"] = latency_data
        
        return metrics
    
    def evaluate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate optimization proposal using historical data"""
        changes = proposal.get("changes", [])
        scope = proposal.get("scope", "")
        
        if self.simulation_mode:
            return self._simulate_backtest(changes, scope)
        else:
            return self._run_actual_backtest(changes, scope)
    
    def _simulate_backtest(self, changes: List[Dict], scope: str) -> Dict[str, Any]:
        """Simulate backtest evaluation"""
        # Analyze proposed changes
        impact_score = self._calculate_impact_score(changes)
        
        # Simulate performance metrics after applying changes
        baseline_metrics = self._get_baseline_metrics()
        projected_metrics = self._project_metrics_with_changes(baseline_metrics, changes, impact_score)
        
        # Calculate improvement metrics
        improvement = self._calculate_improvement(baseline_metrics, projected_metrics)
        
        # Risk assessment
        risk_assessment = self._assess_risk(changes, improvement)
        
        return {
            "status": "completed",
            "simulation_mode": True,
            "baseline_metrics": baseline_metrics,
            "projected_metrics": projected_metrics,
            "improvement": improvement,
            "risk_assessment": risk_assessment,
            "confidence_score": min(0.95, 0.7 + (impact_score * 0.2)),
            "evaluation_window_seconds": self.eval_window,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _run_actual_backtest(self, changes: List[Dict], scope: str) -> Dict[str, Any]:
        """Run actual backtest against real historical data"""
        # In production: query Prometheus/metrics store for historical data
        prom_url = os.getenv("PROM_URL")
        if not prom_url:
            return self._simulate_backtest(changes, scope)
        
        # Would implement actual Prometheus queries here
        return {
            "status": "completed",
            "simulation_mode": False,
            "note": "Production backtest not implemented - using simulation"
        }
    
    def _calculate_impact_score(self, changes: List[Dict]) -> float:
        """Calculate expected impact score for changes"""
        total_impact = 0.0
        
        for change in changes:
            path = change.get("path", "")
            value = change.get("value", 0)
            
            # Weight different types of changes
            if "cpu" in path.lower():
                if isinstance(value, (int, float)):
                    total_impact += abs(value - 1.0) * 0.3  # CPU changes have moderate impact
            elif "memory" in path.lower():
                total_impact += 0.2  # Memory changes have lower impact
            elif "timeout" in path.lower() or "latency" in path.lower():
                total_impact += 0.4  # Latency changes have higher impact
            elif "replicas" in path.lower() or "scale" in path.lower():
                total_impact += 0.5  # Scaling changes have high impact
        
        return min(1.0, total_impact)
    
    def _get_baseline_metrics(self) -> Dict[str, float]:
        """Get baseline metrics from recent history"""
        baseline = {}
        
        for metric_name, data_points in self.historical_metrics.items():
            # Get last 10 data points for baseline
            recent_points = data_points[-10:]
            values = [point["value"] for point in recent_points]
            
            baseline[metric_name] = {
                "mean": np.mean(values),
                "p95": np.percentile(values, 95),
                "p50": np.percentile(values, 50),
                "std": np.std(values)
            }
        
        return baseline
    
    def _project_metrics_with_changes(self, baseline: Dict, changes: List[Dict], impact_score: float) -> Dict[str, float]:
        """Project how metrics would change with proposed optimizations"""
        projected = {}
        
        for metric_name, baseline_stats in baseline.items():
            base_value = baseline_stats["mean"]
            
            # Apply change effects based on optimization type
            improvement_factor = 1.0
            
            for change in changes:
                path = change.get("path", "")
                
                if metric_name == "cpu_utilization" and "cpu" in path:
                    # CPU limit changes affect CPU utilization
                    new_limit = change.get("value", 1.0)
                    if isinstance(new_limit, (int, float)):
                        improvement_factor *= (1.0 / max(0.5, new_limit))
                
                elif metric_name == "latency_p95" and ("timeout" in path or "router" in path):
                    # Router optimizations reduce latency
                    improvement_factor *= 0.85  # 15% improvement
                
                elif metric_name == "memory_utilization" and "memory" in path:
                    # Memory limit changes affect memory utilization
                    improvement_factor *= 0.9  # 10% improvement
            
            # Apply improvement with some randomness for realism
            noise_factor = 1.0 + np.random.normal(0, 0.05)  # ±5% noise
            projected_value = base_value * improvement_factor * noise_factor
            
            projected[metric_name] = {
                "mean": projected_value,
                "p95": projected_value * 1.2,  # P95 typically higher than mean
                "improvement_factor": improvement_factor
            }
        
        return projected
    
    def _calculate_improvement(self, baseline: Dict, projected: Dict) -> Dict[str, Any]:
        """Calculate improvement metrics"""
        improvements = {}
        
        for metric_name in baseline.keys():
            if metric_name in projected:
                baseline_val = baseline[metric_name]["mean"]
                projected_val = projected[metric_name]["mean"]
                
                # Calculate percentage improvement (negative for metrics where lower is better)
                if metric_name in ["latency_p95", "error_rate"]:
                    # Lower is better
                    improvement_pct = ((baseline_val - projected_val) / baseline_val) * 100
                else:
                    # Higher is better (for utilization, we want it closer to target)
                    improvement_pct = ((projected_val - baseline_val) / baseline_val) * 100
                
                improvements[metric_name] = {
                    "baseline": baseline_val,
                    "projected": projected_val,
                    "improvement_percent": improvement_pct,
                    "significant": abs(improvement_pct) > 5.0  # >5% change is significant
                }
        
        return improvements
    
    def _assess_risk(self, changes: List[Dict], improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk of proposed changes"""
        risk_factors = []
        overall_risk = "low"
        
        # Check for high-impact changes
        for change in changes:
            path = change.get("path", "")
            value = change.get("value")
            
            if "replicas" in path or "scale" in path:
                risk_factors.append("Scaling changes affect availability")
                overall_risk = "medium"
            
            if isinstance(value, (int, float)) and value > 2.0:
                risk_factors.append("Large parameter changes")
                overall_risk = "high"
        
        # Check for negative improvements
        negative_impacts = [
            metric for metric, data in improvement.items()
            if data["improvement_percent"] < -10  # >10% degradation
        ]
        
        if negative_impacts:
            risk_factors.append(f"Potential degradation in: {', '.join(negative_impacts)}")
            overall_risk = "high"
        
        return {
            "level": overall_risk,
            "factors": risk_factors,
            "mitigation": "Use canary deployment with automatic rollback",
            "approval_required": overall_risk in ["medium", "high"]
        }
    
    def get_evaluation_history(self, limit: int = 10) -> List[Dict]:
        """Get recent evaluation history"""
        # In simulation mode, return synthetic history
        if self.simulation_mode:
            return [
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "proposal_id": f"sim_{i}",
                    "status": "completed",
                    "confidence_score": 0.8 + (i * 0.02),
                    "improvement_summary": f"Simulated evaluation {i}"
                }
                for i in range(limit)
            ]
        
        # In production: query actual evaluation history from database
        return []