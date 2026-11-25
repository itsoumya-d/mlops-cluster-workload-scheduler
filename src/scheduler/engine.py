from typing import Dict, List, Optional, Tuple
from .models import AcceleratorNode, WorkloadJob, NodeHealth

class WorkloadScheduler:
    def __init__(self):
        self.nodes: Dict[str, AcceleratorNode] = {}
        self.pending_jobs: List[WorkloadJob] = []
        self.running_jobs: Dict[str, WorkloadJob] = {}

    def register_node(self, node: AcceleratorNode):
        self.nodes[node.node_id] = node

    def submit_job(self, job: WorkloadJob):
        self.pending_jobs.append(job)

    def schedule_pending(self) -> List[Tuple[str, str]]:
        """Schedules pending jobs onto healthy nodes with matching capacity."""
        # Sort by priority descending
        self.pending_jobs.sort(key=lambda j: -j.priority)
        scheduled: List[Tuple[str, str]] = []
        unassigned: List[WorkloadJob] = []

        for job in self.pending_jobs:
            assigned = False
            # Find healthiest node with sufficient free devices
            candidate_nodes = [
                n for n in self.nodes.values()
                if n.health == NodeHealth.HEALTHY and n.free_devices >= job.required_devices
            ]
            # Pick node with least free devices (best-fit bin packing)
            candidate_nodes.sort(key=lambda n: n.free_devices)

            if candidate_nodes:
                target_node = candidate_nodes[0]
                target_node.used_devices += job.required_devices
                job.assigned_node = target_node.node_id
                self.running_jobs[job.job_id] = job
                scheduled.append((job.job_id, target_node.node_id))
                assigned = True

            if not assigned:
                unassigned.append(job)

        self.pending_jobs = unassigned
        return scheduled

    def complete_job(self, job_id: str) -> bool:
        """Releases devices when a workload finishes."""
        if job_id not in self.running_jobs:
            return False
        job = self.running_jobs.pop(job_id)
        if job.assigned_node and job.assigned_node in self.nodes:
            node = self.nodes[job.assigned_node]
            node.used_devices = max(0, node.used_devices - job.required_devices)
        return True

    def update_node_health(self, node_id: str, health: NodeHealth, fault_count: int = 0) -> List[str]:
        """Updates health and evacuates jobs if the node is no longer healthy."""
        if node_id not in self.nodes:
            return []

        node = self.nodes[node_id]
        node.health = health
        node.fault_count = fault_count
        evacuated_job_ids: List[str] = []

        if health != NodeHealth.HEALTHY:
            # Evacuate running jobs on this node
            for jid, job in list(self.running_jobs.items()):
                if job.assigned_node == node_id:
                    del self.running_jobs[jid]
                    job.assigned_node = None
                    job.priority += 10  # Priority boost for evacuated jobs
                    self.pending_jobs.append(job)
                    evacuated_job_ids.append(jid)
            node.used_devices = 0

        return evacuated_job_ids
