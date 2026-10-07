# -*- coding: utf-8 -*-
# Filtro de alvos — 30/set/2026.
#
# As suites que varrem a pasta inteira (`glob('pagina-*.html')`) passam a
# respeitar a variavel de ambiente DESK_ALVOS. Com ela preenchida, a suite roda
# SO nas telas listadas; vazia ou ausente, roda em tudo, exatamente como antes.
#
# Quem preenche e o `selo.py`: quando 3 telas mudaram, nao ha por que reabrir as
# 52. Rodar a suite inteira a cada mudanca e o que fazia a verificacao demorar
# tanto que ela passava a ser pulada — e teste que se pula nao protege nada.
import os


def filtrar(arquivos):
    """Restringe uma lista de caminhos ao que DESK_ALVOS pedir (por basename)."""
    bruto = os.environ.get('DESK_ALVOS', '').strip()
    if not bruto:
        return arquivos
    quero = set(p.strip() for p in bruto.split(',') if p.strip())
    return [a for a in arquivos if os.path.basename(a) in quero]
