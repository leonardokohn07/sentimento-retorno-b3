# Pré-registro mestre — fase de causalidade

**Data:** 02/10/2026, escrito **antes** de rodar `scripts/25_fase_causal.py`
sobre o sentimento real.

**O que já se sabia ao escrever:**
- os resultados anteriores (diário, seção 1);
- contagens de notícias por janela de horário, sem nenhum retorno;
- a qualidade dos dados de preço;
- a calibração do código com sentimento embaralhado: falso positivo entre
  0% e 8% em 60 rodadas para cada teste, contra os 5% nominais.

**A coleta de horários via WordPress ainda está em andamento.** A regra de uso
(abaixo) foi fixada antes de ver o resultado da validação.

## Objetivo

Testar se a notícia chega ANTES do movimento de preço (notícia → preço) ou
DEPOIS (preço → notícia), separando o retorno do dia em:

- **abertura:** do fechamento anterior até a abertura;
- **pregão:** da abertura até o fechamento;
- **horas:** barras de 60 minutos;

e cruzando com o horário de publicação.

## Dados

- **Notícias:** `noticias_com_sentimento.csv` (2024-2026) e
  `noticias_2021_2023.csv` (2021-2023), os 8 ativos do estudo, fuso
  corrigido (`fuso.py`).
- **Sentimento:** `score_polaridade`, a média por ativo e por unidade de tempo.
- **Retorno anormal:** retorno do ativo menos a média das demais ações do
  cache (β = 1). O Ibovespa do Yahoo não serve para isso, porque sua abertura
  é igual ao fechamento anterior em 29,6% dos dias.
  **Exceção:** a réplica P8 usa o método original do Teste 3 (Ibovespa no
  fechamento, α e β estimados em 2023).
- **Horário de publicação, em ordem de prioridade:**
  1. a hora real do Google (não 07:00/08:00 UTC);
  2. a hora da API do WordPress (date_gmt), **somente se** a validação
     contra o Google, nas notícias que têm as duas, der **≥ 85% dentro de 15
     minutos com n ≥ 20**. Se não der, a análise principal usa só o Google;
  3. a hora da busca web: só na análise de sensibilidade S3, sem as linhas de
     controle.
- **Janelas, no horário de Brasília:**
  - **noite/madrugada:** depois das 18h de um pregão até antes das 10h do
    pregão seguinte, inclusive fins de semana e feriados;
  - **pregão:** das 11h às 15h59, para que existam a hora anterior e a hora
    seguinte inteiras dentro do mesmo dia;
  - **excluídas:** notícias das 17h às 17h59 (fechamento ambíguo), das 10h
    às 10h59 e das 16h às 16h59.

## Família principal (Holm sobre P1 a P9, α = 5%)

| | Pergunta | Linhas | Resultado testado | Controle | Lado |
|---|---|---|---|---|---|
| **P1** | A notícia do dia D prevê a ABERTURA de D+1? | notícias de dia útil, 2024-26 | abertura anormal D+1 | pregão D e abertura D | bicaudal |
| **P2** | A notícia da noite prevê a ABERTURA seguinte? | notícias com hora, janela noite | abertura anormal do pregão seguinte | pregão anterior | bicaudal |
| **P3** | A notícia da noite reflete o PREGÃO que já passou? (relato) | as mesmas de P2 | pregão anormal anterior | — | bicaudal |
| **P4** | A notícia no pregão prevê a HORA SEGUINTE? | notícias com hora, 11h às 15h59 | barra anormal k+1 | — | bicaudal |
| **P5** | A notícia no pregão vem depois da HORA ANTERIOR? (relato ou vazamento) | as mesmas de P4 | barra anormal k−1 | — | bicaudal |
| **P6** | Réplica de P1 em 2021-2023 | notícias de dia útil, 2021-23 | igual a P1 | igual a P1 | unicaudal, no sinal de P1 |
| **P7** | Réplica do Teste 1 (informativas, D+0) em 2021-2023 | sem manchetes de relato | retorno bruto D+0 | — | unicaudal (r > 0) |
| **P8** | Réplica do Teste 3 (retorno anormal, D+0) em 2021-2023 | todas | retorno anormal (Ibovespa) D+0 | — | unicaudal (r > 0) |
| **P9** | A notícia de fim de semana prevê a ABERTURA de segunda? | notícias de sábado e domingo, 2024-26 | abertura anormal de segunda | pregão de sexta | bicaudal |

- **Estatística:** correlação parcial agrupada. O sentimento é padronizado
  dentro do ativo e residualizado nos controles. O resultado é residualizado
  por ativo em todo o calendário.
- **p-valor:** permutação em blocos de data, 10.000 permutações, semente 42.
  Nas barras horárias, a permutação sorteia outro dia e mantém a mesma hora.
- **P9 é um refinamento declarado:** o teste de fim de semana anterior, com
  o retorno de fechamento a fechamento, deu nulo. P9 troca o resultado pela
  abertura de segunda, onde a informação do fim de semana deveria aparecer.
  Por ser um refinamento depois de um nulo, entra na família corrigida e não
  é tratado como achado isolado.

## Análises secundárias (sem correção, só apoio)

- **S1:** P4 e P5 com as janelas do resto do dia (da abertura até a notícia;
  da notícia até o fechamento).
- **S2:** P1 a P5 com o retorno bruto.
- **S3:** P2 a P5 acrescentando os horários da busca web.
- **S4 — controle positivo do método:** só as manchetes de relato ("Ação da
  Vale cai 3%"). Elas DEVEM se associar ao movimento ANTERIOR à publicação.
  Se isso não aparecer, o método não enxerga nem o relato óbvio.
- **S5 — falsificação:** P4 usando a mesma hora do pregão ANTERIOR (o dia
  errado). Deve dar ≈ 0.
- **S6:** réplica do placebo (própria contra cruzada) em 2021-2023.
- **S7:** perfil médio do retorno anormal hora a hora (−3h a +3h) para as
  notícias mais positivas e as mais negativas. É descritivo e vira gráfico.

## Poder

Menor r detectável com 80% de poder, supondo independência (número otimista):

| Teste | n | Menor r detectável |
|---|---|---|
| P1 | ~4.000 | 0,044 |
| P2/P3 | ~250 | 0,18 |
| P4/P5 | ~190 | 0,20 |
| P6/P7 | ~2.700 | 0,054 |
| P8 | ~2.700 | 0,054 |
| P9 | ~540 | 0,12 |

Os n de P2 a P5 podem crescer se os horários do WordPress passarem na
validação.

## Regras de interpretação (fixadas agora)

- **Evidência direta de notícia → preço:** P4 rejeitada (Holm) com r > 0.
  O preço se move na hora DEPOIS da publicação. P2 e P1 com r > 0 reforçam.
- **Evidência de relato (preço → notícia):** P3 ou P5 rejeitada com r > 0.
  Ressalva: P5 também pode ser negociação informada antes da notícia
  (Hendershott et al., 2015). Não se distingue uma coisa da outra.
- **As duas ao mesmo tempo:** a relação é bidirecional. Reportar a força de
  cada direção.
- **Replicado:** P6, P7 e P8 rejeitadas (Holm). Só então o resultado é
  chamado de robusto entre períodos.
- **Nulos:** um teste com poder baixo (P2 a P5) que não rejeita **não**
  significa ausência de efeito. Reportar o menor r detectável.
- **Nenhuma conclusão será escrita como "comprovado 100%".** A linguagem
  permitida é:
  - "evidência direta de precedência temporal" (P4);
  - "evidência consistente" (P1, P2, P9);
  - "não confirmado".

## O que não será feito

- Trocar janela, controle, horário de corte ou fonte de horário depois de
  ver resultado.
- Promover uma análise secundária a principal.
- Esconder qualquer teste desta lista.
