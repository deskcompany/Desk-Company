# -*- coding: utf-8 -*-
# Usuarios do sistema e Permissoes de usuarios, entrega 1 (10/nov/2026): a lista de usuarios, a pagina do usuario, a lista de perfis e a pagina do perfil.
#
# O que ele protege sao as decisoes do usuario (barganha de 10/nov/2026, com os prints do Olist como piso):
#   Um perfil por usuario, mais permissoes avulsas que so ACRESCENTAM ao perfil
#   O codigo de autorizacao e separado da senha de entrar: de 4 a 6 numeros, por pessoa, e nunca e mostrado depois de gravado
#   O desconto sem senha: o perfil traz um padrao, a pessoa pode ter um proprio que vale no lugar dele (vazio = o do perfil); o Owner nao tem limite
#   A grade e a lista do Olist com os modulos do NOSSO menu: cada tela do menu e um item, as funcoes de dentro so valem com o item marcado, "Marcar todos" por
#   aba e, no fim, as acoes que pedem autorizacao (as mesmas chaves de Confirmacoes por senha)
#   O Owner nao se edita nem se exclui; so excluir perfil sem usuario; clonar copia como perfil novo; so quem esta com o perfil Owner altera
#   Alterar a grade de um perfil ou as permissoes avulsas de alguem pede a senha (perfilPermissoes, usuarioPermissoes); incluir, bloquear, trocar a senha e
#   trocar o codigo vao para o Registro de atividades
#
#   [1]  As copias e os espelhos: o catalogo (4 telas), a grade (2) e os dados (5 telas); o catalogo contra o menu e o hub; os usuarios contra as telas de origem;
#        as duas acoes novas no catalogo de Confirmacoes por senha, em todas as telas
#   [2]  As ligacoes entre as telas: o hub, Vendedores (o usuario vinculado), a lista, o perfil, o vendedor
#   [3]  A lista de usuarios: indicadores que filtram, busca, filtros, painel, ordem
#   [4]  A pagina do usuario, nos dois modos (?id e ?novo=1), e as validacoes
#   [5]  O codigo de autorizacao: so 4 a 6 numeros e nunca mostrado; a senha de acesso
#   [6]  O desconto sem senha: o proprio vale no lugar do perfil
#   [7]  A grade e a pagina do perfil: marcar todos, a hierarquia, o Owner travado, a senha ao mudar a grade
#   [8]  As permissoes avulsas so acrescentam
#   [9]  A lista de perfis: excluir so perfil sem usuario, clonar, o Owner
#   [10] Bloquear e ativar; so o Owner altera; o Registro de atividades
#   [11] Os dois temas, em 1280 e 1440: sem barra para o lado e o menu abre para baixo
from playwright.sync_api import sync_playwright
import os as _os, glob as _g, re, sys, shutil, tempfile
import localiza
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None
SO = (sys.argv[1:] or [''])[0]
LU = 'pagina-configuracoes-usuarios.html'
DU = 'pagina-configuracoes-usuarios-detalhe.html'
LP = 'pagina-configuracoes-perfis-usuario.html'
DP = 'pagina-configuracoes-perfis-usuario-detalhe.html'
QUATRO = (LU, DU, LP, DP)
HUB = 'pagina-configuracoes.html'
CONF = 'pagina-configuracoes-confirmacoes-senha.html'
VEND = 'pagina-cadastros-vendedores.html'
VENDD = 'pagina-cadastros-vendedores-detalhe.html'
REG = 'pagina-configuracoes-registro-atividades.html'

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


def fonte(nome):
    return open(localiza.onde(nome), encoding='utf-8').read()


def bloco(t, ini, fim):
    i = t.find(ini)
    if i < 0:
        return None
    j = t.find(fim, i)
    return t[i:j] if j >= 0 else None


with sync_playwright() as p:
    nav = p.chromium.launch(executable_path=CHROME)
    pg = nav.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('pageerror', lambda e: erros.append(str(e)[:160]))
    pg.on('dialog', lambda d: d.dismiss())

    def ir(tela, q=''):
        pg.goto(localiza.uri(tela) + q); pg.wait_for_load_state('load'); pg.wait_for_timeout(250)

    def limpo(tela, q=''):
        ir(tela); pg.evaluate("localStorage.clear(); sessionStorage.clear()"); ir(tela, q)

    def ev(js, *a):
        return pg.evaluate(js, *a) if a else pg.evaluate(js)

    def clica(sel):
        pg.evaluate("(s) => document.querySelector(s).click()", sel); pg.wait_for_timeout(150)

    def preenche(sel, valor):
        pg.fill(sel, valor); pg.wait_for_timeout(60)

    def confirmar(senha=None):
        if senha is not None:
            pg.fill('#inputSenhaModal', senha)
        clica('#btnConfirmModalConfirmar'); pg.wait_for_timeout(300)

    def modal_aberto():
        return ev("document.getElementById('confirmModal').classList.contains('open')")

    def nomes_lista():
        return ev("Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())")

    def usuarios():
        return ev("JSON.parse(localStorage.getItem('deskUsuarios') || 'null')")

    def perfis():
        return ev("JSON.parse(localStorage.getItem('deskPerfis') || 'null')")

    def log(chave):
        return ev("(k) => JSON.parse(localStorage.getItem('deskLog') || '[]').filter(e => e.chave === k)", chave)

    def marcar_grade(chave, ligado=True):
        """Marca ou desmarca uma chave da grade pelo clique de verdade na caixa."""
        pg.evaluate("""([c, l]) => { const e = document.querySelector('.pg-chk[data-chave="' + c + '"]');
            if (e.checked !== l) e.click(); }""", [chave, ligado]); pg.wait_for_timeout(80)

    def abrir_aba(modulo):
        clica('.aba-sit[data-aba="%s"]' % modulo)

    # ------------------------------------------------------------------------------------------------
    if secao(1, 'As cópias, os espelhos, o catálogo e o menu'):
        CI, CF = '  // ===== PERMISSOES: O CATALOGO', '  // ===== FIM DO BLOCO PERMISSOES: O CATALOGO ====='
        cop = [bloco(fonte(n), CI, CF) for n in QUATRO]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco PERMISSOES: O CATALOGO é idêntico nas quatro telas')
        GI, GF = '  // ===== PERMISSOES: A GRADE', '  // ===== FIM DO BLOCO PERMISSOES: A GRADE ====='
        cop = [bloco(fonte(n), GI, GF) for n in (DU, DP)]
        ok(cop[0] and cop[0] == cop[1], 'o bloco PERMISSOES: A GRADE é idêntico nas duas páginas')
        DI, DF = '  // ===== USUARIOS E PERFIS: DADOS E LEITURA', '  // ===== FIM DO BLOCO USUARIOS E PERFIS ====='
        cop = [bloco(fonte(n), DI, DF) for n in QUATRO + (VENDD,)]
        ok(cop[0] and all(c == cop[0] for c in cop), 'o bloco USUARIOS E PERFIS é idêntico nas quatro telas e na página do vendedor')
        for n in QUATRO:
            f = fonte(n)
            ok(localiza.pasta(n) == 'configuracoes', '%s mora em Configurações' % n)
        # o catalogo contra o menu: cada tela do menu e um item, com o nome e a tela do menu
        hub = fonte(HUB)
        menu = {}
        for fly, corpo in re.findall(r'id="flyout-([a-z]+)"(.*?)(?=<div class="flyout-col"|<div class="main">)', hub, re.S):
            if fly == 'config':
                continue
            for lab, href in re.findall(r'data-label="([^"]+)" data-href="\.\./[a-z]+/(pagina-[a-z0-9-]+\.html)"', corpo):
                menu[lab] = href
        ir(LU)
        cat = ev("PERM_MODULOS.filter(m => m.id !== 'configuracoes').reduce((r, m) => r.concat(m.itens.map(i => [i.nome, i.tela])), [])")
        cat_d = {a: localiza.nome(b) for a, b in cat}
        ok(len(menu) >= 40 and cat_d == menu, 'os itens da grade (fora de Configurações) são os itens do menu com tela, com o mesmo nome: %d no menu, %d na grade; faltam %s, sobram %s' %
           (len(menu), len(cat_d), sorted(set(menu) - set(cat_d))[:3], sorted(set(cat_d) - set(menu))[:3]))
        mods = ev("PERM_MODULOS.map(m => m.nome)")
        ok(mods == ['Início', 'Cadastros', 'Estoque', 'Vendas', 'Logística', 'Finanças', 'Integrações', 'Configurações'], 'as abas são os módulos do nosso menu: %s' % mods)
        telas = ev("PERM_MODULOS.reduce((r, m) => r.concat(m.itens.map(i => [m.id, i.tela])), [])")
        ok(all(localiza.existe(localiza.nome(t)) and localiza.pasta(localiza.nome(t)) == m and t == '../%s/%s' % (m, localiza.nome(t)) for m, t in telas), 'cada item da grade é uma tela que existe, na pasta do módulo dele (%d itens)' % len(telas))
        hrefs = set(re.findall(r"href:'\.\./configuracoes/(pagina-[a-z0-9-]+\.html)'", hub))
        ok(hrefs <= set(localiza.nome(t) for m, t in telas if m == 'configuracoes'), 'toda tela de Configurações aberta pelo hub é item da grade: sobram %s' % sorted(hrefs - set(localiza.nome(t) for m, t in telas))[:3])
        chaves = ev("permTodasChaves()")
        ok(len(chaves) == len(set(chaves)), 'nenhuma chave da grade se repete (%d chaves)' % len(chaves))
        ok(ev("PERM_MODULOS.every(m => m.itens.every(i => /^[A-Za-z]+$/.test(i.id)))"), 'a chave de cada item é só letras')
        fn = ev("PERM_MODULOS.reduce((r, m) => r.concat(m.itens.map(i => [m.id + '/' + i.id, Object.keys(i.fn || {}).length])), [])")
        ok(sum(n for _, n in fn) >= 150, 'as funções concretas de cada tela estão na grade (%d funções)' % sum(n for _, n in fn))
        com_fn = {k: n for k, n in fn}
        ok(com_fn['vendas/pdv'] == 6 and ev("Object.keys(PERM_MODULOS[3].itens[2].fn).join(',')") == 'abrirCaixa,fecharCaixa,relatorio,sangria,reforco,cancelarVenda', 'o PDV tem abrir e fechar o caixa, o relatório de controle de caixa, a sangria, o reforço e cancelar venda')
        ok(ev("['pedidos', 'crm', 'metas'].every(i => PERM_MODULOS.reduce((r, m) => r.concat(m.itens), []).filter(x => x.id === i)[0].fn.verOutros)"), 'Pedidos de Venda, CRM e Metas têm "ver os de outros vendedores"')
        ok(ev("PERM_MODULOS[0].itens.map(i => i.id).join(',')") == 'boasVindas,dashboardKpis,agenda,minhaConta', 'tela sem função própria fica só com o item de acesso (Início)')
        # as acoes: as mesmas chaves e nomes do catalogo de Confirmacoes por senha, agrupadas pelo grupo
        ir(CONF)
        conf = ev("ACOES_SENHA.filter(a => a.pronto && a.ligado && exigeSenha(a.chave)).map(a => [a.chave, a.nome, a.grupo])")
        ir(LU)
        mine = ev("permAcoes().map(a => [a.chave, a.nome, a.grupo])")
        ok(mine == conf and len(conf) > 40, 'as ações de autorização são as de Confirmações por senha, com as mesmas chaves e nomes (%d ações que pedem senha hoje)' % len(conf))
        ok(set(g for _, _, g in conf) <= set(ev("Object.keys(PERM_GRUPO_MODULO)")), 'todo grupo do catálogo cai numa aba da grade')
        ok(ev("permAcoes().every(a => permModuloDoGrupo(a.grupo) && permTodasChaves().includes('@' + a.chave))"), 'cada ação aparece na grade, na aba do módulo dela')
        # as duas acoes novas, em todas as telas com o catalogo completo
        com = [n for n in localiza.nomes() if "chave:'promocaoNaHora'" in fonte(n)]
        sem = [n for n in com if "chave:'perfilPermissoes'" not in fonte(n) or "chave:'usuarioPermissoes'" not in fonte(n)]
        ok(len(com) >= 29 and not sem, 'as duas ações novas estão no catálogo das %d telas que têm o catálogo completo; faltam em %s' % (len(com), sem[:3]))
        ok(ev("ACOES_SENHA.filter(a => ['perfilPermissoes', 'usuarioPermissoes'].includes(a.chave)).map(a => [a.chave, a.grupo, a.exigePadrao, a.nome])") ==
           [['perfilPermissoes', 'Configurações', True, 'Alterar as permissões de um perfil'], ['usuarioPermissoes', 'Configurações', True, 'Alterar o perfil ou as permissões avulsas de um usuário']],
           'perfilPermissoes e usuarioPermissoes: grupo Configurações, com senha de fábrica, com os nomes combinados')
        ir(CONF)
        ok(ev("['perfilPermissoes', 'usuarioPermissoes'].every(k => ACOES_SENHA.filter(a => a.chave === k).length === 1 && exigeSenha(k))"), 'Confirmações por senha mostra as duas, ligadas')
        # as pessoas: as que ja existem nas outras telas
        ir('pagina-inicio-minha-conta.html')
        equipe = ev("SUBORDINADOS.map(s => s.nome)")
        ir('pagina-vendas-metas.html')
        vends = ev("VENDEDORES.map(v => v.nome)")
        ir(LU)
        nomes = ev("UP_USUARIOS_FABRICA.map(u => u.nome)")
        ok(set(nomes) - {'Administrador Desk'} <= set(equipe) | set(vends) | {'Rafael Andrade'}, 'os usuários de exemplo são pessoas que já existem no sistema: %s' % nomes)
        ok(all(n in nomes for n in equipe), 'a equipe de Minha Conta (%s) está entre os usuários' % ', '.join(equipe))
        ok(len(nomes) == len(set(nomes)) and ev("UP_USUARIOS_FABRICA.map(u => u.login).every(l => /^[a-z0-9._-]+@desk$/.test(l))"), 'o login de cada um é nome@desk, sem repetir')
        ir(VEND)
        vend_cad = ev("VENDEDORES.filter(v => !v.excluido).map(v => [v.id, v.nome])")
        ir(LU)
        ok(ev("UP_VENDEDORES.map(v => [v.id, v.nome])") == vend_cad, 'UP_VENDEDORES espelha Cadastros → Vendedores (os que não foram excluídos): %s' % vend_cad)
        ir('pagina-logistica-devolucao.html')
        lojas = ev("LOJAS")
        ir(LU)
        ok(ev("UP_LOJAS") == lojas, 'as quatro lojas espelham as de Devolução')
        # os perfis de partida
        ok(ev("UP_PERFIS_FABRICA.map(p => p.nome)") == ['Owner', 'Gerente', 'Supervisor de vendas', 'Vendedor interno', 'Caixa / vendedor de balcão', 'Representante externo'], 'os seis perfis de partida')
        ok(ev("UP_PERFIS_FABRICA.map(p => p.descontoPct)") == [None, 20, 15, 10, 10, 10], 'os descontos de partida: Gerente 20%, Supervisor 15%, Vendedor interno 10%, Caixa 10%, Representante 10% (o Owner sem limite)')
        ok(ev("UP_PERFIS_FABRICA.filter(p => p.fixo).map(p => p.nome)") == ['Owner'], 'só o Owner é fixo')
        a = ev("(() => { const g = lerPerfis().filter(p => p.nome === 'Gerente')[0], s = lerPerfis().filter(p => p.nome === 'Supervisor de vendas')[0]; return [permContar(permExpandir(g.perms)).acoes, permContar(permExpandir(s.perms)).acoes]; })()")
        ok(a[0] > 30 and a[1] == 0, 'o Gerente vem com as ações de autorização marcadas (%d) e o Supervisor com nenhuma' % a[0])
        ok(ev("permContar(permExpandir(lerPerfis()[0].perms)).acoes") == len(conf) and ev("permExpandir(['*']).size") == len(chaves), 'o Owner tem tudo marcado: %d chaves' % len(chaves))
        quatro = ev("(() => { const ps = lerPerfis(), pega = n => permExpandir(ps.filter(p => p.nome === n)[0].perms); const caixa = pega('Caixa / vendedor de balcão'), vi = pega('Vendedor interno'), rep = pega('Representante externo'), sup = pega('Supervisor de vendas');"
                    " return [caixa.has('pdv.abrirCaixa') && caixa.has('pdv.fecharCaixa') && caixa.has('pdv.relatorio'), !vi.has('pdv'), vi.has('pedidos') && !vi.has('pedidos.verOutros'), rep.has('crm') && !rep.has('pdv'), sup.has('pedidos.verOutros') && sup.has('metas') && !sup.has('pdv')]; })()")
        ok(all(quatro), 'os perfis de venda seguem o mapa dos canais: caixa abre e fecha o caixa, vendedor interno não usa o PDV e não vê pedido de outros, representante sem PDV, supervisor vê os de outros: %s' % quatro)
        us = ev("UP_USUARIOS_FABRICA.map(u => [u.nome, u.perfilId, u.situacao, !!u.codigoHash])")
        ok({u[1] for u in us} == {1, 2, 3, 4, 5, 6}, 'tem pelo menos um usuário de cada perfil')
        ok(sum(1 for u in us if u[2] == 'bloqueado') == 1 and sum(1 for u in us if not u[3]) == 2, 'um usuário bloqueado e dois sem código de autorização')

    # ------------------------------------------------------------------------------------------------
    if secao(2, 'As ligações entre as telas'):
        limpo(HUB)
        ir(HUB)
        hub = fonte(HUB)
        ok("nome:'Usuários do sistema', href:'../configuracoes/pagina-configuracoes-usuarios.html'" in hub, 'o hub liga "Usuários do sistema" à lista')
        ok("nome:'Permissões de usuários', href:'../configuracoes/pagina-configuracoes-perfis-usuario.html'" in hub, 'o hub liga "Permissões de usuários" à lista de perfis, com a ajuda atualizada')
        ok('as mesmas de Confirmações por senha' in hub and 'Mesma grade de Confirmações por senha, com outra pergunta' not in hub, 'a ajuda de Permissões de usuários não é mais a de "ainda não existe"')
        for rotulo, destino in (('Usuários do sistema', LU), ('Permissões de usuários', LP)):
            ir(HUB)
            pg.evaluate("(r) => { const el = Array.from(document.querySelectorAll('.cfg-item, .item-config, [data-nome], a, div')).filter(e => e.textContent.trim().indexOf(r) === 0 && e.children.length < 6)[0]; }", rotulo)
        # o hub: cada card navega (a aba Geral abre primeiro)
        ir(HUB)
        achados = ev("""() => Array.from(document.querySelectorAll('*')).filter(e => e.children.length === 0 && ['Usuários do sistema', 'Permissões de usuários'].includes(e.textContent.trim()))
                        .map(e => { let n = e; while (n && !(n.onclick || n.getAttribute('data-href') || n.tagName === 'A')) n = n.parentElement; return e.textContent.trim() + '|' + (n ? (n.getAttribute('href') || n.getAttribute('data-href') || 'clique') : 'solto'); })""")
        ok(len(achados) >= 2 and all(not a.endswith('|solto') for a in achados), 'os dois cards do hub são clicáveis: %s' % achados)
        for rotulo, destino in (('Usuários do sistema', LU), ('Permissões de usuários', LP)):
            ir(HUB)
            pg.evaluate("""(r) => { const el = Array.from(document.querySelectorAll('*')).filter(e => e.children.length === 0 && e.textContent.trim() === r)[0]; el.click(); }""", rotulo)
            pg.wait_for_timeout(500)
            ok(localiza.nome(pg.url).split('?')[0] == destino, 'clicar em "%s" no hub abre %s (abriu %s)' % (rotulo, destino, localiza.nome(pg.url)))
        # Vendedores: o usuario vinculado
        limpo(VENDD, '?id=1')
        ok('Marina Costa' in ev("document.getElementById('blocoUsuarioVinculado').textContent") and ev("document.getElementById('linkUsuarioVinculado').getAttribute('href')") == '../configuracoes/pagina-configuracoes-usuarios-detalhe.html?id=3',
           'o vendedor Marina Costa mostra o usuário vinculado, com o link para a página dele')
        ok(ev("document.getElementById('linkPerfilVinculado').textContent") == 'Supervisor de vendas' and ev("document.getElementById('situacaoUsuarioVinculado').textContent") == 'ativo', 'e o perfil e a situação dele')
        ir(VENDD, '?id=3')
        ok(ev("document.getElementById('situacaoUsuarioVinculado').textContent") == 'bloqueado' and 'Rafael Andrade' in ev("document.getElementById('blocoUsuarioVinculado').textContent"), 'Rafael Andrade: o usuário vinculado está bloqueado')
        ir(VENDD, '?id=2')
        ok(ev("document.getElementById('linkIncluirUsuarioVendedor').getAttribute('href')") == '../configuracoes/pagina-configuracoes-usuarios-detalhe.html?novo=1', 'o vendedor sem usuário leva a "incluir usuário"')
        ir(VENDD, '?id=1')
        ok(ev("['inputUsuarioSistema', 'chkAcessoHorario', 'chkAcessoIp'].every(i => document.getElementById(i).disabled) && Array.from(document.querySelectorAll('#listaModulosAcesso input')).every(i => i.disabled)"),
           'horário, IP e módulos deixaram de ser editados na ficha do vendedor (só consulta)')
        ok('Configurações → Usuários do sistema' in ev("document.getElementById('tab-acesso').textContent"), 'a aba diz onde os campos de acesso moram agora')
        clica('#linkUsuarioVinculado'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == DU + '?id=3' and ev("document.getElementById('inputNome').value") == 'Marina Costa', 'o link do vendedor abre a página do usuário dele')
        # a lista de usuarios
        ir(LU)
        ok(ev("document.getElementById('btnPerfis').getAttribute('href')") == '../configuracoes/pagina-configuracoes-perfis-usuario.html' and ev("document.getElementById('btnIncluirUsuario').getAttribute('href')") == DU.join(['../configuracoes/', '?novo=1']),
           'a lista tem "Perfis e permissões" e "Incluir usuário"')
        clica('#menuMaisAcoes .dropdown-select-btn'); pg.wait_for_timeout(100)
        ok(ev("Array.from(document.querySelectorAll('#menuMaisAcoes .dropdown-select-item')).map(i => i.textContent.trim())") == ['Gerenciar vendedores', 'Baixar planilha', 'Imprimir'], 'Mais ações: Gerenciar vendedores, Baixar planilha e Imprimir')
        clica('#menuMaisAcoes [data-acao="vendedores"]'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == VEND, '"Gerenciar vendedores" leva a Cadastros → Vendedores')
        ir(LU); clica('#btnPerfis'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LP, '"Perfis e permissões" leva à lista de perfis')
        clica('#btnUsuarios'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LU, 'e a lista de perfis leva de volta aos usuários')
        # o painel da lista leva ao perfil e ao vendedor
        ir(LU); clica('#corpoTabela tr[data-id="3"]'); pg.wait_for_timeout(300)
        ok(ev("document.getElementById('linkPerfil').getAttribute('href')") == '../configuracoes/pagina-configuracoes-perfis-usuario-detalhe.html?id=3' and ev("document.getElementById('linkVendedor').getAttribute('href')") == '../cadastros/pagina-cadastros-vendedores-detalhe.html?id=1',
           'o painel do usuário leva ao perfil e à ficha do vendedor')
        clica('#linkPerfil'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == DP + '?id=3' and ev("document.getElementById('inputNome').value") == 'Supervisor de vendas', 'o link do perfil abre a página dele')
        clica('#linkUsuariosDoPerfil'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LU + '?perfil=3' and nomes_lista() == ['Marina Costa'], '"Quem tem este perfil" leva à lista de usuários já filtrada pelo perfil')
        ir(DU, '?id=3'); clica('#linkFichaVendedor'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == VENDD + '?id=1', 'a página do usuário abre a ficha do vendedor vinculado')
        ir(DU, '?id=3'); clica('#linkPerfil'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == DP + '?id=3', 'e o perfil')
        ir(DU, '?id=3'); clica('#btnVoltarLista'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LU, 'o "Voltar para Usuários do sistema" da página volta para a lista')
        ir(DU, '?id=3'); pg.locator('#breadcrumb .crumb').nth(2).click(); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LU, 'o nome do meio do caminho leva à lista')
        ir(DP, '?id=3'); pg.locator('#breadcrumb .crumb').nth(2).click(); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LP, 'e na página do perfil, à lista de perfis')
        ir(DP, '?id=3'); clica('#btnVoltarLista'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LP, '"Voltar para Permissões de usuários" volta para a lista de perfis')
        ir(DP, '?id=3'); clica('#linkUsuariosDoPerfil'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == LU + '?perfil=3', 'a página do perfil leva aos usuários dele')
        ir(DP, '?id=99')
        ok(ev("document.getElementById('naoEncontrado').style.display") == '' and ev("document.getElementById('conteudoPerfil').style.display") == 'none', 'perfil que não existe: a página diz isso, sem mostrar perfil nenhum')
        ir(DU, '?id=99')
        ok(ev("document.getElementById('naoEncontrado').style.display") == '' and ev("document.getElementById('conteudoUsuario').style.display") == 'none', 'usuário que não existe: a página diz isso')

    # ------------------------------------------------------------------------------------------------
    if secao(3, 'A lista de usuários'):
        limpo(LU)
        ok(nomes_lista() == ['Administrador Desk', 'Ana Souza', 'Bianca Furtado', 'Carlos Mendes', 'Fernanda Lima', 'Marina Costa', 'Rafael Andrade'], 'abre com os 7 usuários, em ordem de nome: %s' % nomes_lista())
        cabec = ev("Array.from(document.querySelectorAll('.estoque-table thead th')).map(t => t.textContent.replace(/[▲▼]/g, '').trim())")
        ok(cabec == ['Usuário', 'Login', 'Perfil', 'Lojas', 'Vendedor', 'Desconto sem senha', 'Situação'], 'colunas: nome, login, perfil, lojas, vendedor, desconto sem senha e situação')
        linhas = ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => Array.from(tr.children).map(c => c.textContent.replace(/\\s+/g, ' ').trim()))")
        marina = [l for l in linhas if 'Marina Costa' in l[0]][0]
        ok(marina[1] == 'marina.costa@desk' and marina[2] == 'Supervisor de vendas' and marina[3] == 'Desk Shope, Desk Brands' and marina[4] == 'Marina Costa' and marina[5] == '18%' and 'Ativo' in marina[6], 'Marina: login, perfil, lojas, vendedor vinculado, o desconto próprio (18%%) e a situação: %s' % marina)
        ana = [l for l in linhas if 'Ana Souza' in l[0]][0]
        ok(ana[5] == 'do perfil: 10%', 'quem não tem desconto próprio mostra "do perfil: 10%%": %s' % ana[5])
        adm = [l for l in linhas if 'Administrador Desk' in l[0]][0]
        ok(adm[5] == 'Sem limite', 'o Owner mostra "Sem limite"')
        ok(ev("document.querySelector('#corpoTabela tr .up-av').textContent") == 'AD', 'a inicial vai em círculo')
        kpis = ev("Array.from(document.querySelectorAll('#indicadoresUsuarios .kpi-card')).map(c => [c.querySelector('.kpi-label').textContent.trim(), c.querySelector('.kpi-value').textContent.trim()])")
        ok(kpis == [['Ativos', '6'], ['Bloqueados', '1'], ['Autorizam', '3'], ['Sem código de autorização', '2']], 'indicadores: Ativos, Bloqueados, Autorizam e Sem código de autorização: %s' % kpis)
        esperado = {'ativos': ['Administrador Desk', 'Ana Souza', 'Bianca Furtado', 'Carlos Mendes', 'Fernanda Lima', 'Marina Costa'], 'bloqueados': ['Rafael Andrade'],
                    'autorizam': ['Administrador Desk', 'Carlos Mendes', 'Marina Costa'], 'semCodigo': ['Bianca Furtado', 'Fernanda Lima']}
        for k, quem in esperado.items():
            clica('#indicadoresUsuarios [data-kpi="%s"]' % k)
            ok(nomes_lista() == quem and ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"%s\"]').getAttribute('aria-pressed')" % k) == 'true',
               'o indicador "%s" deixa na lista exatamente quem ele somou e fica aceso: %s' % (k, nomes_lista()))
            clica('#indicadoresUsuarios [data-kpi="%s"]' % k)
            ok(len(nomes_lista()) == 7 and ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"%s\"]').getAttribute('aria-pressed')" % k) == 'false', 'clicar de novo desfaz o indicador')
        # "Autorizam" conta quem tem acao E codigo: a Ana tem codigo e nenhuma acao; a Bianca nao tem codigo
        ok(ev("(() => { const ps = lerPerfis(), us = lerUsuarios(); const f = n => us.filter(u => u.nome === n)[0]; return [permAutoriza(ps.filter(p => p.id === f('Ana Souza').perfilId)[0], f('Ana Souza')), permAutoriza(ps[0], Object.assign({}, f('Administrador Desk'), { codigoHash: null }))]; })()") == [False, False],
           'quem tem o código mas nenhuma ação não autoriza, e quem tem a ação mas não tem o código também não')
        clica('#indicadoresUsuarios [data-kpi="bloqueados"]'); preenche('#campoBusca', 'ana')
        ok(ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"bloqueados\"]').getAttribute('aria-pressed')") == 'false' and nomes_lista() == ['Ana Souza'], 'mexer na busca à mão apaga o indicador')
        preenche('#campoBusca', ''); pg.wait_for_timeout(100)
        for termo, quem in (('marina.costa', ['Marina Costa']), ('example.com', ['Marina Costa']), ('CARLOS', ['Carlos Mendes']), ('Fernanda', ['Fernanda Lima']), ('nao existe', [])):
            preenche('#campoBusca', termo)
            ok(nomes_lista() == quem, 'a busca "%s" acha %s' % (termo, quem))
        ok(ev("document.getElementById('emptyState').style.display") == 'flex', 'sem resultado, a lista diz que não há usuário e oferece limpar os filtros')
        clica('#btnLimparFiltros')
        ok(len(nomes_lista()) == 7 and ev("document.getElementById('campoBusca').value") == '', 'limpar os filtros devolve os 7')
        for dd, valor, quem in (('filtroPerfil', '2', ['Carlos Mendes']), ('filtroPerfil', '4', ['Ana Souza', 'Bianca Furtado']), ('filtroLoja', '3', ['Administrador Desk', 'Carlos Mendes', 'Rafael Andrade']),
                                ('filtroLoja', '2', ['Administrador Desk', 'Carlos Mendes', 'Fernanda Lima', 'Marina Costa']), ('filtroSituacao', 'bloqueado', ['Rafael Andrade'])):
            clica('#%s .dropdown-select-btn' % dd); clica('#%s .dropdown-select-item[data-value="%s"]' % (dd, valor))
            ok(nomes_lista() == quem, 'filtro %s = %s: %s' % (dd, valor, quem))
            clica('#linkLimparFiltros')
        clica('#filtroPerfil .dropdown-select-btn'); clica('#filtroPerfil .dropdown-select-item[data-value="4"]'); clica('#filtroLoja .dropdown-select-btn'); clica('#filtroLoja .dropdown-select-item[data-value="1"]'); preenche('#campoBusca', 'bianca')
        ok(nomes_lista() == ['Bianca Furtado'], 'os filtros se combinam')
        clica('#btnLimparFiltros' if ev("document.getElementById('emptyState').style.display") == 'flex' else '#linkLimparFiltros')
        ok(len(nomes_lista()) == 7 and ev("document.getElementById('filtroPerfil').getAttribute('data-value')") == 'todos', '"limpar filtros" desfaz tudo')
        ok(ev("Array.from(document.querySelectorAll('#menuFiltroPerfil .dropdown-select-item')).map(i => i.textContent).join('|')") == 'Todos os perfis|Owner|Gerente|Supervisor de vendas|Vendedor interno|Caixa / vendedor de balcão|Representante externo', 'o filtro de perfil traz os perfis cadastrados')
        clica('.estoque-table th[data-ordem="nome"]')
        ok(nomes_lista()[0] == 'Rafael Andrade', 'clicar em "Usuário" inverte a ordem')
        clica('.estoque-table th[data-ordem="perfilNome"]')
        ok(nomes_lista()[0] == 'Administrador Desk' or ev("document.querySelector('#corpoTabela tr td:nth-child(3)').textContent") == 'Caixa / vendedor de balcão', 'ordena por perfil')
        # o painel
        ir(LU); clica('#corpoTabela tr[data-id="3"]')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')") and 'Marina Costa' in ev("document.getElementById('drawerCorpo').textContent"), 'clicar na linha abre o painel do usuário')
        pn = ev("document.getElementById('drawerCorpo').textContent.replace(/\\s+/g, ' ')")
        ok('18% (o dele)' in pn and 'Definido em 15/10/2026' in pn and '1 permissão a mais' in pn and 'Autoriza' in pn, 'o painel mostra o desconto próprio, o código "definido em", as permissões avulsas e quanto autoriza')
        ok(ev("Array.from(document.querySelectorAll('#drawerCorpo .drawer-footer > *')).map(e => e.textContent.trim())") == ['Abrir usuário', 'Alterar senha', 'Alterar código de autorização', 'Bloquear usuário', 'Fechar'], 'o painel tem abrir, alterar senha, alterar código e bloquear')
        clica('#btnAlterarSenha'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == DU + '?id=3&senha=1' and ev("document.getElementById('painelSenha').style.display") == '' and ev("document.getElementById('eventDrawer').classList.contains('open')"), '"Alterar senha" do painel abre a página já com o painel da senha')
        ir(LU); clica('#corpoTabela tr[data-id="3"]'); clica('#btnAlterarCodigo'); pg.wait_for_timeout(500)
        ok(ev("document.getElementById('painelCodigo').style.display") == '' and 'Alterar código' in ev("document.getElementById('drawerTitulo').textContent"), '"Alterar código de autorização" abre o painel do código')
        ir(LU); clica('#corpoTabela tr[data-id="5"]')
        ok('Não definido' in ev("document.getElementById('upCodigo').textContent") and 'Definir código de autorização' in ev("document.getElementById('btnAlterarCodigo').textContent"), 'quem não tem o código: "Não definido" e o botão diz "Definir"')
        pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
        ok(not ev("document.getElementById('eventDrawer').classList.contains('open')"), 'o Esc fecha o painel')
        ok(ev("document.querySelectorAll('.estoque-table-wrap').length") == 1 and ev("(() => { const w = document.querySelector('.estoque-table-wrap'); return w.scrollWidth <= w.clientWidth + 1; })()"), 'a tabela não tem barra para o lado em 1440')

    # ------------------------------------------------------------------------------------------------
    if secao(4, 'A página do usuário, nos dois modos'):
        limpo(DU, '?id=3')
        v = lambda i: ev("(id) => document.getElementById(id).value", i)
        ok(v('inputNome') == 'Marina Costa' and v('inputLogin') == 'marina.costa@desk' and v('inputEmail') == 'marina.costa@example.com' and v('inputEmailCom') == 'marina.costa@example.com', '?id=3 abre a Marina: nome, login, e-mail de acesso e e-mail para clientes')
        ok(ev("document.getElementById('tituloUsuario').textContent") == 'Marina Costa' and ev("document.getElementById('badgeTexto').textContent") == 'Ativo', 'o título e a situação')
        ok(ev("[1,2,3,4].map(l => document.getElementById('chkLoja' + l).checked)") == [True, True, False, False], 'as lojas em que ela trabalha')
        ok(ev("document.getElementById('inputVendedor').getAttribute('data-value')") == '1' and ev("document.getElementById('inputPerfil').getAttribute('data-value')") == '3', 'o vendedor vinculado e o perfil')
        ok(v('inputDesconto') == '18' and 'Definido em 15/10/2026' in ev("document.getElementById('codigoStatus').textContent") and 'alterada pela última vez em 15/10/2026' in ev("document.getElementById('senhaStatus').textContent"), 'o desconto próprio, o código "definido em" e a senha "alterada em"')
        ok(ev("document.getElementById('perfilResumo').textContent").startswith('Supervisor de vendas') and ev("document.querySelectorAll('#perfilChips .up-chip').length") >= 5, 'o perfil, o que ele dá em resumo e os módulos')
        ok(ev("document.getElementById('avulsasResumo').textContent").startswith('1 permissão a mais'), 'as permissões avulsas dela: 1 permissão a mais (a ação do preço promocional)')
        secoes = ev("Array.from(document.querySelectorAll('.up-card > .section-title')).map(t => t.textContent.trim())")
        ok(secoes == ['Acesso à conta', 'Perfil e permissões', 'Limites e autorização', 'Senha de acesso', 'Restrições de acesso'], 'as seções da página: %s' % secoes)
        ok(ev("document.getElementById('btnVoltarLista').textContent.trim()") == 'Voltar para Usuários do sistema' and ev("document.querySelector('.header-acoes').firstElementChild.id") == 'btnVoltarLista', 'o "Voltar" é o primeiro do cabeçalho')
        # nao mostra nada secreto
        pagina = ev("document.body.innerText")
        ok('fnv1a' not in pagina and 'Hash' not in pagina, 'a página nunca mostra o resumo guardado da senha nem do código')
        # ?novo=1 abre em branco
        limpo(DU, '?novo=1')
        ok(ev("document.getElementById('tituloUsuario').textContent") == 'Novo usuário' and v('inputNome') == '' and v('inputLogin') == '' and v('inputEmail') == '', '?novo=1 abre em branco, com o título "Novo usuário"')
        ok(ev("[1,2,3,4].every(l => !document.getElementById('chkLoja' + l).checked)") and ev("document.getElementById('inputPerfil').getAttribute('data-value')") == '', 'sem loja marcada e sem perfil escolhido')
        ok(ev("['btnSenha', 'btnCodigo', 'btnEditarAvulsas'].every(i => document.getElementById(i).disabled)"), 'a senha, o código e as permissões avulsas esperam o usuário existir')
        # validacoes
        clica('#btnSalvar')
        ok(ev("['campoNome', 'campoLogin', 'campoLojas', 'campoPerfil'].every(c => document.getElementById(c).classList.contains('has-error'))") and len(usuarios() or []) == 0, 'salvar em branco: avisa nome, login, loja e perfil, e não grava')
        preenche('#inputNome', 'Paulo Teste'); ev("document.getElementById('inputNome').dispatchEvent(new Event('blur'))")
        ok(v('inputLogin') == 'paulo.teste@desk', 'o login nasce do nome (paulo.teste@desk)')
        for ruim in ('paulo', 'paulo@gmail.com', 'Pa ulo@desk', 'marina.costa@desk'):
            preenche('#inputLogin', ruim); clica('#btnSalvar')
            ok(ev("document.getElementById('campoLogin').classList.contains('has-error')"), 'login "%s" não passa' % ruim)
        ok('Já existe' in ev("document.getElementById('erroLogin').textContent"), 'login repetido diz que já existe')
        preenche('#inputLogin', 'paulo.teste@desk'); preenche('#inputEmail', 'isto nao e email'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoEmail').classList.contains('has-error')"), 'e-mail mal escrito não passa')
        preenche('#inputEmail', 'paulo@example.com')
        clica('#chkLoja1'); clica('#chkLoja2'); clica('#inputPerfil .dropdown-select-btn'); clica('#menuPerfil .dropdown-select-item[data-value="4"]')
        ok('Vendedor interno' in ev("document.getElementById('perfilResumo').textContent") and 'desconto sem senha do perfil: 10%' in ev("document.getElementById('perfilResumo').textContent"), 'escolher o perfil mostra o que ele dá')
        clica('#inputVendedor .dropdown-select-btn'); clica('#menuVendedor .dropdown-select-item[data-value="1"]'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoVendedor').classList.contains('has-error')") and 'Marina Costa' in ev("document.getElementById('erroVendedor').textContent"), 'vendedor que já está ligado a outro usuário não passa')
        clica('#inputVendedor .dropdown-select-btn'); clica('#menuVendedor .dropdown-select-item[data-value=""]')
        preenche('#inputDesconto', '150'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoDesconto').classList.contains('has-error')"), 'desconto acima de 100 não passa')
        preenche('#inputDesconto', 'abc'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoDesconto').classList.contains('has-error')"), 'desconto com letra não passa')
        preenche('#inputDesconto', '')
        clica('#chkHorario')
        ok(ev("document.getElementById('blocoHorario').style.display") == '', 'restrição por horário mostra os dias e a faixa')
        clica('#btnSalvar')
        ok(ev("document.getElementById('erroHorario').classList.contains('show')"), 'horário sem dia e sem faixa não passa')
        clica('#chkDia1'); clica('#chkDia2'); preenche('#inputDe', '18:00'); preenche('#inputAte', '08:00'); clica('#btnSalvar')
        ok(ev("document.getElementById('erroHorario').classList.contains('show')"), 'a faixa com o início depois do fim não passa')
        preenche('#inputDe', '08:00'); preenche('#inputAte', '18:00')
        clica('#chkIp'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoIps').classList.contains('has-error')"), 'restrição por IP sem IP não passa')
        preenche('#inputIps', '999.1.1.1'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoIps').classList.contains('has-error')"), 'IP inválido não passa')
        preenche('#inputIps', '200.150.10.5, 200.150.10.6')
        ok(ev("document.querySelector('#conteudoUsuario').offsetParent !== null"), 'a página segue aberta enquanto há erro')
        clica('#btnSalvar'); pg.wait_for_timeout(500)
        ok(localiza.nome(pg.url) == DU + '?id=8&senha=1' and ev("document.getElementById('painelSenha').style.display") == '' and ev("document.getElementById('eventDrawer').classList.contains('open')"), 'incluir grava e abre a página do usuário novo já com o painel da senha')
        novo = [u for u in usuarios() if u['id'] == 8][0]
        ok(novo['nome'] == 'Paulo Teste' and novo['login'] == 'paulo.teste@desk' and novo['lojas'] == [1, 2] and novo['perfilId'] == 4 and novo['vendedorId'] is None and novo['descontoPct'] is None and novo['perms'] == [] and novo['situacao'] == 'ativo',
           'o usuário novo gravou como foi preenchido, sem permissão avulsa e sem desconto próprio: %s' % novo)
        ok(novo['horario'] == {'dias': [1, 2], 'de': '08:00', 'ate': '18:00'} and novo['ips'] == ['200.150.10.5', '200.150.10.6'], 'com o horário (dias e faixa) e os IPs')
        ok(novo['senhaHash'] is None and novo['codigoHash'] is None, 'nasce sem senha e sem código')
        ok(len(log('usuarioInclui')) == 1 and 'Paulo Teste' in log('usuarioInclui')[0]['detalhe'], 'incluir vai para o Registro de atividades')
        # abrir de novo: a restricao volta
        ir(DU, '?id=8')
        ok(ev("document.getElementById('chkHorario').checked && document.getElementById('chkIp').checked") and v('inputDe') == '08:00' and v('inputIps') == '200.150.10.5, 200.150.10.6' and ev("document.getElementById('chkDia1').checked && !document.getElementById('chkDia3').checked"),
           'reabrir mostra o horário e os IPs gravados')
        # alterar um usuario sem trocar o perfil nao pede senha e vai para o registro
        preenche('#inputEmailCom', 'vendas@example.com'); clica('#btnSalvar'); pg.wait_for_timeout(500)
        ok(not modal_aberto() and localiza.nome(pg.url) == LU + '?salvo=8', 'salvar sem trocar o perfil não pede senha e volta para a lista')
        ok([u for u in usuarios() if u['id'] == 8][0]['emailCom'] == 'vendas@example.com' and len(log('usuarioSalva')) == 1, 'gravou, e o registro de atividades diz que alterou o cadastro')
        ok('Paulo Teste foi salvo' in ev("document.getElementById('faixaFeito').textContent") and ev("document.querySelectorAll('#corpoTabela tr.up-destaque').length") == 1, 'a lista mostra o que aconteceu, com a linha marcada')
        ok(len(nomes_lista()) == 8, 'a lista passa a ter 8 usuários')
        # trocar o perfil de quem ja existe pede a senha
        ir(DU, '?id=8'); clica('#inputPerfil .dropdown-select-btn'); clica('#menuPerfil .dropdown-select-item[data-value="6"]'); clica('#btnSalvar')
        ok(modal_aberto() and 'Trocar o perfil de Paulo Teste de "Vendedor interno" para "Representante externo"' in ev("document.getElementById('confirmModalTexto').textContent") and ev("document.getElementById('campoSenhaModal').classList.contains('on')"),
           'trocar o perfil de quem já existe pede a senha (usuarioPermissoes), dizendo de qual perfil para qual')
        confirmar('')
        ok([u for u in usuarios() if u['id'] == 8][0]['perfilId'] == 4, 'senha vazia: o perfil não troca')
        confirmar('qualquer')
        ok([u for u in usuarios() if u['id'] == 8][0]['perfilId'] == 6 and len(log('usuarioPermissoes')) == 1 and log('usuarioPermissoes')[0]['senha'] is True, 'com a senha, troca e registra a ação usuarioPermissoes com senha')
        # a rodape de salvar conta o que mudou
        ir(DU, '?id=8')
        ok('Nenhuma alteração pendente' in ev("document.getElementById('infoPendente').textContent"), 'a nota do rodapé abre sem pendência')
        preenche('#inputNome', 'Paulo T.')
        ok('ainda não salvo' in ev("document.getElementById('infoPendente').textContent"), 'mexer num campo faz a nota contar')
        ok('Paulo T.' == ev("document.getElementById('tituloUsuario').textContent"), 'o título acompanha o nome')

    # ------------------------------------------------------------------------------------------------
    if secao(5, 'O código de autorização e a senha de acesso'):
        limpo(DU, '?id=5')
        ok('Não definido' in ev("document.getElementById('codigoStatus').textContent") and ev("document.getElementById('btnCodigo').textContent") == 'Definir código', 'a Bianca não tem código: "Não definido" e o botão diz "Definir código"')
        ok('não autoriza' in ev("document.getElementById('autorizaResumo').textContent") or 'não tem ações' in ev("document.getElementById('autorizaResumo').textContent"), 'a página explica o que o código faz (ou que o perfil não tem ações)')
        clica('#btnCodigo')
        ok(ev("document.getElementById('eventDrawer').classList.contains('open')") and ev("document.getElementById('painelCodigo').style.display") == '', 'o código abre num painel lateral')
        ok(ev("['inputCodigoNovo', 'inputCodigoConf'].every(i => document.getElementById(i).type === 'password')"), 'os campos do código são de senha: nunca mostram o valor')
        casos = [('123', '123', 'curto demais'), ('1234567', '1234567', 'comprido demais'), ('12ab', '12ab', 'com letras'), ('abcd', 'abcd', 'só letras'), ('12 34', '12 34', 'com espaço'), ('1234', '1235', 'confirmação diferente')]
        for novo, conf, motivo in casos:
            preenche('#inputCodigoNovo', novo); preenche('#inputCodigoConf', conf); clica('#btnConfirmarCodigo')
            ok(usuarios() is None or [u for u in usuarios() if u['id'] == 5][0]['codigoHash'] is None, 'o código "%s" (%s) não é aceito' % (novo, motivo))
            ok(ev("document.getElementById('campoCodigoNovo').classList.contains('has-error') || document.getElementById('campoCodigoConf').classList.contains('has-error')"), 'e a tela diz onde está o erro (%s)' % motivo)
        ok(ev("upCodigoValido('1234') && upCodigoValido('123456') && !upCodigoValido('123') && !upCodigoValido('1234567') && !upCodigoValido('12a4') && !upCodigoValido('ab12') && !upCodigoValido('')"), 'upCodigoValido: de 4 a 6 numeros, só números')
        preenche('#inputCodigoNovo', '739104'); preenche('#inputCodigoConf', '739104'); clica('#btnConfirmarCodigo'); pg.wait_for_timeout(200)
        b = [u for u in usuarios() if u['id'] == 5][0]
        ok(b['codigoHash'] and b['codigoEm'] and not ev("document.getElementById('eventDrawer').classList.contains('open')"), 'um código válido grava e fecha o painel')
        guardado = ev("localStorage.getItem('deskUsuarios')") + ev("localStorage.getItem('deskLog')")
        ok('739104' not in guardado, 'o código digitado não fica guardado em texto puro (nem no usuário, nem no registro)')
        ok('739104' not in ev("document.body.innerText") and ev("['inputCodigoNovo', 'inputCodigoConf'].every(i => document.getElementById(i).value === '')"), 'e some da tela: os campos esvaziam')
        ok('Definido em' in ev("document.getElementById('codigoStatus').textContent") and ev("document.getElementById('btnCodigo').textContent") == 'Alterar código', 'a tela diz só "definido em <data>" e o botão passa a dizer "Alterar código"')
        ok(len(log('usuarioCodigo')) == 1 and 'Definiu' in log('usuarioCodigo')[0]['detalhe'] and '739104' not in str(log('usuarioCodigo')), 'definir o código vai para o Registro de atividades, sem o valor')
        clica('#btnCodigo'); preenche('#inputCodigoNovo', '5678'); preenche('#inputCodigoConf', '5678'); clica('#btnConfirmarCodigo')
        ok(len(log('usuarioCodigo')) == 2 and 'Trocou' in log('usuarioCodigo')[0]['detalhe'] and [u for u in usuarios() if u['id'] == 5][0]['codigoHash'] != b['codigoHash'], 'trocar o código grava outro resumo e registra "Trocou"')
        # os resumos do codigo mudam o indicador da lista
        ir(LU)
        ok(ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"semCodigo\"] .kpi-value').textContent") == '1', 'a lista passa a ter 1 usuário sem código')
        # a senha de acesso
        ir(DU, '?id=5'); clica('#btnSenha')
        ok(ev("document.getElementById('painelSenha').style.display") == '' and 'Usuário: bianca.furtado@desk' in ev("document.getElementById('senhaUsuario').textContent"), 'a senha abre num painel lateral, com o usuário no topo')
        ok(ev("['inputSenhaNova', 'inputSenhaConf', 'inputSenhaAtual'].every(i => document.getElementById(i).type === 'password')") and 'e-mail' in ev("document.getElementById('painelSenha').textContent"), 'senha nova, confirmação e "minha senha atual" são de senha, e o código por e-mail entra só como aviso')
        for nova, conf, atual, motivo in (('curta', 'curta', 'x', 'curta'), ('a' * 33, 'a' * 33, 'x', 'comprida demais'), ('umasenhaboa123', 'outradiferente1', 'x', 'confirmação diferente'), ('umasenhaboa123', 'umasenhaboa123', '', 'sem a senha atual')):
            preenche('#inputSenhaNova', nova); preenche('#inputSenhaConf', conf); preenche('#inputSenhaAtual', atual); clica('#btnConfirmarSenha')
            ok(not log('usuarioSenha'), 'a senha %s não é aceita' % motivo)
        preenche('#inputSenhaNova', 'umasenhaboa123'); preenche('#inputSenhaConf', 'umasenhaboa123'); preenche('#inputSenhaAtual', 'minhasenha'); clica('#btnConfirmarSenha'); pg.wait_for_timeout(200)
        ok(len(log('usuarioSenha')) == 1 and log('usuarioSenha')[0]['senha'] is True, 'senha de 12 a 32 caracteres, confirmada e com a senha atual: grava e registra com senha')
        guardado = ev("localStorage.getItem('deskUsuarios')") + ev("localStorage.getItem('deskLog')")
        ok('umasenhaboa123' not in guardado and 'minhasenha' not in guardado, 'nenhuma das senhas fica guardada em texto puro')
        ok(ev("['inputSenhaNova', 'inputSenhaConf', 'inputSenhaAtual'].every(i => document.getElementById(i).value === '')") and 'alterada pela última vez em' in ev("document.getElementById('senhaStatus').textContent"), 'os campos esvaziam e a tela diz quando foi alterada')
        ok(ev("document.querySelector('#painelSenha .up-olho').click(), document.getElementById('inputSenhaNova').type") == 'text', 'o olhinho mostra e esconde o que a pessoa digita')

    # ------------------------------------------------------------------------------------------------
    if secao(6, 'O desconto sem senha: o próprio vale no lugar do perfil'):
        limpo(LU)
        d = ev("(() => { const ps = lerPerfis(), us = lerUsuarios(); const f = n => us.filter(u => u.nome === n)[0]; const de = n => upDesconto(f(n), ps.filter(p => p.id === f(n).perfilId)[0]); return [de('Marina Costa'), de('Ana Souza'), de('Administrador Desk'), de('Carlos Mendes')]; })()")
        ok(d == [{'pct': 18, 'origem': 'proprio'}, {'pct': 10, 'origem': 'perfil'}, {'pct': None, 'origem': 'semLimite'}, {'pct': 20, 'origem': 'perfil'}],
           'o próprio da Marina (18%%) vale no lugar do perfil (15%%); a Ana fica com o do perfil (10%%); o Owner não tem limite; o Gerente 20%%: %s' % d)
        ok(ev("upDesconto({ descontoPct: 5 }, { id: 3, descontoPct: 15 }).pct") == 5 and ev("upDesconto({ descontoPct: 0 }, { id: 3, descontoPct: 15 }).pct") == 0, 'um limite próprio menor ou zero também vale no lugar do perfil')
        ok(ev("upDesconto({ descontoPct: 50 }, { id: 1, descontoPct: null }).origem") == 'semLimite', 'o Owner continua sem limite mesmo com um valor próprio gravado')
        # na pagina: vazio = o do perfil, e o valor aparece
        ir(DU, '?id=4')
        ok(ev("document.getElementById('inputDesconto').value") == '' and 'Vazio = o do perfil (10%)' in ev("document.getElementById('hintDesconto').textContent"), 'o campo vazio diz que vale o do perfil e mostra o valor (10%)')
        preenche('#inputDesconto', '12,5'); clica('#btnSalvar'); pg.wait_for_timeout(500)
        ok([u for u in usuarios() if u['id'] == 4][0]['descontoPct'] == 12.5, 'o desconto próprio de 12,5% grava')
        ir(LU)
        ok('12,5%' in ev("Array.from(document.querySelectorAll('#corpoTabela tr')).filter(t => t.textContent.includes('Ana Souza'))[0].children[5].textContent"), 'a lista mostra o desconto próprio dela (12,5%), e não o do perfil')
        ir(DU, '?id=4'); preenche('#inputDesconto', ''); clica('#btnSalvar'); pg.wait_for_timeout(500)
        ok([u for u in usuarios() if u['id'] == 4][0]['descontoPct'] is None, 'apagar o campo devolve o desconto do perfil')
        ir(DU, '?id=4'); clica('#inputPerfil .dropdown-select-btn'); clica('#menuPerfil .dropdown-select-item[data-value="2"]')
        ok('(20%)' in ev("document.getElementById('hintDesconto').textContent"), 'trocar o perfil na tela atualiza o valor do perfil (20%)')
        ir(DU, '?id=1')
        ok(ev("document.getElementById('inputDesconto').disabled") and 'não tem limite' in ev("document.getElementById('hintDesconto').textContent") and ev("document.getElementById('btnEditarAvulsas').disabled"), 'o Owner não tem limite e não tem o que acrescentar')

    # ------------------------------------------------------------------------------------------------
    if secao(7, 'A grade e a página do perfil'):
        limpo(DP, '?id=2')
        ok(ev("document.getElementById('inputNome').value") == 'Gerente' and ev("document.getElementById('inputDesconto').value") == '20' and ev("document.getElementById('inputDescricao').value").startswith('Vende em todas as lojas'), 'o Gerente abre com nome, descrição e desconto padrão (20%)')
        abas = ev("Array.from(document.querySelectorAll('#gradePerfil .aba-sit > span:first-child')).map(a => a.textContent)")
        ok(abas == ['Início', 'Cadastros', 'Estoque', 'Vendas', 'Logística', 'Finanças', 'Integrações', 'Configurações'], 'as abas da grade são os módulos do nosso menu')
        ok(ev("document.querySelectorAll('#gradePerfil .pg-todos').length") == 8 and 'Marcar todos' in ev("document.querySelector('#gradePerfil .pg-todos').textContent"), 'cada aba tem o "Marcar todos"')
        ok(ev("document.querySelector('.pg-corpo[data-painel=\"inicio\"]').style.display") == '' and ev("document.querySelector('.pg-corpo[data-painel=\"estoque\"]').style.display") == 'none', 'só a aba aberta aparece')
        abrir_aba('cadastros')
        linhas = ev("Array.from(document.querySelectorAll('.pg-corpo[data-painel=\"cadastros\"] .pg-linha')).slice(0, 8).map(l => [l.classList.contains('pg-filho'), l.querySelector('label').textContent])")
        ok(linhas[0] == [False, 'Clientes'] and linhas[1] == [True, 'Incluir cliente'], 'a tela é o item e as funções dela vêm por dentro, recuadas')
        ok(ev("Array.from(document.querySelectorAll('.pg-corpo[data-painel=\"cadastros\"] .pg-secao-titulo')).map(t => t.textContent)") == ['Permissões de ações'], 'no fim da aba: "Permissões de ações"')
        ok(ev("document.querySelectorAll('.pg-corpo[data-painel=\"cadastros\"] .pg-grupo').length") >= 3, 'as ações vêm agrupadas pela tela de origem')
        # a hierarquia
        limpo(DP, '?novo=1')
        ok(ev("document.getElementById('tituloPerfil').textContent") == 'Novo perfil' and ev("document.getElementById('inputNome').value") == '' and ev("document.querySelectorAll('#gradePerfil .pg-chk:checked').length") == 0, '?novo=1 abre em branco, sem nada marcado')
        ok(ev("document.getElementById('cartaoQuem').style.display") == 'none', 'perfil novo não mostra "quem tem este perfil"')
        abrir_aba('cadastros'); marcar_grade('clientes.incluir')
        ok(ev("document.querySelector('.pg-chk[data-chave=\"clientes\"]').checked") and ev("document.querySelector('.pg-chk[data-chave=\"clientes.incluir\"]').checked"), 'marcar uma função marca a tela')
        marcar_grade('clientes.alterar'); marcar_grade('clientes', False)
        ok(not ev("document.querySelector('.pg-chk[data-chave=\"clientes.incluir\"]').checked") and not ev("document.querySelector('.pg-chk[data-chave=\"clientes.alterar\"]').checked"), 'desmarcar a tela desmarca as funções dela (só valem com a tela marcada)')
        ok(ev("permNormalizar(new Set(['clientes.incluir'])).size") == 0 and ev("permNormalizar(new Set(['clientes.incluir', 'clientes'])).size") == 2, 'permNormalizar tira a função que não tem a tela')
        # marcar todos
        clica('.pg-todos[data-aba="cadastros"]')
        n_cad = len(ev("permChavesDoModulo('cadastros')"))
        ok(ev("document.querySelectorAll('.pg-corpo[data-painel=\"cadastros\"] .pg-chk:checked').length") == n_cad and ev("document.querySelector('.pg-todos[data-aba=\"cadastros\"] .switch').classList.contains('on')"), '"Marcar todos" marca tudo da aba (%d chaves) e acende' % n_cad)
        ok(ev("document.querySelectorAll('.pg-corpo[data-painel=\"vendas\"] .pg-chk:checked').length") == 0, 'e só dela')
        ok(ev("document.querySelector('.aba-sit[data-aba=\"cadastros\"] .sit-contador').textContent") == str(n_cad), 'o contador da aba conta o que está marcado')
        clica('.pg-todos[data-aba="cadastros"]')
        ok(ev("document.querySelectorAll('.pg-corpo[data-painel=\"cadastros\"] .pg-chk:checked').length") == 0, 'clicar de novo desmarca a aba inteira')
        ok('0 telas' in ev("document.getElementById('subtituloPerfil').textContent") or ev("document.getElementById('subtituloPerfil').textContent").startswith('0 telas'), 'o subtítulo conta as telas, as funções e as ações marcadas')
        abrir_aba('vendas'); acoes_v = ev("Array.from(document.querySelectorAll('.pg-corpo[data-painel=\"vendas\"] .pg-chk')).filter(c => c.getAttribute('data-chave').charAt(0) === '@').map(c => c.getAttribute('data-chave'))")
        ok('@promocaoAprova' in acoes_v and '@pdvDescontoAcima' in acoes_v and '@perfilPermissoes' not in acoes_v, 'as ações de autorização de Vendas ficam na aba de Vendas (%d)' % len(acoes_v))
        abrir_aba('configuracoes')
        ok(ev("Array.from(document.querySelectorAll('.pg-corpo[data-painel=\"configuracoes\"] .pg-chk')).some(c => c.getAttribute('data-chave') === '@perfilPermissoes') && Array.from(document.querySelectorAll('.pg-corpo[data-painel=\"configuracoes\"] .pg-chk')).some(c => c.getAttribute('data-chave') === '@usuarioPermissoes')"), 'as duas ações novas ficam na aba de Configurações')
        ok('Só quem está no sistema com o perfil Owner' in ev("document.querySelector('.pg-corpo[data-painel=\"configuracoes\"]').textContent"), 'Usuários e Permissões dizem na grade que só o Owner altera')
        # a nota do rodape nao se confunde ao trocar de aba
        ir(DP, '?id=2')
        ok('Nenhuma alteração pendente' in ev("document.getElementById('infoPendente').textContent"), 'o perfil abre sem pendência')
        abrir_aba('estoque'); abrir_aba('vendas')
        ok('Nenhuma alteração pendente' in ev("document.getElementById('infoPendente').textContent"), 'trocar de aba não conta como alteração')
        # salvar o nome ou o desconto: sem senha
        preenche('#inputNome', 'Gerente geral'); preenche('#inputDesconto', '25'); clica('#btnSalvar'); pg.wait_for_timeout(500)
        ok(not modal_aberto() and localiza.nome(pg.url) == LP + '?salvo=2', 'mudar só o nome e o desconto não pede senha e volta para a lista')
        g = [x for x in perfis() if x['id'] == 2][0]
        ok(g['nome'] == 'Gerente geral' and g['descontoPct'] == 25 and len(log('perfilSalva')) == 1 and not log('perfilPermissoes'), 'gravou, registrou a alteração e não registrou permissão')
        ok(set(ev("Array.from(permExpandir(lerPerfis().filter(p => p.id === 2)[0].perms))")) == set(ev("Array.from(permExpandir(UP_PERFIS_FABRICA[1].perms))")), 'as permissões continuam as mesmas (os atalhos de fábrica viraram chaves explícitas)')
        # mudar a grade: pede a senha (perfilPermissoes)
        ir(DP, '?id=2'); abrir_aba('financas'); marcar_grade('caixa.fecharPeriodo', False); preenche('#inputDescricao', 'Descrição nova'); clica('#btnSalvar')
        ok(modal_aberto() and ev("document.getElementById('campoSenhaModal').classList.contains('on')") and 'Alterar as permissões do perfil "Gerente geral"' in ev("document.getElementById('confirmModalTexto').textContent"), 'mudar a grade do perfil pede a senha (perfilPermissoes)')
        confirmar('')
        ok(modal_aberto() and [x for x in perfis() if x['id'] == 2][0]['descricao'] != 'Descrição nova', 'sem a senha não grava')
        confirmar('minha')
        pg.wait_for_timeout(300)
        g = [x for x in perfis() if x['id'] == 2][0]
        ok(g['descricao'] == 'Descrição nova' and 'caixa.fecharPeriodo' not in g['perms'] and 'caixa' in g['perms'] and len(log('perfilPermissoes')) == 1 and log('perfilPermissoes')[0]['senha'] is True, 'com a senha grava a grade nova e registra a ação perfilPermissoes, com senha')
        ok(localiza.nome(pg.url) == LP + '?salvo=2', 'e volta para a lista')
        # as validacoes
        ir(DP, '?id=2'); preenche('#inputNome', ''); clica('#btnSalvar')
        ok(ev("document.getElementById('campoNome').classList.contains('has-error')"), 'perfil sem nome não grava')
        preenche('#inputNome', 'owner'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoNome').classList.contains('has-error')") and 'Já existe' in ev("document.getElementById('erroNome').textContent"), 'nome repetido (sem olhar maiúsculas) não grava')
        preenche('#inputNome', 'Gerente geral'); preenche('#inputDesconto', '101'); clica('#btnSalvar')
        ok(ev("document.getElementById('campoDesconto').classList.contains('has-error')"), 'desconto acima de 100 não grava')
        preenche('#inputDesconto', ''); clica('#btnSalvar')
        ok(ev("document.getElementById('campoDesconto').classList.contains('has-error')"), 'desconto em branco não grava (o perfil sempre tem um padrão)')
        # perfil novo
        limpo(DP, '?novo=1')
        preenche('#inputNome', 'Financeiro'); preenche('#inputDescricao', 'Contas a pagar e a receber'); preenche('#inputDesconto', '0')
        abrir_aba('financas'); marcar_grade('contasPagar.pagar'); marcar_grade('contasReceber')
        clica('#btnSalvar')
        ok(modal_aberto(), 'perfil novo com permissões também pede a senha')
        confirmar('x'); pg.wait_for_timeout(300)
        novo = [x for x in perfis() if x['nome'] == 'Financeiro'][0]
        ok(novo['id'] == 7 and sorted(novo['perms']) == ['contasPagar', 'contasPagar.pagar', 'contasReceber'] and novo['descontoPct'] == 0, 'o perfil novo gravou com as chaves da grade e o desconto 0: %s' % novo['perms'])
        ok(localiza.nome(pg.url) == LP + '?salvo=7&novo=1' and len(log('perfilInclui')) == 1, 'volta para a lista e o registro diz que incluiu')
        ok('Perfil "Financeiro" criado' in ev("document.getElementById('faixaFeito').textContent"), 'a lista mostra o perfil criado')
        # o Owner abre so para ver
        ir(DP, '?id=1')
        ok(ev("document.getElementById('avisoOwner').style.display") == '' and 'não se edita nem se exclui' in ev("document.getElementById('avisoOwner').textContent"), 'o Owner mostra o aviso de por que não se edita')
        ok(ev("Array.from(document.querySelectorAll('#gradePerfil .pg-chk')).every(c => c.checked && c.disabled)"), 'o Owner tem tudo marcado e travado na grade')
        ok(ev("['inputNome', 'inputDescricao', 'inputDesconto'].every(i => document.getElementById(i).disabled)") and ev("document.getElementById('barraSalvar').style.display") == 'none', 'os campos do Owner são só para ver e não há "Salvar"')
        ok(ev("document.getElementById('inputDesconto').value") == 'Sem limite', 'o desconto do Owner diz "Sem limite"')
        clica('.pg-todos[data-aba="cadastros"]')
        ok(ev("Array.from(document.querySelectorAll('#gradePerfil .pg-chk')).every(c => c.checked)"), '"Marcar todos" não destrava nem desmarca o Owner')
        # mesmo que alguem grave outra coisa para o Owner, ele volta de fabrica
        ev("localStorage.setItem('deskPerfis', JSON.stringify([{ id: 1, nome: 'Owner', descricao: 'x', descontoPct: 5, fixo: false, perms: ['clientes'] }]))")
        ir(DP, '?id=1')
        ok(ev("lerPerfis()[0].perms.join()") == '*' and ev("lerPerfis()[0].descontoPct") is None and ev("lerPerfis()[0].fixo") is True and ev("document.querySelectorAll('#gradePerfil .pg-chk:checked').length") == ev("document.querySelectorAll('#gradePerfil .pg-chk').length"),
           'o que estiver gravado para o Owner é ignorado: ele volta sempre com tudo marcado, sem limite e fixo')

    # ------------------------------------------------------------------------------------------------
    if secao(8, 'As permissões avulsas só acrescentam'):
        limpo(DU, '?id=4')
        ok(ev("document.getElementById('avulsasResumo').textContent").startswith('Nenhuma') and not ev("document.getElementById('btnEditarAvulsas').disabled"), 'a Ana não tem permissão avulsa e pode editar')
        clica('#btnEditarAvulsas')
        ok(ev("document.getElementById('eventDrawer').classList.contains('pg-largo') && document.getElementById('painelAvulsas').style.display === ''") and ev("document.querySelectorAll('#gradeAvulsas .aba-sit').length") == 8, 'o painel lateral abre largo, com a mesma grade')
        travadas = ev("Array.from(document.querySelectorAll('#gradeAvulsas .pg-chk')).filter(c => c.disabled).map(c => c.getAttribute('data-chave'))")
        do_perfil = ev("Array.from(permExpandir(lerPerfis().filter(p => p.nome === 'Vendedor interno')[0].perms))")
        ok(sorted(travadas) == sorted(do_perfil) and ev("Array.from(document.querySelectorAll('#gradeAvulsas .pg-chk')).filter(c => c.disabled).every(c => c.checked)") and len(travadas) > 10,
           'o que o perfil já dá aparece marcado e travado (%d chaves)' % len(travadas))
        ok('do perfil' in ev("document.getElementById('gradeAvulsas').textContent"), 'e diz "do perfil"')
        abrir_aba('estoque'); marcar_grade('controleEstoques.exportar')
        ok(ev("document.querySelector('#gradeAvulsas .pg-chk[data-chave=\"controleEstoques\"]').checked"), 'marcar a função avulsa marca a tela dela')
        abrir_aba('vendas'); marcar_grade('@pdvDescontoAcima')
        # nao da para tirar o que o perfil da
        ev("document.querySelector('#gradeAvulsas .pg-chk[data-chave=\"pedidos\"]').click()"); pg.wait_for_timeout(100)
        ok(ev("document.querySelector('#gradeAvulsas .pg-chk[data-chave=\"pedidos\"]').checked"), 'não dá para tirar o que o perfil dá: as avulsas só acrescentam')
        abrir_aba('inicio'); clica('#gradeAvulsas .pg-todos[data-aba="inicio"]')
        ok(ev("Array.from(document.querySelectorAll('#gradeAvulsas .pg-corpo[data-painel=\"inicio\"] .pg-chk')).every(c => c.checked)"), '"Marcar todos" marca o que falta, sem mexer no que o perfil dá')
        clica('#btnSalvarAvulsas')
        ok(modal_aberto() and 'Alterar as permissões avulsas de Ana Souza' in ev("document.getElementById('confirmModalTexto').textContent") and ev("document.getElementById('campoSenhaModal').classList.contains('on')"), 'salvar as avulsas pede a senha (usuarioPermissoes)')
        ok([u for u in usuarios() or [] if u['id'] == 4] == [] or [u for u in usuarios() if u['id'] == 4][0]['perms'] == [], 'antes da senha nada grava')
        confirmar('ok'); pg.wait_for_timeout(200)
        ana = [u for u in usuarios() if u['id'] == 4][0]
        ok(set(ana['perms']) >= {'controleEstoques', 'controleEstoques.exportar', '@pdvDescontoAcima'} and not (set(ana['perms']) & set(do_perfil)), 'gravou só o que o perfil não dá: %s' % sorted(ana['perms'])[:6])
        ok(len(log('usuarioPermissoes')) == 1 and log('usuarioPermissoes')[0]['senha'] is True, 'e registrou a ação com senha')
        ok(not ev("document.getElementById('eventDrawer').classList.contains('open')") and re.match(r'^\d+ permissões a mais', ev("document.getElementById('avulsasResumo').textContent")) is not None, 'o painel fecha e a página resume as permissões a mais')
        # o efetivo: perfil + avulsas
        ef = ev("(() => { const u = lerUsuarios().filter(x => x.id === 4)[0], p = lerPerfis().filter(x => x.id === u.perfilId)[0]; const e = permEfetivas(p, u), so = permExpandir(p.perms); return [e.has('pedidos'), e.has('controleEstoques.exportar'), e.has('@pdvDescontoAcima'), so.has('controleEstoques'), so.size < e.size]; })()")
        ok(ef == [True, True, True, False, True], 'o efetivo é o perfil mais as avulsas, e o perfil em si não mudou: %s' % ef)
        ok(ev("(() => { const p = lerPerfis().filter(x => x.nome === 'Vendedor interno')[0]; return JSON.stringify(p.perms) === JSON.stringify(UP_PERFIS_FABRICA[3].perms); })()"), 'as avulsas de uma pessoa não mexem no perfil dos outros')
        # a Ana passa a autorizar: tem acao, tem codigo
        ir(LU)
        ok('Ana Souza' in (ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"autorizam\"]').click(), Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())")), 'com uma ação de autorização avulsa e o código, a Ana passa a contar em "Autorizam"')
        # sem mudar nada, nao pede senha
        ir(DU, '?id=4'); clica('#btnEditarAvulsas'); clica('#btnSalvarAvulsas')
        ok(not modal_aberto() and len(log('usuarioPermissoes')) == 1, 'salvar sem mudar nada não pede senha nem registra')
        ir(DU, '?id=4'); clica('#btnEditarAvulsas'); abrir_aba('estoque'); marcar_grade('controleEstoques', False)
        ok(not ev("document.querySelector('#gradeAvulsas .pg-chk[data-chave=\"controleEstoques.exportar\"]').checked"), 'tirar a tela avulsa tira as funções avulsas dela')
        clica('#btnSalvarAvulsas'); confirmar('x'); pg.wait_for_timeout(200)
        ok('controleEstoques' not in [u for u in usuarios() if u['id'] == 4][0]['perms'], 'e grava a retirada')
        # o perfil trocado: o que o novo perfil dá nao fica duplicado nas avulsas
        ir(DU, '?id=1')
        ok(ev("document.getElementById('btnEditarAvulsas').disabled"), 'o Owner não tem o que acrescentar')

    # ------------------------------------------------------------------------------------------------
    if secao(9, 'A lista de perfis: excluir só perfil sem usuário, clonar, o Owner'):
        limpo(LP)
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())") == ['Owner', 'Gerente', 'Supervisor de vendas', 'Vendedor interno', 'Caixa / vendedor de balcão', 'Representante externo'], 'abre com os seis perfis de partida')
        ok(ev("Array.from(document.querySelectorAll('.estoque-table thead th')).map(t => t.textContent.replace(/[▲▼]/g, '').trim())") == ['Perfil', 'Descrição', 'Usuários', 'Desconto padrão', 'Permissões', 'Ações de autorização'], 'colunas: nome, descrição, usuários, desconto padrão, permissões e ações de autorização')
        linhas = ev("Array.from(document.querySelectorAll('#corpoTabela tr')).map(tr => Array.from(tr.children).map(c => c.textContent.replace(/\\s+/g, ' ').trim()))")
        ok(linhas[1][2] == '1' and linhas[1][3] == '20%' and linhas[0][3] == 'Sem limite' and 'não se edita' in linhas[0][0], 'usuários, desconto padrão (Gerente 20%%, Owner sem limite) e a marca do Owner: %s' % linhas[1])
        ok(re.match(r'^\d+ telas · \d+ funções$', linhas[1][4]) is not None and int(linhas[1][5]) > 30 and linhas[2][5] == '0', 'as permissões e as ações de autorização de cada perfil (o Gerente tem, o Supervisor não)')
        kp = ev("Array.from(document.querySelectorAll('#indicadoresPerfis .kpi-card')).map(c => [c.querySelector('.kpi-label').textContent.trim(), c.querySelector('.kpi-value').textContent.trim()])")
        ok(kp == [['Perfis', '6'], ['Usuários com perfil', '7'], ['Perfis sem usuário', '0']], 'indicadores: perfis, usuários com perfil, perfis sem usuário: %s' % kp)
        # a lista de perfis nao tem perfil sem usuario ainda: o Financeiro nasce sem
        ir(DP, '?novo=1'); preenche('#inputNome', 'Separador'); preenche('#inputDesconto', '5'); abrir_aba('logistica'); marcar_grade('separacao.separar'); clica('#btnSalvar'); confirmar('x'); pg.wait_for_timeout(300)
        ir(LP)
        ok(ev("document.querySelector('#indicadoresPerfis [data-kpi=\"semUsuario\"] .kpi-value').textContent") == '1', 'o perfil novo, sem ninguém, entra em "Perfis sem usuário"')
        ok(ev("document.querySelector('#indicadoresPerfis [data-kpi=\"semUsuario\"]').click(), Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())") == ['Separador'], 'o indicador filtra só os perfis sem usuário')
        clica('#indicadoresPerfis [data-kpi="comUsuarios"]')
        ok(len(ev("Array.from(document.querySelectorAll('#corpoTabela tr'))")) == 6, 'e o dos perfis com usuário deixa os seis que alguém usa')
        clica('#indicadoresPerfis [data-kpi="comUsuarios"]'); preenche('#campoBusca', 'separ')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())") == ['Separador'], 'a busca acha o perfil pelo nome')
        preenche('#campoBusca', 'dono do sistema')
        ok(ev("Array.from(document.querySelectorAll('#corpoTabela tr .up-nome')).map(e => e.textContent.trim())") == ['Owner'], 'e pela descrição')
        preenche('#campoBusca', '')
        # o painel: o Owner
        clica('#corpoTabela tr[data-id="1"]')
        ok(ev("Array.from(document.querySelectorAll('#drawerCorpo .drawer-footer > *')).map(e => e.textContent.trim())") == ['Ver perfil', 'Clonar perfil', 'Fechar'], 'o painel do Owner: ver e clonar, sem excluir')
        ok(not ev("document.getElementById('btnExcluirPerfil')"), 'o Owner não tem o botão de excluir')
        ok('Sem limite' in ev("document.getElementById('pfDesconto').textContent") and 'Administrador Desk' in ev("document.getElementById('pfQuem').textContent"), 'o painel mostra o desconto, a contagem e quem tem o perfil')
        # excluir com usuario: bloqueado
        clica('#btnFecharPreview'); clica('#corpoTabela tr[data-id="3"]')
        ok(ev("document.getElementById('btnExcluirPerfil').disabled") and 'Só se exclui perfil sem usuário' in ev("document.getElementById('drawerCorpo').textContent"), 'perfil com usuário: o botão de excluir fica apagado e diz por quê')
        ev("document.getElementById('btnExcluirPerfil').click()")
        ok(not modal_aberto() and len(perfis() or []) >= 1 and 'Supervisor de vendas' in ev("JSON.stringify(lerPerfis())"), 'e clicar nele não exclui')
        ev("excluir(PERFIS.filter(p => p.id === 3)[0])"); pg.wait_for_timeout(200)
        ok(ev("document.getElementById('confirmModalTexto').textContent").startswith('Só se exclui perfil sem usuário') and 'Supervisor de vendas' in ev("JSON.stringify(lerPerfis())"), 'mesmo pela função, perfil com usuário não se exclui')
        confirmar()
        ev("excluir(PERFIS.filter(p => p.id === 1)[0])"); pg.wait_for_timeout(200)
        ok(not modal_aberto() and ev("lerPerfis()[0].nome") == 'Owner', 'o Owner nunca se exclui, nem pela função')
        # excluir o perfil sem usuario
        ir(LP); clica('#corpoTabela tr[data-id="%d"]' % [x for x in perfis() if x['nome'] == 'Separador'][0]['id']); clica('#btnExcluirPerfil')
        ok(modal_aberto() and 'Excluir o perfil "Separador"' in ev("document.getElementById('confirmModalTexto').textContent"), 'perfil sem usuário: pede a confirmação')
        confirmar(); pg.wait_for_timeout(300)
        ok('Separador' not in str(perfis()) and 'Perfil "Separador" excluído' in ev("document.getElementById('faixaFeito').textContent") and len(log('perfilExclui')) == 1, 'excluiu, a lista diz e o registro de atividades guarda')
        ok(ev("document.querySelector('#indicadoresPerfis [data-kpi=\"perfis\"] .kpi-value').textContent") == '6', 'a lista volta a ter os 6 perfis')
        # clonar
        ir(LP); clica('#corpoTabela tr[data-id="2"]'); clica('#btnClonarPerfil')
        ok(modal_aberto() and 'Clonar o perfil "Gerente"' in ev("document.getElementById('confirmModalTexto').textContent"), 'clonar pergunta antes')
        confirmar(); pg.wait_for_timeout(300)
        c = [x for x in perfis() if x['nome'] == 'Gerente (cópia)'][0]
        orig = ev("Array.from(permExpandir(lerPerfis().filter(p => p.id === 2)[0].perms)).sort()")
        ok(sorted(c['perms']) == orig and c['descontoPct'] == 20, 'a cópia leva as mesmas permissões e o mesmo desconto, como perfil novo (id %s)' % c['id'])
        ok(c['id'] not in (1, 2) and 'criado a partir de "Gerente"' in ev("document.getElementById('faixaFeito').textContent") and len(log('perfilClona')) == 1, 'com id próprio, a lista diz de onde veio e o registro guarda')
        ok(ev("document.querySelectorAll('#corpoTabela tr.up-destaque').length") == 1 and ev("document.querySelector('#corpoTabela tr.up-destaque .up-nome').textContent") == 'Gerente (cópia)', 'a cópia fica marcada na lista')
        clica('#corpoTabela tr[data-id="%d"]' % c['id']); clica('#btnClonarPerfil'); confirmar(); pg.wait_for_timeout(300)
        ok(len([x for x in perfis() if x['nome'].startswith('Gerente (cópia')]) == 2 and any(x['nome'] == 'Gerente (cópia) (cópia)' for x in perfis()), 'clonar a cópia gera outro nome, sem repetir')
        clica('#corpoTabela tr[data-id="1"]'); clica('#btnClonarPerfil'); confirmar(); pg.wait_for_timeout(300)
        o = [x for x in perfis() if x['nome'] == 'Owner (cópia)'][0]
        ok(o['fixo'] is False and o['descontoPct'] is None and len(o['perms']) == ev("permTodasChaves().length"), 'clonar o Owner dá um perfil comum e editável, com tudo marcado')
        ir(DP, '?id=%d' % o['id'])
        ok(not ev("document.getElementById('inputNome').disabled") and ev("document.getElementById('barraSalvar').style.display") != 'none', 'a cópia do Owner abre para editar')
        # a pagina do perfil: quem tem
        ir(DP, '?id=3')
        ok('Marina Costa' in ev("document.getElementById('listaQuem').textContent"), 'a página do perfil lista quem tem o perfil')

    # ------------------------------------------------------------------------------------------------
    if secao(10, 'Bloquear e ativar, quem pode mexer e o Registro de atividades'):
        limpo(LU)
        clica('#corpoTabela tr[data-id="4"]'); clica('#btnBloquear')
        ok(modal_aberto() and 'Bloquear Ana Souza' in ev("document.getElementById('confirmModalTexto').textContent"), 'bloquear pergunta antes')
        confirmar(); pg.wait_for_timeout(300)
        ok([u for u in usuarios() if u['id'] == 4][0]['situacao'] == 'bloqueado' and 'foi bloqueado' in ev("document.getElementById('faixaFeito').textContent"), 'bloqueou e a lista diz')
        ok(len(log('usuarioBloqueia')) == 1 and log('usuarioBloqueia')[0]['modulo'] == 'Configurações' and log('usuarioBloqueia')[0]['onde'] == 'Configurações → Usuários do sistema', 'o registro de atividades guarda o bloqueio')
        ok(ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"bloqueados\"] .kpi-value').textContent") == '2' and ev("document.querySelector('#indicadoresUsuarios [data-kpi=\"ativos\"] .kpi-value').textContent") == '5', 'os indicadores acompanham: 2 bloqueados, 5 ativos')
        ok(ev("(() => { const ps = lerPerfis(), u = lerUsuarios().filter(x => x.id === 4)[0]; return [u.codigoHash, ps.filter(p => p.id === u.perfilId).length]; })()")[0] is not None, 'bloquear guarda o cadastro e o código')
        clica('#corpoTabela tr[data-id="4"]')
        ok(ev("document.getElementById('btnBloquear').textContent") == 'Ativar usuário', 'o botão passa a dizer "Ativar usuário"')
        clica('#btnBloquear'); confirmar(); pg.wait_for_timeout(300)
        ok([u for u in usuarios() if u['id'] == 4][0]['situacao'] == 'ativo' and len(log('usuarioAtiva')) == 1, 'ativar devolve o acesso e registra')
        clica('#corpoTabela tr[data-id="1"]'); clica('#btnBloquear'); pg.wait_for_timeout(200)
        ok(ev("document.getElementById('confirmModalTexto').textContent").startswith('Você não pode bloquear a si mesmo') and [u for u in usuarios() if u['id'] == 1][0]['situacao'] == 'ativo', 'ninguém bloqueia a si mesmo')
        confirmar()
        # quem nao e Owner so ve
        ev("USUARIO_SESSAO.perfil = 'Gerente'")
        clica('#corpoTabela tr[data-id="3"]')
        ok(ev("Array.from(document.querySelectorAll('#drawerCorpo .drawer-footer > *')).map(e => e.textContent.trim())") == ['Abrir usuário', 'Fechar'] and 'Só quem está no sistema com o perfil Owner' in ev("document.getElementById('drawerCorpo').textContent"),
           'sem o perfil Owner o painel só abre o usuário, e diz que só o Owner altera')
        ev("alternarBloqueio(USUARIOS.filter(u => u.id === 3)[0])"); pg.wait_for_timeout(200)
        ok(not modal_aberto() and [u for u in usuarios() if u['id'] == 3][0]['situacao'] == 'ativo', 'e mesmo pela função, só o Owner bloqueia')
        ok(ev("upPodeMexer()") is False, 'upPodeMexer lê o perfil de quem está no sistema')
        # as paginas, abertas por quem nao e Owner (copia das telas, com outro perfil na sessao)
        tmp = tempfile.mkdtemp(prefix='desk-usuarios-')
        try:
            shutil.copytree(_os.path.join(PASTA, 'telas'), _os.path.join(tmp, 'telas'))
            for n in (DU, DP):
                c = _os.path.join(tmp, 'telas', 'configuracoes', n)
                t = open(c, encoding='utf-8', newline='').read()
                assert t.count("perfil: 'Owner' }") == 1
                open(c, 'w', encoding='utf-8', newline='').write(t.replace("perfil: 'Owner' }", "perfil: 'Gerente' }"))
            import pathlib
            for n, q, barra in ((DU, '?id=3', '.barra-salvar'), (DP, '?id=3', '#barraSalvar')):
                pg.goto(pathlib.Path(_os.path.join(tmp, 'telas', 'configuracoes', n)).as_uri() + q); pg.wait_for_timeout(400)
                ok(ev("document.getElementById('avisoSomenteOwner').style.display") == '' and not ev("document.querySelector('%s').offsetParent" % barra), '%s: sem o perfil Owner a página só abre para ver, sem "Salvar"' % n)
                ok(ev("Array.from(document.querySelectorAll('.main input[type=text], .main input[type=checkbox]:not(#confirmCienteCheckbox)')).every(i => i.disabled)"), '%s: todos os campos travados' % n)
            pg.goto(pathlib.Path(_os.path.join(tmp, 'telas', 'configuracoes', DU)).as_uri() + '?id=3'); pg.wait_for_timeout(300)
            ok(ev("['btnSenha', 'btnCodigo', 'btnEditarAvulsas'].every(i => document.getElementById(i).disabled)"), 'sem o perfil Owner, a senha, o código e as avulsas ficam apagados')
            antes = ev("localStorage.getItem('deskUsuarios')")
            ev("salvar()"); pg.wait_for_timeout(200)
            ok(ev("localStorage.getItem('deskUsuarios')") == antes, 'e salvar não grava')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        # o Registro de atividades mostra as acoes de usuarios
        limpo(LU)
        clica('#corpoTabela tr[data-id="4"]'); clica('#btnBloquear'); confirmar(); pg.wait_for_timeout(300)
        ir(REG)
        txt = ev("document.getElementById('corpoTabela') ? document.getElementById('corpoTabela').textContent.replace(/\\s+/g, ' ') : document.body.innerText")
        ok('Bloquear um usuário' in txt and 'Configurações → Usuários do sistema' in txt, 'o Registro de atividades lista o bloqueio, com a tela de origem')

    # ------------------------------------------------------------------------------------------------
    if secao(11, 'Os dois temas, 1280 e 1440: sem barra para o lado, o menu abre para baixo'):
        for tema in ('dark', 'light'):
            for larg in (1280, 1440):
                pg.set_viewport_size({'width': larg, 'height': 900})
                for tela, q in ((LU, ''), (LP, ''), (DU, '?id=3'), (DU, '?novo=1'), (DP, '?id=2'), (DP, '?id=1')):
                    ir(tela, q)
                    pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", tema); pg.wait_for_timeout(120)
                    m = ev("({ pag: document.documentElement.scrollWidth <= innerWidth + 1, tab: Array.from(document.querySelectorAll('.estoque-table-wrap')).every(w => w.scrollWidth <= w.clientWidth + 1) })")
                    ok(m['pag'] and m['tab'], '%s%s, %s, %d: a página e a tabela não rolam para o lado' % (tela, q, tema, larg))
                ir(LU)
                pg.evaluate("(t) => document.body.classList.toggle('dark', t === 'dark')", tema)
                for dd in ('filtroPerfil', 'filtroLoja', 'filtroSituacao'):
                    clica('#%s .dropdown-select-btn' % dd); pg.wait_for_timeout(120)
                    r = ev("(id) => { const b = document.querySelector('#' + id + ' .dropdown-select-btn').getBoundingClientRect(), m = document.querySelector('#' + id + ' .dropdown-select-menu').getBoundingClientRect(); return [m.top >= b.bottom - 1, m.right <= innerWidth + 1]; }", dd)
                    ok(all(r), '%s, %s, %d: o menu abre para baixo e cabe na janela' % (dd, tema, larg))
                    clica('#%s .dropdown-select-btn' % dd)
        pg.set_viewport_size({'width': 1440, 'height': 900})
        # o painel das permissoes avulsas cabe na janela
        ir(DU, '?id=4'); clica('#btnEditarAvulsas'); pg.wait_for_timeout(400)
        r = ev("(() => { const b = document.getElementById('eventDrawer').getBoundingClientRect(); return [b.left >= 0, Math.round(b.width), document.documentElement.scrollWidth <= innerWidth + 1]; })()")
        ok(r[0] and 500 <= r[1] <= 740 and r[2], 'o painel largo das permissões avulsas cabe em 1440 (%dpx)' % r[1])
        pg.set_viewport_size({'width': 1280, 'height': 900}); pg.wait_for_timeout(300)
        r = ev("(() => { const b = document.getElementById('eventDrawer').getBoundingClientRect(); return [b.left >= 0, document.documentElement.scrollWidth <= innerWidth + 1]; })()")
        ok(all(r), 'e em 1280')
        pg.set_viewport_size({'width': 1440, 'height': 900})
        ok(not [e for e in erros if 'ERR_' not in e and 'Failed to load' not in e], 'nenhum erro de JavaScript em toda a rodada: %s' % erros[:2])
    nav.close()

print('\n%d asserções' % total[0])
print('FALHAS: %d' % len(falhas))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
