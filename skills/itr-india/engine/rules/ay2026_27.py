from datetime import date
from decimal import Decimal
from engine.rulebase import Rule, RuleTable

_CLEARTAX_STCG = "https://cleartax.in/s/short-term-capital-gain-on-shares"
_QUICKO_HP = "https://learn.quicko.com/capital-gains-holding-period-tax"
_CLEARTAX_50AA = "https://cleartax.in/s/section-50aa-income-tax-act"
_IK_2_42A = "https://indiankanoon.org/search/?formInput=section%202(42A)%20income%20tax"
_IK_115BBH = "https://indiankanoon.org/search/?formInput=section%20115BBH%20income%20tax"
_QUICKO_VDA = "https://learn.quicko.com/income-tax-on-cryptocurrency-nft-vda"

TABLE = RuleTable([
    Rule(key="holding.listed_equity.lt_months", value=12,
         authority="s.2(42A) proviso — listed securities / equity-oriented units",
         source_primary=_IK_2_42A, source_secondary=_CLEARTAX_STCG,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="holding.listed_nonequity.lt_months", value=12,
         authority="s.2(42A) — listed non-equity units, units acquired on/after 1-Apr-2025",
         source_primary=_IK_2_42A, source_secondary=_QUICKO_HP,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Units acquired 23-Jul-2024..31-Mar-2025 carried a 24-month "
                        "transitional threshold; 12-month applies for acquisitions on/after 1-Apr-2025."),
    Rule(key="holding.other.lt_months", value=24,
         authority="s.2(42A) — other capital assets",
         source_primary=_IK_2_42A, source_secondary=_QUICKO_HP,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s50aa.acquired_from", value=date(2023, 4, 1),
         authority="s.50AA — specified mutual fund; units acquired on/after 1-Apr-2023",
         source_primary=_IK_2_42A, source_secondary=_CLEARTAX_50AA,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s50aa.applies", value=True,
         authority="s.50AA — specified MF gains always short-term (slab), any holding",
         source_primary=_IK_2_42A, source_secondary=_CLEARTAX_50AA,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s115bbh.applies", value=Decimal("0.30"),
         authority="s.115BBH — VDA gains taxed at flat 30%, any holding period",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="settled"),
])
