from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g, tempfile as _tempfile
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

ARQ = localiza.uri('pagina-financas-contas-pagar-detalhe.html')
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def aba(pg, nome):
    pg.click('.tab-item[data-tab="%s"]' % nome); pg.wait_for_timeout(200)

def escolher(pg, dd, menu, valor):
    pg.click('#%s .dropdown-select-btn' % dd); pg.wait_for_timeout(200)
    pg.click('#%s .dropdown-select-item[data-value="%s"]' % (menu, valor)); pg.wait_for_timeout(280)


def abrir_mais_acoes(pg):
    """As acoes destrutivas de pagina de registro moram dentro do "Mais acoes"
    desde 28/set/2026. Abre o menu antes de clicar no item — e nao falha quando a
    tela ainda nao tem menu."""
    if pg.evaluate("!!document.getElementById('menuMaisAcoes')"):
        pg.evaluate("document.querySelector('#menuMaisAcoes .dropdown-select-btn').click()")
        pg.wait_for_timeout(150)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(ARQ); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.clear()")
    pg.goto(ARQ); pg.wait_for_timeout(500)
    visivel = lambda cid: pg.eval_on_selector('#' + cid, "e => getComputedStyle(e).display") != 'none'

    print('1. conta nova abre em edicao, sem badge')
    ok(not erros, 'sem erro de JS: %s' % erros[:2])
    ok(not pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'abre editavel')
    ok(pg.eval_on_selector_all('#tituloConta .sit-badge', 'e => e.length') == 0, 'sem badge: ainda nao existe situacao')
    ok(not visivel('campoParcelas') and not visivel('campoRepetirAte'), 'Unica nao pede quantidade nem horizonte')

    print('2. as DUAS familias pedem campos diferentes  [aba: dados]')
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Parcelada')
    ok(visivel('campoParcelas') and visivel('campoBaseValor'), 'Parcelada pede QUANTIDADE e o que o valor significa')
    ok(not visivel('campoRepetirAte'), 'e nao pede horizonte: compra dividida acaba')
    ok(pg.text_content('#labelValor') == 'Valor total (R$)', 'o rotulo do valor virou "Valor total": %s' % pg.text_content('#labelValor'))
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Mensal')
    ok(visivel('campoRepetirAte') and visivel('campoDiaVenc'), 'Mensal pede HORIZONTE e dia do mes')
    ok(not visivel('campoParcelas') and not visivel('campoBaseValor'), 'e nao pede quantidade: despesa recorrente nao tem fim contado')
    ok(pg.text_content('#labelValor') == 'Valor (R$)', 'o rotulo voltou a ser "Valor"')
    ok('até quando' in pg.text_content('#notaOcorrencia'), 'a nota explica que recorrente tem ate quando')
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Semanal')
    ok(visivel('campoDiaSemana') and not visivel('campoDiaVenc'), 'Semanal troca para dia da SEMANA')

    print('2b. campo visivel continua sendo BLOCO — rotulo em cima, nao ao lado')
    est = pg.evaluate("""(function(){
      var out = [];
      ['campoOcorrencia','campoRepetirAte','campoDiaVenc','campoDiaSemana','campoParcelas','campoBaseValor'].forEach(function(id){
        var el = document.getElementById(id);
        if (getComputedStyle(el).display === 'none') return;
        var lab = el.querySelector('label'), ctrl = el.querySelector('input, .dropdown-select-btn');
        out.push({ id: id, display: getComputedStyle(el).display,
                   rotuloEmCima: lab.getBoundingClientRect().bottom <= ctrl.getBoundingClientRect().top + 1 });
      });
      return out;
    })()""")
    ok(all(x['display'] == 'block' for x in est), 'o .form-field continua block: %s' % [x['display'] for x in est])
    ok(all(x['rotuloEmCima'] for x in est), 'e o rotulo fica ACIMA do campo, nao ao lado')

    print('3. o horizonte nasce em 31/12 e o dia vem do 1o vencimento')
    pg.fill('#inputVencimento', '15/03/2026')
    pg.dispatch_event('#inputVencimento', 'change'); pg.wait_for_timeout(300)
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Mensal')
    ok(pg.input_value('#inputRepetirAte') == '31/12/2026', 'repetir ate = fim do ano: %s' % pg.input_value('#inputRepetirAte'))
    ok(pg.get_attribute('#ddDiaVenc', 'data-value') == '15', 'dia do vencimento veio do 1o vencimento: %s' % pg.get_attribute('#ddDiaVenc', 'data-value'))
    ok(pg.eval_on_selector_all('#menuDiaVenc .dropdown-select-item', 'e => e.length') == 31, 'o dia do mes e ESCOLHA entre 31, no mesmo componente do dia da semana')
    ok('mês curto' in pg.text_content('#menuDiaVenc'), 'e a lista avisa o que acontece com 29, 30 e 31')

    print('4. aluguel de marco gera DEZ contas, nao doze')
    pg.fill('#inputValor', '1.200,00'); pg.wait_for_timeout(350)
    plano = pg.evaluate("planoDaRepeticao()")
    ok(len(plano['parcelas']) == 10, 'dez contas — o ano acabou: %d' % len(plano['parcelas']))
    ok(all(abs(x['valor'] - 1200) < 0.005 for x in plano['parcelas']), 'todas com o valor CHEIO: recorrencia repete')
    ok(plano['parcelas'][-1]['venc'] == '2026-12-15', 'a ultima vence em 15/12: %s' % plano['parcelas'][-1]['venc'])
    prev = pg.text_content('#previaRepeticaoTexto')
    ok('10 contas' in prev and '1.200,00' in prev, 'a previa diz o que sera criado: "%s"' % prev[:60])

    print('5. parcelada DIVIDE o total, e o ultimo centavo fica no fim')
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Parcelada')
    pg.fill('#inputParcelas', '3')
    pg.fill('#inputValor', '3.000,00'); pg.wait_for_timeout(350)
    v = pg.evaluate("planoDaRepeticao().parcelas.map(function(x){return x.valor})")
    ok(v == [1000, 1000, 1000], '3.000 em 3x = tres de 1.000: %s' % v)
    d = pg.evaluate("planoDaRepeticao().parcelas.map(function(x){return x.venc})")
    ok(d == ['2026-03-15', '2026-04-15', '2026-05-15'], 'e o dia repete mes a mes: %s' % d)
    pg.fill('#inputValor', '1.000,00'); pg.wait_for_timeout(320)
    v2 = pg.evaluate("planoDaRepeticao().parcelas.map(function(x){return x.valor})")
    ok(v2 == [333.33, 333.33, 333.34], 'arredonda pra BAIXO e a ultima absorve: %s' % v2)
    ok(abs(sum(v2) - 1000) < 0.005, 'a soma bate exata com a nota')

    print('6. "valor por parcela" nao divide')
    escolher(pg, 'ddBaseValor', 'ddBaseValor', 'parcela')
    v3 = pg.evaluate("planoDaRepeticao().parcelas.map(function(x){return x.valor})")
    ok(v3 == [1000, 1000, 1000], 'o mesmo 1.000 virou tres de 1.000: %s' % v3)
    ok('cada parcela' in pg.text_content('#notaOcorrencia'), 'a nota acompanhou a troca')

    print('7. aviso quando a repeticao gera muita conta')
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Semanal')
    pg.wait_for_timeout(300)
    n = pg.evaluate("planoDaRepeticao().parcelas.length")
    ok(n > 30, 'semanal de marco a dezembro passa de 30: %d' % n)
    ok(pg.eval_on_selector_all('#previaRepeticao .previa-alerta', 'e => e.length') == 1, 'a previa avisa antes de criar')

    print('8. salvar cria o grupo todo')
    escolher(pg, 'ddOcorrencia', 'menuOcorrencia', 'Mensal')
    pg.fill('#inputValor', '1.200,00')
    pg.fill('#inputFornecedor', 'Imobili'); pg.wait_for_timeout(350)
    pg.click('#menuFornecedor .auto-item'); pg.wait_for_timeout(200)
    escolher(pg, 'ddCategoria', 'menuCategoria', '7')
    pg.fill('#inputHistorico', 'Aluguel da loja nova')
    pg.evaluate("(function(){var p=JSON.parse(localStorage.getItem('deskParametros')||'{}');p.aoSalvar='ficar';localStorage.setItem('deskParametros',JSON.stringify(p));PARAM.aoSalvar='ficar'})()")
    n0 = pg.evaluate("TITULOS.length")
    pg.click('#btnSalvarConta'); pg.wait_for_timeout(500)
    ok(pg.evaluate("TITULOS.length") == n0 + 10, 'nasceram 10 contas: %d' % (pg.evaluate("TITULOS.length") - n0))
    novas = pg.evaluate("TITULOS.slice(-10)")
    ok(len(set(x['grupo'] for x in novas)) == 1, 'todas no mesmo grupo')
    ok(all(x.get('parcela') is None for x in novas), 'sem contador de parcela gravado')
    comps = [x['comp'] for x in novas]
    ok(comps == sorted(set(comps)) and len(set(comps)) == 10, 'cada conta com a competencia do SEU mes: %s' % comps[:3])

    print('9. conta existente do grupo abre em leitura e diz que se repete')
    pg.goto(ARQ + '?id=105'); pg.wait_for_timeout(600)
    ok(pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'abre em leitura')
    ok('12 contas no grupo' in pg.text_content('#roOcorrencia'), 'a ocorrencia diz o tamanho do grupo: %s' % pg.text_content('#roOcorrencia'))
    sub = pg.text_content('#subtituloConta')
    ok('parcela' not in sub, 'o subtitulo NAO fala de parcela: "%s"' % sub)
    ok('compet' in sub, 'ele fala de competencia, que e o que identifica o mes')
    ok(pg.input_value('#inputRepetirAte') == '15/12/2026', 'o horizonte foi lido do ultimo do grupo: %s' % pg.input_value('#inputRepetirAte'))

    print('10. o reajuste do aluguel pergunta o ESCOPO')
    pg.click('#btnEditar'); pg.wait_for_timeout(250)
    pg.fill('#inputValor', '4.500,00')
    pg.click('#btnSalvarConta'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#modalEscopo', "e => e.classList.contains('open')"), 'o modal de escopo abriu ANTES de salvar')
    txt = pg.text_content('#modalEscopo')
    ok('Só esta conta' in txt and 'Esta e as seguintes' in txt and 'Todas as contas' in txt, 'as tres opcoes estao la')
    ok('não propagam' in pg.text_content('#escopoNota'), 'a nota diz o que NAO propaga (vencimento, emissao, competencia)')
    pagas = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1' && x.pago>0}).length")
    ok(str(pagas) in pg.text_content('#escopoNota'), 'e avisa que as %d pagas ficam de fora' % pagas)

    print('11. "esta e as seguintes" muda o daqui pra frente, e so')
    pg.click('.escopo-row[data-escopo="seguintes"]'); pg.wait_for_timeout(200)
    ok(pg.eval_on_selector('.escopo-row[data-escopo="seguintes"]', "e => e.classList.contains('on')"), 'a opcao marcou')
    ok(not pg.eval_on_selector('.escopo-row[data-escopo="uma"]', "e => e.classList.contains('on')"), 'e desmarcou a outra — exclusivo')
    antes = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).map(function(x){return [x.vencIso, x.valor, x.pago]})")
    pg.click('#btnEscopoContinuar'); pg.wait_for_timeout(500)
    depois = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).map(function(x){return [x.vencIso, x.valor, x.pago]})")
    alvo = pg.evaluate("titDe(105).vencIso")
    mudou = [x for a, x in zip(antes, depois) if a[1] != x[1]]
    ok(all(x[0] >= alvo for x in mudou), 'so mudaram as que vencem de %s em diante' % alvo)
    ok(all(abs(x[1] - 4500) < 0.01 for x in mudou), 'e todas foram para 4.500: %d contas' % len(mudou))
    intactas_pagas = [x for x in depois if x[2] > 0]
    ok(all(abs(x[1] - 4200) < 0.01 for x in intactas_pagas), 'as PAGAS ficaram em 4.200 — mexer nelas faria o saldo mentir')
    vencs = pg.evaluate("TITULOS.filter(function(x){return x.grupo==='REC-1'}).map(function(x){return x.vencIso})")
    ok(len(set(vencs)) == len(vencs), 'nenhum vencimento foi propagado junto — cada conta manteve o seu')

    print('12. cancelar existe, e volta atras')
    pg.goto(ARQ + '?id=6'); pg.wait_for_timeout(500)
    abrir_mais_acoes(pg)
    ok(visivel('linkCancelarConta'), 'o link de cancelar aparece no Mais ações')
    ok(pg.text_content('#rotuloCancelar').strip() == 'Cancelar conta', 'rotulo de ida')
    pg.click('#linkCancelarConta'); pg.wait_for_timeout(400)
    ok(pg.evaluate("titDe(6).cancelado") is True, 'a conta ficou cancelada')
    ok(pg.text_content('#tituloConta .sit-badge').strip() == 'cancelada', 'a badge acompanhou')
    ok(pg.eval_on_selector('#btnDarBaixa', "e => getComputedStyle(e).display") == 'none', 'conta cancelada nao se paga')
    ok(pg.text_content('#rotuloCancelar').strip() == 'Reativar conta', 'o mesmo link agora desfaz')
    abrir_mais_acoes(pg)
    pg.click('#linkCancelarConta'); pg.wait_for_timeout(400)
    ok(pg.evaluate("titDe(6).cancelado") is False, 'reativou')
    ok(pg.text_content('#tituloConta .sit-badge').strip() in ('em aberto', 'atrasada'), 'e voltou para em aberto')

    print('13. cancelar conta paga e barrado, e manda estornar')
    pg.goto(ARQ + '?id=1'); pg.wait_for_timeout(500)
    abrir_mais_acoes(pg)
    pg.click('#linkCancelarConta'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#caixaErro', "e => getComputedStyle(e).display") != 'none', 'o erro aparece no topo')
    ok('estorne' in pg.text_content('#caixaErro').lower(), 'e aponta o estorno')
    ok(pg.evaluate("titDe(1).cancelado") is False, 'a conta nao foi cancelada')

    print('14. a baixa continua escrevendo no Caixa  [aba: dados -> painel]')
    pg.goto(ARQ + '?id=4'); pg.wait_for_timeout(500)
    pg.click('#btnDarBaixa'); pg.wait_for_timeout(400)
    ok(pg.eval_on_selector('#inputDataPgto', "e => getComputedStyle(e).display") != 'none', 'o painel abre vivo em modo leitura')
    pg.click('#linkMaisOpcoes'); pg.wait_for_timeout(200)
    pg.fill('#inputJuros', '12,50'); pg.wait_for_timeout(300)
    pg.click('#btnConfirmarPagamento'); pg.wait_for_timeout(450)
    movs = pg.evaluate("JSON.parse(localStorage.getItem('deskCaixaExtras')||'[]')")
    ok(len(movs) == 2, 'principal + juros foram para o Caixa: %d' % len(movs))
    ok(20 in [m['catId'] for m in movs], 'o juros na categoria propria')

    print('15. exclusao em grupo tambem pergunta o escopo')
    pg.goto(ARQ + '?id=110'); pg.wait_for_timeout(500)
    abrir_mais_acoes(pg)
    pg.click('#linkExcluirConta'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#modalEscopo', "e => e.classList.contains('open')"), 'escopo antes de excluir')
    ok('exclus' in pg.text_content('#escopoTexto'), 'o texto fala de exclusao: "%s"' % pg.text_content('#escopoTexto'))
    pg.keyboard.press('Escape'); pg.wait_for_timeout(250)
    ok(not pg.eval_on_selector('#modalEscopo', "e => e.classList.contains('open')"), 'ESC fecha o escopo')

    print('16. largura e erros')
    doc = pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    ok(doc[0] <= doc[1] + 1, 'pagina nao estoura em 1440: %s' % doc)
    ok(not erros, 'nenhum erro de JS no caminho todo: %s' % erros[:4])
    pg.screenshot(path=_os.path.join(_tempfile.gettempdir(), 'qa-cp-detalhe.png'), full_page=True)  # no temp: a raiz do projeto nao e deposito de artefato
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
