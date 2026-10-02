# -*- coding: utf-8 -*-
"""
30_sentimento_modelos.py — sentimento das manchetes com modelos de linguagem.

Fase F (pré-registro: docs/pre-registro_2026-10-02_fase-F_modelo-de-linguagem.md).
SÓ CALCULA OS ESCORES. Nenhum teste é feito aqui.

Modelos (baixados do Hugging Face na 1ª vez; depois ficam no cache do PC):
    finbert : lucas-leme/FinBERT-PT-BR
              (BERT em português ajustado para o mercado financeiro brasileiro)
    distil  : lxyuan/distilbert-base-multilingual-cased-sentiments-student
              (o modelo que o AnalisadorV2 já tentava usar)

Entrada: todas as manchetes do projeto, sem o " - Nome do Jornal":
    dados/noticias_com_sentimento.csv, dados/noticias_2021_2023.csv,
    dados/validacao_lexico/para_rotular.csv e, se existirem,
    dados/prospectivo/noticias_recentes.csv e dados/smallcaps/noticias_smallcaps.csv

Saídas:
    dados/sentimento_<modelo>.csv     manchete + probabilidade de cada rótulo
    dados/modelos/<modelo>/README.md  cartão oficial do modelo, como veio
    dados/modelos/<modelo>/config.json

Se for interrompido, rodar de novo continua de onde parou (só calcula as
manchetes que ainda não têm escore).

Uso:  .\\venv\\Scripts\\python scripts\\30_sentimento_modelos.py
"""
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np
import pandas as pd

from modulos.analise.validacao_lexico import tirar_fonte

MODELOS = {
    "finbert": "lucas-leme/FinBERT-PT-BR",
    "distil": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
}
DADOS = RAIZ / "dados"
STATUS = DADOS / "execucao" / "status.txt"
LOTE = 64            # manchetes por passada no modelo
GRAVAR_A_CADA = 512  # grava o progresso a cada tantas manchetes


def marcar(texto):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"{texto} {datetime.now():%Y-%m-%d %H:%M:%S}\n")


def todas_as_manchetes():
    """Conjunto de manchetes únicas (texto limpo) de todos os arquivos do projeto."""
    textos = set()
    arquivos = [DADOS / "noticias_com_sentimento.csv", DADOS / "noticias_2021_2023.csv",
                DADOS / "validacao_lexico" / "para_rotular.csv",
                DADOS / "prospectivo" / "noticias_recentes.csv",
                DADOS / "smallcaps" / "noticias_smallcaps.csv"]
    for arq in arquivos:
        if not arq.exists():
            continue
        sep = ";" if arq.name == "para_rotular.csv" else ","
        d = pd.read_csv(arq, sep=sep)
        if "manchete" in d.columns:
            novos = d["manchete"].astype(str).str.strip()
        else:
            novos = pd.Series([tirar_fonte(t, f) for t, f in zip(d["titulo"], d["fonte"])])
        antes = len(textos)
        textos |= set(novos[novos.str.len() > 0])
        print(f"  {arq.relative_to(RAIZ)}: {len(d)} linhas, +{len(textos) - antes} manchetes novas")
    textos.discard("nan")
    return sorted(textos)


def guardar_cartao(nome, repo):
    """Copia o cartão oficial (README.md) e o config.json do modelo para dados/modelos/."""
    from huggingface_hub import hf_hub_download
    destino = DADOS / "modelos" / nome
    destino.mkdir(parents=True, exist_ok=True)
    for arq in ("README.md", "config.json"):
        try:
            shutil.copy(hf_hub_download(repo_id=repo, filename=arq), destino / arq)
            print(f"  cartão guardado: dados/modelos/{nome}/{arq}")
        except Exception as e:
            print(f"  [aviso] não deu para guardar {repo}/{arq}: {e}")


def rodar_modelo(nome, repo, textos):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    saida = DADOS / f"sentimento_{nome}.csv"
    feitas = set()
    if saida.exists():
        feitas = set(pd.read_csv(saida)["manchete"].astype(str))
    faltam = [t for t in textos if t not in feitas]
    print(f"\n[{nome}] {repo}: {len(feitas)} já feitas, {len(faltam)} a calcular")
    if not faltam:
        return

    guardar_cartao(nome, repo)
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    tok = AutoTokenizer.from_pretrained(repo)
    modelo = AutoModelForSequenceClassification.from_pretrained(repo)
    modelo.eval()
    rotulos = [str(modelo.config.id2label[i]).strip().lower().replace(" ", "_")
               for i in range(modelo.config.num_labels)]
    print(f"[{nome}] rótulos do modelo (config.id2label): {rotulos}")

    # Ordena por tamanho: lotes de manchetes parecidas desperdiçam menos padding.
    faltam = sorted(faltam, key=len)
    buffer, inicio, feitas_agora = [], time.time(), 0
    for i in range(0, len(faltam), LOTE):
        lote = faltam[i:i + LOTE]
        enc = tok(lote, padding=True, truncation=True, max_length=128, return_tensors="pt")
        with torch.inference_mode():
            prob = torch.softmax(modelo(**enc).logits, dim=-1).numpy()
        for texto, p in zip(lote, prob):
            buffer.append({"manchete": texto, **{f"{nome}_{r}": float(v) for r, v in zip(rotulos, p)}})
        feitas_agora += len(lote)
        if len(buffer) >= GRAVAR_A_CADA or i + LOTE >= len(faltam):
            pd.DataFrame(buffer).to_csv(saida, mode="a", header=not saida.exists(),
                                        index=False, encoding="utf-8")
            buffer = []
            ritmo = feitas_agora / max(time.time() - inicio, 1e-9)
            resta = (len(faltam) - feitas_agora) / max(ritmo, 1e-9)
            print(f"[{nome}] {feitas_agora}/{len(faltam)}  ({ritmo:.0f} por segundo, "
                  f"faltam ~{resta / 60:.1f} min)", flush=True)


def main():
    print(f"Início: {datetime.now():%d/%m/%Y %H:%M}")
    textos = todas_as_manchetes()
    print(f"Total de manchetes únicas: {len(textos)}")
    for nome, repo in MODELOS.items():
        try:
            rodar_modelo(nome, repo, textos)
        except Exception as e:
            print(f"[{nome}] ERRO: {type(e).__name__}: {e}")
    print(f"Fim: {datetime.now():%d/%m/%Y %H:%M}")


if __name__ == "__main__":
    try:
        main()
    finally:
        marcar("FIM_30")
