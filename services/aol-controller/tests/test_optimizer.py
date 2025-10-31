#!/usr/bin/env python3
"""
Unit tests for Optimization Engine
"""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from optimizer import OptimizationEngine

def test_optimizer_initialization():
    """Test optimizer initialization"""
    optimizer = OptimizationEngine(simulation_mode=True)
    assert optimizer.simulation_mode == True
    assert optimizer.learning_rate == 0.05
    assert optimizer.eval_window == 300

def test_update_metrics():
    """Test EWMA metric updates"""
    optimizer = OptimizationEngine(simulation_mode=True)
    
    # Update metric multiple times
    optimizer.update_metrics("cpu_utilization", 0.5)
    optimizer.update_metrics("cpu_utilization", 0.7)
    optimizer.update_metrics("cpu_utilization", 0.6)
    
    # Check EWMA calculation
    history = optimizer.metrics_history["cpu_utilization"]
    assert "ewma" in history
    assert history["samples"] == 3
    assert 0.5 <= history["ewma"] <= 0.7

def test_detect_optimization_opportunities():
    """Test optimization opportunity detection"""
    optimizer = OptimizationEngine(simulation_mode=True)
    
    # Test high CPU utilization
    telemetry = {
        "cpu_utilization": 0.9,  # Above threshold
        "memory_utilization": 0.5,  # Normal
        "latency_p95": 600  # Above threshold
    }
    
    opportunities = optimizer.detect_optimization_opportunities(telemetry)
    assert len(opportunities) >= 2  # CPU and latency issues
    
    # Check CPU opportunity
    cpu_opp = next((o for o in opportunities if o["metric"] == "cpu_utilization"), None)
    assert cpu_opp is not None
    assert cpu_opp["action"] == "scale_up"

def test_generate_optimization_suggestions():
    """Test optimization suggestion generation"""
    optimizer = OptimizationEngine(simulation_mode=True)
    
    opportunities = [
        {
            "metric": "cpu_utilization",
            "current": 0.9,
            "target": 0.6,
            "action": "scale_up",
            "confidence": 0.8,
            "urgency": "high"
        }
    ]
    
    suggestions = optimizer.generate_optimization_suggestions(opportunities, "tenant:test")
    assert len(suggestions) > 0
    
    cpu_suggestion = suggestions[0]
    assert cpu_suggestion["path"] == "scheduler.cpu_limit"
    assert cpu_suggestion["suggested_value"] > cpu_suggestion["current_value"]

def test_apply_changes_simulation():
    """Test applying changes in simulation mode"""
    optimizer = OptimizationEngine(simulation_mode=True)
    
    changes = [
        {
            "path": "scheduler.cpu_limit",
            "value": 1.5,
            "current_value": 1.0
        }
    ]
    
    result = optimizer.apply_changes(changes, "tenant:test")
    assert result["status"] == "simulated"
    assert result["changes_applied"] == 1
    assert "simulation_note" in result

def test_get_optimization_status():
    """Test optimization status retrieval"""
    optimizer = OptimizationEngine(simulation_mode=True)
    
    # Add some metrics
    optimizer.update_metrics("cpu_utilization", 0.6)
    optimizer.update_metrics("memory_utilization", 0.7)
    
    status = optimizer.get_optimization_status()
    assert status["simulation_mode"] == True
    assert status["tracked_metrics"] == 2
    assert "metrics_summary" in status

if __name__ == "__main__":
    pytest.main([__file__])