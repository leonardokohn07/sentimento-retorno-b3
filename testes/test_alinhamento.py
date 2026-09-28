# -*- coding: utf-8 -*-
"""
test_alinhamento.py
-------------------
Garante que a defasagem é medida em PREGÕES e não em linhas da tabela.

O bug que este teste impede de voltar: a série diária só tem os dias que
têm notícia, então deslocar uma linha ("shift") podia pular pregões inteiros.
Em 28/09/2026, 16,6% dos pares D+1 do estudo estavam errados por causa disso.

Rodar (da pasta InvestAI):
    .\\venv\\Scripts\\python -m pytest testes -q
    ou, sem pytest:
    .\\venv\\Scripts\\python testes\\test_alinhamento.py
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

import numpy as np
import pandas as pd

from modulos.analise.hipotese import montar_serie_diaria, _retorno_defasado


def _cenario():
    """5 pregões seguidos; notícia só na segunda, na quarta e na sexta.

    pregões: 01  02  03  04  05   (dias úteis fictícios)
    retorno: 1%  2%  3%  4%  5%
    notícia: sim  -  sim   -  sim
    """
    dias = pd.to_datetime(["2026-01-05", "2026-01-06", "2026-01-07",
                           "2026-01-08", "2026-01-09"])
    retornos = pd.DataFrame({"AAAA.SA": [0.01, 0.02, 0.03, 0.04, 0.05]}, index=dias)
    noticias = pd.DataFrame({
        "ticker": ["AAAA.SA"] * 3,
        "data_pregao": [dias[0], dias[2], dias[4]],
        "score_polaridade": [0.5, -0.2, 0.9],
    })
    return noticias, retornos


def test_d0_pega_o_proprio_pregao():
    noticias, retornos = _cenario()
    s = montar_serie_diaria(noticias, retornos, "AAAA.SA")
    assert np.allclose(_retorno_defasado(s, 0), [0.01, 0.03, 0.05])


def test_d1_pega_o_pregao_seguinte_mesmo_sem_noticia():
    """O dia seguinte ao 1º pregão é o 2º — que NÃO tem notícia.

    O shift por linha pegaria 0,03 (o próximo dia com notícia). O certo é 0,02.
    """
    noticias, retornos = _cenario()
    s = montar_serie_diaria(noticias, retornos, "AAAA.SA")
    d1 = _retorno_defasado(s, 1).to_numpy()
    assert np.isclose(d1[0], 0.02), f"D+1 do primeiro dia deu {d1[0]}, esperado 0,02"
    assert np.isclose(d1[1], 0.04), f"D+1 do segundo dia deu {d1[1]}, esperado 0,04"
    assert np.isnan(d1[2]), "o último dia não tem pregão seguinte: deve ser NaN"


def test_d_menos_1_pega_o_pregao_anterior():
    noticias, retornos = _cenario()
    s = montar_serie_diaria(noticias, retornos, "AAAA.SA")
    dm1 = _retorno_defasado(s, -1).to_numpy()
    assert np.isnan(dm1[0]), "o primeiro dia não tem pregão anterior"
    assert np.isclose(dm1[1], 0.02)
    assert np.isclose(dm1[2], 0.04)


def test_shift_por_linha_daria_resposta_errada():
    """Registra o tamanho do erro antigo, para não repetir a confusão."""
    noticias, retornos = _cenario()
    s = montar_serie_diaria(noticias, retornos, "AAAA.SA")
    por_linha = s["retorno"].shift(-1).to_numpy()
    por_pregao = _retorno_defasado(s, 1).to_numpy()
    assert np.isclose(por_linha[0], 0.03)      # errado: pulou um pregão
    assert np.isclose(por_pregao[0], 0.02)     # certo


if __name__ == "__main__":
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in testes:
        t()
        print(f"[ok] {t.__name__}")
    print(f"\n{len(testes)} testes passaram.")
