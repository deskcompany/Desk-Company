# -*- coding: utf-8 -*-
# Logística → Separação (fila e ficha). Nasceu em 02/out/2026 junto com o módulo
# e abre a F4. O que ele protege não é o desenho: são as decisões da barganha,
# que são exatamente as que um clone ou uma "melhoria" apagam sem fazer barulho.
#
#   a tela do separador NAO mostra valor nenhum — foi a primeira regra pedida
#   falta NAO e situacao: pedido com falta continua andando (design system §14.11/§14.14)
#   item sem resposta TRAVA a conclusao — coletado ou em falta, o silencio nao conta
#   o campo da quantidade achada nasce VAZIO (conferencia, nao confirmacao)
#   falta NAO baixa estoque aqui: vira divergencia aguardando reconferencia
#   sobra nao se resolve na separacao
#   a coleta sai na ordem do ENDERECO, e o parametro desliga isso
#   numero que decide cor vive no PARAM, nao dentro de um `if`
#   "separar o proximo" pega o mais velho da fila, e recusa quem ja tem pedido na mao
#   declarar falta e BOTAO, nao texto laranja, e ele muda de nome depois de usado
#   a quantidade grande e a que esta na CAIXA, nao a que o pedido pediu
#   as colunas das linhas alinham entre si, com falta ou sem
#   separacao parcial guarda sem devolver o pedido para a fila
#   o catalogo de acoes existe nas telas que o LEEM, nao so na que o usa
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
FILA = 'pagina-logistica-separacao.html'
FICHA = 'pagina-logistica-separacao-detalhe.html'

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
    pg.wait_for_timeout(500)
    return pg

# Modal e folha fixa no rodape: numa pagina rolada o clique direto esbarra na
# conta de coordenadas do proprio playwright, nao na tela. Sobe antes de clicar.
def confirmar(pg):
    pg.evaluate('() => window.scrollTo(0, 0)')
    pg.click('#btnConfirmModalConfirmar')
    pg.wait_for_timeout(300)

def texto_modal(pg):
    return pg.locator('#confirmModalTexto').inner_text()


with sync_playwright() as pw:
    erros = []

    # ---------------------------------------------------------------- 1
    print('\n1. A FILA ABRE, CONTA E ORDENA PELA ESPERA')
    pg = nova(pw, FILA, erros)
    ok(pg.locator('#corpoTabela tr').count() > 0, 'a fila renderiza linhas')
    conts = pg.locator('#abasSituacao .sit-contador').all_inner_texts()
    ok(len(conts) == 4, 'quatro abas de situacao (todas + as tres do trabalho): %d' % len(conts))
    ok(int(conts[0]) == int(conts[1]) + int(conts[2]) + int(conts[3]),
       'o contador de "todas" e a soma dos tres: %s' % conts)
    esperas = pg.evaluate("""() => Array.from(document.querySelectorAll('#corpoTabela tr'))
        .map(tr => tr.children[7].firstElementChild.className)""")
    ok(esperas[0] == 'espera-critica', 'a fila abre pelo que espera ha mais tempo: %s' % esperas[0])

    # ---------------------------------------------------------------- 2
    print('\n2. A TELA DO SEPARADOR NAO MOSTRA VALOR NENHUM')
    corpo = pg.locator('.main').inner_text()
    ok('R$' not in corpo, 'nenhum "R$" na fila')
    # "Preco" solto nao serve de asserção: existe cliente chamado Móveis Bom
    # Preço Ltda. O que nao pode aparecer e RÓTULO de valor.
    for palavra in ['Desconto', 'Total do pedido', 'Preço unitário', 'Margem', 'Valor do pedido']:
        ok(palavra not in corpo, 'a fila nao mostra "%s"' % palavra)
    pg.locator('#corpoTabela tr').first.click()
    pg.wait_for_timeout(350)
    drawer = pg.locator('#eventDrawer').inner_text()
    ok('R$' not in drawer, 'nenhum "R$" no painel do pedido')
    ok('Entregar em' in drawer or 'ENTREGAR EM' in drawer.upper(), 'o painel mostra o endereco de entrega')
    ok('R0' in drawer or 'B0' in drawer, 'o painel mostra o endereco de estoque dos itens')

    # ---------------------------------------------------------------- 3
    print('\n3. FALTA E MARCA, NAO SITUACAO')
    abas = pg.locator('#abasSituacao .aba-sit').all_inner_texts()
    ok(not any('falta' in a.lower() for a in abas), 'nenhuma aba de situacao chamada falta: %s' % abas)
    comFalta = pg.evaluate("""() => {
        const tr = Array.from(document.querySelectorAll('#corpoTabela tr'))
          .filter(x => x.querySelector('.marca-falta'))[0];
        return tr ? tr.children[8].innerText.trim() : null;
    }""")
    ok(comFalta is not None, 'existe pedido com a marca de falta na fila')
    ok(comFalta and 'SEPARADO' in comFalta.upper(),
       'pedido com falta continua na situacao normal do fluxo: %s' % comFalta)

    # ---------------------------------------------------------------- 4
    print('\n4. O MENU LOGISTICA LEVA A TELA, E A TELA LEVA A FICHA')
    destino = pg.get_attribute('.flyout-item[data-label="Separação"]', 'data-href')
    ok(localiza.nome(destino) == FILA, 'o item de menu Separacao aponta para a tela: %s' % destino)
    pg.click('#btnAbrirSeparacao')
    pg.wait_for_timeout(600)
    ok(FICHA in pg.url, 'o painel abre a ficha do pedido: %s' % pg.url.split('/')[-1])
    ok('?id=' in pg.url, 'a ficha recebe o id do pedido')

    # ---------------------------------------------------------------- 5
    print('\n5. SEPARAR O PROXIMO PEGA O MAIS VELHO, E SO UM POR VEZ')
    pg = nova(pw, FILA, erros)
    pg.click('#btnSepararProximo')
    pg.wait_for_timeout(300)
    t = texto_modal(pg)
    # #5 e o mais antigo AGUARDANDO; #6 espera mais, mas ja esta com outra pessoa.
    ok('#5' in t, 'oferece o mais antigo da fila, nao o mais antigo da tela: %s' % t[:60])
    ok('#6' not in t, 'nao oferece pedido que ja esta na mao de outro separador')
    pg.click('#btnConfirmModalCancelar')
    pg.wait_for_timeout(200)
    pg.evaluate("() => { FILA.filter(p => p.id === 20)[0].operador = EU; }")
    pg.click('#btnSepararProximo')
    pg.wait_for_timeout(300)
    ok('já está com o pedido' in texto_modal(pg), 'recusa um segundo pedido na mao: %s' % texto_modal(pg)[:60])
    confirmar(pg)

    # ---------------------------------------------------------------- 6
    print('\n6. NUMERO QUE DECIDE COR VIVE NO PARAM')
    pg = nova(pw, FILA, erros)
    antes = pg.evaluate("""() => Array.from(document.querySelectorAll('#corpoTabela tr'))
        .map(tr => tr.children[7].firstElementChild.className)""")
    pg.evaluate("""() => { PARAM.separacaoAlertaHoras = 999; PARAM.separacaoCriticoHoras = 1000; renderTabela(); }""")
    depois = pg.evaluate("""() => Array.from(document.querySelectorAll('#corpoTabela tr'))
        .map(tr => tr.children[7].firstElementChild.className)""")
    ok('espera-critica' in antes and 'espera-critica' not in depois,
       'subir o parametro apaga o alerta — a regra nao esta dentro de um if')
    ok(pg.evaluate("() => typeof PARAM.separacaoOrdemPorEndereco") == 'boolean',
       'a ordem por endereco e parametro, nao decisao do codigo')

    # ---------------------------------------------------------------- 7
    print('\n7. A FICHA ABRE SEM VALOR, COM ENDERECO E NA ORDEM DA COLETA')
    pg = nova(pw, FICHA + '?id=18', erros)
    corpo = pg.locator('.main').inner_text()
    ok('R$' not in corpo, 'nenhum "R$" na ficha do separador')
    ok('Entregar em'.upper() in corpo.upper(), 'a ficha mostra o endereco de entrega')
    ends = pg.evaluate("""() => Array.from(document.querySelectorAll('.sep-item .endereco-chip')).map(e => e.innerText)""")
    ok(len(ends) == 3, 'os tres itens do pedido 18 aparecem: %d' % len(ends))
    ok(ends == sorted(ends), 'os itens saem na ordem do endereco: %s' % ends)
    ok(ends != ['B02-G01-N2', 'B01-G02-N1', 'B01-G02-N4'], 'e nao na ordem em que o cliente escolheu')
    pg.evaluate("() => { PARAM.separacaoOrdemPorEndereco = false; pintarItens(); }")
    ends2 = pg.evaluate("""() => Array.from(document.querySelectorAll('.sep-item .endereco-chip')).map(e => e.innerText)""")
    ok(ends2 != ends, 'desligar o parametro devolve a ordem do pedido: %s' % ends2)

    # ---------------------------------------------------------------- 8
    print('\n8. O CAMPO DA QUANTIDADE ACHADA NASCE VAZIO')
    pg = nova(pw, FICHA + '?id=18', erros)
    pg.locator('.sep-item').first.locator('.sep-falta-btn').click()
    pg.wait_for_timeout(200)
    valor = pg.locator('.sep-item').first.locator('[data-qtd]').input_value()
    ok(valor == '', 'o campo comeca em branco — conferencia, nao confirmacao: "%s"' % valor)
    pedida = pg.locator('.sep-item').first.locator('.sep-item-qtd').inner_text()
    ok(valor != pedida.split('\n')[0], 'o campo nao vem preenchido com a quantidade esperada')

    # ---------------------------------------------------------------- 9
    print('\n9. FALTA SEM RESPOSTA, SEM MOTIVO E COM SOBRA SAO RECUSADAS')
    pg.locator('.sep-item').first.locator('[data-confirma-falta]').click()
    pg.wait_for_timeout(250)
    ok('Informe quantas peças' in texto_modal(pg), 'campo vazio e recusado: %s' % texto_modal(pg)[:50])
    confirmar(pg)
    pg.locator('.sep-item').first.locator('[data-qtd]').fill('9')
    pg.locator('.sep-item').first.locator('[data-confirma-falta]').click()
    pg.wait_for_timeout(250)
    t = texto_modal(pg)
    ok('Acerto de Estoque' in t, 'sobra nao se resolve na separacao — manda para o acerto: %s' % t[:60])
    confirmar(pg)
    pg.locator('.sep-item').first.locator('[data-qtd]').fill('1')
    pg.locator('.sep-item').first.locator('[data-confirma-falta]').click()
    pg.wait_for_timeout(250)
    ok('Escreva o que aconteceu' in texto_modal(pg), 'falta sem motivo e recusada')
    confirmar(pg)

    # ---------------------------------------------------------------- 10
    print('\n10. A FALTA NAO BAIXA ESTOQUE — VIRA DIVERGENCIA')
    pg.locator('.sep-item').first.locator('[data-motivo]').fill('Endereço vazio')
    pg.locator('.sep-item').first.locator('[data-confirma-falta]').click()
    pg.wait_for_timeout(250)
    t = texto_modal(pg)
    ok('divergência' in t, 'a confirmacao diz que vira divergencia: %s' % t[:70])
    ok('não é alterado' in t or 'não é baixado' in t, 'a confirmacao diz que o saldo nao muda')
    ok('Conferência de Saída' in t, 'a confirmacao diz para onde o pedido vai mesmo com falta')
    confirmar(pg)
    ok(pg.locator('.sep-item').first.locator('.sep-falta-btn.tem-falta').count() == 1,
       'a linha passa a oferecer a correcao, com a tinta de alerta')

    # --------------------------------------------------------------- 10b
    # Falta registrada e item RESPONDIDO. Enquanto a linha continuava com a
    # mesma cara de item intocado, o operador varria a lista de cima a baixo
    # procurando o que ja tinha resolvido — e o item respondido mais provavel
    # de ser respondido duas vezes e justamente o que deu problema.
    print('\n10b. FALTA REGISTRADA FICA RESPONDIDA, SEM VIRAR COLETA LIMPA')
    pg.fill('#campoBipar', 'CAB-SAT-050')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(250)
    estados = pg.evaluate("""() => Array.from(document.querySelectorAll('.sep-item')).map(d => {
        const c = d.querySelector('.item-checkbox');
        return { falta: d.classList.contains('falta'), respondido: d.classList.contains('respondido'),
                 check: c.checked, meio: c.indeterminate,
                 risco: getComputedStyle(d.querySelector('.sep-item-nome')).textDecorationLine };
    })""")
    comFalta = [e for e in estados if e['falta']]
    limpos = [e for e in estados if e['respondido'] and not e['falta']]
    intocados = [e for e in estados if not e['respondido']]
    ok(len(comFalta) == 1 and len(limpos) == 1 and len(intocados) == 1,
       'os tres estados convivem na mesma lista: %s' % estados)
    ok(comFalta[0]['respondido'] and 'line-through' in comFalta[0]['risco'],
       'a linha da falta fica riscada, igual a coletada — ela foi respondida')
    ok(comFalta[0]['meio'] and not comFalta[0]['check'],
       'mas a marca e INTERMEDIARIA, nunca cheia: cheia diria que coletou tudo')
    ok(limpos[0]['check'] and not limpos[0]['meio'], 'coleta inteira fica com a marca cheia')
    ok(not intocados[0]['check'] and not intocados[0]['meio'] and 'line-through' not in intocados[0]['risco'],
       'item sem resposta nao ganha nenhum dos dois sinais')

    # --------------------------------------------------------------- 10c
    # O usuario olhou a tela e nao viu um botao: texto laranja solto nao
    # convida clique. E a quantidade grande mostrava o que o pedido PEDIU,
    # com o coletado em miudo — invertendo a pergunta que a proxima etapa faz.
    print('\n10c. DECLARAR FALTA E BOTAO, E A QUANTIDADE E A DA CAIXA')
    linhas = pg.evaluate("""() => Array.from(document.querySelectorAll('.sep-item')).map(d => {
        const btn = d.querySelector('.sep-falta-btn');
        const acao = d.querySelector('.sep-item-acao').getBoundingClientRect();
        return { tag: btn ? btn.tagName : null, rotulo: btn ? btn.innerText.trim() : null,
                 temFalta: btn ? btn.classList.contains('tem-falta') : false,
                 qtd: d.querySelector('.sep-item-qtd').innerText.split('\\n')[0].trim(),
                 acaoLeft: Math.round(acao.left) };
    })""")
    ok(all(l['tag'] == 'BUTTON' for l in linhas), 'declarar falta e um BUTTON em toda linha: %s' % [l['tag'] for l in linhas])
    comFalta = [l for l in linhas if l['temFalta']]
    semFalta = [l for l in linhas if not l['temFalta']]
    ok(len(comFalta) == 1, 'so a linha com falta carrega a tinta de alerta')
    ok(comFalta[0]['rotulo'] == 'corrigir separação',
       'usado, o botao passa a dizer o que ele faz agora: "%s"' % comFalta[0]['rotulo'])
    ok(all(l['rotulo'] == 'não achei tudo' for l in semFalta),
       'nas outras ele continua oferecendo a declaracao: %s' % [l['rotulo'] for l in semFalta])
    ok(comFalta[0]['qtd'] == '1',
       'o numero grande e o que esta na CAIXA (1), nao o que o pedido pediu (2): %s' % comFalta[0]['qtd'])
    ok(len(set(l['acaoLeft'] for l in linhas)) == 1,
       'as colunas alinham entre as linhas, com falta ou sem: %s' % [l['acaoLeft'] for l in linhas])

    # --------------------------------------------------------------- 10d
    # Pedido de 40 itens nao cabe num turno. Sem isto a escolha era concluir
    # mentindo ou devolver para a fila e jogar fora o que ja tinha andado.
    print('\n10d. SEPARACAO PARCIAL GUARDA SEM DEVOLVER O PEDIDO')
    pg2 = nova(pw, FICHA + '?id=18', erros)
    pg2.click('#btnSalvarParcial')
    pg2.wait_for_timeout(300)
    ok('não há contagem para guardar' in texto_modal(pg2),
       'sem nenhum item respondido nao ha o que guardar: %s' % texto_modal(pg2)[:60])
    confirmar(pg2)
    pg2.fill('#campoBipar', 'SSD-NVM-001')
    pg2.press('#campoBipar', 'Enter')
    pg2.wait_for_timeout(250)
    pg2.click('#btnSalvarParcial')
    pg2.wait_for_timeout(300)
    t = texto_modal(pg2)
    ok('1 de 3' in t, 'a confirmacao diz quanto ja foi respondido: %s' % t[:60])
    ok('não volta para a fila' in t, 'e deixa claro que o pedido NAO volta para a fila dos outros')
    ok('Devolver este pedido para a fila' in t, 'e aponta qual acao serve para liberar de verdade')
    fonte = pg2.evaluate("() => salvarParcial.toString()")
    ok("situacao = 'separando'" in fonte, 'guardar deixa o pedido EM SEPARACAO')
    ok("situacao = 'fila'" not in fonte, 'guardar NUNCA devolve o pedido para a fila — devolver e outra acao')
    ok('operador = EU' in fonte, 'e o pedido continua no nome de quem guardou')
    confirmar(pg2)
    pg2.wait_for_timeout(900)
    ok(FILA in pg2.url, 'guardar leva de volta para a fila do galpao: %s' % pg2.url.split('/')[-1])

    # ---------------------------------------------------------------- 11
    print('\n11. ITEM SEM RESPOSTA TRAVA A CONCLUSAO')
    pg.click('#btnConcluir')
    pg.wait_for_timeout(300)
    t = texto_modal(pg)
    ok('sem resposta' in t, 'concluir com item intocado e recusado: %s' % t[:60])
    ok('MEM-DDR-016' in t or 'SSD-NVM-001' in t or 'CAB-SAT-050' in t, 'a recusa diz QUAIS itens faltam responder')
    confirmar(pg)
    ok(pg.locator('#blocoEntrega .badge-situacao').inner_text().upper() != 'SEPARADO',
       'o pedido nao avancou com item sem resposta')

    # ---------------------------------------------------------------- 12
    print('\n12. BIPAR COLETA O ITEM INTEIRO, E SO O QUE E DO PEDIDO')
    pg.fill('#campoBipar', 'SKU-QUE-NAO-EXISTE')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(200)
    ok('não está neste pedido' in pg.locator('#ecoBipar').inner_text(), 'sku de fora nao marca nada')
    antes = pg.evaluate("() => COLETA.filter(i => i.separado !== null).length")
    pg.fill('#campoBipar', 'mem-ddr-016')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(250)
    depois = pg.evaluate("() => COLETA.filter(i => i.separado !== null).length")
    ok(depois == antes + 1, 'bipar marca um item (e nao e sensivel a maiuscula)')
    ok(pg.evaluate("() => COLETA.filter(i => i.sku === 'MEM-DDR-016')[0].separado") == 2,
       'bipar marca a quantidade INTEIRA do item')

    # ---------------------------------------------------------------- 13
    print('\n13. CONCLUIR COM FALTA ANDA, E FICA NO REGISTRO')
    pg.fill('#campoBipar', 'CAB-SAT-050')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(250)
    pg.click('#btnConcluir')
    pg.wait_for_timeout(300)
    t = texto_modal(pg)
    ok('em falta' in t, 'a confirmacao da conclusao avisa da falta: %s' % t[:60])
    confirmar(pg)
    ok('reconferência' in texto_modal(pg), 'o aviso final manda para a reconferencia')
    confirmar(pg)
    ok(pg.locator('#blocoEntrega .badge-situacao').inner_text().upper() == 'SEPARADO',
       'o pedido com falta ANDOU — nao travou')
    ok(pg.locator('#btnConcluir').is_disabled(), 'concluido nao se conclui de novo')
    chaves = pg.evaluate("() => JSON.parse(localStorage.getItem('deskLog')||'[]').map(x => x.chave)")
    ok('separacaoConclui' in chaves, 'a conclusao foi para o registro de atividades')
    ok('separacaoFalta' in chaves, 'a falta foi para o registro de atividades')

    # ---------------------------------------------------------------- 14
    print('\n14. SEM FALTA, A CONCLUSAO NAO INVENTA DIVERGENCIA')
    pg = nova(pw, FICHA + '?id=22', erros)
    pg.fill('#campoBipar', 'CAD-FIX-110')
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(250)
    pg.click('#btnConcluir')
    pg.wait_for_timeout(300)
    t = texto_modal(pg)
    ok('falta' not in t, 'conclusao limpa nao fala em falta: %s' % t[:70])
    ok('Conferência de Saída' in t, 'conclusao limpa diz para onde o pedido vai')
    confirmar(pg)
    ok('divergência' not in texto_modal(pg), 'conclusao limpa nao cria divergencia')
    confirmar(pg)

    # ---------------------------------------------------------------- 15
    print('\n15. ID QUE NAO EXISTE AVISA EM VEZ DE ABRIR CALADO')
    pg = nova(pw, FICHA + '?id=99999', erros)
    ok('não está na fila' in texto_modal(pg), 'id inexistente avisa: %s' % texto_modal(pg)[:60])
    confirmar(pg)
    ok(pg.locator('.sep-item').count() > 0, 'e ainda assim abre num pedido de verdade')

    # ---------------------------------------------------------------- 16
    print('\n16. A FOLHA IMPRESSA NAO LEVA VALOR PARA FORA DO GALPAO')
    pg.evaluate('() => montarFolha()')
    folha = pg.evaluate("() => document.getElementById('listaFolha').innerText")
    ok('R$' not in folha, 'a folha de separacao nao tem valor')
    ok('Separador:' in folha, 'a folha tem onde assinar quem separou')
    ok(pg.evaluate("() => document.getElementById('listaFolha').classList.contains('oculta')"),
       'a folha fica escondida fora da impressao')

    # ---------------------------------------------------------------- 17
    print('\n17. AS ACOES DA SEPARACAO NASCERAM COM A TELA')
    pg = nova(pw, FILA, erros)
    cat = pg.evaluate("() => ACOES_SENHA.filter(a => a.chave.indexOf('separacao') === 0).map(a => a.chave + '/' + a.ligado)")
    for chave in ['separacaoAssume', 'separacaoConclui', 'separacaoFalta', 'separacaoReabre']:
        ok(any(c.startswith(chave + '/') for c in cat), 'o catalogo conhece %s' % chave)
    ok(all(c.endswith('/True') or c.endswith('/true') for c in cat), 'nenhuma delas e celula morta: %s' % cat)
    ok(pg.evaluate("() => exigeSenha('separacaoReabre')"), 'reabrir separacao ja concluida pede senha')
    ok(not pg.evaluate("() => exigeSenha('separacaoConclui')"), 'concluir nao pede senha — trabalho normal de galpao')
    ok(any(c.startswith('separacaoParcial/') for c in cat), 'o catalogo conhece separacaoParcial')

    # O catalogo e UMA lista. Ontem eu construi o modulo e esqueci de levar as
    # celulas para as telas que LEEM o catalogo: a acao acontecia, gravava no
    # registro, e Configuracoes nao tinha onde ligar a trava. Matriz que nao
    # mostra a acao e matriz que mente.
    CHAVES = ['separacaoAssume', 'separacaoConclui', 'separacaoFalta', 'separacaoParcial', 'separacaoReabre']
    for tela in ['pagina-configuracoes-confirmacoes-senha.html',
                 'pagina-cadastros-vendedores-detalhe.html',
                 'pagina-configuracoes-registro-atividades.html']:
        pgc = nova(pw, tela, erros)
        achadas = pgc.evaluate("() => ACOES_SENHA.map(a => a.chave)")
        faltando = [k for k in CHAVES if k not in achadas]
        ok(not faltando, '%s conhece as acoes da separacao%s' % (tela.replace('pagina-', ''), '' if not faltando else ' — falta ' + ', '.join(faltando)))

    print('\nERROS DE CONSOLE: ' + (str(erros) if erros else 'nenhum'))
    if erros: falhas.append('erro de console: %s' % erros)

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
