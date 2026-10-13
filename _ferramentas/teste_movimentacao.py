# -*- coding: utf-8 -*-
# Estoque > Movimentacao de Estoque (13/out/2026).
#
# Pedido do usuario em 12/out, com quatro prints de um kardex: o historico individual de cada produto,
# do saldo de antes ate o saldo de hoje, com o documento inteiro de cada movimento. E so consulta.
#
#   [1] o item esta no menu de todas as telas, e a tela abre so com os filtros: deposito, produto, tipo
#       de movimento, data inicial, data final e Buscar. Sem produto nao ha busca;
#   [2] o historico fecha no Controle de Estoques: saldo final por deposito, custo medio e os cinco
#       indicadores. Cada linha parte do saldo em que a anterior parou;
#   [3] e fecha no Giro de Estoque: as vendas, as entradas e o saldo de partida do periodo sao os
#       mesmos, porque a tela le o mesmo bloco comum;
#   [4] os filtros: deposito, tipo, datas, ordem, paginas e Limpar. Filtrar esconde linha, nao refaz saldo;
#   [5] clicar no movimento abre o documento inteiro: de onde veio, para quem foi e os outros itens.
#       Imprimir manda so o documento para o papel. O documento nao e link: a lista de origem nao tem
#       estes registros no exemplo dela, e link que cai em lista vazia e pior que texto;
#   [6] e so consulta: nada do que a tela faz grava. Planilha e impressao saem com a lista inteira;
#   [7] as vizinhas levam para ca e a tela leva de volta, sempre no mesmo produto;
#   [8] cabe em 1440, 1366 e 1280 de largura: quem cede e o texto, nao a tabela.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

MOV, CE, CED, GIRO = 'pagina-estoque-movimentacao.html', 'pagina-estoque-controle-estoques.html', 'pagina-estoque-controle-estoques-detalhe.html', 'pagina-estoque-giro-estoque.html'
NEC = 'pagina-estoque-necessidades-compra.html'
SO = (sys.argv[1:] or [''])[0]

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    # O console do Windows (cp1252) nao imprime o sinal de menos tipografico que a tela usa.
    cod = sys.stdout.encoding or 'utf-8'
    print((('  ok   ' if cond else '  FALHOU  ') + texto).encode(cod, 'replace').decode(cod))
    if not cond:
        falhas.append(texto)


def secao(n, titulo):
    if SO and SO != str(n):
        return False
    print('\n[%d] %s' % (n, titulo))
    return True


def bloco_comum(tela):
    t = open(localiza.onde(tela), encoding='utf-8').read()
    a = t.index('  // ===== COMPRA E GIRO: BLOCO COMUM =====')
    return t[a:t.index('  // ===== ', a + 10)]


def secao_da_tela():
    t = open(localiza.onde(MOV), encoding='utf-8').read()
    a = t.index('  // ===== MOVIMENTAÇÃO DE ESTOQUE =====')
    return t[a:t.index('  // ===== ', a + 10)]


def num(texto):
    """'1.234,50 UN' ou 'R$ 742,30' ou '−2' viram numero."""
    limpo = re.sub(r'[^0-9,.\-−+]', '', texto).replace('−', '-').replace('+', '').replace('.', '').replace(',', '.')
    return float(limpo) if limpo not in ('', '-') else None


# O saldo fisico de cada produto em cada deposito, do jeito que o Controle de Estoques guarda.
FISICO_CE = """PRODUTOS.map(p => { const d = { todos: 0 };
  p.saldos.forEach(x => { if (x.estagio === 'em_conferencia') return; d[x.dep] = Math.round(((d[x.dep] || 0) + x.qtd) * 1000) / 1000; d.todos = Math.round((d.todos + x.qtd) * 1000) / 1000; });
  return { sku: p.sku, custo: p.custoMedio, deps: d }; })"""
# O que o historico diz de cada produto em cada deposito.
FISICO_MOV = """PRODUTOS.map(p => { const d = {};
  ['todos'].concat(Object.keys(DEPOSITOS)).forEach(k => { const h = historicoDe(p, k); const f = h.linhas.length ? h.linhas[h.linhas.length - 1].depois : h.inicial; if (f !== 0 || k === 'todos') d[k] = f; });
  const todas = historicoDe(p, 'todos').linhas;
  return { sku: p.sku, custo: Math.round(todas[todas.length - 1].m.custoMedio * 1e6) / 1e6, deps: d }; })"""
# As linhas que estao na tela, lidas da propria tabela.
TABELA = """Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => { const c = Array.from(tr.children).map(td => td.textContent.trim());
  return { data: c[0].slice(0, 10), hora: c[0].slice(10), mov: tr.querySelector('.prod-nome').textContent, doc: tr.getAttribute('data-doc'), quem: c[2], antes: c[3], qtd: c[4], depois: c[5], valor: c[6], custo: c[7], estoque: c[8] }; })"""

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950}, accept_downloads=True)
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, query=''):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def escolher(dropdown, valor):
        pg.evaluate("([d, v]) => document.querySelector('#' + d + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [dropdown, valor])

    def buscar(sku=None, dep=None, tipo=None, de=None, ate=None, por_pagina=None):
        if sku: escolher('filtroProduto', sku)
        if dep: escolher('filtroDeposito', dep)
        if tipo: escolher('filtroTipoMov', tipo)
        if de is not None: pg.fill('#dataDe', de)
        if ate is not None: pg.fill('#dataAte', ate)
        clic('#btnBuscar'); pg.wait_for_timeout(200)
        if por_pagina:
            escolher('itensPorPagina', str(por_pagina)); pg.wait_for_timeout(150)

    def linhas():
        return pg.evaluate(TABELA)

    def texto(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.trim() : null; }", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)

    if secao(1, 'Menu e abertura'):
        ITEM = 'data-label="Movimentação de Estoque" data-href="../estoque/%s"' % MOV
        sem, fora = [], []
        for c in localiza.caminhos():
            t = open(c, encoding='utf-8').read()
            if t.count('data-label="Movimentação de Estoque"') != t.count(ITEM) or ITEM not in t:
                sem.append(_os.path.basename(c))
            elif not re.search(r'data-label="Controle de Estoques"[^\n]*\n\s*<div class="flyout-item" ' + re.escape(ITEM), t):
                fora.append(_os.path.basename(c))
        ok(not sem, 'toda tela tem "Movimentação de Estoque" no menu de Estoque, com destino: %s' % sem[:4])
        ok(not fora, 'e o item vem logo depois de Controle de Estoques: %s' % fora[:4])
        ir(CE)
        pg.click('.nav-item[data-id="estoque"]'); pg.wait_for_timeout(450)
        pg.click('#flyout-estoque .flyout-item[data-label="Movimentação de Estoque"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(pg.url.split('/')[-1] == MOV, 'do Controle de Estoques, o menu leva à tela: %s' % pg.url.split('/')[-1])
        ok(texto('#breadcrumb').replace('\n', '').replace(' ', '') == 'Estoque›MovimentaçãodeEstoque' and texto('.page-header h1') == 'Movimentação de Estoque',
           'o caminho no topo e o título dizem onde se está: %s' % texto('#breadcrumb'))
        rotulos = pg.evaluate("Array.from(document.querySelectorAll('#painelFiltros .form-field label')).map(l => l.textContent)")
        ok(rotulos == ['Depósito', 'Produto', 'Tipo de movimento', 'Data inicial', 'Data final'] and visivel('#btnBuscar'),
           'a tela abre com os cinco filtros na ordem pedida e o Buscar: %s' % rotulos)
        ok(visivel('#painelInicio') and not visivel('#painelResultado') and pg.evaluate("document.querySelectorAll('#corpoTabela tr').length") == 0,
           'e sem lista: só o convite para escolher um produto')
        ok(pg.evaluate("document.querySelectorAll('#filtroProduto .dropdown-select-item').length") == 15 and pg.evaluate("document.querySelectorAll('#filtroDeposito .dropdown-select-item').length") == 6
           and pg.evaluate("document.querySelectorAll('#filtroTipoMov .dropdown-select-item').length") == 10,
           'os filtros trazem os 15 produtos, os 5 depósitos e os 9 tipos de movimento (mais "todos")')
        ok(pg.evaluate("document.querySelectorAll('select').length") == 0, 'nenhum campo de escolha nativo: tudo é o dropdown da casa')
        clic('#btnBuscar'); pg.wait_for_timeout(200)
        ok(texto('#erroBusca') == 'Escolha o produto.' and visivel('#erroBusca') and pg.evaluate("document.getElementById('campoProduto').classList.contains('has-error')")
           and not visivel('#painelResultado'), 'Buscar sem produto não busca: o campo fica marcado e a tela diz o que falta')
        buscar('CAD-ERG-001')
        ok(visivel('#painelResultado') and not visivel('#painelInicio') and not visivel('#erroBusca') and texto('#painelProduto .bq-nome') == 'Cadeira Ergonômica Pro',
           'com o produto escolhido, Buscar traz o histórico e o erro some')
        ir(MOV, '?busca=zzqqxx')
        ok(visivel('#painelInicio') and 'zzqqxx' in texto('#inicioTitulo'), 'produto que não existe, vindo pelo endereço, vira explicação e não tela quebrada')

    if secao(2, 'O histórico fecha no Controle de Estoques'):
        ok(bloco_comum(MOV) == bloco_comum(GIRO) == bloco_comum(NEC), 'o bloco comum é o mesmo texto do Giro de Estoque e de Necessidades de Compra')
        ir(CE)
        do_ce = pg.evaluate(FISICO_CE)
        ir(MOV)
        do_mov = pg.evaluate(FISICO_MOV)
        ok(len(do_ce) == 15 and [x['sku'] for x in do_ce] == [x['sku'] for x in do_mov], 'os 15 produtos são os do Controle de Estoques')
        tortos = [(a['sku'], a['deps'], b['deps']) for a, b in zip(do_ce, do_mov) if {k: v for k, v in a['deps'].items() if v != 0 or k == 'todos'} != b['deps']]
        ok(not tortos, 'a última linha de cada produto, em cada depósito e na soma, é o saldo físico do Controle de Estoques: %s' % tortos[:2])
        ok(all(a['custo'] == b['custo'] for a, b in zip(do_ce, do_mov)), 'e o custo médio da última linha é o custo médio de lá: %s' % [(a['sku'], a['custo'], b['custo']) for a, b in zip(do_ce, do_mov) if a['custo'] != b['custo']][:2])
        ok(pg.evaluate("PRODUTOS.every(p => MOVS.filter(x => x.sku === p.sku && x.tipo === 'compra').every(x => x.valor > p.custoMedio * 0.9 && x.valor < p.custoMedio * 1.1))"),
           'o custo de cada nota fica a menos de 10% do custo médio: a conta que fecha a média não inventa preço')
        negativos = pg.evaluate("PRODUTOS.filter(p => ['todos'].concat(Object.keys(DEPOSITOS)).some(d => { const h = historicoDe(p, d); return h.inicial < 0 || h.linhas.some(l => l.depois < 0); })).map(p => p.sku)")
        ok(negativos == ['FON-BLT-013'], 'só o Fone, que o Controle de Estoques já mostra negativo, passa por saldo negativo: %s' % negativos)

        # O caso rico, pela tela: os cinco indicadores contra a pagina do produto.
        ir(CED, '?produto=15')
        la = {k: texto('#' + k) for k in ['kpiFisico', 'kpiAEnderecar', 'kpiBloqueado', 'kpiDisponivel', 'kpiConferencia']}
        ir(MOV); buscar('MON-27I-015', por_pagina=100)
        ok(num(texto('#kpiAtual')) == num(la['kpiFisico']) == 9 and num(texto('#kpiDisponivel')) == num(la['kpiDisponivel']) == 2,
           'Monitor: estoque atual e disponível são os da página do produto (%s e %s)' % (texto('#kpiAtual'), texto('#kpiDisponivel')))
        ok('5 UN a endereçar' in texto('#kpiDisponivelSub') and '2 UN bloqueado' in texto('#kpiDisponivelSub') and num(la['kpiAEnderecar']) == 5 and num(la['kpiBloqueado']) == 2,
           'e o que separa um do outro está dito: %s' % texto('#kpiDisponivelSub'))
        ok(texto('#kpiAtualSub').startswith('4 UN em conferência') and num(la['kpiConferencia']) == 4, 'o que está em conferência aparece à parte, fora do estoque')
        ok(texto('#kpiReservado') == '0 UN' and texto('#kpiCusto') == 'R$ 1.120,00' and texto('#kpiValor') == 'R$ 10.080,00', 'reservado, custo médio e valor em estoque: 0 UN, R$ 1.120,00 e R$ 10.080,00')
        ls = linhas()
        ok(len(ls) == 17 and num(ls[-1]['depois']) == 9 and ls[-1]['custo'] == 'R$ 1.120,00' and ls[-1]['estoque'] == 'R$ 10.080,00',
           'a lista termina na situação de hoje: saldo 9, custo médio R$ 1.120,00, R$ 10.080,00 em estoque')
        ok(num(texto('#avisoMov b')) == num(ls[0]['antes']) and all(abs(num(l['antes']) + num(l['qtd']) - num(l['depois'])) < 1e-9 for l in ls)
           and all(num(ls[i]['depois']) == num(ls[i + 1]['antes']) for i in range(len(ls) - 1)),
           'em toda linha, saldo anterior mais a quantidade dá o saldo atual, e a linha seguinte parte dele')
        ultima_nota = max(i for i, x in enumerate(ls) if x['mov'] == 'Entrada por nota de compra')
        ok(len(set(l['custo'] for l in ls)) > 1 and all(l['custo'] == ls[-1]['custo'] for l in ls[ultima_nota:]),
           'o custo médio muda quando entra nota e fica parado entre uma nota e outra')
        colunas = pg.evaluate("Array.from(document.querySelectorAll('#painelMov thead th')).map(t => t.textContent.replace('▲', '').replace('▼', '').trim())")
        ok(colunas == ['Data e hora', 'Movimento', 'Cliente ou fornecedor', 'Saldo anterior', 'Quantidade', 'Saldo atual', 'Valor unitário', 'Custo médio', 'Valor em estoque'],
           'as colunas são as que o usuário pediu: %s' % colunas)
        # Materia-prima vendida por metro: a quantidade segue a unidade.
        buscar('MAT-MDF-007', por_pagina=100)
        ok(texto('#kpiAtual') == '128,50 M2' and ',' in linhas()[0]['qtd'], 'unidade fracionável sai com casas: %s' % texto('#kpiAtual'))

    if secao(3, 'E fecha no Giro de Estoque'):
        ir(GIRO)
        giro = pg.evaluate("PRODUTOS.map(p => { const g = giroDe(p, 180, 0); return { sku: p.sku, vendas: g.vendas, entradas: g.entradas, inicial: g.inicial, final: g.final }; })")
        ir(MOV)
        aqui = pg.evaluate("""PRODUTOS.map(p => { consulta = { p: p, dep: 'todos', tipo: 'todos', de: dataHa(179), ate: HOJE_ISO }; const r = linhasDaConsulta();
          const soma = (tipos, sinal) => arred(r.periodo.filter(l => tipos.includes(l.m.tipo)).reduce((s, l) => s + sinal * l.m.qtd, 0));
          return { sku: p.sku, vendas: soma(['venda', 'pdv'], -1), entradas: soma(['compra'], 1), inicial: r.saldoAntes, final: r.saldoFim }; })""")
        ok(giro == aqui, 'nos últimos 180 dias, vendas, entradas de compra, saldo de partida e saldo final batem com o Giro nos 15 produtos: %s' % [(g, a) for g, a in zip(giro, aqui) if g != a][:1])
        ok(pg.evaluate("""Object.keys(AJUSTES).every(sku => { const dia = {}; AJUSTES[sku].forEach(a => { dia[a[0]] = (dia[a[0]] || 0) + a[2]; }); return Object.keys(dia).every(d => dia[d] === 0); })
             && Object.keys(TRANSFERENCIAS).every(sku => MOVS.filter(x => x.sku === sku && x.tipo.indexOf('transf') === 0).reduce((s, x) => s + x.qtd, 0) === 0)"""),
           'o que o Giro não conhece (devolução que virou perda, acerto corrigido, inventário, transferência) soma zero no dia: o saldo de cada dia continua o mesmo')
        ok(pg.evaluate("MOVS.filter(x => x.tipo === 'venda' || x.tipo === 'pdv').length === Object.keys(MOVIMENTO).reduce((s, k) => s + MOVIMENTO[k].v.length, 0) && MOVS.filter(x => x.tipo === 'compra').length === Object.keys(MOVIMENTO).reduce((s, k) => s + MOVIMENTO[k].e.length, 0)"),
           'cada venda e cada entrada do bloco comum vira exatamente um movimento')
        # Pela tela: o resumo por tipo contra a coluna "Total de vendas" do Giro.
        ir(GIRO, '?busca=TEC-MEC-006')
        la = num(pg.evaluate("document.querySelector('#corpoTabela tr').children[3].textContent"))
        ir(MOV)
        buscar('TEC-MEC-006', de=pg.evaluate("fmtData(dataHa(179))"))
        clic('#btnResumo'); pg.wait_for_timeout(350)
        resumo = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('#tabelaResumo tr[data-tipo]')).map(tr => [tr.getAttribute('data-tipo'), Array.from(tr.children).map(td => td.textContent)]))")
        vendido = -sum(num(resumo[k][3]) for k in ('venda', 'pdv'))
        ok(vendido == la == 62, 'Teclado: o resumo por tipo soma %s vendidos em 180 dias, o "Total de vendas" que o Giro mostra (%s)' % (vendido, la))
        fatos = pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo .bq-fato b')).map(b => b.textContent)")
        ok(len(resumo) == 5 and num(fatos[0]) + num(fatos[1]) + num(fatos[2]) == num(fatos[3]) == 40,
           'e o resumo fecha: saldo antes, mais entradas, menos saídas, dá o saldo no fim (%s)' % fatos)
        ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('mv-doc')"), 'o resumo abre no painel de largura normal')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'Esc fecha o resumo')

    if secao(4, 'Os filtros'):
        ir(MOV); buscar('CAD-ERG-001', por_pagina=100)
        todas = linhas()
        ok(len(todas) == 49 and texto('#contagemItens') == '49 movimentações' and texto('#paginacaoResumo') == 'Mostrando 1-49 de 49', 'Cadeira, todos os depósitos: 49 movimentações')
        iso = lambda d: d[6:] + d[3:5] + d[:2]
        ok(all(iso(todas[i]['data']) + todas[i]['hora'] <= iso(todas[i + 1]['data']) + todas[i + 1]['hora'] for i in range(len(todas) - 1)), 'em ordem de data e hora, terminando no dia mais recente')
        # deposito
        buscar(dep='3')
        ls = linhas()
        ok([(l['mov'], num(l['qtd'])) for l in ls] == [('Transferência recebida', 5), ('Venda no PDV', -2)] and num(ls[-1]['depois']) == 3 and texto('#kpiAtual') == '3 UN',
           'na Loja Física Aldeota a Cadeira chegou por transferência e vendeu no balcão: termina em 3, o saldo de lá')
        ok(ls[0]['quem'] == 'de Galpão Centro' and texto('#painelProduto .badge-situacao') == 'Loja Física Aldeota', 'a transferência diz de onde veio, e o quadro do produto diz o depósito consultado')
        buscar(dep='2')
        ls2 = linhas()
        ok(len(ls2) == 47 and num(ls2[-1]['depois']) == 21 and len(ls) + len(ls2) == len(todas), 'no Galpão Centro são as outras 47 linhas, terminando em 21: nenhum movimento some nem dobra')
        buscar(dep='4')
        ok(visivel('#emptyState') and texto('#kpiAtual') == '0 UN' and 'não teve movimento' in texto('#emptySub'), 'depósito por onde o produto nunca passou: lista vazia, com explicação')
        # tipo
        buscar(dep='todos', tipo='compra')
        ls = linhas()
        ok(len(ls) == 4 and all(l['mov'] == 'Entrada por nota de compra' for l in ls) and all(l['quem'] == 'Móveis Nordeste Ltda' for l in ls), 'tipo "Entrada por nota de compra": as 4 notas, do fornecedor padrão')
        ok(all(any(t['doc'] == l['doc'] and t['antes'] == l['antes'] and t['depois'] == l['depois'] for t in todas) for l in ls) and num(ls[1]['antes']) != num(ls[0]['depois']),
           'filtrar o tipo esconde linhas e não refaz o saldo: cada nota mostra o saldo que tinha no histórico inteiro')
        ok(texto('#totalLista').startswith('Entradas +80 · Saídas −0') and texto('#totalLista').endswith('24 UN'), 'o rodapé soma o que está na lista e diz o saldo no fim do período: %s' % texto('#totalLista'))
        buscar(tipo='devolucao')
        ok(visivel('#emptyState') and '49 movimentos no período, mas nenhum deste tipo' in texto('#emptySub'), 'tipo sem movimento: a tela diz que o produto teve movimento, só não deste tipo')
        # o filtro so vale no Buscar
        escolher('filtroTipoMov', 'todos'); pg.wait_for_timeout(150)
        ok(visivel('#emptyState'), 'trocar um filtro não mexe na lista: ele vale quando se clica em Buscar')
        # datas
        buscar(de='31/12/2026', ate='01/01/2026')
        ok(texto('#erroBusca') == 'A data inicial é depois da final.' and visivel('#erroBusca'), 'data inicial depois da final é barrada')
        buscar(de='2026-01-01', ate='')
        ok(texto('#erroBusca') == 'Use o formato dd/mm/aaaa nas datas.', 'data fora do formato é barrada')
        meio = todas[20]['data']
        buscar(de=meio, ate=todas[30]['data'])
        ls = linhas()
        ok(len(ls) >= 5 and all(iso(meio) <= iso(l['data']) <= iso(todas[30]['data']) for l in ls) and not visivel('#erroBusca'), 'entre duas datas, só os movimentos do intervalo (%d)' % len(ls))
        antes = [t for t in todas if iso(t['data']) < iso(meio)][-1]
        ok(num(texto('#avisoMov b')) == num(antes['depois']) == num(ls[0]['antes']) and meio in texto('#avisoMov'), 'o saldo antes do período é o saldo em que o histórico estava: %s' % texto('#avisoMov'))
        ok(('Período ' + meio + ' a ' + todas[30]['data']) in texto('#painelProduto'), 'o quadro do produto repete o período consultado')
        pg.fill('#dataDe', todas[40]['data']); pg.press('#dataDe', 'Enter'); pg.wait_for_timeout(250)
        ok(texto('#erroBusca') == 'A data inicial é depois da final.', 'Enter no campo de data também busca')
        pg.fill('#dataDe', meio)
        clic('#dfDataDe .date-btn'); pg.wait_for_timeout(250)
        ok(pg.locator('#dfDataDe .date-pop.open').count() == 1 and pg.locator('#dfDataDe .date-dia.sel').count() == 1, 'o calendário da casa abre no campo de data, com o dia marcado')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        # ordem e paginas
        clic('#btnLimpar'); pg.wait_for_timeout(200)
        ok(visivel('#painelInicio') and not visivel('#painelResultado') and texto('#filtroProduto .dropdown-select-label') == 'Escolha o produto' and pg.input_value('#dataDe') == '',
           'Limpar devolve a tela ao começo: filtros em branco e nenhuma lista')
        ir(MOV); buscar('CAD-ERG-001')
        ok(len(linhas()) == 10 and texto('#paginacaoResumo') == 'Mostrando 1-10 de 49' and texto('#paginacaoPaginas') == 'Página 1 de 5', 'a lista abre com 10 por página')
        clic('#btnPaginaProxima'); pg.wait_for_timeout(150)
        ok(linhas()[0]['doc'] == todas[10]['doc'] and texto('#paginacaoPaginas') == 'Página 2 de 5', 'a segunda página continua de onde a primeira parou')
        clic('#painelMov th.ordenavel'); pg.wait_for_timeout(150)
        ls = linhas()
        ok(ls[0]['doc'] == todas[-1]['doc'] and num(ls[0]['depois']) == 24 and texto('#painelMov th.ordenavel .seta') == '▼' and texto('#paginacaoPaginas') == 'Página 1 de 5',
           'clicar em "Data e hora" inverte: a primeira linha passa a ser a de hoje, com o saldo atual')

    if secao(5, 'O documento do movimento'):
        ir(MOV); buscar('FON-BLT-013', por_pagina=100)
        ls = linhas()
        alvo = pg.evaluate("(() => { const d = Object.keys(DOCS).map(k => DOCS[k]).find(d => d.tipo === 'compra' && d.itens.length === 2 && d.itens.some(i => i.sku === 'FON-BLT-013')); return d.numero; })()")
        i = [l['doc'] for l in ls].index(alvo)
        clic('#corpoTabela tr:nth-child(%d)' % (i + 1)); pg.wait_for_timeout(450)
        ok(pg.evaluate("(() => { const d = document.getElementById('eventDrawer'); return d.classList.contains('open') && d.classList.contains('mv-doc'); })()") and texto('#docNumero') == alvo,
           'clicar no movimento abre o documento dele, no painel largo: %s' % alvo)
        leitura = texto('#docLeitura')
        ok('Fone Bluetooth Desk One entrou com 18 UN' in leitura and ('de %s UN para %s UN' % (ls[i]['antes'], ls[i]['depois'].replace(' UN', ''))) in leitura,
           'o documento repete o que a linha disse do produto: %s' % leitura)
        itens = pg.evaluate("Array.from(document.querySelectorAll('#docItens tbody tr')).map(tr => ({ sku: tr.getAttribute('data-sku'), este: tr.classList.contains('mv-este'), c: Array.from(tr.children).map(td => td.textContent.trim()) }))")
        ok(sorted(x['sku'] for x in itens) == ['CAB-HDM-009', 'FON-BLT-013'] and [x['sku'] for x in itens if x['este']] == ['FON-BLT-013'],
           'a nota traz os dois produtos que vieram juntos, e marca qual é o consultado')
        fatos = pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo .bq-fato b')).map(b => b.textContent)")
        total_itens = round(sum(num(x['c'][7]) for x in itens), 2)
        ok(fatos[0] == '2 itens' and num(fatos[3]) == total_itens == num(pg.evaluate("document.querySelector('#docItens tfoot tr').lastElementChild.textContent")),
           'quantidade de itens e valor total são a soma dos itens: %s e %s' % (fatos[0], fatos[3]))
        ok(all(abs(num(x['c'][4]) * num(x['c'][5]) - num(x['c'][7])) < 0.02 * num(x['c'][4]) for x in itens) and abs(num(fatos[1]) - sum(num(x['c'][2]) for x in itens)) < 0.011,
           'em cada item, quantidade vezes valor unitário dá o total; o peso bruto do documento é a soma dos itens')
        corpo = texto('#drawerCorpo')
        ok(all(t in corpo for t in ['Fornecedor', 'TechParts Distribuidora', 'Depósito', 'Geral', 'Emissão', 'Conferido por', 'Observação', 'Nota fiscal', alvo]),
           'de onde veio e para quem foi: fornecedor, depósito, emissão, quem conferiu, observação e a nota')
        ok('Reservado — usado quando a emissão de NF-e for habilitada' in corpo, 'ICMS aparece como reservado, igual aos outros campos fiscais do sistema')
        ok(pg.evaluate("document.querySelectorAll('#drawerCorpo a').length") == 0 and texto('#btnImprimirDoc') == 'Imprimir documento',
           'o painel não oferece link para lista que não tem o registro; a ação dele é "Imprimir documento"')

        # imprimir so o documento
        pg.evaluate("(() => { window.__n = 0; window.print = () => { window.__n++; window.__classe = document.body.classList.contains('mv-imprime-doc'); }; })()")
        clic('#btnImprimirDoc'); pg.wait_for_timeout(250)
        ok(pg.evaluate("[window.__n, window.__classe, document.body.classList.contains('mv-imprime-doc')]") == [1, True, False],
           'Imprimir chama a impressão uma vez, com a marca de "só o documento", e tira a marca depois')
        pg.evaluate("document.body.classList.add('mv-imprime-doc')"); pg.emulate_media(media='print'); pg.wait_for_timeout(200)
        papel = pg.evaluate("""(() => { const v = (s) => { const e = document.querySelector(s); return !!e && getComputedStyle(e).display !== 'none' && e.getClientRects().length > 0; };
          return { doc: v('#docItens'), lista: v('#painelMov'), filtros: v('#painelFiltros'), produto: v('#painelProduto'), botao: v('#btnImprimirDoc'), fechar: v('#drawerClose'),
                   posicao: getComputedStyle(document.getElementById('eventDrawer')).position,
                   fundo: getComputedStyle(document.querySelector('#drawerCorpo .bq-fato')).backgroundColor, tinta: getComputedStyle(document.querySelector('#docItens td')).color }; })()""")
        ok(papel == {'doc': True, 'lista': False, 'filtros': False, 'produto': False, 'botao': False, 'fechar': False, 'posicao': 'static', 'fundo': 'rgba(0, 0, 0, 0)', 'tinta': 'rgb(16, 16, 16)'},
           'no papel sai só o documento, em folha inteira, texto escuro sobre branco: %s' % papel)
        pg.evaluate("document.body.classList.remove('mv-imprime-doc')"); pg.wait_for_timeout(100)
        papel = pg.evaluate("""(() => { const v = (s) => { const e = document.querySelector(s); return !!e && getComputedStyle(e).display !== 'none' && e.getClientRects().length > 0; };
          return [v('#painelMov'), v('#painelProduto'), v('#kpiAtual'), v('#painelFiltros'), v('#btnPlanilha'), v('#docItens')]; })()""")
        ok(papel == [True, True, True, False, False, False], 'e imprimir a lista manda produto, indicadores e movimentos, sem os filtros, os botões e o painel: %s' % papel)
        pg.emulate_media(media='screen'); pg.wait_for_timeout(150)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'Esc fecha o documento')

        # pedido com mais de um item, transferencia e os movimentos sem parceiro
        dv = [l['mov'] for l in ls].index('Devolução de cliente')
        ok(ls[dv + 1]['mov'] == 'Baixa por perda' and ls[dv]['data'] == ls[dv + 1]['data'] and num(ls[dv]['antes']) == num(ls[dv + 1]['depois']),
           'a devolução com defeito entra e sai por perda no mesmo dia: o saldo do dia não muda')
        # O pedido com mais produtos do exemplo: abre pelo historico de um deles e mostra todos.
        pedido = pg.evaluate("(() => { const d = Object.keys(DOCS).map(k => DOCS[k]).filter(d => d.tipo === 'venda').sort((a, b) => b.itens.length - a.itens.length)[0]; return { numero: d.numero, skus: d.itens.map(i => i.sku), cliente: d.parceiro }; })()")
        buscar(pedido['skus'][0])
        ls = linhas()
        i = [l['doc'] for l in ls].index(pedido['numero'])
        clic('#corpoTabela tr:nth-child(%d)' % (i + 1)); pg.wait_for_timeout(400)
        corpo = texto('#drawerCorpo')
        ok(len(pedido['skus']) >= 3 and pg.evaluate("Array.from(document.querySelectorAll('#docItens tbody tr')).map(tr => tr.getAttribute('data-sku'))") == pedido['skus']
           and all(t in corpo for t in ['Cliente', pedido['cliente'], 'Vendedor', 'Expedido por', 'Pedido da loja']) and ls[i]['quem'] == pedido['cliente'],
           'pedido com %d produtos: todos aparecem, com cliente, vendedor e quem expediu (%s)' % (len(pedido['skus']), pedido['numero']))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        buscar('CAD-ERG-001', tipo='transf_saida')
        clic('#corpoTabela tr'); pg.wait_for_timeout(400)
        corpo = texto('#drawerCorpo')
        ok(texto('#docNumero') == 'TR-0091' and 'De onde saiuGalpão Centro' in corpo and 'Para onde foiLoja Física Aldeota' in corpo and 'saiu com 5 UN' in corpo,
           'a transferência mostra de onde saiu e para onde foi: TR-0091, do Galpão Centro para a Loja Física Aldeota')
        ok('Enviado porCarlos Mendes' in corpo and 'Recebido porAna Souza' in corpo, 'com quem enviou e quem recebeu')

    if secao(6, 'É só consulta'):
        fonte = secao_da_tela()
        proibido = [t for t in ['localStorage', 'gravarParametros', 'registrarAtividade', 'abrirModalConfirmacao', '.push({ data', 'btn-danger'] if t in fonte]
        ok(not proibido, 'o código da tela não grava nada: nem armazenamento, nem parâmetro, nem registro de atividade: %s' % proibido)
        ir(MOV)
        antes = pg.evaluate("JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))")
        buscar('TEC-MEC-006')
        botoes = pg.evaluate("Array.from(document.querySelectorAll('.main button, .main .drawer-link')).filter(b => b.offsetParent !== null && !b.closest('.dropdown-select') && !b.closest('.date-field') && !b.closest('.paginacao-nav') && !b.closest('.modal-card') && !b.closest('.event-drawer')).map(b => b.textContent.trim())")
        ok(botoes == ['Buscar', 'Limpar', 'Resumo por tipo', 'Imprimir lista', 'Baixar planilha'], 'os botões da tela são buscar, limpar, resumir, imprimir e baixar, cada um com um nome só: %s' % botoes)
        ok(pg.evaluate("document.querySelectorAll('#painelResultado input, #painelFiltros input[type=\"checkbox\"], #menuMaisAcoes, .selecao-bar').length") == 0, 'sem seleção, sem menu de ações e sem campo de digitar na lista')
        esperado = pg.evaluate("linhasDaConsulta().lista.length")
        with pg.expect_download(timeout=5000) as d:
            clic('#btnPlanilha')
        csv = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
        ok(d.value.suggested_filename.startswith('movimentacao-tec-mec-006-') and d.value.suggested_filename.endswith('.csv') and len(csv) - 1 == esperado == 62,
           'a planilha baixa com o histórico inteiro, não só a página: %d linhas em %s' % (len(csv) - 1, d.value.suggested_filename))
        ok(csv[0] == '"Data";"Hora";"Movimento";"Documento";"Depósito";"Cliente ou fornecedor";"Saldo anterior";"Quantidade";"Saldo atual";"Valor unitário";"Custo médio";"Valor em estoque"'
           and csv[-1].split(';')[8] == '"40"' and csv[-1].split(';')[10] == '"231,1"', 'com as colunas da tela e a última linha no saldo de hoje: %s' % csv[-1][:80])
        pg.evaluate("(() => { window.__n = 0; window.print = () => { window.__n++; window.__linhas = document.querySelectorAll('#corpoTabela tr').length; }; })()")
        clic('#btnImprimir'); pg.wait_for_timeout(250)
        ok(pg.evaluate("[window.__n, window.__linhas, document.querySelectorAll('#corpoTabela tr').length, document.body.classList.contains('mv-imprime-doc')]") == [1, 62, 10, False],
           'Imprimir manda as 62 linhas para o papel e devolve a página de 10')
        clic('#corpoTabela tr'); pg.wait_for_timeout(300); clic('#btnFecharDoc'); pg.wait_for_timeout(200)
        clic('#btnResumo'); pg.wait_for_timeout(300); clic('#btnFecharResumo'); pg.wait_for_timeout(200)
        clic('#btnLimpar'); pg.wait_for_timeout(150)
        ok(pg.evaluate("JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))") == antes,
           'depois de buscar, abrir documento, resumir, imprimir, baixar e limpar, nada mudou no que o sistema guarda')

    if secao(7, 'As vizinhas levam para cá, e a tela leva de volta'):
        ir(CE)
        pg.evaluate("(() => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); document.querySelector('#menuMaisAcoes [data-acao=\"movimentacao\"]').click(); })()")
        pg.wait_for_load_state('load'); pg.wait_for_timeout(350)
        ok(pg.url.split('/')[-1] == MOV, 'Controle de Estoques, "Mais ações": "Abrir a Movimentação de Estoque" abre a tela')
        ir(CED, '?produto=15')
        ok(texto('#btnVerMovimentacao') == 'Movimentações', 'a página do produto ganhou o botão "Movimentações", ao lado de Compra e Giro')
        clic('#btnVerMovimentacao'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.split('/')[-1] == MOV + '?busca=MON-27I-015' and texto('#painelProduto .bq-nome') == 'Monitor Desk 27" IPS' and len(linhas()) == 10 and texto('#filtroProduto .dropdown-select-label').startswith('Monitor Desk'),
           'e ele abre a tela já no histórico daquele produto, com o filtro preenchido')
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#painelProduto .mv-links a')).map(a => a.getAttribute('href'))")
        ok(hrefs == ['../estoque/%s?produto=15' % CED, '../estoque/%s?busca=MON-27I-015' % GIRO], 'de volta: a tela leva à página do produto e ao Giro, no mesmo produto: %s' % hrefs)
        clic('#painelProduto .mv-links a:nth-child(2)'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(pg.url.split('/')[-1].startswith(GIRO) and pg.evaluate("document.querySelectorAll('#corpoTabela tr').length") == 1, 'o Giro abre só com o Monitor')
        clic('#corpoTabela tr'); pg.wait_for_timeout(400)
        link = pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('#drawerCorpo a.bq-link')).find(a => a.textContent === 'Abrir na Movimentação de Estoque'); return a ? a.getAttribute('href') : null; })()")
        ok(link == '../estoque/%s?busca=MON-27I-015' % MOV, 'e o painel do Giro leva de volta ao histórico do produto: %s' % link)
        ir(MOV, '?busca=7891234000066')
        ok(texto('#painelProduto .bq-nome') == 'Teclado Mecânico Desk', 'pelo endereço, a tela acha o produto também pelo GTIN')

    if secao(8, 'Cabe na largura de referência, e nas menores'):
        # 12/out: tabela nao ganha barra de rolagem com o dado mais comprido, em 1440 e tambem em 1366 e 1280.
        ir(MOV)
        skus = pg.evaluate('PRODUTOS.map(p => p.sku)')
        for largura in (1366, 1280):
            pg.set_viewport_size({'width': largura, 'height': 950})
            ruins = []
            for sku in skus:
                ir(MOV, '?busca=' + sku)
                escolher('itensPorPagina', '100'); escolher('filtroDeposito', '5'); escolher('filtroTipoMov', 'compra'); pg.wait_for_timeout(120)
                m = pg.evaluate("(() => { const w = document.querySelector('#painelMov .estoque-table-wrap'); return [w.scrollWidth - w.clientWidth, document.documentElement.scrollWidth - window.innerWidth, "
                                "Array.from(document.querySelectorAll('#painelFiltros .dropdown-select-label')).filter(l => l.scrollWidth > l.clientWidth + 1).length]; })()")
                if m[0] > 1 or m[1] > 0 or m[2]: ruins.append((sku, m))
            ok(not ruins, 'em %d de largura, nos 15 produtos: a tabela não rola, a página não rola e nenhum filtro corta o texto: %s' % (largura, ruins[:3]))
        ok(pg.evaluate("new Set(Array.from(document.querySelectorAll('.mv-campos .form-field')).map(e => Math.round(e.getBoundingClientRect().top))).size") == 2,
           'em tela estreita as duas datas descem juntas para a linha de baixo')
        pg.set_viewport_size({'width': 1440, 'height': 950})
        for tema in ('dark', 'claro'):
            ir(MOV, '?busca=TEC-MEC-006')
            if tema == 'claro':
                pg.evaluate("document.body.classList.remove('dark')"); pg.wait_for_timeout(150)
            escolher('itensPorPagina', '100'); pg.wait_for_timeout(150)
            ok(pg.evaluate("(() => { const w = document.querySelector('#painelMov .estoque-table-wrap'); return w.scrollWidth <= w.clientWidth + 1 && document.documentElement.scrollWidth <= window.innerWidth; })()"),
               'tema %s, 1440 de largura: as nove colunas cabem no quadro e a página não rola para o lado' % tema)
            # As opcoes de texto mais comprido de cada filtro: e com elas que o campo tem de caber.
            escolher('filtroDeposito', '5'); escolher('filtroTipoMov', 'compra'); escolher('filtroProduto', 'KIT-MNT-010'); pg.wait_for_timeout(150)
            rotulos = pg.evaluate("Array.from(document.querySelectorAll('#painelFiltros .dropdown-select-label')).map(l => [l.textContent, l.scrollWidth <= l.clientWidth + 1])")
            ok(rotulos == [['Showroom Parceiro Norte', True], ['Kit Manutenção Desk Tech', True], ['Entrada por nota de compra', True]],
               'tema %s: os três filtros mostram o texto inteiro, sem reticências, mesmo na opção mais comprida' % tema)
            clic('#corpoTabela tr'); pg.wait_for_timeout(400)
            ok(pg.evaluate("(() => { const d = document.getElementById('eventDrawer'), t = document.getElementById('docItens'); return d.scrollWidth <= d.clientWidth + 1 && t.getBoundingClientRect().right <= d.getBoundingClientRect().right; })()"),
               'tema %s: a tabela de itens cabe no painel do documento' % tema)

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
