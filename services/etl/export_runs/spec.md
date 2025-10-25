# Data Export Specification

## Export Schedule
- **Daily**: Last 24 hours of workflow runs
- **Weekly**: Aggregated metrics and trends
- **Monthly**: Full dataset for model retraining

## Data Processing Pipeline
1. Extract workflow runs from PostgreSQL
2. Generate embeddings using OpenAI API
3. Apply labeling rules for training
4. Export to JSONL format
5. Upload to training data store

## Retention Policy
- Raw exports: 90 days
- Processed training data: 2 years
- Model artifacts: Indefinite

## Quality Assurance
- Data validation checks
- Schema compliance verification
- Duplicate detection and removal
- Privacy scrubbing for sensitive data