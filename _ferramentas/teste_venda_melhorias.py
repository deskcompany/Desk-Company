# -*- coding: utf-8 -*-
# Vendas: os itens V2, V3 e V5 da lista de melhorias (12/out/2026).
#
#   [1] V3  indicadores em Pedidos de Venda: a aprovar, a faturar, atrasados para entrega e vendido em
#           30 dias. Cada um soma o que diz somar, e clicar deixa na lista exatamente aqueles pedidos;
#   [2] V2  a pagina do pedido mostra o acompanhamento inteiro, etapa por etapa, com o estado e o link.
#           Os itens "Acompanhar no galpao" e "na bancada" sairam do menu: nada aparece duas vezes;
#   [3] V5  a venda do PDV aparece em Pedidos de Venda e no Caixa, e a conclusao leva ao pedido;
#   [4] nenhum texto chama pelo nome a tela de Performance de Vendas, que deixou de existir.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

PED, PEDD, PDV, CAIXA = 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-vendas-pdv.html', 'pagina-financas-caixa.html'
SO = (sys.argv[1:] or [''])[0]

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def secao(n, titulo):
    if SO and SO != str(n):
        return False
    print('\n[%d] %s' % (n, titulo))
    return True


fonte = lambda n: open(localiza.onde(n), encoding='utf-8').read()

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    pg.add_init_script("window.print = function () {};")
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def escolher(raiz, valor):
        clic('#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(120)
        pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
        pg.wait_for_timeout(220)

    def na_tela():
        return pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr[data-id]')).map(tr => Number(tr.getAttribute('data-id')))")

    def limpar_guardado():
        pg.evaluate("['deskPdv', 'deskCaixaExtras'].forEach(k => localStorage.removeItem(k))")

    if secao(1, 'V3: os indicadores de Pedidos de Venda somam o que dizem, e clicar filtra a lista'):
        ir(PED); limpar_guardado(); ir(PED)
        padrao = pg.evaluate("periodoAtual")
        contas = pg.evaluate("""(() => { const dias = (s) => Math.round((new Date(s + 'T00:00:00') - HOJE) / 86400000), andando = ['aberto', 'aprovado', 'separacao', 'conferenciasaida', 'faturado', 'prontoenvio'];
            const grupos = { aprovar: PEDIDOS.filter(p => p.situacao === 'aberto'), faturar: PEDIDOS.filter(p => ['aprovado', 'separacao', 'conferenciasaida'].includes(p.situacao)),
              atrasados: PEDIDOS.filter(p => andando.includes(p.situacao) && dias(p.previsto) < 0), periodo: PEDIDOS.filter(p => p.situacao !== 'cancelado' && dias(p.data) <= 0 && dias(p.data) >= -30) };
            return Object.fromEntries(Object.keys(grupos).map(k => [k, { valor: fmtMoeda(grupos[k].reduce((s, p) => s + p.total, 0)), ids: grupos[k].map(p => p.id).sort((a, b) => a - b) }])); })()""")
        visto = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.pv-kpis .kpi-card')).map(c => [c.getAttribute('data-kpi'), c.querySelector('.kpi-value').textContent]))")
        ok(visto == {k: v['valor'] for k, v in contas.items()} and all(len(v['ids']) >= 2 for v in contas.values()),
           'os quatro indicadores somam os pedidos deles, contados a parte: %s' % visto)
        ok(pg.evaluate("document.querySelector('.pv-kpis [data-kpi=atrasados] .kpi-delta').textContent") == '%d pedidos' % len(contas['atrasados']['ids']), 'e dizem quantos pedidos sao')
        pg.evaluate("document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]').click()"); pg.wait_for_timeout(220)
        for k in ['aprovar', 'faturar', 'atrasados', 'periodo']:
            pg.evaluate("(k) => document.querySelector('.pv-kpis [data-kpi=\"' + k + '\"]').click()", k); pg.wait_for_timeout(280)
            acesos = pg.evaluate("Array.from(document.querySelectorAll('.pv-kpis .kpi-card.on')).map(c => c.getAttribute('data-kpi'))")
            ok(sorted(na_tela()) == contas[k]['ids'] and acesos == [k], '  clicar em "%s" deixa na lista exatamente os %d pedidos do indicador, e so ele fica aceso' % (k, len(contas[k]['ids'])))
        pg.evaluate("document.querySelector('.pv-kpis [data-kpi=periodo]').click()"); pg.wait_for_timeout(280)
        ok(pg.evaluate("periodoAtual") == padrao and pg.locator('.pv-kpis .kpi-card.on').count() == 0 and pg.evaluate("filtroKpi") is None
           and pg.evaluate("document.querySelector('#periodoOpcoes .periodo-op.active').getAttribute('data-periodo')") == padrao,
           '  clicar de novo no mesmo indicador desfaz: a lista volta ao periodo de abertura (%s)' % padrao)
        pg.evaluate("document.querySelector('.pv-kpis [data-kpi=aprovar]').click()"); pg.wait_for_timeout(240)
        pg.evaluate("trocarSituacao('enviado')"); pg.wait_for_timeout(240)
        ok(pg.locator('.pv-kpis .kpi-card.on').count() == 0 and pg.evaluate("filtroKpi") is None, '  mexer na situacao a mao apaga o indicador')
        pg.evaluate("document.querySelector('.pv-kpis [data-kpi=faturar]').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(240)
        ok(pg.evaluate("kpiAtivo") == 'faturar', '  o indicador responde ao teclado (Enter)')
        ok(not pg.evaluate("document.documentElement.scrollWidth > window.innerWidth") and pg.evaluate("Array.from(document.querySelectorAll('.pv-kpis .kpi-card')).every(c => c.querySelector('.kpi-value').scrollWidth <= c.clientWidth)"),
           '  os quatro cabem na largura, sem estourar o proprio quadro')

    if secao(2, 'V2: a pagina do pedido mostra o acompanhamento inteiro'):
        ir(PEDD)
        passos = lambda: pg.evaluate("Array.from(document.querySelectorAll('#trilhaPassos .trilha-passo')).map(e => [e.querySelector('b').textContent, e.querySelector('span').textContent, e.getAttribute('href') || ''])")
        ps = passos()
        cliente = pg.evaluate("PEDIDO.cliente")
        ok(pg.evaluate("getComputedStyle(document.getElementById('trilhaPedido')).display") != 'none' and [x[0] for x in ps] == ['Separação', 'Conferência de Saída', 'Expedição', 'Rastreamento', 'Contas a Receber', 'Devolução'],
           'o pedido tem o quadro "Acompanhamento", com as seis paradas do caminho: %s' % [x[0] for x in ps])
        ok(pg.evaluate("PEDIDO.situacao") == 'aberto' and [x[1] for x in ps[:4]] == ['ainda não chegou'] * 3 + ['só depois do envio'] and not any(x[2] for x in ps[:4]) and ps[5][1] == 'só depois do envio' and not ps[5][2],
           'pedido em aberto: galpao, rastreio e devolucao ainda nao tem link, e dizem por que')
        ok(ps[4][2].endswith('pagina-financas-contas-receber.html?busca=' + cliente.replace(' ', '%20')), 'a conta a receber ja tem link, para as contas do cliente')
        menu = pg.evaluate("Array.from(document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')).map(e => e.textContent.trim())")
        ok(not [m for m in menu if 'Acompanhar' in m] and 'Financeiro do cliente' in menu and 'Ver conta a receber' not in menu,
           'os dois "Acompanhar..." sairam do menu (estao no quadro), e "Ver conta a receber" passou a dizer o que abre: %s' % menu[:4])
        pg.evaluate("(() => { PEDIDO.situacao = 'conferenciasaida'; aplicarSituacao(); })()"); pg.wait_for_timeout(200)
        ps = passos()
        ok(ps[0][1] == 'concluída' and ps[1][1] == 'em andamento' and ps[2][1] == 'ainda não chegou' and 'pagina-logistica-separacao' in ps[0][2] and 'pagina-logistica-conferencia-saida' in ps[1][2] and not ps[2][2],
           'andando o pedido ate a conferencia: Separacao concluida, Conferencia em andamento, Expedicao ainda nao')
        pg.evaluate("(() => { PEDIDO.situacao = 'entregue'; aplicarSituacao(); })()"); pg.wait_for_timeout(200)
        ps = passos()
        ok([x[1] for x in ps[:4]] == ['concluída'] * 4 and 'pagina-logistica-rastreamento.html?busca=' in ps[3][2] and 'pagina-logistica-devolucao.html?busca=' in ps[5][2],
           'pedido entregue: as quatro etapas concluidas, com o rastreio e a devolucao ja ligados')
        pg.evaluate("(() => { PEDIDO.situacao = 'cancelado'; aplicarSituacao(); })()"); pg.wait_for_timeout(200)
        ps = passos()
        ok([x[1] for x in ps if x[0] != 'Contas a Receber'] == ['pedido cancelado'] * 5 and not any(x[2] for x in ps if x[0] != 'Contas a Receber'), 'pedido cancelado: nenhuma etapa do galpao vira link')
        f_lista, f_pag = fonte(PED), fonte(PEDD)
        ok('const NO_GALPAO = { separacao: [5, 6, 7], conferencia: [7] };' in f_lista and 'const NO_GALPAO = { separacao: [5, 6, 7], conferencia: [7] };' in f_pag,
           'a pagina e a lista usam o mesmo espelho de em que fichas do galpao cada pedido existe')
        ir(PEDD, '?novo=1')
        ok(pg.evaluate("getComputedStyle(document.getElementById('trilhaPedido')).display") == 'none', 'pedido novo ainda nao tem acompanhamento')
        ir('pagina-financas-contas-receber.html', '?busca=' + cliente)
        ok(pg.evaluate("document.querySelectorAll('#listaTitulos tbody tr[data-linha=titulo]').length") >= 1, 'e o link da conta a receber cai em contas que existem, as do cliente do pedido')

    if secao(3, 'V5: a venda do PDV aparece em Pedidos de Venda e no Caixa'):
        ir(PED); limpar_guardado(); ir(PED)
        antes = pg.evaluate("PEDIDOS.length")
        ir(PDV)
        pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); ir(PDV)   # sem o desconto Pix/dinheiro (21/out/2026): o teste conta o valor cheio
        clic('#btnAbrirCaixa'); pg.wait_for_timeout(300)
        escolher('abrirLoja', 1); pg.fill('#abrirTroco', '0')
        clic('#btnConfirmarAbertura'); pg.wait_for_timeout(450)
        pg.fill('#qtdProduto', '2'); pg.fill('#buscaProduto', 'CAR-33W-01'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(300)
        clic('#btnContinuar'); pg.wait_for_timeout(350)
        escolher('selAddReceb', 'dinheiro')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        venda = pg.evaluate("ultimaVenda ? { numero: ultimaVenda.numero, total: ultimaVenda.total, itens: ultimaVenda.itens.map(i => [i.sku, i.qtd]), conta: ultimaVenda.recebimentos[0].contaId, valor: ultimaVenda.recebimentos[0].valor } : null")
        ok(pg.evaluate('momento') == 'concluida' and venda is not None and venda['total'] > 0, 'a venda de balcao foi concluida: %s' % venda)
        link = pg.evaluate("(() => { const a = document.getElementById('linkPedidoDaVenda'); return a ? [a.textContent, a.getAttribute('href')] : null; })()")
        ok(link == ['PDV-0001', '../vendas/' + PED + '?busca=PDV-0001'], 'a conclusao da venda leva ao pedido: %s' % link)
        gerado = pg.inner_text('#concGerado')
        ok('Conta em Metas e Performance' in gerado and 'Performance de Vendas' not in gerado, 'e diz "Metas e Performance", o nome que o modulo tem hoje')
        clic('#linkPedidoDaVenda'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr[data-id]')).map(tr => tr.innerText.split(String.fromCharCode(10)).join(' ').split(String.fromCharCode(9)).join(' '))")
        ok(PED in pg.url and len(linhas) == 1 and 'PDV-0001' in linhas[0] and 'ENTREGUE' in linhas[0].upper() and pg.evaluate("fmtMoeda(%r)" % venda['total']) in linhas[0],
           'e cai em Pedidos de Venda com a venda na lista, ja entregue e com o total dela: %s' % [l[:90] for l in linhas])
        ok(pg.evaluate("PEDIDOS.length") == antes + 1, '  a lista ganhou um pedido, o do balcao')
        pg.evaluate("document.querySelector('#corpoTabela tr[data-id] td:nth-child(2)').click()"); pg.wait_for_timeout(350)
        painel = pg.inner_text('#drawerCorpo')
        ok('CAR-33W-01' in painel and 'Desk Shope' in painel, '  e o painel do pedido traz o item vendido e a loja do caixa')
        pg.evaluate("(() => { document.getElementById('btnLimparFiltros').click(); const i = document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]'); if (i) i.click(); })()"); pg.wait_for_timeout(300)
        ids = na_tela()
        ok(len(ids) == antes + 1 and ids[-1] >= 900000 and ids[0] == 1, '  na ordem do numero, a venda de balcao vem depois dos pedidos numerados')
        ir(CAIXA)
        mov = pg.evaluate("MOVIMENTOS.filter(m => m.origem === 'PDV-0001').map(m => [m.contaId, m.valor, m.tipo])")
        ok(mov == [[venda['conta'], venda['valor'], 'entrada']], 'o dinheiro da venda entrou no Caixa de Financas, na conta da forma de recebimento: %s' % mov)
        if mov:
            pg.evaluate("(c) => { contaAtualId = c; periodoAtual = 'todos'; itensPorPaginaAtual = 100; render(); }", mov[0][0]); pg.wait_for_timeout(300)
            href = pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('a.cx-origem-link')).filter(x => x.textContent === 'PDV-0001')[0]; return a ? a.getAttribute('href') : ''; })()")
            ok(href == '../vendas/' + PED + '?busca=PDV-0001', '  e a origem do lancamento leva de volta ao pedido: %s' % href)
        limpar_guardado(); ir(PED)
        ok(pg.evaluate("PEDIDOS.length") == antes, 'sem venda de balcao guardada, a lista volta aos pedidos do exemplo')

    if secao(4, 'Nenhum texto chama a tela que deixou de existir'):
        vend, conf, pdv = fonte('pagina-cadastros-vendedores-detalhe.html'), fonte('pagina-configuracoes-pdv.html'), fonte(PDV)
        ok("'Performance de Vendas'" not in vend and vend.count("'Metas e Performance'") >= 2, 'no cadastro do vendedor, o acesso se chama "Metas e Performance"')
        ok('Performance de Vendas' not in conf and 'Metas e Performance' in conf, 'nas Configuracoes do PDV tambem')
        visiveis = [l for l in pdv.split(chr(10)) if 'Performance de Vendas' in l and not l.strip().startswith('//')]
        ok(not visiveis, 'e no PDV nenhum texto de tela cita "Performance de Vendas": %s' % [v.strip()[:60] for v in visiveis[:2]])

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
