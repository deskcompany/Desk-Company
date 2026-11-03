# -*- coding: utf-8 -*-
# Mascara de digitacao dos campos de reais e de peso — 02/nov/2026 (itens 6 e 17 da revisao geral).
# Um bloco comum, igual em toda tela que tem esses campos, ouve o `beforeinput` do documento (fase de captura,
# para valer tambem nas linhas criadas por JS) e faz o campo crescer a partir dos centavos (ou das gramas):
#
#   data-mascara="dinheiro"      2 casas:  2 -> 0,02 ; 0 -> 0,20 ; 0 -> 2,00 ; 1589 -> 15,89 ; 123456 -> 1.234,56
#   data-mascara="peso"          3 casas:  1 -> 0,001 ; 15 -> 0,015 ; 150 -> 0,150 ; 1500 -> 1,500
#   data-mascara="valor-ou-pct"  dinheiro, e o % vira "10%" ; a virgula fica guardada em dataset.bruto
#
# O que a suite protege, nesta ordem:
#   [1] o componente, num campo de cada tipo (tecla a tecla, Backspace, Delete, tudo selecionado, letra, readOnly, teto)
#   [2] colar / fill com valor longo e literal ("150", "150,5", "1.234,56", "1234.56")
#   [3] valor-ou-pct: 10%, 2,5%, 3,00, Backspace depois do %, e o desconto certo no total do Pedido e do PDV
#   [4] o MAPA: cada campo de reais e de peso, em toda tela, tem o atributo (no texto da tela, o que cobre o que nasce
#       em template de JS) e, quando esta no DOM, responde a "250" com o resultado certo
#   [5] valor acima de mil chegando CERTO ao resultado, um por fluxo (a armadilha: o ponto de milhar lido como decimal)
#   [6] o bloco e igual em todas as copias, e o campo de porcentagem fica fora, dito no proprio campo
from playwright.sync_api import sync_playwright
import os, glob, re, hashlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

D, P, V = 'dinheiro', 'peso', 'valor-ou-pct'
CASAS = {D: 2, P: 3, V: 2}

# O mapa (tela -> campos): (agulha no texto da tag <input>, tipo). Agulha `id="x"` tambem vira seletor `#x`.
MAPA = {
    'pagina-molde-referencia.html': [('id="inputPesoLiquido"', P), ('id="inputPesoBruto"', P), ('id="inputPrecoVenda"', D), ('id="inputPrecoPromocional"', D),
        ('id="varPesoLiquido"', P), ('id="varPesoBruto"', P), ('id="varPreco"', D), ('id="varPrecoPromocional"', D),
        ('c.impostos', D), ('c.precoCusto', D), ('c.custoMedio', D), ('c.precoVenda', D), ('@Atacado', D), ('@Varejo', D)],
    'pagina-cadastros-produtos-detalhe.html': [('id="inputPesoLiquido"', P), ('id="inputPesoBruto"', P), ('id="inputPrecoVenda"', D), ('id="inputPrecoPromocional"', D), ('id="inputPrecoListaPadrao"', D),
        ('id="varPesoLiquido"', P), ('id="varPesoBruto"', P), ('id="varPreco"', D), ('id="varPrecoPromocional"', D),
        ('id="calcCusto"', D), ('id="calcFrete"', D), ('id="calcEmbalagem"', D), ('id="calcFreteLoja"', D),
        ('c.impostos', D), ('c.precoCusto', D), ('c.custoMedio', D), ('c.precoVenda', D), ('@Atacado', D), ('@Varejo', D)],
    'pagina-cadastros-embalagens.html': [('id="inputPeso"', P), ('id="inputCusto"', D)],
    'pagina-cadastros-clientes-detalhe.html': [('id="inputLimiteCredito"', D)],
    'pagina-cadastros-fornecedores-detalhe.html': [('data-campo="custo"', D)],
    'pagina-configuracoes-formas-recebimento.html': [('id="inputTaxaFixa"', D)],
    'pagina-configuracoes-transportadoras.html': [('id="inputPesoMax"', P)],
    'pagina-estoque-entrada-notas-detalhe.html': [('id="inputFrete"', D), ('id="inputDesconto"', D), ('data-campo="preco"', D)],
    'pagina-estoque-ordens-compra-detalhe.html': [('id="inputDesconto"', D), ('id="inputFrete"', D), ('id="inputICMSST"', D), ('data-campo="preco"', D)],
    'pagina-financas-caixa-lancamento.html': [('id="inputValor"', D)],
    'pagina-financas-caixa.html': [('id="inputTransfValor"', D)],
    'pagina-financas-comissoes-detalhe.html': [('id="pgValor"', D), ('id="ajValor"', D), ('id="lcValor"', D)],
    'pagina-financas-contas-pagar-detalhe.html': [('id="inputValor"', D), ('id="inputValorPago"', D), ('id="inputJuros"', D), ('id="inputDesconto"', D)],
    'pagina-financas-contas-pagar.html': [('id="inputValorPago"', D), ('id="inputJuros"', D), ('id="inputDesconto"', D)],
    'pagina-financas-contas-receber-detalhe.html': [('id="inputValor"', D), ('id="inputTaxas"', D), ('id="inputLiquido"', D), ('id="inputValorRecebido"', D), ('id="inputJuros"', D), ('id="inputDesconto"', D)],
    'pagina-financas-contas-receber.html': [('id="inputValorRecebido"', D), ('id="inputJuros"', D), ('id="inputDesconto"', D), ('id="inputTaxas"', D)],
    'pagina-financas-vale-compra.html': [('id="incValor"', D)],
    'pagina-integracoes-gateways-detalhe.html': [("campo === 'tarifa' ? ' data-mascara=", D)],
    'pagina-logistica-conferencia-saida-detalhe.html': [('data-peso=', P)],
    'pagina-logistica-devolucao-detalhe.html': [('id="inputFreteReal"', D), ('id="inputPesoReal"', P)],
    'pagina-logistica-expedicao-detalhe.html': [('id="inputPesoBruto"', P)],
    'pagina-vendas-crm-detalhe.html': [('id="propValor"', D)],
    'pagina-vendas-metas.html': [('id="defValor"', D)],
    'pagina-vendas-pdv.html': [('id="finDesconto"', V), ('id="abrirTroco"', D), ('id="itemPreco"', D), ('id="itemAjusteValor"', D), ('id="movValor"', D), ('id="valeUsarValor"', D),
        ('data-receb-valor=', D), ('data-receb-recebido=', D), ('data-parc-valor=', D), ('data-fechar=', D)],
    'pagina-vendas-pedidos-detalhe.html': [('id="inputDesconto"', V), ('id="inputFrete"', D), ('id="inputFretePagoLoja"', D), ('id="inputDespesas"', D), ('id="inputValeUsar"', D),
        ('data-campo="precoLista"', D), ('id="itLista"', D)],
}
# porcentagem com placeholder 0,00: fora da mascara, dito no proprio campo
FORA = {
    'pagina-configuracoes-formas-recebimento.html': ['id="inputTaxaPct"', 'data-taxa-parcela='],
    'pagina-integracoes-gateways-detalhe.html': ['id="gwJuros"', 'id="gwMulta"'],
}

falhas = []
total = [0]


def ok(c, m):
    total[0] += 1
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)


def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e


def brl(n):
    s = '{:,.2f}'.format(round(n + 1e-9, 2))
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def num(txt):
    t = re.sub(r'[^\d,.-]', '', txt or '').replace('.', '').replace(',', '.')
    return float(t) if t not in ('', '-') else None


def tag_do_texto(txt, agulha):
    """Todas as tags <input ...> do texto da tela que contem a agulha."""
    achadas = []
    for m in re.finditer(r'<input\b', txt):
        fim = txt.find('>', m.start())
        t = txt[m.start():fim]
        if agulha in t: achadas.append(t)
    return achadas


with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path=CHROME)
    ctx = b.new_context(viewport={'width': 1440, 'height': 900})
    try: ctx.grant_permissions(['clipboard-read', 'clipboard-write'])
    except Exception: pass
    erros = []

    def nova():
        pg = ctx.new_page()
        pg.on('pageerror', lambda e: erros.append(str(e)))
        pg.on('console', lambda m: erros.append(m.text) if (m.type == 'error' and not ruido(m.text)) else None)
        pg.on('dialog', lambda d: d.dismiss())
        return pg

    def abre(pg, arq, q='', espera=500):
        pg.goto(localiza.uri(arq + q)); pg.wait_for_timeout(espera)

    def clic(pg, sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel)

    def val(pg, sel):
        return pg.input_value(sel)

    def zera(pg, sel):
        """Esvazia por codigo (sem passar pela mascara): ponto de partida limpo."""
        pg.evaluate("(s) => { const e = document.querySelector(s); e.value = ''; e.dataset.bruto = ''; }", sel)

    def digita(pg, sel, teclas, de_zero=True):
        if de_zero: zera(pg, sel)
        pg.locator(sel).press_sequentially(teclas)

    # ------------------------------------------------------------------ campos de prova no meio de uma tela qualquer
    pg = nova()
    abre(pg, 'pagina-financas-caixa-lancamento.html')
    pg.evaluate("""() => {
      ['dinheiro', 'peso', 'valor-ou-pct', 'nenhuma'].forEach((t, i) => {
        const e = document.createElement('input'); e.type = 'text'; e.id = 't_' + t; e.placeholder = '0,00';
        if (t !== 'nenhuma') { e.setAttribute('data-mascara', t); e.setAttribute('inputmode', 'decimal'); }
        e.style.cssText = 'position:fixed;top:' + (8 + i * 40) + 'px;left:8px;width:220px;z-index:99999;background:#fff;color:#000';
        document.body.appendChild(e);   // criado depois da carga: a delegacao no document tem de pegar
      });
      window.__ev = { input: 0, change: 0 };
      document.addEventListener('input', (e) => { if (e.target.id && e.target.id.indexOf('t_') === 0) window.__ev.input++; });
      document.addEventListener('change', (e) => { if (e.target.id && e.target.id.indexOf('t_') === 0) window.__ev.change++; });
    }""")
    DIN, PES, VOP, NEN = '#t_dinheiro', '#t_peso', '#t_valor-ou-pct', '#t_nenhuma'

    def v(sel): return val(pg, sel)

    # ------------------------------------------------------------------ 1
    print('\n[1] O componente: um campo de cada tipo, tecla a tecla')
    for teclas, esp in [('2', '0,02'), ('20', '0,20'), ('200', '2,00'), ('2000', '20,00'), ('250', '2,50'), ('1589', '15,89'),
                        ('123456', '1.234,56'), ('12345678', '123.456,78'), ('0', '0,00'), ('007', '0,07'), ('1a2', '0,12'), ('a-,.%', '')]:
        digita(pg, DIN, teclas)
        ok(v(DIN) == esp, 'dinheiro: digitar "%s" dá "%s" (deu "%s")' % (teclas, esp, v(DIN)))
    zera(pg, DIN); pg.evaluate("document.querySelector('#t_dinheiro').value = '0,00'")
    pg.locator(DIN).press_sequentially('2')
    ok(v(DIN) == '0,02', 'com "0,00" na tela, o 2 dá 0,02')
    digita(pg, DIN, '2'); pg.locator(DIN).press_sequentially('0'); ok(v(DIN) == '0,20', 'o 0 depois dá 0,20')
    pg.locator(DIN).press_sequentially('0'); ok(v(DIN) == '2,00', 'outro 0 dá 2,00')
    pg.locator(DIN).press_sequentially('0'); ok(v(DIN) == '20,00', 'outro 0 dá 20,00')
    for teclas, esp in [('1', '0,001'), ('15', '0,015'), ('150', '0,150'), ('1500', '1,500'), ('1234567', '1.234,567'), ('x9', '0,009')]:
        digita(pg, PES, teclas)
        ok(v(PES) == esp, 'peso: digitar "%s" dá "%s" (deu "%s")' % (teclas, esp, v(PES)))

    print('\n    Backspace, Delete, tudo selecionado')
    digita(pg, DIN, '1589')
    cadeia = []
    for _ in range(4):
        pg.locator(DIN).press('Backspace'); cadeia.append(v(DIN))
    ok(cadeia == ['1,58', '0,15', '0,01', ''], 'Backspace tira o último dígito, um por vez, até esvaziar: %s' % cadeia)
    ok(pg.evaluate("document.querySelector('#t_dinheiro').matches(':placeholder-shown')"), 'esvaziado mostra o placeholder, igual a nunca ter sido preenchido')
    digita(pg, DIN, '1589'); pg.locator(DIN).press('Home'); pg.locator(DIN).press('Delete')
    ok(v(DIN) == '1,58', 'Delete também tira o último dígito: %s' % v(DIN))
    digita(pg, DIN, '5'); pg.locator(DIN).press('Backspace'); ok(v(DIN) == '', '0,05 e Backspace chegam a zero: campo vazio, não "0,00"')
    digita(pg, DIN, '10'); pg.locator(DIN).press('Backspace'); ok(v(DIN) == '0,01', '0,10 e Backspace dão 0,01')
    digita(pg, DIN, '0'); pg.locator(DIN).press('Backspace'); ok(v(DIN) == '', 'o 0,00 digitado e Backspace esvaziam')
    digita(pg, DIN, '1589'); pg.locator(DIN).press('Control+A'); pg.locator(DIN).press('Backspace')
    ok(v(DIN) == '', 'tudo selecionado e Backspace esvazia')
    digita(pg, DIN, '1589'); pg.locator(DIN).press('Control+A'); pg.locator(DIN).press('Delete')
    ok(v(DIN) == '', 'tudo selecionado e Delete esvazia')
    digita(pg, DIN, '1589'); pg.locator(DIN).press('Control+A'); pg.locator(DIN).press_sequentially('7')
    ok(v(DIN) == '0,07', 'tudo selecionado e um dígito: recomeça do dígito digitado (0,07): %s' % v(DIN))
    digita(pg, PES, '1500'); pg.locator(PES).press('Backspace'); ok(v(PES) == '0,150', 'peso: Backspace de 1,500 dá 0,150')
    digita(pg, PES, '1500'); pg.locator(PES).press('Control+A'); pg.locator(PES).press_sequentially('5'); ok(v(PES) == '0,005', 'peso: tudo selecionado e 5 dá 0,005')
    digita(pg, DIN, '1' * 16)
    ok(len(re.sub(r'\D', '', v(DIN))) == 13, 'o teto é de 13 dígitos: %s' % v(DIN))

    print('\n    readOnly, disabled, eventos e campo sem máscara')
    digita(pg, DIN, '150'); pg.evaluate("document.querySelector('#t_dinheiro').readOnly = true")
    pg.locator(DIN).press_sequentially('9'); pg.locator(DIN).press('Backspace')
    ok(v(DIN) == '1,50', 'readOnly não mexe: %s' % v(DIN))
    pg.evaluate("document.querySelector('#t_dinheiro').readOnly = false")
    pg.evaluate("window.__ev = { input: 0, change: 0 }")
    digita(pg, DIN, '12'); pg.locator(DIN).blur(); pg.wait_for_timeout(80)
    ok(pg.evaluate("window.__ev.input") == 2, 'cada tecla dispara um "input" que borbulha até o documento (as contas da tela seguem): %s' % pg.evaluate("window.__ev.input"))
    ok(pg.evaluate("window.__ev.change") == 1, 'e sair do campo dá o "change" que o navegador não daria (valor posto por código): %s' % pg.evaluate("window.__ev.change"))
    pg.evaluate("window.__ev = { input: 0, change: 0 }")
    pg.locator(DIN).focus(); pg.locator(DIN).blur(); pg.wait_for_timeout(50)
    ok(pg.evaluate("window.__ev.change") == 0, 'passar pelo campo sem mudar nada não dá "change"')
    digita(pg, NEN, 'ab1,5'); ok(v(NEN) == 'ab1,5', 'campo sem data-mascara fica livre: %s' % v(NEN))
    pg.evaluate("document.querySelector('#t_dinheiro').value = '99,90'")
    ok(v(DIN) == '99,90', 'valor posto por código (el.value) continua livre, sem máscara')
    pg.locator(DIN).press_sequentially('1'); ok(v(DIN) == '999,01', 'e o dígito seguinte cresce a partir dele: %s' % v(DIN))

    # ------------------------------------------------------------------ 2
    print('\n[2] Colar ou fill com valor longo: literal')
    for txt, esp in [('150', '150,00'), ('150,5', '150,50'), ('1.234,56', '1.234,56'), ('1234.56', '1.234,56'), ('1234,56', '1.234,56'), ('R$ 99,9', '99,90'),
                     ('1.234', '1.234,00'), ('1.234.567', '1.234.567,00'), ('10', '10,00'), ('0,99', '0,99')]:
        pg.fill(DIN, txt)
        ok(v(DIN) == esp, 'dinheiro: colar "%s" dá "%s" (deu "%s")' % (txt, esp, v(DIN)))
    pg.fill(DIN, '77,10'); pg.fill(DIN, 'abc')
    ok(v(DIN) == '77,10', 'colar texto sem dígito nenhum é ignorado: o campo fica como estava')
    pg.fill(DIN, ''); ok(v(DIN) == '', 'fill vazio esvazia')
    pg.fill(DIN, '7'); ok(v(DIN) == '0,07', 'um caractere só é tecla, não valor: "7" dá 0,07')
    for txt, esp in [('1,5', '1,500'), ('1.234', '1,234'), ('12,3456', '12,345'), ('1.500,25', '1.500,250'), ('15', '15,000'), ('0,25', '0,250')]:
        pg.fill(PES, txt)
        ok(v(PES) == esp, 'peso: colar "%s" dá "%s" (deu "%s")' % (txt, esp, v(PES)))
    pg.fill(DIN, '1' * 15); ok(v(DIN) != '' and len(re.sub(r'\D', '', v(DIN))) <= 13, 'colar mais de 13 dígitos não passa do teto')
    colou = None
    try:
        pg.evaluate("navigator.clipboard.writeText('1.234,56')")
        zera(pg, DIN); pg.locator(DIN).focus(); pg.keyboard.press('Control+V'); pg.wait_for_timeout(120)
        colou = v(DIN)
    except Exception as e:
        colou = 'sem área de transferência: %s' % str(e)[:60]
    ok(colou == '1.234,56' or colou.startswith('sem área'), 'Ctrl+V de verdade (insertFromPaste) dá 1.234,56 (%s)' % colou)

    # ------------------------------------------------------------------ 3
    print('\n[3] valor-ou-pct: dinheiro, e o % vira porcentagem')
    def bruto(): return pg.evaluate("document.querySelector('#t_valor-ou-pct').dataset.bruto || ''")
    digita(pg, VOP, '10'); ok(v(VOP) == '0,10' and bruto() == '10', 'dígitos entram como dinheiro (10 dá 0,10) e o bruto guarda o digitado: %s / %s' % (v(VOP), bruto()))
    pg.locator(VOP).press_sequentially('%'); ok(v(VOP) == '10%', '10 e %% dá "10%%": %s' % v(VOP))
    digita(pg, VOP, '2,5'); ok(v(VOP) == '0,25' and bruto() == '2,5', 'a vírgula digitada não muda o que se vê (0,25), mas fica no bruto (2,5): %s / %s' % (v(VOP), bruto()))
    pg.locator(VOP).press_sequentially('%'); ok(v(VOP) == '2,5%', '2,5 e %% dá "2,5%%": %s' % v(VOP))
    digita(pg, VOP, '3,00'); ok(v(VOP) == '3,00' and bruto() == '3,00', '3,00 digitado fica 3,00 (valor em reais): %s / %s' % (v(VOP), bruto()))
    digita(pg, VOP, '10%'); pg.locator(VOP).press_sequentially('5'); ok(v(VOP) == '10%', 'em modo percentual, outro dígito é ignorado: %s' % v(VOP))
    pg.locator(VOP).press('Backspace'); ok(v(VOP) == '0,10', 'Backspace depois do %% tira o %% e volta ao dinheiro dos mesmos dígitos (0,10): %s' % v(VOP))
    pg.locator(VOP).press_sequentially('5'); ok(v(VOP) == '1,05', 'e daí em diante é dinheiro de novo: %s' % v(VOP))
    digita(pg, VOP, '2,5%'); pg.locator(VOP).press('Backspace'); ok(v(VOP) == '0,25', '2,5%% e Backspace voltam a 0,25: %s' % v(VOP))
    digita(pg, VOP, '10%'); pg.locator(VOP).press('Control+A'); pg.locator(VOP).press_sequentially('7')
    ok(v(VOP) == '0,07', 'em modo percentual, tudo selecionado e um dígito recomeça: %s' % v(VOP))
    digita(pg, VOP, '10%'); pg.locator(VOP).press('Control+A'); pg.locator(VOP).press('Backspace'); ok(v(VOP) == '', 'em modo percentual, tudo selecionado e Backspace esvazia')
    digita(pg, VOP, '5'); pg.locator(VOP).press('Backspace'); ok(v(VOP) == '' and bruto() == '', 'esvaziar zera o bruto: "%s"' % bruto())
    digita(pg, VOP, '%'); ok(v(VOP) == '', '% sem dígito nenhum não faz nada')
    for txt, esp in [('10%', '10%'), ('2,5%', '2,5%'), ('3,00', '3,00'), ('1.234,56', '1.234,56'), ('15', '15,00')]:
        pg.fill(VOP, txt); ok(v(VOP) == esp, 'colar "%s" fica "%s" (ficou "%s")' % (txt, esp, v(VOP)))
    pg.evaluate("document.querySelector('#t_valor-ou-pct').value = ''")
    pg.locator(VOP).press_sequentially('5'); ok(v(VOP) == '0,05' and bruto() == '5', 'a tela esvaziou o campo por código: o bruto velho não gruda: %s / %s' % (v(VOP), bruto()))
    digita(pg, DIN, '10'); pg.locator(DIN).press_sequentially('%,'); ok(v(DIN) == '0,10', 'em campo só de dinheiro, % e vírgula são ignorados')
    pg.close()

    print('\n    O desconto certo no total do Pedido de Venda, nos dois modos')
    pg = nova()
    abre(pg, 'pagina-vendas-pedidos-detalhe.html', '?id=1&editar=1', 800)

    def totais():
        return (num(pg.inner_text('#totProdutos')), num(pg.inner_text('#totGeral')), num(val(pg, '#inputFrete')) or 0, num(val(pg, '#inputDespesas')) or 0)
    prod, geral, frete, desp = totais()
    for teclas, calc in [('10%', lambda p: p * 0.10), ('2,5%', lambda p: p * 0.025), ('300', lambda p: 3.00), ('3,00', lambda p: 3.00), ('12550', lambda p: 125.50), ('0', lambda p: 0.0)]:
        digita(pg, '#inputDesconto', teclas); pg.wait_for_timeout(120)
        prod, geral, frete, desp = totais()
        esp = prod - calc(prod) + frete + desp
        ok(abs(geral - esp) < 0.006, 'Pedido: desconto digitado "%s" (campo "%s") dá o total %s (esperado %s)' % (teclas, val(pg, '#inputDesconto'), brl(geral), brl(esp)))
    pg.fill('#inputDesconto', '10%'); pg.wait_for_timeout(120)
    prod, geral, frete, desp = totais()
    ok(abs(geral - (prod * 0.9 + frete + desp)) < 0.006, 'Pedido: colar "10%" dá o mesmo que digitar')
    pg.close()

    print('\n    O desconto certo no total do PDV, nos dois modos')
    pg = nova()
    abre(pg, 'pagina-vendas-pdv.html')
    pg.evaluate("localStorage.removeItem('deskPdv'); localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); pg.reload(); pg.wait_for_timeout(600)

    def escolher(pg, raiz, valor):
        clic(pg, '#' + raiz + ' .dropdown-select-btn'); pg.wait_for_timeout(120)
        pg.evaluate("([r, v]) => document.querySelector('#' + r + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()", [raiz, str(valor)]); pg.wait_for_timeout(220)
    clic(pg, '#btnAbrirCaixa'); pg.wait_for_timeout(300); escolher(pg, 'abrirLoja', 1)
    digita(pg, '#abrirTroco', '123456')
    ok(val(pg, '#abrirTroco') == '1.234,56', 'PDV: troco digitado 123456 mostra 1.234,56')
    clic(pg, '#btnConfirmarAbertura'); pg.wait_for_timeout(400)
    ok(pg.evaluate('turno && turno.trocoInicial') == 1234.56, 'PDV: o caixa abre com o troco 1234,56 (e não 1,234): %s' % pg.evaluate('turno && turno.trocoInicial'))
    pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', 'FON-BT-200'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(300)
    ok(pg.evaluate('venda.itens.length') == 1, 'PDV: um item na venda')
    clic(pg, '#btnContinuar'); pg.wait_for_timeout(450)
    ok(pg.evaluate('momento') == 'finalizar', 'PDV: na tela de finalizar (%s)' % pg.evaluate('momento'))
    sub = num(pg.inner_text('#finTotal'))
    for teclas, calc in [('10%', lambda p: p * 0.10), ('2,5%', lambda p: p * 0.025), ('1500', lambda p: 15.00), ('3,00', lambda p: 3.00)]:
        digita(pg, '#finDesconto', teclas); pg.wait_for_timeout(200)
        esp = sub - round(calc(sub) + 1e-9, 2)
        got = num(pg.inner_text('#finTotal'))
        ok(abs(got - esp) < 0.006, 'PDV: desconto digitado "%s" (campo "%s") dá o total %s (esperado %s)' % (teclas, val(pg, '#finDesconto'), brl(got), brl(esp)))
    pg.fill('#finDesconto', '10%'); pg.wait_for_timeout(200)
    ok(abs(num(pg.inner_text('#finTotal')) - (sub - round(sub * 0.10 + 1e-9, 2))) < 0.006, 'PDV: colar "10%" dá o mesmo que digitar')
    pg.close()

    # ------------------------------------------------------------------ 4
    print('\n[4] O mapa: cada campo de reais e de peso, em toda tela')
    n_campos = 0
    for tela, campos in MAPA.items():
        txt = open(localiza.onde(tela), encoding='utf-8', newline='').read()
        for agulha, tipo in campos:
            n_campos += 1
            if agulha.startswith("campo === 'tarifa'"):
                ok(("campo === 'tarifa' ? ' data-mascara=\"dinheiro\"' : ''" in txt), '%s: a tarifa em reais (célula montada por JS) nasce com data-mascara="dinheiro"' % tela)
                continue
            if agulha.startswith('@'):   # sem id: o campo logo abaixo do rotulo
                m = re.search(r'<label>%s</label>\s*(<input[^>]*>)' % agulha[1:], txt)
                tags = [m.group(1)] if m else []
            else:
                tags = tag_do_texto(txt, agulha)
            certas = [t for t in tags if ('data-mascara="%s"' % tipo) in t and 'inputmode="decimal"' in t]
            ok(len(tags) >= 1 and len(certas) == len(tags), '%s: %s tem data-mascara="%s" e inputmode="decimal" (%d tag%s)' % (tela, agulha, tipo, len(tags), '' if len(tags) == 1 else 's'))
    for tela, agulhas in FORA.items():
        txt = open(localiza.onde(tela), encoding='utf-8', newline='').read()
        for agulha in agulhas:
            tags = tag_do_texto(txt, agulha)
            ok(len(tags) == 1 and 'data-sem-mascara="percentual"' in tags[0] and 'data-mascara=' not in tags[0],
               '%s: %s é porcentagem: fora da máscara, e diz isso no campo' % (tela, agulha))
    print('    (%d campos no mapa, em %d telas)' % (n_campos, len(MAPA)))

    print('\n    Cada campo que está no DOM responde a "250" com o resultado certo')
    pag = nova()
    tocados, pulados = 0, []
    for tela, campos in MAPA.items():
        if tela == 'pagina-molde-referencia.html': continue
        q = '?id=1&editar=1' if tela.endswith('-detalhe.html') else '?editar=1'
        abre(pag, tela, q, 500)
        for agulha, tipo in campos:
            m = re.match(r'id="([^"]+)"', agulha)
            if not m: continue
            sel = '#' + m.group(1)
            if pag.locator(sel).count() != 1:
                pulados.append('%s %s (não está no DOM)' % (tela, sel)); continue
            livre = pag.evaluate("""(s) => { const e = document.querySelector(s);
              if (e.disabled || e.readOnly) return false;
              for (let n = e; n && n !== document.documentElement; n = n.parentElement) {
                const c = getComputedStyle(n);
                if (c.display === 'none') n.style.setProperty('display', 'block', 'important');
                if (c.visibility === 'hidden') n.style.setProperty('visibility', 'visible', 'important');
                n.hidden = false;
              }
              e.value = ''; e.dataset.bruto = ''; e.focus(); return document.activeElement === e; }""", sel)
            if not livre:
                pulados.append('%s %s (travado ou sem foco)' % (tela, sel)); continue
            pag.keyboard.type('250')
            esp = '0,250' if tipo == P else '2,50'
            tocados += 1
            ok(val(pag, sel) == esp, '%s %s (%s): "250" dá "%s" (deu "%s")' % (tela.replace('pagina-', ''), sel, tipo, esp, val(pag, sel)))
    print('    (%d campos tocados no DOM; %d pulados: %s)' % (tocados, len(pulados), '; '.join(pulados)[:600]))
    pag.close()

    # ------------------------------------------------------------------ 5
    print('\n[5] Valor acima de mil chega certo ao resultado, um por fluxo')
    erros.clear()   # a passada acima forca campos escondidos a aparecer; o que ela acende no console nao e de usuario

    print('\n    Pedido de Venda: 1.234,56 x 2 = 2.469,12')
    pg = nova(); abre(pg, 'pagina-vendas-pedidos-detalhe.html', '?id=1&editar=1', 800)
    pg.evaluate("document.getElementById('btnAdicionarItem').click()"); pg.wait_for_timeout(200)
    ult = '#corpoItens tr:last-child '
    pg.fill(ult + 'input[data-campo="qtd"]', '2')
    digita(pg, ult + 'input[data-campo="precoLista"]', '123456'); pg.wait_for_timeout(150)
    ok(val(pg, ult + 'input[data-campo="precoLista"]') == '1.234,56', 'Preço Un digitado mostra 1.234,56')
    ok(pg.evaluate("ITENS[ITENS.length - 1].precoLista") == 1234.56, 'e o item guarda 1234,56 (não 1,234): %s' % pg.evaluate("ITENS[ITENS.length - 1].precoLista"))
    ok(pg.inner_text(ult + 'td:nth-child(7) b').replace('R$', '').strip() == '2.469,12', 'o total da linha é 2.469,12: %s' % pg.inner_text(ult + 'td:nth-child(7) b'))
    digita(pg, '#inputFrete', '123456'); pg.wait_for_timeout(150)
    ok(num(pg.inner_text('#totGeral')) >= 2469.12 + 1234.56, 'o frete 1.234,56 entra no total geral (%s)' % pg.inner_text('#totGeral'))
    pg.close()

    print('\n    PDV: o troco 1.234,56 foi lido acima (turno.trocoInicial). Preço do item e desconto de 1.234,56 abaixo')
    pg = nova(); abre(pg, 'pagina-vendas-pdv.html')
    pg.evaluate("localStorage.removeItem('deskPdv'); localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); pg.reload(); pg.wait_for_timeout(600)
    clic(pg, '#btnAbrirCaixa'); pg.wait_for_timeout(300); escolher(pg, 'abrirLoja', 1); digita(pg, '#abrirTroco', '10000'); clic(pg, '#btnConfirmarAbertura'); pg.wait_for_timeout(400)
    pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', 'FON-BT-200'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(300)
    clic(pg, '#listaItens tbody tr'); pg.wait_for_timeout(350)
    digita(pg, '#itemPreco', '123456'); pg.wait_for_timeout(200)
    ok(val(pg, '#itemPreco') == '1.234,56', 'PDV: preço do item digitado mostra 1.234,56')
    clic(pg, '#btnAplicarItem'); pg.wait_for_timeout(300)
    ok(pg.evaluate('venda.itens[0].preco') == 1234.56 and pg.inner_text('#totVenda') == 'R$ 1.234,56', 'PDV: o item entra a 1234,56 e a venda soma R$ 1.234,56: %s' % pg.inner_text('#totVenda'))
    clic(pg, '#btnContinuar'); pg.wait_for_timeout(450)
    digita(pg, '#finDesconto', '123456'); pg.wait_for_timeout(200)
    ok(abs(num(pg.inner_text('#finTotal')) - 0.0) < 0.006 and 'R$ 1.234,56' in pg.inner_text('#finDescontoValor'),
       'PDV: desconto de 1.234,56 sobre 1.234,56 zera o total: %s / %s' % (pg.inner_text('#finTotal'), pg.inner_text('#finDescontoValor')))
    pg.close()

    print('\n    Contas a Pagar: baixa parcial de 1.234,56')
    pg = nova(); abre(pg, 'pagina-financas-contas-pagar.html', '', 600)
    alvo = pg.evaluate("(() => { const t = TITULOS.filter(x => !x.cancelado && x.pago === 0 && x.valor > 1300)[0]; return t ? t.id : null; })()")
    ok(alvo is not None, 'existe uma conta em aberto acima de R$ 1.300 para provar')
    if alvo is not None:
        pg.evaluate("(id) => document.querySelector('[data-check=\"titulo\"][data-id=\"' + id + '\"]').click()", alvo); pg.wait_for_timeout(250)
        pg.click('#btnPagarSelecionadas'); pg.wait_for_timeout(400); pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(200)
        digita(pg, '#inputValorPago', '123456'); pg.wait_for_timeout(300)
        ok(val(pg, '#inputValorPago') == '1.234,56' and 'parcial' in pg.text_content('#previaPagamento'), 'a prévia aceita 1.234,56 como pagamento parcial')
        pg.click('#btnConfirmarPagamento'); pg.wait_for_timeout(450)
        if pg.evaluate("document.getElementById('confirmModal').classList.contains('open')"): clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
        pago = pg.evaluate("(id) => TITULOS.filter(x => x.id === id)[0].pago", alvo)
        ok(abs(pago - 1234.56) < 0.006, 'a conta ficou com R$ 1234,56 pagos (não 1,23): %s' % pago)
    pg.close()

    print('\n    Contas a Receber: recebimento parcial de 1.234,56')
    pg = nova(); abre(pg, 'pagina-financas-contas-receber.html', '', 600)
    alvo = pg.evaluate("(() => { const t = TITULOS.filter(x => !x.cancelado && x.recebido === 0 && x.valor > 1300)[0]; return t ? t.id : null; })()")
    ok(alvo is not None, 'existe uma conta em aberto acima de R$ 1.300 para provar')
    if alvo is not None:
        pg.evaluate("(id) => { selTit = [id]; render(); }", alvo); pg.wait_for_timeout(300)
        pg.click('#btnReceberSelecionadas'); pg.wait_for_timeout(400); pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(250)
        digita(pg, '#inputValorRecebido', '123456'); zera(pg, '#inputTaxas'); pg.wait_for_timeout(300)
        ok(val(pg, '#inputValorRecebido') == '1.234,56', 'o campo mostra 1.234,56')
        pg.click('#btnConfirmarRecebimento'); pg.wait_for_timeout(450)
        if pg.evaluate("document.getElementById('confirmModal').classList.contains('open')"): clic(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(400)
        rec = pg.evaluate("(id) => TITULOS.filter(x => x.id === id)[0].recebido", alvo)
        ok(abs(rec - 1234.56) < 0.006, 'a conta ficou com R$ 1234,56 recebidos (não 1,23): %s' % rec)
    pg.close()

    print('\n    Lançamento do Caixa: saldo informado de 1.234,56')
    pg = nova(); abre(pg, 'pagina-financas-caixa-lancamento.html', '', 600)
    pg.click('#ddTipo .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#ddTipo .dropdown-select-item[data-value="saldo"]'); pg.wait_for_timeout(200)
    digita(pg, '#inputValor', '123456'); pg.wait_for_timeout(300)
    ok(val(pg, '#inputValor') == '1.234,56', 'o campo mostra 1.234,56')
    nota = pg.inner_text('#notaSaldo')
    ok('Informando R$ 1.234,56' in nota or 'igual' in nota, 'a nota lê o saldo como R$ 1.234,56: %s' % nota[:140])
    pg.close()

    print('\n    Produtos: custo e preço, e a calculadora de preço')
    pg = nova(); abre(pg, 'pagina-cadastros-produtos-detalhe.html', '?editar=1', 700)
    pg.click('.tab-item[data-tab="complementares"]'); pg.wait_for_timeout(150)
    pg.click('#inputLojaDesk .dropdown-select-btn'); pg.wait_for_timeout(80)
    pg.click('#inputLojaDesk .dropdown-select-item[data-value="Desk Shope"]'); pg.wait_for_timeout(150)
    pg.click('.tab-item[data-tab="custos"]'); pg.wait_for_timeout(150)
    celula = '#tabelaCustos tr:last-child td:nth-child(5) input'
    digita(pg, celula, '123456')
    pg.click('.tab-item[data-tab="precos"]'); pg.wait_for_timeout(150)
    digita(pg, '#inputPrecoVenda', '234567'); pg.wait_for_timeout(200)
    pg.click('.tab-item[data-tab="custos"]'); pg.wait_for_timeout(100)
    ok(val(pg, celula) == '1.234,56', 'custo digitado na aba Custos mostra 1.234,56')
    pg.click('.tab-item[data-tab="precos"]'); pg.wait_for_timeout(100)
    ok(val(pg, '#inputPrecoVenda') == '2.345,67', 'preço de venda digitado mostra 2.345,67')
    pg.click('#btnCalcularPreco'); pg.wait_for_timeout(350)
    ok(val(pg, '#calcCusto') == '1.234,56', 'a calculadora lê o custo da aba como 1.234,56 (não 1,23): %s' % val(pg, '#calcCusto'))
    ok('2.345,67' in pg.inner_text('#calcHoje'), 'e o preço de hoje do cadastro como R$ 2.345,67: %s' % pg.inner_text('#calcHoje')[:120])
    for sel in ('#calcFrete', '#calcEmbalagem', '#calcFreteLoja'): pg.fill(sel, '')
    digita(pg, '#calcCusto', '123456'); pg.wait_for_timeout(250)
    ok(pg.inner_text('#calcCustoTotal').strip() == 'R$ 1.234,56', 'digitado na calculadora, o custo total é R$ 1.234,56: %s' % pg.inner_text('#calcCustoTotal'))
    digita(pg, '#calcFrete', '100000'); pg.wait_for_timeout(250)
    ok(pg.inner_text('#calcCustoTotal').strip() == 'R$ 2.234,56', 'mais um frete de 1.000,00: R$ 2.234,56 (%s)' % pg.inner_text('#calcCustoTotal'))
    pg.close()

    print('\n    Embalagens: custo e peso, gravando e reabrindo')
    pg = nova(); abre(pg, 'pagina-cadastros-embalagens.html', '', 600)
    pg.evaluate("localStorage.removeItem('deskEmbalagens')"); pg.reload(); pg.wait_for_timeout(500)
    clic(pg, '#btnNovaEmbalagem'); pg.wait_for_timeout(300)
    pg.fill('#inputNomeEmbalagem', 'Caixa da mascara')
    for k in ('Largura', 'Altura', 'Comprimento'):
        if pg.locator('#input' + k).count(): pg.fill('#input' + k, '10')
    digita(pg, '#inputCusto', '123456'); digita(pg, '#inputPeso', '1500')
    ok(val(pg, '#inputCusto') == '1.234,56' and val(pg, '#inputPeso') == '1,500', 'custo 1.234,56 e peso 1,500 digitados')
    clic(pg, '#btnSalvarEmbalagem'); pg.wait_for_timeout(400)
    gravada = pg.evaluate("(JSON.parse(localStorage.getItem('deskEmbalagens')) || []).filter(e => e.nome === 'Caixa da mascara')[0] || null")
    ok(gravada is not None and gravada['custo'] == 1234.56 and gravada['peso'] == 1.5, 'gravou custo 1234,56 e peso 1,5 (não 1,23 e 1,5 lido como 1): %s' % ({k: gravada[k] for k in ('custo', 'peso')} if gravada else None))
    pg.evaluate("itensPorPaginaAtual = 100; renderEmbalagens();"); pg.fill('#campoBusca', 'Caixa da mascara'); pg.wait_for_timeout(250)
    pg.click('#listaEmbalagens .embalagens-card'); pg.wait_for_timeout(350)
    ok(val(pg, '#inputCusto') == '1.234,56' and val(pg, '#inputPeso') == '1,500', 'reabrir mostra 1.234,56 e 1,500, sem valor deslocado: %s / %s' % (val(pg, '#inputCusto'), val(pg, '#inputPeso')))
    clic(pg, '#btnSalvarEmbalagem'); pg.wait_for_timeout(350)
    de_novo = pg.evaluate("(JSON.parse(localStorage.getItem('deskEmbalagens')) || []).filter(e => e.nome === 'Caixa da mascara')[0]")
    ok(de_novo['custo'] == 1234.56 and de_novo['peso'] == 1.5, 'salvar sem mexer não desloca nada: %s' % ({k: de_novo[k] for k in ('custo', 'peso')}))
    pg.close()

    print('\n    Gateways: tarifa de 1.234,56')
    pg = nova(); abre(pg, 'pagina-integracoes-gateways-detalhe.html', '?id=1&editar=1', 700)
    cel = '#wrapCondicoes .gw-cin[data-campo="tarifa"]'
    n_cel = pg.locator(cel).count()
    ok(n_cel > 0 and pg.evaluate("[...document.querySelectorAll('#wrapCondicoes .gw-cin[data-campo=\"tarifa\"]')].every(e => e.getAttribute('data-mascara') === 'dinheiro')"),
       'as %d células de tarifa têm data-mascara="dinheiro"; taxa e prazo não têm' % n_cel)
    ok(pg.evaluate("[...document.querySelectorAll('#wrapCondicoes .gw-cin:not([data-campo=\"tarifa\"])')].every(e => !e.hasAttribute('data-mascara'))"), 'as células de taxa (%) e prazo ficam sem máscara')
    i0 = pg.evaluate("(() => { const e = [...document.querySelectorAll('#wrapCondicoes .gw-cin[data-campo=\"tarifa\"]')].filter(x => x.offsetParent)[0]; return e ? Number(e.getAttribute('data-i')) : -1; })()")
    ok(i0 >= 0, 'há uma célula de tarifa visível')
    if i0 >= 0:
        sel = '#wrapCondicoes .gw-cin[data-campo="tarifa"][data-i="%d"]' % i0
        digita(pg, sel, '123456'); pg.wait_for_timeout(150)
        ok(val(pg, sel) == '1.234,56' and pg.evaluate("gwNum(G.condicoes[%d].tarifa)" % i0) == 1234.56, 'a tarifa fica 1.234,56 no campo e 1234,56 na leitura: %s' % pg.evaluate("G.condicoes[%d].tarifa" % i0))
    pg.close()

    print('\n    Conferência de Saída: peso aferido')
    pg = nova(); abre(pg, 'pagina-logistica-conferencia-saida-detalhe.html', '?id=1', 600)
    sel = '[data-peso="0"]'
    ok(pg.get_attribute(sel, 'data-mascara') == 'peso', 'o peso aferido do volume tem data-mascara="peso"')
    digita(pg, sel, '1500'); ok(val(pg, sel) == '1,500', 'digitar 1500 dá 1,500: %s' % val(pg, sel))
    digita(pg, sel, '1234567'); ok(val(pg, sel) == '1.234,567' and pg.evaluate("VOLUMES[0].peso") == '1.234,567', 'digitar 1234567 dá 1.234,567 e a tela guarda assim (a sanitização da tela deixa o ponto passar): %s' % pg.evaluate("VOLUMES[0].peso"))
    pg.close()

    print('\n    Devolução (detalhe): frete e peso reais com milhar')
    pg = nova(); abre(pg, 'pagina-logistica-devolucao-detalhe.html', '?id=1', 600)
    ok(pg.locator('#inputFreteReal').count() == 1 and pg.get_attribute('#inputFreteReal', 'data-mascara') == 'dinheiro' and pg.get_attribute('#inputPesoReal', 'data-mascara') == 'peso',
       'os dois campos da cobrança real têm a máscara')
    pg.close()

    # ------------------------------------------------------------------ 6
    print('\n[6] O bloco é igual em toda cópia, e só está onde há campo')
    hashes, com_bloco, com_campo, sem_bloco = {}, [], [], []
    for caminho in localiza.caminhos():
        t = open(caminho, encoding='utf-8', newline='').read().replace('\r\n', '\n').replace('--&gt;', '-->')
        nome = os.path.basename(caminho)
        i = t.find('<!-- MASCARA DE DIGITACAO')
        tem_campo = bool(re.search(r'data-mascara=', t))
        if i >= 0:
            fim = t.find('<!-- /MASCARA DE DIGITACAO -->', i)
            hashes[nome] = hashlib.sha256(t[i:fim].encode('utf-8')).hexdigest()[:12]
            com_bloco.append(nome)
        if tem_campo and i < 0: sem_bloco.append(nome)
        if tem_campo: com_campo.append(nome)
    ok(len(set(hashes.values())) == 1, 'as %d cópias do bloco são idênticas (%d versões diferentes)' % (len(hashes), len(set(hashes.values()))))
    ok(not sem_bloco, 'toda tela com data-mascara tem o bloco: faltam %s' % sem_bloco)
    ok(sorted(com_bloco) == sorted(com_campo), 'e o bloco só está onde há campo com máscara (%d telas)' % len(com_bloco))
    ok(set(com_campo) == set(MAPA), 'e o mapa desta suíte lista exatamente essas telas: %s' % sorted(set(com_campo) ^ set(MAPA)))

    ok(not erros, 'sem erro de JS em nenhum dos fluxos: %s' % erros[:3])
    b.close()

print('\nASSERCOES: %d' % total[0])
print('FALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)
raise SystemExit(1 if falhas else 0)
