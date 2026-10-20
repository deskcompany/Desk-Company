# -*- coding: utf-8 -*-
# Vale-compra, entrega 2: o vale se usa (barganha aprovada pelo usuario em 19/out/2026).
#
# O vale e saldo do cliente, sem codigo, e so vale na loja que o emitiu. Nesta entrega ele se usa: no PDV (tudo ou uma parte, o saldo na loja
# do PDV), no Pedido de Venda (desconta ao SALVAR; cancelar o pedido devolve) e como forma de recebimento "Vale-compra" (a chave interna
# continua `valetroca`). A parte paga com vale vira titulo JA RECEBIDO em Contas a Receber e NAO entra no Caixa. A Devolucao segue com o
# vale reservado (entrega 3).
#
#   [1] O bloco comum: usarVale (vence primeiro, segue para o proximo, nao passa do saldo, nao grava nada parcial) e estornarUsos (volta ao
#       saldo; vale vencido volta e continua vencido; vale cancelado nao recebe e fica "perdido");
#   [2] Formas de Recebimento: Vale-compra habilitada, destino proprio, sem conta/taxa; desabilitar tira o vale do PDV e do Pedido;
#   [3] PDV: o quadro so com saldo na loja certa, outra loja so como aviso, usar parte, usar tudo, validacoes, a venda grava e o saldo desce,
#       nada no Caixa, o turno nao pede contagem do vale;
#   [4] Pedido de Venda: o quadro, as parcelas pelo que falta, salvar desce, editar refaz, cancelar devolve, o pedido 10 mostra o VC-3;
#   [5] A pagina do vale: uso estornado riscado com o motivo, e o perdido no vale cancelado;
#   [6] Contas a Receber: os tres titulos de exemplo, titulo de uso novo, cancelado ao estornar, detalhe so leitura, titulo 9 em Crediario;
#   [7] O bloco identico em todas as copias e a barra de rolagem de 1280 e 1440.
from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
PDV, PED_D, FORMAS_CAD = 'pagina-vendas-pdv.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-configuracoes-formas-recebimento.html'
PED_L = 'pagina-vendas-pedidos.html'
CR_L, CR_D = 'pagina-financas-contas-receber.html', 'pagina-financas-contas-receber-detalhe.html'
VALE_L, VALE_D, CLI_D = 'pagina-financas-vale-compra.html', 'pagina-financas-vale-compra-detalhe.html', 'pagina-cadastros-clientes-detalhe.html'
CHAVES_LOCAIS = ['deskValesCompra', 'deskValesCompraExemplo', 'deskPdv', 'deskParametros', 'deskLog', 'deskCaixaExtras']

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


HOJE = date.today()
dia = lambda n: HOJE + timedelta(days=n)
iso = lambda d: d.isoformat()
br = lambda d: d.strftime('%d/%m/%Y')


def moeda(v):
    return 'R$ ' + ('{:,.2f}'.format(v)).replace(',', 'X').replace('.', ',').replace('X', '.')


def uso(valor, data, tipo='pedido', id_=1, rotulo=None, **extra):
    d = dict(data=iso(data), valor=valor, doc=dict(tipo=tipo, id=id_, rotulo=rotulo or ('Pedido nº %d' % id_)))
    d.update(extra)
    return d


def vale(n, cid, nome, doc, loja, valor, emitido_ha, venc_em, usos=None, cancelado=None):
    return dict(n=n, clienteId=cid, cliente=nome, doc=doc, loja=loja, origem='cortesia', motivo='Motivo de teste', valor=valor,
                emitido=iso(dia(-emitido_ha)), venc=iso(dia(venc_em)), usos=usos or [], reativacoes=[], cancelado=cancelado)


MEDE = """() => { const r = []; document.querySelectorAll('.estoque-table-wrap').forEach(w => {
  if (w.getClientRects().length && w.scrollWidth > w.clientWidth + 1) r.push((w.id || w.className) + ' ' + w.scrollWidth + '>' + w.clientWidth); });
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) r.push('a pagina rola'); return r; }"""


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('console', lambda m: erros.append('console: ' + m.text[:160]) if m.type == 'error' else None)

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)

    def limpar(com_exemplo=False):
        if pg.url == 'about:blank':
            ir(VALE_L)
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        # O desconto Pix/dinheiro do PDV (21/out/2026) nasce ligado; aqui os numeros contam o valor cheio, entao ele fica desligado.
        pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))")
        # Sem exemplo o armazenamento parte vazio, com a marca; com exemplo, o vale nasce do estado de fabrica.
        if not com_exemplo:
            pg.evaluate("localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [] })); localStorage.setItem('deskValesCompraExemplo', '1')")

    def semear(lista):
        pg.evaluate("(v) => { localStorage.setItem('deskValesCompra', JSON.stringify({ vales: v })); localStorage.setItem('deskValesCompraExemplo', '1'); }", lista)

    def gravados():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskValesCompra') || '{}').vales || [])")

    def por_n(n):
        return [v for v in gravados() if v['n'] == n][0]

    def saldo_de(n):
        return pg.evaluate("(n) => valeSaldo(valeLer().filter(v => v.n === n)[0])", n)

    def sit_de(n):
        return pg.evaluate("(n) => valeSituacao(valeLer().filter(v => v.n === n)[0])", n)

    def escolher(raiz, valor):
        clic('#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(120)
        pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
        pg.wait_for_timeout(250)

    # ================================================================== [1] o bloco
    if secao(1, 'O bloco comum: usarVale e estornarUsos'):
        # Marina (1), loja 1: VC-1 (R$ 100, vence em 10 dias), VC-2 (R$ 50, vence em 5 dias, vence primeiro), VC-3 em outra loja,
        # VC-4 vencido e VC-5 cancelado, os dois da loja 1 e que nao se usam.
        cen = [vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 100, 20, 10), vale(2, 1, 'Marina Duarte', '123.456.789-00', 1, 50, 20, 5),
               vale(3, 1, 'Marina Duarte', '123.456.789-00', 2, 70, 20, 30), vale(4, 1, 'Marina Duarte', '123.456.789-00', 1, 40, 200, -5),
               vale(5, 1, 'Marina Duarte', '123.456.789-00', 1, 60, 20, 30, cancelado=dict(em=iso(dia(-1)), motivo='Teste', saldo=60))]
        limpar(); ir(VALE_L); semear(cen); ir(VALE_L)
        DOC = "{ tipo: 'pedido', id: 50, rotulo: 'Pedido nº 50' }"
        ok(pg.evaluate("valeSaldoDoCliente(1, 1)") == 150 and pg.evaluate("valeSaldoDoCliente(1, 2)") == 70, 'o saldo do cliente conta só o disponível da loja: R$ 150,00 na loja 1 (vencido e cancelado ficam fora) e R$ 70,00 na 2')
        r = pg.evaluate("usarVale(1, 1, 60, %s)" % DOC)
        ok(r == [dict(n=2, valor=50), dict(n=1, valor=10)], 'gasta primeiro do vale que vence antes (VC-2, R$ 50,00) e segue para o próximo (VC-1, R$ 10,00): %s' % r)
        ok(saldo_de(2) == 0 and sit_de(2) == 'usado' and saldo_de(1) == 90 and saldo_de(3) == 70 and saldo_de(4) == 40, 'o saldo desce nos dois vales tocados e o resto fica como estava')
        ok(por_n(2)['usos'][-1] == dict(data=iso(HOJE), valor=50, doc=dict(tipo='pedido', id=50, rotulo='Pedido nº 50')) and len(por_n(1)['usos']) == 1,
           'cada vale tocado ganha um uso { data, valor, doc: { tipo, id, rotulo } }: %s' % por_n(2)['usos'][-1])
        antes = pg.evaluate("localStorage.getItem('deskValesCompra')")
        msg = pg.evaluate("(() => { try { usarVale(1, 1, 90.01, %s); return 'passou'; } catch (e) { return e.message; } })()" % DOC)
        ok(msg != 'passou' and 'R$ 90,00' in msg and pg.evaluate("localStorage.getItem('deskValesCompra')") == antes, 'passar do saldo lança erro, diz o saldo (R$ 90,00) e não grava nada: %s' % msg)
        ok(pg.evaluate("(() => { try { usarVale(1, 1, 0, %s); return 'passou'; } catch (e) { return 'erro'; } })()" % DOC) == 'erro' and
           pg.evaluate("(() => { try { usarVale(1, 3, 1, %s); return 'passou'; } catch (e) { return 'erro'; } })()" % DOC) == 'erro' and
           pg.evaluate("localStorage.getItem('deskValesCompra')") == antes, 'valor zero e loja sem vale também lançam erro, sem gravar')
        r = pg.evaluate("usarVale(1, 2, 70, { tipo: 'pdv', id: 3, rotulo: 'PDV-0003' })")
        ok(r == [dict(n=3, valor=70)] and sit_de(3) == 'usado' and saldo_de(1) == 90, 'o vale de outra loja só se usa naquela loja: a loja 2 gasta o VC-3 e não toca nos da loja 1')
        # estorno: volta ao saldo, o uso fica no historico como estornado
        r = pg.evaluate("estornarUsos(%s, 'pedido cancelado')" % DOC)
        ok(sorted(r, key=lambda x: x['n']) == [dict(n=1, valor=10, perdido=False), dict(n=2, valor=50, perdido=False)], 'estornar devolve o valor a cada vale tocado: %s' % r)
        ok(saldo_de(2) == 50 and sit_de(2) == 'disponivel' and saldo_de(1) == 100 and por_n(2)['usos'][0]['estornado'] == dict(em=iso(HOJE), motivo='pedido cancelado'),
           'o valor volta ao saldo, o vale usado volta a disponível e o uso fica no histórico como "estornado: pedido cancelado"')
        ok(pg.evaluate("valeUsado(valeLer().filter(v => v.n === 2)[0])") == 0 and pg.evaluate("estornarUsos(%s, 'de novo')" % DOC) == [], 'o saldo ignora o uso estornado, e estornar de novo não faz nada')
        ok(pg.evaluate("valeUsosDoDoc(%s)" % DOC) == [] and pg.evaluate("valeUsosDoDoc({ tipo: 'pdv', id: 3, rotulo: 'PDV-0003' })") == [dict(n=3, valor=70, cancelado=False)], 'os usos que valem para um documento ignoram o estornado')
        # vale vencido recebe o valor de volta e continua vencido
        pg.evaluate("usarVale(1, 1, 50, { tipo: 'pedido', id: 51, rotulo: 'Pedido nº 51' })")
        sem = gravados()
        for v in sem:
            if v['n'] == 2:
                v['venc'] = iso(dia(-2))
        semear(sem); ir(VALE_L)
        r = pg.evaluate("estornarUsos({ tipo: 'pedido', id: 51, rotulo: 'Pedido nº 51' }, 'pedido cancelado')")
        ok(r and saldo_de(2) == 50 and sit_de(2) == 'vencido', 'vale vencido recebe o valor de volta e continua vencido (reativa com senha, como antes): saldo %s, situação %s' % (saldo_de(2), sit_de(2)))
        # vale cancelado nao recebe: o valor fica perdido
        sem = gravados()
        for v in sem:
            if v['n'] == 1:
                v['usos'].append(uso(25, dia(-3), id_=52))
                v['cancelado'] = dict(em=iso(HOJE), motivo='Teste', saldo=75)
        semear(sem); ir(VALE_L)
        r = pg.evaluate("estornarUsos({ tipo: 'pedido', id: 52, rotulo: 'Pedido nº 52' }, 'pedido cancelado')")
        u52 = [u for u in por_n(1)['usos'] if u['doc']['id'] == 52][0]
        ok(r == [dict(n=1, valor=25, perdido=True)] and saldo_de(1) == 0 and 'estornado' not in u52 and u52['perdido'] == dict(em=iso(HOJE), motivo='pedido cancelado'),
           'vale cancelado não recebe estorno: o saldo segue em zero e o uso fica marcado como perdido: %s' % r)
        ok(pg.evaluate("estornarUsos({ tipo: 'pedido', id: 52, rotulo: 'Pedido nº 52' }, 'outra vez')") == [], 'e o perdido não é estornado de novo')
        # formato antigo (anterior a entrega 2) continua legivel
        semear([vale(9, 1, 'Marina Duarte', '123.456.789-00', 1, 100, 10, 100, usos=[dict(data=iso(dia(-1)), documento='Pedido nº 8', pedidoId=8, valor=10)])]); ir(VALE_L)
        ok(pg.evaluate("valeLer()[0].usos[0].doc") == dict(tipo='pedido', id=8, rotulo='Pedido nº 8') and saldo_de(9) == 90, 'uso gravado no formato antigo ({ documento, pedidoId }) é lido como { doc } e continua valendo')

    # ================================================================== [2] Formas de Recebimento
    if secao(2, 'Formas de Recebimento: Vale-compra habilitada, destino próprio, e desabilitar tira do PDV e do Pedido'):
        limpar(); ir(FORMAS_CAD)
        f = pg.evaluate("FORMAS.filter(f => f.chave === 'valetroca')[0]")
        ok(f['nome'] == 'Vale-compra' and f['ativo'] is True and f['destino'] == 'vale' and f['sistema'] is True and not f.get('reservada') and f['contaId'] is None and f['tarifacao'] == 'sem' and f['taxaPct'] == 0 and f['taxaFixa'] == 0 and f['validaLimite'] is False,
           'o cadastro: Vale-compra, do sistema, habilitada, destino "vale", sem conta, sem taxa e sem limite (a chave interna é valetroca): %s' % f)
        src = fonte(FORMAS_CAD)
        ok('Vale-troca' not in src and 'está <b>reservada</b>' not in src and 'está reservada' not in src, 'os dois avisos de "reservada" saíram da tela')
        ok(not any('Vale-troca' in fonte(t) for t in (PDV, CR_L, CR_D, FORMAS_CAD)), 'o nome Vale-troca saiu de Formas de Recebimento, do PDV e de Contas a Receber (a Devolução fica para a entrega 3)')
        ir(PDV)
        pdv = pg.evaluate("FORMAS.filter(f => f.chave === 'valetroca')[0]")
        ok(all(pdv[k] == f[k] for k in ('nome', 'uso', 'destino', 'contaId', 'tarifacao', 'taxaPct', 'taxaFixa', 'validaLimite', 'ativo')), 'o espelho do PDV é igual ao cadastro, campo a campo')
        ir(PED_D)
        ok(pg.evaluate("FORMA_VALE") == dict(chave='valetroca', nome='Vale-compra', ativo=True), 'o espelho do Pedido de Venda (chave, nome, ativo) é igual ao cadastro')
        # desabilitada, some do PDV e do Pedido
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 120, 10, 170)]); ir(PED_D, '?id=1&editar=1')
        ok(visivel('#inputValeUsar'), 'com a forma habilitada, o Pedido de Marina (loja 1) mostra o campo "Usar do vale"')
        pg.evaluate("FORMA_VALE.ativo = false; pintarQuadroVale(true)"); pg.wait_for_timeout(150)
        ok(not visivel('#linhaVale') and pg.locator('#inputValeUsar').count() == 0, 'com a forma desabilitada, o quadro some do Pedido de Venda')
        ir(PDV)
        pg.evaluate("localStorage.removeItem('deskPdv')"); pg.reload(); pg.wait_for_timeout(400)
        clic('#btnAbrirCaixa'); pg.wait_for_timeout(300); escolher('abrirLoja', 1); pg.fill('#abrirTroco', '100'); clic('#btnConfirmarAbertura'); pg.wait_for_timeout(400)
        pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', 'FON-BT-200'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
        clic('#btnCliente'); pg.wait_for_timeout(300); pg.fill('#buscaCliente', 'Marina'); pg.wait_for_timeout(200); clic('#listaClientes .pdv-cli'); pg.wait_for_timeout(300)
        clic('#btnContinuar'); pg.wait_for_timeout(400)
        ok(visivel('#quadroValeCliente'), 'com a forma habilitada, o PDV mostra o quadro do vale')
        pg.evaluate("formaDe('valetroca').ativo = false; pintarFinalizar()"); pg.wait_for_timeout(150)
        ok(pg.locator('#quadroValeCliente').count() == 0 and pg.locator('#quadroVale').inner_text().strip() == '', 'com a forma desabilitada, o quadro some do PDV')

    # ================================================================== [3] PDV
    if secao(3, 'PDV: o quadro, usar parte ou tudo, as validações, a venda grava e nada entra no Caixa'):
        def pdv_novo(loja=1, produto='FON-BT-200', clienteTxt='Marina', vales=None, continuar=True):
            limpar(); ir(PDV)
            if vales is not None:
                semear(vales)
            pg.evaluate("localStorage.removeItem('deskPdv')"); pg.reload(); pg.wait_for_timeout(450)
            clic('#btnAbrirCaixa'); pg.wait_for_timeout(300); escolher('abrirLoja', loja); pg.fill('#abrirTroco', '100'); clic('#btnConfirmarAbertura'); pg.wait_for_timeout(400)
            pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', produto); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
            if clienteTxt:
                clic('#btnCliente'); pg.wait_for_timeout(300); pg.fill('#buscaCliente', clienteTxt); pg.wait_for_timeout(200)
                clic('#listaClientes .pdv-cli'); pg.wait_for_timeout(300)
            if continuar:
                clic('#btnContinuar'); pg.wait_for_timeout(400)

        MARINA = vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 120, 20, 160)
        # --- o quadro so aparece com saldo na loja do PDV
        pdv_novo(vales=[MARINA, vale(2, 1, 'Marina Duarte', '123.456.789-00', 2, 50, 10, 170)])
        q = pg.inner_text('#quadroValeCliente')
        ok('Vale-compra disponível' in q and 'R$ 120,00' in q and 'vence %s' % br(dia(160)) in q, 'com cliente que tem saldo na loja do PDV, o quadro diz "Vale-compra disponível R$ 120,00" e quando vence: %s' % q.replace('\n', ' | ')[:90])
        ok(pg.input_value('#valeUsarValor') == '120,00' and visivel('#btnUsarVale'), 'o campo nasce com o menor entre o saldo e o que falta pagar (R$ 120,00 de R$ 249,90) e tem o botão "Usar"')
        fora = pg.inner_text('.pdv-vale-fora') if pg.locator('.pdv-vale-fora').count() else ''
        ok('R$ 50,00 em vales da Desk Brands, que não valem nesta loja' in fora, 'o vale da outra loja só aparece como uma linha discreta: %s' % fora)
        ok('R$ 170,00' not in q, 'e o saldo de outra loja não entra no valor do quadro')
        # sem cliente ou sem saldo: nada
        pdv_novo(clienteTxt=None, continuar=True, vales=[MARINA])
        ok(pg.locator('#quadroVale').inner_text().strip() == '', 'sem cliente, nada aparece')
        pdv_novo(clienteTxt='Distribuidora', vales=[MARINA])
        ok(pg.locator('#quadroVale').inner_text().strip() == '', 'cliente sem vale: nada aparece')
        pdv_novo(clienteTxt='Pedro Henrique', vales=[vale(1, 6, 'Pedro Henrique Alves', '456.789.012-33', 2, 80, 10, 170)])
        ok(pg.locator('#quadroValeCliente').count() == 0 and 'R$ 80,00 em vales da Desk Brands, que não valem nesta loja' in pg.inner_text('#quadroVale'), 'cliente que só tem vale em outra loja: sem quadro, só a linha de aviso')
        pdv_novo(loja=2, produto='CAM-BSC-PT', clienteTxt='Pedro Henrique', vales=[vale(1, 6, 'Pedro Henrique Alves', '456.789.012-33', 2, 80, 10, 170)])
        ok(pg.input_value('#valeUsarValor') == '79,90', 'na loja certa o quadro aparece, e o campo sugere o que falta pagar quando é menor que o saldo (R$ 79,90 de R$ 80,00)')
        pdv_novo(vales=[vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 60, 10, 170, cancelado=dict(em=iso(dia(-1)), motivo='T', saldo=60)),
                        vale(2, 1, 'Marina Duarte', '123.456.789-00', 1, 40, 200, -3)])
        ok(pg.locator('#quadroVale').inner_text().strip() == '', 'vale cancelado ou vencido não aparece')
        # --- validacoes
        pdv_novo(vales=[MARINA])
        for txt, trecho in (('0', 'Informe o valor do vale'), ('abc', 'Informe o valor do vale'), ('200', 'R$ 120,00 de vale nesta loja')):
            pg.fill('#valeUsarValor', txt); clic('#btnUsarVale'); pg.wait_for_timeout(250)
            e = pg.inner_text('#erroValeUsar')
            ok(trecho in e and pg.evaluate("venda.recebimentos.length") == 0, 'valor "%s": %s, e nada entra na venda' % (txt, e))
        pdv_novo(produto='CAR-33W-01', clienteTxt='Marina', vales=[MARINA])
        ok(pg.input_value('#valeUsarValor') == '97,55', 'venda de R$ 97,55: o campo sugere só o que falta pagar')
        pg.fill('#valeUsarValor', '110'); clic('#btnUsarVale'); pg.wait_for_timeout(250)
        ok('só precisa de mais R$ 97,55' in pg.inner_text('#erroValeUsar') and pg.evaluate("venda.recebimentos.length") == 0, 'mais do que a venda precisa é barrado, com o número: %s' % pg.inner_text('#erroValeUsar'))
        # --- usar parte: a sobra continua no vale
        pdv_novo(vales=[MARINA])
        pg.fill('#valeUsarValor', '50'); clic('#btnUsarVale'); pg.wait_for_timeout(300)
        r = pg.evaluate("venda.recebimentos.map(r => [r.chave, r.valor])")
        ok(r == [['valetroca', 50]] and 'Falta receber R$ 199,90' in pg.inner_text('#faltaReceber'), 'usar parte vira um recebimento Vale-compra de R$ 50,00, e falta receber R$ 199,90: %s' % pg.inner_text('#faltaReceber'))
        ok(pg.locator('#menuAddReceb .dropdown-select-item[data-value="valetroca"]').count() == 0 and pg.locator('#menuAddReceb .dropdown-select-item[data-value="pix"]').count() == 1,
           'o vale não está no menu "Adicionar recebimento": tem o quadro próprio')
        pg.evaluate("document.querySelector('#menuAddReceb .dropdown-select-item[data-value=\"pix\"]').click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate("venda.recebimentos.map(r => [r.chave, r.valor])") == [['valetroca', 50], ['pix', 199.9]] and 'Pode finalizar' in pg.inner_text('#faltaReceber'),
           'o Pix leva o que falta (R$ 199,90) e a venda pode finalizar')
        ok(saldo_de(1) == 120, 'antes de finalizar o vale não se mexe: o uso só é gravado com a venda')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        ok(saldo_de(1) == 70 and sit_de(1) == 'disponivel', 'venda gravada: o saldo do vale desceu R$ 50,00 e a sobra (R$ 70,00) continua no vale')
        u = por_n(1)['usos'][0]
        ok(u['valor'] == 50 and u['doc'] == dict(tipo='pdv', id=1, rotulo='PDV-0001') and u['data'] == iso(HOJE), 'o uso fica no vale com o documento PDV-0001: %s' % u['doc'])
        ger = pg.inner_text('#concGerado')
        ok('R$ 50,00' in ger and 'pagos com vale-compra (VC-1)' in ger and 'o saldo do vale fica em R$ 70,00' in ger and 'Título já recebido em Contas a Receber, sem entrar no Caixa' in ger,
           'o que a venda gerou diz o valor, o vale, o saldo que sobra e que não entra no Caixa: %s' % ger.replace('\n', ' ')[-190:])
        extras = pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras') || '[]')")
        ok([e['valor'] for e in extras] == [199.9] and 'Vale' not in str(extras), 'no Caixa entra só o Pix (R$ 199,90): o vale não é dinheiro novo')
        pg.evaluate("abrirDetalhesCaixa(null)"); pg.wait_for_timeout(300)
        cx = pg.inner_text('#caixaCorpo')
        ok('Vale-compra: R$ 50,00' in cx and 'não entra na gaveta' in cx, 'o resumo do turno diz o que foi usado de vale e que não entra na gaveta: %s' % cx.replace('\n', ' ')[-150:])
        ok(pg.evaluate("esperadoPorForma(turno).map(l => l.chave)") == ['dinheiro', 'pix'] and pg.evaluate("dinheiroNaGaveta(turno)") == 100,
           'o vale não entra na gaveta nem pede contagem no fechamento: %s' % pg.evaluate("esperadoPorForma(turno).map(l => l.chave)"))
        # o uso aparece na pagina do vale e em Contas a Receber
        ir(VALE_D, '?id=1')
        linhas = pg.evaluate("[...document.querySelectorAll('#corpoUsos tr')].map(tr => [...tr.children].map(td => td.textContent.replace(/\\s+/g, ' ').trim()))")
        ok(linhas == [[br(HOJE), 'PDV-0001', 'R$ 50,00', 'R$ 70,00']], 'a página do vale mostra o uso: data, PDV-0001, R$ 50,00 e saldo depois R$ 70,00: %s' % linhas)
        ok(pg.get_attribute('#corpoUsos a', 'href') == '../vendas/pagina-vendas-pedidos-detalhe.html?id=900001', 'e o documento é link para o pedido que o PDV gerou')
        ir(CR_L)
        t = pg.evaluate("TITULOS.filter(t => t.vale)")
        ok(len(t) == 1 and t[0]['doc'] == 'PDV-0001' and t[0]['forma'] == 'Vale-compra' and t[0]['valor'] == 50 and t[0]['recebido'] == 50 and not t[0]['cancelado'] and t[0]['origemTexto'] == 'PDV-0001',
           'Contas a Receber ganha o título do uso, já recebido, forma Vale-compra, documento PDV-0001: %s' % [(x['doc'], x['valor'], x['forma']) for x in t])
        # --- usar tudo
        pdv_novo(vales=[MARINA])
        clic('#btnUsarVale'); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('#menuAddReceb .dropdown-select-item[data-value=\"pix\"]').click()"); pg.wait_for_timeout(250)
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        ok(saldo_de(1) == 0 and sit_de(1) == 'usado', 'usar tudo (sem digitar nada, o campo já vem com o saldo): o vale fica usado')
        # --- cancelar a venda antes de gravar nao mexe no vale
        pdv_novo(vales=[MARINA])
        clic('#btnUsarVale'); pg.wait_for_timeout(300)
        pg.evaluate("cancelarVenda()"); pg.wait_for_timeout(300); clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
        ok(saldo_de(1) == 120 and pg.evaluate("venda.recebimentos.length") == 0 and len(por_n(1)['usos']) == 0, 'cancelar a venda antes de gravar não toca no vale: nada foi gasto, nada a estornar')
        # --- o saldo mudou em outra aba: a venda nao passa
        pdv_novo(vales=[MARINA])
        clic('#btnUsarVale'); pg.wait_for_timeout(300)
        pg.evaluate("usarVale(1, 1, 120, { tipo: 'pedido', id: 99, rotulo: 'Pedido nº 99' })")
        pg.evaluate("pintarFinalizar()"); pg.wait_for_timeout(200)
        ok('passa do saldo de vale de Marina Duarte nesta loja' in pg.inner_text('#faltaReceber'), 'se o vale foi usado em outra aba, a venda acusa a pendência: %s' % pg.inner_text('#faltaReceber')[:130].replace(chr(10), ' '))
        clic('#btnFinalizar'); pg.wait_for_timeout(400)
        ok(saldo_de(1) == 0 and len(por_n(1)['usos']) == 1 and pg.evaluate("momento") == 'finalizar', 'e a venda não finaliza: o vale não é gasto duas vezes')
        # --- trocar de cliente tira o vale da venda
        pdv_novo(vales=[MARINA])
        clic('#btnUsarVale'); pg.wait_for_timeout(300)
        clic('#btnClienteFin'); pg.wait_for_timeout(300); pg.fill('#buscaCliente', 'Rafael'); pg.wait_for_timeout(200); clic('#listaClientes .pdv-cli'); pg.wait_for_timeout(300)
        ok(pg.evaluate("venda.recebimentos.filter(r => r.chave === 'valetroca').length") == 0, 'trocar de cliente tira da venda o vale do cliente anterior')

    # ================================================================== [4] Pedido de Venda
    if secao(4, 'Pedido de Venda: o quadro, as parcelas pelo que falta, salvar desce, editar refaz e cancelar devolve'):
        def salvar(senha='x'):
            """Clica em Salvar. Sem senha (o padrao de criar) o pedido salva direto e o modal e o aviso de salvo; com senha, aparece a confirmacao primeiro.
            Devolve (texto da confirmacao ou '', texto do modal de depois)."""
            clic('#btnSalvar'); pg.wait_for_timeout(450)
            txt = pg.inner_text('#confirmModalTexto')
            if pg.locator('#confirmModal.open').count() and ('Salvar este pedido reserva' in txt):
                if visivel('#campoSenhaModal'):
                    pg.fill('#inputSenhaModal', senha)
                clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)
                return txt, pg.inner_text('#confirmModalTexto')
            return '', txt

        def fecha():
            if pg.locator('#confirmModal.open').count():
                pg.evaluate("fecharModalConfirmacao()"); pg.wait_for_timeout(200)

        # --- o pedido 10 (Auto Pecas, loja 3) ja tem R$ 30,00 do VC-3
        limpar(True); ir(PED_D, '?id=10')
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')"), 'o pedido abre em leitura (padrão de Interface do usuário)')
        t = pg.inner_text('#quadroValePedido')
        ok(t.strip() == 'Pago com vale-compra: R$ 30,00 (VC-3)', 'o pedido nº 10 mostra "Pago com vale-compra: R$ 30,00 (VC-3)": %s' % t.replace('\n', ' '))
        ok(pg.get_attribute('#quadroValePedido a', 'href') == '../financas/pagina-financas-vale-compra-detalhe.html?id=3' and not visivel('#inputValeUsar'),
           'o VC-3 é link para a página do vale, e em leitura o quadro vira só o texto (sem campo)')
        ir(PED_D, '?id=10&editar=1')
        t = pg.inner_text('#quadroValePedido')
        ok('Vale-compra disponível R$ 80,00, contando os R$ 30,00 que este pedido já usa' in t and pg.input_value('#inputValeUsar') == '30,00' and 'vence em' in t,
           'editando, o quadro conta o que o próprio pedido já usa (R$ 50,00 de saldo + R$ 30,00) e o campo vem com R$ 30,00: %s' % t.replace('\n', ' | ')[:150])
        ok(pg.locator('#notaVale').count() == 1 and 'R$ 30,00' in pg.inner_text('#notaVale') and 'pagos com vale-compra' in pg.inner_text('#notaVale'), 'a prévia diz "R$ 30,00 pagos com vale-compra"')
        # --- as parcelas valem so para o que falta receber
        limpar(True); ir(PED_D, '?id=1&editar=1')
        pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0")
        total_ped = pg.evaluate("recalcularTotais()")
        ok('R$ 120,00' in pg.inner_text('#quadroValePedido') and pg.input_value('#inputValeUsar') == '', 'pedido nº 1 (Marina, loja 1): o quadro mostra o saldo de R$ 120,00 e o campo começa vazio')
        escolher('inputCondicao', 3)
        pg.fill('#inputValeUsar', '100'); pg.wait_for_timeout(250)
        chips = pg.evaluate("[...document.querySelectorAll('#previaParcelas .parcela-chip b')].map(b => paraNumero(b.textContent))")
        ok(len(chips) == 3 and abs(sum(chips) - (total_ped - 100)) < 0.005, 'em 3x, as parcelas somam o que falta (total − vale = %.2f), não o total: %s' % (total_ped - 100, chips))
        ok('R$ 100,00' in pg.inner_text('#notaVale') and 'pagos com vale-compra' in pg.inner_text('#notaVale') and 'faltam receber' in pg.inner_text('#notaVale'), 'e a prévia diz "R$ 100,00 pagos com vale-compra": %s' % pg.inner_text('#notaVale'))
        pg.fill('#inputValeUsar', ''); pg.wait_for_timeout(200)
        chips = pg.evaluate("[...document.querySelectorAll('#previaParcelas .parcela-chip b')].map(b => paraNumero(b.textContent))")
        ok(pg.locator('#notaVale').count() == 0 and abs(sum(chips) - total_ped) < 0.005, 'sem vale, as parcelas voltam a somar o total')
        # --- validacoes
        escolher('inputCondicao', 1)
        for txt, trecho in (('120,01', 'R$ 120,00 de vale-compra nesta loja'), ('99999', 'R$ 120,00 de vale-compra nesta loja')):
            pg.fill('#inputValeUsar', txt); pg.wait_for_timeout(150)
            ant = pg.evaluate("localStorage.getItem('deskValesCompra')")
            salvar(); t = pg.inner_text('#confirmModalTexto')
            ok('não pode ser salvo' in t and trecho in t and pg.evaluate("localStorage.getItem('deskValesCompra')") == ant, 'valor %s: o pedido não salva, diz o saldo e não mexe no vale: %s' % (txt, t[:150]))
            ok(visivel('#erroVale'), 'e o campo marca o erro'); fecha()
        # --- salvar desce o saldo (uso parcial) e o aviso diz quanto saiu
        pg.fill('#inputValeUsar', '45'); pg.wait_for_timeout(150)
        pg.evaluate("PARAM.confirmacoes = { pedidosCria: true }")   # com a senha ligada a confirmação aparece, e o texto diz o que sai do vale
        confirma, aviso = salvar()
        pg.evaluate("PARAM.confirmacoes = {}")
        ok('tira R$ 45,00 do vale-compra' in confirma and 'conta a receber de ' + moeda(total_ped - 45) in confirma, 'a confirmação diz quanto sai do vale e a conta a receber que nasce só do que falta: %s' % confirma[:200])
        ok('R$ 45,00 saíram do vale-compra (VC-4)' in aviso, 'o aviso de salvo diz quanto saiu do vale: %s' % aviso[:220])
        ok(saldo_de(4) == 75 and por_n(4)['usos'][0]['doc'] == dict(tipo='pedido', id=1, rotulo='Pedido nº 1') and por_n(4)['usos'][0]['valor'] == 45, 'o saldo do vale desceu para R$ 75,00 e o uso é do Pedido nº 1')
        fecha()
        ok('Pago com vale-compra: R$ 45,00 (VC-4)' in pg.inner_text('#quadroValePedido') and pg.input_value('#inputValeUsar') == '45,00', 'depois de salvar o quadro mostra o que o pedido usou')
        # --- salvar igual nao refaz
        confirma, aviso = salvar(); fecha()
        ok('continuam pagos com o vale-compra (VC-4)' in aviso and len(por_n(4)['usos']) == 1, 'salvar de novo sem mexer no vale não gasta de novo nem polui o histórico: %s' % aviso[:160])
        # --- editar refaz: estorna o anterior e grava o novo
        pg.fill('#inputValeUsar', '80'); pg.wait_for_timeout(150)
        confirma, aviso = salvar(); fecha()
        us = por_n(4)['usos']
        ok(len(us) == 2 and us[0]['estornado'] == dict(em=iso(HOJE), motivo='pedido alterado') and 'estornado' not in us[1] and us[1]['valor'] == 80 and saldo_de(4) == 40,
           'editar estorna o uso anterior (R$ 45,00, "pedido alterado") e grava o novo (R$ 80,00): saldo R$ 40,00')
        ok('O uso anterior do vale-compra (R$ 45,00) foi estornado' in aviso and 'R$ 80,00 saíram do vale-compra' in aviso, 'o aviso conta o estorno e o uso novo: %s' % aviso[:240])
        # --- tirar o vale devolve
        pg.fill('#inputValeUsar', ''); pg.wait_for_timeout(150)
        confirma, aviso = salvar(); fecha()
        ok(saldo_de(4) == 120 and 'foi estornado' in aviso and len([u for u in por_n(4)['usos'] if 'estornado' not in u]) == 0, 'limpar o campo e salvar devolve tudo ao vale (R$ 120,00)')
        # --- o vale paga o pedido inteiro
        pg.evaluate("ITENS.splice(1); ITENS[0].qtd = 1; ITENS[0].precoLista = 100; ITENS[0].desconto = 0; document.getElementById('inputFrete').value = '0,00'; document.getElementById('inputDesconto').value = '0'; renderItens(); recalcularTotais()")
        pg.fill('#inputValeUsar', '100'); pg.wait_for_timeout(200)
        confirma, aviso = salvar(); fecha()
        ok('nenhuma conta a receber ficou em aberto' in aviso and saldo_de(4) == 20, 'vale igual ao total: o pedido sai pago, sem conta a receber em aberto e o vale fica com R$ 20,00: %s' % aviso[:200])
        # --- cancelar devolve
        clic('#linkCancelarPedido'); pg.wait_for_timeout(350)
        t = pg.inner_text('#confirmModalTexto')
        ok('R$ 100,00 voltam para o vale VC-4' in t, 'a confirmação de cancelar diz "R$ 100,00 voltam para o vale VC-4": %s' % t[:200])
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)
        ok(saldo_de(4) == 120 and [u for u in por_n(4)['usos'] if u['doc']['id'] == 1][-1]['estornado']['motivo'] == 'pedido cancelado', 'cancelar o pedido devolve o valor ao vale, com o motivo "pedido cancelado" (saldo R$ 120,00)')
        ok('voltam para o vale VC-4' in pg.inner_text('#confirmModalTexto'), 'e o aviso depois de cancelar também diz'); fecha()
        ok(pg.locator('#inputValeUsar').count() == 0 or not visivel('#inputValeUsar'), 'pedido cancelado não oferece mais o campo do vale')
        # --- cancelar com o vale cancelado: o valor nao volta
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 120, 20, 160, usos=[uso(30, dia(-2), id_=1)])]); ir(PED_D, '?id=1')
        sem = gravados(); sem[0]['cancelado'] = dict(em=iso(HOJE), motivo='T', saldo=90); semear(sem); ir(PED_D, '?id=1')
        clic('#linkCancelarPedido'); pg.wait_for_timeout(350)
        ok('R$ 30,00 do vale VC-1 não voltam: o vale está cancelado' in pg.inner_text('#confirmModalTexto'), 'se o vale foi cancelado, a confirmação avisa que o valor não volta: %s' % pg.inner_text('#confirmModalTexto')[-120:])
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450); fecha()
        ok(saldo_de(1) == 0 and 'perdido' in por_n(1)['usos'][0], 'e o uso fica como perdido, com o saldo em zero')
        # --- pedido novo: nasce com o numero seguinte
        limpar(True); ir(PED_D, '?novo=1')
        pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0")
        pg.fill('#inputCliente', 'Marina Duarte'); escolher('inputLoja', 1)
        pg.evaluate("ITENS[0] = { nome: 'Fone de Ouvido Bluetooth X200', sku: 'FON-BT-200', qtd: 1, un: 'UN', precoLista: 249.9, desconto: 0, obs: '' }; renderItens(); recalcularTotais()")
        pg.fill('#inputValeUsar', '100'); pg.wait_for_timeout(200)
        confirma, aviso = salvar(); fecha()
        ok(pg.evaluate("PEDIDO.numero") == 17 and pg.input_value('#inputNumero') == '17', 'pedido novo ganha o número seguinte ao maior que existe (17)')
        ok(por_n(4)['usos'][-1]['doc'] == dict(tipo='pedido', id=17, rotulo='Pedido nº 17') and saldo_de(4) == 20, 'o uso fica no vale com o documento "Pedido nº 17": saldo R$ 20,00')
        # --- outra loja: o vale nao vale
        limpar(True); ir(PED_D, '?id=1&editar=1')
        escolher('inputLoja', 2)
        ok(pg.locator('#inputValeUsar').count() == 0 and 'R$ 120,00 em vales da Desk Shope, que não valem nesta loja' in pg.inner_text('#valeOutraLoja'), 'mudando a loja do pedido para Desk Brands, o vale da Desk Shope não vale: sem campo, só o aviso')
        escolher('inputLoja', 1)
        ok(visivel('#inputValeUsar'), 'e voltando para a Desk Shope o campo volta')
        # --- sem vale: nada aparece
        ir(PED_D, '?id=13&editar=1')
        ok(not visivel('#linhaVale'), 'pedido de cliente sem vale não mostra o quadro')
        # --- excluir o pedido e mudar a situacao a mao para Cancelado tambem devolvem o vale (como o botao Cancelar)
        def confirma_modal():
            if visivel('#campoSenhaModal'):
                pg.fill('#inputSenhaModal', 'x')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)

        limpar(True); ir(PED_D, '?id=3')
        clic('#linkExcluirPedido'); pg.wait_for_timeout(350)
        t = pg.inner_text('#confirmModalTexto')
        ok('Confirma exclusão deste pedido?' in t and 'R$ 15,00 voltam para o vale VC-2' in t, 'a confirmação de excluir diz "R$ 15,00 voltam para o vale VC-2": %s' % t[-120:])
        ok(saldo_de(2) == 0, 'antes de confirmar o vale não se mexe')
        confirma_modal()
        ok(saldo_de(2) == 15 and [u for u in por_n(2)['usos'] if u['doc']['id'] == 3][0]['estornado'] == dict(em=iso(HOJE), motivo='pedido excluído'),
           'excluir o pedido devolve o valor ao vale (saldo R$ 15,00), com o motivo "pedido excluído"')
        ok('voltam para o vale VC-2' in pg.inner_text('#confirmModalTexto'), 'e o aviso depois de excluir também diz'); fecha()
        # pedido que nao usou vale: excluir segue como era
        limpar(True); ir(PED_D, '?id=1')
        clic('#linkExcluirPedido'); pg.wait_for_timeout(350)
        ok('vale' not in pg.inner_text('#confirmModalTexto').lower(), 'excluir um pedido que não usou vale não fala em vale')
        fecha()
        # excluir com o vale cancelado: nao volta
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 120, 20, 160, usos=[uso(30, dia(-2), id_=1)])]); ir(PED_D, '?id=1')
        sem = gravados(); sem[0]['cancelado'] = dict(em=iso(HOJE), motivo='T', saldo=90); semear(sem); ir(PED_D, '?id=1')
        clic('#linkExcluirPedido'); pg.wait_for_timeout(350)
        ok('R$ 30,00 do vale VC-1 não voltam: o vale está cancelado' in pg.inner_text('#confirmModalTexto'), 'excluir com o vale cancelado avisa que o valor não volta')
        confirma_modal(); fecha()
        ok(saldo_de(1) == 0 and 'perdido' in por_n(1)['usos'][0], 'e o uso fica como perdido')
        # situacao a mao
        limpar(True); ir(PED_D, '?id=10')
        clic('#linkAlterarSituacao'); pg.wait_for_timeout(350)
        pg.evaluate("document.querySelector('#painelCorpo .sit-opcao[data-sit=\"cancelado\"]').click()"); pg.wait_for_timeout(400)
        t = pg.inner_text('#confirmModalTexto')
        ok('Cancelado' in t and 'R$ 30,00 voltam para o vale VC-3' in t, 'a confirmação de mudar a situação para Cancelado diz "R$ 30,00 voltam para o vale VC-3": %s' % t[-110:])
        confirma_modal()
        ok(saldo_de(3) == 80 and [u for u in por_n(3)['usos'] if u['doc']['id'] == 10][0]['estornado'] == dict(em=iso(HOJE), motivo='pedido cancelado'),
           'mudar a situação para Cancelado à mão devolve o valor ao vale (saldo R$ 80,00), com o motivo "pedido cancelado"')
        ok('voltam para o vale VC-3' in pg.inner_text('#confirmModalTexto'), 'e o aviso diz'); fecha()
        # mudar para outra situacao qualquer nao mexe no vale
        limpar(True); ir(PED_D, '?id=10')
        clic('#linkAlterarSituacao'); pg.wait_for_timeout(350)
        pg.evaluate("document.querySelector('#painelCorpo .sit-opcao[data-sit=\"faturado\"]').click()"); pg.wait_for_timeout(400)
        confirma_modal(); fecha()
        ok(saldo_de(3) == 50, 'mudar a situação para outra que não Cancelado não mexe no vale')
        # saindo de Cancelado o vale NAO volta a ser usado sozinho
        limpar(True); ir(PED_D, '?id=10&editar=1')
        clic('#linkCancelarPedido'); pg.wait_for_timeout(350); clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450); fecha()
        ok(saldo_de(3) == 80 and not visivel('#inputValeUsar'), 'cancelado: o vale voltou (R$ 80,00) e o pedido não oferece o campo')
        clic('#linkAlterarSituacao'); pg.wait_for_timeout(350)
        pg.evaluate("document.querySelector('#painelCorpo .sit-opcao[data-sit=\"aberto\"]').click()"); pg.wait_for_timeout(400)
        confirma_modal(); fecha()
        ok(saldo_de(3) == 80 and visivel('#inputValeUsar') and pg.input_value('#inputValeUsar') == '' and pg.evaluate("valeUsosDoDoc({ tipo: 'pedido', id: 10, rotulo: 'Pedido nº 10' })") == [],
           'tirar o pedido de Cancelado não usa o vale de novo: o campo abre vazio e o saldo segue R$ 80,00')
        ok(pg.locator('#valeDevolvido').count() == 1 and 'O vale deste pedido foi devolvido; para usar de novo, informe o valor e salve' in pg.inner_text('#valeDevolvido'),
           'e o quadro diz que o vale foi devolvido e como usar de novo')
        limpar(True); ir(PED_D, '?id=10&editar=1')
        ok(pg.locator('#valeDevolvido').count() == 0, 'pedido que nunca devolveu vale não tem a frase')

    # ================================================================== [8] lista de Pedidos
    if secao(8, 'Lista de Pedidos: cancelar e excluir em massa devolvem o vale'):
        def confirma_modal():
            if pg.evaluate("document.getElementById('confirmCienteRow').style.display") != 'none':
                clic('#confirmCienteCheckbox')
            if visivel('#campoSenhaModal'):
                pg.fill('#inputSenhaModal', 'x')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)

        def seleciona(ids):
            pg.evaluate("(ids) => { itensSelecionados.clear(); ids.forEach(i => itensSelecionados.add(i)); renderTabela(); }", ids)
            pg.wait_for_timeout(200)

        limpar(True); ir(PED_L)
        seleciona([10, 3])
        clic('#btnCancelarSelecionados'); pg.wait_for_timeout(400)
        t = pg.inner_text('#confirmModalTexto')
        ok('10: R$ 30,00 voltam para o vale VC-3' in t and '3: R$ 15,00 voltam para o vale VC-2' in t, 'cancelar em massa diz o que volta para cada vale: %s' % t[-170:])
        ok(saldo_de(3) == 50 and saldo_de(2) == 0, 'antes de confirmar nada se mexe')
        confirma_modal()
        ok(saldo_de(3) == 80 and saldo_de(2) == 15 and all(u['estornado']['motivo'] == 'pedido cancelado' for v in gravados() for u in v['usos'] if u['doc']['id'] in (3, 10) and 'estornado' in u),
           'cancelar em massa devolve os dois (VC-3 volta a R$ 80,00 e VC-2 a R$ 15,00), com o motivo "pedido cancelado"')
        # excluir em massa: o expedido (10) fica de fora e nao devolve
        limpar(True); ir(PED_L)
        seleciona([10, 3])
        clic('#btnExcluirSelecionados'); pg.wait_for_timeout(400)
        t = pg.inner_text('#confirmModalTexto')
        ok('3: R$ 15,00 voltam para o vale VC-2' in t and 'VC-3' not in t and 'será ignorado' in t, 'excluir em massa diz o que volta e não fala do pedido expedido, que fica de fora: %s' % t[-170:])
        confirma_modal()
        ok(saldo_de(2) == 15 and saldo_de(3) == 50 and [u for u in por_n(2)['usos'] if u['doc']['id'] == 3][0]['estornado']['motivo'] == 'pedido excluído',
           'excluir em massa devolve o vale do pedido excluído (motivo "pedido excluído") e não toca no do expedido')
        # pedido sem vale: nada de vale no texto
        limpar(True); ir(PED_L)
        seleciona([1])
        clic('#btnCancelarSelecionados'); pg.wait_for_timeout(400)
        ok('vale' not in pg.inner_text('#confirmModalTexto').lower(), 'cancelar um pedido que não usou vale não fala em vale')
        pg.evaluate("fecharModalConfirmacao()")

    # ================================================================== [5] pagina do vale
    if secao(5, 'A página do vale: uso estornado riscado com o motivo, e o perdido no vale cancelado'):
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 100, 20, 160,
                     usos=[uso(30, dia(-5), id_=7, estornado=dict(em=iso(dia(-3)), motivo='pedido cancelado')), uso(20, dia(-2), id_=8)]),
                vale(2, 2, 'Rafael Nogueira', '234.567.890-11', 1, 50, 20, 160, usos=[uso(25, dia(-4), id_=9, perdido=dict(em=iso(dia(-1)), motivo='pedido cancelado'))],
                     cancelado=dict(em=iso(dia(-2)), motivo='Teste', saldo=25))])
        ir(VALE_D, '?id=1')
        linhas = pg.evaluate("[...document.querySelectorAll('#corpoUsos tr')].map(tr => [tr.className, ...[...tr.children].map(td => td.textContent.replace(/\\s+/g, ' ').trim())])")
        ok(linhas[0][0] == 'vc-estornado' and 'Pedido nº 7' in linhas[0][2] and 'estornado em %s: pedido cancelado' % br(dia(-3)) in linhas[0][2] and linhas[0][4] == '—',
           'o uso estornado fica na lista, com o motivo: %s' % linhas[0])
        ok(pg.evaluate("getComputedStyle(document.querySelector('#corpoUsos tr.vc-estornado .vc-risca')).textDecorationLine") == 'line-through', 'e riscado')
        ok(linhas[1][0] == '' and linhas[1][4] == 'R$ 80,00', 'o uso que vale mostra o saldo depois (R$ 80,00): o estornado não conta no saldo: %s' % linhas[1])
        dados = pg.inner_text('#corpoDados')
        ok('usado r$ 20,00' in dados.replace('\n', ' ').lower() and 'r$ 80,00' in dados.lower(), 'usado e saldo ignoram o estornado: %s' % dados.replace('\n', ' ')[-130:])
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.children[1].textContent)")
        ok(any('Estornado: R$ 30,00 de Pedido nº 7 voltaram ao vale (pedido cancelado)' in h for h in hist) and not any('Usado: R$ 30,00' in h for h in hist) and any('Usado: R$ 20,00 em Pedido nº 8' in h for h in hist),
           'o histórico não lista o uso estornado como usado: entra o estorno')
        ir(VALE_D, '?id=2')
        linhas = pg.evaluate("[...document.querySelectorAll('#corpoUsos tr')].map(tr => [tr.className, ...[...tr.children].map(td => td.textContent.replace(/\\s+/g, ' ').trim())])")
        ok('valor não voltou: o vale estava cancelado' in linhas[0][2] and linhas[0][0] == '', 'no vale cancelado o uso perdido diz que o valor não voltou: %s' % linhas[0][2])
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.children[1].textContent)")
        ok(any('Perdido: R$ 25,00 de Pedido nº 9 não voltaram' in h for h in hist), 'e o histórico registra a perda')
        ir(VALE_L); pg.evaluate("abrirPainel(1)"); pg.wait_for_timeout(300)
        ok('Pedido nº 8' in pg.inner_text('#drawerCorpo') and 'Pedido nº 7' not in pg.inner_text('#drawerCorpo'), 'o painel da lista não mostra o uso estornado entre os últimos usos')

    # ================================================================== [6] Contas a Receber
    if secao(6, 'Contas a Receber: os títulos do vale, o detalhe só leitura e o título 9 em Crediário'):
        limpar(True); ir(CR_L)
        t = pg.evaluate("TITULOS.filter(t => t.vale).map(t => ({ id: t.id, doc: t.doc, cli: cliDe(t.cliId).nome, valor: t.valor, recebido: t.recebido, forma: t.forma, cat: t.catId, hist: t.hist, venc: t.vencIso, emis: t.emisIso, sit: situacaoDe(t), pedido: t.pedido || 0, rec: t.recebimentos.length, conta: t.recebimentos[0].contaId }))")
        ok(len(t) == 3, 'os três usos de exemplo viram três títulos: %d' % len(t))
        esperado = {9200: ('Pedido nº 16', 'Rafael Nogueira', 25, -28, 'VC-2', 16), 9201: ('Pedido nº 3', 'Rafael Nogueira', 15, -2, 'VC-2', 3), 9300: ('Pedido nº 10', 'Auto Peças Imperatriz Ltda', 30, -11, 'VC-3', 10)}
        for x in sorted(t, key=lambda z: z['id']):
            e = esperado.get(x['id'])
            ok(bool(e) and x['doc'] == e[0] and x['cli'] == e[1] and x['valor'] == e[2] == x['recebido'] and x['venc'] == x['emis'] == iso(dia(e[3])) and x['forma'] == 'Vale-compra' and x['cat'] == 1
               and x['hist'] == 'Pago com vale-compra ' + e[4] and x['sit'] == 'recebida' and x['pedido'] == e[5] and x['conta'] is None,
               'título %s: documento %s, cliente, valor = recebido, data do uso, forma Vale-compra, categoria de venda, "Pago com vale-compra %s", recebido, sem conta' % (x['id'], x['doc'], e[4]))
        pg.fill('#campoBusca', 'vale-compra VC-3'); pg.wait_for_timeout(300)
        ok(pg.locator('#listaTitulos tbody tr[data-id="9300"]').count() == 1, 'na lista o título do vale se acha pela busca')
        ok('Pedido 10' in pg.inner_text('#listaTitulos tbody tr[data-id="9300"]'), 'e a origem leva ao pedido')
        pg.evaluate("document.querySelector('#listaTitulos tbody tr[data-id=\"9300\"]').click()"); pg.wait_for_timeout(350)
        painel = pg.inner_text('#contaCorpo')
        ok('Vale-compra' in painel and 'VC-3' in painel and 'só leitura' in painel and not visivel('#btnBaixarDaConta'), 'o painel da conta mostra o vale e não oferece "Receber": %s' % painel.replace('\n', ' ')[-130:])
        # o titulo 9 deixa de ser vale-troca em aberto
        ok(pg.evaluate("TITULOS.filter(t => t.id === 9)[0].forma") == 'Crediário' and pg.evaluate("situacaoDe(TITULOS.filter(t => t.id === 9)[0])") in ('aberta', 'atrasada') and 'Vale-compra' in pg.evaluate("FORMAS") and 'Vale-troca' not in pg.evaluate("FORMAS"),
           'o título 9 (PV 7) passa para Crediário, continua em aberto, e a lista de formas diz Vale-compra')
        # nada de vale no Caixa
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras') || '[]')") == [], 'ler os títulos do vale não grava nada no Caixa')
        # uso novo vira titulo; estorno cancela
        pg.evaluate("usarVale(1, 1, 40, { tipo: 'pdv', id: 3, rotulo: 'PDV-0003' })"); ir(CR_L)
        n = pg.evaluate("TITULOS.filter(t => t.vale && t.doc === 'PDV-0003').map(t => ({ id: t.id, valor: t.valor, rec: t.recebido, origem: t.origemTexto, cli: cliDe(t.cliId).nome, sit: situacaoDe(t) }))")
        ok(n == [dict(id=9400, valor=40, rec=40, origem='PDV-0003', cli='Marina Duarte', sit='recebida')], 'um uso novo (PDV-0003) vira título 9400, recebido, com a origem PDV-0003: %s' % n)
        pg.fill('#campoBusca', 'PDV-0003'); pg.wait_for_timeout(300)
        ok('PDV-0003' in pg.inner_text('#listaTitulos tbody tr[data-id="9400"]'), 'e a origem aparece na linha')
        pg.evaluate("estornarUsos({ tipo: 'pdv', id: 3, rotulo: 'PDV-0003' }, 'venda cancelada')"); ir(CR_L)
        n = pg.evaluate("TITULOS.filter(t => t.vale && t.doc === 'PDV-0003').map(t => ({ rec: t.recebido, canc: t.cancelado, sit: situacaoDe(t), hist: t.hist }))")
        ok(len(n) == 1 and n[0]['canc'] and n[0]['rec'] == 0 and n[0]['sit'] == 'cancelada' and 'estornado: venda cancelada' in n[0]['hist'], 'uso estornado vira título cancelado, com o motivo: %s' % n)
        # a barra de selecao nao cancela nem exclui titulo de vale
        pg.fill('#campoBusca', ''); pg.evaluate("selTit = [9400]; atualizarBarraSelecao()"); pg.wait_for_timeout(150)
        ok(not visivel('#linkCancelarSelecionadas'), 'selecionar um título de vale não oferece cancelar nem reativar em massa')
        # --- o detalhe e so leitura
        limpar(True); ir(CR_D, '?id=9300')
        aviso = pg.inner_text('#avisoBaixa')
        ok(pg.evaluate("document.getElementById('avisoBaixa').classList.contains('show')") and 'VC-3' in aviso and 'só leitura' in aviso and 'valor muda no pedido ou no vale' in aviso, 'o detalhe do título do vale diz que é só leitura e que o valor muda no pedido ou no vale: %s' % aviso.replace('\n', ' ')[:200])
        ok(pg.get_attribute('#avisoBaixa a', 'href') == '../financas/pagina-financas-vale-compra-detalhe.html?id=3', 'e leva ao vale')
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')") and not visivel('#acoesLeitura') and not visivel('#btnDarBaixa') and not visivel('#btnEditar') and not visivel('#menuMaisAcoes'),
           'sem Dar baixa, sem Editar e sem o menu de cancelar/excluir')
        ok(pg.inner_text('#roForma').strip() == 'Vale-compra' and 'R$ 30,00' in pg.inner_text('#roValor'), 'os dados são os do uso: forma Vale-compra e R$ 30,00')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"recebimentos\"]').click()"); pg.wait_for_timeout(200)
        ok(pg.locator('[data-acao="estornar"]').count() == 0 and 'Vale-compra' in pg.inner_text('#corpoRecebimentos'), 'a aba de recebimentos mostra o recebimento do vale, sem estornar')
        pg.evaluate("document.getElementById('btnEditar').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')"), 'nem forçando o clique de Editar a conta sai da leitura')
        ir(CR_D, '?id=4')
        ok(visivel('#btnDarBaixa') and visivel('#menuMaisAcoes') and not pg.evaluate("document.getElementById('avisoBaixa').classList.contains('show')"), 'um título comum continua com Dar baixa e com o menu (a trava é só do vale)')
        ir(CR_D, '?id=9')
        ok(pg.inner_text('#roForma').strip() == 'Crediário', 'o título 9 no detalhe também está em Crediário')
        ok(pg.evaluate("FORMAS") == ['Dinheiro', 'Pix', 'Cartão de crédito', 'Cartão de débito', 'Boleto', 'Cheque', 'Depósito', 'Crediário', 'Vale-compra', 'Não informada'], 'a lista de formas do detalhe diz Vale-compra: %s' % pg.evaluate("FORMAS"))
        ok(not any(e for e in erros if 'pageerror' in e), 'sem erro de JS')

    # ================================================================== [7] bloco identico e barra de rolagem
    if secao(7, 'O bloco do vale idêntico em todas as cópias e sem barra de rolagem'):
        TODAS = (VALE_L, VALE_D, CLI_D, PDV, PED_D, PED_L, CR_L, CR_D, 'pagina-logistica-devolucao-detalhe.html', 'pagina-financas-comissoes-detalhe.html')
        INI, FIM = '  // ===== VALE-COMPRA: DADOS E REGRAS', '  // ===== FIM DO BLOCO VALE-COMPRA ====='
        blocos = []
        for n in TODAS:
            t = fonte(n)
            blocos.append(t[t.index(INI):t.index(FIM)])
        ok(len(set(blocos)) == 1 and len(blocos[0]) > 8000, 'o bloco é idêntico nas dez cópias (%d caracteres)' % len(blocos[0]))
        ok(all(f in blocos[0] for f in ('function usarVale(', 'function estornarUsos(', 'function valeUsosDoDoc(', 'function valeTodosUsos(', 'function valeDocHref(')), 'e traz o uso do vale: usarVale, estornarUsos e os que leem os usos')
        ok(fonte(CLI_D).replace(blocos[0], '').count('valeGravar(') == 0 and fonte(CLI_D).replace(blocos[0], '').count('usarVale(') == 0, 'o cadastro do cliente continua só lendo o vale')
        for larg in (1280, 1440):
            pg.set_viewport_size({'width': larg, 'height': 900})
            sem_barra = {}
            semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 12345.67, 20, 160)])
            ir(PDV); pg.evaluate("localStorage.removeItem('deskPdv')"); pg.reload(); pg.wait_for_timeout(400)
            clic('#btnAbrirCaixa'); pg.wait_for_timeout(300); escolher('abrirLoja', 1); pg.fill('#abrirTroco', '100'); clic('#btnConfirmarAbertura'); pg.wait_for_timeout(400)
            pg.fill('#qtdProduto', '2'); pg.fill('#buscaProduto', 'MES-140-CZ'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
            clic('#btnCliente'); pg.wait_for_timeout(300); pg.fill('#buscaCliente', 'Marina'); pg.wait_for_timeout(200); clic('#listaClientes .pdv-cli'); pg.wait_for_timeout(300)
            clic('#btnContinuar'); pg.wait_for_timeout(400); clic('#btnUsarVale'); pg.wait_for_timeout(300)
            sem_barra['PDV com o vale na venda'] = pg.evaluate(MEDE)
            limpar(True); ir(PED_D, '?id=10&editar=1'); sem_barra['Pedido com o quadro'] = pg.evaluate(MEDE)
            ir(PED_D, '?id=10'); sem_barra['Pedido em leitura'] = pg.evaluate(MEDE)
            ir(CR_L); sem_barra['Contas a Receber (lista)'] = pg.evaluate(MEDE)
            ir(CR_D, '?id=9300'); sem_barra['Contas a Receber (título do vale)'] = pg.evaluate(MEDE)
            ir(VALE_D, '?id=2'); sem_barra['Página do vale'] = pg.evaluate(MEDE)
            ir(FORMAS_CAD); sem_barra['Formas de Recebimento'] = pg.evaluate(MEDE)
            abrir_vale = pg.evaluate("(() => { const f = FORMAS.filter(f => f.chave === 'valetroca')[0]; document.querySelector('#listaFormas tr[data-id=\"' + f.id + '\"]').click(); return true; })()")
            pg.wait_for_timeout(300); sem_barra['Formas de Recebimento (painel do vale)'] = pg.evaluate(MEDE)
            ruim = dict((k, v) for k, v in sem_barra.items() if v)
            ok(not ruim, 'a %dpx nenhuma das telas mexidas tem barra de rolagem: %s' % (larg, ruim or 'todas limpas'))
        pg.set_viewport_size({'width': 1440, 'height': 900})

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
