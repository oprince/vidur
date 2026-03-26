# vidur/scheduler/global_scheduler/llmd_prefix_cache_aware_scheduler.py

from typing import List, Tuple
from vidur.entities import Request
from vidur.scheduler.global_scheduler.base_global_scheduler import BaseGlobalScheduler


class LLMDPrefixCacheAwareScheduler(BaseGlobalScheduler):
    """
    Simulates llm-d's prefix cache-aware routing algorithm.
    Routes requests to replicas with the highest prefix cache hit probability.

    Assumptions:
    1. Cache state is tracked per-replica (no global cache)
    2. Prefix matching uses simple string comparison based on prompt length buckets
    3. Cache eviction removes random entries when limit is exceeded
    4. Load penalty is linear with queue depth

    Limitations:
    1. Does not model actual KV cache memory constraints
    2. Simplified prefix extraction (production uses token-level matching)
    3. No support for multi-tenant workloads
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Track prefix cache state per replica
        self._replica_cache_state = {
            replica_id: set() for replica_id in self._replicas.keys()
        }

    def _calculate_cache_score(self, request: Request, replica_id: int) -> float:
        """
        Calculate cache hit score for a request on a given replica.
        Higher score = better cache locality.
        """
        # Simulate prefix matching logic
        # In real llm-d, this would check actual KV cache entries
        request_prefix = self._get_request_prefix(request)
        cache_entries = self._replica_cache_state[replica_id]

        # Simple scoring: count matching prefix tokens
        score = 0.0
        for cached_prefix in cache_entries:
            if request_prefix.startswith(cached_prefix):
                score = max(score, len(cached_prefix))

        return score

    def _get_request_prefix(self, request: Request) -> str:
        """
        Extract prefix from request for cache matching.
        In simulation, we use request ID patterns based on prompt length buckets.
        """
        # Simplified: group requests by prompt length ranges (buckets of 100 tokens)
        prompt_length = request.num_prefill_tokens
        return f"prefix_{prompt_length // 100 * 100}"

    def _update_cache_state(self, replica_id: int, request: Request) -> None:
        """Update replica's cache state after routing a request."""
        prefix = self._get_request_prefix(request)
        self._replica_cache_state[replica_id].add(prefix)

        # Simulate cache eviction (keep last N prefixes)
        MAX_CACHE_ENTRIES = 100
        if len(self._replica_cache_state[replica_id]) > MAX_CACHE_ENTRIES:
            # Remove a random entry (simplified eviction)
            self._replica_cache_state[replica_id].pop()

    def schedule(self) -> List[Tuple[int, Request]]:
        """
        Main scheduling logic: route requests to replicas based on cache score and load.
        Returns list of (replica_id, request) tuples.
        """
        self.sort_requests()  # Sort by arrival time

        request_mapping = []

        # Track pending requests locally to account for requests routed in this batch
        pending_requests_map = {
            replica_scheduler.replica_id: replica_scheduler.num_pending_requests
            for replica_scheduler in self._replica_schedulers.values()
        }

        while self._request_queue:
            request = self._request_queue.pop(0)

            # Calculate combined scores for all replicas
            replica_scores = {}
            for replica_id in self._replicas.keys():
                cache_score = self._calculate_cache_score(request, replica_id)

                # Load penalty: penalize replicas with more pending requests
                load_penalty = pending_requests_map[replica_id] * 0.1

                # Combined score: cache benefit - load penalty
                replica_scores[replica_id] = cache_score - load_penalty

            # Route to replica with highest combined score
            best_replica_id = max(replica_scores, key=replica_scores.get)

            # Update cache state and pending count
            self._update_cache_state(best_replica_id, request)
            pending_requests_map[best_replica_id] += 1

            request_mapping.append((best_replica_id, request))

        return request_mapping
