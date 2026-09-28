"""
dashboard.py
------------
InvestAI — sentimento de noticias x retorno de acoes da B3.

Aplicacao de UMA tela: o estudo estatistico da hipotese. Mostra a amostra,
o resultado por defasagem (mesmo pregao e dia seguinte), o controle negativo
por permutacao e as limitacoes.

Em 28/09/2026 as abas de analise de risco de carteira (visao geral, risco,
sentimento da carteira, otimizacao de Markowitz e alertas) foram removidas:
elas nao faziam parte do objeto do estudo e varias decisoes ali — o score
60/40, principalmente — nao tinham referencia que as sustentasse. O codigo
delas continua no historico do git, na tag feicit-2026.

Este trabalho e academico. Nao e recomendacao de investimento.

Execute com: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modulos.coleta.precos import (
    baixar_dados, calcular_retornos, baixar_ibovespa, CARTEIRA_ESTUDO,
)
from modulos.coleta.noticias import coletar_historico, ajustar_data_pregao
from modulos.analise.sentimento import AnalisadorV2
from modulos.analise.hipotese import (
    montar_serie_diaria, testar_correlacao_defasada,
    testar_diferenca_medias, regressao_sentimento_retorno,
    event_study, MIN_OBSERVACOES,
)

st.set_page_config(
    page_title="InvestAI — Sentimento x Retorno (B3)",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Modelo NLP: implementado, porem desativado ───
# A classe AnalisadorV2 suporta combinar o lexico com um DistilBERT
# multilingue. A opcao esta desligada porque o PyTorch nao carregava na
# maquina em que o estudo foi rodado (WinError 1114 ao abrir c10.dll), e
# trocar o instrumento no meio do estudo invalidaria a validacao ja feita.
# Todos os resultados apresentados usam somente o lexico.
usar_modelo_ml = False


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_precos_estudo(tickers, data_inicio_txt):
    """
    Baixa precos cobrindo o periodo do estudo.

    O periodo vem do proprio estudo, e nao de um seletor de interface: assim
    nenhuma escolha de tela descarta silenciosamente dias ja coletados.
    """
    inicio = pd.to_datetime(data_inicio_txt)
    anos = (pd.Timestamp.now() - inicio).days / 365.25
    for limite, rotulo in [(1, "1y"), (2, "2y"), (5, "5y"), (10, "10y")]:
        if anos <= limite:
            periodo_necessario = rotulo
            break
    else:
        periodo_necessario = "max"

    dados_est = baixar_dados(tickers, periodo=periodo_necessario)
    return (
        calcular_retornos(dados_est),
        baixar_ibovespa(periodo=periodo_necessario),
        periodo_necessario,
    )


st.title("🔬 InvestAI — sentimento de notícias × retorno de ações")
st.caption("Estudo estatístico · B3 · trabalho acadêmico, não é recomendação de investimento.")

st.markdown("""
Este estudo testa a **hipótese central do trabalho** com dados históricos:

| | |
|---|---|
| **H₀** (nula) | O sentimento das notícias **não** influencia o retorno das ações |
| **H₁** (alternativa) | O sentimento das notícias **influencia** o retorno das ações |

Em estatística não se "prova" H₁ diretamente — tenta-se **rejeitar H₀**.
Se a chance de o resultado ter surgido por acaso (*p-valor*) for menor
que 0,05, rejeitamos H₀.
""")

st.info(
    "⏱️ **Atenção:** o estudo coleta **meses ou anos** de notícias "
    "históricas. A primeira execução leva de 10 a 20 minutos; depois "
    "disso os dados ficam em cache e a análise é instantânea."
)

from modulos.caminhos import ARQ_NOTICIAS as ARQ_CACHE

# ── Controles do estudo ──
col_a, col_b, col_c = st.columns(3)
with col_a:
    data_ini_est = st.date_input(
        "Início do estudo",
        value=pd.to_datetime("2024-01-01"),
        key="hip_ini",
    )
with col_b:
    data_fim_est = st.date_input(
        "Fim do estudo",
        value=pd.to_datetime("today"),
        key="hip_fim",
    )
with col_c:
    lag_escolhido = st.selectbox(
        "Defasagem principal",
        [0, 1, 2, 3],
        index=1,
        format_func=lambda x: f"D+{x} (reação em {x} dia(s))",
        help="D+1 costuma ser o mais relevante: boa parte das notícias "
             "sai fora do horário de pregão.",
        key="hip_lag",
    )

cache_existe = ARQ_CACHE.exists()

col_bt1, col_bt2 = st.columns([1, 1])
with col_bt1:
    rodar_estudo = st.button(
        "🚀 Coletar histórico e rodar estudo",
        type="primary",
        use_container_width=True,
        key="btn_estudo",
    )
with col_bt2:
    usar_cache = st.button(
        "📂 Usar dados já coletados",
        use_container_width=True,
        disabled=not cache_existe,
        key="btn_cache",
    )

# ── Painel de status do cache ──
if cache_existe:
    try:
        _prev = pd.read_csv(ARQ_CACHE, parse_dates=["data"])
        _mod = datetime.fromtimestamp(ARQ_CACHE.stat().st_mtime)
        _tem_sent = "score_polaridade" in _prev.columns

        with st.container(border=True):
            st.markdown("**📂 Dados já carregados**")
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Notícias", f"{len(_prev):,}".replace(",", "."))
            s2.metric("Ativos", _prev["ticker"].nunique())
            s3.metric(
                "Período",
                f"{_prev['data'].min():%m/%y} – {_prev['data'].max():%m/%y}",
            )
            s4.metric("Sentimento", "✅ pronto" if _tem_sent else "⏳ falta")
            st.caption(
                f"Coletado em {_mod:%d/%m/%Y às %H:%M} · `dados/{ARQ_CACHE.name}`"
            )
    except Exception:
        st.caption(f"✅ Cache encontrado: `dados/{ARQ_CACHE.name}`")
else:
    st.caption(
        "ℹ️ Nenhum dado histórico coletado ainda. "
        "Use o botão azul para começar."
    )

# ── Coleta / carregamento ──
# Guardamos o resultado em session_state: sem isso, trocar o ativo no
# seletor abaixo apagaria todo o estudo e seria preciso coletar tudo
# de novo (o Streamlit reexecuta o script inteiro a cada interação).
noticias_hist = st.session_state.get("noticias_historicas")

if rodar_estudo:
    # ── Painel de progresso ao vivo ──
    painel = st.container()
    with painel:
        st.markdown("##### ⏳ Coleta em andamento")
        barra = st.progress(0.0)
        linha_status = st.empty()   # ex: "Ativo 2/5 · PETR4.SA · 03/2024"
        col_m1, col_m2, col_m3 = st.columns(3)
        m_etapa = col_m1.empty()
        m_noticias = col_m2.empty()
        m_tempo = col_m3.empty()

    def _formatar_tempo(segundos: float) -> str:
        """Converte segundos em '3 min 20 s' ou '45 s'."""
        segundos = max(0, int(segundos))
        if segundos < 60:
            return f"{segundos} s"
        return f"{segundos // 60} min {segundos % 60:02d} s"

    def _ao_coletar(p: dict):
        """Chamado pelo coletor a cada mês concluído."""
        # A coleta ocupa 85% da barra; os 15% finais são o sentimento.
        barra.progress(p["fracao"] * 0.85)
        linha_status.markdown(
            f"📡 Ativo **{p['ticker_atual']}/{p['ticker_total']}** · "
            f"`{p['ticker']}` · período **{p['periodo']}**"
        )
        m_etapa.metric("Etapa", f"{p['passo']}/{p['passo_total']}")
        m_noticias.metric("Notícias", p["noticias_ate_agora"])
        m_tempo.metric(
            "Tempo restante",
            _formatar_tempo(p["segundos_restantes"]),
            help="Estimativa baseada na média até agora. "
                 "Vai ficando mais precisa conforme avança.",
        )

    def _ao_analisar(p: dict):
        """Chamado pelo analisador de sentimento."""
        barra.progress(0.85 + p["fracao"] * 0.15)
        linha_status.markdown(
            f"🤖 Calculando sentimento · **{p['atual']}/{p['total']}** notícias"
        )

    try:
        # janela_dias=15 (era 30): com 30 dias, medimos que 21% das
        # janelas batiam no teto de ~100 resultados do Google News e
        # outras 24% ficavam na zona de risco — ou seja, notícias
        # existiam e não eram entregues, justamente nos meses de maior
        # movimento. Janelas menores cabem abaixo do teto.
        # pausa_seg=1.5 (era 1.0): mais janelas = mais requisições;
        # a pausa maior reduz o risco de bloqueio pelo Google.
        noticias_hist = coletar_historico(
            tickers=CARTEIRA_ESTUDO,
            data_inicio=str(data_ini_est),
            data_fim=str(data_fim_est),
            janela_dias=15,
            pausa_seg=1.5,
            verbose=False,
            callback_progresso=_ao_coletar,
        )

        if not noticias_hist.empty:
            noticias_hist = ajustar_data_pregao(noticias_hist)
            analisador_v2 = AnalisadorV2(usar_ml=usar_modelo_ml)
            noticias_hist = analisador_v2.analisar_batch(
                noticias_hist, callback_progresso=_ao_analisar
            )
            noticias_hist.to_csv(ARQ_CACHE, index=False)
            st.session_state["noticias_historicas"] = noticias_hist

        barra.progress(1.0)
        linha_status.markdown("✅ **Coleta concluída!**")
        painel.empty()   # limpa o painel para dar lugar aos resultados

    except Exception as e:
        painel.empty()
        st.error(f"Erro na coleta: {e}")

elif usar_cache and cache_existe:
    noticias_hist = pd.read_csv(
        ARQ_CACHE, parse_dates=["data", "data_pregao"]
    )
    st.session_state["noticias_historicas"] = noticias_hist

# ── Resultados ──
tem_resultados = False       # só vira True se houver dados suficientes
resultados_ativos = {}

if noticias_hist is None:
    st.markdown("---")
    st.info("👆 Escolha uma das opções acima para começar o estudo.")

elif noticias_hist.empty:
    st.error(
        "Nenhuma notícia coletada. Possíveis causas: período muito curto, "
        "sem conexão, ou bloqueio temporário do Google News "
        "(aumente `pausa_seg` no news_collector.py)."
    )

else:
    st.success(
        f"📊 {len(noticias_hist)} notícias históricas | "
        f"{noticias_hist['data'].min():%d/%m/%Y} a "
        f"{noticias_hist['data'].max():%d/%m/%Y}"
    )

    # ── A amostra vem dos dados, não da interface ──
    # Os ativos analisados são os que EXISTEM no arquivo de notícias.
    # Nenhuma escolha de tela entra na definição da amostra: é isso que
    # sustenta a conclusão estatística do trabalho.
    tickers_estudo = sorted(noticias_hist["ticker"].dropna().unique())

    with st.spinner("📈 Alinhando preços ao período do estudo..."):
        retornos_est, ibov_est, _per = carregar_precos_estudo(
            tuple(tickers_estudo), str(data_ini_est)
        )
    st.caption(
        f"**{len(tickers_estudo)} ativos** no estudo, preços com histórico "
        f"`{_per}`. A amostra é definida pelos dados coletados, não por "
        f"escolhas de interface."
    )

    # Ativos que realmente têm dados suficientes
    resultados_ativos = {}
    for tk in tickers_estudo:
        serie = montar_serie_diaria(noticias_hist, retornos_est, tk)
        # Limite vindo da análise de poder (ver hipotese.MIN_OBSERVACOES)
        if not serie.empty and len(serie) >= MIN_OBSERVACOES:
            resultados_ativos[tk] = serie

    # ── Quem ficou de fora, e por quê ──
    # Antes, um ativo sem série de preços sumia da tabela em silêncio e
    # ainda mudava o denominador do resultado. Agora ele é declarado.
    fora = []
    for tk in tickers_estudo:
        if tk in resultados_ativos:
            continue
        if tk not in retornos_est.columns:
            fora.append(f"`{tk}`: sem série de preços (Yahoo não respondeu)")
        else:
            _n = len(montar_serie_diaria(noticias_hist, retornos_est, tk))
            fora.append(
                f"`{tk}`: {_n} dias com notícia e pregão "
                f"(mínimo {MIN_OBSERVACOES} pela análise de poder)"
            )
    if fora:
        st.warning("**Fora desta rodada** — " + " · ".join(fora))

    try:
        from modulos.coleta.precos import STATUS_PRECOS
        _do_cache = [t for t, v in STATUS_PRECOS.items() if v == "cache"]
        if _do_cache:
            st.info(
                "Preços lidos da cópia local da última coleta (o Yahoo não "
                "respondeu agora): " + ", ".join(_do_cache)
            )
    except Exception:
        pass

    if not resultados_ativos:
        # Não usar st.stop() aqui: ele encerraria a página INTEIRA,
        # apagando também as abas 1 a 5. Uma flag local resolve.
        st.warning(
            f"Nenhum ativo com dados suficientes (mínimo {MIN_OBSERVACOES} "
            f"dias com notícia — abaixo disso o teste tem menos de 80% de "
            f"poder estatístico). Amplie o período do estudo."
        )
        tem_resultados = False
    else:
        tem_resultados = True

if noticias_hist is not None and not noticias_hist.empty and tem_resultados:

    # ══ Painel consolidado ══
    st.markdown("---")
    st.markdown("### 📌 Resultado Consolidado")

    significativos, p_valores, linhas_tabela = 0, [], []

    for tk, serie in resultados_ativos.items():
        reg = regressao_sentimento_retorno(serie, lag=lag_escolhido)
        if "erro" in reg:
            continue
        sig = reg["significativo_5pct"]
        if sig:
            significativos += 1
            p_valores.append(reg["p_valor"])

        linhas_tabela.append({
            "Ativo": tk,
            "Dias c/ notícia": len(serie),
            "Correlação (r)": reg["r"],
            "R²": reg["r2"],
            "% explicado": f"{reg['variancia_explicada_pct']}%",
            "p-valor": reg["p_valor"],
            "H₀ rejeitada": "✅ SIM" if sig else "❌ não",
        })

    total_ativos = len(linhas_tabela)

    c1, c2, c3 = st.columns(3)
    c1.metric("Ativos analisados", total_ativos)
    c2.metric("Com relação significativa", f"{significativos}/{total_ativos}")
    c3.metric(
        "p-valor médio",
        f"{np.mean(p_valores):.4f}" if p_valores else "—",
    )

    # Veredito redigido
    proporcao = significativos / total_ativos if total_ativos else 0
    if proporcao >= 0.6:
        st.success(
            f"**H₀ REJEITADA** em {significativos} de {total_ativos} ativos "
            f"(p < 0,05). Há evidência estatística consistente de que o "
            f"sentimento das notícias influencia o retorno das ações."
        )
    elif proporcao >= 0.3:
        st.warning(
            f"**Evidência PARCIAL**: H₀ rejeitada em {significativos} de "
            f"{total_ativos} ativos. O efeito existe em parte da amostra, "
            f"sugerindo que a influência varia conforme o ativo e sua "
            f"cobertura na mídia."
        )
    else:
        st.info(
            f"**H₀ NÃO rejeitada** na maioria dos casos ({significativos} de "
            f"{total_ativos}). Não houve evidência suficiente no período. "
            f"Este é um resultado válido e deve ser reportado com honestidade."
        )

    st.dataframe(
        pd.DataFrame(linhas_tabela),
        use_container_width=True,
        hide_index=True,
    )

    # ══ Diagnóstico da qualidade dos dados ══
    with st.expander("🩺 Diagnóstico — a medição está funcionando?", expanded=(significativos == 0)):
        st.markdown("""
        Antes de concluir qualquer coisa, é preciso verificar se o
        **instrumento de medição** está funcionando. Se o sentimento
        calculado for quase todo neutro, não há variação para
        correlacionar — e o resultado nulo seria falha da medição,
        não ausência do fenômeno.
        """)

        sc = noticias_hist["score_polaridade"]
        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Desvio-padrão", f"{sc.std():.3f}",
                  help="Abaixo de 0,15 indica pouca variação — sinal fraco.")
        d2.metric("Média", f"{sc.mean():+.3f}",
                  help="Muito longe de zero indica viés do léxico.")
        pct_neutro = (sc.abs() < 0.15).mean() * 100
        d3.metric("Neutros", f"{pct_neutro:.0f}%",
                  help="Acima de 70% indica que o léxico capta pouca coisa.")
        d4.metric("Notícias/dia", f"{len(noticias_hist) / max(1, noticias_hist['data_pregao'].nunique()):.1f}")

        # Balanço entre os grupos que o teste t vai comparar
        n_pos = int((sc > 0.2).sum())
        n_neg = int((sc < -0.2).sum())
        razao = n_pos / max(1, n_neg)
        st.caption(
            f"Grupos que o teste t compara: **{n_pos}** notícias positivas "
            f"vs **{n_neg}** negativas (razão {razao:.1f}:1). "
            "Muito desbalanceado — acima de 3:1 — reduz o poder do teste."
        )

        # Diagnóstico automático
        problemas = []
        if sc.std() < 0.15:
            problemas.append(
                "**Variação baixa** — o léxico está classificando quase "
                "tudo perto de zero. Amplie o dicionário em "
                "`modulos/analise/sentimento.py`."
            )
        if pct_neutro > 70:
            problemas.append(
                f"**{pct_neutro:.0f}% das notícias saíram neutras** — o léxico "
                "não está reconhecendo os termos usados nos títulos."
            )
        if abs(sc.mean()) > 0.12:
            problemas.append(
                f"**Viés sistemático** — a média está em {sc.mean():+.3f}, "
                "longe de zero. Isso indica que o léxico pende para um "
                "lado. Consequência prática: o grupo minoritário fica "
                "pequeno e o teste t perde poder de detecção."
            )

        if problemas:
            st.warning("**Pontos de atenção encontrados:**\n\n" +
                       "\n\n".join(f"- {p}" for p in problemas))
        else:
            st.success(
                "✅ A medição parece saudável: há variação suficiente no "
                "sentimento. Um resultado não-significativo aqui é um "
                "achado legítimo, não falha do instrumento."
            )

        # Histograma da distribuição
        fig_hist = go.Figure(go.Histogram(
            x=sc, nbinsx=40, marker_color="#2E75B6",
        ))
        fig_hist.update_layout(
            height=260,
            xaxis_title="Score de sentimento",
            yaxis_title="Nº de notícias",
            margin=dict(t=20, b=40),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # ── Cobertura do léxico POR ATIVO ──
        # O diagnóstico acima é global: se um ativo estiver mal coberto e
        # quatro bem, a média esconde o problema. A quebra por ativo revela
        # se o vocabulário de algum setor não está representado no léxico.
        st.markdown("**Cobertura do léxico por ativo:**")
        linhas_cob = []
        for tk_c, g in noticias_hist.groupby("ticker"):
            s_c = g["score_polaridade"].dropna()
            if s_c.empty:
                continue
            pct_n = float((s_c.abs() < 0.15).mean() * 100)
            if pct_n > 80:
                sit = "🔴 ruim"
            elif pct_n > 70:
                sit = "🟡 atenção"
            else:
                sit = "🟢 ok"
            linhas_cob.append({
                "Ativo": tk_c,
                "Notícias": len(s_c),
                "% neutro": round(pct_n, 1),
                "Desvio-padrão": round(float(s_c.std()), 3),
                "Média": round(float(s_c.mean()), 3),
                "Cobertura": sit,
            })

        if linhas_cob:
            df_cob = pd.DataFrame(linhas_cob).sort_values(
                "% neutro", ascending=False
            )
            st.dataframe(df_cob, use_container_width=True, hide_index=True)

            ruins = [l["Ativo"] for l in linhas_cob if l["% neutro"] > 70]
            if ruins:
                st.warning(
                    f"**Cobertura fraca em: {', '.join(ruins)}.** Acima de "
                    f"70% de notícias neutras, o léxico está reconhecendo "
                    f"poucos termos do vocabulário desses ativos — "
                    f"provavelmente jargão setorial ausente do dicionário. "
                    f"Isso **reduz o poder do teste** nesses casos e deve "
                    f"ser reportado como limitação, não corrigido depois de "
                    f"ver os resultados (ajustar o instrumento de medida "
                    f"após observar o resultado introduz viés)."
                )
            else:
                st.success(
                    "✅ Cobertura homogênea entre os ativos: o léxico se "
                    "comporta de forma parecida em todos os setores da "
                    "amostra."
                )

        st.markdown("---")

        # Amostra para auditoria manual
        st.markdown("**Amostra para conferência manual:**")
        amostra = noticias_hist.sample(
            min(8, len(noticias_hist)), random_state=1
        )[["titulo", "score_polaridade", "classificacao"]]
        st.dataframe(amostra, use_container_width=True, hide_index=True)
        st.caption(
            "Leia os títulos e confira se o score faz sentido. "
            "Se não fizer, o problema está no léxico — e isso é "
            "corrigível."
        )


    # ══ Análise por ativo ══
    st.markdown("---")
    st.markdown("### 🔍 Análise Detalhada por Ativo")

    ativo_sel = st.selectbox(
        "Escolha o ativo",
        list(resultados_ativos.keys()),
        key="hip_ativo",
    )
    serie_sel = resultados_ativos[ativo_sel]

    # --- Correlação por defasagem ---
    st.markdown("#### 1️⃣ Correlação por Defasagem")
    st.caption(
        "Mede a relação entre o sentimento do dia D e o retorno em D+lag. "
        "Barras verdes indicam correlação estatisticamente significativa."
    )

    corr = testar_correlacao_defasada(serie_sel, lags=[0, 1, 2, 3, 5])

    if not corr.empty:
        cores = [
            "#1D9E75" if s else "#94A3B8"
            for s in corr["significativo_5pct"]
        ]
        fig_lag = go.Figure(go.Bar(
            x=[f"D+{int(l)}" for l in corr["lag_dias"]],
            y=corr["pearson_r"],
            marker_color=cores,
            text=[f"p={p:.3f}" for p in corr["pearson_p"]],
            textposition="outside",
        ))
        fig_lag.update_layout(
            yaxis_title="Correlação de Pearson (r)",
            xaxis_title="Defasagem",
            height=340,
            showlegend=False,
        )
        fig_lag.add_hline(y=0, line_dash="dot", line_color="gray")
        st.plotly_chart(fig_lag, use_container_width=True)

    # --- Dispersão ---
    st.markdown("#### 2️⃣ Dispersão: Sentimento × Retorno")

    s_plot = serie_sel.sort_values("data").copy()
    s_plot["retorno_lag"] = s_plot["retorno"].shift(-lag_escolhido)
    s_plot = s_plot.dropna(subset=["sentimento", "retorno_lag"])

    if len(s_plot) > 2:
        # Reta de tendência calculada aqui, com numpy.
        # (O trendline="ols" do Plotly exigiria a biblioteca statsmodels,
        #  que não faz parte das dependências do projeto.)
        b_lin, a_lin = np.polyfit(
            s_plot["sentimento"], s_plot["retorno_lag"] * 100, 1
        )
        x_linha = np.linspace(
            s_plot["sentimento"].min(), s_plot["sentimento"].max(), 60
        )
        y_linha = a_lin + b_lin * x_linha

        fig_disp = go.Figure()
        fig_disp.add_trace(go.Scatter(
            x=s_plot["sentimento"],
            y=s_plot["retorno_lag"] * 100,
            mode="markers",
            marker=dict(size=7, color="#2E75B6", opacity=0.55),
            name="Dias observados",
            hovertemplate=(
                "Sentimento: %{x:.3f}<br>"
                f"Retorno D+{lag_escolhido}: " + "%{y:.2f}%<extra></extra>"
            ),
        ))
        fig_disp.add_trace(go.Scatter(
            x=x_linha, y=y_linha,
            mode="lines",
            line=dict(color="#E87722", width=2.5),
            name=f"Tendência (b = {b_lin:+.3f})",
        ))
        fig_disp.update_layout(
            height=400,
            xaxis_title="Sentimento da notícia (dia D)",
            yaxis_title=f"Retorno em D+{lag_escolhido} (%)",
            legend=dict(orientation="h", y=1.1),
        )
        fig_disp.add_hline(y=0, line_dash="dot", line_color="gray")
        fig_disp.add_vline(x=0, line_dash="dot", line_color="gray")
        st.plotly_chart(fig_disp, use_container_width=True)

    # --- Teste t ---
    st.markdown("#### 3️⃣ Teste t — Notícia Boa vs Notícia Ruim")
    st.caption(
        "Compara o retorno médio após notícias positivas com o retorno "
        "após notícias negativas."
    )

    tm = testar_diferenca_medias(serie_sel, lag=lag_escolhido, limiar=0.2)

    if "erro" in tm:
        st.warning(f"⚠️ {tm['erro']}")
    else:
        t1, t2, t3, t4 = st.columns(4)
        t1.metric(
            "Após notícia positiva",
            f"{tm['retorno_medio_apos_noticia_positiva_pct']:+.3f}%",
        )
        t1.caption(f"{tm['n_positivo']} ocorrências")
        t2.metric(
            "Após notícia negativa",
            f"{tm['retorno_medio_apos_noticia_negativa_pct']:+.3f}%",
        )
        t2.caption(f"{tm['n_negativo']} ocorrências")
        t3.metric("Diferença", f"{tm['diferenca_pct']:+.3f} p.p.")
        t3.caption(f"p = {tm['p_valor']:.4f}")

        # O tamanho do efeito é exibido SEMPRE, e não apenas quando o
        # resultado é significativo. Sem ele, um p-valor alto não deixa
        # distinguir "não há efeito" de "há efeito, mas a amostra é
        # pequena demais para confirmá-lo".
        t4.metric("Tamanho do efeito", f"d = {tm['d_cohen']:+.3f}")
        t4.caption(tm["magnitude_efeito"])

        if tm["significativo_5pct"]:
            st.success(
                f"✅ Diferença **estatisticamente significativa** "
                f"(p = {tm['p_valor']:.4f} < 0,05). O efeito é **real**. "
                f"E o d de Cohen de {tm['d_cohen']:.3f} indica que sua "
                f"magnitude é **{tm['magnitude_efeito'].lower()}**."
            )
        else:
            st.info(
                f"Diferença **não significativa** (p = {tm['p_valor']:.4f} "
                f"≥ 0,05): não é possível descartar o acaso. O tamanho do "
                f"efeito observado (d = {tm['d_cohen']:.3f}, "
                f"**{tm['magnitude_efeito'].lower()}**) ajuda a interpretar: "
                f"um efeito grande sem significância sugere amostra "
                f"insuficiente; um efeito desprezível sugere ausência real "
                f"de relação."
            )

        with st.expander("Como ler estes dois números"):
            st.markdown("""
| | Pergunta que responde | Regra |
|---|---|---|
| **p-valor** | O resultado é real ou foi acaso? | < 0,05 → é real |
| **d de Cohen** | O efeito é grande ou é migalha? | < 0,2 desprezível · 0,2–0,5 pequeno · 0,5–0,8 médio · > 0,8 grande |

São perguntas **independentes**. Com amostra grande, uma diferença
irrelevante pode ficar significativa — por isso os dois são reportados.
O p-valor sozinho diria que o efeito existe, sem dizer se ele importa.
            """)

    # --- Event Study ---
    st.markdown("#### 4️⃣ Event Study — Retorno Anormal (CAR)")
    st.caption(
        "Desconta o movimento do Ibovespa para isolar o efeito da notícia. "
        "Se a ação subiu porque o mercado inteiro subiu, isso **não** é "
        "efeito da notícia."
    )

    if ativo_sel in retornos_est.columns:
        try:
            ev = event_study(
                noticias_hist, retornos_est[ativo_sel], ibov_est, ativo_sel
            )
            if "erro" in ev:
                st.warning(f"⚠️ {ev['erro']}")
            else:
                e1, e2, e3 = st.columns(3)
                e1.metric("Beta estimado", f"{ev['beta_estimado']:.3f}")
                e2.metric("R² do modelo", f"{ev['r2_modelo_mercado']:.3f}")
                e3.metric(
                    "Eventos analisados",
                    ev["n_eventos_positivos"] + ev["n_eventos_negativos"],
                )

                cp, cn = st.columns(2)
                with cp:
                    if "car_medio_positivo_pct" in ev:
                        st.metric(
                            "CAR após notícia positiva",
                            f"{ev['car_medio_positivo_pct']:+.3f}%",
                            delta=f"p = {ev['p_valor_positivo']:.4f}",
                        )
                        if ev.get("significativo_positivo"):
                            st.success("✅ Significativo")
                    else:
                        st.caption("Eventos positivos insuficientes (mín. 5)")
                with cn:
                    if "car_medio_negativo_pct" in ev:
                        st.metric(
                            "CAR após notícia negativa",
                            f"{ev['car_medio_negativo_pct']:+.3f}%",
                            delta=f"p = {ev['p_valor_negativo']:.4f}",
                        )
                        if ev.get("significativo_negativo"):
                            st.success("✅ Significativo")
                    else:
                        st.caption("Eventos negativos insuficientes (mín. 5)")
        except Exception as e:
            st.warning(f"Event Study indisponível: {e}")

    # --- Casos concretos ---
    st.markdown("---")
    st.markdown("#### 📰 Casos Concretos — Notícia × Movimento do Preço")

    noti_ativo = noticias_hist[
        (noticias_hist["ticker"] == ativo_sel)
        & (noticias_hist["score_polaridade"].abs() >= 0.35)
    ].copy()

    if noti_ativo.empty:
        st.info("Nenhuma notícia com sentimento forte para este ativo.")
    else:
        ret_ativo = retornos_est[ativo_sel].copy()
        ret_ativo.index = pd.to_datetime(ret_ativo.index).normalize()
        calendario = ret_ativo.index

        casos = []
        for _, r in noti_ativo.iterrows():
            d = pd.to_datetime(r["data_pregao"]).normalize()
            pos = calendario.searchsorted(d)
            if pos >= len(calendario) - 1:
                continue
            ret_seguinte = float(ret_ativo.iloc[pos + 1]) * 100
            casos.append({
                "Data": calendario[pos].strftime("%d/%m/%Y"),
                "Notícia": str(r["titulo"])[:75],
                "Sentimento": round(float(r["score_polaridade"]), 3),
                f"Retorno D+1 (%)": round(ret_seguinte, 2),
                "Direção": (
                    "✅ acertou"
                    if np.sign(r["score_polaridade"]) == np.sign(ret_seguinte)
                    else "❌ errou"
                ),
            })

        if casos:
            df_casos = pd.DataFrame(casos)
            taxa = (df_casos["Direção"] == "✅ acertou").mean() * 100

            st.metric(
                "Taxa de acerto da direção",
                f"{taxa:.1f}%",
                delta=f"{taxa - 50:+.1f} p.p. vs acaso (50%)",
            )
            st.caption(
                "⚠️ A tabela mostra **acertos e erros**. Apresentar apenas "
                "os acertos seria seleção enviesada — a banca vai perguntar "
                "pelos erros."
            )
            st.dataframe(
                df_casos.sort_values("Data"),
                use_container_width=True,
                hide_index=True,
                height=340,
            )

            st.download_button(
                "⬇️ Baixar casos em CSV (anexo do TCC)",
                df_casos.to_csv(index=False).encode("utf-8-sig"),
                file_name=f"casos_{ativo_sel.replace('.SA','')}.csv",
                mime="text/csv",
            )

    st.markdown("---")
    st.caption(
        "📌 **Nota metodológica:** valores de R² entre 0,01 e 0,10 são o "
        "esperado nesta literatura. O preço de uma ação depende de dezenas "
        "de fatores — o sentimento é apenas um deles. O que valida a "
        "hipótese é o **p-valor**, não a magnitude do R²."
    )


# Rodapé
st.markdown("---")
st.caption(f"InvestAI B3 | Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Dados: Yahoo Finance")
