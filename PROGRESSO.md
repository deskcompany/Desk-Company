# Progresso do ERP Desk Company

*Atualizado em 30/out/2026: a calculadora de precificação está feita (na aba Preços do produto) e espera a revisão dele. Custos do E-commerce está concluído. O próximo da fila é o estoque das embalagens, já aprovado por ele.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Calculadora de precificação: feita em 30/out/2026, esperando a revisão dele.** Mora na aba Preços do produto, no botão "Calcular preço" (abra `http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1`). Tem o custo do produto (o da aba Custos, de compra ou médio, como Custos do E-commerce lê), a embalagem completa (a caixa do cadastro do produto mais os insumos que entram sozinhos na loja), o frete, a margem desejada, as parcelas, e o imposto e a comissão de Parâmetros de Vendas. Mostra quatro sugestões (Varejo ,90, Abaixo da faixa, Redondo e Exato), a conta aberta, a margem por forma de pagamento, a "venda nossa" sem comissão e o preço mínimo. A taxa e a tarifa vêm do gateway da loja virtual da loja do produto, a mesma fonte de Custos do E-commerce (hoje a tabela do Link), e por isso acompanha sozinha o item 10 da revisão geral. Parâmetros de Vendas ganhou a comissão padrão (5%) e as parcelas da vitrine (3).
- **Só preenche campos:** o preço continua editável à mão, e só o botão "Aplicar preço" mexe no Preço de venda, na lista Padrão e no Markup, guarda o cálculo (`deskCalculoPreco`, por produto) e escreve no Registro de atividades ("Aplicar o preço calculado").
- **Decidido:** o markup é preço ÷ custo do produto; o Exato sobe ao centavo (a margem nunca fica abaixo da pedida); a embalagem é a de um pedido de uma peça (o produto indo sozinho: junto com outro, a margem só melhora). A pesquisa por trás das quatro sugestões está em `docs/pesquisa-psicologia-de-precos.md`.
- **Limite, de propósito:** a lista de produtos, o PDV e os pedidos seguem com o preço do exemplo; o cadastro novo (`?novo=1`) calcula mas não grava o cálculo, até haver banco. A suíte é `teste_calculadora.py`; o detalhe técnico, o §14.101.

**Custos do E-commerce: concluído em 30/out/2026.** As quatro entregas e os ajustes estão no HISTORICO.md, e o detalhe no §14.95 a §14.100. Tela: `http://localhost:3000/vendas/pagina-vendas-custos-ecommerce.html`. As entregas 1 a 3 e a primeira rodada da 4 ele testou e aprovou; os testes finais do ajuste da 4 (a estimativa pelo cadastro, a Separação que não mexe no custo, o "Total de volumes", a troca) ele delegou ao principal, que os rodou no navegador em 30/out: 61 itens, nenhuma falha. O que ficou de fora de propósito está em "Decidido, e ainda não feito de propósito" (a baixa da embalagem no estoque) e na lista da revisão geral (os itens 6, 9, 10, 12, 16 e 17 mexem nesta área; o 9 e o 10 mudam números do lucro).

Confirmado por ele em 22/out: "do mês" vai do dia 1 até hoje; os cards somam a lista toda. **Recebimento da InfinitePay:** a venda no cartão, mesmo parcelada, cai
inteira no dia útil seguinte, já sem a taxa (o gateway da loja virtual é "Antecipado"). **A antecipação saiu do módulo:** o cadastro de gateway não tem taxa de
antecipação à parte, e na InfinitePay ela já está na taxa.

**Vale-compra: concluído.** As três entregas foram testadas e aprovadas pelo usuário (a 3 em 20/out, junto com o conserto
que faz a Devolução ficar gravada); o que foi feito está no HISTORICO.md e o detalhe no §14.89 a §14.91.

**Gateways de Pagamento: as entregas 1 e 2 e os ajustes do teste, testados e aprovados pelo usuário em 21/out** (§14.92 a
§14.94; o que foi feito está no HISTORICO.md). Ficaram três consertos pedidos no teste (comissão sem o vale-compra, a loja
virtual com as taxas da Bronze, os feriados móveis), que foram para a revisão geral (decisão dele em 21/out: a cota semanal
está no fim e ele prefere construir agora). Falta o protótipo da vitrine, no "Próximo da fila".

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
| **Protótipo** | itens do menu que já têm tela HTML validada | **45 de 55 (82%)**, em 90 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 80% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

Eram 80 telas e 41 de 55 itens com tela até 12/out/2026.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 13 de 14 | Relatórios de Estoque |
| Vendas | 5 de 8 | Notas Fiscais, Margem de Contribuição, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 4 de 5 | Relatórios Finanças |
| Integrações | 1 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Relatórios de Integrações |
| Configurações | hub com 20 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## Próximo da fila

Refeita em 30/out, depois da calculadora (a lista de 19/out e os porquês estão em
"Prioridades dos próximos passos", no HISTORICO.md).

1. **Estoque das embalagens** (aprovado por ele em 30/out, opção A). As regras:
   - O estoque mora na própria tela de Embalagens, com o botão "Dar entrada" (quantidade, custo, fornecedor e nota; os dois últimos são opcionais). A lista mostra o saldo e o mínimo, avisa quando está abaixo do mínimo, e Necessidades de Compra ganha um bloco para elas.
   - A baixa é automática quando a Conferência de Saída fecha, nunca na Separação. Falta de saldo não trava a expedição: o saldo fica negativo e avisa. Pedido cancelado depois de fechar não devolve.
   - O saldo é único por empresa, sem depósito. Cada entrada recalcula o custo médio, que passa a ser o custo do cadastro, e o pedido guarda o custo do dia.
   - O insumo ganha o campo "Rende": 1 rolo de fita que rende 50 pedidos, com R$ 15, vira R$ 0,30 por pedido (de fábrica 1).
   - O saldo pode ser acertado à mão, com motivo.
   - Na produção a entrada vem pela nota, como qualquer item.
2. **Desconto da venda nossa na hora da venda** (ideia dele em 30/out, opcional): a venda sem ninguém recebendo comissão e paga no Pix pode somar o desconto da comissão ao do Pix. A calculadora já mostra até onde dá; falta a opção no PDV e no Pedido de Venda, e a vitrine depende do protótipo dela.
3. **Gateways de Pagamento:** falta o protótipo da vitrine. Os três consertos do teste estão na revisão geral (itens 9 a 11).
4. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
5. **Os outros itens pós-MVP** (Margem de Contribuição, Relatórios, Notas Fiscais, Integrações). Módulo novo começa pela
   barganha, com os prints, e já nasce com o exemplo no padrão (§14.73).

**Saiu da fila, por decisão do usuário, e volta quando houver banco de dados:** os alinhamentos de
exemplo (X1 a X7); os painéis dos outros cadastros (C3 a C8); os links V4 e L4, que dependiam dos
alinhamentos; o que sobrou do G3 (a página do romaneio conhecer os 9 romaneios, e "abrir a nota"
na Entrada de Notas, que é o item E3); e as cópias do número da meta (R6), que ele tirou em seguida.

## Decidido, e ainda não feito de propósito

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
  exemplo entre telas prontas. A regra da tela nova está no §14.73 e nas duas skills.

- **A embalagem ainda não sai do estoque** (30/out/2026): a Conferência de Saída confirma caixa, tag e fita, e o custo entra em Custos do E-commerce, mas nenhum saldo baixa,
  porque as embalagens só existem no cadastro, sem estoque próprio. Ficou fora da entrega 4 com ele sabendo. **Saiu desta lista no mesmo dia:** ele aprovou fazer, e virou o item 1 do "Próximo da fila".
- **A barra que ficou** (usuário, 19/out/2026, depois de ouvir o custo): Necessidades de Compra, CRM e Metas seguem com
  barra em 1280 (de 95 a 160px), e os itens da Ordem de Compra e do Pedido de Venda seguem sem barra, com o código comprido
  (SKU, GTIN) cortando alguns caracteres em 1280. De 1440 para cima nada disso acontece. Volta quando as telas forem
  refeitas na produção, ou antes se alguém trabalhar em 1280 todo dia. A suíte `teste_barra_tabelas.py` segura as três
  como estão.

## Para a próxima revisão geral

Revisão em andamento desde 02/nov/2026: pacotes 1 (visual) e 2 (navegação) feitos; faltam cards (3 a 5), digitação (6 e 17) e regras de dinheiro (9 a 11).

Pedidos do usuário de 19 a 26/out/2026, **para não mexer agora**: entram juntos quando ele decidir fazer a próxima auditoria e
revisão. Até lá, seguimos construindo. Cada item vira conserto de componente, em todas as telas de uma vez, com suíte.

3. **Cards que filtram também nas filas de Logística.** Devolução e Rastreamento têm cards no topo que filtram a tabela;
   Separação, Conferência de Saída e Expedição não têm cards. **Não há critério registrado:** as três filas nasceram antes
   do padrão de indicadores, e a proposta G4 (`docs/melhorias-modulos-prontos.md`, 13/out) também as deixou de fora. Na
   revisão: dar às três os cards que filtram, no padrão de Contas a Pagar.
4. **Controle de Estoques: os cards no padrão de Contas a Pagar.** Só "Abaixo do mínimo" reage, e escurece em vez de
   ficar com a borda azul; "A endereçar" e "Bloqueado" não mostram efeito nenhum (hoje são links para outras telas).
   Todos devem mostrar que filtram, com a borda azul quando ativos.
5. **Necessidades de Compra: os cards não filtram.** Mesmo padrão.
6. **Campo de dinheiro digitado a partir dos centavos.** Hoje o campo mostra "0,00" e o que se digita entra como texto.
   O usuário quer a digitação da direita para a esquerda: com "0,00" na tela, digitar 2 dá 0,02; 0 dá 0,20; 0 dá 2,00;
   0 dá 20,00. Digitar 250 dá 2,50; digitar 1589 dá 15,89. Vale para **todo campo de valor em reais**: mapear todos na
   revisão e fazer um componente só. Atenção ao campo que aceita valor ou percentual ("Ex: 3,00 ou 10%", o desconto do
   PDV), que precisa de regra própria. **Reforçado em 30/out** no cadastro de Embalagens (campo Custo): vale em todas as telas.
9. **a comissão não conta o vale-compra**: hoje a base é o total menos o frete; passa a ser o total menos o frete e menos o que o pedido pagou com vale, para vendedor e afiliado (a comissão é sobre o que foi vendido de fato, já com todos os descontos, o Pix/dinheiro incluído) Ele perguntou se fazia sentido e concordamos: o vale não traz dinheiro novo (devolução: a venda original já comissionou; cortesia: presente da loja; comissão em vale: evitaria comissão sobre comissão).
10. **a loja virtual usa as taxas da Bronze da maquininha** no protótipo, decisão dele, e a vitrine dá o mesmo desconto Pix. **Pesquisa obrigatória na integração da API da InfinitePay:** o Checkout Integrado cobra a tabela do Link de Pagamento (mais cara: 4,20% à vista na tabela geral) ou a da maquininha/InfiniteTap? A resposta decide as taxas reais
11. **os feriados nacionais móveis entram no dia útil**, calculados sozinhos para qualquer ano (fixos pela data, móveis pela Páscoa): Carnaval (segunda e terça, banco fechado), Sexta-feira Santa e Corpus Christi. Feriado estadual e municipal (cadastro à mão) fica para depois.
17. **Campo de peso digitado a partir das gramas** (30/out): começa em gramas e cresce conforme se digita, no mesmo jeito do campo de dinheiro (item 6): 1 dá 0,001 kg; 15 dá 0,015; 150 dá 0,150; 1500 dá 1,500. Vale para **todo campo de peso**: mapear todos na revisão e fazer junto com o item 6. Mostrado no cadastro de Embalagens.

*Custos do E-commerce, entrega 2 (27/out):* o vale de cortesia passou a sair da venda do resultado do pedido, mas a comissão **não** mudou por isso; o **item 9 continua aqui, sem mudar** (a base da comissão ainda é o total menos o frete).

## Esperando decisão do usuário

Uma pendência, que é dele:

1. **Reenviar as skills do ERP pelo claude.ai, se quiser.** As regras que o Claude segue no ERP
   (o padrão de tela e o portão de qualidade) existem em dois lugares: nesta máquina, onde são
   atualizadas a cada entrega, e na conta dele no claude.ai, de onde o plugin foi enviado. A cópia
   da conta ficou com o texto antigo. Só faz diferença se ele trabalhar no ERP fora deste
   computador; para atualizar, reenvia por lá a pasta
   `C:\Claude AI\Skills\Skills ERP System\desk-company-erp`.

O defeito dos links do chat que não traziam o navegador para a frente era da sessão do editor e
sumiu sozinho (confirmado por ele em 13/out).

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
