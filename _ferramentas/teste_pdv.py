# -*- coding: utf-8 -*-
# Vendas → PDV e Configurações → Configurações do PDV. Nasceram em 09/out/2026.
#
# O PDV e a tela de venda de balcao: turno de caixa por loja, venda com varias
# formas de recebimento, sangria, reforco e fechamento com conferencia cega.
# Tres decisoes do usuario estao guardadas aqui: a venda vira Pedido de Venda ja
# entregue, a loja e escolhida na abertura do caixa, e o ciclo entra inteiro.
#
# O que a suite guarda:
#   [1]   caixa fechado nao vende; o item de menu e o cartao do hub tem destino;
#   [2]   abrir o caixa: loja, troco, e o turno sobrevive ao F5;
#   [3]   produto so da loja do turno; leitor; quantidade segue a unidade;
#         bloqueio de estoque com os numeros; iguais agrupam;
#   [4]   editar item: desconto dentro do limite passa, acima pede senha;
#   [5]   vendedor da loja, cliente por nome ou documento, cadastro rapido;
#   [6]   finalizar: as formas vem do cadastro, troco, parcelas, titulo pede
#         cliente, limite de credito com os numeros;
#   [7]   concluir: o que a venda gerou, a baixa de estoque, os recibos;
#   [8]   turno: sangria com senha e limite, reforco, fechamento CEGO, diferenca
#         que so fecha com senha;
#   [9]   ESPELHOS: tudo que o PDV le de outro cadastro bate com o cadastro;
#   [10]  parametros: os nove nascem nas duas telas, e o PDV obedece;
#   [11]  as acoes estao no catalogo de senhas;
#   [12]  atalhos, os dois temas e erro de JS.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

TELA = 'pagina-vendas-pdv.html'
CFG = 'pagina-configuracoes-pdv.html'
HUB = 'pagina-configuracoes.html'
FORMAS_CAD = 'pagina-configuracoes-formas-recebimento.html'
PEDIDO = 'pagina-vendas-pedidos-detalhe.html'
METAS = 'pagina-vendas-metas.html'
CLIENTES_CAD = 'pagina-cadastros-clientes.html'
CONTAS_CAD = 'pagina-configuracoes-contas-financeiras.html'
CATEG_CAD = 'pagina-configuracoes-categorias-financeiras.html'
CATALOGOS = ['pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html',
             'pagina-cadastros-vendedores-detalhe.html']
CHAVES = ['pdvSituacaoVenda', 'pdvVendedorObrigatorio', 'pdvClienteObrigatorio', 'pdvBloqueiaSemEstoque',
          'pdvBloqueiaAlterarPreco', 'pdvDescontoMaximoPct', 'pdvAgrupaIguais', 'pdvAbreComUltimoFechamento', 'pdvFechamentoCego']

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
    clic(pg, '#' + raiz + ' .dropdown-select-btn')
    pg.wait_for_timeout(120)
    pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
    pg.wait_for_timeout(220)


def confirmar(pg, senha=True):
    if pg.locator('#confirmModal.open').count():
        if senha and visivel(pg, '#campoSenhaModal'):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(400)


def fechar_aviso(pg):
    if pg.locator('#confirmModal.open').count():
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(300)


def zerar(pg, param=None):
    """Comeca do zero: sem turno guardado e com os parametros pedidos."""
    pg.goto(localiza.http(TELA)); pg.wait_for_load_state('load')
    pg.evaluate("(p) => { localStorage.removeItem('deskPdv'); if (p) localStorage.setItem('deskParametros', JSON.stringify(p)); else localStorage.removeItem('deskParametros'); }", param)
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)


def abrir_caixa(pg, loja=1, troco='150'):
    clic(pg, '#btnAbrirCaixa'); pg.wait_for_timeout(300)
    escolher(pg, 'abrirLoja', loja)
    pg.fill('#abrirTroco', troco)
    clic(pg, '#btnConfirmarAbertura'); pg.wait_for_timeout(400)


def adicionar(pg, codigo, qtd='1'):
    """Passa o codigo no 'leitor': quantidade, codigo exato e Enter."""
    pg.fill('#qtdProduto', qtd)
    pg.fill('#buscaProduto', codigo)
    pg.locator('#buscaProduto').press('Enter')
    pg.wait_for_timeout(250)


def cliente(pg, texto):
    clic(pg, '#btnCliente' if pg.evaluate('momento') == 'venda' else '#btnClienteFin'); pg.wait_for_timeout(300)
    pg.fill('#buscaCliente', texto); pg.wait_for_timeout(200)
    clic(pg, '#listaClientes .pdv-cli'); pg.wait_for_timeout(300)


def receber(pg, chave, valor=None, i=None):
    escolher(pg, 'selAddReceb', chave)
    if valor is not None:
        n = pg.evaluate("venda.recebimentos.length") - 1 if i is None else i
        pg.fill('[data-receb-valor="%d"]' % n, valor)
        pg.locator('[data-receb-valor="%d"]' % n).blur()
        pg.wait_for_timeout(250)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    # Contexto explicito: as duas abas da suite precisam dividir o armazenamento,
    # e nav.new_page() abre um contexto novo (e isolado) a cada chamada.
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    # Impressao em teste: conta as chamadas em vez de abrir a caixa de dialogo.
    pg.add_init_script("window.print = function () { window.__imprimiu = (window.__imprimiu || 0) + 1; };")
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('\n[1] Caixa fechado nao vende, e a tela tem porta')
    zerar(pg)
    ok(pg.evaluate('momento') == 'fechado', 'sem turno, a tela abre com o caixa fechado')
    ok(visivel(pg, '#estadoFechado') and not visivel(pg, '#estadoVenda'), 'so o momento "fechado" aparece')
    ok(not visivel(pg, '#pdvAcoesTopo'), 'sem turno nao ha detalhes do caixa nem mais acoes')
    ok(len(pg.inner_text('#relogioFechado')) == 5 and len(pg.inner_text('#dataFechado')) > 10, 'o relogio e a data aparecem')
    bc = pg.inner_text('#breadcrumb').lower()
    ok('vendas' in bc and 'pdv' in bc, 'o caminho diz Vendas > PDV')
    href = pg.get_attribute('.flyout-item[data-label="PDV"]', 'data-href')
    ok(localiza.nome(href) == TELA, 'o item PDV do menu de Vendas leva a esta tela: %s' % href)
    sem = [n for n in localiza.nomes() if 'data-label="PDV">' in open(localiza.onde(n), encoding='utf-8').read()]
    ok(not sem, 'e leva em todas as telas: %s' % sem[:3])
    hub = open(localiza.onde(HUB), encoding='utf-8').read()
    ok(("href:'../configuracoes/" + CFG + "'") in hub, 'o hub tem o cartao de Configuracoes do PDV com destino')

    print('\n[2] Abrir o caixa: loja, troco, e o turno sobrevive ao F5')
    clic(pg, '#btnAbrirCaixa'); pg.wait_for_timeout(300)
    ok(pg.locator('#abrirDrawer.open').count() == 1, 'o botao abre o painel de abertura')
    escolher(pg, 'abrirLoja', 2)
    ok('Loja Física Aldeota' in pg.inner_text('#hintAbrirLoja') and 'Desk Brands' in pg.inner_text('#hintAbrirLoja'),
       'escolher a loja diz o deposito e de quem sao os produtos: %s' % pg.inner_text('#hintAbrirLoja'))
    pg.fill('#abrirTroco', 'abc')
    clic(pg, '#btnConfirmarAbertura'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroTroco') and pg.evaluate('turno') is None, 'troco que nao e numero nao abre o caixa')
    escolher(pg, 'abrirLoja', 1)
    pg.fill('#abrirTroco', '150,00')
    clic(pg, '#btnConfirmarAbertura'); pg.wait_for_timeout(400)
    ok(pg.evaluate('momento') == 'venda' and pg.evaluate('turno.trocoInicial') == 150, 'com troco valido o caixa abre e vai para a venda')
    chip = pg.inner_text('#chipTurno')
    ok('Desk Shope' in chip and 'caixa aberto' in chip and 'Administrador Desk' in chip, 'o topo diz loja, hora e operador: %s' % chip)
    ok(pg.evaluate("venda.depositoId") == 1, 'a venda nasce no deposito padrao da loja')
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.evaluate('momento') == 'venda' and pg.evaluate('turno && turno.lojaId') == 1, 'depois do F5 o caixa continua aberto')

    print('\n[3] Produto: so da loja, leitor, unidade e estoque')
    pg.fill('#buscaProduto', 'notebook'); pg.wait_for_timeout(250)
    ok(pg.locator('#sugestoes .pdv-sug').count() == 0 and 'outra loja' in pg.inner_text('#sugestoes'),
       'produto de outra loja nao aparece, e a tela diz por que')
    pg.fill('#buscaProduto', 'fone'); pg.wait_for_timeout(250)
    ok(pg.locator('#sugestoes .pdv-sug').count() == 1 and 'saldo 34' in pg.inner_text('#sugestoes'), 'a busca por descricao acha, com preco e saldo')
    pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#prodSelecionado') and pg.inner_text('#prodSku') == 'FON-BT-200', 'Enter escolhe a sugestao e mostra o produto')
    ok('Geral' in pg.inner_text('#prodRotuloEstoque') and '34' in pg.inner_text('#prodEstoque'), 'com o disponivel no deposito da venda')
    pg.fill('#qtdProduto', '1,5'); pg.locator('#qtdProduto').press('Enter'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroProduto') and 'inteira' in pg.inner_text('#erroProduto') and pg.evaluate('venda.itens.length') == 0,
       'quantidade quebrada de produto vendido por UN e barrada')
    pg.fill('#qtdProduto', '40'); pg.locator('#qtdProduto').press('Enter'); pg.wait_for_timeout(250)
    msg = pg.inner_text('#erroProduto')
    ok('disponível 34' in msg and 'pedido 40' in msg and pg.evaluate('venda.itens.length') == 0, 'vender alem do saldo e barrado, com os numeros: %s' % msg)
    pg.fill('#qtdProduto', '2'); pg.locator('#qtdProduto').press('Enter'); pg.wait_for_timeout(250)
    ok(pg.evaluate('venda.itens.length') == 1 and pg.evaluate('venda.itens[0].qtd') == 2, 'quantidade valida adiciona')
    ok(pg.input_value('#buscaProduto') == '' and pg.input_value('#qtdProduto') == '1' and not visivel(pg, '#prodSelecionado'), 'e a busca volta limpa para o proximo')
    adicionar(pg, '7891000100011', '1')
    ok(pg.evaluate('venda.itens.length') == 1 and pg.evaluate('venda.itens[0].qtd') == 3, 'o mesmo produto pelo GTIN, no leitor, soma na linha que ja existe')
    adicionar(pg, 'car-33w-01', '1')
    ok(pg.evaluate('venda.itens.length') == 2, 'codigo exato em minusculas tambem entra direto')
    ok(pg.inner_text('#totItens') == '2' and pg.inner_text('#totQtd') == '4' and pg.inner_text('#totVenda') == 'R$ 847,25',
       'o rodape soma itens, quantidade e total: %s / %s / %s' % (pg.inner_text('#totItens'), pg.inner_text('#totQtd'), pg.inner_text('#totVenda')))
    adicionar(pg, 'FON-BT-200', '32')
    ok('disponível 31' in pg.inner_text('#erroProduto'), 'o saldo desconta o que ja esta na venda: %s' % pg.inner_text('#erroProduto'))
    clic(pg, '#btnLimparProduto'); pg.wait_for_timeout(200)

    print('\n[4] Editar item: desconto dentro do limite passa, acima pede senha')
    clic(pg, '#listaItens tbody tr'); pg.wait_for_timeout(350)
    ok(pg.locator('#itemDrawer.open').count() == 1 and 'Fone' in pg.inner_text('#itemNome'), 'clicar no item abre o painel dele')
    ok(pg.evaluate("document.getElementById('itemPreco').disabled") is False, 'o preco pode ser mudado (parametro desligado)')
    escolher(pg, 'itemAjusteTipo', 'desconto')
    ok(visivel(pg, '#blocoItemAjuste'), 'escolher desconto mostra os campos do ajuste')
    escolher(pg, 'itemAjusteModo', 'pct')
    pg.fill('#itemAjusteValor', '10'); pg.wait_for_timeout(200)
    ok(pg.inner_text('#itemTotal') == 'R$ 674,73' and not visivel(pg, '#itemNota'), 'a previa mostra o total com 10%% (no limite, sem aviso): %s' % pg.inner_text('#itemTotal'))
    clic(pg, '#btnAplicarItem'); pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 0 and pg.evaluate('venda.itens[0].ajusteValor') == 10, 'desconto no limite aplica sem senha')
    ok('desconto de' in pg.inner_text('#listaItens').lower(), 'e a linha do item mostra o desconto')
    clic(pg, '#listaItens tbody tr'); pg.wait_for_timeout(350)
    pg.fill('#itemAjusteValor', '25'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#itemNota') and 'gerente' in pg.inner_text('#itemNota'), 'acima do maximo, o painel avisa antes de aplicar')
    clic(pg, '#btnAplicarItem'); pg.wait_for_timeout(400)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal'), 'e aplicar pede a senha de quem libera')
    ok(pg.evaluate('venda.itens[0].ajusteValor') == 10, 'antes da senha, o desconto continua o antigo')
    confirmar(pg)
    ok(pg.evaluate('venda.itens[0].ajusteValor') == 25, 'com a senha, o desconto de 25% entra')
    clic(pg, '#listaItens tbody tr'); pg.wait_for_timeout(350)
    pg.fill('#itemQtd', '0'); clic(pg, '#btnAplicarItem'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroItem'), 'quantidade zero no painel e barrada')
    pg.fill('#itemQtd', '3'); escolher(pg, 'itemAjusteTipo', 'nenhum'); clic(pg, '#btnAplicarItem'); pg.wait_for_timeout(350)
    ok(pg.evaluate('venda.itens[0].ajusteTipo') == 'nenhum' and pg.inner_text('#totVenda') == 'R$ 847,25', 'tirar o ajuste devolve o total')
    clic(pg, '[data-remover="1"]'); pg.wait_for_timeout(250)
    ok(pg.evaluate('venda.itens.length') == 1, 'o X da linha remove o item')

    print('\n[5] Vendedor da loja, cliente e cadastro rapido')
    vend = pg.evaluate("Array.from(document.querySelectorAll('#menuVendedor .dropdown-select-item')).map(e => e.textContent)")
    ok(vend == ['Sem vendedor', 'Marina Costa', 'Bianca Furtado', 'Ponto Parceiro Vila Mariana'],
       'o vendedor e da loja do turno ou sem loja, e inativo nao aparece: %s' % vend)
    escolher(pg, 'selVendedor', 6)
    ok(pg.evaluate('venda.vendedorId') == 6, 'escolher o vendedor grava na venda')
    clic(pg, '#btnCliente'); pg.wait_for_timeout(300)
    ok(pg.locator('#clienteDrawer.open').count() == 1 and pg.locator('#listaClientes .pdv-cli').count() == 6, 'o painel lista os clientes')
    pg.fill('#buscaCliente', '41223556'); pg.wait_for_timeout(200)
    ok(pg.locator('#listaClientes .pdv-cli').count() == 1 and 'Nordeste' in pg.inner_text('#listaClientes'), 'a busca acha pelo CNPJ, com ou sem pontuacao')
    clic(pg, '#btnNovoCliente'); pg.wait_for_timeout(200)
    pg.fill('#novoCliNome', 'Cliente de Balcão'); pg.fill('#novoCliDoc', '123')
    clic(pg, '#btnSalvarCliente'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#erroNovoCli') and '11' in pg.inner_text('#erroNovoCli'), 'cadastro rapido barra CPF com numero errado de digitos')
    pg.fill('#novoCliDoc', '123.456.789-00')
    clic(pg, '#btnSalvarCliente'); pg.wait_for_timeout(200)
    ok('Já existe' in pg.inner_text('#erroNovoCli'), 'e barra documento que ja tem cadastro')
    pg.fill('#novoCliDoc', '987.654.321-00'); pg.fill('#novoCliFone', '(99) 99999-0000')
    clic(pg, '#btnSalvarCliente'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#rotuloCliente') == 'Cliente de Balcão' and pg.locator('#clienteDrawer.open').count() == 0, 'documento valido cadastra e ja usa na venda')
    cliente(pg, 'nordeste')
    ok(pg.inner_text('#rotuloCliente') == 'Distribuidora Nordeste Ltda' and '41.223.556' in pg.inner_text('#hintCliente'), 'trocar o cliente mostra nome e documento')

    print('\n[6] Finalizar: formas do cadastro, troco, parcelas, titulo e limite')
    clic(pg, '#btnContinuar'); pg.wait_for_timeout(400)
    ok(pg.evaluate('momento') == 'finalizar' and visivel(pg, '#estadoFinalizar'), 'Continuar leva para a finalizacao')
    ok(pg.inner_text('#finTotal') == 'R$ 749,70' and 'Bianca Furtado' in pg.input_value('#finVendedor'), 'com o total e o vendedor da venda')
    ok('entregue' in pg.inner_text('#hintFinDeposito') and 'Geral' in pg.inner_text('#hintFinDeposito'), 'e diz de onde sai o estoque e como a venda entra em Pedidos')
    formas = pg.evaluate("Array.from(document.querySelectorAll('#menuAddReceb .dropdown-select-item')).map(e => e.getAttribute('data-value'))")
    ok(formas == ['dinheiro', 'pix', 'debito', 'credito', 'boleto', 'crediario', 'cheque', 'deposito'],
       'as formas oferecidas sao as habilitadas que valem para receber: %s' % formas)
    clic(pg, '#btnFinalizar'); pg.wait_for_timeout(350)
    ok(pg.evaluate('momento') == 'finalizar' and 'recebimento' in pg.inner_text('#confirmModalTexto'), 'sem recebimento nao finaliza')
    fechar_aviso(pg)
    receber(pg, 'dinheiro', '300')
    ok('Falta receber R$ 449,70' in pg.inner_text('#faltaReceber'), 'recebimento parcial diz quanto falta: %s' % pg.inner_text('#faltaReceber')[:60])
    pg.fill('[data-receb-recebido="0"]', '250'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
    ok('recebido' in pg.inner_text('#faltaReceber') and 'menor' in pg.inner_text('#faltaReceber'), 'dinheiro recebido menor que o valor e barrado')
    pg.fill('[data-receb-recebido="0"]', '350'); pg.locator('[data-receb-recebido="0"]').blur(); pg.wait_for_timeout(250)
    ok(pg.inner_text('#totTroco') == 'R$ 50,00', 'recebido maior vira troco: %s' % pg.inner_text('#totTroco'))
    receber(pg, 'credito')
    ok(pg.evaluate('venda.recebimentos[1].valor') == 449.7, 'a segunda forma ja vem com o que falta')
    ok('Taxa de R$ 15,69' in pg.inner_text('#listaReceb') and 'Líquido' in pg.inner_text('#listaReceb'), 'cartao mostra a taxa do cadastro e o liquido')
    ok('limite de crédito' in pg.inner_text('#listaReceb'), 'e avisa que a forma confere o limite')
    pg.fill('[data-receb-expr="1"]', '3x'); pg.locator('[data-receb-expr="1"]').blur(); pg.wait_for_timeout(250)
    parc = pg.evaluate('venda.recebimentos[1].parcelas')
    ok([x['dias'] for x in parc] == [30, 60, 90] and round(sum(x['valor'] for x in parc), 2) == 449.7,
       '"3x" gera tres parcelas de 30 em 30 que somam o valor: %s' % parc)
    pg.fill('[data-receb-expr="1"]', '15 45'); pg.locator('[data-receb-expr="1"]').blur(); pg.wait_for_timeout(250)
    ok([x['dias'] for x in pg.evaluate('venda.recebimentos[1].parcelas')] == [15, 45], '"15 45" gera as parcelas nos dias pedidos')
    pg.fill('[data-parc-valor="1:0"]', '100'); pg.locator('[data-parc-valor="1:0"]').blur(); pg.wait_for_timeout(250)
    ok('as parcelas somam' in pg.inner_text('#faltaReceber'), 'parcela mexida a mao que nao fecha a soma e barrada, com os numeros')
    pg.fill('[data-receb-expr="1"]', '2x'); pg.locator('[data-receb-expr="1"]').blur(); pg.wait_for_timeout(250)
    ok('Pode finalizar' in pg.inner_text('#faltaReceber'), 'com tudo fechando, a tela diz que pode finalizar')
    clic(pg, '#btnClienteFin'); pg.wait_for_timeout(300); clic(pg, '#btnConsumidorFinal'); pg.wait_for_timeout(300)
    ok('precisa de cliente identificado' in pg.inner_text('#faltaReceber'), 'venda a prazo para consumidor final e barrada: titulo precisa de devedor')
    cliente(pg, 'rafael nog')
    f = pg.inner_text('#faltaReceber')
    ok('limite R$ 1.500,00' in f and 'já usado R$ 1.480,00' in f and 'disponível R$ 20,00' in f and 'R$ 449,70' in f,
       'cliente sem limite e barrado com os quatro numeros: %s' % f[:170])
    cliente(pg, 'nordeste')
    pg.fill('#finDesconto', '200%'); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroFinDesconto') and 'desconto' in pg.inner_text('#faltaReceber').lower(), 'desconto maior que a venda e barrado')
    pg.fill('#finDesconto', ''); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
    escolher(pg, 'finDeposito', 3)
    ok('Sem saldo em Loja Física Aldeota' in pg.inner_text('#faltaReceber'), 'trocar o deposito para um sem saldo barra a venda, com os numeros')
    escolher(pg, 'finDeposito', 1)
    ok('Pode finalizar' in pg.inner_text('#faltaReceber'), 'voltar ao deposito com saldo libera de novo')

    print('\n[7] Concluir: o que a venda gerou, a baixa e os recibos')
    clic(pg, '#btnFinalizar'); pg.wait_for_timeout(450)
    ok(pg.evaluate('momento') == 'concluida' and pg.inner_text('#concTitulo') == 'Venda nº 1 finalizada', 'a venda finaliza e ganha numero')
    ok('Bianca Furtado' in pg.inner_text('#concSub') and 'Nordeste' in pg.inner_text('#concSub'), 'com vendedor e cliente')
    ok(pg.inner_text('#concTotal') == 'R$ 749,70' and pg.inner_text('#concDinheiro') == 'R$ 350,00' and pg.inner_text('#concTroco') == 'R$ 50,00', 'total, recebido em dinheiro e troco conferem')
    g = pg.inner_text('#concGerado')
    ok('Pedido de Venda PDV-0001' in g and 'Entregue' in g and 'Bianca Furtado' in g, 'gerou o Pedido de Venda ja entregue, na meta do vendedor')
    ok('Baixa de estoque em Geral: 3 unidades de 1 produto' in g, 'gerou a baixa no deposito: %s' % [l for l in g.split(chr(10)) if 'Baixa' in l][:1])
    ok('R$ 300,00 entram na hora em Caixa' in g, 'o dinheiro entra direto na conta, sem titulo')
    ok('2 títulos em Contas a Receber' in g and 'Distribuidora Nordeste' in g, 'o cartao gerou os titulos em nome do cliente')
    ok('Taxa de R$ 15,69' in g and 'R$ 434,01' in g, 'e a taxa com o liquido')
    ok(pg.evaluate("saldoDe('FON-BT-200', 1)") == 31, 'o saldo do produto baixou de 34 para 31')
    ok(pg.evaluate('usados[3]') == 449.7, 'e o limite do cliente passou a contar a venda a prazo')
    clic(pg, '#btnRecibo'); pg.wait_for_timeout(250)
    r = pg.evaluate("document.getElementById('folhaImpressao').innerText")
    ok(pg.evaluate('window.__imprimiu') == 1 and 'Recibo de venda' in r and 'R$ 749,70' in r and 'Troco' in r, 'o recibo traz itens, valores, formas e troco')
    clic(pg, '#btnReciboTroca'); pg.wait_for_timeout(250)
    r = pg.evaluate("document.getElementById('folhaImpressao').innerText")
    ok('Recibo para troca' in r and 'R$' not in r and 'Fone de Ouvido' in r, 'o recibo para troca traz os itens e NENHUM valor')
    clic(pg, '#btnOutraVenda'); pg.wait_for_timeout(350)
    ok(pg.evaluate('momento') == 'venda' and pg.evaluate('venda.itens.length') == 0 and pg.evaluate('numeroVenda') == 2, 'iniciar outra venda limpa a tela e avanca o numero')

    print('\n[8] Turno: sangria, reforco e fechamento cego')
    clic(pg, '#btnDetalhesCaixa'); pg.wait_for_timeout(300)
    d = pg.inner_text('#caixaCorpo')
    ok('Caixa aberto' in d and 'R$ 150,00' in d and '1 · R$ 749,70' in d, 'detalhes mostra abertura, troco e vendas')
    ok('não aparece com o caixa aberto' in d and 'R$ 450,00' not in d, 'e NAO mostra o esperado por forma: o fechamento e cego')
    clic(pg, '#abasCaixa [data-aba="vendas"]'); pg.wait_for_timeout(200)
    ok('Venda nº 1' in pg.inner_text('#caixaCorpo') and 'Cartão de crédito' in pg.inner_text('#caixaCorpo'), 'a aba de vendas lista a venda com as formas')
    clic(pg, '#menuMaisAcoes [data-acao="sangria"]'); pg.wait_for_timeout(300)
    ok(pg.locator('#movDrawer.open').count() == 1 and pg.inner_text('#movTitulo') == 'Sangria de caixa', 'Mais acoes abre a sangria')
    ok(pg.inner_text('#movConta .dropdown-select-label') == 'Cofre da loja', 'com o cofre sugerido como destino')
    pg.fill('#movValor', '9000'); pg.fill('#movMotivo', 'teste'); clic(pg, '#btnSalvarMov'); pg.wait_for_timeout(250)
    e = pg.inner_text('#erroMovValor')
    ok(visivel(pg, '#erroMovValor') and 'R$' not in e, 'sangria maior que a gaveta e barrada SEM revelar quanto ha (cego): %s' % e)
    pg.fill('#movValor', '100'); pg.fill('#movMotivo', ''); clic(pg, '#btnSalvarMov'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroMovMotivo'), 'sangria sem motivo e barrada')
    pg.fill('#movMotivo', 'excesso de dinheiro na gaveta'); clic(pg, '#btnSalvarMov'); pg.wait_for_timeout(400)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal'), 'sangria pede senha')
    confirmar(pg); fechar_aviso(pg)
    ok(pg.evaluate("turno.movimentos.length") == 1 and pg.evaluate("dinheiroNaGaveta(turno)") == 350, 'a sangria sai da gaveta: 150 + 300 - 100 = 350')
    clic(pg, '#menuMaisAcoes [data-acao="reforco"]'); pg.wait_for_timeout(300)
    pg.fill('#movValor', '50'); pg.fill('#movMotivo', 'troco'); clic(pg, '#btnSalvarMov'); pg.wait_for_timeout(400)
    ok(not (pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal')), 'reforco nao pede senha por padrao')
    fechar_aviso(pg)
    ok(pg.evaluate("dinheiroNaGaveta(turno)") == 400 and pg.evaluate("turno.movimentos.length") == 2, 'e entra na gaveta: 400')
    adicionar(pg, 'CAR-33W-01', '1')
    clic(pg, '#menuMaisAcoes [data-acao="fechar"]'); pg.wait_for_timeout(350)
    ok(pg.locator('#fecharDrawer.open').count() == 0 and 'venda em andamento' in pg.inner_text('#confirmModalTexto'), 'com venda em andamento o caixa nao fecha')
    fechar_aviso(pg)
    clic(pg, '#btnCancelarVenda'); pg.wait_for_timeout(300)
    ok('Cancelar a venda' in pg.inner_text('#confirmModalTexto'), 'cancelar a venda pergunta antes')
    confirmar(pg, senha=False)
    ok(pg.evaluate('venda.itens.length') == 0, 'e limpa os itens')
    clic(pg, '#menuMaisAcoes [data-acao="fechar"]'); pg.wait_for_timeout(350)
    campos = pg.evaluate("Array.from(document.querySelectorAll('#fecharCampos [data-fechar]')).map(e => e.getAttribute('data-fechar'))")
    ok(campos == ['dinheiro', 'credito'], 'o fechamento pede as formas que o turno recebeu: %s' % campos)
    ok('Esperado:' not in pg.inner_text('#fecharDrawer') and pg.input_value('[data-fechar="dinheiro"]') == '', 'os campos abrem vazios e sem o valor esperado')
    ok('não aparece' in pg.inner_text('#fecharNota'), 'e a nota do painel diz que o esperado nao aparece')
    clic(pg, '#btnConfirmarFechamento'); pg.wait_for_timeout(250)
    ok('todas' in pg.inner_text('#fecharDivergencia') and pg.evaluate('turno') is not None, 'campo em branco nao fecha')
    pg.fill('[data-fechar="dinheiro"]', '380'); pg.fill('[data-fechar="credito"]', '449,70')
    clic(pg, '#btnConfirmarFechamento'); pg.wait_for_timeout(300)
    dv = pg.inner_text('#fecharDivergencia')
    ok('Dinheiro' in dv and 'Cartão de crédito' not in dv and '400' not in dv and pg.evaluate('turno') is not None,
       'contagem que nao bate diz ONDE, nunca quanto era: %s' % dv[:90])
    ok(visivel(pg, '#btnForcarFechamento'), 'e so entao aparece o fechar com diferenca')
    clic(pg, '#btnForcarFechamento'); pg.wait_for_timeout(350)
    t = pg.inner_text('#confirmModalTexto')
    ok(visivel(pg, '#campoSenhaModal') and 'contado R$ 380,00' in t and 'esperado R$ 400,00' in t, 'fechar com diferenca pede senha, e quem libera ve os numeros')
    clic(pg, '#btnConfirmModalCancelar'); pg.wait_for_timeout(300)
    ok(pg.evaluate('turno') is not None, 'cancelar na senha mantem o caixa aberto')
    pg.fill('[data-fechar="dinheiro"]', '400')
    clic(pg, '#btnConfirmarFechamento'); pg.wait_for_timeout(450)
    ok(pg.evaluate('turno') is None and pg.evaluate('momento') == 'fechado', 'contagem certa fecha o caixa sem senha')
    ok('bateu' in pg.inner_text('#confirmModalTexto'), 'e o aviso diz que a contagem bateu')
    fechar_aviso(pg)
    u = pg.inner_text('#ultimoTurno')
    ok('Desk Shope' in u and '1 venda' in u and 'sem diferença' in u, 'a tela de caixa fechado resume o ultimo turno: %s' % u[:110])
    clic(pg, '#linkUltimoTurno'); pg.wait_for_timeout(300)
    d = pg.inner_text('#caixaCorpo')
    ok('Caixa fechado' in d and 'esperado' in d.lower() and 'R$ 400,00' in d, 'depois de fechado, detalhes mostra esperado, contado e diferenca')
    clic(pg, '#btnReimprimirTurno'); pg.wait_for_timeout(250)
    r = pg.evaluate("document.getElementById('folhaImpressao').innerText")
    ok('fechamento de caixa' in r and 'Sangrias' in r and 'Diferença' in r and 'R$ 0,00' in r, 'e o comprovante de fechamento sai com entradas, saidas e diferenca')
    clic(pg, '#caixaDrawer [data-fechar-painel]'); pg.wait_for_timeout(250)
    # fechar com diferenca de verdade, e abrir com o ultimo valor
    abrir_caixa(pg, 1, '100')
    clic(pg, '#menuMaisAcoes [data-acao="fechar"]'); pg.wait_for_timeout(300)
    pg.fill('[data-fechar="dinheiro"]', '90'); clic(pg, '#btnConfirmarFechamento'); pg.wait_for_timeout(250)
    clic(pg, '#btnForcarFechamento'); pg.wait_for_timeout(300); confirmar(pg); fechar_aviso(pg)
    ok(pg.evaluate('ultimoTurno.forcado') is True and pg.evaluate('ultimoTurno.diferenca') == -10 and 'diferença de' in pg.inner_text('#ultimoTurno'),
       'com a senha, o caixa fecha registrando a diferenca de -10')

    print('\n[9] Tudo que o PDV le de outro cadastro bate com o cadastro')
    # Enquanto nao ha backend, o PDV carrega espelhos. Sem estas comparacoes eles
    # divergem em silencio: o PDV ofereceria forma desabilitada, venderia produto
    # com preco velho ou validaria limite numa forma que o cadastro nao manda.
    pdv = pg.evaluate("({ formas: FORMAS, catalogo: CATALOGO, lojas: LOJAS, depositos: DEPOSITOS, padrao: DEPOSITO_PADRAO_DA_LOJA, vendedores: VENDEDORES, "
                      "clientes: CLIENTES.map(c => [c.id, c.nome, c.documento]), contas: CONTAS_FINANCEIRAS.map(c => c.id + ':' + c.nome), categorias: CATEGORIAS })")
    p2 = ctx.new_page()
    e2 = []
    p2.on('pageerror', lambda e: e2.append(str(e)))
    p2.goto(localiza.http(FORMAS_CAD)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    cad = p2.evaluate("FORMAS.filter(f => f.sistema)")
    campos = ['chave', 'nome', 'uso', 'destino', 'contaId', 'tarifacao', 'taxaPct', 'taxaFixa', 'validaLimite', 'ativo']
    dif = [f['chave'] for f in cad if [f[c] for c in campos] != [next((x for x in pdv['formas'] if x['chave'] == f['chave']), {}).get(c) for c in campos]]
    ok(len(cad) == len(pdv['formas']) and not dif, 'formas de recebimento: as dez, campo a campo: %s' % (dif or 'iguais'))
    p2.goto(localiza.http(PEDIDO)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    ped = p2.evaluate("({ catalogo: CATALOGO, lojas: LOJAS, depositos: DEPOSITOS, padrao: DEPOSITO_PADRAO_DA_LOJA })")
    semg = [dict((k, v) for k, v in x.items() if k != 'gtin') for x in pdv['catalogo']]
    ok(semg == ped['catalogo'], 'catalogo: produto, loja, preco e saldo por deposito iguais aos do Pedido de Venda')
    ok(dict((str(l['id']), l['nome']) for l in pdv['lojas']) == ped['lojas'] and dict((str(d['id']), d['nome']) for d in pdv['depositos']) == ped['depositos']
       and dict((str(k), v) for k, v in pdv['padrao'].items()) == dict((str(k), v) for k, v in ped['padrao'].items()),
       'lojas, depositos e o deposito padrao de cada loja iguais aos do Pedido')
    ok(len(set(x['gtin'] for x in pdv['catalogo'])) == len(pdv['catalogo']), 'e nenhum GTIN repetido no catalogo do PDV')
    p2.goto(localiza.http(METAS)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    ok(p2.evaluate("VENDEDORES") == pdv['vendedores'], 'vendedores iguais aos de Metas')
    p2.goto(localiza.http(CLIENTES_CAD)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    cli = p2.evaluate("CLIENTES.map(c => [c.id, c.nome, c.documento])")
    ok(all(c in cli for c in pdv['clientes']), 'todo cliente do PDV existe em Cadastros, com o mesmo nome e documento')
    p2.goto(localiza.http(CONTAS_CAD)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    ok(sorted(p2.evaluate("CONTAS.filter(c => c.ativo).map(c => c.id + ':' + c.nome)")) == sorted(pdv['contas']), 'contas financeiras: as ativas')
    p2.goto(localiza.http(CATEG_CAD)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    cat = p2.evaluate("CATEGORIAS.filter(c => c.grupoId === 1 && c.ativo && c.dre !== 'deducoes').map(c => ({ id: c.id, nome: c.descricao, padraoVenda: c.padraoVenda }))")
    ok(cat == pdv['categorias'], 'categorias financeiras: as de receita de vendas, fora as de deducao, com a padrao de vendas')
    # O espelho casa por id: dois cadastros com o mesmo id fariam o PDV (e a exclusao) pegar o errado.
    ids_cat = p2.evaluate("CATEGORIAS.map(c => c.id)")
    ok(len(ids_cat) == len(set(ids_cat)), 'cadastro de categorias financeiras sem id repetido: %s' % sorted(i for i in set(ids_cat) if ids_cat.count(i) > 1))

    print('\n[10] Os nove parametros nascem nas duas telas, e o PDV obedece')
    padrao_pdv = pg.evaluate("(ks) => ks.map(k => PARAM_PADRAO[k])", CHAVES)
    p2.goto(localiza.http(CFG)); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    p2.evaluate("localStorage.removeItem('deskParametros')"); p2.reload(); p2.wait_for_load_state('load'); p2.wait_for_timeout(500)
    ok(p2.evaluate("(ks) => ks.map(k => PARAM_PADRAO[k])", CHAVES) == padrao_pdv and None not in padrao_pdv,
       'as nove chaves existem nas duas telas, com o mesmo padrao: %s' % padrao_pdv)
    ok('Nenhuma alteração pendente' in p2.inner_text('#notaBarra'), 'Configuracoes do PDV abre sem pendencia')
    clic(p2, '#swVendedor'); clic(p2, '#swPreco'); p2.fill('#descMax', '5'); p2.wait_for_timeout(200)
    ok('3 configurações alteradas' in p2.inner_text('#notaBarra'), 'mexer em tres parametros faz a nota contar tres')
    ok('5%' in p2.inner_text('#previaDesconto') and 'travado' in p2.inner_text('#previaDesconto'), 'e a previa descreve a consequencia: %s' % p2.inner_text('#previaDesconto')[:80])
    p2.fill('#descMax', '250'); p2.wait_for_timeout(150)
    clic(p2, '#btnSalvarParam'); p2.wait_for_timeout(300)
    ok('0 a 100' in p2.inner_text('#avisoTexto') or '0 a 100' in p2.inner_text('#confirmModalTexto'), 'desconto maximo fora de 0 a 100 nao salva')
    p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    p2.fill('#descMax', '5'); p2.wait_for_timeout(150)
    clic(p2, '#btnSalvarParam'); p2.wait_for_timeout(350)
    p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    ok(p2.evaluate("JSON.parse(localStorage.getItem('deskParametros')).pdvDescontoMaximoPct") == 5 and 'Nenhuma alteração pendente' in p2.inner_text('#notaBarra'),
       'salvar grava e zera a nota')
    clic(p2, '#swCego'); p2.wait_for_timeout(150)
    clic(p2, '#btnSalvarParam'); p2.wait_for_timeout(350)
    ok(p2.locator('#confirmModal.open').count() == 1 and visivel(p2, '#campoSenhaModal'), 'desligar o fechamento cego pede senha')
    clic(p2, '#btnConfirmModalCancelar'); p2.wait_for_timeout(250)
    ok(p2.evaluate("JSON.parse(localStorage.getItem('deskParametros')).pdvFechamentoCego") is True, 'e cancelar na senha nao desliga')
    p2.close()
    # o PDV le o que foi salvo: vendedor obrigatorio, preco travado, desconto maximo de 5%
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    abrir_caixa(pg, 2, '0')
    ok(pg.evaluate("Array.from(document.querySelectorAll('#menuVendedor .dropdown-select-item')).map(e => e.textContent)") == ['Sem vendedor', 'Rafael Tenório', 'Ponto Parceiro Vila Mariana'],
       'turno de outra loja troca os vendedores')
    adicionar(pg, 'CAM-BSC-PT', '2')
    ok(pg.evaluate('venda.itens.length') == 1 and pg.evaluate('venda.depositoId') == 3, 'e vende os produtos dela, do deposito dela')
    clic(pg, '#btnContinuar'); pg.wait_for_timeout(300)
    ok(pg.evaluate('momento') == 'venda' and 'vendedor' in pg.inner_text('#confirmModalTexto').lower(), 'com "vendedor obrigatorio" ligado, a venda nao avanca sem vendedor')
    fechar_aviso(pg)
    clic(pg, '#listaItens tbody tr'); pg.wait_for_timeout(300)
    ok(pg.evaluate("document.getElementById('itemPreco').disabled") is True and 'travado' in pg.inner_text('#hintItemPreco'), 'com "bloquear alteracao de preco" ligado, o preco vem travado')
    escolher(pg, 'itemAjusteTipo', 'desconto'); escolher(pg, 'itemAjusteModo', 'pct'); pg.fill('#itemAjusteValor', '8'); pg.wait_for_timeout(200)
    ok(visivel(pg, '#itemNota') and '5,00%' in pg.inner_text('#itemNota'), 'e 8% de desconto ja passa do maximo de 5%')
    clic(pg, '#itemDrawer [data-fechar-painel]'); pg.wait_for_timeout(250)
    # fechamento NAO cego mostra o esperado; abrir com o ultimo valor sugere o troco
    zerar(pg, {'pdvFechamentoCego': False, 'pdvAbreComUltimoFechamento': True, 'pdvBloqueiaSemEstoque': False, 'pdvAgrupaIguais': False})
    abrir_caixa(pg, 1, '80')
    adicionar(pg, 'FON-BT-200', '50')
    ok(pg.evaluate('venda.itens.length') == 1, 'com o bloqueio de estoque desligado, vende alem do saldo')
    adicionar(pg, 'FON-BT-200', '1')
    ok(pg.evaluate('venda.itens.length') == 2, 'e com "agrupar iguais" desligado, o mesmo produto vira outra linha')
    clic(pg, '#btnCancelarVenda'); pg.wait_for_timeout(250); confirmar(pg, senha=False)
    clic(pg, '#btnDetalhesCaixa'); pg.wait_for_timeout(300)
    ok('resumo por forma' in pg.inner_text('#caixaCorpo').lower() and 'R$ 80,00' in pg.inner_text('#caixaCorpo'), 'fechamento nao cego: detalhes mostra o esperado com o caixa aberto')
    clic(pg, '#btnFecharCaixaPainel'); pg.wait_for_timeout(300)
    ok('Esperado: R$ 80,00' in pg.inner_text('#fecharCampos'), 'e o fechamento mostra o esperado ao lado do campo')
    ok('desligado' in pg.inner_text('#fecharNota') and 'não aparece' not in pg.inner_text('#fecharNota'), 'e a nota do painel nao diz mais que o esperado esta oculto')
    pg.fill('[data-fechar="dinheiro"]', '80'); clic(pg, '#btnConfirmarFechamento'); pg.wait_for_timeout(350); fechar_aviso(pg)
    clic(pg, '#btnAbrirCaixa'); pg.wait_for_timeout(300)
    ok(pg.input_value('#abrirTroco') == '80,00' and 'último fechamento' in pg.inner_text('#hintTroco'), 'abrir com o ultimo valor sugere os 80 contados')
    clic(pg, '#abrirDrawer [data-fechar-painel]'); pg.wait_for_timeout(250)

    print('\n[11] As acoes do PDV estao no catalogo de senhas')
    # O desconto na venda inteira obedece ao mesmo maximo do desconto do item.
    zerar(pg); abrir_caixa(pg, 1, '0')
    adicionar(pg, 'CAR-33W-01', '1')
    clic(pg, '#btnContinuar'); pg.wait_for_timeout(350)
    pg.fill('#finDesconto', '20%'); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
    receber(pg, 'dinheiro')
    clic(pg, '#btnFinalizar'); pg.wait_for_timeout(400)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal') and 'venda inteira' in pg.inner_text('#confirmModalTexto'),
       'desconto na venda inteira acima do maximo pede senha para finalizar')
    ok(pg.evaluate('momento') == 'finalizar', 'antes da senha, a venda nao finaliza')
    confirmar(pg)
    ok(pg.evaluate('momento') == 'concluida', 'com a senha, finaliza')
    acoes = pg.evaluate("ACOES_SENHA.filter(a => a.chave.indexOf('pdv') === 0).map(a => a.chave + '/' + a.exigePadrao)")
    ok(sorted(acoes) == ['pdvDescontoAcima/true', 'pdvFechaComDiferenca/true', 'pdvReforco/false', 'pdvSangria/true'], 'as quatro do PDV, com o padrao de cada: %s' % sorted(acoes))
    for arq in CATALOGOS:
        txt = open(localiza.onde(arq), encoding='utf-8').read()
        falta = [k for k in ['pdvSangria', 'pdvReforco', 'pdvFechaComDiferenca', 'pdvDescontoAcima', 'pdvCegoDesliga'] if ("chave:'" + k + "'") not in txt]
        ok(not falta, '%s conhece as cinco acoes: %s' % (arq.replace('pagina-', ''), falta or 'todas'))

    print('\n[12] Atalhos, os dois temas e erro de JS')
    zerar(pg)
    pg.keyboard.press('Control+Enter'); pg.wait_for_timeout(300)
    ok(pg.locator('#abrirDrawer.open').count() == 1, 'Ctrl+Enter com o caixa fechado abre a abertura')
    pg.fill('#abrirTroco', '10'); pg.keyboard.press('Control+Enter'); pg.wait_for_timeout(400)
    ok(pg.evaluate('momento') == 'venda', 'e Ctrl+Enter no painel confirma')
    pg.evaluate("document.activeElement.blur()")
    pg.keyboard.type('cad'); pg.wait_for_timeout(250)
    ok(pg.input_value('#buscaProduto') == 'cad' and pg.locator('#sugestoes .pdv-sug').count() == 1, 'digitar sem clicar no campo vai para a busca de produto')
    pg.keyboard.press('Enter'); pg.wait_for_timeout(200); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)
    ok(pg.evaluate('venda.itens.length') == 1, 'Enter escolhe e Enter adiciona')
    pg.keyboard.press('F8'); pg.wait_for_timeout(300)
    ok(pg.locator('#clienteDrawer.open').count() == 1, 'F8 abre o cliente')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#clienteDrawer.open').count() == 0, 'Esc fecha o painel')
    pg.keyboard.press('Control+Enter'); pg.wait_for_timeout(350)
    ok(pg.evaluate('momento') == 'finalizar', 'Ctrl+Enter na venda continua')
    pg.keyboard.press('F4'); pg.wait_for_timeout(250)
    ok(pg.locator('#menuAddReceb.open').count() == 1, 'F4 abre as formas de recebimento')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#menuAddReceb.open').count() == 0 and pg.evaluate('momento') == 'finalizar', 'o primeiro Esc fecha so o menu aberto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
    ok(pg.evaluate('momento') == 'venda', 'e o segundo volta para os itens')
    pg.keyboard.press('Control+y'); pg.wait_for_timeout(300)
    ok(pg.locator('#caixaDrawer.open').count() == 1, 'Ctrl+Y abre os detalhes do caixa')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(220)
        ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440, 'tema %s: nao estoura em 1440' % tema)
    ok(not erros and not e2, 'sem erro de JS: %s' % (erros + e2)[:2])

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
