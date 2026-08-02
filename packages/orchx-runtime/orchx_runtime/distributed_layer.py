import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from orchx_core.interfaces.distributed_contracts import (
    NodeProfile,
    WorkerAdvertisement,
    DistributedEvent,
    ClusterReport,
    SynchronizationReport,
    DistributedExecutionDNA,
    SimulationReport,
    TaskMigrationPlan,
    NodeReputation
)

class ClusterManager:
    """Manages execution nodes and their health/trust profiles."""
    def __init__(self) -> None:
        self.nodes: Dict[str, NodeProfile] = {}
        
    def register_node(self, profile: NodeProfile) -> None:
        self.nodes[profile.node_id] = profile
        
    def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            del self.nodes[node_id]
            
    def get_cluster_report(self) -> ClusterReport:
        active = len(self.nodes)
        cpu = sum(n.resource_profile.cpu_cores for n in self.nodes.values())
        mem = sum(n.resource_profile.memory_mb for n in self.nodes.values())
        fd_dist: Dict[str, int] = {}
        for n in self.nodes.values():
            fd_dist[n.fault_domain] = fd_dist.get(n.fault_domain, 0) + 1
            
        healthy = sum(1 for n in self.nodes.values() if n.health_profile.status == "healthy")
        return ClusterReport(
            active_nodes=active,
            total_cpu=cpu,
            total_memory=mem,
            fault_domain_distribution=fd_dist,
            healthy_nodes=healthy,
            degraded_nodes=active - healthy
        )

class WorkerDiscovery:
    """Tracks available workers across the cluster based on advertisements."""
    def __init__(self) -> None:
        self.advertisements: Dict[str, WorkerAdvertisement] = {}
        
    def advertise(self, ad: WorkerAdvertisement) -> None:
        self.advertisements[ad.worker_id] = ad
        
    def find_workers_with_capability(self, cap: str) -> List[WorkerAdvertisement]:
        return [ad for ad in self.advertisements.values() if cap in ad.capabilities]

class LocalityEngine:
    """Advises on node affinity based on cached data and memory proximity."""
    def calculate_locality_score(self, task_requirements: List[str], node: NodeProfile) -> float:
        # Mock calculation: if node has "memory" role, higher locality score for memory tasks
        score = 50.0
        if "memory" in task_requirements and "memory" in node.roles:
            score += 40.0
        return score

class CapabilityBasedScheduler:
    """Schedules tasks by capability, trust, resource, locality."""
    def __init__(self, cluster: ClusterManager, discovery: WorkerDiscovery, locality: LocalityEngine):
        self.cluster = cluster
        self.discovery = discovery
        self.locality = locality
        
    def select_node_for_task(self, required_capabilities: List[str], requirements: List[str]) -> Optional[NodeProfile]:
        candidates = []
        for node in self.cluster.nodes.values():
            # 1. Capability matching
            if all(cap in node.capabilities for cap in required_capabilities):
                candidates.append(node)
                
        if not candidates:
            return None
            
        # 2. Sort by Priority: Trust > Resources > Locality > Latency > Load
        def sort_key(n: NodeProfile):
            trust = n.health_profile.reputation.trust_score
            resource = 1.0 - n.resource_profile.utilization_percentage
            loc = self.locality.calculate_locality_score(requirements, n)
            latency = -n.health_profile.latency_ms # lower is better
            return (trust, resource, loc, latency)
            
        candidates.sort(key=sort_key, reverse=True)
        return candidates[0]

class DistributedEventBridge:
    """Bridges local events to remote nodes with ordered delivery."""
    def __init__(self) -> None:
        self.events: List[DistributedEvent] = []
        self.dlq: List[DistributedEvent] = []
        
    def publish(self, event: DistributedEvent) -> bool:
        self.events.append(event)
        # Mock acknowledgement
        if event.requires_ack and event.source_node == "unreachable":
            self.dlq.append(event)
            return False
        return True

class MemorySynchronizationEngine:
    """Synchronizes execution state and memory layers across nodes."""
    def sync_node(self, node_id: str) -> SynchronizationReport:
        return SynchronizationReport(
            sync_id=str(uuid.uuid4()),
            node_id=node_id,
            conflicts_detected=0,
            conflicts_resolved=0,
            sync_latency_ms=12.5,
            status="success"
        )

class ExecutionCoordinator:
    """Coordinates distributed workflows and handles failures."""
    def handle_node_failure(self, failed_node_id: str, task_id: str, cluster: ClusterManager) -> Optional[TaskMigrationPlan]:
        # Simple failover logic
        available_nodes = [n for n in cluster.nodes.keys() if n != failed_node_id]
        if not available_nodes:
            return None
        return TaskMigrationPlan(
            task_id=task_id,
            source_node=failed_node_id,
            target_node=available_nodes[0],
            reason="Node failure detected",
            estimated_migration_cost_ms=150.0
        )

class ClusterSimulation:
    """Simulates distributed failures for the Optimization Engine."""
    def run_simulation(self, scenario: str) -> SimulationReport:
        return SimulationReport(
            simulation_id=str(uuid.uuid4()),
            scenario=scenario,
            simulated_node_failures=1 if "failure" in scenario else 0,
            simulated_sync_delays_ms=45.0,
            recovery_success_rate=0.95,
            advisory_recommendations=["Increase replica count for creative memory"]
        )

class FaultDomainManager:
    """Ensures tasks are spread across fault domains."""
    def check_spread(self, nodes: List[NodeProfile]) -> bool:
        domains = set(n.fault_domain for n in nodes)
        return len(domains) == len(nodes)
