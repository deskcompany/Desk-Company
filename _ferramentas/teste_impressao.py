# -*- coding: utf-8 -*-
# Impressao em formato de relatorio (item P1 — piloto em Ordens de Compra, 14/out/2026; aprovado pelo
# usuario no mesmo dia e levado ao bloco comum das 19 telas que tem planilha e impressao).
#
# Ate aqui a folha era o desenho da tela sem o menu: levava a caixa "Selecionar todos" e a seta de
# ordenacao, e nao dizia o que era, quando foi emitida nem que filtro estava valendo. Combinado com o
# usuario: o relatorio nasce numa lista so, para ele ver a folha, e depois vai para o bloco comum.
#
#   [1] na tela o cabecalho do relatorio nao aparece; no papel aparece, com titulo, data e quem emitiu;
#   [2] o cabecalho diz os filtros que estao valendo (aba, deposito, periodo, busca, indicador) e a
#       quantidade de registros, e diz "nenhum" quando nao ha filtro;
#   [3] o que so serve na tela nao vai para o papel; o cabecalho da tabela se repete a cada folha;
#   [4] "Imprimir", no menu, imprime a lista inteira com o cabecalho pronto; o Ctrl+P tambem o monta;
#   [5] em cada uma das 19 telas: o cabecalho no papel, a quantidade, nada de caixa de selecao, colunas
#       alinhadas, o Ctrl+P levando a lista inteira e o CSS do relatorio igual em todas;
#   [6] em cada lista, o filtro escolhido aparece no cabecalho.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys, datetime
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
OC = 'pagina-estoque-ordens-compra.html'
MARCA = '  // ===== PLANILHA E IMPRESSAO DA TELA (bloco compartilhado, 10/out/2026) ====='
MARCA_CSS = '  /* ===== RELATORIO NA IMPRESSAO (bloco comum, aprovado pelo usuario em 14/out/2026) ====='
FONTES = {_os.path.basename(c): open(c, encoding='utf-8').read() for c in localiza.caminhos()}
COM_BLOCO = sorted(n for n, f in FONTES.items() if MARCA in f)

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

    # Quantas linhas a tela vai mandar para o papel, contadas sem passar pelo codigo do relatorio.
    CONTA = """() => { if (typeof linhasDaPlanilha === 'function') return linhasDaPlanilha().linhas.length;
      const tab = Array.from(document.querySelectorAll('.main table')).filter(e => e.offsetParent !== null)[0];
      return tab ? Array.from(tab.querySelectorAll('tbody tr')).filter(tr => !tr.querySelector('[colspan]')).length : 0; }"""
    ALINHA = """() => Array.from(document.querySelectorAll('.main table')).filter(tb => tb.getClientRects().length && tb.querySelector('tbody tr td:not([colspan])')).map(tb => {
      const vis = (e) => getComputedStyle(e).display !== 'none';
      const linha = Array.from(tb.querySelectorAll('tbody tr')).filter(tr => !tr.querySelector('[colspan]'))[0];
      return [Array.from(tb.querySelectorAll('thead tr:last-child th')).filter(vis).length, Array.from(linha.children).filter(vis).length]; }).filter(p => p[0] && p[0] !== p[1])"""

    if secao(5, 'As 23 telas com o bloco comum'):
        ok(len(COM_BLOCO) == 23, 'são %d telas com o bloco comum de planilha e impressão' % len(COM_BLOCO))
        css = set(FONTES[n][FONTES[n].index(MARCA_CSS):FONTES[n].index('</style>')] if MARCA_CSS in FONTES[n] else '' for n in COM_BLOCO)
        ok(len(css) == 1 and '' not in css, 'o CSS do relatório está em todas, igual')
        ruins, listas, docs = [], 0, 0
        for nome in COM_BLOCO:
            pg.emulate_media(media='screen')
            pg.goto(localiza.uri(nome)); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
            lista = pg.evaluate('!!PLANILHA_REFAZ')
            antes = pg.evaluate(CONTA)
            paginada = pg.evaluate('!!PLANILHA_PAGINA')
            no_papel()
            cab, n = pg.evaluate(CAB), pg.evaluate(CONTA)
            h1 = pg.evaluate("document.querySelector('.main h1').textContent.trim()")
            curto = nome.replace('pagina-', '').replace('.html', '')
            if ('Emitido em ' + HOJE) not in cab or pg.evaluate(VISIVEL, '#relatorioCabecalho') != 1:
                ruins.append('%s: sem cabeçalho no papel' % curto)
            if lista:
                listas += 1
                if h1 not in cab or 'Filtros: ' not in cab or (('%d registros' % n) not in cab and not (n == 1 and '1 registro' in cab)):
                    ruins.append('%s: cabeçalho de lista incompleto (%d linhas): %s' % (curto, n, cab.replace(chr(10), ' | ')[:120]))
                if pg.evaluate(VISIVEL, '.main .page-header') != 0:
                    ruins.append('%s: o cabeçalho da tela foi para o papel junto com o do relatório' % curto)
                if paginada and n < antes:
                    ruins.append('%s: o Ctrl+P imprimiu menos do que a tela tinha (%d de %d)' % (curto, n, antes))
            else:
                docs += 1
                if 'Filtros' in cab or pg.evaluate(VISIVEL, '.main .page-header') != 1:
                    ruins.append('%s: página de documento com filtro no cabeçalho, ou sem o título dela' % curto)
            if pg.evaluate(VISIVEL, '.sidebar-col') or pg.evaluate(VISIVEL, '.main td:has(> .item-checkbox)'):
                ruins.append('%s: menu ou caixa de seleção no papel' % curto)
            desal = pg.evaluate(ALINHA)
            if desal:
                ruins.append('%s: colunas desalinhadas (títulos x células): %s' % (curto, desal))
            pg.evaluate("window.dispatchEvent(new Event('afterprint'))"); pg.wait_for_timeout(150)
            pg.emulate_media(media='screen'); pg.wait_for_timeout(100)
            if lista and paginada and pg.evaluate(CONTA) != antes:
                ruins.append('%s: depois da impressão a lista não voltou à página (%d, era %d)' % (curto, pg.evaluate(CONTA), antes))
        ok(not ruins, 'nas %d listas e nos %d documentos: cabeçalho no papel, quantidade, sem caixa de seleção, colunas alinhadas e a página de volta: %s' % (listas, docs, ruins[:4]))
        # 14/out: Comissoes Afiliados (lista) e a conta do afiliado (documento) entraram com o bloco.
        # 19/out: Vale-compra (a lista e a pagina do vale) entrou com o bloco.
        ok(listas == 17 and docs == 6, 'as listas são 17 e os documentos, 6 (%d e %d)' % (listas, docs))

    if secao(6, 'Em cada lista, o filtro escolhido aparece'):
        ruins, conferidas = [], 0
        for nome in COM_BLOCO:
            pg.emulate_media(media='screen')
            pg.goto(localiza.uri(nome)); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
            if not pg.evaluate('!!PLANILHA_REFAZ'):
                continue
            escolhido = pg.evaluate("""() => {
              const semFiltro = (s) => !s || /\\b(todos|todas)\\b|^sem filtro|^qualquer|^ordenar/i.test(s);
              const rot = (e) => { const c = e.cloneNode(true); c.querySelectorAll('[class*="contador"]').forEach(x => x.remove()); return c.textContent.replace(/[0-9]+$/, '').replace(/\\s+/g, ' ').trim(); };
              const opcoes = Array.from(document.querySelectorAll('.main [class*="abas"] > :not(.active), .main [class$="-toolbar"] [data-filtro]:not(.active)')).filter(e => !semFiltro(rot(e)));
              if (!opcoes.length) return null;
              opcoes[0].click(); return rot(opcoes[0]); }""")
            if escolhido is None:
                continue
            pg.wait_for_timeout(200); no_papel()
            conferidas += 1
            filtros = [l for l in pg.evaluate(CAB).split(chr(10)) if l.startswith('Filtros')]
            if not filtros or escolhido not in filtros[0]:
                ruins.append('%s: escolhi "%s" e o cabeçalho diz %s' % (nome.replace('pagina-', '').replace('.html', ''), escolhido, filtros))
            pg.evaluate("window.dispatchEvent(new Event('afterprint'))")
        ok(not ruins and conferidas >= 12, 'em %d listas, o filtro escolhido (aba ou botão) aparece no cabeçalho do papel: %s' % (conferidas, ruins[:3]))

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
