# -*- coding: utf-8 -*-
# Pedidos de Venda — listagem e pagina do pedido. Nasceu em 30/set/2026, junto
# com o modulo. O que ele protege nao e a tela: sao as DECISOES da barganha de
# 30/set, que sao caras de mudar depois e faceis de quebrar sem perceber.
#
#   reserva nasce com o pedido e volta no cancelamento
#   baixa fisica so no envio — por isso expedido nao pode ser excluido
#   pedido nao nasce sem saldo, e a mensagem diz QUANTO existe
#   desconto do item forma o preco unitario; desconto do pedido vem depois
#   loja escolhe o deposito, e o pedido e de uma loja so
#   faturado existe mesmo sem NF-e, porque a comissao depende dele
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
LISTA = 'pagina-vendas-pedidos.html'
DET = 'pagina-vendas-pedidos-detalhe.html'

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if (m.type == 'error' and not ruido(m.text)) else None)
    pg.on('dialog', lambda d: d.dismiss())

    def abre(arq, espera=450):
        erros.clear()
        pg.goto(URL + arq); pg.wait_for_timeout(espera)

    def fecha_modal():
        pg.evaluate("fecharModalConfirmacao()"); pg.wait_for_timeout(150)

    def marca(pid):
        pg.evaluate("(function(i){var c=document.querySelector('input.item-checkbox[data-id=\"'+i+'\"]'); if(c) c.click();})(%d)" % pid)
        pg.wait_for_timeout(200)

    # =======================================================================
    print('\n[1] Listagem abre e conta')
    abre(LISTA)
    ok(not erros, 'sem erro de JS na abertura' + (' — ' + erros[0] if erros else ''))
    ok(pg.eval_on_selector_all('#corpoTabela tr', 'e => e.length') > 0, 'a tabela tem linhas')
    ok('Pedidos de Venda' in pg.inner_text('.page-header h1'), 'título da tela')
    crumb = pg.inner_text('#breadcrumb').replace('\n', ' ')
    ok('Vendas' in crumb and 'Pedidos de Venda' in crumb, 'breadcrumb: ' + crumb)

    print('\n[2] Situação é filtro suspenso, não linha de abas (02/out)')
    ok(pg.eval_on_selector_all('.aba-sit, .aba-mais, #abasSituacao', 'e => e.length') == 0,
       'a linha de abas saiu da tela, e o menu "mais" junto')
    pg.click('#filtroSituacao .dropdown-select-btn'); pg.wait_for_timeout(300)
    itens = pg.eval_on_selector_all('#menuFiltroSituacao .dropdown-select-item', 'e => e.map(x => x.getAttribute("data-value"))')
    ok(len(itens) == 10, 'o filtro tem 10 opções (todos + as 9 situações): %d' % len(itens))
    ok('devolucao' not in itens, 'devolução NÃO é situação de pedido de venda — é documento do módulo próprio')
    # O menu "mais" abria escondido. Este nao pode repetir isso, e nem cortar
    # item num scroll: a assercao e a do dedo do usuario, item por item.
    todos_visiveis = pg.evaluate("""() => {
      const its = [...document.querySelectorAll('#menuFiltroSituacao .dropdown-select-item')];
      return its.every(it => {
        const b = it.getBoundingClientRect();
        const a = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
        return !!(a && it.contains(a));
      });
    }""")
    ok(todos_visiveis, 'as 10 opções abrem VISÍVEIS — nenhuma cortada por scroll ou recorte')
    ok(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
       'a página não rola na horizontal')
    # Contador dentro da lista: ele era o que a aba dava de graca, e nao podia
    # se perder na troca. E tem de acompanhar os OUTROS filtros.
    n_todos = int(pg.eval_on_selector('#menuFiltroSituacao .dropdown-select-item[data-value="todos"] .sit-contador', 'e => e.textContent'))
    ok(n_todos == pg.evaluate("baseSemAba().length"), 'o contador de "Todas" bate com a base: %d' % n_todos)
    pg.click('#menuFiltroSituacao .dropdown-select-item[data-value="entregue"]'); pg.wait_for_timeout(350)
    ok(pg.inner_text('#filtroSituacao .dropdown-select-label') == 'Entregue',
       'o botão passa a mostrar a situação escolhida')
    ok(pg.evaluate("pedidosFiltrados().every(p => p.situacao === 'entregue')"), 'e a tabela filtra de verdade')
    # contador acompanha loja
    pg.click('#filtroSituacao .dropdown-select-btn'); pg.wait_for_timeout(180)
    pg.click('#menuFiltroSituacao .dropdown-select-item[data-value="todos"]'); pg.wait_for_timeout(250)
    pg.click('#filtroLoja .dropdown-select-btn'); pg.wait_for_timeout(180)
    pg.click('#filtroLoja .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(300)
    pg.click('#filtroSituacao .dropdown-select-btn'); pg.wait_for_timeout(300)
    n2 = int(pg.eval_on_selector('#menuFiltroSituacao .dropdown-select-item[data-value="todos"] .sit-contador', 'e => e.textContent'))
    ok(n2 == pg.evaluate("baseSemAba().length") and n2 < n_todos,
       'os contadores acompanham os outros filtros (%d com loja filtrada, era %d)' % (n2, n_todos))
    # "Limpar filtros" mora no estado vazio, entao primeiro zerar o resultado:
    # loja 3 + aprovado nao tem nenhum. Isto tambem prova que o estado vazio
    # continua aparecendo depois da troca das abas pelo filtro.
    pg.click('#menuFiltroSituacao .dropdown-select-item[data-value="aprovado"]'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#emptyState', 'e => e.offsetParent !== null'), 'combinação sem resultado mostra o estado vazio')
    pg.click('#btnLimparFiltros'); pg.wait_for_timeout(350)
    ok(pg.inner_text('#filtroSituacao .dropdown-select-label') == 'Todas as situações',
       'limpar filtros devolve a situação para "Todas"')
    ok(pg.evaluate("pedidosFiltrados().length") == pg.evaluate("PEDIDOS.length"),
       'e devolve a lista inteira')

    print('\n[3] Contador e rodapé contam a mesma coisa')
    abre(LISTA)
    pg.click('#filtroSituacao .dropdown-select-btn'); pg.wait_for_timeout(300)
    cont_todos = int(pg.eval_on_selector('#menuFiltroSituacao .dropdown-select-item[data-value="todos"] .sit-contador', 'e => e.textContent'))
    na_lista = pg.evaluate("pedidosFiltrados().length")
    ok(cont_todos == na_lista, 'contador de "Todas" (%d) = itens filtrados (%d)' % (cont_todos, na_lista))
    soma = pg.evaluate("""(() => {
      let s = 0;
      document.querySelectorAll('#menuFiltroSituacao .dropdown-select-item').forEach(e => {
        if (e.getAttribute('data-value') !== 'todos') s += Number(e.querySelector('.sit-contador').textContent);
      });
      return s; })()""")
    ok(soma == cont_todos, 'a soma das situações fecha com "Todas": %d' % soma)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    cancelados = pg.evaluate("pedidosFiltrados().filter(p => p.situacao === 'cancelado').length")
    rodape = pg.inner_text('#contagemPedidos')
    ok(('cancelado' in rodape) == (cancelados > 0), 'o rodapé avisa que cancelado fica fora do total: "%s"' % rodape)
    valor_rodape = pg.inner_text('#valorTotalPedidos')
    esperado = pg.evaluate("'R$ ' + pedidosFiltrados().filter(p => p.situacao !== 'cancelado').reduce((s,p) => s+p.total, 0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})")
    ok(valor_rodape == esperado, 'o valor total exclui os cancelados: %s' % valor_rodape)

    print('\n[4] A reserva aparece na tela')
    com_reserva = pg.eval_on_selector_all('#corpoTabela .ped-reserva', 'e => e.length')
    ok(com_reserva > 0, 'linhas de pedido reservado dizem "estoque reservado": %d' % com_reserva)

    print('\n[5] Excluir: expedido não pode; o resto pede senha')
    enviado = pg.evaluate("(PEDIDOS.filter(p => p.situacao === 'enviado')[0] || {}).id")
    marca(enviado)
    ok(pg.inner_text('#btnExcluirSelecionados').startswith('Nenhum pode'),
       'com pedido enviado o botão diz que não dá: "%s"' % pg.inner_text('#btnExcluirSelecionados'))
    antes = pg.evaluate("PEDIDOS.length")
    pg.click('#btnExcluirSelecionados'); pg.wait_for_timeout(300)
    ok(not pg.eval_on_selector('#campoSenhaModal', 'e => e.classList.contains("on")'),
       'o aviso de que nada pode ser excluído NÃO pede senha')
    ok('devolução' in pg.inner_text('#confirmModalTexto'), 'o aviso aponta o caminho certo: devolução')
    fecha_modal()
    pg.click('#btnCancelarSelecao'); pg.wait_for_timeout(200)

    reservado = pg.evaluate("(PEDIDOS.filter(p => SIT_RESERVA.indexOf(p.situacao) >= 0 && document.querySelector('input.item-checkbox[data-id=\"'+p.id+'\"]'))[0] || {}).id")
    marca(reservado)
    ok('estoque reservado' in pg.inner_text('#selecaoInfo'), 'a barra avisa quantos têm estoque reservado')
    pg.click('#btnExcluirSelecionados'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#campoSenhaModal', 'e => e.classList.contains("on")'), 'excluir pedido PEDE senha')
    ok('reserva de estoque volta' in pg.inner_text('#confirmModalTexto'), 'o texto diz que a reserva volta')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
    ok(pg.evaluate("PEDIDOS.length") == antes, 'sem senha não exclui')
    pg.fill('#inputSenhaModal', 'senha123')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(350)
    ok(pg.evaluate("PEDIDOS.length") == antes - 1, 'com senha exclui')
    ok(pg.evaluate("(JSON.parse(localStorage.getItem('deskLog') || '[]')[0] || {}).chave") == 'pedidosExclui',
       'a exclusão entrou no registro de atividades')

    print('\n[6] Cancelar devolve a reserva')
    abre(LISTA)
    alvo2 = pg.evaluate("(PEDIDOS.filter(p => SIT_RESERVA.indexOf(p.situacao) >= 0 && document.querySelector('input.item-checkbox[data-id=\"'+p.id+'\"]'))[0] || {}).id")
    marca(alvo2)
    pg.click('#btnCancelarSelecionados'); pg.wait_for_timeout(300)
    ok('volta' in pg.inner_text('#confirmModalTexto') and 'disponível' in pg.inner_text('#confirmModalTexto'),
       'o texto diz que a reserva volta para disponível')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(350)
    ok(pg.evaluate("pedidoDe(%d).situacao" % alvo2) == 'cancelado', 'o pedido ficou cancelado')

    print('\n[7] Filtros e período pelas duas datas')
    abre(LISTA)
    pg.click('#filtroLoja .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#filtroLoja .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(300)
    so_da_loja = pg.evaluate("pedidosFiltrados().every(p => p.loja === 3)")
    ok(so_da_loja, 'filtrar por loja mostra só os pedidos dela')
    pg.click('#btnLimparFiltros') if pg.eval_on_selector('#emptyState', 'e => e.style.display !== "none"') else None
    abre(LISTA)
    pg.click('#btnPeriodo'); pg.wait_for_timeout(200)
    pg.click('#periodoAbas .periodo-aba[data-base="faturamento"]'); pg.wait_for_timeout(300)
    ok('faturamento' in pg.inner_text('#rotuloPeriodo'), 'o rótulo diz por qual data está filtrando')
    sem_fat = pg.evaluate("pedidosFiltrados().every(p => p.faturamento !== '')")
    ok(sem_fat, 'filtrando por faturamento, pedido sem nota não aparece com data em branco')

    # =======================================================================
    print('\n[8] Página do pedido: modo de abertura')
    abre(DET)
    ok(not erros, 'sem erro de JS' + (' — ' + erros[0] if erros else ''))
    ok(pg.evaluate("document.body.classList.contains('modo-leitura')"), 'consulta abre em visualização (padrão)')
    pg.click('#btnEditarRegistro'); pg.wait_for_timeout(250)
    ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), 'Editar libera os campos')
    abre(DET + '?editar=1')
    ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), '?editar=1 abre em edição')
    abre(DET + '?novo=1')
    ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), '?novo=1 abre em edição')
    ok(pg.inner_text('#tituloPedido') == 'Novo pedido de venda', 'título do pedido novo')
    ok(pg.input_value('#inputNumero') == '', 'número em branco — gerado ao salvar')

    print('\n[9] Cadastro rápido: só para cliente que não existe, e nasce incompleto')
    pg.fill('#inputCliente', 'Marina Duarte'); pg.wait_for_timeout(300)
    ok(not pg.eval_on_selector('#blocoCliente', 'e => e.classList.contains("aberto")'),
       'cliente que já existe não abre o cadastro rápido')
    pg.fill('#inputCliente', 'Freguês Novo da Silva'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#blocoCliente', 'e => e.classList.contains("aberto")'),
       'cliente novo abre o bloco no próprio pedido, sem sair da tela')
    ok(pg.eval_on_selector('#seloIncompleto', 'e => e.style.display !== "none"'),
       'o registro nasce marcado como CADASTRO INCOMPLETO')

    print('\n[10] A loja escolhe o depósito, e o pedido é de uma loja só')
    for loja, esperado_dep in [('1', 'Geral'), ('2', 'Loja Física Aldeota'), ('3', 'Bancada Desk Tech')]:
        pg.click('#inputLoja .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#inputLoja .dropdown-select-item[data-value="%s"]' % loja); pg.wait_for_timeout(250)
        dep = pg.inner_text('#inputDeposito .dropdown-select-label')
        ok(dep == esperado_dep, 'loja %s → depósito padrão "%s"' % (loja, dep))

    print('\n[11] Os dois níveis de desconto, cada um na sua base')
    abre(DET)
    pg.click('#btnEditarRegistro'); pg.wait_for_timeout(200)
    base = pg.evaluate("ITENS.reduce((s,i) => s + i.precoLista * (1 - (i.desconto||0)/100) * i.qtd, 0)")
    mostrado = pg.evaluate("paraNumero(document.getElementById('totProdutos').textContent)")
    ok(abs(base - mostrado) < 0.02, 'Total produtos já vem com o desconto DO ITEM: %.2f' % mostrado)
    pg.fill('#inputDesconto', '10%'); pg.wait_for_timeout(300)
    venda = pg.evaluate("paraNumero(document.getElementById('totGeral').textContent)")
    ok(abs(venda - mostrado * 0.9) < 0.02, 'o desconto do PEDIDO incide sobre esse total: %.2f' % venda)
    pg.fill('#inputDesconto', '100,00'); pg.wait_for_timeout(300)
    venda2 = pg.evaluate("paraNumero(document.getElementById('totGeral').textContent)")
    ok(abs(venda2 - (mostrado - 100)) < 0.02, 'desconto em valor também vale: %.2f' % venda2)

    print('\n[12] Painel do item: preço de lista → desconto → preço unitário')
    pg.click('#corpoItens tr:nth-child(1) [data-editar]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#eventDrawer', 'e => e.classList.contains("open")'), 'o painel do item abre')
    pg.fill('#itLista', '1000,00'); pg.fill('#itDesc', '25'); pg.fill('#itQtd', '2'); pg.wait_for_timeout(250)
    ok(pg.input_value('#itUnit') == '750,00', 'preço unitário = lista − desconto do item: ' + pg.input_value('#itUnit'))
    ok(pg.input_value('#itTotal') == '1.500,00', 'preço total = unitário × qtde: ' + pg.input_value('#itTotal'))
    pg.click('#btnSalvarItem'); pg.wait_for_timeout(350)
    ok(pg.evaluate("ITENS[0].desconto") == 25, 'o desconto do item ficou gravado na linha')

    print('\n[13] Pedido não nasce sem saldo — e a mensagem diz quanto existe')
    abre(DET)
    pg.click('#btnEditarRegistro'); pg.wait_for_timeout(200)
    ok(pg.eval_on_selector_all('#corpoItens .item-saldo', 'e => e.length') > 0, 'cada item mostra o saldo disponível')
    pg.evaluate("ITENS[0].qtd = 9999; renderItens();"); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector_all('#corpoItens tr.linha-sem-saldo', 'e => e.length') == 1, 'a linha sem saldo fica marcada')
    ok(pg.eval_on_selector('#erroSaldo', 'e => e.classList.contains("show")'), 'o erro de saldo aparece sozinho')
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    txt = pg.inner_text('#confirmModalTexto')
    ok('não pode ser salvo' in txt, 'salvar é bloqueado')
    ok('disponível' in txt and '9999' in txt.replace('.', ''), 'a mensagem diz o pedido e o disponível: "%s"' % txt[:90])
    # 9999 notebooks estouram o saldo E o limite de credito ao mesmo tempo. Com
    # um `avisar` por motivo, o segundo apagava o primeiro e o usuario consertava
    # a coisa errada. Os dois motivos tem de caber na MESMA mensagem.
    ok('(1)' in txt and '(2)' in txt, 'os dois bloqueios aparecem juntos, numerados')
    ok('limite de crédito' in txt, 'e o segundo motivo não some: ' + txt[-110:])
    fecha_modal()
    # Esta seção é sobre SALDO. A trava por conta em atraso (02/out) é outra
    # regra e tem seção própria no teste_receber — aqui ela sai do caminho.
    pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0;")
    pg.evaluate("ITENS[0].qtd = 1; renderItens();"); pg.wait_for_timeout(250)
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    txt2 = pg.inner_text('#confirmModalTexto')
    ok('reserva' in txt2 and 'conta a receber' in txt2, 'salvar anuncia a reserva e a conta a receber: "%s"' % txt2[:90])
    fecha_modal()

    print('\n[14] Comissão: a regra é do vendedor, a tela só aplica')
    abre(DET)
    pg.click('.tab-item[data-tab="comissoes"]'); pg.wait_for_timeout(250)
    resumo = pg.inner_text('#resumoComissao')
    ok('Marina Costa' in resumo, 'mostra o vendedor do pedido')
    ok('faturamento' in pg.inner_text('#hintComissao'), 'diz que a liberação é no faturamento')
    pg.click('.tab-item[data-tab="impostos"]'); pg.wait_for_timeout(200)
    desab = pg.eval_on_selector_all('#tab-impostos input', 'e => e.every(x => x.disabled)')
    ok(desab, 'os campos fiscais nascem visíveis e DESABILITADOS (§11)')

    print('\n[15] As duas telas se acham')
    abre(LISTA)
    pg.click('#btnNovoPedido'); pg.wait_for_timeout(400)
    ok(pg.url.endswith(DET + '?novo=1'), 'Incluir pedido abre a página do pedido novo')
    abre(LISTA)
    pg.click('#corpoTabela tr:nth-child(1)'); pg.wait_for_timeout(350)
    pg.click('#btnAbrirPedido'); pg.wait_for_timeout(400)
    ok(DET in pg.url and '?id=' in pg.url, 'o preview abre o pedido completo: ' + pg.url.split('/')[-1])
    abre(DET)
    pg.click('#btnEditarRegistro'); pg.wait_for_timeout(200)
    # O rodape foi unificado em 08/out (design system §11.3): o "Cancelar" que
    # so navegava virou um link que DIZ para onde vai. Sem alteracao pendente
    # ele sai direto, que e o caminho medido aqui.
    pg.click('#btnVoltarRodape'); pg.wait_for_timeout(400)
    ok(pg.url.endswith(LISTA), 'sem pendencia, o link do rodape volta direto para a listagem')

    # =======================================================================
    # Daqui para baixo: a barganha de 02/out. O pedido ANDA, o cliente tem
    # historico e limite, e clonar abre pedido pronto em vez de prometer.
    # =======================================================================

    print('\n[16] O funil anda um passo por vez, na ordem certa')
    abre(DET)
    ok(pg.eval_on_selector('#btnProximoPasso', 'e => e.offsetParent !== null'), 'pedido em aberto oferece o próximo passo')
    ok(pg.inner_text('#btnProximoPassoRotulo') == 'Aprovar pagamento',
       'o rótulo é o EFEITO, não o nome da situação: ' + pg.inner_text('#btnProximoPassoRotulo'))
    esperado = ['Aprovar pagamento', 'Enviar para separação', 'Enviar para conferência de saída', 'Faturar',
                'Marcar pronto para envio', 'Confirmar envio', 'Marcar entregue']
    andou = []
    for _ in range(9):
        if not pg.eval_on_selector('#btnProximoPasso', 'e => e.offsetParent !== null'): break
        andou.append(pg.inner_text('#btnProximoPassoRotulo'))
        pg.click('#btnProximoPasso'); pg.wait_for_timeout(220)
        texto_passo = pg.inner_text('#confirmModalTexto')
        if andou[-1] == 'Confirmar envio':
            ok('BAIXA FÍSICA' in texto_passo, 'o passo do envio avisa que é a baixa física: "%s"' % texto_passo[:70])
        if andou[-1] == 'Faturar':
            ok('COMISSÃO' in texto_passo.upper(), 'faturar avisa que libera a comissão')
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(220)
        fecha_modal()
    ok(andou == esperado, 'o funil inteiro, na ordem: %s' % ' → '.join(andou))
    ok(pg.inner_text('#badgeSituacao').strip().upper() == 'ENTREGUE', 'termina em Entregue')
    ok(not pg.eval_on_selector('#btnProximoPasso', 'e => e.offsetParent !== null'),
       'situação terminal não oferece passo nenhum')
    ok(pg.evaluate("JSON.parse(localStorage.getItem('deskLog')||'[]').filter(l=>l.chave==='pedidosPasso').length") >= 7,
       'cada passo entrou no registro de atividades')
    # Andar no funil e operacao normal: confirma, mas NAO pede senha.
    abre(DET)
    pg.click('#btnProximoPasso'); pg.wait_for_timeout(250)
    ok(not pg.eval_on_selector('#campoSenhaModal', 'e => e.classList.contains("on")'),
       'avançar um passo NÃO pede senha — é operação normal')
    fecha_modal()

    print('\n[17] Alterar situação à mão é correção, e correção pede senha')
    abre(DET)
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#linkAlterarSituacao'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#painelDrawer', 'e => e.classList.contains("open")'), 'o painel de situação abre')
    ok(pg.eval_on_selector_all('#painelCorpo .sit-opcao', 'e => e.length') == 9,
       'as 9 situações estão lá — devolução saiu, é documento do módulo próprio')
    ok(pg.eval_on_selector_all('#painelCorpo .sit-opcao[data-sit="devolucao"]', 'e => e.length') == 0,
       'e não dá para marcar um pedido como devolvido por aqui')
    ordem = pg.eval_on_selector_all('#painelCorpo .sit-opcao', 'e => e.map(x => x.getAttribute("data-sit")).join(",")')
    ok(ordem.startswith('aberto,aprovado,separacao,conferenciasaida,faturado'),
       'na ordem do funil, não em ordem alfabética: ' + ordem[:46])
    ok(pg.eval_on_selector_all('#painelCorpo .sit-opcao.atual', 'e => e.length') == 1, 'a situação atual fica marcada e inerte')
    pg.click('#painelCorpo .sit-opcao[data-sit="enviado"]'); pg.wait_for_timeout(350)
    t = pg.inner_text('#confirmModalTexto')
    ok('BAIXA FÍSICA' in t, 'pular para Enviado avisa que dá baixa física sem passar pelo funil')
    ok(pg.eval_on_selector('#campoSenhaModal', 'e => e.classList.contains("on")'), 'correção manual PEDE senha')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
    ok(pg.inner_text('#badgeSituacao').strip().upper() == 'EM ABERTO', 'sem senha não altera')
    pg.fill('#inputSenhaModal', '1234'); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#badgeSituacao').strip().upper() == 'ENVIADO', 'com senha altera')
    fecha_modal()
    ok(pg.evaluate("JSON.parse(localStorage.getItem('deskLog')||'[]').some(l=>l.chave==='pedidosSituacao')"),
       'a correção entrou no registro de atividades')
    # Voltar de Enviado nao desfaz a saida do estoque — a tela tem de dizer isso.
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#linkAlterarSituacao'); pg.wait_for_timeout(300)
    pg.click('#painelCorpo .sit-opcao[data-sit="separacao"]'); pg.wait_for_timeout(300)
    ok('NÃO devolve o estoque' in pg.inner_text('#confirmModalTexto'),
       'voltar de Enviado avisa que o estoque não volta sozinho')
    fecha_modal()

    print('\n[18] Clonar venda abre o pedido pronto, não uma promessa')
    abre(DET)
    antes = pg.evaluate("ITENS.map(i => i.sku + ':' + i.qtd + ':' + i.desconto).join(',')")
    cliente_antes = pg.input_value('#inputCliente')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#linkClonarVenda'); pg.wait_for_timeout(300)
    ok('Clonar este pedido?' in pg.inner_text('#confirmModalTexto'), 'clonar confirma antes')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(600)
    ok('?clonar=' in pg.url, 'vai para o pedido clonado: ' + pg.url.split('/')[-1])
    ok(pg.evaluate("ITENS.map(i => i.sku + ':' + i.qtd + ':' + i.desconto).join(',')") == antes,
       'itens, quantidades e descontos vieram todos')
    ok(pg.input_value('#inputCliente') == cliente_antes, 'o cliente veio junto')
    ok(pg.input_value('#inputDesconto') == '10%', 'o desconto do pedido veio junto')
    ok(pg.input_value('#inputNumero') == '', 'número em branco — é gerado ao salvar')
    ok(pg.input_value('#inputDataVenda') == pg.evaluate("brDe(HOJE)"), 'a data é a de HOJE — copia a venda, não a data')
    ok(pg.inner_text('#badgeSituacao').strip().upper() == 'EM ABERTO', 'nasce Em aberto')
    ok(not pg.evaluate("document.body.classList.contains('modo-leitura')"), 'abre em edição, pronto para ajustar')
    ok(not pg.eval_on_selector('#btnProximoPasso', 'e => e.offsetParent !== null'),
       'pedido que ainda não existe não anda no funil')

    print('\n[19] Últimas vendas do cliente, sem sair do pedido')
    abre(DET)
    pg.click('#linkUltimasVendas'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#painelDrawer', 'e => e.classList.contains("open")'), 'o painel abre')
    ok(pg.url.endswith(DET), 'continua no pedido — não navegou para a listagem')
    n = pg.eval_on_selector_all('#painelCorpo tr[data-pedido]', 'e => e.length')
    ok(0 < n <= 10, '%d vendas listadas, no máximo 10' % n)
    ok('10 últimos' in pg.inner_text('#painelCorpo'), 'a tela diz que mostra só os 10 últimos')
    # O painel do item ja abriu escondido uma vez neste projeto: aqui a assercao
    # e a do dedo do usuario, nao a do querySelector.
    ok(pg.evaluate("""() => {
        const td = document.querySelector('#painelCorpo tr[data-pedido] td');
        const b = td.getBoundingClientRect();
        const a = document.elementFromPoint(b.left + b.width / 2, b.top + b.height / 2);
        return !!(a && td.contains(a));
      }"""), 'o painel aparece de verdade — não só no DOM')
    pg.click('.painel-aba[data-aba="financeiro"]'); pg.wait_for_timeout(250)
    ok('Total em aberto' in pg.inner_text('#painelCorpo'), 'a aba Financeiro mostra o que o cliente deve')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(not pg.eval_on_selector('#painelDrawer', 'e => e.classList.contains("open")'), 'Esc fecha o painel')

    print('\n[20] Limite de crédito: o painel conta, e a forma de recebimento decide se trava')
    abre(DET)
    pg.click('#linkLimiteCredito'); pg.wait_for_timeout(400)
    txt = pg.inner_text('#painelCorpo')
    for rotulo in ['Limite de crédito', 'Usado', 'Disponível real', 'Este pedido']:
        ok(rotulo in txt, 'o painel mostra "%s"' % rotulo)
    ok('Boleto valida o limite' in txt, 'o painel diz se a forma de recebimento valida: boleto valida')
    bate = pg.evaluate("Math.abs((CLIENTE_FINANCEIRO.limite - usadoDoCliente()) - disponivelDoCliente()) < 0.01")
    ok(bate, 'disponível = limite − usado, sem número solto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    abre(DET + '?editar=1')
    # Idem: esta seção é sobre LIMITE DE CRÉDITO, não sobre conta em atraso.
    pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0;")
    pg.evaluate("ITENS[0].qtd = 4; renderItens();"); pg.wait_for_timeout(300)
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    t = pg.inner_text('#confirmModalTexto')
    ok('não pode ser salvo' in t and 'limite de crédito' in t, 'estourando em boleto, NÃO salva')
    ok('Limite R$' in t and 'disponível' in t, 'a mensagem diz os números, não só que estourou: "%s"' % t[60:150])
    ok(pg.eval_on_selector('#erroCredito', 'e => e.classList.contains("show")'), 'o campo da forma de recebimento marca o erro')
    fecha_modal()
    # Mesma venda, forma a vista: passa. A trava e da forma, nao do cliente.
    pg.evaluate("""(function(){ var d = document.getElementById('inputRecebimento');
      d.setAttribute('data-value','pix'); d.querySelector('.dropdown-select-label').textContent='Pix'; })()""")
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    ok('ficou reservado' in pg.inner_text('#confirmModalTexto'), 'a MESMA venda em Pix passa — Pix não valida limite')
    ok(not pg.eval_on_selector('#erroCredito', 'e => e.classList.contains("show")'), 'e o erro de crédito saiu da tela')
    fecha_modal()

    print('\n[21] Nenhuma ação do menu continua sendo promessa vazia')
    abre(DET)
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(250)
    itens_menu = pg.eval_on_selector_all('#menuMaisAcoes .dropdown-select-item',
                                         'e => e.map(x => x.textContent.trim())')
    ok('Enviar para separação' not in itens_menu,
       'o item que só avisava saiu do menu — virou o botão do funil')
    ok('Clonar venda' in itens_menu and 'Alterar situação' in itens_menu, 'os dois que viraram ação continuam no menu')
    # Sobraram dois avisos, e os dois sao sobre MODULO que nao existe (fiscal,
    # relatorios) — nao sobre tela que existe e nao foi ligada.
    restantes = pg.eval_on_selector_all('#menuMaisAcoes .dropdown-select-item[data-acao]',
                                        'e => e.map(x => x.getAttribute("data-acao"))')
    ok(sorted(restantes) == ['imprimir', 'nota'],
       'os únicos avisos restantes são de módulo inexistente: %s' % sorted(restantes))

    print('\n[22] Nos dois temas, sem estouro')
    for tema in ['dark', 'light']:
        for arq in [LISTA, DET]:
            abre(arq)
            if tema == 'light':
                pg.evaluate("document.body.classList.remove('dark')"); pg.wait_for_timeout(250)
            ok(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
               '%s no tema %s: sem rolagem horizontal' % (arq[7:-5], tema))
            ok(not erros, '%s no tema %s: sem erro de JS' % (arq[7:-5], tema))

    b.close()

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
