# -*- coding: utf-8 -*-
"""O método foi testado antes: dados sintéticos, poder do teste e um simulador ao vivo."""
from math import sqrt, tanh

import numpy as np
import streamlit as st
from scipy import stats

from modulos import graficos as G
from modulos import resultados as R
from modulos.graficos import br, p_txt
from modulos.interface import cartao, como_ler, fonte, mostrar, numero

st.markdown("# Antes de medir, testamos o instrumento")
st.markdown(
    "Antes de usar dados reais, o módulo estatístico foi testado com **dados inventados**, em que a "
    "resposta certa era conhecida. É como conferir uma balança com um peso de 1 kg antes de pesar "
    "qualquer coisa: se ela não marca 1 kg, nenhuma pesagem depois vale.")

v = R.validacao_sintetica()
st.markdown("## Validação com 1.000 séries sintéticas")
a, b = st.columns(2, gap="large")
with a:
    cartao("cenário A — o efeito existe", f"{br(v['poder'], 1)}%".replace(",0%", "%"),
           f"das {numero(v['n_sim'])} simulações detectaram o efeito. Correlação medida "
           f"{br(v['r_medido'], 4)} × teórica {br(v['r_teorico'], 4)}.")
with b:
    cartao("cenário B — o efeito não existe", f"{br(v['falso_positivo'], 1)}%",
           f"de falsos positivos, exatamente o nível de significância de 5% "
           f"(limite aceito: {br(v['limite_fp'], 1)}%).")
fonte(f"etapa E01 do verificador ({numero(v['n_sim'])} séries de {v['dias']} dias em cada cenário).")
st.markdown(
    "Os dois números importam. O primeiro mostra que o teste **enxerga** um efeito que existe; o "
    "segundo, que ele **não inventa** efeito onde não há. Um falso positivo de 5% não é defeito: é a "
    "definição do nível de significância. Em 100 testes sem efeito nenhum, cerca de 5 dão "
    "\"significativo\" por puro acaso. É por isso que o estudo corrige os p-valores quando faz "
    "vários testes juntos (correção de Holm) e registra todos os testes, inclusive os nulos.")

st.markdown("## Até onde o teste enxerga")
col_g, col_t = st.columns([1.3, 1], gap="large")
with col_g:
    mostrar(G.curva_poder(R.curva_de_poder()), "poder")
    fonte("etapa E02 do verificador (300 simulações por ponto, 400 dias, α = 5%).")
with col_t:
    st.markdown(
        "**Poder** é a chance de o teste detectar um efeito que existe. Com efeitos grandes, ele "
        "acerta quase sempre; com efeitos muito pequenos, quase nunca.\n\n"
        "Os pontos azuis (medidos por simulação) caem em cima da linha (calculada pela fórmula): "
        "o programa faz a conta certa.\n\n"
        "Por isso cada teste do estudo declara o seu **menor efeito detectável**: um resultado nulo "
        "quer dizer \"não há efeito *maior que isso*\", e não \"não há efeito nenhum\".")

st.markdown("### Calculadora do menor efeito detectável")
st.markdown("Quanto mais observações, menor o efeito que o teste consegue enxergar com 80% de poder "
            "(equação 11 do relatório).")
NS = {"8 ativos agrupados, diário (4.129)": 4129, "notícias da noite com horário (1.642)": 1642,
      "notícias do pregão com horário (1.155)": 1155, "barras de 1 minuto (470)": 470,
      "um ativo sozinho (≈ 500)": 500, "o mínimo do início do projeto (20)": 20}
escolha = st.selectbox("Escolha uma amostra do estudo, ou ajuste abaixo:", list(NS), index=0)
n = st.slider("Número de observações (n)", 20, 5000, NS[escolha], step=1, key=f"n_{escolha}")
z = 1.959964 + 0.841621
mde = tanh(z / sqrt(n - 3))
c1, c2 = st.columns([1, 2], gap="large")
with c1:
    cartao("menor efeito detectável", f"r ≥ {br(mde)}", f"com n = {numero(n)}, α = 5% e poder de 80%")
    st.latex(r"r_{min} = \tanh\!\left(\frac{z_{0,975} + z_{0,80}}{\sqrt{n-3}}\right)")
    st.markdown(f"= tanh( (1,960 + 0,842) ÷ √{numero(n - 3)} ) = **{br(mde)}**")
with c2:
    mostrar(G.mde_por_n(n), "mde")

# ── Simulador ───────────────────────────────────────────
st.markdown("## Simulador: o teste de permutação na sua frente")
st.markdown(
    "Escolha a força de uma relação **inventada** entre sentimento e retorno e quantos dias de dados "
    "existem. O programa gera os dados, mede a correlação e faz o teste de permutação: embaralha o "
    "sentimento 2.000 vezes, destruindo qualquer relação, e vê com que frequência o acaso produz uma "
    "correlação tão forte quanto a medida.")
s1, s2, s3 = st.columns([1, 1, 1])
with s1:
    r_real = st.slider("Correlação verdadeira (inventada)", 0.0, 0.40, 0.13, 0.01, format="%.2f")
with s2:
    n_sim = st.select_slider("Dias com notícia", [30, 60, 100, 200, 400, 800, 1600, 4000], value=400)
with s3:
    semente = st.number_input("Semente", 0, 9999, 26, help="Mesma semente, mesmos dados: dá para repetir.")

rng = np.random.default_rng(int(semente))
x = rng.standard_normal(n_sim)
y = r_real * x + sqrt(max(1e-9, 1 - r_real ** 2)) * rng.standard_normal(n_sim)
r_obs, p_cla = stats.pearsonr(x, y)
B = 2000
xp = np.tile(x, (B, 1))
rng.permuted(xp, axis=1, out=xp)
xc = xp - xp.mean(axis=1, keepdims=True)
yc = y - y.mean()
nulos = (xc @ yc) / (np.sqrt((xc ** 2).sum(axis=1)) * np.sqrt((yc ** 2).sum()))
p_perm = (np.sum(np.abs(nulos) >= abs(r_obs)) + 1) / (B + 1)

g1, g2 = st.columns([1.1, 1], gap="large")
with g1:
    mostrar(G.permutacao(nulos, r_obs, "dados simulados", p_perm), "sim_hist")
with g2:
    mostrar(G.simulacao(x, y, r_obs), "sim_disp")
veredito = ("**significativo** (p < 0,05): o acaso raramente produz uma correlação assim"
            if p_perm < 0.05 else "**não significativo**: o acaso produz correlações assim com frequência")
st.markdown(f"Correlação medida: **r = {br(r_obs)}** · {p_txt(p_cla, 'p clássico')} · "
            f"{p_txt(p_perm, 'p de permutação')} → {veredito}.")

if st.button("Repetir 500 vezes com estes parâmetros", icon=":material/repeat:"):
    rng2 = np.random.default_rng(int(semente) + 1)
    X = rng2.standard_normal((500, n_sim))
    Y = r_real * X + sqrt(max(1e-9, 1 - r_real ** 2)) * rng2.standard_normal((500, n_sim))
    Xc, Yc = X - X.mean(1, keepdims=True), Y - Y.mean(1, keepdims=True)
    rr = (Xc * Yc).sum(1) / np.sqrt((Xc ** 2).sum(1) * (Yc ** 2).sum(1))
    t = rr * np.sqrt((n_sim - 2) / (1 - rr ** 2))
    pp = 2 * stats.t.sf(np.abs(t), n_sim - 2)
    taxa = (pp < 0.05).mean() * 100
    zz = np.arctanh(r_real) * sqrt(n_sim - 3)
    teor = (stats.norm.sf(1.959964 - zz) + stats.norm.cdf(-1.959964 - zz)) * 100
    if r_real == 0:
        st.success(f"Sem efeito nenhum, {br(taxa, 1)}% das 500 repetições deram \"significativo\": são os "
                   f"falsos positivos, perto dos 5% esperados.", icon=":material/check_circle:")
    else:
        st.success(f"O teste detectou o efeito em {br(taxa, 1)}% das 500 repetições. A fórmula do poder "
                   f"previa {br(teor, 1)}%.", icon=":material/check_circle:")

como_ler(
    "- O **histograma cinza** mostra as correlações que aparecem quando o sentimento é embaralhado: é o "
    "que o acaso sozinho produz.\n"
    "- A **linha azul** é a correlação dos dados de verdade. Quanto mais longe do monte cinza, menor o p-valor.\n"
    "- Teste com correlação 0: a linha cai dentro do monte quase sempre. Teste com 0,13 e 30 dias: o efeito "
    "existe, mas o teste não enxerga. Com 4.000 dias, enxerga. É por isso que o estudo agrupou os 8 ativos.",
    titulo="Como ler o simulador")
