from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


@dataclass(frozen=True)
class Rule:
    key: str
    value: Any
    authority: str
    source_primary: str
    source_secondary: str
    effective_from: date
    effective_to: Optional[date]
    confidence: str          # "settled" | "contested"
    contested_note: str = ""

    def active_on(self, d: date) -> bool:
        if d < self.effective_from:
            return False
        if self.effective_to is not None and d > self.effective_to:
            return False
        return True


class RuleValidationError(ValueError):
    pass


def validate_rule(r: Rule) -> None:
    for f in ("authority", "source_primary", "source_secondary"):
        if not getattr(r, f):
            raise RuleValidationError(f"Rule {r.key!r} missing required provenance field {f!r}")
    if r.confidence not in ("settled", "contested"):
        raise RuleValidationError(f"Rule {r.key!r} invalid confidence {r.confidence!r}")
    if r.confidence == "contested" and not r.contested_note:
        raise RuleValidationError(f"Contested rule {r.key!r} must carry a contested_note")
    if r.effective_to is not None and r.effective_to < r.effective_from:
        raise RuleValidationError(
            f"Rule {r.key!r} has effective_to ({r.effective_to}) before "
            f"effective_from ({r.effective_from})")


class RuleTable:
    def __init__(self, rules: list[Rule]):
        for r in rules:
            validate_rule(r)
        self._rules = list(rules)

    def get(self, key: str, on: date) -> Rule:
        matches = [r for r in self._rules if r.key == key and r.active_on(on)]
        if not matches:
            raise KeyError(f"No active rule {key!r} on {on.isoformat()}")
        if len(matches) > 1:
            raise KeyError(f"Ambiguous: {len(matches)} active rules {key!r} on {on.isoformat()}")
        return matches[0]

    def all(self) -> list[Rule]:
        return list(self._rules)
