# Apresentação em cinco minutos

[Voltar ao portfólio](../README.md)

Um roteiro para discutir raciocínio e demonstrar comportamento. Leia o código antes da apresentação e adapte o texto à sua forma de falar.

## 0:00 — Contexto

“Meu trabalho conecta a pergunta de negócio à operação. Escolhi três tipos de problema da minha experiência e reconstruí exemplos independentes para poder mostrar o raciocínio sem expor sistemas ou dados internos.”

## 0:40 — Conciliação

```bash
python portfolio.py demo
```

Explique por que uma ausência pode significar atraso de atualização. Mostre no relatório uma chave `awaiting_erp`, uma `ambiguous` e uma `amount_mismatch`. A decisão importante é quem deve agir e com qual evidência.

Pergunta para discussão: “Qual hipótese sobre atualização da fonte faria esse indicador induzir a equipe ao erro?”

## 1:50 — Autonomia com escopo

```bash
python portfolio.py ask "orçado versus realizado" --identity manager_north
python portfolio.py ask "orçado versus realizado" --identity controller
```

Mostre a diferença de escopo, o SQL e a definição de desvio. Declare que a persona é uma fixture e que produção exigiria identidade verificada e autorização no banco. Explique por que escolheu contratos aprovados antes de SQL gerado livremente.

## 2:50 — Evidência e limite

```bash
python portfolio.py search "vencimento de contrato" --role operations
python portfolio.py search "vencimento de contrato" --role legal
python portfolio.py search "prazo de reembolso" --as-of 2026-03-31
```

Mostre a abstenção, a citação permitida e a consulta histórica. Declare que é um baseline extrativo de retrieval, sem LLM. Discuta o que seria necessário para incorporar geração com avaliação independente.

## 4:00 — Qualidade e operação

```bash
python -m unittest discover -s tests -v
```

Escolha um teste para explicar: isolamento de unidade, cutoff de atualização ou versão de documento. Depois descreva como faria o piloto, quem validaria as respostas e como treinaria a equipe.

## 4:40 — Conexão com a experiência

Relacione o raciocínio demonstrado a uma experiência que você pode compartilhar. Distinga sua contribuição individual, a contribuição da equipe e o que foi reconstruído com IA neste repositório. Use somente métricas profissionais cuja metodologia e divulgação você consiga sustentar.

Não apresente os resultados sintéticos como ganhos reais, os papéis da CLI como autenticação, nem a suíte pequena como prova de segurança completa.
