# F.6.1 — Schema Visualizer

**Phase:** F.6  
**Branch:** `prod-feature/f.6.1-schema-visualizer`  
**Agent:** @amazon-q  
**Priority:** High  
**Labels:** agent-plan, phase-F.6, backend, UI  

---

## 🎯 Objective
Implement `/api/data/schema` endpoints for Data Studio backend and connect Schema Visualizer UI to live database metadata.

---

## 📁 File Structure

| Path | Description |
|------|--------------|
| `services/data-api/schema.py` | Schema metadata endpoints |
| `ui/launchpad/components/SchemaVisualizer.js` | Interactive schema diagram |
| `tests/integration/test_f_6_1.py` | Integration test |
| `reports/F.6.1_summary.md` | Generated agent report |

---

## ⚙️ Endpoints / Features

```
GET /api/data/schema/tables     → list of tables with columns
GET /api/data/schema/relations  → foreign-key relationships
POST /api/data/schema/analyze   → analyze table structure
```

---

## 🧪 Verification Commands
```bash
pytest -q tests/integration/test_f_6_1.py > /reports/logs/F.6.1.log 2>&1 || true
curl -s http://localhost:8001/api/health > /reports/F.6.1_health.json || true
```

---

## ✅ Acceptance Criteria

1. All endpoints respond correctly (`200 OK`).
2. Tests in `tests/integration/test_f_6_1.py` pass.
3. `/reports/F.6.1_summary.md` exists and includes health output.
4. Schema visualizer shows table relationships.

---

## 🧩 Compliance Checklist

| Policy | Description | Status |
|--------|-------------|--------|
| **P1 Data Privacy** | No PII in logs | ✅ |
| **P2 Secrets & Signing** | Uses Vault for secrets | ✅ |
| **P3 Execution Safety** | Manual approval for auto ops | ✅ |
| **P4 Observability** | `/health` + `/metrics` active | ✅ |
| **P5 Multi-Tenancy** | Tenant ID in JWT enforced | ✅ |
| **P6 Performance Budget** | p95 latency < 1s | ✅ |

---

## ⚠️ Failure / Simulation Mode

If external infra unavailable:
* Set `SIMULATION_MODE=true`
* Use mock schema data
* Add "BLOCKED" note in report

---

## 📤 Agent Actions Sequence

1. Create branch `prod-feature/f.6.1-schema-visualizer`
2. Implement schema endpoints
3. Create UI component
4. Run tests and verification
5. Generate report
6. Commit + push
7. Update GitHub Issue to **Completed**

---

## 📈 Outputs

* `/reports/F.6.1_summary.md`
* `/reports/logs/F.6.1.log`
* Working schema visualization
* Integration test results

---

## 🧾 Notes

* Maintain consistent naming with existing data-api
* Use SQLite introspection for table metadata
* All commits must pass CI

---

# ✅ End of Specification