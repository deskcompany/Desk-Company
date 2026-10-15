# -*- coding: utf-8 -*-
# Vendas Afiliados, entrega 1 (barganha de 14/out/2026).
#
# A venda por link de indicacao e um Pedido de Venda, com o mesmo funil: nao ganhou lista propria. O
# pedido chega da vitrine dizendo quem indicou (`ind`), e isso nao se digita. Uma pessoa recebe por
# pedido, e o link vale sobre o vendedor. O item "Vendas Afiliados" do menu abre Pedidos de Venda
# filtrado nas vendas afiliadas (link ou vendedor). A aba Comissoes do pedido passou a seguir a regra de
# quem recebe: o cadastro do vendedor, ou o programa de afiliados (o percentual vem no pedido).
#
#   [1] Lista: o filtro de origem, a marca "indicacao de" na linha e no painel, limpar filtros;
#   [2] Menu: Vendas Afiliados abre a lista ja filtrada, igual em toda tela;
#   [3] Pagina do pedido: o campo Indicacao, quem recebe a comissao, a regra dita, faturar e o clone;
#   [4] Espelhos: a indicacao igual nas duas telas, a regra igual ao cadastro de vendedores, e quem
#       indica e cliente cadastrado e nunca o proprio comprador.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LISTA, DET = 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html'
HREF = '../vendas/pagina-vendas-pedidos.html?origem=afiliadas'

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


ESCOLHE = "([dd, v]) => document.querySelector('#' + dd + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()"
NUMEROS = "pedidosFiltrados().map(p => p.numero)"

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def limpa_lista():
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(200)

    def origem(v):
        pg.evaluate(ESCOLHE, ['filtroOrigem', v]); pg.wait_for_timeout(200)
        return sorted(pg.evaluate(NUMEROS))

    def aba_comissao():
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"comissoes\"]').click()"); pg.wait_for_timeout(200)
        return pg.inner_text('#resumoComissao'), pg.inner_text('#hintComissao')

    ir(LISTA)
    PEDIDOS = pg.evaluate("PEDIDOS.filter(p => !p.pdv)")
    COM_IND = sorted(x['numero'] for x in PEDIDOS if x.get('ind'))
    AFILIADAS = sorted(x['numero'] for x in PEDIDOS if x.get('ind') or x['vendedor'])
    SEM = sorted(x['numero'] for x in PEDIDOS if not x.get('ind') and not x['vendedor'])

    if secao(1, 'Lista: o filtro de origem e a marca da indicação'):
        ok(pg.evaluate("Array.from(document.querySelectorAll('#filtroOrigem .dropdown-select-item')).map(i => i.getAttribute('data-value'))") == ['todos', 'afiliadas', 'link', 'sem'],
           'o filtro de origem tem: todas, afiliadas (link ou vendedor), só link e sem afiliado')
        limpa_lista()
        ok(COM_IND == [3, 4, 8, 12], 'o exemplo tem quatro vendas por link: %s' % COM_IND)
        ok(origem('link') == COM_IND, 'só link de indicação mostra os quatro')
        ok(origem('afiliadas') == AFILIADAS and len(AFILIADAS) > len(COM_IND), 'afiliadas mostra link ou vendedor: %d pedidos' % len(AFILIADAS))
        ok(origem('sem') == SEM and sorted(SEM + AFILIADAS) == sorted(x['numero'] for x in PEDIDOS), 'sem afiliado mostra o resto, e as duas somam a lista inteira')
        origem('todos')
        linha = lambda n: pg.evaluate("(n) => { const p = PEDIDOS.filter(x => x.numero === n)[0]; const tr = document.querySelector('#corpoTabela tr[data-id=\"' + p.id + '\"]'); return tr ? tr.innerText : null; }", n)
        ok('indicação de Bruno Carvalho' in (linha(4) or '') and 'indicação de Larissa Monteiro' in (linha(8) or ''), 'a linha diz de quem foi a indicação')
        ok('indicação de' not in (linha(5) or 'indicação de'), 'e o pedido sem link não tem a marca')
        pg.evaluate("abrirPreview(4)"); pg.wait_for_timeout(300)
        ok('Bruno Carvalho · cliente afiliado, 4% de comissão' in pg.inner_text('#drawerCorpo'), 'o painel do pedido mostra a indicação, com o percentual')
        pg.evaluate("abrirPreview(3)"); pg.wait_for_timeout(300)
        ok('Marina Costa · link do vendedor' in pg.inner_text('#drawerCorpo'), 'e o link do vendedor')
        pg.evaluate("fecharDrawer()"); pg.wait_for_timeout(150)
        origem('link'); limpa_lista()
        ok(pg.get_attribute('#filtroOrigem', 'data-value') == 'todos' and pg.inner_text('#filtroOrigem .dropdown-select-label') == 'Todas as origens'
           and len(pg.evaluate(NUMEROS)) == len(PEDIDOS), 'limpar filtros devolve a origem para todas')
        # 14/out: o usuario viu a barra quebrar de linha ao escolher "Afiliadas: link ou vendedor", mais
        # largo que "Todas as origens". Em toda largura, escolher uma origem nao pode somar linha a barra.
        # Na largura dele a barra tinha 1024 a 1064px; a varredura de 20 em 20 passa por essa faixa.
        LINHAS = "new Set(Array.from(document.querySelectorAll('.estoque-toolbar > *')).filter(e => e.getClientRects().length).map(e => Math.round(e.getBoundingClientRect().top))).size"
        quebra = []
        for largura in range(1100, 1720, 20):
            pg.set_viewport_size({'width': largura, 'height': 900}); pg.wait_for_timeout(60)
            origem('todos'); padrao = pg.evaluate(LINHAS)
            for v in ('afiliadas', 'link', 'sem'):
                origem(v)
                if pg.evaluate(LINHAS) > padrao: quebra.append('%s em %dpx' % (v, largura))
        pg.set_viewport_size({'width': 1440, 'height': 900}); origem('todos')
        ok(not quebra, 'escolher uma origem não quebra a barra de filtros em mais linhas: %s' % quebra)

    if secao(2, 'Menu: Vendas Afiliados abre a lista filtrada'):
        ir('pagina-cadastros-marcas.html')
        pg.click('.nav-item[data-id="vendas"]'); pg.wait_for_timeout(450)
        pg.click('#flyout-vendas .flyout-item[data-label="Vendas Afiliados"]'); pg.wait_for_timeout(900)
        ok(pg.url.endswith('pagina-vendas-pedidos.html?origem=afiliadas'), 'o item navega para Pedidos de Venda: %s' % pg.url.split('/')[-1])
        ok(pg.get_attribute('#filtroOrigem', 'data-value') == 'afiliadas' and pg.inner_text('#filtroOrigem .dropdown-select-label') == 'Vendas afiliadas',
           'e a lista abre com o filtro de afiliadas escolhido')
        ok(sorted(pg.evaluate(NUMEROS)) == [n for n in AFILIADAS if n in sorted(pg.evaluate("PEDIDOS.filter(p => passaPeriodo(p)).map(p => p.numero)"))],
           'mostrando só as vendas afiliadas do período')
        ok('Vendas afiliadas' in pg.inner_text('#breadcrumb'), 'o caminho no topo diz que a lista está filtrada')
        ir(LISTA, '?origem=qualquer')
        ok(pg.get_attribute('#filtroOrigem', 'data-value') == 'todos', 'origem desconhecida no endereço abre a lista sem filtro')
        com, sem_item = [], []
        for arq in sorted(localiza.caminhos()):
            t = open(arq, encoding='utf-8').read()
            if 'data-label="Vendas Afiliados"' not in t: continue
            (com if t.count('data-label="Vendas Afiliados" data-href="' + HREF + '"') == t.count('data-label="Vendas Afiliados"') else sem_item).append(_os.path.basename(arq))
        ok(not sem_item and len(com) == len(localiza.caminhos()), 'o item tem o mesmo destino nas %d telas: %s' % (len(com), sem_item[:3]))

    if secao(3, 'Página do pedido: a indicação e quem recebe a comissão'):
        ir(DET, '?id=4')
        ok(pg.input_value('#inputIndicacao') == 'Bruno Carvalho · cliente afiliado, 4% de comissão', 'o pedido por link diz quem indicou: %s' % pg.input_value('#inputIndicacao'))
        ok(pg.evaluate("document.getElementById('inputIndicacao').readOnly"), 'e o campo não se digita')
        resumo, dica = aba_comissao()
        ok('Bruno Carvalho' in resumo and 'Cliente afiliado, pelo link' in resumo and '4,00%' in resumo, 'a comissão é de quem indicou, no percentual do pedido')
        ok('R$ 24,48' in resumo, 'e é 4%% da base (612,00): %s' % resumo.replace('\n', ' '))
        ok('7 dias sem devolução' in dica, 'a regra dita é a do programa: entregue e 7 dias sem devolução')
        ok('não libera aqui' in pg.evaluate("efeitoNaComissao(false)"), 'faturar diz que a comissão do afiliado não libera ali')
        pg.evaluate("document.getElementById('btnEditarRegistro').click()"); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['inputVendedor', 'Rafael Andrade']); pg.wait_for_timeout(200)
        ok('Bruno Carvalho' in pg.inner_text('#resumoComissao'), 'marcar um vendedor no pedido por link não tira a comissão de quem indicou')

        ir(DET, '?id=12')
        ok('R$ 40,96' in aba_comissao()[0], 'outro pedido do mesmo afiliado: 4% de 1.024,00')

        ir(DET, '?id=3')
        ok(pg.input_value('#inputIndicacao') == 'Marina Costa · link do vendedor', 'o link do vendedor aparece como tal')
        ok('Vendedor, pelo link' in aba_comissao()[0], 'e a comissão é dela, como vendedora, pelo link')
        pg.evaluate("document.getElementById('btnEditarRegistro').click()"); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['inputVendedor', 'Rafael Andrade']); pg.wait_for_timeout(200)
        ok('Marina Costa' in pg.inner_text('#resumoComissao') and '5,00%' in pg.inner_text('#resumoComissao'),
           'trocar o vendedor do pedido não tira a comissão de quem mandou o link')

        ir(DET, '?id=1')
        ok(pg.input_value('#inputIndicacao') == 'Sem indicação', 'pedido de vendedor sem link: sem indicação')
        resumo, dica = aba_comissao()
        ok('Marina Costa' in resumo and '5,00%' in resumo and 'R$ 94,00' in resumo, 'a comissão segue o cadastro dela: 5% de 1.880,00')
        ok('parcelas pagas' in dica and 'faturamento' not in dica, 'a regra dita é a do cadastro dela (parcial, pelas parcelas pagas), e não mais "no faturamento"')

        ir(DET, '?id=2')
        resumo, dica = aba_comissao()
        ok('Rafael Andrade' in resumo and '0,00%' in resumo and 'alíquota 0%' in dica, 'vendedor com 0% no cadastro: o pedido diz que não gera comissão')

        ir(DET, '?id=14')
        resumo, dica = aba_comissao()
        ok('ninguém' in resumo and 'sem vendedor e sem indicação' in dica, 'sem vendedor e sem link, ninguém recebe')

        ir(DET, '?id=7')
        pg.evaluate("document.getElementById('btnProximoPasso').click()"); pg.wait_for_timeout(300)
        txt = pg.inner_text('#confirmModalTexto')
        ok('Marina Costa não depende do faturamento' in txt and 'LIBERA A COMISSÃO' not in txt, 'faturar o pedido da Marina não promete liberar a comissão: "%s"' % txt[-90:])
        pg.evaluate("document.getElementById('btnConfirmModalCancelar').click()"); pg.wait_for_timeout(200)
        pg.evaluate("COMISSAO_DO_VENDEDOR['Marina Costa'].regra = 'integral_faturamento'")
        pg.evaluate("document.getElementById('btnProximoPasso').click()"); pg.wait_for_timeout(300)
        ok('LIBERA A COMISSÃO de Marina Costa' in pg.inner_text('#confirmModalTexto'), 'com a regra "integral no faturamento", faturar avisa que libera')
        pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(500)
        ok('A comissão de Marina Costa está liberada.' in pg.inner_text('#confirmModalTexto'), 'e, feito, diz que liberou')

        ir(DET, '?clonar=4&id=4')
        ok(pg.input_value('#inputIndicacao') == 'Sem indicação' and 'ninguém' in aba_comissao()[0], 'o clone de um pedido por link nasce sem indicação')
        ir(DET, '?novo=1')
        ok(pg.input_value('#inputIndicacao') == 'Sem indicação', 'e o pedido novo também')

    if secao(4, 'Espelhos: as duas telas e o cadastro dizem o mesmo'):
        ir(LISTA)
        da_lista = pg.evaluate("PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.ind || null])")
        rot_lista = pg.evaluate("PEDIDOS.filter(p => p.ind).map(p => rotuloIndicacao(p.ind))")
        ir(DET)
        ok(pg.evaluate("PEDIDOS_DA_LISTA.filter(p => !p.pdv).map(p => [p.id, p.ind || null])") == da_lista, 'a indicação de cada pedido é a mesma na lista e na página')
        ok(pg.evaluate("PEDIDOS_DA_LISTA.filter(p => p.ind).map(p => rotuloIndicacao(p.ind))") == rot_lista, 'e as duas escrevem a indicação do mesmo jeito')
        regra = pg.evaluate("COMISSAO_DO_VENDEDOR")
        ir('pagina-cadastros-vendedores.html')
        cad = {v['nome']: {'aliquota': v['aliquotaComissao'], 'regra': v['regraComissao']} for v in pg.evaluate("VENDEDORES")}
        ok(all(cad.get(n) == r for n, r in regra.items()), 'a regra de cada vendedor é a do cadastro de vendedores: %s' % regra)
        vend_pedidos = set(x['vendedor'] for x in PEDIDOS if x['vendedor']) | set(x['ind']['nome'] for x in PEDIDOS if x.get('ind') and x['ind']['tipo'] == 'vendedor')
        ok(vend_pedidos <= set(regra), 'todo vendedor que aparece nos pedidos tem a regra aqui: %s' % sorted(vend_pedidos))
        ir('pagina-cadastros-clientes.html')
        clientes = set(c['nome'] for c in pg.evaluate("CLIENTES"))
        indicam = [x['ind'] for x in PEDIDOS if x.get('ind') and x['ind']['tipo'] == 'cliente']
        ok(all(i['nome'] in clientes for i in indicam), 'quem indica é cliente cadastrado')
        ok(not [x for x in PEDIDOS if x.get('ind') and x['ind']['nome'] == x['cliente']], 'e ninguém compra pelo próprio link')

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
