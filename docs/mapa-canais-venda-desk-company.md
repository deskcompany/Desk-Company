# Mapa dos canais de venda da Desk Company

*Aprovado pelo usuário em 10/nov/2026 (proposta e respostas no mesmo dia). É a fonte de quem vende onde, com que preço e
com que desconto. Usuários do sistema, Permissões de Usuários e o pacote do gerente na promoção são construídos a partir dele.*

## A ideia em uma frase

**O canal é de onde a venda veio, não uma tela nova.** São poucas telas, e cada venda leva o nome do canal dela. Exemplos:
o PDV atende o balcão e a feira, e o Pedido de Venda atende o escritório, o WhatsApp, o telefone, o representante e o atacado.
Os canais online chegam sozinhos, pelas integrações.

O usuário confirmou essa linha ("manter o mínimo de telas possíveis"). WhatsApp, redes sociais e televendas sempre levam o
cliente a um de dois lugares. Ou ele vai para o **site** (a loja virtual), ou fala com **um vendedor nosso**, e o vendedor
fecha a venda dentro do sistema, no Pedido de Venda. Nenhum desses canais ganha tela própria.

Os sistemas grandes fazem assim. O Dynamics 365, da Microsoft, separa a venda em loja física, central de atendimento e
loja online, e as três usam a mesma regra de preço. O Olist marca a origem do pedido conforme a integração.

## Os canais

| # | canal | onde a venda nasce | quem vende | desconto na mão | de onde vem o preço | a promoção vale? | tela no ERP | hoje |
|---|---|---|---|---|---|---|---|---|
| 1 | **Balcão da loja física** | o computador do caixa | caixa, vendedor de balcão | até o limite da pessoa; acima, o gerente | cadastro do produto | sim, se marcar "PDV" | PDV | **existe** |
| 2 | **Escritório** | pedido montado por quem está no sistema | Owner, gerente, supervisor | até o limite da pessoa; acima, o gerente | cadastro do produto | sim, se marcar "vendedores" | Pedido de Venda | **existe** (sem limite de desconto) |
| 3 | **Loja virtual** (as vitrines de cada loja) | o cliente, sozinho, no site | ninguém | não tem; só cupom, se um dia existir | cadastro, com o riscado da promoção | sim, se marcar "vitrine" | vitrine e integração | **protótipo na fila** |
| 4 | **Afiliados** | o link do afiliado, que cai na loja virtual | o afiliado divulga | não mexe no preço | o da loja virtual | sim, igual à loja virtual | loja virtual e Comissões | **existe** (comissão) |
| 5 | **WhatsApp e redes sociais** (Instagram, catálogo do WhatsApp) | conversa com o cliente; a rede social leva ao site ou ao vendedor | vendedor interno | até o limite da pessoa | cadastro | sim, se marcar o canal | Pedido de Venda, com link de pagamento (ou a loja virtual, se o cliente fecha no site) | novo |
| 6 | **Televendas** (telefone, ativo e receptivo) | ligação | vendedor interno | até o limite da pessoa | cadastro | sim, se marcar o canal | Pedido de Venda | novo |
| 7 | **Vendedor externo / representante** | visita ao cliente, pelo celular | representante | até o limite da pessoa | cadastro (e o de atacado, a partir da quantidade) | sim, se marcar o canal | hoje, o Pedido de Venda no celular; na produção, o aplicativo de vendas que funciona sem internet | novo |
| 8 | **Atacado** (empresa ou pessoa física) | pedido acima da quantidade mínima de atacado | supervisor, vendedor interno, representante | não; o desconto é o próprio preço de atacado; condição especial só com o gerente | **preço de atacado do cadastro**, a partir da quantidade mínima | só se a promoção marcar "atacado" | Pedido de Venda | novo |
| 9 | **Marketplaces** (Mercado Livre, Shopee, Amazon, Magalu, Shein, TikTok Shop) | o site do marketplace | o marketplace | não; a promoção do marketplace é dele | **preço do marketplace** = cadastro + as taxas dele (a calculadora já conta) | não: cada marketplace tem a sua | Integrações → Marketplaces | novo (sem tela) |
| 10 | **Evento, feira e loja temporária** | um caixa montado fora da loja | caixa, vendedor | até o limite da pessoa | cadastro | sim, se marcar "PDV" | PDV, aberto num ponto de venda "evento" | novo |
| 11 | **Live e venda pelo vídeo** (live no Instagram, TikTok) | a live | a loja; o cliente fecha pelo link | não | cadastro, ou o do marketplace (TikTok Shop) | conforme o lugar onde fecha | loja virtual ou marketplace | depois |

**Ficam para depois, só anotados:** franquia, revenda com loja própria, venda para funcionário, totem de autoatendimento e
assinatura (cliente que compra todo mês). Cada um entra no mapa no dia em que existir.

## A escada do preço (vale em todo canal)

Do mais geral ao mais específico. Cada degrau só existe onde o canal deixa.

1. **O preço do cadastro.** O cadastro do produto é o único dono do preço (decisão de 04/nov).
2. **O preço do canal**, quando o canal tem o seu: o de atacado (do cadastro, a partir da quantidade mínima) e o do marketplace
   (o cadastro mais as taxas). Os outros canais usam o preço de venda do cadastro.
3. **A promoção**, onde ela foi marcada. Hoje a promoção marca vitrine, PDV ou vendedores; com o mapa, marca a lista de canais.
4. **O desconto na mão**, até o limite de quem vende.
5. **O gerente**, com senha, acima do limite: desconto maior, preço promocional fora da promoção, excedente do limite por cliente.
6. **A trava do mínimo da calculadora**, que nem o gerente passa. Vender abaixo do mínimo de propósito vai pela revisão de preço.

## O preço de atacado (resposta do usuário, 10/nov)

- **Mora no cadastro do produto**, na aba Preços, logo abaixo do preço de venda e do promocional: um campo **"Preço de atacado"**
  com **"a partir de N unidades"**. Exemplo: de 12 unidades em diante, cada peça sai por R$ X.
- **Vende para empresa e para pessoa física.** A pessoa física também compra no atacado, desde que assuma os impostos da venda de
  atacado, como a empresa. *Como o imposto entra na nota fica para o módulo de Notas Fiscais, com o contador.*
- **No pedido**, a quantidade decide: chegou ao mínimo, o preço da linha vira o de atacado sozinho. Abaixo do mínimo, vale o
  preço de venda.
- **O preço de atacado também passa pela trava do mínimo da calculadora**, como o promocional.
- **Atacado é atacado** (resposta do usuário, 10/nov). A promoção mexe só no preço de venda e não encosta no atacado: a linha que
  chegou à quantidade mínima fica no preço de atacado, com promoção ativa ou não. No fechamento do pedido, quem tem permissão
  ainda pode dar um desconto (10%, 5%, 2%...) até o limite dele, como em qualquer venda.

## Os perfis que saem do mapa

Estes perfis são a base de Usuários do sistema e Permissões de Usuários (item 2 da fila). São o começo: **outros tipos de
usuário serão cadastrados conforme a empresa crescer**, e por isso o perfil é um cadastro, não uma lista fixa no código.

| perfil | onde vende | desconto sem senha | o que só ele faz |
|---|---|---|---|
| **Owner** (você; no código, o perfil `Owner` que já existe) | todos | sem limite | define os perfis, os limites de cada pessoa e o que cada um pode fazer |
| **Gerente** | todos | o limite dele | autoriza com senha: desconto acima do limite, preço promocional fora da promoção, excedente da promoção, condição especial no atacado |
| **Supervisor de vendas** | escritório, atacado, WhatsApp, televendas | o limite dele (pode ser maior que o do vendedor) | acompanha a equipe (metas, CRM); só autoriza o que o perfil dele permite, e o resto fica com o gerente ou o Owner |
| **Vendedor interno** | escritório, WhatsApp, televendas, atacado | o limite dele | vende; nas promoções, só o preço que elas dão |
| **Caixa / vendedor de balcão** | balcão, evento | o limite dele (o padrão é o de Configurações → PDV, hoje 10%) | abre e fecha o caixa |
| **Representante externo** | visita ao cliente, atacado | o limite dele | vende fora da loja, pelo celular |
| **Afiliado** | não entra no ERP | não tem | divulga o link e recebe comissão |

O limite de cada pessoa fica no cadastro dela, e só o Owner altera. Quem não tem limite próprio fica com o padrão de
Configurações → PDV. O limite vale igual em toda tela: o que muda o limite é a pessoa, não o canal (decisão de 10/nov).
**Cada perfil faz só o que o Owner liberou para ele.** O gerente vem com mais permissões de fábrica, mas o Owner pode tirar
ou dar qualquer uma, a qualquer perfil.
Sistemas de referência: o Erply e o Lightspeed põem "desconto máximo %" no grupo de usuários, e o Shopify deixa cada
permissão como "permitido", "negado" ou "pede o PIN do gerente".

## O que muda no que já existe

- **Toda venda ganha o campo "Canal"**, obrigatório no Pedido de Venda (aprovado em 10/nov) e automático no PDV, nas vitrines e
  nos marketplaces. Os pedidos de hoje se dividem só em "manual" e "loja virtual"; o campo novo dá o nome certo a cada venda.
  Com ele, os relatórios e as metas conseguem mostrar quanto vendeu cada canal.
- **A promoção passa a marcar a lista de canais**, em vez das três opções de hoje (vitrine, PDV, vendedores). As promoções de
  exemplo ficam com o mesmo efeito: "vendedores" vira escritório, WhatsApp, televendas e externo.
- **O Pedido de Venda ganha o limite de desconto da pessoa**, que hoje ele não tem.
- **A ficha do produto ganha o preço de atacado** com a quantidade mínima, na aba Preços.

## O aplicativo de vendas do representante (resposta do usuário, 10/nov; vem na produção)

Por enquanto o representante usa o Pedido de Venda pelo celular. Na produção, ele ganha um **aplicativo de vendas**:

- **Entra com o mesmo usuário** do sistema, com o mesmo perfil e os mesmos limites.
- **Baixa os produtos, os preços e o estoque** e vai atualizando enquanto tem internet.
- **Sem internet, continua vendendo:** monta o pedido e o guarda no celular.
- **Quando a internet volta, o sistema confere o pedido:** o produto que acabou no estoque, o preço que mudou, o desconto acima do
  limite. O que saiu do padrão volta para o representante revisar e corrigir, e ele explica ao cliente antes de confirmar.

## As respostas da aprovação (10/nov/2026)

1. **O canal é obrigatório no Pedido de Venda.** Sim.
2. **O representante externo** usa o Pedido de Venda no celular por enquanto. O aplicativo de vendas sem internet vem na
   produção, como descrito acima.
3. **O atacado** não tem tabela à parte: o preço de atacado é um campo do cadastro do produto, com a quantidade mínima, e vale
   para empresa e para pessoa física que assuma os impostos.
4. **O supervisor** só autoriza o que o perfil dele permite. Pode ter um limite de desconto maior que o do vendedor, mas o resto
   fica com o gerente ou o Owner, que define o que cada usuário pode fazer.
5. **O perfil "Usuário mestre" se chama Owner.** Os perfis da tabela são a base para começar; outros virão.

## Ordem de construção (na fila do PROGRESSO)

1. ~~Este mapa, aprovado.~~ Feito em 10/nov/2026.
2. **Usuários do sistema e Permissões de Usuários:** os perfis acima (como cadastro), o limite por pessoa e "quem pode" cada ação.
3. **O pacote do gerente na promoção**, lendo as permissões de verdade.
4. **O preço de atacado** no cadastro do produto e no Pedido de Venda.
5. Depois, quando cada canal começar: o campo "Canal" e a lista de canais na promoção, e Integrações → Marketplaces. O
   aplicativo de vendas do representante vem na produção.

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
