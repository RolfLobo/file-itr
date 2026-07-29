from datetime import date
from decimal import Decimal
import pytest
from engine.model import Taxpayer, AgeBand, Regime, AssetClass, CapitalGainItem
from engine.scope import check_scope, OutOfScopeError


def _tp(**o):
    base = dict(ay=2027, resident=True, age_band=AgeBand.BELOW_60, regime=Regime.NEW)
    base.update(o)
    return Taxpayer(**base)


def test_unknown_asset_class_refused():
    item = CapitalGainItem(AssetClass.OTHER, date(2024, 1, 1), date(2024, 6, 1),
                           Decimal("100"), Decimal("0"))
    with pytest.raises(OutOfScopeError, match="unknown|OTHER"):
        check_scope(_tp(), [item])


def test_unsupported_ay_refused():
    with pytest.raises(OutOfScopeError, match="AY"):
        check_scope(_tp(ay=2026), [])


def test_non_resident_refused():
    with pytest.raises(OutOfScopeError, match="resident"):
        check_scope(_tp(resident=False), [])


def test_in_scope_passes():
    item = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 6, 1),
                           Decimal("100"), Decimal("0"), stt_paid=True)
    check_scope(_tp(), [item])   # no raise


def test_stt_asset_without_stt_paid_refused():
    item = CapitalGainItem(AssetClass.LISTED_EQUITY_STT, date(2024, 1, 1), date(2024, 6, 1),
                           Decimal("100"), Decimal("0"), stt_paid=False)
    with pytest.raises(OutOfScopeError, match="STT"):
        check_scope(_tp(), [item])


def test_debt_50aa_pre_2023_04_01_refused():
    item = CapitalGainItem(AssetClass.DEBT_MF_50AA, date(2022, 5, 1), date(2024, 1, 1),
                           Decimal("100"), Decimal("0"))
    with pytest.raises(OutOfScopeError, match="50AA"):
        check_scope(_tp(), [item])
