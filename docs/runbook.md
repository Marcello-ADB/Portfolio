# Executar, validar e recuperar

[Voltar ao portfólio](../README.md)

## Ambiente

Python 3.11 ou superior. Sem dependências externas. Execute os comandos na raiz do repositório. Se `python` não existir, use `python3` ou `py -3` conforme o sistema.

```bash
python --version
python portfolio.py demo
python -m unittest discover -s tests -v
```

## Regenerar as evidências

```bash
python scripts/generate_data.py
python portfolio.py demo --write-report
python scripts/check_publication.py
git diff -- data/synthetic reports
```

Sem mudança no código, o último comando não deve mostrar diferenças. O gerador substitui somente os fixtures sintéticos em `data/synthetic/`. A CLI substitui somente os relatórios em `reports/`.

## Diagnóstico

| Sintoma | Interpretação | Ação |
|---|---|---|
| `Request rejected` | Pergunta, período ou persona não permitidos | Consultar o catálogo em `portfolio_lab/analytics.py` |
| `abstained` | A busca não encontrou evidência suficiente no corpus permitido | Experimentar um papel apropriado ao cenário ou registrar lacuna documental |
| `incomplete_snapshot` | Carga incompleta ou linha rejeitada | Inspecionar `rejected`, corrigir o fixture e executar novamente |
| `ambiguous` | Mais de um candidato para a chave | Resolver identidade no dado; não forçar associação |
| Erro de encoding | Terminal usando outra codificação | Executar com `python -X utf8` |
| Arquivo de dados ausente | Fixture foi removido | Executar o gerador |

## Retorno ao estado conhecido

Nenhuma demo altera fontes externas. O banco de analytics é descartado ao final de cada consulta. Para recuperar relatórios ou dados de exemplo, execute o gerador e a CLI novamente. Mantenha experimentos de código em uma branch para comparar com a versão conhecida.

## Proposta para um ambiente real

Antes de implantação: responsável por cada fonte, registro de versão de regras, teste de escopo de acesso, limite de execução, observação de falhas e rota de atendimento. O primeiro piloto deve funcionar em paralelo à referência. Reverter a adoção significa voltar ao fluxo validado e interromper ações do sistema novo, preservando a trilha do incidente.

Este repositório não configura um serviço de produção, não dispara notificações e não agenda tarefas.
