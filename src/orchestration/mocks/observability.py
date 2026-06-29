from orchestration.observability.system import AgentInfo, AgentStatus, EventEntry, SystemSnapshot

MOCK_SNAPSHOT = SystemSnapshot(
    agents=[
        AgentInfo("planner-1", "planner", AgentStatus.OK, 42, 2, 18, 0.0),
        AgentInfo("reader-1", "reader", AgentStatus.OK, 17, 5, 91, 0.01),
        AgentInfo("reader-2", "reader", AgentStatus.DEGRADED, 380, 3, 44, 0.12),
        AgentInfo("evaluator-1", "evaluator", AgentStatus.DOWN, None, 0, 6, 1.0),
    ],
    transport_healthy=True,
    db_healthy=False,
)

MOCK_EVENTS: list[EventEntry] = [
    EventEntry(
        "10:00:01",
        "planner-1",
        "tool",
        "fetch_arxiv(query='attention mechanisms', limit=10)",
    ),
    EventEntry(
        "10:00:03",
        "reader-1",
        "tool",
        "search_memory(query='transformer architectures')",
    ),
    EventEntry(
        "10:00:05",
        "reader-2",
        "action",
        "delegate(target=evaluator-1, task='score results')",
    ),
    EventEntry(
        "10:00:07",
        "reader-1",
        "fork",
        "fork() → reader-3 (context: arxiv search thread)",
    ),
    EventEntry(
        "10:00:09",
        "evaluator-1",
        "error",
        "timeout waiting for reader-2 results",
    ),
    EventEntry(
        "10:00:11",
        "reader-3",
        "tool",
        "fetch_semantic_scholar(query='attention mechanisms', limit=5)",
    ),
    EventEntry(
        "10:00:14",
        "planner-1",
        "action",
        "interrupt(target=reader-2, reason='degraded latency')",
    ),
]
