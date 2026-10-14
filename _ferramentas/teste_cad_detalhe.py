# -*- coding: utf-8 -*-
# O cadastro completo abre o registro clicado (item G3, nos cinco cadastros — 13/out/2026).
#
# Ate esta data "Ver cadastro completo" abria sempre o mesmo exemplo: clicar em qualquer fornecedor
# abria a TechParts. Agora o link leva ?id=, e a pagina de detalhe tem um espelho da lista (REGISTROS).
#
#   [1] o espelho de cada pagina e igual ao array da lista;
#   [2] o link do painel leva o id de cada registro;
#   [3] cada registro abre a si mesmo: o que a pagina mostra bate com a lista, campo a campo; so o
#       exemplo tem cadastro completo, e nos outros o que a lista nao sabe fica em branco;
#   [4] pelo clique: lista > painel > "Ver cadastro completo" chega no registro clicado, em leitura;
#   [5] cadastro novo nao herda nada do exemplo;
#   [6] o subtitulo acompanha o dropdown (antes: "undefined" ou em branco);
#   [7] abrir um registro nao deixa alteracao pendente no rodape;
#   [8] Contas a Pagar e Contas a Receber chegam no cadastro pelo nome;
#   [9] o documento duplicado poupa o cliente que esta aberto, e acusa o dos outros.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]

# base do arquivo, array da lista, funcao que abre o painel, id do exemplo desenhado na pagina
CADASTROS = [
    ('clientes', 'CLIENTES', 'abrirPreviewCliente', 3),
    ('fornecedores', 'FORNECEDORES', 'abrirPreviewFornecedor', 2),
    ('produtos', 'PRODUTOS', 'abrirPreviewProduto', 1),
    ('vendedores', 'VENDEDORES', 'abrirPreviewVendedor', 1),
    ('lojas-desk', 'LOJAS', 'abrirPreviewLoja', 1),
]
lista = lambda base: 'pagina-cadastros-%s.html' % base
detalhe = lambda base: 'pagina-cadastros-%s-detalhe.html' % base

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


# O que a pagina de detalhe mostra. Um retrato so, para as cinco: o que a pagina nao tem volta null.
RETRATO = """() => {
  const v = (id) => { const e = document.getElementById(id); return e ? e.value : null; };
  const rot = (id) => { const e = document.querySelector('#' + id + ' .dropdown-select-label'); return e ? e.textContent.trim() : null; };
  const txt = (sel) => { const e = document.querySelector(sel); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; };
  const linhas = (id) => { const e = document.getElementById(id); return e ? e.children.length : null; };
  const faixa = document.getElementById('faixaLojas');
  return {
    h1: txt('.main h1'), sub: txt('.main .page-header .subtitle'), badge: txt('#statusBadge'),
    pessoa: txt('#tipoPessoaToggle button.active'), tipoLoja: txt('#tipoLojaToggle button.active'),
    faixa: faixa && faixa.offsetParent !== null ? Array.from(faixa.querySelectorAll('.origem-badge')).map(b => b.textContent.trim()) : null,
    nome: v('inputNome') ?? v('inputNomeProduto') ?? v('inputNomeVendedor') ?? v('inputNomeLoja'),
    codigo: v('inputCodigo') ?? v('inputCodigoVendedor'), doc: v('inputDocumento') ?? v('inputDocumentoVendedor') ?? v('inputDocumentoLoja'),
    cidade: v('inputCidade') ?? v('inputCidadeVendedor') ?? v('inputCidadeLoja'), estado: v('inputEstado') ?? v('inputEstadoLoja'),
    endereco: v('inputEndereco') ?? v('inputEnderecoVendedor') ?? v('inputEnderecoLoja'), numero: v('inputNumero') ?? v('inputNumeroVendedor') ?? v('inputNumeroLoja'),
    bairro: v('inputBairro') ?? v('inputBairroVendedor') ?? v('inputBairroLoja'), cep: v('inputCep') ?? v('inputCepVendedor') ?? v('inputCepLoja'),
    telefone: v('inputTelefone'), email: v('inputEmail') ?? v('inputEmailComunicacoes'), desde: v('inputDataCriacao'),
    fantasia: v('inputNomeFantasia') ?? v('inputFantasiaVendedor'), obs: v('inputObservacoesVendedor') ?? v('inputObservacoesLoja'),
    situacao: rot('inputSituacao') ?? rot('dropdownSituacao') ?? rot('inputStatusLoja'), loja: rot('inputLoja') ?? rot('dropdownLojaVinculada'), contato: rot('inputContato'),
    contatos: linhas('tabelaContatos'), anexos: document.querySelectorAll('#listaAnexos .anexo-item').length,
    fornecidos: Array.from(document.querySelectorAll('#pfCorpo tr')).map(tr => tr.getAttribute('data-sku')).sort(),
    sku: v('inputSku'), preco: v('inputPrecoVenda'), estoque: v('inputEstoqueInicial'), tipo: rot('inputTipoProduto'),
    custos: linhas('tabelaCustos'), fornProduto: linhas('tabelaFornecedoresProduto'),
    uf: rot('dropdownUf'), usuario: v('inputUsuarioSistema'), aliquota: v('inputAliquotaComissao'), ie: v('inputInscricaoEstadual'),
    drops: ['dropdownContribuinte', 'dropdownDeposito', 'dropdownRegraComissao'].map(id => { const e = document.getElementById(id); return e ? e.getAttribute('data-value') : null; }),
    chks: ['chkAcessoHorario', 'chkAcessoIp', 'chkDesconsiderarComissaoLinha'].map(id => { const e = document.getElementById(id); return e ? e.checked : null; }),
    perfis: Array.from(document.querySelectorAll('.perfil-checkbox:checked')).map(c => c.value),
    modulos: document.querySelectorAll('#listaModulosAcesso input:checked').length,
    comissao: (document.querySelector('input[name="tipoComissao"]:checked') || {}).value || null,
    deposito: rot('inputDepositoPadrao'), metas: linhas('corpoHistoricoMetas')
  };
}"""

PESSOA = {'fisica': 'Pessoa Física', 'juridica': 'Pessoa Jurídica'}
ATIVO = {'ativo': 'Ativo', 'inativo': 'Inativo'}


def esperado(base, r, exemplo, extra):
    """O que a pagina tem de mostrar para o registro `r` da lista. So as chaves que a lista sabe."""
    if base in ('clientes', 'fornecedores'):
        e = dict(h1=r['nome'], badge=ATIVO[r['status']], pessoa=PESSOA[r['tipo']], nome=r['nome'], codigo=r['codigo'], doc=r['documento'], cidade=r['cidade'],
                 estado=r['estado'], endereco=r['endereco'], numero=r['numero'], bairro=r['bairro'], telefone=r['telefone'], email=r['email'], situacao=ATIVO[r['status']])
        if base == 'fornecedores':
            e.update(sub=r['codigo'] + ' · ' + r['categoria'], loja=r['categoria'], desde=r['fornecedorDesde'], faixa=r.get('fornecePara'))
            if not exemplo:
                e.update(fornecidos=sorted(p['sku'] for p in extra if p['fornecedor'] == r['nome']))
        else:
            manual = r['origem'] == 'Manual'
            e.update(sub=r['codigo'] + ' · ' + ('Cadastro Manual — Desk Shope' if manual else 'Cadastro pela loja — ' + r['origem']),
                     loja='Desk Shope' if manual else r['origem'], desde=r['clienteDesde'], faixa=r.get('lojasAtividade'),
                     contato={'cliente': 'Cliente', 'lead': 'Lead', 'prospect': 'Prospect'}[r['contato']])
        if not exemplo:
            e.update(fantasia='', cep='', contatos=0, anexos=0)
        return e
    if base == 'produtos':
        e = dict(h1=r['nome'], sub='%s · SKU %s' % (r['codigo'], r['sku']), badge=ATIVO[r['status']], nome=r['nome'], sku=r['sku'], estoque=str(r['estoque']),
                 preco=('%.2f' % r['preco']).replace('.', ','), tipo={'simples': 'Simples', 'kit': 'Kit Simples', 'variacoes': 'Com Variações', 'materia_prima': 'Matéria-Prima'}[r['tipo']])
        if not exemplo:
            e.update(custos=0, fornProduto=0)
        return e
    if base == 'vendedores':
        loja = [l['nome'] for l in extra if l['id'] == r['lojaVinculadaId']]
        return dict(h1=r['nome'], sub='Vinculado à ' + loja[0] if loja else 'Vendedor autônomo — sem vínculo com Loja Desk', pessoa=PESSOA[r['tipoPessoa']],
                    badge='Excluído' if r['excluido'] else {'ativo_acesso': 'Ativo com acesso ao sistema', 'ativo': 'Ativo', 'inativo': 'Inativo'}[r['situacao']],
                    nome=r['nome'], fantasia=r['fantasia'], codigo=r['codigo'], doc=r['documento'], ie=r['inscricaoEstadual'], cep=r['cep'], cidade=r['cidade'], uf=r['uf'],
                    endereco=r['endereco'], numero=r['numero'], bairro=r['bairro'], email=r['emailComunicacoes'], usuario=r['usuarioSistema'], aliquota=str(r['aliquotaComissao']),
                    obs=r['observacoes'], loja=loja[0] if loja else 'Nenhuma — vendedor autônomo', drops=[r['contribuinte'], r['deposito'], r['regraComissao']],
                    chks=[r['acessoRestritoHorario'], r['acessoRestritoIp'], r['desconsiderarComissaoPorLinha']], perfis=r['perfisContato'], modulos=len(r['modulosAcesso']),
                    comissao=r['tipoComissao'])
    e = dict(h1=r['nome'], sub={'produto': 'Produtos', 'servico': 'Serviços', 'trade_marketing': 'Trade Marketing'}[r['tipo']], tipoLoja={'produto': 'Produtos', 'servico': 'Serviços', 'trade_marketing': 'Trade Marketing'}[r['tipo']],
             badge=ATIVO[r['status']], pessoa=PESSOA[r['tipoPessoa']], nome=r['nome'], doc=r['documento'], cep=r['cep'], cidade=r['cidade'], estado=r['estado'], endereco=r['endereco'],
             numero=r['numero'], bairro=r['bairro'], obs=r['observacoes'], situacao=ATIVO[r['status']])
    if not exemplo:
        e.update(deposito='', metas=0)
    return e


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, query=''):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)

    # Os registros de cada lista, e o que o painel do fornecedor e o do vendedor leem de fora dela.
    LISTAS, EXTRA = {}, {}
    for base, const, _, _ in CADASTROS:
        ir(lista(base)); pg.evaluate("localStorage.removeItem('deskParametros')")
        LISTAS[base] = pg.evaluate(const)
        EXTRA[base] = pg.evaluate({'fornecedores': 'PRODUTOS_DO_CADASTRO', 'vendedores': 'LOJAS_DESK'}.get(base, 'null'))

    if secao(1, 'O espelho de cada página é igual à lista'):
        for base, const, _, ex in CADASTROS:
            ir(detalhe(base))
            ok(pg.evaluate('REGISTROS') == LISTAS[base] and len(LISTAS[base]) >= 3, '%s: REGISTROS repete os %d registros de %s, campo a campo' % (base, len(LISTAS[base]), const))
            ok(pg.evaluate('ID_DO_EXEMPLO') == ex and any(r['id'] == ex for r in LISTAS[base]), '%s: o exemplo desenhado na página (id %d) existe na lista' % (base, ex))

    if secao(2, 'O link do painel leva o id do registro'):
        for base, const, abre, _ in CADASTROS:
            ir(lista(base))
            hrefs = pg.evaluate("(ids) => ids.map(id => { %s(id); const a = document.querySelector('.event-drawer a.btn-primary'); return a ? a.getAttribute('href') : null; })" % abre,
                                [r['id'] for r in LISTAS[base]])
            errados = [h for r, h in zip(LISTAS[base], hrefs) if h != '../cadastros/%s?id=%d' % (detalhe(base), r['id'])]
            ok(not errados, '%s: "Ver cadastro completo" de cada um dos %d registros leva o seu ?id=: %s' % (base, len(hrefs), errados[:2]))

    if secao(3, 'Cada registro abre a si mesmo'):
        for base, const, _, ex in CADASTROS:
            ruins, vistos = [], {}
            for r in LISTAS[base]:
                ir(detalhe(base), '?id=%d' % r['id'])
                ret = vistos[r['id']] = pg.evaluate(RETRATO)
                for k, quer in esperado(base, r, r['id'] == ex, EXTRA[base]).items():
                    if ret[k] != quer:
                        ruins.append('id %d, %s: %r, e a lista diz %r' % (r['id'], k, ret[k], quer))
            ok(not ruins, '%s: os %d registros abrem com o que a lista diz deles (título, subtítulo, situação e campos): %s' % (base, len(LISTAS[base]), ruins[:3]))
            ok(len(set(v['h1'] for v in vistos.values())) == len(LISTAS[base]), '%s: são %d títulos diferentes, e não o mesmo exemplo %d vezes' % (base, len(LISTAS[base]), len(LISTAS[base])))
            ir(detalhe(base))
            ok(pg.evaluate(RETRATO) == vistos[ex], '%s: sem ?id= a página abre o exemplo, igual a ?id=%d' % (base, ex))
            ir(detalhe(base), '?id=99999')
            ok(pg.evaluate(RETRATO) == vistos[ex], '%s: e com um id que não existe, também' % base)
        cli, forn = LISTAS['clientes'], LISTAS['fornecedores']
        ir(detalhe('fornecedores'), '?id=2'); ret = pg.evaluate(RETRATO)
        ok(ret['fantasia'] == 'TechParts' and ret['cep'] == '01310-100' and ret['contatos'] == 2 and ret['anexos'] == 2 and len(ret['fornecidos']) == 7,
           'o fornecedor do exemplo continua com o cadastro completo: fantasia, CEP, 2 contatos, 2 anexos e 7 produtos')
        padrao = sorted(p['sku'] for p in EXTRA['fornecedores'] if p['fornecedor'] == 'Móveis Nordeste Ltda')
        ir(detalhe('fornecedores'), '?id=1'); pg.click('.tab-item[data-tab="produtos"]'); pg.wait_for_timeout(150)
        ok(pg.evaluate(RETRATO)['fornecidos'] == padrao and len(padrao) == 3 and pg.evaluate("document.getElementById('pfResumo').textContent") == '3 produtos · fornecedor padrão de 3.',
           'em outro fornecedor, a aba Produtos Fornecidos traz os produtos que o painel da lista conta: %s' % padrao)
        ir(detalhe('fornecedores'), '?nome=' + 'Luminárias Brasil')
        ok(pg.evaluate(RETRATO)['h1'] == 'Luminárias Brasil', 'o fornecedor também abre pelo nome (?nome=), para quem chega de outra tela')
        ir(detalhe('clientes'), '?id=3'); ret = pg.evaluate(RETRATO)
        ok(ret['fantasia'] == 'Distribuidora Nordeste' and ret['contatos'] == 2 and ret['anexos'] == 2, 'o cliente do exemplo continua com o cadastro completo')
        ir(detalhe('vendedores'), '?id=3&editar=1')
        alturas = pg.evaluate("['dropdownUf', 'dropdownContribuinte'].map(id => Math.round(document.querySelector('#' + id + ' .dropdown-select-btn').getBoundingClientRect().height))")
        ok(pg.evaluate(RETRATO)['uf'] == '' and alturas[0] == alturas[1] and alturas[0] > 20, 'dropdown sem valor (a UF do vendedor 3) fica em branco e com a altura dos outros: %s' % alturas)
        ok(sum(1 for r in forn if r.get('fornecePara')) >= 2 and sum(1 for r in forn if not r.get('fornecePara')) >= 2 and sum(1 for r in cli if r.get('lojasAtividade')) >= 2,
           'a faixa das lojas foi conferida nos dois casos: registro que tem e registro que não tem')

    if secao(4, 'Pelo clique: lista, painel e "Ver cadastro completo"'):
        for base, const, _, ex in CADASTROS:
            ir(lista(base))
            alvo = None
            linhas = pg.locator('.main [class$="-nome-row"]')
            if linhas.count() < 2:   # Vendedores abre filtrando "com acesso ao sistema", que so tem o exemplo
                pg.click('[data-filtro="ativos"]'); pg.wait_for_timeout(200)
            for i in range(linhas.count()):
                linhas.nth(i).evaluate('e => e.click()'); pg.wait_for_timeout(300)   # o painel aberto cobre a linha seguinte
                href = pg.evaluate("(document.querySelector('.event-drawer.open a.btn-primary') || { getAttribute: () => '' }).getAttribute('href')")
                alvo = int(href.split('?id=')[1]) if '?id=' in href else None
                if alvo and alvo != ex:
                    break
            reg = [r for r in LISTAS[base] if r['id'] == alvo][0] if alvo else {'nome': None}
            pg.evaluate("document.querySelector('.event-drawer.open a.btn-primary').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            leitura = pg.evaluate("Array.from(document.querySelectorAll('.main .form-field > .campo-leitura')).map(x => x.textContent.trim())")
            ok(alvo not in (None, ex) and pg.evaluate("document.querySelector('.main h1').textContent.trim()") == reg['nome'] and reg['nome'] in leitura
               and pg.evaluate("document.body.classList.contains('modo-leitura')"),
               '%s: cliquei em "%s" e a página abriu "%s", só para leitura' % (base, reg['nome'], pg.evaluate("document.querySelector('.main h1').textContent.trim()")))

    if secao(5, 'Cadastro novo não herda nada do exemplo'):
        for base, const, _, ex in CADASTROS:
            ir(detalhe(base), '?novo=1')
            ret = pg.evaluate(RETRATO)
            cheios = pg.evaluate("Array.from(document.querySelectorAll('.main input, .main textarea')).filter(c => c.type !== 'checkbox' && c.type !== 'radio' && c.type !== 'file' && c.value).map(c => c.id + '=' + c.value)")
            sobra = [k for k in ('contatos', 'anexos', 'custos', 'fornProduto', 'metas') if ret[k]] + (['faixa'] if ret['faixa'] is not None else []) + ret['fornecidos']
            ok(ret['h1'].startswith('Nov') and not cheios and not sobra, '%s: "%s" abre sem campo preenchido e sem lista do exemplo: %s %s' % (base, ret['h1'], cheios[:3], sobra))

    if secao(6, 'O subtítulo acompanha o dropdown'):
        for base, drop, quer in [('clientes', 'inputLoja', 'CLI-0003 · Cadastro Manual — %s'), ('fornecedores', 'inputLoja', 'FOR-0002 · %s'), ('vendedores', 'dropdownLojaVinculada', 'Vinculado à %s')]:
            ir(detalhe(base), '?editar=1')
            rotulo = pg.evaluate("(d) => { const itens = document.querySelectorAll('#' + d + ' .dropdown-select-item:not(.active)'); const i = itens[itens.length - 1]; i.click(); return i.textContent.trim(); }", drop)
            pg.wait_for_timeout(120)
            sub = pg.evaluate(RETRATO)['sub']
            ok(sub == quer % rotulo and 'undefined' not in sub, '%s: trocar para "%s" leva o nome ao subtítulo: "%s"' % (base, rotulo, sub))
        ir(detalhe('clientes'), '?id=1&editar=1')
        pg.evaluate("Array.from(document.querySelectorAll('#inputLoja .dropdown-select-item')).filter(i => i.textContent.trim() === 'Desk Brands')[0].click()"); pg.wait_for_timeout(120)
        ok(pg.evaluate(RETRATO)['sub'] == 'CLI-0001 · Cadastro pela loja — Desk Brands', 'cliente que veio de uma loja: o subtítulo diz a loja, e não "Cadastro Manual"')

    if secao(7, 'Abrir um registro não deixa alteração pendente'):
        for base, const, _, ex in CADASTROS:
            outro = [r['id'] for r in LISTAS[base] if r['id'] != ex][-1]
            ir(detalhe(base), '?id=%d&editar=1' % outro); pg.wait_for_timeout(250)
            limpo = pg.evaluate('camposAlterados()')
            campo = pg.evaluate("(() => { const c = Array.from(document.querySelectorAll('.main input[type=text]')).filter(x => x.offsetParent !== null && !x.readOnly && !x.disabled)[0]; c.value = c.value + ' x'; c.dispatchEvent(new Event('input', { bubbles: true })); return c.id; })()")
            pg.wait_for_timeout(120)
            ok(limpo == 0 and pg.evaluate('camposAlterados()') == 1, '%s: o registro %d abre sem pendência, e mexer em um campo (%s) acusa uma' % (base, outro, campo))

    if secao(8, 'Finanças chega no cadastro pelo nome'):
        for tela, nomes, link, base in [('pagina-financas-contas-pagar-detalhe.html', 'FORNECEDORES', 'linkVerFornecedor', 'fornecedores'),
                                        ('pagina-financas-contas-receber-detalhe.html', 'CLIENTES', 'linkVerCliente', 'clientes')]:
            ex = [c[3] for c in CADASTROS if c[0] == base][0]
            do_cadastro = {r['nome']: r for r in LISTAS[base]}
            ir(tela, '?id=1')
            de_la = pg.evaluate(nomes)
            comuns = [f for f in de_la if f['nome'] in do_cadastro and do_cadastro[f['nome']]['id'] != ex]
            outros_ids = [f for f in comuns if f['id'] != do_cadastro[f['nome']]['id']]
            ok(len(comuns) >= 2 and len(outros_ids) >= 1, '%s: %d nomes daqui existem no cadastro, e pelo menos um tem número diferente lá (por isso o link vai pelo nome)' % (tela.replace('pagina-financas-', ''), len(comuns)))
            alvo = (outros_ids or comuns or [{'id': 0, 'nome': ''}])[0]
            pg.evaluate("(id) => { fornEscolhido = id; document.getElementById('%s').click(); }" % link, alvo['id'])
            pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            ok(pg.url.split('/')[-1].startswith(detalhe(base) + '?nome=') and pg.evaluate("document.querySelector('.main h1').textContent.trim()") == alvo['nome'],
               'o link de "%s" abre o cadastro de "%s"' % (alvo['nome'], pg.evaluate("document.querySelector('.main h1').textContent.trim()")))

    if secao(9, 'Documento duplicado: poupa o cliente aberto, acusa o dos outros'):
        ir(detalhe('clientes'), '?id=1&editar=1')
        pg.evaluate("PARAM.aoSalvar = 'ficar'"); pg.click('#btnSalvarCliente'); pg.wait_for_timeout(250)
        ok(not pg.evaluate("document.getElementById('campoDocumento').classList.contains('has-error')"), 'salvar a Marina Duarte com o CPF dela não acusa duplicado')
        pg.fill('#inputDocumento', LISTAS['clientes'][1]['documento']); pg.click('#btnSalvarCliente'); pg.wait_for_timeout(250)
        ok(LISTAS['clientes'][1]['nome'] in pg.evaluate("document.getElementById('erroDocumento').textContent") and pg.evaluate("document.getElementById('erroDocumento').classList.contains('show')"),
           'com o CPF de outro cliente, o erro diz de quem é: %s' % pg.evaluate("document.getElementById('erroDocumento').textContent")[:60])
        pg.fill('#inputDocumento', LISTAS['clientes'][-1]['documento']); pg.click('#btnSalvarCliente'); pg.wait_for_timeout(250)
        ok(LISTAS['clientes'][-1]['nome'] in pg.evaluate("document.getElementById('erroDocumento').textContent"), 'e vale para o último cliente da lista, que a relação antiga (seis nomes) não tinha')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
