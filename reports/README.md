# Evidência reproduzível

> Todos os dados e valores abaixo são sintéticos. Não representam resultados institucionais.

Gerado por `python portfolio.py demo --write-report`. Execução local, sem rede, sem credenciais e sem LLM.

## 01 / Conciliação

| Estado | Documentos |
|---|---:|
| `ambiguous` | 4 |
| `amount_mismatch` | 4 |
| `awaiting_erp` | 4 |
| `awaiting_fiscal` | 4 |
| `cancelled` | 4 |
| `matched` | 4 |
| `missing_erp` | 4 |
| `missing_fiscal` | 4 |
| `state_conflict` | 4 |

**16 exceções para revisão**; o sistema não classifica essas exceções como perdas.

Cutoffs: ERP até 2026-06-29; fiscal até 2026-06-30. Hashes de entrada e evidência por documento no [JSON](reconciliation.json).

## 02 / Consulta governada

Identidade de demonstração: `manager_north`. Unidade autorizada: **Norte**.

```sql
SELECT unit, SUM(budget_cents) AS budget_cents, SUM(actual_cents) AS actual_cents, SUM(actual_cents - budget_cents) AS variance_cents FROM expenses WHERE month = ? GROUP BY unit ORDER BY unit
```

Parâmetro: `2026-06`. Valores em centavos inteiros.

```json
[
  {
    "unit": "Norte",
    "budget_cents": 4967869,
    "actual_cents": 2818508,
    "variance_cents": -2149361
  }
]
```

## 03 / Evidência documental

Pergunta: **prazo de reembolso**

> O prazo de reembolso é de dez dias após a despesa. A solicitação deve conter comprovante e aprovação do gestor.

Fonte: `DOC-002@v2#p1`. Resposta extrativa, sem geração por LLM.

Avaliação sintética: **12/12 cenários aprovados**.

Hit@3: 1.00; MRR: 1.00; acerto de abstenção: 1.00.

A suíte é pequena, escrita junto com o demo e serve como regressão. Não mede qualidade em produção, compreensão semântica ou segurança de um LLM.

[Voltar ao portfólio](../README.md)
