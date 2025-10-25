#!/usr/bin/env python3
"""
Tests for Model Training Pipeline - Phase C.5
"""

import pytest
import tempfile
import os
import sys
import shutil
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pipeline import ModelTrainingPipeline, ModelVersion, TrainingJob

class TestModelTrainingPipeline:
    """Test cases for model training pipeline"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.temp_models_dir = tempfile.mkdtemp()
        self.pipeline = ModelTrainingPipeline(
            db_path=self.temp_db.name,
            models_dir=self.temp_models_dir
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
        
        if hasattr(self, 'temp_models_dir') and os.path.exists(self.temp_models_dir):
            try:
                shutil.rmtree(self.temp_models_dir)
            except (PermissionError, OSError):
                pass
    
    def test_pipeline_initialization(self):
        """Test pipeline initializes correctly"""
        assert self.pipeline.db_path == self.temp_db.name
        assert self.pipeline.models_dir == self.temp_models_dir
        assert os.path.exists(self.temp_models_dir)
        
        # Check initial model exists
        versions = self.pipeline.get_model_versions()
        assert len(versions) >= 1
        assert versions[0].version == "v1.0"
        assert versions[0].active == True
    
    def test_generate_training_data(self):
        """Test synthetic training data generation"""
        X, y = self.pipeline.generate_training_data(size=100)
        
        assert X.shape == (100, 4)  # 4 features
        assert y.shape == (100,)    # 100 labels
        assert X.dtype == np.float64
        assert y.dtype in [np.int32, np.int64]  # Allow both int32 and int64
        
        # Check feature ranges
        assert np.all(X[:, 0] >= 0) and np.all(X[:, 0] <= 100)  # CPU
        assert np.all(X[:, 1] >= 0) and np.all(X[:, 1] <= 100)  # Memory
        assert np.all(X[:, 2] >= 0) and np.all(X[:, 2] <= 20)   # Error rate
        assert np.all(X[:, 3] >= 0) and np.all(X[:, 3] <= 1000) # Response time
        
        # Check labels are binary
        assert np.all(np.isin(y, [0, 1]))
    
    def test_create_training_job(self):
        """Test training job creation"""
        hyperparams = {'C': 0.5, 'max_iter': 500}
        job = self.pipeline.create_training_job("Test Job", hyperparams)
        
        assert job.job_name == "Test Job"
        assert job.status == "queued"
        assert job.progress_percent == 0
        assert job.current_step == "Queued"
        
        # Verify job was stored
        jobs = self.pipeline.get_training_jobs(limit=1)
        assert len(jobs) >= 1
        assert jobs[0].job_name == "Test Job"
    
    def test_model_version_management(self):
        """Test model version creation and management"""
        initial_versions = self.pipeline.get_model_versions()
        initial_count = len(initial_versions)
        
        # Create new training job (creates new model version)
        job = self.pipeline.create_training_job("Version Test")
        
        # Check new version was created
        versions = self.pipeline.get_model_versions()
        assert len(versions) == initial_count + 1
        
        # Find the new version
        new_version = next(v for v in versions if v.id == job.model_version_id)
        assert new_version.status == "training"
        assert new_version.active == False
    
    def test_run_training_job_success(self):
        """Test successful training job execution"""
        # Create training job with small dataset for speed
        job = self.pipeline.create_training_job(
            "Test Training",
            {'data_size': 200, 'max_iter': 100}
        )
        
        # Run training
        success = self.pipeline.run_training_job(job.id)
        assert success == True
        
        # Check job completion
        jobs = self.pipeline.get_training_jobs(limit=1)
        completed_job = jobs[0]
        assert completed_job.status == "completed"
        assert completed_job.progress_percent == 100
        assert completed_job.final_accuracy is not None
        assert completed_job.final_accuracy > 0
        
        # Check model version was updated
        versions = self.pipeline.get_model_versions()
        trained_version = next(v for v in versions if v.id == job.model_version_id)
        assert trained_version.status in ["validation", "active"]
        assert trained_version.accuracy > 0
        assert trained_version.model_path is not None
    
    def test_model_file_creation(self):
        """Test model file is created and can be loaded"""
        job = self.pipeline.create_training_job(
            "File Test",
            {'data_size': 100, 'max_iter': 50}
        )
        
        success = self.pipeline.run_training_job(job.id)
        assert success == True
        
        # Check model file exists
        versions = self.pipeline.get_model_versions()
        trained_version = next(v for v in versions if v.id == job.model_version_id)
        
        assert os.path.exists(trained_version.model_path)
        
        # Try to load model
        model_data, version = self.pipeline.load_active_model()
        if trained_version.active:
            assert model_data is not None
            assert 'model' in model_data
            assert 'scaler' in model_data
            assert version == trained_version.version
    
    def test_model_activation(self):
        """Test model activation logic"""
        # Get current active model
        initial_versions = self.pipeline.get_model_versions()
        initial_active = next(v for v in initial_versions if v.active)
        
        # Create and train new model
        job = self.pipeline.create_training_job(
            "Activation Test",
            {'data_size': 150, 'max_iter': 100}
        )
        
        success = self.pipeline.run_training_job(job.id)
        assert success == True
        
        # Check activation logic
        versions = self.pipeline.get_model_versions()
        new_version = next(v for v in versions if v.id == job.model_version_id)
        
        # If new model has significantly better accuracy, it should be activated
        if new_version.accuracy > initial_active.accuracy + 0.02:
            assert new_version.active == True
            # Check old model was deactivated
            updated_versions = self.pipeline.get_model_versions()
            old_version = next(v for v in updated_versions if v.id == initial_active.id)
            assert old_version.active == False
    
    def test_performance_recording(self):
        """Test model performance recording"""
        versions = self.pipeline.get_model_versions()
        model_version_id = versions[0].id
        
        performance_id = self.pipeline.record_model_performance(
            model_version_id=model_version_id,
            accuracy=0.85,
            precision=0.82,
            recall=0.88,
            f1=0.85,
            total_predictions=100,
            correct_predictions=85
        )
        
        assert performance_id is not None
        assert len(performance_id) > 0
    
    def test_checksum_calculation(self):
        """Test model file checksum calculation"""
        # Create a temporary file
        test_file = os.path.join(self.temp_models_dir, "test_model.pkl")
        with open(test_file, 'w') as f:
            f.write("test model content")
        
        checksum1 = self.pipeline._calculate_file_checksum(test_file)
        checksum2 = self.pipeline._calculate_file_checksum(test_file)
        
        # Same file should produce same checksum
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA-256 hex length
        
        # Different content should produce different checksum
        with open(test_file, 'w') as f:
            f.write("different content")
        
        checksum3 = self.pipeline._calculate_file_checksum(test_file)
        assert checksum1 != checksum3
    
    def test_model_signing(self):
        """Test model signing for P-2 compliance"""
        test_checksum = "abcdef123456"
        signature = self.pipeline._sign_model("/fake/path", test_checksum)
        
        assert signature is not None
        assert signature.startswith("dev-hmac:")
        assert len(signature) > 20  # Should have substantial length
        
        # Same checksum should produce same signature
        signature2 = self.pipeline._sign_model("/fake/path", test_checksum)
        assert signature == signature2
    
    def test_training_job_failure_handling(self):
        """Test handling of training job failures"""
        # Test with non-existent job ID
        fake_job_id = "non-existent-job-id"
        success = self.pipeline.run_training_job(fake_job_id)
        assert success == False
        
        # Test that the pipeline handles errors gracefully
        # Create a valid job and verify it can be created
        job = self.pipeline.create_training_job("Valid Test Job")
        assert job.status == "queued"
        
        # Verify job exists in database
        jobs = self.pipeline.get_training_jobs(limit=5)
        created_job = next((j for j in jobs if j.job_name == "Valid Test Job"), None)
        assert created_job is not None
        assert created_job.status == "queued"

class TestPolicyCompliance:
    """Test P1-P6 policy compliance"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.temp_models_dir = tempfile.mkdtemp()
        self.pipeline = ModelTrainingPipeline(
            db_path=self.temp_db.name,
            models_dir=self.temp_models_dir
        )
    
    def teardown_method(self):
        """Cleanup test environment"""
        if hasattr(self, 'temp_db') and os.path.exists(self.temp_db.name):
            try:
                os.unlink(self.temp_db.name)
            except (PermissionError, OSError):
                pass
        
        if hasattr(self, 'temp_models_dir') and os.path.exists(self.temp_models_dir):
            try:
                shutil.rmtree(self.temp_models_dir)
            except (PermissionError, OSError):
                pass
    
    def test_p2_secrets_and_signing(self):
        """Test P-2: Secrets management and model signing"""
        # Test that signing uses environment variables
        original_key = os.getenv('MODEL_SIGNING_KEY')
        
        # Test with custom key
        os.environ['MODEL_SIGNING_KEY'] = 'test-secret-key'
        signature1 = self.pipeline._sign_model("/test", "checksum123")
        
        # Test with different key
        os.environ['MODEL_SIGNING_KEY'] = 'different-key'
        signature2 = self.pipeline._sign_model("/test", "checksum123")
        
        # Signatures should be different with different keys
        assert signature1 != signature2
        
        # Restore original key
        if original_key:
            os.environ['MODEL_SIGNING_KEY'] = original_key
        elif 'MODEL_SIGNING_KEY' in os.environ:
            del os.environ['MODEL_SIGNING_KEY']
        
        # Test that no hardcoded secrets exist in code
        with open(os.path.join(os.path.dirname(__file__), '..', 'pipeline.py'), 'r', encoding='utf-8') as f:
            code_content = f.read()
        
        # Check for common secret patterns
        forbidden_patterns = [
            'password=',
            'secret=',
            'key="',
            "key='",
            'token="',
            "token='"
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in code_content.lower(), f"Found potential hardcoded secret: {pattern}"
    
    def test_p3_execution_safety(self):
        """Test P-3: Execution safety with validation"""
        # Test that models go through validation before activation
        job = self.pipeline.create_training_job(
            "Safety Test",
            {'data_size': 100, 'max_iter': 50}
        )
        
        success = self.pipeline.run_training_job(job.id)
        assert success == True
        
        # Check model goes to validation status first
        versions = self.pipeline.get_model_versions()
        new_version = next(v for v in versions if v.id == job.model_version_id)
        
        # Model should be in validation or active (if auto-activated due to improvement)
        assert new_version.status in ['validation', 'active']
        
        # Test manual activation requires validation status
        if new_version.status == 'validation':
            activation_success = self.pipeline.activate_model_version(job.model_version_id)
            assert activation_success == True
    
    def test_p4_observability_metrics(self):
        """Test P-4: Comprehensive metrics and monitoring"""
        # Test that training jobs are tracked
        job = self.pipeline.create_training_job("Metrics Test")
        
        # Check job tracking
        jobs = self.pipeline.get_training_jobs()
        assert len(jobs) >= 1
        
        # Run training and check metrics are recorded
        success = self.pipeline.run_training_job(job.id)
        assert success == True
        
        # Check performance metrics are available
        versions = self.pipeline.get_model_versions()
        trained_version = next(v for v in versions if v.id == job.model_version_id)
        
        # Verify all key metrics are recorded
        assert trained_version.accuracy is not None
        assert trained_version.precision_score is not None
        assert trained_version.recall_score is not None
        assert trained_version.f1_score is not None
        
        # Test performance history recording
        performance_id = self.pipeline.record_model_performance(
            trained_version.id, 0.8, 0.75, 0.85, 0.8, 100, 80
        )
        assert performance_id is not None
    
    def test_p5_multi_tenant_isolation(self):
        """Test P-5: Multi-tenant isolation readiness"""
        # While this service doesn't directly implement multi-tenancy,
        # it should be ready for tenant-scoped model training
        
        # Test that model versions can be associated with tenants
        # (In production, this would include tenant_id in model_versions table)
        
        versions = self.pipeline.get_model_versions()
        assert len(versions) >= 1
        
        # Verify model isolation by checking unique model paths
        model_paths = [v.model_path for v in versions if v.model_path]
        unique_paths = set(model_paths)
        assert len(unique_paths) == len(model_paths), "Model paths should be unique"
    
    def test_p6_performance_budget(self):
        """Test P-6: Performance within budget"""
        import time
        
        # Test that training operations complete within reasonable time
        start_time = time.time()
        
        job = self.pipeline.create_training_job(
            "Performance Test",
            {'data_size': 200, 'max_iter': 100}  # Small dataset for speed
        )
        
        creation_time = time.time() - start_time
        assert creation_time < 1.0, "Job creation should be fast"
        
        # Test training time
        start_time = time.time()
        success = self.pipeline.run_training_job(job.id)
        training_time = time.time() - start_time
        
        assert success == True
        assert training_time < 30.0, "Training should complete within 30 seconds for small dataset"
        
        # Test model loading time
        start_time = time.time()
        model_data, version = self.pipeline.load_active_model()
        loading_time = time.time() - start_time
        
        assert loading_time < 1.0, "Model loading should be fast"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])