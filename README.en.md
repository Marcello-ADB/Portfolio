<p align="right"><a href="README.md">Português</a> · <strong>English</strong></p>

# Marcello Alves

**Applied Data & AI · From business problem to operational adoption**

I turn ambiguous business needs into systems people can use, understand and operate. My work connects discovery, data integration, implementation and adoption — an approach aligned with **Forward Deployed Engineering**.

I am a Head of Business Intelligence with a background in financial markets, consulting, entrepreneurship and social impact. I combine hands-on delivery, team development and executive communication. [Professional background →](https://www.linkedin.com/in/marcelloaf/)

## Selected demonstrations

All examples are independent implementations with **entirely synthetic data**. No employer source code, production data, credentials or internal infrastructure is included.

| Project | Business question | Technical evidence |
| :--- | :--- | :--- |
| [Reconciliation with context](projects/reconciliation/README.md) | Is a missing ERP record a real exception or a late snapshot? | Composite keys, exact money, duplicate handling, watermarks and traceable review queue |
| [Governed business analytics](projects/governed-analytics/README.md) | How can managers self-serve without widening data access? | Approved natural-language intents, parameterized SQL, scoped data and read-only execution |
| [Evidence desk](projects/evidence-desk/README.md) | Which current procedure supports the answer? | Permission-aware BM25, versioned citations, extractive answers and abstention tests |

The analytics planner is a deterministic catalog, not unrestricted text-to-SQL. The evidence assistant is a retrieval baseline, not a generative LLM deployment. These choices make the control logic reproducible without accounts, API keys or cost.

## Run locally

Python **3.11+**, standard library only.

```bash
git clone https://github.com/Marcello-ADB/Portfolio.git
cd Portfolio
python portfolio.py demo
python -m unittest discover -s tests -v
```

Use `python3` where appropriate, or `python -X utf8` for terminals with a different default encoding.

```bash
python portfolio.py ask "budget versus actual" --identity manager_north
python portfolio.py ask "spend by category" --identity controller
python portfolio.py search "vencimento de contrato" --role operations
python portfolio.py search "vencimento de contrato" --role legal
```

The last two commands illustrate abstention versus permitted evidence. The document corpus is in Portuguese. CLI personas are test fixtures, not production authentication.

## Review paths

- **Business and delivery:** [Working method](docs/how-i-work.md) and the project case studies.
- **Engineering:** [Architecture and trade-offs](docs/architecture.md), [source](portfolio_lab/) and [tests](tests/).
- **Evidence:** [Generated report](reports/README.md), [retrieval evaluation](reports/evaluation.json) and [data provenance](docs/privacy-and-provenance.md).

The repo contains 26 automated tests and a 12-case authored retrieval regression suite. These verify bounded synthetic scenarios; they are not production performance claims.

My professional toolkit includes Power BI, SQL, Python, PostgreSQL/Supabase, n8n and applied AI integrations. I chose a small offline core here so reviewers can inspect behavior before discussing deployment architecture.

[LinkedIn](https://www.linkedin.com/in/marcelloaf/) · [Reference projects](docs/references.md) · [MIT license](LICENSE)
