# Naksha Cloud — Task 01: End-to-End RAG Workload Test

## Goal
Run a large Retrieval-Augmented Generation job to verify:
- LangGraph orchestration end-to-end
- Vector index writes + retrievals
- Database write-back
- Job completion and metrics

## 1. Run a large job
```bash
curl -X POST http://localhost:30589/v1/jobs \
  -H "Content-Type: application/json" \
  -d @services/langgraph/graph_definitions/sample_rag_large.json
```

## 2. Poll job status
```bash
while true; do
  curl -s http://localhost:30589/v1/jobs/<job_id> | tee /tmp/job_status.json
  grep -q '"state": "completed"' /tmp/job_status.json && break
  sleep 10
done
```

## 3. Validate results
1. Ensure `"state": "completed"`
2. Check `"vector_hits" > 0` in the result
3. Connect to Postgres and confirm new rows
4. Confirm metrics show increased counters

## 4. Success criteria
✅ Job state = completed
✅ Vector hits > 0
✅ DB writes confirmed
✅ Metrics counters increased