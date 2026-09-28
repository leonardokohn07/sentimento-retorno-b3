"""
Pacote 'modulos' — todo o código do InvestAI.

Organização:

    modulos/
    ├── coleta/          De onde vêm os dados
    │   ├── precos.py    Preços das ações (yfinance)
    │   └── noticias.py  Notícias históricas (Google News)
    │
    ├── analise/         O que é calculado com os dados
    │   ├── risco.py     Volatilidade, Beta, VaR, Sharpe, Markowitz
    │   ├── sentimento.py Sentimento das notícias — motor único do
    │   │                 projeto; também agrega por ativo e gera alertas
    │   └── hipotese.py   Testes estatísticos da hipótese
    │
    └── integracao.py    Painel com risco + sentimento lado a lado
                         (sem score combinado — decisão de 15/09/2026)
"""
