from __future__ import annotations
from datetime import date
from engine.model import Taxpayer, CapitalGainItem, AssetClass


class OutOfScopeError(Exception):
    """Raised when the engine cannot faithfully handle an input in this phase."""


# Mirrors rules.ay2026_27 TABLE's "s50aa.acquired_from" value (date(2023, 4, 1)).
# check_scope has no ay_ref_date/table wiring, so this is hardcoded rather than
# read from the rule table; keep in sync with that rule if it ever changes.
_S50AA_ACQUIRED_FROM = date(2023, 4, 1)

_STT_ASSETS = (AssetClass.LISTED_EQUITY_STT, AssetClass.EQUITY_MF_STT)


def check_scope(taxpayer: Taxpayer, items: list) -> None:
    if taxpayer.ay != 2027:
        raise OutOfScopeError(f"Only AY 2026-27 is supported; got AY {taxpayer.ay}")
    if not taxpayer.resident:
        raise OutOfScopeError("Non-resident returns are out of scope in Phase 1")
    for it in items:
        if not isinstance(it, CapitalGainItem):
            continue
        if it.asset is AssetClass.OTHER:
            raise OutOfScopeError(
                "Capital-gain item has unknown asset class OTHER — refusing rather than mis-bucket")
        if it.asset in _STT_ASSETS and not it.stt_paid:
            raise OutOfScopeError(
                "listed equity/equity-MF without STT is not handled in Phase 1 "
                "(would not be 111A/112A)")
        if it.asset is AssetClass.DEBT_MF_50AA and it.acquisition_date < _S50AA_ACQUIRED_FROM:
            raise OutOfScopeError(
                "debt fund acquired before 1-Apr-2023 pre-dates s.50AA — not handled in Phase 1")
