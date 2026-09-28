# InvestAI — sentimento de notícias × retorno de ações na B3

Estudo estatístico que testa se o tom das notícias sobre uma empresa se
relaciona com o retorno da sua ação — e em qual defasagem essa relação
aparece.

> Trabalho acadêmico de conclusão de curso técnico. **Não é recomendação de
> investimento.** O estudo mede associação entre variáveis; não estabelece
> causalidade nem prevê preços.

Leonardo Kohn e Maurício Renck Gedrat · Orientador: Prof. Raul Mesquita
Fundação Escola Técnica Liberato Salzano Vieira da Cunha · 2026

---

## Resultado

19.410 notícias · 8 ações de 7 setores · 32 meses (2024–2026) · α = 0,05
fixado antes da coleta.

| Ativo | n | r (D+0) | p (D+0) | H₀ em D+0 | r (D+1) | p (D+1) | H₀ em D+1 |
|---|---:|---:|---:|:--|---:|---:|:--|
| ABEV3 | 462 | 0,0641 | 0,1689 | não rejeita | 0,0404 | 0,3867 | não rejeita |
| BBDC4 | 657 | 0,1006 | 0,0099 | **rejeita** | −0,0048 | 0,9023 | não rejeita |
| ITUB4 | 551 | 0,0541 | 0,2048 | não rejeita | 0,0012 | 0,9784 | não rejeita |
| MGLU3 | 512 | 0,1607 | 0,0003 | **rejeita** | −0,0268 | 0,5462 | não rejeita |
| PETR4 | 650 | 0,1442 | 0,0002 | **rejeita** | −0,0384 | 0,3284 | não rejeita |
| SUZB3 | 349 | 0,1421 | 0,0078 | **rejeita** | −0,0613 | 0,2540 | não rejeita |
| VALE3 | 583 | 0,1965 | 0,0000 | **rejeita** | 0,0376 | 0,3649 | não rejeita |
| WEGE3 | 367 | 0,1961 | 0,0002 | **rejeita** | 0,0765 | 0,1440 | não rejeita |

**No mesmo pregão (D+0): 6 de 8 rejeitam H₀**, com p médio de 0,0031 entre os
significativos, e os seis vêm de seis setores diferentes.
**No dia seguinte (D+1): 0 de 8.**

O sentimento anda junto com o preço, mas não anda na frente — resultado
coerente com a hipótese de eficiência de mercado em sua forma semiforte.

### Controle negativo: o resultado sobrevive ao acaso?

O sentimento foi embaralhado entre os dias 10.000 vezes (semente 42), o que
destrói o pareamento notícia–dia e mostra quanta correlação aparece só por
sorte. Nos 8 ativos, o p empírico da permutação concordou com o p da fórmula.
Na VALE3, nenhum dos 10.000 embaralhamentos alcançou o valor observado.

![Permutação da VALE3](resultados/banner_permutacao_VALE3.SA.png)

---

## Como o estudo foi feito

- **Hipótese e α escritos antes da coleta** (06/08/2026, no caderno de campo),
  com as duas defasagens já previstas: mesmo pregão e dia seguinte.
- **Unidade de medida:** a notícia — cada manchete recebe um escore sozinha.
  **Unidade de análise:** o par ativo-dia, porque o retorno só existe por
  pregão.
- **Amostra por critério anotado antes de rodar:** no máximo 2 ativos por
  setor, porque empresas do mesmo setor não são casos independentes.
- **Mínimo de 60 observações por ativo**, derivado de análise de poder
  (com 20 observações o poder era de 32%; com 60 passa de 80%, convenção de
  Cohen, 1988) — não é número arbitrado.
- **Validação do módulo estatístico:** 1.000 simulações com dados sintéticos
  de resposta conhecida — 100% de detecção com efeito presente e 5,0% de
  falso positivo sem efeito, igual ao α adotado. A correlação prevista
  analiticamente (0,3592) bateu com a medida (0,3599).
- **Controle negativo:** teste de permutação com 10.000 embaralhamentos.

## Limitações declaradas

- **95,7% dos horários das notícias vêm normalizados pela fonte.** Sem hora
  real não é possível determinar se a notícia precedeu ou sucedeu o movimento
  do preço. Por isso o trabalho afirma associação, e não causa.
- **O léxico não foi validado contra rotulagem humana.** O que foi validado
  foi o método estatístico, não o instrumento de medida.
- **O que se mede é o tom (polaridade) da cobertura jornalística**, não o
  sentimento do investidor, que é um construto distinto, medido por pesquisas
  de opinião e fluxo de capital.

## Próximos passos

1. Teste de defasagem negativa (D−1): se o sentimento se associa ao retorno do
   dia anterior, parte da relação é jornalismo reagindo ao preço.
2. Backtest honesto da estratégia com sinal de D+1, contra buy-and-hold e com
   custos — a expectativa, dado o resultado acima, é que não supere.
3. Notícias por setor como segunda variável: o que move o preço, a notícia da
   empresa ou o clima do setor?
4. Fatos Relevantes da CVM, que têm horário oficial de protocolo — é o caminho
   para atacar a limitação principal.
5. Validação do léxico com 200 manchetes rotuladas à mão (kappa de Cohen) e
   comparação com o FinBERT-PT-BR.

---

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
streamlit run dashboard.py
```

Scripts do estudo, a partir da pasta `InvestAI/`:

| Script | O que faz |
|---|---|
| `scripts/1_validar_modulo_estatistico.py` | Valida o módulo com dados sintéticos (1.000 simulações) |
| `scripts/2_coletar_e_analisar.py` | Coleta notícias e preços e calcula o sentimento |
| `scripts/7_curvas_de_deteccao.py` | Curvas de poder estatístico por tamanho de amostra |
| `scripts/9_teste_fim_de_semana.py` | Tentativa de contornar a limitação de horário |
| `scripts/12_teste_permutacao.py` | Controle negativo: 10.000 permutações por ativo |
| `scripts/congelar_resultados.py` | Recalcula o resultado a partir dos dados locais — teste de regressão do estudo |
| `scripts/diagnostico_ativos.py` | Mostra por que um ativo entrou ou ficou fora da análise |

## Estrutura

```
InvestAI/
├── dashboard.py              aplicação Streamlit — só o estudo
├── modulos/
│   ├── coleta/               notícias (RSS) e preços (yfinance, com cache local)
│   └── analise/
│       ├── sentimento.py     léxico de 300 termos, com negação e intensificadores
│       ├── hipotese.py       testes estatísticos do estudo
│       └── avaliacao.py      retorno acumulado, drawdown e Sharpe (para o backtest)
├── scripts/                  os experimentos, numerados
├── resultados/               figuras e tabelas geradas
└── dados/                    dados locais (não versionados)
```

## Sobre os dados

O repositório **não** inclui o texto das notícias coletadas (conteúdo de
terceiros) nem as séries de preços do Yahoo Finance. O que fica versionado são
o código, as figuras e as tabelas de resultado. Rodando os scripts de coleta,
os dados são reconstruídos.

## Histórico

A versão apresentada na FEICIT 2026 incluía também um módulo de análise de
risco de carteiras (volatilidade, beta, VaR, Markowitz e um classificador de
perfil). Ele foi removido em 28/09/2026: não era objeto do estudo, e decisões
como o score 60/40 não tinham referência que as sustentasse. Esse código
continua acessível no histórico, na tag `feicit-2026`.

## Referências

- FAMA, E. F. Efficient capital markets: a review of theory and empirical work.
  *The Journal of Finance*, v. 25, n. 2, p. 383–417, 1970.
- SOUZA, D. M. S. de; MARTINS, O. S. Brazilian stock market performance and
  investor sentiment on Twitter. *Revista de Gestão*, v. 31, n. 1, p. 18–33,
  2024. DOI: 10.1108/REGE-07-2021-0145.
- COHEN, J. *Statistical power analysis for the behavioral sciences*. 2. ed.
  Hillsdale: Lawrence Erlbaum, 1988.

## Licença

MIT — ver [LICENSE](LICENSE).
