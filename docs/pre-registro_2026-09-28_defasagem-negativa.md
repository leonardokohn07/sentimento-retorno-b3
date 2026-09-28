# Pré-registro — teste de defasagem negativa (D−1)

**Data:** 28 de setembro de 2026
**Autores:** Leonardo Kohn e Maurício Renck Gedrat
**Orientador:** Prof. Raul Mesquita
**Estudo:** InvestAI — sentimento de notícias × retorno de ações da B3

Este documento é escrito e versionado **antes** de o teste ser executado. O
commit que o adiciona precede, no histórico do git, o commit que traz os
resultados — é essa ordem que torna o pré-registro verificável por terceiros.

## Origem da ideia

O teste foi sugerido pelo professor orientador do TCC durante a FEICIT 2026,
com o seguinte raciocínio: se a informação pública já está no preço no momento
em que se torna pública, vale olhar a notícia do dia contra o retorno do dia
anterior.

## O que será testado

Para cada um dos 8 ativos da amostra, a correlação de Pearson entre o
sentimento médio das notícias do pregão D e o retorno do pregão **D−1**, ou
seja, o pregão imediatamente anterior no calendário da B3.

## Hipóteses

- **H₀:** o sentimento das notícias do dia D não tem relação com o retorno do
  pregão anterior (ρ = 0).
- **H₁:** existe relação (ρ ≠ 0).

## Parâmetros fixados agora

| Parâmetro | Valor |
|---|---|
| Nível de significância (α) | 0,05, bilateral |
| Mínimo de observações por ativo | 60, o mesmo do estudo (vem da análise de poder) |
| Amostra | os mesmos 8 ativos já analisados, sem inclusão nem exclusão |
| Alinhamento | por pregão, usando `retorno_lag_-1` |
| Critério de parada | rodada única; nenhum ativo será reanalisado |

## Como cada resultado será interpretado

Isto é decidido **antes** de ver os números, e não muda depois.

1. **D−1 não significativo na maioria dos ativos, e D+0 significativo em 6 de
   8** — a associação observada não é explicada por jornalismo reativo, isto é,
   por veículos escrevendo sobre um movimento de preço que já aconteceu. É o
   resultado que fortalece o estudo.

2. **D−1 significativo com magnitude parecida com a de D+0** — parte relevante
   da associação é o jornal reagindo ao preço. Nesse caso o trabalho passa a
   reportar que a direção temporal não está estabelecida, e a conclusão atual
   sobre D+0 precisa ser reescrita com essa ressalva.

3. **D−1 significativo, mas bem menor que D+0** — há alguma reação do noticiário
   ao preço, sem explicar a associação contemporânea. Reporta-se os dois.

Em qualquer dos três casos o resultado será publicado, inclusive se for o
cenário 2, que é o desfavorável.

## O que este teste não resolve

Mesmo o cenário 1 não estabelece causalidade. Ele afasta uma explicação
alternativa (a de ordem inversa), mas continua sem descartar fatores comuns
que afetem notícia e preço ao mesmo tempo. A limitação de horário permanece:
95,7% das notícias têm horário normalizado pela fonte.
