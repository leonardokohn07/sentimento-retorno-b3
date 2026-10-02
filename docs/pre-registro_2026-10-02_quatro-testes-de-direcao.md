# Pré-registro — quatro testes sobre a direção da relação

**Data:** 02/10/2026, escrito **antes** de rodar qualquer um dos testes abaixo
sobre o sentimento real.

**O que já se sabia ao escrever:** o resultado publicado (D+0 em 6 de 8; D+1
em 0 de 8; D−1 em 3 de 8) e o teste de fim de semana agrupado (nenhuma
hipótese rejeitada). A lista de manchetes de relato (teste 1) foi calibrada
olhando só o texto das manchetes, sem nenhum retorno.

## Por que estes testes

A correlação de D+0 tem três explicações possíveis:

- notícia → preço;
- preço → notícia (o jornal relata o pregão);
- causa comum (dia ruim para a bolsa inteira).

Cada teste elimina uma delas.

## Base comum aos quatro testes

- Notícias: `dados/noticias_com_sentimento.csv`, de 01/01/2024 a 06/09/2026,
  apenas os 8 ativos do estudo.
- `data_pregao` recalculada no horário de Brasília (`modulos/analise/fuso.py`).
  Isso mudou 0,97% das notícias e nenhum veredito do estudo.
- Retornos: logarítmicos, de `dados/cache_precos/`.
- **Teste agrupado:** sentimento e retorno padronizados (z) dentro de cada
  ativo; Pearson sobre o painel; p-valor por permutação em blocos de data
  (10.000, semente 42, bicaudal). A calibração com sentimento embaralhado deu
  4% a 7% de falso positivo em 100 rodadas.
- α = 5% em cada teste. Os resultados por ativo são descritivos.

## Teste 1 — sem as manchetes que relatam preço

- **Filtro:** `filtro_relato.py`, congelado. O verbo de movimento precisa ter
  como sujeito a ação, o ticker ou o índice. Marca 584 manchetes (3,2%).
  Precisão estimada em ~95%, numa revisão de 40 manchetes marcadas.
- **H0-1 (principal):** no subconjunto INFORMATIVO (sem as manchetes de relato),
  a correlação agrupada entre o sentimento e o retorno de D+0 é igual a zero.
- **Secundários:**
  - mesmo teste no subconjunto de relato;
  - D−1 no subconjunto informativo;
  - contagem por ativo, para comparar com o 6 de 8.
- **Leitura:**
  - H0-1 rejeitada com r > 0 → a relação não depende de manchetes que relatam
    preço.
  - H0-1 não rejeitada → a relação de D+0 pode vir do relato. Reportar também
    o menor r detectável.

## Teste 3 — retorno anormal (descontado o Ibovespa)

- **Modelo de mercado:** retorno anormal = r − (α + β·r_Ibovespa). α e β são
  estimados por mínimos quadrados nos **250 pregões anteriores a 02/01/2024**,
  ou seja, antes de qualquer notícia da amostra. Usa `calcular_retorno_anormal`
  do `hipotese.py`.
- **Ibovespa:** `^BVSP` via yfinance, guardado em `dados/mercado/`, fora do
  cache de preços.
- **H0-3 (principal):** a correlação agrupada entre o sentimento e o retorno
  ANORMAL de D+0 é igual a zero.
- **Secundários:** D−1 com retorno anormal; contagem por ativo.
- **Leitura:**
  - H0-3 rejeitada com r > 0 → a associação sobrevive quando se tira o
    movimento da bolsa inteira, então não é só causa comum.
  - Não rejeitada → parte relevante do efeito pode ser o mercado inteiro.

## Teste 2 — placebo entre empresas

- **Construção:** para cada par (A, B) com A ≠ B, correlacionar o sentimento
  da empresa A com o retorno ANORMAL da empresa B, nos dias com notícia de A.
- **Pares principais:** os 54 pares de setores diferentes. Os 2 pares entre
  bancos (ITUB4 e BBDC4) são reportados à parte, porque notícia de um banco pode
  legitimamente afetar o outro.
- **H0-2a:** a média das 54 correlações cruzadas é igual a zero.
- **H0-2b:** a média das 8 correlações próprias (A com A) é igual à média das
  54 cruzadas.
- **Inferência:** permutação em blocos de data (10.000, semente 42), a mesma
  permutação para todos os pares.
- **Leitura:**
  - Correlação cruzada ≈ 0 e própria > cruzada (H0-2b rejeitada) → o efeito é
    da notícia da própria empresa.
  - Correlação cruzada > 0 significativa → existe humor geral que o desconto
    do Ibovespa não removeu.

## Teste 5 — Granger nos dois sentidos

- **Séries diárias por ativo,** em todos os pregões do período: sentimento
  médio do dia (0 quando não há notícia) e retorno bruto.
- **Sentido "sentimento → retorno":** os 5 sentimentos anteriores melhoram a
  previsão do retorno de hoje, além dos 5 retornos anteriores?
- **Sentido "retorno → sentimento":** os 5 retornos anteriores melhoram a
  previsão do sentimento de hoje, além dos 5 sentimentos anteriores?
- **Teste:** Wald robusto à heterocedasticidade (HC1), 5% por ativo.
- **Regra:** um sentido é considerado sustentado se for significativo em **3 ou
  mais dos 8 ativos**. Pelo acaso, P(≥ 3 de 8 | 5%) = 0,6%.
- **Sensibilidade:** 1 defasagem em vez de 5.
- **Limitação declarada:** com dados diários, o Granger não enxerga o que
  acontece dentro do mesmo dia. Ele testa as defasagens, não o D+0.

## O que não será feito

- Nenhum ajuste na lista de palavras depois de ver resultado.
- Nenhum teste extra escolhido depois de ver resultado entra como principal.
  Se surgir algum, ele será marcado como exploratório.
