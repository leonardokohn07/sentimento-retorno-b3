# -*- coding: utf-8 -*-
"""
29_validacao_lexico.py — compara o léxico com os rótulos dos anotadores (Fase E).

Segue o pré-registro docs/pre-registro_2026-10-02_validacao-do-lexico.md:
    1. concordância entre os dois anotadores (kappa de Cohen, 3 classes);
    2. léxico x CONSENSO (itens em que os dois anotadores concordam):
       acurácia (amostra e reponderada para a população), precisão de cada
       classe do léxico, kappa, matriz de confusão e Spearman entre o escore
       contínuo e o rótulo (-1, 0, +1);
    3. sensibilidade: discordâncias contadas como "neutro".
Extras marcados como COMPLEMENTAR (não pré-registrados): intervalos de
confiança por bootstrap, cada anotador sozinho e a matriz reponderada.

Uso:
    python scripts/29_validacao_lexico.py            # anotadores automáticos A e B
    python scripts/29_validacao_lexico.py --humanos  # Leonardo e Maurício
"""
import sys, json, argparse, datetime as dt
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import numpy as np
import pandas as pd
from modulos.analise.validacao_lexico import (
    CLASSES, PESOS_POPULACAO, escores_da_planilha, ler_rotulos, kappa,
    metricas, bootstrap, spearman_permutacao, leitura_kappa, CODIGO)

PASTA = RAIZ / "dados" / "validacao_lexico"
# Rótulos do Claude ficam numa subpasta separada: Leonardo e Maurício NÃO
# podem abrir antes de terminar a rotulagem deles (pré-registro).
CLAUDE = PASTA / "claude_NAO_ABRIR_antes_de_rotular"
ap = argparse.ArgumentParser()
ap.add_argument("--humanos", action="store_true",
                help="usa as planilhas de Leonardo e Maurício em vez dos anotadores automáticos")
ap.add_argument("--n-boot", type=int, default=10_000)
ap.add_argument("--n-perm", type=int, default=10_000)
args = ap.parse_args()

if args.humanos:
    nome = "humanos"
    arquivos = {"Leonardo": PASTA / "rotulagem_sentimento_Leonardo.xlsx",
                "Mauricio": PASTA / "rotulagem_sentimento_Mauricio.xlsx"}
    terceiros = {"Claude A": CLAUDE / "rotulos_anotador_A.csv",
                 "Claude B": CLAUDE / "rotulos_anotador_B.csv"}
else:
    nome = "preliminar_claude"
    arquivos = {"Claude A": CLAUDE / "rotulos_anotador_A.csv",
                "Claude B": CLAUDE / "rotulos_anotador_B.csv"}
    terceiros = {}

planilha = pd.read_csv(PASTA / "para_rotular.csv", sep=";")
noticias = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv")
base = escores_da_planilha(planilha, noticias).set_index("id")

(n1, a1), (n2, a2) = arquivos.items()
try:
    r1, r2 = ler_rotulos(a1), ler_rotulos(a2)
except (ValueError, FileNotFoundError) as erro:
    raise SystemExit(f"Ainda não dá para calcular: {erro}\n"
                     "Termine a rotulagem (todas as 300 linhas) e rode de novo.")
for n_, r_ in [(n1, r1), (n2, r2)]:
    if set(r_.index) != set(base.index):
        raise SystemExit(f"{n_}: os ids não batem com a planilha")
if args.humanos:
    # Guarda os rótulos humanos num CSV só com id;rotulo (sem o texto das
    # manchetes), que pode ir para o git. As planilhas .xlsx ficam fora dele.
    for n_, r_ in [(n1, r1), (n2, r2)]:
        r_.rename("rotulo").to_frame().to_csv(PASTA / f"rotulos_{n_}.csv",
                                              sep=";", encoding="utf-8")
base[n1], base[n2] = r1, r2

saida = []
def p(txt=""):
    print(txt)
    saida.append(txt)

def f(x, casas=3):
    return f"{x:.{casas}f}".replace(".", ",")

def ic(par):
    return f"[{f(par[0])}; {f(par[1])}]"

def bloco_metricas(titulo, lex, ref, esc, com_ic=True):
    m = metricas(lex, ref, esc)
    b = bootstrap(lex, ref, n_boot=args.n_boot) if com_ic else None
    rho, p_rho = spearman_permutacao(esc, [CODIGO[x] for x in ref], n_perm=args.n_perm)
    p(f"\n{titulo}  (n = {m['n']})")
    p(f"  Acurácia na amostra .............. {f(m['acuracia_amostra'])}"
      + (f"  IC95% {ic(b['acuracia_amostra'])}" if b else ""))
    p(f"  Acurácia reponderada (população) . {f(m['acuracia_populacao'])}"
      + (f"  IC95% {ic(b['acuracia_populacao'])}" if b else ""))
    p("  Precisão de cada classe do léxico (quando o léxico diz X, os anotadores também dizem X):")
    for c in CLASSES:
        p(f"     {c:9s} {f(m['precisao_por_classe'][c])}  "
          f"(n = {m['n_por_classe_do_lexico'][c]})"
          + (f"  IC95% {ic(b['precisao_por_classe'][c])}" if b else ""))
    p(f"  Kappa léxico x referência ........ {f(m['kappa'])}  ({leitura_kappa(m['kappa'])})"
      + (f"  IC95% {ic(b['kappa'])}" if b else ""))
    p(f"  Spearman escore x rótulo (-1,0,+1)  {f(m['spearman'])}  "
      f"(p permutação = {f(p_rho, 4)})")
    p("  Matriz de confusão (linhas = léxico, colunas = referência):")
    mt = m["matriz"]
    p("               " + "".join(f"{c:>10s}" for c in CLASSES))
    for c in CLASSES:
        p(f"     {c:9s}" + "".join(f"{mt.loc[c, k]:10d}" for k in CLASSES))
    m["ic"] = b
    m["spearman_p"] = p_rho
    return m


p("FASE E — VALIDAÇÃO DO LÉXICO DE SENTIMENTO")
p(f"Gerado em {dt.datetime.now():%d/%m/%Y %H:%M} | pré-registro de 02/10/2026")
p(f"Anotadores: {n1} e {n2}" + ("  (AUTOMÁTICOS: checagem preliminar, não substitui humanos)"
                               if not args.humanos else ""))
p(f"Amostra: {len(base)} manchetes, estratificada pela classe do léxico "
  f"({base['lexico'].value_counts().to_dict()})")
p(f"Pesos da população: " + ", ".join(f"{c} {f(PESOS_POPULACAO[c]*100,1)}%" for c in CLASSES))

# 1) concordância entre anotadores
igual = base[n1] == base[n2]
k12 = kappa(base[n1], base[n2])
p("\n1) CONCORDÂNCIA ENTRE OS ANOTADORES")
p(f"  Concordaram em {igual.sum()} de {len(base)} ({f(igual.mean()*100,1)}%)")
p(f"  Kappa de Cohen = {f(k12)}  ({leitura_kappa(k12)})")
for nm in (n1, n2):
    p(f"  Distribuição {nm}: " + ", ".join(f"{c} {int((base[nm]==c).sum())}" for c in CLASSES))
disc = base[~igual]
# Só o padrão agregado, sem ids: quem ainda vai rotular não pode ver item a item.
padrao = (disc[n1] + " x " + disc[n2]).value_counts()
p(f"  Discordâncias: {len(disc)} ({n1} x {n2}: " +
  ", ".join(f"{k} {v}" for k, v in padrao.items()) + ")")

# 2) principal: léxico x consenso
cons = base[igual]
p("\n2) PRINCIPAL — LÉXICO x CONSENSO DOS ANOTADORES")
principal = bloco_metricas("Léxico x consenso", cons["lexico"], cons[n1], cons["score_polaridade"])

# 3) sensibilidade: discordância vira neutro
ref_s = base[n1].where(igual, "neutro")
p("\n3) SENSIBILIDADE — discordâncias contadas como 'neutro'")
sens = bloco_metricas("Léxico x referência (discordância = neutro)",
                      base["lexico"], ref_s, base["score_polaridade"])

# 4) complementar
p("\n4) COMPLEMENTAR (não pré-registrado)")
comp = {}
for nm in [n1, n2] + list(terceiros):
    if nm in terceiros:
        try:
            r = ler_rotulos(terceiros[nm])
        except Exception as e:
            p(f"  {nm}: não lido ({e})")
            continue
        lab = r.reindex(base.index)
    else:
        lab = base[nm]
    acc = float((base["lexico"] == lab).mean())
    kk = kappa(base["lexico"], lab)
    comp[nm] = {"acuracia_amostra": acc, "kappa": kk}
    p(f"  Léxico x {nm:9s} sozinho: acurácia {f(acc)}, kappa {f(kk)}")
    if args.humanos and nm in terceiros:
        kh = [kappa(base[h], lab) for h in (n1, n2)]
        comp[nm]["kappa_com_humanos"] = kh
        p(f"     concordância {nm} x {n1}: kappa {f(kh[0])}; x {n2}: kappa {f(kh[1])}")

mp = principal["matriz_populacao"]
p("  Matriz REPONDERADA para a população (léxico x consenso, em % do total):")
p("               " + "".join(f"{c:>10s}" for c in CLASSES))
for c in CLASSES:
    p(f"     {c:9s}" + "".join(f"{f(mp.loc[c, k]*100,1):>10s}" for k in CLASSES))
rev = {c: float(mp.loc[c, c] / mp[c].sum()) for c in CLASSES}
p("  Das manchetes que os anotadores julgam X, quanto o léxico também chama de X")
p("  (sensibilidade/recall estimado na população):  " +
  ", ".join(f"{c} {f(rev[c])}" for c in CLASSES))
p(f"  Kappa reponderado para a população: {f(principal['kappa_populacao'])}")

# salvar
hoje = dt.date.today().isoformat()
arq_txt = RAIZ / "resultados" / f"validacao_lexico_{nome}_{hoje}.txt"
arq_txt.write_text("\n".join(saida) + "\n", encoding="utf-8")

def limpo(m):
    return {k: (v.round(6).to_dict() if isinstance(v, pd.DataFrame) else v)
            for k, v in m.items()}
json.dump({"anotadores": [n1, n2], "n": len(base),
           "concordancia": float(igual.mean()), "kappa_anotadores": k12,
           "discordancias": {k: int(v) for k, v in padrao.items()},
           "principal": limpo(principal), "sensibilidade": limpo(sens),
           "complementar": {"por_anotador": comp, "recall_populacao": rev}},
          open(arq_txt.with_suffix(".json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1, default=float)
print(f"\nSalvo em {arq_txt.relative_to(RAIZ)} (+ .json)")
