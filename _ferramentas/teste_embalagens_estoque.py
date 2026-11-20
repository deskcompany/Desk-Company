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
        ok(emb(pg, 3)['saldo'] == 33 and m['qtd'] == 3 and m['prejuizo'] == 0, 'e a contagem física que dá sobra não é prejuízo')
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
        ok(d.value.suggested_filename.startswith('movimentacao-emb-002-') and len(csv) == 9 and csv[0] == '"Data";"Hora";"Movimento";"Observação";"Registrado por";"Cliente ou fornecedor";"Saldo anterior";"Quantidade";"Saldo atual";"Valor unitário";"Custo médio";"Valor em estoque";"Prejuízo"',
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
        ok(len(com) == 14 and all(b == blocos[0] for b in blocos), 'o bloco EMBALAGENS: LEITURA é idêntico nas 14 cópias (as 13 de antes e a Movimentação de Estoque): %d, diferentes: %s' % (len(com), [n for n, b in zip(nomes, blocos) if b != blocos[0]]))
        ok(MOV in nomes and CONF_F in nomes and CAD in nomes, 'e as três telas do pacote (Embalagens, Conferência de Saída e Movimentação) estão entre elas')
        b0 = blocos[0]
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

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print((' - ' + f).encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8'))
raise SystemExit(1 if falhas else 0)
