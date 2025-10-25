# Workflow Run Data Export for NeuralOps Training

## Overview
Export workflow execution data for machine learning model training and analysis.

## Export Format
JSONL (JSON Lines) format with embeddings and labels for training.

## Data Schema
```json
{
  "run_id": "uuid",
  "workflow_id": "string", 
  "execution_time": "iso_timestamp",
  "duration_ms": "integer",
  "status": "success|failed|timeout",
  "parameters": "object",
  "logs": "string",
  "embedding": "float_array",
  "labels": {
    "success": "boolean",
    "error_type": "string",
    "performance_class": "fast|normal|slow"
  }
}
```

## Usage
```bash
python export_runs.py --start-date 2024-01-01 --end-date 2024-01-31 --output training_data.jsonl
```