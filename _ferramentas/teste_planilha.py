# -*- coding: utf-8 -*-
# Planilha e impressao de verdade, no sistema inteiro (10/out/2026).
#
# A varredura dos modulos prontos achou 33 itens de menu que so abriam um aviso ("entra junto
# com Relatorios") e 12 que nao faziam nada (Clientes, Fornecedores e Produtos). Agora ha um
# bloco so, igual em todas as telas: "Baixar planilha" leva as colunas e as linhas que a tela
# mostra, com todas as paginas, e "Imprimir" manda a lista inteira para o papel.
#
# O que esta suite guarda, varrendo TODAS as telas (tela nova entra sozinha):
#   1. o bloco e identico em toda tela que o tem; so mudam o nome do arquivo, a funcao que
#      redesenha a lista e, nas telas sem tabela, a funcao que diz o que exportar;
#   2. todo item "planilha" de "Mais acoes" baixa um arquivo com cabecalho e com TODAS as
#      linhas da lista, nao so as da pagina;
#   3. todo item "imprimir" chama a impressao uma vez, com a lista inteira na tela, e devolve
#      a pagina como estava;
#   4. nenhum item de "Mais acoes" fica sem efeito: ou navega, ou abre algo, ou baixa, ou imprime;
#   5. o que saiu de proposito nao volta: "Imprimir" duplicado no topo, "Importar XML" na
#      Conferencia de Entrada e os tres cadastros repetidos no menu de Integracoes.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
import sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None

MARCA = '  // ===== PLANILHA E IMPRESSAO DA TELA (bloco compartilhado, 10/out/2026) ====='
falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok   ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def bloco(texto):
    """O bloco compartilhado, sem as linhas que mudam de tela para tela."""
    a = texto.index(MARCA)
    b = texto.index('  // ===== ', a + 10)
    t = texto[a:b]
    t = re.sub(r"const PLANILHA_NOME = '[^']*';", "const PLANILHA_NOME = '';", t)
    t = re.sub(r"const PLANILHA_REFAZ = \w+;", "const PLANILHA_REFAZ = x;", t)
    t = re.sub(r"const PLANILHA_PAGINA = .*?;   //", "const PLANILHA_PAGINA = x;   //", t)
    return re.sub(r"  // Esta lista nao e tabela.*?\n  \}\n", "", t, flags=re.S)


TODAS = localiza.nomes()
fontes = {n: open(localiza.onde(n), encoding='utf-8').read() for n in TODAS}
com_bloco = [n for n in TODAS if MARCA in fontes[n]]

print('\n[1] O bloco e um so')
ok(len(com_bloco) >= 20, 'o bloco de planilha e impressao esta em %d telas' % len(com_bloco))
diferentes = [n for n in com_bloco if bloco(fontes[n]) != bloco(fontes[com_bloco[0]])]
ok(not diferentes, 'e e identico em todas, fora o nome do arquivo e a funcao de cada tela: %s' % diferentes[:3])
sem_nome = [n for n in com_bloco if not re.search(r"const PLANILHA_NOME = '[a-z-]{4,}';", fontes[n])]
ok(not sem_nome, 'toda tela diz o nome do arquivo que baixa: %s' % sem_nome[:3])

print('\n[5] O que saiu de proposito nao volta')
com_atalho = [n for n in TODAS if re.search(r'id="flyout-integracoes".{0,2500}data-label="(Lojas Desk|Depósitos|Endereços de Estoque)"', fontes[n], re.S)
              and 'data-label="Marketplaces e Hubs"' in fontes[n] and
              fontes[n].index('id="flyout-integracoes"') < fontes[n].find('data-label="Lojas Desk"', fontes[n].index('id="flyout-integracoes"')) < fontes[n].index('data-label="Marketplaces e Hubs"', fontes[n].index('id="flyout-integracoes"'))]
ok(not com_atalho, 'o menu de Integracoes nao repete Lojas Desk, Depositos e Enderecos de Estoque: %s' % com_atalho[:3])
ok(all('data-label="Lojas Desk"' in fontes[n] for n in TODAS if 'id="flyout-cadastros"' in fontes[n]), 'e os tres continuam em Cadastros')
ok('btnImportarXML' not in fontes['pagina-estoque-conferencia-entrada.html'] and 'Importar XML' in fontes['pagina-estoque-entrada-notas.html'],
   '"Importar XML" fica so na Entrada de Notas, que e onde a nota nasce')
duplo = [n for n in ['pagina-cadastros-clientes.html', 'pagina-cadastros-fornecedores.html', 'pagina-cadastros-produtos.html', 'pagina-estoque-ordens-compra.html', 'pagina-vendas-pedidos.html']
         if 'id="btnImprimir"' in fontes[n]]
ok(not duplo, 'nenhuma das cinco telas tem "Imprimir" no topo e no menu ao mesmo tempo: %s' % duplo)

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    ctx = nav.new_context(viewport={'width': 1440, 'height': 950}, accept_downloads=True)
    pg = ctx.new_page()
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def abrir(tela):
        pg.goto(localiza.http(tela)); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def total_da_lista():
        """Quantas linhas a lista tem ao todo, lido do rodape de paginacao; None quando a tela nao pagina."""
        t = pg.evaluate("(() => { const e = document.getElementById('paginacaoResumo'); return e && e.offsetParent !== null ? e.textContent : ''; })()")
        m = re.search(r'de (\d+)', t or '')
        return int(m.group(1)) if m else None

    print('\n[2] Baixar planilha')
    alvos = _filtrar([n for n in TODAS if re.search(r'id="menuMaisAcoes".{0,2500}data-acao="planilha"', fontes[n], re.S)])
    ruins = []
    for tela in alvos:
        abrir(tela)
        esperado = total_da_lista()
        try:
            with pg.expect_download(timeout=4000) as d:
                pg.evaluate("(() => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); document.querySelector('#menuMaisAcoes [data-acao=\"planilha\"]').click(); })()")
            linhas = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
            colunas = linhas[0].count('";"') + 1 if linhas else 0
            certo = colunas >= 3 and len(linhas) >= 2 and (esperado is None or len(linhas) - 1 == esperado) and d.value.suggested_filename.endswith('.csv') and '""' not in linhas[0].split(';')
            if not certo:
                ruins.append('%s: %d colunas, %d linhas, esperava %s' % (tela, colunas, len(linhas) - 1, esperado))
        except Exception as e:
            ruins.append('%s: nao baixou (%s)' % (tela, str(e)[:50]))
        if total_da_lista() != esperado:
            ruins.append('%s: a pagina nao voltou como estava' % tela)
    ok(len(alvos) >= 15 and not ruins, 'as %d telas com "Baixar planilha" baixam o arquivo com cabecalho e a lista inteira: %s' % (len(alvos), ruins[:3]))

    print('\n[3] Imprimir')
    alvos = _filtrar([n for n in TODAS if re.search(r'id="menuMaisAcoes".{0,2500}data-acao="imprimir"', fontes[n], re.S)])
    ruins = []
    for tela in alvos:
        abrir(tela)
        esperado = total_da_lista()
        na_tela = pg.evaluate("document.querySelectorAll('.main tbody tr').length")
        # Dentro de uma funcao: o Playwright executa a expressao quando ela devolve uma funcao.
        pg.evaluate("(() => { window.print = () => { window.__n = (window.__n || 0) + 1; window.__linhas = document.querySelectorAll('.main tbody tr').length; }; })()")
        pg.evaluate("(() => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); document.querySelector('#menuMaisAcoes [data-acao=\"imprimir\"]').click(); })()")
        pg.wait_for_timeout(300)
        n, no_papel = pg.evaluate("[window.__n || 0, window.__linhas || 0]")
        aviso = pg.locator('.modal-card.open').count()
        if n != 1 or aviso or (esperado is not None and na_tela and no_papel < esperado) or pg.evaluate("document.querySelectorAll('.main tbody tr').length") != na_tela:
            ruins.append('%s: imprimiu %d vez(es), %d linhas no papel de %s, aviso %d' % (tela, n, no_papel, esperado, aviso))
    ok(len(alvos) >= 10 and not ruins, 'as %d telas com "Imprimir" chamam a impressao uma vez, com a lista inteira, e devolvem a pagina: %s' % (len(alvos), ruins[:3]))
    abrir('pagina-estoque-enderecamento.html')
    pg.evaluate("(() => { window.print = () => { window.__n = (window.__n || 0) + 1; }; })()")
    pg.evaluate("document.getElementById('btnImprimir').click()"); pg.wait_for_timeout(250)
    ok(pg.evaluate("window.__n || 0") == 1 and pg.locator('.modal-card.open').count() == 0, 'no Enderecamento, "Imprimir lista de enderecamento" imprime em vez de avisar')

    print('\n[4] Nenhum item de "Mais acoes" fica sem efeito, nas listas')
    listas = _filtrar([n for n in TODAS if 'id="menuMaisAcoes"' in fontes[n] and 'detalhe' not in n and n not in ('pagina-vendas-pdv.html', 'pagina-estoque-inventario.html', 'pagina-estoque-conferencia.html', 'pagina-financas-caixa-lancamento.html')])
    mudos = []
    for tela in listas:
        abrir(tela)
        for i in range(pg.evaluate("document.querySelectorAll('#menuMaisAcoes .dropdown-select-item').length")):
            abrir(tela)
            pg.evaluate("(() => { window.print = () => { window.__fez = 'imprimiu'; }; })()")
            baixou = []
            pg.once('download', lambda d: baixou.append(1))
            url = pg.url
            rotulo = pg.evaluate("(i) => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); const it = document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')[i]; const r = it.textContent.trim(); it.click(); return r; }", i)
            pg.wait_for_timeout(450)
            fez = pg.url != url or baixou or pg.evaluate("window.__fez || ''") or pg.evaluate("Array.from(document.querySelectorAll('.open')).filter(e => !/backdrop/.test(e.className) && !e.closest('#menuMaisAcoes')).length")
            if not fez:
                mudos.append(tela.replace('pagina-', '') + ': ' + rotulo)
    ok(len(listas) >= 20 and not mudos, 'em %d listas, todo item do menu navega, abre algo, baixa ou imprime: %s' % (len(listas), mudos[:4]))
    cad = {n: pg.evaluate("1") and re.findall(r'data-acao="(\w+)"', re.search(r'id="menuMaisAcoes".*?</div>\n      </div>', fontes[n], re.S).group(0)) for n in ['pagina-cadastros-clientes.html', 'pagina-cadastros-fornecedores.html', 'pagina-cadastros-produtos.html']}
    ok(all(v == ['imprimir', 'planilha'] for v in cad.values()), 'Clientes, Fornecedores e Produtos ficaram com os dois itens que funcionam: %s' % list(cad.values())[0])
    abrir('pagina-cadastros-clientes.html')
    with pg.expect_download() as d:
        pg.evaluate("(() => { document.querySelector('#menuMaisAcoes .dropdown-select-btn').click(); document.querySelector('#menuMaisAcoes [data-acao=\"planilha\"]').click(); })()")
    csv = open(d.value.path(), encoding='utf-8-sig').read().splitlines()
    ok(csv[0] == '"Código";"Nome";"Tipo";"CPF/CNPJ";"Telefone";"E-mail";"Cidade/UF";"Situação"' and len(csv) - 1 == pg.evaluate("clientesFiltrados().length") and len(csv) > 11,
       'a planilha de Clientes sai com as colunas do cadastro e todos os clientes do filtro (%d), nao so os 10 da pagina' % (len(csv) - 1))
    ok(not erros, 'sem erro de JS: %s' % erros[:2])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
raise SystemExit(1 if falhas else 0)
