from __future__ import annotations
from engine.model import Taxpayer, CapitalGainItem, AssetClass


class OutOfScopeError(Exception):
    """Raised when the engine cannot faithfully handle an input in this phase."""


def check_scope(taxpayer: Taxpayer, items: list) -> None:
    if taxpayer.ay != 2027:
        raise OutOfScopeError(f"Only AY 2026-27 is supported; got AY {taxpayer.ay}")
    if not taxpayer.resident:
        raise OutOfScopeError("Non-resident returns are out of scope in Phase 1")
    for it in items:
        if isinstance(it, CapitalGainItem) and it.asset is AssetClass.OTHER:
            raise OutOfScopeError(
                "Capital-gain item has unknown asset class OTHER — refusing rather than mis-bucket")
