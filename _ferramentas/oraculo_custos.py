# -*- coding: utf-8 -*-
# A conta do lucro de um pedido (Custos do E-commerce, 21/out/2026; devolucao, cortesia e itens em 27/out/2026), refeita em Python com Decimal e meio para cima,
# sem olhar o codigo da tela: o oraculo que as suites de Custos do E-commerce e de Comissoes usam para conferir o JavaScript.
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

D = lambda x: Decimal(str(x))
c2 = lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
TAXAS_LINK = [4.20, 6.09, 7.01, 7.91, 8.80, 9.67, 12.59, 13.42, 14.25, 15.06, 15.87, 16.66]   # InfinitePay, Link de pagamento, 1x a 12x
PADRAO_EMB = {1: 5, 2: 8, 3: 0}
# Os itens dos pedidos de venda que tem itens no exemplo (ITENS_PEDIDO): sku, nome, categoria, qtd, preco, custo e custo medio de UMA unidade.
# Os online (1, 3, 4, 8, 9, 11, 12, 16) fecham no total (itens mais frete), na soma do custo e na do custo medio.
ITENS = {
    1:  [('FON-BT-200', 'Fone de Ouvido Bluetooth X200', 'Eletrônicos', 2, 249.90, 150.00, 146.90),
         ('CAR-33W-01', 'Carregador Turbo 33W', 'Eletrônicos', 4, 97.55, 58.50, 57.30),
         ('CAD-EXE-PT', 'Cadeira giratória executiva', 'Mobiliário e Decoração', 2, 495.00, 297.00, 291.00)],
    3:  [('MOB-4001', 'Kit Escritório Completo', 'Mobiliário e Decoração', 1, 349.90, 199.90, 205.40)],
    4:  [('VES-2001', 'Camiseta Básica Algodão', 'Vestuário e Acessórios', 3, 39.90, 23.90, 23.50),
         ('PAP-3001', 'Caderno Universitário 200 folhas', 'Papelaria', 5, 18.50, 11.10, 10.90),
         ('VES-2002', 'Tênis Esportivo Runner', 'Vestuário e Acessórios', 2, 199.90, 120.00, 117.50)],
    8:  [('PAP-3001', 'Caderno Universitário 200 folhas', 'Papelaria', 4, 18.50, 11.30, 11.50),
         ('MOB-4001', 'Kit Escritório Completo', 'Mobiliário e Decoração', 1, 349.90, 213.30, 217.60),
         ('ELE-1003', 'Mouse Sem Fio Compacto', 'Eletrônicos', 2, 59.90, 36.50, 37.20),
         ('PAP-3002', 'Kit Papelaria Volta às Aulas', 'Papelaria', 3, 64.90, 39.50, 40.30)],
    9:  [('PAP-3001', 'Caderno Universitário 200 folhas', 'Papelaria', 3, 18.50, 10.90, 10.70),
         ('MOB-4002', 'Luminária de Mesa LED', 'Mobiliário e Decoração', 5, 79.90, 47.06, 46.08)],
    11: [('VES-2001', 'Camiseta Básica Algodão', 'Vestuário e Acessórios', 1, 39.90, 23.20, 23.80),
         ('ELE-1004', 'Carregador USB-C 20W', 'Eletrônicos', 4, 45.00, 26.20, 26.85)],
    12: [('VES-2002', 'Tênis Esportivo Runner', 'Vestuário e Acessórios', 3, 199.90, 118.00, 116.70),
         ('PAP-3002', 'Kit Papelaria Volta às Aulas', 'Papelaria', 4, 64.90, 38.20, 37.90),
         ('MOB-4003', 'Organizador de Mesa Bambu', 'Mobiliário e Decoração', 3, 54.90, 32.40, 32.10)],
    16: [('PAP-3001', 'Caderno Universitário 200 folhas', 'Papelaria', 6, 18.50, 11.30, 11.20),
         ('MOB-4001', 'Kit Escritório Completo', 'Mobiliário e Decoração', 5, 349.90, 213.80, 211.60),
         ('VES-2002', 'Tênis Esportivo Runner', 'Vestuário e Acessórios', 1, 199.90, 122.30, 120.80),
         ('ELE-1003', 'Mouse Sem Fio Compacto', 'Eletrônicos', 2, 59.90, 36.60, 36.20),
         ('MOB-4002', 'Luminária de Mesa LED', 'Mobiliário e Decoração', 2, 79.90, 48.85, 48.30)],
}
ONLINE = (1, 3, 4, 8, 9, 11, 12, 16)
VENDEDORA = {0: 5, 1: 0}                   # indice do vendedor -> aliquota (Marina Costa 5%, Rafael Andrade 0%); 2 = sem vendedor
CORTESIA_EXEMPLO = {3: 15, 10: 30, 16: 25}   # os usos de vale de origem cortesia no exemplo de Vale-compra (o 10 e manual: a conta online nao o olha)
# As devolucoes do exemplo da Logistica > Devolucao que a conta le (so os campos que ela usa). A vendaId e o pedido de venda de mesmo numero.
DEVOLUCOES = [
    {'id': 1, 'numero': 'DV-0012', 'vendaId': 2, 'abertaEm': '2026-10-06', 'situacao': 'aberta', 'itens': [('FER-2201', 2, 540.00, 'avaria')], 'reversa': None},
    {'id': 2, 'numero': 'DV-0011', 'vendaId': 1, 'abertaEm': '2026-10-03', 'situacao': 'andamento', 'itens': [('FON-BT-200', 1, 249.90, 'revendavel'), ('CAR-33W-01', 2, 97.55, 'revendavel')],
     'reversa': {'paga': 'cliente', 'valor': 24.50}},
    {'id': 3, 'numero': 'DV-0010', 'vendaId': 3, 'abertaEm': '2026-09-29', 'situacao': 'finalizada', 'itens': [('MOB-4001', 1, 349.90, 'avaria')], 'reversa': {'paga': 'nos', 'valor': 38.90}},
    {'id': 4, 'numero': 'DV-0009', 'vendaId': 4, 'abertaEm': '2026-10-06', 'situacao': 'aberta', 'itens': [('VES-2002', 1, 199.90, 'nenhum')], 'reversa': None},
    {'id': 5, 'numero': 'DV-0008', 'vendaId': 5, 'abertaEm': '2026-08-12', 'situacao': 'finalizada', 'itens': [('FLA-0301', 4, 1300.00, 'revendavel')], 'reversa': {'paga': 'nos', 'valor': 0}},
    {'id': 6, 'numero': 'DV-0007', 'vendaId': 3, 'abertaEm': '2026-09-22', 'situacao': 'cancelada', 'itens': [('MOB-4001', 1, 349.90, 'revendavel')], 'reversa': None},
]
ENTREGA = {1: '2026-09-30', 3: '2026-09-28', 4: '2026-10-05'}   # o entregaEm das vendas 1, 3 e 4 da Devolucao
ACEITAS = ('andamento', 'finalizada')


def iso(s):
    a = [int(x) for x in s.split('-')]
    return date(a[0], a[1], a[2])


def aceitas(pid, devolucoes=None, situacoes=ACEITAS):
    """As devolucoes do pedido online nas situacoes pedidas cujos itens existem todos no pedido."""
    itens = {i[0] for i in ITENS.get(pid, [])}
    if pid not in ONLINE:
        return []
    return [d for d in (DEVOLUCOES if devolucoes is None else devolucoes)
            if d['vendaId'] == pid and d['situacao'] in situacoes and d['itens'] and all(i[0] in itens for i in d['itens'])]


def valor_itens(d):
    return sum((D(q) * D(u) for _, q, u, _ in d['itens']), D(0))


def no_prazo(d, pid, prazo=7, entrega=None):
    ent = (entrega or ENTREGA).get(pid)
    return ent is not None and (iso(d['abertaEm']) - iso(ent)).days <= prazo


def conta_devolucao(pid, devs, base='compra', fator=None):
    """valor devolvido, custo que voltou (revendavel), perda (avariado ou perdido) e frete da volta pago pela loja. `fator` = (total - frete - cortesia) / (total - frete):
    a parte paga com vale de cortesia nao volta em dinheiro, entao o valor devolvido e a soma dos itens x fator (sem cortesia, fator None = a soma dos itens)."""
    custos = {i[0]: i for i in ITENS.get(pid, [])}
    dev = rec = perda = frete = D(0)
    for d in devs:
        dev += valor_itens(d)
        for sku, q, u, estado in d['itens']:
            cu = D(custos[sku][6] if base == 'medio' else custos[sku][5]) * q
            if estado == 'revendavel':
                rec += cu
            else:
                perda += cu
        r = d.get('reversa')
        if r and r.get('paga') == 'nos':
            frete += D(r['real'] if r.get('real') is not None else r['valor'])
    dev, rec, perda, frete = c2(dev * fator if fator is not None else dev), c2(rec), c2(perda), c2(frete)
    return dict(devolvido=dev, recuperado=rec, perda=perda, frete_volta=frete, devolucao=c2(dev - rec + frete))


def comissao_reduzida(bruta, base_comissao, devolvido):
    """comissao x (1 - valor devolvido / base da comissao), em centavos, meio para cima; voltou tudo, zero."""
    if not devolvido or base_comissao <= 0:
        return bruta
    return c2(bruta * max(D(0), base_comissao - devolvido) / base_comissao)


def oraculo(p, base='compra', emb=PADRAO_EMB, comissao=None, devolucoes=None, cortesia=None, prazo=7, entrega=None):
    """`comissao` (Decimal) troca a comissao do cadastro: as suites de Comissoes mudam o percentual e passam o valor que a tela deve usar.
    `devolucoes`: a lista de devolucoes (de fabrica, a do exemplo); `cortesia`: R$ do vale de cortesia usado no pedido (de fabrica, o do exemplo); `prazo` e `entrega`: o prazo
    de devolucao e a data de entrega de cada pedido (de fabrica, 7 dias e a ENTREGA do exemplo)."""
    total_, frete = D(p['total']), D(p.get('frete', 0))
    cort = D(CORTESIA_EXEMPLO.get(p['id'], 0) if cortesia is None else cortesia)
    venda = total_ - frete - cort
    dif = D(p['fretePagoLoja']) - frete if p.get('fretePagoLoja') is not None else D(0)
    taxa = D(0)
    pg = p.get('pagamento')
    if pg and pg['forma'] == 'credito':
        taxa = c2(c2(total_) * D(TAXAS_LINK[pg['vezes'] - 1]) / 100)
    pct = p['ind']['pct'] if p.get('ind') else VENDEDORA.get(p['vend'], 0)
    devs = aceitas(p['id'], devolucoes)
    if comissao is None:
        bruta = c2(c2(total_ - frete) * D(pct) / 100)
        no_p = [d for d in devs if no_prazo(d, p['id'], prazo, entrega)]
        comissao = comissao_reduzida(bruta, total_ - frete, sum((valor_itens(d) for d in no_p), D(0)))
    embalagem = c2(D(emb.get(p['loja'], 0)))   # uma por pedido
    custo = D(p['custoMedio'] if base == 'medio' else p['custo'])
    dv = conta_devolucao(p['id'], devs, base, (total_ - frete - cort) / (total_ - frete) if cort and total_ - frete > 0 else None)
    lucro = venda - dif - taxa - comissao - embalagem - custo - dv['devolucao']
    return dict(venda=venda, frete=frete, cortesia=cort, dif=dif, taxa=taxa, comissao=comissao, embalagem=embalagem, custo=custo, devolucao=dv['devolucao'], devolvido=dv['devolvido'],
                recuperado=dv['recuperado'], perda=dv['perda'], frete_volta=dv['frete_volta'], lucro=lucro, margem=(lucro / venda if venda else D(0)))


def repartir(valor, pesos):
    """O valor repartido em centavos, proporcional aos pesos: cada parte arredondada (meio para cima, no valor absoluto), a sobra de centavos na primeira."""
    c = int((abs(D(valor) * 100)).to_integral_value(rounding=ROUND_HALF_UP)) * (1 if valor >= 0 else -1)
    soma = sum(pesos)
    partes = [0] + [(1 if c >= 0 else -1) * int((abs(D(c) * w / soma)).to_integral_value(rounding=ROUND_HALF_UP)) for w in pesos[1:]]
    partes[0] = c - sum(partes)
    return [D(x) / 100 for x in partes]


def itens_do_pedido(p, r, base='compra'):
    """A repartição do pedido entre os itens (a tela de Custos agrupada por produto ou categoria): lista de (sku, categoria, parcelas)."""
    itens = ITENS[p['id']]
    val = [int((D(i[3]) * D(i[4]) * 100).to_integral_value(rounding=ROUND_HALF_UP)) for i in itens]
    cus = [int((D(i[3]) * D(i[6] if base == 'medio' else i[5]) * 100).to_integral_value(rounding=ROUND_HALF_UP)) for i in itens]
    por = dict(venda=repartir(r['venda'], val), freteCobrado=repartir(r['frete'], val), cortesia=repartir(r['cortesia'], val), difFrete=repartir(r['dif'], val),
               taxa=repartir(r['taxa'], val), comissao=repartir(r['comissao'], val), devolucao=repartir(r['devolucao'], val),
               embalagem=repartir(r['embalagem'], val), custo=repartir(r['custo'], cus))
    saida = []
    for n, i in enumerate(itens):
        x = {k: por[k][n] for k in por}
        x['lucro'] = x['venda'] - x['difFrete'] - x['taxa'] - x['comissao'] - x['embalagem'] - x['custo'] - x['devolucao']
        saida.append((i[0], i[2], x))
    return saida


# ---------------------------------------------------------------- entrega 3 (30/out/2026): anuncios, margem minima e mes a mes
# As contas da categoria 14 "Anuncios e midia paga" de Contas a Pagar, como a regra as le (venc = dias para tras a partir de hoje; loja 0 = empresa toda).
ANUNCIOS = [
    {'id': 14, 'loja': 1, 'valor': 180.00, 'venc': 2, 'cancelado': False},
    {'id': 15, 'loja': 1, 'valor': 120.00, 'venc': 4, 'cancelado': False},
    {'id': 16, 'loja': 2, 'valor': 90.00, 'venc': 3, 'cancelado': False},
    {'id': 17, 'loja': 0, 'valor': 60.00, 'venc': 1, 'cancelado': False},
    {'id': 18, 'loja': 1, 'valor': 500.00, 'venc': 5, 'cancelado': True},
    {'id': 19, 'loja': 1, 'valor': 150.00, 'venc': 40, 'cancelado': False},
]


def anuncios_do_periodo(hoje, de, ate, loja=None, contas=None):
    """Soma do valor das contas da categoria 14 nao canceladas, com vencimento entre `de` e `ate` (datas), pagas ou nao. `loja` (1, 2, 3) so as daquela loja;
    sem `loja` (Todas as lojas) entram tambem as contas sem loja."""
    from datetime import timedelta
    soma = D(0)
    for c in (ANUNCIOS if contas is None else contas):
        if c['cancelado']:
            continue
        v = hoje - timedelta(days=c['venc'])
        if not (de <= v <= ate):
            continue
        if loja is not None and c['loja'] != loja:
            continue
        soma += D(c['valor'])
    return soma


def abaixo_da_margem(o, minima):
    """Pedido abaixo da margem: lucro negativo, ou lucro/venda menor que a minima (em %)."""
    return o['lucro'] < 0 or (o['venda'] > 0 and o['lucro'] * 100 < o['venda'] * D(minima))


# Os 5 meses anteriores do grafico (exemplo): deslocamento em meses -> loja -> (faturamento, lucro).
MESES_EXEMPLO = {
    -1: {1: (6120.00, 735.00), 2: (2310.00, 392.70)},
    -2: {1: (5240.00, 576.40), 2: (1980.00, 316.80)},
    -3: {1: (4710.00, 518.10), 2: (1750.00, 245.00)},
    -4: {1: (5560.00, 667.20), 2: (2240.00, 336.00)},
    -5: {1: (3980.00, 358.20), 2: (1420.00, 184.60)},
}
SITUACOES_FABRICA = ('aberto', 'aprovado', 'separacao', 'conferenciasaida', 'faturado', 'prontoenvio', 'enviado', 'entregue')


def meses_do_grafico(hoje, pedidos, loja=None, base='compra', situacoes=SITUACOES_FABRICA, exemplo=None):
    """Os 6 ultimos meses terminando no mes de `hoje`: [((ano, mes), faturamento, lucro)]. O exemplo (so os 5 anteriores) por loja, mais os pedidos online das
    situacoes escolhidas cuja venda (hoje menos `dv` dias) cai no mes. Respeita so a loja, as situacoes e a base de custo."""
    from datetime import timedelta
    ex = MESES_EXEMPLO if exemplo is None else exemplo
    meses = []
    for k in range(5, -1, -1):
        m0 = hoje.year * 12 + hoje.month - 1 - k
        meses.append((m0 // 12, m0 % 12 + 1, -k))
    saida = []
    for ano, mes, desloc in meses:
        fat = lucro = D(0)
        for l, (f, lu) in ex.get(desloc, {}).items():
            if loja is None or l == loja:
                fat += D(f); lucro += D(lu)
        for p in pedidos:
            if p.get('canal') != 'loja_virtual' or p['situacao'] not in situacoes or (loja is not None and p['loja'] != loja):
                continue
            d = hoje - timedelta(days=p['dv'])
            if (d.year, d.month) == (ano, mes):
                o = oraculo(p, base)
                fat += o['venda']; lucro += o['lucro']
        saida.append(((ano, mes), fat, lucro))
    return saida
