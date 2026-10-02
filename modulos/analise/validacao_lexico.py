# -*- coding: utf-8 -*-
"""
validacao_lexico.py — ferramentas da Fase E (pré-registro de 02/10/2026).

Pergunta: o escore do léxico concorda com o sentimento que uma pessoa
atribuiria à manchete, do ponto de vista do acionista?

O que tem aqui:
    tirar_fonte()       tira o " - Nome do Jornal" do fim do título
    tabela_manchetes()  pares únicos (ativo, manchete) com o escore do léxico
    montar_amostra()    sorteio estratificado: 100 Positivo, 100 Negativo, 100 Neutro
    ler_rotulos()       lê os rótulos de um anotador (.csv id;rotulo ou .xlsx)
    kappa()             kappa de Cohen (aceita pesos, para reponderar)
    metricas()          acurácia, precisão por classe, kappa, matriz, Spearman

Só usa numpy e pandas (nada de biblioteca nova para instalar).
"""
from pathlib import Path
import numpy as np
import pandas as pd

ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA",
          "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
EMPRESA = {"ABEV3.SA": "Ambev", "BBDC4.SA": "Bradesco",
           "ITUB4.SA": "Itaú Unibanco", "MGLU3.SA": "Magazine Luiza",
           "PETR4.SA": "Petrobras", "SUZB3.SA": "Suzano",
           "VALE3.SA": "Vale", "WEGE3.SA": "WEG"}

CLASSES = ["negativo", "neutro", "positivo"]          # ordem fixa das tabelas
DO_LEXICO = {"Negativo": "negativo", "Neutro": "neutro", "Positivo": "positivo"}
CODIGO = {"negativo": -1, "neutro": 0, "positivo": 1}  # para o Spearman

# Pesos de cada classe do léxico na POPULAÇÃO (fixados no pré-registro).
PESOS_POPULACAO = {"neutro": 0.704, "positivo": 0.183, "negativo": 0.113}


# ───────────────────────── montar a amostra ─────────────────────────
def tirar_fonte(titulo: str, fonte: str) -> str:
    """'Vale lucra X - Valor Econômico' -> 'Vale lucra X' (se a fonte bate)."""
    titulo, sufixo = str(titulo), " - " + str(fonte)
    return titulo[: -len(sufixo)].strip() if titulo.endswith(sufixo) else titulo.strip()


def tabela_manchetes(noticias: pd.DataFrame) -> pd.DataFrame:
    """Um registro por par (ativo, manchete), mantendo a 1ª ocorrência.

    A mesma manchete republicada por vários sites vira UM item só.
    """
    n = noticias[noticias["ticker"].isin(ATIVOS)].copy()
    n["manchete"] = [tirar_fonte(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    n = n.drop_duplicates(["ticker", "manchete"], keep="first")
    return n.reset_index(drop=True)


def montar_amostra(noticias: pd.DataFrame, n_por_classe: int = 100,
                   semente: int = 42, semente_ordem: int = 7) -> pd.DataFrame:
    """Sorteio estratificado pela classe do léxico + embaralhamento.

    - sorteio de cada classe: semente 42 (a do pré-registro);
    - embaralhamento da planilha: semente 7. Essa é a semente que gerou a
      planilha usada de verdade (reconstituída em 02/10/2026: o script
      refaz exatamente os mesmos 300 itens, na mesma ordem).
    """
    u = tabela_manchetes(noticias)
    partes = [u[u["classificacao"] == c].sample(n=n_por_classe, random_state=semente)
              for c in ["Positivo", "Negativo", "Neutro"]]
    a = pd.concat(partes).sample(frac=1, random_state=semente_ordem).reset_index(drop=True)
    a.insert(0, "id", [f"M{i:03d}" for i in range(1, len(a) + 1)])
    a["empresa"] = a["ticker"].map(EMPRESA)
    return a[["id", "ticker", "empresa", "manchete", "score_polaridade",
              "classificacao", "url"]]


def escores_da_planilha(planilha: pd.DataFrame, noticias: pd.DataFrame) -> pd.DataFrame:
    """Procura o escore do léxico de cada manchete da planilha de rotulagem.

    A planilha (id;empresa;manchete) é a amostra CONGELADA. Mesmo que o CSV
    de notícias cresça depois, cada manchete continua achando o seu escore.
    """
    tab = tabela_manchetes(noticias)
    ticker_de = {v: k for k, v in EMPRESA.items()}
    p = planilha.copy()
    p["ticker"] = p["empresa"].map(ticker_de)
    m = p.merge(tab[["ticker", "manchete", "score_polaridade", "classificacao"]],
                on=["ticker", "manchete"], how="left")
    faltando = m["classificacao"].isna().sum()
    if faltando or len(m) != len(p):
        raise ValueError(f"{faltando} manchetes da planilha não foram achadas no CSV")
    m["lexico"] = m["classificacao"].map(DO_LEXICO)
    return m


# ───────────────────────── ler rótulos ─────────────────────────
def ler_rotulos(arquivo) -> pd.Series:
    """Devolve uma Series id -> rótulo ('positivo'/'negativo'/'neutro').

    Aceita o CSV dos anotadores automáticos (id;rotulo) ou a planilha .xlsx
    dos humanos (aba 'rotular', coluna ROTULO).
    """
    arquivo = Path(arquivo)
    if arquivo.suffix.lower() == ".xlsx":
        d = pd.read_excel(arquivo, sheet_name="rotular")
        d = d.rename(columns={"ROTULO": "rotulo"})
    else:
        d = pd.read_csv(arquivo, sep=";")
    r = d.set_index("id")["rotulo"].astype(str).str.strip().str.lower()
    r = r.replace({"nan": np.nan, "": np.nan})
    vazios = r.isna().sum()
    invalidos = sorted(set(r.dropna()) - set(CLASSES))
    if vazios or invalidos:
        raise ValueError(f"{arquivo.name}: {vazios} linhas em branco, "
                         f"rótulos inválidos: {invalidos}")
    if r.index.duplicated().any():
        raise ValueError(f"{arquivo.name}: ids repetidos")
    return r


# ───────────────────────── métricas ─────────────────────────
def _contar(linhas, colunas, pesos=None) -> np.ndarray:
    """Conta (ou soma pesos) de cada par (classe da linha, classe da coluna).

    Cada classe vira um número (negativo 0, neutro 1, positivo 2) e o par
    vira 3*linha + coluna, de 0 a 8. O bincount soma tudo de uma vez, o que
    deixa o bootstrap de 10 mil repetições rodar em segundos.
    """
    num = {c: i for i, c in enumerate(CLASSES)}
    a = np.array([num[x] for x in linhas])
    b = np.array([num[x] for x in colunas])
    w = None if pesos is None else np.asarray(pesos, float)
    return np.bincount(3 * a + b, weights=w, minlength=9).reshape(3, 3).astype(float)


def matriz(linhas, colunas, pesos=None) -> pd.DataFrame:
    """Matriz de confusão (linhas = léxico, colunas = anotadores)."""
    return pd.DataFrame(_contar(linhas, colunas, pesos), index=CLASSES, columns=CLASSES)


def kappa(a, b, pesos=None) -> float:
    """Kappa de Cohen: concordância descontando a que viria por acaso.

    kappa = (po - pe) / (1 - pe)
      po = proporção de itens em que os dois concordam
      pe = concordância esperada se cada um rotulasse ao acaso,
           mantendo a proporção de cada classe que cada um usou
    """
    m = _contar(a, b, pesos)
    m = m / m.sum()
    po = np.trace(m)
    pe = float(m.sum(axis=1) @ m.sum(axis=0))
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def spearman(x, y) -> float:
    """Correlação de Spearman = Pearson dos postos (empates com posto médio)."""
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    return float(np.corrcoef(rx, ry)[0, 1])


def spearman_permutacao(x, y, n_perm=10_000, semente=42):
    """p-valor bilateral do Spearman por permutação."""
    rng = np.random.default_rng(semente)
    obs = spearman(x, y)
    rx = pd.Series(x).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    rx = (rx - rx.mean()) / rx.std()
    ry = (ry - ry.mean()) / ry.std()
    cont = 0
    for _ in range(n_perm):
        if abs(np.mean(rx * rng.permutation(ry))) >= abs(obs) - 1e-12:
            cont += 1
    return obs, (cont + 1) / (n_perm + 1)


def metricas(lexico, rotulo, escore) -> dict:
    """Todas as métricas pré-registradas para um conjunto de itens.

    lexico : classe do léxico (minúscula) de cada item
    rotulo : rótulo de referência (consenso dos anotadores)
    escore : escore contínuo do léxico (score_polaridade)
    """
    lexico, rotulo = np.asarray(lexico), np.asarray(rotulo)
    escore = np.asarray(escore, float)
    acerto = lexico == rotulo
    precisao = {c: float(acerto[lexico == c].mean()) for c in CLASSES}
    n_classe = {c: int((lexico == c).sum()) for c in CLASSES}
    # Na população, a acurácia é a média das precisões pesada pela
    # frequência real de cada classe do léxico (a amostra tem 1/3 de cada).
    acc_pop = sum(PESOS_POPULACAO[c] * precisao[c] for c in CLASSES)
    # Peso de cada item para reponderar (complementar, não pré-registrado)
    w = np.array([PESOS_POPULACAO[c] / n_classe[c] for c in lexico])
    return {
        "n": int(len(lexico)),
        "n_por_classe_do_lexico": n_classe,
        "acuracia_amostra": float(acerto.mean()),
        "acuracia_populacao": float(acc_pop),
        "precisao_por_classe": precisao,
        "kappa": kappa(lexico, rotulo),
        "matriz": matriz(lexico, rotulo).astype(int),
        "spearman": spearman(escore, [CODIGO[r] for r in rotulo]),
        # complementares
        "kappa_populacao": kappa(lexico, rotulo, w),
        "matriz_populacao": matriz(lexico, rotulo, w),
    }


def bootstrap(lexico, rotulo, n_boot=10_000, semente=42) -> dict:
    """IC 95% por bootstrap ESTRATIFICADO (reamostra dentro de cada classe
    do léxico, como foi o sorteio). Os rótulos ficam fixos."""
    rng = np.random.default_rng(semente)
    lexico, rotulo = np.asarray(lexico), np.asarray(rotulo)
    grupos = [np.flatnonzero(lexico == c) for c in CLASSES]
    acc, accp, kap = [], [], []
    prec = {c: [] for c in CLASSES}
    for _ in range(n_boot):
        idx = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in grupos])
        l, r = lexico[idx], rotulo[idx]
        ok = l == r
        p = {c: ok[l == c].mean() for c in CLASSES}
        acc.append(ok.mean())
        accp.append(sum(PESOS_POPULACAO[c] * p[c] for c in CLASSES))
        kap.append(kappa(l, r))
        for c in CLASSES:
            prec[c].append(p[c])
    ic = lambda v: [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]
    return {"acuracia_amostra": ic(acc), "acuracia_populacao": ic(accp),
            "kappa": ic(kap), "precisao_por_classe": {c: ic(prec[c]) for c in CLASSES}}


def leitura_kappa(k: float) -> str:
    """Faixas de Landis e Koch (1977), como no pré-registro."""
    if k < 0.21:
        return "fraca"
    if k <= 0.40:
        return "razoável"
    if k <= 0.60:
        return "moderada"
    if k <= 0.80:
        return "substancial"
    return "quase perfeita"
