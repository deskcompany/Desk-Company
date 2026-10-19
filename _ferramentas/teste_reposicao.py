# -*- coding: utf-8 -*-
# Estoque > Reposicao: a barra de paginacao padrao no rodape da lista (ajuste do teste do usuario, 19/out/2026).
#
# A fila e derivada das bases de picking (18 de exemplo): sem semear nada ja ha duas paginas com 10 por pagina. A contagem e o
# "abaixo do minimo" do rodape somam o filtro inteiro; a pagina volta a 1 quando a aba, o deposito, a busca ou a ordem mudam.
# A tela nao tem planilha nem impressao (o menu so avisa que entram com Relatorios de Estoque): nao ha o que paginar nelas.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
REP = 'pagina-estoque-reposicao.html'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    cod = sys.stdout.encoding or 'utf-8'
    print((('  ok   ' if cond else '  FALHOU  ') + texto).encode(cod, 'replace').decode(cod))
    if not cond:
        falhas.append(texto)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir():
        pg.goto(localiza.uri(REP)); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(180)

    pag = lambda: pg.evaluate("[document.getElementById('paginacaoResumo').textContent, document.getElementById('paginacaoPaginas').textContent, document.getElementById('btnPaginaAnterior').disabled, document.getElementById('btnPaginaProxima').disabled]")
    n_linhas = lambda: pg.evaluate("document.querySelectorAll('#corpoTabela tr').length")
    txt = lambda i: pg.evaluate("document.getElementById('%s').textContent" % i)

    print('\n[1] A barra de paginacao padrao na lista de Reposicao')
    ir()
    ok(pg.evaluate("!!document.querySelector('.paginacao-bar #itensPorPagina') && !!document.querySelector('.paginacao-bar .paginacao-nav')"), 'o rodape tem a barra de paginacao padrao (seletor de quantidade e navegacao)')
    ok(pg.evaluate("[...document.querySelectorAll('#itensPorPagina .dropdown-select-item')].map(i => i.textContent)") == ['10', '25', '50', '100'] and
       pg.evaluate("document.querySelector('#itensPorPagina .dropdown-select-label').textContent") == '10', 'opcoes 10, 25, 50 e 100, padrao 10')
    ok(pg.evaluate("BASES.length") == 18 and txt('cTodos') == '18', 'a fila tem as 18 bases de picking de exemplo')
    ok(n_linhas() == 10 and pag() == ['Mostrando 1–10 de 18', 'Página 1 de 2', True, False], 'a primeira pagina tem 10 linhas: %s' % pag())
    abaixo = pg.evaluate("filaCompleta().filter(i => i.abaixo).length")
    ok(txt('contagemBases') == '18 endereços de picking' and txt('totalAbaixo') == str(abaixo) and abaixo > 0,
       'a contagem do rodape (18) e o "abaixo do minimo" (%d) sao do filtro inteiro: %s / %s' % (abaixo, txt('contagemBases'), txt('totalAbaixo')))
    clic('#btnPaginaProxima')
    ok(n_linhas() == 8 and pag() == ['Mostrando 11–18 de 18', 'Página 2 de 2', False, True] and txt('contagemBases') == '18 endereços de picking' and txt('totalAbaixo') == str(abaixo),
       'a segunda pagina tem as 8 que sobram, e o rodape nao muda: %s' % pag())
    clic('#btnPaginaProxima')
    ok(pag()[1] == 'Página 2 de 2', 'a proxima desligada nao passa da ultima')
    clic('#btnPaginaAnterior')
    ok(pag()[1] == 'Página 1 de 2', 'a anterior volta')
    clic('#itensPorPagina .dropdown-select-item[data-value="25"]')
    ok(n_linhas() == 18 and pag() == ['Mostrando 1–18 de 18', 'Página 1 de 1', True, True], 'com 25 por pagina, as 18 numa so e os dois botoes desligados')
    clic('#itensPorPagina .dropdown-select-item[data-value="10"]'); clic('#btnPaginaProxima')
    # cada filtro volta a pagina 1
    clic('#abasSituacao .aba-sit[data-aba="repor"]')
    repor = int(txt('cRepor'))
    ok(pag()[1] == 'Página 1 de %d' % max(1, -(-repor // 10)) and txt('contagemBases').startswith('%d ' % repor), 'clicar na aba "A repor" volta a pagina 1 e conta so as %d que dá para repor: %s' % (repor, pag()))
    clic('#abasSituacao .aba-sit[data-aba="todos"]'); clic('#btnPaginaProxima')
    pg.fill('#campoBusca', '-'); pg.wait_for_timeout(200)
    ok(pag() == ['Mostrando 1–10 de 18', 'Página 1 de 2', True, False], 'a busca que ainda deixa as 18 também volta à página 1: %s' % pag())
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(200); clic('#btnPaginaProxima')
    pg.fill('#campoBusca', 'cadeira'); pg.wait_for_timeout(200)
    achados = pg.evaluate("filaFiltrada().length")
    ok(pag()[0] == 'Mostrando 1–%d de %d' % (achados, achados) and pag()[1] == 'Página 1 de 1' and 0 < achados < 10, 'a busca volta a pagina 1 e a paginacao conta so o que ela deixa (%d): %s' % (achados, pag()))
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(200); clic('#btnPaginaProxima')
    clic('.estoque-table th.ordenavel[data-ordem="naBase"]')
    ok(pag()[1] == 'Página 1 de 2', 'ordenar por uma coluna volta a pagina 1')
    clic('#btnPaginaProxima')
    clic('#filtroDeposito .dropdown-select-item[data-value="2"]')
    dep2 = pg.evaluate("filaFiltrada().length")
    ok(pag() == ['Mostrando 1–%d de %d' % (dep2, dep2), 'Página 1 de 1', True, True] and dep2 == 10, 'trocar o deposito volta a pagina 1 e a paginacao acompanha o filtro (%d bases no Galpao Centro): %s' % (dep2, pag()))
    clic('#filtroDeposito .dropdown-select-item[data-value="todos"]')
    pg.fill('#campoBusca', 'zzz'); pg.wait_for_timeout(200)
    ok(pag() == ['Mostrando 0 de 0', 'Página 1 de 1', True, True] and n_linhas() == 0, 'sem resultado, "Mostrando 0 de 0" e os dois botoes desligados')
    # o padrao de abertura vem de Configuracoes
    pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ registrosPorPagina: 25 }))"); ir()
    ok(n_linhas() == 18 and pg.evaluate("document.querySelector('#itensPorPagina .dropdown-select-label').textContent") == '25', 'a quantidade de abertura e a de Configuracoes, Interface do usuario (25)')
    pg.evaluate("localStorage.removeItem('deskParametros')")
    ok(not erros, 'nenhum erro de JavaScript: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
