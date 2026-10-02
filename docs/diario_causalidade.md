# Diário da investigação de causalidade — InvestAI

> **RESUMO EXECUTIVO (02/10/2026)**
>
> **Pergunta:** a notícia move o preço, ou o preço move a notícia?
>
> **Resposta dos dados:** o preço vem primeiro.
> - Com o horário exato de ~5 mil notícias e preços hora a hora, o
>   sentimento das notícias **acompanha o movimento que já aconteceu**:
>   - notícias da noite ← pregão encerrado: p = 0,0009;
>   - notícias do pregão ← hora anterior: p = 0,003;
>   - da abertura até a notícia: r = 0,16, p = 0,0001.
> - E **não antecipa o que vem depois**:
>   - abertura seguinte: r ≈ 0,01;
>   - hora seguinte: r = 0,04, p = 0,23.
>
> **A associação do mesmo dia é real e robusta:**
> - é da própria empresa;
> - sobrevive ao desconto do Ibovespa;
> - **se repete em 2021-2023** (p Holm = 0,0009).
>
> **A direção é preço → notícia.** É coerente com a hipótese de mercado
> eficiente e com o estudo brasileiro mais próximo (Araújo et al., 2018).
>
> **Grau de evidência:** forte e consistente, não "100%".
> - A análise principal pré-registrada (só horas do Google) tinha pouco poder
>   e não passou no Holm, mas aponta na mesma direção.
> - A análise adicional declarada (Google + API dos sites, 5 vezes mais dados)
>   confirma.
> - Ponto cego: reações de poucos minutos, dentro da própria hora da
>   publicação.
> - Medida de sentimento: o léxico concorda só de forma razoável com rótulos
>   de referência (kappa 0,39; acerta ~61%). É uma checagem preliminar, feita
>   com anotador automático; a rotulagem humana ainda falta (seção 13). O
>   ruído enfraquece as correlações nos dois sentidos.
>
> **Todos os testes, nulos e erros estão documentados abaixo.**

Registro cronológico de tudo o que foi feito para testar a **direção** da
relação entre o sentimento das notícias e o retorno das ações. Inclui o que
deu errado e o que não confirmou nada.

**Regra de conduta (fixada no início):** testar a direção, não forçar um
resultado.
- Todo teste novo é pré-registrado antes de rodar.
- Todo resultado é reportado, inclusive os nulos.
- As múltiplas comparações são corrigidas (Holm).

---

## 0. O que significa "causalidade" aqui

A correlação do mesmo dia (D+0, r ≈ 0,13) tem três explicações possíveis:

1. **notícia → preço:** a notícia traz informação e o preço reage;
2. **preço → notícia:** o jornal relata o movimento que já aconteceu;
3. **causa comum:** algo externo move as duas coisas.

**O que estes dados permitem testar** é a *precedência temporal*. A notícia
chega ANTES do movimento de preço? Carrega informação que o preço ainda não
incorporou? Se sim, é notícia → preço no sentido de informação, ou seja,
causalidade de Granger em alta frequência.

**O que estes dados NÃO permitem provar** é que a *reportagem em si*,
independentemente da informação, move o preço. A literatura só consegue isso
com experimentos naturais: greves de jornais (Peress, 2014), colunistas
escalados ao acaso (Dougal et al., 2012) ou cobertura local diferente do mesmo
evento (Engelberg; Parsons, 2011). Não temos nada parecido.

**Nenhum estudo observacional prova causalidade "100%".** O que se pode
alcançar é uma evidência forte de precedência, controlando as explicações
alternativas.

---

## 1. O que já tinha sido feito antes desta fase (01-02/10/2026)

Tudo pré-registrado, com os resultados nos arquivos `resultados/`.

| Teste | Resultado |
|---|---|
| Estudo original | D+0 em 6 de 8 ativos; D+1 em 0 de 8; D−1 em 3 de 8 |
| Bug de fuso horário (UTC tratado como Brasília) | 180 notícias deslocadas (0,97%); nenhum veredito muda |
| Fim de semana agrupado (calendário) | Nenhuma hipótese rejeitada; a direção sugere relato da sexta |
| Sem manchetes de preço (3,2% das notícias) | A correlação cai de 0,13 para 0,07, mas segue significativa |
| Retorno anormal (Ibovespa) | Sobrevive (r = 0,109, p = 0,0001) |
| Placebo entre empresas | Cruzada ≈ 0; própria > cruzada (p = 0,0001) |
| Granger diário (5 defasagens) | Nenhum sentido sustentado |

**Conclusão até aqui:**
- A causa comum (mercado) está praticamente descartada.
- O relato pesa bastante.
- Sobra uma parte informativa cuja direção, no mesmo dia, não dava para separar.

---

## 2. Revisão da literatura (02/10/2026)

A cota de buscas na web da sessão tinha acabado. A pesquisa foi feita pelas
APIs acadêmicas OpenAlex, Crossref, OpenAIRE e DOAJ, e cada referência foi
conferida pelo DOI. O arquivo completo está em
`docs/literatura_causalidade.md`: 29 referências conferidas (uma, Duarte et al., com dúvida sobre o ano do fascículo).

**O que a literatura diz:**

- **Brasil:**
  - Araújo et al. (2018), com o Ibovespa de 2007 a 2015, concluíram que os
    preços afetam mais as notícias do que o contrário.
  - Souza e Martins (REGE) acharam correlação no mesmo dia e nenhuma relação
    defasada, o mesmo padrão do InvestAI.
  - Carosia et al. (2021) acharam Granger no sentido notícia → mercado.
- **Exterior:**
  - Strauß et al. (2016), com preços de abertura e Granger: os jornais
    refletem o mercado.
  - Strauß et al. (2018), com VAR intradiário: o efeito mais forte aparece em
    até 1 hora.
  - Boudoukh et al. (2019): a informação fundamental das notícias explica
    49,6% da volatilidade overnight, contra 12,4% no pregão.
  - Hendershott et al. (2015): investidores institucionais negociam ANTES da
    notícia.
- **Métodos que separam a direção:**
  1. Retorno overnight (fechamento → abertura) contra retorno do pregão,
     cruzado com o horário de publicação.
  2. Estudo de eventos com preço hora a hora em volta do horário da notícia.
  3. Granger/VAR, que já foi feito no diário e deu nulo.

**Armadilha para a interpretação:** preço que se mexe ANTES da publicação
indica relato, mas pode também ser negociação informada antes da notícia
(Hendershott et al., 2015). Não dá para separar essas duas coisas.
Preço que se mexe DEPOIS da publicação é o sinal mais limpo de notícia → preço.

---

## 3. Dados novos e decisões tomadas sem olhar nenhum retorno

- **Barras de 60 minutos** do Yahoo (`scripts/23_baixar_intradiario.py`):
  os 8 ativos e o Ibovespa, de 30/10/2023 a 01/10/2026. São 7 barras por dia
  (10h às 16h), cobrindo todo o período das notícias de 2024 a 2026.
- **Qualidade da abertura diária:**
  - Ações: abertura sempre dentro da faixa mínima/máxima; igual ao fechamento
    anterior em ≤ 1,7% dos dias. **Confiável.**
  - Ibovespa (Yahoo): abertura igual ao fechamento anterior em **29,6%** dos
    dias, e alguns dias com abertura zero. **Não confiável.**
  - **Decisão:** nos testes de abertura, o "mercado" é a média das outras
    ações, sem a própria (retorno ajustado ao mercado, β = 1).
- **Contagem de notícias com hora real do Google** (sem nenhum retorno):
  - fora do pregão (18h às 10h, inclusive fim de semana): 401 notícias, 188
    pares ativo-dia;
  - dentro do pregão, das 11h às 15h59: 250 notícias, 187 pares.
  - Isso dá um menor r detectável de ~0,20. É pouco poder para o teste mais
    forte.
- **Ampliação dos horários via API do WordPress**
  (`scripts/24_horarios_wordpress.py`). Muitos sites brasileiros rodam
  WordPress, que tem uma API pública que devolve a hora oficial de publicação
  (date_gmt). O script testa ~90 sites da amostra e, nos que têm a API aberta,
  procura cada manchete pelo título (similaridade ≥ 0,85). Só lê metadados.
  **Validação planejada:** comparar com as horas do Google nas notícias que
  têm as duas.

- **Horários da busca web:** 84 horas achadas nas linhas 1 a 165 da
  planilha. Duas são linhas de controle e ficam fora. Elas entram só na
  sensibilidade, por causa da divergência de 6 horas numa linha de controle.

## 4. Pré-registro mestre (02/10/2026)

Arquivo: `docs/pre-registro_2026-10-02_fase-causal.md`, enviado no chat antes
de qualquer teste com retorno.

- **Família principal com Holm:**
  - P1: notícia do dia → abertura do dia seguinte;
  - P2 e P3: notícia da noite → abertura seguinte e ← pregão passado;
  - P4 e P5: notícia no pregão → hora seguinte e ← hora anterior;
  - P6, P7 e P8: réplicas em 2021-2023;
  - P9: fim de semana → abertura de segunda.
- **Secundárias:**
  - S4: controle positivo (manchetes de relato);
  - S5: falsificação (dia errado);
  - S7: perfil hora a hora.

## 5. Implementação e verificação do código (02/10/2026)

- **Arquivos:**
  - `modulos/analise/causal.py`: decomposição do retorno, barras horárias,
    teste de correlação parcial agrupado com permutação em blocos de data, e
    Holm;
  - `scripts/25_fase_causal.py`: roda tudo.
- **Teste de código com sentimento embaralhado:** tudo roda e nada aparece
  significativo depois do Holm.
- **Bug encontrado e corrigido no teste de código:** a réplica P8 só cobria
  2023, porque o retorno anormal era calculado só a partir da janela de
  estimação. Agora o mesmo α e β (estimados em 2023) valem para todo o
  período.
- **Calibração:** 60 rodadas com sentimento embaralhado. Falso positivo:
  P1 2%, P2 8%, P3 2%, P4 0%, P5 2%, P6 2%, P7 5%, P8 3%, P9 7%, contra o
  nominal de 5% ± 2,8 pontos. Compatível.

## 6. Resultados: análise principal pré-registrada (horas do Google)

Arquivo: `resultados/fase_causal_<data>.txt`. Rodado no PC do Maurício e
repetido no servidor. Os r e n deram idênticos e os p-valores iguais até a
2ª casa decimal; a diferença mínima vem do dashboard aberto, que atualiza o
cache de preços.

| Teste | r | p | p Holm | Decisão |
|---|---|---|---|---|
| P1 notícia do dia → abertura seguinte (com controles) | +0,011 | 0,48 | 1,00 | não rejeita (n = 4.047, poder alto) |
| P2 notícia da noite → abertura seguinte | +0,113 | 0,075 | 0,48 | não rejeita (n = 254) |
| P3 notícia da noite ← pregão passado (relato) | +0,121 | 0,057 | 0,45 | não rejeita (n = 254) |
| P4 notícia no pregão → hora seguinte | +0,042 | 0,57 | 1,00 | não rejeita (n = 190) |
| P5 notícia no pregão ← hora anterior | +0,103 | 0,19 | 0,97 | não rejeita (n = 189) |
| P6 réplica de P1, 2021-23 | +0,007 | 0,36 | 1,00 | não rejeita |
| P7 réplica do Teste 1 (informativas), 2021-23 | +0,029 | 0,069 | 0,48 | não rejeita |
| **P8 réplica do Teste 3 (retorno anormal), 2021-23** | **+0,077** | **0,0001** | **0,0009** | **REJEITA** |
| P9 fim de semana → abertura de segunda | +0,007 | 0,87 | 1,00 | não rejeita |

**Secundárias:**
- **S1:** a janela da abertura até a notícia deu r = +0,134 (p = 0,09); a da
  notícia até o fechamento deu r = +0,061 (p = 0,46).
- **S5 (falsificação, dia errado):** r = −0,062, p = 0,41. Nulo, como deveria.
- **S6 (réplica do placebo em 2021-23):** própria +0,079 contra cruzada
  −0,021, p = 0,001. **Replicou.**
- **S4 (controle positivo):** amostra pequena demais, n = 8 a 9.

**Leitura:**
- A associação do mesmo dia é real, é da empresa e **se repete em outro
  período** (P8, S6).
- Nos testes de direção com hora do Google, nada passou no Holm, porque o
  poder era baixo (n ≈ 190-254, menor r detectável ≈ 0,20). As estimativas de
  relato (P3, P5, S1 antes) são positivas e maiores que as de notícia → preço
  (P4, S1 depois).
- **A notícia não prevê a abertura seguinte** (P1, P6, P9 ≈ 0). P1 e P6
  tinham poder alto, então esse nulo é informativo.

## 7. Análise adicional A1 (Google + WordPress filtrado, desvio declarado no adendo 1)

São 4.998 notícias com hora (4.047 do WordPress, 951 do Google), cerca de
5 vezes mais que na principal.

| Teste | r | p | p Holm dentro da A1 | n |
|---|---|---|---|---|
| A1_P2 noite → abertura seguinte | +0,013 | 0,60 | 0,60 | 1.642 |
| **A1_P3 noite ← pregão passado (relato)** | **+0,083** | **0,0009** | **0,004** | 1.642 |
| A1_P4 pregão → hora seguinte | +0,036 | 0,23 | 0,45 | 1.159 |
| **A1_P5 pregão ← hora anterior (relato/vazamento)** | **+0,091** | **0,003** | **0,009** | 1.155 |

- **Controle positivo (S4):** as manchetes de relato da noite acompanham o
  pregão passado (r = +0,36, p = 0,02, n = 40). As de relato no pregão
  acompanham a hora anterior (r = +0,22, p = 0,13, n = 55; direção certa, n
  pequeno). **O método enxerga o relato óbvio.**
- **Falsificação (S5):** r = +0,041, p = 0,18. Nulo.
- **Perfil hora a hora:** nas 3 horas ANTES da publicação, o terço mais
  positivo acumula **+0,33%** de retorno anormal e o terço mais negativo
  acumula −0,10%. Na hora da publicação não há salto no sentido do sentimento.
  Depois dela há uma leve devolução (−0,08% no terço positivo). Gráfico:
  `resultados/perfil_horario_noticias.png`.

## 8. Exploratório (decidido DEPOIS de ver os resultados; não confirmatório)

`scripts/27_exploratorio_pos_resultado.py`, com os horários da A1:

| Análise | r | p | n |
|---|---|---|---|
| E1: só notícias INFORMATIVAS, noite ← pregão passado | +0,061 | 0,015 | 1.624 |
| E1: só INFORMATIVAS, pregão ← hora anterior | +0,072 | 0,020 | 1.111 |
| E2: só INFORMATIVAS, pregão → hora seguinte | +0,024 | 0,42 | 1.115 |
| **E3: da abertura do dia até a hora da notícia** | **+0,159** | **0,0001** | 1.160 |
| E3: do fim da hora da notícia até o fechamento | +0,040 | 0,19 | 1.160 |

**Leitura:** não são só as manchetes óbvias. **Até as notícias informativas
saem depois do movimento do preço.** O movimento do dia até a notícia acompanha
fortemente o sentimento; o que vem depois da notícia, não.

## 9. Síntese: o que foi possível concluir

**A direção que os dados mostram é preço → notícia.** O preço se move primeiro
e a notícia vem depois, no mesmo sentido. Não apareceu nenhum sinal de que a
notícia antecipe o preço.

A cadeia de evidências:

1. **A associação é real e da própria empresa.** D+0 em 6 de 8 ativos. Ela
   sobrevive ao desconto do mercado (Teste 3), **se repete em 2021-2023** (P8,
   p Holm = 0,0009) e o placebo própria > cruzada também se repete (S6).
2. **Com horário exato, o preço se move ANTES da notícia:**
   - A1_P3, p = 0,0009;
   - A1_P5, p = 0,003;
   - E3, r = 0,16, p = 0,0001;
   - também sem as manchetes de relato (E1).
   - O controle positivo funciona e a falsificação dá nula.
3. **Nenhum sinal de notícia → preço:**
   - P1 (r = 0,011, com poder para 0,044) e a réplica P6;
   - A1_P2 (0,013), A1_P4 (0,036) e P9 (0,007).
4. **É coerente com a teoria e com a literatura:**
   - a hipótese de mercado eficiente na forma semiforte (Fama, 1970): quando a
     notícia pública sai, o preço já se ajustou;
   - Araújo et al. (2018), no Ibovespa: os preços afetam mais as notícias do
     que o contrário;
   - Strauß et al. (2016): os jornais refletem o mercado.

**Grau de evidência, na linguagem fixada no pré-registro:**
- Na **análise principal pré-registrada**, nenhum teste de direção passou na
  correção de Holm, por falta de poder.
- Na **análise adicional declarada**, com 5 vezes mais notícias, o relato deu
  significativo e a notícia → preço deu nula. As estimativas da principal
  apontam na mesma direção.
- É **evidência consistente de precedência do preço sobre a notícia**. Não é
  prova "100%". Nenhum estudo observacional dá isso.

**O que NÃO se conclui:**
- **Que notícia nunca move preço.** A informação original (fato relevante,
  balanço) certamente move. O que os dados mostram é que, quando a *matéria
  de imprensa* sai, o preço já andou. Efeitos menores que r ≈ 0,07-0,08 não
  podem ser descartados.
- **Que "preço antes da notícia" é sempre um jornalista copiando o preço.**
  Também pode ser negociação informada antes da publicação (Hendershott et
  al., 2015). Nos dois casos, quem lê a notícia chega depois do preço.

## 10. Limitações

- **Hora do Google:** às vezes é a hora de indexação, que atrasa até horas.
  Isso empurra os testes com hora do Google para o lado do relato. Na A1, 80%
  das horas vêm da API dos próprios sites (hora oficial de publicação), e o
  padrão se mantém.
- **Casamento com o WordPress:** 94% de concordância depois do filtro de data
  (n = 100). Sobram alguns erros.
- **Resolução de 60 minutos:** a hora da publicação fica fora dos testes,
  porque mistura o antes e o depois. Uma reação em poucos minutos não seria
  vista pelo P4. No perfil descritivo não há salto nessa hora no sentido do
  sentimento (terço positivo +0,008%, negativo +0,030%), mas só dados de
  minuto confirmariam.
- **Medida de sentimento:** na checagem preliminar da Fase E (seção 13), o
  léxico acerta ~61% e tem kappa 0,39 (razoável) contra o consenso de dois
  anotadores automáticos. A rotulagem humana ainda falta. O erro de medida
  enfraquece as correlações nas duas direções.
- **Amostra:** 8 ações grandes e muito líquidas. Em ações pequenas a mídia
  pode pesar mais (Fang; Peress, 2009).
- **O efeito causal da mídia em si** (Engelberg; Parsons, 2011) exige
  experimento natural e não é testável aqui.

## 11. Para a banca, em uma frase

> "A correlação entre sentimento e retorno existe, é da própria empresa e se
> repete em outro período. Mas, olhando o horário exato de 5 mil notícias e o
> preço hora a hora, o preço se move ANTES da notícia, e a notícia não
> antecipa o preço. A imprensa reflete o mercado, como prevê a hipótese de
> mercado eficiente."

## 12. Próximos passos que fariam diferença

1. **Dados de minuto:** o Yahoo dá barras de 1 minuto dos últimos 7 dias e de
   5/15 minutos dos últimos 60 dias. Coletar daqui para frente notícias com
   hora exata e barras de minuto permite medir a reação DENTRO da hora da
   publicação, que é o único ponto cego deste desenho.
2. **Coleta prospectiva com hora oficial:** feeds e API dos sites, a partir de
   agora.
3. **Validar o léxico com rotulagem humana** (Fase E). A checagem
   preliminar foi feita (seção 13). Falta Leonardo e Maurício rotularem as
   planilhas deles.
4. **Repetir em ações de menor liquidez.**

## 13. Fase E — validação do léxico (02/10/2026, resultado PRELIMINAR)

**Pergunta:** quando o léxico diz que uma manchete é positiva, negativa ou
neutra, uma pessoa concordaria?

**Como foi feito** (pré-registro escrito antes de qualquer rótulo:
`docs/pre-registro_2026-10-02_validacao-do-lexico.md`):
- 300 manchetes únicas, 100 de cada classe do léxico, sorteadas com semente
  42. O `scripts/28_amostra_validacao_lexico.py` refaz a mesma planilha, byte
  a byte.
- Planilha embaralhada e **sem** o escore do léxico.
- Dois anotadores automáticos (Claude, duas rodadas independentes, uma na
  ordem normal e outra na ordem inversa). Cada rodada só leu o protocolo e a
  planilha.
- Leonardo e Maurício: planilhas prontas, ainda não rotuladas.

**Resultados** (`resultados/validacao_lexico_preliminar_claude_2026-10-02.txt`):
- **Anotadores entre si:** 95% iguais, kappa 0,92 (quase perfeita).
  Cuidado: são duas rodadas do mesmo modelo. Isso mostra que o protocolo é
  aplicado de forma consistente, não que duas pessoas concordariam.
- **Léxico x consenso** (285 manchetes em que os dois concordaram):
  - acerta 59% na amostra; reponderado para a população, 61% (IC95%
    54%-68%);
  - kappa 0,39 (razoável), IC95% 0,31-0,47;
  - precisão: negativo 56%, neutro 62%, positivo 60%;
  - Spearman entre o escore e o rótulo: 0,58 (p = 0,0001).
- **Sensibilidade** (discordâncias contadas como neutro): quase igual
  (acurácia na população 61%, kappa 0,37).

**Onde o léxico erra** (matriz de confusão):
- **Quase nunca inverte o sinal.** Das 98 que ele chamou de negativas, só 7
  eram positivas. Das 92 positivas, 9 eram negativas.
- **O erro típico envolve o neutro:**
  - dá direção a manchete neutra (36 das 98 "negativas" e 28 das 92
    "positivas" eram neutras);
  - perde a direção (das 95 "neutras", 19 eram negativas e 17 positivas).
- **Na população** (complementar, não pré-registrado): o léxico só pega 29%
  das manchetes que os anotadores julgam negativas e 45% das positivas. O
  resto ele chama de neutro.

**O que isso muda na conclusão:**
- O léxico é um termômetro **ruidoso, mas que aponta para o lado certo**: o
  escore cresce junto com o rótulo e o sinal raramente é trocado.
- Erro de medida **enfraquece** as correlações: as verdadeiras devem ser
  maiores que as medidas. Isso vale para os dois sentidos, porque preço →
  notícia e notícia → preço usam o mesmo escore. Então, supondo que o erro do
  léxico não dependa do retorno, o ruído sozinho não explica a assimetria
  encontrada (um sentido significativo, o outro nulo).
- Mas reforça a cautela: um efeito notícia → preço pequeno pode ter ficado
  escondido pelo ruído. **"Não detectado" não é "zero".**

**Limite desta etapa:** a referência é um modelo de linguagem, não pessoas.
Vale como checagem preliminar. A validação de verdade é a rotulagem de
Leonardo e Maurício, que se roda com
`python scripts/29_validacao_lexico.py --humanos`.
