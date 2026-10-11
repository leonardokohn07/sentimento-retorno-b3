# -*- coding: utf-8 -*-
"""
finbert_vivo.py
---------------
FinBERT-PT-BR ao vivo, para comparar com o léxico na página de sentimento.

É OPCIONAL. Há dois jeitos de rodar, escolhidos sozinhos:

1. AMBIENTE SEPARADO (preferido, e o que funciona no Windows dos autores)
   Se existir a pasta venv_finbert/ (criada pelo TESTAR_FINBERT.bat), o modelo
   roda num processo à parte, com o Python e o torch DESSE ambiente
   (scripts/finbert_servico.py). O painel continua no venv principal, que é o
   ambiente da verificação, e só troca mensagens com o processo: manda a
   manchete, recebe as probabilidades. O modelo é carregado uma vez só.

   Por que separar: no venv principal (Python 3.14) o torch falhava ao abrir a
   DLL c10.dll (WinError 1114). Num ambiente com Python 3.12 e o torch "CPU"
   oficial, ele carrega, e o venv principal não precisa ser mexido.

2. NO PRÓPRIO PROCESSO
   Sem venv_finbert/, tenta carregar torch e transformers no Python do painel
   (é o que acontece no Linux, onde o torch funciona).

Se nada funcionar, a página mostra o motivo e segue com o léxico e com os
escores do FinBERT já calculados no estudo.

Mesma conta de scripts/30_sentimento_modelos.py:
    escore = P(positivo) − P(negativo), com truncamento em 128 tokens.
"""
import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LOCAL = RAIZ / "dados" / "modelos" / "finbert" / "arquivos"
REPOSITORIO = "lucas-leme/FinBERT-PT-BR"
VENV = RAIZ / "venv_finbert"
SERVICO = RAIZ / "scripts" / "finbert_servico.py"
LOG = RAIZ / "dados" / "execucao" / "log_finbert_servico.txt"
ESPERA_CARGA = 300      # segundos para o modelo carregar na primeira vez
ESPERA_MANCHETE = 60    # segundos para pontuar uma manchete


# ─────────────────────────────────────────────────────────
# No próprio processo (também é o que o serviço usa por dentro)
# ─────────────────────────────────────────────────────────

def carregar_local():
    """Devolve (tokenizer, modelo, rótulos) ou levanta a exceção original."""
    import torch  # noqa: F401  (o erro de DLL do Windows, quando existe, aparece aqui)
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    fonte = str(LOCAL) if (LOCAL / "config.json").exists() else REPOSITORIO
    tok = AutoTokenizer.from_pretrained(fonte)
    mod = AutoModelForSequenceClassification.from_pretrained(fonte)
    mod.eval()
    rotulos = [str(mod.config.id2label[i]).strip().lower() for i in range(mod.config.num_labels)]
    return tok, mod, rotulos


def pontuar_local(carregado, texto: str) -> dict:
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


# ─────────────────────────────────────────────────────────
# Ambiente separado (venv_finbert)
# ─────────────────────────────────────────────────────────

def python_do_ambiente_separado():
    for p in (VENV / "Scripts" / "python.exe", VENV / "bin" / "python"):
        if p.exists():
            return p
    return None


class Servico:
    """Um processo com o FinBERT carregado, que responde manchete por manchete.

    Conversa por linhas de texto em JSON: o painel escreve {"texto": ...} na
    entrada do processo e lê a resposta na saída. Mensagens de aviso das
    bibliotecas vão para dados/execucao/log_finbert_servico.txt.
    """

    def __init__(self, python: Path):
        LOG.parent.mkdir(parents=True, exist_ok=True)
        self._log = open(LOG, "w", encoding="utf-8")
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1",
                   HF_HUB_DISABLE_SYMLINKS_WARNING="1", TOKENIZERS_PARALLELISM="false")
        extra = {"creationflags": subprocess.CREATE_NO_WINDOW} if sys.platform == "win32" else {}
        self.proc = subprocess.Popen(
            [str(python), "-u", str(SERVICO)], cwd=RAIZ, env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._log,
            text=True, encoding="utf-8", errors="replace", bufsize=1, **extra)
        self._fila = queue.Queue()
        threading.Thread(target=self._ler_saida, daemon=True).start()
        self._trava = threading.Lock()
        primeira = self._resposta(ESPERA_CARGA)
        if "erro" in primeira:
            self.fechar()
            raise RuntimeError(primeira["erro"])
        self.info = primeira          # {"pronto": True, "python": ..., "torch": ...}

    def _ler_saida(self):
        for linha in self.proc.stdout:
            linha = linha.strip()
            if linha.startswith("{"):
                try:
                    self._fila.put(json.loads(linha))
                except json.JSONDecodeError:
                    pass
        self._fila.put({"erro": "o processo do FinBERT terminou. " + self._fim_do_log()})

    def _fim_do_log(self) -> str:
        try:
            self._log.flush()
            linhas = LOG.read_text(encoding="utf-8", errors="replace").strip().splitlines()
            return " | ".join(linhas[-3:])[-400:]
        except Exception:
            return ""

    def _resposta(self, espera):
        try:
            return self._fila.get(timeout=espera)
        except queue.Empty:
            return {"erro": f"o FinBERT não respondeu em {espera} s. " + self._fim_do_log()}

    def pontuar(self, texto: str) -> dict:
        with self._trava:
            if self.proc.poll() is not None:
                raise RuntimeError("o processo do FinBERT não está mais rodando. " + self._fim_do_log())
            self.proc.stdin.write(json.dumps({"texto": texto}, ensure_ascii=False) + "\n")
            self.proc.stdin.flush()
            r = self._resposta(ESPERA_MANCHETE)
        if "erro" in r:
            raise RuntimeError(r["erro"])
        return r

    def fechar(self):
        try:
            self.proc.kill()
        except Exception:
            pass


# ─────────────────────────────────────────────────────────
# O que a página usa
# ─────────────────────────────────────────────────────────

def carregar():
    """Escolhe o jeito de rodar: ambiente separado, se existir; senão, no próprio processo."""
    py = python_do_ambiente_separado()
    if py:
        return ("servico", Servico(py))
    return ("local", carregar_local())


def pontuar(carregado, texto: str) -> dict:
    modo, obj = carregado
    return obj.pontuar(texto) if modo == "servico" else pontuar_local(obj, texto)


def descricao(carregado) -> str:
    modo, obj = carregado
    if modo == "servico":
        return f"ambiente separado (venv_finbert) · Python {obj.info.get('python', '?')} · torch {obj.info.get('torch', '?')}"
    import torch
    return f"no próprio processo · torch {torch.__version__}"
