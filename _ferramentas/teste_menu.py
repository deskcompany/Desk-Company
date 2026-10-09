from playwright.sync_api import sync_playwright
import os, sys, re, glob
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
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

    print('1. de uma tela de Cadastros ate Contas a pagar, pelo menu')
    pg.goto('file://' + os.path.abspath('pagina-cadastros-marcas.html')); pg.wait_for_timeout(500)
    # O menu abre no CLIQUE do modulo, nao no hover — foi assim que o molde
    # ficou. O teste segue o caminho do usuario: clica no modulo, depois no item.
    def abrirMenu(modulo):
        pg.click('.nav-item[data-id="%s"]' % modulo); pg.wait_for_timeout(450)
    abrirMenu('financas')
    sel = '#flyout-financas .flyout-item[data-label="Contas a Pagar"]'
    ok(pg.query_selector(sel) is not None, 'o item existe no flyout de Financas')
    ok(pg.get_attribute(sel, 'data-href') == 'pagina-financas-contas-pagar.html', 'e agora tem destino')
    pg.click(sel); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-contas-pagar.html'), 'o clique navegou de verdade: %s' % pg.url.split('/')[-1])

    print('2. e de Contas a pagar de volta para o Caixa')
    abrirMenu('financas')
    pg.click('#flyout-financas .flyout-item[data-label="Caixa"]'); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-caixa.html'), 'chegou no extrato: %s' % pg.url.split('/')[-1])

    print('3. e do Caixa para Contas a receber, construida em 02/out')
    abrirMenu('financas')
    pg.click('#flyout-financas .flyout-item[data-label="Contas a Receber"]'); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-contas-receber.html'), 'chegou no a receber: %s' % pg.url.split('/')[-1])

    print('4. item sem tela continua inerte, sem quebrar')
    # Este caso precisa de um item que de fato NAO tem tela — ate 02/out ele era
    # "Contas a Receber", que agora existe. Teste que prova "nao navega" tem de
    # trocar de alvo quando o alvo ganha destino, senao vira teste de nada.
    abrirMenu('financas')
    antes = pg.url
    pg.click('#flyout-financas .flyout-item[data-label="Comissões Afiliados"]'); pg.wait_for_timeout(500)
    ok(pg.url == antes, 'nao navegou (a tela ainda nao existe)')
    ok('Comissões Afiliados' in pg.text_content('#breadcrumb'), 'mas moveu o breadcrumb, como antes')
    ok(not erros, 'sem erro de JS: %s' % erros[:3])

    print('5. todo destino do menu aponta para arquivo que existe')
    faltando = []
    for arq in _filtrar(glob.glob('*.html')):
        t = open(arq, encoding='utf-8').read()
        for h in set(re.findall(r'flyout-item" data-label="[^"]+" data-href="([^"]+)"', t)):
            if not os.path.exists('' + h): faltando.append((os.path.basename(arq), h))
    ok(not faltando, 'nenhum destino quebrado: %s' % faltando[:3])

    print('5. o painel de Pagamento abre vivo numa conta em LEITURA')
    pg.goto('file://' + os.path.abspath('pagina-financas-contas-pagar-detalhe.html') + '?id=6'); pg.wait_for_timeout(600)
    ok(pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'a conta abre em leitura')
    pg.click('#btnDarBaixa'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#inputDataPgto', "e => getComputedStyle(e).display") != 'none', 'o campo Data do painel esta visivel')
    ok(pg.eval_on_selector('#ddOrigem', "e => getComputedStyle(e).display") != 'none', 'o dropdown de origem esta visivel')
    pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#inputJuros', "e => getComputedStyle(e).display") != 'none', 'e os campos de juros e desconto tambem')
    ok(not erros, 'sem erro de JS no caminho todo: %s' % erros[:3])
    print('6. botao que vira link nao ganha sublinhado, em nenhuma tela')
    # 08/out: o usuario viu "Definir metas" sublinhado, pela segunda vez no dia.
    # Botao escrito como link herda o sublinhado do navegador, e cada tela
    # resolvia isso classe por classe. A medida e feita com TODA classe btn-*
    # que a tela declara, inclusive as que hoje so aparecem em botao de verdade:
    # o defeito latente e o que volta na proxima tela clonada.
    SUBLINHA = """() => {
      const nomes = new Set();
      for (const s of document.styleSheets) { let r; try { r = s.cssRules; } catch (e) { continue; }
        for (const x of r) { const m = (x.selectorText || '').match(/[.]btn-[a-z0-9-]*/gi); if (m) m.forEach(n => nomes.add(n.slice(1))); } }
      const ruins = [];
      nomes.forEach(n => { const a = document.createElement('a'); a.href = '#'; a.className = n; a.textContent = 'x';
        document.body.appendChild(a);
        if (getComputedStyle(a).textDecorationLine.indexOf('underline') >= 0) ruins.push(n); a.remove(); });
      return ruins.sort();
    }"""
    sublinhadas = []
    for arq in sorted(_filtrar(glob.glob('pagina-*.html'))):
        pg.goto('file://' + os.path.abspath(arq)); pg.wait_for_load_state('load')
        ruins = pg.evaluate(SUBLINHA)
        if ruins: sublinhadas.append((os.path.basename(arq), ruins))
    ok(not sublinhadas, 'nenhuma classe de botao sublinha como link: %s' % sublinhadas[:3])
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
