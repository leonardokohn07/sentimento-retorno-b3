# -*- coding: utf-8 -*-
"""
34_coleta_diaria.py — coleta prospectiva da Fase G (roda todo dia).

Pré-registro: docs/pre-registro_2026-10-02_fase-G_minuto.md

O que faz, em ordem:
  1. barras de 1 e 5 minutos do Yahoo (scripts/31_baixar_minuto.py), acrescentando;
  2. notícias dos últimos 3 dias + horário do WordPress (scripts/32_coletar_recentes.py --dias 3);
  3. CONTA quantos eventos confirmatórios já existem (a partir de 03/10/2026,
     dia útil, 10h30-16h20, com horário exato). Só conta: a correlação NÃO é
     calculada antes da regra de parada (1.500 eventos ou 30/06/2027).

Agendamento: scripts/AGENDAR_COLETA_DIARIA.bat (o Leonardo roda uma vez).
Log: dados/prospectivo/log_coleta_diaria.txt
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd

INICIO_CONFIRMATORIO = "2026-10-03"
META, PRAZO = 1500, "2027-06-30"
LOG = RAIZ / "dados" / "prospectivo" / "log_coleta_diaria.txt"


def log(texto):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    linha = f"{datetime.now():%Y-%m-%d %H:%M} {texto}"
    print(linha)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def rodar(*args):
    r = subprocess.run([sys.executable, "-u", *args], cwd=RAIZ)
    return r.returncode


def contar_eventos():
    from modulos.analise.fuso import ajustar_pregao_brasilia
    from modulos.analise.horarios import filtrar_wordpress
    arq_n = RAIZ / "dados" / "prospectivo" / "noticias_recentes.csv"
    arq_w = RAIZ / "dados" / "prospectivo" / "horarios_wordpress_recentes.csv"
    if not arq_n.exists():
        return 0
    n = ajustar_pregao_brasilia(pd.read_csv(arq_n))
    t = n["data_brasilia"].where(n["hora_real"])
    if arq_w.exists():
        wpf = filtrar_wordpress(n, pd.read_csv(arq_w)).drop_duplicates("url").set_index("url")["t_wp_filtrado"]
        t = t.fillna(n["url"].map(wpf))
    n["t"] = t
    n = n.dropna(subset=["t"])
    minuto = n["t"].dt.hour * 60 + n["t"].dt.minute
    n = n[(n["t"] >= INICIO_CONFIRMATORIO) & (n["t"].dt.weekday < 5)
          & (minuto >= 630) & (minuto < 980)]
    faixa = n["t"].dt.floor("5min")
    return int(pd.DataFrame({"a": n["ticker"], "f": faixa}).drop_duplicates().shape[0])


def main():
    log("início da coleta diária")
    c1 = rodar("scripts/31_baixar_minuto.py")
    c2 = rodar("scripts/32_coletar_recentes.py", "--dias", "3", "--limite-wp-min", "10")
    n = contar_eventos()
    falta = max(0, META - n)
    log(f"fim (minuto: {'ok' if c1 == 0 else 'ERRO'}, notícias: {'ok' if c2 == 0 else 'ERRO'}) | "
        f"eventos confirmatórios: {n} de {META} (faltam {falta}; prazo {PRAZO})")
    if n >= META or datetime.now() >= datetime.fromisoformat(PRAZO):
        log("REGRA DE PARADA ATINGIDA: hora de rodar M1 e M2 confirmatórios (uma vez).")


if __name__ == "__main__":
    main()
