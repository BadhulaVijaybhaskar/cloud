#!/usr/bin/env bash
set -euo pipefail

SIMULATION_MODE="${SIMULATION_MODE:-true}"
S3_BUCKET="${S3_BUCKET:-atom-audit-archive}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE_PATH=$(date -u +"%Y/%m/%d")
SRC_DIR="reports/l3"
DEST_PREFIX="l3/${DATE_PATH}"

echo "Archive script starting. SIMULATION_MODE=${SIMULATION_MODE}"
echo "Source: ${SRC_DIR}"
echo "Destination: s3://${S3_BUCKET}/${DEST_PREFIX}"
echo "Retention (days): ${RETENTION_DAYS}"

if [ ! -d "${SRC_DIR}" ]; then
  echo "No reports directory found at ${SRC_DIR} — nothing to archive."
  exit 0
fi

if [ "${SIMULATION_MODE}" = "true" ]; then
  echo "[SIMULATION] Would upload files:"
  find "${SRC_DIR}" -type f -maxdepth 1 -print
  echo "[SIMULATION] Command sample:"
  echo "aws s3 cp ${SRC_DIR}/ s3://$S3_BUCKET/$DEST_PREFIX/ --recursive"
  exit 0
fi

# Real upload
aws s3 cp "${SRC_DIR}/" "s3://${S3_BUCKET}/${DEST_PREFIX}/" --recursive --acl bucket-owner-full-control
echo "Uploaded reports to s3://${S3_BUCKET}/${DEST_PREFIX}/"

# Apply lifecycle via tagging
for f in $(find "${SRC_DIR}" -type f -maxdepth 1); do
  fname=$(basename "$f")
  aws s3api put-object-tagging --bucket "${S3_BUCKET}" --key "${DEST_PREFIX}/${fname}" \
    --tagging "TagSet=[{Key=retention_days,Value=${RETENTION_DAYS}}]"
done

echo "Archival complete."