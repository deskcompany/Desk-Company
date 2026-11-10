# Progresso do ERP Desk Company

*Atualizado em 09/nov/2026: Promoções e Encartes, entrega 1 (a lista, a página da promoção, a revisão com aprovação por senha, o histórico do preço na ficha do produto), feita e esperando o teste dele. As entregas 2 e 3 vêm depois do teste.*

Esta página diz **só onde o projeto está hoje**: onde paramos, os números, o próximo da fila, o que está decidido e o
que espera decisão. É **reescrita a cada entrega**, no mesmo commit, e fica curta: quando uma entrega é testada e
aprovada, o texto dela sai daqui e vai para o começo do [HISTORICO.md](HISTORICO.md), que guarda tudo desde o começo
(cada entrega, as rodadas de teste, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito).
As regras do projeto ficam no `CLAUDE.md`, e o detalhe técnico no §14 do design system.

## Onde paramos

**Promoções e Encartes, entrega 1: feita em 09/nov/2026, esperando o teste dele.** O detalhe está no §14.108. Para abrir:

- `http://localhost:3000/vendas/pagina-vendas-promocoes.html` (a lista; abre em "Em revisão")
- `http://localhost:3000/vendas/pagina-vendas-promocoes-detalhe.html?id=3` (a promoção em revisão com uma linha em cada motivo de "fora")
- `http://localhost:3000/vendas/pagina-vendas-promocoes-detalhe.html?id=8` (em revisão, toda ok: dá para aprovar com senha)
- `http://localhost:3000/cadastros/pagina-cadastros-produtos-detalhe.html?id=7` (aba Preços: "Em promoção até…", o histórico do preço e o encerrar antes)
- `http://localhost:3000/configuracoes/pagina-configuracoes-parametros-vendas.html` (a seção Promoções, com os dois prazos novos)

O que entrou: a lista (cards que filtram, abas por situação, busca, loja, período, a coluna "Vendido / limite", a seleção que encerra ou exclui, o painel com o resumo, quanto vendeu e as ações da situação); a página (dados, onde vale, os produtos pelo SKU, pela seleção detalhada ou pela planilha com o modelo para baixar, limite total e por cliente, "Aplicar X% nos selecionados", a revisão linha por linha e aprovar com senha); depois de aprovada, antecipar, prorrogar, encerrar, alterar antes de começar e clonar; o item no menu logo depois do PDV; as sete ações no catálogo de Confirmações por senha e no Registro de atividades; o módulo no perfil do vendedor; e, na ficha do produto, o histórico do preço de venda e do promocional, de onde sai a trava "o preço de venda subiu nos últimos 30 dias". A trava do mínimo é a conta da própria calculadora de preço, que passou a morar num bloco comum (sem mudar número nenhum).

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
| **Protótipo** | itens do menu que já têm tela HTML validada | **46 de 56 (82%)**, em 92 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 82% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

Eram 90 telas e 45 de 55 itens com tela até 03/nov/2026: Promoções e Encartes entrou no menu já com a lista e a página.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 13 de 14 | Relatórios de Estoque |
| Vendas | 6 de 9 | Notas Fiscais, Margem de Contribuição, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 4 de 5 | Relatórios Finanças |
| Integrações | 1 de 4 | Marketplaces e Hubs, Emissão de Notas Fiscais, Relatórios de Integrações |
| Configurações | hub com 20 telas | Formas de pagamento (a lista fiscal da NF-e) |

O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## Próximo da fila

Refeita em 09/nov, depois da entrega 1 de Promoções e Encartes.

1. **O teste dele na entrega 1 de Promoções e Encartes**, e os ajustes que vierem num pacote só. As perguntas da entrega estão em "Esperando decisão do usuário".
2. **Promoções e Encartes, entrega 2: o preço entra sozinho.** Enquanto a promoção está ativa, o preço promocional entra sozinho no PDV e no Pedido de Venda (onde ela vale), sem senha, respeitando o limite total e o por cliente; o desconto máximo do PDV vale sobre o promocional. E a exceção na hora: o botão "Aplicar preço promocional" no item do PDV e do Pedido de Venda, fora de promoção, com senha, só para quem tem a permissão no cadastro, com a trava do mínimo, indo para Confirmações por senha e para o Registro de atividades. Com isso o "quanto vendeu" passa a contar só o que foi vendido com o preço da promoção.
3. **Promoções e Encartes, entrega 3: "Gerar encarte"** (a peça com foto, "de… por…" e prazo, com a marca da loja, para imprimir ou mandar aos vendedores). Começa pela barganha, com prints de encartes que eles usam hoje, se houver.
4. **O protótipo da vitrine** (Gateways de Pagamento e preço promocional): o preço de venda riscado e o promocional como o preço; o painel da vitrine não cadastra nem muda preço, manda pedidos ao sistema (auditoria de produto, revisão de preço); o "Ativar preço promocional" dele cria uma promoção só da vitrine, com as mesmas travas, na mesma lista de Promoções e Encartes.
5. **Rodada de correção do estoque das embalagens** (pedido dele em 03/nov; começa pela barganha). **Segurada por ele em 04/nov:** a tela fica como está, e ele avisa quando voltar:
   - **Motivos de acerto:** o "Acertar saldo" passa a escolher o motivo de uma lista, em vez de texto solto. Ver se a lista é a de Configurações → Motivos de Perda, que já existe.
   - **Prejuízo pelo motivo:** o acerto para menos por avaria, quantidade errada etc. gera prejuízo, conforme o motivo, como a perda de produto em Tratamento de Perdas.
   - **Inventário geral:** as embalagens (caixas, envelopes, sacolas, insumos) aparecem no Inventário para serem contadas.
   - **Ordem de compra:** em Necessidades de Compra, o bloco das embalagens gera ordem de compra, e não "Dar entrada", para seguir o fluxo normal (ordem → nota → entrada). A decidir: a embalagem entra na Ordem de Compra sem SKU de produto?
   - **Movimentação:** entrada, baixa e acerto de embalagem aparecem em Estoque → Movimentação de Estoque, e não só no Registro de atividades.
6. **Desconto da venda nossa na hora da venda** (ideia dele em 30/out, opcional): a venda sem ninguém recebendo comissão e paga no Pix pode somar o desconto da comissão ao do Pix. A calculadora já mostra até onde dá; falta a opção no PDV e no Pedido de Venda, e a vitrine depende do protótipo dela.
7. **Começar a produção, F0** (a decidir; conta nova só com o pedido dele).
8. **Os outros itens pós-MVP** (Margem de Contribuição, Relatórios, Notas Fiscais, Integrações). Módulo novo começa pela
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
    ela está ativa, o preço entra sozinho, sem senha (a decisão foi tomada ao aprovar). **É a entrega 2.**
  - **A exceção na hora:** fora de promoção, o botão "Aplicar preço promocional" no item do PDV e do Pedido de Venda pede senha, e só
    quem tem a permissão no cadastro dele aplica; vai para Confirmações por senha e para o Registro de atividades, e respeita a trava do mínimo. **É a entrega 2.**
  - **Desconto por cima:** o preço promocional não conta como desconto; o desconto máximo do PDV (hoje 10%) vale sobre o promocional,
    com a mesma liberação de hoje. **É a entrega 2.**
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
  - **Quanto vendeu:** o painel mostra as unidades vendidas contra o limite e o faturamento, lidos dos Pedidos de Venda e do PDV (09/nov).
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
   caixa e dentro de um saquinho da loja. Os insumos que entram sozinhos continuam entrando. (A conta do mínimo agora é um bloco comum com
   Promoções e Encartes, §14.108: mudar a embalagem muda as duas telas juntas.)

Do teste dele na entrega 1 de Promoções e Encartes (09/nov/2026, com prints):

4. **Promoção, tabela de produtos: os números desalinhados com os campos de digitação.** "De" e "Mínimo" (texto) não
   ficam na mesma linha nem na mesma borda dos campos "Por", "Limite" e "Por cliente" (caixas). Alinhar texto e caixa
   na mesma altura e no mesmo lado; ver se o mesmo acontece nas outras tabelas editáveis (Ordem de Compra, Entrada de Notas).
5. **Painel lateral aberto: a página de trás não rola** (vale para o sistema todo). Hoje a rolagem desce a página
   principal por trás do painel. Com o painel da direita aberto, a rolagem mexe só nele; ao fechar, a página volta a rolar
   do ponto em que estava. Todas as telas com painel lateral, num bloco comum.
6. **Painel da promoção: organizar os botões** "Antecipar para hoje", "Prorrogar", "Encerrar agora", "Clonar",
   "Abrir promoção completa" e "Fechar". Hoje são seis pílulas soltas em três linhas, sem hierarquia. Propor a
   organização (a principal em destaque, as outras agrupadas) antes de mexer, seguindo os painéis das telas prontas.
7. **Ficha do produto, aba Dados Complementares: alinhamento.** "Loja Desk" e "Selecionar Loja" ficam colados na
   Categoria, os nomes não seguem a grade das outras linhas, e os valores aparecem no meio. Alinhar à grade da aba Dados Gerais.
8. **Ficha do produto, aba Preços: o botão "Encerrar antes para este produto" está fora do padrão** (saiu com cara de
   botão nativo: a classe `btn-secundario` não tem CSS nessa tela, porque entra pelo JS). Trocar pelo botão do design
   system e procurar, nas 92 telas, outra classe que só aparece em string do JS sem CSS na tela. A regra entrou na skill
   `desk-company-page-qa` (checklist manual, "Interação de verdade") em 09/nov.
9. **Promoção, revisão: "fora" vira "Corrigir"** (escolha dele em 09/nov/2026, entre as sugestões). A linha boa vira
   "Pronto" e a com problema "Corrigir", na etiqueta, no filtro e na frase embaixo da tabela ("3 prontos e 2 para
   corrigir"). Trocar também nos textos de ajuda, na suíte `teste_promocoes.py` e no §14.108.

## Esperando decisão do usuário

Da entrega 1 de Promoções e Encartes (o que está feito segue a escolha marcada; muda num ajuste se ele preferir outra):

Respondidas por ele em 09/nov/2026, e ficam como estão: "Encerrar antes" pela ficha encerra **só aquele produto**;
alterar uma agendada a devolve para "em revisão" e **pede senha** de novo; os quatro motivos a mais ("de outra loja",
"sem custo no cadastro", "não é menor que o preço de venda", "limite inválido") **ficam por ora**; e excluir só
rascunho e em revisão, sem senha de fábrica.

1. **O "quanto vendeu" desta entrega** conta tudo o que se vendeu dos produtos da promoção, na loja e nos lugares marcados, durante o prazo:
   o preço ainda não entra sozinho no PDV e no Pedido de Venda (entrega 2). Na entrega 2 ele passa a contar só a venda com o preço da promoção.

E uma de antes, que é dele:

2. **Reenviar as skills do ERP pelo claude.ai, se quiser.** As regras que o Claude segue no ERP
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
