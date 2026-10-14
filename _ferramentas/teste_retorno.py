# -*- coding: utf-8 -*-
# O retorno do usuario sobre a primeira leva de melhorias (10/out/2026).
#
# Ele testou a leva e devolveu uma lista. Esta suite guarda cada ponto, para nenhum voltar:
#   [1] o popover de periodo fecha quando outro filtro abre, em TODA tela que tem o popover
#       (o conserto tinha ficado em metade delas);
#   [2] Ordens de Compra e Pedidos de Venda abrem do nº 1 para o maior;
#   [3] "incluir" abre em branco: a ordem de compra e os cinco cadastros;
#   [4] Necessidades de Compra: digitar a quantidade marca o produto, a tela abre em "A comprar",
#       e a ordem gerada de um produto so tira o produto da lista;
#   [5] Contas a Receber: pedido cancelado nao deve, e o painel do cliente diz o que ela diz;
#   [6] Separacao: concluir volta para a fila, devolver para a fila funciona, e a etapa que ja
#       passou nao aparece como link nas etapas seguintes (so no Pedido de Venda);
#   [7] Metas e Performance e uma pagina so;
#   [8] Inicio: os botoes 5/10/15/20 mostram mais itens, clicar na loja filtra o painel inteiro,
#       e "Pendencias do Dia" e um quadro proprio, com os numeros de cada fila; os quadros nao crescem.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

OC = 'pagina-estoque-ordens-compra.html'
OCD = 'pagina-estoque-ordens-compra-detalhe.html'
NEC = 'pagina-estoque-necessidades-compra.html'
PED = 'pagina-vendas-pedidos.html'
MARCA_POP = '  // ===== O POPOVER DE PERIODO FECHA QUANDO OUTRO MENU ABRE (10/out/2026) ====='
SO = (sys.argv[1:] or [''])[0]      # python teste_retorno.py 4  -> roda so a secao 4

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


TODAS = localiza.nomes()
fontes = {n: open(localiza.onde(n), encoding='utf-8').read() for n in TODAS}

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(380)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def confirmar():
        """Confirma o modal aberto, com a senha quando a tela pede. Serve tambem para fechar aviso."""
        pg.wait_for_timeout(200)
        if pg.locator('#avisoModal.open').count():
            clic('#btnAvisoOk'); pg.wait_for_timeout(300)
        if pg.locator('#confirmModal.open').count():
            pg.evaluate("() => { const c = document.querySelector('#confirmModal input[type=checkbox]'); if (c && c.offsetParent !== null && !c.checked) c.click(); }")
            if pg.evaluate("(() => { const e = document.getElementById('campoSenhaModal'); return !!e && e.offsetParent !== null; })()"):
                pg.fill('#inputSenhaModal', 'senha-de-teste')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)

    def fechar_aviso():
        confirmar()

    def digitar(seletor, valor):
        """Digita de verdade (teclado), para o campo disparar o que dispara com uma pessoa."""
        pg.click(seletor); pg.keyboard.press('Control+A'); pg.keyboard.type(valor); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)

    if secao(1, 'O popover de periodo fecha quando outro filtro abre'):
        com_pop = [n for n in TODAS if 'class="periodo-menu' in fontes[n]]
        sem = [n for n in com_pop if MARCA_POP not in fontes[n]]
        ok(len(com_pop) >= 11 and not sem, 'toda tela com o popover de periodo tem o bloco que o fecha (%d telas): %s' % (len(com_pop), sem))
        # Confere contra CADA dropdown visivel da tela, e nao so o primeiro: o "Mais acoes" do topo
        # fecha o periodo por outro caminho, e era o filtro de deposito, ao lado, que ficava por cima.
        presos, sobrepostos, pares = [], [], 0
        for tela in com_pop:
            ir(tela)
            r = pg.evaluate("""(() => {
                const wrap = document.querySelector('.main .periodo-wrap'); if (!wrap) return null;
                const menu = wrap.querySelector('.periodo-menu'), botao = wrap.querySelector('button') || wrap.firstElementChild;
                const outros = Array.from(document.querySelectorAll('.main .dropdown-select')).filter(d => !wrap.contains(d) && d.offsetParent && d.querySelector('.dropdown-select-btn') && !d.querySelector('.dropdown-select-btn').disabled);
                const presos = [], sobrepostos = []; let abriu = true;
                outros.forEach(outro => {
                  const nome = outro.id || outro.className, m = outro.querySelector('.dropdown-select-menu');
                  if (!menu.classList.contains('open')) botao.click();
                  if (!menu.classList.contains('open')) abriu = false;
                  outro.querySelector('.dropdown-select-btn').click();
                  if (menu.classList.contains('open') || !m.classList.contains('open')) presos.push(nome);
                  botao.click();
                  if (!menu.classList.contains('open') || m.classList.contains('open')) sobrepostos.push(nome);
                  document.body.click();
                });
                return { abriu: abriu, outros: outros.length, presos: presos, sobrepostos: sobrepostos }; })()""")
            if not r or not r.get('abriu'):
                presos.append(tela + ': o popover nao abriu')
                continue
            pares += r['outros']
            presos += [tela.replace('pagina-', '') + ' x ' + x for x in r['presos']]
            sobrepostos += [tela.replace('pagina-', '') + ' x ' + x for x in r['sobrepostos']]
        ok(pares >= 20 and not presos, 'abrir qualquer outro filtro fecha o periodo (%d pares de filtros conferidos): %s' % (pares, presos[:4]))
        ok(not sobrepostos, 'e abrir o periodo fecha o outro filtro, em todas: %s' % sobrepostos[:4])

    if secao(2, 'As listas numeradas abrem do nº 1 para o maior'):
        for tela, rotulo in [(OC, 'Ordens de Compra'), (PED, 'Pedidos de Venda')]:
            ir(tela)
            pg.evaluate("(() => { const s = document.querySelector('.periodo-op[data-periodo=\"todos\"]'); if (s && !s.classList.contains('active')) s.click(); })()")
            pg.wait_for_timeout(250)
            nums = pg.evaluate("Array.from(document.querySelectorAll('.main tbody tr')).map(tr => { const m = tr.innerText.match(/\\d+/); return m ? Number(m[0]) : null; })")
            ok(len(nums) >= 5 and nums == sorted(nums) and nums[0] == 1, '%s: a primeira linha e o nº 1 e a lista sobe: %s' % (rotulo, nums[:6]))

    if secao(3, '"Incluir" abre em branco'):
        ir(OC); clic('#btnNovaOC'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        r = pg.evaluate("""(() => { const campos = Array.from(document.querySelectorAll('.main input[type=text], .main textarea')).filter(c => c.offsetParent && !c.readOnly);
            return { url: location.search, h1: document.getElementById('tituloOC').textContent, numero: document.getElementById('inputNumero').value,
              cheios: campos.filter(c => c.value.trim() && !/^0,00$/.test(c.value.trim()) && c.id !== 'inputDataCompra').map(c => c.id || c.getAttribute('data-campo')),
              forn: document.querySelector('#inputFornecedor .dropdown-select-label').textContent, valorForn: document.getElementById('inputFornecedor').getAttribute('data-value'),
              itens: document.querySelectorAll('#corpoItens tr, .itens-table tbody tr').length, vazio: getComputedStyle(document.getElementById('itensVazio')).display,
              data: document.getElementById('inputDataCompra').value, selo: document.getElementById('badgeSituacao').textContent.trim(),
              menu: getComputedStyle(document.getElementById('menuMaisAcoes')).display }; })()""")
        ok(r['url'] == '?novo=1' and r['h1'] == 'Nova ordem de compra' and r['numero'] == '', 'Ordem de Compra: o botao abre "Nova ordem de compra", sem numero')
        ok(r['cheios'] == [] and r['valorForn'] == '' and r['forn'] == 'Selecione o fornecedor' and r['vazio'] != 'none',
           'sem fornecedor, sem item e sem campo preenchido: %s' % r['cheios'])
        ok(re.match(r'^\d\d/\d\d/\d{4}$', r['data']) is not None and 'aberto' in r['selo'].lower() and r['menu'] == 'none', 'com a data de hoje, em aberto, e sem as acoes de ordem que ja existe')
        clic('#inputFornecedor .dropdown-select-btn'); pg.wait_for_timeout(150)
        clic('#inputFornecedor .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.getElementById('fDocNumero').textContent") not in ('', '—') and not erros, 'escolher o fornecedor preenche os dados dele, sem erro: %s' % erros[:2])
        ir(OCD)
        ok(pg.evaluate("document.getElementById('tituloOC').textContent") == 'Ordem de Compra nº 2' and pg.evaluate("document.querySelectorAll('.main input[data-campo=\"nome\"]').length") == 2,
           'e abrir uma ordem que existe continua trazendo a ordem')
        for tela, titulo in [('pagina-cadastros-clientes-detalhe.html', 'Novo cliente'), ('pagina-cadastros-fornecedores-detalhe.html', 'Novo fornecedor'),
                             ('pagina-cadastros-lojas-desk-detalhe.html', 'Nova loja'), ('pagina-cadastros-produtos-detalhe.html', 'Novo produto'),
                             ('pagina-cadastros-vendedores-detalhe.html', 'Novo vendedor')]:
            ir(tela, '?novo=1')
            r = pg.evaluate("""(() => { const campos = Array.from(document.querySelectorAll('.main input, .main textarea')).filter(c => c.offsetParent && !c.readOnly && !['checkbox', 'radio', 'file'].includes(c.type));
                return { h1: document.querySelector('.main h1').textContent.trim(), campos: campos.length, cheios: campos.filter(c => c.value.trim()).map(c => c.id || c.name || c.placeholder).slice(0, 4) }; })()""")
            ok(r['h1'] == titulo and r['campos'] >= 5 and r['cheios'] == [], '%s: abre "%s" com os %d campos em branco: %s' % (tela.replace('pagina-cadastros-', ''), r['h1'], r['campos'], r['cheios']))
            ir(tela)
            cheios = pg.evaluate("Array.from(document.querySelectorAll('.main input')).filter(c => !['checkbox', 'radio', 'file'].includes(c.type) && c.value.trim()).length")
            ok(cheios >= 1, '  e sem o ?novo=1 continua trazendo o cadastro (%d campos preenchidos)' % cheios)
        ok(not erros, 'nenhuma dessas paginas da erro ao abrir em branco: %s' % erros[:3])

    if secao(4, 'Necessidades de Compra: marcar ao digitar, e a ordem tira o produto da lista'):
        ir(NEC); pg.evaluate("localStorage.removeItem('deskOrdensGeradas')"); ir(NEC)
        aba = lambda: pg.evaluate("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')")
        skus = lambda: pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => tr.getAttribute('data-sku'))")
        a_comprar = skus()
        ok(aba() == 'comprar' and len(a_comprar) >= 3 and pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela .nc-qtd')).every(c => Number(c.value.replace(',', '.')) > 0)"),
           'a tela abre na aba "A comprar", so com o que tem quantidade a comprar: %s' % a_comprar)
        ir(NEC, '?busca=CAD-ERG-001')
        ok(aba() == 'todos' and skus() == ['CAD-ERG-001'], 'quem chega por link com busca ve "Todos", para achar o produto mesmo sem compra a fazer')
        ir(NEC)
        alvo = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).filter(tr => !/sem fornecedor/.test(tr.innerText))[0].getAttribute('data-sku')")
        ok(pg.evaluate("document.querySelectorAll('#corpoTabela .item-checkbox:checked').length") == 0, 'nada nasce marcado')
        digitar('#corpoTabela .nc-qtd[data-sku="%s"]' % alvo, '7')
        ok(pg.evaluate("(s) => document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"] .item-checkbox').checked", alvo) and pg.evaluate("document.getElementById('barraSelecao').offsetParent !== null"),
           'digitar a quantidade e dar Enter marca o produto e mostra a barra de selecao')
        digitar('#corpoTabela .nc-qtd[data-sku="%s"]' % alvo, '0')
        ok(pg.evaluate("(s) => { const l = document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"] .item-checkbox'); return !l || !l.checked; }", alvo), 'e zerar a quantidade desmarca')
        ir(NEC)
        antes = skus()
        pg.evaluate("(s) => document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"] td:nth-child(2)').click()", alvo); pg.wait_for_timeout(350)
        clic('#btnOrdemDoProduto'); pg.wait_for_timeout(350)
        clic('#btnConfirmarOrdem'); pg.wait_for_timeout(450)
        confirmar(); fechar_aviso()
        depois = skus()
        ok(alvo in antes and alvo not in depois and len(depois) == len(antes) - 1 and not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"),
           'gerar a ordem de UM produto pelo painel tira so ele da lista: %s -> %s' % (len(antes), len(depois)))
        pg.evaluate("document.querySelector('#abasSituacao .aba-sit[data-sit=\"todos\"]').click()"); pg.wait_for_timeout(300)
        nota = pg.evaluate("(s) => { const tr = document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"]'); const n = tr && tr.querySelector('.nc-nota'); return n ? n.textContent : ''; }", alvo)
        ok('já pedido: ordem nº' in nota, 'e em "Todos" a linha dele diz em que ordem ja foi pedido: "%s"' % nota)
        pg.evaluate("localStorage.removeItem('deskOrdensGeradas')")

    if secao(5, 'Quem deve o que: Contas a Receber e a dona do numero'):
        ir(PED)
        cancelados = pg.evaluate("PEDIDOS.filter(p => p.situacao === 'cancelado').map(p => p.numero)")
        ir('pagina-financas-contas-receber.html')
        abertos = pg.evaluate("TITULOS.filter(t => !t.cancelado && t.recebido < t.valor - 0.005).map(t => ({ cliente: cliDe(t.cliId).nome, doc: t.doc || 'Sem documento', saldo: Math.round((t.valor - t.recebido) * 100) / 100, pedido: t.pedido || 0 }))")
        devendo_cancelado = [a['doc'] for a in abertos if a['pedido'] in cancelados]
        ok(len(cancelados) >= 1 and not devendo_cancelado, 'pedido cancelado nao tem titulo em aberto (cancelados: %s): %s' % (cancelados, devendo_cancelado))
        ok(pg.evaluate("TITULOS.filter(t => t.pedido === 15).map(t => [cliDe(t.cliId).nome, t.cancelado])") == [['Marina Duarte', True]], 'o titulo do pedido nº 15, cancelado, esta cancelado')
        ir('pagina-financas-contas-receber.html', '?busca=Marina Duarte')
        docs = [' '.join(d.split()) + ' ' for d in pg.evaluate("Array.from(document.querySelectorAll('.main tbody tr')).map(tr => tr.innerText.toLowerCase())")]
        devendo = [d for d in docs if 'cancelad' not in d]
        ok(len(docs) == 2 and len(devendo) == 1 and 'pedido 1 ' in devendo[0] and '1.890,00' in devendo[0],
           'Marina Duarte em Contas a Receber: deve so o pedido nº 1, de R$ 1.890,00; o nº 15 aparece como cancelado: %s' % [d[:60] for d in docs])
        ir('pagina-cadastros-clientes.html')
        espelho = pg.evaluate("TITULOS_DO_CADASTRO")
        ok(espelho == [{'cliente': a['cliente'], 'doc': a['doc'], 'saldo': a['saldo']} for a in abertos], 'o espelho do cadastro de clientes e igual aos titulos em aberto de Contas a Receber (%d)' % len(espelho))
        diferentes = pg.evaluate("""((abertos) => CLIENTES.map(c => c.nome).filter(n => {
            const daqui = movimentoDoCliente(n).aReceber, dela = abertos.filter(a => a.cliente === n).reduce((s, a) => s + a.saldo, 0);
            return Math.abs(daqui - dela) > 0.005; }))""", abertos) if pg.evaluate("typeof CLIENTES !== 'undefined'") else ['sem CLIENTES']
        ok(diferentes == [], 'para todo cliente do cadastro, o painel diz o que Contas a Receber diz: %s' % diferentes)
        pg.evaluate("(() => { const b = document.querySelector('.main .search-wrap input'); b.value = 'Marina Duarte'; b.dispatchEvent(new Event('input', { bubbles: true })); })()"); pg.wait_for_timeout(300)
        pg.evaluate("Array.from(document.querySelectorAll('.main .card *')).filter(e => e.children.length === 0 && e.textContent.trim() === 'Marina Duarte')[0].click()"); pg.wait_for_timeout(400)
        ok(pg.evaluate("(document.getElementById('pvAReceber') || {}).textContent") == 'R$ 1.890,00 · 1 título' and '15' in pg.evaluate("(document.getElementById('pvUltimo') || {}).textContent || ''"),
           'o painel da Marina: ultimo pedido nº 15 (cancelado), e deve R$ 1.890,00 em 1 titulo: %s' % pg.evaluate("(document.getElementById('pvAReceber') || {}).textContent"))

    if secao(6, 'Separacao: concluir volta para a fila, devolver funciona, e etapa que passou nao volta'):
        SEP, FICHA = 'pagina-logistica-separacao.html', 'pagina-logistica-separacao-detalhe.html'
        CONF, CONFD, EXP = 'pagina-logistica-conferencia-saida.html', 'pagina-logistica-conferencia-saida-detalhe.html', 'pagina-logistica-expedicao.html'
        MARCA = '  // ===== O QUE A FICHA JA FEZ COM O PEDIDO (bloco compartilhado, 10/out/2026) ====='
        corte = lambda n: fontes[n][fontes[n].index(MARCA):fontes[n].index('  })();', fontes[n].index(MARCA))]
        ok(MARCA in fontes[SEP] and MARCA in fontes[FICHA] and corte(SEP) == corte(FICHA), 'a fila e a ficha carregam o mesmo bloco, letra por letra')
        sit = lambda n: pg.evaluate("(n) => { const p = FILA.filter(x => x.id === n)[0]; return [p.situacao, p.operador]; }", n)
        ir(SEP); pg.evaluate("localStorage.removeItem('deskSeparacao')"); ir(SEP)
        ok(sit(22) == ['fila', None] and sit(6)[0] == 'separando', 'ponto de partida: o pedido 22 esta na fila e o 6 em separacao')
        ir(FICHA, '?id=22')
        pg.fill('#campoBipar', 'CAD-FIX-110'); pg.press('#campoBipar', 'Enter'); pg.wait_for_timeout(250)
        clic('#btnConcluir'); pg.wait_for_timeout(300); confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        faixa = pg.evaluate("(document.getElementById('faixaDaFicha') || { textContent: '' }).textContent")
        ok(SEP in pg.url and 'feita=22' in pg.url, 'concluir a separacao volta para a fila do galpao: %s' % pg.url.split('/')[-1])
        ok('Separação do pedido #22 concluída' in faixa and 'Conferência de Saída' in faixa and 'Tratamento de Perdas' not in faixa, 'e a fila diz o que aconteceu com o pedido: %s' % faixa[:90])
        ok(sit(22)[0] == 'separado', 'na fila, o pedido 22 aparece como separado')
        ir(FICHA, '?id=22')
        ok(pg.evaluate("document.getElementById('btnConcluir').disabled") and pg.evaluate("COLETA.every(i => i.separado === i.qtd)"), 'reabrindo a ficha, ela esta concluida e com o que foi coletado')
        clic('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        clic('#menuMaisAcoes .dropdown-select-item[data-acao="devolver"]'); pg.wait_for_timeout(300)
        ok('desfaz a conclusão' in pg.evaluate("document.getElementById('confirmModalTexto').textContent"), '"Devolver para a fila" numa separacao concluida pede confirmacao e diz que desfaz a conclusao')
        confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        faixa = pg.evaluate("(document.getElementById('faixaDaFicha') || { textContent: '' }).textContent")
        ok('devolvido=22' in pg.url and sit(22) == ['fila', None] and 'voltou para a fila' in faixa, 'confirmando, o pedido 22 volta para a fila, sem separador: %s' % sit(22))
        ok(any(l.get('chave') == 'separacaoReabre' for l in pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")), 'e a reabertura fica no registro de atividades')
        ir(FICHA, '?id=6')
        clic('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        clic('#menuMaisAcoes .dropdown-select-item[data-acao="devolver"]'); pg.wait_for_timeout(300); confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok('devolvido=6' in pg.url and sit(6) == ['fila', None], 'devolver um pedido em andamento tambem volta para a fila de verdade: %s' % sit(6))
        pg.evaluate("localStorage.removeItem('deskSeparacao')")

        def painel_da_linha(tela, texto):
            ir(tela)
            pg.evaluate("(() => { const s = document.querySelector('.periodo-op[data-periodo=\"todos\"]'); if (s && !s.classList.contains('active')) s.click(); const i = document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]'); if (i) i.click(); })()")
            pg.wait_for_timeout(300)
            pg.evaluate("(t) => { const tr = Array.from(document.querySelectorAll('.main tbody tr')).filter(r => r.innerText.includes(t))[0]; (tr.children[1] || tr).click(); }", texto)
            pg.wait_for_timeout(400)
            return pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo a')).map(a => a.getAttribute('href'))")
        hrefs = painel_da_linha(CONF, 'Pedro Henrique')
        ok(len(hrefs) >= 1 and not [h for h in hrefs if 'pagina-logistica-separacao' in h], 'o painel da Conferencia de Saida nao leva de volta a Separacao: %s' % [h.split('/')[-1][:40] for h in hrefs])
        ir(EXP)
        pg.evaluate("document.querySelector('.main tbody tr td:nth-child(2)').click()"); pg.wait_for_timeout(400)
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo a')).map(a => a.getAttribute('href'))")
        ok(not [h for h in hrefs if 'pagina-logistica-separacao' in h or 'pagina-logistica-conferencia' in h], 'nem o da Expedicao leva a Conferencia ou a Separacao')

        ir(FICHA); na_sep = pg.evaluate("FILA.map(p => p.id)")
        ir(CONFD); na_conf = pg.evaluate("FILA.map(p => p.id)")
        ir(PED)
        numeros = pg.evaluate("PEDIDOS.map(p => p.numero)")
        ok(pg.evaluate("NO_GALPAO") == {'separacao': sorted(n for n in numeros if n in na_sep), 'conferencia': sorted(n for n in numeros if n in na_conf)},
           'o Pedido de Venda sabe em que fichas do galpao cada pedido existe: %s' % pg.evaluate("NO_GALPAO"))

        def etapas(numero):
            pg.evaluate("(n) => abrirPreview(PEDIDOS.filter(p => p.numero === n)[0].id)", numero); pg.wait_for_timeout(300)
            return pg.evaluate("Array.from(document.querySelectorAll('#pedidoLinks > *')).slice(0, 3).map(e => [e.textContent, e.getAttribute('href') || ''])")
        e1, e5, e7, e12, e15 = etapas(1), etapas(5), etapas(7), etapas(12), etapas(15)
        ok(all('ainda não chegou' in x[0] and not x[1] for x in e1), 'pedido em aberto (nº 1): as tres etapas do galpao dizem "ainda nao chegou", sem link')
        ok('Separação · em andamento' == e5[0][0] and e5[0][1].endswith('pagina-logistica-separacao-detalhe.html?id=5&de=pedido') and 'ainda não chegou' in e5[1][0],
           'pedido em separacao (nº 5): a Separacao esta em andamento e leva para a ficha DELE: %s' % e5[0][1].split('/')[-1])
        ok(e7[0][0] == 'Separação · concluída' and e7[1][0] == 'Conferência de Saída · em andamento' and e7[1][1].endswith('pagina-logistica-conferencia-saida-detalhe.html?id=7&de=pedido') and 'ainda não chegou' in e7[2][0],
           'pedido na conferencia (nº 7): Separacao concluida, Conferencia em andamento, Expedicao ainda nao')
        ok([x[0].split(' · ')[1] for x in e12] == ['concluída'] * 3, 'pedido entregue (nº 12): as tres etapas concluidas')
        ok('cancelado' in e15[0][0].lower() and not e15[0][1], 'pedido cancelado (nº 15): nao passa pelo galpao')
        for tela, rotulo in [(FICHA, 'Separacao'), (CONFD, 'Conferencia de Saida')]:
            ir(tela, '?id=7&de=pedido')
            volta = pg.evaluate("(() => { const b = document.getElementById('btnVoltarPedido'); return b ? [b.textContent, b.getAttribute('href'), b.offsetParent !== null] : null; })()")
            ok(volta is not None and volta[0] == 'Voltar para o pedido de venda' and 'pagina-vendas-pedidos.html?busca=Pedro' in volta[1] and volta[2] and pg.evaluate("PEDIDO.numero") == 7,
               'a ficha da %s abre no pedido 7 e tem "Voltar para o pedido de venda"' % rotulo)
            ir(tela, '?id=7')
            ok(pg.evaluate("!document.getElementById('btnVoltarPedido')"), '  e quem chega pela fila do galpao nao ve esse botao')

    if secao(7, 'Metas e Performance e uma pagina so'):
        # O detalhe (colunas, indicadores, painel) esta em teste_metas.py; aqui fica o que o usuario pediu.
        ok('pagina-vendas-performance-vendas.html' not in TODAS and not [n for n in TODAS if 'pagina-vendas-performance-vendas' in fontes[n]],
           'a tela de Performance de Vendas saiu, e nenhuma tela aponta para ela')
        ir('pagina-vendas-metas.html')
        ok(pg.locator('#visaoModulo').count() == 0 and pg.evaluate("document.querySelectorAll('.estoque-table th').length") == 8 and pg.locator('.mp-kpis .kpi-card').count() == 6,
           'uma lista so, sem botao de trocar de visao: 8 colunas e 6 indicadores')

    if secao(8, 'Inicio: os botoes mostram mais itens, a loja filtra o painel, e o dia tem quadro proprio'):
        DASH, BV = 'pagina-dashboard-kpis.html', 'pagina-inicio-boas-vindas.html'
        ir('pagina-estoque-giro-estoque.html')
        do_giro = pg.evaluate("PRODUTOS.map(p => [p.nome, giroDe(p, 30, 0).vendas]).filter(x => x[1] > 0).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))")
        ir(NEC)
        pg.evaluate("localStorage.removeItem('deskOrdensGeradas'); localStorage.removeItem('deskMinMax')"); ir(NEC)
        da_compra = pg.evaluate("PRODUTOS.map(p => retrato(p)).filter(r => r.abaixoMin || r.emFalta).map(r => [r.p.nome, r.vendavel, r.min]).sort((a, b) => (a[1] - a[2]) - (b[1] - b[2]) || a[0].localeCompare(b[0]))")
        ir('pagina-estoque-controle-estoques.html')
        valor_estoque = pg.evaluate("document.getElementById('kpiValorEstoque').textContent")
        ir(DASH)
        mais = pg.evaluate("MAIS_VENDIDOS.map(x => [x.nome, x.un])")
        ok(sorted(mais) == sorted(do_giro) and len(do_giro) >= 8 and [m[1] for m in mais] == sorted([m[1] for m in mais], reverse=True),
           '"Mais Vendidos" e o que o Giro de Estoque vendeu nos ultimos 30 dias, do que mais vendeu para o que menos (%d produtos)' % len(do_giro))
        ok(pg.evaluate("ALERTAS_ESTOQUE.map(x => [x.nome, x.vendavel, x.minimo])") == da_compra and len(da_compra) >= 5, '"Alertas de Estoque" e o que Necessidades de Compra tem abaixo do minimo (%d)' % len(da_compra))
        ok(pg.evaluate("document.getElementById('estoqueTotal').textContent") == valor_estoque, 'o valor em estoque das tres lojas soma o do Controle de Estoques: %s' % valor_estoque)
        conta = lambda: pg.evaluate("[document.querySelectorAll('#listaMaisVendidos .rank-item').length, document.querySelectorAll('#listaAlertas .stock-item').length]")
        # Segundo retorno (12/out): o quadro nao cresce. A lista fica na altura dos 5 itens e rola por dentro.
        nota = lambda i: pg.evaluate("(i) => (document.getElementById(i) || { textContent: '' }).textContent", i)
        quadros = lambda: pg.evaluate("Array.from(document.querySelectorAll('.row-bottom > .card')).map(c => Math.round(c.getBoundingClientRect().height))")
        rola = lambda: pg.evaluate("['listaMaisVendidos', 'listaAlertas'].map(id => { const l = document.getElementById(id); return l.scrollHeight - l.clientHeight; })")
        pg.wait_for_timeout(300)
        abertura = quadros()
        ok(conta() == [5, 5] and len(set(abertura)) == 1 and all(r <= 1 for r in rola()), 'as duas listas abrem com 5 itens, sem rolagem, e os tres quadros da linha tem a mesma altura: %s' % abertura)
        pg.evaluate("document.querySelectorAll('.qty-filter[data-lista=vendidos] .pill-btn-sm')[1].click()"); pg.wait_for_timeout(200)
        ok(conta()[0] == 10 and nota('notaMaisVendidos') == '', 'o botao 10 de "Mais Vendidos" mostra 10 produtos')
        ok(quadros() == abertura and rola()[0] > 100 and pg.evaluate("getComputedStyle(document.getElementById('listaMaisVendidos')).overflowY") == 'auto',
           'e o quadro NAO cresce: os 10 rolam dentro da lista, e os tres quadros continuam na altura da abertura: %s' % quadros())
        # Terceiro retorno (12/out): a barra de rolagem nao aparece. A lista continua rolando.
        sem_barra = pg.evaluate("""(() => { const l = document.getElementById('listaMaisVendidos'); l.scrollTop = 80;
            return { barra: l.offsetWidth - l.clientWidth, estilo: getComputedStyle(l).scrollbarWidth, rolou: l.scrollTop }; })()""")
        ok(sem_barra['barra'] == 0 and sem_barra['estilo'] == 'none' and sem_barra['rolou'] == 80, 'a lista rola sem barra de rolagem a vista: %s' % sem_barra)
        pg.evaluate("document.querySelectorAll('.qty-filter[data-lista=vendidos] .pill-btn-sm')[3].click()"); pg.wait_for_timeout(200)
        pg.evaluate("document.querySelectorAll('.qty-filter[data-lista=alertas] .pill-btn-sm')[1].click()"); pg.wait_for_timeout(200)
        ok(conta() == [len(do_giro), len(da_compra)] and 'Mostrando os %d que há' % len(do_giro) in nota('notaMaisVendidos')
           and 'Mostrando os %d que há' % len(da_compra) in nota('notaAlertas'),
           'pedindo mais do que existe, a lista mostra todos e diz que sao so esses: %s' % conta())
        ok(quadros() == abertura and rola()[1] > 20, 'com 20 e com a nota, os quadros continuam na mesma altura, e os alertas tambem rolam por dentro')
        url = pg.url
        pg.evaluate("(() => { const l = document.getElementById('listaMaisVendidos'); l.dispatchEvent(new MouseEvent('click', { bubbles: true })); })()"); pg.wait_for_timeout(250)
        ok(pg.url == url, 'clicar na barra de rolagem ou no vazio da lista nao navega')
        ok(pg.evaluate("!document.getElementById('quadroLojas').hasAttribute('data-href')"), '"Vendas por Loja" nao e mais link: o clique nele escolhe a loja')
        geral = pg.evaluate("Array.from(document.querySelectorAll('.kpi-card[data-kpi] .kpi-value')).map(e => e.textContent)")
        pg.evaluate("document.querySelector('#quadroLojas .legend-row[data-store=shope]').click()"); pg.wait_for_timeout(300)
        da_loja = pg.evaluate("Array.from(document.querySelectorAll('.kpi-card[data-kpi] .kpi-value')).map(e => e.textContent)")
        ok(DASH in pg.url and len(geral) == 9 and all(a != b for a, b in zip(geral, da_loja)) and da_loja[0] == 'R$ 82.940,00' and 'Desk Shope' in pg.evaluate("document.querySelector('.subtitle').textContent"),
           'clicar em Desk Shope fica na tela e troca os 9 indicadores pelos da loja: %s' % da_loja[:3])
        so_da_loja = pg.evaluate("[Array.from(document.querySelectorAll('#listaMaisVendidos .rank-store')).every(e => e.textContent === 'Desk Shope'), Array.from(document.querySelectorAll('#listaAlertas .stock-min')).every(e => e.textContent.endsWith('Desk Shope'))]")
        ok(so_da_loja == [True, True] and pg.evaluate("document.getElementById('statusTotal').textContent") != '648 pedidos' and 'Meta da Desk Shope' in pg.evaluate("document.getElementById('metaTotal').textContent")
           and pg.evaluate("document.getElementById('estoqueTotal').textContent") != valor_estoque, 'e as listas, os pedidos por status, a meta e o valor em estoque passam a ser so dela')
        fecham = pg.evaluate("Object.keys(KPI).filter(k => KPI[k].total).every(k => Math.abs(['shope', 'tech', 'brands'].reduce((s, l) => s + daLoja(KPI[k].total, l), 0) - KPI[k].total) < 0.005) && ['shope', 'tech', 'brands'].reduce((s, l) => s + KPI.vendasMes.porLoja[l], 0) === KPI.vendasMes.porLoja.all")
        ok(fecham, 'a soma das tres lojas fecha com o total em cada indicador')
        pg.evaluate("document.querySelector('#quadroLojas .legend-row[data-store=shope]').click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate("Array.from(document.querySelectorAll('.kpi-card[data-kpi] .kpi-value')).map(e => e.textContent)") == geral and 'todas as lojas' in pg.evaluate("document.querySelector('.subtitle').textContent"),
           'clicar de novo na mesma loja desmarca e volta aos numeros de todas')

        filas = {}
        for chave, tela in [('doca', 'pagina-estoque-conferencia-entrada.html'), ('ender', 'pagina-estoque-enderecamento.html'), ('compra', NEC), ('bloq', 'pagina-estoque-itens-bloqueados.html'),
                            ('sep', 'pagina-logistica-separacao.html'), ('conf', 'pagina-logistica-conferencia-saida.html'), ('exp', 'pagina-logistica-expedicao.html'),
                            ('pagar', 'pagina-financas-contas-pagar.html'), ('receber', 'pagina-financas-contas-receber.html')]:
            ir(tela)
            filas[chave] = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.main .aba-sit, .main [data-aba]')).map(a => [a.getAttribute('data-sit') || a.getAttribute('data-aba'), Number((a.querySelector('.sit-contador, .aba-contador, span:last-child') || a).textContent.replace(/[^0-9]/g, ''))]))")
        esperado = {'doca': filas['doca']['pronto'], 'ender': filas['ender']['a_enderecar'], 'compra': filas['compra']['comprar'], 'bloq': filas['bloq']['todos'], 'sep': filas['sep']['fila'],
                    'conf': filas['conf']['aguardando'], 'exp': filas['exp']['montagem'] + filas['exp']['conferindo'], 'pagar': filas['pagar']['atrasada'], 'receber': filas['receber']['atrasada']}
        ir(BV)
        mostrado = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('#quadroDoDia .dia-fila')).map(a => [a.getAttribute('data-fila'), Number(a.querySelector('.dia-numero').textContent)]))")
        ok(mostrado == esperado, 'cada numero de "Pendencias do Dia" e o da aba da fila dona: %s' % mostrado)
        ok(pg.evaluate("document.querySelector('#quadroDoDia .card-title').textContent") == 'Pendências do Dia', 'o quadro tem o nome formal que o usuario pediu, "Pendencias do Dia"')
        destinos = pg.evaluate("Array.from(document.querySelectorAll('#quadroDoDia .dia-fila')).map(a => a.getAttribute('href').split('/').pop())")
        ok(len(destinos) == 9 and all(d in TODAS for d in destinos), 'e cada fila leva a tela dela')
        geo = pg.evaluate("""(() => { const q = document.getElementById('quadroDoDia').getBoundingClientRect(), l = document.querySelector('.row-welcome').getBoundingClientRect();
            const c = Array.from(document.querySelectorAll('.row-welcome > .card')).map(x => x.getBoundingClientRect());
            return { fora: !document.querySelector('.row-welcome #quadroDoDia') && !document.getElementById('filaDoDia'), largura: Math.abs(q.width - l.width) < 2, abaixo: q.top >= Math.max(c[0].bottom, c[1].bottom),
                     alturas: Math.abs(c[0].height - c[1].height), colunas: document.querySelectorAll('#quadroDoDia .dia-coluna').length }; })()""")
        ok(geo['fora'] and geo['largura'] and geo['abaixo'] and geo['colunas'] == 3, 'o quadro e proprio: fora dos atalhos, abaixo dos dois quadros e de lado a lado, em 3 colunas')
        atalhos = pg.evaluate("Array.from(document.querySelectorAll('.shortcut-tile')).map(t => (t.getAttribute('data-href') || '').split('/').pop().split('?')[0])")
        ok(len(atalhos) == 10 and all(a in TODAS for a in atalhos), 'os atalhos ganharam dois botoes, todos com destino')
        ok(geo['alturas'] <= 1, 'o quadro da agenda e o dos atalhos fecham na mesma altura (diferenca de %.1fpx; eram 5)' % geo['alturas'])

    if secao(9, 'Cadastros: o painel leva a ver o cadastro, e o editar fica na pagina'):
        # 13/out: o painel tinha "Editar cadastro completo" e a pagina abria ja editavel. O usuario pediu
        # "Ver cadastro completo", com o botao de editar dentro da pagina, no topo.
        ir('pagina-cadastros-clientes.html'); pg.evaluate("localStorage.removeItem('deskParametros')")
        ruins = []
        for base in ['clientes', 'fornecedores', 'produtos', 'vendedores', 'lojas-desk']:
            det = 'pagina-cadastros-%s-detalhe.html' % base
            ir('pagina-cadastros-%s.html' % base)
            pg.click('.main [class$="-nome-row"]'); pg.wait_for_timeout(350)
            botao = pg.evaluate("(() => { const a = document.querySelector('.event-drawer.open a.btn-primary'); return a ? [a.textContent.trim(), a.getAttribute('href')] : null; })()")
            # O link leva o ?id= do registro clicado (teste_cad_detalhe.py confere qual); aqui importa o rotulo e a pagina.
            if not botao or botao[0] != 'Ver cadastro completo' or botao[1].split('?')[0] != '../cadastros/' + det:
                ruins.append('%s: botao do painel %s' % (base, botao)); continue
            clic('.event-drawer.open a.btn-primary'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            estado = pg.evaluate("(() => { const b = document.getElementById('btnEditarRegistro'); return [document.body.classList.contains('modo-leitura'), !!b && b.offsetParent !== null, b ? b.textContent.trim() : '', "
                                 "!!b && !!b.closest('.page-header')]; })()")
            if not pg.url.split('/')[-1].split('?')[0] == det or estado != [True, True, 'Editar cadastro', True]:
                ruins.append('%s: pagina %s %s' % (base, pg.url.split('/')[-1], estado)); continue
            clic('#btnEditarRegistro'); pg.wait_for_timeout(250)
            if pg.evaluate("document.body.classList.contains('modo-leitura') || document.getElementById('btnEditarRegistro').offsetParent !== null"):
                ruins.append('%s: Editar cadastro nao destravou a pagina' % base)
        ok(not ruins, 'nos cinco cadastros o painel traz "Ver cadastro completo", a pagina abre so para leitura e o botao "Editar cadastro", no topo, destrava: %s' % ruins[:3])
        velho = [n for n in TODAS if 'Editar cadastro completo' in open(localiza.onde(n), encoding='utf-8').read()]
        ok(not velho, 'nenhuma tela ainda oferece "Editar cadastro completo": %s' % velho[:4])
        ir('pagina-cadastros-fornecedores-detalhe.html', '?editar=1')
        ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), 'e o endereco com ?editar=1 continua abrindo editavel, para quem ja chega querendo editar')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
