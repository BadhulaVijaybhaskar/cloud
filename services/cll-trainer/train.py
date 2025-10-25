# train.py: reads /tmp/agent_runs for simulation, writes model_versions.json
import json, os, uuid, time
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def load_training_data():
    """Load training data from agent runs or simulate"""
    input_path = os.getenv("CLL_INPUT", "/tmp/agent_runs")
    
    # Simulate training data if no real data available
    if not os.path.exists(input_path) or not os.listdir(input_path):
        print("No agent run data found, generating synthetic training data...")
        return generate_synthetic_data()
    
    # Load real agent run data
    features = []
    labels = []
    
    for filename in os.listdir(input_path):
        if filename.endswith('.json'):
            with open(os.path.join(input_path, filename), 'r') as f:
                try:
                    run_data = json.load(f)
                    # Extract features from run data
                    feature = extract_features(run_data)
                    label = extract_label(run_data)
                    features.append(feature)
                    labels.append(label)
                except:
                    continue
    
    if not features:
        return generate_synthetic_data()
    
    return np.array(features), np.array(labels)

def generate_synthetic_data():
    """Generate synthetic training data for simulation"""
    np.random.seed(42)
    n_samples = 1000
    
    # Generate features: cpu_usage, memory_usage, error_rate, response_time
    features = np.random.rand(n_samples, 4)
    features[:, 0] *= 100  # CPU usage (0-100%)
    features[:, 1] *= 100  # Memory usage (0-100%)
    features[:, 2] *= 20   # Error rate (0-20%)
    features[:, 3] *= 1000 # Response time (0-1000ms)
    
    # Generate labels based on realistic failure conditions
    labels = np.zeros(n_samples)
    for i in range(n_samples):
        cpu, memory, error_rate, response_time = features[i]
        failure_prob = 0
        if cpu > 80: failure_prob += 0.3
        if memory > 85: failure_prob += 0.3
        if error_rate > 10: failure_prob += 0.2
        if response_time > 500: failure_prob += 0.2
        failure_prob += np.random.normal(0, 0.1)
        labels[i] = 1 if failure_prob > 0.5 else 0
    
    return features, labels.astype(int)

def extract_features(run_data):
    """Extract features from agent run data"""
    # Simulate feature extraction
    return [75.0, 60.0, 2.5, 150.0]  # cpu, memory, error_rate, response_time

def extract_label(run_data):
    """Extract label from agent run data"""
    # Simulate label extraction based on decision
    decision = run_data.get('stages', {}).get('decide', {}).get('decision', 'no_action')
    return 1 if decision != 'no_action_needed' else 0

def train_model(X, y):
    """Train the continuous learning model"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = LogisticRegression(random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    return model, accuracy

def save_model(model, accuracy, model_id):
    """Save model to model store"""
    os.makedirs("/tmp/cll_models", exist_ok=True)
    
    # Save model metadata
    model_info = {
        "model_id": model_id,
        "created": time.time(),
        "accuracy": float(accuracy),
        "model_type": "continuous_learning",
        "version": "1.0",
        "features": ["cpu_usage", "memory_usage", "error_rate", "response_time"]
    }
    
    # Save model file (simulate)
    model_path = f"/tmp/cll_models/{model_id}.json"
    with open(model_path, "w") as f:
        json.dump(model_info, f, indent=2)
    
    return model_info

def main():
    """Main training pipeline"""
    print("Starting Continuous Learning Loop training...")
    
    # Load data
    X, y = load_training_data()
    print(f"Loaded {len(X)} training samples")
    
    # Train model
    model, accuracy = train_model(X, y)
    print(f"Model trained with accuracy: {accuracy:.3f}")
    
    # Save model
    model_id = str(uuid.uuid4())
    model_info = save_model(model, accuracy, model_id)
    
    print(f"Model saved: {model_id}")
    print(json.dumps(model_info, indent=2))
    
    return model_info

if __name__ == "__main__":
    main()