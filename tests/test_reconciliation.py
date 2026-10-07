from copy import deepcopy
import unittest

from portfolio import read, reconciliation_demo
from portfolio_lab.reconciliation import key_of, reconcile


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.fixture = read("invoices.json")

    def run_case(self, **changes):
        options = {"erp_through": self.fixture["erp_through"], "fiscal_through": self.fixture["fiscal_through"]}
        options.update(changes)
        return reconcile(self.fixture["fiscal"], self.fixture["erp"], **options)

    def test_all_planted_business_outcomes(self):
        report = reconciliation_demo()
        observed = {row["key"][-1]: row["status"] for row in report["items"]}
        self.assertEqual(observed, self.fixture["expected"])
        self.assertEqual(report["actionable_count"], 16)

    def test_input_order_does_not_change_decisions_or_hashes(self):
        expected = self.run_case()
        self.fixture["fiscal"].reverse()
        self.fixture["erp"].reverse()
        self.assertEqual(self.run_case(), expected)

    def test_incomplete_load_never_creates_financial_queue(self):
        result = self.run_case(complete=False)
        self.assertEqual(result["actionable_count"], 0)
        self.assertFalse(result["snapshot_complete"])

    def test_invalid_amount_pauses_reconciliation(self):
        for field, value in (("amount", "NaN"), ("supplier", None), ("issued_on", "2026-02-30"), ("state", "unknown")):
            with self.subTest(field=field):
                self.fixture = read("invoices.json")
                self.fixture["fiscal"][0][field] = value
                result = self.run_case()
                self.assertEqual(result["actionable_count"], 0)
                self.assertEqual(len(result["rejected"]), 1)

    def test_replayed_source_id_is_not_counted_twice(self):
        self.fixture["fiscal"].append(deepcopy(self.fixture["fiscal"][0]))
        result = self.run_case()
        self.assertFalse(result["snapshot_complete"])
        self.assertEqual(len(result["rejected"]), 1)

    def test_composite_key_separates_companies_and_suppliers(self):
        row = self.fixture["fiscal"][0]
        self.assertNotEqual(key_of(row), key_of(dict(row, company="OTHER")))
        self.assertNotEqual(key_of(row), key_of(dict(row, supplier="OTHER")))
        self.assertEqual(key_of(row), key_of(dict(row, number="000" + row["number"])))

    def test_rounding_tolerance_boundary(self):
        left = deepcopy(self.fixture["fiscal"][0])
        left["amount"] = "100.00"
        right = dict(left, id="E-BOUNDARY", amount="100.01")
        options = {"erp_through": "2026-06-30", "fiscal_through": "2026-06-30"}
        self.assertEqual(reconcile([left], [right], **options)["summary"], {"matched": 1})
        right["amount"] = "100.02"
        self.assertEqual(reconcile([left], [right], **options)["summary"], {"amount_mismatch": 1})

    def test_cutoff_boundary_is_not_a_late_arrival(self):
        left = deepcopy(self.fixture["fiscal"][0])
        left["issued_on"] = "2026-06-29"
        result = reconcile([left], [], erp_through="2026-06-29", fiscal_through="2026-06-30")
        self.assertEqual(result["summary"], {"missing_erp": 1})

    def test_ambiguous_keys_never_auto_match(self):
        result = self.run_case()
        ambiguous = [row for row in result["items"] if row["status"] == "ambiguous"]
        self.assertEqual(len(ambiguous), 4)
        self.assertTrue(all(not row["actionable"] and row["delta"] is None for row in ambiguous))


if __name__ == "__main__":
    unittest.main()
