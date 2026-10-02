# -*- coding: utf-8 -*-
"""
filtro_relato.py — marca manchetes que RELATAM o movimento da cotação.

Lista congelada em 02/10/2026, antes de qualquer teste com retornos.
Calibrada olhando só o texto das manchetes.

Uma manchete é "relato de preço" quando o verbo de movimento tem como sujeito
a AÇÃO, o TICKER ou o ÍNDICE ("Ação da Vale salta 3,9%", "(MGLU3) cai firme",
"Ibovespa fecha em alta"). "Lucro da Vale cai 56%" ou "Petrobras sobe o preço do
diesel" NÃO são relato: são informação sobre a empresa.
"""
import re
import unicodedata

_TODOS = (r"sobe|sobem|subiu|dispara|disparam|disparou|salta|saltam|saltou|avanca|avancam|avancou|"
          r"valoriza|valorizam|valorizou|cai|caem|caiu|recua|recuam|recuou|despenca|despencam|despencou|"
          r"desaba|desabam|desabou|tomba|tombam|tombou|afunda|afundam|afundou|derrete|derretem|derreteu|"
          r"desvaloriza|desvalorizam|desvalorizou")
_SEM_AVANCA = _TODOS.replace("avanca|avancam|avancou|", "")
_FORTES = r"dispara|disparam|disparou|salta|saltam|saltou|despenca|despencam|despencou|desaba|desabam|desabou|tomba|tombam|tombou|derrete|derretem|derreteu"
_FUNDAMENTO = re.compile(r"\b(lucro|receita|producao|vendas|ebitda|prejuizo|faturamento|dividendo|dividendos|preco do|precos d)")

PADRAO = re.compile(
    rf"\b(?:acao|acoes|papel|papeis|adrs?)\b[^.;:!?]{{0,40}}?\b(?:{_TODOS})\b"
    rf"|\b[a-z]{{4}}\d{{1,2}}\b[^.;:!?]{{0,40}}?\b(?:{_SEM_AVANCA})\b"
    r"|\b(?:ibovespa|ibov|bolsa)\s+(?:hoje|fecha|abre|sobe|cai|recua|avanca|opera|renova|bate|alcanca|mostra|"
    r"termina|encerra|dispara|despenca|tomba|zera|amplia|reduz|vira)\b"
    r"|\b(?:fecha|fecham|fechou|abre|abrem|abriu|opera|operam|operou|termina|terminam|terminou)\s+(?:em|no|na)\s+"
    r"(?:alta|queda|baixa|estabilidade|vermelho|verde|positivo|negativo)"
    r"|\bmaiores\s+(?:altas|quedas|baixas)\b|\blidera(?:m)?\s+(?:ganhos|perdas|altas|quedas)\b")
_FORTE_PCT = re.compile(rf"\b(?:{_FORTES})\s+(?:mais de |quase |ate )?\d+[\d,.]*\s?%")


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s).lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def eh_relato_de_preco(titulo: str) -> bool:
    t = normalizar(titulo)
    if PADRAO.search(t):
        return True
    return bool(_FORTE_PCT.search(t)) and not _FUNDAMENTO.search(t)
