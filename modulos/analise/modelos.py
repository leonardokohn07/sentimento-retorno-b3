# -*- coding: utf-8 -*-
"""
modelos.py — escores de sentimento dos modelos de linguagem (Fase F).

Os escores são calculados por scripts/30_sentimento_modelos.py (no Windows,
porque precisa baixar os modelos) e ficam em dados/sentimento_<modelo>.csv,
com uma coluna de probabilidade para cada rótulo do modelo.

Aqui eles viram as mesmas grandezas do léxico:
    escore = P(positivo) - P(negativo)      de -1 a +1 (como o score_polaridade)
    classe = o rótulo de maior probabilidade (positivo, negativo ou neutro)
"""
from pathlib import Path

import numpy as np
import pandas as pd

from modulos.analise.validacao_lexico import tirar_fonte

RAIZ = Path(__file__).resolve().parent.parent.parent
REPOSITORIOS = {
    "finbert": "lucas-leme/FinBERT-PT-BR",
    "distil": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
}
# Só é usado se o config.json do modelo não tiver nomes de rótulo legíveis
# (ex.: LABEL_0). Nesse caso, o mapeamento vem do cartão oficial do modelo.
MAPA_MANUAL = {}


def _rotulos(nome, colunas):
    """Acha, entre as colunas do arquivo, qual é positivo, negativo e neutro."""
    if nome in MAPA_MANUAL:
        return {k: f"{nome}_{v}" for k, v in MAPA_MANUAL[nome].items()}
    achados = {}
    for c in colunas:
        r = c[len(nome) + 1:]
        for chave, raiz in (("pos", "pos"), ("neg", "neg"), ("neu", "neu")):
            if raiz in r:
                achados[chave] = c
    if set(achados) != {"pos", "neg", "neu"}:
        raise ValueError(f"{nome}: não deu para identificar os rótulos em {list(colunas)}. "
                         "Preencha MAPA_MANUAL a partir do cartão do modelo.")
    return achados


def escores(nome: str) -> pd.DataFrame:
    """manchete, p_pos, p_neg, p_neu, escore, classe — uma linha por manchete."""
    d = pd.read_csv(RAIZ / "dados" / f"sentimento_{nome}.csv")
    d = d.drop_duplicates("manchete", keep="last")
    col = _rotulos(nome, [c for c in d.columns if c.startswith(nome + "_")])
    out = pd.DataFrame({"manchete": d["manchete"].astype(str),
                        "p_pos": d[col["pos"]], "p_neg": d[col["neg"]], "p_neu": d[col["neu"]]})
    out["escore"] = out["p_pos"] - out["p_neg"]
    trio = out[["p_pos", "p_neg", "p_neu"]].to_numpy()
    out["classe"] = np.array(["positivo", "negativo", "neutro"])[trio.argmax(axis=1)]
    return out


def aplicar(noticias: pd.DataFrame, nome: str) -> pd.DataFrame:
    """Troca o score_polaridade das notícias pelo escore do modelo.

    A ligação é pela manchete limpa (sem o " - Nome do Jornal"). Notícias sem
    escore (não deveria haver) saem da análise e o número é informado.
    """
    if nome == "lexico":
        return noticias
    e = escores(nome).set_index("manchete")["escore"]
    df = noticias.copy()
    chave = [tirar_fonte(t, f) for t, f in zip(df["titulo"], df["fonte"])]
    df["score_polaridade"] = pd.Series(chave, index=df.index).map(e)
    falta = int(df["score_polaridade"].isna().sum())
    print(f"[medida = {nome}] {len(df) - falta} de {len(df)} notícias com escore"
          + (f" ({falta} sem escore ficam fora)" if falta else ""))
    return df.dropna(subset=["score_polaridade"])
