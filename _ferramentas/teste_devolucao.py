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

    print('\n[8] Lancar estoque e ACAO EXPLICITA, e muda o saldo uma vez so')
    ok(pg.locator('#btnLancarEstoque:visible').count() == 1, 'ha um botao de lancar estoque')
    ok('ainda não lançado' in pg.inner_text('#docEstQuando').lower(), 'antes de lancar, a tela diz que nao lancou')
    ok('parâmetro' in pg.inner_text('#docEstDeposito').lower(),
       'e diz que o deposito vem do parametro: %s' % pg.inner_text('#docEstDeposito'))
    pg.locator('#btnLancarEstoque').click(); pg.wait_for_timeout(450)
    ok(pg.locator('#confirmModal.open').count() == 1, 'lancar para no modal de confirmacao')
    ok(pg.evaluate("!DEV.estoque"), 'e nao lanca sozinho')
    pg.fill('#inputSenhaModal', 'senha-de-teste')
    pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(600)
    ok(pg.evaluate("!!DEV.estoque"), 'confirmado, o estoque e lancado')
    ok(pg.locator('#btnLancarEstoque:visible').count() == 0,
       'e o botao some: lancar duas vezes duplicaria a entrada')
    ok('já entrou' in pg.inner_text('#avisoEstoqueTexto').lower() or
       'já entraram' in pg.inner_text('#avisoEstoqueTexto').lower(),
       'o aviso passa a falar no passado')

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

    print('\n[13] Finalizar com estoque pendente e barrado')
    pg.goto(URL + DET + '?id=4'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.evaluate("!DEV.estoque"), 'a DV-0009 ainda nao teve estoque lancado')
    temPendente = pg.evaluate("podeLancarEstoque(DEV)")
    pg.locator('#menuMaisAcoes .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#menuMaisAcoes [data-acao="finalizar"]').click(); pg.wait_for_timeout(450)
    if temPendente:
        ok('lançar no estoque' in pg.inner_text('body').lower(),
           'a tela explica que a caixa ficaria fora do saldo')
        ok(pg.evaluate("DEV.situacao") != 'finalizada', 'e nao finaliza')
    else:
        # Nesta devolucao nada volta ao estoque (extravio): finalizar e legitimo.
        ok(pg.evaluate("DEV.situacao") in ('finalizada', 'aberta'),
           'extravio nao tem estoque a lancar, entao finalizar e caminho normal')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[14] Cancelar depois de lancar o estoque e barrado')
    pg.goto(URL + DET + '?id=3'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.evaluate("!!DEV.estoque"), 'a DV-0010 ja teve o estoque lancado')
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
    chaves = ['devolucaoCria', 'devolucaoLancaEstoque', 'devolucaoFinaliza',
              'devolucaoCancela', 'devolucaoReversa']
    for k in chaves:
        achou = pg.evaluate("ACOES_ESPECIFICAS.some(a => a.chave === '%s')" % k)
        ok(achou, 'a acao %s esta no catalogo' % k)
    senha = pg.evaluate("""['devolucaoLancaEstoque','devolucaoFinaliza','devolucaoCancela']
      .every(k => ACOES_ESPECIFICAS.filter(a => a.chave === k)[0].exigePadrao === true)""")
    ok(senha, 'mexer no saldo, finalizar e cancelar nascem exigindo senha')
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
