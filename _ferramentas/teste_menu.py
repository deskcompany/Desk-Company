from playwright.sync_api import sync_playwright
import os, sys, re, glob
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
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('1. de uma tela de Cadastros ate Contas a pagar, pelo menu')
    pg.goto(localiza.uri('pagina-cadastros-marcas.html')); pg.wait_for_timeout(500)
    # O menu abre no CLIQUE do modulo, nao no hover — foi assim que o molde
    # ficou. O teste segue o caminho do usuario: clica no modulo, depois no item.
    def abrirMenu(modulo):
        pg.click('.nav-item[data-id="%s"]' % modulo); pg.wait_for_timeout(450)
    abrirMenu('financas')
    sel = '#flyout-financas .flyout-item[data-label="Contas a Pagar"]'
    ok(pg.query_selector(sel) is not None, 'o item existe no flyout de Financas')
    ok(localiza.nome(pg.get_attribute(sel, 'data-href')) == 'pagina-financas-contas-pagar.html', 'e agora tem destino')
    pg.click(sel); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-contas-pagar.html'), 'o clique navegou de verdade: %s' % pg.url.split('/')[-1])

    print('2. e de Contas a pagar de volta para o Caixa')
    abrirMenu('financas')
    pg.click('#flyout-financas .flyout-item[data-label="Caixa"]'); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-caixa.html'), 'chegou no extrato: %s' % pg.url.split('/')[-1])

    print('3. e do Caixa para Contas a receber, construida em 02/out')
    abrirMenu('financas')
    pg.click('#flyout-financas .flyout-item[data-label="Contas a Receber"]'); pg.wait_for_timeout(900)
    ok(pg.url.endswith('pagina-financas-contas-receber.html'), 'chegou no a receber: %s' % pg.url.split('/')[-1])

    print('4. item sem tela continua inerte, sem quebrar')
    # Este caso precisa de um item que de fato NAO tem tela — ate 02/out ele era
    # "Contas a Receber", que agora existe. Teste que prova "nao navega" tem de
    # trocar de alvo quando o alvo ganha destino, senao vira teste de nada.
    abrirMenu('financas')
    antes = pg.url
    pg.click('#flyout-financas .flyout-item[data-label="Comissões Afiliados"]'); pg.wait_for_timeout(500)
    ok(pg.url == antes, 'nao navegou (a tela ainda nao existe)')
    ok('Comissões Afiliados' in pg.text_content('#breadcrumb'), 'mas moveu o breadcrumb, como antes')
    ok(not erros, 'sem erro de JS: %s' % erros[:3])

    print('5. todo destino do menu aponta para arquivo que existe')
    faltando = []
    for arq in _filtrar(localiza.caminhos()):
        t = open(arq, encoding='utf-8').read()
        for h in set(re.findall(r'flyout-item" data-label="[^"]+" data-href="([^"]+)"', t)):
            if not os.path.isfile(localiza.resolve(h, arq)): faltando.append((os.path.basename(arq), h))
    ok(not faltando, 'nenhum destino quebrado: %s' % faltando[:3])

    print('5. o painel de Pagamento abre vivo numa conta em LEITURA')
    pg.goto(localiza.uri('pagina-financas-contas-pagar-detalhe.html') + '?id=6'); pg.wait_for_timeout(600)
    ok(pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'a conta abre em leitura')
    pg.click('#btnDarBaixa'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#inputDataPgto', "e => getComputedStyle(e).display") != 'none', 'o campo Data do painel esta visivel')
    ok(pg.eval_on_selector('#ddOrigem', "e => getComputedStyle(e).display") != 'none', 'o dropdown de origem esta visivel')
    pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#inputJuros', "e => getComputedStyle(e).display") != 'none', 'e os campos de juros e desconto tambem')
    ok(not erros, 'sem erro de JS no caminho todo: %s' % erros[:3])
    print('6. botao que vira link nao ganha sublinhado, em nenhuma tela')
    # 08/out: o usuario viu "Definir metas" sublinhado, pela segunda vez no dia.
    # Botao escrito como link herda o sublinhado do navegador, e cada tela
    # resolvia isso classe por classe. A medida e feita com TODA classe btn-*
    # que a tela declara, inclusive as que hoje so aparecem em botao de verdade:
    # o defeito latente e o que volta na proxima tela clonada.
    SUBLINHA = """() => {
      const nomes = new Set();
      for (const s of document.styleSheets) { let r; try { r = s.cssRules; } catch (e) { continue; }
        for (const x of r) { const m = (x.selectorText || '').match(/[.]btn-[a-z0-9-]*/gi); if (m) m.forEach(n => nomes.add(n.slice(1))); } }
      const ruins = [];
      nomes.forEach(n => { const a = document.createElement('a'); a.href = '#'; a.className = n; a.textContent = 'x';
        document.body.appendChild(a);
        if (getComputedStyle(a).textDecorationLine.indexOf('underline') >= 0) ruins.push(n); a.remove(); });
      return ruins.sort();
    }"""
    sublinhadas = []
    for arq in sorted(_filtrar(localiza.caminhos())):
        pg.goto(localiza.uri(arq)); pg.wait_for_load_state('load')
        ruins = pg.evaluate(SUBLINHA)
        if ruins: sublinhadas.append((os.path.basename(arq), ruins))
    ok(not sublinhadas, 'nenhuma classe de botao sublinha como link: %s' % sublinhadas[:3])
    print('7. todo link entre telas diz a pasta, e a pasta existe')
    # 08/out: as telas sairam da raiz e foram para telas/<modulo>/. O link entre
    # elas passou a ser sempre ../<pasta>/<arquivo>. Um link nu (so o nome) abre
    # 404 calado, e e exatamente o que nasce quando se copia um trecho de uma
    # conversa antiga ou se escreve o destino de memoria. A checagem e estatica
    # e cobre TODA citacao, nao so o menu: botao, href montado em JS, destino de
    # salvar. As fontes entram junto, pelo mesmo motivo.
    CITA = re.compile(r"(?:\.\./[a-z_]+/)?pagina-[a-z0-9-]+\.html")
    nus, quebrados, fontes = [], [], []
    for arq in sorted(_filtrar(localiza.caminhos())):
        t = open(arq, encoding='utf-8').read()
        for c in set(CITA.findall(t)):
            if not c.startswith('../'): nus.append((os.path.basename(arq), c))
            elif not os.path.isfile(localiza.resolve(c, arq)): quebrados.append((os.path.basename(arq), c))
        for u in set(re.findall(r"url\('([^')]+)'\)", t)):
            if not os.path.isfile(localiza.resolve(u, arq)): fontes.append((os.path.basename(arq), u))
    ok(not nus, 'nenhuma citacao a tela sem a pasta: %s' % nus[:3])
    ok(not quebrados, 'e toda pasta citada tem a tela la dentro: %s' % quebrados[:3])
    ok(not fontes, 'e as fontes carregam de onde a tela esta: %s' % fontes[:3])
    print('8. Configuracoes abre pelo hub: toda tela do modulo tem cartao, e Operacional saiu do menu')
    # 08/out: os cadastros de Operacional (Transportadoras e os dois Motivos)
    # foram para Configuracoes, e o modulo saiu do menu lateral. O hub ja listava
    # os tres como cartao SEM destino, com as telas prontas havia dias: cartao
    # morto para tela que existe. Esta secao cobra as duas pontas: nenhuma tela
    # de Configuracoes fica sem porta no hub, e o modulo apagado nao volta numa
    # tela copiada de uma versao antiga.
    hub = open(localiza.onde('pagina-configuracoes.html'), encoding='utf-8').read()
    sem_cartao = [os.path.basename(c) for c in localiza.caminhos()
                  if os.path.basename(os.path.dirname(c)) == 'configuracoes'
                  and os.path.basename(c) != 'pagina-configuracoes.html'
                  and ("href:'../configuracoes/" + os.path.basename(c) + "'") not in hub]
    ok(not sem_cartao, 'toda tela de Configuracoes tem cartao no hub: %s' % sem_cartao[:4])
    com_modulo = [os.path.basename(c) for c in _filtrar(localiza.caminhos())
                  if 'id="flyout-operacional"' in open(c, encoding='utf-8').read()
                  or 'data-id="operacional"' in open(c, encoding='utf-8').read()]
    ok(not com_modulo, 'nenhuma tela traz o modulo Operacional no menu lateral: %s' % com_modulo[:4])
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
