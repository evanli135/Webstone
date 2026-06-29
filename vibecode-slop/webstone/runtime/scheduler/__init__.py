"""Task scheduler — accepts graph execution jobs and dispatches to workers."""

from webstone.runtime.scheduler.scheduler import InProcessScheduler

__all__ = ["InProcessScheduler"]
