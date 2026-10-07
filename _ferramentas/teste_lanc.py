from playwright.sync_api import sync_playwright
import os, sys
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

BASE = 'file://' + os.path.abspath('pagina-financas-caixa-lancamento.html')
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)


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
    pg.goto(BASE); pg.wait_for_timeout(400)
    pg.evaluate("localStorage.removeItem('deskParametros'); localStorage.removeItem('deskLog')")
    pg.goto(BASE); pg.wait_for_timeout(500)

    print('1. novo lancamento abre em EDICAO')
    ok(not erros, 'sem erro de JS: %s' % erros[:2])
    ok(pg.text_content('#tituloLanc').strip() == 'Novo lançamento', 'titulo de novo')
    ok(pg.eval_on_selector('#rodapeEdicao', "e => getComputedStyle(e).display") != 'none', 'rodape de salvar visivel')
    ok(pg.eval_on_selector('#menuMaisAcoes', "e => getComputedStyle(e).display") == 'none', 'sem Mais ações em lancamento que nao existe')
    ok(pg.eval_on_selector('#roConta', "e => getComputedStyle(e).display") == 'none', 'campo de leitura escondido em edicao')

    print('2. a competencia vem da REGRA DA CATEGORIA')
    def escolher_cat(idcat):
        pg.click('.tab-item[data-tab="dados"]'); pg.wait_for_timeout(120)
        pg.click('#ddCategoria .dropdown-select-btn'); pg.wait_for_timeout(150)
        pg.click('#menuCategoria .dropdown-select-item[data-value="%s"]' % idcat); pg.wait_for_timeout(250)
    mes_atual = pg.evaluate("compDaData(iso(HOJE),0)")
    mes_ant = pg.evaluate("compDaData(iso(HOJE),-1)")
    escolher_cat(1)   # Venda de mercadorias -> mes do vencimento
    pg.click('.tab-item[data-tab="competencia"]'); pg.wait_for_timeout(200)
    ok(pg.text_content('#compValor').strip() == mes_atual[5:] + '/' + mes_atual[:4], 'categoria "mes do vencimento" -> mes da data (%s)' % pg.text_content('#compValor'))
    escolher_cat(8)   # Energia eletrica -> mes anterior
    pg.click('.tab-item[data-tab="competencia"]'); pg.wait_for_timeout(250)
    ok(pg.text_content('#compValor').strip() == mes_ant[5:] + '/' + mes_ant[:4], 'categoria "mes anterior" -> mes anterior (%s)' % pg.text_content('#compValor'))
    ok('Energia' in pg.text_content('#notaCompetencia'), 'a nota diz de qual categoria veio')
    ok('uma data s' in pg.text_content('#notaCompetencia'), 'a nota explica por que vencimento e emissao dao o mesmo mes aqui')

    print('3. sobrepor a competencia a mao desliga a regra')
    pg.click('#btnCompAnterior'); pg.wait_for_timeout(250)
    ok('à mão' in pg.text_content('#notaCompetencia'), 'a nota avisa que foi definida a mao')
    antes = pg.text_content('#compValor')
    escolher_cat(1)
    pg.click('.tab-item[data-tab="competencia"]'); pg.wait_for_timeout(250)
    ok(pg.text_content('#compValor') == antes, 'trocar a categoria nao mexe mais na competencia')

    print('4. Tipo = Saldo lanca a DIFERENCA')
    pg.click('.tab-item[data-tab="dados"]'); pg.wait_for_timeout(150)
    pg.click('#ddTipo .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#ddTipo .dropdown-select-item[data-value="saldo"]'); pg.wait_for_timeout(200)
    ok(pg.text_content('#labelValor').strip().startswith('Saldo informado'), 'o rotulo do campo muda: "%s"' % pg.text_content('#labelValor'))
    saldo = pg.evaluate("saldoAte(1, parseData(document.getElementById('inputData').value))")
    pg.fill('#inputValor', '100,00')
    pg.wait_for_timeout(250)
    nota = pg.text_content('#notaSaldo')
    esperado = 'uma saída' if 100 < saldo else 'uma entrada'
    ok(esperado in nota, 'a nota diz o movimento que vai nascer (%s): "%s"' % (esperado, nota[:110]))
    pg.fill('#inputValor', ('%.2f' % saldo).replace('.', ','))
    pg.wait_for_timeout(250)
    ok('Não há o que lançar' in pg.text_content('#notaSaldo'), 'saldo igual ao atual: avisa que nao ha diferenca')

    print('5. a caixa de erro do topo lista o que reprovou')
    pg.goto(BASE); pg.wait_for_timeout(400)
    pg.click('#btnSalvarLanc'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#caixaErro', "e => getComputedStyle(e).display") != 'none', 'caixa de erro apareceu')
    n = pg.eval_on_selector_all('#listaErros li', 'e => e.length')
    ok(n >= 3, 'lista com os motivos: %d' % n)
    ok(pg.eval_on_selector('#campoCategoria', "e => e.classList.contains('has-error')"), 'o campo Categoria tambem fica marcado')
    ok(pg.evaluate("MOVIMENTOS.length") == 27, 'nada foi gravado')

    print('6. periodo fechado barra pela DATA')
    pg.evaluate("localStorage.setItem('deskParametros', JSON.stringify({fechamentoFinanceiro: iso(HOJE)}))")
    pg.goto(BASE); pg.wait_for_timeout(500)
    pg.click('#ddCategoria .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuCategoria .dropdown-select-item[data-value="1"]'); pg.wait_for_timeout(150)
    pg.fill('#inputValor', '150,00')
    pg.fill('#inputHistorico', 'teste novo')
    nm = pg.evaluate("MOVIMENTOS.length")
    pg.click('#btnSalvarLanc'); pg.wait_for_timeout(350)
    ok(pg.evaluate("MOVIMENTOS.length") == nm, 'nao gravou em data fechada')
    ok(pg.eval_on_selector('#campoData', "e => e.classList.contains('has-error')"), 'o campo Data fica marcado, como no print')
    ok('período financeiro está fechado' in pg.text_content('#erroData'), 'a mensagem do campo diz o motivo: "%s"' % pg.text_content('#erroData'))
    ok('fechado' in pg.text_content('#listaErros'), 'e a caixa do topo repete o motivo')
    # dia seguinte passa
    amanha = pg.evaluate("fmtData(iso(new Date(HOJE.getTime()+86400000)))")
    pg.fill('#inputData', amanha)
    pg.wait_for_timeout(200)
    pg.click('#btnSalvarLanc'); pg.wait_for_timeout(500)
    ok(pg.url.endswith('pagina-financas-caixa.html'), 'no dia seguinte salva e volta para o extrato: %s' % pg.url.split('/')[-1])

    print('7. criar categoria sem sair da tela')
    pg.evaluate("localStorage.removeItem('deskParametros')")
    pg.goto(BASE); pg.wait_for_timeout(450)
    ncat = pg.evaluate("CATS_FIN.length")
    pg.click('#ddCategoria .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuCategoria .dropdown-select-item[data-value="nova"]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#drawerCategoria', "e => getComputedStyle(e).right") == '0px', 'painel da categoria abriu')
    pg.fill('#inputNovaCatDesc', 'Prestação de serviço')
    pg.click('#ddNovaCatComp .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#ddNovaCatComp .dropdown-select-item[data-value="anterior"]'); pg.wait_for_timeout(150)
    pg.click('#btnSalvarNovaCat'); pg.wait_for_timeout(400)
    ok(pg.evaluate("CATS_FIN.length") == ncat + 1, 'categoria criada')
    ok('Presta' in pg.text_content('#ddCategoria .dropdown-select-label'), 'ja fica escolhida no lancamento')
    mes_ant2 = pg.evaluate("compDaData(iso(HOJE),-1)")
    pg.click('.tab-item[data-tab="competencia"]'); pg.wait_for_timeout(200)
    ok(pg.text_content('#compValor').strip() == mes_ant2[5:] + '/' + mes_ant2[:4], 'a regra da categoria NOVA ja vale (%s)' % pg.text_content('#compValor'))
    nlog = pg.evaluate("JSON.parse(localStorage.getItem('deskLog')||'[]').filter(function(l){return l.chave==='categoriasFinanceirasCriar'}).length")
    ok(nlog >= 1, 'criar categoria daqui tambem vai para o Registro de atividades')

    print('8. abrir um lancamento existente cai em LEITURA')
    pg.goto(BASE + '?id=8'); pg.wait_for_timeout(500)
    ok(pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')"), 'modo leitura ligado')
    ok(pg.eval_on_selector('#roHistorico', "e => getComputedStyle(e).display") != 'none', 'valor aparece como texto')
    ok(pg.eval_on_selector('#inputHistorico', "e => getComputedStyle(e).display") == 'none', 'o campo some')
    ok(pg.eval_on_selector('#rodapeEdicao', "e => getComputedStyle(e).display") == 'none', 'sem rodape de salvar')
    ok(pg.eval_on_selector('#menuMaisAcoes', "e => getComputedStyle(e).display") != 'none', 'Mais ações disponivel com o lancamento carregado')
    ok('Aluguel' in pg.text_content('#roHistorico'), 'abriu o lancamento certo: "%s"' % pg.text_content('#roHistorico'))
    pg.click('#btnEditar'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('body', "e => e.classList.contains('modo-leitura')") is False, 'Editar leva para o modo edicao')
    ok(pg.eval_on_selector('#inputHistorico', "e => getComputedStyle(e).display") != 'none', 'o campo volta')

    print('9. calendario do lancamento')
    pg.click('.tab-item[data-tab="dados"]'); pg.wait_for_timeout(150)
    pg.click('#dfLancData .date-btn'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#dfLancData .date-pop', "e => e.classList.contains('open')"), 'calendario abre')
    sel = pg.eval_on_selector_all('#dfLancData .date-dia.sel', 'e => e.length')
    ok(sel == 1, 'o dia do lancamento aparece marcado: %d' % sel)
    pg.click('#dfLancData .date-dia[data-iso]'); pg.wait_for_timeout(250)
    ok(pg.input_value('#inputData') != '', 'clicar no dia preenche o campo: %s' % pg.input_value('#inputData'))
    ok(pg.eval_on_selector_all('.tab-item[data-tab="marcadores"]', 'e => e.length') == 0, 'a aba de marcadores nao existe mais')

    print('10. exclusao pede senha')
    abrir_mais_acoes(pg)
    pg.click('#linkExcluirLanc'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#confirmModal', "e => e.classList.contains('open')"), 'modal abriu')
    ok(pg.eval_on_selector('#campoSenhaModal', "e => e.classList.contains('on')"), 'campo de senha armado')
    pg.click('#btnConfirmModalCancelar'); pg.wait_for_timeout(200)

    print('11. largura e erros')
    doc = pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    ok(doc[0] <= doc[1] + 1, 'pagina nao estoura em 1440: %s' % doc)
    ok(not erros, 'nenhum erro de JS no caminho todo: %s' % erros[:4])
    pg.goto(BASE + '?id=8'); pg.wait_for_timeout(400)
    pg.screenshot(path='qa-lancamento.png')
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
