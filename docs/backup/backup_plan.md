# ATOM Backup and Disaster Recovery Plan

## Backup Schedule
- **Daily**: workflow_runs, insight_signals, audit_logs tables
- **Weekly**: Full database backup
- **Monthly**: Archive to long-term storage

## Retention Policy
- Daily backups: 30 days
- Weekly backups: 12 weeks  
- Monthly backups: 12 months

## Recovery Procedures
1. Identify backup file for target date
2. Stop ATOM services
3. Restore database from backup
4. Verify data integrity
5. Restart services

## Testing
- Monthly restore tests to staging environment
- Annual disaster recovery drill
- Backup integrity verification