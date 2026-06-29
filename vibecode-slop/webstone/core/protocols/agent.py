"""Agent and graph node protocols.

These protocols define the contracts that all cognitive components must satisfy.
They are structural (typing.Protocol) rather than nominal (ABC) so that mock
implementations in tests don't need to inherit from anything.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from webstone.core.state.base import GraphState


@runtime_checkable
class NodeProtocol(Protocol):
    """Contract for a LangGraph node function.

    Every graph node must be an async callable that takes GraphState and
    returns a dict of state updates. Only the fields you update need to be
    included in the return value — LangGraph merges them automatically.

    Example:
        async def my_node(state: GraphState) -> dict[str, Any]:
            return {"plan": "step 1: ..."}
    """

    async def __call__(self, state: GraphState) -> dict[str, Any]:
        """Execute the node and return a partial state update."""
        ...


@runtime_checkable
class AgentProtocol(Protocol):
    """Contract for a reasoning agent.

    Agents encapsulate LLM calls and tool use. They are invoked by graph
    nodes and must not know about the execution runtime.
    """

    @property
    def role(self) -> str:
        """Human-readable role identifier (e.g. 'planner', 'reader')."""
        ...

    async def invoke(self, state: GraphState, **kwargs: Any) -> dict[str, Any]:
        """Run the agent against the current graph state.

        Args:
            state: Current graph state snapshot.
            **kwargs: Optional agent-specific overrides.

        Returns:
            Partial state update dict.
        """
        ...


@runtime_checkable
class EvaluatorProtocol(Protocol):
    """Contract for evaluator/critic agents.

    Evaluators score branches and optionally produce feedback for the planner.
    They must be deterministic given the same inputs to ensure reproducible
    branch pruning decisions.
    """

    async def score(self, state: GraphState) -> list[float]:
        """Score each branch in state.branches.

        Returns:
            List of scores in [0.0, 1.0] aligned with state.branches.
        """
        ...

    async def should_prune(self, score: float) -> bool:
        """Return True if a branch with the given score should be pruned."""
        ...
