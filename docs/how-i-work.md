# Como trabalho

[Voltar ao portfólio](../README.md)

Meu ponto de partida é a decisão que alguém precisa tomar. Procuro entender o processo, identificar onde o dado perde significado e construir uma solução que a equipe consiga incorporar à rotina.

Este documento descreve uma proposta de método para os casos demonstrativos. Não constitui um relato de implantação ou uma medição de resultados de um cliente.

## 1. Descoberta com quem vive o processo

Conversa com patrocinador, usuário operacional e responsável pelo dado. Registro o problema, a decisão afetada, as exceções frequentes e o custo do trabalho manual.

**Exemplo:** na conciliação, “há muitas pendências” vira “a equipe precisa distinguir ausência real de documento posterior à carga”.

Entregável: uma página com problema, público, recorte, critérios de aceite e responsável pela validação. Não escolheria a stack antes de entender a restrição de operação.

## 2. Contrato dos dados

Defino origem, significado, granularidade, identidade, atualização, acesso e dono. Faço profiling com escopo autorizado e comparo resultados com uma referência conhecida.

**Exemplo:** dois sistemas podem chamar campos diferentes de “valor”. Antes de comparar, é preciso confirmar se ambos incluem as mesmas parcelas.

Entregável: dicionário mínimo, regras de qualidade, definição da métrica e tratamento de registros rejeitados.

## 3. Recorte executável

Construo uma fatia que atravesse entrada, regra e saída. Mostro o resultado para a pessoa que vai utilizá-lo, incluindo exemplos de erro e incerteza.

**Exemplo:** a primeira consulta governada responde uma métrica validada para uma unidade. O catálogo cresce conforme o usuário confirma o significado das respostas.

Entregável: demo reproduzível, decisões de arquitetura e testes das regras que poderiam causar uma decisão incorreta.

## 4. Piloto acompanhado

O novo sistema roda em paralelo à referência, com um grupo pequeno. A equipe registra divergências e confirma a correção antes de ampliar o uso.

| Caso | Critério inicial proposto | Condição para interromper |
|---|---|---|
| Conciliação | Cenários acordados classificados corretamente; totais conferidos | Carga sem completude ou crescimento de falsos positivos |
| Consulta governada | Mesmo resultado da consulta oficial e escopo validado | Resultado divergente ou dado fora da permissão |
| Evidência documental | Fontes válidas e acessíveis; falhas registradas | Citação inválida, versão incorreta ou vazamento entre papéis |

Os limiares quantitativos devem ser definidos com os responsáveis antes do piloto. Não há metas de ROI inventadas neste portfólio.

## 5. Adoção e transferência

Documento o fluxo na linguagem da operação, treino quem será responsável e transfiro a capacidade de diagnosticar problemas. A entrega inclui saber quem cuida da fonte, da regra, da infraestrutura e do atendimento.

Entregáveis: manual curto, runbook, rotina de revisão, responsável por indicador e plano de reversão. As exceções do piloto alimentam o backlog com exemplos concretos.

## Minha contribuição consultiva

Conectar o pedido executivo à realidade da operação; negociar o menor escopo útil; tornar trade-offs compreensíveis; construir junto com a equipe; e acompanhar se a solução passou a ajudar uma decisão. Liderança e desenvolvimento de pessoas fazem parte desse trabalho.
