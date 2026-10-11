# -*- coding: utf-8 -*-
"""
finbert_vivo.py
---------------
FinBERT-PT-BR ao vivo, para comparar com o léxico na página de sentimento.

É OPCIONAL. Precisa de torch e transformers funcionando. Se não der para
carregar (no computador Windows dos autores o torch falhava ao abrir a DLL
c10.dll, WinError 1114), a página mostra o motivo e segue só com o léxico e
com os escores do FinBERT já calculados no estudo.

Mesma conta de scripts/30_sentimento_modelos.py:
    escore = P(positivo) − P(negativo), com truncamento em 128 tokens.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LOCAL = RAIZ / "dados" / "modelos" / "finbert" / "arquivos"
REPOSITORIO = "lucas-leme/FinBERT-PT-BR"


def carregar():
    """Devolve (tokenizer, modelo, rótulos) ou levanta a exceção original."""
    import torch  # noqa: F401  (o erro de DLL do Windows, quando existe, aparece aqui)
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    fonte = str(LOCAL) if (LOCAL / "config.json").exists() else REPOSITORIO
    tok = AutoTokenizer.from_pretrained(fonte)
    mod = AutoModelForSequenceClassification.from_pretrained(fonte)
    mod.eval()
    rotulos = [str(mod.config.id2label[i]).strip().lower() for i in range(mod.config.num_labels)]
    return tok, mod, rotulos


def pontuar(carregado, texto: str) -> dict:
    import torch
    tok, mod, rotulos = carregado
    enc = tok([texto], padding=True, truncation=True, max_length=128, return_tensors="pt")
    with torch.inference_mode():
        prob = torch.softmax(mod(**enc).logits, dim=-1).numpy()[0]
    p = {r: float(v) for r, v in zip(rotulos, prob)}
    pos = next((v for k, v in p.items() if "pos" in k), 0.0)
    neg = next((v for k, v in p.items() if "neg" in k), 0.0)
    neu = next((v for k, v in p.items() if "neu" in k), 0.0)
    return {"escore": pos - neg, "positivo": pos, "negativo": neg, "neutro": neu}
