# -*- coding: utf-8 -*-
"""
resultados.py
-------------
Lê os resultados OFICIAIS do estudo para o dashboard.

De onde vêm os números
    Todos saem de verificacao/referencia/, a referência congelada em
    02/10/2026: as saídas das 32 etapas da análise, exatamente como o
    verificador as confere. É a mesma fonte do relatório da MOSTRATEC.
    Nenhum número do dashboard é digitado à mão: se a referência mudar,
    a tela muda junto.

    Cada função diz, no comentário, de qual etapa (E01 a E31) o número vem.
    O mapa etapa -> script está em verificacao/verificar_tudo.py.

Este módulo não depende do Streamlit: dá para testar no terminal com
    python -m modulos.resultados
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REF = RAIZ / "verificacao" / "referencia"
DATA_REF = "2026-10-02"          # data do congelamento, no nome dos arquivos

ATIVOS = ["ABEV3", "BBDC4", "ITUB4", "MGLU3", "PETR4", "SUZB3", "VALE3", "WEGE3"]
EMPRESAS = {
    "ABEV3": "Ambev", "BBDC4": "Bradesco", "ITUB4": "Itaú Unibanco",
    "MGLU3": "Magazine Luiza", "PETR4": "Petrobras", "SUZB3": "Suzano",
    "VALE3": "Vale", "WEGE3": "WEG",
}
ALFA = 0.05


def _arq(etapa: str, nome: str) -> Path:
    return REF / etapa / nome.replace("{data}", DATA_REF)


def _txt(etapa: str, nome: str = "_tela.txt") -> str:
    return _arq(etapa, nome).read_text(encoding="utf-8")


def _json(etapa: str, nome: str) -> dict:
    return json.loads(_arq(etapa, nome).read_text(encoding="utf-8"))


def _num(padrao: str, texto: str, grupo: int = 1, tipo=float):
    m = re.search(padrao, texto)
    if not m:
        raise ValueError(f"não achei '{padrao}' na referência")
    return tipo(m.group(grupo).replace(",", "."))


def _br3(x: float) -> str:
    return f"{x:+.3f}".replace(".", ",").replace("-", "−")


def referencia_disponivel() -> bool:
    return (REF / "E03").is_dir()


# ─────────────────────────────────────────────────────────
# Números de capa
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def numeros_gerais() -> dict:
    tab = por_ativo()
    e17 = _txt("E17", "fase_causal_A1_{data}.txt")
    e12 = _txt("E12", "teste1_sem_manchetes_de_preco_{data}.txt")
    reg = registro_de_testes()
    ver = ultima_verificacao()
    return {
        # E12: "TODAS (referência): 18463 notícias"
        "noticias": int(_num(r"TODAS \(referência\): (\d+) notícias", e12)),
        "ativos": len(tab),
        "pregoes_com_noticia": int(tab["n"].sum()),
        # E17: "Notícias com horário no principal: 4998"
        "com_horario": int(_num(r"horário no principal: (\d+)", e17)),
        "horario_wordpress": int(_num(r"'wordpress_filtrado': (\d+)", e17)),
        "horario_google": int(_num(r"'google': (\d+)", e17)),
        "testes_registrados": len(reg),
        "verificacao_ok": ver["ok"],
        "verificacao_total": ver["total"],
        "d0_rejeita": int((tab["p_d0"] < ALFA).sum()),
        "d1_rejeita": int((tab["p_d1"] < ALFA).sum()),
        "dm1_rejeita": int((tab["p_dm1"] < ALFA).sum()),
    }


# ─────────────────────────────────────────────────────────
# Validação do método (antes dos dados reais)
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def validacao_sintetica() -> dict:
    """E01: 1.000 séries simuladas de 400 dias, cenários A (efeito) e B (sem efeito)."""
    t = _txt("E01")
    a, b = t.split("CENÁRIO B")
    return {
        "n_sim": int(_num(r"(\d+) simulações de (\d+) dias", t)),
        "dias": int(_num(r"(\d+) simulações de (\d+) dias", t, 2)),
        "r_medido": _num(r"Correlação MEDIDA\s*: r = ([+-]?[\d.]+)", a),
        "r_teorico": _num(r"Correlação TEÓRICA\s*: r = ([+-]?[\d.]+)", a),
        "poder": _num(r"H0 rejeitada em\s*: ([\d.]+)%", a),
        "r_medio_b": _num(r"Correlação média\s*: r = ([+-]?[\d.]+)", b),
        "falso_positivo": _num(r"H0 rejeitada em\s*: ([\d.]+)%", b),
        "limite_fp": _num(r"limite: ([\d.]+)%", b),
    }


@lru_cache(maxsize=None)
def curva_de_poder() -> pd.DataFrame:
    """E02, curva 1: poder medido (300 simulações por ponto) x poder teórico, n = 400 dias."""
    t = _txt("E02").split("CURVA 2")[0]
    linhas = re.findall(r"^\s*([\d.]+) \|\s*([\d.]+) \|\s*([\d.]+)% \|\s*([\d.]+)%", t, re.M)
    return pd.DataFrame([dict(b=float(b), r=float(r), medido=float(m), teorico=float(te))
                         for b, r, m, te in linhas])


# ─────────────────────────────────────────────────────────
# Medida de sentimento
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def validacao_medida() -> dict:
    """E22 e E23: kappa contra os rótulos de referência preliminares (300 manchetes)."""
    e23 = _json("E23", "fase_F_validacao_modelos_preliminar_claude_{data}.json")
    e22 = _json("E22", "validacao_lexico_preliminar_claude_{data}.json")
    cand = e23["candidatos"]
    ic = e23["ic_kappa_pop"]

    def pega(chave):
        c = cand[chave]
        return {"kappa": c["kappa_pop"], "ic": ic[chave], "acuracia": c["acc_pop"],
                "spearman": c["spearman"], "matriz": c["matriz"]}

    chave_l = next(k for k in cand if k.startswith("L"))
    chave_f = next(k for k in cand if k.startswith("F"))
    kab = None
    for k, v in e22.items():
        if "anotador" in k.lower() and isinstance(v, (int, float)):
            kab = v
    return {"n": e23["n"], "lexico": pega(chave_l), "finbert": pega(chave_f),
            "diferenca_ic": e23["ic_diferenca"][chave_f], "kappa_anotadores": kab,
            "adota_finbert": e23["adota_finbert"]}


@lru_cache(maxsize=None)
def lexico_vs_finbert() -> dict:
    """E25: correlação entre os escores manchete a manchete e força média dos escores."""
    t = _txt("E25", "fase_F_robustez_comparacao_{data}.txt")
    return {
        "correlacao": _num(r"manchete a manchete: \+?([\d.]+)", t),
        "n": int(_num(r"manchete a manchete: \+?[\d.]+ \(n = (\d+)\)", t)),
        "relato_lex": _num(r"relato\s*: léxico ([\d.]+)", t),
        "relato_fin": _num(r"relato\s*: léxico [\d.]+, FinBERT ([\d.]+)", t),
        "info_lex": _num(r"informativas: léxico ([\d.]+)", t),
        "info_fin": _num(r"informativas: léxico [\d.]+, FinBERT ([\d.]+)", t),
    }


# ─────────────────────────────────────────────────────────
# Pergunta 1 — existe associação?
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def por_ativo() -> pd.DataFrame:
    """E03 (r e p clássicos em D−1, D+0, D+1) + E04 (p de permutação em D+0)."""
    d = pd.read_csv(_arq("E03", "congelado_{data}.csv"))
    d = d[d["motivo"].isna()].copy()
    d["ativo"] = d["ativo"].str.replace(".SA", "", regex=False)
    perm = {}
    for linha in _txt("E04").splitlines():
        m = re.match(r"\s*(\w+)\.SA\s+(\d+)\s+([-\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)%", linha)
        if m:
            perm[m.group(1)] = float(m.group(5))
    d["p_perm_d0"] = d["ativo"].map(perm)
    d["empresa"] = d["ativo"].map(EMPRESAS)
    d["n"] = d["n"].astype(int)
    return d[["ativo", "empresa", "n", "r_dm1", "p_dm1", "r_d0", "p_d0", "p_perm_d0",
              "r_d1", "p_d1"]].reset_index(drop=True)


COMPLEMENTO_D4 = RAIZ / "resultados" / "curva_defasagem_complemento_D+4.csv"


@lru_cache(maxsize=None)
def curva_defasagem() -> pd.DataFrame:
    """E06: correlação do sentimento do dia D com o retorno de D−5 a D+5.

    O D+4 não estava na lista do script 14. Ele foi calculado depois, com o mesmo
    método e os mesmos dados, por scripts/42_defasagem_d4.py (que confere as outras
    90 correlações contra a E06 antes de gravar). Vem marcado como complemento.
    """
    d = pd.read_csv(_arq("E06", "curva_defasagem_{data}.csv"))
    d["complemento"] = False
    if COMPLEMENTO_D4.exists():
        c = pd.read_csv(COMPLEMENTO_D4)
        c["complemento"] = True
        d = pd.concat([d, c], ignore_index=True).sort_values(["ativo", "lag"], kind="stable")
    d["sig"] = d["sig"].astype(str) == "True"
    return d.reset_index(drop=True)


@lru_cache(maxsize=None)
def williams() -> pd.DataFrame:
    """E05: D−1 contra D+0 com o teste de Williams (correlações dependentes)."""
    return pd.read_csv(_arq("E05", "defasagem_negativa_{data}.csv"))


@lru_cache(maxsize=None)
def agrupado_d0() -> dict:
    """E06: os 8 ativos agrupados (todos os pares ativo-dia empilhados), no mesmo pregão.
    É o pico da curva de defasagem (Figura 14 do relatório)."""
    d = curva_defasagem()
    x = d[(d["ativo"] == "AGRUPADO") & (d["lag"] == 0) & ~d["complemento"]].iloc[0]
    return {"r": float(x["r"]), "p": float(x["p"]), "n": int(x["n"])}


# ─────────────────────────────────────────────────────────
# Pergunta 2 — a associação é real? (controles e réplicas)
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def placebo() -> dict:
    """E13: notícias de A contra o retorno anormal de B, para todos os pares."""
    t = _txt("E13", "teste2_placebo_entre_empresas_{data}.txt")
    linhas = [l for l in t.splitlines() if re.match(r"\s+[A-Z]{4}\d\s+[+-]", l)]
    cab = re.search(r"^\s+(ABEV3.*WEGE3)\s*$", t, re.M).group(1).split()
    mat = pd.DataFrame([[float(v) for v in l.split()[1:]] for l in linhas],
                       index=[l.split()[0] for l in linhas], columns=cab)
    return {
        "matriz": mat,
        "propria": _num(r"Média das 8 próprias.*: ([+-][\d.]+)", t),
        "cruzada": _num(r"Média das 54 cruzadas.*: ([+-][\d.]+)", t),
        "p_cruzada": _num(r"H0-2a p = ([\d.]+)", t),
        "diferenca": _num(r"Própria - cruzada\s*: ([+-][\d.]+)", t),
        "p_diferenca": _num(r"H0-2b p = ([\d.]+)", t),
        "bancos": _num(r"Pares entre bancos.*: ([+-][\d.]+)", t),
    }


@lru_cache(maxsize=None)
def controles() -> list:
    """Os testes que tentam derrubar a associação do mesmo dia, todos confirmatórios."""
    reg = registro_de_testes()
    e16 = _json("E16", "fase_causal_{data}.json")
    e28 = _json("E28", "fase_H_smallcaps_lexico_{data}.json")
    ab = reg[(reg["etapa"] == "E14") & reg["teste"].str.startswith("AGRUPADO D+0")].iloc[0]
    sp = reg[(reg["etapa"] == "E12") & (reg["tipo"] == "confirmatório")].iloc[0]
    pl = placebo()
    p8 = e16["principal"]["P8"]
    h1 = e28["resultados"]["H1"]
    return [
        dict(chave="anormal", teste="Retorno anormal (descontado o Ibovespa)",
             pergunta="A associação é só o mercado inteiro subindo e descendo junto?",
             r=ab["r"], p=ab["p"], p_holm=None, n=int(ab["n"]), mde=ab["menor_r_detectavel"],
             etapa="E14", leitura="sobrevive ao desconto do mercado"),
        dict(chave="placebo", teste="Placebo: notícia de uma empresa × retorno de outra",
             pergunta="É a notícia da própria empresa, ou um humor geral do mercado?",
             r=pl["diferenca"], p=pl["p_diferenca"], p_holm=None, n=None, mde=None,
             etapa="E13", leitura=f"própria {_br3(pl['propria'])} × outras {_br3(pl['cruzada'])}"),
        dict(chave="sem_preco", teste="Sem as manchetes que só relatam o preço",
             pergunta="A associação vem só de manchetes do tipo \"ação dispara 5%\"?",
             r=sp["r"], p=sp["p"], p_holm=None, n=int(sp["n"]), mde=sp["menor_r_detectavel"],
             etapa="E12", leitura="diminui, mas continua"),
        dict(chave="replica", teste="Réplica em outro período (out/2021 a dez/2023)",
             pergunta="O resultado se repete com dados que não foram usados antes?",
             r=p8["r"], p=p8["p"], p_holm=e16["holm"]["P8"], n=p8["n"], mde=p8["mde"],
             etapa="E16", leitura="repete"),
        dict(chave="smallcaps", teste="Réplica em 8 ações menores (small caps)",
             pergunta="E em empresas menores, menos acompanhadas pela imprensa?",
             r=h1["r"], p=h1["p"], p_holm=e28["holm"]["H1"], n=h1["n"], mde=h1["mde"],
             etapa="E28", leitura="repete, mais forte"),
    ]


@lru_cache(maxsize=None)
def smallcaps_ativos() -> list:
    return [a.replace(".SA", "") for a in _json("E28", "fase_H_smallcaps_lexico_{data}.json")["ativos"]]


@lru_cache(maxsize=None)
def granger() -> pd.DataFrame:
    """E15: causalidade de Granger com 5 defasagens, nos dois sentidos."""
    t = _txt("E15", "teste5_granger_{data}.txt").split("--- 1 defasagem")[0]
    linhas = re.findall(r"^\s+(\w+)\.SA\s+([\d.]+)\s+([\d.]+)", t, re.M)
    return pd.DataFrame([dict(ativo=a, sent_para_ret=float(x), ret_para_sent=float(y))
                         for a, x, y in linhas])


@lru_cache(maxsize=None)
def finbert_por_ativo() -> pd.DataFrame:
    """E24: o resultado original refeito com o FinBERT-PT-BR no lugar do léxico."""
    d = pd.read_csv(_arq("E24", "fase_F_R3_resultado_original_{data}.csv"))
    d = d.drop(columns=[c for c in d.columns if c.startswith("Unnamed") or c == ""], errors="ignore")
    d["ativo"] = d["ativo"].str.replace(".SA", "", regex=False)
    return d


# ─────────────────────────────────────────────────────────
# Pergunta 3 — quem vem primeiro?
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def testes_direcao() -> list:
    """E17 (horário exato, análise A1), E27 (barras de 1 minuto) e E16 (diário).

    sentido = "preco_antes" quando o teste pergunta se o preço andou ANTES da
    notícia; "noticia_antes" quando pergunta se a notícia antecipou o preço.
    """
    a1 = _json("E17", "fase_causal_A1_{data}.json")
    e18 = _json("E18", "fase_causal_finbert_{data}.json")
    a1f = _json("E19", "fase_causal_A1_finbert_{data}.json")
    c = _json("E27", "fase_G_janelas_curtas_lexico_{data}.json")
    e16 = _json("E16", "fase_causal_{data}.json")
    holm_a1 = {r["teste"]: r["p_holm"] for _, r in registro_de_testes().iterrows()
               if r["etapa"] == "E17"}

    def t(chave, nome, escala, sentido, d, holm=None, fin=None, etapa=""):
        return dict(chave=chave, nome=nome, escala=escala, sentido=sentido, r=d["r"], p=d["p"],
                    n=d["n"], mde=d["mde"], p_holm=holm,
                    r_finbert=fin["r"] if fin else None, p_finbert=fin["p"] if fin else None,
                    etapa=etapa)

    return [
        t("A1_P3", "Pregão que acabou de fechar → notícia da noite", "fechamento e abertura",
          "preco_antes", a1["A1_P3"], holm_a1.get("A1_P3"), a1f["A1_P3"], "E17"),
        t("A1_P5", "Hora anterior → notícia publicada no pregão", "barras de 60 minutos",
          "preco_antes", a1["A1_P5"], holm_a1.get("A1_P5"), a1f["A1_P5"], "E17"),
        t("C2", "Minutos −5 a −1 → notícia", "barras de 1 minuto",
          "preco_antes", c["C2"], c["holm"]["C2"], c.get("CS3_C2_finbert"), "E27"),
        t("A1_P2", "Notícia da noite → abertura do dia seguinte", "fechamento e abertura",
          "noticia_antes", a1["A1_P2"], holm_a1.get("A1_P2"), a1f["A1_P2"], "E17"),
        t("A1_P4", "Notícia publicada no pregão → hora seguinte", "barras de 60 minutos",
          "noticia_antes", a1["A1_P4"], holm_a1.get("A1_P4"), a1f["A1_P4"], "E17"),
        t("C1", "Notícia → minutos +1 a +5", "barras de 1 minuto",
          "noticia_antes", c["C1"], c["holm"]["C1"], c.get("CS3_C1_finbert"), "E27"),
        t("P1", "Notícias do dia → abertura do dia seguinte (todas, diário)", "diário",
          "noticia_antes", e16["principal"]["P1"], e16["holm"]["P1"], e18["principal"]["P1"], "E16"),
    ]


@lru_cache(maxsize=None)
def perfil_horario() -> pd.DataFrame:
    """E17: retorno anormal médio hora a hora em volta das notícias publicadas no pregão
    (terços extremos de sentimento)."""
    return pd.read_csv(_arq("E17", "fase_causal_A1_perfil_horario_{data}.csv"))


@lru_cache(maxsize=None)
def perfil_minuto() -> pd.DataFrame:
    """E27: retorno anormal acumulado minuto a minuto, com intervalo de 95%."""
    return pd.read_csv(_arq("E27", "fase_G_perfil_minuto_bandas_lexico_{data}.csv"))


@lru_cache(maxsize=None)
def exploratorio_abertura() -> dict:
    """E20 (exploratório, decidido depois de ver os resultados)."""
    reg = registro_de_testes()
    x = reg[reg["teste"] == "E3_da_abertura_ate_a_noticia"].iloc[0]
    y = reg[reg["teste"] == "E3_da_noticia_ate_o_fechamento"].iloc[0]
    return {"antes": dict(r=x["r"], p=x["p"], n=int(x["n"])),
            "depois": dict(r=y["r"], p=y["p"], n=int(y["n"]))}


# ─────────────────────────────────────────────────────────
# Transparência
# ─────────────────────────────────────────────────────────

@lru_cache(maxsize=None)
def registro_de_testes() -> pd.DataFrame:
    """verificacao/registro_de_testes.csv: TODOS os testes feitos, inclusive os nulos."""
    d = pd.read_csv(RAIZ / "verificacao" / "registro_de_testes.csv", sep=";", encoding="utf-8-sig")
    for c in ("r", "p", "p_holm", "menor_r_detectavel"):
        d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", "."), errors="coerce")
    return d


@lru_cache(maxsize=None)
def ultima_verificacao() -> dict:
    """O relatório da execução COMPLETA (32 etapas) mais recente gravado em verificacao/.

    Execuções parciais (--etapas) também gravam relatorio_verificacao.txt; elas
    são ignoradas aqui, para o painel não mostrar "13 de 13" como se fosse tudo.
    """
    arqs = sorted((RAIZ / "verificacao").glob("relatorio_verificacao*.txt"),
                  key=lambda p: p.stat().st_mtime, reverse=True)
    for a in arqs:
        t = a.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"RESULTADO: (\d+) de (\d+) saídas conferem", t)
        etapas = re.search(r"RODANDO (\d+) etapas", t)
        if m and etapas and int(etapas.group(1)) == 32:
            ini = re.search(r"Início: ([\d/]+ [\d:]+)\s+Máquina: (.+)", t)
            py = re.search(r"^\s*(Python [^\n]+)", t, re.M)
            return {"ok": int(m.group(1)), "total": int(m.group(2)), "arquivo": a.name,
                    "quando": ini.group(1) if ini else "", "maquina": ini.group(2).strip() if ini else "",
                    "python": py.group(1).strip() if py else ""}
    return {"ok": 0, "total": 0, "arquivo": "", "quando": "", "maquina": "", "python": ""}


def pre_registros() -> pd.DataFrame:
    """Os documentos de pré-registro em docs/, com a data que está no nome do arquivo."""
    linhas = []
    for p in sorted((RAIZ / "docs").glob("pre-registro_*.md")):
        m = re.match(r"pre-registro_(\d{4})-(\d{2})-(\d{2})_(.+)\.md", p.name)
        if not m:
            continue
        nome = m.group(4).replace("-", " ").replace("_", " ")
        linhas.append(dict(data=f"{m.group(3)}/{m.group(2)}/{m.group(1)}", documento=nome,
                           adendo="ADENDO" in p.name.upper(), arquivo=p))
    return pd.DataFrame(linhas)


def coleta_prospectiva() -> dict:
    """Última linha de dados/prospectivo/log_coleta_diaria.txt (se existir)."""
    arq = RAIZ / "dados" / "prospectivo" / "log_coleta_diaria.txt"
    out = {"existe": arq.exists(), "eventos": None, "meta": 1500, "prazo": "30/06/2027",
           "inicio": "02/10/2026", "ultima": "", "dias": 0}
    if not arq.exists():
        return out
    linhas = arq.read_text(encoding="utf-8", errors="replace").splitlines()
    out["dias"] = sum(1 for l in linhas if "início da coleta" in l)
    for l in reversed(linhas):
        m = re.search(r"eventos confirmatórios: (\d+) de (\d+)", l)
        if m:
            out["eventos"], out["meta"] = int(m.group(1)), int(m.group(2))
            out["ultima"] = l[:16]
            break
    if not out["ultima"] and linhas:
        out["ultima"] = linhas[-1][:16]
    return out


if __name__ == "__main__":
    import pprint
    pprint.pprint(numeros_gerais())
    print(por_ativo())
    pprint.pprint(validacao_sintetica())
    print(curva_de_poder())
    pprint.pprint({k: v for k, v in validacao_medida().items() if k not in ("lexico", "finbert")})
    pprint.pprint(lexico_vs_finbert())
    pprint.pprint({k: v for k, v in placebo().items() if k != "matriz"})
    for c in controles():
        print(c["chave"], round(c["r"], 4), c["p"], c["p_holm"], c["n"])
    for t in testes_direcao():
        print(t["chave"], round(t["r"], 4), round(t["p"], 4), t["p_holm"], t["n"], round(t["mde"], 3))
    print(granger())
    print(finbert_por_ativo())
    pprint.pprint(exploratorio_abertura())
    pprint.pprint(ultima_verificacao())
    print(pre_registros()[["data", "documento"]])
    pprint.pprint(coleta_prospectiva())
    print(agrupado_d0(), smallcaps_ativos())
