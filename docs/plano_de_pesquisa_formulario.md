# Plano de pesquisa — versão para o formulário da MOSTRATEC (03/10/2026)

Cada campo cabe no limite do formulário (caracteres com espaços). A versão completa, com 31 referências, está em `plano_de_pesquisa_v3.md`.

Título: SENTIMENTO DE NOTÍCIAS E RETORNO DE AÇÕES: análise de risco de carteiras na bolsa brasileira

---

## 1. TEMA (442 de 500 caracteres)

A relação entre o sentimento das notícias da imprensa econômica e o retorno de ações da B3 e a direção temporal dessa relação: quem se move primeiro, o preço ou a notícia. O recorte abrange oito ações de sete setores, de 2024 a 2026, com dados diários e intradiários (barras de 60, 5 e 1 minuto), e réplicas em 2021-2023 e em oito ações de menor liquidez. Ficam fora mercados estrangeiros, redes sociais e qualquer estratégia de investimento.

---

## 2. JUSTIFICATIVA (1693 de 2000 caracteres)

Social. O número de investidores pessoa física na B3 passou de 583 mil, em 2011 (B3, 2020), para 5,4 milhões no segundo trimestre de 2025 (B3, 2025), e 73% dos investidores entrevistados pela B3 (2020) disseram se informar sobre investimentos pela internet. A pessoa física tende a comprar as ações que estão no noticiário (Barber; Odean, 2008). A pergunta prática é direta: quem decide pela manchete está à frente ou atrás do preço?

Científica. Duas teorias fazem previsões opostas. A hipótese de eficiência de mercado prevê que, quando a notícia pública sai, o preço já se ajustou (Fama, 1970); a literatura de sentimento do investidor prevê que o humor do mercado move os preços no curto prazo (Baker; Wurgler, 2007). A forma de decidir entre elas é a ordem no tempo: a causa precisa vir antes do efeito (Granger, 1969). O estudo brasileiro mais próximo usou dados diários (Araújo; Eleutério; Louçã, 2018), e, nas bases consultadas, não encontramos estudo que use o horário exato de publicação de matérias da imprensa e preços intradiários de ações da B3 para testar a direção.

Metodológica. A pesquisa registra hipóteses e critérios por escrito antes de cada teste, corrige os resultados para múltiplas comparações, publica todos os resultados, inclusive os nulos, e permite refazer todos os testes a partir de dados congelados.

Formação técnica. O problema central é medir o atraso entre dois sinais, o sentimento das notícias e o retorno da ação, por correlação cruzada com defasagem, ferramenta do processamento de sinais. Conceitos do curso técnico em eletrônica foram usados diretamente: taxa de amostragem, relação sinal-ruído, piso de ruído e calibração do instrumento de medida.

---

## 3. PROBLEMA (836 de 4000 caracteres)

Existe associação estatisticamente significativa entre o sentimento das notícias publicadas sobre uma empresa e o retorno da sua ação na B3? Em caso afirmativo, qual é a direção temporal dessa associação: a notícia antecede o movimento do preço (notícia → preço) ou o movimento do preço antecede a notícia (preço → notícia)?

A segunda parte do problema não é detalhe de redação. Uma correlação no mesmo dia é compatível com as duas direções, porque o dia mistura o que aconteceu antes e depois da publicação. Só o horário exato da notícia, comparado ao preço antes e depois dela, separa as duas explicações. Se a notícia antecede o preço, ler notícias dá vantagem e a hipótese de eficiência de mercado é contrariada. Se o preço antecede a notícia, a imprensa relata um movimento já ocorrido, e quem decide pela manchete chega atrasado.

---

## 4. HIPÓTESES (1418 de 2000 caracteres)

Hipótese nula geral (H₀): não existe correlação entre o sentimento das notícias e o retorno da ação na janela analisada. Formalmente, ρ = 0.

Hipótese alternativa geral (H₁): ρ ≠ 0.

A hipótese foi desdobrada em três famílias de testes, cada uma com sua previsão teórica:

1. Associação no mesmo dia (H1a): o sentimento do dia se correlaciona com o retorno do mesmo pregão.
2. Notícia → preço (H1b): o sentimento prevê o retorno posterior à publicação (abertura seguinte, hora seguinte, 30 minutos e 1 a 5 minutos seguintes). A hipótese de eficiência de mercado prevê que H1b não se confirme.
3. Preço → notícia (H1c): o retorno anterior à publicação (pregão passado, hora anterior, minutos anteriores) se correlaciona com o sentimento da notícia.

O nível de significância é de 5%. Os testes de direção são bicaudais; as réplicas de um efeito já conhecido (mesmo dia em 2021-2023 e nas small caps) foram unilaterais, como previsto no pré-registro. Dentro de cada família pré-registrada, os p-valores foram corrigidos pelo método de Holm (1979). A partir de 28/09/2026, o nível de significância, os critérios de inclusão, o tamanho mínimo de amostra e a regra de decisão de cada nova rodada de testes foram registrados por escrito, em documento datado e versionado, antes da execução. Desvios do plano foram declarados em adendos, e as análises decididas depois de ver os resultados foram rotuladas como exploratórias.

---

## 5. OBJETIVOS (1703 de 2000 caracteres)

Objetivo geral: determinar se existe associação estatisticamente significativa entre o sentimento de notícias da imprensa econômica e o retorno de ações da B3, estabelecer a direção temporal dessa associação e quantificar a margem de erro da resposta, com um método que possa ser verificado por outras pessoas.

Objetivos específicos:
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

## 5b. OBJETOS (1281 de 2000 caracteres)

Objeto: a associação estatística entre o sentimento (tom positivo ou negativo) das notícias da imprensa econômica e o retorno de ações da B3, e a direção temporal dessa associação, isto é, se a notícia antecede o movimento do preço ou se o preço se move antes da notícia.

O que será feito: coletar notícias e cotações diárias e intradiárias de oito ações de sete setores (2024 a 2026), medir o sentimento de cada notícia com um léxico financeiro em português, alinhar cada notícia ao seu horário exato de publicação e testar, com métodos estatísticos e regras registradas antes de cada teste, a correlação entre o sentimento e o retorno antes e depois da publicação.

Classificação: pesquisa científica, quantitativa e observacional. O trabalho busca responder a uma pergunta sobre um fenômeno (quem vem primeiro, a notícia ou o preço), e não desenvolver um produto. O sistema de coleta e análise construído pelos autores é o instrumento de medida, não o objeto do estudo.

Área: Ciências da Computação, com aplicação em finanças: coleta automatizada de dados, processamento de linguagem natural (análise de sentimento) e análise estatística de séries temporais.

Fora do objeto: mercados estrangeiros, redes sociais como fonte de sentimento e qualquer estratégia de investimento.

---

## 6. REVISÃO BIBLIOGRÁFICA (1632 de 2000 caracteres)

Marco teórico. A hipótese de eficiência de mercado, na forma semiforte, afirma que o preço de um ativo incorpora toda a informação publicamente disponível (Fama, 1970). Para este problema, a previsão é que o sentimento de uma notícia já publicada não preveja o retorno seguinte. Em direção contrária, a literatura de sentimento do investidor sustenta que fatores psicológicos afetam preços no curto prazo, com efeito maior em ativos difíceis de avaliar (Baker; Wurgler, 2007), e Barber e Odean (2008) mostraram que a pessoa física compra principalmente as ações que chamam atenção, como as que estão no noticiário.

A direção da relação. Granger (1969) definiu a causalidade testável: X causa Y se o passado de X melhora a previsão de Y. Ele também alertou que uma correlação aparentemente instantânea costuma resultar de dados pouco frequentes, o que justifica usar dados intradiários.

O caso brasileiro. Araújo, Eleutério e Louçã (2018), com o Ibovespa de 2007 a 2015 e dados diários, concluíram que as variações de preço afetam mais as notícias do que o contrário. Nas bases consultadas (Crossref, OpenAlex, OpenAIRE e DOAJ), não encontramos estudo brasileiro com o horário exato de publicação de matérias da imprensa e preços intradiários. Este trabalho se distingue por usar a imprensa econômica como fonte e o horário exato de publicação com preços intradiários, e por testar explicitamente as duas direções.

Aparato metodológico. As múltiplas comparações foram corrigidas pelo método de Holm (1979). A medida de sentimento foi comparada a um modelo de linguagem treinado em textos financeiros em português, o FinBERT-PT-BR.

---

## 7. METODOLOGIA (1794 de 2000 caracteres)

Pesquisa quantitativa e observacional, com parte retrospectiva (concluída) e confirmação prospectiva (em andamento).

Amostras: 19.410 notícias sobre oito ações de sete setores (PETR4, VALE3, ITUB4, BBDC4, ABEV3, MGLU3, SUZB3 e WEGE3), de janeiro de 2024 a setembro de 2026; réplicas com 7.291 notícias de 2021 a 2023 e 1.160 notícias de oito ações do índice SMLL. Notícias do Google Notícias; cotações diárias e intradiárias (60, 5 e 1 minuto) do Yahoo Finance.

Sentimento: escore de −1 a +1 por um léxico financeiro em português construído pelos autores, validado em 300 manchetes rotuladas às cegas e comparado ao FinBERT-PT-BR.

Horário: 4.998 notícias com horário exato, obtido do agregador e da API pública dos sites (WordPress).

Testes de direção: em cada resolução, o sentimento é comparado com o retorno depois da publicação (notícia → preço) e antes dela (preço → notícia): pregão anterior e abertura seguinte, hora anterior e seguinte, 30 minutos e 1 a 5 minutos antes e depois. A barra que contém a publicação fica fora do teste. Os retornos são descontados do Ibovespa ou da média das outras ações. Nos testes por ativo, o mínimo é de 60 observações, definido por análise de poder.

Controles: manchetes que só relatam o preço (controle positivo), dia errado (falsificação), placebo entre empresas, calibração com sentimento embaralhado e 1.000 séries sintéticas.

Pré-registro e verificação: desde 28/09/2026, cada rodada de testes foi registrada por escrito antes de rodar (10 pré-registros e 4 adendos). Os dados foram congelados com impressão digital SHA-256, e um verificador refaz as 32 etapas da análise; as 99 saídas conferiram em Linux e em Windows.

Confirmação prospectiva: coleta diária desde 02/10/2026, com regra de parada fixada antes: 1.500 eventos ou 30/06/2027.

---

## 8. CRONOGRAMA (1063 de 2000 caracteres)

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

## 9. ANÁLISE DE DADOS (3190 de 4000 caracteres)

Estatística principal. A associação foi medida pelo coeficiente de correlação de Pearson (r) e, nos testes agrupados, pela correlação parcial com controles, reunindo todos os ativos.

Teste de permutação. O p-valor de cada teste foi obtido por permutação (10.000 repetições, semente fixa), sem supor normalidade. Nos testes agrupados, as permutações sorteiam blocos de datas, preservando a correlação entre ações no mesmo dia; nos intradiários, cada evento recebe o retorno do mesmo horário em outro dia sorteado.

Correções e poder. Holm (1979) dentro de cada família pré-registrada. Para cada teste, o menor efeito detectável com poder de 80% foi calculado antes. A qualidade da medida foi avaliada pelo kappa reponderado, com intervalo de confiança por bootstrap (10.000 reamostragens).

Resultados
1. A associação do mesmo dia existe e é da própria empresa: a hipótese nula foi rejeitada no mesmo pregão (D+0) em 6 dos 8 ativos (r de 0,10 a 0,20) e em nenhum no pregão seguinte (D+1); a curva de defasagem tem pico em D+0 (r = 0,131). A associação sobrevive ao desconto do Ibovespa (r = 0,109; p = 0,0001), é maior com a própria empresa do que com as outras (placebo, p = 0,0001) e se repete em 2021-2023 (r = 0,077; p de Holm = 0,002) e nas small caps (r = 0,213; p de Holm = 0,0004).
2. Com horário exato, o preço se move antes da notícia: o sentimento das notícias da noite acompanha o pregão que acabou de fechar (r = 0,083; p = 0,001; n = 1.642), e o das notícias do pregão acompanha a hora anterior (r = 0,091; p = 0,003; n = 1.155); os dois continuam significativos com a correção de Holm (p = 0,004 e 0,009).
3. A notícia não antecipa o preço: não prevê a abertura seguinte (r = 0,011; n = 4.047) nem a hora seguinte (r = 0,036; p = 0,23), e nenhuma reação foi detectada nos 30 minutos nem nos 1 a 5 minutos após a publicação (minutos +1 a +5: r = −0,023; p = 0,62; n = 469).
4. A conclusão não depende da medida: o léxico teve kappa de 0,30 e o FinBERT-PT-BR, 0,44, diferença que não passou na regra pré-registrada; com o FinBERT, as conclusões se mantêm.
5. Os controles funcionaram: manchetes de relato acompanham o pregão passado (r = 0,36; p = 0,02), testes com o dia errado deram nulos e a taxa de falsos positivos ficou compatível com 5%.
6. O verificador refez as 32 etapas a partir dos dados congelados; as 99 saídas conferiram em Linux e em Windows. O registro lista 279 resultados, inclusive os nulos.

Conclusão. A associação existe, é da própria empresa e se repete em outro período e em outras ações, mas a direção que os dados mostram é preço → notícia: quando a matéria é publicada, o preço já se moveu. O resultado é coerente com a hipótese de eficiência de mercado (Fama, 1970) e com Araújo, Eleutério e Louçã (2018). É evidência de precedência temporal, não prova de causalidade.

Limitações. Efeitos menores que o menor detectável (r de 0,04 a 0,13) não podem ser descartados; o casamento de horários pela API tem cerca de 6% de erro; o léxico é ruidoso (kappa 0,30) e a rotulagem humana está em andamento; abaixo de 1 minuto não há dados; o preço antes da notícia pode ser relato do jornalista ou negociação informada, e os dados não separam as duas coisas.

---

## 10. REFERÊNCIAS (1859 de 2000 caracteres)

ARAÚJO, T.; ELEUTÉRIO, S.; LOUÇÃ, F. Do sentiments influence market dynamics? A reconstruction of the Brazilian stock market and its mood. Physica A, v. 505, p. 1139-1149, 2018. Disponível em: https://doi.org/10.1016/j.physa.2018.04.045. Acesso em: 2 out. 2026.

B3. A descoberta da bolsa pelo investidor brasileiro. São Paulo: B3, dez. 2020. Disponível em: https://www.b3.com.br/data/files/69/75/42/A0/36ECA71068C61CA7AC094EA8/Pesquisa%20PF_vf%20_dez.20_.pdf. Acesso em: 2 out. 2026.

B3. Pessoas físicas: uma análise da evolução dos investidores na B3 — 2º trimestre de 2025. São Paulo: B3, 2025. Disponível em: https://www.b3.com.br/data/files/A2/A0/78/20/E61689100A29E189AC094EA8/Book%20PF%202TRI%202025_vF.pdf. Acesso em: 2 out. 2026.

BAKER, M.; WURGLER, J. Investor sentiment in the stock market. Journal of Economic Perspectives, v. 21, n. 2, p. 129-151, 2007. Disponível em: https://doi.org/10.1257/jep.21.2.129. Acesso em: 2 out. 2026.

BARBER, B. M.; ODEAN, T. All that glitters: the effect of attention and news on the buying behavior of individual and institutional investors. The Review of Financial Studies, v. 21, n. 2, p. 785-818, 2008. Disponível em: https://doi.org/10.1093/rfs/hhm079. Acesso em: 2 out. 2026.

FAMA, E. F. Efficient capital markets: a review of theory and empirical work. The Journal of Finance, v. 25, n. 2, p. 383-417, 1970. Disponível em: https://doi.org/10.2307/2325486. Acesso em: 2 out. 2026.

GRANGER, C. W. J. Investigating causal relations by econometric models and cross-spectral methods. Econometrica, v. 37, n. 3, p. 424-438, 1969. Disponível em: https://doi.org/10.2307/1912791. Acesso em: 2 out. 2026.

HOLM, S. A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics, v. 6, n. 2, p. 65-70, 1979. Disponível em: https://www.jstor.org/stable/4615733. Acesso em: 2 out. 2026.

---

## Notas (não copiar)

- O limite de 2.000 caracteres das referências comporta 8 obras com link. Por isso o texto cita só essas 8; as outras 23 continuam no plano completo (v3).
- Google Notícias, Yahoo Finance, WordPress e FinBERT-PT-BR aparecem como nomes de ferramentas e fontes de dados, sem citação, porque as referências deles não cabem no limite.
- Cronograma: as seis primeiras etapas foram datadas pelo Caderno de Campo (assinado em julho de 2026, que descreve a coleta, o léxico e o Seminário I com "3 meses de trabalho") e pelas datas dos arquivos (notícias do estudo original até 06/09/2026; scripts de validação sintética e análise de poder de 06/09/2026). O módulo estatístico não aparece no caderno de julho e já existia em 06/09, por isso "julho a setembro".
