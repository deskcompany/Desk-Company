from playwright.sync_api import sync_playwright
import os, sys, json
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g, tempfile as _tempfile
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

ARQ = localiza.uri('pagina-financas-caixa.html')
falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width':1440,'height':900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.goto(ARQ); pg.wait_for_timeout(500)
    pg.evaluate("localStorage.removeItem('deskParametros'); localStorage.removeItem('deskLog')")
    pg.reload(); pg.wait_for_timeout(500)

    print('1. carga e extrato')
    ok(not erros, 'sem erro de JS: %s' % erros[:2])
    ok(pg.text_content('#seletorConta .dropdown-select-label').strip() == 'Caixa', 'abre na conta preferencial (Caixa)')
    linhas = pg.eval_on_selector_all('tbody tr[data-id]', 'e => e.length')
    ok(linhas == 10, 'primeira pagina cheia, com 10 lancamentos: %d' % linhas)
    pg.click('#btnPaginaProxima'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector_all('tr.cx-saldo-row', 'e => e.length') == 1, 'a faixa de saldo fecha a tabela, na ultima pagina')
    ultima = pg.evaluate("(function(){var tr=document.querySelectorAll('tbody tr');return tr[tr.length-1].classList.contains('cx-saldo-row')})()")
    ok(ultima, 'e ela e a ULTIMA linha, nao a primeira')
    pg.click('#btnPaginaAnterior'); pg.wait_for_timeout(300)
    datas = pg.eval_on_selector_all('tbody tr[data-id] td.cx-data', 'e => e.map(x => x.textContent.trim())')
    d = [datas[i] for i in range(0, len(datas), 2)]
    conv = lambda s: s.split('/')[2] + s.split('/')[1] + s.split('/')[0]
    ok(all(conv(d[i]) >= conv(d[i+1]) for i in range(len(d)-1)), 'ordem DECRESCENTE por data, como no print: %s' % d[:3])
    ok(pg.eval_on_selector_all('tr.cx-saldo-row', 'e => e.length') == 0, 'com filtro de 30 dias, a faixa de saldo nao abre a tabela')

    print('2. totais fecham')
    def totais():
        return pg.evaluate("""(function(){
          var o = {};
          document.querySelectorAll('#barraTotais .cx-total-item').forEach(function(it){
            var r = it.querySelector('.cx-total-rotulo').textContent.trim();
            var v = it.querySelector('.cx-total-valor').textContent.trim();
            o[r] = v;
          });
          return o;
        })()""")
    pg.click('#filtroPeriodo .dropdown-select-btn'); pg.click('#filtroPeriodo .dropdown-select-item[data-value="todos"]')
    pg.wait_for_timeout(300)
    ok(pg.eval_on_selector_all('tr.cx-saldo-row', 'e => e.length') == 0, 'sem filtro de periodo, nenhuma faixa de saldo — como no print sem filtro')
    t = totais()
    num = lambda s: float(s.replace('R$ ','').replace('−','-').replace('.','').replace(',','.'))
    fecha = abs(num(t['saldo inicial']) + num(t['entradas']) - num(t['saídas']) - num(t['saldo final'])) < 0.01
    ok(fecha, 'saldo inicial + entradas - saidas = saldo final: %s' % json.dumps(t, ensure_ascii=False))
    saldo_pill = num(pg.text_content('#saldoAtual'))
    ok(abs(saldo_pill - num(t['saldo final'])) < 0.01, 'sem filtro, saldo final == saldo atual da conta (%.2f x %.2f)' % (saldo_pill, num(t['saldo final'])))

    print('3. troca de conta')
    pg.click('#seletorConta .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuConta .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(350)
    ok('Inter' in pg.text_content('#seletorConta .dropdown-select-label'), 'seletor mostra a conta nova')
    n2 = pg.eval_on_selector_all('tbody tr[data-id]', 'e => e.length')
    ok(n2 == 9, 'extrato do Inter tem 9 lancamentos: %d' % n2)
    t2 = totais()
    ok(abs(num(t2['saldo inicial']) + num(t2['entradas']) - num(t2['saídas']) - num(t2['saldo final'])) < 0.01, 'totais fecham na outra conta tambem')

    print('4. conta fora do fluxo avisa')
    pg.click('#seletorConta .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuConta .dropdown-select-item[data-value="4"]'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#saldoNota', "e => getComputedStyle(e).display") != 'none', 'Cofre da loja avisa que esta fora do fluxo de caixa')
    ok('fora do fluxo' in pg.text_content('#saldoNota'), 'texto do aviso: "%s"' % pg.text_content('#saldoNota')[:60])

    print('5. selecao e totalizador de selecionados')
    pg.click('#seletorConta .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuConta .dropdown-select-item[data-value="1"]'); pg.wait_for_timeout(300)
    pg.evaluate("document.querySelectorAll('[data-check=\"mov\"]').forEach(function(c,i){ if(i<2) c.click(); })")
    pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#barraSelecao', "e => e.classList.contains('show')"), 'barra de selecao apareceu')
    t3 = totais()
    ok('2 selecionados' in json.dumps(t3, ensure_ascii=False), 'rodape ganhou o bloco de selecionados: %s' % json.dumps(t3, ensure_ascii=False)[:120])

    print('6. alterar categoria em massa (sem senha, mas com registro)')
    pg.click('#ddCategoriaMassa .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#menuCategoriaMassa .dropdown-select-item[data-value="18"]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#confirmModal', "e => e.classList.contains('open')") is False, 'editar desligado: aplica direto')
    nlog = pg.evaluate("JSON.parse(localStorage.getItem('deskLog')||'[]').filter(function(l){return l.chave==='caixaEditar'}).length")
    ok(nlog >= 1, 'mesmo sem senha, foi para o Registro de atividades')
    ok(pg.text_content('#ddCategoriaMassa .dropdown-select-label').strip() == 'Alterar categoria', 'rotulo do menu voltou ao neutro')

    print('7. alterar conta financeira move o saldo')
    antes = pg.evaluate("saldoAte(1,null)")
    pg.evaluate("document.querySelectorAll('[data-check=\"mov\"]').forEach(function(c,i){ if(i<1) c.click(); })")
    pg.wait_for_timeout(200)
    pg.click('#linkAlterarContaMassa'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#drawerConta', "e => getComputedStyle(e).right") == '0px', 'painel de conta abriu')
    ok(pg.text_content('#contaAtualRo').strip() == 'Caixa', 'conta atual em somente-leitura')
    pg.click('#ddNovaConta .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuNovaConta .dropdown-select-item[data-value="6"]'); pg.wait_for_timeout(150)
    pg.click('#btnSalvarConta'); pg.wait_for_timeout(400)
    depois = pg.evaluate("saldoAte(1,null)")
    ok(abs(depois - antes) > 0.001, 'saldo da conta de origem mudou (%.2f -> %.2f)' % (antes, depois))
    nlog2 = pg.evaluate("JSON.parse(localStorage.getItem('deskLog')||'[]').filter(function(l){return l.chave==='caixaAlterarConta'}).length")
    ok(nlog2 >= 1, 'alterar conta ficou registrado')

    print('8. transferencia cria DOIS lancamentos ligados')
    nm = pg.evaluate("MOVIMENTOS.length")
    pg.click('#btnTransferir'); pg.wait_for_timeout(300)
    pg.fill('#inputTransfValor', '250,00')
    pg.click('#ddTransfDestino .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuTransfDestino .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(150)
    pg.click('#btnSalvarTransferencia'); pg.wait_for_timeout(400)
    nm2 = pg.evaluate("MOVIMENTOS.length")
    ok(nm2 == nm + 2, 'dois movimentos criados (%d -> %d)' % (nm, nm2))
    par = pg.evaluate("(function(){var a=MOVIMENTOS.slice(-2);return a[0].parId===a[1].id && a[1].parId===a[0].id && a[0].tipo!==a[1].tipo;})()")
    ok(par, 'os dois estao ligados e sao de tipos opostos')
    ok('Transfer' in pg.content(), 'a origem "Transferencia" aparece na tabela')

    print('9. fechamento financeiro')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#menuMaisAcoes .dropdown-select-item[data-value="fechamento"]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#drawerFechamento', "e => getComputedStyle(e).right") == '0px', 'painel de fechamento abriu')
    hoje = pg.evaluate("fmtData(iso(HOJE))")
    pg.fill('#inputDataFechamento', hoje)
    pg.click('#btnFecharPeriodo'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#confirmModal', "e => e.classList.contains('open')"), 'fechar periodo pede confirmacao')
    ok(pg.eval_on_selector('#campoSenhaModal', "e => e.classList.contains('on')"), 'fechar periodo exige SENHA por padrao')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#confirmModal', "e => e.classList.contains('open')"), 'sem senha nao fecha')
    pg.fill('#inputSenhaModal', 'senha123')
    pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(450)
    ok(pg.evaluate("lerFechamento()") != '', 'fechamento gravado: %s' % pg.evaluate("lerFechamento()"))
    ok('financeiro fechado' in pg.text_content('#barraTotais'), 'rodape mostra o estado do fechamento')

    print('10. a trava do periodo fechado pega')
    pg.evaluate("document.querySelectorAll('[data-check=\"mov\"]').forEach(function(c,i){ if(i<2) c.click(); })")
    pg.wait_for_timeout(250)
    info = pg.text_content('#selecaoInfo')
    ok('período fechado' in info, 'a barra avisa quantos estao travados: "%s"' % info)
    rot = pg.text_content('#linkExcluirSelecionados')
    ok(rot.startswith('Nenhum pode'), 'link de excluir diz que nao da: "%s"' % rot)
    nm3 = pg.evaluate("MOVIMENTOS.length")
    pg.click('#linkExcluirSelecionados'); pg.wait_for_timeout(300)
    ok(pg.evaluate("MOVIMENTOS.length") == nm3, 'clicar no link travado nao exclui nada')
    # transferencia em data fechada tambem barra
    pg.click('#linkLimparSelecao'); pg.wait_for_timeout(200)
    pg.click('#btnTransferir'); pg.wait_for_timeout(300)
    pg.fill('#inputTransfValor', '10,00')
    pg.click('#ddTransfDestino .dropdown-select-btn'); pg.wait_for_timeout(150)
    pg.click('#menuTransfDestino .dropdown-select-item[data-value="2"]'); pg.wait_for_timeout(150)
    nm4 = pg.evaluate("MOVIMENTOS.length")
    pg.click('#btnSalvarTransferencia'); pg.wait_for_timeout(350)
    ok(pg.evaluate("MOVIMENTOS.length") == nm4, 'transferencia em data fechada nao passa')
    ok(pg.eval_on_selector('#erroTransfData', "e => e.classList.contains('show')"), 'o erro aparece no campo Data, nao num alerta solto')
    pg.click('#btnCancelarTransferencia'); pg.wait_for_timeout(200)

    print('10b. calendario nos campos de data')
    pg.click('#btnTransferir'); pg.wait_for_timeout(300)
    pg.click('#dfTransfData .date-btn'); pg.wait_for_timeout(300)
    ok(pg.eval_on_selector('#dfTransfData .date-pop', "e => e.classList.contains('open')"), 'o calendario abre no icone')
    dias = pg.eval_on_selector_all('#dfTransfData .date-dia:not(.vazio)', 'e => e.length')
    ok(dias >= 28 and dias <= 31, 'o mes tem %d dias desenhados' % dias)
    riscados = pg.eval_on_selector_all('#dfTransfData .date-dia.off', 'e => e.length')
    ok(riscados > 0, 'com periodo fechado, os dias travados aparecem riscados: %d' % riscados)
    sem_clique = pg.eval_on_selector_all('#dfTransfData .date-dia.off[data-iso]', 'e => e.length')
    ok(sem_clique == 0, 'dia riscado nao e clicavel')
    motivo = pg.eval_on_selector('#dfTransfData .date-dia.off', "e => e.getAttribute('title')")
    ok('fechado' in (motivo or ''), 'o dia riscado diz o motivo: "%s"' % motivo)
    ok('Fechado at' in pg.text_content('#dfTransfData .date-rodape'), 'o rodape do calendario repete a trava')
    # O periodo foi fechado HOJE, entao o mes corrente pode nao ter NENHUM dia
    # livre — e no ultimo dia do mes ele nunca tem. Quem transfere avanca um mes,
    # que e o que o calendario oferece. Sem isto o teste passa 29 dias por mes e
    # reprova no trigesimo: mesma familia do "o mock envelhece" (design system
    # 13) — o teste nao muda, o calendario muda.
    livre = pg.eval_on_selector_all('#dfTransfData .date-dia[data-iso]', 'e => e.length')
    if livre == 0:
        pg.click('#dfTransfData .date-nav[data-passo="1"]'); pg.wait_for_timeout(250)
        livre = pg.eval_on_selector_all('#dfTransfData .date-dia[data-iso]', 'e => e.length')
        ok(livre > 0, 'mes corrente todo fechado; o mes seguinte tem %d dias livres' % livre)
    else:
        ok(livre > 0, 'sobram dias clicaveis: %d' % livre)
    pg.click('#dfTransfData .date-dia[data-iso]'); pg.wait_for_timeout(250)
    ok(pg.eval_on_selector('#dfTransfData .date-pop', "e => e.classList.contains('open')") is False, 'escolher o dia fecha o calendario')
    ok(pg.input_value('#inputTransfData') != '', 'o campo recebeu a data: %s' % pg.input_value('#inputTransfData'))
    pg.click('#btnCancelarTransferencia'); pg.wait_for_timeout(200)
    # no fechamento a regra e o TETO
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#menuMaisAcoes .dropdown-select-item[data-value="fechamento"]'); pg.wait_for_timeout(300)
    pg.click('#dfFechamento .date-btn'); pg.wait_for_timeout(300)
    futuros = pg.evaluate("(function(){var h=iso(HOJE);var n=0;document.querySelectorAll('#dfFechamento .date-dia[data-iso]').forEach(function(d){if(d.getAttribute('data-iso')>h)n++});return n})()")
    ok(futuros == 0, 'no fechamento, dia futuro nao e clicavel: %d' % futuros)
    # o calendario aberto cobre o rodape do painel, como qualquer date picker:
    # ESC fecha. O teste faz o que o usuario faz, em vez de clicar por cima.
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    ok(pg.eval_on_selector('#dfFechamento .date-pop', "e => e.classList.contains('open')") is False, 'ESC fecha o calendario')
    pg.click('#btnCancelarFechamento'); pg.wait_for_timeout(200)

    print('11. bloqueadas abre e explica')
    pg.click('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(200)
    pg.click('#menuMaisAcoes .dropdown-select-item[data-value="bloqueadas"]'); pg.wait_for_timeout(350)
    ok(pg.eval_on_selector('#drawerBloqueadas', "e => getComputedStyle(e).right") == '0px', 'painel de bloqueadas abriu')
    ok('Nenhuma movimenta' in pg.text_content('#listaBloqueadas'), 'abre vazio de verdade, com a explicacao')
    pg.click('#fecharBloqueadas'); pg.wait_for_timeout(250)

    print('12. largura')
    ov = pg.eval_on_selector('.estoque-table-wrap', 'e => [e.scrollWidth, e.clientWidth]')
    ok(ov[0] <= ov[1], 'tabela cabe sem rolagem horizontal: %d x %d' % (ov[0], ov[1]))
    doc = pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    ok(doc[0] <= doc[1] + 1, 'pagina nao estoura em 1440: %s' % doc)

    print('13. erros acumulados')
    ok(not erros, 'nenhum erro de JS no caminho todo: %s' % erros[:4])
    pg.evaluate("localStorage.removeItem('deskParametros')")
    pg.reload(); pg.wait_for_timeout(500)
    pg.screenshot(path=_os.path.join(_tempfile.gettempdir(), 'qa-caixa.png'))  # no temp: a raiz do projeto nao e deposito de artefato
    b.close()

print(); print('FALHAS: %d' % len(falhas))
for f in falhas: print(' - ' + f)
sys.exit(1 if falhas else 0)
