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
    pg.goto(URL + METAS)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(800)

    print('\n[1] Metas e listagem, no padrao do sistema')
    ok(pg.locator('.kpi-card').count() == 4, 'quatro KPIs no topo')
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

    print('\n[9] A Performance le a MESMA base')
    # Esta e a asserção que impede a copia de voltar: as duas telas carregam o
    # mesmo bloco de dados, e aqui ele e comparado valor a valor.
    pg.goto(URL + METAS)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(700)
    base_metas = pg.evaluate("JSON.stringify([LOJAS, VENDEDORES, METAS, REALIZADO])")
    p2 = nav.new_page(viewport={'width': 1440, 'height': 950})
    err2 = []
    p2.on('pageerror', lambda e: err2.append(str(e)))
    p2.goto(URL + PERF)
    p2.wait_for_load_state('load')
    p2.wait_for_timeout(800)
    base_perf = p2.evaluate("JSON.stringify([LOJAS, VENDEDORES, METAS, REALIZADO])")
    ok(base_metas == base_perf, 'lojas, vendedores, metas e realizado sao identicos nas duas telas')
    ok(p2.evaluate("situacaoDaMeta.toString()") == pg.evaluate("situacaoDaMeta.toString()"),
       'e a regra de situacao e a mesma funcao, letra por letra')

    print('\n[10] Performance: tres visoes, e nenhuma escreve')
    ok(p2.locator('.kpi-card').count() == 4, 'quatro KPIs')
    cab = p2.inner_text('#cabecalhoPerf')
    ok('TICKET' in cab.upper(), 'a visao de resultado mostra ticket medio')
    escolher(p2, 'filtroVisao', 'devolucoes')
    ok('TAXA DE DEVOLU' in p2.inner_text('#cabecalhoPerf').upper(), 'a de devolucoes troca as colunas')
    escolher(p2, 'filtroVisao', 'comparativo')
    ok('ANO ANTERIOR' in p2.inner_text('#cabecalhoPerf').upper(), 'e a de comparativo tambem')
    larg2 = p2.evaluate("document.querySelector('.estoque-table').getBoundingClientRect().width")
    wrap2 = p2.evaluate("document.querySelector('.estoque-table-wrap').getBoundingClientRect().width")
    ok(larg2 <= wrap2 + 1, 'a tabela cabe no card nas tres (%d em %d)' % (larg2, wrap2))
    # O modal de confirmacao (com o campo de senha) mora dentro do .main; o
    # que nao pode existir e campo de digitacao na LISTAGEM.
    ok(p2.locator('.card input, .estoque-toolbar input:not(#campoBusca)').count() == 0,
       'nao ha campo de digitacao na listagem alem da busca')
    ok(p2.evaluate("typeof salvarMeta === 'undefined'"), 'e a tela nao carrega a funcao de gravar meta')
    ok(p2.locator('#btnIrMetas').get_attribute('href') == METAS, 'quem quer definir meta e levado para Metas')
    escolher(p2, 'filtroVisao', 'resultado')
    clic(p2, '#corpoTabela tr')
    p2.wait_for_timeout(450)
    ok(p2.locator('#eventDrawer.open').count() == 1, 'clicar na linha abre a leitura')
    p2.keyboard.press('Escape')
    p2.wait_for_timeout(350)
    ok(p2.locator('#eventDrawer.open').count() == 0, 'e Esc fecha')
    ok(not err2, 'Performance sem erro de JS: %s' % err2[:2])
    p2.close()

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

    print(chr(10) + '[12] De Performance, "Definir meta" cai no painel daquela loja')
    # 08/out: o botao levava para a listagem de Metas inteira, e a pessoa tinha
    # de achar de novo a loja em que ja estava. O link agora carrega o alvo e o
    # periodo, e Metas abre o painel de escrita ja preenchido.
    p3 = nav.new_page(viewport={'width': 1440, 'height': 950})
    e3 = []
    p3.on('pageerror', lambda e: e3.append(str(e)))
    p3.goto(URL + PERF)
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(700)
    nome = p3.evaluate("document.querySelector('#corpoTabela tr td').innerText.split(String.fromCharCode(10))[0].trim()")
    p3.evaluate("document.querySelector('#corpoTabela tr').click()")
    p3.wait_for_timeout(450)
    href = p3.get_attribute('#btnDefinirDaqui', 'href') or ''
    ok('definir=loja:' in href and 'mes=' in href and 'ano=' in href, 'o link leva o alvo e o periodo: %s' % href)
    ok(p3.evaluate("getComputedStyle(document.getElementById('btnDefinirDaqui')).textDecorationLine") == 'none',
       'e o botao nao esta sublinhado')
    p3.evaluate("document.getElementById('btnDefinirDaqui').click()")
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(800)
    ok(METAS in p3.url, 'chegou em Metas')
    ok(p3.locator('#defDrawer.open').count() == 1, 'com o painel de definir ABERTO')
    alvo = p3.inner_text('#defAlvo .dropdown-select-label')
    ok(nome and nome.lower() in alvo.lower(), 'no alvo que estava clicado: %s / %s' % (nome, alvo))

    p3.goto(URL + METAS + '?definir=vendedor:5&mes=3&ano=2026')
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(800)
    ok(p3.evaluate("document.querySelector('#abasNivel .aba-sit.active').getAttribute('data-nivel')") == 'vendedor',
       'link de vendedor abre na aba de vendedores')
    ok(p3.evaluate('mesSel') == 3 and 'Mar' in p3.inner_text('#defMes .dropdown-select-label'),
       'e no mes que o link pediu, na tela e no painel')
    p3.goto(URL + METAS + '?definir=loja:999')
    p3.wait_for_load_state('load')
    p3.wait_for_timeout(800)
    ok(p3.locator('#defDrawer.open').count() == 0 and p3.locator('#confirmModal.open').count() == 1,
       'alvo que nao existe avisa em vez de abrir painel vazio')
    ok(not e3, 'sem erro de JS no caminho: %s' % e3[:2])

    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
