#!/usr/bin/env python3
"""
Optimization Engine - ML + Rule-based Hybrid Optimizer
Phase I.6.1 - Core optimization logic with EWMA and threshold detection
"""

import os
import json
import time
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

class OptimizationEngine:
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        self.learning_rate = float(os.getenv("AOL_MAX_LEARN_RATE", "0.05"))
        self.eval_window = int(os.getenv("AOL_EVAL_WINDOW_S", "300"))
        
        # EWMA parameters for metric tracking
        self.alpha = 0.3  # EWMA smoothing factor
        self.metrics_history = {}
        
        # Optimization thresholds
        self.thresholds = {
            "cpu_utilization": {"min": 0.2, "max": 0.8, "target": 0.6},
            "memory_utilization": {"min": 0.3, "max": 0.85, "target": 0.7},
            "latency_p95": {"min": 50, "max": 500, "target": 200},
            "throughput": {"min": 100, "max": 10000, "target": 1000},
            "error_rate": {"min": 0.0, "max": 0.05, "target": 0.01}
        }
    
    def update_metrics(self, metric_name: str, value: float, timestamp: float = None):
        """Update EWMA for a metric"""
        if timestamp is None:
            timestamp = time.time()
        
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = {
                "ewma": value,
                "last_update": timestamp,
                "samples": 1
            }
        else:
            history = self.metrics_history[metric_name]
            # Calculate EWMA: new_ewma = alpha * new_value + (1 - alpha) * old_ewma
            history["ewma"] = self.alpha * value + (1 - self.alpha) * history["ewma"]
            history["last_update"] = timestamp
            history["samples"] += 1
    
    def detect_optimization_opportunities(self, telemetry_data: Dict[str, Any]) -> List[Dict]:
        """Detect optimization opportunities using threshold analysis"""
        opportunities = []
        
        for metric_name, current_value in telemetry_data.items():
            if metric_name not in self.thresholds:
                continue
            
            threshold = self.thresholds[metric_name]
            target = threshold["target"]
            
            # Update EWMA
            self.update_metrics(metric_name, current_value)
            ewma_value = self.metrics_history[metric_name]["ewma"]
            
            # Detect if metric is outside optimal range
            deviation = abs(ewma_value - target) / target
            
            if deviation > 0.2:  # 20% deviation threshold
                if ewma_value > threshold["max"]:
                    # Resource overutilization
                    opportunities.append({
                        "metric": metric_name,
                        "current": ewma_value,
                        "target": target,
                        "action": "scale_up" if "utilization" in metric_name else "optimize_down",
                        "confidence": min(0.9, deviation),
                        "urgency": "high" if deviation > 0.5 else "medium"
                    })
                elif ewma_value < threshold["min"]:
                    # Resource underutilization
                    opportunities.append({
                        "metric": metric_name,
                        "current": ewma_value,
                        "target": target,
                        "action": "scale_down" if "utilization" in metric_name else "optimize_up",
                        "confidence": min(0.9, deviation),
                        "urgency": "low"
                    })
        
        return opportunities
    
    def generate_optimization_suggestions(self, opportunities: List[Dict], scope: str) -> List[Dict]:
        """Generate specific parameter change suggestions"""
        suggestions = []
        
        for opp in opportunities:
            metric = opp["metric"]
            action = opp["action"]
            confidence = opp["confidence"]
            
            if metric == "cpu_utilization":
                if action == "scale_up":
                    suggestions.append({
                        "path": "scheduler.cpu_limit",
                        "current_value": 1.0,
                        "suggested_value": min(2.0, 1.0 + self.learning_rate * confidence),
                        "reason": f"CPU utilization {opp['current']:.2f} exceeds target {opp['target']:.2f}",
                        "confidence": confidence
                    })
                elif action == "scale_down":
                    suggestions.append({
                        "path": "scheduler.cpu_limit",
                        "current_value": 1.0,
                        "suggested_value": max(0.5, 1.0 - self.learning_rate * confidence),
                        "reason": f"CPU utilization {opp['current']:.2f} below target {opp['target']:.2f}",
                        "confidence": confidence
                    })
            
            elif metric == "memory_utilization":
                if action == "scale_up":
                    suggestions.append({
                        "path": "scheduler.memory_limit",
                        "current_value": "2Gi",
                        "suggested_value": "3Gi",
                        "reason": f"Memory utilization {opp['current']:.2f} exceeds target {opp['target']:.2f}",
                        "confidence": confidence
                    })
            
            elif metric == "latency_p95":
                if opp["current"] > opp["target"]:
                    suggestions.append({
                        "path": "router.timeout_ms",
                        "current_value": 5000,
                        "suggested_value": max(1000, int(5000 * (1 - self.learning_rate * confidence))),
                        "reason": f"P95 latency {opp['current']:.0f}ms exceeds target {opp['target']:.0f}ms",
                        "confidence": confidence
                    })
        
        return suggestions
    
    def apply_changes(self, changes: List[Dict], scope: str) -> Dict[str, Any]:
        """Apply optimization changes"""
        if self.simulation_mode:
            return {
                "status": "simulated",
                "changes_applied": len(changes),
                "scope": scope,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "simulation_note": "Changes simulated - no actual infrastructure modified"
            }
        
        # In production mode, would integrate with actual infrastructure APIs
        applied_changes = []
        for change in changes:
            try:
                # Simulate API calls to infrastructure services
                result = self._apply_single_change(change, scope)
                applied_changes.append({
                    "path": change.get("path"),
                    "value": change.get("value"),
                    "status": "applied",
                    "result": result
                })
            except Exception as e:
                applied_changes.append({
                    "path": change.get("path"),
                    "value": change.get("value"),
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "changes_applied": len([c for c in applied_changes if c["status"] == "applied"]),
            "changes_failed": len([c for c in applied_changes if c["status"] == "failed"]),
            "details": applied_changes,
            "scope": scope,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    def _apply_single_change(self, change: Dict, scope: str) -> Dict:
        """Apply a single optimization change"""
        path = change.get("path", "")
        value = change.get("value")
        
        # Route to appropriate service based on path
        if path.startswith("scheduler."):
            return self._apply_scheduler_change(path, value, scope)
        elif path.startswith("router."):
            return self._apply_router_change(path, value, scope)
        elif path.startswith("neural."):
            return self._apply_neural_change(path, value, scope)
        else:
            raise ValueError(f"Unknown optimization path: {path}")
    
    def _apply_scheduler_change(self, path: str, value: Any, scope: str) -> Dict:
        """Apply scheduler-related changes"""
        # In production: call Neural Fabric Scheduler API
        neural_fabric_url = os.getenv("NEURAL_FABRIC_URL")
        if neural_fabric_url and not self.simulation_mode:
            # Would make actual API call here
            pass
        
        return {
            "service": "neural-fabric-scheduler",
            "path": path,
            "value": value,
            "scope": scope,
            "applied_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def _apply_router_change(self, path: str, value: Any, scope: str) -> Dict:
        """Apply router-related changes"""
        # In production: call Global Router API
        router_url = os.getenv("GLOBAL_ROUTER_URL")
        if router_url and not self.simulation_mode:
            # Would make actual API call here
            pass
        
        return {
            "service": "global-router",
            "path": path,
            "value": value,
            "scope": scope,
            "applied_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def _apply_neural_change(self, path: str, value: Any, scope: str) -> Dict:
        """Apply neural network related changes"""
        return {
            "service": "neural-fabric",
            "path": path,
            "value": value,
            "scope": scope,
            "applied_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization engine status"""
        return {
            "simulation_mode": self.simulation_mode,
            "learning_rate": self.learning_rate,
            "eval_window_seconds": self.eval_window,
            "tracked_metrics": len(self.metrics_history),
            "metrics_summary": {
                name: {
                    "ewma": data["ewma"],
                    "samples": data["samples"],
                    "last_update": data["last_update"]
                }
                for name, data in self.metrics_history.items()
            }
        }