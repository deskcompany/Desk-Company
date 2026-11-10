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
        cop = [bloco(fonte(n), PI, PF) for n in (LISTA, PAG, PROD)]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco PROMOCOES é idêntico na lista, na página da promoção e na ficha do produto')
        MI, MF = '  // ===== PRECO MINIMO: A CONTA DA CALCULADORA', '  // ===== FIM DO BLOCO PRECO MINIMO ====='
        cop = [bloco(fonte(n), MI, MF) for n in (PAG, PROD)]
        ok(cop[0] and cop[0] == cop[1], 'o bloco PRECO MINIMO é idêntico na página da promoção e na ficha do produto (a calculadora)')
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
        PDV = '<div class="flyout-item" data-label="PDV" data-href="../vendas/pagina-vendas-pdv.html">'
        item = re.compile(r'\n[ \t]*' + re.escape(PDV) + r'[^\n]*\n[ \t]*<div class="flyout-item" data-label="Promoções e Encartes" data-href="\.\./vendas/pagina-vendas-promocoes\.html">')
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
        ir(CONF)
        ok('Aprovar uma promoção' in pg.inner_text('.main'), 'Confirmações por senha mostra "Aprovar uma promoção"')
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
        esperado = ev("""(() => { const sku = ['PAP-3002', 'ELE-1003', 'MOB-4001']; let q = 0, v = 0;
            PEDIDOS.filter(p => p.loja === 1 && p.dv <= 10 && p.situacao !== 'cancelado' && ITENS_PEDIDO[p.id]).forEach(p => ITENS_PEDIDO[p.id].forEach(i => { if (sku.includes(i.sku)) { q += i.qtd; v += i.qtd * i.preco; } }));
            return [q, Math.round(v * 100) / 100]; })()""")
        ir(LISTA)
        clica('.aba-sit[data-sit="todos"]'); clica('#corpoTabela tr[data-id="1"]')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')"), 'clicar na linha abre o painel')
        fmt = lambda n: 'R$ ' + '{:,.2f}'.format(n).replace(',', 'X').replace('.', ',').replace('X', '.')
        ok(pg.inner_text('#prVendidoQtd').startswith('%d de 62' % esperado[0]) and pg.inner_text('#prVendidoValor') == fmt(esperado[1]),
           'o painel da nº 1 diz quanto vendeu, igual à conta feita nos Pedidos: %s un., %s (%s; %s)' % (esperado[0], fmt(esperado[1]), pg.inner_text('#prVendidoQtd'), pg.inner_text('#prVendidoValor')))
        links = ev("Array.from(document.querySelectorAll('#prPedidos a')).map(a => a.getAttribute('href'))")
        ok(links == ['../vendas/pagina-vendas-pedidos-detalhe.html?id=3', '../vendas/pagina-vendas-pedidos-detalhe.html?id=8'], 'e leva aos pedidos que somaram: %s' % links)
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
        ok(pg.inner_text('#indicadoresPromocoes [data-kpi="ativas"] .kpi-value') == fmt(esperado[1] + 3 * 39.90), 'o card "Vendido nas ativas" soma a nº 1 e a nº 7')
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

    limpar()
    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript em toda a suíte: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
