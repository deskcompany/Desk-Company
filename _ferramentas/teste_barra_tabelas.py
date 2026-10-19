# A varredura da barra de rolagem — 19/out/2026.
#
# A regra do design system (§14.86): nenhuma tabela rola na horizontal de 1280px de janela para cima, e a pagina
# nunca rola na horizontal. Comissoes nasceu cumprindo; o levantamento de 15/out achou 25 de 83 telas antigas
# com tabela rolando a 1280px, e o usuario mandou varrer (§14.88). Esta suite e o que impede a regressao: abre
# TODA tela no estado em que ela abre, a 1280 e a 1440 de largura (900 de altura), e mede a mesma coisa que a
# secao 9 de teste_comissoes.py: cada .estoque-table-wrap e cada .contatos-table visivel (a largura da tabela
# contra a da caixa) e a propria pagina. Uma asserção por tela; a mensagem diz a largura e a medida que estourou.
#
# Desde a segunda rodada de 19/out tambem mede, alem do estado em que a tela abre, os quatro detalhes que so mostram a
# tabela com um registro aberto (?id=1, o primeiro que a lista manda), e mede tambem a .itens-table, a tabela dos itens
# de um documento, que tem a classe e o CSS proprios.
#
# Limite conhecido: fora isso mede so o estado em que a tela abre. Aba, painel, modal e filtro que mudam a tabela tem a
# medida na suite de cada tela (como a secao 9 de teste_comissoes.py).
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_sys_path = _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _sys_path)
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele

MOLDE = 'pagina-molde-referencia.html'   # dois documentos no mesmo arquivo, de proposito
# Telas que o bloco comum nao basta para encolher e que esperam decisao do usuario (§14.88, 19/out): o que as faz rolar nao e
# largura minima e sim texto que nao quebra (selo, chip, linha de apoio, SKU). Ficam fora da regra, e a suite exige que CONTINUEM
# rolando: no dia em que uma passar, ela reprova ate a tela sair desta lista, para a excecao nao ficar esquecida.
PENDENTES = {'pagina-estoque-necessidades-compra.html', 'pagina-vendas-crm.html', 'pagina-vendas-metas.html'}
LARGURAS = (1280, 1440)
# Telas de detalhe: aberta sem ?id= elas dizem "nao encontrado" e escondem a tabela, entao tambem se mede com o registro aberto.
COM_REGISTRO = ['pagina-estoque-ordens-compra-detalhe.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-logistica-rastreamento-detalhe.html',
                'pagina-estoque-controle-estoques-detalhe.html']
MEDE = """(cortes) => {
  const vis = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const r = [];
  document.querySelectorAll('.estoque-table-wrap, .contatos-table, .itens-table').forEach(w => {
    if (!vis(w)) return;
    const eh = w.classList.contains('contatos-table') || w.classList.contains('itens-table');
    const caixa = eh ? w.parentElement : w, tab = eh ? w : w.querySelector('table');
    const larg = Math.round(tab ? tab.scrollWidth : w.scrollWidth), cab = Math.round(caixa.clientWidth);
    if (larg > cab + 1) r.push((w.id || w.className) + ' ' + larg + ' > ' + cab);
  });
  // 19/out: encolher a tabela nao pode cortar o texto do campo de item (o valor nao cabe na caixa).
  if (cortes) document.querySelectorAll('.itens-table tbody input[type=text]').forEach(i => {
    if (vis(i) && i.scrollWidth > i.clientWidth + 1) r.push('campo cortado: ' + i.value + ' ' + i.clientWidth + ' < ' + i.scrollWidth);
  });
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) r.push('a pagina rola');
  return r;
}"""

# Ordem de Compra e Pedido de Venda: em 1280 os campos do item nao cabem inteiros sem barra; o usuario decidiu deixar assim (19/out). Corte medido so em 1440.
CORTE_SO_1440 = {'pagina-estoque-ordens-compra-detalhe.html', 'pagina-vendas-pedidos-detalhe.html'}

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    cod = sys.stdout.encoding or 'utf-8'
    print((('  ok   ' if cond else '  FALHOU  ') + texto).encode(cod, 'replace').decode(cod))
    if not cond:
        falhas.append(texto)


nomes = [n for n in _filtrar(localiza.nomes()) if n != MOLDE]
print('%d telas (e %d detalhes com registro aberto), a %s de largura' % (len(nomes), len([n for n in COM_REGISTRO if n in nomes]), ' e '.join(str(l) for l in LARGURAS)))
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    abrir = [(n, '') for n in nomes] + [(n, '?id=1') for n in COM_REGISTRO if n in nomes]
    for nome, q in abrir:
        # contexto novo por tela: o que uma tela guardou no armazenamento nao chega na seguinte
        ctx = b.new_context(viewport={'width': LARGURAS[0], 'height': 900})
        pg = ctx.new_page()
        com_barra = []
        for largura in LARGURAS:
            pg.set_viewport_size({'width': largura, 'height': 900})
            if largura == LARGURAS[0]:
                pg.goto(localiza.uri(nome) + q); pg.wait_for_load_state('load')
            pg.wait_for_timeout(350)
            cortes = largura >= 1440 or nome not in CORTE_SO_1440
            com_barra += ['%dpx %s' % (largura, i) for i in pg.evaluate(MEDE, cortes)]
        nome += q
        if nome in PENDENTES:
            ok(com_barra, '%s: barra mantida por decisão do usuário (19/out), e ainda rola (se passou, tire da lista PENDENTES): %s' % (nome, '; '.join(com_barra)))
        else:
            ok(not com_barra, '%s: nenhuma tabela rola na horizontal e a página não rola%s' % (nome, (': ' + '; '.join(com_barra)) if com_barra else ''))
        ctx.close()
    b.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
raise SystemExit(1 if falhas else 0)
