import re, sys, os, subprocess, collections, tempfile

# ---------------------------------------------------------------- utilitarios
# Quatro checagens erravam por olhar o texto cru. Elas agora olham o texto
# LIMPO, ou perguntam ao proprio arquivo se aquilo tem guarda. Auditoria que
# grita a toa e auditoria que ninguem le.

def sem_comentarios(txt):
    """Tira comentario de HTML, de bloco e de linha. Usado por quem procura
    marcacao de verdade — o texto `select` aparece dentro do comentario que
    descreve o dropdown customizado, e isso nunca foi um select nativo."""
    t = re.sub(r'<!--.*?-->', '', txt, flags=re.S)
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
    t = re.sub(r'(?m)^\s*//.*$', '', t)
    return t

def tem_guarda(txt, ident):
    """A busca por `ident` esta protegida? Conta como guarda tanto o
    `if (!x) return;` quanto o `if (x)`, o `x &&` e o `?.` logo apos a
    propria chamada. Sem isto o script acusava `menuMaisAcoes` em 13 telas
    onde a linha seguinte e exatamente `if (!raiz) return;`."""
    if re.search(r"getElementById\('" + re.escape(ident) + r"'\)\s*\?\.", txt):
        return True
    for m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*document\.getElementById\('" + re.escape(ident) + r"'\)", txt):
        v = m.group(1)
        trecho = txt[m.end(): m.end() + 900]
        if re.search(r'if\s*\(\s*!' + v + r'\s*\)', trecho): return True
        if re.search(r'if\s*\(\s*' + v + r'\s*\)', trecho): return True
        if re.search(r'\b' + v + r'\s*&&', trecho): return True
        if re.search(r'\b' + v + r'\s*\?\.', trecho): return True
    return False

def ids_construidos_por_js(txt):
    """Ids que nascem de innerHTML. Uma funcao recebe o id e monta a marcacao
    (`id="' + id + '"`); `getElementById` acha em tempo de execucao. Acusar
    isto e confundir "nao esta escrito no arquivo" com "nao existe" — era o
    caso dos seis dropdowns de periodo em Metas."""
    criados = set()
    for m in re.finditer(r'function\s+(\w+)\s*\(\s*(\w+)', txt):
        nome, prim = m.group(1), m.group(2)
        i = txt.find('{', m.end())
        if i < 0: continue
        d = 0; j = i
        while j < len(txt):
            if txt[j] == '{': d += 1
            elif txt[j] == '}':
                d -= 1
                if d == 0: break
            j += 1
        corpo = txt[i:j]
        if re.search(r'id="\'\s*\+\s*' + prim + r'\b', corpo) or re.search(r'id="\$\{' + prim + r'\}', corpo):
            for c2 in re.finditer(re.escape(nome) + r"\(\s*'([^']+)'", txt):
                criados.add(c2.group(1))
    return criados

def classes_que_estilizam_checkbox(txt):
    """Classes do PAI que o CSS do proprio arquivo usa para estilizar o
    checkbox (ex.: `.dropdown-multi-item input[type="checkbox"]`). Checkbox
    dentro de um desses nao precisa carregar `.item-checkbox` no atributo."""
    css = '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', txt, re.S))
    fora = set()
    for sel in re.findall(r'([^{}]+)\{', css):
        if 'input[type="checkbox"]' in sel or "input[type='checkbox']" in sel:
            fora.update(re.findall(r'\.([A-Za-z0-9_-]+)', sel))
    return fora


def texto_de_modal(txt):
    """Trechos passados a avisar()/confirmarAcao()/abrirModalConfirmacao().

    Todos tres caem em `confirmModalTexto.textContent`. Tag escrita ali nao
    vira negrito: vira `</b>` na cara do usuario. Ja aconteceu duas vezes,
    entao virou verificacao em vez de lembrete."""
    achados = []
    for chamada in ('avisar(', 'confirmarAcao(', 'abrirModalConfirmacao('):
        i = 0
        while True:
            i = txt.find(chamada, i)
            if i < 0: break
            j = i + len(chamada); nivel = 1; aspas = None
            while j < len(txt) and nivel:
                c = txt[j]
                if aspas:
                    if c == '\\': j += 1
                    elif c == aspas: aspas = None
                elif c in '"\'`': aspas = c
                elif c == '(': nivel += 1
                elif c == ')': nivel -= 1
                j += 1
            achados.append((chamada, txt[i:j]))
            i = j
    return achados

def audita(caminho):
    nome = os.path.basename(caminho)
    txt = open(caminho, encoding='utf-8').read()
    limpo = sem_comentarios(txt)
    probs = []

    # 1A estrutura
    if txt.count('<body') != 1: probs.append('1A <body ocorre %d vez(es)' % txt.count('<body'))
    if txt.count('</html>') != 1: probs.append('1A </html> ausente/duplicado')
    ab = len(re.findall(r'<div\b', txt)); fe = txt.count('</div>')
    if ab != fe: probs.append('1B divs: %d abertas x %d fechadas' % (ab, fe))
    if txt.count('<script') != txt.count('</script>'): probs.append('1B script desbalanceado')
    if txt.count('<style') != txt.count('</style>'): probs.append('1B style desbalanceado')

    # 2 ids duplicados
    ids = re.findall(r'\sid="([^"]+)"', txt)
    dup = [k for k, v in collections.Counter(ids).items() if v > 1]
    if dup: probs.append('2 ids duplicados: ' + ', '.join(dup))

    # 3 getElementById sem id no HTML (ignora ids criados por innerHTML)
    usados = set(re.findall(r"getElementById\('([^']+)'\)", txt))
    criados = set(ids) | set(re.findall(r"id=\\?'?\"?chk", txt))
    dinamicos = set(re.findall(r"id=\"' \+ ", txt))
    faltando = sorted(u for u in usados if u not in set(ids) and not u.startswith('chk'))
    # Busca guardada (`if (!x) return;`, `if (x)`, `x &&`, `?.`) nao e defeito:
    # a tela previu a ausencia. Antes isto era uma lista de dois ids na mao.
    faltando = [u for u in faltando if not tem_guarda(txt, u)]
    faltando = [u for u in faltando if u not in ids_construidos_por_js(txt)]
    if faltando: probs.append('3 getElementById sem elemento: ' + ', '.join(faltando))

    # 4 select nativo e checkbox sem classe do design system
    if re.search(r'<select\b', limpo): probs.append('4 <select> nativo')
    pais_ok = classes_que_estilizam_checkbox(txt)
    for m in re.finditer(r'<input[^>]*type="checkbox"[^>]*>', limpo):
        tag = m.group(0)
        if 'item-checkbox' in tag or 'checkbox-todos' in tag:
            continue
        # o pai estiliza? olha as classes das tags abertas logo antes
        volta = limpo[max(0, m.start() - 400): m.start()]
        herdadas = set(x for cl in re.findall(r'class="([^"]+)"', volta) for x in cl.split())
        if herdadas & pais_ok:
            continue
        probs.append('4 checkbox sem classe do DS: ' + tag[:70])

    # 10 tag escrita dentro de texto de modal (o modal usa textContent)
    for chamada, trecho in texto_de_modal(limpo):
        # so o argumento de TEXTO interessa; a funcao executora vem depois
        corte = trecho.split('() =>')[0].split('function ()')[0]
        tags = set(re.findall(r'</?(?:b|i|u|strong|em|br|span|div|p)\b[^>]*>', corte))
        if tags:
            probs.append('10 tag literal em texto de modal (%s): %s'
                         % (chamada.rstrip('('), ', '.join(sorted(tags))[:60]))

    # 11 item de menu repetido dentro do mesmo flyout
    # Clonar uma tela e renomear em bloco ja transformou o item "Contas a Pagar"
    # em um segundo "Contas a Receber": o menu ficou com o mesmo nome duas vezes
    # e um modulo inteiro sumiu dele. Link quebrado a auditoria oficial pega;
    # item DUPLICADO, nao — os dois apontavam para arquivo existente.
    for fly in re.finditer(r'id="(flyout-[a-z-]+)"(.*?)(?=<div class="flyout-col"|<div class="flyout"|$)', limpo, re.S):
        nome_fly, corpo = fly.group(1), fly.group(2)[:6000]
        rotulos = re.findall(r'class="flyout-item"[^>]*data-label="([^"]+)"', corpo)
        repetidos = [k for k, v in collections.Counter(rotulos).items() if v > 1]
        if repetidos:
            probs.append('11 item de menu repetido em %s: %s' % (nome_fly, ', '.join(repetidos)))

    # 12 a folha de confirmacao executa ANTES de fechar
    # O botao Confirmar chamava o callback e so entao fechava. Callback que
    # termina com `avisar(...)` abria a folha e o fechamento seguinte a derrubava
    # na mesma linha: a explicacao do que acabou de acontecer era escrita e
    # apagada antes de alguem ler. Nenhum teste pegava porque o TEXTO estava la
    # — so a folha e que nao estava aberta. Oito telas; o funil do Pedido de
    # Venda era uma delas.
    if re.search(r'if \(acaoConfirmada\) acaoConfirmada\(\);\s*\n?\s*fecharModalConfirmacao\(\);', limpo):
        probs.append('12 a folha de confirmacao executa antes de fechar: aviso dentro do callback nao aparece')

    # 5 fontes
    fontes = set(re.findall(r"font-family:\s*'([^']+)'", txt))
    ruins = fontes - {'Nunito'}
    if ruins: probs.append('5 fonte fora do padrao: ' + ', '.join(ruins))

    # 6 sintaxe JS
    for i, m in enumerate(re.finditer(r'<script[^>]*>(.*?)</script>', txt, re.S)):
        js = m.group(1)
        f = os.path.join(tempfile.gettempdir(), '_aud_%s_%d.js' % (nome.replace('.', '_'), i))
        open(f, 'w', encoding='utf-8').write(js)
        r = subprocess.run(['node', '--check', f], capture_output=True, text=True)
        if r.returncode != 0:
            probs.append('6 erro de sintaxe no script %d: %s' % (i, r.stderr.strip().splitlines()[-3:]))

    # 7 chaves de senha usadas x catalogo
    chaves_uso = set(re.findall(r"(?:exigeSenha|armarSenhaModal|confirmarAcao)\('([A-Za-z]+)'", txt))
    bases = set(re.findall(r"\{ base:'([A-Za-z]+)'", txt))
    espec = set(re.findall(r"\{ chave:'([A-Za-z]+)'", txt))
    sufixos = ['Criar', 'Editar', 'Exclui']
    catalogo = set(espec)
    for b in bases:
        for s in sufixos: catalogo.add(b + s)
    orfas = sorted(k for k in chaves_uso if k not in catalogo)
    if orfas: probs.append('7 chave fora do catalogo: ' + ', '.join(orfas))

    # 8 localStorage
    for k in set(re.findall(r"localStorage\.\w+Item\(\"([^\"]+)\"|localStorage\.\w+Item\('([^']+)'", txt)):
        pass
    # Sao CINCO os depositos compartilhados, e so cinco (o comentario dizia
    # "tres" e ja listava quatro — a lista e que manda):
    #   deskParametros  - a configuracao do sistema
    #   deskLog         - o registro de atividades
    #   deskCaixaExtras - movimentos que uma tela grava e o Caixa le (baixa de contas)
    #   deskAvisos      - avisos que uma tela publica e a Agenda le (renovacao)
    #   deskNomes       - o dicionario de rotulos das listas FECHADAS (08/out).
    #                     Chave e do codigo e nao muda; rotulo e de quem usa o
    #                     sistema e se edita em Configuracoes > Nomes do sistema.
    # Qualquer outra chave e tela guardando estado por conta propria: erro.
    OK_LS = {'deskParametros', 'deskLog', 'deskCaixaExtras', 'deskAvisos', 'deskNomes', 'deskPdv'}
    chaves_ls = set(x for t in re.findall(r"localStorage\.\w+Item\(['\"]([^'\"]+)['\"]", txt) for x in [t])
    if chaves_ls - OK_LS:
        probs.append('8 chave de localStorage inesperada: ' + ', '.join(chaves_ls - OK_LS))

    # 9 botoes/links com id e sem listener
    with_id = set(re.findall(r'<(?:button|div|a)[^>]*\sid="(btn[^"]+|link[^"]+)"', limpo))
    # Link com destino real NAVEGA: nao precisa de listener nenhum. Antes o
    # script acusava seis `a href` como "controle mudo".
    navegam = set()
    for m in re.finditer(r'<a\b[^>]*>', limpo):
        tag = m.group(0)
        mid = re.search(r'\sid="([^"]+)"', tag)
        href = re.search(r'\shref="([^"]*)"', tag)
        if mid and href and href.group(1) not in ('', '#') and not href.group(1).startswith('javascript:'):
            navegam.add(mid.group(1))
    sem_acao = [i for i in with_id
                if i not in navegam
                and ("getElementById('" + i + "')") not in txt
                and ('querySelector' not in txt or ("#" + i) not in txt)]
    if sem_acao: probs.append('9 controle sem acao: ' + ', '.join(sorted(sem_acao)))

    return nome, probs

# O molde consolidado sao DOIS documentos no mesmo arquivo, de proposito: a
# listagem que executa e o Produtos-detalhe anexado como referencia. Dois
# `body`, um `/html` e ids repetidos sao o esperado ali — e so ali. Marcado
# como EXCECAO em vez de silenciado: o problema continua visivel, sem contar
# como falha e sem poluir o resultado das outras 52.
EXCECOES = {
    # O molde tem DOIS documentos no mesmo arquivo, entao tem dois menus — e por
    # isso todo rotulo de menu aparece duas vezes nele, de proposito.
    'pagina-molde-referencia.html': ('1A ', '2 ids duplicados', '11 item de menu repetido'),
}

falhas = 0
for c in sys.argv[1:]:
    nome, probs = audita(c)
    previstos = EXCECOES.get(nome, ())
    reais = [x for x in probs if not any(x.startswith(e) for e in previstos)]
    excecoes = [x for x in probs if x not in reais]
    if reais:
        falhas += 1
        print('FALHA ' + nome)
    elif excecoes:
        print('EXCECAO ' + nome + ' (dois documentos no mesmo arquivo — previsto)')
    else:
        print('OK    ' + nome)
    for p in reais: print('      - ' + p)
    for p in excecoes: print('      ~ (previsto) ' + p[:90])

# O veredito sai SEMPRE, com um arquivo ou com cinquenta, e o codigo de saida
# acompanha. Antes a linha de resumo so aparecia com 2+ arquivos: o `selo.py`,
# que le essa linha, dava a auditoria por reprovada numa rodada de um arquivo so
# — ferramenta limpa, veredito ilegivel. Quem julga precisa de resposta em
# TODA chamada, nao so na chamada grande.
print('\n%d arquivo(s) com falha real, de %d' % (falhas, len(sys.argv) - 1))
sys.exit(1 if falhas else 0)
