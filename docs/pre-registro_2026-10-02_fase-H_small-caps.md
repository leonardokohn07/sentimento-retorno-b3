# Pré-registro — Fase H: réplica em ações de menor liquidez

**Data:** 02/10/2026, escrito **antes** de coletar qualquer notícia ou preço
dessas ações e antes de saber quais serão sorteadas.

## Pergunta

O padrão "o preço vem antes da notícia" também aparece em ações menores? A
literatura sugere que a imprensa pesa mais nas empresas pouco acompanhadas
(Fang; Peress, 2009). Se em algum lugar a notícia antecipa o preço, é ali.

## Seleção (regra fixa, sem escolher a dedo)

1. **Universo:** a carteira do Índice Small Cap (SMLL) da B3 no dia da
   coleta, baixada do site da B3 e guardada como veio. Se a B3 não responder,
   a fase **não** é feita com uma lista improvisada.
2. **Fora:** os ativos que já estão no estudo e os que têm termos próprios
   no coletor (ABEV3, BBAS3, BBDC4, ELET3, ITUB4, MGLU3, PETR4, RENT3,
   SUZB3, VALE3, WEGE3).
3. **Sondagem de cobertura** (conta notícias, não olha preço nem
   sentimento):
   - busca no Google News pelo **código de negociação** (ex.: "CVCB3"), que
     é a regra padrão do coletor para ativos sem termos próprios;
   - de 01/06/2026 a 31/08/2026.
   - O código evita a ambiguidade de nomes que são palavras comuns
     ("Azul", "Vamos").
4. **Elegíveis:** pelo menos 30 manchetes únicas na sondagem (≈ 10 por mês).
5. **Sorteio:** 8 elegíveis, em ordem alfabética, sorteados com semente 42
   (`numpy.random.default_rng(42).choice`). Com menos de 8 elegíveis, entram
   todos. A lista completa, com as contagens, é guardada.

## Coleta

- **Notícias:** de 01/01/2024 a 06/09/2026 (o período do estudo), com o mesmo
  coletor, o termo = código e o mesmo léxico. O escore do FinBERT também é
  calculado.
- **Preços diários** (abertura e fechamento) do Yahoo, em pasta separada
  (`dados/smallcaps/`), sem tocar no cache do estudo.
- **Sentimento usado:** a medida escolhida pela regra da Fase F. A outra
  entra como secundária.

## Testes (família própria, Holm, α = 5%)

| | Pergunta | Resultado | Controle | Lado |
|---|---|---|---|---|
| **H1** | Associação no mesmo dia (D+0) | retorno anormal do pregão D (fechamento a fechamento) | — | unicaudal (r > 0), como réplica |
| **H2** | A notícia do dia D prevê a ABERTURA de D+1? (notícia → preço) | abertura anormal D+1 | pregão D e abertura D | bicaudal |
| **H3** | A notícia do dia D vem depois do pregão D−1? (preço → notícia) | retorno anormal de D−1 | — | bicaudal |
| **H4** | A notícia de fim de semana prevê a abertura de segunda? | abertura anormal de segunda | pregão de sexta | bicaudal |

- **Dia da notícia:**
  - em H1 e H3, o pregão em que a notícia pode agir (antes das 17h, o mesmo
    dia; depois, o seguinte; fim de semana, a segunda), com o fuso
    corrigido;
  - em H2, o dia útil de calendário, como no P1.
- **Retorno anormal:** retorno do ativo menos a média das outras 7 small caps
  (β = 1), como no `causal.py`.
- **Estatística e p-valor:** os da fase causal (`teste_parcial`):
  - correlação parcial agrupada;
  - permutação em blocos de data, com 10.000 sorteios e semente 42.

## Leitura

- **Mesmo padrão das grandes:** H3 positivo e significativo, H2 nulo.
- **Diferença importante:** H2 positivo e significativo. Em ações menores, a
  notícia antecipa o preço.
- **Poder:** o menor r detectável é reportado com o n que a coleta der.
  Nulo com poder baixo não é ausência de efeito.

## O que não será feito

- Trocar a regra de seleção, o período, os termos ou os testes depois de ver
  qualquer resultado.
- Substituir uma ação sorteada por outra "melhor".
