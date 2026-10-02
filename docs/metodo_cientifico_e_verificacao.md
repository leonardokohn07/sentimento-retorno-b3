# Método científico e verificação — como tornar o estudo "confirmável"

**Data:** 02/10/2026.

## 1. "100% comprovado" não existe; "100% verificável", sim

Nenhuma pesquisa com dados do mundo real prova uma conclusão com 100% de
certeza. Sempre sobra alguma chance de acaso, de erro de medida ou de uma
explicação que ninguém pensou. Na estatística, isso aparece no p-valor e no
intervalo de confiança; na eletrônica, aparece na incerteza de toda medição
(nenhum multímetro mede a tensão "exata").

O que dá para alcançar é outra coisa, e é isso que a banca valoriza:

> **Qualquer pessoa, com os mesmos dados e o mesmo código, chega aos mesmos
> números. E qualquer pessoa consegue conferir que as regras do teste foram
> escritas antes de olhar o resultado.**

Isso é **verificabilidade** (ou reprodutibilidade). É o máximo que a ciência
oferece, e o InvestAI agora tem isso de forma completa.

## 2. A escada da confirmação

Cada degrau responde a uma desconfiança diferente. Quanto mais degraus, mais
forte a conclusão.

| Degrau | A desconfiança | O que responde | Status |
|---|---|---|---|
| 1. Reprodução | "Esses números saem mesmo desses dados?" | verificador de um comando | **feito** |
| 2. Dados intactos | "E se os dados foram mexidos depois?" | impressão digital SHA-256 de cada arquivo | **feito** |
| 3. Regras antes | "E se vocês escolheram o teste depois de ver?" | pré-registros datados no git | **feito** (falta carimbo público, item 4) |
| 4. Carimbo público | "E se a data do git foi forjada?" | publicar no GitHub e no Zenodo (DOI com data) | **a fazer** (5 minutos) |
| 5. Todos os testes | "E se esconderam os que deram errado?" | registro de testes com os 279 resultados, nulos inclusive | **feito** |
| 6. Outra máquina | "Só funciona no computador de vocês?" | mesma verificação em Linux e Windows | **feito** (seção 5) |
| 7. Outros dados | "Vale fora desta amostra?" | réplica em 2021-2023 e em *small caps* | **feito** |
| 8. Dados futuros | "Vale para notícias que ainda nem existiam?" | coleta prospectiva com regra de parada | **em andamento** (a partir de 03/10/2026) |
| 9. Medida humana | "O termômetro de sentimento mede certo?" | rotulagem de vocês dois | **em andamento** |
| 10. Outra equipe | "E se o erro for de vocês?" | alguém de fora refaz com o pacote | **a fazer** (pode ser um professor) |

## 3. O que foi construído hoje

### 3.1 Dados congelados com impressão digital

- `verificacao/dados_congelados_2026-10-02.zip`: os 75 arquivos de dados
  usados nas análises (19 MB). Não vai para o GitHub público, porque tem
  texto de notícias e preços de terceiros.
- `verificacao/manifesto_dados_congelados_2026-10-02.sha256`: o SHA-256 de
  cada arquivo. **Este vai para o git.**

**O que é SHA-256:** uma função que transforma qualquer arquivo numa
"impressão digital" de 64 caracteres. Mude um único byte e a impressão
digital muda completamente. É impossível, na prática, criar outro arquivo
com a mesma impressão digital. Funciona como o lacre de um medidor de
energia: se o lacre está intacto, ninguém mexeu.

**Por que congelar foi necessário (descoberta de hoje):** comparando os
dados do PC do Leonardo com os do servidor, todos os arquivos eram idênticos
**menos os preços diários** (`dados/cache_precos/`). O motivo: cada vez que o
painel baixa preços do Yahoo, o Yahoo recalcula os preços ajustados por
dividendos dos dias antigos (diferença na 7ª casa decimal), e o cache é
reescrito. Isso explica as diferenças na 4ª casa decimal de alguns p-valores
entre a rodada de 01/10 e as de hoje. Com os dados congelados, essa fonte de
variação acabou.

### 3.2 O verificador

`python verificacao/verificar_tudo.py` (ou dois cliques em
`VERIFICAR_TUDO.bat`):

1. confere o SHA-256 dos 75 arquivos;
2. monta uma pasta separada com os dados congelados (os dados do dia a dia
   não são tocados);
3. roda as **32 etapas** de análise, do teste de alinhamento até as *small
   caps*;
4. compara cada saída com a referência.

Dois detalhes técnicos que fazem a comparação ser exata:
- **Relógio parado** (`verificacao/_relogio_congelado.py`): os scripts põem a
  data do dia no nome dos arquivos. O verificador faz o computador "achar"
  que é sempre 02/10/2026 12:00, como o *trigger* de um osciloscópio que
  congela a tela num instante. Assim os arquivos saem com o mesmo nome em
  qualquer dia.
- **Sem internet para preços** (`INVESTAI_SO_CACHE=1`): dois scripts antigos
  (9 e 12) baixavam preços do Yahoo. Agora, no modo de verificação, eles só
  leem o arquivo congelado. Fora da verificação, nada mudou.

### 3.3 A referência bate com o que foi publicado

A referência foi gerada a partir dos dados congelados e comparada com os
arquivos que já estavam em `resultados/` (47 arquivos de texto e tabela):

- **44 idênticos**, letra por letra (descontada só a data no nome);
- **3 com diferença mínima**, todos explicados pelo cache de preços:
  - `congelado`: o número de pregões no cabeçalho (1.254 contra 1.250; o
    cache tem 4 dias a mais). Todos os r e p são iguais;
  - `curva_defasagem` (CSV): dois p-valores na 4ª casa (0,3794 × 0,3793 e
    0,2997 × 0,2998);
  - `exploratorio_pos_resultado`: E1 noite deu r = 0,0612 e p = 0,0143,
    contra 0,0611 e 0,0152 na rodada de 01/10.
- Nenhuma conclusão muda.

### 3.4 O registro de testes

`verificacao/registro_de_testes.csv` (abre no Excel): **279 linhas**, uma por
teste, montadas automaticamente a partir das saídas
(`verificacao/montar_registro_de_testes.py`). Para cada teste: etapa do
verificador, fase, pré-registro, tipo, pergunta, r, p, p de Holm, n, menor
efeito detectável e decisão.

Os tipos deixam claro o peso de cada resultado:
- **confirmatório:** a hipótese e a regra foram escritas antes;
- **análise adicional declarada:** desvio do plano, avisado num adendo
  antes de rodar;
- **secundário, robustez, sensibilidade:** previstos no pré-registro, sem
  correção;
- **exploratório:** decidido depois de ver os resultados. Serve para gerar
  hipóteses, não para confirmar;
- **calibração e validação:** testes do próprio instrumento.

## 4. O que ainda falta para subir os últimos degraus

1. **Carimbo público (degrau 4), o mais urgente e o mais fácil:**
   - fazer o `git push` dos commits para o GitHub. A data dos commits passa
     a estar num servidor de terceiros;
   - (opcional, recomendado) ligar o repositório ao **Zenodo**, que gera um
     DOI com data para cada versão. Isso dá um registro permanente e citável
     de que o pré-registro existia antes da coleta prospectiva.
2. **Coleta prospectiva (degrau 8):** dar dois cliques em
   `scripts/AGENDAR_COLETA_DIARIA.bat` antes de 03/10. A regra de parada já
   está escrita.
3. **Rotulagem humana (degrau 9):** as duas planilhas em
   `dados/validacao_lexico/`, sem olhar a do outro. Depois:
   `python scripts/29_validacao_lexico.py --humanos` e
   `python scripts/35_validacao_modelos.py --humanos`.
4. **Replicação independente (degrau 10):** entregar o pacote (pasta do
   projeto + zip dos dados) a um professor e pedir que ele rode
   `VERIFICAR_TUDO.bat`. Se der "TUDO REPRODUZIDO" no computador dele, vocês
   podem dizer na feira que um terceiro verificou.

## 5. Reprodução em máquinas diferentes

| Máquina | Sistema | Python | numpy | pandas | scipy | Resultado |
|---|---|---|---|---|---|---|
| Servidor (onde a referência foi gerada) | Linux | 3.11.15 | 2.4.4 | 3.0.2 | 1.17.1 | 99 de 99 conferem |
| PC do Leonardo | **Windows 11** | **3.14.4** | 2.5.2 | 3.0.5 | 1.18.1 | **99 de 99 conferem** |
| VM Linux no PC do Leonardo | Linux | 3.10.12 | 2.2.6 | 2.3.3 | 1.15.3 | 93 de 99: as 6 diferentes são o perfil hora a hora descritivo (S7) das etapas E16 e E18; todos os testes estatísticos saíram idênticos (seção 22) |

No Windows, das 99 saídas:
- **64 idênticas letra por letra** (todos os resultados em texto, com os r, p
  e n que aparecem no diário e no plano);
- **15 tabelas/JSON iguais com diferença menor que 1e-9**. A maior diferença
  relativa foi 5,4 × 10⁻¹⁴, ou seja, na 14ª casa significativa. É o
  arredondamento do processador (a soma de números com vírgula pode mudar na
  última casa conforme a ordem das contas), e não muda nenhum valor
  impresso;
- **20 imagens** geradas (só a existência é conferida, porque o desenho muda
  com a versão do matplotlib).

**Por que isso importa:** as duas máquinas têm sistemas, versões do Python e
versões de todas as bibliotecas diferentes. Mesmo assim os números saem
iguais. Isso mostra que o resultado não depende do computador de vocês.

**Na VM Linux (pandas 2.3.3), a verificação achou dois problemas reais:**
1. Cinco etapas quebravam: com pandas 2.x, o código do teste agrupado
   (`modulos/analise/painel.py` e `scripts/17`) comparava datas de tipos
   diferentes. Foi corrigido convertendo as datas para um tipo só
   (`datetime64[ns]`). No servidor e no Windows, os resultados continuaram
   idênticos depois da correção.
2. O **perfil hora a hora** da análise principal (um gráfico descritivo, não
   um teste) muda um pouco: muitas manchetes têm o mesmo escore, e a ordem em
   que o pandas desempata essas manchetes mudou entre as versões 2 e 3. Isso
   muda qual manchete cai na fronteira entre os terços (por exemplo, 51 em vez
   de 52 eventos num ponto). Todos os r, p e n dos testes saíram idênticos.

Isso é exatamente para o que o verificador serve: ele achou, sozinho, uma
dependência de versão que ninguém tinha visto.

Os relatórios completos estão em `verificacao/relatorio_verificacao_*.txt`.

## 6. Para a banca, em uma frase

> "Não dá para provar nada 100% com dados reais, mas o nosso estudo é 100%
> verificável: os dados estão lacrados com impressão digital, as regras foram
> registradas antes de cada teste, e um único comando refaz os 279 testes e
> confere que tudo bate — inclusive num computador diferente do nosso."
