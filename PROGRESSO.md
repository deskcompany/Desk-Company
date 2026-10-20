# Progresso do ERP Desk Company

*Atualizado em 19/out/2026: a entrega 1 do Vale-compra, aprovada pelo usuário.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Vale-compra, entrega 1: testada e aprovada pelo usuário em 19/out** (§14.89; o que foi feito está no HISTORICO.md),
junto com a barra de paginação em Comissões, Reposição, Transferência e Metas. **O próximo é a entrega 2: o vale se usa.**

**Entregas que faltam do Vale-compra:** (2) o vale se usa, no PDV e no Pedido de Venda, em parte se o cliente quiser, e
Formas de Recebimento; (3) o vale nasce da Devolução e do pagamento de Comissão.

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
2. **Vale-compra, entregas 2 e 3** (a 1 está feita, §14.89): (2) o vale se usa, no PDV e no Pedido de Venda, com Formas de
   Recebimento; (3) o vale nasce da Devolução e do pagamento de Comissão. Liga o vale-troca reservado nas telas prontas.
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

- **Para a próxima revisão geral: a barra do caminho** (usuário, 19/out/2026, "não mexa agora"). Ele quer usá-la como
  no Olist, para voltar uma tela ou mudar de módulo. Análise: é um bloco comum (`renderBreadcrumb`) em 87 telas, e cada
  nome é um texto, não um link. Clicar num nome do meio só corta o caminho e troca o título, sem sair da tela. O primeiro
  nome sempre leva ao Início, mesmo quando é o módulo: em "Finanças › Vale-compra › VC-6", "Finanças" abre o Início.
  Proposta para a revisão: o módulo abre o menu daquele módulo, a tela de lista leva à lista (com os filtros, como o
  "Voltar" faz) e o último nome continua parado. Consertar no bloco comum, nas 87 de uma vez, com uma suíte que clica em
  cada nome de cada tela.

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
