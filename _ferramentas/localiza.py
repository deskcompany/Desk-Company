# -*- coding: utf-8 -*-
# Onde mora cada tela — 08/out/2026.
#
# Ate hoje as 71 telas ficavam soltas na raiz do projeto, e cada suite achava a
# sua com `glob('pagina-*.html')` ou `os.path.abspath('pagina-x.html')`. As telas
# agora moram em `telas/<modulo>/`, e este arquivo e o UNICO lugar que sabe disso.
#
# O nome do arquivo continua unico no sistema inteiro (`pagina-vendas-metas.html`
# existe uma vez so). Por isso as suites seguem citando a tela pelo NOME, e
# perguntam aqui onde ela esta. Mudar uma tela de pasta nao exige tocar em suite.
#
# Tres formas de pedir a mesma tela:
#   localiza.onde('pagina-vendas-metas.html')   caminho absoluto no disco
#   localiza.uri('pagina-vendas-metas.html?id=3')   endereco file:// para o navegador
#   localiza.http('pagina-vendas-metas.html')   endereco no servidor de preview
import glob
import os
import pathlib
import shutil
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.environ.get('DESK_PASTA') or os.path.dirname(AQUI)
TELAS = os.path.join(RAIZ, 'telas')
SERVIDOR = 'http://localhost:3000/'


def _mapa():
    m = {}
    for c in glob.glob(os.path.join(TELAS, '*', 'pagina-*.html')):
        n = os.path.basename(c)
        if n in m:
            raise SystemExit('localiza: %s existe em duas pastas (%s e %s). O nome da tela e unico.' % (
                n, os.path.basename(os.path.dirname(m[n])), os.path.basename(os.path.dirname(c))))
        m[n] = os.path.abspath(c)
    return m


def nomes():
    """Nomes de todas as telas, em ordem alfabetica — a ordem do glob antigo."""
    return sorted(_mapa())


def caminhos():
    """Caminho absoluto de todas as telas, na mesma ordem de nomes()."""
    m = _mapa()
    return [m[n] for n in sorted(m)]


def existe(nome):
    return os.path.basename(nome) in _mapa()


def _partes(alvo):
    """Separa 'pagina-x.html?id=1' em nome e resto. Aceita caminho no lugar do nome."""
    resto = ''
    for sep in ('?', '#'):
        i = alvo.find(sep)
        if i >= 0:
            alvo, resto = alvo[:i], alvo[i:] + resto
    return os.path.basename(alvo.replace(chr(92), '/')), resto


def onde(alvo):
    """Caminho absoluto da tela. Falha alto se ela nao existe: tela citada que
    sumiu e defeito, e um caminho inventado faria a suite testar coisa nenhuma."""
    n, _ = _partes(alvo)
    m = _mapa()
    if n not in m:
        raise SystemExit('localiza: a tela %s nao existe em telas/. Foi renomeada ou removida?' % n)
    return m[n]


def pasta(alvo):
    """Nome da pasta (modulo) em que a tela mora."""
    return os.path.basename(os.path.dirname(onde(alvo)))


def uri(alvo):
    """Endereco file:// na forma do navegador (barras e %20), com a query junto."""
    _, resto = _partes(alvo)
    return pathlib.Path(onde(alvo)).as_uri() + resto


def http(alvo):
    """Endereco da tela no servidor de preview (`node servidor.js`)."""
    n, resto = _partes(alvo)
    return SERVIDOR + pasta(alvo) + '/' + n + resto


def nome(endereco):
    """De um href, data-href ou URL do navegador, so o arquivo e a query:
    '../vendas/pagina-vendas-metas.html?id=3' -> 'pagina-vendas-metas.html?id=3'.
    E o que as suites comparam; a pasta e conferida por quem navega de verdade."""
    if not endereco:
        return endereco
    return endereco.replace(chr(92), '/').split('/')[-1]


def resolve(href, de):
    """Caminho no disco para onde um href relativo aponta, a partir da tela `de`."""
    limpo = href.split('?')[0].split('#')[0]
    return os.path.normpath(os.path.join(os.path.dirname(onde(de)), limpo))


def espelho_plano():
    """Copia as telas para UMA pasta so, com os links de volta ao formato antigo.

    Existe por causa da auditoria oficial da skill: ela mora fora deste projeto,
    varre `pagina-*.html` numa pasta unica e compara as telas entre si. Enquanto
    a skill nao aprender a estrutura por modulo, ela audita este espelho — que e
    o mesmo HTML, o mesmo CSS e o mesmo JS, so com o endereco das vizinhas sem a
    pasta. Nada aqui e fonte: o espelho e refeito a cada chamada.
    """
    import re
    dest = os.path.join(tempfile.gettempdir(), 'desk-erp-espelho-plano')
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(dest)
    vizinha = re.compile('[.][.]/[a-z_]+/(pagina-[a-z0-9-]+[.]html)')
    for c in caminhos():
        with open(c, encoding='utf-8', newline='') as f:
            t = f.read()
        t = vizinha.sub(lambda m: m.group(1), t).replace("url('../fontes/", "url('fontes/")
        with open(os.path.join(dest, os.path.basename(c)), 'w', encoding='utf-8', newline='') as f:
            f.write(t)
    fontes = os.path.join(TELAS, 'fontes')
    if os.path.isdir(fontes):
        shutil.copytree(fontes, os.path.join(dest, 'fontes'))
    return dest


if __name__ == '__main__':
    por_pasta = {}
    for c in caminhos():
        por_pasta.setdefault(os.path.basename(os.path.dirname(c)), []).append(os.path.basename(c))
    for p in sorted(por_pasta):
        print('%-14s %2d tela(s)' % (p, len(por_pasta[p])))
    print('%-14s %2d' % ('total', len(nomes())))
