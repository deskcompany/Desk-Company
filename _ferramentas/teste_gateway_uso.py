# -*- coding: utf-8 -*-
# Gateways de Pagamento, entrega 2: Formas de Recebimento e o PDV leem as condicoes do gateway (barganha aprovada pelo usuario em 20/out/2026).
#
# Decisoes dele (nao se reabrem): (1) SO os cartoes (debito e credito) leem o gateway; Pix e boleto seguem como eram. (2) No PDV o caixa escolhe a
# MAQUININHA entre os gateways habilitados da loja do PDV, so os do tipo Outro (a InfinitePay e da loja virtual), com o padrao da forma ja marcado; com
# uma so, o campo nao aparece. (3) O caixa marca a BANDEIRA, com a bandeira padrao do gateway ja marcada; trocar recalcula a taxa e o repasse.
#
#   [1] O bloco de leitura (`GATEWAYS: LEITURA`): copias identicas, a semente igual a da pagina do gateway, as funcoes de leitura e o gateway padrao da forma;
#   [2] Formas de recebimento: o cartao escolhe o gateway padrao e mostra as condicoes so para ler; o que sumiu; Pix e boleto como eram; sem gateway; salvar;
#   [3] PDV, a maquininha e a bandeira: quais aparecem, o padrao, a loja sem maquininha, trocar recalcula (credito sim, debito nao), parcelas com condicao;
#   [4] PDV, o repasse: as quatro regras do gateway, "a partir da" e a senha do gerente;
#   [5] PDV, o titulo: vencimento pelo prazo do gateway (e o proximo dia util), conta, maquininha e bandeira gravadas, o caixa e o turno;
#   [6] O catalogo (a acao do repasse), o Pedido de Venda que le a venda e o que nao mudou;
#   [7] O exemplo REAL no PDV (InfinitePay Bronze): taxa, dias uteis, debito por bandeira, loja sem maquininha (a Bronze desabilitada dentro do teste);
#   [8] O desconto Pix e dinheiro (21/out/2026): tudo Pix, venda dividida, troco, sem maquininha, desligado, tirar com senha, subir de nivel, centavos;
#   [9] Configuracoes > PDV (o interruptor), a troca do exemplo antigo vista pelas quatro telas e o gateway padrao de Formas que cai na Bronze.
#
# As secoes 1 a 6 rodam numa BANCADA: tres gateways de numeros redondos (a "Stone" com 3,00% a 10,00% e prazo de 31 dias uteis, a "Cielo", a loja virtual),
# postos direto no armazenamento. Testam o mecanismo (padrao, bandeira, repasse, vencimento) sem depender das taxas oficiais, que mudam; o exemplo real
# da Desk e testado nas secoes 7 a 9 e em teste_gateways.py [8]. O desconto Pix/dinheiro nasce DESLIGADO na bancada (os numeros das secoes 1 a 6 nao o contam).
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys, json, re, datetime
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
PDV, FORMAS, LISTA, DET = 'pagina-vendas-pdv.html', 'pagina-configuracoes-formas-recebimento.html', 'pagina-integracoes-gateways.html', 'pagina-integracoes-gateways-detalhe.html'
CFG = 'pagina-configuracoes-pdv.html'
PEDIDOS, SENHAS = 'pagina-vendas-pedidos.html', 'pagina-configuracoes-confirmacoes-senha.html'
CATALOGOS = ['pagina-vendas-pdv.html', 'pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html', 'pagina-cadastros-vendedores-detalhe.html']
CHAVES_LOCAIS = ['deskPdv', 'deskParametros', 'deskGateways', 'deskGatewaysExemplo', 'deskLog']
INI, FIM = '  // ===== GATEWAYS: LEITURA', '  // ===== FIM DO BLOCO GATEWAYS: LEITURA ====='
FERIADOS_FIXOS = {(1, 1), (21, 4), (1, 5), (7, 9), (12, 10), (2, 11), (15, 11), (20, 11), (25, 12)}

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


def e_util(d):
    return d.weekday() < 5 and (d.day, d.month) not in FERIADOS_FIXOS


def dia_util_a_partir(d):
    while not e_util(d):
        d += datetime.timedelta(days=1)
    return d


br = lambda d: d.strftime('%d/%m/%Y')
HOJE = datetime.date.today()


def mais_uteis(d, n):
    """Soma n dias UTEIS (sabado, domingo e feriado nacional de data fixa nao contam): o prazo do gateway."""
    while n > 0:
        d += datetime.timedelta(days=1)
        if e_util(d):
            n -= 1
    return d


def pago_avista(valor, pct):
    """O que o cliente paga de um recebimento em Pix ou dinheiro: em centavos inteiros, meio centavo sobe (como o PDV)."""
    return int(round(valor * 100) * (10000 - round(pct * 100)) / 10000 + 0.5) / 100


BANDEIRAS_ORDEM = ['visa', 'mastercard', 'amex', 'diners', 'elo', 'hipercard', 'bndes', 'outro']
TAXAS_BANCADA = [3, 3.6, 4.25, 4.9, 5.5, 6.15, 6.8, 7.45, 8, 8.7, 9.35, 10]


def condicoes_bancada(bandeiras):
    c = [dict(forma='debito', bandeira='', parcelas=0, prazo=2, taxa=0, tarifa=2), dict(forma='boleto', bandeira='', parcelas=0, prazo=2, taxa=0, tarifa=2),
         dict(forma='pix', bandeira='', parcelas=0, prazo=0, taxa=0, tarifa=0)]
    for b in BANDEIRAS_ORDEM:
        if b in bandeiras:
            for n in range(1, 13):
                c.append(dict(forma='credito', bandeira=b, parcelas=n, prazo=30 if n == 12 else 31, taxa=TAXAS_BANCADA[n - 1], tarifa=0))
    return c


def gateways_bancada():
    base = dict(situacao='habilitado', cnpj='', endereco='', municipio='', antecipacao='sem', repassar='nao', repassarAPartir=1)

    def g(i, **x):
        d = dict(base, id=i)
        d.update(x)
        d['condicoes'] = condicoes_bancada(d['bandeiras'])
        return d
    return [
        g(1, tipo='infinitepay', descricao='InfinitePay — loja virtual', lojas=[1, 2], categoriaId=1, contaCreditoId=2, baixa='liberacao', juros=1, multa=2, diasMulta=0, calculaAtraso=True,
          cnpj='12.345.678/0001-95', endereco='Av. Santos Dumont, 1500, Aldeota', municipio='Fortaleza', chave='ipay_live_8f3a1c9e72b4d605', conciliacao=None,
          bandeiras=['visa', 'mastercard', 'elo'], bandeiraPadrao='visa', repassar='opcional', repassarAPartir=2),
        g(2, tipo='outro', descricao='Stone — maquininha da loja', lojas=[1], tarifacao='seguinte', diaDebito=None, categoriaTarifaId=17, bandeiras=list(BANDEIRAS_ORDEM),
          bandeiraPadrao='mastercard', antecipacao='antecipado'),
        g(3, tipo='outro', descricao='Cielo (antiga)', situacao='desabilitado', lojas=[2], tarifacao='especifico', diaDebito=10, categoriaTarifaId=18, bandeiras=['visa', 'mastercard'],
          bandeiraPadrao='visa')]
FORMAS_LINHA = "(n) => { const tr = Array.from(document.querySelectorAll('#listaFormas tbody tr')).filter(t => t.querySelector('.cf-nome').textContent.trim() === n)[0]; return tr ? tr.textContent.replace(/\\s+/g, ' ').trim() : ''; }"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    pg.set_default_timeout(8000)
    pg.add_init_script("window.print = function () { window.__imprimiu = (window.__imprimiu || 0) + 1; };")
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('console', lambda m: erros.append('console: ' + m.text[:160]) if m.type == 'error' else None)

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.getClientRects().length > 0 && getComputedStyle(e).display !== 'none'; }", sel)

    def txt(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.trim() : null; }", sel)

    def escolher(raiz, valor):
        clic('#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(100)
        pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
        pg.wait_for_timeout(220)

    def rotulos(sel):
        return pg.evaluate("(s) => Array.from(document.querySelectorAll(s)).map(e => e.textContent.trim())", sel)

    def valores(sel):
        return pg.evaluate("(s) => Array.from(document.querySelectorAll(s)).map(e => e.getAttribute('data-value'))", sel)

    def modal():
        return pg.evaluate("document.getElementById('confirmModal').classList.contains('open') ? document.getElementById('confirmModalTexto').textContent : ''")

    def senha_pedida():
        return pg.evaluate("(() => { const r = document.getElementById('campoSenhaModal'); return !!r && r.classList.contains('on'); })()")

    def confirmar(senha=True):
        if pg.locator('#confirmModal.open').count():
            if senha and senha_pedida():
                pg.fill('#inputSenhaModal', 'senha-de-teste')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)

    def cancelar():
        clic('#btnConfirmModalCancelar'); pg.wait_for_timeout(250)

    def gws():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskGateways') || '{}').gateways || [])")

    def gateway(id_, **mud):
        """Muda um gateway gravado para o cenario do teste; as telas leem o gravado a cada pintura."""
        pg.evaluate("([i, m]) => { const d = JSON.parse(localStorage.getItem('deskGateways')); Object.assign(d.gateways.filter(g => g.id === i)[0], m); localStorage.setItem('deskGateways', JSON.stringify(d)); }", [id_, mud])

    def condicao(id_, forma, bandeira, parcelas, **mud):
        pg.evaluate("([i, f, b, n, m]) => { const d = JSON.parse(localStorage.getItem('deskGateways')); const g = d.gateways.filter(x => x.id === i)[0];"
                    " Object.assign(g.condicoes.filter(c => c.forma === f && c.bandeira === b && c.parcelas === n)[0], m); localStorage.setItem('deskGateways', JSON.stringify(d)); }",
                    [id_, forma, bandeira, parcelas, mud])

    def tirar_condicoes(id_, forma, bandeira, parcelas=None):
        pg.evaluate("([i, f, b, n]) => { const d = JSON.parse(localStorage.getItem('deskGateways')); const g = d.gateways.filter(x => x.id === i)[0];"
                    " g.condicoes = g.condicoes.filter(c => !(c.forma === f && c.bandeira === b && (n === null || c.parcelas === n))); localStorage.setItem('deskGateways', JSON.stringify(d)); }",
                    [id_, forma, bandeira, parcelas])

    def novo_gateway(**g):
        base = dict(tipo='outro', descricao='Maquininha nova', situacao='habilitado', lojas=[1], tarifacao='transacao', diaDebito=None, categoriaTarifaId=17,
                    bandeiras=['visa', 'elo'], bandeiraPadrao='elo', antecipacao='sem', proximoDiaUtil=False, repassar='nao', repassarAPartir=1, cnpj='', endereco='', municipio='')
        base.update(g)
        pg.evaluate("""(g) => { const d = JSON.parse(localStorage.getItem('deskGateways')); g.id = d.gateways.reduce((m, x) => Math.max(m, x.id), 0) + 1;
            g.condicoes = gwlCondicoesFabrica(g.bandeiras); d.gateways.push(g); localStorage.setItem('deskGateways', JSON.stringify(d)); }""", base)
        return max(x['id'] for x in gws())

    def param(**params):
        pg.evaluate("(d) => localStorage.setItem('deskParametros', JSON.stringify(d))", params)

    def limpar(bancada=True, **params):
        """Zera o armazenamento e poe os parametros pedidos. Com `bancada` (o padrao) poe os tres gateways de numeros redondos e o desconto Pix/dinheiro
        desligado; com bancada=False o exemplo REAL (InfinitePay) nasce na proxima abertura de tela e o desconto segue o padrao (ligado)."""
        if pg.url == 'about:blank':
            ir(PDV)
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        if bancada:
            pg.evaluate("(g) => { localStorage.setItem('deskGateways', JSON.stringify({ gateways: g })); localStorage.setItem('deskGatewaysExemplo', '2'); }", gateways_bancada())
            params = dict(dict(pdvDescontoAVista=False), **params)
        if params:
            param(**params)

    def venda(loja=1, sku='FON-BT-200', qtd='1', **params):
        """PDV novo: caixa aberto na loja, um produto, e a tela de finalizar."""
        limpar(**params); ir(PDV)
        clic('#btnAbrirCaixa'); pg.wait_for_timeout(250)
        escolher('abrirLoja', loja)
        pg.fill('#abrirTroco', '150'); clic('#btnConfirmarAbertura'); pg.wait_for_timeout(400)
        pg.fill('#qtdProduto', qtd); pg.fill('#buscaProduto', sku); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
        clic('#btnContinuar'); pg.wait_for_timeout(400)

    def receber(chave):
        escolher('selAddReceb', chave)

    def pend():
        return pg.inner_text('#faltaReceber')

    def lista():
        return pg.inner_text('#listaReceb')

    def troca(attr, i, valor):
        pg.evaluate("([a, i, v]) => { const r = document.querySelector('[' + a + '=\"' + i + '\"]'); r.querySelector('.dropdown-select-btn').click(); r.querySelector('.dropdown-select-item[data-value=\"' + v + '\"]').click(); }", [attr, i, str(valor)])
        pg.wait_for_timeout(250)

    def rec(i=0):
        return pg.evaluate("venda.recebimentos[%d]" % i)

    def repintar():
        pg.evaluate("pintarFinalizar()"); pg.wait_for_timeout(200)

    def log():
        return pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")

    # ================================================================== [1] o bloco de leitura
    if secao(1, 'O bloco de leitura: copias identicas, a semente, as funcoes e o gateway padrao da forma'):
      try:
        a, b, c3 = fonte(PDV), fonte(FORMAS), fonte(CFG)
        ok(a.count(INI) == 1 and b.count(INI) == 1 and c3.count(INI) == 1 and a[a.index(INI):a.index(FIM)] == b[b.index(INI):b.index(FIM)] == c3[c3.index(INI):c3.index(FIM)],
           'o bloco GATEWAYS: LEITURA e identico no PDV, em Formas de recebimento e em Configuracoes > PDV, uma vez em cada')
        bloco = a[a.index(INI):a.index(FIM)]
        ok(bloco.count('localStorage.setItem') == 3 and 'gwlSemear' in bloco, 'so grava a semente (a lista, a marca e o gateway padrao de Formas que sumiu): nenhuma outra escrita')
        ok(all(f in bloco for f in ('function gwlLer(', 'const gwlHabilitados', 'function gwlCondicao(', 'const gwlVezes', 'const gwlRepasse', 'function gwlPadraoDaForma(', 'const gwlConta')), 'e traz as funcoes de leitura')
        # a semente do PDV de um navegador que nunca abriu Gateways e a mesma da pagina do gateway
        limpar(bancada=False); ir(PDV)
        do_pdv = json.dumps(gws(), sort_keys=True)
        ok(len(gws()) == 5 and pg.evaluate("localStorage.getItem('deskGatewaysExemplo')") == '2', 'o PDV, num navegador limpo, semeia os cinco gateways do exemplo (sem ele ficaria sem maquininha)')
        limpar(bancada=False); ir(LISTA)
        ok(json.dumps(gws(), sort_keys=True) == do_pdv, 'e sao os mesmos dados que a pagina do gateway semeia, campo a campo')
        limpar(bancada=False); ir(FORMAS)
        ok(json.dumps(gws(), sort_keys=True) == do_pdv, 'Formas de recebimento semeia os mesmos')
        limpar(bancada=False); ir(CFG)
        ok(json.dumps(gws(), sort_keys=True) == do_pdv, 'e Configuracoes > PDV tambem')
        # o que ja esta gravado vence o exemplo
        pg.evaluate("localStorage.setItem('deskGateways', JSON.stringify({ gateways: [] }))"); ir(PDV)
        ok(len(gws()) == 0, 'gravado vence o exemplo: com a marca de exemplo posta e nenhum gateway, o PDV nao os traz de volta')
        # as funcoes
        limpar(); ir(PDV)
        hab = lambda loja, tipo: pg.evaluate("gwlHabilitados(%s, %s).map(g => g.id)" % (loja, json.dumps(tipo)))
        ok(hab(1, 'outro') == [2] and hab(1, 'infinitepay') == [1] and hab(1, None) == [1, 2], 'gateways habilitados da loja 1: Stone (Outro) e InfinitePay; por tipo')
        ok(hab(2, 'outro') == [] and hab(2, None) == [1] and hab(3, None) == [], 'a loja 2 so tem a InfinitePay (a Cielo esta desabilitada); a loja 3 nao tem nenhum')
        ok(pg.evaluate("gwlHabilitados(null, 'outro').map(g => g.id)") == [2], 'sem loja, vale a de qualquer loja')
        c = pg.evaluate("gwlCondicao(gwlPorId(2), 'credito', 'visa', 3)")
        ok(c == dict(prazo=31, taxa=4.25, tarifa=0), 'a condicao do credito Visa 3x: prazo 31, taxa 4,25, tarifa 0: %s' % c)
        ok(pg.evaluate("gwlCondicao(gwlPorId(2), 'credito', 'visa', 12)") == dict(prazo=30, taxa=10, tarifa=0), 'e a de 12x: prazo 30, taxa 10')
        deb = dict(prazo=2, taxa=0, tarifa=2)
        ok(pg.evaluate("gwlCondicao(gwlPorId(2), 'debito', 'visa', 1)") == deb and pg.evaluate("gwlCondicao(gwlPorId(2), 'debito', '', 1)") == deb,
           'o debito e uma linha so, qualquer que seja a bandeira: prazo 2, taxa 0, tarifa R$ 2,00')
        ok(pg.evaluate("gwlCondicao(gwlPorId(1), 'credito', 'amex', 1)") is None and pg.evaluate("gwlCondicao(null, 'debito', '', 1)") is None, 'sem a linha, ou sem gateway, devolve nulo')
        ok(pg.evaluate("gwlVezes(gwlPorId(2), 'visa')") == list(range(1, 13)) and pg.evaluate("gwlVezes(gwlPorId(1), 'amex')") == [], 'as parcelas que o gateway tem para a bandeira')
        ok(pg.evaluate("gwlRepasse(gwlPorId(1))") == dict(modo='opcional', aPartirDa=2) and pg.evaluate("gwlRepasse(gwlPorId(2))") == dict(modo='nao', aPartirDa=1), 'as regras de repasse do gateway: modo e "a partir da"')
        ok(pg.evaluate("gwlConta(gwlPorId(2))") == dict(id='gw2', nome='Stone — maquininha da loja'), 'a conta do gateway tem o id gw<n> e o nome dele')
        # gateway padrao da forma
        ok(pg.evaluate("gwlPadraoDaForma('credito').id") == 2 and pg.evaluate("gwlPadraoDaForma('debito').id") == 2, 'de fabrica o gateway padrao e o primeiro habilitado do tipo Outro (a Stone)')
        param(formaGatewayPadrao=dict(credito=1))
        ok(pg.evaluate("gwlPadraoDaForma('credito').id") == 1 and pg.evaluate("gwlPadraoDaForma('debito').id") == 2, 'o gravado em Formas de recebimento vale, forma por forma')
        gateway(1, situacao='desabilitado')
        ok(pg.evaluate("gwlPadraoDaForma('credito').id") == 2, 'gateway padrao que foi desabilitado cai no de fabrica')
        gateway(2, situacao='desabilitado')
        ok(pg.evaluate("gwlPadraoDaForma('credito')") is None, 'sem gateway habilitado nenhum, nao ha padrao')
        pg.evaluate("localStorage.setItem('deskGateways', '{ isto nao e json')")
        ok(pg.evaluate("gwlLer().length") == 0 and pg.evaluate("gwlPadraoDaForma('credito')") is None, 'dado gravado estragado le como vazio, sem erro')
      except Exception as e:
        ok(False, 'a secao 1 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [2] Formas de recebimento
    if secao(2, 'Formas de recebimento: o cartao escolhe o gateway e mostra as condicoes so para ler'):
      try:
        limpar(); ir(FORMAS)

        def abrir(nome):
            pg.evaluate("(n) => { const f = FORMAS.filter(x => x.nome === n)[0]; abrirDrawerForma(f.id); }", nome); pg.wait_for_timeout(300)

        ok(pg.evaluate("FORMAS.filter(f => f.viaGateway).map(f => f.chave)") == ['debito', 'credito']
           and pg.evaluate("FORMAS.filter(f => f.viaGateway).every(f => f.taxaPct === 0 && f.taxaFixa === 0 && f.contaId === null && f.prazoUteis === null && f.tarifacao === 'sem')"),
           'so o debito e o credito leem o gateway, e os valores de fabrica deles (3,49% e companhia) sairam')
        abrir('Cartão de crédito')
        ok(visivel('#blocoGateway') and txt('#inputGateway .dropdown-select-label').startswith('Stone — maquininha da loja · Outro · Desk Shope'), 'o credito abre com o campo Gateway padrao, ja no de fabrica (a Stone), com tipo e lojas')
        ok(rotulos('#menuGateway .dropdown-select-item') == ['InfinitePay — loja virtual · InfinitePay · Desk Shope, Desk Brands', 'Stone — maquininha da loja · Outro · Desk Shope'],
           'o menu traz so os gateways habilitados (a Cielo, desabilitada, nao), com o tipo e as lojas: %s' % rotulos('#menuGateway .dropdown-select-item'))
        ok(not any(visivel(s) for s in ('#campoConta', '#campoVencimento', '#blocoPrazoFixo', '#campoTarifacao', '#blocoTaxa', '#linhaAntecipa', '#campoTaxasParcela', '#linhaRepassa')),
           'prazo, parcelas, taxa, tarifa, repasse, antecipacao e conta deixaram de ser editaveis no cartao: somem')
        r = pg.inner_text('#resumoGateway')
        ok(all(x in r for x in ('Stone — maquininha da loja', 'Mastercard', '31 dias úteis', '30 dias úteis na 12x', '12x', '3,00%', 'de 3,60% a 10,00%', 'R$ 0,00', 'Dia seguinte após a transação', 'Antecipado')),
           'o resumo so de leitura traz as condicoes do gateway: prazo, parcelas, taxa de 1x e das demais, tarifa, quando debita e antecipacao: %s' % r.replace(chr(10), ' | ')[:220])
        ok('Repasse da taxa ao cliente' in txt('#resumoGateway') and 'Não' in r and 'nasce com o gateway' in r, 'e o repasse e a conta (a do gateway) tambem')
        ok(pg.evaluate("document.querySelectorAll('#resumoGateway input, #resumoGateway select, #resumoGateway textarea').length") == 0, 'o resumo e leitura: nenhum campo para digitar')
        ok(pg.get_attribute('#linkEditarGateway', 'href') == '../integracoes/pagina-integracoes-gateways-detalhe.html?id=2' and txt('#linkEditarGateway') == 'editar no gateway', 'com o link "editar no gateway", para a pagina dele')
        # as condicoes do resumo sao as da tabela do gateway
        g2 = [g for g in gws() if g['id'] == 2][0]
        mc = sorted([c for c in g2['condicoes'] if c['forma'] == 'credito' and c['bandeira'] == 'mastercard'], key=lambda c: c['parcelas'])
        ok((('%.2f' % mc[0]['taxa']).replace('.', ',') + '%') in r and (('%.2f' % mc[1]['taxa']).replace('.', ',') + '%') in r, 'a taxa de 1x e a das demais parcelas do resumo sao as das linhas Mastercard do gateway')
        gateway(2, bandeiraPadrao='visa'); condicao(2, 'credito', 'visa', 1, taxa=2.5, prazo=29)
        abrir('Cartão de crédito')
        ok('2,50%' in pg.inner_text('#resumoGateway') and 'Visa' in pg.inner_text('#resumoGateway'), 'o resumo segue o gateway: mudou a bandeira padrao e a taxa la, mudou aqui')
        # o debito
        pg.evaluate("fecharDrawer()"); abrir('Cartão de débito')
        r = pg.inner_text('#resumoGateway')
        ok('Não parcela' in r and '2 dias' in r and 'R$ 2,00' in r and 'Bandeira de referência' not in r, 'o resumo do debito: 2 dias, nao parcela, tarifa de R$ 2,00, sem bandeira de referencia')
        # mudar o gateway padrao
        pg.evaluate("fecharDrawer()"); abrir('Cartão de crédito')
        escolher('inputGateway', 1)
        r = pg.inner_text('#resumoGateway')
        ok('InfinitePay — loja virtual' in r and 'Opcional' in r and 'a partir da 2ª parcela' in r, 'escolher outro gateway troca o resumo na hora (InfinitePay: repasse opcional a partir da 2ª parcela)')
        ok(pg.get_attribute('#linkEditarGateway', 'href').endswith('?id=1'), 'e o link vai para o gateway escolhido')
        # salvar: so o gateway padrao muda, e isso e regra de dinheiro (pede senha)
        clic('#btnSalvarForma'); pg.wait_for_timeout(450)
        ok(modal() != '' and 'regras' in modal() and senha_pedida(), 'trocar o gateway padrao e mexer em regra de dinheiro: o painel diz e pede senha')
        ok(pg.evaluate("(JSON.parse(localStorage.getItem('deskParametros') || '{}').formaGatewayPadrao || {}).credito") is None, 'antes da senha, nada foi gravado')
        confirmar()
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskParametros')).formaGatewayPadrao") == dict(credito=1), 'confirmado, o gateway padrao do credito fica gravado em deskParametros.formaGatewayPadrao (so o credito)')
        ok(pg.evaluate("FORMAS.filter(f => f.chave === 'credito')[0].taxaPct") == 0 and pg.evaluate("FORMAS.filter(f => f.chave === 'credito')[0].prazoUteis") is None, 'e a forma nao ganhou taxa nem prazo: segue sem eles')
        ok('InfinitePay — loja virtual' in pg.evaluate(FORMAS_LINHA, 'Cartão de crédito') and 'Stone' in pg.evaluate(FORMAS_LINHA, 'Cartão de débito'), 'a lista passa a mostrar a conta do gateway novo no credito, e o debito continua no dele')
        ok(pg.evaluate("gwlPadraoDaForma('debito').id") == 2, 'o debito continua no gateway dele')
        # sem escolher: erro
        abrir('Cartão de débito')
        pg.evaluate("setDropdownValor('inputGateway', '')"); clic('#btnSalvarForma'); pg.wait_for_timeout(300)
        ok(visivel('#erroGateway') and modal() == '', 'sem gateway escolhido, com gateways habilitados, o cartao nao salva: a mensagem aparece')
        pg.evaluate("fecharDrawer()")
        # Pix e boleto como eram
        abrir('Pix')
        ok(not visivel('#blocoGateway') and visivel('#campoConta') and visivel('#campoTarifacao') and not visivel('#campoVencimento'), 'o Pix segue como era: conta e tarifa editaveis, sem bloco de gateway')
        pg.evaluate("fecharDrawer()"); abrir('Boleto')
        ok(not visivel('#blocoGateway') and visivel('#campoConta') and visivel('#campoVencimento') and visivel('#campoTarifacao') and pg.input_value('#inputTaxaFixa') == '2,90', 'e o boleto tambem: conta, vencimento e taxa de R$ 2,90 editaveis')
        pg.evaluate("fecharDrawer()")
        # sem gateway habilitado
        pg.evaluate("localStorage.setItem('deskGateways', JSON.stringify({ gateways: [] }))"); ir(FORMAS); abrir('Cartão de crédito')
        ok(visivel('#avisoSemGateway') and pg.get_attribute('#linkNovoGateway', 'href') == '../integracoes/pagina-integracoes-gateways-detalhe.html?novo=1' and 'Nenhum gateway habilitado' in txt('#inputGateway .dropdown-select-label'),
           'sem gateway habilitado o cartao mostra o aviso e o link para incluir um')
        ok(pg.evaluate("document.querySelector('#inputGateway .dropdown-select-btn').disabled") and pg.inner_text('#resumoGateway') == '', 'o campo trava e nao ha resumo')
        clic('#btnSalvarForma'); pg.wait_for_timeout(300)
        ok(not visivel('#erroGateway'), 'e salvar nao exige gateway que nao existe')
        pg.evaluate("fecharDrawer()")
        ok('sem gateway' in pg.evaluate(FORMAS_LINHA, 'Cartão de crédito').lower(), 'a lista diz "sem gateway" no cartao')
        # a forma criada pelo usuario continua com o painel de sempre
        limpar(); ir(FORMAS); abrir('Carteira digital')
        ok(not visivel('#blocoGateway') and visivel('#campoConta') and visivel('#campoTarifacao'), 'a forma criada pelo usuario segue com conta e taxa proprias')
      except Exception as e:
        ok(False, 'a secao 2 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [3] PDV: a maquininha e a bandeira
    if secao(3, 'PDV: a maquininha e a bandeira'):
      try:
        venda(); receber('credito')
        r = rec()
        ok(r['gatewayId'] == 2 and r['bandeira'] == 'mastercard' and r['vezes'] == 1, 'o credito nasce com a maquininha da loja (Stone) e a bandeira padrao dela (Mastercard)')
        ok(pg.locator('[data-receb-maq]').count() == 0 and 'Stone — maquininha da loja' in lista(), 'com uma maquininha so, o campo nao aparece, e o nome dela vem no resumo')
        ok(pg.locator('[data-receb-band]').count() == 1 and txt('[data-receb-band] .dropdown-select-label') == 'Mastercard', 'a bandeira aparece, com a padrao marcada')
        ok(rotulos('[data-receb-band] .dropdown-select-item') == ['Visa', 'Mastercard', 'American Express', 'Diners Club', 'Elo', 'Hipercard', 'BNDES', 'Outro'], 'e oferece as bandeiras atendidas pela maquininha')
        ok(pg.evaluate("maquininhasDoTurno().map(g => g.id)") == [2], 'a InfinitePay (habilitada na loja) nao e oferecida como maquininha: o tipo dela nao e Outro')
        # duas maquininhas
        novo = novo_gateway(descricao='Cielo nova', bandeiras=['visa', 'elo'], bandeiraPadrao='elo', lojas=[1, 2])
        repintar()
        ok(pg.locator('[data-receb-maq]').count() == 1 and rotulos('[data-receb-maq] .dropdown-select-item') == ['Stone — maquininha da loja', 'Cielo nova'],
           'com duas maquininhas habilitadas na loja o campo aparece, so com as do tipo Outro dela: %s' % rotulos('[data-receb-maq] .dropdown-select-item'))
        ok(rec()['gatewayId'] == 2, 'a que ja estava na venda continua')
        # a de outra loja nao aparece
        gateway(3, situacao='habilitado', lojas=[2])
        repintar()
        ok(valores('[data-receb-maq] .dropdown-select-item') == [str(2), str(novo)], 'maquininha habilitada so para outra loja (Cielo antiga, da Desk Brands) nao aparece nesta')
        # padrao da forma
        param(formaGatewayPadrao=dict(credito=novo, debito=2))
        venda(); novo = novo_gateway(descricao='Cielo nova', bandeiras=['visa', 'elo'], bandeiraPadrao='elo', lojas=[1]); param(formaGatewayPadrao=dict(credito=novo, debito=2))
        receber('credito'); receber('debito')
        ok(rec(0)['gatewayId'] == novo and rec(0)['bandeira'] == 'elo' and txt('[data-receb-maq="0"] .dropdown-select-label') == 'Cielo nova',
           'o gateway padrao do credito (gravado em Formas) ja vem marcado, com a bandeira padrao dele (Elo)')
        ok(rec(1)['gatewayId'] == 2 and rec(1)['bandeira'] == 'mastercard', 'e o do debito, o dele (a Stone, Mastercard): cada forma com o seu padrao')
        # padrao que nao e desta loja: vale a primeira maquininha
        gateway(3, situacao='habilitado', lojas=[2]); param(formaGatewayPadrao=dict(credito=3, debito=3))
        venda(); gateway(3, situacao='habilitado', lojas=[2]); param(formaGatewayPadrao=dict(credito=3, debito=3)); receber('credito')
        ok(rec()['gatewayId'] == 2, 'gateway padrao da forma que nao e desta loja nao vale: entra a primeira maquininha da loja')
        # trocar a maquininha recalcula tudo
        venda(); novo = novo_gateway(descricao='Cielo nova', bandeiras=['visa', 'elo'], bandeiraPadrao='elo', lojas=[1])
        condicao(novo, 'credito', 'elo', 1, taxa=4.5, prazo=20)
        receber('credito')
        ok('Taxa da maquininha (3,00%)' in lista() and rec()['bandeira'] == 'mastercard', 'na Stone, Mastercard 1x: 3,00%')
        troca('data-receb-maq', 0, novo)
        r = rec()
        ok(r['gatewayId'] == novo and r['bandeira'] == 'elo' and 'Taxa da maquininha (4,50%)' in lista() and r['parcelas'][0]['dias'] == (mais_uteis(HOJE, 20) - HOJE).days,
           'trocar a maquininha refaz a bandeira (a Mastercard nao existe nela: entra a padrao, Elo), a taxa (4,50%) e o vencimento (20 dias uteis)')
        troca('data-receb-maq', 0, 2)
        ok(rec()['bandeira'] == 'elo' and 'Taxa da maquininha (3,00%)' in lista() and rec()['parcelas'][0]['dias'] == (mais_uteis(HOJE, 31) - HOJE).days, 'voltar para a Stone mantem a Elo (ela existe la) e a taxa e o prazo voltam')
        # a bandeira recalcula o credito, mas nao o debito
        venda(); condicao(2, 'credito', 'amex', 1, taxa=5.5)
        receber('credito')
        ok(rec()['bandeira'] == 'mastercard' and pg.evaluate('taxaDe(venda.recebimentos[0])') == 7.5, 'Mastercard 1x: 3,00% de 249,90 = 7,50')
        troca('data-receb-band', 0, 'amex')
        ok(rec()['bandeira'] == 'amex' and pg.evaluate('taxaDe(venda.recebimentos[0])') == 13.74 and 'Taxa da maquininha (5,50%)' in lista(), 'trocar para American Express: 5,50% = 13,74. A taxa do credito muda com a bandeira')
        venda(); condicao(2, 'credito', 'amex', 1, taxa=5.5)
        receber('debito')
        ok(pg.evaluate('taxaDe(venda.recebimentos[0])') == 2 and 'Taxa da maquininha (R$ 2,00)' in lista(), 'o debito paga a tarifa de R$ 2,00 do gateway (taxa 0%)')
        ok('A bandeira não muda a taxa do débito' in lista(), 'e a tela diz que a bandeira nao muda a taxa do debito')
        troca('data-receb-band', 0, 'amex')
        ok(pg.evaluate('taxaDe(venda.recebimentos[0])') == 2 and rec()['bandeira'] == 'amex', 'trocar a bandeira do debito marca a bandeira, e a taxa nao muda')
        # parcelas: so as que tem condicao
        venda(); receber('credito')
        ok(valores('[data-receb-vezes] .dropdown-select-item') == [str(n) for n in range(1, 13)], 'o menu de parcelas tem 1x a 12x quando o gateway tem as doze')
        troca('data-receb-vezes', 0, 7)
        tirar_condicoes(2, 'credito', 'mastercard', 7); repintar()
        ok(valores('[data-receb-vezes] .dropdown-select-item') == [str(n) for n in range(1, 13) if n != 7], 'sem a linha de 7x no gateway, o menu nao oferece 7x')
        ok(rec()['vezes'] == 6, 'e a venda que estava em 7x passa para a parcela mais proxima que existe (6x)')
        tirar_condicoes(2, 'credito', 'visa'); troca('data-receb-band', 0, 'visa')
        ok('não tem condição para Visa em' in pend() and pg.locator('[data-receb-vezes]').count() == 0 and 'não tem condição' in lista(), 'bandeira sem linha nenhuma no gateway: a venda diz e nao oferece parcelas')
        clic('#btnFinalizar'); pg.wait_for_timeout(350)
        ok(pg.evaluate('momento') == 'finalizar' and 'não tem condição' in modal(), 'e nao deixa finalizar')
        confirmar(senha=False)
        venda(); tirar_condicoes(2, 'debito', ''); receber('debito')
        ok('não tem condição para débito' in pend(), 'debito sem a linha "Cartao de debito" no gateway: a venda diz e nao fecha')
        # loja sem maquininha
        venda(loja=2, sku='CAM-BSC-PT'); repintar()
        ok(valores('#menuAddReceb .dropdown-select-item') == ['dinheiro', 'pix', 'boleto', 'crediario', 'cheque', 'deposito'], 'na Desk Brands (so a InfinitePay, que nao e maquininha) o cartao nao e oferecido: %s' % valores('#menuAddReceb .dropdown-select-item'))
        ok(visivel('#avisoSemMaquininha') and 'Cartão de débito e Cartão de crédito não pode ser usado nesta venda' in txt('#avisoSemMaquininha') and 'Desk Brands' in txt('#avisoSemMaquininha')
           and pg.get_attribute('#linkSemMaquininha', 'href') == '../integracoes/pagina-integracoes-gateways.html', 'a tela diz o motivo, com o link para Gateways')
        pg.evaluate("adicionarRecebimento('credito')"); pg.wait_for_timeout(300)
        ok('não há maquininha habilitada nesta loja' in modal() and pg.evaluate('venda.recebimentos.length') == 0, 'e adicionar o cartao a forca avisa e nao adiciona')
        confirmar(senha=False)
        gateway(3, situacao='habilitado', lojas=[2]); repintar()
        ok('credito' in valores('#menuAddReceb .dropdown-select-item') and 'debito' in valores('#menuAddReceb .dropdown-select-item') and not visivel('#avisoSemMaquininha'), 'habilitada uma maquininha na loja, o cartao volta a ser oferecido e o aviso some')
        receber('credito')
        ok(rec()['gatewayId'] == 3 and rec()['bandeira'] == 'visa', 'e a venda usa a maquininha dela (Cielo antiga, bandeira padrao Visa)')
        gateway(3, situacao='desabilitado'); repintar()
        ok('não há maquininha habilitada nesta loja' in pend() and 'Sem maquininha habilitada' in lista() and pg.evaluate('rec = venda.recebimentos[0]; rec.parcelas.length') == 0,
           'recebimento de cartao que ficou sem maquininha (o gateway foi desabilitado) trava a venda, com o motivo')
        venda(loja=3, sku='CAB-HDM-009'); repintar()
        ok('credito' not in valores('#menuAddReceb .dropdown-select-item') and visivel('#avisoSemMaquininha'), 'a Desk Tech, sem gateway nenhum, tambem nao oferece cartao')
        # venda guardada antes desta entrega (sem maquininha nem bandeira) entra em ordem
        venda()
        pg.evaluate("venda.recebimentos.push({ chave: 'credito', valor: 100, digitado: true, recebido: null, parcelas: [], expr: '1x', vezes: 3, repassa: true }); gravar();")
        ir(PDV); pg.wait_for_timeout(300)
        r = rec()
        ok(pg.evaluate('momento') == 'finalizar' and r['gatewayId'] == 2 and r['bandeira'] == 'mastercard' and r['vezes'] == 3 and r['parcelas'][0]['valor'] == 100,
           'venda em andamento gravada antes (cartao sem maquininha nem bandeira) abre em ordem: Stone, Mastercard, 3x, e o repasse antigo e ignorado (a Stone nao repassa)')
      except Exception as e:
        ok(False, 'a secao 3 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [4] PDV: o repasse
    if secao(4, 'PDV: o repasse pelas regras do gateway'):
      try:
        def cartao3x(**gw):
            venda(); gateway(2, **gw)
            receber('credito'); troca('data-receb-vezes', 0, 3)

        cartao3x(repassar='nao')
        ok(pg.locator('#listaReceb .switch-row').count() == 0 and pg.locator('[data-receb-repassa]').count() == 0 and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9,
           'Nao: sem repasse e o switch some: o cliente passa o valor da venda')
        cartao3x(repassar='sim', repassarAPartir=1)
        ok(pg.locator('#listaReceb .switch.on.travado').count() == 1 and pg.locator('[data-receb-repassa]').count() == 0 and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99,
           'Sim: repassa sempre, travado (o switch aparece ligado e sem controle): 249,90 / (1 - 4,25%) = 260,99')
        clic('#listaReceb .switch.travado'); pg.wait_for_timeout(200)
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99 and pg.evaluate('taxaDe(venda.recebimentos[0])') == 11.09 and '+ R$ 11,09' in txt('#finAcrescimo'), 'clicar no travado nao muda nada; a taxa de 11,09 vira acrescimo na venda')
        cartao3x(repassar='opcional', repassarAPartir=1)
        ok(pg.locator('[data-receb-repassa]').count() == 1 and pg.locator('#listaReceb .switch.on').count() == 0 and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'Opcional: o switch e livre e nasce desligado')
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99 and rec()['repassa'] is True and modal() == '', 'ligar repassa a taxa, sem senha')
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'e desligar volta ao valor da venda')
        # opcional com liberacao do gerente
        cartao3x(repassar='gerente', repassarAPartir=1)
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(400)
        ok(senha_pedida() and 'Liberar o repasse da taxa' in modal() and 'Stone — maquininha da loja' in modal() and rec()['repassa'] is False, 'Opcional com liberacao do gerente: ligar pede a senha dele, e diz o que libera')
        cancelar()
        ok(rec()['repassa'] is False and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'cancelar a senha deixa o repasse desligado')
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(400)
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
        ok(rec()['repassa'] is False and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('has-error')"), 'confirmar sem a senha e barrado')
        confirmar()
        ok(rec()['repassa'] is True and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99, 'com a senha o repasse liga')
        ok(any(e['chave'] == 'pdvRepasseTaxa' and e['senha'] and 'Liberar o repasse' in e['detalhe'] for e in log()), 'e a liberacao entra no Registro de atividades, com a marca de senha')
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(300)
        ok(rec()['repassa'] is False and modal() == '', 'desligar nao pede senha')
        venda(confirmacoes=dict(pdvRepasseTaxa=False)); gateway(2, repassar='gerente'); receber('credito'); troca('data-receb-vezes', 0, 3)
        clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(300)
        ok(rec()['repassa'] is True and modal() == '' and any(e['chave'] == 'pdvRepasseTaxa' and not e['senha'] for e in log()), 'com a senha desligada em Confirmacoes de senha, liga direto, e o registro grava sem a marca de senha')
        # a partir da parcela
        cartao3x(repassar='opcional', repassarAPartir=3)
        ok(pg.locator('[data-receb-repassa]').count() == 1, 'a partir da 3ª parcela: em 3x o switch existe')
        vez2 = lambda n: (troca('data-receb-vezes', 0, n))
        vez2(2)
        ok(pg.locator('[data-receb-repassa]').count() == 0 and 'a partir da 3ª parcela' in lista() and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'abaixo de 3x nao ha repasse: sem switch, com o aviso da regra')
        cartao3x(repassar='sim', repassarAPartir=3)
        vez2(2)
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9 and pg.locator('#listaReceb .switch').count() == 0, 'Sim a partir da 3ª: em 2x a loja paga a taxa')
        vez2(3)
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99, 'e em 3x o repasse comeca')
        # os rotulos das parcelas contam o repasse so onde ele vale
        ok(txt('[data-receb-vezes] .dropdown-select-label').startswith('3x de R$ 87,00'), 'o rotulo de 3x ja traz o repasse (260,99 / 3 = 87,00)')
        menu = rotulos('[data-receb-vezes] .dropdown-select-item')
        ok(menu[1].startswith('2x de R$ 124,95') and menu[0].startswith('1x de R$ 249,90'), 'e os de 1x e 2x, onde nao ha repasse, saem sem ele (124,95 e 249,90)')
        # debito
        venda(); gateway(2, repassar='sim', repassarAPartir=1); receber('debito')
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 251.9 and pg.evaluate('taxaDe(venda.recebimentos[0])') == 2, 'o debito tambem segue a regra: Sim repassa a tarifa de R$ 2,00 (251,90)')
        venda(); gateway(2, repassar='sim', repassarAPartir=2); receber('debito')
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'com "a partir da 2ª parcela" o debito (1x) nao repassa')
        # a escolha do operador sobrevive ao F5
        cartao3x(repassar='opcional', repassarAPartir=1); clic('[data-receb-repassa="0"]'); pg.wait_for_timeout(250)
        ir(PDV); pg.wait_for_timeout(300)
        ok(rec()['repassa'] is True and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 260.99, 'o repasse ligado fica gravado: depois do F5 continua ligado')
        gateway(2, repassar='nao'); repintar()
        ok(pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9 and pg.locator('[data-receb-repassa]').count() == 0, 'e se o gateway deixar de repassar, a venda segue o gateway')
      except Exception as e:
        ok(False, 'a secao 4 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [5] PDV: o titulo, a conta, o caixa
    if secao(5, 'PDV: o titulo (vencimento, taxa, conta, maquininha e bandeira) e o caixa'):
      try:
        venda(); receber('credito')
        v31 = mais_uteis(HOJE, 31)
        ok(rec()['parcelas'] == [dict(dias=(v31 - HOJE).days, valor=249.9)] and ('A loja recebe em ' + br(v31) + ' (31 dias úteis)') in lista(),
           'o titulo vence pelo prazo do gateway em DIAS UTEIS: hoje mais 31 dias uteis (%s)' % br(v31))
        ok((v31 - HOJE).days >= 43, 'e nao em 31 dias corridos: 31 dias uteis sao no minimo 43 dias no calendario (deu %d)' % (v31 - HOJE).days)
        condicao(2, 'credito', 'mastercard', 1, prazo=1); repintar()
        um = mais_uteis(HOJE, 1)
        ok(rec()['parcelas'][0]['dias'] == (um - HOJE).days and br(um) in lista() and '(1 dia útil)' in lista(), 'prazo de 1 dia util: vence no dia util seguinte (%s)' % br(um))
        calc = lambda y, m, d: pg.evaluate("(a) => dataBr(vencimentoDoCartao(venda.recebimentos[0], new Date(a[0], a[1] - 1, a[2])))", [y, m, d])
        ok(calc(2026, 10, 23) == '26/10/2026', 'vendida numa sexta, com 1 dia util, vence na segunda (nao no sabado)')
        condicao(2, 'credito', 'mastercard', 1, prazo=2); repintar()
        ok(calc(2026, 10, 23) == '27/10/2026' and calc(2026, 10, 22) == '26/10/2026', 'com 2 dias uteis: da sexta vai a terca; da quinta, a segunda (o fim de semana nao conta)')
        condicao(2, 'credito', 'mastercard', 1, prazo=1); repintar()
        ok(calc(2026, 10, 9) == '13/10/2026', 'o feriado nacional de data fixa tambem nao conta: da sexta 09/10, 1 dia util e terca 13/10 (segunda 12/10 e feriado)')
        condicao(2, 'credito', 'mastercard', 1, prazo=0); repintar()
        ok(calc(2026, 10, 24) == '24/10/2026', 'prazo zero e o mesmo dia, ate num sabado')
        gateway(2, proximoDiaUtil=True); condicao(2, 'credito', 'mastercard', 1, prazo=1); repintar()
        ok(rec()['parcelas'][0]['dias'] == (um - HOJE).days and calc(2026, 10, 23) == '26/10/2026', 'um "proximo dia util" gravado de antes e ignorado: o prazo e sempre em dias uteis')
        # a venda finalizada: conta do gateway, maquininha e bandeira no titulo
        venda(); novo = novo_gateway(descricao='Cielo nova', bandeiras=['visa', 'elo'], bandeiraPadrao='elo', lojas=[1]); condicao(2, 'credito', 'amex', 3, taxa=6.0, prazo=33)
        venc = mais_uteis(HOJE, 33)
        receber('dinheiro'); pg.fill('[data-receb-valor="0"]', '100'); pg.locator('[data-receb-valor="0"]').blur(); pg.wait_for_timeout(250)
        receber('credito'); troca('data-receb-band', 1, 'amex'); troca('data-receb-vezes', 1, 3)
        ok(rec(1)['parcelas'][0]['dias'] == (venc - HOJE).days and rec(1)['parcelas'][0]['valor'] == 149.9 and pg.evaluate('taxaDe(venda.recebimentos[1])') == 8.99, 'a condicao da bandeira e das vezes decide: American Express 3x, 33 dias uteis e 6,00% de 149,90 = 8,99')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        v = pg.evaluate('ultimaVenda'); c = v['recebimentos'][1]
        ok(c['contaId'] == 'gw2' and c['gatewayId'] == 2 and c['gatewayNome'] == 'Stone — maquininha da loja' and c['bandeira'] == 'amex' and c['bandeiraNome'] == 'American Express' and c['vezes'] == 3,
           'a venda grava o gateway e a bandeira em cada recebimento de cartao, e a conta e a do gateway: %s' % {k: c[k] for k in ('contaId', 'gatewayId', 'bandeira')})
        ok(c['vencimento'] == venc.isoformat() and c['parcelas'] == [dict(dias=(venc - HOJE).days, valor=149.9)] and c['taxa'] == 8.99 and c['prazoFixo'] is True and c['repasse'] is False, 'com o vencimento (hoje mais 33 dias uteis), a taxa e UM titulo no valor cobrado')
        ok(c['historico'] == 'Cartão de crédito · American Express · 3x · Stone — maquininha da loja', 'e o historico do titulo diz forma, bandeira, vezes e maquininha: %s' % c['historico'])
        ok(v['recebimentos'][0]['gatewayId'] is None and v['recebimentos'][0]['historico'] is None and v['recebimentos'][0]['contaId'] == 1, 'o dinheiro continua sem gateway e entra na conta Caixa')
        g = pg.inner_text('#concGerado')
        ok('1 título em Contas a Receber, somando R$ 149,90 (Cartão de crédito em 3x)' in g and 'a receber de Stone — maquininha da loja' in g and 'Maquininha Stone — maquininha da loja, bandeira American Express' in g and ('Vencimento em ' + br(venc)) in g,
           'a tela da venda concluida diz titulo, conta do gateway, maquininha, bandeira e vencimento: %s' % [l for l in g.split(chr(10)) if 'título' in l][:1])
        ok('Taxa de R$ 8,99 em Cartão de crédito' in g and 'descontada no dia seguinte' in g, 'e a taxa, descontada quando o gateway diz (dia seguinte, o da Stone)')
        # o caixa: cartao nao entra na gaveta
        ok(pg.evaluate('dinheiroNaGaveta(turno)') == 250 and pg.evaluate('recebidoNaForma(turno, "credito")') == 149.9 and pg.evaluate('recebidoNaForma(turno, "dinheiro")') == 100,
           'no caixa o cartao nao entra na gaveta (troco 150 + dinheiro 100 = 250) e aparece por forma, pelo valor que passou na maquininha (149,90)')
        clic('#btnDetalhesCaixa'); pg.wait_for_timeout(300)
        d = pg.inner_text('#caixaCorpo')
        ok('1 · R$ 249,90' in d and 'Cartão de crédito' in d, 'o resumo do turno conta a venda e lista o cartao: %s' % d.replace(chr(10), ' ')[:120])
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ir(PDV); pg.wait_for_timeout(300)
        ok(pg.evaluate('turno.vendas[0].recebimentos[1].gatewayNome') == 'Stone — maquininha da loja' and pg.evaluate('turno.vendas[0].recebimentos[1].historico').endswith('Stone — maquininha da loja'), 'depois do F5 a venda continua com a maquininha e a bandeira gravadas')
        # o debito finalizado
        clic('#btnOutraVenda'); pg.wait_for_timeout(300)
        pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', 'CAR-33W-01'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
        clic('#btnContinuar'); pg.wait_for_timeout(400)
        receber('debito'); troca('data-receb-band', 0, 'visa')
        ok(rec()['parcelas'] == [dict(dias=(mais_uteis(HOJE, 2) - HOJE).days, valor=97.55)] and pg.evaluate('taxaDe(venda.recebimentos[0])') == 2, 'o debito vence em 2 dias uteis, com tarifa de R$ 2,00, qualquer que seja a bandeira (a bancada tem uma linha so de debito)')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        g = pg.inner_text('#concGerado')
        ok('Taxa de R$ 2,00 em Cartão de débito' in g and 'bandeira Visa' in g and ('Vencimento em ' + br(mais_uteis(HOJE, 2))) in g, 'o titulo do debito: tarifa de R$ 2,00, bandeira Visa, vencimento em 2 dias uteis')
        # o recibo segue sem vencimento de cartao
        clic('#btnRecibo'); pg.wait_for_timeout(250)
        r = pg.evaluate("document.getElementById('folhaImpressao').innerText")
        ok('Cartão de débito' in r and 'venc.' not in r, 'o recibo diz o cartao, sem vencimento para o cliente')
      except Exception as e:
        ok(False, 'a secao 5 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [6] o catalogo, o Pedido de Venda e o que nao mudou
    if secao(6, 'O catalogo, o Pedido de Venda e o que nao mudou'):
      try:
        for arq in CATALOGOS:
            ok("chave:'pdvRepasseTaxa'" in fonte(arq) and re.search(r"chave:'pdvRepasseTaxa'.*grupo:'Vendas'.*exigePadrao:true", fonte(arq)) is not None, '%s conhece a acao de liberar o repasse (grupo Vendas, com senha por padrao)' % arq.replace('pagina-', ''))
        limpar(); ir(SENHAS)
        ok('Liberar o repasse da taxa do cartão ao cliente no PDV' in pg.evaluate("document.body.textContent"), 'a tela de Confirmacoes de senha mostra a acao')
        # o Pedido de Venda le a venda do PDV (so o total) e nao quebra
        venda(); gateway(2, repassar='sim', repassarAPartir=1); receber('credito'); troca('data-receb-vezes', 0, 3)
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        total_venda = pg.evaluate('ultimaVenda.total')
        ir(PEDIDOS); pg.fill('#campoBusca', 'PDV-0001'); pg.wait_for_timeout(300)
        t = pg.inner_text('#corpoTabela') if pg.locator('#corpoTabela').count() else pg.inner_text('.main')
        ok(total_venda == 260.99 and 'PDV-0001' in t, 'o Pedido de Venda lista a venda do PDV pelo total (260,99, com o repasse): ele nao le taxa nem prazo de cartao e segue como estava')
        # so o PDV e Formas de recebimento leem os campos do cartao
        leem = [_os.path.basename(c) for c in localiza.caminhos() if re.search(r'taxasParcela|prazoUteis|parcelasMax', open(c, encoding='utf-8').read())]
        ok(sorted(leem) == sorted([PDV, FORMAS]), 'nenhuma outra tela le prazo, parcelas ou taxa por parcela dos cartoes: %s' % leem)
      except Exception as e:
        ok(False, 'a secao 6 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [7] o exemplo real no PDV
    if secao(7, 'O exemplo real no PDV: InfinitePay Bronze, dias uteis, debito por bandeira e loja sem maquininha'):
      try:
        venda(bancada=False); receber('credito')
        r = rec()
        ok(r['gatewayId'] == 2 and r['bandeira'] == 'visa' and r['vezes'] == 1, 'o credito nasce na maquininha da loja, a InfinitePay Maquininha Bronze, com a bandeira padrao Visa')
        ok(pg.locator('[data-receb-maq]').count() == 0 and 'InfinitePay Maquininha — Bronze' in lista() and pg.evaluate("maquininhasDoTurno().map(g => g.id)") == [2],
           'a Bronze e a unica maquininha habilitada da loja (a loja virtual e de outro tipo): o campo de maquininha nao aparece')
        ok(rotulos('[data-receb-band] .dropdown-select-item') == ['Visa', 'Mastercard', 'Elo', 'American Express', 'Hipercard'], 'as bandeiras oferecidas sao as cinco da maquininha: %s' % rotulos('[data-receb-band] .dropdown-select-item'))
        ok('Taxa da maquininha (3,15%)' in lista() and pg.evaluate('taxaDe(venda.recebimentos[0])') == 7.87, 'Visa em 1x na Bronze: 3,15%, e 3,15% de 249,90 = 7,87')
        um = mais_uteis(HOJE, 1)
        ok(rec()['parcelas'][0]['dias'] == (um - HOJE).days and ('A loja recebe em ' + br(um) + ' (1 dia útil)') in lista(), 'vence em 1 dia util (%s), como a InfinitePay paga' % br(um))
        ok(pg.locator('[data-receb-repassa]').count() == 1 and pg.evaluate('cobradoDe(venda.recebimentos[0])') == 249.9, 'repasse Opcional a partir da 1a parcela: o switch existe e nasce desligado')
        troca('data-receb-vezes', 0, 12)
        ok('Taxa da maquininha (12,40%)' in lista(), 'Visa em 12x: 12,40%')
        troca('data-receb-band', 0, 'elo')
        ok(rec()['bandeira'] == 'elo' and 'Taxa da maquininha (13,41%)' in lista(), 'Elo em 12x: 13,41% (Elo, American Express e Hipercard tem outra tabela)')
        troca('data-receb-vezes', 0, 1)
        ok('Taxa da maquininha (4,91%)' in lista(), 'Elo em 1x: 4,91%')
        # o debito e por bandeira
        venda(bancada=False); receber('debito')
        ok(rec()['bandeira'] == 'visa' and 'Taxa da maquininha (1,37%)' in lista() and pg.evaluate('taxaDe(venda.recebimentos[0])') == 3.42, 'debito na Visa: 1,37%, e 1,37% de 249,90 = 3,42')
        ok('O débito usa a taxa da bandeira escolhida' in lista() and 'A bandeira não muda a taxa do débito' not in lista(), 'e a dica diz que o debito usa a taxa da bandeira (nao a de "uma linha so")')
        troca('data-receb-band', 0, 'elo')
        ok('Taxa da maquininha (2,58%)' in lista() and pg.evaluate('taxaDe(venda.recebimentos[0])') == 6.45, 'trocar para Elo muda o debito: 2,58%, e 2,58% de 249,90 = 6,45')
        troca('data-receb-band', 0, 'mastercard')
        ok('Taxa da maquininha (1,37%)' in lista(), 'Mastercard no debito volta a 1,37% (Visa e Mastercard tem a mesma tabela)')
        troca('data-receb-band', 0, 'hipercard')
        ok('Taxa da maquininha (2,58%)' in lista(), 'e Hipercard e 2,58% (o grupo da Elo)')
        ok(rec()['parcelas'][0]['dias'] == (mais_uteis(HOJE, 1) - HOJE).days, 'o debito tambem vence em 1 dia util')
        # a mesma venda finalizada grava a Bronze e a bandeira
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        c = pg.evaluate('ultimaVenda')['recebimentos'][0]
        ok(c['contaId'] == 'gw2' and c['gatewayNome'] == 'InfinitePay Maquininha — Bronze' and c['bandeira'] == 'hipercard' and c['taxa'] == 6.45, 'a venda grava a maquininha (conta gw2), a bandeira e a taxa do debito')
        # a Desk Brands e a Desk Tech tambem tem a Bronze
        venda(loja=2, sku='CAM-BSC-PT', bancada=False); repintar()
        ok('credito' in valores('#menuAddReceb .dropdown-select-item') and 'debito' in valores('#menuAddReceb .dropdown-select-item') and not visivel('#avisoSemMaquininha'), 'a Desk Brands tem a Bronze (lojas 1, 2 e 3): oferece o cartao')
        # loja sem maquininha: a Bronze desabilitada dentro do teste
        venda(bancada=False); gateway(2, situacao='desabilitado'); repintar()
        ok('credito' not in valores('#menuAddReceb .dropdown-select-item') and 'debito' not in valores('#menuAddReceb .dropdown-select-item') and visivel('#avisoSemMaquininha'),
           'com a Bronze desabilitada a loja fica sem maquininha: o cartao some e o aviso aparece')
        gateway(3, situacao='habilitado'); repintar()
        receber('credito')
        ok(rec()['gatewayId'] == 3 and 'Taxa da maquininha (2,89%)' in lista() and not visivel('#avisoSemMaquininha'), 'habilitada a Prata, ela vira a maquininha da loja: Visa 1x a 2,89%')
        troca('data-receb-band', 0, 'elo'); troca('data-receb-vezes', 0, 12)
        ok('Taxa da maquininha (11,88%)' in lista(), 'Prata, Elo em 12x: 11,88%')
      except Exception as e:
        ok(False, 'a secao 7 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [8] o desconto Pix e dinheiro
    if secao(8, 'O desconto Pix e dinheiro: a taxa do credito a vista, sobre o valor que o recebimento quita'):
      try:
        rs = lambda v: 'R$ ' + ('%.2f' % v).replace('.', ',')
        PCT = 3.15
        def com_desconto(**p):
            venda(bancada=False, pdvDescontoAVista=True, **p)
        # tudo no Pix
        com_desconto(); receber('pix')
        pago = pago_avista(249.9, PCT); desc = round(249.9 - pago, 2)
        ok(pg.evaluate('descontoAVistaPct()') == PCT, 'o percentual e a taxa do credito 1x da bandeira padrao (Visa) da maquininha da loja (Bronze): 3,15%')
        ok(pg.evaluate('pagoDe(venda.recebimentos[0])') == pago == 242.03 and pg.evaluate('descontoDe(venda.recebimentos[0])') == desc == 7.87, 'Pix de 249,90: o cliente paga 242,03 e o desconto e 7,87')
        ok(visivel('#finDescAVistaLinha') and txt('#finDescAVistaRotulo') == 'Desconto Pix/dinheiro (3,15%)' and txt('#finDescAVista').endswith('R$ 7,87') and txt('#finTotal') == rs(pago),
           'a venda mostra a linha "Desconto Pix/dinheiro (3,15%%) − R$ 7,87" e o total a pagar 242,03: %s | %s' % (txt('#finDescAVista'), txt('#finTotal')))
        ok('Quita R$ 249,90' in lista() and 'o cliente paga R$ 242,03' in lista() and 'desconto à vista de 3,15%' in lista(), 'o recebimento diz o que quita e o que o cliente paga com o desconto')
        ok('Pode finalizar' in pend(), 'os recebimentos fecham com o total ja descontado: pode finalizar')
        ok(visivel('#avisoAVista') and 'InfinitePay Maquininha — Bronze' in txt('#avisoAVista') and 'Visa' in txt('#avisoAVista') and visivel('#btnTirarDescAVista'), 'o aviso diz de onde vem o percentual (maquininha e bandeira) e oferece tirar o desconto')
        ok(pg.evaluate('pagoAVista(100, 3.15)') == 96.85, 'R$ 100,00 em Pix: o cliente paga R$ 96,85')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        v = pg.evaluate('ultimaVenda')
        ok(v['total'] == 242.03 and v['subtotal'] == 249.9 and v['descontoAVista'] == dict(pct=3.15, valor=7.87, gatewayId=2) and v['recebimentos'][0]['cobrado'] == 242.03 and v['recebimentos'][0]['desconto'] == 7.87,
           'a venda grava o total 242,03 (e e esse total que a comissao e a meta leem) e o registro descontoAVista { pct, valor, gatewayId }: %s' % v['descontoAVista'])
        g = pg.inner_text('#concGerado')
        ok('R$ 242,03 entram na hora em' in g and 'já com o desconto à vista de R$ 7,87' in g, 'a conta do Pix recebe o valor ja descontado: 242,03')
        clic('#btnRecibo'); pg.wait_for_timeout(250)
        rc = pg.evaluate("document.getElementById('folhaImpressao').innerText")
        ok('Desconto Pix/dinheiro (3,15%)' in rc and 'R$ 7,87' in rc and 'R$ 242,03' in rc, 'o recibo traz a linha do desconto e o valor a pagar')
        # venda dividida: so o dinheiro desconta
        com_desconto(); receber('dinheiro'); pg.fill('[data-receb-valor="0"]', '100'); pg.locator('[data-receb-valor="0"]').blur(); pg.wait_for_timeout(250)
        receber('credito')
        ok(rec(1)['valor'] == 149.9 and pg.evaluate('descontoDe(venda.recebimentos[0])') == 3.15 and pg.evaluate('descontoDe(venda.recebimentos[1])') == 0 and pg.evaluate('cobradoDe(venda.recebimentos[1])') == 149.9,
           'dinheiro de 100 + cartao de 149,90: o desconto (3,15) e so do dinheiro; o cartao passa o valor cheio')
        ok(pg.evaluate('totalAPagar()') == 246.75 and txt('#finTotal') == 'R$ 246,75' and txt('#finDescAVista').endswith('R$ 3,15'), 'o total a pagar e 249,90 menos 3,15 = 246,75')
        ok('Pode finalizar' in pend(), 'e os recebimentos fecham')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        v = pg.evaluate('ultimaVenda')
        ok(v['total'] == 246.75 and v['descontoAVista']['valor'] == 3.15 and v['recebimentos'][0]['desconto'] == 3.15 and v['recebimentos'][1]['desconto'] == 0 and v['recebimentos'][1]['cobrado'] == 149.9,
           'a venda dividida grava o desconto so no dinheiro')
        ok(pg.evaluate('dinheiroNaGaveta(turno)') == round(150 + 96.85, 2), 'a gaveta recebe o dinheiro ja descontado: troco 150 + 96,85 = 246,85')
        # dinheiro com troco: o troco e sobre o valor descontado
        com_desconto(); receber('dinheiro'); pg.fill('[data-receb-valor="0"]', '50'); pg.locator('[data-receb-valor="0"]').blur(); pg.wait_for_timeout(250)
        ok('Quita R$ 50,00' in lista() and 'o cliente paga R$ 48,43' in lista(), 'dinheiro de 50,00: "quita R$ 50,00 · com o desconto à vista de 3,15% o cliente paga R$ 48,43"')
        pg.fill('[data-receb-recebido="0"]', '100'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
        ok(pg.evaluate('trocoDe(venda.recebimentos[0])') == 51.57 and txt('#totTroco') == 'R$ 51,57', 'o cliente entrega 100,00: o troco e 51,57 (100,00 menos 48,43), e nao 50,00')
        ok(pago_avista(50, PCT) == 48.43, 'meio centavo sobe: 50,00 a 3,15% fica 48,43 (e nao 48,42)')
        # centavos: duas partes em Pix fecham sem sobrar centavo
        com_desconto(); receber('pix'); pg.fill('[data-receb-valor="0"]', '33,33'); pg.locator('[data-receb-valor="0"]').blur(); pg.wait_for_timeout(250)
        receber('dinheiro')
        p1, p2 = pago_avista(33.33, PCT), pago_avista(216.57, PCT)
        ok(rec(1)['valor'] == 216.57 and pg.evaluate('totalAPagar()') == round(p1 + p2, 2) and 'Pode finalizar' in pend(), 'Pix de 33,33 + dinheiro de 216,57: cada um e arredondado em centavos e o total fecha sem sobrar centavo (%s)' % rs(p1 + p2))
        # o desconto manual vem primeiro
        com_desconto(); pg.fill('#finDesconto', '10%'); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
        receber('pix')
        base = round(249.9 - 24.99, 2)
        ok(rec()['valor'] == base and pg.evaluate('totalAPagar()') == pago_avista(base, PCT), 'o desconto manual (10%%) vem primeiro: o Pix quita %s e o desconto a vista e sobre esse valor' % rs(base))
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        v = pg.evaluate('ultimaVenda')
        ok(v['desconto'] == 24.99 and v['descontoAVista']['valor'] == round(base - pago_avista(base, PCT), 2) and v['total'] == pago_avista(base, PCT), 'a venda grava o desconto manual e o desconto a vista, separados')
        # so Pix e dinheiro
        com_desconto()
        res = pg.evaluate("['pix','dinheiro','credito','debito','boleto','crediario','cheque','deposito','vale'].map(c => descontoDe({ chave: c, valor: 100 }))")
        ok(res == [3.15, 3.15, 0, 0, 0, 0, 0, 0, 0], 'so Pix e dinheiro descontam: cartao, boleto, crediario, cheque, deposito e vale-compra nao: %s' % res)
        # sem maquininha na loja
        com_desconto(); gateway(2, situacao='desabilitado'); receber('pix')
        ok(pg.evaluate('descontoAVistaPct()') == 0 and not visivel('#finDescAVistaLinha') and not visivel('#avisoAVista') and txt('#finTotal') == 'R$ 249,90', 'loja sem maquininha habilitada: sem desconto, o Pix paga o valor cheio')
        com_desconto(loja=3, sku='CAB-HDM-009'); gateway(2, lojas=[1, 2]); receber('pix')
        ok(pg.evaluate('descontoAVistaPct()') == 0 and not visivel('#finDescAVistaLinha'), 'a Desk Tech sem maquininha habilitada tambem nao tem desconto')
        # desligado em Configuracoes > PDV
        venda(bancada=False, pdvDescontoAVista=False); receber('pix')
        ok(pg.evaluate('descontoAVistaPct()') == 0 and not visivel('#finDescAVistaLinha') and 'o cliente paga' not in lista(), 'com o interruptor desligado em Configuracoes > PDV, o Pix paga o valor cheio')
        # subir de nivel: o desconto acompanha
        com_desconto(); gateway(2, situacao='desabilitado'); gateway(3, situacao='habilitado'); receber('pix')
        ok(pg.evaluate('descontoAVistaPct()') == 2.89 and 'InfinitePay Maquininha — Prata' in txt('#avisoAVista') and txt('#finTotal') == rs(pago_avista(249.9, 2.89)),
           'a loja sobe da Bronze para a Prata: o desconto passa a 2,89%% sozinho (Pix de 249,90 paga %s)' % rs(pago_avista(249.9, 2.89)))
        com_desconto(); gateway(4, situacao='habilitado'); param(pdvDescontoAVista=True, formaGatewayPadrao=dict(credito=4)); receber('pix')
        ok(pg.evaluate('descontoAVistaPct()') == 2.79 and 'InfinitePay Maquininha — Ouro' in txt('#avisoAVista'), 'o gateway padrao do credito em Formas (Ouro) e o que vale: 2,79%')
        gateway(4, lojas=[2]); repintar()
        ok(pg.evaluate('descontoAVistaPct()') == 3.15, 'padrao de Formas que nao e da loja nao vale: cai na primeira maquininha da loja (Bronze, 3,15%)')
        # tirar o desconto da venda: com senha
        com_desconto(); receber('pix')
        clic('#btnTirarDescAVista'); pg.wait_for_timeout(300)
        ok(senha_pedida() and 'Tirar o desconto à vista de 3,15%' in modal() and '7,87' in modal() and 'Quem tirou:' in modal(), 'tirar o desconto pede a senha e diz quanto e quem tira: %s' % modal()[:100])
        ok(pg.evaluate('!!venda.semDescontoAVista') is False and pg.evaluate('descontosAVista()') == 7.87, 'antes da senha nada mudou')
        cancelar()
        ok(pg.evaluate('descontosAVista()') == 7.87, 'cancelar mantem o desconto')
        clic('#btnTirarDescAVista'); pg.wait_for_timeout(300)
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
        ok(pg.evaluate('descontosAVista()') == 7.87 and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('has-error')"), 'confirmar sem a senha e barrado')
        confirmar()
        ok(pg.evaluate('descontosAVista()') == 0 and txt('#finTotal') == 'R$ 249,90' and not visivel('#finDescAVistaLinha') and 'foi tirado' in txt('#avisoAVista'), 'com a senha o desconto sai da venda: o Pix paga 249,90 e o aviso diz que foi tirado')
        ok(any(e['chave'] == 'pdvDescontoAVistaTira' and e['senha'] and 'Quem tirou: ' in e['detalhe'] for e in log()), 'o Registro de atividades guarda quem tirou, com a marca de senha')
        clic('#btnFinalizar'); pg.wait_for_timeout(500)
        v = pg.evaluate('ultimaVenda')
        ok(v['descontoAVista'] is None and v['descontoAVistaTirado'] is True and v['total'] == 249.9 and v['recebimentos'][0]['desconto'] == 0, 'a venda finalizada sem o desconto grava o total cheio e a marca de que foi tirado')
        com_desconto(confirmacoes=dict(pdvDescontoAVistaTira=False)); receber('pix')
        clic('#btnTirarDescAVista'); pg.wait_for_timeout(300)
        ok(modal() == '' and pg.evaluate('descontosAVista()') == 0 and any(e['chave'] == 'pdvDescontoAVistaTira' and not e['senha'] for e in log()), 'com a senha desligada em Confirmacoes de senha tira direto, e o registro grava sem a marca de senha')
        # o catalogo
        for arq in CATALOGOS:
            ok(re.search(r"chave:'pdvDescontoAVistaTira'.*grupo:'Vendas'.*exigePadrao:true", fonte(arq)) is not None, '%s conhece a acao de tirar o desconto a vista (grupo Vendas, com senha por padrao)' % arq.replace('pagina-', ''))
      except Exception as e:
        ok(False, 'a secao 8 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    # ================================================================== [9] Configuracoes > PDV, a troca do exemplo antigo e o padrao de Formas
    if secao(9, 'Configuracoes > PDV: o interruptor; a troca do exemplo antigo vista pelas quatro telas; o padrao de Formas cai na Bronze'):
      try:
        limpar(bancada=False); ir(CFG)
        ok(pg.evaluate("document.getElementById('swAVista').classList.contains('on')") and 'Desconto Pix e dinheiro igual à taxa do crédito à vista' in pg.inner_text('body'), 'o interruptor do desconto Pix e dinheiro existe e nasce ligado')
        prev = txt('#previaAVista')
        ok('Desk Shope: 3,15% (InfinitePay Maquininha — Bronze, Visa em 1x)' in prev and 'Desk Brands: 3,15%' in prev and 'Desk Tech: 3,15%' in prev, 'a previa mostra o percentual de hoje por loja, lido do gateway: %s' % prev[:140])
        ok(pg.get_attribute('.cf-link', 'href') == '../integracoes/pagina-integracoes-gateways.html', 'e tem o link para Gateways')
        gateway(2, situacao='desabilitado'); gateway(3, situacao='habilitado'); ir(CFG)
        ok('Desk Shope: 2,89% (InfinitePay Maquininha — Prata, Visa em 1x)' in txt('#previaAVista'), 'a previa acompanha o nivel: na Prata, 2,89%')
        gateway(3, lojas=[1, 2]); ir(CFG)
        ok('Desk Tech: sem desconto (nenhuma maquininha habilitada na loja)' in txt('#previaAVista'), 'loja sem maquininha aparece como sem desconto')
        clic('#swAVista'); pg.wait_for_timeout(200)
        ok('não aplica' in txt('#previaAVista'), 'desligar mostra que o PDV nao aplica o desconto')
        clic('#btnSalvarParam'); pg.wait_for_timeout(450)
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskParametros')).pdvDescontoAVista") is False, 'salvar grava pdvDescontoAVista = false')
        ir(PDV)
        ok(pg.evaluate('PARAM.pdvDescontoAVista') is False, 'e o PDV le o parametro desligado')
        # a troca do exemplo antigo, vista pelas quatro telas
        velho = gateways_bancada()   # o exemplo antigo de 20/out, com a grafia e o tipo antigos: so aqui, para provar a conversao
        velho[0].update(tipo='infinitypay', descricao='InfinityPay — loja virtual', proximoDiaUtil=True)
        def estado_antigo():
            limpar(bancada=False)
            pg.evaluate("(a) => { localStorage.setItem('deskGateways', JSON.stringify({ gateways: a[0] })); localStorage.setItem('deskGatewaysExemplo', '1'); "
                        "localStorage.setItem('deskParametros', JSON.stringify(a[1])); }", [velho, dict(formaGatewayPadrao=dict(credito=2, debito=2))])
        depois = {}
        for tela in (PDV, LISTA, FORMAS, CFG):
            estado_antigo(); ir(tela)
            depois[tela] = json.dumps(gws(), sort_keys=True)
        ok(len(set(depois.values())) == 1, 'a troca do exemplo antigo da o mesmo resultado qualquer que seja a primeira tela aberta (PDV, Gateways, Formas, Configuracoes PDV)')
        gs = gws()
        ok(sorted(g['descricao'] for g in gs) == sorted(['InfinitePay — loja virtual'] + ['InfinitePay Maquininha — ' + n for n in ('Bronze', 'Prata', 'Ouro', 'Infinite')]), 'sairam a Stone e a Cielo, ficaram a loja virtual e os quatro niveis: %s' % sorted(g['descricao'] for g in gs))
        ok(gs[0]['id'] == 1 and gs[0]['tipo'] == 'infinitepay' and gs[0]['chave'] == 'ipay_live_8f3a1c9e72b4d605' and 'proximoDiaUtil' not in gs[0], 'a loja virtual antiga virou InfinitePay (tipo com e), com a chave guardada, sem o campo do proximo dia util')
        ok(json.loads(pg.evaluate("localStorage.getItem('deskParametros')"))['formaGatewayPadrao'] == {}, 'o gateway padrao de Formas que apontava para a Stone foi apagado')
        ir(FORMAS)
        pg.evaluate("(n) => { const f = FORMAS.filter(x => x.nome === n)[0]; abrirDrawerForma(f.id); }", 'Cartão de crédito'); pg.wait_for_timeout(300)
        ok(txt('#inputGateway .dropdown-select-label').startswith('InfinitePay Maquininha — Bronze'), 'em Formas de recebimento o credito cai na Bronze: %s' % txt('#inputGateway .dropdown-select-label'))
        pg.evaluate("fecharDrawer()")
        ir(PDV)
        ok(pg.evaluate("gwlPadraoDaForma('credito').descricao") == 'InfinitePay Maquininha — Bronze' and pg.evaluate("gwlPadraoDaForma('debito').descricao") == 'InfinitePay Maquininha — Bronze', 'e no PDV o padrao de credito e de debito e a Bronze')
      except Exception as e:
        ok(False, 'a secao 9 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
