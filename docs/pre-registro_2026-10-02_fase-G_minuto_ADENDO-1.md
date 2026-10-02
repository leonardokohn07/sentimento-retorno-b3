# Adendo 1 ao pré-registro da Fase G — atraso do horário do Google

**Data:** 02/10/2026, escrito **antes** de rodar qualquer teste da Fase G.
Até aqui, só foram baixados os dados (barras de 5 e de 1 minuto e notícias
recentes). Nenhum retorno em volta das notícias foi calculado.

## Por que este adendo existe

O adendo 1 da fase causal mostrou que, quando o Google e o site discordam, o
Google costuma registrar a notícia **depois** do site, de 23 minutos a 8
horas. Às vezes é a hora em que o Google indexou a matéria.

Na escala de horas isso pesa pouco. **Na escala de minutos pesa muito.** Se
a matéria saiu às 10h00 e o Google marca 10h20, a reação das 10h00 às 10h20
cai na janela "antes". Fica parecendo que o preço se moveu antes da notícia,
quando foi o contrário.

Esse viés empurra o resultado para M2 (preço → notícia), justamente a
conclusão do estudo. Por isso precisa de um teste próprio.

## O que é acrescentado (só análises secundárias, sem mudar M1 e M2)

- **G-D1, diagnóstico:** nas notícias que têm as duas horas (Google real e
  WordPress com o filtro de data), a distribuição da diferença Google −
  WordPress em minutos: mediana, quartis e % em que o Google vem depois.
- **G-S6, sensibilidade com a hora oficial:** M1 e M2 com a prioridade
  invertida. Usa a hora do WordPress quando existe e a do Google só quando
  não há WordPress.
- **G-S7, só hora oficial:** M1 e M2 apenas com eventos que têm hora do
  WordPress.

## Regra de leitura (fixada agora)

- **Atraso de indexação:** M2 aparece com a hora do Google, mas some (perde
  a significância e cai em módulo) com a hora do WordPress em G-S6/G-S7.
  Nesse caso, a leitura é "atraso de indexação", **não** "preço antes da
  notícia".
- **Precedência do preço confirmada na escala de minutos:** M2 se mantém
  com a hora oficial.
- **M1 e M2 continuam sendo os testes principais**, com a prioridade do
  pré-registro original.
