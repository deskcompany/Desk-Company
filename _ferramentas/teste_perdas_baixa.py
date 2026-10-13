# -*- coding: utf-8 -*-
# Tratamento de Perdas: o zero e os motivos da baixa (pedido do usuario em 12/out/2026).
#
#   [1] os campos de "O que fazer" abrem em branco, e o zero DIGITADO e resposta: 0 em "Volta para a
#       venda" quer dizer que nada foi recuperado, e a linha vai para a baixa por perda, que pede o
#       motivo. Antes o campo mostrava um "0" que nao era valor, e confirmar era barrado;
#   [2] o motivo da perda e o da operacao que criou o bloqueio: transferencia, conferencia de
#       entrada, separacao e conferencia de saida. Vem antes dos gerais;
#   [3] o cadastro de Motivos de Perda guarda em que baixa cada motivo aparece, e a tela de
#       Tratamento de Perdas carrega a mesma lista. O Acerto de Estoque so oferece os gerais.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

PERDAS, CADASTRO, ACERTO = 'pagina-estoque-itens-bloqueados.html', 'pagina-configuracoes-motivos-perda.html', 'pagina-estoque-acerto.html'
GUARDADO = ['deskBloqueados', 'deskBloqueiosEntrada', 'deskParametros', 'deskLog', 'deskTransferencias']
GERAIS = ['Quebra ou avaria', 'Perda', 'Furto ou roubo', 'Extravio', 'Consumo próprio', 'Deterioração ou vencimento', 'Correção de lançamento']
DA_OPERACAO = {
    'transferencia': ['Perda em trânsito', 'Avaria no percurso', 'Furto ou roubo no trajeto'],
    'entrada': ['Avaria do fornecedor', 'Avaria no recebimento', 'Avaria no transporte da compra'],
    'saida': ['Avaria na separação', 'Avaria no picking', 'Avaria na embalagem', 'Não encontrado no endereço'],
}
SO = (sys.argv[1:] or [''])[0]

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def secao(n, titulo):
    if SO and SO != str(n):
        return False
    print('\n[%d] %s' % (n, titulo))
    return True


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, query=''):
        pg.goto(localiza.http(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def do_zero(caixa=None):
        """A fila na semente; `caixa` e o que as outras telas deixaram para bloquear."""
        ir(PERDAS)
        pg.evaluate("([chaves, c]) => { chaves.forEach(k => localStorage.removeItem(k)); if (c) localStorage.setItem('deskBloqueiosEntrada', JSON.stringify(c)); }", [GUARDADO, caixa])
        ir(PERDAS)

    def clic(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def visivel(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null; }", sel)

    def texto(sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; }", sel)

    def abrir(id_):
        clic('#corpoTabela tr[data-id="%d"]' % id_); pg.wait_for_timeout(400)

    def fechar_painel():
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)

    def digitar(campo, valor):
        pg.fill('#' + campo, valor); pg.wait_for_timeout(160)

    def campos():
        return [pg.input_value('#resLiberar'), pg.input_value('#resBaixar'), pg.inner_text('#resResto')]

    def escolher(raiz, valor):
        clic('#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(120)
        pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, valor])
        pg.wait_for_timeout(220)

    def confirmar_modal():
        dito = pg.inner_text('#confirmModalTexto') if pg.locator('#confirmModal.open').count() else ''
        if pg.locator('#confirmModal.open').count():
            if visivel('#campoSenhaModal'):
                pg.fill('#inputSenhaModal', 'senha-de-teste')
            clic('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)
        return dito

    def motivos_oferecidos():
        return pg.evaluate("Array.from(document.querySelectorAll('#resPerda .dropdown-select-item')).map(e => e.textContent.trim()).filter(t => t !== 'Selecione o motivo')")

    def id_de(doc):
        return pg.evaluate("(d) => (ITENS.find(i => i.doc === d) || {}).id", doc)

    DE_FORA = {
        'transf:TR-0101:CAB-HDM-009:falta:1': {'chave': 'transf:TR-0101:CAB-HDM-009:falta:1', 'sku': 'CAB-HDM-009', 'produto': 'Cabo HDMI 2.1 · 2m', 'un': 'UN', 'dep': 3, 'qtd': 2,
                                               'motivo': 'falta', 'origem': 'conferencia_entrada', 'doc': 'TR-0101', 'quem': 'Administrador Desk', 'obs': 'Não chegou na transferência TR-0101.'},
        'conf:24:KIT-COZ-006': {'chave': 'conf:24:KIT-COZ-006', 'sku': 'KIT-COZ-006', 'produto': 'Kit utensílios de cozinha 6 peças', 'un': 'UN', 'dep': 2, 'qtd': 1,
                                'motivo': 'falta', 'origem': 'conferencia_saida', 'doc': 'Pedido #24', 'quem': 'Ana Souza', 'obs': ''},
    }

    if secao(1, 'Os campos abrem em branco, e o zero digitado e resposta'):
        do_zero()
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        abrir(1)
        vazio = pg.evaluate("['resLiberar', 'resBaixar'].map(id => { const c = document.getElementById(id); return [c.value, c.getAttribute('placeholder') || '']; })")
        ok(vazio == [['', ''], ['', '']], 'os dois campos abrem em branco, sem o "0" que parecia valor: %s' % vazio)
        ok('Se nada voltou, digite 0' in texto('#wrapResLiberar'), 'e a linha de "Volta para a venda" diz o que o zero quer dizer')
        # O mesmo defeito na ficha da Separacao: la tambem zero e resposta ("nao achei nenhuma"), e o campo vazio mostrava um "0" cinza.
        ficha = open(localiza.onde('pagina-logistica-separacao-detalhe.html'), encoding='utf-8').read()
        campo = ficha[ficha.index('data-qtd="'):][:160]
        ok('placeholder="0"' not in campo and "i.separado === null ? ''" in campo, 'na ficha da Separacao, o campo de "quantidade que voce achou" tambem abre em branco')
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(250)
        ok(visivel('#erroTriagem') and 'Se nada voltou, digite 0' in pg.inner_text('#erroTriagem') and pg.locator('#confirmModal.open').count() == 0,
           'confirmar em branco continua barrado, e a mensagem ensina o zero: %s' % pg.inner_text('#erroTriagem'))
        digitar('resLiberar', '0')
        ok(campos() == ['0', '1', '0 UN'] and not visivel('#erroTriagem'), 'digitar 0 em "Volta para a venda" manda a linha inteira para a baixa: %s' % campos())
        ok(visivel('#avisoZero') and pg.inner_text('#avisoZero') == 'Nada voltou para a venda: 1 UN vai para a baixa por perda. Informe o motivo.' and visivel('#wrapPerda') and pg.inner_text('#btnConfirmarResolver') == 'Dar baixa',
           'a tela diz o que entendeu, pede o motivo, e o botao vira "Dar baixa": %s' % pg.inner_text('#avisoZero'))
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(250)
        ok(visivel('#erroPerda') and pg.locator('#confirmModal.open').count() == 0, 'sem o motivo da perda, a baixa nao segue')
        digitar('resLiberar', '1')
        ok(campos() == ['1', '', '0 UN'] and not visivel('#avisoZero') and pg.inner_text('#btnConfirmarResolver') == 'Liberar para venda', 'trocar o zero por outro numero tira a baixa que o zero tinha posto: %s' % campos())
        fechar_painel()

        abrir(7)   # 8 unidades
        digitar('resLiberar', '0')
        ok(campos() == ['0', '8', '0 UN'] and '8 UN vão para a baixa' in pg.inner_text('#avisoZero'), 'com mais de uma unidade, o zero leva todas: %s' % campos())
        digitar('resBaixar', '3')
        ok(campos() == ['0', '3', '5 UN'] and not visivel('#avisoZero'), 'a baixa posta pelo zero pode ser corrigida a mao, e o que sobra continua bloqueado: %s' % campos())
        digitar('resLiberar', '2')
        ok(campos() == ['2', '3', '3 UN'], 'e baixa digitada a mao nao some quando o outro campo muda: %s' % campos())
        digitar('resLiberar', '0'); digitar('resBaixar', '0')
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(250)
        ok(visivel('#erroTriagem') and 'Zero nas duas saídas' in pg.inner_text('#erroTriagem') and 'Manter bloqueado' in pg.inner_text('#erroTriagem'), 'zero nas duas saidas nao resolve nada, e a tela diz para onde ir: %s' % pg.inner_text('#erroTriagem'))
        digitar('resBaixar', ''); digitar('resLiberar', '0')
        clic('#btnLiberarTudo'); pg.wait_for_timeout(200)
        ok(campos() == ['8', '', '0 UN'], '"tudo" em "Volta para a venda" desfaz a baixa que o zero tinha posto: %s' % campos())
        fechar_painel()

        abrir(4)   # Cabo HDMI, 3 UN, avaria da conferencia de entrada
        digitar('resLiberar', '0'); escolher('resPerda', 'entrada_fornecedor')
        ok('baixa por avaria do fornecedor exige NF-e própria' in pg.inner_text('#resPrevia'), 'escolhido o motivo, a previa diz o que a baixa obriga: %s' % pg.inner_text('#resPrevia')[55:130])
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(350)
        dito = confirmar_modal()
        ok(dito == 'Cabo HDMI 2.1 · 2m: dar baixa em 3 UN por avaria do fornecedor, no acerto de saída AC-0051.', 'a confirmacao diz o que vai acontecer: %s' % dito)
        aviso = pg.inner_text('#confirmModalTexto') if pg.locator('#confirmModal.open').count() else ''
        confirmar_modal()
        registro = pg.evaluate("RESOLVIDOS.filter(r => r.sku === 'CAB-HDM-009').map(r => [r.desfecho, r.qtd, r.motivoPerda, r.acerto])")
        ok(registro == [['baixado', 3, 'Avaria do fornecedor', 'AC-0051']] and pg.evaluate("!ITENS.some(i => i.id === 4)") and 'por avaria do fornecedor' in aviso,
           'a baixa fica registrada com o motivo da operacao, e a linha sai da fila: %s' % registro)

    if secao(2, 'O motivo da perda e o da operacao que criou o bloqueio'):
        do_zero(DE_FORA)
        ok(not erros, 'a tela abre sem erro de JavaScript: %s' % erros[:2])
        casos = [(1, 'entrada', 'conferência de entrada', 'nota de entrada'), (5, 'saida', 'separação e conferência de saída', 'separacao'),
                 (id_de('Pedido #24'), 'saida', 'separação e conferência de saída', 'conferencia de saida'), (id_de('TR-0101'), 'transferencia', 'transferência entre estoques', 'transferencia')]
        for idn, op, nome, rotulo in casos:
            abrir(idn)
            vistos, dica = motivos_oferecidos(), texto('#dicaMotivoOperacao') or ''
            ok(vistos == DA_OPERACAO[op] + GERAIS, 'bloqueio que veio de %s: a baixa oferece primeiro os motivos dela: %s' % (rotulo, vistos[:len(DA_OPERACAO[op])]))
            ok(dica.endswith(nome + '.'), '  e a tela diz de que operacao sao: %s' % dica[-50:])
            fechar_painel()
        for idn, rotulo in [(2, 'acerto de estoque'), (6, 'bloqueio manual')]:
            abrir(idn)
            ok(motivos_oferecidos() == GERAIS and pg.locator('#dicaMotivoOperacao').count() == 0, 'bloqueio de %s nao tem operacao: so os motivos gerais' % rotulo)
            fechar_painel()

        idt = id_de('TR-0101')
        abrir(idt)
        digitar('resLiberar', '0'); escolher('resPerda', 'transito_perda')
        ok(campos() == ['0', '2', '0 UN'] and 'baixa por perda em trânsito exige NF-e própria' in pg.inner_text('#resPrevia'), 'a falta da transferencia que nao apareceu: zero, e o motivo e "Perda em trânsito"')
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(350)
        dito = confirmar_modal(); confirmar_modal()
        ok(dito.endswith('dar baixa em 2 UN por perda em trânsito, no acerto de saída AC-0051.') and pg.evaluate("RESOLVIDOS.some(r => r.motivoPerda === 'Perda em trânsito' && r.qtd === 2)"), 'e a baixa sai com esse motivo: %s' % dito[-70:])
        clic('#abasSituacao .aba-sit[data-sit="resolvidos"]'); pg.wait_for_timeout(300)
        ok('Perda em trânsito · AC-0051' in pg.inner_text('#corpoResolvidos'), 'no historico dos resolvidos a linha diz o motivo e o acerto')

    if secao(3, 'O cadastro guarda em que baixa o motivo aparece'):
        do_zero()
        da_tela = pg.evaluate("Object.fromEntries(Object.keys(MOTIVOS_DA_OPERACAO).map(k => [k, MOTIVOS_DA_OPERACAO[k].map(m => [m.l, m.fiscal])]))")
        ir(CADASTRO)
        ok(not erros, 'o cadastro abre sem erro de JavaScript: %s' % erros[:2])
        do_cadastro = pg.evaluate("""(() => { const r = {}; MOTIVOS.filter(m => m.status === 'ativo' && m.operacao && m.operacao !== 'todas').forEach(m => { (r[m.operacao] = r[m.operacao] || []).push([m.nome, m.destino]); }); return r; })()""")
        ok(da_tela == do_cadastro and {k: [x[0] for x in v] for k, v in da_tela.items()} == DA_OPERACAO, 'os motivos de cada operacao em Tratamento de Perdas sao os do cadastro, com o mesmo tratamento fiscal')
        ok(pg.evaluate("MOTIVOS.filter(m => m.grupo !== 'saida' && m.operacao && m.operacao !== 'todas').length") == 0 and pg.evaluate("new Set(MOTIVOS.map(m => m.nome.toLowerCase())).size === MOTIVOS.length"),
           'todo motivo de operacao e motivo de saida, e nenhum nome se repete')
        pg.evaluate("(() => { itensPorPaginaAtual = 100; renderMotivos(); })()"); pg.wait_for_timeout(250)
        cartoes = pg.evaluate("Object.fromEntries(Array.from(document.querySelectorAll('.motivo-card')).map(c => [c.querySelector('.motivo-nome').textContent, c.querySelector('.motivo-meta').textContent]))")
        ok(cartoes['Perda em trânsito'].startswith('só em Transferência entre estoques') and cartoes['Avaria no picking'].startswith('só em Separação e conferência de saída') and 'só em' not in cartoes['Furto ou roubo'],
           'a lista diz em que baixa o motivo aparece; os gerais nao dizem nada: %s' % cartoes['Perda em trânsito'][:60])
        pg.evaluate("abrirDrawerMotivo(MOTIVOS.find(m => m.nome === 'Perda em trânsito').id)"); pg.wait_for_timeout(350)
        ok(pg.get_attribute('#inputOperacao', 'data-value') == 'transferencia' and texto('#inputOperacao .dropdown-select-label') == 'Transferência entre estoques', 'abrir o motivo mostra a operacao dele')
        clic('#inputOperacao .dropdown-select-btn'); pg.wait_for_timeout(120)
        clic('#inputOperacao .dropdown-select-item[data-value="todas"]'); pg.wait_for_timeout(200)
        clic('#btnSalvarMotivo'); pg.wait_for_timeout(350); confirmar_modal()
        ok(pg.evaluate("MOTIVOS.find(m => m.nome === 'Perda em trânsito').operacao") == 'todas', 'e a operacao pode ser trocada no cadastro')
        clic('#btnNovoMotivo'); pg.wait_for_timeout(350)
        ok(pg.get_attribute('#inputOperacao', 'data-value') == 'todas' and pg.evaluate("Array.from(document.querySelectorAll('#inputOperacao .dropdown-select-item')).map(e => e.textContent)") ==
           ['Todas as baixas', 'Transferência entre estoques', 'Conferência de entrada', 'Separação e conferência de saída'], 'motivo novo nasce valendo em todas as baixas, com as quatro opcoes')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        ir(ACERTO)
        no_acerto = pg.evaluate("MOTIVOS.saida.map(m => m.l)")
        ok(no_acerto == GERAIS, 'o Acerto de Estoque continua oferecendo so os motivos de todas as baixas: %d' % len(no_acerto))

    if secao(4, 'O que se cadastra em Motivos de Perda vale na baixa'):
        # Pedido do usuario em 13/out: "para podermos fazer esses cadastros". Ate entao o cadastro vivia
        # so na tela dele, ate recarregar, e a baixa oferecia a lista de exemplo.
        do_zero()
        pg.evaluate("localStorage.removeItem('deskMotivosPerda')")
        ir(CADASTRO)
        clic('#btnNovoMotivo'); pg.wait_for_timeout(350)
        pg.fill('#inputNomeMotivo', 'Avaria na doca')
        clic('#inputOperacao .dropdown-select-btn'); pg.wait_for_timeout(120)
        clic('#inputOperacao .dropdown-select-item[data-value="entrada"]'); pg.wait_for_timeout(200)
        clic('#btnSalvarMotivo'); pg.wait_for_timeout(350); confirmar_modal()
        pg.evaluate("abrirDrawerMotivo(MOTIVOS.find(m => m.nome === 'Perda em trânsito').id)"); pg.wait_for_timeout(350)
        pg.fill('#inputNomeMotivo', 'Extravio na estrada')
        clic('#btnSalvarMotivo'); pg.wait_for_timeout(350); confirmar_modal()
        pg.evaluate("abrirDrawerMotivo(MOTIVOS.find(m => m.nome === 'Consumo próprio').id)"); pg.wait_for_timeout(350)
        clic('#inputSituacao .dropdown-select-btn'); pg.wait_for_timeout(120)
        clic('#inputSituacao .dropdown-select-item[data-value="inativo"]'); pg.wait_for_timeout(200)
        clic('#btnSalvarMotivo'); pg.wait_for_timeout(350); confirmar_modal()
        ir(CADASTRO)
        ok(pg.evaluate("MOTIVOS.some(m => m.nome === 'Avaria na doca' && m.operacao === 'entrada') && MOTIVOS.some(m => m.nome === 'Extravio na estrada') && !MOTIVOS.some(m => m.nome === 'Perda em trânsito')"),
           'o motivo criado e o renomeado continuam no cadastro depois de recarregar a tela')
        ir(PERDAS)
        pg.evaluate("(c) => localStorage.setItem('deskBloqueiosEntrada', JSON.stringify(c))", DE_FORA); ir(PERDAS)
        abrir(1)
        vistos = motivos_oferecidos()
        ok(vistos[:4] == DA_OPERACAO['entrada'] + ['Avaria na doca'], 'a baixa de um bloqueio da conferencia de entrada passa a oferecer o motivo criado: %s' % vistos[:4])
        ok('Consumo próprio' not in vistos and 'Quebra ou avaria' in vistos and 'Furto ou roubo' in vistos, 'o motivo inativado no cadastro sai da baixa; os outros gerais continuam')
        fechar_painel()
        abrir(id_de('TR-0101'))
        ok(motivos_oferecidos()[:3] == ['Extravio na estrada', 'Avaria no percurso', 'Furto ou roubo no trajeto'], 'e o motivo renomeado aparece com o nome novo: %s' % motivos_oferecidos()[:3])
        digitar('resLiberar', '0')
        pg.evaluate("document.querySelector('#resPerda .dropdown-select-btn').click()"); pg.wait_for_timeout(150)
        pg.evaluate("Array.from(document.querySelectorAll('#resPerda .dropdown-select-item')).filter(e => e.textContent.trim() === 'Extravio na estrada')[0].click()"); pg.wait_for_timeout(250)
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(350)
        dito = confirmar_modal(); confirmar_modal()
        ok(dito.endswith('dar baixa em 2 UN por extravio na estrada, no acerto de saída AC-0051.') and pg.evaluate("RESOLVIDOS.some(r => r.motivoPerda === 'Extravio na estrada')"), 'a baixa sai com o motivo do cadastro: %s' % dito[-70:])
        pg.evaluate("localStorage.setItem('deskMotivosPerda', '{\"lixo\": true}')"); ir(PERDAS)
        abrir(1)
        ok(motivos_oferecidos() == DA_OPERACAO['entrada'] + GERAIS and not erros, 'cadastro guardado ilegivel nao derruba a tela: valem os motivos de exemplo')
        fechar_painel()
        pg.evaluate("localStorage.removeItem('deskMotivosPerda')")

    if secao(5, 'A linha dos Resolvidos abre o painel do bloqueio que saiu da fila'):
        do_zero()
        clic('#abasSituacao .aba-sit[data-sit="resolvidos"]'); pg.wait_for_timeout(300)

        def resolvido(rid):
            clic('#corpoResolvidos tr[data-rid="%d"] td' % rid); pg.wait_for_timeout(400)
            r = pg.evaluate("""() => { const t = (id) => { const e = document.getElementById(id); return e ? e.textContent.trim() : null; };
                const linhas = Object.fromEntries(Array.from(document.querySelectorAll('#rvFatos .extrato-linha')).map(l => [l.querySelector('.extrato-rotulo').textContent, l.querySelector('.extrato-valor').textContent.trim()]));
                const a = document.querySelector('#rvFatos a');
                return { aberto: document.getElementById('eventDrawer').classList.contains('open'), titulo: document.getElementById('drawerTitulo').textContent,
                         desfecho: t('rvDesfecho'), qtd: t('rvQtd'), valor: t('rvValor'), parado: t('rvParado'), dep: t('rvDeposito'), linhas: linhas, link: a ? a.getAttribute('href') : null,
                         hist: Array.from(document.querySelectorAll('#rvHistorico .mov-tipo')).map(e => e.textContent) }; }""")
            pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
            return r

        ok(pg.evaluate("getComputedStyle(document.querySelector('#corpoResolvidos tr')).cursor") == 'pointer', 'a linha dos resolvidos mostra que e clicavel')
        a = resolvido(2)
        ok(a['aberto'] and a['titulo'] == 'Bloqueio resolvido' and [a['desfecho'], a['qtd'], a['valor'], a['parado'], a['dep']] == ['Liberado', '1 UN', 'R$ 512,75', '3 dias', 'Galpão Centro'],
           'liberado: o painel abre com a quantidade, o valor que voltou, os dias parado e o deposito: %s' % [a['desfecho'], a['qtd'], a['valor'], a['parado']])
        ok(a['linhas'].get('De onde veio') == 'Conferência de saída · Pedido #25' and a['linhas'].get('Bloqueado em', '').endswith('· Ana Souza') and a['linhas'].get('Liberado em', '').endswith('· Administrador Desk')
           and a['linhas'].get('O que a auditoria achou') == 'Estava no endereço: erro de conferência' and a['linhas'].get('Voltou para') == 'A-03-2-01',
           'e diz de onde veio, quem bloqueou, quem liberou, o que a auditoria achou e para onde voltou')
        ok(a['link'] == '../logistica/pagina-logistica-conferencia-saida-detalhe.html?id=25' and a['hist'] == ['Bloqueio', 'Liberação de 1 UN'], 'a origem leva ao pedido, e a historia tem o bloqueio e a liberacao: %s' % a['hist'])
        ir('pagina-logistica-conferencia-saida-detalhe.html', '?id=25')
        ok(pg.evaluate("!PEDIDO_INEXISTENTE && PEDIDO.numero === 25"), 'e a Conferencia de Saida tem o pedido 25')
        ir(PERDAS); clic('#abasSituacao .aba-sit[data-sit="resolvidos"]'); pg.wait_for_timeout(300)
        b = resolvido(1)
        ok([b['desfecho'], b['qtd'], b['valor'], b['parado']] == ['Baixado', '1 UN', 'R$ 86,20', '9 dias'] and b['linhas'].get('Motivo da perda') == 'Quebra ou avaria' and b['linhas'].get('Acerto de saída') == 'AC-0050'
           and 'NF-e' in b['linhas'].get('O que a baixa obriga', '') and b['linhas'].get('Baixado em', '').endswith('· Administrador Desk') and b['link'] is None,
           'baixado: o valor da perda, o motivo, o acerto, o que a baixa obriga e quem baixou: %s' % [b['valor'], b['parado'], b['linhas'].get('Motivo da perda')])

        # Uma baixa feita agora guarda a historia do bloqueio, com a anotacao que ele tinha.
        clic('#abasSituacao .aba-sit[data-sit="todos"]'); pg.wait_for_timeout(250)
        abrir(7); clic('#btnBaixarTudo'); pg.wait_for_timeout(200); escolher('resPerda', 'perda')
        clic('#btnConfirmarResolver'); pg.wait_for_timeout(350); confirmar_modal(); confirmar_modal()
        clic('#abasSituacao .aba-sit[data-sit="resolvidos"]'); pg.wait_for_timeout(300)
        novo = pg.evaluate("RESOLVIDOS.find(r => r.sku === 'CAM-DKB-011').id")
        c = resolvido(novo)
        ok([c['desfecho'], c['qtd'], c['valor'], c['parado']] == ['Baixado', '8 UN', 'R$ 334,40', '12 dias'] and c['hist'] == ['Bloqueio', 'Anotação', 'Baixa de 8 UN']
           and c['linhas'].get('Bloqueado em', '').endswith('· Administrador Desk'), 'baixa feita agora: 12 dias parado, e a historia traz o bloqueio, a anotacao e a baixa: %s' % c['hist'])

        # O navegador de quem ja usava a tela tem resolvidos sem a data do bloqueio.
        pg.evaluate("""() => { const e = JSON.parse(localStorage.getItem('deskBloqueados')); e.resolvidos.forEach(r => { delete r.bloqueadoEm; delete r.bloqueadoPor; delete r.notas; delete r.obsBloqueio; });
            e.resolvidos.filter(r => r.doc === 'Pedido #25').forEach(r => { r.doc = 'Pedido #19'; }); localStorage.setItem('deskBloqueados', JSON.stringify(e)); }""")
        ir(PERDAS); clic('#abasSituacao .aba-sit[data-sit="resolvidos"]'); pg.wait_for_timeout(300)
        d = resolvido(2)
        ok(d['aberto'] and d['parado'] == '—' and d['linhas'].get('Bloqueado em') == 'não registrado' and d['hist'] == ['Liberação de 1 UN'] and d['linhas'].get('De onde veio') == 'Conferência de saída · Pedido #25' and not erros,
           'resolvido guardado antes desta mudanca abre sem erro, diz que a data do bloqueio nao foi registrada, e o pedido do exemplo antigo e corrigido')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
