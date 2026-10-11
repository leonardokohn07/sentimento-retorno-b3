# -*- coding: utf-8 -*-
"""
congelados.py
-------------
Acesso aos DADOS do estudo, para o dashboard refazer contas ao vivo.

Qual arquivo é lido
    1. verificacao/dados_congelados_2026-10-02.zip, se existir. É o pacote
       congelado, o mesmo que o verificador usa: com ele, as contas refeitas
       na tela dão EXATAMENTE os números do relatório. O zip é lido direto,
       sem extrair nada.
    2. Senão, a pasta dados/ (a coleta local). As contas funcionam, mas os
       números podem diferir um pouco, porque os preços são atualizados.
    3. Se nenhum dos dois existir (quem baixou o repositório do GitHub, que
       não traz os dados de terceiros), as páginas de dados avisam e as de
       resultados continuam funcionando, porque leem a referência.

As contas usam as MESMAS funções do estudo (modulos/analise/hipotese.py),
na mesma ordem e com a mesma semente dos scripts originais.
"""
import hashlib
import io
import zipfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from modulos.analise.hipotese import (MIN_OBSERVACOES, montar_serie_diaria,
                                      regressao_sentimento_retorno)
from modulos.analise.validacao_lexico import tirar_fonte

RAIZ = Path(__file__).resolve().parent.parent
ZIP = RAIZ / "verificacao" / "dados_congelados_2026-10-02.zip"
MANIFESTO = RAIZ / "verificacao" / "manifesto_dados_congelados_2026-10-02.sha256"
PASTA = RAIZ / "dados"
FORA_DA_AMOSTRA = {"ELET3.SA", "RENT3.SA"}     # saíram da amostra (relatório, seção 3.4)
SEMENTE, N_PERM = 42, 10000                    # as de scripts/12_teste_permutacao.py


def fonte() -> str:
    """'zip', 'pasta' ou '' (sem dados)."""
    if ZIP.exists():
        return "zip"
    if (PASTA / "noticias_com_sentimento.csv").exists():
        return "pasta"
    return ""


def descricao_fonte() -> str:
    f = fonte()
    if f == "zip":
        return "pacote de dados congelados de 02/10/2026 (o mesmo do verificador)"
    if f == "pasta":
        return "pasta dados/ (coleta local; pode diferir um pouco do congelado)"
    return "sem dados locais"


@lru_cache(maxsize=1)
def _nomes_zip() -> frozenset:
    with zipfile.ZipFile(ZIP) as z:
        return frozenset(z.namelist())


def _ler_zip(nome: str) -> bytes:
    # Um ZipFile por leitura: o Streamlit roda cada sessão numa thread, e um
    # mesmo ZipFile aberto não deve ser lido por duas threads ao mesmo tempo.
    with zipfile.ZipFile(ZIP) as z:
        return z.read(nome)


def _existe(rel: str) -> bool:
    if fonte() == "zip":
        return f"dados/{rel}" in _nomes_zip()
    return (PASTA / rel).exists()


def _abrir(rel: str):
    """rel é o caminho dentro de dados/, ex.: 'cache_precos/PETR4.SA_1d.csv'."""
    if fonte() == "zip":
        return io.BytesIO(_ler_zip(f"dados/{rel}"))
    return open(PASTA / rel, "rb")


def _listar(prefixo: str) -> list:
    if fonte() == "zip":
        return sorted(n[len("dados/"):] for n in _nomes_zip()
                      if n.startswith(f"dados/{prefixo}") and not n.endswith("/"))
    pasta = PASTA / prefixo
    return sorted(f"{prefixo}{p.name}" for p in pasta.glob("*") if p.is_file()) if pasta.is_dir() else []


# ─────────────────────────────────────────────────────────
# Notícias e preços
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def noticias_todas() -> pd.DataFrame:
    """As 19.410 notícias do arquivo, inclusive as de ELET3 e RENT3 (fora da amostra).
    É assim que os scripts originais leem; quem filtra é a falta de preço ou de dias."""
    with _abrir("noticias_com_sentimento.csv") as f:
        return pd.read_csv(f, parse_dates=["data", "data_pregao"])


@lru_cache(maxsize=1)
def noticias() -> pd.DataFrame:
    """As 18.463 notícias dos 8 ativos da amostra principal, com o escore do FinBERT ao lado."""
    n = noticias_todas()
    n = n[~n["ticker"].isin(FORA_DA_AMOSTRA)].copy()
    n["ativo"] = n["ticker"].str.replace(".SA", "", regex=False)
    n["manchete"] = [tirar_fonte(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    fb = escores_finbert()
    if fb is not None:
        n["finbert"] = n["manchete"].map(fb)
    else:
        n["finbert"] = np.nan
    return n.reset_index(drop=True)


@lru_cache(maxsize=1)
def escores_finbert():
    """manchete -> P(positivo) − P(negativo), como em modulos/analise/modelos.py."""
    if not _existe("sentimento_finbert.csv"):
        return None
    with _abrir("sentimento_finbert.csv") as f:
        d = pd.read_csv(f)
    d = d.drop_duplicates("manchete", keep="last")
    return pd.Series((d["finbert_positive"] - d["finbert_negative"]).to_numpy(),
                     index=d["manchete"].astype(str))


@lru_cache(maxsize=1)
def precos_fechamento() -> pd.DataFrame:
    """Fechamento diário de cada ativo (dados/cache_precos/)."""
    fech = {}
    for rel in _listar("cache_precos/"):
        if not rel.endswith("_1d.csv"):
            continue
        tk = rel.split("/")[-1].replace("_1d.csv", "")
        with _abrir(rel) as f:
            df = pd.read_csv(f, index_col=0, parse_dates=True)
        fech[tk] = df["Close"]
    return pd.DataFrame(fech)


@lru_cache(maxsize=1)
def retornos() -> pd.DataFrame:
    """Mesma conta de scripts/congelar_resultados.py: retorno logarítmico do
    fechamento, e o dia só entra se TODOS os ativos tiverem preço."""
    p = precos_fechamento()
    return np.log(p / p.shift(1)).dropna()


@lru_cache(maxsize=16)
def serie_diaria(ticker: str) -> pd.DataFrame:
    """Um registro por pregão com notícia: sentimento médio, nº de notícias e retornos."""
    return montar_serie_diaria(noticias_todas(), retornos(), ticker)


# ─────────────────────────────────────────────────────────
# Contas refeitas ao vivo
# ─────────────────────────────────────────────────────────

def refazer_resultado_original() -> pd.DataFrame:
    """Refaz a etapa E03: r e p clássicos em D−1, D+0 e D+1 para cada ativo."""
    linhas = []
    for tk in sorted(noticias_todas()["ticker"].dropna().unique()):
        if tk not in retornos().columns:
            continue
        s = serie_diaria(tk)
        if len(s) < MIN_OBSERVACOES:
            continue
        l = {"ativo": tk.replace(".SA", ""), "n": len(s)}
        for lag, rot in ((-1, "dm1"), (0, "d0"), (1, "d1")):
            reg = regressao_sentimento_retorno(s, lag=lag)
            l[f"r_{rot}"], l[f"p_{rot}"] = reg["r"], reg["p_valor"]
        linhas.append(l)
    return pd.DataFrame(linhas)


def refazer_permutacoes(ao_avancar=None) -> dict:
    """Refaz a etapa E04: 10.000 embaralhamentos por ativo, semente 42.

    Os ativos são percorridos na mesma ordem do script original, com UM
    gerador aleatório para todos; por isso os p-valores saem idênticos aos
    da referência. ao_avancar(fração, ativo) atualiza a barra de progresso.
    """
    rng = np.random.default_rng(SEMENTE)
    tks = sorted(noticias_todas()["ticker"].dropna().unique())
    validos = [tk for tk in tks if tk in retornos().columns and len(serie_diaria(tk)) >= MIN_OBSERVACOES]
    saida = {}
    for i, tk in enumerate(validos):
        s = serie_diaria(tk).dropna(subset=["sentimento", "retorno"])
        sent = s["sentimento"].to_numpy(dtype=float)
        ret = s["retorno"].to_numpy(dtype=float)
        r_obs = np.corrcoef(sent, ret)[0, 1]
        nulos = np.empty(N_PERM)
        x = sent.copy()
        for k in range(N_PERM):
            rng.shuffle(x)
            nulos[k] = np.corrcoef(x, ret)[0, 1]
            if ao_avancar and k % 2500 == 0:
                ao_avancar((i + k / N_PERM) / len(validos), tk.replace(".SA", ""))
        p = (np.sum(np.abs(nulos) >= abs(r_obs)) + 1) / (N_PERM + 1)
        saida[tk.replace(".SA", "")] = {"r": r_obs, "p": p, "nulos": nulos, "n": len(s)}
    if ao_avancar:
        ao_avancar(1.0, "")
    return saida


def conferir_impressoes_digitais(ao_avancar=None) -> dict:
    """Recalcula o SHA-256 de cada arquivo congelado e compara com o manifesto."""
    if not (ZIP.exists() and MANIFESTO.exists()):
        return {"ok": 0, "total": 0, "diferentes": [], "faltando": [], "disponivel": False}
    esperado = {}
    for l in MANIFESTO.read_text(encoding="utf-8").splitlines():
        if l.strip() and not l.startswith("#"):
            h, rel = l.split(None, 1)
            esperado["dados/" + rel.strip()] = h
    ok, dif, falta = 0, [], []
    with zipfile.ZipFile(ZIP) as z:
        nomes = set(z.namelist())
        for i, (rel, h) in enumerate(sorted(esperado.items())):
            if rel not in nomes:
                falta.append(rel)
            elif hashlib.sha256(z.read(rel)).hexdigest() == h:
                ok += 1
            else:
                dif.append(rel)
            if ao_avancar:
                ao_avancar((i + 1) / len(esperado), rel)
    return {"ok": ok, "total": len(esperado), "diferentes": dif, "faltando": falta,
            "disponivel": True}
