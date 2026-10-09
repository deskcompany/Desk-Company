# -*- coding: utf-8 -*-
# Configurações → Finanças → Formas de recebimento. Nasceu em 08/out/2026.
#
# Ate esse dia a lista de formas vivia escrita no codigo de cinco telas, e a
# regra "esta forma valida o limite de credito" morava dentro do Pedido de
# Venda, com um comentario prometendo sair dali quando este cadastro existisse.
#
# O que a suite guarda:
#   [1-3]  o catalogo carrega e cada linha diz o que a forma DECIDE: para que
#          vale, se vira titulo ou entra direto na conta, qual a taxa;
#   [4]    os filtros filtram;
#   [5]    forma do sistema pode ser desabilitada, nunca excluida nem renomeada;
#   [6]    campo que nao se aplica SOME: forma que so paga nao mostra destino,
#          taxa nem limite, e "sem taxa" nao mostra os campos de taxa;
#   [7]    o que nao pode ser gravado e barrado antes de salvar;
#   [8-10] incluir e alterar pedem senha; desabilitar, habilitar e excluir;
#   [11]   a trava nasce com a tela;
#   [12]   A QUE JUSTIFICA O CADASTRO: as cinco telas que oferecem formas
#          oferecem as MESMAS do cadastro, e o Pedido valida limite nas mesmas
#          formas que o cadastro manda validar;
#   [13]   a porta e o hub de Configuracoes;
#   [14]   Esc fecha o que esta por cima primeiro.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

TELA = 'pagina-configuracoes-formas-recebimento.html'
HUB = 'pagina-configuracoes.html'
PEDIDO = 'pagina-vendas-pedidos-detalhe.html'
RECEBER = ['pagina-financas-contas-receber.html', 'pagina-financas-contas-receber-detalhe.html']
PAGAR = ['pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html']
CONTAS = 'pagina-configuracoes-contas-financeiras.html'
CATALOGOS = ['pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html',
             'pagina-cadastros-vendedores-detalhe.html']

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clic(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


def escolher(pg, raiz, valor):
    """Abre o dropdown e escolhe a opcao, pelo DOM (com o painel aberto o
    Playwright recusa o clique por interceptacao de ponteiro)."""
    clic(pg, '#' + raiz + ' .dropdown-select-btn')
    pg.wait_for_timeout(150)
    pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, valor])
    pg.wait_for_timeout(250)


def linha(pg, nome):
    """Texto da linha da forma, em minusculas (as etiquetas saem em maiusculas por CSS)."""
    return pg.evaluate("""(n) => { const f = FORMAS.filter(x => x.nome === n)[0];
        const tr = f && document.querySelector('#listaFormas tr[data-id="' + f.id + '"]');
        return tr ? tr.innerText.split(String.fromCharCode(10)).join(' | ').split(String.fromCharCode(9)).join(' | ').toLowerCase() : null; }""", nome)


def abrir(pg, nome):
    pg.evaluate("""(n) => { const f = FORMAS.filter(x => x.nome === n)[0];
        document.querySelector('#listaFormas tr[data-id="' + f.id + '"]').click(); }""", nome)
    pg.wait_for_timeout(350)


def visivel(pg, sel):
    return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)


def confirmar(pg, senha=True):
    if pg.locator('#confirmModal.open').count():
        if senha and visivel(pg, '#campoSenhaModal'):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(450)
    if pg.locator('#confirmModal.open').count():      # aviso de "gravado", quando a tela mostra
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(350)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 950})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(localiza.http(TELA))
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(800)

    print('\n[1] O catalogo carrega com as formas que as telas ja usavam')
    ok(pg.evaluate("FORMAS.length") == 11, 'onze formas no catalogo: %d' % pg.evaluate("FORMAS.length"))
    ok('de 11' in pg.inner_text('#paginacaoResumo'), 'e a paginacao sabe das onze: %s' % pg.inner_text('#paginacaoResumo'))
    escolher(pg, 'itensPorPagina', '25')
    n = pg.locator('#listaFormas tbody tr').count()
    ok(n == 11, 'com 25 por pagina as onze cabem numa pagina so: %d' % n)
    corpo = pg.inner_text('#listaFormas')
    for nome in ['Dinheiro', 'Pix', 'Cartão de crédito', 'Cartão de débito', 'Boleto', 'Crediário',
                 'Cheque', 'Depósito', 'Vale-troca', 'Transferência']:
        ok(nome in corpo, 'a forma "%s" tem cadastro' % nome)
    ok(pg.evaluate("FORMAS.filter(f => f.sistema).length") == 10, 'dez sao do sistema')
    ok(pg.locator('#listaFormas .cf-cadeado').count() == 10, 'e as dez trazem o cadeado na lista')

    print('\n[2] O indicador conta o que esta habilitado, e diz para onde o dinheiro vai')
    hab = pg.evaluate("FORMAS.filter(f => f.ativo).length")
    ok(pg.inner_text('#kpiFormas').strip() == str(hab), 'habilitadas no indicador: %s' % pg.inner_text('#kpiFormas'))
    nota = pg.inner_text('#kpiNota')
    ok('título' in nota and 'direto na conta' in nota and 'para pagar' in nota, 'a nota separa titulo, conta e pagar: %s' % nota)

    print('\n[3] Cada linha diz o que a forma decide')
    l = linha(pg, 'Dinheiro')
    ok('receber e pagar' in l and 'conta financeira' in l and 'caixa' in l and 'sem taxa' in l, 'Dinheiro entra direto no Caixa, sem taxa: %s' % l)
    l = linha(pg, 'Cartão de crédito')
    ok('contas a receber' in l and '3,49%' in l and 'valida limite' in l, 'Cartao de credito vira titulo, tem taxa e valida limite: %s' % l)
    l = linha(pg, 'Boleto')
    ok('r$ 2,90' in l and 'no dia do pagamento' in l, 'Boleto mostra a taxa fixa e quando ela incide: %s' % l)
    l = linha(pg, 'Transferência')
    ok(l.count('—') == 3 and '| pagar |' in l, 'forma que so paga nao inventa destino, conta nem taxa: %s' % l)
    l = linha(pg, 'Vale-troca')
    ok('reservada' in l and 'desabilitada' in l, 'Vale-troca aparece reservada e desabilitada: %s' % l)
    l = linha(pg, 'Cheque')
    ok('valida limite' not in l, 'Cheque NAO valida limite (decisao do usuario): %s' % l)

    print('\n[4] Os filtros filtram')
    escolher(pg, 'filtroUso', 'receber')
    t = pg.inner_text('#listaFormas')
    ok('Transferência' not in t and 'Cheque' in t, '"valem para receber" tira a Transferencia')
    escolher(pg, 'filtroUso', 'pagar')
    t = pg.inner_text('#listaFormas')
    ok('Transferência' in t and 'Dinheiro' in t and 'Cheque' not in t, '"valem para pagar" mostra Transferencia e Dinheiro, e tira o Cheque')
    escolher(pg, 'filtroUso', 'todos')
    escolher(pg, 'filtroSituacao', 'inativo')
    ok(pg.locator('#listaFormas tbody tr').count() == 1 and 'Vale-troca' in pg.inner_text('#listaFormas'),
       '"desabilitadas" mostra so o Vale-troca')
    escolher(pg, 'filtroSituacao', 'todos')
    pg.fill('#campoBusca', 'mercado')
    pg.wait_for_timeout(250)
    t = pg.inner_text('#listaFormas')
    ok('Cartão de crédito' in t and 'Dinheiro' not in t, 'a busca acha a forma pela conta preferencial')
    pg.fill('#campoBusca', '')
    pg.wait_for_timeout(250)
    ok(pg.locator('#listaFormas tbody tr').count() == 11, 'limpar a busca devolve as onze')

    print('\n[5] Forma do sistema: desabilita, mas nao exclui nem renomeia')
    abrir(pg, 'Boleto')
    ok(pg.locator('#eventDrawer.open').count() == 1, 'clicar na linha abre o painel')
    ok(pg.evaluate("document.getElementById('inputNomeForma').disabled") is True, 'o nome vem travado')
    ok(not visivel(pg, '#linkExcluirForma'), 'nao ha link de excluir')
    ok(visivel(pg, '#linkSituacaoForma') and pg.inner_text('#linkSituacaoForma').strip() == 'Desabilitar', 'mas ha o de desabilitar')
    ok('não excluída nem renomeada' in pg.inner_text('#notaForma'), 'e a nota explica a trava antes do clique')
    ok(pg.inner_text('#inputUso .dropdown-select-label') == 'Receber e pagar', 'o painel abre com os dados da forma: vale para')
    ok(pg.inner_text('#inputTarifacao .dropdown-select-label') == 'Descontada no dia do pagamento', 'e a taxa')
    ok(pg.input_value('#inputTaxaFixa') == '2,90', 'e o valor fixo: %s' % pg.input_value('#inputTaxaFixa'))
    ok(pg.evaluate("document.getElementById('swLimite').classList.contains('on')"), 'e o interruptor de limite ligado')

    print('\n[6] Campo que nao se aplica some')
    ok(visivel(pg, '#blocoReceber') and visivel(pg, '#blocoTaxa'), 'Boleto mostra recebimento e taxa')
    escolher(pg, 'inputTarifacao', 'sem')
    ok(not visivel(pg, '#blocoTaxa'), '"sem taxa" esconde percentual e valor fixo')
    escolher(pg, 'inputUso', 'pagar')
    ok(not visivel(pg, '#blocoReceber'), '"so pagar" esconde destino, conta, taxa e limite de uma vez')
    escolher(pg, 'inputUso', 'ambos')
    ok(visivel(pg, '#blocoReceber'), 'e voltar a receber traz o bloco de volta')
    escolher(pg, 'inputDestino', 'conta')
    ok('entra' in pg.inner_text('#rotuloConta'), 'com destino em conta, o campo passa a pedir a conta em que o valor entra')
    clic(pg, '#btnCancelarForma')
    pg.wait_for_timeout(300)
    ok(pg.evaluate("FORMAS.filter(f => f.nome === 'Boleto')[0].tarifacao") == 'pagamento', 'cancelar nao grava nada do que foi mexido')

    print('\n[7] O que nao pode ser gravado e barrado antes de salvar')
    antes = pg.evaluate("FORMAS.length")
    clic(pg, '#btnNovaForma')
    pg.wait_for_timeout(350)
    ok(pg.inner_text('#drawerTitulo') == 'Nova forma de recebimento', 'o botao de incluir abre o painel vazio')
    ok(not visivel(pg, '#linkSituacaoForma') and not visivel(pg, '#linkExcluirForma'), 'sem desabilitar nem excluir numa forma que ainda nao existe')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroNomeForma'), 'sem nome nao salva')
    pg.fill('#inputNomeForma', 'cartao de credito')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroNomeForma') and 'Já existe' in pg.inner_text('#erroNomeForma'), 'nome repetido e barrado, mesmo sem acento e em minusculas')
    pg.fill('#inputNomeForma', 'Link de pagamento')
    escolher(pg, 'inputDestino', 'conta')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroConta'), 'destino em conta financeira exige a conta')
    escolher(pg, 'inputConta', '3')
    ok(not visivel(pg, '#erroConta'), 'escolher a conta apaga o erro')
    escolher(pg, 'inputTarifacao', 'transacao')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroTaxa'), 'taxa escolhida sem valor nenhum e barrada')
    pg.fill('#inputTaxaPct', 'abc')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroTaxa') and 'números' in pg.inner_text('#erroTaxa'), 'texto no lugar de numero e barrado, em vez de gravar zero')
    pg.fill('#inputTaxaPct', '250')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroTaxa') and '100%' in pg.inner_text('#erroTaxa'), 'percentual acima de 100 e barrado')
    ok(pg.evaluate("FORMAS.length") == antes and pg.locator('#confirmModal.open').count() == 0, 'e nada disso chegou a ser gravado')

    print('\n[8] Incluir segue a matriz do modulo; mexer em regra de dinheiro pede senha')
    # No sistema, criar e editar nascem SEM senha e excluir nasce com (a matriz
    # de Confirmacoes por senha). Mexer no destino, na taxa ou no limite de uma
    # forma que ja existe e outra coisa: muda para onde o dinheiro das proximas
    # vendas vai. Tem acao propria, que pede senha por padrao.
    pg.fill('#inputTaxaPct', '4,5')
    clic(pg, '#swLimite')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(450)
    ok(pg.locator('#confirmModal.open').count() == 0, 'incluir forma nova nao pede senha por padrao, como todo cadastro')
    nova = pg.evaluate("FORMAS.filter(f => f.nome === 'Link de pagamento')[0] || null")
    ok(nova is not None and nova['sistema'] is False and nova['ativo'] is True, 'a forma nova entra habilitada e nao e do sistema')
    ok(nova and nova['destino'] == 'conta' and nova['contaId'] == 3 and nova['taxaPct'] == 4.5 and nova['validaLimite'] is True,
       'com o que foi preenchido: %s' % nova)
    ok(pg.locator('#eventDrawer.open').count() == 0, 'e o painel fecha')
    l = linha(pg, 'Link de pagamento')
    ok(l and '4,50%' in l and 'mercado pago' in l, 'a linha nova aparece na lista: %s' % l)
    ok(pg.inner_text('#kpiFormas').strip() == str(hab + 1), 'e o indicador soma uma habilitada')

    abrir(pg, 'Link de pagamento')
    pg.fill('#inputNomeForma', 'Link de pagamento online')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(450)
    ok(pg.locator('#confirmModal.open').count() == 0 and
       pg.evaluate("FORMAS.filter(f => f.nome === 'Link de pagamento online').length") == 1,
       'mudar so o nome tambem segue a matriz: grava sem senha')

    abrir(pg, 'Cheque')
    clic(pg, '#swLimite')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(450)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal'), 'mexer no limite de credito de uma forma PEDE senha')
    ok('regras' in pg.inner_text('#confirmModalTexto'), 'e a pergunta diz que e regra: %s' % pg.inner_text('#confirmModalTexto')[:70])
    ok(pg.evaluate("FORMAS.filter(f => f.chave === 'cheque')[0].validaLimite") is False, 'antes de confirmar, nada mudou')
    confirmar(pg)
    ch = pg.evaluate("FORMAS.filter(f => f.chave === 'cheque')[0]")
    ok(ch['validaLimite'] is True and ch['nome'] == 'Cheque', 'confirmada, a regra muda e o nome da forma do sistema continua o mesmo')
    abrir(pg, 'Cheque'); clic(pg, '#swLimite'); clic(pg, '#btnSalvarForma'); pg.wait_for_timeout(450); confirmar(pg)

    abrir(pg, 'Boleto')
    pg.fill('#inputTaxaFixa', '3,10')
    clic(pg, '#btnSalvarForma')
    pg.wait_for_timeout(450)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal'), 'mexer na taxa tambem pede senha')
    clic(pg, '#btnConfirmModalCancelar')
    pg.wait_for_timeout(350)
    ok(pg.evaluate("FORMAS.filter(f => f.chave === 'boleto')[0].taxaFixa") == 2.9, 'e cancelar na senha nao grava a taxa nova')
    if pg.locator('#eventDrawer.open').count():
        clic(pg, '#btnCancelarForma'); pg.wait_for_timeout(300)

    print('\n[9] Desabilitar e habilitar')
    abrir(pg, 'Depósito')
    clic(pg, '#linkSituacaoForma')
    pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 1 and 'Desabilitar' in pg.inner_text('#confirmModalTexto'), 'desabilitar pergunta antes')
    confirmar(pg, senha=False)
    ok('desabilitada' in linha(pg, 'Depósito'), 'e a forma fica desabilitada na lista')
    abrir(pg, 'Depósito')
    ok(pg.inner_text('#linkSituacaoForma').strip() == 'Habilitar', 'o link do painel vira "Habilitar"')
    clic(pg, '#linkSituacaoForma'); pg.wait_for_timeout(350); confirmar(pg, senha=False)
    ok('habilitada' in linha(pg, 'Depósito') and 'desabilitada' not in linha(pg, 'Depósito'), 'e ela volta')
    abrir(pg, 'Vale-troca')
    ok('reservada' in pg.inner_text('#notaForma').lower(), 'a reservada avisa no painel que nao pode ser ligada')
    clic(pg, '#linkSituacaoForma')
    pg.wait_for_timeout(600)
    ok(pg.evaluate("FORMAS.filter(f => f.chave === 'valetroca')[0].ativo") is False and
       pg.locator('#confirmModal.open').count() == 1 and 'reservada' in pg.inner_text('#confirmModalTexto'),
       'e tentar habilitar explica, em vez de ligar')
    clic(pg, '#btnConfirmModalConfirmar')
    pg.wait_for_timeout(350)
    if pg.locator('#confirmModal.open').count():
        clic(pg, '#btnConfirmModalCancelar'); pg.wait_for_timeout(300)

    print('\n[10] Excluir so o que o usuario criou, e com senha')
    abrir(pg, 'Carteira digital')
    ok(visivel(pg, '#linkExcluirForma'), 'forma criada pelo usuario tem o link de excluir')
    ok(pg.evaluate("document.getElementById('inputNomeForma').disabled") is False, 'e o nome dela pode ser mudado')
    clic(pg, '#linkExcluirForma')
    pg.wait_for_timeout(400)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal'), 'excluir pede senha')
    confirmar(pg)
    ok(pg.evaluate("FORMAS.filter(f => f.nome === 'Carteira digital').length") == 0, 'e a forma sai do catalogo')

    print('\n[11] A trava nasce com a tela')
    base = pg.evaluate("MODULOS_SENHA.filter(m => m.base === 'formasRecebimento')[0] || null")
    ok(base is not None, 'o cadastro esta no catalogo de senhas')
    if base:
        ok(all(base['ligado'][v] for v in ['criar', 'editar', 'excluir']), 'com os tres verbos ligados desde o primeiro dia')
    regra = pg.evaluate("ACOES_SENHA.filter(a => a.chave === 'formasRecebimentoRegra')[0] || null")
    ok(regra is not None and regra['exigePadrao'] is True and regra['ligado'] is True,
       'mexer em regra de dinheiro e acao propria, que nasce pedindo senha')
    for arq in CATALOGOS:
        txt = open(localiza.onde(arq), encoding='utf-8').read()
        ok("base:'formasRecebimento'" in txt and "chave:'formasRecebimentoRegra'" in txt,
           '%s conhece o cadastro e a acao' % arq.replace('pagina-', ''))

    print('\n[12] As telas que oferecem formas oferecem as MESMAS do cadastro')
    # Esta e a secao que justifica o cadastro existir. Enquanto nao ha backend,
    # as listas das outras telas ficam como espelho, e sem esta comparacao elas
    # divergem em silencio: o Pedido validaria limite numa forma que o cadastro
    # manda nao validar, e ninguem veria.
    pg.goto(localiza.http(TELA)); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    sis = pg.evaluate("FORMAS.filter(f => f.sistema)")
    recebem = sorted(f['nome'] for f in sis if f['uso'] != 'pagar')
    pagam = sorted(f['nome'] for f in sis if f['uso'] != 'receber')
    por_chave = dict((f['chave'], f) for f in sis)
    contas_espelho = sorted(pg.evaluate("CONTAS_FINANCEIRAS.map(c => c.id + ':' + c.nome)"))
    p2 = nav.new_page(viewport={'width': 1440, 'height': 950})
    e2 = []
    p2.on('pageerror', lambda e: e2.append(str(e)))
    for arq in RECEBER:
        p2.goto(localiza.http(arq)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
        la = sorted(x for x in p2.evaluate("FORMAS") if x != 'Não informada')
        ok(la == recebem, '%s oferece as formas que valem para receber: %s' % (arq.replace('pagina-financas-', ''), [x for x in set(la) ^ set(recebem)] or 'iguais'))
    for arq in PAGAR:
        p2.goto(localiza.http(arq)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
        la = sorted(p2.evaluate("FORMAS"))
        ok(la == pagam, '%s oferece as formas que valem para pagar: %s' % (arq.replace('pagina-financas-', ''), [x for x in set(la) ^ set(pagam)] or 'iguais'))
    p2.goto(localiza.http(PEDIDO)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    rot = p2.evaluate("RECEBIMENTO_ROTULO")
    val = p2.evaluate("RECEBIMENTO_VALIDA_LIMITE")
    ok(all(k in por_chave for k in rot), 'toda forma do Pedido existe no cadastro: %s' % sorted(rot))
    dif_rot = [k for k in rot if k in por_chave and por_chave[k]['nome'] != rot[k]]
    ok(not dif_rot, 'com o mesmo nome: %s' % (dif_rot or 'iguais'))
    dif_val = [k for k in val if k in por_chave and por_chave[k]['validaLimite'] != val[k]]
    ok(not dif_val, 'e o Pedido valida limite nas MESMAS formas que o cadastro manda: %s' % (dif_val or 'iguais'))
    p2.goto(localiza.http(CONTAS)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    ativas = sorted(p2.evaluate("CONTAS.filter(c => c.ativo).map(c => c.id + ':' + c.nome)"))
    ok(ativas == contas_espelho, 'as contas oferecidas aqui sao as contas financeiras ativas: %s' % ([x for x in set(ativas) ^ set(contas_espelho)] or 'iguais'))

    print('\n[13] A porta e o hub de Configuracoes')
    p2.goto(localiza.http(HUB)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    clic(p2, '.aba-sit[data-aba="financas"]')
    p2.wait_for_timeout(300)
    cartao = '.cfg-item[data-nome="Formas de recebimento"]'
    ok(p2.locator(cartao).count() == 1 and p2.locator(cartao).get_attribute('data-href') is not None, 'o cartao existe e tem destino')
    if p2.locator(cartao).count() == 1:
        p2.click(cartao)
        p2.wait_for_timeout(800)
    ok(localiza.nome(p2.url) == TELA, 'e abre esta tela: %s' % localiza.nome(p2.url))
    bc = p2.inner_text('#breadcrumb').lower() if localiza.nome(p2.url) == TELA else ''
    ok('configura' in bc and 'formas de recebimento' in bc, 'o caminho diz Configuracoes > Formas de recebimento')
    ok(not e2, 'sem erro de JS nas telas espelho e no hub: %s' % e2[:2])
    p2.close()

    print('\n[14] Esc fecha o que esta por cima primeiro, e os dois temas')
    abrir(pg, 'Pix')
    clic(pg, '#linkSituacaoForma')
    pg.wait_for_timeout(350)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 0 and pg.locator('#eventDrawer.open').count() == 1,
       'com a pergunta aberta, o primeiro Esc fecha so a pergunta')
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(350)
    ok(pg.locator('#eventDrawer.open').count() == 0, 'e o segundo fecha o painel')
    ok(pg.evaluate("FORMAS.filter(f => f.chave === 'pix')[0].ativo") is True, 'sem ter desabilitado nada')
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(220)
        ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440, 'tema %s: nao estoura em 1440' % tema)
    ok(not erros, 'sem erro de JS: %s' % erros[:2])

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
