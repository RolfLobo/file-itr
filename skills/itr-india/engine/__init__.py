from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from engine.buckets import Bucket, bucket_income
from engine.trace import Trace, trace_bucketing
from engine.scope import check_scope
from engine.rules.ay2026_27 import TABLE


@dataclass(frozen=True)
class BucketResult:
    totals: dict
    trace: Trace


def bucket_income_report(taxpayer, items, table=TABLE, ay_ref_date: date = date(2025, 6, 1)) -> BucketResult:
    check_scope(taxpayer, items)
    totals = bucket_income(items, table, ay_ref_date)
    trace = trace_bucketing(items, table, ay_ref_date)
    return BucketResult(totals=totals, trace=trace)
