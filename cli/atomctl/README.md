# atomctl - ATOM CLI Tool

## Installation
```bash
pip install -e .
```

## Commands

### pack - Package workflow
```bash
atomctl pack workflow.yaml --output workflow.wpk.yaml
```

### sign - Sign with cosign
```bash
atomctl sign workflow.wpk.yaml --key cosign.key
```

### push - Upload to registry
```bash
atomctl push workflow.wpk.yaml --registry http://localhost:8000
```

### run - Execute workflow
```bash
atomctl run workflow-name --version 1.0.0 --params params.json
```

### list - List workflows
```bash
atomctl list --registry http://localhost:8000
```

### status - Check workflow status
```bash
atomctl status workflow-run-id
```