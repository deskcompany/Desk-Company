# -*- coding: utf-8 -*-
# Becos sem saida, senha no lugar certo e modo de abertura dos cadastros.
# Nasceu em 29/set/2026, da varredura que achou botoes respondendo "a navegacao
# so funciona no Lovable" e "e a proxima tela a ser construida" com a tela ja
# existindo ha semanas — e tres exclusoes em massa sem senha porque a trava
# estava armada no aviso, e nao no modal que exclui. A auditoria dizia "todos os
# botoes respondem": respondiam, com uma mentira. Este teste pega as duas coisas.
from playwright.sync_api import sync_playwright
import os, re, glob, json
import pathlib as _pathlib
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
import sys as _sys, os as _os2
_sys.path.insert(0, _os2.path.dirname(_os2.path.abspath(__file__)))
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

# ---------------------------------------------------------------------------
print('\n[1] Nenhum texto de tela diz que tela existente "ainda nao existe"')
PROIBIDO = re.compile(
    r"s[óo] (passa a )?funciona(r)? de verdade no Lovable|arquivo isolado|"
    r"[ée] a pr[óo]xima (tela|a ser constru)|pr[óo]xima tela da fase|no fim da fase|entra no fim da F5|"
    r"A tela entra depois de Entrada de Notas|Entra junto com a Confer[êe]ncia", re.I)
for f in _filtrar(sorted(glob.glob('pagina-*.html'))):
    if 'molde' in f: continue
    achados = []
    for i, l in enumerate(open(f, encoding='utf-8'), 1):
        t = l.strip()
        if t.startswith('//') or t.startswith('/*') or t.startswith('*'): continue
        if PROIBIDO.search(l): achados.append(i)
    ok(not achados, f + (' linhas ' + ','.join(map(str, achados)) if achados else ''))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('dialog', lambda d: d.dismiss())

    def abre(arq, espera=250):
        erros.clear()
        pg.goto(URL + arq); pg.wait_for_timeout(espera)

    def destino():
        return pg.url.replace(URL, '')

    def menu(item_acao, raiz='#menuMaisAcoes'):
        pg.locator(raiz + ' .dropdown-select-btn').first.click(); pg.wait_for_timeout(120)
        pg.locator(raiz + ' .dropdown-select-item[data-acao="' + item_acao + '"]').first.click(); pg.wait_for_timeout(300)

    # -----------------------------------------------------------------------
    print('\n[2] Botoes que levam a telas que existem')
    casos = [
        ('pagina-estoque-ordens-compra.html', lambda: pg.click('#btnNovaOC'), 'pagina-estoque-ordens-compra-detalhe.html'),
        ('pagina-estoque-ordens-compra.html', lambda: (pg.evaluate("abrirPreview(ORDENS.find(o => document.querySelector('input.item-checkbox[data-id=\"' + o.id + '\"]')).id)"), pg.wait_for_timeout(200), pg.click('#btnAbrirDetalhe')), 'pagina-estoque-ordens-compra-detalhe.html'),
        ('pagina-estoque-ordens-compra-detalhe.html', lambda: pg.click('#btnCancelar'), 'pagina-estoque-ordens-compra.html'),
        ('pagina-estoque-ordens-compra-detalhe.html', lambda: menu('nota'), 'pagina-estoque-entrada-notas-detalhe.html'),
        ('pagina-estoque-ordens-compra-detalhe.html', lambda: menu('receber'), 'pagina-estoque-conferencia-compra.html?receber=1'),
        ('pagina-estoque-ordens-compra-detalhe.html', lambda: menu('parcial'), 'pagina-estoque-conferencia-compra.html?receber=1'),
        ('pagina-estoque-ordens-compra-detalhe.html', lambda: menu('clonar'), 'pagina-estoque-ordens-compra-detalhe.html?clonar=1'),
        ('pagina-estoque-entrada-notas.html', lambda: pg.click('#btnNovaNota'), 'pagina-estoque-entrada-notas-detalhe.html'),
        ('pagina-estoque-entrada-notas.html', lambda: (pg.evaluate("abrirPreview(NOTAS.find(n => Number(n.numero) === 2301).id)"), pg.wait_for_timeout(200), pg.click('#btnAbrirConferencia')), 'pagina-estoque-conferencia.html?nota=2301'),
        ('pagina-estoque-entrada-notas.html', lambda: (pg.evaluate("abrirPreview(NOTAS.find(n => Number(n.numero) === 731).id)"), pg.wait_for_timeout(200), pg.click('#btnAbrirConferencia')), 'pagina-estoque-conferencia-compra.html'),
        ('pagina-estoque-entrada-notas-detalhe.html', lambda: pg.click('#btnCancelar'), 'pagina-estoque-entrada-notas.html'),
        ('pagina-estoque-entrada-notas-detalhe.html', lambda: menu('conferencia'), 'pagina-estoque-conferencia-compra.html'),
        ('pagina-estoque-conferencia.html', lambda: pg.click('#btnCancelar'), 'pagina-estoque-conferencia-compra.html'),
        ('pagina-estoque-conferencia.html', lambda: menu('nota'), 'pagina-estoque-entrada-notas-detalhe.html'),
        ('pagina-estoque-conferencia.html', lambda: menu('oc'), 'pagina-estoque-ordens-compra-detalhe.html'),
        ('pagina-estoque-conferencia-compra.html', lambda: menu('notas'), 'pagina-estoque-entrada-notas.html'),
        ('pagina-estoque-controle-estoques.html', lambda: pg.click('#btnGerenciarProdutos'), 'pagina-cadastros-produtos.html'),
        ('pagina-estoque-controle-estoques-detalhe.html', lambda: pg.click('#btnAbrirCadastro'), 'pagina-cadastros-produtos-detalhe.html'),
        ('pagina-estoque-enderecamento.html', lambda: menu('enderecos'), 'pagina-cadastros-enderecos-estoque.html'),
        ('pagina-estoque-reposicao.html', lambda: pg.click('#btnVerEnderecos'), 'pagina-cadastros-enderecos-estoque.html'),
    ]
    for arq, acao, esperado in casos:
        try:
            abre(arq); acao(); pg.wait_for_timeout(250)
            d = destino()
            ok(d == esperado and not erros, arq + ' -> ' + esperado + ('' if d == esperado else '  (foi para ' + d + ')') + (' ERRO ' + erros[0] if erros else ''))
        except Exception as e:
            ok(False, arq + ' -> ' + esperado + ' (' + str(e).split('\n')[0][:90] + ')')

    print('\n[3] Chegada nos destinos com parametro')
    abre('pagina-estoque-conferencia-compra.html?receber=1', 400)
    ok(pg.evaluate("document.getElementById('receberModal') ? document.getElementById('receberModal').classList.contains('open') : [...document.querySelectorAll('.open')].some(e => /receber/i.test(e.id))"),
       'Conferencia de Compra ?receber=1 abre o modal de receber mercadorias')
    abre('pagina-estoque-ordens-compra-detalhe.html?clonar=1', 300)
    ok(pg.inner_text('#tituloOC') == 'Nova ordem de compra', 'clone da OC: titulo "Nova ordem de compra"')
    ok(pg.input_value('#inputNumero') == '', 'clone da OC: numero vazio (gerado ao salvar)')
    ok(pg.input_value('#inputDataPrevista') == '', 'clone da OC: previsao vazia')
    ok('Em aberto' in pg.evaluate("document.getElementById('badgeSituacao').textContent"), 'clone da OC: situacao "Em aberto"')
    ok(not erros, 'clone da OC: sem erro de JS' + (' ' + erros[0] if erros else ''))
    abre('pagina-estoque-conferencia.html?nota=731', 300)
    crumb = pg.evaluate("path[path.length - 1]")
    ok(crumb == 'Nota 9051', 'Conferencia ?nota=731 (nao conferivel): breadcrumb diz a nota que a tela carregou (' + crumb + ')')

    # -----------------------------------------------------------------------
    print('\n[4] Cadastros: Incluir e "Editar cadastro completo" abrem editaveis; consulta segue a preferencia')
    CAD = [('clientes', 'btnNovoCliente'), ('fornecedores', 'btnNovoFornecedor'), ('produtos', 'btnNovoProduto'),
           ('vendedores', 'btnIncluirVendedor'), ('lojas-desk', 'btnNovaLoja')]
    leitura = lambda: pg.evaluate("document.body.classList.contains('modo-leitura')")
    for base, btn in CAD:
        abre('pagina-cadastros-' + base + '.html'); pg.click('#' + btn); pg.wait_for_timeout(300)
        ok(not leitura() and destino().endswith('?novo=1'), base + ': Incluir abre em edicao')
        abre('pagina-cadastros-' + base + '-detalhe.html')
        ok(leitura(), base + ': aberto para consulta, padrao = visualizacao')
        abre('pagina-cadastros-' + base + '-detalhe.html?editar=1')
        ok(not leitura(), base + ': ?editar=1 abre em edicao')
    # preferencia gravada em Interface do usuario
    abre('pagina-configuracoes-interface-usuario.html')
    pg.check('input[name="aoAbrirCadastro"][value="edicao"]'); pg.click('#btnSalvarParam'); pg.wait_for_timeout(200)
    salvo = pg.evaluate("JSON.parse(localStorage.getItem('deskParametros') || '{}').aoAbrirCadastro")
    ok(salvo == 'edicao', 'Interface do usuario grava aoAbrirCadastro=edicao (' + str(salvo) + ')')
    for base, _ in CAD:
        abre('pagina-cadastros-' + base + '-detalhe.html')
        ok(not leitura(), base + ': com a preferencia "edicao", consulta abre editavel')
    pg.evaluate("localStorage.removeItem('deskParametros')")

    # -----------------------------------------------------------------------
    print('\n[5] Senha no modal que EXCLUI, nunca no aviso de que nada pode ser excluido')
    senha = lambda: pg.evaluate("(() => { const r = document.getElementById('campoSenhaModal'); return !!(r && r.classList.contains('on')); })()")
    texto = lambda: pg.evaluate("(document.getElementById('confirmModalTexto') || {}).textContent || ''")
    def marca(arq, dados, cond):
        abre(arq)
        i = pg.evaluate("(() => { const vis = new Set([...document.querySelectorAll('input.item-checkbox[data-id]')].map(c => +c.getAttribute('data-id'))); const x = " + dados + ".find(o => vis.has(o.id) && (" + cond + ")); return x ? x.id : null; })()")
        if i is None: return None
        pg.locator('input.item-checkbox[data-id="' + str(i) + '"]').click(); pg.wait_for_timeout(150)
        return i
    PAR = [
        ('pagina-estoque-ordens-compra.html', 'ORDENS', "o.situacao === 'aberto'", "o.situacao === 'andamento' || o.situacao === 'atendida'", 'ordem'),
        ('pagina-cadastros-depositos.html', 'DEPOSITOS', '!o.principal && !o.excluido', 'o.principal', 'deposito'),
        ('pagina-cadastros-enderecos-estoque.html', 'ENDERECOS', '!(o.produtos > 0)', 'o.produtos > 0', 'endereco'),
    ]
    for arq, dados, livre, travado, nome in PAR:
        if marca(arq, dados, livre) is None: ok(False, arq + ': sem ' + nome + ' livre na primeira pagina'); continue
        pg.click('#btnExcluirSelecionados'); pg.wait_for_timeout(250)
        ok(senha(), arq + ': excluir ' + nome + ' livre PEDE senha')
        if marca(arq, dados, travado) is None: ok(False, arq + ': sem ' + nome + ' travado na primeira pagina'); continue
        pg.click('#btnExcluirSelecionados'); pg.wait_for_timeout(250)
        ok(not senha(), arq + ': aviso de que nada pode ser excluido NAO pede senha')
    # cancelar OC recebida
    marca('pagina-estoque-ordens-compra.html', 'ORDENS', "o.situacao === 'andamento'")
    pg.click('#btnCancelarSelecionadas'); pg.wait_for_timeout(250)
    ok(senha() and 'já recebeu mercadoria' in texto(), 'OC: cancelar ordem ja recebida pede senha e diz o que acontece com o estoque')
    marca('pagina-estoque-ordens-compra.html', 'ORDENS', "o.situacao === 'aberto'")
    pg.click('#btnCancelarSelecionadas'); pg.wait_for_timeout(250)
    ok(not senha(), 'OC: cancelar ordem que nao recebeu nada nao pede senha')

    # -----------------------------------------------------------------------
    print('\n[6] Caixa: competencia em massa')
    abre('pagina-financas-caixa.html', 350)
    id_ = pg.evaluate("(() => { const c = document.querySelector('[data-check=\"mov\"]'); return c ? +c.getAttribute('data-id') : null; })()")
    if id_ is None:
        ok(False, 'Caixa: nenhum lancamento na tela para selecionar')
    else:
        pg.locator('[data-check="mov"][data-id="' + str(id_) + '"]').click(); pg.wait_for_timeout(150)
        alvo = pg.evaluate("document.querySelector('#menuCompetenciaMassa .dropdown-select-item:last-child').getAttribute('data-value')")
        pg.locator('#ddCompetenciaMassa .dropdown-select-btn').click(); pg.wait_for_timeout(120)
        pg.locator('#menuCompetenciaMassa .dropdown-select-item[data-value="' + alvo + '"]').click(); pg.wait_for_timeout(250)
        if pg.evaluate("!!document.getElementById('btnConfirmModalConfirmar') && getComputedStyle(document.getElementById('confirmModal') || document.body).display !== 'none' && (document.getElementById('confirmModal') || {classList:{contains:()=>false}}).classList.contains('open')"):
            pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(200)
        comp = pg.evaluate("movDe(" + str(id_) + ").comp")
        ok(comp == alvo and not erros, 'Caixa: competencia do lancamento ' + str(id_) + ' mudou para ' + alvo + ' (' + str(comp) + ')' + (' ERRO ' + erros[0] if erros else ''))

    # -----------------------------------------------------------------------
    print('\n[7] Hub de Configuracoes nao promete tela de marcador nem de tag (decisoes de 22 e 29/set)')
    abre('pagina-configuracoes.html')
    txt = pg.inner_text('body')
    ok('Marcadores' not in txt and 'Tags de produtos' not in txt, 'hub sem "Marcadores..." e sem "Tags de produtos"')

    b.close()

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
