# -*- coding: utf-8 -*-
# As setas do teclado em toda busca que abre sugestoes (13/out/2026).
#
# Decisao do usuario, depois de fechar o padrao de busca: lista que ja esta na tela filtra enquanto se
# digita; escolher um item para agir abre sugestoes. No segundo jeito, so o PDV deixava andar pela
# lista com as setas; nas outras cinco telas o Enter escolhia sempre o primeiro. O conserto e de
# componente: um bloco comum que so mexe na marcacao (a seta move a classe `ativo`, o Enter clica no
# item ativo), e cada tela continua dona de escolher o item.
#
#   [1] toda tela que tem a caixa de sugestoes tem o bloco, com o mesmo texto;
#   [2] em cada uma: a lista abre com o primeiro item ativo; seta para baixo e para cima andam um a
#       um, com um ativo so, e dao a volta no fim; o texto digitado fica; Enter escolhe o item ativo,
#       e nao o primeiro; com a lista fechada as setas nao fazem nada;
#   [3] na Movimentacao de Estoque, pelo resultado: descer uma vez e dar Enter poe no campo o segundo
#       produto da lista.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

MARCA = '  // ===== SETAS NA BUSCA COM SUGESTOES (correcao de COMPONENTE, nao de tela — 13/out/2026) ====='
# Como se chega a busca de cada tela: o que abrir antes, o campo, e um texto que traz varios produtos.
BUSCAS = [
    ('pagina-estoque-acerto.html', '', None, '#campoBuscaProduto', 'desk'),
    # A busca da transferencia so libera com origem e destino escolhidos.
    ('pagina-estoque-transferencia-nova.html', '', "(() => { document.querySelector('#campoOrigemDep .dropdown-select-item[data-value=\"2\"]').click();"
     " const d = Array.from(document.querySelectorAll('#campoDestinoDep .dropdown-select-item')).find(x => x.getAttribute('data-value') && x.getAttribute('data-value') !== '2' && !x.classList.contains('disabled'));"
     " d.click(); })()", '#campoBuscaProduto', 'e'),
    ('pagina-estoque-itens-bloqueados.html', '', "document.getElementById('btnBloquearItem').click()", '#bloqBusca', 'desk'),
    ('pagina-estoque-movimentacao.html', '', None, '#buscaProduto', 'desk'),
    ('pagina-cadastros-fornecedores-detalhe.html', '?editar=1', "document.querySelector('.tab-item[data-tab=\"produtos\"]').click()", '#pfBusca', 'a'),
]
SO = (sys.argv[1:] or [''])[0]

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


# O estado da lista de sugestoes que esta aberta junto do campo.
LISTA = """(campo) => { const w = document.querySelector(campo).closest('.busca-produto-wrap'); const c = w ? w.querySelector('.sugestoes.open') : null;
  const itens = c ? Array.from(c.querySelectorAll('.sugestao-item')) : [];
  return { n: itens.length, ativos: itens.map((x, i) => x.classList.contains('ativo') ? i : -1).filter(i => i >= 0),
           chaves: itens.map(x => x.getAttribute('data-id') || x.getAttribute('data-sku')), foco: document.activeElement === document.querySelector(campo) }; }"""
VIGIA = """(campo) => { window.__clicou = null; const w = document.querySelector(campo).closest('.busca-produto-wrap');
  w.querySelectorAll('.sugestoes.open .sugestao-item').forEach(x => x.addEventListener('click', () => { window.__clicou = x.getAttribute('data-id') || x.getAttribute('data-sku'); })); }"""

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def abrir(tela, query, prepara, campo, termo):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        if prepara:
            pg.evaluate(prepara); pg.wait_for_timeout(400)
        pg.fill(campo, termo); pg.wait_for_timeout(250)

    if secao(1, 'O bloco está em toda tela que tem a caixa de sugestões'):
        todas = {_os.path.basename(c): open(c, encoding='utf-8').read() for c in localiza.caminhos()}
        com = sorted(n for n in todas if 'class="sugestoes"' in todas[n])
        ok(com == sorted(b[0] for b in BUSCAS), 'as telas com caixa de sugestões são as cinco que esta suíte percorre: %s' % [n.replace('pagina-', '') for n in com])
        sem = [n for n in com if MARCA not in todas[n]]
        ok(not sem, 'e as cinco têm o bloco das setas: %s' % sem)
        ok(len(set(bloco(todas[n]) for n in com if MARCA in todas[n])) == 1, 'com o mesmo texto em todas')

    if secao(2, 'Em cada busca, as setas andam pela lista e o Enter escolhe o item ativo'):
        for tela, query, prepara, campo, termo in BUSCAS:
            nome = tela.replace('pagina-', '').replace('.html', '')
            abrir(tela, query, prepara, campo, termo)
            e = pg.evaluate(LISTA, campo)
            ok(e['n'] >= 3 and e['ativos'] == [0], '%s: a lista abre com %d itens e o primeiro ativo' % (nome, e['n']))
            n = e['n']
            passos = []
            for tecla in ['ArrowDown', 'ArrowDown', 'ArrowUp', 'ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown']:
                pg.keyboard.press(tecla); pg.wait_for_timeout(40)
                passos.append(pg.evaluate(LISTA, campo)['ativos'])
            esperado = [[1], [2 % n], [1], [0], [n - 1], [0], [1]] if n else []
            ok(passos == esperado, '%s: descer e subir andam um a um, com um ativo só, e dão a volta no fim da lista: %s' % (nome, passos))
            e = pg.evaluate(LISTA, campo)
            ok(e['foco'] and pg.input_value(campo) == termo, '%s: o cursor e o texto digitado ficam no campo' % nome)
            pg.evaluate(VIGIA, campo)
            pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
            clicou = pg.evaluate('window.__clicou')
            ok(n >= 2 and clicou == e['chaves'][1] and clicou != e['chaves'][0] and pg.evaluate(LISTA, campo)['n'] == 0,
               '%s: Enter escolhe o item ativo (o segundo), e não o primeiro, e a lista fecha: %s' % (nome, clicou))
            pg.keyboard.press('ArrowDown'); pg.keyboard.press('ArrowUp'); pg.wait_for_timeout(60)

    if secao(3, 'Na Movimentação de Estoque, pelo resultado'):
        abrir('pagina-estoque-movimentacao.html', '', None, '#buscaProduto', 'desk')
        nomes = pg.evaluate("Array.from(document.querySelectorAll('#sugestoesProduto .sugestao-nome')).map(x => x.textContent)")
        pg.keyboard.press('ArrowDown'); pg.wait_for_timeout(60); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok(len(nomes) >= 2 and pg.input_value('#buscaProduto') == nomes[1] and pg.evaluate('produtoEscolhido.nome') == nomes[1],
           'descer uma vez e dar Enter põe no campo o segundo produto da lista: %s' % pg.input_value('#buscaProduto'))
        pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.getElementById('painelResultado').style.display") != 'none' and pg.evaluate("document.querySelector('#painelProduto .bq-nome').textContent") == nomes[1],
           'e, com o produto escolhido, o Enter seguinte busca, como antes')
        pg.fill('#buscaProduto', 'cadeira'); pg.wait_for_timeout(200); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok(pg.input_value('#buscaProduto') == 'Cadeira Ergonômica Pro', 'sem mexer nas setas, o Enter continua escolhendo o primeiro')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
