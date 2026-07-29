from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from engine.buckets import Bucket, classify
from engine.rulebase import RuleTable


@dataclass(frozen=True)
class TraceLine:
    label: str
    amount: Decimal
    bucket: Bucket
    rule_key: str
    source: str
    contested: bool


@dataclass
class Trace:
    lines: list = field(default_factory=list)

    def add(self, line: TraceLine) -> None:
        self.lines.append(line)

    def contested(self) -> list:
        return [ln for ln in self.lines if ln.contested]

    def render(self) -> str:
        rows = []
        for ln in self.lines:
            flag = "  [CONTESTED]" if ln.contested else ""
            rows.append(f"{ln.label:<28} {ln.bucket.value:<12} {ln.amount:>14} "
                        f"<- {ln.rule_key} ({ln.source}){flag}")
        return "\n".join(rows)


def trace_bucketing(items: list, table: RuleTable, ay_ref_date: date) -> Trace:
    tr = Trace()
    for i, it in enumerate(items):
        bucket, rule_key = classify(it, table, ay_ref_date)
        rule = table.get(rule_key, ay_ref_date)   # every classify rule_key MUST exist; raises if not
        source = rule.source_primary
        contested = rule.confidence == "contested"
        label = f"item[{i}] {type(it).__name__}"
        tr.add(TraceLine(label, it.gain, bucket, rule_key, source, contested))
    return tr
