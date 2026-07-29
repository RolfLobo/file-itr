from datetime import date
from decimal import Decimal
import pytest
from engine.model import AgeBand, AssetClass, CapitalGainItem, Regime, Taxpayer
from engine.rules.ay2026_27 import TABLE
from engine.buckets import Bucket
from engine.scope import OutOfScopeError, check_rate_scope
from engine.rates import compute_tax

REF = date(2025, 6, 1)


def tp(regime=Regime.NEW, age=AgeBand.BELOW_60):
    return Taxpayer(ay=2027, resident=True, age_band=age, regime=regime)


def bk(normal=0, slab_st=0, s111a=0, s112=0, s112a=0, vda=0):
    return {
        Bucket.NORMAL: Decimal(normal),
        Bucket.STCG_SLAB: Decimal(slab_st),
        Bucket.STCG_111A: Decimal(s111a),
        Bucket.LTCG_112: Decimal(s112),
        Bucket.LTCG_112A: Decimal(s112a),
        Bucket.VDA_115BBH: Decimal(vda),
    }


# ---------------- new-regime slabs & 87A ----------------

def test_new_regime_10l_fully_rebated():
    r = compute_tax(bk(normal=1000000), tp(), TABLE, REF)
    assert r.slab_tax == Decimal("40000")
    assert r.rebate_87a == Decimal("40000")
    assert r.total_tax == Decimal("0")


def test_new_regime_15l():
    r = compute_tax(bk(normal=1500000), tp(), TABLE, REF)
    assert r.slab_tax == Decimal("105000")
    assert r.rebate_87a == Decimal("0")
    assert r.cess == Decimal("4200")
    assert r.total_tax == Decimal("109200")


def test_new_regime_87a_marginal_relief_just_above_12l():
    r = compute_tax(bk(normal=1210000), tp(), TABLE, REF)
    assert r.slab_tax == Decimal("61500")
    # marginal relief: pay only the excess over 12L
    assert r.slab_tax - r.rebate_87a == Decimal("10000")
    assert r.total_tax == Decimal("10400")  # + 4% cess


def test_slab_stcg_is_taxed_as_normal_income():
    a = compute_tax(bk(normal=1500000), tp(), TABLE, REF)
    b = compute_tax(bk(normal=1400000, slab_st=100000), tp(), TABLE, REF)
    assert a.total_tax == b.total_tax


# ---------------- old-regime slabs & 87A ----------------

def test_old_regime_48l_below60_fully_rebated():
    r = compute_tax(bk(normal=480000), tp(Regime.OLD), TABLE, REF)
    assert r.slab_tax == Decimal("11500")
    assert r.rebate_87a == Decimal("11500")
    assert r.total_tax == Decimal("0")


def test_old_regime_senior_exemption_3l():
    r = compute_tax(bk(normal=400000), tp(Regime.OLD, AgeBand.SENIOR), TABLE, REF)
    assert r.slab_tax == Decimal("5000")
    assert r.total_tax == Decimal("0")


def test_old_regime_super_senior_exemption_5l():
    r = compute_tax(bk(normal=600000), tp(Regime.OLD, AgeBand.SUPER_SENIOR), TABLE, REF)
    # 5L-6L @ 20%
    assert r.slab_tax == Decimal("20000")
    assert r.rebate_87a == Decimal("0")


def test_old_regime_10l():
    r = compute_tax(bk(normal=1000000), tp(Regime.OLD), TABLE, REF)
    # 2.5-5 @5% = 12500; 5-10 @20% = 100000
    assert r.slab_tax == Decimal("112500")
    assert r.total_tax == Decimal("117000")  # + 4% cess


def test_old_regime_special_rate_income_below_5l_refused():
    # 87A x special-rate interplay (s.112A(6) etc.) is contested — fail loud.
    with pytest.raises(OutOfScopeError):
        compute_tax(bk(normal=300000, s111a=100000), tp(Regime.OLD), TABLE, REF)


# ---------------- special rates ----------------

def test_111a_at_20_percent():
    r = compute_tax(bk(normal=2000000, s111a=100000), tp(), TABLE, REF)
    assert r.special_tax[Bucket.STCG_111A] == Decimal("20000")


def test_112a_exemption_then_12_5_percent():
    r = compute_tax(bk(normal=2000000, s112a=200000), tp(), TABLE, REF)
    assert r.special_taxable[Bucket.LTCG_112A] == Decimal("75000")
    assert r.special_tax[Bucket.LTCG_112A] == Decimal("9375")


def test_112a_within_exemption_is_nil():
    r = compute_tax(bk(normal=2000000, s112a=120000), tp(), TABLE, REF)
    assert r.special_tax[Bucket.LTCG_112A] == Decimal("0")


def test_112_at_12_5_percent():
    r = compute_tax(bk(normal=2000000, s112=100000), tp(), TABLE, REF)
    assert r.special_tax[Bucket.LTCG_112] == Decimal("12500")


def test_vda_at_30_percent_flat():
    r = compute_tax(bk(vda=100000), tp(), TABLE, REF)
    assert r.special_tax[Bucket.VDA_115BBH] == Decimal("30000")
    # new-regime 87A never touches special-rate tax
    assert r.rebate_87a == Decimal("0")
    assert r.total_tax == Decimal("31200")


def test_new_regime_rebate_never_touches_special_tax():
    # total income 11L (< 12L): slab part rebated, 111A tax survives
    r = compute_tax(bk(normal=900000, s111a=200000), tp(), TABLE, REF)
    assert r.rebate_87a == r.slab_tax  # slab fully rebated
    assert r.special_tax[Bucket.STCG_111A] == Decimal("40000")
    assert r.total_tax == Decimal("41600")  # 40000 + 4% cess


# ---------------- basic-exemption adjustment (residents) ----------------

def test_unexhausted_basic_exemption_absorbs_special_cg():
    # slab income 1L -> 3L of the 4L new-regime exemption unexhausted
    r = compute_tax(bk(normal=100000, s111a=200000), tp(), TABLE, REF)
    assert r.special_taxable[Bucket.STCG_111A] == Decimal("0")
    assert r.total_tax == Decimal("0")


def test_basic_exemption_adjust_order_highest_rate_first():
    # slab 3L -> 1L unexhausted; 111A 80k absorbed fully, 20k goes to 112
    r = compute_tax(bk(normal=300000, s111a=80000, s112=50000), tp(), TABLE, REF)
    assert r.special_taxable[Bucket.STCG_111A] == Decimal("0")
    assert r.special_taxable[Bucket.LTCG_112] == Decimal("30000")
    assert r.special_tax[Bucket.LTCG_112] == Decimal("3750")
    rule = TABLE.get("engine.basic_exemption_adjust_order", REF)
    assert rule.confidence == "contested"


def test_basic_exemption_never_absorbs_vda():
    r = compute_tax(bk(normal=0, vda=100000), tp(), TABLE, REF)
    assert r.special_tax[Bucket.VDA_115BBH] == Decimal("30000")


# ---------------- surcharge ----------------

def test_no_surcharge_at_or_below_50l():
    r = compute_tax(bk(normal=5000000), tp(), TABLE, REF)
    assert r.surcharge == Decimal("0")


def test_surcharge_10_percent_above_50l():
    r = compute_tax(bk(normal=6000000), tp(), TABLE, REF)
    assert r.slab_tax == Decimal("1380000")
    assert r.surcharge == Decimal("138000")
    assert r.total_tax == Decimal("1578720")


def test_surcharge_marginal_relief_just_above_50l():
    r = compute_tax(bk(normal=5050000), tp(), TABLE, REF)
    # tax at 50L = 1080000; cap = 1080000 + 50000 excess income
    assert r.slab_tax == Decimal("1095000")
    assert r.slab_tax + r.surcharge - r.marginal_relief == Decimal("1130000")
    assert r.total_tax == Decimal("1175200")


def test_surcharge_cg_capped_at_15_percent():
    # ti = 2.6cr -> base rate 25%, but 111A tax surcharged at only 15%
    r = compute_tax(bk(normal=6000000, s111a=20000000), tp(), TABLE, REF)
    assert r.surcharge == Decimal("0.15") * Decimal("4000000") + \
        Decimal("0.25") * Decimal("1380000")


def test_new_regime_surcharge_capped_at_25_percent():
    r = compute_tax(bk(normal=60000000), tp(), TABLE, REF)   # 6cr
    # old regime would be 37% above 5cr; new regime caps at 25%
    assert r.surcharge == Decimal("0.25") * r.slab_tax


def test_old_regime_surcharge_37_percent_above_5cr():
    r = compute_tax(bk(normal=60000000), tp(Regime.OLD), TABLE, REF)
    assert r.surcharge == Decimal("0.37") * r.slab_tax


# ---------------- rounding ----------------

def test_income_rounded_288a():
    # 12,00,004 rounds DOWN to 12,00,000 -> still rebate-eligible
    r = compute_tax(bk(normal=1200004), tp(), TABLE, REF)
    assert r.total_income == Decimal("1200000")
    assert r.total_tax == Decimal("0")


def test_tax_rounded_288b():
    r = compute_tax(bk(normal=1500100), tp(), TABLE, REF)
    # slab tax 105015; cess 4200.60 -> 109215.60 -> 288B rounds to 109220
    assert r.total_tax == Decimal("109220")


# ---------------- rate-layer scope guards ----------------

def test_pre_jul2024_land_ltcg_refused():
    item = CapitalGainItem(AssetClass.LAND_BUILDING, date(2020, 1, 1), date(2025, 6, 1),
                           Decimal("5000000"), Decimal("2000000"))
    with pytest.raises(OutOfScopeError, match="indexation"):
        check_rate_scope(tp(), [item], TABLE, REF)


def test_post_jul2024_land_short_term_ok():
    item = CapitalGainItem(AssetClass.LAND_BUILDING, date(2024, 8, 1), date(2025, 6, 1),
                           Decimal("5000000"), Decimal("2000000"))
    check_rate_scope(tp(), [item], TABLE, REF)  # no raise
