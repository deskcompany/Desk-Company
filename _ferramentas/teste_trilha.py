# -*- coding: utf-8 -*-
# A trilha entre as telas (10/out/2026).
#
# A varredura dos modulos prontos mostrou que o painel lateral de quase toda lista mostrava o
# registro e nao levava a tela vizinha: a ordem de compra nao levava a nota, o pedido nao levava a
# separacao. Esta suite guarda o que foi ligado e os defeitos que a varredura achou no caminho.
#
#   [1] toda lista aceita ?busca=... no endereco: abre filtrada, com uma faixa dizendo de onde
#       veio o filtro; registro que o exemplo nao tem vira explicacao, nao lista vazia muda;
#   [2] Ordens de Compra: recebido e a receber, atraso, o botao certo para a situacao e os links;
#   [3] a ordem de compra e link na Entrada de Notas, na Conferencia de Entrada e em Necessidades
#       de Compra, e o link cai na ordem certa; nota de devolucao nao diz mais "nº null";
#   [4] Controle de Estoques: indicadores que batem com a lista, quadro que filtra, menu que leva
#       as vizinhas, e a pagina do produto leva a compra e ao giro;
#   [5] Reposicao: "o caminho e comprar" virou link, e a aba se chama "A repor";
#   [6] Vendas e Logistica: o pedido leva a cada etapa, e a etapa leva de volta ao pedido;
#   [7] defeitos: cada nota da Conferencia de Entrada abre o proprio painel (duas tinham o mesmo
#       identificador), e o Pedido manda o numero dele para o galpao.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

OC = 'pagina-estoque-ordens-compra.html'
NOTAS = 'pagina-estoque-entrada-notas.html'
DOCA = 'pagina-estoque-conferencia-entrada.html'
CE = 'pagina-estoque-controle-estoques.html'
PROD = 'pagina-estoque-controle-estoques-detalhe.html'
REPO = 'pagina-estoque-reposicao.html'
ENDER = 'pagina-estoque-enderecamento.html'
NEC = 'pagina-estoque-necessidades-compra.html'
PED = 'pagina-vendas-pedidos.html'
PEDD = 'pagina-vendas-pedidos-detalhe.html'
SEP = 'pagina-logistica-separacao.html'
CONF = 'pagina-logistica-conferencia-saida.html'
EXP = 'pagina-logistica-expedicao.html'
DEV = 'pagina-logistica-devolucao.html'
MARCA_BUSCA = '  // ===== BUSCA PELO ENDERECO (bloco compartilhado, 10/out/2026) ====='

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def bloco(texto, marca):
    a = texto.index(marca)
    return texto[a:texto.index('  // ===== ', a + 10)]


LINHAS = "(document.querySelectorAll('.main tbody tr').length || Array.from(document.querySelectorAll('.main .card .item-checkbox')).filter(e => e.offsetParent !== null).length)"
FAIXA = "(() => { const f = document.getElementById('faixaBuscaLink'); return f ? f.querySelector('span').textContent : ''; })()"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(380)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def linha(texto, coluna=2):
        """Clica na linha da lista que contem o texto. A linha pode estar na segunda pagina: mostra 100 por pagina."""
        if not pg.evaluate("(t) => Array.from(document.querySelectorAll('.main tbody tr')).some(r => r.innerText.includes(t))", texto):
            pg.evaluate("(() => { const i = document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]'); if (i) i.click(); })()")
            pg.wait_for_timeout(300)
        pg.evaluate("([t, c]) => { const tr = Array.from(document.querySelectorAll('.main tbody tr')).filter(r => r.innerText.includes(t))[0]; (tr.children[c - 1] || tr).click(); }", [texto, coluna])
        pg.wait_for_timeout(420)

    def painel():
        return pg.inner_text('#drawerCorpo') if pg.locator('#drawerCorpo').count() else ''

    def seguir(sel):
        """Clica num link do painel e devolve (tela de destino, texto da faixa, linhas na lista)."""
        clic(sel); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        return pg.url.split('/')[-1].split('?')[0], pg.evaluate(FAIXA), pg.evaluate(LINHAS)

    print('\n[1] Toda lista aceita a busca pelo endereco')
    fontes = {n: open(localiza.onde(n), encoding='utf-8').read() for n in localiza.nomes()}
    listas = [n for n in fontes if MARCA_BUSCA in fontes[n]]
    # Eram 30 ate Performance de Vendas virar parte de Metas e Performance.
    ok(len(listas) >= 29 and len(set(bloco(fontes[n], MARCA_BUSCA) for n in listas)) == 1, 'o bloco de busca pelo endereco esta em %d listas, identico em todas' % len(listas))
    mudas = []
    for tela in listas:
        ir(tela)
        antes = pg.evaluate(LINHAS)
        ir(tela, '?busca=zzqqxx')
        if 'não tem esse registro' not in pg.evaluate(FAIXA):
            mudas.append(tela + ': sem explicacao')
            continue
        clic('#faixaBuscaLink button'); pg.wait_for_timeout(250)
        if pg.locator('#faixaBuscaLink').count() or pg.evaluate(LINHAS) != antes or pg.evaluate("document.querySelector('.main .search-wrap input').value") != '':
            mudas.append(tela + ': "Mostrar tudo" nao devolveu a lista (%s de %s)' % (pg.evaluate(LINHAS), antes))
    ok(not mudas, 'registro que o exemplo nao tem vira explicacao, e "Mostrar tudo" devolve a lista inteira: %s' % mudas[:3])
    ir(OC, '?busca=Embalagens do Vale')
    ok('Lista filtrada por "Embalagens do Vale"' in pg.evaluate(FAIXA) and pg.evaluate(LINHAS) == 2, 'Ordens de Compra com ?busca=Embalagens do Vale abre nas 2 ordens dele, com a faixa')
    ir(PED, '?busca=Marina Duarte')
    ok(pg.evaluate(LINHAS) >= 1 and pg.evaluate("document.querySelector('.periodo-op[data-periodo=\"todos\"]').classList.contains('active')"),
       'Pedidos de Venda solta o periodo padrao para o registro pedido nao ficar escondido')

    print('\n[2] Ordens de Compra: o painel da ordem')
    ir(OC)
    pg.evaluate("abrirPreview(2)"); pg.wait_for_timeout(350)
    ok(pg.inner_text('#ocRecebido') == 'R$ 2.773,20' and pg.inner_text('#ocAReceber') == 'R$ 4.539,80', 'ordem 2, em andamento: R$ 2.773,20 ja recebidos e R$ 4.539,80 a receber')
    ok(pg.locator('#btnReceberOrdem').count() == 1 and pg.inner_text('#btnReceberOrdem') == 'Receber mercadorias' and 'btn-secundario' in pg.get_attribute('#btnAbrirDetalhe', 'class'),
       'quem ainda espera mercadoria tem "Receber mercadorias" como botao principal')
    ok(pg.locator('#ocAtraso').count() == 0, 'prevista para depois de hoje (da tela): sem aviso de atraso')
    hrefs = pg.evaluate("Array.from(document.querySelectorAll('#ocLinks a')).map(a => a.getAttribute('href'))")
    ok(len(hrefs) == 3 and all('?busca=TechParts%20Distribuidora' in h for h in hrefs), 'e o painel leva a Entrada de Notas, a Conferencia de Entrada e a Necessidades de Compra, no fornecedor')
    destino, faixa, n = seguir('#ocLinks a[href*="entrada-notas"]')
    ok(destino == NOTAS and 'Lista filtrada' in faixa and n >= 1, 'o link das notas cai na Entrada de Notas filtrada, com %d nota(s) do fornecedor' % n)
    ir(OC)
    pg.evaluate("abrirPreview(4)"); pg.wait_for_timeout(300)
    ok(pg.locator('#ocAtraso').count() == 0 or 'atrasada' in pg.inner_text('#ocAtraso'), 'ordem 4: o atraso, quando ha, aparece ao lado da previsao')
    pg.evaluate("(() => { const o = ORDENS.find(x => x.id === 3); o.previsto = '2026-09-01'; abrirPreview(3); })()"); pg.wait_for_timeout(300)
    ok(pg.locator('#ocAtraso').count() == 1 and 'atrasada há 9 dias' in pg.inner_text('#ocAtraso'), 'ordem em aberto com previsao vencida diz ha quantos dias: %s' % (pg.inner_text('#ocAtraso') if pg.locator('#ocAtraso').count() else ''))
    pg.evaluate("abrirPreview(1)"); pg.wait_for_timeout(300)
    ok(pg.locator('#btnReceberOrdem').count() == 0 and 'btn-primary' in pg.get_attribute('#btnAbrirDetalhe', 'class') and pg.locator('#ocAtraso').count() == 0,
       'ordem atendida nao oferece receber nem avisa atraso')
    pg.evaluate("abrirPreview(2)"); pg.wait_for_timeout(300)
    clic('#btnReceberOrdem'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
    ok(pg.url.endswith(DOCA + '?receber=1'), '"Receber mercadorias" leva a Conferencia de Entrada, ja no recebimento')

    print('\n[3] A ordem de compra e link')
    ir(DOCA)
    linha('1190')
    ok(pg.get_attribute('#drawerCorpo a.painel-link', 'href').endswith(OC + '?busca=11'), 'na Conferencia de Entrada, a nota 1190 aponta para a ordem 11')
    destino, faixa, n = seguir('#drawerCorpo a.painel-link')
    ok(destino == OC and n >= 1 and pg.evaluate("Array.from(document.querySelectorAll('.main tbody tr')).some(r => r.innerText.includes('Tecidos Ceará'))"),
       'e o link cai em Ordens de Compra com a ordem 11, da Tecidos Ceara, na lista')
    ir(DOCA)
    linha('9001')
    ok('sem ordem vinculada' in painel() and 'null' not in painel(), 'nota que veio de devolucao diz "sem ordem vinculada" (antes dizia "nº null")')
    ir(NOTAS)
    linha('4471')
    ok(pg.get_attribute('#drawerCorpo a.painel-link', 'href').endswith(OC + '?busca=2'), 'na Entrada de Notas, a nota 4471 aponta para a ordem 2')
    ir(ENDER)
    pg.evaluate("document.querySelector('.main tbody tr td:nth-child(2)').click()"); pg.wait_for_timeout(400)
    ok(pg.locator('#drawerCorpo a.painel-link[href*="entrada-notas.html?busca="]').count() >= 1, 'no Enderecamento, a nota de origem do saldo e link para a Entrada de Notas')

    print('\n[4] Controle de Estoques')
    ir(CE)
    esperado = pg.evaluate("""(() => { const l = PRODUTOS.filter(existeNoDeposito);
        return [fmtMoeda(l.reduce((s, p) => s + Math.max(0, saldoDe(p)) * p.custoMedio, 0)), String(l.filter(abaixoDoMinimo).length), String(l.filter(p => aEnderecarDe(p) > 0).length), String(l.filter(p => bloqueadoDe(p) > 0).length)]; })()""")
    na_tela = [pg.inner_text('#' + i) for i in ['kpiValorEstoque', 'kpiAbaixoMinimo', 'kpiAEnderecar', 'kpiBloqueado']]
    ok(na_tela == esperado and na_tela[1:] == ['6', '2', '2'], 'os quatro indicadores batem com os saldos da lista: %s' % na_tela)
    clic('#cardAbaixoMinimo'); pg.wait_for_timeout(300)
    ok(pg.evaluate(LINHAS) == 6 and pg.get_attribute('#filtroSaldo', 'data-value') == 'abaixo_minimo', 'clicar no quadro "Abaixo do minimo" filtra a lista nos 6')
    escolher_dep = "(() => { document.querySelector('#filtroDeposito .dropdown-select-item[data-value=\"4\"]').click(); })()"
    if pg.locator('#filtroDeposito').count():
        pg.evaluate(escolher_dep); pg.wait_for_timeout(300)
        ok(pg.inner_text('#kpiValorEstoqueSub').startswith('3 produto'), 'e os indicadores acompanham o deposito escolhido: %s' % pg.inner_text('#kpiValorEstoqueSub'))
    ir(CE)
    clic('#linkOQueComprar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
    ok(pg.url.endswith(NEC), '"ver o que comprar" leva a Necessidades de Compra')
    for acao, destino in [('compra', NEC), ('giro', 'pagina-estoque-giro-estoque.html'), ('bloqueados', 'pagina-estoque-itens-bloqueados.html'), ('acerto', 'pagina-estoque-acerto.html'), ('transferencia', 'pagina-estoque-transferencia.html')]:
        ir(CE)
        pg.evaluate("(a) => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); document.querySelector('#menuMaisAcoes [data-acao=\"' + a + '\"]').click(); }", acao)
        pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
        ok(pg.url.endswith(destino), '"Mais ações" do Controle de Estoques leva a %s' % destino)
    ir(PROD, '?produto=15')
    clic('#btnVerCompra'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok(pg.url.endswith(NEC + '?busca=MON-27I-015') and pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => t.getAttribute('data-sku'))") == ['MON-27I-015'],
       'da pagina do produto, "Compra" abre Necessidades de Compra no proprio produto')
    ir(PROD, '?produto=15')
    clic('#btnVerGiro'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok('pagina-estoque-giro-estoque.html?busca=MON-27I-015' in pg.url and pg.evaluate(LINHAS) == 1, 'e "Giro" abre o Giro de Estoque no proprio produto')

    print('\n[5] Reposicao')
    ir(REPO)
    ok('A repor' in pg.inner_text('.aba-sit[data-aba="repor"]') and 'Necessidade Reposição' not in pg.inner_text('.main'), 'a aba passou a se chamar "A repor"')
    linha('Camiseta Desk Brands · M', 1)
    ok(pg.locator('#linkComprar').count() == 1 and pg.evaluate("(() => { const e = document.getElementById('linkComprar'); return !!e && e.offsetParent !== null; })()"),
       'sem saldo fora da base, o painel traz o link para Necessidades de Compra')
    clic('#linkComprar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok(pg.url.endswith(NEC + '?busca=CAM-DKB-012') and pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => t.getAttribute('data-sku'))") == ['CAM-DKB-012'],
       'e o link abre a compra ja no produto que falta')

    print('\n[6] Vendas e Logistica')
    ir(PED)
    linha('Móveis Bom Preço')
    links = pg.evaluate("Array.from(document.querySelectorAll('#pedidoLinks a')).map(a => a.getAttribute('href').split('/').pop().split('?')[0])")
    # Desde o retorno do usuario (10/out): o painel mostra a etapa em que o pedido esta e so da link
    # para a etapa que ele ja alcancou, levando a ficha DAQUELE pedido. teste_retorno.py cobre cada situacao.
    ok(links == ['pagina-logistica-separacao-detalhe.html', 'pagina-financas-contas-receber.html', 'pagina-cadastros-clientes.html'],
       'o painel de um pedido em separacao leva a ficha da Separacao, a Contas a Receber e ao cadastro do cliente: %s' % links)
    pg.evaluate("document.querySelector('#pedidoLinks a[href*=\"separacao-detalhe\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok('pagina-logistica-separacao-detalhe.html?id=6&de=pedido' in pg.url and pg.evaluate("PEDIDO.cliente") == 'Móveis Bom Preço Ltda', 'o link da Separacao abre a ficha do pedido do cliente')
    ir(SEP)
    linha('Móveis Bom Preço')
    destino, faixa, n = seguir('#drawerCorpo a.painel-link[href*="pedidos.html"]')
    ok(destino == PED and n >= 1 and 'Lista filtrada' in faixa, 'e o painel da Separacao leva de volta aos pedidos do cliente')
    ir(CONF)
    linha('Pedro Henrique')
    hrefs = pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo a.painel-link')).map(a => a.getAttribute('href').split('/').pop().split('?')[0])")
    ok(hrefs == [PED], 'o painel da Conferencia de Saida leva ao pedido, e nao de volta a Separacao: %s' % hrefs)
    ir(EXP)
    pg.evaluate("document.querySelector('.main tbody tr td:nth-child(2)').click()"); pg.wait_for_timeout(400)
    ok(pg.locator('#drawerCorpo .drawer-item-nome a.painel-link[href*="pedidos.html?busca="]').count() >= 1, 'no romaneio, cada pedido da carga e link para Pedidos de Venda')
    ir(DEV)
    linha('DV-0012', 1)
    ok(pg.get_attribute('#drawerCorpo a.painel-link[href*="rastreamento"]', 'href').endswith('?busca=PV-4862'), 'a devolucao aponta para o pedido de origem, no Rastreamento')
    destino, faixa, n = seguir('#drawerCorpo a.painel-link[href*="entrada-notas"]')
    ok(destino == NOTAS and n >= 1 and 'Construtora Veredas' in faixa, 'e para a nota de entrada que ela gerou: o caminho de volta que nao existia')

    print('\n[7] Os defeitos que a varredura achou')
    ir(DOCA)
    pg.evaluate("document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]').click()"); pg.wait_for_timeout(300)
    trocadas = []
    for numero in pg.evaluate("NOTAS.map(n => String(n.numero))"):
        linha(numero)
        tit = pg.inner_text('#drawerTitulo') if pg.locator('#eventDrawer.open').count() else ''
        if ('Nota ' + numero + ' ') not in tit + ' ':
            trocadas.append('%s abriu "%s"' % (numero, tit))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(160)
    ok(not trocadas and pg.evaluate("new Set(NOTAS.map(n => n.id)).size === NOTAS.length"), 'cada uma das notas da Conferencia de Entrada abre o proprio painel: %s' % trocadas[:3])
    ir(PEDD)
    # 12/out: "Acompanhar no galpao" saiu do menu e virou o quadro de acompanhamento da pagina
    # (teste_venda_melhorias.py). O defeito guardado aqui e o mesmo: o link nunca sai com "undefined".
    pg.evaluate("(() => { PEDIDO.numero = 5; PEDIDO.situacao = 'separacao'; aplicarSituacao(); })()"); pg.wait_for_timeout(200)
    pg.evaluate("document.querySelector('#trilhaPassos a.trilha-passo').click()")
    pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
    ok('undefined' not in pg.url and re.search(r'separacao-detalhe\.html\?id=5&de=pedido$', pg.url) is not None, 'o Pedido manda o numero dele para a Separacao: %s' % pg.url.split('/')[-1])

    print('\n[8] O Inicio leva a algum lugar, e nao contradiz o estoque')
    DASH, BOAS = 'pagina-dashboard-kpis.html', 'pagina-inicio-boas-vindas.html'
    ir(DASH)
    quadros = pg.evaluate("Array.from(document.querySelectorAll('.main .card')).map(c => [(c.querySelector('.kpi-label, .card-title') || {}).textContent || '', c.getAttribute('data-href') || ''])")
    sem_destino = [q[0] for q in quadros if not q[1]]
    quebrados = [q for q in quadros if q[1] and not _os.path.exists(localiza.onde(localiza.nome(q[1]).split('?')[0]))]
    # "Vendas por Loja" deixou de ser link em 10/out: clicar numa loja filtra o painel (teste_retorno.py).
    ok(len(quadros) == 15 and sem_destino == ['Vendas por Loja'] and not quebrados, '14 quadros do Dashboard levam a uma tela que existe, e "Vendas por Loja" filtra o painel: sem destino %s' % sem_destino[:3])
    pg.evaluate("Array.from(document.querySelectorAll('.main .card')).filter(c => /Alertas de Estoque/.test(c.textContent))[0].querySelector('.stock-name').click()")
    pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
    ok(pg.url.endswith(NEC), 'clicar no quadro Alertas de Estoque abre Necessidades de Compra')
    ir(DASH)
    url = pg.url
    pg.evaluate("Array.from(document.querySelectorAll('.main .card')).filter(c => /Alertas de Estoque/.test(c.textContent))[0].querySelector('.qty-filter button:not(.active)').click()")
    pg.wait_for_timeout(350)
    ok(pg.url == url, 'e o botao de dentro do quadro continua sendo so um botao: nao navega')
    alertas = pg.evaluate("Array.from(document.querySelectorAll('.stock-item')).map(i => [i.querySelector('.stock-name').textContent, parseInt(i.querySelector('.stock-qty').textContent, 10), parseInt(i.querySelector('.stock-min').textContent.replace(/[^0-9]/g, ' ').trim(), 10)])")
    valor = pg.evaluate("document.querySelector('.stock-total b').textContent")
    vendidos = pg.evaluate("Array.from(document.querySelectorAll('.rank-name')).map(e => e.textContent)")
    ir(CE)
    do_estoque = pg.evaluate("PRODUTOS.filter(abaixoDoMinimo).map(p => [p.nome, disponivelDe(p) + aEnderecarDe(p), p.minimo])")
    ok(len(alertas) >= 5 and all(a in do_estoque for a in alertas) and valor == pg.inner_text('#kpiValorEstoque'),
       'todo Alerta de Estoque do Dashboard esta abaixo do minimo no Controle de Estoques, com o mesmo valor em estoque (%s, %d alertas)' % (valor, len(alertas)))
    ir('pagina-estoque-giro-estoque.html')
    encalhados = pg.evaluate("PRODUTOS.filter(p => classeGiro(giroDe(p, PARAM.giroJanelaDias, 0), PARAM.giroEncalheAte, PARAM.giroBaixoAte) === 'encalhe').map(p => p.nome)")
    ok(not [v for v in vendidos if v in encalhados] and len(encalhados) >= 1, 'nenhum produto de "Mais Vendidos" e encalhe no Giro de Estoque (antes a Luminaria era as duas coisas)')
    ir(BOAS)
    atalhos = pg.evaluate("Array.from(document.querySelectorAll('.shortcut-tile')).map(t => [t.textContent.trim(), t.getAttribute('data-href') || ''])")
    ok(len(atalhos) == 10 and all(a[1] and _os.path.exists(localiza.onde(localiza.nome(a[1]).split('?')[0])) for a in atalhos), 'os 10 atalhos rapidos de Boas-vindas tem destino: %s' % [a[0] for a in atalhos])
    clic('.shortcut-tile[data-href*="pedidos-detalhe"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
    ok(pg.url.endswith('pagina-vendas-pedidos-detalhe.html?novo=1'), '"Novo Pedido" abre o pedido novo')
    ir(BOAS)
    filas = pg.evaluate("Array.from(document.querySelectorAll('#quadroDoDia a.dia-fila')).map(a => a.getAttribute('href'))")
    ok(len(filas) == 9 and all(_os.path.exists(localiza.onde(localiza.nome(f))) for f in filas) and pg.get_attribute('#linkAgenda', 'href').endswith('pagina-inicio-agenda.html'),
       '"Pendências do Dia" lista as 9 filas de trabalho, cada uma com a tela dela, e a agenda tem o link para a Agenda')

    print('\n[9] O cadastro do cliente mostra o que ele comprou e o que deve')
    CLI = 'pagina-cadastros-clientes.html'
    ir(PED)
    de_la = pg.evaluate("PEDIDOS.map(p => [p.numero, p.cliente, p.total, p.situacao, !!p.pago])")
    ir(CLI)
    ok(pg.evaluate("PEDIDOS_DO_CADASTRO.map(p => [p.numero, p.cliente, p.total, p.situacao, p.pago])") == de_la and len(de_la) == 16,
       'o espelho de pedidos do cadastro e igual a lista de Pedidos de Venda: 16 pedidos')
    esperado = pg.evaluate("(() => { const m = movimentoDoCliente('Móveis Bom Preço Ltda'); return [m.pedidos, dinheiro(m.comprado), m.titulos]; })()")
    pg.evaluate("abrirPreviewCliente(CLIENTES.find(c => c.nome === 'Móveis Bom Preço Ltda').id)"); pg.wait_for_timeout(400)
    ok(esperado[0] >= 1 and pg.inner_text('#pvPedidos') == str(esperado[0]) and pg.inner_text('#pvComprado') == esperado[1] and 'nº' in pg.inner_text('#pvUltimo'),
       'o painel de Moveis Bom Preco traz os pedidos, o total comprado e o ultimo pedido: %s pedido(s), %s' % (esperado[0], esperado[1]))
    hrefs = pg.evaluate("Array.from(document.querySelectorAll('#previewLinks a')).map(a => a.getAttribute('href').split('/').pop().split('?')[0])")
    ok(hrefs == [PED, 'pagina-financas-contas-receber.html', 'pagina-vendas-crm.html'], 'e leva aos pedidos, as contas a receber e ao CRM')
    destino, faixa, n = seguir('#previewLinks a[href*="pedidos.html"]')
    ok(destino == PED and n == esperado[0] and 'Lista filtrada' in faixa, 'o link dos pedidos cai em Pedidos de Venda com os %d pedido(s) do cliente' % n)
    ir(CLI)
    # Cliente sem pedido no exemplo: o painel diz isso, em vez de mostrar zeros. Se todo cliente tiver pedido, um e inventado so para o teste.
    pg.evaluate("(() => { if (!CLIENTES.some(c => movimentoDoCliente(c.nome).pedidos === 0)) CLIENTES.push(Object.assign({}, CLIENTES[0], { id: 9999, nome: 'Cliente Sem Pedido' })); abrirPreviewCliente(CLIENTES.filter(c => movimentoDoCliente(c.nome).pedidos === 0)[0].id); })()")
    pg.wait_for_timeout(350)
    ok(pg.inner_text('#pvPedidos') == 'nenhum neste exemplo' and pg.locator('#pvComprado').count() == 0, 'cliente sem pedido no exemplo diz isso, em vez de mostrar zeros')
    ok(not erros, 'sem erro de JS em nenhuma das telas: %s' % erros[:2])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
