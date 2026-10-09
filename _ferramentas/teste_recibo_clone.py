# -*- coding: utf-8 -*-
# Clonar conta e Imprimir recibo, dentro do "Mais acoes". 29/set/2026.
from playwright.sync_api import sync_playwright
import os, sys
import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
ARQ = localiza.uri('pagina-financas-contas-pagar-detalhe.html')

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 950})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)
    def limpos(): return [e for e in erros if 'ERR_' not in e and 'Failed to load' not in e]

    print('1. o menu tem as quatro acoes, na ordem certa')
    erros.clear(); pg.goto(ARQ + '?id=1'); pg.wait_for_timeout(600)
    ok(not limpos(), 'conta paga carrega sem erro de JS: %s' % limpos()[:1])
    itens = pg.evaluate("[...document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')].map(i=>i.textContent.trim())")
    ok(itens == ['Clonar conta', 'Imprimir recibo', 'Cancelar conta', 'Excluir conta'], 'ordem do menu: %s' % itens)
    ok(pg.evaluate("[...document.querySelectorAll('#menuMaisAcoes .item-perigo')].length") == 2,
       'so as duas destrutivas sao vermelhas')

    print('2. recibo so existe com pagamento')
    ok(not pg.evaluate("linkImprimirRecibo.classList.contains('travado')"), 'conta paga: recibo liberado')
    erros.clear(); pg.goto(ARQ + '?id=3'); pg.wait_for_timeout(500)
    ok(pg.evaluate("linkImprimirRecibo.classList.contains('travado')"), 'conta sem baixa: recibo TRAVADO')
    ok('pagamento' in pg.evaluate("linkImprimirRecibo.title"), 'e o motivo esta no title')
    pg.evaluate("linkImprimirRecibo.click()"); pg.wait_for_timeout(250)
    ok(not pg.evaluate("drawerRecibo.classList.contains('open')"), 'travado nao abre o painel')

    print('3. o painel do recibo')
    erros.clear(); pg.goto(ARQ + '?id=1'); pg.wait_for_timeout(600)
    pg.evaluate("linkImprimirRecibo.click()"); pg.wait_for_timeout(350)
    ok(pg.evaluate("drawerRecibo.classList.contains('open')"), 'painel abre')
    r = pg.evaluate("({forn:reciboForn.value, valor:reciboValor.value, data:inputReciboData.value, ref:reciboRef.value})")
    ok(r['forn'] == 'Prime Distribuidora', 'fornecedor vem da conta')
    ok(r['valor'] == '6.740,00', 'valor e o PAGO, nao o da conta: %s' % r['valor'])
    ok('/' in r['data'], 'data nasce preenchida')
    ok('11804' in r['ref'], 'referencia sai do documento')
    ok(pg.evaluate("!!document.querySelector('#dfReciboData .date-pop')"), 'a data usa o componente de calendario (§9.2)')

    print('4. o valor por extenso')
    casos = [(1, 'UM REAL'), (100, 'CEM REAIS'), (1000, 'MIL REAIS'), (1040, 'MIL E QUARENTA REAIS'),
             (1700, 'MIL E SETECENTOS REAIS'), (6740, 'SEIS MIL SETECENTOS E QUARENTA REAIS'),
             (0.5, 'CINQUENTA CENTAVOS')]
    for v, esperado in casos:
        got = pg.evaluate("porExtenso(%s)" % v)
        ok(got == esperado, 'R$ %s -> %s' % (v, got))

    print('5. clonar copia a despesa, nao a data')
    erros.clear(); pg.goto(ARQ + '?clonar=1'); pg.wait_for_timeout(700)
    ok(not limpos(), 'clone carrega sem erro de JS: %s' % limpos()[:1])
    ok(pg.evaluate("document.getElementById('inputFornecedor').value") == 'Prime Distribuidora', 'fornecedor veio')
    ok(pg.evaluate("document.getElementById('inputValor').value") == '6.740,00', 'valor veio')
    ok(pg.evaluate("document.getElementById('inputHistorico').value") != '', 'historico veio')
    ok(pg.evaluate("document.getElementById('inputDoc').value") == '', 'documento NAO veio (cada conta tem a sua nota)')
    ok(pg.evaluate("document.getElementById('inputVencimento').value") == '', 'vencimento nasce VAZIO')
    ok(pg.evaluate("document.getElementById('inputEmissao').value") != '', 'emissao nasce hoje')
    ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), 'clone abre em EDICAO')
    ok('clonada' in pg.evaluate("document.getElementById('avisoBaixa').textContent"), 'a faixa avisa que e clone')
    pg.evaluate("document.getElementById('btnSalvarConta').click()"); pg.wait_for_timeout(400)
    ok(pg.evaluate("document.getElementById('caixaErro').style.display") != 'none', 'salvar sem vencimento e barrado')
    b.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas: print('  - ' + f)
sys.exit(1 if falhas else 0)
