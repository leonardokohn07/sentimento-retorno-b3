
"""
sentimento.py
-------------
Analisador de sentimento financeiro em português — versão melhorada.

Melhorias em relação à versão 1 do analisador (retirada do projeto em
18/09/2026; o que ela fazia está descrito abaixo, item a item):

  1. SCORE CONTÍNUO de -1 a +1 (antes era só Positivo/Negativo/Neutro).
     Necessário para calcular correlação — não se correlaciona texto.

  2. TRATAMENTO DE NEGAÇÃO. O léxico antigo classificava
     "Petrobras NÃO teve lucro" como POSITIVO, porque via a palavra "lucro".
     Agora "não", "sem", "deixou de" invertem o sinal do termo seguinte.

  3. INTENSIFICADORES e ATENUADORES. "forte alta" pesa mais que "leve alta".

  4. LÉXICO PONDERADO. "falência" (-1,0) é muito pior que "cautela" (-0,3).

  5. PESO POR RECÊNCIA e por posição: título pesa mais que o resumo,
     porque é o que o investidor realmente lê.
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from typing import Dict, Optional


# ─────────────────────────────────────────────────────────
# 1. LÉXICO FINANCEIRO PONDERADO
# ─────────────────────────────────────────────────────────
# Valores de -1,0 (péssimo) a +1,0 (ótimo).

LEXICO = {
    # ══ POSITIVO FORTE (+0,7 a +1,0) ══
    "lucro recorde": 1.0, "prejuizo revertido": 0.9, "recorde historico": 0.95,
    "recorde": 0.85, "dispara": 0.9, "disparam": 0.9, "disparou": 0.9,
    "dispararam": 0.9, "salta": 0.85, "saltam": 0.85, "saltou": 0.85,
    "saltaram": 0.85, "decola": 0.85, "decolam": 0.85, "voa": 0.8,
    "supera expectativas": 0.9, "superou expectativas": 0.9,
    "acima do esperado": 0.85, "acima das expectativas": 0.85,
    "melhor resultado": 0.9, "melhor da historia": 0.9,
    "forte alta": 0.9, "alta expressiva": 0.85, "forte valorizacao": 0.9,
    "maxima historica": 0.9, "maxima": 0.7, "renova maxima": 0.9,
    "dividendos extraordinarios": 0.9, "aquisicao estrategica": 0.75,

    # ══ POSITIVO MODERADO (+0,4 a +0,7) ══
    "lucro": 0.65, "lucros": 0.65, "lucra": 0.65, "lucrou": 0.65,
    "alta": 0.5, "altas": 0.5, "sobe": 0.55, "sobem": 0.55, "subiu": 0.55,
    "subiram": 0.55, "avanca": 0.5, "avancam": 0.5, "avancou": 0.5,
    "ganha": 0.5, "ganham": 0.5, "ganhou": 0.5, "ganho": 0.55, "ganhos": 0.55,
    "valoriza": 0.6, "valorizam": 0.6, "valorizou": 0.6, "valorizacao": 0.6,
    "crescimento": 0.6, "cresce": 0.55, "crescem": 0.55, "cresceu": 0.55,
    "expansao": 0.55, "expande": 0.5, "recuperacao": 0.5, "recupera": 0.5,
    "retomada": 0.5, "otimismo": 0.6, "otimista": 0.55,
    "dividendos": 0.6, "dividendo": 0.6, "jcp": 0.6,
    "juros sobre capital proprio": 0.65, "proventos": 0.6, "bonificacao": 0.6,
    "recompra": 0.55, "recompra de acoes": 0.6,
    "supera": 0.6, "superou": 0.6, "superam": 0.6,
    "eleva": 0.5, "elevou": 0.5, "elevam": 0.5, "elevacao": 0.5,
    "aumenta": 0.45, "aumentou": 0.45, "aumento": 0.45,
    "upgrade": 0.7, "recomendacao de compra": 0.75,
    "eleva recomendacao": 0.7, "eleva preco alvo": 0.65,
    "melhora": 0.5, "melhorou": 0.5, "positivo": 0.5, "positiva": 0.5,
    "aprovado": 0.2, "aprovacao": 0.2, "aprova": 0.2, "aprovou": 0.2,
    "fusao": 0.3, "aquisicao": 0.25, "expansao internacional": 0.6,

    # ══ POSITIVO FRACO (+0,15 a +0,4) ══
    "investimento": 0.15, "investimentos": 0.15, "investe": 0.15,
    "investira": 0.15, "plano de investimentos": 0.2,
    "parceria": 0.25, "acordo": 0.15, "contrato": 0.15, "contratos": 0.15,
    "leve alta": 0.3, "ligeira alta": 0.3, "sobe levemente": 0.3,
    "estavel": 0.05, "estaveis": 0.05, "manteve": 0.05, "mantem": 0.05,
    "confirma": 0.1, "confirmou": 0.1, "reafirma": 0.1,
    "expectativa": 0.05, "expectativas": 0.05, "projecao": 0.05,
    "eleva projecao": 0.55, "eleva estimativa": 0.55,
    "novo projeto": 0.2, "nova unidade": 0.2, "inaugura": 0.25,

    # ══ NEGATIVO FRACO (-0,15 a -0,4) ══
    "cautela": -0.3, "cauteloso": -0.3, "atencao": -0.2,
    "revisao": -0.25, "revisa": -0.2, "adiamento": -0.35, "adia": -0.35,
    "leve queda": -0.3, "ligeira queda": -0.3, "cai levemente": -0.3,
    "volatilidade": -0.25, "incerteza": -0.4, "incertezas": -0.4,
    "duvida": -0.3, "duvidas": -0.3, "pressao": -0.35, "pressiona": -0.35,
    "pressionado": -0.4, "pressionada": -0.4, "pressionam": -0.35,
    "desafio": -0.25, "desafios": -0.25, "temor": -0.45, "temores": -0.45,
    "receio": -0.4, "preocupa": -0.45,

    # ══ NEGATIVO MODERADO (-0,4 a -0,7) ══
    "queda": -0.55, "quedas": -0.55, "cai": -0.55, "caem": -0.55,
    "caiu": -0.55, "cairam": -0.55, "recua": -0.5, "recuam": -0.5,
    "recuou": -0.5, "recuo": -0.5, "cede": -0.4, "cedem": -0.4,
    "perde": -0.55, "perdem": -0.55, "perdeu": -0.55, "perda": -0.6,
    "perdas": -0.6, "prejuizo": -0.75, "prejuizos": -0.75,
    "baixa": -0.5, "em baixa": -0.5, "fecha em baixa": -0.55,
    "desvaloriza": -0.6, "desvalorizacao": -0.6,
    "reduz": -0.4, "reduziu": -0.4, "reducao": -0.4,
    "corte": -0.5, "cortes": -0.5, "corta": -0.5, "cortou": -0.5,
    "demissao": -0.6, "demissoes": -0.6, "corte de vagas": -0.6,
    "fechamento": -0.45, "fecha unidade": -0.6, "encerra operacao": -0.6,
    "negativo": -0.5, "negativa": -0.5, "pessimismo": -0.6,
    "preocupacao": -0.5, "fraco": -0.5, "fraca": -0.5, "fracos": -0.5,
    "risco": -0.4, "riscos": -0.4, "alerta": -0.45,
    "endividamento": -0.55, "divida": -0.45, "dividas": -0.45,
    "alavancagem": -0.4, "multa": -0.6, "multado": -0.6,
    "processo": -0.45, "processada": -0.5, "acao judicial": -0.55,
    "investigacao": -0.6, "investigado": -0.6, "denuncia": -0.6,
    "downgrade": -0.7, "recomendacao de venda": -0.75,
    "corta recomendacao": -0.65, "reduz preco alvo": -0.6,
    "abaixo do esperado": -0.7, "aquem do esperado": -0.7,
    "aquem das expectativas": -0.7, "abaixo das expectativas": -0.7,
    "ficou aquem": -0.65, "nao atingiu": -0.6, "deixou de atingir": -0.6,
    "frustra": -0.65, "frustrou": -0.65, "decepciona": -0.7,
    "greve": -0.55, "paralisacao": -0.55, "acidente": -0.6,
    "vazamento": -0.6, "interdicao": -0.6, "embargo": -0.6,

    # ══ NEGATIVO FORTE (-0,7 a -1,0) ══
    "falencia": -1.0, "recuperacao judicial": -0.95, "calote": -0.95,
    "default": -0.9, "fraude": -0.95, "escandalo": -0.9,
    "despenca": -0.9, "despencam": -0.9, "despencou": -0.9,
    "desaba": -0.9, "desabam": -0.9, "desabou": -0.9,
    "derrete": -0.85, "derretem": -0.85, "afunda": -0.85, "afundou": -0.85,
    "tombo": -0.85, "forte queda": -0.85, "queda expressiva": -0.85,
    "minima historica": -0.85, "renova minima": -0.85, "minima": -0.6,
    "crise": -0.75, "recessao": -0.8, "colapso": -0.9,
    "prejuizo recorde": -1.0, "pior resultado": -0.9,
    "demissao em massa": -0.85, "sancao": -0.7, "sancoes": -0.7,
    "rebaixamento": -0.8, "rebaixa": -0.75, "rombo": -0.85,
    "suspensao": -0.6, "suspende": -0.55, "cancelamento": -0.6,
    "cancela": -0.55, "desastre": -0.9, "tragedia": -0.9,
}

# Palavras que INVERTEM o sentido do termo seguinte
NEGADORES = {
    "nao", "nem", "sem", "nunca", "jamais", "nenhum", "nenhuma",
    "deixou de", "deixa de", "aquem", "abaixo do", "menos que",
    "frustrou", "frustra", "descarta", "descartou", "negou", "nega",
}

# Palavras que AUMENTAM a intensidade
INTENSIFICADORES = {
    "muito": 1.5, "forte": 1.5, "fortemente": 1.5, "extremamente": 1.8,
    "bastante": 1.3, "significativo": 1.4, "significativa": 1.4,
    "expressivo": 1.5, "expressiva": 1.5, "recorde": 1.6, "historico": 1.5,
    "acentuado": 1.5, "acentuada": 1.5, "drastico": 1.7, "drastica": 1.7,
}

# Palavras que DIMINUEM a intensidade
ATENUADORES = {
    "leve": 0.5, "leves": 0.5, "ligeiro": 0.5, "ligeira": 0.5,
    "pouco": 0.6, "discreto": 0.55, "discreta": 0.55, "parcial": 0.6,
    "moderado": 0.7, "moderada": 0.7, "pequeno": 0.6, "pequena": 0.6,
}


# ─────────────────────────────────────────────────────────
# 2. NORMALIZAÇÃO DE TEXTO
# ─────────────────────────────────────────────────────────

def normalizar(texto: str) -> str:
    """
    Deixa o texto em minúsculas e SEM ACENTOS.

    Por quê? Para que "prejuízo", "prejuizo" e "PREJUÍZO" sejam tratados
    como a mesma palavra. Sem isso, metade das ocorrências escapa do léxico.
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    # NFD separa a letra do acento; depois removemos os acentos (categoria Mn)
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


# ─────────────────────────────────────────────────────────
# 3. ANÁLISE LÉXICA COM CONTEXTO
# ─────────────────────────────────────────────────────────

def analisar_lexico(texto: str, janela_contexto: int = 3) -> Dict:
    """
    Calcula a polaridade do texto considerando negação e intensidade.

    Como funciona, passo a passo:
        1. Normaliza o texto
        2. Procura expressões de 2 palavras primeiro (ex: "forte queda"),
           depois palavras isoladas
        3. Para cada termo encontrado, olha as N palavras ANTERIORES:
             - achou negador?      -> inverte o sinal e reduz a 80%
             - achou intensificador -> multiplica o peso
             - achou atenuador      -> divide o peso
        4. Soma tudo e normaliza para o intervalo -1 a +1

    Returns:
        score_polaridade : float de -1 a +1
        classificacao    : "Positivo" / "Negativo" / "Neutro"
        confianca        : 0 a 1 (quantos termos foram achados)
        termos_achados   : lista para você auditar o resultado
    """
    limpo = normalizar(texto)
    if not limpo:
        return _resultado_neutro()

    palavras = limpo.split()
    contribuicoes = []
    achados = []
    i = 0

    while i < len(palavras):
        termo, peso, tamanho = None, None, 1

        # Tenta expressão de 2 palavras (tem prioridade)
        if i + 1 < len(palavras):
            bigrama = f"{palavras[i]} {palavras[i+1]}"
            if bigrama in LEXICO:
                termo, peso, tamanho = bigrama, LEXICO[bigrama], 2

        # Senão, palavra isolada
        if termo is None and palavras[i] in LEXICO:
            termo, peso = palavras[i], LEXICO[palavras[i]]

        if termo is None or peso == 0:
            i += 1
            continue

        # ---- olha o contexto anterior ----
        inicio = max(0, i - janela_contexto)
        contexto = palavras[inicio:i]
        contexto_txt = " ".join(contexto)

        negado = any(n in contexto_txt for n in NEGADORES)
        multiplicador = 1.0

        for p in contexto:
            if p in INTENSIFICADORES:
                multiplicador *= INTENSIFICADORES[p]
            elif p in ATENUADORES:
                multiplicador *= ATENUADORES[p]

        valor = peso * multiplicador
        if negado:
            # Negação inverte, mas com força menor:
            # "não teve lucro" é ruim, porém menos ruim que "prejuízo"
            valor = -valor * 0.8

        valor = float(np.clip(valor, -1.0, 1.0))
        contribuicoes.append(valor)
        achados.append({
            "termo": termo,
            "peso_base": peso,
            "negado": negado,
            "multiplicador": round(multiplicador, 2),
            "valor_final": round(valor, 3),
        })

        i += tamanho

    if not contribuicoes:
        return _resultado_neutro()

    # Média das contribuições encontradas.
    #
    # Antes havia aqui um fator de "reforço" que ENCOLHIA o score quando
    # poucos termos eram achados (0,7x com um único termo). Isso penalizava
    # justamente o caso mais comum: manchete curta com uma palavra forte.
    # "Vale despenca 8%" tem um termo só — e é uma notícia clarissimamente
    # negativa. O fator foi removido.
    #
    # O termo mais forte domina: se a manchete traz "falência" (-1,0) junto
    # de "contrato" (+0,35), a média simples suavizaria demais. Por isso a
    # média é ponderada pelo peso absoluto de cada termo.
    valores = np.array(contribuicoes)
    pesos_abs = np.abs(valores)
    if pesos_abs.sum() > 0:
        score = float(np.average(valores, weights=pesos_abs))
    else:
        score = float(np.mean(valores))
    score = float(np.clip(score, -1.0, 1.0))

    if score > 0.15:
        classe = "Positivo"
    elif score < -0.15:
        classe = "Negativo"
    else:
        classe = "Neutro"

    return {
        "score_polaridade": round(score, 4),
        "classificacao": classe,
        "confianca": round(min(1.0, len(contribuicoes) / 5), 3),
        "n_termos": len(contribuicoes),
        "termos_achados": achados,
    }


def _resultado_neutro() -> Dict:
    return {
        "score_polaridade": 0.0,
        "classificacao": "Neutro",
        "confianca": 0.0,
        "n_termos": 0,
        "termos_achados": [],
    }


# ─────────────────────────────────────────────────────────
# 4. ANALISADOR COM MODELO ML (OPCIONAL)
# ─────────────────────────────────────────────────────────

class AnalisadorV2:
    """
    Combina o léxico com um modelo de NLP do HuggingFace.

    Se o modelo estiver disponível, usa a MÉDIA PONDERADA dos dois métodos.
    Isso costuma dar resultado melhor que qualquer um sozinho:
        - o léxico entende o jargão financeiro
        - o modelo entende a estrutura da frase
    """

    def __init__(self, usar_ml: bool = True, peso_ml: float = 0.5):
        self.peso_ml = peso_ml
        self.modelo = None
        if usar_ml:
            self._carregar()

    def _carregar(self):
        try:
            from transformers import pipeline
            print("[INFO] Carregando modelo NLP (demora na 1ª vez)...")
            self.modelo = pipeline(
                "sentiment-analysis",
                model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
                top_k=None, truncation=True, max_length=512,
            )
            print("[OK] Modelo carregado.")
        except Exception as e:
            print(f"[AVISO] Modelo indisponível ({e}). Usando só o léxico.")
            self.modelo = None

    def _score_ml(self, texto: str) -> Optional[float]:
        """Converte a saída do modelo para o intervalo -1 a +1."""
        if not self.modelo:
            return None
        try:
            saida = self.modelo(texto[:512])[0]
            s = {r["label"].lower(): r["score"] for r in saida}
            return float(s.get("positive", 0) - s.get("negative", 0))
        except Exception:
            return None

    def analisar(self, titulo: str, resumo: str = "") -> Dict:
        """
        Analisa uma notícia.

        Peso entre título e resumo:
            O título é o que causa a reação imediata do investidor, então
            pesa mais. MAS: o Google News quase nunca envia um resumo útil
            (costuma vir vazio ou só com o nome do veículo).

            Se o resumo entrasse como 0,0 nesses casos, TODO score seria
            multiplicado por 0,7 — um desconto de 30% que empurra notícias
            legítimas para a faixa neutra. Por isso só dividimos o peso
            quando o resumo realmente tem conteúdo.
        """
        if not isinstance(titulo, str):
            titulo = ""
        r_tit = analisar_lexico(titulo)

        # Ao ler de CSV, células vazias viram NaN (float), não string.
        # Sem esta normalização, .strip() quebra com AttributeError.
        if not isinstance(resumo, str):
            resumo = ""

        # O resumo só conta se tiver conteúdo de verdade
        resumo_util = len(resumo.strip()) >= 25
        r_res = analisar_lexico(resumo) if resumo_util else _resultado_neutro()

        if resumo_util and r_res["n_termos"] > 0:
            score_lex = 0.7 * r_tit["score_polaridade"] + 0.3 * r_res["score_polaridade"]
        else:
            # Sem resumo aproveitável: o título carrega 100% do peso
            score_lex = r_tit["score_polaridade"]

        score_ml = self._score_ml(f"{titulo}. {resumo}")
        if score_ml is not None:
            score = (1 - self.peso_ml) * score_lex + self.peso_ml * score_ml
            metodo = "hibrido"
        else:
            score, metodo = score_lex, "lexico"

        score = float(np.clip(score, -1.0, 1.0))

        if score > 0.15:
            classe = "Positivo"
        elif score < -0.15:
            classe = "Negativo"
        else:
            classe = "Neutro"

        return {
            "score_polaridade": round(score, 4),
            "score_lexico": round(score_lex, 4),
            "score_ml": round(score_ml, 4) if score_ml is not None else None,
            "classificacao": classe,
            "confianca": max(r_tit["confianca"], r_res["confianca"]),
            "metodo": metodo,
        }

    def analisar_batch(self, noticias: pd.DataFrame, callback_progresso=None) -> pd.DataFrame:
        """
        Aplica a análise em um DataFrame inteiro de notícias.

        Args:
            callback_progresso: função opcional chamada a cada 25 notícias,
                recebendo {"fracao": 0-1, "atual": int, "total": int}.
                Permite desenhar barra de progresso na interface.
        """
        df = noticias.copy()
        total = len(df)
        resultados = []

        for i, (_, row) in enumerate(df.iterrows(), start=1):
            resultados.append(
                self.analisar(row.get("titulo", ""), row.get("resumo", ""))
            )
            # Reporta a cada 25 itens (ou no último) para não travar a interface
            if callback_progresso is not None and (i % 25 == 0 or i == total):
                try:
                    callback_progresso({
                        "fracao": i / total if total else 1.0,
                        "atual": i,
                        "total": total,
                    })
                except Exception:
                    pass

        for campo in ["score_polaridade", "score_lexico", "score_ml",
                      "classificacao", "confianca", "metodo"]:
            df[campo] = [r[campo] for r in resultados]
        return df


# ─────────────────────────────────────────────────────────
# 5. AGREGAÇÃO POR ATIVO E ALERTAS
# ─────────────────────────────────────────────────────────
# Estas duas funções moram aqui porque pertencem ao sentimento, não à
# interface. Até 18/09/2026 elas estavam dentro de sentimento_antigo.py,
# de carona: quando o analisador V2 foi escrito, o analisador mudou de
# arquivo e elas ficaram para trás. O resultado é que o dashboard
# importava do arquivo da versão 1 para conseguir usar funções que nada
# tinham de antigas. Ficou resolvido movendo-as para o lugar certo.

LIMIAR_CLASSE = 0.15   # o mesmo usado por notícia, em analisar_lexico


def agregar_sentimento_por_ativo(
    noticias: pd.DataFrame,
    tickers: Optional[list] = None,
    col_score: str = "score_polaridade",
    col_classe: str = "classificacao",
) -> pd.DataFrame:
    """
    Resume as notícias de cada ativo numa linha.

    Atenção à unidade: a análise acontece POR NOTÍCIA (uma manchete de cada
    vez, sem ver as outras). Esta função apenas AGREGA o que já foi
    classificado. É a distinção entre unidade de medida (a notícia) e
    unidade de análise (o ativo-dia) — a mesma que aparece no estudo da
    hipótese.

    A média é simples, não ponderada por confiança: ponderar daria peso
    maior às manchetes com mais termos do léxico, o que enviesaria o
    resultado para o vocabulário que por acaso foi cadastrado.

    Returns:
        DataFrame indexado por ticker, com n_noticias, score_sentimento,
        pct_positivo, pct_negativo, pct_neutro e classificacao.
    """
    alvo = list(tickers) if tickers is not None else []
    if not alvo and noticias is not None and not noticias.empty:
        alvo = sorted(noticias["ticker"].dropna().unique())

    linhas = []
    for tk in alvo:
        if noticias is None or noticias.empty or col_score not in noticias.columns:
            sub = pd.DataFrame()
        else:
            sub = noticias[noticias["ticker"] == tk].dropna(subset=[col_score])

        if sub.empty:
            linhas.append({
                "ticker": tk, "n_noticias": 0, "score_sentimento": 0.0,
                "pct_positivo": 0, "pct_negativo": 0, "pct_neutro": 0,
                "classificacao": "Sem notícias",
            })
            continue

        n = len(sub)
        media = float(sub[col_score].mean())

        if col_classe in sub.columns:
            cont = sub[col_classe].value_counts()
            n_pos = int(cont.get("Positivo", 0))
            n_neg = int(cont.get("Negativo", 0))
        else:
            n_pos = int((sub[col_score] > LIMIAR_CLASSE).sum())
            n_neg = int((sub[col_score] < -LIMIAR_CLASSE).sum())
        n_neu = n - n_pos - n_neg

        if media > LIMIAR_CLASSE:
            classe = "Positivo"
        elif media < -LIMIAR_CLASSE:
            classe = "Negativo"
        else:
            classe = "Neutro"

        linhas.append({
            "ticker": tk,
            "n_noticias": n,
            "score_sentimento": round(media, 3),
            "pct_positivo": round(n_pos / n * 100),
            "pct_negativo": round(n_neg / n * 100),
            "pct_neutro": round(n_neu / n * 100),
            "classificacao": classe,
        })

    return pd.DataFrame(linhas).set_index("ticker")


def gerar_alertas(
    sentimento_por_ativo: pd.DataFrame,
    limiar_negativo: float = -0.3,
    limiar_pct_negativo: int = 50,
    minimo_noticias: int = 3,
) -> list:
    """
    Aponta os ativos cujo noticiário está claramente negativo.

    Por que um mínimo de notícias: com uma ou duas manchetes, a média não
    descreve o noticiário do ativo — descreve o acaso de quais notícias
    foram capturadas. Alertar em cima disso seria ruído com cara de sinal.

    Dois gatilhos independentes, de propósito:
        - média muito negativa -> poucas notícias muito ruins
        - maioria negativa     -> muitas notícias moderadamente ruins
    Um ativo pode acionar um sem acionar o outro, e os dois casos
    interessam.

    ISTO NÃO É RECOMENDAÇÃO DE INVESTIMENTO. É a leitura do que o
    noticiário coletado diz, e nada além disso.
    """
    alertas = []
    if sentimento_por_ativo is None or sentimento_por_ativo.empty:
        return alertas

    for tk, row in sentimento_por_ativo.iterrows():
        n = int(row.get("n_noticias", 0))
        if n < minimo_noticias:
            continue

        score = float(row.get("score_sentimento", 0.0))
        pct_neg = float(row.get("pct_negativo", 0))

        if score <= limiar_negativo:
            alertas.append({
                "ticker": tk,
                "tipo": "Sentimento negativo",
                "mensagem": (
                    f"sentimento médio {score:.2f} em {n} notícias "
                    f"(limiar {limiar_negativo:.2f})"
                ),
                "severidade": "Alta",
            })
        elif pct_neg >= limiar_pct_negativo:
            alertas.append({
                "ticker": tk,
                "tipo": "Maioria negativa",
                "mensagem": (
                    f"{pct_neg:.0f}% das {n} notícias são negativas, "
                    f"apesar da média em {score:.2f}"
                ),
                "severidade": "Média",
            })

    ordem = {"Alta": 0, "Média": 1}
    alertas.sort(key=lambda a: ordem.get(a["severidade"], 9))
    return alertas


# ─────────────────────────────────────────────────────────
# 5. TESTE — DEMONSTRA A CORREÇÃO DA NEGAÇÃO
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    testes = [
        "Petrobras registra lucro recorde no trimestre",
        "Petrobras não teve lucro no trimestre",          # negação!
        "Vale despenca após forte queda do minério",
        "Vale tem leve queda no pregão desta terça",      # atenuador
        "Ações do Itaú ficaram estáveis nesta sessão",
        "Magazine Luiza entra em recuperação judicial",
        "Resultado da WEG ficou aquém das expectativas",  # negação indireta
    ]

    print("=" * 70)
    print("  TESTE DO ANALISADOR V2")
    print("=" * 70)

    for t in testes:
        r = analisar_lexico(t)
        print(f"\n{t}")
        print(f"  -> score = {r['score_polaridade']:+.3f}  ({r['classificacao']})")
        for a in r["termos_achados"]:
            flag = " [NEGADO]" if a["negado"] else ""
            print(f"     · {a['termo']}: {a['peso_base']:+.2f} "
                  f"x{a['multiplicador']} = {a['valor_final']:+.3f}{flag}")
