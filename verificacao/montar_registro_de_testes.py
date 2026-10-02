# -*- coding: utf-8 -*-
"""
montar_registro_de_testes.py — monta verificacao/registro_de_testes.csv
a partir das saídas de referência (verificacao/referencia/), que são as
mesmas que o verificar_tudo.py reproduz.

Uma linha por teste estatístico, INCLUSIVE os nulos, com:
    etapa do verificador, fase, pré-registro, tipo, pergunta, r, p, p de Holm,
    n, decisão e arquivo de origem.

Os números não são digitados: são lidos dos arquivos de resultado. As únicas
linhas escritas à mão são as da calibração (60 rodadas com sentimento
embaralhado), cujos números estão no diário (seção 5) e não fazem parte do
verificador, porque cada rodada leva vários minutos.

Uso: python verificacao/montar_registro_de_testes.py
"""
import csv
import json
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REF = AQUI / "referencia"
SAIDA = AQUI / "registro_de_testes.csv"

PR = "docs/pre-registro_"
META = {   # etapa: (fase, pré-registro, tipo padrão)
    "E03": ("Estudo original", "sem documento datado no repositório (estudo original) [CONFERIR]",
            "confirmatório (estudo original)"),
    "E05": ("Estudo original", PR + "2026-09-28_defasagem-negativa.md", "confirmatório"),
    "E06": ("Estudo original", PR + "2026-09-28_curva-de-defasagem.md", "descritivo pré-registrado (forma da curva)"),
    "E08": ("Auditoria", "—", "diagnóstico"),
    "E09": ("Fim de semana agrupado", PR + "2026-10-02_fim-de-semana-agrupado.md", "confirmatório"),
    "E10": ("Fim de semana agrupado", PR + "2026-10-02_fim-de-semana-agrupado.md", "sensibilidade pré-registrada"),
    "E11": ("Fim de semana agrupado", PR + "2026-10-02_fim-de-semana-agrupado.md", "sensibilidade pré-registrada"),
    "E12": ("Quatro testes de direção", PR + "2026-10-02_quatro-testes-de-direcao.md", "confirmatório"),
    "E13": ("Quatro testes de direção", PR + "2026-10-02_quatro-testes-de-direcao.md", "confirmatório"),
    "E14": ("Quatro testes de direção", PR + "2026-10-02_quatro-testes-de-direcao.md", "confirmatório"),
    "E15": ("Quatro testes de direção", PR + "2026-10-02_quatro-testes-de-direcao.md", "confirmatório"),
    "E16": ("Fase causal", PR + "2026-10-02_fase-causal.md", "confirmatório (família principal, Holm)"),
    "E17": ("Fase causal", PR + "2026-10-02_fase-causal_ADENDO-1.md", "análise adicional declarada (adendo 1)"),
    "E18": ("Fase F (robustez)", PR + "2026-10-02_fase-F_modelo-de-linguagem.md", "robustez com FinBERT"),
    "E19": ("Fase F (robustez)", PR + "2026-10-02_fase-F_modelo-de-linguagem.md", "robustez com FinBERT"),
    "E20": ("Fase causal", "— (decidido depois de ver os resultados)", "exploratório"),
    "E22": ("Fase E", PR + "2026-10-02_validacao-do-lexico.md", "validação da medida (preliminar)"),
    "E23": ("Fase F", PR + "2026-10-02_fase-F_modelo-de-linguagem.md", "validação da medida (preliminar)"),
    "E26": ("Fase G (piloto 30 min)", PR + "2026-10-02_fase-G_minuto.md", "piloto"),
    "E27": ("Fase G (adendo 2, até 5 min)", PR + "2026-10-02_fase-G_minuto_ADENDO-2.md", "piloto exploratório"),
    "E28": ("Fase H (small caps)", PR + "2026-10-02_fase-H_small-caps.md", "confirmatório (Holm)"),
    "E29": ("Fase H (small caps)", PR + "2026-10-02_fase-H_small-caps.md", "secundário (FinBERT)"),
}
NUM = r"[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?"
LINHA = re.compile(rf"^\s*(?P<rot>[^:\n]{{3,90}}?)\s*:\s*r = (?P<r>{NUM})\s+p = (?P<p>{NUM})"
                   rf"(?:\s+n = (?P<n>\d+))?(?:.*?~(?P<mde>{NUM}))?")
ATIVO = re.compile(rf"^\s*(?P<a>[A-Z0-9]{{4,6}}\.SA)\s+n=\s*(?P<n>\d+)\s+r(?:\([^)]*\))?\s*=\s*(?P<r>{NUM})\s+p\s*=\s*(?P<p>{NUM})")

linhas = []


def add(eid, teste, pergunta, r=None, p=None, n=None, holm=None, mde=None, tipo=None, arquivo="", medida="léxico",
        fase=None, pre=None):
    f, pr, t = META.get(eid, ("", "", ""))
    if holm is not None:
        dec = "REJEITA H0" if holm < 0.05 else "não rejeita"
    elif p is None:
        dec = "—"
    elif (tipo or t).startswith(("confirmatório", "sensibilidade")):
        dec = "REJEITA H0" if p < 0.05 else "não rejeita"
    else:
        dec = "p < 0,05 (não confirmatório)" if p < 0.05 else "nulo"
    fmt = lambda v, d=4: "" if v is None else f"{v:.{d}f}".replace(".", ",")
    linhas.append({"etapa": eid, "fase": fase or f, "pre_registro": pre or pr, "tipo": tipo or t,
                   "teste": teste, "pergunta": pergunta, "medida": medida, "r": fmt(r), "p": fmt(p),
                   "p_holm": fmt(holm), "n": "" if n is None else int(n), "menor_r_detectavel": fmt(mde, 3),
                   "decisao": dec, "arquivo": arquivo})


def rotulos(eid):
    """Lê o .txt da etapa e devolve {chave: descrição}, ex.: P1 -> 'notícias do dia D -> ABERTURA de D+1'."""
    mapa = {}
    for arq in (REF / eid).glob("*.txt"):
        for ln in arq.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z][A-Za-z0-9_\-]{1,30})\s+(.+?)\s*:\s*(?:r = |própria)", ln)
            if m and m[1] not in mapa:
                mapa[m[1]] = re.sub(r"\s+", " ", m[2]).strip()
    return mapa


def holm_local(pv):
    """Holm dentro da análise A1 (como no diário, seção 7)."""
    ordem = sorted(pv, key=pv.get)
    m, aj, maior = len(ordem), {}, 0.0
    for i, k in enumerate(ordem):
        maior = max(maior, min(1.0, (m - i) * pv[k]))
        aj[k] = maior
    return aj


def ler(eid, padrao):
    arqs = sorted((REF / eid).glob(padrao))
    return arqs[0] if arqs else None


# ── estudo original, por ativo ──
a = ler("E03", "congelado_*.csv")
for row in csv.DictReader(open(a, encoding="utf-8")):
    for k, nome in (("dm1", "D−1"), ("d0", "D+0"), ("d1", "D+1")):
        if row.get(f"r_{k}"):
            add("E03", f"{row['ativo']} {nome}", f"sentimento do dia × retorno em {nome}",
                float(row[f"r_{k}"]), float(row[f"p_{k}"]), float(row[f"n_{k}"]), arquivo=a.name,
                pre=(META["E05"][1] if k == "dm1" else None))
a = ler("E06", "curva_defasagem_*.csv")
for row in csv.DictReader(open(a, encoding="utf-8")):
    add("E06", f"{row['ativo']} lag {int(row['lag']):+d}", "curva de defasagem por ativo",
        float(row["r"]), float(row["p"]), int(row["n"]), arquivo=a.name)

# ── saídas em texto: qualquer linha "rótulo : r = ... p = ... n = ..." ──
for eid in ("E09", "E10", "E11", "E12", "E13", "E14", "E15", "E20"):
    for arq in sorted((REF / eid).glob("*.txt")):
        if arq.name == "_tela.txt":
            continue
        bloco = ""
        for ln in arq.read_text(encoding="utf-8").splitlines():
            if ln.strip().startswith("---"):
                bloco = ln.strip(" -")[:40]
            m = LINHA.match(ln)
            if m:
                rot = m["rot"].strip()
                tipo = None
                if rot.startswith("AGRUPADO D-1"):
                    tipo = "secundário"
                elif eid == "E12" and "INFORMATIVAS" not in bloco:
                    tipo = "descritivo"
                add(eid, rot, (bloco + " | " if bloco else "") + rot,
                    float(m["r"]), float(m["p"]), m["n"] and int(m["n"]),
                    mde=m["mde"] and float(m["mde"]), arquivo=arq.name, tipo=tipo)
            m = ATIVO.match(ln)
            if m:
                add(eid, f"{m['a']} ({bloco or 'por ativo'})", "por ativo (descritivo)", float(m["r"]),
                    float(m["p"]), int(m["n"]), tipo="descritivo", arquivo=arq.name)
        if eid == "E13":
            for m in re.finditer(rf"(H0-2[ab]) p = ({NUM})", arq.read_text(encoding="utf-8")):
                add(eid, m[1], "placebo: cruzadas = 0 (2a); própria − cruzada (2b)", p=float(m[2]), arquivo=arq.name)


# ── fase causal (JSON) ──
def bloco_json(eid, arq, d, holm=None, tipo_fora=None, medida="léxico"):
    rot = rotulos(eid)
    for k, v in d.items():
        if isinstance(v, dict) and "r" in v:
            hk = (holm or {}).get(k)
            add(eid, k, rot.get(k, k), v["r"], v.get("p"), v.get("n"), hk, v.get("mde"),
                tipo=None if hk is not None else tipo_fora, arquivo=arq.name, medida=medida)


for eid, medida in (("E16", "léxico"), ("E18", "FinBERT")):
    arq = ler(eid, "fase_causal_*.json")
    d = json.load(open(arq, encoding="utf-8"))
    bloco_json(eid, arq, d["principal"], d.get("holm"), medida=medida)
    bloco_json(eid, arq, d["secundarias"], tipo_fora="secundário", medida=medida)
for eid, medida in (("E17", "léxico"), ("E19", "FinBERT")):
    arq = ler(eid, "fase_causal_A1*.json")
    d = json.load(open(arq, encoding="utf-8"))
    fam = {k: d[k]["p"] for k in ("A1_P2", "A1_P3", "A1_P4", "A1_P5") if k in d}
    bloco_json(eid, arq, {k: v for k, v in d.items() if isinstance(v, dict)}, medida=medida,
               holm=holm_local(fam) if eid == "E17" else None,
               tipo_fora=None if eid == "E17" else "robustez com FinBERT")

# ── Fases E e F (validação da medida) ──
arq = ler("E22", "*.json")
d = json.load(open(arq, encoding="utf-8"))
add("E22", "kappa anotador A × B", "concordância entre os dois anotadores", r=d["kappa_anotadores"], n=d["n"],
    arquivo=arq.name, medida="—")
pr_ = d["principal"]
add("E22", "kappa léxico × referência (amostra)", "léxico concorda com os rótulos?", r=pr_["kappa"],
    n=pr_["n"], arquivo=arq.name)
add("E22", "kappa léxico × referência (população)", "idem, reponderado para a população",
    r=pr_["kappa_populacao"], n=pr_["n"], arquivo=arq.name)
add("E22", "Spearman escore × rótulo", "o escore cresce com o rótulo?", r=pr_["spearman"], p=pr_["spearman_p"],
    n=pr_["n"], arquivo=arq.name)
arq = ler("E23", "*.json")
d = json.load(open(arq, encoding="utf-8"))
for nome, v in d["candidatos"].items():
    add("E23", f"kappa população — {nome.split(None, 1)[-1]}", "medida × rótulos de referência",
        r=v["kappa_pop"], n=d["n"], arquivo=arq.name, medida=nome.split(None, 1)[-1])
kl = d["candidatos"]["L  léxico"]["kappa_pop"]
for nome, (lo, hi) in d["ic_diferenca"].items():
    dif = d["candidatos"][nome]["kappa_pop"] - kl
    add("E23", f"diferença de kappa: {nome.split(None, 1)[-1]} − léxico",
        f"IC 95% [{lo:+.3f}; {hi:+.3f}]; troca só se o IC ficar todo acima de 0 -> "
        + ("TROCA" if lo > 0 else "mantém o léxico"),
        r=dif, n=d["n"], arquivo=arq.name, tipo="regra de decisão pré-registrada", medida=nome.split(None, 1)[-1])

# ── Fase G ──
for eid, padrao, fam in (("E26", "fase_G_piloto_*.json", ("M1", "M2")),
                         ("E27", "fase_G_janelas_curtas_*.json", ("C1", "C2", "C3", "C4"))):
    arq = ler(eid, padrao)
    d = json.load(open(arq, encoding="utf-8"))
    holm = d.get("holm", {})
    rot = rotulos(eid)
    for k, v in d.items():
        if isinstance(v, dict) and "r" in v:
            add(eid, k, rot.get(k, k), v["r"], v.get("p"), v.get("n"), holm.get(k) if k in fam else None, v.get("mde"),
                tipo=None if k in fam else "secundário", arquivo=arq.name,
                medida="FinBERT" if ("GS3" in k or "CS3" in k) else "léxico")

# ── Fase H ──
for eid, medida in (("E28", "léxico"), ("E29", "FinBERT")):
    arq = ler(eid, "fase_H_*.json")
    d = json.load(open(arq, encoding="utf-8"))
    rot = rotulos(eid)
    for k, v in d["resultados"].items():
        add(eid, k, rot.get(k, k), v["r"], v.get("p"), v.get("n"), d["holm"].get(k) if eid == "E28" else None, v.get("mde"),
            arquivo=arq.name, medida=medida)

# ── calibração (números do diário, seção 5; fora do verificador) ──
for t, fp in (("P1", 2), ("P2", 8), ("P3", 2), ("P4", 0), ("P5", 2), ("P6", 2), ("P7", 5), ("P8", 3), ("P9", 7)):
    add("—", f"calibração {t}", f"falsos positivos em 60 rodadas com sentimento embaralhado: {fp}% (nominal 5%)",
        fase="Fase causal", pre=META["E16"][1], tipo="calibração", arquivo="docs/diario_causalidade.md (seção 5)")

campos = list(linhas[0].keys())
with open(SAIDA, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=campos, delimiter=";")
    w.writeheader()
    w.writerows(linhas)
tipos = {}
for ln in linhas:
    tipos[ln["tipo"]] = tipos.get(ln["tipo"], 0) + 1
print(f"{len(linhas)} linhas em {SAIDA.name}")
for t, n in sorted(tipos.items(), key=lambda x: -x[1]):
    print(f"  {n:4d}  {t}")
