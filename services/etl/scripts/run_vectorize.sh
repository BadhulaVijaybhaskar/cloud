#!/bin/bash
# ETL Vectorization Pipeline Runner
# Exports workflow runs and creates embeddings

set -e

EXPORT_FILE="${1:-/tmp/runs.jsonl}"
VECTOR_FILE="${2:-/tmp/vectors.json}"
LIMIT="${3:-100}"

echo "=== ATOM ETL Vectorization Pipeline ==="
echo "Export file: $EXPORT_FILE"
echo "Vector file: $VECTOR_FILE"
echo "Record limit: $LIMIT"
echo "Timestamp: $(date)"

# Step 1: Export workflow runs
echo "Step 1: Exporting workflow runs..."
python services/etl/export_runs/export_to_jsonl.py \
    --output "$EXPORT_FILE" \
    --limit "$LIMIT" \
    --verbose

if [ ! -f "$EXPORT_FILE" ]; then
    echo "ERROR: Export failed, file not created: $EXPORT_FILE"
    exit 1
fi

RECORD_COUNT=$(wc -l < "$EXPORT_FILE")
echo "Exported $RECORD_COUNT records"

# Step 2: Vectorize records
echo "Step 2: Vectorizing records..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "WARNING: OPENAI_API_KEY not set, using local embeddings"
fi

python services/etl/vectorize/vectorize.py \
    --input "$EXPORT_FILE" \
    --output "$VECTOR_FILE" \
    --verbose

if [ ! -f "$VECTOR_FILE" ]; then
    echo "ERROR: Vectorization failed, file not created: $VECTOR_FILE"
    exit 1
fi

# Step 3: Verify results
echo "Step 3: Verifying results..."
VECTOR_COUNT=$(python -c "
import json
with open('$VECTOR_FILE') as f:
    data = json.load(f)
    print(data['metadata']['total_vectors'])
")

echo "Pipeline completed successfully:"
echo "  Records exported: $RECORD_COUNT"
echo "  Vectors created: $VECTOR_COUNT"

echo "ETL pipeline completed at $(date)"