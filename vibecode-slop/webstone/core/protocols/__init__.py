"""Protocol definitions for the cognitive and execution layers.

Protocols enable structural subtyping — any class implementing the required
methods satisfies the protocol without explicit inheritance. This is the
primary mechanism for keeping layers decoupled and testable.
"""

from webstone.core.protocols.agent import AgentProtocol, EvaluatorProtocol, NodeProtocol
from webstone.core.protocols.runtime import (
    CheckpointStoreProtocol,
    EventBusProtocol,
    QueueProtocol,
    SchedulerProtocol,
    WorkerPoolProtocol,
)

__all__ = [
    "AgentProtocol",
    "CheckpointStoreProtocol",
    "EvaluatorProtocol",
    "EventBusProtocol",
    "NodeProtocol",
    "QueueProtocol",
    "SchedulerProtocol",
    "WorkerPoolProtocol",
]
