"""
Agent health/system status TUI — template.

Override `SystemDashboard.fetch_status()` and `SystemDashboard.fetch_events()`
to pull real data from your agents/transport service.

Run:  python -m textual run --dev "src/orchestration/observability/system.py:SystemDashboard"
Deps: pip install textual
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import DataTable, Footer, Header, Label, Log, Static


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

class AgentStatus(str, Enum):
    OK       = "ok"
    DEGRADED = "degraded"
    DOWN     = "down"
    UNKNOWN  = "unknown"


@dataclass
class AgentInfo:
    name: str
    role: str
    status: AgentStatus = AgentStatus.UNKNOWN
    latency_ms: int | None = None
    tasks_active: int = 0
    tasks_completed: int = 0
    error_rate: float = 0.0


@dataclass
class EventEntry:
    timestamp: str        # pre-formatted HH:MM:SS
    source: str           # agent_id that originated the event
    kind: str             # "tool" | "action" | "fork" | "error"
    description: str      # human-readable one-liner


@dataclass
class SystemSnapshot:
    agents: list[AgentInfo] = field(default_factory=list)
    transport_healthy: bool = True
    db_healthy: bool = True


from orchestration.mocks.observability import MOCK_EVENTS, MOCK_SNAPSHOT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STATUS_STYLE: dict[AgentStatus, str] = {
    AgentStatus.OK:       "bold green",
    AgentStatus.DEGRADED: "bold yellow",
    AgentStatus.DOWN:     "bold red",
    AgentStatus.UNKNOWN:  "dim",
}

_KIND_PREFIX: dict[str, str] = {
    "tool":   "[blue]TOOL  [/blue]",
    "action": "[cyan]ACTION[/cyan]",
    "fork":   "[magenta]FORK  [/magenta]",
    "error":  "[red]ERROR [/red]",
}

_SERVICE_ICONS = {True: "[green]●[/green] healthy", False: "[red]●[/red] unhealthy"}


def _fmt_latency(ms: int | None) -> str:
    return f"{ms} ms" if ms is not None else "—"


def _fmt_error_rate(rate: float) -> str:
    pct = rate * 100
    if pct == 0:
        return "[green]0%[/green]"
    if pct < 10:
        return f"[yellow]{pct:.1f}%[/yellow]"
    return f"[red]{pct:.1f}%[/red]"


def _fmt_event(entry: EventEntry) -> str:
    prefix = _KIND_PREFIX.get(entry.kind, entry.kind.upper().ljust(6))
    return f"{entry.timestamp}  {prefix}  [dim]{entry.source}[/dim]  {entry.description}"


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

class ServiceBar(Static):
    """Single-line strip showing infrastructure service health."""

    def compose(self) -> ComposeResult:
        yield Label("", id="service-bar-label")

    def update_snapshot(self, snapshot: SystemSnapshot) -> None:
        transport = _SERVICE_ICONS[snapshot.transport_healthy]
        db        = _SERVICE_ICONS[snapshot.db_healthy]
        self.query_one("#service-bar-label", Label).update(
            f"  Transport: {transport}    Postgres: {db}"
        )


class AgentTable(Static):
    """Summary table — one row per known agent."""

    _COLUMNS = ("Agent", "Role", "Status", "Latency", "Active", "Completed", "Err Rate")

    def compose(self) -> ComposeResult:
        yield DataTable(id="agent-table")

    def on_mount(self) -> None:
        self.query_one(DataTable).add_columns(*self._COLUMNS)

    def update_snapshot(self, snapshot: SystemSnapshot) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for agent in snapshot.agents:
            style = _STATUS_STYLE[agent.status]
            table.add_row(
                agent.name,
                agent.role,
                f"[{style}]{agent.status.value}[/{style}]",
                _fmt_latency(agent.latency_ms),
                str(agent.tasks_active),
                str(agent.tasks_completed),
                _fmt_error_rate(agent.error_rate),
            )


class EventLog(Static):
    """Live feed of tool invocations, agent actions, forks, and errors."""

    def compose(self) -> ComposeResult:
        yield Log(id="event-log", auto_scroll=True)

    def update_events(self, events: list[EventEntry]) -> None:
        log = self.query_one(Log)
        log.clear()
        for entry in events:
            log.write(_fmt_event(entry))


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class SystemDashboard(App):
    """Webstone system status dashboard."""

    CSS = """
    Screen {
        layout: vertical;
        padding: 1 2;
    }

    ServiceBar {
        height: 3;
        border: solid $primary-darken-2;
        padding: 0 1;
        margin-bottom: 1;
    }

    AgentTable {
        height: 40%;
        border: solid $primary-darken-2;
        margin-bottom: 1;
    }

    EventLog {
        height: 1fr;
        border: solid $primary-darken-2;
    }
    """

    BINDINGS = [
        ("q", "quit",    "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    _snapshot: reactive[SystemSnapshot] = reactive(SystemSnapshot)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ServiceBar(id="service-bar")
        yield AgentTable(id="agent-table-widget")
        yield EventLog(id="event-log-widget")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh_timer: Timer = self.set_interval(5, self.action_refresh)
        self.action_refresh()

    # ------------------------------------------------------------------
    # Override these to pull real data
    # ------------------------------------------------------------------

    def fetch_status(self) -> SystemSnapshot:
        """Return a fresh SystemSnapshot."""
        return MOCK_SNAPSHOT

    def fetch_events(self) -> list[EventEntry]:
        """Return recent EventEntry records, newest last."""
        return MOCK_EVENTS

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def action_refresh(self) -> None:
        snapshot = self.fetch_status()
        events   = self.fetch_events()
        self.query_one("#service-bar",        ServiceBar).update_snapshot(snapshot)
        self.query_one("#agent-table-widget", AgentTable).update_snapshot(snapshot)
        self.query_one("#event-log-widget",   EventLog).update_events(events)

    def action_quit(self) -> None:
        self.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    SystemDashboard().run()
