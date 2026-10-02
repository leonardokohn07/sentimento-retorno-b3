# Ancoragem da pesquisa — por que este estudo existe

**Data:** 02/10/2026.

**O que é "ancorar" uma pesquisa:** ligar a pergunta a quatro coisas que
qualquer avaliador consegue conferir:

1. um **problema real**, com números de fontes oficiais;
2. uma **teoria** que faz uma previsão testável;
3. uma **lacuna**, ou seja, o que os estudos anteriores ainda não responderam;
4. uma **contribuição**: o que muda depois que a pesquisa existe.

Sem âncora, a banca ouve "fizemos porque achamos interessante". Com âncora,
ela ouve "existe este problema, a teoria prevê X, ninguém tinha medido Y no
Brasil, e nós medimos".

Todas as fontes abaixo foram conferidas na fonte original em 02/10/2026. O
status de cada uma está no fim do arquivo. Onde o número foi lido por
leitura automática de PDF, está marcado **[CONFERIR]**: abram o PDF e
confirmem a página antes de citar.

---

## 1. O problema real (a "causa")

### 1.1 Milhões de pessoas novas na bolsa

| Ano | Investidores pessoa física na B3 | Fonte |
|---|---|---|
| 2011 | 583 mil | B3, *A descoberta da bolsa pelo investidor brasileiro* (dez/2020) |
| out/2020 | cerca de 3,2 milhões | mesmo estudo |
| 2º tri/2025 | **5,4 milhões** (CPFs únicos em renda variável) | B3, *Book PF 2º tri 2025* |

Em 14 anos, o número de pessoas físicas na bolsa ficou cerca de **9 vezes
maior**. A maioria entrou recentemente e tem pouca experiência.

### 1.2 Essas pessoas se informam pela internet e pelas notícias

- **B3 (2020)**, pesquisa com mais de 1,3 mil investidores (jun-ago/2020):
  - 73% se informam sobre investimentos pela internet;
  - 35% dizem tomar decisões com base em recomendações de **portais da
    internet**. **[CONFERIR]**
- **ANBIMA, Raio X do Investidor Brasileiro, 9ª edição** (com o Datafolha,
  5.832 entrevistas, novembro de 2025):
  - 36% da população investe (cerca de 60,6 milhões de pessoas);
  - para decidir, citam "portais e sites" (20%) e "sites de notícias"
    (11%), além de YouTube (35%) e Instagram (27%). **[CONFERIR]**

### 1.3 A notícia decide o que a pessoa física compra

Barber e Odean (2008) mostraram, nos EUA, que a pessoa física compra
principalmente as ações que **chamam a atenção**: as que estão no
noticiário, com volume anormal ou com retorno extremo no dia. Quem tem
milhares de ações para escolher acaba escolhendo entre as que apareceram na
frente dele.

### 1.4 Negociar no curto prazo costuma dar prejuízo

Chague, De-Losso e Giovannetti (2019, rev. 2020) acompanharam **todas** as
pessoas que começaram a fazer *day trade* no mercado futuro de índice
brasileiro entre 2013 e 2015. Das que persistiram por mais de 300 dias:
- **97% perderam dinheiro**;
- só 1,1% ganharam mais que um salário mínimo.

### 1.5 A pergunta prática que sai daí

> **Quando uma pessoa lê uma manchete e decide comprar ou vender, ela está
> À FRENTE do preço ou ATRÁS dele?**

Se a notícia antecipa o preço, ler notícias dá vantagem. Se o preço já andou
quando a matéria sai, quem decide pela manchete **chega atrasado** e compra
o que já subiu.

### 1.6 Uma regra legal que explica o mecanismo

A **Resolução CVM nº 44/2021** manda a empresa divulgar fato relevante:
- de forma **ampla, imediata e simultânea** em todos os mercados, enviando à
  CVM (art. 3º);
- **sempre que possível, antes do início ou depois do encerramento dos
  negócios** (art. 5º).

Ou seja: o canal oficial da informação é o **comunicado da empresa**, e não
a matéria de jornal. A matéria é escrita **depois**, a partir do comunicado
ou do movimento do preço. Isso dá uma explicação concreta para o que os
dados mostraram (seção 6).

---

## 2. A teoria (o que se espera encontrar)

Duas teorias fazem previsões **diferentes** para a mesma pergunta:

| Teoria | O que prevê | Referência |
|---|---|---|
| **Hipótese de mercado eficiente, forma semiforte** | O preço já incorpora a informação pública. Quando a matéria sai, o preço já se ajustou. A notícia **não** prevê o preço seguinte. | Fama (1970) |
| **Sentimento e atenção do investidor** | O tom da mídia e a atenção movem o preço no curto prazo, sobretudo em ações pequenas e difíceis de avaliar. | Baker e Wurgler (2007); Tetlock (2007); Barber e Odean (2008) |

**Como decidir entre as duas:** pela **ordem no tempo**. Granger (1969)
definiu a causalidade que se pode testar: X "causa" Y se o passado de X
ajuda a prever Y. O mesmo artigo avisa que uma correlação "instantânea"
costuma aparecer quando os dados são pouco frequentes. Por isso este estudo
foi de dados diários para barras de 60, 5 e 1 minuto.

---

## 3. A lacuna (o que ainda não tinha sido feito)

Os estudos brasileiros encontrados usam **dados diários** ou fontes que não
são a imprensa:

| Estudo | Fonte do sentimento | Frequência | Achado |
|---|---|---|---|
| Araújo, Eleutério e Louçã (2018) | índice de mídia (MarketPsych) | diária | o preço afeta mais a notícia do que o contrário |
| Carosia, Coelho e Silva (2021) | 3 portais brasileiros | diária | Granger no sentido notícia → mercado |
| Souza e Martins (2024) | Twitter | diária | correlação no mesmo dia, sem relação defasada |
| Silva (2017, tese UnB) | *Valor Econômico* | diária | efeito do pessimismo em mercado de baixa |

No exterior, o estudo intradiário mais próximo (Strauß, Vliegenthart e
Verhoeven, 2018) usou tweets da Reuters e da Bloomberg contra o Dow Jones.

**A lacuna:** nas bases consultadas (Crossref, OpenAlex, OpenAIRE e DOAJ),
**não encontramos** estudo que use o **horário exato de publicação de
matérias da imprensa** e **preços intradiários** de ações da B3 para testar
**quem vem primeiro**, o preço ou a notícia.

> **Cuidado com a frase na banca:** digam "não encontramos nas bases que
> consultamos", e não "nunca foi feito". A busca não cobriu o SPELL nem o
> SciELO (bloqueado por robots.txt), onde estão periódicos nacionais como a
> RBFin e a RAC.

---

## 4. A âncora do método: a crise de replicação em finanças

Este é o segundo motivo da pesquisa, e talvez o mais forte para uma feira
de ciências.

- **Harvey, Liu e Zhu (2016)** analisaram centenas de "fatores" publicados
  que explicariam os retornos das ações. Conclusão: por causa da mineração
  de dados (testar muitas coisas até alguma dar certo), **a maioria dos
  achados publicados em finanças provavelmente é falsa**. Eles propõem
  exigir estatística t maior que 3,0, e não 2,0.
- **Hou, Xue e Zhang** replicaram 447 "anomalias" de mercado: **64% não
  foram significativas** a 5% quando refeitas com cuidado, e 85% com o
  corte t > 3 (versão de trabalho do NBER, 2017; a versão publicada em 2020
  pode trazer números um pouco diferentes **[CONFERIR]**).
- **Nosek et al. (2018)** defendem o **pré-registro**: escrever a hipótese e
  a análise **antes** de ver o resultado. Isso separa o teste de hipótese da
  "pescaria" de resultados.

**O que isso tem a ver com o InvestAI:** as ferramentas que vendem
"sentimento de notícias para investir" raramente publicam como medem, quanto
erram e quantos testes fizeram. Este estudo faz o oposto:
- pré-registro datado antes de cada teste;
- correção para múltiplos testes (Holm);
- todos os resultados publicados, inclusive os nulos;
- dados congelados e um verificador que refaz tudo com um comando
  (`docs/metodo_cientifico_e_verificacao.md`).

---

## 5. A âncora na eletrônica (o curso de vocês)

O problema central do estudo é um problema clássico de eletrônica:
**medir o atraso entre dois sinais**. É o que faz um radar, um sonar ou um
par de microfones que localiza a fonte de um som: correlação cruzada com
defasagem, procurando onde está o pico (Knapp e Carter, 1976). Granger
(1969) usou métodos de espectro cruzado, da mesma família.

| Na eletrônica | No InvestAI |
|---|---|
| Dois sinais, procurar o atraso | sentimento das notícias × retorno da ação |
| Correlação cruzada com defasagem | curva de D−5 a D+5; horas antes e depois; minutos antes e depois |
| Taxa de amostragem / resolução | barras diárias → 60 min → 5 min → 1 min |
| Relação sinal-ruído | janela de 30 min dilui uma reação de 5 min (o r cai para ~41%, 1/√6) |
| Piso de ruído | calibração com sentimento embaralhado: ~5% de falsos positivos |
| Injetar sinal de teste conhecido | 1.000 séries sintéticas; controle positivo (manchetes de relato) |
| Calibrar o sensor | validação do léxico e do FinBERT contra rótulos (kappa) |
| Sensibilidade do instrumento | menor efeito detectável (r ≈ 0,04 a 0,13, conforme o teste) |

**Para a banca:** "Usamos as ferramentas de medição de sinais que aprendemos
no técnico em eletrônica para medir o atraso entre a notícia e o preço."

Isso é uma analogia de **método**, não uma afirmação de que o mercado
funciona como um circuito.

---

## 6. A contribuição (o que muda depois do estudo)

1. **Resposta à pergunta prática:** na B3, nas 8 ações estudadas, a
   matéria de imprensa sai **depois** do movimento do preço:
   - o sentimento acompanha o movimento já ocorrido (horas antes da
     publicação);
   - e não antecipa o movimento seguinte (próxima hora, próxima abertura e
     até 1 a 5 minutos depois).
2. **Mensagem para o investidor iniciante:** "**a manchete chega depois do
   preço**". Decidir pela manchete é chegar atrasado. Isso conversa
   diretamente com os 5,4 milhões de pessoas físicas da seção 1.
3. **Contribuição de método:** um estudo de sentimento aberto, pré-registrado
   e verificável por qualquer pessoa, que é exatamente o que a crise de
   replicação (seção 4) pede.
4. **Coerência com a teoria:** o resultado é o previsto pela hipótese de
   mercado eficiente (Fama, 1970) e pelo estudo brasileiro mais próximo
   (Araújo et al., 2018).

---

## 7. Como contar a origem do projeto (sugestão, confiram se é verdade)

**[CONFERIR] Só vocês sabem se esta é a história real.** Sugestão:

> "O InvestAI começou como uma ferramenta que lia notícias para ajudar a
> investir. Antes de dizer a alguém que ler o sentimento das notícias ajuda
> a investir, a gente precisava testar se isso é verdade. O teste mostrou
> que a notícia vem depois do preço. Então o projeto mudou: em vez de
> vender uma previsão, ele mede, com método aberto, quando a notícia ajuda
> e quando não ajuda."

---

## 8. Para a banca, em 30 segundos

> "Em 2011 eram 583 mil pessoas físicas na bolsa; hoje são 5,4 milhões, e
> muitas decidem lendo notícias na internet. A pergunta é simples: quem lê a
> manchete está na frente ou atrás do preço? A teoria de mercado eficiente
> diz que está atrás; a teoria do sentimento diz que a notícia move o preço.
> Não encontramos estudo brasileiro que tenha medido isso com o horário
> exato das matérias e o preço minuto a minuto. Medimos, com pré-registro e
> um verificador que qualquer um pode rodar. Resultado: o preço anda
> primeiro, a notícia vem depois."

---

## 9. Fontes novas desta ancoragem e status

| Fonte | Como foi conferida | Status |
|---|---|---|
| B3. *A descoberta da bolsa pelo investidor brasileiro*. dez/2020 | PDF oficial no site da B3 | verificado; percentuais lidos automaticamente **[CONFERIR]** |
| B3. *Pessoas físicas: uma análise da evolução dos investidores na B3*, 2º tri/2025 | PDF oficial no site da B3 | verificado (5,4 milhões) |
| ANBIMA. *Raio X do Investidor Brasileiro*, 9ª ed. | PDF oficial no site da ANBIMA | verificado; percentuais lidos automaticamente **[CONFERIR]** |
| Resolução CVM nº 44/2021 (texto consolidado) | PDF oficial da CVM | verificado (art. 3º e art. 5º) |
| Barber; Odean (2008), RFS 21(2):785-818, DOI 10.1093/rfs/hhm079 | EconPapers/RePEc | verificado |
| Chague; De-Losso; Giovannetti, *Day trading for a living?*, SSRN 3423101 | página do SSRN | verificado (working paper, não é artigo de periódico) |
| Harvey; Liu; Zhu (2016), RFS 29(1):5-68, DOI 10.1093/rfs/hhv059 | IDEAS/RePEc | verificado |
| Hou; Xue; Zhang (2020), RFS 33(5):2019-2133, DOI 10.1093/rfs/hhy131 | página da OUP + NBER w23394 | verificado; números do NBER (2017) **[CONFERIR]** na versão de 2020 |
| Nosek et al. (2018), PNAS 115(11):2600-2606, DOI 10.1073/pnas.1708274114 | registro no Zenodo | verificado |
| Knapp; Carter (1976), IEEE TASSP 24(4):320-327, DOI 10.1109/TASSP.1976.1162830 | base de referências SCIRP; a página da IEEE não abriu | verificado em base secundária **[CONFERIR]** |

**Links:**
- B3 (2020): https://www.b3.com.br/data/files/69/75/42/A0/36ECA71068C61CA7AC094EA8/Pesquisa%20PF_vf%20_dez.20_.pdf
- B3 (2025): https://www.b3.com.br/data/files/A2/A0/78/20/E61689100A29E189AC094EA8/Book%20PF%202TRI%202025_vF.pdf
- ANBIMA (9ª ed.): https://www.anbima.com.br/data/files/BE/05/B0/55/1EABD91008E6DAD9F82BA2A8/Raio-X-do-Investidor-9-edicao.pdf
- CVM 44: https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol044consolid.pdf
- Barber e Odean: https://econpapers.repec.org/RePEc:oup:rfinst:v:21:y:2008:i:2:p:785-818
- Chague et al.: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3423101
- Harvey et al.: https://ideas.repec.org/a/oup/rfinst/v29y2016i1p5-68..html
- Hou et al.: https://academic.oup.com/rfs/article-abstract/33/5/2019/5236964 e https://www.nber.org/papers/w23394
- Nosek et al.: https://zenodo.org/records/13527840
- Knapp e Carter: https://www.scirp.org/reference/referencespapers?referenceid=215008

As demais referências (Fama, Baker e Wurgler, Tetlock, Granger, Araújo et
al., Carosia et al., Souza e Martins, Silva, Strauß et al.) já estavam
conferidas em `docs/literatura_causalidade.md` e no plano anterior.
