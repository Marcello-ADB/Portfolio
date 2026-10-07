# Dados, autoria e limites

[Voltar ao portfólio](../README.md)

## Origem dos exemplos

Este repositório contém **implementações demonstrativas novas**, inspiradas em classes de problema de dados, integração e operação. Não foi obtido removendo nomes de uma base real ou exportando aplicações internas.

O nome **Instituto Horizonte** é fictício neste contexto. Empresas, fornecedores, documentos, unidades, valores, datas de operação e políticas dos fixtures foram criados para o exercício. Não existe tabela de correspondência com organizações ou pessoas reais.

## O que pode ser conferido

- A geração está integralmente em [`scripts/generate_data.py`](../scripts/generate_data.py).
- Seeds `7421` e `1937` produzem valores determinísticos sem ler arquivos externos.
- Os documentos são oito procedimentos fictícios escritos para os testes, com nove versões no total.
- [`data/synthetic/manifest.json`](../data/synthetic/manifest.json) registra a proveniência declarada.
- Os relatórios só contêm resultados dos fixtures versionados.

## Fronteira pública

Não entram código institucional, backups, configurações de produção, endpoints internos, tokens, dados de pessoas, notas fiscais, contratos, fotos, marcas de clientes, dumps, exports de workflows ou capturas de sistemas internos.

A trajetória profissional pública é apresentada por Marcello no LinkedIn. As demonstrações não são produtos de qualquer empregador ou cliente. Números de economia, perda, ROI ou escala de produção não são atribuídos aos demos.

## Autoria

A curadoria foi construída a partir do perfil e da experiência apresentados por Marcello Alves. O código e a documentação desta versão foram elaborados com assistência de IA e validados pelos testes registrados no repositório. Isso não transfere autoria nem direitos sobre aplicações institucionais, que não foram copiadas.

Os repositórios em [Referências](references.md) informaram a organização e os critérios de apresentação. Não houve importação de seu código, imagens ou textos.

## Antes de acrescentar um novo caso

Reconstruir o exemplo a partir do problema, gerar novos dados, explicitar o escopo e revisar todos os arquivos que serão versionados. Um dado “mascarado” ainda pode conservar relações identificáveis; este portfólio adota geração independente.

O verificador local de publicação detecta alguns padrões de segredos, arquivos indevidos e caminhos locais. É uma defesa auxiliar, não certificação de anonimização, segurança ou conformidade legal.
