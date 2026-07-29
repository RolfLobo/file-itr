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


def check_rate_scope(taxpayer: Taxpayer, items: list, table, ay_ref_date: date) -> None:
    """Phase 3 rate-layer refusals (rule-table-aware, unlike check_scope)."""
    opt_before = table.get("s112.land_indexation_option_before", ay_ref_date).value
    lt_months = table.get("holding.other.lt_months", ay_ref_date).value
    for it in items:
        if isinstance(it, CapitalGainItem) and it.asset is AssetClass.LAND_BUILDING \
                and it.acquisition_date < opt_before \
                and it.held_more_than_months(lt_months):
            raise OutOfScopeError(
                "land/building acquired before 23-Jul-2024: resident may opt 20%-with-"
                "indexation instead of 12.5% (s.112 proviso); the engine has no CII "
                "tables to evaluate the option — out of scope")


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
