# Dados sintéticos

Geração: `python scripts/generate_data.py`.

| Arquivo | Conteúdo | Origem |
|---|---|---|
| `synthetic/invoices.json` | 36 chaves; 28 registros fiscais e 32 de ERP; resultados esperados | Nove cenários declarados, seed 7421 |
| `synthetic/expenses.json` | 108 linhas, três unidades × três categorias × doze meses | Valores independentes, seed 1937 |
| `synthetic/documents.json` | Oito procedimentos, nove versões | Textos fictícios escritos para o caso |
| `synthetic/evaluation.json` | Oito perguntas positivas e quatro negativas | Suíte sintética de regressão |
| `synthetic/manifest.json` | Declaração de proveniência | Versionada com o gerador |

Nenhum fixture tem origem em registros de produção. Os meses representam um cenário simulado, não uma série de resultados realizados. Não há CPF, CNPJ, e-mail, endereço, identificador real de fornecedor ou vínculo com pessoas.

Os valores monetários de conciliação são strings decimais, e os de analytics são centavos inteiros. Os procedimentos fictícios não devem ser usados como orientação operacional ou jurídica para uma organização real.
