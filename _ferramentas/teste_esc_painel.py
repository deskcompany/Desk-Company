# -*- coding: utf-8 -*-
# Esc fecha o painel lateral, em toda tela (13/out/2026).
#
# O usuario relatou que o Esc nao funcionava em nenhum painel lateral de Cadastros. Medido nas 81
# telas: eram 42 paineis em 6 modulos. Cada tela escrevia o proprio tratamento da tecla, e a maioria
# so fechava o modal de confirmacao, embora o painel mostre "ESC" ao lado de fechar. O conserto e de
# componente: um bloco comum, na fase de captura, em que o Esc vale como clicar no "fechar" do painel.
#
#   [1] toda tela com painel na marcacao tem o bloco, com o mesmo texto, antes do bloco do dropdown;
#   [2] todo painel de toda tela fecha com Esc, e a tela continua no mesmo endereco;
#   [3] o que esta por cima fecha primeiro: com menu de dropdown ou modal aberto, o Esc nao fecha o
#       painel; fechado o menu, o Esc seguinte fecha o painel;
#   [4] pelo caminho de quem usa, nas listas de Cadastros: clicar na linha abre o painel, Esc fecha.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

MARCA = '  // ===== ESC FECHA O PAINEL LATERAL (correcao de COMPONENTE, nao de tela — 13/out/2026) ====='
DROPDOWN = '  // ===== ESC FECHA O DROPDOWN ABERTO (correcao de COMPONENTE, nao de tela — §13) ====='
CADASTROS = ['fornecedores', 'clientes', 'produtos', 'marcas', 'categorias', 'embalagens', 'vendedores', 'lojas-desk', 'departamento-produtos', 'secao-produtos', 'depositos']
SO = (sys.argv[1:] or [''])[0]
PARCIAL = bool(_os.environ.get('DESK_ALVOS', '').strip())

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


def bloco(t):
    a = t.index(MARCA)
    return t[a:t.index('  }, true);', a)]


todas = {_os.path.basename(c): open(c, encoding='utf-8').read() for c in localiza.caminhos()}
com_painel = sorted(n for n in todas if 'class="event-drawer' in todas[n])
alvos = [_os.path.basename(c) for c in _filtrar([localiza.onde(n) for n in com_painel])]

# Abre o painel `i` pela classe, como a tela faz, e devolve quantos paineis ela tem.
ABRE = """(i) => { const ps = Array.from(document.querySelectorAll('.event-drawer'));
  document.querySelectorAll('.event-drawer.open, .dropdown-select-menu.open, .modal-card.open').forEach(e => e.classList.remove('open'));
  if (ps[i]) ps[i].classList.add('open');
  return ps.length; }"""
ABERTO = "(i) => document.querySelectorAll('.event-drawer')[i].classList.contains('open')"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela):
        pg.goto(localiza.uri(tela)); pg.wait_for_load_state('load'); pg.wait_for_timeout(200)

    if secao(1, 'O bloco está em toda tela que tem painel'):
        sem = [n for n in com_painel if MARCA not in todas[n]]
        ok(len(com_painel) >= 60 and not sem, 'as %d telas com painel lateral têm o bloco "Esc fecha o painel": %s' % (len(com_painel), sem[:4]))
        textos = set(bloco(todas[n]) for n in com_painel if MARCA in todas[n])
        ok(len(textos) == 1, 'e o texto do bloco é o mesmo em todas (%d versão)' % len(textos))
        fora = [n for n in com_painel if MARCA in todas[n] and DROPDOWN in todas[n] and not todas[n].index(MARCA) < todas[n].index(DROPDOWN)]
        ok(not fora, 'ele vem antes do bloco do dropdown, para decidir primeiro quem está por cima: %s' % fora[:4])
        molde = todas.get('pagina-molde-referencia.html', '')
        executa = molde[molde.index('\n<script>\n'):molde.index('</script>', molde.index('\n<script>\n'))] if molde else ''
        ok(not molde or MARCA in executa, 'no molde, que as telas novas copiam, o bloco está no script que executa, e não só na referência em comentário')

    if secao(2, 'Todo painel fecha com Esc'):
        presos, saiu, paineis = [], [], 0
        for tela in alvos:
            ir(tela)
            url = pg.url
            for i in range(pg.evaluate(ABRE, 0)):
                pg.evaluate(ABRE, i)
                pg.keyboard.press('Escape'); pg.wait_for_timeout(60)
                paineis += 1
                if pg.evaluate(ABERTO, i): presos.append('%s#%d' % (tela.replace('pagina-', '').replace('.html', ''), i))
                if pg.url != url: saiu.append(tela); ir(tela)
        ok((PARCIAL or paineis >= 85) and not presos, 'os %d painéis das %d telas fecham com Esc: %s' % (paineis, len(alvos), presos[:5]))
        ok(not saiu, 'e o Esc não tira ninguém da tela: %s' % saiu[:4])

    if secao(3, 'O que está por cima fecha primeiro'):
        menus, modais, por_baixo, travou, com_modal = 0, 0, [], [], []
        # Cada painel de cada tela, com cada modal que a tela tem: seis telas tinham um tratamento proprio
        # de Esc que so conhecia o modal de confirmacao e fechava o painel com um aviso na frente.
        for tela in alvos:
            ir(tela)
            n_paineis = pg.evaluate(ABRE, 0)
            n_modais = pg.evaluate("document.querySelectorAll('.modal-card').length")
            tem_menu = DROPDOWN in todas[tela] and pg.evaluate("!!document.querySelector('.dropdown-select-menu')")
            for i in range(n_paineis):
                nome = tela.replace('pagina-', '').replace('.html', '') + '#%d' % i
                if tem_menu:
                    pg.evaluate(ABRE, i)
                    pg.evaluate("document.querySelector('.dropdown-select-menu').classList.add('open')")
                    pg.keyboard.press('Escape'); pg.wait_for_timeout(50)
                    menus += 1
                    if not pg.evaluate(ABERTO, i) or pg.evaluate("!!document.querySelector('.dropdown-select-menu.open')"): por_baixo.append(nome)
                    pg.keyboard.press('Escape'); pg.wait_for_timeout(50)
                    if pg.evaluate(ABERTO, i): travou.append(nome)
                for m in range(n_modais):
                    pg.evaluate(ABRE, i)
                    pg.evaluate("(m) => document.querySelectorAll('.modal-card')[m].classList.add('open')", m)
                    pg.keyboard.press('Escape'); pg.wait_for_timeout(50)
                    modais += 1
                    if not pg.evaluate(ABERTO, i): com_modal.append(nome + ' modal %d' % m)
        ok((PARCIAL or menus >= 60) and not por_baixo, 'em %d painéis, com um menu aberto o Esc fecha o menu e deixa o painel: %s' % (menus, por_baixo[:5]))
        ok(not travou, 'e o Esc seguinte fecha o painel: %s' % travou[:5])
        ok((PARCIAL or modais >= 100) and not com_modal, 'em %d combinações de painel e modal, com o modal por cima o Esc não fecha o painel: %s' % (modais, com_modal[:6]))

    if secao(4, 'Pelo caminho de quem usa, nas listas de Cadastros'):
        ruins = []
        for c in CADASTROS:
            tela = 'pagina-cadastros-%s.html' % c
            if tela not in alvos: continue
            ir(tela)
            url = pg.url
            pg.click('.main [class$="-nome-row"]'); pg.wait_for_timeout(350)
            abriu = pg.locator('.event-drawer.open').count() == 1
            pg.keyboard.press('Escape'); pg.wait_for_timeout(350)
            fechou = pg.locator('.event-drawer.open').count() == 0 and pg.locator('.drawer-backdrop.open').count() == 0
            if not (abriu and fechou and pg.url == url): ruins.append('%s (abriu %s, fechou %s)' % (c, abriu, fechou))
        ok(not ruins, 'nas listas de Cadastros, clicar na linha abre o painel e o Esc fecha, com o fundo escuro junto: %s' % ruins[:4])
        if 'pagina-cadastros-fornecedores.html' in alvos:
            ir('pagina-cadastros-fornecedores.html')
            pg.click('.main [class$="-nome-row"]'); pg.wait_for_timeout(350)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            pg.click('.main [class$="-nome-row"]'); pg.wait_for_timeout(350)
            ok(pg.locator('.event-drawer.open').count() == 1, 'depois de fechar com Esc, o painel abre de novo normalmente')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
