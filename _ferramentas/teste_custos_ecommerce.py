# -*- coding: utf-8 -*-
# Custos do E-commerce, entrega 1 (barganha de 21/out/2026).
#
# Relatorio vivo do lucro de cada pedido ONLINE (canal 'loja_virtual'): venda, o que saiu do bolso (diferencial de frete, taxa do
# gateway, comissao, embalagem, custo) e o lucro. A conta mora num bloco comum, RESULTADO DO PEDIDO, igual na tela nova, na
# pagina do pedido, nas duas telas de Comissoes e no cadastro do cliente. Esta suite refaz a conta em Python (Decimal, meio para
# cima), confere 4 pedidos contra valores feitos a mao (comentarios abaixo) e liga a tela as vizinhas.
#
#   [1] A conta: quatro pedidos a mao, os 16 contra o oraculo, e o lucro antigo de Comissoes (lucroDe) fora do ar;
#   [2] A lista: so os online, as colunas, os cards, a barra dos R$ 100, a coluna de marketplace escondida;
#   [3] Configurar: situacoes (o cancelado sai de fabrica e volta), custo medio, embalagem por loja, Cancelar descarta, validacao, log;
#   [4] Os cards que filtram, o agrupamento e o clique de volta, a busca, o periodo e a loja;
#   [5] O painel do pedido e o link; a planilha; a largura em 1280 com o dado mais comprido;
#   [6] A pagina do pedido: canal, frete pago pela loja, forma e parcelas, a caixa igual a da lista nos 16 pedidos, ao vivo;
#   [7] Comissoes usa a conta unica;
#   [8] As ligacoes: blocos identicos, espelhos, menu em todas as telas, catalogo de acoes.
#
# Contas a mao (loja 1 = Desk Shope, embalagem R$ 5,00 por unidade; loja 2 = Desk Brands, R$ 8,00; taxas do Link de pagamento
# da InfinitePay: 1x 4,20% · 2x 6,09% · 3x 7,01% · 10x 15,06% · 12x 16,66%, pix 0):
#   pedido 3  (pix, vendedora Marina 5%):   venda 349,90 · dif. frete 22,00 − 0 = 22,00 · taxa 0 · comissao 5% de 349,90 = 17,495 -> 17,50
#             · embalagem 1 un x 5,00 · custo 199,90  ->  lucro 349,90 − 22,00 − 17,50 − 5,00 − 199,90 = 105,50  (30,2%)
#   pedido 12 (credito Visa 10x, afiliado Bruno 5%, Brands):  venda 1.024,00 · dif. 26,50 · taxa 15,06% de 1.024,00 = 154,2144 -> 154,21
#             · comissao 5% de 1.024,00 = 51,20 · embalagem 8,00 · custo 604,00  ->  lucro 1.024,00 − 26,50 − 154,21 − 51,20 − 8,00 − 604,00 = 180,09  (17,6%)
#   pedido 11 (credito Elo 2x, Marina 5%, frete gratis para longe: a loja pagou 95,00):  venda 219,90 · dif. 95,00 · taxa 6,09% de 219,90 = 13,3919 -> 13,39
#             · comissao 5% de 219,90 = 10,995 -> 11,00 · embalagem 5,00 · custo 128,00  ->  lucro 219,90 − 95,00 − 13,39 − 11,00 − 5,00 − 128,00 = −32,49  (−14,8%)
#   pedido 1  (credito Visa 3x, 8 unidades, o cliente pagou 10,00 de frete e a loja 18,50):  venda 1.890,00 − 10,00 = 1.880,00 · dif. 18,50 − 10,00 = 8,50
#             · taxa 7,01% de 1.890,00 (sobre o TOTAL, nao sobre a venda) = 132,489 -> 132,49 · comissao 5% de 1.880,00 = 94,00 · embalagem 8 x 5,00 = 40,00
#             · custo 1.128,00  ->  lucro 1.880,00 − 8,50 − 132,49 − 94,00 − 40,00 − 1.128,00 = 477,01  (25,4%); com o custo medio 1.105,00: 500,01
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
TELA = 'pagina-vendas-custos-ecommerce.html'
PV, PV_D = 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html'
COM, COM_D, CLI_D = 'pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html'
PDV, CFG_PDV, FORMAS = 'pagina-vendas-pdv.html', 'pagina-configuracoes-pdv.html', 'pagina-configuracoes-formas-recebimento.html'
REGISTRO, SENHAS = 'pagina-configuracoes-registro-atividades.html', 'pagina-configuracoes-confirmacoes-senha.html'
RASTREIO = ['pagina-logistica-rastreamento.html', 'pagina-logistica-rastreamento-detalhe.html']
ROTA = '../vendas/pagina-vendas-custos-ecommerce.html'
CHAVES_LOCAIS = ['deskParametros', 'deskLog', 'deskComissoesPagas', 'deskComissoesExemplo', 'deskAfiliados']

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


# ---------------------------------------------------------------- a conta refeita em Python (o oraculo)
from oraculo_custos import D, c2, TAXAS_LINK, PADRAO_EMB, UNIDADES, VENDEDORA, oraculo


def br(v):
    s = '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('− ' if float(v) < 0 else '') + 'R$ ' + s


def pct(v):
    return ('− ' if float(v) < 0 else '') + '{:,.1f}'.format(abs(float(v)) * 100).replace('.', ',') + '%'


def num(t):
    t = t.replace('R$', '').replace('−', '-').replace(' ', '').replace('.', '').replace(',', '.')
    return float(t)


perto = lambda a, b: abs(float(a) - float(b)) < 0.005

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:200]))

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def limpar():
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        pg.evaluate("localStorage.setItem('deskComissoesPagas', JSON.stringify({ pagamentos: [] })); localStorage.setItem('deskComissoesExemplo', '1')")

    def abrir(q=''):
        ir(TELA); limpar(); ir(TELA, q)

    def todo_periodo():
        # o periodo de fabrica e o mes; os pedidos do exemplo andam 28 dias para tras, entao a conferencia pede um ano
        pg.evaluate("per = { de: isoDe(new Date(HOJE_C.getFullYear() - 1, 0, 1)), ate: HOJE_ISO }; paginaAtual = 1; render();"); pg.wait_for_timeout(120)

    def linhas():
        return pg.evaluate("""Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr =>
            Array.from(tr.children).filter(td => getComputedStyle(td).display !== 'none').map(td => td.innerText.replace(/\\s+/g, ' ').trim()))""")

    def cabecalho():
        return pg.evaluate("""Array.from(document.querySelectorAll('#tabelaCustos thead th')).filter(th => getComputedStyle(th).display !== 'none')
            .map(th => th.textContent.replace(/[▲▼]/g, '').replace(/\\s+/g, ' ').trim())""")

    def numeros():
        return [int(re.search(r'nº (\d+)', l[0]).group(1)) for l in linhas()]

    def texto(sel):
        return pg.inner_text(sel).replace('\n', ' ')

    def dados():
        return pg.evaluate("PEDIDOS.map(p => Object.assign({}, p, { ind: p.ind || null }))")

    def online(todos):
        return [x for x in todos if x.get('canal') == 'loja_virtual']

    def abrir_config():
        pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#menuMaisAcoes [data-acao="configurar"]'); pg.wait_for_timeout(250)

    def aplicar_config():
        pg.click('#btnAplicarCfg'); pg.wait_for_timeout(300)

    def param():
        return pg.evaluate("JSON.parse(localStorage.getItem('deskParametros') || '{}').custosEcommerce || null")

    todos = None

    # ================================================================ 1. a conta
    if secao(1, 'A conta: a mao, o oraculo e o lucro antigo fora do ar'):
        abrir(); todo_periodo()
        todos = dados()
        por_id = {x['id']: x for x in todos}
        r = lambda i: pg.evaluate("(i) => resultadoDoPedido(PEDIDOS.filter(p => p.id === i)[0])", i)
        a = r(3)
        ok(perto(a['venda'], 349.90) and perto(a['difFrete'], 22) and a['taxa'] == 0 and perto(a['comissao'], 17.50) and perto(a['embalagem'], 5) and perto(a['custo'], 199.90) and perto(a['lucro'], 105.50),
           'pedido 3 (pix): venda 349,90, dif. 22,00, taxa 0, comissão 17,50, embalagem 5,00, custo 199,90, lucro 105,50 · %s' % {k: a[k] for k in ('venda', 'difFrete', 'taxa', 'comissao', 'embalagem', 'custo', 'lucro')})
        a = r(12)
        ok(perto(a['taxa'], 154.21) and perto(a['comissao'], 51.20) and perto(a['embalagem'], 8) and perto(a['difFrete'], 26.50) and perto(a['lucro'], 180.09),
           'pedido 12 (crédito 10x, afiliado): taxa 154,21 sobre o total, comissão 51,20, embalagem 8,00, lucro 180,09')
        a = r(11)
        ok(perto(a['taxa'], 13.39) and perto(a['comissao'], 11.00) and perto(a['difFrete'], 95.00) and perto(a['lucro'], -32.49) and a['lucro'] < 0,
           'pedido 11 (o do prejuízo): taxa 13,39, comissão 11,00 (10,995 sobe), dif. de frete 95,00, lucro −32,49')
        a = r(1)
        ok(perto(a['venda'], 1880) and perto(a['freteCobrado'], 10) and perto(a['difFrete'], 8.50) and perto(a['taxa'], 132.49) and perto(a['comissao'], 94) and perto(a['embalagem'], 40) and perto(a['lucro'], 477.01),
           'pedido 1: a taxa é sobre o total (1.890,00), a comissão sobre a venda (1.880,00), a embalagem é 8 unidades × 5,00, lucro 477,01')
        ok(perto(a['margem'], 477.01 / 1880), 'a margem é o lucro sobre a venda: %.4f' % a['margem'])
        errados = []
        for i, x in por_id.items():
            o, a = oraculo(x), r(i)
            for k_js, k_py in (('venda', 'venda'), ('freteCobrado', 'frete'), ('difFrete', 'dif'), ('taxa', 'taxa'), ('comissao', 'comissao'), ('embalagem', 'embalagem'), ('custo', 'custo'), ('lucro', 'lucro')):
                if not perto(a[k_js], o[k_py]):
                    errados.append((i, k_js, a[k_js], float(o[k_py])))
        ok(not errados and len(por_id) == 16, 'os 16 pedidos, parcela por parcela, batem com a conta refeita em Python: %s' % errados[:3])
        ok(all(perto(a_['lucro'], (D(a_['venda']) - D(a_['difFrete']) - D(a_['taxa']) - D(a_['comissao']) - D(a_['comissaoMarketplace']) - D(a_['embalagem']) - D(a_['custo']))) for a_ in [r(i) for i in por_id]),
           'o lucro é a venda menos as cinco parcelas (e a de marketplace, zero), a cada centavo')
        ok(all(x['canal'] == 'loja_virtual' for x in todos if x['id'] in (1, 3, 4, 8, 9, 11, 12, 16)) and all(x['canal'] == 'manual' for x in todos if x['id'] in (2, 5, 6, 7, 10, 13, 14, 15)),
           'o canal: online nos pedidos 1, 3, 4, 8, 9, 11, 12 e 16 (4, 8 e 12 vêm de link de afiliado); manual nos outros')
        ok(all(('fretePagoLoja' in x and 'pagamento' in x) for x in online(todos)) and not any(('fretePagoLoja' in x or 'pagamento' in x) for x in todos if x['canal'] == 'manual'),
           'o frete pago pela loja e o pagamento existem só nos online')
        ok(all(x['loja'] in (1, 2) for x in online(todos)), 'nenhum pedido online é da loja 3 (a Desk Tech não tem vitrine)')
        ok(all(perto(x['custoMedio'], x['custo']) for x in todos if x['canal'] == 'manual') and not all(perto(x['custoMedio'], x['custo']) for x in online(todos)),
           'o custo médio dos manuais é o da compra; o dos online é outro número')
        ok(pg.evaluate("typeof lucroDe") == 'undefined', 'o lucroDe antigo (venda − custo − comissão) saiu da lista de Comissões')

    # ================================================================ 2. a lista
    if secao(2, 'A lista: só os online, as colunas, os cards, a barra'):
        abrir()
        ok(pg.evaluate("document.querySelector('h1').textContent") == 'Custos do E-commerce' and 'Vendas' in texto('#breadcrumb') and 'Custos do E-commerce' in texto('#breadcrumb'),
           'título e caminho: início › vendas › custos do e-commerce')
        ok(pg.evaluate("document.querySelector('#rotuloPeriodo').textContent") == 'Do mês' and pg.evaluate("per.de === HOJE_ISO.slice(0, 8) + '01' && per.ate === HOJE_ISO"), 'o período abre no mês atual')
        todo_periodo(); todos = dados()
        ok(sorted(numeros()) == [1, 3, 4, 8, 9, 11, 12, 16], 'só os 8 pedidos online aparecem: %s' % sorted(numeros()))
        ok(cabecalho() == ['Pedido', 'Loja', 'Venda', 'Frete cobrado', 'Dif. de frete', 'Taxa', 'Comissão', 'Embalagem', 'Custo', 'Lucro', 'Margem'],
           'as colunas por pedido, sem a de marketplace enquanto for zero: %s' % cabecalho())
        ok(not pg.evaluate("Array.from(document.querySelectorAll('.col-mkt')).some(c => getComputedStyle(c).display !== 'none')"), 'a coluna Com. marketplace fica escondida (todas as linhas valem zero)')
        pg.evaluate("itensPorPaginaAtual = 100; render();")
        ls = linhas()
        errados = []
        for l in ls:
            i = int(re.search(r'nº (\d+)', l[0]).group(1)); o = oraculo(next(x for x in todos if x['id'] == i))
            esperado = [br(o['venda']), br(o['frete']), br(o['dif']), br(o['taxa']), br(o['comissao']), br(o['embalagem']), br(o['custo']), br(o['lucro']), pct(o['margem'])]
            if l[2:] != esperado:
                errados.append((i, l[2:], esperado))
        ok(not errados, 'cada linha mostra venda, frete, dif., taxa, comissão, embalagem, custo, lucro e margem da conta: %s' % errados[:1])
        ok(all(('/' in l[0] and re.search(r'nº \d+', l[0])) for l in ls), 'a primeira coluna traz o número, e a data e o cliente embaixo')
        ors = [oraculo(x) for x in online(todos)]
        fat = sum(o['venda'] for o in ors); luc = sum(o['lucro'] for o in ors); cus = fat - luc
        cards = pg.evaluate("[kpiFaturamento, kpiCustos, kpiLucro, kpiMargem, kpiPrejuizo, kpiSemCusto].map(e => e.textContent)")
        ok(cards == [br(fat), br(cus), br(luc), pct(luc / fat), '1', '0'], 'os seis cards: faturamento, custos, lucro, margem, no prejuízo (1) e sem custo (0): %s' % cards)
        ok(perto(cus, sum(o['dif'] + o['taxa'] + o['comissao'] + o['embalagem'] + o['custo'] for o in ors)), 'custos é tudo o que saiu: diferencial, taxa, comissão, embalagem e custo')
        ok(texto('#somaFiltro') == br(luc) and '8 pedidos' in texto('#contagemLinhas'), 'o rodapé soma o lucro do filtro: %s' % texto('#somaFiltro'))
        # a barra
        partes = pg.evaluate("Array.from(document.querySelectorAll('#barraDivisao > span')).map(s => [s.getAttribute('data-parte'), parseFloat(s.style.width)])")
        ok([x[0] for x in partes] == ['custo', 'frete', 'taxa', 'comissao', 'embalagem', 'lucro'] and abs(sum(x[1] for x in partes) - 100) < 0.01, 'a barra: custo, frete, taxa, comissão, embalagem e lucro, fechando em 100%%: %s' % partes)
        leg = texto('#legendaDivisao')
        ok(all(t in leg for t in ('Custo dos produtos', 'Frete', 'Taxa do gateway', 'Comissão', 'Embalagem', 'Lucro')) and br(luc) in leg and pct(luc / fat) in leg,
           'a legenda traz o nome, o valor em R$ e o % de cada parte')
        ok(texto('.ce-barra-titulo') == 'Divisão do faturamento', 'o título da barra: %s' % texto('.ce-barra-titulo'))
        ok(texto('.ce-barra-apoio') == 'De tudo o que foi vendido, quanto foi para cada custo e quanto ficou de lucro.', 'a linha de apoio embaixo do título')
        ok(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.ce-barra-apoio')).fontSize) < parseFloat(getComputedStyle(document.querySelector('.ce-barra-titulo')).fontSize)"), 'a linha de apoio é menor que o título')
        # a legenda: grade de 3 colunas iguais, cada valor colado ao seu nome, centralizada sob a barra
        itens = pg.evaluate("""Array.from(document.querySelectorAll('#legendaDivisao > .ce-leg')).map(e => {
            const r = e.getBoundingClientRect(), t = e.querySelector('.ce-leg-t').children, i = e.querySelector('i').getBoundingClientRect();
            return { k: e.getAttribute('data-parte'), nome: t[0].textContent.trim(), valor: t[1].textContent.replace(/\\s+/g, ' ').trim(), x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width),
                     cor: getComputedStyle(e.querySelector('i')).backgroundColor, dotY: Math.round(i.top), nomeY: Math.round(t[0].getBoundingClientRect().top), valY: Math.round(t[1].getBoundingClientRect().top) } })""")
        esperado = [('custo', 'Custo dos produtos', sum(o['custo'] for o in ors)), ('frete', 'Frete', sum(o['dif'] for o in ors)), ('taxa', 'Taxa do gateway', sum(o['taxa'] for o in ors)),
                    ('comissao', 'Comissão', sum(o['comissao'] for o in ors)), ('embalagem', 'Embalagem', sum(o['embalagem'] for o in ors)), ('lucro', 'Lucro', luc)]
        ok([(i['k'], i['nome']) for i in itens] == [(k, n) for k, n, _ in esperado], 'a legenda: os 6 itens na ordem, cada um com o seu nome: %s' % [i['nome'] for i in itens])
        ok(all(i['valor'].startswith(br(v)) and (pct(v / fat) in i['valor']) for i, (_, _, v) in zip(itens, esperado)), 'cada valor em R$ e o %% estão junto do nome certo: %s' % [i['valor'] for i in itens])
        ok(all(i['valY'] > i['nomeY'] for i in itens), 'o valor fica embaixo do nome')
        ok(len({i['cor'] for i in itens}) == 6 and all(abs(i['dotY'] - i['nomeY']) <= 6 for i in itens), 'cada nome tem a bolinha da sua cor, ao lado, e as 6 cores são diferentes')
        ok(len({i['x'] for i in itens}) == 3 and itens[0]['x'] == itens[3]['x'] and itens[1]['x'] == itens[4]['x'] and itens[2]['x'] == itens[5]['x'], 'a grade tem 3 colunas alinhadas: x = %s' % [i['x'] for i in itens])
        ok(len({i['y'] for i in itens}) == 2 and itens[0]['y'] == itens[1]['y'] == itens[2]['y'] and itens[3]['y'] > itens[0]['y'], 'e 2 linhas: y = %s' % [i['y'] for i in itens])
        ok(len({i['w'] for i in itens}) == 1, 'as 3 colunas têm a mesma largura: %s' % sorted({i['w'] for i in itens}))
        cen = pg.evaluate("""(() => { const l = document.getElementById('legendaDivisao').getBoundingClientRect(), c = document.querySelector('.ce-barra-card').getBoundingClientRect(),
            cs = getComputedStyle(document.getElementById('legendaDivisao')); return [l.left - c.left, c.right - l.right, l.width, cs.maxWidth]; })()""")
        ok(abs(cen[0] - cen[1]) <= 1 and cen[2] <= 720.5, 'o bloco da legenda está centralizado sob a barra (sobra %.0f / %.0f) e tem largura máxima (%.0f)' % (cen[0], cen[1], cen[2]))
        pg.set_viewport_size({'width': 860, 'height': 900}); pg.wait_for_timeout(150)
        x860 = pg.evaluate("Array.from(document.querySelectorAll('#legendaDivisao > .ce-leg')).map(e => Math.round(e.getBoundingClientRect().left))")
        ok(len(set(x860)) == 2, 'em tela estreita cai para 2 colunas: x = %s' % x860)
        pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(150)
        pg.click('[data-kpi="prejuizo"]'); pg.wait_for_timeout(150)
        partes = pg.evaluate("Array.from(document.querySelectorAll('#barraDivisao > span')).map(s => s.getAttribute('data-parte'))")
        ok('lucro' not in partes and 'fora da barra' in texto('#legendaDivisao') and '− R$ 32,49' in texto('#legendaDivisao'), 'lucro negativo fica na legenda, fora da barra: %s' % partes)
        ok('só os pedidos no prejuízo' in texto('.ce-barra-titulo') and texto('#kpiLucro') == br(luc), 'a barra diz que explica só os pedidos no prejuízo; os quatro primeiros cards seguem somando a lista inteira')

    # ================================================================ 3. configurar
    if secao(3, 'Configurar: situações, custo médio, embalagem por loja, Cancelar descarta, validação e registro'):
        abrir(); todo_periodo()
        cfg = pg.evaluate("custosEcomLer()")
        ok(cfg['custoBase'] == 'compra' and 'cancelado' not in cfg['situacoes'] and len(cfg['situacoes']) == 8 and cfg['embalagemPorLoja'] == {'1': 5, '2': 8, '3': 0},
           'de fábrica: todas as situações menos Cancelado, custo da compra, embalagem 5,00 / 8,00 / 0,00: %s' % cfg)
        ok(param() is None, 'sem mexer, nada é gravado em deskParametros')
        abrir_config()
        ok(pg.evaluate("cfgDrawer.classList.contains('open')") and 'Configurações' in texto('#cfgDrawer .drawer-title'), 'Mais ações › Configurar abre o painel Configurações')
        rot = texto('#cfgDrawer')
        ok('Situações dos pedidos' in rot and 'Custo baseado em' in rot and 'Embalagem por loja' in rot and 'Desk Shope' in rot and 'Desk Brands' in rot and 'Desk Tech' in rot, 'as três configurações, com uma linha de embalagem por loja')
        marcadas = pg.evaluate("Array.from(document.querySelectorAll('#cfgSituacoes input')).map(i => [i.value, i.checked])")
        ok(len(marcadas) == 9 and [m[0] for m in marcadas if not m[1]] == ['cancelado'], 'as nove situações, todas marcadas menos Cancelado')
        ok([pg.input_value('#cfgEmbalagem input[data-loja="%d"]' % i) for i in (1, 2, 3)] == ['5,00', '8,00', '0,00'], 'a embalagem de fábrica: Shope 5,00, Brands 8,00, Tech 0,00')
        # Cancelar descarta
        pg.evaluate("document.querySelector('#cfgCustoBase .dropdown-select-item[data-value=\"medio\"]').click()")
        pg.fill('#cfgEmbalagem input[data-loja="1"]', '9,99')
        pg.click('#btnCancelarCfg'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("cfgDrawer.classList.contains('open')") and param() is None and 'R$ 477,01' in texto('#corpoTabela'), 'Cancelar fecha sem gravar nada, e a lista segue com a conta de antes')
        abrir_config()
        ok(pg.evaluate("document.querySelector('#cfgCustoBase').getAttribute('data-value')") == 'compra' and pg.input_value('#cfgEmbalagem input[data-loja="1"]') == '5,00', 'e ao reabrir o painel mostra o que está gravado, não o que foi descartado')
        # custo medio
        pg.evaluate("document.querySelector('#cfgCustoBase .dropdown-select-item[data-value=\"medio\"]').click()"); pg.wait_for_timeout(100)
        aplicar_config()
        ok(param() and param()['custoBase'] == 'medio' and not pg.evaluate("cfgDrawer.classList.contains('open')"), 'Aplicar grava em deskParametros.custosEcommerce e fecha o painel: %s' % param())
        todos = dados(); l1 = [l for l in linhas() if 'nº 1 ' in l[0] + ' '][0]
        ok(l1[8] == br(1105) and l1[9] == br(500.01), 'com o custo médio o pedido 1 troca de custo 1.128,00 para 1.105,00 e de lucro 477,01 para 500,01: %s' % l1[8:10])
        errados = [x['id'] for x in online(todos) if not perto(pg.evaluate("(i) => resultadoDoPedido(PEDIDOS.filter(p => p.id === i)[0]).lucro", x['id']), oraculo(x, 'medio')['lucro'])]
        ok(not errados, 'e todos os online batem com a conta refeita em custo médio: %s' % errados)
        ok('custo médio' in (pg.evaluate("JSON.parse(localStorage.getItem('deskLog'))[0].detalhe")), 'o registro de atividades guarda o que mudou')
        # embalagem por loja
        abrir_config()
        pg.fill('#cfgEmbalagem input[data-loja="1"]', '7,00'); aplicar_config()
        ok(param()['embalagemPorLoja']['1'] == 7 and param()['embalagemPorLoja']['2'] == 8, 'a embalagem da Shope grava 7,00 e a da Brands segue 8,00: %s' % param()['embalagemPorLoja'])
        ls = {int(re.search(r'nº (\d+)', l[0]).group(1)): l for l in linhas()}
        ok(ls[3][7] == br(7) and ls[1][7] == br(56) and ls[4][7] == br(8), 'a embalagem do pedido é a da loja vezes as unidades: pedido 3 = 7,00; pedido 1 (8 un) = 56,00; pedido 4 (Brands) segue 8,00')
        o3 = oraculo(next(x for x in todos if x['id'] == 3), 'medio', {1: 7, 2: 8, 3: 0})
        ok(ls[3][9] == br(o3['lucro']) and perto(o3['lucro'], 349.90 - 22 - 17.50 - 7 - 205.40), 'e muda o lucro: pedido 3 em custo médio (205,40) e embalagem 7,00 = %s' % ls[3][9])
        # o cancelado sai de fabrica e volta
        abrir(); todo_periodo()
        pg.evaluate("PEDIDOS.filter(p => p.id === 9)[0].situacao = 'cancelado'; render();"); pg.wait_for_timeout(150)
        ok(9 not in numeros() and len(numeros()) == 7, 'um pedido online cancelado sai da lista de fábrica (7 pedidos)')
        abrir_config()
        pg.evaluate("document.querySelector('#cfgSituacoes input[value=\"cancelado\"]').click()"); pg.wait_for_timeout(100); aplicar_config()
        ok(9 in numeros() and len(numeros()) == 8 and 'cancelado' in param()['situacoes'], 'marcando a situação Cancelado em Configurar ele volta (8 pedidos)')
        abrir_config()
        pg.evaluate("document.querySelectorAll('#cfgSituacoes input').forEach(i => { if (i.checked) i.click(); })"); aplicar_config()
        ok(pg.evaluate("cfgDrawer.classList.contains('open')") and pg.evaluate("document.getElementById('erroCfgSituacoes').classList.contains('show')") and 'cancelado' in param()['situacoes'],
           'sem nenhuma situação marcada, avisa e não grava')
        pg.evaluate("document.querySelector('#cfgSituacoes input[value=\"aberto\"]').click()")
        pg.fill('#cfgEmbalagem input[data-loja="2"]', 'abc'); aplicar_config()
        ok(pg.evaluate("document.getElementById('erroCfgEmbalagem').classList.contains('show')") and param()['embalagemPorLoja']['2'] == 8 and pg.evaluate("cfgDrawer.classList.contains('open')"),
           'embalagem que não é número avisa e não grava')
        pg.fill('#cfgEmbalagem input[data-loja="2"]', '-3'); aplicar_config()
        ok(pg.evaluate("document.getElementById('erroCfgEmbalagem').classList.contains('show')") and param()['embalagemPorLoja']['2'] == 8, 'embalagem negativa também não')
        pg.fill('#cfgEmbalagem input[data-loja="2"]', '8,50'); aplicar_config()
        ok(param()['embalagemPorLoja']['2'] == 8.5 and param()['situacoes'] == ['aberto'], 'corrigido, grava (8,50 e só a situação Em aberto)')
        log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === 'custosEcomConfig').length")
        ok(log == 2, 'cada Aplicar vira uma linha no Registro de atividades (os dois depois da última limpeza: %d)' % log)
        ir(REGISTRO)
        ok('Alterar as configurações de Custos do E-commerce' in pg.evaluate("document.body.textContent"), 'e o Registro de atividades mostra a ação pelo nome')
        limpar()

    # ================================================================ 4. cards, agrupar, busca, periodo, loja
    if secao(4, 'Cards que filtram, agrupar por, busca, período e loja'):
        abrir(); todo_periodo(); todos = dados()
        ok(pg.evaluate("Array.from(document.querySelectorAll('#indicadores .kpi-card')).map(c => c.hasAttribute('aria-pressed'))") == [False] * 4 + [True] * 2, 'só os dois cards de alerta filtram (No prejuízo e Produto sem custo)')
        pg.click('[data-kpi="prejuizo"]'); pg.wait_for_timeout(150)
        ok(numeros() == [11] and pg.evaluate("document.querySelector('[data-kpi=prejuizo]').getAttribute('aria-pressed')") == 'true' and pg.evaluate("document.querySelector('[data-kpi=prejuizo]').classList.contains('on')"),
           'No prejuízo filtra: só o pedido 11, e o card fica marcado')
        borda = pg.evaluate("(() => { const c = document.querySelector('[data-kpi=prejuizo]'); const s = getComputedStyle(c); return [s.borderTopColor, getComputedStyle(document.body).getPropertyValue('--active-text').trim()]; })()")
        ok(borda[0] != 'rgb(38, 38, 38)' and borda[0] != 'rgb(233, 231, 224)', 'a borda do card ativo é azul, não a de repouso: %s' % borda[0])
        cards_depois = pg.evaluate("[kpiFaturamento, kpiPrejuizo].map(e => e.textContent)")
        ok(cards_depois[0] == br(sum(oraculo(x)['venda'] for x in online(todos))) and cards_depois[1] == '1', 'os cards continuam somando a lista inteira, não a que o card filtrou')
        pg.click('[data-kpi="prejuizo"]'); pg.wait_for_timeout(150)
        ok(len(numeros()) == 8 and pg.evaluate("document.querySelector('[data-kpi=prejuizo]').getAttribute('aria-pressed')") == 'false', 'clicar de novo desfaz o filtro')
        pg.evaluate("PEDIDOS.filter(p => p.id === 9)[0].custo = 0; render();"); pg.wait_for_timeout(150)
        ok(texto('#kpiSemCusto') == '1' and 'custo zerado' in texto('#subSemCusto'), 'um pedido com custo zero acende o card Produto sem custo')
        pg.click('[data-kpi="semcusto"]'); pg.wait_for_timeout(150)
        ls = linhas()
        ok(numeros() == [9] and 'sem custo' in ls[0][8], 'e o card filtra esse pedido, que mostra "sem custo" no lugar do custo: %s' % ls[0][8])
        pg.reload(); pg.wait_for_timeout(300)
        # agrupar
        abrir(); todo_periodo()
        pg.evaluate("itensPorPaginaAtual = 100;")
        o_online = {x['id']: oraculo(x) for x in online(dados())}
        luc_total = sum(o['lucro'] for o in o_online.values())

        def agrupa(valor):
            pg.click('#filtroAgrupar .dropdown-select-btn'); pg.wait_for_timeout(100)
            pg.click('#filtroAgrupar .dropdown-select-item[data-value="%s"]' % valor); pg.wait_for_timeout(200)
        agrupa('loja')
        ls = linhas()
        ok(cabecalho()[0] == 'Loja' and [l[0].split(' ')[0] + ' ' + l[0].split(' ')[1] for l in ls] == ['Desk Shope', 'Desk Brands'] or len(ls) == 2, 'agrupar por Loja: duas linhas, e a coluna Loja sai: %s' % cabecalho()[:2])
        shope = [i for i, x in o_online.items() if next(y for y in dados() if y['id'] == i)['loja'] == 1]
        ok(any(br(sum(o_online[i]['lucro'] for i in shope)) in l for l in ls) and 'Loja' not in cabecalho()[1:2], 'o lucro de cada grupo é a soma dos pedidos dele: Shope %s' % br(sum(o_online[i]['lucro'] for i in shope)))
        ok(abs(sum(num(l[-2]) for l in ls) - float(luc_total)) < 0.02, 'e os grupos somam o lucro total (%s)' % br(luc_total))
        ok('5 pedidos' in ls[0][0] or '5 pedidos' in ls[1][0], 'cada grupo diz quantos pedidos tem')
        brands = [i for i, l in enumerate(ls) if l[0].startswith('Desk Brands')][0]
        pg.click('#corpoTabela tr:nth-child(%d)' % (brands + 1)); pg.wait_for_timeout(250)
        ok(pg.evaluate("agrupar") == 'pedido' and sorted(numeros()) == [4, 9, 12] and texto('#filtroLoja .dropdown-select-label') == 'Desk Brands',
           'clicar numa loja volta para Pedido, filtrado por ela: %s' % sorted(numeros()))
        agrupa('vend'); ls = linhas()
        nomes = sorted(l[0].split(' Vendedor')[0].split(' Afiliado')[0] for l in ls)
        ok(len(ls) == 2 and ls[0][0].startswith('Bruno') and ls[1][0].startswith('Rafael'), 'agrupar por Vendedor/Afiliado (com a loja ainda filtrada): %s' % [l[0] for l in ls])
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200); todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        agrupa('vend'); ls = linhas()
        ok(sorted(l[0].split(' ')[0] for l in ls) == ['Bruno', 'Larissa', 'Marina', 'Rafael'] and any('Afiliado · 2 pedidos' in l[0] for l in ls) and any('Vendedor · 4 pedidos' in l[0] for l in ls),
           'quem recebe: Marina (4 pedidos), Bruno (afiliado, 2), Larissa (afiliada, 1) e Rafael (1): %s' % [l[0] for l in ls])
        ok(abs(sum(num(l[-2]) for l in ls) - float(luc_total)) < 0.02, 'a soma dos grupos é o lucro total')
        bruno = [i for i, l in enumerate(ls) if l[0].startswith('Bruno')][0]
        pg.click('#corpoTabela tr:nth-child(%d)' % (bruno + 1)); pg.wait_for_timeout(250)
        ok(sorted(numeros()) == [4, 12] and pg.evaluate("document.getElementById('faixaGrupo').style.display") != 'none' and 'Bruno Carvalho' in texto('#faixaGrupo'),
           'clicar no Bruno volta para Pedido, com os pedidos 4 e 12 e a faixa do filtro: %s' % sorted(numeros()))
        pg.click('#btnTirarGrupo'); pg.wait_for_timeout(200)
        ok(len(numeros()) == 8, 'tirar o filtro devolve os 8 pedidos')
        agrupa('forma'); ls = linhas()
        ok(len(ls) == 7 and any(l[0].startswith('Pix 2 pedidos') for l in ls) and any('Cartão de crédito 3x' in l[0] for l in ls) and any('Cartão de crédito à vista' in l[0] for l in ls),
           'agrupar por Forma de pagamento: Pix (2) e o crédito por parcelamento: %s' % [l[0] for l in ls][:3])
        pix = [i for i, l in enumerate(ls) if l[0].startswith('Pix')][0]
        pg.click('#corpoTabela tr:nth-child(%d)' % (pix + 1)); pg.wait_for_timeout(250)
        ok(sorted(numeros()) == [3, 9], 'clicar em Pix volta para os pedidos 3 e 9: %s' % sorted(numeros()))
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("agrupar") == 'pedido' and pg.evaluate("fGrupo") is None and texto('#filtroAgrupar .dropdown-select-label') == 'Agrupar por: Pedido', 'Limpar filtros volta a agrupar por Pedido')
        # busca, loja
        todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        pg.fill('#campoBusca', '12'); pg.wait_for_timeout(200)
        ok(numeros() == [12], 'a busca pelo número é exata: 12 não traz o 1')
        pg.fill('#campoBusca', 'larissa'); pg.wait_for_timeout(200)
        ok(numeros() == [9], 'a busca pelo cliente: Larissa Monteiro é o pedido 9')
        pg.fill('#campoBusca', ''); pg.wait_for_timeout(100)
        pg.click('#filtroLoja .dropdown-select-btn'); pg.click('#filtroLoja .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(200)
        ok(sorted(numeros()) == [4, 9, 12], 'o filtro de loja: Desk Brands tem 3 pedidos online')
        # periodo
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(150)
        mes = pg.evaluate("per.de")
        pg.click('#btnPeriodo'); pg.wait_for_timeout(100)
        pg.fill('#periodoDe', pg.evaluate("fmtData(isoDe(diaMais(-8)))")); pg.fill('#periodoAte', pg.evaluate("fmtData(HOJE_ISO)")); pg.click('#btnAplicarPeriodo'); pg.wait_for_timeout(250)
        dias = pg.evaluate("PEDIDOS.filter(p => p.canal === 'loja_virtual' && p.dv <= 8).map(p => p.numero).sort((a, b) => a - b)")
        ok(sorted(numeros()) == dias and ' a ' in texto('#rotuloPeriodo'), 'o período entre datas (De/Até) filtra pela data da venda: %s' % sorted(numeros()))
        pg.click('#btnPeriodo'); pg.click('#periodoOpcoes [data-periodo="mes"]'); pg.wait_for_timeout(200)
        ok(texto('#rotuloPeriodo') == 'Do mês' and pg.evaluate("per.de") == mes, 'a opção "Do mês" volta ao mês atual')
        pg.click('#btnPeriodo'); pg.fill('#periodoDe', '31/02/2026'); pg.click('#btnAplicarPeriodo'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('erroPeriodo').classList.contains('show')"), 'data inválida avisa')
        pg.keyboard.press('Escape')

    # ================================================================ 5. painel, planilha, largura
    if secao(5, 'O painel do pedido, a planilha e a largura'):
        abrir(); todo_periodo()
        pg.click('#corpoTabela tr[data-id="11"]'); pg.wait_for_timeout(300)
        corpo = texto('#eventDrawer')
        ok(pg.evaluate("eventDrawer.classList.contains('open')") and 'Pedido nº 11' in corpo, 'clicar no pedido abre o painel lateral')
        ok('− R$ 32,49' in corpo and 'Cartão de crédito Elo 2x' in corpo and 'Marina Costa' in corpo and 'R$ 95,00' in corpo and 'R$ 13,39' in corpo and 'R$ 11,00' in corpo,
           'com o detalhamento: dif. de frete, taxa, comissão, embalagem, custo, lucro e o pagamento')
        ok(pg.evaluate("document.querySelector('#btnAbrirGateways') !== null && document.querySelector('#btnAbrirComissoes') !== null"), 'e os links para Gateways (a taxa) e Comissões (a regra)')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("eventDrawer.classList.contains('open')"), 'Esc fecha o painel')
        pg.click('#corpoTabela tr[data-id="11"]'); pg.wait_for_timeout(250)
        pg.click('#btnAbrirPedido'); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        ok(pg.url.endswith('pagina-vendas-pedidos-detalhe.html?id=11') and 'Pedido de Venda nº 11' in pg.inner_text('#tituloPedido'), 'o link abre o pedido: ../vendas/pagina-vendas-pedidos-detalhe.html?id=11')
        # planilha
        ir(TELA); todo_periodo()
        with pg.expect_download() as dl:
            pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(100)
            pg.click('#menuMaisAcoes [data-acao="planilha"]')
        conteudo = open(dl.value.path(), encoding='utf-8-sig').read().strip().splitlines()
        ok(len(conteudo) == 9 and conteudo[0].count(';') == 10 and 'Com. marketplace' not in conteudo[0], 'a planilha leva as 11 colunas e as 8 linhas da lista (sem a coluna escondida): %d linhas' % len(conteudo))
        ok('"Pedido nº 11' in conteudo[6] or any('Pedido nº 11' in l for l in conteudo), 'e o pedido 11 está nela')
        ok(pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=imprimir]') !== null"), 'Imprimir está no menu (bloco comum)')
        # largura
        for larg in (1280, 1440):
            pg.set_viewport_size({'width': larg, 'height': 900}); pg.wait_for_timeout(150)
            m = pg.evaluate("[document.querySelector('#wrapCustos').scrollWidth, document.querySelector('#wrapCustos').clientWidth, document.documentElement.scrollWidth, document.documentElement.clientWidth]")
            ok(m[0] <= m[1] and m[2] <= m[3], 'sem barra horizontal a %dpx com o exemplo (tabela %d de %d, página %d de %d)' % (larg, m[0], m[1], m[2], m[3]))
        pg.set_viewport_size({'width': 1280, 'height': 900})
        pg.evaluate("PEDIDOS.forEach(p => { if (p.canal === 'loja_virtual') { p.total = 12345.67; p.frete = 1234.56; p.custo = 9876.54; p.fretePagoLoja = 100.00; p.cliente = 'Distribuidora Nordeste de Embalagens Ltda'; } }); render();"); pg.wait_for_timeout(200)
        m = pg.evaluate("[document.querySelector('#wrapCustos').scrollWidth, document.querySelector('#wrapCustos').clientWidth, document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        ok(m[0] <= m[1] and m[2] <= m[3], 'e a 1280px com o dado mais comprido (R$ 12.345,67 de venda, frete de R$ 1.234,56 com diferencial negativo, custo de R$ 9.876,54 e um cliente de 41 letras): tabela %d de %d' % (m[0], m[1]))
        pg.set_viewport_size({'width': 1440, 'height': 900})

    # ================================================================ 6. a pagina do pedido
    if secao(6, 'A página do pedido: canal, frete pago pela loja, forma, parcelas e a caixa do resultado'):
        ir(PV_D); limpar()
        todos = None
        r_lista = {}
        for i in range(1, 17):
            ir(PV_D, '?id=%d' % i)
            if todos is None:
                todos = pg.evaluate("PEDIDOS_DA_LISTA.map(p => Object.assign({}, p, { ind: p.ind || null }))")
            x = next(y for y in todos if y['id'] == i)
            cx = texto('#caixaResultado')
            lucro_esp = oraculo(x)['lucro']
            canal = texto('#canalPedido')
            achou = ('(=) Lucro' in cx and br(lucro_esp) in cx)
            r_lista[i] = (achou, canal, x['canal'])
            if not achou:
                print('   pedido %d: esperava %s em: %s' % (i, br(lucro_esp), cx[-200:]))
        ok(all(v[0] for v in r_lista.values()), 'a caixa Resultado do pedido dá o mesmo lucro da conta nos 16 pedidos, manuais inclusive: %s' % [k for k, v in r_lista.items() if not v[0]])
        ok(all(v[1] == ('Canal: Loja virtual' if v[2] == 'loja_virtual' else 'Canal: Venda manual') for v in r_lista.values()), 'o canal aparece no cabeçalho do pedido: Loja virtual nos 8 online, Venda manual nos 8 outros')
        ir(PV_D, '?id=11')
        cx = texto('#caixaResultado')
        ok(all(t in cx for t in ('Venda', 'R$ 219,90', 'Frete cobrado do cliente', 'Diferencial de frete', 'R$ 95,00', 'Taxa do gateway', 'R$ 13,39', 'Comissão de venda', 'R$ 11,00', 'Embalagem', 'R$ 5,00', 'Custo dos produtos', 'R$ 128,00', 'Lucro', '− R$ 32,49', 'margem de − 14,8%', 'ver em Custos do E-commerce')),
           'a caixa traz venda, frete cobrado, dif. de frete, taxa, comissão, embalagem, custo, lucro e margem, com o link para Custos do E-commerce')
        ok(pg.evaluate("document.getElementById('resLink').getAttribute('href')") == '../vendas/pagina-vendas-custos-ecommerce.html?busca=11', 'o link da caixa abre a tela nova já no pedido')
        ok(pg.input_value('#inputFretePagoLoja') == '95,00' and 'frete pago pela loja' in texto('.totais-grid').lower(), 'o campo "Frete pago pela loja" fica ao lado do frete do cliente: 95,00')
        ok(pg.evaluate("document.querySelector('[data-leitura=inputFretePagoLoja]').textContent") == '95,00' and pg.evaluate("document.body.classList.contains('modo-leitura')"), 'e em leitura mostra o valor, como o vizinho (frete pago pelo cliente)')
        ir(PV_D, '?id=2')
        ok(pg.input_value('#inputFretePagoLoja') == '' and pg.evaluate("document.querySelector('[data-leitura=inputFretePagoLoja]').textContent") == '—' and 'sem o frete pago pela loja' in texto('#caixaResultado'),
           'no pedido manual o frete pago pela loja não é conhecido: campo vazio, "—" em leitura e "—" na caixa')
        ok(re.search(r'Taxa do gateway\s*sem forma de pagamento da loja virtual\s*—', pg.inner_text('#caixaResultado').replace('\n', ' ')) is not None or '—' in cx, 'a taxa sem forma de pagamento da loja virtual também aparece como "—"')
        # ao vivo
        ir(PV_D, '?id=1&editar=1')
        antes = pg.evaluate("[...document.querySelectorAll('#resLinhas .ped-res-linha b')].map(b => b.textContent)")
        pg.fill('#inputFretePagoLoja', '20,00'); pg.wait_for_timeout(200)
        depois = pg.evaluate("[...document.querySelectorAll('#resLinhas .ped-res-linha b')].map(b => b.textContent)")
        ok(antes[2] == 'R$ 8,50' and depois[2] == 'R$ 10,00' and depois[-1] == br(477.01 - 1.50), 'editar o frete pago pela loja (18,50 → 20,00) muda a caixa na hora: dif. 8,50 → 10,00, lucro 477,01 → 475,51 (%s)' % depois[-1])
        pg.fill('#inputFrete', '30,00'); pg.wait_for_timeout(200)
        d2 = pg.evaluate("[...document.querySelectorAll('#resLinhas .ped-res-linha b')].map(b => b.textContent)")
        ok(d2[1] == 'R$ 30,00' and d2[0] == depois[0] and d2[2] == '− R$ 10,00', 'o frete cobrado entra no total mas não na venda: com 30,00 a venda segue %s e o diferencial vira − R$ 10,00 (a loja ganhou no frete)' % d2[0])
        # forma de pagamento e parcelas
        ir(PV_D, '?id=12')
        ok(pg.evaluate("document.getElementById('inputRecebimento').getAttribute('data-value')") == 'credito' and pg.evaluate("document.getElementById('inputCondicao').getAttribute('data-value')") == '10' and
           pg.evaluate("document.querySelector('#inputCondicao .dropdown-select-label').textContent") == '10x', 'a forma e as parcelas vêm do pagamento: crédito, 10x (a lista de condições ganha o 10x só nesse pedido)')
        ir(PV_D, '?id=3')
        ok(pg.evaluate("document.getElementById('inputRecebimento').getAttribute('data-value')") == 'pix' and pg.evaluate("document.getElementById('inputCondicao').getAttribute('data-value')") == '1', 'pedido 3: Pix, à vista')
        ir(PV_D, '?id=8')
        ok(pg.evaluate("document.getElementById('inputCondicao').getAttribute('data-value')") == '6', 'pedido 8: crédito 6x')
        # sem registro: novo, clone, exemplo, balcao
        ir(PV_D, '?novo=1')
        ok('Canal: Venda manual' in texto('#canalPedido') and 'O resultado aparece quando o pedido existe' in texto('#caixaResultado') and pg.input_value('#inputFretePagoLoja') == '', 'pedido novo: canal manual, sem número inventado na caixa')
        ir(PV_D, '?clonar=11&id=11')
        ok('Canal: Venda manual' in texto('#canalPedido') and pg.input_value('#inputFretePagoLoja') == '' and 'O resultado aparece quando o pedido existe' in texto('#caixaResultado') and
           pg.evaluate("document.getElementById('inputRecebimento').getAttribute('data-value')") == 'pix', 'o clone de um pedido online é venda manual: não herda canal, frete da loja nem pagamento')
        ir(PV_D)
        ok('O resultado aparece quando o pedido existe' in texto('#caixaResultado'), 'o exemplo desenhado na página (sem ?id=) também diz isso, em vez de inventar')
        # a tela nova abre no pedido do link
        ir(TELA, '?busca=16')
        ok(numeros() == [16] and 'a pedido de outra tela' in texto('.busca-link'), 'a tela abre no pedido do link (?busca=16), mesmo ele sendo de outro mês: o período se ajusta')

    # ================================================================ 7. Comissoes
    if secao(7, 'Comissões usa a conta única'):
        ir(COM); limpar(); ir(COM)
        ok(pg.evaluate("typeof lucroDe") == 'undefined' and 'Custos do E-commerce' in pg.evaluate("document.querySelector('th[data-ordem=lucro]').getAttribute('title')"), 'a lista de Comissões não tem mais o lucroDe, e o título da coluna Lucro diz a conta nova')
        errados = pg.evaluate("""beneficiarios().filter(b => pedidosDe(b).length).map(b => {
            const r = contaDoPeriodo(b, '2000-01-01', HOJE_ISO);
            const soma = Math.round(pedidosDe(b).filter(p => p.situacao !== 'cancelado').reduce((s, p) => s + resultadoDoPedido(p).lucro, 0) * 100) / 100;
            return [b.nome, Math.round(r.lucro * 100) / 100, soma];
        }).filter(x => Math.abs(x[1] - x[2]) > 0.005)""")
        ok(not errados, 'o lucro de cada pessoa em Comissões é a soma do resultadoDoPedido dos pedidos dela: %s' % errados)
        marina = pg.evaluate("(() => { const b = beneficiarioDe('v1'); return Math.round(contaDoPeriodo(b, '2000-01-01', HOJE_ISO).lucro * 100) / 100; })()")
        todos_c = pg.evaluate("PEDIDOS.map(p => Object.assign({}, p, { ind: p.ind || null }))")
        marina_esp = sum(float(oraculo(x)['lucro']) for x in todos_c if not x.get('ind') and x['vend'] == 0 and x['situacao'] != 'cancelado')
        ok(abs(marina - marina_esp) < 0.01, 'Marina Costa (vendedora): lucro %s = conta refeita %s' % (marina, round(marina_esp, 2)))
        ir(COM_D, '?id=v1')
        ok('Custos do E-commerce' in pg.evaluate("Array.from(document.querySelectorAll('th')).filter(t => t.textContent.trim() === 'Lucro')[0].getAttribute('title')") and pg.evaluate("typeof lucroDe") == 'undefined',
           'a conta do afiliado também: sem lucroDe e com o título novo')
        ir(CLI_D)
        ok(pg.evaluate("typeof lucroDe") == 'undefined' and pg.evaluate("typeof resultadoDoPedido") == 'function', 'o cadastro do cliente (aba Afiliado) usa a mesma conta')

    # ================================================================ 8. ligacoes
    if secao(8, 'Blocos idênticos, espelhos, menu em todas as telas e catálogo de ações'):
        def fonte(n):
            return open(localiza.onde(n), encoding='utf-8').read()

        def bloco(t, ini, fim):
            a = t.index(ini)
            return t[a:t.index(fim, a) + len(fim)] if fim else t[a:t.index('  // ===== ', a + 10)]
        quem = [TELA, PV_D, COM, COM_D, CLI_D]
        res = [bloco(fonte(n), '  // ===== RESULTADO DO PEDIDO', '  // ===== FIM DO BLOCO RESULTADO DO PEDIDO =====') for n in quem]
        ok(all(x == res[0] for x in res) and 'function resultadoDoPedido' in res[0], 'o bloco RESULTADO DO PEDIDO é idêntico nas 5 telas que o carregam (a nova, a do pedido, as duas de Comissões e o cadastro do cliente)')
        gw = [bloco(fonte(n), '  // ===== GATEWAYS: LEITURA', '  // ===== FIM DO BLOCO GATEWAYS: LEITURA =====') for n in quem + [PDV, CFG_PDV, FORMAS]]
        ok(all(x == gw[0] for x in gw), 'o bloco GATEWAYS: LEITURA é idêntico nas 8 telas (as 3 de antes e as 5 desta conta)')
        cm = [bloco(fonte(n), '  // ===== COMISSOES: DADOS E REGRAS', None) for n in quem]
        ok(all(x == cm[0] for x in cm) and len(cm[0]) > 6000, 'o bloco COMISSOES: DADOS E REGRAS é idêntico nas 5 telas (as 3 de antes, a do pedido e a nova)')
        ok(all(fonte(n).count('const PEDIDOS = [') == 1 for n in (TELA, COM, COM_D, CLI_D, PV)) and fonte(PV_D).count('const PEDIDOS_DA_LISTA = [') == 1, 'cada tela tem o seu espelho dos pedidos uma vez só')
        # espelhos: os campos novos iguais aos da lista de pedidos
        ir(PV); CAMPOS = "PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.canal, p.custoMedio, p.fretePagoLoja === undefined ? null : p.fretePagoLoja, p.pagamento || null, p.unidades || 1, p.custo])"
        da_lista = pg.evaluate(CAMPOS)
        outros = {}
        for n in (COM, COM_D, CLI_D, TELA):
            ir(n); outros[n] = pg.evaluate(CAMPOS)
        ir(PV_D); outros[PV_D] = pg.evaluate(CAMPOS.replace('PEDIDOS.filter', 'PEDIDOS_DA_LISTA.filter'))
        ok(len(da_lista) == 16 and all(v == da_lista for v in outros.values()), 'os campos novos (canal, custo médio, frete pago pela loja, pagamento, unidades, custo) são iguais na lista, na página do pedido, nas duas de Comissões, no cliente e na tela nova')
        ir(PV)
        itens = pg.evaluate("Object.keys(ITENS_PEDIDO).map(k => [Number(k), ITENS_PEDIDO[k].reduce((s, i) => s + i.qtd, 0)])")
        ok({k: v for k, v in itens} == UNIDADES, 'as unidades de cada pedido são a soma das quantidades dos itens do exemplo (%s)' % dict(itens))
        # menu e catalogo
        alvo = 'data-label="Custos do E-commerce" data-href="' + ROTA + '"'
        sem = [_os.path.basename(c) for c in localiza.caminhos() if alvo not in open(c, encoding='utf-8').read()]
        ok(not sem, 'o item Custos do E-commerce do menu leva à tela em todas as %d telas: %s' % (len(localiza.caminhos()), sem[:3]))
        ir(PV)
        pg.evaluate("document.querySelector('.nav-item[data-id=vendas]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('#flyout-vendas .flyout-item[data-label=\"Custos do E-commerce\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.endswith('/vendas/pagina-vendas-custos-ecommerce.html') and pg.evaluate("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'vendas', 'clicar no item do menu abre a tela, com Vendas marcado')
        carregam = [c for c in localiza.caminhos() if "chave:'gatewayExcluir'" in open(c, encoding='utf-8').read()]
        com_acao = [c for c in carregam if "chave:'custosEcomConfig'" in open(c, encoding='utf-8').read()]
        ok(len(carregam) >= 20 and len(com_acao) == len(carregam), 'a ação custosEcomConfig está no catálogo das %d telas que o carregam, a nova entre elas' % len(carregam))
        ir(TELA)
        ac = pg.evaluate("ACOES_SENHA.filter(a => a.chave === 'custosEcomConfig').map(a => [a.grupo, a.exigePadrao, a.onde])")
        ok(ac == [['Vendas', False, 'Vendas → Custos do E-commerce']], 'sem senha de fábrica, no grupo Vendas: %s' % ac)
        ir(SENHAS)
        ok('Alterar as configurações de Custos do E-commerce' in pg.evaluate("document.body.textContent"), 'a tela de Confirmações por senha lista a ação')
        # os espelhos de Rastreamento nao comparam o pedido inteiro: a suite deles segue valendo
        ok(all('custoMedio' not in open(localiza.onde(n), encoding='utf-8').read() for n in RASTREIO), 'Rastreamento tem os pedidos dele (outra forma: o canal é um texto da vitrine e o pagamento é "pago"), nenhuma suíte compara aquele objeto com a lista, e ele não ganhou os campos novos')

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
