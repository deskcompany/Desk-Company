# -*- coding: utf-8 -*-
# Revisao geral de 16/nov/2026, pacote A: os blocos de interacao do sistema todo.
#   [1] Item 14: o menu que nao cabe embaixo na janela abre para cima (o "Adicionar recebimento (F4)" do PDV no pe da tela).
#   [2] Item 5: com o painel lateral aberto a pagina de tras nao rola, e volta ao mesmo ponto ao fechar.
#   [3] Item 12: a bolinha das opcoes de marcar e a dos itens de lista centradas, nos dois temas.
# A correcao do custo do minimo no detalhe da promocao tem a assercao em teste_promocoes.py (secao 13).
from playwright.sync_api import sync_playwright
import os, sys
import localiza
FOTOS = os.environ.get('DESK_FOTOS')
SO = (sys.argv[1:] or [''])[0]
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


def texto(caminho):
    return open(caminho, encoding='utf-8').read()


def foto(pg, nome):
    if FOTOS:
        pg.screenshot(path=os.path.join(FOTOS, nome))


with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('dialog', lambda d: d.dismiss())

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(250)

    def clica(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(150)

    def tema(t):
        pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", t)

    def pdv_na_cobranca():
        ir('pagina-vendas-pdv.html'); pg.evaluate("localStorage.removeItem('deskPdv'); localStorage.setItem('deskParametros', JSON.stringify({ pdvDescontoAVista: false }))"); ir('pagina-vendas-pdv.html')
        clica('#btnAbrirCaixa'); clica('#abrirLoja .dropdown-select-btn')
        pg.evaluate("document.querySelector('#abrirLoja .dropdown-select-item[data-value=\"1\"]').click()"); pg.wait_for_timeout(150)
        pg.fill('#abrirTroco', '100'); clica('#btnConfirmarAbertura'); pg.wait_for_timeout(250)
        pg.fill('#qtdProduto', '1'); pg.fill('#buscaProduto', 'PAP-3002'); pg.locator('#buscaProduto').press('Enter'); pg.wait_for_timeout(250)
        clica('#btnContinuar'); pg.wait_for_timeout(300)

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'O menu que não cabe embaixo abre para cima'):
        for alt in (900, 560):
            pg.set_viewport_size({'width': 1440, 'height': alt}); pdv_na_cobranca()
            for t in ('light', 'dark'):
                tema(t)
                pg.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)"); pg.wait_for_timeout(150)
                clica('#selAddReceb .dropdown-select-btn'); pg.wait_for_timeout(250)
                r = pg.evaluate("(() => { const m = document.querySelector('#selAddReceb .dropdown-select-menu'), b = document.querySelector('#selAddReceb .dropdown-select-btn').getBoundingClientRect(), x = m.getBoundingClientRect(); return [m.classList.contains('open'), m.classList.contains('abrir-para-cima'), Math.round(x.top), Math.round(x.bottom), innerHeight, Math.round(b.top), Math.round(b.bottom), x.top >= b.bottom - 1 || x.bottom <= b.top + 1]; })()")
                ok(r[0] and r[2] >= 0 and r[3] <= r[4] and r[7], 'PDV com a venda no pé da tela (%dpx, tema %s): o "Adicionar recebimento (F4)" abre inteiro dentro da janela e sem cobrir o botão: %s' % (alt, t, r))
                foto(pg, 'menu_f4_%d_%s.png' % (alt, t))
                pg.evaluate("document.body.click()"); pg.wait_for_timeout(100)
        pg.set_viewport_size({'width': 1440, 'height': 900})
        # menu com espaço sobrando embaixo continua para baixo
        ir('pagina-vendas-pedidos.html'); pg.evaluate("window.scrollTo(0, 0)")
        clica('#filtroSituacao .dropdown-select-btn'); pg.wait_for_timeout(200)
        r = pg.evaluate("(() => { const m = document.querySelector('#filtroSituacao .dropdown-select-menu'), x = m.getBoundingClientRect(); return [m.classList.contains('open'), m.classList.contains('abrir-para-cima'), Math.round(x.bottom) <= innerHeight]; })()")
        ok(r == [True, False, True], 'com espaço embaixo o menu continua abrindo para baixo: %s' % r)
        velha = [os.path.basename(x) for x in localiza.caminhos() if '!!_fixo && espacoAbaixo' in texto(x)]
        ok(not velha, 'nenhuma tela guarda a regra antiga (só painel fixo abre para cima): %s' % velha[:3])

    # ------------------------------------------------------------------------------------------------
    if secao(2, 'Painel lateral aberto: a página de trás não rola'):
        sem = [os.path.basename(x) for x in localiza.caminhos() if 'html:has(.drawer-backdrop.open) { overflow:hidden; }' not in texto(x)]
        ok(not sem, 'o bloco está nas %d telas (todas têm o painel): faltam %s' % (len(localiza.caminhos()), sem[:3]))
        for tela in ('pagina-vendas-pedidos.html', 'pagina-cadastros-produtos.html'):
            ir(tela)
            pg.evaluate("document.body.style.minHeight = '3000px'; window.scrollTo(0, 400)"); pg.wait_for_timeout(150)
            antes = pg.evaluate("scrollY")
            pg.evaluate("document.querySelector('.drawer-backdrop').classList.add('open')"); pg.wait_for_timeout(150)
            pg.mouse.move(200, 400); pg.mouse.wheel(0, 600); pg.wait_for_timeout(250)
            dentro = pg.evaluate("scrollY")
            foto(pg, 'painel_trava_%s.png' % tela.replace('.html', ''))
            pg.evaluate("document.querySelector('.drawer-backdrop').classList.remove('open')"); pg.wait_for_timeout(150)
            depois = pg.evaluate("scrollY")
            pg.mouse.wheel(0, 300); pg.wait_for_timeout(250)
            volta = pg.evaluate("scrollY")
            ok(antes == 400 and dentro == 400 and depois == 400 and volta > 400,
               '%s: a roda do mouse não mexe na página com o painel aberto (%s), fecha no mesmo ponto (%s) e a rolagem volta (%s)' % (tela, dentro, depois, volta))

    # ------------------------------------------------------------------------------------------------
    if secao(3, 'A bolinha centralizada, nos dois temas'):
        velho = [os.path.basename(x) for x in localiza.caminhos() if 'left:3px; top:3px; width:7px' in texto(x)]
        ok(not velho, 'nenhuma tela guarda o marcador da opção com posição à mão: %s' % velho[:3])
        ir('pagina-vendas-pdv.html')
        for t in ('light', 'dark'):
            tema(t)
            r = pg.evaluate("""(() => {
              const d = document.createElement('div'); d.id = 'tmpA'; d.style.cssText = 'position:fixed;top:20px;left:20px;width:560px;z-index:9999;background:var(--panel-bg);padding:12px';
              d.innerHTML = '<label class="radio-option pdv-opcao"><input type="radio" name="tmpA" checked> Desconto</label><label class="radio-option pdv-opcao"><input type="radio" name="tmpA"> Acréscimo</label>'
                + '<div class="pdv-gerado"><span class="pdv-gerado-ponto"></span><span>Um título a receber de <b>R$ 10,00</b>, com a taxa e a data que cabem em mais de uma linha de texto para ver o ponto na primeira linha e nada mais</span></div><div class="pdv-gerado"><span class="pdv-gerado-ponto"></span><span>Uma linha só</span></div>';
              document.body.appendChild(d);
              const i = d.querySelector('input'), c = getComputedStyle(i, '::after');
              const folga = (i.clientWidth - parseFloat(c.width)) / 2;
              const pontos = Array.from(d.querySelectorAll('.pdv-gerado')).map(g => { const a = g.children[0].getBoundingClientRect(); const s = g.children[1].getBoundingClientRect(); return Math.abs((a.top + a.height / 2) - (s.top + parseFloat(getComputedStyle(g).lineHeight) / 2)); });
              return [parseFloat(c.marginLeft) - folga, parseFloat(c.marginTop) - folga, parseFloat(c.left), parseFloat(c.top), Math.max.apply(null, pontos)];
            })()""")
            ok(abs(r[0]) < 0.05 and abs(r[1]) < 0.05 and r[2] == 0 and r[3] == 0, 'tema %s: a bolinha da opção fica no meio da caixa (folga igual dos quatro lados): %s' % (t, r[:4]))
            ok(r[4] < 0.6, 'tema %s: o ponto da lista fica no meio da primeira linha do texto (desvio de %.2fpx do meio da linha)' % (t, r[4]))
            foto(pg, 'bolinhas_%s.png' % t)
            pg.evaluate("document.getElementById('tmpA').remove()")

    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
