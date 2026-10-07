"""Natural-language entry point to a small, approved semantic catalog.

No LLM generates SQL here. Planning is intentionally bounded and reproducible.
"""

from dataclasses import dataclass
import hashlib
import re
import sqlite3
import unicodedata


def normalize(text):
    return " ".join("".join(c for c in unicodedata.normalize("NFD", text.lower())
                            if unicodedata.category(c) != "Mn").split())


@dataclass(frozen=True)
class Principal:
    name: str
    units: tuple[str, ...]


PRINCIPALS = {
    "manager_north": Principal("manager_north", ("Norte",)),
    "manager_south": Principal("manager_south", ("Sul",)),
    "controller": Principal("controller", ("Norte", "Sul", "Centro")),
}

CATALOG = {
    "budget_variance": {
        "questions": ("orcado versus realizado", "orcado x realizado", "budget versus actual"),
        "sql": "SELECT unit, SUM(budget_cents) AS budget_cents, SUM(actual_cents) AS actual_cents, "
               "SUM(actual_cents - budget_cents) AS variance_cents FROM expenses "
               "WHERE month = ? GROUP BY unit ORDER BY unit",
        "meaning": "Positive variance means actual spend exceeds budget; it is not a forecast.",
    },
    "spend_by_category": {
        "questions": ("despesas por categoria", "gastos por categoria", "spend by category"),
        "sql": "SELECT category, SUM(actual_cents) AS actual_cents FROM expenses "
               "WHERE month = ? GROUP BY category ORDER BY actual_cents DESC, category",
        "meaning": "Actual spend by category within the identity's permitted units.",
    },
    "monthly_spend": {
        "questions": ("evolucao mensal das despesas", "despesas por mes", "monthly spend"),
        "sql": "SELECT month, SUM(actual_cents) AS actual_cents FROM expenses "
               "WHERE month BETWEEN ? AND ? GROUP BY month ORDER BY month",
        "meaning": "Monthly actual spend for the selected year; no interpolation.",
    },
}


class QueryRejected(ValueError):
    """The request cannot be represented by an approved query contract."""


def plan(question, period):
    question = normalize(question)
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
        raise QueryRejected("Period must be YYYY-MM.")
    matches = [key for key, item in CATALOG.items() if question in item["questions"]]
    if len(matches) != 1:
        raise QueryRejected("Unsupported question. Choose one of the documented catalog questions.")
    intent = matches[0]
    params = (period[:4] + "-01", period[:4] + "-12") if intent == "monthly_spend" else (period,)
    return intent, CATALOG[intent]["sql"], params


def scoped_connection(rows, principal):
    # Only authorized records cross the database boundary in this local demo.
    # Production must derive principal from verified identity and enforce database RLS.
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE expenses (unit TEXT, category TEXT, month TEXT, budget_cents INTEGER, actual_cents INTEGER)")
    allowed = []
    for row in rows:
        if row["unit"] not in principal.units:
            continue
        if any(type(row[field]) is not int or row[field] < 0 for field in ("budget_cents", "actual_cents")):
            conn.close()
            raise ValueError("Financial values must be non-negative integer cents")
        allowed.append(tuple(row[k] for k in ("unit", "category", "month", "budget_cents", "actual_cents")))
    conn.executemany("INSERT INTO expenses VALUES (?, ?, ?, ?, ?)", allowed)
    conn.commit()
    conn.execute("PRAGMA query_only = ON")

    def authorize(action, arg1, arg2, database, trigger):
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ and arg1 == "expenses":
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION and arg2 in {"sum"}:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    conn.set_authorizer(authorize)
    return conn


def ask(rows, *, identity, question, period="2026-06"):
    if identity not in PRINCIPALS:
        raise QueryRejected("Unknown demo identity; access denied.")
    principal = PRINCIPALS[identity]
    intent, sql, params = plan(question, period)
    conn = scoped_connection(rows, principal)
    try:
        result = [dict(row) for row in conn.execute(sql, params).fetchmany(101)]
    finally:
        conn.close()
    if len(result) > 100:
        raise QueryRejected("Result limit exceeded.")
    return {
        "synthetic": True, "planner": "approved_templates_v1", "identity": identity,
        "units": list(principal.units), "intent": intent, "sql": sql,
        "parameters": list(params), "rows": result,
        "meaning": CATALOG[intent]["meaning"],
        "query_hash": hashlib.sha256((sql + repr(params)).encode()).hexdigest(),
        "empty": not result,
    }
