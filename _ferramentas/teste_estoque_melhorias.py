# -*- coding: utf-8 -*-
# Estoque: os itens E2, E8 e E10 da lista de melhorias (12/out/2026).
#
#   [1] E2   indicadores em Ordens de Compra: valor em aberto, a receber em 7 dias, atrasadas e sem
#            data prevista. Cada um soma o que diz somar, e clicar faz a lista mostrar exatamente
#            aquelas ordens; clicar de novo desfaz, e mexer num filtro a mao apaga o indicador;
#   [2] E8   clicar na linha da Transferencia Entre Estoques abre o painel da transferencia: itens,
#            enviado e recebido, quem enviou, quem recebeu e o tempo em transito. Dali se confirma o
#            recebimento, e quem confirmou fica no painel;
#   [3] E10  em Itens Bloqueados, "De onde veio" leva ao documento: a nota em Entrada de Notas e a
#            ficha do pedido na Separacao e na Conferencia de Saida. O destino tem o registro.
from playwright.sync_api import sync_playwright
import datetime, os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

OC, TRANSF, BLOQ = 'pagina-estoque-ordens-compra.html', 'pagina-estoque-transferencia.html', 'pagina-estoque-itens-bloqueados.html'
NOTAS, SEP, CONF = 'pagina-estoque-entrada-notas.html', 'pagina-logistica-separacao-detalhe.html', 'pagina-logistica-conferencia-saida-detalhe.html'
GUARDADO = ['deskOrdensGeradas', 'deskBloqueados', 'deskBloqueiosEntrada', 'deskSeparacao', 'deskLog']
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
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def do_zero(tela):
        ir(tela)
        pg.evaluate("(chaves) => chaves.forEach(k => localStorage.removeItem(k))", GUARDADO)
        ir(tela)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def aberto(sel):
        return pg.evaluate("(s) => document.querySelector(s).classList.contains('open')", sel)

    if secao(1, 'E2: os indicadores de Ordens de Compra somam o que dizem, e clicar filtra a lista'):
        do_zero(OC)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        # A conta refeita a parte, com a data de "hoje" da propria tela.
        contas = pg.evaluate("""(() => { const dias = (s) => Math.round((new Date(s + 'T12:00:00') - HOJE) / 86400000);
            const vivas = ORDENS.filter(o => o.situacao !== 'atendida' && o.situacao !== 'cancelada');
            const grupos = { aberto: vivas, semana: vivas.filter(o => o.previsto && dias(o.previsto) >= 0 && dias(o.previsto) <= 7),
                             atrasadas: vivas.filter(o => o.previsto && dias(o.previsto) < 0), semdata: vivas.filter(o => !o.previsto) };
            return Object.fromEntries(Object.keys(grupos).map(k => [k, { valor: fmtMoeda(grupos[k].reduce((s, o) => s + o.total, 0)), ids: grupos[k].map(o => o.id).sort((a, b) => a - b) }])); })()""")

        def cartoes():
            return pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.oc-kpis .kpi-card')).map(c => [c.getAttribute('data-kpi'), [c.querySelector('.kpi-value').textContent, c.querySelector('.kpi-delta').textContent, c.classList.contains('on'), c.getAttribute('aria-pressed')]]))")

        def na_lista():
            return sorted(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela .item-checkbox')).map(c => Number(c.getAttribute('data-id')))"))

        visto = cartoes()
        ok({k: v[0] for k, v in visto.items()} == {k: v['valor'] for k, v in contas.items()} and all(len(v['ids']) >= 1 for v in contas.values()),
           'os quatro indicadores somam as ordens deles, contadas a parte, e nenhum esta vazio: %s' % {k: v[0] for k, v in visto.items()})
        ok(all(visto[k][1].startswith(str(len(contas[k]['ids'])) + ' orde') for k in contas), 'e dizem quantas ordens sao: %s' % {k: v[1] for k, v in visto.items()})
        ok(contas['atrasadas']['ids'] == [6] and contas['semdata']['ids'] == [5], 'no exemplo, a atrasada e a ordem 6 e a sem data e a ordem 5')
        ok(len(contas['aberto']['ids']) == len(contas['semana']['ids']) + len(contas['atrasadas']['ids']) + len(contas['semdata']['ids']) + pg.evaluate("ORDENS.filter(o => (o.situacao === 'aberto' || o.situacao === 'andamento') && o.previsto && Math.round((new Date(o.previsto + 'T12:00:00') - HOJE) / 86400000) > 7).length"),
           'toda ordem em aberto cai em uma faixa so: nesta semana, atrasada, sem data ou mais adiante')
        todas = pg.evaluate("ORDENS.length")
        for k in ['aberto', 'semana', 'atrasadas', 'semdata']:
            clic('.oc-kpis [data-kpi="%s"]' % k); pg.wait_for_timeout(250)
            c = cartoes()
            ok(na_lista() == contas[k]['ids'], 'clicar em "%s" deixa na lista exatamente as ordens dele: %s' % (k, na_lista()))
            ok(c[k][2] and c[k][3] == 'true' and sum(1 for v in c.values() if v[2]) == 1, '  e so ele fica aceso')
            ok(pg.inner_text('#valorTotalOrdens') == contas[k]['valor'], '  e o total do rodape e o valor do indicador: %s' % pg.inner_text('#valorTotalOrdens'))
        clic('.oc-kpis [data-kpi="semdata"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.querySelector('.sit-contador[data-cont=\"todos\"]').textContent") == str(todas) and not any(v[2] for v in cartoes().values()),
           'clicar de novo desfaz: a lista volta a ter as %d ordens e nenhum indicador fica aceso' % todas)
        clic('.oc-kpis [data-kpi="atrasadas"]'); pg.wait_for_timeout(200)
        clic('#abasSituacao .aba-sit[data-sit="atendida"]'); pg.wait_for_timeout(250)
        ok(not any(v[2] for v in cartoes().values()) and len(na_lista()) == pg.evaluate("ORDENS.filter(o => o.situacao === 'atendida').length"),
           'mexer na situacao a mao apaga o indicador, e a lista passa a ser a da aba')
        clic('.oc-kpis [data-kpi="aberto"]'); pg.wait_for_timeout(200)
        pg.fill('#campoBusca', 'TechParts'); pg.wait_for_timeout(250)
        ok(not any(v[2] for v in cartoes().values()) and len(na_lista()) == pg.evaluate("ORDENS.filter(o => o.fornecedor.indexOf('TechParts') >= 0).length"),
           'buscar a mao tambem apaga: a busca vale para todas as ordens do fornecedor, e nao so as em aberto')
        pg.keyboard.press('Tab')
        clic('.oc-kpis [data-kpi="aberto"]'); pg.wait_for_timeout(200)
        ok(pg.input_value('#campoBusca') == '' and na_lista() == contas['aberto']['ids'], 'e o indicador limpa a busca antes de filtrar')

    if secao(2, 'E8: a linha da Transferencia abre o painel, e dali se confirma o recebimento'):
        do_zero(TRANSF)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        hoje = datetime.date.today()
        dias = lambda n: '%d dia' % n + ('' if n == 1 else 's')

        def abrir(num):
            clic('#corpoTabela tr[data-num="%s"] td:nth-child(2)' % num); pg.wait_for_timeout(350)

        def painel():
            return pg.evaluate("""() => { const t = (id) => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
                return { sit: t('verSituacao'), origem: t('verOrigem'), destino: t('verDestino'), envio: t('verEnvio'), chegada: t('verChegada'), viagem: t('verViagem'),
                         itens: Array.from(document.querySelectorAll('#verItens .rep-origem')).map(e => e.textContent.replace(/\\s+/g, ' ').trim()),
                         receber: !!document.getElementById('btnReceberDoPainel') }; }""")

        abrir('TR-0101')
        a = painel()
        parado = (hoje - datetime.date(2026, 9, 12)).days
        ok(aberto('#verDrawer') and not aberto('#recDrawer'), 'clicar na linha abre o painel da transferencia, e nao o de recebimento')
        ok(a['sit'] == 'Em trânsito' and a['origem'] == 'Galpão Centro' and a['destino'] == 'Loja Física Aldeota', 'o painel diz a situacao, de onde saiu e para onde vai: %s' % [a['sit'], a['origem'], a['destino']])
        ok(a['envio'] == '12/09/2026 · Carlos Mendes' and a['chegada'] == 'ainda não chegou', 'quem enviou e quando, e que ainda nao chegou: %s / %s' % (a['envio'], a['chegada']))
        ok(a['viagem'] == 'há ' + dias(parado), 'o tempo em transito conta de quando saiu ate hoje: %s' % a['viagem'])
        ok(len(a['itens']) == 2 and 'Teclado Mecânico Desk' in a['itens'][0] and 'enviado 8' in a['itens'][0] and 'recebido 0' in a['itens'][0] and 'em trânsito 8 UN' in a['itens'][0]
           and 'enviado 12' in a['itens'][1], 'os itens vem com o enviado, o recebido e o que esta em transito: %s' % a['itens'][:1])
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ok(not aberto('#verDrawer'), 'ESC fecha o painel')

        abrir('TR-0100')
        b = painel()
        ok(b['sit'] == 'Recebida em parte' and b['chegada'] == 'em parte, em 11/09/2026 · Ana Souza' and 'com parte ainda a caminho' in b['viagem'] and b['receber'],
           'recebida em parte: quem recebeu, quando, e que parte ainda esta a caminho: %s / %s' % (b['chegada'], b['viagem']))
        ok('enviado 10' in b['itens'][0] and 'recebido 8' in b['itens'][0] and 'em trânsito 2 UN' in b['itens'][0], '  com o que falta chegar no item: %s' % b['itens'][0])
        clic('#btnFecharVer'); pg.wait_for_timeout(250)

        abrir('TR-0099')
        c = painel()
        ok(c['sit'] == 'Recebida' and c['chegada'] == '09/09/2026 · Carlos Mendes' and c['viagem'] == '1 dia' and not c['receber'] and 'em trânsito' not in c['itens'][0],
           'recebida por inteiro: quem recebeu, um dia de viagem, nada em transito e sem botao de receber: %s / %s' % (c['chegada'], c['viagem']))
        clic('#verDrawerClose'); pg.wait_for_timeout(250)

        clic('#corpoTabela tr[data-num="TR-0101"] [data-acao="receber"]'); pg.wait_for_timeout(350)
        ok(aberto('#recDrawer') and not aberto('#verDrawer'), 'o botao da linha continua abrindo so o recebimento, sem o painel por baixo')
        clic('#btnCancelarRec'); pg.wait_for_timeout(250)

        abrir('TR-0101')
        clic('#btnReceberDoPainel'); pg.wait_for_timeout(350)
        ok(aberto('#recDrawer') and not aberto('#verDrawer') and 'TR-0101' in pg.inner_text('#recResumo'), 'do painel se chega ao recebimento daquela transferencia')
        pg.fill('#inputSenha', 'senha'); clic('#btnConfirmarRec'); pg.wait_for_timeout(400)
        if pg.evaluate("document.getElementById('avisoModal').classList.contains('open')"):
            clic('#btnAvisoOk'); pg.wait_for_timeout(250)
        abrir('TR-0101')
        d = painel()
        ok(d['sit'] == 'Recebida' and d['chegada'] == hoje.strftime('%d/%m/%Y') + ' · Administrador Desk' and d['viagem'] == dias(parado) and not d['receber'],
           'confirmado o recebimento, o painel passa a dizer quem recebeu, hoje, e quanto durou a viagem: %s / %s' % (d['chegada'], d['viagem']))
        ok('recebido 8' in d['itens'][0] and 'em trânsito' not in d['itens'][0], '  e os itens aparecem recebidos: %s' % d['itens'][0])

    if secao(3, 'E10: em Itens Bloqueados, a origem leva ao documento, e o documento existe la'):
        do_zero(BLOQ)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])

        def origem(id_):
            clic('#corpoTabela tr[data-id="%d"]' % id_); pg.wait_for_timeout(380)
            r = pg.evaluate("""() => { const a = document.getElementById('linkOrigemBloqueio');
                const l = Array.from(document.querySelectorAll('.extrato-linha')).filter(e => e.offsetParent !== null && e.textContent.indexOf('De onde veio') === 0)[0];
                return { href: a ? a.getAttribute('href') : null, texto: a ? a.textContent : null, linha: l ? l.textContent.replace('De onde veio', '').trim() : null }; }""")
            pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
            return r

        esperado = {1: ('../estoque/' + NOTAS + '?busca=4468', 'Nota 4468'), 3: ('../estoque/' + NOTAS + '?busca=1182', 'Nota 1182'),
                    4: ('../estoque/' + NOTAS + '?busca=9051', 'Nota 9051'), 5: ('../logistica/' + SEP + '?id=23', 'Pedido #23')}
        vistos = {i: origem(i) for i in range(1, 8)}
        for i, (href, texto) in sorted(esperado.items()):
            ok(vistos[i]['href'] == href and vistos[i]['texto'] == texto, 'item %d: a origem e link para o documento: %s -> %s' % (i, vistos[i]['texto'], vistos[i]['href']))
        ok(vistos[2]['href'] is None and vistos[2]['linha'] == 'Acerto de estoque · AC-0041', 'acerto de estoque segue em texto, com o numero do acerto: %s' % vistos[2]['linha'])
        ok(vistos[6]['href'] is None and vistos[6]['linha'] == 'Bloqueio manual' and vistos[7]['href'] is None, 'bloqueio manual nao tem documento, e nao tem link')

        # O destino tem o registro (regra de 12/out: so liga onde o exemplo de la tem o documento).
        deposito = pg.evaluate("Object.fromEntries(ITENS.map(i => [i.id, DEPOSITOS[i.dep]]))")
        sku5 = pg.evaluate("ITENS.find(i => i.id === 5).sku")
        for i in (1, 3, 4):
            numero = esperado[i][1].split(' ')[1]
            ir(NOTAS, '?busca=' + numero)
            # A busca tambem olha outros campos da nota (a 2301 aparece junto da 1182): vale a linha cujo NUMERO e o pedido.
            linhas = pg.evaluate("(n) => Array.from(document.querySelectorAll('#corpoTabela tr')).filter(tr => tr.querySelector('.oc-numero').textContent === n).map(tr => tr.innerText.replace(/\\s+/g, ' '))", numero)
            ok(len(linhas) == 1 and deposito[str(i)] in linhas[0],'a Entrada de Notas tem a nota %s, e no mesmo deposito do bloqueio (%s)' % (numero, deposito[str(i)]))
        ir(SEP, '?id=23')
        ok(pg.evaluate("!PEDIDO_INEXISTENTE && PEDIDO.numero === 23 && PEDIDO.itens.some(i => i.sku === '%s')" % sku5), 'a Separacao tem o pedido 23, com o produto bloqueado entre os itens')

        # Bloqueio que chega da Conferencia de Saida, no formato que a bancada grava.
        ir(BLOQ)
        pg.evaluate("""() => localStorage.setItem('deskBloqueiosEntrada', JSON.stringify({ 'conf:24:KIT-COZ-006': { chave: 'conf:24:KIT-COZ-006', sku: 'KIT-COZ-006',
            produto: 'Kit utensílios de cozinha 6 peças', un: 'UN', dep: 2, endereco: null, tipoEnd: null, base: null, qtd: 1, motivo: 'falta', origem: 'conferencia_saida',
            doc: 'Pedido #24', quem: 'Ana Souza', obs: '' } }))""")
        ir(BLOQ)
        novo = pg.evaluate("(ITENS.find(i => i.sku === 'KIT-COZ-006') || {}).id")
        o = origem(novo) if novo else {'href': None, 'texto': None}
        ok(o['href'] == '../logistica/' + CONF + '?id=24' and o['texto'] == 'Pedido #24', 'a falta que veio da Conferencia de Saida leva a ficha do pedido na bancada: %s' % o['href'])
        ir(CONF, '?id=24')
        ok(pg.evaluate("!PEDIDO_INEXISTENTE && PEDIDO.numero === 24 && PEDIDO.itens.some(i => i.sku === 'KIT-COZ-006')"), 'e a Conferencia de Saida tem o pedido 24, com aquele produto')

        # O navegador de quem ja usava a tela guarda o exemplo ANTIGO (print do usuario, 12/out: o Kit
        # Home Office levou a uma lista vazia, buscando "951"). A suite comecava sempre do zero e nao via.
        do_zero(BLOQ)
        pg.evaluate("""() => { const e = semente(); e.itens.find(i => i.id === 1).doc = 'NF-e 12.951'; e.itens.find(i => i.id === 4).doc = 'NF-e 13.240';
            localStorage.setItem('deskBloqueados', JSON.stringify(e)); }""")
        ir(BLOQ)
        antigo1, antigo4 = origem(1), origem(4)
        ok(antigo1['href'] == esperado[1][0] and antigo1['texto'] == 'Nota 4468' and antigo4['href'] == esperado[4][0],
           'com o exemplo antigo guardado no navegador, a origem abre na nota certa: %s -> %s' % (antigo1['texto'], antigo1['href']))
        ir(NOTAS, '?' + antigo1['href'].split('?')[1])
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela .oc-numero')).some(e => e.textContent === '4468')") and 'não tem esse registro' not in pg.inner_text('#faixaBuscaLink'),
           '  e a Entrada de Notas abre com a nota 4468 na lista, sem o aviso de registro que nao existe')
        ir(BLOQ)
        pg.evaluate("""() => localStorage.setItem('deskBloqueiosEntrada', JSON.stringify({ 'x:1': { chave: 'x:1', sku: 'CAB-HDM-009', produto: 'Cabo HDMI 2.1 · 2m', un: 'UN', dep: 2,
            qtd: 1, motivo: 'avaria', origem: 'conferencia_entrada', doc: 'NF-e 55.123', quem: 'Carlos Mendes', obs: '' } }))""")
        ir(BLOQ)
        estranho = origem(pg.evaluate("ITENS.find(i => i.doc === 'NF-e 55.123').id"))
        ok(estranho['href'] is None and estranho['linha'] == 'Conferência de entrada · NF-e 55.123', 'documento escrito em outro formato fica em texto, em vez de virar link para um pedaco do numero: %s' % estranho['linha'])
        ir(BLOQ); pg.evaluate("(chaves) => chaves.forEach(k => localStorage.removeItem(k))", GUARDADO)

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
