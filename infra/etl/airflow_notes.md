# ETL Pipeline Orchestration

## Airflow DAG Configuration
```python
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta

dag = DAG(
    'atom_data_export',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False
)

export_task = BashOperator(
    task_id='export_workflow_runs',
    bash_command='python /opt/atom/etl/export_runs.py --date {{ ds }}',
    dag=dag
)
```

## Alternative: Cron Jobs
```bash
# Daily export at 2 AM
0 2 * * * /opt/atom/etl/export_runs.py --date $(date -d yesterday +%Y-%m-%d)

# Weekly aggregation on Sundays
0 3 * * 0 /opt/atom/etl/weekly_export.py
```

## Monitoring
- Export success/failure alerts
- Data quality metrics
- Processing time monitoring
- Storage usage tracking