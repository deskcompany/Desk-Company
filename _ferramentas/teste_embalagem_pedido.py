# -*- coding: utf-8 -*-
# Custos do E-commerce, entrega 4 (decidida em 30/out/2026): a embalagem do pedido nasce na Separacao, a Conferencia de Saida confirma, e Custos le o que foi confirmado.
#
# O que ele protege sao as decisoes do usuario, as que "simplificar" apaga primeiro:
#   Cadastro de Embalagens ganha CUSTO e o tipo INSUMO (tag, fita, saco): sem medidas, sem peso, sem "cabe ate"; o insumo pode entrar sozinho em todas as lojas ou numa so
#   Separacao: antes de concluir o separador escolhe a embalagem; a menor caixa que cabe vem sugerida e os insumos automaticos ja vem preenchidos;
#              ele ve so os NOMES, nunca o custo (nem um "R$" no bloco)
#   Conferencia de Saida: recebe preenchido e confirma; pode trocar, com registro (a troca vai para o Registro de atividades); VALE O QUE ELA CONFIRMOU
#   O pedido guarda o CUSTO DO DIA: mudar o preco no cadastro depois nao mexe no pedido antigo
#   Custos e a pagina do pedido mostram a embalagem confirmada com os nomes; o pedido ainda nao confirmado mostra uma ESTIMATIVA pelo cadastro (a menor caixa em que cabem as pecas +
#   os insumos automaticos da loja, a preco de hoje) e diz "estimada". O que a Separacao escolheu NAO mexe no custo: quem decide e a Conferencia (decisao de 30/out/2026, depois da entrega)
#   "Cabe ate" e so sugestao: nada trava por capacidade, e o conferente acerta a quantidade pelo campo Total de volumes (1 a 999)
#   Sugestao de pedido grande: se nenhuma embalagem couber, a de maior capacidade, em quantas unidades forem precisas (e nunca um envelope)
#
#   [1]  Cadastro: custo, tipo Insumo (esconde medidas e peso, mostra "Entra sozinho"), erro em custo invalido, persiste ao recarregar;
#   [2]  Separacao do pedido 4: sugestao, insumos automaticos, nenhum R$, trocar/adicionar/remover, sem embalagem trava, falta muda a sugestao, rascunho, devolver, pedido grande;
#   [3]  O pedido 4 so aparece na Conferencia depois de concluido; vem preenchido; confirmar sem troca grava 'confirmada' com o custo do cadastro; reabrir mostra conferido;
#   [4]  Com troca: o registro tem as trocas, o modal cita, e cai no Registro de atividades;
#   [5]  Custos: o pedido 4 confirmado (7,20, sem "estimada", com os nomes; lucro 167,82, pela taxa Bronze da loja virtual) e os numeros do mes antes e depois, todos do oraculo;
#   [6]  O custo do dia: mudar o cadastro nao mexe no 4; o 16 usa 11,90 com o cadastro em 12,50; um pedido confirmado depois usa o preco novo;
#   [7]  Configurar nao tem o campo de embalagem; o valor antigo por loja e ignorado e some ao salvar; o log nao cita embalagem;
#   [8]  A pagina do pedido: o 11 com os nomes, o 1 "estimada", o 4 com a troca;
#   [9]  As copias: o bloco EMBALAGENS: LEITURA nas 10 telas, o da Conferencia nas 2, o pedido 4 igual nas FILAs;
#   [10] O layout do bloco a 1280 e 860 px, sem barra horizontal;
#   [11] A estimativa pelo cadastro (custo, "cabe ate", cadastro vazio), a Separacao que nao mexe no custo, sem trava de capacidade, Total de volumes e o teto de 999;
#   [12] O painel do cadastro: Largura, Altura e Comprimento na mesma linha;
#   [13] O ESTOQUE das embalagens (03/nov/2026): ver o cabecalho da secao 13 mais abaixo.
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
PROD_D = 'pagina-cadastros-produtos-detalhe.html'
NC = 'pagina-estoque-necessidades-compra.html'
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


from oraculo_custos import D, c2, oraculo, EMB_CONFIRMADA, embalagem_do_pedido, CADASTRO_EMB, anuncios_do_periodo, abaixo_da_margem
from decimal import ROUND_HALF_UP

br = lambda v: ('− ' if float(v) < 0 else '') + 'R$ ' + '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')
perto = lambda a, b: abs(float(a) - float(b)) < 0.005
pct1 = lambda v: str(D(v).quantize(D('0.1'), rounding=ROUND_HALF_UP)).replace('.', ',') + '%'
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
        ok(m['Caixa de Encomenda Flex P'][1] == '26,0×21,0×1,0cm · 0,09 Kg · R$ 3,50 · Saldo 140 · mín. 50' and m['Caixa para Eletrônicos'][1] == '40,0×30,0×30,0cm · 1,20 Kg · R$ 12,50 · Saldo 6 · mín. 5', 'a linha de baixo mostra medidas, peso e custo: %s' % m['Caixa de Encomenda Flex P'][1])
        ok(m['Tag Desk Shope'][1] == 'R$ 0,40 · entra sozinho: Desk Shope · Saldo 800 · mín. 300' and m['Tag Desk Brands'][1] == 'R$ 0,60 · entra sozinho: Desk Brands · Saldo 150 · mín. 200'
           and m['Fita adesiva'][1] == 'R$ 15,00 a unidade · rende 50 (R$ 0,30 por pedido) · entra sozinho: todas as lojas · Saldo 8 · mín. 4' and m['Saco plástico'][1] == 'R$ 0,25 · Saldo 400 · mín. 100', 'o insumo mostra o custo e onde entra sozinho (e só o custo, se não entra): %s' % [m[k][1] for k in ('Tag Desk Shope', 'Fita adesiva', 'Saco plástico')])
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
        ok('Só serve para sugerir a caixa. Quem decide o que vai no pedido é a Conferência de Saída.' in pg.inner_text('#campoCap'), 'o "Cabe até" diz que só serve para sugerir: %s' % pg.inner_text('#campoCap')[:140])
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
            # a mascara de digitacao nao deixa digitar esses textos; posto por codigo, a validacao do salvar segue provada
            pg.evaluate("(v) => { const e = document.getElementById('inputCusto'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); }", ruim); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(150)
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
        ok(metas.get('Etiqueta de teste') == 'R$ 0,15 · entra sozinho: Desk Tech · Saldo 0 · mín. 0' and len(metas) == 15, 'recarregar a página não perde o insumo novo: %s' % metas.get('Etiqueta de teste'))
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
        ok(veio == 'Veio da Separação: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva. Confira: acerte a quantidade, troque, adicione ou tire o que precisar. Vale o que você confirmar.', 'acima da lista: "Veio da Separação: ..." com os nomes: %s' % veio)
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
    if secao(5, 'Custos: o 4 confirmado (7,20, sem "estimada", nomes; lucro 167,82) e os números do mês antes e depois'):
        pg = nova()
        abrir_custos(pg)
        todos = todos_custos(pg)
        online = [x for x in todos if x.get('canal') == 'loja_virtual']
        ors = {x['id']: oraculo(x) for x in online}
        HOJE_F = FIXO.date()
        ini_mes = HOJE_F.replace(day=1)

        def do_mes(loja=None, orx=None):
            """(venda, lucro, anuncios) do mes pelo oraculo: os pedidos online do mes (e da loja) e as contas de anuncio dele."""
            sel = [x['id'] for x in online if HOJE_F - datetime.timedelta(days=x['dv']) >= ini_mes and (loja is None or x['loja'] == loja)]
            return (sum(((orx or ors)[i]['venda'] for i in sel), D(0)), sum(((orx or ors)[i]['lucro'] for i in sel), D(0)), anuncios_do_periodo(HOJE_F, ini_mes, HOJE_F, loja=loja))

        def ors_com(conf4):
            """O oraculo de todos os pedidos online com a embalagem do 4 confirmada em `conf4` (a lista (qtd, custo do dia) do registro)."""
            r = dict(ors)
            r[4] = oraculo(next(x for x in online if x['id'] == 4), confirmadas={**EMB_CONFIRMADA, 4: conf4})
            return r
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaCustos thead th')).filter(th => getComputedStyle(th).display !== 'none').map(th => th.textContent.replace(/[▲▼]/g, '').trim())")
        l = {n: linha_pedido(pg, n) for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        quer_emb = {1: ('R$ 6,60', True), 3: ('R$ 1,80', True), 4: ('R$ 7,20', True), 8: ('R$ 7,00', False), 9: ('R$ 6,80', False), 11: ('R$ 5,40', False), 12: ('R$ 7,20', False), 16: ('R$ 12,60', False)}
        ok(all(l[n]['Embalagem'] == v + (' estimada' if est else '') for n, (v, est) in quer_emb.items()), 'a coluna Embalagem: 1, 3 e 4 estimados (a marca "estimada"), 8, 9, 11, 12 e 16 confirmados: %s' % {n: l[n]['Embalagem'] for n in l})
        ok(pg.evaluate("document.querySelector('#tabelaCustos th[data-ordem=embalagem]').title").startswith('A embalagem que a Conferência de Saída confirmou') and 'até lá, uma estimativa pelo cadastro de Embalagens (a caixa que cabe e os insumos automáticos), uma por pedido' in pg.evaluate("document.querySelector('#tabelaCustos th[data-ordem=embalagem]').title"),
           'o título do cabeçalho explica: a que a Conferência confirmou; até lá, uma estimativa pelo cadastro')
        ok(perto(sum(o['embalagem'] for o in ors.values()), 54.60), 'o oráculo diz 54,60 de embalagem no mês')
        v_mes, l_mes, a_mes = do_mes()
        ok(l_mes == D('1225.23') and a_mes == 450, 'o oráculo (Decimal, taxa Bronze) dá o lucro do mês em 1.225,23 e os anúncios em 450,00: %s %s' % (l_mes, a_mes))
        ok(kpis(pg)[2:] == [br(l_mes), pct1(l_mes / v_mes * 100), br(a_mes), br(l_mes - a_mes)], 'lucro %s (margem %s), anúncios %s, lucro depois dos anúncios %s, tudo do oráculo: %s' % (br(l_mes), pct1(l_mes / v_mes * 100), br(a_mes), br(l_mes - a_mes), kpis(pg)))
        luc = {n: pg.evaluate("(n) => resultadoDoPedido(PEDIDOS.filter(p => p.id === n)[0]).lucro", n) for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        ok(all(perto(luc[n], v) for n, v in {1: 371.48, 3: -262.60, 4: 167.82, 8: 166.72, 9: 159.20, 11: -33.73, 12: 221.85, 16: 434.49}.items()), 'o lucro de cada pedido: %s' % luc)
        ok(all(perto(luc[n], ors[n]['lucro']) for n in luc), 'e bate com o oráculo, pedido a pedido')
        for loja in (1, 2):
            v_l, l_l, a_l = do_mes(loja)
            pg.evaluate("(l) => { fLoja = l; render(); }", str(loja))
            k = kpis(pg)
            ok(k[2] == br(l_l) and k[5] == br(l_l - a_l), 'loja %s: lucro %s, depois dos anúncios %s (do oráculo): %s' % (loja, br(l_l), br(l_l - a_l), k))
        pg.evaluate("fLoja = 'todos'; render();")
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(150)
        ok(sorted(int(re.search(r'nº (\d+)', x).group(1)) for x in pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr td:first-child')).map(t => t.innerText)")) == sorted(i for i, o in ors.items() if abaixo_da_margem(o, 15)) == [3, 11], '"Abaixo da margem" a 15%: o 3 e o 11 (o 16 saiu: com a taxa Bronze a margem dele é 18,8%)')
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(100)
        pg.evaluate("(() => { const p = JSON.parse(localStorage.getItem('deskParametros') || '{}'); p.margemMinimaPct = 20; localStorage.setItem('deskParametros', JSON.stringify(p)); render(); })()")
        pg.click('[data-kpi="abaixo"]'); pg.wait_for_timeout(150)
        ok(sorted(int(re.search(r'nº (\d+)', x).group(1)) for x in pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr td:first-child')).map(t => t.innerText)")) == sorted(i for i, o in ors.items() if abaixo_da_margem(o, 20)) == [1, 3, 11, 16], 'e a 20% são o 1, o 3, o 11 e o 16 (o 12 saiu: a margem dele é 21,7%)')
        # o painel do 11: os nomes
        abrir_custos(pg)
        pg.click('#corpoTabela tr[data-id="11"]'); pg.wait_for_timeout(300)
        painel = pg.inner_text('#eventDrawer').replace('\n', ' ')
        ok('1 Caixa de Encomenda Flex M + 1 Tag Desk Shope + 1 Fita adesiva' in painel and 'estimada' not in painel, 'o painel do 11 mostra a embalagem pelos nomes, sem "estimada"')
        pg.click('#drawerClose'); pg.wait_for_timeout(200)
        pg.click('#corpoTabela tr[data-id="1"]'); pg.wait_for_timeout(300)
        ok('estimada pelo cadastro: 1 Caixa de Encomenda Flex G + 1 Tag Desk Shope + 1 Fita adesiva. O custo final entra quando a Conferência de Saída fechar' in pg.inner_text('#eventDrawer').replace('\n', ' '),
           'o painel do 1 diz "estimada pelo cadastro: 1 Caixa de Encomenda Flex G + 1 Tag Desk Shope + 1 Fita adesiva. O custo final entra quando a Conferência de Saída fechar"')
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
        conf4 = dict(EMB_CONFIRMADA); conf4[4] = [(1, '6.30'), (1, '0.60'), (1, '0.30')]
        todos = todos_custos(pg)
        l4_or = oraculo(next(x for x in todos if x['id'] == 4), confirmadas=conf4)['lucro']
        ok(perto(l4_or, 167.82), 'o oráculo (embalagem confirmada, com Decimal) dá 167,82')
        ok(l4['Lucro'] == br(l4_or), 'lucro do 4 = 167,82: %s' % l4['Lucro'])
        _, l_c, a_c = do_mes(orx=ors_com(conf4[4]))
        ok(kpis(pg)[2] == br(l_c) and kpis(pg)[5] == br(l_c - a_c) and l_c == l_mes, 'o lucro do mês não muda (1.225,23; depois dos anúncios 775,23): o 4 estimado e o confirmado dão 7,20 porque a Conferência confirmou o que o cadastro sugeria: %s' % kpis(pg))
        ok(sum(oraculo(x, confirmadas=conf4)['embalagem'] for x in todos if x.get('canal') == 'loja_virtual') == D('54.60'), 'a embalagem do mês segue 54,60 (o 4 estimado em 7,20 virou confirmado em 7,20)')
        pg.click('#corpoTabela tr[data-id="4"]'); pg.wait_for_timeout(300)
        painel = pg.inner_text('#eventDrawer').replace('\n', ' ')
        ok('1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva' in painel and 'estimada' not in painel and 'Trocada na conferência' not in painel, 'o painel do 4 tem os nomes que a Conferência confirmou, sem troca')
        pg.context.close()
        # trocando a CE-02 pela Flex M e tirando a fita: o 4 vai a 5,30 e o total a 1.052,58
        pg = nova()
        separar4(pg)
        def trocar():
            escolher(pg, '#emb-0', 2)
            pg.click('[data-ins-rem="1"]'); pg.wait_for_timeout(200)
        conferir4(pg, trocar)
        abrir_custos(pg)
        l4 = linha_pedido(pg, 4)
        ors_t = ors_com([(1, '4.70'), (1, '0.60')])
        _, l_t, _ = do_mes(orx=ors_t)
        ok(ors_t[4]['embalagem'] == D('5.30') and ors_t[4]['lucro'] == D('169.72') and l_t == D('1227.13'), 'o oráculo: Flex M 4,70 + tag Brands 0,60 = 5,30, lucro do 4 em 169,72 e o total do mês em 1.227,13: %s %s %s' % (ors_t[4]['embalagem'], ors_t[4]['lucro'], l_t))
        ok(l4['Embalagem'] == br(ors_t[4]['embalagem']) and l4['Lucro'] == br(ors_t[4]['lucro']) and kpis(pg)[2] == br(l_t), 'trocando a CE-02 pela Flex M e tirando a fita: o 4 vai a 5,30, lucro 169,72, e o total a 1.227,13: %s %s %s' % (l4['Embalagem'], l4['Lucro'], kpis(pg)[2]))
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
        conf4 = dict(EMB_CONFIRMADA); conf4[4] = [(1, '6.30'), (1, '0.60'), (1, '0.30')]   # o registro guardou os preços de antes da mudança
        l4_or = oraculo(next(x for x in todos_custos(pg) if x['id'] == 4), confirmadas=conf4)['lucro']
        ok(l4['Embalagem'] == 'R$ 7,20' and l4['Lucro'] == br(l4_or) and perto(l4_or, 167.82), 'o 4, confirmado antes, segue em 7,20 (lucro 167,82, do oráculo): o pedido guardou o custo do dia: %s %s' % (l4['Embalagem'], l4['Lucro']))
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
    if secao(7, 'Configurar não tem o campo de embalagem; o valor antigo por loja é ignorado e some ao salvar; o log não cita embalagem'):
        pg = nova()
        abrir_custos(pg)
        SIT = "['aberto', 'aprovado', 'separacao', 'conferenciasaida', 'faturado', 'prontoenvio', 'enviado', 'entregue']"
        pg.evaluate("() => localStorage.setItem('deskParametros', JSON.stringify({ custosEcommerce: { situacoes: " + SIT + ", custoBase: 'compra', embalagemPorLoja: { 1: 99, 2: 88, 3: 77 } } }))")
        abrir_custos(pg)
        e = {n: linha_pedido(pg, n)['Embalagem'] for n in (1, 3, 4, 8, 9, 11, 12, 16)}
        ok(e[1] == 'R$ 6,60 estimada' and e[3] == 'R$ 1,80 estimada' and e[4] == 'R$ 7,20 estimada', 'o valor antigo por loja (99 / 88 / 77) gravado no navegador é ignorado: a estimada é a do cadastro: %s' % e)
        ok(e[8] == 'R$ 7,00' and e[11] == 'R$ 5,40' and e[16] == 'R$ 12,60' and e[9] == 'R$ 6,80' and e[12] == 'R$ 7,20', 'e os confirmados seguem os mesmos: %s' % e)
        pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#menuMaisAcoes [data-acao="configurar"]'); pg.wait_for_timeout(250)
        rot = pg.inner_text('#cfgDrawer')
        ok('mbalagem' not in rot and 'Por loja' not in rot and pg.evaluate("!document.getElementById('campoCfgEmbalagem') && !document.getElementById('cfgEmbalagem') && !document.getElementById('erroCfgEmbalagem')"),
           'Configurar não tem o campo "Embalagem estimada por loja", nem a dica, nem o erro')
        pg.click('#btnAplicarCfg'); pg.wait_for_timeout(300)
        g = ls(pg, 'deskParametros')['custosEcommerce']
        ok(sorted(g.keys()) == ['custoBase', 'situacoes'], 'ao Aplicar, só ficam situações e custo base: o valor antigo por loja sai: %s' % g)
        det = pg.evaluate("JSON.parse(localStorage.getItem('deskLog'))[0].detalhe")
        ok('mbalagem' not in det and det.startswith('Situações: 8 de 9'), 'o texto do registro de atividades não cita embalagem: %s' % det)
        pg.context.close()

    # ================================================================ 8. pagina do pedido
    if secao(8, 'A página do pedido: nomes, "estimada", troca'):
        pg = nova()
        ir(pg, PV_D, '?id=11')
        cx = pg.inner_text('#caixaResultado').replace('\n', ' ')
        ok('1 Caixa de Encomenda Flex M + 1 Tag Desk Shope + 1 Fita adesiva' in cx and 'R$ 5,40' in cx and 'estimada' not in cx, 'o pedido 11 mostra a embalagem pelos nomes: %s' % cx[cx.index('Embalagem'):cx.index('Embalagem') + 100])
        ir(pg, PV_D, '?id=1')
        cx = pg.inner_text('#caixaResultado').replace('\n', ' ')
        ok('estimada pelo cadastro: 1 Caixa de Encomenda Flex G + 1 Tag Desk Shope + 1 Fita adesiva. O custo final entra quando a Conferência de Saída fechar' in cx and 'R$ 6,60' in cx,
           'o pedido 1 diz "estimada pelo cadastro: 1 Caixa de Encomenda Flex G + 1 Tag Desk Shope + 1 Fita adesiva. O custo final entra quando a Conferência de Saída fechar"')
        ir(pg, PV_D, '?id=4')
        ok('estimada' in pg.inner_text('#caixaResultado'), 'o pedido 4 ainda não confirmado também é estimado')
        ok('a embalagem escolhida na Separação é confirmada antes de a nota sair' in pg.evaluate("PROXIMO_PASSO.separacao.texto"), 'o texto do passo diz que a embalagem escolhida na Separação é confirmada na Conferência de Saída: %s' % pg.evaluate("PROXIMO_PASSO.separacao.texto")[:150])
        # Nome do cadastro com "<" nao vira HTML na pagina do pedido: nem estimado, nem confirmado com troca.
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].nome = 'Caixa <img src=x>'; embalagensGravar(L); }")
        ir(pg, PV_D, '?id=1')
        ok(pg.locator('#caixaResultado img').count() == 0 and 'Caixa <img src=x>' in pg.inner_text('#caixaResultado'), 'nome com "<" aparece como texto na estimativa, sem virar HTML')
        pg.evaluate("() => localStorage.setItem('deskEmbalagensPedido', JSON.stringify({ 1: { situacao: 'confirmada', itens: [{ id: 3, nome: 'Caixa <img src=x>', tipo: 'pacote', qtd: 1, custo: 5.9 }], trocas: ['Flex M → Caixa <img src=x>'] } }))")
        ir(pg, PV_D, '?id=1')
        cx = pg.inner_text('#caixaResultado')
        ok(pg.locator('#caixaResultado img').count() == 0 and 'Trocada na conferência: Flex M → Caixa <img src=x>' in cx, 'nome com "<" aparece como texto na embalagem confirmada e na troca, sem virar HTML')
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
    if secao(9, 'Blocos idênticos: EMBALAGENS: LEITURA nas 10 telas, o da Conferência nas 2, o pedido 4 igual nas FILAs'):
        IN, FIM = '  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA ====='
        n5 = ['pagina-vendas-custos-ecommerce.html', PV_D, 'pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html']
        nove = [bloco(fonte(n), IN, FIM) for n in (CAD, SEP_F, CONF_F, PROD_D, NC) + tuple(n5)]
        ok(len(nove) == 10 and all(x == nove[0] for x in nove) and 'function sugerirEmbalagem(lista, pecas)' in nove[0] and 'function embResumo' in nove[0] and 'function embBaixar' in nove[0] and 'function embCustoUso' in nove[0] and 'Identico em 10 telas' in nove[0],
           'o bloco EMBALAGENS: LEITURA é idêntico nas 10 telas: Cadastro, Separação, Conferência, a ficha do produto, Necessidades de Compra e as 5 do RESULTADO DO PEDIDO')
        ok(all(fonte(n).index(IN) < fonte(n).index('  // ===== RESULTADO DO PEDIDO (bloco comum') for n in n5), 'e nas 5 do RESULTADO DO PEDIDO ele vem ANTES do bloco da conta (o const já está inicializado)')
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
        ok(all('RES_EMBALAGENS_EXEMPLO' in fonte(n) and 'function resEmbalagem(p)' in fonte(n) and 'embalagemPorLoja' not in fonte(n) for n in n5), 'as 5 telas do RESULTADO DO PEDIDO trazem o exemplo confirmado e resEmbalagem (o bloco inteiro é comparado em teste_custos_ecommerce.py)')
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
            al = pg.evaluate("""() => { const i = document.getElementById('inputTotalVolumes').getBoundingClientRect(), b = document.getElementById('btnAddVolume').getBoundingClientRect();
                return { visivel: i.width > 0, dentro: i.right <= window.innerWidth, dy: Math.abs((i.top + i.bottom) / 2 - (b.top + b.bottom) / 2) }; }""")
            ok(al['visivel'] and al['dentro'] and al['dy'] <= 3, 'Conferência a %d px: o campo Total de volumes aparece, cabe na tela e fica alinhado com o botão Adicionar volume: %s' % (w, al))
            pg.context.close()

    # ================================================================ 11. estimativa pelo cadastro, sem trava, total de volumes, teto
    def emb_custos(pg, ns=(1, 3, 4, 8, 9, 11, 12, 16)):
        return {n: linha_pedido(pg, n)['Embalagem'] for n in ns}

    def cadastro_com(*mud, todos=None):
        """O CADASTRO_EMB do oraculo com `mud` = (id, posicao, valor) trocados (posicao 3 = status, 4 = cap, 5 = custo); `todos` = (posicao, valor) em todas as linhas."""
        lista = [list(e) for e in CADASTRO_EMB]
        for e in lista:
            if todos:
                e[todos[0]] = todos[1]
        for i, k, v in mud:
            [e for e in lista if e[0] == i][0][k] = v
        return [tuple(e) for e in lista]

    def painel_custos(pg, n):
        pg.click('#corpoTabela tr[data-id="%d"]' % n); pg.wait_for_timeout(300)
        t_ = pg.inner_text('#eventDrawer').replace('\n', ' ')
        pg.click('#drawerClose'); pg.wait_for_timeout(200)
        return t_

    def editar_cad(pg, busca, **campos):
        pg.fill('#campoBusca', busca); pg.wait_for_timeout(150)
        pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(300)
        for k, v in campos.items():
            pg.fill('#input' + k, v)
        pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(250)

    if secao(11, 'A estimativa pelo cadastro: custo, "cabe até", cadastro vazio; a Separação não mexe no custo; sem trava de capacidade; Total de volumes; teto de 999'):
        # a. mudar o custo no cadastro mexe nos estimados (1, 3, 4) e nao nos confirmados (8, 11, 16)
        pg = nova()
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        editar_cad(pg, 'Flex G', Custo='7,00'); editar_cad(pg, 'Pequeno', Custo='2,00'); editar_cad(pg, 'CE-02', Custo='9,00')
        abrir_custos(pg)
        e = emb_custos(pg)
        ok(e[1] == 'R$ 7,70 estimada' and e[3] == 'R$ 2,70 estimada' and e[4] == 'R$ 9,90 estimada', 'custo novo no cadastro (Flex G 7,00, Envelope Pequeno 2,00, CE-02 9,00) mexe nos estimados: 1 = 7,70, 3 = 2,70, 4 = 9,90: %s' % e)
        ok(e[8] == 'R$ 7,00' and e[11] == 'R$ 5,40' and e[16] == 'R$ 12,60', 'e não mexe nos confirmados: 8 = 7,00, 11 = 5,40, 16 = 12,60: %s' % e)
        todos = {x['id']: x for x in todos_custos(pg)}
        mod = cadastro_com((3, 5, '7.00'), (7, 5, '2.00'), (5, 5, '9.00'))
        ok(all(perto(oraculo(todos[n], cadastro=mod)['embalagem'], v) for n, v in ((1, 7.70), (3, 2.70), (4, 9.90), (8, 7), (11, 5.40), (16, 12.60))), 'e o oráculo, refeito com Decimal sobre o cadastro novo, concorda')
        pg.context.close()
        # b. mudar o "cabe ate" muda a caixa da estimativa
        pg = nova()
        ir(pg, CAD)
        pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(150)
        editar_cad(pg, 'Flex G', Cap='7')
        abrir_custos(pg)
        e = emb_custos(pg, (1, 3, 4))
        ok(e[1] == 'R$ 7,00 estimada' and e[3] == 'R$ 1,80 estimada' and e[4] == 'R$ 7,20 estimada', 'Flex G passa a caber 7: o 1 (8 peças) deixa de caber nela e vai para a CE-02 (6,30 + 0,40 + 0,30 = 7,00); 3 e 4 seguem: %s' % e)
        ok('estimada pelo cadastro: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Shope + 1 Fita adesiva.' in painel_custos(pg, 1), 'e o painel do 1 diz a caixa nova')
        todos = {x['id']: x for x in todos_custos(pg)}
        ok(perto(oraculo(todos[1], cadastro=cadastro_com((3, 4, 7)))['embalagem'], 7.00), 'o oráculo concorda (7,00)')
        pg.context.close()
        # c. sem nenhum "cabe ate": so os insumos, com a marca, sem erro de JS; sem caixa nem insumo: zero, com a marca
        pg = nova()
        abrir_custos(pg)
        n_erros = len(erros)
        pg.evaluate("() => { const l = embalagensLer(); l.forEach(e => { delete e.cap; }); embalagensGravar(l); }")
        abrir_custos(pg)
        e = emb_custos(pg, (1, 3, 4, 8))
        ok(e[1] == 'R$ 0,70 estimada' and e[3] == 'R$ 0,70 estimada' and e[4] == 'R$ 0,90 estimada' and e[8] == 'R$ 7,00', 'sem nenhum "cabe até" no cadastro a estimativa é só dos insumos (Shope 0,70, Brands 0,90), com a marca: %s' % e)
        ok('estimada pelo cadastro: 1 Tag Desk Shope + 1 Fita adesiva.' in painel_custos(pg, 1), 'e o painel diz só os insumos')
        todos = {x['id']: x for x in todos_custos(pg)}
        sem_cap = cadastro_com(todos=None)
        sem_cap = [(x[0], x[1], x[2], x[3], None, x[5], x[6]) for x in sem_cap]
        ok(perto(oraculo(todos[1], cadastro=sem_cap)['embalagem'], 0.70) and perto(oraculo(todos[4], cadastro=sem_cap)['embalagem'], 0.90), 'o oráculo concorda (0,70 e 0,90)')
        pg.evaluate("() => { const l = embalagensLer(); l.forEach(e => { e.status = 'inativo'; }); embalagensGravar(l); }")
        abrir_custos(pg)
        e = emb_custos(pg, (1, 3, 4, 8))
        ok(e[1] == 'R$ 0,00 estimada' and e[3] == 'R$ 0,00 estimada' and e[4] == 'R$ 0,00 estimada' and e[8] == 'R$ 7,00', 'sem caixa nem insumo ativo o valor é 0,00, a marca fica e a tela abre: %s' % e)
        ok('estimada: nada no cadastro para sugerir' in painel_custos(pg, 1), 'e o painel diz "estimada: nada no cadastro para sugerir"')
        ir(pg, PV_D, '?id=1')
        ok('estimada: nada no cadastro para sugerir' in pg.inner_text('#caixaResultado').replace('\n', ' '), 'a página do pedido também')
        ok(len(erros) == n_erros, 'nenhum erro de JavaScript com o cadastro sem "cabe até" e vazio: %s' % erros[n_erros:])
        pg.context.close()

        # e. a Separacao escolheu 3 caixas CE-02: o custo segue a estimativa; a Conferencia fecha com as 3
        pg = nova()
        separar4(pg, antes=lambda: (pg.fill('[data-emb-qtd="0"]', '3'), pg.press('[data-emb-qtd="0"]', 'Tab'), pg.wait_for_timeout(200)))
        r = reg(pg)
        ok(r and r['situacao'] == 'separada' and [(i['id'], i['qtd']) for i in r['itens']] == [(5, 3), (12, 1), (13, 1)], 'a Separação guardou 3 caixas CE-02: %s' % (r and [(i['id'], i['qtd']) for i in r['itens']]))
        abrir_custos(pg)
        l4 = linha_pedido(pg, 4)
        l4_or = oraculo(next(x for x in todos_custos(pg) if x['id'] == 4))['lucro']   # sem registro confirmado: a estimativa do cadastro (7,20)
        ok(l4['Embalagem'] == 'R$ 7,20 estimada' and l4['Lucro'] == br(l4_or) and perto(l4_or, 167.82), 'o 4 "separado" com 3 caixas segue na estimativa do cadastro (7,20, com a marca): quem decide é a Conferência: %s' % l4['Embalagem'])
        ir(pg, PV_D, '?id=4')
        ok('estimada pelo cadastro: 1 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva.' in pg.inner_text('#caixaResultado').replace('\n', ' '), 'a página do pedido também (uma caixa, não as 3 da Separação)')
        ir(pg, CONF_F, '?id=4')
        ok(len(volumes_conf(pg)) == 3, 'a Conferência abre com os 3 volumes da Separação')
        t = conferir4(pg)
        ok('Embalagem confirmada: 3 Caixa de Encomenda CE-02 + 1 Tag Desk Brands + 1 Fita adesiva.' in t and 'trocada' not in t, 'e fecha com as 3, sem troca: %s' % t[-110:])
        abrir_custos(pg)
        l4 = linha_pedido(pg, 4)
        conf4 = dict(EMB_CONFIRMADA); conf4[4] = [(3, '6.30'), (1, '0.60'), (1, '0.30')]
        todos = {x['id']: x for x in todos_custos(pg)}
        ok(l4['Embalagem'] == 'R$ 19,80' and perto(oraculo(todos[4], confirmadas=conf4)['embalagem'], 19.80) and l4['Lucro'] == br(oraculo(todos[4], confirmadas=conf4)['lucro']), 'confirmado, o 4 custa 3 × 6,30 + 0,60 + 0,30 = 19,80, sem a marca "estimada": %s' % l4['Embalagem'])
        pg.context.close()

        # f. sem trava de capacidade: o Envelope Pequeno (cabe 1) para as 10 pecas passa na Separacao e na Conferencia
        pg = nova()
        t = separar4(pg, antes=lambda: escolher(pg, '#emb-sel-0', 7))
        r = reg(pg)
        ok(r and r['situacao'] == 'separada' and r['itens'][0]['id'] == 7 and 'Embalagem: 1 Envelope de Segurança Pequeno + 1 Tag Desk Brands + 1 Fita adesiva.' in t, 'a Separação aceita o Envelope Pequeno para 10 peças, sem aviso de capacidade: %s' % t[-110:])
        ir(pg, CONF_F, '?id=4')
        ok(volumes_conf(pg) == [['Envelope de Segurança Pequeno', 'escolhida na separação']], 'a Conferência abre com o envelope: %s' % volumes_conf(pg))
        t = conferir4(pg)
        r = reg(pg)
        ok(r and r['situacao'] == 'confirmada' and [(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(7, 1, 1.1), (12, 1, 0.6), (13, 1, 0.3)] and 'trocada' not in t, 'e fecha com ele, sem travar: %s' % (r and [(i['id'], i['qtd']) for i in r['itens']]))
        abrir_custos(pg)
        ok(linha_pedido(pg, 4)['Embalagem'] == 'R$ 2,00', 'o custo é 1,10 + 0,60 + 0,30 = 2,00: %s' % linha_pedido(pg, 4)['Embalagem'])
        pg.context.close()

        # g. Separacao com 300 caixas: a Conferencia abre 300 linhas; o Total de volumes acerta; a troca vira UMA entrada
        def sep300():
            p_ = nova()
            separar4(p_, antes=lambda: (p_.fill('[data-emb-qtd="0"]', '300'), p_.press('[data-emb-qtd="0"]', 'Tab'), p_.wait_for_timeout(250)))
            return p_
        pg = sep300()
        ok(reg(pg)['itens'][0]['qtd'] == 300, 'a Separação guardou 300 caixas')
        ir(pg, CONF_F, '?id=4')
        ok(pg.locator('#listaVolumes .vol-linha').count() == 300 and pg.input_value('#inputTotalVolumes') == '300' and pg.locator('#campoTotalVolumes').is_visible(), 'a Conferência abre 300 linhas e o campo Total de volumes mostra 300')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        pg.fill('#inputTotalVolumes', '1'); pg.press('#inputTotalVolumes', 'Tab'); pg.wait_for_timeout(300)
        ok(pg.locator('#listaVolumes .vol-linha').count() == 1 and pg.input_value('#inputTotalVolumes') == '1' and volumes_conf(pg) == [['Caixa de Encomenda CE-02', 'escolhida na separação']], 'Total de volumes em 1 deixa 1 linha (as últimas saem)')
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        t = modal(pg)
        ok('Embalagem trocada: − 299 Caixa de Encomenda CE-02.' in t, 'o modal diz "− 299 Caixa de Encomenda CE-02", numa entrada só: %s' % t[:200])
        confirmar(pg); confirmar(pg)
        r = reg(pg)
        ok(r and r['situacao'] == 'confirmada' and r['trocas'] == ['− 299 Caixa de Encomenda CE-02'] and [(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(5, 1, 6.3), (12, 1, 0.6), (13, 1, 0.3)],
           'o registro grava uma troca só e 1 caixa: %s' % (r and r['trocas']))
        log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(x => x.chave === 'confSaidaFecha')")
        ok(len(log) == 1 and '− 299 Caixa de Encomenda CE-02' in log[0]['detalhe'] and len(log[0]['detalhe']) <= 180, 'e a troca cabe inteira nos 180 caracteres do Registro de atividades (%d): %s' % (len(log[0]['detalhe']), log[0]['detalhe']))
        ir(pg, CONF_F, '?id=4')
        ok(not pg.locator('#campoTotalVolumes').is_visible() and not pg.locator('#inputTotalVolumes').is_visible() and not pg.locator('#btnAddVolume').is_visible(), 'com a conferência fechada o campo Total de volumes não aparece (nem o Adicionar volume)')
        pg.context.close()
        # ... 300 -> 1 -> 3, mais os limites do campo
        pg = sep300()
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        for digitado, esperado in (('0', 300), ('', 300), ('abc', 300), ('5000', 999)):
            pg.fill('#inputTotalVolumes', digitado); pg.press('#inputTotalVolumes', 'Tab'); pg.wait_for_timeout(300)
            if digitado == '5000':
                ok(pg.evaluate("VOLUMES.length") == 999 and pg.input_value('#inputTotalVolumes') == '999', 'digitar 5000 limita a 999 linhas')
            else:
                ok(pg.evaluate("VOLUMES.length") == esperado and pg.input_value('#inputTotalVolumes') == str(esperado), 'Total de volumes "%s" volta ao atual (%d)' % (digitado, esperado))
        pg.fill('#inputTotalVolumes', '1'); pg.press('#inputTotalVolumes', 'Tab'); pg.wait_for_timeout(300)
        pg.fill('#inputTotalVolumes', '3'); pg.press('#inputTotalVolumes', 'Tab'); pg.wait_for_timeout(300)
        v3 = pg.evaluate("VOLUMES.map(v => [v.emb, v.nome, v.peso, v.sugerida, v.origem])")
        ok(len(v3) == 3 and v3[0][0] == 5 and v3[1:] == [[5, 'Caixa de Encomenda CE-02', '', '', None]] * 2 and pg.locator('#listaVolumes .vol-linha').count() == 3, 'de 1 para 3 as três linhas têm a mesma caixa (a da última), sem peso: %s' % v3[:2])
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        confirmar(pg); confirmar(pg)
        r = reg(pg)
        ok(r and r['trocas'] == ['− 297 Caixa de Encomenda CE-02'] and [(i['id'], i['qtd']) for i in r['itens']] == [(5, 3), (12, 1), (13, 1)], 'e fechar com 3 grava 3 caixas e a troca "− 297 Caixa de Encomenda CE-02": %s' % (r and r['trocas']))
        pg.context.close()
        # ... outra caixa na ultima linha e depois 3 volumes: as 3 com a nova; a troca agrupa o que sobra ("+ 2 ...")
        pg = nova()
        separar4(pg)
        ir(pg, CONF_F, '?id=4')
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); confirmar(pg)
        ok(pg.locator('#campoTotalVolumes').is_visible() and pg.input_value('#inputTotalVolumes') == '1', 'com 1 volume o campo mostra 1')
        escolher(pg, '#emb-0', 2)
        pg.fill('#inputTotalVolumes', '3'); pg.press('#inputTotalVolumes', 'Tab'); pg.wait_for_timeout(300)
        ok(pg.evaluate("VOLUMES.map(v => v.emb)") == [2, 2, 2] and pg.evaluate("Array.from(document.querySelectorAll('#listaVolumes .vol-numero')).map(x => x.textContent)") == ['1 de 3', '2 de 3', '3 de 3'], 'trocada a caixa do único volume, subir para 3 repete a Flex M nas três e renumera "1 de 3"')
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        confirmar(pg); confirmar(pg)
        r = reg(pg)
        ok(r and r['trocas'] == ['Caixa de Encomenda CE-02 → Caixa de Encomenda Flex M', '+ 2 Caixa de Encomenda Flex M'] and [(i['id'], i['qtd']) for i in r['itens']] == [(2, 3), (12, 1), (13, 1)],
           'a troca é "CE-02 → Flex M" e as que sobraram vêm numa entrada só, "+ 2 Caixa de Encomenda Flex M": %s' % (r and r['trocas']))
        un = pg.evaluate("""() => { const c = (id, nome, qtd) => ({ id: id, nome: nome, tipo: 'pacote', qtd: qtd });
            return [embTrocas([c(5, 'A', 300), c(2, 'B', 2)], [c(5, 'A', 1), c(2, 'B', 5)]), embTrocas([c(5, 'A', 4)], [c(2, 'B', 1)]), embTrocas([c(5, 'A', 2)], [c(5, 'A', 2)])]; }""")
        ok(un[0] == ['A → B', 'A → B', 'A → B', '− 296 A'] and un[1] == ['A → B', '− 3 A'] and un[2] == [], 'embTrocas: as sobras agrupadas por nome com a quantidade certa e nada quando não mudou: %s' % un)
        pg.context.close()

        # h. teto de 999 nas quantidades da Separacao e da Conferencia
        pg = nova()
        def teto_sep():
            pg.fill('[data-emb-qtd="0"]', '5000'); pg.press('[data-emb-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
            a1 = pg.input_value('[data-emb-qtd="0"]')
            pg.fill('[data-ins-qtd="0"]', '5000'); pg.press('[data-ins-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
            a2 = pg.input_value('[data-ins-qtd="0"]')
            ok(a1 == '999' and a2 == '999', 'Separação: 5000 na quantidade da embalagem e do insumo vira 999 ao sair do campo: %s %s' % (a1, a2))
            pg.fill('[data-emb-qtd="0"]', '1'); pg.press('[data-emb-qtd="0"]', 'Tab'); pg.fill('[data-ins-qtd="0"]', '1'); pg.press('[data-ins-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
        separar4(pg, antes=teto_sep)
        ir(pg, CONF_F, '?id=4')
        pg.fill('[data-ins-qtd="0"]', '5000'); pg.press('[data-ins-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
        ok(pg.input_value('[data-ins-qtd="0"]') == '999' and pg.evaluate("INS_LINHAS[0].qtd") == 999, 'Conferência: 5000 na quantidade do insumo vira 999')
        pg.fill('[data-ins-qtd="0"]', '0'); pg.press('[data-ins-qtd="0"]', 'Tab'); pg.wait_for_timeout(200)
        ok(pg.input_value('[data-ins-qtd="0"]') == '1', 'e zero segue voltando para 1')
        pg.context.close()

    if secao(12, 'O painel do cadastro de Embalagens: Largura, Altura e Comprimento na mesma linha (02/nov/2026)'):
        # O painel tinha 400 px e "Comprimento (cm)" quebrava em duas linhas, jogando o campo para baixo dos outros. Agora tem 540 px.
        for w in (1280, 1440):
            pg = nova(w, 900, fixo=False)
            ir(pg, CAD); pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(500)
            for tipo, quantos in (('pacote', 3), ('envelope', 2), ('rolo', 2)):
                if tipo != 'pacote':
                    pg.evaluate("(t) => document.querySelector('#inputTipoEmbalagem .dropdown-select-item[data-value=\"' + t + '\"]').click()", tipo); pg.wait_for_timeout(200)
                m = pg.evaluate("""() => { const d = document.getElementById('eventDrawer').getBoundingClientRect();
                  const c = Array.from(document.querySelectorAll('#camposDimensoes .form-field')).map(f => ({ rot: f.querySelector('label').getBoundingClientRect(), cx: f.querySelector('input').getBoundingClientRect() }));
                  const fora = Array.from(document.querySelectorAll('#eventDrawer input, #eventDrawer .dropdown-select-btn')).filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > d.right - 20).length;
                  return { n: c.length, linhas: c.map(x => Math.round(x.rot.height)), topos: c.map(x => Math.round(x.cx.top * 10) / 10), fora: fora, direita: Math.round(d.right), janela: innerWidth,
                           rolagem: document.documentElement.scrollWidth - document.documentElement.clientWidth }; }""")
                ok(m['n'] == quantos and max(m['linhas']) < 20 and max(m['topos']) - min(m['topos']) < 0.5 and m['fora'] == 0 and m['rolagem'] <= 0 and m['direita'] == m['janela'],
                   'a %d px, tipo %s: %d campos de medida, rótulos numa linha só, caixas no mesmo topo, nenhum campo do painel passa da borda: %s' % (w, tipo, quantos, m))
            pg.context.close()

    # ================================================================ 13. estoque
    # O ESTOQUE das embalagens (aprovado em 30/out, feito em 03/nov/2026). O que esta secao protege:
    #   o cadastro ganha saldo (na unidade de compra, fracionario e negativo), minimo e, no insumo, "rende" (1 rolo de fita de R$ 15 que rende 50 = R$ 0,30 por pedido);
    #   Dar entrada recalcula o custo MEDIO e soma o saldo; com saldo zerado ou negativo vale so o custo da entrada; entra e fica no Registro de atividades ("Editar · Embalagens");
    #   a baixa e SO quando a Conferencia de Saida fecha (a Separacao nao baixa), uma vez por pedido (ficha reaberta nao baixa de novo), com o custo por uso, e falta de saldo so avisa;
    #   o acerto de saldo exige motivo; ?entrada=<id> abre o painel de entrada; Necessidades de Compra lista as ativas abaixo do minimo; cadastro gravado antes do estoque migra;
    #   o custo de cada pedido de exemplo nao mudou (a fita sai 0,30) e os tres leitores do custo leem o custo por uso.
    if secao(13, 'O estoque das embalagens: entrada com custo médio, baixa na Conferência (uma vez), acerto com motivo, ?entrada=, Necessidades de Compra, migração, custo por uso'):
        def emb(pg, i):
            return next((e for e in (ls(pg, 'deskEmbalagens') or []) if e['id'] == i), None)

        def ir_cad(pg, q=''):
            ir(pg, CAD, q); pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(120)

        def log_edita(pg):
            return pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(x => x.chave === 'embalagensEditar')")

        def preencher_entrada(pg, qtd, custo, forn='', nota=''):
            pg.fill('#entradaQtd', qtd); pg.fill('#entradaCusto', custo)
            if forn: pg.fill('#entradaFornecedor', forn)
            if nota: pg.fill('#entradaNota', nota)
            pg.wait_for_timeout(150)

        def meta(pg, i):
            return pg.evaluate("(i) => document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"' + i + '\"] .embalagens-meta').textContent", i)

        def mostra(pg, sel):
            return pg.evaluate("(s) => document.querySelector(s).classList.contains('show')", sel)

        def grava_cadastro(pg, mexe):
            """Muda o cadastro no navegador: `mexe` e o corpo JS de uma funcao que recebe a lista (por id)."""
            pg.evaluate("(m) => { const L = embalagensLer(); const por = (i) => L.filter(e => e.id === i)[0]; new Function('por', m)(por); embalagensGravar(L); }", mexe)

        # ---- 13a. Dar entrada: o botao, a validacao, o custo medio, o Registro de atividades
        pg = nova()
        ir_cad(pg)
        ok(pg.evaluate("document.getElementById('btnDarEntrada').classList.contains('btn-secundario') && document.getElementById('btnNovaEmbalagem').classList.contains('btn-primary') && (() => { const a = document.getElementById('btnDarEntrada').getBoundingClientRect(), b = document.getElementById('btnNovaEmbalagem').getBoundingClientRect(); return Math.abs(a.top - b.top) < 2 && a.right <= b.left; })()"),
           '"Dar entrada" é o botão secundário, ao lado de "Nova Embalagem" no cabeçalho')
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(350)
        ok(pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')"), 'o botão abre o painel lateral de entrada')
        itens = [x.strip() for x in pg.locator('#entradaEmb .dropdown-select-item').all_inner_texts()]
        ok(len(itens) == 13 and 'Fita adesiva' in itens and 'Tag Desk Brands' in itens and 'Rolo para Tecido' not in itens, 'o dropdown lista só as ativas, insumos inclusive (13 de 14; o rolo inativo fica de fora): %s' % itens)
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroEntradaEmb') and mostra(pg, '#erroEntradaQtd') and mostra(pg, '#erroEntradaCusto') and ls(pg, 'deskEmbalagens') is None and log_edita(pg) == [], 'salvar vazio avisa a embalagem, a quantidade e o custo e não grava nada')
        escolher(pg, '#entradaEmb', 13)
        for ruim in ('0', 'abc', '-2'):
            pg.fill('#entradaQtd', ruim); pg.fill('#entradaCusto', '1,00'); pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(120)
            ok(mostra(pg, '#erroEntradaQtd') and emb(pg, 13) is None, 'quantidade "%s" dá erro e não grava' % ruim)
        pg.fill('#entradaQtd', '2'); pg.fill('#entradaCusto', ''); pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(120)
        ok(mostra(pg, '#erroEntradaCusto') and not mostra(pg, '#erroEntradaQtd') and ls(pg, 'deskEmbalagens') is None, 'o custo da unidade é obrigatório')
        preencher_entrada(pg, '2', '17,00', 'Papelaria Central', 'NF 1234')
        ok(pg.inner_text('#entradaPrevia') == 'Saldo 8 → 10 · custo R$ 15,00 → R$ 15,40 (médio)', 'a prévia mostra o saldo e o custo médio: %s' % pg.inner_text('#entradaPrevia'))
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        f = emb(pg, 13)
        ok(f and f['saldo'] == 10 and perto(f['custo'], 15.40) and f['rende'] == 50 and not pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')"),
           'salvar soma a quantidade ao saldo (8 → 10), grava o custo médio (15,40) no cadastro, mantém o rende e fecha o painel: %s' % f)
        ok(meta(pg, 13) == 'R$ 15,40 a unidade · rende 50 (R$ 0,31 por pedido) · entra sozinho: todas as lojas · Saldo 10 · mín. 4', 'a lista mostra o saldo novo e o custo por pedido (15,40 ÷ 50): %s' % meta(pg, 13))
        lg = log_edita(pg)
        ok(len(lg) == 1 and lg[0]['acao'] == 'Editar · Embalagens' and lg[0]['senha'] is False and 'Entrada de 2 Fita adesiva a R$ 17,00 a unidade.' in lg[0]['detalhe'] and 'Fornecedor: Papelaria Central.' in lg[0]['detalhe'] and 'Nota: NF 1234.' in lg[0]['detalhe']
           and 'Saldo 8 → 10' in lg[0]['detalhe'] and 'R$ 15,00 → R$ 15,40' in lg[0]['detalhe'], 'a entrada vai para o Registro de atividades como "Editar · Embalagens", com quantidade, custo, fornecedor, nota e o antes e depois: %s' % (lg and lg[0]['detalhe']))
        # a segunda entrada pondera de novo: (10 x 15,40 + 10 x 20,00) / 20 = 17,70
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.getElementById('entradaFornecedor').value + document.getElementById('entradaNota').value + document.getElementById('entradaQtd').value") == '' and pg.evaluate("document.getElementById('entradaEmb').getAttribute('data-value')") == '', 'o painel abre limpo da vez seguinte')
        escolher(pg, '#entradaEmb', 13); preencher_entrada(pg, '10', '20,00')
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        f = emb(pg, 13)
        ok(f['saldo'] == 20 and perto(f['custo'], 17.70) and len(log_edita(pg)) == 2 and 'Fornecedor' not in log_edita(pg)[0]['detalhe'] and 'Nota' not in log_edita(pg)[0]['detalhe'], 'a segunda entrada pondera o custo (17,70) e, sem fornecedor nem nota, o registro não os cita: %s' % f)
        pg.context.close()

        # ---- 13b. saldo zerado ou negativo nao pesa no custo: vale so o custo da entrada
        pg = nova()
        ir_cad(pg)
        grava_cadastro(pg, "por(1).saldo = -4; por(2).saldo = 0;")
        ir_cad(pg)
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        escolher(pg, '#entradaEmb', 1); preencher_entrada(pg, '10', '6,00')
        ok(pg.inner_text('#entradaPrevia') == 'Saldo −4 → 6 · custo R$ 3,50 → R$ 6,00 (o da entrada: não havia saldo)', 'saldo negativo antes: a prévia diz que vale o custo da entrada: %s' % pg.inner_text('#entradaPrevia'))
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        ok(emb(pg, 1)['saldo'] == 6 and perto(emb(pg, 1)['custo'], 6.00), 'com saldo −4 a entrada de 10 deixa 6 e o custo é o da entrada (6,00), sem média: %s' % emb(pg, 1))
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        escolher(pg, '#entradaEmb', 2); preencher_entrada(pg, '5', '5,00')
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        ok(emb(pg, 2)['saldo'] == 5 and perto(emb(pg, 2)['custo'], 5.00), 'com saldo zero o custo também é o da entrada (5,00), não a média com 4,70')
        pg.context.close()

        # ---- 13c. ?entrada=<id>
        pg = nova()
        ir_cad(pg, '?entrada=13')
        ok(pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')") and pg.inner_text('#entradaEmb .dropdown-select-label') == 'Fita adesiva' and pg.get_attribute('#entradaEmb', 'data-value') == '13'
           and not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), '?entrada=13 abre o painel de entrada com a Fita adesiva já escolhida (e não o painel de edição)')
        pg.fill('#entradaQtd', '1'); pg.fill('#entradaCusto', '16,00'); pg.wait_for_timeout(150)
        ok(pg.inner_text('#entradaPrevia').startswith('Saldo 8 → 9 · custo R$ 15,00 → R$ 15,11'), 'e a prévia já parte do saldo dela: %s' % pg.inner_text('#entradaPrevia'))
        pg.press('body', 'Escape'); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')"), 'o Esc fecha o painel de entrada')
        for q in ('?entrada=10', '?entrada=999', '?entrada=abc'):
            ir_cad(pg, q)
            ok(pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')") == (q != '?entrada=abc') and pg.inner_text('#entradaEmb .dropdown-select-label') == 'Escolha a embalagem',
               '%s: embalagem inativa ou que não existe não vem escolhida (o painel abre para escolher); texto que não é número nem abre' % q)
        pg.context.close()

        # ---- 13d. Painel de edicao: Estoque, Rende, dica do custo, acerto de saldo
        pg = nova()
        ir_cad(pg)
        pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"13\"]').click()"); pg.wait_for_timeout(350)
        vis = lambda i: pg.evaluate("(i) => document.getElementById(i).getClientRects().length > 0", i)
        ok(pg.input_value('#inputMinimo') == '4' and pg.inner_text('#saldoAtual') == '8' and pg.input_value('#inputRende') == '50' and pg.inner_text('#dicaRende') == 'R$ 0,30 por pedido' and vis('campoRende') and vis('linkAcertarSaldo'),
           'a fita abre com mínimo 4, saldo 8 (só leitura), rende 50 e a dica "R$ 0,30 por pedido"')
        ok('Atualizado sozinho a cada entrada (custo médio).' in pg.inner_text('#campoCusto'), 'o campo Custo diz que é atualizado sozinho a cada entrada')
        ok(not pg.evaluate("document.getElementById('saldoAtual').matches('input, textarea')") and not vis('blocoAcerto'), 'o saldo atual é só leitura e o acerto começa fechado')
        pg.fill('#inputRende', '25'); pg.wait_for_timeout(120)
        ok(pg.inner_text('#dicaRende') == 'R$ 0,60 por pedido', 'a dica do rende acompanha o campo ao vivo: 15,00 ÷ 25 = %s' % pg.inner_text('#dicaRende'))
        pg.fill('#inputCusto', '30,00'); pg.wait_for_timeout(120)
        ok(pg.inner_text('#dicaRende') == 'R$ 1,20 por pedido', 'e o custo (30,00 ÷ 25 = 1,20)')
        for ruim in ('0', 'abc', '2,5', '-1'):
            pg.fill('#inputRende', ruim); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(120)
            ok(mostra(pg, '#erroRende') and ls(pg, 'deskEmbalagens') is None and pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'rende "%s" avisa e não salva (inteiro de 1 em diante)' % ruim)
        pg.fill('#inputRende', '25'); pg.fill('#inputCusto', '15,00'); pg.fill('#inputMinimo', 'x'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(120)
        ok(mostra(pg, '#erroMinimo') and ls(pg, 'deskEmbalagens') is None, 'mínimo que não é número avisa e não salva')
        pg.fill('#inputMinimo', '6'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        f = emb(pg, 13)
        ok(f['minimo'] == 6 and f['saldo'] == 8 and f['rende'] == 25 and perto(f['custo'], 15) and f['auto'] == 'todas', 'o Salvar normal grava o mínimo e o rende, e NÃO mexe no saldo (8): %s' % f)
        # acerto de saldo
        pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"13\"]').click()"); pg.wait_for_timeout(350)
        pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        ok(vis('blocoAcerto') and vis('inputNovoSaldo') and vis('inputMotivoAcerto') and vis('btnAplicarAcerto') and 'Aplicar acerto' in pg.inner_text('#btnAplicarAcerto'), 'o link "Acertar saldo" abre ali mesmo "Novo saldo", "Motivo" e o botão "Aplicar acerto"')
        n_log = len(log_edita(pg))
        pg.fill('#inputNovoSaldo', '5'); pg.fill('#inputMotivoAcerto', ''); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroMotivoAcerto') and emb(pg, 13)['saldo'] == 8 and len(log_edita(pg)) == n_log, 'sem motivo o acerto não vale: o saldo segue 8 e nada vai para o registro')
        pg.fill('#inputNovoSaldo', 'abc'); pg.fill('#inputMotivoAcerto', 'contagem do galpão'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroNovoSaldo') and emb(pg, 13)['saldo'] == 8, 'saldo que não é número também não vale')
        pg.fill('#inputNovoSaldo', '5'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        lg = log_edita(pg)
        ok(emb(pg, 13)['saldo'] == 5 and len(lg) == n_log + 1 and lg[0]['detalhe'] == 'Saldo de Fita adesiva acertado de 8 para 5. Motivo: contagem do galpão' and lg[0]['acao'] == 'Editar · Embalagens',
           'o acerto grava o saldo (5) e vai para o deskLog: "%s"' % (lg and lg[0]['detalhe']))
        ok(pg.inner_text('#saldoAtual') == '5' and not vis('blocoAcerto') and pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')") and 'Saldo 5 · mín. 6' in meta(pg, 13) and 'Abaixo do mínimo' in pg.text_content('#listaEmbalagens .embalagens-card[data-id="13"]'),
           'o painel mostra o saldo novo, o acerto fecha, e a lista já avisa "Abaixo do mínimo" (5 < 6)')
        # saldo negativo e fracionario no acerto
        pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        pg.fill('#inputNovoSaldo', '-1,5'); pg.fill('#inputMotivoAcerto', 'perda'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        ok(emb(pg, 13)['saldo'] == -1.5 and log_edita(pg)[0]['detalhe'] == 'Saldo de Fita adesiva acertado de 5 para −1,5. Motivo: perda' and 'Saldo negativo' in pg.text_content('#listaEmbalagens .embalagens-card[data-id="13"]'), 'o acerto aceita negativo e fração: −1,5 e o selo vira "Saldo negativo"')
        # embalagem nova: saldo 0, minimo 0, rende 1; sem acerto
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(not vis('linkAcertarSaldo') and pg.inner_text('#saldoAtual') == '0' and pg.input_value('#inputMinimo') == '' and not vis('campoRende'), 'embalagem nova: saldo 0, sem "Acertar saldo", o rende só aparece no insumo')
        escolher(pg, '#inputTipoEmbalagem', 'insumo')
        ok(vis('campoRende') and pg.input_value('#inputRende') == '' and pg.inner_text('#dicaRende') == 'R$ 0,00 por pedido', 'no insumo novo o rende aparece, em branco (vale 1)')
        pg.fill('#inputNomeEmbalagem', 'Etiqueta nova'); pg.fill('#inputCusto', '0,20'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        n = next(e for e in ls(pg, 'deskEmbalagens') if e['nome'] == 'Etiqueta nova')
        ok(n['saldo'] == 0 and n['minimo'] == 0 and n['rende'] == 1, 'a nova nasce com saldo 0, mínimo 0 e rende 1: %s' % n)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        pg.fill('#inputNomeEmbalagem', 'Caixa nova'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        n = next(e for e in ls(pg, 'deskEmbalagens') if e['nome'] == 'Caixa nova')
        ok(n['saldo'] == 0 and n['minimo'] == 0 and 'rende' not in n, 'a caixa nova não guarda rende: %s' % n)
        # trocar o tipo de insumo para caixa tira o rende; editar nao mexe no saldo
        pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"13\"]').click()"); pg.wait_for_timeout(350)
        escolher(pg, '#inputTipoEmbalagem', 'pacote'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok('rende' not in emb(pg, 13) and emb(pg, 13)['saldo'] == -1.5, 'mudar o tipo para caixa tira o rende e mantém o saldo')
        pg.context.close()

        # ---- 13e. A lista: selos e as linhas de baixo
        pg = nova()
        ir_cad(pg)
        selos = pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-card')).filter(c => c.querySelector('.selo-estoque')).map(c => [c.querySelector('.embalagens-nome').textContent, c.querySelector('.selo-estoque').textContent])")
        ok(selos == [['Caixa de Encomenda Flex G', 'Abaixo do mínimo'], ['Caixa de Encomenda CE-02', 'Abaixo do mínimo'], ['Tag Desk Brands', 'Abaixo do mínimo']], 'o exemplo tem três abaixo do mínimo, com o selo: %s' % selos)
        ok('Saldo 32 · mín. 40' in meta(pg, 3) and 'Saldo 150 · mín. 200' in meta(pg, 12) and pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"10\"] .selo-estoque')") is None, 'cada cartão mostra "Saldo X · mín. Y"; zero com mínimo zero não avisa (o rolo de tecido)')
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 1)[0].saldo = -2.5; embalagensGravar(L); }")
        ir_cad(pg)
        ok('Saldo −2,5 · mín. 50' in meta(pg, 1) and pg.text_content('#listaEmbalagens .embalagens-card[data-id="1"] .selo-estoque') == 'Saldo negativo' and 'var(--danger-solid)' in pg.get_attribute('#listaEmbalagens .embalagens-card[data-id="1"] .selo-estoque', 'style')
           and 'var(--warning)' in pg.get_attribute('#listaEmbalagens .embalagens-card[data-id="3"] .selo-estoque', 'style'), 'saldo negativo: selo "Saldo negativo" na cor de perigo (o aviso usa a cor de aviso), fração com vírgula')
        CONTRASTE = """() => { const lum = (c) => { const v = c.match(/[\\d.]+/g).slice(0, 3).map(Number).map(x => { x /= 255; return x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4); }); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
            return Array.from(document.querySelectorAll('.selo-estoque')).map(el => { const cs = getComputedStyle(el), a = lum(cs.color), b = lum(cs.backgroundColor); return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); }); }"""
        for tema in ('light', 'dark'):
            pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", tema); pg.wait_for_timeout(300)
            cs = pg.evaluate(CONTRASTE)
            ok(len(cs) == 4 and min(cs) >= 4.5, 'tema %s: o texto dos selos tem contraste de 4,5 ou mais (menor: %.2f)' % (tema, min(cs)))
        pg.context.close()

        # ---- 13f. Separacao nao baixa; a Conferencia baixa na hora de fechar, com o custo por uso
        pg = nova()
        separar4(pg)
        ok(ls(pg, 'deskEmbalagens') is None, 'a Separação concluir o pedido 4 não baixa nada (o cadastro nem foi gravado)')
        t = conferir4(pg)
        ok('A embalagem sai do estoque agora.' in t and t.index('Embalagem confirmada:') < t.index('A embalagem sai do estoque agora.'), 'o texto de confirmação avisa "A embalagem sai do estoque agora.": %s' % t[-120:])
        ce, tg, fi = emb(pg, 5), emb(pg, 12), emb(pg, 13)
        ok(ce['saldo'] == 17 and tg['saldo'] == 149 and fi['saldo'] == 7.98 and emb(pg, 6)['saldo'] == 6 and emb(pg, 3)['saldo'] == 32,
           'fechar baixa a caixa (18 → 17), a tag (150 → 149) e a fita em 1/50 (8 → 7,98); o resto não mexe: %s' % [ce['saldo'], tg['saldo'], fi['saldo']])
        r = reg(pg)
        ok([(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(5, 1, 6.3), (12, 1, 0.6), (13, 1, 0.3)] and fi['custo'] == 15 and fi['rende'] == 50, 'o pedido grava o custo POR USO (a fita 0,30) e o cadastro segue com R$ 15,00 o rolo: %s' % r['itens'])
        a = AVISO[0]
        ok('A embalagem saiu do estoque.' in a and 'Ficou abaixo do mínimo: Caixa de Encomenda CE-02 (17, mínimo 20); Tag Desk Brands (149, mínimo 200).' in a and 'Saldo negativo' not in a and 'Veja em Estoque → Necessidades de Compra.' in a and 'Fita' not in a[a.index('Ficou'):],
           'o aviso final diz o que ficou abaixo do mínimo (CE-02 e a tag; a fita, não) e aponta para Necessidades de Compra: %s' % a[-230:])
        # ficha reaberta que ja estava confirmada: fechar de novo NAO baixa de novo
        ir(pg, CONF_F, '?id=4')
        pg.evaluate("fechada = false"); pg.evaluate("fechar()"); pg.wait_for_timeout(320)
        t2 = modal(pg)
        confirmar(pg); a2 = modal(pg); confirmar(pg)
        ok(t2.startswith('Fechar a conferência do pedido #') and 'Conferência fechada' in a2, 'a ficha reaberta chegou ao fechamento de verdade: %s' % t2[:50])
        ok(emb(pg, 5)['saldo'] == 17 and emb(pg, 12)['saldo'] == 149 and emb(pg, 13)['saldo'] == 7.98 and 'abaixo do mínimo' not in a2 and 'saiu do estoque' not in a2, 'baixa dupla não acontece: o saldo segue 17, 149 e 7,98, e o aviso não repete a baixa: %s' % a2[-120:])
        pg.context.close()

        # ---- 13g. Saldo negativo avisa e nao trava; fita com rende 100
        pg = nova()
        ir_cad(pg)
        grava_cadastro(pg, "por(5).saldo = 0.5; por(13).custo = 15; por(13).rende = 100;")
        separar4(pg)
        t = conferir4(pg)
        r = reg(pg)
        ok(r and r['situacao'] == 'confirmada' and [(i['id'], i['qtd'], i['custo']) for i in r['itens']] == [(5, 1, 6.3), (12, 1, 0.6), (13, 1, 0.15)], 'falta de saldo não trava a expedição: o pedido fecha e grava; a fita com rende 100 grava 0,15: %s' % (r and r['itens']))
        ok(emb(pg, 5)['saldo'] == -0.5 and emb(pg, 13)['saldo'] == 7.99, 'a caixa com 0,5 fica em −0,5 e a fita em 1/100 (7,99)')
        a = AVISO[0]
        ok('Ficou abaixo do mínimo: Tag Desk Brands (149, mínimo 200).' in a and 'Saldo negativo: Caixa de Encomenda CE-02 (−0,5).' in a and 'Veja em Estoque → Necessidades de Compra.' in a, 'o aviso separa "abaixo do mínimo" de "saldo negativo": %s' % a[-210:])
        ir(pg, CONF_F, '?id=4')
        ok(pg.inner_text('#badgeSituacao').strip().upper() == 'CONFERIDO', 'e o pedido fica conferido')
        pg.context.close()

        # ---- 13h. Necessidades de Compra
        pg = nova()
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaEmbalagens thead th')).map(th => th.textContent.trim())")
        ok(cab == ['Embalagem', 'Tipo', 'Saldo', 'Mínimo', 'Comprar', 'Custo da unidade', 'Total', ''] and pg.inner_text('#painelEmbalagens .card-title') == 'Embalagens abaixo do mínimo', 'o card "Embalagens abaixo do mínimo" tem as colunas Embalagem, Tipo, Saldo, Mínimo, Comprar, Custo da unidade e Total: %s' % cab)
        ok(linhas == [['Caixa de Encomenda Flex G', 'Pacote / Caixa', '32', '40', '8', 'R$ 5,90', 'R$ 47,20', 'Dar entrada'],
                      ['Caixa de Encomenda CE-02', 'Pacote / Caixa', '18', '20', '2', 'R$ 6,30', 'R$ 12,60', 'Dar entrada'],
                      ['Tag Desk Brands', 'Insumo', '150', '200', '50', 'R$ 0,60', 'R$ 30,00', 'Dar entrada']], 'lista as três de exemplo, com o que comprar (mínimo − saldo) e o total: %s' % linhas)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens a')).map(a => a.getAttribute('href'))") == ['../cadastros/pagina-cadastros-embalagens.html?entrada=%d' % i for i in (3, 5, 12)], 'cada linha tem o link "Dar entrada" para ../cadastros/pagina-cadastros-embalagens.html?entrada=<id>')
        ok(pg.evaluate("document.getElementById('painelCompra').compareDocumentPosition(document.getElementById('painelEmbalagens')) & 4") == 4, 'o card fica abaixo do painel da compra')
        pg.click('#corpoEmbalagens tr[data-id="12"] a'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok('pagina-cadastros-embalagens.html' in pg.url and pg.inner_text('#entradaEmb .dropdown-select-label') == 'Tag Desk Brands' and pg.evaluate("document.getElementById('entradaDrawer').classList.contains('open')"), 'o link leva à tela de Embalagens com o painel de entrada aberto na Tag Desk Brands')
        pg.context.close()
        pg = nova()
        ir_cad(pg)
        grava_cadastro(pg, "por(13).saldo = 3.98; por(10).saldo = -5; por(10).minimo = 5; por(3).saldo = 40; por(5).saldo = 20; por(12).saldo = 200;")
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(0, 7).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        ok(linhas == [['Fita adesiva', 'Insumo', '3,98', '4', '1', 'R$ 15,00', 'R$ 15,00']], 'saldo fracionário abaixo do mínimo entra (3,98 de 4: comprar 1, arredondado para cima); inativa abaixo do mínimo fica de fora; saldo igual ao mínimo não entra: %s' % linhas)
        grava_cadastro(pg, "por(13).saldo = 4;")
        ir(pg, NC)
        ok(pg.inner_text('#embVazio') == 'Nenhuma embalagem abaixo do mínimo.' and pg.locator('#embVazio').is_visible() and not pg.locator('#tabelaEmbalagens').is_visible(), 'sem nenhuma abaixo: "Nenhuma embalagem abaixo do mínimo."')
        pg.context.close()
        for w in (1280, 1440):
            pg = nova(w, 900, fixo=False)
            ir(pg, NC)
            m = pg.evaluate("(() => { const w = document.getElementById('tabelaEmbalagensWrap'); return [w.scrollWidth - w.clientWidth, document.documentElement.scrollWidth - document.documentElement.clientWidth]; })()")
            ok(m[0] <= 0 and m[1] <= 0, 'a %d px a tabela das embalagens não tem barra horizontal: %s' % (w, m))
            pg.context.close()

        # ---- 13i. Migracao: cadastro gravado antes do estoque
        pg = nova()
        ir_cad(pg)
        pg.evaluate("""() => localStorage.setItem('deskEmbalagens', JSON.stringify([
            { id: 5, nome: 'Caixa de Encomenda CE-02', tipo: 'pacote', largura: 27, altura: 18, comprimento: 9, peso: 0.73, cap: 12, custo: 6.3, status: 'ativo' },
            { id: 13, nome: 'Fita adesiva', tipo: 'insumo', peso: 0, custo: 0.3, auto: 'todas', status: 'ativo' },
            { id: 99, nome: 'Caixa do Fornecedor', tipo: 'pacote', cap: 3, custo: 2, status: 'ativo' },
            { id: 6, nome: 'Caixa para Eletrônicos', tipo: 'pacote', cap: 25, custo: 12.5, saldo: 2, minimo: 1, status: 'ativo' }]))""")
        ir_cad(pg)
        ler = pg.evaluate("embalagensLer().map(e => [e.id, e.saldo, e.minimo, e.custo, e.rende === undefined ? null : e.rende, embCustoUso(e)])")
        ok(ler == [[5, 18, 20, 6.3, None, 6.3], [13, 8, 4, 0.3, None, 0.3], [99, 0, 0, 2, None, 2], [6, 2, 1, 12.5, None, 12.5]],
           'o cadastro antigo ganha saldo e mínimo do padrão de mesmo id (ou 0); a fita gravada a 0,30 NÃO ganha rende nem custo do padrão (segue 0,30 por pedido); quem já tem saldo fica como está: %s' % ler)
        ir_cad(pg)
        ok('Saldo 8 · mín. 4' in meta(pg, 13) and 'R$ 0,30' in meta(pg, 13) and 'rende' not in meta(pg, 13) and 'Abaixo do mínimo' in pg.text_content('#listaEmbalagens .embalagens-card[data-id="5"]'), 'a lista mostra o que migrou: a fita sem "rende" e a CE-02 abaixo do mínimo')
        pg.context.close()

        # ---- 13j. O custo de cada pedido de exemplo nao mudou; os leitores usam o custo por uso
        ANTIGO = {1: 3.5, 2: 4.7, 3: 5.9, 4: 4.2, 5: 6.3, 6: 12.5, 7: 1.1, 8: 1.8, 9: 4.5, 10: 7, 11: 0.4, 12: 0.6, 13: 0.3, 14: 0.25}
        pg = nova()
        ir(pg, PROD_D)
        uso = {i: c for i, c in pg.evaluate("embalagensLer().map(e => [e.id, embCustoUso(e)])")}
        ok(all(perto(uso[i], c) for i, c in ANTIGO.items()), 'o custo por uso de cada embalagem do exemplo é o de antes (a fita sai 0,30): %s' % uso)
        for tela in ('pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html'):
            ir(pg, tela, '?id=v1' if 'detalhe.html' in tela and 'comissoes' in tela else '')
            ok(pg.evaluate("resultadoDoPedido(PEDIDOS.filter(p => p.id === 4)[0]).embalagem") == 7.2, '%s: a embalagem estimada do 4 segue 7,20 (6,30 + 0,60 + 0,30)' % tela.replace('pagina-', ''))
        abrir_custos(pg)
        ok(linha_pedido(pg, 4)['Embalagem'] == 'R$ 7,20 estimada' and linha_pedido(pg, 1)['Embalagem'] == 'R$ 6,60 estimada' and linha_pedido(pg, 3)['Embalagem'] == 'R$ 1,80 estimada', 'Custos do E-commerce: o 4 (7,20), o 1 (6,60) e o 3 (1,80) seguem como antes')
        pg.context.close()
        # com o rende da fita em 100, os cinco leitores e a calculadora usam 0,15 por pedido
        pg = nova()
        ir_cad(pg)
        grava_cadastro(pg, "por(13).custo = 15; por(13).rende = 100;")
        for tela in ('pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html', 'pagina-cadastros-clientes-detalhe.html'):
            ir(pg, tela, '?id=v1' if 'detalhe.html' in tela and 'comissoes' in tela else '')
            ok(perto(pg.evaluate("resultadoDoPedido(PEDIDOS.filter(p => p.id === 4)[0]).embalagem"), 7.05), '%s: com a fita rendendo 100, o 4 estimado vai a 7,05 (a conta lê o custo por uso)' % tela.replace('pagina-', ''))
        abrir_custos(pg)
        ok(linha_pedido(pg, 4)['Embalagem'] == 'R$ 7,05 estimada', 'Custos do E-commerce: 7,05 com o rende da fita em 100')
        ir(pg, PV_D, '?id=4')
        ok('R$ 7,05' in pg.inner_text('#caixaResultado'), 'a página do pedido: 7,05 com o rende da fita em 100')
        ir(pg, PROD_D, '?editar=1')
        ok(pg.evaluate("insumosAutomaticos(embalagensLer(), 1).map(i => i.nome)") == ['Tag Desk Shope', 'Fita adesiva'], 'a ficha do produto lê o cadastro com o rende')
        pg.click('.tab-item[data-tab="complementares"]'); escolher(pg, '#inputLojaDesk', 'Desk Shope'); pg.click('.tab-item[data-tab="precos"]')
        pg.click('#btnCalcularPreco'); pg.wait_for_timeout(500)
        ok(pg.inner_text('#calcEmbOrigem') == 'Caixa R$ 4,70 + Tag Desk Shope R$ 0,40 + Fita adesiva R$ 0,15' and pg.input_value('#calcEmbalagem') == '5,25', 'a calculadora usa o custo por uso: Flex M 4,70 + tag 0,40 + fita 0,15 = 5,25: %s' % pg.inner_text('#calcEmbOrigem'))
        pg.context.close()

        # ---- 13k. O layout dos campos novos: nenhum quebra linha a 1280 e 1440 (e a 1024, a janela de quem usa zoom), nos dois temas
        for w in (1024, 1280, 1440):
            for tema in ('light', 'dark'):
                pg = nova(w, 900, fixo=False)
                ir_cad(pg)
                pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", tema)
                pg.click('#btnDarEntrada'); pg.wait_for_timeout(400)
                MEDE = """(raiz) => { const d = document.getElementById(raiz).getBoundingClientRect(), r = document.getElementById(raiz);
                  const rot = Array.from(r.querySelectorAll('label')).filter(l => l.getBoundingClientRect().width > 0).map(l => Math.round(l.getBoundingClientRect().height));
                  const fora = Array.from(r.querySelectorAll('input, .dropdown-select-btn, .saldo-leitura, button')).filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > d.right - 20).length;
                  return { rotulos: rot, fora: fora, lateral: r.scrollWidth - r.clientWidth, pagina: document.documentElement.scrollWidth - document.documentElement.clientWidth }; }"""
                m = pg.evaluate(MEDE, 'entradaDrawer')
                ok(max(m['rotulos']) < 20 and m['fora'] == 0 and m['lateral'] <= 0 and m['pagina'] <= 0, 'a %d px, tema %s, entrada: rótulos numa linha só e nada passa da borda: %s' % (w, tema, m))
                pg.click('#entradaClose'); pg.wait_for_timeout(300)
                pg.evaluate("document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"13\"]').click()"); pg.wait_for_timeout(450)
                pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(200)
                m = pg.evaluate(MEDE, 'eventDrawer')
                topos = pg.evaluate("['inputMinimo', 'saldoAtual'].map(i => Math.round(document.getElementById(i).getBoundingClientRect().top)).concat(['inputNovoSaldo', 'inputMotivoAcerto'].map(i => Math.round(document.getElementById(i).getBoundingClientRect().top)))")
                ok(max(m['rotulos']) < 20 and m['fora'] == 0 and m['lateral'] <= 0 and m['pagina'] <= 0 and topos[0] == topos[1] and topos[2] == topos[3], 'a %d px, tema %s, edição do insumo (Rende, Estoque, acerto): rótulos numa linha, pares no mesmo topo, nada passa da borda: %s %s' % (w, tema, m, topos))
                pg.context.close()

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print((' - ' + f).encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8'))
raise SystemExit(1 if falhas else 0)
