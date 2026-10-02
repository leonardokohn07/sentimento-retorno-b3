# -*- coding: utf-8 -*-
"""
28_amostra_validacao_lexico.py — monta (ou confere) a amostra da Fase E.

Fase E = validação do léxico (pré-registro de 02/10/2026):
    300 manchetes, 100 de cada classe do léxico (Positivo, Negativo, Neutro),
    sorteadas com semente 42 entre os pares únicos (ativo, manchete) dos 8
    ativos, notícias até 06/09/2026 (fim da coleta usada no estudo).

O que o script faz:
    - Se a planilha dados/validacao_lexico/para_rotular.csv ainda NÃO existe,
      cria a planilha (id;empresa;manchete) e a versão em ordem inversa.
    - Se ela JÁ existe, não mexe em nada: só refaz o sorteio na memória e
      diz se dá exatamente a mesma planilha (prova de que é reproduzível).

O escore do léxico NUNCA é gravado aqui: quem rotula não pode vê-lo.
Quem compara com o léxico é o script 29.

Uso:
    python scripts/28_amostra_validacao_lexico.py
"""
import sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
from modulos.analise.validacao_lexico import montar_amostra

PASTA = RAIZ / "dados" / "validacao_lexico"
PLANILHA = PASTA / "para_rotular.csv"
INVERSA = PASTA / "para_rotular_ordem_inversa.csv"
FIM_DA_COLETA = "2026-09-07"     # notícias ANTES desta data

noticias = pd.read_csv(RAIZ / "dados" / "noticias_com_sentimento.csv")
noticias = noticias[noticias["data"] < FIM_DA_COLETA]
amostra = montar_amostra(noticias)
cega = amostra[["id", "empresa", "manchete"]]
print(f"Amostra reconstruída: {len(cega)} manchetes "
      f"({amostra['classificacao'].value_counts().to_dict()})")

if PLANILHA.exists():
    atual = pd.read_csv(PLANILHA, sep=";")
    iguais = (len(atual) == len(cega)
              and (atual.reset_index(drop=True) == cega.reset_index(drop=True)).all().all())
    if iguais:
        print("OK: a planilha existente é IDÊNTICA à reconstruída (mesmos itens, mesma ordem).")
    else:
        print("ATENÇÃO: a planilha existente é DIFERENTE da reconstruída.")
        print("  Isso acontece se o CSV de notícias foi reordenado ou teve linhas antigas")
        print("  alteradas. A amostra OFICIAL é a planilha congelada; nada foi sobrescrito.")
else:
    PASTA.mkdir(parents=True, exist_ok=True)
    cega.to_csv(PLANILHA, sep=";", index=False, encoding="utf-8")
    cega.iloc[::-1].to_csv(INVERSA, sep=";", index=False, encoding="utf-8")
    print(f"Criadas: {PLANILHA.relative_to(RAIZ)} e {INVERSA.relative_to(RAIZ)}")
