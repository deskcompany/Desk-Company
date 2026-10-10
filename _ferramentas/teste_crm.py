# -*- coding: utf-8 -*-
# CRM (Vendas), as duas telas de Configuracoes de que ele depende e o status do
# contato em Cadastros > Clientes. Nasceu em 09/out/2026.
#
# O que a suite guarda sao as quatro decisoes do usuario e o que vem delas:
#   - o status do contato (lead, prospect, cliente) mora no cadastro de Clientes;
#   - encerrar pergunta ganho ou perdido e, se perdeu, o motivo;
#   - a proxima acao com data vira aviso na Agenda do Inicio;
#   - quadro por estagio, WhatsApp e e-mail (abrem o aplicativo e registram) e a
#     proposta como registro do assunto.
#
#   [1]  menu e hub;                      [2]  lista: abas, ordem, avisos, rodape;
#   [3]  busca e filtros;                 [4]  estrela, menu da linha, status do contato;
#   [5]  selecao, arquivar e excluir;     [6]  incluir assunto;
#   [7]  acoes: nova, editar, concluir;   [8]  estagio, encerrar e reabrir;
#   [9]  proposta;                        [10] anotacao, WhatsApp e e-mail;
#   [11] abas vendas e financeiro;        [12] avisos na Agenda;
#   [13] quadro por estagio;              [14] parametro de dias sem interacao;
#   [15] cadastro de estagios do funil;   [16] ESPELHOS contra os cadastros;
#   [17] catalogo de senhas;              [18] o relogio na Agenda;
#   [19] Esc, temas, largura e erro de JS.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g
import datetime
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

LISTA = 'pagina-vendas-crm.html'
DET = 'pagina-vendas-crm-detalhe.html'
CFG = 'pagina-configuracoes-crm.html'
EST = 'pagina-configuracoes-estagios-funil.html'
HUB = 'pagina-configuracoes.html'
CLI = 'pagina-cadastros-clientes.html'
CLI_DET = 'pagina-cadastros-clientes-detalhe.html'
METAS = 'pagina-vendas-metas.html'
PEDIDOS = 'pagina-vendas-pedidos.html'
RECEBER = 'pagina-financas-contas-receber.html'
AGENDA = 'pagina-inicio-agenda.html'
CATALOGOS = ['pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html',
             'pagina-cadastros-vendedores-detalhe.html']

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
    """Confirma o modal aberto: marca o 'estou ciente' e informa a senha quando a tela pede."""
    if pg.locator('#confirmModal.open').count():
        pg.evaluate("() => { const c = document.querySelector('#confirmModal input[type=checkbox]'); if (c && c.offsetParent !== null && !c.checked) c.click(); }")
        if senha and visivel(pg, '#campoSenhaModal'):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(450)


def fechar_aviso(pg):
    if pg.locator('#confirmModal.open').count():
        clic(pg, '#btnConfirmModalConfirmar')
        pg.wait_for_timeout(300)


def ir(pg, tela, query=''):
    pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(550)


def zerar(pg, param=None):
    """Comeca do zero: sem estado do CRM, sem avisos e com os parametros pedidos."""
    ir(pg, LISTA)
    pg.evaluate("(p) => { localStorage.removeItem('deskCrm'); localStorage.removeItem('deskAvisos'); if (p) localStorage.setItem('deskParametros', JSON.stringify(p)); else localStorage.removeItem('deskParametros'); }", param)
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)


def linhas(pg):
    """Clientes das linhas da lista, na ordem em que aparecem."""
    return pg.evaluate("Array.from(document.querySelectorAll('#listaCrm tbody tr')).map(tr => tr.querySelector('.crm-cli').innerText.trim())")


def abas(pg):
    return pg.evaluate("Array.from(document.querySelectorAll('#abasCrm .aba-sit')).map(a => a.getAttribute('data-aba') + ':' + a.querySelector('.sit-contador').innerText)")


def rodape(pg):
    return pg.inner_text('#rodapeCrm').replace(chr(10), ' ')


def tempo(pg):
    """Titulos da linha do tempo, de cima para baixo."""
    return pg.evaluate("Array.from(document.querySelectorAll('#abaCorpo .crm-lt-tit')).map(e => e.innerText)")


def acao_menu(pg, acao):
    clic(pg, '#menuMaisAcoes [data-acao="' + acao + '"]'); pg.wait_for_timeout(350)


HOJE = datetime.date.today()
def dma(dias): return (HOJE + datetime.timedelta(days=dias)).strftime('%d/%m/%Y')


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    # Contexto explicito: lista, assunto, Agenda e Configuracoes precisam dividir o armazenamento.
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('\n[1] O CRM tem porta no menu e no hub de Configuracoes')
    zerar(pg)
    href = pg.evaluate("document.querySelector('.flyout-item[data-label=\"CRM\"]').getAttribute('data-href')")
    ok(href == '../vendas/pagina-vendas-crm.html' and localiza.existe(LISTA) and localiza.existe(DET), 'o item CRM do menu de Vendas leva para a lista: %s' % href)
    hub = open(localiza.onde(HUB), encoding='utf-8').read()
    ok("nome:'Configurações do CRM', href:'../configuracoes/pagina-configuracoes-crm.html'" in hub and
       "nome:'Estágios do funil de vendas', href:'../configuracoes/pagina-configuracoes-estagios-funil.html'" in hub and localiza.existe(CFG) and localiza.existe(EST),
       'o hub tem os dois cartoes, com destino: Configuracoes do CRM e Estagios do funil de vendas')

    print('\n[2] A lista: abas, ordem, avisos e rodape')
    ok(abas(pg) == ['todos:8', 'pendentes:5', 'encerrados:2', 'estrela:2', 'arquivados:1'], 'as cinco abas contam: %s' % abas(pg))
    l = linhas(pg)
    ok(l[0] == 'Juliana Prado' and l[1] == 'Distribuidora Nordeste Ltda' and l[2] == 'Camila Rêgo' and l[-2:] == ['Bruno Carvalho', 'Tech Solutions Imperatriz Ltda'],
       'o que e para ja vem primeiro, a acao atrasada antes da de hoje, e os encerrados por ultimo: %s' % l)
    corpo = pg.inner_text('#listaCrm')
    ok('SEM INTERAÇÃO HÁ 40 DIAS' in corpo.upper() and corpo.upper().count('SEM INTERAÇÃO') == 1, 'assunto parado ha mais de 30 dias ganha o aviso, e so ele')
    ok('PERDIDO · PREÇO' in corpo.upper() and 'GANHO' in corpo.upper(), 'encerrado diz se foi ganho ou perdido, com o motivo')
    ok('Atrasada · ' + dma(-2)[:5] in corpo and 'Hoje às 15:00' in corpo and 'Amanhã' in corpo and 'Quanto antes' in corpo and 'Esperar' in corpo,
       'a coluna Quando fala em palavras: atrasada, hoje, amanha, quanto antes, esperar')
    ok('R$ 8.450,00' in corpo and 'Apresentada' in corpo and 'R$ 5.980,00' in corpo and 'Aceita' in corpo, 'a coluna Proposta mostra o valor e a situacao')
    ok(rodape(pg) == '8 assuntos 2 leads 3 prospects 3 clientes 0 inativos', 'o rodape conta assuntos e os contatos por status: %s' % rodape(pg))
    ok(pg.evaluate("(() => { const w = document.querySelector('#listaCrm .estoque-table-wrap'); return w.scrollWidth <= w.clientWidth + 1; })()"), 'a tabela cabe no cartao em 1440')

    print('\n[3] Busca e filtros')
    pg.fill('#buscaCrm', 'nordeste'); pg.wait_for_timeout(250)
    ok(linhas(pg) == ['Distribuidora Nordeste Ltda'], 'busca por nome do contato')
    pg.fill('#buscaCrm', '38.114'); pg.wait_for_timeout(250)
    ok(linhas(pg) == ['Móveis Bom Preço Ltda'], 'busca por CNPJ, com ou sem pontuacao')
    pg.fill('#buscaCrm', 'monitores'); pg.wait_for_timeout(250)
    ok(linhas(pg) == ['Tech Solutions Imperatriz Ltda'] and abas(pg)[0] == 'todos:1', 'busca pelo assunto, e as abas contam o que a busca deixou')
    pg.fill('#buscaCrm', 'zzzz'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#emptyState') and rodape(pg).startswith('0 assuntos'), 'busca sem resultado mostra o estado vazio')
    pg.fill('#buscaCrm', ''); pg.wait_for_timeout(250)
    esperado = {'atrasadas': ['Distribuidora Nordeste Ltda'], 'hoje': ['Juliana Prado', 'Camila Rêgo'],
                'semana': ['Camila Rêgo', 'Móveis Bom Preço Ltda'], 'semacao': ['Thiago Almeida']}
    for f, quem in esperado.items():
        escolher(pg, 'filtroQuando', f)
        ok(linhas(pg) == quem, 'filtro "%s": %s' % (f, linhas(pg)))
    escolher(pg, 'filtroQuando', 'todos')
    escolher(pg, 'filtroResp', 6)
    ok(linhas(pg) == ['Juliana Prado', 'Móveis Bom Preço Ltda'], 'filtro por responsavel: %s' % linhas(pg))
    escolher(pg, 'filtroResp', 'todos')
    clic(pg, '#abasCrm [data-aba="arquivados"]'); pg.wait_for_timeout(250)
    ok(linhas(pg) == ['Patrícia Farias'] and 'ARQUIVADO' in pg.inner_text('#listaCrm').upper(), 'a aba de arquivados mostra so o arquivado')
    clic(pg, '#abasCrm [data-aba="pendentes"]'); pg.wait_for_timeout(250)
    ok(len(linhas(pg)) == 5 and 'Thiago Almeida' not in linhas(pg) and 'Tech Solutions Imperatriz Ltda' not in linhas(pg), 'com acoes pendentes: so assunto aberto com acao')
    clic(pg, '#abasCrm [data-aba="todos"]'); pg.wait_for_timeout(250)

    print('\n[4] Estrela, menu da linha e status do contato')
    clic(pg, '#listaCrm [data-estrela="2"]'); pg.wait_for_timeout(250)
    ok(abas(pg)[3] == 'estrela:3' and pg.evaluate("assuntoDe(2).estrela") is True, 'a estrela marca na propria linha')
    clic(pg, '#listaCrm [data-menu="1"]'); pg.wait_for_timeout(250)
    m = pg.inner_text('#menuLinha')
    ok(pg.locator('#menuLinha.open').count() == 1 and 'Camila Rêgo' in m and all(x in m for x in ['Abrir assunto', 'Editar assunto', 'Arquivar assunto', 'Alterar status do contato', 'Excluir assunto']),
       'o menu da linha abre com o nome do cliente e as acoes')
    ok(pg.evaluate("document.querySelector('#menuLinha .crm-menu-contato.ativo').getAttribute('data-contato')") == 'lead', 'e marca o status atual do contato: lead')
    clic(pg, '#menuLinha [data-contato="prospect"]'); pg.wait_for_timeout(300)
    ok(rodape(pg) == '8 assuntos 1 leads 4 prospects 3 clientes 0 inativos', 'trocar o status do contato muda o rodape: %s' % rodape(pg))
    ok(pg.evaluate("assuntoDe(1).eventos.slice(-1)[0].tipo") == 'contato' and 'Prospect' in pg.evaluate("assuntoDe(1).eventos.slice(-1)[0].texto"), 'e fica registrado na linha do tempo do assunto')
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(rodape(pg) == '8 assuntos 1 leads 4 prospects 3 clientes 0 inativos' and abas(pg)[3] == 'estrela:3', 'estrela e status sobrevivem ao F5')
    clic(pg, '#listaCrm [data-menu="1"]'); pg.wait_for_timeout(250)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.locator('#menuLinha.open').count() == 0, 'Esc fecha o menu da linha')

    print('\n[5] Selecao, arquivar e excluir')
    clic(pg, '#listaCrm .item-checkbox[data-id="5"]'); clic(pg, '#listaCrm .item-checkbox[data-id="9"]'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#barraSelecao') and pg.inner_text('#selecaoInfo') == '2 selecionados', 'marcar duas linhas mostra a barra de selecao')
    clic(pg, '#btnExcluirSelecionados'); pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 1 and visivel(pg, '#campoSenhaModal') and '2 assuntos' in pg.inner_text('#confirmModalTexto'), 'excluir em massa pede senha e diz quantos')
    clic(pg, '#btnConfirmModalCancelar'); pg.wait_for_timeout(300)
    ok(pg.evaluate('ASSUNTOS.length') == 9, 'cancelar na senha nao exclui nada')
    clic(pg, '#btnArquivarSelecionados'); pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 1 and not visivel(pg, '#campoSenhaModal'), 'arquivar pergunta antes, sem senha')
    confirmar(pg, senha=False)
    ok(abas(pg)[4] == 'arquivados:3' and abas(pg)[0] == 'todos:6' and not visivel(pg, '#barraSelecao'), 'os dois vao para arquivados e a selecao some: %s' % abas(pg))
    clic(pg, '#abasCrm [data-aba="arquivados"]'); pg.wait_for_timeout(250)
    clic(pg, '#checkSelecionarTodos'); pg.wait_for_timeout(250)
    ok(pg.inner_text('#selecaoInfo') == '3 selecionados', '"selecionar todos" marca a pagina')
    clic(pg, '#btnCancelarSelecao'); pg.wait_for_timeout(200)
    clic(pg, '#listaCrm [data-menu="9"]'); pg.wait_for_timeout(250)
    ok('Desarquivar assunto' in pg.inner_text('#menuLinha'), 'no arquivado o menu oferece desarquivar')
    clic(pg, '#menuLinha [data-linha="arquivar"]'); pg.wait_for_timeout(300); confirmar(pg, senha=False)
    ok(abas(pg)[4] == 'arquivados:2', 'desarquivar devolve o assunto para as listas')
    clic(pg, '#listaCrm [data-menu="5"]'); pg.wait_for_timeout(250)
    clic(pg, '#menuLinha [data-linha="excluir"]'); pg.wait_for_timeout(350)
    ok(visivel(pg, '#campoSenhaModal') and 'Kit home office' in pg.inner_text('#confirmModalTexto'), 'excluir um assunto pede senha e diz qual')
    confirmar(pg)
    ok(pg.evaluate('ASSUNTOS.length') == 8 and pg.evaluate('assuntoDe(5)') is None, 'com a senha, o assunto e excluido')
    clic(pg, '#abasCrm [data-aba="todos"]'); pg.wait_for_timeout(250)

    print('\n[6] Incluir assunto')
    clic(pg, '#btnIncluirAssunto'); pg.wait_for_timeout(350)
    ok(pg.locator('#assuntoDrawer.open').count() == 1 and pg.inner_text('#assuntoDrawerTitulo') == 'Incluir assunto' and visivel(pg, '#novoCampoEstagio'), 'o painel de incluir abre, com o estagio para escolher')
    opcoes = pg.evaluate("Array.from(document.querySelectorAll('#menuNovoCliente .dropdown-select-item')).map(e => e.textContent)")
    ok('Pedro Henrique Alves' not in opcoes and 'Camila Rêgo' in opcoes and len(opcoes) == 11, 'so cliente ativo pode ganhar assunto novo: %d opcoes' % len(opcoes))
    ok(pg.evaluate("Array.from(document.querySelectorAll('#menuNovoEstagio .dropdown-select-item')).map(e => e.textContent)") == ['Prospecção', 'Contato realizado', 'Proposta apresentada', 'Negociação'],
       'e o estagio inicial nao pode ser o que encerra')
    clic(pg, '#btnSalvarAssunto'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#novoErroCliente') and visivel(pg, '#novoErroTitulo') and pg.locator('#confirmModal.open').count() == 0, 'sem cliente e sem assunto nao salva, e diz os dois')
    escolher(pg, 'novoCliente', 11); pg.fill('#novoTitulo', 'Leitores de código de barras')
    # Criar segue a matriz do modulo: sem senha por padrao, a acao acontece direto.
    clic(pg, '#btnSalvarAssunto'); pg.wait_for_timeout(500); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok(pg.locator('#confirmModal.open').count() == 0, 'incluir nao pede senha por padrao')
    novo = pg.evaluate("Number(new URLSearchParams(location.search).get('id'))")
    ok('crm-detalhe' in pg.url and pg.inner_text('#assuntoTitulo') == 'Leitores de código de barras' and pg.inner_text('#cabNome') == 'Auto Peças Imperatriz Ltda',
       'assunto novo abre direto na tela dele: %s' % pg.url[-40:])
    ok(tempo(pg) == ['Assunto criado'] and 'Prospecção' in pg.inner_text('#estagios') and 'iniciado há 0 dias' in pg.inner_text('#cabTempo'), 'nasce em Prospeccao, com a criacao na linha do tempo')

    print('\n[7] Acoes: nova no cartao, editar no painel, concluir')
    ok('Nenhuma ação pendente' in pg.inner_text('#acoesPendentes') and not visivel(pg, '#formNova'), 'sem acao, a tela pede a proxima')
    clic(pg, '#btnIncluirAcao'); pg.wait_for_timeout(300)
    ok(visivel(pg, '#formNova') and pg.inner_text('#novaCont') == 'Você tem 256 caracteres restando.' and visivel(pg, '#novaBlocoData') and not visivel(pg, '#novaCampoHora'),
       'incluir acao abre o formulario no cartao, com data e sem horario')
    clic(pg, '#btnSalvarNova'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#novaErro') and 'Escreva' in pg.inner_text('#novaErro'), 'acao sem texto e barrada')
    pg.fill('#novaTexto', 'Mandar o catálogo de leitores'); pg.wait_for_timeout(150)
    ok(pg.inner_text('#novaCont') == 'Você tem 227 caracteres restando.', 'o contador desconta o que foi escrito: %s' % pg.inner_text('#novaCont'))
    # 09/out: o botao do calendario nao abria nada, porque o campo nasceu sem a caixa dele, e o Esc levava o formulario junto.
    pg.click('#novaDf .date-btn'); pg.wait_for_timeout(250)
    ok(pg.locator('#novaDf .date-pop.open').count() == 1 and pg.locator('#novaDf .date-dia[data-iso]').count() >= 28, 'o botao do calendario abre o mes')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.locator('#novaDf .date-pop.open').count() == 0 and visivel(pg, '#formNova') and pg.input_value('#novaTexto') == 'Mandar o catálogo de leitores',
       'Esc fecha o calendario e o formulario fica, com o que foi escrito')
    pg.click('#novaDf .date-btn'); pg.wait_for_timeout(250); pg.click('#novaDf .date-dia[data-iso]'); pg.wait_for_timeout(250)
    ok(pg.input_value('#novaData')[:3] == '01/' and pg.locator('#novaDf .date-pop.open').count() == 0, 'escolher o dia preenche a data e fecha: %s' % pg.input_value('#novaData'))
    pg.fill('#novaData', '31/02/2027'); clic(pg, '#btnSalvarNova'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#novaErro') and 'dd/mm/aaaa' in pg.inner_text('#novaErro'), 'data que nao existe e barrada')
    escolher(pg, 'novaPrevisto', 'quantoantes')
    ok(not visivel(pg, '#novaBlocoData'), '"quanto antes" esconde data e horario: campo que nao se aplica some')
    escolher(pg, 'novaPrevisto', 'data')
    pg.fill('#novaData', dma(1)); clic(pg, '#novaLinkHora'); pg.wait_for_timeout(150)
    ok(visivel(pg, '#novaCampoHora') and pg.inner_text('#novaLinkHora') == 'remover horário', '"adicionar horario" mostra o campo e vira "remover horario"')
    pg.click('#novaHf .date-btn'); pg.wait_for_timeout(250)
    agora = pg.input_value('#novaHora')
    ok(pg.locator('#novaHf .date-pop.open').count() == 1 and len(agora) == 5 and agora[4] in '05', 'o relogio abre as setas e parte da hora de agora: %s' % agora)
    pg.fill('#novaHora', '13:43'); pg.click('#novaHf [data-parte="m"][data-passo="1"]'); sobe = pg.input_value('#novaHora')
    pg.fill('#novaHora', '13:43'); pg.click('#novaHf [data-parte="m"][data-passo="-1"]'); desce = pg.input_value('#novaHora')
    pg.click('#novaHf [data-parte="h"][data-passo="-1"]')
    ok([sobe, desce, pg.input_value('#novaHora')] == ['13:45', '13:40', '12:40'] and pg.inner_text('#novaHf [data-num="h"]') == '12',
       'as setas mudam a hora de 1 em 1 e o minuto de 5 em 5: %s' % [sobe, desce, pg.input_value('#novaHora')])
    pg.fill('#novaHora', '23:55'); pg.click('#novaHf [data-parte="h"][data-passo="1"]'); pg.click('#novaHf [data-parte="m"][data-passo="1"]')
    ok(pg.input_value('#novaHora') == '00:00', 'e dao a volta em 23h e em 55min: %s' % pg.input_value('#novaHora'))
    pg.click('#novaDf .date-btn'); pg.wait_for_timeout(200)
    ok(pg.locator('#novaHf .date-pop.open').count() == 0 and pg.locator('#novaDf .date-pop.open').count() == 1, 'abrir o calendario fecha o horario: uma caixa por vez')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    pg.fill('#novaHora', '25:00'); clic(pg, '#btnSalvarNova'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#novaErro') and 'hh:mm' in pg.inner_text('#novaErro'), 'horario que nao existe e barrado')
    pg.fill('#novaHora', '14:30'); clic(pg, '#btnSalvarNova'); pg.wait_for_timeout(350)
    cartao = pg.inner_text('#acoesPendentes')
    ok(not visivel(pg, '#formNova') and 'Amanhã às 14:30' in cartao and 'Mandar o catálogo de leitores' in cartao and 'Concluir ação' in cartao, 'a acao salva vira cartao com o quando em palavras')
    ok(tempo(pg) == ['Ação pendente', 'Assunto criado'], 'e entra na linha do tempo como pendente: %s' % tempo(pg))
    clic(pg, '#acoesPendentes [data-editar-acao]'); pg.wait_for_timeout(350)
    ok(pg.locator('#acaoDrawer.open').count() == 1 and pg.inner_text('#acaoDrawer .drawer-title') == 'Ação do CRM' and pg.input_value('#acaoTexto') == 'Mandar o catálogo de leitores'
       and pg.input_value('#acaoData') == dma(1) and pg.input_value('#acaoHora') == '14:30', 'o lapis abre o painel "Acao do CRM" com o que foi salvo')
    pg.fill('#acaoData', dma(0)); clic(pg, '#acaoLinkHora'); clic(pg, '#btnSalvarEd'); pg.wait_for_timeout(350)
    ok(pg.locator('#acaoDrawer.open').count() == 0 and 'Hoje' in pg.inner_text('#acoesPendentes') and '14:30' not in pg.inner_text('#acoesPendentes'), 'editar para hoje, sem horario, muda o cartao')
    clic(pg, '#btnIncluirAcao'); pg.wait_for_timeout(250)
    pg.fill('#novaTexto', 'Confirmar o modelo do leitor'); escolher(pg, 'novaPrevisto', 'semdata'); clic(pg, '#btnSalvarNova'); pg.wait_for_timeout(350)
    ok(pg.locator('#acoesPendentes .crm-card').count() == 2 and pg.evaluate("document.querySelector('#acoesPendentes .crm-card .crm-quando').innerText") == 'Hoje',
       'com duas pendentes, a datada vem antes da sem data')
    clic(pg, '#acoesPendentes [data-concluir]'); pg.wait_for_timeout(350)
    ok(pg.locator('#acoesPendentes .crm-card').count() == 1 and tempo(pg)[:2] == ['Ação pendente', 'Ação concluída'], 'concluir tira dos pendentes e marca na linha do tempo: %s' % tempo(pg))
    clic(pg, '#abaCorpo [data-lt-excluir^="acao:"]'); pg.wait_for_timeout(350)
    ok(pg.locator('#confirmModal.open').count() == 1 and 'Excluir a ação' in pg.inner_text('#confirmModalTexto'), 'excluir uma acao pela linha do tempo pergunta antes')
    confirmar(pg, senha=False)
    ok(pg.locator('#acoesPendentes .crm-card').count() == 0 and tempo(pg) == ['Ação concluída', 'Assunto criado'], 'e a acao some dos dois lugares')

    print('\n[8] Estagio, encerrar com resultado e reabrir')
    ok(pg.inner_text('#btnProximoEstagio').strip() == 'Contato realizado', 'o atalho mostra o proximo estagio do funil')
    clic(pg, '#btnProximoEstagio'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#estagios .crm-estagio.atual') == 'Contato realizado' and tempo(pg)[0] == 'Estágio alterado', 'avancar muda o estagio e registra')
    itens = pg.evaluate("Array.from(document.querySelectorAll('#menuEstagios .dropdown-select-item')).map(e => e.textContent)")
    ok(itens == ['1. Prospecção', '2. Contato realizado', '3. Proposta apresentada', '4. Negociação', '5. Encerrado'], '"mais" lista os cinco estagios numerados')
    clic(pg, '#menuEstagios [data-acao="4"]'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#estagios .crm-estagio.atual') == 'Negociação' and pg.inner_text('#menuEstagios .dropdown-select-label') == 'mais', 'da para pular de estagio, e o botao continua "mais"')
    ok(pg.inner_text('#btnProximoEstagio').strip() == 'Encerrado', 'do penultimo, o proximo e o que encerra')
    clic(pg, '#btnProximoEstagio'); pg.wait_for_timeout(350)
    ok(pg.locator('#encerrarDrawer.open').count() == 1 and pg.evaluate('assunto.resultado') is None and not visivel(pg, '#encCampoMotivo'), 'ir para o ultimo estagio abre o painel de encerrar, sem encerrar ainda')
    clic(pg, '#btnConfirmarEncerrar'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#encErro') and 'ganho ou perdido' in pg.inner_text('#encErro'), 'encerrar sem dizer o resultado e barrado')
    clic(pg, 'input[name="encResultado"][value="perdido"]'); pg.wait_for_timeout(150)
    ok(visivel(pg, '#encCampoMotivo'), 'perdido mostra o motivo')
    clic(pg, '#btnConfirmarEncerrar'); pg.wait_for_timeout(250)
    ok('motivo' in pg.inner_text('#encErro') and pg.evaluate('assunto.resultado') is None, 'perdido sem motivo e barrado')
    clic(pg, 'input[name="encResultado"][value="ganho"]'); pg.wait_for_timeout(150)
    ok(not visivel(pg, '#encCampoMotivo'), 'ganho esconde o motivo')
    clic(pg, 'input[name="encResultado"][value="perdido"]'); escolher(pg, 'encMotivo', 'Prazo de entrega'); pg.fill('#encObs', 'Precisava para a semana que vem.')
    clic(pg, '#btnConfirmarEncerrar'); pg.wait_for_timeout(350)
    ok(pg.evaluate('assunto.resultado') == 'perdido' and 'PERDIDO · PRAZO DE ENTREGA' in pg.inner_text('#estagios').upper() and tempo(pg)[0] == 'Assunto encerrado',
       'encerrado como perdido, com o motivo, e registrado')
    ok(not visivel(pg, '#btnIncluirAcao') and not visivel(pg, '#linkIncluirAcao') and not visivel(pg, '#itemEncerrar'), 'assunto encerrado nao recebe acao nova nem pode ser encerrado de novo')
    clic(pg, '#btnReabrir'); pg.wait_for_timeout(300)
    ok(pg.evaluate('assunto.resultado') is None and pg.inner_text('#estagios .crm-estagio.atual') == 'Negociação' and tempo(pg)[0] == 'Assunto reaberto' and visivel(pg, '#btnIncluirAcao'),
       'reabrir volta para o estagio em que estava')

    print('\n[9] Proposta: registro do assunto')
    ok(pg.inner_text('#itemProposta') == 'Incluir proposta' and pg.locator('#cartaoProposta').count() == 0, 'sem proposta, o menu oferece incluir')
    acao_menu(pg, 'proposta')
    ok(pg.locator('#propostaDrawer.open').count() == 1 and pg.input_value('#propValidade') == dma(7) and not visivel(pg, '#btnRemoverProposta'), 'o painel abre com validade de 7 dias e sem "remover"')
    pg.click('#propDf .date-btn'); pg.wait_for_timeout(250)
    abriu = pg.locator('#propDf .date-pop.open').count() == 1
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(abriu and pg.locator('#propDf .date-pop.open').count() == 0 and pg.locator('#propostaDrawer.open').count() == 1, 'o calendario da validade abre, e o Esc fecha so ele')
    clic(pg, '#btnSalvarProposta'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#propErro') and 'valor' in pg.inner_text('#propErro'), 'proposta sem valor e barrada')
    pg.fill('#propValor', '1.500,00'); pg.fill('#propCondicoes', 'À vista no Pix.'); clic(pg, '#btnSalvarProposta'); pg.wait_for_timeout(350)
    cp = pg.inner_text('#cartaoProposta')
    ok('Proposta de R$ 1.500,00' in cp and 'APRESENTADA' in cp.upper() and dma(7) in cp and 'À vista no Pix.' in cp and tempo(pg)[0] == 'Proposta', 'a proposta vira cartao no assunto e entra na linha do tempo')
    ok(pg.inner_text('#itemProposta') == 'Editar proposta' and pg.locator('#btnPedidoDaProposta').count() == 0, 'o menu passa a editar, e ainda nao oferece pedido')
    clic(pg, '#btnEditarProposta'); pg.wait_for_timeout(300); escolher(pg, 'propSituacao', 'aceita'); clic(pg, '#btnSalvarProposta'); pg.wait_for_timeout(350)
    ok('ACEITA' in pg.inner_text('#cartaoProposta').upper() and pg.locator('#btnPedidoDaProposta').count() == 1 and 'aceita' in pg.evaluate('assunto.eventos.slice(-1)[0].texto'),
       'proposta aceita oferece "Incluir pedido de venda" e registra a mudanca')
    clic(pg, '#btnEditarProposta'); pg.wait_for_timeout(300); clic(pg, '#btnRemoverProposta'); pg.wait_for_timeout(300); confirmar(pg, senha=False)
    ok(pg.locator('#cartaoProposta').count() == 0 and pg.evaluate('assunto.proposta') is None, 'remover proposta pergunta e tira o cartao')

    print('\n[10] Anotacao, WhatsApp e e-mail')
    acao_menu(pg, 'anotacao')
    ok(pg.locator('#notaDrawer.open').count() == 1 and pg.inner_text('#notaTitulo') == 'Anotação' and not visivel(pg, '#btnAbrirCanal') and not visivel(pg, '#notaContato'), 'anotacao abre so com o texto')
    clic(pg, '#btnSalvarNota'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#notaErro'), 'anotacao vazia e barrada')
    pg.fill('#notaTexto', 'Cliente prefere contato à tarde.'); clic(pg, '#btnSalvarNota'); pg.wait_for_timeout(350)
    ok(tempo(pg)[0] == 'Anotação' and pg.locator('#abaCorpo [data-lt-editar^="evento:"]').count() == 1, 'a anotacao entra na linha do tempo e pode ser editada')
    clic(pg, '#abaCorpo [data-lt-editar^="evento:"]'); pg.wait_for_timeout(300)
    ok(pg.inner_text('#notaTitulo') == 'Editar anotação' and pg.input_value('#notaTexto') == 'Cliente prefere contato à tarde.', 'o lapis abre a anotacao para editar')
    pg.fill('#notaTexto', 'Cliente prefere contato de manhã.'); clic(pg, '#btnSalvarNota'); pg.wait_for_timeout(350)
    ok('de manhã' in pg.inner_text('#abaCorpo') and tempo(pg).count('Anotação') == 1, 'editar troca o texto, sem criar outra')
    acao_menu(pg, 'whatsapp')
    ok(pg.inner_text('#notaTitulo') == 'Enviar WhatsApp' and '(99) 3524-3320' in pg.inner_text('#notaContato') and pg.inner_text('#btnAbrirCanal') == 'Abrir o WhatsApp', 'WhatsApp mostra o numero do cliente')
    pg.fill('#notaTexto', 'Bom dia! Segue o catálogo.')
    ok(pg.evaluate('linkDoCanal()') == 'https://wa.me/559935243320?text=Bom%20dia!%20Segue%20o%20cat%C3%A1logo.', 'o link abre o WhatsApp do cliente com a mensagem: %s' % pg.evaluate('linkDoCanal()')[:60])
    clic(pg, '#btnSalvarNota'); pg.wait_for_timeout(350)
    ok(tempo(pg)[0] == 'WhatsApp' and pg.locator('#abaCorpo [data-lt-editar^="evento:"]').count() == 1, 'registrar guarda o contato na linha do tempo; so anotacao e editavel')
    acao_menu(pg, 'email')
    pg.fill('#notaTexto', 'Proposta em anexo.')
    ok(pg.evaluate('linkDoCanal()').startswith('mailto:contato@autopecasimp.com.br?subject=Leitores') and pg.inner_text('#btnAbrirCanal') == 'Abrir o e-mail', 'e-mail abre o programa de e-mail com o assunto')
    clic(pg, '#btnSalvarNota'); pg.wait_for_timeout(350)
    ok(tempo(pg)[0] == 'E-mail', 'e o e-mail fica registrado')

    print('\n[11] Abas vendas e financeiro leem dos espelhos')
    ir(pg, DET, '?id=3')
    clic(pg, '#abasAssunto [data-aba="vendas"]'); pg.wait_for_timeout(250)
    v = pg.inner_text('#abaCorpo')
    ok('ÚLTIMOS CINCO PEDIDOS' in v.upper() and 'R$ 8.975,30' in v and 'Entregue' in v, 'vendas lista os pedidos do cliente: %s' % v.replace(chr(10), ' ')[:90])
    clic(pg, '#abasAssunto [data-aba="financeiro"]'); pg.wait_for_timeout(250)
    f = pg.inner_text('#abaCorpo')
    ok('PV 13' in f and 'R$ 8.975,30' in f and 'ATRASADA' in f.upper(), 'financeiro lista a conta em aberto do cliente, atrasada')
    ir(pg, DET, '?id=1')
    clic(pg, '#abasAssunto [data-aba="vendas"]'); pg.wait_for_timeout(250)
    ok(pg.locator('#abaCorpo .crm-tab tbody tr').count() == pg.evaluate("Math.min(5, PEDIDOS_ESPELHO.filter(p => p.cliente === 'Camila Rêgo').length)") >= 1, 'outro cliente, outros pedidos: so os dele, no maximo cinco')
    clic(pg, '#abasAssunto [data-aba="financeiro"]'); pg.wait_for_timeout(250)
    ok('Não há contas em aberto' in pg.inner_text('#abaCorpo'), 'cliente sem conta em aberto diz isso')
    ir(pg, DET, '?id=999')
    ok(visivel(pg, '#assuntoAusente') and not visivel(pg, '#assuntoCorpo'), 'assunto que nao existe mostra o aviso, em vez de tela vazia')
    ir(pg, DET)
    ok(visivel(pg, '#assuntoCorpo') and pg.inner_text('#assuntoTitulo') == pg.evaluate('ASSUNTOS[0].titulo'), 'a tela aberta sem numero de assunto mostra o primeiro, com os botoes ligados')

    print('\n[12] A proxima acao com data vira aviso na Agenda')
    zerar(pg)
    av = pg.evaluate("JSON.parse(localStorage.getItem('deskAvisos') || '{}')")
    crm = dict((k, x) for k, x in av.items() if k.startswith('crm:'))
    ok(sorted(crm) == ['crm:1:11', 'crm:2:21', 'crm:3:31'], 'so acao pendente COM data, de assunto aberto, vira aviso: %s' % sorted(crm))
    a1 = crm.get('crm:1:11', {})
    ok(a1.get('data') == HOJE.isoformat() and a1.get('hora') == '15:00' and 'Camila' in a1.get('meta', '') and a1.get('href', '').endswith('pagina-vendas-crm-detalhe.html?id=1'),
       'o aviso leva data, hora, cliente e o caminho do assunto')
    pa = ctx.new_page()
    ea = []
    pa.on('pageerror', lambda e: ea.append(str(e)))
    ir(pa, AGENDA)
    na = pa.evaluate("Object.keys(EVENTOS_POR_DIA).reduce((n, k) => n + EVENTOS_POR_DIA[k].filter(e => (e.href || '').indexOf('crm-detalhe') !== -1).length, 0)")
    hoje_ag = pa.evaluate("(EVENTOS_POR_DIA['%s'] || []).filter(e => (e.href || '').indexOf('crm-detalhe') !== -1).map(e => e.hora + ' ' + e.titulo)" % HOJE.isoformat())
    ok(na == 3 and hoje_ag == ['15:00 Ligar para apresentar o catálogo de cadeiras'], 'a Agenda recebe os tres avisos, e o de hoje esta no dia de hoje: %s' % hoje_ag)
    ir(pg, DET, '?id=1')
    clic(pg, '#acoesPendentes [data-concluir]'); pg.wait_for_timeout(350)
    ok('crm:1:11' not in pg.evaluate("JSON.parse(localStorage.getItem('deskAvisos') || '{}')"), 'concluir a acao tira o aviso da Agenda')
    pa.close()

    print('\n[13] Quadro por estagio')
    zerar(pg)
    clic(pg, '#visaoCrm [data-visao="quadro"]'); pg.wait_for_timeout(300)
    col = pg.evaluate("Array.from(document.querySelectorAll('#quadroCrm .crm-col')).map(c => c.querySelector('.crm-col-topo').childNodes[0].textContent + ':' + c.querySelectorAll('.crm-cartao').length)")
    ok(visivel(pg, '#visaoQuadro') and not visivel(pg, '#visaoLista') and col == ['Prospecção:2', 'Contato realizado:2', 'Proposta apresentada:1', 'Negociação:1', 'Encerrado:2'],
       'uma coluna por estagio, na ordem do funil, com os assuntos: %s' % col)
    ok(pg.evaluate("document.documentElement.scrollWidth") <= 1440 and pg.evaluate("(() => { const w = document.querySelector('.crm-quadro-wrap'); return w.scrollWidth <= w.clientWidth + 1; })()"),
       'as cinco colunas cabem em 1440')
    # 09/out: "Perdido · Prazo de entrega" e "avancar" com seta nao cabiam no cartao: vazavam e criavam a barra de rolagem.
    # Pior caso: o motivo mais longo, horario em toda acao e a coluna na largura minima (1280).
    pg.evaluate("ASSUNTOS.forEach(a => { if (a.resultado === 'perdido') a.motivoPerda = 'Comprou do concorrente'; a.acoes.forEach(x => { if (x.data && !x.concluidaEm) x.hora = '15:00'; }); }); pintar();")
    VAZA = '''() => { const f = []; document.querySelectorAll('#quadroCrm .crm-cartao').forEach(c => { const lim = c.getBoundingClientRect().right + 0.5;
        c.querySelectorAll('*').forEach(e => { if (e.getBoundingClientRect().right > lim) f.push(e.textContent.slice(0, 24)); }); }); return f; }'''
    pg.wait_for_timeout(250); fora = pg.evaluate(VAZA)
    ok(not fora and pg.evaluate("(() => { const w = document.querySelector('.crm-quadro-wrap'); return w.scrollWidth <= w.clientWidth + 1; })()"),
       'com o motivo mais longo e horario em toda acao, nenhum texto sai do cartao e o quadro nao rola: %s' % fora[:3])
    pg.set_viewport_size({'width': 1280, 'height': 900}); pg.wait_for_timeout(250); fora = pg.evaluate(VAZA)
    pg.set_viewport_size({'width': 1440, 'height': 900}); pg.wait_for_timeout(250)
    ok(not fora, 'nem com a coluna na largura minima, em 1280: %s' % fora[:3])
    ok(pg.evaluate("Array.from(new Set(Array.from(document.querySelectorAll('#quadroCrm [data-avancar]')).map(b => b.textContent))).sort()") == ['Avançar', 'Encerrar'],
       'o botao do cartao diz so "Avancar" ou "Encerrar", sem seta')
    ok(pg.evaluate("document.querySelector('.crm-cartao[data-id=\"6\"]').getAttribute('draggable')") is None and pg.locator('.crm-cartao[data-id="6"] [data-avancar]').count() == 0,
       'assunto encerrado nao e arrastado nem avanca')
    clic(pg, '#quadroCrm [data-avancar="1"]'); pg.wait_for_timeout(300)
    ok(pg.evaluate("assuntoDe(1).estagioId") == 2 and pg.evaluate("document.querySelector('.crm-cartao[data-id=\"1\"]').closest('.crm-col').getAttribute('data-estagio')") == '2',
       '"avancar" passa o cartao para a coluna seguinte')
    pg.evaluate("moverParaEstagio(assuntoDe(1), 4)"); pg.wait_for_timeout(300)
    ok(pg.evaluate("assuntoDe(1).estagioId") == 4 and pg.evaluate("assuntoDe(1).eventos.slice(-1)[0].tipo") == 'estagio', 'soltar numa coluna muda o estagio e registra')
    clic(pg, '#quadroCrm [data-avancar="1"]'); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    ok('crm-detalhe' in pg.url and 'encerrar=1' in pg.url and pg.locator('#encerrarDrawer.open').count() == 1 and pg.evaluate('assunto.resultado') is None,
       'mandar para o ultimo estagio leva ao assunto, com o painel de encerrar aberto')
    clic(pg, 'input[name="encResultado"][value="ganho"]'); clic(pg, '#btnConfirmarEncerrar'); pg.wait_for_timeout(350)
    ok(pg.evaluate('assunto.resultado') == 'ganho' and 'GANHO' in pg.inner_text('#assuntoChips').upper(), 'e encerrar como ganho nao pede motivo')

    print('\n[14] O parametro de dias sem interacao nasce na tela de Configuracoes, e o CRM obedece')
    zerar(pg)
    padrao = pg.evaluate('PARAM_PADRAO.crmDiasSemInteracao')
    p2 = ctx.new_page()
    e2 = []
    p2.on('pageerror', lambda e: e2.append(str(e)))
    ir(p2, CFG)
    ok(p2.evaluate('PARAM_PADRAO.crmDiasSemInteracao') == padrao == 30 and p2.input_value('#diasSem') == '30' and 'Nenhuma alteração pendente' in p2.inner_text('#notaBarra'),
       'a chave existe nas duas telas, com o padrao de 30 dias')
    p2.fill('#diasSem', '0'); p2.wait_for_timeout(150)
    clic(p2, '#btnSalvarParam'); p2.wait_for_timeout(300)
    ok('1 a 365' in p2.inner_text('#avisoTexto') and p2.evaluate("(JSON.parse(localStorage.getItem('deskParametros') || '{}')).crmDiasSemInteracao") is None, 'prazo fora de 1 a 365 nao salva')
    p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    p2.fill('#diasSem', '50'); p2.wait_for_timeout(150)
    ok('50 dias' in p2.inner_text('#previaDias') and '1 configuração alterada' in p2.inner_text('#notaBarra'), 'a previa diz a consequencia e a nota conta a mudanca')
    clic(p2, '#btnSalvarParam'); p2.wait_for_timeout(300); p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    ok(p2.evaluate("JSON.parse(localStorage.getItem('deskParametros')).crmDiasSemInteracao") == 50 and 'Nenhuma alteração pendente' in p2.inner_text('#notaBarra'), 'salvar grava o parametro e zera a nota')
    pg.reload(); pg.wait_for_load_state('load'); pg.wait_for_timeout(600)
    ok('SEM INTERAÇÃO' not in pg.inner_text('#listaCrm').upper(), 'com 50 dias, o assunto parado ha 40 deixa de ser avisado')
    ir(pg, DET, '?id=4')
    ok('SEM INTERAÇÃO' not in pg.inner_text('#assuntoChips').upper() and pg.evaluate('PARAM.crmDiasSemInteracao') == 50, 'e a tela do assunto le o mesmo parametro')
    zerar(pg)
    ir(pg, DET, '?id=4')
    ok('SEM INTERAÇÃO HÁ 40 DIAS' in pg.inner_text('#assuntoChips').upper(), 'de volta aos 30 dias, o aviso aparece no topo do assunto')

    print('\n[15] Estagios do funil: a ordem e o dado')
    ir(p2, EST)
    def ordem(): return p2.evaluate("Array.from(document.querySelectorAll('#listaEstagios .ef-linha')).map(l => l.querySelector('.ef-num').innerText + ' ' + l.querySelector('.ef-nome').childNodes[0].textContent)")
    ok(ordem() == ['1 Prospecção', '2 Contato realizado', '3 Proposta apresentada', '4 Negociação', '5 Encerrado'] and 'ENCERRA O ASSUNTO' in p2.inner_text('#listaEstagios .ef-linha:last-child').upper(),
       'os cinco estagios numerados, e o ultimo marcado como o que encerra')
    bot = p2.evaluate("Array.from(document.querySelectorAll('#listaEstagios .ef-linha')).map(l => Array.from(l.querySelectorAll('.ef-seta')).map(b => b.disabled ? 0 : 1).join(''))")
    ok(bot == ['01', '11', '11', '10', '00'], 'o primeiro nao sobe, o penultimo nao desce e o ultimo nao se move: %s' % bot)
    clic(p2, '#listaEstagios [data-descer="0"]'); p2.wait_for_timeout(200)
    ok(ordem()[:2] == ['1 Contato realizado', '2 Prospecção'], 'a seta troca a ordem e renumera')
    ok(p2.evaluate('mover(1, 4)') is False and p2.evaluate('mover(4, 0)') is False and ordem()[-1] == '5 Encerrado', 'ninguem passa para depois do ultimo, e o ultimo nao sai do fim')
    ok(p2.evaluate('mover(1, 0)') is True and ordem()[0] == '1 Prospecção', 'arrastar para cima devolve a ordem')
    clic(p2, '#btnNovoEstagio'); p2.wait_for_timeout(300)
    clic(p2, '#efSalvar'); p2.wait_for_timeout(200)
    ok(visivel(p2, '#efErro'), 'estagio sem descricao e barrado')
    p2.fill('#efNome', 'negociacao'); clic(p2, '#efSalvar'); p2.wait_for_timeout(200)
    ok('Já existe' in p2.inner_text('#efErro'), 'descricao repetida e barrada, mesmo sem acento')
    p2.fill('#efNome', 'Demonstração feita'); clic(p2, '#efSalvar'); p2.wait_for_timeout(400)
    ok(p2.locator('#confirmModal.open').count() == 0 and p2.locator('#efDrawer.open').count() == 0, 'incluir estagio nao pede senha por padrao')
    ok(ordem()[-2:] == ['5 Demonstração feita', '6 Encerrado'], 'o estagio novo entra antes do ultimo: %s' % ordem()[-2:])
    clic(p2, '#listaEstagios .ef-linha:nth-child(2)'); p2.wait_for_timeout(300); clic(p2, '#efExcluir'); p2.wait_for_timeout(500)
    ok('2 assuntos' in p2.inner_text('#avisoTexto') and 'não pode ser excluído' in p2.inner_text('#avisoTexto'), 'estagio com assunto dentro nao e excluido, e a tela diz quantos')
    p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    clic(p2, '#listaEstagios .ef-linha:last-child'); p2.wait_for_timeout(300); clic(p2, '#efExcluir'); p2.wait_for_timeout(500)
    ok('encerra o assunto' in p2.inner_text('#avisoTexto'), 'o estagio que encerra tambem nao, e a tela explica')
    p2.keyboard.press('Escape'); p2.wait_for_timeout(250)
    clic(p2, '#listaEstagios .ef-linha:nth-child(5)'); p2.wait_for_timeout(300); clic(p2, '#efExcluir'); p2.wait_for_timeout(400)
    ok(p2.locator('#confirmModal.open').count() == 1 and visivel(p2, '#campoSenhaModal'), 'excluir estagio sem uso pede senha')
    confirmar(p2)
    ok(len(ordem()) == 5 and 'Demonstração feita' not in ' '.join(ordem()), 'com a senha, o estagio sai do funil')

    print('\n[16] Tudo que o CRM le de outro cadastro bate com o cadastro')
    ir(p2, EST)
    cad_est = p2.evaluate("ESTAGIOS.map(e => [e.id, e.nome, !!e.final, e.usos])")
    zerar(pg)
    crm_est = pg.evaluate("ESTAGIOS.map(e => [e.id, e.nome, !!e.final, ASSUNTOS.filter(a => a.estagioId === e.id).length])")
    ok(cad_est == crm_est, 'estagios: mesma ordem, mesmo nome, o mesmo que encerra e a contagem de assuntos de cada um: %s' % [x for x in cad_est if x not in crm_est])
    ir(pg, DET, '?id=1')
    ok(pg.evaluate("ESTAGIOS.map(e => [e.id, e.nome, !!e.final])") == [x[:3] for x in cad_est], 'a tela do assunto carrega os mesmos estagios')
    crm_cli = pg.evaluate("CLIENTES.map(c => [c.id, c.nome, c.documento, c.email, c.telefone, c.contato, c.status])")
    crm_vend = pg.evaluate("VENDEDORES")
    esp_ped = pg.evaluate("PEDIDOS_ESPELHO.map(p => [p.id, p.numero, p.cliente, p.dv, p.total, p.situacao])")
    esp_tit = pg.evaluate("TITULOS_ESPELHO")
    sit = pg.evaluate("SIT_PEDIDO")
    ir(p2, CLI)
    ok(p2.evaluate("CLIENTES.map(c => [c.id, c.nome, c.documento, c.email, c.telefone, c.contato, c.status])") == crm_cli, 'clientes: os 14, com documento, e-mail, telefone, status do contato e situacao')
    tags = p2.evaluate("Array.from(document.querySelectorAll('.cliente-card [data-contato]')).map(e => e.innerText.trim().toLowerCase())")
    ok(len(tags) > 0 and set(tags) <= {'lead', 'prospect', 'cliente'}, 'a lista de Clientes mostra o status do contato em cada linha: %s' % sorted(set(tags)))
    ir(p2, CLI_DET)
    ok(p2.evaluate("Array.from(document.querySelectorAll('#inputContato .dropdown-select-item')).map(e => e.getAttribute('data-value'))") == ['lead', 'prospect', 'cliente'],
       'e o cadastro do cliente tem o campo Status do contato, com as tres opcoes')
    ir(p2, METAS)
    ok(p2.evaluate("VENDEDORES") == crm_vend, 'vendedores iguais aos de Metas')
    ir(p2, PEDIDOS)
    ok(p2.evaluate("PEDIDOS.map(p => [p.id, p.numero, p.cliente, p.dv, p.total, p.situacao])") == esp_ped and
       p2.evaluate("SITUACOES.reduce((m, s) => { m[s.id] = s.rotulo; return m; }, {})") == sit, 'pedidos e nomes de situacao iguais aos de Pedidos de Venda')
    ir(p2, RECEBER)
    cr = p2.evaluate("TITULOS.filter(t => t.venc !== undefined && !t.cancelado && t.recebido < t.valor).map(t => ({ cliente: CLIENTES.filter(c => c.id === t.cliId)[0].nome, doc: t.doc || 'Sem documento', venc: t.venc, valor: t.valor, recebido: t.recebido }))")
    ok(all(t in cr for t in esp_tit) and len(esp_tit) > 0, 'toda conta em aberto do espelho existe em Contas a Receber, com cliente, vencimento e valor')

    print('\n[17] Os modulos estao na matriz de senhas')
    acoes = pg.evaluate("ACOES_SENHA.filter(a => a.chave.indexOf('crm') === 0).map(a => a.chave + '/' + a.exigePadrao)")
    ok(sorted(acoes) == ['crmCriar/false', 'crmEditar/false', 'crmExclui/true'], 'criar e editar sem senha por padrao, excluir com: %s' % sorted(acoes))
    for arq in CATALOGOS:
        txt = open(localiza.onde(arq), encoding='utf-8').read()
        ok("base:'crm'" in txt and "base:'estagiosFunil'" in txt, '%s conhece os modulos CRM e Estagios do funil' % arq.replace('pagina-', ''))
    p2.close()

    print('\n[18] O relogio do horario tambem esta na Agenda')
    # 09/out: a Agenda usava dois dropdowns (hora, e minuto de 15 em 15). O usuario pediu o mesmo
    # relogio do CRM la, para o sistema ter um jeito so de informar horario.
    ir(pg, DET, '?id=2')
    relogio_crm = pg.evaluate('inicializarHoraField.toString()')
    ir(pg, AGENDA)
    ok(pg.evaluate('inicializarHoraField.toString()') == relogio_crm and pg.locator('#formHora, #formMin').count() == 0, 'a Agenda usa o mesmo componente da tela do assunto, e os dois dropdowns sairam')
    pg.evaluate("abrirFormulario('2026-10-15')"); pg.wait_for_timeout(450)
    ok(pg.input_value('#formHorario') == '09:00' and pg.locator('#hfAgenda .date-pop.open').count() == 0, 'compromisso novo abre as 09:00, com a caixa fechada')
    pg.click('#hfAgenda .date-btn'); pg.wait_for_timeout(250)
    pg.click('#hfAgenda [data-parte="h"][data-passo="1"]'); pg.click('#hfAgenda [data-parte="m"][data-passo="-1"]')
    ok(pg.locator('#hfAgenda .date-pop.open').count() == 1 and pg.input_value('#formHorario') == '10:55' and pg.inner_text('#hfAgenda [data-num="m"]') == '55',
       'o relogio abre e as setas mudam o campo: %s' % pg.input_value('#formHorario'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.locator('#hfAgenda .date-pop.open').count() == 0 and pg.locator('.event-drawer.open').count() == 1, 'Esc fecha a caixa e o painel do compromisso fica')
    pg.fill('#formDescricao', 'Visita ao cliente'); pg.evaluate("document.querySelector('.user-checkbox').click()")
    pg.fill('#formHorario', '25:99'); clic(pg, '#formSalvar'); pg.wait_for_timeout(250)
    ok(visivel(pg, '#erroHorario') and pg.locator('.event-drawer.open').count() == 1, 'horario que nao existe nao salva: agora o campo e digitavel')
    pg.fill('#formHorario', '14:30'); pg.wait_for_timeout(150)
    limpou = not visivel(pg, '#erroHorario')
    clic(pg, '#formSalvar'); pg.wait_for_timeout(300)
    ok(limpou and pg.locator('.event-drawer.open').count() == 0, 'corrigir limpa o erro, e o compromisso salva')

    print('\n[19] Esc, os dois temas, largura e erro de JS')
    zerar(pg)
    clic(pg, '#btnIncluirAssunto'); pg.wait_for_timeout(300)
    clic(pg, '#novoCliente .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#assuntoDrawer.open').count() == 1 and pg.locator('#menuNovoCliente.open').count() == 0, 'o primeiro Esc fecha so o menu aberto')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#assuntoDrawer.open').count() == 0, 'e o segundo fecha o painel')
    for tela, q in [(LISTA, ''), (DET, '?id=2')]:
        ir(pg, tela, q)
        for tema in ['claro', 'escuro']:
            pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
            pg.wait_for_timeout(220)
            ok(pg.evaluate('document.documentElement.scrollWidth') <= 1440, '%s, tema %s: nao estoura em 1440' % (tela.replace('pagina-vendas-', ''), tema))
    acao_menu(pg, 'anotacao')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(pg.locator('#notaDrawer.open').count() == 0, 'Esc fecha o painel do assunto')
    acao_menu(pg, 'outros')
    ok(pg.locator('#outrosDrawer.open').count() == 1 and 'não tem outro assunto' in pg.inner_text('#outrosCorpo'), '"outros assuntos" diz quando o cliente so tem este')
    ok(pg.inner_text('#menuMaisAcoes .dropdown-select-label') == 'Mais ações' and pg.locator('#menuMaisAcoes .dropdown-select-item.active').count() == 0, 'e o botao continua "Mais ações", sem item marcado')
    ok(not erros and not e2 and not ea, 'sem erro de JS: %s' % (erros + e2 + ea)[:2])

    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
