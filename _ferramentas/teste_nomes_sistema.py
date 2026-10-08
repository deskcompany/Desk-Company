# Nomes do sistema — 08/out/2026.
#
# O sistema tem 28 conjuntos de rotulos escritos no codigo. Lista que CRESCE
# (motivos, depositos, categorias) ja e cadastro, e isso esta certo. O problema
# sao as listas FECHADAS, em que cada entrada dispara um comportamento:
# `revendavel` segue a regra de entrada, `avaria` bloqueia o saldo, `nenhum`
# nao entra no saldo. Elas nao podem virar cadastro — um quarto estado
# inventado nao teria codigo que o entendesse.
#
# A saida foi separar CHAVE de ROTULO. Esta suite guarda as duas metades dessa
# promessa, e e a segunda que importa mais:
#   renomear MUDA o que aparece em todas as telas que mostram o rotulo [6][8];
#   renomear NAO MUDA nada do que o sistema faz [7] — a chave e o destino no
#   estoque continuam exatamente os mesmos.
#
# Mais: o nome interno fica a vista ao lado do campo [2], dois rotulos iguais
# no mesmo grupo sao barrados antes de salvar [4] (senao a pessoa escolhe entre
# duas opcoes identicas sem saber qual faz o que), e renomear pede senha [5] —
# e mudanca que todo mundo ve.
#
# Nasceu ANTES do fluxo de entrada/conferencia de proposito: aquele fluxo vai
# criar rotulos novos e, sem esta tela, eles nasceriam fixos no codigo.
import sys
from playwright.sync_api import sync_playwright

URL = 'http://localhost:3000/'
TELA = 'pagina-configuracoes-nomes-sistema.html'

falhas = []
total = [0]


def ok(cond, texto):
    total[0] += 1
    print(('  ok  ' if cond else '  FALHOU  ') + texto)
    if not cond:
        falhas.append(texto)


def clicar(pg, sel):
    pg.evaluate("(s) => document.querySelector(s).click()", sel)


with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1440, 'height': 950})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)))

    print('[1] A tela existe e e alcancavel por Configuracoes')
    pg.goto(URL + 'pagina-configuracoes.html')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    alvo = pg.locator('[data-href="pagina-configuracoes-nomes-sistema.html"]')
    ok(alvo.count() >= 1, 'o card aparece na tela de Configuracoes')

    pg.goto(URL + TELA); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    # O numero cresce conforme os conjuntos fechados vao entrando: 11 na
    # estreia (devolucao), 19 depois que entrada de notas entrou. A asserção
    # mede o CONTRATO, nao o numero: todo rotulo declarado tem campo na tela.
    campos = pg.locator('[data-nome]').count()
    declarados = pg.evaluate('TODAS_CHAVES.length')
    ok(campos == declarados,
       'todo rotulo declarado tem campo na tela (%d campos, %d declarados)' % (campos, declarados))
    ok(declarados == pg.evaluate('Object.keys(NOMES_PADRAO).length'),
       'e nenhum rotulo do dicionario fica fora da tela de edicao')

    print('[2] O nome INTERNO aparece ao lado, e e ele que nao muda')
    corpo = pg.inner_text('.main')
    ok('devolucao.estado.revendavel' in corpo, 'a chave interna fica a vista')

    print('[3] A nota conta, e o rodape e o padrao da casa')
    ok('Nenhuma alteração pendente' in pg.inner_text('#notaBarra'),
       'abre sem pendencia: %s' % pg.inner_text('#notaBarra'))
    pg.fill('[data-nome="devolucao.estado.avaria"]', 'Quebrada')
    pg.wait_for_timeout(250)
    ok('1 nome alterado' in pg.inner_text('#notaBarra'),
       'depois de renomear: %s' % pg.inner_text('#notaBarra'))

    print('[4] Dois nomes iguais no mesmo grupo sao barrados')
    pg.fill('[data-nome="devolucao.estado.nenhum"]', 'Quebrada')
    pg.wait_for_timeout(250)
    ok('Dois nomes iguais' in pg.inner_text('#notaBarra'),
       'a nota avisa: %s' % pg.inner_text('#notaBarra')[:48])
    ok('has-error' in (pg.get_attribute('[data-nome="devolucao.estado.nenhum"]', 'class') or ''),
       'e o campo repetido fica marcado')
    clicar(pg, '#btnSalvarNomes')
    pg.wait_for_timeout(400)
    ok(pg.locator('#avisoModal.open').count() == 1, 'salvar com repetido para e explica')
    clicar(pg, '#btnAvisoOk')
    pg.wait_for_timeout(300)

    print('[5] Renomear exige senha — e mudanca que todo mundo ve')
    pg.fill('[data-nome="devolucao.estado.nenhum"]', 'Não voltou')
    pg.wait_for_timeout(200)
    clicar(pg, '#btnSalvarNomes')
    pg.wait_for_timeout(500)
    ok(pg.locator('#confirmModal.open').count() == 1, 'o modal de confirmacao abriu')
    ok(pg.locator('#campoSenhaModal').is_visible(), 'e com o campo de senha, porque exigePadrao e true')
    pg.fill('#inputSenhaModal', 'seiasenha')
    clicar(pg, '#btnConfirmModalConfirmar')
    pg.wait_for_timeout(600)

    print('[6] O novo nome chega nas OUTRAS telas — e a mesma lista')
    pg.goto(URL + 'pagina-logistica-devolucao-detalhe.html?id=1')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(800)
    corpo = pg.inner_text('.main')
    ok('Quebrada' in corpo, 'o detalhe da devolucao mostra o nome novo')
    ok('Avariada' not in corpo, 'e o antigo sumiu de la')

    print('[7] O que o sistema FAZ nao mudou: a chave e a mesma')
    destino = pg.evaluate("ESTADOS_ITEM.avaria.destino")
    ok(destino == 'Avaria, bloqueado', 'o destino no estoque continua o mesmo: %s' % destino)
    chave = pg.evaluate("Object.keys(ESTADOS_ITEM).join(',')")
    ok(chave == 'revendavel,avaria,nenhum', 'e as chaves nao se mexeram: %s' % chave)

    print('[8] O cadastro de Motivos tambem acompanha')
    # Renomeia o estado que o cadastro de Motivos DE FATO mostra. "Avaria" na
    # linha do motivo e o DEPOSITO de destino, nao o estado da mercadoria —
    # dois nomes parecidos, duas coisas diferentes.
    pg.goto(URL + TELA); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    pg.fill('[data-nome="devolucao.estado.revendavel"]', 'Pronta pra vitrine')
    pg.wait_for_timeout(200)
    clicar(pg, '#btnSalvarNomes'); pg.wait_for_timeout(500)
    if pg.locator('#campoSenhaModal').is_visible():
        pg.fill('#inputSenhaModal', 'seiasenha')
    clicar(pg, '#btnConfirmModalConfirmar'); pg.wait_for_timeout(500)
    pg.goto(URL + 'pagina-operacional-motivos-devolucao.html')
    pg.wait_for_load_state('load'); pg.wait_for_timeout(800)
    ok('pronta pra vitrine' in pg.inner_text('#listaMotivos').lower(),
       'a lista de motivos usa o nome novo')
    ok('pronta pra vitrine' in pg.inner_text('#inputDestino').lower(),
       'e o dropdown de destino tambem — o rotulo nao fica so na metade da tela')

    print('[9] Restaurar padrao devolve tudo')
    pg.goto(URL + TELA); pg.wait_for_load_state('load'); pg.wait_for_timeout(700)
    ok(pg.input_value('[data-nome="devolucao.estado.avaria"]') == 'Quebrada',
       'o nome salvo sobreviveu ao recarregar')
    clicar(pg, '#btnRestaurarNomes')
    pg.wait_for_timeout(400)
    clicar(pg, '#btnAvisoOk')
    pg.wait_for_timeout(200)
    ok(pg.input_value('[data-nome="devolucao.estado.avaria"]') == 'Avariada',
       'restaurar traz o padrao de volta para a tela')
    clicar(pg, '#btnSalvarNomes')
    pg.wait_for_timeout(500)
    if pg.locator('#campoSenhaModal').is_visible():
        pg.fill('#inputSenhaModal', 'seiasenha')
    clicar(pg, '#btnConfirmModalConfirmar')
    pg.wait_for_timeout(500)

    print('[10] Nenhum erro de JS no caminho todo')
    ok(not erros, 'console limpo: %s' % (erros[:1] or 'sim'))

    pg.evaluate("localStorage.removeItem('deskNomes')")
    nav.close()

print('')
print('%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
