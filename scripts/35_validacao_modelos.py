# -*- coding: utf-8 -*-
"""
35_validacao_modelos.py — léxico x modelos de linguagem na amostra da Fase E (Fase F).

Pré-registro: docs/pre-registro_2026-10-02_fase-F_modelo-de-linguagem.md

Candidatos: L (léxico), F (FinBERT-PT-BR), D (distilbert do código),
            H1 (0,5 L + 0,5 D) e H2 (0,5 L + 0,5 F), limiar ±0,15 nos híbridos.
Referência: consenso dos dois anotadores (itens em que concordam).
Métrica principal: kappa REPONDERADO para a população (a amostra foi
estratificada pela classe do léxico; cada item pesa peso_da_classe / n_da_classe).
Regra: F substitui L se o kappa reponderado for maior e o IC 95% da diferença
(bootstrap pareado e estratificado, 10.000 reamostragens, semente 42) ficar
inteiro acima de zero.

Uso:
    python scripts/35_validacao_modelos.py            # anotadores automáticos
    python scripts/35_validacao_modelos.py --humanos  # Leonardo e Maurício
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd

from modulos.analise.validacao_lexico import (CLASSES, CODIGO, PESOS_POPULACAO,
                                              escores_da_planilha, kappa, ler_rotulos,
                                              matriz, spearman, leitura_kappa)
from modulos.analise import modelos

PASTA = RAIZ / "dados" / "validacao_lexico"
CLAUDE = PASTA / "claude_NAO_ABRIR_antes_de_rotular"
ap = argparse.ArgumentParser()
ap.add_argument("--humanos", action="store_true")
ap.add_argument("--n-boot", type=int, default=10_000)
args = ap.parse_args()

# ───────────── amostra, rótulos e escores ─────────────
planilha = pd.read_csv(PASTA / "para_rotular.csv", sep=";")
base = escores_da_planilha(planilha, pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv"))
base = base.set_index("id")
if args.humanos:
    nome_ref = "humanos"
    r1 = ler_rotulos(PASTA / "rotulagem_sentimento_Leonardo.xlsx")
    r2 = ler_rotulos(PASTA / "rotulagem_sentimento_Mauricio.xlsx")
else:
    nome_ref = "preliminar_claude"
    r1 = ler_rotulos(CLAUDE / "rotulos_anotador_A.csv")
    r2 = ler_rotulos(CLAUDE / "rotulos_anotador_B.csv")
base["r1"], base["r2"] = r1, r2
cons = base[base["r1"] == base["r2"]].copy()
cons["ref"] = cons["r1"]

for nome in ("finbert", "distil"):
    e = modelos.escores(nome).set_index("manchete")
    cons[f"esc_{nome}"] = cons["manchete"].map(e["escore"])
    cons[f"cls_{nome}"] = cons["manchete"].map(e["classe"])
    falta = int(cons[f"esc_{nome}"].isna().sum())
    if falta:
        raise SystemExit(f"{nome}: {falta} manchetes da amostra sem escore. Rode o script 30.")


def classe_limiar(s):
    return np.where(s > 0.15, "positivo", np.where(s < -0.15, "negativo", "neutro"))


cand = {
    "L  léxico": (cons["lexico"].to_numpy(), cons["score_polaridade"].to_numpy()),
    "F  FinBERT-PT-BR": (cons["cls_finbert"].to_numpy(), cons["esc_finbert"].to_numpy()),
    "D  distilbert (do código)": (cons["cls_distil"].to_numpy(), cons["esc_distil"].to_numpy()),
}
h1 = 0.5 * cons["score_polaridade"].to_numpy() + 0.5 * cons["esc_distil"].to_numpy()
h2 = 0.5 * cons["score_polaridade"].to_numpy() + 0.5 * cons["esc_finbert"].to_numpy()
cand["H1 0,5 léxico + 0,5 D"] = (classe_limiar(h1), h1)
cand["H2 0,5 léxico + 0,5 F"] = (classe_limiar(h2), h2)

estrato = cons["lexico"].to_numpy()          # o sorteio foi estratificado por isto
ref = cons["ref"].to_numpy()
n_estr = {c: int((estrato == c).sum()) for c in CLASSES}
peso = np.array([PESOS_POPULACAO[c] / n_estr[c] for c in estrato])


def medidas(pred, esc, idx=None):
    i = np.arange(len(ref)) if idx is None else idx
    w = peso[i] / peso[i].sum()
    mp = matriz(pred[i], ref[i], w)                # linhas = candidato, colunas = referência
    acc = float(np.trace(mp.to_numpy()))
    prec = {c: float(mp.loc[c, c] / mp.loc[c].sum()) if mp.loc[c].sum() > 0 else float("nan") for c in CLASSES}
    rec = {c: float(mp.loc[c, c] / mp[c].sum()) if mp[c].sum() > 0 else float("nan") for c in CLASSES}
    return {"kappa_pop": kappa(pred[i], ref[i], w), "acc_pop": acc, "kappa_amostra": kappa(pred[i], ref[i]),
            "acc_amostra": float((pred[i] == ref[i]).mean()), "precisao": prec, "recall": rec,
            "spearman": spearman(esc[i], [CODIGO[x] for x in ref[i]]),
            "matriz": matriz(pred[i], ref[i]).astype(int)}


res = {k: medidas(*v) for k, v in cand.items()}

# bootstrap pareado e estratificado: diferença de kappa reponderado contra o léxico
rng = np.random.default_rng(42)
grupos = [np.flatnonzero(estrato == c) for c in CLASSES]
dif = {k: [] for k in cand if not k.startswith("L")}
kap_boot = {k: [] for k in cand}
for _ in range(args.n_boot):
    idx = np.concatenate([rng.choice(g, size=len(g), replace=True) for g in grupos])
    w = peso[idx] / peso[idx].sum()
    kl = kappa(cand["L  léxico"][0][idx], ref[idx], w)
    kap_boot["L  léxico"].append(kl)
    for k in dif:
        kk = kappa(cand[k][0][idx], ref[idx], w)
        kap_boot[k].append(kk)
        dif[k].append(kk - kl)
ic = lambda v: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)))

saida = []
def p(t=""):
    print(t)
    saida.append(t)

def f(x, c=3):
    return f"{x:+.{c}f}".replace(".", ",") if x == x else "  -  "

p("FASE F — LÉXICO x MODELOS DE LINGUAGEM (amostra da Fase E)")
p(f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M} | pré-registro de 02/10/2026")
p(f"Referência: consenso {nome_ref} ({len(cons)} manchetes em que os dois concordam)")
p(f"Pesos da população por classe do léxico: {PESOS_POPULACAO}\n")
p(f"{'candidato':28s} {'kappa pop':>10s} {'IC95%':>17s} {'acur. pop':>10s} {'kappa amostra':>14s} {'Spearman':>9s}")
for k, m in res.items():
    a, b = ic(kap_boot[k])
    p(f"{k:28s} {f(m['kappa_pop']):>10s} [{f(a)}; {f(b)}] {f(m['acc_pop']):>10s} "
      f"{f(m['kappa_amostra']):>14s} {f(m['spearman']):>9s}")
p("\nDiferença de kappa reponderado contra o léxico (bootstrap pareado, 10.000):")
for k in dif:
    a, b = ic(dif[k])
    p(f"  {k:28s} {f(res[k]['kappa_pop'] - res['L  léxico']['kappa_pop'])}   IC95% [{f(a)}; {f(b)}]"
      f"   {'IC acima de zero' if a > 0 else ('IC abaixo de zero' if b < 0 else 'IC inclui zero')}")

kF = "F  FinBERT-PT-BR"
aF, bF = ic(dif[kF])
adota = res[kF]["kappa_pop"] > res["L  léxico"]["kappa_pop"] and aF > 0
p("\nREGRA PRÉ-REGISTRADA (candidato principal F):")
p(f"  kappa F {f(res[kF]['kappa_pop'])} vs L {f(res['L  léxico']['kappa_pop'])}; IC da diferença "
  f"[{f(aF)}; {f(bF)}] -> {'ADOTA o FinBERT-PT-BR nas análises novas' if adota else 'MANTÉM o léxico'}")
p(f"  Leitura do kappa (Landis; Koch, 1977): L {leitura_kappa(res['L  léxico']['kappa_pop'])}, "
  f"F {leitura_kappa(res[kF]['kappa_pop'])}")

p("\nPrecisão e recall por classe (reponderados para a população):")
for k, m in res.items():
    p(f"  {k:28s} " + "  ".join(f"{c[:3]}: P {f(m['precisao'][c], 2)} R {f(m['recall'][c], 2)}" for c in CLASSES))
p("\nMatrizes de confusão na amostra (linhas = candidato, colunas = referência):")
for k, m in res.items():
    mt = m["matriz"]
    p(f"  {k}")
    p("             " + "".join(f"{c:>10s}" for c in CLASSES))
    for c in CLASSES:
        p(f"    {c:9s}" + "".join(f"{mt.loc[c, x]:10d}" for x in CLASSES))

hoje = dt.date.today().isoformat()
arq = RAIZ / "resultados" / f"fase_F_validacao_modelos_{nome_ref}_{hoje}.txt"
arq.write_text("\n".join(saida) + "\n", encoding="utf-8")
json.dump({"referencia": nome_ref, "n": len(cons), "adota_finbert": bool(adota),
           "candidatos": {k: {kk: (vv.to_dict() if isinstance(vv, pd.DataFrame) else vv)
                              for kk, vv in m.items()} for k, m in res.items()},
           "ic_kappa_pop": {k: ic(v) for k, v in kap_boot.items()},
           "ic_diferenca": {k: ic(v) for k, v in dif.items()}},
          open(arq.with_suffix(".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
print(f"\nSalvo em {arq.relative_to(RAIZ)} (+ .json)")
