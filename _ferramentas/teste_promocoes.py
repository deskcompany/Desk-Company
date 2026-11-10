# -*- coding: utf-8 -*-
# Promocoes e Encartes, entrega 1 (09/nov/2026): a lista, a pagina da promocao e as ligacoes (ficha do produto, Parametros de vendas, catalogo).
#
# O que ele protege sao as decisoes do usuario (barganha de 04 e 09/nov/2026):
#   A promocao nasce de UMA loja; produto de outra loja nao entra
#   A revisao de ponta a ponta: cada linha ok ou fora, com o motivo; so aprova com todas ok, e aprovar pede senha
#   A trava do minimo le a MESMA conta da calculadora de preco (o bloco PRECO MINIMO), e nao uma formula copiada
#   O riscado e verdadeiro: preco de venda que subiu nos ultimos N dias (Parametros de vendas) fica fora; o historico de preco mora na ficha do produto
#   Produto ja em outra promocao ativa ou agendada que se sobrepoe no periodo fica fora
#   Depois de aprovada: preco e produtos so mudam antes de comecar; depois de comecar, so antecipar, prorrogar ou encerrar; e clonar
#   Limite total por produto (ou ESTOQUE) e limite por cliente; "Aplicar X% nos selecionados" passa pela mesma revisao
#   Quanto vendeu e lido dos Pedidos de Venda e do PDV (espelho declarado, comparado aqui)
#
#   [1]  As copias e os espelhos: os blocos PROMOCOES (3 telas) e PRECO MINIMO (2), os produtos contra Cadastros > Produtos, as vendas contra Pedidos de Venda
#   [2]  O menu: logo depois do PDV, em toda tela; e o catalogo das 7 acoes
#   [3]  A lista: abre em "Em revisao", abas, indicadores que filtram, filtros, painel e quanto vendeu (refeito aqui a partir dos Pedidos)
#   [4]  A revisao: um motivo em cada linha da nº 3, o minimo igual ao da calculadora, e aprovar com senha
#   [5]  Aplicar X% e os limites
#   [6]  A planilha: o modelo e a importacao
#   [7]  As transicoes: antecipar, prorrogar, encerrar, clonar, alterar antes de comecar e o bloqueio depois de comecar
#   [8]  O historico de preco e a trava dos N dias; a ficha do produto com "Em promocao ate" e o encerrar antes
#   [9]  A selecao detalhada (Categoria > Departamento > Secao), a selecao em massa da lista e Parametros de vendas
#   [10] Os dois temas, 1280 e 1440: sem barra para o lado, e o menu abre para baixo
#   [11] Entrega 2: o preco chega na venda (PDV e Pedido de Venda): so onde vale, os limites, o desconto por cima, a excecao na hora com senha e
#        permissao, a trava do minimo, o registro e o "quanto vendeu" so com o preco da promocao; PDV e Pedido nos dois temas, 1280 e 1440
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LISTA = 'pagina-vendas-promocoes.html'
PAG = 'pagina-vendas-promocoes-detalhe.html'
PROD = 'pagina-cadastros-produtos-detalhe.html'
PRODS = 'pagina-cadastros-produtos.html'
PED = 'pagina-vendas-pedidos.html'
PEDD = 'pagina-vendas-pedidos-detalhe.html'
PDV = 'pagina-vendas-pdv.html'
VEND = 'pagina-cadastros-vendedores-detalhe.html'
PARV = 'pagina-configuracoes-parametros-vendas.html'
CONF = 'pagina-configuracoes-confirmacoes-senha.html'

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


def bloco(t, ini, fim):
    i = t.find(ini)
    if i < 0:
        return None
    j = t.find(fim, i)
    return t[i:j] if j >= 0 else None


TXT = lambda sel: "Array.from(document.querySelectorAll('%s')).map(e => e.textContent.replace(/\\s+/g, ' ').trim())" % sel

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('dialog', lambda d: d.dismiss())

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(250)

    def limpar():
        ir(LISTA); pg.evaluate("localStorage.clear(); sessionStorage.clear()")

    def ev(js, *a):
        return pg.evaluate(js, *a) if a else pg.evaluate(js)

    def clica(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(150)

    def confirmar(senha=None):
        if senha is not None:
            pg.fill('#inputSenhaModal', senha)
        clica('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)

    def modal_aberto():
        return ev("document.getElementById('confirmModal').classList.contains('open')")

    def linhas_itens():
        return ev("Array.from(document.querySelectorAll('#corpoItens tr')).map(t => ({ sku: t.getAttribute('data-sku'), rev: (c => c.querySelector('.pr-ok') ? 'Ok' : c.querySelector('.pr-fora') ? 'Fora: ' + c.querySelector('.pr-motivo').textContent : c.textContent.replace(/\\s+/g, ' ').trim())(t.querySelector('.pr-cel-revisao')), min: t.querySelector('.pr-cel-min').textContent.trim() }))")

    def rev(sku):
        return [l['rev'] for l in linhas_itens() if l['sku'] == sku][0]

    def digitar(sku, classe, valor):
        pg.evaluate("([s, c, v]) => { const i = document.querySelector('#corpoItens tr[data-sku=\"' + s + '\"] .' + c); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); }", [sku, classe, valor])
        pg.wait_for_timeout(80)

    def tirar(sku):
        clica('#corpoItens tr[data-sku="%s"] .pr-tirar' % sku)

    def promo(id_):
        return ev("(id) => lerPromocoes().filter(p => p.id === id)[0]", id_)

    def log(chave):
        return ev("(k) => JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === k)", chave)

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'As cópias e os espelhos'):
        PI, PF = '  // ===== PROMOCOES: DADOS E LEITURA', '  // ===== FIM DO BLOCO PROMOCOES ====='
        cop = [bloco(fonte(n), PI, PF) for n in (LISTA, PAG, PROD, PDV, PEDD)]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco PROMOCOES é idêntico na lista, na página da promoção, na ficha do produto, no PDV e no Pedido de Venda')
        NI, NF = '  // ===== PROMOCOES: NA VENDA', '  // ===== FIM DO BLOCO PROMOCOES: NA VENDA ====='
        nv = [bloco(fonte(n), NI, NF) for n in (PDV, PEDD)]
        ok(nv[0] and nv[0] == nv[1], 'o bloco PROMOCOES: NA VENDA é idêntico no PDV e no Pedido de Venda')
        ok(bloco(fonte(PDV), '  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA =====') == bloco(fonte(PAG), '  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA ====='),
           'o PDV leva o bloco EMBALAGENS: LEITURA igual ao da página da promoção (a trava do mínimo precisa dele)')
        MI, MF = '  // ===== PRECO MINIMO: A CONTA DA CALCULADORA', '  // ===== FIM DO BLOCO PRECO MINIMO ====='
        cop = [bloco(fonte(n), MI, MF) for n in (PAG, PROD, PDV, PEDD)]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco PRECO MINIMO é idêntico na página da promoção, na ficha do produto (a calculadora), no PDV e no Pedido de Venda')
        calc = bloco(fonte(PROD), '  // ===== CALCULADORA DE PRECO (aprovada', '  // ===== ABA PRECOS')
        ok(calc and 'precoPiso(custoTotal' in calc and '10000 - mg - b.tBp' not in calc and 'const parametros = precoParametros' in calc,
           'a calculadora usa a conta do bloco (precoPiso e precoParametros), sem uma cópia da fórmula dentro dela')
        ok('10000 - margemBp' not in fonte(PAG).replace(cop[0] or '', ''), 'e a página da promoção não tem outra fórmula do mínimo fora do bloco')
        for ini, fim in (('  // ===== GATEWAYS: LEITURA', '  // ===== FIM DO BLOCO GATEWAYS: LEITURA ====='), ('  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA =====')):
            ok(bloco(fonte(PAG), ini, fim) == bloco(fonte(PROD), ini, fim), 'o bloco %s da página é igual ao da ficha do produto' % ini.strip(' /=').strip())
        ir(PRODS); cad = ev("PRODUTOS.map(p => [p.id, p.sku, p.nome, p.preco, p.estoque, p.status, p.categoria])")
        ir(PROD); esp = ev("PROMO_PRODUTOS.map(p => [p.id, p.sku, p.nome, p.preco, p.estoque, p.status, p.categoria])")
        ok(cad == esp, 'PROMO_PRODUTOS espelha Cadastros > Produtos (id, SKU, nome, preço, estoque, situação, categoria): %s' % [x for x in esp if x not in cad][:2])
        cats = ev("PROMO_PRODUTOS.filter(p => !CATEGORIAS_PRODUTO.filter(c => c.nome === p.categoria)[0].lojas.includes(PROMO_LOJAS[p.loja]) || !(HIERARQUIA_DEPARTAMENTO_SECAO[p.categoria][p.departamento] || []).includes(p.secao)).map(p => p.sku)")
        ok(not cats, 'a loja de cada produto aceita a categoria dele, e departamento e seção existem na hierarquia da ficha: %s' % cats)
        ok(ev("PROMO_PRODUTOS.filter(p => p.id === 1)[0].custo === 50 && PROMO_PRODUTOS.filter(p => p.id === 1)[0].custoMedio === 48"), 'o custo do produto 1 é o da aba Custos da ficha (50,00 e 48,00)')
        ir(PED)
        ped = ev("(() => { const m = { loja_virtual: 'vitrine', manual: 'vendedores' }; return PEDIDOS.filter(p => !p.pdv && ITENS_PEDIDO[p.id]).map(p => [p.id, p.dv, p.loja, m[p.canal], p.situacao, ITENS_PEDIDO[p.id].map(i => [i.sku, i.qtd, i.preco])]); })()")
        ult = ev("(() => { const r = {}; PEDIDOS.filter(p => ITENS_PEDIDO[p.id]).sort((a, b) => b.dv - a.dv).forEach(p => ITENS_PEDIDO[p.id].forEach(i => { if (i.custo !== undefined) r[i.sku] = [i.custo, i.custoMedio]; })); return r; })()")
        ir(LISTA)
        ok(ev("PROMO_VENDAS") == ped, 'PROMO_VENDAS espelha os Pedidos de Venda com itens (pedido, dias, loja, canal, situação, itens)')
        custos = ev("PROMO_PRODUTOS.filter(p => p.id !== 1).map(p => [p.sku, p.custo, p.custoMedio])")
        errados = [c for c in custos if (c[1] is None) != (c[0] not in ult) or (c[0] in ult and ult[c[0]] != [c[1], c[2]])]
        ok(not errados, 'o custo de cada produto é o do faturamento mais recente dele nos Pedidos (e vazio quando ele nunca foi vendido): %s' % errados)

    # ------------------------------------------------------------------------------------------------
    if secao(2, 'O menu e o catálogo'):
        FLY_PDV = '<div class="flyout-item" data-label="PDV" data-href="../vendas/pagina-vendas-pdv.html">'
        item = re.compile(r'\n[ \t]*' + re.escape(FLY_PDV) + r'[^\n]*\n[ \t]*<div class="flyout-item" data-label="Promoções e Encartes" data-href="\.\./vendas/pagina-vendas-promocoes\.html">')
        sem = [_os.path.basename(c) for c in localiza.caminhos() if 'id="flyout-vendas"' in open(c, encoding='utf-8').read() and not item.search(open(c, encoding='utf-8').read())]
        ok(not sem, 'toda tela com menu traz "Promoções e Encartes" logo depois do PDV: %s' % sem[:4])
        ir(PED)
        ev("document.querySelector('.flyout-item[data-label=\"Promoções e Encartes\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        ok(pg.url.split('/')[-1].split('?')[0] == LISTA, 'o item do menu abre a lista')
        ok(ev("path.join(' > ')") == 'Vendas > Promoções e Encartes' and ev("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'vendas', 'o caminho é Vendas > Promoções e Encartes, e o menu marca Vendas')
        CH = ['promocaoSalva', 'promocaoAprova', 'promocaoAntecipa', 'promocaoProrroga', 'promocaoEncerra', 'promocaoClona', 'promocaoExclui']
        for tela in (LISTA, PAG, PROD, CONF, 'pagina-cadastros-vendedores-detalhe.html', 'pagina-configuracoes-registro-atividades.html'):
            ir(tela)
            r = ev("(ch) => ch.map(c => { const a = ACOES_SENHA.filter(x => x.chave === c)[0]; return a ? [a.grupo, a.onde, a.exigePadrao] : null; })", CH)
            ok(all(x and x[0] == 'Vendas' and x[1] == 'Vendas → Promoções e Encartes' for x in r) and [x[2] for x in r] == [False, True, False, False, False, False, False],
               '%s: as 7 ações no catálogo, grupo Vendas; só aprovar pede senha de fábrica' % tela)
        for tela in (CONF, PDV, PEDD, VEND, 'pagina-configuracoes-registro-atividades.html'):
            ir(tela)
            ok(ev("ACOES_SENHA.filter(a => a.chave === 'promocaoNaHora').map(a => [a.grupo, a.onde, a.exigePadrao, a.nome])") == [['Vendas', 'Vendas → PDV e Pedidos de Venda', True, 'Aplicar o preço promocional fora da promoção']],
               '%s: "Aplicar o preço promocional fora da promoção" no catálogo, com senha de fábrica' % tela)
        com = [c for c in localiza.caminhos() if "chave:'promocaoAprova'" in open(c, encoding='utf-8').read()]
        sem = [_os.path.basename(c) for c in com if "chave:'promocaoNaHora'" not in open(c, encoding='utf-8').read()]
        ok(len(com) >= 24 and not sem, 'a ação nova está nas %d telas com o catálogo completo: %s' % (len(com), sem))
        ir(CONF)
        ok('Aprovar uma promoção' in pg.inner_text('.main') and 'Aplicar o preço promocional fora da promoção' in pg.inner_text('.main'), 'Confirmações por senha mostra "Aprovar uma promoção" e a ação nova')
        ir('pagina-cadastros-vendedores-detalhe.html')
        ok('Promoções e Encartes' in ev("MODULOS_ACESSO") and 'Aprovar uma promoção' in ev("document.getElementById('listaConfirmacoes').textContent"),
           'o perfil do vendedor tem o módulo Promoções e Encartes e a confirmação "Aprovar uma promoção"')

    # ------------------------------------------------------------------------------------------------
    if secao(3, 'A lista'):
        limpar(); ir(LISTA)
        ok(ev("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')") == 'revisao', 'abre na aba "Em revisão" (o que falta fazer), e não em "Todas"')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => +t.getAttribute('data-id'))") == [3, 8], 'com as duas em revisão: nº 3 e nº 8')
        cont = ev("Object.fromEntries(Array.from(document.querySelectorAll('#abasSituacao .sit-contador')).map(e => [e.getAttribute('data-cont'), +e.textContent]))")
        ok(cont == {'rascunho': 1, 'revisao': 2, 'agendada': 1, 'ativa': 2, 'encerrada': 2, 'todos': 8}, 'contadores: 1 rascunho, 2 em revisão, 1 agendada, 2 ativas, 2 encerradas: %s' % cont)
        sits = ev("Object.fromEntries(lerPromocoes().map(p => [p.id, promoSituacao(p)]))")
        ok(sits == {'1': 'ativa', '2': 'agendada', '3': 'revisao', '4': 'encerrada', '5': 'rascunho', '6': 'encerrada', '7': 'ativa', '8': 'revisao'}, 'cada exemplo numa situação, pela data de hoje: %s' % sits)
        # Quanto vendeu, refeito aqui a partir da lista de Pedidos (e nao do espelho).
        ir(PED)
        # Desde a entrega 2 so conta o item vendido com o preco da promocao (`promocao` = 1); os pedidos de exemplo nao levam: o painel diz zero.
        esperado = ev("""(() => { const sku = ['PAP-3002', 'ELE-1003', 'MOB-4001']; let q = 0, v = 0;
            PEDIDOS.filter(p => p.loja === 1 && p.dv <= 10 && p.situacao !== 'cancelado' && ITENS_PEDIDO[p.id]).forEach(p => ITENS_PEDIDO[p.id].forEach(i => { if (sku.includes(i.sku) && i.promocao === 1) { q += i.qtd; v += i.qtd * i.preco; } }));
            return [q, Math.round(v * 100) / 100]; })()""")
        ir(LISTA)
        clica('.aba-sit[data-sit="todos"]'); clica('#corpoTabela tr[data-id="1"]')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')"), 'clicar na linha abre o painel')
        fmt = lambda n: 'R$ ' + '{:,.2f}'.format(n).replace(',', 'X').replace('.', ',').replace('X', '.')
        ok(pg.inner_text('#prVendidoQtd').startswith('%d de 62' % esperado[0]) and pg.inner_text('#prVendidoValor') == fmt(esperado[1]),
           'o painel da nº 1 diz quanto vendeu, igual à conta feita nos Pedidos: %s un., %s (%s; %s)' % (esperado[0], fmt(esperado[1]), pg.inner_text('#prVendidoQtd'), pg.inner_text('#prVendidoValor')))
        ok(esperado == [0, 0] and not ev("!!document.getElementById('prPedidos')") and 'só o que saiu com o preço da promoção' in pg.inner_text('#drawerCorpo'),
           'os pedidos 3 e 8 venderam os produtos pelo preço de venda (vitrine): não contam, e o painel diz que só conta o preço da promoção')
        ok(ev(TXT('#drawerCorpo .drawer-footer button')) == ['Prorrogar', 'Encerrar agora', 'Clonar', 'Abrir promoção completa'], 'ativa: prorrogar, encerrar, clonar e abrir')
        ok(ev("Array.from(document.querySelectorAll('#drawerCorpo .mov-tipo a')).map(a => a.getAttribute('href'))")[0] == '../cadastros/pagina-cadastros-produtos-detalhe.html?id=9', 'o produto do painel leva à ficha dele')
        clica('#drawerClose'); clica('#corpoTabela tr[data-id="2"]')
        ok(ev(TXT('#drawerCorpo .drawer-footer button'))[:3] == ['Antecipar para hoje', 'Prorrogar', 'Encerrar agora'], 'agendada: antecipar, prorrogar e encerrar')
        clica('#drawerClose'); clica('#corpoTabela tr[data-id="3"]')
        ok(ev(TXT('#drawerCorpo .drawer-footer button')) == ['Revisar e aprovar', 'Clonar'] and not ev("!!document.getElementById('prVendidoQtd')"), 'em revisão: revisar e aprovar, e clonar; sem "quanto vendeu"')
        clica('#drawerClose')
        # Indicadores: o card deixa na lista exatamente o que ele somou.
        for k, ids in (('aprovar', [3, 8]), ('ativas', [1, 7]), ('comecam', [2])):
            clica('#indicadoresPromocoes [data-kpi="%s"]' % k)
            ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => +t.getAttribute('data-id'))") == ids and ev("document.querySelector('[data-kpi=\"%s\"]').classList.contains('on')" % k), 'o card "%s" filtra %s e fica aceso' % (k, ids))
            clica('#indicadoresPromocoes [data-kpi="%s"]' % k)
        ok(not ev("document.querySelector('.kpi-card.on')") and ev("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')") == 'revisao', 'clicar de novo desfaz, e a lista volta a abrir em "Em revisão"')
        ok(pg.inner_text('#indicadoresPromocoes [data-kpi="ativas"] .kpi-value') == fmt(0), 'o card "Vendido nas ativas" soma só a venda com o preço da promoção (o pedido 4 vendeu a camiseta a R$ 39,90: não conta)')
        clica('.aba-sit[data-sit="todos"]')
        ev("document.querySelector('#filtroLoja .dropdown-select-btn').click()"); clica('#filtroLoja .dropdown-select-item[data-value="2"]')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => +t.getAttribute('data-id'))") == [4, 7, 8], 'o filtro de loja deixa só as da Desk Brands')
        clica('#btnLimparFiltros'); clica('.aba-sit[data-sit="todos"]')
        clica('#btnPeriodo'); clica('#periodoOpcoes [data-periodo="hoje"]')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => +t.getAttribute('data-id'))") == [1, 7], 'o período "Valendo hoje" deixa as duas ativas')
        ev("document.getElementById('campoBusca').value = 'ELE-1004'; document.getElementById('campoBusca').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(100)
        clica('#btnPeriodo'); clica('#periodoOpcoes [data-periodo="todos"]')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => +t.getAttribute('data-id'))") == [2, 3], 'a busca pelo SKU acha as promoções que têm o produto')
        clica('#btnNovaPromocao'); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        ok(pg.url.endswith(PAG + '?novo=1') and pg.inner_text('#tituloPromo') == 'Nova promoção' and ev("document.getElementById('inputTitulo').value") == '' and not ev("document.querySelectorAll('#corpoItens tr').length"),
           '"Incluir promoção" abre em branco: título "Nova promoção", sem nada do exemplo')

    # ------------------------------------------------------------------------------------------------
    if secao(4, 'A revisão e a aprovação com senha'):
        limpar(); ir(PAG, '?id=3')
        ok(pg.inner_text('#tituloPromo') == 'Promoção nº 3' and ev("document.getElementById('inputTitulo').value") == 'Black Friday Desk Shope', 'o ?id= abre a promoção clicada (nº 3)')
        esperados = {'PAP-3002': 'Ok', 'MOB-4001': 'Ok', 'ELE-1003': 'abaixo do mínimo', 'MOB-4002': 'subiu', 'PAP-3001': 'sem preço promocional', 'ELE-9999': 'SKU não encontrado',
                     'VES-2001': 'é da Desk Brands', 'ELE-1004': 'já está na promoção Semana do escritório'}
        for sku, txt in esperados.items():
            r = rev(sku)
            ok(txt in r and (txt == 'Ok') == r.startswith('Ok'), '%s: %s (%s)' % (sku, txt, r))
        ok(rev('VES-2001') == 'Fora: é da Desk Brands, não da loja da promoção', 'o de outra loja tem só esse motivo')
        ok(ev("document.getElementById('btnAprovar').disabled") and '6 fora' in pg.inner_text('#resumoRevisao'), 'com linhas fora, aprovar fica travado e o resumo diz "6 fora"')
        dicas = ev("Array.from(document.querySelectorAll('#corpoItens tr[data-sku=\"MOB-4001\"] .pr-sub')).map(e => e.textContent)")
        ok(any('no cadastro: R$ 319,90' in d for d in dicas) and ev("document.querySelector('#corpoItens tr[data-sku=\"MOB-4001\"] .pr-diferente').title").startswith('Ao aprovar, este preço entra no cadastro'), 'o preço da planilha diferente do cadastro mostra os dois: %s' % dicas)
        # O minimo e o da calculadora: a ficha do produto 1 e a pagina da promocao 2 dizem o mesmo numero, e mudam juntas.
        ir(PROD, '?id=1'); clica('#btnCalcularPreco'); piso = pg.inner_text('#calcPiso')
        ir(PAG, '?id=2'); minimo = [l['min'] for l in linhas_itens() if l['sku'] == 'ELE-1001'][0]
        ok(piso == minimo == 'R$ 79,28', 'o mínimo do Fone na promoção é o "Preço mínimo" da calculadora: %s e %s' % (minimo, piso))
        ev("localStorage.setItem('deskCalculoPreco', JSON.stringify({ 1: { preco: 129.9, frete: 0, caixaId: 2, embalagemManual: null, freteLoja: 10, margem: 30, parcelas: 6, imposto: 4, comissao: 5, escolhida: 'varejo' } }))")
        ir(PROD, '?id=1'); clica('#btnCalcularPreco'); piso2 = pg.inner_text('#calcPiso')
        ir(PAG, '?id=2'); minimo2 = [l['min'] for l in linhas_itens() if l['sku'] == 'ELE-1001'][0]
        ok(piso2 == minimo2 and piso2 != piso, 'com um cálculo guardado na calculadora (frete da loja e 6x), os dois mudam juntos: %s e %s' % (minimo2, piso2))
        ev("localStorage.removeItem('deskCalculoPreco')")
        ir(PAG, '?id=3')
        for s in ('ELE-9999', 'VES-2001', 'ELE-1004', 'MOB-4002'):
            tirar(s)
        digitar('ELE-1003', 'pr-in-preco', '54,90'); digitar('PAP-3001', 'pr-in-preco', '18,49')
        ok(rev('ELE-1003') == 'Ok' and rev('PAP-3001') == 'Ok', 'corrigido o preço, a linha vira ok na hora (54,90 no Mouse; 18,49 no Caderno, acima do mínimo de 18,47)')
        digitar('PAP-3001', 'pr-in-preco', '18,46')
        ok('abaixo do mínimo de R$ 18,47' in rev('PAP-3001'), 'um centavo abaixo do mínimo, fora de novo')
        digitar('PAP-3001', 'pr-in-preco', '18,50')
        ok('não é menor que o preço de venda' in rev('PAP-3001'), 'igual ao preço de venda não é promoção')
        digitar('PAP-3001', 'pr-in-preco', '18,49')
        ok(not ev("document.getElementById('btnAprovar').disabled") and 'pode aprovar' in pg.inner_text('#resumoRevisao'), 'tudo ok: aprovar destrava')
        clica('#btnAprovar')
        ok(modal_aberto() and ev("getComputedStyle(document.getElementById('campoSenhaModal')).display") != 'none', 'aprovar abre a confirmação com o campo de senha')
        confirmar('')
        ok(modal_aberto() and promo(3)['situacao'] == 'revisao', 'sem senha, não aprova: o modal fica e a promoção continua em revisão')
        confirmar('1234')
        ok(pg.url.split('/')[-1] == LISTA + '?aprovada=3', 'com a senha, aprova e volta para a lista: %s' % pg.url.split('/')[-1])
        ok(promo(3)['situacao'] == 'aprovada' and promo(3)['aprovadaPor'] == 'Administrador Desk', 'a nº 3 fica aprovada, por quem aprovou')
        ok(ev("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')") == 'agendada' and 'aprovada com senha' in pg.inner_text('#faixaFeito')
           and ev("!!document.querySelector('#corpoTabela tr.pr-destaque[data-id=\"3\"]')"), 'a lista abre em "Agendadas", com a linha marcada e a faixa "aprovada com senha"')
        l = log('promocaoAprova')
        ok(len(l) == 1 and l[0]['senha'] is True and 'Black Friday' in l[0]['detalhe'], 'o Registro de atividades tem a aprovação, com senha')
        ok(ev("promoPrecos(4).promocional") == 299.9 and ev("promoPrecos(3).promocional") == 18.49, 'os preços da planilha entraram no cadastro (Kit Escritório 299,90; Caderno 18,49)')
        h = ev("promoHistorico(4)[0]")
        ok(h['campo'] == 'promocional' and h['de'] == 319.9 and h['para'] == 299.9 and h['origem'] == 'planilha' and h['promocao'] == 3, 'e o histórico do produto diz de onde veio: %s' % h)
        ok(ev("promoPrecos(9).promocional") == 59.9 and len(ev("promoHistorico(9)")) == 0, 'preço igual ao do cadastro não gera linha no histórico')

    # ------------------------------------------------------------------------------------------------
    if secao(5, 'Aplicar X% e os limites'):
        limpar(); ir(PAG, '?novo=1')
        ev("document.querySelector('#inputLoja .dropdown-select-btn').click()"); clica('#inputLoja .dropdown-select-item[data-value="1"]')
        for t in ('ELE-1001', 'MOB-4001'):
            pg.fill('#buscaProduto', t); pg.wait_for_timeout(100); pg.press('#buscaProduto', 'Enter'); pg.wait_for_timeout(100)
        ok([l['sku'] for l in linhas_itens()] == ['ELE-1001', 'MOB-4001'], 'a busca pelo SKU com Enter adiciona o produto')
        pg.fill('#buscaProduto', 'VES-2001'); pg.wait_for_timeout(100)
        ok('Nenhum produto ativo da Desk Shope' in pg.inner_text('#sugestoesProduto'), 'produto de outra loja não aparece na busca')
        pg.fill('#buscaProduto', '')
        clica('#checkTodosItens'); pg.fill('#inputPct', '10'); clica('#btnAplicarPct')
        precos = ev("E.itens.map(i => i.preco)")
        ok(precos == [116.91, 314.91] and rev('ELE-1001') == 'Ok' and rev('MOB-4001') == 'Ok', '10%% sobre o preço de venda: 116,91 e 314,91, os dois ok: %s' % precos)
        pg.fill('#inputPct', '50'); clica('#btnAplicarPct')
        ok(ev("E.itens.map(i => i.preco)") == [64.95, 174.95] and 'abaixo do mínimo' in rev('ELE-1001') and 'abaixo do mínimo' in rev('MOB-4001') and 'ficaram fora' in pg.inner_text('#infoPct'),
           '50%: 64,95 e 174,95, os dois abaixo do mínimo, e a barra diz que ficaram fora')
        clica('#checkTodosItens'); clica('#corpoItens tr[data-sku="ELE-1001"] .pr-marca'); pg.fill('#inputPct', '20'); clica('#btnAplicarPct')
        ok(ev("E.itens.map(i => i.preco)") == [103.92, 174.95], 'só o marcado recebe o desconto')
        pg.fill('#inputPct', '120'); clica('#btnAplicarPct')
        ok('maior que 0 e menor que 100' in pg.inner_text('#infoPct') and ev("E.itens[0].preco") == 103.92, 'porcentagem inválida não muda nada')
        digitar('ELE-1001', 'pr-in-limite', 'abc')
        ok('limite inválido' in rev('ELE-1001'), 'limite que não é número nem ESTOQUE fica fora')
        digitar('ELE-1001', 'pr-in-limite', 'estoque'); digitar('ELE-1001', 'pr-in-cliente', '0')
        ok(ev("E.itens[0].limite") == 'ESTOQUE' and 'limite por cliente inválido' in rev('ELE-1001'), '"estoque" vale ESTOQUE; limite por cliente zero é inválido')
        digitar('ELE-1001', 'pr-in-cliente', '2'); digitar('ELE-1001', 'pr-in-limite', '15')
        ok(rev('ELE-1001') == 'Ok' and ev("E.itens[0].limite") == 15 and ev("E.itens[0].cliente") == 2, 'limite 15 e 2 por cliente: ok')
        pg.fill('#inputTitulo', 'Teste'); ev("document.getElementById('inputTitulo').dispatchEvent(new Event('input'))")
        clica('#btnSalvar')
        ok(pg.url.split('/')[-1].startswith(LISTA + '?salva=') and promo(9)['itens'][0]['cliente'] == 2 and promo(9)['situacao'] == 'rascunho', 'salvar o rascunho grava a promoção nº 9 e volta para a lista, na aba Rascunho')
        ok(ev("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')") == 'rascunho', 'a lista abre em "Rascunho", onde ela foi')
        ok(len(log('promocaoSalva')) == 1, 'e o Registro de atividades tem a criação')
        tr = ev("document.querySelector('#corpoTabela tr[data-id=\"9\"]').textContent")
        ok('Teste' in tr, 'a linha nova está na lista')

    # ------------------------------------------------------------------------------------------------
    if secao(6, 'A planilha'):
        limpar(); ir(PAG, '?id=5')
        ok(ev("MODELO_PLANILHA").startswith('SKU;Quantidade;Preço promocional') and 'ESTOQUE' in ev("MODELO_PLANILHA"), 'o modelo tem SKU, Quantidade e Preço promocional, com um exemplo de ESTOQUE')
        with pg.expect_download() as dl:
            clica('#btnBaixarModelo')
        ok(dl.value.suggested_filename == 'modelo-planilha-promocao.csv', 'o botão baixa o modelo')
        csv = 'SKU;Quantidade;Preço promocional\nELE-1002;10;79,90\nTEC-0000;5;10,00\n;3;1,00\nelе-1002;ESTOQUE;\n'.replace('е', 'e')
        pg.set_input_files('#arquivoPlanilha', files=[{'name': 'p.csv', 'mimeType': 'text/csv', 'buffer': csv.encode('utf-8')}]); pg.wait_for_timeout(400)
        ok(modal_aberto() and '3 linhas lidas' in pg.inner_text('#confirmModalTexto') and 'sem SKU foi ignorada' in pg.inner_text('#confirmModalTexto'), 'importar diz o que leu: %s' % pg.inner_text('#confirmModalTexto'))
        confirmar()
        ok([l['sku'] for l in linhas_itens()] == ['ELE-1002', 'TEC-0000'] and ev("E.itens[0].limite") == 'ESTOQUE' and ev("E.itens[0].preco") is None and ev("E.itens[0].planilha"),
           'a linha repetida atualiza a de antes (ESTOQUE, preço vazio), e as linhas da planilha ficam marcadas')
        ok(rev('TEC-0000') == 'Fora: SKU não encontrado', 'SKU que não existe fica fora')
        ok('sem preço promocional' in rev('ELE-1002'), 'preço vazio e cadastro sem promocional: fora')
        digitar('ELE-1002', 'pr-in-preco', '79,90')
        ok('sem custo no cadastro' in rev('ELE-1002'), 'produto sem custo: o mínimo não tem como ser conferido, fica fora')

    # ------------------------------------------------------------------------------------------------
    if secao(7, 'As transições depois de aprovar'):
        limpar(); ir(PAG, '?id=2')
        ok(ev("document.getElementById('inputTitulo').disabled && document.querySelector('#corpoItens .pr-in-preco').disabled") and ev("getComputedStyle(document.querySelector('.barra-salvar')).display") == 'none',
           'agendada: preço, produtos e título travados, sem os botões de rascunho')
        clica('#btnFxAntecipar'); confirmar()
        pr = promo(2)
        ok(pr['inicio'] == ev("promoHoje()") and pr['fim'] == ev("promoDia(6)") and ev("promoSituacao(lerPromocoes().filter(p => p.id === 2)[0])") == 'ativa', 'antecipar: começa hoje, e os 7 dias andam junto (fim em hoje + 6)')
        ok(len(log('promocaoAntecipa')) == 1 and 'Antecipou' in pr['historico'][-1]['texto'], 'vai para o Registro de atividades e para o histórico da promoção')
        ok(ev(TXT('#faixaAcoes button')) == ['Prorrogar', 'Encerrar agora'], 'ativa: só prorrogar e encerrar')
        clica('#btnFxProrrogar')
        ok(ev("document.getElementById('painelProrrogar').style.display") == '' and ev("document.getElementById('eventDrawer').classList.contains('open')"), 'prorrogar abre o painel com a nova data')
        pg.fill('#inputProrrogar', ev("promoData(promoDia(3))")); clica('#btnConfirmarProrrogar')
        ok(ev("document.getElementById('campoProrrogar').classList.contains('has-error')"), 'data antes do fim de hoje é recusada')
        pg.fill('#inputProrrogar', ev("promoData(promoDia(20))")); clica('#btnConfirmarProrrogar'); confirmar()
        ok(promo(2)['fim'] == ev("promoDia(20)") and promo(2)['prazo'] == 'data' and len(log('promocaoProrroga')) == 1, 'prorrogada até hoje + 20, e o prazo de 7 dias vira "até uma data"')
        clica('#btnFxEncerrar'); confirmar()
        ok(promo(2)['situacao'] == 'encerrada' and promo(2)['encerradaEm'] == ev("promoHoje()") and len(log('promocaoEncerra')) == 1, 'encerrar: encerrada hoje, e registrada')
        ok(ev(TXT('#faixaAcoes button')) == ['Clonar como rascunho novo'], 'encerrada: só clonar')
        clica('#btnFxClonar'); confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        novo = promo(9)
        ok(pg.url.endswith(PAG + '?id=9') and novo['situacao'] == 'rascunho' and novo['clonadaDe'] == 2 and [(i['sku'], i['preco'], i['limite'], i['cliente']) for i in novo['itens']] == [('ELE-1001', 99.9, 'ESTOQUE', 2), ('ELE-1004', 42.9, 50, 3)],
           'clonar: rascunho novo nº 9, com os mesmos produtos, preços e limites, aberto na página')
        ok(len(log('promocaoClona')) == 1 and novo['inicio'] == ev("promoDia(1)"), 'começa amanhã, e o clone fica registrado')
        # "Ate acabar o estoque": prorrogar nao passa do limite de dias.
        ir(PAG, '?id=7&acao=prorrogar')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')"), '?acao=prorrogar (vem do painel da lista) abre o painel de prorrogar')
        pg.fill('#inputProrrogar', ev("promoData(promoDia(40))")); clica('#btnConfirmarProrrogar')
        ok(ev("document.getElementById('campoProrrogar').classList.contains('has-error')") and '30 dias' in pg.inner_text('#erroProrrogar'), 'no "até acabar o estoque", prorrogar além dos 30 dias é recusado')
        # Alterar antes de comecar: volta para a revisao.
        limpar(); ir(PAG, '?id=2')
        clica('#btnFxAlterar'); confirmar()
        ok(promo(2)['situacao'] == 'revisao' and 'aprovadaEm' not in promo(2) and not ev("document.getElementById('inputTitulo').disabled"), 'agendada: "Alterar antes de começar" a devolve para a revisão, e os campos destravam')
        ir(PAG, '?id=1')
        ok(ev("Array.from(document.querySelectorAll('#corpoItens input')).every(i => i.disabled)") and not ev("document.getElementById('faixaAcoes').textContent.includes('Alterar')"), 'ativa: nenhum campo de produto se mexe, e não há "Alterar"')
        ok('Vendeu' in rev('PAP-3002'), 'e a coluna da revisão mostra quanto vendeu de cada produto')
        # Pela lista: antecipar e encerrar pelo painel.
        limpar(); ir(LISTA); clica('.aba-sit[data-sit="todos"]'); clica('#corpoTabela tr[data-id="2"]'); clica('#btnPrAntecipar'); confirmar()
        ok(ev("document.querySelector('#abasSituacao .aba-sit.active').getAttribute('data-sit')") == 'ativa' and 'antecipada' in pg.inner_text('#faixaFeito'), 'pelo painel da lista: antecipada, e a lista vai para "Ativas" dizendo o que aconteceu')
        ir(PAG, '?id=3'); clica('[data-acao="excluir"]'); confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
        ok(not promo(3) and 'excluída' in pg.inner_text('#faixaFeito') and len(log('promocaoExclui')) == 1, 'excluir uma em revisão: some da lista, com a faixa e o registro')

    # ------------------------------------------------------------------------------------------------
    if secao(8, 'O histórico de preço, a trava dos N dias e a ficha do produto'):
        limpar(); ir(PROD, '?id=8'); clica('.tab-item[data-tab="precos"]')
        ok('De venda' in pg.inner_text('#tabelaHistoricoPreco') and 'Marina Costa' in pg.inner_text('#tabelaHistoricoPreco') and 'R$ 69,90' in pg.inner_text('#tabelaHistoricoPreco'), 'a aba Preços mostra o histórico: data, de, para, quem e origem')
        ok('não entra em promoção' in pg.inner_text('#historicoPrecoTrava'), 'e avisa que o produto não entra em promoção até passar a trava')
        ir(PARV); pg.fill('#promoRiscado', '10'); clica('#btnSalvarParam'); pg.keyboard.press('Escape')
        ir(PAG, '?id=3')
        ok('subiu' not in rev('MOB-4002') and rev('MOB-4002') == 'Ok', 'com a trava em 10 dias (Parâmetros de vendas), a subida de 12 dias atrás não pesa mais')
        ir(PARV); pg.fill('#promoRiscado', '30'); clica('#btnSalvarParam'); pg.keyboard.press('Escape')
        # Subir o preco de venda na ficha: entra no historico, e a revisao passa a deixar o produto fora.
        ir(PROD, '?id=9'); clica('#btnEditarCadastro') if ev("!!document.getElementById('btnEditarCadastro')") else None
        ev("document.getElementById('inputPrecoVenda').value = '69,90'"); ev("document.getElementById('btnSalvarProduto').click()"); pg.wait_for_timeout(500)
        ok(pg.url.split('/')[-1].split('?')[0] == PRODS, 'salvar volta para a lista de produtos, como antes')
        ir(PROD, '?id=9'); h = ev("promoHistorico(9)[0]")
        ok(h['campo'] == 'venda' and h['de'] == 64.9 and h['para'] == 69.9 and h['origem'] == 'cadastro' and h['quem'] == 'Administrador Desk', 'salvar o preço novo na ficha grava o histórico (de 64,90 para 69,90, cadastro)')
        ir(PROD, '?id=9')
        ok(ev("document.getElementById('inputPrecoVenda').value") == '69,90', 'reaberta, a ficha mostra o preço salvo')
        ir(PAG, '?id=3')
        ok('o preço de venda subiu em' in rev('PAP-3002'), 'e a revisão da promoção passa a deixar o Kit Papelaria fora')
        # Em promocao ate ...: o Mouse esta na nº 1, ativa.
        limpar(); ir(PROD, '?id=7')
        t = pg.inner_text('#promoDoProduto')
        ok(('Em promoção até ' + ev("promoData(promoDia(4))")) in t and 'ativada por Administrador Desk pela tela Promoções e Encartes' in t, 'a ficha do Mouse diz "Em promoção até", quem ativou e por onde: %s' % t[:140])
        ok(ev("document.getElementById('linkPromoProduto').getAttribute('href')") == '../vendas/pagina-vendas-promocoes-detalhe.html?id=1', 'com o link para a promoção')
        clica('#btnEncerrarPromoProduto'); confirmar()
        it = [i for i in promo(1)['itens'] if i['sku'] == 'ELE-1003'][0]
        ok(it.get('encerrado', {}).get('em') == ev("promoHoje()") and ev("getComputedStyle(document.getElementById('promoDoProduto')).display") == 'none', 'encerrar antes tira o produto da promoção hoje, e a faixa some')
        ok(len(log('promocaoEncerra')) == 1 and 'Mouse' in log('promocaoEncerra')[0]['detalhe'], 'e vai para o Registro de atividades')
        ok(ev("promoSituacao(lerPromocoes().filter(p => p.id === 1)[0])") == 'ativa', 'os outros produtos da promoção continuam: ela segue ativa')
        ir(PROD, '?id=1')
        ok('Promoção agendada de' in pg.inner_text('#promoDoProduto'), 'o Fone, numa agendada, mostra "Promoção agendada de … a …"')

    # ------------------------------------------------------------------------------------------------
    if secao(9, 'A seleção detalhada, a seleção em massa e Parâmetros de vendas'):
        limpar(); ir(PAG, '?id=5')
        clica('#btnSelecaoDetalhada')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')") and ev("document.querySelectorAll('#selLista .pr-sel-item').length") == 1, 'Desk Tech: a seleção mostra só o produto ativo da loja (1)')
        clica('#drawerClose')
        ev("document.querySelector('#inputLoja .dropdown-select-btn').click()"); clica('#inputLoja .dropdown-select-item[data-value="1"]')
        ok(modal_aberto() and 'tira 1 produto' in pg.inner_text('#confirmModalTexto'), 'trocar a loja com produto da outra pergunta antes, dizendo o que sai')
        confirmar()
        ok(not linhas_itens() and ev("E.loja") == 1, 'confirmado, o produto da Desk Tech sai')
        clica('#btnSelecaoDetalhada')
        n0 = ev("document.querySelectorAll('#selLista .pr-sel-item').length")
        ok(n0 == 7 and ev("document.getElementById('selDepartamento').classList.contains('disabled') && document.getElementById('selSecao').classList.contains('disabled')"), 'Desk Shope: 7 produtos ativos, e Departamento e Seção nascem travados')
        clica('#selCategoria .dropdown-select-btn'); clica('#selCategoria .dropdown-select-item[data-value="Eletrônicos"]')
        ok(not ev("document.getElementById('selDepartamento').classList.contains('disabled')") and ev("document.querySelectorAll('#selLista .pr-sel-item').length") == 3, 'Eletrônicos: 3, e o Departamento destrava')
        clica('#selDepartamento .dropdown-select-btn'); clica('#selDepartamento .dropdown-select-item[data-value="Informática"]')
        ok(ev("document.querySelectorAll('#selLista .pr-sel-item').length") == 1 and not ev("document.getElementById('selSecao').classList.contains('disabled')"), 'Informática: só o Mouse, e a Seção destrava')
        clica('#selCategoria .dropdown-select-btn'); clica('#selCategoria .dropdown-select-item[data-value=""]')
        clica('#selFornecedor .dropdown-select-btn'); clica('#selFornecedor .dropdown-select-item[data-value="Distribuidora Nordeste Ltda"]')
        ok(ev("document.querySelectorAll('#selLista .pr-sel-item').length") == 2, 'o filtro de fornecedor: os 2 de papelaria ativos')
        clica('#selTodos'); clica('#btnSelAdicionar'); confirmar()
        ok([l['sku'] for l in linhas_itens()] == ['PAP-3001', 'PAP-3002'], 'adicionar os marcados põe os dois na promoção')
        # Selecao em massa da lista.
        limpar(); ir(LISTA); clica('.aba-sit[data-sit="todos"]')
        for i in (5, 1):
            clica('#corpoTabela tr[data-id="%d"] .item-checkbox' % i)
        ok(ev("document.getElementById('barraSelecao').classList.contains('show')"), 'marcar mostra a barra de seleção no rodapé')
        clica('#btnExcluirSelecionados')
        ok(modal_aberto() and 'Uma já aprovada fica de fora' in pg.inner_text('#confirmModalTexto') and ev("getComputedStyle(document.getElementById('confirmCienteRow')).display") == 'none', 'excluir: só o rascunho vai, e a aprovada fica de fora (1 item: sem o "Estou ciente")')
        confirmar()
        ok(not promo(5) and promo(1), 'o rascunho foi excluído, a ativa ficou')
        for i in (1, 7):
            clica('#corpoTabela tr[data-id="%d"] .item-checkbox' % i)
        clica('#btnEncerrarSelecionadas')
        ok(ev("document.getElementById('btnConfirmModalConfirmar').disabled") and ev("getComputedStyle(document.getElementById('confirmCienteRow')).display") != 'none', 'encerrar 2: o "Estou ciente" aparece e trava o botão')
        clica('#confirmCienteCheckbox'); confirmar()
        ok(promo(1)['situacao'] == 'encerrada' and promo(7)['situacao'] == 'encerrada', 'as duas ativas encerradas')
        pg.keyboard.press('Escape')
        # Parametros de vendas.
        ir(PARV)
        ok('Promoções' in ev(TXT('.par-secao-titulo')) and pg.input_value('#promoRiscado') == '30' and pg.input_value('#promoEstoqueMax') == '30', 'Parâmetros de vendas tem a seção Promoções, com 30 e 30 de fábrica')
        ok(ev("PARAM_PADRAO.promoRiscadoDias") == 30 and ev("PARAM_PADRAO.promoEstoqueMaxDias") == 30, 'e o de fábrica declarado é o mesmo das telas que leem')
        ir(LISTA); ok(ev("PROMO_FABRICA") == {'promoRiscadoDias': 30, 'promoEstoqueMaxDias': 30}, 'o bloco PROMOCOES tem o mesmo de fábrica')
        ir(PARV); pg.fill('#promoEstoqueMax', '0'); pg.wait_for_timeout(100)
        ok(ev("document.getElementById('campoEstoqueMax').classList.contains('has-error')"), 'zero dias é inválido')
        pg.fill('#promoEstoqueMax', '20'); clica('#btnSalvarParam'); pg.keyboard.press('Escape')
        ir(PAG, '?novo=1')
        ev("document.querySelector('#inputPrazo .dropdown-select-btn').click()"); clica('#inputPrazo .dropdown-select-item[data-value="estoque"]')
        pg.fill('#inputInicio', ev("promoData(promoDia(2))")); ev("document.getElementById('inputInicio').dispatchEvent(new Event('input'))"); pg.wait_for_timeout(100)
        ok(ev("document.getElementById('inputFim').value") == ev("promoData(promoDia(21))") and '20 dias' in pg.inner_text('#hintPrazo'), 'com 20 dias, "até acabar o estoque" termina no 20º dia: %s' % ev("document.getElementById('inputFim').value"))

    # ------------------------------------------------------------------------------------------------
    if secao(10, 'Os dois temas, 1280 e 1440'):
        limpar()
        for w in (1280, 1440):
            pg.set_viewport_size({'width': w, 'height': 900})
            for tema in ('dark', 'light'):
                for tela, q in ((LISTA, ''), (PAG, '?id=3'), (PAG, '?id=1'), (PROD, '?id=1')):
                    ir(tela, q)
                    ev("(t) => document.body.classList.toggle('dark', t === 'dark')", tema)
                    if tela == LISTA: clica('.aba-sit[data-sit="todos"]')
                    if tela == PROD: clica('.tab-item[data-tab="precos"]')
                    larg = ev("[document.documentElement.scrollWidth, window.innerWidth, Math.max(0, ...Array.from(document.querySelectorAll('.estoque-table-wrap, .itens-table-wrap, .custos-table-wrap')).filter(e => e.offsetParent).map(e => e.scrollWidth - e.clientWidth))]")
                    ok(larg[0] <= larg[1] and larg[2] <= 1, '%s%s a %d, tema %s: sem barra para o lado (página %d de %d, tabela sobra %d)' % (tela, q, w, tema, larg[0], larg[1], larg[2]))
        pg.set_viewport_size({'width': 1440, 'height': 900})
        ir(PAG, '?id=3'); ev("document.querySelector('#inputPrazo .dropdown-select-btn').click()"); pg.wait_for_timeout(200)
        r = ev("(() => { const b = document.querySelector('#inputPrazo .dropdown-select-btn').getBoundingClientRect(), m = document.querySelector('#inputPrazo .dropdown-select-menu').getBoundingClientRect(); return [m.top >= b.bottom - 1, m.bottom <= innerHeight + 1]; })()")
        ok(r == [True, True], 'o menu do Prazo abre para baixo, inteiro na tela')
        ev("document.querySelector('#inputLoja .dropdown-select-btn').click()"); pg.wait_for_timeout(100)
        ok(ev("document.querySelectorAll('.dropdown-select-menu.open').length") == 1, 'abrir um dropdown fecha o outro')
        ok(ev("getComputedStyle(document.body).fontFamily").startswith('Nunito'), 'Nunito no corpo')

    # ------------------------------------------------------------------------------------------------
    # Entrega 2 (09/nov/2026): o preco chega na venda. PDV e Pedido de Venda, os limites, o desconto por cima, a excecao na hora e o vendido.
    def escolhe(raiz, v):
        clica('#%s .dropdown-select-btn' % raiz)
        ev("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(v)]); pg.wait_for_timeout(150)

    def pdv_abre(loja=1):
        ir(PDV); ev("localStorage.removeItem('deskPdv'); localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); ir(PDV)
        clica('#btnAbrirCaixa'); escolhe('abrirLoja', loja); pg.fill('#abrirTroco', '100'); clica('#btnConfirmarAbertura'); pg.wait_for_timeout(250)

    def pdv_add(sku, q='1'):
        pg.fill('#qtdProduto', q); pg.fill('#buscaProduto', sku); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)

    def fecha_aviso():
        if modal_aberto():
            clica('#btnConfirmModalConfirmar'); pg.wait_for_timeout(150)

    def itens_pdv():
        return ev("venda.itens.map(i => [i.sku, i.qtd, i.preco, i.promocao || null])")

    def pdv_finaliza():
        clica('#btnContinuar'); pg.wait_for_timeout(300)
        escolhe('selAddReceb', 'pix'); clica('#btnFinalizar'); pg.wait_for_timeout(350); fecha_aviso()
        clica('#btnOutraVenda'); pg.wait_for_timeout(250)

    def pdv_cliente(txt):
        clica('#btnCliente'); pg.fill('#buscaCliente', txt); pg.wait_for_timeout(150); clica('#listaClientes .pdv-cli'); pg.wait_for_timeout(200)

    def ped_campo(i, c, v):
        ev("([i, c, v]) => { const e = document.querySelector('#corpoItens input[data-campo=\"' + c + '\"][data-i=\"' + i + '\"]'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); }", [i, c, v])
        pg.wait_for_timeout(150)

    def ped_novo(loja=1):
        ir(PEDD, '?novo=1'); escolhe('inputLoja', loja)

    def ped_add(sku, q):
        n = ev("ITENS.findIndex(i => !i.sku)")   # o pedido novo ja abre com uma linha em branco
        if n < 0:
            clica('#btnAdicionarItem'); n = ev("ITENS.length") - 1
        ped_campo(n, 'sku', sku); ped_campo(n, 'qtd', q)

    def itens_ped():
        return ev("ITENS.filter(i => i.sku).map(i => [i.sku, i.qtd, i.precoLista, i.promocao || null])")

    def promo_muda(id_, **m):
        ev("([i, m]) => { const l = lerPromocoes(); Object.assign(l.filter(p => p.id === i)[0], m); gravarPromocoes(l); }", [id_, m])

    if secao(11, 'O preço na venda: PDV e Pedido de Venda'):
        limpar()
        # --- o preco entra sozinho so onde vale
        pdv_abre(1)
        pdv_add('PAP-3002')
        ok(itens_pdv() == [['PAP-3002', 1, 59.9, 1]], 'PDV: a promoção ativa nº 1 (Desk Shope, PDV marcado) põe o preço dela sozinha, sem senha: %s' % itens_pdv())
        ok(not modal_aberto(), 'e não pede senha nem mostra aviso')
        tag = ev("(() => { const t = document.querySelector('#listaItens tbody tr .promo-tag'); return t ? [t.textContent.replace(/\\s+/g, ' ').trim(), !!t.querySelector('a')] : null; })()")
        # 10/nov (pedido do usuario): a etiqueta so diz o preco, sem o link da promocao, no PDV e no Pedido de Venda (o bloco NA VENDA e o mesmo)
        ok(tag and 'de R$ 64,90 por R$ 59,90' in tag[0] and 'Volta às aulas' not in tag[0] and not tag[1],
           'o item mostra "de R$ 64,90 por R$ 59,90", sem o nome nem o link da promoção: %s' % tag)
        pdv_add('ELE-1004')
        ok(itens_pdv()[-1] == ['ELE-1004', 1, 45.0, None], 'a agendada (nº 2, Carregador) não entra: preço de venda')
        ok(ev("promoNaVenda('VES-2001', 1, 'pdv')") is None and ev("promoNaVenda('VES-2001', 2, 'pdv').preco") == 37.9, 'a camiseta só tem o preço da nº 7 na Desk Brands, a loja da promoção')
        # --- o limite por cliente, sem cliente: vale por venda; a linha se divide
        pdv_add('PAP-3002', '2')
        av = ev("document.getElementById('confirmModalTexto').textContent") if modal_aberto() else ''
        fecha_aviso()
        ok(itens_pdv() == [['PAP-3002', 2, 59.9, 1], ['ELE-1004', 1, 45.0, None], ['PAP-3002', 1, 64.9, None]],
           'limite de 2 por cliente: a terceira unidade entra numa linha a parte, pelo preço de venda: %s' % itens_pdv())
        ok('numa linha a parte' in av and 'por venda' in av, 'e a tela diz por quê, e que sem cliente o limite vale por venda: "%s"' % av[:160])
        ok('sem cliente identificado, vale por venda' in ev("document.querySelectorAll('#listaItens tbody tr')[2].textContent"), 'a linha do preço de venda guarda o motivo')
        # --- o desconto maximo vale sobre o promocional
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)')
        ev("document.querySelector('input[name=itemAjusteModo][value=valor]').click()")
        pg.fill('#itemAjusteValor', '11,98'); ev("document.getElementById('itemAjusteValor').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem')
        ok(not modal_aberto() and ev("venda.itens[0].ajusteValor") == 11.98, 'desconto de R$ 11,98 nas 2 un. de R$ 59,90 (10% do promocional) passa sem liberação')
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)')
        pg.fill('#itemAjusteValor', '12,98'); ev("document.getElementById('itemAjusteValor').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem')
        txt = ev("document.getElementById('confirmModalTexto').textContent") if modal_aberto() else ''
        ok(modal_aberto() and '10,83%' in txt and ev("document.getElementById('campoSenhaModal').classList.contains('on')"),
           'R$ 12,98 (10%% do preço de venda, 10,83%% do promocional) pede a liberação com senha: o máximo vale sobre o promocional: "%s"' % txt[:90])
        clica('#btnConfirmModalCancelar'); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # --- "Aplicar preco promocional": so fora de promocao e com o promocional no cadastro
        botao = lambda: ev("getComputedStyle(document.getElementById('btnAplicarPromo')).display !== 'none' && document.getElementById('itemDrawer').classList.contains('open')")
        clica('#listaItens tbody tr[data-item="1"] td:nth-child(2)')
        ok(botao(), 'no Carregador (fora de promoção hoje, promocional R$ 42,90 no cadastro) aparece "Aplicar preço promocional"')
        est = ev("(() => { const s = getComputedStyle(document.getElementById('btnAplicarPromo')); return [s.fontFamily.split(',')[0], s.borderRadius]; })()")
        ok(est == ['Nunito', '20px'], 'e o botão tem o CSS do botão secundário do sistema (Nunito, cantos de 20px), e não o nativo: %s' % est)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)')
        ok(not botao(), 'no item que já está na promoção, não aparece'); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        pdv_add('PAP-3001'); clica('#listaItens tbody tr[data-item="3"] td:nth-child(2)')
        ok(not botao(), 'no produto sem promocional no cadastro (Caderno), não aparece'); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # sem permissao
        escolhe('selVendedor', 6)
        clica('#listaItens tbody tr[data-item="1"] td:nth-child(2)'); clica('#btnAplicarPromo')
        ok(not modal_aberto() and 'Bianca Furtado não tem a permissão' in pg.inner_text('#erroItem') and ev("venda.itens[1].preco") == 45,
           'vendedora sem a permissão no cadastro (Bianca Furtado): não aplica e diz onde a permissão mora')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # abaixo do minimo: o promocional do cadastro abaixo da conta da calculadora
        ev("localStorage.setItem('deskPrecoProduto', JSON.stringify({ 11: { promocional: 39.90 } }))")
        escolhe('selVendedor', 1)
        clica('#listaItens tbody tr[data-item="1"] td:nth-child(2)'); clica('#btnAplicarPromo')
        ok(not modal_aberto() and 'abaixo do mínimo da calculadora (R$ 40,07)' in pg.inner_text('#erroItem') and ev("venda.itens[1].preco") == 45,
           'promocional do cadastro abaixo do mínimo da calculadora: não aplica e diz por quê: "%s"' % pg.inner_text('#erroItem')[:120])
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ev("localStorage.removeItem('deskPrecoProduto')")
        # com permissao: pede senha; sem senha nao aplica
        clica('#listaItens tbody tr[data-item="1"] td:nth-child(2)'); clica('#btnAplicarPromo')
        ok(modal_aberto() and ev("document.getElementById('campoSenhaModal').classList.contains('on')") and 'Quem aplica: Marina Costa' in ev("document.getElementById('confirmModalTexto').textContent"),
           'Marina Costa (com a permissão): abre a confirmação, com o campo de senha')
        confirmar('')
        ok(modal_aberto() and ev("venda.itens[1].preco") == 45, 'sem a senha, não aplica')
        confirmar('1234')
        ok(not modal_aberto() and ev("venda.itens[1].preco") == 42.9 and ev("venda.itens[1].naHora.por") == 'Marina Costa', 'com a senha, o item passa a R$ 42,90, com quem aplicou')
        l = log('promocaoNaHora')
        ok(len(l) == 1 and l[0]['senha'] is True and 'Carregador USB-C 20W' in l[0]['detalhe'] and 'Marina Costa' in l[0]['detalhe'], 'e vai para o Registro de atividades, com senha: %s' % (l[:1],))
        ok('aplicado com senha' in ev("document.querySelectorAll('#listaItens tbody tr')[1].textContent"), 'a linha mostra que o promocional foi aplicado com senha')
        # o minimo e a mesma conta da pagina da promocao (bloco PRECO MINIMO)
        m_pdv = ev("PROMO_PRODUTOS.map(p => promoMinimoCent(p))")
        # --- fecha a venda: o vendido conta so o que saiu com o preco da promocao
        pdv_finaliza()
        vend = ev("JSON.parse(localStorage.getItem('deskPdv')).turno.vendas[0].itens.map(i => [i.sku, i.qtd, i.promocao, !!i.naHora])")
        ok(vend == [['PAP-3002', 2, 1, False], ['ELE-1004', 1, None, True], ['PAP-3002', 1, None, False], ['PAP-3001', 1, None, False]], 'a venda gravada marca a promoção de cada item: %s' % vend)
        ir(PAG, '?id=1')
        ok(ev("PROMO_PRODUTOS.map(p => minimoDe(p))") == m_pdv, 'o mínimo do PDV é o da página da promoção, produto a produto (a mesma conta da calculadora)')
        ir(LISTA); clica('.aba-sit[data-sit="todos"]'); clica('#corpoTabela tr[data-id="1"]')
        ok(pg.inner_text('#prVendidoQtd').startswith('2 de 62') and pg.inner_text('#prVendidoValor') == 'R$ 107,82',
           'o painel da nº 1 conta só as 2 un. com o preço dela (2 × R$ 59,90 − R$ 11,98 de desconto): %s, %s' % (pg.inner_text('#prVendidoQtd'), pg.inner_text('#prVendidoValor')))
        ok(ev("Array.from(document.querySelectorAll('#prPedidos a')).map(a => a.getAttribute('href'))") == ['../vendas/pagina-vendas-pedidos.html?busca=PDV-0001'], 'e leva à venda do PDV que usou o preço')
        clica('#drawerClose')
        ok(pg.inner_text('#indicadoresPromocoes [data-kpi="ativas"] .kpi-value') == 'R$ 107,82', 'o card "Vendido nas ativas" soma a mesma venda')
        # --- o limite por cliente entre vendas, com cliente identificado
        pdv_abre(1); pdv_cliente('Marina Duarte'); pdv_add('PAP-3002', '2'); fecha_aviso(); pdv_finaliza()
        pdv_cliente('Marina Duarte'); pdv_add('PAP-3002', '1')
        av = ev("document.getElementById('confirmModalTexto').textContent") if modal_aberto() else ''
        fecha_aviso()
        ok(itens_pdv() == [['PAP-3002', 1, 64.9, None]] and 'o cliente já levou 2' in av, 'a cliente que já levou 2 na promoção leva a próxima pelo preço de venda, e a tela diz que ela já levou 2: "%s"' % av[:140])
        pdv_cliente('Pedro Henrique'); ev("venda.itens = []; pintarVenda()"); pdv_add('PAP-3002', '1')
        ok(itens_pdv() == [['PAP-3002', 1, 59.9, 1]], 'outro cliente leva pelo preço da promoção')
        # trocar para o cliente que ja levou: a venda nao fecha com a linha da promocao
        pdv_cliente('Marina Duarte'); clica('#btnContinuar'); pg.wait_for_timeout(250); escolhe('selAddReceb', 'pix'); clica('#btnFinalizar'); pg.wait_for_timeout(300)
        ok(modal_aberto() and 'cabem só 0 un. no preço da promoção' in ev("document.getElementById('confirmModalTexto').textContent"), 'trocar para a cliente que já levou o limite trava a venda e diz o que fazer')
        fecha_aviso()
        # --- o limite total
        ev("localStorage.setItem('deskPromoUsos', JSON.stringify({ 90: { pedido: null, data: promoHoje(), loja: 1, cliente: 'outro', itens: [{ sku: 'MOB-4001', qtd: 10, preco: 319.9, promocao: 1 }] } }))")
        pdv_abre(1); pdv_add('MOB-4001')
        av = ev("document.getElementById('confirmModalTexto').textContent") if modal_aberto() else ''
        fecha_aviso()
        ok(itens_pdv() == [['MOB-4001', 1, 349.9, None]] and 'o limite de 10 un. da promoção' in av, 'com as 10 un. do limite total já vendidas, o Kit entra pelo preço de venda: "%s"' % av[:120])
        ev("localStorage.removeItem('deskPromoUsos')")
        # --- agendada antecipada, encerrada, e o lugar
        promo_muda(1, onde=['vitrine', 'vendedores'])
        pdv_abre(1); pdv_add('PAP-3002')
        ok(itens_pdv() == [['PAP-3002', 1, 64.9, None]], 'a nº 1 sem o PDV marcado não entra no PDV')
        promo_muda(1, onde=['vitrine', 'pdv', 'vendedores'], situacao='encerrada', encerradaEm=ev("promoHoje()"), encerradaPor='Teste')
        pdv_abre(1); pdv_add('PAP-3002')
        ok(itens_pdv() == [['PAP-3002', 1, 64.9, None]], 'encerrada não entra')
        promo_muda(2, inicio=ev("promoHoje()"))
        pdv_abre(1); pdv_add('ELE-1004')
        ok(itens_pdv() == [['ELE-1004', 1, 42.9, 2]], 'a nº 2, antecipada para hoje (ativa), entra')
        ev("localStorage.setItem('deskPrecoProduto', JSON.stringify({ 9: { venda: 69.90 } }))")
        pdv_add('PAP-3002')
        ok(itens_pdv()[-1] == ['PAP-3002', 1, 69.9, None], 'o preço de venda é o da ficha do produto (a dona do preço): mudou lá, a venda usa o novo')
        limpar()

        # --- Pedido de Venda
        ped_novo(1); ped_add('PAP-3002', '3')
        ok(itens_ped() == [['PAP-3002', 2, 59.9, 1], ['PAP-3002', 1, 64.9, None]], 'Pedido de Venda: a nº 1 (vendedores marcado) entra sozinha, e o que passa do limite vai numa linha logo abaixo: %s' % itens_ped())
        tags = ev("Array.from(document.querySelectorAll('#corpoItens [data-promo]')).map(e => e.textContent.replace(/\\s+/g, ' ').trim())")
        ok('de R$ 64,90 por R$ 59,90' in tags[0] and 'passou do limite de 2 por cliente' in tags[1], 'cada linha diz a sua: "de… por…" e o motivo do preço de venda: %s' % tags[:2])
        ok(not ev("!!document.querySelector('#corpoItens [data-promo] a')") and 'Volta às aulas' not in tags[0], 'sem o nome nem o link da promoção (pedido do usuário em 10/nov)')
        ev("ITENS[0].desconto = 10; renderItens()")
        ok(abs(ev("precoUnit(ITENS[0])") - 53.91) < 0.001, 'o desconto do item vale sobre o promocional (R$ 59,90 − 10% = R$ 53,91)')
        ped_novo(2); ped_add('PAP-3002', '1')
        ok(itens_ped() == [['PAP-3002', 1, 64.9, None]], 'num pedido da Desk Brands, a promoção da Desk Shope não entra')
        promo_muda(1, onde=['vitrine', 'pdv'])
        ped_novo(1); ped_add('PAP-3002', '1')
        ok(itens_ped() == [['PAP-3002', 1, 64.9, None]], 'a nº 1 sem "vendedores" marcado não entra no Pedido de Venda')
        limpar()
        ped_novo(1); ped_add('ELE-1004', '1')
        escolhe('inputVendedor', 'Rafael Andrade'); clica('#corpoItens [data-editar="0"]'); clica('#btnAplicarPromoItem')
        ok(not modal_aberto() and 'Rafael Andrade não tem a permissão' in pg.inner_text('#erroPromoItem') and ev("ITENS[0].precoLista") == 45, 'Pedido: sem a permissão, não aplica')
        clica('#btnCancelarItem'); escolhe('inputVendedor', 'Marina Costa'); clica('#corpoItens [data-editar="0"]'); clica('#btnAplicarPromoItem'); confirmar('1234')
        ok(ev("ITENS[0].precoLista") == 42.9 and ev("ITENS[0].naHora.por") == 'Marina Costa' and len(log('promocaoNaHora')) == 1, 'com a permissão e a senha, aplica e registra')
        # salvar grava o uso; o painel da promocao conta
        ped_add('PAP-3002', '2')
        pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))")
        ev("PARAM.bloquearPedidoAtrasoDias = 0"); clica('#btnSalvar'); pg.wait_for_timeout(250); fecha_aviso(); pg.wait_for_timeout(200)
        uso = ev("JSON.parse(localStorage.getItem('deskPromoUsos') || '{}')")
        ok(len(uso) == 1 and list(uso.values())[0]['itens'] == [{'sku': 'PAP-3002', 'qtd': 2, 'preco': 59.9, 'promocao': 1}] and list(uso.values())[0]['cliente'] == 'juliana prado',
           'salvar grava o que saiu com o preço da promoção (e só isso; o Carregador aplicado na hora não conta): %s' % uso)
        ir(LISTA); clica('.aba-sit[data-sit="todos"]'); clica('#corpoTabela tr[data-id="1"]')
        ok(pg.inner_text('#prVendidoQtd').startswith('2 de 62') and pg.inner_text('#prVendidoValor') == 'R$ 119,80' and 'Pedido de Venda nº' in pg.inner_text('#prPedidos'),
           'o painel da nº 1 conta o pedido salvo: %s, %s' % (pg.inner_text('#prVendidoQtd'), pg.inner_text('#prVendidoValor')))
        ir(PAG, '?id=1')
        ok('2 unidades, R$ 119,80, com o preço dela' in pg.inner_text('#faixaTexto') and 'Pedido de Venda nº' in pg.inner_text('#prFaixaVendas'), 'a página da promoção diz quanto vendeu com o preço dela, e em qual pedido: "%s"' % pg.inner_text('#faixaTexto')[:160])
        ped_novo(1); pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))"); ped_add('PAP-3002', '1')
        ok(itens_ped() == [['PAP-3002', 1, 64.9, None]], 'a mesma cliente, em outro pedido, já levou as 2: preço de venda')
        # --- a permissao mora no cadastro do vendedor
        ir(VEND, '?id=1')
        ok(ev("PODE_CONFIRMAR.promocaoNaHora") is True, 'o perfil da Marina Costa pode confirmar a ação')
        nomes = ev("PODE_NA_HORA_IDS.map(i => REGISTROS.filter(r => r.id === i)[0].nome)")
        ir(VEND, '?id=3'); sem_perm = ev("PODE_CONFIRMAR.promocaoNaHora")
        ir(PDV); esp_pdv = ev("PROMO_PODE_NA_HORA")
        ok(sem_perm is False and nomes == esp_pdv == ['Marina Costa'], 'o do Rafael Andrade não; e o PDV e o Pedido leem o espelho do cadastro: %s' % esp_pdv)
        cat = ev("PROMO_PRODUTOS.filter(p => CATALOGO.some(c => c.sku === p.sku)).map(p => { const c = CATALOGO.filter(x => x.sku === p.sku)[0]; return [p.sku, c.nome === p.nome, c.loja === p.loja, c.preco === p.preco, Object.values(c.saldo).reduce((s, n) => s + n, 0) === p.estoque]; })")
        ok(len(cat) == 8 and all(all(x[1:]) for x in cat), 'os produtos do cadastro no catálogo do PDV têm o nome, a loja, o preço e o estoque da ficha: %s' % [x for x in cat if not all(x[1:])])
        # --- PDV e Pedido nos dois temas, 1280 e 1440
        for w in (1280, 1440):
            pg.set_viewport_size({'width': w, 'height': 900})
            for tema in ('dark', 'light'):
                pdv_abre(1); pdv_add('PAP-3002', '3'); fecha_aviso()
                ev("(t) => document.body.classList.toggle('dark', t === 'dark')", tema)
                r = ev("[document.documentElement.scrollWidth <= innerWidth, getComputedStyle(document.querySelector('.promo-tag-selo')).fontFamily.split(',')[0]]")
                ok(r == [True, 'Nunito'], 'PDV com item em promoção a %d, tema %s: sem barra para o lado, selo em Nunito: %s' % (w, tema, r))
                ped_novo(1); ped_add('PAP-3002', '3')
                ev("(t) => document.body.classList.toggle('dark', t === 'dark')", tema)
                r = ev("[document.documentElement.scrollWidth <= innerWidth, Math.max(0, ...Array.from(document.querySelectorAll('.itens-table-wrap')).map(e => e.scrollWidth - e.clientWidth)) <= 1, getComputedStyle(document.querySelector('.promo-tag-selo')).fontFamily.split(',')[0]]")
                ok(r == [True, True, 'Nunito'], 'Pedido de Venda com a linha dividida a %d, tema %s: sem barra, selo em Nunito: %s' % (w, tema, r))
        pg.set_viewport_size({'width': 1440, 'height': 900})
        limpar()

    limpar()
    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript em toda a suíte: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
