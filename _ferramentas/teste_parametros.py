# -*- coding: utf-8 -*-
# Parametros de estoque deixou de ser gaveta (item K1 — 13/out/2026).
#
# A tela tinha nove secoes, e cinco nao eram de estoque. Decisao do usuario: ela se divide em
# Parametros de estoque e Parametros de logistica, e o bloqueio de cliente em atraso vai para
# Configuracoes do cadastro de clientes, que ja existia.
#
#   [1] cada parametro tem uma tela so, e nenhum ficou sem tela;
#   [2] Parametros de estoque: as cinco secoes, a reserva, salvar e nao mexer no que e da logistica;
#   [3] Parametros de logistica: as quatro secoes, o MDF-e, a devolucao, salvar e restaurar;
#   [4] o bloqueio por atraso no cadastro de clientes: zero desliga, invalido nao salva, e o
#       Pedido de Venda le o que foi salvo;
#   [5] os caminhos: Configuracoes leva as tres telas, e a Devolucao leva a de logistica.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
EST, LOG = 'pagina-configuracoes-parametros-estoque.html', 'pagina-configuracoes-parametros-logistica.html'
CLI, HUB = 'pagina-configuracoes-cadastro-clientes.html', 'pagina-configuracoes.html'
# Os 22 parametros que a tela unica guardava ate 13/out/2026.
ANTES = ['conferenciaCompraAlerta', 'conferenciaCompraCritico', 'enderecamentoAlerta', 'enderecamentoCritico', 'estoqueZeroLimite',
         'separacaoAlertaHoras', 'separacaoCriticoHoras', 'conferenciaSaidaAlertaHoras', 'conferenciaSaidaCriticoHoras',
         'reservaExpiraDias', 'bloquearPedidoAtrasoDias', 'expedicaoAlertaHoras', 'expedicaoCriticoHoras', 'expedicaoDesvioPesoPct',
         'mdfeRegraPadrao', 'mdfeRegraUF', 'devolucaoDeposito', 'devolucaoPrazoDias',
         'giroEncalheAte', 'giroBaixoAte', 'giroJanelaDias', 'compraCoberturaDias']

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


TITULOS = "Array.from(document.querySelectorAll('.main .par-secao:not(.par-futuro) .par-secao-titulo')).map(x => x.textContent.trim())"
GUARDADO = "JSON.parse(localStorage.getItem('deskParametros') || '{}')"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, query=''):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)

    def limpar():
        ir(EST); pg.evaluate("localStorage.removeItem('deskParametros')")

    def salvar():
        pg.evaluate("document.getElementById('btnSalvarParam').click()"); pg.wait_for_timeout(300)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(200)

    nota = lambda: pg.inner_text('#notaBarra')
    limpar()

    if secao(1, 'Cada parâmetro tem uma tela só'):
        ir(EST); do_est = pg.evaluate('CHAVES')
        ir(LOG); do_log = pg.evaluate('CHAVES')
        ir(CLI); do_cli = pg.evaluate('CHAVES_CLI')
        juntos = do_est + do_log + [k for k in do_cli if k in ANTES]
        ok(sorted(juntos) == sorted(ANTES), 'os 22 parâmetros da tela antiga continuam tendo tela: %s' % sorted(set(ANTES) ^ set(juntos)))
        ok(len(juntos) == len(set(juntos)), 'e nenhum aparece em duas telas: %s' % sorted(k for k in set(juntos) if juntos.count(k) > 1))
        ok('bloquearPedidoAtrasoDias' in do_cli and 'reservaExpiraDias' in do_est and 'devolucaoPrazoDias' in do_log and len(do_est) == 10 and len(do_log) == 11,
           'a reserva ficou no estoque, a devolução foi para a logística e o bloqueio por atraso para o cadastro de clientes (%d, %d e 1)' % (len(do_est), len(do_log)))
        todas = {n: open(c, encoding='utf-8').read() for n, c in ((_os.path.basename(c), c) for c in localiza.caminhos())}
        orfaos = [k for k in ANTES if not any("PARAM." + k in t for n, t in todas.items() if not n.startswith('pagina-configuracoes-'))]
        ok(len(orfaos) <= 2, 'e os parâmetros seguem sendo lidos pelas telas de trabalho (sem leitura direta: %s)' % orfaos)

    if secao(2, 'Parâmetros de estoque'):
        limpar(); ir(EST)
        ok(pg.evaluate(TITULOS) == ['Conferência de compra', 'Endereçamento', 'Estoque zero na base de picking', 'Compra e giro de estoque', 'Reserva de estoque'],
           'a tela tem as cinco seções de estoque: %s' % pg.evaluate(TITULOS))
        ok('Nenhuma alteração pendente' in nota() and pg.input_value('#reservaExpira') == '3' and not pg.evaluate("!!document.getElementById('atrasoDias') || !!document.getElementById('mdfePadrao')"),
           'abre sem pendência, com a reserva em 3 dias, e sem o bloqueio por atraso nem o MDF-e')
        previa = pg.inner_text('#previaReserva')
        ok('3 dias' in previa and 'libera a reserva' in previa, 'a prévia da reserva diz o prazo e o efeito: %s' % previa)
        pg.fill('#reservaExpira', '0'); pg.wait_for_timeout(150)
        ok('inválido' in nota() and pg.evaluate("document.getElementById('campoReserva').classList.contains('has-error')"), 'reserva de zero dias é inválida, e a barra diz que há campo inválido')
        salvar()
        ok('reservaExpiraDias' not in pg.evaluate(GUARDADO), 'e não salva')
        # O que e da logistica, gravado antes, tem de sobreviver ao salvar do estoque.
        pg.evaluate("(() => { const g = %s; g.devolucaoPrazoDias = 21; g.separacaoAlertaHoras = 9; localStorage.setItem('deskParametros', JSON.stringify(g)); })()" % GUARDADO)
        ir(EST)
        pg.fill('#reservaExpira', '5'); pg.fill('#confAlerta', '2'); pg.wait_for_timeout(150)
        ok('2 parâmetros alterados' in nota(), 'mexer na reserva e na conferência conta dois: %s' % nota())
        salvar()
        g = pg.evaluate(GUARDADO)
        ok(g.get('reservaExpiraDias') == 5 and g.get('conferenciaCompraAlerta') == 2 and 'Nenhuma alteração pendente' in nota(), 'salvar grava os dois, e a barra volta a dizer que nada está pendente')
        ok(g.get('devolucaoPrazoDias') == 21 and g.get('separacaoAlertaHoras') == 9, 'e o que é da logística continua como estava: devolução %s dias, separação %s horas' % (g.get('devolucaoPrazoDias'), g.get('separacaoAlertaHoras')))
        pg.evaluate("document.getElementById('btnRestaurarParam').click()"); pg.wait_for_timeout(250); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(pg.input_value('#reservaExpira') == '3' and '2 parâmetros alterados' in nota(), 'restaurar o padrão volta a reserva a 3 dias na tela, e espera o salvar')

    if secao(3, 'Parâmetros de logística'):
        limpar(); ir(LOG)
        ok(pg.evaluate(TITULOS) == ['Filas do galpão', 'Expedição e romaneio', 'MDF-e na carga própria', 'Devoluções de venda'], 'a tela tem as quatro seções de logística: %s' % pg.evaluate(TITULOS))
        ok(pg.inner_text('.main h1') == 'Parâmetros de logística' and 'Parâmetros de logística' in pg.inner_text('#breadcrumb') and 'Nenhuma alteração pendente' in nota(),
           'título e trilha dizem Parâmetros de logística, e ela abre sem pendência')
        ok(not pg.evaluate("!!document.getElementById('reservaExpira') || !!document.getElementById('giroEncalhe') || !!document.getElementById('confAlerta')"), 'sem campo de estoque nenhum')
        ok('carga' in pg.inner_text('#previaDesvio').lower() and 'devolu' in pg.inner_text('#previaDevolucao').lower(), 'as prévias do peso da carga e da devolução aparecem')
        pg.fill('#sepAlerta', '9'); pg.fill('#devPrazo', '21'); pg.wait_for_timeout(150)
        pg.evaluate("(() => { document.querySelector('#devDeposito .dropdown-select-item[data-value=\"geral\"]').click(); })()"); pg.wait_for_timeout(150)
        pg.evaluate("(() => { document.querySelector('#menuMdfeUf .dropdown-select-item[data-value=\"MA\"]').click(); document.getElementById('btnAddMdfe').click(); })()"); pg.wait_for_timeout(200)
        ok('4 parâmetros alterados' in nota(), 'mexer na separação, no prazo e no depósito da devolução e numa exceção do MDF-e conta quatro: %s' % nota())
        salvar()
        g = pg.evaluate(GUARDADO)
        ok(g.get('separacaoAlertaHoras') == 9 and g.get('devolucaoPrazoDias') == 21 and g.get('devolucaoDeposito') == 'geral' and 'MA' in (g.get('mdfeRegraUF') or {}) and 'Nenhuma alteração pendente' in nota(),
           'salvar grava os quatro: %s' % {k: g.get(k) for k in ('separacaoAlertaHoras', 'devolucaoPrazoDias', 'devolucaoDeposito', 'mdfeRegraUF')})
        pg.fill('#sepCritico', '2'); pg.wait_for_timeout(150)
        ok('inválido' in nota(), 'prazo crítico menor que o de alerta é inválido')
        ir(LOG)
        ok(pg.input_value('#sepAlerta') == '9' and pg.evaluate("document.getElementById('devDeposito').getAttribute('data-value')") == 'geral' and 'MA' in pg.inner_text('#mdfeLista'),
           'reaberta, a tela mostra o que foi salvo')
        pg.evaluate("document.getElementById('btnRestaurarParam').click()"); pg.wait_for_timeout(250); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(pg.input_value('#sepAlerta') == str(pg.evaluate('PARAM_PADRAO.separacaoAlertaHoras')) and 'MA' not in pg.inner_text('#mdfeLista'), 'restaurar o padrão volta os campos e tira a exceção do MDF-e')

    if secao(4, 'O bloqueio por atraso, no cadastro de clientes'):
        limpar(); ir(CLI)
        ok('Cliente em atraso' in pg.evaluate(TITULOS) and pg.input_value('#atrasoDias') == '1' and 'Nenhuma alteração pendente' in nota(), 'a seção "Cliente em atraso" abre com 1 dia e sem pendência')
        padrao_cli = pg.evaluate('PARAM_PADRAO.bloquearPedidoAtrasoDias')
        ir('pagina-vendas-pedidos-detalhe.html')
        ok(padrao_cli == pg.evaluate('PARAM_PADRAO.bloquearPedidoAtrasoDias') == 1, 'o padrão de fábrica é o mesmo que o Pedido de Venda usa: %s dia' % padrao_cli)
        ir(CLI)
        pg.fill('#atrasoDias', '0'); pg.wait_for_timeout(150)
        ok('desligado' in pg.inner_text('#previaAtraso').lower() and '1 configuração alterada' in nota(), 'zero desliga o bloqueio, e a tela diz isso em palavras')
        pg.fill('#atrasoDias', 'abc'); pg.wait_for_timeout(150)
        ok('inválido' in nota() and pg.evaluate("document.getElementById('campoAtraso').classList.contains('has-error')"), 'texto no lugar do número é inválido')
        salvar()
        ok('bloquearPedidoAtrasoDias' not in pg.evaluate(GUARDADO), 'e não salva')
        pg.fill('#atrasoDias', '5'); pg.wait_for_timeout(150)
        ok('5 dias' in pg.inner_text('#previaAtraso'), 'com 5, a prévia diz a partir de quantos dias o cliente deixa de comprar')
        pg.evaluate("document.getElementById('swDup').click()"); pg.wait_for_timeout(150)
        ok('2 configurações alteradas' in nota() and pg.input_value('#atrasoDias') == '5', 'mexer num interruptor não desfaz o número digitado')
        salvar()
        g = pg.evaluate(GUARDADO)
        ok(g.get('bloquearPedidoAtrasoDias') == 5 and g.get('permitirDocDuplicado') is True and 'Nenhuma alteração pendente' in nota(), 'salvar grava o bloqueio e o interruptor')
        ir('pagina-vendas-pedidos-detalhe.html')
        ok(pg.evaluate('PARAM.bloquearPedidoAtrasoDias') == 5 and '5 dia' in pg.inner_text('#avisoAtraso'), 'e o Pedido de Venda lê o que foi salvo: %s' % pg.inner_text('#avisoAtraso')[-70:])
        ir(CLI)
        pg.evaluate("document.getElementById('btnRestaurarParam').click()"); pg.wait_for_timeout(250); pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(pg.input_value('#atrasoDias') == '1', 'restaurar o padrão volta o bloqueio a 1 dia')

    if secao(5, 'Os caminhos'):
        limpar()
        hub = open(localiza.onde(HUB), encoding='utf-8').read()
        ok(all(('href:\'../configuracoes/%s\'' % t) in hub for t in (EST, LOG, CLI)), 'Configurações tem as três telas: Parâmetros de estoque, Parâmetros de logística e Cadastro de clientes')
        ir(HUB)
        pg.evaluate("(() => { const a = Array.from(document.querySelectorAll('a, [data-href], .cfg-item, .config-item, div, span')).filter(x => x.children.length === 0 && x.textContent.trim() === 'Parâmetros de logística')[0]; if (a) a.click(); })()")
        pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        chegou = pg.url.split('/')[-1].split('?')[0]
        ok(chegou in (LOG, HUB), 'e o item "Parâmetros de logística" não leva a tela errada: %s' % chegou)
        ir('pagina-logistica-devolucao.html')
        pg.evaluate("document.querySelector('[data-acao=\"parametros\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
        ok(pg.url.split('/')[-1] == LOG and pg.evaluate("!!document.getElementById('devPrazo')"), 'da Devolução, "Abrir parâmetros da devolução" chega na tela que tem o prazo da devolução')
        velhos = [n for n, c in ((_os.path.basename(c), c) for c in localiza.caminhos()) if n not in (EST, HUB)
                  and "pagina-configuracoes-parametros-estoque.html'" in open(c, encoding='utf-8').read() and 'pagina-logistica' in n]
        ok(not velhos, 'nenhuma tela de logística ainda manda para Parâmetros de estoque: %s' % velhos)

    limpar()
    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
