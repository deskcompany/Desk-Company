# -*- coding: utf-8 -*-
# Custos do E-commerce, entrega 4 (decidida em 30/out/2026): a embalagem do pedido nasce na Separacao, a Conferencia de Saida confirma, e Custos le o que foi confirmado.
#
# O que ele protege sao as decisoes do usuario, as que "simplificar" apaga primeiro:
#   Cadastro de Embalagens ganha CUSTO e o tipo INSUMO (tag, fita, saco): sem medidas, sem peso, sem "cabe ate"; o insumo pode entrar sozinho em todas as lojas ou numa so
#   Separacao: antes de concluir o separador escolhe a embalagem; a menor caixa que cabe vem sugerida e os insumos automaticos ja vem preenchidos;
#              ele ve so os NOMES, nunca o custo (nem um "R$" no bloco)
#   Conferencia de Saida: recebe preenchido e confirma; pode trocar, com registro (a troca vai para o Registro de atividades); VALE O QUE ELA CONFIRMOU
#   O pedido guarda o CUSTO DO DIA: mudar o preco no cadastro depois nao mexe no pedido antigo
#   Custos e a pagina do pedido mostram a embalagem confirmada com os nomes; o pedido ainda nao confirmado usa o valor da loja e diz "estimada"
#   Sugestao de pedido grande: se nenhuma embalagem couber, a de maior capacidade, em quantas unidades forem precisas (e nunca um envelope)
#
#   [1]  Cadastro: custo, tipo Insumo (esconde medidas e peso, mostra "Entra sozinho"), erro em custo invalido, persiste ao recarregar;
#   [2]  Separacao do pedido 4: sugestao, insumos automaticos, nenhum R$, trocar/adicionar/remover, sem embalagem trava, falta muda a sugestao, rascunho, devolver, pedido grande;
#   [3]  O pedido 4 so aparece na Conferencia depois de concluido; vem preenchido; confirmar sem troca grava 'confirmada' com o custo do cadastro; reabrir mostra conferido;
#   [4]  Com troca: o registro tem as trocas, o modal cita, e cai no Registro de atividades;
#   [5]  Custos: o pedido 4 confirmado (7,20, sem "estimada", com os nomes; lucro 161,40) e os numeros do mes antes e depois;
#   [6]  O custo do dia: mudar o cadastro nao mexe no 4; o 16 usa 11,90 com o cadastro em 12,50; um pedido confirmado depois usa o preco novo;
#   [7]  Configurar muda so os estimados;
#   [8]  A pagina do pedido: o 11 com os nomes, o 1 "estimada", o 4 com a troca;
#   [9]  As copias: o bloco EMBALAGENS: LEITURA nas 3 telas, o da Conferencia nas 2, o pedido 4 igual nas FILAs;
#   [10] O layout do bloco a 1280 e 860 px, sem barra horizontal.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys, datetime
import localiza
from decimal import Decimal
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
CAD = 'pagina-cadastros-embalagens.html'
SEP, SEP_F = 'pagina-logistica-separacao.html', 'pagina-logistica-separacao-detalhe.html'
CONF, CONF_F = 'pagina-logistica-conferencia-saida.html', 'pagina-logistica-conferencia-saida-detalhe.html'
CUSTOS = 'pagina-vendas-custos-ecommerce.html'
PV_D = 'pagina-vendas-pedidos-detalhe.html'
FIXO = datetime.datetime(2026, 10, 30, 10, 0, 0)   # sexta: o mes, o periodo e os anuncios nao dependem do dia em que a suite roda

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


from oraculo_custos import D, c2, oraculo, EMB_CONFIRMADA, embalagem_do_pedido

br = lambda v: ('− ' if float(v) < 0 else '') + 'R$ ' + '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')
perto = lambda a, b: abs(float(a) - float(b)) < 0.005
erros = []


def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e


def fonte(n):
    return open(localiza.onde(n), encoding='utf-8').read()


def bloco(t, ini, fim):
    a = t.index(ini)
    return t[a:t.index(fim, a) + len(fim)]


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)

    def nova(w=1440, h=950, fixo=True):
        """Uma aba num contexto novo: localStorage limpo, e o relogio na sexta 30/10/2026."""
        pg = nav.new_context(viewport={'width': w, 'height': h}).new_page()
        pg.on('pageerror', lambda e: erros.append(str(e)[:200]))
        pg.on('console', lambda m: erros.append(m.text[:200]) if m.type == 'error' and not ruido(m.text) else None)
        if fixo:
            pg.clock.set_fixed_time(FIXO)
        return pg

    def ir(pg, tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def confirmar(pg):
        pg.evaluate('() => window.scrollTo(0, 0)')
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)

    def modal(pg):
        return pg.locator('#confirmModalTexto').inner_text()

    def ls(pg, chave):
        return pg.evaluate("(k) => JSON.parse(localStorage.getItem(k) || 'null')", chave)

    def reg(pg, i=4):
        return (ls(pg, 'deskEmbalagensPedido') or {}).get(str(i))

    def escolher(pg, raiz, valor):
        """Escolhe um item do dropdown da casa pelo valor (a raiz e o seletor do .dropdown-select)."""
        pg.evaluate("([r, v]) => document.querySelector(r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
        pg.wait_for_timeout(250)

    # ---- a Separacao
    def linhas_sep(pg, lista):
        return pg.evaluate("(l) => Array.from(document.querySelectorAll('#' + l + ' .emb-linha')).map(x => [x.querySelector('.dropdown-select-label').textContent.trim(), x.querySelector('input').value, !!x.querySelector('.emb-sugerida')])", lista)

    def bipar_tudo(pg, skus=('VES-2001', 'PAP-3001', 'VES-2002')):
        for s in skus:
            pg.fill('#campoBipar', s); pg.press('#campoBipar', 'Enter')
        pg.wait_for_timeout(250)

    def concluir_sep(pg):
        pg.click('#btnConcluir'); pg.wait_for_timeout(300)
        t = modal(pg)
        confirmar(pg); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        return t

    def separar4(pg, antes=None):
        ir(pg, SEP_F, '?id=4')
        bipar_tudo(pg)
        if antes: antes()
        return concluir_sep(pg)

    # ---- a Conferencia
    def volumes_conf(pg):
        return pg.evaluate("Array.from(document.querySelectorAll('#listaVolumes .vol-linha')).map(x => [x.querySelector('.dropdown-select-label').textContent.trim(), (x.querySelector('.vol-sugerida') || { textContent: '' }).textContent.trim()])")

    AVISO = ['']

    def conferir4(pg, antes=None):
        """Abre a bancada do 4, confirma a contagem da separacao, deixa `antes` mexer na embalagem e fecha. Devolve o texto do modal de fechar."""
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        if antes: antes()
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        t = modal(pg)
        confirmar(pg)          # fecha a conferencia
        AVISO[0] = modal(pg)
        confirmar(pg)          # o aviso final
        return t

    # ---- Custos
    def abrir_custos(pg, q=''):
        ir(pg, CUSTOS, q)

    def linha_pedido(pg, n):
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaCustos thead th')).filter(th => getComputedStyle(th).display !== 'none').map(th => th.textContent.replace(/[▲▼]/g, '').replace(/\\s+/g, ' ').trim())")
        cel = pg.evaluate("(n) => { const tr = document.querySelector('#corpoTabela tr[data-id=\"' + n + '\"]'); return tr ? Array.from(tr.children).filter(td => getComputedStyle(td).display !== 'none').map(td => td.innerText.replace(/\\s+/g, ' ').trim()) : null; }", n)
        return dict(zip(cab, cel)) if cel else None

    def todos_custos(pg):
        return pg.evaluate("PEDIDOS.map(p => Object.assign({}, p, { ind: p.ind || null }))")

    def kpis(pg):
        return pg.evaluate("[kpiFaturamento, kpiCustos, kpiLucro, kpiMargem, kpiAnuncios, kpiLucroAnuncios].map(e => e.textContent)")

    # ================================================================ 1. cadastro
    if secao(1, 'Cadastro: custo, tipo Insumo, erro em custo inválido, persiste ao recarregar'):
        pg = nova()
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        metas = pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-card')).map(c => [c.querySelector('.embalagens-nome').textContent, c.querySelector('.embalagens-meta').textContent, c.querySelector('.tipo-badge').textContent])")
        ok(len(metas) == 14, 'o padrão de fábrica tem as 10 de antes e os 4 insumos: %d' % len(metas))
        m = {x[0]: x for x in metas}
        ok(m['Caixa de Encomenda Flex P'][1] == '26,0×21,0×1,0cm · 0,09 Kg · R$ 3,50' and m['Caixa para Eletrônicos'][1] == '40,0×30,0×30,0cm · 1,20 Kg · R$ 12,50', 'a linha de baixo mostra medidas, peso e custo: %s' % m['Caixa de Encomenda Flex P'][1])
        ok(m['Tag Desk Shope'][1] == 'R$ 0,40 · entra sozinho: Desk Shope' and m['Tag Desk Brands'][1] == 'R$ 0,60 · entra sozinho: Desk Brands'
           and m['Fita adesiva'][1] == 'R$ 0,30 · entra sozinho: todas as lojas' and m['Saco plástico'][1] == 'R$ 0,25', 'o insumo mostra o custo e onde entra sozinho (e só o custo, se não entra): %s' % [m[k][1] for k in ('Tag Desk Shope', 'Fita adesiva', 'Saco plástico')])
        ok(m['Tag Desk Shope'][2] == 'INSUMO' and m['Rolo para Tecido'][1].startswith('Ø12,0×120,0cm'), 'o tipo Insumo tem a etiqueta, e o rolo segue com o diâmetro')
        ok([x['v'] for x in pg.evaluate("Array.from(document.querySelectorAll('#filtroTipo .dropdown-select-item')).map(i => ({ v: i.getAttribute('data-value') }))")] == ['todos', 'pacote', 'envelope', 'rolo', 'insumo'], 'o filtro de tipo ganhou "Insumo"')
        escolher(pg, '#filtroTipo', 'insumo')
        ok(pg.locator('#listaEmbalagens .embalagens-card').count() == 4, 'filtrar por Insumo traz os 4')
        escolher(pg, '#filtroTipo', 'todos')
        # novo cadastro: o tipo Insumo esconde o que nao serve
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        vis = lambda i: pg.evaluate("(i) => document.getElementById(i).getClientRects().length > 0", i)
        ok(vis('blocoMedidas') and vis('campoPeso') and vis('campoCap') and not vis('campoAuto') and vis('campoCusto'), 'caixa: medidas, peso, "cabe até" e custo aparecem; "entra sozinho" não')
        ok([x.strip() for x in pg.locator('#inputTipoEmbalagem .dropdown-select-item').all_inner_texts()] == ['Pacote / Caixa', 'Envelope', 'Rolo / Cilindro', 'Insumo'], 'o tipo do formulário ganhou "Insumo"')
        escolher(pg, '#inputTipoEmbalagem', 'insumo')
        ok(not vis('blocoMedidas') and not vis('campoPeso') and not vis('campoCap') and vis('campoAuto') and vis('campoCusto'), 'insumo: sem medidas, sem diagrama, sem peso e sem "cabe até"; mostra "Entra sozinho no pedido" e o custo')
        ok([x.strip() for x in pg.locator('#inputAuto .dropdown-select-item').all_inner_texts()] == ['Não, o separador adiciona', 'Em todas as lojas', 'Desk Shope', 'Desk Brands', 'Desk Tech'], 'as opções de "Entra sozinho no pedido"')
        escolher(pg, '#inputTipoEmbalagem', 'rolo')
        ok(vis('blocoMedidas') and vis('campoPeso') and not vis('campoCap'), 'rolo tem medidas e peso, mas não tem "cabe até"')
        escolher(pg, '#inputTipoEmbalagem', 'insumo')
        # custo invalido: avisa e nao salva
        pg.fill('#inputNomeEmbalagem', 'Etiqueta de teste')
        antes = len(ls(pg, 'deskEmbalagens') or [])
        for ruim in ('abc', '-3', '1,234', '4,70,1'):
            pg.fill('#inputCusto', ruim); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(150)
            ok(pg.evaluate("document.getElementById('erroCusto').classList.contains('show') && document.getElementById('campoCusto').classList.contains('has-error')") and ls(pg, 'deskEmbalagens') is None
               and pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'custo "%s" dá erro no padrão da casa e não salva' % ruim)
        pg.fill('#inputCusto', '0,15')
        ok(not pg.evaluate("document.getElementById('erroCusto').classList.contains('show')"), 'digitar de novo tira o erro')
        escolher(pg, '#inputAuto', '3')
        pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)
        salvo = [e for e in (ls(pg, 'deskEmbalagens') or []) if e['nome'] == 'Etiqueta de teste']
        ok(len(salvo) == 1 and salvo[0]['tipo'] == 'insumo' and perto(salvo[0]['custo'], 0.15) and salvo[0]['auto'] == '3' and salvo[0]['id'] == 15 and 'largura' not in salvo[0] and 'cap' not in salvo[0] and salvo[0]['peso'] == 0,
           'o insumo grava tipo, custo e a loja; sem medida, sem "cabe até": %s' % salvo)
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        metas = {c[0]: c[1] for c in pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-card')).map(c => [c.querySelector('.embalagens-nome').textContent, c.querySelector('.embalagens-meta').textContent])")}
        ok(metas.get('Etiqueta de teste') == 'R$ 0,15 · entra sozinho: Desk Tech' and len(metas) == 15, 'recarregar a página não perde o insumo novo: %s' % metas.get('Etiqueta de teste'))
        # editar a caixa: custo e "cabe ate" persistem, e custo vazio vale zero
        pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"2\"]').click()"); pg.wait_for_timeout(300)
        ok(pg.input_value('#inputCusto') == '4,70' and pg.input_value('#inputCap') == '5' and vis('campoCap'), 'a Flex M abre com custo 4,70 e "cabe até" 5')
        pg.fill('#inputCusto', '5,10'); pg.fill('#inputCap', '6'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)
        pg.fill('#campoBusca', 'Flex G'); pg.wait_for_timeout(150)
        pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
        pg.fill('#inputCusto', ''); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)
        lista = {e['nome']: e for e in ls(pg, 'deskEmbalagens')}
        ok(perto(lista['Caixa de Encomenda Flex M']['custo'], 5.10) and lista['Caixa de Encomenda Flex M']['cap'] == 6 and lista['Caixa de Encomenda Flex G']['custo'] == 0, 'custo e "cabe até" gravam; custo vazio vale zero')
        pg.fill('#campoBusca', 'Flex M'); pg.wait_for_timeout(150)
        pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
        pg.fill('#inputCap', 'x'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('erroCap').classList.contains('show')") and pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), '"cabe até" que não é número inteiro avisa e não salva')
        # excluir persiste (pode pedir senha)
        pg.click('#drawerClose'); pg.wait_for_timeout(250)
        pg.fill('#campoBusca', 'Etiqueta'); pg.wait_for_timeout(150)
        pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
        pg.click('#linkExcluirEmbalagem'); pg.wait_for_timeout(300)
        if pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
        ok(not [e for e in ls(pg, 'deskEmbalagens') if e['nome'] == 'Etiqueta de teste'] and len(ls(pg, 'deskEmbalagens')) == 14, 'excluir também persiste')
        # a ficha da Separacao e a da Conferencia leem o cadastro (o "cabe ate" novo da Flex M manda na sugestao)
        ir(pg, SEP_F, '?id=19')
        ok(pg.evaluate("embalagensLer().filter(e => e.nome === 'Caixa de Encomenda Flex M')[0].cap") == 6, 'as fichas leem o cadastro que a tela de Embalagens gravou')
        pg.context.close()

    # ================================================================ 2. separacao
    if secao(2, 'Separação do pedido 4: sugestão, insumos, nenhum R$, trocar, adicionar, remover, travas, falta, rascunho, devolver, pedido grande'):
        pg = nova()
        ir(pg, SEP, '')
        ordem = pg.evaluate("FILA.map(p => p.id)")
        ok(ordem.index(4) == ordem.index(22) + 1 and ordem.index(7) == ordem.index(4) + 1, 'o pedido 4 entra na FILA depois do 22 e antes do 7 (as telas abrem o primeiro não separado): %s' % ordem)
        ir(pg, SEP_F, '?id=4')
        ok(pg.locator('#blocoEmbalagens').is_visible() and 'Embalagens do pedido' in pg.locator('#blocoEmbalagens').inner_text(), 'a ficha tem o bloco "Embalagens do pedido"')
        ok(pg.evaluate("(() => { const l = document.getElementById('listaItens'), b = document.getElementById('blocoEmbalagens'), r = document.querySelector('.sep-rodape'); return !!(l.compareDocumentPosition(b) & 4) && !!(b.compareDocumentPosition(r) & 4); })()"), 'entre a lista de itens e o rodapé')
        ok(pg.evaluate("[PEDIDO.id, PEDIDO.loja, PEDIDO.pecas, PEDIDO.cliente]") == [4, 2, 10, 'Juliana Prado'], 'o pedido 4 da Juliana Prado: Desk Brands, 10 peças')
        ok(pg.evaluate("PARAM.sugerirEmbalagem") is True, 'o PARAM da Separação conhece sugerirEmbalagem (bloco comum)')
        emb = linhas_sep(pg, 'listaEmbalagens'); ins = linhas_sep(pg, 'listaInsumos')
        ok(emb == [['Caixa de Encomenda CE-02', '1', True]], '10 peças: a sugestão é a CE-02 (cabe até 12), com a marca "sugerida pelo volume dos itens": %s' % emb)
        ok(ins == [['Tag Desk Brands', '1', False], ['Fita adesiva', '1', False]], 'os insumos automáticos da loja: a tag da Desk Brands e a fita (não a tag da Shope): %s' % ins)
        corpo = pg.inner_text('.main')
        ok('R$' not in pg.inner_text('#blocoEmbalagens') and 'R$' not in corpo and 'Custo' not in pg.inner_text('#blocoEmbalagens'), 'nenhum "R$" nem a palavra Custo no bloco, nem na ficha')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#emb-sel-0 .dropdown-select-item')).map(i => i.textContent)") == ['Caixa de Encomenda Flex P', 'Caixa de Encomenda Flex M', 'Caixa de Encomenda Flex G', 'Caixa de Encomenda CE-01', 'Caixa de Encomenda CE-02', 'Caixa para Eletrônicos', 'Envelope de Segurança Pequeno', 'Envelope de Segurança Grande', 'Rolo para Pôster'],
           'o menu de embalagem só tem as ativas que não são insumo (sem tag, fita, saco; sem o rolo inativo)')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#ins-sel-0 .dropdown-select-item')).map(i => i.textContent)") == ['Tag Desk Shope', 'Tag Desk Brands', 'Fita adesiva', 'Saco plástico'], 'o menu de insumo só tem os insumos ativos')
        # trocar
        escolher(pg, '#emb-sel-0', 3)
        emb = linhas_sep(pg, 'listaEmbalagens')
        ok(emb == [['Caixa de Encomenda Flex G', '1', False]], 'trocar para a Flex G: a marca de sugerida sai: %s' % emb)
        # adicionar e remover
        pg.click('#btnAddEmbalagem'); pg.wait_for_timeout(200)
        ok(len(linhas_sep(pg, 'listaEmbalagens')) == 2, 'Adicionar embalagem acrescenta uma linha')
        pg.fill('[data-emb-qtd="1"]', '2'); pg.press('[data-emb-qtd="1"]', 'Tab'); pg.wait_for_timeout(200)
        ok(linhas_sep(pg, 'listaEmbalagens')[1][1] == '2', 'a quantidade se edita')
        pg.fill('[data-emb-qtd="1"]', '0'); pg.press('[data-emb-qtd="1"]', 'Tab'); pg.wait_for_timeout(200)
        ok(linhas_sep(pg, 'listaEmbalagens')[1][1] == '1', 'quantidade zero ou vazia volta para 1 (remover é o botão)')
        pg.click('[data-emb-rem="1"]'); pg.wait_for_timeout(200)
        ok(len(linhas_sep(pg, 'listaEmbalagens')) == 1, 'remover tira a linha')
        pg.click('#btnAddInsumo'); pg.wait_for_timeout(200)
        ok(len(linhas_sep(pg, 'listaInsumos')) == 3, 'Adicionar insumo acrescenta uma linha')
        pg.click('[data-ins-rem="2"]'); pg.wait_for_timeout(200)
        pg.click('[data-ins-rem="1"]'); pg.wait_for_timeout(200)
        ok(linhas_sep(pg, 'listaInsumos') == [['Tag Desk Brands', '1', False]], 'remover o insumo tira a linha dele')
        # sem nenhuma embalagem, trava
        pg.click('[data-emb-rem="0"]'); pg.wait_for_timeout(200)
        bipar_tudo(pg)
        pg.click('#btnConcluir'); pg.wait_for_timeout(300)
        ok('Escolha a embalagem do pedido' in modal(pg) and pg.evaluate("PEDIDO.situacao") == 'fila', 'sem embalagem a conclusão trava: %s' % modal(pg)[:70])
        confirmar(pg)
        pg.click('#btnAddEmbalagem'); pg.wait_for_timeout(200)
        pg.click('#btnConcluir'); pg.wait_for_timeout(300)
        ok('Escolha a embalagem' not in modal(pg), 'com embalagem, a trava sai')
        pg.click('#btnConfirmModalCancelar')
        pg.wait_for_timeout(200)
        # a falta declarada muda a sugestao enquanto o separador nao mexeu
        pg = nova()
        ir(pg, SEP_F, '?id=4')
        idx = pg.evaluate("COLETA.map(i => i.sku).indexOf('PAP-3001')")
        pg.click('[data-falta="%d"]' % idx); pg.wait_for_timeout(200)
        pg.fill('[data-qtd="%d"]' % idx, '0'); pg.fill('[data-motivo="%d"]' % idx, 'Endereço vazio')
        pg.click('[data-confirma-falta="%d"]' % idx); pg.wait_for_timeout(300); confirmar(pg)
        emb = linhas_sep(pg, 'listaEmbalagens')
        ok(emb == [['Caixa de Encomenda Flex M', '1', True]], 'falta de 5 cadernos: sobram 5 peças e a sugestão acompanha (Flex M, cabe até 5), enquanto o separador não mexeu: %s' % emb)
        # ... e nao muda quando ele mexeu
        pg = nova()
        ir(pg, SEP_F, '?id=4')
        escolher(pg, '#emb-sel-0', 3)
        idx = pg.evaluate("COLETA.map(i => i.sku).indexOf('PAP-3001')")
        pg.click('[data-falta="%d"]' % idx); pg.wait_for_timeout(200)
        pg.fill('[data-qtd="%d"]' % idx, '0'); pg.fill('[data-motivo="%d"]' % idx, 'Endereço vazio')
        pg.click('[data-confirma-falta="%d"]' % idx); pg.wait_for_timeout(300); confirmar(pg)
        ok(linhas_sep(pg, 'listaEmbalagens') == [['Caixa de Encomenda Flex G', '1', False]], 'mexeu na embalagem, a escolha dele fica (Flex G), mesmo com a falta: %s' % linhas_sep(pg, 'listaEmbalagens'))
        # rascunho: guarda e restaura
        pg = nova()
        ir(pg, SEP_F, '?id=4')
        escolher(pg, '#emb-sel-0', 3)
        pg.click('#btnAddInsumo'); pg.wait_for_timeout(200)
        pg.fill('#campoBipar', 'VES-2001'); pg.press('#campoBipar', 'Enter'); pg.wait_for_timeout(200)
        pg.click('#btnSalvarParcial'); pg.wait_for_timeout(300); confirmar(pg); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        r = reg(pg)
        ok(r and r['situacao'] == 'rascunho' and [(i['id'], i['qtd']) for i in r['itens']] == [(3, 1), (12, 1), (13, 1), (11, 1)] and all('custo' not in i for i in r['itens']),
           '"Salvar e continuar depois" grava o rascunho com id, nome, tipo e quantidade, sem custo: %s' % (r and [(i['id'], i['qtd']) for i in r['itens']]))
        ir(pg, SEP_F, '?id=4')
        ok(linhas_sep(pg, 'listaEmbalagens') == [['Caixa de Encomenda Flex G', '1', False]] and [x[0] for x in linhas_sep(pg, 'listaInsumos')] == ['Tag Desk Brands', 'Fita adesiva', 'Tag Desk Shope'], 'reabrir restaura o rascunho: a Flex G e os três insumos')
        # devolver para a fila apaga
        pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#menuMaisAcoes .dropdown-select-item[data-acao="devolver"]'); pg.wait_for_timeout(300)
        if pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(reg(pg) is None, '"Devolver para a fila" apaga o registro de embalagem')
        # rascunho que e a sugestao pura continua acompanhando a falta
        ir(pg, SEP_F, '?id=4')
        pg.fill('#campoBipar', 'VES-2001'); pg.press('#campoBipar', 'Enter'); pg.wait_for_timeout(200)
        pg.click('#btnSalvarParcial'); pg.wait_for_timeout(300); confirmar(pg); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ir(pg, SEP_F, '?id=4')
        idx = pg.evaluate("COLETA.map(i => i.sku).indexOf('PAP-3001')")
        pg.click('[data-falta="%d"]' % idx); pg.wait_for_timeout(200)
        pg.fill('[data-qtd="%d"]' % idx, '0'); pg.fill('[data-motivo="%d"]' % idx, 'Endereço vazio')
        pg.click('[data-confirma-falta="%d"]' % idx); pg.wait_for_timeout(300); confirmar(pg)
        ok(linhas_sep(pg, 'listaEmbalagens')[0][0] == 'Caixa de Encomenda Flex M', 'rascunho que ainda é a sugestão pura segue acompanhando a falta')
        # pedido grande: nunca um envelope
        pg = nova()
        ir(pg, SEP_F, '?id=19')
        emb = linhas_sep(pg, 'listaEmbalagens')
        ok(emb[0][:2] == ['Caixa para Eletrônicos', '2'], '46 peças (40 resmas e 6 canetas): 2 × Caixa para Eletrônicos, e não um envelope: %s' % emb)
        sug = pg.evaluate("[sugerirEmbalagem(embalagensLer(), 40), sugerirEmbalagem(embalagensLer(), 26), sugerirEmbalagem(embalagensLer(), 25), sugerirEmbalagem(embalagensLer(), 1), sugerirEmbalagem(embalagensLer(), 0), sugerirEmbalagem(embalagensLer(), 12), sugerirEmbalagem(embalagensLer(), 13)]")
        ok(sug == [{'id': 6, 'qtd': 2}, {'id': 6, 'qtd': 2}, {'id': 6, 'qtd': 1}, {'id': 7, 'qtd': 1}, {'id': 7, 'qtd': 1}, {'id': 5, 'qtd': 1}, {'id': 6, 'qtd': 1}], 'sugerirEmbalagem: 40 e 26 peças = 2 caixas grandes; 25 = 1; 1 e 0 = o envelope pequeno; 12 = CE-02; 13 = a grande: %s' % sug)
        sem_cap = pg.evaluate("sugerirEmbalagem([{ id: 1, nome: 'X', tipo: 'pacote', status: 'ativo' }, { id: 2, nome: 'T', tipo: 'insumo', cap: 99, status: 'ativo' }, { id: 3, nome: 'I', tipo: 'pacote', cap: 9, status: 'inativo' }], 3)")
        ok(sem_cap is None, 'sem "cabe até", insumo ou inativa a embalagem não entra na sugestão')
        ok(pg.evaluate("insumosAutomaticos(embalagensLer(), 1).map(i => i.id)") == [11, 13] and pg.evaluate("insumosAutomaticos(embalagensLer(), 2).map(i => i.id)") == [12, 13] and pg.evaluate("insumosAutomaticos(embalagensLer(), 3).map(i => i.id)") == [13],
           'insumosAutomaticos: Shope = tag Shope + fita; Brands = tag Brands + fita; Tech = só a fita (o saco não entra sozinho)')
        ok(pg.evaluate("embResumo([{ qtd: 1, nome: 'A' }, { qtd: 2, nome: 'B' }])") == '1 A + 2 B', 'embResumo: "1 A + 2 B"')
        # parametro desligado: sem sugestao, mas os insumos continuam
        pg = nova()
        ir(pg, SEP_F, '?id=4')
        pg.evaluate("(() => { const p = JSON.parse(localStorage.getItem('deskParametros') || '{}'); p.sugerirEmbalagem = false; localStorage.setItem('deskParametros', JSON.stringify(p)); })()")
        ir(pg, SEP_F, '?id=4')
        ok(linhas_sep(pg, 'listaEmbalagens') == [] and 'Nenhuma embalagem escolhida' in pg.inner_text('#listaEmbalagens') and len(linhas_sep(pg, 'listaInsumos')) == 2, 'com a sugestão desligada em Configurações a ficha abre sem caixa, mas com os insumos automáticos')
        # concluir: o modal cita os nomes e grava
        pg = nova()
        t = separar4(pg)
        ok('Embalagem: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva.' in t, 'o modal de concluir cita a embalagem pelos nomes: %s' % t[-95:])
        r = reg(pg)
        ok(r and r['situacao'] == 'separada' and r['separadoPor'] == 'Marcos Vinícius' and [(i['id'], i['tipo'], i['qtd']) for i in r['itens']] == [(5, 'pacote', 1), (12, 'insumo', 1), (13, 'insumo', 1)] and all('custo' not in i for i in r['itens']),
           'concluir grava "separada" com quem separou, e sem custo: %s' % r)
        ir(pg, SEP_F, '?id=4')
        ok(pg.evaluate("PEDIDO.situacao") == 'separado' and pg.evaluate("Array.from(document.querySelectorAll('#blocoEmbalagens .dropdown-select-btn')).every(b => b.disabled)") and pg.evaluate("Array.from(document.querySelectorAll('#blocoEmbalagens input')).every(b => b.disabled)")
           and not pg.locator('#btnAddEmbalagem').is_visible() and not pg.locator('#btnAddInsumo').is_visible() and pg.locator('#blocoEmbalagens').is_visible(), 'pedido já separado: o bloco fica só leitura, sem adicionar')
        ok(linhas_sep(pg, 'listaEmbalagens')[0][0] == 'Caixa de Encomenda CE-02' and 'R$' not in pg.inner_text('#blocoEmbalagens'), 'e continua mostrando a escolha, sem valor')
        for n in (7, 23, 24):
            ir(pg, SEP_F, '?id=%d' % n)
            ok(not pg.locator('#blocoEmbalagens').is_visible(), 'o exemplo já separado %d não tem registro: o bloco não aparece' % n)
        pg.context.close()

    # ================================================================ 3. conferencia
    if secao(3, 'Conferência: o 4 só aparece depois de separado, vem preenchido, confirma sem troca e reabre conferido'):
        pg = nova()
        ir(pg, CONF)
        ok(4 not in pg.evaluate("FILA.map(p => p.id)"), 'antes de a Separação concluir, o pedido 4 não está na fila da Conferência')
        ir(pg, CONF_F, '?id=4')
        ok('não está na fila' in modal(pg), 'a bancada avisa que o 4 ainda não chegou: %s' % modal(pg)[:60])
        pg.context.close()
        pg = nova()
        separar4(pg)
        ir(pg, CONF)
        pg.evaluate("itensPorPaginaAtual = 25; renderTabela();"); pg.wait_for_timeout(150)
        ok(4 in pg.evaluate("FILA.map(p => p.id)") and 'Juliana Prado' in pg.inner_text('#corpoTabela') and pg.evaluate("FILA.filter(p => p.id === 4)[0].situacao") == 'aguardando', 'depois de separado, o 4 entra na fila da Conferência (aguardando)')
        ok(pg.evaluate("FILA.filter(p => p.id === 4)[0].pecas") == 10 and pg.evaluate("FILA.filter(p => p.id === 4)[0].falta") is False, 'com as 10 peças que o separador achou e sem falta')
        ir(pg, CONF_F, '?id=4')
        ok(pg.evaluate("[PEDIDO.id, PEDIDO.cliente, PEDIDO.pago, PEDIDO.transp, PEDIDO.separador]") == [4, 'Juliana Prado', True, 'Correios · SEDEX', 3], 'a ficha abre o 4, pago, por Correios · SEDEX, separado pelo operador 3')
        veio = pg.inner_text('#embVeio')
        ok(veio == 'Veio da Separação: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva. Confira e troque só se não servir.', 'acima da lista: "Veio da Separação: ..." com os nomes: %s' % veio)
        ok(volumes_conf(pg) == [['Caixa de Encomenda CE-02', 'escolhida na separação']], 'um volume já preenchido, com a marca "escolhida na separação": %s' % volumes_conf(pg))
        ins = pg.evaluate("Array.from(document.querySelectorAll('#listaInsumos .emb-linha')).map(x => [x.querySelector('.dropdown-select-label').textContent.trim(), x.querySelector('input').value])")
        ok(ins == [['Tag Desk Brands', '1'], ['Fita adesiva', '1']], 'o bloco Insumos vem preenchido: %s' % ins)
        ok(pg.evaluate("(() => { const a = document.getElementById('btnAddVolume').closest('.itens-acoes'), b = document.getElementById('blocoInsumos'); return !!(a.compareDocumentPosition(b) & 4); })()"), 'o bloco Insumos fica logo abaixo do botão Adicionar volume')
        card = pg.evaluate("document.getElementById('listaVolumes').closest('.card').innerText")
        ok('R$' not in card, 'nada de R$ na área de embalagem da bancada')
        pg.evaluate('() => montarEtiquetas()')
        etiq = pg.evaluate("document.getElementById('etiqFolha').innerText")
        ok(pg.evaluate("VOLUMES.length") == 1 and 'Volume 1 de 1' in etiq and 'Tag' not in etiq and 'Fita' not in etiq and 'Embalagem: Caixa de Encomenda CE-02' in etiq, 'o insumo não vira volume nem etiqueta: 1 volume, 1 etiqueta, só a caixa')
        t = conferir4(pg)
        ok('Embalagem confirmada: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva.' in t and 'trocada' not in t, 'o modal de fechar cita a embalagem confirmada, sem troca: %s' % t[-100:])
        r = reg(pg)
        ok(r and r['situacao'] == 'confirmada' and r['trocas'] == [] and r['conferidoPor'] == 'Tatiane Moura' and r['separadoPor'] == 'Marcos Vinícius' and r['em'] == '2026-10-30'
           and [(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(5, 1, 6.3), (12, 1, 0.6), (13, 1, 0.3)], 'confirmar sem troca grava "confirmada" com o custo do cadastro e trocas vazio: %s' % r)
        ok('faturado' in AVISO[0] and 'No protótipo nada persiste' not in AVISO[0] and 'guardada no pedido' in AVISO[0], 'o aviso final não diz mais que nada persiste: diz que a embalagem fica guardada no pedido: %s' % AVISO[0][-150:])
        ir(pg, CONF_F, '?id=4')
        ok(pg.inner_text('#badgeSituacao').strip().upper() == 'CONFERIDO' and pg.locator('#btnFechar').is_disabled() and pg.locator('#btnFecharRodape').is_disabled(), 'reabrir mostra o pedido conferido, com o fechar desligado')
        ok(pg.evaluate("fechada") is True and pg.evaluate("ITENS.map(i => i.conferida)") == [3, 5, 2], 'fechado: a contagem é a da separação (3, 5 e 2)')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#listaVolumes .dropdown-select-btn, #listaInsumos .dropdown-select-btn, #listaVolumes input, #listaInsumos input, #corpoItens input, .emb-remover, .vol-remover')).every(e => e.disabled)")
           and not pg.locator('#btnAddVolume').is_visible() and not pg.locator('#btnAddInsumo').is_visible(), 'tudo só leitura: menus, quantidades, remover e adicionar')
        ok(pg.inner_text('#embVeio') == 'Embalagem confirmada por Tatiane Moura em 30/10/2026: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva.' and volumes_conf(pg) == [['Caixa de Encomenda CE-02', '']],
           'a linha de cima diz quem confirmou e quando; o volume vem do registro: %s' % pg.inner_text('#embVeio'))
        ok(not pg.locator('#blocoCompensa').is_visible(), 'sem falta, sem bloco de compensação')
        ir(pg, CONF)
        pg.evaluate("itensPorPaginaAtual = 25; renderTabela();"); pg.wait_for_timeout(150)
        ok(pg.evaluate("FILA.filter(p => p.id === 4)[0].situacao") == 'conferido', 'e na fila o 4 nasce "conferido"')
        # voltar a Separacao e devolver o pedido tira o 4 da Conferencia
        ir(pg, SEP_F, '?id=4')
        ok(linhas_sep(pg, 'listaEmbalagens')[0][0] == 'Caixa de Encomenda CE-02' and pg.evaluate("Array.from(document.querySelectorAll('#blocoEmbalagens .dropdown-select-btn')).every(b => b.disabled)"), 'a Separação mostra o que foi confirmado, só leitura')
        pg.context.close()

    # ================================================================ 4. troca
    if secao(4, 'Com troca: o registro, o modal e o Registro de atividades'):
        pg = nova()
        separar4(pg)
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        escolher(pg, '#emb-0', 3)
        ok(volumes_conf(pg) == [['Caixa de Encomenda Flex G', 'trocada: era Caixa de Encomenda CE-02']], 'trocar o volume mostra "trocada: era ..." : %s' % volumes_conf(pg))
        pg.click('[data-ins-rem="1"]'); pg.wait_for_timeout(200)           # tira a fita
        pg.click('#btnAddInsumo'); pg.wait_for_timeout(200)                # acrescenta uma linha (a tag da Shope) e troca para o saco
        escolher(pg, '#ins-sel-1', 14)
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        t = modal(pg)
        quer = ['Caixa de Encomenda CE-02 → Caixa de Encomenda Flex G', '+ 1 Saco plástico', '− 1 Fita adesiva']
        ok('Embalagem trocada: ' + '; '.join(quer) + '.' in t, 'o modal cita as trocas: %s' % t[:200])
        ok('Embalagem confirmada: 1 Caixa de Encomenda Flex G + 1 Tag Desk Brands + 1 Saco plástico.' in t, 'e a embalagem que vale: %s' % t[-100:])
        confirmar(pg); confirmar(pg)
        r = reg(pg)
        ok(r and r['trocas'] == quer and [(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(3, 1, 5.9), (12, 1, 0.6), (14, 1, 0.25)],
           'o registro tem as trocas e vale o que a Conferência confirmou (Flex G, tag Brands, saco; sem a fita): %s' % (r and r['trocas']))
        log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(x => x.chave === 'confSaidaFecha')")
        ok(len(log) == 1 and all(q in log[0]['detalhe'] for q in quer), 'a troca cai no Registro de atividades (ação confSaidaFecha), inteira: %s' % (log and log[0]['detalhe']))
        ir(pg, CONF_F, '?id=4')
        ok('Trocada na conferência: ' + '; '.join(quer) in pg.inner_text('#embVeio'), 'reabrir mostra a troca na linha de cima')
        # um insumo a mais ou um volume a mais tambem entram
        pg = nova()
        separar4(pg)
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        pg.click('#btnAddVolume'); pg.wait_for_timeout(200)
        pg.fill('[data-ins-qtd="0"]', '3'); pg.press('[data-ins-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        t = modal(pg)
        ok('Embalagem trocada: + 1 Caixa de Encomenda CE-02; + 2 Tag Desk Brands.' in t, 'volume a mais (a sugestão do segundo volume é a CE-02) e insumo a mais viram "+": %s' % t[60:220])
        confirmar(pg); confirmar(pg)
        r = reg(pg)
        ok(r['trocas'] == ['+ 1 Caixa de Encomenda CE-02', '+ 2 Tag Desk Brands'] and [i['qtd'] for i in r['itens'] if i['tipo'] != 'insumo'] == [2], 'e o registro guarda 2 caixas CE-02 e as trocas: %s' % r['trocas'])
        pg.context.close()

    # ================================================================ 5. custos
    if secao(5, 'Custos: o 4 confirmado (7,20, sem "estimada", nomes; lucro 161,40) e os números do mês antes e depois'):
        pg = nova()
        abrir_custos(pg)
        todos = todos_custos(pg)
        online = [x for x in todos if x.get('canal') == 'loja_virtual']
        ors = {x['id']: oraculo(x) for x in online}
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaCustos thead th')).filter(th => getComputedStyle(th).display !== 'none').map(th => th.textContent.replace(/[▲▼]/g, '').trim())")
        l = {n: linha_pedido(pg, n) for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        quer_emb = {1: ('R$ 5,00', True), 3: ('R$ 5,00', True), 4: ('R$ 8,00', True), 8: ('R$ 7,00', False), 9: ('R$ 6,80', False), 11: ('R$ 5,40', False), 12: ('R$ 7,20', False), 16: ('R$ 12,60', False)}
        ok(all(l[n]['Embalagem'] == v + (' estimada' if est else '') for n, (v, est) in quer_emb.items()), 'a coluna Embalagem: 1, 3 e 4 estimados (a marca "estimada"), 8, 9, 11, 12 e 16 confirmados: %s' % {n: l[n]['Embalagem'] for n in l})
        ok(pg.evaluate("document.querySelector('#tabelaCustos th[data-ordem=embalagem]').title").startswith('A embalagem que a Conferência de Saída confirmou') and 'até lá, o valor da loja' in pg.evaluate("document.querySelector('#tabelaCustos th[data-ordem=embalagem]').title"),
           'o título do cabeçalho explica: a que a Conferência confirmou; até lá, o valor da loja')
        ok(perto(sum(o['embalagem'] for o in ors.values()), 57), 'o oráculo diz 57,00 de embalagem no mês')
        ok(pg.evaluate("[kpiFaturamento, kpiCustos, kpiLucro, kpiMargem, kpiAnuncios, kpiLucroAnuncios].map(e => e.textContent)")[2:] == ['R$ 1.048,28', '13,8%', 'R$ 450,00', 'R$ 598,28'], 'lucro 1.048,28 (margem 13,8%%), anúncios 450,00, lucro depois dos anúncios 598,28: %s' % kpis(pg))
        luc = {n: pg.evaluate("(n) => resultadoDoPedido(PEDIDOS.filter(p => p.id === n)[0]).lucro", n) for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        ok(all(perto(luc[n], v) for n, v in {1: 356.26, 3: -265.80, 4: 160.60, 8: 156.46, 9: 159.20, 11: -32.89, 12: 180.89, 16: 333.56}.items()), 'o lucro de cada pedido: %s' % luc)
        ok(all(perto(luc[n], ors[n]['lucro']) for n in luc), 'e bate com o oráculo, pedido a pedido')
        for loja, lucro, depois in (('1', 'R$ 547,59', 'R$ 247,59'), ('2', 'R$ 500,69', 'R$ 410,69')):
            pg.evaluate("(l) => { fLoja = l; render(); }", loja)
            k = kpis(pg)
            ok(k[2] == lucro and k[5] == depois, 'loja %s: lucro %s, depois dos anúncios %s: %s' % (loja, lucro, depois, k))
        pg.evaluate("fLoja = 'todos'; render();")
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(150)
        ok(sorted(int(re.search(r'nº (\d+)', x).group(1)) for x in pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr td:first-child')).map(t => t.innerText)")) == [3, 11, 16], '"Abaixo da margem" segue 3 a 15%: o 3, o 11 e o 16')
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(100)
        pg.evaluate("(() => { const p = JSON.parse(localStorage.getItem('deskParametros') || '{}'); p.margemMinimaPct = 20; localStorage.setItem('deskParametros', JSON.stringify(p)); render(); })()")
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(150)
        ok(sorted(int(re.search(r'nº (\d+)', x).group(1)) for x in pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr td:first-child')).map(t => t.innerText)")) == [1, 3, 11, 12, 16], 'e a 20% são o 1, o 3, o 11, o 12 e o 16')
        # o painel do 11: os nomes
        abrir_custos(pg)
        pg.click('#corpoTabela tr[data-id="11"]'); pg.wait_for_timeout(300)
        painel = pg.inner_text('#eventDrawer').replace('\n', ' ')
        ok('1 Caixa de Encomenda Flex M + 1 Tag Desk Shope + 1 Fita adesiva' in painel and 'estimada' not in painel, 'o painel do 11 mostra a embalagem pelos nomes, sem "estimada"')
        pg.click('#drawerClose'); pg.wait_for_timeout(200)
        pg.click('#corpoTabela tr[data-id="1"]'); pg.wait_for_timeout(300)
        ok('estimada pelo valor da loja, até a Conferência de Saída confirmar' in pg.inner_text('#eventDrawer').replace('\n', ' '), 'o painel do 1 diz "estimada pelo valor da loja, até a Conferência de Saída confirmar"')
        # agrupar e dividir por item seguem fechando
        pg.evaluate("agrupar = 'produto'; render();"); pg.wait_for_timeout(200)
        gr = pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => Array.from(tr.children).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        ok(len(gr) > 5 and not any('estimada' in c for r_ in gr for c in r_), 'agrupado por produto a repartição segue (e a marca "estimada" fica só nas linhas de pedido)')
        pg.context.close()
        # o fluxo do 4 sem trocar nada
        pg = nova()
        separar4(pg)
        conferir4(pg)
        abrir_custos(pg)
        l4 = linha_pedido(pg, 4)
        ok(l4['Embalagem'] == 'R$ 7,20' and 'estimada' not in l4['Embalagem'], 'depois do fluxo (10 peças, CE-02, tag Brands e fita), a embalagem do 4 é 7,20 e não é mais estimada: %s' % l4['Embalagem'])
        ok(l4['Lucro'] == 'R$ 161,40', 'lucro do 4 = 161,40: %s' % l4['Lucro'])
        conf4 = dict(EMB_CONFIRMADA); conf4[4] = [(1, '6.30'), (1, '0.60'), (1, '0.30')]
        todos = todos_custos(pg)
        ok(perto(oraculo(next(x for x in todos if x['id'] == 4), confirmadas=conf4)['lucro'], 161.40), 'o oráculo (embalagem confirmada, com Decimal) também dá 161,40')
        ok(kpis(pg)[2] == 'R$ 1.049,08' and kpis(pg)[5] == 'R$ 599,08', 'lucro do mês 1.049,08 (depois dos anúncios 599,08): %s' % kpis(pg))
        ok(sum(oraculo(x, confirmadas=conf4)['embalagem'] for x in todos if x.get('canal') == 'loja_virtual') == D('56.20'), 'a embalagem do mês cai para 56,20 (o 4 saiu dos 8,00 estimados e foi para 7,20)')
        pg.click('#corpoTabela tr[data-id="4"]'); pg.wait_for_timeout(300)
        painel = pg.inner_text('#eventDrawer').replace('\n', ' ')
        ok('1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva' in painel and 'estimada' not in painel and 'Trocada na conferência' not in painel, 'o painel do 4 tem os nomes que a Conferência confirmou, sem troca')
        pg.context.close()

    # ================================================================ 6. custo do dia
    if secao(6, 'O custo do dia: mudar o cadastro depois não mexe no pedido; o 16 usa 11,90; um pedido confirmado depois usa o preço novo'):
        pg = nova()
        separar4(pg)
        conferir4(pg)
        # o cadastro muda: CE-02 vai a 9,00, a tag Brands a 1,00, a Caixa para Eletronicos segue em 12,50
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        for nome, custo in (('Caixa de Encomenda CE-02', '9,00'), ('Tag Desk Brands', '1,00')):
            pg.fill('#campoBusca', nome); pg.wait_for_timeout(150)
            pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
            pg.fill('#inputCusto', custo); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)
        cad = {e['nome']: e['custo'] for e in ls(pg, 'deskEmbalagens')}
        ok(perto(cad['Caixa de Encomenda CE-02'], 9) and perto(cad['Tag Desk Brands'], 1) and perto(cad['Caixa para Eletrônicos'], 12.5), 'o cadastro mudou: CE-02 9,00, tag Brands 1,00; a caixa de eletrônicos segue em 12,50')
        abrir_custos(pg)
        l4, l16 = linha_pedido(pg, 4), linha_pedido(pg, 16)
        ok(l4['Embalagem'] == 'R$ 7,20' and l4['Lucro'] == 'R$ 161,40', 'o 4, confirmado antes, segue em 7,20 (lucro 161,40): o pedido guardou o custo do dia: %s' % l4['Embalagem'])
        ok(l16['Embalagem'] == 'R$ 12,60' and pg.evaluate("JSON.parse(localStorage.getItem('deskEmbalagens')).filter(e => e.id === 6)[0].custo") == 12.5, 'o 16 usa 11,90 + tag + fita = 12,60 com o cadastro em 12,50')
        ok(reg(pg)['itens'][0]['custo'] == 6.3, 'o registro do 4 guarda 6,30 da CE-02')
        pg.context.close()
        # um pedido confirmado DEPOIS da mudanca usa o preco novo
        pg = nova()
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        for nome, custo in (('Caixa de Encomenda CE-02', '9,00'), ('Tag Desk Brands', '1,00')):
            pg.fill('#campoBusca', nome); pg.wait_for_timeout(150)
            pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
            pg.fill('#inputCusto', custo); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)
        separar4(pg)
        conferir4(pg)
        abrir_custos(pg)
        l4 = linha_pedido(pg, 4)
        ok(l4['Embalagem'] == 'R$ 10,30' and 'estimada' not in l4['Embalagem'], 'confirmado depois da mudança, o 4 usa o preço novo: 9,00 + 1,00 + 0,30 = 10,30: %s' % l4['Embalagem'])
        ok(reg(pg)['itens'][0]['custo'] == 9 and reg(pg)['itens'][1]['custo'] == 1, 'o registro guarda os custos de hoje')
        pg.context.close()

    # ================================================================ 7. configurar
    if secao(7, 'Configurar muda só os estimados'):
        pg = nova()
        abrir_custos(pg)
        pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#menuMaisAcoes [data-acao="configurar"]'); pg.wait_for_timeout(250)
        rot = pg.inner_text('#cfgDrawer')
        ok('Embalagem estimada por loja (R$ por pedido)' in rot and 'Vale só para o pedido que a Conferência de Saída ainda não confirmou' in rot, 'o rótulo e a dica de Configurar dizem "estimada" e "ainda não confirmou"')
        pg.fill('#cfgEmbalagem input[data-loja="1"]', '6,00'); pg.click('#btnAplicarCfg'); pg.wait_for_timeout(300)
        e = {n: linha_pedido(pg, n)['Embalagem'] for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        ok(e[1] == 'R$ 6,00 estimada' and e[3] == 'R$ 6,00 estimada' and e[4] == 'R$ 8,00 estimada', 'Shope a 6,00 mexe no 1 e no 3 (estimados), não no 4 (Brands): %s' % e)
        ok(e[8] == 'R$ 7,00' and e[11] == 'R$ 5,40' and e[16] == 'R$ 12,60' and e[9] == 'R$ 6,80' and e[12] == 'R$ 7,20', 'e não mexe no 8, no 11, no 16 (confirmados): %s' % e)
        pg.context.close()

    # ================================================================ 8. pagina do pedido
    if secao(8, 'A página do pedido: nomes, "estimada", troca'):
        pg = nova()
        ir(pg, PV_D, '?id=11')
        cx = pg.inner_text('#caixaResultado').replace('\n', ' ')
        ok('1 Caixa de Encomenda Flex M + 1 Tag Desk Shope + 1 Fita adesiva' in cx and 'R$ 5,40' in cx and 'estimada' not in cx, 'o pedido 11 mostra a embalagem pelos nomes: %s' % cx[cx.index('Embalagem'):cx.index('Embalagem') + 100])
        ir(pg, PV_D, '?id=1')
        cx = pg.inner_text('#caixaResultado').replace('\n', ' ')
        ok('estimada pelo valor da loja, até a Conferência de Saída confirmar' in cx and 'R$ 5,00' in cx, 'o pedido 1 diz "estimada pelo valor da loja, até a Conferência de Saída confirmar"')
        ir(pg, PV_D, '?id=4')
        ok('estimada' in pg.inner_text('#caixaResultado'), 'o pedido 4 ainda não confirmado também é estimado')
        ok('a embalagem escolhida na Separação é confirmada antes de a nota sair' in pg.evaluate("PROXIMO_PASSO.separacao.texto"), 'o texto do passo diz que a embalagem escolhida na Separação é confirmada na Conferência de Saída: %s' % pg.evaluate("PROXIMO_PASSO.separacao.texto")[:150])
        pg.context.close()
        pg = nova()
        separar4(pg)
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        escolher(pg, '#emb-0', 3)
        pg.click('#btnFechar'); pg.wait_for_timeout(320); confirmar(pg); confirmar(pg)
        ir(pg, PV_D, '?id=4')
        cx = pg.inner_text('#caixaResultado').replace('\n', ' ')
        ok('1 Caixa de Encomenda Flex G + 1 Tag Desk Brands + 1 Fita adesiva' in cx and 'R$ 6,80' in cx and 'Trocada na conferência: Caixa de Encomenda CE-02 → Caixa de Encomenda Flex G' in cx, 'o 4 confirmado com troca: os nomes novos, 5,90 + 0,60 + 0,30 = 6,80 e a linha da troca')
        abrir_custos(pg)
        pg.click('#corpoTabela tr[data-id="4"]'); pg.wait_for_timeout(300)
        painel = pg.inner_text('#eventDrawer').replace('\n', ' ')
        ok('Trocada na conferência: Caixa de Encomenda CE-02 → Caixa de Encomenda Flex G' in painel and 'R$ 6,80' in painel, 'em Custos o painel também diz a troca')
        for tela in ('pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html'):
            ir(pg, tela, '?id=v1' if 'detalhe.html' in tela and 'comissoes' in tela else '')
            ok(pg.evaluate("resultadoDoPedido(PEDIDOS.filter(p => p.id === 4)[0]).embalagem") == 6.8 and pg.evaluate("resultadoDoPedido(PEDIDOS.filter(p => p.id === 4)[0]).embalagemEstimada") is False,
               '%s: a conta do 4 usa a embalagem confirmada (6,80)' % tela.replace('pagina-', ''))
        pg.context.close()

    # ================================================================ 9. copias
    if secao(9, 'Blocos idênticos: EMBALAGENS: LEITURA nas 3 telas, o da Conferência nas 2, o pedido 4 igual nas FILAs'):
        IN, FIM = '  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA ====='
        tres = [bloco(fonte(n), IN, FIM) for n in (CAD, SEP_F, CONF_F)]
        ok(all(x == tres[0] for x in tres) and 'function sugerirEmbalagem(lista, pecas)' in tres[0] and 'function embResumo' in tres[0], 'o bloco EMBALAGENS: LEITURA é idêntico no Cadastro, na ficha da Separação e na bancada da Conferência')
        ok(fonte(CONF_F).count('function sugerirEmbalagem') == 1 and fonte(SEP_F).count('function sugerirEmbalagem') == 1, 'a sugerirEmbalagem local da bancada saiu: uma só em cada ficha')
        ok('const EMBALAGENS = [' not in fonte(CONF_F), 'a bancada não carrega mais a lista fixa de embalagens: lê o cadastro')
        def aplica(n):
            t = fonte(n); a = t.index('  // ===== O QUE A SEPARACAO E A EMBALAGEM JA FIZERAM COM O PEDIDO'); return t[a:t.index('  })();', a) + 8]
        ok(aplica(CONF) == aplica(CONF_F) and "deskSeparacao" in aplica(CONF) and "situacao === 'confirmada'" in aplica(CONF), 'o bloco que aplica a Separação e a embalagem confirmada é idêntico nas duas telas da Conferência')
        def entrada4(n):
            t = fonte(n); a = re.search(r"    \{ id: 4, +numero: 4", t).start(); return t[a:t.index("} ] }", a) + 5]
        ok(entrada4(SEP) == entrada4(SEP_F) and "cliente: 'Juliana Prado'" in entrada4(SEP) and "liberadoHa: 6" in entrada4(SEP), 'o pedido 4 é igual nas duas FILAs da Separação')
        ok(entrada4(CONF) == entrada4(CONF_F) and 'daSeparacao: true' in entrada4(CONF) and "preco: 199.90" in entrada4(CONF), 'o pedido 4 é igual nas duas FILAs da Conferência (daSeparacao, pago, preço de cada item)')
        css = lambda n: bloco(fonte(n), '  /* ===== EMBALAGENS DO PEDIDO (30/out/2026) =====', '@media (max-width:760px) { .emb-linha { grid-template-columns:minmax(0,1fr) 84px 32px; gap:8px; } }')
        ok(css(SEP_F) == css(CONF_F), 'o CSS do bloco de embalagens é idêntico na Separação e na Conferência')
        n5 = ['pagina-vendas-custos-ecommerce.html', PV_D, 'pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html']
        ok(all('RES_EMBALAGENS_EXEMPLO' in fonte(n) and 'function resEmbalagem(p, cfg)' in fonte(n) for n in n5), 'as 5 telas do RESULTADO DO PEDIDO trazem o exemplo confirmado e resEmbalagem (o bloco inteiro é comparado em teste_custos_ecommerce.py)')
        # a Separacao e a Conferencia nao se contradizem: o 4 tem os mesmos itens, transportadora e endereco
        pg = nova()
        ir(pg, SEP_F, '?id=4'); a = pg.evaluate("[PEDIDO.transp, PEDIDO.entrega, PEDIDO.itens.map(i => [i.sku, i.qtd])]")
        separar4(pg)
        ir(pg, CONF_F, '?id=4'); b = pg.evaluate("[PEDIDO.transp, PEDIDO.entrega, PEDIDO.itens.map(i => [i.sku, i.pedido])]")
        ok(a == b, 'o 4 tem o mesmo envio, endereço e itens na Separação e na Conferência: %s' % (a == b))
        pg.context.close()

    # ================================================================ 10. layout
    if secao(10, 'O layout do bloco a 1280 e 860 px, sem barra horizontal'):
        for w in (1280, 860):
            pg = nova(w, 800)
            ir(pg, SEP_F, '?id=19')
            pg.click('#btnAddInsumo'); pg.wait_for_timeout(150)
            r = pg.evaluate("""() => { const b = document.getElementById('blocoEmbalagens'), br = b.getBoundingClientRect();
                const fora = Array.from(b.querySelectorAll('*')).filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > br.right + 1 || r.left < br.left - 1); }).length;
                return { pagina: document.documentElement.scrollWidth - window.innerWidth, bloco: b.scrollWidth - b.clientWidth, fora: fora }; }""")
            ok(r['pagina'] <= 0 and r['bloco'] <= 0 and r['fora'] == 0, 'Separação a %d px: sem barra horizontal e nada para fora do bloco: %s' % (w, r))
            pg.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            pg.click('#emb-sel-0 .dropdown-select-btn'); pg.wait_for_timeout(250)
            alcance = pg.evaluate("""() => { const m = document.querySelector('#emb-sel-0 .dropdown-select-menu'), r = m.getBoundingClientRect(), b = document.querySelector('#emb-sel-0 .dropdown-select-btn').getBoundingClientRect();
                return { abre_baixo: r.top >= b.bottom - 1, dentro: r.right <= window.innerWidth + 1 }; }""")
            ok(alcance['abre_baixo'] and alcance['dentro'], 'o menu de embalagem abre para baixo e cabe na tela a %d px: %s' % (w, alcance))
            pg.context.close()
            pg = nova(w, 800)
            separar4(pg)
            ir(pg, CONF_F, '?id=4')
            r = pg.evaluate("""() => { const b = document.getElementById('blocoInsumos'), br = b.getBoundingClientRect(), v = document.getElementById('listaVolumes');
                const fora = Array.from(b.querySelectorAll('*')).filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && (r.right > br.right + 1 || r.left < br.left - 1); }).length;
                return { pagina: document.documentElement.scrollWidth - window.innerWidth, bloco: b.scrollWidth - b.clientWidth, fora: fora, vol: v.scrollWidth - v.clientWidth }; }""")
            # A 860 px a linha de volumes da bancada ja rolava na lateral antes desta entrega (a grade tem colunas fixas: 118 px a mais no HEAD); o bloco novo dos insumos nao.
            ok(r['bloco'] <= 0 and r['fora'] == 0 and (w == 860 or (r['pagina'] <= 0 and r['vol'] <= 0)), 'Conferência a %d px: os insumos cabem no bloco%s: %s' % (w, '' if w == 860 else ' e a página e os volumes não rolam na lateral', r))
            pg.context.close()

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
raise SystemExit(1 if falhas else 0)
