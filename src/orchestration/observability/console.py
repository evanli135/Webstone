from orchestration.observability.base import (
    AgentActionEvent,
    AgentEvent,
    BaseTelemetry,
    ErrorEvent,
    FetchEvent,
    ToolEvent,
)


class ConsoleTelemetry(BaseTelemetry):
    """Logs telemetry to stdout. Default backend for development."""

    def record_fetch(self, event: FetchEvent) -> None:
        status = "OK" if event.success else "FAIL"
        print(
            f"[{status}] {event.source} | {event.query!r} | "
            f"{event.result_count} results | {event.duration_ms:.0f}ms"
        )

    def record_agent(self, event: AgentEvent) -> None:
        status = "OK" if event.success else "FAIL"
        print(f"[AGENT:{status}] {event.agent_id} → {event.action} | {event.duration_ms:.0f}ms")

    def record_error(self, event: ErrorEvent) -> None:
        print(f"[ERROR] {event.agent_id}: {event.error}")

    def record_tool(self, event: ToolEvent) -> None:
        status = "OK" if event.success else "FAIL"
        print(
            f"[TOOL:{status}] {event.agent_id} → "
            f"{event.tool}({event.args}) | {event.duration_ms:.0f}ms"
        )

    def record_agent_action(self, event: AgentActionEvent) -> None:
        result = f" → {event.result}" if event.result else ""
        print(f"[ACTION] {event.source_agent_id} → {event.action}({event.target_agent_id}){result}")
