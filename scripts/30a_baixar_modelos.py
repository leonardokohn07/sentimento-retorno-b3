# -*- coding: utf-8 -*-
"""
30a_baixar_modelos.py — baixa os arquivos dos modelos de linguagem (Fase F).
SÓ BAIXA. Não precisa do torch.

Por que existe: no Windows do Leonardo, o torch não carrega (erro WinError 1114
ao abrir c10.dll, típico de Visual C++ Redistributable desatualizado). Então
os modelos são baixados aqui e o cálculo dos escores roda no Linux, com o
mesmo scripts/30_sentimento_modelos.py (opção --pasta-modelos).

Saída: dados/modelos/<modelo>/arquivos/  (config, tokenizador e pesos)
       dados/modelos/<modelo>/README.md e config.json (cartão oficial)
Uso:   .\\venv\\Scripts\\python scripts\\30a_baixar_modelos.py
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MODELOS = {
    "finbert": "lucas-leme/FinBERT-PT-BR",
    "distil": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
}
STATUS = RAIZ / "dados" / "execucao" / "status.txt"


def marcar(texto):
    STATUS.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(f"{texto} {datetime.now():%Y-%m-%d %H:%M:%S}\n")


def main():
    from huggingface_hub import HfApi, snapshot_download
    api = HfApi()
    for nome, repo in MODELOS.items():
        try:
            arquivos = api.list_repo_files(repo)
            print(f"[{nome}] {repo}: {len(arquivos)} arquivos no repositório")
            pesos = [a for a in arquivos if a.endswith(".safetensors") and "/" not in a]
            if not pesos:
                pesos = [a for a in arquivos if a == "pytorch_model.bin"]
            outros = [a for a in arquivos if "/" not in a and (
                a.endswith(".json") or a.endswith(".txt") or a.endswith(".model") or a == "README.md")]
            destino = RAIZ / "dados" / "modelos" / nome / "arquivos"
            snapshot_download(repo_id=repo, local_dir=destino, allow_patterns=pesos + outros)
            for a in ("README.md", "config.json"):
                if (destino / a).exists():
                    shutil.copy(destino / a, destino.parent / a)
            for a in sorted(destino.iterdir()):
                if a.is_file():
                    print(f"   {a.name:40s} {a.stat().st_size / 1e6:9.1f} MB")
        except Exception as e:
            print(f"[{nome}] ERRO: {type(e).__name__}: {e}")


if __name__ == "__main__":
    try:
        main()
    finally:
        marcar("FIM_30a")
