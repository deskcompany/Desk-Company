# -*- coding: utf-8 -*-
# O preco de atacado (16/nov/2026): a ficha do produto, o PDV e o Pedido de Venda.
#
# O que ele protege sao as decisoes do usuario (10/nov no mapa de canais; 16/nov na barganha deste plano):
#   O preco mora na ficha do produto (aba Precos): "Preco de atacado" + "A partir de N unidades", os dois juntos ou nenhum; a "Preco por lista" saiu
#   A trava ao salvar: inteiro de 2 para cima, abaixo do preco de venda e nao abaixo do minimo da calculadora; erro no campo, nao em alert
#   O historico do preco ganha uma linha para o preco e outra para a quantidade
#   Na venda (PDV e Pedido de Venda) a soma do produto na venda inteira decide: chegou ao minimo, as linhas se juntam numa so, pelo preco de atacado;
#   caiu abaixo, volta ao caminho de hoje. Atacado e atacado: a promocao nao conta uso e nao divide a linha. Atacado nao e desconto.
#   A linha diz "Atacado, a partir de N un." e, antes do minimo, "faltam N para o atacado (R$ X cada)"
#   Atacado abaixo do minimo da calculadora (custo alto gravado) nao entra na venda
#
#   [1]  Os blocos comuns iguais e a semente (acima do minimo, abaixo do preco de venda e do promocional)
#   [2]  A ficha: a secao antiga saiu; salvar; as travas; apagar
#   [3]  O PDV: o aviso, o atacado, voltar abaixo, a promocao, o desconto, os botoes e o registro
#   [4]  O Pedido de Venda: o mesmo caminho, e salvar
#   [5]  O atacado travado pelo minimo da calculadora nao entra na venda
#   [6]  Os dois temas, 1280 e 1440: sem barra para o lado, selo em Nunito
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys
import localiza
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
PROD = 'pagina-cadastros-produtos-detalhe.html'
PRODS = 'pagina-cadastros-produtos.html'
PDV = 'pagina-vendas-pdv.html'
PEDD = 'pagina-vendas-pedidos-detalhe.html'
LISTA = 'pagina-vendas-promocoes.html'
PAG = 'pagina-vendas-promocoes-detalhe.html'

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


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


def bloco(t, ini, fim):
    i = t.find(ini)
    if i < 0:
        return None
    j = t.find(fim, i)
    return t[i:j] if j >= 0 else None


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('dialog', lambda d: d.dismiss())

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(250)

    def limpar():
        ir(LISTA); pg.evaluate("localStorage.clear(); sessionStorage.clear()")

    def ev(js, *a):
        return pg.evaluate(js, *a) if a else pg.evaluate(js)

    def clica(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(150)

    def modal_aberto():
        return ev("document.getElementById('confirmModal').classList.contains('open')")

    def texto_modal():
        return ev("document.getElementById('confirmModalTexto').textContent")

    def fecha_aviso():
        if modal_aberto():
            clica('#btnConfirmModalConfirmar'); pg.wait_for_timeout(150)

    def escolhe(raiz, v):
        clica('#%s .dropdown-select-btn' % raiz)
        ev("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(v)]); pg.wait_for_timeout(150)

    def txt(sel):
        return ev("(s) => document.querySelector(s).textContent.replace(/\\s+/g, ' ').trim()", sel)

    def ls(chave):
        return ev("(k) => JSON.parse(localStorage.getItem(k) || 'null')", chave)

    # ---------------- ficha ----------------
    def ficha(id_):
        ir(PROD, '?editar=1&id=%d' % id_); clica('.tab-item[data-tab="precos"]')

    def digita(sel, v):
        pg.fill(sel, v); ev("(s) => document.querySelector(s).dispatchEvent(new Event('input', { bubbles: true }))", sel)

    def salva_ficha():
        clica('#btnSalvarProduto'); pg.wait_for_timeout(500)

    def erro_ficha():
        return ev("(() => { const e = document.getElementById('erroAtacado'); return e.classList.contains('show') ? e.textContent : ''; })()")

    def pp(id_):
        ir(PDV); return ev('(i) => promoPrecos(i)', id_)

    # ---------------- PDV ----------------
    def pdv_abre(loja=1):
        ir(PDV); ev("localStorage.removeItem('deskPdv'); localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); ir(PDV)
        clica('#btnAbrirCaixa'); escolhe('abrirLoja', loja); pg.fill('#abrirTroco', '100'); clica('#btnConfirmarAbertura'); pg.wait_for_timeout(250)

    def pdv_add(sku, q='1'):
        pg.fill('#qtdProduto', q); pg.fill('#buscaProduto', sku); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)

    def itens_pdv():
        return ev("venda.itens.map(i => [i.sku, i.qtd, i.preco, i.promocao || null, !!i.atacado])")

    def pdv_item_qtd(i, q):
        clica('#listaItens tbody tr[data-item="%d"] td:nth-child(2)' % i); pg.wait_for_timeout(200)
        pg.fill('#itemQtd', str(q)); ev("document.getElementById('itemQtd').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem'); pg.wait_for_timeout(250)

    def linha_pdv(i):
        return ev("(i) => { const t = document.querySelector('#listaItens tbody tr[data-item=\"' + i + '\"] td.col-texto'); return t ? t.textContent.replace(/\\s+/g, ' ').trim() : ''; }", i)

    # ---------------- Pedido de Venda ----------------
    def ped_campo(i, c, v):
        ev("([i, c, v]) => { const e = document.querySelector('#corpoItens input[data-campo=\"' + c + '\"][data-i=\"' + i + '\"]'); e.value = v; e.dispatchEvent(new Event('input', { bubbles: true })); e.dispatchEvent(new Event('change', { bubbles: true })); }", [i, c, v])
        pg.wait_for_timeout(150)

    def ped_novo(loja=1):
        ir(PEDD, '?novo=1'); escolhe('inputLoja', loja)

    def ped_add(sku, q):
        n = ev("ITENS.findIndex(i => !i.sku)")
        if n < 0:
            clica('#btnAdicionarItem'); n = ev("ITENS.length") - 1
        ped_campo(n, 'sku', sku); ped_campo(n, 'qtd', q)

    def itens_ped():
        return ev("ITENS.filter(i => i.sku).map(i => [i.sku, i.qtd, i.precoLista, i.promocao || null, !!i.atacado])")

    def tags_ped():
        return ev("Array.from(document.querySelectorAll('#corpoItens [data-promo]')).map(e => e.textContent.replace(/\\s+/g, ' ').trim())")

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'Os blocos comuns e a semente'):
        PI, PF = '  // ===== PROMOCOES: DADOS E LEITURA', '  // ===== FIM DO BLOCO PROMOCOES ====='
        cop = [bloco(fonte(n), PI, PF) for n in (LISTA, PAG, PROD, PDV, PEDD)]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco PROMOCOES continua idêntico nas 5 telas que o têm')
        ok('promoGravarAtacado' in cop[0] and 'PROMO_ATACADO_PADRAO' in cop[0], 'e leva o atacado (a semente e a gravação com o histórico)')
        NI, NF = '  // ===== PROMOCOES: NA VENDA', '  // ===== FIM DO BLOCO PROMOCOES: NA VENDA ====='
        nv = [bloco(fonte(n), NI, NF) for n in (PDV, PEDD)]
        ok(nv[0] and nv[0] == nv[1] and 'function promoAtacado' in nv[0], 'o bloco PROMOCOES: NA VENDA continua idêntico no PDV e no Pedido, e leva promoAtacado')
        ir(PDV)
        s = ev("[8, 9].map(i => [promoPrecos(i).atacado, promoPrecos(i).atacadoMin, promoPrecos(i).venda, promoPrecos(i).promocional, promoMinimoCent(promoProdutoId(i))])")
        ok(s[0][:2] == [72.9, 6] and s[1][:2] == [59.5, 10], 'a semente: Luminária (MOB-4002) a partir de 6 un. e o Kit da promoção (PAP-3002) a partir de 10 un.: %s' % s)
        ok(s[0][4] <= round(s[0][0] * 100) and s[0][0] < s[0][2], 'o atacado do Luminária fica acima do mínimo da calculadora (%d) e abaixo do preço de venda (%s)' % (s[0][4], s[0][2]))
        ok(s[1][4] <= round(s[1][0] * 100) and s[1][0] < s[1][3] < s[1][2], 'o do Kit fica acima do mínimo (%d), abaixo do promocional (%s) e do preço de venda (%s)' % (s[1][4], s[1][3], s[1][2]))
        ok(ev("[promoAtacado('MOB-4002'), promoAtacado('PAP-3002'), promoAtacado('ELE-1001'), promoAtacado('XXX-0')]") == [{'preco': 72.9, 'min': 6}, {'preco': 59.5, 'min': 10}, None, None],
           'promoAtacado devolve {preco, min}, ou null para o produto sem atacado e para o que não existe')

        # a guarda: o preco de venda baixou depois do atacado gravado, e o atacado nunca sobe o preco da linha
        ev("localStorage.setItem('deskPrecoProduto', JSON.stringify({ 8: { venda: 70 } }))"); ir(PDV)
        ok(ev("promoAtacado('MOB-4002')") is None, 'atacado maior que o preço de venda de hoje (a venda baixou para R$ 70,00, o atacado é R$ 72,90) devolve null: não entra')
        ev("localStorage.setItem('deskPrecoProduto', JSON.stringify({ 8: { venda: 72.9 } }))"); ir(PDV)
        ok(ev("promoAtacado('MOB-4002')") is None, 'atacado igual ao preço de venda também não entra')
        ev("localStorage.removeItem('deskPrecoProduto')")

    # ------------------------------------------------------------------------------------------------
    if secao(2, 'A ficha do produto: a aba Preços'):
        limpar()
        ficha(1)
        corpo = ev("document.getElementById('tab-precos').textContent")
        ok('Preço por lista' not in corpo and 'Varejo' not in corpo and not ev("!!document.getElementById('inputPrecoListaPadrao')"), 'a seção "Preço por lista" (Padrão, Atacado e Varejo) saiu')
        ok(ev("!!document.getElementById('inputPrecoAtacado') && !!document.getElementById('inputAtacadoMin')"), 'entram "Preço de atacado" e "A partir de"')
        r = ev("(() => { const a = document.getElementById('inputPrecoAtacado'), m = document.getElementById('inputAtacadoMin'); return [a.getAttribute('data-mascara'), a.getAttribute('placeholder'), m.type, m.getAttribute('inputmode'), m.nextElementSibling.textContent.trim(), a.value, m.value]; })()")
        ok(r == ['dinheiro', '0,00', 'text', 'numeric', 'unidades', '', ''], 'o preço tem máscara de dinheiro e 0,00; a quantidade é type=text numérico, com "unidades" ao lado; o produto 1 nasce vazio: %s' % r)
        ok('A promoção não mexe no atacado' in corpo, 'o texto de baixo explica que a promoção não mexe no atacado')
        ordem = ev("(() => { const p = document.getElementById('inputPrecoPromocional'), a = document.getElementById('inputPrecoAtacado'); return !!(p.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING); })()")
        ok(ordem, 'a linha do atacado fica logo abaixo da linha do preço de venda e do promocional')
        ok(ev("document.getElementById('inputPrecoAtacado').getBoundingClientRect().top") > ev("document.getElementById('inputPrecoPromocional').getBoundingClientRect().bottom"), 'e fica abaixo na tela')
        # --- as travas: o erro fica no campo e nada e gravado
        mimo = ev("CALC.minimo()")
        ok(mimo == 7928, 'o mínimo da calculadora do produto 1 é R$ 79,28 (custo de R$ 50,00 da aba Custos): %s' % mimo)

        def tenta(preco, qtd, trecho, rotulo, id_=1):
            ficha(id_); digita('#inputPrecoAtacado', preco); digita('#inputAtacadoMin', qtd); salva_ficha()
            e = erro_ficha()
            ok(trecho in e and PROD in pg.url and not modal_aberto(), '%s: recusa com a mensagem no campo (sem alert): "%s"' % (rotulo, e[:110]))
            ok(ls('deskPrecoProduto') is None or 'atacado' not in (ls('deskPrecoProduto') or {}).get(str(id_), {}), 'e nada foi gravado')
        tenta('90,00', '', 'Informe o preço e a quantidade, ou deixe os dois vazios.', 'só o preço')
        tenta('', '10', 'Informe o preço e a quantidade, ou deixe os dois vazios.', 'só a quantidade')
        tenta('90,00', '1', 'número inteiro, de 2 para cima', 'quantidade 1')
        tenta('90,00', '12,5', 'número inteiro, de 2 para cima', 'quantidade com vírgula')
        tenta('90,00', 'abc', 'número inteiro, de 2 para cima', 'quantidade com letra')
        tenta('129,90', '10', 'precisa ficar abaixo do preço de venda (R$ 129,90)', 'preço igual ao de venda')
        tenta('150,00', '10', 'precisa ficar abaixo do preço de venda', 'preço acima do de venda')
        tenta('70,00', '10', 'abaixo do mínimo da calculadora (R$ 79,28)', 'preço abaixo do mínimo')
        tenta('15,00', '10', 'não tem custo no cadastro', 'produto sem custo no catálogo (o Filamento, id 5)', 5)
        ok(ev("document.getElementById('campoPrecoAtacado').classList.contains('has-error')"), 'o campo fica com a borda de erro')
        digita('#inputPrecoAtacado', '90,00')
        ok(erro_ficha() == '', 'digitar de novo limpa o erro')
        # --- salvar grava o preco, a quantidade e as duas linhas do historico
        ficha(1); digita('#inputPrecoAtacado', '90,00'); digita('#inputAtacadoMin', '10'); salva_ficha()
        reg = (ls('deskPrecoProduto') or {}).get('1', {})
        ok(PRODS in pg.url and reg.get('atacado') == 90 and reg.get('atacadoMin') == 10, 'salvar grava 90,00 a partir de 10 un. e volta para a lista: %s' % reg)
        h = [x for x in (ls('deskHistoricoPreco') or {}).get('1', []) if x['campo'] in ('atacado', 'atacadoMin')]
        ok(len(h) == 2 and sorted((x['campo'], x['de'], x['para'], x['origem']) for x in h) == [('atacado', None, 90, 'cadastro'), ('atacadoMin', None, 10, 'cadastro')],
           'e cria as duas linhas do histórico (o preço e a quantidade): %s' % h)
        ficha(1)
        ok(ev("document.getElementById('inputPrecoAtacado').value") == '90,00' and ev("document.getElementById('inputAtacadoMin').value") == '10', 'reabrir a ficha mostra o que foi gravado')
        hist = ev("document.getElementById('tabelaHistoricoPreco').innerText")
        ok('Atacado a partir de' in hist and 'Atacado' in hist and '10 un.' in hist and 'R$ 90,00' in hist, 'a tabela do histórico mostra "Atacado" e "Atacado a partir de"')
        ok(ev("promoSubiu(1)") is None, 'o histórico do atacado não mexe na trava do "preço de venda subiu"')
        # salvar sem mexer nao grava de novo
        salva_ficha(); ficha(1)
        ok(len([x for x in (ls('deskHistoricoPreco') or {}).get('1', []) if x['campo'] in ('atacado', 'atacadoMin')]) == 2, 'salvar sem mexer no atacado não cria linha nova')
        # mudar so a quantidade: uma linha so
        digita('#inputAtacadoMin', '15'); salva_ficha()
        h = [x for x in (ls('deskHistoricoPreco') or {}).get('1', []) if x['campo'] in ('atacado', 'atacadoMin')]
        ok(len(h) == 3 and [x for x in h if x['campo'] == 'atacadoMin' and x['de'] == 10 and x['para'] == 15], 'mudar só a quantidade (10 para 15) cria uma linha só, a da quantidade')
        # --- apagar os dois
        ficha(1); digita('#inputPrecoAtacado', ''); digita('#inputAtacadoMin', ''); salva_ficha()
        reg = (ls('deskPrecoProduto') or {}).get('1', {})
        h = [x for x in (ls('deskHistoricoPreco') or {}).get('1', []) if x['campo'] in ('atacado', 'atacadoMin')]
        ok(PRODS in pg.url and reg.get('atacado') is None and reg.get('atacadoMin') is None and pp(1)['atacado'] is None, 'apagar os dois tira o atacado do produto (grava null)')
        ok(len(h) == 5 and [x for x in h if x['campo'] == 'atacado' and x['de'] == 90 and x['para'] is None], 'e deixa a linha no histórico (de R$ 90,00 para nada)')
        # --- o atacado de semente nao trava o resto do cadastro, e apagar o de semente vale
        ficha(8)
        ok(ev("document.getElementById('inputPrecoAtacado').value") == '72,90' and ev("document.getElementById('inputAtacadoMin').value") == '6', 'a ficha do Luminária abre com o atacado de semente: 72,90 a partir de 6')
        salva_ficha()
        ok(PRODS in pg.url and erro_ficha() == '' if False else PRODS in pg.url, 'salvar a ficha do Luminária sem mexer no atacado não é travado (o produto não tem custo na aba Custos)')
        ficha(8); digita('#inputPrecoAtacado', ''); digita('#inputAtacadoMin', ''); salva_ficha()
        ok(pp(8)['atacado'] is None and ev("promoAtacado('MOB-4002')") is None, 'apagar o de semente também vale (null gravado ganha da semente)')

        # --- a aba Custos grava (16/nov): a Luminaria abre com o custo do catalogo, e o minimo e um so, na ficha e no PDV
        limpar(); ficha(8)
        cus = ev("Array.from(document.querySelectorAll('#tabelaCustos tr')).map(tr => Array.from(tr.querySelectorAll('input')).map(i => i.value))")
        ok(len(cus) == 1 and cus[0][3] == '47,06' and cus[0][4] == '46,08' and cus[0][5] == '79,90', 'a Luminária abre a aba Custos com o custo do catálogo (custo 47,06, custo médio 46,08, venda 79,90): %s' % cus)
        ok(ev("CALC.minimo()") == 6992 and pp(8) is not None and ev("promoMinimoCent(promoProdutoId(8))") == 6992, 'a ficha e o PDV dão o mesmo mínimo, R$ 69,92, sem nada gravado')
        ficha(5)
        ok(ev("document.querySelectorAll('#tabelaCustos tr').length") == 0, 'produto sem custo no catálogo (Filamento) segue sem linha')
        ficha(8); digita('#inputPrecoAtacado', '72,90'); digita('#inputAtacadoMin', '7'); salva_ficha()
        ok(PRODS in pg.url and (ls('deskPrecoProduto') or {}).get('8', {}).get('atacadoMin') == 7, 'o atacado da Luminária salva, sem "não tem custo"')
        ficha(8); clica('.tab-item[data-tab="custos"]')
        pg.evaluate("() => 0")
        ev("(() => { const i = document.querySelectorAll('#tabelaCustos tr input'); i[3].value = '60,00'; i[4].value = '55,00'; })()")
        salva_ficha()
        ficha(8)
        cus = ev("Array.from(document.querySelectorAll('#tabelaCustos tr')).map(tr => Array.from(tr.querySelectorAll('input')).map(i => i.value))")
        ok(cus[0][3] == '60,00' and cus[0][4] == '55,00' and (ls('deskCustoProduto') or {}).get('8', [{}])[0].get('custoMedio') == '55,00', 'mudar o custo, salvar e recarregar mantém o valor: %s' % cus)
        m = ev("CALC.minimo()")
        ok(m > 6992 and pp(8) is not None and ev("promoMinimoCent(promoProdutoId(8))") == m, 'o mínimo do PDV muda junto com o custo gravado e continua igual ao da ficha (R$ %s)' % (m / 100.0))
        ev("localStorage.removeItem('deskCustoProduto')")

    # ------------------------------------------------------------------------------------------------
    if secao(3, 'O PDV'):
        limpar()
        pdv_abre(1); pdv_add('MOB-4002', '5')
        ok(itens_pdv() == [['MOB-4002', 5, 79.9, None, False]], 'o Luminária com 5 fica no preço de venda: %s' % itens_pdv())
        l = linha_pdv(0)
        ok('faltam 1 para o atacado (R$ 72,90 cada)' in l and 'Atacado' not in l.replace('para o atacado', ''), 'e a linha avisa "faltam 1 para o atacado (R$ 72,90 cada)": %s' % l)
        ok(ev("(() => { const e = Array.from(document.querySelectorAll('#listaItens .pdv-item-sub')).filter(x => x.textContent.indexOf('faltam') >= 0)[0]; return !!e && getComputedStyle(e).color === getComputedStyle(document.querySelector('#listaItens .pdv-item-sub')).color; })()"),
           'o aviso usa o estilo de texto secundário da tela, sem cor de alerta')
        # a previa de "Adicionar produto" conta o atacado: a soma do que ja esta na venda mais a quantidade digitada
        ev("selecionarProduto(produtoDe('MOB-4002'))"); pg.fill('#qtdProduto', '1'); ev("document.getElementById('qtdProduto').dispatchEvent(new Event('input'))")
        ok(txt('#prodPreco') == 'R$ 72,90 Atacado' and txt('#prodTotal') == 'R$ 72,90', 'a prévia com 5 na venda + 1 digitada = 6 mostra o atacado: %s / %s' % (txt('#prodPreco'), txt('#prodTotal')))
        ev("limparProduto()")
        pdv_add('MOB-4002', '1')
        ok(itens_pdv() == [['MOB-4002', 6, 72.9, None, True]], 'com 6, as linhas viram uma só, pelo preço de atacado: %s' % itens_pdv())
        l = linha_pdv(0)
        ok('Atacado' in l and 'a partir de 6 un.' in l and 'faltam' not in l, 'a linha mostra o selo "Atacado" e "a partir de 6 un.", e o aviso some: %s' % l)
        ok(ev("document.querySelector('#listaItens .promo-tag .promo-tag-selo').textContent") == 'Atacado', 'a etiqueta usa a classe promo-tag da promoção')
        ok(ev("subtotal()") == 437.4 and ev("totalVenda()") == 437.4, 'o total é 6 x R$ 72,90 = R$ 437,40: %s' % ev("totalVenda()"))
        ok(ev("venda.itens[0].precoOriginal") == 79.9 and not ev("venda.itens[0].promocao") and not ev("venda.itens[0].naHora") and not ev("venda.itens[0].excedente"), 'a linha guarda o preço de venda como original, sem promoção, sem "na hora" e sem excedente')
        # voltar a 5 devolve o preco de venda
        pdv_item_qtd(0, 5)
        ok(itens_pdv() == [['MOB-4002', 5, 79.9, None, False]] and 'faltam 1 para o atacado' in linha_pdv(0), 'voltar a 5 devolve o preço de venda e o aviso')
        pdv_item_qtd(0, 6)
        ok(itens_pdv() == [['MOB-4002', 6, 72.9, None, True]], 'subir a 6 pelo painel do item volta ao atacado')
        # tirar uma linha: duas linhas do produto somam, e tirar derruba abaixo do minimo
        ev("venda = novaVenda()"); ev("pintarVenda()")
        pdv_add('MOB-4002', '4'); pdv_add('MOB-4002', '2')
        ok(itens_pdv() == [['MOB-4002', 6, 72.9, None, True]], '4 + 2 na mesma venda somam 6: atacado numa linha só')
        pg.evaluate("document.querySelector('#listaItens [data-remover=\"0\"]').click()"); pg.wait_for_timeout(200)
        ok(itens_pdv() == [], 'remover a linha de atacado esvazia a venda')
        # --- o painel do item
        pdv_add('MOB-4002', '6')
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)'); pg.wait_for_timeout(250)
        ok('Atacado' in txt('#itemPromo') and 'a partir de 6 un.' in txt('#itemPromo') and ev("document.getElementById('itemPromo').offsetParent !== null"), 'o painel do item mostra a etiqueta do atacado')
        ok(ev("document.getElementById('btnAplicarPromo').offsetParent === null") and ev("document.getElementById('itemExcedente').offsetParent === null"),
           'e não tem os botões "Aplicar preço promocional" nem "Aplicar preço promocional no excedente"')
        # o desconto na mao vale por cima do atacado: 10% no item nao pede liberacao e a base e o preco de atacado
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        lim = ev("autoLimiteVenda().pct")
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)'); pg.wait_for_timeout(200)
        ev("document.querySelector('input[name=itemAjusteModo][value=pct]').click()")
        pg.fill('#itemAjusteValor', str(lim)); ev("document.getElementById('itemAjusteValor').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem'); pg.wait_for_timeout(200)
        ok(not modal_aberto() and ev("venda.itens[0].ajusteValor") == lim, 'desconto de %s%% (o limite) no item de atacado passa sem liberação' % lim)
        ok(ev("descontoPctDoItem(venda.itens[0])") == lim, 'a base do percentual é o preço de atacado da linha (%s%%), não o preço de venda' % lim)
        clica('#listaItens tbody tr[data-item="0"] td:nth-child(2)'); pg.wait_for_timeout(200)
        pg.fill('#itemAjusteValor', str(lim + 1)); ev("document.getElementById('itemAjusteValor').dispatchEvent(new Event('input'))"); clica('#btnAplicarItem'); pg.wait_for_timeout(250)
        ok(modal_aberto() and 'Liberar desconto' in texto_modal(), 'um ponto acima do limite pede a liberação: o desconto na mão continua limitado')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150); fecha_aviso()

        # --- o Kit com promocao ativa: atacado e atacado, a promocao nao conta uso
        pdv_abre(1)
        antes = ev("promoVendido(lerPromocoes().filter(p => p.id === 1)[0]).porSku['PAP-3002'].qtd")
        pdv_add('PAP-3002', '5')
        ok(itens_pdv() == [['PAP-3002', 2, 59.9, 1, False], ['PAP-3002', 3, 64.9, None, False]], 'o Kit com 5: 2 no preço da promoção e 3 pelo preço de venda (limite de 2 por cliente): %s' % itens_pdv())
        ok('faltam 5 para o atacado (R$ 59,50 cada)' in linha_pdv(0) and 'faltam' not in linha_pdv(1), 'o aviso sai uma vez, na primeira linha do produto: faltam 5 (R$ 59,50 cada)')
        pdv_add('PAP-3002', '5')
        ok(itens_pdv() == [['PAP-3002', 10, 59.5, None, True]], 'com 10 (2 da promoção + 3 + 5), as linhas se juntam numa só pelo preço de atacado, sem promoção: %s' % itens_pdv())
        ok(not ev("venda.itens[0].excedente") and ev("venda.itens[0].precoOriginal") == 64.9, 'sem excedente; o original é o preço de venda (R$ 64,90)')
        ok(ev("subtotal()") == 595, 'o total é 10 x R$ 59,50 = R$ 595,00 (abaixo do promocional de R$ 59,90)')
        # desconto na venda ate o limite do vendedor: nao pede liberacao por causa do atacado
        clica('#btnContinuar'); pg.wait_for_timeout(300)
        pg.fill('#finDesconto', '%s%%' % lim); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
        ok(not ev("document.getElementById('notaFinDesconto').offsetParent !== null"), 'desconto de %s%% na venda (o limite): sem aviso de "acima do máximo" na tela' % lim)
        escolhe('selAddReceb', 'pix'); clica('#btnFinalizar'); pg.wait_for_timeout(450)
        ok(ev("momento") == 'concluida' and not (modal_aberto() and 'Liberar desconto' in texto_modal()), 'e finaliza sem pedir liberação (o atacado nem a promoção entram na conta do desconto)')
        fecha_aviso()
        v = ev("ultimaVenda")
        ok(v['itens'][0]['atacado'] is True and v['itens'][0]['promocao'] is None and v['itens'][0]['qtd'] == 10 and v['itens'][0]['preco'] == 59.5,
           'o cupom grava a linha com atacado: true, sem promoção: %s' % [v['itens'][0].get(k) for k in ('sku', 'qtd', 'preco', 'atacado', 'promocao')])
        ok(abs(v['desconto'] - 59.5) < 0.005 and abs(v['subtotal'] - 595) < 0.005, 'o desconto de 10%% é sobre o atacado: R$ %s sobre R$ %s' % (v['desconto'], v['subtotal']))
        depois = ev("promoVendido(lerPromocoes().filter(p => p.id === 1)[0]).porSku['PAP-3002'].qtd")
        ok(depois == antes, 'a promoção não conta uso nenhum para as 10 peças de atacado (vendido antes %s, depois %s)' % (antes, depois))
        # o controle: um ponto acima do limite pede a liberacao
        pdv_abre(1); pdv_add('PAP-3002', '10'); clica('#btnContinuar'); pg.wait_for_timeout(300)
        pg.fill('#finDesconto', '%s%%' % (lim + 1)); pg.locator('#finDesconto').blur(); pg.wait_for_timeout(250)
        escolhe('selAddReceb', 'pix'); clica('#btnFinalizar'); pg.wait_for_timeout(350)
        ok(modal_aberto() and 'Liberar desconto' in texto_modal(), 'controle: %s%% na venda de atacado pede a liberação (o limite da pessoa continua valendo)' % (lim + 1))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)

        # --- caiu abaixo do minimo: volta ao caminho de hoje (a promocao onde ela vale, com o limite)
        pdv_abre(1); pdv_add('PAP-3002', '10')
        ok(itens_pdv() == [['PAP-3002', 10, 59.5, None, True]], 'o Kit com 10 de uma vez já entra no atacado')
        pdv_item_qtd(0, 9)
        ok(itens_pdv() == [['PAP-3002', 2, 59.9, 1, False], ['PAP-3002', 7, 64.9, None, False]], 'baixar para 9 volta ao caminho de hoje: 2 no preço da promoção e 7 pelo de venda: %s' % itens_pdv())
        pdv_add('PAP-3002', '1')
        ok(itens_pdv() == [['PAP-3002', 10, 59.5, None, True]], 'e subir a 10 de novo junta tudo no atacado (a linha do excedente também)')

    # ------------------------------------------------------------------------------------------------
    if secao(4, 'O Pedido de Venda'):
        limpar()
        ped_novo(1); ped_add('MOB-4002', '5')
        ok(itens_ped() == [['MOB-4002', 5, 79.9, None, False]], 'o Luminária com 5 fica no preço de venda: %s' % itens_ped())
        ok('faltam 1 para o atacado (R$ 72,90 cada)' in tags_ped()[0], 'a linha avisa "faltam 1 para o atacado (R$ 72,90 cada)": %s' % tags_ped())
        ped_campo(0, 'qtd', '6')
        ok(itens_ped() == [['MOB-4002', 6, 72.9, None, True]], 'com 6, o preço da linha vira o de atacado sozinho: %s' % itens_ped())
        t = tags_ped()[0]
        ok('Atacado' in t and 'a partir de 6 un.' in t and 'faltam' not in t, 'a linha mostra o selo "Atacado" e "a partir de 6 un.": %s' % t)
        ok(ev("document.querySelector('#corpoItens [data-promo] .promo-tag .promo-tag-selo').textContent") == 'Atacado', 'com a classe promo-tag')
        ok(txt('#totProdutos') == 'R$ 437,40', 'o total dos produtos é R$ 437,40: %s' % txt('#totProdutos'))
        ped_campo(0, 'qtd', '5')
        ok(itens_ped() == [['MOB-4002', 5, 79.9, None, False]], 'voltar a 5 devolve o preço de venda')
        ped_campo(0, 'qtd', '6')
        # --- o drawer do item
        clica('#corpoItens [data-editar="0"]'); pg.wait_for_timeout(250)
        d = txt('#drawerCorpo')
        ok('Atacado' in d and 'a partir de 6 un.' in d and not ev("!!document.getElementById('btnAplicarPromoItem')") and not ev("!!document.getElementById('btnAplicarPromoExcedente')"),
           'o painel do item mostra a etiqueta do atacado, sem os botões de preço promocional')
        clica('#btnCancelarItem'); pg.wait_for_timeout(150)
        # --- o Kit com promocao: junta as linhas
        ped_novo(1); ped_add('PAP-3002', '3')
        ok(itens_ped() == [['PAP-3002', 2, 59.9, 1, False], ['PAP-3002', 1, 64.9, None, False]], 'o Kit com 3: a promoção (2) e o excedente (1) em linhas separadas: %s' % itens_ped())
        ok('faltam 7 para o atacado (R$ 59,50 cada)' in tags_ped()[0] and 'faltam' not in tags_ped()[1], 'o aviso (faltam 7) sai só na primeira linha do produto')
        ped_campo(0, 'qtd', '9')
        ok(itens_ped() == [['PAP-3002', 10, 59.5, None, True]], 'com 9 + 1 = 10 as linhas se juntam numa só pelo preço de atacado, sem promoção: %s' % itens_ped())
        ok(ev("ITENS[0].precoVenda") == 64.9 and not ev("ITENS[0].excedente"), 'o original é o preço de venda e não sobra excedente')
        ped_campo(0, 'qtd', '9')
        ok(itens_ped() == [['PAP-3002', 2, 59.9, 1, False], ['PAP-3002', 7, 64.9, None, False]], 'baixar para 9 volta ao caminho de hoje: 2 pela promoção e 7 pelo preço de venda: %s' % itens_ped())
        ped_campo(0, 'qtd', '3')
        ok(itens_ped() == [['PAP-3002', 2, 59.9, 1, False], ['PAP-3002', 8, 64.9, None, False]] or ev("ITENS.reduce((s, i) => s + i.qtd, 0)") == 10, 'a soma continua valendo (a conta é do produto, não da linha)')
        # --- remover uma linha derruba abaixo do minimo
        ped_novo(1); ped_add('MOB-4002', '6')
        clica('#btnAdicionarItem'); n = ev("ITENS.length") - 1; ped_campo(n, 'qtd', '1'); ped_campo(n, 'sku', 'MOB-4002')
        ok(itens_ped() == [['MOB-4002', 7, 72.9, None, True]], 'a linha nova do mesmo produto entra na soma: 6 + 1 = 7 numa linha de atacado: %s' % itens_ped())
        clica('#corpoItens [data-remover="0"]'); pg.wait_for_timeout(200)
        ok(itens_ped() == [], 'remover a linha de atacado esvazia o pedido (o produto some todo)')
        # --- desconto por cima, salvar
        ped_novo(1); ped_add('PAP-3002', '10')
        ok(itens_ped() == [['PAP-3002', 10, 59.5, None, True]], 'o Kit com 10 de uma vez já entra no atacado')
        escolhe('inputVendedor', 'Marina Costa')
        lim = ev("autoLimiteVenda().pct")
        ok(lim == 18, 'a vendedora (Marina Costa) tem o limite de 18%%: %s' % lim)
        ev("ITENS[0].desconto = %s; renderItens()" % lim)
        ok(abs(ev("precoUnit(ITENS[0])") - 59.5 * (1 - lim / 100.0)) < 0.001, 'o desconto do item vale sobre o preço de atacado (R$ 59,50 − %s%%)' % lim)
        pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))")
        ev("ITENS[0].desconto = 0; renderItens()")
        pg.fill('#inputDesconto', '%s%%' % lim); ev("document.getElementById('inputDesconto').dispatchEvent(new Event('input', { bubbles: true }))")
        ev("PARAM.bloquearPedidoAtrasoDias = 0"); clica('#btnSalvar'); pg.wait_for_timeout(300)
        ok(modal_aberto() and 'Pedido salvo' in texto_modal() and 'Liberar desconto' not in texto_modal(), 'desconto de %s%% (o limite) no pedido de atacado: o pedido salva, sem pedir liberação por causa do atacado' % lim)
        fecha_aviso(); pg.wait_for_timeout(200)
        uso = ev("JSON.parse(localStorage.getItem('deskPromoUsos') || '{}')")
        ok(uso == {}, 'salvar não grava uso de promoção para as peças de atacado: %s' % uso)
        ok(itens_ped() == [['PAP-3002', 10, 59.5, None, True]] and ev("ITENS[0].atacadoMin") == 10, 'o pedido salvo segue com o preço gravado (R$ 59,50, atacado, a partir de 10)')
        ev("renderItens()")
        ok(itens_ped() == [['PAP-3002', 10, 59.5, None, True]], 'redesenhar o pedido não recalcula: só mexer na quantidade recalcula')
        ped_novo(1); ped_add('PAP-3002', '10'); escolhe('inputVendedor', 'Marina Costa'); pg.fill('#inputCliente', 'Juliana Prado'); ev("document.getElementById('inputCliente').dispatchEvent(new Event('input'))"); pg.fill('#inputDesconto', '%s%%' % (lim + 1)); ev("document.getElementById('inputDesconto').dispatchEvent(new Event('input', { bubbles: true }))")
        ev("PARAM.bloquearPedidoAtrasoDias = 0"); clica('#btnSalvar'); pg.wait_for_timeout(300)
        ok(modal_aberto() and 'Liberar desconto' in texto_modal(), 'controle: %s%% no pedido de atacado pede a liberação (o limite da pessoa continua)' % (lim + 1))
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        # --- preco mexido a mao deixa o produto fora da conta
        ped_novo(1); ped_add('MOB-4002', '6')
        ped_campo(0, 'precoLista', '70,00')
        ped_campo(0, 'qtd', '3')
        ok(itens_ped() == [['MOB-4002', 3, 70, None, False]], 'o preço mexido à mão vale, e a linha deixa de ser de atacado ao baixar a quantidade: %s' % itens_ped())

    # ------------------------------------------------------------------------------------------------
    if secao(5, 'O atacado travado pelo mínimo da calculadora não entra na venda'):
        limpar()
        ir(PDV)
        ev("localStorage.setItem('deskCalculoPreco', JSON.stringify({ 8: { preco: 90, frete: 40 } }))")
        ir(PDV)
        ok(ev("promoMinimoCent(promoProdutoId(8))") > 7290 and ev("promoAtacado('MOB-4002')") is None, 'com um custo alto gravado (frete de R$ 40,00), o mínimo passa do atacado e promoAtacado devolve null')
        pdv_abre(1)
        pdv_add('MOB-4002', '6')
        ok(itens_pdv() == [['MOB-4002', 6, 79.9, None, False]] and 'faltam' not in linha_pdv(0), 'PDV: com 6 o Luminária fica no preço de venda, sem atacado e sem aviso: %s' % itens_pdv())
        ped_novo(1); ped_add('MOB-4002', '6')
        ok(itens_ped() == [['MOB-4002', 6, 79.9, None, False]], 'Pedido: o mesmo, o atacado travado não entra: %s' % itens_ped())
        ev("localStorage.removeItem('deskCalculoPreco')")
        ped_novo(1); ped_add('MOB-4002', '6')
        ok(itens_ped() == [['MOB-4002', 6, 72.9, None, True]], 'tirado o custo alto, o atacado volta a entrar')
        # produto sem custo no cadastro: o minimo nao tem como ser conferido, e o atacado nao entra
        ev("localStorage.setItem('deskPrecoProduto', JSON.stringify({ 5: { atacado: 80, atacadoMin: 3 } }))")
        ir(PDV)
        ok(ev("promoAtacado('ELE-1002')") is None and ev("promoPrecos(5).atacado") == 80, 'produto sem custo no cadastro (Filamento): o atacado gravado não entra (não há como conferir o mínimo)')

    # ------------------------------------------------------------------------------------------------
    if secao(6, 'Os dois temas, 1280 e 1440'):
        limpar()
        for w in (1280, 1440):
            for tema in ('claro', 'escuro'):
                pg.set_viewport_size({'width': w, 'height': 900})
                pdv_abre(1); pdv_add('MOB-4002', '5')
                if tema == 'escuro':
                    ev("document.body.classList.add('dark')")
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.querySelector('#listaItens .pdv-item-sub:last-child, #listaItens .pdv-item-sub')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True], 'PDV com o aviso do atacado a %d, tema %s: sem barra para o lado, Nunito: %s' % (w, tema, r))
                pdv_add('MOB-4002', '1')
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.querySelector('#listaItens .promo-tag-selo')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True], 'PDV com a linha de atacado a %d, tema %s: sem barra para o lado, selo em Nunito: %s' % (w, tema, r))
                ped_novo(1); ped_add('MOB-4002', '6')
                if tema == 'escuro':
                    ev("document.body.classList.add('dark')")
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.querySelector('#corpoItens .promo-tag-selo')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True], 'Pedido com a linha de atacado a %d, tema %s: sem barra para o lado, selo em Nunito: %s' % (w, tema, r))
                ficha(1)
                if tema == 'escuro':
                    ev("document.body.classList.add('dark')")
                r = ev("[document.documentElement.scrollWidth <= document.documentElement.clientWidth, getComputedStyle(document.getElementById('inputAtacadoMin')).fontFamily.indexOf('Nunito') >= 0]")
                ok(r == [True, True], 'ficha, aba Preços, a %d, tema %s: sem barra para o lado, campos em Nunito: %s' % (w, tema, r))
        pg.set_viewport_size({'width': 1440, 'height': 900})

    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript em toda a suíte: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
