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
# Os online (1, 3, 4, 8, 9, 11, 12, 16) fecham no total (itens mais frete), na soma do custo e na do custo medio; 2, 6 e 10 sao manuais e so entram nas unidades.
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
UNIDADES = {1: 8, 2: 23, 3: 1, 4: 10, 6: 14, 8: 10, 9: 8, 10: 32, 11: 5, 12: 10, 16: 16}   # soma das quantidades dos itens (os manuais 2, 6 e 10 trazem `unidades`; sem itens, 1)
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


def conta_devolucao(pid, devs, base='compra'):
    """valor devolvido, custo que voltou (revendavel), perda (avariado ou perdido) e frete da volta pago pela loja."""
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
    dev, rec, perda, frete = c2(dev), c2(rec), c2(perda), c2(frete)
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
    unidades = sum(i[3] for i in ITENS[p['id']]) if p['id'] in ONLINE else UNIDADES.get(p['id'], 1)
    embalagem = c2(D(emb.get(p['loja'], 0)) * unidades)
    custo = D(p['custoMedio'] if base == 'medio' else p['custo'])
    dv = conta_devolucao(p['id'], devs, base)
    lucro = venda - dif - taxa - comissao - embalagem - custo - dv['devolucao']
    return dict(venda=venda, frete=frete, cortesia=cort, dif=dif, taxa=taxa, comissao=comissao, embalagem=embalagem, custo=custo, devolucao=dv['devolucao'], devolvido=dv['devolvido'],
                recuperado=dv['recuperado'], perda=dv['perda'], frete_volta=dv['frete_volta'], lucro=lucro, margem=(lucro / venda if venda else D(0)), unidades=unidades)


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
    qtd = [i[3] for i in itens]
    cus = [int((D(i[3]) * D(i[6] if base == 'medio' else i[5]) * 100).to_integral_value(rounding=ROUND_HALF_UP)) for i in itens]
    por = dict(venda=repartir(r['venda'], val), freteCobrado=repartir(r['frete'], val), cortesia=repartir(r['cortesia'], val), difFrete=repartir(r['dif'], val),
               taxa=repartir(r['taxa'], val), comissao=repartir(r['comissao'], val), devolucao=repartir(r['devolucao'], val),
               embalagem=repartir(r['embalagem'], qtd), custo=repartir(r['custo'], cus))
    saida = []
    for n, i in enumerate(itens):
        x = {k: por[k][n] for k in por}
        x['lucro'] = x['venda'] - x['difFrete'] - x['taxa'] - x['comissao'] - x['embalagem'] - x['custo'] - x['devolucao']
        saida.append((i[0], i[2], x))
    return saida
