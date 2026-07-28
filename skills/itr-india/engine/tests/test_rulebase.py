from datetime import date
import pytest
from engine.rulebase import Rule, RuleValidationError, validate_rule, RuleTable


def _complete_rule(**over):
    base = dict(
        key="holding.listed_equity.lt_months", value=12,
        authority="s.2(42A); Finance (No.2) Act 2024",
        source_primary="https://indiankanoon.org/doc/? (s.2(42A))",
        source_secondary="https://cleartax.in/s/short-term-capital-gain-on-shares",
        effective_from=date(2025, 4, 1), effective_to=None,
        confidence="settled", contested_note="",
    )
    base.update(over)
    return Rule(**base)


def test_complete_rule_validates():
    validate_rule(_complete_rule())  # no raise


def test_missing_primary_source_fails():
    with pytest.raises(RuleValidationError):
        validate_rule(_complete_rule(source_primary=""))


def test_contested_rule_needs_note():
    with pytest.raises(RuleValidationError):
        validate_rule(_complete_rule(confidence="contested", contested_note=""))


def test_active_on_respects_effective_window():
    r = _complete_rule(effective_from=date(2025, 4, 1), effective_to=date(2026, 3, 31))
    assert r.active_on(date(2025, 6, 1)) is True
    assert r.active_on(date(2026, 4, 1)) is False
    assert r.active_on(date(2025, 3, 31)) is False


def test_ruletable_get_by_date():
    r = _complete_rule()
    table = RuleTable([r])
    assert table.get("holding.listed_equity.lt_months", on=date(2025, 6, 1)) is r
    with pytest.raises(KeyError):
        table.get("nonexistent.key", on=date(2025, 6, 1))
