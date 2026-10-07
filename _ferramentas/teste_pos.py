from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto('file://' + os.path.abspath('pagina-financas-caixa-lancamento.html')); pg.wait_for_timeout(500)

    print('posicao do calendario')
    pg.click('#dfLancData .date-btn'); pg.wait_for_timeout(350)
    m = pg.evaluate("""(function(){
      const btn = document.querySelector('#dfLancData .date-btn').getBoundingClientRect();
      const pop = document.querySelector('#dfLancData .date-pop').getBoundingClientRect();
      const campo = document.querySelector('#dfLancData').getBoundingClientRect();
      return {btnR: btn.right, btnT: btn.top, popR: pop.right, popL: pop.left, popB: pop.bottom, campoL: campo.left};
    })()""")
    ok(abs(m['popR'] - m['btnR']) <= 10, 'o calendario alinha pela DIREITA, junto do icone (pop %.0f x icone %.0f)' % (m['popR'], m['btnR']))
    ok(m['popL'] > m['campoL'] + 50, 'nao abre mais na ponta esquerda do campo (pop %.0f x campo %.0f)' % (m['popL'], m['campoL']))
    ok(m['popB'] <= m['btnT'] + 2, 'abre ACIMA do icone (base do pop %.0f x topo do icone %.0f)' % (m['popB'], m['btnT']))
    dist = m['btnT'] - m['popB']
    ok(0 <= dist <= 12, 'colado no icone: %.0fpx de distancia' % dist)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    print('campo no topo da tela desce, em vez de sair pra fora')
    pg.goto('file://' + os.path.abspath('pagina-financas-caixa.html')); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.removeItem('deskParametros')")
    pg.click('#btnTransferir'); pg.wait_for_timeout(350)
    pg.click('#dfTransfData .date-btn'); pg.wait_for_timeout(350)
    m2 = pg.evaluate("""(function(){
      const btn = document.querySelector('#dfTransfData .date-btn').getBoundingClientRect();
      const pop = document.querySelector('#dfTransfData .date-pop').getBoundingClientRect();
      return {btnT: btn.top, btnB: btn.bottom, popT: pop.top, popB: pop.bottom, abaixo: document.querySelector('#dfTransfData .date-pop').classList.contains('abaixo')};
    })()""")
    ok(m2['popT'] >= -1, 'o calendario nao sai pela borda de cima (topo %.0f)' % m2['popT'])
    ok(m2['abaixo'] == (m2['popT'] > m2['btnT']), 'a classe combina com a posicao real (abaixo=%s)' % m2['abaixo'])
    ok(not erros, 'sem erro de JS: %s' % erros[:2])
    pg.screenshot(path='qa-pos-transf.png')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    pg.click('#btnCancelarTransferencia'); pg.wait_for_timeout(200)
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
