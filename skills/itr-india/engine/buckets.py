from __future__ import annotations
from collections import defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum
from engine.model import CapitalGainItem, VdaItem, AssetClass
from engine.rulebase import RuleTable


class Bucket(Enum):
    NORMAL = "normal"
    STCG_111A = "stcg_111a"
    STCG_SLAB = "stcg_slab"
    LTCG_112A = "ltcg_112a"
    LTCG_112 = "ltcg_112"
    VDA_115BBH = "vda_115bbh"


def classify(item, table: RuleTable, ay_ref_date: date) -> tuple[Bucket, str]:
    if isinstance(item, VdaItem):
        return Bucket.VDA_115BBH, "s115bbh.applies"

    if isinstance(item, CapitalGainItem):
        a = item.asset
        if a is AssetClass.DEBT_MF_50AA:
            rule = table.get("s50aa.acquired_from", ay_ref_date)
            if item.acquisition_date >= rule.value:
                return Bucket.STCG_SLAB, rule.key
            raise ValueError("Debt MF acquired before 1-Apr-2023 pre-dates s.50AA — out of Phase 1 scope")
        if a in (AssetClass.LISTED_EQUITY_STT, AssetClass.EQUITY_MF_STT) and item.stt_paid:
            r = table.get("holding.listed_equity.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112A, r.key) if lt else (Bucket.STCG_111A, r.key)
        if a is AssetClass.GOLD_ETF_LISTED:
            r = table.get("holding.listed_nonequity.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112, r.key) if lt else (Bucket.STCG_SLAB, r.key)
        if a in (AssetClass.LAND_BUILDING, AssetClass.UNLISTED_SHARES):
            r = table.get("holding.other.lt_months", ay_ref_date)
            lt = item.held_more_than_months(r.value)
            return (Bucket.LTCG_112, r.key) if lt else (Bucket.STCG_SLAB, r.key)

    raise ValueError(
        f"internal invariant violated: unclassifiable item {item!r} reached classify; "
        "check_scope should have refused it")


def bucket_income(items: list, table: RuleTable, ay_ref_date: date) -> dict[Bucket, Decimal]:
    out: dict[Bucket, Decimal] = defaultdict(lambda: Decimal("0"))
    for it in items:
        bucket, _ = classify(it, table, ay_ref_date)
        out[bucket] += it.gain
    return dict(out)
