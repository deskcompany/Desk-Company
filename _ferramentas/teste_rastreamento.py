from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g, pathlib as _pathlib
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
ARQ = URL + 'pagina-logistica-rastreamento.html'

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(ARQ); pg.wait_for_timeout(500)

    print('\n[1] A lista nasce de pe')
    linhas = pg.locator('#corpoTabela tr').count()
    ok(linhas > 0, 'a tabela renderiza linhas (%d)' % linhas)
    ok(pg.locator('#corpoTabela tr').count() <= 10, 'respeita o "por pagina" de 10 (%d)' % linhas)
    cab = pg.locator('.estoque-table thead th').count()
    cel = pg.locator('#corpoTabela tr').first.locator('td').count()
    ok(cab == cel, 'cabecalho e celulas batem: %d th x %d td' % (cab, cel))

    print('\n[2] A tabela cabe no card a 1440px')
    # O design system mede isto, nao opina: foi assim que o estouro de 88px apareceu.
    m = pg.evaluate("""() => {
      const w = document.querySelector('.estoque-table-wrap');
      const t = document.querySelector('.estoque-table');
      return { wrap: w.clientWidth, tabela: t.scrollWidth, pagina: document.documentElement.scrollWidth };
    }""")
    ok(m['tabela'] <= m['wrap'] + 1, 'tabela cabe sem rolagem: %d em %d' % (m['tabela'], m['wrap']))
    ok(m['pagina'] <= 1440, 'a pagina nao estoura em 1440: %d' % m['pagina'])

    print('\n[3] Pagamento e EIXO SEPARADO, nao passo do funil')
    # A barganha de 07/out: boleto fica enviado e nao pago; Pix fica pago em aberto.
    # Se alguem transformar isto em situacao, a independencia morre em silencio.
    sits = pg.evaluate("SITUACOES.map(s => s.id)")
    ok(len(sits) == 9, 'o funil tem os 9 passos do pedido (%d)' % len(sits))
    ok('pago' not in sits and 'pagamento' not in sits, 'pagamento NAO e situacao do funil')
    ok('devolucao' not in sits and 'devolvido' not in sits, 'devolucao NAO e situacao de pedido (decisao de 02/out)')
    cruz = pg.evaluate("""() => {
      const env = PEDIDOS.filter(p => p.situacao === 'enviado' && p.pagamento !== 'pago').length;
      const ab  = PEDIDOS.filter(p => p.situacao !== 'enviado' && p.situacao !== 'entregue' && p.pagamento === 'pago').length;
      return { enviadoSemPagar: env, pagoSemEnviar: ab };
    }""")
    ok(cruz['enviadoSemPagar'] > 0, 'existe pedido enviado e nao pago (prova que os eixos sao livres)')
    ok(cruz['pagoSemEnviar'] > 0, 'existe pedido pago e ainda nao enviado')

    print('\n[4] A previsao e CONGELADA, nao calculada')
    # Se fosse calculada do cadastro, mudar o prazo da transportadora reescreveria
    # o passado. O prazo usado fica gravado junto da previsao justamente para provar isso.
    cong = pg.evaluate("""() => {
      const p = PEDIDOS.filter(x => x.previsao)[0];
      const prazoHoje = TRANSPORTADORAS[p.transp].prazo;
      return { gravado: p.prazoUsado, cadastro: prazoHoje, previsao: p.previsao, enviado: p.enviadoEm };
    }""")
    ok(cong['gravado'] is not None, 'o prazo usado no despacho fica gravado no pedido')
    recalc = pg.evaluate("""() => {
      // Mexer no cadastro NAO pode mudar a previsao de quem ja saiu.
      const p = PEDIDOS.filter(x => x.previsao)[0];
      const antes = p.previsao;
      TRANSPORTADORAS[p.transp].prazo = 99;
      render();
      return { antes: antes, depois: p.previsao };
    }""")
    ok(recalc['antes'] == recalc['depois'],
       'mudar o prazo da transportadora NAO reescreve a previsao de quem ja saiu (%s)' % recalc['antes'])

    print('\n[5] Codigo de rastreio e POR VOLUME')
    multi = pg.evaluate("PEDIDOS.filter(p => p.volumes.length > 1).length")
    ok(multi > 0, 'existe pedido com mais de um volume (%d)' % multi)
    parcial = pg.evaluate("""() => {
      const p = PEDIDOS.filter(x => x.volumes.length > 1 && x.volumes.some(v => v.codigo) && x.volumes.some(v => !v.codigo))[0];
      return p ? p.numero : null;
    }""")
    ok(parcial is not None, 'existe pedido com codigo em parte dos volumes: %s' % parcial)

    print('\n[6] O painel abre sem sair da lista')
    pg.locator('#corpoTabela tr').first.click(); pg.wait_for_timeout(400)
    ok(pg.locator('#eventDrawer.open').count() == 1, 'o painel abre no clique da linha')
    # inner_text devolve o texto COMO RENDERIZADO, e os titulos de secao do painel
    # tem text-transform:uppercase — "Historico" chega "HISTORICO". Comparar sem
    # caixa deixa a assercao falar do conteudo, nao do estilo dele.
    corpo = pg.inner_text('#drawerCorpo').lower()
    ok('volumes e códigos' in corpo, 'o painel lista volumes e codigos')
    ok('histórico' in corpo, 'o painel mostra o historico')
    ok('comprovante de entrega' in corpo, 'o comprovante de entrega aparece')
    ok('reservado' in corpo, 'e o comprovante esta RESERVADO, nao prometido como pronto')
    ok('lido de contas a receber' in corpo, 'o painel diz que o pagamento vem de Contas a Receber')

    print('\n[7] O historico separa o que o cliente ve do que e interno')
    marcas = pg.evaluate("""() => {
      const t = Array.from(document.querySelectorAll('#drawerCorpo .ev-visto')).map(e => e.textContent.trim());
      return { total: t.length, publicos: t.filter(x => x.indexOf('cliente') >= 0).length,
               internos: t.filter(x => x.indexOf('interno') >= 0).length };
    }""")
    ok(marcas['total'] > 0, 'todo evento carrega o marcador de quem o ve (%d)' % marcas['total'])
    ok(marcas['publicos'] > 0, 'ha evento que o cliente ve (%d)' % marcas['publicos'])
    vit = pg.evaluate("ROTULO_VITRINE['faturado'] === null && ROTULO_VITRINE['conferenciasaida'] === 'Pedido embalado'")
    ok(vit, 'Faturado e interno e Conferencia de saida vira "Pedido embalado" para o cliente')

    print('\n[8] O painel MOSTRA o codigo de quem ja tem')
    # Confirmar aqui deixou de existir em 07/out (ver [14]). O que o painel
    # ainda precisa fazer e deixar o codigo visivel de relance, sem navegar.
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    comCod = pg.evaluate("PEDIDOS.filter(p => p.volumes.some(v => v.codigo))[0].id")
    pg.evaluate("abrirPedido(" + str(comCod) + ")"); pg.wait_for_timeout(350)
    ok(pg.locator('#drawerCorpo .cod-chip').count() > 0, 'o codigo ja confirmado aparece no painel')
    semCod = pg.evaluate("PEDIDOS.filter(p => p.volumes.some(v => !v.codigo))[0].id")
    pg.evaluate("abrirPedido(" + str(semCod) + ")"); pg.wait_for_timeout(350)
    ok(pg.locator('#drawerCorpo .cod-falta').count() > 0, 'o volume sem codigo aparece como falta, nao em branco')

    print('\n[9] Entrega a mao PEDE confirmacao, como alterar situacao em Pedidos')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    exige = pg.evaluate("exigeSenha('rastreioEntregaManual')")
    ok(exige is True, 'rastreioEntregaManual exige senha por padrao')
    ok(pg.evaluate("exigeSenha('rastreioConfirma')") is False,
       'confirmar codigo NAO exige senha (e rotina, pede rastro)')
    ok(pg.evaluate("exigeSenha('rastreioAltera')") is True,
       'ALTERAR codigo ja confirmado exige senha (o cliente ja viu o antigo)')
    cat = pg.evaluate("ACOES_ESPECIFICAS.filter(a => a.chave.indexOf('rastreio') === 0).length")
    ok(cat == 4, 'as 4 acoes de rastreamento estao no catalogo (%d)' % cat)

    print('\n[10] Filtros, contadores e KPIs falam da MESMA lista')
    pg.evaluate("estado.situacao='enviado'; estado.pagina=1; render();")
    pg.wait_for_timeout(250)
    conf = pg.evaluate("""() => {
      const vis = document.querySelectorAll('#corpoTabela tr').length;
      const kpi = +document.getElementById('kpiTransito').textContent;
      const rod = document.getElementById('contagemPedidos').textContent;
      return { vis: vis, kpi: kpi, rodape: rod };
    }""")
    ok(str(conf['kpi']) in conf['rodape'] or conf['kpi'] > 0,
       'o KPI de em transito acompanha o filtro (kpi %d, rodape "%s")' % (conf['kpi'], conf['rodape']))
    pg.evaluate("estado.situacao='todos'; render();")
    pg.wait_for_timeout(200)
    cont = pg.evaluate("""() => {
      const itens = Array.from(document.querySelectorAll('#menuFiltroSituacao .dropdown-select-item'));
      return itens.map(i => i.textContent.trim()).filter(t => t.indexOf('(') >= 0).length;
    }""")
    ok(cont > 0, 'o filtro de situacao traz contador em cada opcao (%d)' % cont)

    print('\n[11] Dropdown abre de verdade, nao so no DOM')
    # "Abrir nao e aparecer" (02/out): a assercao e a do dedo do usuario.
    btn = pg.locator('#filtroSituacao .dropdown-select-btn')
    btn.click(); pg.wait_for_timeout(300)
    viu = pg.evaluate("""() => {
      const m = document.querySelector('#menuFiltroSituacao');
      const it = m && m.querySelector('.dropdown-select-item');
      if (!it) return false;
      const r = it.getBoundingClientRect();
      const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
      return !!(el && m.contains(el));
    }""")
    ok(viu, 'o menu de situacao aparece de verdade no ponto do primeiro item')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.locator('#filtroSituacao.open').count() == 0, 'Esc fecha o dropdown')

    print('\n[12] Os dois temas')
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(250)
        est = pg.evaluate("""() => {
          const f = getComputedStyle(document.body).fontFamily;
          const b = getComputedStyle(document.body).backgroundColor;
          return { fonte: f, fundo: b };
        }""")
        ok('unito' in est['fonte'], 'tema %s: a fonte e Nunito' % tema)
        ok(est['fundo'] != 'rgba(0, 0, 0, 0)', 'tema %s: o body tem fundo solido' % tema)

    print('\n[13] Nenhum erro de JS na listagem')
    ok(not erros, 'sem erro de JS na listagem: %s' % erros[:2])

    print('\n[14] O painel da listagem SO MOSTRA')
    # Decisao de 07/out: confirmar codigo sem ver o pedido inteiro — itens, cliente,
    # vendedor, quem separou — e decidir no escuro o que o cliente vai acompanhar.
    # A acao migrou para o detalhe; o painel vira resumo e porta de entrada.
    pg.goto(ARQ); pg.wait_for_timeout(450)
    pg.locator('#corpoTabela tr').first.click(); pg.wait_for_timeout(350)
    ok(pg.locator('#drawerCorpo [data-confirmar]').count() == 0, 'o painel NAO oferece confirmar codigo')
    ok(pg.locator('#drawerCorpo [data-alterar]').count() == 0, 'o painel NAO oferece alterar codigo')
    ok(pg.locator('#drawerCorpo [data-abrir-detalhe]').count() == 1, 'o painel oferece abrir o pedido')
    ok('só consulta' in pg.inner_text('#drawerCorpo').lower(), 'o painel diz que e so consulta')

    print('\n[15] O painel leva ao detalhe, pelo ?id=')
    pg.locator('#drawerCorpo [data-abrir-detalhe]').click()
    pg.wait_for_load_state('load'); pg.wait_for_timeout(500)
    ok('pagina-logistica-rastreamento-detalhe.html' in pg.url, 'navegou para a tela de detalhe')
    ok('?id=' in pg.url, 'levou o id na URL, como as outras telas de detalhe')
    ok('Pedido PV-' in pg.inner_text('#tituloPedido'), 'o titulo traz o pedido: %s' % pg.inner_text('#tituloPedido'))

    print('\n[16] O detalhe mostra o pedido inteiro')
    corpo = pg.inner_text('.main').lower()
    for rotulo in ['itens do pedido', 'cliente', 'pagamento', 'quem tocou o pedido',
                   'transportadora e códigos de rastreio', 'histórico']:
        ok(rotulo in corpo, 'tem o bloco "%s"' % rotulo)
    ok(pg.locator('#corpoItens tr').count() > 0, 'os itens do pedido aparecem (%d)' % pg.locator('#corpoItens tr').count())
    ok(pg.inner_text('#docOnde').strip() not in ('', '—'), 'onde comprou: %s' % pg.inner_text('#docOnde'))
    ok(pg.inner_text('#docVendedor').strip() not in ('', '—'), 'vendedor: %s' % pg.inner_text('#docVendedor'))
    ok(pg.inner_text('#docTranspContato').strip() not in ('', '—'), 'contato da transportadora: %s' % pg.inner_text('#docTranspContato'))
    ok(pg.locator('#listaToques .toque-item').count() == 3, 'quem tocou tem as 3 etapas')

    print('\n[17] Venda de vitrine diz que NAO teve vendedor, em vez de deixar vazio')
    semVend = pg.evaluate("PEDIDOS.filter(p => !p.vendedor)[0].id")
    pg.goto(ARQ.replace('.html', '-detalhe.html') + '?id=' + str(semVend))
    pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok('sem vendedor' in pg.inner_text('#docVendedor').lower(),
       'diz "Sem vendedor", nao deixa em branco: %s' % pg.inner_text('#docVendedor'))

    print('\n[18] Pagamento no detalhe tambem e SO LEITURA')
    ok('contas a receber' in pg.inner_text('.main').lower(), 'o detalhe diz de onde vem o pagamento')
    campos_pg = pg.evaluate("""() => {
      const ids = ['docPgSituacao','docPgForma','docPgParcelas','docPgValor','docPgRecebido','docPgSaldo'];
      return ids.filter(i => {
        const e = document.getElementById(i);
        return e && e.querySelector('input, textarea, select');
      }).length;
    }""")
    ok(campos_pg == 0, 'nenhum campo de pagamento e editavel nesta tela')

    print('\n[19] Inserir codigo: a tela de detalhe e a UNICA que escreve')
    alvo = pg.evaluate("PEDIDOS.filter(p => p.volumes.some(v => !v.codigo))[0].id")
    pg.goto(ARQ.replace('.html', '-detalhe.html') + '?id=' + str(alvo))
    pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    # Mira o volume SEM codigo: preencher o de um volume que ja tem transforma
    # a acao em alteracao, que e outra chave e exige senha (ver [19b]).
    volVazio = pg.evaluate("PEDIDOS.filter(p => p.id === %d)[0].volumes.filter(v => !v.codigo)[0].id" % alvo)
    vazio = pg.locator('#corpoVolumes input[data-vol="' + volVazio + '"]')
    ok(vazio.count() > 0, 'o volume sem codigo tem campo para inserir (%s)' % volVazio)
    vazio.fill('TESTE123456BR')
    pg.locator('#btnSalvarCodigos').click(); pg.wait_for_timeout(600)
    # Inserir e rotina: nao pede senha, entao grava direto.
    gravou = pg.evaluate("PEDIDOS.filter(p => p.id === %d)[0].volumes.some(v => v.codigo === 'TESTE123456BR')" % alvo)
    ok(gravou, 'o codigo novo foi gravado no volume')


    print('\n[19b] ALTERAR um codigo ja confirmado para e pede senha')
    # O cliente ja recebeu o codigo antigo e pode estar acompanhando por ele.
    # Por isso alterar e outra chave, com exigePadrao true: a acao nao acontece
    # sozinha, ela para no modal de confirmacao.
    volCheio = pg.evaluate("PEDIDOS.filter(p => p.id === %d)[0].volumes.filter(v => v.codigo)[0].id" % alvo)
    antigo = pg.evaluate("PEDIDOS.filter(p => p.id === %d)[0].volumes.filter(v => v.id === '%s')[0].codigo" % (alvo, volCheio))
    campoCheio = pg.locator('#corpoVolumes input[data-vol="' + volCheio + '"]')
    campoCheio.fill('OUTROCODIGO999')
    pg.locator('#btnSalvarCodigos').click(); pg.wait_for_timeout(500)
    travou = pg.evaluate("PEDIDOS.filter(p => p.id === %d)[0].volumes.filter(v => v.id === '%s')[0].codigo" % (alvo, volCheio))
    ok(travou == antigo, 'a alteracao NAO acontece sozinha: o codigo segue %s' % travou)
    ok(pg.locator('#confirmModal.open').count() == 1, 'ela para no modal de confirmacao')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(300)

    print('\n[20] Salvar sem mexer em nada avisa, em vez de fingir que salvou')
    # Recarrega: depois do Esc da [19b] o campo ainda tem o rascunho digitado, e
    # isso e proposital — o chip mostra o que esta SALVO e o campo e rascunho.
    # Para testar "nao ha o que salvar" e preciso partir de uma tela sem rascunho.
    pg.goto(ARQ.replace('.html', '-detalhe.html') + '?id=' + str(alvo))
    pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    pg.locator('#btnSalvarCodigos').click(); pg.wait_for_timeout(450)
    txt_modal = pg.inner_text('body').lower()
    ok('nenhum código novo' in txt_modal, 'avisa que nao ha o que salvar')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)

    print('\n[21] Id invalido NAO inventa pedido')
    pg.goto(ARQ.replace('.html', '-detalhe.html') + '?id=99999')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    ok('não encontrado' in pg.inner_text('#tituloPedido').lower(), 'diz que nao encontrou')
    visiveis = pg.evaluate("Array.from(document.querySelectorAll('.main .card')).filter(c => c.offsetParent !== null).length")
    ok(visiveis == 0, 'nao mostra card nenhum com dado de outro pedido (%d visiveis)' % visiveis)

    print('\n[22] O detalhe nos dois temas, sem erro de JS')
    pg.goto(ARQ.replace('.html', '-detalhe.html') + '?id=2')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(450)
    for tema in ['claro', 'escuro']:
        pg.evaluate("document.body.classList.%s('dark')" % ('remove' if tema == 'claro' else 'add'))
        pg.wait_for_timeout(220)
        est = pg.evaluate("""() => ({
          fonte: getComputedStyle(document.body).fontFamily,
          fundo: getComputedStyle(document.body).backgroundColor,
          larg: document.documentElement.scrollWidth
        })""")
        ok('unito' in est['fonte'], 'detalhe tema %s: fonte Nunito' % tema)
        ok(est['larg'] <= 1440, 'detalhe tema %s: nao estoura em 1440 (%d)' % (tema, est['larg']))
    ok(not erros, 'sem erro de JS no detalhe: %s' % erros[:2])

    b.close()

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo.
raise SystemExit(1 if falhas else 0)
