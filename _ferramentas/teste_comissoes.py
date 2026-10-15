# -*- coding: utf-8 -*-
# Comissoes Afiliados, entrega 2a (barganha de 14/out/2026).
#
# A lista de Financas > Comissoes Afiliados tem uma linha por quem recebe comissao: vendedor do cadastro ou
# cliente aprovado como afiliado de uma loja (o percentual e o da loja, em Configuracoes > Cadastro de
# clientes). O cliente pede pela vitrine; a aprovacao e aqui. A conta do afiliado segue as linhas do Olist.
# A tela nao guarda venda propria: le os pedidos de Pedidos de Venda, num espelho que esta suite compara.
#
#   [1] Lista: cada linha e cada indicador batem com a conta refeita aqui, em Python, a partir dos pedidos;
#   [2] Inscricoes: aprovar, recusar (com motivo) e incluir afiliado a mao;
#   [3] Conta do afiliado: resumo, pedidos do mes, pendentes; editar, excluir e lancar pedem motivo e senha;
#       suspender; o endereco sem id;
#   [4] Espelhos e ligacoes: pedidos, vendedores, clientes e percentuais iguais as telas donas; o mesmo
#       valor de comissao na pagina do pedido; menu, catalogo de senha e o bloco comum das duas telas;
#   [5] Configuracoes: o Programa de afiliados valida, grava, e a lista passa a usar o percentual novo;
#   [9] Sem barra de rolagem na horizontal em nenhuma tabela, de 1280px para cima, no pior caso do historico (2e);
#   [8] Periodo por data inicial e final, historico com saldo corrente e filtro de mes e ano, historico no cadastro (2d);
#   [7] Historico, saque pedido na vitrine, pago vindo da baixa, a aba Afiliado do cliente e o link do vendedor (2c);
#   [6] Pagamento (entrega 2b): nao passa do saldo, pede senha, desce o saldo e nasce a conta em Contas a Pagar.
from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import os as _os, glob as _g, math, sys
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LISTA, CONTA = 'pagina-financas-comissoes.html', 'pagina-financas-comissoes-detalhe.html'
PV, PV_D, CFG = 'pagina-vendas-pedidos.html', 'pagina-vendas-pedidos-detalhe.html', 'pagina-configuracoes-cadastro-clientes.html'
CHAVES_LOCAIS = ['deskAfiliados', 'deskComissoesAjustes', 'deskComissoesLanc', 'deskComissoesPagas', 'deskSaques', 'deskParametros', 'deskLog']

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
INI = date(HOJE.year, HOJE.month, 1)
redondo = lambda x: math.floor(x + 0.5)
dia = lambda n: HOJE + timedelta(days=n)
base = lambda p: p['total'] - p.get('frete', 0)
comissao = lambda p, pct: redondo(redondo(base(p) * 100) * pct / 100) / 100
no_mes = lambda d: d is not None and d.year == HOJE.year and d.month == HOJE.month


def oraculo(pedidos, b):
    vend = ['Marina Costa', 'Rafael Andrade', '']
    r = dict(pedidos=0, vendido=0.0, lucro=0.0, mes=0.0, anterior=0.0, pendente=0.0)
    for p in pedidos:
        meu = (p.get('ind') and p['ind']['nome'] == b['nome'] and p['loja'] == b.get('loja')) if b['tipo'] == 'cliente' else (not p.get('ind') and vend[p['vend']] == b['nome'])
        if not meu or p['situacao'] == 'cancelado':
            continue
        pct = p['ind']['pct'] if p.get('ind') else b['aliquota']
        v = comissao(p, pct)
        if b['tipo'] == 'cliente':
            lib = dia(p['dp']) + timedelta(days=7)
            libera = lib if p['situacao'] == 'entregue' and lib <= HOJE else None
        else:
            libera = dia(-p['dv']) if p['pago'] else None   # parcial pelas parcelas: o exemplo e pago de uma vez
        if libera is None: r['pendente'] += v
        elif no_mes(libera): r['mes'] += v
        elif libera < INI: r['anterior'] += v
        if no_mes(dia(-p['dv'])):
            r['pedidos'] += 1; r['vendido'] += base(p); r['lucro'] += base(p) - p['custo'] - v
    return r


ESCOLHE = "([dd, v]) => document.querySelector('#' + dd + ' .dropdown-select-item[data-value=\"' + v + '\"]').click()"
MUDA = "([sel, v]) => { const i = document.querySelector(sel); i.value = v; i.dispatchEvent(new Event('input', { bubbles: true })); }"
perto = lambda a, b: abs(a - b) < 0.005

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(350)

    def limpar():
        pg.evaluate("(ks) => ks.forEach(k => localStorage.removeItem(k))", CHAVES_LOCAIS)

    def modal_aberto():
        return pg.evaluate("document.getElementById('confirmModal').classList.contains('open')")

    def confirmar():
        pg.wait_for_timeout(250)
        senha = pg.evaluate("(() => { const c = document.getElementById('campoSenhaModal'); return !!c && getComputedStyle(c).display !== 'none' && c.getClientRects().length > 0; })()")
        if senha:
            pg.fill('#inputSenhaModal', 'senha-de-teste')
        pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(350)
        return senha

    def fechar_aviso():
        pg.wait_for_timeout(200)
        if modal_aberto():
            pg.evaluate("document.getElementById('btnConfirmModalConfirmar').click()"); pg.wait_for_timeout(200)

    ir(PV); PEDIDOS = pg.evaluate("PEDIDOS.filter(p => !p.pdv)")
    PV_CAMPOS = pg.evaluate("PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.numero, p.dv, p.dp, p.cliente, p.doc, p.loja, p.vend, p.total, p.situacao, p.pago, p.frete || 0, p.desconto || 0, p.ind || null, p.custo])")
    ir(LISTA); limpar(); ir(LISTA)

    if secao(1, 'Lista: as linhas e os indicadores batem com a conta refeita a partir dos pedidos'):
        linhas = pg.evaluate("linhas().map(l => ({ chave: l.b.chave, nome: l.b.nome, tipo: l.b.tipo, loja: l.b.loja || null, aliquota: l.b.aliquota, pedidos: l.pedidos, vendido: l.vendido, lucro: l.lucro, mes: l.mes, anterior: l.anterior, pendente: l.pendente, saldo: l.saldo, creditos: l.creditos }))")
        ok([l['nome'] for l in linhas] == ['Marina Costa', 'Ponto Parceiro Vila Mariana', 'Rafael Andrade', 'Bruno Carvalho', 'Larissa Monteiro'],
           'quem recebe: os três vendedores não excluídos e os dois clientes aprovados: %s' % [l['nome'] for l in linhas])
        errados = []
        for l in linhas:
            o = oraculo(PEDIDOS, l)
            for k in ('pedidos', 'vendido', 'lucro', 'mes', 'anterior', 'pendente'):
                if not perto(l[k], o[k]): errados.append('%s.%s: tela %s, conta %s' % (l['nome'], k, l[k], o[k]))
            if not perto(l['saldo'], o['anterior'] + o['mes'] + l['creditos']): errados.append('%s.saldo' % l['nome'])
        ok(not errados, 'pedidos, vendido, lucro, comissão do mês, anterior, a liberar e saldo de cada um batem com a conta refeita: %s' % errados[:3])
        # O total do mes nao basta: tirar os 7 dias do afiliado mudava o dia (02/10 em vez de 09/10) e nao o mes.
        datas_ruins = []
        for chave, tipo in (('a1', 'cliente'), ('v1', 'vendedor')):
            for pid, libera, prevista in pg.evaluate("(k) => comissoesDe(beneficiarioDe(k)).filter(i => !i.cancelada).map(i => [i.pedido.id, i.libera, i.prevista])", chave):
                x = next(q for q in PEDIDOS if q['id'] == pid)
                if tipo == 'cliente':
                    lib = dia(x['dp']) + timedelta(days=7)
                    esp = [lib.isoformat() if x['situacao'] == 'entregue' and lib <= HOJE else '', lib.isoformat()]
                else:
                    esp = [dia(-x['dv']).isoformat() if x['pago'] else '', dia(x['dp']).isoformat()]
                if [libera, prevista] != esp: datas_ruins.append('%s/%d: tela %s, conta %s' % (chave, pid, [libera, prevista], esp))
        ok(not datas_ruins, 'cada comissão libera no dia certo: a do afiliado com o pedido entregue e 7 dias, a da vendedora com o pedido pago: %s' % datas_ruins[:3])
        ok(next(l for l in linhas if l['nome'] == 'Marina Costa')['creditos'] == 150, 'o prêmio lançado à mão entra no saldo da Marina')
        soma = lambda k: sum(l[k] for l in linhas)
        kpi = lambda s: pg.inner_text(s).replace('R$', '').replace('.', '').replace(',', '.').strip()
        ok(perto(float(kpi('#kpiVendido')), soma('vendido')) and int(kpi('#kpiPedidos')) == soma('pedidos') and perto(float(kpi('#kpiSaldo')), soma('saldo'))
           and perto(float(kpi('#kpiComissao')), soma('mes')) and perto(float(kpi('#kpiPendente')), soma('pendente')), 'os indicadores somam as linhas do mês')
        texto_bruno = pg.inner_text('#corpoTabela tr[data-chave="a1"]')
        ok('Cliente afiliado · Desk Brands' in texto_bruno and '5%' in texto_bruno, 'o afiliado aparece com a loja e o percentual dela')
        pg.evaluate(ESCOLHE, ['filtroTipo', 'cliente']); pg.wait_for_timeout(200)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#corpoTabela tr')).map(t => t.getAttribute('data-chave'))") == ['a1', 'a2'], 'o filtro de tipo mostra só os clientes afiliados')
        pg.evaluate("document.getElementById('btnLimparFiltros').click()"); pg.wait_for_timeout(150)
        pg.evaluate("abrirPainel('v1')"); pg.wait_for_timeout(300)
        corpo = pg.inner_text('#drawerCorpo').lower()   # o rotulo vem em maiusculas pelo CSS
        ok('saldo anterior' in corpo and '(=) saldo' in corpo and '(+) outros créditos' in corpo, 'o painel lateral mostra a conta do mês: %s' % corpo.replace('\n', ' ')[:120])
        pg.evaluate("document.getElementById('btnAbrirConta').click()"); pg.wait_for_timeout(700)
        ok(CONTA + '?id=v1&mes=' in pg.url, '"Abrir a conta" leva à conta dela, no mesmo mês: %s' % pg.url.split('/')[-1])

    if secao(2, 'Inscrições: aprovar, recusar e incluir'):
        limpar(); ir(LISTA)
        ok(pg.evaluate("document.querySelectorAll('#corpoInscricoes tr').length") == 2 and 'Camila Rêgo' in pg.inner_text('#corpoInscricoes'), 'chegaram duas inscrições pela vitrine')
        pg.evaluate("document.querySelector('[data-aprovar=\"3\"]').click()"); pg.wait_for_timeout(250)
        ok('5%' in pg.inner_text('#confirmModalTexto') and 'Desk Brands' in pg.inner_text('#confirmModalTexto'), 'aprovar pergunta antes, dizendo a loja e o percentual')
        confirmar(); fechar_aviso()
        ok('Camila Rêgo' not in pg.inner_text('#corpoInscricoes') and pg.evaluate("!!document.querySelector('#corpoTabela tr[data-chave=\"a3\"]')"), 'aprovada, sai da fila e entra na lista')
        pg.evaluate("document.querySelector('[data-recusar=\"4\"]').click()"); pg.wait_for_timeout(250)
        pg.evaluate("document.getElementById('btnRecusar').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('erroMotivoRec').classList.contains('show')") and not modal_aberto(), 'recusar sem motivo não passa, e diz por quê')
        pg.evaluate(MUDA, ['#recMotivo', 'Conta criada há menos de 30 dias']); pg.evaluate("document.getElementById('btnRecusar').click()")
        confirmar(); fechar_aviso()
        ok(pg.evaluate("getComputedStyle(document.getElementById('cardInscricoes')).display") == 'none', 'com a fila vazia, o quadro de inscrições some')
        ir(LISTA)
        ok(pg.evaluate("afiliados().filter(a => a.id === 4)[0].situacao") == 'recusado' and pg.evaluate("!!document.querySelector('#corpoTabela tr[data-chave=\"a3\"]')"), 'a decisão continua depois de recarregar')
        pg.evaluate("abrirIncluir()"); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['incCliente', '12']); pg.wait_for_timeout(150)
        ok(pg.evaluate("Array.from(document.querySelectorAll('#menuIncLoja .dropdown-select-item')).map(i => i.getAttribute('data-value'))") == ['1', '3'] and
           pg.input_value('#incPix') == 'bruno.carvalho@hotmail.com', 'para o Bruno, só as lojas em que ele ainda não é afiliado, e o PIX sugerido é o e-mail do cadastro')
        pg.evaluate(ESCOLHE, ['incCliente', '4']); pg.evaluate(ESCOLHE, ['incLoja', '1']); pg.wait_for_timeout(150)
        pg.evaluate("document.getElementById('btnIncluir').click()"); confirmar(); fechar_aviso()
        ok('Juliana Prado' in pg.inner_text('#corpoTabela') and 'Desk Shope' in pg.inner_text('#corpoTabela'), 'o afiliado incluído à mão entra na lista, com a loja')
        pg.evaluate("abrirIncluir()"); pg.wait_for_timeout(150); pg.evaluate("document.getElementById('btnIncluir').click()"); pg.wait_for_timeout(150)
        ok(pg.evaluate("['erroIncCliente', 'erroIncLoja', 'erroIncPix'].every(i => document.getElementById(i).classList.contains('show'))"), 'incluir sem cliente, loja e PIX mostra as três mensagens')
        pg.evaluate("fecharIncluir()")

    if secao(3, 'Conta do afiliado'):
        limpar(); ir(CONTA, '?id=v1')
        ok(pg.inner_text('#tituloConta') == 'Comissões · Marina Costa' and 'parcelas pagas' in pg.inner_text('#subConta'), 'abre a conta pedida, com a regra dela')
        resumo = pg.inner_text('#corpoResumo').lower()   # o rotulo vem em maiusculas pelo CSS
        ok('comissões pendentes do período anterior' in resumo and 'valor adicional a receber' in resumo and 'total a pagar' in resumo, 'o resumo traz os textos dos (i) do Olist')
        ok('saldo anterior' in resumo and '(−) outros débitos' not in resumo and '(−) pagamentos' not in resumo, 'e só as linhas com valor, além do saldo anterior e do saldo')
        hrefs = pg.evaluate("Array.from(document.querySelectorAll('#corpoPedidos a')).map(a => a.getAttribute('href'))")
        ok(hrefs and all(h.startswith('../vendas/pagina-vendas-pedidos-detalhe.html?id=') for h in hrefs), 'cada pedido do mês abre o pedido: %s' % hrefs[:2])
        saldo0 = pg.evaluate("contaAtual().saldo")
        pend = pg.evaluate("contaAtual().itens.filter(i => !i.cancelada && !i.libera).map(i => i.id)")
        ok(len(pend) >= 1, 'a Marina tem comissão pendente: %s' % pend)
        pg.evaluate("(id) => document.querySelector('[data-ajustar=\"' + id + '\"]').click()", pend[0]); pg.wait_for_timeout(200)
        pg.evaluate(MUDA, ['#ajValor', '50,00']); pg.evaluate("document.getElementById('btnAjSalvar').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('erroAjMotivo').classList.contains('show')") and not modal_aberto(), 'editar sem motivo não passa')
        pg.evaluate(MUDA, ['#ajMotivo', 'Desconto combinado com o cliente']); pg.evaluate("document.getElementById('btnAjSalvar').click()")
        pediu = confirmar(); fechar_aviso()
        ok(pediu, 'mudar comissão pede senha (Confirmações com senha)')
        ok('R$ 50,00' in pg.inner_text('#corpoPendentes') and 'ajustada à mão' in pg.inner_text('#corpoPendentes'), 'a comissão muda e aparece como ajustada à mão')
        ok(pg.evaluate("JSON.parse(localStorage.getItem('deskLog') || '[]').some(l => l.chave === 'comissaoAjusta' && l.detalhe.indexOf('Desconto combinado') >= 0)"), 'e a mudança vai para o registro de atividades, com o motivo')
        pg.evaluate("(id) => document.querySelector('[data-ajustar=\"' + id + '\"]').click()", pend[0]); pg.wait_for_timeout(200)
        pg.evaluate(MUDA, ['#ajMotivo', 'Pedido vai ser refeito']); pg.evaluate("document.getElementById('btnAjExcluir').click()"); confirmar(); fechar_aviso()
        ok(pg.evaluate("(id) => !contaAtual().itens.some(i => i.id === id)", pend[0]), 'excluir tira a comissão da conta')
        pg.evaluate("abrirLancamento()"); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['lcTipo', 'debito']); pg.evaluate(MUDA, ['#lcValor', '40,00']); pg.evaluate(MUDA, ['#lcDescricao', 'Adiantamento a descontar'])
        pg.evaluate("document.getElementById('btnLcSalvar').click()"); confirmar(); fechar_aviso()
        ok('(−) outros débitos' in pg.inner_text('#corpoResumo').lower() and perto(pg.evaluate("contaAtual().saldo"), saldo0 - 40),
           'o débito lançado aparece no resumo e tira R$ 40,00 do saldo')
        pg.evaluate("document.querySelector('#corpoLanc [data-remover^=\"n\"]').click()"); confirmar(); fechar_aviso()
        ok(perto(pg.evaluate("contaAtual().saldo"), saldo0), 'excluir o lançamento devolve o saldo')
        ok(pg.evaluate("getComputedStyle(document.getElementById('itemSuspender')).display") == 'none', 'vendedor não tem "suspender do programa"')
        ir(CONTA, '?id=a1')
        pg.evaluate("document.getElementById('itemSuspender').click()"); confirmar(); fechar_aviso()
        ok('suspenso' in pg.inner_text('#subConta') and pg.inner_text('#itemSuspender') == 'Reativar no programa', 'suspender marca o afiliado e oferece reativar')
        ir(LISTA)
        ok('suspenso' in pg.inner_text('#corpoTabela tr[data-chave="a1"]'), 'e a lista mostra a suspensão')
        ir(CONTA, '?id=zz')
        ok(not modal_aberto() and 'não dizia de quem é a conta' in pg.inner_text('#avisoSemId') and pg.evaluate("getComputedStyle(document.getElementById('avisoSemId')).display") != 'none',
           'endereço sem id que exista: abre a primeira conta e diz isso numa faixa, sem modal por cima')
        ir(CONTA, '?id=v1')
        ok(pg.evaluate("getComputedStyle(document.getElementById('avisoSemId')).display") == 'none', 'com id, a faixa não aparece')

    if secao(4, 'Espelhos e ligações'):
        limpar(); ir(LISTA)
        CAMPOS = "PEDIDOS.filter(p => !p.pdv).map(p => [p.id, p.numero, p.dv, p.dp, p.cliente, p.doc, p.loja, p.vend, p.total, p.situacao, p.pago, p.frete || 0, p.desconto || 0, p.ind || null, p.custo])"
        ok(pg.evaluate(CAMPOS) == PV_CAMPOS and len(PV_CAMPOS) == 16, 'os pedidos de Comissões são os de Pedidos de Venda, campo a campo')
        vend_c, cli_c, afi_c, comum_l = pg.evaluate("VENDEDORES_C"), pg.evaluate("CLIENTES_C"), pg.evaluate("AFILIADOS_C"), None
        padrao_l = pg.evaluate("[1, 2, 3].map(l => PARAM_PADRAO['afiliadoPctLoja' + l]).concat([PARAM_PADRAO.afiliadoLinkDias])")
        ir('pagina-cadastros-vendedores.html')
        cad_v = [{'id': v['id'], 'nome': v['nome'], 'situacao': v['situacao'], 'aliquota': v['aliquotaComissao'], 'regra': v['regraComissao']} for v in pg.evaluate("VENDEDORES") if not v['excluido']]
        ok(vend_c == cad_v, 'os vendedores são os não excluídos do cadastro, com a mesma regra: %s' % [v['nome'] for v in cad_v])
        ir('pagina-cadastros-clientes.html')
        cad_c = {c['id']: c for c in pg.evaluate("CLIENTES")}
        ok(all(c['id'] in cad_c and cad_c[c['id']]['nome'] == c['nome'] and cad_c[c['id']]['documento'] == c['doc'] and cad_c[c['id']]['email'] == c['email'] for c in cli_c) and len(cli_c) == len(cad_c),
           'os clientes para incluir afiliado são os do cadastro, com documento e e-mail')
        ok(all(a['clienteId'] in cad_c and cad_c[a['clienteId']]['nome'] == a['cliente'] and cad_c[a['clienteId']]['documento'] == a['doc'] and cad_c[a['clienteId']]['email'] == a['pix'] for a in afi_c),
           'quem pediu para ser afiliado é cliente do cadastro, e a chave PIX é o e-mail dele')
        ir(CFG)
        ok(pg.evaluate("[1, 2, 3].map(l => PARAM_PADRAO['afiliadoPctLoja' + l]).concat([PARAM_PADRAO.afiliadoLinkDias])") == padrao_l == [4, 5, 3, 30], 'o percentual de cada loja e os 30 dias são os de Configurações')
        ok(all(x['ind']['pct'] == padrao_l[x['loja'] - 1] and x['ind']['tipo'] == 'cliente' for x in PEDIDOS if x.get('ind')), 'cada pedido por link traz o percentual da loja dele, e todo link é de cliente')
        valores = {}
        for pid in (3, 4):
            ir(PV_D, '?id=%d' % pid); pg.evaluate("document.querySelector('.tab-item[data-tab=\"comissoes\"]').click()"); pg.wait_for_timeout(200)
            valores[pid] = pg.inner_text('#resumoComissao').split('\n')[-1].strip()
        ir(CONTA, '?id=v1'); com3 = pg.evaluate("moedaC(contaAtual().itens.concat([]).filter(i => i.pedido.id === 3)[0].valor)")
        ir(CONTA, '?id=a1'); com4 = pg.evaluate("moedaC(comissoesDe(B).filter(i => i.pedido.id === 4)[0].valor)")
        ok(valores[3] == com3 == 'R$ 17,50' and valores[4] == com4 == 'R$ 30,60', 'a página do pedido e Comissões dão o mesmo valor: %s %s / %s %s' % (valores[3], com3, valores[4], com4))
        sem = [_os.path.basename(c) for c in localiza.caminhos() if 'data-label="Comissões Afiliados" data-href="../financas/pagina-financas-comissoes.html"' not in open(c, encoding='utf-8').read()]
        ok(not sem, 'o item Comissões Afiliados do menu tem destino nas %d telas: %s' % (len(localiza.caminhos()), sem[:3]))
        com_cat = [c for c in localiza.caminhos() if "chave:'comissaoAjusta'" in open(c, encoding='utf-8').read()]
        ok(len(com_cat) == 15 and any('confirmacoes-senha' in c for c in com_cat), 'as três ações novas estão no catálogo de senha das 15 telas que o carregam, Confirmações com senha entre elas')
        fontes = [open(localiza.onde(n), encoding='utf-8').read() for n in (LISTA, CONTA, 'pagina-cadastros-clientes-detalhe.html')]
        def bloco(t):
            a = t.index('  // ===== COMISSOES: DADOS E REGRAS')
            return t[a:t.index('  // ===== ', a + 10)]
        ok(bloco(fontes[0]) == bloco(fontes[1]) == bloco(fontes[2]) and len(bloco(fontes[0])) > 6000,
           'o bloco de dados e regras é idêntico nas duas telas de Comissões e no cadastro do cliente (aba Afiliado)')

    if secao(5, 'Configurações: o Programa de afiliados'):
        limpar(); ir(CFG)
        ok('Programa de afiliados' in pg.inner_text('.main') and pg.input_value('#afPct2') == '5' and pg.input_value('#afLinkDias') == '30', 'a seção abre com os padrões')
        pg.evaluate(MUDA, ['#afPct2', '60'])
        ok(pg.evaluate("document.getElementById('campoPct2').classList.contains('has-error')") and 'inválido' in pg.inner_text('#notaBarra'), '60% é recusado, e a barra diz que há campo inválido')
        pg.evaluate(MUDA, ['#afPct2', '6,5']); pg.evaluate("document.getElementById('btnSalvarParam').click()"); pg.wait_for_timeout(300)
        ok('6,5% na Desk Brands' in pg.inner_text('#avisoTexto'), 'salvar diz o percentual novo')
        pg.evaluate("document.getElementById('avisoBackdrop').classList.remove('open'); document.getElementById('avisoModal').classList.remove('open')")
        ir(LISTA)
        ok('6,5%' in pg.inner_text('#corpoTabela tr[data-chave="a1"]'), 'a lista de Comissões passa a mostrar 6,5% para o afiliado da Desk Brands')
        ir(PV_D, '?id=4'); pg.evaluate("document.querySelector('.tab-item[data-tab=\"comissoes\"]').click()"); pg.wait_for_timeout(200)
        ok('5,00%' in pg.inner_text('#resumoComissao'), 'e o pedido já feito continua com o percentual do dia dele (5%)')
        limpar()

    if secao(6, 'Pagamento: a conta nasce em Contas a Pagar'):
        limpar(); ir(CONTA, '?id=v1')
        saldo = pg.evaluate("saldoDeHoje()")
        ok(saldo > 100, 'a Marina tem saldo para pagar hoje: %s' % saldo)
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"pagar\"]').click()"); pg.wait_for_timeout(250)
        ok(pg.input_value('#pgValor') == ('%.2f' % saldo).replace('.', ',') and pg.input_value('#pgVenc') == HOJE.strftime('%d/%m/%Y'), 'o painel abre com o saldo de hoje e vencimento hoje')
        pg.evaluate(MUDA, ['#pgValor', ('%.2f' % (saldo + 10)).replace('.', ',')]); pg.evaluate("document.getElementById('btnPgSalvar').click()"); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.getElementById('erroPgValor').classList.contains('show')") and 'Não passa do saldo' in pg.inner_text('#erroPgValor') and not modal_aberto(),
           'pagar mais que o saldo não passa, e diz o saldo')
        pg.evaluate(MUDA, ['#pgValor', '100,00']); pg.evaluate("document.getElementById('btnPgSalvar').click()")
        pediu = confirmar(); fechar_aviso()
        ok(pediu, 'realizar pagamento pede senha (Confirmações com senha)')
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo - 100) and '(−) pagamentos' in pg.inner_text('#corpoResumo').lower(), 'o saldo desce R$ 100,00 na hora, e o resumo mostra o pagamento')
        href = pg.get_attribute('#corpoPagtos a', 'href')
        ok(href == '../financas/pagina-financas-contas-pagar-detalhe.html?id=9001', 'o pagamento leva à conta a pagar: %s' % href)
        ir('pagina-financas-contas-pagar.html')
        conta = pg.evaluate("(() => { const t = TITULOS.filter(x => x.id === 9001)[0]; return t ? [fornDe(t.fornId).nome, t.valor, t.doc, catDe(t.catId).nome, t.pago, t.vencIso] : null; })()")
        ok(conta == ['Marina Costa', 100, 'COM-1', 'Comissões de vendedores e afiliados', 0, HOJE.isoformat()],
           'em Contas a Pagar, a COM-1 está a pagar, para a Marina, na categoria de comissões, com o vencimento escolhido: %s' % conta)
        ir('pagina-financas-contas-pagar.html', '?busca=Marina Costa')
        ok('COM-1' in pg.inner_text('.main tbody') or 'Marina Costa' in pg.inner_text('.main tbody'), 'e aparece na lista de Contas a Pagar')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        ok('Marina Costa' in pg.inner_text('.main') and '100,00' in pg.inner_text('.main'), 'a página da conta abre a COM-1, com a Marina e o valor')
        # 15/out: o usuario editou a COM-1 para R$ 100 e ela voltou ao valor de Comissoes. O valor e de la: fica travado.
        ok(pg.evaluate("document.getElementById('inputValor').readOnly") and 'Comissões Afiliados' in pg.inner_text('#subtituloConta'),
           'a conta de comissão diz de onde veio e trava o valor, que é de Comissões')
        ok(pg.get_attribute('#origemComissao a', 'href') == '../financas/pagina-financas-comissoes-detalhe.html?id=v1', 'e leva de volta à conta da Marina')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=6')
        ok(not pg.evaluate("document.getElementById('inputValor').readOnly"), 'conta que não é de comissão continua com o valor editável')
        ir(CONTA, '?id=v1')
        pg.evaluate("document.querySelector('[data-cancelar-pg=\"1\"]').click()"); confirmar(); fechar_aviso()
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo) and '(−) pagamentos' not in pg.inner_text('#corpoResumo').lower(), 'cancelar o pagamento devolve o valor ao saldo')
        ir('pagina-financas-contas-pagar.html')
        ok(pg.evaluate("(TITULOS.filter(t => t.id === 9001)[0] || {}).cancelado === true"), 'e a conta fica cancelada em Contas a Pagar, no histórico')
        # Segunda rodada (15/out): cancelar e excluir em Contas a Pagar voltavam ao recarregar. Agora gravam no pagamento.
        ir(CONTA, '?id=v1')
        pg.evaluate("abrirPagamento()"); pg.wait_for_timeout(200); pg.evaluate(MUDA, ['#pgValor', '50,00'])
        pg.evaluate("document.getElementById('btnPgSalvar').click()"); confirmar(); fechar_aviso()
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo - 50), 'um pagamento novo, COM-2, de R$ 50,00')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9002')
        pg.evaluate("document.getElementById('linkCancelarConta').click()"); confirmar(); fechar_aviso()
        ir(CONTA, '?id=v1')
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo), 'cancelar a conta em Contas a Pagar cancela o pagamento: o saldo volta, depois de recarregar')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9002')
        ok(pg.evaluate("conta.cancelado === true"), 'e a conta continua cancelada ao abrir de novo')
        pg.evaluate("document.getElementById('linkCancelarConta').click()"); confirmar(); fechar_aviso()
        ir(CONTA, '?id=v1')
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo - 50), 'reativar a conta reativa o pagamento')
        ir('pagina-financas-contas-pagar.html')
        pg.evaluate("selTit = [9002]; document.getElementById('linkExcluirSelecionadas').click()"); confirmar(); fechar_aviso()
        ir('pagina-financas-contas-pagar.html')
        ok(pg.evaluate("!TITULOS.some(t => t.id === 9002)"), 'excluir a conta na lista some com ela, e ela não volta ao recarregar')
        ir(CONTA, '?id=v1')
        ok(perto(pg.evaluate("saldoDeHoje()"), saldo), 'e o valor volta ao saldo de comissão')
        # 15/out: cancelada pela pagina da conta, ela nao aparecia em "canceladas": o Voltar do navegador trazia a lista
        # da memoria. As telas recarregam quando voltam da memoria (o navegador marca o evento como `persisted`).
        recarregou = []
        for tela in ('pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html', LISTA, CONTA):
            ir(tela)
            pg.evaluate("window.__daMemoria = 1; window.dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true }))"); pg.wait_for_timeout(900)
            recarregou.append(pg.evaluate("typeof window.__daMemoria === 'undefined'"))
        ok(all(recarregou), 'voltar pelo navegador recarrega Contas a Pagar e Comissões, em vez de mostrar a conta como estava: %s' % recarregou)
        fontes = {n: open(c, encoding='utf-8').read() for n, c in ((_os.path.basename(c), c) for c in localiza.caminhos())}
        cp = [fontes[n] for n in ('pagina-financas-contas-pagar.html', 'pagina-financas-contas-pagar-detalhe.html')]
        bl = lambda t: t[t.index('  // ===== CONTAS DE COMISSAO'):t.index('  TITULOS.forEach(t => {')]
        ok(bl(cp[0]) == bl(cp[1]), 'o bloco que lê os pagamentos é o mesmo na lista e na página de Contas a Pagar')
        com_cat = [n for n, t in fontes.items() if "'Comissões de vendedores e afiliados'" in t and 'id:25,' in t]
        ok(len(com_cat) == 8 and 'pagina-configuracoes-categorias-financeiras.html' in com_cat, 'a categoria nova está em Configurações e nas 7 telas que repetem as categorias: %d' % len(com_cat))
        ok(len([n for n, t in fontes.items() if "chave:'comissaoPaga'" in t]) == 15, 'e "Realizar pagamento de comissão" está no catálogo de senha das 15 telas')
        limpar()

    if secao(7, 'Histórico, saque pedido na vitrine, pago e os cadastros (entrega 2c)'):
        limpar(); ir(CONTA, '?id=a1')
        hist = pg.inner_text('#corpoHistorico')
        ok(all(x in hist for x in ['Pediu para ser afiliado da Desk Brands', 'Aprovado no programa de afiliados', 'Venda pelo link: pedido nº 12', 'Comissão liberada: pedido nº 12', 'Pediu o saque pela vitrine']),
           'o histórico do Bruno traz a inscrição, a aprovação, as vendas, a comissão liberada e o saque pedido')
        datas = pg.evaluate("historicoDe(B).map(e => e.data)")
        ok(datas == sorted(datas, reverse=True) and len(datas) >= 6, 'do mais novo para o mais velho: %d eventos' % len(datas))
        ok(pg.evaluate("getComputedStyle(document.getElementById('avisoSaque')).display") != 'none' and 'R$ 51,20' in pg.inner_text('#avisoSaque'), 'a conta avisa do saque que espera aprovação')
        ir(LISTA)
        ok('Bruno Carvalho' in pg.inner_text('#corpoSaques') and pg.inner_text('#minimoSaque') == 'R$ 50,00', 'a lista mostra o saque pedido, com o mínimo do programa')
        pg.evaluate("document.querySelector('[data-recusar-saque=\"1\"]').click()"); pg.wait_for_timeout(200)
        pg.evaluate("document.getElementById('btnRecusar').click()"); pg.wait_for_timeout(150)
        ok(pg.evaluate("document.getElementById('erroMotivoRec').classList.contains('show')") and not modal_aberto(), 'recusar o saque sem motivo não passa')
        pg.evaluate(MUDA, ['#recMotivo', 'Chave PIX inválida']); pg.evaluate("document.getElementById('btnRecusar').click()"); confirmar(); fechar_aviso()
        ok(pg.evaluate("getComputedStyle(document.getElementById('cardSaques')).display") == 'none' and pg.evaluate("saques()[0].situacao") == 'recusado', 'recusado, o saque sai da fila')
        ir(CONTA, '?id=a1')
        ok('Saque recusado: Chave PIX inválida' in pg.inner_text('#corpoHistorico') and pg.evaluate("getComputedStyle(document.getElementById('avisoSaque')).display") == 'none',
           'e o histórico diz o motivo, sem a faixa de saque pendente')
        limpar(); ir(LISTA)
        saldo0 = pg.evaluate("saldoHoje(beneficiarioDe('a1'))")
        pg.evaluate("document.querySelector('[data-aprovar-saque=\"1\"]').click()"); pediu = confirmar(); fechar_aviso()
        ok(pediu and perto(pg.evaluate("saldoHoje(beneficiarioDe('a1'))"), saldo0 - 51.20) and pg.evaluate("getComputedStyle(document.getElementById('cardSaques')).display") == 'none',
           'aprovar pede senha, faz o pagamento (o saldo desce R$ 51,20) e tira o saque da fila')
        ir('pagina-financas-contas-pagar.html')
        ok(pg.evaluate("(() => { const t = TITULOS.filter(x => x.id === 9001)[0]; return !!t && fornDe(t.fornId).nome === 'Bruno Carvalho' && t.valor === 51.2; })()"), 'e nasce a COM-1 em Contas a Pagar, para o Bruno')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        pg.evaluate("document.getElementById('btnDarBaixa').click()"); pg.wait_for_timeout(300)
        pg.evaluate("document.getElementById('btnConfirmarPagamento').click()"); confirmar(); fechar_aviso()
        ok(pg.evaluate("(JSON.parse(localStorage.getItem('deskComissoesPagas')).pagamentos[0].baixas || []).length") == 1, 'a baixa em Contas a Pagar volta para o pagamento de Comissões')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        ok(pg.evaluate("conta.pago") == 51.2, 'e a conta continua paga depois de recarregar')
        ir(CONTA, '?id=a1')
        ok('pago em ' in pg.inner_text('#corpoPagtos') and 'COM-1 pago em Contas a Pagar' in pg.inner_text('#corpoHistorico'), 'Comissões mostra o pagamento como pago, e o histórico também')
        ok('cancelar' not in pg.inner_text('#corpoPagtos'), 'pagamento já pago não se cancela por Comissões')
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        pg.evaluate("estornar(0)"); confirmar(); fechar_aviso()
        ir(CONTA, '?id=a1')
        ok('a pagar até' in pg.inner_text('#corpoPagtos'), 'estornar a baixa em Contas a Pagar devolve o pagamento para "a pagar"')
        ir('pagina-cadastros-clientes-detalhe.html', '?id=12')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"afiliado\"]').click()"); pg.wait_for_timeout(200)
        txt = pg.inner_text('#corpoAfiliado')
        ok(pg.evaluate("getComputedStyle(document.getElementById('tab-afiliado')).display") != 'none' and all(x in txt for x in ['Desk Brands', 'ativo', '5%', 'R$ 51,20']),
           'o cadastro do Bruno tem a aba Afiliado: loja, situação, comissão e o pagamento feito: %s' % txt.replace(chr(10), ' ')[:120])
        ok(pg.get_attribute('#corpoAfiliado a', 'href') == '../financas/pagina-financas-comissoes-detalhe.html?id=a1', 'e leva à conta de comissões dele')
        ir('pagina-cadastros-clientes-detalhe.html', '?id=4')
        ok('não participa do programa' in pg.inner_text('#corpoAfiliado'), 'cliente fora do programa diz isso, com o caminho para convidar')
        ir('pagina-cadastros-vendedores-detalhe.html', '?id=1')
        ok(pg.get_attribute('#linkContaComissoes', 'href') == '../financas/pagina-financas-comissoes-detalhe.html?id=v1', 'o cadastro do vendedor leva à conta de comissões dele')
        ir(CFG)
        ok(pg.input_value('#afSaqueMin') == '50', 'Configurações tem o saque mínimo, 50 reais')
        pg.evaluate(MUDA, ['#afSaqueMin', 'abc'])
        ok(pg.evaluate("document.getElementById('campoSaque').classList.contains('has-error')"), 'e recusa o que não é valor')
        limpar()

    if secao(8, 'Data inicial e final, histórico com saldo e o histórico no cadastro (entrega 2d)'):
        limpar(); ir(CONTA, '?id=v1')
        ini = HOJE.replace(day=1)
        fim = ((ini.replace(day=28) + timedelta(days=4)).replace(day=1)) - timedelta(days=1)
        br = lambda d: d.strftime('%d/%m/%Y')
        ok(pg.input_value('#dataIni') == br(ini) and pg.input_value('#dataFim') == br(fim), 'a conta abre no mês inteiro, com data inicial e final')
        ok(pg.evaluate("document.getElementById('filtroMes') === null && document.getElementById('filtroAno') === null"), 'e o mês e o ano em lista suspensa saíram do topo')
        ok(('Período: ' + br(ini) + ' a ' + br(fim)) in pg.inner_text('#periodoConta'), 'o período aparece escrito sob o título, e por isso vai para o papel')
        ok('(+) comissões do mês' in pg.inner_text('#corpoResumo').lower(), 'mês inteiro: a linha se chama "do mês"')
        mes_cheio = pg.evaluate("contaAtual()")
        ir(CONTA, '?id=v1&mes=%d&ano=%d' % (HOJE.month, HOJE.year))
        ok(pg.input_value('#dataIni') == br(ini) and perto(pg.evaluate("contaAtual().saldo"), mes_cheio['saldo']), '?mes= e ?ano= da lista viram o mês inteiro')
        ir(CONTA, '?id=v1&inicio=%s&fim=%s' % (ini.isoformat(), HOJE.isoformat()))
        ok(pg.input_value('#dataFim') == br(HOJE), '?inicio= e ?fim= abrem o período pedido')

        def periodo(de, ate):
            pg.fill('#dataIni', br(de)); pg.fill('#dataFim', br(ate)); pg.keyboard.press('Enter'); pg.wait_for_timeout(250)

        def da_marina(a, b):   # a conta refeita aqui: pedidos da Marina, sem link, nao cancelados, vendidos entre as duas datas
            return [q for q in PEDIDOS if not q.get('ind') and q['vend'] == 0 and q['situacao'] != 'cancelado' and a <= HOJE - timedelta(days=q['dv']) <= b]
        ir(CONTA, '?id=v1')
        periodo(ini, ini + timedelta(days=4))
        c1 = pg.evaluate("contaAtual()")
        ok('(+) comissões do período' in pg.inner_text('#corpoResumo').lower() and ('Período: %s a %s' % (br(ini), br(ini + timedelta(days=4)))) in pg.inner_text('#periodoConta'),
           'período que não é um mês: a linha se chama "do período" e o período é o escrito')
        esperados = da_marina(ini, ini + timedelta(days=4))
        ok(c1['pedidos'] == len(esperados) and perto(c1['vendido'], sum(q['total'] - q.get('frete', 0) for q in esperados)),
           'os pedidos e o vendido do período são os da data inicial à final: %d pedido(s)' % len(esperados))
        # periodos seguidos: o saldo do fim de um, sem os lancamentos que valem pelo mes, e o saldo anterior do seguinte
        periodo(ini, ini + timedelta(days=9)); ca = pg.evaluate("contaAtual()")
        periodo(ini + timedelta(days=10), fim); cb = pg.evaluate("contaAtual()")
        ok(perto(cb['anterior'], ca['saldo'] - ca['creditos'] + ca['debitos']),
           'períodos seguidos fecham: o saldo anterior do segundo é o saldo do primeiro, menos os lançamentos do mês (que valem pelo mês a que se referem)')
        ok(ca['creditos'] == cb['creditos'] == 150, 'o prêmio de R$ 150, referente ao mês, entra nos dois períodos que tocam o mês')
        periodo(ini + timedelta(days=9), ini + timedelta(days=2))
        ok(pg.evaluate("document.getElementById('erroPeriodo').classList.contains('show')") and 'depois da final' in pg.inner_text('#erroPeriodo')
           and pg.evaluate("document.getElementById('campoDataIni').classList.contains('has-error')"), 'data inicial depois da final diz o erro e marca o campo')
        pg.fill('#dataIni', '32/13/2026'); pg.keyboard.press('Enter'); pg.wait_for_timeout(200)
        ok('formato dd/mm/aaaa' in pg.inner_text('#erroPeriodo'), 'data que não existe diz o formato')
        pg.evaluate("document.getElementById('btnMesAtual').click()"); pg.wait_for_timeout(250)
        ok(pg.input_value('#dataIni') == br(ini) and pg.input_value('#dataFim') == br(fim) and not pg.evaluate("document.getElementById('erroPeriodo').classList.contains('show')"),
           '"Mês atual" volta ao mês inteiro e limpa o erro')
        pg.evaluate("document.querySelector('#dfIni .date-btn').click()"); pg.wait_for_timeout(250)
        ok(pg.evaluate("document.querySelector('#dfIni .date-pop').classList.contains('open')") and pg.evaluate("document.querySelectorAll('#dfIni .date-dia[data-iso]').length") >= 28,
           'o calendário abre no botão da data inicial')
        dia3 = ini + timedelta(days=2)
        pg.evaluate("document.querySelector('#dfIni .date-dia[data-iso=\"%s\"]').click()" % dia3.isoformat()); pg.wait_for_timeout(250)
        ok(pg.input_value('#dataIni') == br(dia3) and ('Período: ' + br(dia3)) in pg.inner_text('#periodoConta'), 'escolher o dia no calendário aplica o período')

        # o historico: tipo, efeito, saldo corrente, links, e o filtro so de mes e ano
        ir(CONTA, '?id=a1')
        ev = pg.evaluate("historicoDe(B)")
        ok(all(e['tipo'] in ('inscricao', 'venda', 'comissao', 'saque', 'pagamento', 'lancamento') for e in ev) and len(ev) >= 7, 'cada acontecimento do histórico tem tipo: %d' % len(ev))
        ok(perto(ev[0]['saldo'], pg.evaluate("saldoDeHoje()")), 'o saldo do acontecimento mais novo é o saldo de hoje da conta (%s)' % ev[0]['saldo'])
        ok(all(perto(a['saldo'] - b2['saldo'], a['efeito'] or 0) for a, b2 in zip(ev, ev[1:])), 'e cada saldo é o anterior mais o efeito: a conta fecha linha a linha')
        for chave in ('v1', 'v2', 'a2'):
            ir(CONTA, '?id=' + chave)
            ok(perto(pg.evaluate("(historicoDe(B)[0] || { saldo: 0 }).saldo"), pg.evaluate("saldoDeHoje()")), 'o mesmo para a conta %s (sem acontecimento, o saldo é zero)' % chave)
        ir(CONTA, '?id=a1')
        n_hist = pg.evaluate("document.querySelectorAll('#corpoHistorico tr').length")
        cab = pg.evaluate("Array.from(document.querySelectorAll('#wrapHistorico thead th')).map(t => t.textContent.trim())")
        ok(cab == ['Data', 'Tipo', 'O que aconteceu', 'Valor', 'Efeito', 'Saldo'], 'a tabela tem tipo, valor, efeito e saldo, com o cabeçalho curto: %s' % cab)
        ok(pg.get_attribute('#corpoHistorico a[href*="pedidos-detalhe"]', 'href').startswith('../vendas/pagina-vendas-pedidos-detalhe.html?id='), 'o pedido do histórico abre o pedido')
        anos = pg.evaluate("Array.from(document.querySelectorAll('#menuHistAno .dropdown-select-item')).map(i => i.getAttribute('data-value'))")
        meses = pg.evaluate("document.querySelectorAll('#menuHistMes .dropdown-select-item').length")
        ok(anos[0] == 'todos' and str(HOJE.year) in anos and meses == 13, 'o filtro do histórico é só mês e ano: %d meses (com "todos") e anos %s' % (meses, anos))
        ok(not pg.evaluate("!!document.querySelector('.com-hist-filtros input, .com-hist-filtros .date-field')"), 'e nenhum campo de data no histórico')
        tipos = pg.evaluate("Array.from(document.querySelectorAll('#menuHistTipo .dropdown-select-item')).map(i => i.getAttribute('data-value'))")
        ok(tipos == ['todos', 'inscricao', 'venda', 'comissao', 'saque', 'pagamento', 'lancamento'], 'e também por tipo: %s' % tipos)
        pg.evaluate(ESCOLHE, ['histTipo', 'venda']); pg.wait_for_timeout(250)
        so_vendas = pg.evaluate("Array.from(document.querySelectorAll('#corpoHistorico .com-tipo')).map(t => t.textContent.trim())")
        ok(len(so_vendas) == len([e for e in ev if e['tipo'] == 'venda']) and len(so_vendas) > 0 and set(so_vendas) == {'Venda'} and len(so_vendas) < n_hist,
           'escolher "Venda" mostra só as vendas: %d de %d' % (len(so_vendas), n_hist))
        mes_com = int([e for e in ev if e['tipo'] == 'comissao'][0]['data'][5:7])
        pg.evaluate(ESCOLHE, ['histTipo', 'comissao']); pg.evaluate(ESCOLHE, ['histMes', str(mes_com)]); pg.wait_for_timeout(250)
        junto = pg.evaluate("Array.from(document.querySelectorAll('#corpoHistorico tr')).map(r => [r.children[0].textContent.slice(3, 5), r.children[1].textContent.trim()])")
        esperado_junto = [e for e in ev if e['tipo'] == 'comissao' and int(e['data'][5:7]) == mes_com]
        ok(len(junto) == len(esperado_junto) > 0 and all(x[1] == 'Comissão' and int(x[0]) == mes_com for x in junto),
           'tipo e mês funcionam juntos: %d comissão(ões) de %02d' % (len(junto), mes_com))
        pg.evaluate(ESCOLHE, ['histTipo', 'todos']); pg.evaluate(ESCOLHE, ['histMes', 'todos']); pg.wait_for_timeout(200)
        usados = sorted(set(int(e['data'][5:7]) for e in ev))
        mes_velho = int(ev[-1]['data'][5:7])
        pg.evaluate(ESCOLHE, ['histMes', str(mes_velho)]); pg.wait_for_timeout(250)
        so_mes = pg.evaluate("Array.from(document.querySelectorAll('#corpoHistorico tr td:first-child')).map(t => Number(t.textContent.slice(3, 5)))")
        ok(len(so_mes) == len([e for e in ev if int(e['data'][5:7]) == mes_velho]) and set(so_mes) == {mes_velho} and len(so_mes) < n_hist,
           'escolher o mês de %02d mostra só os acontecimentos dele: %d de %d' % (mes_velho, len(so_mes), n_hist))
        ok(pg.evaluate("document.getElementById('contHistorico').textContent").endswith('de %d' % n_hist), 'o contador diz quantos são de quantos')
        ok(perto(pg.evaluate("historicoDe(B)[0].saldo"), ev[0]['saldo']), 'o saldo de cada linha não muda com o filtro')
        livre = [m for m in range(1, 13) if m not in usados][0]
        pg.evaluate(ESCOLHE, ['histMes', str(livre)]); pg.wait_for_timeout(250)
        ok('Nada com este mês, ano e tipo' in pg.inner_text('#semHistorico') and pg.evaluate("getComputedStyle(document.getElementById('semHistorico')).display") != 'none',
           'mês sem acontecimento diz isso')
        pg.evaluate(ESCOLHE, ['histMes', 'todos']); pg.wait_for_timeout(200)
        ok(pg.evaluate("document.querySelectorAll('#corpoHistorico tr').length") == n_hist, '"Todos" devolve o histórico inteiro')

        # o que o usuario viu faltar no cadastro: o saque aprovado e o pagamento excluido em Contas a Pagar
        limpar(); ir(LISTA)
        pg.evaluate("document.querySelector('[data-aprovar-saque=\"1\"]').click()"); confirmar(); fechar_aviso()
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        pg.evaluate("document.getElementById('linkExcluirConta').click()"); confirmar()
        pg.wait_for_timeout(500)
        ir(CONTA, '?id=a1')
        h = pg.inner_text('#corpoHistorico')
        ok('Saque aprovado: virou o pagamento COM-1' in h and 'excluído em Contas a Pagar' in h and 'o cliente pode pedir de novo' in h,
           'o histórico da conta tem o saque aprovado e o pagamento excluído em Contas a Pagar')
        # O saldo corrente tem de fechar tambem depois do pagamento excluido: sai R$ 51,20 e volta R$ 51,20.
        ok(perto(pg.evaluate("historicoDe(B)[0].saldo"), pg.evaluate("saldoDeHoje()")) and perto(pg.evaluate("saldoDeHoje()"), 51.2),
           'depois do pagamento excluído, o saldo do acontecimento mais novo continua sendo o saldo de hoje (R$ 51,20)')
        na_conta = pg.evaluate("historicoDe(B).length")
        ir('pagina-cadastros-clientes-detalhe.html', '?id=12')
        pg.evaluate("document.querySelector('.tab-item[data-tab=\"afiliado\"]').click()"); pg.wait_for_timeout(250)
        ch = pg.inner_text('#corpoAfiHistorico')
        ok('Saque aprovado: virou o pagamento COM-1' in ch and 'excluído em Contas a Pagar' in ch and 'Desk Brands' in ch,
           'o cadastro do cliente mostra o mesmo histórico, inclusive o pagamento excluído')
        ok(pg.evaluate("document.querySelectorAll('#corpoAfiHistorico tbody tr').length") == na_conta, 'com os mesmos %d acontecimentos da conta' % na_conta)
        ok(pg.evaluate("getComputedStyle(document.getElementById('afiHistMes')).display") != 'none' and pg.evaluate("document.body.classList.contains('modo-leitura')"),
           'o filtro de mês e ano aparece com o cadastro em modo leitura')
        ok(pg.evaluate("Array.from(document.querySelectorAll('#menuAfiHistTipo .dropdown-select-item')).length") == 7, 'o cadastro filtra por tipo, com os mesmos seis tipos')
        pg.evaluate(ESCOLHE, ['afiHistTipo', 'pagamento']); pg.wait_for_timeout(250)
        pagos = pg.evaluate("Array.from(document.querySelectorAll('#corpoAfiHistorico .com-tipo')).map(t => t.textContent.trim())")
        ok(len(pagos) >= 2 and set(pagos) == {'Pagamento'}, 'e "Pagamento" mostra o pagamento e o pagamento excluído: %d' % len(pagos))
        pg.evaluate(ESCOLHE, ['afiHistTipo', 'todos']); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['afiHistMes', str(livre)]); pg.wait_for_timeout(250)
        ok('Nada com este mês, ano e tipo' in pg.inner_text('#corpoAfiHistorico') and ' de %d' % na_conta in pg.inner_text('#corpoAfiHistorico .afi-loja'),
           'e filtra o histórico do cadastro por mês')
        ir('pagina-cadastros-clientes-detalhe.html', '?id=4')
        ok(pg.evaluate("getComputedStyle(document.getElementById('afiHistorico')).display") == 'none', 'cliente fora do programa não mostra histórico')
        limpar()

    if secao(9, 'Sem barra de rolagem na horizontal (entrega 2e)'):
        # 15/out: o usuario viu a barra no historico, e pediu a regra para as paginas. O pior caso do historico e a frase do
        # pagamento excluido; a tabela tem de caber no cartao a partir de 1280px, e a pagina nao pode rolar.
        limpar(); ir(LISTA)
        pg.evaluate("document.querySelector('[data-aprovar-saque=\"1\"]').click()"); confirmar(); fechar_aviso()
        ir('pagina-financas-contas-pagar-detalhe.html', '?id=9001')
        pg.evaluate("document.getElementById('linkExcluirConta').click()"); confirmar(); pg.wait_for_timeout(500)
        MEDE = """() => {
          const vis = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
          const r = [];
          document.querySelectorAll('.estoque-table-wrap, .contatos-table').forEach(w => {
            if (!vis(w)) return;
            const eh = w.classList.contains('contatos-table');
            const caixa = eh ? w.parentElement : w, tab = eh ? w : w.querySelector('table');
            const larg = Math.round(tab ? tab.scrollWidth : w.scrollWidth), cab = Math.round(caixa.clientWidth);
            if (larg > cab + 1) r.push((w.id || w.className) + ' ' + larg + ' > ' + cab);
          });
          if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) r.push('a pagina rola');
          return r;
        }"""
        telas = [(LISTA, ''), (CONTA, '?id=a1'), (CONTA, '?id=v1'), ('pagina-cadastros-clientes-detalhe.html', '?id=12')]
        com_barra = []
        for largura in (1280, 1440):
            pg.set_viewport_size({'width': largura, 'height': 900})
            for tela, q in telas:
                ir(tela, q)
                if 'cadastros' in tela:
                    pg.evaluate("document.querySelector('.tab-item[data-tab=\"afiliado\"]').click()"); pg.wait_for_timeout(250)
                    ok(pg.evaluate("document.querySelectorAll('#corpoAfiHistorico tbody tr').length") > 0, 'o histórico do cadastro está na tela para medir')
                for item in pg.evaluate(MEDE):
                    com_barra.append('%s %dpx %s' % (tela.replace('pagina-', '').replace('.html', ''), largura, item))
        pg.set_viewport_size({'width': 1440, 'height': 900})
        ok(not com_barra, 'nenhuma tabela das telas de Comissões nem do histórico no cadastro tem barra na horizontal, e a página não rola: %s' % com_barra[:4])
        ir(CONTA, '?id=a1')
        ok(pg.evaluate("getComputedStyle(document.querySelector('#corpoHistorico td.col-texto:nth-child(3)')).whiteSpace") == 'normal',
           'a frase do histórico quebra linha, em vez de alargar a tabela')
        limpar()

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
