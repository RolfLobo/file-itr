from datetime import date
from decimal import Decimal
import pytest
from engine import bucket_income_report, BucketResult
from engine.buckets import Bucket
from engine.model import (Taxpayer, AgeBand, Regime, AssetClass, CapitalGainItem, VdaItem)
from engine.scope import OutOfScopeError

TP = Taxpayer(ay=2027, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)


def test_end_to_end_report():
    items = [
        CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1),
                        Decimal("30000"), Decimal("0"), stt_paid=True),
        VdaItem(Decimal("100000"), Decimal("60000")),
    ]
    res = bucket_income_report(TP, items)
    assert isinstance(res, BucketResult)
    assert res.totals[Bucket.STCG_111A] == Decimal("30000")
    assert res.totals[Bucket.VDA_115BBH] == Decimal("40000")
    assert len(res.trace.lines) == 2


def test_report_refuses_out_of_scope():
    bad = [CapitalGainItem(AssetClass.OTHER, date(2024, 1, 1), date(2024, 6, 1),
                           Decimal("1"), Decimal("0"))]
    with pytest.raises(OutOfScopeError):
        bucket_income_report(TP, bad)
