# -*- coding: utf-8 -*-
# Financas: os itens F1 a F4 da lista de melhorias (12/out/2026).
#
#   [1] F1  clicar na linha de Contas a Pagar e de Contas a Receber abre o painel da conta, sem sair
#           da lista, e dali se da a baixa;
#   [2] F2  a conta diz de onde veio e leva ate la: a nota de entrada e a ordem de compra (pagar), o
#           pedido e o cliente (receber). As contas que vem de nota batem com a Entrada de Notas, e a
#           nota leva de volta a conta;
#   [3] F3  indicadores: vencidas, vencem hoje, proximos 7 dias e total. Cada um soma o que diz somar,
#           e clicar faz a lista mostrar exatamente aquelas contas; clicar de novo desfaz;
#   [4] F4  no Caixa, a origem do lancamento leva a conta que o gerou.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

PAGAR, PAGAR_D = 'pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html'
RECEBER, RECEBER_D = 'pagina-financas-contas-receber.html', 'pagina-financas-contas-receber-detalhe.html'
CAIXA, NOTAS, OC = 'pagina-financas-caixa.html', 'pagina-estoque-entrada-notas.html', 'pagina-estoque-ordens-compra.html'
LISTAS = [(PAGAR, PAGAR_D, 'pago', 'drawerPagamento', 'emPagamento', 'Pagar'), (RECEBER, RECEBER_D, 'recebido', 'drawerRecebimento', 'emRecebimento', 'Receber')]
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


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(420)

    def tudo():
        """A lista inteira na tela: sem periodo, sem busca, 100 por pagina."""
        pg.evaluate("(() => { document.getElementById('limparFiltros').click(); const i = document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]'); if (i) i.click(); })()")
        pg.wait_for_timeout(250)

    def linha(idt):
        pg.evaluate("(id) => document.querySelector('#listaTitulos tr[data-id=\"' + id + '\"] td:nth-child(2)').click()", idt); pg.wait_for_timeout(320)

    def na_tela():
        return pg.evaluate("Array.from(document.querySelectorAll('#listaTitulos tbody tr[data-linha=titulo]')).map(tr => Number(tr.getAttribute('data-id')))")

    aberto = "document.getElementById('drawerConta').classList.contains('open')"

    if secao(1, 'F1: a linha abre o painel da conta, e dali se da a baixa'):
        for tela, detalhe, pago, drawer, fila, verbo in LISTAS:
            ir(tela); tudo()
            url = pg.url
            alvo = pg.evaluate("TITULOS.filter(t => !t.cancelado && saldoDe(t) > 0 && t.%s > 0)[0]" % pago) or pg.evaluate("TITULOS.filter(t => !t.cancelado && saldoDe(t) > 0)[0]")
            linha(alvo['id'])
            ok(pg.url == url and pg.evaluate(aberto), '%s: clicar na linha fica na lista e abre o painel da conta' % verbo)
            esperado = pg.evaluate("(id) => { const t = titDe(id); return ['R$ ' + fmtDin(t.valor), 'R$ ' + fmtDin(t.%s), 'R$ ' + fmtDin(saldoDe(t))]; }" % pago, alvo['id'])
            visto = pg.evaluate("['contaValor', 'contaPago', 'contaSaldo'].map(i => document.getElementById(i).textContent)")
            ok(visto == esperado and esperado[1] != 'R$ 0,00' and 'parcial' in pg.evaluate("document.getElementById('contaSelo').textContent"),
               '  com os tres valores da conta (valor, %s e saldo) e a marca de parcial: %s' % (pago, visto))
            ok(pg.get_attribute('#btnAbrirConta', 'href').endswith(detalhe + '?id=%d' % alvo['id']) and pg.evaluate("document.getElementById('contaCorpo').scrollWidth <= document.getElementById('drawerConta').clientWidth"),
               '  "Abrir a conta" leva a pagina dela, e o painel nao estoura na largura')
            ok(pg.inner_text('#btnBaixarDaConta') == verbo, '  conta com saldo tem o botao "%s"' % verbo)
            pg.evaluate("document.getElementById('btnBaixarDaConta').click()"); pg.wait_for_timeout(320)
            ok(not pg.evaluate(aberto) and pg.evaluate("document.getElementById('%s').classList.contains('open')" % drawer) and pg.evaluate(fila) == [alvo['id']],
               '  e o botao abre a baixa daquela conta, fechando o painel')
            pg.evaluate("fecharDrawers()"); pg.wait_for_timeout(200)
            quitada = pg.evaluate("TITULOS.filter(t => !t.cancelado && saldoDe(t) === 0)[0].id")
            cancelada = pg.evaluate("TITULOS.filter(t => t.cancelado)[0].id")
            linha(quitada); sem1 = pg.locator('#btnBaixarDaConta').count() == 0
            pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
            fechou = not pg.evaluate(aberto)
            linha(cancelada); sem2 = pg.locator('#btnBaixarDaConta').count() == 0 and pg.inner_text('#contaSaldo') == 'R$ 0,00'
            ok(sem1 and sem2 and fechou, '  conta quitada e conta cancelada nao oferecem a baixa, e Esc fecha o painel')
            pg.evaluate("fecharConta()")
            # a caixa de selecao e a seta de expandir continuam fazendo so o que faziam
            pg.evaluate("document.querySelector('#listaTitulos tbody [data-check=\"titulo\"]').click()"); pg.wait_for_timeout(200)
            pg.evaluate("document.querySelector('#listaTitulos .tit-chevron').click()"); pg.wait_for_timeout(200)
            ok(not pg.evaluate(aberto) and pg.evaluate("selTit.length") == 1 and pg.locator('#listaTitulos .tit-detalhe').count() == 1, '  marcar a caixa e expandir a linha nao abrem o painel')

    if secao(2, 'F2: a conta diz de onde veio, e leva ate la'):
        ir(NOTAS)
        notas = pg.evaluate("NOTAS.map(n => ({ numero: n.numero, fornecedor: n.fornecedor, valor: n.valor, situacao: n.situacao, oc: n.oc }))")
        espelho = pg.evaluate("NOTAS_COM_CONTA")
        ir(PAGAR)
        de_nota = pg.evaluate("TITULOS.filter(t => t.nota).map(t => ({ id: t.id, nota: t.nota, oc: t.oc, fornecedor: fornDe(t.fornId).nome, valor: t.valor, doc: t.doc }))")
        ruins = []
        for t in de_nota:
            n = [x for x in notas if x['numero'] == t['nota']]
            if not n or n[0]['fornecedor'] != t['fornecedor'] or abs(n[0]['valor'] - t['valor']) > 0.005 or n[0]['oc'] != t['oc'] or n[0]['situacao'] != 'lancada' or t['doc'] != 'NF %d' % t['nota']:
                ruins.append(t['doc'])
        ok(len(de_nota) >= 3 and not ruins, 'toda conta que vem de nota tem, na Entrada de Notas, a nota lancada com o mesmo fornecedor, valor e ordem (%d contas): %s' % (len(de_nota), ruins))
        ok(sorted(espelho) == sorted(t['nota'] for t in de_nota), 'e a Entrada de Notas sabe quais notas viraram conta: %s' % espelho)
        lista = pg.evaluate("JSON.stringify([FORNECEDORES, TITULOS.map(t => [t.id, t.fornId, t.doc, t.nota || 0, t.oc || 0, t.valor, t.pago, t.vencIso])])")
        ir(PAGAR_D)
        ok(pg.evaluate("JSON.stringify([FORNECEDORES, TITULOS.map(t => [t.id, t.fornId, t.doc, t.nota || 0, t.oc || 0, t.valor, t.pago, t.vencIso])])") == lista, 'a lista e a pagina da conta carregam os mesmos fornecedores e titulos')
        com_oc = [t for t in de_nota if t['oc']][0]
        sem_oc = [t for t in de_nota if not t['oc']][0]
        ir(PAGAR); tudo(); linha(com_oc['id'])
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#contaOrigem a')).map(a => a.getAttribute('href'))")
        ok(hrefs == ['../estoque/%s?busca=%d' % (NOTAS, com_oc['nota']), '../estoque/%s?busca=%d' % (OC, com_oc['oc'])], 'o painel de uma conta de nota leva a nota de entrada e a ordem de compra: %s' % [h.split('/')[-1] for h in hrefs])
        linha(sem_oc['id'])
        ok('nota sem ordem vinculada' in pg.inner_text('#contaOrigem') and pg.locator('#contaOrigem a').count() == 1, 'nota sem ordem de compra diz isso, em vez de um link para lugar nenhum')
        a_mao = pg.evaluate("TITULOS.filter(t => !t.nota && !t.grupo)[0].id")
        linha(a_mao)
        ok('Lançada à mão' in pg.inner_text('#contaOrigem') and pg.locator('#contaOrigem a').count() == 0, 'e conta lancada a mao diz que nao veio de nota')
        for dest, busca, quer in [(NOTAS, str(com_oc['nota']), com_oc['fornecedor']), (OC, str(com_oc['oc']), com_oc['fornecedor'])]:
            ir(dest, '?busca=' + busca)
            linhas = pg.evaluate("Array.from(document.querySelectorAll('.main tbody tr')).map(tr => tr.innerText)")
            ok(len(linhas) == 1 and quer in linhas[0], '  o link cai em %s, numa linha so, a de %s' % (dest.replace('pagina-estoque-', ''), quer))
        ir(PAGAR_D, '?id=%d' % com_oc['id'])
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#origemConta a')).map(a => a.getAttribute('href').split('/').pop())")
        ok(hrefs == ['%s?busca=%d' % (NOTAS, com_oc['nota']), '%s?busca=%d' % (OC, com_oc['oc'])] and 'veio da nota de entrada nº %d' % com_oc['nota'] in pg.inner_text('#subtituloConta'),
           'a pagina da conta tambem diz de que nota e de que ordem ela veio, com link')
        ir(PAGAR_D, '?id=%d' % a_mao)
        ok(pg.locator('#origemConta').count() == 0, '  e a de conta lancada a mao nao inventa origem')
        ir(NOTAS, '?busca=%d' % com_oc['nota'])
        pg.evaluate("document.querySelector('.main tbody tr td:nth-child(2)').click()"); pg.wait_for_timeout(350)
        ok(pg.locator('#linkContaDaNota').count() == 1, 'o painel da nota lancada tem o caminho de volta: "Ver a conta desta nota"')
        pg.evaluate("document.getElementById('linkContaDaNota').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(PAGAR in pg.url and na_tela() == [com_oc['id']], '  e ele cai em Contas a Pagar, na conta daquela nota')
        outra = [n for n in notas if n['numero'] not in espelho and n['situacao'] != 'lancada'][0]
        ir(NOTAS, '?busca=%d' % outra['numero'])
        pg.evaluate("document.querySelector('.main tbody tr td:nth-child(2)').click()"); pg.wait_for_timeout(350)
        ok(pg.locator('#linkContaDaNota').count() == 0, '  nota que ainda nao virou conta nao mostra o link')
        ir(RECEBER); tudo()
        de_pedido = pg.evaluate("TITULOS.filter(t => t.pedido && !t.cancelado)[0]")
        linha(de_pedido['id'])
        cliente = pg.evaluate("(id) => cliDe(titDe(id).cliId).nome", de_pedido['id'])
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#contaOrigem a')).map(a => decodeURIComponent(a.getAttribute('href')).split('/').pop())")
        ok(hrefs == ['pagina-vendas-pedidos.html?busca=' + cliente, 'pagina-cadastros-clientes.html?busca=' + cliente] and 'nº %d' % de_pedido['pedido'] in pg.inner_text('#contaOrigem'),
           'Contas a Receber: o painel leva ao pedido de venda e ao cadastro do cliente')
        ir('pagina-cadastros-clientes.html', '?busca=' + cliente)
        ok(pg.evaluate("Array.from(document.querySelectorAll('.main .card *')).filter(e => e.children.length === 0 && e.textContent.trim() === '%s').length" % cliente) >= 1, '  e o cadastro tem esse cliente')

    if secao(3, 'F3: os indicadores somam o que dizem, e clicar filtra a lista'):
        for tela, detalhe, pago, drawer, fila, verbo in LISTAS:
            ir(tela)
            padrao = pg.evaluate("[periodoAtual, abaAtual]")
            ok(pg.locator('.cp-kpis .kpi-card').count() == 4 and pg.locator('#filtroPeriodo .dropdown-select-item[data-value="0"]').count() == 1,
               '%s: quatro indicadores no topo, e o filtro de periodo ganhou "Vencem hoje"' % verbo)
            contas = pg.evaluate("""(() => { const hoje = HOJE_ISO, d = new Date(HOJE); d.setDate(d.getDate() + 7); const sete = iso(d);
                const vivo = TITULOS.filter(t => !t.cancelado && saldoDe(t) > 0), soma = (l) => 'R$ ' + fmtDin(l.reduce((s, t) => s + saldoDe(t), 0));
                const grupos = { vencidas: vivo.filter(t => t.vencIso < hoje), hoje: vivo.filter(t => t.vencIso === hoje), sete: vivo.filter(t => t.vencIso >= hoje && t.vencIso <= sete), total: vivo };
                return Object.fromEntries(Object.keys(grupos).map(k => [k, { valor: soma(grupos[k]), ids: grupos[k].map(t => t.id).sort((a, b) => a - b) }])); })()""")
            visto = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.cp-kpis .kpi-card')).map(c => [c.getAttribute('data-kpi'), c.querySelector('.kpi-value').textContent]))")
            ok(visto == {k: v['valor'] for k, v in contas.items()} and len(contas['total']['ids']) >= 5 and len(contas['vencidas']['ids']) >= 1,
               '  cada indicador soma o saldo das contas dele, contado a parte: %s' % visto)
            pg.evaluate("document.querySelector('#itensPorPagina .dropdown-select-item[data-value=\"100\"]').click()"); pg.wait_for_timeout(200)
            for k in ['vencidas', 'hoje', 'sete', 'total']:
                pg.evaluate("(k) => document.querySelector('.cp-kpis [data-kpi=\"' + k + '\"]').click()", k); pg.wait_for_timeout(260)
                acesos = pg.evaluate("Array.from(document.querySelectorAll('.cp-kpis .kpi-card.on')).map(c => c.getAttribute('data-kpi'))")
                ok(sorted(na_tela()) == contas[k]['ids'] and acesos == [k], '  clicar em "%s" deixa na lista exatamente as %d contas do indicador, e so ele fica aceso' % (k, len(contas[k]['ids'])))
            pg.evaluate("document.querySelector('.cp-kpis [data-kpi=total]').click()"); pg.wait_for_timeout(260)
            ok(pg.evaluate("[periodoAtual, abaAtual]") == padrao and pg.locator('.cp-kpis .kpi-card.on').count() == 0 and not pg.evaluate("soEmAberto"),
               '  clicar de novo no mesmo indicador desfaz: a lista volta ao periodo de abertura (%s)' % padrao[0])
            pg.evaluate("document.querySelector('.cp-kpis [data-kpi=vencidas]').click()"); pg.wait_for_timeout(220)
            pg.evaluate("document.querySelector('.sit-tab[data-aba=todas]').click()"); pg.wait_for_timeout(220)
            ok(pg.locator('.cp-kpis .kpi-card.on').count() == 0, '  e mexer na aba a mao apaga o indicador: ele so fica aceso enquanto a lista e a dele')
            pg.evaluate("document.querySelector('.cp-kpis [data-kpi=sete]').focus()"); pg.keyboard.press('Enter'); pg.wait_for_timeout(240)
            ok(pg.evaluate("kpiAtivo") == 'sete', '  o indicador tambem responde ao teclado (Enter)')
            ok(not pg.evaluate("document.documentElement.scrollWidth > window.innerWidth") and pg.evaluate("Array.from(document.querySelectorAll('.cp-kpis .kpi-card')).every(c => c.querySelector('.kpi-value').scrollWidth <= c.clientWidth)"),
               '  os quatro cabem na largura da tela, sem estourar o proprio quadro')

    if secao(4, 'F4: no Caixa, a origem do lancamento leva a conta que o gerou'):
        ir(PAGAR)
        pagas = pg.evaluate("TITULOS.filter(t => t.id <= 2).map(t => [t.id, t.valor, t.pago, fornDe(t.fornId).nome])")
        ir(CAIXA)
        pg.evaluate("localStorage.removeItem('deskCaixaExtras')"); ir(CAIXA)
        com_origem = pg.evaluate("MOVIMENTOS.filter(m => /^CP /.test(m.origem || '')).map(m => [Number(m.origem.slice(3)), m.valor, m.valor, m.pessoa])")
        ok(sorted(com_origem) == sorted(pagas) and len(pagas) == 2, 'os dois pagamentos do extrato que sao baixa de conta a pagar apontam para a conta certa: mesmo valor e mesmo fornecedor')
        pg.evaluate("(() => { contaAtualId = 2; periodoAtual = 'todos'; itensPorPaginaAtual = 100; render(); })()"); pg.wait_for_timeout(300)
        links = pg.evaluate("Array.from(document.querySelectorAll('#listaMovimentos a.cx-origem-link, .main a.cx-origem-link')).map(a => [a.textContent, a.getAttribute('href').split('/').pop()])")
        ok(sorted(links) == [['CP 1', PAGAR_D + '?id=1'], ['CP 2', PAGAR_D + '?id=2']], 'na conta do banco, as duas origens sao link para a pagina da conta a pagar: %s' % links)
        pg.evaluate("document.querySelector('a.cx-origem-link').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(PAGAR_D in pg.url and 'caixa-lancamento' not in pg.url, '  e clicar na origem abre a conta, e nao o lancamento')
        # uma baixa feita agora aparece no extrato com a origem ja ligada
        ir(RECEBER); tudo()
        alvo = pg.evaluate("TITULOS.filter(t => !t.cancelado && t.recebido === 0 && !t.grupo)[0].id")
        linha(alvo)
        pg.evaluate("document.getElementById('btnBaixarDaConta').click()"); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('btnConfirmarRecebimento').click()"); pg.wait_for_timeout(300)
        pg.evaluate("(() => { const m = document.getElementById('confirmModal'); if (m && m.classList.contains('open')) { const s = document.getElementById('inputSenhaModal'); if (s && s.offsetParent) s.value = 'senha-de-teste'; document.getElementById('btnConfirmModalConfirmar').click(); } })()")
        pg.wait_for_timeout(450)
        ok(pg.evaluate("(id) => saldoDe(titDe(id)) === 0", alvo), 'recebendo uma conta pelo painel, ela fica quitada')
        ir(CAIXA)
        novo = pg.evaluate("MOVIMENTOS.filter(m => m.origem === 'CR %d').map(m => m.contaId)" % alvo)
        ok(len(novo) == 1, '  e o recebimento chega ao Caixa com a origem "CR %d"' % alvo)
        if novo:
            pg.evaluate("(c) => { contaAtualId = c; periodoAtual = 'todos'; itensPorPaginaAtual = 100; render(); }", novo[0]); pg.wait_for_timeout(300)
            href = pg.evaluate("(t) => { const a = Array.from(document.querySelectorAll('a.cx-origem-link')).filter(x => x.textContent === t)[0]; return a ? a.getAttribute('href').split('/').pop() : ''; }", 'CR %d' % alvo)
            ok(href == RECEBER_D + '?id=%d' % alvo, '  como link para a pagina da conta a receber: %s' % href)
        ok(pg.evaluate("origemHtml('Transferência')") == '<span class="cx-origem">Transferência</span>' and 'cf-vazio' in pg.evaluate("origemHtml(null)"),
           'transferencia e lancamento a mao continuam sem link: nao ha documento para abrir')
        pg.evaluate("localStorage.removeItem('deskCaixaExtras')")

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
