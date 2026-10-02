# Pré-registro — Fase G: o que acontece DENTRO da hora da notícia

**Data:** 02/10/2026, escrito **antes** de baixar qualquer barra de minuto e
antes da coleta de notícias recentes.

## Por que esta fase existe

No desenho com barras de 60 minutos, a hora da publicação fica de fora,
porque mistura o antes e o depois. Uma reação em poucos minutos não seria
vista. Esse é o único ponto cego da fase causal (diário, seção 10).

## Pergunta

Nos minutos em volta da publicação, o preço se move **depois** da notícia
(notícia → preço) ou **antes** dela (preço → notícia)?

## Dados

- **Barras de 5 minutos** do Yahoo dos 8 ativos, nos ~60 dias que o Yahoo
  guarda no dia do download. As barras de 1 minuto dos últimos dias também
  são guardadas, mas só servem para a coleta futura.
- **Notícias dos 8 ativos com horário exato,** no período coberto pelas
  barras:
  - as que já estão em `noticias_com_sentimento.csv`;
  - mais uma coleta nova, com o mesmo coletor e os mesmos termos, até
    02/10/2026, em arquivo separado.
  - Repetidas (mesmo ativo e mesma manchete) contam uma vez.
- **Horário, em ordem de prioridade:**
  1. a hora real do Google;
  2. a hora do WordPress com o filtro de data do adendo 1.
- **Sentimento:** a medida escolhida pela regra da Fase F (o FinBERT, se
  adotado; senão, o léxico). A outra entra como análise secundária.

## Desenho

- **Evento:** notícia publicada em dia de pregão entre **10h30 e 16h20**
  (horário de Brasília). Assim cabem 30 minutos antes e 30 minutos depois
  dentro do pregão contínuo (barras de 10h00 a 16h50).
- **Barra da publicação:** a barra de 5 minutos que contém o horário. Ela
  fica **fora** dos dois lados, porque mistura antes e depois. O ponto cego
  cai de 60 para 5 minutos.
- **Retorno anormal de cada barra:** retorno do ativo menos a média dos
  outros 7 (β = 1), como no `causal.py`.
- **Agregação:** várias notícias do mesmo ativo na mesma barra viram um
  evento, com a média do sentimento.

## Testes (Holm sobre M1 e M2, α = 5%, bicaudais)

| | Pergunta | Retorno usado |
|---|---|---|
| **M1** | A notícia prevê os 30 min SEGUINTES? (notícia → preço) | soma das 6 barras depois da barra da publicação |
| **M2** | A notícia vem depois dos 30 min ANTERIORES? (preço → notícia) | soma das 6 barras antes da barra da publicação |

- **Estatística:** correlação agrupada, como no `teste_horario`. O sentimento
  é padronizado dentro do ativo. O retorno é padronizado por ativo em todas
  as barras.
- **p-valor:** permutação com 10.000 sorteios e semente 42. Cada evento
  recebe o retorno da **mesma faixa de 5 minutos em outro dia sorteado**,
  com todos os ativos juntos.

## Análises secundárias (sem correção)

- **G-S1:** janelas de 15 minutos (3 barras).
- **G-S2:** perfil do retorno anormal acumulado de −60 a +60 minutos para o
  terço mais positivo e o mais negativo. É descritivo e vira gráfico.
  Usa eventos entre 11h00 e 15h50.
- **G-S3:** M1 e M2 com a outra medida de sentimento.
- **G-S4, controle positivo:** só as manchetes de relato ("Ação da Vale cai
  3%"). Elas DEVEM se associar aos 30 min anteriores.
- **G-S5, falsificação:** a mesma faixa de horário no pregão anterior (dia
  errado). Deve dar ≈ 0.

## Status: PILOTO

- O n deste piloto é limitado pelos ~60 dias do Yahoo.
- O menor r detectável (80% de poder) será reportado junto.
- Se um teste não rejeitar com poder baixo, isso **não** significa ausência
  de efeito.

## Coleta prospectiva e regra de parada (fixadas agora)

- **Coletor diário** (`scripts/34_coleta_diaria.py`), ativado pelo Leonardo no
  Agendador de Tarefas do Windows. Ele guarda:
  - as notícias dos últimos dias, que vêm com a hora real do Google;
  - os horários do WordPress;
  - as barras de 1 e de 5 minutos.
  Ele **acrescenta** ao arquivo, sem sobrescrever o que já foi guardado.
- **Amostra confirmatória:** só eventos **a partir de 03/10/2026**. Não se
  mistura com o piloto.
- **Parada:** quando a amostra confirmatória chegar a **1.500 eventos**
  (menor r detectável ≈ 0,072) ou em **30/06/2027**, o que vier primeiro.
  Aí M1 e M2 rodam **uma vez**, com a medida fixada pela Fase F (confirmada
  pela rotulagem humana).
- **Sem espiar:** até a parada, o coletor só informa quantos eventos já
  existem, nunca a correlação.

## O que não será feito

- Trocar janela, horário de corte, fonte de horário ou medida depois de ver
  resultado.
- Rodar M1/M2 na amostra confirmatória antes da regra de parada.
