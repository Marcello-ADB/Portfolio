"""One entry point for the three offline portfolio demonstrations."""

import argparse
import json
from pathlib import Path

from portfolio_lab.analytics import QueryRejected, ask
from portfolio_lab.evidence import answer, evaluate
from portfolio_lab.reconciliation import reconcile


ROOT = Path(__file__).resolve().parent


def read(name):
    return json.loads((ROOT / "data" / "synthetic" / name).read_text(encoding="utf-8"))


def reconciliation_demo():
    fixture = read("invoices.json")
    return reconcile(fixture["fiscal"], fixture["erp"], erp_through=fixture["erp_through"], fiscal_through=fixture["fiscal_through"])


def all_demos():
    reconciliation = reconciliation_demo()
    analytics = ask(read("expenses.json")["rows"], identity="manager_north", question="orçado versus realizado")
    evidence = answer(read("documents.json")["documents"], "prazo de reembolso")
    evaluation = evaluate(read("documents.json")["documents"], read("evaluation.json")["cases"])
    return {"reconciliation": reconciliation, "analytics": analytics, "evidence": evidence, "evaluation": evaluation}


def write_report(results):
    directory = ROOT / "reports"
    directory.mkdir(exist_ok=True)
    for name, result in results.items():
        (directory / f"{name}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    reconciliation, analytics, evidence, evaluation = (results[key] for key in ("reconciliation", "analytics", "evidence", "evaluation"))
    lines = ["# Evidência reproduzível", "", "> Todos os dados e valores abaixo são sintéticos. Não representam resultados institucionais.", "",
             "Gerado por `python portfolio.py demo --write-report`. Execução local, sem rede, sem credenciais e sem LLM.", "",
             "## 01 / Conciliação", "", "| Estado | Documentos |", "|---|---:|"]
    lines += [f"| `{status}` | {count} |" for status, count in reconciliation["summary"].items()]
    lines += ["", f"**{reconciliation['actionable_count']} exceções para revisão**; o sistema não classifica essas exceções como perdas.", "",
              "Cutoffs: ERP até 2026-06-29; fiscal até 2026-06-30. Hashes de entrada e evidência por documento no [JSON](reconciliation.json).", "",
              "## 02 / Consulta governada", "", f"Identidade de demonstração: `{analytics['identity']}`. Unidade autorizada: **Norte**.", "",
              "```sql", analytics["sql"], "```", "", "Parâmetro: `2026-06`. Valores em centavos inteiros.", "",
              "```json", json.dumps(analytics["rows"], ensure_ascii=False, indent=2), "```", "",
              "## 03 / Evidência documental", "", "Pergunta: **prazo de reembolso**", "", f"> {evidence['answer']}", "",
              f"Fonte: `{evidence['citations'][0]['citation']}`. Resposta extrativa, sem geração por LLM.", "",
              f"Avaliação sintética: **{evaluation['passed']}/{evaluation['cases']} cenários aprovados**.", "",
              f"Hit@3: {evaluation['retrieval_hit_at_3']:.2f}; MRR: {evaluation['mean_reciprocal_rank']:.2f}; acerto de abstenção: {evaluation['abstention_accuracy']:.2f}.", "",
              "A suíte é pequena, escrita junto com o demo e serve como regressão. Não mede qualidade em produção, compreensão semântica ou segurança de um LLM.", "",
              "[Voltar ao portfólio](../README.md)", ""]
    (directory / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Marcello Alves | Synthetic data and AI delivery portfolio")
    sub = parser.add_subparsers(dest="command", required=True)
    demo = sub.add_parser("demo", help="Run all offline demonstrations")
    demo.add_argument("--write-report", action="store_true", help="Regenerate synthetic reports/")
    sub.add_parser("reconcile", help="Reconcile synthetic fiscal and ERP snapshots")
    analytics = sub.add_parser("ask", help="Query an approved business metric")
    analytics.add_argument("question")
    analytics.add_argument("--identity", default="manager_north")
    analytics.add_argument("--period", default="2026-06")
    evidence = sub.add_parser("search", help="Retrieve evidence from fictional procedures")
    evidence.add_argument("question")
    evidence.add_argument("--role", default="operations")
    evidence.add_argument("--as-of", default="2026-06-30")
    sub.add_parser("evaluate", help="Evaluate retrieval and abstention")
    args = parser.parse_args()
    try:
        if args.command == "demo":
            results = all_demos()
            if args.write_report:
                write_report(results)
            result = {
                "synthetic": True, "offline": True,
                "reconciliation": results["reconciliation"]["summary"],
                "review_queue": results["reconciliation"]["actionable_count"],
                "analytics_scope": results["analytics"]["units"],
                "evidence": results["evidence"]["citations"][0]["citation"],
                "evaluation": f"{results['evaluation']['passed']}/{results['evaluation']['cases']}",
            }
        elif args.command == "reconcile":
            result = reconciliation_demo()
        elif args.command == "ask":
            result = ask(read("expenses.json")["rows"], identity=args.identity, question=args.question, period=args.period)
        elif args.command == "search":
            result = answer(read("documents.json")["documents"], args.question, role=args.role, as_of=args.as_of)
        else:
            result = evaluate(read("documents.json")["documents"], read("evaluation.json")["cases"])
    except (ValueError, QueryRejected) as exc:
        parser.exit(2, f"Request rejected: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
