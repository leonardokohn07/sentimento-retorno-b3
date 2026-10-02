# Pré-registro — teste de fim de semana agrupado

**Data:** 02/10/2026, escrito **antes** de rodar
`scripts/17_fim_de_semana_agrupado.py` sobre o sentimento real.

**O que já se sabia ao escrever:** só contagens e testes de código. O número
de pares (523 ativo-segunda, 135 fins de semana) foi contado com o sentimento
**embaralhado**, o que não revela relação nenhuma. A versão antiga deste teste
(script 9, ativo por ativo) já tinha rodado antes e deu inconclusiva por falta
de amostra.

## Pergunta

O sentimento das notícias publicadas com o mercado fechado (sábado e domingo,
horário de Brasília) se associa ao retorno da segunda-feira seguinte?

A ordem temporal é garantida pelo calendário. Uma notícia de sábado não pode
estar relatando o pregão de segunda, porque ele ainda não aconteceu.

## Dados

- Notícias: `dados/noticias_com_sentimento.csv`, de 01/01/2024 a 06/09/2026,
  sem alteração.
- Os 8 ativos do estudo: ABEV3, BBDC4, ITUB4, MGLU3, PETR4, SUZB3, VALE3, WEGE3.
- Fuso corrigido (`modulos/analise/fuso.py`): o dia da semana é o de Brasília.
  Notícia sem hora real fica com a data gravada.
- Preços: `dados/cache_precos/`, retorno logarítmico de fechamento a fechamento.
  O retorno de segunda já inclui o salto de abertura depois do fim de semana.

## Variáveis

- **Sentimento:** média do `score_polaridade` das notícias do fim de semana,
  por ativo e por segunda-feira, padronizada (z) dentro de cada ativo.
- **Retorno de segunda:** z dentro de cada ativo.
- **Retorno da sexta** (pregão anterior, controle): z dentro de cada ativo.

## Hipóteses

- **H0-A (principal):** a correlação entre o sentimento do fim de semana e o
  retorno de segunda é igual a zero.
- **H0-B (controle):** a correlação entre o sentimento do fim de semana e o
  retorno da sexta anterior é igual a zero.
  A notícia de fim de semana pode estar relatando a sexta. Este controle mede
  isso.

## Teste

- Pearson sobre o painel agrupado, com os ativos juntos.
- p-valor por permutação em **blocos de data**: 10.000 permutações, semente
  42, bicaudal, p = (k+1)/(N+1). A permutação sorteia qual segunda-feira recebe
  os retornos de qual, levando os 8 ativos juntos, para preservar a correlação
  entre ativos na mesma data.
- α = 5% para cada hipótese. As duas respondem perguntas diferentes, então não
  há correção para múltiplas comparações entre elas.
- Comparação entre segunda e sexta: teste de Steiger (1980) para correlações
  dependentes.
- Os resultados por ativo são **apenas descritivos**. Não se tira conclusão de
  nenhum ativo isolado.

## Calibração feita antes (sem olhar o resultado real)

Em 100 rodadas com o sentimento embaralhado, a taxa de falso positivo foi de
4% para H0-A e 7% para H0-B. O p-valor médio foi 0,48. É compatível com o
nível nominal de 5%.

## Poder

Com n = 523, o menor r detectável com 80% de poder é **0,122**, supondo
independência entre as observações. Esse número é **otimista**: os ativos se
movem juntos na mesma segunda-feira, e o n efetivo fica entre 135 (número de
fins de semana) e 523. O efeito do estudo em D+0 vai de 0,10 a 0,20, então o
teste pode não ter poder para os efeitos menores.

## Regra de decisão (fixada agora)

1. H0-A rejeitada com r > 0 e H0-B não rejeitada → compatível com
   notícia → preço.
2. H0-A e H0-B rejeitadas → se Steiger mostrar segunda > sexta, predomina
   notícia → preço. Se não mostrar, é inconclusivo quanto à direção.
3. H0-A rejeitada com r < 0 → não sustenta a hipótese. Reportar como achado
   inesperado.
4. Só H0-B rejeitada → o fim de semana relata a sexta, o que é evidência de
   preço → notícia.
5. Nenhuma rejeitada → **não** é evidência de ausência de efeito. Reportar o
   menor r detectável.

## Análises secundárias, reportadas qualquer que seja o resultado

- **Sensibilidade:** a mesma análise sem a correção de fuso.
- **Período estendido:** acrescentar as notícias de 01/10/2021 a 31/12/2023,
  coletadas em 02/10/2026 com o mesmo coletor, os mesmos termos e o mesmo
  léxico (`scripts/18_coletar_periodo_anterior.py`), em arquivo separado. Se
  a análise principal e a estendida discordarem, as duas são reportadas e a
  **principal governa a conclusão**.
- Limitação já conhecida para o período estendido: o arquivo antigo do Google
  News pode ser mais esparso. A densidade por ano é reportada.
