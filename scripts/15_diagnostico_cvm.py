# -*- coding: utf-8 -*-
"""
15_diagnostico_cvm.py
---------------------
DIAGNÓSTICO da Fase D. Não testa hipótese nenhuma — só descreve o dado.

Responde três perguntas, nesta ordem, antes de a gente decidir se a Fase D
vale a pena:

  1. O campo de entrega dos documentos da CVM tem HORA, ou só data?
     É a razão inteira de usar a CVM. Se não tiver hora, a Fase D morre aqui
     e a gente economiza uma semana.

  2. Quantos Fatos Relevantes existem por empresa do estudo?
     Responde a sua própria dúvida: "a amostra não ficaria pequena demais?"

  3. Esse tamanho passa no critério de poder (60 observações)?

Só DEPOIS deste diagnóstico a gente escreve o pré-registro e roda o teste.
Diagnóstico descritivo não precisa de pré-registro; teste de hipótese precisa.

Rodar (da pasta InvestAI):
    .\\venv\\Scripts\\python scripts\\15_diagnostico_cvm.py
"""
from __future__ import annotations

import io
import re
import sys
import unicodedata
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request

import pandas as pd

# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────────────────
ANOS = [2024, 2025, 2026]
BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/IPE/DADOS/ipe_cia_aberta_{ano}.zip"

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "dados" / "cvm"

MIN_OBSERVACOES = 60  # mesmo critério do estudo, vindo da análise de poder

# Empresas do estudo. O arquivo da CVM é indexado por CNPJ e nome, não por
# ticker — então a gente procura por pedaço do nome e CONFERE o que achou.
EMPRESAS = {
    "PETR4": ["PETROLEO BRASILEIRO", "PETROBRAS"],
    "VALE3": ["VALE S.A", "VALE SA", "VALE "],
    "ITUB4": ["ITAU UNIBANCO"],
    "BBDC4": ["BRADESCO"],
    "ABEV3": ["AMBEV"],
    "MGLU3": ["MAGAZINE LUIZA"],
    "SUZB3": ["SUZANO"],
    "WEGE3": ["WEG "],
}


def sem_acento(texto: str) -> str:
    """Tira acento e deixa maiúsculo, pra comparação de nome funcionar."""
    if not isinstance(texto, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).upper()


def baixar(ano: int) -> Path | None:
    """Baixa o zip do ano, se ainda não estiver em disco."""
    DESTINO.mkdir(parents=True, exist_ok=True)
    alvo = DESTINO / f"ipe_cia_aberta_{ano}.zip"
    if alvo.exists() and alvo.stat().st_size > 0:
        print(f"  {ano}: já estava em disco ({alvo.stat().st_size/1e6:.1f} MB)")
        return alvo
    url = BASE.format(ano=ano)
    print(f"  {ano}: baixando {url}")
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (pesquisa academica)"})
        with urlopen(req, timeout=120) as r:
            conteudo = r.read()
        alvo.write_bytes(conteudo)
        print(f"  {ano}: OK, {len(conteudo)/1e6:.1f} MB")
        return alvo
    except Exception as e:
        print(f"  {ano}: FALHOU -> {e}")
        return None


def ler_zip(caminho: Path) -> pd.DataFrame | None:
    """Lê o CSV de dentro do zip. A CVM usa ';' e latin-1."""
    try:
        with zipfile.ZipFile(caminho) as z:
            nomes = [n for n in z.namelist() if n.lower().endswith(".csv")]
            if not nomes:
                print(f"  {caminho.name}: zip sem CSV dentro")
                return None
            with z.open(nomes[0]) as f:
                bruto = f.read()
    except zipfile.BadZipFile:
        print(f"  {caminho.name}: não é um zip válido (provavelmente baixou "
              f"uma página de erro). Apague o arquivo e tente de novo.")
        return None

    for enc in ("latin-1", "utf-8", "cp1252"):
        try:
            return pd.read_csv(io.BytesIO(bruto), sep=";", encoding=enc,
                               dtype=str, low_memory=False)
        except Exception:
            continue
    print(f"  {caminho.name}: não consegui decodificar")
    return None


def main() -> int:
    print("=" * 70)
    print("DIAGNÓSTICO CVM — Fatos Relevantes")
    print("=" * 70)

    print("\n[1/4] Baixando os arquivos IPE")
    partes = []
    for ano in ANOS:
        z = baixar(ano)
        if z is None:
            continue
        df = ler_zip(z)
        if df is not None:
            df["_ano_arquivo"] = ano
            partes.append(df)

    if not partes:
        print("\nNenhum arquivo foi lido. Verifique a internet e tente de novo.")
        return 1

    dados = pd.concat(partes, ignore_index=True)
    print(f"\n  Total de linhas lidas: {len(dados):,}".replace(",", "."))

    # ── PERGUNTA 1: tem hora? ────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("[2/4] PERGUNTA 1 — o campo de entrega tem HORA?")
    print("=" * 70)
    print("\nColunas disponíveis no arquivo:")
    for c in dados.columns:
        print(f"    - {c}")

    candidatas = [c for c in dados.columns
                  if "ENTREGA" in sem_acento(c) or "DATA" in sem_acento(c)]
    print(f"\nColunas de data encontradas: {candidatas}")

    tem_hora = False
    for col in candidatas:
        amostra = dados[col].dropna().astype(str).head(5).tolist()
        print(f"\n  {col} — 5 primeiros valores:")
        for v in amostra:
            print(f"      {v!r}")
        if any(re.search(r"\d{1,2}:\d{2}", str(v)) for v in
               dados[col].dropna().astype(str).head(2000)):
            print(f"      >>> ESTA COLUNA TEM HORA <<<")
            tem_hora = True

    print("\n  VEREDITO DA PERGUNTA 1:")
    if tem_hora:
        print("    TEM HORA. A Fase D faz sentido — dá pra separar notícia")
        print("    divulgada antes e depois da abertura do pregão.")
    else:
        print("    NÃO ACHEI HORA em nenhuma coluna de data.")
        print("    Se confirmar, a Fase D NÃO resolve a limitação dos 95,7%,")
        print("    e a gente precisa repensar antes de investir tempo nela.")

    # ── PERGUNTA 2: quantos fatos relevantes por empresa? ────────────────
    print("\n" + "=" * 70)
    print("[3/4] PERGUNTA 2 — quantos Fatos Relevantes por empresa?")
    print("=" * 70)

    col_cat = next((c for c in dados.columns if "CATEGORIA" in sem_acento(c)), None)
    col_nome = next((c for c in dados.columns if "NOME" in sem_acento(c)), None)

    if col_cat is None or col_nome is None:
        print(f"  Não achei coluna de categoria ou de nome.")
        print(f"  categoria={col_cat}  nome={col_nome}")
        return 1

    print(f"\n  Usando categoria='{col_cat}' e nome='{col_nome}'")
    print("\n  Categorias mais frequentes no arquivo:")
    for cat, n in dados[col_cat].value_counts().head(10).items():
        print(f"    {n:>7,}  {cat}".replace(",", "."))

    fr = dados[dados[col_cat].apply(sem_acento).str.contains("FATO RELEVANTE",
                                                             na=False)]
    print(f"\n  Fatos Relevantes no total: {len(fr):,}".replace(",", "."))

    nomes_norm = fr[col_nome].apply(sem_acento)
    print("\n  Por empresa do estudo:")
    print(f"    {'TICKER':<8} {'FATOS':>7}  {'PODER':<12} NOME ENCONTRADO")
    print("    " + "-" * 66)

    resumo = {}
    for ticker, pedacos in EMPRESAS.items():
        mascara = nomes_norm.apply(
            lambda s: any(sem_acento(p) in s for p in pedacos))
        sub = fr[mascara]
        n = len(sub)
        resumo[ticker] = n
        encontrados = sorted(sub[col_nome].dropna().unique())[:2]
        rotulo = encontrados[0][:34] if encontrados else "(nenhum nome casou)"
        status = "OK" if n >= MIN_OBSERVACOES else f"ABAIXO de {MIN_OBSERVACOES}"
        print(f"    {ticker:<8} {n:>7}  {status:<12} {rotulo}")
        if len(encontrados) > 1:
            for extra in encontrados[1:]:
                print(f"    {'':<8} {'':>7}  {'':<12} + {extra[:34]}")

    # ── PERGUNTA 3: passa no critério? ───────────────────────────────────
    print("\n" + "=" * 70)
    print("[4/4] PERGUNTA 3 — a amostra passa no critério de poder?")
    print("=" * 70)
    aprovados = [t for t, n in resumo.items() if n >= MIN_OBSERVACOES]
    print(f"\n  Critério do estudo: mínimo {MIN_OBSERVACOES} observações por ativo")
    print(f"  Ativos que passam: {len(aprovados)} de {len(EMPRESAS)}")
    if aprovados:
        print(f"    {', '.join(aprovados)}")
    reprovados = [f"{t} ({resumo[t]})" for t in EMPRESAS if resumo[t] < MIN_OBSERVACOES]
    if reprovados:
        print(f"  Ativos abaixo do mínimo: {', '.join(reprovados)}")

    print("\n  ATENÇÃO: esse número é o total de Fatos Relevantes publicados.")
    print("  O N final do teste será MENOR, porque só conta fato relevante que")
    print("  caia em dia com pregão e com cotação disponível. Conte com perda.")

    saida = DESTINO / "diagnostico_resumo.csv"
    pd.DataFrame([{"ticker": t, "fatos_relevantes": n,
                   "passa_criterio": n >= MIN_OBSERVACOES}
                  for t, n in resumo.items()]).to_csv(saida, index=False)
    print(f"\n  Resumo salvo em: {saida}")

    print("\n" + "=" * 70)
    print("PRÓXIMO PASSO")
    print("=" * 70)
    print("  Me manda a saída inteira deste script.")
    print("  Com a resposta das 3 perguntas a gente faz a análise de poder e")
    print("  escreve o pré-registro ANTES de rodar qualquer teste.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
