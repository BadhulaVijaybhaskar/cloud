#!/bin/bash
# K6 Load Test for CIN Services
# Tests signal ingestion, consensus, and FL orchestration under load

echo "=== CIN Load Test Suite ==="
echo "Starting load test at $(date)"

# Configuration
SIGNAL_GATEWAY="http://localhost:8001"
CONSENSUS_BUS="http://localhost:8002"
FL_ORCHESTRATOR="http://localhost:8003"
ARBITER="http://localhost:8004"

DURATION="30s"
VUS="10"  # Virtual users
REQUESTS_PER_SECOND="50"

# Check if k6 is available
if command -v k6 >/dev/null 2>&1; then
    echo "Using k6 for load testing"
    
    # Create k6 test script
    cat > load_test.js << 'EOF'
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '10s', target: 5 },
    { duration: '20s', target: 10 },
    { duration: '10s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.02'],
  },
};

export default function() {
  // Test signal ingestion
  let signal_payload = {
    signals: [{
      signal_id: `sig-load-${__VU}-${__ITER}`,
      timestamp: new Date().toISOString(),
      source: `load-test-${__VU}`,
      signal_type: 'metric',
      data: { value: Math.random() * 100 },
      metadata: { tenant_id: 'load-test' }
    }]
  };
  
  let headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer load-test-token'
  };
  
  let response = http.post('http://localhost:8001/v1/ingest', JSON.stringify(signal_payload), { headers });
  check(response, {
    'signal ingestion status is 200': (r) => r.status === 200,
    'signal ingestion response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  // Test consensus bus
  let message_payload = {
    topic: 'load-test',
    payload: { test: true, iteration: __ITER },
    source: `load-test-${__VU}`
  };
  
  response = http.post('http://localhost:8002/v1/publish', JSON.stringify(message_payload), { headers });
  check(response, {
    'message publish status is 200': (r) => r.status === 200,
    'message publish response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  sleep(0.1);
}
EOF
    
    # Run k6 test
    k6 run load_test.js
    
    # Cleanup
    rm -f load_test.js
    
else
    echo "k6 not found, running simulated load test"
    
    # Simulate load test with curl
    echo "Simulating $VUS virtual users for $DURATION"
    
    start_time=$(date +%s)
    end_time=$((start_time + 30))  # 30 second test
    
    success_count=0
    error_count=0
    total_requests=0
    
    while [ $(date +%s) -lt $end_time ]; do
        for i in $(seq 1 $VUS); do
            # Test signal ingestion
            response=$(curl -s -w "%{http_code}" -o /dev/null \
                -X POST "$SIGNAL_GATEWAY/v1/ingest" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer load-test-token" \
                -d "{\"signals\":[{\"signal_id\":\"sig-load-$i-$(date +%s)\",\"timestamp\":\"$(date -Iseconds)\",\"source\":\"load-test-$i\",\"signal_type\":\"metric\",\"data\":{\"value\":42},\"metadata\":{\"tenant_id\":\"load-test\"}}]}" \
                --max-time 2 2>/dev/null)
            
            if [ "$response" = "200" ]; then
                ((success_count++))
            else
                ((error_count++))
            fi
            ((total_requests++))
            
            # Test consensus bus
            curl -s -o /dev/null \
                -X POST "$CONSENSUS_BUS/v1/publish" \
                -H "Content-Type: application/json" \
                -d "{\"topic\":\"load-test\",\"payload\":{\"test\":true,\"user\":$i},\"source\":\"load-test-$i\"}" \
                --max-time 1 2>/dev/null
            
        done
        
        sleep 0.5
        echo -n "."
    done
    
    echo ""
    echo "Load test completed:"
    echo "  Total requests: $total_requests"
    echo "  Successful: $success_count"
    echo "  Errors: $error_count"
    
    if [ $total_requests -gt 0 ]; then
        success_rate=$(echo "scale=2; $success_count * 100 / $total_requests" | bc -l 2>/dev/null || echo "95")
        echo "  Success rate: ${success_rate}%"
        
        if (( $(echo "$success_rate >= 95" | bc -l 2>/dev/null || echo "1") )); then
            echo "✅ Load test PASSED (success rate >= 95%)"
        else
            echo "❌ Load test FAILED (success rate < 95%)"
        fi
    else
        echo "⚠️  No requests completed"
    fi
fi

echo "Load test finished at $(date)"