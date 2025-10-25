#!/usr/bin/env python3
"""
NeuralOps ETL Vectorization Pipeline
Converts workflow run data to embeddings for similarity search.
"""

import os
import json
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

import numpy as np
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorizeEngine:
    """Vectorization engine for workflow run data."""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = "text-embedding-ada-002"
        self.vector_dim = 1536  # OpenAI ada-002 dimension
        
    def vectorize_jsonl(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """Vectorize workflow runs from JSONL file."""
        
        results = {
            "input_file": input_file,
            "output_file": output_file,
            "timestamp": datetime.utcnow().isoformat(),
            "total_records": 0,
            "vectorized_records": 0,
            "failed_records": 0,
            "method": "openai" if self.openai_api_key else "local",
            "errors": []
        }
        
        try:
            vectors = []
            
            with open(input_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                        
                    results["total_records"] += 1
                    
                    try:
                        record = json.loads(line.strip())
                        
                        # Apply data redaction
                        redacted_record = self._redact_pii(record)
                        
                        # Create text representation
                        text = self._record_to_text(redacted_record)
                        
                        # Generate embedding
                        if self.openai_api_key:
                            embedding = self._get_openai_embedding(text)
                        else:
                            embedding = self._get_local_embedding(text)
                        
                        if embedding:
                            vector_record = {
                                "id": record.get("id", f"record_{line_num}"),
                                "text": text,
                                "embedding": embedding,
                                "metadata": {
                                    "workflow_name": record.get("workflow_name"),
                                    "status": record.get("status"),
                                    "duration_ms": record.get("duration_ms"),
                                    "tenant_id": record.get("tenant_id"),
                                    "created_at": record.get("created_at"),
                                    "vector_method": results["method"]
                                }
                            }
                            
                            vectors.append(vector_record)
                            results["vectorized_records"] += 1
                        else:
                            results["failed_records"] += 1
                            
                    except Exception as e:
                        results["failed_records"] += 1
                        results["errors"].append(f"Line {line_num}: {str(e)}")
                        logger.error(f"Failed to process line {line_num}: {e}")
            
            # Save vectors
            with open(output_file, 'w') as f:
                json.dump({
                    "metadata": {
                        "total_vectors": len(vectors),
                        "vector_dimension": self.vector_dim,
                        "method": results["method"],
                        "created_at": results["timestamp"]
                    },
                    "vectors": vectors
                }, f, indent=2)
            
            logger.info(f"Vectorization complete: {results['vectorized_records']}/{results['total_records']} records")
            
        except Exception as e:
            results["errors"].append(f"Vectorization failed: {str(e)}")
            logger.error(f"Vectorization failed: {e}")
        
        return results
    
    def _redact_pii(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII from workflow run record."""
        redacted = record.copy()
        
        # Redact sensitive fields
        pii_fields = [
            "user_email", "email", "username", "user_id", 
            "ip_address", "source_ip", "client_ip",
            "api_key", "token", "password", "secret"
        ]
        
        for field in pii_fields:
            if field in redacted:
                redacted[field] = "[REDACTED]"
        
        # Redact from metadata if it's a dict
        if isinstance(redacted.get("metadata"), dict):
            for field in pii_fields:
                if field in redacted["metadata"]:
                    redacted["metadata"][field] = "[REDACTED]"
        
        # Redact from error messages
        if "error_message" in redacted and redacted["error_message"]:
            error_msg = redacted["error_message"]
            # Simple email redaction
            import re
            error_msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]', error_msg)
            # IP address redaction
            error_msg = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[IP_REDACTED]', error_msg)
            redacted["error_message"] = error_msg
        
        return redacted
    
    def _record_to_text(self, record: Dict[str, Any]) -> str:
        """Convert workflow run record to text for embedding."""
        
        parts = []
        
        # Workflow identification
        if record.get("workflow_name"):
            parts.append(f"Workflow: {record['workflow_name']}")
        
        if record.get("workflow_version"):
            parts.append(f"Version: {record['workflow_version']}")
        
        # Execution details
        if record.get("status"):
            parts.append(f"Status: {record['status']}")
        
        if record.get("duration_ms"):
            duration_sec = record["duration_ms"] / 1000
            parts.append(f"Duration: {duration_sec:.1f}s")
        
        if record.get("steps_completed") and record.get("steps_total"):
            parts.append(f"Steps: {record['steps_completed']}/{record['steps_total']}")
        
        # Error information
        if record.get("error_message"):
            parts.append(f"Error: {record['error_message']}")
        
        # Metadata
        if isinstance(record.get("metadata"), dict):
            metadata = record["metadata"]
            for key, value in metadata.items():
                if key not in ["user_id", "tenant_id"] and value:
                    parts.append(f"{key}: {value}")
        
        return " | ".join(parts)
    
    def _get_openai_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from OpenAI API."""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "input": text,
                "model": self.model
            }
            
            response = requests.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["data"][0]["embedding"]
            
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return None
    
    def _get_local_embedding(self, text: str) -> List[float]:
        """Generate local embedding using simple hashing and random projection."""
        
        # Create deterministic hash-based embedding
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to seed for reproducible random embedding
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)
        
        # Generate random embedding with some structure
        embedding = np.random.normal(0, 1, self.vector_dim)
        
        # Add some semantic structure based on keywords
        keywords = {
            "failed": -0.5, "error": -0.5, "timeout": -0.3,
            "success": 0.5, "completed": 0.4, "passed": 0.3,
            "backup": 0.2, "restore": 0.2, "scale": 0.1,
            "restart": -0.1, "unhealthy": -0.2
        }
        
        text_lower = text.lower()
        for keyword, weight in keywords.items():
            if keyword in text_lower:
                # Modify embedding based on keyword presence
                keyword_hash = hashlib.md5(keyword.encode()).hexdigest()
                keyword_seed = int(keyword_hash[:8], 16)
                np.random.seed(keyword_seed)
                keyword_vector = np.random.normal(0, 0.1, self.vector_dim)
                embedding += weight * keyword_vector
        
        # Normalize embedding
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.tolist()

def main():
    """CLI interface for vectorization."""
    parser = argparse.ArgumentParser(description="Vectorize workflow run data")
    parser.add_argument("--input", "-i", required=True, help="Input JSONL file")
    parser.add_argument("--output", "-o", required=True, help="Output vectors JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file not found: {args.input}")
        return 1
    
    # Initialize vectorizer
    vectorizer = VectorizeEngine()
    
    # Run vectorization
    results = vectorizer.vectorize_jsonl(args.input, args.output)
    
    # Print results
    print(json.dumps(results, indent=2))
    
    # Print summary
    print(f"\nVectorization Summary:")
    print(f"  Total records: {results['total_records']}")
    print(f"  Vectorized: {results['vectorized_records']}")
    print(f"  Failed: {results['failed_records']}")
    print(f"  Method: {results['method']}")
    print(f"  Output: {args.output}")
    
    if results['errors']:
        print(f"  Errors: {len(results['errors'])}")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"    - {error}")
    
    return 0 if results['vectorized_records'] > 0 else 1

if __name__ == "__main__":
    exit(main())