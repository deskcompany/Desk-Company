# -*- coding: utf-8 -*-
# O caminho no topo (breadcrumb) navega, e as paginas de detalhe tem o botao "Voltar para <lista>" no
# cabecalho. Pacote 2 da revisao geral (02/nov/2026). O que ele protege:
#
#   o ultimo nome e a tela em que se esta: parado, sem mao e sem clique
#   o nome de um modulo abre o menu daquele modulo, sem sair da pagina e sem trocar o titulo
#   Inicio leva ao Inicio; Configuracoes leva ao hub
#   o nome do meio leva a lista (com os filtros do botao Voltar, quando ele aponta para a mesma lista)
#   clicar no caminho NUNCA corta o caminho (`path`) nem troca o titulo
#   toda pagina de detalhe tem um unico "Voltar para ..." como PRIMEIRO item de .header-acoes
#   o link pequeno de baixo da barra do caminho (.voltar-link) sumiu
#   o botao tem a mesma aparencia nos dois temas
#   a coluna do titulo mede ao menos 360 px a 1280 px nas 22 paginas (os botoes descem em vez de espremer o titulo)
#   "Voltar" (botao ou nome do meio do caminho) devolve a lista com os filtros que o usuario deixou; menu, link e F5 abrem limpo
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

TODAS = [n for n in localiza.nomes()
         if 'function renderBreadcrumb()' in open(localiza.onde(n), encoding='utf-8').read()]
DETALHES = [n for n in localiza.nomes()
            if n.endswith('-detalhe.html') or n in ('pagina-financas-caixa-lancamento.html', 'pagina-estoque-transferencia-nova.html')]
# "Voltar para Gateways" e o texto que a revisao deixou como estava; o item do menu e "Gateways de Pagamento".
NOME_DIFERENTE = {'pagina-integracoes-gateways.html': 'Gateways'}

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1280, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('dialog', lambda d: d.accept())

    def abre(arq, espera=300):
        erros.clear()
        pg.goto(localiza.uri(arq)); pg.wait_for_timeout(espera)

    def estado():
        return pg.evaluate("""() => ({ url: location.href, path: path.slice(), h1: (document.querySelector('.main h1') || {}).textContent,
          aberto: [...document.querySelectorAll('.flyout-col.open')].map(f => f.id),
          ativo: (document.querySelector('.nav-item.active, .bottom-item.active') || {getAttribute: () => null}).getAttribute('data-id') })""")

    # =======================================================================
    print('\n[1] Em %d telas com caminho: o ultimo nome parado, os outros com cara de link' % len(TODAS))
    ruins_ult, ruins_link, ruins_js = [], [], []
    for n in TODAS:
        abre(n, 250)
        if erros: ruins_js.append(n)
        r = pg.evaluate("""() => [...document.querySelectorAll('#breadcrumb .crumb')].map((c, i, t) => ({
          ultimo: i === t.length - 1, role: c.getAttribute('role'), tab: c.getAttribute('tabindex'), cursor: getComputedStyle(c).cursor,
          atual: c.classList.contains('current') }))""")
        for c in r:
            if c['ultimo'] and not (c['atual'] and c['role'] is None and c['tab'] is None and c['cursor'] == 'default'):
                ruins_ult.append(n)
            if not c['ultimo'] and not (c['role'] == 'link' and c['tab'] == '0' and c['cursor'] == 'pointer'):
                ruins_link.append(n)
    ok(not ruins_js, 'sem erro de JS ao abrir as %d telas %s' % (len(TODAS), ruins_js[:3]))
    ok(not ruins_ult, 'o ultimo nome fica parado (sem role, sem tabindex, cursor padrao) em todas: %s' % ruins_ult[:3])
    ok(not ruins_link, 'os outros nomes tem role="link", tabindex 0 e cursor de mao em todas: %s' % ruins_link[:3])

    # =======================================================================
    print('\n[2] Clicar no ultimo nome nao faz nada; clicar no modulo abre o menu dele, sem sair e sem trocar o titulo')
    ruins_ult, ruins_mod, ruins_cortou = [], [], []
    com_modulo = 0
    for n in TODAS:
        abre(n, 250)
        antes = estado()
        pg.locator('#breadcrumb .crumb').last.click(); pg.wait_for_timeout(100)
        d = estado()
        if d['url'] != antes['url'] or d['path'] != antes['path'] or d['h1'] != antes['h1']:
            ruins_ult.append(n)
        if len(antes['path']) < 2 or antes['path'][0] in ('Início', 'Configurações'):
            continue
        com_modulo += 1
        mod_id = pg.evaluate("document.querySelector('.nav-item[data-label=\"%s\"]').getAttribute('data-id')" % antes['path'][0])
        pg.locator('#breadcrumb .crumb').first.click(); pg.wait_for_timeout(120)
        d = estado()
        if d['url'] != antes['url'] or d['h1'] != antes['h1']:
            ruins_mod.append(n)
        if d['path'] != antes['path']:
            ruins_cortou.append(n)
        if d['aberto'] != ['flyout-' + mod_id] or d['ativo'] != mod_id:
            ruins_mod.append(n + ' (menu: %s, ativo: %s)' % (d['aberto'], d['ativo']))
    ok(not ruins_ult, 'clicar no ultimo nome nao muda endereco, caminho nem titulo: %s' % ruins_ult[:3])
    ok(com_modulo >= 60, '%d telas testadas com o nome do modulo' % com_modulo)
    ok(not ruins_mod, 'o nome do modulo abre o menu certo e marca o modulo, sem mudar de endereco nem de titulo: %s' % ruins_mod[:3])
    ok(not ruins_cortou, 'e o caminho continua inteiro (clicar nunca corta `path`): %s' % ruins_cortou[:3])

    # =======================================================================
    print('\n[3] Inicio leva ao Inicio; Configuracoes leva ao hub')
    abre('pagina-inicio-agenda.html')
    pg.locator('#breadcrumb .crumb').first.click(); pg.wait_for_timeout(500)
    ok(pg.url.endswith('pagina-inicio-boas-vindas.html'), 'na Agenda, "Início" abre as boas-vindas: %s' % localiza.nome(pg.url))
    ok(pg.evaluate("path.length") == 1 and pg.evaluate("document.querySelectorAll('#breadcrumb .crumb[role=link]').length") == 0,
       'e nas boas-vindas o caminho e um nome so, parado')
    abre('pagina-configuracoes-pdv.html')
    pg.locator('#breadcrumb .crumb').first.click(); pg.wait_for_timeout(500)
    ok(pg.url.endswith('pagina-configuracoes.html'), 'numa tela de Configuracoes, "Configurações" abre o hub: %s' % localiza.nome(pg.url))
    antes = pg.url
    pg.locator('#breadcrumb .crumb').first.click(); pg.wait_for_timeout(300)
    d = estado()
    ok(d['url'] == antes and d['aberto'] == ['flyout-config'], 'no hub, "Configurações" so abre o menu de Configurações: %s' % d['aberto'])
    abre('pagina-configuracoes-pdv.html')
    pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(500)
    ok(pg.url.endswith('pagina-configuracoes.html'), '"Configurações ERP" (nome do meio com destino no menu) tambem abre o hub')

    # =======================================================================
    print('\n[4] O nome do meio leva a lista (nas %d paginas de detalhe)' % len(DETALHES))
    ruins = []
    for n in DETALHES:
        abre(n)
        # sem registro aberto o caminho tem so dois nomes; o terceiro e o do registro, como nas telas com ?id
        pg.evaluate("if (path.length < 3) { path = path.concat(['Registro']); renderBreadcrumb(); }")
        esperado = pg.evaluate("""() => { const it = document.querySelector('.flyout-item[data-label="' + path[1] + '"][data-href]');
          const v = document.getElementById('btnVoltarLista'); if (!it) return null;
          const f = (u) => new URL(u, location.href).pathname;
          return (v && v.getAttribute('href') && f(v.getAttribute('href')) === f(it.getAttribute('data-href'))) ? v.getAttribute('href') : it.getAttribute('data-href'); }""")
        if not esperado:
            ruins.append(n + ' (o nome "%s" nao e item do menu)' % pg.evaluate("path[1]")); continue
        pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(500)
        if localiza.nome(pg.url) != localiza.nome(esperado):
            ruins.append('%s -> %s (esperado %s)' % (n, localiza.nome(pg.url), localiza.nome(esperado)))
    ok(not ruins, 'em todas, o nome do meio leva a lista: %s' % ruins[:3])

    abre('pagina-financas-vale-compra-detalhe.html?id=2&q=rafael&loja=1&sit=usado')
    pg.evaluate("path = ['Finanças', 'Vale-compra', 'VC-2']; renderBreadcrumb()")
    href = pg.get_attribute('#btnVoltarLista', 'href')
    pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(500)
    ok('q=rafael' in href and 'loja=1' in href and 'sit=usado' in href and pg.url.endswith(href.split('/')[-1]),
       'em Vale-compra, o nome do meio leva a lista COM os filtros que o botao Voltar leva: %s' % localiza.nome(pg.url))

    abre('pagina-logistica-separacao-detalhe.html?id=7&de=pedido')
    pg.evaluate("path = ['Logística', 'Separação', 'Pedido']; renderBreadcrumb()")
    pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(500)
    ok(localiza.nome(pg.url) == 'pagina-logistica-separacao.html', 'quando o Voltar leva ao pedido, o nome "Separação" do caminho ainda leva a fila de Separação: %s' % localiza.nome(pg.url))

    abre('pagina-financas-caixa-lancamento.html')
    antes = estado()
    pg.evaluate("path = ['Finanças', 'Relatórios Finanças', 'Qualquer']; renderBreadcrumb()")
    pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(200)
    d = estado()
    ok(d['url'] == antes['url'] and d['aberto'] == ['flyout-financas'] and d['path'] == ['Finanças', 'Relatórios Finanças', 'Qualquer'] and d['h1'] == antes['h1'],
       'nome do meio sem tela no menu abre o menu do modulo, sem sair, sem cortar o caminho e sem trocar o titulo')

    abre('pagina-financas-caixa-lancamento.html')
    pg.locator('#breadcrumb .crumb').nth(1).focus()
    pg.keyboard.press('Enter'); pg.wait_for_timeout(500)
    ok(localiza.nome(pg.url) == 'pagina-financas-caixa.html', 'pelo teclado: foco no nome e Enter levam a lista (Caixa)')

    # =======================================================================
    print('\n[5] O botao "Voltar para ..." no cabecalho das %d paginas de detalhe' % len(DETALHES))
    ruins = []
    for n in DETALHES:
        abre(n)
        r = pg.evaluate("""() => {
          const hs = [...document.querySelectorAll('.page-header .header-acoes')].filter(h => h.offsetParent !== null);
          const h = hs[0]; const f = h && h.firstElementChild;
          const voltas = h ? [...h.children].filter(x => /^Voltar para /.test(x.textContent.trim())) : [];
          const item = f && f.getAttribute('href') && [...document.querySelectorAll('.flyout-item[data-href]')].filter(i => i.getAttribute('data-href') === f.getAttribute('href').split('?')[0])[0];
          return { achou: !!f, tag: f && f.tagName, classe: f && f.className, texto: f && f.textContent.trim().replace(/\\s+/g, ' '),
                   href: f && f.getAttribute('href'), voltas: voltas.length, menu: item ? item.getAttribute('data-label') : null,
                   velho: document.querySelectorAll('.voltar-link').length, seta: !!(f && f.querySelector('svg polyline')) } }""")
        defeitos = []
        if not r['achou'] or r['tag'] != 'A' or r['classe'] != 'btn-secundario-topo': defeitos.append('nao e o botao-link do cabecalho em primeiro lugar')
        if r['voltas'] != 1: defeitos.append('%d botoes "Voltar para"' % r['voltas'])
        if not r['seta']: defeitos.append('sem seta')
        if r['velho']: defeitos.append('sobrou .voltar-link')
        if not r['href'] or not localiza.existe(localiza.nome(r['href']).split('?')[0]): defeitos.append('href nao leva a tela que existe: %s' % r['href'])
        nome_menu = NOME_DIFERENTE.get(localiza.nome(r['href'] or '').split('?')[0], r['menu'])
        if not r['menu'] or r['texto'] != 'Voltar para ' + nome_menu: defeitos.append('texto "%s", menu "%s"' % (r['texto'], r['menu']))
        if defeitos: ruins.append('%s: %s' % (n, '; '.join(defeitos)))
    ok(not ruins, 'todas: um so "Voltar para <nome do menu>", primeiro de .header-acoes, com seta e href para tela que existe: %s' % ruins[:3])

    for tela in ('pagina-logistica-separacao-detalhe.html', 'pagina-logistica-conferencia-saida-detalhe.html'):
        abre(tela + '?id=7&de=pedido')
        r = pg.evaluate("[...document.querySelectorAll('.page-header .header-acoes > *')].filter(x => /^Voltar para /.test(x.textContent.trim())).map(x => [x.textContent.trim(), x.getAttribute('href')])")
        ok(len(r) == 1 and r[0][0] == 'Voltar para o pedido de venda' and 'pagina-vendas-pedidos.html' in r[0][1],
           '%s: vindo do pedido, o MESMO botao passa a dizer "Voltar para o pedido de venda": %s' % (tela, r))

    for tela in ('pagina-vendas-crm-detalhe.html',):
        abre(tela)
        r = pg.evaluate("[...document.querySelectorAll('#btnVoltarLista')].length")
        ok(r == 1, 'CRM: um so #btnVoltarLista')

    # o botao leva a lista de verdade, e a pergunta de alteracao pendente continua (Clientes)
    abre('pagina-cadastros-clientes-detalhe.html')
    pg.click('#btnVoltarLista'); pg.wait_for_timeout(500)
    ok(localiza.nome(pg.url) == 'pagina-cadastros-clientes.html', 'sem alteracao, "Voltar para Clientes" volta para a lista: %s' % localiza.nome(pg.url))

    # =======================================================================
    print('\n[6] O cabecalho nao quebra a 1280 px e o botao tem a mesma aparencia nos dois temas')
    ruins, ruins_larg = [], []
    for n in DETALHES:
        abre(n)
        r = pg.evaluate("""() => { const h = [...document.querySelectorAll('.page-header .header-acoes')].filter(x => x.offsetParent !== null)[0];
          const t = document.querySelector('.page-header h1'); const hb = h.getBoundingClientRect(), tb = t.getBoundingClientRect(), pb = document.querySelector('.page-header').getBoundingClientRect();
          return { semSobrepor: !(hb.top < tb.bottom && hb.left < tb.right), dentro: hb.right <= innerWidth && document.documentElement.scrollWidth <= innerWidth, altura: Math.round(pb.height),
                   coluna: Math.round(h.closest('.page-header').firstElementChild.getBoundingClientRect().width) } }""")
        if not r['semSobrepor'] or not r['dentro']:
            ruins.append('%s %s' % (n, r))
        if r['coluna'] < 360: ruins_larg.append('%s (%dpx)' % (n, r['coluna']))
    ok(not ruins, 'a 1280 px os botoes nao cobrem o titulo (quando nao cabem na linha, descem para uma segunda, com o Voltar primeiro) e a pagina nao ganha barra horizontal: %s' % ruins[:3])
    ok(not ruins_larg, 'a 1280 px a coluna do titulo mede ao menos 360 px nas %d paginas (o titulo nao e espremido pelos botoes): %s' % (len(DETALHES), ruins_larg[:3]))

    def aparencia():
        return pg.evaluate("""() => { const e = document.getElementById('btnVoltarLista'); const c = getComputedStyle(e);
          return [c.color, c.backgroundColor, c.borderTopColor, c.borderTopWidth, c.borderRadius, c.fontSize, c.fontWeight, c.paddingTop, c.paddingLeft, c.display, c.textDecorationLine, c.fontFamily.split(',')[0]].join('|') }""")
    for tema in ('claro', 'escuro'):
        modelo = None
        for n in ('pagina-financas-vale-compra-detalhe.html', 'pagina-cadastros-clientes-detalhe.html', 'pagina-financas-contas-pagar-detalhe.html', 'pagina-vendas-pedidos-detalhe.html'):
            abre(n)
            pg.evaluate("document.body.classList.%s('dark')" % ('add' if tema == 'escuro' else 'remove'))
            pg.wait_for_timeout(100)
            a = aparencia()
            if modelo is None:
                modelo = a
                continue
            ok(a == modelo, 'tema %s: o botao de %s e igual ao do Vale-compra (%s)' % (tema, n, a if a != modelo else 'igual'))
        if tema == 'escuro':
            fundo = modelo.split('|')[1]
            ok(fundo != 'rgb(255, 255, 255)', 'tema escuro: o fundo do botao nao e branco (%s)' % fundo)

    # =======================================================================
    print('\n[7] Voltar devolve a lista como o usuario a deixou (busca, dropdowns, aba/periodo, card, pagina); menu, link e F5 abrem limpo')
    ABAS = '.aba-sit, .sit-tab, .periodo-aba, .periodo-op, #filtroTipo > button, #filtroEstado > button, #filtroTipoProduto > button'
    CASOS = [  # lista, detalhe, busca, [(dropdown, valor)], rotulo da aba/periodo
        ('pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html', 'a', [('filtroCategoria', '4')], 'em aberto'),
        ('pagina-cadastros-clientes.html', 'pagina-cadastros-clientes-detalhe.html', 'a', [('filtroSituacao', 'ativo')], 'Pessoa Jurídica'),
        ('pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html?id=2', '', [('filtroSituacao', 'entregue')], 'Sem filtro'),
        ('pagina-logistica-separacao.html', 'pagina-logistica-separacao-detalhe.html?id=7', 'a', [('filtroLoja', '1')], 'Aguardando separação'),
    ]
    def foto_lista(dds):
        return pg.evaluate("""(dds) => ({ q: (document.getElementById('campoBusca') || {}).value,
          resumo: (document.getElementById('paginacaoResumo') || {}).textContent,
          dd: dds.map(i => document.getElementById(i).getAttribute('data-value')),
          abas: [...document.querySelectorAll(%r)].filter(e => e.classList.contains('active') || e.classList.contains('on')).map(e => e.textContent.trim()) })""" % ABAS, dds)
    def aplica_filtros(busca, dds, rotulo):
        pg.fill('#campoBusca', busca)
        for i, v in dds:
            pg.click('#%s .dropdown-select-btn' % i); pg.click('#%s .dropdown-select-item[data-value="%s"]' % (i, v))
        pg.evaluate("""([sel, rot]) => [...document.querySelectorAll(sel)].find(e => e.textContent.trim().toLowerCase().startsWith(rot.toLowerCase())).click()""", [ABAS, rotulo])
        pg.wait_for_timeout(200)
    def vai_ao_detalhe(lista, detalhe, busca, dds, rotulo):
        abre(lista); pg.evaluate('sessionStorage.clear()'); abre(lista)
        limpa = foto_lista([i for i, v in dds])
        aplica_filtros(busca, dds, rotulo)
        filtrada = foto_lista([i for i, v in dds])
        abre(detalhe)
        return limpa, filtrada
    for lista, detalhe, busca, dds, rotulo in CASOS:
        ids = [i for i, v in dds]
        limpa, filtrada = vai_ao_detalhe(lista, detalhe, busca, dds, rotulo)
        ok(filtrada != limpa and filtrada['resumo'] != limpa['resumo'],
           '%s: o filtro aplicado muda a lista (%s -> %s)' % (lista, limpa['resumo'], filtrada['resumo']))
        pg.click('#btnVoltarLista'); pg.wait_for_timeout(700)
        volta = foto_lista(ids)
        ok(localiza.nome(pg.url) == lista and volta == filtrada, '%s: pelo botao Voltar a lista volta como estava: %s' % (lista, volta if volta != filtrada else filtrada['resumo']))
        # pelo nome do meio do caminho
        abre(lista); pg.evaluate('sessionStorage.clear()'); abre(lista)
        aplica_filtros(busca, dds, rotulo)
        abre(detalhe)
        pg.evaluate("if (path.length < 3) { path = path.concat(['Registro']); renderBreadcrumb(); }")
        pg.locator('#breadcrumb .crumb').nth(1).click(); pg.wait_for_timeout(700)
        volta = foto_lista(ids)
        ok(localiza.nome(pg.url) == lista and volta == filtrada, '%s: pelo nome do meio do caminho a lista volta filtrada: %s' % (lista, volta if volta != filtrada else filtrada['resumo']))
        # pelo menu: abre limpa (o estado do pagehide ficou guardado, e mesmo assim nao e usado)
        abre(lista); pg.evaluate('sessionStorage.clear()'); abre(lista)
        aplica_filtros(busca, dds, rotulo)
        abre(detalhe)
        mod_label, item_label = pg.evaluate("[path[0], path[1]]")
        pg.evaluate("document.querySelector('.nav-item[data-label=\"%s\"]').click()" % mod_label); pg.wait_for_timeout(200)
        pg.evaluate("document.querySelector('.flyout-item[data-label=\"%s\"][data-href]').click()" % item_label); pg.wait_for_timeout(700)
        ok(localiza.nome(pg.url) == lista and foto_lista(ids) == limpa, '%s: pelo menu a lista abre limpa: %s' % (lista, foto_lista(ids)['resumo']))
        # por link / F5 (endereco direto) e com query string: tambem limpa, mesmo com a marca de volta
        abre(lista); pg.evaluate('sessionStorage.clear()'); abre(lista)
        aplica_filtros(busca, dds, rotulo)
        abre(detalhe)
        abre(lista)
        ok(foto_lista(ids) == limpa, '%s: por link direto (ou F5) a lista abre limpa' % lista)
        abre(lista); aplica_filtros(busca, dds, rotulo)
        abre(detalhe)
        pg.evaluate("sessionStorage.setItem('deskVoltandoPara', '%s|' + Date.now())" % lista)
        abre(lista + '?zz=1')
        ok(foto_lista(ids) == limpa, '%s: com ? no endereco a lista abre limpa, mesmo com a marca de volta' % lista)
        # a marca velha (pergunta de saida respondida "nao", usuario voltou horas depois pelo menu) nao vale
        abre(lista); aplica_filtros(busca, dds, rotulo)
        abre(detalhe)
        pg.evaluate("sessionStorage.setItem('deskVoltandoPara', '%s|' + (Date.now() - 600000))" % lista)
        abre(lista)
        ok(foto_lista(ids) == limpa, '%s: a marca com mais de 2 minutos nao vale' % lista)
        ok(not erros, '%s: sem erro de JS %s' % (lista, erros[:2]))
    pg.evaluate('sessionStorage.clear()')


    b.close()

print('\n%s · FALHAS: %d' % ('TUDO VERDE' if not falhas else '%d FALHA(S)' % len(falhas), len(falhas)))
raise SystemExit(1 if falhas else 0)
