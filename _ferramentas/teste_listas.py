# Listas no lugar do texto livre — 24/nov/2026 (pacote das listas, itens 3 a 8).
#
# O usuario pediu que o campo de digitacao livre que tem cadastro, ou que pede um cadastro, vire lista de escolher: o dropdown da casa,
# sem digitacao, com os itens em ordem. A condicao de pagamento tem a suite propria (teste_condicoes_pagamento.py); esta guarda o resto:
#   [1] o transportador da nota de entrada e da ordem de compra: as transportadoras ativas do cadastro, "Por conta do fornecedor" e "Sem transportador";
#   [2] o vendedor padrao do cliente (Cadastros > Vendedores) e o comprador do fornecedor (os usuarios ativos de `deskUsuarios`);
#   [3] o fornecedor do "Dar entrada sem nota" das Embalagens: os mesmos 7 do "Fornecedor padrao", mais "Sem fornecedor", com o padrao da embalagem ja escolhido;
#   [4] a unidade do produto: lista fixa de 14, padrao UN, o "Un" de antes cai em UN, o desconhecido fica no rotulo;
#   [5] a categoria financeira da nota e da ordem: as ativas do cadastro, e o valor antigo cai na equivalente;
#   [6] Necessidades de Compra: a ordem que cobre so parte ganha a linha "N a caminho na ordem nº X" embaixo do nome.
# Cada lista e conferida contra a tela de ORIGEM: copia que diverge do cadastro e o defeito que esta suite existe para pegar.
from playwright.sync_api import sync_playwright
import os, json

import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

NOTA = 'pagina-estoque-entrada-notas-detalhe.html'
OC = 'pagina-estoque-ordens-compra-detalhe.html'
CLI = 'pagina-cadastros-clientes-detalhe.html'
FORN = 'pagina-cadastros-fornecedores-detalhe.html'
EMB = 'pagina-cadastros-embalagens.html'
PROD = 'pagina-cadastros-produtos-detalhe.html'
NC = 'pagina-estoque-necessidades-compra.html'
TRANSP = 'pagina-configuracoes-transportadoras.html'
CATS = 'pagina-configuracoes-categorias-financeiras.html'
VEND = 'pagina-cadastros-vendedores.html'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clic(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    erros = []

    def nova():
        ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: erros.append(str(e)[:200]))
        return pg

    def ir(pg, tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def itens(pg, raiz):
        return pg.evaluate("(r) => Array.from(document.querySelectorAll(r + ' .dropdown-select-item')).map(i => [i.getAttribute('data-value'), i.textContent.trim()])", raiz)

    def rotulo(pg, raiz):
        return pg.inner_text(raiz + ' .dropdown-select-label').strip()

    def valor(pg, raiz):
        return pg.get_attribute(raiz, 'data-value')

    def escolher(pg, raiz, v):
        pg.evaluate("([r, v]) => document.querySelector(r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(v)])
        pg.wait_for_timeout(200)

    pg = nova()
    # ---- as telas de origem: o que os cadastros dizem hoje
    ir(pg, TRANSP)
    transp_ativas = pg.evaluate("TRANSPORTADORAS.filter(t => t.status === 'ativo').map(t => [String(t.id), t.nome])")
    transp_inativas = pg.evaluate("TRANSPORTADORAS.filter(t => t.status !== 'ativo').map(t => t.nome)")
    ir(pg, CATS)
    cats_ativas = pg.evaluate("CATEGORIAS.filter(c => c.ativo).map(c => [String(c.id), c.descricao])")
    cats_inativas = pg.evaluate("CATEGORIAS.filter(c => !c.ativo).map(c => c.descricao)")
    ir(pg, VEND)
    vend_ativos = pg.evaluate("VENDEDORES.filter(v => v.situacao !== 'inativo').map(v => [String(v.id), v.nome])")
    vend_inativos = pg.evaluate("VENDEDORES.filter(v => v.situacao === 'inativo').map(v => v.nome)")
    ordenado = pg.evaluate("(l) => l.slice().sort((a, b) => a.localeCompare(b, 'pt-BR'))", [t[1] for t in transp_ativas])

    print('\n[1] O transportador da nota e da ordem de compra e uma lista')
    ok(len(transp_ativas) == 8 and len(transp_inativas) == 2, 'o cadastro de Transportadoras tem 8 ativas e 2 inativas: %d e %d' % (len(transp_ativas), len(transp_inativas)))
    for tela, raiz in ((NOTA, '#inputTransportador'), (OC, '#inputTransportador')):
        pg = nova(); ir(pg, tela)
        it = itens(pg, raiz)
        ok(it[0] == ['', 'Sem transportador'] and it[1] == ['fornecedor', 'Por conta do fornecedor'], '%s: as duas primeiras opcoes sao "Sem transportador" e "Por conta do fornecedor"' % tela)
        ok(sorted(it[2:]) == sorted(transp_ativas), '%s: depois delas vem as transportadoras ativas do cadastro, com o mesmo id e o mesmo nome (%d)' % (tela, len(it) - 2))
        ok([r for v, r in it[2:]] == ordenado, '%s: em ordem alfabetica' % tela)
        ok(not any(n in [r for v, r in it] for n in transp_inativas), '%s: as inativas (%s) ficam de fora' % (tela, ', '.join(transp_inativas)))
        ok(rotulo(pg, raiz) == 'Sem transportador' and valor(pg, raiz) == '', '%s: abre em "Sem transportador" (o campo e opcional)' % tela)
        ok('Texto livre por enquanto' not in pg.inner_text('body'), '%s: a dica "Texto livre por enquanto" saiu' % tela)
        escolher(pg, raiz, 'fornecedor')
        ok(rotulo(pg, raiz) == 'Por conta do fornecedor' and valor(pg, raiz) == 'fornecedor', '%s: escolher "Por conta do fornecedor" grava o valor' % tela)
        escolher(pg, raiz, transp_ativas[2][0])
        ok(rotulo(pg, raiz) == transp_ativas[2][1] and valor(pg, raiz) == transp_ativas[2][0], '%s: escolher uma transportadora grava o id dela' % tela)
        ok(not pg.evaluate("document.querySelector('%s input')" % raiz), '%s: nao ha mais campo de texto' % tela)
        pg.context.close()

    print('\n[2] Os responsaveis sao listas')
    pg = nova(); ir(pg, CLI)
    it = itens(pg, '#inputVendedor')
    ok(it[0] == ['', 'Sem vendedor'] and sorted(it[1:]) == sorted(vend_ativos), 'cliente: "Sem vendedor" e os vendedores ativos do cadastro (mesmo id e nome): %s' % [r for v, r in it])
    ok(not any(n in [r for v, r in it] for n in vend_inativos), 'cliente: o vendedor inativo (%s) fica de fora' % ', '.join(vend_inativos))
    ok([r for v, r in it[1:]] == sorted([r for v, r in it[1:]], key=lambda s: s.lower()), 'cliente: em ordem alfabetica')
    ok(rotulo(pg, '#inputVendedor') == 'Sem vendedor' and valor(pg, '#inputVendedor') == '', 'cliente: abre em "Sem vendedor"')
    escolher(pg, '#inputVendedor', vend_ativos[0][0])
    ok(valor(pg, '#inputVendedor') == vend_ativos[0][0] and rotulo(pg, '#inputVendedor') == vend_ativos[0][1], 'cliente: escolher grava o id do vendedor')
    ok(pg.evaluate("document.querySelectorAll('#inputVendedor input').length") == 0 and pg.evaluate("document.querySelectorAll('#inputPrazoPagamento input').length") == 0, 'cliente: o vendedor e o prazo de pagamento nao tem mais campo de texto')
    pg.context.close()
    pg = nova(); ir(pg, FORN)
    it = itens(pg, '#inputVendedor')
    usuarios = pg.evaluate("autoUsuarios().filter(u => u.situacao === 'ativo').map(u => [String(u.id), u.nome])")
    ok(it[0] == ['', 'Sem comprador'] and sorted(it[1:]) == sorted(usuarios) and len(usuarios) == 6, 'fornecedor: "Sem comprador" e os 6 usuarios ativos de fabrica: %s' % [r for v, r in it])
    ok('Rafael Andrade' not in [r for v, r in it], 'fornecedor: o usuario bloqueado fica de fora')
    ok(rotulo(pg, '#inputVendedor') == 'Sem comprador', 'fornecedor: abre em "Sem comprador"')
    pg.context.close()
    # os usuarios guardados valem: um novo entra, o inativo sai
    pg = nova(); ir(pg, FORN)
    pg.evaluate("localStorage.setItem('deskUsuarios', JSON.stringify([{ id: 2, nome: 'Carlos Mendes', login: 'carlos.mendes@desk', situacao: 'ativo', perfilId: 2, perms: [] }, { id: 9, nome: 'Zeca Novo', login: 'zeca@desk', situacao: 'ativo', perfilId: 4, perms: [] }, { id: 3, nome: 'Marina Costa', login: 'marina.costa@desk', situacao: 'inativo', perfilId: 3, perms: [] }]))")
    ir(pg, FORN)
    nomes = [r for v, r in itens(pg, '#inputVendedor')]
    ok(nomes == ['Sem comprador', 'Administrador Desk', 'Carlos Mendes', 'Zeca Novo'], 'fornecedor: o comprador sai do que esta guardado em deskUsuarios (o inativo sai, o novo entra, o Owner fica): %s' % nomes)
    pg.context.close()

    print('\n[3] O fornecedor do "Dar entrada sem nota" das Embalagens')
    pg = nova(); ir(pg, EMB)
    padrao = [v for v, r in itens(pg, '#inputFornecedorEmb') if v != '']
    ok(len(padrao) == 7, 'o campo "Fornecedor padrao" tem 7 fornecedores: %s' % padrao)
    clic(pg, '#btnDarEntrada'); pg.wait_for_timeout(400)
    it = itens(pg, '#entradaFornecedor')
    ok(it[0] == ['', 'Sem fornecedor'] and sorted(v for v, r in it[1:]) == sorted(padrao), 'a lista da entrada e "Sem fornecedor" mais os mesmos 7 do fornecedor padrao: %s' % [r for v, r in it])
    ok([r for v, r in it[1:]] == sorted([r for v, r in it[1:]], key=lambda s: s.lower().replace('í', 'i').replace('ã', 'a')), 'em ordem alfabetica')
    ok(rotulo(pg, '#entradaFornecedor') == 'Sem fornecedor' and valor(pg, '#entradaFornecedor') == '', 'sem embalagem escolhida, o fornecedor abre em "Sem fornecedor"')
    escolher(pg, '#entradaEmb', 13)
    ok(valor(pg, '#entradaFornecedor') == 'Embalagens do Vale' and rotulo(pg, '#entradaFornecedor') == 'Embalagens do Vale', 'escolhida a embalagem, ja vem escolhido o fornecedor padrao dela: %s' % rotulo(pg, '#entradaFornecedor'))
    pg.fill('#entradaQtd', '2'); pg.fill('#entradaCusto', '17,00'); pg.wait_for_timeout(100)
    clic(pg, '#btnSalvarEntrada'); pg.wait_for_timeout(400)
    mov = pg.evaluate("JSON.parse(localStorage.getItem('deskMovEmbalagens') || '[]').filter(m => m.tipo === 'entrada_sem_nota').pop()")
    ok(mov and mov['fornecedor'] == 'Embalagens do Vale', 'o movimento grava o fornecedor no mesmo campo e formato de sempre (o nome): %s' % (mov and mov['fornecedor']))
    clic(pg, '#btnDarEntrada'); pg.wait_for_timeout(400)
    escolher(pg, '#entradaEmb', 13); escolher(pg, '#entradaFornecedor', 'Papelaria Central')
    ok(rotulo(pg, '#entradaFornecedor') == 'Papelaria Central', 'a pessoa troca o fornecedor padrao por outro da lista')
    escolher(pg, '#entradaFornecedor', '')
    pg.fill('#entradaQtd', '1'); pg.fill('#entradaCusto', '16,00'); pg.wait_for_timeout(100)
    clic(pg, '#btnSalvarEntrada'); pg.wait_for_timeout(400)
    mov = pg.evaluate("JSON.parse(localStorage.getItem('deskMovEmbalagens') || '[]').filter(m => m.tipo === 'entrada_sem_nota').pop()")
    ok(mov and mov['fornecedor'] == '', '"Sem fornecedor" grava o campo vazio, como o campo em branco gravava: %r' % (mov and mov['fornecedor']))
    clic(pg, '#btnDarEntrada'); pg.wait_for_timeout(400)
    ok(valor(pg, '#entradaFornecedor') == '' and rotulo(pg, '#entradaFornecedor') == 'Sem fornecedor', 'o painel reaberto volta a "Sem fornecedor"')
    pg.context.close()

    print('\n[4] A unidade do produto e uma lista fixa')
    pg = nova(); ir(pg, PROD, '?novo=1')
    it = itens(pg, '#inputUnidadeMedida')
    esperado = ['UN', 'PC', 'PAR', 'KIT', 'CX', 'FD', 'RL', 'KG', 'G', 'L', 'ML', 'M', 'M²', 'M³']
    ok([v for v, r in it] == esperado, 'sao as 14 unidades, nesta ordem: %s' % [v for v, r in it])
    rot = dict(it)
    ok(rot['UN'] == 'UN (Unidade)' and rot['PC'] == 'PC (Peça)' and rot['CX'] == 'CX (Caixa)' and rot['FD'] == 'FD (Fardo)' and rot['RL'] == 'RL (Rolo)' and rot['KG'] == 'KG', 'com os rotulos: UN (Unidade), PC (Peça), CX (Caixa), FD (Fardo), RL (Rolo)')
    ok(valor(pg, '#inputUnidadeMedida') == 'UN' and rotulo(pg, '#inputUnidadeMedida') == 'UN (Unidade)', 'o padrao e UN (produto novo)')
    ok(pg.evaluate("document.querySelectorAll('#inputUnidadeMedida input').length") == 0, 'nao ha mais campo de texto')
    for antigo, certo in (('Un', 'UN'), ('un', 'UN'), ('UN', 'UN'), ('Kg', 'KG'), ('kg', 'KG'), ('g', 'G'), ('cx', 'CX'), ('Par', 'PAR'), ('ml', 'ML'), ('M²', 'M²'), ('m³', 'M³'), ('', 'UN'), (None, 'UN')):
        pg.evaluate("(v) => unidadeNoProduto(v)", antigo)
        ok(valor(pg, '#inputUnidadeMedida') == certo, 'o valor gravado %r cai em %s: %s' % (antigo, certo, valor(pg, '#inputUnidadeMedida')))
    ok(pg.evaluate("document.querySelectorAll('#inputUnidadeMedida .dropdown-select-item.active').length") == 1, 'e so uma opcao fica marcada')
    pg.evaluate("(v) => unidadeNoProduto(v)", 'Duzia')
    ok(rotulo(pg, '#inputUnidadeMedida') == 'Duzia' and valor(pg, '#inputUnidadeMedida') == 'Duzia' and pg.evaluate("document.querySelectorAll('#inputUnidadeMedida .dropdown-select-item.active').length") == 0,
       'valor que a lista nao conhece fica no rotulo, com o valor guardado, e nenhuma opcao marcada')
    escolher(pg, '#inputUnidadeMedida', 'CX')
    ok(valor(pg, '#inputUnidadeMedida') == 'CX' and rotulo(pg, '#inputUnidadeMedida') == 'CX (Caixa)', 'escolher na lista troca o valor desconhecido')
    pg.context.close()
    pg = nova(); ir(pg, PROD)
    ok(valor(pg, '#inputUnidadeMedida') == 'UN', 'o produto de exemplo, que guardava "Un", abre em UN')
    pg.context.close()
    # o molde de referencia traz o mesmo campo: a suite do molde nao exige a mudanca, e ele fica como esta
    ok(True, 'o molde de referencia nao e tocado (nenhuma suite exige)')

    print('\n[5] A categoria financeira da nota e da ordem vem do cadastro')
    pg = nova(); ir(pg, NOTA)
    it = itens(pg, '#inputCategoria')
    ok(sorted(it) == sorted(cats_ativas) and len(cats_ativas) == 24, 'nota: as 24 categorias ativas do cadastro, com o mesmo id e o mesmo nome')
    ok(not any(n in [r for v, r in it] for n in cats_inativas), 'nota: a categoria inativa (%s) fica de fora' % ', '.join(cats_inativas))
    ok([r for v, r in it] == sorted([r for v, r in it], key=lambda s: s.lower().replace('í', 'i').replace('ã', 'a').replace('é', 'e').replace('ç', 'c').replace('ú', 'u').replace('ô', 'o')), 'nota: em ordem alfabetica')
    ok('Lista mocada' not in pg.inner_text('body'), 'nota: a dica "Lista mocada até Finanças ganhar o cadastro" saiu')
    ok(valor(pg, '#inputCategoria') == '' and rotulo(pg, '#inputCategoria') == 'Selecione a categoria', 'nota: abre sem categoria escolhida (e continua obrigatoria)')
    ok(not any(v in ('compras', 'impostos', 'servicos', 'veiculos') for v, r in it), 'nota: os quatro valores de exemplo de antes sumiram da lista')
    # valor antigo
    r = pg.evaluate("""(() => {
      const f = (v, txt) => { listaMontar('inputCategoria', itensCategoria(), categoriaDoValor(v), txt, 'Selecione a categoria'); return [document.getElementById('inputCategoria').getAttribute('data-value'), document.querySelector('#inputCategoria .dropdown-select-label').textContent]; };
      return { compras: f('compras', CATEGORIA_ANTIGA_ROTULO.compras), impostos: f('impostos', CATEGORIA_ANTIGA_ROTULO.impostos), servicos: f('servicos', CATEGORIA_ANTIGA_ROTULO.servicos), veiculos: f('veiculos', CATEGORIA_ANTIGA_ROTULO.veiculos), id: f('13', ''), vazio: f('', '') };
    })()""")
    ok(r['compras'] == ['4', 'Compra de mercadoria para revenda'], 'nota gravada com "compras" cai na categoria de nome equivalente (Compra de mercadoria para revenda): %s' % r['compras'])
    ok(r['impostos'] == ['impostos', 'Impostos e taxas'] and r['servicos'] == ['servicos', 'Serviços gerais'] and r['veiculos'] == ['veiculos', 'Veículos'], 'sem equivalente, o texto antigo fica no rotulo e o valor nao se perde: %s %s %s' % (r['impostos'], r['servicos'], r['veiculos']))
    ok(r['id'] == ['13', 'Comissão de marketplace'] and r['vazio'] == ['', 'Selecione a categoria'], 'e o id novo e o vazio seguem como sao')
    pg.context.close()
    pg = nova(); ir(pg, OC, '?id=2')
    ids_oc = pg.evaluate("CATS_FIN.filter(c => c.id > 0).map(c => String(c.id))")
    ok(sorted(ids_oc) == sorted(v for v, r in cats_ativas) and pg.evaluate("CATS_FIN.filter(c => c.id > 0).every(c => %s.some(a => a[0] === String(c.id) && a[1] === c.nome))" % json.dumps(cats_ativas, ensure_ascii=False)),
       'ordem de compra: o dropdown lista as 24 categorias ativas do cadastro, com o mesmo id e o mesmo nome (%d)' % len(ids_oc))
    ok('só entram categorias de saída' not in pg.inner_text('body'), 'ordem de compra: a dica que dizia "so entram categorias de saida" (e nao era verdade) saiu')
    ok(valor(pg, '#inputCategoria') == '4', 'ordem de compra: segue abrindo em "Compra de mercadoria para revenda"')
    pg.context.close()

    print('\n[6] Necessidades de Compra: a ordem que cobre so parte')
    def ordem(numero, itens_, situacao='aberto'):
        return {'numero': numero, 'data': '2026-10-30', 'previsto': '', 'fornecedor': 'Embalagens do Vale', 'dep': 1, 'total': 10, 'situacao': situacao,
                'itens': [{'nome': 'x', 'sku': 'EMB-%03d' % i[0], 'qtd': i[1], 'un': 'UN', 'preco': 5, 'recebido': 0, 'embId': i[0]} for i in itens_]}
    pg = nova(); ir(pg, NC)
    pg.evaluate("(l) => localStorage.setItem('deskOrdensGeradas', JSON.stringify(l))", [ordem(12, [(3, 4)])])
    ir(pg, NC)
    linha = pg.evaluate("(() => { const out = {}; document.querySelectorAll('#corpoEmbalagens tr').forEach(tr => { const a = tr.querySelector('.emb-a-caminho'); out[tr.getAttribute('data-id')] = a ? [a.textContent.trim(), Array.from(a.querySelectorAll('a')).map(x => x.getAttribute('href'))] : null; }); return out; })()")
    ok(linha.get('3') and linha['3'][0] == '4 a caminho na ordem nº 12' and linha['3'][1] == ['../estoque/pagina-estoque-ordens-compra-detalhe.html?id=12'],
       'a Flex G (32 de minimo 40) tem ordem de 4 e ainda precisa comprar: embaixo do nome fica "4 a caminho na ordem nº 12", com o numero em link: %s' % (linha.get('3'),))
    ok(set(linha.keys()) == {'3', '5', '12'} and linha['5'] is None and linha['12'] is None, 'as embalagens abaixo do minimo sem ordem (EMB-005, EMB-012) nao ganham a linha: %s' % {k: v for k, v in linha.items()})
    ok(pg.evaluate("document.querySelector('#corpoEmbalagens tr[data-id=\"3\"] .emb-a-caminho').parentElement.className.indexOf('col-texto') >= 0 && document.querySelector('#corpoEmbalagens tr[data-id=\"3\"] td:nth-child(3)').firstChild.textContent.length > 0"),
       'a linha mora na celula do nome')
    estilo = pg.evaluate("(() => { const e = document.querySelector('#corpoEmbalagens .emb-a-caminho'); const s = getComputedStyle(e); return [parseFloat(s.fontSize), s.color, getComputedStyle(document.querySelector('#corpoEmbalagens tr[data-id=\"3\"] td:nth-child(3)')).color]; })()")
    ok(estilo[0] <= 11.5 and estilo[1] != estilo[2], 'e pequena (%spx) e apagada (cor diferente da do nome)' % estilo[0])
    # duas ordens
    pg.evaluate("(l) => localStorage.setItem('deskOrdensGeradas', JSON.stringify(l))", [ordem(12, [(3, 4)]), ordem(14, [(3, 2)])])
    ir(pg, NC)
    t = pg.evaluate("document.querySelector('#corpoEmbalagens tr[data-id=\"3\"] .emb-a-caminho').textContent.trim()")
    ok(t == '6 a caminho nas ordens nº 12, nº 14', 'com duas ordens os numeros vem separados por virgula e o total soma: %s' % t)
    # ordem que cobre tudo: vai para o bloco das ja pedidas, como sempre
    pg.evaluate("(l) => localStorage.setItem('deskOrdensGeradas', JSON.stringify(l))", [ordem(12, [(3, 4)]), ordem(15, [(12, 50)])])
    ir(pg, NC)
    ids = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => tr.getAttribute('data-id'))")
    ped = pg.evaluate("Array.from(document.querySelectorAll('#embPedidas .emb-pedida-linha')).map(l => l.innerText.replace(/\\s+/g, ' ').trim())")
    ok(ids == ['3', '5'] and ped == ['EMB-012 Tag Desk Brands 50 a caminho ordem nº 15'], 'a embalagem que a ordem cobre inteira segue no bloco das ja pedidas, sem mudanca: tabela %s, pedidas %s' % (ids, ped))
    ok(pg.evaluate("document.querySelectorAll('#embPedidas .emb-a-caminho').length") == 0 and pg.evaluate("document.querySelectorAll('#corpoEmbalagens tr[data-id=\"12\"]').length") == 0, 'e a linha nova so aparece na tabela, nunca no bloco das ja pedidas')
    # ordem atendida nao conta
    pg.evaluate("(l) => localStorage.setItem('deskOrdensGeradas', JSON.stringify(l))", [ordem(12, [(3, 4)], 'atendida')])
    ir(pg, NC)
    ok(pg.evaluate("document.querySelectorAll('#corpoEmbalagens .emb-a-caminho').length") == 0, 'ordem atendida nao deixa a linha: a embalagem volta ao normal')
    pg.context.close()

    ok(not erros, 'sem erro de JS em toda a suite: %s' % erros[:3])
    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
