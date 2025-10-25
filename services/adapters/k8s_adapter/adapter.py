import asyncio
import subprocess
import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile
import os

logger = logging.getLogger(__name__)

class KubernetesAdapter:
    """
    Kubernetes adapter for executing k8s operations
    Supports: apply, scale, restart, run job, rollback operations
    """
    
    def __init__(self, kubeconfig_path: Optional[str] = None, namespace: str = "default"):
        self.kubeconfig_path = kubeconfig_path or os.getenv("KUBECONFIG")
        self.namespace = namespace
        self.kubectl_cmd = "kubectl"
        
        if self.kubeconfig_path:
            self.kubectl_cmd += f" --kubeconfig={self.kubeconfig_path}"
    
    async def execute_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute kubectl command asynchronously"""
        try:
            logger.info(f"Executing: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return {
                "returncode": process.returncode,
                "stdout": stdout.decode() if stdout else "",
                "stderr": stderr.decode() if stderr else "",
                "success": process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {command}")
            return {
                "returncode": 124,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "success": False
            }
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            return {
                "returncode": 1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
    
    async def apply_manifest(self, manifest: Dict[str, Any], namespace: Optional[str] = None) -> Dict[str, Any]:
        """Apply Kubernetes manifest"""
        ns = namespace or self.namespace
        
        try:
            # Create temporary file for manifest
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                yaml.dump(manifest, f, default_flow_style=False)
                manifest_path = f.name
            
            # Apply manifest
            cmd = f"{self.kubectl_cmd} apply -f {manifest_path} -n {ns}"
            result = await self.execute_command(cmd)
            
            # Cleanup
            os.unlink(manifest_path)
            
            if result["success"]:
                return {
                    "status": "success",
                    "action": "apply_manifest",
                    "message": "Manifest applied successfully",
                    "output": result["stdout"],
                    "resource": manifest.get("metadata", {}).get("name", "unknown")
                }
            else:
                return {
                    "status": "error",
                    "action": "apply_manifest",
                    "message": f"Failed to apply manifest: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Apply manifest failed: {str(e)}")
            return {
                "status": "error",
                "action": "apply_manifest",
                "message": str(e)
            }
    
    async def scale_deployment(self, deployment_name: str, replicas: int, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Scale deployment to specified replica count"""
        ns = namespace or self.namespace
        
        try:
            cmd = f"{self.kubectl_cmd} scale deployment {deployment_name} --replicas={replicas} -n {ns}"
            result = await self.execute_command(cmd)
            
            if result["success"]:
                # Wait for scaling to complete
                await self.wait_for_deployment_ready(deployment_name, namespace=ns, timeout=300)
                
                return {
                    "status": "success",
                    "action": "scale_deployment",
                    "message": f"Deployment {deployment_name} scaled to {replicas} replicas",
                    "deployment": deployment_name,
                    "replicas": replicas,
                    "namespace": ns
                }
            else:
                return {
                    "status": "error",
                    "action": "scale_deployment",
                    "message": f"Failed to scale deployment: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Scale deployment failed: {str(e)}")
            return {
                "status": "error",
                "action": "scale_deployment",
                "message": str(e)
            }
    
    async def restart_pod(self, pod_name: Optional[str] = None, deployment_name: Optional[str] = None, 
                         namespace: Optional[str] = None) -> Dict[str, Any]:
        """Restart pod or deployment"""
        ns = namespace or self.namespace
        
        try:
            if deployment_name:
                # Rolling restart of deployment
                cmd = f"{self.kubectl_cmd} rollout restart deployment/{deployment_name} -n {ns}"
                result = await self.execute_command(cmd)
                
                if result["success"]:
                    # Wait for rollout to complete
                    await self.wait_for_rollout_complete(deployment_name, namespace=ns)
                    
                    return {
                        "status": "success",
                        "action": "restart_deployment",
                        "message": f"Deployment {deployment_name} restarted successfully",
                        "deployment": deployment_name,
                        "namespace": ns
                    }
                else:
                    return {
                        "status": "error",
                        "action": "restart_deployment",
                        "message": f"Failed to restart deployment: {result['stderr']}",
                        "error": result["stderr"]
                    }
            
            elif pod_name:
                # Delete pod (will be recreated by controller)
                cmd = f"{self.kubectl_cmd} delete pod {pod_name} -n {ns}"
                result = await self.execute_command(cmd)
                
                if result["success"]:
                    return {
                        "status": "success",
                        "action": "restart_pod",
                        "message": f"Pod {pod_name} deleted and will be recreated",
                        "pod": pod_name,
                        "namespace": ns
                    }
                else:
                    return {
                        "status": "error",
                        "action": "restart_pod",
                        "message": f"Failed to delete pod: {result['stderr']}",
                        "error": result["stderr"]
                    }
            
            else:
                return {
                    "status": "error",
                    "action": "restart_pod",
                    "message": "Either pod_name or deployment_name must be specified"
                }
                
        except Exception as e:
            logger.error(f"Restart operation failed: {str(e)}")
            return {
                "status": "error",
                "action": "restart_pod",
                "message": str(e)
            }
    
    async def run_job(self, job_manifest: Dict[str, Any], namespace: Optional[str] = None, 
                     wait_for_completion: bool = True) -> Dict[str, Any]:
        """Run Kubernetes job"""
        ns = namespace or self.namespace
        
        try:
            # Apply job manifest
            apply_result = await self.apply_manifest(job_manifest, namespace=ns)
            
            if apply_result["status"] != "success":
                return apply_result
            
            job_name = job_manifest.get("metadata", {}).get("name", "unknown")
            
            if wait_for_completion:
                # Wait for job completion
                completion_result = await self.wait_for_job_completion(job_name, namespace=ns)
                
                if completion_result["status"] == "success":
                    # Get job logs
                    logs_result = await self.get_job_logs(job_name, namespace=ns)
                    
                    return {
                        "status": "success",
                        "action": "run_job",
                        "message": f"Job {job_name} completed successfully",
                        "job": job_name,
                        "namespace": ns,
                        "logs": logs_result.get("logs", "")
                    }
                else:
                    return completion_result
            else:
                return {
                    "status": "success",
                    "action": "run_job",
                    "message": f"Job {job_name} started",
                    "job": job_name,
                    "namespace": ns
                }
                
        except Exception as e:
            logger.error(f"Run job failed: {str(e)}")
            return {
                "status": "error",
                "action": "run_job",
                "message": str(e)
            }
    
    async def rollback_deployment(self, deployment_name: str, revision: Optional[str] = None, 
                                 namespace: Optional[str] = None) -> Dict[str, Any]:
        """Rollback deployment to previous or specific revision"""
        ns = namespace or self.namespace
        
        try:
            if revision:
                cmd = f"{self.kubectl_cmd} rollout undo deployment/{deployment_name} --to-revision={revision} -n {ns}"
            else:
                cmd = f"{self.kubectl_cmd} rollout undo deployment/{deployment_name} -n {ns}"
            
            result = await self.execute_command(cmd)
            
            if result["success"]:
                # Wait for rollback to complete
                await self.wait_for_rollout_complete(deployment_name, namespace=ns)
                
                return {
                    "status": "success",
                    "action": "rollback_deployment",
                    "message": f"Deployment {deployment_name} rolled back successfully",
                    "deployment": deployment_name,
                    "revision": revision or "previous",
                    "namespace": ns
                }
            else:
                return {
                    "status": "error",
                    "action": "rollback_deployment",
                    "message": f"Failed to rollback deployment: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Rollback deployment failed: {str(e)}")
            return {
                "status": "error",
                "action": "rollback_deployment",
                "message": str(e)
            }
    
    async def wait_for_deployment_ready(self, deployment_name: str, namespace: Optional[str] = None, 
                                      timeout: int = 300) -> Dict[str, Any]:
        """Wait for deployment to be ready"""
        ns = namespace or self.namespace
        
        try:
            cmd = f"{self.kubectl_cmd} wait --for=condition=available --timeout={timeout}s deployment/{deployment_name} -n {ns}"
            result = await self.execute_command(cmd, timeout=timeout + 10)
            
            if result["success"]:
                return {
                    "status": "success",
                    "action": "wait_for_deployment_ready",
                    "message": f"Deployment {deployment_name} is ready",
                    "deployment": deployment_name,
                    "namespace": ns
                }
            else:
                return {
                    "status": "error",
                    "action": "wait_for_deployment_ready",
                    "message": f"Deployment not ready within timeout: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Wait for deployment ready failed: {str(e)}")
            return {
                "status": "error",
                "action": "wait_for_deployment_ready",
                "message": str(e)
            }
    
    async def wait_for_rollout_complete(self, deployment_name: str, namespace: Optional[str] = None, 
                                      timeout: int = 300) -> Dict[str, Any]:
        """Wait for rollout to complete"""
        ns = namespace or self.namespace
        
        try:
            cmd = f"{self.kubectl_cmd} rollout status deployment/{deployment_name} --timeout={timeout}s -n {ns}"
            result = await self.execute_command(cmd, timeout=timeout + 10)
            
            if result["success"]:
                return {
                    "status": "success",
                    "action": "wait_for_rollout_complete",
                    "message": f"Rollout of {deployment_name} completed",
                    "deployment": deployment_name,
                    "namespace": ns
                }
            else:
                return {
                    "status": "error",
                    "action": "wait_for_rollout_complete",
                    "message": f"Rollout did not complete within timeout: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Wait for rollout complete failed: {str(e)}")
            return {
                "status": "error",
                "action": "wait_for_rollout_complete",
                "message": str(e)
            }
    
    async def wait_for_job_completion(self, job_name: str, namespace: Optional[str] = None, 
                                    timeout: int = 600) -> Dict[str, Any]:
        """Wait for job to complete"""
        ns = namespace or self.namespace
        
        try:
            cmd = f"{self.kubectl_cmd} wait --for=condition=complete --timeout={timeout}s job/{job_name} -n {ns}"
            result = await self.execute_command(cmd, timeout=timeout + 10)
            
            if result["success"]:
                return {
                    "status": "success",
                    "action": "wait_for_job_completion",
                    "message": f"Job {job_name} completed successfully",
                    "job": job_name,
                    "namespace": ns
                }
            else:
                # Check if job failed
                failed_cmd = f"{self.kubectl_cmd} wait --for=condition=failed --timeout=5s job/{job_name} -n {ns}"
                failed_result = await self.execute_command(failed_cmd, timeout=10)
                
                if failed_result["success"]:
                    return {
                        "status": "error",
                        "action": "wait_for_job_completion",
                        "message": f"Job {job_name} failed",
                        "job": job_name,
                        "namespace": ns
                    }
                else:
                    return {
                        "status": "error",
                        "action": "wait_for_job_completion",
                        "message": f"Job did not complete within timeout: {result['stderr']}",
                        "error": result["stderr"]
                    }
                
        except Exception as e:
            logger.error(f"Wait for job completion failed: {str(e)}")
            return {
                "status": "error",
                "action": "wait_for_job_completion",
                "message": str(e)
            }
    
    async def get_job_logs(self, job_name: str, namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get logs from job pods"""
        ns = namespace or self.namespace
        
        try:
            # Get pods for the job
            cmd = f"{self.kubectl_cmd} get pods -l job-name={job_name} -n {ns} -o jsonpath='{{.items[*].metadata.name}}'"
            result = await self.execute_command(cmd)
            
            if not result["success"] or not result["stdout"].strip():
                return {
                    "status": "error",
                    "action": "get_job_logs",
                    "message": "No pods found for job",
                    "logs": ""
                }
            
            pod_names = result["stdout"].strip().split()
            all_logs = []
            
            for pod_name in pod_names:
                log_cmd = f"{self.kubectl_cmd} logs {pod_name} -n {ns}"
                log_result = await self.execute_command(log_cmd)
                
                if log_result["success"]:
                    all_logs.append(f"=== Pod {pod_name} ===\n{log_result['stdout']}")
            
            return {
                "status": "success",
                "action": "get_job_logs",
                "message": f"Retrieved logs for job {job_name}",
                "logs": "\n\n".join(all_logs)
            }
            
        except Exception as e:
            logger.error(f"Get job logs failed: {str(e)}")
            return {
                "status": "error",
                "action": "get_job_logs",
                "message": str(e),
                "logs": ""
            }
    
    async def get_resource_status(self, resource_type: str, resource_name: str, 
                                namespace: Optional[str] = None) -> Dict[str, Any]:
        """Get status of a Kubernetes resource"""
        ns = namespace or self.namespace
        
        try:
            cmd = f"{self.kubectl_cmd} get {resource_type} {resource_name} -n {ns} -o json"
            result = await self.execute_command(cmd)
            
            if result["success"]:
                resource_data = json.loads(result["stdout"])
                return {
                    "status": "success",
                    "action": "get_resource_status",
                    "message": f"Retrieved status for {resource_type}/{resource_name}",
                    "resource_data": resource_data
                }
            else:
                return {
                    "status": "error",
                    "action": "get_resource_status",
                    "message": f"Failed to get resource status: {result['stderr']}",
                    "error": result["stderr"]
                }
                
        except Exception as e:
            logger.error(f"Get resource status failed: {str(e)}")
            return {
                "status": "error",
                "action": "get_resource_status",
                "message": str(e)
            }

# Factory function for creating adapter instances
def create_k8s_adapter(kubeconfig_path: Optional[str] = None, namespace: str = "default") -> KubernetesAdapter:
    """Create a new Kubernetes adapter instance"""
    return KubernetesAdapter(kubeconfig_path=kubeconfig_path, namespace=namespace)