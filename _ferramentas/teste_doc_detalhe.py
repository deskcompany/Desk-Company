# -*- coding: utf-8 -*-
# A pagina do documento abre o registro clicado (item G3, segunda parte — 13/out/2026).
#
# A primeira parte, dos cinco cadastros, esta em teste_cad_detalhe.py. Aqui entram os documentos:
# a pagina desenhava um exemplo fixo, e qualquer linha clicada abria o mesmo.
#
#   [1] Ordens de Compra: o espelho da pagina e igual a lista;
#   [2] cada ordem abre a si mesma: titulo, fornecedor, deposito, datas, situacao, itens e total;
#   [3] pelo clique: lista, painel e "Abrir ordem completa" chegam na ordem clicada;
#   [4] o que a ordem oferece segue a situacao dela; clonar copia a ordem aberta;
#   [5] a ordem criada em Necessidades de Compra abre com os itens dela;
#   [6] ordem nova, endereco sem id e id que nao existe.
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, sys, json
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
OC, OC_D = 'pagina-estoque-ordens-compra.html', 'pagina-estoque-ordens-compra-detalhe.html'

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


def br(iso):
    return iso[8:10] + '/' + iso[5:7] + '/' + iso[0:4] if iso else ''


# O que a pagina da ordem mostra.
RETRATO_OC = """() => {
  const rot = (id) => document.querySelector('#' + id + ' .dropdown-select-label').textContent.trim();
  const visivel = (acao) => { const i = document.querySelector('#menuMaisAcoes [data-acao="' + acao + '"]'); return !!i && i.style.display !== 'none'; };
  return {
    h1: document.getElementById('tituloOC').textContent.trim(), numero: document.getElementById('inputNumero').value,
    fornecedor: rot('inputFornecedor'), deposito: rot('inputDeposito'), doc: document.getElementById('fDocNumero').textContent.trim(),
    data: document.getElementById('inputDataCompra').value, previsto: document.getElementById('inputDataPrevista').value,
    situacao: document.getElementById('badgeSituacao').textContent.trim(),
    itens: ITENS.map(i => [i.nome, i.sku, i.qtd, i.un, i.preco]), linhas: document.getElementById('corpoItens').children.length,
    total: paraNumero(document.getElementById('totGeral').textContent.replace('R$', '')),
    receber: visivel('receber'), parcial: visivel('parcial'), clonar: visivel('clonar'),
    trilha: document.getElementById('breadcrumb').textContent.replace(/\\s+/g, ' ').trim()
  };
}"""

with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:140]))

    def ir(tela, query=''):
        pg.goto(localiza.uri(tela) + query); pg.wait_for_load_state('load'); pg.wait_for_timeout(300)

    ir(OC); pg.evaluate("localStorage.removeItem('deskOrdensGeradas'); localStorage.removeItem('deskParametros')")
    ir(OC)
    ORDENS, ITENS_OC = pg.evaluate('ORDENS'), pg.evaluate('ITENS_OC')
    DEPOSITOS, SIT = pg.evaluate('DEPOSITOS'), pg.evaluate('SITUACAO_LABEL')

    if secao(1, 'Ordens de Compra: o espelho da página é igual à lista'):
        ir(OC_D)
        ok(pg.evaluate('ORDENS_DA_LISTA') == ORDENS and len(ORDENS) == 14, 'ORDENS_DA_LISTA repete as 14 ordens da lista, campo a campo')
        ok(pg.evaluate('ITENS_DA_LISTA') == ITENS_OC and len(ITENS_OC) == 4, 'ITENS_DA_LISTA repete os itens das 4 ordens que a lista tem com itens')
        nomes = pg.evaluate("Object.keys(FORNECEDORES).map(k => FORNECEDORES[k].nome)")
        ok(not [o['fornecedor'] for o in ORDENS if o['fornecedor'] not in nomes], 'todo fornecedor da lista existe na página da ordem: %s' % sorted(set(o['fornecedor'] for o in ORDENS) - set(nomes)))
        fora = []
        for o in ORDENS:
            itens = ITENS_OC.get(str(o['id']))
            if itens and abs(sum(i['qtd'] * i['preco'] for i in itens) + o.get('frete', 0) - o.get('desconto', 0) - o['total']) > 0.005:
                fora.append(o['numero'])
        ok(not fora, 'na lista, itens mais frete menos desconto fecham no total de cada ordem que tem itens: %s' % fora)

    if secao(2, 'Cada ordem abre a si mesma'):
        ruins, vistos = [], {}
        for o in ORDENS:
            ir(OC_D, '?id=%d' % o['id'])
            r = vistos[o['id']] = pg.evaluate(RETRATO_OC)
            itens = ITENS_OC.get(str(o['id']))
            quer = dict(h1='Ordem de Compra nº %d' % o['numero'], numero=str(o['numero']), fornecedor=o['fornecedor'], deposito=DEPOSITOS[str(o['dep'])],
                        data=br(o['data']), previsto=br(o['previsto']), situacao=SIT[o['situacao']],
                        itens=[[i['nome'], i['sku'], i['qtd'], i['un'], i['preco']] for i in itens] if itens else [['Item de exemplo', '', 1, 'UN', o['total']]],
                        receber=o['situacao'] in ('aberto', 'andamento'), parcial=o['situacao'] in ('aberto', 'andamento'), clonar=True)
            for k, v in quer.items():
                if r[k] != v:
                    ruins.append('nº %d, %s: %r, e a lista diz %r' % (o['numero'], k, r[k], v))
            if abs(r['total'] - o['total']) > 0.005 or r['linhas'] != len(r['itens']) or r['doc'] in ('', '—'):
                ruins.append('nº %d: total %s (lista %s), %d linhas, documento %r' % (o['numero'], r['total'], o['total'], r['linhas'], r['doc']))
        ok(not ruins, 'as 14 ordens abrem com o que a lista diz delas (fornecedor, depósito, datas, situação, itens e total): %s' % ruins[:3])
        ok(len(set(v['h1'] for v in vistos.values())) == 14, 'são 14 títulos diferentes, e não a ordem nº 2 quatorze vezes')
        ok(sum(1 for o in ORDENS if str(o['id']) in ITENS_OC) == 4 and sum(1 for o in ORDENS if o['situacao'] in ('atendida', 'cancelada')) >= 4,
           'a conferência passou por ordem com itens e sem itens, e por ordem que espera mercadoria e que não espera')
        ir(OC)
        painel = pg.evaluate("""(ids) => ids.map(id => { abrirPreview(id); return Array.from(document.querySelectorAll('#eventDrawer .mov-item')).map(m => m.querySelector('.mov-qtd').textContent.trim()); })""",
                             [o['id'] for o in ORDENS if str(o['id']) not in ITENS_OC][:2])
        sem = [o for o in ORDENS if str(o['id']) not in ITENS_OC][:2]
        ok(len(painel) == 2 and all(len(x) == 1 for x in painel) and [x[0] for x in painel] == [pg.evaluate("(n) => fmtMoeda(n)", o['total']) for o in sem], 'no painel da lista, o item de exemplo da ordem sem itens leva o total dela: %s' % painel)

    if secao(3, 'Pelo clique: lista, painel e o botão de abrir'):
        for alvo in (ORDENS[0], ORDENS[9]):
            ir(OC)
            pg.evaluate("(id) => abrirPreview(id)", alvo['id']); pg.wait_for_timeout(250)
            pg.evaluate("document.getElementById('btnAbrirDetalhe').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
            r = pg.evaluate(RETRATO_OC)
            ok(pg.url.split('/')[-1] == OC_D + '?id=%d' % alvo['id'] and r['h1'] == 'Ordem de Compra nº %d' % alvo['numero'] and r['fornecedor'] == alvo['fornecedor'],
               'cliquei na ordem nº %d (%s) e a página abriu "%s", de %s' % (alvo['numero'], alvo['fornecedor'], r['h1'], r['fornecedor']))
        ir('pagina-estoque-conferencia.html')
        oc = pg.evaluate('NOTA.oc')
        pg.evaluate("document.querySelector('[data-acao=\"oc\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        ok(oc and oc != 2 and pg.url.split('/')[-1] == OC_D + '?id=%s' % oc and pg.evaluate(RETRATO_OC)['numero'] == str(oc),
           'da Conferência, "ver a ordem de compra" abre a ordem nº %s, que é a da nota' % oc)

    if secao(4, 'O que a ordem oferece segue a situação; clonar copia a ordem aberta'):
        atendida = [o for o in ORDENS if o['situacao'] == 'atendida'][0]
        ir(OC_D, '?id=%d' % atendida['id'])
        antes = pg.evaluate(RETRATO_OC)
        pg.evaluate("SITUACAO = 'aberto'; aplicarSituacao()")
        ok(not antes['receber'] and not antes['parcial'] and pg.evaluate(RETRATO_OC)['receber'], 'ordem atendida não oferece "Receber mercadorias"; voltando para em aberto, oferece de novo')
        ir(OC_D, '?id=4')
        pg.evaluate("document.querySelector('#menuMaisAcoes [data-acao=\"clonar\"]').click()"); pg.wait_for_load_state('load'); pg.wait_for_timeout(400)
        r = pg.evaluate(RETRATO_OC)
        q = pg.url.split('?')[-1]
        ok('clonar=1' in q and 'id=4' in q and r['h1'] == 'Nova ordem de compra' and r['numero'] == '' and r['fornecedor'] == ORDENS[3]['fornecedor']
           and [i[1] for i in r['itens']] == [i['sku'] for i in ITENS_OC['4']] and 'Cópia da nº 4' in r['trilha'] and r['situacao'] == SIT['aberto'],
           'clonar a ordem nº 4 abre uma ordem nova com o fornecedor e os itens da nº 4: %s, %s' % (r['fornecedor'], [i[1] for i in r['itens']]))

    if secao(5, 'A ordem criada em Necessidades de Compra abre com os itens dela'):
        gerada = {'numero': 15, 'fornecedor': 'Luminárias Brasil', 'data': '2026-10-13', 'previsto': '2026-10-20', 'dep': 2, 'total': 1724.00,
                  'itens': [{'nome': 'Luminária LED Ajustável', 'sku': 'LUM-LED-004', 'qtd': 20, 'un': 'UN', 'preco': 86.20}]}
        ir(OC); pg.evaluate("(o) => localStorage.setItem('deskOrdensGeradas', JSON.stringify([o]))", gerada)
        ir(OC)
        ok(pg.evaluate("ORDENS.some(o => o.numero === 15)"), 'a ordem nº 15, gravada como Necessidades de Compra grava, entra na lista')
        ir(OC_D, '?id=15')
        r = pg.evaluate(RETRATO_OC)
        ok(r['h1'] == 'Ordem de Compra nº 15' and r['fornecedor'] == 'Luminárias Brasil' and r['itens'] == [['Luminária LED Ajustável', 'LUM-LED-004', 20, 'UN', 86.2]]
           and abs(r['total'] - 1724.00) < 0.005 and r['situacao'] == SIT['aberto'] and r['previsto'] == '20/10/2026',
           'e a página dela abre a nº 15, da Luminárias Brasil, com o item e o total: %s' % r['itens'])
        pg.evaluate("localStorage.removeItem('deskOrdensGeradas')")

    if secao(6, 'Ordem nova, endereço sem id e id que não existe'):
        ir(OC_D, '?novo=1')
        r = pg.evaluate(RETRATO_OC)
        ok(r['h1'] == 'Nova ordem de compra' and r['numero'] == '' and r['itens'] == [] and r['fornecedor'] == 'Selecione o fornecedor' and r['previsto'] == '',
           'ordem nova continua abrindo em branco')
        ir(OC_D); sem_id = pg.evaluate(RETRATO_OC)
        ir(OC_D, '?id=2'); com_2 = pg.evaluate(RETRATO_OC)
        ir(OC_D, '?id=99999'); fora = pg.evaluate(RETRATO_OC)
        ok(sem_id == com_2 == fora and com_2['h1'] == 'Ordem de Compra nº 2', 'sem id, ou com um que não existe, abre a ordem nº 2, como antes')
        ir(OC_D, '?id=11&editar=1'); pg.wait_for_timeout(250)
        tem = pg.evaluate("typeof camposAlterados === 'function'")
        ok((not tem) or pg.evaluate('camposAlterados()') == 0, 'abrir a ordem nº 11 não deixa alteração pendente no rodapé')

    ok(not erros, 'nenhum erro de JavaScript em toda a suite: %s' % erros[:3])
    nav.close()

print('\n%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print(' - ' + f)
sys.exit(1 if falhas else 0)
