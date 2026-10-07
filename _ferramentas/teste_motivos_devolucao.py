# -*- coding: utf-8 -*-
# Operacional → Motivos de Devolução. Nasceu em 07/out/2026 ANTES da tela de
# Devolução usar ele, de propósito: campo que aponta para um cadastro que não
# existe já custou caro aqui duas vezes.
#
# O que esta suíte protege são as decisões, não o desenho:
#
#   o motivo diz DE QUEM É A CONTA — sem isso o relatório só conta quantas voltaram
#   o motivo SUGERE o destino no estoque, e o destino não é só enfeite de cadastro
#   destino que muda o estoque avisa ANTES de salvar, não depois
#   motivo genérico pode EXIGIR descrição, senão seis meses depois ninguém sabe
#   nome duplicado é barrado: o relatório agrupa por motivo
#   inativar guarda a história das devoluções antigas; excluir apaga, e a tela diz
#   a trava nasce com a tela: criar, editar e excluir já estão no catálogo
#   e o catálogo existe nas telas que o LEEM, não só na que o usa
#   o item de menu saiu de inerte e leva a esta tela, nas 67 que têm o menu
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'
TELA = 'pagina-operacional-motivos-devolucao.html'

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
    pg.goto(URL + alvo)
    pg.wait_for_timeout(500)
    return pg

with sync_playwright() as pw:
    erros = []
    pg = nova(pw, TELA, erros)

    print('\n[1] A lista carrega e cada linha diz o que o motivo faz')
    n = pg.locator('#listaMotivos .motivo-card').count()
    ok(n > 0, 'a lista renderiza (%d motivos na pagina)' % n)
    corpo = pg.inner_text('#listaMotivos').lower()
    ok('volta revend' in corpo, 'a linha diz quando o item volta revendavel')
    ok('avaria' in corpo, 'e quando ele vai para Avaria')
    ok('bloqueado' in corpo, 'dizendo que entra bloqueado, nao so "avaria"')

    print('\n[2] De quem e a conta e um eixo proprio, nao um texto solto')
    grupos = pg.evaluate("Object.keys(GRUPOS)")
    ok(sorted(grupos) == ['cliente', 'fiscal', 'nossa', 'transporte'],
       'os quatro responsaveis existem: %s' % grupos)
    usados = pg.evaluate("Array.from(new Set(MOTIVOS.map(m => m.grupo)))")
    ok(len(usados) >= 3, 'o mock usa mais de um responsavel (%s)' % usados)
    fora = pg.evaluate("MOTIVOS.filter(m => !GRUPOS[m.grupo]).length")
    ok(fora == 0, 'nenhum motivo aponta para responsavel inexistente (%d fora)' % fora)
    badges = pg.locator('#listaMotivos .tipo-badge').count()
    ok(badges == n, 'toda linha mostra de quem e a conta (%d de %d)' % (badges, n))

    print('\n[3] O destino no estoque e escolha, e tem os tres casos reais')
    destinos = pg.evaluate("Object.keys(DESTINOS)")
    ok(sorted(destinos) == ['avaria', 'nenhum', 'revendavel'],
       'revendavel, avaria e "nao volta" existem: %s' % destinos)
    # Extravio e o caso que prova o terceiro: a mercadoria sumiu, o dinheiro se
    # resolve e o saldo nao se mexe. Sem ele, "nenhum" seria opcao teorica.
    temNenhum = pg.evaluate("MOTIVOS.some(m => m.destino === 'nenhum')")
    ok(temNenhum, 'o mock tem motivo em que a mercadoria NAO volta')
    foraD = pg.evaluate("MOTIVOS.filter(m => !DESTINOS[m.destino]).length")
    ok(foraD == 0, 'nenhum motivo aponta para destino inexistente (%d fora)' % foraD)

    print('\n[4] Destino que mexe no estoque avisa ANTES de salvar')
    pg.locator('#btnNovoMotivo').click(); pg.wait_for_timeout(400)
    ok(pg.locator('#notaAvaria:visible').count() == 0, 'no padrao revendavel nao ha aviso')
    pg.locator('#inputDestino .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#inputDestino .dropdown-select-item[data-value="avaria"]').click(); pg.wait_for_timeout(300)
    ok(pg.locator('#notaAvaria:visible').count() == 1, 'escolher Avaria mostra o aviso na hora')
    ok('bloqueado' in pg.inner_text('#notaAvaria').lower(), 'e o aviso diz que entra bloqueado')
    pg.locator('#inputDestino .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#inputDestino .dropdown-select-item[data-value="nenhum"]').click(); pg.wait_for_timeout(300)
    ok(pg.locator('#notaNenhum:visible').count() == 1, 'escolher "nao volta" troca o aviso')
    ok(pg.locator('#notaAvaria:visible').count() == 0, 'e esconde o anterior, em vez de empilhar os dois')

    print('\n[5] Nome vazio e nome repetido nao passam')
    pg.locator('#btnSalvarMotivo').click(); pg.wait_for_timeout(350)
    ok(pg.locator('#campoNomeMotivo.has-error').count() == 1, 'nome vazio e recusado')
    antes = pg.evaluate("MOTIVOS.length")
    repetido = pg.evaluate("MOTIVOS[0].nome")
    pg.fill('#inputNomeMotivo', repetido.upper())
    pg.locator('#btnSalvarMotivo').click(); pg.wait_for_timeout(350)
    ok(pg.locator('#campoNomeMotivo.has-error').count() == 1,
       'nome repetido e recusado mesmo com outra caixa: %s' % repetido)
    ok('já existe' in pg.inner_text('#erroNomeMotivo').lower(), 'e a mensagem diz por que')
    ok(pg.evaluate("MOTIVOS.length") == antes, 'nada foi gravado (%d)' % antes)

    print('\n[6] Cadastrar um motivo novo grava o que foi escolhido')
    pg.fill('#inputNomeMotivo', 'Pacote violado na entrega')
    pg.locator('#inputGrupo .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#inputGrupo .dropdown-select-item[data-value="transporte"]').click(); pg.wait_for_timeout(250)
    pg.locator('#inputDestino .dropdown-select-btn').click(); pg.wait_for_timeout(250)
    pg.locator('#inputDestino .dropdown-select-item[data-value="avaria"]').click(); pg.wait_for_timeout(250)
    pg.locator('#inputExigeObs').check(); pg.wait_for_timeout(200)
    pg.locator('#btnSalvarMotivo').click(); pg.wait_for_timeout(400)
    # Criar e rotina: o catalogo nao exige senha para criar, entao confirma e grava.
    if pg.locator('#confirmModal.open').count():
        pg.evaluate('() => window.scrollTo(0, 0)')
        pg.locator('#btnConfirmModalConfirmar').click(); pg.wait_for_timeout(400)
    novo = pg.evaluate("MOTIVOS.filter(m => m.nome === 'Pacote violado na entrega')[0] || null")
    ok(novo is not None, 'o motivo novo entrou na lista')
    if novo:
        ok(novo['grupo'] == 'transporte', 'com o responsavel escolhido: %s' % novo['grupo'])
        ok(novo['destino'] == 'avaria', 'com o destino escolhido: %s' % novo['destino'])
        ok(novo['exigeObs'] is True, 'e exigindo descricao, como foi marcado')

    print('\n[7] Exigir descricao e campo do cadastro, nao enfeite')
    # Quem le isto e a tela de Devolucao: ela usa o campo para obrigar o texto.
    temExige = pg.evaluate("MOTIVOS.some(m => m.exigeObs) && MOTIVOS.some(m => !m.exigeObs)")
    ok(temExige, 'o mock tem motivo que exige e motivo que nao exige')
    generico = pg.evaluate("MOTIVOS.filter(m => m.nome.toLowerCase() === 'outro')[0] || null")
    ok(generico is not None and generico['exigeObs'] is True,
       '"Outro", que e generico de proposito, exige descricao')

    print('\n[8] Inativar guarda a historia; excluir apaga, e a tela diz isso')
    pg.goto(URL + TELA); pg.wait_for_timeout(500)
    pg.locator('#listaMotivos .motivo-card').first.click(); pg.wait_for_timeout(400)
    pg.locator('#linkExcluirMotivo').click(); pg.wait_for_timeout(400)
    txt = pg.inner_text('#confirmModalTexto').lower()
    ok('inativar' in txt, 'o aviso de exclusao oferece o caminho que nao apaga')
    ok('devolu' in txt, 'e explica que as devolucoes antigas apontam para ele')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[9] A trava nasce com a tela')
    base = pg.evaluate("MODULOS_SENHA.filter(m => m.base === 'motivosDevolucao')[0] || null")
    ok(base is not None, 'o cadastro esta no catalogo de senhas')
    if base:
        ok(base['grupo'] == 'Operacional', 'no grupo Operacional: %s' % base['grupo'])
        ok(all(base['ligado'][v] for v in ['criar', 'editar', 'excluir']),
           'com os tres verbos: %s' % base['ligado'])

    print('\n[10] O catalogo existe nas telas que o LEEM, nao so nesta')
    for tela in ['pagina-configuracoes-confirmacoes-senha.html',
                 'pagina-configuracoes-registro-atividades.html']:
        p2 = nova(pw, tela, erros)
        achou = p2.evaluate("MODULOS_SENHA.some(m => m.base === 'motivosDevolucao')")
        ok(achou, 'o catalogo de %s conhece motivosDevolucao' % tela.replace('pagina-configuracoes-', ''))
        p2.close()

    print('\n[11] O item de menu deixou de ser inerte')
    pg.goto(URL + TELA); pg.wait_for_timeout(450)
    href = pg.evaluate("""() => {
      const el = Array.from(document.querySelectorAll('.flyout-item'))
        .filter(e => (e.getAttribute('data-label') || '').indexOf('Motivos de Devolu') === 0)[0];
      return el ? el.getAttribute('data-href') : null;
    }""")
    ok(href == TELA, 'o item do menu leva a esta tela: %s' % href)
    bc = pg.inner_text('#breadcrumb').lower()
    ok('operacional' in bc and 'motivos' in bc, 'o caminho diz Operacional > Motivos: %s' % bc.replace(chr(10), ' '))

    print('\n[12] Nos dois temas, sem erro de JS e sem estourar a largura')
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(250)
        est = pg.evaluate("""() => ({
          fonte: getComputedStyle(document.body).fontFamily,
          larg: document.documentElement.scrollWidth
        })""")
        ok('unito' in est['fonte'], 'tema %s: fonte Nunito' % tema)
        ok(est['larg'] <= 1440, 'tema %s: nao estoura em 1440 (%d)' % (tema, est['larg']))
    ok(not erros, 'sem erro de JS: %s' % erros[:2])

print('\nFALHAS: %d' % len(falhas))
for f in falhas: print('  - ' + f)

raise SystemExit(1 if falhas else 0)
