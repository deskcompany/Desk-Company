from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

casos = [
    ('pagina-estoque-ordens-compra-detalhe.html', 'dfDataCompra', 'dfDataPrevista', 'inputDataCompra'),
    ('pagina-estoque-entrada-notas-detalhe.html', 'dfEmissao', 'dfEntrada', 'inputEmissao'),
    ('pagina-cadastros-clientes-detalhe.html', 'dfNascimento', None, None),
]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    for arq, df1, df2, dep in casos:
        print(arq)
        pg = b.new_page(viewport={'width':1440,'height':900})
        erros = []
        pg.on('pageerror', lambda e: erros.append(str(e)))
        pg.goto(localiza.uri(arq)); pg.wait_for_timeout(600)
        ok(not erros, '  sem erro de JS: %s' % erros[:2])
        # abrir o primeiro campo (pode estar dentro de aba/painel: forca a exibicao do pai)
        vis = pg.eval_on_selector('#' + df1, "e => { const r = e.getBoundingClientRect(); return r.width > 0; }")
        if not vis:
            pg.evaluate("""(id)=>{let e=document.getElementById(id);while(e&&e!==document.body){const cs=getComputedStyle(e);if(cs.display==='none')e.style.display='block';e=e.parentElement;}}""", df1)
            pg.wait_for_timeout(200)
        pg.click('#' + df1 + ' .date-btn'); pg.wait_for_timeout(300)
        ok(pg.eval_on_selector('#' + df1 + ' .date-pop', "e => e.classList.contains('open')"), '  calendario abre')
        dias = pg.eval_on_selector_all('#' + df1 + ' .date-dia:not(.vazio)', 'e => e.length')
        ok(28 <= dias <= 31, '  %d dias no mes' % dias)
        pg.click('#' + df1 + ' .date-dia[data-iso]'); pg.wait_for_timeout(250)
        ok(pg.eval_on_selector('#' + df1 + ' .date-pop', "e => e.classList.contains('open')") is False, '  fecha ao escolher')
        if df2:
            # o limite so aparece se o primeiro campo tiver uma data no MEIO do mes:
            # com dia 1, nao ha dia anterior no mes visivel para ficar riscado.
            hoje = pg.evaluate("(function(){var h=new Date();return '15/' + String(h.getMonth()+1).padStart(2,'0') + '/' + h.getFullYear()})()")
            pg.fill('#' + dep, hoje); pg.wait_for_timeout(200)
            pg.click('#' + df2 + ' .date-btn'); pg.wait_for_timeout(300)
            riscados = pg.eval_on_selector_all('#' + df2 + ' .date-dia.off', 'e => e.length')
            ok(riscados > 0, '  o segundo campo respeita o limite do primeiro: %d dias riscados' % riscados)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(not erros, '  sem erro de JS ao final: %s' % erros[:2])
        pg.close()
    # 09/out: o CRM nasceu com dois campos de data sem a caixa do calendario. O componente
    # desiste calado quando falta uma das tres pecas, entao o botao existia e nao abria nada.
    print('toda tela: campo de data com botao e caixa')
    pg = b.new_page(viewport={'width':1440,'height':900})
    capengas = []
    for caminho in sorted(localiza.caminhos()):
        if 'date-field' not in open(caminho, encoding='utf-8').read(): continue
        nome = _os.path.basename(caminho)
        pg.goto(localiza.uri(nome)); pg.wait_for_timeout(350)
        n = pg.evaluate("Array.from(document.querySelectorAll('.date-field')).filter(d => !d.querySelector('input') || !d.querySelector('.date-btn') || !d.querySelector('.date-pop')).length")
        if n: capengas.append('%s: %d' % (nome, n))
    ok(not capengas, '  nenhum campo de data sem uma das tres pecas: %s' % capengas[:4])
    # 09/out: na Agenda o calendario abria alinhado pela direita do campo e, como o campo fica
    # colado na borda esquerda do painel, a primeira coluna (domingo) saia cortada. A caixa tem
    # 252px e abria para a esquerda sem medir se cabia. Aqui cada calendario que da para abrir e
    # aberto, e a caixa tem de caber na area que a contem (o painel, ou a janela).
    print('toda tela: calendario aberto cabe na area que o contem')
    ABRIR_ANTES = {'pagina-inicio-agenda.html': "abrirFormulario('2026-10-15')",
                   'pagina-vendas-crm-detalhe.html': "document.querySelector('#acoesPendentes [data-editar-acao]').click()",
                   'pagina-estoque-itens-bloqueados.html': "document.getElementById('btnPeriodo').click()"}
    cortados = []
    for caminho in sorted(localiza.caminhos()):
        if 'date-field' not in open(caminho, encoding='utf-8').read(): continue
        nome = _os.path.basename(caminho)
        pg.goto(localiza.uri(nome)); pg.wait_for_timeout(350)
        # Formulario que nasce escondido nao e medido se ninguem o abrir: a Agenda era o caso.
        if nome in ABRIR_ANTES: pg.evaluate(ABRIR_ANTES[nome]); pg.wait_for_timeout(450)
        achados = pg.evaluate("""() => { const ruins = [];
            document.querySelectorAll('.date-field').forEach(df => {
              const btn = df.querySelector('.date-btn'), pop = df.querySelector('.date-pop');
              if (!btn || !pop || pop.classList.contains('hora-pop') || df.getBoundingClientRect().width === 0) return;
              btn.click();
              if (!pop.classList.contains('open')) return;
              const r = pop.getBoundingClientRect();
              let lim = { left: 0, right: window.innerWidth, nome: 'janela' };
              for (let el = df.parentElement; el && el !== document.body; el = el.parentElement) {
                const o = getComputedStyle(el);
                if (/(auto|scroll|hidden)/.test(o.overflowX + ' ' + o.overflowY)) { const c = el.getBoundingClientRect(); lim = { left: c.left, right: c.right, nome: el.id || String(el.className).split(' ')[0] }; break; }
              }
              if (r.left < lim.left - 0.5 || r.right > lim.right + 0.5) ruins.push((df.id || '?') + ' em ' + lim.nome + ' (' + Math.round(Math.max(lim.left - r.left, r.right - lim.right)) + 'px)');
              btn.click();
            });
            return ruins; }""")
        if achados: cortados.append('%s: %s' % (nome.replace('pagina-', '').replace('.html', ''), ', '.join(achados)))
    ok(not cortados, '  nenhum calendario cortado: %s' % cortados[:6])
    # 10/out: o popover de periodo ficava aberto por baixo do dropdown vizinho (print do usuario em
    # Tratamento de Perdas). Os dropdowns param a propagacao do clique, e o fechamento geral da tela
    # nunca chegava ao popover. Das dez telas com filtro de periodo, o defeito estava em quatro:
    # Tratamento de Perdas, Devolucao, Expedicao e Rastreamento. Nas outras seis o proprio dropdown
    # ja fechava o periodo. A primeira conta dizia dez; a prova do avesso em Entrada de Notas
    # passou sem acusar nada, e foi medindo tela por tela que o numero certo apareceu.
    print('toda tela com filtro de periodo: abrir outro menu fecha o de periodo')
    juntos, medidas = [], 0
    for caminho in sorted(localiza.caminhos()):
        if 'class="periodo-menu"' not in open(caminho, encoding='utf-8').read(): continue
        nome = _os.path.basename(caminho)
        pg.goto(localiza.uri(nome)); pg.wait_for_timeout(350)
        pg.click('.periodo-wrap > button'); pg.wait_for_timeout(200)
        abriu = pg.locator('.periodo-menu.open').count() == 1
        tem = pg.evaluate("(() => { const b = Array.from(document.querySelectorAll('.dropdown-select .dropdown-select-btn')).find(x => !x.closest('.periodo-wrap') && x.offsetParent !== null && !x.disabled && !x.closest('.event-drawer') && !x.closest('.paginacao-bar')); if (b) b.setAttribute('data-vizinho', '1'); return !!b; })()")
        if not (abriu and tem): juntos.append('%s: nao deu para medir' % nome); continue
        pg.click('[data-vizinho]'); pg.wait_for_timeout(250)
        medidas += 1
        if pg.locator('.periodo-menu.open').count(): juntos.append(nome.replace('pagina-', '').replace('.html', ''))
    ok(medidas >= 10 and not juntos, '  em %d telas, nenhuma deixa os dois abertos juntos: %s' % (medidas, juntos[:5]))
    pg.close()
    b.close()
print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
