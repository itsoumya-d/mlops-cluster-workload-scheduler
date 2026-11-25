import pytest
from src.scheduler.models import AcceleratorNode, WorkloadJob, NodeHealth
from src.scheduler.engine import WorkloadScheduler

def test_priority_scheduling():
    sched = WorkloadScheduler()
    sched.register_node(AcceleratorNode(node_id="node-a", accelerator_type="IPU-POD", total_devices=8))

    low = WorkloadJob(job_id="job-low", required_devices=4, priority=1)
    high = WorkloadJob(job_id="job-high", required_devices=4, priority=10)

    sched.submit_job(low)
    sched.submit_job(high)

    scheduled = sched.schedule_pending()
    assert len(scheduled) == 2
    # High priority must be scheduled first
    assert scheduled[0][0] == "job-high"
    assert scheduled[1][0] == "job-low"
    assert sched.nodes["node-a"].used_devices == 8
    assert len(sched.pending_jobs) == 0

def test_insufficient_capacity_stays_pending():
    sched = WorkloadScheduler()
    sched.register_node(AcceleratorNode(node_id="node-small", accelerator_type="IPU-POD", total_devices=4))

    big_job = WorkloadJob(job_id="job-big", required_devices=8, priority=5)
    sched.submit_job(big_job)

    scheduled = sched.schedule_pending()
    assert len(scheduled) == 0
    assert len(sched.pending_jobs) == 1
    assert sched.pending_jobs[0].job_id == "job-big"

def test_unhealthy_node_eviction():
    sched = WorkloadScheduler()
    sched.register_node(AcceleratorNode(node_id="node-1", accelerator_type="IPU-POD", total_devices=8))
    sched.register_node(AcceleratorNode(node_id="node-2", accelerator_type="IPU-POD", total_devices=8))

    job = WorkloadJob(job_id="job-train-1", required_devices=4, priority=5)
    sched.submit_job(job)
    sched.schedule_pending()
    assert job.assigned_node == "node-1"

    # Node-1 suffers hardware fault
    evacuated = sched.update_node_health("node-1", NodeHealth.UNHEALTHY, fault_count=3)
    assert "job-train-1" in evacuated
    assert sched.nodes["node-1"].used_devices == 0
    assert len(sched.pending_jobs) == 1

    # Reschedule moves it to healthy node-2
    new_scheduled = sched.schedule_pending()
    assert len(new_scheduled) == 1
    assert new_scheduled[0] == ("job-train-1", "node-2")
