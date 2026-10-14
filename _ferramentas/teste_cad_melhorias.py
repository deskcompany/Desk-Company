# -*- coding: utf-8 -*-
# Cadastros: os itens C2 em diante da lista de melhorias (13/out/2026).
#
#   [1] C2  o painel do fornecedor mostra as ordens em aberto e o que falta receber, a ultima
#           compra, as contas a pagar em aberto e de quantos produtos ele e o fornecedor padrao. O
#           cadastro tem os fornecedores que as telas de compra e de financas usam, e cada numero do
#           painel bate com a tela que e dona dele;
#   [2]     a lista dos produtos mora no cadastro do fornecedor, na aba Produtos Fornecidos (pedido
#           do usuario em 13/out): o custo neste fornecedor e o pedido minimo se editam, o resto vem
#           do produto, com o lucro por unidade. Busca padrao para adicionar, lixeira para tirar.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

FORN_D = 'pagina-cadastros-fornecedores-detalhe.html'
FORN, OC, CP, NEC = 'pagina-cadastros-fornecedores.html', 'pagina-estoque-ordens-compra.html', 'pagina-financas-contas-pagar.html', 'pagina-estoque-necessidades-compra.html'
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

    if secao(1, 'C2: o painel do fornecedor mostra o que as outras telas tem dele'):
        # O que cada tela dona do numero diz, lido dela.
        ir(OC); pg.evaluate("localStorage.removeItem('deskOrdensGeradas')"); ir(OC)
        da_oc = pg.evaluate("""ORDENS.map(o => { const aberta = o.situacao === 'aberto' || o.situacao === 'andamento', itens = ITENS_OC[o.numero];
            const falta = itens ? itens.reduce((s, i) => s + Math.max(0, i.qtd - i.recebido) * i.preco, 0) : o.total;
            return [o.numero, o.fornecedor, o.data, o.previsto, o.total, o.situacao, aberta ? Math.round(falta * 100) / 100 : 0]; }).sort((a, b) => a[0] - b[0])""")
        ir(CP)
        da_cp = pg.evaluate("TITULOS.filter(t => saldoDe(t) > 0 && ['paga', 'cancelada'].indexOf(situacaoDe(t)) < 0).map(t => [t.id, fornDe(t.fornId).nome, Math.round(saldoDe(t) * 100) / 100])")
        ir(NEC)
        da_nec = pg.evaluate("PRODUTOS.map(p => [p.sku, p.nome, FORNECEDORES[retrato(p).f.fornecedor] || '']).filter(x => x[2]).sort()")

        ir(FORN)
        ok(not erros, 'o cadastro abre sem erro de JavaScript: %s' % erros[:2])
        nomes = pg.evaluate("FORNECEDORES.filter(f => f.status === 'ativo').map(f => f.nome)")
        usados = sorted(set(o[1] for o in da_oc))
        ok(len(usados) == 7 and not [n for n in usados if n not in nomes], 'os sete fornecedores das ordens de compra estao no cadastro, com o mesmo nome: %s' % [n for n in usados if n not in nomes])
        ok(pg.evaluate("new Set(FORNECEDORES.map(f => f.nome)).size === FORNECEDORES.length && new Set(FORNECEDORES.map(f => f.documento)).size === FORNECEDORES.length"), 'e nenhum nome ou documento se repete no cadastro')
        ok(pg.evaluate("ORDENS_DO_CADASTRO.map(o => [o.numero, o.fornecedor, o.data, o.previsto, o.total, o.situacao, o.aReceber]).sort((a, b) => a[0] - b[0])") == da_oc,
           'o espelho das ordens bate com Ordens de Compra, inclusive no que falta receber: %d ordens' % len(da_oc))
        ok(sorted(pg.evaluate("CONTAS_DO_CADASTRO.map(x => [x.id, x.fornecedor, x.saldo])")) == sorted(x for x in da_cp if x[1] in nomes) and len([x for x in da_cp if x[1] in nomes]) == 3,
           'o espelho das contas bate com as contas em aberto de Contas a Pagar, dos fornecedores do cadastro')
        ok(pg.evaluate("PRODUTOS_DO_CADASTRO.map(x => [x.sku, x.nome, x.fornecedor]).sort()") == da_nec and len(da_nec) >= 10, 'o espelho dos produtos bate com o fornecedor padrao de Necessidades de Compra: %d produtos' % len(da_nec))

        def painel(nome):
            pg.evaluate("(n) => abrirPreviewFornecedor(FORNECEDORES.find(f => f.nome === n).id)", nome); pg.wait_for_timeout(350)
            return pg.evaluate("""() => { const t = (id) => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
                const h = (id) => { const a = document.querySelector('#' + id + ' a'); return a ? a.getAttribute('href') : null; };
                return { ordens: t('pfOrdens'), hOrdens: h('pfOrdens'), falta: t('pfAReceber'), ultima: t('pfUltima'), contas: t('pfContas'), hContas: h('pfContas'), deve: t('pfDeve'),
                         produtos: t('pfProdutos'), linksDeProduto: document.querySelectorAll('#drawerBody a[href*="necessidades"]').length,
                         corpo: document.getElementById('drawerBody').textContent }; }""")

        a = painel('TechParts Distribuidora')
        ok([a['ordens'], a['falta'], a['ultima']] == ['2 ordens', 'R$ 5.073,80', '10/09/2026 · R$ 890,00 · ordem nº 12'], 'TechParts: duas ordens em aberto, o que falta receber e a ultima compra: %s' % [a['ordens'], a['falta'], a['ultima']])
        ok([a['contas'], a['deve']] == ['1 conta', 'R$ 2.460,00'], 'e uma conta a pagar em aberto, com o saldo: %s' % [a['contas'], a['deve']])
        ok(a['hOrdens'] == '../estoque/' + OC + '?busca=TechParts%20Distribuidora' and a['hContas'] == '../financas/' + CP + '?busca=TechParts%20Distribuidora', 'as duas linhas levam as ordens e as contas dele')
        ok(a['produtos'] == '6 produtos' and a['linksDeProduto'] == 0 and 'aba Produtos Fornecidos' in a['corpo'],
           'o painel diz de quantos produtos ele e o fornecedor padrao, e que a lista fica no cadastro: %s' % a['produtos'])
        b = painel('Tecidos Ceará S/A')
        ok([b['ordens'], b['falta'], b['contas'], b['deve']] == ['2 ordens', 'R$ 13.432,00', 'nenhuma', '—'], 'Tecidos Ceara: o que falta receber soma a ordem em andamento e a em aberto, e nao ha conta: %s' % [b['ordens'], b['falta'], b['contas']])
        c = painel('Distribuidora Nordeste Ltda')
        ok([c['ordens'], c['falta'], c['ultima'], c['contas'], c['deve'], c['produtos']] == ['nenhuma', '—', 'nunca comprou', 'nenhuma', '—', 'nenhum produto'] and c['hOrdens'] is None,
           'fornecedor de quem nunca se comprou: o painel diz isso, sem link para lista vazia: %s' % [c['ordens'], c['ultima'], c['produtos']])

        # Os links caem em lista que tem o registro.
        ir(OC, '?busca=TechParts%20Distribuidora')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).length") == len([o for o in da_oc if o[1] == 'TechParts Distribuidora']) and 'não tem esse registro' not in pg.inner_text('#faixaBuscaLink'),
           'o link das ordens abre Ordens de Compra com as ordens dele')
        ir(CP, '?busca=TechParts%20Distribuidora')
        ok('TechParts Distribuidora' in pg.inner_text('.main') and 'não tem esse registro' not in pg.inner_text('#faixaBuscaLink'), 'o link das contas abre Contas a Pagar com a conta dele')

    if secao(2, 'A lista dos produtos mora no cadastro do fornecedor, na aba Produtos Fornecidos'):
        ir(NEC)
        da_nec = pg.evaluate("PRODUTOS.map(p => { const r = retrato(p); return [p.sku, p.nome, p.unidade, p.gtin, p.custoMedio, Math.round(r.vendaDia * 30 * 10) / 10, FORNECEDORES[r.f.fornecedor] || '']; }).sort()")
        ir(FORN)
        da_lista = pg.evaluate("(() => { const f = FORNECEDORES.find(x => x.nome === 'TechParts Distribuidora'); return [f.nome, f.codigo, f.documento, f.email, f.telefone, f.cidade, f.estado]; })()")
        ir(FORN_D, '?editar=1')
        ok(not erros, 'o cadastro abre sem erro de JavaScript: %s' % erros[:2])
        na_pagina = pg.evaluate("['inputNome', 'inputCodigo', 'inputDocumento', 'inputEmail', 'inputTelefone', 'inputCidade', 'inputEstado'].map(id => document.getElementById(id).value)")
        ok(na_pagina == da_lista and pg.inner_text('#tituloFornecedor') == 'TechParts Distribuidora', 'o cadastro de exemplo e a TechParts, com os mesmos dados que ela tem na lista: %s' % na_pagina[:3])
        abas = pg.evaluate("Array.from(document.querySelectorAll('.tab-item')).map(e => e.textContent.trim())")
        ok(abas == ['Dados Gerais', 'Dados Complementares', 'Anexos', 'Produtos Fornecidos', 'Observações'], 'a aba Produtos Fornecidos vem antes de Observacoes: %s' % abas[-2:])
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"produtos\"]').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("CATALOGO.map(x => [x.sku, x.nome, x.un, x.gtin, x.custoMedio, x.giroMensal, x.padrao]).sort()") == da_nec and len(da_nec) == 15,
           'o catalogo da aba bate com Necessidades de Compra: nome, unidade, custo medio, giro mensal e fornecedor padrao dos 15 produtos')

        def linhas():
            return pg.evaluate("""Array.from(document.querySelectorAll('#pfCorpo tr')).map(tr => { const c = tr.children;
                return { sku: tr.getAttribute('data-sku'), padrao: !!tr.querySelector('.pf-padrao'), custo: c[1].querySelector('input').value, minimo: c[2].querySelector('input').value,
                         medio: c[3].textContent.trim(), giro: c[4].textContent.replace(/\\s+/g, ' ').trim(), venda: c[5].textContent.trim(), lucro: c[6].textContent.replace(/\\s+/g, ' ').trim() }; })""")

        def campo(sku, qual, valor):
            pg.fill('#pfCorpo tr[data-sku="%s"] input[data-campo="%s"]' % (sku, qual), valor); pg.wait_for_timeout(150)

        L = linhas()
        padrao_la = sorted(x[0] for x in da_nec if x[6] == 'TechParts Distribuidora')
        ok(len(L) == 7 and sorted(l['sku'] for l in L if l['padrao']) == padrao_la and [l['sku'] for l in L if not l['padrao']] == ['LUM-LED-004'],
           'a lista traz os seis produtos em que ela e o fornecedor padrao, marcados, e um que ela tambem entrega: %d linhas' % len(L))
        sup = [l for l in L if l['sku'] == 'SUP-MON-003'][0]
        ok(sup == {'sku': 'SUP-MON-003', 'padrao': True, 'custo': '89,00', 'minimo': '5', 'medio': 'R$ 138,40', 'giro': '3,5 UN/mês', 'venda': 'R$ 249,90', 'lucro': 'R$ 160,9064% do preço'},
           'cada linha tem o custo e o pedido minimo deste fornecedor, o custo medio, o giro mensal, o preco de venda e o lucro por unidade: %s' % [sup['custo'], sup['minimo'], sup['lucro']])
        ok(pg.inner_text('#pfResumo') == '7 produtos · fornecedor padrão de 6.' and pg.evaluate("(() => { const t = document.getElementById('pfTabela'); return t.scrollWidth <= t.closest('.tab-panel').clientWidth; })()"),
           'o rodape da lista resume, e a tabela cabe na pagina: %s' % pg.inner_text('#pfResumo'))

        campo('SUP-MON-003', 'custo', '100')
        ok([l for l in linhas() if l['sku'] == 'SUP-MON-003'][0]['lucro'] == 'R$ 149,9060% do preço' and pg.evaluate("document.activeElement.getAttribute('data-campo')") == 'custo',
           'mudar o custo refaz o lucro na hora, sem tirar o foco do campo')
        campo('SUP-MON-003', 'custo', '300')
        ok([l for l in linhas() if l['sku'] == 'SUP-MON-003'][0]['lucro'] == '− R$ 50,10prejuízo', 'custo acima do preco de venda aparece como prejuizo')
        campo('SUP-MON-003', 'custo', '')
        ok([l for l in linhas() if l['sku'] == 'SUP-MON-003'][0]['lucro'] == '—' and pg.evaluate("document.querySelector('#pfCorpo tr[data-sku=\"SUP-MON-003\"] input[data-campo=\"custo\"]').classList.contains('pf-erro')"),
           'custo em branco nao vira zero: o lucro fica sem numero e o campo e marcado')
        pg.evaluate("document.getElementById('btnSalvarFornecedor').click()"); pg.wait_for_timeout(300)
        ok(FORN_D in pg.url and pg.evaluate("(() => { const e = document.getElementById('pfErro'), a = document.querySelector('.tab-item.active'); return !!e && e.classList.contains('show') && !!a && a.getAttribute('data-tab') === 'produtos'; })()"),
           'e salvar com custo em branco nao passa: a tela mostra a aba e o que falta')
        campo('SUP-MON-003', 'custo', '89,00')

        pg.fill('#pfBusca', 'tecl'); pg.wait_for_timeout(250)
        ok('Já está na lista deste fornecedor' in pg.inner_text('#pfSugestoes'), 'a busca nao oferece o que ja esta na lista: %s' % pg.inner_text('#pfSugestoes')[:40])
        pg.fill('#pfBusca', 'cad'); pg.wait_for_timeout(250)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#pfSugestoes .sugestao-nome')).map(e => e.textContent)") == ['Cadeira Ergonômica Pro'], 'pesquisar acha o produto pelo nome')
        pg.evaluate("document.querySelector('#pfSugestoes .sugestao-item').click()"); pg.wait_for_timeout(300)
        nova = linhas()[-1]
        ok(len(linhas()) == 8 and nova == {'sku': 'CAD-ERG-001', 'padrao': False, 'custo': '742,30', 'minimo': '1', 'medio': 'R$ 742,30', 'giro': '7,7 UN/mês', 'venda': 'R$ 1.299,00', 'lucro': 'R$ 556,7043% do preço'},
           'clicar no produto desce para a lista com os dados dele, o custo medio como custo e pedido minimo 1: %s' % [nova['sku'], nova['custo'], nova['minimo'], nova['lucro']])
        ok(pg.input_value('#pfBusca') == '' and pg.evaluate("(() => { const a = document.activeElement; return a.getAttribute('data-campo') === 'custo' && a.closest('tr').getAttribute('data-sku') === 'CAD-ERG-001'; })()"),
           'a busca limpa, e o foco vai para o custo do produto que entrou')
        pg.fill('#pfBusca', 'MAT-TEC'); pg.wait_for_timeout(250); pg.press('#pfBusca', 'Enter'); pg.wait_for_timeout(300)
        mat = linhas()[-1]
        ok(mat['sku'] == 'MAT-TEC-008' and mat['venda'] == 'não é vendido' and mat['lucro'] == '—' and mat['giro'] == '9 M/mês', 'Enter adiciona o primeiro da busca; materia-prima entra sem preco de venda e sem lucro: %s' % [mat['sku'], mat['venda']])
        ok(pg.inner_text('#infoPendente') != 'Nenhuma alteração pendente.', 'a barra de salvar acusa alteracao pendente: %s' % pg.inner_text('#infoPendente'))
        pg.evaluate("document.querySelector('#pfCorpo tr[data-sku=\"CAD-ERG-001\"] [data-remover]').click()"); pg.wait_for_timeout(250)
        ok([l['sku'] for l in linhas()][-2:] == ['LUM-LED-004', 'MAT-TEC-008'] and pg.inner_text('#pfResumo') == '8 produtos · fornecedor padrão de 6.', 'a lixeira tira o produto da lista: %s' % pg.inner_text('#pfResumo'))
        # Laco com teto: sem ele, uma lixeira que nao remove prendia a suite ate estourar o tempo do selo (13/out).
        pg.evaluate("(() => { for (let n = 0; n < 30 && document.querySelector('#pfCorpo [data-remover]'); n++) document.querySelector('#pfCorpo [data-remover]').click(); })()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.getElementById('pfVazio').offsetParent !== null && document.getElementById('pfTabela').offsetParent === null"), 'sem produto nenhum, a aba diz isso e convida a pesquisar')

        ir(FORN_D)   # em leitura
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"produtos\"]').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.body.classList.contains('modo-leitura') && document.getElementById('pfBusca').offsetParent === null && document.querySelector('#pfCorpo [data-remover]').offsetParent === null && document.querySelectorAll('#pfCorpo tr').length === 7"),
           'em leitura a lista aparece inteira, sem busca e sem lixeira')
        ir(FORN_D, '?novo=1')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"produtos\"]').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.querySelectorAll('#pfCorpo tr').length === 0 && document.getElementById('pfVazio').offsetParent !== null && document.getElementById('pfBusca').offsetParent !== null"),
           'fornecedor novo abre sem produto nenhum, com a busca pronta')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
