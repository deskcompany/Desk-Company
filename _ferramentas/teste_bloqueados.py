# -*- coding: utf-8 -*-
# Estoque -> Itens Bloqueados (09/out/2026): a fila do saldo que esta no estoque e
# nao pode ser vendido. Nasceu de uma pergunta do usuario diante do "1 bloqueado"
# na pagina do produto: onde eu resolvo isso? Nao havia onde.
#
# O que esta suite guarda:
#   - tudo que bloqueia desagua na mesma fila: avaria, falta a auditar, item em
#     analise e produto travado por decisao;
#   - so ha duas saidas, e as duas aceitam parte da quantidade: liberar (volta
#     para o disponivel) e dar baixa (gera o acerto de saida, com o motivo e a
#     consequencia fiscal do Acerto de Estoque);
#   - liberar uma FALTA pede a causa: e a decisao de 05/out (design system 14.14);
#   - decisao de 09/out, revendo a de 05/out: a falta da Separacao e da
#     Conferencia de Saida BLOQUEIA a unidade. Nao e baixa, o fisico nao muda;
#   - decisao de 09/out: o que nao e avaria fica no proprio endereco, so travado;
#     avaria vai para endereco de Avaria (ou espera um, no Enderecamento);
#   - o bloqueio manual e um tipo de lancamento da pagina do produto, em
#     Controle de Estoques, e nao muda o fisico nem o custo.
#
# Secoes: [1] menu e abertura; [2] lista; [3] filtros; [4] liberar parte;
#   [5] falta pede a causa; [6] baixa, com senha; [7] fracionavel e sem base;
#   [8] resolvidos e F5; [9] a senha obedece a matriz; [10] bloquear item leva
#   a pagina do produto; [11] o tipo Bloqueio; [12] separacao; [13] conferencia
#   de saida; [14] espelhos; [15] catalogo e registro; [16] Esc, temas e erros.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

BLOQ = 'pagina-estoque-itens-bloqueados.html'
PROD = 'pagina-estoque-controle-estoques-detalhe.html'
ACERTO = 'pagina-estoque-acerto.html'
ENDERECAMENTO = 'pagina-estoque-enderecamento.html'
SEP = 'pagina-logistica-separacao-detalhe.html'
CONF = 'pagina-logistica-conferencia-saida-detalhe.html'
CRM = 'pagina-vendas-crm.html'
CATALOGOS = ['pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html',
             'pagina-cadastros-vendedores-detalhe.html']
CHAVES = ['deskBloqueados', 'deskBloqueiosEntrada', 'deskParametros', 'deskLog']

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
    clic(pg, '#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(120)
    pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
    pg.wait_for_timeout(220)


def modal(pg):
    """Texto do modal de confirmacao aberto, ou '' quando nao ha."""
    return pg.inner_text('#confirmModalTexto') if pg.locator('#confirmModal.open').count() else ''


def pede_senha(pg):
    return pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal')


def confirmar(pg):
    """Confirma o modal aberto, com a senha quando a tela pede. Serve tambem para fechar aviso."""
    if pg.locator('#confirmModal.open').count():
        pg.evaluate("() => { const c = document.querySelector('#confirmModal input[type=checkbox]'); if (c && c.offsetParent !== null && !c.checked) c.click(); }")
        if visivel(pg, '#campoSenhaModal'):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)


def ir(pg, tela, query=''):
    pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(550)


def zerar(pg, param=None):
    """Comeca do zero: fila na semente, caixa de entrada vazia, sem registro e com os parametros pedidos."""
    ir(pg, BLOQ)
    pg.evaluate("([chaves, p]) => { chaves.forEach(k => localStorage.removeItem(k)); if (p) localStorage.setItem('deskParametros', JSON.stringify(p)); }", [CHAVES, param])
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(550)


def abas(pg):
    return pg.evaluate("Array.from(document.querySelectorAll('#abasSituacao .aba-sit')).map(a => a.getAttribute('data-sit') + ':' + a.querySelector('.sit-contador').textContent)")


def skus(pg):
    return pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => tr.querySelector('.prod-sku').textContent)")


def linha(pg, id_):
    return pg.evaluate("(id) => { const tr = document.querySelector('#corpoTabela tr[data-id=\"' + id + '\"]'); return tr ? tr.innerText.replace(/\\s+/g, ' ') : null; }", id_)


def abrir(pg, id_):
    clic(pg, '#corpoTabela tr[data-id="%d"]' % id_); pg.wait_for_timeout(400)


def acao(pg, qual):
    clic(pg, 'input[name="resAcao"][value="%s"]' % qual); pg.wait_for_timeout(220)


def item(pg, id_):
    return pg.evaluate("(id) => ITENS.find(i => i.id === id) || null", id_)


def qtd(pg, id_):
    """Quantidade ainda bloqueada na linha, ou None quando ela ja saiu da fila."""
    i = item(pg, id_)
    return i['qtd'] if i else None


def caixa(pg):
    return pg.evaluate("JSON.parse(localStorage.getItem('deskBloqueiosEntrada') || '{}')")


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    # Contexto explicito: a fila, a pagina do produto e as telas de galpao dividem o armazenamento.
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('\n[1] Menu e abertura')
    padrao = re.compile(r'data-label="Itens Bloqueados" data-href="\.\./estoque/pagina-estoque-itens-bloqueados\.html">.*?</div>\s*<div class="flyout-item" data-label="Acerto de Estoque"', re.S)
    com_menu = [c for c in localiza.caminhos() if 'data-label="Acerto de Estoque"' in open(c, encoding='utf-8').read()]
    sem = [_os.path.basename(c) for c in com_menu if len(padrao.findall(open(c, encoding='utf-8').read())) != open(c, encoding='utf-8').read().count('data-label="Acerto de Estoque"')]
    ok(len(com_menu) >= 79 and not sem, 'toda tela com menu traz Itens Bloqueados logo acima de Acerto de Estoque: %d telas, faltando %s' % (len(com_menu), sem[:3]))
    ir(pg, CRM)
    clic(pg, '.nav-item[data-id="estoque"]'); pg.wait_for_timeout(450)
    clic(pg, '#flyout-estoque .flyout-item[data-label="Itens Bloqueados"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
    ok(pg.url.endswith(BLOQ), 'o item do menu abre a tela: %s' % pg.url.split('/')[-1])
    zerar(pg)
    ok(pg.inner_text('h1') == 'Itens Bloqueados' and pg.inner_text('#breadcrumb').replace('\n', ' ').replace('  ', ' ').strip().endswith('Itens Bloqueados')
       and pg.evaluate("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'estoque', 'titulo, caminho e modulo marcado no menu lateral')

    print('\n[2] Lista')
    ok(abas(pg) == ['todos:7', 'avaria:4', 'falta:1', 'analise:1', 'decisao:1', 'resolvidos:2'], 'as abas contam cada motivo, e resolvidos fica fora de "todos": %s' % abas(pg))
    ok(skus(pg) == ['CAM-DKB-011', 'MON-27I-015', 'CAB-HDM-009', 'KIT-HOF-005', 'POL-ALM-040', 'MAT-TEC-008', 'TEC-MEC-006'], 'abre com o mais antigo em cima: %s' % skus(pg))
    mon = linha(pg, 2)
    ok(all(x in mon for x in ['Monitor Desk 27" IPS', 'Galpão Centro', 'AV-02 · Avaria', '2 UN', 'AVARIA', 'Acerto de estoque', 'AC-0041', '9 dias']), 'a linha diz produto, onde esta, quanto, motivo, origem e ha quanto tempo: %s' % mon)
    cores = pg.evaluate("[7, 2, 4, 1, 5].map(id => document.querySelector('#corpoTabela tr[data-id=\"' + id + '\"] td:last-child span').className)")
    ok(cores == ['dias-critico', 'dias-critico', 'dias-alerta', 'dias-alerta', 'dias-ok'], 'o tempo bloqueado muda de cor pelos prazos de Parametros de estoque: %s' % cores)
    tec = linha(pg, 3)
    ok('aguardando endereço de Avaria' in tec and '2,50 M' in tec, 'avaria sem endereco diz que espera um, e a quantidade segue a unidade: %s' % tec)
    ok('R04-P02-N2 · Picking' in linha(pg, 5) and 'Pedido #23' in linha(pg, 5) and 'FALTA A AUDITAR' in linha(pg, 5).upper(), 'a falta fica no proprio endereco e aponta o pedido')
    ok(pg.inner_text('#contagemItens') == '7 itens' and pg.inner_text('#custoParado') == 'R$ 4.711,70', 'o rodape soma os itens e o custo parado: %s' % pg.inner_text('#custoParado'))
    aviso = pg.inner_text('#avisoBloqueados')
    ok('7 bloqueios' in aviso and 'fora da venda' in aviso and '2 estão parados há mais de 7 dias' in aviso, 'o aviso diz quantos, que estao fora da venda e quantos passaram do prazo')
    ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440 and pg.evaluate("(() => { const w = document.querySelector('#painelBloqueados .estoque-table-wrap'); return w.scrollWidth <= w.clientWidth + 1; })()"),
       'a tabela cabe no cartao em 1440')

    print('\n[3] Filtros')
    clic(pg, '#abasSituacao [data-sit="avaria"]'); pg.wait_for_timeout(250)
    ok(len(skus(pg)) == 4 and pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela .badge-situacao')).every(b => b.textContent === 'Avaria')"), 'a aba mostra so o motivo dela')
    clic(pg, '#abasSituacao [data-sit="todos"]'); pg.wait_for_timeout(200)
    pg.fill('#campoBusca', 'pedido #23'); pg.wait_for_timeout(250)
    ok(skus(pg) == ['POL-ALM-040'] and abas(pg)[0] == 'todos:1' and abas(pg)[2] == 'falta:1' and abas(pg)[1] == 'avaria:0', 'a busca acha pelo documento de origem, e os contadores acompanham: %s' % abas(pg))
    pg.fill('#campoBusca', 'av-01'); pg.wait_for_timeout(250)
    ok(sorted(skus(pg)) == ['CAB-HDM-009', 'KIT-HOF-005'], 'e pelo endereco: %s' % skus(pg))
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(200)
    escolher(pg, 'filtroTempo', 'critico')
    criticos = skus(pg)
    escolher(pg, 'filtroTempo', 'alerta')
    ok(criticos == ['CAM-DKB-011', 'MON-27I-015'] and len(skus(pg)) == 4, 'o filtro de tempo usa os dois prazos: %s e %d' % (criticos, len(skus(pg))))
    escolher(pg, 'filtroTempo', 'todos'); escolher(pg, 'filtroDeposito', '1')
    ok(visivel(pg, '#emptyState') and not visivel(pg, '#painelBloqueados .estoque-table-wrap') and pg.inner_text('#contagemItens') == '0 itens', 'deposito sem bloqueio mostra o estado vazio')
    clic(pg, '#btnLimparFiltros'); pg.wait_for_timeout(300)
    ok(len(skus(pg)) == 7 and pg.inner_text('#filtroDeposito .dropdown-select-label') == 'Todos os depósitos', '"limpar filtros" devolve a fila inteira')
    clic(pg, '#painelBloqueados th[data-ordem="qtd"]'); pg.wait_for_timeout(250)
    qts = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => ITENS.find(i => i.id === Number(tr.getAttribute('data-id'))).qtd)")
    ok(qts == sorted(qts) and qts[-1] == 8, 'clicar no cabecalho ordena pela coluna: %s' % qts)
    ir(pg, BLOQ, '?produto=MON-27I-015')
    ok(pg.input_value('#campoBusca') == 'MON-27I-015' and skus(pg) == ['MON-27I-015'], 'vindo da pagina do produto, a fila abre filtrada nele')
    zerar(pg, {'enderecamentoAlerta': 4})
    ok(pg.evaluate("document.querySelector('#corpoTabela tr[data-id=\"1\"] td:last-child span').className") == 'dias-ok'
       and 'Há mais de 4 dias' in pg.evaluate("document.getElementById('menuFiltroTempo').textContent"), 'mudar o prazo em Parametros de estoque muda a cor e o filtro')
    zerar(pg)

    print('\n[4] Liberar parte de um bloqueio de avaria')
    abrir(pg, 2)
    corpo = pg.inner_text('#drawerCorpo')
    ok(pg.locator('#eventDrawer.open').count() == 1 and pg.inner_text('#drawerTitulo') == 'Resolver bloqueio' and all(x in corpo for x in ['Monitor Desk 27" IPS', 'MON-27I-015', 'AV-02', 'AC-0041', 'há 9 dias', 'Fernanda Lima', 'Tela trincada.']),
       'o painel abre com tudo que se sabe do bloqueio')
    ok(not visivel(pg, '#resCampos'), 'antes de escolher o que fazer, nenhum campo aparece')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroAcao') and pg.locator('#eventDrawer.open').count() == 1, 'confirmar sem escolher e barrado')
    acao(pg, 'liberar')
    ok(visivel(pg, '#resCampos') and not visivel(pg, '#wrapCausa') and not visivel(pg, '#wrapPerda') and pg.input_value('#resQtd') == '2' and pg.inner_text('#btnConfirmarResolver') == 'Liberar para venda',
       'liberar mostra a quantidade inteira, sem causa e sem motivo de perda: campo que nao se aplica some')
    previa = pg.inner_text('#resPrevia')
    ok('Destino de 2 UN: disponível, na base de picking D-04-2-01' in previa and 'recuperado' in previa, 'avaria liberada volta para a base de picking, e a tela diz o que liberar significa: %s' % previa[:70])
    barrados = []
    for valor in ['3', '0', '1,5', 'dois']:
        pg.fill('#resQtd', valor); clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(180)
        barrados.append(pg.inner_text('#erroResQtd') if visivel(pg, '#erroResQtd') else '')
    ok('Só há 2 UN' in barrados[0] and 'maior que zero' in barrados[1] and 'número inteiro' in barrados[2] and 'maior que zero' in barrados[3] and qtd(pg, 2) == 2,
       'quantidade acima do bloqueado, zerada, quebrada em UN ou que nao e numero nao passa: %s' % [b[:22] for b in barrados])
    pg.fill('#resQtd', '1'); pg.wait_for_timeout(150)
    ok('Destino de 1 UN' in pg.inner_text('#resPrevia') and not visivel(pg, '#erroResQtd'), 'corrigir a quantidade limpa o erro e refaz a previa')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450)
    ok(not pede_senha(pg) and 'Liberação registrada: 1 UN de Monitor' in modal(pg) and 'D-04-2-01' in modal(pg), 'liberar nao pede senha por padrao, e avisa para onde foi: %s' % modal(pg)[:60])
    confirmar(pg)
    r = pg.evaluate('RESOLVIDOS[0]')
    ok(pg.locator('#eventDrawer.open').count() == 0 and qtd(pg, 2) == 1 and '1 UN' in (linha(pg, 2) or '') and abas(pg)[0] == 'todos:7' and abas(pg)[5] == 'resolvidos:3',
       'liberar parte deixa o resto bloqueado na mesma linha: %s' % abas(pg))
    ok(r['sku'] == 'MON-27I-015' and r['qtd'] == 1 and r['desfecho'] == 'liberado' and r['destino'] == 'D-04-2-01' and r['causa'] is None and r['quem'] == 'Administrador Desk',
       'e o desfecho fica guardado com quem resolveu')

    print('\n[5] Liberar uma falta pede a causa')
    abrir(pg, 5); acao(pg, 'liberar')
    causas = pg.evaluate("Array.from(document.querySelectorAll('#resCausa .dropdown-select-item')).map(e => e.getAttribute('data-value'))")
    ok(visivel(pg, '#wrapCausa') and causas == ['erro_separacao', 'erro_conferencia', 'outro_lugar'], 'a falta mostra as causas: %s' % causas)
    ok('no mesmo endereço (R04-P02-N2)' in pg.inner_text('#resPrevia'), 'o que nao e avaria volta a ficar disponivel no mesmo endereco')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(220)
    ok(visivel(pg, '#erroCausa') and item(pg, 5) is not None, 'sem causa, a falta nao e liberada')
    escolher(pg, 'resCausa', 'erro_separacao')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450)
    ok('erro de separação' in modal(pg), 'o aviso repete a causa apontada')
    confirmar(pg)
    r = pg.evaluate('RESOLVIDOS[0]')
    ok(item(pg, 5) is None and abas(pg)[2] == 'falta:0' and abas(pg)[0] == 'todos:6' and r['causa'] == 'erro_separacao' and r['destino'] == 'R04-P02-N2' and r['doc'] == 'Pedido #23',
       'resolvido inteiro, o item sai da fila e a causa fica no historico')

    print('\n[6] Dar baixa: motivo, aviso fiscal e senha')
    abrir(pg, 1); acao(pg, 'baixar')
    ok(visivel(pg, '#wrapPerda') and not visivel(pg, '#wrapCausa') and pg.inner_text('#btnConfirmarResolver') == 'Dar baixa', 'dar baixa mostra o motivo da perda')
    previa = pg.inner_text('#resPrevia')
    ok('AC-0051' in previa and 'baixa de 1 UN' in previa and 'R$ 1.398,00' in previa, 'a previa diz o acerto que nasce, quanto sai e o custo: %s' % previa[:80])
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(220)
    ok(visivel(pg, '#erroPerda') and pg.locator('#confirmModal.open').count() == 0, 'sem motivo, a baixa nao segue')
    fiscais = []
    for motivo in ['deterioracao', 'erro_lancamento', 'quebra']:
        escolher(pg, 'resPerda', motivo); fiscais.append(pg.inner_text('#resPrevia'))
    ok('Não gera NF-e' in fiscais[0] and 'NF-e' not in fiscais[1] and 'obrigação fiscal' in fiscais[2] and 'CFOP 5.927' in fiscais[2], 'o aviso fiscal segue o motivo, como no Acerto de Estoque')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450)
    ok(pede_senha(pg) and 'Dar baixa em 1 UN de Kit Home Office Completo por quebra ou avaria' in modal(pg) and 'AC-0051' in modal(pg), 'a baixa pede senha e diz o que vai acontecer')
    clic(pg, '#btnConfirmModalCancelar'); pg.wait_for_timeout(300)
    ok(qtd(pg, 1) == 1 and pg.evaluate('ESTADO.proxAcerto') == 51 and pg.locator('#eventDrawer.open').count() == 1, 'cancelar na senha nao baixa nada nem gasta o numero do acerto')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(400)
    clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
    ok(pede_senha(pg) and item(pg, 1) is not None, 'senha em branco nao confirma')
    confirmar(pg)
    ok('Baixa registrada no acerto AC-0051' in modal(pg) and 'fila de baixas pendentes de regularização fiscal' in modal(pg), 'com a senha, a baixa acontece e lembra da obrigacao fiscal: %s' % modal(pg)[:60])
    confirmar(pg)
    r = pg.evaluate('RESOLVIDOS[0]')
    ok(item(pg, 1) is None and r['desfecho'] == 'baixado' and r['acerto'] == 'AC-0051' and r['motivoPerda'] == 'Quebra ou avaria' and pg.evaluate('ESTADO.proxAcerto') == 52,
       'o item sai da fila e o historico guarda o acerto e o motivo')

    print('\n[7] Unidade fracionavel, e avaria de produto sem base de picking')
    abrir(pg, 3); acao(pg, 'liberar')
    ok(pg.input_value('#resQtd') == '2,50' and 'aguardando endereço de Avaria' in pg.inner_text('#drawerCorpo'), 'tecido abre com a quantidade em metros')
    pg.fill('#resQtd', '1,25'); clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450); confirmar(pg)
    ok(qtd(pg, 3) == 1.25 and '1,25 M' in linha(pg, 3) and pg.evaluate('RESOLVIDOS[0].destino') == 'A-10-1-01', 'em metro a quantidade pode ser quebrada, e sobra o resto: %s' % linha(pg, 3)[:60])
    abrir(pg, 4); acao(pg, 'liberar')
    ok('fila de endereçar' in pg.inner_text('#resPrevia') and 'não tem base de picking' in pg.inner_text('#resPrevia'), 'sem base de picking no deposito, a avaria liberada vai para a fila de enderecar')
    clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450); confirmar(pg)
    ok(item(pg, 4) is None and pg.evaluate('RESOLVIDOS[0].destino') == 'a endereçar', 'e o destino fica registrado assim')

    print('\n[8] Resolvidos, e o que sobrevive ao F5')
    clic(pg, '#abasSituacao [data-sit="resolvidos"]'); pg.wait_for_timeout(300)
    ok(visivel(pg, '#painelResolvidos') and not visivel(pg, '#painelBloqueados') and pg.locator('#corpoResolvidos tr').count() == 7, 'a aba troca a fila pelo historico: %d linhas' % pg.locator('#corpoResolvidos tr').count())
    primeira = pg.evaluate("document.querySelector('#corpoResolvidos tr').innerText.replace(/\\s+/g, ' ')")
    ok(all(x in primeira for x in ['Cabo HDMI', '3 UN', 'Avaria', 'NF-e 13.240', 'LIBERADO', 'Recuperado', 'a endereçar', 'Administrador Desk']), 'cada linha diz o que era, o desfecho e quem resolveu: %s' % primeira[:90])
    todo = pg.inner_text('#corpoResolvidos')
    ok('BAIXADO' in todo.upper() and 'Quebra ou avaria · AC-0051' in todo and 'Estava no endereço: erro de separação' in todo, 'a baixa mostra motivo e acerto, e a falta mostra a causa')
    ok(pg.inner_text('#resumoResolvidos') == '7 resolvidos' and pg.inner_text('#totalBaixado') == 'R$ 1.484,20', 'o rodape soma o que foi baixado como perda: %s' % pg.inner_text('#totalBaixado'))
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(550)
    ok(abas(pg) == ['todos:4', 'avaria:2', 'falta:0', 'analise:1', 'decisao:1', 'resolvidos:7'] and qtd(pg, 2) == 1 and qtd(pg, 3) == 1.25 and pg.evaluate('ESTADO.proxAcerto') == 52,
       'tudo sobrevive ao F5: %s' % abas(pg))

    print('\n[9] A senha obedece a Configuracoes -> Confirmacoes por senha')
    pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({ confirmacoes: { bloqueadosLibera: true, bloqueadosBaixa: false } }))")
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(550)
    abrir(pg, 6); acao(pg, 'liberar'); clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450)
    ok(pede_senha(pg) and 'Liberar 2 UN de Teclado Mecânico Desk para venda' in modal(pg) and item(pg, 6) is not None, 'ligada na matriz, a liberacao passa a pedir senha')
    confirmar(pg); confirmar(pg)
    abrir(pg, 7); acao(pg, 'baixar'); escolher(pg, 'resPerda', 'perda'); pg.fill('#resQtd', '3'); clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450)
    ok(not pede_senha(pg) and 'Baixa registrada no acerto AC-0052' in modal(pg) and qtd(pg, 7) == 5, 'desligada na matriz, a baixa acontece direto: %s' % modal(pg)[:50])
    confirmar(pg)
    log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').map(l => l.chave + ':' + l.senha)")
    ok(log[:2] == ['bloqueadosBaixa:false', 'bloqueadosLibera:true'] and 'bloqueadosBaixa:true' in log and 'bloqueadosLibera:false' in log, 'com ou sem senha, tudo vai para o registro de atividades: %s' % log[:4])

    print('\n[10] "Bloquear item" leva para a pagina do produto')
    zerar(pg)
    clic(pg, '#btnBloquearItem'); pg.wait_for_timeout(400)
    ok(pg.inner_text('#drawerTitulo') == 'Bloquear item' and pg.locator('#bloqProduto .dropdown-select-item').count() == 15 and 'página do produto' in pg.inner_text('#drawerCorpo'), 'o painel explica onde o bloqueio e lancado e lista os produtos')
    clic(pg, '#btnContinuarBloqueio'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroBloqProduto') and pg.url.split('/')[-1].startswith(BLOQ), 'sem produto, nao sai do lugar')
    escolher(pg, 'bloqProduto', 6)
    clic(pg, '#btnContinuarBloqueio'); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    ok(PROD in pg.url and 'produto=6' in pg.url and pg.inner_text('#tituloProduto') == 'Teclado Mecânico Desk' and pg.locator('#eventDrawer.open').count() == 1
       and pg.get_attribute('#campoTipo', 'data-value') == 'bloqueio', 'abre o produto com o lancamento ja no tipo Bloqueio: %s' % pg.url.split('/')[-1])

    print('\n[11] O tipo Bloqueio no lancamento do Controle de Estoques')
    def kpis():
        return [pg.inner_text('#kpiFisico').replace('\n', ''), pg.inner_text('#kpiBloqueado'), pg.inner_text('#kpiDisponivel')]
    def aviso_produto():
        t = pg.inner_text('#avisoTexto') if pg.locator('#avisoModal.open').count() else ''
        if t: clic(pg, '#btnAvisoOk'); pg.wait_for_timeout(250)
        return t
    antes = kpis()
    ok(antes == ['40UN', '0', '40'] and visivel(pg, '#notaBloqueado') and not visivel(pg, '#linkBloqueados'), 'sem nada bloqueado, o produto nao oferece o atalho: %s' % antes)
    motivos = pg.evaluate("Array.from(document.querySelectorAll('#menuMotivo .dropdown-select-item')).map(e => e.textContent)")
    origens = pg.evaluate("Array.from(document.querySelectorAll('#menuOrigem .dropdown-select-item')).map(e => e.textContent)")
    ok(motivos == ['Avaria', 'Falta a auditar', 'Em análise', 'Travado por decisão'] and not visivel(pg, '#wrapPreco'), 'o bloqueio troca os motivos e esconde o preco: %s' % motivos)
    ok(visivel(pg, '#wrapOrigem') and len(origens) == 2 and all('Disponível' in o for o in origens), 'com saldo em dois enderecos, pergunta de qual sai, e nunca oferece o que ja esta bloqueado: %s' % origens)
    ok('não muda o estoque físico nem o custo' in pg.inner_text('#previaEntrada') and 'Itens Bloqueados' in pg.inner_text('#previaEntrada'), 'a previa diz o que o bloqueio faz e onde ele se resolve')
    clic(pg, '#btnSalvarLancamento'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroQuantidade') and visivel(pg, '#erroMotivo') and pg.inner_text('#erroMotivo') == 'Escolha o motivo do bloqueio.', 'sem quantidade e sem motivo, nao salva')
    pg.fill('#campoQuantidade', '99'); escolher(pg, 'campoMotivo', 'analise'); clic(pg, '#btnSalvarLancamento'); pg.wait_for_timeout(350)
    ok('apenas 6 UN' in aviso_produto() and kpis() == antes, 'nao bloqueia mais do que ha no endereco')
    pg.fill('#campoQuantidade', '2'); escolher(pg, 'campoMotivo', 'decisao'); clic(pg, '#btnSalvarLancamento'); pg.wait_for_timeout(350)
    ok('Escreva nas observações' in aviso_produto() and kpis() == antes, 'travar por decisao exige dizer por que')
    escolher(pg, 'campoMotivo', 'analise')
    ok('no mesmo endereço' in pg.inner_text('#previaEntrada'), 'o que nao e avaria fica no mesmo endereco')
    pg.fill('#campoObs', 'Teclas falhando no teste.'); clic(pg, '#btnSalvarLancamento'); pg.wait_for_timeout(450)
    dito = aviso_produto()
    ok('Bloqueio registrado: 2 UN de Teclado Mecânico Desk, motivo Em análise, em A-05-1-02' in dito and 'Itens Bloqueados' in dito and pg.locator('#eventDrawer.open').count() == 0, 'salva sem senha por padrao e avisa onde resolver: %s' % dito[:70])
    saldos = pg.evaluate("produtoAtual.saldos.filter(s => s.endereco === 'A-05-1-02').map(s => s.estagio + ':' + s.qtd).sort()")
    ok(kpis() == ['40UN', '2', '38'] and saldos == ['bloqueado:2', 'disponivel:4'], 'o fisico nao muda: a quantidade so passa de disponivel para bloqueado, no mesmo endereco: %s %s' % (kpis(), saldos))
    ok(visivel(pg, '#linkBloqueados') and not visivel(pg, '#notaBloqueado') and pg.get_attribute('#linkBloqueados', 'href').endswith('pagina-estoque-itens-bloqueados.html?produto=TEC-MEC-006'), 'e o numero bloqueado ganha o atalho para a fila, filtrada no produto')
    extrato = pg.evaluate("document.querySelector('#corpoLancamentos tr').innerText.replace(/\\s+/g, ' ')")
    ok('Bloqueio' in extrato and 'BL-' in extrato and '2 UN · Em análise · A-05-1-02 · Teclas falhando no teste.' in extrato, 'o extrato do produto registra o bloqueio: %s' % extrato[:90])
    escolher(pg, 'filtroTipoMov', 'bloqueio')
    ok(pg.locator('#corpoLancamentos tr').count() == 1, 'e o filtro de tipo acha so ele')
    escolher(pg, 'filtroTipoMov', 'todos')
    clic(pg, '#btnIncluirLancamento'); pg.wait_for_timeout(350)
    pg.fill('#campoQuantidade', '1'); escolher(pg, 'campoMotivo', 'avaria')
    ok('endereço de Avaria' in pg.inner_text('#previaEntrada'), 'avaria avisa que muda de endereco')
    clic(pg, '#btnSalvarLancamento'); pg.wait_for_timeout(450)
    ok('ainda sem endereço de Avaria' in aviso_produto() and pg.evaluate("produtoAtual.saldos.filter(s => s.estagio === 'bloqueado' && s.endereco === null && s.qtd === 1).length") == 1 and kpis() == ['40UN', '3', '37'],
       'avaria sai do endereco de venda e espera um endereco de Avaria: %s' % kpis())
    cx = caixa(pg)
    ok(len(cx) == 2 and sorted(v['motivo'] for v in cx.values()) == ['analise', 'avaria'], 'os dois bloqueios ficam na caixa de entrada da fila: %s' % list(cx.keys()))
    clic(pg, '#linkBloqueados'); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    novos = pg.evaluate("ITENS.filter(i => i.sku === 'TEC-MEC-006' && i.id > 7).map(i => [i.motivo, i.qtd, i.endereco, i.base, i.custo, i.origem, i.obs].join('|')).sort()")
    ok(pg.input_value('#campoBusca') == 'TEC-MEC-006' and novos == ['analise|2|A-05-1-02|A-05-1-02|231.1|manual|Teclas falhando no teste.', 'avaria|1||A-05-1-02|231.1|manual|'],
       'a fila recolhe os dois, com endereco, base, custo e observacao: %s' % novos)
    ok(caixa(pg) == {} and len(skus(pg)) == 3 and 'aguardando endereço de Avaria' in pg.inner_text('#corpoTabela'), 'esvazia a caixa de entrada e mostra o que chegou')
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
    ok(pg.evaluate('ITENS.length') == 9, 'recarregar nao traz o mesmo bloqueio duas vezes: %d' % pg.evaluate('ITENS.length'))
    ir(pg, PROD, '?produto=5')
    ok(kpis() == ['5UN', '1', '4'] and visivel(pg, '#linkBloqueados') and 'KIT-HOF-005' in pg.get_attribute('#linkBloqueados', 'href'), 'o produto do print do usuario ja abre com o atalho: %s' % kpis())

    print('\n[12] A falta da separacao bloqueia a unidade')
    zerar(pg)
    ir(pg, SEP)
    fonte = pg.content()
    ok('fica <b>bloqueada para venda</b> em Estoque → Itens Bloqueados' in fonte and 'não é mexido aqui' not in fonte and 'aguardando reconferência' not in fonte, 'a tela deixou de dizer que o saldo nao e mexido')
    pedido = pg.evaluate('PEDIDO.numero')
    pg.evaluate("COLETA.forEach(i => { i.separado = i.qtd; i.motivo = ''; i.declarando = false; }); COLETA[0].separado = COLETA[0].qtd - 2; COLETA[0].motivo = 'Endereço com menos peças.'; pintarItens();")
    clic(pg, '#btnConcluir'); pg.wait_for_timeout(400)
    ok('fica bloqueado para venda em Estoque → Itens Bloqueados' in modal(pg) and 'Nenhum saldo é baixado' in modal(pg) and caixa(pg) == {}, 'concluir com falta avisa do bloqueio, e nada e bloqueado antes de confirmar')
    confirmar(pg)
    ok('bloqueado para venda, aguardando auditoria em Estoque → Itens Bloqueados' in modal(pg), 'o aviso final manda para Itens Bloqueados: %s' % modal(pg)[:70])
    confirmar(pg)
    cx = caixa(pg)
    chave = 'sep:%s:MES-ESC-120' % pedido
    ok(list(cx.keys()) == [chave] and cx[chave]['qtd'] == 2 and cx[chave]['endereco'] == 'R02-P01-N1' and cx[chave]['motivo'] == 'falta' and cx[chave]['origem'] == 'separacao'
       and cx[chave]['doc'] == 'Pedido #%s' % pedido and cx[chave]['obs'] == 'Endereço com menos peças.', 'so o item que faltou e bloqueado, na quantidade que faltou e no endereco dele: %s' % list(cx.keys()))

    print('\n[13] A falta da conferencia de saida tambem')
    ir(pg, CONF)
    fonte = pg.content()
    ok('fica <b>bloqueado para venda</b>, aguardando auditoria em Estoque → Itens Bloqueados' in fonte and 'aguardando reconferência' not in fonte, 'a bancada tambem mudou o texto')
    pedido_c = pg.evaluate('PEDIDO.numero')
    pg.evaluate("ITENS.forEach(i => { i.conferida = i.separado; i.bancou = false; i.motivo = ''; }); ITENS[1].conferida = ITENS[1].separado - 1; ITENS[1].bancou = true; ITENS[1].motivo = 'nao_veio'; VOLUMES.forEach(v => { if (!v.emb) v.emb = 5; }); compensaEscolhida = 'restituicao';")
    clic(pg, '#btnFechar'); pg.wait_for_timeout(400)
    ok('o que faltou fica bloqueado para venda em Estoque → Itens Bloqueados' in modal(pg), 'fechar com divergencia avisa do bloqueio: %s' % modal(pg)[-110:])
    confirmar(pg); confirmar(pg)
    cx = caixa(pg)
    chave_c = 'conf:%s:TAP-SAL-200' % pedido_c
    ok(sorted(cx.keys()) == sorted([chave, chave_c]) and cx[chave_c]['qtd'] == 1 and cx[chave_c]['origem'] == 'conferencia_saida' and cx[chave_c]['quem'] == 'Tatiane Moura',
       'a peca que a caixa nao tinha e bloqueada; o item que ja veio com falta da separacao nao entra de novo: %s' % sorted(cx.keys()))
    # caso torto na caixa: motivo que nao existe e quantidade zero nao viram linha
    pg.evaluate("(() => { const c = JSON.parse(localStorage.getItem('deskBloqueiosEntrada')); c['lixo:1'] = { sku: 'X', qtd: 3, motivo: 'inventado' }; c['lixo:2'] = { sku: 'Y', qtd: 0, motivo: 'falta' }; localStorage.setItem('deskBloqueiosEntrada', JSON.stringify(c)); })()")
    ir(pg, BLOQ)
    chegou = pg.evaluate("ITENS.filter(i => i.id > 7).map(i => [i.sku, i.qtd, i.motivo, i.origem, i.doc, i.endereco, i.quem].join('|')).sort()")
    ok(chegou == ['MES-ESC-120|2|falta|separacao|Pedido #%s|R02-P01-N1|Jonas Ribeiro' % pedido, 'TAP-SAL-200|1|falta|conferencia_saida|Pedido #%s||Tatiane Moura' % pedido_c] and abas(pg)[2] == 'falta:3',
       'as duas faltas chegam a fila como "Falta a auditar", e o que veio torto fica de fora: %s' % chegou)
    id_conf = pg.evaluate("ITENS.find(i => i.sku === 'TAP-SAL-200').id")
    ok('endereço não informado' in linha(pg, id_conf) and 'Conferência de saída' in linha(pg, id_conf) and 'hoje' in linha(pg, id_conf), 'a da conferencia diz de onde veio e que nao sabe o endereco: %s' % linha(pg, id_conf)[:90])
    abrir(pg, id_conf); acao(pg, 'baixar'); escolher(pg, 'resPerda', 'extravio')
    ok('baixa de 1 UN.' in pg.inner_text('#resPrevia') and 'R$' not in pg.inner_text('#resPrevia').split('Gera obrigação')[0], 'sem custo conhecido, a previa nao inventa valor')
    acao(pg, 'liberar'); escolher(pg, 'resCausa', 'erro_conferencia'); clic(pg, '#btnConfirmarResolver'); pg.wait_for_timeout(450); confirmar(pg)
    ok(pg.evaluate('RESOLVIDOS[0].causa') == 'erro_conferencia' and pg.evaluate('RESOLVIDOS[0].origem') == 'conferencia_saida', 'a auditoria fecha a falta com a causa: erro de conferencia')
    pg.evaluate("(k) => localStorage.setItem('deskBloqueiosEntrada', JSON.stringify({ [k]: { sku: 'MES-ESC-120', produto: 'Mesa', qtd: 2, motivo: 'falta', origem: 'separacao' } }))", chave)
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
    ok(pg.evaluate("ITENS.filter(i => i.sku === 'MES-ESC-120').length") == 1 and caixa(pg) == {}, 'o mesmo caso publicado de novo nao entra duas vezes')

    print('\n[14] Espelhos: o que esta tela repete das outras')
    zerar(pg)
    semente = pg.evaluate('semente().itens')
    baixa_aqui = pg.evaluate('MOTIVOS_BAIXA')
    espelho = pg.evaluate('PRODUTOS_ESPELHO')
    motivos_aqui = pg.evaluate("Object.keys(MOTIVOS_BLOQ).map(k => k + ':' + MOTIVOS_BLOQ[k].rotulo)")
    ir(pg, ACERTO)
    ok(baixa_aqui == pg.evaluate('MOTIVOS.saida'), 'os motivos de baixa sao os de saida do Acerto de Estoque, com a mesma consequencia fiscal')
    ir(pg, PROD)
    ok(espelho == pg.evaluate('PRODUTOS.map(p => ({ id: p.id, sku: p.sku, nome: p.nome }))'), 'a lista de produtos e a do Controle de Estoques')
    ok(motivos_aqui == pg.evaluate("MOTIVOS_BLOQUEIO.map(m => m.v + ':' + m.l)") and baixa_aqui == pg.evaluate('MOTIVOS.saida'), 'os motivos de bloqueio sao os mesmos na fila e na pagina do produto')
    bloqueados = pg.evaluate("""PRODUTOS.flatMap(p => p.saldos.filter(s => s.estagio === 'bloqueado').map(s => {
        const b = BASES.find(x => x.produto === p.id && x.dep === s.dep);
        return [p.sku, s.dep, s.endereco, s.qtd, p.custoMedio, p.unidade, b ? b.endereco : null].join('|'); }))""")
    aqui_js = pg.evaluate("(l) => l.map(i => [i.sku, i.dep, i.endereco, i.qtd, i.custo, i.un, i.base].join('|'))", semente)
    ok(len(bloqueados) == 2 and all(b in aqui_js for b in bloqueados), 'todo saldo bloqueado do Controle de Estoques esta na fila, com endereco, custo e base: %s' % bloqueados)
    ir(pg, ENDERECAMENTO)
    fila_end = pg.evaluate("PENDENTES.filter(p => p.situacao === 'bloqueado').map(p => [p.sku, p.dep, p.qtd, 'Nota ' + p.nota].join('|'))")
    ok(len(fila_end) == 1 and all(e in ['|'.join(str(x) for x in [i['sku'], i['dep'], i['qtd'], i['doc']]) for i in semente if i['endereco'] is None] for e in fila_end),
       'a avaria que o Enderecamento mostra sem endereco e a mesma daqui: %s' % fila_end)
    ir(pg, CONF)
    veio = pg.evaluate("FILA.flatMap(p => p.itens.filter(i => i.separado < i.pedido).map(i => [i.sku, i.pedido - i.separado, 'Pedido #' + p.numero].join('|')))")
    ok(len(veio) == 1 and veio[0] in ['|'.join(str(x) for x in [i['sku'], i['qtd'], i['doc']]) for i in semente if i['motivo'] == 'falta'], 'o pedido que a Conferencia mostra com falta da separacao tem a unidade bloqueada aqui: %s' % veio)

    print('\n[15] Catalogo de senhas e registro de atividades')
    esperado = ['bloqueadosBaixa:true:Estoque', 'bloqueadosLibera:false:Estoque', 'estoqueBloqueia:false:Estoque']
    for tela in CATALOGOS + [BLOQ, PROD]:
        ir(pg, tela)
        tem = pg.evaluate("ACOES_SENHA.filter(a => ['estoqueBloqueia', 'bloqueadosLibera', 'bloqueadosBaixa'].includes(a.chave)).map(a => a.chave + ':' + a.exigePadrao + ':' + a.grupo).sort()")
        ok(tem == esperado, '%s conhece as tres acoes, e so a baixa pede senha por padrao' % tela.replace('pagina-', '').replace('.html', ''))
    ir(pg, CATALOGOS[0])
    ok('Dar baixa em item bloqueado' in pg.inner_text('body') and 'Liberar item bloqueado para venda' in pg.inner_text('body') and 'Bloquear saldo de produto' in pg.inner_text('body'), 'Confirmacoes por senha mostra as tres para ligar e desligar')

    print('\n[16] Esc, temas, menu de acoes e erro de JS')
    zerar(pg)
    abrir(pg, 2); acao(pg, 'baixar')
    clic(pg, '#resPerda .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#resPerda .dropdown-select-menu.open').count() == 0 and pg.locator('#eventDrawer.open').count() == 1, 'Esc fecha primeiro o dropdown aberto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    ok(pg.locator('#eventDrawer.open').count() == 0 and qtd(pg, 2) == 2, 'e o segundo fecha o painel, sem resolver nada')
    clic(pg, '#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    destinos = pg.evaluate("Array.from(document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')).map(e => e.textContent)")
    ok(pg.locator('#menuMaisAcoes .dropdown-select-menu.open').count() == 1 and destinos == ['Abrir o Acerto de Estoque', 'Abrir o Endereçamento', 'Abrir os Motivos de Perda'], '"Mais ações" leva as telas vizinhas: %s' % destinos)
    clic(pg, '#menuMaisAcoes [data-acao="motivos"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
    ok(pg.url.endswith('pagina-configuracoes-motivos-perda.html'), 'e navega de verdade: %s' % pg.url.split('/')[-1])
    ir(pg, BLOQ)
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add')); pg.wait_for_timeout(220)
        abrir(pg, 2); acao(pg, 'baixar')
        ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440 and pg.evaluate("(() => { const d = document.getElementById('eventDrawer'); return d.scrollWidth <= d.clientWidth + 1; })()"),
           'tema %s: nem a pagina nem o painel estouram na largura' % tema)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(not erros, 'sem erro de JS em nenhuma das telas: %s' % erros[:2])

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
