# -*- coding: utf-8 -*-
# Esc fecha o dropdown aberto — e NAO atropela o Esc do modal/drawer. 28/set/2026.
from playwright.sync_api import sync_playwright
import os, sys
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
import sys as _sys, os as _os2
_sys.path.insert(0, _os2.path.dirname(_os2.path.abspath(__file__)))
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

falhas = []
acertos = []
def ok(c, m):
    if c: acertos.append(m)
    else: falhas.append(m); print('  FALHA ' + m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    telas = [os.path.basename(f) for f in _filtrar(sorted(_g.glob('pagina-*.html'))) if 'molde' not in f]
    testadas = 0
    for n in telas:
        pg.goto('file://' + os.path.abspath(n)); pg.wait_for_timeout(200)
        if not pg.evaluate("!!document.querySelector('.dropdown-select-menu')"): continue
        abriu = pg.evaluate("""() => {
            const b = [...document.querySelectorAll('.dropdown-select .dropdown-select-btn')]
              .find(x => x.offsetParent !== null && !x.disabled);
            if (!b) return null; b.click();
            return !!document.querySelector('.dropdown-select-menu.open'); }""")
        if abriu is None: continue
        ok(abriu, f'{n}: algum dropdown abre')
        if not abriu: continue
        pg.keyboard.press('Escape'); pg.wait_for_timeout(120)
        ok(not pg.evaluate("!!document.querySelector('.dropdown-select-menu.open')"),
           f'{n}: Esc FECHA o dropdown aberto')
        testadas += 1

        # sem dropdown aberto, o Esc do modal continua funcionando
        if pg.evaluate("typeof abrirModalConfirmacao === 'function'"):
            pg.evaluate("abrirModalConfirmacao('t',1,'primary',()=>{})"); pg.wait_for_timeout(120)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
            ok(not pg.evaluate("document.getElementById('confirmModal').classList.contains('open')"),
               f'{n}: sem dropdown aberto, Esc continua fechando o modal')
    b.close()
print(f'\n{testadas} telas testadas · {len(acertos)} asserções · FALHAS: {len(falhas)}')
sys.exit(1 if falhas else 0)
