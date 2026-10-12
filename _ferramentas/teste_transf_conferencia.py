# -*- coding: utf-8 -*-
# A chegada da transferencia e uma conferencia de entrada (decisao do usuario em 12/out/2026).
#
#   [1] na Transferencia Entre Estoques o painel de recebimento, que vinha com a quantidade
#       preenchida, saiu: o botao e "Conferir chegada" e leva a contagem;
#   [2] a contagem e a da nota de entrada: cega. A quantidade enviada fica escondida ate contar, e
#       nao vaza pelo resumo;
#   [3] sem divergencia, tudo entra e a transferencia encerra; a pessoa volta para a lista, que diz
#       o que aconteceu, e o painel passa a mostrar quem recebeu;
#   [4] chegou menos e "o resto ainda vem": segue em transito, e da para conferir de novo so o resto;
#   [5] chegou menos e "faltou": vai para Tratamento de Perdas como falta a auditar. A avaria que
#       ficou conosco tambem vai; a que voltou com o transportador segue em transito;
#   [6] a fila da Conferencia de Entrada mostra a transferencia a caminho, e leva a contagem dela;
#   [7] fechar pede a senha do recebimento, e o numero que vem no endereco nao e aceito de olhos
#       fechados. A conferencia da nota segue como era.
from playwright.sync_api import sync_playwright
import datetime, os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

TRANSF, FILA, CONF = 'pagina-estoque-transferencia.html', 'pagina-estoque-conferencia-entrada.html', 'pagina-estoque-conferencia.html'
PERDAS, INICIO = 'pagina-estoque-itens-bloqueados.html', 'pagina-inicio-boas-vindas.html'
GUARDADO = ['deskTransferencias', 'deskBloqueados', 'deskBloqueiosEntrada', 'deskParametros', 'deskLog']
MARCA = '  // ===== O QUE A CONFERENCIA JA FEZ COM A TRANSFERENCIA (bloco compartilhado, 12/out/2026) ====='
FIM = '  // ===== FIM DO BLOCO DA CONFERENCIA DE TRANSFERENCIA ====='
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
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    hoje = datetime.date.today().strftime('%d/%m/%Y')

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def do_zero(tela, query=''):
        ir(tela)
        pg.evaluate("(chaves) => chaves.forEach(k => localStorage.removeItem(k))", GUARDADO)
        ir(tela, query)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def texto(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; }", sel)

    def linha_tr(num):
        return pg.evaluate("(n) => { const tr = document.querySelector('#corpoTabela tr[data-num=\"' + n + '\"]'); return tr ? tr.innerText.replace(/\\s+/g, ' ').trim() : null; }", num)

    def guardado():
        return pg.evaluate("JSON.parse(localStorage.getItem('deskTransferencias') || '{}')")

    def caixa_de_perdas():
        return pg.evaluate("Object.values(JSON.parse(localStorage.getItem('deskBloqueiosEntrada') || '{}')).map(b => [b.sku, b.motivo, b.qtd, b.origem, b.doc, b.dep])")

    # --- a contagem ---
    def contar(i, valor):
        pg.fill('.qtd-input[data-i="%d"]' % i, str(valor)); pg.wait_for_timeout(120)

    def celulas(i):
        return pg.evaluate("(i) => [document.querySelector('.cel-nota[data-i=\"' + i + '\"]').textContent.trim(), document.querySelector('.cel-dif[data-i=\"' + i + '\"]').textContent.trim()]", i)

    def confirmar_modal(senha='senha'):
        if pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"):
            pg.fill('#inputSenhaModal', senha)
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(350)

    def validar(i):
        clic('[data-validar="%d"]' % i); pg.wait_for_timeout(250); confirmar_modal()

    def motivo(i, qual, destino=None):
        clic('#motivo-%d .dropdown-select-btn' % i); pg.wait_for_timeout(120)
        clic('#motivo-%d .dropdown-select-item[data-value="%s"]' % (i, qual)); pg.wait_for_timeout(200)
        if destino:
            clic('#destino-%d .dropdown-select-btn' % i); pg.wait_for_timeout(120)
            clic('#destino-%d .dropdown-select-item[data-value="%s"]' % (i, destino)); pg.wait_for_timeout(200)

    def abrir_fechamento():
        clic('#btnFinalizar'); pg.wait_for_timeout(400)
        return pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')")

    def fechar(resto=None, senha='senha'):
        """Do painel de fechamento ate a volta para a lista de transferencias."""
        if resto:
            clic('#selResto .dropdown-select-btn'); pg.wait_for_timeout(120)
            clic('#selResto .dropdown-select-item[data-value="%s"]' % resto); pg.wait_for_timeout(200)
        clic('#btnConfirmarFechamentoTransf'); pg.wait_for_timeout(350)
        dito = pg.inner_text('#confirmModalTexto')
        confirmar_modal(senha); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        return dito

    def painel(num):
        clic('#corpoTabela tr[data-num="%s"] td:nth-child(2)' % num); pg.wait_for_timeout(350)
        r = pg.evaluate("""() => { const t = (id) => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
            const a = document.querySelector('#verPerdas a');
            return { sit: t('verSituacao'), chegada: t('verChegada'), itens: Array.from(document.querySelectorAll('#verItens .rep-origem')).map(e => e.textContent.replace(/\\s+/g, ' ').trim()),
                     conferir: !!document.getElementById('btnConferirDoPainel'), perdas: a ? a.getAttribute('href') : null }; }""")
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        return r

    if secao(1, 'Na Transferencia, o recebimento saiu e o botao leva a contagem'):
        do_zero(TRANSF)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        src = fonte(TRANSF)
        ok(pg.locator('#recDrawer').count() == 0 and 'Confirmar recebimento' not in src and 'abrirRecebimento' not in src, 'o painel "Confirmar recebimento", que vinha com a quantidade preenchida, nao existe mais')
        botoes = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr[data-num]')).map(tr => [tr.getAttribute('data-num'), (tr.querySelector('button') || { textContent: '' }).textContent.trim()])")
        ok(botoes == [['TR-0101', 'Conferir chegada'], ['TR-0100', 'Conferir chegada'], ['TR-0099', '']], 'transferencia com mercadoria a caminho tem o botao "Conferir chegada"; a recebida, nenhum: %s' % botoes)
        ok('confere a chegada' in pg.inner_text('.subtitle') and 'conferida como uma nota de entrada' in pg.inner_text('.nota-reservado') and 'o resto ainda vem' in pg.inner_text('.nota-reservado'),
           'o topo da tela explica a chegada como conferencia, e o que acontece com o que nao chega')
        ok(pg.evaluate("Array.from(document.querySelectorAll('.estoque-table th')).map(t => t.textContent.trim()).pop()") == 'Chegada', 'a coluna do botao se chama "Chegada"')
        clic('#corpoTabela tr[data-num="TR-0101"] [data-acao="conferir"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.endswith(CONF + '?transf=TR-0101') and pg.inner_text('#tituloConf') == 'Conferência da transferência TR-0101', 'o botao da linha leva a contagem daquela transferencia: %s' % pg.url.split('/')[-1])
        ir(TRANSF)
        clic('#corpoTabela tr[data-num="TR-0100"] td:nth-child(2)'); pg.wait_for_timeout(350)
        clic('#btnConferirDoPainel'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.endswith(CONF + '?transf=TR-0100'), 'e o botao do painel tambem: %s' % pg.url.split('/')[-1])

    if secao(2, 'A contagem e a da nota: cega, e o enviado nao vaza'):
        do_zero(CONF, '?transf=TR-0101')
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        quadros = pg.evaluate("Array.from(document.querySelectorAll('.doc-grid .doc-item')).filter(e => e.offsetParent !== null).map(e => [e.querySelector('.doc-rotulo').textContent, e.querySelector('.doc-valor').textContent])")
        ok(quadros == [['Transferência', 'TR-0101'], ['Saiu de', 'Galpão Centro'], ['Enviada em', '12/09/2026 · Carlos Mendes'], ['Depósito de destino', 'Loja Física Aldeota'], ['Chegou em', hoje]],
           'o documento diz de onde a transferencia veio, e nao fala de fornecedor, ordem de compra nem valor: %s' % quadros)
        ok(pg.inner_text('#breadcrumb').replace('\n', ' ').strip().endswith('Transferência TR-0101') and texto('#thQtdNota') == 'Qtde enviada', 'o caminho e a coluna falam de transferencia e de quantidade enviada')
        itens = pg.evaluate("Array.from(document.querySelectorAll('#corpoItens .item-nome')).map(e => e.textContent)")
        ok(itens == ['Teclado Mecânico Desk', 'Cabo HDMI 2.1 · 2m'] and pg.evaluate("cego") is True, 'os itens sao os da transferencia, e a conferencia abre cega: %s' % itens)
        ok(celulas(0)[0] == 'oculta' and celulas(1)[0] == 'oculta', 'antes de contar, a quantidade enviada esta oculta nos dois itens')
        visivel = pg.inner_text('#tabelaItens') + ' ' + pg.inner_text('.totais-grid')
        ok(pg.evaluate("document.getElementById('totValorNota').parentElement.offsetParent === null") and pg.inner_text('#totValorConferido') == '0'
           and texto('.totais-grid .total-item.destaque .total-rotulo') == 'Unidades conferidas' and not re.search(r'\b(8|12|20)\b', visivel),
           'o resumo mostra so o que foi contado: nem 8, nem 12, nem 20 aparecem na tela antes da contagem')
        contar(0, 8)
        ok(celulas(0) == ['8', 'confere'], 'contou certo: a quantidade enviada aparece e o item confere: %s' % celulas(0))
        contar(1, 10)
        ok(celulas(1) == ['oculta', 'divergência'] and pg.inner_text('#totValorConferido') == 'aguardando confirmação',
           'contou diferente: a tela diz que ha divergencia, sem dizer quanto, e o enviado segue oculto: %s' % celulas(1))
        ok(not abrir_fechamento() and 'não confirmada' in pg.inner_text('#erroItens'), 'com divergencia nao confirmada, a conferencia nao fecha')
        validar(1)
        ok(celulas(1) == ['12', '-2'] and pg.inner_text('#totValorConferido') == '18', 'confirmada a contagem, o enviado e a diferenca aparecem: %s' % celulas(1))
        ok(not abrir_fechamento() and 'motivo' in pg.inner_text('#erroItens'), 'e a divergencia exige motivo antes de fechar')
        ok('entra no depósito de destino' in pg.inner_text('#textoProcedimento') and 'fornecedor' not in pg.inner_text('#textoProcedimento'), 'o procedimento fala do deposito de origem, e nao de fornecedor')

    if secao(3, 'Sem divergencia: tudo entra, a transferencia encerra e a lista diz o que houve'):
        do_zero(CONF, '?transf=TR-0101')
        contar(0, 8); contar(1, 12)
        ok(abrir_fechamento(), 'tudo contado e batendo, o fechamento abre')
        ok([texto('#fechaEnviadas'), texto('#fechaConferidas'), texto('#fechaDivergentes')] == ['20', '20', '0'] and pg.locator('#selResto').count() == 0 and 'Comunicado' not in texto('#drawerCorpo'),
           'o fechamento mostra 20 enviadas e 20 conferidas, sem pergunta do resto e sem comunicado a fornecedor')
        ok('Trânsito' in pg.inner_text('#drawerCorpo') and 'Loja Física Aldeota' in pg.inner_text('#drawerCorpo') and 'a endereçar' in pg.inner_text('#drawerCorpo'), 'e diz para onde o estoque vai')
        dito = fechar()
        ok('Fechar a conferência da TR-0101? 20 unidades entram em Loja Física Aldeota.' == dito, 'a confirmacao diz o que vai acontecer: %s' % dito)
        ok(pg.url.endswith(TRANSF + '?conferida=TR-0101'), 'fechar devolve a pessoa para a lista de transferencias: %s' % pg.url.split('/')[-1])
        faixa = texto('#faixaDaConferencia span')
        ok(faixa == 'Chegada da TR-0101 conferida: 20 unidades entraram em Loja Física Aldeota. Nada ficou em trânsito, e a transferência foi encerrada.', 'e a lista diz o que aconteceu: %s' % faixa)
        ok('Recebida' in linha_tr('TR-0101') and 'Conferir chegada' not in linha_tr('TR-0101') and [pg.inner_text('#cTransito'), pg.inner_text('#cParcial'), pg.inner_text('#cRecebida')] == ['0', '1', '2'],
           'a transferencia passou para Recebidas, sem botao de conferir: %s' % linha_tr('TR-0101'))
        a = painel('TR-0101')
        ok(a['sit'] == 'Recebida' and a['chegada'] == hoje + ' · Administrador Desk' and not a['conferir'] and 'recebido 8' in a['itens'][0] and 'recebido 12' in a['itens'][1] and 'em trânsito' not in ' '.join(a['itens']),
           'o painel diz quem recebeu e quando, com os itens recebidos: %s' % a['chegada'])
        ok(guardado()['TR-0101']['itens'] == {'TEC-MEC-006': {'recebido': 8, 'faltou': 0, 'avaria': 0}, 'CAB-HDM-009': {'recebido': 12, 'faltou': 0, 'avaria': 0}} and caixa_de_perdas() == [],
           'o que a conferencia apurou ficou guardado, e nada foi para Tratamento de Perdas')
        clic('#faixaDaConferencia button'); pg.wait_for_timeout(150)
        ok(pg.locator('#faixaDaConferencia').count() == 0, '"Entendi" tira o aviso')
        ir(CONF, '?transf=TR-0101')
        ok('já foi conferida' in (texto('#semNadaAConferir') or '') and pg.locator('#btnFinalizar').count() == 0, 'conferir de novo o que ja chegou inteiro nao e possivel: %s' % texto('#semNadaAConferir'))

    if secao(4, 'Chegou menos e "o resto ainda vem": segue em transito, e se confere de novo'):
        do_zero(CONF, '?transf=TR-0101')
        contar(0, 8); contar(1, 10); validar(1); motivo(1, 'faltou_na_entrega')
        ok(abrir_fechamento(), 'com o motivo informado, o fechamento abre')
        ok((texto('#fechaNaoVeio') or '').startswith('2 unidades não vieram') and texto('#selResto .dropdown-select-label') == 'O resto ainda vem (segue em trânsito)'
           and pg.evaluate("Array.from(document.querySelectorAll('#selResto .dropdown-select-item')).map(e => e.textContent)") == ['O resto ainda vem (segue em trânsito)', 'Faltou (vai para Tratamento de Perdas)'] and 'como falta a auditar' in (texto('#fechaNaoVeio') or '')
           and pg.evaluate("(() => { const m = document.querySelector('#selResto .dropdown-select-menu'); m.classList.add('open'); const r = m.getBoundingClientRect(); m.classList.remove('open'); return r.right <= window.innerWidth && r.left >= document.getElementById('eventDrawer').getBoundingClientRect().left; })()"),
           'o fechamento pergunta do que nao chegou, com as duas saidas, abre em "o resto ainda vem", e o menu cabe no painel')
        dito = fechar()
        ok(dito.endswith('O que não veio (2) segue em trânsito.'), 'a confirmacao repete a escolha: %s' % dito[-45:])
        faixa = texto('#faixaDaConferencia span')
        ok('18 unidades entraram em Loja Física Aldeota.' in faixa and '2 seguem em trânsito' in faixa and 'Tratamento de Perdas' not in faixa, 'a lista diz que 18 entraram e 2 seguem na estrada: %s' % faixa)
        ok('Recebida em parte' in linha_tr('TR-0101') and '2 ainda em trânsito' in linha_tr('TR-0101') and 'Conferir chegada' in linha_tr('TR-0101') and caixa_de_perdas() == [],
           'a transferencia fica em Recebidas em parte, com o botao para conferir o resto, e nada vai para Tratamento de Perdas')
        clic('#corpoTabela tr[data-num="TR-0101"] [data-acao="conferir"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        itens = pg.evaluate("Array.from(document.querySelectorAll('#corpoItens .item-nome')).map(e => e.textContent)")
        ok(itens == ['Cabo HDMI 2.1 · 2m'] and celulas(0)[0] == 'oculta', 'a segunda conferencia traz so o que ainda esta a caminho, de novo as cegas: %s' % itens)
        contar(0, 2)
        ok(celulas(0) == ['2', 'confere'], 'e o que se espera agora sao as 2 que faltavam: %s' % celulas(0))
        abrir_fechamento(); fechar()
        ok('Recebida' in linha_tr('TR-0101') and 'em parte' not in linha_tr('TR-0101') and guardado()['TR-0101']['itens']['CAB-HDM-009']['recebido'] == 12,
           'chegado o resto, a transferencia encerra: as duas conferencias somam as 12')

    if secao(5, 'Chegou menos e "faltou": vai para Tratamento de Perdas; a avaria que ficou tambem'):
        do_zero(CONF, '?transf=TR-0101')
        contar(0, 7); validar(0); motivo(0, 'avaria', 'ficou')
        contar(1, 10); validar(1); motivo(1, 'faltou_na_entrega')
        abrir_fechamento()
        ok((texto('#fechaAvaria') or '').startswith('1 unidade avariada fica conosco') and 'Tratamento de Perdas' in (texto('#fechaAvaria') or '') and texto('#fechaConferidas') == '17', 'o fechamento separa a avaria que ficou: %s' % (texto('#fechaAvaria') or '')[:60])
        dito = fechar('faltou')
        ok(dito.endswith('O que não veio (2) vai para Tratamento de Perdas, como falta a auditar.'), 'escolhido "faltou", a confirmacao diz para onde vai: %s' % dito[-70:])
        faixa = texto('#faixaDaConferencia span')
        ok('17 unidades entraram' in faixa and '2 faltaram e estão em Tratamento de Perdas, como falta a auditar.' in faixa and '1 chegou avariada e está bloqueada em Tratamento de Perdas.' in faixa and 'Nada ficou em trânsito' in faixa,
           'a lista diz o que entrou, o que faltou e o que chegou avariado: %s' % faixa)
        ok('Recebida' in linha_tr('TR-0101') and 'em parte' not in linha_tr('TR-0101') and '2 em falta a auditar' in linha_tr('TR-0101') and '1 com avaria' in linha_tr('TR-0101'),
           'a transferencia encerra, com a falta e a avaria a vista na linha: %s' % linha_tr('TR-0101'))
        a = painel('TR-0101')
        ok('recebido 7' in a['itens'][0] and 'avaria 1' in a['itens'][0] and 'recebido 10' in a['itens'][1] and 'faltou 2' in a['itens'][1] and a['perdas'] == '../estoque/' + PERDAS + '?busca=TR-0101',
           'o painel mostra a avaria e a falta por item, e leva a Tratamento de Perdas: %s' % a['itens'])
        ok(sorted(caixa_de_perdas()) == [['CAB-HDM-009', 'falta', 2, 'conferencia_entrada', 'TR-0101', 3], ['TEC-MEC-006', 'avaria', 1, 'conferencia_entrada', 'TR-0101', 3]],
           'a falta e a avaria foram deixadas para Tratamento de Perdas, no deposito de destino: %s' % sorted(caixa_de_perdas()))
        ir(PERDAS)
        novos = pg.evaluate("ITENS.filter(i => i.doc === 'TR-0101').map(i => [i.sku, i.motivo, i.qtd]).sort()")
        ok(novos == [['CAB-HDM-009', 'falta', 2], ['TEC-MEC-006', 'avaria', 1]], 'Tratamento de Perdas recolhe os dois: %s' % novos)
        idn = pg.evaluate("ITENS.find(i => i.doc === 'TR-0101' && i.motivo === 'falta').id")
        clic('#corpoTabela tr[data-id="%d"]' % idn); pg.wait_for_timeout(380)
        link = pg.evaluate("(() => { const a = document.getElementById('linkOrigemBloqueio'); return a ? [a.textContent, a.getAttribute('href')] : null; })()")
        ok(link == ['TR-0101', '../estoque/' + TRANSF + '?busca=TR-0101'], 'e a origem do bloqueio leva a transferencia: %s' % link)
        ir(TRANSF, '?busca=TR-0101')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr[data-num]')).map(tr => tr.getAttribute('data-num'))") == ['TR-0101'], 'que abre filtrada naquela transferencia')

        do_zero(CONF, '?transf=TR-0101')
        contar(0, 7); validar(0); motivo(0, 'avaria', 'voltou'); contar(1, 12)
        abrir_fechamento()
        ok((texto('#fechaVolta') or '').startswith('1 unidade não entra neste depósito e segue em trânsito') and pg.locator('#fechaAvaria').count() == 0 and pg.locator('#selResto').count() == 0,
           'avaria que voltou com o transportador nao entra e segue em transito, sem pergunta do resto: %s' % (texto('#fechaVolta') or '')[:55])
        fechar()
        ok('Recebida em parte' in linha_tr('TR-0101') and '1 ainda em trânsito' in linha_tr('TR-0101') and caixa_de_perdas() == [], 'a transferencia fica em parte, e nada vai para Tratamento de Perdas')

    if secao(6, 'A fila da Conferencia de Entrada mostra a transferencia a caminho'):
        do_zero(FILA)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        pg.evaluate("(() => { itensPorPaginaAtual = 100; renderTabela(); })()"); pg.wait_for_timeout(250)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).filter(tr => tr.querySelector('.oc-numero').textContent.indexOf('TR-') === 0).map(tr => tr.innerText.replace(/\\s+/g, ' ').trim())")
        ok(len(linhas) == 2 and all('Transferência entre estoques' in l and 'Galpão Centro' in l and 'AGUARDANDO ENTRADA' in l.upper() and 'série' not in l for l in linhas)
           and 'Loja Física Aldeota' in ' '.join(linhas) and 'Showroom Parceiro Norte' in ' '.join(linhas),
           'as duas transferencias com mercadoria a caminho estao na fila, aguardando entrada, vindas do deposito de origem: %s' % [l[:60] for l in linhas])
        notas_aguardando = pg.evaluate("NOTAS.filter(n => n.origem !== 'transferencia' && n.situacao === 'aguardando').length")
        ok(pg.evaluate("document.querySelector('.sit-contador[data-cont=\"aguardando\"]').textContent") == str(notas_aguardando + 2), 'e contam na aba Aguardando entrada: %d notas mais 2 transferencias' % notas_aguardando)
        ok(pg.evaluate("Array.from(document.querySelectorAll('.estoque-table th')).slice(1, 3).map(t => t.textContent.replace('▲', '').trim())") == ['Documento', 'De onde vem'] and pg.inner_text('#contagemNotas').endswith(' entradas'),
           'as colunas e o rodape deixam de falar so de nota: %s' % pg.inner_text('#contagemNotas'))
        pg.fill('#campoBusca', 'tr-0101'); pg.wait_for_timeout(250)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela .oc-numero')).map(e => e.textContent)") == ['TR-0101'], 'a busca acha a transferencia pelo numero, em maiuscula ou minuscula')
        clic('#corpoTabela tr td:nth-child(2)'); pg.wait_for_timeout(350)
        corpo = pg.inner_text('#drawerCorpo')
        ok(pg.inner_text('#drawerTitulo') == 'Transferência TR-0101' and all(x in corpo for x in ['Saiu de', 'Galpão Centro', 'Loja Física Aldeota', '12/09/2026', 'a caminho']) and 'CNPJ' not in corpo and 'Valor da nota' not in corpo
           and pg.get_attribute('#drawerCorpo a.painel-link', 'href') == '../estoque/' + TRANSF + '?busca=TR-0101',
           'o painel da linha mostra os dados da transferencia, sem chave, CNPJ nem valor, e leva a ela')
        clic('#btnReceberUma'); pg.wait_for_timeout(300)
        ok('da transferência TR-0101' in pg.inner_text('#confirmModalTexto'), 'registrar a chegada chama o documento pelo nome: %s' % pg.inner_text('#confirmModalTexto')[:60])
        confirmar_modal()
        ok(pg.evaluate("NOTAS.find(n => n.numero === 'TR-0101').situacao") == 'pronto', 'registrada a chegada, a transferencia fica pronta para conferir')
        clic('#corpoTabela tr td:nth-child(2)'); pg.wait_for_timeout(350)
        clic('#btnAbrirConferencia'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.endswith(CONF + '?transf=TR-0101') and pg.inner_text('#tituloConf') == 'Conferência da transferência TR-0101', 'e "Iniciar conferência" leva a contagem dela: %s' % pg.url.split('/')[-1])
        contar(0, 8); contar(1, 12); abrir_fechamento(); fechar()
        ir(FILA)
        ok(pg.evaluate("NOTAS.find(n => n.numero === 'TR-0101').situacao") == 'conferida' and pg.evaluate("NOTAS.find(n => n.numero === 'TR-0100').situacao") == 'aguardando',
           'fechada a conferencia, a fila mostra a TR-0101 como conferida, e a outra segue aguardando')

        # Os espelhos: a fila e a contagem carregam a mesma copia, que bate com a tela de Transferencia.
        do_zero(TRANSF)
        forma = "t => [t.num, t.saiu, t.enviou, t.origem, t.destino, t.itens.map(i => [i.nome, i.sku, i.un, i.enviado, i.recebido])]"
        da_tela = pg.evaluate("TRANSFERENCIAS.filter(t => t.situacao !== 'recebida').map(%s)" % forma)
        ir(FILA); da_fila = pg.evaluate("TRANSF_A_CAMINHO.map(%s)" % forma)
        ir(CONF); da_contagem = pg.evaluate("TRANSF_A_CAMINHO.map(%s)" % forma)
        ok(da_tela == da_fila == da_contagem and len(da_tela) == 2, 'o espelho da fila e o da contagem batem com a tela de Transferencia: %d transferencias' % len(da_tela))
        blocos = []
        for tela in (TRANSF, FILA, CONF):
            s = fonte(tela)
            blocos.append(s[s.index(MARCA):s.index(FIM)] if s.count(MARCA) == 1 and s.count(FIM) == 1 else tela)
        ok(blocos[0] == blocos[1] == blocos[2] and len(blocos[0]) > 1500, 'o bloco que guarda e le a conferencia e identico nas tres telas')
        ir(FILA); abas = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.sit-contador')).map(e => [e.getAttribute('data-cont'), Number(e.textContent)]))")
        ir(INICIO); sub = texto('.dia-fila[data-fila="doca"] .dia-sub')
        ok(sub == '%d aguardando entrada · %d em conferência' % (abas['aguardando'], abas['emconferencia']), 'e Pendencias do Dia conta a mesma fila: %s' % sub)

    if secao(7, 'A senha do recebimento, o numero do endereco e a nota, que segue como era'):
        do_zero(CONF, '?transf=TR-0101')
        contar(0, 8); contar(1, 12); abrir_fechamento()
        clic('#btnConfirmarFechamentoTransf'); pg.wait_for_timeout(350)
        ok(pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'fechar a conferencia da transferencia pede a senha do recebimento')
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
        ok(CONF in pg.url and guardado() == {}, 'sem senha, nada e gravado e a pessoa continua na contagem')
        pg.fill('#inputSenhaModal', 'senha'); clic('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(pg.url.endswith(TRANSF + '?conferida=TR-0101') and 'TR-0101' in guardado(), 'com a senha, fecha')
        registro = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(l => l.chave === 'transfRecebe').length")
        ok(registro == 1, 'e a acao fica no registro de atividades')

        do_zero(CONF)
        pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ confirmacoes: { transfRecebe: false } }))")
        ir(CONF, '?transf=TR-0100')
        contar(0, 2); abrir_fechamento(); clic('#btnConfirmarFechamentoTransf'); pg.wait_for_timeout(350)
        ok(not pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'com a exigencia desligada em Configuracoes, a senha nao e pedida')
        clic('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok('Recebida' in linha_tr('TR-0100') and 'em parte' not in linha_tr('TR-0100') and guardado()['TR-0100']['itens']['CAM-DKB-011']['recebido'] == 2,
           'a transferencia que estava em parte recebe as 2 que faltavam e encerra')
        ok(painel('TR-0100')['itens'][0].find('recebido 10') > 0, '  somando com as 8 que ja tinham chegado')

        do_zero(CONF, '?transf=TR-9999')
        ok('não existe nesta lista de exemplo' in (texto('#semNadaAConferir') or '') and pg.locator('#btnFinalizar').count() == 0 and pg.inner_text('#tituloConf') == 'Conferência da transferência TR-9999',
           'numero de transferencia que nao existe: a tela diz isso, e nao abre contagem nenhuma')
        ir(CONF, '?transf=%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E')
        ok(pg.inner_text('#tituloConf') == 'Conferência da nota 9051' and pg.locator('img[src="x"]').count() == 0 and not erros, 'texto que nao e numero de transferencia e ignorado: a tela nao o escreve em lugar nenhum')

        ir(CONF, '?nota=4476')
        ok(pg.inner_text('#tituloConf') == 'Conferência da nota 4476' and texto('#thQtdNota') == 'Qtde da nota' and pg.evaluate("document.getElementById('totValorNota').parentElement.offsetParent !== null")
           and texto('.doc-grid .doc-item .doc-rotulo') == 'Nota' and pg.inner_text('#docValor').startswith('R$'), 'a conferencia da nota segue como era: titulo, coluna, valor e fornecedor')
        contar(0, 1); validar(0); motivo(0, 'faltou_na_entrega'); abrir_fechamento()
        ok('Saldo da ordem de compra' in texto('#drawerCorpo') and 'Comunicado ao fornecedor' in texto('#drawerCorpo') and pg.locator('#selResto').count() == 0,
           'e o fechamento dela continua com o saldo da ordem de compra e o comunicado ao fornecedor')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
