from datetime import date
from decimal import Decimal
from engine.rulebase import Rule, RuleTable

_CLEARTAX_STCG = "https://cleartax.in/s/short-term-capital-gain-on-shares"
_QUICKO_HP = "https://learn.quicko.com/capital-gains-holding-period-tax"
_CLEARTAX_50AA = "https://cleartax.in/s/section-50aa-income-tax-act"
# Deep links verified by WebFetch (2026-07-29): each page was fetched and its
# operative statutory text confirmed to state the value(s) this rule encodes.
# "Section 2 in The Income Tax Act, 1961" — contains clause (42A). CAVEAT: this
# mirror pre-dates Finance (No.2) Act 2024 (base definition still reads "36
# months"; the 2014 date-conditional proviso is unchanged). It DOES corroborate
# holding.listed_equity.lt_months=12 (first proviso: units of an equity-oriented
# fund / UTI / zero-coupon bond / other listed non-unit securities -> 12 months)
# and holding.other.lt_months=24 (third proviso: unlisted shares / immovable
# property -> 24 months). It does NOT corroborate holding.listed_nonequity's
# 12-month value or its acquisition-date condition — that reclassification of
# listed non-equity units (e.g. gold ETFs) is a Finance (No.2) Act 2024 change
# not present on this page. Left as the least-bad available deep primary
# because it is still on-point for two of the three holding.* rules and is not
# a search URL; the listed_nonequity gap is called out in the report for the
# controller to adjudicate (a fresher primary should be sourced later).
_IK_2_42A = "https://indiankanoon.org/doc/545792/"
# "Section 24 in The Finance Act, 2023" — the enacting provision that inserts
# s.50AA into the Income-tax Act; contains "Specified Mutual Fund" and the
# "1st day of April, 2023" effective-date language, which corroborates
# s50aa.acquired_from directly. CAVEAT: the fetched text truncated before the
# deeming-as-short-term-capital-gains language, so s50aa.applies ("always
# short-term, any holding") is corroborated by inference from "Notwithstanding
# anything contained in clause (42A) of section 2 or section 48" (an explicit
# override of the normal holding-period test), not by directly-read deeming
# text. Also note (not a value/citation defect, flagged for the record): this
# section's own commencement clause reads "with effect from the 1st day of
# April, 2024" — standard Finance Act drafting for "applicable from AY
# 2024-25" (PY 2023-24, beginning 1-Apr-2023), consistent with this rule's
# effective_from=2023-04-01, but worth a second look if this rule is revisited.
_IK_50AA = "https://indiankanoon.org/doc/71017618/"
# "Section 115BBH in The Income Tax Act, 1961" — contains "virtual digital
# asset" and "thirty per cent".
_IK_115BBH = "https://indiankanoon.org/doc/4837707/"
_QUICKO_VDA = "https://learn.quicko.com/income-tax-on-cryptocurrency-nft-vda"
# Set-off & carry-forward deep links, verified by WebFetch (2026-07-29):
# "Section 70 in The Income Tax Act, 1961" — sub-s (2): STCL "set off against
# the income … in respect of any other capital asset"; sub-s (3): LTCL against
# "any other capital asset not being a short-term capital asset".
_IK_70 = "https://indiankanoon.org/doc/1628473/"
# "Section 71 in The Income Tax Act, 1961" — sub-s (3): CG loss "shall not be
# entitled to have such loss set off against income under the other head".
_IK_71 = "https://indiankanoon.org/doc/178812545/"
# "Section 74 in The Income Tax Act, 1961" — (1)(a) c/f STCL against "any other
# capital asset"; (1)(b) c/f LTCL against "any other capital asset not being a
# short-term capital asset"; (2) "not … more than eight assessment years
# immediately succeeding the assessment year for which the loss was first
# computed".
_IK_74 = "https://indiankanoon.org/doc/1129438/"
# "Section 80 in The Income Tax Act, 1961" — "no loss which has not been
# determined in pursuance of a return filed [u/s 139(3)] shall be carried
# forward and set off under … sub-section (1) or sub-section (3) of section 74".
_IK_80 = "https://indiankanoon.org/doc/1502697/"
# s.115BBH(2)(b) on the same _IK_115BBH page: "no set off of loss from transfer
# of the virtual digital asset … against income computed under any provision of
# this Act … and such loss shall not be allowed to be carried forward".
_CLEARTAX_SETOFF = "https://cleartax.in/s/set-off-carry-forward-capital-losses"

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
         source_primary=_IK_50AA, source_secondary=_CLEARTAX_50AA,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s50aa.applies", value=True,
         authority="s.50AA — specified MF gains always short-term (slab), any holding",
         source_primary=_IK_50AA, source_secondary=_CLEARTAX_50AA,
         effective_from=date(2023, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s115bbh.applies", value=Decimal("0.30"),
         authority="s.115BBH — VDA gains taxed at flat 30%, any holding period",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="settled"),
    # --- Phase 2: set-off & carry-forward ---
    Rule(key="s70.stcl_setoff_any_cg", value=True,
         authority="s.70(2) — current-year STCL sets off against ST and LT capital gains",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s70.ltcl_setoff_ltcg_only", value=True,
         authority="s.70(3) — current-year LTCL sets off against LTCG only",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s71.capital_loss_no_interhead", value=True,
         authority="s.71(3) — capital loss never sets off against any other head",
         source_primary=_IK_71, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_stcl_setoff_any_cg", value=True,
         authority="s.74(1)(a) — b/f STCL sets off against ST and LT capital gains",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_ltcl_setoff_ltcg_only", value=True,
         authority="s.74(1)(b) — b/f LTCL sets off against LTCG only",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s74.cf_years", value=8,
         authority="s.74(2) — capital losses carried forward max 8 AYs after the loss AY",
         source_primary=_IK_74, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2000, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s80.timely_return_required", value=True,
         authority="s.80 r/w s.139(3) — loss not determined in a timely loss-year return "
                   "cannot be carried forward under s.74",
         source_primary=_IK_80, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="settled"),
    Rule(key="s115bbh.loss_setoff_disallowed", value=True,
         authority="s.115BBH(2)(b) — VDA loss: no set-off against any income, no carry-forward",
         source_primary=_IK_115BBH, source_secondary=_QUICKO_VDA,
         effective_from=date(2022, 4, 1), effective_to=None, confidence="contested",
         contested_note="Applied per item: loss on one VDA is not netted against gain on "
                        "another (enacted 'any provision of this Act' wording + the "
                        "government's Mar-2022 clarification dropping 'other'; early "
                        "practitioner debate existed on intra-VDA netting)."),
    Rule(key="engine.cg_setoff_order", value=("stcg_slab", "stcg_111a", "ltcg_112", "ltcg_112a"),
         authority="engine policy — statute prescribes no absorption order across buckets",
         source_primary=_IK_70, source_secondary=_CLEARTAX_SETOFF,
         effective_from=date(2025, 4, 1), effective_to=None, confidence="contested",
         contested_note="Ordering changes per-bucket totals that Phase 3 taxes at different "
                        "rates. Policy: within each term, slab buckets before concession "
                        "buckets; LTCL (restricted, s.70(3)) gets first claim on LTCG before "
                        "STCL spillover. Revisit against the ITD utility in Phase 3+."),
])
