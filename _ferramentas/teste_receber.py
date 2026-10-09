# -*- coding: utf-8 -*-
# Contas a Receber — listagem e pagina da conta. Nasceu em 02/out/2026, junto com
# o modulo, e fecha a F5. O que ele protege nao e o desenho: sao as decisoes que
# separam o a RECEBER do a PAGAR, e que um clone apaga sem fazer barulho.
#
#   a conta nasce do PEDIDO, e a coluna Origem leva ate ele
#   Valor, Liquido, Recebido e Saldo sao QUATRO numeros diferentes
#   a taxa retida QUITA o titulo sem entrar no caixa
#   baixa e ENTRADA no caixa; estorno e SAIDA — o clone trouxe o sentido invertido
#   recibo e duplicata tem travas INVERSAS
#   o pedido define as parcelas, e a sobra dos centavos fica na primeira
#   cliente com conta vencida nao compra de novo
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
LISTA = 'pagina-financas-contas-receber.html'
CONTA = 'pagina-financas-contas-receber-detalhe.html'
PEDIDO = 'pagina-vendas-pedidos-detalhe.html'

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if (m.type == 'error' and not ruido(m.text)) else None)
    pg.on('dialog', lambda d: d.dismiss())

    def abre(arq, espera=600):
        erros.clear()
        pg.goto(localiza.uri(arq)); pg.wait_for_timeout(espera)

    def fecha_modal():
        pg.evaluate("fecharModalConfirmacao()"); pg.wait_for_timeout(150)

    # =======================================================================
    print('\n[1] A listagem abre e se explica')
    abre(LISTA)
    ok(not erros, 'sem erro de JS na abertura' + (' — ' + erros[0] if erros else ''))
    ok('Contas a Receber' in pg.inner_text('.page-header h1'), 'título da tela')
    ok(pg.eval_on_selector_all('#breadcrumb .crumb', 'e => e.map(x => x.textContent)') == ['Finanças', 'Contas a Receber'],
       'breadcrumb com dois níveis, sem buraco')
    ok(pg.eval_on_selector_all('tbody tr', 'e => e.length') > 0, 'a tabela tem linhas')

    print('\n[2] O controle de período diz o estado em que a tela abriu')
    # O a pagar abria filtrado pelo mes e a pill jurava "sem filtro". Achado ao
    # clonar; corrigido nas duas telas.
    for arq, esperado in [(LISTA, 'todos'), ('pagina-financas-contas-pagar.html', 'mes')]:
        abre(arq)
        estado = pg.evaluate("periodoAtual")
        rotulo = pg.inner_text('#filtroPeriodo .dropdown-select-label')
        item = pg.eval_on_selector('#filtroPeriodo .dropdown-select-item[data-value="%s"]' % estado, 'e => e.textContent.trim()')
        ok(estado == esperado, '%s abre em "%s"' % (arq[7:-5], estado))
        ok(rotulo == item, 'e a pill diz exatamente isso: "%s"' % rotulo)

    print('\n[3] Quatro valores, e eles não são o mesmo número')
    abre(LISTA)
    cab = pg.eval_on_selector_all('thead th', 'e => e.map(x => x.textContent.trim())')
    for c in ['Valor', 'Líquido', 'Saldo', 'Recebido']:
        ok(c in cab, 'a coluna %s existe' % c)
    com_taxa = pg.evaluate("TITULOS.filter(t => t.taxas > 0)[0]")
    ok(com_taxa is not None, 'há conta com taxa retida no exemplo')
    ok(abs(com_taxa['valor'] - com_taxa['taxas'] - com_taxa['liquido']) < 0.01,
       'líquido = valor − taxas: %.2f − %.2f = %.2f' % (com_taxa['valor'], com_taxa['taxas'], com_taxa['liquido']))
    ok(pg.evaluate("TITULOS.every(t => t.liquido !== undefined && t.taxas !== undefined)"),
       'nenhum título fica sem os campos de valor do §12.4')

    print('\n[4] A conta nasce do pedido, e a Origem leva até ele')
    n_origem = pg.eval_on_selector_all('.tit-origem', 'e => e.length')
    ok(n_origem > 0, '%d linhas apontam para o pedido que as criou' % n_origem)
    ok(pg.evaluate("TITULOS.some(t => !t.pedido)"), 'e existe conta lançada à mão, sem origem — as duas coisas são possíveis')
    pg.click('.tit-origem'); pg.wait_for_timeout(500)
    ok(PEDIDO in pg.url and '?id=' in pg.url, 'clicar na origem abre a venda: ' + pg.url.split('/')[-1])

    print('\n[5] A taxa retida quita o título sem entrar no caixa')
    abre(LISTA)
    alvo = pg.evaluate("TITULOS.filter(t => t.taxas > 0 && t.recebido === 0 && !t.cancelado)[0].id")
    dados = pg.evaluate("(function(id){var t=TITULOS.filter(x=>x.id===id)[0]; return {v:t.valor, tx:t.taxas, lq:t.liquido};})(%d)" % alvo)
    pg.evaluate("(function(id){ selTit=[id]; render(); })(%d)" % alvo); pg.wait_for_timeout(300)
    pg.click('#btnReceberSelecionadas'); pg.wait_for_timeout(400)
    pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(250)
    pg.fill('#inputValorRecebido', ('%.2f' % dados['lq']).replace('.', ','))
    pg.fill('#inputTaxas', ('%.2f' % dados['tx']).replace('.', ','))
    pg.wait_for_timeout(350)
    previa = pg.inner_text('#previaRecebimento')
    ok('quita o título mas não entra no caixa' in previa, 'a prévia explica o que a taxa faz')
    # Formatar o esperado com o MESMO formatador da tela: comparar com '%.2f'
    # ignora o separador de milhar e reprova uma tela certa.
    liq_txt = pg.evaluate("fmtDin(%f)" % dados['lq'])
    cheio_txt = pg.evaluate("fmtDin(%f)" % dados['v'])
    ok(liq_txt in previa, 'o que entra no caixa é o LÍQUIDO (R$ %s)' % liq_txt)
    ok(cheio_txt not in previa.split('quita o título')[0],
       'e NÃO o valor cheio (R$ %s), que é o que o cliente deve' % cheio_txt)
    pg.click('#btnConfirmarRecebimento'); pg.wait_for_timeout(400)
    if pg.eval_on_selector('#confirmModal', 'e => e.classList.contains("open")'):
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
    saldo = pg.evaluate("(function(id){var t=TITULOS.filter(x=>x.id===id)[0]; return Math.max(0,t.valor-t.recebido);})(%d)" % alvo)
    ok(saldo < 0.01, 'o título fica QUITADO — sem a taxa, sobraria saldo eterno de %.2f' % dados['tx'])
    ok(pg.evaluate("(function(id){return situacaoDe(TITULOS.filter(x=>x.id===id)[0]);})(%d)" % alvo) == 'recebida',
       'e a situação vira recebida')

    print('\n[6] Baixa é entrada no caixa; estorno é saída')
    # O clone trouxe o sentido do a pagar. Invertido e, por isso, sob teste.
    abre(CONTA + '?id=4')
    pg.wait_for_timeout(300)
    sentidos = pg.evaluate("""() => {
      const fonte = document.documentElement.innerHTML;
      return {
        baixaEntrada: fonte.indexOf("tipo: 'entrada', valor: v - desc") >= 0,
        estornoSaida: fonte.indexOf("tipo: 'saida', valor: p.valor") >= 0
      };
    }""")
    ok(sentidos['baixaEntrada'], 'receber escreve ENTRADA no Caixa')
    ok(sentidos['estornoSaida'], 'estornar escreve SAÍDA — o inverso, não a cópia do a pagar')
    ok(pg.evaluate("document.documentElement.innerHTML.indexOf(\"origem: 'CP '\") === -1"),
       'e nenhum lançamento nasce marcado como origem de conta a PAGAR')

    print('\n[7] Recibo e duplicata têm travas inversas')
    abre(CONTA + '?id=4')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#linkImprimirRecibo', 'e => e.classList.contains("travado")'),
       'conta sem baixa: recibo travado — ele comprova o que entrou')
    ok(not pg.eval_on_selector('#linkImprimirDuplicata', 'e => e.classList.contains("travado")'),
       'conta sem baixa: duplicata liberada — ela cobra o que falta')
    ok(len(pg.get_attribute('#linkImprimirRecibo', 'title') or '') > 10, 'e o item travado diz POR QUE')
    abre(CONTA + '?id=1')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(250)
    ok(not pg.eval_on_selector('#linkImprimirRecibo', 'e => e.classList.contains("travado")'),
       'conta recebida: recibo liberado')
    ok(pg.eval_on_selector('#linkImprimirDuplicata', 'e => e.classList.contains("travado")'),
       'conta recebida: duplicata travada — não há o que cobrar')

    print('\n[8] A página da conta carrega os três valores')
    abre(CONTA + '?id=3')
    ok(pg.input_value('#inputTaxas') != '0,00', 'as taxas vêm preenchidas: ' + pg.input_value('#inputTaxas'))
    ok(pg.input_value('#inputLiquido') != pg.input_value('#inputValor'),
       'e o líquido é diferente do valor: %s vs %s' % (pg.input_value('#inputLiquido'), pg.input_value('#inputValor')))
    ok(pg.inner_text('#ddAntecipado .dropdown-select-label') in ('Sim', 'Não'), 'antecipado tem valor')

    print('\n[9] O líquido é sugerido, mas quem manda é quem digita')
    abre(CONTA + '?novo=1')
    pg.fill('#inputValor', '1.000,00'); pg.wait_for_timeout(150)
    pg.fill('#inputTaxas', '90,00'); pg.wait_for_timeout(250)
    ok(pg.input_value('#inputLiquido') == '910,00', 'sugere valor − taxa: ' + pg.input_value('#inputLiquido'))
    pg.fill('#inputLiquido', '905,00'); pg.wait_for_timeout(150)
    pg.fill('#inputTaxas', '95,00'); pg.wait_for_timeout(250)
    ok(pg.input_value('#inputLiquido') == '905,00',
       'depois que o usuário escreve, a tela NÃO mexe mais — o número dele veio do extrato')

    print('\n[10] O pedido define as parcelas (02/out)')
    abre(PEDIDO + '?editar=1')
    ok(pg.eval_on_selector('#linhaParcelas', 'e => e.offsetParent === null'), 'à vista não mostra prévia nenhuma')
    pg.click('#inputCondicao .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#inputCondicao .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(400)
    chips = pg.eval_on_selector_all('.parcela-chip', 'e => e.length')
    ok(chips == 3, '3x mostra 3 parcelas na prévia: %d' % chips)
    ok(pg.evaluate("Math.abs(planoDeParcelas(recalcularTotais()).reduce((s,x)=>s+x.valor,0) - recalcularTotais()) < 0.005"),
       'a soma das parcelas fecha com o total do pedido')
    # A regra dos centavos: com um total que NAO divide redondo, a sobra fica na
    # primeira. Testar com 6.064,77/7, que sobra.
    sobra = pg.evaluate("""(() => {
      const p = planoDeParcelas(1000.00);
      return { n: p.length, primeira: p[0].valor, outras: p.slice(1).map(x => x.valor) };
    })()""")
    pg.click('#inputCondicao .dropdown-select-btn'); pg.wait_for_timeout(180)
    pg.click('#inputCondicao .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(250)
    r = pg.evaluate("(() => { const p = planoDeParcelas(1000.00); return [p[0].valor, p[1].valor, p[2].valor]; })()")
    ok(abs(sum(r) - 1000.00) < 0.005, '1.000,00 em 3x soma exatamente 1.000,00: %s' % r)
    ok(r[0] > r[1] and r[1] == r[2], 'e a sobra de centavos fica TODA na primeira: %s' % r)
    ok(pg.evaluate("planoDeParcelas(recalcularTotais()).every((x,i,a) => i === 0 || x.venc !== a[i-1].venc)"),
       'cada parcela tem vencimento próprio')

    print('\n[11] Cliente com conta vencida não compra de novo')
    abre(PEDIDO + '?editar=1')
    ok(pg.eval_on_selector('#avisoAtraso', 'e => e.offsetParent !== null'),
       'o aviso aparece na ABERTURA, não só ao salvar — descobrir a trava no fim é perder o pedido inteiro')
    ok('não vai salvar' in pg.inner_text('#avisoAtraso'), 'e diz o que vai acontecer: ' + pg.inner_text('#avisoAtraso')[:70])
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    t = pg.inner_text('#confirmModalTexto')
    ok('não pode ser salvo' in t and 'vencida' in t, 'salvar é bloqueado')
    ok('dia(s) de atraso' in t, 'e a mensagem diz há quantos dias: "%s"' % t[40:150])
    ok(pg.eval_on_selector('#erroAtraso', 'e => e.classList.contains("show")'), 'o campo do cliente marca o erro')
    fecha_modal()
    # Tolerancia 0 desliga a trava: o numero manda, nao o `if`.
    pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0;")
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    ok('ficou reservado' in pg.inner_text('#confirmModalTexto'),
       'com tolerância 0 a trava some — o parâmetro é que decide, não o código')
    fecha_modal()

    print('\n[12] Salvar anuncia as contas que vão nascer')
    abre(PEDIDO + '?editar=1')
    pg.evaluate("PARAM.bloquearPedidoAtrasoDias = 0;")
    pg.click('#inputCondicao .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#inputCondicao .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(350)
    pg.click('#btnSalvar'); pg.wait_for_timeout(400)
    t = pg.inner_text('#confirmModalTexto')
    ok('3 contas a receber' in t, 'o aviso diz QUANTAS contas nascem: "%s"' % t[:80])
    ok('vencendo de' in t, 'e entre que datas')
    fecha_modal()

    print('\n[13] Padrão de cabeçalho e de linhas (02/out) — nas telas que têm os dois')
    # Tres regras que o usuario pediu depois de ver o mesmo elemento mudar de
    # lugar conforme a tela. Elas valem para o SISTEMA, nao para estas duas — por
    # isso a varredura e por toda a pasta, nao por lista escrita a mao.
    import glob as _g, os as _o
    telas = sorted(_o.path.basename(x) for x in localiza.caminhos()
                   if 'molde' not in x)

    fora_de_ordem, abas_acima = [], []
    for nome in telas:
        abre(nome, 420)
        r = pg.evaluate("""() => {
          const out = {};
          // 1) "Mais ações" é sempre o ÚLTIMO do cabeçalho
          const topo = document.querySelector('.header-acoes') ||
                       (document.querySelector('.cx-acoes-topo') || {}).parentElement;
          if (topo) {
            // Só os CONTROLES do cabeçalho: botões soltos e a raiz de cada
            // dropdown. O botão que vive DENTRO do dropdown é parte dele, não um
            // irmão — contá-lo fazia 10 telas certas parecerem fora de ordem.
            const vis = [...topo.querySelectorAll('button, .dropdown-select')]
              .filter(e => e.offsetParent !== null)
              .filter(e => !e.closest('.dropdown-select-menu'))
              .filter(e => !(e.tagName === 'BUTTON' && e.closest('.dropdown-select')));
            const idx = vis.findIndex(e => e.classList.contains('dropdown-select'));
            out.temMais = idx >= 0;
            out.maisPorUltimo = idx < 0 || idx === vis.length - 1;
            out.ordem = vis.map(e => e.id || e.className.split(' ')[0]).join(' > ');
          }
          // 2) filtros ACIMA das abas de situação, quando a tela tem os dois
          const abas = document.querySelector('#sitTabs, #abasSituacao, .abas-situacao, .sit-tabs');
          const filtros = document.querySelector('.marcas-toolbar, .estoque-toolbar');
          if (abas && filtros && abas.offsetParent !== null && filtros.offsetParent !== null) {
            out.temOsDois = true;
            out.filtrosAcima = filtros.getBoundingClientRect().top < abas.getBoundingClientRect().top;
          }
          return out;
        }""")
        if r.get('temMais') and not r.get('maisPorUltimo'):
            fora_de_ordem.append('%s (%s)' % (nome[7:-5], r.get('ordem', '')))
        if r.get('temOsDois') and not r.get('filtrosAcima'):
            abas_acima.append(nome[7:-5])

    ok(not fora_de_ordem, '"Mais ações" é o ÚLTIMO botão do cabeçalho em todas as telas' +
       ('' if not fora_de_ordem else ' — fora de ordem: ' + '; '.join(fora_de_ordem)))
    ok(not abas_acima, 'filtros ACIMA, situação com as bolinhas abaixo, em todas as telas que têm os dois' +
       ('' if not abas_acima else ' — invertidas: ' + ', '.join(abas_acima)))

    # 3) nenhum item de menu repetido — o bug que duplicou "Contas a Receber"
    repetidos = []
    for nome in telas:
        abre(nome, 380)
        achados = pg.evaluate("""() => {
          const ruins = [];
          document.querySelectorAll('[id^="flyout-"]').forEach(fly => {
            const vistos = {};
            fly.querySelectorAll('.flyout-item').forEach(it => {
              const r = it.getAttribute('data-label');
              vistos[r] = (vistos[r] || 0) + 1;
            });
            Object.keys(vistos).forEach(r => { if (vistos[r] > 1) ruins.push(fly.id + ': ' + r); });
          });
          return ruins;
        }""")
        if achados: repetidos.append(nome[7:-5] + ' → ' + ', '.join(achados))
    ok(not repetidos, 'nenhum item de menu aparece duas vezes no mesmo flyout' +
       ('' if not repetidos else ' — ' + '; '.join(repetidos)))

    print('\n[14] Nos dois temas, sem estouro')
    for tema in ['dark', 'light']:
        for arq in [LISTA, CONTA]:
            abre(arq)
            if tema == 'light':
                pg.evaluate("document.body.classList.remove('dark')"); pg.wait_for_timeout(250)
            ok(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
               '%s no tema %s: sem rolagem horizontal' % (arq[7:-5], tema))
            ok(not erros, '%s no tema %s: sem erro de JS' % (arq[7:-5], tema))

    b.close()

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
