from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime

class NodeHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

@dataclass
class AcceleratorNode:
    node_id: str
    accelerator_type: str  # e.g., IPU-POD, H100
    total_devices: int
    used_devices: int = 0
    health: NodeHealth = NodeHealth.HEALTHY
    temperature_celsius: float = 45.0
    fault_count: int = 0

    @property
    def free_devices(self) -> int:
        return max(0, self.total_devices - self.used_devices)

@dataclass
class WorkloadJob:
    job_id: str
    required_devices: int
    priority: int  # Higher value = higher priority
    assigned_node: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
