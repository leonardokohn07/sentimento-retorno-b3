# Revisão de literatura: direção da causalidade entre notícias e retornos (B3)

**Pergunta:** a correlação no mesmo dia entre sentimento de notícias e retornos aparece porque **as notícias movem os preços** ou porque **os jornalistas noticiam movimentos de preço que já aconteceram**?

**Como foi verificado (02/10/2026):** os metadados de cada referência foram conferidos pelo DOI no **Crossref** (`api.crossref.org/works/<DOI>`). Quando o Crossref recusou o pedido por limite de requisições (HTTP 429), usei **OpenAlex** (registro individual) + **OpenAIRE**. As buscas por artigos novos foram feitas no OpenAlex (autocomplete por título), **OpenAIRE** e **DOAJ**, porque a busca livre do OpenAlex também deu 429. Os resumos vieram do Crossref, do OpenAIRE ou do OpenAlex. No OpenAlex o resumo é reconstruído a partir de um índice invertido, então usei esse texto só para a ideia geral e para números que aparecem nele.

**Legenda de status**
- **VERIFICADO via Crossref:** autores, ano, título, periódico, v., n., p. e DOI batem com o registro Crossref do DOI.
- **VERIFICADO via OpenAlex/OpenAIRE:** os mesmos campos batem nessas duas bases (o Crossref ficou indisponível para aquele DOI).
- **CORRIGIDO:** a referência candidata tinha algum erro (nenhum caso nesta lista).
- **NÃO VERIFICADO:** não foi possível confirmar (nenhum caso nesta lista).

---

## A. Referências candidatas: verificação

### A1
TETLOCK, P. C. Giving content to investor sentiment: the role of media in the stock market. **The Journal of Finance**, v. 62, n. 3, p. 1139-1168, 2007. DOI: 10.1111/j.1540-6261.2007.01232.x
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** usa uma série temporal diária do pessimismo no texto de uma coluna popular do *Wall Street Journal* para prever retornos e volume do mercado. Pessimismo alto prevê queda de preços **seguida de reversão** aos fundamentos, e pessimismo extremo prevê volume alto. O autor lê isso como sentimento de *noise traders*, e não como informação nova.
- **Observação:** os resumos lidos (Crossref, OpenAlex, OpenAIRE) **não** citam um teste no sentido retorno → mídia. Lembro que o artigo estima um VAR com defasagens nos dois sentidos, mas **não consegui confirmar isso pelo resumo**. Conferir no PDF.

### A2
TETLOCK, P. C.; SAAR-TSECHANSKY, M.; MACSKASSY, S. More than words: quantifying language to measure firms' fundamentals. **The Journal of Finance**, v. 63, n. 3, p. 1437-1467, 2008. DOI: 10.1111/j.1540-6261.2008.01362.x
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** mede a fração de palavras negativas em notícias específicas de cada empresa e testa se ela prevê lucros e retornos futuros. Palavras negativas preveem lucros baixos, os preços **subreagem brevemente**, e a previsibilidade é maior em notícias **sobre fundamentos**. Isso sustenta separar notícias de fundamento das notícias que só relatam o preço.

### A3
TETLOCK, P. C. All the news that's fit to reprint: do investors react to stale information? **Review of Financial Studies**, v. 24, n. 5, p. 1481-1512, 2011. DOI: 10.1093/rfs/hhq141
- **Status:** VERIFICADO via Crossref. O Crossref não traz o resumo, então ele foi lido no OpenAlex.
- **Método/achado:** define a "velhice" (*staleness*) de uma notícia como a similaridade textual com as 10 notícias anteriores da mesma empresa e compara a reação a notícias novas e velhas. Os retornos reagem menos a notícias velhas, mas o retorno do dia de uma notícia velha prevê **reversão na semana seguinte**, o que indica sobrerreação de investidores pessoa física.

### A4
ENGELBERG, J.; PARSONS, C. A. The causal impact of media in financial markets. **The Journal of Finance**, v. 66, n. 1, p. 67-97, 2011. DOI: 10.1111/j.1540-6261.2010.01626.x
- **Status:** VERIFICADO via OpenAlex + OpenAIRE. O Crossref deu 429 em todas as tentativas para este DOI.
- **Método/achado:** compara investidores de 19 regiões dos EUA (separadas por CEP) que receberam **coberturas diferentes do mesmo evento** (anúncios de resultado de empresas do S&P 500). Assim o evento fica fixo e só a cobertura muda. A cobertura local prevê a negociação local, e a negociação acompanha **o horário da reportagem local**, o que é difícil de explicar sem efeito causal da mídia. (Resumo: OpenAIRE.)

### A5
PERESS, J. The media and the diffusion of information in financial markets: evidence from newspaper strikes. **The Journal of Finance**, v. 69, n. 5, p. 2007-2043, 2014. DOI: 10.1111/jofi.12179
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** usa um experimento natural: greves de jornais nacionais em vários países, ou seja, dias sem jornal. Nos dias de greve o volume cai 12% e a dispersão dos retornos e a volatilidade intradiária caem 7%, enquanto os retornos agregados não mudam. Os jornais propagam notícias do dia anterior.

### A6
DOUGAL, C.; ENGELBERG, J.; GARCÍA, D.; PARSONS, C. A. Journalists and the stock market. **Review of Financial Studies**, v. 25, n. 3, p. 639-679, 2012. DOI: 10.1093/rfs/hhr133
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** aproveita a escala **exógena** de colunistas do *WSJ*: coloca efeitos fixos de colunista numa regressão diária do retorno do Dow Jones (o R² sobe cerca de 35%) e depois **interage esses efeitos com os retornos defasados**. Essa interação aumenta o poder explicativo em mais um terço: os jornalistas **amplificam ou atenuam o sentimento recente do mercado**. O efeito do colunista depende do movimento passado e ainda explica parte do retorno diário, ou seja, há as duas direções ao mesmo tempo. É o caso mais próximo da pergunta do projeto.

### A7
HUBERMAN, G.; REGEV, T. Contagious speculation and a cure for cancer: a nonevent that made stock prices soar. **The Journal of Finance**, v. 56, n. 1, p. 387-396, 2001. DOI: 10.1111/0022-1082.00330
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** estudo de caso. Uma matéria de domingo do *New York Times* sobre a EntreMed repetia informação publicada 5 meses antes (na *Nature* e no próprio *Times*). A ação foi de 12,063 no fechamento de sexta para abertura a 85 e fechamento perto de 52 na segunda, e a alta foi persistente **sem informação nova**. A atenção da mídia, sozinha, moveu o preço.

### A8
CHAN, W. S. Stock price reaction to news and no-news: drift and reversal after headlines. **Journal of Financial Economics**, v. 70, n. 2, p. 223-260, 2003. DOI: 10.1016/S0304-405X(03)00146-6
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** compara ações que tiveram manchetes (notícia pública identificável) com ações de retorno mensal parecido **sem notícia**. Depois da notícia há *drift* (subreação), mais forte após más notícias. Depois de movimentos extremos **sem notícia** há reversão. Separar movimentos com e sem notícia é informativo.

### A9
KLIBANOFF, P.; LAMONT, O.; WIZMAN, T. A. Investor reaction to salient news in closed-end country funds. **The Journal of Finance**, v. 53, n. 2, p. 673-699, 1998. DOI: 10.1111/0022-1082.265570
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** painel semanal de preço × valor patrimonial (NAV) de fundos fechados de países, comparando semanas **com e sem** notícia do país na capa do *NYT*. Numa semana típica o preço subreage ao fundamento (elasticidade menor que 1). Nas semanas com notícia de capa a elasticidade fica perto de 1: notícia saliente acelera a reação.

### A10
BOUDOUKH, J.; FELDMAN, R.; KOGAN, S.; RICHARDSON, M. Information, trading, and volatility: evidence from firm-specific news. **The Review of Financial Studies**, v. 32, n. 3, p. 992-1033, 2019. DOI: 10.1093/rfs/hhy083
- **Status:** VERIFICADO via Crossref. Publicado online em 30/07/2018, fascículo de março de 2019. Resumo lido no OpenAIRE.
- **Método/achado:** usa análise textual para identificar **informação fundamental** nas notícias e compara a volatilidade **overnight** com a do **pregão**. Essa informação responde por 49,6% da volatilidade idiossincrática overnight, contra 12,4% durante o pregão. Notícias explicam muito mais o que acontece fora do pregão.

### A11
FANG, L.; PERESS, J. Media coverage and the cross-section of stock returns. **The Journal of Finance**, v. 64, n. 5, p. 2023-2052, 2009. DOI: 10.1111/j.1540-6261.2009.01493.x
- **Status:** VERIFICADO via Crossref.
- **Método/achado:** comparação *cross-section*: ordena as ações pela cobertura de mídia e compara os retornos esperados, controlando fatores de risco. Ações **sem cobertura** rendem mais que ações muito cobertas, sobretudo as pequenas, com muita pessoa física, pouca cobertura de analistas e alta volatilidade idiossincrática.

### A12
ENGELBERG, J.; SASSEVILLE, C.; WILLIAMS, J. Market madness? The case of Mad Money. **Management Science**, v. 58, n. 2, p. 351-364, 2012. DOI: 10.1287/mnsc.1100.1290
- **Status:** VERIFICADO via Crossref. Fascículo de fevereiro de 2012; o OpenAlex marca 2011, que é o ano da versão online. Resumo lido no OpenAlex.
- **Método/achado:** trata as recomendações do programa de TV *Mad Money* como choques de atenção e usa a **audiência diária da Nielsen** como medida direta de atenção. As recomendações geram grandes **retornos overnight** que revertem nos meses seguintes. O efeito é maior em ações pequenas e ilíquidas e quando a audiência de alta renda é alta: a mídia gera *mispricing*.

### A13
MACKINLAY, A. C. Event studies in economics and finance. **Journal of Economic Literature**, v. 35, n. 1, p. 13-39, 1997.
- **Status:** VERIFICADO via OpenAlex. **Não tem DOI** registrado, o que é normal para o JEL de 1997.
- **Método/achado:** artigo metodológico sobre **estudo de eventos**. Mede o efeito de um evento datado pelos retornos (anormais) em torno da data, supondo que o mercado incorpora a informação rapidamente. É a base para medir a reação a notícias com data e hora.

### A14
GRANGER, C. W. J. Investigating causal relations by econometric models and cross-spectral methods. **Econometrica**, v. 37, n. 3, p. 424-438, 1969. DOI: 10.2307/1912791
- **Status:** VERIFICADO via OpenAlex + OpenAIRE. O Crossref deu 429. O OpenAlex registra a página final errada (424-424), e o OpenAIRE dá 424-(4)38.
- **Método/achado:** define a causalidade **testável**: X "causa" Y se o passado de X melhora a previsão de Y. Também mede defasagem e força causal com o espectro cruzado. O resumo avisa que a **"causalidade instantânea" aparente** costuma vir de registro lento da informação, ou seja, dados pouco frequentes, ou de variáveis omitidas. Esse é exatamente o problema de uma correlação no mesmo dia, e dados horários ajudam a separar as direções.

### A15
BARCLAY, M. J.; HENDERSHOTT, T. Price discovery and trading after hours. **Review of Financial Studies**, v. 16, n. 4, p. 1041-1073, 2003. DOI: 10.1093/rfs/hhg030
- **Status:** VERIFICADO via OpenAlex + OpenAIRE. O Crossref deu 429.
- **Método/achado:** compara a quantidade e a eficiência da descoberta de preços por hora no pregão e no *after-hours* (Nasdaq). O pregão revela mais informação por hora, mas o *after-hours* gera descoberta de preços significativa, embora ruidosa. As variações **antes da abertura** refletem mais informação privada que as de depois do fechamento.

**Placar da Seção A:** 15 de 15 confirmadas (11 via Crossref e 4 via OpenAlex/OpenAIRE), 0 corrigidas, 0 não verificadas.

---

## B. Artigos adicionais: timing intradiário, overnight e causalidade reversa

### B1. Causalidade reversa com preço de abertura
STRAUß, N.; VLIEGENTHART, R.; VERHOEVEN, P. Lagging behind? Emotions in newspaper articles and stock market prices in the Netherlands. **Public Relations Review**, v. 42, n. 4, p. 548-555, 2016. DOI: 10.1016/j.pubrev.2016.03.010
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** mede emoções (dicionário LIWC holandês) em 128.507 notícias de jornal e as compara com os **preços de abertura** de 21 ações do AEX (2002-2013), usando **testes de causalidade de Granger**. As emoções das notícias **não** afetam de forma consistente a abertura do dia seguinte. O Granger indica que os jornais é que **refletem** o mercado nos dias seguintes.

### B2. Relação recíproca intradiária
STRAUß, N.; VLIEGENTHART, R.; VERHOEVEN, P. Intraday news trading: the reciprocal relationships between the stock market and economic news. **Communication Research**, v. 45, n. 7, p. 1054-1077, 2018. DOI: 10.1177/0093650217705528
- **Status:** VERIFICADO via Crossref. Online em 28/04/2017, fascículo de outubro de 2018. Resumo lido no OpenAIRE.
- **Método/achado:** estima **VAR** em intervalos de 5 min, 20 min e **1 h** com 2.440 tweets econômicos da Reuters/Bloomberg (set/2015), 50 matérias do terminal Bloomberg e o Dow Jones. O volume e a relevância das notícias influenciam o índice, e as notícias também respondem às oscilações do mercado. O efeito notícia → índice é **mais forte no intervalo de 1 hora**. Os tweets funcionam mais como reportagem *posterior* para o público.

### B3. "Espelho ou molde?"
SCHEUFELE, B.; HAAS, A.; BROSIUS, H.-B. Mirror or molder? A study of media coverage, stock prices, and trading volumes in Germany. **Journal of Communication**, v. 61, n. 1, p. 48-70, 2011. DOI: 10.1111/j.1460-2466.2010.01526.x
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAlex.
- **Método/achado:** combina análise de conteúdo das notícias sobre 8 empresas alemãs com as variações **diárias** de preço e volume, num desenho de séries temporais com **modelagem ARIMA**. No curto prazo (2 meses), a mídia **reflete mais do que molda** os preços. Quase não há sinal de efeito amplo da mídia.

### B4. O preço se move antes da notícia (negociação informada)
HENDERSHOTT, T.; LIVDAN, D.; SCHÜRHOFF, N. Are institutions informed about news? **Journal of Financial Economics**, v. 117, n. 2, p. 249-287, 2015. DOI: 10.1016/j.jfineco.2015.03.007
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** cruza dados diários não públicos de compra e venda de institucionais (NYSE, 2003-2005) com todas as notícias da Reuters, cujo sentimento é classificado por PLN. O fluxo de ordens institucional **prevê a ocorrência e o tom das notícias** e a reação do mercado. Por isso, um preço que se move *antes* da notícia não prova que o jornalista copiou o preço: pode ser negociação informada.

### B5. Notícias com horário e retornos de alta frequência
JIANG, H.; LI, S. Z.; WANG, H. Pervasive underreaction: evidence from high-frequency data. **Journal of Financial Economics**, v. 141, n. 2, p. 573-599, 2021. DOI: 10.1016/j.jfineco.2021.04.003
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** divide o retorno diário, com dados de alta frequência, em uma parte **ligada a notícias** (a reação em torno do horário de chegada) e uma parte sem notícias. Há **subreação generalizada**: o preço continua na direção da reação inicial por vários dias, sem reversão, e mais ainda quando os investidores estão distraídos.

### B6. Reação em segundos a uma notícia com horário exato
BUSSE, J. A.; GREEN, T. C. Market efficiency in real time. **Journal of Financial Economics**, v. 65, n. 3, p. 415-437, 2002. DOI: 10.1016/S0304-405X(02)00148-4
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** usa o **horário exato** em que cada ação é citada nos segmentos *Morning Call* e *Midday Call* da CNBC, transmitidos com o mercado aberto, junto com dados intradiários. O preço reage **em segundos**: notícias positivas são incorporadas em cerca de 1 minuto e as negativas em cerca de 15 minutos, e o volume dobra no minuto seguinte. É a identificação de manual por *timestamp*.

### B7. VAR de alta frequência com *news analytics*
GROß-KLUßMANN, A.; HAUTSCH, N. When machines read the news: using automated text analytics to quantify high frequency news-implied market reactions. **Journal of Empirical Finance**, v. 18, n. 2, p. 321-340, 2011. DOI: 10.1016/j.jempfin.2010.11.009
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** estima um **VAR com dados de 20 segundos** para ações da Bolsa de Londres, com notícias pré-processadas por uma ferramenta automática (relevância, novidade e direção). Retornos, volatilidade, volume e spread reagem à chegada das notícias. **Filtrar por relevância é crucial** para separar sinal de ruído.

### B8. Retorno overnight, abertura e atenção
BERKMAN, H.; KOCH, P. D.; TUTTLE, L.; ZHANG, Y. J. Paying attention: overnight returns and the hidden cost of buying at the open. **Journal of Financial and Quantitative Analysis**, v. 47, n. 4, p. 715-741, 2012. DOI: 10.1017/S0022109012000270
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAlex.
- **Método/achado:** separa o retorno **overnight** (fechamento → abertura) do **intradiário** (abertura → fechamento). Retornos overnight positivos são seguidos de reversão no pregão, porque o **preço de abertura fica alto** em ações que atraíram atenção recente de pessoa física. A atenção aparece primeiro na abertura.

**Placar da Seção B:** 8 de 8 verificados via Crossref.

---

## C. Estudos brasileiros (B3/Ibovespa)

### C1. Causalidade reversa no Brasil
ARAÚJO, T.; ELEUTÉRIO, S.; LOUÇÃ, F. Do sentiments influence market dynamics? A reconstruction of the Brazilian stock market and its mood. **Physica A: Statistical Mechanics and its Applications**, v. 505, p. 1139-1149, 2018. DOI: 10.1016/j.physa.2018.04.045
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** usa uma abordagem de **redes** para relacionar os retornos dos ativos do Ibovespa a um índice de sentimento da mídia especializada (**Thomson Reuters MarketPsych**), com dados diários de 2007 a 2015. Conclusão do resumo: "**changes in market prices affect news more than the reverse**", ou seja, no Brasil o preço afeta mais a notícia do que o contrário.

### C2. Granger entre sentimento diário de portais brasileiros e o mercado
CAROSIA, A. E. O.; COELHO, G. P.; SILVA, A. E. A. Investment strategies applied to the Brazilian stock market: a methodology based on sentiment analysis with deep learning. **Expert Systems with Applications**, v. 184, art. 115470, 2021. DOI: 10.1016/j.eswa.2021.115470
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAIRE.
- **Método/achado:** classifica o sentimento de notícias financeiras em português com uma rede neural (a CNN foi a melhor), aplica o **teste de causalidade de Granger** entre o sentimento diário predominante de três grandes portais e o mercado, e simula estratégias de investimento. Há **influência significativa** do sentimento diário das notícias sobre o mercado, e as estratégias superaram *Random Walk* e *Buy & Hold*.

### C3. Correlação contemporânea sem relação dinâmica (caso parecido com o do projeto)
SOUZA, D. M. S.; MARTINS, O. S. Brazilian stock market performance and investor sentiment on Twitter. **Revista de Gestão (REGE)**, v. 31, n. 1, p. 18-33, 2024. DOI: 10.1108/REGE-07-2021-0145
- **Status:** VERIFICADO via Crossref. Publicado online em 06/09/2022, fascículo de janeiro de 2024. Resumo lido no OpenAIRE.
- **Método/achado:** constrói um índice de sentimento do Twitter com 314.864 tweets (2017-2018) e o relaciona a retorno e volume com **regressão quantílica e VAR**. O sentimento tem **correlação contemporânea positiva** com os retornos, mas o **VAR não confirmou relação dinâmica** (defasada). Pela regressão quantílica, o efeito só aparece em períodos de retornos baixos.

### C4. Sentimento do *Valor Econômico* e Ibovespa (tese)
SILVA, M. D. O. P. **O efeito do sentimento das notícias sobre o comportamento dos preços no mercado acionário brasileiro**. 2017. Tese (Doutorado em Ciências Contábeis), Programa Multi-Institucional e Inter-Regional de Pós-Graduação em Ciências Contábeis, Universidade de Brasília, Brasília, 2017. DOI: 10.26512/2018.02.t.32178
- **Status:** VERIFICADO via OpenAlex + OpenAIRE. O Crossref foi bloqueado por limite de requisições. O orientador listado no OpenAIRE é M. A. V. Machado. O ano 2017 vem da nota "Tese (doutorado) ... 2017" do registro; o DOI traz 2018 e o repositório, 2022.
- **Método/achado:** mede o sentimento textual de 45.304 notícias do *Valor Econômico* (25/07/2011 a 30/06/2017). Seleciona os preditores da volatilidade por **regressão quantílica LASSO** e avalia o impacto do sentimento no mercado por **autorregressão quantílica**. Os dados também incluem DJIA, VIX e S&P 500. Em mercado de baixo desempenho, o pessimismo prevê queda de 28,72 pontos-base no Ibovespa e o otimismo, alta de 22 pb. Em alta incerteza, o pessimismo prevê -76,21 pb (q0,05) e -81,94 pb (q0,95).

### C5. Notícias em português preveem quedas de preço
DUARTE, J. J.; GONZÁLEZ, S. M.; CRUZ, J. C. Predicting stock price falls using news data: evidence from the Brazilian market. **Computational Economics**, v. 57, n. 1, p. 311-340, 2020. DOI: 10.1007/s10614-020-10060-y
- **Status:** VERIFICADO via OpenAlex + OpenAIRE. O Crossref foi bloqueado por limite de requisições.
  - O OpenAlex dá 2020, que provavelmente é a data online. O v. 57, n. 1 deve ser o fascículo impresso, possivelmente de 2021: **conferir no PDF**.
  - O nome da segunda autora aparece como "Sahudy Montenegro González". Conferir se a entrada ABNT é GONZÁLEZ, S. M. ou MONTENEGRO GONZÁLEZ, S.
- **Método/achado:** combina notícias em português com preços históricos de 64 ações e testa 11 algoritmos de aprendizado de máquina contra *Buy & Hold* e média móvel. As janelas de publicação e de retorno são diárias, semanais e mensais. O resumo aponta **forte relação entre a publicação de notícias e as variações de preço** no Brasil, e dá para prever quedas com notícias em português.

### C6. Estudo de eventos com notícias ESG no Brasil
PICCIONI, C. A.; BASTOS, S. B.; CAJUEIRO, D. O. Stock price reaction to environmental, social, and governance news: evidence from Brazil and financial materiality. **Sustainability**, v. 16, n. 7, art. 2839, 2024. DOI: 10.3390/su16072839
- **Status:** VERIFICADO via Crossref. Resumo lido no OpenAlex.
- **Método/achado:** cria um dicionário aberto de termos ESG (categorias SASB) para classificar notícias sobre as maiores empresas brasileiras e mede a **reação dos preços depois das notícias**. Os preços reagem positivamente a notícias ESG favoráveis e negativamente a adversas, e os investidores priorizam a informação **financeiramente material**.

**Placar da Seção C:** 6 de 6 verificados (4 via Crossref e 2 via OpenAlex/OpenAIRE).

*Outros estudos brasileiros encontrados e não incluídos por causa do limite de 6:*
- Nizer & Nievola (2012, *Expert Systems with Applications*, 10.1016/j.eswa.2012.02.162).
- Carosia, Coelho & Silva (2020, *Applied Artificial Intelligence*, 10.1080/08839514.2019.1673037).
- Januário et al. (*IEEE Latin America Transactions*, v. 20, n. 3, 10.1109/TLA.2022.9667151).
- de Jesus et al. (2025, *Computational Economics*, 10.1007/s10614-024-10835-7).

Esses quatro foram conferidos só no OpenAlex/OpenAIRE, sem Crossref. O resumo de Januário et al. trata só da classificação de sentimento, sem relação com retornos.

---

## Métodos da literatura mais aplicáveis ao projeto

Dados disponíveis: preços diários, preço de abertura, horário de parte das notícias e preços horários dos últimos 2 anos.

1. **Granger/VAR nos dois sentidos com dados diários** (Granger, 1969; Scheufele et al., 2011; Strauß et al., 2016; Carosia et al., 2021; Souza & Martins, 2024; Araújo et al., 2018; Dougal et al., 2012).
   - Estimar duas equações: o retorno de hoje explicado pelos retornos e sentimentos defasados, e o sentimento de hoje explicado pelos sentimentos e retornos defasados.
   - Se o retorno passado prevê o sentimento e o contrário não acontece, os jornalistas estão reagindo ao preço.
   - Granger (1969) avisa que a causalidade "instantânea" aparente pode vir do registro lento da informação (dados pouco frequentes). Por isso este teste deve ser complementado pelos métodos 2 e 3.

2. **Retorno overnight × intradiário usando o preço de abertura e o horário de publicação** (Barclay & Hendershott, 2003; Berkman et al., 2012; Boudoukh et al., 2019; Strauß et al., 2016; Engelberg et al., 2012).
   - Dividir o retorno do dia em overnight, ln(Abertura_t / Fechamento_{t-1}), e intradiário, ln(Fechamento_t / Abertura_t).
   - Classificar as notícias pela hora de publicação: antes da abertura, durante o pregão ou depois do fechamento.
   - Se a notícia move o preço, o tom das notícias publicadas antes da abertura deve explicar o retorno **overnight seguinte**.
   - Se o tom de notícias publicadas **depois do fechamento** explica o retorno intradiário **que já aconteceu**, a notícia está apenas relatando o preço. Essa comparação funciona como teste placebo.

3. **Estudo de eventos intradiário com preços horários em torno do horário da notícia** (MacKinlay, 1997; Busse & Green, 2002; Groß-Klußmann & Hautsch, 2011; Jiang, Li & Wang, 2021; Strauß et al., 2018).
   - Para cada notícia com horário, calcular o retorno anormal (ação menos Ibovespa) nas horas -k ... +k e tirar a média por grupo (positivas e negativas).
   - Movimento que começa **antes** da notícia indica que o jornalista reporta um preço que já se moveu. Atenção: também pode ser negociação informada, como em Hendershott et al. (2015).
   - Salto ou *drift* **depois** da notícia indica que a notícia move o preço.
   - Alternativa: um VAR com dados horários (Strauß et al., 2018).

**Cuidado prático:** retirar ou marcar as notícias que só resumem o mercado (do tipo "Ibovespa fecha em alta"), porque elas são causalidade reversa por construção. Tetlock et al. (2008), Boudoukh et al. (2019) e Chan (2003) mostram que vale separar notícias de fundamento dos movimentos sem notícia.

**Desenhos ideais, mas difíceis de reproduzir com estes dados:** cobertura local diferente do mesmo evento (Engelberg & Parsons, 2011), greves de jornal (Peress, 2014), rodízio de colunistas (Dougal et al., 2012) e notícia velha republicada (Huberman & Regev, 2001; Tetlock, 2011). Servem para a discussão do trabalho.

---

## Limitações da busca (páginas que não consegui ler)

- **Recusados pelo proxy do WebFetch por limite de requisições (429)**, com pedido para não tentar de novo:
  - `api.crossref.org/works?query.bibliographic=Market+Madness...` (resolvido pelo OpenAlex);
  - `api.crossref.org/works/10.1007/s10614-020-10060-y` (C5);
  - `api.crossref.org/works/10.26512/2018.02.t.32178` (C4).
- **Crossref com 429 repetido** para os DOIs de A4, A14 e A15. Esses três foram verificados pelo OpenAlex + OpenAIRE.
- **Bloqueios de busca:** a busca livre do OpenAlex (`/works?search=`) e a API do Semantic Scholar deram 429, e a busca do SciELO é bloqueada por robots.txt. Por isso a busca de estudos brasileiros usou OpenAIRE e DOAJ, e pode ter deixado de fora artigos de periódicos nacionais fora dessas bases (por exemplo, RBFin, RAC e RCF via SPELL).
