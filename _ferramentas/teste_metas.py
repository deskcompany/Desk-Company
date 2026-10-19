# Metas e Performance de Vendas — 09/out/2026.
#
# As duas telas foram refeitas no padrao do sistema. A de Metas era um
# formulario de digitacao (uma linha por loja com um campo "Meta R$"), sem
# realizado, sem atingimento e sem mostrar o que ja estava cadastrado. A de
# Performance guardava uma COPIA propria dos numeros de meta, e a copia ja
# divergia: Desk Brands tinha 28.000 em setembro numa tela e 25.000 na outra.
#
# Divisao entre as duas, para nao virarem a mesma tela:
#   Metas       responde "vamos bater?"   -> meta, realizado, ritmo. ESCREVE.
#   Performance responde "como vendemos?" -> vendas, ticket, devolucao. SO LE.
#
# O que a suite guarda:
#   [1]  a tela de Metas e listagem: KPIs, tabela que cabe no card, duas abas;
#   [2]  o RITMO e em dias corridos, e a situacao sai dele — nao e opiniao;
#   [3]  loja e vendedor sao INDEPENDENTES, e a tela diz quando nao fecham;
#   [4]  a listagem SO LE: nenhum campo de digitacao fora do painel;
#   [5]  o painel de escrita mostra a PREVIA do que vai gravar, com o valor
#        antigo de cada mes — sobrescrever calado era o que a tela fazia;
#   [6]  os quatro modos gravam os meses certos, e o progressivo mostra os 12;
#   [7]  mexer em mes FECHADO e outro ato, com chave propria e senha;
#   [8]  salvar grava e a listagem reflete na hora;
#   [9]  a Performance le a MESMA base — a asserção que impede a copia de
#        voltar a divergir;
#   [10] as tres visoes trocam as colunas e a Performance nao escreve nada;
#   [11] Esc fecha os paineis, nos dois temas, sem erro de JS.
from playwright.sync_api import sync_playwright
import os, sys, glob

import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

URL = 'http://localhost:3000/'
METAS = 'pagina-vendas-metas.html'
PERF = 'pagina-vendas-performance-vendas.html'

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
    clic(pg, '#' + raiz + ' .dropdown-select-btn')
    pg.wait_for_timeout(200)
    clic(pg, '#' + raiz + ' .dropdown-select-item[data-value="' + str(valor) + '"]')
    pg.wait_for_timeout(300)


def confirmar(pg):
    if pg.locator('#confirmModal.open').count():
        if pg.locator('#campoSenhaModal').count() and pg.locator('#campoSenhaModal').is_visible():
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(500)
    # o aviso de "gravado" abre em seguida, no mesmo modal
    if pg.locator('#confirmModal.open').count():
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(400)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 950})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(localiza.http(METAS))
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(800)

    print('\n[1] Metas e listagem, no padrao do sistema')
    ok(pg.locator('.kpi-card').count() == 6, 'seis indicadores no topo: meta, realizado, atingimento, vendas, ticket e devolucao')
    ok(pg.locator('#corpoTabela tr').count() == pg.evaluate('LOJAS.length'),
       'uma linha por loja (%d)' % pg.locator('#corpoTabela tr').count())
    larg = pg.evaluate("document.querySelector('.estoque-table').getBoundingClientRect().width")
    wrap = pg.evaluate("document.querySelector('.estoque-table-wrap').getBoundingClientRect().width")
    ok(larg <= wrap + 1, 'a tabela cabe no card a 1440px (%d em %d)' % (larg, wrap))
    ok(not pg.evaluate('document.documentElement.scrollWidth > window.innerWidth'),
       'e a pagina nao rola na horizontal')
    ok(pg.locator('#abasNivel .aba-sit').count() == 2, 'duas abas: lojas e vendedores')

    print('\n[2] O ritmo e em DIAS CORRIDOS, e a situacao sai dele')
    # Meta de 31.000 num mes de 31 dias pede 1.000 por dia: no dia 8, 8.000.
    esp = pg.evaluate('ritmoDe(31000, MES_HOJE, ANO_HOJE).esperado')
    dias = pg.evaluate('diasNoMes(MES_HOJE, ANO_HOJE)')
    hoje = pg.evaluate('DIA_HOJE')
    ok(abs(esp - 31000.0 * hoje / dias) < 0.01,
       'esperado = meta x dia de hoje / dias do mes (%.2f)' % esp)
    ok(pg.evaluate("situacaoDaMeta(1000, 1000, MES_HOJE, ANO_HOJE)") == 'batida', 'realizado >= meta e batida')
    ok(pg.evaluate("situacaoDaMeta(31000, 1, MES_HOJE, ANO_HOJE)") == 'abaixo', 'atras do esperado e abaixo do ritmo')
    ok(pg.evaluate("situacaoDaMeta(31000, 30000, MES_HOJE, ANO_HOJE)") == 'noritmo', 'a frente do esperado e no ritmo')
    ok(pg.evaluate("situacaoDaMeta(1000, 900, MES_HOJE - 1, ANO_HOJE)") == 'naobatida',
       'mes FECHADO abaixo da meta nao e "abaixo do ritmo": e nao bateu')
    ok(pg.evaluate("situacaoDaMeta(1000, 0, 12, ANO_HOJE)") == 'futuro', 'mes que nao comecou nao e atraso')
    ok(pg.evaluate("situacaoDaMeta(null, 500, MES_HOJE, ANO_HOJE)") == 'semmeta', 'sem meta nao ha o que medir')
    # A tabela usa a mesma regra que a funcao: nenhum selo e escrito a mao.
    coerente = pg.evaluate("""linhasDoNivel('loja').every(function (l) {
      return l.sit === situacaoDaMeta(l.meta, l.real, mesSel, anoSel);
    })""")
    ok(coerente, 'e todo selo da listagem vem dessa regra')

    print('\n[3] Loja e vendedor sao independentes, e a tela avisa a diferenca')
    d = pg.evaluate("diferencaDaLoja(LOJAS[0], MES_HOJE, ANO_HOJE)")
    ok(d['metaLoja'] != d['soma'], 'no exemplo, a soma dos vendedores nao fecha com a loja (%s x %s)' % (d['soma'], d['metaLoja']))
    ok(pg.evaluate('LOJAS[0].nome') in pg.inner_text('#avisoMetasTexto'),
       'e o aviso nomeia a loja em que nao fecha')
    autonomo = pg.evaluate("VENDEDORES.filter(v => v.ativo && v.lojaId === null).length")
    ok(autonomo >= 1 and 'autônomo' in pg.inner_text('#avisoMetasTexto'),
       'vendedor autonomo tem meta propria e fica fora da soma')
    clic(pg, '#abasNivel [data-nivel="vendedor"]')
    pg.wait_for_timeout(350)
    ok(pg.locator('#corpoTabela tr').count() == pg.evaluate("VENDEDORES.filter(v => v.ativo).length"),
       'a aba de vendedores lista so os ativos')
    # inner_text devolve o texto ja transformado pelo CSS (caixa alta).
    ok('VENDEDOR' in pg.inner_text('#thNome').upper(), 'e o cabecalho acompanha a aba')
    clic(pg, '#abasNivel [data-nivel="loja"]')
    pg.wait_for_timeout(300)

    print('\n[4] A listagem SO LE')
    ok(pg.locator('.main .estoque-table input').count() == 0, 'nenhum campo de digitacao na tabela')
    ok(pg.locator('#defDrawer.open').count() == 0, 'e o painel de escrita nasce fechado')
    # Design system 9.3: dropdown de painel nasce com a TELA.
    ok(pg.locator('#menuDefAlvo .dropdown-select-item').count() > 0,
       'os menus do painel ja existem antes de ele abrir')

    print('\n[5] O painel mostra a PREVIA, com o que ja existia em cada mes')
    clic(pg, '#corpoTabela tr')
    pg.wait_for_timeout(450)
    ok(pg.locator('#eventDrawer.open').count() == 1, 'clicar na linha abre a leitura')
    ok(pg.locator('#drawerCorpo .meta-ano tbody tr').count() == 12, 'com os doze meses do ano')
    clic(pg, '#btnDefinirDaqui')
    pg.wait_for_timeout(450)
    ok(pg.locator('#defDrawer.open').count() == 1 and pg.locator('#eventDrawer.open').count() == 0,
       'definir meta troca a leitura pela escrita')
    ok('Loja' in pg.inner_text('#defAlvo .dropdown-select-label'), 'ja apontando para a loja clicada')
    ok('Informe o valor' in pg.inner_text('#defPrevia'), 'sem valor, a previa pede o valor em vez de mostrar zero')
    pg.fill('#defValor', '50000')
    pg.wait_for_timeout(300)
    ok(pg.locator('#defPrevia .meta-previa-linha').count() == 1, 'modo de um mes grava um mes')
    ok('substitui' in pg.inner_text('#defPrevia'), 'e a previa diz o valor que vai ser substituido')

    print('\n[6] Os quatro modos gravam os meses certos')
    escolher(pg, 'defModo', 'trimestral')
    ok(pg.locator('#defPrevia .meta-previa-linha').count() == 3, 'trimestre grava tres meses')
    ok(pg.evaluate("mesesAGravar().every(x => Math.abs(x.valor - 50000 / 3) < 0.01)"),
       'dividindo o total igualmente')
    escolher(pg, 'defModo', 'anual')
    ok(pg.locator('#defPrevia .meta-previa-linha').count() == 12, 'ano grava doze meses')
    escolher(pg, 'defModo', 'progressivo')
    ok(pg.locator('#campoDefPct').is_visible(), 'o progressivo pede o percentual')
    ok(pg.locator('#defPrevia .meta-previa-linha').count() == 0, 'e sem percentual nao inventa previa')
    pg.fill('#defPct', '10')
    pg.wait_for_timeout(300)
    lista = pg.evaluate('mesesAGravar()')
    ok(len(lista) == 12, 'com percentual, mostra os doze meses que vai gravar')
    ok(abs(lista[1]['valor'] - 55000) < 0.01, 'o segundo mes cresce 10%% sobre o primeiro (%.2f)' % lista[1]['valor'])
    ok(lista[-1]['ano'] == lista[0]['ano'] + 1, 'e a sequencia vira o ano')

    print('\n[7] Mexer em mes FECHADO e outro ato')
    escolher(pg, 'defModo', 'mensal')
    escolher(pg, 'defMes', 9)
    pg.wait_for_timeout(200)
    ok('fechado' in pg.inner_text('#defPrevia'), 'a previa marca o mes como fechado')
    acao = pg.evaluate("""(function () {
      return ACOES_ESPECIFICAS.filter(a => a.chave === 'metasAlteraFechado')[0];
    })()""")
    ok(acao and acao.get('exigePadrao') is True, 'alterar mes fechado nasce exigindo senha')
    normal = pg.evaluate("ACOES_ESPECIFICAS.filter(a => a.chave === 'metasDefine')[0].exigePadrao")
    ok(normal is False, 'definir meta de mes aberto e rotina, sem senha')
    # A loja em jogo e a da LINHA clicada (a tabela abre em ordem alfabetica),
    # nao a primeira do cadastro.
    alvo = pg.evaluate("Number(valDrop('defAlvo').split(':')[1])")
    antes = pg.evaluate("metaDe('loja', %d, 9, ANO_HOJE)" % alvo)
    clic(pg, '#defSalvar')
    pg.wait_for_timeout(500)
    ok(pg.locator('#confirmModal.open').count() == 1, 'salvar mes fechado para no modal')
    ok('já aconteceu' in pg.inner_text('#confirmModalTexto'), 'dizendo o que esta em jogo')
    ok(pg.evaluate("metaDe('loja', %d, 9, ANO_HOJE)" % alvo) == antes, 'e nada e gravado antes de confirmar')
    clic(pg, '#btnConfirmModalCancelar')
    pg.wait_for_timeout(300)

    print('\n[8] Salvar grava, e a listagem reflete na hora')
    escolher(pg, 'defMes', pg.evaluate('MES_HOJE'))
    pg.fill('#defValor', '60000')
    pg.wait_for_timeout(250)
    clic(pg, '#defSalvar')
    pg.wait_for_timeout(500)
    confirmar(pg)
    ok(pg.evaluate("metaDe('loja', %d, MES_HOJE, ANO_HOJE)" % alvo) == 60000, 'a meta nova foi gravada')
    ok(pg.locator('#defDrawer.open').count() == 0, 'o painel fecha')
    ok('60.000,00' in pg.inner_text('#corpoTabela'), 'e a linha da tabela mostra o valor novo')
    # Campo obrigatorio vazio nao grava nada.
    clic(pg, '#btnDefinirMeta')
    pg.wait_for_timeout(400)
    n_antes = pg.evaluate('METAS.length')
    clic(pg, '#defSalvar')
    pg.wait_for_timeout(350)
    ok(pg.locator('#campoAlvo.has-error').count() == 1, 'sem escolher para quem, o campo e marcado')
    ok(pg.evaluate('METAS.length') == n_antes, 'e nada e gravado')
    clic(pg, '#defCancelar')
    pg.wait_for_timeout(300)

    print('\n[9] A venda entra na MESMA lista (10/out/2026)')
    # O usuario recusou duas telas para o mesmo assunto, e tambem o seletor que trocava de uma para
    # a outra: quer uma lista so. O que Performance de Vendas media (numero de vendas, ticket,
    # devolucao, comparacao) mora agora na lista e no painel de Metas e Performance.
    pg.goto(localiza.http(METAS))
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(700)
    ok(PERF not in localiza.nomes(), 'a tela de Performance de Vendas deixou de existir')
    citam = [n for n in localiza.nomes() if PERF in open(localiza.onde(n), encoding='utf-8').read()]
    ok(not citam, 'e nenhuma tela aponta mais para ela: %s' % citam[:3])
    ok(pg.locator('#visaoModulo').count() == 0 and pg.locator('#filtroVisao').count() == 0, 'nao ha seletor de visao: a pagina mostra uma coisa so')
    cab = [c.replace('▲', '').strip().upper() for c in pg.evaluate("Array.from(document.querySelectorAll('.estoque-table th')).map(t => t.textContent)")]
    ok(cab == ['LOJA', 'META', 'REALIZADO', 'ATINGIMENTO', 'RITMO ATÉ HOJE', 'VENDAS', 'DEVOLUÇÃO', 'SITUAÇÃO'], 'as colunas das duas telas numa lista: %s' % cab)

    print('\n[10] Os numeros da venda saem da mesma base da meta')
    linhas = pg.evaluate("linhasDoNivel('loja').map(l => [l.id, l.real, l.vendas, l.ticket, l.devolvido, l.taxaDev])")
    certo = pg.evaluate("""linhasDoNivel('loja').every(function (l) {
      return l.real === realizadoDe('loja', l.id, mesSel, anoSel) && l.vendas === numeroDeVendas('loja', l.id, mesSel, anoSel) &&
             l.devolvido === devolvidoDe('loja', l.id, mesSel, anoSel) && (!l.vendas || Math.abs(l.ticket - l.real / l.vendas) < 0.001);
    })""")
    ok(certo and len(linhas) == 3, 'vendas, ticket e devolucao de cada loja saem do realizado do mes: %s' % linhas[0])
    soma_v = sum(l[2] for l in linhas); soma_r = sum(l[1] for l in linhas); soma_d = sum(l[4] for l in linhas)
    ok(pg.inner_text('#kpiNumero') == str(soma_v), 'o indicador de numero de vendas e a soma da lista (%d)' % soma_v)
    ok(pg.inner_text('#kpiTicket') == pg.evaluate("moeda(%r / %d)" % (soma_r, soma_v)), 'o ticket medio e o realizado dividido pelas vendas: %s' % pg.inner_text('#kpiTicket'))
    ok(pg.inner_text('#kpiDevolucao') == pg.evaluate("pct(%r / %r * 100)" % (soma_d, soma_r)), 'e a devolucao e o devolvido sobre o vendido: %s' % pg.inner_text('#kpiDevolucao'))
    linha1 = pg.evaluate("document.querySelector('#corpoTabela tr').innerText")
    ok('ticket R$' in linha1 and '%' in linha1, 'a linha mostra as vendas com o ticket e a taxa de devolucao')
    atras = pg.evaluate("linhasDoNivel('loja').filter(l => l.sit === 'abaixo' || l.sit === 'naobatida').map(l => l.nome)")
    ok(len(atras) >= 1 and all(n in pg.inner_text('#avisoMetasTexto') for n in atras) and 'Atrás da meta (%d)' % len(atras) in pg.inner_text('#avisoMetasTexto'),
       'o aviso abre dizendo quem esta atras da meta: %s' % atras)
    larg2 = pg.evaluate("document.querySelector('.estoque-table').getBoundingClientRect().width")
    wrap2 = pg.evaluate("document.querySelector('.estoque-table-wrap').getBoundingClientRect().width")
    ok(larg2 <= wrap2 + 1, 'com as colunas novas a tabela continua cabendo no card (%d em %d)' % (larg2, wrap2))
    estouram = pg.evaluate("Array.from(document.querySelectorAll('.mp-kpis .kpi-card')).filter(k => k.querySelector('.kpi-value').scrollWidth > k.clientWidth).length")
    ok(estouram == 0, 'e nenhum dos seis indicadores estoura o proprio quadro')
    com_meta = pg.evaluate("linhasDoNivel('loja').filter(l => l.meta !== null)[0].id")
    sem_meta = pg.evaluate("(linhasDoNivel('loja').filter(l => l.meta === null)[0] || {}).id || 0")
    pg.evaluate("abrirPainel('loja', %d)" % com_meta); pg.wait_for_timeout(350)
    painel = pg.inner_text('#drawerCorpo').upper()
    ok('COMO VENDEU' in painel and 'TICKET MÉDIO' in painel and 'COMPARADO COM' in painel and 'MÊS ANTERIOR' in painel, 'o painel da loja traz a meta, como vendeu e a comparacao')
    ok(pg.inner_text('#btnDefinirDaqui') == 'Editar meta', 'loja com meta no mes: o botao do painel e "Editar meta"')
    ok(pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo .meta-ano th')).map(t => t.textContent)") == ['Mês', 'Meta', 'Realizado', '%', 'Vendas'], 'e a tabela do ano ganhou a coluna de vendas')
    pg.evaluate("fecharDrawer()"); pg.wait_for_timeout(200)
    if sem_meta:
        pg.evaluate("abrirPainel('loja', %d)" % sem_meta); pg.wait_for_timeout(350)
        ok(pg.inner_text('#btnDefinirDaqui') == 'Definir meta', 'loja sem meta no mes: o botao e "Definir meta"')
        clic(pg, '#btnDefinirDaqui'); pg.wait_for_timeout(400)
        ok(pg.locator('#defDrawer.open').count() == 1 and pg.evaluate("valDrop('defAlvo')") == 'loja:%d' % sem_meta, 'e abre o painel de definir ja naquela loja')
        clic(pg, '#defCancelar'); pg.wait_for_timeout(250)
    else:
        ok(False, 'o exemplo deveria ter uma loja sem meta no mes corrente')

    print('\n[11] Esc, os dois temas e o console')
    clic(pg, '#corpoTabela tr')
    pg.wait_for_timeout(400)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(350)
    ok(pg.locator('#eventDrawer.open').count() == 0, 'Esc fecha o painel de leitura')
    clic(pg, '#btnDefinirMeta')
    pg.wait_for_timeout(400)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(350)
    ok(pg.locator('#defDrawer.open').count() == 0, 'e o de escrita')
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(220)
        ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440, 'tema %s: nao estoura em 1440' % tema)
    ok(not erros, 'Metas sem erro de JS: %s' % erros[:2])

    print(chr(10) + '[12] Link com ?definir= abre o painel de escrita no alvo')
    p3 = nav.new_page(viewport={'width': 1440, 'height': 950})
    e3 = []
    p3.on('pageerror', lambda e: e3.append(str(e)))
    p3.goto(localiza.http(METAS + '?definir=vendedor:5&mes=3&ano=2026'))
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(800)
    ok(p3.evaluate("document.querySelector('#abasNivel .aba-sit.active').getAttribute('data-nivel')") == 'vendedor',
       'link de vendedor abre na aba de vendedores')
    ok(p3.evaluate('mesSel') == 3 and 'Mar' in p3.inner_text('#defMes .dropdown-select-label'),
       'e no mes que o link pediu, na tela e no painel')
    p3.goto(localiza.http(METAS + '?definir=loja:999'))
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(800)
    ok(p3.locator('#defDrawer.open').count() == 0 and p3.locator('#confirmModal.open').count() == 1,
       'alvo que nao existe avisa em vez de abrir painel vazio')
    ok(not e3, 'sem erro de JS no caminho: %s' % e3[:2])

    print('\n[12] Um modulo so: Metas e Performance (10/out/2026)')
    # Pedido do usuario: as duas telas sao o mesmo assunto. Um item de menu, um titulo e uma pagina.
    fontes = {n: open(localiza.onde(n), encoding='utf-8').read() for n in localiza.nomes()}
    com_menu = [n for n in fontes if 'id="flyout-vendas"' in fontes[n]]
    ruim = [n for n in com_menu if fontes[n].count('class="flyout-item" data-label="Metas e Performance" data-href="../vendas/pagina-vendas-metas.html"') < 1
            or 'data-label="Performance de Vendas"' in fontes[n] or 'class="flyout-item" data-label="Metas" ' in fontes[n]]
    ok(len(com_menu) >= 80 and not ruim, 'o menu de toda tela tem um item so, "Metas e Performance": %d telas, fora do padrao %s' % (len(com_menu), ruim[:3]))
    p4 = nav.new_page(viewport={'width': 1440, 'height': 950})
    e4 = []
    p4.on('pageerror', lambda e: e4.append(str(e)))
    p4.goto(localiza.http(METAS)); p4.wait_for_load_state('load'); p4.wait_for_timeout(600)
    ok(p4.inner_text('.main h1') == 'Metas e Performance' and 'Metas e Performance' in p4.inner_text('#breadcrumb') and
       p4.evaluate("(document.querySelector('.nav-item.active') || { getAttribute: () => '' }).getAttribute('data-label')") == 'Vendas',
       'a pagina abre com o titulo do modulo e o caminho de Vendas')
    ok(p4.locator('#menuMaisAcoes [data-acao="performance"]').count() == 0, 'e o menu nao tem mais "Abrir Performance de Vendas"')
    # Os quadros do Dashboard que levavam a Performance levam a pagina unica.
    p4.goto(localiza.http('pagina-dashboard-kpis.html')); p4.wait_for_load_state('load'); p4.wait_for_timeout(500)
    destinos = p4.evaluate("Array.from(document.querySelectorAll('.main [data-href]')).map(q => q.getAttribute('data-href').split('/').pop())")
    ok(METAS in destinos and PERF not in destinos, 'os quadros do Dashboard apontam para a pagina unica')
    ok(not e4, 'sem erro de JS: %s' % e4[:2])

    print('\n[13] A barra de paginacao padrao na lista (ajuste do teste, 19/out/2026)')
    p5 = nav.new_page(viewport={'width': 1440, 'height': 950})
    e5 = []
    p5.on('pageerror', lambda e: e5.append(str(e)))
    p5.goto(localiza.http(METAS)); p5.wait_for_load_state('load'); p5.wait_for_timeout(600)
    # Doze vendedores a mais, cada um com meta de R$ 1.000,00 no mes: a aba Vendedores passa a ter 16 linhas.
    p5.evaluate("""() => { for (let i = 1; i <= 12; i++) { VENDEDORES.push({ id: 100 + i, nome: 'Teste ' + String(i).padStart(2, '0'), lojaId: 1, ativo: true });
        METAS.push({ nivel: 'vendedor', id: 100 + i, mes: MES_HOJE, ano: ANO_HOJE, valor: 1000 }); } }""")
    pag = lambda: p5.evaluate("[document.getElementById('paginacaoResumo').textContent, document.getElementById('paginacaoPaginas').textContent, document.getElementById('btnPaginaAnterior').disabled, document.getElementById('btnPaginaProxima').disabled]")
    n_linhas = lambda: p5.evaluate("document.querySelectorAll('#corpoTabela tr').length")
    prox = lambda: (clic(p5, '#btnPaginaProxima'), p5.wait_for_timeout(150))
    por = lambda n: (clic(p5, '#itensPorPagina .dropdown-select-item[data-value="%s"]' % n), p5.wait_for_timeout(200))
    ok(p5.evaluate("!!document.querySelector('.paginacao-bar #itensPorPagina') && !!document.querySelector('.paginacao-bar .paginacao-nav')"), 'o rodape tem a barra de paginacao padrao')
    ok(p5.evaluate("[...document.querySelectorAll('#itensPorPagina .dropdown-select-item')].map(i => i.textContent)") == ['10', '25', '50', '100'], 'opcoes 10, 25, 50 e 100')
    p5.evaluate("render()")
    ok(n_linhas() == 3 and pag() == ['Mostrando 1–3 de 3 lojas', 'Página 1 de 1', True, True], 'a aba Lojas (3) cabe numa pagina so: %s' % pag())
    clic(p5, '#abasNivel .aba-sit[data-nivel="vendedor"]'); p5.wait_for_timeout(200)
    ok(n_linhas() == 10 and pag() == ['Mostrando 1–10 de 16 vendedores', 'Página 1 de 2', True, False], 'a aba Vendedores tem 16: a primeira pagina mostra 10: %s' % pag())
    total_meta = p5.evaluate("filtradas().reduce((s, l) => s + (l.meta || 0), 0)")
    da_pagina = p5.evaluate("filtradas().slice(0, 10).reduce((s, l) => s + (l.meta || 0), 0)")
    ok(total_meta > da_pagina and p5.evaluate("document.getElementById('somaFiltro').textContent") == p5.evaluate("moeda(%s)" % total_meta) and p5.evaluate("document.getElementById('contagemLinhas').textContent") == '16 vendedores',
       'a contagem (16) e a "Meta do filtro" somam o filtro inteiro (%s), nao so a pagina (%s)' % (total_meta, da_pagina))
    prox()
    ok(n_linhas() == 6 and pag() == ['Mostrando 11–16 de 16 vendedores', 'Página 2 de 2', False, True] and p5.evaluate("document.getElementById('somaFiltro').textContent") == p5.evaluate("moeda(%s)" % total_meta),
       'a segunda pagina tem as 6 que sobram, e a meta do filtro nao muda: %s' % pag())
    clic(p5, '#abasNivel .aba-sit[data-nivel="loja"]'); p5.wait_for_timeout(150)
    clic(p5, '#abasNivel .aba-sit[data-nivel="vendedor"]'); p5.wait_for_timeout(150)
    ok(pag()[1] == 'Página 1 de 2', 'trocar de aba (Lojas, Vendedores) volta a pagina 1')
    prox(); p5.fill('#campoBusca', 'teste'); p5.wait_for_timeout(150)
    ok(pag() == ['Mostrando 1–10 de 12 vendedores', 'Página 1 de 2', True, False], 'a busca volta a pagina 1 e conta so os 12 "Teste": %s' % pag())
    prox(); p5.fill('#campoBusca', 'teste 1'); p5.wait_for_timeout(150)
    ok(pag() == ['Mostrando 1–3 de 3 vendedores', 'Página 1 de 1', True, True], 'busca "teste 1" deixa Teste 10, 11 e 12: %s' % pag())
    p5.fill('#campoBusca', ''); p5.wait_for_timeout(150); prox()
    p5.evaluate("document.querySelector('#menuFiltroSituacao .dropdown-select-item[data-value=\"todas\"]').click()"); p5.wait_for_timeout(150)
    ok(pag()[1] == 'Página 1 de 2', 'o filtro de situacao volta a pagina 1')
    prox(); p5.evaluate("document.querySelector('#menuFiltroMes .dropdown-select-item[data-value=\"9\"]').click()"); p5.wait_for_timeout(200)
    ok(pag()[1].startswith('Página 1 de '), 'trocar o mes volta a pagina 1')
    p5.evaluate("document.querySelector('#menuFiltroMes .dropdown-select-item[data-value=\"' + MES_HOJE + '\"]').click()"); p5.wait_for_timeout(200); prox()
    clic(p5, '.estoque-table th.ordenavel[data-ordem="meta"]'); p5.wait_for_timeout(150)
    ok(pag()[1] == 'Página 1 de 2', 'ordenar por uma coluna volta a pagina 1')
    por(25); ok(n_linhas() == 16 and pag() == ['Mostrando 1–16 de 16 vendedores', 'Página 1 de 1', True, True], 'com 25 por pagina, as 16 numa so')
    por(10)
    # impressao e planilha levam todas as linhas e devolvem a pagina como estava
    p5.evaluate("window.print = () => { window.dispatchEvent(new Event('beforeprint')); window.__imp = { linhas: document.querySelectorAll('#corpoTabela tr').length, cab: document.getElementById('relatorioCabecalho').innerText }; window.dispatchEvent(new Event('afterprint')); }")
    prox(); antes = pag()
    p5.evaluate("imprimirTela()")
    imp = p5.evaluate("window.__imp")
    ok(bool(imp) and imp['linhas'] == 16 and '16 registros' in imp['cab'], 'imprimir leva as 16 linhas: %s' % str(imp and imp['linhas']))
    ok(pag() == antes and n_linhas() == 6, 'e a lista volta a pagina em que estava')
    dados = p5.evaluate("(() => { let d; comListaInteira(() => { d = tabelaDaTela(); }); return d; })()")
    ok(len(dados['linhas']) == 16 and pag() == antes, 'a planilha le as 16 linhas, e a pagina volta')
    p5.fill('#campoBusca', 'zzz'); p5.wait_for_timeout(150)
    ok(pag() == ['Mostrando 0 de 0', 'Página 1 de 1', True, True], 'sem resultado, "Mostrando 0 de 0" e os dois botoes desligados')
    ok(not e5, 'sem erro de JS: %s' % e5[:2])
    p5.close()

    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
