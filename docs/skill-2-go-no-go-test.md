# Skill 2: Go-No-Go Test for New Algorithm

This guide shows how to run a basic validation test for your newly implemented routing algorithm.

## Purpose

A go-no-go test verifies:
- ✅ Algorithm runs without errors
- ✅ Completes a short simulation successfully
- ✅ Generates basic metrics
- ✅ Integration with Vidur works correctly

## Quick Test Command

```bash
python -m vidur.main \
    --global_scheduler_config_type your_algorithm \
    --replica_config_device h100 \
    --replica_config_model_name meta-llama/Llama-2-70b-hf \
    --cluster_config_num_replicas 2 \
    --replica_config_tensor_parallel_size 2 \
    --request_generator_config_type synthetic \
    --synthetic_request_generator_config_duration 60 \
    --poisson_request_interval_generator_config_qps 2 \
    --length_generator_config_type trace \
    --trace_request_length_generator_config_trace_file ./data/processed_traces/splitwise_conv.csv \
    --metrics_config_write_metrics
```

**Configuration Notes:**
- **Duration**: 60 seconds (short test)
- **QPS**: 2 (low load)
- **Replicas**: 2 (minimal setup)
- **Metrics**: Enabled to verify output

## Expected Output

### Success Indicators

```
✓ Simulation completed successfully
✓ Total requests processed: ~120
✓ No errors or warnings
✓ Metrics generated in output directory
```

### Output Files

Check for generated files in the output directory:
```
output/
├── metrics.json
├── request_metrics.csv
└── replica_metrics.csv
```

## Validation Checklist

### 1. Basic Functionality
```bash
# Test completes without errors
echo $?  # Should return 0
```

### 2. Request Processing
```python
# Check metrics.json
import json
with open('output/metrics.json') as f:
    metrics = json.load(f)
    print(f"Requests completed: {metrics['num_requests_completed']}")
    print(f"Average E2E time: {metrics['request_e2e_time_mean']:.2f}s")
```

### 3. Algorithm Execution
Look for log messages indicating your algorithm is running:
```bash
grep "YourAlgorithmScheduler" output/simulation.log
```

## Common Issues

### Issue 1: Import Errors
```
ImportError: cannot import name 'YourAlgorithmScheduler'
```
**Fix:** Ensure you added the import in `global_scheduler_registry.py`

### Issue 2: Config Not Found
```
ValueError: Unknown scheduler type 'your_algorithm'
```
**Fix:** Verify enum is added in `global_scheduler_type.py` and config class exists

### Issue 3: Simulation Hangs
```
Simulation stuck at "Starting simulation..."
```
**Fix:** Check your `schedule()` method returns properly and doesn't have infinite loops

## Quick Validation Script

Create `validate_algorithm.sh`:

```bash
#!/bin/bash
set -e

echo "🧪 Running go-no-go test for your algorithm..."

python -m vidur.main \
    --global_scheduler_config_type your_algorithm \
    --replica_config_device h100 \
    --replica_config_model_name meta-llama/Llama-2-70b-hf \
    --cluster_config_num_replicas 2 \
    --replica_config_tensor_parallel_size 2 \
    --request_generator_config_type synthetic \
    --synthetic_request_generator_config_duration 60 \
    --poisson_request_interval_generator_config_qps 2 \
    --length_generator_config_type trace \
    --trace_request_length_generator_config_trace_file ./data/processed_traces/splitwise_conv.csv \
    --metrics_config_write_metrics

if [ $? -eq 0 ]; then
    echo "✅ Go-No-Go Test PASSED"
    echo "📊 Metrics generated in output directory"
else
    echo "❌ Go-No-Go Test FAILED"
    exit 1
fi
```

Run it:
```bash
chmod +x validate_algorithm.sh
./validate_algorithm.sh
```

## WandB Integration (Optional)

Add WandB logging to track your test:

```bash
python -m vidur.main \
    --global_scheduler_config_type your_algorithm \
    # ... other args ...
    --metrics_config_wandb_project my_algorithm_tests \
    --metrics_config_wandb_group go_no_go_test
```

## Next Steps

Once your algorithm passes the go-no-go test:
1. ✅ Algorithm is functionally correct
2. → Proceed to [Skill 3: Comparison Test](skill-3-comparison-test.md)
3. → Compare against baseline algorithms

## Reference

See complete example go-no-go test:
- Test configuration in [compare_routing_algorithms.sh](https://github.com/oprince/vidur/blob/test_new_routing_algorithm/compare_routing_algorithms.sh)
