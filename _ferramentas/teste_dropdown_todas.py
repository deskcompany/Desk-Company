# O componente de dropdown foi trocado em 51 telas. Teste que clica de verdade em
# CADA uma: o script de auditoria confirma que nao ha erro de JS no carregamento,
# mas so o clique prova que o dropdown abre, escolhe e fecha.
from playwright.sync_api import sync_playwright
import os, sys, glob
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
import sys as _sys, os as _os2
_sys.path.insert(0, _os2.path.dirname(_os2.path.abspath(__file__)))
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

falhas = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    arquivos = _filtrar(sorted(localiza.caminhos()))
    testadas = 0
    for arq in arquivos:
        nome = os.path.basename(arq)
        erros = []
        pg.on('pageerror', lambda e, box=erros: box.append(str(e)))
        try:
            pg.goto(localiza.uri(arq))
        except Exception:
            pg.wait_for_timeout(600)
            pg.goto(localiza.uri(arq))
        pg.wait_for_timeout(420)
        # primeiro dropdown visivel da tela
        idx = pg.evaluate("""(function(){
          var ds = document.querySelectorAll('.dropdown-select');
          for (var i = 0; i < ds.length; i++) {
            var d = ds[i], btn = d.querySelector('.dropdown-select-btn'), menu = d.querySelector('.dropdown-select-menu');
            if (!btn || !menu) continue;
            if (btn.offsetParent === null || btn.disabled) continue;
            if (!menu.querySelectorAll('.dropdown-select-item').length) continue;
            // `offsetParent` nao basta: dropdown dentro de painel lateral FECHADO
            // (deslocado para fora da tela) ainda tem offsetParent. Exigir que o
            // PROPRIO botao responda ao clique no ponto dele — se o usuario nao
            // alcanca o botao, nao faz sentido cobrar que o menu apareca.
            var cb = btn.getBoundingClientRect();
            var sobre = document.elementFromPoint(cb.left + cb.width / 2, cb.top + cb.height / 2);
            if (!sobre || !btn.contains(sobre)) continue;
            return i;
          }
          return -1;
        })()""")
        if idx == -1:
            pg.remove_listener('pageerror', lambda e: None) if False else None
            continue
        testadas += 1
        sel = '.dropdown-select:nth-of-type(1)'
        est = pg.evaluate("""(function(i){
          var d = document.querySelectorAll('.dropdown-select')[i];
          var btn = d.querySelector('.dropdown-select-btn'), menu = d.querySelector('.dropdown-select-menu');
          var label = d.querySelector('.dropdown-select-label');
          btn.click();
          var abriu = menu.classList.contains('open');
          // ABRIR NAO E APARECER. Em 30/set o menu "mais" das abas de Pedidos de
          // Venda abria no DOM e ficava invisivel, recortado por um
          // `overflow:hidden` do container — o usuario clicava e nada acontecia,
          // e o teste passava porque so olhava classe. A assercao certa e a do
          // dedo do usuario: `elementFromPoint` no centro do primeiro item.
          var primeiro = menu.querySelector('.dropdown-select-item');
          var caixa = primeiro ? primeiro.getBoundingClientRect() : null;
          var noPonto = caixa ? document.elementFromPoint(caixa.left + caixa.width / 2, caixa.top + caixa.height / 2) : null;
          var apareceu = !!(primeiro && noPonto && primeiro.contains(noPonto));
          var todos = Array.prototype.slice.call(menu.querySelectorAll('.dropdown-select-item'));
          // Item de acao ("+ Adicionar nova categoria") nao guarda selecao: ele
          // executa e repoe o rotulo. Preferir um item normal quando existir.
          var normais = todos.filter(function (x) { return !x.classList.contains('dropdown-acao'); });
          var alvo = (normais.length ? normais : todos)[(normais.length ? normais : todos).length - 1];
          var eraAcao = alvo.classList.contains('dropdown-acao');
          var valorAntes = d.getAttribute('data-value');
          var rotuloAntes = label ? label.textContent : '';
          var esperadoVal = alvo.getAttribute('data-value');
          alvo.click();
          var valorDepois = d.getAttribute('data-value');
          // MENU DE ACOES ("Ações", "Mais ações"): nao guarda escolha nenhuma —
          // continua vazio e repoe o rotulo, para a mesma acao poder ser
          // escolhida de novo. Contrato diferente, igualmente correto.
          var menuDeAcoes = (!valorAntes && !valorDepois) || eraAcao;
          // O CONTRATO do componente e gravar o data-value escolhido na raiz.
          // O rotulo NAO serve de asserçao: menu de acoes ("Ações", "Mais ações")
          // e item de acao ("+ Adicionar nova categoria") repoem o rotulo de
          // proposito depois do callback — e isso e correto, nao defeito.
          return { abriu: abriu, apareceu: apareceu, fechou: !menu.classList.contains('open'),
                   acoes: menuDeAcoes,
                   gravou: menuDeAcoes ? (label ? label.textContent === rotuloAntes : true)
                                       : (esperadoVal === null || valorDepois === esperadoVal),
                   id: d.id, itemVal: esperadoVal, valor: valorDepois };
        })(%d)""" % idx)
        if not est['abriu']: falhas.append(nome + ': o dropdown nao abriu no clique')
        if est['abriu'] and not est['apareceu']:
            falhas.append(nome + ': o menu abriu mas nao APARECE — recortado ou coberto (veja overflow do pai)')
        if not est['fechou']: falhas.append(nome + ': nao fechou ao escolher (sintoma de bind duplicado)')
        if not est['gravou']:
            falhas.append('%s: %s %s (%s -> %s)' % (nome, est['id'],
                'menu de acoes nao repos o rotulo' if est['acoes'] else 'nao gravou o valor escolhido',
                est['itemVal'], est['valor']))
        if erros: falhas.append(nome + ': erro de JS -> ' + erros[0][:90])
        # Item de menu de acoes pode NAVEGAR, e isso e legitimo: "Abrir a fila de
        # separacao" e exatamente isso. Sem esperar a navegacao terminar, o
        # `goto` do arquivo seguinte colide com ela e a suite quebra acusando uma
        # tela que esta certa. Esperar custa milissegundos; adivinhar custou uma
        # falha falsa.
        pg.wait_for_timeout(250)
        try:
            pg.wait_for_load_state('load', timeout=4000)
        except Exception:
            pass
    print('telas com dropdown testadas: %d de %d' % (testadas, len(arquivos)))

    print()
    print('E o toggle que reaproveita .theme-seg nao pode mexer no tema:')
    for nome in ['pagina-cadastros-clientes-detalhe.html', 'pagina-cadastros-fornecedores-detalhe.html']:
        pg.goto(localiza.uri(nome)); pg.wait_for_timeout(450)
        r = pg.evaluate("""(function(){
          var segs = document.querySelectorAll('.theme-seg');
          if (segs.length < 2) return { pulou: true };
          var antes = document.body.className;
          var btns = segs[segs.length - 1].querySelectorAll('button, .theme-seg-btn, div');
          if (!btns.length) return { pulou: true };
          btns[btns.length - 1].click();
          return { pulou: false, mudou: document.body.className !== antes, antes: antes, depois: document.body.className };
        })()""")
        if r.get('pulou'):
            print('  --   %s: sem toggle reaproveitado' % nome)
        elif r['mudou']:
            falhas.append(nome + ': o toggle mexeu no tema (%s -> %s)' % (r['antes'], r['depois']))
            print('  FALHA %s' % nome)
        else:
            print('  ok   %s: o tema nao se mexeu' % nome)
    b.close()

print()
print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
