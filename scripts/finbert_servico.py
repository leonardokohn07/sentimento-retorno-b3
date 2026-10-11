# -*- coding: utf-8 -*-
"""
finbert_servico.py — o FinBERT-PT-BR rodando à parte, para o painel.

Quem inicia este script é o painel (modulos/finbert_vivo.py), com o Python do
ambiente separado venv_finbert. Não precisa rodar à mão.

Como conversa com o painel (uma linha de JSON por mensagem):
    1. carrega o modelo e escreve {"pronto": true, "python": ..., "torch": ...}
       (ou {"erro": ...}, se não conseguir);
    2. para cada linha {"texto": "manchete"} que chega na entrada, escreve
       {"escore": ..., "positivo": ..., "negativo": ..., "neutro": ...}.

A conta é a mesma do estudo (modulos/finbert_vivo.pontuar_local).
"""
import json
import platform
import sys
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def responder(obj):
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def main():
    try:
        from modulos import finbert_vivo
        modelo = finbert_vivo.carregar_local()
        import torch
    except Exception as e:  # noqa: BLE001 — o motivo vai para a tela do painel
        traceback.print_exc()          # vai para o log (stderr)
        responder({"erro": f"{type(e).__name__}: {e}"})
        return 1
    responder({"pronto": True, "python": platform.python_version(), "torch": torch.__version__})
    for linha in sys.stdin:
        linha = linha.strip()
        if not linha:
            continue
        try:
            texto = json.loads(linha)["texto"]
            responder(finbert_vivo.pontuar_local(modelo, texto))
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            responder({"erro": f"{type(e).__name__}: {e}"})
    return 0


if __name__ == "__main__":
    sys.exit(main())
