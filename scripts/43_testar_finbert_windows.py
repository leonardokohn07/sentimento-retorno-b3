# -*- coding: utf-8 -*-
"""
43_testar_finbert_windows.py — testa se o FinBERT-PT-BR roda neste computador.

NÃO calcula nada do estudo e NÃO altera nenhum arquivo de dados.
Roda num ambiente separado (venv_finbert), criado pelo TESTAR_FINBERT.bat,
para não mexer no venv principal, que é o ambiente da verificação (99 de 99).
Se este teste passar, o painel usa o mesmo ambiente para o FinBERT ao vivo
(modulos/finbert_vivo.py e scripts/finbert_servico.py).

Passos:
  1. mostra a versão do Python e tenta carregar o torch. Se falhar
     (ex.: WinError 1114 ao abrir c10.dll), mostra o erro completo e lista
     as DLLs do runtime do Visual C++ e do OpenMP que o Windows pode estar usando;
  2. acha o modelo em dados/modelos/finbert/arquivos (baixado pelo 30a).
     Se não achar, baixa do Hugging Face para essa mesma pasta;
  3. pontua 5 manchetes que já têm escore no estudo (dados/sentimento_finbert.csv,
     calculado no Linux) e compara. A diferença precisa ser praticamente zero:
     é a prova de que o FinBERT no Windows dá o mesmo resultado do estudo.

Uso: venv_finbert\\Scripts\\python scripts\\43_testar_finbert_windows.py
O resultado também fica em dados/execucao/log_finbert_windows.txt.
"""
import csv
import os
import platform
import sys
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ / "dados" / "modelos" / "finbert" / "arquivos"
REFERENCIA = RAIZ / "dados" / "sentimento_finbert.csv"
REPO = "lucas-leme/FinBERT-PT-BR"
TOLERANCIA = 1e-3   # diferença máxima aceita em cada probabilidade

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class _Duplo:
    """Escreve na tela e no arquivo de log ao mesmo tempo (como o comando tee)."""

    def __init__(self, *destinos):
        self.destinos = destinos

    def write(self, texto):
        for d in self.destinos:
            d.write(texto)
            d.flush()

    def flush(self):
        for d in self.destinos:
            d.flush()


_ARQ_LOG = RAIZ / "dados" / "execucao" / "log_finbert_windows.txt"
_ARQ_LOG.parent.mkdir(parents=True, exist_ok=True)
_log = open(_ARQ_LOG, "w", encoding="utf-8")
sys.stdout = _Duplo(sys.stdout, _log)
sys.stderr = _Duplo(sys.stderr, _log)


def procurar_dlls():
    """Lista as DLLs que costumam causar o WinError 1114 no torch."""
    nomes = {"libiomp5md.dll", "vcruntime140.dll", "vcruntime140_1.dll",
             "msvcp140.dll", "c10.dll", "vcomp140.dll"}
    lugares = [Path(sys.prefix)] + [Path(p) for p in os.environ.get("PATH", "").split(os.pathsep) if p]
    vistos = set()
    for base in lugares:
        try:
            if not base.is_dir() or base in vistos:
                continue
            vistos.add(base)
            arquivos = base.rglob("*.dll") if base == Path(sys.prefix) else base.glob("*.dll")
            for f in arquivos:
                if f.name.lower() in nomes:
                    print(f"   {f}  ({f.stat().st_size / 1e3:.0f} kB)")
        except Exception:
            pass


def baixar_modelo():
    """Mesma lógica do 30a: pesos + arquivos de configuração do repositório oficial."""
    from huggingface_hub import HfApi, snapshot_download
    arquivos = HfApi().list_repo_files(REPO)
    pesos = [a for a in arquivos if a.endswith(".safetensors") and "/" not in a]
    if not pesos:
        pesos = [a for a in arquivos if a == "pytorch_model.bin"]
    outros = [a for a in arquivos if "/" not in a and (
        a.endswith(".json") or a.endswith(".txt") or a.endswith(".model") or a == "README.md")]
    snapshot_download(repo_id=REPO, local_dir=PASTA, allow_patterns=pesos + outros)


def main():
    print("Python:     ", sys.version.replace("\n", " "))
    print("Sistema:    ", platform.platform())
    print("Executável: ", sys.executable)

    # ---------------------------------------------------------------- 1. torch
    print("\n[1] Carregando o torch...")
    try:
        import torch
    except Exception:
        traceback.print_exc()
        print("\n>>> O torch NÃO carregou. DLLs relevantes encontradas:")
        procurar_dlls()
        print("\n>>> Próximo passo: instalar o Visual C++ Redistributable x64 mais recente")
        print("    (https://aka.ms/vc14/vc_redist.x64.exe), reiniciar o PC e rodar este teste de novo.")
        return 1
    import transformers
    print(f"   torch {torch.__version__} OK | transformers {transformers.__version__} OK")

    # ---------------------------------------------------------------- 2. modelo
    print("\n[2] Modelo...")
    if not (PASTA / "config.json").exists():
        print(f"   não achei os arquivos em {PASTA}")
        print("   baixando do Hugging Face (algumas centenas de MB)...")
        baixar_modelo()
    for f in sorted(PASTA.iterdir()):
        if f.is_file():
            print(f"   {f.name:40s} {f.stat().st_size / 1e6:9.1f} MB")
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(str(PASTA))
    modelo = AutoModelForSequenceClassification.from_pretrained(str(PASTA))
    modelo.eval()
    rotulos = [str(modelo.config.id2label[i]).strip().lower().replace(" ", "_")
               for i in range(modelo.config.num_labels)]
    print(f"   rótulos do modelo: {rotulos}")

    def pontuar(texto):
        enc = tok([texto], padding=True, truncation=True, max_length=128, return_tensors="pt")
        with torch.inference_mode():
            p = torch.softmax(modelo(**enc).logits, dim=-1)[0].tolist()
        return dict(zip(rotulos, p))

    pos = next((r for r in rotulos if "pos" in r), None)
    neg = next((r for r in rotulos if "neg" in r), None)

    # ---------------------------------------------------- 3. confere com o estudo
    print("\n[3] Conferindo com os escores do estudo (calculados no Linux)...")
    ok = True
    if not REFERENCIA.exists():
        print(f"   não achei {REFERENCIA.relative_to(RAIZ)}; pulo a conferência.")
    else:
        with open(REFERENCIA, encoding="utf-8", newline="") as f:
            linhas = list(csv.DictReader(f))
        n = len(linhas)
        amostra = [linhas[i] for i in sorted({0, n // 4, n // 2, (3 * n) // 4, n - 1})]
        maior = 0.0
        for lin in amostra:
            calc = pontuar(lin["manchete"])
            dif = max(abs(calc[r] - float(lin[f"finbert_{r}"])) for r in rotulos)
            maior = max(maior, dif)
            print(f"   dif. máx. {dif:.2e} | {lin['manchete'][:70]}")
        ok = maior <= TOLERANCIA
        print(f"   >>> maior diferença: {maior:.2e} -> {'IGUAL AO ESTUDO' if ok else 'DIFERENTE DO ESTUDO'}")

    # ------------------------------------------------------------- demonstração
    print("\n[4] Demonstração (manchetes inventadas, só para teste):")
    for t in ["Petrobras dispara após lucro recorde no trimestre",
              "Vale despenca com queda do preço do minério",
              "Itaú divulga resultado do terceiro trimestre"]:
        p = pontuar(t)
        escore = (p[pos] - p[neg]) if pos and neg else float("nan")
        print(f"   escore {escore:+.3f} | {t}")

    print("\nRESULTADO:", "FINBERT FUNCIONANDO NESTE PC" if ok else "RODOU, MAS NÃO BATEU COM O ESTUDO")
    if ok:
        print("Agora reinicie o painel (Ctrl+C e streamlit run dashboard.py) e ligue")
        print("'Rodar o FinBERT-PT-BR ao vivo' na página 'Como medimos o sentimento'.")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
