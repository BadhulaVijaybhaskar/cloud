# atomctl CLI Specification

## Commands

### pack
Package YAML workflow into WPK format with metadata validation.

### sign  
Sign WPK with cosign private key and embed signature.

### push
Upload signed WPK to workflow registry with authentication.

### run
Execute workflow with parameters and return run ID.

### list
List available workflows with filtering options.

### status
Get workflow execution status and logs.

## Example Workflow
```bash
atomctl pack restart-pods.yaml -o restart-pods.wpk.yaml
atomctl sign restart-pods.wpk.yaml --key cosign.key
atomctl push restart-pods.wpk.yaml --registry https://atom.company.com
atomctl run restart-pods --version 1.0.0 --params '{"namespace": "production"}'
```