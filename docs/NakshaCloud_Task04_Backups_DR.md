# Naksha Cloud — Task 04: Backups & Disaster Recovery (Postgres + VectorDB)

---

## Goal
Automate daily database and vector-index backups with S3 storage and provide restore scripts.

---

## 1. Prerequisites
Secrets or env vars required (through Vault or .env):

| Name | Purpose |
|------|----------|
| `AWS_ACCESS_KEY_ID` | S3 upload key |
| `AWS_SECRET_ACCESS_KEY` | S3 secret |
| `S3_BUCKET` | Target bucket (`naksha-backups`) |
| `AWS_REGION` | Region (`ap-south-1` example) |

If S3 unavailable, backups can be written to `/data/backups/`.

---

## 2. Kubernetes CronJobs

### Postgres Backup
`infra/backup/postgres-backup-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: langgraph
spec:
  schedule: "0 1 * * *"    # daily 01:00 UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: bitnami/postgresql:15
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: S3_BUCKET
              valueFrom:
                secretKeyRef:
                  name: s3-creds
                  key: bucket
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: s3-creds
                  key: accessKey
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: s3-creds
                  key: secretKey
            command:
              - /bin/sh
              - -c
              - |
                ts=$(date +%F_%H-%M)
                pg_dump -U $POSTGRES_USER -h $POSTGRES_HOST $POSTGRES_DB \
                  | gzip > /tmp/backup_$ts.sql.gz
                aws s3 cp /tmp/backup_$ts.sql.gz s3://$S3_BUCKET/postgres/
          restartPolicy: OnFailure
```

### Vector DB (Milvus or custom vector service)

`infra/backup/vector-backup-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: vector-backup
  namespace: vector
spec:
  schedule: "30 1 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: vector-backup
            image: naksha/vector:latest
            command:
              - /bin/sh
              - -c
              - |
                ts=$(date +%F_%H-%M)
                python /app/ingestion/export_vectors.py \
                  --output /tmp/vector_$ts.json
                aws s3 cp /tmp/vector_$ts.json s3://$S3_BUCKET/vector/
          restartPolicy: OnFailure
```

---

## 3. Restore Scripts

`infra/scripts/restore_from_backup.sh`

```bash
#!/bin/bash
# Usage: ./restore_from_backup.sh <backup_file>
set -e
BACKUP_FILE=$1
echo "Restoring from $BACKUP_FILE ..."
gunzip -c "$BACKUP_FILE" | psql "$DATABASE_URL"
echo "Restore completed."
```

For vector restore (add to `infra/scripts/restore_vectors.sh`):

```bash
#!/bin/bash
python /app/ingestion/ingest.py --file $1
```

Make scripts executable:

```bash
chmod +x infra/scripts/restore_from_backup.sh infra/scripts/restore_vectors.sh
```

---

## 4. Apply Manifests and Test

```bash
kubectl apply -f infra/backup/postgres-backup-cronjob.yaml
kubectl apply -f infra/backup/vector-backup-cronjob.yaml
kubectl get cronjobs -A
kubectl get jobs -A
```

Manual trigger (for testing):

```bash
kubectl create job --from=cronjob/postgres-backup postgres-backup-manual -n langgraph
kubectl logs job/postgres-backup-manual -n langgraph
```

Confirm file exists in S3 or `/data/backups/`.

---

## 5. Verification

* Both CronJobs `ACTIVE 0`, `LAST SCHEDULE < 1m>` ✅
* `kubectl logs` shows upload to S3 ✅
* Downloaded `.sql.gz` file valid ✅
* Run `restore_from_backup.sh` and confirm DB restored ✅

---

## 6. Reporting

Create:

* `/reports/backup_report.md` (summary with timestamps and S3 paths)
* `/reports/logs/backup_apply.log` (cronjob creation and run logs)
  Commit to branch `prod-hardening/04-backups-dr`.
  Open PR: **"prod-hardening: 04 Backups & DR CronJobs"**.

---

## 7. Success Criteria

✅ CronJobs deployed and visible
✅ Manual run produces valid dump and upload
✅ Restore scripts executed successfully
✅ Reports committed and PR created