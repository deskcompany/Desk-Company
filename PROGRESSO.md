# Progresso do ERP Desk Company

*Atualizado em 21/out/2026: Gateways de Pagamento, ajustes do teste da entrega 2 feitos (esperando o teste do usuário).*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Vale-compra: concluído.** As três entregas foram testadas e aprovadas pelo usuário (a 3 em 20/out, junto com o conserto
que faz a Devolução ficar gravada); o que foi feito está no HISTORICO.md e o detalhe no §14.89 a §14.91.

**Gateways de Pagamento: as entregas 1 e 2 e os ajustes do teste, testados e aprovados pelo usuário em 21/out** (§14.92 a
§14.94; o que foi feito está no HISTORICO.md). Ficaram três consertos pedidos no teste (comissão sem o vale-compra, a loja
virtual com as taxas da Bronze, os feriados móveis) e a calculadora de precificação: estão no item 2 e 3 de "Próximo da fila".
**O próximo é decidir com ele por onde seguir:** esses consertos, a calculadora, a vitrine ou a F0.

**Como trabalhamos desde 19/out** (combinado com o usuário, depois de ver que o tempo e o consumo não caíram com o
executor): o mesmo executor é reaproveitado quando a tarefa continua a anterior; o plano manda os trechos exatos
(arquivo e linhas); a prova com defeitos injetados fica em 5 a 8 defeitos, na lógica nova; e os retornos de teste vêm
num pacote só. Medir nas próximas rodadas.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **44 de 55 (80%)**, em 88 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 80% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

Eram 80 telas e 41 de 55 itens com tela até 12/out/2026.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 13 de 14 | Relatórios de Estoque |
| Vendas | 4 de 8 | Notas Fiscais, Margem de Contribuição, Custos do E-commerce, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 4 de 5 | Relatórios Finanças |
| Integrações | 1 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Relatórios de Integrações |
| Configurações | hub com 19 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## Próximo da fila

Refeita em 19/out, depois da varredura da barra (a lista completa e os porquês estão em "Prioridades dos próximos passos", no HISTORICO.md).

1. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
2. **Gateways de Pagamento:** as entregas 1 e 2 e os ajustes do teste estão feitos e aprovados (21/out); falta o protótipo
   da vitrine.
   Os três consertos pedidos no teste dos ajustes foram para "Para a próxima revisão geral" (itens 9 a 11).
3. **Calculadora de precificação** (pedido dele em 21/out, começa pela barganha): custo do produto, frete da compra,
   embalagem completa (um item só, em vez de separar tag, caixa e saco), a taxa da maquininha e a margem desejada (20%,
   30%, 50%), dando o custo total e o preço final para o cliente. Onde mora: no cadastro do produto ou como item próprio
   (decidir na barganha; os itens Margem de Contribuição e Custos do E-commerce do menu são vizinhos).
4. **Os 11 itens pós-MVP** (Margem, Custos, Relatórios, Notas Fiscais, Integrações). Módulo novo começa pela
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

- **A barra que ficou** (usuário, 19/out/2026, depois de ouvir o custo): Necessidades de Compra, CRM e Metas seguem com
  barra em 1280 (de 95 a 160px), e os itens da Ordem de Compra e do Pedido de Venda seguem sem barra, com o código comprido
  (SKU, GTIN) cortando alguns caracteres em 1280. De 1440 para cima nada disso acontece. Volta quando as telas forem
  refeitas na produção, ou antes se alguém trabalhar em 1280 todo dia. A suíte `teste_barra_tabelas.py` segura as três
  como estão.

## Para a próxima revisão geral

Pedidos do usuário de 19 a 21/out/2026, **para não mexer agora**: entram juntos quando ele decidir fazer a próxima auditoria e
revisão. Até lá, seguimos construindo. Cada item vira conserto de componente, em todas as telas de uma vez, com suíte.

1. **A barra do caminho navega.** Hoje cada nome é texto: clicar num nome do meio só corta o caminho e troca o título, e o
   primeiro nome sempre leva ao Início, mesmo quando é o módulo ("Finanças" em "Finanças › Vale-compra › VC-6" abre o
   Início). É o bloco comum `renderBreadcrumb`, em 87 telas. Proposta: o módulo abre o menu daquele módulo, a tela de
   lista leva à lista com os filtros, e o último nome fica parado.
2. **O "voltar" vira botão no cabeçalho, como em Vale-compra.** Hoje as páginas de detalhe têm um link pequeno embaixo
   da barra do caminho ("voltar para o extrato", "Voltar pra listagem"). O usuário prefere o botão "Voltar para <lista>"
   à direita do título, o primeiro da fila dos botões, como "Voltar para Vale-compra". Opinião registrada: concordo; o
   botão é o caminho óbvio de volta (com os filtros) e a barra do caminho fica para pular de nível ou de módulo. Os dois
   convivem, e o link de baixo sai.
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
   PDV), que precisa de regra própria.
7. **O seletor Pessoa Física / Pessoa Jurídica justo.** O fundo cinza é bem mais largo que as duas opções, em Clientes,
   Fornecedores e Vendedores (cadastro novo e página). Deve ter a largura só das duas opções.
8. **O campo de número com sufixo ("dias") desnivelado nos cards de Configurações** (21/out, com print de Parâmetros de
   Estoque: Conferência de compra e Endereçamento). A caixa do número fica cerca de 1 px mais alta em cima e embaixo
   que a do "dias", e o card fica com um degrau. Ele viu em Estoque, em todos os cards; mapear na revisão todos os
   campos número + sufixo das telas de Configurações (e onde mais houver) e deixar número e sufixo com a mesma altura.
9. **a comissão não conta o vale-compra**: hoje a base é o total menos o frete; passa a ser o total menos o frete e menos o que o pedido pagou com vale, para vendedor e afiliado (a comissão é sobre o que foi vendido de fato, já com todos os descontos, o Pix/dinheiro incluído) Ele perguntou se fazia sentido e concordamos: o vale não traz dinheiro novo (devolução: a venda original já comissionou; cortesia: presente da loja; comissão em vale: evitaria comissão sobre comissão).
10. **a loja virtual usa as taxas da Bronze da maquininha** no protótipo, decisão dele, e a vitrine dá o mesmo desconto Pix. **Pesquisa obrigatória na integração da API da InfinitePay:** o Checkout Integrado cobra a tabela do Link de Pagamento (mais cara: 4,20% à vista na tabela geral) ou a da maquininha/InfiniteTap? A resposta decide as taxas reais
11. **os feriados nacionais móveis entram no dia útil**, calculados sozinhos para qualquer ano (fixos pela data, móveis pela Páscoa): Carnaval (segunda e terça, banco fechado), Sexta-feira Santa e Corpus Christi. Feriado estadual e municipal (cadastro à mão) fica para depois.

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
