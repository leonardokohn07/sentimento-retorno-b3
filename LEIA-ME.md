# InvestAI — Análise de Carteiras da B3 com IA

**TCC — Curso Técnico em Eletrônica, 4º ano**
Leonardo Kohn e Maurício Renck Gedrat · Orientador: Prof. Raul Mesquita
Fundação Escola Técnica Liberato Salzano Vieira da Cunha

Sistema que combina **análise quantitativa de risco** com **análise de
sentimento de notícias** para avaliar carteiras de ações da B3, e testa
estatisticamente a hipótese de que o sentimento das notícias se relaciona
com o retorno das ações.

---

## 🗺️ Onde fica cada coisa

```
InvestAI/
│
├── LEIA-ME.md              ← você está aqui
├── requirements.txt        Lista de bibliotecas a instalar
├── dashboard.py            ★ PROGRAMA PRINCIPAL (é o que você abre)
│
├── modulos/                O CÓDIGO do sistema
│   ├── caminhos.py         Define onde cada arquivo é salvo
│   ├── integracao.py       Painel com risco + sentimento lado a lado
│   │                       (sem score combinado — decisão de 15/09/2026)
│   │
│   ├── coleta/             ── DE ONDE VÊM OS DADOS ──
│   │   ├── precos.py       Preços das ações (yfinance)
│   │   └── noticias.py     Notícias históricas (Google News)
│   │
│   └── analise/            ── O QUE É CALCULADO ──
│       ├── risco.py        Volatilidade, Beta, VaR, Sharpe, Markowitz
│       ├── sentimento.py   Sentimento das notícias — motor único: léxico,
│       │                   agregação por ativo e alertas
│       └── hipotese.py     Testes estatísticos da hipótese
│
├── scripts/                PROGRAMAS DE TERMINAL
│   ├── 1_validar_modulo_estatistico.py   Valida o método com dados sintéticos
│   ├── 2_coletar_e_analisar.py           Pipeline completo do estudo
│   ├── 6_analisar_drawdown.py            Drawdown da carteira vs Ibovespa
│   ├── 7_curvas_de_deteccao.py           Até onde o instrumento enxerga
│   ├── 9_teste_fim_de_semana.py          Subamostra causalmente limpa
│   └── 12_teste_permutacao.py            Controle negativo (embaralhamento)
│
├── dados/                  ARQUIVOS BAIXADOS (gerados automaticamente)
│   └── noticias_com_sentimento.csv
│
└── resultados/             SAÍDAS PARA O TCC (gerados automaticamente)
    ├── resultado_hipotese.json
    ├── resultado_permutacao.txt
    ├── curvas_de_deteccao.png
    └── *.png               Demais gráficos
```

> As pastas `dados/` e `resultados/` se preenchem sozinhas conforme os
> scripts rodam.

### Por que a numeração dos scripts tem buracos

Os números são **históricos**: indicam a ordem em que cada rotina foi
escrita ao longo do projeto, e estão registrados assim no caderno de campo.
Os scripts 0, 3, 4, 5, 8, 10 e 11 eram de desenvolvimento (teste de
módulos, reprocessamento de cache, versionamento de resultados, coleta com
retomada) e foram arquivados em **18/09/2026** na pasta
`_arquivo_investai/`, um nível acima desta.

Renumerar apagaria esse rastro. Os buracos são informação, não descuido.

---

## ⚙️ Instalação (fazer uma vez só)

### 1. Liberar scripts no Windows

Abra o **PowerShell** e rode:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Confirme com `S`. Sem isso o Windows bloqueia o ambiente virtual.

### 2. Criar o ambiente virtual

```powershell
cd C:\Users\user\Downloads\InvestAI_v6\InvestAI
python -m venv venv
venv\Scripts\activate
```

Deu certo se aparecer `(venv)` no início da linha.

### 3. Instalar as bibliotecas

```powershell
pip install -r requirements.txt
```

> Se der erro no `torch`, **ignore**. Ele alimentaria o modelo neural de
> sentimento, que está desligado. Todo o estudo do TCC foi feito com o
> léxico — e é ele que está validado.

---

## ▶️ Como usar

### Opção A — Dashboard

```powershell
streamlit run dashboard.py
```

Abre no navegador em `http://localhost:8501`.

**As 6 abas:**

| Aba | O que mostra |
|-----|--------------|
| 📋 Visão Geral | Métricas da carteira e de cada ativo, separadas, com a referência de cada uma |
| 📉 Risco | Volatilidade, Beta, VaR, Sharpe, Drawdown |
| 📰 Sentimento | Notícias recentes classificadas |
| 🎯 Otimização | Markowitz — pesos ótimos sugeridos |
| ⚠️ Alertas | Pontos de atenção detectados |
| 🔬 Validação da Hipótese | **Os testes estatísticos do TCC** |

### Opção B — Scripts de terminal, na ordem metodológica

A ordem abaixo não é arbitrária: é a sequência de um protocolo de
pesquisa. Primeiro se valida o instrumento, depois se mede o alcance dele,
só então se coleta o dado real, e por último se tenta derrubar o próprio
resultado.

```powershell
# 1. O instrumento funciona?  (segundos, sem internet)
python scripts\1_validar_modulo_estatistico.py

# 2. Até onde ele enxerga?  (minutos, sem internet)
python scripts\7_curvas_de_deteccao.py

# 3. O estudo em si  (10-20 min, precisa de internet)
python scripts\2_coletar_e_analisar.py

# 4. Controle negativo — o resultado some quando deveria sumir?
python scripts\12_teste_permutacao.py

# 5. Robustez — e na subamostra sem ambiguidade causal?
python scripts\9_teste_fim_de_semana.py

# 6. Aprofundamento do risco — o tombo foi do mercado ou da carteira?
python scripts\6_analisar_drawdown.py
```

---

## 🔬 A hipótese do TCC

| | |
|---|---|
| **H₀** (nula) | O sentimento das notícias **não** se relaciona com o retorno das ações |
| **H₁** (alternativa) | O sentimento das notícias **se relaciona** com o retorno das ações |

Em estatística não se "prova" H₁ diretamente — tenta-se **rejeitar H₀**.
Se a probabilidade de o resultado ter surgido por acaso (o **p-valor**)
for menor que 0,05, rejeitamos H₀.

**Testes aplicados:**

1. **Correlação com defasagem** — existe relação? Em qual dia ela aparece?
2. **Teste t de Welch** — notícia boa rende mais que notícia ruim?
3. **Event Study** — desconta o Ibovespa para isolar o efeito da notícia
4. **Regressão linear** — quanto o sentimento explica do movimento?
5. **Teste de permutação** — controle negativo, ver abaixo

---

## 🧪 Validação do instrumento (antes dos dados reais)

O `1_validar_modulo_estatistico.py` roda 1000 simulações em dois cenários
com resposta conhecida:

| Cenário | Dados | O que se mede | Esperado |
|---|---|---|---|
| **A** | efeito real embutido (b = 0,010) | **poder** do teste | ≥ 80% |
| **B** | sentimento e retorno independentes | **erro tipo I** (falso positivo) | ~5% |

Como os parâmetros da simulação são conhecidos, a correlação esperada pode
ser derivada analiticamente: **r = 0,3592**. Se o valor medido bater com
esse, o módulo não só detecta o efeito — ele estima a magnitude certa.

O `7_curvas_de_deteccao.py` responde a pergunta seguinte: *até onde o
instrumento enxerga?* Varre tamanho de amostra e força de efeito e mostra
o menor efeito detectável em cada n.

Juntos, os dois respondem de forma empírica à pergunta mais perigosa da
banca: *"e se o seu resultado for só ruído?"*

---

## 🎲 O controle negativo (teste de permutação)

O `12_teste_permutacao.py` embaralha a coluna de sentimento 10.000 vezes e
refaz a correlação a cada vez. Embaralhar destrói o **pareamento** entre
sentimento e retorno, mas preserva as duas distribuições intactas.

Se a relação for real, ela precisa sumir quando o pareamento é destruído.

O p-valor que sai daí é **empírico**: a fração de embaralhamentos que
produziu correlação igual ou maior, em módulo, que a observada. Ele não
assume normalidade nem nada sobre a forma da distribuição — a única
suposição é que, sob H₀, o pareamento é arbitrário, que é literalmente o
enunciado da hipótese nula.

Se ele bater com o p-valor clássico, os dois métodos se corroboram por
caminhos independentes. Se divergirem, **o de permutação é o que vale**.

---

## ⚠️ Pontos importantes para a defesa

**Não existe mais um score único, e isso é argumento a favor, não
limitação.** Até 15/09/2026 o sistema mostrava um score integrado por
ativo, `risco × 0,6 + (risco + sentimento) × 0,4`. Os pesos 0,6 e 0,4
foram escolhidos por nós, sem base em literatura e sem calibração. Se
perguntarem por que o score saiu, a resposta tem três partes:

1. **Era arbitrário.** Trocar 0,6/0,4 por 0,5/0,5 mudava o ranking dos
   ativos e não havia argumento para defender uma escolha contra a outra.
2. **Somar apaga informação.** Volatilidade, Sharpe, VaR e drawdown medem
   riscos diferentes. Um ativo pode oscilar pouco no dia a dia e ter
   levado um tombo enorme uma vez — na média isso vira "risco médio", que
   não descreve nenhum dos dois casos. No sistema hoje dá para ver isso:
   o ativo mais volátil quase nunca é o de pior Sharpe.
3. **Contaminava o próprio estudo.** A hipótese do trabalho é testar *se*
   o sentimento se relaciona com o retorno. Embutir o sentimento no
   indicador de risco antes de testar isso é assumir a conclusão.

O que sobrou do lado da carteira é uma **faixa** (Baixo / Médio / Alto /
Muito Alto) vinda da contagem de critérios acionados, com os limiares
declarados na tela e cada ponto rastreável até a métrica que o gerou.
Faixa ordinal, não nota — não existe "62 de 100".

**Cada métrica de risco tem uma referência, e ela está no sistema.**
Na aba Visão Geral, o expansor *"Em que se baseia cada métrica de risco"*
mostra a tabela completa: o que a métrica mede, como ler, como é calculada
e de onde vem (Markowitz 1952, Sharpe 1964 e 1966, Jorion 2007,
Magdon-Ismail & Atiya 2004, Hirschman 1964). A resposta da banca está
dentro do programa, não só na cabeça de quem apresenta.

**Um motor de sentimento só.** Até 18/09/2026 a aba Sentimento rodava o
analisador versão 1 e o estudo da hipótese rodava o versão 2 — dois motores
diferentes sobre os mesmos dados, o que permitia a tela mostrar um número e
o estudo outro sem nada acusar a divergência. A versão 1 saiu do projeto e
agora o `sentimento.py` atende os dois. O ganho não é só de arrumação: o V2
trata negação, então *"Petrobras NÃO teve lucro"* agora é classificada como
negativa na tela também, e não mais como positiva por causa da palavra
"lucro".

**R² baixo é normal.** Valores entre 0,01 e 0,10 são o esperado nesta
literatura. O preço de uma ação depende de dezenas de fatores; o
sentimento é apenas um deles. O que valida a hipótese é o **p-valor**,
não a magnitude do R².

**Mostre os erros também.** Apresentar só os acertos é seleção enviesada,
e a banca vai perguntar. Ter a taxa geral de acerto documentada é o que
sustenta a conclusão.

**A conclusão correta é "se relaciona", nunca "determina" nem "prevê".**
A análise principal pareia notícia e retorno no mesmo pregão, o que não
separa *causou* de *relatou*. O `9_teste_fim_de_semana.py` existe
justamente para atacar esse ponto — e o resultado dele foi inconclusivo
por tamanho de amostra, não por ausência de efeito. Inconclusivo não é a
mesma coisa que negativo, e dizer isso na defesa conta a favor.

---

## 🔧 Problemas comuns

| Erro | Solução |
|------|---------|
| `python não é reconhecido` | Reinstale o Python marcando *"Add to PATH"* |
| `execução de scripts desabilitada` | Rode o `Set-ExecutionPolicy` do passo 1 |
| `ModuleNotFoundError: modulos` | Rode a partir da pasta `InvestAI/` |
| `0 notícias coletadas` | Bloqueio do Google. Em `modulos/coleta/noticias.py`, aumente `pausa_seg` de 1.0 para 2.0 |
| Erro ao instalar/importar `torch` | Ignore — o modo neural está desligado e o estudo usa o léxico |
| Alterei um módulo e o Streamlit não viu | O Streamlit guarda os módulos já importados em memória. Pare o servidor e rode de novo |

Para ver o que já foi gerado:

```powershell
python modulos\caminhos.py
```

---

*Sistema desenvolvido para fins educacionais e acadêmicos.
Não constitui recomendação de investimento.*
