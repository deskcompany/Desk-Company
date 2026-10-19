# -*- coding: utf-8 -*-
# Vale-compra, entrega 1: o vale nasce a mao e se ve (barganha aprovada pelo usuario em 19/out/2026).
#
# O vale e SALDO DO CLIENTE, sem codigo, e so vale na loja que o emitiu. Cada vale tem numero (VC-n), cliente, loja, origem, valor, emissao,
# vencimento (fixado na emissao: hoje mais o prazo de Configuracoes), usos e situacao (disponivel, usado, vencido, cancelado). A lista e
# `pagina-financas-vale-compra.html`; a pagina do vale (`-detalhe.html?id=`) cancela e reativa; a aba Vale-compra do cadastro do cliente le.
# Uma chave so no navegador, `deskValesCompra`, lida pelas tres telas com o mesmo bloco de leitura.
#
#   [1] O exemplo de fabrica: os cinco vales, as situacoes, os saldos, o vencido em vermelho, a marca que nao deixa duplicar, e os espelhos
#       (clientes do cadastro, lojas de Lojas Desk, pedidos de Pedidos de Venda);
#   [2] Os indicadores, refeitos aqui em Python, e que nao mexem com o filtro;
#   [3] Busca, loja, origem e abas com contagem; o estado da lista que volta pelo endereco; o link de outra tela com ?busca=;
#   [4] Incluir vale: validacoes, a busca de cliente, senha, vencimento pelo prazo, entra na lista e no cadastro, registro de atividades;
#   [5] A pagina do vale: dados, usos, historico; cancelar e reativar (motivo, senha, saldo, novo vencimento, historico);
#   [6] Configuracoes: o prazo grava, os limites, e nao muda o vale que ja existe;
#   [7] A aba do cliente: saldo por loja (so a propria loja), os vales, o link para a lista, e o cadastro em modo leitura;
#   [8] O item de menu na posicao certa em toda tela, e o catalogo de acoes com as tres acoes;
#   [9] O bloco de leitura identico nas tres copias, a impressao em relatorio e a barra de rolagem de 1280px para cima.
from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import os as _os, glob as _g, re, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LISTA, DET, CLI_D, CFG = 'pagina-financas-vale-compra.html', 'pagina-financas-vale-compra-detalhe.html', 'pagina-cadastros-clientes-detalhe.html', 'pagina-configuracoes-cadastro-clientes.html'
CLI_L, LOJAS_D, PED_L, PED_D = 'pagina-cadastros-clientes.html', 'pagina-cadastros-lojas-desk.html', 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html'
COM, SENHAS = 'pagina-financas-comissoes.html', 'pagina-configuracoes-confirmacoes-senha.html'
CHAVES_LOCAIS = ['deskValesCompra', 'deskValesCompraExemplo', 'deskParametros', 'deskLog']

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


# ---------------------------------------------------------------- a conta refeita em Python (o oraculo)
HOJE = date.today()
dia = lambda n: HOJE + timedelta(days=n)
iso = lambda d: d.isoformat()
br = lambda d: d.strftime('%d/%m/%Y')


def moeda(v):
    return 'R$ ' + ('{:,.2f}'.format(v)).replace(',', 'X').replace('.', ',').replace('X', '.')


def usado(v): return round(sum(u['valor'] for u in v.get('usos', [])), 2)
def saldo(v): return 0 if v.get('cancelado') else round(v['valor'] - usado(v), 2)


def situacao(v):
    if v.get('cancelado'): return 'cancelado'
    if saldo(v) <= 0: return 'usado'
    return 'vencido' if HOJE > date.fromisoformat(v['venc']) else 'disponivel'


def vale(n, cid, nome, doc, loja, valor, emitido_ha, venc_em, usos=None, cancelado=None, reativ=None, origem='cortesia', ref=None):
    v = dict(n=n, clienteId=cid, cliente=nome, doc=doc, loja=loja, origem=origem, motivo='Motivo de teste' if origem == 'cortesia' else '', valor=valor,
             emitido=iso(dia(-emitido_ha)), venc=iso(dia(venc_em)), usos=usos or [], reativacoes=reativ or [], cancelado=cancelado)
    if ref: v['ref'] = ref
    return v


def kpis(vales):
    disp = [v for v in vales if situacao(v) == 'disponivel']
    v30 = [v for v in disp if (date.fromisoformat(v['venc']) - HOJE).days <= 30]
    venc = [v for v in vales if situacao(v) == 'vencido']
    soma = lambda l: round(sum(saldo(v) for v in l), 2)
    return dict(saldo=soma(disp), n_disp=len(disp), n30=len(v30), s30=soma(v30), n_venc=len(venc), s_venc=soma(venc))


ESCOLHE = "([dd, v]) => document.querySelector('#' + dd + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()"
MUDA = "([sel, v]) => { const i = document.querySelector(sel); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); }"
LINHAS = """() => [...document.querySelectorAll('#corpoTabela tr')].map(tr => { const td = tr.children, t = i => td[i].textContent.replace(/\\s+/g, ' ').trim();
  const sub = td[5].querySelector('.vol-sub');
  return { n: t(0), cliente: td[1].querySelector('.vol-nome').textContent, doc: td[1].querySelector('.vol-sub').textContent, loja: t(2), origem: t(3), emitido: t(4),
           vence: td[5].childNodes[0].textContent.trim(), venceTexto: sub ? sub.textContent : '', venceVermelho: !!td[5].querySelector('.com-atraso'),
           valor: t(6), usado: t(7), saldo: t(8), sit: t(9) }; })"""
MEDE = """() => { const r = []; document.querySelectorAll('.estoque-table-wrap, .contatos-table').forEach(w => {
  const caixa = w.classList.contains('contatos-table') ? w.parentElement : w;
  if (w.getClientRects().length && (caixa.scrollWidth > caixa.clientWidth + 1 || w.scrollWidth > caixa.clientWidth + 1)) r.push((w.id || w.className) + ' ' + w.scrollWidth + '>' + caixa.clientWidth); });
  if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) r.push('a pagina rola'); return r; }"""


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


def trecho(t, ini, fim):
    a = t.index(ini)
    return t[a:t.index(fim, a + len(ini))]


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('console', lambda m: erros.append('console: ' + m.text[:160]) if m.type == 'error' else None)

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def limpar(com_exemplo=False):
        if pg.url == 'about:blank':
            ir(LISTA)   # o armazenamento so existe numa pagina da casa
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)
        # Os cinco vales de exemplo nascem sozinhos no primeiro acesso. As secoes que contam coisas partem sem eles, gravando a marca; a
        # secao 1 e a que testa o estado de fabrica (com_exemplo=True).
        if not com_exemplo:
            pg.evaluate("localStorage.setItem('deskValesCompra', JSON.stringify({ vales: [] })); localStorage.setItem('deskValesCompraExemplo', '1')")

    def semear(lista):
        pg.evaluate("(v) => { localStorage.setItem('deskValesCompra', JSON.stringify({ vales: v })); localStorage.setItem('deskValesCompraExemplo', '1'); }", lista)

    def vales_gravados():
        return pg.evaluate("(JSON.parse(localStorage.getItem('deskValesCompra') || '{}').vales || [])")

    def params(**kw):
        pg.evaluate("(kw) => { const g = JSON.parse(localStorage.getItem('deskParametros') || '{}'); Object.assign(g, kw); localStorage.setItem('deskParametros', JSON.stringify(g)); }", kw)

    def modal_aberto():
        return pg.evaluate("document.getElementById('confirmModal').classList.contains('open')")

    def senha_visivel():
        return pg.evaluate("(() => { const c = document.getElementById('campoSenhaModal'); return !!c && getComputedStyle(c).display !== 'none' && c.getClientRects().length > 0; })()")

    def trava_sem_senha():
        pg.evaluate("document.getElementById('inputSenhaModal').value = ''")
        pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(250)
        return modal_aberto() and pg.evaluate("document.getElementById('campoSenhaModal').classList.contains('has-error')")

    def confirmar():
        pg.wait_for_timeout(250)
        senha = senha_visivel()
        if senha:
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(350)
        return senha

    def fechar_aviso():
        pg.wait_for_timeout(200)
        if modal_aberto():
            pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(200)

    def texto_modal():
        return pg.evaluate("document.getElementById('confirmModalTexto').textContent")

    def log():
        return pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]')")

    def linhas():
        return pg.evaluate(LINHAS)

    def abrir_incluir():
        pg.evaluate("document.getElementById('btnIncluirVale').click()"); pg.wait_for_timeout(250)

    def preencher_incluir(busca, loja, valor, motivo, escolher=True):
        pg.fill('#buscaClienteVale', busca); pg.wait_for_timeout(150)
        if escolher:
            pg.press('#buscaClienteVale', 'Enter'); pg.wait_for_timeout(150)
        if loja:
            pg.evaluate(ESCOLHE, ['incLoja', str(loja)])
        pg.evaluate(MUDA, ['#incValor', valor]); pg.evaluate(MUDA, ['#incMotivo', motivo])

    def enviar_incluir():
        pg.evaluate("document.getElementById('btnIncluir').click()"); pg.wait_for_timeout(250)

    def erros_incluir():
        return pg.evaluate("['IncCliente', 'IncLoja', 'IncValor', 'IncMotivo'].filter(c => document.getElementById('erro' + c).classList.contains('show'))")

    def mais_acao(acao):
        pg.evaluate("(a) => document.querySelector('#menuMaisAcoes .dropdown-select-item[data-acao=\"' + a + '\"]').click()", acao); pg.wait_for_timeout(300)

    def itens_menu():
        return pg.evaluate("[...document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')].filter(i => i.style.display !== 'none').map(i => i.getAttribute('data-acao'))")

    # ================================================================== [1] o exemplo de fabrica
    if secao(1, 'O exemplo de fábrica: cinco vales, as situações, os saldos, o vencido em vermelho e a marca'):
        limpar(True); ir(LISTA)
        ls = linhas()
        ok(len(ls) == 5 and [l['n'] for l in ls] == ['VC-5', 'VC-4', 'VC-3', 'VC-2', 'VC-1'], 'a lista de fábrica tem os cinco vales, do mais novo para o mais velho: %s' % [l['n'] for l in ls])
        por_n = dict((l['n'], l) for l in ls)
        esperado = {
            'VC-1': ('Camila Rêgo', '567.890.123-44', 'Desk Brands', 50, 0, 50, 'Vencido', br(dia(-20))),
            'VC-2': ('Rafael Nogueira', '234.567.890-11', 'Desk Shope', 40, 40, 0, 'Usado', br(dia(120))),
            'VC-3': ('Auto Peças Imperatriz Ltda', '29.887.501/0001-22', 'Desk Tech', 80, 30, 50, 'Disponível', br(dia(140))),
            'VC-4': ('Marina Duarte', '123.456.789-00', 'Desk Shope', 120, 0, 120, 'Disponível', br(dia(160))),
            'VC-5': ('Juliana Prado', '345.678.901-22', 'Desk Brands', 60, 0, 0, 'Cancelado', br(dia(165)))}
        for n, (cli, doc, loja, valor, usd, sld, sit, venc) in sorted(esperado.items()):
            l = por_n.get(n, {})
            ok((l.get('cliente'), l.get('doc'), l.get('loja'), l.get('origem'), l.get('valor'), l.get('usado'), l.get('saldo'), l.get('sit'), l.get('vence')) ==
               (cli, doc, loja, 'Cortesia', moeda(valor), moeda(usd), moeda(sld), sit, venc),
               '%s: cliente, documento, loja, origem, valor, usado, saldo, situação e vencimento batem (%s, %s, saldo %s, %s)' % (n, cli, loja, moeda(sld), sit))
        ok(por_n['VC-1']['venceTexto'] == 'vencido há 20 dias' and por_n['VC-1']['venceVermelho'] and not any(l['venceVermelho'] for l in ls if l['n'] != 'VC-1'),
           'o vencido diz "vencido há 20 dias" em vermelho, e nenhum outro vale fica vermelho')
        ok(pg.evaluate("""() => { const e = document.querySelector('#corpoTabela .com-atraso'); const t = document.createElement('span'); t.style.color = 'var(--danger)'; document.body.appendChild(t);
            const ref = getComputedStyle(t).color; t.remove(); return !!e && getComputedStyle(e).color === ref; }"""), 'e o vermelho é o do sistema (--danger), não um tom solto')
        ok(por_n['VC-4']['venceTexto'] == 'vence em 160 dias' and por_n['VC-3']['venceTexto'] == 'vence em 140 dias', 'o disponível diz "vence em N dias"')
        ok(pg.evaluate("localStorage.getItem('deskValesCompraExemplo')") == '1' and len(vales_gravados()) == 5, 'a marca do exemplo fica gravada')
        # a cor do selo da situacao: o vencido vermelho, o disponivel verde (o selo nao e so texto)
        cores = pg.evaluate("[...document.querySelectorAll('#corpoTabela .badge-situacao')].map(b => getComputedStyle(b).color)")
        ok(len(set(cores)) == 4, 'as quatro situações têm quatro cores de selo diferentes: %s' % sorted(set(cores)))
        # nao duplica, em nenhuma das tres telas
        ir(LISTA); ir(DET, '?id=1'); ir(CLI_D, '?id=1')
        ok(len(vales_gravados()) == 5, 'abrir de novo, e abrir a página do vale e o cadastro do cliente, não duplica o exemplo')
        # navegador que ja tinha um vale e nao tem a marca: acrescenta sem apagar, com o n seguindo o maior
        limpar(True)
        semear([vale(7, 4, 'Juliana Prado', '345.678.901-22', 2, 33, 3, 177)])
        pg.evaluate("localStorage.removeItem('deskValesCompraExemplo')")
        ir(LISTA)
        gr = vales_gravados()
        ok([v['n'] for v in gr] == [7, 8, 9, 10, 11, 12] and gr[0]['valor'] == 33 and pg.evaluate("localStorage.getItem('deskValesCompraExemplo')") == '1',
           'navegador com um vale e sem a marca: os cinco entram ao fim, com n 8 a 12, o dele fica, e a marca é gravada: %s' % [v['n'] for v in gr])
        # excluido ou cancelado, o exemplo nao volta
        pg.evaluate("() => { const g = JSON.parse(localStorage.getItem('deskValesCompra')); g.vales.splice(1, 2); localStorage.setItem('deskValesCompra', JSON.stringify(g)); }")
        ir(LISTA); ir(DET, '?id=9')
        ok([v['n'] for v in vales_gravados()] == [7, 10, 11, 12], 'vale tirado do navegador não volta ao recarregar (a marca segura): %s' % [v['n'] for v in vales_gravados()])
        # armazenamento corrompido vale lista vazia, sem quebrar a tela
        limpar(True); pg.evaluate("localStorage.setItem('deskValesCompra', '{nao e json'); localStorage.setItem('deskValesCompraExemplo', '1')"); ir(LISTA)
        ok(len(linhas()) == 0 and pg.evaluate("document.getElementById('emptyState').style.display") != 'none', 'chave ilegível vale lista vazia, e a tela abre com o estado vazio')
        limpar(True); pg.evaluate("localStorage.setItem('deskValesCompra', '{nao e json')"); ir(LISTA)
        ok(len(linhas()) == 5, 'chave ilegível e sem a marca: o exemplo nasce em cima da lista vazia')
        limpar(True)
        # os espelhos: cliente (id, nome, documento) do cadastro, lojas de Lojas Desk, pedidos de Pedidos de Venda
        cad = dict((int(m.group(1)), (m.group(2), m.group(3))) for m in re.finditer(r"\{ id: (\d+), codigo: 'CLI-\d+', tipo: '[a-z]+', nome: '([^']+)', documento: '([^']+)'", fonte(CLI_D)))
        ok(len(cad) == 14, 'o cadastro de clientes tem os 14 do exemplo (para o espelho)')
        ir(LISTA)
        gr = vales_gravados()
        ok(all(cad.get(v['clienteId']) == (v['cliente'], v['doc']) for v in gr), 'todo vale de exemplo é de um cliente que existe no cadastro, com o mesmo nome e o mesmo documento')
        lojas_src = dict((int(m.group(1)), m.group(2)) for m in re.finditer(r"\{ id: (\d), nome: '([^']+)'", fonte(LOJAS_D)))
        ok(all(lojas_src.get(v['loja']) == pg.evaluate("VALE_LOJAS[%d]" % v['loja']) for v in gr) and pg.evaluate("VALE_LOJAS") == dict((str(k), lojas_src[k]) for k in (1, 2, 3)),
           'as três lojas do vale são as de Lojas Desk, com o mesmo nome: %s' % lojas_src)
        peds = {}
        for fonte_ped in (PED_L, PED_D):
            peds[fonte_ped] = dict((int(m.group(1)), (int(m.group(2)), int(m.group(3)), m.group(4), int(m.group(5)))) for m in
                                   re.finditer(r"\{ id: (\d+),\s+numero: (\d+),\s+dv: (-?\d+),[^\n]*?cliente: '([^']+)',[^\n]*?loja: (\d),", fonte(fonte_ped)))
        ok(len(peds[PED_L]) >= 16 and len(peds[PED_D]) >= 16, 'Pedidos de Venda (a lista e a página) têm os pedidos de exemplo para o espelho')
        usos = [(v, u) for v in gr for u in v['usos']]
        ok(len(usos) == 3, 'os três usos do exemplo estão gravados')
        for v, u in usos:
            for tela in (PED_L, PED_D):
                p_ = peds[tela].get(u['pedidoId'])
                ok(bool(p_) and p_[0] == int(u['documento'].split('º ')[1]) and p_[2] == v['cliente'] and p_[3] == v['loja'] and iso(dia(-p_[1])) == u['data'],
                   'o uso de %s no %s existe em %s, do mesmo cliente, da mesma loja e no dia da venda' % (moeda(u['valor']), u['documento'], tela.replace('pagina-vendas-', '').replace('.html', '')))
        ok(pg.evaluate("CLIENTES_VALE.map(c => [c.id, c.nome, c.doc])") == [[k, cad[k][0], cad[k][1]] for k in sorted(cad)], 'a busca de cliente do Incluir vale é o espelho do cadastro (14 clientes, mesmo id, nome e documento)')

    # ================================================================== [2] os indicadores
    if secao(2, 'Os indicadores: saldo, os que vencem em 30 dias e os vencidos com saldo'):
        limpar(True); ir(LISTA)
        k = kpis(vales_gravados())
        txt = lambda i: pg.evaluate("document.getElementById('%s').textContent" % i)
        ok(txt('kpiSaldo') == moeda(170) and txt('kpiSaldoSub') == '2 vales disponíveis' and k['saldo'] == 170, 'de fábrica o saldo em vales é R$ 170,00, em 2 vales disponíveis')
        ok(txt('kpiVence') == '0' and txt('kpiVenceSub') == 'somam R$ 0,00 em saldo', 'de fábrica nenhum vale vence nos próximos 30 dias')
        ok(txt('kpiVencido') == '1' and txt('kpiVencidoSub') == 'somam R$ 50,00 sem usar', 'e há um vencido, de R$ 50,00')
        cenario = [vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 100, 20, 10, usos=[dict(data=iso(dia(-5)), documento='Venda no balcão', pedidoId=0, valor=30)]),
                   vale(2, 2, 'Rafael Nogueira', '234.567.890-11', 1, 40, 20, 30), vale(3, 4, 'Juliana Prado', '345.678.901-22', 2, 25, 20, 31),
                   vale(4, 7, 'Camila Rêgo', '567.890.123-44', 2, 15, 190, -1), vale(5, 11, 'Auto Peças Imperatriz Ltda', '29.887.501/0001-22', 3, 200, 280, -100,
                        usos=[dict(data=iso(dia(-120)), documento='Venda no balcão', pedidoId=0, valor=50)]),
                   vale(6, 12, 'Bruno Carvalho', '890.123.456-77', 1, 80, 20, 160, cancelado=dict(em=iso(dia(-2)), motivo='x', saldo=80)),
                   vale(7, 13, 'Patrícia Farias', '901.234.567-88', 2, 10, 200, -5, usos=[dict(data=iso(dia(-30)), documento='Venda no balcão', pedidoId=0, valor=10)]),
                   vale(8, 10, 'Larissa Monteiro', '789.012.345-66', 3, 5, 20, 0)]
        semear(cenario); ir(LISTA)
        k = kpis(cenario)
        ok((k['n_disp'], k['n30'], k['n_venc']) == (4, 3, 2) and k['saldo'] == 140 and k['s30'] == 115 and k['s_venc'] == 165, 'o cenário de teste tem as contas que se espera: %s' % k)
        ok(txt('kpiSaldo') == moeda(k['saldo']) and txt('kpiSaldoSub') == '4 vales disponíveis', 'saldo em vales: soma o saldo (valor menos usos) só dos disponíveis, e o cancelado e o vencido ficam fora: %s' % txt('kpiSaldo'))
        ok(txt('kpiVence') == '3' and txt('kpiVenceSub') == 'somam %s em saldo' % moeda(k['s30']), 'vencem em 30 dias: o de 10, o de 30 e o que vence hoje contam; o de 31 não: %s, %s' % (txt('kpiVence'), txt('kpiVenceSub')))
        ok(txt('kpiVencido') == '2' and txt('kpiVencidoSub') == 'somam %s sem usar' % moeda(k['s_venc']), 'vencidos com saldo: o de ontem e o de há 100 dias; o usado inteiro, vencido, não conta: %s, %s' % (txt('kpiVencido'), txt('kpiVencidoSub')))
        # os indicadores sao o retrato: nao mexem com a busca, a loja nem a aba
        pg.fill('#campoBusca', 'rafael'); pg.evaluate(ESCOLHE, ['filtroLoja', '3']); pg.evaluate("document.querySelector('.aba-sit[data-sit=\"cancelado\"]').click()"); pg.wait_for_timeout(200)
        ok(txt('kpiSaldo') == moeda(140) and txt('kpiVence') == '3' and txt('kpiVencido') == '2', 'os indicadores não mudam com a busca, a loja nem a aba')
        # 1 vale e "1 vale disponivel", no singular
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 10, 1, 179)]); ir(LISTA)
        ok(txt('kpiSaldoSub') == '1 vale disponível', 'no singular: "1 vale disponível"')

    # ================================================================== [3] busca, filtros e abas
    if secao(3, 'Busca, loja, origem e abas com contagem; o estado que volta pelo endereço'):
        limpar(True); ir(LISTA)
        ns = lambda: [l['n'] for l in linhas()]
        cont = lambda: pg.evaluate("[...document.querySelectorAll('.aba-sit')].map(a => [a.getAttribute('data-sit'), a.querySelector('.sit-contador').textContent])")
        ok(cont() == [['todos', '5'], ['disponivel', '2'], ['usado', '1'], ['vencido', '1'], ['cancelado', '1']], 'as abas abrem com a contagem de todos, disponíveis, usados, vencidos e cancelados: %s' % cont())
        ok(pg.evaluate("document.querySelector('.aba-sit.active').getAttribute('data-sit')") == 'todos', 'e abrem em Todos')
        for sit, esperado in (('vencido', ['VC-1']), ('disponivel', ['VC-4', 'VC-3']), ('usado', ['VC-2']), ('cancelado', ['VC-5']), ('todos', ['VC-5', 'VC-4', 'VC-3', 'VC-2', 'VC-1'])):
            pg.evaluate("(s) => document.querySelector('.aba-sit[data-sit=\"' + s + '\"]').click()", sit); pg.wait_for_timeout(150)
            ok(ns() == esperado, 'a aba %s mostra exatamente %s: %s' % (sit, esperado, ns()))
        for busca, esperado, como in (('rafael', ['VC-2'], 'o primeiro nome'), ('REGO', ['VC-1'], 'sem acento e sem diferença de caixa (Rêgo)'), ('234.567.890-11', ['VC-2'], 'o documento inteiro'),
                                      ('29887501', ['VC-3'], 'o documento só com os dígitos'), ('vc-4', ['VC-4'], 'o número do vale'), ('VC-3', ['VC-3'], 'o número do vale em maiúsculas'),
                                      ('imperatriz', ['VC-3'], 'o meio do nome'), ('zzz', [], 'um nome que não existe')):
            pg.fill('#campoBusca', busca); pg.wait_for_timeout(150)
            ok(ns() == esperado, 'a busca "%s" acha %s (%s): %s' % (busca, esperado, como, ns()))
        ok(pg.evaluate("document.getElementById('emptyState').style.display") != 'none' and pg.evaluate("document.getElementById('wrapVales').style.display") == 'none', 'sem resultado, a lista diz "Nenhum vale neste filtro"')
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(150)
        ok(len(ns()) == 5 and pg.input_value('#campoBusca') == '', 'Limpar filtros traz os cinco de volta e esvazia a busca')
        # loja e origem, e os contadores acompanham os outros filtros
        pg.evaluate(ESCOLHE, ['filtroLoja', '2']); pg.wait_for_timeout(150)
        ok(ns() == ['VC-5', 'VC-1'] and cont() == [['todos', '2'], ['disponivel', '0'], ['usado', '0'], ['vencido', '1'], ['cancelado', '1']], 'a loja Desk Brands deixa VC-5 e VC-1, e os contadores contam só elas: %s' % cont())
        pg.evaluate(ESCOLHE, ['filtroLoja', '1']); pg.wait_for_timeout(150)
        ok(ns() == ['VC-4', 'VC-2'], 'a loja Desk Shope deixa VC-4 e VC-2')
        pg.evaluate(ESCOLHE, ['filtroLoja', 'todas']); pg.evaluate(ESCOLHE, ['filtroOrigem', 'cortesia']); pg.wait_for_timeout(150)
        ok(len(ns()) == 5, 'a origem Cortesia deixa os cinco')
        pg.evaluate(ESCOLHE, ['filtroOrigem', 'devolucao']); pg.wait_for_timeout(150)
        ok(ns() == [] and cont()[0] == ['todos', '0'], 'a origem Devolução não tem vale ainda: lista vazia e Todos em 0')
        ok(pg.evaluate("[...document.querySelectorAll('#menuFiltroOrigem .dropdown-select-item')].map(i => i.textContent)") == ['Todas as origens', 'Devolução', 'Comissão', 'Cortesia'],
           'o filtro de origem oferece devolução, comissão e cortesia')
        pg.evaluate(ESCOLHE, ['filtroOrigem', 'todas'])
        # busca + loja + aba juntas
        pg.fill('#campoBusca', 'a'); pg.evaluate(ESCOLHE, ['filtroLoja', '1']); pg.evaluate("document.querySelector('.aba-sit[data-sit=\"disponivel\"]').click()"); pg.wait_for_timeout(150)
        ok(ns() == ['VC-4'], 'busca, loja e aba valem juntas: %s' % ns())
        ok(pg.evaluate("document.getElementById('somaFiltro').textContent") == moeda(120) and pg.evaluate("document.getElementById('contagemLinhas').textContent") == '1 vale', 'o rodapé conta os vales do filtro e soma o saldo deles')
        # ordem
        limpar(True); ir(LISTA)
        pg.evaluate("document.querySelector('#wrapVales th[data-ordem=\"saldo\"]').click()"); pg.wait_for_timeout(150)
        saldos = [l['saldo'] for l in linhas()]
        num = lambda s: float(s[3:].replace('.', '').replace(',', '.'))
        ok(saldos == sorted(saldos, key=num, reverse=True), 'clicar em Saldo ordena do maior para o menor, como as outras colunas de número: %s' % saldos)
        pg.evaluate("document.querySelector('#wrapVales th[data-ordem=\"saldo\"]').click()"); pg.wait_for_timeout(150)
        ok([num(l['saldo']) for l in linhas()] == sorted(num(s) for s in saldos), 'e o segundo clique inverte')
        pg.evaluate("document.querySelector('#wrapVales th[data-ordem=\"cliente\"]').click()"); pg.wait_for_timeout(150)
        ok([l['cliente'] for l in linhas()] == ['Auto Peças Imperatriz Ltda', 'Camila Rêgo', 'Juliana Prado', 'Marina Duarte', 'Rafael Nogueira'], 'clicar em Cliente ordena de A a Z')
        # o estado volta pelo endereco quando a pagina do vale devolve para a lista
        limpar(True); ir(LISTA, '?q=rafael&loja=1&sit=usado')
        ok(ns() == ['VC-2'] and pg.input_value('#campoBusca') == 'rafael' and pg.evaluate("document.querySelector('#filtroLoja .dropdown-select-label').textContent") == 'Desk Shope' and
           pg.evaluate("document.querySelector('.aba-sit.active').getAttribute('data-sit')") == 'usado', 'a lista abre com o estado que o endereço traz (busca, loja e aba)')
        pg.evaluate("document.querySelector('#corpoTabela tr').click()"); pg.wait_for_timeout(600)
        ok('vale-compra-detalhe.html?id=2' in pg.url and 'q=rafael' in pg.url and 'loja=1' in pg.url and 'sit=usado' in pg.url, 'clicar na linha abre a página do vale e leva o estado no endereço: %s' % pg.url.split('/')[-1])
        href_voltar = pg.get_attribute('#btnVoltarLista', 'href')
        ok(href_voltar.startswith('../financas/pagina-financas-vale-compra.html?') and 'q=rafael' in href_voltar and 'loja=1' in href_voltar and 'sit=usado' in href_voltar, 'o "Voltar" da página do vale leva o mesmo estado de volta: %s' % href_voltar)
        pg.click('#btnVoltarLista'); pg.wait_for_timeout(600)
        ok(ns() == ['VC-2'] and pg.input_value('#campoBusca') == 'rafael' and pg.evaluate("document.querySelector('.aba-sit.active').getAttribute('data-sit')") == 'usado' and
           pg.evaluate("document.querySelector('#filtroLoja .dropdown-select-label').textContent") == 'Desk Shope', 'e a lista volta como estava: a mesma busca, a mesma loja e a mesma aba')
        ir(LISTA, '?q=a&loja=9&origem=xx&sit=zz')
        ok(len(ns()) >= 1 and pg.evaluate("document.getElementById('filtroLoja').getAttribute('data-value')") == 'todas' and pg.evaluate("document.querySelector('.aba-sit.active').getAttribute('data-sit')") == 'todos',
           'loja, origem e aba que não existem no endereço são ignoradas, sem quebrar')
        ir(DET, '?id=1'); ok(pg.get_attribute('#btnVoltarLista', 'href') == '../financas/pagina-financas-vale-compra.html', 'sem estado, o "Voltar" é o endereço simples da lista')
        # o link de outra tela: ?busca=
        ir(LISTA, '?busca=Marina%20Duarte')
        ok(ns() == ['VC-4'] and pg.evaluate("!!document.getElementById('faixaBuscaLink')"), 'o link de outra tela com ?busca= abre a lista filtrada, com a faixa "Mostrar tudo"')
        pg.evaluate("document.querySelector('#faixaBuscaLink button').click()"); pg.wait_for_timeout(200)
        ok(len(ns()) == 5, 'e "Mostrar tudo" desfaz o filtro')

    # ================================================================== [4] incluir vale
    if secao(4, 'Incluir vale: validações, a busca de cliente, senha, vencimento pelo prazo, lista, cadastro e registro'):
        limpar(); ir(LISTA)
        ok(pg.evaluate("document.getElementById('incDrawer').classList.contains('open')") is False, 'o painel abre fechado')
        abrir_incluir()
        ok(pg.evaluate("document.getElementById('incDrawer').classList.contains('open')"), 'o botão "Incluir vale" abre o painel')
        ok(pg.evaluate("document.getElementById('incVencimentoData').textContent") == br(dia(180)) and '180 dias' in pg.evaluate("document.getElementById('incVencimentoSub').textContent"),
           'o vencimento aparece no painel antes de confirmar: hoje mais 180 dias, %s' % br(dia(180)))
        ok(pg.evaluate("[...document.querySelectorAll('#menuIncLoja .dropdown-select-item')].map(i => i.textContent)") == ['Desk Shope', 'Desk Brands', 'Desk Tech'], 'as lojas do painel são as três de Lojas Desk')
        enviar_incluir()
        ok(erros_incluir() == ['IncCliente', 'IncLoja', 'IncValor', 'IncMotivo'] and not modal_aberto(), 'em branco, as quatro validações aparecem e nada vai para a confirmação: %s' % erros_incluir())
        for ruim in ('0', '0,00', 'abc', '-5', '10,555', '1,2,3', ''):
            preencher_incluir('Larissa', 3, ruim, 'Teste'); enviar_incluir()
            ok('IncValor' in erros_incluir() and not modal_aberto(), 'o valor "%s" é recusado' % ruim)
        preencher_incluir('Larissa', 3, '10', '   '); enviar_incluir()
        ok(erros_incluir() == ['IncMotivo'] and not modal_aberto(), 'motivo só com espaços é recusado (e é o único erro): %s' % erros_incluir())
        # a busca de cliente: nome, documento ou e-mail; ate oito sugestoes; Enter escolhe a primeira; mexer no texto desfaz
        pg.fill('#buscaClienteVale', 'Pe'); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('sugestoesCliente').classList.contains('open')") and pg.evaluate("document.querySelectorAll('#sugestoesCliente .sugestao-item').length") >= 2,
           'digitar "Pe" abre as sugestões, com mais de um cliente')
        preencher_incluir('Pe', 3, '10', 'Teste', escolher=False); enviar_incluir()
        ok('IncCliente' in erros_incluir() and not modal_aberto(), 'cliente digitado e não escolhido (várias opções) não passa: pede para escolher na lista')
        for busca, nome in (('789.012.345-66', 'Larissa Monteiro'), ('bruno.carvalho@', 'Bruno Carvalho'), ('MOVEIS', 'Móveis Bom Preço Ltda'), ('papelaria', 'Papelaria Central Ltda')):
            pg.fill('#buscaClienteVale', busca); pg.wait_for_timeout(120); pg.press('#buscaClienteVale', 'Enter'); pg.wait_for_timeout(120)
            ok(pg.input_value('#buscaClienteVale') == nome, 'buscar por "%s" e dar Enter escolhe %s' % (busca, nome))
        pg.fill('#buscaClienteVale', 'Larissa'); pg.press('#buscaClienteVale', 'Enter'); pg.fill('#buscaClienteVale', 'Larissa M'); pg.wait_for_timeout(120)
        ok(pg.evaluate("document.getElementById('btnLimparCliente').style.display") != 'none', 'com texto no campo, o "x" que tira o cliente aparece')
        pg.evaluate("document.getElementById('btnLimparCliente').click()"); pg.wait_for_timeout(120)
        ok(pg.input_value('#buscaClienteVale') == '', 'o "x" esvazia o campo')
        # texto que so casa com um cliente ja e a escolha, no momento de incluir
        preencher_incluir('Larissa', 3, '25,50', 'Cortesia de teste', escolher=False); enviar_incluir()
        ok(modal_aberto() and erros_incluir() == [], 'texto que só casa com um cliente já é a escolha: vai para a confirmação')
        t = texto_modal()
        ok('R$ 25,50' in t and 'Larissa Monteiro' in t and 'Desk Tech' in t and br(dia(180)) in t and 'Cortesia de teste' in t, 'a confirmação diz valor, cliente, loja, vencimento e motivo: %s' % t[:200])
        ok(senha_visivel(), 'incluir vale pede senha por padrão')
        ok(trava_sem_senha() and len(vales_gravados()) == 0, 'sem a senha a confirmação não passa, e nada foi gravado')
        confirmar(); fechar_aviso()
        gr = vales_gravados()
        ok(len(gr) == 1 and gr[0]['n'] == 1 and gr[0]['clienteId'] == 10 and gr[0]['cliente'] == 'Larissa Monteiro' and gr[0]['doc'] == '789.012.345-66' and gr[0]['loja'] == 3 and gr[0]['origem'] == 'cortesia' and
           gr[0]['valor'] == 25.5 and gr[0]['emitido'] == iso(HOJE) and gr[0]['venc'] == iso(dia(180)) and gr[0]['motivo'] == 'Cortesia de teste' and gr[0]['usos'] == [] and gr[0]['cancelado'] is None,
           'o vale gravado: VC-1, Larissa (cliente 10), Desk Tech, cortesia, R$ 25,50, emitido hoje, vence hoje + 180, com o motivo: %s' % gr)
        ls = linhas()
        ok(len(ls) == 1 and ls[0]['n'] == 'VC-1' and ls[0]['sit'] == 'Disponível' and ls[0]['saldo'] == 'R$ 25,50' and ls[0]['vence'] == br(dia(180)), 'o vale entra na lista, disponível, com o saldo e o vencimento')
        ok(not pg.evaluate("document.getElementById('incDrawer').classList.contains('open')"), 'o painel fecha depois de incluir')
        ok(any(e['chave'] == 'valeCompraIncluir' and e['senha'] for e in log()), 'a ação entra no Registro de atividades, com a marca de que passou por senha')
        # o segundo vale: numera depois, limpa os filtros para o novo aparecer, e a lista abre nele
        pg.fill('#campoBusca', 'nada que exista'); pg.wait_for_timeout(100)
        abrir_incluir(); preencher_incluir('Bruno', 1, '1.234,50', 'Atraso na entrega'); enviar_incluir(); confirmar(); fechar_aviso()
        ls = linhas()
        ok([l['n'] for l in ls] == ['VC-2', 'VC-1'] and ls[0]['cliente'] == 'Bruno Carvalho' and ls[0]['valor'] == 'R$ 1.234,50' and pg.input_value('#campoBusca') == '',
           'o segundo vale é VC-2, os filtros se limpam e ele é o primeiro da lista: %s' % [l['n'] for l in ls])
        # o cadastro do cliente mostra o vale
        ir(CLI_D, '?id=10&aba=vale')
        ok('VC-1' in pg.inner_text('#tab-vale') and 'R$ 25,50' in pg.inner_text('#tab-vale'), 'o vale incluído aparece na aba Vale-compra da Larissa Monteiro')
        # cancelar o painel nao grava
        ir(LISTA); abrir_incluir(); preencher_incluir('Larissa', 3, '5', 'x'); enviar_incluir()
        pg.evaluate("document.getElementById('btnConfirmModalCancelar').click()"); pg.wait_for_timeout(200)
        ok(len(vales_gravados()) == 2, 'desistir na confirmação não grava nada')
        # a senha e ligavel e desligavel em Confirmacoes com senha: sem senha, ainda registra
        limpar(); params(confirmacoes=dict(valeCompraIncluir=False)); ir(LISTA)
        abrir_incluir(); preencher_incluir('Larissa', 2, '9', 'Sem senha'); enviar_incluir()
        ok(modal_aberto() and not senha_visivel(), 'com a senha desligada em Confirmações, a confirmação aparece sem o campo de senha')
        confirmar(); fechar_aviso()
        ok(len(vales_gravados()) == 1 and any(e['chave'] == 'valeCompraIncluir' and not e['senha'] for e in log()), 'o vale entra, e o registro de atividades grava a ação sem a marca de senha')
        # o prazo de Configuracoes vale na hora de incluir
        limpar(); params(valeCompraValidadeDias=45); ir(LISTA); abrir_incluir()
        ok(pg.evaluate("document.getElementById('incVencimentoData').textContent") == br(dia(45)) and '45 dias' in pg.evaluate("document.getElementById('incVencimentoSub').textContent"),
           'com o prazo de 45 dias, o painel mostra o vencimento de hoje + 45')
        preencher_incluir('Larissa', 3, '10', 'Prazo curto'); enviar_incluir(); confirmar(); fechar_aviso()
        ok(vales_gravados()[0]['venc'] == iso(dia(45)), 'e o vale nasce vencendo em hoje + 45')
        ok(linhas()[0]['venceTexto'] == 'vence em 45 dias' and pg.evaluate("document.getElementById('kpiVence').textContent") == '0', 'a lista diz "vence em 45 dias", e ele ainda não conta nos que vencem em 30')
        params(valeCompraValidadeDias=30); ir(LISTA)
        ok(pg.evaluate("document.getElementById('kpiVence').textContent") == '0', 'o vale de 45 dias, criado antes, mantém o vencimento de 45 quando o prazo muda para 30 (o indicador não o conta)')
        # prazo corrompido cai no padrao
        params(valeCompraValidadeDias='abc'); ir(LISTA); abrir_incluir()
        ok(pg.evaluate("document.getElementById('incVencimentoData').textContent") == br(dia(180)), 'prazo ilegível em Configurações cai nos 180 dias de fábrica')
        # incluir nao e acao da lista para quem so le: o link do painel vai para a validade
        ok(pg.get_attribute('#incVencimentoSub a', 'href') == '../configuracoes/pagina-configuracoes-cadastro-clientes.html', 'o painel leva a Configurações, onde se muda o prazo')
        limpar()

    # ================================================================== [5] a pagina do vale: cancelar e reativar
    if secao(5, 'A página do vale: dados, usos e histórico; cancelar e reativar'):
        limpar(True); ir(DET, '?id=99')
        ok(pg.evaluate("document.getElementById('avisoSemId').style.display") != 'none' and pg.evaluate("['cardDados', 'cardUsos', 'cardHistorico'].every(i => document.getElementById(i).style.display === 'none')") and
           pg.evaluate("document.getElementById('menuMaisAcoes').style.display") == 'none', 'um endereço sem vale que exista diz isso, esconde os quadros e as ações, e não abre outro vale no lugar')
        ir(DET)
        ok(pg.evaluate("document.getElementById('avisoSemId').style.display") != 'none', 'sem ?id= também')
        # os dados de cada um dos cinco
        ir(DET, '?id=1')
        ok(pg.evaluate("document.getElementById('tituloVale').textContent").startswith('Vale-compra VC-1') and 'Vencido' in pg.evaluate("document.getElementById('tituloVale').textContent"), 'a página do vencido tem o número e a situação no título')
        dados = pg.evaluate("document.getElementById('corpoDados').textContent.replace(/\\s+/g, ' ')")
        ok('Camila Rêgo' in dados and '567.890.123-44' in dados and 'Desk Brands' in dados and 'Cortesia' in dados and 'Troca de tamanho sem estoque na loja' in dados and 'R$ 50,00' in dados and
           br(dia(-200)) in dados and br(dia(-20)) in dados and 'vencido há 20 dias' in dados, 'os dados do vencido: cliente, documento, loja, origem com o motivo, valor, emissão, vencimento e "vencido há 20 dias"')
        ok(pg.evaluate("!!document.querySelector('#corpoDados .com-atraso')") and 'venceu em %s' % br(dia(-20)) in pg.evaluate("document.getElementById('avisoSituacaoTexto').textContent"), 'o vencido aparece em vermelho, e o aviso diz que venceu e o que reativar faz')
        ok(pg.get_attribute('#corpoDados a.com-link', 'href') == '../cadastros/pagina-cadastros-clientes-detalhe.html?id=7&aba=vale', 'o cliente é link para o cadastro dele, na aba Vale-compra')
        ok(pg.evaluate("document.getElementById('breadcrumb').textContent.replace(/\\s+/g, '')") == 'Finanças›Vale-compra›VC-1', 'o caminho no topo diz Finanças, Vale-compra e o número')
        ok(pg.evaluate("document.getElementById('semUsos').style.display") != 'none', 'sem uso, diz que o vale ainda não foi usado')
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
        ok(len(hist) == 2 and hist[0].startswith(br(dia(-20))) and 'Venceu com saldo de R$ 50,00' in hist[0] and hist[1].startswith(br(dia(-200))) and 'Emitido: R$ 50,00' in hist[1], 'o histórico do vencido: venceu (em cima) e emitido: %s' % hist)
        # usos, com o saldo depois
        ir(DET, '?id=2')
        us = pg.evaluate("[...document.querySelectorAll('#corpoUsos tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(us == [[br(dia(-28)), 'Pedido nº 16', 'R$ 25,00', 'R$ 15,00'], [br(dia(-2)), 'Pedido nº 3', 'R$ 15,00', 'R$ 0,00']], 'os usos do vale usado inteiro, em ordem de data, com o saldo depois de cada um: %s' % us)
        ok(pg.evaluate("[...document.querySelectorAll('#corpoUsos a')].map(a => a.getAttribute('href'))") == ['../vendas/pagina-vendas-pedidos-detalhe.html?id=16', '../vendas/pagina-vendas-pedidos-detalhe.html?id=3'], 'o documento do uso é link para o pedido, com o id certo')
        ir(DET, '?id=3')
        us = pg.evaluate("[...document.querySelectorAll('#corpoUsos tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(us == [[br(dia(-11)), 'Pedido nº 10', 'R$ 30,00', 'R$ 50,00']], 'o uso parcial: R$ 30,00 no pedido 10, e sobram R$ 50,00: %s' % us)
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
        ok(len(hist) == 2 and 'Usado: R$ 30,00 em Pedido nº 10' in hist[0] and 'Emitido: R$ 80,00' in hist[1], 'o histórico traz o uso: %s' % hist)
        ir(DET, '?id=5')
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
        ok(len(hist) == 2 and 'Cancelado: R$ 60,00 de saldo cancelados. Motivo: Emitido em duplicidade' in hist[0] and hist[0].startswith(br(dia(-5))), 'o cancelado mostra o cancelamento e o motivo no histórico: %s' % hist[:1])
        ok('Emitido em duplicidade' in pg.evaluate("document.getElementById('avisoSituacaoTexto').textContent") and 'Cancelado' in pg.evaluate("document.getElementById('tituloVale').textContent"), 'e o aviso da página diz o motivo')
        # as acoes que valem para cada situacao
        for n, esperado, quem in ((1, ['reativar', 'cancelar', 'imprimir'], 'vencido'), (4, ['cancelar', 'imprimir'], 'disponível'), (2, ['imprimir'], 'usado'), (5, ['imprimir'], 'cancelado')):
            ir(DET, '?id=%d' % n)
            ok(itens_menu() == esperado, 'o vale %s mostra as ações %s: %s' % (quem, esperado, itens_menu()))
        # cancelar: so com saldo, com motivo e senha, o saldo que resta
        ir(DET, '?id=3'); mais_acao('cancelar')
        ok(pg.evaluate("document.getElementById('canDrawer').classList.contains('open')") and 'R$ 50,00' in pg.evaluate("document.getElementById('canResumo').textContent"), 'cancelar abre o painel e diz o saldo que resta, R$ 50,00')
        pg.evaluate("document.getElementById('btnCancelarVale').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('erroCanMotivo').classList.contains('show')") and not modal_aberto(), 'sem motivo, não cancela')
        pg.evaluate(MUDA, ['#canMotivo', 'Pedido do cliente']); pg.evaluate("document.getElementById('btnCancelarVale').click()"); pg.wait_for_timeout(300)
        ok(modal_aberto() and senha_visivel() and 'R$ 50,00' in texto_modal() and 'Pedido do cliente' in texto_modal(), 'a confirmação pede senha e diz o saldo e o motivo: %s' % texto_modal()[:160])
        ok(trava_sem_senha() and vales_gravados()[2]['cancelado'] is None, 'sem a senha não cancela, e nada foi gravado')
        confirmar(); fechar_aviso()
        v3 = [v for v in vales_gravados() if v['n'] == 3][0]
        ok(v3['cancelado'] == dict(em=iso(HOJE), motivo='Pedido do cliente', saldo=50) and len(v3['usos']) == 1 and v3['valor'] == 80, 'cancelou o saldo que resta (R$ 50,00): o valor e o uso continuam como estavam: %s' % v3['cancelado'])
        ok('Cancelado' in pg.evaluate("document.getElementById('tituloVale').textContent") and 'R$ 0,00' in pg.evaluate("document.getElementById('corpoDados').textContent") and itens_menu() == ['imprimir'], 'a página passa a Cancelado, com saldo zero e sem as ações')
        hist = pg.evaluate("document.querySelector('#corpoHistorico tr').textContent.replace(/\\s+/g, ' ').trim()")
        ok(hist.startswith(br(HOJE)) and 'Cancelado: R$ 50,00 de saldo cancelados. Motivo: Pedido do cliente' in hist, 'o cancelamento é o primeiro do histórico: %s' % hist)
        ok(any(e['chave'] == 'valeCompraCancelar' and e['senha'] for e in log()), 'cancelar entra no Registro de atividades, com senha')
        # nao se cancela o que nao tem saldo, nem por fora do menu
        ir(DET, '?id=2'); pg.evaluate("abrirCancelar()"); pg.wait_for_timeout(200)
        ok(not pg.evaluate("document.getElementById('canDrawer').classList.contains('open')"), 'vale sem saldo não abre o cancelamento nem por fora do menu')
        ir(DET, '?id=3'); pg.evaluate("abrirCancelar()"); pg.wait_for_timeout(200)
        ok(not pg.evaluate("document.getElementById('canDrawer').classList.contains('open')"), 'vale já cancelado também não')
        # a lista e os indicadores acompanham
        ir(LISTA)
        ok(pg.evaluate("document.getElementById('kpiSaldo').textContent") == moeda(120) and linhas()[2]['sit'] == 'Cancelado' and linhas()[2]['saldo'] == 'R$ 0,00', 'na lista o VC-3 está cancelado, sem saldo, e o saldo em vales caiu para R$ 120,00')
        pg.evaluate("document.querySelector('.aba-sit[data-sit=\"cancelado\"]').click()"); pg.wait_for_timeout(150)
        ok([l['n'] for l in linhas()] == ['VC-5', 'VC-3'], 'e ele aparece na aba Cancelados (2)')
        # cancelar um vencido tambem vale (ele tem saldo)
        ir(DET, '?id=1'); mais_acao('cancelar'); pg.evaluate(MUDA, ['#canMotivo', 'Vencido e sem interesse']); pg.evaluate("document.getElementById('btnCancelarVale').click()"); pg.wait_for_timeout(250); confirmar(); fechar_aviso()
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
        ok(len(hist) == 3 and 'Cancelado' in hist[0] and 'Venceu com saldo' in hist[1] and 'Emitido' in hist[2], 'cancelar um vencido guarda as três linhas: cancelado, venceu e emitido: %s' % [h[:40] for h in hist])
        # reativar: so o vencido, com vencimento novo de hoje mais o prazo, e senha
        limpar(True); ir(DET, '?id=1'); mais_acao('reativar')
        t = texto_modal()
        ok(modal_aberto() and senha_visivel() and br(dia(-20)) in t and 'R$ 50,00' in t and br(dia(180)) in t and '180 dias' in t, 'reativar pergunta, com senha, e diz o vencimento novo (hoje + 180): %s' % t[:200])
        ok(trava_sem_senha() and vales_gravados()[0]['venc'] == iso(dia(-20)), 'sem a senha não reativa, e o vencimento não mudou')
        confirmar(); fechar_aviso()
        v1 = [v for v in vales_gravados() if v['n'] == 1][0]
        ok(v1['venc'] == iso(dia(180)) and v1['reativacoes'] == [dict(em=iso(HOJE), de=iso(dia(-20)), para=iso(dia(180)))] and v1['valor'] == 50 and v1['cancelado'] is None,
           'o vale ganha o vencimento novo (hoje + 180) e o histórico guarda de quando para quando: %s' % v1['reativacoes'])
        ok('Disponível' in pg.evaluate("document.getElementById('tituloVale').textContent") and 'vence em 180 dias' in pg.evaluate("document.getElementById('corpoDados').textContent") and itens_menu() == ['cancelar', 'imprimir'],
           'a página passa a Disponível, e a ação de reativar some')
        hist = pg.evaluate("[...document.querySelectorAll('#corpoHistorico tr')].map(tr => tr.textContent.replace(/\\s+/g, ' ').trim())")
        ok(len(hist) == 3 and 'Reativado: o vencimento passou de %s para %s' % (br(dia(-20)), br(dia(180))) in hist[0] and 'Venceu com saldo' in hist[1] and 'Emitido' in hist[2],
           'o histórico: reativado (de quando para quando), venceu e emitido: %s' % [h[:50] for h in hist])
        ok(any(e['chave'] == 'valeCompraReativar' and e['senha'] for e in log()), 'reativar entra no Registro de atividades, com senha')
        ir(LISTA)
        ok(pg.evaluate("document.getElementById('kpiSaldo').textContent") == moeda(220) and pg.evaluate("document.getElementById('kpiVencido').textContent") == '0', 'na lista o saldo em vales sobe para R$ 220,00 e não há mais vencido')
        # o prazo de Configuracoes vale na reativacao
        limpar(True); params(valeCompraValidadeDias=45); ir(DET, '?id=1'); mais_acao('reativar'); confirmar(); fechar_aviso()
        ok([v for v in vales_gravados() if v['n'] == 1][0]['venc'] == iso(dia(45)), 'com o prazo de 45 dias, reativar dá hoje + 45')
        # reativar so o vencido
        for n in (4, 2, 5):
            ir(DET, '?id=%d' % n); pg.evaluate("reativar()"); pg.wait_for_timeout(200)
            ok(not modal_aberto(), 'o vale %d não é vencido, e reativar por fora do menu não abre nada' % n)
        # senha desligada: reativar e cancelar pedem so a confirmacao, e ainda registram
        limpar(True); params(confirmacoes=dict(valeCompraReativar=False)); ir(DET, '?id=1'); mais_acao('reativar')
        ok(modal_aberto() and not senha_visivel(), 'com a senha desligada, reativar confirma sem o campo de senha')
        confirmar(); fechar_aviso()
        ok(any(e['chave'] == 'valeCompraReativar' and not e['senha'] for e in log()), 'e o registro grava sem a marca de senha')
        # origem devolucao ou comissao: o documento de onde o vale nasceu e link
        limpar(); semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 70, 5, 175, origem='devolucao', ref=dict(texto='Devolução nº 7', href='../logistica/pagina-logistica-devolucao-detalhe.html?id=7'))])
        ir(DET, '?id=1')
        ok(pg.evaluate("[...document.querySelectorAll('#corpoDados a')].map(a => [a.textContent, a.getAttribute('href')])")[1] == ['Devolução nº 7', '../logistica/pagina-logistica-devolucao-detalhe.html?id=7'] and 'Devolução' in pg.evaluate("document.getElementById('corpoDados').textContent"),
           'um vale que nasceu de uma devolução mostra a origem e o documento, que é link')
        limpar()

    # ================================================================== [6] Configuracoes
    if secao(6, 'Configurações: a validade do vale grava, tem limites e não muda o vale que já existe'):
        limpar(True); ir(CFG)
        ok('Vale-compra' in pg.inner_text('.main') and pg.input_value('#valeDias') == '180', 'a seção "Vale-compra" abre com o padrão de 180 dias')
        ok(pg.evaluate("PARAM_PADRAO.valeCompraValidadeDias") == 180, 'o padrão de fábrica é 180')
        ok('não muda os que já existem' in pg.inner_text('#campoValeDias').replace('\n', ' ') or 'não muda os que já existem' in pg.evaluate("document.querySelector('#campoValeDias').parentElement.parentElement.textContent"),
           'a dica do campo diz que mudar o prazo não muda os vales que já existem')
        ok(br(dia(180)) in pg.inner_text('#previaVale'), 'a prévia mostra o vencimento de um vale que nascesse hoje: %s' % pg.inner_text('#previaVale')[:80])
        for ruim in ('0', '3651', 'abc', '', '12,5', '-3', '1e3'):
            pg.evaluate(MUDA, ['#valeDias', ruim])
            ok(pg.evaluate("document.getElementById('campoValeDias').classList.contains('has-error')") and pg.evaluate("document.getElementById('erroVale').classList.contains('show')") and 'inválido' in pg.inner_text('#notaBarra'),
               '"%s" dias é recusado, e a barra diz que há campo inválido' % ruim)
        pg.evaluate(MUDA, ['#valeDias', '0']); pg.evaluate("document.getElementById('btnSalvarParam').click()"); pg.wait_for_timeout(300)
        ok('3650' in pg.inner_text('#avisoTexto') and pg.evaluate("localStorage.getItem('deskParametros')") is None, 'salvar com prazo inválido avisa o limite e não grava nada')
        pg.evaluate("document.getElementById('avisoBackdrop').classList.remove('open'); document.getElementById('avisoModal').classList.remove('open')")
        for bom in ('1', '3650', '365'):
            pg.evaluate(MUDA, ['#valeDias', bom])
            ok(not pg.evaluate("document.getElementById('campoValeDias').classList.contains('has-error')"), '"%s" dias é aceito' % bom)
        # as duas pontas do que ja existe: o vale que existe nao muda, o novo usa o prazo novo
        ir(LISTA)
        antes = [(v['n'], v['venc']) for v in vales_gravados()]
        ir(CFG)
        pg.evaluate(MUDA, ['#valeDias', '90']); pg.evaluate("document.getElementById('btnSalvarParam').click()"); pg.wait_for_timeout(300)
        ok('90 dias' in pg.inner_text('#avisoTexto') and 'não mudam' in pg.inner_text('#avisoTexto'), 'salvar diz o prazo novo e que os vales que existem não mudam')
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskParametros')).valeCompraValidadeDias") == 90, 'o prazo fica gravado em deskParametros, com os outros parâmetros')
        ir(CFG)
        ok(pg.input_value('#valeDias') == '90', 'recarregada, a tela mostra os 90 dias')
        ir(LISTA)
        ok([(v['n'], v['venc']) for v in vales_gravados()] == antes, 'o vencimento dos vales que já existiam não mudou: %s' % antes)
        abrir_incluir()
        ok(pg.evaluate("document.getElementById('incVencimentoData').textContent") == br(dia(90)), 'o vale novo vence em hoje + 90')
        preencher_incluir('Larissa', 3, '10', 'Prazo novo'); enviar_incluir(); confirmar(); fechar_aviso()
        ok(vales_gravados()[-1]['venc'] == iso(dia(90)) and [v['venc'] for v in vales_gravados()[:5]] == [a[1] for a in antes], 'e só ele leva o prazo novo')
        # restaurar o padrao
        ir(CFG); pg.evaluate("document.getElementById('btnRestaurarParam').click()")
        ok(pg.input_value('#valeDias') == '180', 'restaurar o padrão volta os 180 dias (na tela; vale quando salvar)')
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskParametros')).valeCompraValidadeDias") == 90, 'e o que está gravado só muda ao salvar')
        limpar()

    # ================================================================== [7] a aba do cliente
    if secao(7, 'A aba Vale-compra do cadastro do cliente: saldo por loja, os vales, o link e o modo leitura'):
        limpar(True); ir(CLI_D, '?id=1')
        ok(pg.evaluate("[...document.querySelectorAll('.tab-item')].map(t => t.textContent.trim())") == ['Dados Gerais', 'Dados Complementares', 'Anexos', 'Observações', 'Afiliado', 'Vale-compra'], 'a aba Vale-compra fica ao lado da aba Afiliado: %s' % pg.evaluate("[...document.querySelectorAll('.tab-item')].map(t => t.textContent.trim())"))
        ok(not pg.evaluate("document.getElementById('tab-vale').classList.contains('active')"), 'a aba abre fechada (a de Dados Gerais é a que abre)')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"vale\"]').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('tab-vale').classList.contains('active')"), 'clicar na aba abre o painel dela')
        sd = pg.evaluate("[...document.querySelectorAll('#tabelaValeSaldos tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(sd == [['Desk Shope', 'R$ 120,00', '1', '%s · vence em 160 dias' % br(dia(160))]], 'saldo por loja da Marina Duarte: Desk Shope, R$ 120,00, 1 vale, e o vencimento: %s' % sd)
        vs = pg.evaluate("[...document.querySelectorAll('#tabelaValeVales tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(vs == [['VC-4', 'Desk Shope', 'Cortesia', br(dia(-20)), '%s · vence em 160 dias' % br(dia(160)), 'R$ 120,00', 'R$ 120,00', 'Disponível']], 'a lista dos vales dela: %s' % vs)
        ok(pg.get_attribute('#tabelaValeVales a', 'href') == '../financas/pagina-financas-vale-compra-detalhe.html?id=4', 'o número do vale é link para a página do vale')
        ok(pg.get_attribute('#linkVerVales', 'href') == '../financas/pagina-financas-vale-compra.html?busca=Marina%20Duarte', 'o link "Ver em Vale-compra" leva à lista filtrada pelo cliente')
        pg.evaluate("document.getElementById('linkVerVales').click()"); pg.wait_for_timeout(700)
        ok('pagina-financas-vale-compra.html' in pg.url and [l['n'] for l in linhas()] == ['VC-4'] and pg.evaluate("!!document.getElementById('faixaBuscaLink')"), 'e a lista abre só com o vale dela, com a faixa dizendo de onde veio o filtro')
        # cada cliente do exemplo
        ir(CLI_D, '?id=2&aba=vale')
        ok(pg.evaluate("document.getElementById('tab-vale').classList.contains('active')"), '?aba=vale abre o cadastro já na aba')
        sd = pg.evaluate("[...document.querySelectorAll('#tabelaValeSaldos tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(sd == [['Desk Shope', 'R$ 0,00', '0', '—']], 'o Rafael Nogueira só tem vale usado: saldo zero, nenhum disponível: %s' % sd)
        ir(CLI_D, '?id=7&aba=vale')
        sd = pg.evaluate("[...document.querySelectorAll('#tabelaValeSaldos tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim()))")
        ok(sd == [['Desk Brands', 'R$ 0,00', '0', '—']] and 'vencido há 20 dias' in pg.inner_text('#tabelaValeVales'), 'a Camila Rêgo tem só um vale vencido: o saldo disponível é zero, e a lista diz "vencido há 20 dias"')
        ok(pg.evaluate("!!document.querySelector('#tabelaValeVales .com-atraso')"), 'e o vencido fica em vermelho')
        ir(CLI_D, '?id=14&aba=vale')
        ok('Este cliente não tem vale-compra' in pg.inner_text('#corpoVale') and pg.evaluate("document.querySelectorAll('#corpoVale table').length") == 0, 'cliente sem vale diz que não tem, e indica onde incluir')
        ir(CLI_D, '?novo=1&aba=vale')
        ok('O cadastro novo ainda não tem vale-compra' in pg.inner_text('#corpoVale'), 'o cadastro novo (em branco) também abre a aba, sem vale')
        # saldo por loja: so a propria loja entra; o vencido e o cancelado ficam fora; nao ha total
        limpar()
        semear([vale(1, 1, 'Marina Duarte', '123.456.789-00', 1, 120, 20, 160), vale(2, 1, 'Marina Duarte', '123.456.789-00', 1, 30, 10, 170),
                vale(3, 1, 'Marina Duarte', '123.456.789-00', 3, 40, 10, 170, usos=[dict(data=iso(dia(-3)), documento='Venda no balcão', pedidoId=0, valor=15)]),
                vale(4, 1, 'Marina Duarte', '123.456.789-00', 3, 99, 200, -20), vale(5, 1, 'Marina Duarte', '123.456.789-00', 2, 77, 5, 175, cancelado=dict(em=iso(dia(-1)), motivo='x', saldo=77)),
                vale(6, 2, 'Rafael Nogueira', '234.567.890-11', 1, 500, 5, 175)])
        ir(CLI_D, '?id=1&aba=vale')
        sd = pg.evaluate("[...document.querySelectorAll('#tabelaValeSaldos tbody tr')].map(tr => [...tr.children].map(td => td.textContent.trim().slice(0, 12)))")
        ok([s[:3] for s in sd] == [['Desk Shope', 'R$ 150,00', '2'], ['Desk Brands', 'R$ 0,00', '0'], ['Desk Tech', 'R$ 25,00', '1']], 'o saldo é por loja: Desk Shope R$ 150,00 (dois vales), Desk Tech R$ 25,00 (o vencido de R$ 99,00 fica fora), Desk Brands zero (o cancelado fica fora): %s' % sd)
        ok(pg.evaluate("document.querySelectorAll('#tabelaValeVales tbody tr').length") == 5 and 'R$ 500,00' not in pg.inner_text('#tab-vale'), 'a lista traz os cinco vales dela, e nenhum de outro cliente')
        ok('Total' not in pg.inner_text('#tab-vale'), 'não há linha de total: o vale não se junta entre lojas')
        # a funcao do bloco comum: o saldo do cliente numa loja
        ok(pg.evaluate("[valeSaldoDoCliente(1, 1), valeSaldoDoCliente(1, 2), valeSaldoDoCliente(1, 3), valeSaldoDoCliente(2, 1), valeSaldoDoCliente(2, 3), valeSaldoDoCliente(99, 1)]") == [150, 0, 25, 500, 0, 0],
           'valeSaldoDoCliente(cliente, loja) soma só os disponíveis daquele cliente naquela loja')
        # modo leitura e edicao
        limpar(True); ir(CLI_D, '?id=1')
        ok(pg.evaluate("document.body.classList.contains('modo-leitura')"), 'o cadastro abre em modo leitura (a preferência de fábrica)')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"vale\"]').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('tab-vale').classList.contains('active')") and pg.evaluate("document.querySelectorAll('#tabelaValeVales tbody tr').length") == 1 and pg.is_visible('#tabelaValeVales'),
           'a aba funciona com o cadastro em modo leitura: abre e mostra a tabela')
        pg.evaluate("[...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Editar cadastro')[0].click()"); pg.wait_for_timeout(300)
        ok(not pg.evaluate("document.body.classList.contains('modo-leitura')") and pg.evaluate("document.getElementById('tab-vale').classList.contains('active')") and pg.is_visible('#tabelaValeVales'),
           'e continua à vista quando se entra em edição')
        ir(CLI_D, '?id=1&aba=vale')
        ok(pg.is_visible('#tabelaValeVales') and pg.evaluate("document.body.classList.contains('modo-leitura')"), '?aba=vale abre a aba em modo leitura')

    # ================================================================== [8] menu e catalogo
    if secao(8, 'O item de menu na posição certa em toda tela, e o catálogo com as três ações'):
        sem, fora, destino = [], [], []
        com_menu = 0
        for arq in localiza.caminhos():
            t = open(arq, encoding='utf-8').read()
            m = re.search(r'<div class="flyout-col" id="flyout-financas">.*?</div>\n  </div>', t, re.S)
            if not m: continue
            com_menu += 1
            rot = re.findall(r'data-label="([^"]+)"', m.group(0))
            if rot != ['Contas a Receber', 'Contas a Pagar', 'Caixa', 'Comissões Afiliados', 'Vale-compra', 'Relatórios Finanças']:
                fora.append((_os.path.basename(arq), rot))
            if re.findall(r'data-label="Vale-compra" data-href="([^"]+)"', m.group(0)) != ['../financas/pagina-financas-vale-compra.html']:
                destino.append(_os.path.basename(arq))
        ok(com_menu >= 84 and not fora, 'em todas as %d telas com menu, "Vale-compra" vem logo depois de "Comissões Afiliados" e antes de Relatórios Finanças: %s' % (com_menu, fora[:2]))
        ok(not destino, 'e leva sempre a ../financas/pagina-financas-vale-compra.html: %s' % destino[:3])
        ir(COM)
        pg.click('.nav-item[data-id="financas"]'); pg.wait_for_timeout(400)
        pg.click('#flyout-financas .flyout-item[data-label="Vale-compra"]'); pg.wait_for_timeout(800)
        ok(pg.url.endswith('pagina-financas-vale-compra.html') and pg.evaluate("document.querySelector('.nav-item.active').getAttribute('data-id')") == 'financas', 'o clique no item abre a lista, com Finanças marcado no menu')
        ok(pg.evaluate("document.getElementById('breadcrumb').textContent.replace(/\\s+/g, '')") == 'Finanças›Vale-compra', 'e o caminho no topo diz Finanças › Vale-compra')
        # o catalogo de acoes
        carregam = [c for c in localiza.caminhos() if "chave:'comissaoReprograma'" in open(c, encoding='utf-8').read()]
        ok(len(carregam) == 17 and any(_os.path.basename(c) == LISTA for c in carregam) and any(_os.path.basename(c) == DET for c in carregam),
           'o catálogo está em 17 telas: as 15 que carregavam e as duas novas: %d' % len(carregam))
        faltam = [_os.path.basename(c) for c in carregam
                  if len(re.findall(r"chave:'valeCompra(?:Incluir|Cancelar|Reativar)'.*exigePadrao:true", open(c, encoding='utf-8').read())) != 3]
        ok(not faltam, 'cada uma traz as três ações (incluir, cancelar, reativar), todas com senha por padrão: %s' % faltam[:3])
        sem_catalogo = [_os.path.basename(c) for c in localiza.caminhos() if 'valeCompraIncluir' in open(c, encoding='utf-8').read() and c not in carregam]
        ok(not sem_catalogo, 'nenhuma tela fora das 17 cita as ações: %s' % sem_catalogo[:3])
        ir(LISTA)
        ok(pg.evaluate("ACOES_SENHA.filter(a => a.chave.indexOf('valeCompra') === 0).map(a => [a.chave, a.nome, a.exigePadrao])") ==
           [['valeCompraIncluir', 'Incluir vale-compra de cortesia', True], ['valeCompraCancelar', 'Cancelar vale-compra', True], ['valeCompraReativar', 'Reativar vale-compra vencido', True]],
           'os nomes são "Incluir vale-compra de cortesia", "Cancelar vale-compra" e "Reativar vale-compra vencido"')
        ir(SENHAS)
        corpo = pg.inner_text('.main')
        ok('Incluir vale-compra de cortesia' in corpo and 'Cancelar vale-compra' in corpo and 'Reativar vale-compra vencido' in corpo, 'as três aparecem em Configurações → Confirmações com senha, onde se liga e desliga a senha')
        ir('pagina-configuracoes-registro-atividades.html')
        ok('Reativar vale-compra vencido' in pg.evaluate("document.body.textContent") or 'valeCompraReativar' in fonte('pagina-configuracoes-registro-atividades.html'), 'e o Registro de atividades conhece as três')

    # ================================================================== [9] bloco identico, impressao e barra de rolagem
    if secao(9, 'O bloco de leitura idêntico nas três cópias, a impressão em relatório e a barra de rolagem'):
        fontes = dict((n, fonte(n)) for n in (LISTA, DET, CLI_D))
        INI, FIM = '  // ===== VALE-COMPRA: DADOS E REGRAS', '  // ===== FIM DO BLOCO VALE-COMPRA ====='
        blocos = [trecho(fontes[n], INI, FIM) for n in (LISTA, DET, CLI_D)]
        ok(blocos[0] == blocos[1] == blocos[2] and len(blocos[0]) > 4000, 'o bloco de leitura do vale é idêntico na lista, na página do vale e no cadastro do cliente (%d caracteres)' % len(blocos[0]))
        ok("localStorage.getItem('deskValesCompra')" in blocos[0] and "localStorage.setItem('deskValesCompraExemplo'" in blocos[0], 'o bloco lê a chave deskValesCompra e grava a marca do exemplo')
        ok(sum(1 for n in (LISTA, DET, CLI_D) if 'function valeSituacao' in fontes[n]) == 3 and all(fontes[n].count('function valeSituacao') == 1 for n in fontes), 'a situação do vale é calculada num lugar só em cada tela, no bloco')
        # a chave so e escrita pelos donos: a lista e a pagina do vale; o cadastro do cliente so le
        ok('valeGravar(' not in fontes[CLI_D].replace(blocos[2], ''), 'o cadastro do cliente só lê: não grava vale')
        # impressao em formato de relatorio
        limpar(True); ir(LISTA)
        pg.evaluate("montarCabecalhoDoRelatorio()")
        cab = pg.inner_text('#relatorioCabecalho') if pg.evaluate("!!document.getElementById('relatorioCabecalho')") else ''
        ok('Vale-compra' in cab and 'Filtros: nenhum, a lista inteira' in cab and '5 registros' in cab and 'Emitido em' in cab, 'a folha do relatório diz o título, quem e quando emitiu, os filtros (nenhum) e a quantidade: %s' % cab.replace('\n', ' | ')[:160])
        pg.evaluate("document.querySelector('.aba-sit[data-sit=\"vencido\"]').click()"); pg.evaluate(ESCOLHE, ['filtroLoja', '2']); pg.fill('#campoBusca', 'rego'); pg.wait_for_timeout(150)
        pg.evaluate("montarCabecalhoDoRelatorio()")
        cab = pg.inner_text('#relatorioCabecalho')
        ok('Situação: Vencidos' in cab and 'Desk Brands' in cab and 'Busca: "rego"' in cab and '1 registro' in cab and '5 registros' not in cab, 'com filtros, a folha os lista (aba, loja, busca) e conta 1 registro: %s' % cab.replace('\n', ' | ')[-120:])
        ok(pg.evaluate("document.body.classList.contains('imprime-lista')"), 'a impressão da lista usa o formato de relatório')
        ir(LISTA)
        tab = pg.evaluate("tabelaDaTela()")
        ok([c.lower() for c in tab['cabecalho'][:2]] == ['nº', 'cliente'] and len(tab['linhas']) == 5 and tab['cabecalho'][-1].lower() == 'situação', 'a planilha leva as colunas e as cinco linhas da tela: %s' % tab['cabecalho'])
        # a barra de rolagem, de 1280 para cima: a lista (no pior caso), a pagina do vale e a aba do cliente
        pior = [vale(1, 11, 'Auto Peças Imperatriz Ltda', '29.887.501/0001-22', 3, 12345.67, 3, 177, usos=[dict(data=iso(dia(-2)), documento='Pedido nº 10', pedidoId=10, valor=2345.67)]),
                vale(2, 3, 'Distribuidora Nordeste Ltda', '41.223.556/0001-09', 2, 9999.99, 300, -120), vale(3, 5, 'Tech Solutions Imperatriz Ltda', '52.998.104/0001-77', 1, 1234.5, 20, 160),
                vale(4, 8, 'Móveis Bom Preço Ltda', '38.114.220/0001-15', 3, 55.5, 20, 160, cancelado=dict(em=iso(dia(-2)), motivo='Emitido em duplicidade, a pedido da loja', saldo=55.5))]
        com_barra = []
        for largura in (1280, 1440):
            pg.set_viewport_size({'width': largura, 'height': 900})
            for rotulo, lista_v in (('fábrica', None), ('pior caso', pior)):
                limpar(True) if lista_v is None else semear(lista_v)
                for tela, q in ((LISTA, ''), (DET, '?id=1'), (DET, '?id=2'), (DET, '?id=3'), (DET, '?id=4'), (DET, '?id=5'), (CLI_D, '?id=1&aba=vale'), (CLI_D, '?id=11&aba=vale')):
                    if lista_v is None and tela == DET and q == '?id=1': pass
                    ir(tela, q)
                    for item in pg.evaluate(MEDE):
                        com_barra.append('%s %s %dpx %s' % (tela.replace('pagina-', '').replace('.html', ''), rotulo + q, largura, item))
        pg.set_viewport_size({'width': 1440, 'height': 900})
        ok(not com_barra, 'nenhuma tabela rola na horizontal, a 1280 e a 1440, na lista, na página do vale e na aba do cliente, nem no pior caso (valores e nomes longos): %s' % com_barra[:4])
        limpar()

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
