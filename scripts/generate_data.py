"""Build entirely fictional fixtures. No external input, network or private sources."""

from pathlib import Path
import json
import random


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "synthetic"


def write(name, value):
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_invoices():
    rng = random.Random(7421)
    fiscal, erp, expected = [], [], {}
    scenarios = ("matched", "amount_mismatch", "missing_erp", "awaiting_erp", "cancelled",
                 "ambiguous", "state_conflict", "missing_fiscal", "awaiting_fiscal")
    for scenario_index, scenario in enumerate(scenarios):
        for variant in range(4):
            index = scenario_index * 4 + variant + 1
            amount = f"{rng.randrange(200, 3200)}.{rng.randrange(100):02d}"
            base = {"company": f"ORG-{variant % 2 + 1:02d}", "supplier": f"SUP-{variant + 1:03d}",
                    "series": "A", "number": str(1000 + index), "amount": amount,
                    "issued_on": "2026-06-28", "state": "active"}
            left, right = dict(base, id=f"F-{index:03d}"), dict(base, id=f"E-{index:03d}")
            right["number"] = "00" + right["number"]  # Equivalent key, different formatting.
            if scenario == "amount_mismatch":
                cents = int(amount.replace(".", "")) + 7500
                right["amount"] = f"{cents // 100}.{cents % 100:02d}"
            if scenario == "awaiting_erp":
                left["issued_on"] = "2026-06-30"
            if scenario == "awaiting_fiscal":
                right["issued_on"] = "2026-07-01"
            if scenario == "cancelled":
                left["state"] = right["state"] = "cancelled"
            if scenario == "state_conflict":
                left["state"] = "cancelled"
            if scenario not in {"missing_fiscal", "awaiting_fiscal"}:
                fiscal.append(left)
            if scenario not in {"missing_erp", "awaiting_erp"}:
                erp.append(right)
            if scenario == "ambiguous":
                erp.append(dict(right, id=f"E-{index:03d}-duplicate"))
            expected[base["number"]] = scenario
    return {"synthetic": True, "seed": 7421, "fiscal_through": "2026-06-30", "erp_through": "2026-06-29",
            "fiscal": fiscal, "erp": erp, "expected": expected}


def make_expenses():
    rng = random.Random(1937)
    return {"synthetic": True, "seed": 1937, "currency": "BRL", "rows": [
        {"unit": unit, "month": f"2026-{month:02d}", "category": category,
         "budget_cents": rng.randrange(800000, 2200000), "actual_cents": rng.randrange(750000, 2300000)}
        for unit in ("Norte", "Sul", "Centro") for month in range(1, 13)
        for category in ("Operação", "Suprimentos", "Serviços")
    ]}


def make_documents():
    all_roles = ["operations", "finance", "legal"]
    specs = [
        ("DOC-001", "Compra e cotação", "Compra acima de R$ 8.000 exige três propostas de cotação. O responsável registra a justificativa de escolha do fornecedor antes da aprovação.", all_roles),
        ("DOC-002", "Prazo de reembolso", "O prazo de reembolso é de dez dias após a despesa. A solicitação deve conter comprovante e aprovação do gestor.", all_roles),
        ("DOC-003", "Vencimento de contrato", "O vencimento de contrato é revisado pelo Jurídico com antecedência de 45 dias. A renovação depende de decisão registrada pelo responsável.", ["legal"]),
        ("DOC-004", "Fechamento mensal", "O fechamento mensal ocorre no quinto dia útil. Finanças verifica divergências e registra exceções antes de liberar o relatório.", ["finance"]),
        ("DOC-005", "Incidente operacional", "Um incidente operacional deve ser registrado com horário, impacto e responsável. A liderança define contenção e acompanha a recuperação.", all_roles),
        ("DOC-006", "Política de backup", "O backup é realizado diariamente. A equipe faz teste de restauração mensal e registra as evidências do procedimento.", all_roles),
        ("DOC-007", "Solicitação de acesso", "A solicitação de acesso precisa indicar área, unidade e finalidade. O gestor aprova o menor conjunto de permissões necessário.", all_roles),
        ("DOC-008", "Cadastro de fornecedor", "O cadastro de fornecedor exige validação documental e aprovação de Finanças. Alterações ficam registradas com data e motivo.", ["finance"]),
    ]
    docs = [{"id": ident, "version": 1, "title": title, "body": body, "roles": roles,
             "valid_from": "2026-01-01", "valid_until": None} for ident, title, body, roles in specs]
    docs[1]["version"] = 2
    docs[1]["valid_from"] = "2026-04-01"
    docs.append({"id": "DOC-002", "version": 1, "title": "Prazo de reembolso", "body": "O prazo de reembolso é de cinco dias após a despesa. A solicitação deve conter comprovante.",
                 "roles": all_roles, "valid_from": "2026-01-01", "valid_until": "2026-04-01"})
    questions = [
        ("E01", "compra cotação", "operations", "DOC-001"),
        ("E02", "prazo de reembolso", "operations", "DOC-002"),
        ("E03", "vencimento de contrato", "legal", "DOC-003"),
        ("E04", "fechamento mensal", "finance", "DOC-004"),
        ("E05", "incidente operacional", "operations", "DOC-005"),
        ("E06", "política de backup", "operations", "DOC-006"),
        ("E07", "solicitação de acesso", "operations", "DOC-007"),
        ("E08", "cadastro de fornecedor", "finance", "DOC-008"),
        ("E09", "vencimento de contrato", "operations", None),
        ("E10", "salário do presidente", "finance", None),
        ("E11", "fechamento mensal", "operations", None),
        ("E12", "reembolso para turismo lunar", "operations", None),
    ]
    return {"synthetic": True, "documents": docs}, {"synthetic": True, "cases": [
        {"id": ident, "question": question, "role": role, "expected_document": expected}
        for ident, question, role, expected in questions
    ]}


def main():
    write("invoices.json", make_invoices())
    write("expenses.json", make_expenses())
    documents, questions = make_documents()
    write("documents.json", documents)
    write("evaluation.json", questions)
    write("manifest.json", {"synthetic": True, "organization": "Instituto Horizonte (fictício)",
                            "provenance": "Generated from authored scenarios and fixed random seeds; no source records or production code.",
                            "contains_personal_data": False, "generator": "scripts/generate_data.py", "version": "1.0"})
    print("Synthetic fixtures regenerated: 36 document keys, 108 expense rows, 9 document versions, 12 evaluation cases.")


if __name__ == "__main__":
    main()
