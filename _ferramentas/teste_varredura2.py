# -*- coding: utf-8 -*-
# Os achados da segunda varredura (14/out/2026), consertados com as decisoes do usuario.
#
# A varredura percorreu Inventario, Acerto, PDV com caixa aberto e a contagem da Conferencia de Entrada.
# Os fluxos se defendiam bem; sairam seis defeitos e tres decisoes. O usuario mandou seguir as
# sugestoes: entrada de acerto em qualquer deposito (S7), aviso do desconto da venda no campo (S8) e
# uma confirmacao por divergencia na conferencia, como ja e (S9, sem mudanca).
#
#   [1] Inventario: a senha que falta e dita (S1); cancelar com contagem pergunta (S2); os codigos
#       recusados aparecem, com o motivo (S3); o usuario e o das outras telas (S4);
#   [2] Acerto: o usuario (S4); cada deposito uma vez (S5); saida maior que o endereco para na linha
#       (S6); entrada em qualquer deposito, saida so onde ha saldo (S7);
#   [3] PDV: o desconto da venda acima do maximo avisa no campo, e finalizar ainda pede a senha (S8).
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
INV, ACE, PDV = 'pagina-estoque-inventario.html', 'pagina-estoque-acerto.html', 'pagina-vendas-pdv.html'

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


VISIVEL = "(sel) => { const e = document.querySelector(sel); return !!e && getComputedStyle(e).display !== 'none' && e.getClientRects().length > 0; }"
MUDA = "([sel, v]) => { const i = document.querySelector(sel); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); i.dispatchEvent(new Event('change', { bubbles: true })); }"
ITENS = "(id) => Array.from(document.querySelectorAll('#' + id + ' .dropdown-select-item')).map(i => i.getAttribute('data-value'))"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela):
        pg.goto(localiza.uri(tela)); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def aviso():
        pg.wait_for_timeout(450)
        return pg.evaluate("document.getElementById('avisoModal').classList.contains('open') ? document.getElementById('avisoTexto').textContent : ''")

    def fecha_aviso():
        pg.evaluate("document.getElementById('avisoBackdrop').classList.remove('open'); document.getElementById('avisoModal').classList.remove('open')"); pg.wait_for_timeout(150)

    def abre_inventario(dep):
        pg.evaluate("(d) => { document.querySelector('[data-caminho=\"gerar\"]').click(); document.querySelector('#menuDeposito .dropdown-select-item[data-value=\"' + d + '\"]').click(); document.getElementById('btnAbrirInventario').click(); }", dep)
        pg.wait_for_timeout(450)

    if secao(1, 'Inventário'):
        ir(INV); abre_inventario('2')
        pg.evaluate("document.getElementById('btnAcaoInv').click()"); pg.wait_for_timeout(250)
        pg.evaluate(MUDA, ['#corpoInv input', '5']); pg.wait_for_timeout(150)
        pg.evaluate("document.getElementById('btnAcaoInv').click()"); pg.wait_for_timeout(350)
        ok('Administrador Desk' in pg.inner_text('#fecharDrawer') and 'Walysson' not in pg.inner_text('#fecharDrawer'), 'S4: o painel de fechar mostra o usuário das outras telas, Administrador Desk')
        pg.evaluate("document.getElementById('btnConfirmarFechar').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate(VISIVEL, '#erroSenha') and 'senha' in pg.inner_text('#erroSenha').lower(), 'S1: fechar sem senha mostra a mensagem, e não só a borda vermelha')
        pg.fill('#inputSenha', 'x'); pg.wait_for_timeout(100)
        ok(not pg.evaluate(VISIVEL, '#erroSenha'), 'e a mensagem some quando a senha é digitada')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("document.getElementById('fecharDrawer').classList.remove('open'); document.getElementById('fecharBackdrop').classList.remove('open')")
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"cancelar\"]').click()"); pg.wait_for_timeout(350)
        perg = aviso()
        ok('descarta 1 quantidade' in perg and pg.evaluate("document.getElementById('painelInventario').style.display") != 'none',
           'S2: com uma quantidade informada, cancelar pergunta antes, e o inventário continua aberto: %s' % perg[:90])
        pg.evaluate("document.getElementById('btnAvisoOk').click()"); pg.wait_for_timeout(600)
        ok(pg.evaluate("getComputedStyle(document.getElementById('painelIndice')).display") != 'none' and 'cancelado' in aviso(), 'confirmado, o inventário é cancelado e a tela diz isso')
        fecha_aviso()
        ir(INV); abre_inventario('3')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"cancelar\"]').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("getComputedStyle(document.getElementById('painelIndice')).display") != 'none', 'sem nada contado, cancelar não pergunta')
        fecha_aviso()
        txt = _os.path.join(_os.environ.get('TEMP', '.'), 'desk-coletor-teste.txt')
        open(txt, 'w', encoding='utf-8').write('CAB-HDM-009\nCODIGO-QUE-NAO-EXISTE\n')
        ir(INV)
        pg.evaluate("document.querySelector('[data-caminho=\"coletor\"]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('#menuDeposito .dropdown-select-item[data-value=\"4\"]').click()"); pg.wait_for_timeout(150)
        pg.set_input_files('#inputArquivo', txt); pg.wait_for_timeout(350)
        pg.evaluate("document.getElementById('btnAbrirInventario').click()")
        a = aviso()
        ok('CODIGO-QUE-NAO-EXISTE' in a and 'não encontrado' in a and '<b>' not in a, 'S3: depois de importar, o aviso diz qual código foi recusado e por quê: %s' % a[-110:])
        fecha_aviso()
        pg.evaluate("document.getElementById('btnAcaoInv').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.getElementById('btnAcaoInv').click()"); pg.wait_for_timeout(350)
        ok('CODIGO-QUE-NAO-EXISTE' in pg.inner_text('#previaFechar'), 'e o painel de fechamento também lista o código recusado')
        _os.remove(txt)

    if secao(2, 'Acerto'):
        ir(ACE)
        pg.fill('#campoBuscaProduto', 'cadeira'); pg.wait_for_timeout(250); pg.keyboard.press('Enter'); pg.wait_for_timeout(350)
        deps = pg.evaluate(ITENS, 'menuDeposito')
        ok(len(deps) == len(set(deps)), 'S5: cada depósito aparece uma vez na linha: %s' % deps)
        todos = pg.evaluate("Object.keys(DEPOSITOS).map(String)")
        com_saldo = pg.evaluate("Array.from(new Set(produtoLinha.saldos.map(s => String(s.dep))))")
        ok(pg.evaluate("tipoLanc") == 'entrada' and sorted(deps) == sorted(todos) and len(com_saldo) < len(todos),
           'S7: na entrada, a lista traz os %d depósitos, e não só os %d onde a cadeira tem saldo' % (len(todos), len(com_saldo)))
        sem_saldo = [d for d in todos if d not in com_saldo][0]
        pg.evaluate("(d) => document.querySelector('#menuDeposito .dropdown-select-item[data-value=\"' + d + '\"]').click()", sem_saldo); pg.wait_for_timeout(200)
        ok('a endereçar' in pg.inner_text('#previaEntrada') or 'Sem base' in pg.inner_text('#previaEntrada'), 'num depósito sem saldo, a entrada diz que fica a endereçar: %s' % pg.inner_text('#previaEntrada')[:80])
        pg.evaluate("document.querySelector('#campoTipo .dropdown-select-item[data-value=\"saida\"]').click()"); pg.wait_for_timeout(250)
        ok(sorted(pg.evaluate(ITENS, 'menuDeposito')) == sorted(com_saldo) and pg.evaluate("String(depLanc)") in com_saldo,
           'na saída, só os depósitos com saldo, e o depósito escolhido volta para um deles')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.fill('#campoBuscaProduto', 'teclado'); pg.wait_for_timeout(250); pg.keyboard.press('Enter'); pg.wait_for_timeout(350)
        pg.evaluate("document.querySelector('#campoTipo .dropdown-select-item[data-value=\"saida\"]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('#campoMotivo .dropdown-select-item:not([data-value=\"\"])').click()"); pg.wait_for_timeout(150)
        disp = pg.evaluate("produtoLinha.saldos[origemLanc].qtd")
        pg.fill('#campoQuantidade', '99999'); pg.evaluate("document.getElementById('btnGravarLinha').click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate(VISIVEL, '#erroQuantidade') and ('tem %d' % disp) in pg.inner_text('#erroQuantidade') and pg.evaluate("LINHAS.length") == 0,
           'S6: saída de 99.999 num endereço com %d para na linha, com o que o endereço tem: %s' % (disp, pg.inner_text('#erroQuantidade')))
        pg.fill('#campoQuantidade', str(disp - 1)); pg.evaluate("document.getElementById('btnGravarLinha').click()"); pg.wait_for_timeout(350)
        ok(pg.evaluate("LINHAS.length") == 1, 'a saída que cabe entra no lote')
        pg.fill('#campoBuscaProduto', 'teclado'); pg.wait_for_timeout(250); pg.keyboard.press('Enter'); pg.wait_for_timeout(350)
        pg.evaluate("document.querySelector('#campoTipo .dropdown-select-item[data-value=\"saida\"]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('#campoMotivo .dropdown-select-item:not([data-value=\"\"])').click()"); pg.wait_for_timeout(150)
        pg.fill('#campoQuantidade', '2'); pg.evaluate("document.getElementById('btnGravarLinha').click()"); pg.wait_for_timeout(300)
        ok(pg.evaluate("LINHAS.length") == 1 and 'outra linha deste lote' in pg.inner_text('#erroQuantidade'), 'e uma segunda linha do mesmo endereço que passaria do saldo também para, contando a primeira')
        pg.fill('#campoQuantidade', '0'); pg.evaluate("document.getElementById('btnGravarLinha').click()"); pg.wait_for_timeout(200)
        ok('maior que zero' in pg.inner_text('#erroQuantidade'), 'a mensagem de quantidade zero continua a de antes')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
        pg.evaluate("document.getElementById('btnFinalizar').click()"); pg.wait_for_timeout(350)
        corpo = pg.evaluate("Array.from(document.querySelectorAll('.event-drawer.open')).map(d => d.innerText).join(' ')")
        ok('Administrador Desk' in corpo and 'Walysson' not in corpo, 'S4: finalizar o acerto mostra o usuário das outras telas')

    if secao(3, 'PDV'):
        ir(PDV); pg.evaluate("localStorage.removeItem('deskPdv')"); ir(PDV)
        pg.evaluate("document.getElementById('btnAbrirCaixa').click()"); pg.wait_for_timeout(200)
        pg.fill('#abrirTroco', '100,00'); pg.evaluate("document.getElementById('btnConfirmarAbertura').click()"); pg.wait_for_timeout(400)
        pg.fill('#buscaProduto', 'FON-BT-200'); pg.keyboard.press('Enter'); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('btnContinuar').click()"); pg.wait_for_timeout(350)
        ok(not pg.evaluate(VISIVEL, '#notaFinDesconto'), 'sem desconto, nenhum aviso')
        pg.click('#finDesconto'); pg.keyboard.type('50%'); pg.wait_for_timeout(200)
        ok(pg.evaluate(VISIVEL, '#notaFinDesconto') and '50,00%' in pg.inner_text('#notaFinDesconto') and 'gerente' in pg.inner_text('#notaFinDesconto'),
           'S8: digitar 50%% no desconto da venda mostra o aviso no campo, sem sair dele: %s' % pg.inner_text('#notaFinDesconto')[:80])
        pg.fill('#finDesconto', '2%'); pg.wait_for_timeout(200)
        ok(not pg.evaluate(VISIVEL, '#notaFinDesconto'), 'com 2%, dentro do máximo, o aviso some')
        pg.fill('#finDesconto', '50%'); pg.keyboard.press('Tab'); pg.wait_for_timeout(250)
        pg.evaluate("document.querySelector('#menuAddReceb .dropdown-select-item[data-value=\"pix\"]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.getElementById('btnFinalizar').click()"); pg.wait_for_timeout(500)
        ok(pg.evaluate("document.getElementById('confirmModal').classList.contains('open')") and 'Liberar desconto' in pg.inner_text('#confirmModal'),
           'e finalizar com 50% continua pedindo a liberação, com senha')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
