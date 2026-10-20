# -*- coding: utf-8 -*-
# Vale-compra, entrega 3: o vale nasce da Devolucao e do pagamento de Comissao de afiliado (barganha aprovada pelo usuario em 20/out/2026).
#
# Decisoes dele (nao se reabrem): (1) Devolucao: o vale nasce AO FINALIZAR, com o total da devolucao, na loja do pedido; escolher a forma so anota.
# (2) Devolucao finalizada com vale e depois cancelada: vale intacto e cancelado junto; vale ja usado, mesmo em parte, IMPEDE cancelar a devolucao.
# (3) Comissao: SO AFILIADO recebe em vale (vendedor e funcionario: comissao e salario, em dinheiro). (4) Sem bonus: R$ 100 de comissao = R$ 100 de
# vale, na loja da comissao. (5) A comissao paga em vale aparece em Contas a Pagar JA PAGA, forma Vale-compra, so leitura, sem saida do Caixa.
#
#   [1] O bloco comum: emitirVale (valida, trava duplicidade, validade de Configuracoes, nao grava se falha), valeDaOrigem e cancelarValeDaOrigem;
#   [2] Devolucao: a opcao habilitada ou desabilitada pelos 4 motivos, finalizar gera o vale, o link nos dois sentidos, recarregar nao finaliza
#       de novo, finalizar com o vale falhando nao finaliza, cancelar (vale intacto, vale usado, vale cancelado a mao);
#   [3] Comissoes Afiliados: o vendedor nao ve a opcao, o afiliado ve, o pagamento nasce pago e gera o vale certo, o historico, cancelar o pagamento;
#   [4] Contas a Pagar: o titulo ja pago, so leitura, fora do Caixa e do extrato, a selecao em massa nao toca;
#   [5] As outras telas que leem os pagamentos (vencidos, cancelar sozinho, tela inicial) e a barra de rolagem.
from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import os as _os, glob as _g, sys, json
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
DEV_L, DEV_D = 'pagina-logistica-devolucao.html', 'pagina-logistica-devolucao-detalhe.html'
COM_L, COM_D = 'pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html'
CP_L, CP_D, CAIXA = 'pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html', 'pagina-financas-caixa.html'
VALE_L, VALE_D, CLI_D, INICIO = 'pagina-financas-vale-compra.html', 'pagina-financas-vale-compra-detalhe.html', 'pagina-cadastros-clientes-detalhe.html', 'pagina-inicio-boas-vindas.html'
FORMAS_CAD = 'pagina-configuracoes-formas-recebimento.html'
CHAVES_LOCAIS = ['deskValesCompra', 'deskValesCompraExemplo', 'deskParametros', 'deskLog', 'deskCaixaExtras', 'deskComissoesPagas', 'deskComissoesExemplo',
                 'deskAfiliados', 'deskSaques', 'deskComissoesLanc', 'deskComissoesAjustes', 'deskDevolucoes']
PADRAO = {}   # confirmacoes de senha no padrao do catalogo: finalizar e cancelar a devolucao pedem senha, e e a senha ligada que abre o painel com o texto do que vai acontecer

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


MEDE = """() => { const r = []; document.querySelectorAll('.estoque-table-wrap, .table-wrap, .com-tabela, .cp-tabela').forEach(w => {
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
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.getClientRects().length > 0 && getComputedStyle(e).display !== 'none'; }", sel)

    def limpar(com_vales=False, **params):
        """Zera o armazenamento. Sem exemplo de vales (lista vazia com a marca) e sem exemplo de pagamentos de comissao, para os numeros partirem de VC-1 e COM-1."""
        if pg.url == 'about:blank':
            ir(VALE_L)
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        if not com_vales:
            pg.evaluate("localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [] })); localStorage.setItem('deskValesCompraExemplo', '1')")
        pg.evaluate("localStorage.setItem('deskComissoesExemplo', '1')")
        param(**params)

    def param(**params):
        d = dict(confirmacoes=PADRAO)
        d.update(params)
        pg.evaluate("(d) => localStorage.setItem('deskParametros', JSON.stringify(d))", d)

    def gravados():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskValesCompra') || '{}').vales || [])")

    def pagamentos():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskComissoesPagas') || '{}').pagamentos || [])")

    def modal():
        return pg.evaluate("document.getElementById('confirmModal').classList.contains('open') ? document.getElementById('confirmModalTexto').textContent : ''")

    def confirmar():
        """Confirma o painel aberto, com a senha quando ele pede, e espera o resultado."""
        if pg.evaluate("(() => { const r = document.getElementById('campoSenhaModal'); return !!r && r.classList.contains('on'); })()"):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)

    def fechar_modal():
        if pg.evaluate("document.getElementById('confirmModal').classList.contains('open')"):
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)

    def tenta(js):
        return pg.evaluate("(() => { try { return { v: (%s) }; } catch (e) { return { erro: e.message }; } })()" % js)

    # ================================================================== [1] o bloco
    if secao(1, 'O bloco comum: emitirVale, valeDaOrigem e cancelarValeDaOrigem'):
        limpar(); ir(VALE_L)
        cli = dict(clienteId=12, cliente='Bruno Carvalho', doc='890.123.456-77', loja=1, origem='devolucao', valor=100,
                   ref=dict(tipo='devolucao', id=4, texto='Devolução DV-0009', href='../logistica/pagina-logistica-devolucao-detalhe.html?id=4'))

        def emitir(**mud):
            d = dict(cli); d.update(mud)
            return tenta("emitirVale(%s)" % json.dumps(d))

        for rotulo, mud in (('valor zero', dict(valor=0)), ('valor negativo', dict(valor=-5)), ('loja fora das que emitem vale (4 Desk Flash)', dict(loja=4)),
                            ('sem cliente no cadastro', dict(clienteId=None)), ('sem o documento de origem', dict(ref=None))):
            r = emitir(**mud)
            ok('erro' in r and len(gravados()) == 0, 'emitir com %s lança erro e não grava nada: %s' % (rotulo, r.get('erro')))
        r = emitir()
        v = r.get('v') or {}
        ok(v.get('n') == 1 and v.get('valor') == 100 and v.get('loja') == 1 and v.get('clienteId') == 12 and v.get('origem') == 'devolucao' and v.get('emitido') == iso(HOJE)
           and v.get('usos') == [] and v.get('reativacoes') == [] and v.get('cancelado') is None, 'emite o VC-1 com cliente, loja, origem, emissão de hoje, sem usos nem reativações: %s' % v)
        ok(v.get('venc') == iso(dia(180)), 'o vencimento é hoje mais 180 dias, o prazo de fábrica: %s' % v.get('venc'))
        ok(v.get('ref') == cli['ref'], 'a ref leva tipo, id, texto e href')
        r = emitir()
        ok('erro' in r and len(gravados()) == 1, 'emitir de novo pelo mesmo documento lança erro e não grava um segundo vale (trava de duplicidade): %s' % r.get('erro'))
        r = emitir(ref=dict(tipo='comissao', id=4, texto='Comissão COM-4', href='x'), origem='comissao', loja=2)
        ok(r.get('v', {}).get('n') == 2, 'outro tipo de documento com o mesmo id não é duplicidade; o n é o seguinte (VC-2)')
        ok(pg.evaluate("valeDaOrigem('devolucao', 4).n") == 1 and pg.evaluate("valeDaOrigem('comissao', '4').n") == 2 and pg.evaluate("valeDaOrigem('devolucao', 99)") is None,
           'valeDaOrigem acha o vale pelo tipo e pelo id (texto ou número) e devolve null quando não há')
        # cancelar
        r = tenta("cancelarValeDaOrigem('devolucao', 4, 'devolução cancelada')")
        ok(r.get('v', {}).get('cancelado') == dict(em=iso(HOJE), motivo='devolução cancelada', saldo=100), 'cancelar o vale intacto grava { em: hoje, motivo, saldo: o saldo que restava }: %s' % r)
        ok(gravados()[0]['cancelado'] is not None and gravados()[1]['cancelado'] is None, 'e só esse vale foi cancelado')
        r = emitir()
        ok(r.get('v', {}).get('n') == 3, 'depois de cancelado, o documento pode emitir outro vale (a trava só vale para o vale não cancelado): VC-%s' % r.get('v', {}).get('n'))
        ok(pg.evaluate("valeDaOrigem('devolucao', 4).n") == 3, 'e valeDaOrigem passa a achar o mais novo')
        pg.evaluate("usarVale(12, 1, 30, { tipo: 'pedido', id: 7, rotulo: 'Pedido nº 7' })")
        r = tenta("cancelarValeDaOrigem('devolucao', 4, 'devolução cancelada')")
        ok('erro' in r and 'R$ 30,00' in r['erro'] and pg.evaluate("valeLer().filter(v => v.n === 3)[0].cancelado") is None,
           'vale já usado, mesmo em parte, não se cancela: lança erro com o valor usado e o vale fica como estava: %s' % r.get('erro'))
        r = tenta("cancelarValeDaOrigem('devolucao', 99, 'x')")
        ok(r.get('v') is None and 'erro' not in r, 'sem vale daquele documento não faz nada')
        # validade vem de Configuracoes, lida na hora de emitir
        limpar(); param(valeCompraValidadeDias=45, confirmacoes=PADRAO); ir(VALE_L)
        r = emitir()
        ok(r.get('v', {}).get('venc') == iso(dia(45)), 'com a validade de Configurações em 45 dias o vale vence em hoje mais 45: %s' % r.get('v', {}).get('venc'))
        limpar(); param(valeCompraValidadeDias=0, confirmacoes=PADRAO); ir(VALE_L)
        ok(emitir().get('v', {}).get('venc') == iso(dia(180)), 'prazo inválido em Configurações cai no de fábrica, 180 dias')
        # o armazenamento falha: nada de vale
        limpar(); ir(VALE_L)
        pg.evaluate("window.__setItem = Storage.prototype.setItem; Object.defineProperty(Storage.prototype, 'setItem', { configurable: true, writable: true, value: function (k, v) { if (k === 'deskValesCompra') throw new Error('cheio'); return window.__setItem.apply(this, arguments); } })")
        r = emitir()
        pg.evaluate("Object.defineProperty(Storage.prototype, 'setItem', { value: window.__setItem, configurable: true, writable: true })")
        ok('erro' in r and len(gravados()) == 0, 'se não dá para gravar, emitirVale lança erro e não deixa vale pela metade: %s' % r.get('erro'))

    # ================================================================== [2] Devolucao
    if secao(2, 'Devolução: a opção, finalizar gera o vale, os links, recarregar, cancelar'):
        def forma_vale_e_salva():
            """Escolhe Vale-compra no dropdown da forma e salva (so anota)."""
            clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(150)
            pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').click()"); pg.wait_for_timeout(300)
            clic('#btnSalvar'); pg.wait_for_timeout(300)
            if modal(): confirmar()

        def finalizar_em_vale(prazo=None):
            limpar(**({'valeCompraValidadeDias': prazo} if prazo else {})); ir(DEV_D, '?id=4')
            forma_vale_e_salva()
            pg.evaluate("finalizar()"); pg.wait_for_timeout(300)
            txt = modal()
            confirmar()
            return txt

        # ---- 2a. a opcao pelos quatro motivos
        limpar(); ir(DEV_D, '?id=4')
        ok(pg.evaluate("motivoSemVale(DEV)") == '' and not pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').classList.contains('item-indisponivel')"),
           'DV-0009 (Bruno Carvalho, do cadastro, Desk Shope, R$ 414,80): a opção Vale-compra está habilitada')
        ok(pg.evaluate("formaDe('valetroca').rotulo") == 'Vale-compra' and 'vale-compra para o cliente, na loja do pedido' in pg.evaluate("formaDe('valetroca').nota") and pg.evaluate("FORMAS.filter(f => f.reservado).length") == 0,
           'a forma chama Vale-compra, a nota diz "gera um vale-compra para o cliente, na loja do pedido" e nada é reservado')
        ok('vale-troca' not in pg.inner_text('body').lower() and 'vales-troca' not in pg.inner_text('body').lower() and 'submódulo' not in pg.inner_text('body').lower(), 'o nome Vale-troca e o aviso do submódulo que não existia saíram da tela')
        ok(pg.evaluate("FORMA_VALE") == dict(chave='valetroca', nome='Vale-compra', ativo=True), 'o espelho da forma (chave, nome, ativo) é igual ao de Formas de Recebimento')
        ir(FORMAS_CAD)
        ok(pg.evaluate("FORMAS.filter(f => f.chave === 'valetroca')[0].ativo") is True, 'e Formas de Recebimento tem a forma habilitada')
        ir(DEV_D, '?id=4')
        motivos = [
            ('forma desabilitada em Formas de Recebimento', "FORMA_VALE.ativo = false", 'desabilitada'),
            ('cliente fora do cadastro (Mariana Rocha)', "DEV.vendaId = 1", 'cadastro de clientes'),
            ('loja que não emite vale (Desk Flash)', "vendaDe(DEV.vendaId).loja = 4", 'Desk Flash não emite'),
            ('total a devolver zero', "DEV.itens.forEach(i => { i.qtd = 0; }); DEV.frete = 0", 'zero'),
        ]
        for rotulo, js, trecho in motivos:
            ir(DEV_D, '?id=4')
            pg.evaluate("(() => { %s; montarMenuForma(); pintarValores(); })()" % js)
            sem = pg.evaluate("motivoSemVale(DEV)")
            ok(trecho in sem, 'motivo "%s": a tela sabe o porquê: %s' % (rotulo, sem))
            ok(trecho in pg.inner_text('#hintForma') and pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').classList.contains('item-indisponivel')"),
               'e o hint da forma diz o motivo, e a opção fica marcada como indisponível')
            clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(120)
            pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').click()"); pg.wait_for_timeout(300)
            ok(pg.evaluate("DEV.forma") == 'dinheiro' and pg.evaluate("RASCUNHO.forma") is None and trecho in modal() and 'indisponível' in modal(),
               'escolher a opção não muda a forma (segue Dinheiro) e a tela avisa: %s' % modal()[:90])
            fechar_modal()
            ok(pg.evaluate("document.getElementById('inputForma').getAttribute('data-value')") == 'dinheiro', 'o campo volta a mostrar a forma que valia')

        # ---- 2b. escolher sem salvar e finalizar: avisa, em vez de finalizar com a forma antiga
        limpar(); ir(DEV_D, '?id=4')
        clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').click()"); pg.wait_for_timeout(300)
        pg.evaluate("finalizar()"); pg.wait_for_timeout(300)
        ok('não salvas' in modal() and pg.evaluate("DEV.situacao") == 'aberta' and pg.evaluate("DEV.forma") == 'dinheiro' and len(gravados()) == 0,
           'Vale-compra escolhido e não salvo: finalizar pede para salvar antes, e nada finaliza nem nasce: %s' % modal()[:90])
        fechar_modal()
        # ---- 2b. escolher so anota; finalizar gera
        limpar(); ir(DEV_D, '?id=4')
        forma_vale_e_salva()
        ok(pg.evaluate("DEV.forma") == 'valetroca' and len(gravados()) == 0 and pg.evaluate("DEV.situacao") == 'aberta', 'escolher e salvar a forma Vale-compra só anota: nenhum vale nasceu e a devolução segue aberta')
        pg.evaluate("finalizar()"); pg.wait_for_timeout(300)
        prazo = br(dia(180))
        ok(modal().endswith('Gera o vale-compra de R$ 414,80 para Bruno Carvalho, na Desk Shope, válido até %s.' % prazo), 'a confirmação diz o valor, o cliente, a loja e a validade: %s' % modal())
        ok(len(gravados()) == 0, 'e nada nasce antes de confirmar')
        confirmar()
        gr = gravados()
        ok(len(gr) == 1, 'ao confirmar nasce um vale só')
        v = gr[0]
        ok(v['valor'] == 414.8 and v['loja'] == 1 and v['clienteId'] == 12 and v['cliente'] == 'Bruno Carvalho' and v['doc'] == '890.123.456-77' and v['origem'] == 'devolucao',
           'o vale tem o total da devolução (R$ 414,80: itens e frete), a loja do pedido (Desk Shope), o cliente do cadastro e origem devolução: %s' % dict(valor=v['valor'], loja=v['loja'], cli=v['cliente']))
        ok(v['emitido'] == iso(HOJE) and v['venc'] == iso(dia(180)) and v['usos'] == [] and v['cancelado'] is None, 'emitido hoje, vence em 180 dias, sem usos, não cancelado')
        ok(v['ref'] == dict(tipo='devolucao', id=4, texto='Devolução DV-0009', href='../logistica/pagina-logistica-devolucao-detalhe.html?id=4'), 'a ref é { tipo, id, texto, href } da devolução: %s' % v['ref'])
        ok(pg.evaluate("DEV.situacao") == 'finalizada' and pg.evaluate("document.getElementById('badgeSituacao').textContent.trim()").lower().startswith('finalizada'), 'a devolução fica finalizada')
        ev = pg.evaluate("DEV.eventos[DEV.eventos.length - 1]")
        ok(ev['tipo'] == 'finalizou' and 'Finalizada. Vale-compra' in ev['nota'] and 'VC-1' in ev['nota'] and 'R$ 414,80' in ev['nota'], 'o histórico diz "Finalizada. Vale-compra VC-1 de R$ 414,80": %s' % ev['nota'])
        ok(visivel('#notaVale') and pg.inner_text('#notaValeTexto').startswith('Vale-compra VC-1 · R$ 414,80 · saldo R$ 414,80'), 'o cartão de pagamento mostra a linha do vale com valor e saldo: %s' % pg.inner_text('#notaValeTexto'))
        ok(pg.get_attribute('#notaValeTexto a', 'href') == '../financas/pagina-financas-vale-compra-detalhe.html?id=1', 'e o VC-1 é link para a página do vale (?id=1)')
        ok(pg.evaluate("document.querySelector('#inputForma .dropdown-select-btn').disabled") is True, 'a forma não muda mais depois de finalizada com vale (o campo trava)')
        clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.querySelector('#menuForma').classList.contains('open')") is False, 'e o menu da forma não abre')
        pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"dinheiro\"]').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("DEV.forma") == 'valetroca' and pg.evaluate("RASCUNHO.forma") is None and 'não muda mais' in modal(), 'nem à força: escolher outra forma é recusado com o motivo')
        fechar_modal()

        # ---- 2c. os links nos dois sentidos
        clic('#notaValeTexto a'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.endswith('pagina-financas-vale-compra-detalhe.html?id=1'), 'o link da devolução abre a página do VC-1')
        ref = pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('a.com-link')).filter(x => x.textContent.indexOf('Devolução DV-0009') >= 0)[0]; return a ? [a.textContent, a.getAttribute('href')] : null; })()")
        ok(ref == ['Devolução DV-0009', '../logistica/pagina-logistica-devolucao-detalhe.html?id=4'], 'a página do vale mostra a origem Devolução com o documento como link: %s' % ref)
        pg.evaluate("document.querySelector('a.com-link[href*=\"devolucao-detalhe\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(pg.url.endswith('pagina-logistica-devolucao-detalhe.html?id=4') and pg.evaluate("DEV.numero") == 'DV-0009', 'e o link do vale abre a devolução certa (DV-0009)')
        ok(pg.evaluate("DEV.situacao") == 'finalizada' and pg.evaluate("DEV.forma") == 'valetroca', 'que abre finalizada, com a forma Vale-compra (a devolução de exemplo não é gravada: é o vale que diz)')
        ev = pg.inner_text('#listaEventos')
        ok('Finalizada. Vale-compra VC-1' in ev, 'e o histórico dela conta o vale: %s' % ev.replace('\n', ' | ')[:120])

        # ---- 2d. recarregar nao finaliza de novo
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250)
        ok('já está finalizada' in modal() and len(gravados()) == 1, 'recarregada, a devolução não finaliza de novo e o segundo vale não nasce: %s' % modal()[:60])
        fechar_modal()
        pg.evaluate("document.getElementById('menuMaisAcoes').querySelector('[data-acao=\"finalizar\"]').click()"); pg.wait_for_timeout(250)
        ok(len(gravados()) == 1, 'nem pelo menu "Mais ações"'); fechar_modal()
        ok(pg.evaluate("document.querySelector('#inputForma .dropdown-select-btn').disabled") is True, 'e a forma segue travada ao recarregar')

        # ---- 2e. a validade vem de Configuracoes
        finalizar_em_vale(prazo=30)
        ok(gravados()[0]['venc'] == iso(dia(30)), 'com a validade de Configurações em 30 dias, o vale da devolução vence em hoje mais 30: %s' % gravados()[0]['venc'])
        txt = finalizar_em_vale(prazo=90)
        ok(('válido até ' + br(dia(90))) in txt and gravados()[0]['venc'] == iso(dia(90)), 'e a confirmação já diz a data (90 dias): %s' % txt[-60:])

        # ---- 2f. o vale que nao pode nascer impede finalizar
        limpar(); ir(DEV_D, '?id=4'); forma_vale_e_salva()
        pg.evaluate("(() => { window.emitirVale = function () { throw new Error('falhou de propósito'); }; })()")
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250); confirmar()
        ok(pg.evaluate("DEV.situacao") != 'finalizada' and len(gravados()) == 0 and 'não foi finalizada' in modal() and 'falhou de propósito' in modal(),
           'se o vale não puder nascer, a devolução NÃO finaliza e a tela diz o motivo: %s' % modal())
        fechar_modal()
        ok(pg.evaluate("DEV.eventos.filter(e => e.tipo === 'finalizou').length") == 0 and not visivel('#notaVale'), 'sem evento de finalização e sem linha de vale')
        # trava de duplicidade de verdade: ja existe vale vivo da devolucao (outra aba) -> a segunda tentativa e barrada
        ir(DEV_D, '?id=4'); forma_vale_e_salva()
        pg.evaluate("localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [{ n: 5, clienteId: 12, cliente: 'Bruno Carvalho', doc: '890.123.456-77', loja: 1, origem: 'devolucao', "
                    "ref: { tipo: 'devolucao', id: 4, texto: 'Devolução DV-0009', href: 'x' }, valor: 414.8, emitido: '2026-10-19', venc: '2027-04-17', usos: [], reativacoes: [], cancelado: null }] }))")
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250)
        confirmar()
        ok(pg.evaluate("DEV.situacao") != 'finalizada' and len(gravados()) == 1 and 'não foi finalizada' in modal() and 'Já existe um vale-compra' in modal(),
           'a trava de duplicidade barra o segundo vale: com um vale vivo desta devolução gravado em outra aba, finalizar não finaliza e não emite outro: %s' % modal()[:90])
        fechar_modal()

        # ---- 2g. cancelar: vale intacto e cancelado junto
        finalizar_em_vale()
        pg.evaluate("cancelar()"); pg.wait_for_timeout(250)
        ok('O vale-compra VC-1 (R$ 414,80) é cancelado junto.' in modal(), 'cancelar a devolução com vale intacto avisa: "O vale-compra VC-1 (R$ 414,80) é cancelado junto.": %s' % modal()[-80:])
        ok(gravados()[0]['cancelado'] is None, 'e nada muda antes de confirmar')
        confirmar()
        v = gravados()[0]
        ok(v['cancelado'] == dict(em=iso(HOJE), motivo='devolução cancelada', saldo=414.8), 'confirmado, o vale é cancelado com o motivo "devolução cancelada": %s' % v['cancelado'])
        ok(pg.evaluate("DEV.situacao") == 'cancelada', 'e a devolução fica cancelada')
        ir(DEV_D, '?id=4')
        ok(pg.evaluate("DEV.situacao") == 'cancelada' and 'cancelado junto' in pg.inner_text('#notaValeTexto'), 'recarregada, segue cancelada, e a linha do vale diz "cancelado junto com a devolução": %s' % pg.inner_text('#notaValeTexto'))
        ir(VALE_D, '?id=1')
        ok('devolução cancelada' in pg.inner_text('body') and pg.evaluate("valeSituacao(valeLer()[0])") == 'cancelado', 'a página do vale mostra o vale cancelado com o motivo')

        # ---- 2h. vale usado impede cancelar
        for usado in (100, 0.01):
            finalizar_em_vale()
            pg.evaluate("usarVale(12, 1, %s, { tipo: 'pedido', id: 31, rotulo: 'Pedido nº 31' })" % usado)
            ir(DEV_D, '?id=4')
            pg.evaluate("cancelar()"); pg.wait_for_timeout(250)
            m = modal()
            esperado = 'O vale-compra VC-1 já foi usado (%s de R$ 414,80). O crédito foi gasto: cancelar a devolução agora deixaria o cliente com a compra e o ressarcimento. O caminho é um acerto.' % moeda(usado)
            ok(m == esperado, 'vale usado (%s) bloqueia o cancelamento da devolução com a mensagem do acerto: %s' % (moeda(usado), m[:70]))
            fechar_modal()
            ok(pg.evaluate("DEV.situacao") == 'finalizada' and gravados()[0]['cancelado'] is None and len(gravados()[0]['usos']) == 1, 'nada mudou: a devolução segue finalizada e o vale intacto, com o uso')
            # o uso estornado devolve o saldo: ai o vale volta a ser intacto e a devolucao pode ser cancelada
        pg.evaluate("estornarUsos({ tipo: 'pedido', id: 31, rotulo: 'Pedido nº 31' }, 'pedido cancelado')")
        pg.evaluate("cancelar()"); pg.wait_for_timeout(250)
        ok('é cancelado junto' in modal(), 'com o uso estornado o vale volta a ficar intacto e a devolução pode ser cancelada')
        fechar_modal()

        # ---- 2i. vale cancelado a mao nao cancela a devolucao
        finalizar_em_vale()
        pg.evaluate("(() => { const vs = valeLer(); vs[0].cancelado = { em: valeIsoHoje(), motivo: 'Emitido por engano', saldo: valeSaldo(vs[0]) }; valeGravar(vs); })()".replace('valeIsoHoje()', 'VALE_HOJE'))
        ir(DEV_D, '?id=4')
        ok(pg.evaluate("DEV.situacao") == 'finalizada', 'vale cancelado à mão no Vale-compra NÃO cancela a devolução: ela segue finalizada')
        ok('cancelado' in pg.inner_text('#notaValeTexto') and 'junto' not in pg.inner_text('#notaValeTexto'), 'a linha do vale diz cancelado, sem dizer "junto com a devolução": %s' % pg.inner_text('#notaValeTexto'))
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250)
        ok('já está finalizada' in modal() and len(gravados()) == 1, 'e ela não finaliza de novo para gerar outro vale'); fechar_modal()
        pg.evaluate("cancelar()"); pg.wait_for_timeout(250)
        ok('é cancelado junto' not in modal(), 'cancelar a devolução depois não mexe no vale já cancelado (a confirmação não fala dele): %s' % modal()[-60:])
        em0 = gravados()[0]['cancelado']['em']
        confirmar()
        ok(gravados()[0]['cancelado']['motivo'] == 'Emitido por engano' and pg.evaluate("DEV.situacao") == 'cancelada', 'o vale conserva o motivo que já tinha')

        # ---- 2j. devolucao sem vale: o fluxo de sempre
        limpar(); ir(DEV_D, '?id=4')
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250)
        ok('Forma: Dinheiro' in modal() and 'Gera o vale-compra' not in modal(), 'finalizar em dinheiro continua como antes, sem vale: %s' % modal()[-70:])
        confirmar()
        ok(pg.evaluate("DEV.situacao") == 'finalizada' and len(gravados()) == 0 and not visivel('#notaVale'), 'e nenhum vale nasce')
        # o vale da devolucao de outra lista (DV-0012, cliente fora do cadastro) nem chega a poder
        ir(DEV_D, '?id=1')
        ok(pg.evaluate("motivoSemVale(DEV)") != '', 'DV-0012 (Construtora Veredas, fora do cadastro) não pode ser em vale')
        # a lista mostra o nome novo da forma
        ir(DEV_L)
        ok('Vale-compra' in pg.evaluate("FORMAS.map(f => f.rotulo).join('|')") and 'Vale-troca' not in fonte(DEV_L) and 'reservado: true' not in fonte(DEV_L), 'a lista de devoluções chama a forma de Vale-compra e não reserva mais nada')
        ok(pg.evaluate("document.body.innerText").count('Pedro Antunes') == 0 and 'Bruno Carvalho' in pg.evaluate("document.body.innerText"), 'o cliente de exemplo da venda PV-4903 é o mesmo nas duas telas (Bruno Carvalho)')

        # ---- 2k. a devolucao e gravada (defeito do teste do usuario em 20/out): salvar a forma, sair e voltar nao desfaz; o proximo passo fica visivel
        PROX = 'O vale-compra de R$ 414,80 nasce quando a devolução for finalizada (Mais ações → Finalizar).'
        gravadas = lambda: pg.evaluate("(JSON.parse(localStorage.getItem('deskDevolucoes') || '{}').devolucoes || {})")
        linha_lista = lambda num: pg.evaluate("(n) => Array.from(document.querySelectorAll('#corpoTabela tr')).filter(r => r.innerText.indexOf(n) >= 0)[0].innerText.toLowerCase()", num)
        limpar(); ir(DEV_D, '?id=4')
        ok(PROX not in pg.inner_text('#hintForma'), 'com a forma de fábrica (Dinheiro) o hint não fala de vale')
        clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').click()"); pg.wait_for_timeout(300)
        ok(PROX not in pg.inner_text('#hintForma') and gravadas() == {}, 'escolhida e ainda não salva, a forma não gera o aviso do próximo passo nem grava nada')
        clic('#btnSalvar'); pg.wait_for_timeout(400)   # a senha de salvar nao esta ligada: o aviso de salvo abre direto
        ok(modal() == 'Alterações salvas na devolução DV-0009. ' + PROX, 'o aviso de salvo acrescenta o próximo passo: %s' % modal())
        fechar_modal()
        ok(PROX in pg.inner_text('#hintForma'), 'e o hint da forma, com Vale-compra salvo e a devolução não finalizada, diz: %s' % pg.inner_text('#hintForma')[-100:])
        ok(gravadas().get('4', {}).get('forma') == 'valetroca' and len(gravados()) == 0, 'a devolução foi gravada no navegador com a forma Vale-compra, e nenhum vale nasceu')
        ir(DEV_D, '?id=4')
        ok(pg.evaluate("DEV.forma") == 'valetroca' and pg.evaluate("DEV.situacao") == 'aberta' and pg.evaluate("document.getElementById('inputForma').getAttribute('data-value')") == 'valetroca',
           'sair e voltar: a DV-0009 continua com a forma Vale-compra salva (antes voltava Dinheiro)')
        ok(PROX in pg.inner_text('#hintForma') and 'Nenhuma alteração pendente' in pg.inner_text('#infoPendente'), 'o hint do próximo passo segue lá, e nada fica pendente')
        ir(DEV_L)
        lin = linha_lista('DV-0009')
        ok('vale-compra' in lin and 'em aberto' in lin, 'a lista mostra a DV-0009 em aberto com a forma Vale-compra, igual ao detalhe: %s' % lin.replace('\n', ' | ')[:100])
        ir(DEV_D, '?id=4')
        pg.evaluate("finalizar()"); pg.wait_for_timeout(300); confirmar()
        ok(pg.evaluate("DEV.situacao") == 'finalizada' and len(gravados()) == 1 and gravadas()['4']['situacao'] == 'finalizada', 'finalizar grava a devolução finalizada e o vale nasce')
        ok(PROX not in pg.inner_text('#hintForma') and 'nasce quando' not in pg.inner_text('#hintForma'), 'depois de finalizada o hint do próximo passo some')
        ir(DEV_D, '?id=4')
        ok(pg.evaluate("DEV.situacao") == 'finalizada' and pg.evaluate("DEV.forma") == 'valetroca' and visivel('#notaVale') and 'VC-1' in pg.inner_text('#notaValeTexto'), 'sair e voltar: segue finalizada, com a linha do vale VC-1')
        ok(pg.evaluate("DEV.eventos.filter(e => e.tipo === 'finalizou').length") == 1 and pg.evaluate("DEV.eventos.filter(e => e.tipo === 'editou').length") == 1,
           'o histórico não duplica a finalização ao restaurar (uma finalização, uma alteração)')
        ok(PROX not in pg.inner_text('#hintForma'), 'e o hint do próximo passo continua ausente')
        pg.evaluate("finalizar()"); pg.wait_for_timeout(250)
        ok('já está finalizada' in modal() and len(gravados()) == 1, 'recarregada, não finaliza de novo e o segundo vale não nasce'); fechar_modal()
        ir(DEV_L)
        lin = linha_lista('DV-0009')
        ok('vale-compra' in lin and 'finalizada' in lin, 'a lista mostra a DV-0009 finalizada com Vale-compra: %s' % lin.replace('\n', ' | ')[:100])
        # vale cancelado a mao e devolucao cancelada depois: a gravada manda (o vale ficou com o motivo dele)
        ir(DEV_D, '?id=4')
        pg.evaluate("(() => { const vs = valeLer(); vs[0].cancelado = { em: VALE_HOJE, motivo: 'Emitido por engano', saldo: valeSaldo(vs[0]) }; valeGravar(vs); })()")
        ir(DEV_D, '?id=4')
        pg.evaluate("cancelar()"); pg.wait_for_timeout(250); confirmar()
        ir(DEV_D, '?id=4')
        ok(pg.evaluate("DEV.situacao") == 'cancelada' and pg.evaluate("DEV.eventos.filter(e => e.tipo === 'cancelou').length") == 1, 'vale cancelado à mão e devolução cancelada depois: recarregada, segue cancelada (a gravada manda), com um evento só')
        ir(DEV_L)
        ok('cancelada' in linha_lista('DV-0009'), 'e a lista também diz cancelada')

    # ================================================================== [3] Comissoes
    if secao(3, 'Comissões Afiliados: só o afiliado recebe em vale; o pagamento nasce pago e gera o vale certo'):
        def abrir_pagamento(chave):
            ir(COM_D, '?id=' + chave)
            pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(350)

        def escolher_forma_pg(valor):
            pg.evaluate("(v) => document.querySelector('#pgForma .dropdown-select-item[data-value=\"' + v + '\"]').click()", valor); pg.wait_for_timeout(250)

        def pagar(chave, forma, valor):
            """Faz o pagamento pelo painel, ate o aviso final. Devolve o texto do aviso."""
            abrir_pagamento(chave)
            if forma != 'Pix': escolher_forma_pg(forma)
            pg.fill('#pgValor', valor); pg.wait_for_timeout(200)
            clic('#btnPgSalvar'); pg.wait_for_timeout(350)
            if 'Pagar' in modal(): confirmar()
            return modal()

        # ---- 3a. o vendedor nunca ve a opcao
        limpar(); abrir_pagamento('v1')
        itens = pg.evaluate("Array.from(document.querySelectorAll('#pgForma .dropdown-select-item')).map(i => i.textContent.trim())")
        ok(itens == ['Pix', 'Transferência', 'Boleto', 'Dinheiro'] and pg.locator('#pgFormaVale').count() == 0, 'vendedor (Marina Costa): o menu da forma não tem Vale-compra: %s' % itens)
        ok(pg.inner_text('#hintPgForma').strip() == '', 'e o painel não fala de vale-compra')
        pg.evaluate("document.getElementById('pgForma').setAttribute('data-value', 'Vale-compra')")
        pg.fill('#pgValor', '10,00'); clic('#btnPgSalvar'); pg.wait_for_timeout(300)
        ok('não pode ser em vale-compra' in modal() and len(pagamentos()) == 0 and len(gravados()) == 0, 'nem à força: pagamento de vendedor em vale é recusado, sem pagamento e sem vale: %s' % modal())
        fechar_modal()

        # ---- 3b. o afiliado ve a opcao, com o texto e o vencimento travado
        abrir_pagamento('a1')
        itens = pg.evaluate("Array.from(document.querySelectorAll('#pgForma .dropdown-select-item')).map(i => i.textContent.trim())")
        ok(itens == ['Pix', 'Transferência', 'Boleto', 'Dinheiro', 'Vale-compra'], 'afiliado (Bruno Carvalho, Desk Brands): o menu da forma ganha Vale-compra: %s' % itens)
        ok('Chave PIX' in pg.inner_text('#pgResumo') and pg.evaluate("document.getElementById('pgVenc').readOnly") is False, 'com Pix, a chave Pix aparece e o vencimento é livre')
        escolher_forma_pg('Vale-compra'); pg.fill('#pgValor', '20,00'); pg.wait_for_timeout(200)
        ok(pg.inner_text('#hintPgForma') == 'Vira vale-compra de R$ 20,00 na Desk Brands, válido até %s. Nada sai do Caixa.' % br(dia(180)), 'o hint diz o valor, a loja e a validade: %s' % pg.inner_text('#hintPgForma'))
        ok(pg.evaluate("document.getElementById('pgVenc').readOnly") is True and pg.input_value('#pgVenc') == br(HOJE), 'com Vale-compra o vencimento fica hoje e travado')
        ok('Chave PIX' not in pg.inner_text('#pgResumo'), 'e a chave Pix some do painel')
        pg.fill('#pgValor', '25,50'); pg.wait_for_timeout(150)
        ok('R$ 25,50' in pg.inner_text('#hintPgForma'), 'o hint acompanha o valor digitado')
        escolher_forma_pg('Pix')
        ok(pg.evaluate("document.getElementById('pgVenc').readOnly") is False and 'Chave PIX' in pg.inner_text('#pgResumo'), 'voltando para Pix, o vencimento solta e a chave volta')
        # as condicoes da opcao: forma desabilitada, sem cadastro de cliente, loja que nao emite vale
        for rotulo, js in (('forma Vale-compra desabilitada', "FORMA_VALE.ativo = false"), ('afiliado sem cliente no cadastro', "AFILIADOS_C[0].clienteId = null"),
                           ('loja que não emite vale (Desk Flash)', "AFILIADOS_C[0].loja = 4")):
            ir(COM_D, '?id=a1')
            pg.evaluate("(() => { %s; B = beneficiarioDe('a1'); abrirPagamento(); })()" % js); pg.wait_for_timeout(300)
            ok(pg.locator('#pgFormaVale').count() == 0, 'sem a opção quando: %s' % rotulo)

        # ---- 3c. pagar em vale
        limpar()
        aviso = pagar('a1', 'Vale-compra', '20,00')
        gr, pgs = gravados(), pagamentos()
        ok(len(gr) == 1 and len(pgs) == 1, 'um vale e um pagamento nasceram')
        v, pa = gr[0], pgs[0]
        ok(v['valor'] == 20 and v['loja'] == 2 and v['clienteId'] == 12 and v['cliente'] == 'Bruno Carvalho' and v['doc'] == '890.123.456-77' and v['origem'] == 'comissao',
           'o vale é do afiliado, na loja da comissão (Desk Brands), origem comissão, sem bônus: R$ 20,00 de comissão, R$ 20,00 de vale: %s' % dict(valor=v['valor'], loja=v['loja']))
        ok(v['emitido'] == iso(HOJE) and v['venc'] == iso(dia(180)) and v['usos'] == [] and v['cancelado'] is None, 'emitido hoje, vence em 180 dias, intacto')
        ok(v['ref'] == dict(tipo='comissao', id=1, texto='Comissão COM-1', href='../financas/pagina-financas-comissoes-detalhe.html?id=a1'), 'a ref aponta o pagamento COM-1 e a conta do afiliado: %s' % v['ref'])
        ok(pa['n'] == 1 and pa['forma'] == 'Vale-compra' and pa['vale'] == 1 and pa['venc'] == iso(HOJE) and pa['data'] == iso(HOJE) and pa['valor'] == 20 and pa['chave'] == 'a1' and pa.get('pix', '') == '',
           'o pagamento COM-1 nasce com forma Vale-compra, vale 1, vencimento hoje: %s' % dict(forma=pa['forma'], vale=pa.get('vale'), venc=pa['venc']))
        ok(pa['baixas'] == [dict(data=iso(HOJE), valor=20, contaId=None, juros=0, desconto=0, forma='Vale-compra', vale=1)], 'e já vem pago: uma baixa com o vale, sem conta financeira: %s' % pa['baixas'])
        ok(aviso == 'Pagamento COM-1: R$ 20,00 em vale-compra VC-1 para Bruno Carvalho, na Desk Brands. Nada saiu do Caixa.', 'o aviso diz o pagamento, o vale, o cliente, a loja e que nada saiu do Caixa: %s' % aviso)
        fechar_modal()
        ok(pg.evaluate("Math.round(saldoDeHoje() * 100) / 100") == 31.2, 'o saldo de comissão desceu: R$ 51,20 menos R$ 20,00 = R$ 31,20')
        linha = pg.inner_text('#corpoPagtos')
        ok('Vale-compra' in linha and 'pago em vale-compra VC-1' in linha and 'COM-1' in linha and 'dar baixa' not in linha and 'reprogramar' not in linha, 'a lista de pagamentos mostra o pago em vale-compra VC-1 (sem dar baixa nem reprogramar): %s' % linha.replace('\n', ' | ')[:120])
        ok(pg.get_attribute('#corpoPagtos a[href*="vale-compra-detalhe"]', 'href') == '../financas/pagina-financas-vale-compra-detalhe.html?id=1', 'com link para o vale')
        hist = pg.inner_text('#corpoHistorico')
        ok('pago em vale-compra VC-1' in hist and 'conta a pagar' not in hist.split('Pagamento COM-1')[1][:60] and 'pago em Contas a Pagar' not in hist, 'o histórico diz "Pagamento COM-1: pago em vale-compra VC-1" e não "conta a pagar"')
        ok(pg.locator('#corpoHistorico a[href*="vale-compra-detalhe.html?id=1"]').count() == 1, 'e o VC-1 do histórico é link para o vale')
        ir(VALE_D, '?id=1')
        ref = pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('a.com-link')).filter(x => x.textContent.indexOf('Comissão COM-1') >= 0)[0]; return a ? [a.textContent, a.getAttribute('href')] : null; })()")
        ok(ref == ['Comissão COM-1', '../financas/pagina-financas-comissoes-detalhe.html?id=a1'], 'a página do vale mostra a origem Comissão com o documento como link para a conta do afiliado: %s' % ref)
        pg.evaluate("document.querySelector('a.com-link[href*=\"comissoes-detalhe\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(pg.evaluate("B.chave") == 'a1', 'e o link abre a conta do afiliado certo (a1)')
        ok('Vale-compra' in pg.inner_text('#corpoPagtos'), 'que mostra o pagamento')
        # o mesmo pagamento nao gera outro vale ao recarregar; um segundo pagamento gera o VC-2 e o COM-2
        aviso = pagar('a1', 'Vale-compra', '5,00')
        ok(len(gravados()) == 2 and gravados()[1]['ref']['id'] == 2 and 'COM-2' in aviso and 'VC-2' in aviso, 'um segundo pagamento em vale gera o VC-2 do COM-2: %s' % aviso[:70])
        fechar_modal()

        # ---- 3d. ordem atomica: o pagamento nao grava -> o vale volta ao texto de antes
        limpar(); ir(COM_D, '?id=a1')
        antes = pg.evaluate("localStorage.getItem('deskValesCompra')")
        pg.evaluate("window.__setItem = Storage.prototype.setItem; Object.defineProperty(Storage.prototype, 'setItem', { configurable: true, writable: true, value: function (k, v) { if (k === 'deskComissoesPagas') throw new Error('cheio'); return window.__setItem.apply(this, arguments); } })")
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(300); escolher_forma_pg('Vale-compra'); pg.fill('#pgValor', '20,00')
        clic('#btnPgSalvar'); pg.wait_for_timeout(300); confirmar()
        txt = modal()
        pg.evaluate("Object.defineProperty(Storage.prototype, 'setItem', { value: window.__setItem, configurable: true, writable: true })")
        ok('não foi feito' in txt and pg.evaluate("localStorage.getItem('deskValesCompra')") == antes and len(pagamentos()) == 0, 'se o pagamento não grava, o vale volta ao texto de antes e nada fica registrado: %s' % txt[:80])
        fechar_modal()
        # o vale nao pode nascer -> nao registra o pagamento
        ir(COM_D, '?id=a1')
        pg.evaluate("(() => { window.emitirVale = function () { throw new Error('sem vale'); }; })()")
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(300); escolher_forma_pg('Vale-compra'); pg.fill('#pgValor', '20,00')
        clic('#btnPgSalvar'); pg.wait_for_timeout(300); confirmar()
        ok('não foi feito' in modal() and 'sem vale' in modal() and len(pagamentos()) == 0, 'se o vale não nasce, o pagamento não é registrado: %s' % modal()[:70])
        fechar_modal()

        # ---- 3e. a validade de Configuracoes
        limpar(valeCompraValidadeDias=60, confirmacoes=PADRAO)
        pagar('a1', 'Vale-compra', '20,00'); fechar_modal()
        ok(gravados()[0]['venc'] == iso(dia(60)), 'com a validade em 60 dias, o vale da comissão vence em hoje mais 60: %s' % gravados()[0]['venc'])

        # ---- 3f. pagar em Pix continua como antes
        limpar()
        pagar('a1', 'Pix', '10,00'); fechar_modal()
        pa = pagamentos()[0]
        ok(len(gravados()) == 0 and pa['forma'] == 'Pix' and not pa.get('vale') and not pa.get('baixas') and pa['venc'] == iso(HOJE), 'pagar em Pix não gera vale e nasce a pagar, como antes: %s' % dict(forma=pa['forma']))

        # ---- 3g. cancelar o pagamento em vale
        limpar(); pagar('a1', 'Vale-compra', '20,00'); fechar_modal()
        pg.evaluate("document.querySelector('[data-cancelar-pg=\"1\"]').click()"); pg.wait_for_timeout(300)
        ok(modal() == 'Cancelar o pagamento COM-1? O vale-compra VC-1 (R$ 20,00) é cancelado e o valor volta ao saldo de comissão.', 'a confirmação diz que o vale é cancelado e o valor volta ao saldo: %s' % modal())
        confirmar()
        v, pa = gravados()[0], pagamentos()[0]
        ok(v['cancelado'] == dict(em=iso(HOJE), motivo='pagamento de comissão cancelado', saldo=20) and pa.get('cancelado') is True, 'o vale é cancelado com o motivo "pagamento de comissão cancelado" e o pagamento fica cancelado: %s' % v['cancelado'])
        ok(pg.evaluate("Math.round(saldoDeHoje() * 100) / 100") == 51.2, 'o valor voltou ao saldo de comissão (R$ 51,20)')
        ok('cancelado' in pg.inner_text('#corpoHistorico') and 'voltou ao saldo' in pg.inner_text('#corpoHistorico'), 'o histórico conta o cancelamento')
        fechar_modal()
        # com o saldo de volta, pagar de novo gera outro vale e outro pagamento
        aviso = pagar('a1', 'Vale-compra', '51,20'); fechar_modal()
        ok(len(gravados()) == 2 and gravados()[1]['valor'] == 51.2 and gravados()[1]['ref']['id'] == 2, 'depois de cancelar, dá para pagar de novo (COM-2, VC-2)')
        # vale usado impede
        limpar(); pagar('a1', 'Vale-compra', '20,00'); fechar_modal()
        pg.evaluate("usarVale(12, 2, 5, { tipo: 'pedido', id: 40, rotulo: 'Pedido nº 40' })")
        ir(COM_D, '?id=a1')
        pg.evaluate("document.querySelector('[data-cancelar-pg=\"1\"]').click()"); pg.wait_for_timeout(300)
        ok(modal() == 'O vale-compra VC-1 já foi usado (R$ 5,00). O pagamento não se cancela.', 'vale usado (mesmo em parte) bloqueia o cancelamento do pagamento: %s' % modal())
        fechar_modal()
        ok(pagamentos()[0].get('cancelado') is None and gravados()[0]['cancelado'] is None, 'e nada mudou')
        # vale cancelado a mao: cancelar o pagamento so devolve o valor ao saldo
        limpar(); pagar('a1', 'Vale-compra', '20,00'); fechar_modal()
        pg.evaluate("(() => { const vs = valeLer(); vs[0].cancelado = { em: VALE_HOJE, motivo: 'Emitido por engano', saldo: 20 }; valeGravar(vs); })()")
        ir(COM_D, '?id=a1')
        pg.evaluate("document.querySelector('[data-cancelar-pg=\"1\"]').click()"); pg.wait_for_timeout(300)
        ok('já está cancelado' in modal(), 'com o vale já cancelado à mão, a confirmação diz isso: %s' % modal())
        confirmar(); fechar_modal()
        ok(pagamentos()[0].get('cancelado') is True and gravados()[0]['cancelado']['motivo'] == 'Emitido por engano', 'o pagamento é cancelado e o vale conserva o motivo dele')

    # ================================================================== [4] Contas a Pagar
    if secao(4, 'Contas a Pagar: o título já pago, só leitura, fora do Caixa; a seleção em massa não toca'):
        limpar()
        ir(CAIXA)
        movs_antes = pg.evaluate("MOVIMENTOS.length")
        saldos_antes = pg.evaluate("[1, 2, 3, 4, 6].map(c => saldoAte(c, null))")
        ir(COM_D, '?id=a1')
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(300)
        pg.evaluate("document.querySelector('#pgForma .dropdown-select-item[data-value=\"Vale-compra\"]').click()"); pg.fill('#pgValor', '20,00'); pg.wait_for_timeout(150)
        clic('#btnPgSalvar'); pg.wait_for_timeout(300); confirmar(); fechar_modal()
        # um segundo, em Pix, de controle (a pagar, com baixa possivel)
        ir(COM_D, '?id=a1')
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(300); pg.fill('#pgValor', '10,00'); clic('#btnPgSalvar'); pg.wait_for_timeout(300); confirmar(); fechar_modal()
        ok(len(pagamentos()) == 2 and pagamentos()[0]['vale'] == 1 and not pagamentos()[1].get('vale'), 'COM-1 em vale e COM-2 em Pix (o controle)')
        ir(CP_L)
        t = pg.evaluate("(() => { const t = titDe(9001); return t && { valor: t.valor, pago: t.pago, forma: t.forma, hist: t.hist, vale: t.vale, cancelado: t.cancelado, comissao: t.comissao, doc: t.doc, pagamentos: t.pagamentos, sit: situacaoDe(t), saldo: saldoDe(t) }; })()")
        ok(t and t['sit'] == 'paga' and t['pago'] == 20 and t['valor'] == 20 and t['saldo'] == 0 and t['forma'] == 'Vale-compra' and t['vale'] == 1 and t['doc'] == 'COM-1', 'o COM-1 é o título 9001, já pago por inteiro, forma Vale-compra, marcado com o vale 1: %s' % (t and dict(sit=t['sit'], forma=t['forma'], vale=t['vale'])))
        ok(t and 'Pago com vale-compra VC-1' in t['hist'] and 'Bruno Carvalho' in t['hist'], 'o histórico diz "Pago com vale-compra VC-1": %s' % (t and t['hist']))
        ok(t and t['pagamentos'] == [dict(data=iso(HOJE), valor=20, contaId=None, juros=0, desconto=0, forma='Vale-compra', vale=1)], 'a baixa é a do pagamento, sem conta financeira: %s' % (t and t['pagamentos']))
        c = pg.evaluate("(() => { const t = titDe(9002); return { sit: situacaoDe(t), vale: t.vale || null, pago: t.pago }; })()")
        ok(c['sit'] == 'aberta' and c['vale'] is None and c['pago'] == 0, 'o COM-2, em Pix, é um título a pagar comum')
        pg.evaluate("abaAtual = 'paga'; paginaAtual = 1; render()"); pg.wait_for_timeout(250)
        corpo = pg.inner_text('body')
        ok('COM-1' in corpo and 'COM-2' not in corpo, 'na aba Pagas aparece o COM-1, e não o COM-2: conta como pago nos totais da lista')
        pg.evaluate("abaAtual = 'todas'; render()")
        # o painel da conta
        pg.evaluate("abrirConta(9001)"); pg.wait_for_timeout(300)
        painel = pg.inner_text('#contaCorpo')
        ok('Vale-compra' in painel and 'VC-1' in painel and 'só leitura' in painel and 'Pagar' not in painel.split('\n')[-3:], 'o painel lateral da lista mostra o vale e o "só leitura", e não tem o botão Pagar')
        ok(pg.evaluate("document.querySelector('#btnBaixarDaConta')") is None and 'Vale-compra' in pg.inner_text('#contaBaixas'), 'a baixa do painel diz Vale-compra, no lugar do nome de uma conta financeira')
        clic('#fecharConta'); pg.wait_for_timeout(200)
        # massa
        pg.evaluate("selTit = [9001]; atualizarBarraSelecao()"); pg.wait_for_timeout(150)
        ok(not visivel('#linkCancelarSelecionadas'), 'selecionado só o título do vale, o link "Cancelar contas" nem aparece')
        clic('#linkCancelarSelecionadas'); pg.wait_for_timeout(250)
        ok(modal() == '' and pg.evaluate("titDe(9001).cancelado") is False, 'a seleção em massa não cancela o título do vale')
        pg.evaluate("selTit = [9001]"); clic('#linkExcluirSelecionadas'); pg.wait_for_timeout(250)
        ok(modal() == '' and pg.evaluate("!!titDe(9001)") is True, 'a seleção em massa não exclui o título do vale')
        pg.evaluate("selTit = [9001, 9002]"); pg.evaluate("atualizarBarraSelecao()")
        ok(visivel('#linkCancelarSelecionadas'), 'com o COM-2 junto, o link aparece (controle)')
        clic('#linkCancelarSelecionadas'); pg.wait_for_timeout(250)
        if modal(): confirmar()   # sem senha na ação, a seleção cancela direto
        ok(pg.evaluate("titDe(9002).cancelado") is True and pg.evaluate("titDe(9001).cancelado") is False, 'o COM-2 foi cancelado e o do vale não')
        # nada no Caixa
        extras = pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras') || '[]')")
        ok(not any(str(m.get('origem', '')).startswith('CP 9001') for m in extras), 'nada foi escrito no Caixa pelo título do vale: %s' % extras)
        ir(CAIXA)
        ok(pg.evaluate("MOVIMENTOS.length") == movs_antes and pg.evaluate("MOVIMENTOS.filter(m => String(m.origem || '').indexOf('CP 90') === 0).length") == 0, 'o extrato do Caixa não ganhou lançamento (%d antes, %d depois)' % (movs_antes, pg.evaluate("MOVIMENTOS.length")))
        ok(pg.evaluate("[1, 2, 3, 4, 6].map(c => saldoAte(c, null))") == saldos_antes, 'e nenhuma conta financeira mudou de saldo: %s' % saldos_antes)
        # o detalhe: so leitura
        ir(CP_D, '?id=9001')
        ok(not visivel('#btnDarBaixa') and not visivel('#acoesLeitura') and not visivel('#menuMaisAcoes') and not visivel('#btnEditar'), 'o detalhe não tem dar baixa, editar nem o menu de cancelar, excluir e clonar')
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')") and not visivel('#rodapeEdicao'), 'e está em modo leitura, sem rodapé de edição')
        faixa = pg.inner_text('#avisoBaixa')
        ok(pg.evaluate("document.getElementById('avisoBaixa').classList.contains('show')") and 'Pago com vale-compra VC-1' in faixa and 'O valor muda em Comissões Afiliados ou no vale.' in faixa and pg.locator('#avisoBaixa a[href$="vale-compra-detalhe.html?id=1"]').count() == 1,
           'a faixa diz "Pago com vale-compra VC-1" com o link e "O valor muda em Comissões Afiliados ou no vale.": %s' % faixa.replace('\n', ' '))
        pg.evaluate("document.querySelector('[data-tab=\"pagamentos\"]') && document.querySelector('[data-tab=\"pagamentos\"]').click()"); pg.wait_for_timeout(200)
        ok('Vale-compra' in pg.inner_text('#corpoPagamentos') and pg.locator('#corpoPagamentos [data-acao="estornar"]').count() == 0, 'a aba de pagamentos diz Vale-compra e não oferece estornar')
        ok(pg.evaluate("document.getElementById('inputValor').readOnly") is True and 'Pago com vale-compra' in pg.inner_text('#roHistorico'), 'o valor e o histórico só se leem')
        ok('Comissões Afiliados' in pg.inner_text('#subtituloConta'), 'o subtítulo diz de onde veio, como em toda conta de comissão')
        ir(CP_D, '?id=9001&baixar=1')
        ok(pg.evaluate("emPagamento.length") == 0 and not pg.evaluate("document.getElementById('drawerPagamento').classList.contains('open')"), 'nem pelo endereço ?baixar=1 a baixa abre')
        ir(CP_D, '?id=9002')
        # o COM-2 foi cancelado na selecao acima; reativa so para a prova do controle
        pg.evaluate("conta.cancelado = false; aplicarModo()")
        ok(visivel('#btnDarBaixa') and visivel('#menuMaisAcoes') is True, 'o COM-2 (controle, em Pix) segue com dar baixa e o menu')
        # a baixa normal escreve no Caixa (prova de que a checagem de cima enxerga um lançamento quando ele existe)
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(300)
        clic('#btnConfirmarPagamento'); pg.wait_for_timeout(350)
        if modal(): confirmar()
        extras = pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras') || '[]')")
        ok(any(str(m.get('origem', '')) == 'CP 9002' for m in extras) and not any(str(m.get('origem', '')) == 'CP 9001' for m in extras),
           'controle: a baixa do COM-2 (Pix) escreve no Caixa e a do vale nunca escreveu: %s' % [m.get('origem') for m in extras])
        # cancelar o pagamento em Comissoes cancela o titulo, que segue so leitura
        ir(COM_D, '?id=a1')
        pg.evaluate("document.querySelector('[data-cancelar-pg=\"1\"]').click()"); pg.wait_for_timeout(300); confirmar(); fechar_modal()
        ir(CP_D, '?id=9001')
        ok(pg.evaluate("situacaoDe(conta)") == 'cancelada' and not visivel('#btnDarBaixa') and not visivel('#menuMaisAcoes') and not visivel('#acoesLeitura'), 'cancelado o pagamento, o título aparece cancelado e segue só leitura (não dá para reativar)')

    # ================================================================== [5] outras telas
    if secao(5, 'As outras telas: pago em vale conta como pago; vencidos; cancelar sozinho; tela inicial'):
        # um vale pago ontem (data e vencimento no passado) e um Pix da mesma data, a pagar
        limpar(afiliadoCancelaVencido=True, afiliadoCancelaVencidoDias=1, confirmacoes=PADRAO)
        ir(INICIO)
        base = pg.evaluate("(() => { const l = document.querySelector('.dia-fila[data-fila=\"pagar\"]'); return [l.querySelector('.dia-numero').textContent, l.querySelector('.dia-sub').textContent]; })()")
        ontem = iso(dia(-3))
        pg.evaluate("(o) => { localStorage.setItem('deskComissoesPagas', JSON.stringify({ pagamentos: [ "
                    "{ n: 1, chave: 'a1', nome: 'Bruno Carvalho', tipo: 'cliente', valor: 20, data: o, venc: o, forma: 'Vale-compra', pix: '', vale: 1, ref: 'outubro de 2026', "
                    "baixas: [{ data: o, valor: 20, contaId: null, juros: 0, desconto: 0, forma: 'Vale-compra', vale: 1 }] }, "
                    "{ n: 2, chave: 'a1', nome: 'Bruno Carvalho', tipo: 'cliente', valor: 10, data: o, venc: o, forma: 'Pix', pix: 'bruno.carvalho@hotmail.com', ref: 'outubro de 2026' } ] })); }", ontem)
        pg.evaluate("(o) => localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [{ n: 1, clienteId: 12, cliente: 'Bruno Carvalho', doc: '890.123.456-77', loja: 2, origem: 'comissao', "
                    "ref: { tipo: 'comissao', id: 1, texto: 'Comissão COM-1', href: 'x' }, valor: 20, emitido: o, venc: '2027-04-01', usos: [], reativacoes: [], cancelado: null }] }))", ontem)
        ir(COM_D, '?id=a1')
        pgs = pagamentos()
        ok(not pgs[0].get('cancelado') and pgs[1].get('cancelado') is True and pgs[1].get('canceladoAuto') == 3, 'o cancelar sozinho (ligado, 1 dia) cancela o Pix vencido e não o pago em vale: %s' % [x.get('cancelado') for x in pgs])
        ok(pg.evaluate("diasDeAtraso(pagamentoDe(1))") == 0 and pg.evaluate("situacaoDoPagamento(pagamentoDe(1)).pago") == 20 and 'pago em vale-compra VC-1' in pg.evaluate("situacaoDoPagamento(pagamentoDe(1)).rotulo"),
           'o pago em vale não tem atraso e conta como pago, "pago em vale-compra VC-1"')
        ok(gravados()[0]['cancelado'] is None, 'e o vale não foi mexido')
        # com o cancelar sozinho desligado: o Pix fica vencido, o vale nao
        param(confirmacoes=PADRAO)
        pg.evaluate("(o) => { const g = JSON.parse(localStorage.getItem('deskComissoesPagas')); delete g.pagamentos[1].cancelado; delete g.pagamentos[1].canceladoAuto; delete g.pagamentos[1].canceladoEm; localStorage.setItem('deskComissoesPagas', JSON.stringify(g)); }", ontem)
        ir(COM_L)
        fila = pg.inner_text('#corpoVencidos')
        ok('COM-2' in fila and 'COM-1' not in fila, 'no quadro de pagamentos vencidos da lista aparece o Pix (COM-2) e não o pago em vale (COM-1)')
        ir(COM_D, '?id=a1')
        ok(pg.evaluate("pagamentosDe(B).filter(p => diasDeAtraso(p) > 0).length") == 1 and 'Há 1 pagamento vencido' in pg.inner_text('#avisoAtraso'), 'na conta do afiliado só o Pix é vencido')
        ok(pg.evaluate("vistaDaVitrine(B).pago") == 20 and pg.evaluate("vistaDaVitrine(B).atrasado") == 10, 'e a vitrine do cliente soma o vale como Pago (R$ 20,00) e só o Pix como em atraso (R$ 10,00)')
        ir(INICIO)
        depois = pg.evaluate("(() => { const l = document.querySelector('.dia-fila[data-fila=\"pagar\"]'); return [l.querySelector('.dia-numero').textContent, l.querySelector('.dia-sub').textContent]; })()")
        ok(int(depois[0]) == int(base[0]) + 1, 'a tela inicial conta 1 conta a pagar atrasada a mais (o Pix), e não 2: %s -> %s' % (base[0], depois[0]))
        ir(CLI_D, '?id=12&aba=afiliado')
        ok(pg.evaluate("(() => { const b = beneficiarioDe('a1'); const pags = pagamentosDe(b); return pags.reduce((s, p) => s + situacaoDoPagamento(p).pago, 0); })()") == 20, 'o cadastro do cliente (aba Afiliado) conta o pagamento em vale como pago')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"afiliado\"]').click()"); pg.wait_for_timeout(250)
        ok('pago em vale-compra VC-1' in pg.inner_text('#corpoAfiHistorico') and pg.locator('#corpoAfiHistorico a[href$="vale-compra-detalhe.html?id=1"]').count() >= 1, 'e o histórico dele fala do vale, com o link')
        # a barra de rolagem
        sem_barra = {}
        for larg in (1280, 1440):
            pg.set_viewport_size({'width': larg, 'height': 900})
            limpar()
            ir(COM_D, '?id=a1')
            pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(250)
            pg.evaluate("document.querySelector('#pgForma .dropdown-select-item[data-value=\"Vale-compra\"]').click()"); pg.wait_for_timeout(150)
            sem_barra['painel de pagamento em vale %d' % larg] = pg.evaluate(MEDE)
            pg.fill('#pgValor', '20,00'); clic('#btnPgSalvar'); pg.wait_for_timeout(300); confirmar(); fechar_modal()
            sem_barra['conta do afiliado com o pagamento em vale %d' % larg] = pg.evaluate(MEDE)
            ir(CP_L); sem_barra['Contas a Pagar %d' % larg] = pg.evaluate(MEDE)
            ir(CP_D, '?id=9001'); sem_barra['conta paga com vale %d' % larg] = pg.evaluate(MEDE)
            ir(DEV_D, '?id=4'); sem_barra['devolução antes de finalizar %d' % larg] = pg.evaluate(MEDE)
            clic('#inputForma .dropdown-select-btn'); pg.wait_for_timeout(100)
            pg.evaluate("document.querySelector('#menuForma .dropdown-select-item[data-value=\"valetroca\"]').click()"); pg.wait_for_timeout(250)
            clic('#btnSalvar'); pg.wait_for_timeout(250)
            if modal(): confirmar()
            pg.evaluate("finalizar()"); pg.wait_for_timeout(250); confirmar()
            sem_barra['devolução finalizada com vale %d' % larg] = pg.evaluate(MEDE)
            ir(VALE_D, '?id=2'); sem_barra['página do vale (origem devolução) %d' % larg] = pg.evaluate(MEDE)
        pg.set_viewport_size({'width': 1440, 'height': 900})
        ruim = dict((k, v) for k, v in sem_barra.items() if v)
        ok(not ruim, 'nenhuma das telas mexidas tem barra de rolagem a 1280 e a 1440: %s' % (ruim or 'todas limpas'))
        # o bloco
        TODAS = ('pagina-financas-vale-compra.html', 'pagina-financas-vale-compra-detalhe.html', CLI_D, 'pagina-vendas-pdv.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-vendas-pedidos.html',
                 'pagina-financas-contas-receber.html', 'pagina-financas-contas-receber-detalhe.html', DEV_D, COM_D)
        INI, FIM = '  // ===== VALE-COMPRA: DADOS E REGRAS', '  // ===== FIM DO BLOCO VALE-COMPRA ====='
        blocos = [fonte(n)[fonte(n).index(INI):fonte(n).index(FIM)] for n in TODAS]
        ok(len(set(blocos)) == 1 and all(f in blocos[0] for f in ('function valeDaOrigem(', 'function emitirVale(', 'function cancelarValeDaOrigem(')), 'o bloco é idêntico nas dez cópias e traz valeDaOrigem, emitirVale e cancelarValeDaOrigem')
        ok(all(fonte(n).count('function emitirVale(') == 1 for n in TODAS), 'cada tela tem emitirVale uma vez só')
        sem_escrita = [n for n in TODAS if n not in (DEV_D, COM_D, 'pagina-financas-vale-compra.html', 'pagina-financas-vale-compra-detalhe.html', 'pagina-vendas-pdv.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-vendas-pedidos.html')
                       and 'emitirVale(' in fonte(n).replace(blocos[0], '')]
        ok(not sem_escrita, 'só a Devolução e a conta do afiliado chamam emitirVale: %s' % sem_escrita)
        ok(fonte(DEV_D).count("emitirVale({") == 1 and fonte(COM_D).count("emitirVale({") == 1, 'cada uma chama uma vez')

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
