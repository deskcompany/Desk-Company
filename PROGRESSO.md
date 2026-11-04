# Progresso do ERP Desk Company

*Atualizado em 04/nov/2026: a calculadora de precificação foi aprovada por ele; o estoque das embalagens fica como está, com a rodada de correção segurada por ele; as regras do preço promocional foram barganhadas e entram com a vitrine. O próximo a fazer é o desconto da venda nossa (opcional) ou o protótipo da vitrine.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Estoque das embalagens: feito em 03/nov/2026 e testado por ele em 03-04/nov.** Ele pediu para segurar como está; a rodada de correção (motivos de acerto, prejuízo, inventário, ordem de compra e movimentação) é o item 1 do "Próximo da fila". O que foi feito está no HISTORICO.md e o detalhe no §14.107.

**Calculadora de precificação: testada e aprovada por ele em 04/nov/2026.** O que foi feito está no HISTORICO.md e o detalhe no §14.101. As duas observações do teste estão abaixo: várias embalagens na calculadora (revisão geral, item 3) e o que o preço promocional faz (esperando decisão dele).

**Custos do E-commerce: concluído em 30/out/2026.** As quatro entregas e os ajustes estão no HISTORICO.md, e o detalhe no §14.95 a §14.100. Tela: `http://localhost:3000/vendas/pagina-vendas-custos-ecommerce.html`. As entregas 1 a 3 e a primeira rodada da 4 ele testou e aprovou; os testes finais do ajuste da 4 (a estimativa pelo cadastro, a Separação que não mexe no custo, o "Total de volumes", a troca) ele delegou ao principal, que os rodou no navegador em 30/out: 61 itens, nenhuma falha. A baixa da embalagem no estoque, que tinha ficado de fora, foi feita em 03/nov. O que mais ficou de fora está na lista da revisão geral (os itens 6, 9, 10, 12, 16 e 17 mexem nesta área; o 9 e o 10 mudam números do lucro).

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

1. **Rodada de correção do estoque das embalagens** (pedido dele em 03/nov, depois de testar a entrega; começa pela barganha). **Segurada por ele em 04/nov:** a tela fica como está, e ele avisa quando voltar:
   - **Motivos de acerto:** o "Acertar saldo" passa a escolher o motivo de uma lista, em vez de texto solto. Ver se a lista é a de Configurações → Motivos de Perda, que já existe.
   - **Prejuízo pelo motivo:** o acerto para menos por avaria, quantidade errada etc. gera prejuízo, conforme o motivo, como a perda de produto em Tratamento de Perdas.
   - **Inventário geral:** as embalagens (caixas, envelopes, sacolas, insumos) aparecem no Inventário para serem contadas.
   - **Ordem de compra:** em Necessidades de Compra, o bloco das embalagens gera ordem de compra, e não "Dar entrada", para seguir o fluxo normal (ordem → nota → entrada). A decidir: a embalagem entra na Ordem de Compra sem SKU de produto?
   - **Movimentação:** entrada, baixa e acerto de embalagem aparecem em Estoque → Movimentação de Estoque, e não só no Registro de atividades.
2. **Desconto da venda nossa na hora da venda** (ideia dele em 30/out, opcional): a venda sem ninguém recebendo comissão e paga no Pix pode somar o desconto da comissão ao do Pix. A calculadora já mostra até onde dá; falta a opção no PDV e no Pedido de Venda, e a vitrine depende do protótipo dela.
3. **Gateways de Pagamento:** falta o protótipo da vitrine, que agora também leva as regras do preço promocional (em "Decidido").
4. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
5. **Os outros itens pós-MVP** (Margem de Contribuição, Relatórios, Notas Fiscais, Integrações). Módulo novo começa pela
   barganha, com os prints, e já nasce com o exemplo no padrão (§14.73).

**Saiu da fila, por decisão do usuário, e volta quando houver banco de dados:** os alinhamentos de
exemplo (X1 a X7); os painéis dos outros cadastros (C3 a C8); os links V4 e L4, que dependiam dos
alinhamentos; o que sobrou do G3 (a página do romaneio conhecer os 9 romaneios, e "abrir a nota"
na Entrada de Notas, que é o item E3); e as cópias do número da meta (R6), que ele tirou em seguida.

## Decidido, e ainda não feito de propósito

- **Preço promocional** (barganhado com o usuário em 04/nov/2026; entra junto com o protótipo da vitrine). O preço tem um dono só, o
  sistema: o promocional é cadastrado na aba Preços do produto, e a vitrine só ativa e desativa. O painel da vitrine não cadastra nem
  muda preço: mostra os produtos da loja e manda pedidos ao sistema (auditoria de produto, revisão de preço), que viram notificação.
  - **Vale só na vitrine.** O PDV e os pedidos do sistema seguem no preço de venda.
  - **Prazos:** 7 dias, até uma data, ou até acabar o estoque (este com limite de 30 dias). Ao acabar, volta sozinho ao preço de venda.
  - **Na vitrine:** o preço de venda riscado e o promocional como o preço (de R$ 149,90 por R$ 99,90).
  - **Trava do preço mínimo:** promocional abaixo do mínimo da calculadora não ativa, e a vitrine mostra "Peça revisão de preço".
    Bloqueia de vez; vender abaixo do mínimo de propósito passa pela revisão de preço.
  - **O riscado é verdadeiro:** não ativa se o preço de venda subiu nos últimos 30 dias (referência de mercado, não número da lei;
    CDC art. 37). Pede o histórico de preço do produto, que o cadastro ainda não guarda.
  - **Sem promocional cadastrado:** o "Ativar" fica apagado e leva ao pedido de revisão de preço.
  - **O sistema vê e encerra:** a página do produto mostra "Em promoção até <data>, ativada por <nome> pela vitrine", quem está no
    sistema pode encerrar antes, e a ativação vai para o Registro de atividades.
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

- **Preço com mais de 2 casas** (usuário, 03/nov/2026: "por hora tranquilo"). Configurações aceita até 10 casas no
  preço (`casasPreco`, hoje 2), mas a digitação a partir dos centavos (§14.105) fixa 2 casas nos campos de preço. Quando
  alguém precisar de mais casas, o campo passa a ler o parâmetro.
- **Taxas reais da loja virtual:** na integração da API da InfinitePay, pesquisar se o Checkout Integrado cobra a tabela do Link ou a da maquininha; o protótipo usa a Bronze (decisão do usuário). A vitrine dá o mesmo desconto Pix.
- **A barra que ficou** (usuário, 19/out/2026, depois de ouvir o custo): Necessidades de Compra, CRM e Metas seguem com
  barra em 1280 (de 95 a 160px), e os itens da Ordem de Compra e do Pedido de Venda seguem sem barra, com o código comprido
  (SKU, GTIN) cortando alguns caracteres em 1280. De 1440 para cima nada disso acontece. Volta quando as telas forem
  refeitas na produção, ou antes se alguém trabalhar em 1280 todo dia. A suíte `teste_barra_tabelas.py` segura as três
  como estão.

## Para a próxima revisão geral

A revisão geral de 02-03/nov/2026 foi feita: os 17 itens, em cinco pacotes (§14.102 a §14.106). Ficou um item dela,
e entrou uma decisão:

1. **Os campos de tamanho de Embalagens continuam desalinhados** (03/nov, com print no tema claro, editando a caixa
   Flex P). O item 16 da revisão passada alargou o painel lateral de 400 para 540 px e mediu certo a 1280 e 1440, mas
   na janela dele "Comprimento (cm)" ainda quebra em duas linhas e a caixa desce. O usuário repetiu: pode aumentar a
   largura do painel lateral até caber. Medir na largura real da janela dele (menor que 1280, ou com zoom), nos dois
   temas, no cadastro novo e na edição, e o mesmo nos outros tipos (envelope, rolo).
2. **Contas a Pagar: a aba "atrasadas" ignora o período** (aprovado pelo usuário em 03/nov). A lista abre no período
   "mês" (decisão de 23/set), e por isso em 02/11 o card "Vencidas" dizia 8 e a aba "atrasadas" dizia 2. Conta vencida
   em outubro continua atrasada em novembro. Conferir se Contas a Receber tem a mesma aba e o mesmo defeito.
3. **Calculadora de preço: mais de uma embalagem** (pedido dele em 04/nov, no teste da calculadora). O campo "Caixa" vira uma lista com caixa de
   seleção: marcar a caixa e o saquinho da loja (ou mais de uma), só entre as embalagens ativas com estoque. Exemplo dele: a garrafa térmica vai numa
   caixa e dentro de um saquinho da loja. Os insumos que entram sozinhos continuam entrando.

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
