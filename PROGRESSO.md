# Progresso do ERP Desk Company

*Atualizado em 20/out/2026: a entrega 3 do Vale-compra, feita e esperando o teste do usuário.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Vale-compra, entrega 3: o vale nasce da Devolução e do pagamento de Comissão. Feita em 20/out/2026, esperando o teste do
usuário** (§14.91). A Devolução finaliza em vale (a forma "Vale-compra" no lugar do reservado "Vale-troca"; o vale nasce ao
finalizar, e cancelar a devolução cancela o vale intacto ou é barrado se ele já foi usado). O afiliado, e só ele, recebe a comissão em
vale (sem bônus, na loja dele), e o pagamento aparece em Contas a Pagar já pago, só leitura, sem saída do Caixa. Com ela as três
entregas do Vale-compra estão feitas (a entrega 2 foi testada e aprovada em 20/out; o texto dela está no HISTORICO.md).

**O que conferir** (com o servidor de preview de pé em `http://localhost:3000`):
1. A devolução que dá para finalizar com vale:
   [DV-0009, de Bruno Carvalho](http://localhost:3000/logistica/pagina-logistica-devolucao-detalhe.html?id=4). Em "Como o
   dinheiro volta" escolha Vale-compra, clique em Salvar alterações e depois em Mais ações → Finalizar (R$ 414,80, na Desk Shope):
   o vale só nasce ao finalizar, e a tela avisa isso depois de salvar. Agora a devolução continua salva ao sair e voltar (ela é
   gravada no navegador). As outras devoluções, de clientes fora do cadastro, mostram por que a opção não vale. Depois de
   finalizada, a forma trava, e cancelar a devolução cancela o vale.
2. O vale gerado: a [lista do Vale-compra](http://localhost:3000/financas/pagina-financas-vale-compra.html) (o novo é o VC-6, de
   origem Devolução, com o link de volta para a devolução).
3. A conta de afiliado pagando em vale:
   [Bruno Carvalho](http://localhost:3000/financas/pagina-financas-comissoes-detalhe.html?id=a1) (saldo R$ 51,20, Desk Brands).
   "Realizar pagamento", forma Vale-compra: o vencimento trava em hoje e o texto diz o que vai acontecer.
4. O título em Contas a Pagar: o COM-4 que esse pagamento criou, em
   [Contas a Pagar](http://localhost:3000/financas/pagina-financas-contas-pagar-detalhe.html?id=9004) (já pago, só leitura, sem
   dar baixa; o Caixa não ganha lançamento).
5. A conta de vendedor, sem a opção:
   [Marina Costa](http://localhost:3000/financas/pagina-financas-comissoes-detalhe.html?id=v1): "Realizar pagamento" só tem
   Pix, Transferência, Boleto e Dinheiro.

**Barganha da entrega 3, aprovada pelo usuário em 20/out** (ele escolheu as cinco recomendações):
- **Devolução: o vale nasce ao finalizar**, com o total da devolução, na loja do pedido de origem. Escolher a forma só anota.
- **Devolução finalizada com vale e depois cancelada:** o vale intacto é cancelado junto; vale já usado, mesmo em parte,
  impede cancelar a devolução (o caminho é um acerto).
- **Comissão: só afiliado recebe em vale** (vendedor é funcionário, e comissão de funcionário é salário, em dinheiro).
- **Sem bônus:** R$ 100 de comissão viram R$ 100 de vale, na loja da comissão.
- **A comissão paga em vale aparece em Contas a Pagar já paga**, forma Vale-compra, só leitura, sem saída do Caixa (o
  espelho do que a entrega 2 fez em Contas a Receber).

**Como trabalhamos desde 19/out** (combinado com o usuário, depois de ver que o tempo e o consumo não caíram com o
executor): o mesmo executor é reaproveitado quando a tarefa continua a anterior; o plano manda os trechos exatos
(arquivo e linhas); a prova com defeitos injetados fica em 5 a 8 defeitos, na lógica nova; e os retornos de teste vêm
num pacote só. Medir nas próximas rodadas.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **43 de 55 (78%)**, em 86 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 78% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
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
| Integrações | 0 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Gateways de Pagamento, Relatórios de Integrações |
| Configurações | hub com 19 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## Próximo da fila

Refeita em 19/out, depois da varredura da barra (a lista completa e os porquês estão em "Prioridades dos próximos passos", no HISTORICO.md).

1. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
2. **Vale-compra:** as três entregas estão feitas (§14.89, §14.90 e §14.91), esperando o teste da 3 (o vale que nasce da Devolução
   e do pagamento de Comissão de afiliado).
3. **Gateways de Pagamento**, o único item do menu no caminho do MVP, e o protótipo da vitrine.
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

Pedidos do usuário de 19/out/2026, **para não mexer agora**: entram juntos quando ele decidir fazer a próxima auditoria e
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
