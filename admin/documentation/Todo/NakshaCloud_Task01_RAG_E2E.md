Task 1 is the **End-to-End RAG workload test**—the first validation of your LangGraph + Vector + database dataflow.
If you haven’t already created it, you can add this small `.md` so the agent can run it and generate `/reports/rag_e2e.json` before the production-hardening sequence.

---

### **File path:**

`/docs/NakshaCloud_Task01_RAG_E2E.md`

````markdown
# Naksha Cloud — Task 01: End-to-End RAG Workload Test

---

## Goal
Run a large Retrieval-Augmented Generation job to verify:
- LangGraph orchestration end-to-end
- Vector index writes + retrievals
- Database write-back
- Job completion and metrics

---

## 1. Run a large job
```bash
curl -X POST http://localhost:30589/v1/jobs \
  -H "Content-Type: application/x-yaml" \
  --data-binary @services/langgraph/graph_definitions/sample_rag_large.yaml
````

Save the returned `job_id`.

---

## 2. Poll job status

```bash
while true; do
  curl -s http://localhost:30589/v1/jobs/<job_id> | tee /tmp/job_status.json
  grep -q '"state": "completed"' /tmp/job_status.json && break
  sleep 10
done
```

---

## 3. Validate results

1. Ensure `"state": "completed"`.
2. Check `"vector_hits" > 0` in the result.
3. Connect to Postgres and confirm new rows:

   ```bash
   kubectl exec -n langgraph deploy/langgraph -- \
     psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM rag_results;"
   ```
4. Confirm LangGraph and Vector `/metrics` show increased counters.

---

## 4. Artifacts

| File                        | Purpose                        |
| --------------------------- | ------------------------------ |
| `/reports/rag_e2e.json`     | job result JSON                |
| `/reports/logs/rag_e2e.log` | combined stdout + kubectl logs |

---

## 5. Reporting

Add a new branch `prod-hardening/01-rag-e2e`.
Commit:

* `docs/NakshaCloud_Task01_RAG_E2E.md`
* generated reports/logs

Create PR titled **“prod-hardening: 01 RAG E2E Workload Test”**.

---

## 6. Success criteria

✅ Job state = completed
✅ Vector hits > 0
✅ DB writes confirmed
✅ Metrics counters increased
✅ Reports committed

---



