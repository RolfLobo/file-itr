from datetime import date
from decimal import Decimal
from engine.model import AssetClass, CapitalGainItem, VdaItem
from engine.rules.ay2026_27 import TABLE
from engine.buckets import Bucket, classify, bucket_income

REF = date(2025, 6, 1)


def cg(asset, acq, sale, gain, stt=False):
    return CapitalGainItem(asset, acq, sale, Decimal(gain), Decimal(0), stt_paid=stt)


def test_equity_stt_short_term_is_111a():
    b, key = classify(cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1), 30000, stt=True), TABLE, REF)
    assert b is Bucket.STCG_111A


def test_equity_stt_long_term_is_112a():
    b, _ = classify(cg(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2024, 6, 1), 50000, stt=True), TABLE, REF)
    assert b is Bucket.LTCG_112A


def test_arbitrage_fund_short_holding_still_111a():
    # arbitrage funds are equity-oriented: short holding -> 111A, not slab
    b, _ = classify(cg(AssetClass.EQUITY_MF_STT, date(2024, 1, 1), date(2024, 9, 1), 10000, stt=True), TABLE, REF)
    assert b is Bucket.STCG_111A


def test_debt_50aa_always_slab():
    b, _ = classify(cg(AssetClass.DEBT_MF_50AA, date(2023, 5, 1), date(2027, 1, 1), 40000), TABLE, REF)
    assert b is Bucket.STCG_SLAB


def test_gold_etf_long_term_is_112():
    b, _ = classify(cg(AssetClass.GOLD_ETF_LISTED, date(2025, 1, 1), date(2026, 5, 1), 20000), TABLE, REF)
    assert b is Bucket.LTCG_112


def test_vda_is_115bbh():
    b, _ = classify(VdaItem(Decimal("100000"), Decimal("60000")), TABLE, REF)
    assert b is Bucket.VDA_115BBH


def test_bucket_income_sums_and_partitions():
    items = [
        cg(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1), 30000, stt=True),
        cg(AssetClass.EQUITY_MF_STT, date(2023, 1, 1), date(2024, 6, 1), 50000, stt=True),
        VdaItem(Decimal("100000"), Decimal("60000")),
    ]
    out = bucket_income(items, TABLE, REF)
    assert out[Bucket.STCG_111A] == Decimal("30000")
    assert out[Bucket.LTCG_112A] == Decimal("50000")
    assert out[Bucket.VDA_115BBH] == Decimal("40000")
    # every rupee accounted for exactly once
    assert sum(out.values()) == Decimal("120000")
