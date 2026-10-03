# Plano de Pesquisa — MOSTRATEC 2026 (versão 3, 03/10/2026)

Pronto para copiar: cada seção vai no seu campo, na ordem do formulário.
As tabelas da versão 2 viraram listas, porque tabela não cola bem em campo
de formulário.

---

## TÍTULO

SENTIMENTO DE NOTÍCIAS E RETORNO DE AÇÕES: análise de risco de carteiras na bolsa brasileira

---

## 1. TEMA

A relação entre o sentimento das notícias da imprensa econômica e o retorno de ações negociadas na B3, a Bolsa de Valores brasileira, e a direção temporal dessa relação: quem se move primeiro, o preço ou a notícia.

O recorte principal abrange oito ações de sete setores da economia, ao longo de 32 meses (2024 a 2026), com dados diários e intradiários (barras de 60, 5 e 1 minuto). O resultado foi replicado em outro período (2021 a 2023) e em oito ações de menor liquidez (small caps). A delimitação exclui deliberadamente três objetos: mercados estrangeiros, redes sociais como fonte de sentimento — considera-se apenas a imprensa — e qualquer tentativa de construir estratégia de investimento. O objeto é a existência, o momento e a direção de uma associação estatística, não sua exploração financeira.

---

## 2. JUSTIFICATIVA

A pesquisa se justifica em quatro frentes.

**Social.** O número de investidores pessoa física na B3 passou de 583 mil, em 2011 (B3, 2020), para 5,4 milhões no segundo trimestre de 2025 (B3, 2025). Boa parte desse público se informa pela internet: na pesquisa da B3 (2020), 73% dos investidores entrevistados disseram se informar sobre investimentos pela internet; na 9ª edição do Raio X do Investidor Brasileiro, "portais e sites" e "sites de notícias" aparecem entre os canais que os investidores usam para se informar e decidir (ANBIMA, 2026). A literatura mostra que a pessoa física tende a comprar as ações que estão no noticiário (Barber; Odean, 2008) e que, no Brasil, 97% dos que persistiram no day trade por mais de 300 dias perderam dinheiro (Chague; De-Losso; Giovannetti, 2020). A pergunta prática é direta: quem decide pela manchete está à frente ou atrás do preço?

**Científica.** Duas teorias fazem previsões diferentes. A hipótese de eficiência de mercado prevê que, quando a notícia pública sai, o preço já se ajustou (Fama, 1970). A literatura de sentimento e atenção prevê que o tom da mídia move o preço no curto prazo (Baker; Wurgler, 2007; Tetlock, 2007). A forma de decidir entre elas é a ordem no tempo (Granger, 1969). A regulação brasileira dá uma pista do mecanismo: o fato relevante deve ser divulgado de forma ampla e simultânea, de preferência antes da abertura ou depois do fechamento do pregão (Comissão de Valores Mobiliários, 2021). O canal primário da informação é, portanto, o comunicado da empresa, e não a matéria jornalística. Os estudos brasileiros encontrados usam dados diários (Araújo; Eleutério; Louçã, 2018; Carosia; Coelho; Silva, 2021) ou redes sociais (Souza; Martins, 2024). Nas bases consultadas, não encontramos estudo que use o horário exato de publicação de matérias da imprensa e preços intradiários de ações da B3 para testar a direção.

**Metodológica.** Em finanças, muitos resultados publicados não se confirmam quando refeitos: Harvey, Liu e Zhu (2016) concluem que a maioria dos achados declarados na área provavelmente é falsa, por causa do excesso de testes, e Hou, Xue e Zhang (2020) relatam que a maior parte das "anomalias" de mercado não resiste à replicação. As ferramentas comerciais de sentimento de notícias operam como caixa-preta. Esta pesquisa adota o caminho oposto: hipóteses e critérios registrados antes de cada teste (Nosek et al., 2018), correção para múltiplas comparações, publicação de todos os resultados, inclusive os nulos, dados congelados e um verificador que refaz todos os testes com um comando.

**Formação técnica.** O problema central é medir o atraso entre dois sinais — o sentimento das notícias e o retorno da ação —, problema clássico da eletrônica e do processamento de sinais, resolvido por correlação cruzada com defasagem (Knapp; Carter, 1976). Conceitos do curso técnico em eletrônica foram usados diretamente: taxa de amostragem (barras diárias, de 60, 5 e 1 minuto), relação sinal-ruído, piso de ruído e calibração do instrumento de medida.

---

## 3. PROBLEMA

Existe associação estatisticamente significativa entre o sentimento das notícias publicadas sobre uma empresa e o retorno da sua ação na B3? Em caso afirmativo, qual é a direção temporal dessa associação: a notícia antecede o movimento do preço (notícia → preço) ou o movimento do preço antecede a notícia (preço → notícia)?

A segunda parte do problema não é detalhe de redação. Uma correlação no mesmo dia é compatível com as duas direções, porque o dia mistura o que aconteceu antes e depois da publicação. Só o horário exato da notícia, comparado ao preço antes e depois dela, separa as duas explicações. Se a notícia antecede o preço, ler notícias dá vantagem e a hipótese de eficiência de mercado é contrariada. Se o preço antecede a notícia, a imprensa relata um movimento já ocorrido, e quem decide pela manchete chega atrasado.

---

## 4. HIPÓTESE

**Hipótese nula geral (H₀):** não existe correlação entre o sentimento das notícias e o retorno da ação na janela analisada. Formalmente, ρ = 0.

**Hipótese alternativa geral (H₁):** ρ ≠ 0.

A hipótese foi desdobrada em três famílias de testes, cada uma com sua previsão teórica:

1. Associação no mesmo dia (H1a): o sentimento do dia se correlaciona com o retorno do mesmo pregão.
2. Notícia → preço (H1b): o sentimento prevê o retorno posterior à publicação (abertura seguinte, hora seguinte, 30 minutos e 1 a 5 minutos seguintes). A hipótese de eficiência de mercado prevê que H1b não se confirme.
3. Preço → notícia (H1c): o retorno anterior à publicação (pregão passado, hora anterior, minutos anteriores) se correlaciona com o sentimento da notícia.

O nível de significância é de 5%. Os testes de direção são bicaudais; as réplicas de um efeito já conhecido (mesmo dia em 2021-2023 e nas small caps) foram unilaterais, como previsto no pré-registro. Dentro de cada família pré-registrada, os p-valores foram corrigidos pelo método de Holm (1979). A partir de 28/09/2026, o nível de significância, os critérios de inclusão, o tamanho mínimo de amostra e a regra de decisão de cada nova rodada de testes foram registrados por escrito, em documento datado e versionado, antes da execução. Desvios do plano foram declarados em adendos, e as análises decididas depois de ver os resultados foram rotuladas como exploratórias.

---

## 5. OBJETIVOS

**Objetivo geral**

Determinar se existe associação estatisticamente significativa entre o sentimento de notícias da imprensa econômica e o retorno de ações da B3, estabelecer a direção temporal dessa associação e quantificar a margem de erro da resposta, com um método que possa ser verificado por outras pessoas.

**Objetivos específicos**

1. Desenvolver um sistema de coleta automatizada de notícias financeiras e de cotações da B3, diárias e intradiárias.
2. Construir um analisador de sentimento de abordagem léxica adaptado ao vocabulário financeiro em português brasileiro.
3. Validar o módulo estatístico com dados sintéticos de resposta conhecida, antes de aplicá-lo aos dados reais.
4. Determinar o limite de detecção do método por meio de análise de poder estatístico.
5. Testar a hipótese para cada ativo em defasagens de D−5 a D+5 pregões.
6. Controlar a causalidade reversa, testando a associação entre o sentimento de um dia e o retorno do pregão anterior.
7. Testar a direção da associação com o horário exato de publicação das notícias e preços intradiários (antes e depois da abertura, hora a hora e minuto a minuto).
8. Avaliar a qualidade da medida de sentimento contra rótulos de referência e compará-la a um modelo de linguagem treinado em textos financeiros em português (FinBERT-PT-BR).
9. Replicar o resultado fora da amostra original: em outro período (2021 a 2023) e em ações de menor liquidez.
10. Tornar a pesquisa verificável: congelar os dados com impressão digital criptográfica (SHA-256), registrar todos os testes e disponibilizar um verificador que refaz todos os resultados com um comando.
11. Identificar e quantificar as limitações que restringem o alcance das conclusões.

---

## 6. REVISÃO BIBLIOGRÁFICA

**Marco teórico.** A hipótese de eficiência de mercado, na forma semiforte, afirma que o preço de um ativo incorpora toda a informação publicamente disponível (Fama, 1970). A previsão derivada para este problema é que o sentimento de uma notícia já publicada não tenha poder preditivo sobre o retorno seguinte. Em direção contrária, a literatura de sentimento do investidor sustenta que fatores psicológicos afetam preços no curto prazo, com efeito maior em ativos difíceis de avaliar (Baker; Wurgler, 2007). Tetlock (2007) mostrou que o pessimismo de uma coluna do Wall Street Journal prevê queda de preços seguida de reversão, e Barber e Odean (2008) mostraram que a pessoa física compra principalmente as ações que chamam atenção, como as que estão no noticiário.

**A direção da relação.** Granger (1969) definiu a causalidade testável — X causa Y se o passado de X melhora a previsão de Y — e alertou que uma correlação aparentemente instantânea costuma resultar de dados pouco frequentes. Na Holanda, Strauß, Vliegenthart e Verhoeven (2016) concluíram que os jornais refletem o mercado nos dias seguintes; em dados intradiários, os mesmos autores encontraram relação nos dois sentidos, mais forte em janelas de uma hora (Strauß; Vliegenthart; Verhoeven, 2018). Nos Estados Unidos, a reação a uma notícia com horário exato acontece em minutos (Busse; Green, 2002), a informação das notícias explica muito mais a volatilidade fora do pregão do que durante ele (Boudoukh et al., 2019), e investidores institucionais negociam antes da publicação (Hendershott; Livdan; Schürhoff, 2015) — o que torna o movimento de preço anterior à notícia compatível tanto com relato quanto com negociação informada.

**O caso brasileiro.** Araújo, Eleutério e Louçã (2018), com o Ibovespa de 2007 a 2015, concluíram que as variações de preço afetam mais as notícias do que o contrário. Carosia, Coelho e Silva (2021) encontraram causalidade de Granger do sentimento diário de portais brasileiros para o mercado. Souza e Martins (2024), com publicações do Twitter, acharam correlação contemporânea positiva sem relação defasada. O presente trabalho se distingue desses estudos em três aspectos: usa a imprensa econômica como fonte, usa o horário exato de publicação com preços intradiários e testa explicitamente as duas direções.

**Aparato metodológico.** O estudo de eventos segue MacKinlay (1997). A análise de poder segue Cohen (1988), e a comparação entre correlações dependentes, Steiger (1980). As múltiplas comparações foram corrigidas pelo método de Holm (1979). A concordância entre a medida de sentimento e os rótulos de referência foi avaliada pelo kappa, interpretado pela escala de Landis e Koch (1977). O modelo de linguagem usado como comparação é o FinBERT-PT-BR (Santos; Bianchi; Costa, 2023). O pré-registro segue a proposta de Nosek et al. (2018), motivada pela crise de replicação, que em finanças foi documentada por Harvey, Liu e Zhu (2016) e Hou, Xue e Zhang (2020).

---

## 7. METODOLOGIA

A pesquisa é quantitativa, de delineamento observacional, com uma parte retrospectiva (concluída) e uma parte prospectiva de confirmação (em andamento). Nenhuma intervenção foi realizada sobre o objeto: coletaram-se dados públicos e aplicou-se tratamento estatístico.

**7.1 Amostras**

- Principal: 19.410 notícias; 8 ações de 7 setores; janeiro de 2024 a setembro de 2026; estudo original e testes de direção.
- Réplica temporal: 7.291 notícias; as mesmas 8 ações; outubro de 2021 a dezembro de 2023; replicação fora do período.
- Small caps: 1.160 notícias; 8 ações sorteadas do índice SMLL; janeiro de 2024 a setembro de 2026; replicação em ações menores.
- Coleta recente: 2.537 notícias; as mesmas 8 ações; agosto a outubro de 2026; testes minuto a minuto.

Ações da amostra principal, escolhidas por liquidez e diversidade setorial: PETR4 e VALE3 (petróleo/gás e mineração), ITUB4 e BBDC4 (bancos), ABEV3 (bebidas), MGLU3 (varejo), SUZB3 (papel e celulose) e WEGE3 (bens de capital). Small caps, sorteadas com semente fixa entre as ações do índice SMLL com cobertura mínima: ASAI3, FLRY3, MDNE3, MULT3, POMO4, TAEE11, TTEN3 e VAMO3.

Fontes: notícias de um agregador público, o Google Notícias (Google, 2026); horário oficial de publicação pela interface pública (API) dos sites que usam WordPress; cotações diárias e intradiárias (barras de 60, 5 e 1 minuto) do Yahoo Finance (Yahoo, 2026), por meio de biblioteca pública; composição do índice SMLL no site da B3 (B3, 2026).

**7.2 Mensuração do sentimento**

Cada notícia recebeu um escore de −1 a +1 por um léxico de termos do vocabulário financeiro em português, construído pelos autores (medida principal). Como medida de robustez, as 29.160 manchetes únicas também foram pontuadas pelo FinBERT-PT-BR (escore = probabilidade de positivo menos probabilidade de negativo).

A qualidade das medidas foi avaliada em 300 manchetes sorteadas com semente fixa (100 de cada classe do léxico), rotuladas às cegas, sem o escore, segundo protocolo escrito. Nesta etapa preliminar, os rótulos de referência vieram de duas rodadas independentes de um anotador automático (modelo de linguagem); a rotulagem pelos dois autores, também às cegas, está em andamento e substituirá essa referência. A regra para trocar a medida principal foi fixada antes: o kappa do modelo precisaria superar o do léxico com intervalo de confiança de 95% inteiramente acima de zero.

**7.3 Horário de publicação**

O horário exato veio de duas fontes: o horário real informado pelo agregador, disponível apenas para notícias recentes, e o horário oficial obtido pela API WordPress de cada site, com a manchete localizada por similaridade de título e filtro de data. Na amostra principal, 4.998 notícias têm horário exato (4.047 pela API e 951 pelo agregador). A concordância do casamento pela API foi de 94% numa conferência manual de 100 casos. Nas notícias recentes que têm as duas fontes (n = 249), a diferença mediana foi de 0 minuto.

**7.4 Alinhamento temporal**

As defasagens foram calculadas sobre o calendário completo de pregões de cada ativo, e não sobre as linhas da tabela de sentimento. Uma auditoria do próprio código identificou que, em implementação anterior, 16,6% de 4.123 pares defasados apontavam para o pregão errado. O erro foi medido, corrigido e protegido por teste automatizado. A auditoria também encontrou um erro de fuso horário (horários em UTC tratados como horário de Brasília) em 180 notícias (0,97%); corrigido, nenhum veredito mudou.

**7.5 Retornos**

- Diário: retorno logarítmico de fechamento a fechamento.
- Decomposição: retorno overnight (fechamento anterior → abertura) e retorno do pregão (abertura → fechamento).
- Retorno anormal: pelo modelo de mercado com o Ibovespa, com parâmetros estimados antes do período das notícias; nos testes de abertura e intradiários, o retorno da ação menos a média das outras ações da amostra, porque a abertura do Ibovespa na fonte de dados se mostrou pouco confiável.

**7.6 Desenho dos testes de direção**

Em cada resolução, um teste para cada direção:

- Diária: notícia → preço = sentimento de D → retorno de D+1; preço → notícia = retorno de D−1 → sentimento de D.
- Abertura: notícia → preço = notícia da noite → abertura seguinte; preço → notícia = pregão encerrado → notícia da noite.
- 60 minutos: notícia → preço = notícia no pregão → hora seguinte; preço → notícia = hora anterior → notícia.
- 5 minutos: notícia → preço = notícia → 30 minutos seguintes; preço → notícia = 30 minutos anteriores → notícia.
- 1 minuto: notícia → preço = notícia → minutos +1 a +5; preço → notícia = minutos −5 a −1 → notícia.

Em cada resolução, a barra que contém o instante da publicação fica fora do teste, porque mistura o antes e o depois.

**7.7 Controles**

- Controle positivo: manchetes que apenas relatam o preço ("ação dispara 5%") precisam aparecer associadas ao movimento anterior; se não aparecessem, o método estaria cego.
- Falsificação: o mesmo teste com o dia errado precisa dar nulo.
- Placebo entre empresas: o sentimento de uma empresa contra o retorno de outra precisa dar menor que contra o da própria.
- Calibração: os testes foram rodados 60 vezes com o sentimento embaralhado; a taxa de falsos positivos precisa ficar perto de 5%.
- Validação com dados sintéticos: 1.000 séries de resposta conhecida antes de qualquer dado real.

**7.8 Critérios de inclusão**

Mínimo de 60 observações pareadas por ativo nos testes por ativo, definido pela análise de poder (seção 9). Nos testes agrupados, o menor efeito detectável foi calculado e declarado antes de cada teste.

**7.9 Pré-registro e verificabilidade**

A partir de 28/09/2026, cada rodada de testes teve um documento de pré-registro datado e versionado em repositório git antes da execução (10 pré-registros e 4 adendos). Para que os resultados possam ser conferidos:

1. Dados congelados: os 75 arquivos de dados usados foram congelados em 02/10/2026, e a impressão digital SHA-256 de cada um foi publicada no repositório. Qualquer alteração de um único byte muda a impressão digital. O pacote de dados não fica público, porque contém textos e preços de terceiros; ele é entregue a quem pedir, e a impressão digital permite provar que é o mesmo usado no estudo.
2. Verificador de um comando: um programa refaz as 32 etapas de análise a partir dos dados congelados, sem acesso à internet e com o relógio do computador fixado, e compara cada resultado com a referência.
3. Reprodução em máquinas diferentes: a verificação completa foi executada num servidor Linux e no computador Windows 11 de um dos autores, com versões diferentes do Python (3.11 e 3.14) e de todas as bibliotecas de cálculo. As 99 saídas conferiram com a referência nas duas máquinas.
4. Registro de testes: uma tabela lista todos os testes feitos, com data, pré-registro, tipo (confirmatório, secundário, exploratório ou calibração), estatística e decisão, inclusive os nulos.

**7.10 Confirmação prospectiva (em andamento)**

Como a fonte só guarda 30 dias de barras de 1 minuto e só informa o horário real das notícias recentes, uma coleta diária automática começou em 02/10/2026. A regra de parada foi fixada antes de existir qualquer dado novo: 1.500 eventos ou 30/06/2027, o que vier primeiro. Os testes confirmatórios (notícia → 30 minutos e 1 a 5 minutos seguintes; 30 minutos e 5 minutos anteriores → notícia) só serão calculados ao atingir a regra.

---

## 8. CRONOGRAMA

- Revisão bibliográfica e definição do problema: primeiro semestre de 2026
- Construção do sistema de coleta de notícias e cotações: primeiro semestre de 2026
- Construção e calibração do léxico de sentimento: primeiro semestre de 2026
- Implementação do módulo estatístico: julho a setembro de 2026
- Validação com dados sintéticos e análise de poder: setembro de 2026
- Coleta final e testes de hipótese do estudo original: setembro de 2026
- Auditoria do alinhamento temporal, controle D−1 e curva de defasagem: setembro de 2026
- Auditoria de fuso horário, testes de robustez e réplica 2021-2023: outubro de 2026
- Revisão da literatura sobre direção e testes com horário exato: outubro de 2026
- Validação da medida de sentimento e comparação com o FinBERT-PT-BR: outubro de 2026
- Testes minuto a minuto e réplica em small caps: outubro de 2026
- Congelamento dos dados e verificador: outubro de 2026
- Redação do relatório e preparação da apresentação: outubro de 2026
- Coleta prospectiva de confirmação: outubro de 2026 a junho de 2027 (ou 1.500 eventos)

---

## 9. ANÁLISE DE DADOS

**Estatística principal.** A associação foi medida pelo coeficiente de correlação de Pearson (r) e, nos testes agrupados, pela correlação parcial com controles, reunindo todos os ativos. Nenhum r foi interpretado sozinho.

**Teste de permutação.** O p-valor de cada teste foi obtido por permutação (10.000 repetições, semente fixa), sem supor normalidade. Nos testes agrupados, as permutações sorteiam blocos de datas, preservando a correlação entre ações no mesmo dia; nos testes intradiários, cada evento recebe o retorno do mesmo horário em outro dia sorteado.

**Correções e poder.** Holm (1979) dentro de cada família pré-registrada. Para cada teste, o menor efeito detectável com poder de 80% foi calculado antes (Cohen, 1988). No estudo original, o mínimo de 60 observações por ativo elevou o poder teórico de 32% (com 20 observações) para 80%. A comparação entre correlações dependentes seguiu Steiger (1980).

**Qualidade da medida.** Kappa de Cohen reponderado para a população, com intervalo de confiança por bootstrap pareado (10.000 reamostragens).

**Resultados**

1. A associação do mesmo dia existe e é da própria empresa. No estudo original, a hipótese nula foi rejeitada no mesmo pregão (D+0) em 6 dos 8 ativos (r de 0,10 a 0,20), e em nenhum ativo no pregão seguinte (D+1). A curva de defasagem tem pico em D+0 (r = 0,131) e valor intermediário em D−1 (0,060). A associação sobrevive ao desconto do Ibovespa (r = 0,109; p = 0,0001), é maior com a própria empresa do que com as outras (placebo, p = 0,0001) e se repete em 2021-2023 (r = 0,077; p de Holm = 0,002) e nas small caps (r = 0,213; p de Holm = 0,0004).

2. Com horário exato, o preço se move antes da notícia. Com 4.998 notícias com horário: o sentimento das notícias publicadas à noite acompanha o pregão que acabou de fechar (r = 0,083; p = 0,001; n = 1.642); o das notícias publicadas durante o pregão acompanha a hora anterior (r = 0,091; p = 0,003; n = 1.155); os dois continuam significativos com a correção de Holm dentro dessa análise (p = 0,004 e 0,009), que foi declarada num adendo antes de rodar, porque a análise principal, só com os horários do agregador, tinha pouco poder (n ≈ 190 a 254) e não passou na correção. Em análise exploratória, o movimento da abertura até a hora da notícia acompanha o sentimento (r = 0,159; p = 0,0001), e o movimento depois dela, não (r = 0,040; p = 0,19).

3. A notícia não antecipa o preço. A notícia do dia não prevê a abertura seguinte (r = 0,011; n = 4.047, com poder para detectar r = 0,044); a da noite também não (r = 0,013; p = 0,59), nem a do pregão prevê a hora seguinte (r = 0,036; p = 0,23). Em barras de 5 e de 1 minuto, nenhuma reação foi detectada nos 30 minutos nem nos 1 a 5 minutos após a publicação (por exemplo, minutos +1 a +5: r = −0,023; p = 0,62; n = 469).

4. A conclusão não depende da medida de sentimento. Contra os rótulos de referência preliminares, o léxico teve kappa reponderado de 0,30 (concordância razoável) e o FinBERT-PT-BR, 0,44 (moderada). A diferença não passou na regra pré-registrada (intervalo de −0,01 a +0,28), e o léxico foi mantido. Com o FinBERT, a réplica de 2021-2023 continua significativa (p de Holm = 0,005), a notícia da noite continua acompanhando o pregão passado (p = 0,012) e a notícia continua sem prever o preço.

5. Os controles funcionaram. As manchetes de relato acompanham o pregão passado (r = 0,36; p = 0,02); os testes com o dia errado deram nulos; a taxa de falsos positivos com sentimento embaralhado ficou entre 0% e 8% por teste, compatível com os 5% nominais.

6. Verificação. O verificador refez as 32 etapas de análise a partir dos dados congelados, num servidor Linux e no computador Windows de um dos autores. As 99 saídas conferiram nas duas máquinas: todos os resultados em texto saíram idênticos, letra por letra; nas tabelas com números de precisão completa, a maior diferença ficou na 14ª casa significativa (arredondamento do computador). A referência também foi comparada com os resultados publicados antes do congelamento: 44 de 47 arquivos idênticos e 3 com diferença na 4ª casa decimal de alguns p-valores, causada pela atualização do arquivo de preços, sem mudança de nenhuma conclusão. O registro de testes lista 279 resultados, inclusive os nulos.

**Conclusão.** A associação entre o sentimento das notícias e o retorno existe, é da própria empresa e se repete em outro período e em outras ações. Mas a direção que os dados mostram é preço → notícia: quando a matéria de imprensa é publicada, o preço já se moveu, e a matéria não antecipa o movimento seguinte. O resultado é coerente com a hipótese de eficiência de mercado (Fama, 1970) e com o estudo brasileiro mais próximo (Araújo; Eleutério; Louçã, 2018). Trata-se de evidência consistente de precedência temporal, não de prova definitiva: nenhum estudo observacional prova causalidade.

**Limitações**

- Poder: efeitos menores que o menor efeito detectável de cada teste (r de 0,04 a 0,13, conforme o teste) não podem ser descartados. "Não detectado" não significa "zero".
- Horário: o horário do agregador pode atrasar em notícias antigas; por isso 80% dos horários vieram da API dos próprios sites. O casamento pela API tem cerca de 6% de erro.
- Medida: o léxico é ruidoso (kappa 0,30), o que enfraquece as correlações nos dois sentidos; a rotulagem humana está em andamento.
- Resolução: abaixo de 1 minuto a fonte não tem dados.
- Preço antes da notícia pode ser relato do jornalista ou negociação informada antes da publicação; os dados não separam as duas coisas.
- Efeito causal da mídia em si (a reportagem movendo o preço independentemente da informação) exige experimento natural e não é testável com estes dados.

---

## 10. REFERÊNCIAS

ANBIMA. **Raio X do Investidor Brasileiro**. 9. ed. São Paulo: ANBIMA; Datafolha, 2026. Disponível em: https://www.anbima.com.br/data/files/BE/05/B0/55/1EABD91008E6DAD9F82BA2A8/Raio-X-do-Investidor-9-edicao.pdf. Acesso em: 2 out. 2026.

ARAÚJO, T.; ELEUTÉRIO, S.; LOUÇÃ, F. Do sentiments influence market dynamics? A reconstruction of the Brazilian stock market and its mood. **Physica A**, v. 505, p. 1139-1149, 2018. Disponível em: https://doi.org/10.1016/j.physa.2018.04.045. Acesso em: 2 out. 2026.

B3. **A descoberta da bolsa pelo investidor brasileiro**. São Paulo: B3, dez. 2020. Disponível em: https://www.b3.com.br/data/files/69/75/42/A0/36ECA71068C61CA7AC094EA8/Pesquisa%20PF_vf%20_dez.20_.pdf. Acesso em: 2 out. 2026.

B3. **Pessoas físicas**: uma análise da evolução dos investidores na B3 — 2º trimestre de 2025. São Paulo: B3, 2025. Disponível em: https://www.b3.com.br/data/files/A2/A0/78/20/E61689100A29E189AC094EA8/Book%20PF%202TRI%202025_vF.pdf. Acesso em: 2 out. 2026.

B3. **Índice Small Cap (SMLL B3)**: composição da carteira. São Paulo: B3, 2026. Disponível em: https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/indice-small-cap-smll-composicao-da-carteira.htm. Acesso em: 2 out. 2026.

BAKER, M.; WURGLER, J. Investor sentiment in the stock market. **Journal of Economic Perspectives**, v. 21, n. 2, p. 129-151, 2007. Disponível em: https://doi.org/10.1257/jep.21.2.129. Acesso em: 2 out. 2026.

BARBER, B. M.; ODEAN, T. All that glitters: the effect of attention and news on the buying behavior of individual and institutional investors. **The Review of Financial Studies**, v. 21, n. 2, p. 785-818, 2008. Disponível em: https://doi.org/10.1093/rfs/hhm079. Acesso em: 2 out. 2026.

BOUDOUKH, J.; FELDMAN, R.; KOGAN, S.; RICHARDSON, M. Information, trading, and volatility: evidence from firm-specific news. **The Review of Financial Studies**, v. 32, n. 3, p. 992-1033, 2019. Disponível em: https://doi.org/10.1093/rfs/hhy083. Acesso em: 2 out. 2026.

BUSSE, J. A.; GREEN, T. C. Market efficiency in real time. **Journal of Financial Economics**, v. 65, n. 3, p. 415-437, 2002. Disponível em: https://doi.org/10.1016/S0304-405X(02)00148-4. Acesso em: 2 out. 2026.

CAROSIA, A. E. O.; COELHO, G. P.; SILVA, A. E. A. Investment strategies applied to the Brazilian stock market: a methodology based on sentiment analysis with deep learning. **Expert Systems with Applications**, v. 184, art. 115470, 2021. Disponível em: https://doi.org/10.1016/j.eswa.2021.115470. Acesso em: 2 out. 2026.

CHAGUE, F.; DE-LOSSO, R.; GIOVANNETTI, B. **Day trading for a living?** SSRN, 2020. Working paper. Disponível em: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101. Acesso em: 2 out. 2026.

COHEN, J. **Statistical power analysis for the behavioral sciences**. 2. ed. Hillsdale: Lawrence Erlbaum Associates, 1988. Disponível em: https://doi.org/10.4324/9780203771587. Acesso em: 2 out. 2026.

COMISSÃO DE VALORES MOBILIÁRIOS (CVM). **Resolução CVM nº 44, de 23 de agosto de 2021**. Dispõe sobre divulgação de ato ou fato relevante, negociação de valores mobiliários na pendência de informação não divulgada e divulgação sobre negociações de valores mobiliários. Brasília, DF: CVM, 2021. Disponível em: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol044consolid.pdf. Acesso em: 3 out. 2026.

FAMA, E. F. Efficient capital markets: a review of theory and empirical work. **The Journal of Finance**, v. 25, n. 2, p. 383-417, 1970. Disponível em: https://doi.org/10.2307/2325486. Acesso em: 2 out. 2026.

GOOGLE. **Google Notícias**. 2026. Disponível em: https://news.google.com. Acesso em: 2 out. 2026.

GRANGER, C. W. J. Investigating causal relations by econometric models and cross-spectral methods. **Econometrica**, v. 37, n. 3, p. 424-438, 1969. Disponível em: https://doi.org/10.2307/1912791. Acesso em: 2 out. 2026.

HARVEY, C. R.; LIU, Y.; ZHU, H. ... and the cross-section of expected returns. **The Review of Financial Studies**, v. 29, n. 1, p. 5-68, 2016. Disponível em: https://doi.org/10.1093/rfs/hhv059. Acesso em: 2 out. 2026.

HENDERSHOTT, T.; LIVDAN, D.; SCHÜRHOFF, N. Are institutions informed about news? **Journal of Financial Economics**, v. 117, n. 2, p. 249-287, 2015. Disponível em: https://doi.org/10.1016/j.jfineco.2015.03.007. Acesso em: 2 out. 2026.

HOLM, S. A simple sequentially rejective multiple test procedure. **Scandinavian Journal of Statistics**, v. 6, n. 2, p. 65-70, 1979. Disponível em: https://www.jstor.org/stable/4615733. Acesso em: 2 out. 2026.

HOU, K.; XUE, C.; ZHANG, L. Replicating anomalies. **The Review of Financial Studies**, v. 33, n. 5, p. 2019-2133, 2020. Disponível em: https://doi.org/10.1093/rfs/hhy131. Acesso em: 2 out. 2026.

KNAPP, C. H.; CARTER, G. C. The generalized correlation method for estimation of time delay. **IEEE Transactions on Acoustics, Speech, and Signal Processing**, v. 24, n. 4, p. 320-327, 1976. Disponível em: https://doi.org/10.1109/TASSP.1976.1162830. Acesso em: 2 out. 2026.

LANDIS, J. R.; KOCH, G. G. The measurement of observer agreement for categorical data. **Biometrics**, v. 33, n. 1, p. 159-174, 1977. Disponível em: https://doi.org/10.2307/2529310. Acesso em: 2 out. 2026.

MACKINLAY, A. C. Event studies in economics and finance. **Journal of Economic Literature**, v. 35, n. 1, p. 13-39, 1997. Disponível em: https://www.jstor.org/stable/2729691. Acesso em: 3 out. 2026.

NOSEK, B. A.; EBERSOLE, C. R.; DEHAVEN, A. C.; MELLOR, D. T. The preregistration revolution. **Proceedings of the National Academy of Sciences**, v. 115, n. 11, p. 2600-2606, 2018. Disponível em: https://doi.org/10.1073/pnas.1708274114. Acesso em: 2 out. 2026.

SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de sentimentos de textos em português do mercado financeiro. In: BRAZILIAN WORKSHOP ON ARTIFICIAL INTELLIGENCE IN FINANCE, 2., 2023, João Pessoa. **Anais** [...]. Porto Alegre: Sociedade Brasileira de Computação, 2023. p. 144-155. Disponível em: https://doi.org/10.5753/bwaif.2023.231151. Acesso em: 2 out. 2026.

SOUZA, D. M. S. de; MARTINS, O. S. Brazilian stock market performance and investor sentiment on Twitter. **Revista de Gestão**, v. 31, n. 1, p. 18-33, 2024. Disponível em: https://doi.org/10.1108/REGE-07-2021-0145. Acesso em: 2 out. 2026.

STEIGER, J. H. Tests for comparing elements of a correlation matrix. **Psychological Bulletin**, v. 87, n. 2, p. 245-251, 1980. Disponível em: https://doi.org/10.1037/0033-2909.87.2.245. Acesso em: 3 out. 2026.

STRAUß, N.; VLIEGENTHART, R.; VERHOEVEN, P. Lagging behind? Emotions in newspaper articles and stock market prices in the Netherlands. **Public Relations Review**, v. 42, n. 4, p. 548-555, 2016. Disponível em: https://doi.org/10.1016/j.pubrev.2016.03.010. Acesso em: 2 out. 2026.

STRAUß, N.; VLIEGENTHART, R.; VERHOEVEN, P. Intraday news trading: the reciprocal relationships between the stock market and economic news. **Communication Research**, v. 45, n. 7, p. 1054-1077, 2018. Disponível em: https://doi.org/10.1177/0093650217705528. Acesso em: 2 out. 2026.

TETLOCK, P. C. Giving content to investor sentiment: the role of media in the stock market. **The Journal of Finance**, v. 62, n. 3, p. 1139-1168, 2007. Disponível em: https://doi.org/10.1111/j.1540-6261.2007.01232.x. Acesso em: 2 out. 2026.

YAHOO. **Yahoo Finance**. 2026. Disponível em: https://finance.yahoo.com. Acesso em: 2 out. 2026.

---

## Notas (não copiar)

**O que mudou da versão 2 (02/10) para esta (03/10):**

- Citações no formato da NBR 10520:2023, igual ao vídeo: sobrenome com só a
  inicial maiúscula também dentro dos parênteses, como "(Fama, 1970)".
- Todas as referências com link ("Disponível em"), no lugar do DOI. Os links
  novos foram conferidos: Baker e Wurgler, Fama e Steiger no Crossref ou no
  OpenAlex; Holm e MacKinlay no JSTOR; Resolução CVM 44 no texto consolidado
  do site da CVM (a ementa agora está igual à oficial).
- Justificativa: saiu o número intermediário de 2020 ("cerca de 3,2
  milhões"), que não batia com a leitura do relatório da B3; ficou 583 mil
  (2011) → 5,4 milhões (2025), igual ao vídeo. Os 73% (B3, 2020) e os canais
  da ANBIMA (2026) foram conferidos.
- Metodologia: as fontes de dados agora têm citação (Google, Yahoo e B3), e
  essas três obras entraram nas referências (agora são 31).
- 7.9: diz que o pacote de dados é entregue a quem pedir (igual ao slide 17).
- 7.10: a coleta diária começou em 02/10/2026 (o log do PC confirma a
  primeira rodada às 19h40).
- Objetivo geral: "qualquer pessoa possa verificar" virou "possa ser
  verificado por outras pessoas", pelo mesmo motivo do 7.9.
- Tabelas viraram listas, para colar em campo de formulário.

**Cronograma:** as seis primeiras etapas foram datadas pelo Caderno de Campo
(assinado em julho de 2026) e pelas datas dos arquivos do projeto (notícias do
estudo original até 06/09/2026; validação sintética e análise de poder em
06/09/2026).
