# Melhorias nos módulos prontos

*Levantamento de 10/out/2026, a pedido do usuário. No mesmo dia ele **aprovou a lista inteira** e
pediu para fazer por partes. A tabela abaixo diz o que já entrou e o que falta; o texto de cada
item, mais abaixo, continua sendo o do levantamento ("Hoje" é como estava antes).*

## Situação em 12/out/2026

| situação | itens |
|---|---|
| **Feito por inteiro** (17) | D1, D2, D3, D4 · G2 · R1, R2, R3, R4, R5, R7 · E2, E7, E8 · F1, F3 · V3 |
| **Feito no principal, com resto anotado** (22) | G3 · C1, C2 · E1, E3, E4, E5, E6, E9, E10, E11 · V1, V2, V5 · L1, L2, L3, L5 · I1, I2 · F2, F4 |
| **Falta** | P1 · a limpeza de código das 17 telas. Fora da fila por decisão do usuário (13/out): C3 a C8 · V4 e L4 · X1 a X7 · R6 |
| **Entrou na lista em 12/out** | P1 (impressão em formato de relatório) · X1 a X5 (dados de exemplo que ainda não conversam) · X6 e X7 (13/out) |

G1 (a trilha) e G4 (os indicadores) são a soma dos itens de cada tela, e andam com eles.

**Decisão do usuário em 13/out/2026: os exemplos das telas prontas ficam como estão.** Saem da fila,
e voltam quando houver banco de dados: os alinhamentos X1 a X7, os painéis C3 a C8, os links V4 e
L4, o que sobrou do G3 (o romaneio e "abrir a nota") e, tirado em seguida, o R6. K1 foi feito no mesmo dia; continua na fila o P1. A regra da
tela nova está no §14.73 do design system.

O que entrou e o que falta em cada item feito no principal:

- **G3** (a página de detalhe abrir o registro clicado): feito nos cinco cadastros, em Ordens de
  Compra e em Pedidos de Venda em 13/out. O link do painel leva `?id=`, e a página mostra o que a
  lista sabe daquele registro; nos cadastros, só o registro do exemplo tem o cadastro inteiro. O
  lançamento do Caixa e a Conferência de Saída já abriam o registro certo. O botão do romaneio
  passou a mandar o id, mas a página conhece 3 dos 9. Ficam como estão, por decisão do usuário: os
  outros seis romaneios e a Nota de Entrada, que não tem "abrir a nota".
- **C1** (Clientes): o painel mostra pedidos, total comprado, último pedido e quanto ainda deve (lido
  de Contas a Receber desde 12/out, que é a dona do número), com
  links para os pedidos, as contas a receber e o CRM. Faltam os títulos vencidos em separado, os
  assuntos abertos no CRM, as devoluções e as abas Vendas e Financeiro na página do cliente.
- **E1** (Ordens de Compra): recebido e a receber no total, "atrasada há N dias", o botão "Receber
  mercadorias" e três links pelo fornecedor (notas, doca e Necessidades de Compra). Faltam o
  recebido item por item, a conta a pagar gerada e o fornecedor como link para o cadastro.
- **E3** (Entrada de Notas): a ordem de compra virou link, e a nota que já virou conta leva à conta
  a pagar dela (12/out). Faltam o botão "Abrir a nota" no painel e o andamento da conferência.
- **E4** (Conferência de Entrada): a ordem virou link, e nota sem ordem diz "sem ordem vinculada".
  Faltam o caminho para a nota e as divergências já apontadas.
- **E5** (Controle de Estoques): indicadores, quadro que filtra, cinco destinos em "Mais ações" e a
  planilha. Faltam os filtros de loja, categoria e fornecedor.
- **E6** (página do produto): leva à compra e ao giro. Faltam o link para o Endereçamento e para as
  ordens de compra em aberto do produto.
- **E9** (Endereçamento): a nota virou link. Faltam o link do produto e a sugestão de endereço pela
  capacidade livre.
- **C2** (Fornecedores): o painel mostra ordens em aberto, o que falta receber, a última compra, as
  contas a pagar e de quantos produtos ele é o fornecedor padrão. A lista dos produtos mora no
  cadastro, na aba Produtos Fornecidos (custo e pedido mínimo do fornecedor, custo médio, giro, preço
  de venda e lucro por unidade). O preço de venda de exemplo mora nessa aba até o item C3 alinhar o
  cadastro de Produtos. A página do fornecedor
  abre o registro clicado desde 13/out (G3). Falta: os outros oito registros do cadastro ainda têm
  nome de pessoa, sem compra nenhuma.
- **E10** (Tratamento de Perdas): no painel do item, a origem leva à nota e à ficha do pedido na
  Separação e na Conferência de Saída. Faltam a devolução e o acerto (o exemplo de Devolução tem
  outros produtos, e o Acerto não tem lista), e o link no histórico dos resolvidos, que cita um
  pedido e uma devolução que as telas de destino não têm.
- **E11** (Necessidades de Compra): a ordem virou link. Faltam o pedido de venda e o atalho para
  corrigir o fornecedor padrão.
- **V1** (Pedidos de Venda): o painel mostra Separação, Conferência de Saída e Expedição como "ainda
  não chegou", "em andamento" ou "concluída", e leva para a ficha daquele pedido; mais os links de
  Contas a Receber e do cadastro. Faltam o código de rastreio e a devolução.
- **V2** (a página do pedido): o quadro "Acompanhamento" mostra as seis paradas do caminho, com o
  estado e o link. A ficha da etapa só abre no pedido certo quando o exemplo da etapa tem aquele
  pedido; fora disso, o link cai na fila da etapa, filtrada no cliente.
- **V5** (PDV): a venda aparece em Pedidos de Venda e no Caixa, e a conclusão leva ao pedido. Contas
  a Receber não lê os títulos da venda a prazo, e Metas não soma a venda de balcão.
- **L1** (Separação) e **L2** (Conferência de Saída): link para os pedidos do cliente. O link da
  Conferência para a Separação saiu em 12/out, a pedido do usuário: etapa que passou não volta.
  Faltam a situação do pagamento, o prazo prometido e a falta levando ao item em Tratamento de Perdas.
- **L3** (Expedição): cada pedido da carga é link para Pedidos de Venda. Faltam o rastreio e a
  transportadora.
- **L5** (Devolução): o pedido de origem leva ao Rastreamento, e há link para a nota de entrada.
  Falta a conta a pagar.
- **F2** (a origem da conta): a conta a pagar que nasceu de nota leva à nota de entrada e à ordem de
  compra, no painel e na página; a conta a receber leva ao pedido e ao cliente. Só três contas a
  pagar do exemplo vêm de nota; as outras foram lançadas à mão, e o painel diz isso.
- **F4** (Caixa e Bancos): a origem "CP n" ou "CR n" é link para a conta. Venda de balcão e repasse
  de marketplace continuam sem documento para abrir: são lançamentos à mão no exemplo.
- **I1** (Dashboard): 14 quadros levam à tela de origem, e "Vendas por Loja" filtra o painel inteiro
  pela loja clicada. "Mais Vendidos" lê o Giro de Estoque e "Alertas de Estoque" lê Necessidades de
  Compra, e os botões 5/10/15/20 mostram mais itens. Os valores financeiros continuam próprios (R6).
- **I2** (Boas-vindas): dez atalhos com destino, o link para a Agenda e o quadro "Pendências do
  Dia", de lado a lado, com a quantidade de cada fila lida da tela dona (a suíte compara). A
  "Agenda de Hoje" continua texto fixo.

Como cada item foi feito, quando fugiu da proposta:

- **R1** virou uma página só. A primeira versão, de 10/out, era um seletor que trocava entre as
  duas telas; o usuário recusou ("não teve muito ganho") e pediu a lista única. Em 12/out a tela de
  Performance de Vendas deixou de existir: **Metas e Performance** junta as colunas numa lista e
  leva o resto para o painel lateral, com o botão de definir ou editar a meta.
- **Os links caem numa lista filtrada**, e não na página do registro. As páginas de detalhe ainda
  abrem sempre o mesmo exemplo (G3), então o link vai para a lista vizinha com a busca preenchida e
  uma faixa dizendo de onde veio o filtro.
- **Link só onde o exemplo da tela vizinha tem o registro.** C2 e C3 ficaram de fora por isso: os
  fornecedores e produtos do cadastro são outros, diferentes dos do estoque e da compra. Alinhar os
  exemplos vem antes.
- **O Dashboard continua com números de exemplo próprios.** Os quadros levam à tela de origem, e as
  contradições com o estoque saíram (valor em estoque, alertas, mais vendidos). Ler tudo ao vivo
  das outras telas é R6.

O que o usuário devolveu ao testar a primeira leva, e que já entrou (detalhe no §14.54 do design
system): o filtro de período que fecha, nas doze telas; "incluir" em branco, na ordem de compra e
nos cinco cadastros; listas numeradas do nº 1; Necessidades de Compra abrindo em "A comprar";
concluir a separação voltando para a fila, e "devolver para a fila" funcionando; pedido cancelado
sem dívida em Contas a Receber.

Entrou na lista em 12/out:

- **P1 · Impressão em formato de relatório** (M). Hoje a folha é o desenho da tela sem o menu: leva
  a caixa "Selecionar todos", a seta de ordenação e o espaçamento de tela, e não leva título com
  data, filtros nem cabeçalho repetido por página. Entra no bloco comum de impressão e chega às 20
  listas de uma vez. O usuário pediu a análise agora e o conserto depois.
- **X1 · Contas a Receber e Pedidos de Venda** (M). Quatro títulos de exemplo ainda têm cliente ou
  valor diferente do pedido que citam (PV 7, PV 10, PV 11 e PV 16).
- **X2 · Expedição e Pedidos de Venda** (M). Os romaneios de exemplo levam pedidos que o Pedido de
  Venda ainda dá como em separação.
- **X4 · Rastreamento e Pedidos de Venda** (M). O Rastreamento usa outra numeração (PV-4821...) e
  outros clientes. Sem alinhar, o item L4 (do rastreio para a conta a receber e o romaneio) levaria
  a lista vazia.
- **X5 · O realizado de Metas e os pedidos** (M). O realizado de cada loja é número próprio da tela,
  e não a soma dos pedidos faturados. Sem alinhar, o item V4 ("ver os pedidos do mês") mostraria
  uma lista que não fecha com o número.
- **X6 · Fornecedores e clientes de Finanças e os do cadastro** (M). Contas a Pagar tem dez
  fornecedores de exemplo, e só três estão no cadastro (TechParts, Luminárias Brasil e Papelaria
  Central), com outra numeração. Em Contas a Receber falta o "Consumidor Final". O link "visualizar
  dados" vai pelo nome; nome que o cadastro não tem abre o cadastro de exemplo.
- **X7 · Os itens das ordens de compra** (M). Dez das 14 ordens de exemplo só têm o total: o painel
  e a página mostram um "Item de exemplo" pelo valor da ordem. Escrever os itens mexe no "já pedido"
  de Necessidades de Compra e do Giro, que são conferidos contra as ordens em aberto.
- **X3 · O pedido andar de uma fila para a outra** (G). Concluir a separação guarda o que foi feito,
  mas o pedido não aparece sozinho na fila da Conferência de Saída: cada tela tem a sua lista.

A segunda varredura, do miolo de Inventário, Acerto e PDV, continua combinada para depois de o
usuário testar o que entrou em 12/out.

## Como o levantamento foi feito

As 80 telas foram abertas no navegador, uma a uma:

- em cada lista, clique na primeira linha de cada aba, com registro do que abriu (painel lateral,
  outra página ou nada) e do que o painel traz: blocos, botões e links;
- cada item de "Mais ações" e cada botão de imprimir, exportar e importar foi clicado, para separar
  o que funciona do que só mostra um aviso;
- mapa de para onde cada tela leva, fora do menu lateral;
- as páginas de detalhe foram abertas com registros diferentes, para ver se mostram o registro
  clicado.

Limites: o painel foi visto pela primeira linha de cada aba, então outra linha pode mostrar algo a
mais. O miolo dos fluxos longos (Inventário, Acerto, PDV com caixa aberto, contagem da conferência)
e os formulários de cadastro, campo a campo, não entraram.

Tamanho de cada item: **P** mexe numa tela, **M** em duas ou três, **G** em muitas.

## Resumo

1. **O painel lateral mostra o registro, mas quase nunca leva ao vizinho.** A ordem de compra não
   leva à nota, o pedido não leva à separação nem ao rastreio, a conta a pagar não leva à nota que a
   gerou. É o maior ganho disponível: o dado já existe na tela ao lado.
2. **45 ações de menu não fazem o que o nome diz:** 33 só mostram um aviso ("entra junto com
   Relatórios") e 12 não fazem nada. Imprimir e baixar planilha já funcionam em três telas e podem
   ir para as outras.
3. **Os cadastros são a parte mais pobre.** O painel de Clientes, Fornecedores e Produtos mostra só
   o que foi digitado. O que o cliente comprou e deve aparece no Pedido e no CRM, e não no cadastro.
4. **O Início não leva a lugar nenhum e contradiz os módulos.** Nenhum quadro do Dashboard é
   clicável, e os números dele são próprios.
5. **A varredura achou quatro defeitos**, pequenos, que vale corrigir de qualquer jeito (seção 4).

---

## 1. O que vale para vários módulos

**G1 · A trilha do documento no painel lateral** (G)
- Hoje: o painel de Ordens de Compra, Conferência de Entrada, Endereçamento, Reposição, Separação,
  Conferência de Saída, Devolução, Rastreamento, Pedidos de Venda e Metas não tem nenhum link para
  outra tela, além do botão que abre a própria página.
- Proposta: um bloco "De onde veio e para onde vai" em cada painel. Na compra: ordem, nota,
  conferência, endereçamento, conta a pagar. Na venda: pedido, separação, conferência, romaneio,
  rastreio, conta a receber, devolução. Cada etapa com a situação e o link.
- Ganho: seguir um documento do começo ao fim sem voltar ao menu, e ver na hora em que etapa ele
  parou. Os itens E1, E3, E4, V1, L1 a L5 e F2 são este item, tela por tela.

**G2 · Imprimir e baixar planilha de verdade** (G)
- Hoje: 33 itens em 17 telas só abrem um aviso dizendo que a função "entra junto com Relatórios".
  Em Clientes, Fornecedores e Produtos, 12 itens de "Mais ações" fecham o menu e não fazem nada.
- Proposta: levar para as listas o componente que já funciona em Necessidades de Compra, Giro de
  Estoque e Inventário: planilha com as colunas da tela, respeitando os filtros, e impressão da
  lista inteira. O que não tem como funcionar agora (importar planilha, buscar nota na Sefaz) sai do
  menu até existir.
- Ganho: a tela para de prometer. Boa parte do módulo de Relatórios, que é o último da fila, fica
  adiantada.

**G3 · A página de detalhe abrir o registro clicado** (G)
- Hoje: em 11 de 18 páginas de detalhe, qualquer linha clicada abre o mesmo exemplo: Pedidos de
  Venda (sempre o nº 2), Ordens de Compra (sempre a nº 2), Entrada de Notas, lançamento do Caixa,
  Clientes, Fornecedores, Produtos, Vendedores, Lojas Desk, Conferência de Saída e Romaneio. Já
  mostram o registro certo: Contas a Pagar, Contas a Receber, Devolução, Rastreamento, Separação e
  a página do produto no Controle de Estoques.
- Proposta: a página carregar ao menos o cabeçalho e os itens do registro que veio da lista.
- Ganho: teste coerente (cliquei no pedido 16, abriu o 16), e os links da trilha (G1) passam a
  fazer sentido. É o item mais trabalhoso da lista.

**G4 · Indicadores no topo das listas que pedem ação** (M)
- Hoje: só Necessidades de Compra, Devolução, Rastreamento, Metas e Performance têm números no topo.
- Proposta: Ordens de Compra, Pedidos de Venda, Controle de Estoques, Contas a Pagar e Contas a
  Receber (itens E2, V3, E5 e F3). Clicar no número filtra a lista.
- Ganho: ver o tamanho do problema antes de montar filtro.

---

## 2. Por módulo

### Cadastros

**C1 · Clientes: o painel do cliente** (M)
- Hoje: nome, documento, telefone, e-mail, endereço e "cliente desde". A página do cliente tem as
  abas Dados Gerais, Dados Complementares e Anexos.
- Proposta: último pedido e total comprado; títulos em aberto e vencidos, que é o que bloqueia
  pedido novo; assuntos abertos no CRM; devoluções. Links para os pedidos, as contas a receber e o
  CRM do cliente. Na página, as abas Vendas e Financeiro, que o CRM já tem.
- Ganho: atender o cliente olhando uma tela. Hoje esse histórico aparece dentro do Pedido ("Ver
  últimas vendas") e do CRM, e o cadastro do cliente é o único lugar que não mostra.

**C2 · Fornecedores: o painel do fornecedor** (M)
- Hoje: só os dados de cadastro.
- Proposta: ordens em aberto e o que falta receber, última compra, contas a pagar em aberto e os
  produtos em que ele é o fornecedor padrão. Links para as ordens e as contas dele.
- Ganho: negociar com o fornecedor sabendo o que está pedido e o que se deve. A Ordem de Compra já
  tem "Ver últimas compras"; o cadastro não tem.

**C3 · Produtos: o painel do produto** (M)
- Hoje: SKU, preço de venda e "estoque atual 8 un."
- Proposta: saldo por situação (disponível, a endereçar, bloqueado), mínimo e máximo, faixa de
  giro, fornecedor padrão, última entrada e última venda. Links para a página do produto no
  Controle de Estoques, para Necessidades de Compra e para o Giro.
- Ganho: o cadastro vira a porta de entrada do produto. Hoje o Controle de Estoques leva ao
  cadastro, e o cadastro não leva de volta.

**C4 · Lojas Desk: o painel da loja** (P)
- Hoje: contato, documento e endereço, quase tudo "Não informado".
- Proposta: meta e realizado do mês, vendedores e depósitos da loja, quantidade de produtos. Links
  para Metas, Performance e Vendedores.
- Ganho: a loja num clique.

**C5 · Vendedores: o painel do vendedor** (P)
- Hoje: dados de cadastro e a porcentagem de comissão.
- Proposta: meta e realizado do mês, pedidos do mês, comissão acumulada. Links para Metas,
  Performance e os pedidos dele.
- Ganho: acompanhar o vendedor sem montar filtro em três telas.

**C6 · Depósitos: resumo antes da edição** (P)
- Hoje: clicar abre direto o formulário de edição.
- Proposta: no topo do painel, o que há no depósito: valor e quantidade em estoque, saldo a
  endereçar, bloqueado, transferências a caminho e quantidade de endereços. Links para o Controle de
  Estoques e o Endereçamento já filtrados.
- Ganho: saber o que está em cada depósito sem sair do cadastro.

**C7 · Endereços de Estoque: o que está no endereço** (P)
- Hoje: a linha diz "3 produtos alocados", e o painel é só edição.
- Proposta: listar os produtos e o saldo de cada um naquele endereço, com link para o produto.
- Ganho: responder "o que tem na A-01-1?" sem ir ao Controle de Estoques.

**C8 · Marcas, Categorias, Departamento, Seção e Embalagens: onde é usado** (M)
- Hoje: o painel é só edição.
- Proposta: "usado em N produtos", com link para Produtos já filtrado, e o mesmo número no aviso de
  exclusão.
- Ganho: saber o tamanho do estrago antes de excluir ou inativar.

### Estoque

**E1 · Ordens de Compra: o painel da ordem** (M)
- Hoje: igual em todas as situações. Fornecedor, depósito, datas, total, itens e um botão, "Abrir
  ordem completa".
- Proposta: recebido e a receber, por item e no total; "atrasada há N dias" quando a previsão
  passou; as notas de entrada e as conferências ligadas, com link; as contas a pagar geradas; o
  fornecedor como link; e o botão certo para a situação: "Receber mercadorias" em aberto e em
  andamento, que hoje só existe dentro da página.
- Ganho: acompanhar a compra pela lista, sem abrir ordem por ordem.

**E2 · Ordens de Compra: indicadores** (P)
- Hoje: não tem.
- Proposta: valor em aberto, a receber nesta semana, atrasadas e sem data prevista.
- Ganho: cobrar fornecedor atrasado sem procurar.

**E3 · Entrada de Notas: o painel da nota** (M)
- Hoje: o painel não tem como abrir a página da nota; só "Incluir nota de entrada" leva a ela. A
  ordem de compra aparece como texto.
- Proposta: "Abrir a nota"; ordem de compra e fornecedor como links; a conta a pagar da nota; o
  andamento da conferência.
- Ganho: fechar o ciclo nota, ordem, conferência e financeiro.

**E4 · Conferência de Entrada: o painel da nota na doca** (P)
- Hoje: "Ordem de compra nº 11" é texto, e não há caminho para a nota.
- Proposta: os dois como links, e as divergências já apontadas quando a conferência está em
  andamento.
- Ganho: quem está na doca tira a dúvida sem sair da fila.

**E5 · Controle de Estoques: a lista** (M)
- Hoje: sem indicadores; "Mais ações" só leva ao Inventário; os filtros são depósito, nível e
  situação.
- Proposta: indicadores (valor em estoque, abaixo do mínimo, a endereçar, bloqueado); filtros de
  loja, categoria e fornecedor, cujos dados já existem nas telas de compra e giro; "Mais ações"
  levando a Necessidades de Compra, Giro, Tratamento de Perdas, Acerto e Transferência.
- Ganho: a tela central do estoque passa a ser o ponto de partida para as outras.

**E6 · Controle de Estoques: a página do produto** (P)
- Hoje: o bloqueado leva a Tratamento de Perdas, mas "5 a endereçar, travado há 3 dias" não leva ao
  Endereçamento, e não há caminho para a compra.
- Proposta: links para o Endereçamento, para as ordens de compra em aberto do produto, para a conta
  dele em Necessidades de Compra e para o Giro.
- Ganho: da página do produto se chega a tudo que mexe no saldo dele.

**E7 · Reposição: quando o caminho é comprar** (P)
- Hoje: sem saldo fora da base, o painel diz "aqui o caminho é comprar" e termina aí. A aba se
  chama "Necessidade Reposição", nome quase igual ao do módulo Necessidades de Compra.
- Proposta: o link "Abrir em Necessidades de Compra", já no produto; e a aba passar a se chamar "A
  repor".
- Ganho: o aviso vira ação, e os dois nomes param de se confundir.

**E8 · Transferência Entre Estoques: painel da transferência** (M)
- Hoje: clicar na linha não abre nada. Os itens só aparecem dentro de "Confirmar recebimento", e
  uma transferência já recebida não tem como ser vista.
- Proposta: painel com os itens, enviado e recebido, origem e destino, tempo em trânsito, quem
  enviou e quem recebeu.
- Ganho: consultar uma transferência sem precisar recebê-la.

**E9 · Endereçamento: o painel do item** (P)
- Hoje: "nota 736" é texto, não há link para o produto, e a aba Estoque Zero não abre painel.
- Proposta: nota e produto como links, e a sugestão de endereço pela capacidade livre, que o
  cadastro de endereços já guarda para isso.
- Ganho: endereçar mais rápido e conferir a origem do saldo.

**E10 · Tratamento de Perdas: a origem como link** (P)
- Hoje: é o painel mais completo do sistema. Só a origem ("NF-e 12.951", "Pedido #23") é texto.
- Proposta: a origem levar à nota, ao pedido ou à devolução.
- Ganho: auditar a falta ou a avaria indo direto ao documento.

**E11 · Necessidades de Compra: links na conta** (P)
- Hoje: a conta lista "Ordem nº 12" e "Pedido nº 43" como texto, e "sem fornecedor padrão" não leva
  a lugar nenhum.
- Proposta: os três como links (a ordem, o pedido e o cadastro do produto).
- Ganho: corrigir o fornecedor padrão ou conferir a ordem sem perder a lista.

### Vendas

**V1 · Pedidos de Venda: o painel do pedido** (M)
- Hoje: cliente, loja, vendedor, datas, total e itens.
- Proposta: a trilha do pedido: pago ou não, separado, conferido, romaneio, código de rastreio,
  entregue; a conta a receber com a situação; a devolução, se houver. Cada etapa com link, e o
  cliente também.
- Ganho: responder "cadê meu pedido?" pela lista. Hoje o Rastreamento mostra o pagamento e os
  volumes, e o Pedido não mostra nada da logística.

**V2 · Pedidos de Venda: a página do pedido** (P)
- Hoje: tem "Acompanhar no galpão" e "na bancada", e nenhum caminho para Expedição, Rastreamento,
  Devolução e Contas a Receber. "Ver conta a receber" abre um painel, não a conta.
- Proposta: completar os links.
- Ganho: a página do pedido vira o centro do pós-venda.

**V3 · Pedidos de Venda: indicadores** (P)
- Hoje: não tem.
- Proposta: a aprovar, a faturar, atrasados para entrega e total do período.
- Ganho: ver o que está parado sem filtrar por situação.

**V4 · Metas e Performance: links nos painéis** (P)
- Hoje: o painel de Metas não tem link; o de Performance só leva a "Definir meta".
- Proposta: "Ver os pedidos do mês" (Pedidos já filtrado na loja ou no vendedor), um painel levando
  ao outro, e o "Devolvido" da Performance levando às devoluções da loja.
- Ganho: do número para a lista que o explica.

**V5 · PDV: a venda aparecer no resto do sistema** (M)
- Hoje: a venda concluída diz o que gerou, não leva a lugar nenhum e não aparece em Pedidos de
  Venda, Contas a Receber, Caixa nem Metas. Limitação registrada em 09/out.
- Proposta: o mesmo mecanismo das ordens criadas em Necessidades de Compra: o PDV grava, Pedidos de
  Venda lê, e a conclusão da venda ganha o link para o pedido.
- Ganho: testar a venda de balcão de ponta a ponta.

### Logística

**L1 · Separação: o painel do pedido** (P)
- Hoje: cliente, endereço, envio e itens na ordem da coleta. Sem link para o pedido.
- Proposta: "Abrir o pedido", situação do pagamento e o prazo prometido ao cliente.
- Ganho: o separador vê o que é urgente e por quê.

**L2 · Conferência de Saída: o painel do pedido** (P)
- Hoje: sem link para o pedido nem para a ficha de separação. Quando há "falta na separação", é só
  uma etiqueta.
- Proposta: os dois links, e a falta levando ao item em Tratamento de Perdas.
- Ganho: resolver a falta sem procurar o item na outra fila.

**L3 · Expedição: o painel do romaneio** (P)
- Hoje: os pedidos da carga aparecem como texto.
- Proposta: cada pedido como link (pedido e rastreio), e a transportadora também.
- Ganho: do romaneio ao pedido em um clique.

**L4 · Rastreamento: o painel do pedido** (P)
- Hoje: painel completo, com um botão, "Abrir o pedido". "Pagamento: vencido, lido de Contas a
  Receber" é texto.
- Proposta: links para a conta a receber e para o romaneio em que o pedido saiu.
- Ganho: cobrar ou conferir a saída sem trocar de módulo pelo menu.

**L5 · Devolução: o painel da devolução** (P)
- Hoje: painel completo, com um botão, "Abrir a devolução".
- Proposta: o pedido de origem, a nota de entrada gerada e a conta a pagar como links. A Entrada de
  Notas já aponta para a devolução; o caminho de volta não existe.
- Ganho: ver se a mercadoria entrou e se o dinheiro foi devolvido.

### Finanças

**F1 · Contas a Pagar e a Receber: painel de pré-visualização** (M)
- Hoje: clicar na linha sai da lista e abre a página da conta. Não há painel de pré-visualização,
  como há em Pedidos de Venda e em Ordens de Compra.
- Proposta: painel com valor, pago, saldo, vencimento, a origem com link e os botões Pagar ou
  Receber ali mesmo.
- Ganho: baixar um título sem trocar de tela, no mesmo padrão do resto do sistema.

**F2 · Contas a Pagar: a origem da conta** (P)
- Hoje: a página da conta leva ao fornecedor e ao Caixa, e não à nota de entrada nem à ordem de
  compra que a gerou. Contas a Receber já leva ao pedido.
- Proposta: a origem com link nas duas.
- Ganho: conferir a conta contra a nota antes de pagar.

**F3 · Contas a Pagar e a Receber: indicadores** (P)
- Hoje: só as abas com a contagem (em aberto, atrasadas, pagas).
- Proposta: vencidas em valor, vencem hoje, próximos 7 dias e total em aberto.
- Ganho: saber quanto dinheiro está em jogo, não só quantos títulos.

**F4 · Caixa e Bancos: a origem do lançamento** (P)
- Hoje: a coluna Origem é texto.
- Proposta: levar à conta paga, à conta recebida ou à venda que gerou o lançamento.
- Ganho: conciliar sem procurar o documento.

### Início

**I1 · Dashboard: quadros que levam à origem e leem o mesmo dado** (M)
- Hoje: 15 quadros, nenhum clicável, com números próprios. "Mais Vendidos" traz a Luminária LED com
  312 unidades, e o Giro de Estoque a classifica como encalhe, sem venda em 180 dias. "Alertas de
  Estoque" traz a Cadeira Ergonômica com 5 unidades, e o Controle de Estoques tem 24.
- Proposta: cada quadro levar à tela de origem (Contas a Pagar, Contas a Receber, Metas,
  Necessidades de Compra, Giro, Pedidos por situação) e ler o dado dela.
- Ganho: o painel deixa de contradizer os módulos e vira o ponto de entrada do dia.

**I2 · Boas-vindas: atalhos com destino e a lista do dia** (P)
- Hoje: os 8 "Atalhos Rápidos" não levam a lugar nenhum, e a "Agenda de Hoje" é texto fixo, não a
  Agenda.
- Proposta: atalhos com destino, a agenda de verdade e um bloco "O que precisa de você hoje": notas
  a conferir, pedidos a separar, contas vencendo, itens a comprar, bloqueios antigos.
- Ganho: a primeira tela vira lista de trabalho.

### Configurações

**K1 · Parâmetros de estoque virou gaveta** (M) — **feito em 13/out/2026** (§14.74 do design system): duas telas, e o bloqueio por atraso em Configurações do cadastro de clientes
- Hoje: 9 seções, e 5 não são de estoque: filas do galpão, reserva e bloqueio por atraso, expedição
  e romaneio, MDF-e e devoluções de venda.
- Proposta: separar em Parâmetros de estoque e Parâmetros de logística, e levar o bloqueio por
  atraso para junto das configurações de venda.
- Ganho: achar o parâmetro pelo nome da tela.

---

## 3. O que dá para tirar ou juntar

**R1 · Metas e Performance de Vendas repetem meta e atingimento** (P)
- Hoje: as duas listam as mesmas lojas e vendedores, no mesmo mês; as duas têm as colunas de meta,
  atingimento e situação; e os dois painéis trazem a tabela "O ano de 2026".
- Proposta menor, que eu recomendo: Performance fica sem as colunas de meta, que já são de Metas, e
  ganha um link para ela. Proposta maior: uma tela só, com as duas visões.
- Ganho: cada tela responde uma pergunta. Metas, "estamos batendo?"; Performance, "como vendemos?".

**R2 · "Imprimir" duas vezes na mesma tela** (P)
- Hoje: Clientes, Fornecedores, Produtos, Ordens de Compra e Pedidos de Venda têm "Imprimir" no topo
  e de novo em "Mais ações".
- Proposta: ficar só em "Mais ações".
- Ganho: topo mais limpo, com o botão principal em destaque.

**R3 · "Importar XML" em duas telas** (P)
- Hoje: está em Entrada de Notas e em Conferência de Entrada. As duas listas mostram a mesma nota
  por dois lados, e isso foi decidido em setembro: fica.
- Proposta: tirar o botão da Conferência, onde o trabalho é receber e contar. A nota nasce na
  Entrada.
- Ganho: uma porta só para a nota entrar.

**R4 · Três cadastros repetidos no menu de Integrações** (P)
- Hoje: Lojas Desk, Depósitos e Endereços de Estoque aparecem em Cadastros e de novo em Integrações.
- Proposta: tirar os três atalhos de Integrações.
- Ganho: o menu de Integrações passa a mostrar só o que é integração.

**R5 · Dois botões "Gerar ordem de compra" em Necessidades de Compra** (P)
- Hoje: um no topo e outro na barra de seleção. O do topo só serve com produto marcado.
- Proposta: ficar só o da barra, que aparece quando há seleção.
- Ganho: o botão aparece quando pode ser usado.

**R6 · Cópias do número de meta** (M) — **fora da fila** por decisão do usuário em 13/out/2026: é alinhamento de exemplo
- Hoje: a aba "Histórico de Metas" da página da loja e o Dashboard têm números próprios. Pendência
  registrada em 08/out.
- Proposta: as duas lerem de Metas.
- Ganho: um número só para a meta.

**R7 · Itens de menu sem data para existir** (P)
- Hoje: "Buscar notas na Sefaz pela chave", "Gerenciar vales-troca", "Copiar o que a vitrine
  mostra" e as quatro importações de planilha só explicam que ainda não existem.
- Proposta: sair do menu até a função existir.
- Ganho: menu só com o que funciona.

Não precisa mexer: o filtro "abaixo do mínimo" do Controle de Estoques e a aba de mesmo nome em
Necessidades de Compra mostram a mesma lista, e a suíte garante que batem. São duas perguntas
diferentes, o saldo e a compra. Basta o link de uma para a outra (item E5).

---

## 4. Defeitos achados na varredura

Pequenos, e vale corrigir sem esperar o resto.

**D1 · Conferência de Entrada abre a nota errada** (P)
- Na aba Conferidas, clicar na nota 4471 abre o painel da nota 9002. As duas têm o mesmo
  identificador no dado de exemplo.

**D2 · Pedido de Venda: "Acompanhar no galpão" e "na bancada" mandam o pedido errado** (P)
- O link sai sem o número do pedido. A Separação avisa que não achou o pedido e abre outro.

**D3 · Clientes, Fornecedores e Produtos: "Mais ações" não faz nada** (P)
- Os 12 itens fecham o menu e nada acontece, nem aviso. Resolve junto com G2.

**D4 · Cinco telas ainda dizem que algo só funciona numa ferramenta que saiu do projeto** (P)
- Conferência de Entrada, Entrada de Notas (lista e página), página da Ordem de Compra e Separação.
  O sistema passou a ser programado aqui em 10/out.

Limpeza de código, sem efeito para quem usa: 17 telas carregam um trecho do menu de outra tela (um
desvio para o Inventário num menu que elas não têm).

---

## 5. Ordem sugerida

1. **D1 a D4**: os defeitos.
2. **G2** com **R2**, **R7** e **D3**: imprimir e planilha de verdade, e o menu enxuto.
3. **A trilha da compra**: E1, E3, E4, F2, E10 e E11.
4. **A trilha da venda**: V1, V2, L1 a L5, F1 e F4.
5. **Os cadastros**: C1, C2 e C3 primeiro; depois C4 a C8.
6. **O Início**: I1 e I2, com R6.
7. **Indicadores**: E2, E5, V3 e F3.
8. **O que sobra**: E6 a E9, V4, V5, K1, R1, R3, R4 e R5.
9. **G3** por último, por ser o mais trabalhoso.
