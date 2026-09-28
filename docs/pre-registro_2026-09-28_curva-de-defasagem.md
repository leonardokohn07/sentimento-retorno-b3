# Pré-registro — curva de defasagem de D−5 a D+5

**Data:** 28 de setembro de 2026
**Autores:** Leonardo Kohn e Maurício Renck Gedrat
**Orientador:** Prof. Raul Mesquita
**Estudo:** InvestAI — sentimento de notícias × retorno de ações da B3

Escrito e versionado **antes** da execução. O commit seguinte traz os resultados.

## De onde vem a pergunta

O teste D−1 (pré-registro de 28/09/2026, mesma data) encontrou correlação
significativa entre o sentimento da notícia do dia D e o retorno do pregão
anterior em 3 dos 8 ativos. Esse resultado é compatível com **duas**
explicações que o dado diário não separa:

1. **Antecipação da informação.** O conteúdo já circulava — rumor, dado
   parcial, expectativa — e o preço reagiu antes de a notícia ser publicada.
   É a hipótese levantada pelo professor orientador: quando a notícia sai, o
   efeito já está "saturado" no preço.
2. **Cobertura reativa.** O preço se moveu e o veículo escreveu depois, a
   respeito do próprio movimento.

## O que será medido

A correlação de Pearson entre o sentimento do dia D e o retorno em D+k, para
k = −5, −4, −3, −2, −1, 0, +1, +2, +3, +5, em cada um dos 8 ativos da amostra,
e também com os ativos agrupados (todos os pares ativo-dia empilhados).

Todas as defasagens são medidas no calendário de pregões.

## Como cada formato de curva será interpretado

Definido antes de ver o resultado.

- **Decaimento gradual antes de D+0** (correlação cresce de D−5 até D−1 e
  atinge o pico em D+0 ou perto dele): compatível com antecipação — a
  informação chega ao preço aos poucos, antes da publicação. Favorece a
  hipótese 1.
- **Pico isolado em D−1, com D−2 e D−3 próximos de zero**: compatível com
  cobertura reativa de curtíssimo prazo. Favorece a hipótese 2.
- **Curva achatada em toda a parte negativa, com pico só em D+0**: nenhuma das
  duas; a associação é contemporânea, como o estudo vinha reportando.
- **Correlações significativas espalhadas sem padrão**, inclusive em D+2, D+3
  ou D+5: sinal de que parte do que se mede é ruído, e o achado de D−1 perde
  força. Seria reportado como tal.

## O que este teste não resolve

Nenhum formato de curva **prova** antecipação ou reatividade: ambas as
explicações podem coexistir, em proporções diferentes por ativo. A separação
definitiva depende de horário de publicação, e é o que os Fatos Relevantes da
CVM permitirão testar. Esta análise é indício, não prova, e será reportada
nesses termos.

## Parâmetros

| Parâmetro | Valor |
|---|---|
| α | 0,05, bilateral |
| Amostra | os mesmos 8 ativos, sem inclusão nem exclusão |
| Mínimo por ativo | 60 observações |
| Correção para múltiplas comparações | nenhuma no teste por ativo; a leitura é do FORMATO da curva, não de significância isolada em cada k |
| Critério de parada | rodada única |
