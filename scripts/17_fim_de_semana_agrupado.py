# -*- coding: utf-8 -*-
"""
17_fim_de_semana_agrupado.py
----------------------------
Teste de causalidade pelo CALENDÁRIO, com os ativos agrupados.

Pré-registro: docs/pre-registro_2026-10-02_fim-de-semana-agrupado.md
(escrito ANTES de este script rodar sobre os dados reais).

A IDEIA
  Notícia de sábado ou domingo não pode estar relatando o pregão de
  segunda-feira, porque ele ainda não aconteceu. Se o sentimento dessas
  notícias se associa ao retorno de segunda, a ordem temporal é
  notícia -> preço, garantida pelo calendário e não pelo relógio.

POR QUE AGRUPAR
  O script 9 testava ativo por ativo, com 30 a 114 segundas-feiras cada.
  Com n = 60, só correlações acima de ~0,25 seriam detectáveis; o efeito do
  estudo está entre 0,10 e 0,20. Ativo por ativo, o teste não tinha poder.
  Agrupando os 8 ativos, o n passa a ser a soma das segundas-feiras.

COMO
  - Sentimento padronizado (z) dentro de cada ativo; retorno padronizado
    dentro de cada ativo.
  - Correlação de Pearson sobre o painel agrupado.
  - Inferência por permutação em BLOCOS DE DATA (10.000, semente 42):
    sorteia-se qual segunda-feira recebe os retornos de qual, levando os 8
    ativos juntos. Isso preserva o fato de que todos os ativos sobem e caem
    juntos na mesma segunda — permutar linha a linha subestimaria o p-valor.
  - Controle: o mesmo teste contra o retorno da SEXTA anterior. Notícia de
    fim de semana PODE estar relatando a sexta.

Uso, da pasta InvestAI:
    .\\venv\\Scripts\\python scripts\\17_fim_de_semana_agrupado.py
    .\\venv\\Scripts\\python scripts\\17_fim_de_semana_agrupado.py --extra dados\\noticias_2021_2023.csv --rotulo estendido
    .\\venv\\Scripts\\python scripts\\17_fim_de_semana_agrupado.py --sem-correcao-fuso --rotulo sensibilidade
"""
import argparse
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd
from scipy import stats

from modulos.analise.hipotese import montar_serie_diaria
from modulos.analise.fuso import ajustar_pregao_brasilia

ARQ_NOTICIAS = RAIZ / "dados" / "noticias_com_sentimento.csv"
PASTA_CACHE = RAIZ / "dados" / "cache_precos"
PASTA_RES = RAIZ / "resultados"
ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA",
          "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
N_PERM = 10_000
SEMENTE = 42
ALFA = 0.05


def carregar_retornos() -> pd.DataFrame:
    fech = {}
    for arq in sorted(PASTA_CACHE.glob("*_1d.csv")):
        fech[arq.name.replace("_1d.csv", "")] = pd.read_csv(
            arq, index_col=0, parse_dates=True)["Close"]
    precos = pd.DataFrame(fech)
    ret = np.log(precos / precos.shift(1)).dropna()
    ret.index = pd.to_datetime(ret.index).normalize()
    return ret


def pearson(x, y):
    x = x - x.mean(); y = y - y.mean()
    return float(x @ y / np.sqrt((x @ x) * (y @ y)))


def williams(r12, r13, r23, n):
    """Steiger (1980): compara duas correlações que compartilham a variável 1."""
    det = 1 - r12**2 - r13**2 - r23**2 + 2 * r12 * r13 * r23
    rb = (r12 + r13) / 2
    t = (r12 - r13) * np.sqrt(((n - 1) * (1 + r23)) /
                              (2 * ((n - 1) / (n - 3)) * det + rb**2 * (1 - r23)**3))
    return float(t), float(2 * stats.t.sf(abs(t), n - 3))


def mde(n, poder=0.80):
    """Menor correlação detectável com o poder pedido (bicaudal, 5%)."""
    return float(np.tanh((stats.norm.ppf(1 - ALFA / 2) + stats.norm.ppf(poder)) / np.sqrt(n - 3)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--sem-correcao-fuso", action="store_true")
    ap.add_argument("--rotulo", default="principal")
    ap.add_argument("--embaralhar-sentimento", action="store_true",
                    help="SÓ PARA TESTAR O CÓDIGO: destrói a relação real")
    ap.add_argument("--semente-embaralhar", type=int, default=0)
    ap.add_argument("--n-perm", type=int, default=N_PERM)
    ap.add_argument("--silencioso", action="store_true")
    args = ap.parse_args()

    linhas = []
    def p(s=""):
        if not args.silencioso:
            print(s)
        linhas.append(s)

    partes = [pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])]
    for e in args.extra:
        partes.append(pd.read_csv(RAIZ / e, parse_dates=["data", "data_pregao"]))
    noticias = pd.concat(partes, ignore_index=True)
    noticias = noticias[noticias["ticker"].isin(ATIVOS)]
    noticias = noticias.drop_duplicates(subset=["ticker", "titulo", "data"])

    if args.sem_correcao_fuso:
        dia = pd.to_datetime(noticias["data"]).dt.weekday
    else:
        noticias = ajustar_pregao_brasilia(noticias)
        dia = noticias["data_brasilia"].dt.weekday
    fds = noticias[dia >= 5].copy()

    if args.embaralhar_sentimento:
        rng0 = np.random.default_rng(args.semente_embaralhar)
        fds["score_polaridade"] = rng0.permutation(fds["score_polaridade"].to_numpy())

    retornos = carregar_retornos()
    blocos = []
    for t in ATIVOS:
        s = montar_serie_diaria(fds, retornos, t)
        if s.empty:
            continue
        s = s[["data", "sentimento", "n_noticias", "retorno_lag_0", "retorno_lag_-1"]].dropna()
        if len(s) < 3 or s["sentimento"].std() == 0:
            continue
        s["ticker"] = t
        blocos.append(s)
    painel = pd.concat(blocos, ignore_index=True)
    painel["data"] = pd.to_datetime(painel["data"]).dt.normalize()

    datas = np.array(sorted(painel["data"].unique()))
    pos = retornos.index.get_indexer(datas)
    tick = [t for t in ATIVOS if t in painel["ticker"].unique()]
    R0 = retornos.iloc[pos][tick].to_numpy()        # segunda (dia do pregão)
    R1 = retornos.iloc[pos - 1][tick].to_numpy()    # pregão anterior (sexta)
    z = lambda M: (M - M.mean(axis=0)) / M.std(axis=0, ddof=1)
    R0z, R1z = z(R0), z(R1)

    i_d = np.searchsorted(datas, painel["data"].to_numpy())
    i_a = painel["ticker"].map({t: k for k, t in enumerate(tick)}).to_numpy()
    x = painel.groupby("ticker")["sentimento"].transform(
        lambda v: (v - v.mean()) / v.std(ddof=1)).to_numpy()
    y0, y1 = R0z[i_d, i_a], R1z[i_d, i_a]
    n = len(x)

    r0, r1, r01 = pearson(x, y0), pearson(x, y1), pearson(y0, y1)
    rng = np.random.default_rng(SEMENTE)
    c0 = c1 = 0
    for _ in range(args.n_perm):
        perm = rng.permutation(len(datas))
        if abs(pearson(x, R0z[perm[i_d], i_a])) >= abs(r0): c0 += 1
        if abs(pearson(x, R1z[perm[i_d], i_a])) >= abs(r1): c1 += 1
    p0, p1 = (c0 + 1) / (args.n_perm + 1), (c1 + 1) / (args.n_perm + 1)
    tw, pw = williams(r0, r1, r01, n)

    p("=" * 78)
    p(f"  FIM DE SEMANA AGRUPADO — rótulo: {args.rotulo}"
      + ("   [SENTIMENTO EMBARALHADO — TESTE DE CÓDIGO]" if args.embaralhar_sentimento else ""))
    p("=" * 78)
    p(f"  Correção de fuso         : {'NÃO (sensibilidade)' if args.sem_correcao_fuso else 'sim'}")
    p(f"  Arquivos extras          : {', '.join(args.extra) if args.extra else 'nenhum'}")
    p(f"  Período das notícias     : {noticias['data'].min():%d/%m/%Y} a {noticias['data'].max():%d/%m/%Y}")
    p(f"  Notícias de fim de semana: {len(fds)}")
    p(f"  Pares ativo-segunda (n)  : {n}   |   fins de semana distintos: {len(datas)}")
    p(f"  Menor r detectável (80%) : {mde(n):.3f}  (supondo independência; é otimista)")
    p("")
    p("  Por ativo (descritivo, sem inferência):")
    p(f"    {'ativo':<9} {'n':>4} {'r segunda':>10} {'r sexta':>9}")
    for t in tick:
        q = painel[painel["ticker"] == t]
        p(f"    {t:<9} {len(q):>4} {np.corrcoef(q['sentimento'], q['retorno_lag_0'])[0,1]:>10.4f}"
          f" {np.corrcoef(q['sentimento'], q['retorno_lag_-1'])[0,1]:>9.4f}")
    p("")
    p("  AGRUPADO (z dentro do ativo, permutação em blocos de data):")
    p(f"    H0-A  sentimento fds x retorno SEGUNDA : r = {r0:+.4f}   p = {p0:.4f}")
    p(f"    H0-B  sentimento fds x retorno SEXTA   : r = {r1:+.4f}   p = {p1:.4f}")
    p(f"    Williams (segunda vs sexta)            : t = {tw:+.3f}   p = {pw:.4f}")
    p("")
    a_rej, b_rej = p0 < ALFA, p1 < ALFA
    if a_rej and r0 > 0 and not b_rej:
        v = ("H0-A rejeitada com r > 0 e controle não significativo: compatível com "
             "notícia -> preço, sem sinal de que o fim de semana esteja relatando a sexta.")
    elif a_rej and b_rej:
        v = ("H0-A e H0-B rejeitadas. "
             + ("Segunda significativamente maior que sexta (Williams): predomina notícia -> preço."
                if (pw < ALFA and r0 > r1) else
                "Segunda não é significativamente maior que sexta: inconclusivo quanto à direção."))
    elif a_rej and r0 < 0:
        v = "H0-A rejeitada, mas com r NEGATIVO: não sustenta a hipótese; reportar como achado inesperado."
    elif b_rej:
        v = ("Só o controle (sexta) é significativo: o fim de semana parece RELATAR o pregão "
             "anterior. Evidência de preço -> notícia.")
    else:
        v = (f"Nenhuma rejeitada. Não é evidência de ausência de efeito: o teste só detectaria "
             f"r acima de ~{mde(n):.3f}.")
    p("  VEREDITO (regra pré-registrada):")
    p("    " + v)
    p("=" * 78)

    PASTA_RES.mkdir(exist_ok=True)
    suf = "_TESTE_CODIGO" if args.embaralhar_sentimento else ""
    arq = PASTA_RES / f"fim_de_semana_agrupado_{args.rotulo}{suf}_{date.today().isoformat()}.txt"
    if args.silencioso:
        print(f"CALIB {p0:.4f} {p1:.4f}")
        return
    arq.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\nsalvo em: resultados/{arq.name}")


if __name__ == "__main__":
    main()
