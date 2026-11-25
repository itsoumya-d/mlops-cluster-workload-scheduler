from src.scheduler.models import AcceleratorNode, NodeHealth

def test_models_scaffold():
    node = AcceleratorNode(node_id="node-01", accelerator_type="IPU-POD", total_devices=16)
    assert node.free_devices == 16
    assert node.health == NodeHealth.HEALTHY
