# -*- coding: utf-8 -*-
# Logística → Conferência de Saída (fila e bancada). Nasceu em 05/out/2026 e é a
# segunda peça da F4. O que ele protege são as decisões da barganha de 05/out,
# que são justamente as que "simplificar a tela" apaga primeiro:
#
#   a contagem e CEGA: o que a separacao entregou so aparece depois de contar
#   o TAMANHO da divergencia nao vaza antes de o conferente decidir
#   mexer na contagem depois de bancar REABRE a decisao
#   divergencia exige motivo, e os motivos mudam com o SINAL
#   bipar soma UMA peca por leitura
#   fechar emite a nota pelo CONFERIDO, nao pelo vendido
#   falta para o cliente exige a escolha dele (CDC art. 35) — o sistema nao escolhe
#   a etiqueta sai por VOLUME, numerada, e sem valor nenhum
#   quem CONFERE nao desliga a propria cega — o interruptor nao existe na bancada
#   os parametros do modulo tem tela, e o catalogo existe em quem o LE
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
FILA = 'pagina-logistica-conferencia-saida.html'
BANCADA = 'pagina-logistica-conferencia-saida-detalhe.html'
PARAMS = 'pagina-configuracoes-parametros-estoque.html'
CONFIG = 'pagina-configuracoes-conferencia.html'

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

def nova(pw, alvo, erros):
    pg = pw.chromium.launch(executable_path=CHROME).new_page(viewport={'width': 1440, 'height': 950})
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' and not ruido(m.text) else None)
    pg.goto(localiza.uri(alvo))
    pg.wait_for_timeout(600)
    return pg

# Folha de confirmacao e fixa no rodape: numa pagina rolada o clique direto
# esbarra na conta de coordenadas do playwright, nao na tela.
def confirmar(pg):
    pg.evaluate('() => window.scrollTo(0, 0)')
    pg.click('#btnConfirmModalConfirmar')
    pg.wait_for_timeout(320)

def texto_modal(pg):
    return pg.locator('#confirmModalTexto').inner_text()

def contar(pg, i, n):
    pg.fill('#qtd-' + str(i), str(n))
    pg.wait_for_timeout(200)


with sync_playwright() as pw:
    erros = []

    # ---------------------------------------------------------------- 1
    print('\n1. A FILA ABRE, CONTA E HERDA A MARCA DA SEPARACAO')
    pg = nova(pw, FILA, erros)
    ok(pg.locator('#corpoTabela tr').count() > 0, 'a fila renderiza linhas')
    conts = pg.locator('#abasSituacao .sit-contador').all_inner_texts()
    ok(len(conts) == 4, 'quatro abas de situacao: %d' % len(conts))
    ok(int(conts[0]) == int(conts[1]) + int(conts[2]) + int(conts[3]),
       'o contador de "todas" e a soma dos tres: %s' % conts)
    ok(pg.locator('#corpoTabela .marca-falta').count() >= 1,
       'pedido que veio com falta da separacao chega marcado na fila')
    ok('nota fiscal sai' in pg.locator('#avisoFilaTexto').inner_text(),
       'o aviso diz o que esta etapa decide')

    # ---------------------------------------------------------------- 2
    print('\n2. O PROXIMO E O QUE VEIO COM FALTA, NAO SO O MAIS VELHO')
    pg.click('#btnConferirProximo')
    pg.wait_for_timeout(300)
    t = texto_modal(pg)
    ok('#23' in t, 'oferece o pedido que veio com falta: %s' % t[:50])
    ok('COM FALTA' in t, 'e diz por que ele passou na frente')
    pg.click('#btnConfirmModalCancelar')
    pg.wait_for_timeout(200)

    # ---------------------------------------------------------------- 3
    print('\n3. A CONTAGEM ABRE CEGA')
    pg = nova(pw, BANCADA + '?id=26', erros)
    ok(pg.locator('.qtd-oculta').count() == 3, 'as tres quantidades da separacao comecam ocultas')
    ok(pg.evaluate("() => PARAM.conferenciaSaidaCega") is True,
       'o parametro de contagem cega abre ligado')
    vazios = pg.evaluate("() => Array.from(document.querySelectorAll('[data-qtd]')).map(i => i.value)")
    ok(all(v == '' for v in vazios), 'os campos de contagem nascem vazios: %s' % vazios)

    # ---------------------------------------------------------------- 4
    print('\n4. BIPAR SOMA UMA PECA POR LEITURA')
    pg.fill('#campoBipar', 'SKU-INVENTADO')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(200)
    ok('não está neste pedido' in pg.locator('#ecoBipar').inner_text(), 'sku de fora nao soma nada')
    for _ in range(2):
        pg.fill('#campoBipar', 'tec-mec-087')
        pg.press('#campoBipar', 'Enter')
        pg.wait_for_timeout(150)
    ok(pg.evaluate("() => ITENS[0].conferida") == 2,
       'duas leituras somam duas pecas (e nao e sensivel a maiuscula)')
    ok(pg.locator('.cel-dif[data-i="0"]').inner_text().strip().lower() == 'confere',
       'bateu com a separacao: confere')
    ok(pg.locator('.cel-sep[data-i="0"]').inner_text().strip() == '2',
       'e so AGORA o numero da separacao aparece')

    # ---------------------------------------------------------------- 5
    print('\n5. O TAMANHO DA DIVERGENCIA NAO VAZA ANTES DA DECISAO')
    contar(pg, 1, 1)   # separacao entregou 2
    ok(pg.locator('.cel-dif[data-i="1"]').inner_text().strip().lower() == 'divergência',
       'a tela diz QUE existe divergencia: %s' % pg.locator('.cel-dif[data-i="1"]').inner_text())
    ok(pg.locator('.cel-sep[data-i="1"]').inner_text().strip().lower() == 'oculta',
       'e continua sem dizer QUANTO — senao ajustar ate o sistema calar e trivial')
    ok(pg.locator('#validar-1').is_visible(), 'aparece a decisao: recontar ou bancar')
    # 09/out: o botao dizia "Banco a contagem"; o usuario pediu outro nome.
    ok(pg.locator('[data-bancar="1"]').inner_text() == 'Confirmar contagem' and 'confirme o que você contou' in pg.locator('#validar-1').inner_text(),
       'e o botao diz o que faz: confirmar a contagem')
    ok(not pg.locator('#motivo-1').is_visible(), 'o motivo so entra depois da decisao')

    # ---------------------------------------------------------------- 6
    print('\n6. RECONTAR LIMPA, BANCAR REVELA E EXIGE MOTIVO')
    pg.click('[data-recontar="1"]')
    pg.wait_for_timeout(250)
    ok(pg.evaluate("() => ITENS[1].conferida") is None, 'recontar zera a contagem daquele item')
    ok(pg.locator('.cel-sep[data-i="1"]').inner_text().strip().lower() == 'oculta', 'e volta a esconder o esperado')
    contar(pg, 1, 1)
    pg.click('[data-bancar="1"]')
    pg.wait_for_timeout(300)
    # 09/out: o que falta passa a ser bloqueado para venda, em vez de so esperar reconferencia.
    ok('bloqueado para venda' in texto_modal(pg) and 'Itens Bloqueados' in texto_modal(pg),
       'bancar avisa que o que faltar fica bloqueado: %s' % texto_modal(pg)[:70])
    confirmar(pg)
    ok(pg.locator('.cel-dif[data-i="1"]').inner_text().strip() == '-1', 'bancado, o tamanho aparece')
    ok(pg.locator('.cel-sep[data-i="1"]').inner_text().strip() == '2', 'e o numero da separacao tambem')
    ok(pg.locator('#motivo-1').is_visible(), 'o motivo passa a ser obrigatorio')
    ok(pg.evaluate("() => document.getElementById('motivo-1').classList.contains('campo-pendente')"),
       'e aparece marcado como pendente ate alguem escolher')
    # 09/out: o menu do motivo abria DENTRO da tabela, que o cortava e ganhava barra de rolagem
    # (print do usuario). A assercao e a do dedo: cada opcao tem de estar por cima no ponto dela.
    pg.click('#motivo-1 .dropdown-select-btn'); pg.wait_for_timeout(250)
    alcance = pg.evaluate("""() => { const m = document.querySelector('#motivo-1 .dropdown-select-menu'), w = document.querySelector('.itens-table-wrap');
        const itens = Array.from(m.querySelectorAll('.dropdown-select-item'));
        return { aberto: m.classList.contains('open'), itens: itens.length, rola: w.scrollHeight - w.clientHeight,
                 toca: itens.every(it => { const r = it.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2); return e === it || it.contains(e); }) }; }""")
    ok(alcance['aberto'] and alcance['itens'] >= 2 and alcance['toca'] and alcance['rola'] <= 1,
       'o menu do motivo abre inteiro, por cima da tabela, sem barra de rolagem dentro dela: %s' % alcance)
    pg.mouse.wheel(0, 120); pg.wait_for_timeout(250)
    ok(pg.locator('#motivo-1 .dropdown-select-menu.open').count() == 0, 'e rolar a tela fecha o menu, para ele nao ficar solto')
    pg.evaluate('window.scrollTo(0, 0)'); pg.wait_for_timeout(150)

    # ---------------------------------------------------------------- 7
    print('\n7. MEXER NA CONTAGEM DEPOIS DE BANCAR REABRE A DECISAO')
    contar(pg, 1, 0)
    ok(pg.evaluate("() => ITENS[1].bancou") is False,
       'a decisao valia para o numero ANTERIOR, nao para este')
    ok(pg.locator('.cel-sep[data-i="1"]').inner_text().strip().lower() == 'oculta',
       'e o esperado volta a ficar oculto')
    contar(pg, 1, 1)
    pg.click('[data-bancar="1"]'); pg.wait_for_timeout(250); confirmar(pg)

    # ---------------------------------------------------------------- 8
    print('\n8. OS MOTIVOS MUDAM COM O SINAL DA DIVERGENCIA')
    neg = pg.evaluate("() => Array.from(document.querySelectorAll('#motivo-1 .dropdown-select-item')).map(x => x.getAttribute('data-value'))")
    ok('nao_veio' in neg and 'sobra_separacao' not in neg,
       'faltando, so os motivos de falta aparecem: %s' % neg)
    contar(pg, 1, 3)   # agora sobra
    pg.click('[data-bancar="1"]'); pg.wait_for_timeout(250); confirmar(pg)
    pos = pg.evaluate("() => Array.from(document.querySelectorAll('#motivo-1 .dropdown-select-item')).map(x => x.getAttribute('data-value'))")
    ok('sobra_separacao' in pos and 'nao_veio' not in pos,
       'sobrando, so os motivos de sobra: %s' % pos)
    contar(pg, 1, 1)
    pg.click('[data-bancar="1"]'); pg.wait_for_timeout(250); confirmar(pg)

    # ---------------------------------------------------------------- 9
    print('\n9. FECHAR TRAVA NO QUE FALTA, UM DE CADA VEZ')
    pg.click('#btnFechar'); pg.wait_for_timeout(300)
    ok('sem contagem' in texto_modal(pg), 'item nao contado trava: %s' % texto_modal(pg)[:60])
    confirmar(pg)
    contar(pg, 2, 1)
    pg.click('#btnFechar'); pg.wait_for_timeout(300)
    ok('sem motivo' in texto_modal(pg), 'divergencia sem motivo trava: %s' % texto_modal(pg)[:60])
    confirmar(pg)
    pg.click('#motivo-1 .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#motivo-1 .dropdown-select-item[data-value="nao_veio"]'); pg.wait_for_timeout(250)
    pg.click('#btnFechar'); pg.wait_for_timeout(300)
    ok('CDC art. 35' in texto_modal(pg) or 'escolheu' in texto_modal(pg),
       'falta para o cliente trava ate alguem registrar a escolha dele: %s' % texto_modal(pg)[:70])
    confirmar(pg)

    # ---------------------------------------------------------------- 10
    print('\n10. A NOTA SAI PELO CONFERIDO, NAO PELO VENDIDO')
    pedido = pg.evaluate("() => valorPedido()")
    faturar = pg.evaluate("() => valorFaturar()")
    ok(faturar < pedido, 'faltando item, o valor a faturar fica abaixo do pedido: %.2f < %.2f' % (faturar, pedido))
    ok(abs(faturar - pg.evaluate("() => ITENS.reduce((s,i) => s + (i.conferida||0) * i.preco, 0)")) < 0.01,
       'e ele e exatamente a soma do que foi conferido')
    ok(pg.locator('#blocoCompensa').is_visible(), 'o bloco de compensacao aparece')
    txt = pg.locator('#compensaHint').inner_text()
    ok('art. 35' in txt, 'o texto cita a regra que obriga a escolha ser do cliente')
    ok('restituir' in txt, 'e sugere restituir quando o pedido ja esta pago')
    opcoes = pg.evaluate("() => Array.from(document.querySelectorAll('#compensaOpcoes [data-compensa]')).map(b => b.getAttribute('data-compensa'))")
    ok(sorted(opcoes) == ['credito', 'reenvio', 'restituicao'],
       'as tres opcoes do CDC estao na tela: %s' % opcoes)

    # ---------------------------------------------------------------- 11
    print('\n11. VOLUMES: UM SEMPRE SOBRA, E A ETIQUETA SAI NUMERADA E SEM VALOR')
    ok(pg.locator('.vol-linha').count() == 1, 'a bancada abre com um volume')
    ok(pg.locator('[data-remover="0"]').is_disabled(), 'o unico volume nao pode ser removido')
    pg.click('#btnAddVolume'); pg.wait_for_timeout(250)
    ok(pg.locator('.vol-linha').count() == 2, 'da para adicionar volume')
    ok(not pg.locator('[data-remover="0"]').is_disabled(), 'com dois, remover volta a valer')
    pg.evaluate('() => montarEtiquetas()')
    etiq = pg.evaluate("() => document.getElementById('etiqFolha').innerText")
    ok('R$' not in etiq, 'a etiqueta nao leva valor para fora do galpao')
    ok('Volume 1 de 2' in etiq and 'Volume 2 de 2' in etiq, 'uma etiqueta por volume, numerada')
    ok(pg.evaluate("() => document.getElementById('etiqFolha').classList.contains('oculta')"),
       'a folha fica escondida fora da impressao')
    pg.click('[data-remover="1"]'); pg.wait_for_timeout(250)

    # ---------------------------------------------------------------- 12
    print('\n12. FECHAR FATURA, MANDA PARA A EXPEDICAO E FICA NO REGISTRO')
    pg.click('[data-compensa="restituicao"]'); pg.wait_for_timeout(200)
    pg.click('#btnFechar'); pg.wait_for_timeout(320)
    t = texto_modal(pg)
    ok('Expedição' in t, 'a confirmacao diz para onde o pedido vai: %s' % t[:60])
    # 09/out: o que faltou fica bloqueado para venda; baixa continua nao acontecendo aqui.
    ok('nenhum saldo é baixado' in t.lower() and 'bloqueado para venda' in t, 'e que o saldo NAO e baixado aqui: o que faltou fica bloqueado')
    ok('restituir o valor' in t, 'e repete a compensacao escolhida')
    confirmar(pg)
    ok('faturado' in texto_modal(pg), 'o aviso final diz que o pedido foi faturado')
    confirmar(pg)
    ok(pg.locator('#badgeSituacao').inner_text().strip().upper() == 'CONFERIDO', 'o pedido andou')
    ok(pg.locator('#btnFechar').is_disabled(), 'conferido nao se fecha de novo')
    chaves = pg.evaluate("() => JSON.parse(localStorage.getItem('deskLog')||'[]').map(x => x.chave)")
    ok('confSaidaFecha' in chaves, 'o fechamento foi para o registro de atividades')
    ok('confSaidaDivergencia' in chaves, 'e bancar a contagem tambem')

    # ---------------------------------------------------------------- 13
    print('\n13. SEM DIVERGENCIA, A TELA NAO INVENTA COMPENSACAO')
    pg = nova(pw, BANCADA + '?id=27', erros)
    for _ in range(20):
        pg.fill('#campoBipar', 'PAP-A4-500')
        pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(400)
    ok(pg.evaluate("() => ITENS[0].conferida") == 20, 'vinte leituras, vinte pecas')
    ok(not pg.locator('#blocoCompensa').is_visible(), 'batendo, nao ha compensacao a registrar')
    ok(abs(pg.evaluate("() => valorFaturar() - valorPedido()")) < 0.01, 'e a nota sai pelo valor cheio')
    pg.click('#btnFechar'); pg.wait_for_timeout(320)
    ok('divergiu' not in texto_modal(pg), 'a confirmacao nao fala em divergencia: %s' % texto_modal(pg)[:70])
    confirmar(pg); confirmar(pg)

    # ---------------------------------------------------------------- 14
    # Na conferencia de COMPRA o erro que a cega pega e do FORNECEDOR, um
    # terceiro. Aqui ele e do COLEGA que separou — e, no limite, do proprio
    # conferente. Dar o interruptor a quem esta sendo conferido e entregar a
    # chave do controle para o controlado.
    print('\n14. QUEM CONFERE NAO DESLIGA A PROPRIA CEGA')
    pg = nova(pw, BANCADA + '?id=24', erros)
    ok(pg.locator('#switchCego').count() == 0, 'a bancada NAO tem interruptor de contagem cega')
    ok('cega' in pg.locator('#notaCega').inner_text(),
       'mas a tela diz em que estado esta: %s' % pg.locator('#notaCega').inner_text()[:60])
    ok(pg.locator('.qtd-oculta').count() > 0, 'e abre cega, como o parametro manda')

    # Em Configuracoes, que e tela de outro perfil, desligar confirma e registra.
    pgc = nova(pw, CONFIG, erros)
    pgc.click('#swCegaSaida'); pgc.wait_for_timeout(200)
    pgc.click('#btnSalvarParam'); pgc.wait_for_timeout(350)
    t = pgc.locator('#confirmModalTexto').inner_text()
    ok('passa a confirmar o número em vez de conferir' in t,
       'desligar em Configuracoes diz o que se perde: %s' % t[:60])
    ok(pgc.evaluate("() => document.getElementById('campoSenhaModal').classList.contains('on')"),
       'e pede senha — e a mudanca que apaga um controle, nao que ajusta um padrao')
    pgc.evaluate('() => window.scrollTo(0, 0)')
    pgc.fill('#inputSenhaModal', 'senha-de-teste')
    pgc.click('#btnConfirmModalConfirmar'); pgc.wait_for_timeout(350)
    ok(pgc.evaluate("() => PARAM.conferenciaSaidaCega") is False, 'e so entao o valor muda')
    chaves = pgc.evaluate("() => JSON.parse(localStorage.getItem('deskLog')||'[]').map(x => x.chave)")
    ok('confSaidaCegaDesliga' in chaves, 'o momento fica no registro de atividades')

    # E a bancada obedece ao que Configuracoes decidiu. Precisa ser a MESMA aba:
    # cada `nova()` abre um navegador proprio, e localStorage nao atravessa de um
    # para o outro — o parametro ficaria salvo num navegador e lido no outro.
    pgc.goto(localiza.uri(BANCADA + '?id=24'))
    pgc.wait_for_timeout(600)
    ok(pgc.locator('.qtd-oculta').count() == 0, 'desligada la, a bancada abre mostrando a separacao')
    ok('desligada' in pgc.locator('#notaCega').inner_text(),
       'e diz onde isso foi mudado: %s' % pgc.locator('#notaCega').inner_text()[:70])

    # ---------------------------------------------------------------- 15
    print('\n15. ID QUE NAO EXISTE AVISA EM VEZ DE ABRIR CALADO')
    pg = nova(pw, BANCADA + '?id=99999', erros)
    ok('não está na fila' in texto_modal(pg), 'id inexistente avisa: %s' % texto_modal(pg)[:60])
    confirmar(pg)
    ok(pg.locator('#corpoItens tr').count() > 0, 'e ainda assim abre num pedido de verdade')

    # ---------------------------------------------------------------- 16
    print('\n16. OS PARAMETROS DO MODULO TEM TELA')
    # Ate 05/out eram cinco numeros decidindo cor e bloqueio sem existir em
    # Configuracoes — e a nota da listagem de Pedidos ja mandava o usuario para
    # uma tela onde eles nao estavam. Parametro orfao e promessa falsa.
    pgp = nova(pw, PARAMS, erros)
    campos = pgp.evaluate("() => Array.from(document.querySelectorAll('[data-param]')).map(i => i.getAttribute('data-param') + '=' + i.value)")
    for chave in ['separacaoAlertaHoras', 'separacaoCriticoHoras', 'conferenciaSaidaAlertaHoras',
                  'conferenciaSaidaCriticoHoras', 'reservaExpiraDias', 'bloquearPedidoAtrasoDias']:
        achou = [c for c in campos if c.startswith(chave + '=')]
        ok(bool(achou) and not achou[0].endswith('=undefined'),
           '%s tem campo e abre com o valor salvo: %s' % (chave, achou or 'ausente'))
    pgp.fill('#atrasoDias', '0'); pgp.wait_for_timeout(300)
    ok('desligado' in pgp.locator('#previaAtraso').inner_text().lower(),
       'zero desliga a trava, e a tela diz isso em palavras')
    pgc = nova(pw, CONFIG, erros)
    switches = pgc.evaluate("() => Array.from(document.querySelectorAll('[data-param]')).map(s => s.getAttribute('data-param') + '=' + s.classList.contains('on'))")
    for chave in ['conferenciaSaidaCega', 'sugerirEmbalagem', 'separacaoOrdemPorEndereco']:
        ok((chave + '=true') in switches, '%s tem interruptor e abre ligado: %s' % (chave, switches))

    # ---------------------------------------------------------------- 17
    print('\n17. O CATALOGO DE ACOES EXISTE EM QUEM O LE')
    CHAVES = ['confSaidaAssume', 'confSaidaDivergencia', 'confSaidaCegaDesliga',
              'confSaidaFecha', 'confSaidaParcial', 'confSaidaReabre']
    for tela in [FILA, BANCADA, 'pagina-configuracoes-confirmacoes-senha.html',
                 'pagina-cadastros-vendedores-detalhe.html', 'pagina-configuracoes-registro-atividades.html']:
        pgc = nova(pw, tela, erros)
        achadas = pgc.evaluate("() => ACOES_SENHA.map(a => a.chave)")
        faltando = [k for k in CHAVES if k not in achadas]
        ok(not faltando, '%s conhece as acoes da bancada%s' % (tela.replace('pagina-', ''), '' if not faltando else ' — falta ' + ', '.join(faltando)))
    pgc = nova(pw, BANCADA, erros)
    ok(pgc.evaluate("() => exigeSenha('confSaidaReabre')"), 'reabrir conferencia ja faturada pede senha')
    ok(not pgc.evaluate("() => exigeSenha('confSaidaFecha')"), 'fechar nao pede senha — trabalho normal de bancada')

    print('\nERROS DE CONSOLE: ' + (str(erros) if erros else 'nenhum'))
    if erros: falhas.append('erro de console: %s' % erros)

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
