# Plano: o preço de atacado (16/nov/2026)

Item 1 da fila do PROGRESSO. Regras de produto em `docs/mapa-canais-venda-desk-company.md`, seção "O preço de atacado"
(respostas do usuário em 10/nov). Barganha fechada em 16/nov com duas respostas dele:

- **Vale no Pedido de Venda e no PDV.** Chegou à quantidade mínima, o preço vira o de atacado sozinho nas duas telas.
- **Na linha: a etiqueta e o aviso do que falta.** Na quantidade mínima, a etiqueta "Atacado" com "a partir de N un.";
  abaixo dela, um aviso discreto "faltam N para o atacado (R$ X cada)", para o vendedor oferecer.

O Pedido de Venda não tem o campo "canal" ainda: quem decide é só a quantidade, em qualquer venda.

## 1. Onde o preço mora

- `deskPrecoProduto[id]` (o mesmo registro do preço de venda e do promocional) ganha `atacado` (número ou null) e
  `atacadoMin` (inteiro ou null). Os dois existem juntos ou nenhum.
- `promoPrecos(id)` (bloco PROMOCOES, igual nas 5 telas que o têm: promocoes, promocoes-detalhe, produtos-detalhe, pdv,
  pedidos-detalhe) passa a devolver também `atacado` e `atacadoMin`, com a semente `PROMO_ATACADO_PADRAO` (no mesmo bloco)
  quando o produto não tem nada gravado.
- Novo no mesmo bloco: `promoAtacado(sku)` devolve `{ preco, min }` ou null (sem atacado, produto fora do catálogo, ou
  atacado abaixo do mínimo da calculadora `promoMinimoCent`, que é a trava: atacado travado não entra na venda).
- O histórico do preço (`deskHistoricoPreco`, `promoGravarPreco`) registra também `atacado` e `atacadoMin`; a tabela do
  histórico na ficha mostra "Atacado" e "Atacado a partir de".
- **Semente** (para o teste e para a demonstração): o Caderno Universitário (PAP-3001, id 3) a partir de 12 unidades, e
  o produto da promoção ativa "Volta às aulas" (PAP-3002) a partir de 10 unidades. O preço de cada um: abaixo do preço de
  venda, abaixo do promocional (no PAP-3002) e **acima do mínimo da calculadora** (confira o mínimo antes de escolher).
  O bloco PROMOCOES continua idêntico nas 5 telas depois da mudança (script por texto exato).

## 2. A ficha do produto (`telas/cadastros/pagina-cadastros-produtos-detalhe.html`, aba Preços)

- **Sai a seção "Preço por lista"** (título, texto e os campos Padrão, Atacado e Varejo): é resto de clonagem e contraria
  a decisão de 30/set (sem lista de preço). Sai junto o código que copia o preço de venda para `#inputPrecoListaPadrao`.
- **Entra, logo abaixo da linha "Preço de venda / Preço promocional"**, uma linha com dois campos:
  - "Preço de atacado": `#inputPrecoAtacado`, máscara de dinheiro, placeholder `0,00`.
  - "A partir de": `#inputAtacadoMin`, quantidade inteira (`type="text" inputmode="numeric"`, nunca `type=number`), com
    "unidades" ao lado, no padrão de campo com sufixo da tela.
  - Texto curto embaixo: "A partir dessa quantidade do produto na venda, no PDV e no Pedido de Venda, cada peça sai por
    este preço. A promoção não mexe no atacado."
- **A trava ao salvar**, no mesmo lugar e no mesmo jeito em que o promocional é conferido hoje (erro no campo, não alert):
  - os dois campos juntos ou os dois vazios ("Informe o preço e a quantidade, ou deixe os dois vazios.");
  - a quantidade é inteira e de 2 para cima;
  - o preço de atacado é menor que o preço de venda;
  - o preço de atacado não fica abaixo do mínimo da calculadora; sem custo no cadastro, a mesma mensagem do promocional.
  - Apagar os dois tira o atacado do produto (grava null e a linha do histórico).

## 3. A venda (`pagina-vendas-pdv.html` e `pagina-vendas-pedidos-detalhe.html`)

- **A quantidade que conta é a do produto na venda inteira**: a soma de todas as linhas do mesmo SKU (a linha da
  promoção, a do excedente e a normal, se houver).
- **Chegou ao mínimo:** todas as linhas daquele SKU passam ao preço de atacado; se a venda tinha linhas separadas pela
  promoção ou pelo excedente, elas se juntam numa linha só (o atacado não divide). A linha fica com `atacado: true`,
  `precoOriginal` = o preço de venda, sem `promocao`, sem `naHora` e sem `excedente`. **Atacado é atacado:** com promoção
  ativa ou não, o preço é o de atacado, e a promoção não conta uso para essas peças (o uso em `deskPromoUsos` sai só das
  linhas com `promocao`).
- **Caiu abaixo do mínimo** (diminuiu a quantidade ou tirou uma linha): o produto volta ao caminho de hoje, como se
  tivesse acabado de entrar (o preço de venda, a promoção onde ela vale, e o que já existe para o limite dela).
- O desconto na mão continua valendo por cima do preço de atacado, até o limite de quem vende. **O preço de atacado não
  é desconto:** ele nunca dispara a liberação "desconto acima do máximo", nem no item nem na venda. Confira como cada
  tela calcula o percentual e garanta isso (se o cálculo usar `precoOriginal`, a base da linha de atacado é o atacado).
- Nas linhas de atacado não aparecem os botões "Aplicar preço promocional" nem "Aplicar preço promocional no excedente".
- **A etiqueta**, no lugar onde hoje fica a da promoção (na lista dos itens e no painel do item), com a classe
  `promo-tag` que já existe: selo "Atacado" e o texto "a partir de N un.".
- **O aviso do que falta**, no mesmo lugar, quando o produto tem atacado e a quantidade na venda está abaixo do mínimo:
  "faltam N para o atacado (R$ X cada)", no estilo de texto secundário da tela (sem cor de alerta).
- O que a venda grava (o pedido, o cupom do PDV, a linha do item) leva `atacado: true` nas linhas de atacado. Pedido
  salvo reabre com o preço que foi gravado, e só recalcula quando alguém mexer na quantidade.
- Se as duas telas precisarem da mesma função nova fora do bloco PROMOCOES, ela vai num bloco comum, igual nas duas.

## 4. Os testes

- **Suíte nova `_ferramentas/teste_atacado.py`**, no estilo das outras (Playwright, `ok(...)`, `DESK_PASTA`):
  - ficha: a seção antiga não existe; salvar preço e quantidade grava e cria as duas linhas do histórico; cada uma das
    travas da seção 2 recusa com a mensagem; apagar os dois tira o atacado.
  - PDV: o Caderno com 11 mostra "faltam 1 para o atacado"; com 12, a etiqueta, o preço de atacado e o total certo; voltar
    a 11 devolve o preço de venda; o PAP-3002 (com a promoção ativa) a partir de 10 fica no atacado e não grava uso da
    promoção ao finalizar; desconto na venda até o limite do vendedor não pede liberação por causa do atacado.
  - Pedido de Venda: o mesmo caminho principal, mais salvar e reabrir o pedido com a linha de atacado.
  - o atacado travado pelo mínimo da calculadora (custo alto gravado no teste) não entra na venda.
- `teste_calculadora.py`: as asserções que conferem `#inputPrecoListaPadrao` perdem só essa parte (o resto fica).
- `teste_mascara.py`: no MAPA da ficha do produto, `@Atacado`/`@Varejo` saem e entra `id="inputPrecoAtacado"` (dinheiro).
  Atenção: as linhas 33 e 37 são de duas telas diferentes; mexa só na da ficha do produto se a outra não tiver mudado.
- Coloque a suíte nova no selo, do jeito que as outras entram.
- Rode as suítes das telas mexidas (atacado, pdv, promocoes, calculadora, mascara e a do pedido de venda) e depois
  `python selo.py --rodar`. `teste_cpd.py` já reprova de antes (item 13 da revisão geral): não é seu.
- **Provado nos dois sentidos**, numa cópia das telas fora do projeto (`DESK_PASTA`), com o servidor servindo a cópia
  quando a suíte abre as telas por `localhost:3000` (veja como `dois_sentidos_pdv.py` fez: para o servidor da porta
  3000, sobe o da cópia, e religa o verdadeiro no fim): (a) o atacado não entra ao chegar ao mínimo; (b) o atacado entra
  abaixo do mínimo. A suíte tem de reprovar nos dois.
- Conferência visual: foto da aba Preços da ficha e da linha de atacado no PDV e no Pedido, nos dois temas, no scratchpad.

## 5. A documentação

- §14.112 no fim de `docs/design-system-oficial-desk-company.md`: o que entrou, as regras e o que ficou de fora.
- `PROGRESSO.md`: "Onde paramos" ganha o preço de atacado, implementado e esperando o teste dele, com os links completos
  (`http://localhost:3000/...`) e o que conferir; o item 1 do "Próximo da fila" sai e os outros sobem. HISTORICO não.
- Sem commit: o agente principal revisa e envia.

## Fica de fora

- O campo "canal" no Pedido de Venda (o mapa pede, mas é outra entrega).
- Como o imposto do atacado entra na nota (Notas Fiscais, com o contador).
- Atacado por variação de grade: o atacado é do produto (do SKU), como os outros preços.
