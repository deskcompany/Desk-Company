# -*- coding: utf-8 -*-
# Custos do E-commerce, entrega 1 (barganha de 21/out/2026) e entrega 2 (27/out/2026: itens, destino, devolucao, cortesia, produto/categoria/estado).
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
#   [8] As ligacoes: blocos identicos, espelhos, menu em todas as telas, catalogo de acoes;
#   [9] Itens e destino nos pedidos online: fecham no total, no custo e no custo medio; espelhos; a UF;
#   [10] A devolucao entra na conta: revendavel, avariado, frete da loja e do cliente, aberta/recusada/cancelada nao contam, a gravada vence;
#   [11] O vale de cortesia e desconto: a venda diminui, a coluna Cortesia, o espelho do exemplo;
#   [12] Produto, categoria e estado: agrupar, filtrar, a repartição por item que fecha no pedido, a barra que diz o escopo;
#   [13] O bloco das devoluções idêntico, os espelhos da Devolução e de Cadastros › Produtos.
#
# Contas a mao (loja 1 = Desk Shope, embalagem R$ 5,00 POR PEDIDO; loja 2 = Desk Brands, R$ 8,00; taxas do Link de pagamento
# da InfinitePay: 1x 4,20% · 2x 6,09% · 3x 7,01% · 10x 15,06% · 12x 16,66%, pix 0). Desde a entrega 2 (27/out/2026) a devolucao aceita entra na conta e o vale de cortesia sai da venda;
# desde 28/out a embalagem e a da loja UMA vez por pedido (nao mais por unidade) e a devolucao nao traz de volta a parte paga com o vale de cortesia:
#   pedido 3  (pix, vendedora Marina 5%, 1 kit; vale de cortesia de 15,00; DV-0010 finalizada: o kit inteiro voltou AVARIADO, frete da volta de 38,90 pago pela loja):
#             venda 349,90 − 15,00 de cortesia = 334,90 · dif. frete 22,00 − 0 = 22,00 · taxa 0 · comissao 5% de 349,90 = 17,50, mas voltou tudo dentro do prazo -> 0
#             · embalagem 5,00 · custo 199,90 · valor devolvido 349,90 x (349,90 − 15,00) / 349,90 = 334,90 (o vale de 15,00 nao volta em dinheiro)
#             · devolucao 334,90 − 0 (avariado nao devolve o custo) + 38,90 = 373,80
#             ->  lucro 334,90 − 22,00 − 0 − 5,00 − 199,90 − 373,80 = −265,80
#   pedido 12 (credito Visa 10x, afiliado Bruno 5%, Brands):  venda 1.024,00 · dif. 26,50 · taxa 15,06% de 1.024,00 = 154,2144 -> 154,21
#             · comissao 5% de 1.024,00 = 51,20 · embalagem 8,00 · custo 604,00  ->  lucro 1.024,00 − 26,50 − 154,21 − 51,20 − 8,00 − 604,00 = 180,09
#   pedido 11 (credito Elo 2x, Marina 5%, frete gratis para longe: a loja pagou 95,00):  venda 219,90 · dif. 95,00 · taxa 6,09% de 219,90 = 13,3919 -> 13,39
#             · comissao 5% de 219,90 = 10,995 -> 11,00 · embalagem 5,00 · custo 128,00  ->  lucro 219,90 − 95,00 − 13,39 − 11,00 − 5,00 − 128,00 = −32,49
#   pedido 1  (credito Visa 3x, o cliente pagou 10,00 de frete e a loja 18,50; DV-0011 em andamento: 1 fone e 2 carregadores revendaveis, 445,00, frete pago pelo cliente):
#             venda 1.890,00 − 10,00 = 1.880,00 · dif. 18,50 − 10,00 = 8,50 · taxa 7,01% de 1.890,00 (sobre o TOTAL, nao sobre a venda) = 132,489 -> 132,49
#             · comissao 5% de 1.880,00 = 94,00 x (1 − 445,00 / 1.880,00) = 71,75 · embalagem 5,00 · custo 1.128,00
#             · devolucao 445,00 − custo que voltou (150,00 + 2 x 58,50 = 267,00) + 0 = 178,00
#             ->  lucro 1.880,00 − 8,50 − 132,49 − 71,75 − 5,00 − 1.128,00 − 178,00 = 356,26;  com o custo medio (1.105,00; voltou 146,90 + 2 x 57,30 = 261,50; devolucao 183,50): 373,76
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys, datetime
import localiza
from decimal import Decimal, ROUND_HALF_UP
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
CHAVES_LOCAIS = ['deskParametros', 'deskLog', 'deskComissoesPagas', 'deskComissoesExemplo', 'deskAfiliados', 'deskDevolucoes', 'deskValesCompra', 'deskValesCompraExemplo']
DEVOL, DEVOL_D, PRODUTOS = 'pagina-logistica-devolucao.html', 'pagina-logistica-devolucao-detalhe.html', 'pagina-cadastros-produtos.html'
HOJE_PY = datetime.date.today()

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
from oraculo_custos import D, c2, TAXAS_LINK, PADRAO_EMB, VENDEDORA, oraculo, ITENS, ONLINE, DEVOLUCOES, CORTESIA_EXEMPLO, itens_do_pedido


def br(v):
    s = '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('− ' if float(v) < 0 else '') + 'R$ ' + s


def pct(v):
    # meio para cima, como a tela (a formatacao do Python arredonda 18,95 para 18,9 por causa do binario)
    x = abs(v if isinstance(v, Decimal) else D(round(float(v), 10))) * 100
    return ('− ' if float(v) < 0 else '') + '{:,.1f}'.format(x.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)).replace('.', ',') + '%'


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
        ok(perto(a['venda'], 334.90) and perto(a['cortesia'], 15) and perto(a['difFrete'], 22) and a['taxa'] == 0 and perto(a['comissao'], 0) and perto(a['embalagem'], 5) and perto(a['custo'], 199.90)
           and perto(a['devolvido'], 334.90) and perto(a['custoRecuperado'], 0) and perto(a['perdaAvaria'], 199.90) and perto(a['freteVolta'], 38.90) and perto(a['devolucao'], 373.80) and perto(a['lucro'], -265.80),
           'pedido 3 (pix, cortesia de 15,00, kit devolvido inteiro e avariado): venda 334,90, comissão 0, valor devolvido 334,90 (o vale de 15,00 não volta em dinheiro), devolução 373,80 (334,90 − 0 + 38,90), lucro −265,80 · %s' % {k: a[k] for k in ('venda', 'difFrete', 'taxa', 'comissao', 'embalagem', 'custo', 'devolucao', 'lucro')})
        a = r(12)
        ok(perto(a['taxa'], 154.21) and perto(a['comissao'], 51.20) and perto(a['embalagem'], 8) and perto(a['difFrete'], 26.50) and perto(a['devolucao'], 0) and perto(a['lucro'], 180.09),
           'pedido 12 (crédito 10x, afiliado, 10 unidades): taxa 154,21 sobre o total, comissão 51,20, embalagem 8,00 (uma por pedido, não 10 × 8,00), lucro 180,09')
        a = r(11)
        ok(perto(a['taxa'], 13.39) and perto(a['comissao'], 11.00) and perto(a['difFrete'], 95.00) and perto(a['embalagem'], 5) and perto(a['lucro'], -32.49) and a['lucro'] < 0,
           'pedido 11 (o do frete caro): taxa 13,39, comissão 11,00 (10,995 sobe), dif. de frete 95,00, embalagem 5,00 (5 unidades, uma só embalagem), lucro −32,49')
        a = r(1)
        ok(perto(a['venda'], 1880) and perto(a['freteCobrado'], 10) and perto(a['difFrete'], 8.50) and perto(a['taxa'], 132.49) and perto(a['comissao'], 71.75) and perto(a['embalagem'], 5)
           and perto(a['devolvido'], 445) and perto(a['custoRecuperado'], 267) and perto(a['perdaAvaria'], 0) and perto(a['freteVolta'], 0) and perto(a['devolucao'], 178) and perto(a['lucro'], 356.26),
           'pedido 1: a taxa é sobre o total (1.890,00); a comissão de 94,00 cai para 71,75 (445,00 devolvidos de 1.880,00); embalagem 5,00 (8 unidades, uma embalagem); devolução 445,00 − 267,00 de custo que voltou = 178,00; lucro 356,26')
        ok(perto(a['margem'], 356.26 / 1880), 'a margem é o lucro sobre a venda: %.4f' % a['margem'])
        # a embalagem e uma por pedido: nao muda com as unidades (o 16 tem 16 unidades, o 11 tem 5, o 3 tem 1)
        emb = {i: r(i)['embalagem'] for i in (1, 3, 4, 8, 9, 11, 12, 16)}
        ok(emb == {1: 5, 3: 5, 4: 8, 8: 5, 9: 8, 11: 5, 12: 8, 16: 5} and perto(sum(emb.values()), 49), 'a embalagem é a da loja uma vez por pedido (Shope 5,00, Brands 8,00), sem olhar as unidades: %s, total %s' % (emb, sum(emb.values())))
        ok(perto(r(16)['lucro'], 341.16) and perto(r(1)['lucro'], 356.26), 'pedido 16 (16 unidades): lucro 341,16; pedido 1 (8 unidades): lucro 356,26')
        errados = []
        for i, x in por_id.items():
            o, a = oraculo(x), r(i)
            for k_js, k_py in (('venda', 'venda'), ('freteCobrado', 'frete'), ('cortesia', 'cortesia'), ('difFrete', 'dif'), ('taxa', 'taxa'), ('comissao', 'comissao'), ('embalagem', 'embalagem'), ('custo', 'custo'),
                               ('devolucao', 'devolucao'), ('devolvido', 'devolvido'), ('custoRecuperado', 'recuperado'), ('perdaAvaria', 'perda'), ('freteVolta', 'frete_volta'), ('lucro', 'lucro')):
                if not perto(a[k_js], o[k_py]):
                    errados.append((i, k_js, a[k_js], float(o[k_py])))
        ok(not errados and len(por_id) == 16, 'os 16 pedidos, parcela por parcela, batem com a conta refeita em Python: %s' % errados[:3])
        ok(all(perto(a_['lucro'], (D(a_['venda']) - D(a_['difFrete']) - D(a_['taxa']) - D(a_['comissao']) - D(a_['comissaoMarketplace']) - D(a_['embalagem']) - D(a_['custo']) - D(a_['devolucao']))) for a_ in [r(i) for i in por_id]),
           'o lucro é a venda menos as parcelas (a de marketplace, zero) e a devolução, a cada centavo')
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
        ok(cabecalho() == ['Pedido', 'Loja', 'Venda', 'Frete cobrado', 'Cortesia', 'Dif. de frete', 'Taxa', 'Comissão', 'Embalagem', 'Custo', 'Devolução', 'Lucro', 'Margem'],
           'as colunas por pedido, sem a de marketplace enquanto for zero (Cortesia e Devolução aparecem porque há valor): %s' % cabecalho())
        ok(not pg.evaluate("Array.from(document.querySelectorAll('.col-mkt')).some(c => getComputedStyle(c).display !== 'none')"), 'a coluna Com. marketplace fica escondida (todas as linhas valem zero)')
        pg.evaluate("itensPorPaginaAtual = 100; render();")
        ls = linhas()
        errados = []
        for l in ls:
            i = int(re.search(r'nº (\d+)', l[0]).group(1)); o = oraculo(next(x for x in todos if x['id'] == i))
            esperado = [br(o['venda']), br(o['frete']), br(o['cortesia']), br(o['dif']), br(o['taxa']), br(o['comissao']), br(o['embalagem']), br(o['custo']), br(o['devolucao']), br(o['lucro']), pct(o['margem'])]
            if l[2:] != esperado:
                errados.append((i, l[2:], esperado))
        ok(not errados, 'cada linha mostra venda, frete, cortesia, dif., taxa, comissão, embalagem, custo, devolução, lucro e margem da conta: %s' % errados[:1])
        ok(all(('/' in l[0] and re.search(r'nº \d+', l[0])) for l in ls), 'a primeira coluna traz o número, e a data e o cliente embaixo')
        ors = [oraculo(x) for x in online(todos)]
        fat = sum(o['venda'] for o in ors); luc = sum(o['lucro'] for o in ors); cus = fat - luc; prej = sum(1 for o in ors if o['lucro'] < 0)
        cards = pg.evaluate("[kpiFaturamento, kpiCustos, kpiLucro, kpiMargem, kpiPrejuizo, kpiSemCusto].map(e => e.textContent)")
        ok(cards == [br(fat), br(cus), br(luc), pct(luc / fat), str(prej), '0'] and prej == 2, 'os seis cards: faturamento, custos, lucro, margem, no prejuízo (2: o 3 e o 11) e sem custo (0): %s' % cards)
        ok(perto(cus, sum(o['dif'] + o['taxa'] + o['comissao'] + o['embalagem'] + o['custo'] + o['devolucao'] for o in ors)), 'custos é tudo o que saiu: diferencial, taxa, comissão, embalagem, custo e devolução')
        ok(texto('#somaFiltro') == br(luc) and '8 pedidos' in texto('#contagemLinhas'), 'o rodapé soma o lucro do filtro: %s' % texto('#somaFiltro'))
        # a barra
        partes = pg.evaluate("Array.from(document.querySelectorAll('#barraDivisao > span')).map(s => [s.getAttribute('data-parte'), parseFloat(s.style.width)])")
        ok([x[0] for x in partes] == ['custo', 'frete', 'taxa', 'comissao', 'embalagem', 'devolucao', 'lucro'] and abs(sum(x[1] for x in partes) - 100) < 0.01, 'a barra: custo, frete, taxa, comissão, embalagem, devolução e lucro, fechando em 100%%: %s' % partes)
        leg = texto('#legendaDivisao')
        ok(all(t in leg for t in ('Custo dos produtos', 'Frete', 'Taxa do gateway', 'Comissão', 'Embalagem', 'Devolução', 'Lucro')) and br(luc) in leg and pct(luc / fat) in leg,
           'a legenda traz o nome, o valor em R$ e o % de cada parte')
        ok(texto('.ce-barra-titulo') == 'Divisão do faturamento', 'o título da barra: %s' % texto('.ce-barra-titulo'))
        ok(texto('.ce-barra-apoio') == 'De tudo o que foi vendido, quanto foi para cada custo e quanto ficou de lucro.', 'a linha de apoio embaixo do título')
        ok(pg.evaluate("parseFloat(getComputedStyle(document.querySelector('.ce-barra-apoio')).fontSize) < parseFloat(getComputedStyle(document.querySelector('.ce-barra-titulo')).fontSize)"), 'a linha de apoio é menor que o título')
        # a legenda: grade de 4 colunas iguais, cada valor colado ao seu nome, centralizada sob a barra
        itens = pg.evaluate("""Array.from(document.querySelectorAll('#legendaDivisao > .ce-leg')).map(e => {
            const r = e.getBoundingClientRect(), t = e.querySelector('.ce-leg-t').children, i = e.querySelector('i').getBoundingClientRect();
            return { k: e.getAttribute('data-parte'), nome: t[0].textContent.trim(), valor: t[1].textContent.replace(/\\s+/g, ' ').trim(), x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width),
                     cor: getComputedStyle(e.querySelector('i')).backgroundColor, dotY: Math.round(i.top), nomeY: Math.round(t[0].getBoundingClientRect().top), valY: Math.round(t[1].getBoundingClientRect().top) } })""")
        esperado = [('custo', 'Custo dos produtos', sum(o['custo'] for o in ors)), ('frete', 'Frete', sum(o['dif'] for o in ors)), ('taxa', 'Taxa do gateway', sum(o['taxa'] for o in ors)),
                    ('comissao', 'Comissão', sum(o['comissao'] for o in ors)), ('embalagem', 'Embalagem', sum(o['embalagem'] for o in ors)),
                    ('devolucao', 'Devolução', sum(o['devolucao'] for o in ors)), ('cortesia', 'Cortesia', sum(o['cortesia'] for o in ors)), ('lucro', 'Lucro', luc)]
        ok([(i['k'], i['nome']) for i in itens] == [(k, n) for k, n, _ in esperado], 'a legenda: os 8 itens na ordem (a Cortesia entra antes do Lucro, porque há valor), cada um com o seu nome: %s' % [i['nome'] for i in itens])
        ok(all(i['valor'].startswith(br(v)) and (pct(v / fat) in i['valor']) for i, (_, _, v) in zip(itens, esperado)), 'cada valor em R$ e o %% estão junto do nome certo: %s' % [i['valor'] for i in itens])
        ok(all(i['valY'] > i['nomeY'] for i in itens), 'o valor fica embaixo do nome')
        ok(len({i['cor'] for i in itens}) == 8 and all(abs(i['dotY'] - i['nomeY']) <= 6 for i in itens), 'cada nome tem a bolinha da sua cor, ao lado, e as 8 cores são diferentes')
        ok(len({i['x'] for i in itens}) == 4 and itens[0]['x'] == itens[4]['x'] and itens[1]['x'] == itens[5]['x'] and itens[2]['x'] == itens[6]['x'] and itens[3]['x'] == itens[7]['x'], 'a grade tem 4 colunas alinhadas: x = %s' % [i['x'] for i in itens])
        ok(len({i['y'] for i in itens}) == 2 and itens[0]['y'] == itens[1]['y'] == itens[2]['y'] == itens[3]['y'] and itens[4]['y'] == itens[5]['y'] == itens[6]['y'] == itens[7]['y'] and itens[4]['y'] > itens[0]['y'], 'e 2 linhas (4 em cima e 4 embaixo, com a Cortesia): y = %s' % [i['y'] for i in itens])
        ok(len({i['w'] for i in itens}) == 1, 'as 4 colunas têm a mesma largura: %s' % sorted({i['w'] for i in itens}))
        cen = pg.evaluate("""(() => { const l = document.getElementById('legendaDivisao').getBoundingClientRect(), c = document.querySelector('.ce-barra-card').getBoundingClientRect(),
            cs = getComputedStyle(document.getElementById('legendaDivisao')); return [l.left - c.left, c.right - l.right, l.width, cs.maxWidth]; })()""")
        ok(abs(cen[0] - cen[1]) <= 1 and cen[2] <= 920.5, 'o bloco da legenda está centralizado sob a barra (sobra %.0f / %.0f) e tem largura máxima (%.0f)' % (cen[0], cen[1], cen[2]))
        pg.set_viewport_size({'width': 860, 'height': 900}); pg.wait_for_timeout(150)
        x860 = pg.evaluate("Array.from(document.querySelectorAll('#legendaDivisao > .ce-leg')).map(e => Math.round(e.getBoundingClientRect().left))")
        ok(len(set(x860)) == 2, 'em tela estreita cai para 2 colunas: x = %s' % x860)
        pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(150)
        pg.click('[data-kpi="prejuizo"]'); pg.wait_for_timeout(150)
        partes = pg.evaluate("Array.from(document.querySelectorAll('#barraDivisao > span')).map(s => s.getAttribute('data-parte'))")
        ok('lucro' not in partes and 'fora da barra' in texto('#legendaDivisao') and '− R$ 298,29' in texto('#legendaDivisao'), 'lucro negativo (− 265,80 e − 32,49 dos dois pedidos no prejuízo) fica na legenda, fora da barra: %s' % partes)
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
        ok('R$ por pedido' in rot and 'por unidade' not in rot, 'o campo da embalagem em Configurar diz "por pedido", não "por unidade"')
        marcadas = pg.evaluate("Array.from(document.querySelectorAll('#cfgSituacoes input')).map(i => [i.value, i.checked])")
        ok(len(marcadas) == 9 and [m[0] for m in marcadas if not m[1]] == ['cancelado'], 'as nove situações, todas marcadas menos Cancelado')
        ok([pg.input_value('#cfgEmbalagem input[data-loja="%d"]' % i) for i in (1, 2, 3)] == ['5,00', '8,00', '0,00'], 'a embalagem de fábrica: Shope 5,00, Brands 8,00, Tech 0,00')
        # Cancelar descarta
        pg.evaluate("document.querySelector('#cfgCustoBase .dropdown-select-item[data-value=\"medio\"]').click()")
        pg.fill('#cfgEmbalagem input[data-loja="1"]', '9,99')
        pg.click('#btnCancelarCfg'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("cfgDrawer.classList.contains('open')") and param() is None and 'R$ 356,26' in texto('#corpoTabela'), 'Cancelar fecha sem gravar nada, e a lista segue com a conta de antes')
        abrir_config()
        ok(pg.evaluate("document.querySelector('#cfgCustoBase').getAttribute('data-value')") == 'compra' and pg.input_value('#cfgEmbalagem input[data-loja="1"]') == '5,00', 'e ao reabrir o painel mostra o que está gravado, não o que foi descartado')
        # custo medio
        pg.evaluate("document.querySelector('#cfgCustoBase .dropdown-select-item[data-value=\"medio\"]').click()"); pg.wait_for_timeout(100)
        aplicar_config()
        ok(param() and param()['custoBase'] == 'medio' and not pg.evaluate("cfgDrawer.classList.contains('open')"), 'Aplicar grava em deskParametros.custosEcommerce e fecha o painel: %s' % param())
        todos = dados(); l1 = [l for l in linhas() if 'nº 1 ' in l[0] + ' '][0]
        ok(l1[9] == br(1105) and l1[10] == br(183.50) and l1[11] == br(373.76), 'com o custo médio o pedido 1 troca de custo 1.128,00 para 1.105,00, de devolução 178,00 para 183,50 (voltou 261,50) e de lucro 356,26 para 373,76: %s' % l1[9:12])
        errados = [x['id'] for x in online(todos) if not perto(pg.evaluate("(i) => resultadoDoPedido(PEDIDOS.filter(p => p.id === i)[0]).lucro", x['id']), oraculo(x, 'medio')['lucro'])]
        ok(not errados, 'e todos os online batem com a conta refeita em custo médio: %s' % errados)
        ok('custo médio' in (pg.evaluate("JSON.parse(localStorage.getItem('deskLog'))[0].detalhe")), 'o registro de atividades guarda o que mudou')
        # embalagem por loja
        abrir_config()
        pg.fill('#cfgEmbalagem input[data-loja="1"]', '7,00'); aplicar_config()
        ok(param()['embalagemPorLoja']['1'] == 7 and param()['embalagemPorLoja']['2'] == 8, 'a embalagem da Shope grava 7,00 e a da Brands segue 8,00: %s' % param()['embalagemPorLoja'])
        ls = {int(re.search(r'nº (\d+)', l[0]).group(1)): l for l in linhas()}
        ok(ls[3][8] == br(7) and ls[1][8] == br(7) and ls[16][8] == br(7) and ls[4][8] == br(8), 'a embalagem do pedido é a da loja, uma por pedido: pedidos 3 (1 un), 1 (8 un) e 16 (16 un) = 7,00; pedido 4 (Brands) segue 8,00')
        o3 = oraculo(next(x for x in todos if x['id'] == 3), 'medio', {1: 7, 2: 8, 3: 0})
        ok(ls[3][11] == br(o3['lucro']) and perto(o3['lucro'], 334.90 - 22 - 0 - 7 - 205.40 - 373.80), 'e muda o lucro: pedido 3 em custo médio (205,40) e embalagem 7,00 = %s' % ls[3][11])
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
        ok(sorted(numeros()) == [3, 11] and pg.evaluate("document.querySelector('[data-kpi=prejuizo]').getAttribute('aria-pressed')") == 'true' and pg.evaluate("document.querySelector('[data-kpi=prejuizo]').classList.contains('on')"),
           'No prejuízo filtra: o pedido 3 (devolvido inteiro) e o 11 (frete caro), e o card fica marcado')
        borda = pg.evaluate("(() => { const c = document.querySelector('[data-kpi=prejuizo]'); const s = getComputedStyle(c); return [s.borderTopColor, getComputedStyle(document.body).getPropertyValue('--active-text').trim()]; })()")
        ok(borda[0] != 'rgb(38, 38, 38)' and borda[0] != 'rgb(233, 231, 224)', 'a borda do card ativo é azul, não a de repouso: %s' % borda[0])
        cards_depois = pg.evaluate("[kpiFaturamento, kpiPrejuizo].map(e => e.textContent)")
        ok(cards_depois[0] == br(sum(oraculo(x)['venda'] for x in online(todos))) and cards_depois[1] == '2', 'os cards continuam somando a lista inteira, não a que o card filtrou')
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
        ok(pg.locator('.estoque-toolbar .search-wrap').count() == 1 and pg.locator('#campoProduto').count() == 0 and pg.get_attribute('#campoBusca', 'placeholder') == 'Pesquise por nº do pedido ou SKU',
           'há uma caixa de pesquisa só, com o texto "Pesquise por nº do pedido ou SKU"')
        pg.fill('#campoBusca', 'luminária'); pg.wait_for_timeout(200)
        ok(sorted(numeros()) == sorted(pid for pid in ONLINE if any(i[0] == 'MOB-4002' for i in ITENS[pid])), 'a mesma caixa acha pelo nome do produto: "luminária" traz os pedidos 9 e 16: %s' % sorted(numeros()))
        pg.fill('#campoBusca', 'mob-4001'); pg.wait_for_timeout(200)
        ok(sorted(numeros()) == sorted(pid for pid in ONLINE if any(i[0] == 'MOB-4001' for i in ITENS[pid])), 'e pelo SKU: "mob-4001" traz os pedidos 3, 8 e 16: %s' % sorted(numeros()))
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
        ok('− R$ 32,49' in corpo and 'Cartão de crédito Elo 2x' in corpo and 'Marina Costa' in corpo and 'R$ 95,00' in corpo and 'R$ 13,39' in corpo and 'R$ 11,00' in corpo and 'Amazonas (AM)' in corpo
           and 'camiseta básica algodão' in corpo.lower() and 'carregador usb-c 20w' in corpo.lower(),
           'com o detalhamento: estado de destino, itens, dif. de frete, taxa, comissão, embalagem, custo, lucro e o pagamento')
        ok(pg.evaluate("document.querySelector('#btnAbrirGateways') !== null && document.querySelector('#btnAbrirComissoes') !== null"), 'e os links para Gateways (a taxa) e Comissões (a regra)')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("eventDrawer.classList.contains('open')"), 'Esc fecha o painel')
        pg.click('#corpoTabela tr[data-id="11"]'); pg.wait_for_timeout(250)
        pg.click('#btnAbrirPedido'); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        ok(pg.url.endswith('pagina-vendas-pedidos-detalhe.html?id=11') and 'Pedido de Venda nº 11' in pg.inner_text('#tituloPedido'), 'o link abre o pedido: ../vendas/pagina-vendas-pedidos-detalhe.html?id=11')
        ir(TELA, '?busca=11'); todo_periodo()
        ok(numeros() == [11], 'o link ?busca=11 de outra tela segue abrindo a lista já no pedido, pela caixa única: %s' % numeros())
        abrir(); todo_periodo()
        pg.click('#corpoTabela tr[data-id="1"]'); pg.wait_for_timeout(300)
        corpo = texto('#eventDrawer')
        ok('DV-0011: 1 Fone de Ouvido Bluetooth X200 e 2 Carregador Turbo 33W' in corpo and 'uma por pedido, pela embalagem da loja' in corpo and 'unidades, pela' not in corpo and '8 × R$ 5,00' not in corpo,
           'o painel do pedido 1 tem a linha "DV-0011: 1 Fone de Ouvido Bluetooth X200 e 2 Carregador Turbo 33W" e a embalagem diz "uma por pedido"')
        cl = corpo.lower(); ok(cl.index('valor devolvido') < cl.index('dv-0011:') < cl.index('custo recuperado'), 'e a linha fica logo abaixo do Valor devolvido')
        href = pg.get_attribute('#eventDrawer a:has-text("DV-0011")', 'href')
        ok(href == '../logistica/pagina-logistica-devolucao-detalhe.html?id=2', 'DV-0011 é link para o detalhe da devolução, como a lista da Devolução abre (?id=): %s' % href)
        pg.click('#eventDrawer a:has-text("DV-0011")'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(pg.url.endswith('pagina-logistica-devolucao-detalhe.html?id=2') and 'DV-0011' in pg.inner_text('body'), 'e o clique abre o detalhe da DV-0011')
        abrir(); todo_periodo()
        pg.click('#corpoTabela tr[data-id="3"]'); pg.wait_for_timeout(300)
        corpo = texto('#eventDrawer')
        ok('DV-0010: 1 Kit Escritório Completo' in corpo and 'DV-0007' not in corpo and 'já sem a parte paga com vale de cortesia' in corpo, 'o painel do pedido 3: só a DV-0010 (a DV-0007, cancelada, não entra) e a nota da cortesia no Valor devolvido')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        pg.click('#corpoTabela tr[data-id="9"]'); pg.wait_for_timeout(300)
        ok('DV-' not in texto('#eventDrawer') and 'já sem a parte paga' not in texto('#eventDrawer'), 'pedido sem devolução não tem linha de DV nem a nota da cortesia')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # planilha
        ir(TELA); todo_periodo()
        with pg.expect_download() as dl:
            pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(100)
            pg.click('#menuMaisAcoes [data-acao="planilha"]')
        conteudo = open(dl.value.path(), encoding='utf-8-sig').read().strip().splitlines()
        ok(len(conteudo) == 9 and conteudo[0].count(';') == 12 and 'marketplace' not in conteudo[0].lower() and 'devolução' in conteudo[0].lower() and 'cortesia' in conteudo[0].lower(),
           'a planilha leva as 13 colunas e as 8 linhas da lista (sem a coluna escondida): %d linhas' % len(conteudo))
        ok('"Pedido nº 11' in conteudo[6] or any('Pedido nº 11' in l for l in conteudo), 'e o pedido 11 está nela')
        ok(pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=imprimir]') !== null"), 'Imprimir está no menu (bloco comum)')
        # largura
        for larg in (1280, 1440):
            pg.set_viewport_size({'width': larg, 'height': 900}); pg.wait_for_timeout(150)
            m = pg.evaluate("[document.querySelector('#wrapCustos').scrollWidth, document.querySelector('#wrapCustos').clientWidth, document.documentElement.scrollWidth, document.documentElement.clientWidth]")
            ok(m[0] <= m[1] and m[2] <= m[3], 'sem barra horizontal a %dpx com o exemplo (tabela %d de %d, página %d de %d)' % (larg, m[0], m[1], m[2], m[3]))
        pg.set_viewport_size({'width': 1280, 'height': 900})
        # com Cortesia e Devolução escondidas (zero em tudo): são as 11 colunas de antes, com o dado mais comprido
        pg.evaluate("resCortesia = () => 0; devolucoesLidas = () => []; PEDIDOS.forEach(p => { if (p.canal === 'loja_virtual') { p.total = 12345.67; p.frete = 1234.56; p.custo = 9876.54; p.fretePagoLoja = 100.00; p.cliente = 'Distribuidora Nordeste de Embalagens Ltda'; } }); render();"); pg.wait_for_timeout(200)
        m = pg.evaluate("[document.querySelector('#wrapCustos').scrollWidth, document.querySelector('#wrapCustos').clientWidth, document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        ok(m[0] <= m[1] and m[2] <= m[3] and not pg.evaluate("Array.from(document.querySelectorAll('.col-cort, .col-dev')).some(c => getComputedStyle(c).display !== 'none')"),
           'e a 1280px com o dado mais comprido e as colunas Cortesia e Devolução escondidas (R$ 12.345,67 de venda, frete de R$ 1.234,56 com diferencial negativo, custo de R$ 9.876,54 e um cliente de 41 letras): tabela %d de %d' % (m[0], m[1]))
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
        ok(all(v[1].startswith('Canal: Loja virtual · Entrega em ') if v[2] == 'loja_virtual' else v[1] == 'Canal: Venda manual' for v in r_lista.values()),
           'o canal aparece no cabeçalho do pedido, com o estado de destino: Loja virtual · Entrega em UF nos 8 online, Venda manual nos 8 outros')
        ir(PV_D, '?id=11')
        cx = texto('#caixaResultado')
        ok(all(t in cx for t in ('Venda', 'R$ 219,90', 'Frete cobrado do cliente', 'Diferencial de frete', 'R$ 95,00', 'Taxa do gateway', 'R$ 13,39', 'Comissão de venda', 'R$ 11,00', 'Embalagem', 'uma por pedido, pela embalagem da loja', 'R$ 5,00', 'Custo dos produtos', 'R$ 128,00', 'Lucro', '− R$ 32,49', 'margem de − 14,8%', 'ver em Custos do E-commerce')),
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
        ok(antes[2] == 'R$ 8,50' and depois[2] == 'R$ 10,00' and depois[-1] == br(356.26 - 1.50), 'editar o frete pago pela loja (18,50 → 20,00) muda a caixa na hora: dif. 8,50 → 10,00, lucro 356,26 → 354,76 (%s)' % depois[-1])
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
        ir(PV); CAMPOS = "PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.canal, p.custoMedio, p.fretePagoLoja === undefined ? null : p.fretePagoLoja, p.pagamento || null, p.custo])"
        da_lista = pg.evaluate(CAMPOS)
        outros = {}
        for n in (COM, COM_D, CLI_D, TELA):
            ir(n); outros[n] = pg.evaluate(CAMPOS)
        ir(PV_D); outros[PV_D] = pg.evaluate(CAMPOS.replace('PEDIDOS.filter', 'PEDIDOS_DA_LISTA.filter'))
        ok(len(da_lista) == 16 and all(v == da_lista for v in outros.values()), 'os campos novos (canal, custo médio, frete pago pela loja, pagamento, custo) são iguais na lista, na página do pedido, nas duas de Comissões, no cliente e na tela nova')
        ir(PV)
        ok(pg.evaluate("PEDIDOS.some(p => 'unidades' in p)") is False, 'o campo unidades saiu dos pedidos (só servia à embalagem, que agora é por pedido)')
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

    # ================================================================ 9. itens e destino
    if secao(9, 'Itens e destino nos pedidos online'):
        ir(PV); limpar(); ir(PV)
        itens_pv = pg.evaluate('ITENS_PEDIDO'); peds = pg.evaluate("PEDIDOS.filter(p => !p.pdv).map(p => Object.assign({}, p, { ind: p.ind || null }))")
        por = {p['id']: p for p in peds}
        fecha = []
        for pid in ONLINE:
            its, p = itens_pv[str(pid)], por[pid]
            if abs(sum(i['qtd'] * i['preco'] for i in its) + p.get('frete', 0) - p.get('desconto', 0) - p['total']) > 0.005: fecha.append((pid, 'total'))
            if abs(sum(i['qtd'] * i['custo'] for i in its) - p['custo']) > 0.005: fecha.append((pid, 'custo'))
            if abs(sum(i['qtd'] * i['custoMedio'] for i in its) - p['custoMedio']) > 0.005: fecha.append((pid, 'custo médio'))
        ok(not fecha, 'nos 8 pedidos online, itens mais frete menos desconto fecham no total, a soma do custo dos itens no custo e a do custo médio no custo médio: %s' % fecha)
        ok(sum(1 for pid in ONLINE if len(itens_pv[str(pid)]) > 1) >= 3 and len({i['categoria'] for pid in ONLINE for i in itens_pv[str(pid)]}) >= 2,
           'pelo menos 3 pedidos têm mais de um produto, e o conjunto tem mais de uma categoria: %s' % sorted({i['categoria'] for pid in ONLINE for i in itens_pv[str(pid)]}))
        un = {pid: sum(i['qtd'] for i in itens_pv[str(pid)]) for pid in ONLINE}
        ok(max(un.values()) <= 16, 'os pedidos online têm poucas unidades, sem dezenas: %s' % un)
        ok(not any('unidades' in p for p in peds), 'nenhum pedido (online ou manual) guarda mais o campo unidades')
        ufs = {i: por[i].get('ufEntrega') for i in ONLINE}
        ok(all(ufs.values()) and len(set(ufs.values())) >= 4 and ufs[11] in ('AM', 'RS') and not any('ufEntrega' in p for p in peds if p['id'] not in ONLINE),
           'os 8 online têm estado de destino (pelo menos 4 diferentes; o 11, do frete caro, vai para longe): %s' % ufs)
        campos = "PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.ufEntrega || null])"
        da_lista = pg.evaluate(campos); outros = {}
        for n in (COM, COM_D, CLI_D, TELA):
            ir(n); outros[n] = pg.evaluate(campos)
        ir(PV_D); outros[PV_D] = pg.evaluate(campos.replace('PEDIDOS.filter', 'PEDIDOS_DA_LISTA.filter'))
        ok(all(v == da_lista for v in outros.values()), 'o estado de destino é igual na lista, na página do pedido, nas duas de Comissões, no cliente e na tela nova')
        chaves = [str(i) for i in ONLINE]
        ok(pg.evaluate("ITENS_DA_LISTA") == itens_pv, 'ITENS_DA_LISTA (página do pedido) repete os itens da lista, os 11 pedidos que têm itens')
        for n in (COM, COM_D, CLI_D, TELA, PV_D):
            ir(n)
            ok(pg.evaluate("ITENS_ONLINE") == {k: itens_pv[k] for k in chaves}, 'ITENS_ONLINE de %s repete os itens dos 8 pedidos online da lista (espelho declarado)' % n)
        ir(PV_D, '?id=11')
        ok(texto('#canalPedido') == 'Canal: Loja virtual · Entrega em AM', 'a página do pedido mostra o estado junto do canal: %s' % texto('#canalPedido'))
        ir(PV_D, '?id=3&editar=1')
        ok(not pg.evaluate("document.getElementById('erroSaldo').classList.contains('show')") and pg.evaluate("document.querySelectorAll('#corpoItens tr.linha-sem-saldo').length") == 0,
           'o produto de Cadastros › Produtos, que o catálogo da página não tem, não acusa falta de saldo (o pedido já foi feito na vitrine)')
        ir(PV_D, '?id=2')
        ok(texto('#canalPedido') == 'Canal: Venda manual', 'o pedido manual segue sem estado de destino')

    # ================================================================ 10. devolucao
    def dev_py(id_, venda, situacao, itens, reversa=None, aberta=None, numero=None):
        return {'id': id_, 'numero': numero or 'DV-%04d' % (100 + id_), 'vendaId': venda, 'abertaEm': aberta or HOJE_PY.isoformat(), 'situacao': situacao, 'itens': itens, 'reversa': reversa}

    def grava(devs):
        js = {str(d['id']): {'id': d['id'], 'numero': d['numero'], 'vendaId': d['vendaId'], 'abertaEm': d['abertaEm'], 'situacao': d['situacao'], 'eventos': [],
                             'itens': [{'sku': i[0], 'qtd': i[1], 'unit': i[2], 'estado': i[3]} for i in d['itens']], 'reversa': d['reversa']} for d in devs}
        pg.evaluate("(g) => localStorage.setItem('deskDevolucoes', JSON.stringify({ devolucoes: g }))", js)

    def conta(pid, **kw):
        return pg.evaluate("(i) => resultadoDoPedido(PEDIDOS.filter(p => p.id === i)[0])", pid)

    if secao(10, 'A devolução entra na conta: revendável, avariado, frete da loja e do cliente, aberta e cancelada não contam, a gravada vence'):
        abrir(); todo_periodo(); todos = dados(); por = {x['id']: x for x in todos}
        entrega8 = {8: (HOJE_PY + datetime.timedelta(days=por[8]['dp'])).isoformat()}

        def confere(pid, devs, nome, base='compra', **kw):
            grava(devs); pg.evaluate("render()")
            a, o = conta(pid), oraculo(por[pid], base, devolucoes=devs, **kw)
            bate = all(perto(a[k_js], o[k_py]) for k_js, k_py in (('devolucao', 'devolucao'), ('devolvido', 'devolvido'), ('custoRecuperado', 'recuperado'), ('perdaAvaria', 'perda'),
                                                                   ('freteVolta', 'frete_volta'), ('comissao', 'comissao'), ('lucro', 'lucro')))
            ok(bate, '%s: devolução %s, voltou %s, perda %s, frete %s, lucro %s (conta refeita: %s, %s, %s, %s, %s)' % (nome, a['devolucao'], a['custoRecuperado'], a['perdaAvaria'], a['freteVolta'], a['lucro'],
               o['devolucao'], o['recuperado'], o['perda'], o['frete_volta'], o['lucro']))
            return a, o
        # pedido 8: 4 cadernos (11,30 de custo), 1 kit (213,30), 2 mouses, 3 kits de papelaria
        a, o = confere(8, [dev_py(10, 8, 'andamento', [('PAP-3001', 2, 18.50, 'revendavel')], {'paga': 'cliente', 'valor': 20})], 'item revendável (2 cadernos), frete pago pelo cliente', entrega=entrega8)
        ok(perto(a['devolvido'], 37) and perto(a['custoRecuperado'], 22.60) and perto(a['perdaAvaria'], 0) and perto(a['freteVolta'], 0) and perto(a['devolucao'], 14.40),
           'o revendável devolve o custo dele: 37,00 devolvidos − 2 × 11,30 = 14,40 de devolução, e o frete do cliente não custa nada à loja')
        a, o = confere(8, [dev_py(10, 8, 'finalizada', [('MOB-4001', 1, 349.90, 'avaria')], {'paga': 'nos', 'valor': 30})], 'item avariado, frete pago pela loja', entrega=entrega8)
        ok(perto(a['custoRecuperado'], 0) and perto(a['perdaAvaria'], 213.30) and perto(a['freteVolta'], 30) and perto(a['devolucao'], 379.90),
           'o avariado não devolve o custo (fica como perda de 213,30): devolução = 349,90 − 0 + 30,00 de frete da loja = 379,90')
        confere(8, [dev_py(10, 8, 'andamento', [('MOB-4001', 1, 349.90, 'nenhum')], {'paga': 'nos', 'valor': 0})], 'item perdido, coleta da nossa frota (frete 0)', entrega=entrega8)
        confere(8, [dev_py(10, 8, 'andamento', [('PAP-3002', 1, 64.90, 'revendavel'), ('ELE-1003', 1, 59.90, 'avaria')], {'paga': 'nos', 'valor': 18.40})], 'dois itens, um revendável e um avariado', entrega=entrega8)
        grava([dev_py(10, 8, 'aberta', [('PAP-3001', 2, 18.50, 'revendavel')])]); pg.evaluate("render()"); a = conta(8)
        ok(perto(a['devolucao'], 0) and a['devolucaoEmAnalise'] == 1 and perto(a['valorEmAnalise'], 37), 'a devolução aberta não conta (devolução 0), só aparece como aviso: 1 em análise, 37,00')
        for sit in ('cancelada', 'recusada'):
            grava([dev_py(10, 8, sit, [('PAP-3001', 2, 18.50, 'revendavel')])]); pg.evaluate("render()"); a = conta(8)
            ok(perto(a['devolucao'], 0) and a['devolucoesAceitas'] == 0 and a['devolucaoEmAnalise'] == 0, 'a devolução %s não conta' % sit)
        grava([dev_py(10, 8, 'andamento', [('FER-2201', 1, 540.00, 'revendavel')])]); pg.evaluate("render()")
        ok(perto(conta(8)['devolucao'], 0), 'devolução com item que o pedido não tem é ignorada')
        # o custo medio
        pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ custosEcommerce: { custoBase: 'medio' } }))")
        a, o = confere(8, [dev_py(10, 8, 'andamento', [('PAP-3001', 2, 18.50, 'revendavel')])], 'com o custo médio, o que volta é o custo médio do item', base='medio', entrega=entrega8)
        ok(perto(a['custoRecuperado'], 23.00), 'o custo médio do caderno é 11,50: 2 × 11,50 = 23,00')
        pg.evaluate("localStorage.removeItem('deskParametros')")
        # a gravada vence a de exemplo de mesmo id (DV-0011 e o pedido 1)
        grava([]); pg.evaluate("render()")
        ok(perto(conta(1)['devolucao'], 178) and perto(conta(1)['comissao'], 71.75), 'sem nada gravado vale o exemplo: pedido 1, devolução 178,00 e comissão 71,75')
        grava([dev_py(2, 1, 'cancelada', [('FON-BT-200', 1, 249.90, 'revendavel')], numero='DV-0011', aberta='2026-10-03')]); pg.evaluate("render()")
        ok(perto(conta(1)['devolucao'], 0) and perto(conta(1)['comissao'], 94) and perto(conta(1)['lucro'], float(oraculo(por[1], devolucoes=[d for d in DEVOLUCOES if d['id'] != 2])['lucro'])),
           'a gravada vence a de exemplo de mesmo id: DV-0011 cancelada e o pedido 1 volta a 94,00 de comissão e sem devolução')
        grava([]); pg.evaluate("render()")
        # a tela
        todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        ok('Devolução' in cabecalho() and 'Cortesia' in cabecalho(), 'a coluna Devolução aparece, porque há devolução aceita na lista')
        pg.click('#filtroLoja .dropdown-select-btn'); pg.click('#filtroLoja .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(200)
        ok('Devolução' not in cabecalho() and 'Cortesia' not in cabecalho(), 'e some quando é zero em tudo (Desk Brands não tem devolução aceita nem vale de cortesia)')
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200); todo_periodo()
        pg.click('#corpoTabela tr[data-id="1"]'); pg.wait_for_timeout(300)
        corpo = texto('#eventDrawer').lower()
        ok(all(t in corpo for t in ('valor devolvido', 'r$ 445,00', 'custo recuperado', 'r$ 267,00', 'perda do avariado', 'frete da volta', 'r$ 178,00')), 'o painel do pedido 1 detalha a devolução: devolvido 445,00, custo que voltou 267,00, devolução 178,00')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        pg.click('#corpoTabela tr[data-id="3"]'); pg.wait_for_timeout(300)
        corpo = texto('#eventDrawer').lower()
        ok('r$ 199,90' in corpo and 'r$ 38,90' in corpo and 'r$ 373,80' in corpo, 'o painel do pedido 3: perda do avariado 199,90, frete da volta pago pela loja 38,90, devolução 373,80')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        pg.click('#corpoTabela tr[data-id="4"]'); pg.wait_for_timeout(300)
        ok('devolução em análise' in texto('#eventDrawer').lower() and 'R$ 199,90' in texto('#eventDrawer'), 'o painel do pedido 4 traz só o aviso "devolução em análise" (199,90), sem somar na conta')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ir(PV_D, '?id=3')
        cx = texto('#caixaResultado')
        ok(all(t in cx for t in ('Devolução', 'Valor devolvido', 'R$ 334,90', 'Custo recuperado', 'Perda do avariado', 'R$ 199,90', 'Frete da volta', 'R$ 38,90', '− R$ 265,80')), 'a caixa da página do pedido 3 traz valor devolvido (334,90, já sem o vale), custo recuperado, perda do avariado e frete da volta')
        ok(re.search(r'Valor devolvido\s*os itens da devolução aceita, já sem a parte paga com vale de cortesia\s*R\$ 334,90', pg.inner_text('#caixaResultado').replace('\n', ' ')) is not None, 'a legenda do Valor devolvido ganha "já sem a parte paga com vale de cortesia" quando há cortesia')
        ok('DV-0010: 1 Kit Escritório Completo' in cx and 'DV-0007' not in cx, 'a caixa do pedido 3 traz a linha da DV-0010 (a DV-0007, cancelada, não)')
        ok(pg.get_attribute('#caixaResultado a:has-text("DV-0010")', 'href') == '../logistica/pagina-logistica-devolucao-detalhe.html?id=3', 'e DV-0010 é link para o detalhe da devolução')
        ir(PV_D, '?id=1'); cx = texto('#caixaResultado')
        ok('DV-0011: 1 Fone de Ouvido Bluetooth X200 e 2 Carregador Turbo 33W' in cx and 'uma por pedido, pela embalagem da loja' in cx and 'já sem a parte paga' not in cx and cx.index('Valor devolvido') < cx.index('DV-0011:') < cx.index('Custo recuperado'),
           'a caixa do pedido 1: a linha "DV-0011: 1 Fone de Ouvido Bluetooth X200 e 2 Carregador Turbo 33W" logo abaixo do Valor devolvido, sem a nota de cortesia (não há vale), e a embalagem "uma por pedido"')
        ir(PV_D, '?id=3'); cx = texto('#caixaResultado')
        # varios itens: separados por virgula, o ultimo por "e"; a gravada com o mesmo id vence
        ir(TELA); limpar(); ir(TELA)
        grava([dev_py(10, 8, 'andamento', [('PAP-3001', 1, 18.50, 'revendavel'), ('ELE-1003', 1, 59.90, 'revendavel'), ('PAP-3002', 2, 64.90, 'revendavel')], numero='DV-0030')]); pg.evaluate('render()')
        ok(pg.evaluate("devolucoesNomeadas(PEDIDOS.filter(p => p.id === 8)[0]).map(d => d.numero + ': ' + d.texto)") == ['DV-0030: 1 Caderno Universitário 200 folhas, 1 Mouse Sem Fio Compacto e 2 Kit Papelaria Volta às Aulas'],
           'com três itens: vírgula entre os primeiros e "e" antes do último')
        limpar()
        ir(PV_D, '?id=4')
        ok('Devolução em análise' in texto('#caixaResultado') and 'R$ 199,90' in texto('#caixaResultado'), 'e a do pedido 4 traz o aviso da devolução em análise')
        limpar()

    # ================================================================ 11. cortesia
    if secao(11, 'O vale de cortesia é desconto: a venda diminui, a coluna, o espelho do exemplo'):
        abrir(); todo_periodo(); todos = dados(); por = {x['id']: x for x in todos}
        ok(perto(conta(3)['cortesia'], 15) and perto(conta(16)['cortesia'], 25) and all(conta(i)['cortesia'] == 0 for i in (1, 4, 8, 9, 11, 12)),
           'no exemplo só os pedidos 3 (15,00) e 16 (25,00) usaram vale de cortesia')
        ok(perto(conta(16)['venda'], 2340 - 25) and perto(conta(16)['comissao'], 117), 'a venda do 16 é 2.340,00 − 25,00 = 2.315,00, e a comissão segue 5% de 2.340,00 = 117,00 (a comissão não muda nesta entrega)')
        ls = {int(re.search(r'nº (\d+)', l[0]).group(1)): l for l in linhas()}
        ok(ls[16][4] == 'R$ 25,00' and ls[3][4] == 'R$ 15,00' and ls[1][4] == 'R$ 0,00', 'a coluna Cortesia mostra o vale de cada pedido: %s' % [ls[i][4] for i in (1, 3, 16)])
        # simulacao: so cortesia conta, uso estornado e outras origens nao
        vales = {'vales': [
            {'n': 1, 'origem': 'cortesia', 'valor': 100, 'usos': [{'valor': 20, 'doc': {'tipo': 'pedido', 'id': 9}}, {'valor': 5, 'doc': {'tipo': 'pedido', 'id': 9}, 'estornado': {'em': '2026-10-20'}},
                                                                   {'valor': 7, 'doc': {'tipo': 'pdv', 'id': 9}}]},
            {'n': 2, 'origem': 'devolucao', 'valor': 50, 'usos': [{'valor': 10, 'doc': {'tipo': 'pedido', 'id': 9}}]},
            {'n': 3, 'origem': 'comissao', 'valor': 50, 'usos': [{'valor': 12, 'doc': {'tipo': 'pedido', 'id': 9}}]}]}
        pg.evaluate("(v) => { localStorage.setItem('deskValesCompra', JSON.stringify(v)); localStorage.setItem('deskValesCompraExemplo', '1'); }", vales); pg.evaluate("render()")
        a, o = conta(9), oraculo(por[9], cortesia=20)
        ok(perto(a['cortesia'], 20) and perto(a['venda'], 435) and perto(a['lucro'], o['lucro']) and perto(conta(3)['cortesia'], 0) and perto(conta(16)['cortesia'], 0),
           'só o uso de vale de origem cortesia, não estornado, conta: 20,00 no pedido 9 (venda 435,00); devolução, comissão, estornado e PDV não contam, e com a marca do exemplo ele não volta')
        pg.evaluate("render()"); ls = {int(re.search(r'nº (\d+)', l[0]).group(1)): l for l in linhas()}
        ok(ls[9][4] == 'R$ 20,00', 'a coluna Cortesia mostra o 20,00 do pedido 9')
        # a devolucao nao traz de volta a parte paga com o vale: 2 cadernos (37,00) no pedido 9 (total 455,00, sem frete, cortesia 20,00) -> 37,00 x 435 / 455 = 35,37
        devs9 = [dev_py(10, 9, 'andamento', [('PAP-3001', 2, 18.50, 'revendavel')], {'paga': 'cliente', 'valor': 20})]
        entrega9 = {9: (HOJE_PY + datetime.timedelta(days=por[9]['dp'])).isoformat()}
        grava(devs9); pg.evaluate("render()"); a, o = conta(9), oraculo(por[9], cortesia=20, devolucoes=devs9, entrega=entrega9)
        ok(perto(a['devolvido'], 35.37) and perto(o['devolvido'], 35.37) and perto(a['devolucao'], o['devolucao']) and perto(a['lucro'], o['lucro']),
           'com 20,00 de cortesia o valor devolvido de 2 cadernos (37,00) é 37,00 × 435 / 455 = 35,37, e a conta bate com a refeita em Python: %s' % a['devolvido'])
        ok(perto(a['comissao'], o['comissao']) and perto(a['comissao'], float(oraculo(por[9], cortesia=0, devolucoes=devs9, entrega=entrega9)['comissao'])), 'a comissão não muda por causa da cortesia na devolução (segue a soma dos itens)')
        pg.evaluate("localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [] }))"); pg.evaluate("render()"); a = conta(9)
        ok(perto(a['cortesia'], 0) and perto(a['devolvido'], 37), 'sem cortesia o valor devolvido é a soma dos itens, 37,00')
        grava([]); pg.evaluate("render()")
        limpar(); pg.evaluate("render()")
        # espelho do exemplo: o que a Vale-compra grava
        ir(PV_D); limpar(); ir(PV_D)
        gravados = sorted((u['doc']['id'], u['valor']) for v in pg.evaluate("valeLer()") if v['origem'] == 'cortesia' for u in v['usos'] if u['doc']['tipo'] == 'pedido')
        ir(TELA)
        espelho = sorted((u['doc']['id'], u['valor']) for v in pg.evaluate("RES_VALES_EXEMPLO") for u in v['usos'])
        ok(gravados == espelho == sorted(CORTESIA_EXEMPLO.items()), 'RES_VALES_EXEMPLO repete os usos de cortesia que o exemplo de Vale-compra grava: %s' % espelho)
        limpar()

    # ================================================================ 12. produto, categoria e estado
    if secao(12, 'Produto, categoria e estado: agrupar, filtrar e a repartição por item'):
        abrir(); todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();"); todos = dados(); por = {x['id']: x for x in todos}
        base_ = {pid: oraculo(por[pid]) for pid in ONLINE}
        partes_py = {pid: itens_do_pedido(por[pid], base_[pid]) for pid in ONLINE}
        lucro_total = sum(o['lucro'] for o in base_.values())
        # a repartição fecha no pedido e bate com a refeita em Python
        errados = []
        for pid in ONLINE:
            js = pg.evaluate("(i) => { const p = PEDIDOS.filter(x => x.id === i)[0]; const r = resultadoDoPedido(p); return [r, partesDoPedido(p, r)]; }", pid)
            r, pts = js
            for k in ('venda', 'freteCobrado', 'cortesia', 'difFrete', 'taxa', 'comissao', 'embalagem', 'custo', 'devolucao', 'lucro'):
                if not perto(sum(x['r'][k] for x in pts), r[k]): errados.append((pid, k, 'soma'))
            for x, (sku, cat, py) in zip(pts, partes_py[pid]):
                for k_js, k_py in (('venda', 'venda'), ('difFrete', 'difFrete'), ('taxa', 'taxa'), ('comissao', 'comissao'), ('embalagem', 'embalagem'), ('custo', 'custo'), ('devolucao', 'devolucao'), ('lucro', 'lucro')):
                    if x['sku'] != sku or not perto(x['r'][k_js], py[k_py]): errados.append((pid, sku, k_js, x['r'][k_js], float(py[k_py])))
        ok(not errados, 'a repartição por item fecha no total do pedido, parcela por parcela, e bate com a refeita em Python nos 8 pedidos: %s' % errados[:3])
        skus = sorted({i[0] for pid in ONLINE for i in ITENS[pid]}); cats = sorted({i[2] for pid in ONLINE for i in ITENS[pid]})

        def agrupa(valor):
            pg.click('#filtroAgrupar .dropdown-select-btn'); pg.wait_for_timeout(100)
            pg.click('#filtroAgrupar .dropdown-select-item[data-value="%s"]' % valor); pg.wait_for_timeout(200)
        agrupa('produto'); ls = linhas()
        ok(len(ls) == len(skus) and cabecalho()[0] == 'Produto' and abs(sum(num(l[-2]) for l in ls) - float(lucro_total)) < 0.02, 'agrupar por Produto: uma linha por produto (%d) e o lucro das linhas soma o lucro total' % len(skus))
        alvo = 'PAP-3001'
        esp = sum(py['lucro'] for pid in ONLINE for sku, cat, py in partes_py[pid] if sku == alvo)
        linha = [l for l in ls if alvo in l[0]][0]
        npeds = len({pid for pid in ONLINE for i in ITENS[pid] if i[0] == alvo})
        ok(num(linha[-2]) == float(esp) and ('%d pedidos' % npeds) in linha[0], 'a linha do Caderno Universitário soma a parte dele nos %d pedidos: lucro %s' % (npeds, linha[-2]))
        pg.click('#corpoTabela tr[data-grupo="%s"]' % alvo); pg.wait_for_timeout(250)
        com = sorted(pid for pid in ONLINE if any(i[0] == alvo for i in ITENS[pid]))
        ok(pg.evaluate("agrupar") == 'pedido' and pg.input_value('#campoBusca') == alvo and sorted(numeros()) == com, 'clicar no produto volta para Pedido, filtrado por ele: %s' % sorted(numeros()))
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200); todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        agrupa('categoria'); ls = linhas()
        ok(len(ls) == len(cats) == 4 and cabecalho()[0] == 'Categoria' and abs(sum(num(l[-2]) for l in ls) - float(lucro_total)) < 0.02, 'agrupar por Categoria: %d linhas e o lucro soma o total' % len(ls))
        esp = sum(py['lucro'] for pid in ONLINE for sku, cat, py in partes_py[pid] if cat == 'Papelaria')
        ok(num([l for l in ls if l[0].startswith('Papelaria')][0][-2]) == float(esp), 'a linha de Papelaria soma a parte dos itens dessa categoria')
        pg.click('#corpoTabela tr[data-grupo="Papelaria"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("fCategoria") == 'Papelaria' and texto('#filtroCategoria .dropdown-select-label') == 'Papelaria' and sorted(numeros()) == sorted(pid for pid in ONLINE if any(i[2] == 'Papelaria' for i in ITENS[pid])),
           'clicar na categoria volta para Pedido, filtrado por ela')
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200); todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        agrupa('uf'); ls = linhas()
        ufs = {pid: por[pid]['ufEntrega'] for pid in ONLINE}
        ok(cabecalho()[0] == 'Estado de destino' and len(ls) == len(set(ufs.values())) and any(l[0].startswith('Amazonas (AM)') for l in ls) and abs(sum(num(l[-2]) for l in ls) - float(lucro_total)) < 0.02,
           'agrupar por Estado de destino: uma linha por estado (%d), Amazonas entre elas, e o lucro soma o total' % len(ls))
        am = [i for i, l in enumerate(ls) if l[0].startswith('Amazonas')][0]
        pg.click('#corpoTabela tr:nth-child(%d)' % (am + 1)); pg.wait_for_timeout(250)
        ok(numeros() == [11] and 'estado de destino: Amazonas (AM)' in texto('#faixaGrupo'), 'clicar em Amazonas volta para o pedido 11, com a faixa do filtro: %s' % texto('#faixaGrupo'))
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200); todo_periodo(); pg.evaluate("itensPorPaginaAtual = 100; render();")
        # filtros
        cats_menu = pg.evaluate("Array.from(document.querySelectorAll('#filtroCategoria .dropdown-select-item')).map(e => e.textContent.trim())")
        ok(cats_menu == ['Todas as categorias'] + cats, 'o filtro Categoria lista as categorias dos itens: %s' % cats_menu)
        pg.fill('#campoBusca', 'camiseta'); pg.wait_for_timeout(200)
        com = sorted(pid for pid in ONLINE if any(i[0] == 'VES-2001' for i in ITENS[pid]))
        ok(sorted(numeros()) == com, 'a pesquisa busca no nome dos itens, sem acento e em qualquer parte do nome: "camiseta" traz só os pedidos que têm o item: %s' % sorted(numeros()))
        parte = [(pid, py) for pid in com for sku, cat, py in partes_py[pid] if sku == 'VES-2001']
        cards = pg.evaluate("[kpiFaturamento, kpiLucro].map(e => e.textContent)")
        ok(cards == [br(sum(py['venda'] for _, py in parte)), br(sum(py['lucro'] for _, py in parte))], 'os cards somam só a parte da camiseta em cada pedido: %s' % cards)
        ok('só a parte do item "camiseta"' in texto('.ce-barra-titulo'), 'e o título da barra diz isso: %s' % texto('.ce-barra-titulo'))
        l4 = [l for l in linhas() if 'nº 4 ' in l[0] + ' '][0]
        py4 = [py for sku, cat, py in partes_py[4] if sku == 'VES-2001'][0]
        ok(l4[2] == br(py4['venda']) and num(l4[-2]) == float(py4['lucro']), 'a linha do pedido 4 mostra a parte da camiseta (venda %s), não o pedido inteiro' % l4[2])
        pg.fill('#campoBusca', 'MOB-4001'); pg.wait_for_timeout(150)
        ok(sorted(numeros()) == sorted(pid for pid in ONLINE if any(i[0] == 'MOB-4001' for i in ITENS[pid])), 'a busca também acha pelo SKU')
        pg.fill('#campoBusca', 'xyz'); pg.wait_for_timeout(150)
        ok(numeros() == [] and pg.evaluate("document.getElementById('emptyState').style.display") != 'none', 'produto que nenhum pedido tem: lista vazia')
        pg.fill('#campoBusca', ''); pg.wait_for_timeout(100)
        pg.click('#filtroCategoria .dropdown-select-btn'); pg.click('#filtroCategoria .dropdown-select-item[data-value="Papelaria"]'); pg.wait_for_timeout(200)
        parte = [py for pid in ONLINE for sku, cat, py in partes_py[pid] if cat == 'Papelaria']
        cards = pg.evaluate("[kpiFaturamento, kpiLucro].map(e => e.textContent)")
        ok(cards == [br(sum(py['venda'] for py in parte)), br(sum(py['lucro'] for py in parte))] and 'só a parte da categoria Papelaria' in texto('.ce-barra-titulo'), 'a categoria Papelaria soma só a parte dos itens dela, e o título diz: %s' % cards)
        pg.fill('#campoBusca', 'caderno'); pg.wait_for_timeout(150)
        parte = [py for pid in ONLINE for sku, cat, py in partes_py[pid] if sku == 'PAP-3001']
        ok(pg.evaluate("kpiFaturamento.textContent") == br(sum(py['venda'] for py in parte)) and 'e da categoria' in texto('.ce-barra-titulo'), 'produto e categoria juntos: só o caderno, e o título cita os dois')
        agrupa('produto')
        ok(len(linhas()) == 1, 'agrupar por produto com o filtro ligado mostra só o produto do filtro')
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200)
        ok(pg.input_value('#campoBusca') == '' and texto('#filtroCategoria .dropdown-select-label') == 'Todas as categorias', 'Limpar filtros limpa a pesquisa e a categoria')
        limpar()

    # ================================================================ 13. devolucao: bloco e espelhos
    if secao(13, 'Blocos idênticos (devoluções), espelhos da Devolução e de Cadastros › Produtos'):
        def fonte2(n):
            return open(localiza.onde(n), encoding='utf-8').read()

        def bloco2(t, ini, fim):
            a = t.index(ini)
            return t[a:t.index(fim, a) + len(fim)]
        quem = [TELA, PV_D, COM, COM_D, CLI_D]
        dv = [bloco2(fonte2(n), '  // ===== DEVOLUCOES: LEITURA', '  // ===== FIM DO BLOCO DEVOLUCOES: LEITURA =====') for n in quem]
        ok(all(x == dv[0] for x in dv) and 'function devolucoesDoPedido' in dv[0], 'o bloco DEVOLUCOES: LEITURA é idêntico nas 5 telas que carregam a conta')
        forma = "d => [d.id, d.numero, d.vendaId, d.abertaEm, d.situacao, d.itens.map(i => [i.sku, i.qtd, i.unit, i.estado]), d.reversa ? [d.reversa.paga, d.reversa.valor] : null]"
        ir(TELA); limpar(); ir(TELA)
        espelho = pg.evaluate("DEVOLUCOES_C.map(%s)" % forma)
        for tela_dev in (DEVOL, DEVOL_D):
            ir(tela_dev); limpar(); ir(tela_dev)
            ok(pg.evaluate("DEVOLUCOES.map(%s)" % forma) == espelho and len(espelho) == 6, 'DEVOLUCOES_C repete as 6 devoluções de %s (id, número, venda, abertura, situação, itens com estado, e a reversa com quem paga e o valor)' % tela_dev)
        ir(DEVOL); t1 = pg.evaluate("totalItens.toString()")
        ir(DEVOL_D); t2 = pg.evaluate("totalItensDev.toString()")
        ir(TELA); t3 = pg.evaluate("totalItensDev.toString()")
        ret = lambda s: re.search(r'return (.*?);', s).group(1)
        ok(ret(t1) == ret(t2) == ret(t3), 'o valor devolvido é a mesma conta de totalItens da Devolução (%s)' % ret(t3))
        ir(DEVOL)
        entregas = pg.evaluate("VENDAS.filter(v => [1, 3, 4].indexOf(v.id) >= 0).map(v => [v.id, v.entregaEm])")
        ir(TELA)
        ok(dict(entregas) == {int(k): v for k, v in pg.evaluate("ENTREGA_DA_VENDA").items()}, 'ENTREGA_DA_VENDA repete o entregaEm das vendas 1, 3 e 4 da Devolução: %s' % entregas)
        # as vendas 1, 3 e 4 da Devolucao sao os pedidos de venda 1, 3 e 4: itens, quantidades e preco
        itens_dev = {}
        ir(DEVOL); vendas = {v['id']: v for v in pg.evaluate("VENDAS")}; devs = pg.evaluate("DEVOLUCOES")
        errados = []
        for vid in (1, 3, 4):
            esperado = [(i[0], i[3], i[4]) for i in ITENS[vid]]
            if [(i['sku'], i['qtd'], i['unit']) for i in vendas[vid]['itens']] != esperado:
                errados.append(('venda', vid))
            for d in [d for d in devs if d['vendaId'] == vid]:
                for i in d['itens']:
                    m = [x for x in ITENS[vid] if x[0] == i['sku']]
                    if not m or i['qtdVendida'] != m[0][3] or i['qtd'] > i['qtdVendida'] or abs(i['unit'] - m[0][4]) > 0.001:
                        errados.append((d['numero'], i['sku']))
        ok(not errados, 'as devoluções das vendas 1, 3 e 4 têm itens que existem nos pedidos 1, 3 e 4, com a quantidade vendida deles e o mesmo preço: %s' % errados)
        ok(any(d['reversa'] and d['reversa'].get('paga') == 'nos' and d['reversa'].get('valor') for d in devs if d['vendaId'] in (1, 3, 4)) and
           any(i['estado'] == 'avaria' for d in devs if d['vendaId'] in (1, 3, 4) for i in d['itens']),
           'o exemplo tem pelo menos um item avariado e uma reversa paga pela loja entre as devoluções dos pedidos online')
        ok(sorted((d['numero'], d['abertaEm'], d['situacao']) for d in devs) == sorted([('DV-0012', '2026-10-06', 'aberta'), ('DV-0011', '2026-10-03', 'andamento'), ('DV-0010', '2026-09-29', 'finalizada'),
                                                                                          ('DV-0009', '2026-10-06', 'aberta'), ('DV-0008', '2026-08-12', 'finalizada'), ('DV-0007', '2026-09-22', 'cancelada')]), 'número, data e situação das 6 devoluções ficaram como estavam')
        # Cadastros > Produtos: o mesmo sku, nome e categoria
        ir(PRODUTOS); prod = {p['sku']: (p['nome'], p['categoria']) for p in pg.evaluate("PRODUTOS")}
        fora = [(pid, i[0]) for pid in ONLINE for i in ITENS[pid] if pid != 1 and prod.get(i[0]) != (i[1], i[2])]
        ok(not fora, 'os itens dos pedidos online 3, 4, 8, 9, 11, 12 e 16 são produtos de Cadastros › Produtos, com o mesmo SKU, nome e categoria: %s' % fora)
        ok(all(i[0] not in prod for i in ITENS[1]), 'o pedido 1 segue com os SKUs do catálogo do pedido (FON-BT-200 e outros), que Cadastros › Produtos não tem: a categoria deles é a mais próxima')

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
