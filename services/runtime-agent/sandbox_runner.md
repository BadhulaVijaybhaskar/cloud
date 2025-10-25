# Sandbox Runner for WPK Dry-Run Execution

## Overview

The Sandbox Runner provides isolated execution environments for testing WPK workflows without affecting production systems. It supports both static validation and dynamic dry-run execution in secure, ephemeral environments.

## Architecture

### Sandbox Types

#### 1. Kind Cluster Sandbox
- **Purpose**: Full Kubernetes environment simulation
- **Isolation**: Separate kind cluster per dry-run
- **Cleanup**: Automatic cluster deletion after execution
- **Use Case**: Complex workflows with Kubernetes resources

#### 2. Container Sandbox
- **Purpose**: Isolated container execution
- **Isolation**: Docker containers with restricted capabilities
- **Cleanup**: Container removal after execution
- **Use Case**: Simple containerized workflows

#### 3. VM Sandbox (Future)
- **Purpose**: Full OS-level isolation
- **Isolation**: Ephemeral virtual machines
- **Cleanup**: VM destruction after execution
- **Use Case**: System-level operations

## Implementation

### Kind Cluster Sandbox

```bash
#!/bin/bash
# Create ephemeral kind cluster for dry-run

CLUSTER_NAME="atom-dryrun-$(date +%s)"
KUBECONFIG_PATH="/tmp/kubeconfig-${CLUSTER_NAME}"

# Create kind cluster
kind create cluster --name "${CLUSTER_NAME}" --kubeconfig "${KUBECONFIG_PATH}"

# Set resource limits
kubectl --kubeconfig="${KUBECONFIG_PATH}" create namespace atom-sandbox
kubectl --kubeconfig="${KUBECONFIG_PATH}" apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: sandbox-quota
  namespace: atom-sandbox
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "10"
EOF

# Execute workflow in sandbox
export KUBECONFIG="${KUBECONFIG_PATH}"
# ... run workflow steps ...

# Cleanup
kind delete cluster --name "${CLUSTER_NAME}"
rm -f "${KUBECONFIG_PATH}"
```

### Container Sandbox

```bash
#!/bin/bash
# Create container sandbox for dry-run

SANDBOX_NAME="atom-sandbox-$(date +%s)"
NETWORK_NAME="atom-sandbox-net"

# Create isolated network
docker network create --driver bridge "${NETWORK_NAME}"

# Run sandbox container with restrictions
docker run -d \
  --name "${SANDBOX_NAME}" \
  --network "${NETWORK_NAME}" \
  --security-opt no-new-privileges \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --memory=1g \
  --cpus=1 \
  --pids-limit=100 \
  ubuntu:20.04 sleep 3600

# Execute commands in sandbox
docker exec "${SANDBOX_NAME}" /bin/bash -c "echo 'Dry-run execution'"

# Cleanup
docker stop "${SANDBOX_NAME}"
docker rm "${SANDBOX_NAME}"
docker network rm "${NETWORK_NAME}"
```

## Security Measures

### Network Isolation
- **No External Access**: Sandbox environments cannot reach external networks
- **Internal DNS**: Custom DNS resolution for internal services only
- **Firewall Rules**: Strict ingress/egress filtering

### Resource Limits
- **CPU**: Maximum 2 cores per sandbox
- **Memory**: Maximum 4GB RAM per sandbox
- **Storage**: Maximum 10GB ephemeral storage
- **Time**: Maximum 30 minutes execution time

### Capability Restrictions
- **No Privileged Access**: All containers run as non-root
- **Dropped Capabilities**: Remove dangerous Linux capabilities
- **Read-Only Filesystem**: Prevent persistent changes
- **Process Limits**: Restrict number of processes

## Dry-Run Execution Flow

### 1. Pre-Execution Validation
```python
def validate_for_sandbox(wpk_data):
    """Validate WPK is safe for sandbox execution."""
    
    # Check for dangerous operations
    dangerous_patterns = [
        "rm -rf /",
        "dd if=/dev/zero",
        ":(){ :|:& };:",  # Fork bomb
        "curl.*evil.com"
    ]
    
    # Scan all commands
    for handler in wpk_data.get("spec", {}).get("handlers", []):
        for step in handler.get("steps", []):
            command = step.get("shell", {}).get("command", "")
            for pattern in dangerous_patterns:
                if pattern in command:
                    raise SecurityError(f"Dangerous command detected: {pattern}")
    
    return True
```

### 2. Sandbox Creation
```python
def create_sandbox(sandbox_type="kind"):
    """Create isolated sandbox environment."""
    
    if sandbox_type == "kind":
        return create_kind_sandbox()
    elif sandbox_type == "container":
        return create_container_sandbox()
    else:
        raise ValueError(f"Unsupported sandbox type: {sandbox_type}")

def create_kind_sandbox():
    """Create kind cluster sandbox."""
    
    cluster_name = f"atom-dryrun-{int(time.time())}"
    kubeconfig_path = f"/tmp/kubeconfig-{cluster_name}"
    
    # Create cluster with timeout
    result = subprocess.run([
        "kind", "create", "cluster",
        "--name", cluster_name,
        "--kubeconfig", kubeconfig_path,
        "--wait", "300s"
    ], capture_output=True, timeout=600)
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create kind cluster: {result.stderr}")
    
    return {
        "type": "kind",
        "cluster_name": cluster_name,
        "kubeconfig": kubeconfig_path,
        "cleanup_cmd": f"kind delete cluster --name {cluster_name}"
    }
```

### 3. Workflow Execution
```python
def execute_in_sandbox(wpk_data, sandbox_config):
    """Execute workflow in sandbox environment."""
    
    try:
        # Set sandbox environment
        env = os.environ.copy()
        if sandbox_config["type"] == "kind":
            env["KUBECONFIG"] = sandbox_config["kubeconfig"]
        
        # Execute handlers
        results = []
        for handler in wpk_data.get("spec", {}).get("handlers", []):
            handler_result = execute_handler(handler, env, sandbox_config)
            results.append(handler_result)
        
        return {
            "status": "success",
            "results": results,
            "sandbox": sandbox_config["type"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "sandbox": sandbox_config["type"]
        }
```

### 4. Cleanup
```python
def cleanup_sandbox(sandbox_config):
    """Clean up sandbox environment."""
    
    try:
        if sandbox_config["type"] == "kind":
            subprocess.run([
                "kind", "delete", "cluster",
                "--name", sandbox_config["cluster_name"]
            ], timeout=120)
            
            # Remove kubeconfig
            kubeconfig_path = sandbox_config.get("kubeconfig")
            if kubeconfig_path and os.path.exists(kubeconfig_path):
                os.remove(kubeconfig_path)
        
        elif sandbox_config["type"] == "container":
            container_name = sandbox_config["container_name"]
            subprocess.run(["docker", "stop", container_name], timeout=30)
            subprocess.run(["docker", "rm", container_name], timeout=30)
            
            # Remove network
            network_name = sandbox_config.get("network_name")
            if network_name:
                subprocess.run(["docker", "network", "rm", network_name], timeout=30)
        
        logger.info(f"Sandbox cleanup completed: {sandbox_config['type']}")
        
    except Exception as e:
        logger.error(f"Sandbox cleanup failed: {e}")
```

## Configuration

### Sandbox Limits
```yaml
sandbox:
  limits:
    cpu: "2"
    memory: "4Gi"
    storage: "10Gi"
    execution_time: "30m"
    network_bandwidth: "100Mbps"
  
  security:
    allow_privileged: false
    allow_host_network: false
    allow_host_pid: false
    drop_capabilities:
      - ALL
    add_capabilities:
      - NET_BIND_SERVICE
  
  cleanup:
    auto_cleanup: true
    cleanup_timeout: "5m"
    force_cleanup: true
```

### Resource Monitoring
```python
def monitor_sandbox_resources(sandbox_config):
    """Monitor sandbox resource usage."""
    
    if sandbox_config["type"] == "kind":
        # Monitor kind cluster resources
        result = subprocess.run([
            "kubectl", "--kubeconfig", sandbox_config["kubeconfig"],
            "top", "nodes", "--no-headers"
        ], capture_output=True, text=True)
        
        # Parse resource usage
        lines = result.stdout.strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                cpu_usage = parts[2]
                memory_usage = parts[4]
                
                # Check limits
                if cpu_usage.rstrip('%') > 80:
                    logger.warning(f"High CPU usage in sandbox: {cpu_usage}")
                if memory_usage.rstrip('%') > 80:
                    logger.warning(f"High memory usage in sandbox: {memory_usage}")
```

## Usage Examples

### Basic Dry-Run
```bash
# Create sandbox and run workflow
./sandbox_runner.sh --type=kind --wpk=restart-unhealthy.wpk.yaml --timeout=30m

# Output:
# Creating kind cluster: atom-dryrun-1640995200
# Executing workflow: restart-unhealthy
# Step 1/3: Checking pod health... OK
# Step 2/3: Restarting unhealthy pods... OK (dry-run)
# Step 3/3: Verifying restart... OK (simulated)
# Cleaning up sandbox...
# Dry-run completed successfully
```

### Advanced Dry-Run with Monitoring
```bash
# Run with resource monitoring
./sandbox_runner.sh \
  --type=kind \
  --wpk=scale-on-latency.wpk.yaml \
  --monitor-resources \
  --save-logs=/tmp/dryrun-logs \
  --timeout=45m
```

## Integration with Registry

### Dry-Run Endpoint
```python
@app.post("/workflows/{workflow_id}/dry-run")
async def dry_run_workflow(workflow_id: str, parameters: Optional[Dict] = None):
    """Execute workflow in sandbox environment."""
    
    # Load workflow
    workflow = get_workflow(workflow_id)
    wpk_content = load_wpk_content(workflow["file_path"])
    
    # Validate for sandbox execution
    validate_for_sandbox(wpk_content)
    
    # Create sandbox
    sandbox_config = create_sandbox("kind")
    
    try:
        # Execute dry-run
        result = execute_in_sandbox(wpk_content, sandbox_config)
        
        return {
            "workflow_id": workflow_id,
            "dry_run_result": result,
            "sandbox_type": sandbox_config["type"],
            "execution_time": result.get("execution_time"),
            "resource_usage": result.get("resource_usage")
        }
        
    finally:
        # Always cleanup
        cleanup_sandbox(sandbox_config)
```

## Monitoring and Logging

### Execution Metrics
- **Success Rate**: Percentage of successful dry-runs
- **Execution Time**: Average and percentile execution times
- **Resource Usage**: CPU, memory, and storage consumption
- **Error Rate**: Types and frequency of errors

### Security Monitoring
- **Escape Attempts**: Detection of container/sandbox escape attempts
- **Network Violations**: Unauthorized network access attempts
- **Resource Abuse**: Excessive resource consumption patterns
- **Malicious Patterns**: Known attack signatures in workflows

## Troubleshooting

### Common Issues

1. **Kind Cluster Creation Fails**
   ```bash
   # Check Docker daemon
   docker info
   
   # Check kind installation
   kind version
   
   # Check available resources
   docker system df
   ```

2. **Sandbox Timeout**
   ```bash
   # Increase timeout
   ./sandbox_runner.sh --timeout=60m
   
   # Check resource limits
   kubectl top nodes
   ```

3. **Network Isolation Issues**
   ```bash
   # Verify network configuration
   docker network ls
   
   # Check firewall rules
   iptables -L
   ```

## Future Enhancements

### Planned Features
- **GPU Sandbox**: Support for GPU-accelerated workloads
- **Multi-Cloud**: Sandbox execution across cloud providers
- **Compliance**: Automated compliance checking in sandbox
- **Performance**: Benchmark and performance testing capabilities

### Integration Roadmap
- **CI/CD**: Integration with GitHub Actions and GitLab CI
- **IDE**: VS Code extension for local dry-run execution
- **Monitoring**: Integration with Prometheus and Grafana
- **Security**: Integration with security scanning tools