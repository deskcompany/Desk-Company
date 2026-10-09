# -*- coding: utf-8 -*-
# Confirmacao por senha: o modal existe, a trava trava, e o despacho entrega o callback.
# Nasceu em 28/set/2026, junto com a revisao completa da pasta.
from playwright.sync_api import sync_playwright
import os, sys, re
# --- ambiente: achado sozinho, para o teste servir em qualquer sessao ---
import os as _os, glob as _g
import localiza
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

# Nao ha mais lista fixa: a partir de 28/set/2026 TODA tela que carrega o bloco de
# senha tem modal de confirmacao de verdade. O teste descobre as telas sozinho — lista
# escrita a mao envelhece, e foi assim que "8 telas" virou 23 sem ninguem perceber.
PATCHADAS = []
for _f in _filtrar(sorted(localiza.caminhos())):
    if 'molde' in _f: continue
    _c = open(_f, encoding='utf-8').read()
    if 'function confirmarAcao' in _c and 'id="confirmModal"' in _c:
        PATCHADAS.append(_os.path.basename(_f))

falhas = []
def ok(c, m):
    print(('  ok   ' if c else '  FALHA ') + m)
    if not c: falhas.append(m)

def ruido(e):
    # A fonte do Google nao carrega em sandbox sem rede: nao e defeito da tela.
    return '[desk]' in e or 'ERR_TUNNEL' in e or 'Failed to load resource' in e

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    erros = []
    pg.on('console', lambda m: erros.append(m.text) if m.type == 'error' else None)

    print('\n--- 1. telas com modal: a trava trava e a acao fica registrada ---')
    for n in PATCHADAS:
        erros.clear()
        pg.goto(localiza.uri(n)); pg.wait_for_timeout(250)
        ok(not [e for e in erros if not ruido(e)], f'{n}: carrega sem erro de console')
        ok(pg.evaluate("typeof abrirModalConfirmacao === 'function'"), f'{n}: abrirModalConfirmacao existe')
        r = pg.evaluate("""() => { window.__ran=false;
            confirmarAcao('__teste_qa__','Confirma esta ação de teste?', ()=>{window.__ran=true;});
            return {aberto:document.getElementById('confirmModal').classList.contains('open'),
                    senha:document.getElementById('campoSenhaModal').classList.contains('on'),
                    rodou:window.__ran,
                    texto:document.getElementById('confirmModalTexto').textContent}; }""")
        ok(r['aberto'], f'{n}: modal abriu')
        ok(r['senha'], f'{n}: campo de senha ligado')
        ok(not r['rodou'], f'{n}: acao NAO executou antes de confirmar')
        ok(r['texto'] == 'Confirma esta ação de teste?', f'{n}: texto chegou no modal')
        pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(120)
        r2 = pg.evaluate("({erro:document.getElementById('campoSenhaModal').classList.contains('has-error'),"
                         " rodou:window.__ran, aberto:document.getElementById('confirmModal').classList.contains('open')})")
        ok(r2['erro'] and not r2['rodou'] and r2['aberto'], f'{n}: senha vazia trava e nao executa')
        pg.fill('#inputSenhaModal', '123456'); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(150)
        r3 = pg.evaluate("({rodou:window.__ran, aberto:document.getElementById('confirmModal').classList.contains('open'),"
                         " log:(JSON.parse(localStorage.getItem('deskLog')||'[]')[0]||{}).chave})")
        ok(r3['rodou'], f'{n}: com senha, a acao executa')
        ok(not r3['aberto'], f'{n}: modal fecha depois de confirmar')
        ok(r3['log'] == '__teste_qa__', f'{n}: gravou no registro de atividades')
        pg.evaluate("abrirModalConfirmacao('x',1,'primary',()=>{})"); pg.wait_for_timeout(100)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
        ok(not pg.evaluate("document.getElementById('confirmModal').classList.contains('open')"), f'{n}: Esc fecha o modal')
        # §8: tela de detalhe que so exclui UM registro por vez nasce sem a linha do
        # "estou ciente" — ali a asercao e so a cor do botao.
        r4 = pg.evaluate("""() => { abrirModalConfirmacao('dois',2,'danger',()=>{});
            const row = document.getElementById('confirmCienteRow');
            return {temCiente: !!row,
                    ciente: row ? getComputedStyle(row).display : null,
                    travado:document.getElementById('btnConfirmModalConfirmar').disabled,
                    cor:document.getElementById('btnConfirmModalConfirmar').className}; }""")
        if r4['temCiente']:
            ok(r4['ciente'] == 'flex' and r4['travado'], f'{n}: 2+ itens pede "estou ciente" e trava o botao')
        else:
            print(f'  --   {n}: modal sem linha de "estou ciente" (exclui 1 por vez — §8)')
        ok(r4['cor'] == 'btn-danger', f'{n}: cor danger aplicada')
        pg.keyboard.press('Escape')

    print('\n--- 2. falha FECHADA: sem modal, a acao com senha nao acontece ---')
    # Nenhuma tela esta mais nessa condicao — entao a prova e derrubar a funcao em
    # tempo de execucao e exigir que `confirmarAcao` recuse, em vez de executar.
    for n in PATCHADAS[:3]:
        erros.clear()
        pg.goto(localiza.uri(n)); pg.wait_for_timeout(250)
        r = pg.evaluate("""() => { window.__ran=false;
            abrirModalConfirmacao = undefined;
            confirmarAcao('__teste_qa__','x',()=>{window.__ran=true;});
            return window.__ran; }""")
        ok(not r, f'{n}: sem o modal, a acao com senha NAO executa')
        ok(any('[desk]' in e for e in erros), f'{n}: avisa no console em vez de falhar calado')

    print('\n--- 3. as tres assinaturas do modal: o despacho entrega o callback ---')
    grupos = {}
    for f in _filtrar(sorted(localiza.caminhos())):
        c = open(f, encoding='utf-8').read()
        if 'function confirmarAcao' not in c: continue
        m = re.search(r'function\s+abrirModalConfirmacao\s*\(([^)]*)\)', c)
        if not m: continue
        k = len([a for a in m.group(1).split(',') if a.strip()])
        grupos.setdefault(k, []).append(os.path.basename(f))
    for k in sorted(grupos):
        for n in grupos[k][:2]:
            pg.goto(localiza.uri(n)); pg.wait_for_timeout(250)
            ar = pg.evaluate("abrirModalConfirmacao.length")
            pg.evaluate("() => { window.__ran=false; confirmarAcao('__qa__','t',()=>{window.__ran=true;}); }")
            pg.fill('#inputSenhaModal', '123456'); pg.click('#btnConfirmModalConfirmar'); pg.wait_for_timeout(150)
            ok(pg.evaluate("window.__ran") and ar == k,
               f'{n}: assinatura de {k} args — .length={ar}, callback disparou')
    b.close()

print(f'\nFALHAS: {len(falhas)}')
for f in falhas: print('  - ' + f)
sys.exit(1 if falhas else 0)
