# Skill 1: Implement a New Routing Algorithm in Vidur

This guide walks through implementing a new global scheduler (routing algorithm) in Vidur.

## Files to Modify/Create

You'll need to work with 4 files:

1. **NEW:** `vidur/scheduler/global_scheduler/{your_algorithm}_scheduler.py`
2. **MODIFIED:** `vidur/types/global_scheduler_type.py`
3. **MODIFIED:** `vidur/scheduler/global_scheduler/global_scheduler_registry.py`
4. **MODIFIED:** `vidur/config/config.py`

## Step 1: Create Scheduler Class

Create a new file `vidur/scheduler/global_scheduler/{your_algorithm}_scheduler.py`:

```python
from typing import List, Tuple
from vidur.entities import Request
from vidur.scheduler.global_scheduler.base_global_scheduler import BaseGlobalScheduler

class YourAlgorithmScheduler(BaseGlobalScheduler):
    """
    Brief description of your routing algorithm.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize any algorithm-specific state here
        self._your_state = {}
    
    def schedule(self) -> List[Tuple[int, Request]]:
        """
        Main scheduling logic.
        Returns: List of (replica_id, request) tuples
        """
        self.sort_requests()  # Sort by arrival time
        request_mapping = []
        
        while self._request_queue:
            request = self._request_queue.pop(0)
            
            # Your algorithm logic here
            best_replica_id = self._select_replica(request)
            request_mapping.append((best_replica_id, request))
        
        return request_mapping
    
    def _select_replica(self, request: Request) -> int:
        """Your replica selection logic"""
        # Implement your algorithm here
        pass
```

**Key Methods:**
- `schedule()`: Main entry point called by the simulator
- `sort_requests()`: Sorts pending requests by arrival time
- `_request_queue`: List of pending requests
- `_replicas`: Dict of available replicas

## Step 2: Add Enum Type

Edit `vidur/types/global_scheduler_type.py`:

```python
from vidur.types.base_int_enum import BaseIntEnum

class GlobalSchedulerType(BaseIntEnum):
    RANDOM = 1
    ROUND_ROBIN = 2
    LOR = 3
    YOUR_ALGORITHM = 4  # Add your algorithm
```

## Step 3: Register Scheduler

Edit `vidur/scheduler/global_scheduler/global_scheduler_registry.py`:

```python
from vidur.scheduler.global_scheduler.your_algorithm_scheduler import YourAlgorithmScheduler
from vidur.types import GlobalSchedulerType
from vidur.utils import BaseRegistry

class GlobalSchedulerRegistry(BaseRegistry):
    pass

# Existing registrations...

GlobalSchedulerRegistry.register(
    GlobalSchedulerType.YOUR_ALGORITHM,
    YourAlgorithmScheduler
)
```

## Step 4: Add Configuration

Edit `vidur/config/config.py`:

```python
from dataclasses import dataclass
from vidur.config.base_poly_config import BaseGlobalSchedulerConfig
from vidur.types import GlobalSchedulerType

@dataclass
class YourAlgorithmGlobalSchedulerConfig(BaseGlobalSchedulerConfig):
    # Add any algorithm-specific config parameters here
    # Example: your_param: int = 10
    
    @staticmethod
    def get_type():
        return GlobalSchedulerType.YOUR_ALGORITHM
```

## Step 5: Test Your Implementation

Run a basic test:

```bash
python -m vidur.main \
    --global_scheduler_config_type your_algorithm \
    --replica_config_device h100 \
    --replica_config_model_name meta-llama/Llama-2-70b-hf \
    --cluster_config_num_replicas 4 \
    --replica_config_tensor_parallel_size 4 \
    --request_generator_config_type synthetic \
    --synthetic_request_generator_config_duration 60 \
    --poisson_request_interval_generator_config_qps 2
```

## Common Patterns

### Access Replica State
```python
for replica_id, replica in self._replicas.items():
    num_pending = len(replica.request_queue)
```

### Track Custom Metrics
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._custom_metric = 0

def schedule(self):
    # Your logic
    self._custom_metric += 1
```

### Load Balancing
```python
def _find_least_loaded_replica(self) -> int:
    return min(
        self._replicas.keys(),
        key=lambda rid: len(self._replicas[rid].request_queue)
    )
```

## Next Steps

Once implemented, proceed to:
- [Skill 2: Go-No-Go Test](skill-2-go-no-go-test.md)
- [Skill 3: Comparison Test](skill-3-comparison-test.md)

## Example Reference

See the complete implementation example:
- [llmd_prefix_cache_aware_scheduler.py](https://github.com/oprince/vidur/blob/test_new_routing_algorithm/vidur/scheduler/global_scheduler/llmd_prefix_cache_aware_scheduler.py)
