# -*- coding: utf-8 -*-
# Varredura de cliques — criada em 29/set/2026. LENTA (~10 min): e ferramenta de
# fechamento de modulo, nao teste de todo dia.
# Clica em cada controle da area principal de cada tela, um por vez, com a tela
# recarregada entre cliques, e abre a primeira linha da listagem para clicar no
# que aparecer no painel. Relata: erro de JS, navegacao para arquivo que nao
# existe, e aviso dizendo que uma tela existente "ainda nao existe".
# Uso:  python3 varredura_cliques.py            (todas as telas)
#       python3 varredura_cliques.py - estoque  (so as que tem 'estoque' no nome)
import os, sys, json, glob, re
from multiprocessing import Pool
from playwright.sync_api import sync_playwright
import pathlib as _pathlib
from urllib.parse import urlparse as _urlparse
from urllib.request import url2pathname as _url2path

import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome')
CH = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
import tempfile
SAIDA = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != '-' else os.path.join(tempfile.gettempdir(), 'varredura_cliques.json')

# A URL que o navegador devolve nao e a que se monta com concatenacao: ela tem
# barras para frente, tres barras depois do esquema e espaco como %20. Num
# caminho sem espaco (o /home/claude/desk-company do Linux) a diferenca nao
# aparecia; em "C:\Claude AI\Desk Company" ela quebra toda comparacao.
BASE = _pathlib.Path(PASTA).as_uri() + '/'


def _caminho(u):
    """URL do navegador -> caminho de arquivo real, sem query."""
    return _url2path(_urlparse(u.split('?')[0]).path)


def _relativo(u):
    """URL do navegador -> nome do arquivo relativo a pasta do projeto."""
    return localiza.nome(u)


HOOK = r"""
(() => {
  window.__avisos = [];
  const envolve = (nome) => {
    const o = window[nome];
    if (typeof o !== 'function' || o.__env) return;
    const f = function(){ try { window.__avisos.push(nome + '|' + String(arguments[0])); } catch(e){}; return o.apply(this, arguments); };
    Object.defineProperty(f, 'length', { value: o.length });
    f.__env = true;
    window[nome] = f;
  };
  envolve('avisar'); envolve('abrirModalConfirmacao'); envolve('confirmarAcao');
})();
"""

# candidatos: controles clicaveis FORA da sidebar
LISTA = r"""
(() => {
  const fora = el => !el.closest('.sidebar-col, .flyout-body, .flyout-col, .flyout-item, .sidebar, .floating-card');
  const sel = 'button, a[href], [data-acao], .dropdown-select-item, .drawer-link, .btn-mini, .tab-btn, .aba, [role="button"], .link-acao, .acao-link';
  const todos = Array.from(document.querySelectorAll(sel)).filter(fora);
  return todos.map((el, i) => {
    const menu = el.closest('.dropdown-select-menu');
    let pai = null;
    if (menu) {
      const raiz = menu.closest('.dropdown-select') || menu.parentElement;
      const b = raiz && raiz.querySelector('.dropdown-select-btn, button');
      if (b && b !== el) pai = Array.from(document.querySelectorAll(sel)).filter(fora).indexOf(b);
    }
    const r = el.getBoundingClientRect();
    const vis = !!(el.offsetParent || el.getClientRects().length) && getComputedStyle(el).visibility !== 'hidden';
    return { i, pai, vis, id: el.id || '', tag: el.tagName, txt: (el.innerText || el.getAttribute('title') || el.getAttribute('aria-label') || '').trim().replace(/\s+/g,' ').slice(0,60),
             href: el.getAttribute('href') || '', acao: el.getAttribute('data-acao') || '', dis: !!el.disabled };
  });
})();
"""

def pega(pg, i):
    return pg.evaluate("""(i) => {
      const fora = el => !el.closest('.sidebar-col, .flyout-body, .flyout-col, .flyout-item, .sidebar, .floating-card');
      const sel = 'button, a[href], [data-acao], .dropdown-select-item, .drawer-link, .btn-mini, .tab-btn, .aba, [role="button"], .link-acao, .acao-link';
      const todos = Array.from(document.querySelectorAll(sel)).filter(fora);
      const el = todos[i]; if (!el) return false;
      el.setAttribute('data-crawl-alvo', '1'); return true;
    }""", i)

def varre(arq):
    res = {'arq': arq, 'itens': [], 'erro_carga': []}
    url = localiza.uri(arq)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CH)
        ctx = b.new_context(viewport={'width': 1440, 'height': 900})
        pg = ctx.new_page()
        erros = []
        pg.on('pageerror', lambda e: erros.append(str(e)))
        pg.on('dialog', lambda d: d.dismiss())
        pg.goto(url); pg.wait_for_timeout(250)
        res['erro_carga'] = list(erros)
        cands = pg.evaluate(LISTA)
        res['n'] = len(cands)
        for c in cands:
            if c['dis']: continue
            erros.clear()
            try:
                pg.goto(url); pg.wait_for_timeout(120)
                pg.evaluate(HOOK)
                if c['pai'] is not None and c['pai'] >= 0 and not c['vis']:
                    if pega(pg, c['pai']):
                        pg.locator('[data-crawl-alvo]').first.click(timeout=1200)
                        pg.evaluate("document.querySelectorAll('[data-crawl-alvo]').forEach(e=>e.removeAttribute('data-crawl-alvo'))")
                        pg.wait_for_timeout(80)
                if not pega(pg, c['i']): continue
                loc = pg.locator('[data-crawl-alvo]').first
                if not loc.is_visible():
                    continue
                antes = pg.url
                loc.click(timeout=1500)
                pg.wait_for_timeout(220)
                depois = pg.url
                av = []
                try: av = pg.evaluate("window.__avisos || []")
                except Exception: pass
                nav = None
                if depois != antes:
                    alvo = _caminho(depois)
                    nav = {'url': _relativo(depois), 'existe': os.path.exists(alvo)}
                res['itens'].append({**c, 'nav': nav, 'avisos': av, 'erros': list(erros)})
            except Exception as e:
                res['itens'].append({**c, 'falha_clique': str(e).split('\n')[0][:160], 'erros': list(erros)})
        # fase 2: abre a primeira linha/cartao e clica no que aparecer dentro do painel
        ROW = "(() => { const r = Array.from(document.querySelectorAll('tbody tr[data-id], tbody tr.linha-clicavel, .produto-card, .cliente-card, .item-card, tbody tr')).filter(e => e.offsetParent && !e.closest('.sidebar-col')); if (!r.length) return false; const alvo = r[0].querySelector('td:nth-child(3), td:nth-child(2), .card-nome, .item-nome') || r[0]; alvo.setAttribute('data-crawl-linha','1'); return true; })()"
        try:
            pg.goto(url); pg.wait_for_timeout(150)
            vis0 = set(c['i'] for c in pg.evaluate(LISTA) if c['vis'])
            if pg.evaluate(ROW):
                pg.locator('[data-crawl-linha]').first.click(timeout=1500); pg.wait_for_timeout(250)
                depois_linha = pg.url
                novos = [c for c in pg.evaluate(LISTA) if c['vis'] and c['i'] not in vis0 and not c['dis']]
                res['linha_nav'] = _relativo(depois_linha) if depois_linha != url else None
                for c in novos:
                    erros.clear()
                    try:
                        pg.goto(url); pg.wait_for_timeout(120); pg.evaluate(HOOK)
                        pg.evaluate(ROW); pg.locator('[data-crawl-linha]').first.click(timeout=1500); pg.wait_for_timeout(200)
                        if pg.url != url:
                            break
                        if not pega(pg, c['i']): continue
                        loc = pg.locator('[data-crawl-alvo]').first
                        antes = pg.url
                        loc.click(timeout=1500); pg.wait_for_timeout(220)
                        av = pg.evaluate("window.__avisos || []") if pg.url == antes else []
                        nav = None
                        if pg.url != antes:
                            alvo = _caminho(pg.url)
                            nav = {'url': _relativo(pg.url), 'existe': os.path.exists(alvo)}
                        res['itens'].append({**c, 'fase': 'linha', 'nav': nav, 'avisos': av, 'erros': list(erros)})
                    except Exception as e:
                        res['itens'].append({**c, 'fase': 'linha', 'falha_clique': str(e).split('\n')[0][:160], 'erros': list(erros)})
        except Exception as e:
            res['fase2_erro'] = str(e)[:200]
        b.close()
    return res

if __name__ == '__main__':
    arqs = sorted(os.path.basename(f) for f in localiza.caminhos() if 'molde' not in f)
    if len(sys.argv) > 2: arqs = [a for a in arqs if any(s in a for s in sys.argv[2].split(','))]
    with Pool(6) as pool:
        out = pool.map(varre, arqs)
    json.dump(out, open(SAIDA, 'w'), ensure_ascii=False, indent=0)
    tot = sum(len(r['itens']) for r in out)
    PROIB = re.compile(r"s[óo] (passa a )?funciona(r)? de verdade|arquivo isolado|pr[óo]xima (tela|a ser)|no fim da fase", re.I)
    erros = [(r['arq'], it['txt'][:40], it['erros'][0][:120]) for r in out for it in r['itens'] if it.get('erros')]
    erros += [(r['arq'], '(ao carregar)', e[:120]) for r in out for e in r['erro_carga']]
    navs = [(r['arq'], it['txt'][:40], it['nav']['url']) for r in out for it in r['itens'] if it.get('nav') and not it['nav']['existe']]
    falsos = [(r['arq'], it['txt'][:40], a[7:120]) for r in out for it in r['itens'] for a in it.get('avisos', []) if a.startswith('avisar|') and PROIB.search(a)]
    print('telas', len(out), '· cliques', tot)
    print('erros de JS:', len(erros)); [print('  ', *x) for x in erros]
    print('navegacao para arquivo inexistente:', len(navs)); [print('  ', *x) for x in navs]
    print('aviso dizendo que tela existente nao existe:', len(falsos)); [print('  ', *x) for x in falsos]
    print('(controles dentro de modal/painel/menu fechado nao executam aqui — as suites dedicadas cobrem)')
    print('detalhe por clique em', SAIDA)
    print('FALHAS: ' + str(len(erros) + len(navs) + len(falsos)))
