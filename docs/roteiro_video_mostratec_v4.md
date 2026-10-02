# Roteiro do vídeo — MOSTRATEC 2026 (versão 4, citações em ABNT)

**Até 5 minutos · horizontal · mínimo 480p / 30 fps · YouTube não listado**

- **[L]** = Leonardo · **[M]** = Maurício · **`[slide N]`** = o slide de fundo que entra nessa fala
  (arquivo `slides_fundo_video.pdf`, 22 slides; a imagem de vocês fica no canto inferior direito).
- **Ordem obrigatória** (recomendações oficiais da MOSTRATEC):
  1. apresentação (alunos, orientador, escola, estado);
  2. introdução (justificativa, problema, hipóteses, objetivos);
  3. fundamentação e metodologia;
  4. resultados e discussão.
- **Tempo:** cerca de 675 palavras faladas. Com os anos das citações, que
  demoram mais para falar, dá entre **4min30 e 4min45** em ritmo normal, mais uns
  **8 segundos** dos dois slides de referências no fim. **Cronometrem o
  primeiro take.**
- **Se passar de 4min50**, cortem nesta ordem até caber:
  1. a frase opcional do bloco 1, se estiverem usando;
  2. "Duas teorias dão respostas opostas." (slide 7; o título do slide já diz isso);
  3. a frase da verificação (slide 17; o slide continua na tela, sem fala).

## O que mudou da versão 3 para esta

- **Citações no formato ABNT** (sistema autor-data, NBR 10520:2023): na frase,
  o sobrenome com inicial maiúscula e o ano entre parênteses, como "Fama (1970)";
  dentro dos parênteses, sobrenome e ano separados por vírgula, como
  "(Fama, 1970)", e vários autores separados por ponto e vírgula, como
  "(Santos; Bianchi; Costa, 2023)". Toda fala que usa um trabalho de outra
  pessoa agora diz quem e de que ano.
- **Toda figura do slide tem "Figura N – título" em cima e "Fonte:" embaixo**
  (NBR 14724). Os gráficos feitos pelos nossos scripts ficam com "Fonte: Os
  autores (2026)"; os que usam dados de fora dizem de onde vieram os dados
  (Google Notícias e Yahoo Finance). A tabela dos estudos brasileiros virou
  "Quadro 1", que é o nome que a ABNT dá a tabela de texto.
- **Slides 21 e 22: referências completas em ABNT** (NBR 6023), em ordem
  alfabética, só das obras citadas no vídeo.
- **Para caber nos 5 minutos com as citações**, saíram da fala três
  trechos que continuam nos slides: as "mil séries simuladas" (slide 12),
  "ou seja, a relação existe" (título do slide 13) e de onde vieram os dados
  (rodapé do slide 9).
- **Frase dos 73% voltou com fonte.** Na versão 3, "boa parte se informa pela
  internet" estava marcada para conferir. Conferi no relatório da B3 (2020):
  73% dos investidores entrevistados responderam que se informam pela
  internet. Agora a frase tem número e fonte.

### Como ler as citações em voz alta (para o teleprompter)

O texto está escrito em ABNT, mas na fala fica mais natural assim:

| Escrito | Falado |
|---|---|
| Segundo a B3 (2020, 2025) | "Segundo a B3, em 2020 e 2025" |
| na pesquisa da B3 (2020) | "na pesquisa da B3 de 2020" |
| Barber e Odean (2008) mostraram | "Barber e Odean, em 2008, mostraram" |
| de Fama (1970) | "de Fama, de 1970" |
| de Santos, Bianchi e Costa (2023) | "de Santos, Bianchi e Costa, de 2023" |

> **Antes de gravar, confiram três coisas (não ponham no vídeo sem conferir):**
> 1. **O título** já está como vocês informaram: "Sentimento de notícias e
>    retorno de ações: análise de risco de carteiras na bolsa brasileira".
> 2. **O nome completo do Maurício** e **o nome do orientador** como estão na
>    inscrição. Usei "Maurício Renck Gedrat" e "professor Raul Mesquita", que
>    é como está no README do projeto.
> 3. **A coleta diária ligada** (dois cliques em
>    `scripts/AGENDAR_COLETA_DIARIA.bat`), porque o bloco 7 diz que ela "já
>    está preparada".

---

## BLOCO 1 — Apresentação (0:00 – 0:20)

`[slide 1]`

**[L]** Olá! Eu sou o Leonardo Kohn.

**[M]** E eu sou o Maurício Renck Gedrat.

**[L]** Somos estudantes do quarto ano do curso técnico em Eletrônica da
Fundação Escola Técnica Liberato Salzano Vieira da Cunha, em Novo Hamburgo,
Rio Grande do Sul. Nosso orientador é o professor Raul Mesquita.

**[M]** Nosso projeto se chama "Sentimento de notícias e retorno de ações:
análise de risco de carteiras na bolsa brasileira", e está na área de
Ciências da Computação.

**[M] (OPCIONAL — combinem antes com o orientador)** O título fala em risco
de carteiras porque o projeto começou com essa parte. Em setembro, ela foi
retirada para concentrar o trabalho no teste científico.

---

## BLOCO 2 — Justificativa (0:20 – 0:58)

`[slide 2]`

**[L]** Segundo a B3 (2020, 2025), a bolsa brasileira passou de 583 mil
investidores pessoa física, em 2011, para 5,4 milhões, em 2025. E, na
pesquisa da B3 (2020), 73% dos entrevistados se informam pela internet.

`[slide 3]`

**[L]** Barber e Odean (2008) mostraram que o pequeno investidor tende a
comprar as ações que aparecem no noticiário. E, no Brasil, Chague, De-Losso
e Giovannetti (2020) acompanharam quem fazia day trade: dos que insistiram
por mais de 300 dias, 97% perderam dinheiro.

`[slide 4]`

**[L]** Daí vem uma pergunta prática: quem decide pela manchete está à frente
ou atrás do preço?

---

## BLOCO 3 — Problema, hipóteses e objetivo (0:58 – 1:30)

`[slide 5]`

**[M]** Nosso problema de pesquisa é: existe relação entre o sentimento das
notícias e o retorno das ações na B3? E, se existe, quem vem primeiro, a
notícia ou o preço?

**[M]** Quando falamos em sentimento, é o tom do texto, positivo ou negativo,
e não a emoção de quem lê.

`[slide 6]`

**[M]** A hipótese nula é que não existe correlação. Contra ela, testamos as
duas direções: notícia antes do preço, ou preço antes da notícia. O objetivo
foi responder isso com um método que qualquer pessoa consiga verificar.

---

## BLOCO 4 — Fundamentação teórica (1:30 – 2:10)

`[slide 7]`

**[L]** Duas teorias dão respostas opostas. Pela hipótese de mercado
eficiente, de Fama (1970), o preço já incorpora a informação pública: quando
a notícia sai, o preço já andou. Já Baker e Wurgler (2007) mostram que o
humor do mercado pode mover os preços no curto prazo.

**[L]** Para decidir, usamos a ideia de Granger (1969): a causa tem que vir
antes do efeito.

`[slide 8]`

**[L]** Os estudos brasileiros que encontramos, como os de Araújo, Eleutério
e Louçã (2018), Carosia, Coelho e Silva (2021) e Souza e Martins (2024),
usam dados diários. Nenhum usou o horário exato das notícias e o preço
minuto a minuto.

---

## BLOCO 5 — Metodologia (2:10 – 3:12)

`[slide 9]`

**[M]** Coletamos 19.410 notícias sobre oito ações de sete setores, de 2024 a
2026, além de duas amostras de réplica.

`[slide 10]`

**[M]** Cada notícia recebeu uma nota de sentimento por um léxico, um
dicionário de palavras do mercado financeiro feito por nós. Para validar,
comparamos com rótulos de referência e com o FinBERT-PT-BR, um modelo de
inteligência artificial de Santos, Bianchi e Costa (2023).

`[slide 11]`

**[M]** Para descobrir quem vem primeiro, conseguimos o horário exato de 4.998
notícias e cruzamos com o preço em barras de uma hora, cinco minutos e um
minuto.

`[slide 12]`

**[M]** Cada correlação foi testada embaralhando os dados dez mil vezes, com
a correção de Holm (1979) para testes múltiplos. As hipóteses dos testes de
direção foram registradas por escrito, com data, antes de rodar.

---

## BLOCO 6 — Resultados e discussão (3:12 – 4:20)

`[slide 13]`

**[L]** No mesmo dia da notícia, a correlação foi significativa em seis das
oito ações. Ela continuou depois de descontar o movimento do Ibovespa, e se
repetiu em 2021 a 2023 e nas ações menores.

`[slide 14]`

**[L]** Mas quem vem primeiro? Com o horário exato, o preço se moveu antes da
notícia. O tom das notícias da noite acompanhou o pregão que já tinha
fechado, e o das notícias do pregão, a hora anterior.

`[slide 15]`

**[M]** No sentido contrário, a notícia não antecipou nada: nem a abertura do
dia seguinte, nem a hora seguinte,

`[slide 16]`

**[M]** nem os cinco minutos depois da publicação. A limitação é que efeitos
muito pequenos podem ter escapado dos testes.

`[slide 17]`

**[M]** Por fim, congelamos os dados, e um programa que refaz todos os testes
deu os mesmos resultados em Linux e em Windows.

---

## BLOCO 7 — Conclusão (4:20 – 4:45)

`[slide 18]`

**[L]** Concluímos que a relação entre o sentimento das notícias e o preço é
real, mas a imprensa reflete um movimento que o mercado já fez, como prevê a
hipótese de mercado eficiente. Para o investidor, a mensagem é clara: a
manchete chega depois do preço.

`[slide 19]`

**[M]** Os próximos passos já estão preparados: uma coleta diária, para
testar o resultado com notícias futuras, e a validação do léxico com
rotulagem humana.

`[slide 20]`

**[L e M]** Obrigado!

`[slides 21 e 22 — Referências: uns 4 segundos cada, sem fala]`

---

## De onde sai cada informação falada

As citações estão no formato autor-data da ABNT; a referência completa de
cada uma está na seção "Referências", logo abaixo. Quando a fonte é o nosso
próprio trabalho, a coluna mostra o arquivo do projeto.

| Bloco | Frase | Fonte |
|---|---|---|
| 1 | Nome da escola, cidade e estado | página da MOSTRATEC Virtual dos projetos de 2025 da escola; README do projeto |
| 2 | 583 mil investidores (2011) | B3 (2020) |
| 2 | 5,4 milhões (2º trimestre de 2025) | B3 (2025) |
| 2 | 73% se informam pela internet | B3 (2020): pergunta "Onde você costuma se informar sobre investimentos?" |
| 2 | Pequeno investidor compra o que está no noticiário | Barber e Odean (2008) |
| 2 | 97% dos que insistiram por mais de 300 dias perderam | Chague, De-Losso e Giovannetti (2020) |
| 3 | "Sentimento = tom do texto" | README do projeto, seção de limitações (crítica da FEICIT) |
| 4 | Mercado eficiente | Fama (1970) |
| 4 | Humor do mercado move preços no curto prazo | Baker e Wurgler (2007) |
| 4 | A causa vem antes do efeito | Granger (1969) |
| 4 | Estudos brasileiros com dados diários | Araújo, Eleutério e Louçã (2018); Carosia, Coelho e Silva (2021); Souza e Martins (2024) |
| 5 | (só no slide 9) Notícias do Google Notícias; preços do Yahoo Finance | Google (2026); Yahoo (2026); `modulos/coleta/precos.py` |
| 5 | 19.410 notícias, 8 ações, 7 setores | `resultados/congelado_*.txt` |
| 5 | Réplicas: 2021–2023 e 8 ações menores do índice SMLL | `dados/noticias_2021_2023.csv` (7.291); `resultados/fase_H_*` (1.160 notícias); carteira do SMLL: B3 (2026) |
| 5 | FinBERT-PT-BR | Santos, Bianchi e Costa (2023); `resultados/fase_F_validacao_modelos_*` (kappa 0,30 e 0,44) |
| 5 | 4.998 notícias com horário exato | `resultados/fase_causal_A1_*.txt` |
| 5 | Barras de 1 hora, 5 min e 1 min | `dados/intradiario/`, `dados/minuto/` (Yahoo, 2026) |
| 5 | 10.000 embaralhamentos; correção de Holm | Holm (1979); scripts 12, 25, 37, 38 e 40 |
| 5 | Hipóteses registradas antes (testes de direção) | `docs/pre-registro_*` (10 pré-registros e 4 adendos) |
| 5 | (só no slide 12) 1.000 séries simuladas, 5% de falsos positivos | saída do `scripts/1_validar_modulo_estatistico.py` |
| 6 | 6 de 8 no mesmo dia | `resultados/congelado_*.txt` |
| 6 | Sobrevive ao Ibovespa; réplicas | `teste3_retorno_anormal` (r = 0,109); P8 (Holm 0,002); H1 small caps (r = 0,213) |
| 6 | Noite ← pregão; pregão ← hora anterior | A1_P3 (r = 0,083; p = 0,001); A1_P5 (r = 0,091; p = 0,003) |
| 6 | Não antecipa abertura, hora seguinte nem 5 min | P1 (r = 0,011); A1_P4 (p = 0,23); C1 (r = −0,023; p = 0,62) |
| 6 | Efeitos pequenos podem ter escapado | análise de poder conforme Cohen (1988): menor r detectável de cada teste (0,04 a 0,13); o slide 16 mostra a citação |
| 6 | Dados congelados; mesmos resultados em Linux e Windows | `verificacao/relatorio_verificacao_linux_servidor.txt` e `_windows.txt` (99 de 99) |
| 7 | Conclusão alinhada ao mercado eficiente | Fama (1970), já citado no bloco 4; o slide 18 repete a citação |
| 7 | Coleta diária e rotulagem humana | `docs/pre-registro_2026-10-02_fase-G_minuto.md`; planilhas em `dados/validacao_lexico/` |

## Figuras e quadro dos slides (legenda e fonte)

| Slide | Ilustração | Fonte |
|---|---|---|
| 5 | Figura 1 – Escala da nota de sentimento de cada notícia | Os autores (2026) |
| 6 | Figura 2 – As duas direções testadas contra a hipótese nula | Os autores (2026) |
| 8 | Quadro 1 – Estudos brasileiros sobre sentimento e mercado de ações | Os autores (2026) |
| 10 | Figura 3 – Concordância (kappa, com intervalo de 95%) de cada medida com os rótulos de referência | Os autores (2026) |
| 11 | Figura 4 – Janelas de tempo comparadas antes e depois da publicação de cada notícia | Os autores (2026) |
| 13 | Figura 5 – Correlação entre o sentimento do dia D e o retorno em D+k | Os autores (2026), com dados de Google Notícias (Google, 2026) e Yahoo Finance (Yahoo, 2026) |
| 14 | Figura 6 – Retorno acumulado, hora a hora, em torno das notícias do pregão | idem |
| 15 | Figura 7 – Correlação em cada teste de direção | idem |
| 16 | Figura 8 – Retorno acumulado, minuto a minuto, em torno da publicação | idem |

Não há nenhuma foto ou imagem tirada da internet nos slides: todos os
gráficos e esquemas foram feitos por nós (gráficos pelo script
`charts.py`, a partir dos resultados congelados do projeto).

## Referências

ARAÚJO, T.; ELEUTÉRIO, S.; LOUÇÃ, F. Do sentiments influence market
dynamics? A reconstruction of the Brazilian stock market and its mood.
**Physica A**, v. 505, p. 1139-1149, 2018. DOI: 10.1016/j.physa.2018.04.045.

B3. **A descoberta da bolsa pelo investidor brasileiro**. São Paulo: B3, dez.
2020. Disponível em:
https://www.b3.com.br/data/files/69/75/42/A0/36ECA71068C61CA7AC094EA8/Pesquisa%20PF_vf%20_dez.20_.pdf.
Acesso em: 2 out. 2026.

B3. **Pessoas físicas**: uma análise da evolução dos investidores na B3 — 2º
trimestre de 2025. São Paulo: B3, 2025. Disponível em:
https://www.b3.com.br/data/files/A2/A0/78/20/E61689100A29E189AC094EA8/Book%20PF%202TRI%202025_vF.pdf.
Acesso em: 2 out. 2026.

B3. **Índice Small Cap (SMLL B3)**: composição da carteira. São Paulo: B3,
2026. Disponível em:
https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-de-segmentos-e-setoriais/indice-small-cap-smll-composicao-da-carteira.htm.
Acesso em: 2 out. 2026.

BAKER, M.; WURGLER, J. Investor sentiment in the stock market. **Journal of
Economic Perspectives**, v. 21, n. 2, p. 129-151, 2007.

BARBER, B. M.; ODEAN, T. All that glitters: the effect of attention and news
on the buying behavior of individual and institutional investors. **The
Review of Financial Studies**, v. 21, n. 2, p. 785-818, 2008. DOI:
10.1093/rfs/hhm079.

CAROSIA, A. E. O.; COELHO, G. P.; SILVA, A. E. A. Investment strategies
applied to the Brazilian stock market: a methodology based on sentiment
analysis with deep learning. **Expert Systems with Applications**, v. 184,
art. 115470, 2021. DOI: 10.1016/j.eswa.2021.115470.

CHAGUE, F.; DE-LOSSO, R.; GIOVANNETTI, B. **Day trading for a living?**
SSRN, 2020. Working paper. Disponível em:
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101. Acesso em: 2
out. 2026.

COHEN, J. **Statistical power analysis for the behavioral sciences**. 2. ed.
Hillsdale: Lawrence Erlbaum Associates, 1988.

FAMA, E. F. Efficient capital markets: a review of theory and empirical work.
**The Journal of Finance**, v. 25, n. 2, p. 383-417, 1970.

GOOGLE. **Google Notícias**. 2026. Disponível em: https://news.google.com.
Acesso em: 2 out. 2026.

GRANGER, C. W. J. Investigating causal relations by econometric models and
cross-spectral methods. **Econometrica**, v. 37, n. 3, p. 424-438, 1969.
DOI: 10.2307/1912791.

HOLM, S. A simple sequentially rejective multiple test procedure.
**Scandinavian Journal of Statistics**, v. 6, n. 2, p. 65-70, 1979.

SANTOS, L. L.; BIANCHI, R. A. C.; COSTA, A. H. R. FinBERT-PT-BR: análise de
sentimentos de textos em português do mercado financeiro. In: BRAZILIAN
WORKSHOP ON ARTIFICIAL INTELLIGENCE IN FINANCE, 2., 2023, João Pessoa.
**Anais** [...]. Porto Alegre: Sociedade Brasileira de Computação, 2023.
p. 144-155. DOI: 10.5753/bwaif.2023.231151.

SOUZA, D. M. S. de; MARTINS, O. S. Brazilian stock market performance and
investor sentiment on Twitter. **Revista de Gestão**, v. 31, n. 1, p. 18-33,
2024. DOI: 10.1108/REGE-07-2021-0145.

YAHOO. **Yahoo Finance**. 2026. Disponível em: https://finance.yahoo.com.
Acesso em: 2 out. 2026.

## O que ficou de fora de propósito

- **Números com r e p na fala.** Número demais cansa; eles aparecem nos
  gráficos dos slides 13 a 16.
- **Nome do professor que deu cada ideia.** Não tenho certeza de quem sugeriu
  o quê (por exemplo, o teste do pregão anterior). Se quiserem agradecer,
  confirmem antes.
- **A história de origem do projeto.** Só entra se for verdade.

## Checklist de gravação

- [ ] Horizontal, 480p ou mais, 30 fps
- [ ] Os dois aparecem e falam; o orientador é citado e **não aparece**
- [ ] Título, nomes e orientador conferidos com a inscrição
- [ ] Coleta diária ligada (bloco 7)
- [ ] Teleprompter logo abaixo da lente, não ao lado
- [ ] Gravar bloco por bloco; assistir cada um antes de passar ao próximo
- [ ] Deixar os slides 21 e 22 (referências) uns 4 segundos cada no fim
- [ ] Cronometrar: tem que ficar abaixo de 5:00
- [ ] YouTube **não listado**; abrir o link numa janela anônima para testar
