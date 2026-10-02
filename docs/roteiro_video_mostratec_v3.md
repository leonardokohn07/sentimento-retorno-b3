# Roteiro do vídeo — MOSTRATEC 2026 (versão 3, com os slides)

**Até 5 minutos · horizontal · mínimo 480p / 30 fps · YouTube não listado**

- **[L]** = Leonardo · **[M]** = Maurício · **`[slide N]`** = o slide de fundo que entra nessa fala
  (arquivo `slides_fundo_video.pdf`; a imagem de vocês fica no canto inferior direito).
- **Ordem obrigatória** (recomendações oficiais da MOSTRATEC):
  1. apresentação (alunos, orientador, escola, estado);
  2. introdução (justificativa, problema, hipóteses, objetivos);
  3. fundamentação e metodologia;
  4. resultados e discussão.
- **Tempo:** cerca de 670 palavras faladas: **4min30** em ritmo normal e
  **4min45** falando mais devagar. **Cronometrem o primeiro take.**
  - Se passar de 4min50, cortem a frase das "mil séries simuladas" (bloco 5).
  - Se usarem a frase opcional do bloco 1, cortem a das "mil séries" de
    qualquer jeito.

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

## BLOCO 2 — Justificativa (0:20 – 0:55)

`[slide 2]`

**[L]** Em 2011, a bolsa brasileira tinha 583 mil investidores pessoa física.
Em 2025, eram 5,4 milhões. E boa parte se informa pela internet.

`[slide 3]`

**[L]** Pesquisas mostram que o pequeno investidor tende a comprar as ações
que aparecem no noticiário. E um estudo brasileiro acompanhou quem fazia day
trade: dos que insistiram por mais de 300 dias, 97% perderam dinheiro.

`[slide 4]`

**[L]** Daí vem uma pergunta prática: quem decide pela manchete está à frente
ou atrás do preço?

---

## BLOCO 3 — Problema, hipóteses e objetivo (0:55 – 1:30)

`[slide 5]`

**[M]** Nosso problema de pesquisa é: existe relação entre o sentimento das notícias e o retorno das ações na B3? E, se existe, quem vem
primeiro, a notícia ou o preço?

**[M]** Quando falamos em sentimento, é o tom do texto, positivo ou negativo,
e não a emoção de quem lê.

`[slide 6]`

**[M]** A hipótese nula é que não existe correlação. Contra ela, testamos as
duas direções: notícia antes do preço, ou preço antes da notícia. O objetivo foi responder isso com um método que qualquer pessoa
consiga verificar.

---

## BLOCO 4 — Fundamentação teórica (1:30 – 2:05)

`[slide 7]`

**[L]** Duas teorias dão respostas opostas. A hipótese de mercado eficiente,
de Eugene Fama, diz que o preço já incorpora a informação pública: quando a
notícia sai, o preço já andou. Já Baker e Wurgler mostram que o humor do
mercado pode mover os preços no curto prazo.

**[L]** Para decidir, usamos a ideia de Clive Granger: a causa tem que vir
antes do efeito.

`[slide 8]`

**[L]** Os estudos brasileiros que encontramos usam dados diários ou redes
sociais. Não encontramos nenhum que usasse o horário exato das notícias e o
preço minuto a minuto.

---

## BLOCO 5 — Metodologia (2:05 – 3:10)

`[slide 9]`

**[M]** Coletamos 19.410 notícias sobre oito ações de sete setores, de 2024 a
2026, além de duas amostras de réplica.

`[slide 10]`

**[M]** Cada notícia recebeu uma nota de sentimento por um dicionário de
palavras do mercado financeiro, o léxico. Para validar, comparamos com
rótulos de referência e com um modelo de inteligência artificial treinado em
notícias financeiras em português.

`[slide 11]`

**[M]** Para descobrir quem vem primeiro, conseguimos o horário exato de 4.998
notícias e cruzamos com o preço em barras de uma hora, de cinco minutos e de
um minuto.

`[slide 12]`

**[M]** Cada correlação foi testada embaralhando os dados dez mil vezes, com
correção para testes múltiplos. As hipóteses dos testes de direção foram
registradas por escrito, com data, antes de rodar. E o método foi validado
antes em mil séries simuladas, com cinco por cento de falsos positivos, como
esperado.

---

## BLOCO 6 — Resultados e discussão (3:10 – 4:20)

`[slide 13]`

**[L]** No mesmo dia da notícia, a correlação foi significativa em seis das
oito ações. Ela continuou depois de descontar o movimento do Ibovespa, e se
repetiu em 2021 a 2023 e nas ações menores. Ou seja, a relação existe.

`[slide 14]`

**[L]** Mas quem vem primeiro? Com o horário exato, o preço se moveu antes da
notícia. O tom das notícias da noite acompanhou o pregão que já tinha
fechado, e o das notícias do pregão acompanhou a hora anterior.

`[slide 15]`

**[M]** No sentido contrário, a notícia não antecipou nada: nem a abertura do
dia seguinte, nem a hora seguinte,

`[slide 16]`

**[M]** nem os cinco minutos depois da publicação. A limitação é que efeitos
muito pequenos podem ter escapado dos testes.

`[slide 17]`

**[M]** Por fim, congelamos os dados e criamos um programa que refaz todos os
testes. Ele deu os mesmos resultados em dois computadores diferentes, com
Linux e com Windows.

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

---

## De onde sai cada informação falada

| Bloco | Frase | Fonte |
|---|---|---|
| 1 | Nome da escola, cidade e estado | página da MOSTRATEC Virtual dos projetos de 2025 da escola; README do projeto |
| 2 | 583 mil (2011) e 5,4 milhões (2025) | B3, *A descoberta da bolsa pelo investidor brasileiro* (dez/2020); B3, *Book PF 2º tri 2025* |
| 2 | "boa parte se informa pela internet" | B3 (2020): 73% se informam pela internet **[CONFERIR no PDF; por isso o vídeo não diz o número]** |
| 2 | Pequeno investidor compra o que está no noticiário | Barber e Odean (2008), *Review of Financial Studies* |
| 2 | 97% dos que insistiram por mais de 300 dias perderam | Chague, De-Losso e Giovannetti, *Day trading for a living?* (SSRN) |
| 3 | "Sentimento = tom do texto" | README do projeto, seção de limitações (crítica da FEICIT) |
| 4 | Fama; Baker e Wurgler; Granger | Fama (1970); Baker e Wurgler (2007); Granger (1969) — todos no plano v2 |
| 4 | Estudos brasileiros diários ou de redes sociais | Araújo et al. (2018); Carosia et al. (2021); Souza e Martins (2024) — `docs/literatura_causalidade.md` |
| 5 | 19.410 notícias, 8 ações, 7 setores | `resultados/congelado_*.txt`; `modulos/coleta/precos.py` |
| 5 | Réplicas: 2021-2023 e 8 ações menores | `dados/noticias_2021_2023.csv` (7.291); `resultados/fase_H_*` (1.160 notícias) |
| 5 | Léxico validado; modelo de IA (FinBERT-PT-BR) | `resultados/fase_F_validacao_modelos_*` (kappa 0,30 e 0,44) |
| 5 | 4.998 notícias com horário exato | `resultados/fase_causal_A1_*.txt` |
| 5 | Barras de 1 hora, 5 min e 1 min | `dados/intradiario/`, `dados/minuto/` |
| 5 | 10.000 embaralhamentos; correção de Holm | scripts 12, 25, 37, 38 e 40 |
| 5 | Hipóteses registradas antes (testes de direção) | `docs/pre-registro_*` (10 pré-registros e 4 adendos) |
| 5 | 1.000 séries simuladas, 5% de falsos positivos | saída do `scripts/1_validar_modulo_estatistico.py` |
| 6 | 6 de 8 no mesmo dia | `resultados/congelado_*.txt` |
| 6 | Sobrevive ao Ibovespa; réplicas | `teste3_retorno_anormal` (r = 0,109); P8 (Holm 0,002); H1 small caps (r = 0,213) |
| 6 | Noite ← pregão; pregão ← hora anterior | A1_P3 (r = 0,083; p = 0,001); A1_P5 (r = 0,091; p = 0,003) |
| 6 | Não antecipa abertura, hora seguinte nem 5 min | P1 (r = 0,011); A1_P4 (p = 0,23); C1 (r = −0,023; p = 0,62) |
| 6 | Efeitos pequenos podem ter escapado | menor r detectável de cada teste (0,04 a 0,13) |
| 6 | Dados congelados; mesmos resultados em Linux e Windows | `verificacao/relatorio_verificacao_linux_servidor.txt` e `_windows.txt` (99 de 99) |
| 7 | Coleta diária e rotulagem humana | `docs/pre-registro_2026-10-02_fase-G_minuto.md`; planilhas em `dados/validacao_lexico/` |

## O que ficou de fora de propósito

- **Números com r e p.** Na fala, número demais cansa. Se quiserem, eles
  entram nos cartões de tela do bloco 6.
- **Nome do professor que deu cada ideia.** Não tenho certeza de quem sugeriu
  o quê (por exemplo, o teste do pregão anterior). Se quiserem agradecer,
  confirmem antes.
- **A história de origem do projeto.** Só entra se for verdade. Exemplo, se
  for: "O projeto começou como uma ferramenta que lia notícias para ajudar a
  investir; antes de afirmar que isso funciona, decidimos testar."

## Checklist de gravação

- [ ] Horizontal, 480p ou mais, 30 fps
- [ ] Os dois aparecem e falam; o orientador é citado e **não aparece**
- [ ] Título, nomes e orientador conferidos com a inscrição
- [ ] Coleta diária ligada (bloco 7)
- [ ] Teleprompter logo abaixo da lente, não ao lado
- [ ] Gravar bloco por bloco; assistir cada um antes de passar ao próximo
- [ ] Cronometrar: tem que ficar abaixo de 5:00
- [ ] YouTube **não listado**; abrir o link numa janela anônima para testar
