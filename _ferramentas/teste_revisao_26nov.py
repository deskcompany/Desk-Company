# -*- coding: utf-8 -*-
# Revisao geral de 26/nov/2026 — os quatro itens do pedido dele:
#   (1) data escrita DD/MM/AAAA, em maiusculas, em todo texto que a pessoa ve;
#   (2) o dia bloqueado do calendario fica so apagado, sem o risco no meio;
#   (3) a acao da linha de item e botao de icone (lapis, lixeira) com aria-label, nao texto solto;
#   (4) lista suspensa aberta trava a rolagem da pagina (roda e toque fora do menu), e o menu rola por dentro.
# Roda por endereco de arquivo e respeita DESK_PASTA (copia do projeto para provar o defeito plantado).
from playwright.sync_api import sync_playwright
import os, re, glob
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

falhas = []
total = [0]
def ok(c, m):
    total[0] += 1
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def codigo(arq):
    """Texto do arquivo sem as linhas que sao so comentario de JS."""
    t = open(localiza.onde(arq), encoding='utf-8').read()
    return '\n'.join(l for l in t.split('\n') if not l.lstrip().startswith('//'))

nomes = [n for n in localiza.nomes()]

# ---------------------------------------------------------------- (1) datas em maiusculas
print('\n[1] Data escrita DD/MM/AAAA, em maiusculas')
com_minusculo = [n for n in nomes if 'dd/mm/aaaa' in codigo(n)]
ok(not com_minusculo, '%d telas conferidas: nenhuma escreve "dd/mm/aaaa" em minusculo%s' % (
    len(nomes), (' — ' + ', '.join(com_minusculo[:4])) if com_minusculo else ''))
com_padrao = [n for n in nomes if 'DD/MM/AAAA' in codigo(n)]
ok(len(com_padrao) >= 20, '%d telas mostram DD/MM/AAAA (esperado ao menos 20)' % len(com_padrao))

# ---------------------------------------------------------------- (2) dia bloqueado sem o risco
print('\n[2] Dia bloqueado do calendario sem o risco')
regra = re.compile(r'^\s*\.date-dia\.off \{[^}]*\}', re.M)
com_calendario, riscadas = [], []
for n in nomes:
    t = open(localiza.onde(n), encoding='utf-8').read()
    for m in regra.finditer(t):
        com_calendario.append(n)
        if 'line-through' in m.group(0) or 'underline' in m.group(0):
            riscadas.append(n)
ok(len(com_calendario) >= 29, '%d telas tem o calendario com o dia bloqueado (esperado ao menos 29)' % len(com_calendario))
ok(not riscadas, 'nenhuma regra de .date-dia.off tem risco%s' % ((' — ' + ', '.join(riscadas[:4])) if riscadas else ''))

REAL = """(raiz) => { const e = document.querySelector(raiz + ' .date-dia.off');
  if (!e) return null; const c = getComputedStyle(e); return [c.textDecorationLine, c.cursor, parseFloat(c.opacity), e.hasAttribute('data-iso')]; }"""

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    ctx = b.new_context(viewport={'width': 1280, 'height': 900})
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    def abre(arq, q='', espera=450):
        erros.clear()
        pg.goto(localiza.uri(arq) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(espera)

    # calendario aberto de verdade, num dia que o proprio calendario trava
    for arq, raiz in [('pagina-vendas-promocoes-detalhe.html', '#dfFim'), ('pagina-estoque-movimentacao.html', '#dfDataDe'),
                      ('pagina-estoque-ordens-compra-detalhe.html', '#dfDataPrevista')]:
        abre(arq, espera=300)
        pg.click(raiz + ' .date-btn'); pg.wait_for_timeout(300)
        r = pg.evaluate(REAL, raiz)
        ok(r is not None and r[0] == 'none' and r[1] == 'not-allowed' and r[2] < 0.5 and r[3] is False,
           '%s %s: dia travado no calendario aberto fica so apagado, sem risco e sem clique: %s' % (arq, raiz, r))

    # ------------------------------------------------------------ (3) acoes da linha viram botao
    print('\n[3] Acoes da linha de item: botao de icone com aria-label')
    TEXTO_SOLTO = """() => [...document.querySelectorAll('#corpoItens td span, #corpoItens td a, #corpoItens td div')]
      .filter(e => /^(editar|remover|limpar|excluir)$/i.test(e.textContent.trim())).length"""

    # Pedido de Venda
    abre('pagina-vendas-pedidos-detalhe.html')
    pg.click('#btnEditarRegistro'); pg.wait_for_timeout(250)
    n0 = pg.locator('#corpoItens tr').count()
    ok(n0 >= 2, 'Pedido de Venda: %d itens na tabela' % n0)
    ok(pg.locator('#corpoItens tr .btn-icone-linha[aria-label="Editar item"]').count() == n0
       and pg.locator('#corpoItens tr .btn-icone-linha[aria-label="Remover item"]').count() == n0,
       'Pedido de Venda: cada linha tem Editar item e Remover item, com aria-label')
    ok(pg.locator('#corpoItens .btn-icone-linha[title="Editar item"]').count() == n0
       and pg.locator('#corpoItens .btn-icone-linha[title="Remover item"]').count() == n0,
       'Pedido de Venda: os dois tem title (a dica ao passar o mouse)')
    ok(pg.evaluate(TEXTO_SOLTO) == 0, 'Pedido de Venda: nenhuma acao em texto solto na tabela')
    tam = pg.evaluate("(() => { const r = document.querySelector('#corpoItens .btn-icone-linha').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })()")
    ok(tam == [28, 28], 'Pedido de Venda: botao de 28x28 (%s)' % tam)
    cor = pg.evaluate("getComputedStyle(document.querySelector('#corpoItens .btn-icone-linha.perigo')).color")
    pg.hover('#corpoItens tr:nth-child(1) .btn-icone-linha.perigo'); pg.wait_for_timeout(150)
    cor_hover = pg.evaluate("getComputedStyle(document.querySelector('#corpoItens .btn-icone-linha.perigo')).color")
    ok(cor_hover != cor, 'Pedido de Venda: a lixeira muda para o tom de erro ao passar o mouse (%s)' % cor_hover)
    # foco visivel pelo teclado: Tab ate o botao
    pg.click('#corpoItens tr:nth-child(1) input[data-campo="precoLista"]')
    achou = False
    for _ in range(6):
        pg.keyboard.press('Tab')
        if pg.evaluate("document.activeElement.classList.contains('btn-icone-linha')"):
            achou = True; break
    ok(achou, 'Pedido de Venda: o Tab chega no botao de icone')
    ok(achou and pg.evaluate("getComputedStyle(document.activeElement).outlineStyle") == 'solid',
       'Pedido de Venda: foco pelo teclado desenha o contorno')
    pg.click('#corpoItens tr:nth-child(1) [data-editar]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#eventDrawer', 'e => e.classList.contains("open")'), 'Pedido de Venda: o lapis abre o painel do item (o clique faz o que fazia)')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    nome1 = pg.evaluate("ITENS[1].sku")
    pg.click('#corpoItens tr:nth-child(1) [data-remover]'); pg.wait_for_timeout(300)
    n1 = pg.locator('#corpoItens tr').count()
    ok(n1 == n0 - 1 and pg.evaluate("ITENS[0].sku") == nome1,
       'Pedido de Venda: clicar na lixeira remove a linha (%d -> %d) e o item de baixo sobe' % (n0, n1))
    ok(not erros, 'Pedido de Venda: sem erro de JS' + (' — ' + erros[0] if erros else ''))

    # Entrada de Notas
    abre('pagina-estoque-entrada-notas-detalhe.html')
    pg.click('#btnAdicionarItem'); pg.wait_for_timeout(250)
    pg.click('#btnAdicionarItem'); pg.wait_for_timeout(250)
    e0 = pg.locator('#corpoItens tr').count()
    ok(e0 >= 2, 'Entrada de Notas: %d itens na tabela' % e0)
    ok(pg.locator('#corpoItens tr .btn-icone-linha[aria-label="Remover item"]').count() == e0
       and pg.locator('#corpoItens .btn-icone-linha[title="Remover item"]').count() == e0,
       'Entrada de Notas: cada linha tem Remover item, com aria-label e title')
    ok(pg.evaluate(TEXTO_SOLTO) == 0, 'Entrada de Notas: nenhuma acao em texto solto na tabela')
    pg.click('#corpoItens tr:nth-child(1) [data-remover]'); pg.wait_for_timeout(300)
    e1 = pg.locator('#corpoItens tr').count()
    ok(e1 == e0 - 1, 'Entrada de Notas: clicar na lixeira remove a linha (%d -> %d)' % (e0, e1))
    ok(not erros, 'Entrada de Notas: sem erro de JS' + (' — ' + erros[0] if erros else ''))

    # Ordem de Compra, Conferencia e Acerto: so a presenca dos botoes com aria-label
    abre('pagina-estoque-ordens-compra-detalhe.html', '?id=1')
    oc = pg.locator('#corpoItens tr').count()
    ok(oc >= 1 and pg.locator('#corpoItens tr .btn-icone-linha[aria-label="Remover item"]').count() == oc and pg.evaluate(TEXTO_SOLTO) == 0,
       'Ordem de Compra: %d linhas, todas com Remover item (aria-label) e nenhuma em texto solto' % oc)
    pg.click('#corpoItens tr:nth-child(1) [data-remover]'); pg.wait_for_timeout(300)
    ok(pg.locator('#corpoItens tr').count() == oc - 1, 'Ordem de Compra: a lixeira remove a linha')
    abre('pagina-estoque-conferencia.html')
    cf = pg.locator('#corpoItens tr').count()
    ok(cf >= 1 and pg.locator('#corpoItens tr .btn-icone-linha[aria-label="Limpar a contagem do item"]').count() == cf and pg.evaluate(TEXTO_SOLTO) == 0,
       'Conferencia de Estoque: %d linhas, todas com o botao Limpar a contagem (aria-label)' % cf)
    abre('pagina-estoque-acerto.html')
    pg.evaluate("""() => { if (typeof LINHAS !== 'undefined' && LINHAS.length === 0) {
        LINHAS.push({ sku:'X-1', nome:'Item de teste', motivoLabel:'Ajuste', onde:'Deposito', tipo:'saida', qtd:1, unidade:'UN', fiscal:'', obs:'' }); }
        if (typeof renderLinhas === 'function') renderLinhas(); }""")
    ac = pg.locator('#corpoLinhas [data-remover]').count()
    ok(ac >= 1 and pg.locator('#corpoLinhas .btn-icone-linha[data-remover][aria-label="Remover esta linha"]').count() == ac and pg.evaluate("[...document.querySelectorAll('#corpoLinhas [data-remover]')].every(e => e.tagName === 'BUTTON')"),
       'Acerto de Estoque: %d linhas, todas com botao Remover esta linha (aria-label)' % ac)
    pg.click('#corpoLinhas [data-remover]'); pg.wait_for_timeout(250)
    ok(pg.locator('#corpoLinhas tr').count() == ac - 1, 'Acerto de Estoque: a lixeira remove a linha')

    # ------------------------------------------------------------ (4) lista suspensa trava a rolagem
    print('\n[4] Lista suspensa aberta trava a rolagem da pagina')
    CASOS = [('pagina-financas-caixa.html', '#filtroCategoria', 'Escape'), ('pagina-estoque-entrada-notas-detalhe.html', '#inputCondicao', 'clique')]
    for arq, sel, fecha in CASOS:
        abre(arq)
        pg.evaluate("window.scrollTo(0, 120)"); pg.wait_for_timeout(200)
        pg.click(sel + ' .dropdown-select-btn'); pg.wait_for_timeout(300)
        menu = sel + ' .dropdown-select-menu'
        ok(pg.evaluate("document.querySelector('%s').classList.contains('open')" % menu), '%s: a lista abre' % arq)
        sy = pg.evaluate("window.scrollY")
        cx = pg.evaluate("(() => { const r = document.querySelector('%s').getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; })()" % menu)
        comprido = pg.evaluate("(() => { const m = document.querySelector('%s'); return m.scrollHeight > m.clientHeight + 20; })()" % menu)
        ok(comprido, '%s: a lista e comprida o bastante para rolar por dentro' % arq)
        # a roda sobre a pagina, fora do menu (ao lado dele, no meio do conteudo)
        fora = (min(1250, cx[2] + 300), max(120, min(700, (cx[1] + cx[3]) / 2)))
        pg.mouse.move(fora[0], fora[1]); pg.mouse.wheel(0, 500); pg.wait_for_timeout(350)
        ok(pg.evaluate("window.scrollY") == sy, '%s: roda sobre a pagina com a lista aberta nao rola a pagina (%s -> %s)' % (arq, sy, pg.evaluate("window.scrollY")))
        # dentro do menu a rolagem funciona e nao passa para a pagina
        pg.mouse.move((cx[0] + cx[2]) / 2, (cx[1] + cx[3]) / 2); pg.mouse.wheel(0, 90); pg.wait_for_timeout(300)
        st = pg.evaluate("document.querySelector('%s').scrollTop" % menu)
        ok(st > 0, '%s: a roda sobre a lista rola a lista por dentro (scrollTop %s)' % (arq, st))
        for _ in range(6):
            pg.mouse.wheel(0, 400); pg.wait_for_timeout(120)
        pg.wait_for_timeout(250)
        ok(pg.evaluate("window.scrollY") == sy, '%s: no fim da lista a roda nao escapa para a pagina (%s)' % (arq, pg.evaluate("window.scrollY")))
        toque_fora = pg.evaluate("(() => { const e = new Event('touchmove', { bubbles: true, cancelable: true }); document.querySelector('.main, body').dispatchEvent(e); return e.defaultPrevented; })()")
        ok(toque_fora, '%s: o toque arrastando fora da lista nao rola a pagina' % arq)
        toque_dentro = pg.evaluate("(() => { const e = new Event('touchmove', { bubbles: true, cancelable: true }); document.querySelector('%s .dropdown-select-item').dispatchEvent(e); return e.defaultPrevented; })()" % menu)
        ok(not toque_dentro, '%s: o toque arrastando dentro da lista segue livre' % arq)
        ok(pg.evaluate("getComputedStyle(document.querySelector('%s')).overscrollBehaviorY" % menu) == 'contain', '%s: a lista tem overscroll-behavior: contain' % arq)
        ok(pg.evaluate("getComputedStyle(document.body).overflow") != 'hidden', '%s: o body nao ganha overflow:hidden (a barra nao some)' % arq)
        # fecha e libera tudo
        if fecha == 'Escape':
            pg.keyboard.press('Escape')
        else:
            pg.mouse.click(fora[0], 60)
        pg.wait_for_timeout(250)
        ok(not pg.evaluate("!!document.querySelector('.dropdown-select-menu.open')"), '%s: a lista fecha (%s)' % (arq, fecha))
        pg.evaluate('window.scrollTo(0, 0)'); sy = 0
        pg.mouse.move(fora[0], fora[1]); pg.mouse.wheel(0, 300); pg.wait_for_timeout(400)
        ok(pg.evaluate("window.scrollY") > sy, '%s: fechada a lista, a roda volta a rolar a pagina (%s -> %s)' % (arq, sy, pg.evaluate("window.scrollY")))
        toque_livre = pg.evaluate("(() => { const e = new Event('touchmove', { bubbles: true, cancelable: true }); document.body.dispatchEvent(e); return e.defaultPrevented; })()")
        ok(not toque_livre, '%s: fechada a lista, o toque volta a rolar a pagina' % arq)
        ok(not erros, '%s: sem erro de JS' % arq + (' — ' + erros[0] if erros else ''))

    # o bloco existe igual em todas as telas que tem a lista suspensa
    blocos = set(); sem_bloco = []
    for n in nomes:
        t = open(localiza.onde(n), encoding='utf-8', newline='').read().replace(chr(13), '')   # tres telas tem fim de linha CRLF
        if 'function inicializarDropdownSelect' not in t:
            continue
        i = t.find('function travarRolagemComListaAberta')
        if i < 0: sem_bloco.append(n); continue
        blocos.add(t[i:t.find("{ passive: false });\n", t.find("addEventListener('touchmove'", i)) + 20])
    ok(not sem_bloco and len(blocos) == 1, 'a trava existe, igual, em toda tela com lista suspensa (%d versoes, %d sem)' % (len(blocos), len(sem_bloco)))
    b.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
raise SystemExit(1 if falhas else 0)
