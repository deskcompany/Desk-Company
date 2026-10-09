# -*- coding: utf-8 -*-
# Configurações → Transportadoras (ate 08/out/2026 era Operacional → Transportadoras; o modulo
# Operacional saiu do menu e os cadastros dele abrem pelo hub). Nasceu em 06/out/2026 junto com a Expedição,
# porque sem ele a forma de envio era texto solto no mock — e romaneio que
# agrupa por texto solto não agrupa coisa nenhuma.
#
# O que esta suíte protege são as decisões, não o desenho:
#
#   o tipo DECIDE o formulario: retirada no balcao nao tem coleta nem limite
#   retirada no balcao NAO entra em romaneio, e a tela diz isso em palavras
#   MDF-e so aparece em frota propria — nos outros tipos o documento e do prestador
#   a regra do MDF-e e PARAMETRO POR UF, nunca `if` dentro da tela
#   a frase do MDF-e MUDA quando a UF muda (senao o parametro e enfeite)
#   nome duplicado e barrado: o romaneio agrupa por transportadora
#   dia de coleta sai na ordem da SEMANA, nao na ordem em que foi marcado
#   peso maximo zero DESLIGA o aviso, e a lista diz "sem limite de peso"
#   a trava nasce com a tela: criar, editar e excluir ja estao no catalogo
#   e o catalogo existe nas telas que o LEEM, nao so na que o usa
#   o item de menu mora em Operacional, que e onde o proprio menu ja o previa
from playwright.sync_api import sync_playwright
import os, glob
import pathlib as _pathlib
import localiza
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PASTA)
_ch = glob.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + glob.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
URL = _pathlib.Path(PASTA).as_uri() + '/'   # forma do navegador: barras e %20
TELA = 'pagina-configuracoes-transportadoras.html'

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

def nova(pw, alvo, erros):
    pg = pw.chromium.launch(executable_path=CHROME).new_page(viewport={'width': 1440, 'height': 950})
    pg.on('pageerror', lambda e: erros.append(str(e)))
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' and not ruido(m.text) else None)
    pg.goto(localiza.uri(alvo))
    pg.wait_for_timeout(500)
    return pg

# Modal e folha fixa no rodape: numa pagina rolada o clique direto esbarra na
# conta de coordenadas do proprio playwright, nao na tela. Sobe antes de clicar.
def confirmar(pg):
    pg.evaluate('() => window.scrollTo(0, 0)')
    pg.click('#btnConfirmModalConfirmar')
    pg.wait_for_timeout(300)

# Os dias de coleta moram DENTRO do menu do dropdown, que nasce fechado: clicar
# direto no quadradinho e clicar num elemento invisivel. Abre, marca e recolhe.
def marcar_dias(pg, *dias):
    pg.click('#dropdownDiasColeta .dropdown-select-btn')
    pg.wait_for_timeout(200)
    for d in dias:
        pg.click('[data-dia="' + d + '"]')
        pg.wait_for_timeout(120)
    pg.click('#dropdownDiasColeta .dropdown-select-btn')
    pg.wait_for_timeout(200)

def escolher(pg, raiz, valor):
    pg.click('#' + raiz + ' .dropdown-select-btn')
    pg.wait_for_timeout(200)
    pg.click('#' + raiz + ' .dropdown-select-item[data-value="' + valor + '"]')
    pg.wait_for_timeout(250)


with sync_playwright() as pw:
    erros = []

    # ---------------------------------------------------------------- 1
    print('\n1. A LISTA ABRE E DIZ O QUE A EXPEDICAO PRECISA SABER')
    pg = nova(pw, TELA, erros)
    linhas = pg.locator('.transp-card')
    ok(linhas.count() == 10, 'dez transportadoras no mock: %d' % linhas.count())
    ok(pg.locator('.tipo-badge').count() == 10, 'toda linha carrega o tipo como etiqueta')
    tipos = set(pg.locator('.tipo-badge').all_inner_texts())
    for esperado in ['CORREIOS', 'TRANSPORTADORA', 'FROTA PRÓPRIA', 'RETIRADA NO BALCÃO']:
        ok(esperado in tipos, 'o mock cobre o tipo %s' % esperado)
    ok('configura' in pg.locator('#breadcrumb').inner_text().lower(),
       'o caminho diz Configuracoes, para onde o cadastro foi em 08/out')
    ok(pg.locator('.nav-item[data-id="operacional"]').count() == 0,
       'e o modulo Operacional nao existe mais no menu lateral')

    # ---------------------------------------------------------------- 2
    print('\n2. RETIRADA NO BALCAO NAO ENTRA EM ROMANEIO — E A LISTA DIZ ISSO')
    retirada = pg.locator('.transp-card', has_text='Retirada no balcão').first
    ok('não entra em romaneio' in retirada.inner_text(),
       'a linha da retirada avisa que ela fica fora da Expedicao')
    ok('kg/volume' not in retirada.inner_text(),
       'retirada nao mostra limite de peso: nao ha carga')

    # ---------------------------------------------------------------- 3
    print('\n3. O DIA DE COLETA SAI NA ORDEM DA SEMANA')
    # "sex·seg" em vez de "seg·sex" faz o leitor reler a linha. A ordem vem da
    # lista DIAS, nao da ordem em que a pessoa marcou os quadradinhos.
    jaguar = pg.locator('.transp-card', has_text='Jaguar Cargas').first.inner_text()
    ok('seg·qua·sex' in jaguar, 'Jaguar coleta seg·qua·sex, nessa ordem: %s' % jaguar.replace('\n', ' | '))
    pac = pg.locator('.transp-card', has_text='Correios · PAC').first.inner_text()
    ok('de segunda a sexta' in pac, 'cinco dias uteis viram "de segunda a sexta", nao cinco siglas')

    # ---------------------------------------------------------------- 4
    print('\n4. O TIPO DECIDE O FORMULARIO')
    pg.click('#btnNovaTransp')
    pg.wait_for_timeout(350)
    ok(pg.is_visible('#blocoColeta'), 'transportadora (padrao) pede coleta e prazo')
    ok(not pg.is_visible('#blocoMdfe'), 'transportadora nao fala de MDF-e: o documento e do prestador')
    ok(not pg.is_visible('#notaRetirada'), 'a nota da retirada fica escondida nos outros tipos')
    ok(pg.is_visible('#campoDoc'), 'transportadora pede CNPJ')

    escolher(pg, 'inputTipo', 'correios')
    ok(not pg.is_visible('#campoDoc'), 'Correios nao pede CNPJ de terceiro')
    ok(not pg.is_visible('#blocoMdfe'), 'Correios nao fala de MDF-e')
    ok(pg.is_visible('#blocoColeta'), 'Correios ainda tem coleta, prazo e limite')

    escolher(pg, 'inputTipo', 'retirada')
    ok(not pg.is_visible('#blocoColeta'), 'retirada esconde coleta e limites em vez de pedi-los em cinza')
    ok(not pg.is_visible('#blocoMdfe'), 'retirada nao fala de MDF-e')
    ok(pg.is_visible('#notaRetirada'), 'retirada explica por escrito por que ela some da Expedicao')
    ok('não entra em romaneio' in pg.locator('#notaRetirada').inner_text().lower() or
       'Não entra em romaneio' in pg.locator('#notaRetirada').inner_text(),
       'e a explicacao e justamente que ela nao entra em romaneio')

    # ---------------------------------------------------------------- 5
    print('\n5. MDF-e: SO NA FROTA PROPRIA, E A REGRA E PARAMETRO POR UF')
    escolher(pg, 'inputTipo', 'frota')
    ok(pg.is_visible('#blocoMdfe'), 'frota propria e o unico tipo em que o documento e NOSSO')
    ok(not pg.is_visible('#campoDoc'), 'frota propria nao pede CNPJ: o veiculo e da empresa')
    sp = pg.locator('#textoMdfe').inner_text()
    escolher(pg, 'inputUf', 'RS')
    rs = pg.locator('#textoMdfe').inner_text()
    escolher(pg, 'inputUf', 'BA')
    ba = pg.locator('#textoMdfe').inner_text()
    ok(sp != rs, 'trocar a UF MUDA a frase — senao o parametro seria enfeite')
    ok('mais de uma NF-e' in sp, 'SP: interestadual com mais de uma nota')
    ok('intermunicipal' in rs, 'RS: tambem no intermunicipal, ate com uma nota so')
    ok('interestadual' in ba and 'intermunicipal' not in ba,
       'UF fora do mapa cai no padrao conservador, sem inventar regra: %s' % ba[:70])
    for frase in [sp, rs, ba]:
        ok('mesmo município' in frase, 'toda frase lembra que intramunicipal nao exige')
        ok('módulo fiscal' in frase, 'e que quem emite e o modulo fiscal, nao esta tela')

    # A regra nao pode estar escrita dentro de um `if`: ela e PARAMETRO.
    ok(pg.evaluate("() => typeof PARAM.mdfeRegraUF === 'object' && !!PARAM.mdfeRegraPadrao"),
       'a regra do MDF-e vive no PARAM, com mapa por UF e padrao')
    ok(pg.evaluate("() => regraMdfe('SP') !== regraMdfe('RS')"),
       'o mapa distingue SP de RS de verdade')
    ok(pg.evaluate("() => regraMdfe('AC') === PARAM.mdfeRegraPadrao"),
       'quem nao esta no mapa herda o padrao')

    # ---------------------------------------------------------------- 6
    print('\n6. O QUE O FORMULARIO BARRA')
    pg.click('#btnCancelarTransp'); pg.wait_for_timeout(250)
    pg.click('#btnNovaTransp'); pg.wait_for_timeout(300)
    pg.click('#btnSalvarTransp'); pg.wait_for_timeout(250)
    ok(pg.locator('#erroNomeTransp').is_visible(), 'salvar sem nome acusa o nome')
    ok(pg.locator('#erroDias').is_visible(), 'salvar sem dia de coleta acusa o dia')
    ok(pg.evaluate('() => TRANSPORTADORAS.length') == 10, 'formulario invalido nao grava nada')

    # Nome repetido: o romaneio agrupa POR transportadora. Dois cadastros com o
    # mesmo nome viram duas pilhas na doca que o motorista le como uma so.
    pg.fill('#inputNomeTransp', 'Jaguar Cargas')
    marcar_dias(pg, 'ter')
    pg.click('#btnSalvarTransp'); pg.wait_for_timeout(250)
    ok('Já existe' in pg.locator('#erroNomeTransp').inner_text(), 'nome repetido e barrado')

    pg.fill('#inputNomeTransp', 'Transportadora Nova')
    pg.fill('#inputCorte', '25:00')
    pg.click('#btnSalvarTransp'); pg.wait_for_timeout(250)
    ok(pg.locator('#erroCorte').is_visible(), 'hora impossivel (25:00) e recusada')
    pg.fill('#inputCorte', '14:30')
    pg.fill('#inputPrazo', '3,5')
    pg.click('#btnSalvarTransp'); pg.wait_for_timeout(250)
    ok(pg.locator('#erroPrazo').is_visible(), 'prazo quebrado em dias uteis nao existe: 3,5 e recusado')
    ok(pg.evaluate('() => TRANSPORTADORAS.length') == 10, 'nada entrou enquanto o formulario estava errado')

    # ---------------------------------------------------------------- 7
    print('\n7. SALVAR GRAVA, E ZERO DESLIGA O LIMITE DE PESO')
    # Criar nao pede senha por padrao, entao `confirmarAcao` executa DIRETO: sem
    # modal, sem atrito. Isso e regra do catalogo, nao descuido da tela — a
    # secao 7B prova que ligar o interruptor devolve a confirmacao.
    pg.fill('#inputPrazo', '4')
    pg.fill('#inputPesoMax', '0')
    pg.click('#btnSalvarTransp'); pg.wait_for_timeout(350)
    ok(not pg.locator('#eventDrawer').evaluate("el => el.classList.contains('open')"),
       'formulario valido grava e fecha o painel')
    ok(pg.evaluate('() => TRANSPORTADORAS.length') == 11, 'a nova transportadora entrou no cadastro')
    # A listagem abre com 10 por pagina (Interface do usuario), entao a decima
    # primeira cai na pagina 2: procura por nome em vez de supor que ela aparece.
    pg.fill('#campoBusca', 'Transportadora Nova'); pg.wait_for_timeout(300)
    ok(pg.locator('.transp-card').count() == 1, 'e a busca acha ela')
    nova_linha = pg.locator('.transp-card', has_text='Transportadora Nova').first.inner_text()
    ok('sem limite de peso' in nova_linha,
       'peso maximo zero DESLIGA o aviso, e a lista diz isso em palavras: %s' % nova_linha.replace('\n', ' | '))
    ok('ter' in nova_linha and '14:30' in nova_linha, 'a linha mostra o dia e o corte salvos')
    pg.fill('#campoBusca', ''); pg.wait_for_timeout(250)

    # ---------------------------------------------------------------- 7B
    print('\n7B. LIGAR A TRAVA EM CONFIGURACOES DEVOLVE A CONFIRMACAO')
    # A celula do catalogo nao pode ser enfeite: ligada, a criacao passa a pedir
    # senha e a folha tem de dizer o nome do que vai ser criado.
    pg2 = nova(pw, TELA, erros)
    pg2.evaluate("""() => {
      const p = JSON.parse(localStorage.getItem('deskParametros') || '{}');
      p.confirmacoes = Object.assign({}, p.confirmacoes, { transportadorasCriar: true });
      localStorage.setItem('deskParametros', JSON.stringify(p));
    }""")
    pg2.reload(); pg2.wait_for_timeout(500)
    ok(pg2.evaluate("() => exigeSenha('transportadorasCriar')"), 'o interruptor de Configuracoes chega na tela')
    pg2.click('#btnNovaTransp'); pg2.wait_for_timeout(300)
    pg2.fill('#inputNomeTransp', 'Carga Leste')
    marcar_dias(pg2, 'qua')
    pg2.fill('#inputCorte', '09:00')
    pg2.fill('#inputPrazo', '2')
    pg2.fill('#inputPesoMax', '45')
    pg2.click('#btnSalvarTransp'); pg2.wait_for_timeout(350)
    ok(pg2.locator('#confirmModal').evaluate("el => el.classList.contains('open')"),
       'com a trava ligada, criar abre a folha de confirmacao')
    ok('Carga Leste' in pg2.locator('#confirmModalTexto').inner_text(),
       'e a folha diz o nome do que vai ser criado')
    ok(pg2.locator('#campoSenhaModal').evaluate("el => el.classList.contains('on')"),
       'com a trava ligada, o campo de senha aparece')
    pg2.fill('#inputSenhaModal', 'senha')
    confirmar(pg2)
    pg2.fill('#campoBusca', 'Carga Leste'); pg2.wait_for_timeout(300)
    ok(pg2.locator('.transp-card', has_text='Carga Leste').count() == 1, 'confirmada, a transportadora entra')
    pg2.fill('#campoBusca', ''); pg2.wait_for_timeout(200)
    registro = pg2.evaluate("() => (JSON.parse(localStorage.getItem('deskLog') || '[]')[0] || {})")
    ok(registro.get('chave') == 'transportadorasCriar', 'a acao foi para o registro de atividades: %s' % registro.get('chave'))
    ok(registro.get('senha') is True, 'e o registro guarda que houve senha')
    pg2.evaluate("() => localStorage.removeItem('deskParametros')")

    # ---------------------------------------------------------------- 8
    print('\n8. EDITAR CARREGA O QUE ESTAVA GRAVADO')
    pg.click('.transp-card:has-text("Frota Desk · Sul")')
    pg.wait_for_timeout(350)
    ok(pg.locator('#drawerTitulo').inner_text() == 'Frota Desk · Sul', 'o painel abre com o nome no titulo')
    ok(pg.locator('#inputUf').get_attribute('data-value') == 'RS', 'a UF gravada volta no dropdown')
    ok(pg.is_visible('#blocoMdfe'), 'frota gravada reabre com o bloco de MDF-e')
    ok('intermunicipal' in pg.locator('#textoMdfe').inner_text(),
       'e a frase do MDF-e ja vem com a regra do RS, sem precisar mexer na UF')
    ok(pg.locator('#diasColetaLabel').inner_text() == 'Terça, Quinta',
       'os dias voltam na ordem da semana: %s' % pg.locator('#diasColetaLabel').inner_text())
    ok(pg.locator('#linkExcluirTransp').is_visible(), 'editar oferece excluir; criar nao')

    # ---------------------------------------------------------------- 9
    print('\n9. FILTRO E BUSCA')
    pg.click('#btnCancelarTransp'); pg.wait_for_timeout(250)
    escolher(pg, 'filtroTipo', 'frota')
    ok(pg.locator('.transp-card').count() == 2, 'duas frotas proprias no mock')
    escolher(pg, 'filtroTipo', 'todos')
    escolher(pg, 'filtroSituacao', 'inativo')
    ok(pg.locator('.transp-card').count() == 2, 'duas inativas no mock')
    escolher(pg, 'filtroSituacao', 'todos')
    pg.fill('#campoBusca', '12.345.678')
    pg.wait_for_timeout(250)
    ok(pg.locator('.transp-card').count() == 1, 'a busca tambem acha por CNPJ')
    pg.fill('#campoBusca', 'xxxxx')
    pg.wait_for_timeout(250)
    ok(pg.locator('#emptyState').is_visible(), 'busca sem resultado mostra o estado vazio')
    pg.fill('#campoBusca', '')
    pg.wait_for_timeout(250)

    # ---------------------------------------------------------------- 10
    print('\n10. EXCLUIR PEDE SENHA E AVISA O QUE ACONTECE COM O HISTORICO')
    ok(pg.evaluate("() => exigeSenha('transportadorasExclui')"), 'excluir transportadora pede senha')
    ok(not pg.evaluate("() => exigeSenha('transportadorasCriar')"), 'criar nao pede senha por padrao')
    ok(not pg.evaluate("() => exigeSenha('transportadorasEditar')"), 'editar nao pede senha por padrao')
    pg.click('.transp-card:has-text("Entrega Já Expressa")')
    pg.wait_for_timeout(300)
    pg.click('#linkExcluirTransp')
    pg.wait_for_timeout(300)
    texto = pg.locator('#confirmModalTexto').inner_text()
    ok('Romaneios antigos' in texto, 'a confirmacao explica que o historico guarda o nome: %s' % texto[:80])
    ok(pg.locator('#campoSenhaModal').evaluate("el => el.classList.contains('on')"),
       'o campo de senha aparece dentro da propria folha de confirmacao')
    pg.click('#btnConfirmModalConfirmar')
    pg.wait_for_timeout(300)
    ok(pg.locator('#campoSenhaModal').evaluate("el => el.classList.contains('has-error')"),
       'confirmar sem senha nao exclui: a trava reclama')
    pg.fill('#inputSenhaModal', 'senha')
    confirmar(pg)
    ok(pg.locator('.transp-card', has_text='Entrega Já Expressa').count() == 0, 'com senha, exclui')

    # ---------------------------------------------------------------- 11
    print('\n11. A TRAVA NASCEU COM A TELA, E O CATALOGO E UMA LISTA SO')
    cat = pg.evaluate("""() => ACOES_SENHA.filter(a => a.base === 'transportadoras')
        .map(a => a.chave + '/' + a.ligado)""")
    ok(len(cat) == 3, 'os tres verbos estao no catalogo: %s' % cat)
    ok(all(c.endswith('/true') or c.endswith('/True') for c in cat),
       'nenhum deles e celula morta — modulo novo entra com os tres ligados')
    ok(pg.evaluate("() => ACOES_SENHA.filter(a => a.base === 'transportadoras')[0].grupo") == 'Operacional',
       'o catalogo arquiva a tela no grupo Operacional, igual a secao do hub')

    CHAVES = ['transportadorasCriar', 'transportadorasEditar', 'transportadorasExclui']
    for tela in ['pagina-configuracoes-confirmacoes-senha.html',
                 'pagina-cadastros-vendedores-detalhe.html',
                 'pagina-configuracoes-registro-atividades.html']:
        pgc = nova(pw, tela, erros)
        achadas = pgc.evaluate("() => ACOES_SENHA.map(a => a.chave)")
        faltando = [k for k in CHAVES if k not in achadas]
        ok(not faltando, '%s conhece as acoes de Transportadoras%s'
           % (tela.replace('pagina-', ''), '' if not faltando else ' — falta ' + ', '.join(faltando)))

    # ---------------------------------------------------------------- 12
    print('\n12. A PORTA E O HUB DE CONFIGURACOES, E O ITEM ANTIGO SUMIU DE TODAS AS TELAS')
    # Ate 08/out o item morava no menu lateral, em Operacional, e esta secao
    # cobrava o item em todas as telas. O modulo saiu do menu: cadastro que se
    # configura uma vez abre pelo hub. A secao agora cobra o contrario.
    hub = open(localiza.onde('pagina-configuracoes.html'), encoding='utf-8').read()
    ok(("href:'../configuracoes/" + TELA + "'") in hub, 'o hub de Configuracoes tem o cartao que abre esta tela')
    sobrou = [arq for arq in localiza.nomes()
              if 'data-label="Transportadoras"' in open(localiza.onde(arq), encoding='utf-8').read()]
    ok(not sobrou, 'nenhuma tela ficou com o item antigo no menu lateral%s' % ('' if not sobrou else ': ' + ', '.join(sobrou[:4])))

    print('\nERROS DE CONSOLE: ' + (str(erros) if erros else 'nenhum'))
    if erros: falhas.append('erro de console: %s' % erros)

print('\nFALHAS: ' + str(len(falhas)))
for f in falhas: print('  - ' + f)

# O codigo de saida e contrato, como ja valia para a auditoria.py: o selo le o
# texto, mas quem roda na mao (ou um script futuro) le o codigo. Sem isto a
# suite saia 0 com 20 falhas impressas, e um teste por exit code a dava verde.
raise SystemExit(1 if falhas else 0)
