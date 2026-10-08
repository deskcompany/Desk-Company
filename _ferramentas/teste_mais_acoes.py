# -*- coding: utf-8 -*-
# "Mais acoes": um componente so, um rotulo so — e a acao destrutiva das paginas
# de registro dentro dele. Nasceu em 28/set/2026.
from playwright.sync_api import sync_playwright
import os, sys, re
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

# telas com menu -> acao destrutiva que tem de estar DENTRO dele (None = nao tem)
COM_MENU = {
 'pagina-cadastros-clientes.html': None,
 'pagina-cadastros-fornecedores.html': None,
 'pagina-cadastros-produtos.html': None,
 'pagina-cadastros-vendedores-detalhe.html': 'btnExcluirVendedor',
 'pagina-estoque-conferencia-entrada.html': None,
 'pagina-estoque-conferencia.html': None,
 'pagina-estoque-controle-estoques.html': None,
 'pagina-estoque-enderecamento.html': None,
 'pagina-estoque-entrada-notas.html': None,
 'pagina-estoque-entrada-notas-detalhe.html': None,
 'pagina-estoque-inventario.html': None,
 'pagina-estoque-ordens-compra.html': None,
 'pagina-estoque-ordens-compra-detalhe.html': 'linkExcluirOC',
 'pagina-financas-caixa.html': None,
 'pagina-cadastros-produtos-detalhe.html': 'linkExcluirProduto',
 'pagina-financas-caixa-lancamento.html': 'linkExcluirLanc',
 'pagina-financas-contas-pagar-detalhe.html': 'linkExcluirConta',
}
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)

    for n, alvo in COM_MENU.items():
        erros.clear()
        pg.goto('file://' + os.path.abspath(n)); pg.wait_for_timeout(300)
        ok(not [e for e in erros if not ruido(e)], f'{n}: carrega sem erro de console')

        r = pg.evaluate("""() => {
            const raiz = document.getElementById('menuMaisAcoes');
            if (!raiz) return {existe:false};
            const btn = raiz.querySelector('.dropdown-select-btn');
            const lab = raiz.querySelector('.dropdown-select-label');
            const menu = raiz.querySelector('.dropdown-select-menu');
            return {existe:true, classe:btn.className, rotulo:lab ? lab.textContent.trim() : null,
                    itens:menu.querySelectorAll('.dropdown-select-item').length,
                    proprio:!!raiz.closest('.dropdown-select')}; }""")
        ok(r['existe'], f'{n}: #menuMaisAcoes existe')
        if not r['existe']: continue
        ok(r['rotulo'] == 'Mais ações', f'{n}: rótulo é "Mais ações" (achei "{r["rotulo"]}")')
        ok(r['classe'] == 'btn-ghost dropdown-select-btn', f'{n}: botão usa btn-ghost (achei "{r["classe"]}")')
        ok(r['itens'] > 0, f'{n}: menu tem {r["itens"]} itens')

        # abre
        pg.evaluate("document.querySelector('#menuMaisAcoes .dropdown-select-btn').click()")
        pg.wait_for_timeout(150)
        ok(pg.evaluate("document.querySelector('#menuMaisAcoes .dropdown-select-menu').classList.contains('open')"),
           f'{n}: o menu abre no clique')

        # fecha mutuamente: abrir outro dropdown tem de fechar este
        outro = pg.evaluate("""() => {
            const b = [...document.querySelectorAll('.dropdown-select .dropdown-select-btn')]
              .find(x => !x.closest('#menuMaisAcoes') && x.offsetParent !== null && !x.disabled);
            if (!b) return null; b.click();
            return document.querySelector('#menuMaisAcoes .dropdown-select-menu').classList.contains('open'); }""")
        if outro is None:
            print(f'  --   {n}: sem outro dropdown visível para testar fechamento mútuo')
        else:
            ok(outro is False, f'{n}: abrir outro dropdown FECHA o Mais ações')
        pg.keyboard.press('Escape'); pg.evaluate("document.body.click()")

        if alvo:
            r2 = pg.evaluate(f"""() => {{
                const el = document.getElementById('{alvo}');
                if (!el) return {{achou:false}};
                return {{achou:true, dentro: !!el.closest('#menuMaisAcoes'),
                         classe: el.className,
                         soltoNoRodape: !el.closest('#menuMaisAcoes')}}; }}""")
            ok(r2['achou'], f'{n}: a ação destrutiva #{alvo} continua existindo')
            ok(r2.get('dentro'), f'{n}: #{alvo} está DENTRO do Mais ações')
            ok('item-perigo' in (r2.get('classe') or ''), f'{n}: #{alvo} usa item-perigo (vermelho)')
    b.close()

print(f'\nFALHAS: {len(falhas)}')
for f_ in falhas: print('  - ' + f_)
sys.exit(1 if falhas else 0)
