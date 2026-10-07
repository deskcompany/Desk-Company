# -*- coding: utf-8 -*-
# Logística → Expedição (fila da doca e romaneio). Nasceu em 06/out/2026 e fecha
# o trio do galpão: Separação → Conferência de Saída → Expedição.
#
# O que esta suíte protege são as decisões da barganha e da pesquisa de doze
# sistemas — exatamente as que um clone ou uma "melhoria" apagam sem barulho:
#
#   o romaneio NASCE sugerido, por forma de envio x dia de coleta, e so por isso
#   um romaneio = UMA forma de envio (regra do Magis5/Bling/Omie)
#   o dia de coleta sai do CADASTRO: so dia que ela coleta, e hoje so antes do corte
#   retirada no balcao nao tem dia de coleta — logo nao entra em romaneio, e a tela diz
#   a tela escreve por que um pedido pronto ficou de fora, em vez de deixar deduzir
#   a conferencia e por VOLUME, mas a carga e por PEDIDO: incompleto volta inteiro
#   peso bruto e a UNICA trava numerica, e ele nasce na doca porque a balanca esta la
#   o desvio de peso compara com o que foi BIPADO, nao com o romaneio inteiro
#   MDF-e so em carga propria, e e aviso por parametro por UF — nunca trava fixa
#   etiqueta de outro romaneio avisa; etiqueta repetida avisa e NAO desmarca
#   bipar o primeiro volume ja move de "em montagem" para "conferindo"
#   nada e estornado ao tirar/cancelar/despachar parcial: a baixa so acontece no despacho
#   o romaneio sai em DUAS vias com assinatura, e nao e documento fiscal
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
FILA = 'pagina-logistica-expedicao.html'
ROM = 'pagina-logistica-expedicao-detalhe.html'

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

# Modal e folha fixa no rodape: numa pagina rolada o clique direto esbarra na
# conta de coordenadas do proprio playwright, nao na tela. Sobe antes de clicar.
def confirmar(pg):
    pg.evaluate('() => window.scrollTo(0, 0)')
    pg.click('#btnConfirmModalConfirmar')
    pg.wait_for_timeout(350)

def texto_modal(pg):
    return pg.locator('#confirmModalTexto').inner_text()

def bipar(pg, codigo):
    pg.fill('#campoBipar', codigo)
    pg.press('#campoBipar', 'Enter')
    pg.wait_for_timeout(140)


with sync_playwright() as pw:
    erros = []

    # ---------------------------------------------------------------- 1
    print('\n1. A FILA ABRE COM OS ROMANEIOS JA SUGERIDOS')
    pg = nova(pw, FILA, erros)
    linhas = pg.locator('#corpoTabela tr').count()
    ok(linhas >= 8, 'a fila renderiza os romaneios do mock mais os sugeridos: %d' % linhas)
    sugeridos = pg.locator('.marca-sugerido').count()
    ok(sugeridos > 0, 'pelo menos um romaneio carrega a marca "sugerido": %d' % sugeridos)
    criados = pg.evaluate("() => ROMANEIOS.filter(r => r.id >= 'ROM-0192').map(r => r.id)")
    ok(len(criados) >= 3, 'a sugestao criou romaneios na abertura: %s' % criados)
    conts = pg.locator('#abasSituacao .sit-contador').all_inner_texts()
    ok(len(conts) == 4, 'quatro abas (todas + as tres do trabalho): %d' % len(conts))
    ok(int(conts[0]) == int(conts[1]) + int(conts[2]) + int(conts[3]),
       'o contador de "todos" e a soma dos tres: %s' % conts)

    # ---------------------------------------------------------------- 2
    print('\n2. UM ROMANEIO = UMA FORMA DE ENVIO, UM DIA DE COLETA')
    misturado = pg.evaluate("""() => {
      const chaves = {};
      let erro = null;
      ROMANEIOS.forEach(r => {
        const ps = PRONTOS.filter(p => p.romaneio === r.id);
        ps.forEach(p => { if (p.transp !== r.transp) erro = r.id + ' mistura transportadora'; });
        const k = r.transp + '|' + r.coleta + '|' + r.situacao;
        if (r.situacao === 'montagem' && chaves[k]) erro = 'dois romaneios abertos para ' + k;
        chaves[k] = true;
      });
      return erro;
    }""")
    ok(not misturado, 'nenhum romaneio mistura formas de envio nem duplica o par transportadora+dia%s'
       % ('' if not misturado else ': ' + str(misturado)))

    # ---------------------------------------------------------------- 3
    print('\n3. O DIA DE COLETA SAI DO CADASTRO, COM CORTE')
    # Correios PAC coleta seg-sex com corte 16:00. As 15:20 de uma terca, hoje
    # ainda vale; as 16:30 ja nao vale e a carga cai no dia seguinte.
    antes = pg.evaluate("() => proximaColeta(1, new Date('2026-10-06T15:20:00'))")
    depois = pg.evaluate("() => proximaColeta(1, new Date('2026-10-06T16:30:00'))")
    ok(antes == '2026-10-06', 'pronto antes do corte entra na coleta de hoje: %s' % antes)
    ok(depois == '2026-10-07', 'pronto depois do corte cai no proximo dia: %s' % depois)
    # RotaSul coleta so terca e quinta.
    rota = pg.evaluate("() => proximaColeta(3, new Date('2026-10-07T09:00:00'))")
    ok(rota == '2026-10-08', 'quem coleta ter/qui pula a quarta: %s' % rota)
    # Retirada no balcao nao tem dia: devolve NULO, e nulo quer dizer "fica fora".
    ok(pg.evaluate("() => proximaColeta(9, new Date('2026-10-06T09:00:00')) === null"),
       'retirada no balcao nao tem dia de coleta — devolve nulo, nao erro')
    ok(pg.evaluate("() => PRONTOS.filter(p => p.transp === 9).every(p => !p.romaneio)"),
       'e por isso ela nunca entra em romaneio')

    # ---------------------------------------------------------------- 4
    print('\n4. A TELA DIZ O QUE FICOU DE FORA, E POR QUE')
    aviso = pg.locator('#avisoFilaTexto').inner_text()
    ok('saem hoje' in aviso, 'o aviso conta quantos saem hoje: %s' % aviso)
    ok('próximo dia de coleta' in aviso, 'conta quantos esperam o proximo dia de coleta')
    ok('retirada no balcão' in aviso, 'e diz que a retirada no balcao nao entra em romaneio')

    # ---------------------------------------------------------------- 5
    print('\n5. PESO BRUTO AUSENTE APARECE COMO FALTA, NUNCA COMO ZERO')
    pend = pg.locator('.peso-pendente').count()
    ok(pend > 0, 'romaneio sem balanca mostra "falta pesar", nao 0: %d linha(s)' % pend)
    zeros = pg.evaluate("""() => Array.from(document.querySelectorAll('#corpoTabela tr'))
        .map(tr => tr.children[5].innerText.trim()).filter(x => x === '0' || x === '0,0 kg').length""")
    ok(zeros == 0, 'nenhuma linha mostra peso zero no lugar de "falta pesar"')

    # ---------------------------------------------------------------- 6
    print('\n6. MONTAR ROMANEIO: A FORMA DE ENVIO E A PRIMEIRA ESCOLHA')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(250)
    pg.click('#menuMaisAcoes .dropdown-select-item[data-acao="montar"]'); pg.wait_for_timeout(400)
    ok(pg.locator('#montarDrawer').evaluate("el => el.classList.contains('open')"), 'o painel de montar abre')
    itens = pg.locator('#menuMontarTransp .dropdown-select-item').count()
    ok(itens == 7, 'so transportadora COM dia de coleta aparece (a retirada fica fora): %d' % itens)
    pg.click('#montarTransp .dropdown-select-btn'); pg.wait_for_timeout(250)
    pg.click('#menuMontarTransp .dropdown-select-item[data-value="3"]'); pg.wait_for_timeout(350)
    dias = pg.locator('#menuMontarColeta .dropdown-select-item').all_inner_texts()
    ok(len(dias) == 4, 'o painel oferece os proximos 4 dias de coleta DELA: %s' % dias)
    ok(all(('terça' in d or 'quinta' in d) for d in dias),
       'e so terca e quinta, que e o que a RotaSul coleta: %s' % dias)
    pg.click('#btnMontarCancelar'); pg.wait_for_timeout(300)

    # ---------------------------------------------------------------- 7
    print('\n7. CANCELAR DEVOLVE OS PEDIDOS, E NADA E ESTORNADO')
    pg.click('#corpoTabela tr:has-text("ROM-0192")'); pg.wait_for_timeout(400)
    ok(pg.locator('#eventDrawer').evaluate("el => el.classList.contains('open')"), 'a linha abre o resumo do romaneio')
    antes_fora = pg.evaluate("() => PRONTOS.filter(p => !p.romaneio).length")
    pg.click('#btnCancelarRomaneio'); pg.wait_for_timeout(400)
    texto = texto_modal(pg)
    ok('Nada é estornado' in texto, 'a confirmacao explica que nada e estornado: %s' % texto[:110])
    confirmar(pg)
    pg.wait_for_timeout(300)
    # o aviso que vem depois precisa APARECER (a folha fecha antes de executar)
    ok(pg.locator('#confirmModal').evaluate("el => el.classList.contains('open')"),
       'o aviso que o callback abre fica visivel — a folha fecha ANTES de executar')
    ok('cancelado' in texto_modal(pg), 'e o aviso diz o que aconteceu: %s' % texto_modal(pg)[:90])
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
    depois_fora = pg.evaluate("() => PRONTOS.filter(p => !p.romaneio).length")
    ok(depois_fora > antes_fora, 'os pedidos voltaram para a fila de prontos: %d -> %d' % (antes_fora, depois_fora))
    ok(pg.evaluate("() => ROMANEIOS.filter(r => r.id === 'ROM-0192').length") == 0, 'e o romaneio deixou de existir')

    # ---------------------------------------------------------------- 8
    print('\n8. RODAR A SUGESTAO DE NOVO REMONTA O QUE VOLTOU')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(250)
    pg.click('#menuMaisAcoes .dropdown-select-item[data-acao="sugerir"]'); pg.wait_for_timeout(450)
    ok('Sugestão rodada' in texto_modal(pg), 'a sugestao diz o que fez: %s' % texto_modal(pg)[:80])
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)
    fora = pg.evaluate("() => PRONTOS.filter(p => !p.romaneio).map(p => p.transp)")
    ok(all(t == 9 for t in fora), 'depois da sugestao so sobra a retirada no balcao: %s' % fora)

    # ---------------------------------------------------------------- 9
    print('\n9. O CATALOGO DE ACOES DA EXPEDICAO')
    cat = pg.evaluate("""() => ACOES_SENHA.filter(a => (a.chave || '').indexOf('expedicao') === 0)
        .map(a => a.chave + '/' + a.exigePadrao)""")
    ok(len(cat) == 5, 'cinco acoes especificas de Expedicao: %s' % cat)
    ok(pg.evaluate("() => exigeSenha('expedicaoReabre')"), 'reabrir romaneio despachado PEDE senha')
    for chave in ['expedicaoMonta', 'expedicaoTiraPedido', 'expedicaoCancela', 'expedicaoDespacha']:
        ok(not pg.evaluate("() => exigeSenha('%s')" % chave), '%s nao pede senha — trabalho normal de doca' % chave)

    # ---------------------------------------------------------------- 10
    print('\n10. O ROMANEIO: CONFERENCIA POR VOLUME')
    pg2 = nova(pw, ROM, erros)
    ok(pg2.locator('#tituloRom').inner_text() == 'Romaneio ROM-0192', 'o romaneio abre pelo id padrao')
    ok(pg2.locator('#totVolumes').inner_text() == '0 de 10', 'dez volumes, nenhum bipado ainda')
    ok(pg2.locator('#totPedidos').inner_text() == '0 de 2', 'nenhum pedido completo ainda')
    ok(pg2.locator('#badgeSituacao').inner_text().strip().upper().startswith('CONFERINDO') or
       pg2.locator('#badgeSituacao').inner_text().strip().upper().startswith('EM MONTAGEM'),
       'a situacao sai do mock, nao de um botao')

    bipar(pg2, 'VOL-0026-1')
    ok(pg2.locator('#totVolumes').inner_text() == '1 de 10', 'uma leitura marca UM volume')
    ok('VOL-0026-1' in pg2.locator('#ecoBipar').inner_text(), 'o eco confirma qual volume entrou')
    bipar(pg2, 'VOL-0026-1')
    ok(pg2.locator('#totVolumes').inner_text() == '1 de 10',
       'etiqueta repetida NAO desmarca — leitor dispara duas vezes com facilidade')
    ok('já estava' in pg2.locator('#ecoBipar').inner_text(), 'e o eco avisa que ela ja estava conferida')

    bipar(pg2, 'VOL-9999-1')
    ok('não pertence a este romaneio' in texto_modal(pg2),
       'etiqueta de outra carga avisa — e exatamente isso que esta conferencia pega')
    pg2.click('#btnConfirmModalConfirmar'); pg2.wait_for_timeout(250)
    ok(pg2.locator('#totVolumes').inner_text() == '1 de 10', 'e nao marca nada')

    # ---------------------------------------------------------------- 11
    print('\n11. A CONFERENCIA E POR VOLUME, MAS A CARGA E POR PEDIDO')
    for i in range(2, 7):
        bipar(pg2, 'VOL-0026-%d' % i)
    ok(pg2.locator('#totVolumes').inner_text() == '6 de 10', 'seis volumes bipados')
    ok(pg2.locator('#totPedidos').inner_text() == '1 de 2', 'e UM pedido completo — o outro nao tem volume nenhum')
    ok(pg2.locator('.marca-completo').count() == 1, 'o pedido inteiro ganha a marca "completo"')
    ok(pg2.is_visible('#blocoParcial'), 'a tela avisa que a carga vai sair incompleta')
    ok('#25' in pg2.locator('#textoParcial').inner_text(), 'e diz QUAL pedido fica: %s' % pg2.locator('#textoParcial').inner_text()[:90])
    ok('volta inteiro' in pg2.locator('#textoParcial').inner_text(),
       'e que ele volta INTEIRO — pedido nao embarca pela metade')
    bipar(pg2, 'VOL-0025-2')
    ok(pg2.locator('.marca-parcial').count() == 1, 'pedido comecado e nao terminado fica marcado como incompleto')
    ok(pg2.locator('#totPedidos').inner_text() == '1 de 2', 'e continua nao contando como completo')

    # ---------------------------------------------------------------- 12
    print('\n12. PESO BRUTO: A UNICA TRAVA NUMERICA')
    pg2.click('#btnDespachar'); pg2.wait_for_timeout(400)
    ok('peso bruto' in texto_modal(pg2), 'despachar sem pesar e recusado: %s' % texto_modal(pg2)[:80])
    pg2.click('#btnConfirmModalConfirmar'); pg2.wait_for_timeout(300)
    ok(pg2.evaluate("() => ROM.situacao") != 'despachado', 'e nada foi despachado')

    # A referencia e o que foi BIPADO (132 kg), nao o romaneio inteiro (218 kg):
    # comparar com o total acusaria desvio justo quando um pedido fica para tras.
    pg2.fill('#inputPesoBruto', '136,5'); pg2.wait_for_timeout(250)
    dica = pg2.locator('#dicaPeso').inner_text()
    ok('bipados' in dica, 'a dica compara com a soma dos volumes BIPADOS: %s' % dica)
    ok('dentro do esperado' in dica, 'e 136,5 kg contra os volumes bipados fica dentro do parametro')
    pg2.fill('#inputPesoBruto', '240'); pg2.wait_for_timeout(250)
    ok('fora' in pg2.locator('#dicaPeso').inner_text(), 'desvio grande avisa: %s' % pg2.locator('#dicaPeso').inner_text()[:80])
    ok(pg2.evaluate("() => typeof PARAM.expedicaoDesvioPesoPct === 'number'"),
       'o limite do desvio vive no PARAM, nao dentro de um `if`')
    pg2.fill('#inputPesoBruto', '160'); pg2.wait_for_timeout(250)

    # ---------------------------------------------------------------- 13
    print('\n13. DESPACHAR: O QUE SAI, O QUE VOLTA, E A BAIXA DO ESTOQUE')
    pg2.fill('#inputMotorista', 'Alencar Dias')
    pg2.fill('#inputPlaca', 'qrb7c41')
    pg2.click('#btnDespachar'); pg2.wait_for_timeout(450)
    texto = texto_modal(pg2)
    ok('#26' in texto and '#25' in texto, 'a confirmacao nomeia o que sai e o que volta: %s' % texto[:150])
    ok('estoque físico' in texto, 'e diz que o estoque fisico e baixado agora')
    ok('nada é estornado' in texto.lower(), 'e que o que volta nao precisa de estorno')
    confirmar(pg2)
    ok(pg2.locator('#confirmModal').evaluate("el => el.classList.contains('open')"),
       'o aviso do despacho aparece — a folha fecha antes de executar')
    pg2.click('#btnConfirmModalConfirmar'); pg2.wait_for_timeout(350)
    ok(pg2.evaluate("() => ROM.situacao") == 'despachado', 'o romaneio ficou despachado')
    ok(pg2.evaluate("() => ROM.pedidos.length") == 1, 'so o pedido completo continua na carga')
    ok(pg2.evaluate("() => ROM.placa") == 'QRB7C41', 'a placa fica em maiusculas, do jeito que vai no papel')
    ok(not pg2.is_visible('#btnDespachar'), 'despachado, o botao de despachar some')
    ok(pg2.locator('#campoBipar').is_disabled(), 'e a bipagem fecha')

    # ---------------------------------------------------------------- 14
    print('\n14. REABRIR PEDE SENHA E DIZ O QUE ISSO SIGNIFICA')
    pg2.click('#menuMaisAcoes .dropdown-select-btn'); pg2.wait_for_timeout(250)
    pg2.click('#menuMaisAcoes .dropdown-select-item[data-acao="reabrir"]'); pg2.wait_for_timeout(400)
    texto = texto_modal(pg2)
    ok('devolve ao estoque' in texto, 'a confirmacao explica o efeito real: %s' % texto[:110])
    ok(pg2.locator('#campoSenhaModal').evaluate("el => el.classList.contains('on')"), 'e pede senha')
    pg2.click('#btnConfirmModalConfirmar'); pg2.wait_for_timeout(300)
    ok(pg2.locator('#campoSenhaModal').evaluate("el => el.classList.contains('has-error')"),
       'confirmar sem senha nao reabre')
    pg2.fill('#inputSenhaModal', 'senha')
    confirmar(pg2)
    pg2.click('#btnConfirmModalConfirmar'); pg2.wait_for_timeout(300)
    ok(pg2.evaluate("() => ROM.situacao") == 'conferindo', 'com senha, reabre')

    # ---------------------------------------------------------------- 15
    print('\n15. MDF-e: SO EM CARGA PROPRIA, E POR PARAMETRO POR UF')
    pg3 = nova(pw, ROM + '?id=ROM-0193', erros)
    ok(pg3.is_visible('#blocoMdfe'), 'frota propria mostra o aviso de MDF-e')
    ok(pg3.is_visible('#marcaMdfe'), 'e a marca aparece no cabecalho')
    txt = pg3.locator('#textoMdfe').inner_text()
    ok('RS' in txt and 'intermunicipal' in txt, 'com a regra do RS, que e a mais exigente: %s' % txt[:110])
    ok('módulo fiscal' in txt, 'e lembrando que quem emite e o modulo fiscal, nao esta tela')
    ok(pg3.evaluate("() => regraMdfe('RS') !== regraMdfe('SP')"), 'o mapa por UF distingue de verdade')
    ok(pg3.evaluate("() => regraMdfe('AC') === PARAM.mdfeRegraPadrao"), 'UF fora do mapa herda o padrao')
    # Mas MDF-e NAO trava: com peso e volumes bipados, a carga sai.
    for i in range(1, 4):
        bipar(pg3, 'VOL-0028-%d' % i)
    pg3.fill('#inputPesoBruto', '56')
    pg3.wait_for_timeout(250)
    pg3.click('#btnDespachar'); pg3.wait_for_timeout(450)
    ok('MDF-e' in texto_modal(pg3), 'a confirmacao lembra do MDF-e em carga propria')
    confirmar(pg3)
    pg3.click('#btnConfirmModalConfirmar'); pg3.wait_for_timeout(300)
    ok(pg3.evaluate("() => ROM.situacao") == 'despachado', 'e o MDF-e NAO impede o despacho — e aviso, nao trava')

    pg4 = nova(pw, ROM + '?id=ROM-0190', erros)
    ok(not pg4.is_visible('#blocoMdfe'), 'Correios nao fala de MDF-e: o documento e do prestador')

    # ---------------------------------------------------------------- 16
    print('\n16. O ROMANEIO IMPRESSO: DUAS VIAS, COM ASSINATURA')
    pg5 = nova(pw, ROM, erros)
    for i in range(1, 7):
        bipar(pg5, 'VOL-0026-%d' % i)
    pg5.fill('#inputPesoBruto', '136,5')
    pg5.evaluate("() => montarFolha()")
    folha = pg5.locator('#romFolha').inner_html()
    ok(folha.count('rom-via"') == 2, 'a folha sai em DUAS vias')
    ok('VIA DO GALPÃO' in folha.upper() and 'VIA DO TRANSPORTADOR' in folha.upper(),
       'uma do galpao e uma do transportador')
    ok(folha.count('rom-assina') == 2, 'cada via tem o bloco de assinatura')
    ok('sem validade fiscal' in folha, 'e o rodape diz que o romaneio NAO e documento fiscal')
    ok('NÃO EMBARCA' in folha, 'o rascunho marca o pedido que ainda nao embarca')
    ok('6 de 6' in folha and '0 de 4' in folha, 'e mostra quantos volumes de cada pedido ja foram bipados')

    # ---------------------------------------------------------------- 17
    print('\n17. TIRAR UM PEDIDO DO ROMANEIO')
    pg5.click('[data-tirar="1"]'); pg5.wait_for_timeout(400)
    ok('Nada é estornado' in texto_modal(pg5), 'tirar explica que nada e estornado')
    confirmar(pg5)
    pg5.click('#btnConfirmModalConfirmar'); pg5.wait_for_timeout(300)
    ok(pg5.evaluate("() => ROM.pedidos.length") == 1, 'o pedido saiu da carga')
    ok(pg5.locator('#totVolumes').inner_text() == '6 de 6', 'e os volumes dele sairam da conta junto')

    # ---------------------------------------------------------------- 18
    print('\n18. LINK PARA ROMANEIO QUE NAO EXISTE NAO ABRE TELA EM BRANCO')
    pg6 = nova(pw, ROM + '?id=ROM-9999', erros)
    ok(pg6.locator('#confirmModal').evaluate("el => el.classList.contains('open')"),
       'a tela avisa em vez de fingir')
    ok('não existe' in texto_modal(pg6), 'e diz o que aconteceu: %s' % texto_modal(pg6)[:90])
    pg6.click('#btnConfirmModalConfirmar'); pg6.wait_for_timeout(250)
    ok(pg6.locator('#tituloRom').inner_text() == 'Romaneio ROM-0192', 'abrindo no romaneio padrao')

    # ---------------------------------------------------------------- 19
    print('\n19. O CATALOGO E UMA LISTA SO, E O MENU LEVA AS TELAS')
    CHAVES = ['expedicaoMonta', 'expedicaoTiraPedido', 'expedicaoCancela', 'expedicaoDespacha', 'expedicaoReabre']
    for tela in ['pagina-configuracoes-confirmacoes-senha.html',
                 'pagina-cadastros-vendedores-detalhe.html',
                 'pagina-configuracoes-registro-atividades.html']:
        pgc = nova(pw, tela, erros)
        achadas = pgc.evaluate("() => ACOES_SENHA.map(a => a.chave)")
        faltando = [k for k in CHAVES if k not in achadas]
        ok(not faltando, '%s conhece as acoes da Expedicao%s'
           % (tela.replace('pagina-', ''), '' if not faltando else ' — falta ' + ', '.join(faltando)))

    sem, morto = [], []
    for arq in sorted(glob.glob('pagina-*.html')):
        txt = open(arq, encoding='utf-8').read()
        if 'data-label="Expedição"' not in txt: sem.append(arq)
        elif 'data-href="pagina-logistica-expedicao.html"' not in txt: morto.append(arq)
    ok(not sem, 'toda tela tem o item Expedição no menu%s' % ('' if not sem else ': falta em ' + ', '.join(sem)))
    ok(not morto, 'e nenhum deles e item morto%s' % ('' if not morto else ': ' + ', '.join(morto)))

    print('\nERROS DE CONSOLE: ' + (str(erros) if erros else 'nenhum'))
    if erros: falhas.append('erro de console: %s' % erros)

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
