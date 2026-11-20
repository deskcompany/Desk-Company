# -*- coding: utf-8 -*-
# O desconto da venda nossa (20/nov/2026): o PDV e o Pedido de Venda.
#
# O que ele protege sao as decisoes do usuario de 20/nov/2026 (plano docs/plano-venda-nossa-e-embalagens.md, Entrega 1):
#   E uma OPCAO que se aplica (nao automatica): "Dar o desconto da venda nossa (5%)" so aparece sem vendedor (no Pedido, tambem sem indicacao) e com Pix ou dinheiro
#   O percentual e o `comissaoPadraoPct` de Parametros de vendas; so a parte paga no Pix ou no dinheiro leva o desconto
#   A trava: o desconto nunca leva um produto abaixo do minimo da calculadora; o que passa e cortado, e o aviso diz quanto e em qual produto
#   Nao pede codigo e nao conta no limite de desconto; escolher o vendedor (ou chegar uma indicacao) tira o desconto, com aviso
#   O registro grava `vendaNossa: { pct, valor, cortado }`
#
#   [1]  O bloco VENDA NOSSA e a conta pura
#   [2]  O PDV: a opcao, o valor, o pagamento dividido, a trava, o vendedor, o Pix que sai e volta
#   [3]  O PDV: sem codigo e fora do limite; o total a pagar, o troco, o caixa, o recibo e o registro
#   [4]  O Pedido de Venda: a opcao, o valor, o vale-compra, a trava, o vendedor e a indicacao, e salvar
#   [5]  Os dois temas, 1280 e 1440: sem barra para o lado, Nunito
import os as _os, glob as _g, sys
from playwright.sync_api import sync_playwright
import localiza
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
FOTOS = _os.environ.get('DESK_FOTOS') or ''
PDV = 'pagina-vendas-pdv.html'
PEDD = 'pagina-vendas-pedidos-detalhe.html'
LISTA = 'pagina-vendas-promocoes.html'

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


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


def bloco(t, ini, fim):
    i = t.find(ini)
    if i < 0:
        return None
    j = t.find(fim, i)
    return t[i:j] if j >= 0 else None


def perto(a, b):
    return abs(a - b) < 0.005


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('dialog', lambda d: d.dismiss())

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(250)

    def limpar():
        ir(LISTA); pg.evaluate("localStorage.clear(); sessionStorage.clear()")

    def ev(js, *a):
        return pg.evaluate(js, *a) if a else pg.evaluate(js)

    def clica(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(150)

    def modal_aberto():
        return ev("document.getElementById('confirmModal').classList.contains('open')")

    def texto_modal():
        return ev("document.getElementById('confirmModalTexto').textContent")

    def fecha_aviso():
        if modal_aberto():
            clica('#btnConfirmModalConfirmar'); pg.wait_for_timeout(150)

    def escolhe(raiz, v):
        clica('#%s .dropdown-select-btn' % raiz)
        ev("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(v)]); pg.wait_for_timeout(150)

    def txt(sel):
        return ev("(s) => document.querySelector(s).textContent.replace(/\\s+/g, ' ').trim()", sel)

    def vis(sel):
        return ev("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)

    def params(**kw):
        d = {'pdvDescontoAVista': False}
        d.update(kw)
        ev("(d) => localStorage.setItem('deskParametros', JSON.stringify(d))", d)

    def foto(nome):
        if FOTOS:
            pg.screenshot(path=_os.path.join(FOTOS, nome))

    # ---------------- PDV ----------------
    def pdv_abre(loja=1, **kw):
        ir(PDV); ev("localStorage.removeItem('deskPdv')"); params(**kw); ir(PDV)
        clica('#btnAbrirCaixa'); escolhe('abrirLoja', loja); pg.fill('#abrirTroco', '100'); clica('#btnConfirmarAbertura'); pg.wait_for_timeout(250)

    def pdv_add(sku, q='1'):
        pg.fill('#qtdProduto', q); pg.fill('#buscaProduto', sku); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)

    def pdv_cobra(sku, q='1', forma='pix', vendedor=None):
        # abre o caixa, poe o produto, (o vendedor,) continua e poe a forma de recebimento
        pdv_abre(1)
        if vendedor is not None:
            escolhe('selVendedor', vendedor)
        pdv_add(sku, q); clica('#btnContinuar'); pg.wait_for_timeout(300)
        if forma:
            escolhe('selAddReceb', forma)

    def valor_receb(n, v):
        pg.fill('[data-receb-valor="%d"]' % n, v); pg.locator('[data-receb-valor="%d"]' % n).blur(); pg.wait_for_timeout(250)

    def dar_pdv():
        clica('#btnVendaNossa'); pg.wait_for_timeout(250)

    # ---------------- Pedido ----------------
    def ped_campo(i, c, v):
        ev("([i, c, v]) => { const e = document.querySelector('#corpoItens input[data-campo=\"' + c + '\"][data-i=\"' + i + '\"]'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); }", [i, c, v])
        pg.wait_for_timeout(150)

    def ped_novo(sku, q='1', forma='pix'):
        ir(PEDD, '?novo=1'); escolhe('inputLoja', 1)
        n = ev("ITENS.findIndex(i => !i.sku)")
        if n < 0:
            clica('#btnAdicionarItem'); n = ev("ITENS.length") - 1
        ped_campo(n, 'sku', sku); ped_campo(n, 'qtd', q)
        escolhe('inputRecebimento', forma)

    def dar_ped():
        clica('#btnVendaNossa'); pg.wait_for_timeout(250)

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'O bloco VENDA NOSSA e a conta pura'):
        BI, BF = '  // ===== VENDA NOSSA (bloco comum', '  // ===== FIM DO BLOCO VENDA NOSSA ====='
        cop = [bloco(fonte(n), BI, BF) for n in (PDV, PEDD)]
        ok(cop[0] and cop[0] == cop[1], 'o bloco VENDA NOSSA é idêntico no PDV e no Pedido de Venda')
        ok('function vendaNossaConta' in cop[0] and 'vendaNossaPode' in cop[0] and 'vendaNossaPct' in cop[0], 'e leva a conta, a condição (vendedor e indicação) e o percentual')
        PMI, PMF = '  // ===== PRECO MINIMO: A CONTA DA CALCULADORA', '  // ===== FIM DO BLOCO PRECO MINIMO ====='
        pm = [bloco(fonte(n), PMI, PMF) for n in (PDV, PEDD)]
        ok(pm[0] and pm[0] == pm[1], 'o bloco PRECO MINIMO, de que ele depende, segue idêntico nas duas telas')
        ir(PDV); ev("localStorage.removeItem('deskParametros')"); ir(PDV)
        ok(ev("vendaNossaPct()") == 5, 'o percentual de fábrica é 5 (o comissaoPadraoPct de Parâmetros de vendas)')
        params(comissaoPadraoPct=4); ir(PDV)
        ok(ev("vendaNossaPct()") == 4, 'com 4% em Parâmetros de vendas, o percentual é 4')
        params(comissaoPadraoPct='lixo'); ir(PDV)
        ok(ev("vendaNossaPct()") == 5, 'parâmetro estragado vale o de fábrica (5)')
        ev("localStorage.removeItem('deskParametros')")
        c = ev("vendaNossaConta([{ nome: 'A', qtd: 1, base: 10000, minimo: null }], 1, 5, 0)")
        ok(c['valor'] == 500 and c['cortado'] == 0 and c['nomes'] == [], 'R$ 100,00 a 5%%, tudo no Pix: R$ 5,00, nada cortado: %s' % c)
        c = ev("vendaNossaConta([{ nome: 'A', qtd: 1, base: 10000, minimo: null }], 0.5, 5, 0)")
        ok(c['valor'] == 250, 'a fatia de metade desconta só a metade (R$ 2,50): %s' % c)
        c = ev("vendaNossaConta([{ nome: 'A', qtd: 2, base: 10000, minimo: 4990 }], 1, 5, 0)")
        ok(c['valor'] == 20 and c['cortado'] == 480 and c['nomes'] == ['A'], 'a trava corta no mínimo (2 x R$ 49,90 = R$ 99,80 sobre R$ 100,00): R$ 0,20 de R$ 5,00, R$ 4,80 cortados: %s' % c)
        c = ev("vendaNossaConta([{ nome: 'A', qtd: 1, base: 10000, minimo: 9400 }], 1, 5, 5)")
        ok(c['valor'] == 100 and c['cortado'] == 400, 'com o desconto à vista de 5%%: paga R$ 95,00 sem ele, o mínimo é R$ 94,00, a folga é R$ 1,00: %s' % c)
        ok(ev("[vendaNossaPode(null, null, 1), vendaNossaPode('Ana', null, 1), vendaNossaPode(null, { nome: 'x' }, 1), vendaNossaPode(null, null, 0)]") == [True, False, False, False],
           'a condição: sem vendedor, sem indicação e com fatia de Pix ou dinheiro')
        ok(ev("vendaNossaRotuloPct(5) + '|' + vendaNossaRotuloPct(3.5)") == '5|3,5', 'o rótulo do percentual: 5 e 3,5')

    # ------------------------------------------------------------------------------------------------
    if secao(2, 'O PDV: a opção, o valor, o pagamento dividido, a trava, o vendedor'):
        limpar()
        # --- 1: a opcao so cabe sem vendedor e com Pix ou dinheiro
        pdv_cobra('MOB-4002', '1', None)
        ok(not vis('#finVendaNossaOpcao'), 'sem forma de recebimento, o link não aparece')
        escolhe('selAddReceb', 'pix')
        ok(vis('#finVendaNossaOpcao') and txt('#btnVendaNossa') == 'Dar o desconto da venda nossa (5%)', 'com Pix e sem vendedor aparece "Dar o desconto da venda nossa (5%%)": %s' % txt('#btnVendaNossa'))
        ok(not vis('#finVendaNossaLinha'), 'e a linha do desconto ainda não aparece (é opção, não automático)')
        ok(ev("totalAPagar()") == 79.9, 'enquanto não for dado, o total a pagar é o cheio (R$ 79,90)')
        pdv_cobra('MOB-4002', '1', 'dinheiro')
        ok(vis('#finVendaNossaOpcao'), 'com dinheiro também aparece')
        pdv_cobra('MOB-4002', '1', 'credito')
        ok(not vis('#finVendaNossaOpcao'), 'só com cartão, não aparece')
        pdv_cobra('MOB-4002', '1', 'pix', vendedor='1')
        ok(not vis('#finVendaNossaOpcao'), 'com vendedor escolhido, não aparece (mesmo com Pix)')
        # --- 2: o valor
        pdv_cobra('MOB-4002', '1', 'pix')
        dar_pdv()
        ok(ev("venda.vendaNossaPedida") is True and vis('#finVendaNossaLinha') and not vis('#finVendaNossaOpcao'), 'dar o desconto mostra a linha e tira o link')
        ok(txt('#finVendaNossaRotulo') == 'Desconto da venda nossa (5%)' and txt('#finVendaNossa') == '− R$ 4,00', 'a linha diz "Desconto da venda nossa (5%%)  − R$ 4,00" (5%% de R$ 79,90, ao centavo): %s | %s' % (txt('#finVendaNossaRotulo'), txt('#finVendaNossa')))
        ok(not modal_aberto(), 'sem corte, sem aviso')
        ok(ev("totalAPagar()") == 75.9 and txt('#finTotal') == 'R$ 75,90' and txt('#totVendaFin') == 'R$ 75,90', 'o total a pagar é R$ 75,90: %s' % txt('#finTotal'))
        ok(ev("pagoDe(venda.recebimentos[0])") == 75.9 and ev("venda.recebimentos[0].valor") == 79.9, 'o Pix quita R$ 79,90 e o cliente paga R$ 75,90')
        ok('desconto da venda nossa de 5%' in txt('#listaReceb'), 'a linha do recebimento diz o desconto: %s' % txt('#listaReceb')[:160])
        ok('Pode finalizar' in txt('#faltaReceber') and 'R$ 75,90' in txt('#faltaReceber'), 'a barra de falta diz R$ 75,90 e "Pode finalizar"')
        clica('#btnTirarVendaNossa'); pg.wait_for_timeout(200)
        ok(ev("venda.vendaNossaPedida") is False and not vis('#finVendaNossaLinha') and vis('#finVendaNossaOpcao') and ev("totalAPagar()") == 79.9 and not modal_aberto(),
           '"tirar" tira na hora, sem código, e o link volta')
        # --- 2b: com 4% em Parametros de vendas
        params(comissaoPadraoPct=4); ir(PDV)
        ok(txt('#btnVendaNossa') == 'Dar o desconto da venda nossa (4%)', 'com 4%% em Parâmetros de vendas o link diz 4%%: %s' % txt('#btnVendaNossa'))
        dar_pdv()
        ok(txt('#finVendaNossa') == '− R$ 3,20' and ev("totalAPagar()") == 76.7, 'e o desconto é de 4%% (R$ 3,20 sobre R$ 79,90): %s' % txt('#finVendaNossa'))
        # --- 3: pagamento dividido
        pdv_abre(1); pdv_add('MOB-4002', '1'); clica('#btnContinuar'); pg.wait_for_timeout(300)
        escolhe('selAddReceb', 'pix'); escolhe('selAddReceb', 'credito')
        valor_receb(0, '40')
        dar_pdv()
        ok(txt('#finVendaNossa') == '− R$ 2,00' and ev("vendaNossaDe(venda.recebimentos[0])") == 2, 'metade no Pix (R$ 40,00) e o resto no cartão: o desconto é só de 5%% do Pix, R$ 2,00: %s' % txt('#finVendaNossa'))
        ok(ev("vendaNossaDe(venda.recebimentos[1])") == 0 and ev("pagoDe(venda.recebimentos[0])") == 38, 'o cartão não leva desconto, e o cliente paga R$ 38,00 no Pix')
        # Pix e dinheiro: o centavo que sobra vai para o maior
        pdv_abre(1); pdv_add('MOB-4002', '1'); clica('#btnContinuar'); pg.wait_for_timeout(300)
        escolhe('selAddReceb', 'pix'); escolhe('selAddReceb', 'dinheiro')
        valor_receb(0, '10')
        dar_pdv()
        pa = ev("venda.recebimentos.map(r => vendaNossaDe(r))")
        ok(pa == [0.5, 3.5] and perto(sum(pa), 4), 'Pix de R$ 10,00 e dinheiro de R$ 69,90: o desconto de R$ 4,00 divide na proporção, e o centavo que sobra vai para o maior: %s' % pa)
        ok(ev("totalAPagar()") == 75.9 and ev("trocoTotal()") == 0, 'e o total a pagar segue R$ 75,90')
        # --- 4: a trava
        pdv_cobra('PAP-3001', '1', 'pix')
        dar_pdv()
        ok(txt('#finVendaNossa') == '− R$ 0,03', 'o produto no limite do mínimo (PAP-3001, R$ 18,50, mínimo de R$ 18,47): o desconto é cortado a R$ 0,03: %s' % txt('#finVendaNossa'))
        ok(modal_aberto() and 'ficou em R$ 0,03' in texto_modal() and 'R$ 0,90 cortados' in texto_modal() and 'chegou ao preço mínimo' in texto_modal(),
           'o aviso diz quanto ficou e quanto foi cortado: %s' % (texto_modal() if modal_aberto() else '(sem aviso)'))
        nome = ev("venda.itens[0].nome")
        ok(nome in texto_modal(), 'e diz em qual produto (%s)' % nome)
        fecha_aviso()
        ok(vis('#finVendaNossaCorte') and 'R$ 0,90 cortados' in txt('#finVendaNossaCorte'), 'o aviso fica escrito embaixo da linha: %s' % txt('#finVendaNossaCorte'))
        ok(ev("totalAPagar()") == 18.47, 'e o cliente paga o mínimo (R$ 18,47)')
        # preco digitado perto do minimo: a trava vale sobre o preco da linha
        pdv_cobra('MOB-4002', '1', 'pix')
        ev("irPara('venda')"); pg.wait_for_timeout(200)
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)'); pg.wait_for_timeout(250)
        pg.fill('#itemPreco', '72,00'); ev("document.getElementById('itemPreco').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem'); pg.wait_for_timeout(250)
        fecha_aviso()
        ok(ev("venda.itens[0].preco") == 72, 'o preço digitado vale (R$ 72,00)')
        clica('#btnContinuar'); pg.wait_for_timeout(300)
        dar_pdv()
        ok(txt('#finVendaNossa') == '− R$ 2,08' and 'R$ 1,52 cortados' in txt('#finVendaNossaCorte'), 'com o preço digitado perto do mínimo (R$ 72,00, mínimo de R$ 69,92): R$ 2,08, e R$ 1,52 cortados: %s | %s' % (txt('#finVendaNossa'), txt('#finVendaNossaCorte')))
        fecha_aviso()
        # --- 5: escolher o vendedor tira o desconto
        pdv_cobra('MOB-4002', '1', 'pix'); dar_pdv()
        ev("irPara('venda')"); pg.wait_for_timeout(200)
        escolhe('selVendedor', '1'); pg.wait_for_timeout(200)
        ok(modal_aberto() and 'O desconto da venda nossa saiu' in texto_modal() and 'vendedor' in texto_modal(), 'escolher o vendedor avisa "O desconto da venda nossa saiu": %s' % (texto_modal() if modal_aberto() else '(sem aviso)'))
        fecha_aviso()
        ok(ev("venda.vendaNossaPedida") is False, 'e tira a opção de vez')
        clica('#btnContinuar'); pg.wait_for_timeout(300)
        ok(not vis('#finVendaNossaLinha') and not vis('#finVendaNossaOpcao') and ev("totalAPagar()") == 79.9, 'na cobrança não há linha nem link, e o total volta ao cheio (R$ 79,90)')
        # --- 6: o Pix sai da venda e volta
        pdv_cobra('MOB-4002', '1', 'pix'); dar_pdv()
        clica('[data-receb-remover="0"]'); pg.wait_for_timeout(250)
        ok(not vis('#finVendaNossaLinha') and ev("vendaNossaCalculo().valor") == 0 and ev("venda.vendaNossaPedida") is True, 'sem o Pix a linha some (valor 0), e a opção continua pedida')
        escolhe('selAddReceb', 'pix')
        ok(vis('#finVendaNossaLinha') and txt('#finVendaNossa') == '− R$ 4,00', 'o Pix volta e a linha volta: %s' % txt('#finVendaNossa'))

    # ------------------------------------------------------------------------------------------------
    if secao(3, 'O PDV: sem código, fora do limite, o total, o troco, o caixa, o recibo e o registro'):
        limpar()
        pdv_abre(1); pdv_add('FON-BT-200', '1'); clica('#btnContinuar'); pg.wait_for_timeout(300)
        lim = ev("autoLimiteVenda().pct")
        pg.fill('#finDesconto', '%s%%' % lim); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
        escolhe('selAddReceb', 'dinheiro')
        dar_pdv()
        ok(txt('#finVendaNossa') == '− R$ 11,25' and ev("totalVenda()") == 224.91, 'R$ 249,90 com %s%% na venda = R$ 224,91; o desconto da venda nossa é 5%% disso: R$ 11,25: %s' % (lim, txt('#finVendaNossa')))
        ok(not ev("document.getElementById('notaFinDesconto').offsetParent !== null"), 'o desconto da venda nossa não entra no "acima do máximo": sem aviso no campo do desconto')
        ok(ev("descontoGeralPct()") == lim, 'o percentual da venda para o limite segue %s%% (sem o da venda nossa)' % lim)
        ok(ev("totalAPagar()") == 213.66 and txt('#finTotal') == 'R$ 213,66', 'o total a pagar é R$ 213,66: %s' % txt('#finTotal'))
        # dinheiro recebido: o troco e sobre o que o cliente paga
        pg.fill('[data-receb-recebido="0"]', '250'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
        ok(ev("trocoTotal()") == 36.34 and 'Troco' in txt('#listaReceb') and 'R$ 36,34' in txt('#listaReceb'), 'recebendo R$ 250,00 em dinheiro o troco é R$ 36,34 (sobre R$ 213,66): %s' % ev("trocoTotal()"))
        pg.fill('[data-receb-recebido="0"]', '200'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
        ok('menor que o valor' in txt('#faltaReceber') and 'R$ 213,66' in txt('#faltaReceber'), 'recebido abaixo do que o cliente paga trava e diz R$ 213,66: %s' % txt('#faltaReceber')[:120])
        pg.fill('[data-receb-recebido="0"]', '250'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
        foto('pdv-cobranca-claro.png')
        clica('#btnFinalizar'); pg.wait_for_timeout(450)
        ok(ev("momento") == 'concluida' and not (modal_aberto() and 'Liberar desconto' in texto_modal()), 'finaliza sem pedir código nem liberação, com o desconto da venda nossa dado')
        fecha_aviso()
        v = ev("ultimaVenda")
        ok(v['vendaNossa'] == {'pct': 5, 'valor': 11.25, 'cortado': 0}, 'o registro grava vendaNossa { pct, valor, cortado }: %s' % v['vendaNossa'])
        ok(perto(v['total'], 213.66) and perto(v['troco'], 36.34) and perto(v['recebimentos'][0]['cobrado'], 213.66) and perto(v['recebimentos'][0]['descontoVendaNossa'], 11.25),
           'total R$ 213,66, troco R$ 36,34, cobrado R$ 213,66 e desconto da venda nossa R$ 11,25 no recebimento: %s' % [v['total'], v['troco'], v['recebimentos'][0]['cobrado'], v['recebimentos'][0]['descontoVendaNossa']])
        ok(txt('#concTotal') == 'R$ 213,66' and txt('#concTroco') == 'R$ 36,34', 'a tela de concluída diz R$ 213,66 e troco R$ 36,34')
        ok('desconto da venda nossa de R$ 11,25' in txt('#concGerado'), '"O que esta venda gerou" diz o desconto da venda nossa: %s' % txt('#concGerado')[-170:])
        ok(ev("dinheiroNaGaveta(turno)") == 313.66, 'o dinheiro na gaveta é a abertura (R$ 100,00) mais R$ 213,66: %s' % ev("dinheiroNaGaveta(turno)"))
        ex = ev("JSON.parse(localStorage.getItem('deskCaixaExtras') || '[]')")
        ok(len(ex) == 1 and perto(ex[0]['valor'], 213.66), 'o Caixa de Finanças recebe R$ 213,66 (o que o cliente pagou): %s' % [e['valor'] for e in ex])
        rec = ev("folhaRecibo(ultimaVenda, false)")
        ok('Desconto da venda nossa (5%)' in rec and '− R$ 11,25' in rec and 'R$ 213,66' in rec, 'o recibo tem a linha "Desconto da venda nossa (5%)" e o valor a pagar de R$ 213,66')
        # o limite da pessoa continua valendo: um ponto acima pede a liberacao, com o desconto da venda nossa dado
        pdv_abre(1); pdv_add('FON-BT-200', '1'); clica('#btnContinuar'); pg.wait_for_timeout(300)
        pg.fill('#finDesconto', '%s%%' % (lim + 1)); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
        escolhe('selAddReceb', 'pix'); dar_pdv()
        clica('#btnFinalizar'); pg.wait_for_timeout(350)
        ok(modal_aberto() and 'Liberar desconto' in texto_modal(), 'controle: %s%% na venda pede a liberação (o limite da pessoa vale só para o desconto manual)' % (lim + 1))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # sem o desconto dado, o registro nao traz vendaNossa
        pdv_cobra('FON-BT-200', '1', 'pix')
        clica('#btnFinalizar'); pg.wait_for_timeout(450); fecha_aviso()
        v = ev("ultimaVenda")
        ok(v['vendaNossa'] is None and perto(v['total'], 249.9), 'venda sem o desconto dado: vendaNossa é null e o total é o cheio (R$ 249,90)')

    # ------------------------------------------------------------------------------------------------
    if secao(4, 'O Pedido de Venda'):
        limpar()
        ped_novo('MOB-4002', '1', 'pix')
        ok(vis('#vnOpcao') and txt('#btnVendaNossa') == 'Dar o desconto da venda nossa (5%)', 'sem vendedor, sem indicação e com Pix aparece "Dar o desconto da venda nossa (5%%)": %s' % txt('#btnVendaNossa'))
        ok(not vis('#vnLinha') and txt('#totGeral') == 'R$ 79,90', 'e o total da venda segue cheio (R$ 79,90) até dar o desconto')
        escolhe('inputRecebimento', 'dinheiro')
        ok(vis('#vnOpcao'), 'com dinheiro também aparece')
        escolhe('inputRecebimento', 'credito')
        ok(not vis('#boxVendaNossa'), 'com cartão, não aparece')
        escolhe('inputRecebimento', 'boleto')
        ok(not vis('#boxVendaNossa'), 'com boleto (qualquer outra forma), não aparece')
        escolhe('inputRecebimento', 'pix'); escolhe('inputVendedor', 'Marina Costa')
        ok(not vis('#boxVendaNossa'), 'com vendedor escolhido, não aparece')
        escolhe('inputVendedor', '')
        ok(vis('#vnOpcao'), 'sem vendedor de novo, volta')
        ev("PEDIDO.ind = { nome: 'Afiliado Teste', pct: 3 }; recalcularTotais()")
        ok(not vis('#boxVendaNossa'), 'com indicação (cliente afiliado), não aparece')
        ev("PEDIDO.ind = null; recalcularTotais()")
        ev("PEDIDO.canal = 'loja_virtual'; recalcularTotais()")
        ok(not vis('#boxVendaNossa'), 'pedido da loja virtual (o pagamento vem da vitrine), não aparece')
        ev("PEDIDO.canal = 'manual'; recalcularTotais()")
        ok(vis('#vnOpcao'), 'pedido digitado de novo, volta')
        # --- o valor
        dar_ped()
        ok(vis('#vnLinha') and not vis('#vnOpcao') and txt('#vnRotulo') == 'Desconto da venda nossa (5%)' and txt('#totVendaNossa') == '− R$ 4,00', 'dar o desconto mostra a linha entre os totais: %s | %s' % (txt('#vnRotulo'), txt('#totVendaNossa')))
        ok(txt('#totGeral') == 'R$ 75,90', 'o total da venda desconta: R$ 75,90 (%s)' % txt('#totGeral'))
        ok(ev("PEDIDO.vendaNossa") == {'pct': 5, 'valor': 4, 'cortado': 0}, 'o pedido guarda vendaNossa { pct, valor, cortado }: %s' % ev("PEDIDO.vendaNossa"))
        ok([x['valor'] for x in ev("planoDeParcelas()")] == [75.9], 'o plano de parcelas (e a conta a receber) segue o total com o desconto: R$ 75,90')
        foto('pedido-totais-claro.png')
        clica('#btnTirarVendaNossa'); pg.wait_for_timeout(200)
        ok(not vis('#vnLinha') and vis('#vnOpcao') and txt('#totGeral') == 'R$ 79,90' and ev("PEDIDO.vendaNossa") is None and not modal_aberto(), '"tirar" tira na hora, sem código')
        params(comissaoPadraoPct=4); ir(PEDD, '?novo=1'); escolhe('inputLoja', 1)
        ped_campo(0, 'sku', 'MOB-4002'); ped_campo(0, 'qtd', '1'); escolhe('inputRecebimento', 'pix'); dar_ped()
        ok(txt('#totVendaNossa') == '− R$ 3,20' and txt('#vnRotulo') == 'Desconto da venda nossa (4%)' and txt('#totGeral') == 'R$ 76,70', 'com 4%% em Parâmetros de vendas o desconto é de 4%%: %s | %s' % (txt('#totVendaNossa'), txt('#totGeral')))
        ev("localStorage.removeItem('deskParametros')")
        # --- pagamento dividido: o vale-compra paga uma parte e o Pix a outra
        ped_novo('MOB-4002', '1', 'pix')
        ev("VALE.edita = true; VALE.txt = '29,90'; recalcularTotais()")
        dar_ped()
        ok(txt('#totVendaNossa') == '− R$ 2,50', 'R$ 29,90 no vale-compra e R$ 50,00 no Pix: o desconto é só de 5%% dos R$ 50,00, R$ 2,50: %s' % txt('#totVendaNossa'))
        ok(txt('#totGeral') == 'R$ 77,40' and 'R$ 47,50' in ev("document.getElementById('previaParcelas').textContent"), 'o total é R$ 77,40 e as parcelas somam o que falta depois do vale (R$ 47,50)')
        ev("VALE.edita = false; VALE.txt = ''")
        # --- a trava
        ped_novo('PAP-3001', '1', 'pix'); dar_ped()
        ok(txt('#totVendaNossa') == '− R$ 0,03', 'a trava corta no mínimo (PAP-3001): R$ 0,03: %s' % txt('#totVendaNossa'))
        ok(modal_aberto() and 'ficou em R$ 0,03' in texto_modal() and 'R$ 0,90 cortados' in texto_modal() and 'chegou ao preço mínimo' in texto_modal(), 'o aviso diz quanto foi cortado: %s' % (texto_modal() if modal_aberto() else '(sem aviso)'))
        ok(ev("ITENS[0].nome") in texto_modal(), 'e em qual produto')
        fecha_aviso()
        ok(vis('#vnCorte') and 'R$ 0,90 cortados' in txt('#vnCorte'), 'o aviso fica escrito embaixo da linha')
        alto = ev("[document.getElementById('boxVendaNossa').contains(document.getElementById('vnCorte')), document.getElementById('boxVendaNossa').offsetHeight, document.getElementById('inputDesconto').closest('.total-item').offsetHeight]")
        ok(not alto[0] and alto[1] <= alto[2] + 2, 'o aviso fica embaixo dos totais, fora do card, e o card não estica a fileira (%spx, o do desconto do pedido %spx)' % (alto[1], alto[2]))
        ped_novo('MOB-4002', '1', 'pix'); ped_campo(0, 'precoLista', '72,00'); dar_ped()
        ok(txt('#totVendaNossa') == '− R$ 2,08', 'com o preço digitado perto do mínimo (R$ 72,00, mínimo de R$ 69,92): R$ 2,08: %s' % txt('#totVendaNossa'))
        fecha_aviso()
        # --- vendedor e indicacao tiram o desconto, com aviso
        ped_novo('MOB-4002', '1', 'pix'); dar_ped()
        escolhe('inputVendedor', 'Marina Costa')
        ok(modal_aberto() and 'O desconto da venda nossa saiu' in texto_modal() and 'vendedor' in texto_modal(), 'escolher o vendedor avisa: %s' % (texto_modal() if modal_aberto() else '(sem aviso)'))
        fecha_aviso()
        ok(not vis('#boxVendaNossa') and txt('#totGeral') == 'R$ 79,90' and ev("PEDIDO.vendaNossa") is None, 'e o total volta ao cheio')
        escolhe('inputVendedor', '')
        ok(vis('#vnOpcao') and not vis('#vnLinha'), 'tirar o vendedor depois não devolve o desconto sozinho: o link volta')
        dar_ped()
        ev("PEDIDO.ind = { nome: 'Afiliado Teste', pct: 3 }; recalcularTotais()"); pg.wait_for_timeout(200)
        ok(modal_aberto() and 'O desconto da venda nossa saiu' in texto_modal() and 'indicação' in texto_modal(), 'chegar uma indicação avisa também: %s' % (texto_modal() if modal_aberto() else '(sem aviso)'))
        fecha_aviso()
        ev("PEDIDO.ind = null")
        # --- sem codigo e fora do limite; salvar
        ped_novo('FON-BT-200', '1', 'pix'); dar_ped()
        ok(ev("autoLimiteVenda().pct") == 10, 'o Pedido traz de fábrica o limite do sistema (10%, o mesmo do PDV): sem vendedor ele não fica sem limite')
        pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))")
        lim = ev("autoLimiteVenda().pct")
        pg.fill('#inputDesconto', '%s%%' % lim); ev("document.getElementById('inputDesconto').dispatchEvent(new Event('input', { bubbles: true }))")
        ok(txt('#totVendaNossa') == '− R$ 11,25' and txt('#totGeral') == 'R$ 213,66', 'R$ 249,90 com %s%% no pedido: 5%% de R$ 224,91 = R$ 11,25, total R$ 213,66: %s | %s' % (lim, txt('#totVendaNossa'), txt('#totGeral')))
        ev("PARAM.bloquearPedidoAtrasoDias = 0"); clica('#btnSalvar'); pg.wait_for_timeout(300)
        ok(modal_aberto() and 'Pedido salvo' in texto_modal() and 'Liberar desconto' not in texto_modal(), 'com o desconto no limite (%s%%) o pedido salva sem pedir liberação: o da venda nossa não entra no limite' % lim)
        ok('R$ 213,66' in texto_modal(), 'a conta a receber nasce com o total já com o desconto (R$ 213,66): %s' % texto_modal()[:150])
        fecha_aviso(); pg.wait_for_timeout(200)
        ok(ev("PEDIDO.vendaNossa") == {'pct': 5, 'valor': 11.25, 'cortado': 0}, 'o pedido salvo grava vendaNossa { pct, valor, cortado }: %s' % ev("PEDIDO.vendaNossa"))
        ped_novo('FON-BT-200', '1', 'pix'); dar_ped()
        pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))")
        pg.fill('#inputDesconto', '%s%%' % (lim + 1)); ev("document.getElementById('inputDesconto').dispatchEvent(new Event('input', { bubbles: true }))")
        ev("PARAM.bloquearPedidoAtrasoDias = 0"); clica('#btnSalvar'); pg.wait_for_timeout(300)
        ok(modal_aberto() and 'Liberar desconto' in texto_modal(), 'controle: %s%% no pedido pede a liberação (o limite da pessoa continua valendo)' % (lim + 1))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # --- aberto so para leitura (o nº 14: digitado, sem vendedor, no Pix), sem o desconto dado: nada de card vazio nos totais
        ir(PEDD, '?id=14')
        ok(ev("PEDIDO.canal") == 'manual' and ev("document.body.classList.contains('modo-leitura')") and not vis('#boxVendaNossa'), 'pedido aberto só para leitura, sem o desconto dado: a caixa não aparece vazia')

    # ------------------------------------------------------------------------------------------------
    if secao(5, 'Os dois temas, 1280 e 1440'):
        limpar()
        for w in (1280, 1440):
            for tema in ('claro', 'escuro'):
                pg.set_viewport_size({'width': w, 'height': 900})
                pdv_cobra('PAP-3001', '1', 'pix'); dar_pdv(); fecha_aviso()
                ev("document.body.classList.%s('dark')" % ('add' if tema == 'escuro' else 'remove'))
                pg.wait_for_timeout(500)   # a troca de tema tem transicao
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.getElementById('finVendaNossaCorte')).fontFamily.indexOf('Nunito') >= 0, getComputedStyle(document.getElementById('btnTirarVendaNossa')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True, True], 'PDV, cobrança com o desconto da venda nossa cortado, a %d, tema %s: sem barra para o lado, Nunito: %s' % (w, tema, r))
                if w == 1440:
                    foto('pdv-cobranca-%s.png' % tema)
                ped_novo('PAP-3001', '1', 'pix'); dar_ped(); fecha_aviso()
                ev("document.body.classList.%s('dark')" % ('add' if tema == 'escuro' else 'remove'))
                pg.wait_for_timeout(500)   # a troca de tema tem transicao
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.getElementById('vnCorte')).fontFamily.indexOf('Nunito') >= 0, getComputedStyle(document.getElementById('btnTirarVendaNossa')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True, True], 'Pedido, totais com o desconto da venda nossa cortado, a %d, tema %s: sem barra para o lado, Nunito: %s' % (w, tema, r))
                if w == 1440:
                    ev("document.getElementById('boxVendaNossa').scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(150)
                    foto('pedido-totais-%s.png' % tema)
        pg.set_viewport_size({'width': 1440, 'height': 900})

    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript em toda a suíte: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
