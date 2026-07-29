from datetime import date
from decimal import Decimal
from engine.model import AssetClass, CapitalGainItem
from engine.rules.ay2026_27 import TABLE
from engine.trace import trace_bucketing

REF = date(2025, 6, 1)


def test_trace_records_rule_key_and_source():
    item = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 11, 1),
                           Decimal("30000"), Decimal("0"), stt_paid=True)
    tr = trace_bucketing([item], TABLE, REF)
    line = tr.lines[0]
    assert line.rule_key == "holding.listed_equity.lt_months"
    assert line.source.startswith("http")
    assert "http" in tr.render()


def test_trace_flags_contested_lines():
    # gold ETF uses the 'contested' listed_nonequity threshold rule
    item = CapitalGainItem(AssetClass.GOLD_ETF_LISTED, date(2025, 1, 1), date(2026, 5, 1),
                           Decimal("20000"), Decimal("0"))
    tr = trace_bucketing([item], TABLE, REF)
    assert len(tr.contested()) == 1
