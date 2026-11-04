# Progresso do ERP Desk Company

*Atualizado em 03/nov/2026: o estoque das embalagens está feito (selo verde) e espera a revisão dele, junto com a calculadora de precificação. A revisão geral de 02-03/nov também está feita, com dois itens anotados para a próxima. O próximo da fila é o desconto da venda nossa na hora da venda (opcional) ou o protótipo da vitrine.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Estoque das embalagens: feito em 03/nov/2026, esperando a revisão dele.** Mora na tela de Embalagens (abra `http://localhost:3000/cadastros/pagina-cadastros-embalagens.html`) e em Necessidades de Compra (`http://localhost:3000/estoque/pagina-estoque-necessidades-compra.html`). O que conferir:
- **A lista:** cada embalagem diz "Saldo X · mín. Y"; Flex G, CE-02 e a Tag Desk Brands (de exemplo) trazem o selo "Abaixo do mínimo"; a fita diz "R$ 15,00 a unidade · rende 50 (R$ 0,30 por pedido)".
- **Dar entrada** (botão ao lado de "Nova Embalagem"): escolha a Fita adesiva, quantidade 2, custo 17,00; a prévia diz "Saldo 8 → 10 · custo R$ 15,00 → R$ 15,40 (médio)". Salve e veja a lista e o Registro de atividades ("Editar · Embalagens").
- **Abrir uma embalagem:** a parte "Estoque" (mínimo, saldo só leitura, "Acertar saldo" com motivo obrigatório) e, no insumo, o "Rende" com a dica ao vivo.
- **A baixa:** a Separação do pedido 4 não baixa nada; ao fechar a Conferência de Saída dele, o saldo cai (a fita em 1/50) e o aviso final cita o que ficou abaixo do mínimo ou negativo, sem travar.
- **Necessidades de Compra:** o card "Embalagens abaixo do mínimo" (só as ativas), com o link "Dar entrada" que abre o painel já na embalagem certa (`?entrada=<id>`).
- **Decidido (pelo principal, com a regra que ele aprovou em 30/out):** o custo da entrada é por unidade; o fornecedor é texto livre; o saldo do insumo fica na unidade de compra, com fração; entrada e acerto vão para o Registro de atividades como "Editar · Embalagens" (a chave que já existe, `embalagensEditar`; sem senha de fábrica, segue a trava de editar embalagens); Necessidades de Compra só mostra e leva à entrada, sem ordem de compra (na produção a entrada vem pela nota); não há extrato de movimentações por embalagem (o histórico é o Registro de atividades). Cancelar depois de fechar não devolve.
- **Limite, de propósito:** o saldo é um só por empresa, sem depósito, e vive no navegador como o resto do protótipo. O detalhe técnico e a prova estão no §14.107; a suíte é a seção [13] de `teste_embalagem_pedido.py`.

**Calculadora de precificação: feita em 30/out/2026, esperando a revisão dele.** Mora na aba Preços do produto, no botão "Calcular preço" (abra `http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?editar=1`). Tem o custo do produto (o da aba Custos, de compra ou médio, como Custos do E-commerce lê), a embalagem completa (a caixa do cadastro do produto mais os insumos que entram sozinhos na loja), o frete, a margem desejada, as parcelas, e o imposto e a comissão de Parâmetros de Vendas. Mostra quatro sugestões (Varejo ,90, Abaixo da faixa, Redondo e Exato), a conta aberta, a margem por forma de pagamento, a "venda nossa" sem comissão e o preço mínimo. A taxa e a tarifa vêm do gateway da loja virtual da loja do produto, a mesma fonte de Custos do E-commerce (hoje a tabela do Link), e por isso acompanha sozinha o item 10 da revisão geral. Parâmetros de Vendas ganhou a comissão padrão (5%) e as parcelas da vitrine (3).
- **Só preenche campos:** o preço continua editável à mão, e só o botão "Aplicar preço" mexe no Preço de venda, na lista Padrão e no Markup, guarda o cálculo (`deskCalculoPreco`, por produto) e escreve no Registro de atividades ("Aplicar o preço calculado").
- **Decidido:** o markup é preço ÷ custo do produto; o Exato sobe ao centavo (a margem nunca fica abaixo da pedida); a embalagem é a de um pedido de uma peça (o produto indo sozinho: junto com outro, a margem só melhora). A pesquisa por trás das quatro sugestões está em `docs/pesquisa-psicologia-de-precos.md`.
- **Limite, de propósito:** a lista de produtos, o PDV e os pedidos seguem com o preço do exemplo; o cadastro novo (`?novo=1`) calcula mas não grava o cálculo, até haver banco. A suíte é `teste_calculadora.py`; o detalhe técnico, o §14.101.

**Custos do E-commerce: concluído em 30/out/2026.** As quatro entregas e os ajustes estão no HISTORICO.md, e o detalhe no §14.95 a §14.100. Tela: `http://localhost:3000/vendas/pagina-vendas-custos-ecommerce.html`. As entregas 1 a 3 e a primeira rodada da 4 ele testou e aprovou; os testes finais do ajuste da 4 (a estimativa pelo cadastro, a Separação que não mexe no custo, o "Total de volumes", a troca) ele delegou ao principal, que os rodou no navegador em 30/out: 61 itens, nenhuma falha. A baixa da embalagem no estoque, que tinha ficado de fora, foi feita em 03/nov (acima). O que mais ficou de fora está na lista da revisão geral (os itens 6, 9, 10, 12, 16 e 17 mexem nesta área; o 9 e o 10 mudam números do lucro).

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

1. **Rodada de correção do estoque das embalagens** (pedido dele em 03/nov, depois de testar a entrega; começa pela barganha):
   - **Motivos de acerto:** o "Acertar saldo" passa a escolher o motivo de uma lista, em vez de texto solto. Ver se a lista é a de Configurações → Motivos de Perda, que já existe.
   - **Prejuízo pelo motivo:** o acerto para menos por avaria, quantidade errada etc. gera prejuízo, conforme o motivo, como a perda de produto em Tratamento de Perdas.
   - **Inventário geral:** as embalagens (caixas, envelopes, sacolas, insumos) aparecem no Inventário para serem contadas.
   - **Ordem de compra:** em Necessidades de Compra, o bloco das embalagens gera ordem de compra, e não "Dar entrada", para seguir o fluxo normal (ordem → nota → entrada). A decidir: a embalagem entra na Ordem de Compra sem SKU de produto?
   - **Movimentação:** entrada, baixa e acerto de embalagem aparecem em Estoque → Movimentação de Estoque, e não só no Registro de atividades.
2. **Desconto da venda nossa na hora da venda** (ideia dele em 30/out, opcional): a venda sem ninguém recebendo comissão e paga no Pix pode somar o desconto da comissão ao do Pix. A calculadora já mostra até onde dá; falta a opção no PDV e no Pedido de Venda, e a vitrine depende do protótipo dela.
3. **Gateways de Pagamento:** falta o protótipo da vitrine.
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
