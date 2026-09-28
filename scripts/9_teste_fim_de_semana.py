"""
9_teste_fim_de_semana.py
------------------------
TESTE DE ROBUSTEZ — a subamostra causalmente limpa.

O PROBLEMA QUE ESTE SCRIPT RESOLVE
    A análise principal casa o sentimento das notícias de um dia com o
    retorno do pregão daquele mesmo dia (D+0). Isso deixa uma ambiguidade
    que não pode ser resolvida com os dados disponíveis:

        a notícia CAUSOU o movimento, ou apenas o RELATOU?

    O módulo ajustar_data_pregao foi escrito para tratar isso — notícia
    publicada após o fechamento vale para o pregão seguinte. Mas a regra
    depende do horário de publicação, e o Google News NÃO entrega horário
    real: 95,7% dos registros têm o timestamp cravado em :00:00, quase
    todos em 07h ou 08h. Sem hora confiável, a regra quase nunca dispara.

A SOLUÇÃO
    Existe uma subamostra em que a ordem causal é garantida SEM depender
    de horário nenhum: as notícias publicadas no SÁBADO e no DOMINGO.

    No fim de semana não há pregão. Uma notícia de sábado não pode estar
    descrevendo o movimento de segunda-feira, porque esse movimento ainda
    não existe. A causalidade fica assegurada pelo calendário, não pelo
    relógio.

    Rodando a mesma análise apenas nessas notícias, contra o retorno da
    segunda-feira seguinte, obtém-se uma medida imune à crítica de
    causalidade reversa.

COMO LER O RESULTADO
    Significativo  -> evidência causal limpa. A crítica fica respondida.
    Não significativo -> a subamostra é bem menor; compare o n com o
                      limite de detecção antes de concluir ausência de
                      efeito. Pode ser falta de poder, não falta de efeito.

Como rodar (a partir da pasta InvestAI/):
    venv\\Scripts\\activate
    python scripts\\9_teste_fim_de_semana.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
import pandas as pd

from modulos.coleta.precos import baixar_dados, calcular_retornos
from modulos.analise.hipotese import (
    montar_serie_diaria, regressao_sentimento_retorno, MIN_OBSERVACOES,
)
from modulos.caminhos import ARQ_NOTICIAS

MIN_ROBUSTEZ = 30   # relaxado: a subamostra de fim de semana é pequena


def r_critico(n: int) -> float:
    """Menor correlação que atinge significância a 5% com n observações."""
    return 1.96 / np.sqrt(n) if n > 4 else float("nan")


print("\n" + "=" * 74)
print("  TESTE DE ROBUSTEZ — SUBAMOSTRA DE FIM DE SEMANA")
print("=" * 74)

if not ARQ_NOTICIAS.exists():
    print("\n[ERRO] Arquivo de notícias não encontrado. Rode a coleta antes.")
    sys.exit(1)

noticias = pd.read_csv(ARQ_NOTICIAS, parse_dates=["data", "data_pregao"])
print(f"\n  Notícias no arquivo : {len(noticias)}")

# ── Separa a subamostra ──
# weekday(): 5 = sábado, 6 = domingo
noticias["dia_semana"] = noticias["data"].dt.weekday
fds = noticias[noticias["dia_semana"] >= 5].copy()

print(f"  Publicadas no fim de semana : {len(fds)}  "
      f"({len(fds)/len(noticias)*100:.1f}%)")
print(f"  Sábados  : {(fds['dia_semana'] == 5).sum()}")
print(f"  Domingos : {(fds['dia_semana'] == 6).sum()}")

if fds.empty:
    print("\n[ERRO] Nenhuma notícia de fim de semana encontrada.")
    sys.exit(1)

# Confere se o ajuste jogou mesmo para segunda-feira
seg = (fds["data_pregao"].dt.weekday == 0).mean() * 100
print(f"\n  Atribuídas ao pregão de segunda-feira : {seg:.1f}%")
print("  (o ajustar_data_pregao empurra sábado +2 dias e domingo +1)")

tickers = sorted(fds["ticker"].dropna().unique())
print(f"\n  Ativos na subamostra : {len(tickers)}")

# ── Preços ──
print("\n  Baixando preços (histórico 5 anos)...")
dados = baixar_dados(tickers, periodo="5y")
if not dados:
    print("\n[ERRO] Não foi possível baixar preços.")
    sys.exit(1)
retornos = calcular_retornos(dados)

# ── Análise comparada ──
print("\n" + "=" * 74)
print("  RESULTADO — amostra completa  x  somente fim de semana")
print("=" * 74)
print(f"\n  {'ativo':<10} | {'--- AMOSTRA COMPLETA ---':^30} | "
      f"{'--- SÓ FIM DE SEMANA ---':^32}")
print(f"  {'':<10} | {'n':>5} {'r':>8} {'p':>8} {'sig':>5} | "
      f"{'n':>5} {'r':>8} {'p':>8} {'r_crit':>7} {'sig':>5}")
print("  " + "-" * 72)

linhas = []
for tk in tickers:
    # completa
    s_full = montar_serie_diaria(noticias, retornos, tk)
    if s_full.empty or len(s_full) < MIN_OBSERVACOES:
        continue
    reg_f = regressao_sentimento_retorno(s_full, lag=0)
    if "erro" in reg_f:
        continue

    # fim de semana
    s_fds = montar_serie_diaria(fds, retornos, tk)
    n_fds = len(s_fds)

    if n_fds >= MIN_ROBUSTEZ:
        reg_w = regressao_sentimento_retorno(s_fds, lag=0)
        if "erro" in reg_w:
            rw = pw = float("nan"); sw = "—"
        else:
            rw, pw = reg_w["r"], reg_w["p_valor"]
            sw = "SIM" if reg_w["significativo_5pct"] else "não"
        rc = r_critico(n_fds)
    else:
        rw = pw = rc = float("nan"); sw = "n<30"

    sig_f = "SIM" if reg_f["significativo_5pct"] else "não"
    esq = (f"  {tk:<10} | {len(s_full):>5} {reg_f['r']:>8.4f} "
           f"{reg_f['p_valor']:>8.4f} {sig_f:>5} | ")

    if np.isnan(rw):
        dir_ = f"{n_fds:>5} {'—':>8} {'—':>8} {'—':>7} {sw:>5}"
    else:
        dir_ = f"{n_fds:>5} {rw:>8.4f} {pw:>8.4f} {rc:>7.3f} {sw:>5}"

    print(esq + dir_)

    linhas.append({
        "ticker": tk,
        "n_full": len(s_full), "r_full": reg_f["r"],
        "sig_full": reg_f["significativo_5pct"],
        "n_fds": n_fds, "r_fds": rw, "p_fds": pw,
        "sig_fds": (sw == "SIM"), "r_crit": rc,
    })

# ── Veredito ──
validos = [l for l in linhas if l["n_fds"] >= MIN_ROBUSTEZ and not np.isnan(l["r_fds"])]
print("\n" + "=" * 74)
print("  VEREDITO DO TESTE DE ROBUSTEZ")
print("=" * 74)

if not validos:
    print("\n  Nenhum ativo atingiu o mínimo de 30 observações no fim de semana.")
    print("  A subamostra causalmente limpa é pequena demais para testar.")
    print("  Isso deve ser reportado como limitação — não como ausência de efeito.")
else:
    sig = sum(1 for l in validos if l["sig_fds"])
    print(f"\n  Ativos testáveis          : {len(validos)}")
    print(f"  Com relação significativa : {sig}/{len(validos)}")
    print(f"  n médio da subamostra     : {np.mean([l['n_fds'] for l in validos]):.0f}")

    print("\n  Comparação das correlações (mesma direção?):")
    for l in validos:
        seta = "=" if np.sign(l["r_full"]) == np.sign(l["r_fds"]) else "≠"
        print(f"    {l['ticker']:<10} completa {l['r_full']:+.4f}  {seta}  "
              f"fim de semana {l['r_fds']:+.4f}")

    print()
    if sig >= len(validos) * 0.5:
        print("  >>> EVIDÊNCIA CAUSAL SUSTENTADA.")
        print("      O efeito aparece mesmo na subamostra em que a notícia")
        print("      NÃO pode estar descrevendo o movimento. A crítica de")
        print("      causalidade reversa fica respondida com dados.")
    else:
        print("  >>> INCONCLUSIVO NA SUBAMOSTRA.")
        print("      Antes de concluir ausência de efeito, compare o r observado")
        print("      com o r_crit da tabela: se |r| < r_crit, o teste não tinha")
        print("      poder para detectar — é limitação de amostra, não evidência")
        print("      de que o efeito inexiste.")

print("\n" + "=" * 74 + "\n")
