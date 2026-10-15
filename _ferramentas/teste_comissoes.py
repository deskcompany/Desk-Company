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
#   [5] Configuracoes: o Programa de afiliados valida, grava, e a lista passa a usar o percentual novo.
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
CHAVES_LOCAIS = ['deskAfiliados', 'deskComissoesAjustes', 'deskComissoesLanc', 'deskParametros', 'deskLog']

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
        saldo0 = pg.evaluate("contaDoMes(B, mesSel, anoSel).saldo")
        pend = pg.evaluate("contaDoMes(B, mesSel, anoSel).itens.filter(i => !i.cancelada && !i.libera).map(i => i.id)")
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
        ok(pg.evaluate("(id) => !contaDoMes(B, mesSel, anoSel).itens.some(i => i.id === id)", pend[0]), 'excluir tira a comissão da conta')
        pg.evaluate("abrirLancamento()"); pg.wait_for_timeout(200)
        pg.evaluate(ESCOLHE, ['lcTipo', 'debito']); pg.evaluate(MUDA, ['#lcValor', '40,00']); pg.evaluate(MUDA, ['#lcDescricao', 'Adiantamento a descontar'])
        pg.evaluate("document.getElementById('btnLcSalvar').click()"); confirmar(); fechar_aviso()
        ok('(−) outros débitos' in pg.inner_text('#corpoResumo').lower() and perto(pg.evaluate("contaDoMes(B, mesSel, anoSel).saldo"), saldo0 - 40),
           'o débito lançado aparece no resumo e tira R$ 40,00 do saldo')
        pg.evaluate("document.querySelector('#corpoLanc [data-remover^=\"n\"]').click()"); confirmar(); fechar_aviso()
        ok(perto(pg.evaluate("contaDoMes(B, mesSel, anoSel).saldo"), saldo0), 'excluir o lançamento devolve o saldo')
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
        ir(CONTA, '?id=v1'); com3 = pg.evaluate("moedaC(contaDoMes(B, mesSel, anoSel).itens.concat([]).filter(i => i.pedido.id === 3)[0].valor)")
        ir(CONTA, '?id=a1'); com4 = pg.evaluate("moedaC(comissoesDe(B).filter(i => i.pedido.id === 4)[0].valor)")
        ok(valores[3] == com3 == 'R$ 17,50' and valores[4] == com4 == 'R$ 30,60', 'a página do pedido e Comissões dão o mesmo valor: %s %s / %s %s' % (valores[3], com3, valores[4], com4))
        sem = [_os.path.basename(c) for c in localiza.caminhos() if 'data-label="Comissões Afiliados" data-href="../financas/pagina-financas-comissoes.html"' not in open(c, encoding='utf-8').read()]
        ok(not sem, 'o item Comissões Afiliados do menu tem destino nas %d telas: %s' % (len(localiza.caminhos()), sem[:3]))
        com_cat = [c for c in localiza.caminhos() if "chave:'comissaoAjusta'" in open(c, encoding='utf-8').read()]
        ok(len(com_cat) == 15 and any('confirmacoes-senha' in c for c in com_cat), 'as três ações novas estão no catálogo de senha das 15 telas que o carregam, Confirmações com senha entre elas')
        fontes = [open(localiza.onde(n), encoding='utf-8').read() for n in (LISTA, CONTA)]
        bloco = lambda t: t[t.index('  // ===== COMISSOES: DADOS E REGRAS'):t.index('  // ===== COMPONENTE: dropdown customizado')]
        ok(bloco(fontes[0]) == bloco(fontes[1]) and len(bloco(fontes[0])) > 6000, 'o bloco de dados e regras é idêntico nas duas telas')

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

    ok(not erros, 'nenhum erro de JavaScript em toda a suíte: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
