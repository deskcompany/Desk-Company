# Contas a pagar escreve -> Caixa le. O teste faz o caminho do usuario:
# da a baixa numa tela e clica no link que leva para a outra.
from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g, tempfile as _tempfile
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

CP = localiza.uri('pagina-financas-contas-pagar.html')
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(CP); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.clear()")
    pg.goto(CP); pg.wait_for_timeout(500)

    print('1. a baixa em Contas a pagar')
    # Escolher entre as linhas QUE ESTAO NA TELA, nao entre todas do mock: a
    # listagem abre filtrada pelo mes corrente, e o primeiro titulo em aberto do
    # mock pode estar fora dele. Terceira mordida do "o mock envelhece" — em
    # 30/set o alvo caia dentro do mes e o teste passava; em 02/out, nao.
    alvo = pg.evaluate("""(function(){
      var na_tela = [].slice.call(document.querySelectorAll('[data-check="titulo"]'))
                      .map(function(e){ return Number(e.getAttribute('data-id')); });
      var t = TITULOS.filter(function(x){ return !x.cancelado && x.pago === 0 && na_tela.indexOf(x.id) >= 0; })[0];
      return { id: t.id, valor: t.valor, cat: t.catId };
    })()""")
    pg.evaluate("(function(id){document.querySelector('[data-check=\"titulo\"][data-id=\"'+id+'\"]').click()})(%d)" % alvo['id'])
    pg.wait_for_timeout(250)
    pg.click('#btnPagarSelecionadas'); pg.wait_for_timeout(400)
    pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(200)
    pg.fill('#inputJuros', '35,00'); pg.wait_for_timeout(250)
    pg.click('#btnConfirmarPagamento'); pg.wait_for_timeout(450)
    movs = pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras')||'[]')")
    ok(len(movs) == 2, 'a baixa deixou 2 movimentos no deposito: %d' % len(movs))
    ok(pg.eval_on_selector('#avisoBaixa', "e => e.classList.contains('show')"), 'o aviso com o link para o Caixa apareceu')

    print('2. o link leva ao Caixa')
    pg.click('#avisoBaixa a'); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-caixa.html'), 'abriu o extrato: %s' % pg.url.split('/')[-1])
    ok(not erros, 'sem erro de JS nas duas telas: %s' % erros[:3])

    print('3. o extrato mostra os dois lancamentos, sem nenhum texto de gambiarra')
    vindos = pg.evaluate("MOVIMENTOS.filter(function(m){return m.id>=900000}).length")
    ok(vindos == 2, 'o Caixa leu os 2 movimentos junto com o mock: %d' % vindos)
    txt = pg.text_content('tbody')
    ok('Juros e multa' in txt, 'o lancamento de juros aparece na primeira pagina (e do dia de hoje)')
    cat = pg.evaluate("""(function(){
      var m = MOVIMENTOS.filter(function(x){return x.catId===20})[0];
      return m ? (CATS_FIN.filter(function(c){return c.id===20})[0]||{}).nome : null })()""")
    ok(cat == 'Juros e multas pagos', 'o juros caiu na categoria propria, nao na do titulo: %s' % cat)
    principal = pg.evaluate("MOVIMENTOS.filter(function(m){return m.id>=900000 && m.catId!==20})[0]")
    ok(abs(principal['valor'] - alvo['valor']) < 0.01, 'o valor do principal bate com o titulo: %s x %s' % (principal['valor'], alvo['valor']))
    ok(principal['catId'] == alvo['cat'], 'o principal manteve a categoria do titulo')
    ok(all(m['tipo'] == 'saida' for m in movs), 'os dois entram como saida no extrato')

    print('4. os totais do extrato incluem o que veio de fora')
    soma = pg.evaluate("""(function(){
      var hoje = iso(HOJE);
      return MOVIMENTOS.filter(function(m){return m.data===hoje && m.id>=900000})
                       .reduce(function(s,m){return s+m.valor},0) })()""")
    ok(abs(soma - (alvo['valor'] + 35)) < 0.01, 'principal + juros somam no dia de hoje: %.2f' % soma)

    print('5. recarregar nao duplica')
    pg.reload(); pg.wait_for_timeout(600)
    ok(pg.evaluate("MOVIMENTOS.filter(function(m){return m.id>=900000}).length") == 2, 'continua 2 depois do reload')
    ok(pg.eval_on_selector_all('tbody tr[data-id]', 'e => e.length') > 0, 'o extrato continua renderizando')
    ok(not erros, 'nenhum erro de JS no caminho todo: %s' % erros[:3])
    pg.screenshot(path=_os.path.join(_tempfile.gettempdir(), 'qa-integracao-caixa.png'))  # no temp: a raiz do projeto nao e deposito de artefato
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
