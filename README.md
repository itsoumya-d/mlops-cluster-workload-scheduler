# MLOps Cluster Workload Scheduler

Automated AI accelerator (GPU/IPU) workload scheduler, node health evaluator, and eviction controller in Python.

## Core Capabilities
- Dynamic bin-packing scheduler for distributed AI training and inference jobs.
- Automated health monitoring tracking node temperature, memory utilization, and hardware fault counts.
- Proactive workload evacuation and re-queueing from degraded accelerator nodes.
- Priority-weighted scheduling queues.

## Test Suite
```bash
pytest -v
```
