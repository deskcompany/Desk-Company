# -*- coding: utf-8 -*-
# Impressao em formato de relatorio (item P1 — piloto em Ordens de Compra, 14/out/2026).
#
# Ate aqui a folha era o desenho da tela sem o menu: levava a caixa "Selecionar todos" e a seta de
# ordenacao, e nao dizia o que era, quando foi emitida nem que filtro estava valendo. Combinado com o
# usuario: o relatorio nasce numa lista so, para ele ver a folha, e depois vai para o bloco comum.
#
#   [1] na tela o cabecalho do relatorio nao aparece; no papel aparece, com titulo, data e quem emitiu;
#   [2] o cabecalho diz os filtros que estao valendo (aba, deposito, periodo, busca, indicador) e a
#       quantidade de registros, e diz "nenhum" quando nao ha filtro;
#   [3] o que so serve na tela nao vai para o papel; o cabecalho da tabela se repete a cada folha;
#   [4] "Imprimir", no menu, imprime a lista inteira com o cabecalho pronto; o Ctrl+P tambem o monta.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys, datetime
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
OC = 'pagina-estoque-ordens-compra.html'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    cod = sys.stdout.encoding or 'utf-8'
    print((('  ok   ' if cond else '  FALHOU  ') + texto).encode(cod, 'replace').decode(cod))
    if not cond:
        falhas.append(texto)


def secao(n, titulo):
    if SO and SO != str(n):
        return False
    print('\n[%d] %s' % (n, titulo))
    return True


HOJE = datetime.date.today().strftime('%d/%m/%Y')
CAB = "(document.getElementById('relatorioCabecalho') || { innerText: '' }).innerText"
VISIVEL = "(sel) => Array.from(document.querySelectorAll(sel)).filter(e => getComputedStyle(e).display !== 'none' && e.getClientRects().length > 0).length"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def abrir():
        pg.emulate_media(media='screen')
        pg.goto(localiza.uri(OC)); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def no_papel():
        pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        pg.emulate_media(media='print'); pg.wait_for_timeout(150)

    def linhas_na_tela():
        return pg.evaluate("Array.from(document.querySelectorAll('.main table tbody tr')).filter(tr => !tr.querySelector('[colspan]')).length")

    abrir(); pg.evaluate("localStorage.removeItem('deskParametros')")

    if secao(1, 'O cabeçalho do relatório só existe no papel'):
        abrir()
        ok(pg.evaluate(VISIVEL, '#relatorioCabecalho') == 0, 'antes de imprimir, a tela não tem cabeçalho de relatório')
        no_papel()
        cab = pg.evaluate(CAB)
        ok(pg.evaluate(VISIVEL, '#relatorioCabecalho') == 1 and 'Ordens de Compra' in cab and ('Emitido em ' + HOJE) in cab and 'Administrador Desk' in cab,
           'no papel, o cabeçalho diz a lista, a data de hoje e quem emitiu: %s' % cab.replace('\n', ' | ')[:150])
        pg.emulate_media(media='screen'); pg.wait_for_timeout(100)
        ok(pg.evaluate(VISIVEL, '#relatorioCabecalho') == 0, 'e volta a sumir na tela depois da impressão')

    if secao(2, 'Os filtros e a quantidade'):
        abrir(); no_papel()
        cab = pg.evaluate(CAB)
        ok('Filtros: nenhum, a lista inteira' in cab and ('%d registros' % linhas_na_tela()) in cab, 'sem filtro, o cabeçalho diz que é a lista inteira, e quantos registros: %s' % cab.split('\n')[-1])
        abrir()
        pg.evaluate("document.querySelector('.aba-sit[data-sit=\"aberto\"]').click()"); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('#filtroDeposito .dropdown-select-item[data-value=\"2\"]').click()"); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('.periodo-op[data-periodo=\"30\"]').click()"); pg.wait_for_timeout(150)
        pg.fill('#campoBusca', 'nordic'); pg.wait_for_timeout(250)
        no_papel()
        cab = pg.evaluate(CAB)
        n = linhas_na_tela()
        ok('Situação: Em aberto' in cab and 'Galpão Centro' in cab and 'Período: Últimos 30 dias' in cab and 'Busca: "nordic"' in cab,
           'com aba, depósito, período e busca, o cabeçalho diz os quatro: %s' % [l for l in cab.split('\n') if l.startswith('Filtros')])
        ok(('%d registro' % n) in cab and 'Todos' not in cab.split('Filtros:')[1], 'a quantidade é a das linhas que vão para o papel (%d), e o "todos" de cada filtro não aparece' % n)
        abrir()
        pg.evaluate("document.querySelector('.kpi-card[data-kpi=\"atrasadas\"]').click()"); pg.wait_for_timeout(200)
        no_papel()
        ok('Indicador: Atrasadas' in pg.evaluate(CAB), 'o indicador clicado também é filtro, e aparece')

    if secao(3, 'O que não vai para o papel'):
        abrir(); no_papel()
        fora = {sel: pg.evaluate(VISIVEL, sel) for sel in ['.sidebar-col', '.estoque-toolbar', '.abas-situacao', '.oc-kpis', '.selecionar-todos-row', '.page-header',
                                                          '.main td:has(> .item-checkbox)', '.main th .seta', '.main .sit-dot']}
        ok(not [s for s, v in fora.items() if v], 'menu, barra de filtros, abas, indicadores, "Selecionar todos", caixas de seleção e setas não vão para o papel: %s' % [s for s, v in fora.items() if v])
        ok(pg.evaluate(VISIVEL, '.main table tbody tr') == linhas_na_tela() > 3 and pg.evaluate(VISIVEL, '.main thead th') >= 7, 'a tabela vai inteira, com as colunas que têm título')
        ok(pg.evaluate("getComputedStyle(document.querySelector('.main thead')).display") == 'table-header-group', 'o cabeçalho da tabela se repete em cada folha')
        ok(pg.evaluate("getComputedStyle(document.querySelector('.main .badge-situacao')).backgroundColor") in ('rgba(0, 0, 0, 0)', 'transparent'), 'a situação vai como texto, sem a pílula colorida')
        larg = pg.evaluate("[document.querySelector('.main table').getBoundingClientRect().left, document.getElementById('relatorioCabecalho').getBoundingClientRect().left]")
        ok(abs(larg[0] - larg[1]) <= 2, 'a tabela começa alinhada com o cabeçalho: %s' % larg)

    if secao(4, 'Pelo menu e pelo Ctrl+P'):
        abrir()
        pg.evaluate("PLANILHA_PAGINA.por(5, 1); PLANILHA_REFAZ()"); pg.wait_for_timeout(150)
        na_pagina = linhas_na_tela()
        pg.evaluate("""(() => { window.__impressoes = []; window.print = () => { window.dispatchEvent(new Event('beforeprint'));
          window.__impressoes.push([document.getElementById('relatorioCabecalho').innerText, Array.from(document.querySelectorAll('.main table tbody tr')).filter(tr => !tr.querySelector('[colspan]')).length]); }; })()""")
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"imprimir\"]').click()"); pg.wait_for_timeout(300)
        imp = pg.evaluate('window.__impressoes')
        todas = pg.evaluate("ORDENS.length")
        ok(len(imp) == 1 and imp[0][1] == todas and ('%d registros' % todas) in imp[0][0] and na_pagina == 5 and linhas_na_tela() == 5,
           '"Imprimir" manda as %d ordens com o cabeçalho pronto, e a lista volta à página de 5: %s' % (todas, [(i[1]) for i in imp]))
        abrir()
        antes = linhas_na_tela()
        pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        ok('Ordens de Compra' in pg.evaluate(CAB) and linhas_na_tela() == todas and ('%d registros' % todas) in pg.evaluate(CAB) and antes < todas,
           'o Ctrl+P, que não passa pelo menu, também monta o cabeçalho e leva a lista inteira (%d linhas, e não as %d da página)' % (linhas_na_tela(), antes))
        pg.evaluate("window.dispatchEvent(new Event('afterprint'))"); pg.wait_for_timeout(150)
        ok(linhas_na_tela() == antes, 'e, depois da impressão, a lista volta à página que estava aberta')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
