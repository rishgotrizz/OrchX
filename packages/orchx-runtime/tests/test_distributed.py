import pytest
from orchx_core.interfaces.distributed_contracts import (
    NodeProfile,
    WorkerAdvertisement,
    ResourceProfile,
    FaultDomain,
    DistributedEvent
)
from orchx_runtime.distributed_layer import (
    ClusterManager,
    WorkerDiscovery,
    LocalityEngine,
    CapabilityBasedScheduler,
    DistributedEventBridge,
    MemorySynchronizationEngine,
    ExecutionCoordinator,
    ClusterSimulation,
    FaultDomainManager
)

def test_cluster_manager():
    manager = ClusterManager()
    node = NodeProfile(
        node_id="node-1",
        hardware_profile="m2-max",
        operating_system="macOS",
        architecture="arm64",
        capabilities=["apple_silicon", "local_llm"]
    )
    manager.register_node(node)
    
    report = manager.get_cluster_report()
    assert report.active_nodes == 1
    assert report.healthy_nodes == 1
    
    manager.remove_node("node-1")
    assert len(manager.nodes) == 0

def test_worker_discovery():
    discovery = WorkerDiscovery()
    ad = WorkerAdvertisement(
        worker_id="worker-a",
        node_id="node-1",
        capabilities=["gpu", "threejs"],
        resource_limits=ResourceProfile()
    )
    discovery.advertise(ad)
    
    workers = discovery.find_workers_with_capability("gpu")
    assert len(workers) == 1
    assert workers[0].worker_id == "worker-a"

def test_capability_based_scheduler():
    cluster = ClusterManager()
    discovery = WorkerDiscovery()
    locality = LocalityEngine()
    scheduler = CapabilityBasedScheduler(cluster, discovery, locality)
    
    node1 = NodeProfile(
        node_id="node-1", hardware_profile="m2", operating_system="macOS", architecture="arm64",
        capabilities=["cpu"]
    )
    node2 = NodeProfile(
        node_id="node-2", hardware_profile="h100", operating_system="linux", architecture="amd64",
        capabilities=["gpu", "cuda"]
    )
    cluster.register_node(node1)
    cluster.register_node(node2)
    
    # Needs GPU
    selected = scheduler.select_node_for_task(["gpu"], ["ml_training"])
    assert selected is not None
    assert selected.node_id == "node-2"
    
    # Needs Vision (no node has it)
    selected_vision = scheduler.select_node_for_task(["vision"], [])
    assert selected_vision is None

def test_distributed_event_bridge():
    bridge = DistributedEventBridge()
    event = DistributedEvent(
        event_id="evt-1",
        event_type="ExecutionDistributed",
        payload={},
        source_node="node-1"
    )
    assert bridge.publish(event) == True
    assert len(bridge.events) == 1
    
    # Unreachable node DLQ test
    event2 = DistributedEvent(
        event_id="evt-2",
        event_type="NodeJoined",
        payload={},
        source_node="unreachable",
        requires_ack=True
    )
    assert bridge.publish(event2) == False
    assert len(bridge.dlq) == 1

def test_execution_coordinator_failover():
    cluster = ClusterManager()
    cluster.register_node(NodeProfile(node_id="node-1", hardware_profile="m2", operating_system="macOS", architecture="arm64"))
    cluster.register_node(NodeProfile(node_id="node-2", hardware_profile="m2", operating_system="macOS", architecture="arm64"))
    
    coordinator = ExecutionCoordinator()
    plan = coordinator.handle_node_failure("node-1", "task-123", cluster)
    assert plan is not None
    assert plan.target_node == "node-2"

def test_memory_sync_and_simulation():
    engine = MemorySynchronizationEngine()
    report = engine.sync_node("node-1")
    assert report.status == "success"
    
    sim = ClusterSimulation()
    sim_report = sim.run_simulation("node_failure_scenario")
    assert sim_report.simulated_node_failures == 1
    assert "creative memory" in sim_report.advisory_recommendations[0]

def test_fault_domain_isolation():
    manager = FaultDomainManager()
    node1 = NodeProfile(node_id="n1", hardware_profile="m2", operating_system="macOS", architecture="arm64", fault_domain="az-1")
    node2 = NodeProfile(node_id="n2", hardware_profile="m2", operating_system="macOS", architecture="arm64", fault_domain="az-2")
    node3 = NodeProfile(node_id="n3", hardware_profile="m2", operating_system="macOS", architecture="arm64", fault_domain="az-1")
    
    assert manager.check_spread([node1, node2]) == True
    assert manager.check_spread([node1, node3]) == False
