#!/usr/bin/env python3
"""
Model Optimization Pipeline - Phase C.5
Automates model training, validation, and deployment
"""

import sqlite3
import json
import os
import pickle
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib

@dataclass
class ModelVersion:
    id: str
    version: str
    model_type: str
    accuracy: float
    precision_score: float
    recall_score: float
    f1_score: float
    model_path: str
    status: str
    active: bool

@dataclass
class TrainingJob:
    id: str
    model_version_id: str
    job_name: str
    status: str
    progress_percent: int
    current_step: str
    final_accuracy: Optional[float] = None

class ModelTrainingPipeline:
    def __init__(self, db_path: str = "model_pipeline.db", models_dir: str = "models"):
        self.db_path = db_path
        self.models_dir = models_dir
        self.vault_available = False  # Simulate Vault unavailability
        
        # Create models directory
        os.makedirs(models_dir, exist_ok=True)
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database for fallback"""
        conn = sqlite3.connect(self.db_path)
        
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS model_versions (
                id TEXT PRIMARY KEY,
                version TEXT UNIQUE NOT NULL,
                model_type TEXT DEFAULT 'predictive_failure',
                accuracy REAL CHECK (accuracy >= 0 AND accuracy <= 1),
                precision_score REAL CHECK (precision_score >= 0 AND precision_score <= 1),
                recall_score REAL CHECK (recall_score >= 0 AND recall_score <= 1),
                f1_score REAL CHECK (f1_score >= 0 AND f1_score <= 1),
                training_data_size INTEGER DEFAULT 0,
                model_path TEXT,
                model_checksum TEXT,
                model_signature TEXT,
                status TEXT DEFAULT 'training',
                active BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                activated_at TEXT,
                created_by TEXT,
                hyperparameters TEXT DEFAULT '{}',
                training_config TEXT DEFAULT '{}'
            );
            
            CREATE TABLE IF NOT EXISTS training_jobs (
                id TEXT PRIMARY KEY,
                model_version_id TEXT,
                job_name TEXT NOT NULL,
                status TEXT DEFAULT 'queued',
                progress_percent INTEGER DEFAULT 0,
                current_step TEXT,
                total_steps INTEGER DEFAULT 0,
                final_accuracy REAL,
                training_loss REAL,
                validation_loss REAL,
                started_at TEXT,
                completed_at TEXT,
                duration_sec INTEGER,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT
            );
            
            CREATE TABLE IF NOT EXISTS model_performance_history (
                id TEXT PRIMARY KEY,
                model_version_id TEXT,
                measured_at TEXT DEFAULT CURRENT_TIMESTAMP,
                accuracy REAL,
                precision_score REAL,
                recall_score REAL,
                f1_score REAL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0
            );
        """)
        
        # Insert initial model if not exists
        cursor = conn.execute("SELECT COUNT(*) FROM model_versions")
        if cursor.fetchone()[0] == 0:
            self._insert_initial_model(conn)
        
        conn.commit()
        conn.close()
    
    def _insert_initial_model(self, conn):
        """Insert initial model version from C.1"""
        initial_model_id = str(uuid.uuid4())
        conn.execute("""
            INSERT INTO model_versions 
            (id, version, model_type, accuracy, precision_score, recall_score, f1_score,
             training_data_size, model_path, status, active, created_by)
            VALUES (?, 'v1.0', 'predictive_failure', 0.75, 0.72, 0.78, 0.75,
                    1000, '/models/predictive_v1.0.pkl', 'active', 1, 'system')
        """, (initial_model_id,))
    
    def generate_training_data(self, size: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Generate synthetic training data for model training"""
        np.random.seed(42)  # For reproducible results
        
        # Generate features: cpu_usage, memory_usage, error_rate, response_time
        features = np.random.rand(size, 4)
        
        # Scale features to realistic ranges
        features[:, 0] *= 100  # CPU usage (0-100%)
        features[:, 1] *= 100  # Memory usage (0-100%)
        features[:, 2] *= 20   # Error rate (0-20%)
        features[:, 3] *= 1000 # Response time (0-1000ms)
        
        # Generate labels based on realistic failure conditions
        labels = np.zeros(size)
        for i in range(size):
            cpu, memory, error_rate, response_time = features[i]
            
            # Failure probability based on thresholds
            failure_prob = 0
            if cpu > 80: failure_prob += 0.3
            if memory > 85: failure_prob += 0.3
            if error_rate > 10: failure_prob += 0.2
            if response_time > 500: failure_prob += 0.2
            
            # Add some randomness
            failure_prob += np.random.normal(0, 0.1)
            labels[i] = 1 if failure_prob > 0.5 else 0
        
        return features, labels.astype(int)
    
    def create_training_job(self, job_name: str, hyperparameters: Dict = None) -> TrainingJob:
        """Create a new training job"""
        job_id = str(uuid.uuid4())
        model_version_id = str(uuid.uuid4())
        
        # Generate new version number
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT MAX(CAST(SUBSTR(version, 2) AS REAL)) FROM model_versions")
        max_version = cursor.fetchone()[0] or 1.0
        new_version = f"v{max_version + 0.1:.1f}"
        
        # Create model version record
        conn.execute("""
            INSERT INTO model_versions 
            (id, version, model_type, status, created_by, hyperparameters)
            VALUES (?, ?, 'predictive_failure', 'training', 'pipeline', ?)
        """, (model_version_id, new_version, json.dumps(hyperparameters or {})))
        
        # Create training job
        conn.execute("""
            INSERT INTO training_jobs 
            (id, model_version_id, job_name, status, total_steps, created_by)
            VALUES (?, ?, ?, 'queued', 5, 'pipeline')
        """, (job_id, model_version_id, job_name))
        
        conn.commit()
        conn.close()
        
        return TrainingJob(
            id=job_id,
            model_version_id=model_version_id,
            job_name=job_name,
            status='queued',
            progress_percent=0,
            current_step='Queued'
        )
    
    def run_training_job(self, job_id: str) -> bool:
        """Execute a training job"""
        try:
            # Update job status
            self._update_job_progress(job_id, 'running', 0, 'Starting training')
            
            # Get job details
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute("""
                SELECT tj.model_version_id, mv.version, mv.hyperparameters
                FROM training_jobs tj
                JOIN model_versions mv ON tj.model_version_id = mv.id
                WHERE tj.id = ?
            """, (job_id,))
            
            row = cursor.fetchone()
            if not row:
                conn.close()
                return False
            
            model_version_id, version, hyperparams_json = row
            hyperparams = json.loads(hyperparams_json or '{}')
            conn.close()
            
            # Step 1: Generate training data
            self._update_job_progress(job_id, 'running', 20, 'Generating training data')
            X, y = self.generate_training_data(size=hyperparams.get('data_size', 1500))
            
            # Step 2: Split data
            self._update_job_progress(job_id, 'running', 40, 'Splitting data')
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Step 3: Scale features
            self._update_job_progress(job_id, 'running', 60, 'Scaling features')
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Step 4: Train model
            self._update_job_progress(job_id, 'running', 80, 'Training model')
            model = LogisticRegression(
                C=hyperparams.get('C', 1.0),
                max_iter=hyperparams.get('max_iter', 1000),
                random_state=42
            )
            model.fit(X_train_scaled, y_train)
            
            # Step 5: Evaluate model
            self._update_job_progress(job_id, 'running', 90, 'Evaluating model')
            y_pred = model.predict(X_test_scaled)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, zero_division=0)
            recall = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=3)
            cv_accuracy = cv_scores.mean()
            
            # Save model
            model_filename = f"predictive_{version}.pkl"
            model_path = os.path.join(self.models_dir, model_filename)
            
            # Save both model and scaler
            model_data = {
                'model': model,
                'scaler': scaler,
                'feature_names': ['cpu_usage', 'memory_usage', 'error_rate', 'response_time'],
                'version': version,
                'training_accuracy': accuracy,
                'cv_accuracy': cv_accuracy
            }
            
            joblib.dump(model_data, model_path)
            
            # Calculate checksum
            checksum = self._calculate_file_checksum(model_path)
            
            # Sign model (simulate Vault signing)
            signature = self._sign_model(model_path, checksum)
            
            # Update model version with results
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE model_versions 
                SET accuracy = ?, precision_score = ?, recall_score = ?, f1_score = ?,
                    training_data_size = ?, model_path = ?, model_checksum = ?,
                    model_signature = ?, status = 'validation'
                WHERE id = ?
            """, (accuracy, precision, recall, f1, len(X), model_path, checksum, signature, model_version_id))
            
            # Complete training job
            conn.execute("""
                UPDATE training_jobs 
                SET status = 'completed', progress_percent = 100, current_step = 'Completed',
                    final_accuracy = ?, completed_at = CURRENT_TIMESTAMP,
                    duration_sec = (strftime('%s', 'now') - strftime('%s', started_at))
                WHERE id = ?
            """, (accuracy, job_id))
            
            conn.commit()
            conn.close()
            
            # Auto-activate if accuracy improved
            if self._should_activate_model(model_version_id, accuracy):
                self.activate_model_version(model_version_id)
            
            return True
            
        except Exception as e:
            # Handle training failure
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                UPDATE training_jobs 
                SET status = 'failed', error_message = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (str(e), job_id))
            
            conn.execute("""
                UPDATE model_versions 
                SET status = 'failed'
                WHERE id = (SELECT model_version_id FROM training_jobs WHERE id = ?)
            """, (job_id,))
            
            conn.commit()
            conn.close()
            
            return False
    
    def _update_job_progress(self, job_id: str, status: str, progress: int, step: str):
        """Update training job progress"""
        conn = sqlite3.connect(self.db_path)
        
        # Set started_at if transitioning to running
        if status == 'running':
            conn.execute("""
                UPDATE training_jobs 
                SET status = ?, progress_percent = ?, current_step = ?,
                    started_at = CASE WHEN started_at IS NULL THEN CURRENT_TIMESTAMP ELSE started_at END
                WHERE id = ?
            """, (status, progress, step, job_id))
        else:
            conn.execute("""
                UPDATE training_jobs 
                SET status = ?, progress_percent = ?, current_step = ?
                WHERE id = ?
            """, (status, progress, step, job_id))
        
        conn.commit()
        conn.close()
    
    def _calculate_file_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of model file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _sign_model(self, model_path: str, checksum: str) -> str:
        """Sign model with Vault (simulated for P-2 compliance)"""
        if self.vault_available:
            # In production, this would use Vault API
            # vault_client.sign(checksum)
            pass
        
        # Simulate signing with HMAC for development
        import hmac
        secret_key = os.getenv('MODEL_SIGNING_KEY', 'dev-model-key')
        signature = hmac.new(
            secret_key.encode(),
            checksum.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"dev-hmac:{signature}"
    
    def _should_activate_model(self, model_version_id: str, accuracy: float) -> bool:
        """Determine if new model should be automatically activated"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT accuracy FROM model_versions 
            WHERE active = 1 AND model_type = 'predictive_failure'
        """)
        
        current_accuracy = cursor.fetchone()
        conn.close()
        
        if not current_accuracy:
            return True  # No active model, activate this one
        
        # Activate if accuracy improved by at least 2%
        improvement_threshold = 0.02
        return accuracy > (current_accuracy[0] + improvement_threshold)
    
    def activate_model_version(self, model_version_id: str) -> bool:
        """Activate a model version"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Deactivate current active model
            conn.execute("""
                UPDATE model_versions 
                SET active = 0 
                WHERE active = 1 AND model_type = 'predictive_failure'
            """)
            
            # Activate new model
            conn.execute("""
                UPDATE model_versions 
                SET active = 1, status = 'active', activated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND status = 'validation'
            """, (model_version_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_model_versions(self, limit: int = 10) -> List[ModelVersion]:
        """Get model versions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, version, model_type, accuracy, precision_score, recall_score, 
                   f1_score, model_path, status, active
            FROM model_versions 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append(ModelVersion(
                id=row[0], version=row[1], model_type=row[2],
                accuracy=row[3] or 0.0, precision_score=row[4] or 0.0,
                recall_score=row[5] or 0.0, f1_score=row[6] or 0.0,
                model_path=row[7] or '', status=row[8], active=bool(row[9])
            ))
        
        conn.close()
        return versions
    
    def get_training_jobs(self, limit: int = 10) -> List[TrainingJob]:
        """Get training jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT id, model_version_id, job_name, status, progress_percent, 
                   current_step, final_accuracy
            FROM training_jobs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append(TrainingJob(
                id=row[0], model_version_id=row[1], job_name=row[2],
                status=row[3], progress_percent=row[4] or 0,
                current_step=row[5] or 'Unknown', final_accuracy=row[6]
            ))
        
        conn.close()
        return jobs
    
    def record_model_performance(self, model_version_id: str, accuracy: float, 
                               precision: float, recall: float, f1: float,
                               total_predictions: int = 0, correct_predictions: int = 0) -> str:
        """Record model performance metrics"""
        performance_id = str(uuid.uuid4())
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO model_performance_history 
            (id, model_version_id, accuracy, precision_score, recall_score, f1_score,
             total_predictions, correct_predictions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (performance_id, model_version_id, accuracy, precision, recall, f1,
              total_predictions, correct_predictions))
        
        conn.commit()
        conn.close()
        
        return performance_id
    
    def load_active_model(self):
        """Load the currently active model"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("""
            SELECT model_path, version FROM model_versions 
            WHERE active = 1 AND model_type = 'predictive_failure'
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        if not row or not row[0]:
            return None, None
        
        model_path, version = row
        
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                return model_data, version
        except Exception:
            pass
        
        return None, None

def main():
    """Main pipeline execution"""
    pipeline = ModelTrainingPipeline()
    
    print("Starting Model Training Pipeline")
    print("=" * 50)
    
    # Create and run training job
    job = pipeline.create_training_job(
        job_name="Automated Training v2.0",
        hyperparameters={
            'C': 0.8,
            'max_iter': 1500,
            'data_size': 2000
        }
    )
    
    print(f"Created training job: {job.job_name} ({job.id})")
    
    # Run training
    success = pipeline.run_training_job(job.id)
    
    if success:
        print("Training completed successfully")
        
        # Show results
        versions = pipeline.get_model_versions(limit=3)
        print("\nModel Versions:")
        for v in versions:
            status_icon = "[ACTIVE]" if v.active else "[INACTIVE]"
            print(f"  {status_icon} {v.version}: {v.accuracy:.3f} accuracy ({v.status})")
        
        # Show active model
        model_data, version = pipeline.load_active_model()
        if model_data:
            print(f"\nActive Model: {version}")
            print(f"   Training Accuracy: {model_data.get('training_accuracy', 0):.3f}")
            print(f"   CV Accuracy: {model_data.get('cv_accuracy', 0):.3f}")
        
    else:
        print("Training failed")
        
        # Show job status
        jobs = pipeline.get_training_jobs(limit=1)
        if jobs:
            job = jobs[0]
            print(f"   Status: {job.status}")
            print(f"   Step: {job.current_step}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())