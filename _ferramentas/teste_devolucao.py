# -*- coding: utf-8 -*-
# Logística → Devolução (listagem + detalhe). Última peça da F4, construída em
# 07/out/2026 depois de pesquisar como o Olist trata devoluções e de barganhar
# as quatro decisões em que nos afastamos dele.
#
# O que esta suíte protege são as DECISÕES, não o desenho:
#
#   devolução é DOCUMENTO PRÓPRIO e aponta para o pedido; o pedido mantém a
#     situação dele — faturamento e baixa física continuam tendo acontecido
#   ela nasce com `origem` (pedido | chamado) mesmo sem o Help Desk existir
#   a listagem LÊ, o detalhe ESCREVE — mesma regra do Rastreamento
#   lançar estoque é AÇÃO EXPLÍCITA: no Olist a SEFAZ dispara, e nós não temos NF-e
#   o estado é POR ITEM, sugerido pelo motivo e confirmado por quem recebe a caixa
#   o código da reversa mora na devolução, não no Rastreamento (lá é a ida)
#   Vale-troca aparece e fica RESERVADO enquanto o submódulo não existe
#   os dois parâmetros nasceram em Configurações no mesmo dia da tela
#   devolver mais do que foi vendido é barrado: isso é entrada, não devolução
#   finalizar com estoque pendente é barrado: a caixa ficaria fora do saldo
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'
LISTA = 'pagina-logistica-devolucao.html'
DET = 'pagina-logistica-devolucao-detalhe.html'

def clicarId(pg, eid):
    """Clique pelo DOM: com um painel aberto o Playwright recusa o clique por
    interceptacao de ponteiro, e aqui o painel e justamente o alvo."""
    pg.evaluate("(i) => document.getElementById(i).click()", eid)


def trocar(pg, raiz, menu, valor):
    """Abre o dropdown e escolhe a opcao, pelo DOM: com um painel aberto o
    Playwright recusa o clique por interceptacao de ponteiro."""
    pg.evaluate("(r) => document.querySelector('#' + r + ' .dropdown-select-btn').click()", raiz)
    pg.wait_for_timeout(250)
    pg.evaluate("([m, v]) => document.querySelector('#' + m + ' [data-value=\"' + v + '\"]').click()",
                [menu, valor])
    pg.wait_for_timeout(350)


falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

with sync_playwright() as pw:
    erros = []
    nav = pw.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 1000})
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' and not ruido(m.text) else None)
    pg.goto(URL + LISTA); pg.wait_for_timeout(600)

    print('\n[1] A listagem carrega e a tabela cabe no card a 1440px')
    n = pg.locator('#corpoTabela tr').count()
    ok(n > 0, 'a lista renderiza (%d devolucoes)' % n)
    m = pg.evaluate("""() => {
      const w = document.querySelector('.estoque-table-wrap');
      return { wrap: Math.round(w.clientWidth), tabela: Math.round(w.querySelector('table').scrollWidth) };
    }""")
    ok(m['tabela'] <= m['wrap'], 'a tabela cabe no card: %dpx em %dpx' % (m['tabela'], m['wrap']))
    ok(pg.evaluate("document.documentElement.scrollWidth") <= 1440, 'a pagina nao rola na horizontal')

    print('\n[2] As abas de situacao cabem numa linha, e contam COM os filtros')
    linhas = pg.evaluate("""() => {
      const tops = Array.from(document.querySelectorAll('.aba-sit')).map(a => Math.round(a.getBoundingClientRect().top));
      return new Set(tops).size;
    }""")
    ok(linhas == 1, 'as abas ficam numa linha so (%d linhas)' % linhas)
    total = pg.evaluate("Number(document.querySelector('[data-cont=\"todas\"]').textContent)")
    soma = pg.evaluate("""['aberta','andamento','finalizada','cancelada']
      .reduce((s,k) => s + Number(document.querySelector('[data-cont=\"'+k+'\"]').textContent), 0)""")
    ok(total == soma, 'o contador de Todas e a soma das partes (%d = %d)' % (total, soma))
    # Contador que ignora o filtro e aba mentindo sobre a lista embaixo dela.
    pg.fill('#campoBusca', 'Veredas'); pg.wait_for_timeout(400)
    depois = pg.evaluate("Number(document.querySelector('[data-cont=\"todas\"]').textContent)")
    ok(depois < total, 'os contadores acompanham a busca (%d -> %d)' % (total, depois))
    ok(depois == pg.locator('#corpoTabela tr').count(), 'e batem com o que a lista mostra')
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(400)

    print('\n[3] Devolucao e DOCUMENTO PROPRIO, e aponta para o pedido')
    # Decisao de 02/out, ja gravada em Pedidos de Venda: o pedido devolvido mantem
    # a situacao dele. Se devolucao fosse status, o pedido perderia o faturamento.
    ok(pg.evaluate("typeof DEVOLUCOES !== 'undefined' && DEVOLUCOES.length > 0"),
       'existe a colecao propria de devolucoes')
    apontam = pg.evaluate("DEVOLUCOES.every(d => !!vendaDe(d.vendaId))")
    ok(apontam, 'toda devolucao aponta para uma venda que existe')
    repetido = pg.evaluate("new Set(DEVOLUCOES.map(d => d.vendaId)).size < DEVOLUCOES.length")
    ok(repetido, 'a mesma venda pode ter mais de uma devolucao — o que status nao permitiria')

    print('\n[4] `origem` nasce antes do Help Desk existir')
    # Decisao registrada no roadmap: uma devolucao, duas portas — nunca duas telas.
    temOrigem = pg.evaluate("DEVOLUCOES.every(d => d.origem === 'pedido' || d.origem === 'chamado')")
    ok(temOrigem, 'toda devolucao diz de onde nasceu')
    temCampo = pg.evaluate("DEVOLUCOES.every(d => 'chamadoId' in d)")
    ok(temCampo, 'e carrega chamadoId, anulavel, para quando o chamado existir')

    print('\n[5] O painel da listagem SO MOSTRA')
    pg.locator('#corpoTabela tr').first.click(); pg.wait_for_timeout(450)
    corpo = pg.inner_text('#drawerCorpo').lower()
    ok('só consulta' in corpo, 'o painel diz que e so consulta')
    ok(pg.locator('#drawerCorpo input, #drawerCorpo textarea').count() == 0,
       'nao ha campo editavel nenhum no painel')
    ok(pg.locator('#drawerCorpo [data-abrir-detalhe]').count() == 1, 'ele oferece abrir a devolucao')

    print('\n[6] O painel leva ao detalhe, pelo ?id=')
    pg.locator('#drawerCorpo [data-abrir-detalhe]').click()
    pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(DET in pg.url, 'navegou para o detalhe')
    ok('?id=' in pg.url, 'levou o id na URL, como as outras telas de detalhe')
    ok('Devolu' in pg.inner_text('#tituloDev'), 'o titulo traz a devolucao: %s' % pg.inner_text('#tituloDev'))
    bc = pg.inner_text('#breadcrumb').lower()
    ok('devolu' in bc and 'expedi' not in bc and 'rastreamento' not in bc,
       'o caminho e o desta tela: %s' % bc.replace(chr(10), ' '))

    print('\n[7] O estado da mercadoria e POR ITEM')
    pg.goto(URL + DET + '?id=1'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.locator('#corpoItens [data-estado]').count() == pg.locator('#corpoItens tr').count(),
       'toda linha tem o seu proprio estado')
    estados = pg.evaluate("Object.keys(ESTADOS_ITEM)")
    ok(sorted(estados) == ['avaria', 'nenhum', 'revendavel'],
       'os tres estados existem: %s' % estados)
    ok('avaria' in pg.inner_text('#avisoItensTexto').lower(), 'o aviso conta o que vai para Avaria')
    ok('bloquead' in pg.inner_text('#avisoItensTexto').lower(), 'dizendo que entra bloqueado')
    # O motivo sugere, nao decide: o cadastro sugere avaria e a linha pode dizer outra coisa.
    ok('sugest' in pg.inner_text('#hintMotivo').lower(),
       'a tela diz que o motivo SUGERE o destino: %s' % pg.inner_text('#hintMotivo'))

    print('\n[8] A Devolucao NAO mexe no saldo: ela so confirma que a caixa chegou')
    # Devolucao de venda e, fiscalmente, uma nota de ENTRADA. O "Lancar
    # estoque" que existia aqui pulava o documento E deixava alguem declarar o
    # estado da mercadoria antes de ter aberto a caixa. Agora a devolucao faz
    # nascer a nota, e o saldo sobe na Conferencia de Entrada.
    ok(pg.evaluate("!document.getElementById('btnLancarEstoque')"),
       'nao existe mais botao de lancar estoque nesta tela')
    ok(pg.evaluate("!!DEV.notaEntrada"), 'a devolucao fez nascer a nota de entrada')
    ok(pg.evaluate("DEV.notaEntrada.situacao") == 'transito',
       'ela nasce EM TRANSITO: o documento existe e a mercadoria esta na rua')
    ok('em trânsito' in pg.inner_text('#docEstSitNota').lower(),
       'e a tela diz isso: %s' % pg.inner_text('#docEstSitNota'))
    ok('ainda na rua' in pg.inner_text('#docEstChegada').lower(),
       'sem data de chegada enquanto nao chegou')
    ok(pg.locator('#btnConfirmarChegada:visible').count() == 1, 'ha o botao de confirmar chegada')

    # Confirmar chegada NAO pede senha de proposito: quem recebe caixa faz isso
    # dezenas de vezes por dia, e senha a cada caixa vira senha compartilhada —
    # pior que senha nenhuma. Pela mecanica do sistema, acao sem senha executa
    # direto e fica no registro de atividades.
    pg.locator('#btnConfirmarChegada').click(); pg.wait_for_timeout(600)
    ok(pg.locator('#confirmModal.open').count() == 0,
       'nao para em modal: e fato da portaria, nao decisao sobre o saldo')
    ok(pg.evaluate("ACOES_ESPECIFICAS.filter(a => a.chave === 'devolucaoConfirmaChegada')[0].pronto"),
       'mas a acao esta no catalogo, entao vai para o registro de atividades')
    ok(pg.evaluate("!!DEV.notaEntrada.chegada"), 'confirmado, a chegada e registrada')
    ok(pg.evaluate("DEV.notaEntrada.situacao") == 'aconferir',
       'e a nota entra na fila de conferencia')
    # A asserção que guarda o ponto do fluxo: chegar NAO e entrar no saldo.
    ok(pg.evaluate("DEV.notaEntrada.situacao !== 'lancada'"),
       'confirmar chegada NAO lanca o saldo — isso e da conferencia')
    ok('conferência de entrada' in pg.inner_text('#avisoEstoqueTexto').lower(),
       'e o aviso diz onde o saldo sobe: %s' % pg.inner_text('#avisoEstoqueTexto')[:60])
    ok(pg.locator('#btnConfirmarChegada:visible').count() == 0,
       'o botao some: confirmar duas vezes nao faz sentido')

    print('\n[9] Devolver mais do que foi vendido e barrado')
    pg.goto(URL + DET + '?id=2'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    vendidas = pg.evaluate("DEV.itens[0].qtdVendida")
    antes = pg.evaluate("DEV.itens[0].qtd")
    pg.fill('#corpoItens input[data-qtd="0"]', str(vendidas + 5)); pg.wait_for_timeout(250)
    pg.locator('#btnSalvar').click(); pg.wait_for_timeout(450)
    txt = pg.inner_text('body').lower()
    ok('não dá para devolver' in txt or 'nao da para devolver' in txt,
       'a tela recusa devolver mais do que saiu')
    ok(pg.evaluate("DEV.itens[0].qtd") == antes, 'e nada foi gravado (%s)' % antes)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[10] Motivo que exige descricao nao salva sem ela')
    pg.goto(URL + DET + '?id=2'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    exige = pg.evaluate("Object.keys(MOTIVOS).filter(k => MOTIVOS[k].exigeObs)[0]")
    pg.locator('#inputMotivo .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#inputMotivo .dropdown-select-item[data-value="' + exige + '"]').click(); pg.wait_for_timeout(300)
    ok('exige' in pg.inner_text('#hintDescricao').lower(), 'a tela avisa que o motivo exige descricao')
    pg.fill('#inputDescricao', ''); pg.wait_for_timeout(200)
    pg.locator('#btnSalvar').click(); pg.wait_for_timeout(450)
    ok(pg.locator('#campoDescricao.has-error').count() == 1, 'o campo e marcado em erro')
    ok(pg.evaluate("String(DEV.motivoId)") != exige, 'e o motivo novo nao foi gravado')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[11] Vale-troca aparece e fica RESERVADO')
    # Forma que nao gera documento nenhum seria prometer um credito que ninguem
    # consegue usar. Mesma regra do campo fiscal: visivel e desabilitado.
    reservada = pg.evaluate("FORMAS.filter(f => f.reservado).map(f => f.id)")
    ok(reservada == ['valetroca'], 'vale-troca e a unica forma reservada: %s' % reservada)
    ok(pg.locator('#menuForma .dropdown-select-item[data-value="valetroca"]').count() == 1,
       'ela APARECE na lista, nao some')
    antesF = pg.evaluate("DEV.forma")
    pg.locator('#inputForma .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#menuForma .dropdown-select-item[data-value="valetroca"]').click(); pg.wait_for_timeout(450)
    ok(pg.evaluate("DEV.forma") == antesF, 'escolher nao muda nada: a forma segue %s' % antesF)
    ok('vales-troca' in pg.inner_text('body').lower(), 'e a tela explica por que')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[12] O codigo da reversa mora AQUI, nao no Rastreamento')
    pg.goto(URL + DET + '?id=2'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.inner_text('#docRevCodigo').strip() not in ('', '—'),
       'a devolucao guarda o codigo da reversa: %s' % pg.inner_text('#docRevCodigo'))
    ok(pg.inner_text('#docRevTransp').strip() not in ('', '—'), 'e a transportadora da volta')
    # O funil do Rastreamento e a IDA: nove situacoes, previsao congelada, KPI de
    # atraso. Um movimento ao contrario caberia mal la.
    pg2 = nav.new_page(viewport={'width': 1440, 'height': 950})
    pg2.goto(URL + 'pagina-logistica-rastreamento.html'); pg2.wait_for_timeout(600)
    semReversa = pg2.evaluate("SITUACOES.filter(s => s.id.indexOf('devol') >= 0 || s.id.indexOf('revers') >= 0).length")
    ok(semReversa == 0, 'o funil do Rastreamento nao ganhou situacao de volta (%d)' % semReversa)
    pg2.close()

    print('\n[12b] A reversa e COTACAO: ofertas, quem paga, e o codigo que ainda nao saiu')
    # A escolha e a mesma do checkout: comparar ofertas e decidir. E ha uma
    # distincao que o cliente sente na pele — autorizacao de postagem (ele
    # leva um codigo) contra etiqueta invertida (ele PRECISA imprimir).
    pg.goto(URL + DET + '?id=1'); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    ok(pg.evaluate("!DEV.reversa"), 'a DV-0012 ainda nao pediu reversa')
    # §9.3: dropdown de painel nasce com a TELA. Painel fechado tambem e pagina.
    ok(pg.evaluate("document.querySelectorAll('#revOfertas .oferta').length") > 0,
       'as ofertas ja existem antes de o painel abrir')
    clicarId(pg, 'btnReversa'); pg.wait_for_timeout(500)
    ok(pg.locator('#revDrawer.open').count() == 1, 'o painel abre em vez de gravar direto')

    plats = pg.evaluate("OFERTAS_REVERSA.map(o => o.plataforma)")
    ok(len(set(plats)) >= 3,
       'as ofertas vem de plataformas diferentes, para comparar: %s' % sorted(set(plats)))
    tipos = pg.evaluate("OFERTAS_REVERSA.map(o => o.entrega)")
    ok('codigo' in tipos and 'etiqueta' in tipos,
       'e distinguem codigo de postagem de etiqueta para imprimir: %s' % sorted(set(tipos)))
    ok('propria' in tipos, 'a coleta por frota propria tambem e uma oferta')

    # Quem paga vem do GRUPO do motivo, como o destino no estoque.
    grupo = pg.evaluate("motivoDe(DEV.motivoId).grupo")
    sugerido = pg.evaluate("document.getElementById('revQuemPaga').getAttribute('data-value')")
    ok(grupo == 'transporte' and sugerido == 'nos',
       'motivo de grupo %s sugere que NOS pagamos (%s)' % (grupo, sugerido))

    # Escolher a etiqueta tem de AVISAR que o cliente precisa de impressora.
    pg.evaluate("(s) => document.querySelector(s).click()", '[data-oferta="sf-jadlog"]')
    pg.wait_for_timeout(400)
    ok('IMPRIMIR' in pg.inner_text('#revResumo'),
       'a oferta de etiqueta avisa que o cliente precisa imprimir')
    ok('19,80' in pg.inner_text('#revResumo'), 'e mostra o valor dela')

    clicarId(pg, 'revConfirmar'); pg.wait_for_timeout(700)
    if pg.locator('#campoSenhaModal').count() and pg.locator('#campoSenhaModal').is_visible():
        pg.fill('#inputSenhaModal', 'senha-de-teste')
    if pg.locator('#btnConfirmModalConfirmar').count():
        clicarId(pg, 'btnConfirmModalConfirmar'); pg.wait_for_timeout(600)
    r = pg.evaluate("DEV.reversa")
    ok(r and r.get('plataforma') == 'SuperFrete', 'grava a plataforma: %s' % (r or {}).get('plataforma'))
    ok(r and abs((r.get('valor') or 0) - 19.80) < 0.01, 'e o valor da oferta: %s' % (r or {}).get('valor'))

    # O passo do meio: pedido gerado, codigo inexistente. Sem ele visivel,
    # alguem avisa o cliente e o manda a agencia a toa.
    ok(r and r.get('codigo') == '', 'o codigo nasce VAZIO: ele sai depois do pagamento')
    ok('ainda não saiu' in pg.inner_text('#avisoReversaTexto'),
       'e a tela nomeia esse estado, em vez de dizer so que foi pedida')
    ok('não foi avisado' in pg.inner_text('#avisoReversaTexto'),
       'dizendo que o cliente ainda NAO foi avisado')
    ok(pg.locator('#linhaCodReversa').is_visible(), 'e abre o campo para registrar o codigo')
    soInterno = pg.evaluate(
        'DEV.eventos.filter(e => e.tipo === "reversa").every(e => e.interna === true)')
    ok(soInterno, 'enquanto nao ha codigo, nada da reversa vai para a vitrine')

    # Codigo curto demais e recusado: um codigo errado manda o cliente a toa.
    pg.fill('#inputCodReversa', 'ab12'); pg.wait_for_timeout(200)
    clicarId(pg, 'btnCodReversa'); pg.wait_for_timeout(500)
    ok(pg.evaluate("DEV.reversa.codigo") == '', 'codigo curto nao e aceito')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    pg.fill('#inputCodReversa', 'ab123456789br'); pg.wait_for_timeout(200)
    clicarId(pg, 'btnCodReversa'); pg.wait_for_timeout(600)
    if pg.locator('#confirmModal.open').count() and pg.locator('#btnConfirmModalConfirmar').count():
        clicarId(pg, 'btnConfirmModalConfirmar'); pg.wait_for_timeout(600)
    ok(pg.evaluate("DEV.reversa.codigo") == 'AB123456789BR',
       'o codigo e gravado em maiuscula: %s' % pg.evaluate("DEV.reversa.codigo"))
    # Padrao Shopee: devolucao aprovada, codigo no pedido do cliente.
    temVitrine = pg.evaluate(
        'DEV.eventos.some(e => e.tipo === "reversa" && !e.interna && String(e.nota).indexOf("AB123456789BR") >= 0)')
    ok(temVitrine, 'e SO entao o codigo vira evento de vitrine, visivel para o cliente')
    ok(not pg.locator('#linhaCodReversa').is_visible(), 'o campo some depois de registrado')

    print('\n[12c] O frete sai do PESO FATURADO, nao do peso da balanca')
    # Frete e cobrado pelo maior entre peso real e peso cubado — (CxLxA)/6000.
    # Com uma excecao que muda a conta: nos Correios, Jadlog e Loggi, cubagem
    # de ate 5kg e desconsiderada e vale o peso real. Cotar so pelo peso real
    # subestima tudo o que e volumoso, e a diferenca volta como debito depois.
    pg.goto(URL + DET + '?id=1'); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    pe = pg.evaluate("pesoDaDevolucao()")
    ok(pe and pe.get('real', 0) > 0, 'a tela calcula o peso real dos itens que voltam: %s' % (pe or {}).get('real'))
    ok(pe and pe.get('cubado', 0) > 0, 'e a cubagem da embalagem: %s' % (pe or {}).get('cubado'))
    # O peso vem do ITEM mais a embalagem, entao mexer na quantidade mexe nele.
    antes = pe['real']
    pg.fill('input[data-qtd="0"]', '6'); pg.wait_for_timeout(300)
    depois = pg.evaluate("pesoDaDevolucao().real")
    ok(depois > antes, 'devolver mais pecas pesa mais (%.3f -> %.3f)' % (antes, depois))
    pg.fill('input[data-qtd="0"]', '2'); pg.wait_for_timeout(300)

    # A regra dos 5kg: abaixo dela a cubagem nao conta, e e o caso da caixa
    # media. A asserção mede a REGRA, nao o numero do exemplo.
    regra = pg.evaluate(
        '(function(){var p=pesoDaDevolucao();'
        'return p.contaCubagem === (p.cubado > CUBAGEM_MINIMA);})()')
    ok(regra, 'a cubagem so conta acima do piso de 5kg')
    coerente = pg.evaluate(
        '(function(){var p=pesoDaDevolucao();'
        'return p.faturado === (p.contaCubagem ? Math.max(p.real,p.cubado) : p.real);})()')
    ok(coerente, 'e o faturado e o maior dos dois quando ela conta, senao o real')

    clicarId(pg, 'btnReversa'); pg.wait_for_timeout(500)
    ok('Faturado' in pg.inner_text('#revPeso'),
       'o painel mostra de onde o preco sai, em vez de so entregar um numero')
    clicarId(pg, 'revCancelar'); pg.wait_for_timeout(300)

    print('\n[12d] A transportadora reafere, e o financeiro acompanha')
    # O pacote e pesado de novo na agencia e a diferenca e repassada. Antes a
    # reversa gravava UM valor, o simulado: se o frete era do cliente, a conta
    # a receber ficava errada; se era nosso, a despesa ficava subdimensionada.
    clicarId(pg, 'btnReversa'); pg.wait_for_timeout(400)
    clicarId(pg, 'revConfirmar'); pg.wait_for_timeout(600)
    if pg.locator('#confirmModal.open').count():
        clicarId(pg, 'btnConfirmModalConfirmar'); pg.wait_for_timeout(500)
    pg.fill('#inputCodReversa', 'aa111111111br'); pg.wait_for_timeout(200)
    clicarId(pg, 'btnCodReversa'); pg.wait_for_timeout(600)
    if pg.locator('#confirmModal.open').count():
        clicarId(pg, 'btnConfirmModalConfirmar'); pg.wait_for_timeout(500)

    ok(pg.locator('#linhaReal').is_visible(),
       'depois da postagem, abre o campo da cobranca real')
    ok('ainda não cobrado' in pg.inner_text('#docRevReal'),
       'e ate la o campo diz que nao houve cobranca, em vez de repetir o cotado')
    cotado = pg.evaluate("DEV.reversa.valor")

    pg.fill('#inputFreteReal', '31,70'); pg.fill('#inputPesoReal', '4,1'); pg.wait_for_timeout(200)
    clicarId(pg, 'btnFreteReal'); pg.wait_for_timeout(700)
    if pg.locator('#campoSenhaModal').count() and pg.locator('#campoSenhaModal').is_visible():
        pg.fill('#inputSenhaModal', 'senha-de-teste')
    if pg.locator('#confirmModal.open').count():
        clicarId(pg, 'btnConfirmModalConfirmar'); pg.wait_for_timeout(600)
    ok(abs(pg.evaluate("DEV.reversa.real") - 31.70) < 0.01, 'a cobranca real e gravada')
    ok(abs(pg.evaluate("DEV.reversa.pesoReal") - 4.1) < 0.01, 'e o peso aferido junto')
    ok(cotado != pg.evaluate("DEV.reversa.real"),
       'cotado e real sao campos DIFERENTES: um nao sobrescreve o outro')
    ok('+' in pg.inner_text('#docRevDif'), 'a diferenca aparece com sinal: %s' % pg.inner_text('#docRevDif'))
    # Reafericao e conversa nossa com a transportadora: o cliente nao tem o que
    # fazer com ela. Se o frete era dele, a mudanca aparece na conta a receber.
    interno = pg.evaluate(
        'DEV.eventos.filter(e => String(e.nota).indexOf("Cobrança real") >= 0).every(e => e.interna === true)')
    ok(interno, 'e o evento da reafericao e INTERNO, nao vai para a vitrine')
    ok(not pg.locator('#linhaReal').is_visible(), 'o campo some depois de registrado')

    print('\n[13] Finalizar com estoque pendente e barrado')
    pg.goto(URL + DET + '?id=4'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.evaluate("!estoqueLancado(DEV)"), 'a DV-0009 ainda nao teve estoque lancado')
    temPendente = pg.evaluate("podeLancarEstoque(DEV)")
    pg.locator('#menuMaisAcoes .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#menuMaisAcoes [data-acao="finalizar"]').click(); pg.wait_for_timeout(450)
    if temPendente:
        ok('não entrou no saldo' in pg.inner_text('body').lower(),
           'a tela explica que a caixa ficaria fora do saldo')
        ok(pg.evaluate("DEV.situacao") != 'finalizada', 'e nao finaliza')
    else:
        # Nesta devolucao nada volta ao estoque (extravio): finalizar e legitimo.
        ok(pg.evaluate("DEV.situacao") in ('finalizada', 'aberta'),
           'extravio nao tem estoque a lancar, entao finalizar e caminho normal')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[14] Cancelar depois de lancar o estoque e barrado')
    pg.goto(URL + DET + '?id=3'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.evaluate("estoqueLancado(DEV)"), 'a DV-0010 ja teve o estoque lancado pela conferencia')
    pg.locator('#menuMaisAcoes .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#menuMaisAcoes [data-acao="cancelar"]').click(); pg.wait_for_timeout(450)
    ok('acerto de estoque' in pg.inner_text('body').lower(),
       'a tela diz qual e a saida real')
    ok(pg.evaluate("DEV.situacao") != 'cancelada', 'e nao cancela')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[15] Nova devolucao nasce da VENDA, com tudo o que foi vendido')
    pg.goto(URL + DET + '?venda=2'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok('nova' in pg.inner_text('#tituloDev').lower(), 'a tela se apresenta como nova')
    vendaItens = pg.evaluate("vendaDe(2).itens.length")
    ok(pg.locator('#corpoItens tr').count() == vendaItens,
       'ela nasce com os %d itens da venda, para quem recebe RETIRAR o que nao voltou' % vendaItens)
    ok('ainda não existe' in pg.inner_text('#infoPendente').lower(),
       'o rodape diz que salvar e o que abre a devolucao')
    ok(pg.evaluate("DEV.origem") == 'pedido', 'ela nasce com origem pedido')

    print('\n[16] A nota fiscal de devolucao fica RESERVADA')
    corpoD = pg.inner_text('.main').lower()
    ok('reservado' in corpoD, 'a tela marca o bloco fiscal como reservado')
    ok('nf-e' in corpoD, 'e diz que depende da emissao de NF-e')
    ok('sefaz' in corpoD, 'explicando que no Olist e a SEFAZ que finaliza sozinha')

    print('\n[17] Os dois parametros nasceram em Configuracoes')
    p3 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p3.goto(URL + 'pagina-configuracoes-parametros-estoque.html'); p3.wait_for_timeout(700)
    ok(p3.locator('#devDeposito').count() == 1, 'o deposito da devolucao tem campo na tela')
    ok(p3.locator('[data-param="devolucaoPrazoDias"]').count() == 1, 'o prazo tambem')
    nas = p3.evaluate("CHAVES.indexOf('devolucaoDeposito') >= 0 && CHAVES.indexOf('devolucaoPrazoDias') >= 0")
    ok(nas, 'e os dois entram no que a tela salva')
    # Parametro que aparece e nao grava e enfeite: o teste grava e reabre.
    p3.locator('#devDeposito .dropdown-select-btn').click(); p3.wait_for_timeout(250)
    p3.locator('#devDeposito .dropdown-select-item[data-value="geral"]').click(); p3.wait_for_timeout(250)
    p3.fill('#devPrazo', '21'); p3.wait_for_timeout(250)
    p3.evaluate("window.scrollTo(0,0)")
    p3.locator('#btnSalvarParam').click(); p3.wait_for_timeout(500)
    for sel in ['#btnConfirmModalConfirmar', '#btnAvisoOk']:
        if p3.locator(sel).count() and p3.locator(sel).is_visible():
            p3.evaluate("document.querySelector('%s').click()" % sel); p3.wait_for_timeout(400); break
    salvo = p3.evaluate("JSON.parse(localStorage.getItem('deskParametros')||'{}')")
    ok(salvo.get('devolucaoDeposito') == 'geral', 'o deposito grava: %s' % salvo.get('devolucaoDeposito'))
    ok(salvo.get('devolucaoPrazoDias') == 21, 'o prazo grava: %s' % salvo.get('devolucaoPrazoDias'))

    print('\n[18] O parametro MANDA de verdade na tela de devolucao')
    # Parametro que a tela ignora e pior que parametro inexistente: ele promete.
    # Segue na MESMA pagina: no Playwright cada new_page nasce num contexto
    # proprio, e o localStorage de uma nao chega na outra.
    p3.goto(URL + DET + '?id=1'); p3.wait_for_load_state('load'); p3.wait_for_timeout(700)
    ok('geral' in p3.inner_text('#docEstDeposito').lower(),
       'com o parametro em Geral, o destino vira Geral: %s' % p3.inner_text('#docEstDeposito'))
    ok(p3.evaluate("PRAZO_DEV") == 21, 'e o prazo lido e o que foi salvo (%s)' % p3.evaluate("PRAZO_DEV"))
    p3.evaluate("localStorage.removeItem('deskParametros')")
    p3.close()

    print('\n[19] A trava nasce com a tela')
    pg.goto(URL + DET + '?id=1'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    chaves = ['devolucaoCria', 'devolucaoConfirmaChegada', 'devolucaoFinaliza',
              'devolucaoCancela', 'devolucaoReversa']
    for k in chaves:
        achou = pg.evaluate("ACOES_ESPECIFICAS.some(a => a.chave === '%s')" % k)
        ok(achou, 'a acao %s esta no catalogo' % k)
    senha = pg.evaluate("""['devolucaoFinaliza','devolucaoCancela']
      .every(k => ACOES_ESPECIFICAS.filter(a => a.chave === k)[0].exigePadrao === true)""")
    ok(senha, 'finalizar e cancelar nascem exigindo senha')
    # Confirmar chegada NAO pede senha: e um fato da portaria, nao uma decisao
    # sobre o saldo. Quem mexe no saldo e a conferencia, e la a trava e outra.
    semSenha = pg.evaluate(
        "ACOES_ESPECIFICAS.filter(a => a.chave === 'devolucaoConfirmaChegada')[0].exigePadrao === false")
    ok(semSenha, 'confirmar chegada nasce SEM senha: e fato da portaria, nao decisao de saldo')
    p5 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p5.goto(URL + 'pagina-configuracoes-confirmacoes-senha.html'); p5.wait_for_timeout(600)
    todas = p5.evaluate("['%s'].every(k => ACOES_ESPECIFICAS.some(a => a.chave === k))" % "','".join(chaves))
    ok(todas, 'e Configuracoes conhece as cinco')
    p5.close()

    print('\n[20] Nos dois temas, sem erro de JS')
    for alvo in [LISTA, DET + '?id=1']:
        pg.goto(URL + alvo); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        for tema in ['claro', 'escuro']:
            pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
            pg.wait_for_timeout(220)
            est = pg.evaluate("""() => ({
              fonte: getComputedStyle(document.body).fontFamily,
              larg: document.documentElement.scrollWidth
            })""")
            ok('unito' in est['fonte'], '%s tema %s: fonte Nunito' % (alvo.split('?')[0][-18:], tema))
            ok(est['larg'] <= 1440, '%s tema %s: nao estoura em 1440 (%d)' % (alvo.split('?')[0][-18:], tema, est['larg']))
    ok(not erros, 'sem erro de JS nas duas telas: %s' % erros[:2])

    print('\n[21b] A nota da devolucao aparece na Entrada de Notas e na fila')
    # A promessa do fluxo so vale se o documento aparecer do OUTRO lado. Sem
    # isto, "nasce uma nota de entrada" e texto na tela de devolucao.
    p6 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p6.goto(URL + 'pagina-estoque-entrada-notas.html'); p6.wait_for_timeout(800)
    temTransito = p6.evaluate("NOTAS.some(n => n.origem === 'devolucao' && n.situacao === 'transito')")
    ok(temTransito, 'Entrada de Notas tem devolucao em transito')
    ok(p6.locator('.aba-sit[data-sit="transito"]').count() == 1, 'e a aba Em transito existe la')
    semMde = p6.evaluate("""() => {
      const n = NOTAS.filter(x => x.origem === 'devolucao')[0];
      return celulaMde(n).indexOf('naoseaplica') >= 0;
    }""")
    ok(semMde, 'manifestacao nao se aplica a devolucao: a coluna mostra tracinho')
    p6.goto(URL + 'pagina-estoque-conferencia-entrada.html'); p6.wait_for_timeout(800)
    naFila = p6.evaluate("NOTAS.some(n => n.origem === 'devolucao')")
    ok(naFila, 'e a devolucao entra na fila de Conferencia de Entrada')
    ok('Conferência de Entrada' in p6.inner_text('h1'),
       'que mudou de nome, porque nao recebe so compra: %s' % p6.inner_text('h1'))
    p6.close()

    print('\n[21] O item de menu deixou de ser inerte')
    href = pg.evaluate("""() => {
      const el = Array.from(document.querySelectorAll('.flyout-item'))
        .filter(e => (e.getAttribute('data-label') || '') === 'Devolução')[0];
      return el ? el.getAttribute('data-href') : null;
    }""")
    ok(href == LISTA, 'o item do menu leva a listagem: %s' % href)

    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas: print('  - ' + f)

raise SystemExit(1 if falhas else 0)
