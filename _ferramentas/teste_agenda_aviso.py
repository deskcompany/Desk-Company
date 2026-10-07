# A recorrencia que termina aparece na Agenda. Caminho do usuario: abre Contas a
# Pagar (que publica o aviso), vai para a Agenda e clica no item.
from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------
CP = 'file://' + os.path.abspath('pagina-financas-contas-pagar.html')
AG = 'file://' + os.path.abspath('pagina-inicio-agenda.html')
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(CP); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.clear()")

    print('1. a Agenda sozinha nao inventa aviso nenhum')
    pg.goto(AG); pg.wait_for_timeout(600)
    ok(pg.eval_on_selector_all('.agenda-item-aviso', 'e => e.length') == 0, 'sem aviso antes de Contas a Pagar existir na sessao')

    print('2. Contas a pagar publica a renovacao')
    pg.goto(CP); pg.wait_for_timeout(600)
    avisos = pg.evaluate("JSON.parse(localStorage.getItem('deskAvisos')||'{}')")
    ok(len(avisos) == 1, 'um aviso publicado (o aluguel): %d' % len(avisos))
    a = list(avisos.values())[0]
    ultima = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).map(function(x){return x.vencIso}).sort().pop()")
    ok(a['data'] == ultima, 'na data da ULTIMA conta do grupo: %s' % a['data'])
    ok('Renovar' in a['titulo'] and 'aluguel' in a['titulo'].lower(), 'o titulo diz o que fazer: "%s"' % a['titulo'])
    ok('Contas a pagar' in a['meta'], 'e de onde veio: "%s"' % a['meta'])
    ok('contas-pagar-detalhe' in a['href'], 'com destino na conta')

    print('3. recarregar nao duplica')
    pg.goto(CP); pg.wait_for_timeout(600)
    ok(len(pg.evaluate("JSON.parse(localStorage.getItem('deskAvisos')||'{}')")) == 1, 'continua um: o deposito e mapa, nao fila')

    print('4. a Agenda mostra o aviso no dia certo, e ele LEVA para a conta')
    pg.goto(AG); pg.wait_for_timeout(600)
    # O usuario anda de mes pelas setas do calendario e clica no dia.
    mes = int(ultima.split('-')[1]); dia = int(ultima.split('-')[2])
    atual = pg.evaluate("calMes + 1")
    for _ in range(14):
        if atual == mes: break
        pg.click('#calNext' if atual < mes else '#calPrev'); pg.wait_for_timeout(250)
        atual = pg.evaluate("calMes + 1")
    ok(atual == mes, 'navegou ate o mes da ultima conta (%02d): %02d' % (mes, atual))
    ok(pg.evaluate("Object.keys(getEventosFiltrados()).indexOf('%s') !== -1" % ultima), 'o dia %d tem evento' % dia)
    marcado = pg.eval_on_selector_all('#calGrid .calendar-day', """e => e.filter(c => !c.classList.contains('outro-mes')
        && c.textContent.trim().startsWith('%d')).length""" % dia)
    pg.evaluate("aoClicarDia('%s')" % ultima)
    pg.wait_for_timeout(450)
    n = pg.eval_on_selector_all('.agenda-item-aviso', 'e => e.length')
    ok(n == 1, 'o aviso aparece marcado como vindo de fora: %d' % n)
    ok('Renovar' in pg.text_content('.agenda-item-aviso'), 'com o texto da renovacao')
    pg.click('.agenda-item-aviso'); pg.wait_for_timeout(900)
    ok('contas-pagar-detalhe' in pg.url, 'clicar levou para a conta, nao abriu formulario: %s' % pg.url.split("/")[-1])
    print('5. a conta abre pronta para renovar, e salvar cria o ano seguinte')
    ok(not pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'abre em EDICAO: quem clicou em renovar veio para mexer')
    proximo = str(int(ultima[:4]) + 1) + '-12-31'
    ok(pg.input_value('#inputRepetirAte') == '31/12/' + proximo[:4], 'o horizonte ja aponta para o fim do ano seguinte: %s' % pg.input_value('#inputRepetirAte'))
    ok(pg.eval_on_selector('#avisoBaixa', "e => e.classList.contains('show')"), 'e a faixa do topo explica o que salvar vai fazer')
    ok('mesmo grupo' in pg.text_content('#avisoBaixa'), 'dizendo que continua no mesmo grupo')
    faltam = pg.evaluate("contasQueFaltam({ocorrencia:'Mensal', catId: titDe(111).catId}).length")
    ok(faltam == 12, 'doze contas a criar — o ano seguinte inteiro: %d' % faltam)
    pg.evaluate("(function(){var p=JSON.parse(localStorage.getItem('deskParametros')||'{}');p.aoSalvar='ficar';localStorage.setItem('deskParametros',JSON.stringify(p));PARAM.aoSalvar='ficar'})()")
    n0 = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).length")
    pg.click('#btnSalvarConta'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#modalEscopo', "e => e.classList.contains('open')"), 'ainda pergunta o escopo da alteracao')
    pg.click('#btnEscopoContinuar'); pg.wait_for_timeout(500)
    n1 = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).length")
    ok(n1 == n0 + 12, 'nasceram as 12 do ano seguinte, no MESMO grupo: %d' % (n1 - n0))
    novas = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1' && x.vencIso > '%s'}).map(function(x){return x.vencIso})" % ultima)
    ok(len(novas) == 12 and novas[0] > ultima, 'continuam de onde parou: %s ...' % novas[:2])
    ok(all(v[5:7] != '' for v in novas) and len(set(v[5:7] for v in novas)) == 12, 'uma por mes, sem repetir mes')

    print('6. encurtar o horizonte NAO apaga nada')
    pg.fill('#inputRepetirAte', '31/12/%s' % ultima[:4]); pg.wait_for_timeout(250)
    ok(pg.evaluate("contasQueFaltam({ocorrencia:'Mensal', catId: titDe(111).catId}).length") == 0, 'nada a criar')
    n2 = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).length")
    pg.click('#btnSalvarConta'); pg.wait_for_timeout(400)
    if pg.eval_on_selector('#modalEscopo', "e => e.classList.contains('open')"):
        pg.click('#btnEscopoContinuar'); pg.wait_for_timeout(500)
    ok(pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).length") == n2, 'e nenhuma conta foi apagada por causa de uma data')

    ok(not erros, 'nenhum erro de JS no caminho todo: %s' % erros[:3])
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
