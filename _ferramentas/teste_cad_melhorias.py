# -*- coding: utf-8 -*-
# Cadastros: os itens C2 em diante da lista de melhorias (13/out/2026).
#
#   [1] C2  o painel do fornecedor mostra as ordens em aberto e o que falta receber, a ultima
#           compra, as contas a pagar em aberto e os produtos em que ele e o fornecedor padrao, com
#           link. O cadastro tem os fornecedores que as telas de compra e de financas usam, e cada
#           numero do painel bate com a tela que e dona dele.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

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
        da_cp = pg.evaluate("TITULOS.filter(t => saldoDe(t) > 0 && ['paga', 'cancelada'].indexOf(situacaoDe(t)) < 0).map(t => [t.id, fornDe(t.fornId).nome, t.vencIso, Math.round(saldoDe(t) * 100) / 100])")
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
        ok(sorted(pg.evaluate("CONTAS_DO_CADASTRO.map(x => [x.id, x.fornecedor, x.vencimento, x.saldo])")) == sorted(x for x in da_cp if x[1] in nomes) and len([x for x in da_cp if x[1] in nomes]) == 3,
           'o espelho das contas bate com as contas em aberto de Contas a Pagar, dos fornecedores do cadastro')
        ok(pg.evaluate("PRODUTOS_DO_CADASTRO.map(x => [x.sku, x.nome, x.fornecedor]).sort()") == da_nec and len(da_nec) >= 10, 'o espelho dos produtos bate com o fornecedor padrao de Necessidades de Compra: %d produtos' % len(da_nec))

        def painel(nome):
            pg.evaluate("(n) => abrirPreviewFornecedor(FORNECEDORES.find(f => f.nome === n).id)", nome); pg.wait_for_timeout(350)
            return pg.evaluate("""() => { const t = (id) => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
                const h = (id) => { const a = document.querySelector('#' + id + ' a'); return a ? a.getAttribute('href') : null; };
                return { ordens: t('pfOrdens'), hOrdens: h('pfOrdens'), falta: t('pfAReceber'), ultima: t('pfUltima'), contas: t('pfContas'), hContas: h('pfContas'), deve: t('pfDeve'),
                         produtos: Array.from(document.querySelectorAll('#pfProdutos a')).map(a => [a.textContent, a.getAttribute('href')]),
                         semProduto: document.getElementById('pfProdutos').textContent.trim() }; }""")

        a = painel('TechParts Distribuidora')
        ok([a['ordens'], a['falta'], a['ultima']] == ['2 ordens', 'R$ 5.073,80', '10/09/2026 · R$ 890,00 · ordem nº 12'], 'TechParts: duas ordens em aberto, o que falta receber e a ultima compra: %s' % [a['ordens'], a['falta'], a['ultima']])
        ok([a['contas'], a['deve']] == ['1 conta', 'R$ 2.460,00'], 'e uma conta a pagar em aberto, com o saldo: %s' % [a['contas'], a['deve']])
        ok(a['hOrdens'] == '../estoque/' + OC + '?busca=TechParts%20Distribuidora' and a['hContas'] == '../financas/' + CP + '?busca=TechParts%20Distribuidora', 'as duas linhas levam as ordens e as contas dele')
        ok(sorted(x[0] for x in a['produtos']) == sorted(x[1] for x in da_nec if x[2] == 'TechParts Distribuidora') and len(a['produtos']) == 6 and a['produtos'][0][1].startswith('../estoque/' + NEC + '?busca='),
           'e a lista dos produtos em que ele e o fornecedor padrao, cada um com link: %d produtos' % len(a['produtos']))
        b = painel('Tecidos Ceará S/A')
        ok([b['ordens'], b['falta'], b['contas'], b['deve']] == ['2 ordens', 'R$ 13.432,00', 'nenhuma', '—'], 'Tecidos Ceara: o que falta receber soma a ordem em andamento e a em aberto, e nao ha conta: %s' % [b['ordens'], b['falta'], b['contas']])
        c = painel('Distribuidora Nordeste Ltda')
        ok([c['ordens'], c['falta'], c['ultima'], c['contas'], c['deve'], c['semProduto']] == ['nenhuma', '—', 'nunca comprou', 'nenhuma', '—', 'nenhum produto'] and c['hOrdens'] is None,
           'fornecedor de quem nunca se comprou: o painel diz isso, sem link para lista vazia: %s' % [c['ordens'], c['ultima'], c['semProduto']])

        # Os links caem em lista que tem o registro.
        ir(OC, '?busca=TechParts%20Distribuidora')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).length") == len([o for o in da_oc if o[1] == 'TechParts Distribuidora']) and 'não tem esse registro' not in pg.inner_text('#faixaBuscaLink'),
           'o link das ordens abre Ordens de Compra com as ordens dele')
        ir(CP, '?busca=TechParts%20Distribuidora')
        ok('TechParts Distribuidora' in pg.inner_text('.main') and 'não tem esse registro' not in pg.inner_text('#faixaBuscaLink'), 'o link das contas abre Contas a Pagar com a conta dele')
        ir(NEC, '?busca=SUP-MON-003')
        ok('Suporte Monitor Duplo' in pg.inner_text('#corpoTabela'), 'e o link do produto abre Necessidades de Compra no produto')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
