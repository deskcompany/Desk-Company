# -*- coding: utf-8 -*-
# A pagina do documento abre o registro clicado (item G3, segunda parte — 13/out/2026).
#
# A primeira parte, dos cinco cadastros, esta em teste_cad_detalhe.py. Aqui entram os documentos:
# a pagina desenhava um exemplo fixo, e qualquer linha clicada abria o mesmo.
#
#   [1] Ordens de Compra: o espelho da pagina e igual a lista;
#   [2] cada ordem abre a si mesma: titulo, fornecedor, deposito, datas, situacao, itens e total;
#   [3] pelo clique: lista, painel e "Abrir ordem completa" chegam na ordem clicada;
#   [4] o que a ordem oferece segue a situacao dela; clonar copia a ordem aberta;
#   [5] a ordem criada em Necessidades de Compra abre com os itens dela;
#   [6] ordem nova, endereco sem id e id que nao existe;
#   [7] Pedidos de Venda: o espelho da pagina e igual a lista, e os itens fecham no total;
#   [8] cada pedido abre a si mesmo, sem acusar falta de saldo nem pedir cadastro do cliente;
#   [9] pelo clique: lista, painel e "Abrir pedido completo"; o cliente leva ao cadastro pelo nome;
#  [10] o clone parte do pedido aberto; a venda de balcao abre; sem id, o exemplo desenhado;
#  [11] Expedicao: "Abrir o romaneio" leva o id do romaneio.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
OC, OC_D = 'pagina-estoque-ordens-compra.html', 'pagina-estoque-ordens-compra-detalhe.html'
PV, PV_D = 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html'
EXP, EXP_D = 'pagina-logistica-expedicao.html', 'pagina-logistica-expedicao-detalhe.html'

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


def br(iso):
    return iso[8:10] + '/' + iso[5:7] + '/' + iso[0:4] if iso else ''


# O que a pagina da ordem mostra.
RETRATO_OC = """() => {
  const rot = (id) => document.querySelector('#' + id + ' .dropdown-select-label').textContent.trim();
  const visivel = (acao) => { const i = document.querySelector('#menuMaisAcoes [data-acao="' + acao + '"]'); return !!i && i.style.display !== 'none'; };
  return {
    h1: document.getElementById('tituloOC').textContent.trim(), numero: document.getElementById('inputNumero').value,
    fornecedor: rot('inputFornecedor'), deposito: rot('inputDeposito'), doc: document.getElementById('fDocNumero').textContent.trim(),
    data: document.getElementById('inputDataCompra').value, previsto: document.getElementById('inputDataPrevista').value,
    situacao: document.getElementById('badgeSituacao').textContent.trim(),
    itens: ITENS.map(i => [i.nome, i.sku, i.qtd, i.un, i.preco]), linhas: document.getElementById('corpoItens').children.length,
    total: paraNumero(document.getElementById('totGeral').textContent.replace('R$', '')),
    receber: visivel('receber'), parcial: visivel('parcial'), clonar: visivel('clonar'),
    trilha: document.getElementById('breadcrumb').textContent.replace(/\\s+/g, ' ').trim()
  };
}"""

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, query=''):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)

    ir(OC); pg.evaluate("localStorage.removeItem('deskOrdensGeradas'); localStorage.removeItem('deskParametros')")
    ir(OC)
    ORDENS, ITENS_OC = pg.evaluate('ORDENS'), pg.evaluate('ITENS_OC')
    DEPOSITOS, SIT = pg.evaluate('DEPOSITOS'), pg.evaluate('SITUACAO_LABEL')

    if secao(1, 'Ordens de Compra: o espelho da página é igual à lista'):
        ir(OC_D)
        ok(pg.evaluate('ORDENS_DA_LISTA') == ORDENS and len(ORDENS) == 14, 'ORDENS_DA_LISTA repete as 14 ordens da lista, campo a campo')
        ok(pg.evaluate('ITENS_DA_LISTA') == ITENS_OC and len(ITENS_OC) == 4, 'ITENS_DA_LISTA repete os itens das 4 ordens que a lista tem com itens')
        nomes = pg.evaluate("Object.keys(FORNECEDORES).map(k => FORNECEDORES[k].nome)")
        ok(not [o['fornecedor'] for o in ORDENS if o['fornecedor'] not in nomes], 'todo fornecedor da lista existe na página da ordem: %s' % sorted(set(o['fornecedor'] for o in ORDENS) - set(nomes)))
        fora = []
        for o in ORDENS:
            itens = ITENS_OC.get(str(o['id']))
            if itens and abs(sum(i['qtd'] * i['preco'] for i in itens) + o.get('frete', 0) - o.get('desconto', 0) - o['total']) > 0.005:
                fora.append(o['numero'])
        ok(not fora, 'na lista, itens mais frete menos desconto fecham no total de cada ordem que tem itens: %s' % fora)

    if secao(2, 'Cada ordem abre a si mesma'):
        ruins, vistos = [], {}
        for o in ORDENS:
            ir(OC_D, '?id=%d' % o['id'])
            r = vistos[o['id']] = pg.evaluate(RETRATO_OC)
            itens = ITENS_OC.get(str(o['id']))
            quer = dict(h1='Ordem de Compra nº %d' % o['numero'], numero=str(o['numero']), fornecedor=o['fornecedor'], deposito=DEPOSITOS[str(o['dep'])],
                        data=br(o['data']), previsto=br(o['previsto']), situacao=SIT[o['situacao']],
                        itens=[[i['nome'], i['sku'], i['qtd'], i['un'], i['preco']] for i in itens] if itens else [['Item de exemplo', '', 1, 'UN', o['total']]],
                        receber=o['situacao'] in ('aberto', 'andamento'), parcial=o['situacao'] in ('aberto', 'andamento'), clonar=True)
            for k, v in quer.items():
                if r[k] != v:
                    ruins.append('nº %d, %s: %r, e a lista diz %r' % (o['numero'], k, r[k], v))
            if abs(r['total'] - o['total']) > 0.005 or r['linhas'] != len(r['itens']) or r['doc'] in ('', '—'):
                ruins.append('nº %d: total %s (lista %s), %d linhas, documento %r' % (o['numero'], r['total'], o['total'], r['linhas'], r['doc']))
        ok(not ruins, 'as 14 ordens abrem com o que a lista diz delas (fornecedor, depósito, datas, situação, itens e total): %s' % ruins[:3])
        ok(len(set(v['h1'] for v in vistos.values())) == 14, 'são 14 títulos diferentes, e não a ordem nº 2 quatorze vezes')
        ok(sum(1 for o in ORDENS if str(o['id']) in ITENS_OC) == 4 and sum(1 for o in ORDENS if o['situacao'] in ('atendida', 'cancelada')) >= 4,
           'a conferência passou por ordem com itens e sem itens, e por ordem que espera mercadoria e que não espera')
        ir(OC)
        painel = pg.evaluate("""(ids) => ids.map(id => { abrirPreview(id); return Array.from(document.querySelectorAll('#eventDrawer .mov-item')).map(m => m.querySelector('.mov-qtd').textContent.trim()); })""",
                             [o['id'] for o in ORDENS if str(o['id']) not in ITENS_OC][:2])
        sem = [o for o in ORDENS if str(o['id']) not in ITENS_OC][:2]
        ok(len(painel) == 2 and all(len(x) == 1 for x in painel) and [x[0] for x in painel] == [pg.evaluate("(n) => fmtMoeda(n)", o['total']) for o in sem], 'no painel da lista, o item de exemplo da ordem sem itens leva o total dela: %s' % painel)

    if secao(3, 'Pelo clique: lista, painel e o botão de abrir'):
        for alvo in (ORDENS[0], ORDENS[9]):
            ir(OC)
            pg.evaluate("(id) => abrirPreview(id)", alvo['id']); pg.wait_for_timeout(250)
            pg.evaluate("document.getElementById('btnAbrirDetalhe').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            r = pg.evaluate(RETRATO_OC)
            ok(pg.url.split('/')[-1] == OC_D + '?id=%d' % alvo['id'] and r['h1'] == 'Ordem de Compra nº %d' % alvo['numero'] and r['fornecedor'] == alvo['fornecedor'],
               'cliquei na ordem nº %d (%s) e a página abriu "%s", de %s' % (alvo['numero'], alvo['fornecedor'], r['h1'], r['fornecedor']))
        ir('pagina-estoque-conferencia.html')
        oc = pg.evaluate('NOTA.oc')
        pg.evaluate("document.querySelector('[data-acao=\"oc\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(oc and oc != 2 and pg.url.split('/')[-1] == OC_D + '?id=%s' % oc and pg.evaluate(RETRATO_OC)['numero'] == str(oc),
           'da Conferência, "ver a ordem de compra" abre a ordem nº %s, que é a da nota' % oc)

    if secao(4, 'O que a ordem oferece segue a situação; clonar copia a ordem aberta'):
        atendida = [o for o in ORDENS if o['situacao'] == 'atendida'][0]
        ir(OC_D, '?id=%d' % atendida['id'])
        antes = pg.evaluate(RETRATO_OC)
        pg.evaluate("SITUACAO = 'aberto'; aplicarSituacao()")
        ok(not antes['receber'] and not antes['parcial'] and pg.evaluate(RETRATO_OC)['receber'], 'ordem atendida não oferece "Receber mercadorias"; voltando para em aberto, oferece de novo')
        ir(OC_D, '?id=4')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"clonar\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        r = pg.evaluate(RETRATO_OC)
        q = pg.url.split('?')[-1]
        ok('clonar=1' in q and 'id=4' in q and r['h1'] == 'Nova ordem de compra' and r['numero'] == '' and r['fornecedor'] == ORDENS[3]['fornecedor']
           and [i[1] for i in r['itens']] == [i['sku'] for i in ITENS_OC['4']] and 'Cópia da nº 4' in r['trilha'] and r['situacao'] == SIT['aberto'],
           'clonar a ordem nº 4 abre uma ordem nova com o fornecedor e os itens da nº 4: %s, %s' % (r['fornecedor'], [i[1] for i in r['itens']]))

    if secao(5, 'A ordem criada em Necessidades de Compra abre com os itens dela'):
        gerada = {'numero': 15, 'fornecedor': 'Luminárias Brasil', 'data': '2026-10-13', 'previsto': '2026-10-20', 'dep': 2, 'total': 1724.00,
                  'itens': [{'nome': 'Luminária LED Ajustável', 'sku': 'LUM-LED-004', 'qtd': 20, 'un': 'UN', 'preco': 86.20}]}
        ir(OC); pg.evaluate("(o) => localStorage.setItem('deskOrdensGeradas', JSON.stringify([o]))", gerada)
        ir(OC)
        ok(pg.evaluate("ORDENS.some(o => o.numero === 15)"), 'a ordem nº 15, gravada como Necessidades de Compra grava, entra na lista')
        ir(OC_D, '?id=15')
        r = pg.evaluate(RETRATO_OC)
        ok(r['h1'] == 'Ordem de Compra nº 15' and r['fornecedor'] == 'Luminárias Brasil' and r['itens'] == [['Luminária LED Ajustável', 'LUM-LED-004', 20, 'UN', 86.2]]
           and abs(r['total'] - 1724.00) < 0.005 and r['situacao'] == SIT['aberto'] and r['previsto'] == '20/10/2026',
           'e a página dela abre a nº 15, da Luminárias Brasil, com o item e o total: %s' % r['itens'])
        pg.evaluate("localStorage.removeItem('deskOrdensGeradas')")

    if secao(6, 'Ordem nova, endereço sem id e id que não existe'):
        ir(OC_D, '?novo=1')
        r = pg.evaluate(RETRATO_OC)
        ok(r['h1'] == 'Nova ordem de compra' and r['numero'] == '' and r['itens'] == [] and r['fornecedor'] == 'Selecione o fornecedor' and r['previsto'] == '',
           'ordem nova continua abrindo em branco')
        ir(OC_D); sem_id = pg.evaluate(RETRATO_OC)
        ir(OC_D, '?id=2'); com_2 = pg.evaluate(RETRATO_OC)
        ir(OC_D, '?id=99999'); fora = pg.evaluate(RETRATO_OC)
        ok(sem_id == com_2 == fora and com_2['h1'] == 'Ordem de Compra nº 2', 'sem id, ou com um que não existe, abre a ordem nº 2, como antes')
        ir(OC_D, '?id=11&editar=1'); pg.wait_for_timeout(250)
        tem = pg.evaluate("typeof camposAlterados === 'function'")
        ok((not tem) or pg.evaluate('camposAlterados()') == 0, 'abrir a ordem nº 11 não deixa alteração pendente no rodapé')

    # O que a pagina do pedido mostra.
    RETRATO_PV = """() => {
      const rot = (id) => document.querySelector('#' + id + ' .dropdown-select-label').textContent.trim();
      const v = (id) => document.getElementById(id).value;
      const some = (id) => { const e = document.getElementById(id); return !e || e.style.display === 'none' || e.offsetParent === null; };
      return {
        h1: document.getElementById('tituloPedido').textContent.trim(), numero: v('inputNumero'), cliente: v('inputCliente'), doc: v('inputDoc'),
        loja: rot('inputLoja'), vendedor: rot('inputVendedor'), data: v('inputDataVenda'), previsto: v('inputPrevisto'),
        situacao: document.getElementById('badgeSituacao').textContent.trim(),
        itens: ITENS.map(i => [i.nome, i.sku, i.qtd, i.un, i.precoLista]), linhas: document.getElementById('corpoItens').children.length,
        total: paraNumero(document.getElementById('totGeral').textContent.replace('R$', '')),
        semSaldo: document.getElementById('erroSaldo').classList.contains('show') || document.querySelectorAll('#corpoItens tr.linha-sem-saldo').length > 0,
        pedeCadastro: document.getElementById('blocoCliente').classList.contains('aberto'), atraso: !some('avisoAtraso'),
        contasAbertas: CLIENTE_FINANCEIRO.aberto.length, ultimas: ULTIMAS_VENDAS.length
      };
    }"""
    PICA = "(l) => l.filter(p => !p.pdv).map(p => [p.id, p.numero, p.dv, p.dp, p.cliente, p.doc, p.loja, p.vend, p.total, p.situacao, p.pago, p.frete || 0, p.desconto || 0, p.ind || null])"
    ir(PV); pg.evaluate("['deskPdv', 'deskCaixaExtras'].forEach(k => localStorage.removeItem(k))")
    ir(PV)
    PEDIDOS, ITENS_PV = pg.evaluate('PEDIDOS'), pg.evaluate('ITENS_PEDIDO')
    LOJAS, ROTULO_SIT = pg.evaluate('LOJAS'), pg.evaluate("Object.fromEntries(SITUACOES.map(s => [s.id, s.rotulo]))")
    EXEMPLO_PV = 'Tech Solutions Imperatriz Ltda'

    if secao(7, 'Pedidos de Venda: o espelho da página é igual à lista'):
        da_lista = pg.evaluate(PICA.replace('(l) =>', '((l) =>') + ')(PEDIDOS)')
        vend = pg.evaluate('VENDEDORES')
        ir(PV_D)
        ok(pg.evaluate(PICA.replace('(l) =>', '((l) =>') + ')(PEDIDOS_DA_LISTA)') == da_lista and len(da_lista) == 16, 'PEDIDOS_DA_LISTA repete os 16 pedidos da lista, campo a campo')
        ok(pg.evaluate('ITENS_DA_LISTA') == ITENS_PV and len(ITENS_PV) == 4 and pg.evaluate('VENDEDORES_DA_LISTA') == vend,
           'ITENS_DA_LISTA repete os itens dos 4 pedidos que a lista tem com itens, e os vendedores são os mesmos')
        fora = []
        for p in PEDIDOS:
            itens = ITENS_PV.get(str(p['id']))
            if itens and abs(sum(i['qtd'] * i['preco'] for i in itens) + p.get('frete', 0) - p.get('desconto', 0) - p['total']) > 0.005:
                fora.append(p['numero'])
        ok(not fora, 'na lista, itens mais frete menos desconto fecham no total de cada pedido que tem itens: %s' % fora)
        skus = sorted(set(i['sku'] for itens in ITENS_PV.values() for i in itens))
        ok(not [s for s in skus if not pg.evaluate("(s) => !!produtoDe(s)", s)], 'todo produto dos pedidos da lista existe no catálogo da página: %s' % [s for s in skus if not pg.evaluate("(s) => !!produtoDe(s)", s)])

    if secao(8, 'Cada pedido abre a si mesmo'):
        ruins, vistos = [], {}
        for p in PEDIDOS:
            ir(PV_D, '?id=%d' % p['id'])
            r = vistos[p['id']] = pg.evaluate(RETRATO_PV)
            itens = ITENS_PV.get(str(p['id']))
            quer = dict(h1='Pedido de Venda nº %d' % p['numero'], numero=str(p['numero']), cliente=p['cliente'], doc=p['doc'], loja=LOJAS[str(p['loja'])],
                        vendedor=p['vendedor'] or 'Sem vendedor', data=br(p['data']), previsto=br(p['previsto']), situacao=ROTULO_SIT[p['situacao']],
                        itens=[[i['nome'], i['sku'], i['qtd'], i['un'], i['preco']] for i in itens] if itens else [['Item de exemplo', '', 1, 'UN', p['total']]],
                        semSaldo=False, pedeCadastro=False)
            for k, v in quer.items():
                if r[k] != v:
                    ruins.append('nº %d, %s: %r, e a lista diz %r' % (p['numero'], k, r[k], v))
            if abs(r['total'] - p['total']) > 0.005 or r['linhas'] != len(r['itens']):
                ruins.append('nº %d: total %s (lista %s), %d linhas' % (p['numero'], r['total'], p['total'], r['linhas']))
            if p['cliente'] != EXEMPLO_PV and (r['atraso'] or r['contasAbertas'] or r['ultimas']):
                ruins.append('nº %d: mostra conta em atraso ou venda anterior do cliente do exemplo' % p['numero'])
        ok(not ruins, 'os 16 pedidos abrem com o que a lista diz deles (cliente, loja, vendedor, datas, situação, itens e total): %s' % ruins[:3])
        ok(len(set(v['h1'] for v in vistos.values())) == 16, 'são 16 títulos diferentes, e não o pedido nº 2 dezesseis vezes')
        ok(len(set(p['situacao'] for p in PEDIDOS)) >= 8 and sum(1 for p in PEDIDOS if str(p['id']) not in ITENS_PV) == 12,
           'a conferência passou por pedido com itens e sem itens, em %d situações diferentes' % len(set(p['situacao'] for p in PEDIDOS)))
        ir(PV)
        sem = [p for p in PEDIDOS if str(p['id']) not in ITENS_PV][:2]
        painel = pg.evaluate("(ids) => ids.map(id => itensDe(id).map(i => [i.nome, i.preco]))", [p['id'] for p in sem])
        ok(painel == [[['Item de exemplo', p['total']]] for p in sem], 'no painel da lista, o item de exemplo do pedido sem itens leva o total dele: %s' % painel)

    if secao(9, 'Pelo clique: lista, painel e o botão de abrir'):
        for alvo in (PEDIDOS[15], PEDIDOS[4]):
            ir(PV)
            pg.evaluate("(id) => abrirPreview(id)", alvo['id']); pg.wait_for_timeout(250)
            pg.evaluate("document.getElementById('btnAbrirPedido').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            r = pg.evaluate(RETRATO_PV)
            ok(pg.url.split('/')[-1] == PV_D + '?id=%d' % alvo['id'] and r['h1'] == 'Pedido de Venda nº %d' % alvo['numero'] and r['cliente'] == alvo['cliente'],
               'cliquei no pedido nº %d (%s) e a página abriu "%s", de %s' % (alvo['numero'], alvo['cliente'], r['h1'], r['cliente']))
        ir(PV_D, '?id=3')
        pg.evaluate("document.getElementById('linkDadosCliente').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok('pagina-cadastros-clientes-detalhe.html?nome=' in pg.url and pg.evaluate("document.querySelector('.main h1').textContent.trim()") == PEDIDOS[2]['cliente'],
           'do pedido nº 3, "dados do cliente" abre o cadastro de %s' % PEDIDOS[2]['cliente'])

    if secao(10, 'Clone, venda de balcão e o exemplo desenhado'):
        ir(PV_D, '?id=6')
        pg.evaluate("document.getElementById('linkClonarVenda').click()"); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
        q = pg.url.split('?')[-1]
        ok('clonar=6' in q and 'id=6' in q, 'com o pedido nº 6 aberto, "Clonar venda" leva o número e o id dele: %s' % q)
        r = pg.evaluate(RETRATO_PV)
        ok(r['h1'] == 'Novo pedido de venda — clonado do nº 6' and r['numero'] == '' and r['cliente'] == PEDIDOS[5]['cliente']
           and [i[1] for i in r['itens']] == [i['sku'] for i in ITENS_PV['6']] and r['situacao'] == ROTULO_SIT['aberto'],
           'o clone do nº 6 abre um pedido novo com o cliente e os itens do nº 6: %s, %s' % (r['cliente'], [i[1] for i in r['itens']]))
        venda = {'numero': 1, 'quando': '2026-10-13T10:30:00', 'clienteNome': 'Consumidor final', 'clienteDoc': '', 'lojaId': 1, 'vendedorNome': 'Marina Costa',
                 'total': 129.80, 'situacao': 'entregue', 'recebimentos': [{'destino': 'conta'}],
                 'itens': [{'nome': 'Produto do balcão', 'sku': 'BALCAO-01', 'qtd': 2, 'un': 'UN', 'preco': 64.90}]}
        ir(PV); pg.evaluate("(v) => localStorage.setItem('deskPdv', JSON.stringify({ turno: { vendas: [v] } }))", venda)
        ir(PV)
        ok(pg.evaluate("PEDIDOS.some(p => p.id === 900001 && p.numero === 'PDV-0001')"), 'a venda de balcão PDV-0001, gravada como o PDV grava, entra na lista')
        ir(PV_D, '?id=900001')
        r = pg.evaluate(RETRATO_PV)
        ok(r['h1'] == 'Pedido de Venda nº PDV-0001' and r['cliente'] == 'Consumidor final' and r['itens'] == [['Produto do balcão', 'BALCAO-01', 2, 'UN', 64.9]]
           and abs(r['total'] - 129.80) < 0.005 and r['situacao'] == ROTULO_SIT['entregue'] and r['data'] == '13/10/2026' and not r['semSaldo'],
           'e a página dela abre a PDV-0001, com o item e o total, sem acusar falta de saldo: %s' % r['itens'])
        pg.evaluate("localStorage.removeItem('deskPdv')")
        ir(PV_D); sem_id = pg.evaluate(RETRATO_PV)
        ir(PV_D, '?id=99999'); fora = pg.evaluate(RETRATO_PV)
        ok(sem_id == fora and sem_id['h1'] == 'Pedido de Venda nº 2' and [i[1] for i in sem_id['itens']] == ['NTB-PRO-14', 'TEC-MEC-006', 'CAB-HDM-009'] and sem_id['contasAbertas'] == 3,
           'sem id, ou com um que não existe, abre o exemplo desenhado na página, com as contas do cliente dele')
        ir(PV_D, '?novo=1'); r = pg.evaluate(RETRATO_PV)
        ok(r['h1'] == 'Novo pedido de venda' and r['cliente'] == '' and r['numero'] == '', 'pedido novo continua abrindo em branco')
        ir(PV_D, '?id=2&editar=1')
        pg.evaluate("(() => { const i = document.querySelector('#corpoItens input[data-campo=\"qtd\"]'); i.value = '9999'; i.dispatchEvent(new Event('input', { bubbles: true })); })()")
        pg.wait_for_timeout(200)
        ok(pg.evaluate(RETRATO_PV)['semSaldo'], 'num pedido da lista, pedir mais do que existe continua acusando falta de saldo')

    if secao(11, 'Expedição: "Abrir o romaneio" leva o id'):
        ir(EXP)
        roms = pg.evaluate("ROMANEIOS.map(r => r.id)")
        hrefs = pg.evaluate("(ids) => ids.map(id => { abrirResumo(id); const a = document.getElementById('btnAbrirRomaneio'); return a ? a.getAttribute('href') : null; })", roms)
        ok(len(roms) >= 5 and hrefs == ['../logistica/%s?id=%s' % (EXP_D, r) for r in roms], 'o botão do painel leva o id de cada um dos %d romaneios: %s' % (len(roms), hrefs[:2]))
        tem = pg.evaluate("ROMANEIOS.map(r => r.id)")
        ir(EXP_D, '?id=ROM-0190')
        ok('ROM-0190' in tem and pg.evaluate("document.querySelector('.main h1').textContent.replace(/\\s+/g, ' ').trim()").startswith('Romaneio ROM-0190'),
           'e o ROM-0190 abre a página do ROM-0190, e não a do romaneio padrão')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
