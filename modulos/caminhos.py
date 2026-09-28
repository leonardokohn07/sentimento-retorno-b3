"""
caminhos.py
-----------
Define, em UM ÚNICO LUGAR, onde cada arquivo do projeto fica salvo.

Por que isso existe?
    Sem este módulo, cada script salvaria arquivo na pasta em que foi
    executado. Rodar o dashboard da raiz e um script de dentro de scripts/
    criaria DUAS cópias do mesmo CSV em pastas diferentes — e você perderia
    tempo procurando qual é a atual.

    Aqui os caminhos são sempre ABSOLUTOS, calculados a partir da posição
    deste arquivo. Não importa de onde você rode: os dados vão sempre para
    InvestAI/dados/ e os resultados para InvestAI/resultados/.

Como usar:
    from modulos.caminhos import ARQ_NOTICIAS, PASTA_RESULTADOS
    df.to_csv(ARQ_NOTICIAS, index=False)
"""

from pathlib import Path

# ─────────────────────────────────────────────────────────
# PASTAS
# ─────────────────────────────────────────────────────────
# Este arquivo está em InvestAI/modulos/caminhos.py
# .parent      -> modulos/
# .parent.parent -> InvestAI/   (a raiz do projeto)

RAIZ = Path(__file__).resolve().parent.parent

PASTA_MODULOS = RAIZ / "modulos"
PASTA_SCRIPTS = RAIZ / "scripts"
PASTA_DADOS = RAIZ / "dados"
PASTA_RESULTADOS = RAIZ / "resultados"

# Cria as pastas de saída se ainda não existirem
for _pasta in (PASTA_DADOS, PASTA_RESULTADOS):
    _pasta.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────────
# ARQUIVOS DE DADOS (entrada / cache)
# ─────────────────────────────────────────────────────────

ARQ_NOTICIAS = PASTA_DADOS / "noticias_com_sentimento.csv"


# ─────────────────────────────────────────────────────────
# ARQUIVOS DE RESULTADO (saída)
# ─────────────────────────────────────────────────────────

ARQ_RESULTADO_HIPOTESE = PASTA_RESULTADOS / "resultado_hipotese.json"
ARQ_RESULTADO_PERMUTACAO = PASTA_RESULTADOS / "resultado_permutacao.txt"


def grafico(nome: str) -> Path:
    """
    Caminho de um gráfico dentro de resultados/.

    Exemplo:
        plt.savefig(grafico("dispersao_PETR4.png"))
    """
    return PASTA_RESULTADOS / nome


def listar_saidas() -> None:
    """Imprime o que já foi gerado — útil para conferir o andamento."""
    print(f"\nRaiz do projeto: {RAIZ}\n")
    for pasta, rotulo in [
        (PASTA_DADOS, "dados"),
        (PASTA_RESULTADOS, "resultados"),
    ]:
        arquivos = sorted(p for p in pasta.iterdir() if p.is_file()
                          and not p.name.startswith("."))
        print(f"  {rotulo}/")
        if not arquivos:
            print("    (vazio)")
        for a in arquivos:
            tamanho = a.stat().st_size / 1024
            print(f"    {a.name:38s} {tamanho:8.1f} KB")
        print()


if __name__ == "__main__":
    listar_saidas()
