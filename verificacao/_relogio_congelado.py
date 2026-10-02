# -*- coding: utf-8 -*-
"""
_relogio_congelado.py — roda UM script do projeto com o relógio parado.

Uso (quem chama é o verificar_tudo.py):
    python verificacao/_relogio_congelado.py scripts/25_fase_causal.py --medida finbert

Por que existe:
    Os scripts põem a data do dia no nome dos arquivos de resultado
    (fase_causal_2026-10-02.txt) e em linhas como "Gerado em 02/10/2026 14:31".
    Se a verificação rodar em outro dia, os nomes e essas linhas mudam, e a
    comparação com a referência falharia por um motivo bobo.

    Aqui, date.today() e datetime.now() passam a responder sempre
    02/10/2026 12:00, como um relógio parado. NADA mais muda: os dados, as
    contas e as sementes aleatórias são os do próprio script.

    Truque técnico: as classes falsas usam uma metaclasse para que
    isinstance(x, datetime) continue dando True para datas de verdade (é o
    mesmo truque da biblioteca freezegun).
"""
import datetime as _dt
import os
import runpy
import sys
from pathlib import Path

# As bibliotecas são importadas ANTES de parar o relógio: elas guardam as
# classes de data verdadeiras e funcionam normalmente. Só o código do projeto,
# importado depois, vê o relógio parado.
os.environ.setdefault("MPLBACKEND", "Agg")
for _mod in ("numpy", "pandas", "scipy.stats", "matplotlib.pyplot", "matplotlib.dates"):
    try:
        __import__(_mod)
    except ImportError:
        pass

AGORA = (2026, 10, 2, 12, 0, 0)          # 02/10/2026 12:00, horário de Brasília

_DataReal, _DataHoraReal = _dt.date, _dt.datetime


class _MetaData(type):
    def __instancecheck__(cls, obj):
        return isinstance(obj, _DataReal)

    def __subclasscheck__(cls, sub):
        return issubclass(sub, _DataReal)


class _MetaDataHora(type):
    def __instancecheck__(cls, obj):
        return isinstance(obj, _DataHoraReal)

    def __subclasscheck__(cls, sub):
        return issubclass(sub, _DataHoraReal)


class _Data(_DataReal, metaclass=_MetaData):
    def __new__(cls, *a, **k):
        return _DataReal(*a, **k)

    @classmethod
    def today(cls):
        return _DataReal(*AGORA[:3])


class _DataHora(_DataHoraReal, metaclass=_MetaDataHora):
    def __new__(cls, *a, **k):
        return _DataHoraReal(*a, **k)

    @classmethod
    def now(cls, tz=None):
        local = _DataHoraReal(*AGORA)
        if tz is None:
            return local
        brasilia = _dt.timezone(_dt.timedelta(hours=-3))
        return local.replace(tzinfo=brasilia).astimezone(tz)

    @classmethod
    def today(cls):
        return cls.now()

    @classmethod
    def utcnow(cls):
        return _DataHoraReal(*AGORA) + _dt.timedelta(hours=3)


_dt.date = _Data
_dt.datetime = _DataHora

if __name__ == "__main__":
    script = Path(sys.argv[1]).resolve()
    sys.argv = [str(script)] + sys.argv[2:]
    sys.path[0] = str(script.parent)        # igual a "python scripts/x.py"
    os.environ.setdefault("MPLBACKEND", "Agg")
    runpy.run_path(str(script), run_name="__main__")
