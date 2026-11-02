# -*- coding: utf-8 -*-
# A calculadora de preco da aba Precos de Cadastros > Produtos (aprovada em 30/out/2026), com a conta refeita aqui, independente, em Decimal.
#
# O que ele protege sao as decisoes do usuario, as que "simplificar" apaga primeiro:
#   A calculadora so da visao e preenche campos; o preco continua editavel a mao e ela NUNCA sobrescreve sozinha, so ao clicar em Aplicar
#   Taxa e tarifa vem do gateway da loja virtual da loja do produto (a mesma fonte de Custos do E-commerce); a tarifa em R$ entra na conta; loja sem gateway: taxa 0
#   O Exato sobe ao centavo (a margem nunca fica abaixo da pedida); o "Abaixo da faixa" some na beira da faixa e abaixo da margem minima
#   A lista de parcelas fica numa linha so, com a mesma altura em todos os itens (10x, 11x e 12x quebravam)
#   O calculo guardado vence os parametros; o custo do produto e o da embalagem sao lidos de novo; a embalagem digitada a mao so vale ate trocar a caixa
#
#   [1]  Os numeros da aprovacao (produto 1, Desk Shope, custo 50,00): as quatro sugestoes, a conta, as formas de pagamento, a venda nossa, o minimo, o Custos e o Markup;
#   [2]  A conta contra o oraculo em Decimal, em varios cenarios (custo, margem, parcelas, imposto, comissao);
#   [3]  As bordas: o Varejo na beira da faixa, o custo baixo, margem abaixo da minima, margem que nao fecha, comissao 0 escondendo o bloco;
#   [4]  Os parametros mudando o que entra, e a parcela limitada ao que o gateway tem;
#   [5]  Parametros de Vendas: os dois campos novos, a validacao, o registro e o restaurar;
#   [6]  O gateway: taxa mudada, tarifa maior que zero, Desk Brands (Tag Brands), Desk Tech (sem gateway), sem loja escolhida, trocar a loja e reabrir;
#   [7]  O campo Embalagem do produto, o cadastro de Embalagens mudando o custo, "customizada" usando a sugestao, a embalagem digitada a mao;
#   [8]  O custo: custo medio, o custo lido de novo a cada abertura, produto sem custo;
#   [9]  Aplicar: os tres campos, o calculo guardado, o registro de atividades, o reload, o salvo com prioridade;
#   [10] Edicao a mao + Salvar alteracoes sobrevivendo ao reload, e a calculadora que nunca grava sozinha;
#   [11] Modo leitura e cadastro novo;
#   [12] A lista de parcelas de uma linha so, a 1280, 1024 e 853 px, e a gaveta sem barra para o lado;
#   [13] Os dois temas e o contraste;
#   [14] O catalogo da acao, a chave do localStorage e Esc.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys, datetime, json
import localiza
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING, ROUND_FLOOR
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
PROD = 'pagina-cadastros-produtos-detalhe.html'
PARAM_V = 'pagina-configuracoes-parametros-vendas.html'
REGISTRO = 'pagina-configuracoes-registro-atividades.html'
FIXO = datetime.datetime(2026, 10, 30, 10, 0, 0)

falhas = []
total = [0]
erros = []


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


def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e


def fonte(n):
    return open(localiza.onde(n), encoding='utf-8').read()


# ====================================================================== o oraculo: a conta refeita em Decimal, sem olhar para o codigo da tela
LINK = [D(x) for x in ('4.20', '6.09', '7.01', '7.91', '8.80', '9.67', '12.59', '13.42', '14.25', '15.06', '15.87', '16.66')]   # o Link de Pagamento: 1x a 12x
CENT = D('0.01')


def q(x):
    return D(x).quantize(CENT, rounding=ROUND_HALF_UP)


def brl(x):
    x = q(x)
    s = '{:,.2f}'.format(abs(x)).replace(',', 'X').replace('.', ',').replace('X', '.')
    return ('− ' if x < 0 else '') + 'R$ ' + s


def campo(x):
    return brl(x).replace('R$ ', '')


def pct1(x):
    return str(D(x).quantize(D('0.1'), rounding=ROUND_HALF_UP)).replace('.', ',') + '%'


def pctt(x):
    return format(D(x).quantize(CENT).normalize(), 'f').replace('.', ',') + '%'


def conta(preco, custo, taxa, tarifa, imp, com):
    t = q(preco * taxa / 100) + D(tarifa)
    i, c = q(preco * imp / 100), q(preco * com / 100)
    return {'preco': q(preco), 'taxa': t, 'imposto': i, 'comissao': c, 'lucro': q(preco) - custo - t - i - c}


def margem(r):
    return r['lucro'] / r['preco'] * 100


def exato_de(custo, tarifa, m, taxa, imp, com):
    sobra = 1 - (D(m) + taxa + imp + com) / 100
    return ((custo + tarifa) / sobra).quantize(CENT, rounding=ROUND_CEILING) if sobra > 0 else None


def oraculo(custo_total, m, taxa, tarifa, imp, com, minima=D(15), tabela=None):
    """As quatro sugestoes, na ordem da tela, so as que a tela deve mostrar. `tabela`: taxa e tarifa de cada vezes (para as formas)."""
    custo_total, m, taxa, tarifa, imp, com, minima = [D(x) for x in (custo_total, m, taxa, tarifa, imp, com, minima)]
    ex = exato_de(custo_total, tarifa, m, taxa, imp, com)
    if ex is None:
        return None
    var = ex.to_integral_value(rounding=ROUND_FLOOR) + D('0.90')
    if var < ex:
        var += 1
    passo = D(10) if var < 1000 else D(100)
    if var % passo == passo - D('0.10'):
        barr = D(0)
    else:
        barr = ((var - (passo - D('0.10')) - D('0.01')) / passo).to_integral_value(rounding=ROUND_FLOOR) * passo + (passo - D('0.10'))
    degrau = D(1) if ex < 20 else D(5) if ex < 100 else D(10) if ex < 1000 else D(50)
    red = (ex / degrau).to_integral_value(rounding=ROUND_CEILING) * degrau
    ops = []
    for id_, p in (('varejo', var), ('barreira', barr), ('redondo', red), ('exato', ex)):
        if p <= 0:
            continue
        r = conta(p, custo_total, taxa, tarifa, imp, com)
        if id_ == 'barreira' and margem(r) < minima:
            continue
        cor = 'minima' if margem(r) < minima else ('abaixo' if margem(r) < m - D('0.005') else '')
        ops.append(dict(id=id_, r=r, cor=cor))
    sobra_min = 1 - (minima + taxa + imp + com) / 100
    piso = ((custo_total + tarifa) / sobra_min).quantize(CENT, rounding=ROUND_CEILING) if sobra_min > 0 else None
    return dict(ops=ops, piso=piso, ex=ex, custo_total=custo_total)


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)

    def nova(w=1280, h=800, tema='dark'):
        """Uma aba num contexto novo: localStorage limpo, o relogio na sexta 30/10/2026 e o tema pedido."""
        pg = nav.new_context(viewport={'width': w, 'height': h}).new_page()
        pg.on('pageerror', lambda e: erros.append(str(e)[:200]))
        pg.on('console', lambda m: erros.append(m.text[:200]) if m.type == 'error' and not ruido(m.text) else None)
        pg.clock.set_fixed_time(FIXO)
        pg.add_init_script("try { var _p = JSON.parse(localStorage.getItem('deskParametros') || '{}'); if (!_p.tema) { _p.tema = '%s'; localStorage.setItem('deskParametros', JSON.stringify(_p)); } } catch (e) {}" % tema)
        return pg

    def ir(pg, tela, q_=''):
        pg.goto(localiza.uri(tela) + q_); pg.wait_for_load_state('load'); pg.wait_for_timeout(450)

    def ls(pg, chave):
        return pg.evaluate("(k) => JSON.parse(localStorage.getItem(k) || 'null')", chave)

    def ls_set(pg, chave, valor):
        pg.evaluate("([k, v]) => localStorage.setItem(k, JSON.stringify(v))", [chave, valor])

    def param_set(pg, **kv):
        pr = ls(pg, 'deskParametros') or {}
        pr.update(kv)
        ls_set(pg, 'deskParametros', pr)

    def editar(pg, q_='', loja=None, tela=PROD):
        """Abre a ficha do produto ja editavel, na aba Precos, e escolhe a loja."""
        ir(pg, tela, '?editar=1' + q_)
        if loja:
            pg.click('.tab-item[data-tab="complementares"]')   # a Loja Desk mora em Dados Complementares
            escolher(pg, '#inputLojaDesk', loja)
        pg.click('.tab-item[data-tab="precos"]')

    def escolher(pg, raiz, valor):
        pg.click(raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(80)
        pg.click(raiz + ' .dropdown-select-item[data-value="%s"]' % valor); pg.wait_for_timeout(120)

    def trocar_loja(pg, loja):
        pg.click('.tab-item[data-tab="complementares"]')
        escolher(pg, '#inputLojaDesk', loja)
        pg.click('.tab-item[data-tab="precos"]')

    def abrir(pg):
        pg.click('#btnCalcularPreco'); pg.wait_for_timeout(300)

    def fechar(pg):
        pg.click('#calcFechar'); pg.wait_for_timeout(250)

    def preencher(pg, **kv):
        ids = dict(custo='calcCusto', frete='calcFrete', emb='calcEmbalagem', freteloja='calcFreteLoja', margem='calcMargem', imposto='calcImposto', comissao='calcComissao')
        for k, v in kv.items():
            if k == 'parcelas':
                escolher(pg, '#calcParcelas', v)
            else:
                pg.fill('#' + ids[k], str(v))
        pg.wait_for_timeout(120)

    def txt(pg, sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; }", sel)

    def visivel(pg, sel):
        return pg.evaluate("(s) => { const e = document.querySelector(s); return !!e && e.offsetParent !== null && getComputedStyle(e).visibility !== 'hidden'; }", sel)

    def cartoes(pg):
        return pg.evaluate("""() => Array.from(document.querySelectorAll('#calcOpcoes .calc-opcao')).map(e => ({
            id: e.dataset.id, ativa: e.classList.contains('ativa'), preco: e.querySelector('.calc-opcao-preco').textContent, margem: e.querySelector('.calc-opcao-margem').textContent,
            cor: e.querySelector('.calc-opcao-margem').className.replace('calc-opcao-margem', '').trim(), parcela: (e.querySelector('.calc-opcao-parcela') || {}).textContent || '' }))""")

    def formas(pg):
        return pg.evaluate("Array.from(document.querySelectorAll('#calcFormas .calc-linha')).map(e => [e.children[0].textContent, e.children[1].textContent, e.children[1].className])")

    def confere_opcoes(pg, esp, parcelas, rotulo, mostra_parcela=True):
        """As sugestoes da tela contra o oraculo: quais, o preco, a margem, o lucro, a cor e as parcelas."""
        vistos = cartoes(pg)
        ids = [c['id'] for c in vistos]
        ok(ids == [o['id'] for o in esp['ops']], '%s: as sugestoes que aparecem: %s (esperado %s)' % (rotulo, ids, [o['id'] for o in esp['ops']]))
        for c, o in zip(vistos, esp['ops']):
            r = o['r']
            bom = (c['preco'] == brl(r['preco']) and c['margem'] == 'margem ' + pct1(margem(r)) + 'lucro ' + brl(r['lucro']) and c['cor'] == o['cor'])
            if mostra_parcela and parcelas > 1:
                bom = bom and c['parcela'] == 'ou %dx de %s' % (parcelas, brl((r['preco'] / parcelas).quantize(CENT, rounding=ROUND_CEILING)))
            else:
                bom = bom and c['parcela'] == ''
            ok(bom, '%s: %s %s, %s, lucro %s, cor "%s"' % (rotulo, o['id'], c['preco'], pct1(margem(r)), brl(r['lucro']), c['cor']))

    def confere_resultado(pg, esp, id_, taxa_rot, custo_prod, imp, com, minima, desc, tabela, parcelas, rotulo, pix=(D(0), D(0)), mostra_formas=(1, 3, 6, 10, 12)):
        """A conta detalhada do preco escolhido, as formas de pagamento, a venda nossa, o minimo e a nota de Custos."""
        o = [x for x in esp['ops'] if x['id'] == id_][0]
        r = o['r']
        ok(txt(pg, '#calcPreco') == brl(r['preco']) and txt(pg, '#calcR1') == brl(esp['custo_total']), '%s: preco escolhido %s e custo total %s' % (rotulo, txt(pg, '#calcPreco'), txt(pg, '#calcR1')))
        ok(txt(pg, '#calcR2') == brl(r['taxa']) and txt(pg, '#calcR3') == brl(r['imposto']) and txt(pg, '#calcR5') == brl(r['comissao']) and txt(pg, '#calcR4') == brl(r['lucro']),
           '%s: taxa %s, imposto %s, comissao %s, lucro %s' % (rotulo, txt(pg, '#calcR2'), txt(pg, '#calcR3'), txt(pg, '#calcR5'), txt(pg, '#calcR4')))
        ok(txt(pg, '#calcR2rot') == taxa_rot and txt(pg, '#calcR3rot') == 'Imposto (%s)' % pctt(imp) and txt(pg, '#calcR5rot') == 'Comissão (%s)' % pctt(com) and txt(pg, '#calcR4rot') == 'Lucro (%s)' % pct1(margem(r)),
           '%s: os rotulos da conta: "%s" / "%s"' % (rotulo, txt(pg, '#calcR2rot'), txt(pg, '#calcR4rot')))
        if custo_prod:
            mk = (r['preco'] / D(custo_prod)).quantize(D('0.00001'), rounding=ROUND_HALF_UP)
            ok(txt(pg, '#calcMarkup') == str(mk).replace('.', ','), '%s: markup %s (preco / custo do produto)' % (rotulo, txt(pg, '#calcMarkup')))
        # as formas: o Pix com o desconto a vista, e as parcelas que o gateway tem
        esperadas = [('Pix, com o desconto de %s' % pctt(desc), margem(conta(q(r['preco'] * (1 - desc / 100)), esp['custo_total'], pix[0], pix[1], imp, com)))]
        for n in mostra_formas:
            tx, tar = tabela[n]
            esperadas.append(('%dx no cartão%s' % (n, ' (a escolhida)' if n == parcelas else ''), margem(conta(r['preco'], esp['custo_total'], tx, tar, imp, com))))
        vistas = [(f[0], f[1], f[2]) for f in formas(pg)]
        bom = len(vistas) == len(esperadas) and all(v[0] == e[0] and v[1] == pct1(e[1]) and (v[2] == 'baixa') == (e[1] < minima) for v, e in zip(vistas, esperadas))
        ok(bom, '%s: margem por forma de pagamento: %s' % (rotulo, [(v[0].split(',')[0], v[1]) for v in vistas]))
        # a venda nossa: o desconto da comissao soma com o do Pix, e nao ha comissao
        if com > 0:
            pd = q(r['preco'] * (1 - (com + desc) / 100))
            rd = conta(pd, esp['custo_total'], pix[0], pix[1], imp, 0)
            ok(visivel(pg, '#calcDiretaBloco') and txt(pg, '#calcDireta') == brl(pd) and ('Lucro de %s, margem de %s.' % (brl(rd['lucro']), pct1(margem(rd)))) in txt(pg, '#calcDiretaNota')
               and txt(pg, '#calcDiretaRot') == 'No Pix, com os dois descontos (%s)' % pctt(com + desc), '%s: venda nossa %s, lucro %s, margem %s' % (rotulo, txt(pg, '#calcDireta'), brl(rd['lucro']), pct1(margem(rd))))
        else:
            ok(not visivel(pg, '#calcDiretaBloco'), '%s: com comissao 0 o bloco "Venda nossa" fica escondido' % rotulo)
        ok(txt(pg, '#calcPiso') == (brl(esp['piso']) if esp['piso'] else '—') and txt(pg, '#calcPisoRot') == 'Preço mínimo, com a margem de %s' % pctt(minima), '%s: preco minimo %s' % (rotulo, txt(pg, '#calcPiso')))
        ok(('margem de %s,' % pct1((r['lucro'] + r['imposto']) / r['preco'] * 100)) in txt(pg, '#calcNaTela'), '%s: em Custos do E-commerce o pedido aparece com %s' % (rotulo, pct1((r['lucro'] + r['imposto']) / r['preco'] * 100)))

    TAB_LINK = {n + 1: (LINK[n], D(0)) for n in range(12)}
    EMB_SHOPE = D('5.40')   # Flex M 4,70 + Tag Desk Shope 0,40 + Fita 0,30

    # ================================================================ 1. os numeros da aprovacao
    if secao(1, 'Os numeros da aprovacao: produto 1, Desk Shope, custo 50,00, Flex M 4,70 + Tag 0,40 + Fita 0,30, margem 30, 3x, imposto 4, comissao 5'):
        pg = nova()
        editar(pg, loja='Desk Shope')
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 129,90 dá margem de 41,3%', 'a margem de hoje com R$ 129,90 no preco: "%s"' % txt(pg, '#calcHoje'))
        abrir(pg)
        ok(pg.input_value('#calcCusto') == '50,00' and pg.input_value('#calcEmbalagem') == '5,40' and txt(pg, '#calcCustoTotal') == 'R$ 55,40', 'custo 50,00 (da aba Custos), embalagem 5,40 e custo total 55,40')
        ok(txt(pg, '#calcEmbOrigem') == 'Caixa R$ 4,70 + Tag Desk Shope R$ 0,40 + Fita adesiva R$ 0,30' and txt(pg, '#calcCaixa .dropdown-select-label') == 'Caixa de Encomenda Flex M', 'a origem da embalagem e a caixa do produto: "%s"' % txt(pg, '#calcEmbOrigem'))
        ok(txt(pg, '#calcCustoOrigem') == 'O mesmo que Custos do E-commerce usa: custo da compra' and txt(pg, '#calcMinimaDica') == 'A mínima é 15%, de Parâmetros de Vendas', 'as dicas do custo e da margem minima')
        ok(pg.input_value('#calcMargem') == '30' and pg.input_value('#calcImposto') == '4' and pg.input_value('#calcComissao') == '5' and txt(pg, '#calcParcelas .dropdown-select-label') == '3x · taxa 7,01%', 'margem 30, imposto 4, comissao 5 e 3x com taxa 7,01%')
        v = {c['id']: c for c in cartoes(pg)}
        ok([c['id'] for c in cartoes(pg)] == ['varejo', 'barreira', 'redondo', 'exato'], 'as quatro sugestoes, na ordem')
        ok(v['varejo']['preco'] == 'R$ 102,90' and v['varejo']['margem'] == 'margem 30,1%lucro R$ 31,02' and v['varejo']['cor'] == '', 'Varejo R$ 102,90, 30,1%, lucro 31,02')
        ok(v['barreira']['preco'] == 'R$ 99,90' and v['barreira']['margem'] == 'margem 28,5%lucro R$ 28,50' and v['barreira']['cor'] == 'abaixo', 'Abaixo da faixa R$ 99,90, 28,5%, lucro 28,50, laranja')
        ok(v['redondo']['preco'] == 'R$ 110,00' and v['redondo']['margem'] == 'margem 33,6%lucro R$ 36,99', 'Redondo R$ 110,00, 33,6%, lucro 36,99')
        ok(v['exato']['preco'] == 'R$ 102,62' and v['exato']['margem'] == 'margem 30,0%lucro R$ 30,80', 'Exato R$ 102,62, 30,0%, lucro 30,80 (sobe ao centavo)')
        ok(v['varejo']['ativa'] and txt(pg, '#calcPreco') == 'R$ 102,90' and txt(pg, '#calcPrecoRot') == 'Preço escolhido: Varejo ,90', 'o Varejo abre escolhido')
        ok([txt(pg, i) for i in ('#calcR2', '#calcR3', '#calcR5', '#calcR4')] == ['R$ 7,21', 'R$ 4,12', 'R$ 5,15', 'R$ 31,02'] and txt(pg, '#calcMarkup') == '2,05800', 'no Varejo: taxa 7,21, imposto 4,12, comissao 5,15, lucro 31,02 e markup 2,05800')
        ok([(f[0].split(',')[0].split(' no ')[0], f[1]) for f in formas(pg)] == [('Pix', '35,4%'), ('1x', '33,0%'), ('3x', '30,1%'), ('6x', '27,5%'), ('10x', '22,1%'), ('12x', '20,5%')], 'as formas: Pix 35,4%%, 1x 33,0%%, 3x 30,1%%, 6x 27,5%%, 10x 22,1%%, 12x 20,5%%: %s' % [f[1] for f in formas(pg)])
        ok(txt(pg, '#calcPiso') == 'R$ 80,31' and 'margem de 34,1%' in txt(pg, '#calcNaTela'), 'preco minimo 80,31 e, em Custos do E-commerce, 34,1%')
        ok(txt(pg, '#calcDireta') == 'R$ 94,51' and 'Lucro de R$ 35,33, margem de 37,4%.' in txt(pg, '#calcDiretaNota') and 'No Pix, com os dois descontos (8,15%)' == txt(pg, '#calcDiretaRot'), 'venda nossa no Pix (8,15%): R$ 94,51, lucro 35,33, margem 37,4%')
        ok(txt(pg, '#calcParcelasDica') == 'Taxa do gateway da loja, a mesma de Custos do E-commerce' and not visivel(pg, '#calcAvisoCusto') and not visivel(pg, '#calcErro'), 'a dica da taxa e nenhum aviso')
        pg.click('.calc-opcao[data-id="redondo"]'); pg.wait_for_timeout(100)
        ok(txt(pg, '#calcPreco') == 'R$ 110,00' and txt(pg, '#calcMarkup') == '2,20000' and txt(pg, '#calcPrecoRot') == 'Preço escolhido: Redondo', 'escolher o Redondo muda o preco escolhido e o markup (2,20000)')
        pg.context.close()

    # ================================================================ 2. a conta contra o oraculo
    if secao(2, 'A conta contra o oraculo em Decimal: custo, margem, parcelas, imposto, comissao e frete'):
        pg = nova()
        editar(pg, loja='Desk Shope')
        abrir(pg)
        cenarios = [
            dict(custo='50,00', margem='30', imposto='4', comissao='5', parcelas=3, frete='0,00', freteloja='0,00'),
            dict(custo='20,00', margem='20', imposto='4', comissao='5', parcelas=1, frete='0,00', freteloja='0,00'),
            dict(custo='120,00', margem='50', imposto='6', comissao='8', parcelas=12, frete='3,50', freteloja='7,25'),
            dict(custo='1.234,56', margem='25,5', imposto='4', comissao='0', parcelas=6, frete='12,00', freteloja='0,00'),
            dict(custo='79,90', margem='35', imposto='0', comissao='10', parcelas=10, frete='0,00', freteloja='15,00'),
            dict(custo='9,99', margem='40', imposto='4', comissao='5', parcelas=2, frete='0,00', freteloja='0,00'),
            dict(custo='350,00', margem='30', imposto='4', comissao='5', parcelas=3, frete='20,00', freteloja='0,00'),
            dict(custo='18,50', margem='30', imposto='4', comissao='5', parcelas=4, frete='0,00', freteloja='0,00'),
        ]
        for k, c in enumerate(cenarios):
            preencher(pg, custo=c['custo'], frete=c['frete'], freteloja=c['freteloja'], margem=c['margem'], imposto=c['imposto'], comissao=c['comissao'], parcelas=c['parcelas'])
            n = lambda s: D(s.replace('.', '').replace(',', '.'))
            custo_prod = n(c['custo'])
            total_custo = custo_prod + n(c['frete']) + EMB_SHOPE + n(c['freteloja'])
            taxa = LINK[c['parcelas'] - 1]
            esp = oraculo(total_custo, n(c['margem']), taxa, 0, n(c['imposto']), n(c['comissao']))
            rot = 'cenario %d (custo %s, margem %s, %dx, imposto %s, comissao %s)' % (k + 1, c['custo'], c['margem'], c['parcelas'], c['imposto'], c['comissao'])
            confere_opcoes(pg, esp, c['parcelas'], rot)
            confere_resultado(pg, esp, 'varejo', 'Taxa do cartão %dx (%s)' % (c['parcelas'], pctt(taxa)), custo_prod, n(c['imposto']), n(c['comissao']), D(15), D('3.15'), TAB_LINK, c['parcelas'], rot)
        pg.context.close()

    # ================================================================ 3. as bordas
    if secao(3, 'As bordas: Varejo na beira da faixa, custo baixo, margem abaixo da minima, margem que nao fecha, comissao 0'):
        pg = nova()
        editar(pg, loja='Desk Shope')
        abrir(pg)
        preencher(pg, custo='48,32')
        ids = [c['id'] for c in cartoes(pg)]
        ok(ids == ['varejo', 'redondo', 'exato'] and cartoes(pg)[0]['preco'] == 'R$ 99,90' and txt(pg, '#calcCustoTotal') == 'R$ 53,72', 'custo 48,32 (total 53,72): sem "Abaixo da faixa" e Varejo R$ 99,90: %s %s' % (ids, cartoes(pg)[0]['preco']))
        preencher(pg, custo='3,00')
        ids = [c['id'] for c in cartoes(pg)]
        ok('barreira' not in ids and cartoes(pg)[0]['preco'] == 'R$ 15,90', 'custo 3,00: sem "Abaixo da faixa" (cairia abaixo da margem minima) e Varejo R$ 15,90: %s %s' % (ids, cartoes(pg)[0]['preco']))
        preencher(pg, custo='50,00', margem='10')
        ok(all(c['cor'] == 'minima' for c in cartoes(pg)) and 'barreira' not in [c['id'] for c in cartoes(pg)], 'margem 10: todos em vermelho (abaixo da minima de 15%%) e sem "Abaixo da faixa": %s' % [(c['id'], c['cor']) for c in cartoes(pg)])
        ok(all(f[2] == 'baixa' for f in formas(pg)[1:] if float(f[1].replace('%', '').replace(',', '.')) < 15), 'as formas abaixo da minima ficam em vermelho')
        preencher(pg, margem='90')
        ok(visivel(pg, '#calcErro') and not visivel(pg, '#calcOpcoes') and not visivel(pg, '#calcResultado') and pg.is_disabled('#calcAplicar'), 'margem 90: a conta nao fecha, avisa e some o resultado (e o Aplicar trava)')
        ok('somam 100% ou mais' in txt(pg, '#calcErro'), 'o aviso diz o motivo: "%s"' % txt(pg, '#calcErro'))
        preencher(pg, margem='30', comissao='0')
        ok(not visivel(pg, '#calcDiretaBloco') and visivel(pg, '#calcResultado'), 'comissao 0 esconde o bloco "Venda nossa, sem comissao"')
        preencher(pg, comissao='5')
        ok(visivel(pg, '#calcDiretaBloco') and not pg.is_disabled('#calcAplicar'), 'comissao de volta: o bloco volta e o Aplicar destrava')
        # nao conta valor negativo nem texto: vira zero
        preencher(pg, custo='abc')
        ok(visivel(pg, '#calcAvisoCusto'), 'custo que nao e numero e o mesmo que sem custo')
        pg.context.close()

    # ================================================================ 4. os parametros mudando o que entra
    if secao(4, 'Os parametros de Vendas mudam o que a calculadora usa de inicio, e a parcela fica no que o gateway tem'):
        pg = nova()
        ir(pg, PROD)
        param_set(pg, impostoPadraoPct=6, margemMinimaPct=20, comissaoPadraoPct=8, parcelasVitrine=6)
        editar(pg, loja='Desk Shope')
        abrir(pg)
        ok(pg.input_value('#calcImposto') == '6' and pg.input_value('#calcComissao') == '8' and txt(pg, '#calcParcelas .dropdown-select-label') == '6x · taxa 9,67%', 'imposto 6, comissao 8 e 6x vem dos parametros: %s / %s / %s' % (pg.input_value('#calcImposto'), pg.input_value('#calcComissao'), txt(pg, '#calcParcelas .dropdown-select-label')))
        ok(txt(pg, '#calcMinimaDica') == 'A mínima é 20%, de Parâmetros de Vendas' and txt(pg, '#calcPisoRot') == 'Preço mínimo, com a margem de 20%', 'a margem minima de 20% muda a dica e o rotulo do preco minimo')
        esp = oraculo(EMB_SHOPE + 50, 30, LINK[5], 0, 6, 8, minima=20)
        confere_opcoes(pg, esp, 6, 'com os parametros (imposto 6, comissao 8, 6x, minima 20)')
        confere_resultado(pg, esp, 'varejo', 'Taxa do cartão 6x (9,67%)', 50, D(6), D(8), D(20), D('3.15'), TAB_LINK, 6, 'com os parametros')
        fechar(pg)
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 129,90 dá margem de %s' % pct1(margem(conta(D('129.90'), EMB_SHOPE + 50, LINK[5], 0, 6, 8))), 'a margem de hoje acompanha os parametros: "%s"' % txt(pg, '#calcHoje'))
        # parametro estragado cai no de fabrica
        param_set(pg, impostoPadraoPct='abc', comissaoPadraoPct=-3, parcelasVitrine=2.5, margemMinimaPct=150)
        pg.reload(); pg.wait_for_timeout(450); trocar_loja(pg, 'Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcImposto') == '4' and pg.input_value('#calcComissao') == '5' and txt(pg, '#calcParcelas .dropdown-select-label').startswith('3x') and txt(pg, '#calcMinimaDica').startswith('A mínima é 15%'), 'parametro estragado (texto, negativo, fracionado, acima de 100) volta ao de fabrica: 4, 5, 3x, 15%')
        # a parcela de vitrine acima do que o gateway tem: vale a maior que ele tem
        pg.context.close()
        pg = nova()
        ir(pg, PROD)
        g = ls(pg, 'deskGateways')
        for gw in g['gateways']:
            if gw['tipo'] == 'infinitepay':
                gw['condicoes'] = [c for c in gw['condicoes'] if not (c['forma'] == 'credito' and c['parcelas'] > 6)]
        ls_set(pg, 'deskGateways', g)
        param_set(pg, parcelasVitrine=10)
        editar(pg, loja='Desk Shope')
        abrir(pg)
        itens = pg.evaluate("Array.from(document.querySelectorAll('#calcParcelasMenu .dropdown-select-item')).map(e => e.textContent)")
        ok(len(itens) == 6 and itens[-1].startswith('6x') and txt(pg, '#calcParcelas .dropdown-select-label').startswith('6x'), 'gateway so ate 6x e vitrine em 10: a lista tem 6 itens e abre em 6x: %s' % txt(pg, '#calcParcelas .dropdown-select-label'))
        ok([f[0].split(' no ')[0].split(',')[0] for f in formas(pg)] == ['Pix', '1x', '3x', '6x'], 'e as formas de pagamento so listam as que o gateway tem: %s' % [f[0].split(',')[0] for f in formas(pg)])
        pg.context.close()

    # ================================================================ 5. Parametros de Vendas
    if secao(5, 'Parametros de Vendas: a comissao padrao e as parcelas da vitrine'):
        pg = nova()
        ir(pg, PARAM_V)
        corpo = pg.inner_text('.main')
        ok(pg.input_value('#comissaoPadrao') == '5,00' and pg.input_value('#parcelasVitrine') == '3', 'de fabrica: comissao 5,00 e parcelas 3: %s / %s' % (pg.input_value('#comissaoPadrao'), pg.input_value('#parcelasVitrine')))
        ok('Comissão padrão na calculadora' in corpo and 'Parcelas sem juros na vitrine' in corpo and corpo.count('calculadora de preços do produto') >= 2, 'os dois campos e a dica de cada um, dizendo que a calculadora de preco usa de inicio')

        def salvar():
            pg.click('#btnSalvarParam'); pg.wait_for_timeout(250)
            pg.evaluate("document.getElementById('btnAvisoOk').click()"); pg.wait_for_timeout(100)

        def param():
            return ls(pg, 'deskParametros') or {}
        pg.fill('#comissaoPadrao', '7,5'); pg.fill('#parcelasVitrine', '6')
        ok('2 parâmetros alterados' in pg.inner_text('#notaBarra'), 'digitar conta as alteracoes: %s' % pg.inner_text('#notaBarra'))
        salvar()
        ok(param().get('comissaoPadraoPct') == 7.5 and param().get('parcelasVitrine') == 6, 'Salvar grava comissaoPadraoPct 7,5 e parcelasVitrine 6: %s' % {k: param().get(k) for k in ('comissaoPadraoPct', 'parcelasVitrine')})
        ir(pg, PARAM_V)
        ok(pg.input_value('#comissaoPadrao') == '7,50' and pg.input_value('#parcelasVitrine') == '6', 'ao reabrir mostra o gravado: %s / %s' % (pg.input_value('#comissaoPadrao'), pg.input_value('#parcelasVitrine')))
        log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === 'parametrosVendas')")
        ok(len(log) == 1 and all(x in log[0]['detalhe'] for x in ('Imposto padrão 4,00%', 'margem mínima 15,00%', 'comissão padrão na calculadora 7,50%', 'parcelas na vitrine 6x')), 'o registro cita os quatro: "%s"' % (log[0]['detalhe'] if log else None))
        ruins_c = ['', 'abc', '-1', '100,01', '101', '5,555', '1e1', '5,']
        ruins_p = ['', 'abc', '0', '13', '-1', '1,5', '2.5', '99', '100', '1e1', ' ']
        falhou = []
        for v in ruins_c:
            pg.fill('#comissaoPadrao', v); pg.click('#btnSalvarParam'); pg.wait_for_timeout(200)
            pg.evaluate("document.getElementById('btnAvisoOk').click()"); pg.wait_for_timeout(80)
            if not (pg.evaluate("document.getElementById('campoComissao').classList.contains('has-error')") and param().get('comissaoPadraoPct') == 7.5):
                falhou.append('comissao ' + repr(v))
        pg.fill('#comissaoPadrao', '7,5')
        for v in ruins_p:
            pg.fill('#parcelasVitrine', v); pg.click('#btnSalvarParam'); pg.wait_for_timeout(200)
            pg.evaluate("document.getElementById('btnAvisoOk').click()"); pg.wait_for_timeout(80)
            if not (pg.evaluate("document.getElementById('campoParcelas').classList.contains('has-error')") and param().get('parcelasVitrine') == 6):
                falhou.append('parcelas ' + repr(v))
        ok(not falhou, 'valor invalido avisa, destaca o campo e nao grava (comissao e parcelas): %s' % falhou)
        pg.fill('#parcelasVitrine', '6')
        gravados = []
        for vc, vp, ec, ep in (('0', '1', 0, 1), ('100', '12', 100, 12), ('0,01', '3', 0.01, 3), ('7.25', '9', 7.25, 9)):
            pg.fill('#comissaoPadrao', vc); pg.fill('#parcelasVitrine', vp); salvar(); pp = param(); gravados.append((vc, pp.get('comissaoPadraoPct'), vp, pp.get('parcelasVitrine')))
            if not (pp.get('comissaoPadraoPct') == ec and pp.get('parcelasVitrine') == ep):
                falhou.append(vc + '/' + vp)
        ok(not falhou, 'os limites 0 e 100, 1 e 12 sao aceitos e gravados: %s' % gravados)
        pg.fill('#comissaoPadrao', '1'); pg.fill('#parcelasVitrine', '2'); pg.click('#btnRestaurarParam'); pg.wait_for_timeout(200); pg.evaluate("document.getElementById('btnAvisoOk').click()")
        ok(pg.input_value('#comissaoPadrao') == '5,00' and pg.input_value('#parcelasVitrine') == '3' and param().get('parcelasVitrine') == 9, 'Restaurar padrao poe 5,00 e 3 na tela, e so vale quando salvar')
        # o imposto e a margem minima seguem do jeito que estavam
        ok(pg.input_value('#impostoPadrao') == '4,00' and pg.input_value('#margemMinima') == '15,00', 'o imposto e a margem minima nao mudaram')
        pg.context.close()

    # ================================================================ 6. o gateway
    if secao(6, 'O gateway: taxa mudada, tarifa, Desk Brands, Desk Tech, sem loja escolhida, trocar a loja e reabrir'):
        pg = nova()
        ir(pg, PROD)
        g = ls(pg, 'deskGateways')
        tab = dict(TAB_LINK)
        for gw in g['gateways']:
            if gw['tipo'] == 'infinitepay':
                for c in gw['condicoes']:
                    if c['forma'] == 'credito' and c['parcelas'] == 3:
                        c['taxa'] = 9.99
                        c['tarifa'] = 0.5
        tab[3] = (D('9.99'), D('0.50'))
        ls_set(pg, 'deskGateways', g)
        editar(pg, loja='Desk Shope')
        abrir(pg)
        ok(txt(pg, '#calcParcelas .dropdown-select-label') == '3x · taxa 9,99% + R$ 0,50', 'a lista de parcelas mostra a taxa e a tarifa do gateway: "%s"' % txt(pg, '#calcParcelas .dropdown-select-label'))
        esp = oraculo(EMB_SHOPE + 50, 30, D('9.99'), D('0.50'), 4, 5)
        confere_opcoes(pg, esp, 3, 'taxa 9,99% + tarifa 0,50 em 3x')
        confere_resultado(pg, esp, 'varejo', 'Taxa do cartão 3x (9,99% + R$ 0,50)', 50, D(4), D(5), D(15), D('3.15'), tab, 3, 'taxa 9,99% + tarifa 0,50 em 3x')
        ok(esp['ops'][0]['r']['taxa'] == q(esp['ops'][0]['r']['preco'] * D('9.99') / 100) + D('0.50'), 'no oraculo a tarifa em R$ soma na taxa do preco (e o lucro a desconta)')
        # a tarifa muda o Exato: sem ela daria outro preco
        sem_tarifa = exato_de(EMB_SHOPE + 50, D(0), 30, D('9.99'), D(4), D(5))
        ok(esp['ex'] > sem_tarifa and txt(pg, '.calc-opcao[data-id="exato"] .calc-opcao-preco') == brl(esp['ex']), 'o Exato conta a tarifa: %s (sem ela seria %s)' % (brl(esp['ex']), brl(sem_tarifa)))
        # trocar a loja e reabrir: tudo acompanha
        fechar(pg)
        trocar_loja(pg, 'Desk Brands')
        abrir(pg)
        ok(pg.input_value('#calcEmbalagem') == '5,60' and txt(pg, '#calcEmbOrigem') == 'Caixa R$ 4,70 + Tag Desk Brands R$ 0,60 + Fita adesiva R$ 0,30', 'Desk Brands: a Tag Brands entra no lugar da Tag Shope (5,60): "%s"' % txt(pg, '#calcEmbOrigem'))
        esp = oraculo(D('5.60') + 50, 30, D('9.99'), D('0.50'), 4, 5)
        confere_opcoes(pg, esp, 3, 'Desk Brands')
        fechar(pg)
        # Desk Tech: sem gateway da loja virtual
        trocar_loja(pg, 'Desk Tech')
        abrir(pg)
        ok(pg.is_disabled('#calcParcelas .dropdown-select-btn') and txt(pg, '#calcParcelasDica') == 'Esta loja não tem gateway da loja virtual habilitado: a conta sai sem taxa.', 'Desk Tech: o dropdown de parcelas fica desabilitado e a dica diz o motivo: "%s"' % txt(pg, '#calcParcelasDica'))
        ok(pg.input_value('#calcEmbalagem') == '5,00' and txt(pg, '#calcEmbOrigem') == 'Caixa R$ 4,70 + Fita adesiva R$ 0,30', 'Desk Tech: so a fita entra sozinha (5,00): "%s"' % txt(pg, '#calcEmbOrigem'))
        esp = oraculo(D('5.00') + 50, 30, D(0), D(0), 4, 5)
        confere_opcoes(pg, esp, 1, 'Desk Tech, sem gateway', mostra_parcela=False)
        ok(txt(pg, '#calcR2') == brl(0) and txt(pg, '#calcR2rot') == 'Taxa do cartão (loja sem gateway)' and [f[0].split(',')[0] for f in formas(pg)] == ['Pix'], 'Desk Tech: taxa 0, e das formas so o Pix: %s' % [f[0] for f in formas(pg)])
        fechar(pg)
        trocar_loja(pg, 'Desk Shope')
        abrir(pg)
        ok(not pg.is_disabled('#calcParcelas .dropdown-select-btn') and pg.input_value('#calcEmbalagem') == '5,40', 'voltando para a Desk Shope reabre com gateway e a embalagem dela')
        pg.context.close()
        # sem loja escolhida: a conta usa a Desk Shope e a dica avisa
        pg = nova()
        ir(pg, PROD, '?editar=1')
        pg.click('.tab-item[data-tab="precos"]'); abrir(pg)
        ok(txt(pg, '#calcParcelasDica') == 'Sem loja escolhida: a conta usa a Desk Shope. Escolha a Loja Desk em Dados Complementares.' and pg.input_value('#calcEmbalagem') == '5,40', 'sem loja escolhida: a conta usa a Desk Shope e a dica manda escolher a Loja Desk em Dados Complementares')
        confere_opcoes(pg, oraculo(EMB_SHOPE + 50, 30, LINK[2], 0, 4, 5), 3, 'sem loja escolhida')
        pg.context.close()

    # ================================================================ 7. o cadastro de Embalagens
    if secao(7, 'O campo Embalagem do produto, o cadastro de Embalagens mudando o custo, "customizada" e a embalagem digitada a mao'):
        pg = nova()
        ir(pg, PROD, '?editar=1')
        itens = pg.evaluate("Array.from(document.querySelectorAll('#inputEmbalagem .dropdown-select-item')).map(e => e.textContent)")
        esperado_itens = ['Embalagem customizada', 'Caixa de Encomenda Flex P', 'Caixa de Encomenda Flex M', 'Caixa de Encomenda Flex G', 'Caixa de Encomenda CE-01', 'Caixa de Encomenda CE-02', 'Caixa para Eletrônicos',
                          'Envelope de Segurança Pequeno', 'Envelope de Segurança Grande', 'Rolo para Pôster']
        ok(itens == esperado_itens, 'o campo lista "Embalagem customizada" e as embalagens ativas que nao sao insumo (sem o rolo inativo, sem tag, fita e saco): %s' % itens)
        ok(txt(pg, '#inputEmbalagem .dropdown-select-label') == 'Caixa de Encomenda Flex M' and pg.get_attribute('#inputEmbalagem', 'data-value') == '2', 'o produto 1 vem com a Caixa de Encomenda Flex M (valor = o id do cadastro)')
        ok('Lista virá do futuro cadastro' not in pg.content() and 'hoje é mock' not in pg.content(), 'a dica "hoje e mock" saiu')
        ir(pg, PROD, '?editar=1&id=2')
        ok(txt(pg, '#inputEmbalagem .dropdown-select-label') == 'Embalagem customizada', 'os outros produtos ficam em "customizada"')
        # em leitura o campo mostra o texto
        ir(pg, PROD)
        ok(pg.evaluate("document.querySelector('#inputEmbalagem').closest('.form-field').querySelector('.campo-leitura').textContent") == 'Caixa de Encomenda Flex M', 'em modo leitura o campo mostra a caixa como texto')
        pg.context.close()
        # o cadastro de Embalagens muda o custo da calculadora
        pg = nova()
        ir(pg, PROD)
        lista = pg.evaluate("embalagensLer()")
        for e in lista:
            if e['nome'] == 'Caixa de Encomenda Flex M':
                e['custo'] = 6.0
            if e['nome'] == 'Fita adesiva':
                e['custo'] = 0.55
        ls_set(pg, 'deskEmbalagens', lista)
        editar(pg, loja='Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcEmbalagem') == '6,95' and txt(pg, '#calcEmbOrigem') == 'Caixa R$ 6,00 + Tag Desk Shope R$ 0,40 + Fita adesiva R$ 0,55', 'mudar o custo no cadastro de Embalagens muda a embalagem completa: "%s"' % txt(pg, '#calcEmbOrigem'))
        confere_opcoes(pg, oraculo(D('6.95') + 50, 30, LINK[2], 0, 4, 5), 3, 'com a embalagem a 6,95')
        # trocar a caixa recalcula; a digitada a mao vale ate trocar
        escolher(pg, '#calcCaixa', '1')
        ok(pg.input_value('#calcEmbalagem') == '4,45' and txt(pg, '#calcCaixa .dropdown-select-label') == 'Caixa de Encomenda Flex P', 'trocar a caixa refaz a embalagem completa (Flex P 3,50 + Tag 0,40 + Fita 0,55 = 4,45): %s' % pg.input_value('#calcEmbalagem'))
        preencher(pg, emb='7,00')
        ok(txt(pg, '#calcCustoTotal') == brl(50 + D('7.00')) and 'digitado' in txt(pg, '#calcEmbOrigem'), 'a embalagem digitada a mao vale: custo total 57,00 e a origem diz "digitado"')
        preencher(pg, margem='35')
        ok(pg.input_value('#calcEmbalagem') == '7,00', 'e continua valendo ao mexer em outros campos')
        escolher(pg, '#calcCaixa', '3')
        ok(pg.input_value('#calcEmbalagem') == '6,85' and 'digitado' not in txt(pg, '#calcEmbOrigem'), 'trocar a caixa descarta o digitado e refaz a conta do cadastro (Flex G 5,90 + 0,40 + 0,55 = 6,85): %s' % pg.input_value('#calcEmbalagem'))
        fechar(pg)
        # "customizada": a calculadora usa a sugestao para 1 peca (a menor caixa em que cabe)
        pg.click('.tab-item[data-tab="gerais"]'); escolher(pg, '#inputEmbalagem', 'customizada'); pg.click('.tab-item[data-tab="precos"]')
        abrir(pg)
        ok(txt(pg, '#calcCaixa .dropdown-select-label') == 'Envelope de Segurança Pequeno' and pg.input_value('#calcEmbalagem') == '2,05', 'embalagem "customizada": usa a sugerida para 1 peca, o Envelope Pequeno (1,10 + Tag 0,40 + Fita 0,55 = 2,05): %s' % pg.input_value('#calcEmbalagem'))
        pg.context.close()

    # ================================================================ 8. o custo
    if secao(8, 'O custo do produto: custo medio, lido de novo a cada abertura, e produto sem custo'):
        pg = nova()
        ir(pg, PROD)
        param_set(pg, custosEcommerce={'situacoes': ['aberto'], 'custoBase': 'medio'})
        editar(pg, loja='Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcCusto') == '48,00' and txt(pg, '#calcCustoOrigem') == 'O mesmo que Custos do E-commerce usa: custo médio', 'com o custo base "medio" a calculadora usa o custo medio (48,00) e diz isso: "%s"' % txt(pg, '#calcCustoOrigem'))
        confere_opcoes(pg, oraculo(EMB_SHOPE + 48, 30, LINK[2], 0, 4, 5), 3, 'custo medio 48,00')
        fechar(pg)
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 129,90 dá margem de %s' % pct1(margem(conta(D('129.90'), EMB_SHOPE + 48, LINK[2], 0, 4, 5))), 'a margem de hoje tambem usa o custo medio: "%s"' % txt(pg, '#calcHoje'))
        pg.context.close()
        # o custo e lido de novo: o que esta na aba Custos agora vale a cada abertura
        pg = nova()
        editar(pg, loja='Desk Shope')
        pg.click('.tab-item[data-tab="custos"]')
        pg.fill('#tabelaCustos tr:last-child td:nth-child(5) input', '60,00')
        pg.click('.tab-item[data-tab="precos"]'); abrir(pg)
        ok(pg.input_value('#calcCusto') == '60,00', 'o preco de custo digitado na aba Custos vale na abertura seguinte: %s' % pg.input_value('#calcCusto'))
        fechar(pg)
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 129,90 dá margem de %s' % pct1(margem(conta(D('129.90'), EMB_SHOPE + 60, LINK[2], 0, 4, 5))), 'e a margem de hoje acompanha: "%s"' % txt(pg, '#calcHoje'))
        pg.click('.tab-item[data-tab="custos"]')
        pg.fill('#tabelaCustos tr:last-child td:nth-child(5) input', '0,00')
        pg.click('.tab-item[data-tab="precos"]')
        ok(txt(pg, '#calcHoje') == '', 'sem custo (0,00) nao ha linha de margem de hoje')
        abrir(pg)
        ok(pg.input_value('#calcCusto') == '' and visivel(pg, '#calcAvisoCusto') and txt(pg, '#calcAvisoCusto') == 'Informe o custo do produto para ver os preços' and not visivel(pg, '#calcOpcoes') and not visivel(pg, '#calcResultado') and pg.is_disabled('#calcAplicar'),
           'sem custo: o campo fica vazio, o aviso toma o lugar das sugestoes e do resultado, e o Aplicar trava')
        preencher(pg, custo='50,00')
        ok(not visivel(pg, '#calcAvisoCusto') and visivel(pg, '#calcOpcoes') and not pg.is_disabled('#calcAplicar'), 'digitando o custo na propria calculadora as sugestoes aparecem')
        confere_opcoes(pg, oraculo(EMB_SHOPE + 50, 30, LINK[2], 0, 4, 5), 3, 'custo digitado na calculadora')
        pg.context.close()
        # um produto da lista que nao tem custo cadastrado
        pg = nova()
        editar(pg, q_='&id=3', loja='Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcCusto') == '' and visivel(pg, '#calcAvisoCusto') and txt(pg, '#calcHoje') == '', 'o produto 3 (sem custo no cadastro): campo vazio, aviso e nenhuma margem de hoje')
        pg.context.close()

    # ================================================================ 9. Aplicar
    if secao(9, 'Aplicar: os tres campos, o calculo guardado, o registro de atividades, o reload e o salvo com prioridade'):
        pg = nova()
        ir(pg, PROD)
        param_set(pg, aoSalvar='ficar')
        editar(pg, loja='Desk Shope'); abrir(pg)
        ok(ls(pg, 'deskCalculoPreco') is None, 'so abrir e mexer na calculadora nao grava nada')
        pg.click('#calcAplicar'); pg.wait_for_timeout(350)
        ok(pg.input_value('#inputPrecoVenda') == '102,90' and pg.input_value('#inputPrecoListaPadrao') == '102,90' and pg.input_value('#inputMarkup') == '2,05800', 'Aplicar preenche o Preco de venda, a lista Padrao e o Markup: %s / %s / %s' % (pg.input_value('#inputPrecoVenda'), pg.input_value('#inputPrecoListaPadrao'), pg.input_value('#inputMarkup')))
        ok(not pg.evaluate("document.getElementById('calcDrawer').classList.contains('open')"), 'e fecha a gaveta')
        sv = (ls(pg, 'deskCalculoPreco') or {}).get('1')
        ok(sv and sv['preco'] == 102.9 and sv['markup'] == 2.058 and sv['margem'] == 30 and sv['parcelas'] == 3 and sv['imposto'] == 4 and sv['comissao'] == 5 and sv['frete'] == 0 and sv['freteLoja'] == 0 and sv['escolhida'] == 'varejo' and sv['caixaId'] == 2 and sv['embalagemManual'] is None and sv['em'],
           'o calculo fica guardado por id do produto: %s' % sv)
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 102,90 dá margem de 30,1%', 'a margem de hoje passa a ser a do preco aplicado: "%s"' % txt(pg, '#calcHoje'))
        log = pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === 'calculadoraPreco')")
        ok(len(log) == 1 and log[0]['acao'] == 'Aplicar o preço calculado' and log[0]['modulo'] == 'Cadastros' and log[0]['senha'] is False and log[0]['onde'] == 'Cadastros → Produtos', 'cai no Registro de atividades (grupo Cadastros, sem senha): %s' % (log[0] if log else None))
        ok(log and log[0]['detalhe'] == 'Fone de Ouvido Bluetooth X200: preço de R$ 129,90 para R$ 102,90, margem de 30,1%.' and len(log[0]['detalhe']) <= 180, 'o texto diz produto, preco anterior, preco novo e margem (ate 180): "%s"' % (log[0]['detalhe'] if log else None))
        ok(txt(pg, '#inputEmbalagem .dropdown-select-label') == 'Caixa de Encomenda Flex M', 'Aplicar devolve a caixa escolhida ao campo Embalagem')
        ir(pg, REGISTRO)
        ok('Aplicar o preço calculado' in pg.evaluate("document.body.textContent"), 'o Registro de atividades mostra a acao pelo nome')
        # reload: repoe preco, Padrao e Markup; a calculadora abre com os numeros guardados
        editar(pg, loja='Desk Shope')
        ok(pg.input_value('#inputPrecoVenda') == '102,90' and pg.input_value('#inputPrecoListaPadrao') == '102,90' and pg.input_value('#inputMarkup') == '2,05800', 'recarregar repoe o preco, a lista Padrao e o Markup: %s / %s / %s' % (pg.input_value('#inputPrecoVenda'), pg.input_value('#inputPrecoListaPadrao'), pg.input_value('#inputMarkup')))
        ok(txt(pg, '#calcHoje') == 'Com o custo de hoje, R$ 102,90 dá margem de 30,1%', 'e a margem de hoje com o preco guardado: "%s"' % txt(pg, '#calcHoje'))
        pg.context.close()

        # um calculo bem diferente, guardado, e depois os parametros e o cadastro mudam
        pg = nova()
        ir(pg, PROD)
        param_set(pg, aoSalvar='ficar')
        editar(pg, loja='Desk Shope'); abrir(pg)
        preencher(pg, frete='1,00', freteloja='2,00', margem='40', imposto='6', comissao='7', parcelas=6)
        pg.click('.calc-opcao[data-id="redondo"]'); pg.wait_for_timeout(100)
        total_custo = D(50) + 1 + EMB_SHOPE + 2
        esp = oraculo(total_custo, 40, LINK[5], 0, 6, 7)
        red = [o for o in esp['ops'] if o['id'] == 'redondo'][0]['r']['preco']
        pg.click('#calcAplicar'); pg.wait_for_timeout(350)
        ok(pg.input_value('#inputPrecoVenda') == campo(red) and pg.input_value('#inputMarkup') == str((red / 50).quantize(D('0.00001'), rounding=ROUND_HALF_UP)).replace('.', ','), 'o Redondo aplicado: preco %s e markup %s' % (pg.input_value('#inputPrecoVenda'), pg.input_value('#inputMarkup')))
        sv = (ls(pg, 'deskCalculoPreco') or {})['1']
        ok(sv['margem'] == 40 and sv['parcelas'] == 6 and sv['imposto'] == 6 and sv['comissao'] == 7 and sv['frete'] == 1 and sv['freteLoja'] == 2 and sv['escolhida'] == 'redondo' and sv['preco'] == float(red), 'guardou margem 40, 6x, imposto 6, comissao 7, frete 1, frete da loja 2 e o Redondo: %s' % sv)
        # os parametros e o cadastro mudam depois
        param_set(pg, impostoPadraoPct=9, comissaoPadraoPct=1, parcelasVitrine=2)
        lista = pg.evaluate("embalagensLer()")
        for e in lista:
            if e['nome'] == 'Caixa de Encomenda Flex M':
                e['custo'] = 5.0
        ls_set(pg, 'deskEmbalagens', lista)
        editar(pg, loja='Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcMargem') == '40' and pg.input_value('#calcImposto') == '6' and pg.input_value('#calcComissao') == '7' and txt(pg, '#calcParcelas .dropdown-select-label').startswith('6x') and pg.input_value('#calcFrete') == '1,00' and pg.input_value('#calcFreteLoja') == '2,00',
           'o salvo tem prioridade sobre os parametros (margem 40, imposto 6, comissao 7, 6x, fretes): %s' % [pg.input_value('#calcMargem'), pg.input_value('#calcImposto'), pg.input_value('#calcComissao')])
        ok(pg.input_value('#calcEmbalagem') == '5,70' and pg.input_value('#calcCusto') == '50,00', 'mas a embalagem e lida de novo, com o custo de hoje do cadastro (5,00 + 0,40 + 0,30 = 5,70): %s' % pg.input_value('#calcEmbalagem'))
        esp = oraculo(D(50) + 1 + D('5.70') + 2, 40, LINK[5], 0, 6, 7)
        confere_opcoes(pg, esp, 6, 'o salvo, com a embalagem de hoje')
        ok([c['id'] for c in cartoes(pg) if c['ativa']] == ['redondo'], 'e abre com o Redondo escolhido, como foi guardado')
        fechar(pg)
        # a embalagem digitada a mao: vale o digitado, e so enquanto nao trocar a caixa
        abrir(pg); preencher(pg, emb='8,00'); pg.click('#calcAplicar'); pg.wait_for_timeout(300)
        sv = (ls(pg, 'deskCalculoPreco') or {})['1']
        ok(sv['embalagemManual'] == 8, 'a embalagem digitada fica guardada como embalagemManual: %s' % sv['embalagemManual'])
        lista = pg.evaluate("embalagensLer()")
        for e in lista:
            if e['nome'] == 'Caixa de Encomenda Flex M':
                e['custo'] = 4.0
        ls_set(pg, 'deskEmbalagens', lista)
        editar(pg, loja='Desk Shope'); abrir(pg)
        ok(pg.input_value('#calcEmbalagem') == '8,00' and 'digitado' in txt(pg, '#calcEmbOrigem'), 'a digitada vale mesmo com o cadastro mudado: %s' % pg.input_value('#calcEmbalagem'))
        escolher(pg, '#calcCaixa', '2')
        ok(pg.input_value('#calcEmbalagem') == '4,70', 'e trocar a caixa volta ao cadastro (4,00 + 0,40 + 0,30 = 4,70): %s' % pg.input_value('#calcEmbalagem'))
        pg.click('#calcAplicar'); pg.wait_for_timeout(300)
        ok((ls(pg, 'deskCalculoPreco') or {})['1']['embalagemManual'] is None, 'aplicar sem digitar guarda embalagemManual nulo')
        pg.context.close()

    # ================================================================ 10. edicao a mao
    if secao(10, 'Edicao a mao: a margem de hoje na hora, Salvar alteracoes sobrevive ao reload, a calculadora nunca grava sozinha'):
        pg = nova()
        ir(pg, PROD)
        param_set(pg, aoSalvar='ficar')
        editar(pg, loja='Desk Shope')
        # sem calculo guardado: digitar atualiza a margem de hoje e mais nada
        pg.fill('#inputPrecoVenda', '119,90'); pg.wait_for_timeout(120)
        esperado = 'Com o custo de hoje, R$ 119,90 dá margem de %s' % pct1(margem(conta(D('119.90'), EMB_SHOPE + 50, LINK[2], 0, 4, 5)))
        ok(txt(pg, '#calcHoje') == esperado and pg.input_value('#inputPrecoListaPadrao') == '129,90' and pg.input_value('#inputMarkup') == '', 'digitar o preco atualiza a margem de hoje na hora (%s) e nada mais: Padrao %s, Markup "%s"' % (txt(pg, '#calcHoje'), pg.input_value('#inputPrecoListaPadrao'), pg.input_value('#inputMarkup')))
        ok(ls(pg, 'deskCalculoPreco') is None, 'e nada e gravado')
        # abrir e fechar a calculadora nunca muda o preco
        abrir(pg); fechar(pg)
        ok(pg.input_value('#inputPrecoVenda') == '119,90' and ls(pg, 'deskCalculoPreco') is None, 'abrir e fechar a calculadora sem Aplicar nao mexe no preco digitado nem grava')
        pg.click('#btnSalvarProduto'); pg.wait_for_timeout(300)
        ok(ls(pg, 'deskCalculoPreco') is None, 'Salvar alteracoes sem calculo guardado nao cria calculo')
        # com calculo guardado
        abrir(pg); pg.click('#calcAplicar'); pg.wait_for_timeout(300)
        ok(pg.input_value('#inputPrecoVenda') == '102,90', 'Aplicar sobrescreve o digitado (so ele faz isso)')
        pg.fill('#inputPrecoVenda', '115,50'); pg.wait_for_timeout(120)
        ok(pg.input_value('#inputPrecoListaPadrao') == '102,90' and pg.input_value('#inputMarkup') == '2,05800' and (ls(pg, 'deskCalculoPreco') or {})['1']['preco'] == 102.9, 'digitar depois de aplicar nao mexe na lista Padrao, no Markup nem no guardado')
        pg.click('#btnSalvarProduto'); pg.wait_for_timeout(300)
        sv = (ls(pg, 'deskCalculoPreco') or {})['1']
        ok(sv['preco'] == 115.5 and sv['markup'] == 2.058 and pg.input_value('#inputPrecoListaPadrao') == '115,50', 'Salvar alteracoes leva o digitado para o preco guardado e para a lista Padrao: %s' % sv['preco'])
        pg.reload(); pg.wait_for_timeout(450); pg.click('.tab-item[data-tab="precos"]')
        ok(pg.input_value('#inputPrecoVenda') == '115,50' and pg.input_value('#inputPrecoListaPadrao') == '115,50' and pg.input_value('#inputMarkup') == '2,05800', 'o reload nao desfaz a edicao: preco 115,50, Padrao 115,50 e o Markup do calculo')
        pg.fill('#inputPrecoVenda', ''); pg.click('#btnSalvarProduto'); pg.wait_for_timeout(300)
        ok((ls(pg, 'deskCalculoPreco') or {})['1']['preco'] == 115.5, 'preco vazio ao salvar nao apaga o guardado')
        pg.context.close()

    # ================================================================ 11. modo leitura e cadastro novo
    if secao(11, 'Modo leitura (o botao some, a margem de hoje fica) e cadastro novo (funciona, nao grava)'):
        pg = nova()
        ir(pg, PROD)
        pg.click('.tab-item[data-tab="precos"]')
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')") and not visivel(pg, '#btnCalcularPreco') and visivel(pg, '#calcHoje') and txt(pg, '#calcHoje').startswith('Com o custo de hoje, R$ 129,90 dá margem de 41,3%'),
           'em modo leitura o botao "Calcular preco" some e a margem de hoje continua: "%s"' % txt(pg, '#calcHoje'))
        pg.click('#btnEditarRegistro'); pg.wait_for_timeout(200)
        ok(visivel(pg, '#btnCalcularPreco') and visivel(pg, '#calcHoje'), 'ao editar o botao aparece')
        pg.context.close()
        pg = nova()
        ir(pg, PROD, '?novo=1')
        pg.click('.tab-item[data-tab="precos"]')
        ok(visivel(pg, '#btnCalcularPreco') and txt(pg, '#calcHoje') == '', 'cadastro novo: o botao aparece e nao ha margem de hoje')
        abrir(pg)
        ok(pg.input_value('#calcCusto') == '' and visivel(pg, '#calcAvisoCusto'), 'cadastro novo nao tem custo: avisa')
        preencher(pg, custo='50,00')
        # o cadastro novo nasce com a embalagem "customizada": a sugerida para 1 peca e o Envelope Pequeno (1,10 + Tag 0,40 + Fita 0,30 = 1,80)
        esp = oraculo(D('1.80') + 50, 30, LINK[2], 0, 4, 5)
        confere_opcoes(pg, esp, 3, 'cadastro novo, custo 50,00')
        pg.click('#calcAplicar'); pg.wait_for_timeout(300)
        va = esp['ops'][0]['r']['preco']
        ok(pg.input_value('#inputPrecoVenda') == campo(va) and pg.input_value('#inputPrecoListaPadrao') == campo(va) and pg.input_value('#inputMarkup') == str((va / 50).quantize(D('0.00001'), rounding=ROUND_HALF_UP)).replace('.', ','), 'cadastro novo: Aplicar preenche os tres campos (%s)' % pg.input_value('#inputPrecoVenda'))
        ok(ls(pg, 'deskCalculoPreco') is None and not pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === 'calculadoraPreco').length"), 'mas nao grava o calculo nem registra (grava quando houver banco)')
        ok('shortcut:' in fonte(PROD) and re.search(r'shortcut: cadastro novo \(\?novo=1\) nao grava o calculo', fonte(PROD)) is not None, 'o limite esta registrado com um comentario shortcut:')
        pg.context.close()

    # ================================================================ 12. layout
    if secao(12, 'A lista de parcelas fica numa linha so, com a mesma altura nos 12 itens, a 1280, 1024 e 853 px; a gaveta sem barra para o lado'):
        for larg in (1280, 1024, 853):
            pg = nova(larg, 800)
            editar(pg, loja='Desk Shope'); abrir(pg)
            pg.click('#calcParcelas .dropdown-select-btn'); pg.wait_for_timeout(250)
            r = pg.evaluate("""() => {
                const it = Array.from(document.querySelectorAll('#calcParcelasMenu .dropdown-select-item')), d = document.getElementById('calcDrawer').getBoundingClientRect();
                const lab = document.querySelector('#calcParcelas .dropdown-select-label'), btn = document.querySelector('#calcParcelas .dropdown-select-btn').getBoundingClientRect(), menu = document.getElementById('calcParcelasMenu').getBoundingClientRect();
                const dr = document.getElementById('calcDrawer');
                return { n: it.length, alturas: Array.from(new Set(it.map(e => Math.round(e.getBoundingClientRect().height * 10)))), nowrap: it.every(e => getComputedStyle(e).whiteSpace === 'nowrap') && getComputedStyle(lab).whiteSpace === 'nowrap',
                         cabem: it.every(e => e.scrollWidth <= e.clientWidth + 1), dentro: it.every(e => e.getBoundingClientRect().right <= d.right + 1 && e.getBoundingClientRect().left >= d.left - 1), fonte: getComputedStyle(it[0]).fontSize,
                         gaveta: dr.scrollWidth - dr.clientWidth, pagina: document.documentElement.scrollWidth - window.innerWidth, baixo: menu.top >= btn.bottom - 1 }; }""")
            ok(r['n'] == 12 and len(r['alturas']) == 1 and r['nowrap'] and r['cabem'] and r['dentro'] and r['fonte'] == '12.5px', 'a %dpx: 12 itens com a mesma altura (%s), numa linha so (nowrap, 12,5px, nenhum estoura) e dentro da gaveta' % (larg, r['alturas']))
            ok(r['gaveta'] <= 0 and r['pagina'] <= 0, 'a %dpx: a gaveta e a pagina nao rolam para o lado (%s / %s)' % (larg, r['gaveta'], r['pagina']))
            ok(r['baixo'], 'a %dpx: o menu abre para baixo' % larg)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
            ok(pg.evaluate("document.getElementById('calcDrawer').classList.contains('open')") and not pg.evaluate("document.getElementById('calcParcelasMenu').classList.contains('open')"), 'a %dpx: Esc fecha o menu primeiro e a gaveta continua' % larg)
            if larg == 1280:
                # o fim da gaveta, com tudo o que o resultado tem, cabe sem estourar a largura
                pg.evaluate("document.getElementById('calcDrawer').scrollTop = 99999"); pg.wait_for_timeout(150)
                f = pg.evaluate("(() => { const dr = document.getElementById('calcDrawer'), b = dr.getBoundingClientRect(); return [dr.scrollWidth - dr.clientWidth, Array.from(dr.querySelectorAll('*')).filter(e => e.offsetParent !== null && e.getBoundingClientRect().right > b.right + 1).length]; })()")
                ok(f == [0, 0], 'a 1280 o fim da gaveta tem tudo dentro da largura: %s' % f)
            pg.context.close()

    # ================================================================ 13. os dois temas e o contraste
    if secao(13, 'Os dois temas: contraste de cada texto da calculadora e cores das margens'):
        for tema in ('dark', 'light'):
            pg = nova(1280, 800, tema)
            editar(pg, loja='Desk Shope'); abrir(pg)
            ok(pg.evaluate("document.body.classList.contains('dark')") == (tema == 'dark'), '%s: a tela abriu no tema %s' % (tema, tema))
            preencher(pg, margem='10')   # deixa o vermelho (minima) aparecer, e depois o laranja
            cores_min = pg.evaluate("Array.from(document.querySelectorAll('.calc-opcao-margem.minima')).length")
            preencher(pg, margem='30')
            JS = """(sels) => {
                const lum = (c) => { const m = c.match(/[\\d.]+/g).map(Number); const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(m[0]) + 0.7152 * f(m[1]) + 0.0722 * f(m[2]); };
                const fundo = (e) => { while (e) { const c = getComputedStyle(e).backgroundColor; const m = c.match(/[\\d.]+/g); if (m && (m.length < 4 || Number(m[3]) > 0.9)) return c; e = e.parentElement; } return 'rgb(255,255,255)'; };
                return sels.map(s => { const e = document.querySelector(s); if (!e) return [s, null]; const a = lum(getComputedStyle(e).color), b = lum(fundo(e)); return [s, (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)]; });
            }"""
            sels = ['.calc-opcao-margem.abaixo', '.calc-opcao-margem:not(.abaixo):not(.minima)', '.calc-opcao-nome', '.calc-opcao-preco', '.calc-opcao-uso', '.calc-opcao-parcela', '#calcR1', '#calcR4', '#calcR4rot', '.calc-origem', '.calc-nota',
                    '#calcFormas .calc-linha span', '#calcFormas .calc-linha b', '.calc-bloco-tit', '#calcPreco', '#calcPrecoRot', '#calcCustoTotal', '.drawer-title', '#calcMinimaDica']
            baixos = [(s, round(c, 2)) for s, c in pg.evaluate(JS, sels) if c is not None and c < 4.5]
            ok(not baixos, '%s: todos os textos da calculadora passam de 4,5:1 (%d medidos): %s' % (tema, len(sels), baixos))
            preencher(pg, margem='10')
            minimos = pg.evaluate(JS, ['.calc-opcao-margem.minima', '#calcFormas .calc-linha b.baixa', '#calcDireta.baixa'])
            ok(all(c is None or c >= 4.5 for s, c in minimos) and cores_min > 0 and pg.evaluate("document.querySelectorAll('.calc-opcao-margem.minima').length") > 0, '%s: o vermelho da margem abaixo da minima passa de 4,5:1: %s' % (tema, [(s, c and round(c, 2)) for s, c in minimos]))
            preencher(pg, margem='30')
            ok(pg.evaluate("getComputedStyle(document.querySelector('.calc-opcao-margem.abaixo')).color") == ('rgb(245, 166, 35)' if tema == 'dark' else 'rgb(180, 83, 9)'), '%s: o laranja de "abaixo da pedida" usa o ambar certo para o tema' % tema)
            # a cor do hoje
            fechar(pg)
            h = pg.evaluate(JS, ['#calcHoje'])
            ok(h[0][1] is not None and h[0][1] >= 4.5, '%s: a margem de hoje passa de 4,5:1: %s' % (tema, h))
            pg.context.close()

    # ================================================================ 14. catalogo, chave e Esc
    if secao(14, 'O catalogo da acao, a chave do localStorage e o Esc'):
        com = [c for c in localiza.caminhos() if "chave:'parametrosVendas'" in open(c, encoding='utf-8').read()]
        sem = [c for c in com if not re.search(r"chave:'calculadoraPreco',\s+nome:'Aplicar o preço calculado',\s+onde:'Cadastros → Produtos', grupo:'Cadastros',\s+pronto:true,\s+exigePadrao:false", open(c, encoding='utf-8').read())]
        ok(len(com) >= 20 and not sem, 'a acao calculadoraPreco esta no catalogo das %d telas que tem a parametrosVendas (grupo Cadastros, sem senha de fabrica); faltam: %s' % (len(com), [_os.path.basename(c) for c in sem]))
        ok("chave:'calculadoraPreco'" in fonte(PROD), 'e na propria ficha do produto')
        aud = open(_os.path.join(PASTA, '_ferramentas', 'auditoria.py'), encoding='utf-8').read()
        ok("'deskCalculoPreco'" in aud, 'a chave deskCalculoPreco esta na lista permitida da auditoria')
        pg = nova()
        ir(pg, PARAM_V)
        ok(pg.evaluate("ACOES_SENHA.filter(a => a.chave === 'calculadoraPreco').map(a => [a.grupo, a.exigePadrao, a.onde, a.nome])") == [['Cadastros', False, 'Cadastros → Produtos', 'Aplicar o preço calculado']], 'no catalogo de outra tela: grupo Cadastros, sem senha de fabrica')
        pg.context.close()
        pg = nova()
        editar(pg, loja='Desk Shope'); abrir(pg)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.getElementById('calcDrawer').classList.contains('open')") and not pg.evaluate("document.getElementById('calcBackdrop').classList.contains('open')"), 'Esc fecha a gaveta')
        abrir(pg); pg.click('#calcBackdrop', position={'x': 20, 'y': 400}); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.getElementById('calcDrawer').classList.contains('open')"), 'o clique fora fecha a gaveta')
        # exigir senha: a acao passa pelo modal de confirmacao como as outras
        param_set(pg, confirmacoes={'calculadoraPreco': True})
        pg.reload(); pg.wait_for_timeout(450); pg.click('.tab-item[data-tab="precos"]'); abrir(pg)
        pg.click('#calcAplicar'); pg.wait_for_timeout(300)
        ok(pg.evaluate("document.getElementById('confirmModal').classList.contains('open')") and pg.input_value('#inputPrecoVenda') == '129,90', 'com senha exigida em Confirmacoes por senha, Aplicar abre o modal e ainda nao muda o preco')
        pg.click('#btnConfirmModalCancelar'); pg.wait_for_timeout(200)
        ok(pg.input_value('#inputPrecoVenda') == '129,90' and ls(pg, 'deskCalculoPreco') is None, 'cancelar o modal nao aplica nem grava')
        pg.context.close()

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:5])
    nav.close()

print('\n%d asserções — FALHAS: %d' % (total[0], len(falhas)))
if falhas:
    print('\nFalharam:')
    for f in falhas:
        print(' -', f)
sys.exit(1 if falhas else 0)
