# -*- coding: utf-8 -*-
"""
verificar_tudo.py — refaz TODOS os testes do estudo a partir dos dados
congelados e confere se os resultados saem iguais aos publicados.

Uso (na pasta do projeto):
    python verificacao/verificar_tudo.py              verifica tudo (~1 hora)
    python verificacao/verificar_tudo.py --so-dados   só confere os dados (1 minuto)
    python verificacao/verificar_tudo.py --etapas E03 E27   só algumas etapas
    python verificacao/verificar_tudo.py --listar     mostra as etapas
No Windows: dois cliques em VERIFICAR_TUDO.bat.

O que ele faz, em ordem:
    1. Confere a "impressão digital" (SHA-256) de cada arquivo dos dados
       congelados contra o manifesto publicado no git. Se um único byte de um
       único arquivo mudou, o hash muda e a verificação para.
    2. Monta uma pasta de execução separada (verificacao/_execucao/), com os
       dados congelados e uma cópia do código. Os dados do dia a dia (dados/)
       nunca são lidos nem alterados.
    3. Roda cada script com o relógio parado em 02/10/2026 12:00 e sem
       internet para preços (INVESTAI_SO_CACHE=1).
    4. Compara cada arquivo de resultado com a referência
       (verificacao/referencia/). Texto: idêntico, letra por letra. Tabelas e
       JSON: idênticos ou com diferença numérica menor que 1e-9. Imagens: só
       a existência (o desenho muda com a versão do matplotlib).
    5. Escreve o relatório em verificacao/relatorio_verificacao.txt.

Só para os autores (refazer a referência ou o manifesto):
    python verificacao/verificar_tudo.py --gerar-manifesto
    python verificacao/verificar_tudo.py --gerar-referencia
"""
import argparse
import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
NOME_PACOTE = "dados_congelados_2026-10-02"
PACOTE = AQUI / f"{NOME_PACOTE}.zip"
MANIFESTO = AQUI / f"manifesto_{NOME_PACOTE}.sha256"
REFERENCIA = AQUI / "referencia"
EXECUCAO = AQUI / "_execucao"
RELATORIO = AQUI / "relatorio_verificacao.txt"
TOL = 1e-9

# ─────────────────────────────────────────────────────────────────────────────
# As etapas: (id, script, argumentos, o que reproduz, etapas de que depende)
# ─────────────────────────────────────────────────────────────────────────────
ETAPAS = [
    ("E00", "testes/test_alinhamento.py", [], "teste automático do alinhamento de datas (bug dos 16,6%)", []),
    ("E01", "scripts/1_validar_modulo_estatistico.py", [], "validação do método com séries sintéticas", []),
    ("E02", "scripts/7_curvas_de_deteccao.py", [], "curvas de detecção (poder do teste)", []),
    ("E03", "scripts/congelar_resultados.py", [], "resultado original: D+0 e D+1 por ativo", []),
    ("E04", "scripts/12_teste_permutacao.py", [], "permutação por ativo (10.000)", []),
    ("E05", "scripts/13_defasagem_negativa.py", [], "controle de causalidade reversa (D−1)", []),
    ("E06", "scripts/14_curva_de_defasagem.py", [], "curva de defasagem D−5 a D+5", []),
    ("E07", "scripts/9_teste_fim_de_semana.py", [], "fim de semana por ativo (antigo)", []),
    ("E08", "scripts/16_impacto_fuso.py", [], "impacto do bug de fuso horário", []),
    ("E09", "scripts/17_fim_de_semana_agrupado.py", ["--rotulo", "principal"], "fim de semana agrupado (principal)", []),
    ("E10", "scripts/17_fim_de_semana_agrupado.py", ["--rotulo", "sensibilidade", "--sem-correcao-fuso"],
     "fim de semana agrupado (sem correção de fuso)", []),
    ("E11", "scripts/17_fim_de_semana_agrupado.py", ["--rotulo", "estendido", "--extra", "dados/noticias_2021_2023.csv"],
     "fim de semana agrupado (com 2021-2023)", []),
    ("E12", "scripts/19_sem_manchetes_de_preco.py", [], "teste 1: sem manchetes de preço", []),
    ("E13", "scripts/20_placebo_entre_empresas.py", [], "teste 2: placebo entre empresas", []),
    ("E14", "scripts/21_retorno_anormal.py", [], "teste 3: retorno anormal (Ibovespa)", []),
    ("E15", "scripts/22_granger.py", [], "teste 5: Granger diário", []),
    ("E16", "scripts/25_fase_causal.py", [], "fase causal, análise principal (P1-P9, S1-S7)", []),
    ("E17", "scripts/25_fase_causal.py", ["--adicional-wp"], "fase causal, análise adicional A1", []),
    ("E18", "scripts/25_fase_causal.py", ["--medida", "finbert"], "fase causal principal com FinBERT", []),
    ("E19", "scripts/25_fase_causal.py", ["--adicional-wp", "--medida", "finbert"], "A1 com FinBERT", []),
    ("E20", "scripts/27_exploratorio_pos_resultado.py", [], "exploratório E1-E3 (decidido depois)", []),
    ("E21", "scripts/28_amostra_validacao_lexico.py", [], "Fase E: a amostra de 300 manchetes se refaz igual", []),
    ("E22", "scripts/29_validacao_lexico.py", [], "Fase E: léxico x anotadores (preliminar)", []),
    ("E23", "scripts/35_validacao_modelos.py", [], "Fase F: léxico x FinBERT x distilbert", []),
    ("E24", "scripts/36_resultado_original_medida.py", [], "Fase F, R3: resultado original por medida", []),
    ("E25", "scripts/39_resumo_fase_F.py", ["--data", "2026-10-02"], "Fase F: robustez lado a lado + exploratório",
     ["E16", "E17", "E18", "E19", "E24"]),  # E24: lê o CSV do R3 (faltava; corrida achada em 10/10/2026)
    ("E26", "scripts/37_piloto_minuto.py", [], "Fase G: piloto de 30 minutos (barras de 5 min)", []),
    ("E27", "scripts/40_janelas_curtas.py", [], "Fase G, adendo 2: janelas de até 5 minutos", []),
    ("E28", "scripts/38_smallcaps_testes.py", [], "Fase H: small caps (léxico)", []),
    ("E29", "scripts/38_smallcaps_testes.py", ["--medida", "finbert"], "Fase H: small caps (FinBERT)", []),
    ("E30", "scripts/26_grafico_perfil_horario.py", [], "gráfico do perfil hora a hora",
     ["E16", "E17", "E18", "E19"]),
    ("E31", "scripts/41_grafico_perfil_minuto.py", [], "gráfico do perfil minuto a minuto", ["E27"]),
]
POR_ID = {e[0]: e for e in ETAPAS}

# linhas da tela que mudam de máquina para máquina e não são resultado
IGNORAR_NA_TELA = re.compile(
    r"(Warning|warnings\.warn|DeprecationWarning|FutureWarning|^\s*$|"
    r"\[CACHE\]|\[OK\]|\[AVISO\]|tempo|segundos|elapsed|it/s)", re.IGNORECASE)


def sha256(caminho, bloco=1 << 20):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for parte in iter(lambda: f.read(bloco), b""):
            h.update(parte)
    return h.hexdigest()


def ler_manifesto():
    linhas = {}
    for ln in MANIFESTO.read_text(encoding="utf-8").splitlines():
        if ln.strip() and not ln.startswith("#"):
            h, nome = ln.split(None, 1)
            linhas[nome.strip()] = h
    return linhas


# ─────────────────────────────── 1. dados ───────────────────────────────────
def conferir_dados(destino, log):
    """Extrai o pacote em destino/dados e confere cada arquivo contra o manifesto."""
    if not PACOTE.exists():
        log(f"  [FALTA] {PACOTE.name} não está em verificacao/. Copie o pacote para lá.")
        return False
    esperado = ler_manifesto()
    with zipfile.ZipFile(PACOTE) as z:
        z.extractall(destino)
    pasta = destino / "dados"
    achados = {p.relative_to(pasta).as_posix(): p for p in sorted(pasta.rglob("*")) if p.is_file()}
    ok = True
    for nome, h in esperado.items():
        if nome not in achados:
            log(f"  [FALTA]     {nome}")
            ok = False
        elif sha256(achados[nome]) != h:
            log(f"  [ALTERADO]  {nome}")
            ok = False
    extras = sorted(set(achados) - set(esperado))
    for nome in extras:
        log(f"  [A MAIS]    {nome}")
        ok = False
    log(f"  {len(esperado)} arquivos no manifesto; "
        + ("TODOS com o hash certo." if ok else "HÁ DIFERENÇAS (veja acima)."))
    return ok


def gerar_manifesto(pasta_dados):
    """Só para os autores: grava o manifesto a partir de uma pasta de dados."""
    linhas = ["# SHA-256 de cada arquivo de dados congelados em 02/10/2026.",
              "# Gerado por verificacao/verificar_tudo.py --gerar-manifesto.",
              "# Mude um byte de qualquer arquivo e o hash dele muda."]
    for p in sorted(pasta_dados.rglob("*")):
        if p.is_file():
            linhas.append(f"{sha256(p)}  {p.relative_to(pasta_dados).as_posix()}")
    MANIFESTO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"manifesto: {MANIFESTO.name} ({len(linhas) - 3} arquivos)")


# ───────────────────────────── 2-3. execução ─────────────────────────────────
def montar_pasta(destino):
    for sub in ("scripts", "modulos", "testes", "verificacao"):
        origem = RAIZ / sub
        if sub == "verificacao":
            (destino / sub).mkdir(parents=True, exist_ok=True)
            shutil.copy2(AQUI / "_relogio_congelado.py", destino / sub / "_relogio_congelado.py")
            continue
        shutil.copytree(origem, destino / sub, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (destino / "resultados").mkdir(exist_ok=True)


def rodar_etapa(etapa, pasta):
    eid, script, args, _, _ = etapa
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1", MPLBACKEND="Agg",
               PYTHONHASHSEED="0", INVESTAI_SO_CACHE="1", PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-u", "verificacao/_relogio_congelado.py", script] + args
    t0 = time.time()
    r = subprocess.run(cmd, cwd=pasta, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return eid, r.returncode, r.stdout, r.stderr, time.time() - t0


def normalizar_texto(txt, pasta):
    txt = txt.replace("\r\n", "\n").replace(str(pasta), "<RAIZ>").replace("\\", "/")
    return txt.replace(str(pasta).replace("\\", "/"), "<RAIZ>")


def tela_filtrada(txt, pasta):
    return "\n".join(ln for ln in normalizar_texto(txt, pasta).splitlines()
                     if not IGNORAR_NA_TELA.search(ln)) + "\n"


def executar(ids, pasta, log, paralelo):
    """Roda as etapas respeitando as dependências. Devolve {id: (código, tela, erro, s, arquivos)}."""
    antes = {}
    res = {}
    pendentes = list(ids)
    feitas = set()
    # Sem paralelismo, cada etapa vê claramente quais arquivos ela criou.
    # Com paralelismo, os arquivos de cada etapa vêm da lista da referência.
    lista_ref = json.loads((REFERENCIA / "arquivos_por_etapa.json").read_text(encoding="utf-8")) \
        if (REFERENCIA / "arquivos_por_etapa.json").exists() else {}

    def arquivos_atuais():
        return {p.name: p.stat().st_mtime_ns for p in (pasta / "resultados").glob("*") if p.is_file()}

    if paralelo <= 1 or not lista_ref:
        for eid in pendentes:
            antes = arquivos_atuais()
            log(f"  {eid} {POR_ID[eid][3]} ...")
            _, cod, out, err, s = rodar_etapa(POR_ID[eid], pasta)
            depois = arquivos_atuais()
            novos = sorted(n for n, m in depois.items() if antes.get(n) != m)
            res[eid] = (cod, out, err, s, novos)
            log(f"      terminou em {s:.0f} s (código {cod}); arquivos: {', '.join(novos) or 'só a tela'}")
        return res

    with ThreadPoolExecutor(max_workers=paralelo) as ex:
        rodando = {}
        while pendentes or rodando:
            for eid in list(pendentes):
                deps = [d for d in POR_ID[eid][4] if d in ids]
                if all(d in feitas for d in deps) and len(rodando) < paralelo:
                    pendentes.remove(eid)
                    log(f"  {eid} começou: {POR_ID[eid][3]}")
                    rodando[eid] = ex.submit(rodar_etapa, POR_ID[eid], pasta)
            time.sleep(0.5)
            for eid, fut in list(rodando.items()):
                if fut.done():
                    _, cod, out, err, s = fut.result()
                    res[eid] = (cod, out, err, s, lista_ref.get(eid, []))
                    feitas.add(eid)
                    del rodando[eid]
                    log(f"  {eid} terminou em {s:.0f} s (código {cod})")
    return res


# ─────────────────────────────── 4. comparação ──────────────────────────────
def numeros_iguais(a, b):
    """Compara dois JSON/CSV já lidos, com tolerância numérica."""
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
            return (isinstance(a, float) and math.isnan(a)) and (isinstance(b, float) and math.isnan(b))
        return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(numeros_iguais(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(numeros_iguais(x, y) for x, y in zip(a, b))
    return a == b


def _csv_para_lista(txt):
    linhas = []
    for ln in txt.splitlines():
        cel = []
        for c in ln.split(","):
            try:
                cel.append(float(c))
            except ValueError:
                cel.append(c)
        linhas.append(cel)
    return linhas


def comparar_arquivo(novo, ref, pasta):
    """Devolve 'IDÊNTICO', 'IGUAL (dif. < 1e-9)', 'EXISTE' (imagem) ou 'DIFERENTE: ...'."""
    if novo.suffix.lower() in (".png", ".jpg", ".svg", ".pdf"):
        return "EXISTE (imagem)"
    a = normalizar_texto(novo.read_text(encoding="utf-8", errors="replace"), pasta)
    b = ref.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    if a == b:
        return "IDÊNTICO"
    try:
        if novo.suffix == ".json":
            if numeros_iguais(json.loads(a), json.loads(b)):
                return f"IGUAL (dif. < {TOL:g})"
        elif novo.suffix == ".csv":
            if numeros_iguais(_csv_para_lista(a), _csv_para_lista(b)):
                return f"IGUAL (dif. < {TOL:g})"
    except Exception:
        pass
    la, lb = a.splitlines(), b.splitlines()
    for i, (x, y) in enumerate(zip(la, lb)):
        if x != y:
            return f"DIFERENTE na linha {i + 1}:\n          novo: {x.strip()[:110]}\n          ref.: {y.strip()[:110]}"
    return f"DIFERENTE: {len(la)} linhas contra {len(lb)} na referência"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so-dados", action="store_true", help="só confere os hashes dos dados")
    ap.add_argument("--etapas", nargs="*", help="só estas etapas (ex.: E03 E27)")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--paralelo", type=int, default=max(1, min(4, (os.cpu_count() or 2) - 1)),
                    help="quantas etapas ao mesmo tempo (padrão: núcleos − 1, no máximo 4)")
    ap.add_argument("--gerar-manifesto", metavar="PASTA_DADOS", help="(autores) grava o manifesto")
    ap.add_argument("--gerar-referencia", action="store_true", help="(autores) grava a referência")
    a = ap.parse_args()

    if a.listar:
        for eid, script, args, desc, deps in ETAPAS:
            print(f"{eid}  {desc}\n      python {script} {' '.join(args)}")
        return 0
    if a.gerar_manifesto:
        gerar_manifesto(Path(a.gerar_manifesto).resolve())
        return 0

    linhas = []

    def log(t=""):
        print(t, flush=True)
        linhas.append(t)

    inicio = datetime.now()
    log("=" * 78)
    log("  VERIFICAÇÃO DO ESTUDO InvestAI — refaz tudo a partir dos dados congelados")
    log("=" * 78)
    log(f"  Início: {inicio:%d/%m/%Y %H:%M}   Máquina: {platform.system()} {platform.release()} "
        f"({platform.machine()})")
    import numpy, pandas, scipy
    log(f"  Python {platform.python_version()} | numpy {numpy.__version__} | pandas {pandas.__version__} "
        f"| scipy {scipy.__version__}")
    log(f"  Pacote de dados: {PACOTE.name}")

    pasta = EXECUCAO / f"{inicio:%Y%m%d_%H%M%S}"
    pasta.mkdir(parents=True)
    log("\n1) DADOS: conferindo a impressão digital (SHA-256) de cada arquivo")
    if not conferir_dados(pasta, log):
        log("\n  PAROU: os dados não são os congelados. Nada foi rodado.")
        RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return 1
    if a.so_dados:
        RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        shutil.rmtree(pasta, ignore_errors=True)
        return 0

    ids = a.etapas or [e[0] for e in ETAPAS]
    for d in [d for eid in ids for d in POR_ID[eid][4]]:
        if d not in ids:
            ids.insert(0, d)
    ids = sorted(set(ids), key=lambda e: [x[0] for x in ETAPAS].index(e))
    montar_pasta(pasta)
    paralelo = 1 if a.gerar_referencia else a.paralelo
    log(f"\n2) RODANDO {len(ids)} etapas (relógio parado em 02/10/2026 12:00; "
        f"{paralelo} por vez)")
    res = executar(ids, pasta, log, paralelo)

    if a.gerar_referencia:
        REFERENCIA.mkdir(exist_ok=True)
        lista = {}
        for eid in ids:
            cod, out, err, s, novos = res[eid]
            if cod != 0:
                log(f"  [ERRO] {eid} saiu com código {cod}:\n{err[-2000:]}")
                return 1
            dest = REFERENCIA / eid
            shutil.rmtree(dest, ignore_errors=True)
            dest.mkdir()
            (dest / "_tela.txt").write_text(tela_filtrada(out, pasta), encoding="utf-8")
            for n in novos:
                arq = pasta / "resultados" / n
                if arq.suffix.lower() in (".png", ".jpg"):
                    (dest / (n + ".existe")).write_text("imagem gerada\n", encoding="utf-8")
                else:
                    (dest / n).write_text(normalizar_texto(arq.read_text(encoding="utf-8", errors="replace"),
                                                           pasta), encoding="utf-8")
            lista[eid] = novos
        (REFERENCIA / "arquivos_por_etapa.json").write_text(json.dumps(lista, indent=1, ensure_ascii=False),
                                                           encoding="utf-8")
        log(f"\nReferência gravada em verificacao/referencia/ ({len(ids)} etapas).")
        RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        return 0

    log("\n3) COMPARANDO com a referência (verificacao/referencia/)")
    placar = {"ok": 0, "dif": 0, "erro": 0}
    for eid in ids:
        cod, out, err, s, novos = res[eid]
        log(f"\n  {eid}  {POR_ID[eid][3]}")
        if cod != 0:
            log(f"      [ERRO] o script parou (código {cod}). Final da mensagem:")
            for ln in err.strip().splitlines()[-6:]:
                log(f"        {ln}")
            placar["erro"] += 1
            continue
        dest = REFERENCIA / eid
        itens = [("_tela.txt", None)] + [(n, pasta / "resultados" / n) for n in novos]
        for nome, arq in itens:
            if nome == "_tela.txt":
                a_ = tela_filtrada(out, pasta)
                b_ = (dest / "_tela.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
                st = "IDÊNTICO" if a_ == b_ else "DIFERENTE"
                if st == "DIFERENTE":
                    for i, (x, y) in enumerate(zip(a_.splitlines(), b_.splitlines())):
                        if x != y:
                            st += f" na linha {i + 1}:\n          novo: {x.strip()[:110]}\n          ref.: {y.strip()[:110]}"
                            break
                rotulo = "(o que o script mostrou na tela)"
            elif arq.suffix.lower() in (".png", ".jpg"):
                st = "EXISTE (imagem)" if arq.exists() else "DIFERENTE: imagem não foi gerada"
                rotulo = nome
            elif not arq.exists():
                st, rotulo = "DIFERENTE: o arquivo não foi gerado", nome
            elif not (dest / nome).exists():
                st, rotulo = "DIFERENTE: arquivo novo, não está na referência", nome
            else:
                st, rotulo = comparar_arquivo(arq, dest / nome, pasta), nome
            bom = not st.startswith("DIFERENTE")
            placar["ok" if bom else "dif"] += 1
            log(f"      {'✔' if bom else '✘'} {rotulo}: {st}")

    fim = datetime.now()
    log("\n" + "=" * 78)
    total = placar["ok"] + placar["dif"]
    log(f"  RESULTADO: {placar['ok']} de {total} saídas conferem com a referência; "
        f"{placar['dif']} diferentes; {placar['erro']} etapas com erro.")
    log(f"  Tempo total: {(fim - inicio).seconds // 60} min. Relatório: verificacao/{RELATORIO.name}")
    if placar["dif"] == 0 and placar["erro"] == 0:
        log("  ==> TUDO REPRODUZIDO: os mesmos dados dão os mesmos resultados nesta máquina.")
    else:
        log("  ==> ATENÇÃO: há diferenças. Veja acima quais arquivos e linhas.")
    log("=" * 78)
    RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return 0 if placar["dif"] == 0 and placar["erro"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
