# Configuracoes > Condicoes de pagamento — 24/nov/2026 (pacote das listas).
#
# O usuario pediu que o texto livre que tem cadastro vire lista de escolha. A condicao de pagamento ("30 60 90",
# "3x", "15 +2x") era o campo mais digitado do sistema, em cinco telas e em cinco formatos. Agora ela mora num
# cadastro (`deskCondicoesPagamento`): nome, prazos em dias (0 a 365, crescentes, sem repetir; 0 e a vista), para
# que uso vale (receber, pagar ou os dois) e situacao. Cada prazo vira uma parcela de valor igual.
#
# O que esta suite guarda:
#   [1]  a lista de fabrica (14 condicoes) e o que cada linha diz;
#   [2]  incluir: o que e digitado vira prazos crescentes, e a previa mostra as parcelas;
#   [3]  as validacoes: nome vazio e repetido (com outra caixa), prazo fora de 0 a 365, prazo repetido, sem prazo, texto que nao e numero;
#   [4]  editar, inativar e excluir, e o filtro de "vale para" e de situacao;
#   [5]  a gravacao em `deskCondicoesPagamento` e o Registro de atividades;
#   [6]  a trava nasce com a tela: tres verbos no catalogo, a exclusao pede o codigo, o hub e as permissoes conhecem a tela;
#   [7]  o bloco comum CONDICOES DE PAGAMENTO: LEITURA e identico em todas as telas que o carregam;
#   [8]  condicao inativa ou de outro uso nao aparece na escolha (nota, cadastros e PDV);
#   [9]  as parcelas da nota e da ordem de compra batem com os prazos da condicao;
#   [10] ordem de compra com texto antigo: o nome que bate escolhe a condicao, o que nao bate fica no rotulo;
#   [11] as parcelas do PDV saem dos prazos, e a condicao padrao e a de 30 dias;
#   [12] a migracao de uma vez so: nomes novos, as condicoes 13 e 14, e a 13 apagada nao volta.
from playwright.sync_api import sync_playwright
import os, re, json

import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

TELA = 'pagina-configuracoes-condicoes-pagamento.html'
NOTA = 'pagina-estoque-entrada-notas-detalhe.html'
OC = 'pagina-estoque-ordens-compra-detalhe.html'
FORN = 'pagina-cadastros-fornecedores-detalhe.html'
CLI = 'pagina-cadastros-clientes-detalhe.html'
PDV = 'pagina-vendas-pdv.html'
HUB = 'pagina-configuracoes.html'
SENHAS = 'pagina-configuracoes-confirmacoes-senha.html'
USUARIOS = 'pagina-configuracoes-usuarios.html'
CHAVE = 'deskCondicoesPagamento'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clic(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


def ir(pg, tela, q=''):
    pg.goto(localiza.uri(tela) + q)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(500)


def escolher(pg, raiz, valor):
    pg.evaluate("([r, v]) => document.querySelector(r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
    pg.wait_for_timeout(200)


def guardado(pg):
    return pg.evaluate("JSON.parse(localStorage.getItem('%s') || 'null')" % CHAVE)


def itens(pg, raiz):
    """Os itens do menu de um dropdown: [(valor, rotulo)]."""
    return pg.evaluate("(r) => Array.from(document.querySelectorAll(r + ' .dropdown-select-item')).map(i => [i.getAttribute('data-value'), i.textContent.trim()])", raiz)


def preenche(pg, nome, prazos, uso=None):
    pg.fill('#inputNomeCondicao', nome)
    pg.fill('#inputPrazos', prazos)
    if uso:
        escolher(pg, '#inputUso', uso)
    pg.wait_for_timeout(120)


def erro_visivel(pg, id_):
    return pg.evaluate("(i) => document.getElementById(i).classList.contains('show')", id_)


def bloco(arq):
    t = open(localiza.onde(arq), encoding='utf-8').read()
    a = t.find('// ===== CONDICOES DE PAGAMENTO: LEITURA')
    b = t.find('// ===== FIM DO BLOCO CONDICOES DE PAGAMENTO: LEITURA =====')
    return t[a:b] if a >= 0 and b > a else None


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})   # um contexto so: o que uma tela grava a outra le
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    ir(pg, TELA)

    print('\n[1] A lista de fabrica')
    pg.evaluate("itensPorPaginaAtual = 25; renderCondicoes();")
    nomes = pg.evaluate("Array.from(document.querySelectorAll('#listaCondicoes .cond-nome')).map(e => e.textContent)")
    esperado = ['À vista', '7 dias', '14 dias', '21 dias', '28 dias', '30 dias', '45 dias', '2x (30/60)', '3x (30/60/90)', '4x (30/60/90/120)', '3x (28/56/84)', 'Entrada + 2x (30/60)', '5x (30 a 150)', '6x (30 a 180)']
    ok(nomes == esperado, 'as 14 condicoes de fabrica, nesta ordem: %s' % nomes)
    fab = pg.evaluate("CONDICOES.map(c => [c.nome, c.prazos, c.uso, c.ativo])")
    ok(fab[0] == ['À vista', [0], 'ambos', True] and fab[8] == ['3x (30/60/90)', [30, 60, 90], 'ambos', True] and fab[11] == ['Entrada + 2x (30/60)', [0, 30, 60], 'ambos', True] and fab[12] == ['5x (30 a 150)', [30, 60, 90, 120, 150], 'ambos', True] and fab[13][1] == [30, 60, 90, 120, 150, 180],
       'prazos de fabrica: a vista [0], 3x [30,60,90], entrada + 2x [0,30,60], 5x e 6x de 30 em 30')
    ok(all(f[2] == 'ambos' and f[3] for f in fab), 'todas ativas e valendo para receber e pagar')
    corpo = pg.inner_text('#listaCondicoes')
    ok('3 parcelas: 30, 60 e 90 dias' in corpo and 'à vista, 1 parcela' in corpo and '1 parcela: 7 dias' in corpo, 'cada linha diz as parcelas que a condicao gera')
    ok(guardado(pg) is None, 'sem mexer em nada, nada e gravado: a lista de fabrica vale sozinha')

    print('\n[2] Incluir: o que se digita vira prazos crescentes, e a previa mostra as parcelas')
    clic(pg, '#btnNovaCondicao'); pg.wait_for_timeout(500)
    ok(pg.inner_text('#previaPrazos') == 'Digite os prazos para ver as parcelas.', 'o painel abre com a previa pedindo os prazos')
    pg.fill('#inputPrazos', '30, 60 90'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#previaPrazos') == '3 parcelas: 30, 60 e 90 dias', 'virgula e espaco separam: %s' % pg.inner_text('#previaPrazos'))
    pg.fill('#inputPrazos', '45'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#previaPrazos') == '1 parcela: 45 dias', 'um prazo: %s' % pg.inner_text('#previaPrazos'))
    pg.fill('#inputPrazos', '0'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#previaPrazos') == 'à vista, 1 parcela', 'zero sozinho e a vista: %s' % pg.inner_text('#previaPrazos'))
    pg.fill('#inputPrazos', '90/60/30/0'); pg.wait_for_timeout(100)
    ok(pg.inner_text('#previaPrazos') == '4 parcelas: 0, 30, 60 e 90 dias', 'a barra tambem separa e a previa ja mostra a ordem crescente: %s' % pg.inner_text('#previaPrazos'))
    preenche(pg, '15/45 especial', '45 15', 'pagar')
    clic(pg, '#btnSalvarCondicao'); pg.wait_for_timeout(500)
    nova = pg.evaluate("CONDICOES.filter(c => c.nome === '15/45 especial')[0]")
    ok(nova and nova['prazos'] == [15, 45] and nova['uso'] == 'pagar' and nova['ativo'] is True, 'gravou ordenado [15, 45], so para pagar, ativa: %s' % nova)
    ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'o painel fecha ao salvar')

    print('\n[3] As validacoes')
    def tenta(nome, prazos):
        clic(pg, '#btnNovaCondicao'); pg.wait_for_timeout(350)
        preenche(pg, nome, prazos)
        antes = pg.evaluate("CONDICOES.length")
        clic(pg, '#btnSalvarCondicao'); pg.wait_for_timeout(250)
        depois = pg.evaluate("CONDICOES.length")
        r = (depois == antes, erro_visivel(pg, 'erroNomeCondicao'), erro_visivel(pg, 'erroPrazos'), pg.inner_text('#erroPrazos'), pg.inner_text('#erroNomeCondicao'))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        return r
    r = tenta('', '30')
    ok(r[0] and r[1], 'nome vazio e barrado: %s' % (r,))
    r = tenta('3x (30/60/90)', '30 60 90')
    ok(r[0] and r[1] and 'Já existe' in r[4], 'nome repetido e barrado: %s' % r[4])
    r = tenta('fAcIl 30/60', '30 60')
    ok(r[0] is False and not r[1], 'nome parecido mas diferente passa (a conta so barra o igual)')
    r = tenta('30 DIAS', '31')
    ok(r[0] and r[1], 'nome repetido com outra caixa tambem e barrado ("30 DIAS" ja existe como "30 dias")')
    r = tenta('Longo', '366')
    ok(r[0] and r[2] and '366' in r[3] and '365' in r[3], 'prazo acima de 365 e barrado: %s' % r[3])
    r = tenta('Limite', '0 365')
    ok(r[0] is False, '0 e 365 sao os dois extremos validos')
    r = tenta('Repetido', '30 60 30')
    ok(r[0] and r[2] and 'repetido' in r[3], 'prazo repetido e barrado: %s' % r[3])
    r = tenta('Sem prazo', '')
    ok(r[0] and r[2] and 'ao menos um prazo' in r[3], 'sem prazo e barrado: %s' % r[3])
    r = tenta('Texto', '30 dias')
    ok(r[0] and r[2] and 'não é um prazo' in r[3], 'texto no lugar do numero e barrado: %s' % r[3])
    r = tenta('Negativo', '-5')
    ok(r[0] and r[2], 'prazo negativo e barrado: %s' % r[3])
    r = tenta('Decimal', '30,5')
    ok(r[0] is False, 'virgula separa: "30,5" sao os prazos 30 e 5 (ordenados: 5 e 30), sem erro')
    pg.evaluate("(() => { const i = CONDICOES.findIndex(c => c.nome === 'fAcIl 30/60'); if (i >= 0) CONDICOES.splice(i, 1); const j = CONDICOES.findIndex(c => c.nome === 'Limite'); if (j >= 0) CONDICOES.splice(j, 1); const k = CONDICOES.findIndex(c => c.nome === 'Decimal'); if (k >= 0) CONDICOES.splice(k, 1); guardarCondicoes(); renderCondicoes(); })()")
    ok(pg.evaluate("CONDICOES.length") == 15, 'tirei as tres de teste: sobram as 14 de fabrica e a "15/45 especial"')

    print('\n[4] Editar, inativar e excluir; os filtros')
    pg.evaluate("itensPorPaginaAtual = 25; renderCondicoes();")
    clic(pg, '#listaCondicoes .cond-card[data-id="%d"]' % nova['id']); pg.wait_for_timeout(500)
    ok(pg.input_value('#inputPrazos') == '15, 45' and pg.input_value('#inputNomeCondicao') == '15/45 especial', 'editar abre com o que foi gravado')
    ok(pg.get_attribute('#inputUso', 'data-value') == 'pagar' and pg.is_visible('#linkExcluirCondicao'), 'e o uso, com o link de excluir visivel')
    preenche(pg, '15/45 especial', '15 45 75', 'receber')
    clic(pg, '#btnSalvarCondicao'); pg.wait_for_timeout(400)
    e = pg.evaluate("CONDICOES.filter(c => c.id === %d)[0]" % nova['id'])
    ok(e['prazos'] == [15, 45, 75] and e['uso'] == 'receber', 'alterou os prazos e o uso: %s' % e)
    # o proprio nome nao conta como repetido ao editar
    clic(pg, '#listaCondicoes .cond-card[data-id="%d"]' % nova['id']); pg.wait_for_timeout(400)
    clic(pg, '#btnSalvarCondicao'); pg.wait_for_timeout(300)
    ok(pg.evaluate("CONDICOES.filter(c => c.nome === '15/45 especial').length") == 1, 'salvar de novo sem mudar o nome nao acusa nome repetido')
    # filtros
    escolher(pg, '#filtroUso', 'receber')
    n_rec = pg.evaluate("document.querySelectorAll('#listaCondicoes .cond-card').length")
    escolher(pg, '#filtroUso', 'pagar')
    n_pag = pg.evaluate("document.querySelectorAll('#listaCondicoes .cond-card').length")
    ok(n_rec == 15 and n_pag == 14, '"Valem para receber" lista 15 (as 14 dos dois usos e a so receber) e "valem para pagar" 12: %d e %d' % (n_rec, n_pag))
    escolher(pg, '#filtroUso', 'todos')
    # inativar pela situacao do painel
    clic(pg, '#listaCondicoes .cond-card[data-id="%d"]' % nova['id']); pg.wait_for_timeout(400)
    escolher(pg, '#inputSituacao', 'inativo')
    clic(pg, '#btnSalvarCondicao'); pg.wait_for_timeout(400)
    ok(pg.evaluate("CONDICOES.filter(c => c.id === %d)[0].ativo" % nova['id']) is False, 'inativar pelo painel guarda ativo = false')
    escolher(pg, '#filtroSituacao', 'inativo')
    ok(pg.evaluate("document.querySelectorAll('#listaCondicoes .cond-card').length") == 1 and 'inativa' in pg.inner_text('#listaCondicoes').lower(), 'o filtro "Inativas" acha so ela, com o selo: %s' % pg.evaluate("Array.from(document.querySelectorAll('#listaCondicoes .cond-nome')).map(e => e.textContent)"))
    escolher(pg, '#filtroSituacao', 'ativo')
    ok(pg.evaluate("document.querySelectorAll('#listaCondicoes .cond-card').length") == 14, 'e "Ativas" tem as 14 de fabrica')
    escolher(pg, '#filtroSituacao', 'todos')
    pg.fill('#campoBusca', '90'); pg.wait_for_timeout(150)
    achadas = pg.evaluate("Array.from(document.querySelectorAll('#listaCondicoes .cond-nome')).map(e => e.textContent)")
    ok(achadas == ['3x (30/60/90)', '4x (30/60/90/120)', '5x (30 a 150)', '6x (30 a 180)'], 'a busca "90" acha as condicoes que tem o prazo 90: %s' % achadas)
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(100)
    # excluir: a exclusao pede o codigo, e sem o codigo nada some
    clic(pg, '#listaCondicoes .cond-card[data-id="%d"]' % nova['id']); pg.wait_for_timeout(400)
    clic(pg, '#linkExcluirCondicao'); pg.wait_for_timeout(400)
    ok(pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'excluir abre o modal com o campo do codigo de autorizacao')
    ok('"15/45 especial"' in pg.inner_text('#confirmModalTexto') and 'inativar guarda a história' in pg.inner_text('#confirmModalTexto'), 'o texto cita a condicao e diz que inativar guarda a historia')
    clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
    ok(pg.evaluate("CONDICOES.some(c => c.id === %d)" % nova['id']), 'sem o codigo, a condicao continua la')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[5] A gravacao em deskCondicoesPagamento e o Registro de atividades')
    g = guardado(pg)
    ok(isinstance(g, list) and len(g) == 15 and any(c['nome'] == '15/45 especial' and c['prazos'] == [15, 45, 75] for c in g), 'a lista inteira esta gravada, com as de fabrica junto (15)')
    ok(pg.evaluate("localStorage.getItem('deskCondicoesPagamentoV')") == '2', 'e a marca da versao (2) vai junto, para a migracao nao rodar de novo')
    log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")
    criar = [l for l in log if l['chave'] == 'condicoesPagamentoCriar']
    editar = [l for l in log if l['chave'] == 'condicoesPagamentoEditar']
    ok(len(criar) >= 1 and '15/45 especial' in criar[-1]['detalhe'] and '2 parcelas: 15 e 45 dias' in criar[-1]['detalhe'], 'incluir fica no registro, com as parcelas: %s' % (criar and criar[-1]['detalhe']))
    ok(len(editar) >= 2 and 'Configurações → Condições de pagamento' in editar[0]['onde'].replace('→', '→'), 'editar tambem, e o registro diz onde foi: %s' % (editar and editar[0]['onde']))
    # outra tela le o que esta gravado
    pg2 = ctx.new_page(); pg2.on('pageerror', lambda e: erros.append(str(e)))
    ir(pg2, NOTA)
    rotulos = [r for v, r in itens(pg2, '#inputCondicao')]
    ok('15/45 especial' not in rotulos and rotulos[:2] == ['À vista', '7 dias'] and len(rotulos) == 14, 'a nota le o cadastro gravado (a inativa e so-receber ficam de fora): %d itens' % len(rotulos))
    pg2.close()
    # exclusao de verdade: o codigo liberado nos parametros desta sessao
    pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ confirmacoes: { condicoesPagamentoExclui: false } }))")
    ir(pg, TELA)
    pg.evaluate("itensPorPaginaAtual = 25; renderCondicoes();")
    clic(pg, '#listaCondicoes .cond-card[data-id="%d"]' % nova['id']); pg.wait_for_timeout(400)
    clic(pg, '#linkExcluirCondicao'); pg.wait_for_timeout(300)
    ok(not pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'com a exigencia desligada em Confirmacoes por senha, o modal nao pede o codigo')
    clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
    ok(not pg.evaluate("CONDICOES.some(c => c.nome === '15/45 especial')") and len(guardado(pg)) == 14, 'excluiu e gravou a lista sem ela (14)')
    exclui = [l for l in pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')") if l['chave'] == 'condicoesPagamentoExclui']
    ok(len(exclui) == 1 and exclui[0]['senha'] is False, 'a exclusao fica no registro, sem senha porque a exigencia estava desligada')
    # selecao em massa: inativar duas
    clic(pg, '#listaCondicoes .cond-card[data-id="2"] .item-checkbox'); clic(pg, '#listaCondicoes .cond-card[data-id="3"] .item-checkbox'); pg.wait_for_timeout(200)
    ok(pg.is_visible('#barraSelecao') and '2 selecionadas' in pg.inner_text('#selecaoInfo'), 'a barra de selecao diz 2 selecionadas')
    clic(pg, '#btnInativarSelecionados'); pg.wait_for_timeout(300)
    clic(pg, '#confirmCienteCheckbox'); clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
    ok(pg.evaluate("CONDICOES.filter(c => !c.ativo).map(c => c.id).sort().join(',')") == '2,3', 'inativar em massa: 7 dias e 14 dias')
    pg.evaluate("localStorage.removeItem('%s'); localStorage.removeItem('deskParametros')" % CHAVE)

    print('\n[6] A trava nasce com a tela')
    ir(pg, TELA)
    ok(pg.evaluate("MODULOS_SENHA.filter(m => m.base === 'condicoesPagamento').map(m => [m.ligado.criar, m.ligado.editar, m.ligado.excluir])[0]") == [True, True, True], 'o modulo esta no catalogo com os tres verbos ligados')
    ok(pg.evaluate("exigeSenha('condicoesPagamentoExclui') && !exigeSenha('condicoesPagamentoCriar') && !exigeSenha('condicoesPagamentoEditar')"), 'excluir pede o codigo; criar e editar seguem a matriz (sem codigo)')
    p3 = ctx.new_page(); ir(p3, SENHAS)
    ok(p3.evaluate("MODULOS_SENHA.some(m => m.base === 'condicoesPagamento')"), 'Confirmacoes por senha conhece o modulo')
    p3.close()
    p3 = ctx.new_page(); ir(p3, USUARIOS)
    ok(p3.evaluate("PERM_MODULOS.some(m => m.itens.some(i => i.id === 'condicoesPagamento' && i.tela.indexOf('%s') > 0))" % TELA), 'Usuarios e Permissoes listam a tela nas permissoes')
    p3.close()
    hub = open(localiza.onde(HUB), encoding='utf-8').read()
    ok(("href:'../configuracoes/" + TELA + "'") in hub, 'o hub de Configuracoes tem o cartao que abre a tela')

    print('\n[7] O bloco comum e identico em todas as telas que o carregam')
    telas = [TELA, NOTA, OC, FORN, CLI, PDV]
    blocos = {t: bloco(t) for t in telas}
    ok(all(blocos.values()), 'as 6 telas tem o bloco (nota, ordem, fornecedor, cliente, PDV e o proprio cadastro): %s' % [t for t in telas if not blocos[t]])
    base = blocos[TELA]
    ok(all(b == base for b in blocos.values() if b), 'o texto do bloco e o mesmo nas 6: %s' % [t for t in telas if blocos[t] != base])
    todas = [c for c in localiza.nomes() if 'CONDICOES DE PAGAMENTO: LEITURA' in open(localiza.onde(c), encoding='utf-8').read()]
    ok(sorted(todas) == sorted(telas), 'e nenhuma outra tela o carrega sem estar nesta lista: %s' % todas)
    ok('Entrada + 2x (30/60)' in base and 'function condMigrar' in base and 'function condAtivas' in base and 'function condPorId' in base and 'function condTexto' in base and 'function condLer' in base, 'o bloco traz a lista de fabrica e as quatro funcoes: condLer, condAtivas, condPorId e condTexto')

    print('\n[8] Inativa, so receber ou so pagar nao aparece onde nao vale')
    LISTA = [
        {'id': 1, 'nome': 'À vista', 'prazos': [0], 'uso': 'ambos', 'ativo': True},
        {'id': 2, 'nome': 'Inativa antiga', 'prazos': [10], 'uso': 'ambos', 'ativo': False},
        {'id': 3, 'nome': 'So receber 20', 'prazos': [20], 'uso': 'receber', 'ativo': True},
        {'id': 4, 'nome': 'So pagar 40', 'prazos': [40], 'uso': 'pagar', 'ativo': True},
        {'id': 5, 'nome': '30 dias', 'prazos': [30], 'uso': 'ambos', 'ativo': True},
    ]
    def com_lista(tela, q=''):
        pgx = ctx.new_page(); pgx.on('pageerror', lambda e: erros.append(str(e)))
        pgx.goto(localiza.uri(TELA)); pgx.evaluate("(l) => { localStorage.setItem('%s', JSON.stringify(l)); localStorage.setItem('deskCondicoesPagamentoV', '2'); }" % CHAVE, LISTA)
        ir(pgx, tela, q)
        return pgx
    px = com_lista(NOTA)
    ok([v for v, r in itens(px, '#inputCondicao')] == ['1', '4', '5'], 'na nota (pagar): a inativa e a so-receber ficam de fora: %s' % [r for v, r in itens(px, '#inputCondicao')])
    ok(px.evaluate("condAtivas('pagar').map(c => c.id).join()") == '1,4,5' and px.evaluate("condAtivas('receber').map(c => c.id).join()") == '1,3,5', 'condAtivas respeita a situacao e o uso nos dois sentidos')
    px.close()
    px = com_lista(FORN)
    ok([v for v, r in itens(px, '#inputPrazoPagamento')] == ['', '1', '4', '5'], 'no fornecedor (pagar): "Sem condicao padrao" e as ativas de pagar: %s' % [r for v, r in itens(px, '#inputPrazoPagamento')])
    ok(itens(px, '#inputPrazoPagamento')[0][1] == 'Sem condição padrão', 'a primeira opcao e "Sem condição padrão" (a condicao e opcional)')
    px.close()
    px = com_lista(CLI)
    ok([v for v, r in itens(px, '#inputPrazoPagamento')] == ['', '1', '3', '5'], 'no cliente (receber): so as ativas de receber: %s' % [r for v, r in itens(px, '#inputPrazoPagamento')])
    px.close()
    px = com_lista(OC, '?id=2')
    ok([v for v, r in itens(px, '#inputCondicaoPagamento')] == ['1', '4', '5'], 'na ordem de compra (pagar): %s' % [r for v, r in itens(px, '#inputCondicaoPagamento')])
    px.close()
    px = com_lista(PDV)
    ok(px.evaluate("condAtivas('receber').map(c => c.id).join()") == '1,3,5', 'no PDV (receber): a so-pagar e a inativa ficam de fora')
    px.close()

    print('\n[9] As parcelas da nota e da ordem de compra batem com os prazos')
    pg.evaluate("localStorage.removeItem('%s')" % CHAVE)   # volta a lista de fabrica
    pn = ctx.new_page(); pn.on('pageerror', lambda e: erros.append(str(e)))
    ir(pn, NOTA)
    ok(pn.evaluate("document.getElementById('inputCondicao').getAttribute('data-value')") == '' and pn.inner_text('#inputCondicao .dropdown-select-label') == 'Selecione a condição de pagamento', 'a nota abre sem condicao escolhida')
    for cid, texto, prazos in [(9, '3 parcelas: 30, 60 e 90 dias', [30, 60, 90]), (12, '3 parcelas: 0, 30 e 60 dias', [0, 30, 60]), (1, 'à vista, 1 parcela', [0]), (10, '4 parcelas: 30, 60, 90 e 120 dias', [30, 60, 90, 120])]:
        escolher(pn, '#inputCondicao', cid)
        ok(texto in pn.inner_text('#hintCondicao') and pn.evaluate("condPorId(document.getElementById('inputCondicao').getAttribute('data-value')).prazos") == prazos,
           'nota, condicao %d: a dica diz "%s" e os prazos sao %s' % (cid, texto, prazos))
    # sem condicao a nota nao salva
    ir(pn, NOTA)
    clic(pn, '#btnSalvar'); pn.wait_for_timeout(500)
    ok('Escolha a condição de pagamento.' in pn.inner_text('#blocoErros'), 'sem condicao a nota nao salva: "Escolha a condição de pagamento."')
    pn.close()
    po = ctx.new_page(); po.on('pageerror', lambda e: erros.append(str(e)))
    ir(po, OC, '?id=2')
    geral = po.evaluate("recalcularTotais()")
    for cid, prazos in [(9, [30, 60, 90]), (12, [0, 30, 60]), (8, [30, 60]), (1, [0])]:
        escolher(po, '#inputCondicaoPagamento', cid)
        clic(po, '#btnGerarParcelas'); po.wait_for_timeout(250)
        par = po.evaluate("PARCELAS")
        soma = round(sum(x['valor'] for x in par), 2)
        linhas = po.evaluate("document.querySelectorAll('#corpoParcelas tr').length")
        ok([x['dias'] for x in par] == prazos and soma == round(geral, 2) and linhas == len(prazos),
           'OC, condicao %d: as parcelas saem dos prazos %s, somam o total (%.2f) e a tabela tem %d linha(s)' % (cid, prazos, geral, linhas))
    ir(po, OC, '?id=2')
    clic(po, '#btnGerarParcelas'); po.wait_for_timeout(250)
    ok(po.evaluate("PARCELAS.length") == 0 and 'Escolha a condição de pagamento' in po.inner_text('#confirmModalTexto'),
       'sem condicao escolhida, "Gerar parcelas" avisa e nao gera')

    print('\n[10] Ordem de compra com o texto antigo: o nome que bate escolhe, o que nao bate fica no rotulo')
    ir(po, OC, '?id=2')
    po.evaluate("condicaoNaOrdem('3x (30/60/90)')")
    ok(po.get_attribute('#inputCondicaoPagamento', 'data-value') == '9' and po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == '3x (30/60/90)', 'o texto "3x (30/60/90)" bate com o nome e escolhe a condicao 9')
    po.evaluate("condicaoNaOrdem('a vista')")
    ok(po.get_attribute('#inputCondicaoPagamento', 'data-value') == 'a vista' and po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == 'a vista',
       'o texto que nao bate com nenhum nome fica no rotulo, e o valor antigo nao se perde')
    po.evaluate("condicaoNaOrdem('30 60 90')")
    ok(po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == '30 60 90' and po.get_attribute('#inputCondicaoPagamento', 'data-value') == '30 60 90', '"30 60 90" (como se digitava) fica no rotulo ate a pessoa escolher')
    ok(po.evaluate("document.querySelectorAll('#inputCondicaoPagamento .dropdown-select-item.active').length") == 0, 'nenhum item da lista fica marcado enquanto o texto antigo esta no rotulo')
    escolher(po, '#inputCondicaoPagamento', 9)
    ok(po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == '3x (30/60/90)' and po.get_attribute('#inputCondicaoPagamento', 'data-value') == '9', 'escolher na lista troca o texto antigo pela condicao')
    po.evaluate("condicaoNaOrdem('NORDESTE 30/60')")
    ok(po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == 'NORDESTE 30/60', 'texto com palavras alem do nome tambem fica como esta')
    po.evaluate("condicaoNaOrdem('2X (30/60)')")
    ok(po.get_attribute('#inputCondicaoPagamento', 'data-value') == '8', 'e "2X (30/60)" (igual ao nome, caixa a parte) escolhe a condicao 8')
    # condicao guardada que depois foi inativada continua aparecendo pelo nome
    po.evaluate("localStorage.setItem('%s', JSON.stringify(COND_FABRICA.map(c => Object.assign({}, c, { ativo: c.id !== 9 }))))" % CHAVE)
    po.evaluate("condicaoNaOrdem(9)")
    ok(po.inner_text('#inputCondicaoPagamento .dropdown-select-label') == '3x (30/60/90)' and '9' not in [v for v, r in itens(po, '#inputCondicaoPagamento')], 'a condicao inativada depois continua no rotulo da ordem que ja a usava, mas sai da lista de escolha')
    po.close()

    print('\n[11] As parcelas do PDV saem dos prazos, e a padrao e a de 30 dias')
    pv = ctx.new_page(); pv.on('pageerror', lambda e: erros.append(str(e)))
    ir(pv, PDV)
    r = pv.evaluate("(() => { const r = { valor: 100, parcelas: [] }; const ok = gerarParcelas(r, 9); return [ok, r.parcelas.map(x => x.dias), r.parcelas.reduce((s, x) => s + x.valor, 0), r.condId]; })()")
    ok(r[0] and r[1] == [30, 60, 90] and abs(r[2] - 100) < 0.001 and r[3] == '9', 'a condicao 3x (30/60/90) gera 3 titulos que somam o valor: %s' % r)
    r = pv.evaluate("(() => { const r = { valor: 100, parcelas: [] }; gerarParcelas(r, 12); return r.parcelas.map(x => [x.dias, x.valor]); })()")
    ok([x[0] for x in r] == [0, 30, 60] and abs(sum(x[1] for x in r) - 100) < 0.001 and r[0][1] == 33.33 and r[2][1] == 33.34, 'entrada + 30/60: o valor de 100 divide em 33,33 / 33,33 / 33,34 (a sobra fica no ultimo): %s' % r)
    r = pv.evaluate("(() => { const r = { valor: 100, parcelas: [] }; gerarParcelas(r, ''); return [r.parcelas.map(x => x.dias), r.condId]; })()")
    ok(r[0] == [30] and r[1] == '6', 'sem condicao escolhida vale a padrao: 30 dias (a condicao 6): %s' % r)
    r = pv.evaluate("(() => { const r = { valor: 100, parcelas: [] }; gerarParcelas(r, 'texto antigo'); return r.parcelas.map(x => x.dias); })()")
    ok(r == [30], 'valor que nao e id de condicao cai na padrao em vez de quebrar')
    pv.close()

    print('\n[12] A migracao de uma vez so: nomes no formato "3x (...)" e as condicoes 13 e 14')
    ANTIGOS = {8: '30/60', 9: '30/60/90', 10: '30/60/90/120', 11: '28/56/84', 12: 'Entrada + 30/60'}
    PRAZOS = {1: [0], 2: [7], 3: [14], 4: [21], 5: [28], 6: [30], 7: [45], 8: [30, 60], 9: [30, 60, 90], 10: [30, 60, 90, 120], 11: [28, 56, 84], 12: [0, 30, 60]}
    NOMES1A7 = {1: 'À vista', 2: '7 dias', 3: '14 dias', 4: '21 dias', 5: '28 dias', 6: '30 dias', 7: '45 dias'}
    gravada = [{'id': i, 'nome': ANTIGOS.get(i) or NOMES1A7[i], 'prazos': PRAZOS[i], 'uso': 'ambos', 'ativo': True} for i in range(1, 13)]
    gravada[8]['nome'] = 'Meu 3x'                       # o usuario editou o nome da 9: a migracao nao mexe
    gravada.append({'id': 99, 'nome': '15/45 minha', 'prazos': [15, 45], 'uso': 'pagar', 'ativo': True})
    pm = ctx.new_page(); pm.on('pageerror', lambda e: erros.append(str(e)))
    pm.goto(localiza.uri(TELA)); pm.wait_for_load_state('load')
    pm.evaluate("(l) => { localStorage.setItem('%s', JSON.stringify(l)); localStorage.removeItem('deskCondicoesPagamentoV'); }" % CHAVE, gravada)
    ir(pm, NOTA)                                       # uma tela que so le: a migracao roda na leitura
    mig = guardado(pm)
    por_id = {c['id']: c for c in mig}
    ok([por_id[i]['nome'] for i in (8, 10, 11, 12)] == ['2x (30/60)', '4x (30/60/90/120)', '3x (28/56/84)', 'Entrada + 2x (30/60)'], 'o nome antigo de fabrica vira o novo (8, 10, 11 e 12): %s' % [por_id[i]['nome'] for i in (8, 10, 11, 12)])
    ok(por_id[9]['nome'] == 'Meu 3x' and por_id[99]['nome'] == '15/45 minha' and por_id[1]['nome'] == 'À vista', 'o nome que o usuario editou fica como esta, e as condicoes dele e as de 1 a 7 nao mudam')
    ok([c['id'] for c in mig].count(13) == 1 and [c['id'] for c in mig].count(14) == 1 and por_id[13]['prazos'] == [30, 60, 90, 120, 150] and por_id[14]['prazos'] == [30, 60, 90, 120, 150, 180] and por_id[13]['ativo'] and por_id[14]['uso'] == 'ambos',
       'a 13 e a 14 entram uma vez so, ativas e para os dois usos')
    ok(pm.evaluate("localStorage.getItem('deskCondicoesPagamentoV')") == '2', 'a marca da versao fica gravada')
    ir(pm, CLI); ir(pm, NOTA)                          # ler mais vezes nao acrescenta de novo
    mig = guardado(pm)
    ok(len(mig) == 15 and [c['id'] for c in mig].count(13) == 1, 'ler de novo em outras telas nao repete a 13 nem a 14: %d itens' % len(mig))
    ok('3x (30/60/90)' not in pm.evaluate("condAtivas('pagar').map(c => c.nome)") and 'Meu 3x' in pm.evaluate("condAtivas('pagar').map(c => c.nome)"), 'a tela que le ja enxerga o resultado (o "Meu 3x" no lugar do 3x de fabrica)')
    # apagar a 13 pelo proprio cadastro e ler de novo: a marca impede que ela volte
    ir(pm, TELA)
    pm.evaluate("(() => { const i = CONDICOES.findIndex(c => c.id === 13); CONDICOES.splice(i, 1); guardarCondicoes(); })()")
    ir(pm, NOTA)
    ir(pm, PDV)
    ids = [c['id'] for c in guardado(pm)]
    ok(13 not in ids and 14 in ids and len(ids) == 14, 'apagar a 13 depois da migracao nao a traz de volta (a 14 segue): %s' % ids)
    ir(pm, TELA)
    ok(pm.evaluate("CONDICOES.some(c => c.id === 13)") is False and pm.evaluate("localStorage.getItem('deskCondicoesPagamentoV')") == '2', 'e o proprio cadastro tambem nao a mostra')
    # lista que a tela de cadastro gravou antes desta versao (sem a marca) e sem a 13: ela volta uma vez so
    pm.evaluate("(l) => { localStorage.setItem('%s', JSON.stringify(l)); localStorage.removeItem('deskCondicoesPagamentoV'); }" % CHAVE, gravada[:12])
    ir(pm, NOTA); ir(pm, NOTA)
    ids = [c['id'] for c in guardado(pm)]
    ok(ids.count(13) == 1 and ids.count(14) == 1 and len(ids) == 14, 'lista antiga sem a marca recebe a 13 e a 14 uma vez so: %s' % ids)
    pm.evaluate("localStorage.removeItem('%s'); localStorage.removeItem('deskCondicoesPagamentoV')" % CHAVE)
    pm.close()

    ok(not erros, 'sem erro de JS em toda a suite: %s' % erros[:3])
    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
