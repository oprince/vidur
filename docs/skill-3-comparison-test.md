# Skill 3: Comparison Test with Baseline Algorithms

This guide shows how to compare your new routing algorithm against baseline algorithms in Vidur.

## Purpose

A comparison test:
- 📊 Benchmarks your algorithm vs. existing algorithms
- 📈 Generates side-by-side performance metrics
- 🔍 Identifies strengths and weaknesses
- ✅ Validates improvements over baselines

## Comparison Script Template

Create `compare_algorithms.sh`:

```bash
#!/bin/bash
set -e

COMMON_ARGS="
    --replica_config_device h100
    --replica_config_model_name meta-llama/Llama-2-70b-hf
    --cluster_config_num_replicas 4
    --replica_config_tensor_parallel_size 4
    --request_generator_config_type synthetic
    --synthetic_request_generator_config_duration 300
    --poisson_request_interval_generator_config_qps 4
    --length_generator_config_type trace
    --trace_request_length_generator_config_trace_file ./data/processed_traces/splitwise_conv.csv
    --metrics_config_wandb_project algorithm_comparison
    --metrics_config_write_metrics
"

echo "========================================"
echo "  Routing Algorithm Comparison Suite"
echo "========================================"
echo ""

# Baseline 1: Round Robin
echo "▶ [1/4] Running Round Robin (baseline)..."
python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type round_robin \
    --metrics_config_wandb_group round_robin
echo "✅ Round Robin complete"
echo ""

# Baseline 2: LOR (Least Outstanding Requests)
echo "▶ [2/4] Running LOR (baseline)..."
python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type lor \
    --metrics_config_wandb_group lor
echo "✅ LOR complete"
echo ""

# Baseline 3: Random (optional)
echo "▶ [3/4] Running Random (baseline)..."
python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type random \
    --metrics_config_wandb_group random
echo "✅ Random complete"
echo ""

# Your Algorithm
echo "▶ [4/4] Running YourAlgorithm (new)..."
python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type your_algorithm \
    --metrics_config_wandb_group your_algorithm
echo "✅ YourAlgorithm complete"
echo ""

echo "========================================"
echo "✅ All simulations complete!"
echo "📊 View results at:"
echo "   https://wandb.ai/your-username/algorithm_comparison"
echo "========================================"
```

## Configuration Parameters

### Standard Test Configuration

```bash
# Hardware
--replica_config_device h100
--cluster_config_num_replicas 4
--replica_config_tensor_parallel_size 4

# Model
--replica_config_model_name meta-llama/Llama-2-70b-hf

# Workload
--synthetic_request_generator_config_duration 300  # 5 minutes
--poisson_request_interval_generator_config_qps 4  # Moderate load
--trace_request_length_generator_config_trace_file ./data/processed_traces/splitwise_conv.csv
```

### Workload Variations

**Light Load:**
```bash
--synthetic_request_generator_config_duration 180
--poisson_request_interval_generator_config_qps 2
```

**Heavy Load:**
```bash
--synthetic_request_generator_config_duration 600
--poisson_request_interval_generator_config_qps 8
```

## Running the Comparison

```bash
chmod +x compare_algorithms.sh
./compare_algorithms.sh
```

Expected runtime: ~20-30 minutes for 4 algorithms

## Metrics to Compare

### Latency Metrics
- **Request E2E Time (P50, P99)**: Total request completion time
- **TTFT (Time to First Token)**: Prefill latency
- **TPOT (Time Per Output Token)**: Decode latency

### System Metrics
- **Throughput**: Requests completed per second
- **Queue Depth**: Average pending requests per replica
- **Load Balance**: Distribution of requests across replicas

### View in WandB

1. Navigate to your WandB project
2. Compare runs side-by-side
3. Look for:
   - Lower latency (better)
   - Higher throughput (better)
   - More balanced load distribution (better)

## Analysis Template

### Performance Summary Table

| Algorithm | P50 Latency | P99 Latency | Throughput | Load Balance |
|-----------|-------------|-------------|------------|--------------|
| Round Robin | 20s | 60s | 4.0 req/s | ⭐⭐⭐⭐⭐ |
| LOR | 22s | 65s | 3.8 req/s | ⭐⭐⭐⭐ |
| Random | 25s | 80s | 3.5 req/s | ⭐⭐⭐ |
| **YourAlgorithm** | **?** | **?** | **?** | **?** |

### Key Questions

1. **Does your algorithm improve P50 latency?**
   - Yes → Good median case performance
   - No → May have overhead

2. **Does your algorithm improve P99 latency?**
   - Yes → Better tail latency, fewer outliers
   - No → May create imbalances

3. **Is throughput maintained or improved?**
   - Higher → More efficient
   - Lower → Check for bottlenecks

4. **Is load balanced across replicas?**
   - Yes → Efficient resource utilization
   - No → Some replicas may be idle

## Advanced Comparison

### Multi-Workload Testing

Test with different workload patterns:

```bash
# Workload 1: Short requests
./compare_algorithms.sh --trace_file splitwise_conv.csv

# Workload 2: Long requests  
./compare_algorithms.sh --trace_file arxiv_summarization.csv

# Workload 3: Mixed
./compare_algorithms.sh --length_generator_config_type zipf
```

### Stress Testing

Increase load to find breaking points:

```bash
for qps in 2 4 8 16; do
    echo "Testing at ${qps} QPS..."
    ./compare_algorithms.sh --qps $qps
done
```

## Visualization

### Generate Comparison Charts

```python
import wandb
import matplotlib.pyplot as plt

api = wandb.Api()
runs = api.runs("your-username/algorithm_comparison")

algorithms = []
p50_latencies = []

for run in runs:
    algorithms.append(run.config['global_scheduler_config_type'])
    p50_latencies.append(run.summary['request_e2e_time_p50'])

plt.bar(algorithms, p50_latencies)
plt.ylabel('P50 Latency (s)')
plt.title('Algorithm Comparison')
plt.savefig('comparison.png')
```

## Common Patterns

### Your Algorithm Performs Better
✅ **Celebrate!** Document:
- Which metrics improved
- By how much
- Under what conditions

### Your Algorithm Performs Worse
🔍 **Investigate:**
- Algorithm overhead
- Load imbalance
- Edge cases
- Iterate and improve

### Mixed Results
📊 **Analyze trade-offs:**
- Better P50 but worse P99?
- Better under light load only?
- Workload-dependent behavior?

## Next Steps

After comparison testing:
1. ✅ Document performance characteristics
2. ✅ Identify optimal use cases
3. → Consider production deployment
4. → Monitor real-world performance

## Reference

Complete example:
- [compare_routing_algorithms.sh](https://github.com/oprince/vidur/blob/test_new_routing_algorithm/compare_routing_algorithms.sh)
- [WandB Comparison Results](https://wandb.ai/oprince10-ibm/llmd_routing_comparison)
