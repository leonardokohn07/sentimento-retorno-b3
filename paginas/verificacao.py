# -*- coding: utf-8 -*-
"""Verificação e transparência: impressões digitais, verificador, registro de testes, pré-registros."""
import os
import re
import subprocess
import sys
import time

import streamlit as st

from modulos import congelados as C
from modulos import resultados as R
from modulos.interface import cartao, fonte, numero, tabela

RAIZ = R.RAIZ

st.markdown("# Verificação e transparência")
st.markdown(
    "Um resultado científico precisa poder ser conferido por outra pessoa. Esta página mostra as "
    "quatro coisas que permitem isso: os dados congelados, o verificador que refaz tudo, o registro de "
    "todos os testes e os pré-registros escritos antes de cada rodada.")

# ── 1. Impressões digitais ──────────────────────────────
st.markdown("## 1. Os dados não mudaram desde 02/10/2026")
st.markdown(
    "Os 75 arquivos usados no estudo foram congelados, e a **impressão digital SHA-256** de cada um foi "
    "publicada no repositório. A impressão digital é uma sequência de 64 caracteres calculada a partir de "
    "todos os bytes do arquivo: mudar um único número numa planilha muda a impressão digital inteira. "
    "É como o lacre de um envelope.")
if not C.ZIP.exists():
    st.info("O pacote de dados congelados não está neste computador, então a conferência não pode ser "
            "feita aqui. O manifesto com as 75 impressões digitais está em "
            "verificacao/manifesto_dados_congelados_2026-10-02.sha256.", icon=":material/folder_off:")
elif st.button("Conferir as 75 impressões digitais agora", type="primary", icon=":material/fingerprint:"):
    barra = st.progress(0.0)
    res = C.conferir_impressoes_digitais(lambda fr, rel: barra.progress(fr, text=rel.replace("dados/", "")))
    barra.empty()
    if res["ok"] == res["total"]:
        st.success(f"{res['ok']} de {res['total']} arquivos com a impressão digital certa: os dados são "
                   "exatamente os do estudo.", icon=":material/verified:")
    else:
        st.error(f"{res['ok']} de {res['total']} conferem. Diferentes: {res['diferentes']}; "
                 f"faltando: {res['faltando']}", icon=":material/error:")

# ── 2. Verificador ──────────────────────────────────────
st.markdown("## 2. O verificador refaz a análise inteira")
ver = R.ultima_verificacao()
a, b = st.columns([1, 2], gap="large")
with a:
    cartao("última execução", f"{ver['ok']} de {ver['total']}", f"saídas iguais à referência · {ver['quando']}")
with b:
    st.markdown(
        "O programa `verificacao/verificar_tudo.py` refaz as **32 etapas** da análise a partir dos dados "
        "congelados, sem internet e com o relógio do computador parado em 02/10/2026, e compara cada uma "
        "das 99 saídas com a referência. Já rodou num servidor Linux e no computador Windows dos autores, "
        "com versões diferentes do Python.")
    st.caption(f"{ver['maquina']} · {ver['python']} · {ver['arquivo']}")

if C.ZIP.exists():
    modo = st.radio("Rodar o verificador agora:", ["só as etapas do resultado principal (E03 a E06, ≈ 30 s)",
                                                   "completo, 32 etapas (≈ 2 a 3 min)"], horizontal=True)
    if st.button("Rodar o verificador", icon=":material/play_arrow:"):
        args = [sys.executable, "-u", str(RAIZ / "verificacao" / "verificar_tudo.py")]
        total = 32
        if modo.startswith("só"):
            args += ["--etapas", "E03", "E04", "E05", "E06"]
            total = 4
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        barra = st.progress(0.0, text="Conferindo os dados…")
        tela = st.empty()
        linhas, feitas, t0 = [], 0, time.time()
        proc = subprocess.Popen(args, cwd=RAIZ, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", env=env)
        for linha in proc.stdout:
            linhas.append(linha.rstrip())
            if "terminou em" in linha:
                feitas += 1
                barra.progress(min(feitas / total, 1.0),
                               text=f"{feitas} de {total} etapas · {int(time.time() - t0)} s")
            tela.code("\n".join(linhas[-18:]), language=None)
        proc.wait()
        barra.empty()
        final = next((l for l in reversed(linhas) if "RESULTADO:" in l), "")
        m = re.search(r"(\d+) de (\d+) saídas conferem.*?(\d+) diferentes.*?(\d+) etapas com erro", final)
        if m and m.group(3) == "0" and m.group(4) == "0":
            st.success(final.strip(), icon=":material/verified:")
        elif final:
            st.warning(final.strip(), icon=":material/warning:")
        else:
            st.error("O verificador terminou sem a linha de resultado. Veja a saída acima.")
        R.ultima_verificacao.cache_clear()

# ── 3. Registro de testes ───────────────────────────────
st.markdown("## 3. Todos os testes, inclusive os que deram nulo")
reg = R.registro_de_testes()
conf = reg[reg["tipo"].str.contains("confirmatório", na=False)]
c1, c2, c3, c4 = st.columns(4)
with c1:
    cartao("resultados registrados", numero(len(reg)), "nenhum teste fica de fora")
with c2:
    cartao("confirmatórios", numero(len(conf)), "classificados assim no registro")
with c3:
    cartao("confirmatórios que rejeitaram H₀", numero(int((conf["decisao"] == "REJEITA H0").sum())), "")
with c4:
    cartao("exploratórios e secundários", numero(len(reg) - len(conf)), "rotulados como tal")
st.markdown(
    "Fazer muitos testes e mostrar só os que deram certo é uma forma de enganar sem mentir (p-hacking). "
    "Por isso cada teste feito está no registro, com o pré-registro que o previu, o tipo (confirmatório, "
    "secundário ou exploratório), o menor efeito detectável e a decisão.")
f1, f2 = st.columns(2)
with f1:
    fases = st.multiselect("Fase:", sorted(reg["fase"].dropna().unique()), placeholder="todas as fases")
with f2:
    so_rej = st.toggle("Só os que rejeitaram H₀")
v = reg.copy()
if fases:
    v = v[v["fase"].isin(fases)]
if so_rej:
    v = v[v["decisao"] == "REJEITA H0"]
tabela(v[["etapa", "tipo", "teste", "pergunta", "medida", "r", "p", "p_holm", "n",
          "menor_r_detectavel", "decisao"]].rename(columns={"menor_r_detectavel": "menor r detectável",
                                                             "p_holm": "p de Holm", "decisao": "decisão"}),
       {"r": 4, "p": 4, "p de Holm": 4, "menor r detectável": 3, "n": 0}, height=360,
       column_config={"etapa": st.column_config.TextColumn(width="small"),
                      "tipo": st.column_config.TextColumn(width="medium"),
                      "pergunta": st.column_config.TextColumn(width="large")})
fonte("verificacao/registro_de_testes.csv.")
if R.COMPLEMENTO_D4.exists():
    st.caption("Depois do relatório, foi calculado o ponto D+4 que faltava na curva de defasagem (9 correlações, "
               "todas não significativas). Ele não entra no registro acima, que é o da referência congelada; "
               "está em resultados/curva_defasagem_complemento_D+4.csv, marcado como complemento descritivo.")

# ── 4. Pré-registros ────────────────────────────────────
st.markdown("## 4. As regras foram escritas antes")
pr = R.pre_registros()
st.markdown(
    f"A partir de 28/09/2026, cada rodada de testes teve um documento datado, gravado no repositório git "
    f"**antes** da execução: {int((~pr['adendo']).sum())} pré-registros e {int(pr['adendo'].sum())} adendos. "
    f"Quando o plano mudou, a mudança foi declarada num adendo.")
for _, l in pr.iterrows():
    with st.expander(f"{l['data']} · {l['documento']}"):
        st.markdown(l["arquivo"].read_text(encoding="utf-8"))

# ── 5. Coleta prospectiva ───────────────────────────────
st.markdown("## 5. O próximo passo já está rodando")
cp = R.coleta_prospectiva()
st.markdown(
    "Um resultado só é realmente testado com dados que **ainda não existiam** quando a conclusão foi "
    f"escrita. Desde {cp['inicio']}, uma coleta diária automática guarda notícias com horário e preços "
    f"minuto a minuto. A regra de parada foi fixada antes: **{numero(cp['meta'])} eventos ou {cp['prazo']}**, "
    "o que vier primeiro. Só então os testes confirmatórios serão calculados.")
if cp["existe"] and cp["eventos"] is not None:
    st.progress(min(cp["eventos"] / cp["meta"], 1.0),
                text=f"{numero(cp['eventos'])} de {numero(cp['meta'])} eventos confirmatórios "
                     f"(último registro: {cp['ultima']})")
else:
    st.caption("O registro da coleta diária não está neste computador.")

# ── 6. Limitações e IA ──────────────────────────────────
st.markdown("## 6. O que o estudo não consegue afirmar")
st.markdown(
    "- **Poder:** efeitos menores que o limite de detecção de cada teste não podem ser descartados.\n"
    "- **Horário:** o casamento de horários pelos sites tem cerca de 6% de erro, e o horário do agregador "
    "pode atrasar em notícias antigas; esse tipo de erro enfraquece as correlações, em vez de criá-las.\n"
    "- **Medida:** o léxico não reconhece ironia, lê alguns termos fora de contexto e não encontrou "
    "nenhum termo em 62,6% das manchetes.\n"
    "- **Resolução:** não há preços abaixo de 1 minuto.\n"
    "- **Fonte:** as notícias vêm de um único agregador, e só a manchete é analisada.\n"
    "- **Desenho:** o estudo é observacional: mostra a ordem no tempo, não prova causa.")
with st.expander("Uso de inteligência artificial"):
    st.markdown(
        "Os autores usaram ferramentas de IA generativa, principalmente o assistente Claude (Anthropic), na "
        "escrita de código e de textos e como anotador preliminar na validação do léxico. Os números vêm dos "
        "scripts de análise e podem ser refeitos pelo verificador desta página. A declaração completa está "
        "no apêndice B do relatório.")
