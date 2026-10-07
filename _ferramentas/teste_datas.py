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

casos = [
    ('pagina-estoque-ordens-compra-detalhe.html', 'dfDataCompra', 'dfDataPrevista', 'inputDataCompra'),
    ('pagina-estoque-entrada-notas-detalhe.html', 'dfEmissao', 'dfEntrada', 'inputEmissao'),
    ('pagina-cadastros-clientes-detalhe.html', 'dfNascimento', None, None),
]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    for arq, df1, df2, dep in casos:
        print(arq)
        pg = b.new_page(viewport={'width':1440,'height':900})
        erros = []
        pg.on('pageerror', lambda e: erros.append(str(e)))
        pg.goto('file://' + os.path.abspath(arq)); pg.wait_for_timeout(600)
        ok(not erros, '  sem erro de JS: %s' % erros[:2])
        # abrir o primeiro campo (pode estar dentro de aba/painel: forca a exibicao do pai)
        vis = pg.eval_on_selector('#' + df1, "e => { const r = e.getBoundingClientRect(); return r.width > 0; }")
        if not vis:
            pg.evaluate("""(id)=>{let e=document.getElementById(id);while(e&&e!==document.body){const cs=getComputedStyle(e);if(cs.display==='none')e.style.display='block';e=e.parentElement;}}""", df1)
            pg.wait_for_timeout(200)
        pg.click('#' + df1 + ' .date-btn'); pg.wait_for_timeout(300)
        ok(pg.eval_on_selector('#' + df1 + ' .date-pop', "e => e.classList.contains('open')"), '  calendario abre')
        dias = pg.eval_on_selector_all('#' + df1 + ' .date-dia:not(.vazio)', 'e => e.length')
        ok(28 <= dias <= 31, '  %d dias no mes' % dias)
        pg.click('#' + df1 + ' .date-dia[data-iso]'); pg.wait_for_timeout(250)
        ok(pg.eval_on_selector('#' + df1 + ' .date-pop', "e => e.classList.contains('open')") is False, '  fecha ao escolher')
        if df2:
            # o limite so aparece se o primeiro campo tiver uma data no MEIO do mes:
            # com dia 1, nao ha dia anterior no mes visivel para ficar riscado.
            hoje = pg.evaluate("(function(){var h=new Date();return '15/' + String(h.getMonth()+1).padStart(2,'0') + '/' + h.getFullYear()})()")
            pg.fill('#' + dep, hoje); pg.wait_for_timeout(200)
            pg.click('#' + df2 + ' .date-btn'); pg.wait_for_timeout(300)
            riscados = pg.eval_on_selector_all('#' + df2 + ' .date-dia.off', 'e => e.length')
            ok(riscados > 0, '  o segundo campo respeita o limite do primeiro: %d dias riscados' % riscados)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(not erros, '  sem erro de JS ao final: %s' % erros[:2])
        pg.close()
    b.close()
print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
