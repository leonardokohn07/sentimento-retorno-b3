# Como conferir os resultados do InvestAI (passo a passo)

Este guia é para qualquer pessoa — avaliador da feira, professor, outro
estudante — que queira conferir, com as próprias mãos, que os números do
estudo saem dos dados e do código, e não de escolhas feitas depois.

## O que você precisa

1. Esta pasta do projeto (o repositório git).
2. O pacote de dados congelados `dados_congelados_2026-10-02.zip` (19 MB),
   dentro da pasta `verificacao/`.
   - Ele **não** fica no GitHub público, porque contém texto de notícias e
     séries de preço de terceiros. Os autores entregam o pacote a quem
     pedir (pen drive na feira, ou por e-mail).
   - Mesmo sem o pacote, a **impressão digital** de cada arquivo está
     publicada no git (`verificacao/manifesto_dados_congelados_2026-10-02.sha256`).
     Assim dá para provar que o pacote entregue é exatamente o que foi usado.
3. Python 3.10 ou mais novo, com `pip install -r requirements-analise.txt`.

## Conferir em 3 passos

**Passo 1 — os dados são os mesmos?** (1 minuto)

    python verificacao/verificar_tudo.py --so-dados

Confere o SHA-256 de cada um dos 75 arquivos. Se um único byte mudou, aparece
`[ALTERADO]` e a verificação para.

**Passo 2 — os resultados se refazem?** (10 a 60 minutos)

    python verificacao/verificar_tudo.py

No Windows: dois cliques em `VERIFICAR_TUDO.bat`.

O programa roda as 32 etapas de análise numa pasta separada, sem internet e
com o relógio fixado em 02/10/2026 12:00, e compara cada arquivo de
resultado com a referência em `verificacao/referencia/`. No fim aparece:

    RESULTADO: N de N saídas conferem com a referência; 0 diferentes; 0 etapas com erro.
    ==> TUDO REPRODUZIDO

O relatório completo fica em `verificacao/relatorio_verificacao.txt`.

**Passo 3 — os testes foram decididos antes?**

- Cada pré-registro está em `docs/pre-registro_*.md`.
- O `git log` mostra a data e a hora em que cada um entrou no repositório,
  **antes** do arquivo de resultado correspondente. Exemplo:

      git log --format="%h %ad %s" --date=iso -- docs/pre-registro_2026-10-02_fase-G_minuto_ADENDO-2.md resultados/fase_G_janelas_curtas_lexico_2026-10-02.txt

- `verificacao/registro_de_testes.csv` lista **todos** os testes, inclusive
  os que deram nulo, com o pré-registro de cada um.

## O que a verificação prova e o que ela não prova

| Prova | Não prova |
|---|---|
| Os números publicados saem destes dados e deste código. | Que os dados representam bem o mundo (isso é discutido nas limitações). |
| Nenhum número foi digitado à mão nem escolhido depois. | Que o mesmo resultado aparece com notícias futuras (isso é a coleta prospectiva). |
| O resultado não depende do computador nem da versão das bibliotecas testadas. | Causalidade: o estudo mede **precedência no tempo**. |

## Etapas

`python verificacao/verificar_tudo.py --listar` mostra as 32 etapas e o
comando de cada uma. Para rodar só algumas:

    python verificacao/verificar_tudo.py --etapas E03 E27
