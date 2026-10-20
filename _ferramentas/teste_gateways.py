# -*- coding: utf-8 -*-
# Gateways de Pagamento, entrega 1: a lista, a pagina do gateway, o menu e a conta financeira (barganha aprovada pelo usuario em 20/out/2026).
#
# Decisoes dele (nao se reabrem): (1) o gateway e DONO das taxas e dos prazos dos cartoes (tabela "Condicoes comerciais"); ligar Formas de Recebimento e o PDV
# a ele e a entrega 2. (2) Gateways: InfinityPay e Outro, sem Pagar.me. (3) Cada gateway tem "Vale para", as lojas em que vale. (4) A conta financeira do
# gateway nasce sozinha ao salvar, com a descricao dele, e aparece em Configuracoes > Contas financeiras.
#
#   [1] A lista: colunas, filtro de situacao (Habilitados de fabrica), busca, vazio e limpar filtros, abrir, ordem, incluir;
#   [2] A pagina por tipo: o que aparece e some, a descricao que nasce com o tipo, dia para debito, os blocos de InfinityPay e de Outro;
#   [3] A tabela de condicoes: gerada por bandeira, tirar a bandeira (e o aviso da editada), adicionar, repetida recusada, validacoes, "a partir da";
#   [4] A chave da API: mascarada, nunca inteira (tela, impressao, planilha, registro), trocar, testar conexao, o link de conciliacao;
#   [5] Gravar e recarregar, sair com alteracao pendente, excluir, as confirmacoes de senha e o registro de atividades;
#   [6] A conta financeira: nasce, renomeia, acompanha a situacao e some ao excluir, e as outras telas seguem na lista fixa;
#   [7] O menu, o bloco comum, o catalogo e os espelhos (lojas, categorias, contas), o exemplo que o gravado vence, a barra de rolagem e os dois temas.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys, json, re, csv, io
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LISTA, DET = 'pagina-integracoes-gateways.html', 'pagina-integracoes-gateways-detalhe.html'
CONTAS, CATS, LOJAS_CAD = 'pagina-configuracoes-contas-financeiras.html', 'pagina-configuracoes-categorias-financeiras.html', 'pagina-cadastros-lojas-desk.html'
SENHAS, REGISTRO, VALE = 'pagina-configuracoes-confirmacoes-senha.html', 'pagina-configuracoes-registro-atividades.html', 'pagina-financas-vale-compra.html'
CHAVES_LOCAIS = ['deskGateways', 'deskGatewaysExemplo', 'deskParametros', 'deskLog']
CHAVE_API = 'ipay_live_8f3a1c9e72b4d605'   # a do primeiro exemplo: nunca pode aparecer inteira na tela
CHAVE_NOVA = 'ipay_live_Zq81mTe5Kd02vXa9'
MASCARA = '••••'
TAXAS = [3, 3.6, 4.25, 4.9, 5.5, 6.15, 6.8, 7.45, 8, 8.7, 9.35, 10]

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


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


MEDE = """() => { const r = []; document.querySelectorAll('.estoque-table-wrap, .table-wrap').forEach(w => {
  if (w.getClientRects().length && w.scrollWidth > w.clientWidth + 1) r.push((w.id || w.className) + ' ' + w.scrollWidth + '>' + w.clientWidth); });
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) r.push('a pagina rola'); return r; }"""

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 900}, accept_downloads=True)
    try:
        ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    except Exception:
        pass
    pg = ctx.new_page()
    pg.set_default_timeout(8000)   # defeito que some com um elemento vira falha em segundos, e nao espera meio minuto
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('console', lambda m: erros.append('console: ' + m.text[:160]) if m.type == 'error' else None)

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.getClientRects().length > 0 && getComputedStyle(e).display !== 'none'; }", sel)

    def txt(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.trim() : null; }", sel)

    def limpar(**params):
        """Zera o armazenamento: o exemplo de fabrica (tres gateways) nasce na proxima abertura. O Registro de atividades tambem."""
        if pg.url == 'about:blank':
            ir(LISTA)
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        param(**params)

    def param(**params):
        d = dict(aoSalvar='ficar')   # ficar na pagina depois de salvar, para o teste olhar o que ficou na tela
        d.update(params)
        pg.evaluate("(d) => localStorage.setItem('deskParametros', JSON.stringify(d))", d)

    def gws():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskGateways') || '{}').gateways || [])")

    def gw(i):
        return [g for g in gws() if g['id'] == i][0]

    def log():
        return pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")

    def modal():
        return pg.evaluate("document.getElementById('confirmModal').classList.contains('open') ? document.getElementById('confirmModalTexto').textContent : ''")

    def confirmar():
        """Confirma o painel aberto, com a senha quando ele pede, e espera o resultado."""
        if pg.evaluate("(() => { const r = document.getElementById('campoSenhaModal'); return !!r && r.classList.contains('on'); })()"):
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)

    def cancelar_modal():
        clic('#btnConfirmModalCancelar'); pg.wait_for_timeout(250)

    def escolher(id_, valor):
        clic("#%s .dropdown-select-item[data-value='%s']" % (id_, valor)); pg.wait_for_timeout(120)

    def marcar(menu, valor):
        clic("#%s input[value='%s']" % (menu, valor)); pg.wait_for_timeout(120)

    def todas_bandeiras():
        clic('#menuGwBandeiras [data-todas]'); pg.wait_for_timeout(150)

    def novo(tipo='outro', descricao=None, lojas=('1',)):
        """Abre o cadastro em branco e preenche o minimo para salvar."""
        ir(DET, '?novo=1')
        escolher('gwTipo', tipo)
        if descricao is not None:
            pg.fill('#gwDescricao', descricao)
        for l in lojas:
            marcar('menuGwLojas', l)
        if tipo == 'outro':
            escolher('gwCategoriaTarifa', '17')
        else:
            escolher('gwCategoria', '1'); escolher('gwContaCredito', '2'); pg.fill('#gwChave', CHAVE_NOVA)

    def salvar():
        clic('#btnSalvarGw'); pg.wait_for_timeout(400)
        if modal():
            confirmar()
        pg.wait_for_timeout(200)

    def linhas():
        return pg.evaluate("G.condicoes.length")

    def corpo():
        return pg.evaluate("document.documentElement.outerHTML")

    def tudo_da_tela():
        """Todo texto que a tela tem: o que se le, o que esta em campo e o que esta no codigo da pagina (sem o script, que traz o exemplo de fabrica)."""
        return pg.evaluate("""() => { const c = document.documentElement.cloneNode(true); c.querySelectorAll('script').forEach(s => s.remove()); return c.outerHTML; } """) + pg.evaluate("""() => document.body.innerText + '|' +
            Array.from(document.querySelectorAll('input, textarea')).map(i => i.value).join('|') + '|' + Array.from(document.querySelectorAll('[title], [aria-label]')).map(e => (e.title || '') + (e.getAttribute('aria-label') || '')).join('|')""")

    # ================================================================== [1] a lista
    if secao(1, 'A lista: colunas, filtro de situação, busca, vazio, limpar filtros, abrir, ordem, incluir'):
        try:
            limpar(); ir(LISTA)
            ok(txt('h1') == 'Gateways' and 'intermediários entre as operadoras de cartões e a sua empresa' in txt('.subtitle'), 'o título é Gateways e o subtítulo explica o que é um gateway')
            cab = pg.evaluate("Array.from(document.querySelectorAll('#wrapGateways thead th')).map(t => t.textContent.replace(/[▲▼]/g, '').trim())")
            ok(cab == ['Descrição', 'Gateway', 'Vale para', 'Conta financeira', 'Situação'], 'as colunas são Descrição, Gateway, Vale para, Conta financeira e Situação: %s' % cab)
            def tabela():
                return pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => Array.from(tr.children).map(td => td.textContent.replace(/\\s+/g, ' ').trim()))")
            t = tabela()
            ok([l[0] for l in t] == ['InfinityPay — loja virtual', 'Stone — maquininha da loja'], 'de fábrica a lista abre só nos Habilitados: InfinityPay e Stone (a Cielo, desabilitada, fica de fora): %s' % [l[0] for l in t])
            ok(txt('#filtroSituacao .dropdown-select-label') == 'Habilitados', 'o filtro de situação diz Habilitados')
            ok(t[0][1] == 'InfinityPay' and t[0][2] == 'Desk Shope, Desk Brands' and t[1][1] == 'Outro' and t[1][2] == 'Desk Shope', 'o Gateway e o Vale para (as lojas) estão certos: %s' % t)
            ok(t[0][3].startswith('InfinityPay — loja virtual') and t[1][3].startswith('Stone — maquininha da loja'), 'a Conta financeira de cada um é a própria descrição')
            ok(txt('#contagemLinhas') == '2 gateways' and 'HABILITADO' in pg.inner_text('#corpoTabela tr').upper(), 'o rodapé conta 2 gateways e a situação vem como badge')
            ok(pg.evaluate("document.querySelector('#btnIncluirGateway').getAttribute('href')") == '../integracoes/pagina-integracoes-gateways-detalhe.html?novo=1', '"Incluir gateway" abre a página em branco (?novo=1)')
            escolher('filtroSituacao', 'todos')
            ok(sorted(l[0] for l in tabela()) == ['Cielo (antiga)', 'InfinityPay — loja virtual', 'Stone — maquininha da loja'], 'Todos mostra os três, com a Cielo (antiga)')
            escolher('filtroSituacao', 'desabilitado')
            t = tabela()
            ok(len(t) == 1 and t[0][0] == 'Cielo (antiga)' and 'DESABILITADO' in t[0][4].upper() and t[0][2] == 'Desk Brands', 'Desabilitados mostra só a Cielo, na Desk Brands')
            escolher('filtroSituacao', 'todos')
            pg.fill('#campoBusca', 'stone')
            ok([l[0] for l in tabela()] == ['Stone — maquininha da loja'], 'a busca acha pela descrição')
            pg.fill('#campoBusca', 'infinity')
            ok([l[0] for l in tabela()] == ['InfinityPay — loja virtual'], 'a busca acha pelo tipo e sem diferenciar maiúscula')
            pg.fill('#campoBusca', 'MAQUININHA')
            ok(len(tabela()) == 1, 'a busca ignora maiúscula')
            pg.fill('#campoBusca', 'nada disso existe')
            ok(visivel('#emptyState') and not visivel('#wrapGateways') and txt('#emptyTitulo') == 'Nenhum gateway neste filtro', 'sem resultado aparece o estado vazio, dizendo que é o filtro')
            ok(txt('#contagemLinhas') == '0 gateways' and txt('#paginacaoResumo') == 'Mostrando 0 de 0', 'e o rodapé diz zero')
            clic('#btnLimparFiltros'); pg.wait_for_timeout(150)
            ok(len(tabela()) == 2 and pg.input_value('#campoBusca') == '' and txt('#filtroSituacao .dropdown-select-label') == 'Habilitados' and not visivel('#emptyState'),
               '"Limpar filtros" do vazio devolve a lista como ela abre: sem busca, só os Habilitados')
            escolher('filtroSituacao', 'todos'); pg.fill('#campoBusca', 'cielo')
            clic('#linkLimparFiltros'); pg.wait_for_timeout(150)
            ok(len(tabela()) == 2 and pg.input_value('#campoBusca') == '' and txt('#filtroSituacao .dropdown-select-label') == 'Habilitados', 'o link "limpar filtros" da barra faz o mesmo')
            # ordem
            pg.click("#wrapGateways th[data-ordem='descricao']"); pg.wait_for_timeout(150)
            ok([l[0] for l in tabela()] == ['Stone — maquininha da loja', 'InfinityPay — loja virtual'], 'clicar na Descrição inverte a ordem')
            pg.click("#wrapGateways th[data-ordem='tipo']"); pg.wait_for_timeout(150)
            ok(tabela()[0][1] == 'InfinityPay', 'ordenar pelo Gateway')
            # abrir
            pg.click('#corpoTabela tr:nth-child(2)'); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            ok(re.search(r'pagina-integracoes-gateways-detalhe\.html\?id=2$', pg.url) is not None and txt('#tituloGw') == 'Stone — maquininha da loja', 'clicar na linha abre a página daquele gateway: %s' % pg.url[-50:])
            # sem nenhum gateway
            limpar(); ir(LISTA)
            pg.evaluate("localStorage.setItem('deskGateways', JSON.stringify({ gateways: [] }))"); ir(LISTA)
            ok(visivel('#emptyState') and txt('#emptyTitulo') == 'Nenhum gateway cadastrado', 'sem nenhum gateway a lista diz que não há nenhum cadastrado (e não que é o filtro)')
            ok(pg.evaluate("localStorage.getItem('deskGatewaysExemplo')") == '1' and len(gws()) == 0, 'e o exemplo de fábrica não volta por cima do que o usuário apagou')

        # ================================================================== [2] a pagina por tipo
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 1 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(2, 'A página por tipo: o que aparece e some'):
        try:
            limpar(); ir(DET, '?novo=1')
            ok(txt('#tituloGw') == 'Novo gateway' and 'nada foi gravado' in txt('#subGw'), 'o cadastro novo abre em branco, com o título Novo gateway')
            ok(not visivel('#menuMaisAcoes'), 'sem as ações que só valem para gateway que já existe (excluir)')
            ok(visivel('#cardGateway') and all(not visivel(s) for s in ('#secRecebimento', '#secDados', '#secTarifas', '#secSped', '#secGateway', '#secCondicoes', '#campoConta')),
               'sem escolher o gateway só o bloco do topo aparece')
            ok(txt('#gwTipo .dropdown-select-label') == 'Selecione' and pg.input_value('#gwDescricao') == '' and txt('#gwSituacao .dropdown-select-label') == 'Habilitado' and txt('#gwLojas .dropdown-select-label') == 'Selecione as lojas',
               'Gateway e Vale para em "Selecione", descrição vazia, Situação Habilitado')
            itens = pg.evaluate("Array.from(document.querySelectorAll('#menuGwTipo .dropdown-select-item')).map(i => i.textContent)")
            ok(itens == ['InfinityPay', 'Outro'], 'o menu do Gateway tem InfinityPay e Outro, sem Pagar.me: %s' % itens)
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwSituacao .dropdown-select-item')).map(i => i.textContent)") == ['Habilitado', 'Desabilitado'], 'a Situação é Habilitado ou Desabilitado')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwLojas label')).map(i => i.textContent.trim())") == ['Desk Shope', 'Desk Brands', 'Desk Tech'], 'Vale para lista as três lojas, em caixas de marcar')
            # Outro
            escolher('gwTipo', 'outro')
            ok(pg.input_value('#gwDescricao') == 'Outro' and txt('#gwConta') == 'Outro', 'escolher Outro preenche a descrição com o nome do tipo, e a conta financeira é igual a ela')
            ok(visivel('#campoConta') and 'Conta de extrato do saldo disponível no gateway' in txt('#gwContaHint') and 'nasce ao salvar' in txt('#gwContaHint'), 'a conta aparece só para leitura, com a dica do print e dizendo que nasce ao salvar')
            ok(pg.evaluate("document.querySelector('#gwConta').tagName") == 'DIV', 'a conta financeira é leitura: não é campo para digitar')
            ok(all(visivel(s) for s in ('#secTarifas', '#secSped', '#secGateway', '#secCondicoes')) and all(not visivel(s) for s in ('#secRecebimento', '#secDados', '#blocoChave')),
               'Outro mostra tarifas, Sped, configurações do gateway e condições, e não mostra recebimento, juros nem chave da API')
            ok(txt('#gwTarifacao .dropdown-select-label') == 'Dia seguinte após a transação' and not visivel('#campoDiaDebito'), 'a tarifação abre em "Dia seguinte após a transação" e sem o Dia para débito')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwTarifacao .dropdown-select-item')).map(i => i.textContent)") ==
               ['Em dia específico', 'No dia da transação', 'Dia seguinte após a transação', 'No dia do pagamento (somada à taxa)'], 'as quatro opções de tarifação')
            escolher('gwTarifacao', 'especifico')
            ok(visivel('#campoDiaDebito'), 'o Dia para débito só aparece com "Em dia específico"')
            for outra in ('transacao', 'seguinte', 'pagamento'):
                escolher('gwTarifacao', outra)
                ok(not visivel('#campoDiaDebito'), 'com a tarifação "%s" o Dia para débito some' % outra)
            escolher('gwTarifacao', 'especifico')
            pg.fill('#gwDescricao', 'Minha maquininha'); marcar('menuGwLojas', '1'); escolher('gwCategoriaTarifa', '17')
            for ruim in ('', '0', '32', 'abc', '1.5'):
                pg.fill('#gwDiaDebito', ruim); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
                ok(visivel('#erroDiaDebito') and len(gws()) == 3 and not modal(), 'Dia para débito "%s" é recusado, com a mensagem, e nada é gravado' % ruim)
            for bom in ('1', '31', '15'):
                pg.fill('#gwDiaDebito', bom)
                ok(pg.evaluate("validar().some(e => e.campo === 'DiaDebito')") is False, 'Dia para débito %s é aceito' % bom)
            escolher('gwTarifacao', 'transacao')
            pg.evaluate("G.diaDebito = ''")
            ok(pg.evaluate("validar().some(e => e.campo === 'DiaDebito')") is False, 'com outra tarifação o Dia para débito vazio não é erro')
            # troca de tipo
            pg.fill('#gwDescricao', 'Minha maquininha')
            escolher('gwTipo', 'infinitypay')
            ok(pg.input_value('#gwDescricao') == 'Minha maquininha', 'trocar de tipo não mexe na descrição que a pessoa escreveu')
            ok(all(visivel(s) for s in ('#secRecebimento', '#secDados', '#secSped', '#secGateway', '#secCondicoes', '#blocoChave')) and all(not visivel(s) for s in ('#secTarifas', '#campoDiaDebito')),
               'InfinityPay mostra recebimento, dados adicionais, Sped, chave da API e condições, e não mostra as tarifas')
            pg.fill('#gwDescricao', ''); escolher('gwTipo', 'outro'); escolher('gwTipo', 'infinitypay')
            ok(pg.input_value('#gwDescricao') == 'InfinityPay', 'trocar de tipo com a descrição vazia a preenche de novo com o nome do tipo')
            escolher('gwTipo', 'outro')
            ok(pg.input_value('#gwDescricao') == 'Outro', 'e, sem edição, ela acompanha o nome do tipo a cada troca')
            # os blocos de InfinityPay (molde: Pagar.me 2.0)
            escolher('gwTipo', 'infinitypay')
            rot = pg.evaluate("Array.from(document.querySelectorAll('#secRecebimento label, #secDados label, #secSped label, #secGateway label')).filter(l => l.getClientRects().length).map(l => l.textContent.replace(/\\s+/g, ' ').trim())")
            for esperado in ('Categoria padrão para as contas a receber', 'Conta financeira para crédito', 'Data em que será baixada a conta a receber', 'Taxa mensal de juros', 'Multa',
                             'Nº de dias para multa após o vencimento', 'CNPJ da instituição', 'Endereço da instituição', 'Município da instituição', 'Chave da API', 'Bandeiras atendidas',
                             'Bandeira padrão', 'Antecipação dos recebíveis i'):
                ok(esperado in rot, 'o campo "%s" existe em InfinityPay' % esperado)
            ok('Versão da API' not in ' '.join(rot), 'sem "Versão da API", que é do Pagar.me')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwCategoria .dropdown-select-item')).map(i => i.textContent)") ==
               ['Venda de mercadorias', 'Venda em marketplace', 'Frete cobrado do cliente', 'Juros e multas recebidos', 'Rendimento de aplicação'], 'a categoria padrão traz as categorias de receita')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwContaCredito .dropdown-select-item')).map(i => i.textContent)") == ['Banco Inter — conta corrente', 'Mercado Pago'] and
               'Conta bancária que recebe os resgates efetuados neste gateway' in pg.inner_text('#campoContaCredito'), 'a conta para crédito traz as contas bancárias, com a dica do print')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwBaixa .dropdown-select-item')).map(i => i.textContent)") == ['Data de liberação no gateway', 'Data do pagamento'], 'a data da baixa tem as duas opções')
            ok('Calcular juros e multas após o vencimento' in pg.inner_text('#secDados') and 'recebimento de títulos vencidos no contas a receber' in pg.inner_text('#secDados'), 'o interruptor de juros e multas traz o texto do print')
            # categorias de despesa em Outro
            escolher('gwTipo', 'outro')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwCategoriaTarifa .dropdown-select-item')).map(i => i.textContent)").count('Taxa de cartão e gateway') == 1 and
               'Venda de mercadorias' not in pg.evaluate("Array.from(document.querySelectorAll('#menuGwCategoriaTarifa .dropdown-select-item')).map(i => i.textContent)"), 'a categoria das tarifas traz as de despesa, e nenhuma de receita')
            # antecipacao e ajuda
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwAntecipacao .dropdown-select-item')).map(i => i.textContent)") == ['Sem antecipação', 'Antecipado'], 'a antecipação é Sem antecipação ou Antecipado')
            ok(not visivel('#ajudaAntecipacao'), 'a explicação da antecipação começa fechada')
            clic('#btnAjudaAntecipacao'); pg.wait_for_timeout(100)
            ok(visivel('#ajudaAntecipacao') and 'Antecipado: o gateway paga' in txt('#ajudaAntecipacao') and pg.get_attribute('#btnAjudaAntecipacao', 'aria-expanded') == 'true', 'o ícone de ajuda abre a explicação')
            clic('#btnAjudaAntecipacao'); pg.wait_for_timeout(100)
            ok(not visivel('#ajudaAntecipacao'), 'e fecha de novo')
            ok('Considerar próximo dia útil para parcelas e tarifas' in pg.inner_text('#secGateway'), 'o interruptor do próximo dia útil existe')
            # validacoes do topo
            limpar(); ir(DET, '?novo=1'); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok(visivel('#erroTipo') and len(gws()) == 3, 'salvar sem escolher o gateway é recusado, com a mensagem')
            escolher('gwTipo', 'outro'); pg.fill('#gwDescricao', ''); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok(visivel('#erroDescricao') and visivel('#erroLojas') and visivel('#erroCategoriaTarifa'), 'sem descrição, sem loja e sem categoria das tarifas: as três mensagens aparecem')
            pg.fill('#gwDescricao', 'Stone — maquininha da loja'); marcar('menuGwLojas', '1'); escolher('gwCategoriaTarifa', '17'); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok(visivel('#erroDescricao') and 'Já existe um gateway com esta descrição' in txt('#erroDescricao') and len(gws()) == 3, 'a descrição é única: repetir a de outro gateway é recusado')
            pg.fill('#gwDescricao', 'stone — MAQUININHA da loja'); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok('Já existe um gateway' in txt('#erroDescricao'), 'e a comparação ignora maiúscula')
            pg.fill('#gwDescricao', 'Mercado Pago'); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok('Já existe uma conta financeira com este nome' in txt('#erroDescricao') and len(gws()) == 3, 'a descrição também não repete o nome de uma conta financeira que já existe (a conta do gateway leva a descrição)')
            pg.fill('#gwDescricao', 'Meu gateway'); pg.evaluate("document.getElementById('gwDescricao').dispatchEvent(new Event('input', { bubbles: true }))")
            ok(not visivel('#erroDescricao'), 'digitar tira a mensagem de erro')
            ok(txt('#tituloGw') == 'Meu gateway', 'o título acompanha a descrição enquanto se digita')
            # os campos de InfinityPay
            escolher('gwTipo', 'infinitypay'); pg.fill('#gwDescricao', 'Minha InfinityPay')
            clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok(visivel('#erroCategoria') and visivel('#erroContaCredito') and visivel('#erroChave'), 'InfinityPay exige a categoria, a conta para crédito e a chave da API')
            escolher('gwCategoria', '1'); escolher('gwContaCredito', '2')
            for campo, ruim in (('gwJuros', '101'), ('gwJuros', 'abc'), ('gwJuros', '1,234'), ('gwMulta', '-1'), ('gwMulta', '100,5'), ('gwDiasMulta', '2,5'), ('gwDiasMulta', '-3')):
                pg.fill('#' + campo, ruim); pg.fill('#gwChave', CHAVE_NOVA); clic('#btnSalvarGw'); pg.wait_for_timeout(150)
                err = {'gwJuros': '#erroJuros', 'gwMulta': '#erroMulta', 'gwDiasMulta': '#erroDiasMulta'}[campo]
                ok(visivel(err) and len(gws()) == 3, '%s "%s" é recusado' % (campo, ruim))
                pg.fill('#' + campo, '')
            for campo, bom in (('gwJuros', '1,99'), ('gwMulta', '100'), ('gwDiasMulta', '30')):
                pg.fill('#' + campo, bom)
            pg.fill('#gwCnpj', '123'); clic('#btnSalvarGw'); pg.wait_for_timeout(150)
            ok(visivel('#erroCnpj') and len(gws()) == 3, 'CNPJ pela metade é recusado')
            pg.fill('#gwCnpj', '12345678000195')
            ok(pg.input_value('#gwCnpj') == '12.345.678/0001-95', 'o CNPJ ganha a máscara enquanto se digita')
            ok(pg.evaluate("validar().some(e => e.campo === 'Cnpj')") is False and not visivel('#erroCnpj'), 'o CNPJ completo é aceito, e digitar tira a mensagem')
            pg.fill('#gwCnpj', ''); pg.fill('#gwChave', CHAVE_NOVA)
            ok(pg.evaluate("document.getElementById('gwChave').type") == 'password', 'a chave da API é campo de senha')

        # ================================================================== [3] a tabela de condicoes
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 2 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(3, 'A tabela de condições: por bandeira, tirar, adicionar, repetida, validações, "a partir da"'):
        try:
            limpar(); novo('outro', 'Maquininha de teste')
            ok(linhas() == 3 and pg.evaluate("G.condicoes.map(c => c.forma).join()") == 'debito,boleto,pix', 'sem bandeira a tabela tem só débito, boleto e Pix')
            fab = pg.evaluate("G.condicoes.map(c => [c.prazo, c.taxa, c.tarifa])")
            ok(fab == [['2', '0,00', '2,00'], ['2', '0,00', '2,00'], ['0', '0,00', '0,00']], 'de fábrica: débito e boleto 2 dias e tarifa de R$ 2,00; Pix 0 dia e tarifa zero; taxa zero nos três: %s' % fab)
            ok(txt('#gwCondContagem') == '3 condições', 'a contagem diz 3 condições')
            ok(txt('#gwBandeiras .dropdown-select-label') == 'Selecione' and pg.evaluate("document.querySelector('#gwBandeiraPadrao .dropdown-select-btn').disabled"), 'sem bandeira o rótulo é Selecione e a bandeira padrão fica travada')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwBandeiras label')).map(l => l.textContent.trim())") ==
               ['Selecionar todas', 'Visa', 'Mastercard', 'American Express', 'Diners Club', 'Elo', 'Hipercard', 'BNDES', 'Outro'], 'a multiseleção tem "Selecionar todas" e as oito bandeiras')
            marcar('menuGwBandeiras', 'visa')
            ok(linhas() == 15 and txt('#gwBandeiras .dropdown-select-label') == 'Visa', 'marcar a Visa traz o crédito de 1x a 12x: 15 linhas')
            ok(txt('#gwBandeiraPadrao .dropdown-select-label') == 'Visa', 'e a primeira bandeira escolhida vira a padrão')
            visa = pg.evaluate("G.condicoes.filter(c => c.bandeira === 'visa')")
            ok([c['taxa'] for c in visa] == [('%.2f' % t).replace('.', ',') for t in TAXAS], 'as taxas de fábrica da Visa: 3 · 3,6 · 4,25 · 4,9 · 5,5 · 6,15 · 6,8 · 7,45 · 8 · 8,7 · 9,35 · 10')
            ok([c['prazo'] for c in visa] == ['31'] * 11 + ['30'] and all(c['tarifa'] == '0,00' for c in visa), 'prazo 31 dias, e 30 na 12x; tarifa zero no crédito')
            ok([c['parcelas'] for c in visa] == list(range(1, 13)), 'de 1x a 12x')
            marcar('menuGwBandeiras', 'mastercard')
            ok(linhas() == 27 and txt('#gwBandeiras .dropdown-select-label') == 'Visa, Mastercard', 'Mastercard traz mais 12: 27 linhas')
            todas_bandeiras()
            ok(linhas() == 99 and txt('#gwBandeiras .dropdown-select-label') == 'Todas selecionadas (8)', '"Selecionar todas": as oito bandeiras dão 99 linhas (3 fixas e 8 vezes 12)')
            ok(pg.evaluate("document.querySelector('#menuGwBandeiras [data-todas]').checked"), 'a caixa "Selecionar todas" fica marcada')
            ok(pg.evaluate("document.querySelectorAll('#wrapCondicoes tr.gw-linha').length") == 99 and txt('#gwCondContagem') == '99 condições', 'a tela tem as 99 linhas, e a contagem diz 99 condições')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes th')).map(t => t.textContent.trim())") == ['Forma', 'Bandeira', 'Parcelado até', 'Prazo', 'Taxa', 'Tarifa', ''], 'as colunas são Forma, Bandeira, Parcelado até, Prazo, Taxa, Tarifa e excluir')
            # agrupamento
            grupos = pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-grupo')).map(t => t.textContent)")
            ok(len(grupos) == 9 and 'Débito, boleto e Pix' in grupos[0] and 'Cartão de crédito · Visa' in grupos[1] and 'Cartão de crédito · Outro' in grupos[8], 'a tabela vem agrupada: débito/boleto/Pix e uma faixa por bandeira, com o nome da bandeira')
            ok('12 condições · taxa de 3,00% a 10,00%' in pg.inner_text('#wrapCondicoes tr.gw-grupo:nth-child(n+2)'), 'a faixa resume a bandeira: quantas condições e de quanto a quanto vai a taxa')
            ok(pg.evaluate("document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"fixas\"]').length") == 3 and pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"fixas\"]')).every(t => t.style.display !== 'none')"),
               'com muitas bandeiras o grupo de débito, boleto e Pix fica aberto')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de^=\"credito\"]')).every(t => t.style.display === 'none')"),
               'com mais de duas bandeiras as faixas de crédito começam recolhidas')
            VISIVEIS = "Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha')).filter(t => t.getClientRects().length).length"
            ok(pg.evaluate(VISIVEIS) == 3 and txt('#btnAlternarGrupos') == 'Recolher todas', 'só as 3 linhas de débito, boleto e Pix aparecem, e o botão oferece "Recolher todas"')
            # recolher e expandir
            clic('#btnAlternarGrupos'); pg.wait_for_timeout(100)
            ok(pg.evaluate(VISIVEIS) == 0 and txt('#btnAlternarGrupos') == 'Expandir todas', '"Recolher todas" fecha tudo, e o botão passa a oferecer "Expandir todas"')
            clic('#btnAlternarGrupos'); pg.wait_for_timeout(100)
            ok(pg.evaluate(VISIVEIS) == 99 and txt('#btnAlternarGrupos') == 'Recolher todas', '"Expandir todas" abre as 99 linhas')
            pg.evaluate("ESTADO_GRUPOS = {}; renderCond()")
            clic("#wrapCondicoes tr.gw-grupo[data-grupo='credito|visa']"); pg.wait_for_timeout(100)
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"credito|visa\"]')).filter(t => t.getClientRects().length).length") == 12 and
               pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"credito|elo\"]')).filter(t => t.getClientRects().length).length") == 0, 'clicar na faixa da Visa abre só as 12 linhas dela')
            clic("#wrapCondicoes tr.gw-grupo[data-grupo='credito|visa']"); pg.wait_for_timeout(100)
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"credito|visa\"]')).filter(t => t.getClientRects().length).length") == 0, 'e clicar de novo recolhe')
            # tirar bandeira sem editar
            marcar('menuGwBandeiras', 'outro')
            ok(linhas() == 87 and not modal() and txt('#gwBandeiras .dropdown-select-label') == '7 selecionadas', 'tirar a bandeira "Outro", sem ter mexido nela, tira as 12 linhas dela sem perguntar: 87 linhas')
            ok(pg.evaluate("G.condicoes.some(c => c.bandeira === 'outro')") is False, 'e nenhuma linha dela sobra')
            # padrao acompanha
            escolher('gwBandeiraPadrao', 'elo')
            marcar('menuGwBandeiras', 'elo')
            ok(txt('#gwBandeiraPadrao .dropdown-select-label') == 'Visa' and linhas() == 75, 'tirar a bandeira que era a padrão passa a padrão para outra que sobrou (Visa)')
            # editar e tirar
            pg.evaluate("ESTADO_GRUPOS['credito|visa'] = true; renderCond()")
            i = pg.evaluate("G.condicoes.findIndex(c => c.bandeira === 'visa' && c.parcelas === 3)")
            pg.fill("#wrapCondicoes input[data-i='%d'][data-campo='taxa']" % i, '5,25')
            ok(pg.evaluate("G.condicoes[%d].taxa" % i) == '5,25' and '1 editada' in pg.inner_text('#wrapCondicoes tr.gw-grupo[data-grupo="credito|visa"]') and '1 editada' in txt('#gwCondContagem'),
               'editar uma taxa passa para o rascunho, e a faixa e a contagem dizem "1 editada"')
            marcar('menuGwBandeiras', 'visa')
            m = modal()
            ok('Visa' in m and '1 condição' in m and 'apaga todas as linhas' in m and linhas() == 75, 'tirar a Visa, que tem uma linha editada, pergunta antes e diz o que vai embora: %s' % m[:110])
            ok(pg.evaluate("document.querySelector('#menuGwBandeiras input[value=visa]').checked") is True, 'enquanto não confirma, a Visa continua marcada')
            cancelar_modal()
            ok(linhas() == 75 and pg.evaluate("G.bandeiras.indexOf('visa')") >= 0 and pg.evaluate("G.condicoes[%d].taxa" % i) == '5,25', 'cancelar mantém a bandeira, as 12 linhas e a taxa editada')
            marcar('menuGwBandeiras', 'visa'); confirmar()
            ok(linhas() == 63 and pg.evaluate("G.condicoes.some(c => c.bandeira === 'visa')") is False and pg.evaluate("document.querySelector('#menuGwBandeiras input[value=visa]').checked") is False,
               'confirmar tira a Visa e as 12 linhas dela, inclusive a editada: 63 linhas')
            marcar('menuGwBandeiras', 'visa')
            ok(pg.evaluate("G.condicoes.filter(c => c.bandeira === 'visa').map(c => c.taxa)") == [('%.2f' % t).replace('.', ',') for t in TAXAS], 'pôr a Visa de volta traz as linhas de fábrica, e não a taxa editada que se foi')
            # adicionar condicao
            limpar(); novo('outro', 'Maquininha de teste')
            marcar('menuGwBandeiras', 'visa'); marcar('menuGwBandeiras', 'elo')
            clic('#btnAddCondicao'); pg.wait_for_timeout(150)
            ok(visivel('#gwNovaCond') and visivel('#ncBandeira') and visivel('#ncParcelas'), '"adicionar condição comercial" abre a linha de escolha: forma, bandeira e parcela')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuNcBandeira .dropdown-select-item')).map(i => i.textContent)") == ['Visa', 'Elo'], 'a bandeira da nova condição é uma das escolhidas')
            escolher('ncForma', 'debito')
            ok(not visivel('#ncBandeira') and not visivel('#ncParcelas'), 'débito, boleto e Pix não têm bandeira nem parcela')
            clic('#btnNcAdicionar'); pg.wait_for_timeout(150)
            ok(visivel('#erroNovaCond') and 'já existe' in txt('#erroNovaCond') and linhas() == 27, 'débito já existe: a condição repetida é recusada, dizendo qual é, e nada entra')
            escolher('ncForma', 'credito'); escolher('ncBandeira', 'elo'); escolher('ncParcelas', '3')
            clic('#btnNcAdicionar'); pg.wait_for_timeout(150)
            ok('já existe' in txt('#erroNovaCond') and 'Elo' in txt('#erroNovaCond') and 'em 3x' in txt('#erroNovaCond') and linhas() == 27, 'crédito Elo 3x já existe: recusada também')
            # tira a de Pix e volta
            pg.evaluate("G.condicoes.splice(G.condicoes.findIndex(c => c.forma === 'pix'), 1); renderCond()")
            ok(linhas() == 26 and not pg.evaluate("G.condicoes.some(c => c.forma === 'pix')"), 'excluir uma linha (lixeira da linha) a tira da tabela')
            escolher('ncForma', 'pix'); clic('#btnNcAdicionar'); pg.wait_for_timeout(200)
            ok(linhas() == 27 and pg.evaluate("G.condicoes.filter(c => c.forma === 'pix').length") == 1 and not visivel('#gwNovaCond'), 'depois de excluída, a condição pode ser acrescentada de novo, e a linha de escolha fecha')
            ok(pg.evaluate("G.condicoes.map(c => c.forma).slice(0, 3).join()") == 'debito,boleto,pix', 'ela entra no lugar dela: débito, boleto e Pix antes do crédito')
            pg.evaluate("document.querySelector('#wrapCondicoes tr.gw-linha .gw-lixo').click()")
            ok(linhas() == 26, 'a lixeira da linha excluí a linha')
            # sem bandeira nao ha credito
            limpar(); novo('outro', 'Sem bandeira')
            clic('#btnAddCondicao'); pg.wait_for_timeout(100); clic('#btnNcAdicionar'); pg.wait_for_timeout(150)
            ok('Escolha antes as bandeiras' in txt('#erroNovaCond') and linhas() == 3, 'crédito sem bandeira escolhida: a tela manda escolher as bandeiras antes')
            # validacoes
            def cel(i, campo):
                return "#wrapCondicoes input[data-i='%d'][data-campo='%s']" % (i, campo)
            casos = [('prazo', 'abc'), ('prazo', '-1'), ('prazo', '2,5'), ('taxa', '101'), ('taxa', 'x'), ('taxa', '-1'), ('tarifa', '-0,5'), ('tarifa', 'zz'), ('taxa', '1,234'), ('prazo', '')]
            for campo, ruim in casos:
                limpar(); novo('outro', 'Validando'); marcar('menuGwBandeiras', 'visa'); pg.evaluate("ESTADO_GRUPOS['fixas'] = true; renderCond()")
                pg.fill(cel(0, campo), ruim); clic('#btnSalvarGw'); pg.wait_for_timeout(250)
                ok(pg.evaluate("document.querySelectorAll('#wrapCondicoes td.tem-erro').length") == 1 and visivel('#erroCondicoes') and len(gws()) == 3 and not modal(),
                   '%s "%s" na tabela é recusado: a célula fica marcada, com a mensagem, e nada é gravado' % (campo, ruim))
            ok(pg.evaluate("document.querySelector('#wrapCondicoes .gw-erro-cel').textContent.length") > 5, 'a mensagem de erro aparece na célula, e não só a borda')
            pg.fill(cel(0, 'prazo'), '2')
            ok(pg.evaluate("document.querySelectorAll('#wrapCondicoes td.tem-erro').length") == 0 and not visivel('#erroCondicoes'), 'corrigir o valor tira a marca e a mensagem')
            for campo, bom in (('prazo', '0'), ('prazo', '45'), ('taxa', '0'), ('taxa', '100'), ('taxa', '4,25'), ('tarifa', '0'), ('tarifa', '12,5')):
                pg.fill(cel(0, campo), bom)
                ok(pg.evaluate("(() => { validar(); return Object.keys(ERROS_COND).length; })()") == 0, '%s "%s" é aceito' % (campo, bom))
            # erro dentro de grupo recolhido abre o grupo
            limpar(); novo('outro', 'Validando'); marcar('menuGwBandeiras', 'visa'); marcar('menuGwBandeiras', 'elo'); marcar('menuGwBandeiras', 'bndes')
            pg.evaluate("ESTADO_GRUPOS['credito|elo'] = false; G.condicoes.filter(c => c.bandeira === 'elo')[4].taxa = '999'; renderCond()")
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"credito|elo\"]')).every(t => t.style.display === 'none')"), 'a faixa da Elo está recolhida')
            clic('#btnSalvarGw'); pg.wait_for_timeout(250)
            ok(pg.evaluate("Array.from(document.querySelectorAll('#wrapCondicoes tr.gw-linha[data-grupo-de=\"credito|elo\"]')).every(t => t.style.display !== 'none')") and pg.evaluate("document.querySelectorAll('#wrapCondicoes td.tem-erro').length") == 1,
               'o erro numa linha de faixa recolhida abre a faixa, para o erro aparecer')
            # repassar taxas
            limpar(); novo('outro', 'Repasse')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwRepassar .dropdown-select-item')).map(i => i.textContent)") == ['Não', 'Sim', 'Opcional', 'Opcional com liberação do gerente'], 'repassar taxas: Não, Sim, Opcional e Opcional com liberação do gerente')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#menuGwAPartir .dropdown-select-item')).map(i => i.textContent)") == ['%dª parcela' % n for n in range(1, 13)], '"a partir da" vai da 1ª à 12ª parcela')
            ok('Neste momento, o repasse de taxas é exclusivo para PDV.' in pg.inner_text('#campoRepassar'), 'a dica diz que o repasse é exclusivo para PDV')
            ok(txt('#gwRepassar .dropdown-select-label') == 'Não' and pg.evaluate("document.querySelector('#gwAPartir .dropdown-select-btn').disabled") is True, 'com "Não" o "a partir da" fica desabilitado')
            clic('#gwAPartir .dropdown-select-btn'); pg.wait_for_timeout(100)
            ok(not pg.evaluate("document.querySelector('#menuGwAPartir').classList.contains('open')"), 'e não abre')
            for v in ('sim', 'opcional', 'gerente'):
                escolher('gwRepassar', v)
                ok(pg.evaluate("document.querySelector('#gwAPartir .dropdown-select-btn').disabled") is False, 'com "%s" o "a partir da" é habilitado' % v)
            escolher('gwAPartir', '4')
            ok(txt('#gwAPartir .dropdown-select-label') == '4ª parcela' and pg.evaluate("G.repassarAPartir") == '4', 'e escolhe-se a parcela')
            escolher('gwRepassar', 'nao')
            ok(pg.evaluate("document.querySelector('#gwAPartir .dropdown-select-btn').disabled") is True, 'voltar a "Não" trava de novo')

        # ================================================================== [4] a chave da API
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 3 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(4, 'A chave da API: mascarada, nunca inteira; testar conexão; o link de conciliação'):
        try:
            limpar(); ir(DET, '?id=1')
            ok(visivel('#chaveSalvaBox') and not visivel('#chaveEdicaoBox') and txt('#gwChaveMascara') == MASCARA + 'd605', 'a chave que já está guardada aparece só mascarada: •••• e os 4 últimos caracteres: %s' % txt('#gwChaveMascara'))
            ok(CHAVE_API not in tudo_da_tela() and CHAVE_API[:-4] not in tudo_da_tela(), 'a chave inteira não está em lugar nenhum da tela: nem no texto, nem em campo, nem no código da página')
            ok(pg.input_value('#gwChave') == '' and pg.evaluate("G.chaveNova") == '', 'a caixa de senha está vazia')
            ok(pg.evaluate("G.chaveSalva") == CHAVE_API, 'o rascunho em memória guarda a chave (é o que o teste de conexão usa), mas ela nunca é escrita na página')
            # testar conexao com a chave guardada
            clic('#btnTestar'); pg.wait_for_timeout(100)
            ok(txt('#gwTesteMsg') == 'Conexão ok (simulada no protótipo).' and 'ok' in pg.get_attribute('#gwTesteMsg', 'class'), 'testar conexão com a chave guardada diz "Conexão ok (simulada no protótipo)"')
            ok(CHAVE_API not in tudo_da_tela(), 'e a chave continua fora da tela depois do teste')
            # trocar
            clic('#btnTrocarChave'); pg.wait_for_timeout(100)
            ok(visivel('#chaveEdicaoBox') and not visivel('#chaveSalvaBox') and visivel('#btnCancelarTroca'), '"Trocar chave" abre a caixa de senha vazia, com como voltar atrás')
            clic('#btnTestar'); pg.wait_for_timeout(100)
            ok('Informe a chave da API' in txt('#gwTesteMsg') and 'erro' in pg.get_attribute('#gwTesteMsg', 'class'), 'testar com a caixa vazia: erro dizendo que falta a chave')
            pg.fill('#gwChave', 'abc123'); clic('#btnTestar'); pg.wait_for_timeout(100)
            ok('curta demais' in txt('#gwTesteMsg') and 'pelo menos 16' in txt('#gwTesteMsg'), 'testar com chave curta: erro dizendo que é curta e quanto precisa ter')
            pg.fill('#gwChave', 'ipay live 8f3a1c9e72b4d6%'); clic('#btnTestar'); pg.wait_for_timeout(100)
            ok('caracteres' in txt('#gwTesteMsg') and 'erro' in pg.get_attribute('#gwTesteMsg', 'class'), 'testar com caracteres que não existem numa chave: erro dizendo quais valem')
            pg.fill('#gwChave', CHAVE_NOVA); clic('#btnTestar'); pg.wait_for_timeout(100)
            ok(txt('#gwTesteMsg') == 'Conexão ok (simulada no protótipo).', 'chave com formato válido: "Conexão ok (simulada no protótipo)"')
            ok(pg.evaluate("document.getElementById('gwChave').type") == 'password' and 'Conexão ok' in txt('#gwTesteMsg'), 'a chave digitada fica numa caixa de senha')
            # cancelar a troca
            clic('#btnCancelarTroca'); pg.wait_for_timeout(100)
            ok(visivel('#chaveSalvaBox') and pg.input_value('#gwChave') == '' and pg.evaluate("G.chaveNova") == '' and CHAVE_NOVA not in tudo_da_tela(), '"Manter a chave que está guardada" volta à máscara e joga fora o que foi digitado')
            # salvar chave curta
            clic('#btnTrocarChave'); pg.fill('#gwChave', 'curta'); clic('#btnSalvarGw'); pg.wait_for_timeout(200)
            ok(visivel('#erroChave') and 'curta demais' in txt('#erroChave') and not modal() and gw(1)['chave'] == CHAVE_API, 'salvar com chave curta é recusado, e a guardada não muda')
            # salvar chave nova: pede senha
            pg.fill('#gwChave', CHAVE_NOVA); clic('#btnSalvarGw'); pg.wait_for_timeout(300)
            ok(pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')") and 'A chave da API é trocada' in modal(), 'trocar a chave pede a senha (ação gatewayChave) e o painel diz que a chave é trocada')
            ok(CHAVE_NOVA not in modal() and CHAVE_API not in modal(), 'o painel de confirmação não mostra chave nenhuma')
            confirmar()
            ok(gw(1)['chave'] == CHAVE_NOVA and txt('#gwChaveMascara') == MASCARA + CHAVE_NOVA[-4:] and visivel('#chaveSalvaBox'), 'depois de salvar a tela volta à máscara com os 4 últimos da chave nova, e a chave nova foi gravada')
            ok(CHAVE_NOVA not in tudo_da_tela() and CHAVE_API not in tudo_da_tela() and pg.input_value('#gwChave') == '', 'a chave nova também não ficou na tela depois de salvar: nem a caixa, nem o código da página')
            # impressao
            pg.emulate_media(media='print'); pg.wait_for_timeout(100)
            ok(not visivel('#gwChave') and CHAVE_NOVA not in pg.evaluate("document.body.innerText") and CHAVE_API not in pg.evaluate("document.body.innerText"), 'na impressão a chave não sai: só a máscara')
            pg.emulate_media(media='screen')
            reg = log()
            ok(any(e['chave'] == 'gatewayChave' and e['senha'] for e in reg), 'a troca entra no Registro de atividades, com a marca de que passou por senha')
            ok(CHAVE_NOVA not in json.dumps(reg) and CHAVE_API not in json.dumps(reg) and all(CHAVE_NOVA[:12] not in e['detalhe'] for e in reg), 'e o registro de atividades não guarda a chave, nem inteira nem em pedaço')
            # planilha e impressao da lista
            ir(LISTA)
            with pg.expect_download(timeout=5000) as d:
                clic("#menuMaisAcoes [data-acao='planilha']")
            corpo_csv = open(d.value.path(), encoding='utf-8-sig').read()
            ok('InfinityPay — loja virtual' in corpo_csv and CHAVE_NOVA not in corpo_csv and CHAVE_API not in corpo_csv and 'ipay_' not in corpo_csv, 'a planilha da lista leva os gateways, e nenhuma chave')
            linhas_csv = list(csv.reader(io.StringIO(corpo_csv), delimiter=';'))
            ok([c.upper() for c in linhas_csv[0]] == ['DESCRIÇÃO', 'GATEWAY', 'VALE PARA', 'CONTA FINANCEIRA', 'SITUAÇÃO'] and len(linhas_csv) == 3, 'o cabeçalho da planilha é o da lista, com os dois habilitados: %s' % linhas_csv[0])
            pg.evaluate("window.dispatchEvent(new Event('beforeprint'))"); pg.emulate_media(media='print'); pg.wait_for_timeout(100)
            ok('Gateways' in pg.evaluate("document.getElementById('relatorioCabecalho').innerText") and 'ipay_' not in pg.evaluate("document.body.innerText"), 'a impressão da lista sai como relatório, sem chave')
            pg.emulate_media(media='screen')
            # chave no novo: digitada, so existe na caixa de senha
            limpar(); novo('infinitypay', 'Outra InfinityPay')
            ok(visivel('#chaveEdicaoBox') and not visivel('#chaveSalvaBox') and not visivel('#btnCancelarTroca'), 'no gateway novo a caixa de senha já abre, sem a máscara nem o "manter"')
            # link de conciliacao
            ok(not visivel('#gwLinkBox') and txt('#btnGerarLink') == 'Gerar link para conciliação automática de contas', 'o link de conciliação começa sem endereço')
            clic('#btnGerarLink'); pg.wait_for_timeout(100)
            url = txt('#gwLinkUrl')
            ok(visivel('#gwLinkBox') and re.match(r'^https://[^/]+/conciliacao/[a-z0-9]{8,}$', url) is not None, 'gerar o link mostra um endereço fictício https://…/conciliacao/<id>: %s' % url)
            ok('A InfinityPay chama este endereço para avisar os pagamentos' in txt('#gwLinkBox') and 'fictício' in txt('#gwLinkBox'), 'e o aviso diz o que é o link e que no protótipo ele é fictício')
            clic('#btnCopiarLink'); pg.wait_for_timeout(300)
            copiado = txt('#btnCopiarLink') == 'copiado' or 'Não foi possível copiar' in modal()
            ok(copiado, '"copiar" copia o endereço (e o botão diz "copiado") ou, se o navegador não deixa, avisa')
            try:
                lido = pg.evaluate("navigator.clipboard.readText()")
                ok(lido == url or txt('#btnCopiarLink') != 'copiado', 'o que foi copiado é o endereço do link: %s' % lido[-24:])
            except Exception:
                ok(True, 'o navegador do teste não deixa ler a área de transferência: o botão foi o que se pôde conferir')
            if modal():
                cancelar_modal()
            clic('#btnGerarLink'); pg.wait_for_timeout(100)
            ok(txt('#gwLinkUrl') != url and txt('#btnGerarLink').startswith('Gerar outro link'), 'gerar de novo troca o endereço (o anterior deixa de valer)')
            # o link grava
            pg.fill('#gwChave', CHAVE_NOVA); marcar('menuGwLojas', '3'); escolher('gwCategoria', '2'); escolher('gwContaCredito', '3')
            salvar()
            ok(gw(4)['conciliacao']['id'] == txt('#gwLinkUrl').split('/')[-1], 'o link de conciliação fica gravado com o gateway')

        # ================================================================== [5] gravar, recarregar, sair, excluir
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 4 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(5, 'Gravar e recarregar, sair com alteração pendente, excluir, senhas e registro'):
        try:
            limpar(); novo('outro', 'Stone da loja 2', lojas=('2', '3'))
            pg.fill('#gwCnpj', '98765432000110'); pg.fill('#gwEndereco', 'Rua Teste, 10'); pg.fill('#gwMunicipio', 'Fortaleza')
            escolher('gwTarifacao', 'especifico'); pg.fill('#gwDiaDebito', '12')
            marcar('menuGwBandeiras', 'visa'); marcar('menuGwBandeiras', 'elo'); escolher('gwBandeiraPadrao', 'elo'); escolher('gwAntecipacao', 'antecipado')
            clic('#gwProximoDiaUtil'); escolher('gwRepassar', 'sim'); escolher('gwAPartir', '3'); escolher('gwSituacao', 'desabilitado')
            i = pg.evaluate("G.condicoes.findIndex(c => c.bandeira === 'visa' && c.parcelas === 2)")
            pg.evaluate("ESTADO_GRUPOS['credito|visa'] = true; renderCond()")
            pg.fill("#wrapCondicoes input[data-i='%d'][data-campo='taxa']" % i, '3,9'); pg.fill("#wrapCondicoes input[data-i='%d'][data-campo='prazo']" % i, '28')
            pg.fill("#wrapCondicoes input[data-i='0'][data-campo='tarifa']", '1,5')
            ok('alterações' in txt('#infoPendente') and 'não salvas' in txt('#infoPendente'), 'com campo mexido o rodapé diz que há alterações não salvas')
            clic('#btnSalvarGw'); pg.wait_for_timeout(400)
            ok(modal() == '' and len(gws()) == 4, 'incluir gateway de Outro não pede senha nem painel (a ação nasce sem trava): grava direto')
            det = [e['detalhe'] for e in log() if e['chave'] == 'gatewayIncluir']
            ok(len(det) == 1 and 'Incluir o gateway “Stone da loja 2” (Outro)' in det[0] and 'Desk Brands, Desk Tech' in det[0] and 'nasce com ele' in det[0], 'o Registro de atividades guarda o que entrou: o gateway, as lojas e que a conta nasce com ele: %s' % det)
            g = gw(4)
            ok(len(gws()) == 4 and g['descricao'] == 'Stone da loja 2' and g['tipo'] == 'outro' and g['lojas'] == [2, 3] and g['situacao'] == 'desabilitado', 'o gateway novo é gravado com id 4, tipo, lojas e situação: %s' % {k: g[k] for k in ('id', 'tipo', 'lojas', 'situacao')})
            ok(g['tarifacao'] == 'especifico' and g['diaDebito'] == 12 and g['categoriaTarifaId'] == 17 and g['cnpj'] == '98.765.432/0001-10' and g['endereco'] == 'Rua Teste, 10' and g['municipio'] == 'Fortaleza',
               'tarifação, dia do débito, categoria das tarifas e Sped gravados')
            ok(g['bandeiras'] == ['visa', 'elo'] and g['bandeiraPadrao'] == 'elo' and g['antecipacao'] == 'antecipado' and g['proximoDiaUtil'] is True and g['repassar'] == 'sim' and g['repassarAPartir'] == 3, 'bandeiras, padrão, antecipação, dia útil e repasse gravados')
            ok(len(g['condicoes']) == 27, 'as 27 condições (3 fixas e 2 bandeiras) foram gravadas')
            c2 = [c for c in g['condicoes'] if c['bandeira'] == 'visa' and c['parcelas'] == 2][0]
            ok(c2['taxa'] == 3.9 and c2['prazo'] == 28 and c2['tarifa'] == 0 and g['condicoes'][0]['tarifa'] == 1.5, 'e com números de verdade (3,9 · 28 dias · tarifa 1,5), não texto: %s' % c2)
            ok(g.get('chave') is None and 'categoriaId' not in g, 'gateway de Outro não grava chave nem categoria de recebimento')
            ok(re.search(r'\?id=4$', pg.url) is not None and txt('#tituloGw') == 'Stone da loja 2' and visivel('#menuMaisAcoes') and 'Desabilitado' in txt('#subGw'), 'depois de salvar a página passa a ser a do gateway gravado (?id=4), com o título dele e o menu de excluir')
            ok('Nenhuma alteração pendente' in txt('#infoPendente'), 'e o rodapé volta a dizer que não há alteração pendente')
            ok(any(e['chave'] == 'gatewayIncluir' and not e['senha'] and 'Stone da loja 2' in e['detalhe'] for e in log()), 'o Registro de atividades tem a inclusão, sem a marca de senha')
            # recarregar
            ir(DET, '?id=4')
            ok(txt('#tituloGw') == 'Stone da loja 2' and pg.input_value('#gwDescricao') == 'Stone da loja 2' and txt('#gwTipo .dropdown-select-label') == 'Outro' and txt('#gwSituacao .dropdown-select-label') == 'Desabilitado' and
               txt('#gwLojas .dropdown-select-label') == 'Desk Brands, Desk Tech', 'recarregar traz tudo do topo: tipo, descrição, situação e lojas')
            ok(txt('#gwTarifacao .dropdown-select-label') == 'Em dia específico' and pg.input_value('#gwDiaDebito') == '12' and txt('#gwCategoriaTarifa .dropdown-select-label') == 'Taxa de cartão e gateway' and
               pg.input_value('#gwCnpj') == '98.765.432/0001-10' and pg.input_value('#gwEndereco') == 'Rua Teste, 10', 'tarifas e Sped voltam')
            ok(txt('#gwBandeiras .dropdown-select-label') == 'Visa, Elo' and txt('#gwBandeiraPadrao .dropdown-select-label') == 'Elo' and txt('#gwAntecipacao .dropdown-select-label') == 'Antecipado' and
               pg.evaluate("document.getElementById('gwProximoDiaUtil').classList.contains('on')") and txt('#gwRepassar .dropdown-select-label') == 'Sim' and txt('#gwAPartir .dropdown-select-label') == '3ª parcela', 'bandeiras, padrão, antecipação, interruptor e repasse voltam')
            ok(pg.evaluate("G.condicoes.length") == 27 and pg.evaluate("G.condicoes.filter(c => c.bandeira === 'visa' && c.parcelas === 2)[0].taxa") == '3,90' and pg.evaluate("G.condicoes[0].tarifa") == '1,50', 'e as condições voltam, com a taxa editada (3,90) e a tarifa (1,50)')
            ok('Nenhuma alteração pendente' in txt('#infoPendente'), 'recém-aberta, a página não tem alteração pendente')
            # a lista mostra
            ir(LISTA); escolher('filtroSituacao', 'todos')
            ok('Stone da loja 2' in pg.inner_text('#corpoTabela') and txt('#contagemLinhas') == '4 gateways', 'a lista mostra o gateway novo, e conta 4')
            # sair com alteracao
            ir(DET, '?id=4')
            clic('#btnVoltarLista'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            ok(modal() == '' and pg.url.endswith('pagina-integracoes-gateways.html'), 'sem alteração, "Voltar para Gateways" volta direto, sem perguntar')
            ir(DET, '?id=4'); pg.fill('#gwEndereco', 'Outra rua'); pg.wait_for_timeout(100)
            ok('alteração' in txt('#infoPendente') or 'alterações' in txt('#infoPendente'), 'mexer num campo acende o aviso do rodapé')
            clic('#btnVoltarLista'); pg.wait_for_timeout(250)
            ok('ainda não foram salvas' in modal() and pg.url.endswith('id=4'), '"Voltar para Gateways" com alteração pendente para e pergunta')
            cancelar_modal()
            ok(pg.url.endswith('id=4') and pg.input_value('#gwEndereco') == 'Outra rua', 'cancelar a pergunta fica na página, com o que foi digitado')
            clic('#btnCancelarRodape'); pg.wait_for_timeout(250)
            ok('ainda não foram salvas' in modal(), 'o "Cancelar" do rodapé pergunta também (os dois caminhos de saída)')
            confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
            ok(pg.url.endswith('pagina-integracoes-gateways.html') and gw(4)['endereco'] == 'Rua Teste, 10', 'confirmar sai para a lista e descarta o que foi mexido: nada foi gravado')
            ir(DET, '?id=4'); pg.fill('#gwEndereco', 'Rua Nova, 20'); salvar()
            ok(gw(4)['endereco'] == 'Rua Nova, 20' and any(e['chave'] == 'gatewayEditar' for e in log()), 'alterar e salvar grava, e o registro tem a ação gatewayEditar')
            ok('Nenhuma alteração pendente' in txt('#infoPendente'), 'depois de salvar não há pendência')
            # aoSalvar listagem
            param(aoSalvar='listagem'); ir(DET, '?id=4'); pg.fill('#gwEndereco', 'Rua Final, 30'); salvar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
            ok(pg.url.endswith('pagina-integracoes-gateways.html') and gw(4)['endereco'] == 'Rua Final, 30', 'com a preferência "ao salvar, ir para a listagem" a página volta para a lista depois de gravar')
            param()
            # id que nao existe
            ir(DET, '?id=99')
            ok(txt('#tituloGw') == 'Gateway não encontrado' and visivel('#avisoSemId') and not visivel('#formGateway') and 'Não existe gateway com este endereço' in txt('#avisoSemIdTexto'), 'um id que não existe diz isso e não mostra gateway nenhum')
            ir(DET)
            ok(visivel('#avisoSemId') and not visivel('#formGateway'), 'sem id e sem ?novo=1 a página também não inventa um gateway')
            # excluir
            ir(DET, '?id=4'); pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(100); clic('#itemExcluir'); pg.wait_for_timeout(300)
            m = modal()
            ok('Excluir o gateway “Stone da loja 2”' in m and 'conta financeira “Stone da loja 2”' in m and 'sai junto' in m and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"),
               'excluir pede senha e diz que a conta financeira sai junto: %s' % m[:90])
            pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
            ok(len(gws()) == 4 and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('has-error')"), 'confirmar sem a senha é barrado, e nada sai')
            pg.fill('#inputSenhaModal', 'x'); clic('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            ok(len(gws()) == 3 and all(x['id'] != 4 for x in gws()) and pg.url.endswith('pagina-integracoes-gateways.html'), 'com a senha o gateway sai e a página volta para a lista')
            ok(any(e['chave'] == 'gatewayExcluir' and e['senha'] for e in log()), 'a exclusão entra no registro, com senha')
            ir(DET, '?id=4')
            ok(visivel('#avisoSemId'), 'o endereço do gateway excluído diz que ele não existe mais')
            # senha ligada ou desligada pela tela de Confirmacoes
            limpar(confirmacoes=dict(gatewayExcluir=False)); ir(DET, '?id=3'); pg.click('#menuMaisAcoes .dropdown-select-btn'); clic('#itemExcluir'); pg.wait_for_timeout(300)
            ok(modal() != '' and not pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'com a senha desligada em Confirmações de senha, a exclusão abre o painel sem o campo de senha')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
            ok(len(gws()) == 2 and any(e['chave'] == 'gatewayExcluir' and not e['senha'] for e in log()), 'e o registro grava a exclusão sem a marca de senha')
            limpar(confirmacoes=dict(gatewayChave=False)); ir(DET, '?id=1'); clic('#btnTrocarChave'); pg.fill('#gwChave', CHAVE_NOVA); clic('#btnSalvarGw'); pg.wait_for_timeout(300)
            ok(gw(1)['chave'] == CHAVE_NOVA and not modal() and any(e['chave'] == 'gatewayChave' and not e['senha'] for e in log()), 'com a senha da chave desligada a troca salva direto, e o registro grava sem a marca de senha')
            # mudar de InfinityPay para Outro apaga a chave
            limpar(); ir(DET, '?id=1'); escolher('gwTipo', 'outro'); escolher('gwCategoriaTarifa', '17'); clic('#btnSalvarGw'); pg.wait_for_timeout(300)
            ok('A chave da API que está guardada é apagada' in modal() and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('on')"), 'trocar um InfinityPay para Outro avisa que a chave guardada é apagada, e pede senha')
            confirmar()
            g = gw(1)
            ok(g['tipo'] == 'outro' and 'chave' not in g and 'categoriaId' not in g and g['descricao'] == 'InfinityPay — loja virtual', 'e o gateway grava como Outro, sem a chave nem os campos de InfinityPay, com a descrição que tinha')
            # gateway novo InfinityPay completo
            limpar(); novo('infinitypay', 'InfinityPay da loja 3', lojas=('3',))
            pg.fill('#gwJuros', '1,5'); pg.fill('#gwMulta', '2'); pg.fill('#gwDiasMulta', '5'); clic('#gwCalculaAtraso'); escolher('gwBaixa', 'pagamento')
            salvar()
            ok(len(gws()) == 4 and gw(4)['chave'] == CHAVE_NOVA, 'InfinityPay novo com chave: o painel de senha foi confirmado e a inclusão gravou')
            g = gw(4)
            ok(g['tipo'] == 'infinitypay' and g['categoriaId'] == 1 and g['contaCreditoId'] == 2 and g['juros'] == 1.5 and g['multa'] == 2 and g['diasMulta'] == 5 and g['calculaAtraso'] is True and g['baixa'] == 'pagamento' and g['lojas'] == [3],
               'os campos de InfinityPay gravam: categoria, conta para crédito, juros, multa, dias, interruptor e data da baixa')
            ok(any(e['chave'] == 'gatewayChave' and e['senha'] for e in log()), 'a inclusão com chave passa pela ação gatewayChave, com senha')

        # ================================================================== [6] a conta financeira
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 5 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(6, 'A conta financeira do gateway: nasce, renomeia, acompanha a situação e some ao excluir'):
        try:
            limpar(); ir(LISTA)
            ir(CONTAS)
            nomes = pg.evaluate("Array.from(document.querySelectorAll('#listaContas .cf-nome')).map(e => e.textContent)")
            ok('InfinityPay — loja virtual' in nomes and 'Stone — maquininha da loja' in nomes and 'Cielo (antiga)' not in nomes, 'com o exemplo de fábrica, Contas financeiras mostra a conta de cada gateway habilitado (a da Cielo, desabilitada, não está em "Ativas")')
            ok(all(n in nomes for n in ('Caixa', 'Banco Inter — conta corrente', 'Mercado Pago', 'Cofre da loja', 'Conta teste')) and len(nomes) == 7, 'as contas de sempre continuam (cinco ativas) e as dos gateways vêm depois: %d contas' % len(nomes))
            linha = pg.evaluate("Array.from(document.querySelectorAll('#listaContas tbody tr')).filter(t => t.textContent.indexOf('Stone') >= 0)[0].innerText")
            ok('GATEWAY' in linha.upper() and 'criada pelo gateway' in linha and 'Stone — maquininha da loja' in linha, 'a conta diz o tipo (gateway) e "criada pelo gateway <descrição>": %s' % linha.replace(chr(10), ' | ')[:120])
            href = pg.evaluate("Array.from(document.querySelectorAll('#listaContas tbody tr')).filter(t => t.textContent.indexOf('Stone') >= 0)[0].querySelector('a.cf-link').getAttribute('href')")
            ok(href == '../integracoes/pagina-integracoes-gateways-detalhe.html?id=2', 'e tem o link para a página do gateway: %s' % href)
            ok(pg.evaluate("document.querySelector('#listaContas tbody tr[data-gw]').style.cursor") != 'pointer', 'a linha da conta do gateway não abre o painel de edição: é só leitura')
            pg.evaluate("document.querySelector('#listaContas tbody tr[data-gw]').click()"); pg.wait_for_timeout(200)
            ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'clicar nela não abre o painel de conta')
            pg.click("#listaContas a.cf-link"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            ok(re.search(r'pagina-integracoes-gateways-detalhe\.html\?id=1$', pg.url) is not None and txt('#tituloGw') == 'InfinityPay — loja virtual', 'o link leva ao gateway certo')
            ok(txt('#gwConta') == 'InfinityPay — loja virtual' and 'ver em Contas financeiras' in txt('#gwContaHint'), 'e a página do gateway leva de volta às Contas financeiras')
            ir(CONTAS); pg.fill('#campoBusca', 'cielo'); pg.wait_for_timeout(100)
            ok(pg.evaluate("document.querySelectorAll('#listaContas tbody tr').length") == 0, 'a conta da Cielo (desabilitada) não está nas Ativas')
            escolher('filtroSituacao', 'inativo')
            ok(pg.evaluate("Array.from(document.querySelectorAll('#listaContas .cf-nome')).map(e => e.textContent)") == ['Cielo (antiga)'], 'ela está nas Inativas: a conta acompanha a situação do gateway')
            # nasce ao salvar
            limpar(); novo('outro', 'Conta que nasce', lojas=('1',))
            ir(CONTAS)
            ok('Conta que nasce' not in pg.inner_text('#listaContas'), 'antes de salvar o gateway a conta não existe')
            novo('outro', 'Conta que nasce', lojas=('1',)); salvar()
            ir(CONTAS)
            ok('Conta que nasce' in pg.inner_text('#listaContas'), 'depois de salvar o gateway a conta nasce, com o nome dele')
            # renomeia
            ir(DET, '?id=4'); pg.fill('#gwDescricao', 'Conta renomeada')
            ok('O nome da conta muda ao salvar' in txt('#gwContaHint') and txt('#gwConta') == 'Conta renomeada', 'mudar a descrição mostra na hora o nome novo da conta, e diz que ele muda ao salvar')
            salvar()
            ir(CONTAS)
            ok('Conta renomeada' in pg.inner_text('#listaContas') and 'Conta que nasce' not in pg.inner_text('#listaContas'), 'a conta muda de nome quando a descrição muda: o nome antigo some')
            ok(gw(4)['id'] == 4 and len([g for g in gws() if g['descricao'] == 'Conta renomeada']) == 1, 'e é o mesmo gateway (id 4), não um novo')
            # situacao
            ir(DET, '?id=4'); escolher('gwSituacao', 'desabilitado'); salvar()
            ir(CONTAS)
            ok('Conta renomeada' not in pg.inner_text('#listaContas'), 'desabilitar o gateway tira a conta das Ativas')
            escolher('filtroSituacao', 'todos')
            ok('Conta renomeada' in pg.inner_text('#listaContas'), 'e ela continua em Todas')
            # busca na conta
            pg.fill('#campoBusca', 'renomeada')
            ok(pg.evaluate("document.querySelectorAll('#listaContas tbody tr').length") == 1, 'a busca de Contas financeiras acha a conta do gateway pelo nome')
            # exclui
            ir(DET, '?id=4'); pg.click('#menuMaisAcoes .dropdown-select-btn'); clic('#itemExcluir'); pg.wait_for_timeout(250); confirmar(); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)
            ir(CONTAS); escolher('filtroSituacao', 'todos')
            ok('Conta renomeada' not in pg.inner_text('#listaContas'), 'excluir o gateway tira a conta dele de Contas financeiras')
            ok(len(pg.evaluate("Array.from(document.querySelectorAll('#listaContas .cf-nome')).map(e => e.textContent)")) == 9, 'e sobram as 6 de sempre mais as 3 dos gateways do exemplo (a conta antiga do Bradesco aparece em Todas)')
            # nome com html nao quebra a tela
            limpar(); novo('outro', 'Maquininha <b>x</b>', lojas=('1',)); salvar()
            ir(CONTAS); escolher('filtroSituacao', 'todos')
            ok('Maquininha <b>x</b>' in pg.inner_text('#listaContas') and pg.evaluate("document.querySelectorAll('#listaContas .cf-nome b').length") == 0, 'um nome com marca de página aparece como texto: não vira código na tela de Contas financeiras')
            ir(LISTA); escolher('filtroSituacao', 'todos')
            ok('Maquininha <b>x</b>' in pg.inner_text('#corpoTabela') and pg.evaluate("document.querySelectorAll('#corpoTabela b').length") == 0, 'e na lista de gateways também')
            # as outras telas seguem na lista fixa
            ir(CONTAS)
            fixas = pg.evaluate("CONTAS.map(c => [c.id, c.nome])")
            ok(len(fixas) == 6 and all(not str(c[0]).startswith('gw') for c in fixas), 'a lista fixa de Contas financeiras continua com as seis contas de sempre: os gateways entram só na tela')
            ir('pagina-configuracoes-formas-recebimento.html')
            espelho = pg.evaluate("CONTAS_FINANCEIRAS.map(c => c.nome)")
            ok('Maquininha <b>x</b>' not in espelho and not any('gateway' in n.lower() for n in espelho), 'o espelho de Formas de Recebimento não ganhou a conta do gateway (é a entrega 2): %s' % espelho)

        # ================================================================== [7] menu, bloco, catalogo, espelhos, exemplo, barra e temas
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 6 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    if secao(7, 'O menu, o bloco comum, o catálogo, os espelhos, o exemplo, a barra de rolagem e os dois temas'):
        try:
            DESTINO = '../integracoes/pagina-integracoes-gateways.html'
            sem_destino = []
            for c in localiza.caminhos():
                t = open(c, encoding='utf-8').read()
                if 'data-label="Gateways de Pagamento"' not in t:
                    continue
                achados = re.findall(r'<div class="flyout-item" data-label="Gateways de Pagamento"([^>]*)>', t)
                if not achados or any(('data-href="%s"' % DESTINO) not in a for a in achados):
                    sem_destino.append(_os.path.basename(c))
            ok(not sem_destino, 'o item "Gateways de Pagamento" tem destino em todas as telas: %s' % sem_destino[:4])
            ok(len([c for c in localiza.caminhos() if 'data-label="Gateways de Pagamento"' in open(c, encoding='utf-8').read()]) == len(localiza.caminhos()) == 88, 'e o item existe nas 88 telas, as duas novas inclusive')
            limpar(); ir(VALE)
            pg.evaluate("document.querySelector('.nav-item[data-id=integracoes]').click()"); pg.wait_for_timeout(200)
            pg.evaluate("document.querySelector('#flyout-integracoes .flyout-item[data-label=\"Gateways de Pagamento\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
            ok(pg.url.endswith('/integracoes/pagina-integracoes-gateways.html') and txt('h1') == 'Gateways', 'clicar no item do menu abre a lista de Gateways')
            ok(pg.evaluate("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'integracoes' and 'Gateways de Pagamento' in txt('#breadcrumb'), 'o menu marca Integrações e o caminho diz Integrações › Gateways de Pagamento')
            ir(DET, '?id=2')
            ok(pg.evaluate("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'integracoes' and 'Stone — maquininha da loja' in txt('#breadcrumb'), 'a página do gateway também, com o nome dele no fim do caminho')
            # o bloco
            INI, FIM = '  // ===== GATEWAYS: DADOS E REGRAS', '  // ===== FIM DO BLOCO GATEWAYS ====='
            a, b = fonte(LISTA), fonte(DET)
            ok(a[a.index(INI):a.index(FIM)] == b[b.index(INI):b.index(FIM)] and 'function gwCondicoesFabrica(' in a, 'o bloco de dados e regras é idêntico na lista e na página do gateway')
            ok(a.count('const GW_LOJAS') == 1 and b.count('const GW_LOJAS') == 1 and 'deskGateways' in fonte(CONTAS), 'cada tela tem o bloco uma vez; Contas financeiras lê a mesma chave')
            ok('shortcut:' in a[a.index(INI):a.index(FIM)] and 'servidor como segredo' in a[a.index(INI):a.index(FIM)], 'a chave da API no navegador está marcada como shortcut, com o que a produção faz')
            ok('nao entram no saldo' in fonte(CONTAS), 'Contas financeiras diz, no código, por que a conta do gateway não entra no saldo')
            ok('no prototipo nao ha lancamento numa conta de gateway' in a, 'e o bloco diz, num shortcut, que excluir o gateway não confere lançamentos porque no protótipo não há (na produção bloqueia)')
            # catalogo
            carregam = [c for c in localiza.caminhos() if "chave:'valeCompraReativar'" in open(c, encoding='utf-8').read()]
            com4 = [_os.path.basename(c) for c in carregam if len(re.findall(r"chave:'gateway(?:Incluir|Editar|Chave|Excluir)'", open(c, encoding='utf-8').read())) == 4]
            ok(len(carregam) >= 19 and len(com4) == len(carregam), 'as quatro ações de gateway estão no catálogo de todas as telas que o carregam (%d de %d)' % (len(com4), len(carregam)))
            ok(all(('chave:\'gateway%s\'' % x) in a for x in ('Incluir', 'Editar', 'Chave', 'Excluir')), 'e nas duas telas novas')
            ir(DET, '?id=1')
            acoes = pg.evaluate("ACOES_SENHA.filter(a => a.chave.indexOf('gateway') === 0).map(a => [a.chave, a.exigePadrao, a.grupo])")
            ok(acoes == [['gatewayIncluir', False, 'Integrações'], ['gatewayEditar', False, 'Integrações'], ['gatewayChave', True, 'Integrações'], ['gatewayExcluir', True, 'Integrações']],
               'incluir e alterar não pedem senha de fábrica; trocar a chave e excluir pedem: %s' % acoes)
            ir(SENHAS)
            ok('gatewayChave' in fonte(SENHAS) and 'Guardar, trocar ou apagar a chave da API de um gateway' in pg.evaluate("document.body.textContent") and 'Excluir gateway de pagamento' in pg.evaluate("document.body.textContent"),
               'a tela de Confirmações de senha mostra as ações de gateway, sob o grupo Integrações')
            ir(REGISTRO)
            ok('gatewayExcluir' in fonte(REGISTRO), 'e o Registro de atividades conhece as quatro')
            # espelhos
            ir(LOJAS_CAD)
            ok(pg.evaluate("LOJAS.map(l => [l.id, l.nome])") == [[1, 'Desk Shope'], [2, 'Desk Brands'], [3, 'Desk Tech']], 'Lojas Desk tem as três lojas')
            ir(LISTA)
            ok(pg.evaluate("JSON.stringify(GW_LOJAS)") == '{"1":"Desk Shope","2":"Desk Brands","3":"Desk Tech"}', 'o espelho de lojas dos gateways é o de Lojas Desk')
            gw_cat_r, gw_cat_d = pg.evaluate("GW_CATEGORIAS_RECEITA"), pg.evaluate("GW_CATEGORIAS_DESPESA")
            gw_contas, gw_fixas = pg.evaluate("GW_CONTAS_CREDITO"), pg.evaluate("GW_CONTAS_FIXAS")
            ir(CATS)
            cats = pg.evaluate("CATEGORIAS.map(c => [c.id, c.descricao, c.ativo, c.grupoId])")
            mapa = dict((c[0], c) for c in cats)
            ok(all(x['id'] in mapa and mapa[x['id']][1] == x['nome'] and mapa[x['id']][2] for x in gw_cat_r + gw_cat_d), 'as categorias dos gateways (receita e despesa) existem em Categorias financeiras, com o mesmo nome e ativas')
            ok(all(mapa[x['id']][3] in (1, 0) for x in gw_cat_r) and all(mapa[x['id']][3] != 1 for x in gw_cat_d), 'as de receita são do grupo Receitas de vendas (ou sem grupo) e as de despesa não são')
            ok(not set(x['id'] for x in gw_cat_r) & set(x['id'] for x in gw_cat_d), 'nenhuma categoria é receita e despesa ao mesmo tempo')
            ir(CONTAS)
            contas = pg.evaluate("CONTAS.map(c => [c.id, c.nome, c.ativo, c.bancaria])")
            ok([[c['id'], c['nome']] for c in gw_contas] == [[c[0], c[1]] for c in contas if c[2] and c[3]], 'as contas para crédito são as contas bancárias ativas de Contas financeiras')
            ok(gw_fixas == [c[1] for c in contas], 'e a lista de nomes que a descrição não pode repetir é a de todas as contas fixas')
            # o gravado vence o exemplo
            limpar(); ir(LISTA)
            pg.evaluate("(() => { const l = gwLer().filter(g => g.id !== 1); l.forEach(g => { if (g.id === 2) g.descricao = 'Stone renomeada'; }); gwGravar(l); })()")
            ir(LISTA); escolher('filtroSituacao', 'todos')
            ok(sorted(g['descricao'] for g in gws()) == ['Cielo (antiga)', 'Stone renomeada'] and 'InfinityPay' not in pg.inner_text('#corpoTabela'), 'o que está gravado vence o exemplo: gateway excluído não volta e o renomeado continua renomeado')
            pg.evaluate("localStorage.removeItem('deskGatewaysExemplo')"); ir(LISTA)
            ok(len(gws()) == 5 and sum(1 for g in gws() if g['descricao'] == 'Stone renomeada') == 1, 'sem a marca de exemplo, o exemplo é acrescentado sem apagar nem duplicar o que já havia (5 gateways, com ids novos)')
            ok(len(set(g['id'] for g in gws())) == 5, 'e os ids continuam únicos')
            pg.evaluate("localStorage.setItem('deskGateways', '{ isto nao e json')"); ir(LISTA)
            ok(visivel('#emptyState') and txt('#emptyTitulo') == 'Nenhum gateway cadastrado', 'dado gravado estragado: a lista abre vazia, sem erro')
            ir(DET, '?novo=1')
            pg.evaluate("window.__s = Storage.prototype.setItem; Object.defineProperty(Storage.prototype, 'setItem', { configurable: true, writable: true, value: function () { throw new Error('bloqueado'); } })")
            escolher('gwTipo', 'outro'); marcar('menuGwLojas', '1'); escolher('gwCategoriaTarifa', '17'); clic('#btnSalvarGw'); pg.wait_for_timeout(300)
            ok('Não foi possível gravar o gateway neste navegador' in modal(), 'se o navegador bloqueia o armazenamento, a tela diz que não gravou, em vez de fingir')
            pg.evaluate("Object.defineProperty(Storage.prototype, 'setItem', { configurable: true, writable: true, value: window.__s })")
            # barra de rolagem
            limpar()
            sem_barra = {}
            for larg in (1280, 1440):
                pg.set_viewport_size({'width': larg, 'height': 900})
                ir(LISTA); sem_barra['lista %d' % larg] = pg.evaluate(MEDE)
                ir(DET, '?id=2'); pg.evaluate("gruposDaTabela().forEach(gr => { ESTADO_GRUPOS[gr.chave] = true; }); aplicarGrupos()"); sem_barra['página do Stone (99 linhas abertas) %d' % larg] = pg.evaluate(MEDE)
                ir(DET, '?id=1'); sem_barra['página da InfinityPay %d' % larg] = pg.evaluate(MEDE)
                ir(CONTAS); sem_barra['contas financeiras %d' % larg] = pg.evaluate(MEDE)
            pg.set_viewport_size({'width': 1440, 'height': 900})
            ruim = dict((k, v) for k, v in sem_barra.items() if v)
            ok(not ruim, 'nenhuma das telas tem barra de rolagem a 1280 e a 1440, nem a tabela de 99 linhas aberta: %s' % (ruim or 'todas limpas'))
            # os dois temas
            for tema in ('light', 'dark'):
                param(tema=tema)
                for tela, q in ((LISTA, ''), (DET, '?id=1'), (DET, '?novo=1')):
                    ir(tela, q)
                    ok(pg.evaluate("document.body.classList.contains('dark')") == (tema == 'dark'), 'tema %s: %s abre no tema certo' % (tema, tela.replace('pagina-integracoes-', '')))
            param()
            # os dropdowns abrem para baixo
            ir(DET, '?id=1')
            for ident in ('gwTipo', 'gwSituacao', 'gwCategoria', 'gwLojas', 'gwBandeiras', 'gwRepassar'):
                pg.evaluate("document.querySelector('#%s .dropdown-select-btn').click()" % ident); pg.wait_for_timeout(120)
                abre_baixo = pg.evaluate("(() => { const m = document.querySelector('#%s .dropdown-select-menu'); const b = document.querySelector('#%s .dropdown-select-btn'); return m.classList.contains('open') && !m.classList.contains('abrir-para-cima') && m.getBoundingClientRect().top >= b.getBoundingClientRect().bottom - 1; })()" % (ident, ident))
                ok(abre_baixo, 'o dropdown %s abre para baixo' % ident)
            pg.evaluate("document.querySelector('#gwLojas .dropdown-select-btn').click()"); pg.wait_for_timeout(120)
            ok(pg.evaluate("document.querySelectorAll('.dropdown-select-menu.open').length") == 1, 'abrir um dropdown fecha os outros')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(120)
            ok(pg.evaluate("document.querySelectorAll('.dropdown-select-menu.open').length") == 0, 'Esc fecha o dropdown aberto')
            # a caixa de marcar de Vale para nao fecha ao marcar
            pg.evaluate("document.querySelector('#gwLojas .dropdown-select-btn').click()"); pg.wait_for_timeout(100)
            pg.evaluate("document.querySelector('#menuGwLojas input[value=\"3\"]').click()"); pg.wait_for_timeout(100)
            ok(pg.evaluate("document.querySelector('#menuGwLojas').classList.contains('open')") and txt('#gwLojas .dropdown-select-label') == 'Todas as lojas', 'marcar uma loja não fecha o menu, e as três dizem "Todas as lojas"')
        except Exception as e:   # uma secao que para por erro de navegador e falha, e nao derruba o resumo
            ok(False, 'a seção 7 parou por erro: %s: %s' % (type(e).__name__, str(e).split(chr(10))[0][:150]))

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
