# -*- coding: utf-8 -*-
# Pedido de Venda no cartao: as contas a receber pelo gateway (ajuste do teste de 22/out/2026, §14.96).
#
# Antes, o cartao parcelado virava N contas a receber, uma por mes, sem olhar o gateway. O certo, com gateway
# ANTECIPADO (a InfinitePay), e UMA conta: o valor inteiro menos a taxa, no dia util seguinte, na conta do gateway.
# Este arquivo protege a regra nova, e que as outras formas seguem como eram:
#   [1] o pedido online no credito: uma conta, taxa igual a do "Resultado do pedido", vencimento em dia util
#   [2] o pedido de outro canal: gateway padrao da forma, credito (a vista e parcelado) e debito
#   [3] o gateway sem antecipacao: N contas, a parte da taxa de cada uma, os vencimentos mes a mes
#   [4] sem gateway ou sem condicao: o aviso fica a vista e o Salvar bloqueia (a regra do PDV)
#   [5] Boleto, Crediario, Pix e as outras formas como eram; trocar a forma recalcula; o vale-compra
#   [6] o Salvar anuncia o mesmo plano
#
# O relogio do navegador e fixado numa sexta (30/10/2026): o dia util seguinte pula sabado, domingo e o feriado de
# Finados (02/11) e cai na terca 03/11. Dia corrido daria 31/10, e a suite pega isso em qualquer dia em que rode.
# A conta e refeita aqui em Python (Decimal, meio para cima), sem ler nada do codigo da tela.
from playwright.sync_api import sync_playwright
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import os, glob, re
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
DET = 'pagina-vendas-pedidos-detalhe.html'
HOJE = date(2026, 10, 30)   # sexta-feira
FERIADOS = {(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25)}
LINK = '../integracoes/pagina-integracoes-gateways.html'

falhas = []


def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c:
        falhas.append(m)


def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e


# ---------------------------------------------------------------- a conta refeita em Python
def cent(x):
    return Decimal(x).quantize(Decimal('0.01'), ROUND_HALF_UP)


def util(d):
    return d.weekday() < 5 and (d.month, d.day) not in FERIADOS


def mais_uteis(d, n):
    while n > 0:
        d += timedelta(days=1)
        if util(d):
            n -= 1
    return d


def para_util(d):
    while not util(d):
        d += timedelta(days=1)
    return d


def mais_meses(d, n):
    m = d.month - 1 + n
    ano, mes = d.year + m // 12, m % 12 + 1
    dia = d.day
    while True:
        try:
            return date(ano, mes, dia)
        except ValueError:
            dia -= 1


def dividir(valor, n):
    c = int(cent(valor) * 100)
    base = c // n
    return [Decimal(base + (c - base * n if i == 0 else 0)) / 100 for i in range(n)]


def br(v):
    s = '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('− ' if float(v) < 0 else '') + 'R$ ' + s


def dbr(d):
    return d.strftime('%d/%m/%Y')


def num(t):
    return Decimal(t.replace('R$', '').replace('−', '-').replace(' ', '').replace('.', '').replace(',', '.'))


def taxa_de(total, pct, tarifa=0):
    return cent(Decimal(str(total)) * Decimal(str(pct)) / 100 + Decimal(str(tarifa)))


# As taxas conferidas a mao, das tabelas de fabrica (Link da InfinitePay = loja virtual; Maquininha Bronze = Outro):
LINK_TAXAS = {1: 4.20, 2: 6.09, 3: 7.01, 4: 7.91, 5: 8.80, 6: 9.67, 7: 12.59, 8: 13.42, 9: 14.25, 10: 15.06, 11: 15.87, 12: 16.66}
BRONZE_VM = {'debito': 1.37, 1: 3.15, 2: 5.39, 3: 6.12}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    pg = ctx.new_page()
    pg.clock.set_fixed_time(datetime(2026, 10, 30, 10, 0, 0))
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if (m.type == 'error' and not ruido(m.text)) else None)
    pg.on('dialog', lambda d: d.dismiss())

    def abre(qs='', espera=500):
        erros.clear()
        pg.goto(localiza.uri(DET) + qs); pg.wait_for_timeout(espera)

    def gateways(js):
        """Mexe na copia do gateway que o navegador guarda (a copia do teste), com `js` operando sobre `d.gateways`."""
        pg.evaluate("(function(){ var d = JSON.parse(localStorage.getItem('deskGateways')); " + js + " localStorage.setItem('deskGateways', JSON.stringify(d)); })()")

    def escolhe(idsel, valor):
        if not pg.is_visible('#%s .dropdown-select-btn' % idsel):
            # pedido da loja virtual: forma e condicao travadas (27/out/2026). Estas secoes simulam a troca por dentro, para provar a conta a receber em outras formas.
            pg.evaluate("(a) => { document.getElementById(a[0]).setAttribute('data-value', a[1]); recalcularTotais(); }", [idsel, valor]); pg.wait_for_timeout(250)
            return
        pg.click('#%s .dropdown-select-btn' % idsel); pg.wait_for_timeout(150)
        pg.click('#%s .dropdown-select-item[data-value="%s"]' % (idsel, valor)); pg.wait_for_timeout(250)

    def chips():
        r = pg.evaluate("""Array.from(document.querySelectorAll('#previaParcelas .parcela-chip')).map(c =>
            [c.children[0].textContent, c.children[1].textContent, c.children[2].textContent, c.title])""")
        out = []
        for n, liq, venc, tit in r:
            m = re.match(r'Bruto (R\$ [\d.,]+) · taxa (R\$ [\d.,]+) · líquido (R\$ [\d.,]+)', tit)
            out.append({'n': n, 'liq': liq, 'venc': venc, 'bruto': m.group(1) if m else None, 'taxa': m.group(2) if m else None, 'liqt': m.group(3) if m else None})
        return out

    def nota():
        return pg.inner_text('#notaCartao').replace('\n', ' ') if pg.query_selector('#notaCartao') else ''

    def total_tela():
        return num(pg.inner_text('#totGeral'))

    def taxa_resultado():
        return pg.evaluate("""(Array.from(document.querySelectorAll('#resLinhas .ped-res-linha')).filter(l => l.textContent.indexOf('Taxa do gateway') >= 0)[0] || {querySelector: () => ({textContent: ''})}).querySelector('b').textContent""")

    def aviso_salvar(prep=''):
        """Clica em Salvar (sem trava de atraso) e devolve o texto do modal."""
        pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0;" + prep); pg.wait_for_timeout(100)
        pg.click('#btnSalvar'); pg.wait_for_timeout(450)
        return pg.inner_text('#confirmModalTexto').replace('\n', ' ')

    def fecha_modal():
        pg.evaluate("fecharModalConfirmacao()"); pg.wait_for_timeout(150)

    # =======================================================================
    abre('?id=1'); pg.evaluate("localStorage.clear()")   # navegador limpo: o exemplo de gateways nasce igual para todos
    print('\n[1] Pedido online no credito: uma conta so, com a taxa do Resultado do pedido')
    abre('?id=1')
    ok(not erros, 'sem erro de JS na abertura' + (' — ' + erros[0] if erros else ''))
    ok(pg.evaluate("new Date().getDate()") == 30, 'o relógio do teste está fixo na sexta 30/10/2026')
    tot = total_tela()
    ok(tot == Decimal('1890.00'), 'o pedido nº 1 vale R$ 1.890,00: %s' % tot)
    cs = chips()
    taxa1 = taxa_de(1890, LINK_TAXAS[3])
    ok(len(cs) == 1, 'crédito Visa 3x na InfinitePay (antecipada): UMA conta, não três: %d chips' % len(cs))
    ok(taxa1 == Decimal('132.49'), 'a conta à mão: 7,01% de 1.890,00 = 132,49 (o 6,09% é o 2x da tabela, não o 3x)')
    if cs:
        c = cs[0]
        ok(c['n'] == '1/1', 'o chip diz 1/1: %s' % c['n'])
        ok(c['bruto'] == br(1890) and c['taxa'] == br(taxa1) and c['liq'] == br(1890 - taxa1) and c['liqt'] == c['liq'],
           'bruto %s, taxa %s e líquido %s' % (c['bruto'], c['taxa'], c['liq']))
        ok(c['venc'] == dbr(mais_uteis(HOJE, 1)) == '03/11/2026', 'vence no dia útil seguinte (sexta → pula sábado, domingo e o feriado de 02/11): %s' % c['venc'])
        ok(pg.evaluate("getComputedStyle(document.querySelector('#previaParcelas .parcela-chip b')).fontWeight") in ('800', '700', 'bold'), 'o líquido está em negrito')
    n = nota()
    esperada = ('No cartão em 3x do cliente, o gateway antecipado deposita tudo de uma vez: nasce 1 conta a receber de %s, com %s de taxa, %s em 03/11, na conta InfinitePay — loja virtual.'
                % (br(1890), br(taxa1), br(1890 - taxa1)))
    ok(n == esperada, 'a nota: %s' % n)
    ok('Salvar faz nascer' not in pg.inner_text('#previaParcelas'), 'e não diz mais "uma conta por parcela"')
    ok(taxa_resultado() == br(taxa1), 'a taxa é o mesmo número do "Resultado do pedido": %s' % taxa_resultado())
    conta = pg.evaluate("planoDoCartao(1890).itens[0].conta")
    ok(conta['nome'] == 'InfinitePay — loja virtual' and conta['id'] == 'gw1', 'a conta a receber é a do gateway (gw1): %s' % conta)
    # os 6 pedidos online no credito, cada um com a sua bandeira e parcelas
    for pid, vezes in ((1, 3), (4, 1), (8, 6), (11, 2), (12, 10), (16, 12)):
        abre('?id=%d' % pid)
        t = total_tela(); cs = chips()
        # O pedido nº 16 tem R$ 25,00 pagos em vale-compra no exemplo: a conta (e a taxa) e so do que falta receber.
        vale = Decimal(25) if pid == 16 else Decimal(0)
        t = t - vale; tx = taxa_de(t, LINK_TAXAS[vezes])
        certo = len(cs) == 1 and cs[0]['n'] == '1/1' and cs[0]['taxa'] == br(tx) and cs[0]['liq'] == br(t - tx) and cs[0]['bruto'] == br(t) and cs[0]['venc'] == '03/11/2026'
        ok(certo, 'pedido nº %d (%dx, %s): 1 conta de %s, taxa %s, líquido %s' % (pid, vezes, t, br(t), br(tx), br(t - tx)) + ('' if certo else ' — veio %s' % cs))
        if vale:
            ok('R$ 25,00 pagos com vale-compra' in pg.inner_text('#previaParcelas'), 'pedido nº %d: a nota do vale (R$ 25,00) está lá, e a conta é só do que falta receber' % pid)
        else:
            ok(taxa_resultado() == br(tx), 'pedido nº %d: a taxa é a do Resultado do pedido (%s)' % (pid, taxa_resultado()))

    # =======================================================================
    print('\n[2] Pedido de outro canal: o gateway padrão da forma')
    abre('?id=2&editar=1')
    tot = total_tela()
    ok(pg.evaluate("PEDIDO.canal") == 'manual', 'o pedido nº 2 é venda manual (R$ %s)' % tot)
    escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    cs = chips(); tx = taxa_de(tot, BRONZE_VM[3])
    certo = len(cs) == 1 and cs[0]['n'] == '1/1' and cs[0]['taxa'] == br(tx) and cs[0]['liq'] == br(tot - tx) and cs[0]['venc'] == '03/11/2026'
    ok(certo, 'crédito 3x na maquininha padrão (Bronze, antecipada, Visa 6,12%%): 1 conta, taxa %s, líquido %s' % (br(tx), br(tot - tx)) + ('' if certo else ' — veio %s' % cs))
    ok('InfinitePay Maquininha — Bronze' in nota() and 'No cartão em 3x do cliente' in nota(), 'a nota diz a conta da maquininha: %s' % nota())
    escolhe('inputCondicao', '1')
    cs = chips(); tx = taxa_de(tot, BRONZE_VM[1])
    ok(len(cs) == 1 and cs[0]['taxa'] == br(tx) and nota().startswith('No cartão à vista do cliente'), 'crédito à vista: 1 conta, taxa de 3,15%% (%s) e a nota diz "à vista": %s' % (br(tx), nota()[:40]))
    escolhe('inputRecebimento', 'debito')
    cs = chips(); tx = taxa_de(tot, BRONZE_VM['debito'])
    ok(len(cs) == 1 and cs[0]['taxa'] == br(tx) and cs[0]['liq'] == br(tot - tx) and cs[0]['venc'] == '03/11/2026', 'débito: 1 conta, taxa de 1,37%% (%s)' % br(tx) + ('' if len(cs) == 1 else ' — veio %s' % cs))
    ok(nota().startswith('No débito do cliente'), 'a nota diz "No débito": %s' % nota()[:40])
    escolhe('inputCondicao', '6')
    ok(len(chips()) == 1 and 'No débito' in nota(), 'no débito as parcelas do cliente não contam: com 6x marcado, continua 1 conta')

    # =======================================================================
    print('\n[3] Gateway sem antecipação: uma conta por parcela')
    abre('?id=2&editar=1')
    gateways("d.gateways.forEach(function(g){ if (g.descricao.indexOf('Bronze') >= 0) g.antecipacao = 'sem'; });")
    abre('?id=2&editar=1')
    tot = total_tela()
    escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    cs = chips(); tx = taxa_de(tot, BRONZE_VM[3])
    vals = dividir(tot, 3); taxs = dividir(tx, 3)
    primeiro = mais_uteis(HOJE, 1)
    vencs = [dbr(primeiro)] + [dbr(para_util(mais_meses(primeiro, i))) for i in (1, 2)]
    ok(len(cs) == 3, 'crédito 3x sem antecipação: 3 contas: %d' % len(cs))
    if len(cs) == 3:
        ok([c['n'] for c in cs] == ['1/3', '2/3', '3/3'], 'os chips são 1/3, 2/3 e 3/3')
        ok([c['bruto'] for c in cs] == [br(v) for v in vals] and vals[0] > vals[1] == vals[2], 'a divisão de centavos fica na primeira: %s' % [c['bruto'] for c in cs])
        ok([c['taxa'] for c in cs] == [br(v) for v in taxs] and sum(taxs) == tx, 'cada parcela com a sua parte da taxa (soma %s, a do Resultado): %s' % (br(tx), [c['taxa'] for c in cs]))
        ok([c['liq'] for c in cs] == [br(v - t) for v, t in zip(vals, taxs)], 'o líquido de cada uma: %s' % [c['liq'] for c in cs])
        ok([c['venc'] for c in cs] == vencs, 'vencimentos: a primeira no prazo do gateway (dia útil), as outras um mês depois, passadas pelo dia útil: %s' % [c['venc'] for c in cs])
    ok(vencs == ['03/11/2026', '03/12/2026', '04/01/2027'], 'a conta à mão dos vencimentos: 03/11, 03/12 e 04/01 (o dia 03/01 é domingo)')
    n = nota()
    ok('o gateway sem antecipação' in n and 'nascem 3 contas a receber' in n and 'InfinitePay Maquininha — Bronze' in n and br(tot - tx) in n and br(tx) in n, 'a nota diz quantas, a conta e o líquido total: %s' % n)
    ok(taxa_de(tot, BRONZE_VM[3]) == tx and sum(num(c['liqt']) for c in cs) == tot - tx, 'a soma do líquido das parcelas é o líquido total (%s)' % br(tot - tx))
    escolhe('inputCondicao', '1')
    ok(len(chips()) == 1 and chips()[0]['n'] == '1/1', 'sem antecipação à vista: 1 conta')
    # pedido online com o gateway da loja virtual sem antecipação
    gateways("d.gateways.forEach(function(g){ if (g.tipo === 'infinitepay') g.antecipacao = 'sem'; });")
    abre('?id=1')
    cs = chips(); tx = taxa_de(1890, LINK_TAXAS[3]); vals = dividir(1890, 3); taxs = dividir(tx, 3)
    ok(len(cs) == 3 and [c['taxa'] for c in cs] == [br(v) for v in taxs] and [c['bruto'] for c in cs] == [br(v) for v in vals],
       'pedido nº 1 com a InfinitePay da loja virtual sem antecipação: 3 contas de %s, com a taxa repartida (total %s)' % ([c['bruto'] for c in cs], br(tx)))
    ok(taxa_resultado() == br(tx) and sum(taxs) == tx, 'e a soma das taxas é a do Resultado do pedido')

    # =======================================================================
    print('\n[4] Sem gateway ou sem condição: aviso à vista e Salvar bloqueado')
    abre('?id=1'); pg.evaluate("localStorage.clear()"); abre('?id=1&editar=1')
    pg.evaluate("PEDIDO.pagamento.bandeira = 'hipercard'; recalcularTotais();"); pg.wait_for_timeout(200)
    vis = pg.evaluate("(function(){ var e = document.getElementById('erroCartao'); return !!e && e.offsetParent !== null; })()")
    txt = pg.inner_text('#previaParcelas').replace('\n', ' ')
    ok(vis and 'não tem a condição do cartão de crédito Hipercard em 3x' in txt, 'bandeira sem linha no gateway: o aviso diz o motivo: %s' % txt)
    ok(pg.evaluate("document.querySelector('#erroCartao a').getAttribute('href')") == LINK, 'e leva para Gateways de Pagamento')
    ok(pg.query_selector('#previaParcelas .parcela-chip') is None, 'sem conta desenhada')
    t = aviso_salvar()
    ok('não pode ser salvo' in t and 'não tem a condição do cartão de crédito Hipercard em 3x' in t and 'ficou reservado' not in t, 'Salvar bloqueado, com o motivo: %s' % t[:200])
    fecha_modal()
    # débito: a InfinitePay da loja virtual não tem débito
    abre('?id=1&editar=1'); escolhe('inputRecebimento', 'debito')
    ok(pg.query_selector('#erroCartao') is not None and 'não tem a condição do cartão de débito Visa' in pg.inner_text('#erroCartao'), 'débito no pedido da loja virtual (sem linha de débito no Link): aviso: %s' % pg.inner_text('#previaParcelas')[:90])
    t = aviso_salvar()
    ok('não pode ser salvo' in t, 'e Salvar bloqueia')
    fecha_modal()
    # gateway da loja virtual desabilitado
    gateways("d.gateways.forEach(function(g){ if (g.tipo === 'infinitepay') g.situacao = 'desabilitado'; });")
    abre('?id=1&editar=1')
    ok('não tem gateway InfinitePay habilitado para a loja virtual' in pg.inner_text('#previaParcelas'), 'sem a InfinitePay habilitada na loja: aviso: %s' % pg.inner_text('#previaParcelas')[:100])
    t = aviso_salvar()
    ok('não pode ser salvo' in t and 'InfinitePay habilitado' in t, 'Salvar bloqueia')
    fecha_modal()
    # pedido manual: nenhum gateway habilitado
    gateways("d.gateways.forEach(function(g){ g.situacao = 'desabilitado'; });")
    abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito')
    ok('Não há gateway nem maquininha habilitados nesta loja para o cartão de crédito' in pg.inner_text('#previaParcelas') and pg.query_selector('#erroCartao a') is not None, 'sem nenhum gateway habilitado: aviso com o link: %s' % pg.inner_text('#previaParcelas')[:100])
    t = aviso_salvar()
    ok('não pode ser salvo' in t and 'Não há gateway nem maquininha habilitados' in t, 'Salvar bloqueia')
    fecha_modal()
    # boleto no mesmo pedido: nada de gateway, salva
    escolhe('inputRecebimento', 'boleto')
    ok(pg.query_selector('#erroCartao') is None, 'trocando para boleto o aviso do cartão sai')
    # o gateway padrão sem a linha da condição
    abre('?id=2'); pg.evaluate("localStorage.clear()"); abre('?id=2&editar=1')
    gateways("d.gateways.forEach(function(g){ if (g.descricao.indexOf('Bronze') >= 0) g.condicoes = g.condicoes.filter(function(c){ return !(c.forma === 'credito' && c.bandeira === 'visa' && c.parcelas === 3); }); });")
    abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    ok('não tem a condição do cartão de crédito Visa em 3x' in pg.inner_text('#previaParcelas'), 'o padrão da forma sem o 3x da Visa: aviso: %s' % pg.inner_text('#previaParcelas')[:100])
    escolhe('inputCondicao', '2')
    ok(pg.query_selector('#erroCartao') is None and len(chips()) == 1, 'e no 2x, que o gateway tem, o aviso sai e a conta aparece')

    # =======================================================================
    print('\n[5] As outras formas como eram; trocar a forma recalcula; o vale-compra')
    abre('?id=1'); pg.evaluate("localStorage.clear()"); abre('?id=1&editar=1')
    escolhe('inputRecebimento', 'boleto')
    cs = chips(); partes = dividir(1890, 3)
    ok(len(cs) == 3 and [c['liq'] for c in cs] == [br(v) for v in partes], 'boleto 3x no pedido nº 1: as 3 parcelas de %s, como sempre' % br(partes[0]))
    ok([c['venc'] for c in cs] == [dbr(mais_meses(HOJE, i)) for i in range(3)], 'com o vencimento mensal de sempre, em dias corridos: %s' % [c['venc'] for c in cs])
    txt = pg.inner_text('#previaParcelas').replace('\n', ' ')
    ok('Salvar faz nascer 3 contas a receber, uma por parcela' in txt and 'A diferença de centavos da divisão fica na primeira parcela' in txt and 'líquido' not in txt, 'a nota é a de sempre: %s' % txt[-170:])
    ok(pg.query_selector('#erroCartao') is None and pg.query_selector('#notaCartao') is None, 'sem aviso e sem nota de cartão')
    escolhe('inputRecebimento', 'crediario')
    ok(len(chips()) == 3, 'crediário 3x: 3 parcelas')
    escolhe('inputRecebimento', 'pix'); escolhe('inputCondicao', '1')
    ok(pg.evaluate("document.getElementById('linhaParcelas').style.display") == 'none', 'Pix à vista: sem parcelas')
    escolhe('inputRecebimento', 'dinheiro'); escolhe('inputCondicao', '3')
    ok(len(chips()) == 3, 'dinheiro 3x segue como era (a divisão simples): 3 parcelas')
    # trocar a forma recalcula
    escolhe('inputRecebimento', 'credito')
    cs = chips(); tx = taxa_de(1890, LINK_TAXAS[3])
    ok(len(cs) == 1 and cs[0]['liq'] == br(1890 - tx), 'de dinheiro para crédito: a lista vira 1 conta de %s' % br(1890 - tx))
    escolhe('inputRecebimento', 'boleto')
    ok(len(chips()) == 3 and pg.query_selector('#notaCartao') is None, 'e de volta para boleto: as 3 parcelas')
    # a loja do pedido manda no gateway do canal (loja virtual): trocar de loja recalcula
    escolhe('inputRecebimento', 'credito')
    escolhe('inputLoja', '3')
    ok('não tem gateway InfinitePay habilitado para a loja virtual' in pg.inner_text('#previaParcelas'), 'pedido da loja virtual passado para a Desk Tech (sem vitrine): sem InfinitePay na loja, aviso')
    escolhe('inputLoja', '1')
    ok(len(chips()) == 1, 'e de volta à Desk Shope, a conta volta')
    # o vale-compra: a taxa e sobre o que falta receber
    pg.evaluate("renderParcelas(1000, 890)"); pg.wait_for_timeout(100)
    cs = chips(); tx = taxa_de(1000, LINK_TAXAS[3])
    ok(len(cs) == 1 and cs[0]['bruto'] == br(1000) and cs[0]['taxa'] == br(tx) and cs[0]['liq'] == br(1000 - tx), 'com R$ 890,00 pagos em vale, a conta é de R$ 1.000,00 e a taxa é sobre ela (%s)' % br(tx))
    ok('R$ 890,00 pagos com vale-compra' in pg.inner_text('#previaParcelas'), 'e a nota do vale continua lá')
    pg.evaluate("renderParcelas(0, 1890)"); pg.wait_for_timeout(100)
    ok(pg.query_selector('#notaCartao') is None and pg.query_selector('#erroCartao') is None, 'vale pagando tudo: nada a receber, então sem nota nem aviso de cartão')

    # =======================================================================
    print('\n[6] O Salvar anuncia o mesmo plano')
    abre('?id=1'); pg.evaluate("localStorage.clear()"); abre('?id=1&editar=1')
    tx = taxa_de(1890, LINK_TAXAS[3])
    ok(pg.evaluate("fraseNascer(1890)") == 'a conta a receber de %s (líquido de %s em 03/11/2026, já sem a taxa de %s)' % (br(1890), br(1890 - tx), br(tx)), 'a pergunta antes de salvar: %s' % pg.evaluate("fraseNascer(1890)"))
    t = aviso_salvar()
    ok('Pedido salvo' in t and 'a conta a receber de %s nasceu em aberto, com %s de taxa: líquido de %s em 03/11/2026, na conta InfinitePay — loja virtual' % (br(1890), br(tx), br(1890 - tx)) in t,
       'a mensagem de salvar: %s' % t[:260])
    ok('3 contas' not in t, 'e não diz mais "3 contas"')
    fecha_modal()
    escolhe('inputRecebimento', 'boleto')
    t = aviso_salvar()
    ok('3 contas a receber nasceram em aberto, de %s a %s' % (br(630), br(630)) in t, 'boleto salva como sempre: %s' % t[:200])
    fecha_modal()
    abre('?id=1&editar=1')
    gateways("d.gateways.forEach(function(g){ if (g.tipo === 'infinitepay') g.antecipacao = 'sem'; });")
    abre('?id=1&editar=1')
    ok(pg.evaluate("fraseNascer(1890)").startswith('3 contas a receber, uma por parcela (líquido total de %s' % br(1890 - tx)), 'sem antecipação a pergunta diz 3 contas e o líquido total')
    t = aviso_salvar()
    ok('3 contas a receber nasceram em aberto, de %s a %s' % (br(630), br(630)) in t and 'líquido total de %s' % br(1890 - tx) in t and 'vencendo de 03/11/2026 a 04/01/2027' in t and 'na conta InfinitePay — loja virtual' in t,
       'e a mensagem de salvar diz as 3, o líquido total, os vencimentos e a conta: %s' % t[:300])
    fecha_modal()

    # =======================================================================
    print('\n[7] Ajustes de 27/out: pedido online com forma e condição travadas; pedido manual com o gateway do PDV')
    def travado():
        return pg.evaluate("""(function(){ var v = function(s){ var e = document.querySelector(s); return !!e && e.offsetParent !== null; };
          return { drops: [v('#inputRecebimento .dropdown-select-btn'), v('#inputCondicao .dropdown-select-btn')],
                   leitura: [v('[data-leitura=inputRecebimento]') ? document.querySelector('[data-leitura=inputRecebimento]').textContent : null, v('[data-leitura=inputCondicao]') ? document.querySelector('[data-leitura=inputCondicao]').textContent : null],
                   notas: Array.from(document.querySelectorAll('.ped-nota-pago')).filter(function(e){ return e.offsetParent !== null; }).map(function(e){ return e.textContent.trim(); }),
                   classe: document.body.classList.contains('pedido-online') }; })()""")
    abre('?id=1'); pg.evaluate("localStorage.clear()")
    for qs, forma, cond in (('?id=12', 'Cartão de crédito', '10x'), ('?id=12&editar=1', 'Cartão de crédito', '10x'), ('?id=3&editar=1', 'Pix', 'À vista'), ('?id=1', 'Cartão de crédito', '3x')):
        abre(qs); r = travado()
        ok(r['drops'] == [False, False] and r['leitura'] == [forma, cond] and r['notas'] == ['pago na loja virtual'] * 2 and r['classe'],
           'pedido online %s: forma e condição só de leitura (%s, %s), com a nota "pago na loja virtual": %s' % (qs, forma, cond, r))
    abre('?id=2&editar=1'); r = travado()
    ok(r['drops'] == [True, True] and r['notas'] == [] and not r['classe'], 'pedido manual segue editável, sem a nota: %s' % r)
    escolhe('inputRecebimento', 'credito')
    ok(pg.evaluate("document.getElementById('inputRecebimento').getAttribute('data-value')") == 'credito', 'e a forma do manual troca de verdade')
    abre('?clonar=11&id=11'); r = travado()
    ok(r['drops'] == [True, True] and r['notas'] == [] and not r['classe'], 'o clone de um pedido online vira venda manual e volta a ser editável: %s' % r)
    abre('?novo=1'); r = travado()
    ok(r['drops'] == [True, True] and r['notas'] == [], 'pedido novo: editável')

    def gateway_do_manual():
        return pg.evaluate("(function(){ var p = planoDoCartao(1000); return p ? [p.gateway ? p.gateway.descricao : null, p.motivo] : null; })()")
    abre('?id=1'); pg.evaluate("localStorage.clear()"); abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    ok(gateway_do_manual() == ['InfinitePay Maquininha — Bronze', ''], 'o padrão da forma (Bronze) está habilitado na loja do pedido (Desk Tech): é ele: %s' % gateway_do_manual())
    gateways("d.gateways.forEach(function(g){ if (g.id === 2) g.lojas = [1, 2]; if (g.id === 3) { g.situacao = 'habilitado'; g.lojas = [3]; } });")
    abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    ok(gateway_do_manual() == ['InfinitePay Maquininha — Prata', ''] and 'InfinitePay Maquininha — Prata' in nota(), 'o padrão (Bronze) não está habilitado na Desk Tech: vale a primeira maquininha habilitada nela (Prata): %s' % gateway_do_manual())
    escolhe('inputLoja', '1')
    ok(gateway_do_manual() == ['InfinitePay Maquininha — Bronze', ''] and 'InfinitePay Maquininha — Bronze' in nota(), 'trocar a loja do pedido para a Desk Shope recalcula: volta o padrão (Bronze): %s' % gateway_do_manual())
    escolhe('inputLoja', '3')
    ok(gateway_do_manual()[0] == 'InfinitePay Maquininha — Prata', 'e de volta à Desk Tech, a Prata')
    gateways("d.gateways.forEach(function(g){ if (g.id === 3) g.situacao = 'desabilitado'; });")
    abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito')
    r = gateway_do_manual()
    ok(r[0] is None and 'Não há gateway nem maquininha habilitados nesta loja' in r[1] and pg.query_selector('#erroCartao a') is not None, 'sem maquininha habilitada na loja: aviso com o link para Gateways: %s' % r)
    t = aviso_salvar()
    ok('não pode ser salvo' in t, 'e o Salvar bloqueia no cartão')
    fecha_modal()
    escolhe('inputLoja', '1')
    ok(pg.query_selector('#erroCartao') is None and len(chips()) == 1, 'trocar para a Desk Shope, onde o padrão está habilitado, tira o aviso')
    abre('?id=1'); pg.evaluate("localStorage.clear(); localStorage.setItem('deskParametros', JSON.stringify({ formaGatewayPadrao: { credito: 1 } }))")
    abre('?id=2&editar=1'); escolhe('inputRecebimento', 'credito'); escolhe('inputCondicao', '3')
    ok(gateway_do_manual()[0] == 'InfinitePay Maquininha — Bronze', 'padrão da forma fora da loja do pedido (a InfinitePay da loja virtual não atende a Desk Tech): cai na maquininha')
    escolhe('inputLoja', '1')
    ok(gateway_do_manual()[0] == 'InfinitePay — loja virtual', 'padrão da forma habilitado na loja do pedido (Desk Shope): é ele')
    pg.evaluate("localStorage.clear()")

    ok(not erros, 'sem erro de JS no caminho todo' + (' — ' + erros[0] if erros else ''))

    b.close()

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
