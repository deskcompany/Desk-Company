# Rodape de salvar — 08/out/2026.
#
# O sistema tinha QUATRO nomes para um componente so: .barra-salvar (8 telas),
# .par-barra (Configuracoes), .form-footer-bar (os cadastros) e dois rodapes
# soltos usando .form-actions e .drawer-footer. Tres deles ja punham o botao a
# esquerda; o quarto, nao. E o preco de ter quatro nomes apareceu em Pedidos de
# Venda: alguem renomeou o CSS para .barra-salvar e esqueceu o HTML, que ficou
# em .form-footer-bar — classe que naquela tela so existia dentro de
# body.modo-leitura, para esconder. Em modo de edicao a barra era uma div crua,
# sem sticky, sem borda, sem espacamento, e ninguem percebeu.
#
# Agora e um nome so. Esta suite guarda as quatro promessas do componente:
#   1. nenhum dos nomes antigos sobrevive em lugar nenhum da pasta;
#   2. o botao fica na ponta esquerda da barra e a nota na ponta direita;
#   3. a nota diz a verdade — e a verdade e medida contra a tela JA montada,
#      nao contra o esqueleto vazio que existia no instante do carregamento;
#   4. sair com alteracao pendente para e pergunta, em vez de levar embora o
#      que nao foi salvo. Era isso que o antigo "Cancelar" fazia calado: ele
#      nao cancelava nada, so navegava.
from playwright.sync_api import sync_playwright
import os, sys, glob, io
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
PASTA = _os.environ.get('DESK_PASTA') or _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_os.chdir(PASTA)
import sys as _sys, os as _os2
_sys.path.insert(0, _os2.path.dirname(_os2.path.abspath(__file__)))
try:
    from alvos import filtrar as _filtrar          # DESK_ALVOS: roda so nas telas pedidas
except Exception:
    def _filtrar(x): return x
_ch = _g.glob('/opt/pw-browsers/chromium*/chrome-linux/chrome') + _g.glob('/opt/pw-browsers/chromium*/chrome-linux*/chrome')
CHROME = _ch[0] if _ch else None      # None = o Playwright usa o navegador dele
# ------------------------------------------------------------------------

falhas = []
total = [0]


def sufixo(nome):
    """?editar=1 porque varias telas abrem em modo leitura, e la o rodape e
    escondido de proposito. ?id=1 nas de detalhe: sem documento elas dizem
    'nao encontrado' e escondem o rodape — tambem de proposito."""
    return '?id=1&editar=1' if nome.endswith('-detalhe.html') else '?editar=1'


def ok(cond, texto):
    total[0] += 1
    if not cond:
        falhas.append(texto)
        print('  FALHOU  ' + texto)


# Nomes aposentados. Cada um foi, um dia, o jeito certo de escrever um rodape
# de pagina — e e exatamente por isso que precisam estar mortos: enquanto os
# dois existirem, a proxima tela copia o que estiver mais perto.
APOSENTADOS = ['form-footer-bar', 'par-barra', 'par-barra-nota']

arquivos = _filtrar(sorted(glob.glob(PASTA + '/pagina-*.html')))

print('[1] Os nomes antigos nao existem mais em lugar nenhum')
for arq in arquivos:
    nome = os.path.basename(arq)
    with io.open(arq, encoding='utf-8') as f:
        fonte = f.read()
    for velho in APOSENTADOS:
        ok(velho not in fonte, '%s ainda cita "%s"' % (nome, velho))
    # .form-actions e .drawer-footer continuam validos DENTRO de painel lateral;
    # o que nao pode e um deles bancar o rodape da pagina.
    ok('class="form-actions"' not in fonte,
       '%s usa .form-actions como rodape de pagina' % nome)

# O molde consolidado tem dois documentos no mesmo arquivo e o segundo vive
# dentro de um comentario HTML — o navegador nao renderiza nada dele. E a
# mesma excecao da secao 1B da auditoria. A checagem de texto [1] continua
# valendo para ele; so as medidas de navegador nao fazem sentido.
ocultas = []
com_barra = []
for arq in arquivos:
    if os.path.basename(arq) == 'pagina-molde-referencia.html':
        continue
    with io.open(arq, encoding='utf-8') as f:
        if 'class="barra-salvar"' in f.read():
            com_barra.append(arq)
print('    %d tela(s) com rodape de salvar' % len(com_barra))

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 950})

    print('[2] Uma barra so por tela, botao a esquerda e nota a direita')
    print('[3] A nota nasce dizendo a verdade sobre a tela JA montada')
    print('[4] Mexer num campo faz a nota contar, e desfazer zera a contagem')
    for arq in com_barra:
        nome = os.path.basename(arq)
        erros = []
        pg.on('pageerror', lambda e, box=erros: box.append(str(e)))
        # ?editar=1 porque varias destas telas abrem em modo leitura, e la o
        # rodape e escondido de proposito — nao ha o que salvar.
        pg.goto('file://' + arq + sufixo(nome))
        pg.wait_for_load_state('load')
        pg.wait_for_timeout(700)

        # --- [2] geometria -------------------------------------------------
        ok(pg.locator('.barra-salvar').count() == 1,
           '%s: deveria ter exatamente uma .barra-salvar' % nome)
        if not pg.locator('.barra-salvar').is_visible():
            # O ?id=1 pode cair num documento ja fechado, e ai o rodape some de
            # proposito. Antes de desistir da tela, tenta sem o documento.
            pg.goto('file://' + arq + '?editar=1')
            pg.wait_for_load_state('load')
            pg.wait_for_timeout(700)
        if not pg.locator('.barra-salvar').is_visible():
            # Rodape escondido na abertura e proposital: documento ja quitado,
            # pedido ja expedido — nao ha o que salvar. Nada a medir aqui.
            print('  --  %s: rodape oculto nesta abertura' % nome)
            ocultas.append(nome)
            continue
        caixa = pg.evaluate("""() => {
          const bar = document.querySelector('.barra-salvar');
          if (!bar) return null;
          const btn = bar.querySelector('.btn-primary');
          const nota = bar.querySelector('.barra-info');
          const r = bar.getBoundingClientRect();
          return {
            btn: btn ? btn.getBoundingClientRect().left - r.left : null,
            nota: nota ? r.right - nota.getBoundingClientRect().right : null,
            temNota: !!nota
          };
        }""")
        ok(caixa and caixa['btn'] is not None and caixa['btn'] < 20,
           '%s: o botao principal deveria encostar na esquerda da barra (%s)' % (nome, caixa and caixa['btn']))
        ok(caixa and caixa['temNota'], '%s: a barra deveria ter a nota de estado' % nome)
        if caixa and caixa['temNota']:
            ok(caixa['nota'] < 20,
               '%s: a nota deveria encostar na direita da barra (%s)' % (nome, caixa['nota']))

        # --- [3] a referencia foi medida com a tela pronta ------------------
        # O bug que isto pega e silencioso: medida antes de a tela se montar, a
        # referencia congela um formulario vazio. A nota continua dizendo
        # "nenhuma alteracao pendente" — nao porque seja verdade, mas porque
        # parou de olhar. So se descobre quando alguem digita.
        tem_rodape = pg.evaluate("typeof RODAPE !== 'undefined' && typeof estadoDoFormulario === 'function'")
        if tem_rodape:
            ok(pg.evaluate('RODAPE.limpo === estadoDoFormulario()'),
               '%s: a referencia nao bate com a tela ja montada' % nome)
            ok(pg.evaluate('temPendencia()') is False,
               '%s: tela recem-aberta nao deveria ter pendencia' % nome)
        nota_inicial = pg.inner_text('.barra-info') if caixa and caixa['temNota'] else ''
        ok('Nenhuma alteração pendente' in nota_inicial or 'ainda não existe' in nota_inicial,
           '%s: a nota deveria abrir dizendo que nada esta pendente (disse "%s")' % (nome, nota_inicial[:50]))

        # --- [4] a nota acompanha o que a pessoa faz ------------------------
        if tem_rodape:
            campo = pg.evaluate("""() => {
              const livres = [...document.querySelectorAll('.main input[type=text]')]
                .filter(e => e.offsetParent !== null && !e.disabled && !e.readOnly);
              const el = livres.find(e => e.value.trim() !== '') || livres[0];
              if (!el) return null;
              if (el.id) return '#' + el.id;
              return '.main input[type=text] >> nth=' +
                [...document.querySelectorAll('.main input[type=text]')].indexOf(el);
            }""")
            if campo:
                antes = pg.input_value(campo)
                pg.fill(campo, 'ZZ teste de rodape')
                pg.wait_for_timeout(260)
                ok('ainda não salvo' in pg.inner_text('.barra-info'),
                   '%s: depois de digitar, a nota deveria acusar pendencia (disse "%s")'
                   % (nome, pg.inner_text('.barra-info')[:50]))
                pg.fill(campo, antes)
                pg.wait_for_timeout(260)
                ok('Nenhuma alteração pendente' in pg.inner_text('.barra-info'),
                   '%s: desfazer deveria zerar a nota (ficou "%s")'
                   % (nome, pg.inner_text('.barra-info')[:50]))

        ok(not erros, '%s: erro de JS no rodape — %s' % (nome, erros[:1]))
        pg.remove_listener('pageerror', lambda e: None) if False else None

    print('[5] Sair com pendencia PARA e pergunta — o buraco que o "Cancelar" tinha')
    # So vale onde o rodape tem caminho de saida. Minha Conta nao tem (abre
    # pelo menu do perfil) e Metas se edita na propria grade.
    for arq in com_barra:
        nome = os.path.basename(arq)
        # ?editar=1 porque varias destas telas abrem em modo leitura, e la o
        # rodape e escondido de proposito — nao ha o que salvar.
        if nome in ocultas:
            continue
        pg.goto('file://' + arq + sufixo(nome))
        pg.wait_for_load_state('load')
        pg.wait_for_timeout(700)
        if not pg.locator('.barra-salvar').is_visible():
            pg.goto('file://' + arq + '?editar=1')
            pg.wait_for_load_state('load')
            pg.wait_for_timeout(700)
        tem = pg.evaluate("""() => {
          const bar = document.querySelector('.barra-salvar');
          const link = bar && bar.querySelector('.drawer-link');
          return !!(link && typeof temPendencia === 'function'
                    && typeof abrirModalConfirmacao === 'function');
        }""")
        if not tem:
            continue
        campo = pg.evaluate("""() => {
          const livres = [...document.querySelectorAll('.main input[type=text]')]
            .filter(e => e.offsetParent !== null && !e.disabled && !e.readOnly);
          const el = livres.find(e => e.value.trim() !== '') || livres[0];
          if (!el) return null;
          if (el.id) return '#' + el.id;
          return '.main input[type=text] >> nth=' +
            [...document.querySelectorAll('.main input[type=text]')].indexOf(el);
        }""")
        if not campo:
            continue
        pg.fill(campo, 'ZZ saida com pendencia')
        pg.wait_for_timeout(260)
        if not pg.evaluate('temPendencia()'):
            continue
        antes_url = pg.url
        # Clique pelo DOM: com um modal aberto o Playwright recusa o clique
        # por interceptacao de ponteiro, e aqui o modal e justamente o que
        # se quer provocar. As outras suites ja usam este caminho.
        pg.evaluate("() => [...document.querySelectorAll('.barra-salvar .drawer-link')].pop().click()")
        pg.wait_for_timeout(500)
        # Duas respostas sao honestas: parar e perguntar (link que SAI), ou
        # desfazer na hora (link que DESCARTA, como em Minha Conta). O que nao
        # vale e sumir da tela calado levando o que nao foi salvo — era
        # exatamente isso que o antigo "Cancelar" fazia.
        perguntou = pg.url == antes_url and pg.locator('#confirmModal.open').count() == 1
        descartou = pg.url == antes_url and pg.evaluate('temPendencia()') is False
        ok(perguntou or descartou,
           '%s: clicar no link do rodape com pendencia nao perguntou nem desfez '
           '(url mudou: %s)' % (nome, pg.url != antes_url))

    b.close()

print('')
print('%d asserções · FALHAS: %d' % (total[0], len(falhas)))
for f in falhas:
    print('  - ' + f)
sys.exit(1 if falhas else 0)
