# -*- coding: utf-8 -*-
# Estoque -> Necessidades de Compra e Giro de Estoque (10/out/2026).
#
# As duas telas nasceram juntas, de 31 prints do Olist e quatro decisoes do usuario:
#   1. LISTA VIVA, no padrao do sistema: abre ja calculada, com indicadores, abas e painel
#      lateral. Nao ha botao "gerar";
#   2. SO O VENDAVEL conta como estoque na compra (disponivel + aguardando endereco).
#      Reservado e bloqueado ficam de fora, o que esta chegando soma e o que ainda vai sair
#      desconta. O aviso de minimo do Controle de Estoques passou a usar a mesma regra;
#   3. O PAINEL CRIA A ORDEM, uma por fornecedor, e ela aparece em Ordens de Compra;
#   4. O GIRO AVISA NA COMPRA: encalhe abaixo do minimo entra sem quantidade sugerida. As
#      faixas sao parametro da empresa (Parametros de estoque), e a regua do Giro simula.
#
# O que esta suite guarda, alem das quatro decisoes:
#   - as duas telas leem o MESMO bloco de dados e fazem a mesma conta de giro (o texto do
#     bloco e comparado), e PRODUTOS e espelho do Controle de Estoques;
#   - os espelhos de Ordens de Compra e de Transferencia conferem com as telas de origem;
#   - minimo e maximo se editam no painel do produto, nao na linha, e o Controle de Estoques
#     le o novo minimo;
#   - excluir ou cancelar em Ordens de Compra uma ordem criada aqui devolve a necessidade;
#   - o cadastro do produto marca qual fornecedor e o padrao.
#
# Secoes: [1] menu e abertura; [2] bloco comum e espelhos; [3] a conta; [4] so o vendavel,
#   nos dois sentidos; [5] filtros e calculo; [6] o painel da conta, minimo e maximo;
#   [7] a coluna Comprar; [8] ordem de compra; [9] Ordens de Compra le e devolve;
#   [10] o giro; [11] a regua e o aviso na compra, nos dois sentidos; [12] periodo, filtros,
#   painel, planilha e impressao; [13] Parametros de estoque; [14] fornecedor padrao no
#   cadastro do produto; [15] largura, temas, Esc e erros.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, datetime
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

NEC = 'pagina-estoque-necessidades-compra.html'
GIRO = 'pagina-estoque-giro-estoque.html'
CE = 'pagina-estoque-controle-estoques.html'
OC = 'pagina-estoque-ordens-compra.html'
TRANSF = 'pagina-estoque-transferencia.html'
PARAMS = 'pagina-configuracoes-parametros-estoque.html'
PRODUTO = 'pagina-cadastros-produtos-detalhe.html'
DEPOSITOS = 'pagina-cadastros-depositos.html'
CHAVES = ['deskMinMax', 'deskOrdensGeradas', 'deskParametros', 'deskLog']

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clic(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


def visivel(pg, sel):
    return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)


def escolher(pg, raiz, valor):
    """Abre o dropdown e escolhe a opcao, pelo DOM."""
    clic(pg, '#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(100)
    pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
    pg.wait_for_timeout(180)


def modal(pg):
    """Texto do modal de confirmacao aberto, ou '' quando nao ha. Parametros de estoque tem o aviso proprio."""
    if pg.locator('#avisoModal.open').count():
        return pg.inner_text('#avisoTexto')
    return pg.inner_text('#confirmModalTexto') if pg.locator('#confirmModal.open').count() else ''


def confirmar(pg):
    """Confirma o modal aberto, com a senha quando a tela pede. Serve tambem para fechar aviso."""
    if pg.locator('#avisoModal.open').count():
        clic(pg, '#btnAvisoOk'); pg.wait_for_timeout(300)
    if pg.locator('#confirmModal.open').count():
        pg.evaluate("() => { const c = document.querySelector('#confirmModal input[type=checkbox]'); if (c && c.offsetParent !== null && !c.checked) c.click(); }")
        if visivel(pg, '#campoSenhaModal'):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)


def ir(pg, tela, query=''):
    pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)


def zerar(pg, tela=NEC, param=None):
    """Comeca do zero: sem minimo alterado, sem ordem gerada, sem registro e com os parametros pedidos."""
    ir(pg, tela)
    pg.evaluate("([chaves, p]) => { chaves.forEach(k => localStorage.removeItem(k)); if (p) localStorage.setItem('deskParametros', JSON.stringify(p)); }", [CHAVES, param])
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)


def abas(pg):
    return pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('#abasSituacao .aba-sit')).map(a => [a.getAttribute('data-sit'), Number(a.querySelector('.sit-contador').textContent)]))")


def aba(pg, nome):
    clic(pg, '#abasSituacao .aba-sit[data-sit="%s"]' % nome); pg.wait_for_timeout(150)


def skus(pg):
    return pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => tr.getAttribute('data-sku'))")


def garantir(pg, sku):
    """A linha pedida pode estar na segunda pagina: passa para 25 por pagina quando ela nao esta na tela."""
    if not pg.evaluate("(s) => !!document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"]')", sku):
        escolher(pg, 'itensPorPagina', 25)


def linha(pg, sku):
    garantir(pg, sku)
    return pg.evaluate("(s) => { const tr = document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"]'); return tr ? tr.innerText.replace(/\\s+/g, ' ') : null; }", sku)


def conta(pg, sku):
    """O retrato que a tela de compra calcula para o produto, sem o que nao serializa."""
    return pg.evaluate("""(s) => { const r = retrato(produtoDe(s)); return { vendavel: r.vendavel, chegando: r.chegando, saidas: r.saidas, projetado: r.projetado,
        min: r.min, max: r.max, sugestao: r.sugestao, comprar: r.comprar, segurado: r.segurado, classe: r.classe, abaixoMin: r.abaixoMin, emFalta: r.emFalta,
        bloqueado: r.bloqueado, disp: r.disp, aEnd: r.aEnd, emConf: r.emConf, deOc: r.deOc, deTransf: r.deTransf }; }""", sku)


def campo_comprar(pg, sku):
    garantir(pg, sku)
    return pg.evaluate("(s) => { const c = document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"] .nc-qtd'); return c ? c.value : null; }", sku)


def digitar_comprar(pg, sku, valor):
    garantir(pg, sku)
    pg.evaluate("([s, v]) => { const c = document.querySelector('#corpoTabela tr[data-sku=\"' + s + '\"] .nc-qtd'); c.value = v; c.dispatchEvent(new Event('change', { bubbles: true })); }", [sku, valor])
    pg.wait_for_timeout(150)


def abrir_conta(pg, sku):
    garantir(pg, sku)
    clic(pg, '#corpoTabela tr[data-sku="%s"] td:nth-child(2)' % sku); pg.wait_for_timeout(350)


def opcoes(pg, modo=None, cobertura=None, saidas=None, situacoes=None, transf=None, cod=None, marca=None, tipo=None):
    """Abre Filtros e calculo, ajusta o que foi pedido e aplica."""
    clic(pg, '#btnOpcoes'); pg.wait_for_timeout(300)
    if modo:
        clic(pg, '#opModo button[data-modo="%s"]' % modo)
    if cobertura is not None:
        pg.fill('#opCoberturaDias', str(cobertura))
    for ident, valor in [('opSaidas', saidas), ('opTransf', transf), ('opCodForn', cod)]:
        if valor is not None and pg.evaluate("(i) => document.getElementById(i).classList.contains('on')", ident) != valor:
            clic(pg, '#' + ident)
    if situacoes is not None:
        pg.evaluate("(l) => document.querySelectorAll('#opSituacoes input').forEach(i => { if (i.checked !== l.includes(i.value)) i.click(); })", situacoes)
    if marca:
        escolher(pg, 'opMarca', marca)
    if tipo:
        escolher(pg, 'opTipo', tipo)
    clic(pg, '#btnAplicarOpcoes'); pg.wait_for_timeout(300)


def guardadas(pg):
    return pg.evaluate("JSON.parse(localStorage.getItem('deskOrdensGeradas') || '[]')")


def mover_regua(pg, campo, valor):
    pg.evaluate("([c, v]) => { const e = document.getElementById(c); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); }", [campo, valor])
    pg.wait_for_timeout(150)


def cabe(pg, painel):
    return pg.evaluate("(p) => { const w = document.querySelector('#' + p + ' .estoque-table-wrap'); return w.scrollWidth <= w.clientWidth + 1; }", painel)


def bloco_comum(tela):
    t = open(localiza.onde(tela), encoding='utf-8').read()
    a = t.index('  // ===== COMPRA E GIRO: BLOCO COMUM =====')
    return t[a:t.index('  // ===== ', a + 10)]


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    # Contexto explicito: as telas de compra, o Controle de Estoques e Ordens de Compra dividem o armazenamento.
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('\n[1] Menu e abertura')
    destinos = {'Necessidades de Compra': NEC, 'Giro de Estoque': GIRO}
    sem = []
    for c in localiza.caminhos():
        t = open(c, encoding='utf-8').read()
        for rotulo, arq in destinos.items():
            if t.count('data-label="%s"' % rotulo) != t.count('data-label="%s" data-href="../estoque/%s"' % (rotulo, arq)) or 'data-label="%s"' % rotulo not in t:
                sem.append(_os.path.basename(c) + ' / ' + rotulo)
    ok(len(localiza.caminhos()) >= 81 and not sem, 'toda tela leva o menu as duas telas novas: %d telas, faltando %s' % (len(localiza.caminhos()), sem[:3]))
    zerar(pg)
    ok(pg.inner_text('h1') == 'Necessidades de Compra' and 'Estoque' in pg.inner_text('#breadcrumb') and 'Necessidades de Compra' in pg.inner_text('#breadcrumb'),
       'Necessidades de Compra abre com o titulo e o caminho de Estoque')
    ok(pg.evaluate("(() => { const a = document.querySelector('.nav-item.active'); return a ? a.getAttribute('data-label') : ''; })()") == 'Estoque', 'e o menu lateral marca Estoque')
    ok(len(skus(pg)) == 10 and pg.locator('#btnGerar, button#gerar').count() == 0, 'a lista ja abre calculada, sem botao "gerar": 10 linhas na primeira pagina')
    ir(pg, GIRO)
    ok(pg.inner_text('h1') == 'Giro de Estoque' and pg.evaluate("(() => { const a = document.querySelector('.nav-item.active'); return a ? a.getAttribute('data-label') : ''; })()") == 'Estoque',
       'Giro de Estoque abre com o titulo e o menu em Estoque')
    clic(pg, '.flyout-item[data-label="Necessidades de Compra"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
    ok(pg.url.endswith(NEC), 'o item do menu navega de verdade: %s' % pg.url.split('/')[-1])

    print('\n[2] Bloco comum e espelhos')
    ok(bloco_comum(NEC) == bloco_comum(GIRO) and len(bloco_comum(NEC)) > 8000, 'o bloco de dados e de giro e identico nas duas telas (%d caracteres)' % len(bloco_comum(NEC)))
    ok('const DEPOSITOS' in bloco_comum(NEC), 'e a comparacao nao passou por bloco truncado (injetar uma diferenca num dos lados reprova a linha acima)')
    forma = "PRODUTOS.map(p => [p.id, p.sku, p.nome, p.gtin, p.tipo, p.custoMedio, p.unidade, p.saldos.map(s => [s.dep, s.endereco, s.estagio, s.qtd])])"
    ir(pg, CE); pg.evaluate("localStorage.removeItem('deskMinMax')"); pg.reload(); pg.wait_for_timeout(400)
    do_ce = pg.evaluate(forma)
    minimos_ce = pg.evaluate("Object.fromEntries(PRODUTOS.map(p => [p.sku, p.minimo]))")
    ir(pg, NEC)
    ok(pg.evaluate(forma) == do_ce and len(do_ce) == 15, 'PRODUTOS e o mesmo do Controle de Estoques: 15 produtos, com saldo por deposito, endereco e estagio')
    ok(pg.evaluate("Object.fromEntries(PRODUTOS.map(p => [p.sku, p.minimo]))") == minimos_ce, 'e com o mesmo estoque minimo')
    ok(pg.evaluate("PRODUTOS.every(p => FICHA[p.sku] && LOJAS[FICHA[p.sku].loja] && (FICHA[p.sku].fornecedor === null || FORNECEDORES[FICHA[p.sku].fornecedor]))"),
       'todo produto tem ficha de compra, com loja e fornecedor que existem')
    ok(pg.evaluate("""PRODUTOS.every(p => { const piso = Math.min(0, fisicoDe(p)); for (let t = 0; t <= 366; t++) { if (saldoHa(p, t) < piso - 0.0001) return false; } return true; })"""),
       'o movimento fecha: em nenhum dia do ultimo ano o saldo de um produto fica abaixo de zero')
    espelho_oc = pg.evaluate("OC_A_RECEBER.map(o => [o.numero, o.fornecedor, o.dep, o.previsto, o.sku, o.qtd, o.recebido]).sort()")
    espelho_tr = pg.evaluate("TRANSF_TRANSITO.map(t => [t.num, t.origem, t.destino, t.sku, t.qtd]).sort()")
    nomes_forn = pg.evaluate("Object.values(FORNECEDORES).sort()")
    conhecidos = pg.evaluate("PRODUTOS.map(p => p.sku)")
    primeiro = pg.evaluate("PRIMEIRO_NUMERO_OC")
    principal = pg.evaluate("DEPOSITO_PRINCIPAL")
    ir(pg, OC)
    da_oc = pg.evaluate("""(skus) => { const l = []; ORDENS.filter(o => o.situacao === 'aberto' || o.situacao === 'andamento').forEach(o => (ITENS_OC[o.id] || []).forEach(i => {
        if (skus.includes(i.sku) && i.qtd > i.recebido) l.push([o.numero, o.fornecedor, o.dep, o.previsto, i.sku, i.qtd, i.recebido]); })); return l.sort(); }""", conhecidos)
    ok(espelho_oc == da_oc and len(da_oc) == 4, 'o que falta receber e espelho de Ordens de Compra: %d linhas de ordens em aberto e em andamento' % len(da_oc))
    ok(pg.evaluate("Math.max.apply(null, ORDENS.map(o => o.numero))") + 1 == primeiro, 'e a primeira ordem criada aqui continua a numeracao de la: %d' % primeiro)
    ok(set(nomes_forn) == set(pg.evaluate("Array.from(new Set(ORDENS.map(o => o.fornecedor))).sort()")), 'os fornecedores sao os mesmos de Ordens de Compra')
    ir(pg, TRANSF)
    da_tr = pg.evaluate("""(() => { const l = []; TRANSFERENCIAS.filter(t => t.situacao === 'transito' || t.situacao === 'parcial').forEach(t => t.itens.forEach(i => {
        if (i.enviado > i.recebido) l.push([t.num, t.origem, t.destino, i.sku, i.enviado - i.recebido]); })); return l.sort(); })()""")
    ok(espelho_tr == da_tr and len(da_tr) == 3, 'o que esta em transito e espelho de Transferencia Entre Estoques: %d linhas' % len(da_tr))
    dep_txt = open(localiza.onde(DEPOSITOS), encoding='utf-8').read()
    ok(re.search(r"\{ id: %d, nome: 'Geral'[^}]*principal: true" % principal, dep_txt) is not None, 'e o deposito de entrega padrao e o principal de Cadastros -> Depositos')

    print('\n[3] A conta')
    zerar(pg)
    ok(abas(pg) == {'todos': 15, 'comprar': 4, 'minimo': 6, 'falta': 2, 'segurados': 1}, 'as abas contam: %s' % abas(pg))
    ok(pg.inner_text('#kpiComprar') == '4' and pg.inner_text('#kpiValor') == 'R$ 18.992,80' and pg.inner_text('#kpiFalta') == '2' and pg.inner_text('#kpiSegurados') == '1',
       'e os indicadores dizem o mesmo: 4 a comprar, R$ 18.992,80, 2 em falta, 1 segurado')
    ok('2 fornecedores' in pg.inner_text('#kpiValorSub') and '1 sem fornecedor padrão' in pg.inner_text('#kpiValorSub'), 'a compra sugerida diz em quantos fornecedores esta: %s' % pg.inner_text('#kpiValorSub'))
    sup = conta(pg, 'SUP-MON-003')
    ok((sup['vendavel'], sup['chegando'], sup['saidas'], sup['projetado'], sup['comprar']) == (2, 6, 3, 5, 19),
       'Suporte: vendavel 2, chegando 6 da ordem 12, 3 a sair, projetado 5, abaixo do minimo 8: comprar 19 ate o maximo 24')
    ok(conta(pg, 'MES-SLM-002')['comprar'] == 16 and conta(pg, 'CAM-DKB-012')['comprar'] == 60 and conta(pg, 'FON-BLT-013')['comprar'] == 32,
       'Mesa 16, Camiseta M 60 e Fone 32 (saldo negativo: a compra cobre o buraco e vai ao maximo)')
    tec = conta(pg, 'MAT-TEC-008')
    ok(tec['abaixoMin'] and tec['comprar'] == 0 and tec['chegando'] == 36, 'Tecido: abaixo do minimo hoje, mas os 36 m da ordem 4 cobrem. Nada a comprar')
    aba(pg, 'comprar')
    ok(skus(pg) == ['CAM-DKB-012', 'FON-BLT-013', 'SUP-MON-003', 'MES-SLM-002'], 'a aba A comprar lista os quatro, da maior quantidade para a menor: %s' % skus(pg))
    ok(campo_comprar(pg, 'SUP-MON-003') == '19' and 'TechParts Distribuidora' in linha(pg, 'SUP-MON-003') and 'R$ 138,40' in linha(pg, 'SUP-MON-003'),
       'a linha traz fornecedor padrao, custo medio e a quantidade num campo: %s' % linha(pg, 'SUP-MON-003'))
    ok('sem fornecedor padrão' in linha(pg, 'CAM-DKB-012'), 'produto sem fornecedor padrao diz isso na linha')
    aba(pg, 'falta')
    ok(sorted(skus(pg)) == ['CAM-DKB-012', 'FON-BLT-013'], 'Em falta: o zerado e o negativo')
    aba(pg, 'segurados')
    ok(skus(pg) == ['LUM-LED-004'] and campo_comprar(pg, 'LUM-LED-004') == '' and 'segurado pelo giro' in linha(pg, 'LUM-LED-004') and 'encalhe' in linha(pg, 'LUM-LED-004').lower(),
       'Segurados pelo giro: a Luminaria, com o campo vazio e o aviso na linha')
    ok(conta(pg, 'LUM-LED-004')['sugestao'] == 33 and conta(pg, 'LUM-LED-004')['comprar'] == 0, 'a conta dela pediria 33; a sugestao fica em zero')
    aba(pg, 'todos')
    ok('Conta por mínimo e máximo' in pg.inner_text('#avisoConta') and 'Aprovado' in pg.inner_text('#avisoConta') and 'Em aberto' not in pg.inner_text('#avisoConta'),
       'o aviso do topo da lista diz como a conta esta sendo feita')

    print('\n[4] So o vendavel, nos dois sentidos')
    mon = conta(pg, 'MON-27I-015')
    ok((mon['disp'], mon['aEnd'], mon['bloqueado'], mon['vendavel']) == (2, 5, 2, 7), 'Monitor: 2 disponiveis + 5 aguardando endereco = 7 vendaveis; os 2 bloqueados ficam de fora')
    ok(conta(pg, 'KIT-HOF-005')['vendavel'] == 4 and conta(pg, 'KIT-HOF-005')['bloqueado'] == 1, 'Kit Home Office: 4 vendaveis, 1 bloqueado fora da conta')
    abaixo_nec = sorted(pg.evaluate("baseFiltrada().filter(r => r.abaixoMin).map(r => r.p.sku)"))
    ir(pg, CE)
    abaixo_ce = sorted(pg.evaluate("PRODUTOS.filter(abaixoDoMinimo).map(p => p.sku)"))
    ok(abaixo_nec == abaixo_ce and len(abaixo_ce) == 6, 'a aba Abaixo do minimo e o aviso do Controle de Estoques apontam os mesmos 6 produtos')
    clic(pg, '.dropdown-select-item[data-value="abaixo_minimo"]'); pg.wait_for_timeout(250)
    ok(pg.locator('#corpoTabela tr').count() == 6 if pg.locator('#corpoTabela').count() else pg.locator('tbody tr').count() == 6, 'e o filtro "abaixo do minimo" de la mostra 6 linhas')
    # O caso que separa as duas regras: minimo 8 para o Monitor. Fisico 9 (com 2 bloqueados), vendavel 7.
    pg.evaluate("localStorage.setItem('deskMinMax', JSON.stringify({ 'MON-27I-015': { minimo: 8, maximo: 14 } }))"); pg.reload(); pg.wait_for_timeout(400)
    ok(pg.evaluate("(() => { const m = PRODUTOS.find(p => p.sku === 'MON-27I-015'); return [m.minimo, saldoDe(m), abaixoDoMinimo(m)]; })()") == [8, 9, True],
       'com minimo 8 o Monitor entra no aviso do Controle de Estoques: fisico 9, mas so 7 vendaveis (pela regra antiga, do fisico, ele nao entraria)')
    ir(pg, NEC)
    mon = conta(pg, 'MON-27I-015')
    ok(mon['abaixoMin'] and mon['min'] == 8 and abas(pg)['minimo'] == 7, 'e entra na aba Abaixo do minimo daqui: agora sao 7')
    ok(mon['projetado'] == 11 and mon['comprar'] == 0, 'sem compra sugerida, porque os 4 em conferencia levam o projetado a 11')
    pg.evaluate("localStorage.removeItem('deskMinMax')"); pg.reload(); pg.wait_for_timeout(400)
    ok(abas(pg)['minimo'] == 6 and not conta(pg, 'MON-27I-015')['abaixoMin'], 'sem o minimo alterado, voltam os 6')

    print('\n[5] Filtros e calculo')
    escolher(pg, 'filtroLoja', 3)
    ok(abas(pg)['todos'] == 6 and pg.inner_text('#kpiComprar') == '2', 'loja Desk Tech: 6 produtos, 2 a comprar. Os indicadores acompanham o filtro')
    escolher(pg, 'filtroLoja', 'todos'); escolher(pg, 'filtroFornecedor', 'sem')
    ok(sorted(skus(pg)) == ['CAM-DKB-011', 'CAM-DKB-012'], 'fornecedor "sem fornecedor padrao": as duas camisetas')
    escolher(pg, 'filtroFornecedor', 'todos'); escolher(pg, 'filtroDeposito', 4)
    ok(sorted(skus(pg)) == ['KIT-MNT-010', 'SUP-MON-003', 'TEC-MEC-006'] and 'depósito escolhido' in pg.inner_text('#avisoConta'),
       'deposito Bancada Desk Tech: so os 3 produtos com saldo la, e o aviso lembra que o minimo e do produto inteiro')
    ok(conta(pg, 'TEC-MEC-006')['vendavel'] == 6, 'e o saldo passa a ser so o do deposito: 6 teclados')
    escolher(pg, 'filtroDeposito', 'todos')
    pg.fill('#campoBusca', 'cab-hdm'); pg.wait_for_timeout(200)
    ok(skus(pg) == ['CAB-HDM-009'], 'busca por SKU')
    pg.fill('#campoBusca', 'tecidos ceará'); pg.wait_for_timeout(200)
    ok(skus(pg) == ['MAT-TEC-008'], 'e por nome do fornecedor')
    pg.fill('#campoBusca', 'nada disso existe'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#emptyState') and not visivel(pg, '#painelCompra .estoque-table-wrap'), 'busca sem resultado mostra a lista vazia')
    clic(pg, '#btnLimparFiltros'); pg.wait_for_timeout(250)
    ok(abas(pg)['todos'] == 15 and pg.input_value('#campoBusca') == '', '"Limpar filtros" devolve os 15')
    ok(not visivel(pg, '#contOpcoes'), 'no padrao, o botao Filtros e calculo nao mostra contador')
    opcoes(pg, saidas=False)
    ok(abas(pg)['comprar'] == 2 and conta(pg, 'MES-SLM-002')['comprar'] == 0 and conta(pg, 'SUP-MON-003')['comprar'] == 0 and 'não' in pg.inner_text('#avisoConta'),
       'sem descontar os pedidos que vao sair, Mesa e Suporte deixam de precisar de compra: sobram 2')
    ok(visivel(pg, '#contOpcoes') and pg.inner_text('#contOpcoes') == '1', 'e o botao avisa que ha 1 ajuste fora do padrao')
    opcoes(pg, saidas=True, situacoes=['aberto', 'aprovado', 'separacao', 'conferenciasaida', 'faturado', 'prontoenvio'])
    ok(conta(pg, 'CAM-DKB-012')['comprar'] == 66 and conta(pg, 'CAM-DKB-012')['saidas'] == 6, 'contando tambem os pedidos em aberto, a Camiseta M sobe para 66')
    opcoes(pg, situacoes=['aprovado', 'separacao', 'conferenciasaida', 'faturado', 'prontoenvio'], transf=False)
    ok(conta(pg, 'TEC-MEC-006')['chegando'] == 18 and conta(pg, 'TEC-MEC-006')['deTransf'] == 0, 'sem as transferencias em transito, o Teclado tem 18 chegando')
    opcoes(pg, transf=True)
    ok(conta(pg, 'TEC-MEC-006')['chegando'] == 26, 'com elas, 26: os 18 da ordem 2 e os 8 da TR-0101')
    opcoes(pg, cod=True)
    ok('cód. TP-88213' in linha(pg, 'SUP-MON-003'), 'ligando "codigo no fornecedor", ele aparece sob o fornecedor padrao')
    tema_antes = pg.evaluate("document.body.className")
    clic(pg, '#btnOpcoes'); pg.wait_for_timeout(250); clic(pg, '#opModo button[data-modo="cobertura"]'); pg.wait_for_timeout(150)
    ok(pg.evaluate("document.body.className") == tema_antes and visivel(pg, '#campoCobertura'),
       'o seletor "minimo e maximo / dias de cobertura" usa o visual do seletor de tema, mas nao troca o tema da tela')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    opcoes(pg, cod=False, modo='cobertura', cobertura=30)
    ok(pg.text_content('#rotColA') == 'Venda por dia' and pg.text_content('#rotColB') == 'Cobertura' and 'dias de cobertura' in pg.inner_text('#avisoConta'),
       'por dias de cobertura, as colunas de minimo e maximo dao lugar a venda por dia e cobertura')
    ok(abas(pg)['comprar'] == 2 and conta(pg, 'FON-BLT-013')['comprar'] == 7 and conta(pg, 'CAM-DKB-012')['comprar'] == 8,
       'cobrir 30 dias: Fone 7 (4,5 de venda mais os 2 negativos) e Camiseta M 8')
    clic(pg, '#btnOpcoes'); pg.wait_for_timeout(250); pg.fill('#opCoberturaDias', '0'); clic(pg, '#btnAplicarOpcoes'); pg.wait_for_timeout(200)
    ok(pg.locator('#eventDrawer.open').count() == 1 and visivel(pg, '#erroCobertura'), 'cobertura de 0 dias nao passa: o painel fica aberto com o erro')
    clic(pg, '#btnPadraoOpcoes'); pg.wait_for_timeout(300)
    ok(abas(pg)['comprar'] == 4 and pg.text_content('#rotColA') == 'Mínimo' and not visivel(pg, '#contOpcoes'), '"Voltar ao padrao" refaz a conta por minimo e maximo')
    opcoes(pg, tipo='materia_prima')
    ok(sorted(skus(pg)) == ['MAT-MDF-007', 'MAT-PAR-014', 'MAT-TEC-008'], 'tipo Materia-prima, no painel: 3 produtos')
    opcoes(pg, tipo='todos', marca='Desk Tech')
    ok(abas(pg)['todos'] == 5, 'marca Desk Tech, no painel: 5 produtos')
    clic(pg, '#btnLimparFiltros'); pg.wait_for_timeout(250)

    print('\n[6] O painel da conta, minimo e maximo')
    abrir_conta(pg, 'SUP-MON-003')
    txt = pg.inner_text('#drawerCorpo')
    ok(pg.locator('#eventDrawer.open').count() == 1 and pg.inner_text('#drawerTitulo') == 'A conta da compra' and 'Suporte Monitor Duplo' in txt, 'clicar na linha abre a conta do produto')
    ok('Ordem nº 12' in txt and 'Pedido nº 43' in txt and 'Aprovado' in txt, 'a conta mostra de onde vem cada numero: a ordem que esta chegando e o pedido que vai sair')
    ok('abaixo do mínimo de 8 UN' in pg.inner_text('#contaResultado') and '19 UN' in pg.inner_text('#contaResultado') and 'máximo de 24 UN' in pg.inner_text('#contaResultado'),
       'e diz o resultado por extenso: %s' % pg.inner_text('#contaResultado'))
    ok(pg.input_value('#inputMin') == '8' and pg.input_value('#inputMax') == '24', 'minimo e maximo vem preenchidos, no painel e nao na linha')
    pg.fill('#inputMin', '30'); clic(pg, '#btnSalvarMinMax'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroMinMax') and 'máximo' in pg.inner_text('#erroMinMax') and conta(pg, 'SUP-MON-003')['min'] == 8, 'maximo menor que o minimo nao salva')
    pg.fill('#inputMin', '2,5'); pg.fill('#inputMax', '24'); clic(pg, '#btnSalvarMinMax'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroMinMax') and 'inteiras' in pg.inner_text('#erroMinMax'), 'nem meia unidade em produto contado por unidade')
    pg.fill('#inputMin', '4'); clic(pg, '#btnSalvarMinMax'); pg.wait_for_timeout(350)
    ok(conta(pg, 'SUP-MON-003')['min'] == 4 and conta(pg, 'SUP-MON-003')['comprar'] == 0 and 'Nada a comprar' in pg.inner_text('#contaResultado'),
       'minimo 4: o projetado de 5 passa a cobrir, e o painel ja mostra a conta nova')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('deskMinMax'))") == {'SUP-MON-003': {'minimo': 4, 'maximo': 24}}, 'o novo minimo fica guardado')
    ok(any(l.get('chave') == 'produtosEditar' and 'SUP-MON-003' in l.get('detalhe', '') for l in pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")),
       'e a alteracao vai para o registro de atividades')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    ok(pg.locator('#eventDrawer.open').count() == 0 and abas(pg)['comprar'] == 3, 'Esc fecha o painel; a lista ja esta com 3 a comprar')
    pg.reload(); pg.wait_for_timeout(400)
    ok(conta(pg, 'SUP-MON-003')['min'] == 4, 'F5 nao desfaz')
    ir(pg, CE)
    ok(pg.evaluate("PRODUTOS.find(p => p.sku === 'SUP-MON-003').minimo") == 4, 'e o Controle de Estoques passa a mostrar o mesmo minimo')
    ir(pg, NEC)
    abrir_conta(pg, 'LUM-LED-004')
    ok(pg.locator('#contaResultado.alerta').count() == 1 and 'encalhe' in pg.inner_text('#contaResultado') and '33 UN' in pg.inner_text('#contaResultado'),
       'a conta da Luminaria explica por que a sugestao foi segurada')
    ok(pg.get_attribute('#drawerCorpo a[href*="giro-estoque"]', 'href').endswith('pagina-estoque-giro-estoque.html?busca=LUM-LED-004'), 'e leva ao Giro de Estoque ja no produto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    abrir_conta(pg, 'MON-27I-015')
    ok('Itens Bloqueados' in pg.inner_text('#drawerCorpo') and pg.get_attribute('#drawerCorpo a[href*="itens-bloqueados"]', 'href').endswith('?produto=MON-27I-015'),
       'produto com saldo bloqueado mostra o bloqueado fora da conta e leva a Itens Bloqueados')
    ok(re.search(r'Estoque físico[^0-9]*9 UN', pg.inner_text('#drawerCorpo').replace(chr(10), ' ')) is not None, 'e o painel mostra o estoque fisico, 9: os 7 vendaveis mais os 2 bloqueados')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    pg.evaluate("localStorage.removeItem('deskMinMax')"); pg.reload(); pg.wait_for_timeout(400)

    print('\n[7] A coluna Comprar')
    digitar_comprar(pg, 'SUP-MON-003', '25')
    ok(conta(pg, 'SUP-MON-003')['comprar'] == 25 and 'pela conta: 19' in linha(pg, 'SUP-MON-003') and pg.inner_text('#kpiValor') == 'R$ 19.823,20',
       'digitar 25 no Suporte vale no lugar da sugestao, a linha lembra que a conta dava 19 e o total acompanha')
    digitar_comprar(pg, 'SUP-MON-003', 'abc')
    ok(pg.evaluate("document.querySelector('tr[data-sku=\"SUP-MON-003\"] .nc-qtd').classList.contains('has-error')") and conta(pg, 'SUP-MON-003')['comprar'] == 25,
       'texto que nao e quantidade marca o campo e nao muda nada')
    digitar_comprar(pg, 'SUP-MON-003', '19')
    ok('pela conta' not in linha(pg, 'SUP-MON-003') and pg.inner_text('#kpiValor') == 'R$ 18.992,80', 'digitar o numero da conta volta a ser a conta')
    digitar_comprar(pg, 'MAT-TEC-008', '12,5')
    ok(conta(pg, 'MAT-TEC-008')['comprar'] == 12.5, 'produto vendido por metro aceita 12,5')
    digitar_comprar(pg, 'MAT-TEC-008', '')
    digitar_comprar(pg, 'LUM-LED-004', '10')
    ok(abas(pg)['segurados'] == 0 and abas(pg)['comprar'] == 5 and 'segurada' in linha(pg, 'LUM-LED-004'), 'digitar na Luminaria e a decisao de comprar mesmo assim: ela sai dos segurados e entra em A comprar')
    digitar_comprar(pg, 'LUM-LED-004', '')
    ok(abas(pg)['segurados'] == 1 and abas(pg)['comprar'] == 4, 'apagar devolve o produto aos segurados')

    print('\n[8] Ordem de compra')
    clic(pg, '#btnGerarOrdem'); pg.wait_for_timeout(300)
    ok('Marque na lista' in modal(pg) and pg.locator('#eventDrawer.open').count() == 0, 'sem nada marcado, o botao avisa em vez de abrir uma ordem vazia')
    confirmar(pg)
    aba(pg, 'comprar')
    clic(pg, '#checkSelecionarTodos'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#barraSelecao') and '4 produtos selecionados' in pg.inner_text('#selecaoInfo') and 'R$ 18.992,80' in pg.inner_text('#selecaoInfo'),
       'marcar todos mostra a barra no rodape da lista, com a soma: %s' % pg.inner_text('#selecaoInfo'))
    clic(pg, '#btnGerarSelecionados'); pg.wait_for_timeout(350)
    titulos = pg.evaluate("Array.from(document.querySelectorAll('.nc-grupo')).map(g => g.querySelector('.dropdown-select-label').textContent)")
    ok(pg.inner_text('#drawerTitulo') == 'Ordem de compra' and titulos == ['Móveis Nordeste Ltda', 'TechParts Distribuidora', 'Selecione o fornecedor'],
       'o painel separa por fornecedor padrao: %s' % titulos)
    ok(pg.inner_text('#btnConfirmarOrdem') == 'Gerar 3 ordens de compra' and pg.inner_text('#ocTotalGeral') == 'R$ 18.992,80', 'e ja diz quantas ordens vao nascer e o total')
    clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#ocErro2') and 'Selecione o fornecedor' in pg.inner_text('#ocErro2') and guardadas(pg) == [] and pg.locator('#eventDrawer.open').count() == 1,
       'bloco sem fornecedor trava tudo: nenhuma ordem nasce pela metade')
    escolher(pg, 'ocForn2', 1)
    ok(pg.inner_text('#btnConfirmarOrdem') == 'Gerar 2 ordens de compra' and not visivel(pg, '#ocErro2'), 'escolhendo TechParts, os dois blocos dela viram uma ordem so: 2 ordens')
    pg.fill('#ocPrev0', '99/99/2026'); clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#ocErro0') and 'inválida' in pg.inner_text('#ocErro0') and guardadas(pg) == [], 'data prevista invalida nao passa')
    pg.fill('#ocPrev0', '01/01/2020'); clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#ocErro0') and 'anterior a hoje' in pg.inner_text('#ocErro0'), 'nem data no passado')
    futuro = (datetime.date.today() + datetime.timedelta(days=12))
    pg.fill('#ocPrev0', futuro.strftime('%d/%m/%Y'))
    pg.evaluate("(() => { const c = document.querySelector('.nc-itens .nc-qtd[data-grupo=\"1\"][data-item=\"0\"]'); c.value = '0'; c.dispatchEvent(new Event('input', { bubbles: true })); })()")
    clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#ocErro1') and 'quantidade' in pg.inner_text('#ocErro1') and guardadas(pg) == [], 'nem item com quantidade zero')
    pg.evaluate("(() => { const c = document.querySelector('.nc-itens .nc-qtd[data-grupo=\"1\"][data-item=\"0\"]'); c.value = '32'; c.dispatchEvent(new Event('input', { bubbles: true })); })()")
    clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(500)
    aviso = modal(pg)
    ok('2 ordens de compra foram criadas com sucesso' in aviso and 'nº 15 para Móveis Nordeste Ltda (R$ 8.204,00)' in aviso and 'nº 16 para TechParts Distribuidora (R$ 10.788,80)' in aviso,
       'as duas ordens nascem e o aviso diz quais: %s' % aviso[:150])
    confirmar(pg)
    g = guardadas(pg)
    ok([(o['numero'], o['fornecedor'], o['situacao'], o['previsto'], o['total']) for o in g] ==
       [(15, 'Móveis Nordeste Ltda', 'aberto', futuro.isoformat(), 8204.0), (16, 'TechParts Distribuidora', 'aberto', '', 10788.8)],
       'ficam guardadas em aberto, com fornecedor, data prevista e total')
    ok(sorted(i['sku'] for i in g[1]['itens']) == ['CAM-DKB-012', 'FON-BLT-013', 'SUP-MON-003'] and all(i['recebido'] == 0 for o in g for i in o['itens']),
       'a da TechParts leva os tres produtos, a camiseta inclusive')
    ok(abas(pg)['comprar'] == 0 and conta(pg, 'SUP-MON-003')['chegando'] == 25 and conta(pg, 'MES-SLM-002')['chegando'] == 22 and not visivel(pg, '#barraSelecao'),
       'o que foi pedido passa a contar como chegando: nada mais a comprar, e a selecao se desfaz')
    ok(any(l.get('chave') == 'ordensCompraCriar' for l in pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")), 'a criacao vai para o registro de atividades')
    aba(pg, 'todos')
    abrir_conta(pg, 'SUP-MON-003')
    ok('Ordem nº 16' in pg.inner_text('#drawerCorpo') and 'Ordem nº 12' in pg.inner_text('#drawerCorpo'), 'e a conta do Suporte lista a ordem nova ao lado da antiga')
    clic(pg, '#btnOrdemDoProduto'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#drawerTitulo') == 'Ordem de compra' and pg.locator('.nc-grupo').count() == 1 and pg.inner_text('#btnConfirmarOrdem') == 'Gerar ordem de compra',
       'do painel da conta da para abrir a ordem so daquele produto')
    clic(pg, '.nc-x'); pg.wait_for_timeout(250)
    ok(pg.locator('#eventDrawer.open').count() == 0 and len(guardadas(pg)) == 2, 'tirar o unico item fecha o painel sem criar nada')

    print('\n[9] Ordens de Compra le e devolve')
    ir(pg, OC)
    ok(pg.evaluate("ORDENS.length") == 16 and pg.evaluate("ORDENS.filter(o => o.numero >= 15).map(o => [o.numero, o.fornecedor, o.situacao, o.total])") ==
       [[15, 'Móveis Nordeste Ltda', 'aberto', 8204], [16, 'TechParts Distribuidora', 'aberto', 10788.8]], 'as duas ordens aparecem em Ordens de Compra, em aberto')
    topo = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).slice(0, 2).map(tr => tr.innerText.replace(/\\s+/g, ' '))")
    ok('16' in topo[0] and 'TechParts Distribuidora' in topo[0] and '10.788,80' in topo[0] and 'Móveis Nordeste Ltda' in topo[1] and '8.204,00' in topo[1],
       'no topo da lista, com fornecedor e total: %s' % topo[0][:80])
    ok(pg.evaluate("ITENS_OC[16].map(i => [i.sku, i.qtd, i.recebido])") == [['FON-BLT-013', 32, 0], ['SUP-MON-003', 19, 0], ['CAM-DKB-012', 60, 0]], 'com os itens e as quantidades')
    pg.evaluate("document.querySelector('#corpoTabela .item-checkbox[data-id=\"15\"]').click()"); pg.wait_for_timeout(150)
    clic(pg, '#btnCancelarSelecionadas'); pg.wait_for_timeout(300); confirmar(pg)
    ok([o['numero'] for o in guardadas(pg)] == [16], 'cancelar a 15 la tira a ordem do que a compra enxerga')
    ir(pg, NEC)
    ok(conta(pg, 'MES-SLM-002')['comprar'] == 16 and abas(pg)['comprar'] == 1, 'e a necessidade da Mesa volta')
    ir(pg, OC)
    ok(pg.evaluate("ORDENS.some(o => o.numero === 15)") is False, 'a ordem cancelada nao volta a lista ao recarregar')
    pg.evaluate("document.querySelector('#corpoTabela .item-checkbox[data-id=\"16\"]').click()"); pg.wait_for_timeout(150)
    clic(pg, '#btnExcluirSelecionados'); pg.wait_for_timeout(300); confirmar(pg)
    ok(guardadas(pg) == [], 'excluir a 16 esvazia o que a compra enxerga')
    ir(pg, OC)
    ok(pg.evaluate("ORDENS.length") == 14, 'e Ordens de Compra volta as 14 do exemplo')
    ir(pg, NEC)
    ok(abas(pg)['comprar'] == 4 and pg.inner_text('#kpiValor') == 'R$ 18.992,80', 'em Necessidades de Compra, voltam os 4 a comprar')
    clic(pg, '#abasSituacao .aba-sit[data-sit="comprar"]'); pg.wait_for_timeout(150)
    pg.evaluate("document.querySelector('tr[data-sku=\"MES-SLM-002\"] .item-checkbox').click()"); pg.wait_for_timeout(150)
    clic(pg, '#btnGerarOrdem'); pg.wait_for_timeout(300); clic(pg, '#btnConfirmarOrdem'); pg.wait_for_timeout(450)
    ok('A ordem de compra foi criada com sucesso: nº 15 para Móveis Nordeste Ltda' in modal(pg), 'uma ordem nova reaproveita o numero que ficou livre: %s' % modal(pg)[:90])
    confirmar(pg)

    print('\n[10] O giro')
    zerar(pg, GIRO)
    ok(abas(pg) == {'todos': 13, 'encalhe': 2, 'baixo': 3, 'normal': 8}, 'as abas contam: %s' % abas(pg))
    faixas = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('[data-faixa]')).map(e => [e.getAttribute('data-faixa'), e.textContent]))")
    ok(faixas == {'encalhe': 'até 0,00', 'baixo': 'de 0,01 até 1,00', 'normal': 'maior que 1,00'}, 'as tres faixas, por extenso, como no print: %s' % faixas)
    qtds = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('[data-qtd]')).map(e => [e.getAttribute('data-qtd'), Number(e.textContent)]))")
    ok(qtds == {'encalhe': 2, 'baixo': 3, 'normal': 8}, 'os tres quadros contam o mesmo que as abas')
    quadro = pg.inner_text('.gi-classe.normal')
    ok('Giro médio' in quadro and 'DSI médio' in quadro and 'Qtd. produtos' in quadro and 'Custo em estoque' in quadro, 'cada quadro traz giro medio, DSI medio, quantidade e custo em estoque')
    cad = pg.evaluate("(() => { const g = giroDe(produtoDe('CAD-ERG-001'), 180, 0); return [g.vendas, g.inicial, g.final, g.medio, Math.round(g.giro * 100) / 100, Math.round(g.dsi)]; })()")
    ok(cad == [46, 30, 24, 27, 1.7, 106], 'Cadeira: 46 vendidas, estoque de 30 para 24, medio 27, giro 1,70 e DSI de 106 dias: %s' % cad)
    ok('1,70' in linha(pg, 'CAD-ERG-001') and '106 dias' in linha(pg, 'CAD-ERG-001') and 'giro normal' in linha(pg, 'CAD-ERG-001').lower(), 'e a linha mostra isso')
    escolher(pg, 'itensPorPagina', 10)
    ok(skus(pg)[:2] == ['LUM-LED-004', 'MAT-PAR-014'] and 'encalhe' in linha(pg, 'LUM-LED-004').lower() and '—' in linha(pg, 'LUM-LED-004'),
       'a lista abre do menor giro para o maior: os dois encalhes primeiro, sem DSI para mostrar')
    ok('2 produtos ficaram de fora' in pg.inner_text('#avisoGiro'), 'e o aviso diz quantos ficaram de fora por terminar o periodo sem estoque')
    clic(pg, '#checkZerados'); pg.wait_for_timeout(200)
    ok(abas(pg) == {'todos': 15, 'encalhe': 2, 'baixo': 3, 'normal': 10}, '"considerar saldo final zerado" traz a Camiseta M e o Fone: %s' % abas(pg))
    clic(pg, '#checkZerados'); pg.wait_for_timeout(200)
    clic(pg, '.gi-ver[data-ver="baixo"]'); pg.wait_for_timeout(200)
    ok(sorted(skus(pg)) == ['CAB-HDM-009', 'KIT-HOF-005', 'MAT-MDF-007'] and pg.inner_text('.gi-ver[data-ver="baixo"]') == 'ocultar produtos' and pg.locator('.gi-classe.baixo.ativa').count() == 1,
       '"ver produtos" do quadro filtra a lista naquela faixa e vira "ocultar produtos"')
    clic(pg, '.gi-ver[data-ver="baixo"]'); pg.wait_for_timeout(200)
    ok(abas(pg)['todos'] == 13 and len(skus(pg)) == 10, '"ocultar produtos" volta para todos')
    classes_giro = pg.evaluate("Object.fromEntries(PRODUTOS.map(p => [p.sku, classeGiro(giroDe(p, PARAM.giroJanelaDias, 0), PARAM.giroEncalheAte, PARAM.giroBaixoAte)]))")
    ir(pg, NEC)
    ok(pg.evaluate("Object.fromEntries(PRODUTOS.map(p => [p.sku, retrato(p).classe]))") == classes_giro and classes_giro['LUM-LED-004'] == 'encalhe',
       'a classificacao que a compra usa e a mesma que o Giro mostra, produto a produto')

    print('\n[11] A regua e o aviso na compra, nos dois sentidos')
    ir(pg, GIRO)
    mover_regua(pg, 'faixaBaixo', 1.5)
    ok(abas(pg) == {'todos': 13, 'encalhe': 2, 'baixo': 7, 'normal': 4} and visivel(pg, '#faixasBarra'), 'baixo giro ate 1,50: quatro produtos mudam de faixa, e a tela avisa que a mudanca e so dela')
    ok(pg.inner_text('[data-faixa="normal"]') == 'maior que 1,50' and pg.evaluate("PARAM.giroBaixoAte") == 1, 'os quadros acompanham, e o parametro salvo continua em 1,00')
    mover_regua(pg, 'faixaEncalhe', 3)
    ok(pg.evaluate("[FAIXAS.encalhe, FAIXAS.baixo]") == [1.5, 1.5] and pg.inner_text('[data-faixa="baixo"]') == 'faixa vazia', 'o pino do encalhe nao atravessa o do baixo giro: para em 1,50')
    clic(pg, '#btnDesfazerFaixas'); pg.wait_for_timeout(200)
    ok(abas(pg)['baixo'] == 3 and not visivel(pg, '#faixasBarra'), '"Desfazer" volta as faixas salvas')
    mover_regua(pg, 'faixaBaixo', 1.5); clic(pg, '#btnSalvarFaixas'); pg.wait_for_timeout(350)
    ok('Faixas salvas' in modal(pg) and pg.evaluate("JSON.parse(localStorage.getItem('deskParametros')).giroBaixoAte") == 1.5, '"Salvar faixas" grava o parametro da empresa')
    confirmar(pg)
    ok(not visivel(pg, '#faixasBarra'), 'e a barra de pendencia some')
    ir(pg, NEC)
    ok(conta(pg, 'MON-27I-015')['classe'] == 'baixo' and 'baixo giro' in linha(pg, 'MON-27I-015').lower(), 'Necessidades de Compra passa a ver o Monitor como baixo giro')
    # O outro sentido: com 12 meses de periodo a Luminaria deixa de ser encalhe (vendeu 5 no ano), e a sugestao aparece.
    zerar(pg, NEC, {'giroJanelaDias': 365})
    lum = conta(pg, 'LUM-LED-004')
    ok(lum['classe'] == 'normal' and not lum['segurado'] and lum['comprar'] == 33 and abas(pg)['segurados'] == 0,
       'com o giro medido em 12 meses a Luminaria nao e encalhe: a sugestao de 33 aparece. E a classe que segura, nao o produto')
    zerar(pg, NEC, {'giroEncalheAte': 2, 'giroBaixoAte': 2})
    ok(conta(pg, 'MES-SLM-002')['segurado'] and conta(pg, 'MES-SLM-002')['comprar'] == 0 and abas(pg)['segurados'] >= 2,
       'e subindo o encalhe para 2,00 a Mesa (giro 1,75) passa a ser segurada tambem')

    print('\n[12] Periodo, filtros, painel, planilha e impressao')
    zerar(pg, GIRO)
    ok(pg.inner_text('#rotuloPeriodo') == 'Últimos 180 dias' and pg.evaluate("Array.from(document.querySelectorAll('#periodoOpcoes .periodo-op')).map(b => b.textContent)") ==
       ['Últimos 30 dias', 'Últimos 90 dias', 'Últimos 180 dias', 'Últimos 12 meses'], 'o periodo abre na janela de Parametros de estoque, com quatro opcoes prontas')
    clic(pg, '#btnPeriodo'); pg.wait_for_timeout(150); clic(pg, '#periodoOpcoes .periodo-op[data-periodo="30"]'); pg.wait_for_timeout(250)
    ok(pg.inner_text('#rotuloPeriodo') == 'Últimos 30 dias' and pg.evaluate("[PER.de, PER.ate]") == [30, 0] and pg.locator('#periodoMenu.open').count() == 0,
       'escolher 30 dias refaz a conta e fecha o popover')
    ok(pg.evaluate("giroDe(produtoDe('CAD-ERG-001'), 30, 0).vendas") == pg.evaluate("MOVIMENTO['CAD-ERG-001'].v.filter(x => x[0] < 30).reduce((s, x) => s + x[1], 0)"), 'so entram as vendas dos ultimos 30 dias')
    clic(pg, '#btnPeriodo'); pg.wait_for_timeout(150)
    hoje = datetime.date.today()
    pg.fill('#periodoDe', (hoje - datetime.timedelta(days=10)).strftime('%d/%m/%Y')); pg.fill('#periodoAte', (hoje - datetime.timedelta(days=40)).strftime('%d/%m/%Y'))
    clic(pg, '#btnAplicarPeriodo'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroPeriodo') and 'depois da final' in pg.inner_text('#erroPeriodo'), 'data inicial depois da final nao aplica')
    pg.fill('#periodoDe', (hoje - datetime.timedelta(days=500)).strftime('%d/%m/%Y')); pg.fill('#periodoAte', '')
    clic(pg, '#btnAplicarPeriodo'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroPeriodo') and '12 meses' in pg.inner_text('#erroPeriodo'), 'nem data mais antiga que o movimento guardado')
    pg.fill('#periodoDe', (hoje - datetime.timedelta(days=59)).strftime('%d/%m/%Y')); pg.fill('#periodoAte', hoje.strftime('%d/%m/%Y'))
    clic(pg, '#btnAplicarPeriodo'); pg.wait_for_timeout(250)
    ok(pg.evaluate("[PER.de, PER.ate]") == [60, 0] and pg.inner_text('#rotuloPeriodo') == (hoje - datetime.timedelta(days=59)).strftime('%d/%m/%Y') + ' a ' + hoje.strftime('%d/%m/%Y'),
       'entre datas: o dia inicial e o final entram na conta (60 dias): %s' % pg.inner_text('#rotuloPeriodo'))
    clic(pg, '#btnPeriodo'); pg.wait_for_timeout(150); clic(pg, '#periodoOpcoes .periodo-op[data-periodo="180"]'); pg.wait_for_timeout(250)
    escolher(pg, 'filtroLoja', 2)
    ok(skus(pg) == ['CAM-DKB-011'] and abas(pg)['todos'] == 1, 'loja Desk Brands: so a Camiseta P (a M terminou o periodo zerada)')
    escolher(pg, 'filtroLoja', 'todos'); escolher(pg, 'filtroCategoria', 'Matéria-prima')
    ok(sorted(skus(pg)) == ['MAT-MDF-007', 'MAT-PAR-014', 'MAT-TEC-008'], 'categoria Materia-prima: 3 produtos')
    escolher(pg, 'filtroCategoria', 'todos'); escolher(pg, 'filtroTipo', 'kit')
    ok(sorted(skus(pg)) == ['KIT-HOF-005', 'KIT-MNT-010'], 'tipo Kit: 2 produtos')
    clic(pg, '#abasSituacao .aba-sit[data-sit="encalhe"]'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#emptyState'), 'faixa sem produto mostra a lista vazia')
    clic(pg, '#btnLimparFiltros'); pg.wait_for_timeout(250)
    ok(abas(pg)['todos'] == 13 and len(skus(pg)) == 10, '"Limpar filtros" devolve os 13')
    clic(pg, '#corpoTabela tr[data-sku="LUM-LED-004"] td'); pg.wait_for_timeout(350)
    txt = pg.inner_text('#drawerCorpo')
    ok(pg.inner_text('#drawerTitulo') == 'O giro do produto' and 'Não vendeu nada em 180 dias' in pg.inner_text('#giroLeitura') and 'Estoque inicial' in txt and 'Última venda' in txt,
       'clicar na linha abre o giro do produto, com a leitura por extenso')
    ok(pg.locator('.gi-meses tbody tr').count() == 6, 'e o periodo quebrado em 6 blocos de 30 dias')
    ok(pg.get_attribute('#drawerCorpo a[href*="necessidades-compra"]', 'href').endswith('?busca=LUM-LED-004'), 'com o caminho de volta para Necessidades de Compra')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ir(pg, GIRO, '?busca=FON-BLT-013')
    ok(skus(pg) == ['FON-BLT-013'] and pg.is_checked('#checkZerados'), 'chegando pelo link da compra, a lista abre no produto mesmo que ele tenha terminado zerado')
    ir(pg, GIRO)
    with pg.expect_download() as d:
        clic(pg, '#btnPlanilha')
    csv = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
    ok(csv[0] == '"Classificação";"Produto";"SKU";"Estoque Médio";"Total de Vendas";"Giro de Estoque";"DSI"' and len(csv) == 14 and d.value.suggested_filename.startswith('giro-de-estoque-'),
       'a planilha do Giro sai com as 7 colunas do Olist e os 13 produtos: %s' % d.value.suggested_filename)
    ok(any(l.startswith('"Giro normal";"Cadeira Ergonômica Pro";"CAD-ERG-001";"27";"46";"1,7";') for l in csv), 'com os numeros da tela')
    # Dentro de uma funcao: o Playwright EXECUTA a expressao quando ela devolve uma funcao, e contaria uma impressao a mais.
    pg.evaluate("(() => { window.print = () => { window.__impressoes = (window.__impressoes || 0) + 1; window.__linhas = document.querySelectorAll('#corpoTabela tr').length; }; })()")
    clic(pg, '#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150); clic(pg, '#menuMaisAcoes [data-acao="imprimir"]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("[window.__impressoes, window.__linhas]") == [1, 13] and len(skus(pg)) == 10, 'imprimir manda a lista inteira para o papel e devolve a pagina de 10 linhas')
    ir(pg, NEC)
    with pg.expect_download() as d:
        clic(pg, '#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(120); clic(pg, '#menuMaisAcoes [data-acao="planilha"]')
    csv = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
    ok(csv[0].startswith('"Produto";"Código (SKU)";"GTIN/EAN";"Fornecedor padrão";"Un";"Custo médio"') and csv[0].endswith('"Comprar"') and len(csv) == 16,
       'a planilha da compra sai com as colunas do print e os 15 produtos')
    ok(any('"SUP-MON-003"' in l and l.endswith('"19"') for l in csv), 'com a quantidade a comprar de cada um')
    # Dentro de uma funcao: o Playwright EXECUTA a expressao quando ela devolve uma funcao, e contaria uma impressao a mais.
    pg.evaluate("(() => { window.print = () => { window.__impressoes = (window.__impressoes || 0) + 1; window.__linhas = document.querySelectorAll('#corpoTabela tr').length; }; })()")
    clic(pg, '#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150); clic(pg, '#menuMaisAcoes [data-acao="imprimir"]'); pg.wait_for_timeout(250)
    ok(pg.evaluate("[window.__impressoes, window.__linhas]") == [1, 15], 'e a impressao leva os 15')
    pg.emulate_media(media='print'); pg.wait_for_timeout(250)
    papel = pg.evaluate("""(() => { const c = document.querySelector('#corpoTabela .nc-qtd'), e = getComputedStyle(c), n = getComputedStyle(document.querySelector('#corpoTabela .prod-nome'));
        return [e.backgroundColor, e.color, n.color, getComputedStyle(document.querySelector('.floating-card')).display, getComputedStyle(document.querySelector('.estoque-toolbar')).display]; })()""")
    pg.emulate_media(media='screen')
    ok(papel == ['rgba(0, 0, 0, 0)', 'rgb(16, 16, 16)', 'rgb(16, 16, 16)', 'none', 'none'],
       'no papel, com a tela no tema escuro: o campo Comprar sai sem fundo e com texto escuro, e o menu e os filtros nao sao impressos: %s' % papel)
    for acao, destino in [('ordens', OC), ('giro', GIRO), ('parametros', PARAMS)]:
        ir(pg, NEC)
        clic(pg, '#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(120); clic(pg, '#menuMaisAcoes [data-acao="%s"]' % acao); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
        ok(pg.url.endswith(destino), '"Mais ações" da compra leva a %s' % destino)

    print('\n[13] Parametros de estoque')
    zerar(pg, PARAMS)
    campos = pg.evaluate("['giroEncalheAte', 'giroBaixoAte', 'giroJanelaDias', 'compraCoberturaDias'].map(k => { const i = document.querySelector('[data-param=\"' + k + '\"]'); return i ? i.value : null; })")
    ok(campos == ['0', '1', '180', '30'] and 'Compra e giro de estoque' in pg.inner_text('body'), 'a secao Compra e giro nasce com os quatro parametros no padrao: %s' % campos)
    ok('até 0,00' in pg.inner_text('#previaGiro') and 'maior que 1,00' in pg.inner_text('#previaGiro'), 'e a previa escreve as faixas por extenso')
    pg.fill('#giroEncalhe', '0,8'); pg.fill('#giroBaixo', '0,5'); pg.wait_for_timeout(150)
    clic(pg, '#btnSalvarParam'); pg.wait_for_timeout(300)
    ok(pg.locator('#campoGiroBaixo.has-error').count() == 1 and 'inválidos' in modal(pg) and pg.evaluate("localStorage.getItem('deskParametros')") is None,
       'baixo giro menor que o encalhe nao salva, e o campo fica marcado')
    confirmar(pg)
    pg.fill('#giroEncalhe', '0,2'); pg.fill('#giroBaixo', '0,8'); pg.fill('#giroJanela', '90'); pg.wait_for_timeout(150)
    ok('3 parâmetros alterados' in pg.inner_text('#notaBarra'), 'a nota da barra conta os tres campos mexidos: %s' % pg.inner_text('#notaBarra'))
    clic(pg, '#btnSalvarParam'); pg.wait_for_timeout(300)
    salvo = pg.evaluate("JSON.parse(localStorage.getItem('deskParametros'))")
    ok('3 parâmetros salvos' in modal(pg) and 'Giro de Estoque' in modal(pg) and (salvo['giroEncalheAte'], salvo['giroBaixoAte'], salvo['giroJanelaDias'], salvo['compraCoberturaDias']) == (0.2, 0.8, 90, 30),
       'salvar grava os quatro e avisa que as telas de compra e giro passam a usar')
    confirmar(pg)
    pg.reload(); pg.wait_for_timeout(400)
    ok(pg.input_value('#giroEncalhe') == '0,2' and pg.input_value('#giroBaixo') == '0,8', 'ao reabrir, os campos vem com virgula, como foram digitados')
    ir(pg, GIRO)
    ok(pg.inner_text('[data-faixa="encalhe"]') == 'até 0,20' and pg.inner_text('#rotuloPeriodo') == 'Últimos 90 dias' and pg.locator('#periodoOpcoes .periodo-op.active').inner_text() == 'Últimos 90 dias',
       'o Giro abre com as faixas e o periodo salvos')
    ir(pg, NEC)
    clic(pg, '#btnOpcoes'); pg.wait_for_timeout(250)
    ok('últimos 90 dias' in pg.text_content('#campoCobertura') and pg.input_value('#opCoberturaDias') == '30' and conta(pg, 'CAD-ERG-001')['classe'] in ('normal', 'baixo', 'encalhe') and
       pg.evaluate("retrato(produtoDe('CAD-ERG-001')).g.dias") == 90, 'e a compra usa o mesmo periodo para o giro e para a venda por dia')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    zerar(pg, PARAMS)

    print('\n[14] Fornecedor padrao no cadastro do produto')
    ir(pg, PRODUTO)
    forn = "Array.from(document.querySelectorAll('#tabelaFornecedoresProduto tr')).map(tr => [tr.querySelector('input[type=text]').value, tr.querySelector('input[type=radio]').checked])"
    ok(pg.evaluate("Array.from(document.querySelectorAll('#tabelaFornecedoresProduto')[0].closest('table').querySelectorAll('th')).map(t => t.textContent)") == ['Fornecedor', 'Código no Fornecedor', 'Padrão', ''],
       'a tabela de fornecedores do produto ganhou a coluna Padrao')
    ok(pg.evaluate(forn) == [['Tech Solutions Imperatriz Ltda', True]], 'o primeiro fornecedor nasce como padrao')
    clic(pg, '#btnAddFornecedor'); pg.wait_for_timeout(150)
    pg.evaluate("(() => { const c = document.querySelectorAll('#tabelaFornecedoresProduto tr')[1].querySelector('input[type=text]'); c.value = 'Móveis Nordeste Ltda'; c.dispatchEvent(new Event('input', { bubbles: true })); })()")
    clic(pg, '#btnAddFornecedor'); pg.wait_for_timeout(150)
    ok(pg.evaluate(forn) == [['Tech Solutions Imperatriz Ltda', True], ['Móveis Nordeste Ltda', False], ['', False]],
       'adicionar outra linha nao apaga o nome ja digitado (antes, redesenhar a tabela apagava)')
    pg.evaluate("document.querySelectorAll('#tabelaFornecedoresProduto input[type=radio]')[1].click()"); pg.wait_for_timeout(150)
    ok(pg.evaluate("fornecedoresProduto.map(f => f.padrao)") == [False, True, False] and pg.evaluate(forn)[0][1] is False, 'marcar o segundo como padrao desmarca o primeiro: so ha um')
    pg.evaluate("document.querySelectorAll('#tabelaFornecedoresProduto .remove-contato-btn')[1].click()"); pg.wait_for_timeout(150)
    ok(pg.evaluate(forn) == [['Tech Solutions Imperatriz Ltda', True], ['', False]], 'remover o padrao passa a marca para o primeiro que sobra')

    print('\n[15] Largura, temas, Esc e erros')
    for tela, painel in [(NEC, 'painelCompra'), (GIRO, 'painelGiro')]:
        zerar(pg, tela)
        for tema in ['claro', 'escuro']:
            pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add')); pg.wait_for_timeout(220)
            ok(cabe(pg, painel) and pg.evaluate('document.documentElement.scrollWidth') <= 1440, '%s, tema %s: a tabela cabe no card a 1440px e a pagina nao rola de lado' % (tela.replace('pagina-estoque-', '').replace('.html', ''), tema))
    ir(pg, NEC)
    ok(pg.evaluate("(() => { const c = document.querySelector('tr[data-sku=\"SUP-MON-003\"] .nc-qtd').getBoundingClientRect(), k = document.getElementById('painelCompra').getBoundingClientRect(); return c.right <= k.right && c.width > 40; })()"),
       'a coluna Comprar, que e a que importa, esta inteira dentro do card')
    aba(pg, 'comprar'); clic(pg, '#checkSelecionarTodos'); pg.wait_for_timeout(150); clic(pg, '#btnGerarSelecionados'); pg.wait_for_timeout(350)
    ok(pg.evaluate("(() => { const d = document.getElementById('eventDrawer'); return d.scrollWidth <= d.clientWidth + 1; })()"), 'o painel da ordem de compra nao estoura na largura')
    clic(pg, '#ocForn0 .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#ocForn0 .dropdown-select-menu.open').count() == 0 and pg.locator('#eventDrawer.open').count() == 1, 'Esc fecha primeiro o dropdown aberto dentro do painel')
    clic(pg, '#dfPrev0 .date-btn'); pg.wait_for_timeout(200)
    aberto = pg.locator('#dfPrev0 .date-pop.open').count() == 1
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(aberto and pg.locator('#dfPrev0 .date-pop.open').count() == 0 and pg.locator('#eventDrawer.open').count() == 1, 'e primeiro o calendario, sem levar o painel junto')
    ok(pg.evaluate("(() => { const p = document.querySelector('#dfPrev0 .date-pop'); p.classList.add('open'); const r = p.getBoundingClientRect(), d = document.getElementById('eventDrawer').getBoundingClientRect(); p.classList.remove('open'); return r.left >= d.left && r.right <= d.right; })()"),
       'o calendario abre inteiro dentro do painel')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    ok(pg.locator('#eventDrawer.open').count() == 0 and guardadas(pg) == [], 'e o Esc seguinte fecha o painel, sem criar ordem')
    ir(pg, GIRO)
    clic(pg, '#btnPeriodo'); pg.wait_for_timeout(150); clic(pg, '#filtroLoja .dropdown-select-btn'); pg.wait_for_timeout(200)
    ok(pg.locator('#periodoMenu.open').count() == 0 and pg.locator('#filtroLoja .dropdown-select-menu.open').count() == 1, 'abrir um filtro fecha o popover de periodo que estava aberto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.evaluate("['faixaEncalhe', 'faixaBaixo'].every(i => document.getElementById(i).getAttribute('aria-label') && document.getElementById(i).getAttribute('aria-valuetext'))"),
       'os dois pinos da regua tem nome e valor para leitor de tela, e andam pelo teclado')
    ok(not erros, 'sem erro de JS em nenhuma das telas: %s' % erros[:2])

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
