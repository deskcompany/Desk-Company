# -*- coding: utf-8 -*-
# SELO DE VERIFICACAO — 30/set/2026
#
# O problema que ele resolve: a verificacao completa (15 suites + 2 auditorias)
# passou de 20 minutos. Rodar tudo depois de mexer em 2 telas e caro, e teste
# caro demais e teste que alguem comeca a pular — e teste pulado nao protege
# nada. Mas "pular por achismo" e pior ainda: foi assim que a exclusao em massa
# ficou sem senha por 11 dias.
#
# A regra, entao, e mecanica e nao depende de memoria de ninguem:
#
#   uma suite so e pulada quando NADA que ela cobre mudou desde que ela passou.
#
# O selo guarda, por suite, o SHA-256 de cada arquivo que ela cobre e o SHA da
# propria suite. Na hora de verificar:
#
#   arquivo coberto mudou  -> a suite roda (nas telas que mudaram, quando ela
#                             varre a pasta; inteira, quando ela e de telas fixas)
#   a suite mudou          -> a suite roda inteira (teste novo nunca nasce selado)
#   tela nova apareceu     -> toda suite que varre a pasta roda nela
#   nada mudou             -> SELADA, pula
#
# Cobertura nao e escrita a mao: sai do proprio codigo da suite (os nomes de
# `pagina-*.html` que ela cita, ou "a pasta toda" quando ela faz glob). Lista
# escrita a mao envelhece — foi o que fez "8 telas com o problema" virar 23.
#
# Uso:
#   python3 selo.py                 o que esta selado e o que precisa rodar
#   python3 selo.py --rodar         roda so o que precisa, e sela o que passar
#   python3 selo.py --rodar --tudo  ignora o selo, roda tudo, e sela
#   python3 selo.py --selar         sela o estado atual sem rodar (use so quando
#                                   acabou de rodar tudo verde na mao)
#
# O selo vive em `selo.json`, do lado deste arquivo, e vai para a pasta do
# usuario junto com o resto — sessao nova ja abre sabendo o que esta provado.
import hashlib
import json
import os
import re
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.environ.get('DESK_PASTA') or os.path.dirname(AQUI)
SELO = os.path.join(AQUI, 'selo.json')
VERSAO = 1

# Auditoria oficial da skill: e a autoridade, e nao aceita lista de arquivos —
# ela varre a pasta inteira. Entao ela e selada no conjunto: se NENHUMA tela
# mudou, pula; se qualquer uma mudou, roda inteira.
AUDITORIA_OFICIAL = os.environ.get('DESK_AUDITORIA_OFICIAL') or (
    '/root/.claude/plugins/synced/44dd30e4-8853-45a7-867a-c1c780abb4a1_'
    '7e3124fd-8416-4980-a388-94ccf3f7a041/desk-company-erp/skills/'
    'desk-company-erp/assets/auditoria.py')


# ---------------------------------------------------------------- utilitarios
def sha(caminho):
    h = hashlib.sha256()
    with open(caminho, 'rb') as f:
        for bloco in iter(lambda: f.read(65536), b''):
            h.update(bloco)
    return h.hexdigest()[:16]


def telas():
    return sorted(a for a in os.listdir(PASTA) if a.startswith('pagina-') and a.endswith('.html'))


def suites():
    return sorted(a for a in os.listdir(AQUI) if a.startswith('teste_') and a.endswith('.py'))


def cobertura(suite):
    """(arquivos cobertos, varre_a_pasta) lidos do codigo da propria suite."""
    fonte = open(os.path.join(AQUI, suite), encoding='utf-8').read()
    varre = bool(re.search(r"glob\([^)]*'(?:\*|pagina-\*)\.html'", fonte)) or \
        bool(re.search(r"glob\(PASTA \+ '/pagina-\*\.html'\)", fonte))
    if varre:
        return telas(), True
    citados = sorted(set(re.findall(r"pagina-[a-z0-9-]+\.html", fonte)))
    return [c for c in citados if os.path.exists(os.path.join(PASTA, c))], False


def sha_ferramenta():
    """Muda quando o filtro DESK_ALVOS muda — invalida todo selo de suite."""
    p = os.path.join(AQUI, 'alvos.py')
    return sha(p) if os.path.exists(p) else '-'


def ler_selo():
    if not os.path.exists(SELO):
        return {'versao': VERSAO, 'suites': {}, 'auditorias': {}}
    d = json.load(open(SELO, encoding='utf-8'))
    return d if d.get('versao') == VERSAO else {'versao': VERSAO, 'suites': {}, 'auditorias': {}}


def gravar_selo(d):
    d['versao'] = VERSAO
    json.dump(d, open(SELO, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)


# ------------------------------------------------------------------ diagnostico
def estado():
    """Para cada suite: 'selada' ou o motivo de rodar, e em quais telas."""
    d = ler_selo()
    hoje = {t: sha(os.path.join(PASTA, t)) for t in telas()}
    saida = []
    for s in suites():
        cob, varre = cobertura(s)
        gravado = d['suites'].get(s)
        meu_sha = sha(os.path.join(AQUI, s))
        if not gravado:
            saida.append((s, 'nunca selada', cob if varre else [], varre, cob))
            continue
        if gravado.get('teste_sha') != meu_sha:
            saida.append((s, 'a propria suite mudou', cob if varre else [], varre, cob))
            continue
        if gravado.get('ferramenta_sha') != sha_ferramenta():
            saida.append((s, 'o filtro de alvos mudou', cob if varre else [], varre, cob))
            continue
        antes = gravado.get('cobertura', {})
        mudaram = [t for t in cob if hoje.get(t) != antes.get(t)]
        sumiram = [t for t in antes if t not in hoje]
        if sumiram:
            saida.append((s, 'tela coberta sumiu: ' + ', '.join(sumiram), cob if varre else [], varre, cob))
        elif mudaram:
            rotulo = ('%d tela(s) mudaram' % len(mudaram)) if len(mudaram) > 3 else ', '.join(mudaram)
            saida.append((s, rotulo, mudaram if varre else [], varre, cob))
        else:
            saida.append((s, None, [], varre, cob))
    # auditorias
    conjunto = hashlib.sha256(''.join(hoje[t] for t in sorted(hoje)).encode()).hexdigest()[:16]
    aud = []
    sha_estrita = sha(os.path.join(AQUI, 'auditoria.py'))
    sha_oficial = sha(AUDITORIA_OFICIAL) if os.path.exists(AUDITORIA_OFICIAL) else '-'
    a_estrita = d['auditorias'].get('estrita', {})
    mudaram = [t for t in hoje if hoje[t] != a_estrita.get('cobertura', {}).get(t)]
    if not a_estrita:
        motivo_e = 'nunca selada'
    elif a_estrita.get('script_sha') != sha_estrita:
        motivo_e, mudaram = 'a auditoria.py mudou', list(hoje)
    else:
        motivo_e = ('%d tela(s) mudaram' % len(mudaram)) if mudaram else None
    aud.append(('estrita', motivo_e, mudaram))
    a_of = d['auditorias'].get('oficial', {})
    if not a_of:
        motivo_o = 'nunca selada'
    elif a_of.get('script_sha') != sha_oficial:
        motivo_o = 'a auditoria oficial da skill mudou'
    elif a_of.get('conjunto') != conjunto:
        motivo_o = 'a pasta mudou'
    else:
        motivo_o = None
    aud.append(('oficial', motivo_o, []))
    return saida, aud, hoje, conjunto


# ---------------------------------------------------------------------- rodar
def roda(cmd, env=None, limite=900):
    amb = dict(os.environ)
    amb.setdefault('DESK_PASTA', PASTA)
    if env:
        amb.update(env)
    t0 = time.time()
    p = subprocess.run(cmd, cwd=AQUI, env=amb, capture_output=True, text=True, timeout=limite)
    return p.returncode, (p.stdout or '') + (p.stderr or ''), time.time() - t0


def verde_suite(saida):
    m = re.findall(r'FALHAS:\s*(\d+)', saida)
    return bool(m) and all(int(x) == 0 for x in m)


def asseracoes(saida):
    return saida.count('  ok   ') + saida.count('  ok ')


def principal():
    args = sys.argv[1:]
    so_status = '--rodar' not in args and '--selar' not in args
    tudo = '--tudo' in args
    lista, aud, hoje, conjunto = estado()

    print('SELO DE VERIFICACAO — %s' % time.strftime('%d/%m/%Y %H:%M'))
    print('pasta: %s · %d telas · %d suites\n' % (PASTA, len(hoje), len(lista)))

    seladas = [x for x in lista if x[1] is None and not tudo]
    rodar = [x for x in lista if x[1] is not None or tudo]

    for s, motivo, alvos, varre, cob in lista:
        if motivo is None and not tudo:
            print('  SELADA   %-26s (%d arquivo%s)' % (s, len(cob), '' if len(cob) == 1 else 's'))
        else:
            alvo_txt = (' · alvos: %d tela(s)' % len(alvos)) if alvos else ''
            print('  RODAR    %-26s %s%s' % (s, motivo or 'forcado (--tudo)', alvo_txt))
    for nome, motivo, alvos in aud:
        selada_aud = motivo is None and not tudo
        print('  %s auditoria %s%s' % ('SELADA  ' if selada_aud else 'RODAR   ', nome,
                                       '' if selada_aud else ' — ' + (motivo or 'forcado (--tudo)')))

    if so_status:
        print('\n%d selada(s), %d a rodar. `--rodar` executa so o que precisa.'
              % (len(seladas), len(rodar)))
        return 0

    d = ler_selo()
    if '--selar' in args and '--rodar' not in args:
        for s, _motivo, _alvos, _varre, cob in lista:
            d['suites'][s] = {'teste_sha': sha(os.path.join(AQUI, s)),
                              'ferramenta_sha': sha_ferramenta(),
                              'cobertura': {t: hoje[t] for t in cob},
                              'selado_em': time.strftime('%Y-%m-%d'),
                              'asseracoes': d['suites'].get(s, {}).get('asseracoes')}
        d['auditorias'] = {
            'estrita': {'cobertura': dict(hoje), 'script_sha': sha(os.path.join(AQUI, 'auditoria.py')),
                        'selado_em': time.strftime('%Y-%m-%d')},
            'oficial': {'conjunto': conjunto,
                        'script_sha': sha(AUDITORIA_OFICIAL) if os.path.exists(AUDITORIA_OFICIAL) else '-',
                        'selado_em': time.strftime('%Y-%m-%d')}}
        gravar_selo(d)
        print('\nSelado o estado atual, sem rodar nada. (Use so depois de uma rodada verde na mao.)')
        return 0

    falhou = []
    print('')
    for s, motivo, alvos, varre, cob in rodar:
        restrita = bool(alvos and varre and not tudo and len(alvos) < len(cob))
        env = {'DESK_ALVOS': ','.join(alvos)} if restrita else {'DESK_ALVOS': ''}
        cod, saida, seg = roda(['python3', s], env)
        verde = cod == 0 and verde_suite(saida)
        n = asseracoes(saida)
        print('  %-26s %s  %5.1fs  %s' % (s, 'ok   ' if verde else 'FALHOU', seg,
                                          ('%d asserções%s' % (n, ' em %d tela(s)' % len(alvos) if restrita else '')) if verde else ''))
        if verde:
            # Rodada restrita conta menos asserções do que a suite inteira prova.
            # Gravar esse numero menor faria o total do selo encolher a cada
            # correcao pontual — numero que mente e pior que numero nenhum.
            # So a rodada COMPLETA atualiza a contagem.
            antes_n = (d['suites'].get(s) or {}).get('asseracoes')
            d['suites'][s] = {'teste_sha': sha(os.path.join(AQUI, s)),
                              'ferramenta_sha': sha_ferramenta(),
                              'cobertura': {t: hoje[t] for t in cob},
                              'selado_em': time.strftime('%Y-%m-%d'),
                              'asseracoes': (antes_n if (restrita and antes_n) else n),
                              'asseracoes_de': ((d['suites'].get(s) or {}).get('asseracoes_de')
                                                if (restrita and antes_n) else 'rodada completa ' + time.strftime('%d/%m'))}
        else:
            falhou.append(s)
            print('\n'.join('      ' + l for l in saida.strip().split('\n')[-12:]))

    for nome, motivo, alvos in aud:
        if motivo is None and not tudo:
            continue
        if nome == 'estrita':
            alvo = [os.path.join(PASTA, t) for t in (alvos if (alvos and not tudo) else hoje)]
            cod, saida, seg = roda(['python3', 'auditoria.py'] + alvo)
            # Codigo de saida PRIMEIRO: e o contrato que nao depende de formato
            # de texto. A linha de resumo fica como segunda confirmacao.
            verde = cod == 0 and re.search(r'\n0 arquivo\(s\) com falha real', saida) is not None
            print('  %-26s %s  %5.1fs  (%d arquivo(s))' % ('auditoria estrita', 'ok   ' if verde else 'FALHOU', seg, len(alvo)))
            if verde:
                d.setdefault('auditorias', {})['estrita'] = {'cobertura': dict(hoje), 'script_sha': sha(os.path.join(AQUI, 'auditoria.py')), 'selado_em': time.strftime('%Y-%m-%d')}
            else:
                falhou.append('auditoria estrita')
                print('\n'.join('      ' + l for l in saida.strip().split('\n')[-12:]))
        else:
            if not os.path.exists(AUDITORIA_OFICIAL):
                print('  %-26s pulada (a skill nao esta montada nesta sessao)' % 'auditoria oficial')
                continue
            cod, saida, seg = roda(['python3', AUDITORIA_OFICIAL, PASTA])
            verde = 'tudo limpo' in saida
            print('  %-26s %s  %5.1fs' % ('auditoria oficial', 'ok   ' if verde else 'FALHOU', seg))
            if verde:
                d.setdefault('auditorias', {})['oficial'] = {'conjunto': conjunto, 'script_sha': sha(AUDITORIA_OFICIAL), 'selado_em': time.strftime('%Y-%m-%d')}
            else:
                falhou.append('auditoria oficial')
                print('\n'.join('      ' + l for l in saida.strip().split('\n')[-14:]))

    gravar_selo(d)
    total = sum((v.get('asseracoes') or 0) for v in d['suites'].values())
    print('\n%d selada(s) · %d asserções sob selo (contadas na última rodada completa de cada suíte) · FALHAS: %d'
          % (len(d['suites']), total, len(falhou)))
    for f in falhou:
        print('  - ' + f)
    return 1 if falhou else 0


if __name__ == '__main__':
    sys.exit(principal())
