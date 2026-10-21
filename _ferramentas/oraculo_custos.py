# -*- coding: utf-8 -*-
# A conta do lucro de um pedido (Custos do E-commerce, 21/out/2026), refeita em Python com Decimal e meio para cima, sem
# olhar o codigo da tela: o oraculo que as suites de Custos do E-commerce e de Comissoes usam para conferir o JavaScript.
from decimal import Decimal, ROUND_HALF_UP

D = lambda x: Decimal(str(x))
c2 = lambda x: x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
TAXAS_LINK = [4.20, 6.09, 7.01, 7.91, 8.80, 9.67, 12.59, 13.42, 14.25, 15.06, 15.87, 16.66]   # InfinitePay, Link de pagamento, 1x a 12x
PADRAO_EMB = {1: 5, 2: 8, 3: 0}
UNIDADES = {1: 8, 2: 23, 6: 14, 10: 32}   # soma das quantidades dos itens do exemplo (ITENS_PEDIDO)
VENDEDORA = {0: 5, 1: 0}                   # indice do vendedor -> aliquota (Marina Costa 5%, Rafael Andrade 0%); 2 = sem vendedor


def oraculo(p, base='compra', emb=PADRAO_EMB, comissao=None):
    """`comissao` (Decimal) troca a comissao do cadastro: as suites de Comissoes mudam o percentual e passam o valor que a tela deve usar."""
    total_, frete = D(p['total']), D(p.get('frete', 0))
    venda = total_ - frete
    dif = D(p['fretePagoLoja']) - frete if p.get('fretePagoLoja') is not None else D(0)
    taxa = D(0)
    pg = p.get('pagamento')
    if pg and pg['forma'] == 'credito':
        taxa = c2(c2(total_) * D(TAXAS_LINK[pg['vezes'] - 1]) / 100)
    pct = p['ind']['pct'] if p.get('ind') else VENDEDORA.get(p['vend'], 0)
    if comissao is None:
        comissao = c2(c2(venda) * D(pct) / 100)
    embalagem = c2(D(emb.get(p['loja'], 0)) * UNIDADES.get(p['id'], 1))
    custo = D(p['custoMedio'] if base == 'medio' else p['custo'])
    lucro = venda - dif - taxa - comissao - embalagem - custo
    return dict(venda=venda, frete=frete, dif=dif, taxa=taxa, comissao=comissao, embalagem=embalagem, custo=custo, lucro=lucro,
                margem=(lucro / venda if venda else D(0)))
