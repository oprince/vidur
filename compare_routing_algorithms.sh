#!/bin/bash
# compare_routing_algorithms.sh
# Compares Round Robin, LOR, and LLMD Prefix Cache Aware routing algorithms

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
    --metrics_config_wandb_project llmd_routing_comparison
    --metrics_config_write_metrics
"

echo "========================================"
echo "  Routing Algorithm Comparison Suite"
echo "========================================"
echo ""

# Test Round Robin (baseline)
echo "▶ [1/3] Running Round Robin (baseline)..."
conda run -p ./env python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type round_robin \
    --metrics_config_wandb_group round_robin
echo "✅ Round Robin complete"
echo ""

# Test LOR (Least Outstanding Requests)
echo "▶ [2/3] Running LOR (Least Outstanding Requests)..."
conda run -p ./env python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type lor \
    --metrics_config_wandb_group lor
echo "✅ LOR complete"
echo ""

# Test LLMD Prefix Cache Aware (new algorithm)
echo "▶ [3/3] Running LLMD Prefix Cache Aware (new algorithm)..."
conda run -p ./env python -m vidur.main $COMMON_ARGS \
    --global_scheduler_config_type llmd_prefix_cache_aware \
    --metrics_config_wandb_group prefix_cache_aware
echo "✅ LLMD Prefix Cache Aware complete"
echo ""

echo "========================================"
echo "✅ All simulations complete!"
echo "📊 View results at:"
echo "   https://wandb.ai/oprince10-ibm/llmd_routing_comparison"
echo "========================================"
