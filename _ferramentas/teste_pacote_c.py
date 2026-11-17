# -*- coding: utf-8 -*-
# Revisao geral de 16/nov/2026, pacote C: as telas, uma a uma.
#   [19] Preview do Produto: os quatro blocos.
#   [6]  Painel da promocao: o fechar no alto, o azul e o Mais acoes.
#   [7]  Ficha do produto: Dados Complementares na grade de Dados Gerais.
#   [8]  O botao 'Encerrar antes para este produto' e as classes so-no-JS sem CSS.
#   [1]  Embalagens: os campos de tamanho numa linha, a 1152, 1280 e 1280 com zoom de 110%.
#   [15] Registro de atividades: clicar na linha abre o painel com a atividade inteira.
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
    if secao(15, 'Registro de atividades: o painel da linha'):
        TXT = 'Confirma a exclusão da marca Samsung? Esta ação não pode ser desfeita e fica registrada com o seu nome e o código de quem autorizou.'
        pg.set_viewport_size({'width': 1280, 'height': 800})
        ir('pagina-configuracoes-registro-atividades.html')
        pg.evaluate("""(txt) => { const l = []; for (let i = 0; i < 130; i++) l.push({ ts: Date.now() - i * 60000, chave: 'marcasExcluir', acao: 'Excluir · Marcas', onde: 'Cadastros → Marcas', modulo: 'Cadastros', usuario: 'Administrador Desk', perfil: 'Owner', senha: i % 2 === 0, autorizadoPor: i % 2 === 0 ? 'Carlos Menezes' : '', detalhe: txt }); localStorage.setItem('deskLog', JSON.stringify(l)); }""", TXT)
        ir('pagina-configuracoes-registro-atividades.html')
        ok(pg.evaluate("document.querySelectorAll('tr[data-i]').length") > 0, 'as linhas do registro são clicáveis')
        ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'o painel começa fechado')
        for t in ('light', 'dark'):
            tema(t)
            pg.evaluate("document.querySelector('tr[data-i]').click()"); pg.wait_for_timeout(350)
            r = pg.evaluate("""(() => ({
              aberto: document.getElementById('eventDrawer').classList.contains('open'),
              texto: document.getElementById('logTextoInteiro').textContent,
              quem: document.getElementById('logQuem').textContent,
              aut: document.getElementById('logAutorizou').textContent,
              quando: document.getElementById('logQuando').textContent,
              link: (document.getElementById('logOndeLink') || {}).href || '',
              chave: document.getElementById('logChave').textContent,
              ov: getComputedStyle(document.documentElement).overflow,
              barraH: document.getElementById('eventDrawer').scrollWidth > document.getElementById('eventDrawer').clientWidth
            }))()""")
            ok(r['aberto'], 'tema %s: clicar na linha abre o painel' % t)
            ok(r['texto'] == TXT, 'tema %s: o painel mostra o texto inteiro que a pessoa confirmou' % t)
            ok('Administrador Desk' in r['quem'] and 'Owner' in r['quem'], 'tema %s: quem fez, com o perfil: %s' % (t, r['quem']))
            ok(r['aut'] == 'Carlos Menezes', 'tema %s: quem autorizou: %s' % (t, r['aut']))
            ok(r['link'].endswith('/cadastros/pagina-cadastros-marcas.html'), 'tema %s: o onde é link da tela: %s' % (t, r['link']))
            ok(len(r['quando']) > 10 and '/' in r['quando'] and ':' in r['quando'], 'tema %s: quando, com data e hora: %s' % (t, r['quando']))
            ok(r['chave'] == 'marcasExcluir', 'tema %s: o registro traz o código da ação' % t)
            ok(r['ov'] == 'hidden' and not r['barraH'], 'tema %s: a página de trás não rola e o painel não tem barra horizontal' % t)
            foto(pg, 'registro_painel_%s.png' % t)
            pg.keyboard.press('Escape'); pg.wait_for_timeout(350)
            ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'tema %s: Esc fecha o painel' % t)
        # o bloco comum registrarLog cortava em 180; desde 17/nov guarda ate 1000, para o painel mostrar o texto inteiro
        longo = pg.evaluate("(() => { const t = 'x'.repeat(600); registrarLog(Object.keys(ACOES_SENHA)[0], t, false); return JSON.parse(localStorage.getItem('deskLog'))[0].detalhe.length; })()")
        ok(longo == 600, 'o registro guarda o texto confirmado inteiro, mesmo com 600 caracteres: %s' % longo)
        pg.evaluate("document.querySelector('tr[data-i]').click()"); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('drawerBackdrop').click()"); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.getElementById('eventDrawer').classList.contains('open')"), 'clicar fora fecha o painel')
        ok(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"), 'com o registro cheio a página não rola na horizontal a 1280')
        pg.evaluate("localStorage.removeItem('deskLog')")

    # ------------------------------------------------------------------------------------------------
    if secao(19, 'Preview do Produto: os quatro blocos'):
        def bl(tela, i, f):
            t = texto(localiza.onde(tela)); a = t.index(i); return t[a:t.index(f, a)]
        for i, f in (('  // ===== GATEWAYS: LEITURA', '  // ===== FIM DO BLOCO GATEWAYS: LEITURA ====='), ('  // ===== EMBALAGENS: LEITURA', '  // ===== FIM DO BLOCO EMBALAGENS: LEITURA =====')):
            ok(bl('pagina-cadastros-produtos.html', i, f) == bl('pagina-vendas-pdv.html', i, f), 'a lista de Produtos leva o bloco %s igual ao do PDV' % i.strip(' /='))
        pg.set_viewport_size({'width': 1280, 'height': 800})
        ir('pagina-cadastros-produtos.html')
        ok(pg.evaluate("PRODUTOS.every(p => { const e = PREVIEW_ESTOQUE[p.id]; return e && e.dep.reduce((s, d) => s + d[1], 0) === p.estoque && e.reservado <= p.estoque; })"), 'o saldo por depósito soma o estoque da lista, e o reservado não passa dele')
        deps = pg.evaluate("PREVIEW_DEPOSITO")
        ir('pagina-cadastros-depositos.html')
        ok(all(pg.evaluate("(a) => DEPOSITOS.filter(d => d.id === Number(a[0]))[0].nome === a[1]", [k, v]) for k, v in deps.items()), 'os nomes dos depósitos do preview são os de Cadastros > Depósitos')
        ir('pagina-cadastros-produtos.html')
        # a luminária (8): atacado de exemplo, sem promocional, com custo; o kit (9): promoção ativa; o mouse (7): promocional e sem saldo
        def abre(i):
            pg.evaluate("(i) => abrirPreviewProduto(i)", i); pg.wait_for_timeout(300)
        def v(id_):
            return pg.evaluate("(i) => (document.getElementById(i) || {}).textContent", id_)
        abre(8)
        ok(v('pvVenda') == 'R$ 79,90' and 'R$ 72,90 a partir de 6 un.' in v('pvAtacado'), 'preços: venda e atacado "a partir de N un." (%s / %s)' % (v('pvVenda'), v('pvAtacado')))
        ok(v('pvPromocao') == 'nenhuma agora', 'sem promoção ativa, o preview diz que não há')
        ok(v('pvCusto') == 'R$ 46,08' and v('pvMargem') == '42,3%', 'custo médio e margem sobre o preço de venda: %s / %s' % (v('pvCusto'), v('pvMargem')))
        ok(v('pvMinimo') == 'R$ 69,92', 'o mínimo da calculadora é o da conta do bloco: %s' % v('pvMinimo'))
        ok(v('pvFisico') == '15 un.' and v('pvDisponivel') == '12 un.' and v('pvEstoqueMinimo') == '6 un.', 'estoque: físico, disponível e mínimo')
        ok('Geral' in pg.evaluate("document.getElementById('drawerBody').textContent") and 'Loja Física Aldeota' in pg.evaluate("document.getElementById('drawerBody').textContent"), 'o saldo aparece por depósito')
        ok(v('pvLoja') == 'Desk Shope' and v('pvMarca') == 'Nordic Home' and v('pvFornecedor') == 'Luminárias Brasil' and 'sugerida' in v('pvEmbalagem'), 'cadastro: loja, marca, fornecedor padrão e embalagem')
        for t in ('light', 'dark'):
            tema(t); foto(pg, 'preview_produto_%s.png' % t)
        ok(pg.evaluate("(() => { const d = document.getElementById('eventDrawer'); return d.scrollWidth <= d.clientWidth; })()"), 'o painel não tem barra horizontal')
        pg.evaluate("fecharDrawer()")
        abre(9)
        ok('Volta às aulas' in v('pvPromocao') and 'R$ 59,90' in v('pvPromocao'), 'a promoção ativa aparece com o nome e o preço dela: %s' % v('pvPromocao'))
        pg.evaluate("fecharDrawer()")
        abre(1)
        ok(v('pvPromocional') == 'R$ 99,90' and v('pvEmbalagem') == 'Caixa de Encomenda Flex M', 'o produto 1: promocional e a embalagem do cadastro (%s)' % v('pvEmbalagem'))
        # a aba Custos gravada vale mais que o catalogo (a mesma fonte da ficha)
        pg.evaluate("""localStorage.setItem('deskCustoProduto', JSON.stringify({ 8: [{ data: '01/11/2026', precoCusto: '50,00', custoMedio: '40,00' }] }))""")
        pg.evaluate("fecharDrawer()"); abre(8)
        ok(v('pvCusto') == 'R$ 40,00' and v('pvMargem') == '49,9%', 'o custo médio vem da aba Custos gravada: %s / %s' % (v('pvCusto'), v('pvMargem')))
        pg.evaluate("localStorage.removeItem('deskCustoProduto')")
        pg.evaluate("fecharDrawer()"); abre(5)
        ok(v('pvCusto') == 'sem custo no cadastro' and 'abra a calculadora na ficha' in v('pvMinimo'), 'produto sem custo: "abra a calculadora na ficha"')
        pg.evaluate("fecharDrawer()")

    # ------------------------------------------------------------------------------------------------
    if secao(6, 'Painel da promoção: o fechar no alto e o Mais ações embaixo'):
        pg.set_viewport_size({'width': 1280, 'height': 800})
        ir('pagina-vendas-promocoes.html'); pg.evaluate("localStorage.removeItem('deskPromocoes')"); ir('pagina-vendas-promocoes.html')
        clica('.aba-sit[data-sit="todos"]')
        sits = pg.evaluate("PROMOS.map(p => [p.id, promoSituacao(p)])")
        por = {}
        for i, s_ in sits:
            por.setdefault(s_, i)
        for sit, esperado in (('agendada', ['Antecipar para hoje', 'Prorrogar', 'Clonar', 'Encerrar agora']), ('ativa', ['Prorrogar', 'Clonar', 'Encerrar agora']), ('encerrada', ['Clonar']), ('rascunho', ['Clonar'])):
            if sit not in por:
                continue
            clica('#corpoTabela tr[data-id="%d"]' % por[sit]); pg.wait_for_timeout(350)
            r = pg.evaluate("""(() => ({
              fechar: !!document.querySelector('#eventDrawer .drawer-header #drawerClose'),
              rodapeFechar: !!document.getElementById('btnFecharPreview'),
              primario: (document.querySelector('#eventDrawer .drawer-footer > .btn-primary') || {}).id,
              itens: Array.from(document.querySelectorAll('#prMaisAcoes .dropdown-select-item')).map(i => i.textContent.trim()),
              linha: !!document.getElementById('prMenuLinha'),
              soltos: document.querySelectorAll('#eventDrawer .drawer-footer > button.btn-secundario').length
            }))()""")
            ok(r['fechar'] and not r['rodapeFechar'], '%s: o "fechar" fica no alto do painel, e não no rodapé' % sit)
            ok(r['primario'] == 'btnPrAbrir' and r['soltos'] == 0, '%s: embaixo, só o botão azul da promoção e o Mais ações' % sit)
            ok(r['itens'] == esperado, '%s: o Mais ações mostra só o que vale hoje: %s' % (sit, r['itens']))
            ok(r['linha'] == ('Encerrar agora' in esperado), '%s: a linha separa o Encerrar agora das outras' % sit)
            if sit == 'agendada':
                for t in ('light', 'dark'):
                    tema(t); clica('#btnPrMais'); pg.wait_for_timeout(200)
                    ok(pg.evaluate("document.querySelector('#prMaisAcoes .dropdown-select-menu').classList.contains('open')"), 'tema %s: o Mais ações abre' % t)
                    ok(pg.evaluate("(() => { const m = document.querySelector('#prMaisAcoes .dropdown-select-menu').getBoundingClientRect(); return m.top >= 0 && m.bottom <= window.innerHeight; })()"), 'tema %s: o menu aberto cabe na janela' % t)
                    foto(pg, 'promocao_painel_%s.png' % t)
                    clica('#btnPrMais'); pg.wait_for_timeout(100)
            clica('#drawerClose'); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"), 'a lista não rola na horizontal')

    # ------------------------------------------------------------------------------------------------
    if secao(7, 'Ficha do produto, Dados Complementares: a grade da aba Dados Gerais'):
        for larg in (1440, 1280):
            pg.set_viewport_size({'width': larg, 'height': 1000})
            ir('pagina-cadastros-produtos-detalhe.html', '?editar=1&id=8')
            g = pg.evaluate("""(() => { const r = (s) => document.querySelector(s).getBoundingClientRect(); return [r('#inputTipoProduto').left, r('#inputTipoSped').left, r('#inputTipoProduto').width]; })()""")
            clica('.tab-item[data-tab="complementares"]')
            c = pg.evaluate("""(() => { const r = (s) => document.querySelector(s).getBoundingClientRect(); const ids = ['#inputLojaDesk', '#inputCategoria', '#inputDepartamento', '#inputSecao', '#inputMarca']; 
              const lojaHint = document.querySelector('#campoLojaDesk .field-hint').getBoundingClientRect(), lab = Array.from(document.querySelectorAll('#tab-complementares label')).filter(l => l.textContent.trim() === 'Departamento')[0].getBoundingClientRect();
              const tab = Array.from(document.querySelectorAll('#tab-complementares input')).filter(i => i.placeholder.indexOf('tabela') >= 0)[0].getBoundingClientRect();
              return { lefts: ids.map(i => Math.round(r(i).left)), larguras: ids.map(i => Math.round(r(i).width)), folga: lab.top - lojaHint.bottom, tabela: Math.round(tab.left), barra: document.documentElement.scrollWidth > document.documentElement.clientWidth }; })()""")
            col1, col2 = round(g[0]), round(g[1])
            ok(c['lefts'] == [col1, col2, col1, col2, col1] and c['tabela'] == col2, 'a %d: os campos de Dados Complementares caem nas duas colunas de Dados Gerais (%s, colunas %d e %d)' % (larg, c['lefts'], col1, col2))
            ok(abs(c['larguras'][0] - round(g[2])) <= 1 and c['larguras'][0] == c['larguras'][1], 'a %d: a largura é a da grade (%s)' % (larg, c['larguras']))
            ok(c['folga'] >= 10, 'a %d: a dica da Loja Desk não cola na linha de baixo (folga de %dpx)' % (larg, c['folga']))
            ok(not c['barra'], 'a %d: sem barra horizontal' % larg)
            for t in ('light', 'dark'):
                tema(t); foto(pg, 'ficha_complementares_%d_%s.png' % (larg, t)) if larg == 1440 else None

    # ------------------------------------------------------------------------------------------------
    if secao(8, 'Classes que só aparecem em string do JS, sem CSS na tela'):
        import re
        TOK = re.compile(r'^[A-Za-z][\w-]*$')
        achados = []
        for c in localiza.caminhos():
            t_ = texto(c)
            css = ' '.join(re.findall(r'<style[^>]*>(.*?)</style>', t_, re.S))
            js = '\n'.join(re.findall(r'<script(?![^>]*src)[^>]*>(.*?)</script>', t_, re.S))
            html = re.sub(r'<script.*?</script>|<style.*?</style>', '', t_, flags=re.S)
            conhecidas = set()
            for sel, corpo in re.findall(r'([^{}]+)\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', css, flags=re.S)):
                decl = [d.split(':')[0].strip() for d in corpo.split(';') if d.strip()]
                if decl and all(d == 'text-decoration' for d in decl):
                    continue   # so tira o sublinhado: nao e estilo
                conhecidas.update(re.findall(r'\.([A-Za-z_][\w-]*)', sel))
            for m in re.finditer(r'class="([^"]*)"', html):
                conhecidas.update(m.group(1).split())
            usadas = set()
            for m in re.finditer(r'class=\?["\']([^"\'<>]*?)\?["\']', js):
                usadas.update(x for x in m.group(1).split() if TOK.match(x))
            for m in re.finditer(r'className\s*=\s*[\'"]([^\'"]*)[\'"]', js):
                usadas.update(x for x in m.group(1).split() if TOK.match(x))
            for m in re.finditer(r'classList\.(?:add|toggle)\(\s*[\'"]([\w-]+)[\'"]', js):
                usadas.add(m.group(1))
            ganchos = set(re.findall(r'\.([A-Za-z_][\w-]*)', ' '.join(re.findall(r'(?:querySelector(?:All)?|closest|matches)\(\s*[\'"]([^\'"]*)[\'"]', js)))) | set(re.findall(r'classList\.contains\(\s*[\'"]([\w-]+)', js)) | set(re.findall(r'[\'"` ]\.([A-Za-z_][\w-]*)', js))
            for x in sorted(usadas - conhecidas - ganchos):
                if not x.endswith('-'):   # "pr-faixa-" e o comeco de um nome montado em tempo de execucao
                    achados.append('%s: %s' % (os.path.basename(c), x))
        ok(not achados, 'nenhuma classe aparece só em string do JS sem CSS na tela, nas %d telas (e sem seletor no JS que a use como gancho): %s' % (len(localiza.caminhos()), achados[:6]))
        ir('pagina-cadastros-produtos-detalhe.html', '?editar=1&id=1'); clica('.tab-item[data-tab="precos"]'); pg.wait_for_timeout(300)
        if not pg.evaluate("!!document.getElementById('btnEncerrarPromoProduto')"):
            ir('pagina-cadastros-produtos-detalhe.html', '?editar=1&id=9'); clica('.tab-item[data-tab="precos"]'); pg.wait_for_timeout(300)
        for t in ('light', 'dark'):
            tema(t)
            r = pg.evaluate("""(() => { const b = document.getElementById('btnEncerrarPromoProduto'); if (!b) return null; const c = getComputedStyle(b), v = getComputedStyle(document.querySelector('.btn-ghost')); return { raio: c.borderRadius, fonte: c.fontFamily.slice(0, 6), peso: c.fontWeight, tamanho: c.fontSize, borda: c.borderTopWidth, fundo: c.backgroundColor, igual: c.borderRadius === v.borderRadius && c.fontWeight === v.fontWeight && c.fontSize === v.fontSize && c.borderTopColor === v.borderTopColor && c.color === v.color }; })()""")
            ok(r is not None and r['igual'] and r['fonte'] == 'Nunito', 'tema %s: o "Encerrar antes para este produto" usa o botão do design system (mesmo raio, peso, tamanho, cor e borda do botão secundário da ficha): %s' % (t, r))
            foto(pg, 'encerrar_antes_%s.png' % t)

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'Embalagens: os campos de tamanho numa linha'):
        EMB = {'pacote': 1, 'envelope': 7, 'rolo': 9}   # o cadastro de exemplo de cada tipo (edicao)
        for nome, larg, alt, zoom in (('1152', 1152, 800, 1), ('1280', 1280, 800, 1), ('1280 com zoom de 110%', 1164, 727, 1.1)):
            ctx = nav.new_context(viewport={'width': larg, 'height': alt}, device_scale_factor=zoom)
            pz = ctx.new_page(); pz.on('dialog', lambda d: d.dismiss())
            pz.goto(localiza.uri('pagina-cadastros-embalagens.html')); pz.wait_for_timeout(350)
            for t in ('light', 'dark'):
                pz.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", t)
                for tipo, eid in EMB.items():
                    for modo in ('novo', 'edicao'):
                        if modo == 'novo':
                            pz.evaluate("document.getElementById('btnNovaEmbalagem').click()"); pz.wait_for_timeout(250)
                            pz.evaluate("(t) => { const r = document.getElementById('inputTipoEmbalagem'); r.querySelector('.dropdown-select-item[data-value=\"' + t + '\"]').click(); }", tipo)
                        else:
                            pz.evaluate("(i) => abrirDrawerEmbalagem(i)", eid)
                        pz.wait_for_timeout(350)
                        r = pz.evaluate("""(() => {
                          const cs = Array.from(document.querySelectorAll('#camposDimensoes .form-field')), rb = (e) => e.getBoundingClientRect();
                          const ls = cs.map(c => rb(c.querySelector('label'))), is = cs.map(c => rb(c.querySelector('input'))), sv = rb(document.getElementById('diagramaDimensoes'));
                          const d = document.getElementById('eventDrawer');
                          const lh = parseFloat(getComputedStyle(cs[0].querySelector('label')).lineHeight) || 18;
                          return { n: cs.length, linhaUnica: ls.every(l => l.height < lh * 1.6), mesmoTopo: is.every(i => Math.abs(i.top - is[0].top) < 0.6) && ls.every(l => Math.abs(l.top - ls[0].top) < 0.6),
                                   diagramaNaLinha: sv.left >= is[is.length - 1].right - 0.5 && sv.top < is[0].bottom && sv.bottom > ls[0].top - 40,
                                   barra: d.scrollWidth > d.clientWidth + 1 || document.documentElement.scrollWidth > document.documentElement.clientWidth,
                                   cabe: d.getBoundingClientRect().left >= 0 && d.getBoundingClientRect().width > 0, aberto: d.classList.contains('open') };
                        })()""")
                        quem = '%s, tema %s, %s, %s' % (nome, t, modo, tipo)
                        ok(r['aberto'] and r['linhaUnica'] and r['mesmoTopo'] and r['diagramaNaLinha'] and not r['barra'], '%s: o nome de cada campo numa linha só, os campos no mesmo nível, o desenho ao lado e sem barra (%s)' % (quem, r))
                        if t == 'light' and modo == 'edicao' and tipo == 'pacote' and nome == '1152':
                            if FOTOS: pz.screenshot(path=os.path.join(FOTOS, 'embalagem_1152_light.png'))
                        pz.evaluate("document.getElementById('drawerClose').click()"); pz.wait_for_timeout(300)
            ctx.close()

    # SECOES

    reais = [e for e in erros if 'ERR_' not in e]
    ok(not reais, 'nenhum erro de JavaScript: %s' % reais[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
