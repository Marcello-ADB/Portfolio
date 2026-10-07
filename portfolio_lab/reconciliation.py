"""Reconcile two snapshots without treating missing evidence as a financial loss."""

from collections import Counter, defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re


def money(value):
    """Reject ambiguous money instead of silently rounding or accepting floats."""
    if not isinstance(value, str) or not re.fullmatch(r"\d+\.\d{2}", value):
        raise ValueError("amount must be a non-negative decimal string with two places")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid amount") from exc


def key_of(row):
    # Company + supplier + series + number: document number alone is not unique.
    if not isinstance(row, dict):
        raise ValueError("document must be an object")
    raw_fields = [row.get(field) for field in ("company", "supplier", "series", "number")]
    if any(not isinstance(value, str) for value in raw_fields):
        raise ValueError("business key fields must be strings")
    fields = [value.strip().upper() for value in raw_fields]
    if any(not value for value in fields):
        raise ValueError("incomplete business key")
    if not fields[-1].isdigit():
        raise ValueError("document number must contain only digits")
    fields[-1] = str(int(fields[-1]))
    return tuple(fields)


def validate_row(row):
    key_of(row)
    money(row["amount"])
    date.fromisoformat(row["issued_on"])
    if row["state"] not in {"active", "cancelled"}:
        raise ValueError("unknown document state")
    if not isinstance(row.get("id"), str) or not row["id"]:
        raise ValueError("missing source record id")


def fingerprint(rows):
    canonical = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True))
    return hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()


def reconcile(fiscal, erp, *, erp_through, fiscal_through, complete=True):
    """Return a review queue; never write back to either source."""
    erp_cutoff = date.fromisoformat(erp_through)
    fiscal_cutoff = date.fromisoformat(fiscal_through)
    if type(complete) is not bool:
        raise ValueError("complete must be boolean")
    groups = {"fiscal": defaultdict(list), "erp": defaultdict(list)}
    invalid = []
    for source, rows in (("fiscal", fiscal), ("erp", erp)):
        seen_ids = set()
        for index, row in enumerate(rows):
            try:
                validate_row(row)
                if row["id"] in seen_ids:
                    raise ValueError("repeated source record id")
                seen_ids.add(row["id"])
            except (ValueError, KeyError, TypeError) as exc:
                invalid.append({"source": source, "position": index, "reason": str(exc)})
                continue
            groups[source][key_of(row)].append(row)

    results = []
    # Any rejected input invalidates completeness: absence cannot become an action.
    reliable = complete and not invalid
    for key in sorted(set(groups["fiscal"]) | set(groups["erp"])):
        left, right = groups["fiscal"].get(key, []), groups["erp"].get(key, [])
        delta = None
        if len(left) > 1 or len(right) > 1:
            status, reason = "ambiguous", "Business key is not one-to-one; resolve source duplicates."
        elif not reliable:
            status, reason = "incomplete_snapshot", "Snapshot is incomplete; reconciliation is paused."
        elif left and right and left[0]["state"] != right[0]["state"]:
            status, reason = "state_conflict", "Cancellation state differs between sources."
        elif all(row["state"] == "cancelled" for row in left + right):
            status, reason = "cancelled", "Cancelled document; exclude from the active queue."
        elif not left:
            if date.fromisoformat(right[0]["issued_on"]) > fiscal_cutoff:
                status, reason = "awaiting_fiscal", "Document is newer than the fiscal snapshot."
            else:
                status, reason = "missing_fiscal", "Investigate absence from the complete fiscal snapshot."
        elif not right:
            if date.fromisoformat(left[0]["issued_on"]) > erp_cutoff:
                status, reason = "awaiting_erp", "Document is newer than the ERP snapshot."
            else:
                status, reason = "missing_erp", "Investigate absence from the complete ERP snapshot."
        else:
            delta = money(right[0]["amount"]) - money(left[0]["amount"])
            status = "matched" if abs(delta) <= Decimal("0.01") else "amount_mismatch"
            reason = "Within the configured one-cent tolerance." if status == "matched" else "Amounts disagree; review source evidence."
        actionable = status in {"missing_fiscal", "missing_erp", "amount_mismatch", "state_conflict"}
        results.append({
            "key": list(key), "status": status, "reason": reason,
            "fiscal_ids": sorted(row["id"] for row in left),
            "erp_ids": sorted(row["id"] for row in right),
            "delta": str(delta) if delta is not None else None,
            "owner": "finance_review" if actionable else "data_quality" if status == "ambiguous" else None,
            "actionable": actionable,
        })
    return {
        "synthetic": True, "rule_version": "1.0", "snapshot_complete": reliable,
        "cutoffs": {"fiscal": fiscal_through, "erp": erp_through},
        "source_hashes": {"fiscal": fingerprint(fiscal), "erp": fingerprint(erp)},
        "summary": dict(sorted(Counter(row["status"] for row in results).items())),
        "actionable_count": sum(row["actionable"] for row in results),
        "rejected": invalid, "items": results,
        "interpretation": "Exceptions are review candidates, not losses or savings.",
    }
