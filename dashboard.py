"""
dashboard.py
------------
InvestAI — sentimento de notícias × retorno de ações na B3.

O painel do estudo apresentado na MOSTRATEC-LIBERATO 2026. Mostra TODOS os
resultados, na ordem das perguntas da pesquisa, e refaz partes das contas na
frente de quem estiver olhando:

    O estudo
        Início ............................ a pergunta, a resposta e os números
        Como medimos o sentimento ......... o léxico ao vivo (digite uma manchete)
        O método foi testado antes ........ validação com dados sintéticos e poder
    Resultados
        1 · Existe relação? ............... mesmo dia, por ativo, defasagens, permutação
        2 · A relação é real? ............. retorno anormal, placebo, réplicas
        3 · Quem vem primeiro? ............ testes de direção, hora a hora, minuto a minuto
    Por dentro
        Explorar os dados ................. as notícias e os preços de cada ativo
        Verificação e transparência ....... impressões digitais, verificador, registro

De onde vêm os números
    Das saídas congeladas do verificador (verificacao/referencia/), as mesmas
    do relatório. Nada é digitado à mão. As contas refeitas ao vivo leem o
    pacote de dados congelados (verificacao/dados_congelados_2026-10-02.zip)
    e chegam aos mesmos números.

Até 10/10/2026 este arquivo era a tela de coleta do estudo. A coleta continua
nos scripts (scripts/2_coletar_e_analisar.py e scripts/34_coleta_diaria.py);
o painel agora é só leitura e demonstração. A versão anterior está no
histórico do git.

Este trabalho é acadêmico. Não é recomendação de investimento.

Execute com: streamlit run dashboard.py
"""
import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modulos.visual import aplicar_estilo  # noqa: E402
from modulos.interface import preparar_pagina  # noqa: E402

st.set_page_config(
    page_title="InvestAI — notícias × preço na B3",
    page_icon=":material/query_stats:",
    layout="wide",
    initial_sidebar_state="expanded",
)
aplicar_estilo()
preparar_pagina()

paginas = {
    "O estudo": [
        st.Page("paginas/inicio.py", title="Início", icon=":material/home:", default=True),
        st.Page("paginas/sentimento.py", title="Como medimos o sentimento", icon=":material/text_fields:"),
        st.Page("paginas/metodo.py", title="O método foi testado antes", icon=":material/science:"),
    ],
    "Resultados": [
        st.Page("paginas/mesmo_dia.py", title="1 · Existe relação?", icon=":material/link:"),
        st.Page("paginas/robustez.py", title="2 · A relação é real?", icon=":material/verified:"),
        st.Page("paginas/direcao.py", title="3 · Quem vem primeiro?", icon=":material/schedule:"),
    ],
    "Por dentro": [
        st.Page("paginas/explorar.py", title="Explorar os dados", icon=":material/table_view:"),
        st.Page("paginas/verificacao.py", title="Verificação e transparência", icon=":material/fact_check:"),
    ],
}

with st.sidebar:
    st.markdown("**InvestAI**  \nNotícias × preço na B3")
    st.caption("Leonardo Kohn e Maurício Renck Gedrat · orientador: Prof. Raul Mesquita  \n"
               "Fundação Liberato · MOSTRATEC-LIBERATO 2026")

pg = st.navigation(paginas, expanded=True)
pg.run()

st.markdown("---")
st.caption("Trabalho acadêmico, apresentado na MOSTRATEC-LIBERATO 2026. Não é recomendação de investimento. "
           "Números: verificacao/referencia (dados congelados em 02/10/2026).")
