# -*- coding: utf-8 -*-
"""
24_horarios_wordpress.py — SÓ COLETA (nenhum teste).

Muitos sites de notícia brasileiros usam WordPress, que tem uma API pública
(/wp-json/wp/v2/posts) que devolve a data e a HORA EXATA de publicação de
cada matéria, em UTC (campo date_gmt). Este script:
  1. testa quais sites da amostra têm essa API aberta;
  2. nesses sites, procura cada manchete pelo título e guarda a hora oficial.

Educado com os sites: uma consulta por vez por site, com pausa.
Só lê metadados (título, link, data). Nada de texto das matérias.

Saída: dados/horarios_wordpress.csv
Uso:   .\\venv\\Scripts\\python scripts\\24_horarios_wordpress.py
"""
import concurrent.futures as cf
import difflib
import html
import re
import sys
import time
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import pandas as pd
import requests

ATIVOS = ["ABEV3.SA", "BBDC4.SA", "ITUB4.SA", "MGLU3.SA", "PETR4.SA", "SUZB3.SA", "VALE3.SA", "WEGE3.SA"]
SAIDA = RAIZ / "dados" / "horarios_wordpress.csv"
UA = {"User-Agent": "InvestAI-pesquisa-escolar/1.0 (estudo estatistico; so metadados)"}
PAUSA = 0.8
LIMITE_MIN = 45   # tempo máximo de coleta

DOMINIOS = {
 "InfoMoney": "www.infomoney.com.br", "Money Times": "www.moneytimes.com.br", "moneytimes.com.br": "www.moneytimes.com.br",
 "Seu Dinheiro": "www.seudinheiro.com", "InvestNews": "investnews.com.br", "suno.com.br": "www.suno.com.br",
 "Forbes Brasil": "forbes.com.br", "poder360.com.br": "www.poder360.com.br", "Poder360": "www.poder360.com.br",
 "cqcs.com.br": "cqcs.com.br", "CQCS": "cqcs.com.br", "Sindicato dos Bancários": "spbancarios.com.br",
 "Investidor10": "investidor10.com.br", "NeoFeed": "neofeed.com.br", "neofeed.com.br": "neofeed.com.br",
 "VEJA": "veja.abril.com.br", "veja.abril.com.br": "veja.abril.com.br",
 "CPG Click Petróleo e Gás": "clickpetroleoegas.com.br", "istoedinheiro.com.br": "istoedinheiro.com.br",
 "ISTOÉ DINHEIRO": "istoedinheiro.com.br", "Agência iNFRA": "agenciainfra.com",
 "CNN Brasil": "www.cnnbrasil.com.br", "cnnbrasil.com.br": "www.cnnbrasil.com.br",
 "Marcas pelo Mundo": "marcaspelomundo.com.br", "Brazil Journal": "braziljournal.com", "braziljournal.com": "braziljournal.com",
 "JC Concursos": "jcconcursos.com.br", "Passageiro de Primeira": "passageirodeprimeira.com",
 "Diário do Comércio": "diariodocomercio.com.br", "CartaCapital": "www.cartacapital.com.br",
 "EuQueroInvestir": "euqueroinvestir.com", "Brasil de Fato": "www.brasildefato.com.br",
 "trademap.com.br": "trademap.com.br", "TV Foco": "www.otvfoco.com.br", "Meio e Mensagem": "www.meioemensagem.com.br",
 "Estratégia Concursos": "www.estrategiaconcursos.com.br", "Monitor Mercantil": "monitormercantil.com.br",
 "OCP News": "ocp.news", "Nord Investimentos": "www.nordinvestimentos.com.br", "BPMoney": "bpmoney.com.br",
 "Guia do Investidor": "guiadoinvestidor.com.br", "Exame": "exame.com", "Agência eixos": "eixos.com.br",
 "Bloomberg Línea Brasil": "www.bloomberglinea.com.br", "Editora Brasil Energia": "brasilenergia.com.br",
 "Brasil Mineral": "www.brasilmineral.com.br", "Melhores Cartões": "www.melhorescartoes.com.br",
 "SEGS Portal Nacional": "www.segs.com.br", "Sindicato dos Bancários da Bahia": "bancariosbahia.org.br",
 "Pipeline": "pipelinevalor.globo.com", "TudoCelular.com": "www.tudocelular.com", "Migalhas": "www.migalhas.com.br",
 "metropoles.com": "www.metropoles.com", "Sonho Seguro": "www.sonhoseguro.com.br", "Economic News Brasil": "economicnewsbrasil.com.br",
 "bancariosbh.org.br": "bancariosbh.org.br", "Live MKT News": "livemktnews.com.br", "ND Mais": "ndmais.com.br",
 "mercadoeconsumo.com.br": "mercadoeconsumo.com.br", "Mercado&Consumo": "mercadoeconsumo.com.br",
 "TI INSIDE Online": "tiinside.com.br", "financenews.com.br": "financenews.com.br", "A Revista": "arevista.com.br",
 "CidadeMarketing": "www.cidademarketing.com.br", "MegaWhat": "megawhat.energy", "Revista Cobertura": "www.revistacobertura.com.br",
 "O Fator": "ofator.com.br", "Empiricus": "www.empiricus.com.br", "Giro News": "gironews.com", "StartSe": "www.startse.com",
 "Mobills": "www.mobills.com.br", "Revista Oeste": "revistaoeste.com", "Portal Celulose": "www.portalcelulose.com.br",
 "Mobile Time": "www.mobiletime.com.br", "Money Report": "www.moneyreport.com.br", "Finsiders Brasil": "finsidersbrasil.com.br",
 "finsidersbrasil.com.br": "finsidersbrasil.com.br", "TeleSíntese": "telesintese.com.br", "itforum.com.br": "itforum.com.br",
 "Promoview": "www.promoview.com.br", "Tecnoblog": "tecnoblog.net", "AgFeed": "agfeed.com.br", "Capital Reset": "capitalreset.uol.com.br",
 "Times Brasil | CNBC": "timesbrasil.com.br", "Bora Investir": "borainvestir.b3.com.br", "Mais Retorno": "maisretorno.com",
 "Canal Solar": "canalsolar.com.br", "SpaceMoney": "spacemoney.com.br", "Consumidor Moderno": "consumidormoderno.com.br",
 "Mundo do Marketing": "mundodomarketing.com.br", "Movimento Econômico": "movimentoeconomico.com.br",
 "Visno Invest": "visnoinvest.com", "melhorinvestimento.net": "melhorinvestimento.net", "Bem Paraná": "www.bemparana.com.br",
 "SindicarioNET": "www.seebcgms.org.br", "Portos e Navios": "www.portosenavios.com.br", "Serra Noticiário": "serranoticiario.com.br",
 "Jornal do Comércio": "www.jornaldocomercio.com", "Campo Grande News": "www.campograndenews.com.br",
 "Correio de Carajás": "correiodecarajas.com.br", "Século Diário": "www.seculodiario.com.br", "adnews.com.br": "adnews.com.br",
 "Baguete": "www.baguete.com.br", "Janela Publicitária": "janela.com.br", "Business Moment": "businessmoment.com.br",
}


def norm(s):
    s = html.unescape(re.sub(r"<[^>]+>", "", str(s)))
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s).split()


def titulo_limpo(t, fonte):
    t = str(t)
    suf = f" - {fonte}"
    if t.endswith(suf):
        t = t[: -len(suf)]
    elif " - " in t:
        t = t.rsplit(" - ", 1)[0]
    return t.strip()


def sondar(dom):
    try:
        r = requests.get(f"https://{dom}/wp-json/wp/v2/posts", params={"per_page": 1, "_fields": "id,date_gmt"},
                         headers=UA, timeout=15)
        return dom, (r.status_code == 200 and r.text.strip().startswith("[") and "date_gmt" in r.text), r.status_code
    except Exception as e:
        return dom, False, type(e).__name__


def buscar(dom, linhas, prazo):
    out = []
    for _, n in linhas.iterrows():
        if time.time() > prazo:
            out.append({**n, "status": "nao_tentado_tempo"}); continue
        alvo = norm(n["titulo_limpo"])
        achou = None
        for k in (8, 5):
            q = " ".join(alvo[:k])
            try:
                r = requests.get(f"https://{dom}/wp-json/wp/v2/posts",
                                 params={"search": q, "per_page": 5, "_fields": "date,date_gmt,link,title"},
                                 headers=UA, timeout=20)
                res = r.json() if r.status_code == 200 else []
            except Exception:
                res = []
            time.sleep(PAUSA)
            melhor, sim = None, 0.0
            for p in res if isinstance(res, list) else []:
                s = difflib.SequenceMatcher(None, " ".join(alvo), " ".join(norm(p.get("title", {}).get("rendered", "")))).ratio()
                if s > sim:
                    melhor, sim = p, s
            if melhor is not None and sim >= 0.85:
                achou = (melhor, sim); break
        if achou:
            p, sim = achou
            out.append({**n, "status": "ok", "wp_titulo": html.unescape(re.sub(r"<[^>]+>", "", p["title"]["rendered"])),
                        "wp_link": p.get("link"), "wp_date": p.get("date"), "wp_date_gmt": p.get("date_gmt"),
                        "similaridade": round(sim, 3)})
        else:
            out.append({**n, "status": "nao_achou"})
    return out


def main():
    partes = [pd.read_csv(RAIZ / "dados" / f) for f in ("noticias_com_sentimento.csv", "noticias_2021_2023.csv")
              if (RAIZ / "dados" / f).exists()]
    n = pd.concat(partes, ignore_index=True)
    n = n[n["ticker"].isin(ATIVOS)].drop_duplicates("url")
    n = n[n["fonte"].isin(DOMINIOS)].copy()
    n["dominio"] = n["fonte"].map(DOMINIOS)
    n["titulo_limpo"] = [titulo_limpo(t, f) for t, f in zip(n["titulo"], n["fonte"])]
    n = n[["url", "fonte", "dominio", "titulo_limpo", "data"]]
    print(f"Artigos de fontes mapeadas: {len(n)} em {n['dominio'].nunique()} sites")

    with cf.ThreadPoolExecutor(16) as ex:
        sond = list(ex.map(sondar, sorted(n["dominio"].unique())))
    abertos = {d for d, ok, _ in sond if ok}
    for d, ok, st in sond:
        print(f"  {'API ABERTA ' if ok else 'fechada    '} {d}  ({st})")
    alvo = n[n["dominio"].isin(abertos)]
    print(f"\nSites com API aberta: {len(abertos)} | artigos a procurar: {len(alvo)}")

    prazo = time.time() + LIMITE_MIN * 60
    res = []
    with cf.ThreadPoolExecutor(max(1, len(abertos))) as ex:
        futs = {ex.submit(buscar, d, g, prazo): d for d, g in alvo.groupby("dominio")}
        for f in cf.as_completed(futs):
            r = f.result(); res.extend(r)
            ok = sum(1 for x in r if x.get("status") == "ok")
            print(f"  {futs[f]:<32} {ok:>4} de {len(r):>4} achados")
    df = pd.DataFrame(res)
    SAIDA.parent.mkdir(exist_ok=True)
    df.to_csv(SAIDA, index=False)
    print(f"\nTOTAL: {int((df['status'] == 'ok').sum())} horários de {len(df)} artigos procurados -> dados/{SAIDA.name}")


if __name__ == "__main__":
    main()
