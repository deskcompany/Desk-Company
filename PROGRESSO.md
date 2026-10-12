# Progresso do ERP Desk Company

*Atualizado em 12/out/2026, na troca de nome para Tratamento de Perdas.*

Esta página diz onde o projeto está, o que vem depois e o que está esperando decisão. Serve para
começar uma conversa nova sem reler o projeto inteiro. É **reescrita a cada entrega**, no mesmo
commit; o histórico de cada entrega fica no `git log`, e as regras do projeto no `CLAUDE.md`.

## Onde paramos

**As melhorias do estoque (E2, E8 e E10 da lista) estão feitas e esperam o teste do usuário**,
junto com as da venda (V2, V3 e V5) e as de Finanças (F1 a F4), entregues antes no mesmo dia. Ele
mandou seguir a lista grupo a grupo; sobre Finanças, voltou com um ponto só, a barra de rolagem na
tabela de Caixa e Bancos, que entrou nesta entrega.

**O usuário já testou o estoque e voltou com três pontos, e os três estão decididos.**

- **O link do Kit Home Office** abria uma lista vazia em Entrada de Notas. Era defeito, está
  consertado e ele deu ok (§14.58, no fim).
- **"Itens Bloqueados" passou a se chamar "Tratamento de Perdas"** (§14.59). Barganhado e fechado
  por ele em 12/out. Muda o nome da tela; "bloqueado" segue sendo a situação do saldo, e o arquivo
  continua `pagina-estoque-itens-bloqueados.html`.
- **A chegada da transferência vira conferência.** Aprovado por ele em 12/out, com a opção (a): ao
  fechar com falta, a conferência pergunta se o resto ainda vem (segue em trânsito) ou se faltou
  (vai para a fila de falta a auditar). **Ainda não construído:** é o próximo da fila.

Dois itens do grupo da venda não entraram, e o motivo é o mesmo: o exemplo da tela de destino não
tem o registro. V4 (do painel de Metas para os pedidos do mês) e L4 (do Rastreamento para a conta a
receber e o romaneio) esperam o alinhamento dos dados de exemplo, que virou os itens X4 e X5.

A impressão em formato de relatório segue analisada e por fazer: ele pediu para deixar para depois.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **41 de 55 (75%)**, em 80 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 75% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

Eram 81 telas: a de Performance de Vendas deixou de existir quando Metas e Performance virou uma
página só. O menu continua com 55 itens.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 12 de 13 | Relatórios de Estoque |
| Vendas | 4 de 9 | Notas Fiscais, Vendas Afiliados, Margem de Contribuição, Custos do E-commerce, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 3 de 5 | Comissões Afiliados, Relatórios Finanças |
| Integrações | 0 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Gateways de Pagamento, Relatórios de Integrações |
| Configurações | hub com 19 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## O que ficou pronto nesta conversa

**1. Necessidades de Compra e Giro de Estoque** (10/out, §14.52 do design system).

**2. A primeira leva de melhorias dos módulos prontos** (10/out, §14.53): os links entre as telas,
imprimir e baixar planilha de verdade em 20 listas, os painéis de Ordens de Compra e de Clientes, os
indicadores do Controle de Estoques, o Início com destino e o menu de Integrações enxuto.

**3. O retorno do usuário sobre essa leva** (12/out, §14.54):

- **Metas e Performance é uma página só.** A lista junta meta, realizado, atingimento, ritmo,
  vendas com ticket médio e devolução; o painel lateral traz a meta, como vendeu, a comparação e o
  botão de definir ou editar a meta. O seletor entre duas telas, que ele recusou, saiu.
- **"Incluir" abre em branco:** a ordem de compra e os cinco cadastros com página própria.
- **Ordens de Compra e Pedidos de Venda abrem do nº 1 para o maior.**
- **O filtro de período fecha quando outro filtro abre**, nas doze telas que o têm.
- **Necessidades de Compra** abre em "A comprar", o produto sai da lista quando a ordem é gerada, e
  digitar a quantidade marca o produto.
- **Separação:** concluir volta para a fila, que diz o que aconteceu; "Devolver este pedido para a
  fila" funciona, inclusive em separação já concluída; o que a ficha fez fica guardado.
- **Etapa que passou não volta:** a Conferência de Saída não leva mais à Separação. O Pedido de
  Venda mostra a etapa em que o pedido está e leva para a ficha daquele pedido, que tem o botão de
  voltar para o pedido.
- **Contas a Receber:** pedido cancelado não deve. O painel do cliente lê de lá quanto ele deve.
- **Dashboard:** os botões 5/10/15/20 mostram mais itens **sem esticar o quadro**: a lista rola
  por dentro e os três quadros da linha ficam na mesma altura. Clicar numa loja filtra o painel
  inteiro; clicar de novo volta a todas.
- **Boas-vindas:** o quadro **Pendências do Dia** (nasceu como "O que precisa de você hoje"; o
  usuário pediu um nome mais formal), de lado a lado, com a quantidade de cada fila. Os atalhos
  ganharam dois botões, e a agenda e os atalhos fecham na mesma altura.
- **A ferramenta de construção que saiu do projeto** não é mais citada em lugar nenhum: telas,
  documentos, skills e os outros projetos da pasta.

**4. Finanças, itens F1 a F4 da lista** (12/out, §14.56):

- **O painel da conta.** Em Contas a Pagar e em Contas a Receber, clicar na linha abre a conta ao
  lado, sem sair da lista: situação e prazo, valor, pago e saldo, os dados, de onde veio, os
  pagamentos já feitos, e os botões "Pagar" ou "Receber" e "Abrir a conta".
- **A origem com link.** Conta a pagar que nasceu de nota leva à nota de entrada e à ordem de
  compra, no painel e na página da conta. Três contas novas nasceram de notas que a Entrada de Notas
  tem como lançadas, com o mesmo fornecedor e o mesmo valor; e a nota leva de volta à conta. Conta a
  receber leva ao pedido e ao cadastro do cliente.
- **Indicadores** nas duas listas: vencidas, vencem hoje, próximos 7 dias e total. Clicar num deles
  deixa na lista exatamente aquelas contas; clicar de novo desfaz.
- **Caixa e Bancos:** a origem do lançamento ("CP 1", "CR 3") é link para a conta que o gerou.

**5. A venda, itens V2, V3 e V5 da lista** (12/out, §14.57):

- **A página do pedido** ganhou o quadro "Acompanhamento": Separação, Conferência de Saída,
  Expedição, Rastreamento, Contas a Receber e Devolução, cada uma com o estado e o link. Os itens
  "Acompanhar no galpão" e "na bancada" saíram do menu.
- **Indicadores em Pedidos de Venda:** a aprovar, a faturar, atrasados para entrega e vendido em 30
  dias. Clicar deixa na lista exatamente aqueles pedidos; clicar de novo desfaz.
- **A venda do PDV aparece no resto do sistema:** entra em Pedidos de Venda como "PDV-0001", já
  entregue; o dinheiro recebido na hora entra no Caixa de Finanças; e a conclusão da venda tem o
  link para o pedido. Contas a Receber e Metas ainda não leem a venda de balcão.

**6. O estoque, itens E2, E8 e E10 da lista, e o Caixa sem barra de rolagem** (12/out, §14.58):

- **Caixa e Bancos:** a tabela cabe no quadro. A data vai sem o ano (a competência ao lado já o
  mostra, e a data inteira aparece ao passar o mouse), e o histórico e a categoria quebram de linha.
  Cabe em tela de 1440, 1366 e 1280 de largura, mesmo com histórico comprido.
- **Indicadores em Ordens de Compra:** valor em aberto, a receber em 7 dias, atrasadas e sem data
  prevista. Clicar deixa na lista exatamente aquelas ordens; clicar de novo desfaz. A ordem nº 6 do
  exemplo passou a estar atrasada, para o indicador ter o que mostrar.
- **Transferência Entre Estoques:** clicar na linha abre o painel da transferência, com os itens,
  o enviado e o recebido, quem enviou, quem recebeu e o tempo em trânsito. Dali se confirma o
  recebimento, e quem confirmou fica registrado.
- **Tratamento de Perdas** (na época, Itens Bloqueados): "De onde veio" leva ao documento: a nota em Entrada de Notas e a ficha do
  pedido na Separação e na Conferência de Saída. Acerto, devolução e bloqueio manual seguem em
  texto.

**7. A verificação.** Quatro suítes novas: `teste_retorno.py`, `teste_fin_melhorias.py`,
`teste_venda_melhorias.py` e `teste_estoque_melhorias.py`. Sessenta defeitos injetados de
propósito, um por vez; os sessenta são pegos (os dois últimos são do conserto do link, com o
exemplo antigo guardado no navegador). A auditoria do projeto reprova
qualquer menção à ferramenta que saiu e enxerga chave de armazenamento guardada em constante.

**8. As skills do ERP** ganharam o que o retorno ensinou, na seção "A tela dentro do sistema" e no
"mapa de vizinhança". O texto está na cópia que o Claude carrega neste computador e em
`C:\Claude AI\Skills\Skills ERP System`.

## Próximo da fila

1. **A conferência na chegada da transferência**, aprovada em 12/out com a opção (a). A
   transferência a caminho entra na fila da Conferência de Entrada, "Confirmar recebimento" vira
   "Conferir chegada" e abre a mesma contagem cega da nota, e o painel que já vinha com a quantidade
   preenchida sai. Depois, o resto do teste dele em Finanças, na venda e no estoque.
2. **O resto da lista aprovada**, na ordem sugerida: os cadastros (C2 a C8, que pedem alinhar os
   dados de exemplo antes); K1 e R6; os alinhamentos de exemplo (X1 a X5), que destravam V4 e L4; e
   por último G3, a página de detalhe abrir o registro clicado.
3. **A impressão em formato de relatório** (item P1): analisada, falta fazer. O usuário pediu para
   deixar para depois. Entra no bloco comum e chega às 20 listas de uma vez.
4. **A segunda varredura:** o miolo de Inventário, Acerto e PDV, que a primeira não abriu.
5. **Módulo novo:** Vendas Afiliados e Comissões Afiliados; depois Margem de Contribuição e Custos
   do E-commerce; Formas de pagamento; Notas Fiscais e Integrações; e os relatórios por último.
   Começa pela barganha, com os prints.

## Decidido, e ainda não feito de propósito

- **Hospedagem: Cloudflare Pages, com o banco no Supabase** (usuário, 10/out/2026). A Vercel fica
  como destino de migração, para quando o projeto pedir mais. **Nenhuma conta foi criada e nada foi
  publicado:** ele quer mais módulos prontos antes de subir. O detalhe está na seção 2 de
  `docs/arquitetura-roadmap-desk-company.md`.
- **GitHub:** o último envio foi em 09/out/2026. Tudo de 10 e 12/out está em commit só neste
  computador. O usuário pediu para **não enviar por enquanto**; ele avisa quando for para enviar.

## Esperando decisão do usuário

Nenhuma destas trava o teste.

1. **Skill na origem:** o plugin das skills foi enviado pelo claude.ai. O texto novo vale neste
   computador; para valer também no app da Claude, o usuário reenvia a pasta
   `C:\Claude AI\Skills\Skills ERP System\desk-company-erp` por lá.
2. **Filtro de período:** o intervalo com data inicial e final existe em Tratamento de Perdas e no
   Giro de Estoque. As outras telas com esse filtro têm só as opções prontas; levar para elas é uma
   oferta em aberto.
3. **Kit na compra:** hoje o kit entra em Necessidades de Compra como um produto comum, porque a
   composição de kit ainda não existe. Quando existir, falta decidir se a compra sugere o kit ou
   os componentes.

## O que continua sendo dado de exemplo

O usuário aceitou, em 10/out/2026, que isto fique assim nesta fase:

- **Cada tela tem os seus registros de exemplo.** Um link entre telas cai na lista vizinha já
  filtrada; quando o exemplo de lá não tem o registro, a faixa da lista explica isso.
- **O pedido não anda sozinho de uma fila para a outra.** Concluir a separação guarda o que foi
  feito, mas o pedido não aparece na fila da Conferência de Saída por causa disso.
- **Quatro títulos de Contas a Receber** têm cliente ou valor diferente do pedido que citam, e os
  romaneios da Expedição levam pedidos que o Pedido de Venda dá como em separação.
- **11 páginas de detalhe abrem sempre o mesmo exemplo**, qualquer que seja a linha clicada (item
  G3 da lista).
- **A venda do PDV e a ordem criada em Necessidades de Compra** não aparecem em todas as telas
  vizinhas (a ordem aparece em Ordens de Compra; a página dela abre o exemplo fixo).
- **Os valores financeiros do Dashboard** são próprios, e os de cada loja são uma fatia do total.

Quando o sistema rodar de verdade, o usuário limpa tudo e configura do zero.

## Ficou de fora de Necessidades de Compra e Giro, de propósito

- **Tags** (filtrar por tags e "aplicar tags"): marcador não existe neste sistema (§12.1).
- **Natureza de operação:** é fiscal, e a NF-e não está habilitada.
- **Prazo de entrega do fornecedor:** não existe no cadastro; a data prevista da ordem é digitada.
- **Os pedidos que ainda vão sair** são dado de exemplo da própria tela: Pedidos de Venda tem outro
  cadastro de produtos.

## Para retomar numa conversa nova

1. Abra o editor na pasta `C:\Claude AI\Desk Company`.
2. Primeira mensagem: "vamos para onde paramos", com os prints do próximo módulo, se for o caso. É
   para ler este arquivo e seguir do próximo da fila.
3. Para ver as telas: `node _ferramentas/servidor.js` na pasta `ERP System`, e depois
   `http://localhost:3000/<pasta>/<arquivo>`. O servidor cai quando a sessão fecha.
4. Antes de dar algo por pronto: `python selo.py --rodar` na pasta `_ferramentas`.
5. Commit local a cada entrega. Envio ao GitHub só quando o usuário disser.
