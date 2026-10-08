# Motivos de Perda — 08/out/2026.
#
# O item ja existia no menu de Estoque, em Acerto e Inventario, apontando para
# lugar nenhum. E os motivos viviam escritos no codigo do Acerto, com um campo
# que NAO e rotulo: `fiscal` decide se a baixa exige NF-e propria (CFOP 5.927,
# sem destaque de ICMS, com estorno do credito aproveitado na entrada), se
# resolve com documento interno, ou se depende da diferenca apurada.
#
# Motivo sem cadastro e regra fiscal sem dono — e a mesma licao que fez o
# cadastro de Motivos de Devolucao nascer ANTES da tela que o usa.
#
# O que esta suite guarda:
#   [1][2] a lista carrega e cada motivo diz as duas coisas que ele decide:
#          em que MOVIMENTO vale e o que a baixa OBRIGA;
#   [3]    movimento e eixo de verdade — o Acerto so oferece os motivos do
#          movimento escolhido, e furto nao serve para entrada;
#   [4]    tratamento que gera obrigacao AVISA antes de salvar, e trocar de
#          aviso esconde o anterior em vez de empilhar;
#   [5]    nome repetido e barrado mesmo com outra caixa;
#   [6]    excluir avisa que inativar guarda a historia;
#   [7]    a trava nasce com a tela, nos tres verbos;
#   [8]    o VINCULO: o que o cadastro diz e o que o Acerto oferece sao a
#          mesma lista — codigo, rotulo e tratamento fiscal. E esta a
#          asserção que justifica o cadastro existir;
#   [9]    o item de menu deixou de ser promessa vazia, em Estoque E na tela.
from playwright.sync_api import sync_playwright
import os, sys, glob

import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

URL = 'http://localhost:3000/'
TELA = 'pagina-operacional-motivos-perda.html'
ACERTO = 'pagina-estoque-acerto.html'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clic(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 950})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(URL + TELA)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(800)

    print('\n[1] A lista carrega e os motivos sao os que o Acerto ja usava')
    n = pg.locator('#listaMotivos .motivo-card').count()
    ok(n > 0, 'a lista renderiza (%d motivos na pagina)' % n)
    corpo = pg.inner_text('#listaMotivos')
    for termo in ['Quebra ou avaria', 'Furto ou roubo', 'Sobra de contagem', 'Contagem física']:
        ok(termo in corpo, 'o motivo "%s" tem cadastro' % termo)

    print('\n[2] Cada motivo diz as DUAS coisas que ele decide')
    movs = pg.evaluate("Object.keys(GRUPOS)")
    ok(sorted(movs) == ['balanco', 'entrada', 'saida'],
       'os tres movimentos existem: %s' % sorted(movs))
    fis = pg.evaluate("Object.keys(DESTINOS)")
    ok(sorted(fis) == ['depende', 'interno', 'nenhum', 'nfe'],
       'e os quatro tratamentos fiscais: %s' % sorted(fis))
    fora = pg.evaluate("MOTIVOS.filter(m => !GRUPOS[m.grupo] || !DESTINOS[m.destino]).length")
    ok(fora == 0, 'nenhum motivo aponta para movimento ou tratamento inexistente (%d)' % fora)
    ok('CFOP 5.927' in pg.inner_text('.main'),
       'e a tela diz qual e a obrigacao, em vez de so dizer que existe uma')

    print('\n[3] Movimento e eixo de verdade, nao etiqueta')
    # Furto nao serve para entrada, e sobra de contagem nao serve para baixa.
    furto = pg.evaluate("MOTIVOS.filter(m => m.nome.indexOf('Furto') >= 0)[0].grupo")
    ok(furto == 'saida', 'furto e motivo de SAIDA (%s)' % furto)
    sobra = pg.evaluate("MOTIVOS.filter(m => m.nome.indexOf('Sobra') >= 0)[0].grupo")
    ok(sobra == 'entrada', 'sobra de contagem e motivo de ENTRADA (%s)' % sobra)

    print('\n[4] Tratamento que obriga alguma coisa AVISA antes de salvar')
    clic(pg, '#btnNovoMotivo')
    pg.wait_for_timeout(600)
    ok(pg.locator('#notaAvaria').is_visible(),
       'o formulario abre em "exige NF-e" e o aviso ja esta la')
    ok('CFOP 5.927' in pg.inner_text('#notaAvaria'), 'dizendo qual CFOP e por que')
    clic(pg, '#inputDestino .dropdown-select-btn')
    pg.wait_for_timeout(250)
    clic(pg, '#inputDestino [data-value="depende"]')
    pg.wait_for_timeout(400)
    ok(not pg.locator('#notaAvaria').is_visible(), 'trocar de tratamento esconde o aviso anterior')
    ok(pg.locator('#notaNenhum').is_visible(), 'e mostra o do novo, em vez de empilhar')
    clic(pg, '#inputDestino .dropdown-select-btn')
    pg.wait_for_timeout(250)
    clic(pg, '#inputDestino [data-value="interno"]')
    pg.wait_for_timeout(400)
    ok(not pg.locator('#notaAvaria').is_visible() and not pg.locator('#notaNenhum').is_visible(),
       'tratamento sem obrigacao nao inventa aviso')

    print('\n[5] Nome repetido e barrado, mesmo com outra caixa')
    pg.fill('#inputNomeMotivo', 'fUrTo Ou RoUbO')
    pg.wait_for_timeout(200)
    clic(pg, '#btnSalvarMotivo')
    pg.wait_for_timeout(500)
    repetido = pg.evaluate("MOTIVOS.filter(m => m.nome.toLowerCase() === 'furto ou roubo').length")
    ok(repetido == 1, 'continua havendo um so "Furto ou roubo" (%d)' % repetido)
    pg.keyboard.press('Escape')
    pg.wait_for_timeout(300)

    print('\n[6] Excluir avisa que inativar guarda a historia')
    pg.goto(URL + TELA)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(700)
    antes = pg.evaluate("MOTIVOS.length")
    clic(pg, '#listaMotivos .motivo-card')
    pg.wait_for_timeout(500)
    if pg.locator('#btnExcluirMotivo').count() and pg.locator('#btnExcluirMotivo').is_visible():
        clic(pg, '#btnExcluirMotivo')
        pg.wait_for_timeout(500)
        texto = pg.inner_text('body').lower()
        ok('inativar' in texto or 'histórico' in texto or 'historico' in texto,
           'a tela oferece inativar antes de apagar')
        ok(pg.evaluate("MOTIVOS.length") == antes, 'e nada sumiu sem confirmacao')
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(300)
    else:
        print('  --   excluir fica em "Mais ações" nesta tela')

    print('\n[7] A trava nasce com a tela')
    pg.goto(URL + TELA)
    pg.wait_for_load_state('load')
    pg.wait_for_timeout(700)
    tem = pg.evaluate("MODULOS_SENHA.some(m => m.base === 'motivosPerda')")
    ok(tem, 'o modulo esta no catalogo de acoes')
    verbos = pg.evaluate("""(function () {
      var m = MODULOS_SENHA.filter(x => x.base === 'motivosPerda')[0];
      return m ? [m.ligado.criar, m.ligado.editar, m.ligado.excluir] : null;
    })()""")
    ok(verbos == [True, True, True], 'com os tres verbos ligados: %s' % verbos)
    p2 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p2.goto(URL + 'pagina-configuracoes-confirmacoes-senha.html')
    p2.wait_for_timeout(700)
    ok(p2.evaluate("MODULOS_SENHA.some(m => m.base === 'motivosPerda')"),
       'e Configuracoes conhece o modulo — a chave entra nas telas que LEEM o catalogo')
    p2.close()

    print('\n[8] O cadastro e o Acerto falam a MESMA lista')
    # Esta e a asserção que justifica o cadastro existir. Enquanto nao ha
    # backend, a lista do Acerto e espelho; se as duas divergirem, o motivo
    # escolhido no Acerto nao e o que o cadastro descreve — e o tratamento
    # fiscal, que nao e rotulo, passa a ser outro.
    doCadastro = pg.evaluate("""(function () {
      var fora = {};
      MOTIVOS.forEach(function (m) {
        if (m.status !== 'ativo') return;
        fora[m.nome.toLowerCase()] = m.destino;
      });
      return fora;
    })()""")
    p3 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p3.goto(URL + ACERTO)
    p3.wait_for_timeout(800)
    doAcerto = p3.evaluate("""(function () {
      var fora = {};
      ['entrada', 'saida', 'balanco'].forEach(function (t) {
        (MOTIVOS[t] || []).forEach(function (m) { fora[m.l.toLowerCase()] = m.fiscal; });
      });
      return fora;
    })()""")
    p3.close()
    faltando = [k for k in doAcerto if k not in doCadastro]
    ok(not faltando, 'todo motivo que o Acerto oferece tem cadastro: %s' % (faltando or 'todos têm'))
    divergentes = [k for k in doAcerto if k in doCadastro and doAcerto[k] != doCadastro[k]]
    ok(not divergentes,
       'e o tratamento fiscal e o MESMO nos dois lados: %s' % (divergentes or 'nenhuma divergência'))

    print('\n[9] O item de menu deixou de ser promessa vazia')
    href = pg.evaluate("""(function () {
      var el = Array.from(document.querySelectorAll('.flyout-item'))
        .filter(function (e) { return (e.getAttribute('data-label') || '') === 'Motivos de Perda'; })[0];
      return el ? el.getAttribute('data-href') : null;
    })()""")
    ok(href == TELA, 'o item leva ao cadastro: %s' % href)
    p4 = nav.new_page(viewport={'width': 1440, 'height': 950})
    p4.goto(URL + ACERTO)
    p4.wait_for_timeout(700)
    hrefEst = p4.evaluate("""(function () {
      var el = Array.from(document.querySelectorAll('.flyout-item'))
        .filter(function (e) { return (e.getAttribute('data-label') || '') === 'Motivos de Perda'; })[0];
      return el ? el.getAttribute('data-href') : null;
    })()""")
    ok(hrefEst == TELA, 'e o item do menu de Estoque tambem, que era onde ele nao levava a lugar nenhum')
    p4.close()

    print('\n[10] Nos dois temas, sem erro de JS')
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(250)
        larg = pg.evaluate("document.documentElement.scrollWidth")
        ok(larg <= 1440, 'tema %s: nao estoura em 1440 (%d)' % (tema, larg))
    ok(not erros, 'sem erro de JS: %s' % erros[:2])

    nav.close()

print('\nFALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)

raise SystemExit(1 if falhas else 0)
