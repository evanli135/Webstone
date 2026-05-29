"""Execution runtime layer.

This layer knows how to schedule, parallelize, retry, and persist work.
It has NO knowledge of agent reasoning — it only manages execution mechanics.

The Go runtime integration will replace the internals of this layer while
keeping the Protocol interfaces in `webstone.core.protocols.runtime` stable.
"""
