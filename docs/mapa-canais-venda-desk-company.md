# Mapa dos canais de venda da Desk Company

*Proposta de 10/nov/2026, para o usuário aprovar. Item 1 da fila do PROGRESSO. Depois de aprovada, este arquivo é a fonte
de quem vende onde, com que preço e com que desconto. Usuários do sistema, Permissões de Usuários e o pacote do gerente na
promoção são construídos a partir dele.*

## A ideia em uma frase

**O canal é de onde a venda veio, não uma tela nova.** São poucas telas, e cada venda leva o nome do canal dela. Exemplos:
o PDV atende o balcão e a feira, e o Pedido de Venda atende o escritório, o WhatsApp, o telefone, o representante e o atacado.
Os canais online chegam sozinhos, pelas integrações.

Os sistemas grandes fazem assim. O Dynamics 365, da Microsoft, separa a venda em loja física, central de atendimento e
loja online, e as três usam a mesma regra de preço. O Olist marca a origem do pedido conforme a integração.

## Os canais

| # | canal | onde a venda nasce | quem vende | desconto na mão | de onde vem o preço | a promoção vale? | tela no ERP | hoje |
|---|---|---|---|---|---|---|---|---|
| 1 | **Balcão da loja física** | o computador do caixa | caixa, vendedor de balcão | até o limite da pessoa; acima, o gerente | cadastro do produto | sim, se marcar "PDV" | PDV | **existe** |
| 2 | **Escritório** | pedido montado por quem está no sistema | você, gerente, supervisor | até o limite da pessoa; acima, o gerente | cadastro do produto | sim, se marcar "vendedores" | Pedido de Venda | **existe** (sem limite de desconto) |
| 3 | **Loja virtual** (as vitrines de cada loja) | o cliente, sozinho, no site | ninguém | não tem; só cupom, se um dia existir | cadastro, com o riscado da promoção | sim, se marcar "vitrine" | vitrine e integração | **protótipo na fila** |
| 4 | **Afiliados** | o link do afiliado, que cai na loja virtual | o afiliado divulga | não mexe no preço | o da loja virtual | sim, igual à loja virtual | loja virtual e Comissões | **existe** (comissão) |
| 5 | **WhatsApp e redes sociais** (Instagram, catálogo do WhatsApp) | conversa com o cliente | vendedor interno | até o limite da pessoa | cadastro | sim, se marcar o canal | Pedido de Venda, com link de pagamento | novo |
| 6 | **Televendas** (telefone, ativo e receptivo) | ligação | vendedor interno | até o limite da pessoa | cadastro | sim, se marcar o canal | Pedido de Venda | novo |
| 7 | **Vendedor externo / representante** | visita ao cliente, pelo celular | representante | até o limite da pessoa | cadastro, ou a tabela dele | sim, se marcar o canal | Pedido de Venda na versão celular | novo |
| 8 | **Atacado para empresas e revenda** | pedido de cliente com CNPJ | supervisor, vendedor interno, representante | não; o desconto vem da tabela de atacado; condição especial só com o gerente | **tabela de atacado** (preço por quantidade) | só se a promoção marcar "atacado" | Pedido de Venda | novo |
| 9 | **Marketplaces** (Mercado Livre, Shopee, Amazon, Magalu, Shein, TikTok Shop) | o site do marketplace | o marketplace | não; a promoção do marketplace é dele | **preço do marketplace** = cadastro + as taxas dele (a calculadora já conta) | não: cada marketplace tem a sua | Integrações → Marketplaces | novo (sem tela) |
| 10 | **Evento, feira e loja temporária** | um caixa montado fora da loja | caixa, vendedor | até o limite da pessoa | cadastro | sim, se marcar "PDV" | PDV, aberto num ponto de venda "evento" | novo |
| 11 | **Live e venda pelo vídeo** (live no Instagram, TikTok) | a live | a loja; o cliente fecha pelo link | não | cadastro, ou o do marketplace (TikTok Shop) | conforme o lugar onde fecha | loja virtual ou marketplace | depois |

**Ficam para depois, só anotados:** franquia, revenda com loja própria, venda para funcionário, totem de autoatendimento e
assinatura (cliente que compra todo mês). Cada um entra no mapa no dia em que existir.

## A escada do preço (vale em todo canal)

Do mais geral ao mais específico. Cada degrau só existe onde o canal deixa.

1. **O preço do cadastro.** O cadastro do produto é o único dono do preço (decisão de 04/nov).
2. **A tabela do canal**, quando o canal tem a sua: atacado (por quantidade) e marketplace (o cadastro mais as taxas).
   Os outros canais usam o preço do cadastro.
3. **A promoção**, onde ela foi marcada. Hoje a promoção marca vitrine, PDV ou vendedores; com o mapa, marca a lista de canais.
4. **O desconto na mão**, até o limite de quem vende.
5. **O gerente**, com senha, acima do limite: desconto maior, preço promocional fora da promoção, excedente do limite por cliente.
6. **A trava do mínimo da calculadora**, que nem o gerente passa. Vender abaixo do mínimo de propósito vai pela revisão de preço.

## Os perfis que saem do mapa

Estes perfis são a base de Usuários do sistema e Permissões de Usuários (item 2 da fila).

| perfil | onde vende | desconto sem senha | o que só ele faz |
|---|---|---|---|
| **Usuário mestre** (você) | todos | sem limite | define os perfis, os limites de cada pessoa e quem é gerente |
| **Gerente** | todos | o limite dele | autoriza com senha: desconto acima do limite, preço promocional fora da promoção, excedente da promoção, condição especial no atacado |
| **Supervisor de vendas** | escritório, atacado, WhatsApp, televendas | o limite dele | acompanha a equipe (metas, CRM); não autoriza o que é do gerente, a não ser que o mestre dê |
| **Vendedor interno** | escritório, WhatsApp, televendas, atacado | o limite dele | vende; nas promoções, só o preço que elas dão |
| **Caixa / vendedor de balcão** | balcão, evento | o limite dele (o padrão é o de Configurações → PDV, hoje 10%) | abre e fecha o caixa |
| **Representante externo** | visita ao cliente, atacado | o limite dele | vende fora da loja, pelo celular |
| **Afiliado** | não entra no ERP | não tem | divulga o link e recebe comissão |

O limite de cada pessoa fica no cadastro dela, e só o usuário mestre altera. Quem não tem limite próprio fica com o padrão
de Configurações → PDV. O limite vale igual em toda tela: o que muda o limite é a pessoa, não o canal (decisão de 10/nov).
Sistemas de referência: o Erply e o Lightspeed põem "desconto máximo %" no grupo de usuários, e o Shopify deixa cada
permissão como "permitido", "negado" ou "pede o PIN do gerente".

## O que muda no que já existe

- **Toda venda ganha o campo "Canal"**, obrigatório no Pedido de Venda e automático no PDV, nas vitrines e nos marketplaces.
  Os pedidos de hoje se dividem só em "manual" e "loja virtual"; o campo novo dá o nome certo a cada venda. Com ele, os
  relatórios e as metas conseguem mostrar quanto vendeu cada canal.
- **A promoção passa a marcar a lista de canais**, em vez das três opções de hoje (vitrine, PDV, vendedores). As promoções de
  exemplo ficam com o mesmo efeito: "vendedores" vira escritório, WhatsApp, televendas e externo.
- **O Pedido de Venda ganha o limite de desconto da pessoa**, que hoje ele não tem.

## Para decidir na aprovação

1. **O canal vira um campo obrigatório no Pedido de Venda?** A proposta é sim, porque sem ele não dá para medir os canais.
2. **O representante externo usa o próprio Pedido de Venda no celular?** A proposta é sim, por enquanto. Um aplicativo próprio,
   que funcione sem internet, fica para a produção.
3. **O atacado ganha uma tabela de preço própria**, com preço por quantidade e só para cliente com CNPJ? A proposta é anotar
   agora e construir quando o atacado começar.
4. **O supervisor autoriza o que o gerente autoriza?** A proposta é não, salvo se o usuário mestre der a ele essa permissão.

## Ordem de construção (já na fila do PROGRESSO)

1. Este mapa, aprovado.
2. **Usuários do sistema e Permissões de Usuários:** os perfis acima, o limite por pessoa e "quem pode" cada ação.
3. **O pacote do gerente na promoção**, lendo as permissões de verdade.
4. Depois, quando cada canal começar: o campo "Canal" e a lista de canais na promoção, a tabela de atacado e Integrações →
   Marketplaces.

## Fontes da pesquisa (10/nov/2026)

- Olist ERP: não tem tela de mapa de canais; o canal vem da integração.
  [Integração Olist e Tiny](https://olist.com/blog/pt/olist/olist-news/integracao-olist-e-tiny-2)
- Omie: o campo "Origem" do pedido diz o canal. [Omie Hub](https://ajuda.omie.com.br/pt-BR/articles/10206157-gerenciando-pedidos-no-omie-hub)
- Bluesoft: os canais de venda são um cadastro, opcional no pedido. [Guia do Pedido de Venda](https://ajuda.bluesoft.com.br/wp-content/uploads/2015/12/Guia-de-Implantação-Pedido-de-Venda.pdf)
- Microsoft Dynamics 365 Commerce: os canais são loja física, central de atendimento e online. [Visão geral dos canais](https://learn.microsoft.com/en-us/dynamics365/commerce/channel-setup-retail)
- Shopify POS: os papéis da equipe; o desconto pode ser permitido, negado ou pedir o PIN do gerente. [POS roles](https://help.shopify.com/en/manual/sell-in-person/shopify-pos/staff-management/pos-roles)
- Erply: "desconto máximo %" por grupo de usuários. [Role settings](https://wiki.erply.com/article/2335-role-settings)
- Senior e Alterdata: perfil de desconto e perfil de usuário; o desconto do representante conferido contra a tabela.
  [Senior: desconto máximo do representante](https://documentacao.senior.com.br/venda-mais/manual-do-usuario/representante/percentual-maximo-de-desconto-permitido),
  [Alterdata: perfil de usuários](https://ajuda.alterdata.com.br/retaguarda/cadastro-geral-retaguarda/perfil-de-usuarios)
- Gestão Plus: perfil de desconto ligado ao vendedor. [Perfil de desconto](https://docs.gestao.plus/erp-v2/funcionalidades/usuarios_vendedores/perfil_desconto)
