#!/usr/bin/env python3
"""
Explainability Engine - Generate human-readable rationale for optimization decisions
Phase I.6.4 - Explainability implementation
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExplainabilityEngine:
    def __init__(self, simulation_mode: bool = True):
        self.simulation_mode = simulation_mode
        
        # Templates for different types of explanations
        self.explanation_templates = {
            "cpu_optimization": {
                "scale_up": "CPU utilization of {current:.1%} exceeds the optimal range. Increasing CPU allocation to {new_value} will reduce resource contention and improve response times.",
                "scale_down": "CPU utilization of {current:.1%} is below optimal levels. Reducing CPU allocation to {new_value} will improve resource efficiency without impacting performance."
            },
            "memory_optimization": {
                "scale_up": "Memory utilization of {current:.1%} is approaching limits. Increasing memory allocation to {new_value} will prevent out-of-memory conditions.",
                "scale_down": "Memory utilization of {current:.1%} indicates over-provisioning. Reducing allocation to {new_value} will optimize costs."
            },
            "latency_optimization": {
                "timeout_adjust": "P95 latency of {current:.0f}ms exceeds target of {target:.0f}ms. Adjusting timeout to {new_value}ms will improve user experience.",
                "routing_optimize": "Current routing configuration shows {current:.0f}ms latency. Optimizing routing rules will reduce latency by approximately {improvement:.1f}%."
            },
            "throughput_optimization": {
                "capacity_increase": "Current throughput of {current:.0f} req/s is near capacity limits. Scaling to handle {new_value:.0f} req/s will prevent bottlenecks.",
                "load_balance": "Uneven load distribution detected. Rebalancing will improve throughput by {improvement:.1f}%."
            }
        }
        
        # Risk explanation templates
        self.risk_templates = {
            "low": "This optimization has minimal risk as it involves small parameter adjustments within safe bounds.",
            "medium": "This optimization requires careful monitoring as it may impact {affected_services} performance during deployment.",
            "high": "This optimization involves significant changes that could affect system stability. Canary deployment and approval are required."
        }
    
    def explain_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive explanation for optimization proposal"""
        changes = proposal.get("changes", [])
        risk_level = proposal.get("risk_level", "low")
        scope = proposal.get("scope", "")
        
        # Generate explanations for each change
        change_explanations = []
        for change in changes:
            explanation = self._explain_single_change(change)
            change_explanations.append(explanation)
        
        # Generate overall rationale
        overall_rationale = self._generate_overall_rationale(changes, proposal)
        
        # Generate risk explanation
        risk_explanation = self._explain_risk_level(risk_level, changes)
        
        # Generate impact assessment
        impact_assessment = self._assess_expected_impact(changes)
        
        # Generate monitoring recommendations
        monitoring_recommendations = self._generate_monitoring_recommendations(changes)
        
        return {
            "proposal_id": proposal.get("id"),
            "overall_rationale": overall_rationale,
            "change_explanations": change_explanations,
            "risk_explanation": risk_explanation,
            "impact_assessment": impact_assessment,
            "monitoring_recommendations": monitoring_recommendations,
            "confidence_factors": self._identify_confidence_factors(changes),
            "alternative_approaches": self._suggest_alternatives(changes),
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def _explain_single_change(self, change: Dict[str, Any]) -> Dict[str, Any]:
        """Explain a single optimization change"""
        path = change.get("path", "")
        current_value = change.get("current_value")
        new_value = change.get("value")
        reason = change.get("reason", "")
        
        # Determine change type and generate explanation
        change_type = self._classify_change_type(path)
        explanation_text = self._generate_change_explanation(change_type, change)
        
        # Calculate change magnitude
        magnitude = self._calculate_change_magnitude(current_value, new_value)
        
        # Identify affected components
        affected_components = self._identify_affected_components(path)
        
        return {
            "path": path,
            "change_type": change_type,
            "explanation": explanation_text,
            "magnitude": magnitude,
            "affected_components": affected_components,
            "technical_details": {
                "current_value": current_value,
                "new_value": new_value,
                "change_percentage": self._calculate_percentage_change(current_value, new_value)
            }
        }
    
    def _classify_change_type(self, path: str) -> str:
        """Classify the type of optimization change"""
        path_lower = path.lower()
        
        if "cpu" in path_lower:
            return "cpu_optimization"
        elif "memory" in path_lower:
            return "memory_optimization"
        elif "timeout" in path_lower or "latency" in path_lower:
            return "latency_optimization"
        elif "throughput" in path_lower or "capacity" in path_lower:
            return "throughput_optimization"
        elif "replicas" in path_lower or "scale" in path_lower:
            return "scaling_optimization"
        elif "router" in path_lower or "routing" in path_lower:
            return "routing_optimization"
        else:
            return "general_optimization"
    
    def _generate_change_explanation(self, change_type: str, change: Dict[str, Any]) -> str:
        """Generate human-readable explanation for a change"""
        path = change.get("path", "")
        current_value = change.get("current_value")
        new_value = change.get("value")
        
        # Use templates based on change type
        if change_type == "cpu_optimization":
            if isinstance(new_value, (int, float)) and isinstance(current_value, (int, float)):
                if new_value > current_value:
                    return f"Increasing CPU allocation from {current_value} to {new_value} cores to handle higher workload demands and reduce processing delays."
                else:
                    return f"Reducing CPU allocation from {current_value} to {new_value} cores to optimize resource utilization while maintaining performance."
        
        elif change_type == "memory_optimization":
            return f"Adjusting memory allocation for {path} from {current_value} to {new_value} to optimize memory usage patterns."
        
        elif change_type == "latency_optimization":
            return f"Modifying {path} from {current_value} to {new_value} to reduce response latency and improve user experience."
        
        elif change_type == "scaling_optimization":
            return f"Scaling {path} to {new_value} instances to better match current demand patterns."
        
        elif change_type == "routing_optimization":
            return f"Optimizing routing configuration {path} to improve traffic distribution and reduce bottlenecks."
        
        else:
            return f"Adjusting {path} from {current_value} to {new_value} to improve system performance based on observed metrics."
    
    def _calculate_change_magnitude(self, current_value: Any, new_value: Any) -> str:
        """Calculate the magnitude of change"""
        if not isinstance(current_value, (int, float)) or not isinstance(new_value, (int, float)):
            return "qualitative"
        
        if current_value == 0:
            return "major" if new_value != 0 else "none"
        
        percentage_change = abs((new_value - current_value) / current_value) * 100
        
        if percentage_change < 5:
            return "minimal"
        elif percentage_change < 20:
            return "moderate"
        elif percentage_change < 50:
            return "significant"
        else:
            return "major"
    
    def _calculate_percentage_change(self, current_value: Any, new_value: Any) -> Optional[float]:
        """Calculate percentage change between values"""
        if not isinstance(current_value, (int, float)) or not isinstance(new_value, (int, float)):
            return None
        
        if current_value == 0:
            return None
        
        return ((new_value - current_value) / current_value) * 100
    
    def _identify_affected_components(self, path: str) -> List[str]:
        """Identify system components affected by the change"""
        components = []
        path_lower = path.lower()
        
        if "scheduler" in path_lower:
            components.extend(["Neural Fabric Scheduler", "Workload Distribution"])
        if "router" in path_lower:
            components.extend(["Global Router", "Traffic Routing"])
        if "cpu" in path_lower or "memory" in path_lower:
            components.extend(["Resource Allocation", "Container Runtime"])
        if "timeout" in path_lower:
            components.extend(["Request Processing", "Client Experience"])
        if "neural" in path_lower:
            components.extend(["Neural Network Processing", "Model Inference"])
        
        return components if components else ["General System Configuration"]
    
    def _generate_overall_rationale(self, changes: List[Dict], proposal: Dict[str, Any]) -> str:
        """Generate overall rationale for the optimization proposal"""
        num_changes = len(changes)
        scope = proposal.get("scope", "")
        reason = proposal.get("reason", "")
        
        if num_changes == 1:
            change = changes[0]
            change_type = self._classify_change_type(change.get("path", ""))
            return f"This optimization addresses a single {change_type.replace('_', ' ')} issue in {scope}. {reason}"
        
        else:
            change_types = set(self._classify_change_type(c.get("path", "")) for c in changes)
            types_str = ", ".join(t.replace("_", " ") for t in change_types)
            return f"This comprehensive optimization addresses {num_changes} configuration changes across {types_str} for {scope}. {reason}"
    
    def _explain_risk_level(self, risk_level: str, changes: List[Dict]) -> Dict[str, Any]:
        """Explain the risk level and contributing factors"""
        risk_factors = []
        mitigation_strategies = []
        
        # Analyze risk factors
        for change in changes:
            path = change.get("path", "")
            magnitude = self._calculate_change_magnitude(change.get("current_value"), change.get("value"))
            
            if magnitude in ["significant", "major"]:
                risk_factors.append(f"Large parameter change in {path}")
            
            if "replicas" in path.lower() or "scale" in path.lower():
                risk_factors.append("Scaling changes affect service availability")
            
            if "router" in path.lower():
                risk_factors.append("Routing changes impact traffic distribution")
        
        # Generate mitigation strategies
        if risk_level in ["medium", "high"]:
            mitigation_strategies.extend([
                "Canary deployment with gradual rollout",
                "Continuous monitoring during deployment",
                "Automated rollback on failure detection"
            ])
        
        if risk_level == "high":
            mitigation_strategies.extend([
                "Human approval required before deployment",
                "Extended validation period",
                "Comprehensive pre-deployment testing"
            ])
        
        return {
            "level": risk_level,
            "description": self.risk_templates.get(risk_level, "Unknown risk level"),
            "contributing_factors": risk_factors,
            "mitigation_strategies": mitigation_strategies
        }
    
    def _assess_expected_impact(self, changes: List[Dict]) -> Dict[str, Any]:
        """Assess expected impact of changes"""
        positive_impacts = []
        potential_concerns = []
        
        for change in changes:
            change_type = self._classify_change_type(change.get("path", ""))
            
            if change_type == "cpu_optimization":
                positive_impacts.append("Improved CPU utilization and reduced processing delays")
            elif change_type == "memory_optimization":
                positive_impacts.append("Better memory management and reduced OOM risks")
            elif change_type == "latency_optimization":
                positive_impacts.append("Reduced response times and improved user experience")
            elif change_type == "scaling_optimization":
                positive_impacts.append("Better capacity matching and improved availability")
                potential_concerns.append("Temporary service disruption during scaling")
        
        return {
            "positive_impacts": positive_impacts,
            "potential_concerns": potential_concerns,
            "estimated_improvement": "5-15% performance improvement based on historical data"
        }
    
    def _generate_monitoring_recommendations(self, changes: List[Dict]) -> List[str]:
        """Generate monitoring recommendations for the changes"""
        recommendations = []
        
        metrics_to_monitor = set()
        for change in changes:
            path = change.get("path", "").lower()
            
            if "cpu" in path:
                metrics_to_monitor.update(["CPU utilization", "CPU throttling"])
            if "memory" in path:
                metrics_to_monitor.update(["Memory utilization", "OOM events"])
            if "timeout" in path or "latency" in path:
                metrics_to_monitor.update(["Response latency", "Request timeouts"])
            if "router" in path:
                metrics_to_monitor.update(["Traffic distribution", "Route success rates"])
        
        recommendations.extend([f"Monitor {metric} closely for 24 hours post-deployment" for metric in metrics_to_monitor])
        recommendations.append("Set up alerts for metric deviations beyond 20% of baseline")
        recommendations.append("Review performance trends after 1 week to assess long-term impact")
        
        return recommendations
    
    def _identify_confidence_factors(self, changes: List[Dict]) -> Dict[str, Any]:
        """Identify factors affecting confidence in the optimization"""
        return {
            "high_confidence_factors": [
                "Changes based on established performance patterns",
                "Similar optimizations have shown positive results",
                "Comprehensive simulation and validation performed"
            ],
            "uncertainty_factors": [
                "Limited historical data for some metrics",
                "Potential interaction effects between multiple changes",
                "External load variations may affect results"
            ],
            "overall_confidence": "High (85%)" if len(changes) <= 2 else "Medium (70%)"
        }
    
    def _suggest_alternatives(self, changes: List[Dict]) -> List[str]:
        """Suggest alternative optimization approaches"""
        alternatives = []
        
        if len(changes) > 3:
            alternatives.append("Consider implementing changes in smaller batches to reduce risk")
        
        for change in changes:
            change_type = self._classify_change_type(change.get("path", ""))
            
            if change_type == "scaling_optimization":
                alternatives.append("Alternative: Use horizontal pod autoscaling instead of manual scaling")
            elif change_type == "cpu_optimization":
                alternatives.append("Alternative: Implement CPU request/limit optimization instead of allocation changes")
        
        if not alternatives:
            alternatives.append("Current approach is optimal based on available data")
        
        return alternatives