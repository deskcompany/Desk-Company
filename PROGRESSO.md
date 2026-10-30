# Progresso do ERP Desk Company

*Atualizado em 30/out/2026: Custos do E-commerce, entrega 4 (a embalagem automática: custo e insumo no cadastro, a escolha na Separação, a confirmação na Conferência de Saída e o custo do dia) feita, com o ajuste de 30/out (a estimativa vem do cadastro, o campo de Configurar saiu, a Conferência acerta o total de volumes), esperando o teste dele; a entrega 3 foi testada e aprovada por ele em 30/out e foi para o HISTORICO.md. A calculadora de precificação vem depois que ele aprovar a 4.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Custos do E-commerce: entrega 4 feita em 30/out/2026 (§14.99). Ele testou em 30/out: 1, 2, 3, 4 e 6 ok; o 5 (a troca na Conferência) ele não rodou, e foi conferido na revisão do principal. Ele respondeu a pergunta que estava em aberto: o campo "Embalagem estimada por loja" saiu de Configurar, e o pedido ainda não confirmado mostra uma estimativa pelo próprio cadastro (a caixa que cabe e os insumos automáticos), marcada "estimada" (§14.100). A entrega segue esperando o teste desse ajuste.** Telas: `http://localhost:3000/cadastros/pagina-cadastros-embalagens.html`, `http://localhost:3000/logistica/pagina-logistica-separacao-detalhe.html?id=4`, `http://localhost:3000/logistica/pagina-logistica-conferencia-saida-detalhe.html?id=4` (o 4 só aparece lá depois de separado) e `http://localhost:3000/vendas/pagina-vendas-custos-ecommerce.html`.
A entrega 3 (anúncios, oito cards, mês a mês, Parâmetros de Vendas, o módulo no perfil) ele testou e aprovou em 30/out: o texto dela está no começo do HISTORICO.md. O que a entrega 4 trouxe:

- **Cadastro de Embalagens:** campo **Custo** em toda embalagem, **"Cabe até (peças)"** em caixa e envelope (opcional) e o tipo **Insumo** (tag, fita, saco): sem medidas, sem peso, sem virar volume, e com a escolha de **entrar sozinho** no pedido de todas as lojas ou de uma só. De fábrica: as 10 de antes, com custo, mais a Tag Desk Shope, a Tag Desk Brands, a Fita adesiva (todas as lojas) e o Saco plástico (o separador adiciona). A lista agora fica gravada no navegador.
- **Separação:** o pedido online real **4** (Juliana Prado, Desk Brands, 10 peças) entrou na fila. Antes de concluir o separador escolhe as embalagens: a **menor caixa que cabe vem sugerida** (CE-02 para as 10 peças) e os **insumos automáticos já vêm preenchidos** (tag da Desk Brands e fita). Ele vê só os nomes, **nunca o custo**. Falta declarada muda a sugestão enquanto ele não mexe na caixa; "Salvar e continuar depois" guarda, "Devolver para a fila" apaga. A sugestão de pedido grande agora usa várias caixas grandes (46 peças: 2 × Caixa para Eletrônicos), e nunca um envelope.
- **Conferência de Saída:** o 4 só chega depois de separado, já **preenchido** ("Veio da Separação: ..."), com a marca "escolhida na separação" e um bloco novo de **Insumos** (que não viram volume, nem etiqueta, nem romaneio). Pode trocar, e a troca fica no pedido e no Registro de atividades; **vale o que ela confirmou**. Aberto de novo, o pedido aparece conferido e só leitura.
- **O pedido guarda o custo do dia:** mudar o preço no cadastro depois não mexe no pedido antigo (o pedido 16 foi confirmado a 11,90, com o cadastro em 12,50, de propósito).
- **Custos e página do pedido:** a embalagem confirmada aparece com os nomes ("1 Caixa de Encomenda Flex M + 1 Tag Desk Shope + 1 Fita adesiva = R$ 5,40") e a troca, se houve; o pedido ainda não confirmado mostra a **estimativa pelo cadastro** (a menor caixa em que cabem as peças mais os insumos automáticos da loja, a preço de hoje) e diz **"estimada"**; o que a Separação escolheu não mexe no custo, só a Conferência. Mês atual: embalagem 54,60 no total, lucro **R$ 1.050,68** (13,9%), depois dos anúncios **R$ 600,68**. Fazendo o fluxo no 4 sem trocar nada: embalagem 7,20, lucro do 4 em 161,40 e o total não muda.
- **Conferência de Saída:** campo novo **"Total de volumes"** ao lado de "Adicionar volume" (acerta o número de linhas, de 1 a 999; mais repete a caixa da última, menos corta as últimas); as caixas que sobram na troca saem numa entrada só ("− 299 Caixa de Encomenda CE-02"). "Cabe até" é só sugestão: nada trava por capacidade. Quantidade de embalagem e de insumo tem teto de 999.
- **Fora por enquanto:** baixar a embalagem do estoque. **A calculadora de precificação não foi mexida:** ela vem depois que ele aprovar a entrega 4.
- **O que conferir:** criar um insumo no cadastro; separar o pedido 4 (sem R$ na tela), conferir, trocar uma caixa e fechar, e acertar o "Total de volumes"; ver o painel do 4 e do 11 em Custos, e Configurar sem o campo de embalagem; tudo nos temas claro e escuro.

Confirmado por ele em 22/out: "do mês" vai do dia 1 até hoje; os cards somam a lista toda. **Recebimento da InfinitePay:** a venda no cartão, mesmo parcelada, cai
inteira no dia útil seguinte, já sem a taxa (o gateway da loja virtual é "Antecipado"). **A antecipação saiu do módulo:** o cadastro de gateway não tem taxa de
antecipação à parte, e na InfinitePay ela já está na taxa.

**Vale-compra: concluído.** As três entregas foram testadas e aprovadas pelo usuário (a 3 em 20/out, junto com o conserto
que faz a Devolução ficar gravada); o que foi feito está no HISTORICO.md e o detalhe no §14.89 a §14.91.

**Gateways de Pagamento: as entregas 1 e 2 e os ajustes do teste, testados e aprovados pelo usuário em 21/out** (§14.92 a
§14.94; o que foi feito está no HISTORICO.md). Ficaram três consertos pedidos no teste (comissão sem o vale-compra, a loja
virtual com as taxas da Bronze, os feriados móveis), que foram para a revisão geral (decisão dele em 21/out: a cota semanal
está no fim e ele prefere construir agora). Falta o protótipo da vitrine, no "Próximo da fila".

**Calculadora de precificação: parada, de propósito, até ele aprovar a entrega 4 de Custos do E-commerce** (decisão dele em 21/out; a entrega 4 trouxe o custo da embalagem no cadastro). A
embalagem completa vai vir de lá, e o módulo de custos também vai mexer em outros pontos (Margem de Contribuição, o
imposto padrão); a calculadora é construída depois, já lendo esses custos. **Nada dela foi construído.** O que está pronto
para quando ela voltar:

*A barganha, aprovada em 21/out (as quatro recomendações):*
- **Mora na aba Preços do produto:** o botão "Calcular preço" abre a calculadora com o custo do produto; aplicar preenche o
  Preço de venda e o markup, e o produto guarda os dados do cálculo (embalagem, frete, margem, parcelas, imposto) para refazer.
- **Margem sobre o preço final**, com taxa e imposto por dentro: preço = custo total ÷ (1 − margem − taxa − imposto). Exemplo
  dele: R$ 50 + R$ 5 de embalagem, margem 30%, taxa 3,15% → R$ 82,27, lucro de R$ 24,68 (30%).
- **A taxa é a do parcelamento sem juros** escolhido (padrão 1x), lida do gateway habilitado (Bronze: 1x 3,15%, 3x 6,12%).
- **Imposto sobre a venda (%)**, com o valor de fábrica em Configurações (ex.: 6% do Simples).
- Embalagem completa (um item só, ex.: caixa + tag + saco = R$ 5) e o frete da compra por unidade entram no custo total.
  **A embalagem vem preenchida de Custos do E-commerce** (decisão dele em 21/out), editável, como o custo do produto vem da
  aba Custos. **A fonte agora é o cadastro de Embalagens** (caixa + tag + fita, com custo): o campo "Embalagem estimada por loja" de Configurar não existe mais (30/out). **O custo da embalagem é por pedido, não por unidade: a calculadora ainda precisa decidir como ratear a embalagem de um pedido entre os produtos** (pergunta em aberto, para quando ela voltar).

*As sugestões de preço (pedido dele em 21/out, "está melhor"):* no lugar de um preço, quatro cartões, cada um com a margem
e o lucro reais daquele número: **Varejo ,90** (marcada), **Abaixo da faixa**, **Redondo** e **Exato**. A pesquisa, as regras
de cada um e o que ficou de fora estão em `docs/pesquisa-psicologia-de-precos.md`. O preço continua editável à mão depois.

*O rascunho clicável* é o molde da construção: `docs/rascunhos/calculadora-trecho.html` (o painel, o estilo e a conta).
Para ver, monte a cópia da página do produto, que fica fora do git:
`python docs/rascunhos/montar_rascunho.py telas/cadastros/pagina-cadastros-produtos-detalhe.html docs/rascunhos/calculadora-trecho.html telas/cadastros/_rascunho-calculadora.html`
e abra `http://localhost:3000/cadastros/_rascunho-calculadora.html`. Apague a cópia depois.

*Esperando decisão dele, quando a calculadora voltar:* o markup (preço ÷ custo do produto, ou ÷ custo total); o
arredondamento do Exato (centavo comum, como no exemplo dele, ou para cima); e onde fica o imposto padrão (decidido na barganha de
Custos do E-commerce, em 21/out: **Parâmetros de Vendas**, tela feita na entrega 3 do módulo, em `deskParametros.impostoPadraoPct`; a calculadora lê dele).

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

Refeita em 21/out, com a decisão de fazer os custos antes da calculadora (a lista de 19/out e os porquês estão em
"Prioridades dos próximos passos", no HISTORICO.md).

1. **Custos do E-commerce, entrega 4: embalagem automática** (feita em 30/out, espera o teste dele; ver "Onde paramos"). A entrega 3 ele aprovou em 30/out.
2. **Calculadora de precificação**, **depois que ele aprovar a 4** (o imposto padrão sai de Parâmetros de Vendas, entrega 3; a embalagem, do cadastro com custo, entrega 4): barganha, pesquisa e rascunho prontos (ver "Onde paramos").
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

- **A barra que ficou** (usuário, 19/out/2026, depois de ouvir o custo): Necessidades de Compra, CRM e Metas seguem com
  barra em 1280 (de 95 a 160px), e os itens da Ordem de Compra e do Pedido de Venda seguem sem barra, com o código comprido
  (SKU, GTIN) cortando alguns caracteres em 1280. De 1440 para cima nada disso acontece. Volta quando as telas forem
  refeitas na produção, ou antes se alguém trabalhar em 1280 todo dia. A suíte `teste_barra_tabelas.py` segura as três
  como estão.

## Para a próxima revisão geral

Pedidos do usuário de 19 a 26/out/2026, **para não mexer agora**: entram juntos quando ele decidir fazer a próxima auditoria e
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
   PDV), que precisa de regra própria. **Reforçado em 30/out** no cadastro de Embalagens (campo Custo): vale em todas as telas.
7. **O seletor Pessoa Física / Pessoa Jurídica justo.** O fundo cinza é bem mais largo que as duas opções, em Clientes,
   Fornecedores e Vendedores (cadastro novo e página). Deve ter a largura só das duas opções.
8. **O campo de número com sufixo ("dias") desnivelado nos cards de Configurações** (21/out, com print de Parâmetros de
   Estoque: Conferência de compra e Endereçamento). A caixa do número fica cerca de 1 px mais alta em cima e embaixo
   que a do "dias", e o card fica com um degrau. Ele viu em Estoque, em todos os cards; mapear na revisão todos os
   campos número + sufixo das telas de Configurações (e onde mais houver) e deixar número e sufixo com a mesma altura.
9. **a comissão não conta o vale-compra**: hoje a base é o total menos o frete; passa a ser o total menos o frete e menos o que o pedido pagou com vale, para vendedor e afiliado (a comissão é sobre o que foi vendido de fato, já com todos os descontos, o Pix/dinheiro incluído) Ele perguntou se fazia sentido e concordamos: o vale não traz dinheiro novo (devolução: a venda original já comissionou; cortesia: presente da loja; comissão em vale: evitaria comissão sobre comissão).
10. **a loja virtual usa as taxas da Bronze da maquininha** no protótipo, decisão dele, e a vitrine dá o mesmo desconto Pix. **Pesquisa obrigatória na integração da API da InfinitePay:** o Checkout Integrado cobra a tabela do Link de Pagamento (mais cara: 4,20% à vista na tabela geral) ou a da maquininha/InfiniteTap? A resposta decide as taxas reais
11. **os feriados nacionais móveis entram no dia útil**, calculados sozinhos para qualquer ano (fixos pela data, móveis pela Páscoa): Carnaval (segunda e terça, banco fechado), Sexta-feira Santa e Corpus Christi. Feriado estadual e municipal (cadastro à mão) fica para depois.
12. **O "Por página" da paginação abre sempre para cima** (26/out, com print de Pedidos de Venda). Hoje a lista de 10 / 25 / 50 / 100 abre para baixo, sai do rodapé do card e fica desproporcional. Deve abrir para cima sempre, em qualquer posição da página. É o rodapé de paginação comum: mapear todas as telas que o têm e corrigir de uma vez. **Reforçado em 30/out**, com print do cadastro de Embalagens: em todas as páginas.
13. **O campo SKU do item desalinhado** (27/out, com print de Pedido de Venda). O aviso de saldo embaixo do campo ("só 0 disponível") empurra a caixa do SKU para cima, e ela fica fora da linha das outras caixas (descrição, quantidade, preço). O aviso não pode mexer na altura da caixa. Ver onde mais a tabela de itens tem o mesmo aviso (PDV, Orçamento). Junto: a linha nova e vazia ("Adicionar outro item") já nasce vermelha, com "só 0 disponível" e o aviso de item sem saldo. Linha sem produto escolhido não deve acusar falta de saldo.
14. **No Início, o "em aberto, ainda no prazo" das contas a pagar é um número fixo de exemplo que está um abaixo de Contas a Pagar** (30/out): mostra 8 em navegador limpo, e Contas a Pagar tem 9 (total em aberto 17 menos 8 vencidas). Já vinha de antes da entrega 3; não foi consertado, de propósito.
15. **A lista de volumes da Conferência de Saída rola na lateral em janela estreita** (30/out): a 860 px passa 118 px da largura, porque a grade tem colunas fixas. Já era assim antes da entrega 4 (medido na versão anterior); não foi consertado, de propósito.
16. **Os campos de tamanho do cadastro de Embalagens desalinhados** (30/out, com print): "Comprimento (cm)" quebra em duas linhas e joga o campo para baixo dos de Largura e Altura. Pode aumentar a largura do painel lateral para caberem na mesma altura.
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
