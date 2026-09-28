"""
noticias.py
-----------
Coleta de notícias financeiras com SUPORTE A HISTÓRICO.

Por que Google News e não o RSS comum:
    - O RSS de um portal (Infomoney, Valor...) só devolve os ~7 dias mais
      recentes. Não dá para montar série histórica com isso.
    - O Google News RSS aceita os operadores de busca "after:" e "before:",
      o que libera ANOS de notícias antigas.

Por que isso importa para o TCC:
    Para provar que "notícia influencia preço" é preciso comparar MUITAS
    notícias com MUITOS dias de preço. Com 7 dias não há amostra suficiente
    para nenhum teste estatístico ter validade.
"""

import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import quote_plus
import time
import re


# ─────────────────────────────────────────────────────────
# 1. TERMOS DE BUSCA POR TICKER
# ─────────────────────────────────────────────────────────
# Cada ticker tem um termo PRINCIPAL (usado na busca no Google News)
# e termos SECUNDÁRIOS (usados para confirmar que a notícia é mesmo do ativo).

TERMOS_BUSCA = {
    "PETR4.SA": {
        "principal": "Petrobras",
        "confirmacao": ["petrobras", "petr4", "petr3", "pré-sal", "presal"],
    },
    "VALE3.SA": {
        "principal": "Vale mineradora",
        "confirmacao": ["vale", "vale3", "minério de ferro", "mineradora"],
    },
    "ITUB4.SA": {
        "principal": "Itaú Unibanco",
        "confirmacao": ["itaú", "itau", "itub4", "unibanco"],
    },
    "BBDC4.SA": {
        "principal": "Bradesco",
        "confirmacao": ["bradesco", "bbdc4", "bbdc3"],
    },
    "WEGE3.SA": {
        "principal": "WEG empresa",
        "confirmacao": ["weg", "wege3"],
    },
    "MGLU3.SA": {
        "principal": "Magazine Luiza",
        "confirmacao": ["magazine luiza", "magalu", "mglu3"],
    },
    "ABEV3.SA": {
        "principal": "Ambev",
        "confirmacao": ["ambev", "abev3"],
    },
    "BBAS3.SA": {
        "principal": "Banco do Brasil",
        "confirmacao": ["banco do brasil", "bbas3"],
    },
    # ATENÇÃO ao montar termos de confirmação: "localiza" também é forma
    # verbal ("o app localiza o endereço"), então o termo isolado deixaria
    # entrar notícia que não é da empresa. Aqui exige-se contexto.
    # NOTA: os termos abaixo se mostraram RESTRITIVOS DEMAIS na prática —
    # renderam apenas 39 notícias em 33 dias, abaixo do mínimo de 60
    # observações, e o ativo ficou fora da amostra final. O termo isolado
    # "localiza" traria muito ruído (é forma verbal), mas exigir a expressão
    # completa descarta manchetes legítimas. Um meio-termo a testar em
    # trabalhos futuros: aceitar "localiza" quando acompanhado de contexto
    # financeiro na mesma frase.
    "RENT3.SA": {
        "principal": "Localiza Rent a Car aluguel de carros",
        "confirmacao": ["rent3", "localiza rent", "localiza hertz",
                        "locadora localiza", "localiza s.a", "localiza fleet"],
    },
    # ELET3 permanece aqui apenas para reprodutibilidade da coleta já
    # realizada. O ticker foi extinto (Eletrobras -> Axia Energia, AXIA3,
    # novembro/2025) e o ativo não entra na amostra final por ausência de
    # série de preços. Ver a nota em modulos/coleta/precos.py.
    "ELET3.SA": {
        "principal": "Eletrobras",
        "confirmacao": ["eletrobras", "elet3", "elet6", "furnas", "chesf"],
    },
    "SUZB3.SA": {
        "principal": "Suzano papel celulose",
        "confirmacao": ["suzano", "suzb3", "celulose"],
    },

    # ─────────────────────────────────────────────────────────
    # B3SA3 foi DELIBERADAMENTE excluída do estudo. Três motivos:
    #
    #   1. Ambiguidade: "b3" colide com vitamina B3, códigos, blocos...
    #   2. Confusão semântica: "Bolsa fecha em queda" é notícia sobre o
    #      MERCADO, não sobre a empresa que opera a bolsa. O filtro não
    #      consegue separar as duas coisas.
    #   3. Endogeneidade: o Event Study desconta o Ibovespa para isolar o
    #      efeito da notícia — mas o Ibovespa é o índice DA B3. Além disso,
    #      a receita da empresa vem do volume negociado, então o sentimento
    #      de mercado a atinge por um canal econômico diferente do das
    #      demais empresas.
    #
    # "B3SA3.SA": {"principal": "B3 bolsa", "confirmacao": ["b3", ...]},
    # ─────────────────────────────────────────────────────────
}


def _termos(ticker: str) -> Dict:
    """Devolve os termos de busca de um ticker, com fallback genérico."""
    if ticker in TERMOS_BUSCA:
        return TERMOS_BUSCA[ticker]
    base = ticker.replace(".SA", "")
    return {"principal": base, "confirmacao": [base.lower()]}


# ─────────────────────────────────────────────────────────
# 2. COLETA HISTÓRICA VIA GOOGLE NEWS RSS
# ─────────────────────────────────────────────────────────

def _montar_url_google_news(termo: str, data_ini: datetime, data_fim: datetime) -> str:
    """
    Monta a URL do RSS do Google News com filtro de data.

    O Google News aceita operadores de busca dentro do parâmetro q:
        after:AAAA-MM-DD   -> notícias publicadas DEPOIS dessa data
        before:AAAA-MM-DD  -> notícias publicadas ANTES dessa data

    hl / gl / ceid definem idioma e região (Brasil, português).
    """
    query = f"{termo} after:{data_ini:%Y-%m-%d} before:{data_fim:%Y-%m-%d}"
    return (
        "https://news.google.com/rss/search"
        f"?q={quote_plus(query)}"
        "&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    )


def _limpar_html(texto: str) -> str:
    """Remove tags HTML e espaços sobrando."""
    if not texto:
        return ""
    limpo = BeautifulSoup(texto, "html.parser").get_text(" ")
    return re.sub(r"\s+", " ", limpo).strip()


def coletar_historico(
    tickers: List[str],
    data_inicio: str,
    data_fim: Optional[str] = None,
    janela_dias: int = 30,
    pausa_seg: float = 1.0,
    verbose: bool = True,
    callback_progresso=None,
) -> pd.DataFrame:
    """
    Coleta notícias HISTÓRICAS para cada ticker, fatiando o período em janelas.

    Por que fatiar em janelas de 30 dias?
        O Google News devolve no máximo ~100 resultados por consulta.
        Se pedirmos "2 anos de uma vez", perdemos quase tudo.
        Pedindo mês a mês, coletamos muito mais notícias.

    Args:
        tickers: ex. ["PETR4.SA", "VALE3.SA"]
        data_inicio: "2024-01-01"
        data_fim: "2025-12-31" (padrão = hoje)
        janela_dias: tamanho de cada fatia de busca
        pausa_seg: pausa entre requisições (evita bloqueio por excesso)
        callback_progresso: função opcional chamada a cada janela concluída.
            Recebe um dicionário com o andamento, permitindo que o Streamlit
            (ou qualquer outra interface) desenhe uma barra de progresso real:

                {
                  "fracao": 0.42,           # 0 a 1, para a barra
                  "ticker": "PETR4.SA",
                  "ticker_atual": 2,        # índice do ativo em processamento
                  "ticker_total": 5,
                  "periodo": "03/2024",     # mês sendo coletado
                  "passo": 17,              # janelas já concluídas
                  "passo_total": 40,
                  "noticias_ate_agora": 312,
                  "segundos_restantes": 145.0,
                }

    Returns:
        DataFrame com: ticker, data, titulo, resumo, fonte, url
    """
    dt_ini = pd.to_datetime(data_inicio).to_pydatetime()
    dt_fim = pd.to_datetime(data_fim).to_pydatetime() if data_fim else datetime.now()

    # ---- Calcula quantas janelas serão necessárias no TOTAL ----
    # Precisamos disso ANTES de começar, para a barra saber o denominador.
    dias_totais = max(1, (dt_fim - dt_ini).days)
    janelas_por_ticker = max(1, -(-dias_totais // janela_dias))  # divisão para cima
    passo_total = janelas_por_ticker * len(tickers)

    registros = []
    passo = 0
    inicio_exec = time.time()

    for idx_ticker, ticker in enumerate(tickers, start=1):
        cfg = _termos(ticker)
        termo = cfg["principal"]
        confirmacao = cfg["confirmacao"]
        total_ticker = 0

        # Fatia o período total em janelas menores
        cursor = dt_ini
        while cursor < dt_fim:
            janela_fim = min(cursor + timedelta(days=janela_dias), dt_fim)
            url = _montar_url_google_news(termo, cursor, janela_fim)

            try:
                feed = feedparser.parse(url)

                for entry in feed.entries:
                    titulo = entry.get("title", "")
                    resumo = _limpar_html(entry.get("summary", ""))

                    # Confirma que a notícia é realmente sobre o ativo
                    texto = f"{titulo} {resumo}".lower()
                    if not any(kw in texto for kw in confirmacao):
                        continue

                    # Data de publicação
                    data_pub = None
                    if getattr(entry, "published_parsed", None):
                        data_pub = datetime(*entry.published_parsed[:6])
                    elif getattr(entry, "updated_parsed", None):
                        data_pub = datetime(*entry.updated_parsed[:6])
                    if data_pub is None:
                        continue

                    # Fonte: o Google News põe o veículo no campo source
                    fonte = "Google News"
                    if hasattr(entry, "source"):
                        fonte = getattr(entry.source, "title", fonte)

                    registros.append({
                        "ticker": ticker,
                        "data": data_pub,
                        "titulo": titulo,
                        "resumo": resumo[:500],
                        "fonte": fonte,
                        "url": entry.get("link", ""),
                    })
                    total_ticker += 1

            except Exception as e:
                if verbose:
                    print(f"  [aviso] {ticker} {cursor:%Y-%m}: {e}")

            # ---- Reporta o progresso desta janela ----
            passo += 1
            if callback_progresso is not None:
                decorrido = time.time() - inicio_exec
                # Estimativa simples: tempo médio por passo x passos restantes
                media = decorrido / passo
                restantes = (passo_total - passo) * media
                try:
                    callback_progresso({
                        "fracao": min(1.0, passo / passo_total),
                        "ticker": ticker,
                        "ticker_atual": idx_ticker,
                        "ticker_total": len(tickers),
                        "periodo": f"{cursor:%d/%m/%y} – {janela_fim:%d/%m/%y}",
                        "passo": passo,
                        "passo_total": passo_total,
                        "noticias_ate_agora": len(registros),
                        "segundos_restantes": restantes,
                    })
                except Exception:
                    pass  # a interface nunca pode derrubar a coleta

            cursor = janela_fim
            time.sleep(pausa_seg)  # respeita o servidor

        if verbose:
            print(f"[OK] {ticker}: {total_ticker} notícias coletadas")

    if not registros:
        print("[AVISO] Nenhuma notícia coletada. Verifique conexão/período.")
        return pd.DataFrame(
            columns=["ticker", "data", "titulo", "resumo", "fonte", "url"]
        )

    df = pd.DataFrame(registros)
    df = df.drop_duplicates(subset=["ticker", "titulo"])
    df["data"] = pd.to_datetime(df["data"])
    # data_pregao = só a data (sem hora), usada para casar com o preço do dia
    df["data_pregao"] = df["data"].dt.normalize()
    df = df.sort_values("data").reset_index(drop=True)

    print(f"\n[TOTAL] {len(df)} notícias de {df['ticker'].nunique()} ativos")
    print(f"        Período: {df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}")
    return df


# ─────────────────────────────────────────────────────────
# 3. AJUSTE PARA HORÁRIO DE PREGÃO
# ─────────────────────────────────────────────────────────

def ajustar_data_pregao(
    noticias: pd.DataFrame,
    hora_fechamento: int = 17,
) -> pd.DataFrame:
    """
    Ajusta a data da notícia para o pregão em que ela pode ter efeito.

    Regra (importante para a validade do estudo!):
        - Notícia publicada ANTES do fechamento (17h) -> afeta o pregão do MESMO dia
        - Notícia publicada DEPOIS do fechamento      -> afeta o pregão do dia SEGUINTE
        - Notícia de sábado/domingo                    -> afeta a segunda-feira

    Sem esse ajuste, você compara uma notícia da noite de terça com o preço
    de terça — que já fechou. Isso inverteria a causalidade e invalidaria
    a conclusão do TCC.
    """
    df = noticias.copy()
    df["data"] = pd.to_datetime(df["data"])

    # Passo 1: notícia após o fechamento vale para o dia seguinte
    apos_fechamento = df["data"].dt.hour >= hora_fechamento
    df["data_pregao"] = df["data"].dt.normalize()
    df.loc[apos_fechamento, "data_pregao"] += pd.Timedelta(days=1)

    # Passo 2: fim de semana empurra para segunda-feira
    #   weekday(): 5 = sábado, 6 = domingo
    dias_ate_segunda = df["data_pregao"].dt.weekday.map({5: 2, 6: 1}).fillna(0)
    df["data_pregao"] += pd.to_timedelta(dias_ate_segunda, unit="D")

    return df


# ─────────────────────────────────────────────────────────
# 4. COLETA RECENTE (a que alimenta o dashboard)
# ─────────────────────────────────────────────────────────

def coletar_recentes(
    tickers: List[str],
    dias_atras: int = 7,
    pausa_seg: float = 1.0,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Notícias dos últimos N dias, para a visão "estado atual" do dashboard.

    Diferença para coletar_historico:
        Esta é a mesma coleta, com o período amarrado a uma janela curta que
        termina hoje. Não é um coletor separado — chama coletar_historico por
        baixo, de propósito. Ter dois coletores diferentes significaria que a
        tela e o estudo poderiam divergir sem ninguém perceber.

    A coluna tickers_mencionados existe porque a interface filtra por ativo.
    Como a busca é feita UM TICKER POR VEZ, o ativo da notícia é o termo que
    a trouxe — não há detecção de menção no texto, e não deve haver: inferir
    de qual empresa a notícia fala pelo conteúdo é um problema de outra
    natureza, e erraria em silêncio.

    Returns:
        DataFrame com ticker, data, titulo, resumo, fonte, url,
        tickers_mencionados — ordenado da mais recente para a mais antiga.
    """
    colunas = ["ticker", "data", "titulo", "resumo", "fonte", "url",
               "tickers_mencionados"]

    dias = max(1, int(dias_atras))
    data_inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

    df = coletar_historico(
        tickers=tickers,
        data_inicio=data_inicio,
        janela_dias=dias,     # janela única: o período já é curto
        pausa_seg=pausa_seg,
        verbose=verbose,
    )

    if df is None or df.empty:
        return pd.DataFrame(columns=colunas)

    df = df.copy()
    df["tickers_mencionados"] = df["ticker"].apply(lambda t: [t])
    return df.sort_values("data", ascending=False).reset_index(drop=True)


# ─────────────────────────────────────────────────────────
# 5. TESTE DO MÓDULO
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Teste: coleta histórica de notícias ===\n")

    noticias = coletar_historico(
        tickers=["PETR4.SA", "VALE3.SA"],
        data_inicio="2025-01-01",
        data_fim="2025-04-01",
        janela_dias=30,
    )

    if not noticias.empty:
        noticias = ajustar_data_pregao(noticias)
        print("\nAmostra:")
        print(noticias[["ticker", "data", "data_pregao", "titulo"]].head(10).to_string())
        noticias.to_csv("noticias_historico.csv", index=False)
        print("\n[OK] Salvo em noticias_historico.csv")
