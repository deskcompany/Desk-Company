*Atualizado em 16/nov/2026: o preço de atacado (ficha do produto, PDV e Pedido de Venda) foi implementado e está esperando o teste dele. O próximo da fila é a revisão geral.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Revisão geral, pacote E (17/nov/2026), esperando o teste dele:** a calculadora com mais de uma embalagem (item 3). Na [ficha do produto](http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1&id=1), aba Preços, "Calcular preço": o campo "Embalagens do produto" é uma lista com caixa de marcar; marque a Flex M e o Envelope de Segurança Pequeno (a garrafa térmica na caixa e no saquinho, o exemplo dele) e confira que a embalagem vira R$ 6,50 e o preço mínimo sobe de R$ 79,28 para R$ 80,86. O PDV, o Pedido de Venda e a promoção leem o mesmo mínimo. O Saco plástico (insumo que não entra sozinho) também aparece na lista de marcar. Detalhe no §14.117.

**Revisão geral, pacote D (17/nov/2026), esperando o teste dele:** Finanças (itens 2 e 13). Em [Contas a Pagar](http://localhost:3000/financas/pagina-financas-contas-pagar.html) e em [Contas a Receber](http://localhost:3000/financas/pagina-financas-contas-receber.html), a aba "atrasadas" mostra toda conta vencida, fora do período, e dá o mesmo número do card "Vencidas". O teste da página da conta deixou de depender da data, e o selo inteiro ficou verde. Detalhe no §14.116.

**Revisão geral, pacote C (16/nov/2026), esperando o teste dele:** as telas, uma a uma (itens 15, 19, 6, 7, 8, 9, 10, 11 e 1). [Registro de atividades](http://localhost:3000/configuracoes/pagina-configuracoes-registro-atividades.html) (clicar na linha abre o painel), [Produtos](http://localhost:3000/cadastros/pagina-cadastros-produtos.html) (clicar numa linha: o preview com os quatro blocos), [painel da promoção](http://localhost:3000/vendas/pagina-vendas-promocoes.html) (botão azul e "Mais ações"), a ficha do produto ([Dados Complementares](http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1&id=1) e o "Encerrar antes para este produto" na aba Preços), a revisão da promoção ("Pronto" e "Corrigir"), o [PDV](http://localhost:3000/vendas/pagina-vendas-pdv.html) (o resumo e o "Desconto à vista" sem maquininha) e [Embalagens](http://localhost:3000/cadastros/pagina-cadastros-embalagens.html) (campos de tamanho numa linha). Detalhe no §14.115.

**Revisão geral, pacote B (16/nov/2026), esperando o teste dele:** as tabelas (itens 16, 17, 18 e 4). Nenhuma tabela rola na horizontal a 1280 px e o título da coluna fica numa linha só: [Registro de atividades](http://localhost:3000/configuracoes/pagina-configuracoes-registro-atividades.html) (a coluna "Ação" estreita, com reticências; faça algumas ações para encher o registro), [Necessidades de Compra](http://localhost:3000/estoque/pagina-estoque-necessidades-compra.html) (o fornecedor foi para baixo do produto), [CRM](http://localhost:3000/vendas/pagina-vendas-crm.html), [Metas](http://localhost:3000/vendas/pagina-vendas-metas.html), [Usuários](http://localhost:3000/configuracoes/pagina-configuracoes-usuarios.html) ("Desconto sem liberação") e os títulos encurtados em Giro, Controle de Estoques, Expedição e Custos do E-commerce; o texto solto "De" e "Mínimo" da [promoção](http://localhost:3000/vendas/pagina-vendas-promocoes-detalhe.html?id=1) e o "Total" da Ordem de Compra e da Entrada de Notas alinhados com os campos. Detalhe no §14.114.

**Revisão geral, pacote A (16/nov/2026), esperando o teste dele:** o mínimo do detalhe da promoção lê o custo da aba Custos; o menu abre para cima quando não cabe embaixo (item 14: PDV, [cobrança](http://localhost:3000/vendas/pagina-vendas-pdv.html), venda com um item, "Adicionar recebimento (F4)"); o painel lateral aberto trava a página de trás (item 5, qualquer lista, ex. [Pedidos](http://localhost:3000/vendas/pagina-vendas-pedidos.html)); a bolinha centralizada (item 12, "Desconto / Acréscimo" e "O que esta venda gerou" no PDV). Detalhe no §14.113.

**O preço de atacado: implementado em 16/nov/2026, esperando o teste dele.** A ficha do produto ganhou, na aba Preços, o "Preço de atacado" e o "A partir de N unidades" (saiu a
seção "Preço por lista"); no PDV e no Pedido de Venda, chegou à quantidade mínima, a linha vira o preço de atacado sozinha (a soma do produto na venda inteira decide, a promoção
não divide e não conta uso), e antes do mínimo a linha avisa "faltam N para o atacado (R$ X cada)". O atacado não é desconto. A aba Custos da ficha passou a gravar (o mínimo do atacado usa o custo dela). O detalhe está no §14.112 e o plano em `docs/plano-preco-atacado.md`.
O que conferir (a Luminária de Mesa LED já tem atacado de exemplo: R$ 72,90 a partir de 6, com o preço de venda em R$ 79,90; o Kit Papelaria, R$ 59,50 a partir de 10; os códigos de exemplo: 1234 do Administrador, 2468 do Carlos):
- A ficha, aba Preços: [Luminária, com o atacado de exemplo](http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1&id=8) e
  [Fone de Ouvido, para testar as travas](http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1&id=1): só o preço sem a quantidade, quantidade 1, preço igual
  ao de venda e preço abaixo de R$ 79,28 (o mínimo da calculadora) recusam, com a mensagem no campo; salvar cria duas linhas no histórico do preço.
- O PDV: [PDV](http://localhost:3000/vendas/pagina-vendas-pdv.html), abra o caixa na Desk Shope, ponha 5 Luminárias (a linha diz "faltam 1 para o atacado (R$ 72,90 cada)"), depois mais 1 (vira "Atacado, a partir de
  6 un." a R$ 72,90; a prévia de "Adicionar produto" já mostra o atacado quando a soma chega a 6); o Kit Papelaria com 10 sai a R$ 59,50 mesmo com a promoção ativa.
- O Pedido de Venda: [novo pedido](http://localhost:3000/vendas/pagina-vendas-pedidos-detalhe.html?novo=1), loja Desk Shope, o mesmo caminho (a conferência acontece ao sair do campo da
  quantidade). Diminuir a quantidade abaixo do mínimo devolve o preço de venda.

**Usuários do sistema e Permissões de usuários, entrega 2: testada por ele em 16/nov/2026** ("os demais testes passaram"). O que ele
pediu no teste ficou para a revisão geral (itens 14 a 18). O texto da entrega foi para o HISTORICO.md, e o detalhe está no §14.111.
**Os códigos de exemplo:** 1234 do Administrador Desk (Owner, libera tudo), 2468 do Carlos Mendes (Gerente), 3456 da Marina Costa,
4567 da Ana Souza; o Rafael Andrade (5678) está bloqueado, e a Bianca Furtado e a Fernanda Lima não têm código.

**Usuários do sistema e Permissões de usuários, entrega 1: testada por ele em 11/nov/2026** ("os testes passaram"). O texto da entrega foi para o HISTORICO.md, e o detalhe está no §14.110. O resto do módulo é a entrega 2, o primeiro da fila.

**Promoções e Encartes, entrega 2 (o preço chega na venda): testada por ele em 10/nov/2026.** Os ajustes que ele pediu na hora foram
feitos no mesmo dia (a etiqueta sem o link da promoção, no PDV e no Pedido; o histórico sem "com senha"); os que ele deixou para depois
estão na revisão geral (itens 10 a 12). O texto da entrega foi para o HISTORICO.md, e o detalhe está no §14.109.

**Promoções e Encartes, entrega 1: testada por ele em 09/nov/2026.** Os ajustes que ele pediu estão na revisão geral (itens 4 a 9) e ficam para ela; o texto da entrega foi para o HISTORICO.md, e o detalhe está no §14.108.

**Estoque das embalagens: feito em 03/nov/2026 e testado por ele em 03-04/nov.** Ele pediu para segurar como está; a rodada de correção é o item 4 do "Próximo da fila". O que foi feito está no HISTORICO.md e o detalhe no §14.107.

**Calculadora de precificação: testada e aprovada por ele em 04/nov/2026** (HISTORICO.md, §14.101). A observação do teste, várias embalagens na calculadora, está na revisão geral (item 3).

**Custos do E-commerce: concluído em 30/out/2026** (HISTORICO.md, §14.95 a §14.100). O que ficou de fora está na lista da revisão geral.

**Vale-compra e Gateways de Pagamento: concluídos e aprovados por ele** (HISTORICO.md, §14.89 a §14.94). Falta o protótipo da vitrine, no "Próximo da fila".

**Como trabalhamos desde 21/out** (combinado com o usuário depois de gastar 78% da cota semanal em 2 dias, com entregas
de 1 a 3 horas; medido: o executor reaproveitado chegou a 840 mil tokens e 300 ações, e esperar o selo em laço relia
o contexto a cada 10 s): **executor novo a cada entrega** (reaproveitar só num ajuste pequeno logo em seguida); **selo uma
vez, no fim, sem espera em laço**, e durante o trabalho só as suítes que a mudança toca; **defeitos injetados: 3 a 4, só
onde há dinheiro ou regra nova**; o executor **lê por trecho** (grep e linhas), nunca a tela inteira; **uma conversa nova
por módulo**, começando por este arquivo; e o principal **sugere esforço médio** ao executor quando a tarefa é mecânica e
de baixo risco (o usuário decide). Os retornos de teste vêm num pacote só.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **46 de 56 (82%)**, em 96 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 82% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

Eram 90 telas e 45 de 55 itens com tela até 03/nov/2026: Promoções e Encartes entrou no menu já com a lista e a página. Em 10/nov entraram as quatro telas de Usuários e Perfis, em Configurações (o menu não mudou).

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 13 de 14 | Relatórios de Estoque |
| Vendas | 6 de 9 | Notas Fiscais, Margem de Contribuição, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 4 de 5 | Relatórios Finanças |
| Integrações | 1 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Relatórios de Integrações |
| Configurações | hub com 24 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## Próximo da fila

Refeita em 10/nov, depois do teste da entrega 2 de Promoções e Encartes e da barganha das quatro perguntas.

**O mapa dos canais de venda foi aprovado por ele em 10/nov/2026** ([docs/mapa-canais-venda-desk-company.md](docs/mapa-canais-venda-desk-company.md)):
11 canais, a escada do preço, os 7 perfis (o dele se chama **Owner**; outros tipos de usuário virão, por isso o perfil é um
cadastro), o preço de atacado no cadastro do produto e o aplicativo de vendas do representante, que vem na produção.

1. **A revisão geral** (a lista "Para a próxima revisão geral", abaixo, com os ajustes dos testes das entregas 1 e 2), quando ele quiser.
2. **Promoções e Encartes, entrega 3: "Gerar encarte"** (a peça com foto, "de… por…" e prazo, com a marca da loja, para imprimir ou mandar aos vendedores). Começa pela barganha, com prints de encartes que eles usam hoje, se houver.
3. **O protótipo da vitrine** (Gateways de Pagamento e preço promocional): o preço de venda riscado e o promocional como o preço; o painel da vitrine não cadastra nem muda preço, manda pedidos ao sistema (auditoria de produto, revisão de preço); o "Ativar preço promocional" dele cria uma promoção só da vitrine, com as mesmas travas, na mesma lista de Promoções e Encartes.
4. **Rodada de correção do estoque das embalagens** (pedido dele em 03/nov; começa pela barganha). **Segurada por ele em 04/nov:** a tela fica como está, e ele avisa quando voltar:
   - **Motivos de acerto:** o "Acertar saldo" passa a escolher o motivo de uma lista, em vez de texto solto. Ver se a lista é a de Configurações → Motivos de Perda, que já existe.
   - **Prejuízo pelo motivo:** o acerto para menos por avaria, quantidade errada etc. gera prejuízo, conforme o motivo, como a perda de produto em Tratamento de Perdas.
   - **Inventário geral:** as embalagens (caixas, envelopes, sacolas, insumos) aparecem no Inventário para serem contadas.
   - **Ordem de compra:** em Necessidades de Compra, o bloco das embalagens gera ordem de compra, e não "Dar entrada", para seguir o fluxo normal (ordem → nota → entrada). A decidir: a embalagem entra na Ordem de Compra sem SKU de produto?
   - **Movimentação:** entrada, baixa e acerto de embalagem aparecem em Estoque → Movimentação de Estoque, e não só no Registro de atividades.
5. **Desconto da venda nossa na hora da venda** (ideia dele em 30/out, opcional): a venda sem ninguém recebendo comissão e paga no Pix pode somar o desconto da comissão ao do Pix. A calculadora já mostra até onde dá; falta a opção no PDV e no Pedido de Venda, e a vitrine depende do protótipo dela.
6. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
7. **Os outros itens pós-MVP** (Margem de Contribuição, Relatórios, Notas Fiscais, Integrações). Módulo novo começa pela
   barganha, com os prints, e já nasce com o exemplo no padrão (§14.73).

**Saiu da fila, por decisão do usuário, e volta quando houver banco de dados:** os alinhamentos de
exemplo (X1 a X7); os painéis dos outros cadastros (C3 a C8); os links V4 e L4, que dependiam dos
alinhamentos; o que sobrou do G3 (a página do romaneio conhecer os 9 romaneios, e "abrir a nota"
na Entrada de Notas, que é o item E3); e as cópias do número da meta (R6), que ele tirou em seguida.

## Decidido, e ainda não feito de propósito

- **Preço promocional** (barganhado com o usuário em 04/nov/2026; mora em Promoções e Encartes, em Vendas).
  O preço tem um dono só, o sistema: o promocional é cadastrado na aba Preços do produto (ou chega pela planilha da promoção e entra no
  cadastro quando ela é aprovada). O painel da vitrine não cadastra nem muda preço: mostra os produtos da loja e manda pedidos ao
  sistema (auditoria de produto, revisão de preço), que viram notificação; o "Ativar preço promocional" dele cria uma promoção só
  da vitrine, com as mesmas travas, na mesma lista.
  - **Vale onde a promoção for ativada:** as vitrines, o PDV e os vendedores (Pedido de Venda), cada um marcado na promoção. Enquanto
    ela está ativa, o preço entra sozinho, sem senha (a decisão foi tomada ao aprovar). *(Feito na entrega 2, no PDV e no Pedido de Venda; a vitrine vem com o protótipo dela.)*
  - **A exceção na hora:** fora de promoção, o botão "Aplicar preço promocional" no item do PDV e do Pedido de Venda pede senha, e só
    quem tem a permissão no cadastro dele aplica; vai para Confirmações por senha e para o Registro de atividades, e respeita a trava do mínimo. *(Feito na entrega 2.)*
    **Muda (resposta dele em 10/nov):** a permissão é **do gerente**, não do vendedor. O vendedor só tem os preços das promoções e
    encartes ativos; fora disso, preço promocional ou desconto acima do limite dele pede a autorização do gerente. *(Feito na entrega 2
    de Usuários: quem libera é quem tem a ação `promocaoNaHora` na permissão efetiva — o perfil Gerente —, e o pedido é feito com o
    código de autorização dele; a linha passa a mostrar o nome de quem autorizou.)*
  - **Desconto por cima:** o preço promocional não conta como desconto; o desconto máximo do PDV (hoje 10%) vale sobre o promocional,
    com a mesma liberação de hoje. *(Feito na entrega 2.)*
  - **Desconto sem senha, por pessoa** (resposta dele em 10/nov, opção b): o PDV continua dando até 10% sem senha e o gerente libera
    acima disso. O parâmetro já existe (Configurações → PDV, `pdvDescontoMaximoPct`). O limite passa a ser **por pessoa**, num
    campo "desconto máximo sem senha" que só o Owner altera; quem não tem o seu fica com o de Configurações → PDV, e vale
    igual no PDV e no Pedido de Venda (hoje o Pedido não tem limite). *(Feito na entrega 2 de Usuários: o limite do PDV e do Pedido de
    Venda passa a ser o do vendedor da venda — o próprio da pessoa, o do perfil, ou o de Configurações → PDV — e a liberação é pelo
    código do gerente.)*
  - **O excedente do limite por cliente** (resposta dele em 10/nov): continua automático, numa linha a parte pelo preço de venda. Na
    linha, o botão "Aplicar preço promocional no excedente": o gerente põe a senha e diz quantas peças recebem o promocional (todas
    ou uma parte), e a linha se divide. Exemplo dele: o cliente pede 5, o máximo é 2, o gerente negocia e libera mais 2. A peça
    liberada **conta no limite total** da promoção e não passa dele. Vai para o Registro de atividades com quem e quantas.
    *(Feito na entrega 2 de Usuários: o botão "Aplicar preço promocional no excedente" aparece na linha que passou do limite por
    cliente, só para quem pode liberar; o gerente diz quantas peças recebem o promocional, a linha se divide e a peça liberada não
    consome a cota do cliente.)*
  - **O exemplo da nº 1 abre com zero vendido** (resposta dele em 10/nov: "deixa como está"). Os pedidos de exemplo 3 e 8 venderam
    pelo preço de venda e não são refeitos.
  - **Prazos:** 7 dias, até uma data, ou até acabar o estoque (este com limite de 30 dias, em Parâmetros de vendas); e, por produto, um limite de unidades.
    Ao acabar, volta sozinho ao preço de venda. *(Feito na entrega 1.)*
  - **Na vitrine:** o preço de venda riscado e o promocional como o preço (de R$ 149,90 por R$ 99,90). **Vem com o protótipo da vitrine.**
  - **Trava do preço mínimo:** promocional abaixo do mínimo da calculadora não ativa, e a vitrine mostra "Peça revisão de preço".
    Bloqueia de vez; vender abaixo do mínimo de propósito passa pela revisão de preço. *(Feito na entrega 1: a revisão deixa a linha fora.)*
  - **O riscado é verdadeiro:** não ativa se o preço de venda subiu nos últimos 30 dias (referência de mercado, não número da lei;
    CDC art. 37), lido do histórico de preço do produto. *(Feito na entrega 1; os 30 dias estão em Parâmetros de vendas.)*
  - **Sem promocional cadastrado:** o "Ativar" fica apagado e leva ao pedido de revisão de preço. **Vem com o protótipo da vitrine.**
  - **O sistema vê e encerra:** a página do produto mostra "Em promoção até <data>, ativada por <nome> pela <origem>", quem está no
    sistema pode encerrar antes, e a ativação vai para o Registro de atividades. *(Feito na entrega 1.)*
- **Usuários do sistema e Permissões de Usuários** (barganha de 10/nov/2026; a entrega 1 fez tudo o que está abaixo, menos o que diz "entrega 2"; com 15 prints do Olist: Configurações → Geral →
  Usuários do sistema, Perfil de usuários, a página do usuário e as permissões adicionais; o print é o piso da tela):
  - **4 telas em Configurações:** a lista de usuários (no padrão da casa: indicadores, busca, filtros, tabela, painel lateral), a
    página do usuário, a lista de perfis e a página do perfil. A aba "Acesso e Permissões" de Vendedores vira só o vínculo com o usuário.
  - **Um perfil por usuário, mais permissões avulsas** (opção A dele): o perfil diz tudo, e a exceção aparece no próprio usuário.
  - **O código de autorização é separado da senha de entrar** (como o "código para liberação de descontos" do Olist): quem autoriza
    digita o código dele, e o sistema sabe quem autorizou. Resolve a senha mocada de Confirmações por senha.
  - **Desconto sem senha:** o perfil traz um padrão, e a pessoa pode ter um valor próprio, que vale no lugar dele.
  - **A grade é a lista do Olist** (opção B dele): cada tela do menu é um item, e dentro dela as funções concretas (abrir e fechar o
    caixa, relatório, incluir, alterar, cancelar, ver os de outros), com "marcar todos" por aba de módulo. No fim, "Permissões de
    ações": as ações que pedem autorização, as mesmas chaves de Confirmações por senha.
  - **Os perfis de partida** são os do mapa dos canais: Owner (não se edita), Gerente, Supervisor de vendas, Vendedor interno,
    Caixa / vendedor de balcão, Representante externo.
  - **Fora do protótipo:** a confirmação da troca de senha por código no e-mail (só o aviso) e as integrações próprias do Olist.
  - **Entrega 2 (feita em 12/nov/2026, esperando o teste dele):** o código de autorização valendo no lugar da senha mocada nas
    outras telas (quem autoriza digita o código dele e o sistema sabe quem foi), e o PDV e o Pedido de Venda lendo o limite de desconto
    da pessoa. Ver §14.111.
- **Promoções e Encartes** (barganha de 04 e 09/nov/2026; a entrega 1 fez o que está marcado como feito):
  - **Quem:** o gerente e quem tiver a permissão no perfil cria; aprovar pede senha (Confirmações por senha). *(A permissão é mocada, como o resto, até Permissões de Usuários existir.)*
  - **A promoção nasce de UMA loja** (o encarte sai com a marca dela); produtos de outra loja não entram (09/nov).
  - **Situações:** rascunho, em revisão, agendada, ativa, encerrada. Começa e termina sozinha.
  - **A planilha:** SKU (obrigatório), Quantidade (número ou "ESTOQUE" = até acabar o estoque) e Preço promocional (opcional: vazio = o do
    cadastro; diferente = a revisão mostra os dois e o novo entra no cadastro ao aprovar), com o modelo para baixar.
  - **A revisão de ponta a ponta:** cada linha "ok" ou "fora", com o motivo (SKU não encontrado, abaixo do mínimo da calculadora, sem preço
    promocional, preço subiu nos últimos 30 dias, já está em outra promoção); corrige ou tira a linha antes de aprovar.
  - **Produto já em outra promoção** ativa ou agendada que se sobrepõe no período fica "fora", motivo "já está na promoção <nome>" (09/nov).
  - **Depois de aprovada** (igual à Bluesoft): preço e produtos só mudam antes de começar; depois de começar, só antecipar (o início vira
    hoje), prorrogar (nova data final) ou encerrar (09/nov).
  - **Clonar** copia a promoção, com os preços, como rascunho novo (09/nov).
  - **Limite por cliente** (unidades por cliente com o preço promocional), além do limite total por produto ("ESTOQUE" = até acabar o estoque) (09/nov).
  - **"Aplicar X% nos selecionados"** calcula o promocional dos marcados a partir do preço de venda, e passa pela mesma revisão (09/nov).
  - **Quanto vendeu:** o painel mostra as unidades vendidas contra o limite e o faturamento, lidos dos Pedidos de Venda e do PDV (09/nov); desde a entrega 2, só a venda com o preço da promoção.
  - **Menu:** Vendas → "Promoções e Encartes", logo depois do PDV (09/nov).
  - **Histórico de preço do produto** na ficha (data, de, para, quem, origem: cadastro, promoção aprovada, planilha); dele sai a trava dos
    30 dias, e a mesma aba mostra "Em promoção até…" com o link e o encerrar antes (09/nov; ele pediu nesta entrega, mesmo sendo o mais caro).
  - **"Gerar encarte":** entrega 3.
- **Hospedagem: Cloudflare Pages, com o banco no Supabase** (usuário, 10/out/2026). A Vercel fica
  como destino de migração, para quando o projeto pedir mais. **Nenhuma conta foi criada e nada foi
  publicado:** ele quer mais módulos prontos antes de subir. O detalhe está na seção 2 de
  `docs/arquitetura-roadmap-desk-company.md`.
- **GitHub:** em 13/out/2026 o usuário liberou o envio normal, a cada entrega, "até por segurança".
  O pedido de 10/out, de segurar o envio, era sobre publicar: o que continua parado é a Cloudflare.
- **Kit na compra** (usuário, 13/out/2026): o kit entra em Necessidades de Compra como item
  individual, pelo estoque mínimo do próprio kit. A necessidade de cada componente passa a juntar o
  mínimo do produto com o que falta para fechar o mínimo do kit; se a conta fecha, ela se atualiza e
  passa direto, sem aviso nem bloqueio. **Depende da composição do kit, que ainda não existe no
  cadastro:** entra junto com ela. Até lá o kit segue como produto comum, que é a primeira metade
  da regra.
- **Filtro com data inicial e final** (usuário, 13/out/2026): fica onde já existe (Movimentação de
  Estoque, Tratamento de Perdas e Giro de Estoque). As outras telas seguem com as opções prontas.
- **Exemplos como estão** (usuário, 13/out/2026): "telas mais simples, sem muita complexidade para
  teste, pode deixar os exemplos como estão, mas deixe registrado também que as próximas telas devem
  seguir um padrão melhor, corrija as que realmente precisa agora". Não se abre entrega para alinhar
  exemplo entre telas prontas. A regra da tela nova está no §14.73 e nas duas skills. **Promoções e
  Encartes** usa os produtos de Cadastros › Produtos (a ficha é a dona do preço); os pedidos de exemplo
  vendem o mesmo SKU em lojas diferentes, e a promoção só conta a venda da loja dela (§14.108).
- **Preço com mais de 2 casas** (usuário, 03/nov/2026: "por hora tranquilo"). Configurações aceita até 10 casas no
  preço (`casasPreco`, hoje 2), mas a digitação a partir dos centavos (§14.105) fixa 2 casas nos campos de preço. Quando
  alguém precisar de mais casas, o campo passa a ler o parâmetro.
- **Taxas reais da loja virtual:** na integração da API da InfinitePay, pesquisar se o Checkout Integrado cobra a tabela do Link ou a da maquininha; o protótipo usa a Bronze (decisão do usuário). A vitrine dá o mesmo desconto Pix.
- **A barra que ficou: caiu em 16/nov/2026.** A decisão de 19/out (Necessidades de Compra, CRM e Metas com barra em 1280) foi reaberta por ele; as três passaram a caber sem barra e a suíte `teste_barra_tabelas.py` passou a exigir isso (`PENDENTES` vazio). Os itens da Ordem de Compra e do Pedido de Venda seguem sem barra, com o código comprido (SKU, GTIN) cortando alguns caracteres em 1280. Detalhe no §14.114.

## Para a próxima revisão geral

A revisão geral de 02-03/nov/2026 foi feita: os 17 itens, em cinco pacotes (§14.102 a §14.106). O item 2 dela saiu no
pacote D de 16/nov (§14.116) e o item 3 no pacote E de 17/nov (§14.117); não ficou pedido solto da revisão geral.

Do teste dele na entrega 1 de Promoções e Encartes (09/nov/2026, com prints):

Do teste dele na entrega 2 de Promoções e Encartes (10/nov/2026, com prints; "vamos avaliar depois"):

Pedidos dele no teste da entrega 2 de Usuários (16/nov/2026, com prints):

O plano da revisão, com as escolhas dele de 16/nov para os itens 6, 10, 11, 18 e 19, está em
[docs/plano-revisao-geral-16nov.md](docs/plano-revisao-geral-16nov.md).

## Esperando decisão do usuário

As quatro perguntas da entrega 2, o mapa dos canais e a barganha de Usuários e Permissões foram respondidos em 10/nov e estão em "Decidido". Falta:

1. **Reenviar as skills do ERP pelo claude.ai, se quiser.** As regras que o Claude segue no ERP
   (o padrão de tela e o portão de qualidade) existem em dois lugares: nesta máquina, onde são
   atualizadas a cada entrega, e na conta dele no claude.ai, de onde o plugin foi enviado. A cópia
   da conta ficou com o texto antigo. Só faz diferença se ele trabalhar no ERP fora deste
   computador; para atualizar, reenvia por lá a pasta
   `C:\Claude AI\Skills\Skills ERP System\desk-company-erp`.

## O que está no HISTORICO.md

O que cada entrega fez e como foi testada; o balanço de 15/out/2026 (o que existe, o que ganhamos, a projeção e as
prioridades); o que continua sendo dado de exemplo; e o que ficou de fora da Movimentação de Estoque, de Necessidades de
Compra e de Giro, de propósito.

## Para retomar numa conversa nova

1. Abra o editor na pasta `C:\Claude AI\Desk Company`.
2. Primeira mensagem: "vamos para onde paramos", com os prints do próximo módulo, se for o caso. É
   para ler este arquivo e seguir do próximo da fila. O `HISTORICO.md` só se abre quando precisar do passado.
3. Para ver as telas: `node _ferramentas/servidor.js` na pasta `ERP System`, e depois
   `http://localhost:3000/<pasta>/<arquivo>`. O servidor cai quando a sessão fecha.
4. Antes de dar algo por pronto: `python selo.py --rodar` na pasta `_ferramentas`.
5. Commit e envio ao GitHub a cada entrega (liberado pelo usuário em 13/out/2026). Nada é publicado
   na Cloudflare ainda.
