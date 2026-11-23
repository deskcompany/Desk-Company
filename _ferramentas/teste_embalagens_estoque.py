# -*- coding: utf-8 -*-
# O estoque das embalagens, pacote 1 (decidido em 20/nov/2026): codigo EMB, movimento, motivos, acerto, prejuizo e Movimentacao.
#
# O que ele protege sao as decisoes do usuario, as que "simplificar" apaga primeiro:
#   Codigo: a embalagem ganha EMB-001, EMB-002...; as 14 de exemplo vao de EMB-001 a EMB-014; o codigo nasce com a embalagem, fica gravado e NUNCA se reaproveita (excluir a ultima e criar outra nao repete);
#           so leitura no painel ("Gerado pelo sistema."); aparece na lista, no painel e na Movimentacao, e a busca acha por ele
#   Movimento: a chave deskMovEmbalagens (embMovRegistrar / embMovLer, no bloco comum); o saldo de antes e o de depois NAO se gravam: a ficha parte do saldo do cadastro e desfaz os movimentos
#           de tras para a frente, e a primeira linha e o "Saldo de abertura". O exemplo de fabrica (60 dias) nunca deixa saldo de abertura negativo e nunca nasce no futuro
#   Motivos de Perda: o campo `embalagem` ("Vale para embalagens"), de fabrica nos ids 1, 2, 3, 4, 5, 7, 8 e 10; o guardado sem o campo usa o de fabrica; o motivo novo nasce desmarcado
#   Acerto: o motivo e uma lista (so os ativos que valem para embalagens), a dica aparece embaixo, `exigeObs` pede a observacao; o grupo do motivo manda na direcao (saida = menos,
#           entrada = mais, balanco = os dois); a falta com motivo de saida ou de balanco e PREJUIZO = quantidade x custo, que vai na confirmacao, no Registro de atividades e no movimento
#   Cards no topo: Prejuizo com embalagens no mes (leva a Movimentacao ja em Embalagens), Abaixo do minimo, Valor em estoque; sem prejuizo, "R$ 0,00" e "nenhum acerto no mes"
#   Movimentacao: "Produtos / Embalagens"; a ficha das embalagens usa as mesmas colunas, sem deposito; o prejuizo vai em vermelho no Movimento; so consulta
#   Entrada sem nota (o "Dar entrada" de antes): "Comprovante (opcional)" no lugar de "Nota"; soma o saldo, recalcula o custo medio e grava o movimento 'entrada_sem_nota'
#   Conferencia de Saida: embBaixar(itens, ref) grava um 'baixa_pedido' por embalagem, com o numero do pedido, e so uma vez (ficha reaberta nao baixa de novo)
#
#   [1]  O codigo: sequencia, lista, painel, busca, nunca repete, o guardado sem codigo;
#   [2]  Motivos de Perda: o campo de fabrica, o guardado sem o campo, o motivo novo, a marca na lista, o formulario;
#   [3]  A lista de motivos do acerto: so os ativos que valem para embalagens, o espelho de fabrica, a dica;
#   [4]  O acerto: direcao, observacao obrigatoria, prejuizo, o movimento gravado, o Registro de atividades;
#   [5]  O movimento: os campos, o exemplo de fabrica (abertura nunca negativa, nunca no futuro, 09:15 ou 00:01) e o guardado estragado;
#   [6]  Os cards do topo;
#   [7]  A Movimentacao em Embalagens: a ficha fecha no cadastro, o saldo de abertura, os textos, o prejuizo em vermelho, os filtros, a planilha, o endereco;
#   [8]  A entrada sem nota;
#   [9]  A Conferencia de Saida grava a baixa com o pedido, uma vez so;
#   [10] Os blocos comuns: as copias idênticas;
#   [11] Fotos nos dois temas a 1280 e 1440, sem barra de rolagem para o lado.
# PACOTE 2 (20/nov/2026): compra, nota e Inventario.
#   Necessidades de Compra: o bloco das embalagens tem Codigo, "Chegando" (ordens em aberto e em andamento, pedido - recebido) e a caixa de marcar; comprar = max(0, teto(minimo - saldo - chegando));
#           "Gerar ordem de compra" usa o painel das ordens de produto (fornecedor obrigatorio, previsto, quantidade editavel) e a ordem nasce em deskOrdensGeradas so com embalagens (sku = codigo, embId)
#   Ordens de Compra: a ordem gerada le o `recebido` e a `situacao` gravados; "Gerar nota de entrada" leva ?oc=<numero>
#   Entrada de Notas: a ordem gerada preenche fornecedor e itens pendentes; item EMB-xxx e embalagem (nome do cadastro); salvar soma ao saldo com a MESMA conta do "Dar entrada sem nota" (embEntradaConta,
#           no bloco comum), grava 'entrada_nota' e soma ao recebido da ordem; a nota nao entra duas vezes (chave = CNPJ so com digitos | serie | numero, sem espacos nem zeros a esquerda, em deskNotasLancadas)
#   Inventario: "Produtos / Embalagens" ao gerar; sem deposito e sem trava; a diferenca e contra o saldo da ABERTURA e se aplica ao saldo de agora; falta vira prejuizo; planilha e coletor recusam codigo EMB
#   [12] Necessidades de Compra; [13] Ordens de Compra; [14] a nota que soma o saldo; [15] a nota que nao entra duas vezes; [16] o Inventario de embalagens; [17] fotos do pacote 2
# PACOTE 3 (23/nov/2026): os ajustes que o usuario pediu depois de testar os pacotes 1 e 2. (O item da impressao da Movimentacao esta em teste_impressao.py, secao 7.)
#   Entrada de Notas: embalagem com preco unitario >= 10 vezes o custo atual (custo > 0) ganha uma linha em vermelho no modal e o botao "Salvar mesmo assim"; produto e custo 0 nao avisam
#   Necessidades de Compra: a embalagem que ja tem ordem aberta ou em andamento cobrindo o minimo SAI da tabela e vira o bloco "N embalagens ja pedidas" acima dela (com o link da ordem); atendida, volta
#   Fornecedor padrao: campo da embalagem (dropdown com os 7 fornecedores), as 14 de fabrica no Vale; o painel da ordem so oferece os fornecedores dos itens marcados; a busca avancada da Ordem de Compra
#           e a sugestao ao digitar o item (Ordem de Compra e Entrada de Notas) so mostram o que e do fornecedor da ordem/nota
#   Inventario: Enter no campo vai ao proximo; vazio avisa em vermelho e nao pula. Botao "Gerar" o codigo: Embalagens, Produtos (SKU), Clientes e Fornecedores
#   [18] aviso de preco; [19] fornecedor padrao; [20] painel da ordem; [21] busca avancada; [22] sugestao; [23] Enter no Inventario; [24] botao Gerar; [25] fotos do pacote 3. A secao 12 ganhou o bloco das ja pedidas.
# Aceita o numero da secao como argumento. As fotos vao para a pasta de DESK_FOTOS.
from playwright.sync_api import sync_playwright
import datetime, os as _os, glob as _g, re, sys, tempfile
import localiza

PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
FOTOS = _os.environ.get('DESK_FOTOS') or _os.path.join(tempfile.gettempdir(), 'desk_fotos_embalagens')
_os.makedirs(FOTOS, exist_ok=True)

CAD = 'pagina-cadastros-embalagens.html'
MOTIVOS = 'pagina-configuracoes-motivos-perda.html'
MOV = 'pagina-estoque-movimentacao.html'
NC = 'pagina-estoque-necessidades-compra.html'
OCL = 'pagina-estoque-ordens-compra.html'
OCD = 'pagina-estoque-ordens-compra-detalhe.html'
NOTA = 'pagina-estoque-entrada-notas-detalhe.html'
INVT = 'pagina-estoque-inventario.html'
SEP_F = 'pagina-logistica-separacao-detalhe.html'
CONF_F = 'pagina-logistica-conferencia-saida-detalhe.html'
FIXO = datetime.datetime(2026, 10, 30, 10, 0, 0)    # sexta, 10h: o mes e o "hoje, as 09:15" do exemplo nao dependem do dia em que a suite roda
CEDO = datetime.datetime(2026, 10, 30, 8, 0, 0)     # antes das 09:15: o acerto de hoje cai as 00:01
PRIMEIRO = datetime.datetime(2026, 11, 1, 10, 0, 0)  # dia 1: so o acerto de hoje conta no mes

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


erros = []


def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e


def fonte(n):
    return open(localiza.onde(n), encoding='utf-8').read()


def brl(v):
    return 'R$ ' + '{:,.2f}'.format(abs(float(v))).replace(',', 'X').replace('.', ',').replace('X', '.')


perto = lambda a, b: abs(float(a) - float(b)) < 0.0051

# O cadastro de fabrica (saldo, custo, minimo, ativo): o oraculo dos cards, escrito aqui e nao lido da tela.
FAB = {1: (140, 3.5, 50, 1), 2: (85, 4.7, 50, 1), 3: (32, 5.9, 40, 1), 4: (60, 4.2, 30, 1), 5: (18, 6.3, 20, 1), 6: (6, 12.5, 5, 1), 7: (300, 1.1, 100, 1), 8: (120, 1.8, 50, 1),
       9: (12, 4.5, 5, 1), 10: (0, 7, 0, 0), 11: (800, 0.4, 300, 1), 12: (150, 0.6, 200, 1), 13: (8, 15, 4, 1), 14: (400, 0.25, 100, 1)}
VALOR_ESTOQUE = sum(s * c for s, c, m, a in FAB.values() if s > 0)
ABAIXO = sum(1 for s, c, m, a in FAB.values() if a and s < m)
NOMES = {1: 'Caixa de Encomenda Flex P', 2: 'Caixa de Encomenda Flex M', 3: 'Caixa de Encomenda Flex G', 5: 'Caixa de Encomenda CE-02', 12: 'Tag Desk Brands', 13: 'Fita adesiva', 14: 'Saco plástico'}
MOTIVOS_FAB = ['Quebra ou avaria', 'Perda', 'Furto ou roubo', 'Extravio', 'Consumo próprio', 'Sobra de contagem', 'Correção de lançamento', 'Contagem física']

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)

    def nova(w=1440, h=950, relogio=FIXO):
        """Uma aba num contexto novo: localStorage limpo e o relogio parado."""
        ctx = nav.new_context(viewport={'width': w, 'height': h}, accept_downloads=True)
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: erros.append(str(e)[:200]))
        pg.on('console', lambda m: erros.append(m.text[:200]) if m.type == 'error' and not ruido(m.text) else None)
        if relogio:
            pg.clock.set_fixed_time(relogio)
        return pg

    def ir(pg, tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def ir_cad(pg, q=''):
        ir(pg, CAD, q); pg.evaluate("itensPorPaginaAtual = 25; renderEmbalagens();"); pg.wait_for_timeout(120)

    def ls(pg, chave):
        return pg.evaluate("(k) => JSON.parse(localStorage.getItem(k) || 'null')", chave)

    def poe(pg, chave, valor):
        if pg.url == 'about:blank':
            pg.goto(localiza.uri(CAD))   # o armazenamento so existe numa pagina de verdade (file:// compartilha entre as telas)
        pg.evaluate("([k, v]) => localStorage.setItem(k, JSON.stringify(v))", [chave, valor])

    def emb(pg, i):
        return next((e for e in (ls(pg, 'deskEmbalagens') or []) if e['id'] == i), None)

    def sd(pg, i):
        return pg.evaluate("(i) => embalagensLer().filter(e => e.id === i)[0].saldo", i)

    def movs(pg):
        return ls(pg, 'deskMovEmbalagens') or []

    def escolher(pg, raiz, valor):
        pg.evaluate("([r, v]) => document.querySelector(r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)])
        pg.wait_for_timeout(200)

    def mostra(pg, sel):
        return pg.evaluate("(s) => document.querySelector(s).classList.contains('show')", sel)

    def vis(pg, i):
        return pg.evaluate("(i) => { const e = document.getElementById(i); return !!e && e.getClientRects().length > 0; }", i)

    def tx(pg, sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; }", sel)

    def log_edita(pg):
        return pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(x => x.chave === 'embalagensEditar')")

    def abre_card(pg, i):
        pg.evaluate("(i) => document.querySelector('#listaEmbalagens .embalagens-card[data-id=\"' + i + '\"]').click()", i); pg.wait_for_timeout(350)

    def acerto(pg, i, motivo, novo, obs=''):
        """Abre a embalagem, abre o acerto, escolhe o motivo e aplica; devolve sem fechar nada."""
        abre_card(pg, i)
        pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(120)
        if motivo is not None:
            escolher(pg, '#acertoMotivo', motivo)
        pg.fill('#inputNovoSaldo', novo)
        if obs:
            pg.fill('#inputObsAcerto', obs)
        pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)

    def linhas_mov(pg):
        return pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => Array.from(tr.children).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")

    def num(s):
        limpo = re.sub(r'[^0-9,.\-−]', '', s).replace('−', '-').replace('.', '').replace(',', '.')
        return float(limpo) if limpo not in ('', '-') else None

    def buscar_emb(pg, termo, tipo=None, de='tudo'):
        """Na Movimentacao: escolhe Embalagens, acha pela busca, abre o historico inteiro (ou o mes) e busca."""
        pg.click('#modoMov [data-modo="embalagens"]'); pg.wait_for_timeout(150)
        pg.fill('#buscaProduto', termo); pg.wait_for_timeout(150)
        pg.press('#buscaProduto', 'Enter'); pg.wait_for_timeout(100)
        if tipo:
            escolher(pg, '#filtroTipoMov', tipo)
        if de == 'tudo':
            pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)"))
        pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)

    # ================================================================ 1. codigo
    if secao(1, 'O código EMB: a sequência, a lista, o painel, a busca, nunca repete'):
        pg = nova()
        ir_cad(pg)
        cods = pg.evaluate("embalagensLer().map(e => [e.id, embCodigo(e)])")
        ok(cods == [[i, 'EMB-%03d' % i] for i in range(1, 15)], 'as 14 de exemplo vão do id 1 = EMB-001 ao id 14 = EMB-014: %s' % cods[:3])
        na_lista = pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-card')).map(c => [Number(c.dataset.id), c.querySelector('.embalagens-codigo').textContent])")
        ok(na_lista == [[i, 'EMB-%03d' % i] for i in range(1, 15)], 'a lista mostra o código de cada uma, ao lado do nome')
        ok(pg.evaluate("embCodigo(null) === '' && embCodigo({ id: 7, codigo: 'EMB-099' }) === 'EMB-099' && embCodigo({ id: 1234 }) === 'EMB-1234'"), 'embCodigo: o gravado vale, sem ele vale o do id (com 3 casas ou mais), e sem embalagem não quebra')
        abre_card(pg, 5)
        ok(tx(pg, '#campoCodigoEmbalagem label') == 'Código' and tx(pg, '#codigoEmbalagem') == 'EMB-005' and 'Gerado pelo sistema.' in tx(pg, '#campoCodigoEmbalagem')
           and not pg.evaluate("document.getElementById('codigoEmbalagem').matches('input, textarea, select')"), 'o painel mostra "Código EMB-005", só leitura, com a dica "Gerado pelo sistema."')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(tx(pg, '#codigoEmbalagem') == 'EMB-015', 'embalagem nova: o painel já mostra o próximo código, EMB-015')
        pg.fill('#inputNomeEmbalagem', 'Caixa A'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        a = next(e for e in ls(pg, 'deskEmbalagens') if e['nome'] == 'Caixa A')
        ok(a['id'] == 15 and a['codigo'] == 'EMB-015' and ls(pg, 'deskEmbalagensSeq') == 15, 'a nova nasce com id 15 e o código GRAVADO (EMB-015), e o contador guardado vai a 15: %s' % a)
        ok(tx(pg, '#listaEmbalagens .embalagens-card[data-id="15"] .embalagens-codigo') == 'EMB-015', 'e aparece na lista com o código')
        # excluir a ultima e criar outra: o numero nao volta
        pg.evaluate("() => embalagensGravar(embalagensLer().filter(e => e.id !== 15))")   # o efeito do "Excluir embalagem" no cadastro guardado (a exclusao pede o modal de confirmacao, que nao importa aqui)
        ir_cad(pg)
        ok(emb(pg, 15) is None, 'excluída a EMB-015, ela some do cadastro')
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(tx(pg, '#codigoEmbalagem') == 'EMB-016', 'e o próximo código é EMB-016: o 015 nunca se reaproveita (antes, o id era "o maior + 1" e repetia)')
        pg.fill('#inputNomeEmbalagem', 'Caixa B'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        b = next(e for e in ls(pg, 'deskEmbalagens') if e['nome'] == 'Caixa B')
        ok(b['id'] == 16 and b['codigo'] == 'EMB-016', 'a Caixa B nasce EMB-016: %s' % b)
        # excluir uma de exemplo e a ultima: o contador segue
        pg.evaluate("() => { const L = embalagensLer().filter(e => e.id !== 14 && e.id !== 16); embalagensGravar(L); }")
        ir_cad(pg)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(tx(pg, '#codigoEmbalagem') == 'EMB-017', 'sem a EMB-014 e sem a EMB-016, o próximo é EMB-017 (o maior já usado, não o maior que sobrou)')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        # outro navegador (sem o contador): o maior do exemplo vale, excluir a 14 e criar nao repete o 14
        pg2 = nova()
        ir_cad(pg2)
        pg2.evaluate("() => { const L = embalagensLer().filter(e => e.id !== 14); embalagensGravar(L); }")
        ir_cad(pg2)
        pg2.click('#btnNovaEmbalagem'); pg2.wait_for_timeout(300)
        ok(tx(pg2, '#codigoEmbalagem') == 'EMB-015', 'mesmo sem o contador, excluída a EMB-014 de exemplo, a nova é EMB-015 e não repete o 14')
        pg2.context.close()
        # editar mantem o codigo (gravado ou do id)
        pg = nova()
        ir_cad(pg)
        abre_card(pg, 3); pg.fill('#inputNomeEmbalagem', 'Flex G renomeada'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(pg.evaluate("embCodigo(embalagensLer().filter(e => e.id === 3)[0])") == 'EMB-003' and tx(pg, '#listaEmbalagens .embalagens-card[data-id="3"] .embalagens-codigo') == 'EMB-003', 'editar uma de exemplo não muda o código dela (EMB-003)')
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        pg.fill('#inputNomeEmbalagem', 'Caixa C'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        abre_card(pg, 15); pg.fill('#inputNomeEmbalagem', 'Caixa C renomeada'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(emb(pg, 15)['codigo'] == 'EMB-015' and emb(pg, 15)['nome'] == 'Caixa C renomeada', 'editar uma criada guarda o código gravado: %s' % emb(pg, 15))
        # cadastro antigo, com ids soltos: o proximo passa do maior
        pg.evaluate("""() => localStorage.setItem('deskEmbalagens', JSON.stringify([
            { id: 5, nome: 'Caixa de Encomenda CE-02', tipo: 'pacote', cap: 12, custo: 6.3, status: 'ativo', saldo: 18, minimo: 20 },
            { id: 99, nome: 'Caixa do Fornecedor', tipo: 'pacote', cap: 3, custo: 2, status: 'ativo', saldo: 0, minimo: 0 }]))""")
        ir_cad(pg)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(tx(pg, '#codigoEmbalagem') == 'EMB-100' and tx(pg, '#listaEmbalagens .embalagens-card[data-id="99"] .embalagens-codigo') == 'EMB-099', 'cadastro com id solto (99): a lista mostra EMB-099 e a nova será EMB-100')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        # a busca acha pelo codigo
        pg.evaluate("localStorage.clear()")
        ir_cad(pg)
        def achados(q):
            pg.fill('#campoBusca', q); pg.wait_for_timeout(150)
            return pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-card')).map(c => Number(c.dataset.id))")
        ok(achados('EMB-005') == [5] and achados('emb-012') == [12] and achados('EMB-01') == [10, 11, 12, 13, 14] and achados('fita') == [13] and achados('EMB-999') == [], 'a busca acha pelo código (com ou sem maiúscula, pelo começo) e continua achando pelo nome: %s' % achados('EMB-01'))
        ok(pg.get_attribute('#campoBusca', 'placeholder') == 'Buscar por nome ou código...', 'o campo de busca diz que aceita o código')
        ok(achados('EMB-999') == [] and pg.locator('#emptyState').is_visible() and 'undefined' not in tx(pg, '.main') and 'NaN' not in tx(pg, '.main'), 'busca sem resultado: mostra o estado vazio, sem "undefined" nem "NaN"')
        pg.context.close()

    # ================================================================ 2. motivos de perda
    if secao(2, 'Motivos de Perda: o campo "Vale para embalagens"'):
        pg = nova()
        ir(pg, MOTIVOS)
        marc = pg.evaluate("MOTIVOS.filter(m => m.embalagem).map(m => m.id)")
        ok(marc == [1, 2, 3, 4, 5, 7, 8, 10], 'de fábrica vêm marcados os ids 1, 2, 3, 4, 5, 7, 8 e 10: %s' % marc)
        ok(pg.evaluate("MOTIVOS.every(m => typeof m.embalagem === 'boolean')"), 'e nenhum motivo fica sem o campo (todos true ou false)')
        marcas = pg.evaluate("Array.from(document.querySelectorAll('#listaMotivos .motivo-card')).filter(c => c.querySelector('.marca-embalagem')).map(c => c.querySelector('.motivo-nome').textContent)")
        ok(marcas == ['Quebra ou avaria', 'Perda', 'Furto ou roubo', 'Extravio', 'Consumo próprio', 'Sobra de contagem', 'Correção de lançamento', 'Contagem física'] and tx(pg, '#listaMotivos .motivo-card .marca-embalagem') == 'EMBALAGENS',
           'a lista traz a marca "Embalagens" nos 8 marcados (e só neles): %s' % marcas)
        pg.evaluate("document.querySelector('#listaMotivos .motivo-card').click()"); pg.wait_for_timeout(350)
        ok(pg.is_checked('#inputEmbalagem') and 'Vale para embalagens' in tx(pg, '.main') + tx(pg, '#eventDrawer'), 'o painel do motivo "Quebra ou avaria" abre com "Vale para embalagens" marcado')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('btnNovoMotivo').click()"); pg.wait_for_timeout(350)
        ok(not pg.is_checked('#inputEmbalagem'), 'motivo novo nasce desmarcado')
        pg.fill('#inputNomeMotivo', 'Caixa molhada na chuva'); pg.check('#inputEmbalagem'); pg.click('#btnSalvarMotivo'); pg.wait_for_timeout(400)
        guardado = ls(pg, 'deskMotivosPerda')
        novo = next(m for m in guardado if m['nome'] == 'Caixa molhada na chuva')
        ok(novo['embalagem'] is True and all(isinstance(m['embalagem'], bool) for m in guardado), 'marcar e salvar grava embalagem: true no motivo novo, e o cadastro guardado traz o campo em todos: %s' % novo['embalagem'])
        # desmarcar um de fabrica persiste
        pg.evaluate("document.querySelector('#listaMotivos .motivo-card').click()"); pg.wait_for_timeout(350)
        pg.uncheck('#inputEmbalagem'); pg.click('#btnSalvarMotivo'); pg.wait_for_timeout(400)
        ir(pg, MOTIVOS)
        ok(pg.evaluate("MOTIVOS.filter(m => m.id === 1)[0].embalagem") is False and pg.evaluate("MOTIVOS.filter(m => m.nome === 'Caixa molhada na chuva')[0].embalagem") is True, 'desmarcar "Quebra ou avaria" persiste ao recarregar, e o motivo novo segue marcado')
        pg.context.close()
        # guardado sem o campo: vale o de fabrica pelo id
        pg = nova()
        poe(pg, 'deskMotivosPerda', [
            {'id': 1, 'nome': 'Quebra ou avaria', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': True, 'obs': '', 'status': 'ativo'},
            {'id': 6, 'nome': 'Deterioração ou vencimento', 'grupo': 'saida', 'destino': 'interno', 'exigeObs': True, 'obs': '', 'status': 'ativo'},
            {'id': 1700000000000, 'nome': 'Motivo criado antes do campo', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': False, 'obs': '', 'status': 'ativo'}])
        ir(pg, MOTIVOS)
        ok(pg.evaluate("MOTIVOS.map(m => [m.id, m.embalagem])") == [[1, True], [6, False], [1700000000000, False]], 'guardado sem o campo: o id 1 (de fábrica) fica marcado, o 6 e o criado antes do campo ficam desmarcados')
        pg.context.close()

    # ================================================================ 3. a lista de motivos do acerto
    if secao(3, 'O acerto escolhe o motivo da lista de Motivos de Perda: só os ativos que valem para embalagens'):
        pg = nova()
        ir_cad(pg)
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        nomes = [x.strip() for x in pg.locator('#acertoMotivo .dropdown-select-item').all_inner_texts()]
        ok(nomes == MOTIVOS_FAB, 'sem nada guardado vale o espelho de fábrica: os 8 motivos marcados, na ordem do cadastro: %s' % nomes)
        ok(pg.evaluate("document.querySelectorAll('select').length") == 0 and vis(pg, 'acertoMotivo') and pg.inner_text('#acertoMotivo .dropdown-select-label') == 'Escolha o motivo', 'é o dropdown da casa (nenhum select nativo), começando em "Escolha o motivo"')
        escolher(pg, '#acertoMotivo', 1)
        ok(tx(pg, '#dicaMotivoAcerto') == 'Pedir foto antes do descarte. É a prova de que a mercadoria existia e deixou de existir.' and tx(pg, '#rotuloObsAcerto') == 'Observação (obrigatória)', 'escolher o motivo mostra a dica dele embaixo e a observação vira obrigatória')
        escolher(pg, '#acertoMotivo', 5)
        ok('Mercadoria que saiu do estoque' in tx(pg, '#dicaMotivoAcerto') and tx(pg, '#rotuloObsAcerto') == 'Observação (opcional)', 'trocar de motivo troca a dica e a observação volta a ser opcional')
        pg.context.close()
        # o cadastro guardado manda: ativos que valem para embalagens (e o de outra operacao tambem, se marcado)
        pg = nova()
        poe(pg, 'deskMotivosPerda', [
            {'id': 1, 'nome': 'Quebra ou avaria', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': True, 'obs': 'Foto antes.', 'status': 'ativo', 'embalagem': False},
            {'id': 2, 'nome': 'Perda', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': True, 'obs': '', 'status': 'inativo', 'embalagem': True},
            {'id': 3, 'nome': 'Furto ou roubo', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': True, 'obs': '', 'status': 'ativo'},
            {'id': 6, 'nome': 'Deterioração ou vencimento', 'grupo': 'saida', 'destino': 'interno', 'exigeObs': True, 'obs': '', 'status': 'ativo'},
            {'id': 12, 'nome': 'Perda em trânsito', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': True, 'operacao': 'transferencia', 'obs': '', 'status': 'ativo', 'embalagem': True},
            {'id': 1700000000001, 'nome': 'Caixa molhada', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': False, 'obs': '', 'status': 'ativo', 'embalagem': True},
            {'id': 1700000000002, 'nome': 'Motivo sem o campo', 'grupo': 'saida', 'destino': 'nfe', 'exigeObs': False, 'obs': '', 'status': 'ativo'}])
        ir_cad(pg)
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        nomes = [x.strip() for x in pg.locator('#acertoMotivo .dropdown-select-item').all_inner_texts()]
        ok(nomes == ['Furto ou roubo', 'Perda em trânsito', 'Caixa molhada'], 'o cadastro guardado manda: some o desmarcado (1), o inativo (2) e o que nunca valeu (6); o guardado sem o campo usa o de fábrica pelo id (3 entra, o criado antes do campo não); o motivo novo marcado entra: %s' % nomes)
        pg.context.close()
        # nenhum motivo vale
        pg = nova()
        poe(pg, 'deskMotivosPerda', [{'id': 6, 'nome': 'Deterioração ou vencimento', 'grupo': 'saida', 'destino': 'interno', 'exigeObs': True, 'obs': '', 'status': 'ativo', 'embalagem': False}])
        ir_cad(pg)
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        ok(pg.inner_text('#acertoMotivo .dropdown-select-label') == 'Nenhum motivo disponível' and 'Nenhum motivo vale para embalagens' in tx(pg, '#dicaMotivoAcerto') and pg.locator('#dicaMotivoAcerto a').get_attribute('href') == '../configuracoes/pagina-configuracoes-motivos-perda.html',
           'sem nenhum motivo marcado a tela diz isso e leva a Motivos de Perda (link ../configuracoes/...)')
        pg.fill('#inputNovoSaldo', '5'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroMotivoAcerto') and ls(pg, 'deskEmbalagens') is None, 'e o acerto não vale sem motivo')
        pg.context.close()
        # cadastro guardado estragado: cai no espelho de fabrica
        pg = nova()
        ir_cad(pg)
        pg.evaluate("localStorage.setItem('deskMotivosPerda', '{lixo')")
        ir_cad(pg)
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        ok(len(pg.locator('#acertoMotivo .dropdown-select-item').all_inner_texts()) == 8, 'cadastro de motivos ilegível: vale o espelho de fábrica (8 motivos)')
        pg.context.close()

    # ================================================================ 4. o acerto
    if secao(4, 'O acerto: direção do motivo, observação obrigatória, prejuízo, o movimento e o Registro de atividades'):
        pg = nova()
        ir_cad(pg)
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150)
        ok(vis(pg, 'blocoAcerto') and vis(pg, 'inputNovoSaldo') and vis(pg, 'acertoMotivo') and vis(pg, 'inputObsAcerto') and vis(pg, 'btnAplicarAcerto') and not vis(pg, 'inputMotivoAcerto'), 'o acerto tem Novo saldo, Motivo (a lista), Observação e Aplicar; o campo de texto solto saiu')
        n_log = len(log_edita(pg))
        # a direcao: Perda e de saida
        escolher(pg, '#acertoMotivo', 2)
        pg.fill('#inputNovoSaldo', '90'); pg.fill('#inputObsAcerto', 'x'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroNovoSaldo') and tx(pg, '#erroNovoSaldo') == 'Este motivo é de saída: o novo saldo tem de ser menor que o atual (85).' and emb(pg, 2) is None and len(log_edita(pg)) == n_log and movs(pg) == [],
           'motivo de SAÍDA com saldo maior que o atual: a mensagem fica no campo do saldo e nada é gravado: %s' % tx(pg, '#erroNovoSaldo'))
        pg.fill('#inputNovoSaldo', '85'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroNovoSaldo') and emb(pg, 2) is None, 'saída com o mesmo saldo também não vale')
        pg.fill('#inputNovoSaldo', 'abc'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(tx(pg, '#erroNovoSaldo') == 'Informe o saldo, como 12 ou -3.', 'saldo que não é número volta à mensagem de número')
        # entrada: Sobra de contagem
        escolher(pg, '#acertoMotivo', 7)
        pg.fill('#inputNovoSaldo', '80'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(tx(pg, '#erroNovoSaldo') == 'Este motivo é de entrada: o novo saldo tem de ser maior que o atual (85).' and emb(pg, 2) is None, 'motivo de ENTRADA com saldo menor: barra, com a mensagem dele')
        # balanco: Contagem fisica aceita os dois, mas nao o igual
        escolher(pg, '#acertoMotivo', 10)
        pg.fill('#inputNovoSaldo', '85'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(tx(pg, '#erroNovoSaldo') == 'O novo saldo é igual ao atual (85): não há o que acertar.' and emb(pg, 2) is None, 'motivo de BALANÇO com o mesmo saldo: não há o que acertar')
        # observacao obrigatoria
        escolher(pg, '#acertoMotivo', 1)
        pg.fill('#inputNovoSaldo', '80'); pg.fill('#inputObsAcerto', ''); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
        ok(mostra(pg, '#erroObsAcerto') and not mostra(pg, '#erroNovoSaldo') and emb(pg, 2) is None and movs(pg) == [], 'motivo que exige observação (Quebra ou avaria) sem ela: avisa no campo e não grava')
        pg.fill('#inputObsAcerto', 'x'); pg.wait_for_timeout(100)
        ok(not mostra(pg, '#erroObsAcerto'), 'digitar a observação tira o aviso')
        # o prejuizo: 85 -> 80 com Quebra (4,70) = 23,50
        pg.fill('#inputObsAcerto', 'Cinco caixas amassadas'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        lg = log_edita(pg)
        ok(emb(pg, 2)['saldo'] == 80 and len(lg) == n_log + 1 and lg[0]['detalhe'] == 'Saldo de Caixa de Encomenda Flex M acertado de 85 para 80. Motivo: Quebra ou avaria (Cinco caixas amassadas). Prejuízo de R$ 23,50 (5 × R$ 4,70).' and lg[0]['acao'] == 'Editar · Embalagens',
           'o acerto para menos com motivo de saída grava o saldo e o Registro diz o motivo e o prejuízo (5 × 4,70 = 23,50): "%s"' % (lg and lg[0]['detalhe']))
        m = movs(pg)[-1]
        ok(m['tipo'] == 'acerto' and m['embId'] == 2 and m['qtd'] == -5 and perto(m['custoUnit'], 4.7) and perto(m['custoMedio'], 4.7) and m['motivoId'] == 1 and m['motivo'] == 'Quebra ou avaria' and m['obs'] == 'Cinco caixas amassadas'
           and perto(m['prejuizo'], 23.5) and m['ref'] == {'tipo': '', 'numero': '', 'texto': ''} and m['fornecedor'] == '' and m['quem'] == 'Administrador Desk' and m['em'] == '2026-10-30T10:00:00',
           'o movimento grava todos os campos: tipo acerto, qtd −5, custo 4,70, motivo, observação, prejuízo 23,50, quem e a hora: %s' % m)
        n_ex = pg.evaluate("EMB_MOV_EXEMPLO.reduce((s, e) => s + e[1].length, 0)")
        ok(len(movs(pg)) == n_ex + 1, 'a lista gravada parte do exemplo de fábrica e acrescenta o movimento no fim (%d = %d + 1)' % (len(movs(pg)), n_ex))
        ok(pg.inner_text('#saldoAtual') == '80' and not vis(pg, 'blocoAcerto'), 'o painel mostra o saldo novo e o acerto fecha')
        # acerto para mais com motivo de entrada: sem prejuizo
        abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(120)
        escolher(pg, '#acertoMotivo', 7); pg.fill('#inputNovoSaldo', '83,5'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        m = movs(pg)[-1]
        ok(emb(pg, 2)['saldo'] == 83.5 and m['qtd'] == 3.5 and m['prejuizo'] == 0 and log_edita(pg)[0]['detalhe'] == 'Saldo de Caixa de Encomenda Flex M acertado de 80 para 83,5. Motivo: Sobra de contagem.',
           'o acerto para mais (Sobra de contagem) não tem prejuízo, e o Registro diz só o motivo: "%s"' % log_edita(pg)[0]['detalhe'])
        # balanco para menos = prejuizo; balanco para mais = sem prejuizo
        abre_card(pg, 3); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(120)
        escolher(pg, '#acertoMotivo', 10); pg.fill('#inputNovoSaldo', '30'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        m = movs(pg)[-1]
        ok(emb(pg, 3)['saldo'] == 30 and m['qtd'] == -2 and perto(m['prejuizo'], 11.8) and m['motivo'] == 'Contagem física' and 'Prejuízo de R$ 11,80 (2 × R$ 5,90).' in log_edita(pg)[0]['detalhe'], 'a contagem física (balanço) que dá falta é prejuízo: 2 × 5,90 = 11,80')
        abre_card(pg, 3); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(120)
        escolher(pg, '#acertoMotivo', 10); pg.fill('#inputNovoSaldo', '33'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        m = movs(pg)[-1]
        ok(sd(pg, 3) == 33 and m['qtd'] == 3 and m['prejuizo'] == 0, 'e a contagem física que dá sobra não é prejuízo')
        # fracionario e negativo
        abre_card(pg, 13); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(120)
        escolher(pg, '#acertoMotivo', 5); pg.fill('#inputNovoSaldo', '-1,5'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(300)
        m = movs(pg)[-1]
        ok(emb(pg, 13)['saldo'] == -1.5 and m['qtd'] == -9.5 and perto(m['prejuizo'], 142.5) and 'Prejuízo de R$ 142,50 (9,5 × R$ 15,00).' in log_edita(pg)[0]['detalhe'], 'o acerto aceita saldo negativo e fração: 9,5 × 15,00 = 142,50')
        pg.context.close()

    # ================================================================ 5. o movimento
    if secao(5, 'O movimento: os campos, o exemplo de fábrica e o guardado estragado'):
        pg = nova()
        ir_cad(pg)
        ex = pg.evaluate("embMovLer()")
        campos = ['em', 'embId', 'tipo', 'qtd', 'custoUnit', 'custoMedio', 'motivoId', 'motivo', 'obs', 'prejuizo', 'ref', 'fornecedor', 'quem']
        ok(len(ex) >= 30 and all(sorted(m.keys()) == sorted(campos) for m in ex), 'o exemplo de fábrica (%d movimentos) tem exatamente os campos do plano: %s' % (len(ex), campos))
        ok(all(sorted(m['ref'].keys()) == ['numero', 'texto', 'tipo'] for m in ex), 'e `ref` é { tipo, numero, texto } em todos')
        ok(set(m['tipo'] for m in ex) == {'entrada_nota', 'entrada_sem_nota', 'baixa_pedido', 'acerto', 'contagem'}, 'o exemplo tem os cinco tipos de movimento: %s' % sorted(set(m['tipo'] for m in ex)))
        ok(all(m['em'] <= '2026-10-30T10:00:00' for m in ex) and all(re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$', m['em']) for m in ex) and ex == sorted(ex, key=lambda m: m['em']), 'com o relógio às 10:00 nenhum movimento nasce no futuro, o formato é AAAA-MM-DDTHH:MM:SS e a lista vem em ordem')
        ok(all((m['qtd'] > 0) == (m['tipo'] in ('entrada_nota', 'entrada_sem_nota')) or m['tipo'] in ('acerto', 'contagem') for m in ex) and all(m['prejuizo'] == 0 or (m['tipo'] in ('acerto', 'contagem') and m['qtd'] < 0) for m in ex), 'entrada soma, baixa subtrai, e só a falta de acerto ou contagem tem prejuízo')
        dias = pg.evaluate("(() => { const hoje = new Date(); const ini = new Date(hoje.getFullYear(), hoje.getMonth(), hoje.getDate() - 60), z = (n) => String(n).padStart(2, '0'); return embMovLer().every(m => m.em.slice(0, 10) >= ini.getFullYear() + '-' + z(ini.getMonth() + 1) + '-' + z(ini.getDate())); })()")
        ok(dias, 'os movimentos são dos últimos 60 dias')
        aj = [m for m in ex if m['tipo'] == 'acerto' and m['em'].startswith('2026-10-30')]
        ok(len(aj) == 1 and aj[0]['embId'] == 2 and aj[0]['em'] == '2026-10-30T09:15:00' and aj[0]['motivo'] == 'Quebra ou avaria' and perto(aj[0]['prejuizo'], 9.4) and aj[0]['qtd'] == -2, 'o acerto de hoje é o de 2 Flex M por quebra ou avaria, às 09:15 (prejuízo 2 × 4,70 = 9,40): %s' % aj)
        # o saldo de abertura nunca e negativo e a ficha fecha no cadastro
        ab = pg.evaluate("embalagensLer().map(e => [e.id, Math.round((e.saldo - embMovLer().filter(m => m.embId === e.id).reduce((t, m) => t + m.qtd, 0)) * 10000) / 10000])")
        ok(all(a >= 0 for i, a in ab), 'o saldo de abertura (saldo do cadastro menos o que o exemplo moveu) não é negativo em NENHUMA embalagem: %s' % [x for x in ab if x[1] < 0])
        ok(any(a > 0 for i, a in ab) and len([1 for i, a in ab if i in (1, 2, 3, 5, 6, 7, 11, 12, 13, 14)]) == 10, 'e o exemplo move 10 embalagens (abertura positiva): %s' % ab)
        ult = pg.evaluate("embalagensLer().map(e => { const l = embMovLer().filter(m => m.embId === e.id); return [e.id, l.length ? l[l.length - 1].custoMedio : null, e.custo]; })")
        ok(all(c is None or perto(c, k) for i, c, k in ult), 'o custo médio do último movimento de cada embalagem é o custo do cadastro (a ficha não desmente o painel): %s' % [x for x in ult if x[1] is not None and not perto(x[1], x[2])])
        # antes das 09:15 o acerto de hoje cai as 00:01
        pg2 = nova(relogio=CEDO)
        ir_cad(pg2)
        ex2 = pg2.evaluate("embMovLer()")
        aj2 = [m for m in ex2 if m['tipo'] == 'acerto' and m['em'].startswith('2026-10-30')]
        ok(len(aj2) == 1 and aj2[0]['em'] == '2026-10-30T00:01:00' and all(m['em'] <= '2026-10-30T08:00:00' for m in ex2), 'com o relógio às 08:00 o acerto de hoje vira 00:01 e nenhum movimento nasce no futuro')
        pg2.context.close()
        # embMovRegistrar: os campos e os padroes
        r = pg.evaluate("embMovRegistrar({ embId: 6, tipo: 'acerto', qtd: 0.123456, custoUnit: 12.5, custoMedio: 12.5, motivoId: 2, motivo: 'Perda', obs: 'x', prejuizo: 1.239, ref: { numero: 7 }, quem: 'Ana' })")
        ok(r['qtd'] == 0.1235 and r['prejuizo'] == 1.24 and r['ref'] == {'tipo': '', 'numero': '7', 'texto': ''} and r['fornecedor'] == '' and r['quem'] == 'Ana' and r['em'] == '2026-10-30T10:00:00', 'embMovRegistrar arredonda a quantidade a 4 casas e o prejuízo a 2, guarda o número do ref como texto e preenche o que faltou: %s' % r)
        r = pg.evaluate("embMovRegistrar({ embId: 6, tipo: 'entrada_sem_nota', qtd: 1 })")
        ok(r['quem'] == 'Sistema' and r['custoUnit'] == 0 and r['motivoId'] is None and r['obs'] == '' and r['prejuizo'] == 0, 'sem `quem` vale "Sistema" (a saída segura de uma tela sem usuário da sessão)')
        gr = movs(pg)
        ok(len(gr) == len(ex) + 2 and gr[:len(ex)] == ex, 'o primeiro registro parte do exemplo de fábrica e acrescenta no fim (%d = %d + 2)' % (len(gr), len(ex)))
        pg.context.close()
        # guardado estragado e lista vazia
        pg = nova()
        ir_cad(pg)
        pg.evaluate("localStorage.setItem('deskMovEmbalagens', '{lixo')")
        ok(pg.evaluate("embMovLer().length") >= 30, 'chave estragada: vale o exemplo de fábrica')
        pg.evaluate("localStorage.setItem('deskMovEmbalagens', JSON.stringify([{ lixo: 1 }, null, { em: '2026-10-01T10:00:00', embId: 2, tipo: 'acerto', qtd: -1 }]))")
        ok(pg.evaluate("embMovLer().length") == 1, 'itens inválidos da lista são descartados, sem derrubar a leitura')
        pg.evaluate("localStorage.setItem('deskMovEmbalagens', '[]')")
        ok(pg.evaluate("embMovLer().length") == 0, 'a lista vazia gravada vale (não volta ao exemplo)')
        pg.context.close()

    # ================================================================ 6. os cards do topo
    if secao(6, 'Os cards do topo: prejuízo do mês, abaixo do mínimo e valor em estoque'):
        pg = nova()
        ir_cad(pg)
        ok(tx(pg, '#kpiPrejuizo .kpi-label').lower() == 'prejuízo com embalagens no mês', 'o card se chama "Prejuízo com embalagens no mês": %s' % tx(pg, '#kpiPrejuizo .kpi-label'))
        ok(tx(pg, '#kpiPrejuizoValor') == 'R$ 13,10' and tx(pg, '#kpiPrejuizoSub') == '3 acertos · o maior: Caixa de Encomenda Flex M', 'o exemplo já acende o card em outubro: 9,40 (Flex M hoje) + 2,20 (a perda de tags) + 1,50 (a contagem do saco) = R$ 13,10, "3 acertos · o maior: Caixa de Encomenda Flex M": %s / %s' % (tx(pg, '#kpiPrejuizoValor'), tx(pg, '#kpiPrejuizoSub')))
        ok(tx(pg, '#kpiMinimoValor') == str(ABAIXO) and tx(pg, '#kpiEstoqueValor') == brl(VALOR_ESTOQUE), '"Abaixo do mínimo": %d (Flex G, CE-02 e a tag da Brands); "Valor em estoque" (saldo × custo): %s' % (ABAIXO, brl(VALOR_ESTOQUE)))
        ok(pg.evaluate("Array.from(document.querySelectorAll('#kpisEmb .kpi-card')).length") == 3, 'a fileira nasce com os três cards')
        ok(pg.get_attribute('#kpiPrejuizo', 'href') == '../estoque/pagina-estoque-movimentacao.html?ver=embalagens' and pg.get_attribute('#kpiMinimo', 'href') == '../estoque/pagina-estoque-necessidades-compra.html', 'o do prejuízo leva à Movimentação em Embalagens e o do mínimo a Necessidades de Compra (links ../<pasta>/<arquivo>)')
        # um acerto novo soma ao card na hora
        acerto(pg, 2, 1, '80', 'Cinco amassadas')
        ok(tx(pg, '#kpiPrejuizoValor') == 'R$ 36,60' and tx(pg, '#kpiPrejuizoSub') == '4 acertos · o maior: Caixa de Encomenda Flex M', 'um acerto novo soma ao card na hora (13,10 + 23,50 = 36,60, 4 acertos): %s' % tx(pg, '#kpiPrejuizoValor'))
        ok(tx(pg, '#kpiEstoqueValor') == brl(VALOR_ESTOQUE - 5 * 4.7), 'e o valor em estoque acompanha o saldo (−5 × 4,70)')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        pg.click('#kpiPrejuizo'); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(MOV in pg.url and 'ver=embalagens' in pg.url and pg.evaluate("document.querySelector('#modoMov .pill-btn.active').dataset.modo") == 'embalagens' and tx(pg, '#campoProduto label') == 'Embalagem',
           'clicar no card abre a Movimentação já em Embalagens: %s' % pg.url.split('/')[-1])
        pg.context.close()
        # o do mes: so conta o mes de hoje
        pg = nova(relogio=PRIMEIRO)
        ir_cad(pg)
        ok(tx(pg, '#kpiPrejuizoValor') == 'R$ 9,40' and tx(pg, '#kpiPrejuizoSub') == '1 acerto · o maior: Caixa de Encomenda Flex M', 'no dia 1 só o acerto de hoje conta no mês: R$ 9,40, "1 acerto" (singular): %s' % tx(pg, '#kpiPrejuizoSub'))
        pg.context.close()
        # sem prejuizo no mes
        pg = nova()
        ir_cad(pg)
        poe(pg, 'deskMovEmbalagens', [])
        ir_cad(pg)
        ok(tx(pg, '#kpiPrejuizoValor') == 'R$ 0,00' and tx(pg, '#kpiPrejuizoSub') == 'nenhum acerto no mês', 'sem prejuízo no mês: "R$ 0,00" e "nenhum acerto no mês": %s / %s' % (tx(pg, '#kpiPrejuizoValor'), tx(pg, '#kpiPrejuizoSub')))
        poe(pg, 'deskMovEmbalagens', [{'em': '2026-09-15T10:00:00', 'embId': 2, 'tipo': 'acerto', 'qtd': -3, 'prejuizo': 14.1}, {'em': '2026-10-10T10:00:00', 'embId': 2, 'tipo': 'acerto', 'qtd': 3, 'prejuizo': 0},
                                      {'em': '2026-10-11T10:00:00', 'embId': 2, 'tipo': 'entrada_nota', 'qtd': 3, 'prejuizo': 7}])
        ir_cad(pg)
        ok(tx(pg, '#kpiPrejuizoValor') == 'R$ 0,00' and tx(pg, '#kpiPrejuizoSub') == 'nenhum acerto no mês', 'prejuízo de outro mês, acerto sem prejuízo e entrada não contam')
        # sem embalagem com saldo, sem abaixo do minimo: nada de NaN
        pg.evaluate("() => { const L = embalagensLer(); L.forEach(e => { e.saldo = 0; e.minimo = 0; }); embalagensGravar(L); }")
        ir_cad(pg)
        ok(tx(pg, '#kpiMinimoValor') == '0' and tx(pg, '#kpiMinimoSub') == 'tudo em dia' and tx(pg, '#kpiEstoqueValor') == 'R$ 0,00' and tx(pg, '#kpiEstoqueSub') == 'nenhuma embalagem com saldo', 'tudo zerado: "0 / tudo em dia" e "R$ 0,00 / nenhuma embalagem com saldo"')
        ok('NaN' not in tx(pg, '#kpisEmb') and 'undefined' not in tx(pg, '#kpisEmb') and 'null' not in tx(pg, '#kpisEmb'), 'e nenhum card mostra NaN, undefined ou null')
        # movimento de embalagem que nao existe mais: o nome cai no codigo
        poe(pg, 'deskMovEmbalagens', [{'em': '2026-10-10T10:00:00', 'embId': 77, 'tipo': 'acerto', 'qtd': -3, 'prejuizo': 14.1}])
        ir_cad(pg)
        ok(tx(pg, '#kpiPrejuizoSub') == '1 acerto · o maior: EMB-077', 'o acerto de uma embalagem excluída mostra o código no lugar do nome, não "undefined"')
        # nada vazio: cada card tem rotulo, valor e linha de baixo
        ok(pg.evaluate("Array.from(document.querySelectorAll('#kpisEmb .kpi-card')).every(c => ['.kpi-label', '.kpi-value', '.kpi-delta'].every(s => c.querySelector(s).textContent.trim() !== ''))"), 'nenhum card sai com rótulo, valor ou linha de baixo vazios')
        pg.context.close()

    # ================================================================ 7. a Movimentacao em Embalagens
    if secao(7, 'A Movimentação em Embalagens: a ficha fecha no cadastro, o saldo de abertura, os textos, os filtros'):
        pg = nova()
        ir(pg, MOV)
        ok(tx(pg, '#modoMov') == 'Consultar Produtos Embalagens' and pg.evaluate("document.querySelector('#modoMov .pill-btn.active').dataset.modo") == 'produtos', 'a tela abre em Produtos, com a escolha "Produtos / Embalagens" junto da busca')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#painelFiltros .form-field label')).map(l => l.textContent)") == ['Depósito', 'Produto', 'Tipo de movimento', 'Data inicial', 'Data final'], 'em Produtos nada mudou: os cinco filtros de antes')
        pg.click('#modoMov [data-modo="embalagens"]'); pg.wait_for_timeout(200)
        ok(tx(pg, '#campoProduto label') == 'Embalagem' and not vis(pg, 'filtroDeposito') and pg.get_attribute('#buscaProduto', 'placeholder') == 'Pesquise por nome ou código (EMB-001)', 'em Embalagens o campo vira "Embalagem", o filtro de depósito some e a busca aceita o código')
        tipos = [x.strip() for x in pg.locator('#filtroTipoMov .dropdown-select-item').all_inner_texts()]
        ok(tipos == ['Todos os tipos', 'Entrada pela nota', 'Entrada sem nota', 'Baixa no pedido', 'Acerto de estoque', 'Contagem física'], 'o filtro de tipo de movimento vale para os dois: em Embalagens traz os cinco tipos de embalagem: %s' % tipos)
        ok('É só consulta' in tx(pg, '.page-header') and pg.evaluate("document.querySelectorAll('select').length") == 0, 'a frase "É só consulta" continua, e nenhum select nativo')
        # a busca: nome e codigo
        pg.fill('#buscaProduto', 'EMB-002'); pg.wait_for_timeout(150)
        sug = pg.evaluate("Array.from(document.querySelectorAll('#sugestoesProduto .sugestao-item')).map(s => s.innerText.replace(/\\s+/g, ' ').trim())")
        ok(sug == ['Caixa de Encomenda Flex M EMB-002 · Pacote / Caixa'], 'digitar o código mostra a embalagem: %s' % sug)
        pg.fill('#buscaProduto', 'fita'); pg.wait_for_timeout(150)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#sugestoesProduto .sugestao-item')).map(s => s.dataset.emb)") == ['13'], 'e o nome também')
        pg.fill('#buscaProduto', 'xyz'); pg.wait_for_timeout(150)
        ok(tx(pg, '#sugestoesProduto') == 'Nenhuma embalagem encontrada para “xyz”.', 'sem resultado: "Nenhuma embalagem encontrada"')
        pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(150)
        ok(tx(pg, '#erroBusca') == 'Escolha a embalagem na lista de sugestões.', 'buscar sem escolher diz "Escolha a embalagem na lista de sugestões."')
        # a ficha da Flex M
        buscar_emb(pg, 'EMB-002')
        ok(pg.evaluate("document.getElementById('painelResultado').classList.contains('modo-emb')") and 'Caixa de Encomenda Flex M' in tx(pg, '#painelProduto .bq-nome') and 'EMB-002 · Pacote / Caixa' in tx(pg, '#painelProduto'), 'o quadro da embalagem mostra o nome, o código e o tipo')
        rows = linhas_mov(pg)
        ok(len(rows) == 8 and rows[0][1].startswith('Saldo de abertura') and rows[0][5] == '48' and rows[0][3] == '—', 'a primeira linha é o "Saldo de abertura": 48 = 85 do cadastro − os 37 que o exemplo moveu')
        ok(rows[-1][5] == '85', 'e a última linha termina no saldo do cadastro (85)')
        cadeia = True
        for i in range(1, len(rows)):
            cadeia = cadeia and num(rows[i][3]) == num(rows[i - 1][5]) and round(num(rows[i][3]) + num(rows[i][4]), 4) == num(rows[i][5])
        ok(cadeia, 'cada linha parte do saldo em que a anterior parou, e saldo anterior + quantidade = saldo atual')
        ok([r[1].split(' ')[0:3] for r in rows[1:4]] == [['Entrada', 'pela', 'nota'], ['Baixa', 'no', 'pedido'], ['Baixa', 'no', 'pedido']] and rows[1][1].startswith('Entrada pela nota nº 8755') and rows[2][1].startswith('Baixa no pedido nº 2910'),
           'o Movimento diz "Entrada pela nota nº 8755", "Baixa no pedido nº 2910": %s' % [r[1] for r in rows[1:3]])
        ok(rows[1][2] == 'Embalagens do Vale' and rows[2][2] == '—' and rows[1][4] == '+30' and rows[2][4] == '−3', 'a entrada traz o fornecedor (Embalagens do Vale), a baixa não tem, e a quantidade vai com o sinal')
        ult = rows[-1]
        ok(ult[1].startswith('Acerto: Quebra ou avaria') and 'prejuízo de R$ 9,40' in ult[1] and ult[4] == '−2' and ult[7] == 'R$ 4,70' and ult[8] == 'R$ 399,50', 'o acerto diz "Acerto: Quebra ou avaria" com "prejuízo de R$ 9,40", e o custo médio e o valor em estoque (85 × 4,70 = 399,50) saem: %s' % ult)
        cor = pg.evaluate("(() => { const s = document.querySelector('#corpoTabela tr:last-child .qtd-saida'); return s ? [s.textContent, getComputedStyle(s).color] : null; })()")
        ok(cor and cor[0].startswith('prejuízo de R$ 9,40') and cor[1] != pg.evaluate("getComputedStyle(document.querySelector('#corpoTabela tr:last-child td')).color"), 'o prejuízo vai em vermelho (a cor da quantidade que sai), diferente do texto da linha: %s' % cor)
        ok(pg.evaluate("document.querySelector('#corpoTabela tr:last-child').title") == 'Duas caixas amassadas na prateleira', 'a observação do acerto fica na linha (passando o mouse)')
        kp = [tx(pg, i) for i in ('#kpiAtual', '#kpiCusto', '#kpiValor', '#kpiPrejuizoMov')]
        ok(kp == ['85', 'R$ 4,70', 'R$ 399,50', 'R$ 9,40'], 'os cards da ficha: estoque atual 85, custo médio 4,70, valor em estoque 399,50 e prejuízo no período 9,40: %s' % kp)
        ok(not vis(pg, 'kpiReservado') and not pg.evaluate("document.querySelector('#kpiDisponivel').offsetParent !== null") and vis(pg, 'kpiPrejuizoMov') and not vis(pg, 'btnResumo'), 'em Embalagens somem Reservado, Disponível e o Resumo por tipo (não se aplicam), e entra o prejuízo do período')
        ok(tx(pg, '#avisoMov').startswith('Saldo antes de ') and tx(pg, '#contagemItens') == '7 movimentações' and tx(pg, '#totalLista') == 'Entradas +50 · Saídas −13 · Saldo no fim do período 85', 'o rodapé diz 7 movimentações (a abertura não é movimento): %s | %s' % (tx(pg, '#contagemItens'), tx(pg, '#totalLista')))
        ok(pg.evaluate("document.querySelectorAll('#corpoTabela tr.sem-doc').length") == 8 and pg.evaluate("getComputedStyle(document.querySelector('#corpoTabela tr')).cursor") == 'default', 'as linhas não são clicáveis (não há documento para abrir): cursor comum')
        corpo = tx(pg, '.main')
        ok('undefined' not in corpo and 'NaN' not in corpo and 'null' not in corpo, 'nenhum "undefined", "NaN" ou "null" na ficha')
        ok(pg.get_attribute('#painelProduto .mv-links a', 'href') == '../cadastros/pagina-cadastros-embalagens.html?busca=EMB-002', 'o link do quadro leva ao cadastro, já na embalagem: ../cadastros/pagina-cadastros-embalagens.html?busca=EMB-002')
        # ordem, filtro de tipo, mes
        pg.click('#painelMov th.ordenavel'); pg.wait_for_timeout(150)
        r2 = linhas_mov(pg)
        ok(r2[0][1].startswith('Acerto: Quebra') and r2[-1][1].startswith('Saldo de abertura'), 'a ordem se inverte (a abertura vai para o fim)')
        pg.click('#painelMov th.ordenavel'); pg.wait_for_timeout(150)
        escolher(pg, '#filtroTipoMov', 'baixa_pedido'); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(200)
        r3 = linhas_mov(pg)
        ok(len(r3) == 4 and all(r[1].startswith('Baixa no pedido') for r in r3), 'o filtro "Baixa no pedido" deixa só as 4 baixas (e esconde a abertura): %s' % [r[1][:24] for r in r3])
        ok(r3[0][3] == '78' and r3[-1][5] == '87', 'filtrar esconde linha, não refaz saldo: a primeira baixa parte de 78 e a última deixa 87')
        escolher(pg, '#filtroTipoMov', 'contagem'); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(200)
        ok(pg.locator('#emptyState').is_visible() and 'A embalagem teve 7 movimentos no período, mas nenhum deste tipo.' in tx(pg, '#emptySub') and 'undefined' not in tx(pg, '#emptySub'), 'tipo sem movimento: estado vazio com a frase certa: %s' % tx(pg, '#emptySub'))
        escolher(pg, '#filtroTipoMov', 'todos')
        pg.fill('#dataDe', '01/10/2026'); pg.fill('#dataAte', '30/10/2026'); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(200)
        r4 = linhas_mov(pg)
        ok(len(r4) == 4 and r4[0][3] == '73' and 'Saldo antes de 01/10/2026: 73' in tx(pg, '#avisoMov') and not any(r[1].startswith('Saldo de abertura') for r in r4),
           'no período de outubro: os 4 movimentos do mês, sem a abertura (que é de antes), e "Saldo antes de 01/10/2026: 73" é o de depois da última baixa de setembro: %s' % tx(pg, '#avisoMov'))
        # embalagem sem movimento no exemplo, e inativa
        for termo, saldo in (('EMB-009', '12'), ('EMB-010', '0'), ('EMB-004', '60')):
            buscar_emb(pg, termo)
            rr = linhas_mov(pg)
            ok(len(rr) == 1 and rr[0][1].startswith('Saldo de abertura') and rr[0][5] == saldo and tx(pg, '#contagemItens') == '0 movimentações' and 'undefined' not in tx(pg, '.main') and 'NaN' not in tx(pg, '.main'),
               '%s sem movimento: só o saldo de abertura (= saldo do cadastro, %s), 0 movimentações, sem NaN' % (termo, saldo))
        # a ficha de TODAS bate com o cadastro (abertura incluida)
        bate = pg.evaluate("embalagensLer().map(e => { const h = embHistorico(e); const u = h.linhas[h.linhas.length - 1]; return [e.id, u.depois, e.saldo, h.linhas[0].abertura === true, h.abertura >= 0]; })")
        ok(all(d == s and a and n for i, d, s, a, n in bate), 'a ficha de cada uma das 14 fecha no saldo do cadastro e começa pelo saldo de abertura: %s' % [x for x in bate if not (x[1] == x[2] and x[3] and x[4])])
        # planilha
        buscar_emb(pg, 'EMB-002')
        with pg.expect_download(timeout=5000) as d:
            pg.click('#btnPlanilha')
        csv = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
        ok(d.value.suggested_filename.startswith('movimentacao-estoque-') and len(csv) == 9 and csv[0] == '"Data";"Hora";"Movimento";"Observação";"Registrado por";"Cliente ou fornecedor";"Saldo anterior";"Quantidade";"Saldo atual";"Valor unitário";"Custo médio";"Valor em estoque";"Prejuízo"',
           'a planilha baixa o histórico inteiro com as colunas da ficha: %s, %d linhas' % (d.value.suggested_filename, len(csv)))
        ok(csv[1].split(';')[2] == '"Saldo de abertura"' and csv[1].split(';')[8] == '"48"' and csv[-1].split(';')[12] == '"9,4"' and csv[-1].split(';')[8] == '"85"', 'com a abertura na primeira linha e o prejuízo na última')
        pg.evaluate("(() => { window.__n = 0; window.print = () => { window.__n++; window.__linhas = document.querySelectorAll('#corpoTabela tr').length; }; })()")
        pg.click('#btnImprimir'); pg.wait_for_timeout(200)
        ok(pg.evaluate("[window.__n, window.__linhas]") == [1, 8], 'Imprimir lista manda as 8 linhas para o papel')
        # so consulta: nada do que o sistema guarda muda
        antes = pg.evaluate("JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))")
        buscar_emb(pg, 'EMB-012'); pg.click('#btnLimpar'); pg.wait_for_timeout(150)
        ok(pg.evaluate("JSON.stringify(Object.keys(localStorage).sort().map(k => [k, localStorage.getItem(k)]))") == antes, 'é só consulta: buscar, ordenar, filtrar e limpar não mudam nada do que o sistema guarda')
        # voltar a Produtos
        pg.click('#modoMov [data-modo="produtos"]'); pg.wait_for_timeout(200)
        ok(tx(pg, '#campoProduto label') == 'Produto' and vis(pg, 'filtroDeposito') and len(pg.locator('#filtroTipoMov .dropdown-select-item').all_inner_texts()) == 10 and not vis(pg, 'painelResultado') and tx(pg, '#inicioTitulo') == 'Escolha um produto e clique em Buscar',
           'voltar a Produtos devolve o depósito, os 9 tipos e a tela ao começo')
        pg.fill('#buscaProduto', 'TEC-MEC-006'); pg.wait_for_timeout(150)
        pg.press('#buscaProduto', 'Enter'); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
        ok(tx(pg, '#painelProduto .bq-nome') == 'Teclado Mecânico Desk' and not pg.evaluate("document.getElementById('painelResultado').classList.contains('modo-emb')") and vis(pg, 'kpiReservado') and not vis(pg, 'kpiPrejuizoMov') and vis(pg, 'btnResumo'), 'e a ficha de produto segue como estava (Reservado e Disponível de volta, sem o card de prejuízo)')
        pg.context.close()
        # o endereco
        pg = nova()
        ir(pg, MOV, '?ver=embalagens')
        ok(pg.evaluate("document.querySelector('#modoMov .pill-btn.active').dataset.modo") == 'embalagens' and tx(pg, '#inicioTitulo') == 'Escolha uma embalagem e clique em Buscar' and not vis(pg, 'painelResultado'), '?ver=embalagens abre já em Embalagens, esperando a escolha')
        ir(pg, MOV, '?ver=embalagens&busca=EMB-013')
        ok('Fita adesiva' in tx(pg, '#painelProduto .bq-nome') and pg.input_value('#buscaProduto') == 'Fita adesiva' and len(linhas_mov(pg)) >= 1, '?ver=embalagens&busca=EMB-013 abre na ficha da Fita adesiva, no mês')
        ir(pg, MOV, '?ver=embalagens&busca=nao-existe')
        ok('Nenhuma embalagem com "nao-existe"' in tx(pg, '#inicioTitulo'), 'busca que não acha diz isso, sem lista vazia nem undefined')
        pg.context.close()
        # sem nada guardado e com cadastro estragado
        pg = nova()
        ir_cad(pg)
        pg.evaluate("localStorage.setItem('deskEmbalagens', 'lixo')"); ir(pg, MOV, '?ver=embalagens&busca=EMB-001')
        ok('NaN' not in tx(pg, '.main') and 'undefined' not in tx(pg, '.main') and len(linhas_mov(pg)) >= 1, 'cadastro de embalagens estragado: vale o padrão de fábrica, sem NaN')
        pg.context.close()

    # ================================================================ 8. a entrada sem nota
    if secao(8, 'A entrada sem nota: soma o saldo, recalcula o custo médio e grava o movimento'):
        pg = nova()
        ir_cad(pg)
        ok(tx(pg, '#btnDarEntrada') == 'Dar entrada sem nota', 'o botão do cabeçalho agora é "Dar entrada sem nota"')
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(350)
        ok(tx(pg, '#entradaDrawer .drawer-title') == 'Dar entrada sem nota' and tx(pg, '#btnSalvarEntrada') == 'Dar entrada sem nota', 'o painel e o botão dele dizem "Dar entrada sem nota"')
        rot = pg.evaluate("Array.from(document.querySelectorAll('#entradaDrawer label')).map(l => l.textContent)")
        ok(rot == ['Embalagem', 'Quantidade', 'Custo da unidade (R$)', 'Fornecedor (opcional)', 'Comprovante (opcional)'], 'o campo "Nota" virou "Comprovante (opcional)": %s' % rot)
        ok('Compra com nota fiscal entra pela Entrada de Notas' in tx(pg, '#entradaDrawer .form-field:nth-of-type(5)') and pg.locator('#entradaDrawer .form-field a').get_attribute('href') == '../estoque/pagina-estoque-entrada-notas.html', 'a dica diz que compra com nota entra pela Entrada de Notas, com o link ../estoque/pagina-estoque-entrada-notas.html')
        ok(pg.get_attribute('#entradaNota', 'placeholder') == 'Ex: Recibo 118', 'o exemplo do campo é um recibo, não uma NF')
        escolher(pg, '#entradaEmb', 13)
        pg.fill('#entradaQtd', '2'); pg.fill('#entradaCusto', '17,00'); pg.fill('#entradaFornecedor', 'Papelaria Central'); pg.fill('#entradaNota', 'Recibo 9'); pg.wait_for_timeout(150)
        ok(pg.inner_text('#entradaPrevia') == 'Saldo 8 → 10 · custo R$ 15,00 → R$ 15,40 (médio)', 'a prévia mostra saldo e custo médio: %s' % pg.inner_text('#entradaPrevia'))
        pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        f = emb(pg, 13)
        ok(f['saldo'] == 10 and perto(f['custo'], 15.4), 'soma ao saldo (8 → 10) e recalcula o custo médio (15,40): %s' % [f['saldo'], f['custo']])
        m = movs(pg)[-1]
        ok(m['tipo'] == 'entrada_sem_nota' and m['embId'] == 13 and m['qtd'] == 2 and perto(m['custoUnit'], 17) and perto(m['custoMedio'], 15.4) and m['fornecedor'] == 'Papelaria Central'
           and m['ref'] == {'tipo': 'comprovante', 'numero': 'Recibo 9', 'texto': 'comprovante Recibo 9'} and m['prejuizo'] == 0 and m['quem'] == 'Administrador Desk' and m['em'] == '2026-10-30T10:00:00',
           'grava o movimento entrada_sem_nota: qtd 2, custo da unidade 17, custo médio 15,40, fornecedor, comprovante e quem: %s' % m)
        lg = log_edita(pg)
        ok(len(lg) == 1 and 'Entrada sem nota de 2 Fita adesiva a R$ 17,00 a unidade.' in lg[0]['detalhe'] and 'Comprovante: Recibo 9.' in lg[0]['detalhe'] and 'Saldo 8 → 10' in lg[0]['detalhe'], 'o Registro de atividades diz "Entrada sem nota" e o comprovante: %s' % (lg and lg[0]['detalhe']))
        # saldo zerado: vale o custo da entrada
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        escolher(pg, '#entradaEmb', 9)
        pg.fill('#entradaQtd', '3'); pg.fill('#entradaCusto', '5,00'); pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        m = movs(pg)[-1]
        ok(emb(pg, 9)['saldo'] == 15 and perto(emb(pg, 9)['custo'], 4.6) and perto(m['custoMedio'], 4.6) and m['ref'] == {'tipo': 'comprovante', 'numero': '', 'texto': ''} and m['fornecedor'] == '', 'sem comprovante nem fornecedor o movimento sai com os campos vazios e a média certa ((12 × 4,50 + 3 × 5,00) ÷ 15 = 4,60)')
        pg.context.close()
        # a ficha na Movimentacao mostra a entrada
        pg = nova()
        ir_cad(pg)
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        escolher(pg, '#entradaEmb', 6); pg.fill('#entradaQtd', '4'); pg.fill('#entradaCusto', '13,00'); pg.fill('#entradaNota', 'Recibo 77'); pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        ir(pg, MOV, '?ver=embalagens&busca=EMB-006')
        pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)")); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
        rows = linhas_mov(pg)
        ok(rows[-1][1].startswith('Entrada sem nota') and rows[-1][2] == '—' and rows[-1][4] == '+4' and rows[-1][5] == '10' and rows[-1][6] == 'R$ 13,00' and rows[-1][7] == 'R$ 12,70' and rows[-1][8] == 'R$ 127,00',
           'a Movimentação mostra "Entrada sem nota" na ficha da Caixa para Eletrônicos: +4, saldo 10, custo da unidade 13,00, custo médio 12,70 ((6 × 12,50 + 4 × 13,00) ÷ 10) e valor em estoque 127,00: %s' % rows[-1])
        ok(rows[0][1].startswith('Saldo de abertura') and rows[0][5] == '2' and rows[-1][5] == '10', 'e o saldo de abertura segue o mesmo (2), com o saldo atual de 10 no fim')
        pg.context.close()

    # ================================================================ 9. a Conferencia de Saida
    if secao(9, 'A Conferência de Saída grava a baixa com o pedido, uma vez só'):
        pg = nova()
        ir(pg, SEP_F, '?id=4')
        for s in ('VES-2001', 'PAP-3001', 'VES-2002'):
            pg.fill('#campoBipar', s); pg.press('#campoBipar', 'Enter')
        pg.wait_for_timeout(250)
        pg.click('#btnConcluir'); pg.wait_for_timeout(300)
        pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
        ok(ls(pg, 'deskMovEmbalagens') is None, 'a Separação não baixa nada: nenhum movimento gravado')
        ir(pg, CONF_F, '?id=4')
        numero = pg.evaluate("String(PEDIDO.numero)")
        pg.click('#btnConferirTudo'); pg.wait_for_timeout(300); pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)
        pg.click('#btnFechar'); pg.wait_for_timeout(320)
        pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)
        pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)
        quem = pg.evaluate("OPERADORES[EU]")
        bx = [m for m in movs(pg) if m['tipo'] == 'baixa_pedido' and m['em'].startswith('2026-10-30T10')]
        por = {m['embId']: m for m in bx}
        ok(sorted(por) == [5, 12, 13] and len(bx) == 3, 'fechar o pedido grava UM movimento baixa_pedido por embalagem baixada (5, 12 e 13): %s' % sorted(por))
        ok(all(m['ref'] == {'tipo': 'pedido', 'numero': numero, 'texto': 'pedido nº ' + numero} for m in bx) and bool(quem) and all(m['quem'] == quem for m in bx), 'cada um leva o número do pedido (%s) e quem conferiu (%s)' % (numero, quem))
        ok(por[5]['qtd'] == -1 and perto(por[5]['custoUnit'], 6.3) and perto(por[5]['custoMedio'], 6.3) and por[12]['qtd'] == -1 and por[13]['qtd'] == -0.02 and perto(por[13]['custoUnit'], 15) and all(m['prejuizo'] == 0 and m['motivoId'] is None for m in bx),
           'a quantidade é a baixa de verdade (a fita em 1/50 = −0,02, a caixa −1), com o custo do cadastro e sem prejuízo: %s' % [(m['embId'], m['qtd']) for m in bx])
        ok(emb(pg, 5)['saldo'] == 17 and emb(pg, 12)['saldo'] == 149 and emb(pg, 13)['saldo'] == 7.98, 'e o saldo baixou junto (17, 149 e 7,98): o movimento e o cadastro não se desmentem')
        # reaberta: nao baixa de novo
        ir(pg, CONF_F, '?id=4')
        pg.evaluate("fechada = false"); pg.evaluate("fechar()"); pg.wait_for_timeout(320)
        pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)
        pg.evaluate("window.scrollTo(0, 0)"); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(320)
        bx2 = [m for m in movs(pg) if m['tipo'] == 'baixa_pedido' and m['em'].startswith('2026-10-30T10')]
        ok(len(bx2) == 3 and emb(pg, 5)['saldo'] == 17 and emb(pg, 13)['saldo'] == 7.98, 'ficha reaberta que já estava confirmada: fechar de novo NÃO grava outro movimento (continuam 3) nem baixa de novo')
        # a ficha na Movimentacao
        ir(pg, MOV, '?ver=embalagens&busca=EMB-012')
        pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)")); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
        rows = linhas_mov(pg)
        ok(rows[-1][1].startswith('Baixa no pedido nº ' + numero) and rows[-1][4] == '−1' and rows[-1][5] == '149' and rows[0][1].startswith('Saldo de abertura') and rows[0][5] == '19', 'a Movimentação mostra "Baixa no pedido nº %s" na ficha da Tag Desk Brands, com o saldo de abertura (19) intacto: %s' % (numero, rows[-1][1]))
        bate = pg.evaluate("embalagensLer().map(e => { const h = embHistorico(e); return [e.id, h.linhas[h.linhas.length - 1].depois === Number(e.saldo), h.abertura >= 0]; })")
        ok(all(a and b for i, a, b in bate), 'depois da baixa, a ficha de TODAS as embalagens ainda fecha no cadastro, com abertura não negativa')
        pg.context.close()
        # a baixa isolada: embBaixar com e sem ref
        pg = nova()
        ir(pg, CONF_F, '?id=4')
        r = pg.evaluate("(() => { const av = embBaixar([{ id: 2, qtd: 3 }, { id: 2, qtd: 1 }], { numero: 77, texto: 'pedido nº 77' }, 'Fulana'); const m = embMovLer().filter(x => x.embId === 2 && x.tipo === 'baixa_pedido').pop(); return [av, m.qtd, m.ref, m.quem, embalagensLer().filter(e => e.id === 2)[0].saldo]; })()")
        ok(r[1] == -4 and r[2] == {'tipo': 'pedido', 'numero': '77', 'texto': 'pedido nº 77'} and r[3] == 'Fulana' and r[4] == 81, 'embBaixar(itens, ref, quem): a mesma embalagem duas vezes vira UM movimento de −4, com o número 77 e quem chamou: %s' % r[1:])
        r = pg.evaluate("(() => { embBaixar([{ id: 6, qtd: 1 }]); const m = embMovLer().filter(x => x.embId === 6 && x.tipo === 'baixa_pedido').pop(); return [m.ref, m.quem]; })()")
        ok(r[0] == {'tipo': 'pedido', 'numero': '', 'texto': ''} and r[1] == 'Sistema', 'sem ref nem quem o movimento sai sem pedido e "Sistema" (não quebra)')
        pg.context.close()

    # ================================================================ 10. blocos
    if secao(10, 'Os blocos comuns: as cópias idênticas'):
        IN, FIM = '  // ===== EMBALAGENS: LEITURA (bloco comum', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA ====='
        com = [c for c in localiza.caminhos() if IN in open(c, encoding='utf-8').read()]
        blocos = []
        for c in com:
            t = open(c, encoding='utf-8').read()
            a = t.index(IN); blocos.append(t[a:t.index(FIM, a) + len(FIM)])
        nomes = [_os.path.basename(c) for c in com]
        ok(len(com) == 16 and all(b == blocos[0] for b in blocos), 'o bloco EMBALAGENS: LEITURA é idêntico nas 16 cópias (as 14 de antes, a Entrada de Notas e o Inventário): %d, diferentes: %s' % (len(com), [n for n, b in zip(nomes, blocos) if b != blocos[0]]))
        ok(MOV in nomes and CONF_F in nomes and CAD in nomes and NOTA in nomes and INVT in nomes and NC in nomes, 'e as telas dos dois pacotes (Embalagens, Conferência de Saída, Movimentação, Necessidades de Compra, Entrada de Notas e Inventário) estão entre elas')
        ok(all(t.count('function embEntradaConta(e, qtd, custoUnit)') == 1 for t in [open(c, encoding='utf-8').read() for c in com]) and 'A conta da entrada de embalagem, uma so' in blocos[0], 'a conta da entrada (embEntradaConta) mora no bloco comum, uma vez em cada cópia')
        ok('Identico em 10 telas' not in blocos[0] and 'grep -rl "EMBALAGENS: LEITURA (bloco comum" telas' in blocos[0] and 'teste_embalagens_estoque.py compara as copias' in blocos[0] and 'ANTES dele' in blocos[0], 'o cabeçalho do bloco não tem número nem lista: diz o grep, quem compara e por que vem antes do RESULTADO DO PEDIDO')
        b0 = blocos[0]
        ok(b0.count("fornecedor: 'Embalagens do Vale' }") == 14 and "'fornecedor' in e" in b0 and 'fornecedor            o nome do fornecedor padrao' in b0, 'o bloco comum documenta o campo `fornecedor` e traz as 14 de fábrica no Vale (as cópias são idênticas pela comparação acima)')
        ok(all(x in b0 for x in ('function embCodigo(e)', 'function embMovRegistrar(m)', 'function embMovLer()', 'function embMovExemplo()', 'function embBaixar(itens, ref, quem)', "tipo: 'baixa_pedido'", "'deskMovEmbalagens'")) and b0.count('function embBaixar') == 1,
           'o bloco traz embCodigo, embMovRegistrar, embMovLer, o exemplo e o embBaixar(itens, ref, quem), uma vez cada')
        ok(all(t.count('function embCodigo') == 1 and t.count('function embMovRegistrar') == 1 for t in [open(c, encoding='utf-8').read() for c in com]), 'cada tela declara as funções uma vez só')
        ok(re.search(r"jaConfirmada \? \[\] : embBaixar\(itensEmb, \{ numero: PEDIDO.numero", fonte(CONF_F)) is not None, 'a Conferência de Saída continua baixando só quando o pedido não estava confirmado (jaConfirmada ? [] : embBaixar(...)) e passa o número do pedido')
        ok(all('embBaixar(' not in fonte(n).replace(b0, '') for n in nomes if n != CONF_F), 'ninguém mais chama o embBaixar fora do bloco')

    # ================================================================ 11. fotos e barras de rolagem
    if secao(11, 'Fotos nos dois temas, a 1280 e a 1440, sem barra de rolagem para o lado'):
        def tema(pg, t):
            pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", t); pg.wait_for_timeout(300)

        def lateral(pg):
            return pg.evaluate("(() => [document.documentElement.scrollWidth - document.documentElement.clientWidth, Math.max.apply(null, [0].concat(Array.from(document.querySelectorAll('.estoque-table-wrap')).map(w => w.scrollWidth - w.clientWidth)))])()")

        for w in (1280, 1440):
            for t in ('light', 'dark'):
                pg = nova(w, 900)
                ir_cad(pg); tema(pg, t)
                pg.screenshot(path=_os.path.join(FOTOS, 'embalagens_lista_%d_%s.png' % (w, t)))
                ok(lateral(pg)[0] <= 0 and pg.evaluate("(() => { const k = Array.from(document.querySelectorAll('#kpisEmb .kpi-card')).map(c => c.getBoundingClientRect()); return k.every(r => r.width > 150) && Math.max.apply(null, k.map(r => r.top)) - Math.min.apply(null, k.map(r => r.top)) < 1; })()"),
                   'Embalagens a %d px, tema %s: sem barra para o lado e os três cards na mesma fileira' % (w, t))
                abre_card(pg, 2); pg.click('#linkAcertarSaldo'); pg.wait_for_timeout(150); escolher(pg, '#acertoMotivo', 1)
                pg.fill('#inputNovoSaldo', '80'); pg.click('#btnAplicarAcerto'); pg.wait_for_timeout(150)
                pg.evaluate("document.getElementById('eventDrawer').scrollTop = 600"); pg.wait_for_timeout(150)
                pg.screenshot(path=_os.path.join(FOTOS, 'embalagens_painel_acerto_%d_%s.png' % (w, t)))
                m = pg.evaluate("(() => { const d = document.getElementById('eventDrawer'), r = d.getBoundingClientRect(); const rot = Array.from(d.querySelectorAll('label')).filter(l => l.getBoundingClientRect().width > 0).map(l => Math.round(l.getBoundingClientRect().height)); const fora = Array.from(d.querySelectorAll('input, .dropdown-select-btn, .saldo-leitura, button')).filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > r.right - 20).length; return { rot: Math.max.apply(null, rot), fora: fora, lateral: d.scrollWidth - d.clientWidth }; })()")
                ok(m['rot'] < 20 and m['fora'] == 0 and m['lateral'] <= 0, 'painel de Embalagens com o acerto aberto a %d px, tema %s: rótulos numa linha só, nada passa da borda: %s' % (w, t, m))
                pg.click('#drawerClose'); pg.wait_for_timeout(300)
                pg.click('#btnDarEntrada'); pg.wait_for_timeout(350)
                pg.screenshot(path=_os.path.join(FOTOS, 'embalagens_entrada_%d_%s.png' % (w, t)))
                m = pg.evaluate("(() => { const d = document.getElementById('entradaDrawer'), r = d.getBoundingClientRect(); const rot = Array.from(d.querySelectorAll('label')).filter(l => l.getBoundingClientRect().width > 0).map(l => Math.round(l.getBoundingClientRect().height)); const fora = Array.from(d.querySelectorAll('input, .dropdown-select-btn, button')).filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > r.right - 20).length; return { rot: Math.max.apply(null, rot), fora: fora, lateral: d.scrollWidth - d.clientWidth }; })()")
                ok(m['rot'] < 20 and m['fora'] == 0 and m['lateral'] <= 0, 'painel de entrada sem nota a %d px, tema %s: rótulos numa linha só, nada passa da borda: %s' % (w, t, m))
                pg.context.close()
                # a Movimentacao em Embalagens
                pg = nova(w, 900)
                ir(pg, MOV, '?ver=embalagens&busca=EMB-002'); tema(pg, t)
                pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)")); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
                pg.set_viewport_size({'width': w, 'height': 1500}); pg.wait_for_timeout(200)   # janela alta: a foto da pagina inteira mostraria a folha de confirmacao (fora da tela) por cima da lista
                pg.screenshot(path=_os.path.join(FOTOS, 'movimentacao_embalagens_%d_%s.png' % (w, t)))
                pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(150)
                lat = lateral(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'Movimentação em Embalagens a %d px, tema %s: sem barra para o lado, nem na página nem na tabela: %s' % (w, t, lat))
                ok(pg.evaluate("(() => { const k = Array.from(document.querySelectorAll('#painelResultado .mv-kpis .kpi-card')).filter(c => c.offsetParent !== null).map(c => c.getBoundingClientRect()); return k.length === 4 && Math.max.apply(null, k.map(r => r.top)) - Math.min.apply(null, k.map(r => r.top)) < 1; })()"), 'e os quatro cards da ficha ficam na mesma fileira')
                pg.click('#modoMov [data-modo="produtos"]'); pg.wait_for_timeout(200)
                pg.screenshot(path=_os.path.join(FOTOS, 'movimentacao_produtos_%d_%s.png' % (w, t)))
                ok(lateral(pg)[0] <= 0, 'Movimentação em Produtos a %d px, tema %s: sem barra para o lado' % (w, t))
                pg.context.close()
                # Motivos de Perda
                pg = nova(w, 900)
                ir(pg, MOTIVOS); tema(pg, t)
                pg.screenshot(path=_os.path.join(FOTOS, 'motivos_lista_%d_%s.png' % (w, t)))
                pg.evaluate("document.querySelector('#listaMotivos .motivo-card').click()"); pg.wait_for_timeout(400)
                pg.evaluate("document.getElementById('inputEmbalagem').scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(200)
                pg.screenshot(path=_os.path.join(FOTOS, 'motivos_formulario_%d_%s.png' % (w, t)))
                m = pg.evaluate("(() => { const d = document.getElementById('eventDrawer'); return { lateral: d.scrollWidth - d.clientWidth, pagina: document.documentElement.scrollWidth - document.documentElement.clientWidth }; })()")
                ok(m['lateral'] <= 0 and m['pagina'] <= 0, 'Motivos de Perda a %d px, tema %s: o painel com "Vale para embalagens" não rola para o lado: %s' % (w, t, m))
                pg.context.close()
        print('  fotos em %s (%d arquivos)' % (FOTOS, len(_g.glob(_os.path.join(FOTOS, '*.png')))))


    # ================================================================ pacote 2: ajudantes
    NOMES_EMB = {1: 'Caixa de Encomenda Flex P', 2: 'Caixa de Encomenda Flex M', 3: 'Caixa de Encomenda Flex G', 5: 'Caixa de Encomenda CE-02', 12: 'Tag Desk Brands', 13: 'Fita adesiva'}
    CNPJ_VALE = '55666777000166'

    def ordem_emb(numero, itens, situacao='aberto'):
        """Uma ordem gerada so de embalagens, como a Necessidades de Compra grava. itens = [(embId, qtd, preco, recebido)]."""
        return {'numero': numero, 'data': '2026-10-30', 'previsto': '', 'fornecedor': 'Embalagens do Vale', 'dep': 1, 'total': round(sum(i[1] * i[2] for i in itens), 2), 'situacao': situacao,
                'itens': [{'nome': NOMES_EMB[i[0]], 'sku': 'EMB-%03d' % i[0], 'qtd': i[1], 'un': 'UN', 'preco': i[2], 'recebido': i[3] if len(i) > 3 else 0, 'embId': i[0]} for i in itens]}

    def gerar_ordem(pg, ids, forn='5'):
        ir(pg, NC)
        for i in ids:
            pg.click('#corpoEmbalagens tr[data-id="%d"] .item-checkbox' % i)
        pg.click('#btnGerarEmb'); pg.wait_for_timeout(300)
        if forn:
            pg.evaluate("(v) => document.querySelector('#ocForn0 .dropdown-select-item[data-value=\"' + v + '\"]').click()", forn)
        pg.click('#btnConfirmarOrdem'); pg.wait_for_timeout(400)
        if forn:
            pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)

    def preenche_nota(pg, serie, numero, forn=None):
        if forn:
            escolher(pg, '#inputFornecedor', forn)
        pg.fill('#inputSerie', serie); pg.fill('#inputNumero', numero); pg.fill('#inputEmissao', '29/10/2026'); pg.fill('#inputEntrada', '30/10/2026')
        pg.fill('#inputNatureza', 'Compra'); pg.fill('#inputCondicao', '30 dias')
        escolher(pg, '#inputDeposito', 1)
        pg.evaluate("document.querySelector('#inputCategoria .dropdown-select-item').click()")

    def salvar_nota(pg):
        pg.click('#btnSalvar'); pg.wait_for_timeout(400)
        return tx(pg, '#confirmModalTexto')

    def notas(pg):
        return ls(pg, 'deskNotasLancadas') or []

    def ordens(pg):
        return ls(pg, 'deskOrdensGeradas') or []

    # ================================================================ 12. necessidades de compra
    if secao(12, 'Necessidades de Compra: o chegando, o comprar, a caixa de marcar e a ordem só de embalagens'):
        pg = nova()
        ir(pg, NC)
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaEmbalagens thead th')).map(th => th.textContent.trim())")
        ok(cab == ['', 'Código', 'Embalagem', 'Tipo', 'Saldo', 'Chegando', 'Mínimo', 'Comprar', 'Custo da unidade', 'Total'], 'o bloco das embalagens tem a caixa de marcar e a coluna Código e a Chegando: %s' % cab)
        txt = tx(pg, '#painelEmbalagens')
        ok('Dar entrada' not in txt and 'Aqui não se gera ordem de compra' not in txt and pg.evaluate("document.querySelectorAll('#corpoEmbalagens a').length") == 0, 'saíram o link "Dar entrada" e a frase "Aqui não se gera ordem de compra"')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr td:nth-child(2)')).map(td => td.textContent)") == ['EMB-003', 'EMB-005', 'EMB-012'], 'o código de cada linha vem do cadastro (EMB-003, EMB-005, EMB-012)')
        ok(not pg.evaluate("document.getElementById('barraSelecaoEmb').classList.contains('show')"), 'sem nada marcado, a barra de seleção das embalagens não aparece')
        pg.click('#corpoEmbalagens tr[data-id="3"] .item-checkbox'); pg.click('#corpoEmbalagens tr[data-id="12"] .item-checkbox')
        ok(tx(pg, '#selecaoInfoEmb') == '2 embalagens selecionadas · R$ 77,20' and pg.evaluate("document.getElementById('barraSelecaoEmb').classList.contains('show')"), 'marcar duas embalagens mostra a barra com a soma (8 × 5,90 + 50 × 0,60 = R$ 77,20): %s' % tx(pg, '#selecaoInfoEmb'))
        # fornecedor obrigatorio
        pg.click('#btnGerarEmb'); pg.wait_for_timeout(300)
        ok('Ordem só de embalagens' in tx(pg, '#drawerCorpo') and pg.evaluate("document.getElementById('ocDeposito')") is None, 'o painel é o das ordens de produto, sem depósito (embalagem não tem) e com o aviso de que a mercadoria entra pela nota')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#drawerCorpo .prod-sku')).map(e => e.textContent)") == ['EMB-003', 'EMB-012'], 'cada item mostra o código EMB no lugar do SKU')
        pg.click('#btnConfirmarOrdem'); pg.wait_for_timeout(250)
        ok(tx(pg, '#ocErro0') == 'Selecione o fornecedor desta ordem.' and ordens(pg) == [], 'sem fornecedor a ordem não nasce: a mensagem aparece e nada é gravado')
        # quantidade editavel
        pg.fill('#drawerCorpo .nc-qtd[data-item="0"]', '10'); pg.wait_for_timeout(120)
        ok(tx(pg, '#ocTotalGeral') == 'R$ 89,00', 'a quantidade é editável e o total acompanha (10 × 5,90 + 50 × 0,60 = R$ 89,00): %s' % tx(pg, '#ocTotalGeral'))
        pg.evaluate("document.querySelector('#ocForn0 .dropdown-select-item[data-value=\"5\"]').click()")
        pg.fill('#drawerCorpo .nc-qtd[data-item="0"]', '2,5'); pg.click('#btnConfirmarOrdem'); pg.wait_for_timeout(250)
        ok('número inteiro' in tx(pg, '#ocErro0') and len(ordens(pg)) == 0, 'embalagem se compra em unidades inteiras: 2,5 é barrado e nada é gravado')
        pg.fill('#drawerCorpo .nc-qtd[data-item="0"]', '8')
        pg.click('#btnConfirmarOrdem'); pg.wait_for_timeout(400)
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
        o = ordens(pg)
        ok(len(o) == 1 and o[0]['numero'] == 15 and o[0]['fornecedor'] == 'Embalagens do Vale' and o[0]['situacao'] == 'aberto' and o[0]['dep'] == 1 and perto(o[0]['total'], 77.2), 'a ordem nasce em deskOrdensGeradas: nº 15, Embalagens do Vale, em aberto, R$ 77,20: %s' % [(x['numero'], x['total']) for x in o])
        ok(o[0]['itens'] == [{'nome': 'Caixa de Encomenda Flex G', 'sku': 'EMB-003', 'qtd': 8, 'un': 'UN', 'preco': 5.9, 'recebido': 0, 'embId': 3}, {'nome': 'Tag Desk Brands', 'sku': 'EMB-012', 'qtd': 50, 'un': 'UN', 'preco': 0.6, 'recebido': 0, 'embId': 12}],
           'os itens levam nome, o código no lugar do SKU, a quantidade, UN, o custo como preço, recebido 0 e o embId: %s' % o[0]['itens'])
        ok('nº 15 para Embalagens do Vale (R$ 77,20)' in tx(pg, '#confirmModalTexto') and 'no card das embalagens' in tx(pg, '#confirmModalTexto'), 'o aviso diz a ordem e que ela já conta como chegando no card das embalagens')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(1, 10).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        ok(linhas == [['EMB-005', 'Caixa de Encomenda CE-02', 'Pacote / Caixa', '18', '—', '20', '2', 'R$ 6,30', 'R$ 12,60']],
           'a Flex G e a Tag, que a ordem cobre, SAEM da tabela (só fica o que ainda dá para pedir): a CE-02, com 2 a comprar: %s' % linhas)
        ok(tx(pg, '#embPedidas .emb-pedidas-titulo') == '2 embalagens já pedidas' and vis(pg, 'embPedidas') and 'já estão pedidas' in tx(pg, '#embPedidas') and 'não precisam de compra agora' in tx(pg, '#embPedidas'),
           'acima da tabela entra o bloco "2 embalagens já pedidas", que diz que já estão pedidas e não precisam de compra agora: %s' % tx(pg, '#embPedidas')[:120])
        ok(pg.evaluate("Array.from(document.querySelectorAll('#embPedidas .emb-pedida-linha')).map(l => l.innerText.replace(/\s+/g, ' ').trim())") == ['EMB-003 Caixa de Encomenda Flex G 8 a caminho ordem nº 15', 'EMB-012 Tag Desk Brands 50 a caminho ordem nº 15'],
           'uma linha por embalagem: código, nome, quantidade a caminho e o número da ordem')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#embPedidas a')).map(a => a.getAttribute('href'))") == ['../estoque/pagina-estoque-ordens-compra-detalhe.html?id=15'] * 2, 'cada ordem é um link para a ordem (?id=15)')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens .item-checkbox')).map(c => c.disabled)") == [False] and not pg.evaluate("document.getElementById('barraSelecaoEmb').classList.contains('show')") and pg.evaluate("document.querySelectorAll('#corpoEmbalagens .item-checkbox[title]').length") == 0,
           'sem caixa travada na tabela: o que sobrou tem caixa de marcar normal, e a seleção das que saíram foi limpa')
        pg.click('#embPedidas a'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(pg.url.endswith('pagina-estoque-ordens-compra-detalhe.html?id=15') and pg.evaluate("ITENS.map(i => i.sku)") == ['EMB-003', 'EMB-012'], 'e o link abre a ordem nº 15, com as duas embalagens')
        pg.context.close()
        # o chegando e a conta
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 3, 5.9)]), ordem_emb(16, [(3, 2, 5.9, 1)], 'andamento'), ordem_emb(17, [(3, 90, 5.9)], 'atendida'), ordem_emb(18, [(3, 90, 5.9)], 'cancelada'), ordem_emb(19, [(5, 4, 6.3, 4)])])
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(1, 10).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        ok(linhas[0][4] == '4 ordem nº 15, nº 16' and linhas[0][6] == '4', 'chegando = (qtd − recebido) das ordens em aberto e em andamento (3 + 1 = 4); atendida e cancelada não contam; comprar = 8 − 4 = 4: %s' % linhas[0])
        ok(linhas[1][4] == '—' and linhas[1][6] == '2', 'ordem com tudo recebido não é chegando (a CE-02 segue pedindo 2)')
        ok(pg.evaluate("[embCompra({ id: 9, saldo: 3.98, minimo: 4 }, {}).comprar, embCompra({ id: 9, saldo: 5, minimo: 5 }, { 9: [{ numero: 1, qtd: 4.9 }] }).comprar, embCompra({ id: 9, saldo: 0.1, minimo: 5 }, { 9: [{ numero: 1, qtd: 4.9 }] }).comprar, embCompra({ id: 9, saldo: 0, minimo: 10 }, { 9: [{ numero: 1, qtd: 99 }] }).comprar]") == [1, 0, 0, 0],
           'comprar = max(0, teto(mínimo − saldo − chegando)): 3,98 de 4 pede 1; o erro de ponto flutuante (5 − 0,1 − 4,9) não pede 1; chegando maior que a falta dá 0, nunca negativo')
        pg.context.close()
        # o bloco no singular, a ordem atendida (volta para a tabela), a que cobre so em parte (fica) e a lista sem pedidas (o bloco some)
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9)])])
        ir(pg, NC)
        ok(tx(pg, '#embPedidas .emb-pedidas-titulo') == '1 embalagem já pedida' and pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => tr.getAttribute('data-id'))") == ['5', '12'], 'com uma só: "1 embalagem já pedida", e a Tag (sem ordem) segue na tabela junto da CE-02')
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 8)], 'atendida')])
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(1, 10).map(td => td.innerText.replace(/\s+/g, ' ').trim()))")
        ok(not vis(pg, 'embPedidas') and [l[0] for l in linhas] == ['EMB-003', 'EMB-005', 'EMB-012'] and linhas[0][4] == '—' and linhas[0][6] == '8', 'ordem atendida: a quantidade a caminho cai a zero, o bloco some e a Flex G VOLTA para a tabela (ainda abaixo do mínimo), pedindo 8: %s' % linhas[0])
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 4)], 'andamento')])
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(1, 10).map(td => td.innerText.replace(/\s+/g, ' ').trim()))")
        ok(not vis(pg, 'embPedidas') and linhas[0][0] == 'EMB-003' and linhas[0][4] == '4 ordem nº 15' and linhas[0][6] == '4', 'ordem em andamento que cobre só em parte (faltam 4 de 8): a Flex G continua na tabela, com o chegando e 4 a comprar, e não vira aviso: %s' % linhas[0])
        pg.context.close()
        pg = nova()
        ir(pg, NC)
        ok(not vis(pg, 'embPedidas') and pg.evaluate("document.getElementById('embPedidas').innerHTML") == '', 'sem nenhuma ordem, o bloco não existe')
        pg.context.close()
        # sem nenhuma ordem de produto mexida
        pg = nova()
        ir(pg, NC)
        ok(pg.evaluate("document.querySelectorAll('#corpoTabela tr').length") > 0 and pg.evaluate("document.getElementById('barraSelecao').classList.contains('show')") is False, 'a lista de produtos continua do mesmo jeito, com a barra dela separada da barra das embalagens')

    # ================================================================ 13. ordens de compra
    if secao(13, 'Ordens de Compra: a ordem gerada lê o recebido e a situação gravados; "Gerar nota de entrada" leva a ordem'):
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 3), (12, 50, 0.6, 0)], 'andamento'), ordem_emb(16, [(5, 4, 6.3)])])
        ir(pg, OCL)
        r = pg.evaluate("[ORDENS.filter(o => o.numero === 15)[0].situacao, ORDENS.filter(o => o.numero === 16)[0].situacao, ITENS_OC[15].map(i => [i.sku, i.qtd, i.recebido]), ITENS_OC[16][0].recebido]")
        ok(r[0] == 'andamento' and r[1] == 'aberto' and r[2] == [['EMB-003', 8, 3], ['EMB-012', 50, 0]] and r[3] == 0, 'a lista lê a situação (andamento e aberto) e o recebido gravados, com o código na linha: %s' % r)
        pg.evaluate("abrirPreview(15)"); pg.wait_for_timeout(300)
        d = tx(pg, '#drawerCorpo')
        ok('EM ANDAMENTO' in d.upper() and 'EMB-003 · 8 UN × R$ 5,90 · recebido 3 de 8' in d and 'EMB-012 · 50 UN × R$ 0,60 · não recebido' in d, 'o painel da ordem mostra o código e o que já chegou ("recebido 3 de 8"): %s' % d[:260])
        pg.context.close()
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 3), (12, 50, 0.6, 0)], 'andamento')])
        ir(pg, OCD, '?id=15')
        r = pg.evaluate("[ORDEM.situacao, ITENS.map(i => [i.sku, i.qtd, i.recebido]), Array.from(document.querySelectorAll('#corpoItens input[data-campo=\"sku\"]')).map(i => i.value), Array.from(document.querySelectorAll('.item-recebido')).map(e => e.textContent)]")
        ok(r[0] == 'andamento' and r[1] == [['EMB-003', 8, 3], ['EMB-012', 50, 0]] and r[2] == ['EMB-003', 'EMB-012'] and r[3] == ['recebido 3 de 8'], 'o detalhe lê a situação e o recebido, mostra o código na linha e diz o que já chegou só onde chegou algo: %s' % r)
        ok('EM ANDAMENTO' in tx(pg, '#badgeSituacao').upper(), 'e a situação na tela é "Em andamento"')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"nota\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(pg.url.endswith('pagina-estoque-entrada-notas-detalhe.html?oc=15') and pg.get_attribute('#inputOC', 'data-value') == '15', 'a ação da nota leva ?oc=15 e a Entrada de Notas abre com a ordem escolhida: %s' % pg.url[-50:])
        ir(pg, OCD, '?id=2')
        ok(pg.evaluate("ITENS.map(i => i.recebido)") == [12, 0] and pg.evaluate("document.querySelectorAll('.item-recebido').length") == 1, 'a ordem de exemplo nº 2 também mostra o recebido do exemplo (12 de 30) e nada onde não chegou')
        pg.context.close()

    # ================================================================ 14. a nota soma o saldo
    if secao(14, 'Entrada de Notas: a ordem gerada, a embalagem que entra no saldo, o custo médio e a ordem marcada'):
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 3), (12, 50, 0.6, 0)], 'andamento')])
        ir(pg, NOTA, '?oc=15')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#inputOC .dropdown-select-item')).map(i => i.textContent)") == ['Sem ordem vinculada', 'Ordem nº 2', 'Ordem nº 3', 'Ordem nº 11', 'Ordem nº 15'], 'o campo da ordem lista também as geradas em aberto e em andamento')
        ok(pg.get_attribute('#inputOC', 'data-value') == '15' and pg.get_attribute('#inputFornecedor', 'data-value') == '5' and tx(pg, '#inputFornecedor .dropdown-select-label') == 'Embalagens do Vale' and pg.input_value('#inputCEP') == '65915-000', '?oc=15 já vem com a ordem escolhida e o fornecedor preenchido (com o endereço dele)')
        ok(pg.evaluate("ITENS.map(i => [i.nome, i.sku, i.qtd, i.preco, i.un])") == [['Caixa de Encomenda Flex G', 'EMB-003', 5, 5.9, 'UN'], ['Tag Desk Brands', 'EMB-012', 50, 0.6, 'UN']], 'os itens são os pendentes (pedido − recebido): 8 − 3 = 5 da Flex G e 50 da Tag')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoItens input[data-campo=\"sku\"]')).map(i => i.value)") == ['EMB-003', 'EMB-012'], 'a tabela mostra o código na coluna SKU')
        pg.evaluate("ITENS[0].preco = 6.4; ITENS[1].preco = 0.7; renderItens()")
        preenche_nota(pg, '1', '123')
        aviso = salvar_nota(pg)
        e3, e12 = emb(pg, 3), emb(pg, 12)
        ok(e3['saldo'] == 37 and e12['saldo'] == 200, 'a linha de embalagem soma ao saldo (32 + 5 = 37; 150 + 50 = 200): %s' % [e3['saldo'], e12['saldo']])
        ok(perto(e3['custo'], 5.97) and perto(e12['custo'], 0.63), 'o custo médio é o ponderado, não o preço da nota: (32 × 5,90 + 5 × 6,40) ÷ 37 = 5,97 e (150 × 0,60 + 50 × 0,70) ÷ 200 = 0,63: %s' % [e3['custo'], e12['custo']])
        m = [x for x in movs(pg) if x['tipo'] == 'entrada_nota' and x['em'].startswith('2026-10-30T10')]
        ok(len(m) == 2 and [x['embId'] for x in m] == [3, 12] and m[0]['qtd'] == 5 and perto(m[0]['custoUnit'], 6.4) and perto(m[0]['custoMedio'], 5.97) and perto(m[1]['custoUnit'], 0.7) and perto(m[1]['custoMedio'], 0.63),
           'grava um movimento entrada_nota por linha: qtd, custo da unidade = o preço da linha, custo médio = o novo: %s' % [(x['embId'], x['qtd'], x['custoUnit'], x['custoMedio']) for x in m])
        ok(all(x['ref'] == {'tipo': 'nota', 'numero': '123', 'texto': 'nota nº 123, série 1'} and x['fornecedor'] == 'Embalagens do Vale' and x['quem'] == 'Administrador Desk' and x['prejuizo'] == 0 for x in m), 'o movimento leva o número e a série da nota, o fornecedor e quem lançou')
        o = ordens(pg)[0]
        ok(o['situacao'] == 'atendida' and [i['recebido'] for i in o['itens']] == [8, 50], 'a ordem soma o recebido (3 + 5 = 8; 0 + 50) e, com tudo chegado, fica atendida: %s %s' % (o['situacao'], [i['recebido'] for i in o['itens']]))
        ok('2 embalagens entraram no saldo' in aviso and 'Caixa de Encomenda Flex G (+5)' in aviso and 'Tag Desk Brands (+50)' in aviso and 'material de uso e não passa pela conferência' in aviso and 'Não sobrou nada desta nota para a Conferência de Entrada' in aviso and 'ordem de compra nº 15 ficou atendida' in aviso,
           'o aviso diz quantas embalagens entraram, que material de uso não passa pela conferência e a situação da ordem: %s' % aviso)
        pg.context.close()
        # parcial: a ordem fica em andamento e o chegando cai
        pg = nova()
        poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9)])])
        ir(pg, NOTA, '?oc=15')
        pg.evaluate("ITENS[0].qtd = 3; renderItens()")
        preenche_nota(pg, '1', '77')
        aviso = salvar_nota(pg)
        o = ordens(pg)[0]
        ok(o['situacao'] == 'andamento' and o['itens'][0]['recebido'] == 3 and 'ficou em andamento' in aviso, 'chegou só parte: a ordem fica em andamento com recebido 3 de 8: %s' % [o['situacao'], o['itens'][0]['recebido']])
        ir(pg, NC)
        linhas = pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => Array.from(tr.children).slice(1, 10).map(td => td.innerText.replace(/\\s+/g, ' ').trim()))")
        ok(pg.evaluate("Array.from(document.querySelectorAll('#embPedidas .emb-pedida-linha')).map(l => l.innerText.replace(/\s+/g, ' ').trim())") == ['EMB-003 Caixa de Encomenda Flex G 5 a caminho ordem nº 15'] and pg.evaluate("Array.from(document.querySelectorAll('#corpoEmbalagens tr')).map(tr => tr.getAttribute('data-id'))") == ['5', '12'], 'em Necessidades de Compra o chegando caiu para o que falta (5; com o saldo em 35 ainda cobre o mínimo): a Flex G segue no aviso das já pedidas, e só a CE-02 e a Tag estão na tabela')
        pg.context.close()
        # a mesma conta nas duas telas
        pg = nova()
        ir(pg, NOTA)
        a = pg.evaluate("[embEntradaConta({ saldo: 32, custo: 5.9 }, 5, 6.4), embEntradaConta({ saldo: -2, custo: 5 }, 10, 7), embEntradaConta({ saldo: 0, custo: 5 }, 10, 7.005)]")
        ir_cad(pg)
        b = pg.evaluate("[embEntradaConta({ saldo: 32, custo: 5.9 }, 5, 6.4), embEntradaConta({ saldo: -2, custo: 5 }, 10, 7), embEntradaConta({ saldo: 0, custo: 5 }, 10, 7.005)]")
        ok(a == b and a[0]['novoSaldo'] == 37 and perto(a[0]['novoCusto'], 5.97) and a[0]['medio'] is True and a[1]['novoSaldo'] == 8 and a[1]['novoCusto'] == 7 and a[1]['medio'] is False and a[2]['novoCusto'] == 7.01,
           'a conta é uma só e dá o mesmo na Entrada de Notas e em Embalagens: saldo positivo pesa (5,97); saldo negativo ou zerado vale só o custo da entrada: %s' % a)
        pg.click('#btnDarEntrada'); pg.wait_for_timeout(300)
        escolher(pg, '#entradaEmb', 3); pg.fill('#entradaQtd', '5'); pg.fill('#entradaCusto', '6,40'); pg.click('#btnSalvarEntrada'); pg.wait_for_timeout(300)
        ok(emb(pg, 3)['saldo'] == 37 and perto(emb(pg, 3)['custo'], 5.97) and perto(movs(pg)[-1]['custoMedio'], 5.97), 'o "Dar entrada sem nota" com os mesmos números dá o mesmo resultado da nota (37 e 5,97)')
        ok(all('(r.saldo + qtd)' not in fonte(n) for n in (CAD, NOTA)) and 'embEntradaConta(e, qtd, custoEnt)' in fonte(CAD) and 'embEntradaConta(e, it.qtd, it.preco)' in fonte(NOTA), 'nenhuma das duas telas guarda a fórmula do custo médio: as duas chamam embEntradaConta')
        pg.context.close()
        # o codigo digitado: o nome vem do cadastro; codigo que nao existe e embalagem inativa
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill('#corpoItens input[data-campo="sku"]', 'emb-005'); pg.press('#corpoItens input[data-campo="sku"]', 'Tab'); pg.wait_for_timeout(150)
        ok(pg.evaluate("[ITENS[0].sku, ITENS[0].nome, document.querySelector('#corpoItens input[data-campo=\"nome\"]').value]") == ['EMB-005', 'Caixa de Encomenda CE-02', 'Caixa de Encomenda CE-02'], 'digitar emb-005 no SKU vira EMB-005 e o nome vem do cadastro (Caixa de Encomenda CE-02)')
        pg.fill('#corpoItens input[data-campo="sku"]', 'EMB-099'); pg.press('#corpoItens input[data-campo="sku"]', 'Tab')
        preenche_nota(pg, '1', '500', '5')
        pg.click('#btnSalvar'); pg.wait_for_timeout(300)
        ok('O código EMB-099 não existe no cadastro de Embalagens.' in tx(pg, '#blocoErros') and notas(pg) == [] and ls(pg, 'deskMovEmbalagens') is None, 'código EMB que não existe: pendência na lista, e nada é gravado (nem nota, nem movimento)')
        pg.fill('#corpoItens input[data-campo="sku"]', 'EMB-010'); pg.press('#corpoItens input[data-campo="sku"]', 'Tab'); pg.click('#btnSalvar'); pg.wait_for_timeout(300)
        ok('EMB-010 (Rolo para Tecido) está inativa' in tx(pg, '#blocoErros') and notas(pg) == [], 'embalagem inativa também é barrada, como na entrada sem nota')
        pg.context.close()
        # nota mista: a embalagem entra, o produto segue para a conferencia
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.evaluate("ITENS[1].sku = 'EMB-012'; ITENS[1].nome = 'x'; ITENS[1].qtd = 10; ITENS[1].preco = 0.6; renderItens()")
        preenche_nota(pg, '2', '900', '1')
        aviso = salvar_nota(pg)
        ok('1 embalagem entrou no saldo: Tag Desk Brands (+10)' in aviso and 'O produto da nota entra na fila de Conferência de Entrada' in aviso and emb(pg, 12)['saldo'] == 160 and len(movs(pg)) == 53, 'nota com produto e embalagem: a embalagem entra (150 + 10), o produto segue para a Conferência de Entrada e só ela gera movimento: %s' % aviso[:200])
        ok([n['chave'] for n in notas(pg)] == ['98765432000110|2|900'], 'a chave grava com o CNPJ do fornecedor 1 (só os dígitos), a série e o número')
        pg.context.close()
        # nota so de produto: o texto de antes, e nada de embalagem mexe
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        preenche_nota(pg, '1', '321', '1')
        aviso = salvar_nota(pg)
        ok(aviso.startswith('Nota salva. Ela entra na fila de Conferência de Entrada') and 'embalagem' not in aviso and ls(pg, 'deskMovEmbalagens') is None and ls(pg, 'deskEmbalagens') is None and len(notas(pg)) == 1, 'nota só de produto: o aviso é o de antes, nenhuma embalagem é mexida, e a chave grava do mesmo jeito')
        pg.context.close()

    # ================================================================ 15. a nota que nao entra duas vezes
    if secao(15, 'A mesma nota não entra duas vezes: chave normalizada, mensagem no campo do número, nada gravado'):
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(100)
        pg.evaluate("ITENS[0].sku = 'EMB-012'; ITENS[0].nome = 'x'; ITENS[0].qtd = 10; ITENS[0].preco = 0.6; renderItens()")
        preenche_nota(pg, '1', '123', '5')
        ok(pg.evaluate("chaveDaNota()") == CNPJ_VALE + '|1|123', 'a chave é o CNPJ (só os dígitos) + série + número, separados por |: %s' % pg.evaluate("chaveDaNota()"))
        pg.fill('#inputNumero', ' 000123 '); pg.fill('#inputSerie', ' 01 ')
        ok(pg.evaluate("chaveDaNota()") == CNPJ_VALE + '|1|123', 'espaços e zeros à esquerda não mudam a chave (" 01 " e " 000123 " são 1 e 123)')
        pg.fill('#inputNumero', '000'); pg.fill('#inputSerie', '0')
        ok(pg.evaluate("chaveDaNota()") == CNPJ_VALE + '|0|0', 'número 000 vira 0, não vazio')
        pg.fill('#inputSerie', 'a'); pg.fill('#inputNumero', '123')
        ok(pg.evaluate("chaveDaNota()") == CNPJ_VALE + '|A|123', 'a série é comparada sem diferença de maiúscula')
        pg.fill('#inputSerie', '1'); pg.fill('#inputNumero', '123')
        salvar_nota(pg); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
        ok(notas(pg) == [{'chave': CNPJ_VALE + '|1|123', 'em': '2026-10-30', 'fornecedor': 'Embalagens do Vale'}], 'a primeira vez grava a chave, a data (AAAA-MM-DD) e o fornecedor: %s' % notas(pg))
        saldo, n_mov = emb(pg, 12)['saldo'], len(movs(pg))
        pg.fill('#inputNumero', '0000123'); pg.fill('#inputSerie', ' 1')
        pg.click('#btnSalvar'); pg.wait_for_timeout(350)
        ok(tx(pg, '#erroNumero') == 'Esta nota já foi lançada em 30/10/2026.' and mostra(pg, '#erroNumero') and pg.evaluate("document.getElementById('campoNumero').classList.contains('has-error')"), 'a segunda vez é barrada no campo do número, com a data real: "%s"' % tx(pg, '#erroNumero'))
        ok('Esta nota já foi lançada em 30/10/2026.' in tx(pg, '#blocoErros'), 'e a mensagem entra na lista de pendências no topo')
        ok(emb(pg, 12)['saldo'] == saldo and len(movs(pg)) == n_mov and len(notas(pg)) == 1, 'barrada antes de qualquer gravação: o saldo (%s), os movimentos (%d) e a lista de notas (1) não mudam' % (saldo, n_mov))
        pg.fill('#inputNumero', '124'); pg.click('#btnSalvar'); pg.wait_for_timeout(350)
        ok(tx(pg, '#erroNumero') != 'Esta nota já foi lançada em 30/10/2026.' or not mostra(pg, '#erroNumero'), 'outro número passa (a mensagem de repetida sai)')
        pg.keyboard.press('Escape')
        ok(len(notas(pg)) == 2 and emb(pg, 12)['saldo'] == saldo + 10, 'e entra normalmente: 2 notas guardadas e o saldo soma de novo (%s)' % emb(pg, 12)['saldo'])
        pg.fill('#inputSerie', '2'); pg.fill('#inputNumero', '123')
        ok(pg.evaluate("notaJaLancada()") is None, 'a mesma numeração em outra série é outra nota')
        escolher(pg, '#inputFornecedor', 1)
        pg.fill('#inputSerie', '1')
        ok(pg.evaluate("notaJaLancada()") is None and pg.evaluate("chaveDaNota()").startswith('98765432000110|'), 'o mesmo número de outro fornecedor (CNPJ diferente) é outra nota')
        pg.context.close()
        # a chave sobrevive a recarregar e vale em nota de produto
        pg = nova()
        poe(pg, 'deskNotasLancadas', [{'chave': '98765432000110|1|321', 'em': '2026-10-01', 'fornecedor': 'TechParts Distribuidora'}])
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(100)
        preenche_nota(pg, '1', '321', '1')
        pg.click('#btnSalvar'); pg.wait_for_timeout(350)
        ok(tx(pg, '#erroNumero') == 'Esta nota já foi lançada em 01/10/2026.', 'a nota de produto também não entra duas vezes (a data da guardada, 01/10/2026): "%s"' % tx(pg, '#erroNumero'))
        poe(pg, 'deskNotasLancadas', 'lixo')
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(100)
        preenche_nota(pg, '1', '321', '1')
        salvar_nota(pg)
        ok(len(notas(pg)) == 1, 'lista guardada estragada: a tela não quebra e começa de novo')
        pg.context.close()

    # ================================================================ 16. inventario
    if secao(16, 'Inventário de embalagens: diferença contra a abertura, prejuízo, sem trava, e o coletor recusa o código EMB'):
        pg = nova()
        ir(pg, INVT)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(300)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#modoInv .pill-btn')).map(b => b.textContent + ':' + b.classList.contains('active'))") == ['Produtos:true', 'Embalagens:false'] and tx(pg, '#modoInv .mv-modo-rotulo') == 'Contar', 'ao gerar, a escolha "Produtos / Embalagens" usa os mesmos .pill-btn da Movimentação, com Produtos de início')
        ok(vis(pg, 'wrapDeposito') and vis(pg, 'camposGerar'), 'em Produtos o painel é o de antes (depósito e filtros)')
        pg.click('#modoInv [data-modo="embalagens"]'); pg.wait_for_timeout(200)
        ok(not vis(pg, 'wrapDeposito') and not vis(pg, 'camposGerar') and 'não trava nada' in tx(pg, '#previaGerar') and '13 embalagem(ns)' in tx(pg, '#previaGerar'), 'em Embalagens some o depósito e os filtros, e a prévia diz que não trava nada e quantas são (13, as ativas)')
        ok('saldo de quando o inventário é gerado' in tx(pg, '#previaGerar') and 'baixas dos pedidos' in tx(pg, '#previaGerar'), 'a prévia diz que a diferença é contra o saldo de quando foi gerado e que as baixas dos pedidos continuam valendo')
        pg.click('#modoInv [data-modo="produtos"]'); pg.wait_for_timeout(150)
        ok(vis(pg, 'wrapDeposito') and vis(pg, 'camposGerar'), 'voltar a Produtos traz o painel de antes')
        pg.click('#btnCancelarDrawer'); pg.wait_for_timeout(200)
        pg.click('[data-caminho="planilha"]'); pg.wait_for_timeout(250)
        ok(not vis(pg, 'modoInv'), 'planilha (e coletor) seguem só para produtos: sem a escolha')
        pg.click('#btnCancelarDrawer'); pg.wait_for_timeout(200)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(250)
        ok(pg.evaluate("tipoGerar") == 'produtos' and vis(pg, 'modoInv'), 'reabrir o painel volta em Produtos')
        pg.click('#modoInv [data-modo="embalagens"]'); pg.click('#btnAbrirInventario'); pg.wait_for_timeout(300)
        ok(pg.evaluate("INV.tipo") == 'embalagens' and len(pg.evaluate("INV.linhas")) == 13 and all(l['abertura'] == FAB[l['eid']][0] for l in pg.evaluate("INV.linhas")) and not any(l['eid'] == 10 for l in pg.evaluate("INV.linhas")), 'abre com as 13 ativas (a inativa fica de fora), cada uma com o saldo da abertura = o do cadastro')
        cab = pg.evaluate("Array.from(document.querySelectorAll('#tabelaInvEmb thead th')).map(th => th.textContent.trim())")
        ok(cab == ['Código', 'Embalagem', 'Tipo', 'Custo', 'Saldo na abertura', 'Qtde inventário', 'Diferença', 'Valor da diferença'] and vis(pg, 'tabelaInvEmb') and not vis(pg, 'tabelaInv'), 'a tabela é a das embalagens: %s' % cab)
        ok('nada fica travado' in tx(pg, '#textoTravado') and 'saldo da abertura' in tx(pg, '#textoTravado') and 'prejuízo' in tx(pg, '#textoTravado'), 'o texto da tela diz que nada trava, que a diferença é contra a abertura e que a falta é prejuízo')
        ok(pg.evaluate("document.querySelector('#corpoInvEmb tr td').textContent") == 'EMB-001' and pg.evaluate("Array.from(document.querySelectorAll('#corpoInvEmb tr')).map(tr => tr.children[0].textContent).slice(0, 3)") == ['EMB-001', 'EMB-002', 'EMB-003'], 'cada linha mostra o código')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"filtros\"]').click()"); pg.fill('#campoBuscaInv', 'tag'); pg.wait_for_timeout(150)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoInvEmb tr')).map(tr => tr.children[0].textContent)") == ['EMB-011', 'EMB-012'], 'a busca acha pelo nome (tag → as duas tags)')
        pg.fill('#campoBuscaInv', 'EMB-013'); pg.wait_for_timeout(150)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoInvEmb tr')).map(tr => tr.children[0].textContent)") == ['EMB-013'], 'e pelo código')
        pg.fill('#campoBuscaInv', '')
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(200)
        # a baixa de um pedido DURANTE a contagem: o inventario nao trava
        pg.evaluate("embBaixar([{ id: 2, qtd: 3 }], { numero: 77 }, 'Fulana')")
        for i, v in ((2, '80'), (1, '140'), (5, '20'), (13, '7,5'), (12, '150')):
            pg.fill('[data-eid="%d"][data-campo="qtdeInvEmb"]' % i, v)
        c = pg.evaluate("Array.from(document.querySelectorAll('#corpoInvEmb tr')).filter(tr => ['2','1','5','13'].includes(tr.getAttribute('data-eid'))).map(tr => [tr.getAttribute('data-eid'), tr.children[6].innerText, tr.children[7].innerText])")
        ok(c == [['1', '0', 'R$ 0,00'], ['2', '-5', '−R$ 23,50'], ['5', '+2', '+R$ 12,60'], ['13', '-0,5', '−R$ 7,50']], 'a diferença na tela é contra a abertura (Flex M: 80 − 85 = −5, mesmo com a baixa de 3 no meio): %s' % c)
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(300)
        prev = tx(pg, '#previaFechar')
        ok('8 embalagem(ns) não foram contadas' in prev and 'contra o saldo de quando o inventário foi gerado' in prev and 'baixas dos pedidos feitas durante a contagem continuam valendo' in prev and 'Sobra: +2 un.' in prev and 'Falta: −5,5 un.' in prev and 'prejuízo de R$ 31,00' in prev,
           'o painel de fechar diz as não contadas, que a diferença é contra a abertura e que as baixas valem, a sobra e a falta com o prejuízo de R$ 31,00: %s' % prev[:300])
        pg.fill('#inputSenha', 'x'); pg.click('#btnConfirmarFechar'); pg.wait_for_timeout(500)
        aviso = tx(pg, '#avisoTexto')
        ok('Inventário de embalagens nº 1 fechado' in aviso and '2 divergência' not in aviso and '3 divergência(s) aplicada(s)' in aviso and 'prejuízo de R$ 31,00' in aviso, 'o aviso de fechamento: nº 1, 3 divergências (as iguais não contam), o prejuízo: %s' % aviso)
        ok(emb(pg, 2)['saldo'] == 77 and emb(pg, 5)['saldo'] == 20 and perto(emb(pg, 13)['saldo'], 7.5) and emb(pg, 1)['saldo'] == 140 and emb(pg, 12)['saldo'] == 150 and sd(pg, 3) == 32,
           'o saldo novo = o saldo de AGORA + a diferença: Flex M 85 − 3 (pedido) − 5 = 77; CE-02 18 + 2 = 20; fita 8 − 0,5 = 7,5; as iguais e as não contadas ficam como estão')
        mc = [m for m in movs(pg) if m['tipo'] == 'contagem' and m['ref']['tipo'] == 'inventario']
        por = {m['embId']: m for m in mc}
        ok(sorted(por) == [2, 5, 13] and len(mc) == 3, 'só as três com diferença geram movimento contagem (a de diferença zero e as não contadas não): %s' % sorted(por))
        ok(por[2]['qtd'] == -5 and por[2]['prejuizo'] == 23.5 and por[13]['qtd'] == -0.5 and por[13]['prejuizo'] == 7.5 and por[5]['qtd'] == 2 and por[5]['prejuizo'] == 0, 'a qtd é a diferença, e a falta vira prejuízo = a quantidade × o custo (23,50 e 7,50; a sobra não): %s' % [(i, m['qtd'], m['prejuizo']) for i, m in por.items()])
        ok(all(m['motivoId'] == 10 and m['motivo'] == 'Contagem física' and m['ref'] == {'tipo': 'inventario', 'numero': '1', 'texto': 'inventário nº 1'} and m['quem'] == 'Administrador Desk' and perto(m['custoUnit'], m['custoMedio']) for m in mc), 'o movimento leva o motivo Contagem física (id 10), "inventário nº 1" e quem fechou; o custo médio é o de agora')
        ok(perto(por[2]['custoUnit'], 4.7) and perto(por[13]['custoUnit'], 15), 'o custo no movimento é o do cadastro de agora')
        ok(vis(pg, 'painelIndice') and not vis(pg, 'painelInventario'), 'fechado, a tela volta ao índice')
        # o numero segue
        pg.click('#btnAvisoOk'); pg.wait_for_timeout(250)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(250)
        pg.click('#modoInv [data-modo="embalagens"]'); pg.click('#btnAbrirInventario'); pg.wait_for_timeout(300)
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(150)
        pg.fill('[data-eid="3"][data-campo="qtdeInvEmb"]', '30'); pg.click('#btnAcaoInv'); pg.wait_for_timeout(250)
        pg.fill('#inputSenha', 'x'); pg.click('#btnConfirmarFechar'); pg.wait_for_timeout(500)
        ok(movs(pg)[-1]['ref']['numero'] == '2' and movs(pg)[-1]['qtd'] == -2 and perto(movs(pg)[-1]['prejuizo'], 11.8) and emb(pg, 3)['saldo'] == 30, 'o segundo inventário é o nº 2 (Flex G 32 → 30, prejuízo de R$ 11,80)')
        # cancelar
        pg.click('#btnAvisoOk'); pg.wait_for_timeout(250)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(250)
        pg.click('#modoInv [data-modo="embalagens"]'); pg.click('#btnAbrirInventario'); pg.wait_for_timeout(300)
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(150)
        pg.fill('[data-eid="1"][data-campo="qtdeInvEmb"]', '139')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"cancelar\"]').click()"); pg.wait_for_timeout(300)
        ok('descarta 1 quantidade já informada' in tx(pg, '#avisoTexto') and 'destrava' not in tx(pg, '#avisoTexto'), 'cancelar o de embalagens pergunta sem falar de depósito: %s' % tx(pg, '#avisoTexto'))
        pg.click('#btnAvisoOk'); pg.wait_for_timeout(600)
        ok(emb(pg, 1)['saldo'] == 140 and len([m for m in movs(pg) if m['ref']['tipo'] == 'inventario']) == 4 and 'cancelado' in tx(pg, '#avisoTexto'), 'cancelado: nenhum saldo mudou e nenhum movimento foi gravado')
        pg.context.close()
        # o coletor e a planilha recusam o codigo de embalagem
        for caminho, nome, corpo in (('coletor', 'c.txt', b'EMB-003\nEMB-003\nemb-012\nCAD-ERG-001\nCAD-ERG-001\n'), ('planilha', 'p.csv', b'codigo;qtd\nEMB-003;2\nCAD-ERG-001;2\n')):
            pg = nova()
            ir(pg, INVT)
            pg.click('[data-caminho="%s"]' % caminho); pg.wait_for_timeout(250)
            pg.set_input_files('#inputArquivo', {'name': nome, 'mimeType': 'text/plain', 'buffer': corpo}); pg.wait_for_timeout(400)
            escolher(pg, '#campoDeposito', 2)
            ok('não casaram' in tx(pg, '#previaGerar') or 'não casou' in tx(pg, '#previaGerar'), '%s: a prévia conta o que não casou: %s' % (caminho, tx(pg, '#previaGerar')[:200]))
            pg.click('#btnAbrirInventario'); pg.wait_for_timeout(500)
            rec = pg.evaluate("INV.recusados")
            esperado = [{'codigo': 'EMB-003', 'qtd': 2, 'motivo': 'código de embalagem: conte no inventário de embalagens'}] + ([{'codigo': 'emb-012', 'qtd': 1, 'motivo': 'código de embalagem: conte no inventário de embalagens'}] if caminho == 'coletor' else [])
            ok(rec == esperado, '%s: o código de embalagem é recusado com o motivo "código de embalagem: conte no inventário de embalagens": %s' % (caminho, rec))
            ok(pg.evaluate("INV.tipo") == 'produtos' and pg.evaluate("INV.linhas.filter(l => l.contado !== null).length") == 1 and ls(pg, 'deskMovEmbalagens') is None, '%s: o inventário aberto é de produtos, só o produto foi contado, e nenhuma embalagem foi mexida' % caminho)
            pg.context.close()

    # ================================================================ 17. fotos do pacote 2
    if secao(17, 'Fotos do pacote 2 nos dois temas, a 1280 e a 1440, sem barra de rolagem para o lado'):
        def tema2(pg, t):
            pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", t); pg.wait_for_timeout(300)

        def lateral2(pg):
            return pg.evaluate("(() => [document.documentElement.scrollWidth - document.documentElement.clientWidth, Math.max.apply(null, [0].concat(Array.from(document.querySelectorAll('.estoque-table-wrap, .itens-table-wrap')).filter(w => w.getClientRects().length).map(w => w.scrollWidth - w.clientWidth)))])()")

        for w in (1280, 1440):
            for t in ('light', 'dark'):
                pg = nova(w, 900)
                poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 3), (12, 50, 0.6, 0)], 'andamento')])
                # 1. o bloco das embalagens, com o chegando
                ir(pg, NC); tema2(pg, t)
                pg.evaluate("document.getElementById('painelEmbalagens').scrollIntoView({ block: 'start' })"); pg.wait_for_timeout(150)
                pg.click('#corpoEmbalagens tr[data-id="5"] .item-checkbox'); pg.wait_for_timeout(150)
                pg.screenshot(path=_os.path.join(FOTOS, 'nc_embalagens_%d_%s.png' % (w, t)))
                lat = lateral2(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'Necessidades de Compra, bloco das embalagens, a %d px, tema %s: sem barra para o lado, nem na página nem na tabela: %s' % (w, t, lat))
                # 2. o painel de gerar a ordem
                pg.click('#btnGerarEmb'); pg.wait_for_timeout(350)
                pg.screenshot(path=_os.path.join(FOTOS, 'nc_painel_ordem_%d_%s.png' % (w, t)))
                m = pg.evaluate("(() => { const d = document.getElementById('eventDrawer'), r = d.getBoundingClientRect(); return { lateral: d.scrollWidth - d.clientWidth, fora: Array.from(d.querySelectorAll('input, button, .dropdown-select-btn')).filter(e => e.getClientRects().length && e.getBoundingClientRect().right > r.right + 1).length }; })()")
                ok(m['lateral'] <= 0 and m['fora'] == 0, 'painel de gerar a ordem de embalagem a %d px, tema %s: nada passa da borda: %s' % (w, t, m))
                pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
                # 3. o detalhe da ordem
                ir(pg, OCD, '?id=15'); tema2(pg, t)
                pg.screenshot(path=_os.path.join(FOTOS, 'oc_detalhe_%d_%s.png' % (w, t)))
                lat = lateral2(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'detalhe da ordem com embalagem a %d px, tema %s: sem barra para o lado: %s' % (w, t, lat))
                # 4. a Entrada de Notas com a ordem escolhida e o aviso
                ir(pg, NOTA, '?oc=15'); tema2(pg, t)
                pg.evaluate("document.getElementById('campoOC').scrollIntoView({ block: 'start' })"); pg.wait_for_timeout(150)
                pg.screenshot(path=_os.path.join(FOTOS, 'nota_ordem_%d_%s.png' % (w, t)))
                lat = lateral2(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'Entrada de Notas com a ordem escolhida a %d px, tema %s: sem barra para o lado: %s' % (w, t, lat))
                preenche_nota(pg, '1', '123')
                pg.click('#btnSalvar'); pg.wait_for_timeout(450)
                pg.screenshot(path=_os.path.join(FOTOS, 'nota_aviso_%d_%s.png' % (w, t)))
                ok('2 embalagens entraram no saldo' in tx(pg, '#confirmModalTexto'), 'a foto do aviso mostra as embalagens que entraram (%d %s)' % (w, t))
                pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
                # 5. o inventario de embalagens aberto, e a contagem fechada
                ir(pg, INVT); tema2(pg, t)
                pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(300)
                pg.click('#modoInv [data-modo="embalagens"]'); pg.wait_for_timeout(200)
                pg.screenshot(path=_os.path.join(FOTOS, 'inv_gerar_%d_%s.png' % (w, t)))
                pg.click('#btnAbrirInventario'); pg.wait_for_timeout(350)
                pg.click('#btnAcaoInv'); pg.wait_for_timeout(200)
                for i, v in ((2, '80'), (5, '20'), (13, '7,5')):
                    pg.fill('[data-eid="%d"][data-campo="qtdeInvEmb"]' % i, v)
                pg.wait_for_timeout(150)
                pg.screenshot(path=_os.path.join(FOTOS, 'inv_aberto_%d_%s.png' % (w, t)))
                lat = lateral2(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'Inventário de embalagens aberto a %d px, tema %s: sem barra para o lado, nem na página nem na tabela: %s' % (w, t, lat))
                pg.click('#btnAcaoInv'); pg.wait_for_timeout(300)
                pg.screenshot(path=_os.path.join(FOTOS, 'inv_fechar_%d_%s.png' % (w, t)))
                m = pg.evaluate("(() => { const d = document.getElementById('fecharDrawer'), r = d.getBoundingClientRect(); return { lateral: d.scrollWidth - d.clientWidth, fora: Array.from(d.querySelectorAll('input, button')).filter(e => e.getClientRects().length && e.getBoundingClientRect().right > r.right + 1).length }; })()")
                ok(m['lateral'] <= 0 and m['fora'] == 0, 'painel de fechar o inventário de embalagens a %d px, tema %s: nada passa da borda: %s' % (w, t, m))
                pg.fill('#inputSenha', 'x'); pg.click('#btnConfirmarFechar'); pg.wait_for_timeout(500)
                # 6. a Movimentacao com a entrada pela nota e a contagem
                ir(pg, MOV, '?ver=embalagens&busca=EMB-002'); tema2(pg, t)
                pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)")); pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
                pg.set_viewport_size({'width': w, 'height': 1500}); pg.wait_for_timeout(200)
                pg.screenshot(path=_os.path.join(FOTOS, 'mov_contagem_%d_%s.png' % (w, t)))
                pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(150)
                rows = linhas_mov(pg)
                ok(any(r[1].startswith('Contagem física') for r in rows), 'a Movimentação de %d px, tema %s, mostra a contagem do inventário: %s' % (w, t, [r[1] for r in rows][-2:]))
                pg.fill('#buscaProduto', 'EMB-003'); pg.press('#buscaProduto', 'Enter'); pg.wait_for_timeout(150)
                pg.evaluate("document.getElementById('btnBuscar').click()"); pg.wait_for_timeout(250)
                pg.set_viewport_size({'width': w, 'height': 1500}); pg.wait_for_timeout(200)
                pg.screenshot(path=_os.path.join(FOTOS, 'mov_nota_%d_%s.png' % (w, t)))
                pg.set_viewport_size({'width': w, 'height': 900}); pg.wait_for_timeout(150)
                rows = linhas_mov(pg)
                ok(any(r[1].startswith('Entrada pela nota nº 123') for r in rows), 'e a de EMB-003 mostra "Entrada pela nota nº 123" (%d %s): %s' % (w, t, [r[1] for r in rows][-2:]))
                lat = lateral2(pg)
                ok(lat[0] <= 0 and lat[1] <= 0, 'Movimentação com a nota e a contagem a %d px, tema %s: sem barra para o lado: %s' % (w, t, lat))
                pg.context.close()
        print('  fotos em %s (%d arquivos)' % (FOTOS, len(_g.glob(_os.path.join(FOTOS, '*.png')))))


    # ================================================================ PACOTE 3 (23/nov/2026): os ajustes do teste das embalagens
    PROD_D = 'pagina-cadastros-produtos-detalhe.html'
    CLI_D = 'pagina-cadastros-clientes-detalhe.html'
    FOR_D = 'pagina-cadastros-fornecedores-detalhe.html'
    FORN7 = ['TechParts Distribuidora', 'Móveis Nordeste Ltda', 'Nordic Home Importação', 'Tecidos Ceará S/A', 'Embalagens do Vale', 'Papelaria Central', 'Luminárias Brasil']

    def nome_dos_itens(pg, sel):
        return pg.evaluate("(s) => Array.from(document.querySelectorAll(s)).map(e => e.textContent.trim())", sel)

    # ================================================================ 18. aviso de preco fora do normal
    if secao(18, 'Entrada de Notas: o preço muito acima do custo atual pede confirmação, em vermelho, com "Salvar mesmo assim"'):
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(100)
        pg.evaluate("Object.assign(ITENS[0], { sku: 'EMB-003', nome: 'x', qtd: 1, preco: 2304607.96 }); renderItens()")
        preenche_nota(pg, '1', '900', '5')
        pg.click('#btnSalvar'); pg.wait_for_timeout(400)
        aviso = 'Atenção: o preço de Caixa de Encomenda Flex G (R$ 2.304.607,96) está muito acima do custo atual (R$ 5,90).'
        ok(pg.evaluate("document.getElementById('confirmModal').classList.contains('open')") and tx(pg, '#confirmModalAviso') == aviso and vis(pg, 'confirmModalAviso'), 'o modal abre com a linha de aviso: "%s"' % tx(pg, '#confirmModalAviso'))
        ok(pg.evaluate("getComputedStyle(document.getElementById('confirmModalAviso')).color") in ('rgb(185, 28, 28)', 'rgb(252, 165, 165)'), 'e ela é vermelha (a cor dos valores de saída da casa)')
        ok(tx(pg, '#btnConfirmModalConfirmar') == 'Salvar mesmo assim' and notas(pg) == [] and sd(pg, 3) == 32 and ls(pg, 'deskMovEmbalagens') is None, 'o botão diz "Salvar mesmo assim", e até clicar nada é gravado (nem nota, nem saldo, nem movimento)')
        pg.click('#btnConfirmModalCancelar'); pg.wait_for_timeout(250)
        ok(notas(pg) == [] and sd(pg, 3) == 32, 'Cancelar não salva nada: o usuário volta e corrige o preço')
        pg.click('#btnSalvar'); pg.wait_for_timeout(400); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)
        ok(len(notas(pg)) == 1 and sd(pg, 3) == 33 and 'Nota salva' in tx(pg, '#confirmModalTexto') and not vis(pg, 'confirmModalAviso') and tx(pg, '#btnConfirmModalConfirmar') == 'Entendi',
           '"Salvar mesmo assim" salva a nota como sempre, e o aviso do resultado volta sem a linha vermelha')
        pg.context.close()
        # a regra: 10 vezes o custo, so embalagem, so com custo maior que zero
        pg = nova()
        ir(pg, NOTA)
        def avisos(sku, preco):
            return pg.evaluate("([s, p]) => { ITENS.splice(0, ITENS.length, { nome: 'x', sku: s, un: 'UN', qtd: 1, preco: p }); return avisosDePreco().length; }", [sku, preco])
        ok(avisos('EMB-003', 59) == 1 and avisos('EMB-003', 58.99) == 0 and avisos('EMB-003', 5.9) == 0 and avisos('EMB-003', 600) == 1, 'a fronteira é 10 vezes o custo (R$ 5,90): 59,00 avisa, 58,99 não')
        ok(avisos('emb-003', 590) == 1, 'o código digitado em minúscula também compara')
        ok(avisos('TEC-MEC-006', 99999) == 0 and avisos('', 99999) == 0 and avisos('EMB-099', 99999) == 0, 'produto, linha sem código e código que não existe não avisam (o aviso é da embalagem)')
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].custo = 0; embalagensGravar(L); }")
        ok(avisos('EMB-003', 99999) == 0, 'embalagem com custo 0 não tem com o que comparar: sem aviso')
        pg.evaluate("() => { const L = embalagensLer(); delete L.filter(e => e.id === 3)[0].custo; embalagensGravar(L); }")
        ok(avisos('EMB-003', 99999) == 0, 'e sem custo nenhum também')
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].custo = 5.9; embalagensGravar(L); }")
        pg.evaluate("ITENS.splice(0, ITENS.length, { nome: 'a', sku: 'EMB-003', un: 'UN', qtd: 1, preco: 700 }, { nome: 'b', sku: 'EMB-012', un: 'UN', qtd: 1, preco: 9 }, { nome: 'c', sku: 'EMB-005', un: 'UN', qtd: 1, preco: 6 })")
        ok(pg.evaluate("avisosDePreco().map(a => a.split(' (')[0])") == ['Atenção: o preço de Caixa de Encomenda Flex G', 'Atenção: o preço de Tag Desk Brands'], 'com várias linhas, uma linha de aviso por embalagem que passou do limite (a Flex G e a Tag; a CE-02 não)')
        pg.context.close()

    # ================================================================ 19. fornecedor padrao da embalagem
    if secao(19, 'Embalagens: "Fornecedor padrão" no cadastro (dropdown da casa, 7 fornecedores), as 14 de fábrica no Vale, e o nome na lista'):
        pg = nova()
        ir_cad(pg)
        ok(pg.evaluate("embalagensLer().length") == 14 and pg.evaluate("embalagensLer().every(e => e.fornecedor === 'Embalagens do Vale')"), 'as 14 embalagens de fábrica vêm com "Embalagens do Vale"')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#listaEmbalagens .embalagens-forn')).map(e => e.textContent)") == ['Fornecedor: Embalagens do Vale'] * 14, 'a lista mostra o fornecedor embaixo do nome, uma linha em cada uma das 14')
        ok(pg.evaluate("getComputedStyle(document.querySelector('.embalagens-forn')).fontSize") == '11.5px', 'em letra pequena (11,5 px)')
        abre_card(pg, 3)
        ok(tx(pg, '#campoFornecedorEmb label') == 'Fornecedor padrão' and tx(pg, '#inputFornecedorEmb .dropdown-select-label') == 'Embalagens do Vale', 'o painel tem o campo "Fornecedor padrão", com o fornecedor da Flex G')
        ok(pg.evaluate("document.querySelectorAll('#eventDrawer select').length") == 0 and nome_dos_itens(pg, '#inputFornecedorEmb .dropdown-select-item') == ['Sem fornecedor padrão'] + FORN7, 'é o dropdown da casa (não select nativo) com os 7 fornecedores do sistema e a opção de nenhum: %s' % nome_dos_itens(pg, '#inputFornecedorEmb .dropdown-select-item'))
        escolher(pg, '#inputFornecedorEmb', 'Papelaria Central')
        pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(emb(pg, 3)['fornecedor'] == 'Papelaria Central' and tx(pg, '#listaEmbalagens .embalagens-card[data-id="3"] .embalagens-forn') == 'Fornecedor: Papelaria Central', 'trocar o fornecedor e salvar grava na embalagem, e a lista mostra o novo')
        abre_card(pg, 3)
        ok(tx(pg, '#inputFornecedorEmb .dropdown-select-label') == 'Papelaria Central', 'e o painel reabre com ele')
        escolher(pg, '#inputFornecedorEmb', '')
        pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(emb(pg, 3)['fornecedor'] == '' and pg.evaluate("document.querySelectorAll('#listaEmbalagens .embalagens-card[data-id=\"3\"] .embalagens-forn').length") == 0, '"Sem fornecedor padrão" grava vazio, e a lista não mostra a linha')
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(tx(pg, '#inputFornecedorEmb .dropdown-select-label') == 'Sem fornecedor padrão', 'a embalagem nova abre sem fornecedor padrão')
        pg.fill('#inputNomeEmbalagem', 'Caixa Z'); escolher(pg, '#inputFornecedorEmb', 'Luminárias Brasil'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(emb(pg, 15)['fornecedor'] == 'Luminárias Brasil', 'a nova guarda o fornecedor escolhido: %s' % emb(pg, 15).get('fornecedor'))
        pg.context.close()
        # cadastro gravado antes do campo
        pg = nova()
        poe(pg, 'deskEmbalagens', [{'id': 5, 'nome': 'Caixa de Encomenda CE-02', 'tipo': 'pacote', 'cap': 12, 'custo': 6.3, 'status': 'ativo', 'saldo': 18, 'minimo': 20},
                                   {'id': 99, 'nome': 'Caixa do Fornecedor', 'tipo': 'pacote', 'cap': 3, 'custo': 2, 'status': 'ativo', 'saldo': 0, 'minimo': 0}])
        ir_cad(pg)
        ok(pg.evaluate("embalagensLer().map(e => [e.id, e.fornecedor])") == [[5, 'Embalagens do Vale'], [99, '']], 'o cadastro gravado sem o campo ganha o do padrão de mesmo id (Vale), e o que não existe no padrão fica sem fornecedor')
        pg.context.close()

    # ================================================================ 20. o painel da ordem so mostra os fornecedores dos itens marcados
    if secao(20, 'Necessidades de Compra: o dropdown de Fornecedor do painel da ordem mostra só os fornecedores dos itens marcados'):
        pg = nova()
        ir(pg, NC)
        pg.click('#corpoEmbalagens tr[data-id="3"] .item-checkbox'); pg.click('#corpoEmbalagens tr[data-id="12"] .item-checkbox')
        pg.click('#btnGerarEmb'); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == ['Embalagens do Vale'], 'ordem de embalagens, as duas do Vale: o dropdown só tem "Embalagens do Vale": %s' % nome_dos_itens(pg, '#ocForn0 .dropdown-select-item'))
        ok('só aparecem os fornecedores dos itens marcados' in tx(pg, '#drawerCorpo') and 'Ordem só de embalagens' in tx(pg, '#drawerCorpo'), 'o texto do painel diz que só aparecem os fornecedores dos itens marcados')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].fornecedor = 'Papelaria Central'; embalagensGravar(L); }")
        ir(pg, NC)
        pg.click('#corpoEmbalagens tr[data-id="3"] .item-checkbox'); pg.click('#corpoEmbalagens tr[data-id="12"] .item-checkbox')
        pg.click('#btnGerarEmb'); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == ['Embalagens do Vale', 'Papelaria Central'], 'itens de dois fornecedores (Papelaria Central e Vale): o dropdown mostra os dois, para o usuário escolher: %s' % nome_dos_itens(pg, '#ocForn0 .dropdown-select-item'))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].fornecedor = ''; embalagensGravar(L); }")
        ir(pg, NC)
        pg.click('#corpoEmbalagens tr[data-id="3"] .item-checkbox'); pg.click('#corpoEmbalagens tr[data-id="12"] .item-checkbox')
        pg.click('#btnGerarEmb'); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == FORN7, 'um item sem fornecedor padrão: não dá para restringir, o dropdown mostra todos os 7')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        # produtos: o fornecedor que o produto ja tem
        pg.evaluate("abrirOrdem(['CAD-ERG-001'])"); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == ['Móveis Nordeste Ltda'] and 'só aparecem os fornecedores dos itens marcados' in tx(pg, '#drawerCorpo'), 'ordem de produto: a Cadeira Ergonômica é da Móveis Nordeste, e só ela aparece (com a linha de explicação no painel)')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("abrirOrdem(['CAD-ERG-001', 'LUM-LED-004'])"); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == ['Móveis Nordeste Ltda', 'Luminárias Brasil'] and nome_dos_itens(pg, '#ocForn1 .dropdown-select-item') == ['Móveis Nordeste Ltda', 'Luminárias Brasil'], 'dois produtos de fornecedores diferentes: cada bloco oferece os dois')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("abrirOrdem(['CAD-ERG-001', 'CAM-DKB-011'])"); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == FORN7, 'um produto sem fornecedor (a Camiseta): o dropdown não fica restrito')
        pg.context.close()

    # ================================================================ 21. busca avancada da ordem
    if secao(21, 'Ordem de Compra: a busca avançada de itens mostra só o que é do fornecedor da ordem'):
        pg = nova()
        ir(pg, OCD, '?id=2')
        pg.click('#btnBuscaAvancada'); pg.wait_for_timeout(300)
        nomes = nome_dos_itens(pg, '#drawerCorpo .mov-tipo')
        ok(nomes == ['Teclado Mecânico Desk', 'Cabo HDMI 2.1 · 2m', 'Suporte Monitor Duplo', 'Fone Bluetooth Desk One', 'Mouse Sem Fio Compacto', 'Carregador USB-C 20W'] and 'Mostrando só os itens de TechParts Distribuidora' in tx(pg, '#drawerCorpo'),
           'na ordem da TechParts, a busca mostra só os 6 itens dela (e diz isso): %s' % nomes)
        ok('saldo' in tx(pg, '#drawerCorpo') and 'custo médio R$ 231,10' in tx(pg, '#drawerCorpo') and len(nome_dos_itens(pg, '#drawerCorpo [data-add]')) == 6, 'cada item segue com SKU, saldo, custo médio e o botão "Adicionar"')
        antes = pg.evaluate("ITENS.length")
        pg.click('#drawerCorpo [data-add]'); pg.wait_for_timeout(300)
        ok(pg.evaluate("ITENS.length") == antes + 1 and pg.evaluate("ITENS[ITENS.length - 1].sku") == 'TEC-MEC-006', '"Adicionar" continua colocando o item na ordem')
        escolher(pg, '#inputFornecedor', 6)
        pg.click('#btnBuscaAvancada'); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#drawerCorpo .mov-tipo') == ['Caderno Universitário 200 folhas', 'Caneta Esferográfica Caixa c/50'] and 'Papelaria Central' in tx(pg, '#drawerCorpo'), 'trocando o fornecedor da ordem para a Papelaria Central, a busca passa a mostrar os dois itens dela')
        pg.click('#drawerClose'); pg.wait_for_timeout(300)
        escolher(pg, '#inputFornecedor', 4)
        pg.click('#btnBuscaAvancada'); pg.wait_for_timeout(300)
        ok(nome_dos_itens(pg, '#drawerCorpo .mov-tipo') == ['Tecido Algodão (metro)'], 'e na Tecidos Ceará, só o tecido')
        pg.context.close()
        pg = nova()
        ir(pg, OCD, '?novo=1')
        pg.click('#btnBuscaAvancada'); pg.wait_for_timeout(300)
        ok(len(nome_dos_itens(pg, '#drawerCorpo [data-add]')) == 12 and 'Mostrando só' not in tx(pg, '#drawerCorpo'), 'ordem nova, sem fornecedor escolhido: a busca mostra o catálogo inteiro (12 itens), sem restringir')
        pg.context.close()
        ok('Busca avançada' not in fonte(NOTA), 'a Entrada de Notas não tem busca avançada: o filtro por fornecedor dela é o da sugestão ao digitar (seção 22)')

    # ================================================================ 22. sugestao ao digitar o item
    if secao(22, 'Sugestão ao digitar o item (Ordem de Compra e Entrada de Notas): nome, SKU ou GTIN, até 8, do fornecedor, clicar ou Enter preenche'):
        pg = nova()
        ir(pg, OCD, '?id=2')
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        campo = '#corpoItens tr:last-child input[data-campo="nome"]'
        pg.fill(campo, 'mou'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('sugestoesItem').classList.contains('open')") and nome_dos_itens(pg, '#sugestoesItem .sugestao-nome') == ['Mouse Sem Fio Compacto'], 'digitar "mou" abre a lista com o Mouse')
        ok(tx(pg, '#sugestoesItem .sugestao-meta') == 'ELE-1003 · 7891234000301 · custo médio R$ 37,20' and pg.evaluate("document.querySelector('#sugestoesItem .sugestao-item').classList.contains('ativo')"), 'cada linha: nome e, na meta, "SKU · GTIN · custo médio R$ X"; a primeira vem marcada')
        pos = pg.evaluate("(() => { const i = document.querySelector('#corpoItens tr:last-child input[data-campo=\"nome\"]').getBoundingClientRect(), s = document.getElementById('sugestoesItem').getBoundingClientRect(); return [Math.round(s.top - i.bottom), Math.round(s.left - i.left)]; })()")
        ok(0 <= pos[0] <= 12 and abs(pos[1]) <= 2, 'a lista abre embaixo do próprio campo: %s' % pos)
        pg.fill(campo, 'cane'); pg.wait_for_timeout(150)
        ok(tx(pg, '#sugestoesItem .sugestao-vazia') == 'Nenhum item encontrado para este fornecedor.', '"cane" na ordem da TechParts: nada (a caneta é da Papelaria), e a lista diz isso')
        escolher(pg, '#inputFornecedor', 6)
        pg.fill(campo, 'cane'); pg.wait_for_timeout(150)
        ok(nome_dos_itens(pg, '#sugestoesItem .sugestao-nome') == ['Caneta Esferográfica Caixa c/50'], 'trocado o fornecedor para a Papelaria Central, "cane" acha a Caneta')
        pg.fill(campo, 'pap-30'); pg.wait_for_timeout(120)
        a = nome_dos_itens(pg, '#sugestoesItem .sugestao-nome')
        pg.fill(campo, '7891234000305'); pg.wait_for_timeout(120)
        ok(len(a) == 2 and nome_dos_itens(pg, '#sugestoesItem .sugestao-nome') == ['Caneta Esferográfica Caixa c/50'], 'a busca é por nome, SKU (pap-30 acha os dois) ou GTIN (o da caneta acha só ela)')
        pg.press(campo, 'Enter'); pg.wait_for_timeout(250)
        it = pg.evaluate("ITENS[ITENS.length - 1]")
        ok(it['nome'] == 'Caneta Esferográfica Caixa c/50' and it['sku'] == 'PAP-3003' and it['gtin'] == '7891234000305' and abs(it['preco'] - 18) < 0.001 and not pg.evaluate("document.getElementById('sugestoesItem').classList.contains('open')"),
           'Enter preenche a linha: nome, SKU, GTIN e o preço (o custo médio), e a lista fecha: %s' % it)
        ok(pg.evaluate("document.activeElement.getAttribute('data-campo')") == 'qtd', 'e o cursor vai para a quantidade')
        # setas, clique, Escape, clique fora
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill(campo, 'pap-30'); pg.wait_for_timeout(120)
        pg.press(campo, 'ArrowDown'); pg.press(campo, 'Enter'); pg.wait_for_timeout(250)
        ok(pg.evaluate("ITENS[ITENS.length - 1].sku") == 'PAP-3003', 'a seta para baixo move a marca e o Enter pega o segundo')
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill(campo, 'pap-30'); pg.wait_for_timeout(120)
        pg.click('#sugestoesItem .sugestao-item:first-child'); pg.wait_for_timeout(250)
        ok(pg.evaluate("ITENS[ITENS.length - 1].sku") == 'PAP-3001', 'clicar na sugestão também preenche')
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill(campo, 'pap'); pg.wait_for_timeout(120)
        pg.press(campo, 'Escape'); pg.wait_for_timeout(120)
        ok(not pg.evaluate("document.getElementById('sugestoesItem').classList.contains('open')") and pg.evaluate("ITENS[ITENS.length - 1].nome") == 'pap', 'Escape fecha a lista sem preencher')
        pg.fill(campo, 'pap'); pg.wait_for_timeout(120)
        pg.click('#totProdutos'); pg.wait_for_timeout(120)
        ok(not pg.evaluate("document.getElementById('sugestoesItem').classList.contains('open')"), 'clicar fora fecha')
        pg.fill(campo, 'pap'); pg.wait_for_timeout(120); pg.fill(campo, ''); pg.wait_for_timeout(120)
        ok(not pg.evaluate("document.getElementById('sugestoesItem').classList.contains('open')"), 'apagar o texto fecha')
        pg.context.close()
        # no maximo 8
        pg = nova()
        ir(pg, OCD, '?novo=1')
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill(campo, 'a'); pg.wait_for_timeout(150)
        ok(len(nome_dos_itens(pg, '#sugestoesItem .sugestao-item')) == 8, 'sem fornecedor escolhido a lista mostra de todos, e para em 8: %d' % len(nome_dos_itens(pg, '#sugestoesItem .sugestao-item')))
        pg.context.close()
        # a Entrada de Notas
        pg = nova()
        ir(pg, NOTA)
        pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
        pg.fill(campo, 'flex'); pg.wait_for_timeout(150)
        ok(nome_dos_itens(pg, '#sugestoesItem .sugestao-nome') == ['Caixa de Encomenda Flex P', 'Caixa de Encomenda Flex M', 'Caixa de Encomenda Flex G'] and tx(pg, '#sugestoesItem .sugestao-meta') == 'EMB-001 · custo médio R$ 3,50',
           'na nota, "flex" acha as embalagens (código no lugar do SKU, o custo atual): %s' % tx(pg, '#sugestoesItem .sugestao-meta'))
        escolher(pg, '#inputFornecedor', 1)
        pg.fill(campo, 'flex'); pg.wait_for_timeout(150)
        ok(tx(pg, '#sugestoesItem .sugestao-vazia') == 'Nenhum item encontrado para este fornecedor.', 'com a TechParts escolhida na nota, as embalagens (do Vale) não aparecem')
        pg.fill(campo, 'tec'); pg.wait_for_timeout(150)
        ok(nome_dos_itens(pg, '#sugestoesItem .sugestao-nome') == ['Teclado Mecânico Desk'], 'e os produtos da TechParts aparecem')
        escolher(pg, '#inputFornecedor', 5)
        pg.fill(campo, 'flex'); pg.wait_for_timeout(150)
        pg.press(campo, 'ArrowDown'); pg.press(campo, 'ArrowDown'); pg.press(campo, 'Enter'); pg.wait_for_timeout(250)
        it = pg.evaluate("ITENS[0]")
        ok(it['sku'] == 'EMB-003' and it['nome'] == 'Caixa de Encomenda Flex G' and abs(it['preco'] - 5.9) < 0.001 and pg.evaluate("document.querySelector('#corpoItens input[data-campo=\"sku\"]').value") == 'EMB-003', 'com o Vale escolhido, duas setas e Enter pegam a Flex G: nome, código e o preço (o custo): %s' % it)
        pg.fill(campo, 'cane'); pg.wait_for_timeout(120); pg.press(campo, 'Escape')
        pg.context.close()

    # ================================================================ 23. Enter no Inventario
    if secao(23, 'Inventário: o Enter no campo "Qtde inventário" vai ao próximo; vazio não pula e avisa em vermelho'):
        pg = nova()
        ir(pg, INVT)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(300)
        pg.click('#modoInv [data-modo="embalagens"]'); pg.wait_for_timeout(200)
        pg.click('#btnAbrirInventario'); pg.wait_for_timeout(350)
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(250)
        campos = '[data-campo="qtdeInvEmb"]'
        ids = pg.evaluate("Array.from(document.querySelectorAll('%s')).map(c => c.getAttribute('data-eid'))" % campos)
        ok(len(ids) == 13, 'o inventário de embalagens tem 13 campos de contagem')
        pg.focus('[data-eid="%s"]%s' % (ids[0], campos)); pg.keyboard.type('10'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.activeElement.getAttribute('data-eid')") == ids[1], 'campo preenchido: o Enter leva ao próximo campo da coluna')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
        ok(pg.evaluate("document.activeElement.getAttribute('data-eid')") == ids[1], 'campo vazio: o Enter NÃO pula')
        ok(tx(pg, '[data-eid="%s"]%s ~ .inv-aviso-contagem' % (ids[1], campos)) == 'Informe a quantidade para seguir.' and pg.evaluate("getComputedStyle(document.querySelector('.inv-aviso-contagem')).color") in ('rgb(185, 28, 28)', 'rgb(252, 165, 165)'), 'e aparece, em vermelho, logo abaixo do campo e dentro da mesma célula: "Informe a quantidade para seguir."')
        ok(pg.evaluate("document.querySelector('[data-eid=\"%s\"]%s').classList.contains('has-error')" % (ids[1], campos)) and pg.evaluate("getComputedStyle(document.querySelector('[data-eid=\"%s\"]%s')).borderColor" % (ids[1], campos)) in ('rgb(220, 38, 38)', 'rgb(239, 68, 68)'), 'o campo ganha a borda vermelha')
        ok(pg.evaluate("INV.linhas.filter(l => l.eid === %s)[0].contado" % ids[1]) is None, 'é um empurrão e não uma trava: a linha continua "não contada" (o saldo dela não muda no fechamento)')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 1, 'Enter de novo não empilha a mensagem')
        pg.keyboard.type('5'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 0 and not pg.evaluate("document.querySelector('[data-eid=\"%s\"]%s').classList.contains('has-error')" % (ids[1], campos)), 'a mensagem e a borda somem quando o campo recebe valor')
        pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.activeElement.getAttribute('data-eid')") == ids[2], 'com valor, o Enter segue')
        pg.keyboard.type('0'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.activeElement.getAttribute('data-eid')") == ids[3] and pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 0, 'o zero é valor: não avisa e segue')
        pg.focus('[data-eid="%s"]%s' % (ids[-1], campos)); pg.keyboard.type('3'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.activeElement.getAttribute('data-eid')") == ids[-1] and pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 0, 'no último campo, preenchido, o Enter não faz nada e não avisa')
        pg.context.close()
        # produtos
        pg = nova()
        ir(pg, INVT)
        pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(300)
        escolher(pg, '#menuDeposito', 2)
        pg.click('#btnAbrirInventario'); pg.wait_for_timeout(450)
        pg.click('#btnAcaoInv'); pg.wait_for_timeout(250)
        campos = '[data-campo="qtdeInv"]'
        pids = pg.evaluate("Array.from(document.querySelectorAll('%s')).map(c => c.getAttribute('data-pid'))" % campos)
        ok(len(pids) >= 3, 'o inventário de produtos tem campos de contagem (%d)' % len(pids))
        pg.focus('[data-pid="%s"]%s' % (pids[0], campos)); pg.keyboard.press('Enter'); pg.wait_for_timeout(120)
        ok(pg.evaluate("document.activeElement.getAttribute('data-pid')") == pids[0] and tx(pg, '.inv-aviso-contagem') == 'Informe a quantidade para seguir.', 'em produtos também: vazio não pula e avisa')
        pg.keyboard.type('4'); pg.keyboard.press('Enter'); pg.wait_for_timeout(100)
        ok(pg.evaluate("document.activeElement.getAttribute('data-pid')") == pids[1] and pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 0, 'com valor, segue para o próximo produto, e a mensagem some')
        pg.context.close()

    # ================================================================ 24. botao Gerar o codigo
    if secao(24, 'Botão "Gerar" o código no padrão: Embalagens, Produtos, Clientes e Fornecedores'):
        pg = nova()
        ir_cad(pg)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        ok(vis(pg, 'btnGerarCodigoEmb') and tx(pg, '#btnGerarCodigoEmb') == 'Gerar' and tx(pg, '#codigoEmbalagem') == 'EMB-015', 'embalagem nova: o botão "Gerar" está ao lado do código (só leitura)')
        pg.fill('#inputNomeEmbalagem', 'Caixa A'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('codigoEmbalagem').textContent = '—'")
        pg.click('#btnGerarCodigoEmb'); pg.wait_for_timeout(100)
        ok(tx(pg, '#codigoEmbalagem') == 'EMB-016', '"Gerar" preenche o próximo código livre (EMB-016, com a EMB-015 já criada): %s' % tx(pg, '#codigoEmbalagem'))
        ok(pg.evaluate("document.getElementById('codigoEmbalagem').matches('input, textarea, select')") is False, 'e o campo segue só de leitura')
        pg.fill('#inputNomeEmbalagem', 'Caixa B'); pg.click('#btnSalvarEmbalagem'); pg.wait_for_timeout(300)
        ok(emb(pg, 16)['codigo'] == 'EMB-016', 'a embalagem grava o código gerado')
        abre_card(pg, 3)
        ok(not vis(pg, 'btnGerarCodigoEmb'), 'no painel de uma embalagem que já existe o botão não aparece (o código dela não muda)')
        pg.context.close()
        # SKU do produto
        pg = nova()
        ir(pg, PROD_D, '?novo=1')
        ok(vis(pg, 'btnGerarSku') and tx(pg, '#btnGerarSku') == 'Gerar' and pg.evaluate("getComputedStyle(document.getElementById('btnGerarSku')).fontSize") == '12px', 'produto novo: o botão "Gerar" está ao lado do SKU, pequeno (12 px)')
        ok(pg.evaluate("document.getElementById('btnGerarSku').classList.contains('btn-secundario')"), 'é o botão secundário da casa')
        pg.click('#btnGerarSku'); pg.wait_for_timeout(100)
        ok(pg.input_value('#inputSku') == 'PRO-1001', 'sem categoria escolhida, o prefixo é PRO: %s' % pg.input_value('#inputSku'))
        escolher(pg, '#inputLojaDesk', 'Desk Shope')
        pg.evaluate("porNoDropdown('inputCategoria', 'Eletrônicos')"); pg.wait_for_timeout(100)
        pg.click('#btnGerarSku'); pg.wait_for_timeout(100)
        ok(pg.input_value('#inputSku') == 'ELE-1005', 'categoria Eletrônicos (ELE-1001 a ELE-1004 já existem): ELE-1005 (%s)' % pg.input_value('#inputSku'))
        pg.fill('#inputSku', 'MEU-SKU'); pg.wait_for_timeout(50)
        ok(pg.input_value('#inputSku') == 'MEU-SKU', 'o SKU continua editável depois de gerado')
        r = pg.evaluate("[proximoSku('Eletrônicos'), proximoSku('Mobiliário e Decoração'), proximoSku('Vestuário e Acessórios'), proximoSku('Papelaria'), proximoSku('Materiais'), proximoSku('Água e Gás'), proximoSku(''), proximoSku(undefined), prefixoDoSku('Mobiliário'), prefixoDoSku('Vestuário')]")
        ok(r == ['ELE-1005', 'MOB-4004', 'VES-2005', 'PAP-3004', 'MAT-1001', 'AGU-1001', 'PRO-1001', 'PRO-1001', 'MOB', 'VES'], 'prefixo = 3 letras maiúsculas sem acento; a sequência é a menor livre a partir da menor já usada no prefixo (1001 se não há nenhuma); categoria fora da lista usa as 3 primeiras letras: %s' % r)
        pg.goto(localiza.uri(PROD_D)); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(not vis(pg, 'btnGerarSku') and 'ELE-1001' in tx(pg, '.main'), 'no produto aberto em modo leitura o botão não aparece, e o SKU continua visível')
        pg.context.close()
        # Clientes e Fornecedores
        for tela, pre, esperado, existente in ((CLI_D, 'CLI', 'CLI-0015', 'CLI-0003'), (FOR_D, 'FOR', 'FOR-0015', 'FOR-0002')):
            pg = nova()
            ir(pg, tela, '?novo=1')
            ok(vis(pg, 'btnGerarCodigo') and tx(pg, '#btnGerarCodigo') == 'Gerar' and pg.input_value('#inputCodigo') == '' and pg.evaluate("document.getElementById('inputCodigo').readOnly"), '%s novo: o código abre vazio e só de leitura, com o botão "Gerar" ao lado' % pre)
            pg.click('#btnGerarCodigo'); pg.wait_for_timeout(100)
            ok(pg.input_value('#inputCodigo') == esperado and pg.evaluate("document.getElementById('inputCodigo').readOnly"), '"Gerar" preenche o próximo livre, %s (os 14 do exemplo vão até o 0014): %s' % (esperado, pg.input_value('#inputCodigo')))
            pg.goto(localiza.uri(tela)); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            ok(not vis(pg, 'btnGerarCodigo') and existente in tx(pg, '.main'), '%s já existente: o botão não aparece e o código segue (%s)' % (pre, existente))
            pg.context.close()


    # ================================================================ 25. fotos do pacote 3
    if secao(25, 'Fotos do pacote 3 nos dois temas, a 1280 e a 1440, sem barra de rolagem para o lado'):
        def tema3(pg, t):
            pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", t); pg.wait_for_timeout(300)

        def lateral3(pg):
            return pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")

        def foto(pg, nome, w, t):
            pg.screenshot(path=_os.path.join(FOTOS, '%s_%d_%s.png' % (nome, w, t)))

        for w in (1280, 1440):
            for t in ('light', 'dark'):
                # 1. a Movimentacao: a tela e a folha (703 px = A4 com 12 mm de margem)
                pg = nova(w, 900)
                ir(pg, MOV); tema3(pg, t)
                pg.fill('#buscaProduto', 'TEC-MEC-006'); pg.press('#buscaProduto', 'Enter')
                pg.fill('#dataDe', pg.evaluate("fmtData(PRIMEIRO_DIA)")); pg.click('#btnBuscar'); pg.wait_for_timeout(300)
                foto(pg, 'mov_tela', w, t)
                ok(lateral3(pg) <= 0, 'Movimentação a %d px, tema %s: sem barra para o lado' % (w, t))
                pg.set_viewport_size({'width': 703, 'height': 1000})
                pg.evaluate("window.dispatchEvent(new Event('beforeprint'))"); pg.emulate_media(media='print'); pg.wait_for_timeout(250)
                pg.screenshot(path=_os.path.join(FOTOS, 'mov_folha_%d_%s.png' % (w, t)), full_page=True)
                m = pg.evaluate("(() => [document.documentElement.scrollWidth, innerWidth, Math.round(document.querySelector('.main table').getBoundingClientRect().right)])()")
                ok(m[0] <= m[1] and m[2] <= m[1], 'a folha da Movimentação (tema %s, aberta a %d px): a tabela termina em %d de %d, nada fora da folha' % (t, w, m[2], m[1]))
                pg.context.close()
                # 2. a sugestao no campo de item da Ordem de Compra
                pg = nova(w, 900)
                ir(pg, OCD, '?id=2'); tema3(pg, t)
                pg.click('#btnAdicionarItem'); pg.wait_for_timeout(150)
                pg.fill('#corpoItens tr:last-child input[data-campo="nome"]', 'ca'); pg.wait_for_timeout(200)
                foto(pg, 'oc_sugestao', w, t)
                r = pg.evaluate("(() => { const s = document.getElementById('sugestoesItem').getBoundingClientRect(); return [Math.round(s.right), Math.round(s.bottom), innerWidth, innerHeight]; })()")
                ok(r[0] <= r[2] and r[1] <= r[3] and lateral3(pg) <= 0, 'lista de sugestões da Ordem de Compra a %d px, tema %s: cabe na janela: %s' % (w, t, r))
                pg.context.close()
                # 3. o painel da ordem, com o dropdown de fornecedor aberto e filtrado; e o bloco das ja pedidas
                pg = nova(w, 900)
                ir(pg, NC)
                pg.evaluate("() => { const L = embalagensLer(); L.filter(e => e.id === 3)[0].fornecedor = 'Papelaria Central'; embalagensGravar(L); }")
                ir(pg, NC); tema3(pg, t)
                pg.evaluate("document.getElementById('painelEmbalagens').scrollIntoView({ block: 'start' })"); pg.wait_for_timeout(150)
                pg.click('#corpoEmbalagens tr[data-id="3"] .item-checkbox'); pg.click('#corpoEmbalagens tr[data-id="12"] .item-checkbox')
                pg.click('#btnGerarEmb'); pg.wait_for_timeout(350)
                pg.click('#ocForn0 .dropdown-select-btn'); pg.wait_for_timeout(200)
                foto(pg, 'nc_fornecedor', w, t)
                m = pg.evaluate("(() => { const d = document.getElementById('eventDrawer'), r = d.getBoundingClientRect(); return { lateral: d.scrollWidth - d.clientWidth, fora: Array.from(d.querySelectorAll('input, button, .dropdown-select-btn')).filter(e => e.getClientRects().length && e.getBoundingClientRect().right > r.right + 1).length }; })()")
                ok(m['lateral'] <= 0 and m['fora'] == 0 and nome_dos_itens(pg, '#ocForn0 .dropdown-select-item') == ['Embalagens do Vale', 'Papelaria Central'], 'painel da ordem a %d px, tema %s: dropdown só com os dois fornecedores dos itens marcados, nada passa da borda: %s' % (w, t, m))
                poe(pg, 'deskOrdensGeradas', [ordem_emb(15, [(3, 8, 5.9, 0)])])
                ir(pg, NC); tema3(pg, t)
                pg.evaluate("document.getElementById('painelEmbalagens').scrollIntoView({ block: 'start' })"); pg.wait_for_timeout(150)
                foto(pg, 'nc_pedidas', w, t)
                ok(vis(pg, 'embPedidas') and lateral3(pg) <= 0, 'Necessidades de Compra a %d px, tema %s: o bloco "já pedidas" aparece acima da tabela, sem barra para o lado' % (w, t))
                pg.context.close()
                # 4. o painel da embalagem
                pg = nova(w, 900)
                ir_cad(pg); tema3(pg, t)
                pg.click('#btnNovaEmbalagem'); pg.wait_for_timeout(350)
                foto(pg, 'emb_painel_codigo', w, t)
                m = pg.evaluate("(() => { const d = document.getElementById('eventDrawer'), r = d.getBoundingClientRect(); const b = document.getElementById('btnGerarCodigoEmb').getBoundingClientRect(); return { lateral: d.scrollWidth - d.clientWidth, fora: Array.from(d.querySelectorAll('input, .dropdown-select-btn, .saldo-leitura, button')).filter(e => e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().right > r.right - 12).length, botao: Math.round(b.height) }; })()")
                ok(m['lateral'] <= 0 and m['fora'] == 0 and m['botao'] < 40, 'painel da embalagem nova a %d px, tema %s: o código e o botão "Gerar" na mesma linha, nada passa da borda: %s' % (w, t, m))
                pg.evaluate("document.getElementById('campoFornecedorEmb').scrollIntoView({ block: 'center' })"); pg.wait_for_timeout(150)
                foto(pg, 'emb_painel_fornecedor', w, t)
                pg.evaluate("document.querySelector('#inputFornecedorEmb .dropdown-select-btn').click()"); pg.wait_for_timeout(200)
                foto(pg, 'emb_painel_fornecedor_aberto', w, t)
                pg.context.close()
                # 5. o inventario com a mensagem em vermelho
                pg = nova(w, 900)
                ir(pg, INVT); tema3(pg, t)
                pg.click('[data-caminho="gerar"]'); pg.wait_for_timeout(300)
                pg.click('#modoInv [data-modo="embalagens"]'); pg.wait_for_timeout(200)
                pg.click('#btnAbrirInventario'); pg.wait_for_timeout(350)
                pg.click('#btnAcaoInv'); pg.wait_for_timeout(250)
                ids = pg.evaluate("Array.from(document.querySelectorAll('[data-campo=\"qtdeInvEmb\"]')).map(c => c.getAttribute('data-eid'))")
                pg.focus('[data-eid="%s"][data-campo="qtdeInvEmb"]' % ids[0]); pg.keyboard.type('10'); pg.keyboard.press('Enter'); pg.keyboard.press('Enter'); pg.wait_for_timeout(150)
                foto(pg, 'inv_enter', w, t)
                lat = pg.evaluate("[document.documentElement.scrollWidth - document.documentElement.clientWidth, Math.max.apply(null, [0].concat(Array.from(document.querySelectorAll('.estoque-table-wrap')).filter(x => x.getClientRects().length).map(x => x.scrollWidth - x.clientWidth)))]")
                ok(lat[0] <= 0 and lat[1] <= 0 and vis(pg, 'btnAcaoInv') and pg.evaluate("document.querySelectorAll('.inv-aviso-contagem').length") == 1, 'Inventário a %d px, tema %s, com a mensagem em vermelho: sem barra para o lado, na página nem na tabela: %s' % (w, t, lat))
                pg.context.close()
                # 6. o modal da nota com o aviso de preco
                pg = nova(w, 900)
                ir(pg, NOTA); tema3(pg, t)
                pg.click('#btnAdicionarItem'); pg.wait_for_timeout(100)
                pg.evaluate("Object.assign(ITENS[0], { sku: 'EMB-003', nome: 'x', qtd: 1, preco: 2304607.96 }); renderItens()")
                preenche_nota(pg, '1', '900', '5')
                pg.click('#btnSalvar'); pg.wait_for_timeout(500)
                foto(pg, 'nota_aviso_preco', w, t)
                r = pg.evaluate("(() => { const m = document.getElementById('confirmModal').getBoundingClientRect(), a = document.getElementById('confirmModalAviso').getBoundingClientRect(), b = document.getElementById('btnConfirmModalConfirmar').getBoundingClientRect(); return [Math.round(a.right) <= Math.round(m.right), Math.round(b.bottom) <= innerHeight, Math.round(a.height)]; })()")
                ok(r[0] and r[1] and r[2] > 0 and lateral3(pg) <= 0, 'modal da nota com o aviso de preço a %d px, tema %s: a linha vermelha e o botão cabem na janela: %s' % (w, t, r))
                pg.context.close()
        print('  fotos em %s (%d arquivos)' % (FOTOS, len(_g.glob(_os.path.join(FOTOS, '*.png')))))

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print((' - ' + f).encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8'))
raise SystemExit(1 if falhas else 0)
