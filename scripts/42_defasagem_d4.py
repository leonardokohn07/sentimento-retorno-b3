# -*- coding: utf-8 -*-
"""
42_defasagem_d4.py
------------------
COMPLEMENTO DA CURVA DE DEFASAGEM: o ponto D+4 que faltava.

Por que este script existe
    A curva de defasagem (scripts/14_curva_de_defasagem.py, etapa E06 do
    verificador) foi calculada de D−5 a D+5, mas a lista de defasagens do
    script pulou o D+4: ela veio da lista de defasagens pré-calculadas do
    estudo original (LAGS_PRE_CALCULADOS em modulos/analise/hipotese.py, que
    não tem o 4). No gráfico, o D+4 aparecia como "não calculado".

    Este script calcula SÓ o D+4, com o mesmo método e os mesmos dados.

O que ele NÃO muda
    O script 14 e a referência congelada (verificacao/referencia/E06) ficam
    como estão: o verificador continua conferindo as mesmas 32 etapas e 99
    saídas. O D+4 é um COMPLEMENTO, calculado em outubro de 2026, depois dos
    resultados, e fora do pré-registro de 28/09/2026. Por isso é descritivo:
    não entra em nenhuma conclusão confirmatória.

Como garantir que o método é o mesmo
    Antes de calcular o D+4, o script recalcula as outras 10 defasagens
    (D−5 a D+3 e D+5) dos 8 ativos e do agrupado, e compara com a referência
    E06. Só grava o resultado se as 90 correlações baterem.

Dados
    O pacote congelado (verificacao/dados_congelados_2026-10-02.zip), lido
    por modulos/congelados.py. Sem ele, usa a pasta dados/ e avisa.

Rodar (da pasta InvestAI):
    .\\venv\\Scripts\\python scripts\\42_defasagem_d4.py

Gera:
    resultados/curva_defasagem_complemento_D+4.csv   (mesmas colunas da E06)
    resultados/curva_defasagem_complemento_D+4.txt
"""
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

from modulos import congelados as C
from modulos.analise.hipotese import MIN_OBSERVACOES, montar_serie_diaria

ALFA = 0.05
TODOS_OS_LAGS = list(range(-5, 6))           # D−5 a D+5, agora com o D+4
REF_E06 = RAIZ / "verificacao" / "referencia" / "E06" / "curva_defasagem_2026-10-02.csv"
PASTA_RES = RAIZ / "resultados"


def serie_com_lags(noticias, retornos, ticker):
    """Mesma conta de scripts/14_curva_de_defasagem.py: a defasagem é contada em
    PREGÕES no calendário completo do ativo, não em linhas da tabela."""
    s = montar_serie_diaria(noticias, retornos, ticker)
    if s.empty:
        return s
    ret = retornos[ticker].copy()
    ret.index = pd.to_datetime(ret.index).normalize()
    calendario, valores = ret.index, ret.to_numpy()
    pos = calendario.searchsorted(pd.to_datetime(s["data"]))
    for k in TODOS_OS_LAGS:
        alvo = pos + k
        col = np.full(len(s), np.nan)
        dentro = (alvo >= 0) & (alvo < len(valores))
        col[dentro] = valores[alvo[dentro]]
        s[f"lag{k}"] = col
    return s


def correlacao(d, k, ativo):
    d = d.dropna(subset=["sentimento", f"lag{k}"])
    r, p = stats.pearsonr(d["sentimento"], d[f"lag{k}"])
    return dict(ativo=ativo, lag=k, n=len(d), r=round(r, 4), p=round(p, 4), sig=bool(p < ALFA))


def main():
    if not C.fonte():
        print("[ERRO] Sem dados: falta o pacote congelado e a pasta dados/.")
        return 1
    print(f"Dados: {C.descricao_fonte()}")
    noticias, retornos = C.noticias_todas(), C.retornos()

    series, linhas = [], []
    for t in sorted(retornos.columns):              # mesma ordem e mesmo filtro do script 14
        s = serie_com_lags(noticias, retornos, t)
        if s.empty or len(s) < MIN_OBSERVACOES:
            continue
        series.append(s)
        linhas += [correlacao(s, k, t.replace(".SA", "")) for k in TODOS_OS_LAGS]
    todos = pd.concat(series, ignore_index=True)    # agrupado: todos os pares ativo-dia juntos
    linhas += [correlacao(todos, k, "AGRUPADO") for k in TODOS_OS_LAGS]
    tab = pd.DataFrame(linhas)

    # ── conferência: as 10 defasagens que já existiam têm de bater com a E06 ──
    ref = pd.read_csv(REF_E06)
    junto = ref.merge(tab, on=["ativo", "lag"], suffixes=("_ref", "_agora"))
    iguais = ((junto["n_ref"] == junto["n_agora"])
              & np.isclose(junto["r_ref"], junto["r_agora"])
              & np.isclose(junto["p_ref"], junto["p_agora"]))
    print(f"Conferência com a referência E06: {int(iguais.sum())} de {len(ref)} correlações iguais.")
    if not iguais.all() or len(junto) != len(ref):
        print("[PAROU] O método não reproduziu a E06; nada foi gravado.")
        print(junto.loc[~iguais].to_string())
        return 1

    d4 = tab[tab["lag"] == 4].reset_index(drop=True)
    PASTA_RES.mkdir(exist_ok=True)
    d4.to_csv(PASTA_RES / "curva_defasagem_complemento_D+4.csv", index=False)

    L = "=" * 78
    out = [L, "  COMPLEMENTO DA CURVA DE DEFASAGEM — o ponto D+4", L,
           f"  Calculado em {date.today():%d/%m/%Y}, depois dos resultados e fora do pré-registro",
           "  de 28/09/2026: é descritivo. Mesmo método e mesmos dados da etapa E06.",
           f"  Dados: {C.descricao_fonte()}",
           f"  Conferência: as outras {len(ref)} correlações da curva batem com a E06.", L,
           f"  {'ativo':<10}{'n':>6}{'r D+4':>10}{'p':>10}  significativo a 5%?", "  " + "-" * 60]
    for _, l in d4.iterrows():
        out.append(f"  {l['ativo']:<10}{l['n']:>6}{l['r']:>10.4f}{l['p']:>10.4f}  {'sim' if l['sig'] else 'não'}")
    sig = d4[d4["ativo"] != "AGRUPADO"]["sig"].sum()
    out += ["  " + "-" * 60, f"  D+4 significativo em {sig} de {len(d4) - 1} ativos.", L]
    texto = "\n".join(out)
    (PASTA_RES / "curva_defasagem_complemento_D+4.txt").write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
