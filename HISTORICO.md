# Histórico do ERP Desk Company

*Criado em 19/out/2026, quando o PROGRESSO.md foi dividido em dois (pedido do usuário, para cada sessão ler menos na largada).*

Este arquivo guarda **tudo o que o PROGRESSO.md dizia até 19/out/2026**, sem cortar nada: cada entrega e as rodadas de
teste dela, o balanço de 15/out, o que é dado de exemplo e o que ficou de fora de propósito. O estado de hoje (onde
paramos, a fila e o que espera decisão) fica no `PROGRESSO.md`. **Daqui em diante, quando uma entrega sai do topo do
PROGRESSO, o texto dela vem para cá**, no começo de "Entregas, da mais nova para a mais velha". O detalhe técnico de cada
entrega continua no §14 do design system, e o código no `git log`.

## Entregas, da mais nova para a mais velha

### Vale-compra, entrega 3: o vale nasce da Devolução e da Comissão (20/out/2026) — testada e aprovada pelo usuário no mesmo dia. Com ela o Vale-compra fica concluído

**O vale nasce da Devolução e do pagamento de Comissão de afiliado** (§14.91). Na Devolução, "Vale-compra" deixou de
ser reservado: escolher a forma só anota, e o vale nasce ao finalizar, com o total da devolução, na loja do pedido.
Cancelar a devolução cancela o vale ainda intacto; vale já usado impede o cancelamento. Na Comissão, só o afiliado pode
receber em vale, sem bônus, e o pagamento nasce pago e aparece em Contas a Pagar já pago, só leitura, sem saída do Caixa.
O vendedor não vê a opção. O exemplo DV-0009 passou a ser do Bruno Carvalho, cliente do cadastro, para o fluxo poder
ser testado.

**O conserto do teste dele:** salvar a forma na DV-0009 se perdia ao sair, porque a devolução vivia só na memória da
página, e "Finalizar" ficava escondido em "Mais ações". A devolução passou a ser gravada no navegador (a lista lê o mesmo
gravado), e com Vale-compra salvo a tela diz que o vale nasce em Mais ações → Finalizar. Na revisão, finalizar com
alteração não salva passou a pedir que se salve antes.

Para ver:
- `http://localhost:3000/logistica/pagina-logistica-devolucao-detalhe.html?id=4` (Vale-compra, Salvar alterações, Mais ações → Finalizar)
- `http://localhost:3000/financas/pagina-financas-vale-compra.html`
- `http://localhost:3000/financas/pagina-financas-comissoes-detalhe.html?id=a1` (Realizar pagamento em Vale-compra)
- `http://localhost:3000/financas/pagina-financas-comissoes-detalhe.html?id=v1` (vendedor, sem a opção)

Ele testou os cinco pontos e deu ok, depois do conserto da gravação. As escolhas de quem construiu, mostradas a ele
na entrega e sem objeção: cancelar a comissão paga em vale segue a regra da devolução (vale intacto cancela junto, vale
usado impede); cancelar um vale direto no Vale-compra não desfaz a devolução nem o pagamento; e a troca de cliente
da DV-0009.

**Ficou de fora:** ao salvar uma devolução nova, o endereço continua `?venda=`, e recarregar abre um formulário em
branco (já era assim; ela abre pela lista).

### Vale-compra, entrega 2: o vale se usa (19 e 20/out/2026) — testada e aprovada pelo usuário em 20/out

**O vale se usa** (§14.90). No PDV, tudo ou uma parte, só o saldo da loja do PDV; no Pedido de Venda, desconta ao salvar,
e cancelar, excluir ou mudar a situação para Cancelado devolve, também em massa na lista de Pedidos. A forma de
recebimento passou a se chamar **Vale-compra** (a chave interna segue `valetroca`). A parte paga com vale vira **título
já recebido** em Contas a Receber, **sem entrar no Caixa**. Na revisão, excluir o pedido e cancelar à mão, que não
devolviam o vale, passaram a devolver.

Para ver:
- `http://localhost:3000/vendas/pagina-vendas-pdv.html` (caixa na Desk Shope, venda para a Marina Duarte, R$ 50,00 do vale)
- `http://localhost:3000/vendas/pagina-vendas-pedidos-detalhe.html?id=1&editar=1` (100 em "Usar do vale", salvar, cancelar ou excluir)
- `http://localhost:3000/financas/pagina-financas-contas-receber.html?busca=vale-compra`
- `http://localhost:3000/configuracoes/pagina-configuracoes-formas-recebimento.html`

Ele testou e deu ok, e confirmou as cinco escolhas de quem construiu: um título por uso do vale; "Estornado" e
"Perdido" no histórico do vale; o limite de crédito do pedido olhando só o que falta depois do vale; o vale como nota
no fechamento do caixa, sem contagem; e o cliente do Pedido achado pelo nome (na produção, pelo número do cadastro).

### Vale-compra, entrega 1 e os ajustes do teste (19/out/2026) — testada e aprovada pelo usuário no mesmo dia

**Vale-compra, entrega 1 e os ajustes do teste dela** (§14.89). O vale é saldo do
cliente, só vale na loja que o emitiu, tem validade ajustável (180 dias de fábrica) e fica em Finanças, depois de
Comissões Afiliados. A lista tem indicadores que filtram ao clicar, busca, loja, origem e abas por situação; clicar na
linha abre o painel lateral com o resumo e "Ver vale completo". A página do vale tem usos, histórico, Cancelar e Reativar
(com senha). O cadastro do cliente ganhou a aba Vale-compra, e Configurações → Cadastro de clientes, a validade.

**A barra de paginação padrão** entrou também em Comissões Afiliados, Reposição, Transferência Entre Estoques e Metas e
Performance, a pedido dele. Em Comissões, a planilha e a impressão levavam a tabela das inscrições quando havia inscrição
pendente; agora levam a lista.

Para ver:
- `http://localhost:3000/financas/pagina-financas-vale-compra.html`
- `http://localhost:3000/financas/pagina-financas-comissoes.html`
- `http://localhost:3000/estoque/pagina-estoque-reposicao.html` (já abre com duas páginas)
- `http://localhost:3000/estoque/pagina-estoque-transferencia.html`
- `http://localhost:3000/vendas/pagina-vendas-metas.html`

Ele testou tudo (Vale-compra, Comissões, Reposição, Transferência e Metas) e deu ok, e confirmou as três escolhas de quem
construiu: a busca de cliente por nome, CPF/CNPJ ou e-mail; o "Voltar" da página do vale com os filtros da lista; e o uso
de exemplo do VC-3 no dia do Pedido nº 10.

As seções abaixo são o PROGRESSO.md de 19/out/2026, inteiro.

### Onde paramos

**O usuário testou a entrega 1 do Vale-compra e pediu ajustes: feitos e esperando o teste dele** (§14.89, "Ajustes do teste"). Na lista de Vale-compra
(`http://localhost:3000/financas/pagina-financas-vale-compra.html`): (1) **clicar na linha abre um painel lateral** com o resumo do vale (cliente, loja,
origem, valor, usado, saldo, emitido, vence e os três últimos usos) e o botão "Ver vale completo", que leva os filtros e o "Voltar" devolve; Cancelar e
Reativar continuam só na página do vale; (2) **os três indicadores filtram a lista** (clicar de novo desfaz; combinam com busca, loja e origem; o recorte
vai e volta no endereço); (3) **a barra de paginação padrão** no rodapé. A mesma barra entrou, a pedido dele, em **Comissões Afiliados** (só a lista
principal), **Reposição**, **Transferência Entre Estoques** e **Metas e Performance**, sempre com a contagem e o total do filtro inteiro. Em Comissões a
planilha e a impressão levavam a tabela errada (a das inscrições, quando havia inscrição pendente); agora levam a lista. Para ver, além da lista de
vales: `http://localhost:3000/financas/pagina-financas-comissoes.html`, `http://localhost:3000/estoque/pagina-estoque-reposicao.html`,
`http://localhost:3000/estoque/pagina-estoque-transferencia.html` e `http://localhost:3000/vendas/pagina-vendas-metas.html` (a barra fica embaixo da tabela;
Reposição já mostra duas páginas, 18 bases com 10 por página). Verificação: `teste_vale_compra.py` (317 asserções, com o painel, os indicadores e a paginação), `teste_comissoes.py` (256), `teste_transf_conferencia.py` (87), `teste_metas.py`, a suíte nova `teste_reposicao.py` (17), `teste_planilha.py`, `teste_esc_painel.py` e `teste_barra_tabelas.py` (89) verdes; 22 defeitos injetados numa cópia e os 22 pegos; selo verde, com 55 suítes e 5.956 asserções.

**Vale-compra, entrega 1 de 3: feita e esperando o teste do usuário** (§14.89). O vale nasce à mão e se vê. É o desenho que ele aprovou em 19/out
(mantido depois de saber que o Olist usa código): o vale é **saldo do cliente**, sem código, e **só vale na loja que o emitiu**; a **validade é
ajustável**, 180 dias de fábrica, e o vencido reativa com senha; o menu é **Finanças**, logo depois de Comissões Afiliados. O que foi construído:

- **A lista** (Finanças → Vale-compra): saldo em vales, os que vencem em 30 dias e os vencidos com saldo; busca por cliente, documento ou número,
  loja, origem e abas por situação com contagem; o vencido em vermelho ("vencido há N dias"); a linha abre a página do vale. **Incluir vale**
  (cortesia): cliente pela busca padrão, loja, valor e motivo, com o vencimento (hoje mais o prazo) à vista antes de confirmar, e senha.
- **A página do vale**: dados, usos e histórico; **Cancelar** (só com saldo, com motivo e senha) e **Reativar** (só o vencido, vencimento novo de
  hoje mais o prazo, com senha). O "Voltar" leva a lista de volta com os mesmos filtros.
- **A aba Vale-compra no cadastro do cliente**: saldo por loja, os vales dele e o link "Ver em Vale-compra"; funciona em modo leitura.
- **Configurações → Cadastro de clientes → Vale-compra**: a validade do vale, de 1 a 3650 dias; mudar o prazo não muda os vales que já existem.
- **Cinco vales de exemplo** nascem uma vez por navegador (R$ 170,00 em vales disponíveis, 1 vencido de R$ 50,00, 1 usado, 1 cancelado); as três
  ações novas (`valeCompraIncluir`, `valeCompraCancelar`, `valeCompraReativar`) entraram no catálogo de 17 telas, com senha por padrão.

Para ver: `http://localhost:3000/financas/pagina-financas-vale-compra.html`. Conferir: o VC-1 (Camila Rêgo) vencido, em vermelho; abri-lo e reativar
(a senha do protótipo é qualquer texto); incluir um vale e ver o vencimento no painel antes de confirmar; cancelar um disponível; mudar a validade em
Configurações e ver que os vales que existem não mudam; abrir o cadastro da Marina Duarte e ver a aba Vale-compra. Verificação: `teste_vale_compra.py`
(223 asserções), 23 defeitos injetados numa cópia e os 23 pegos; selo com 54 suítes e 5.787 asserções.

**Entregas que faltam:** (2) o vale se usa, no PDV e no Pedido de Venda, em parte se o cliente quiser, com a sobra valendo, e Formas de Recebimento;
(3) o vale nasce da Devolução e do pagamento de Comissão. Nada de PDV, Pedidos, Devolução, Formas de Recebimento, Contas a Receber nem do
"Vale-troca" reservado foi mexido agora. As escolhas que couberam a quem construiu estão em "Esperando decisão".

**Duas entregas de 19/out, testadas e aprovadas pelo usuário no mesmo dia**, junto com os dois ajustes da 2f. Ele decidiu deixar como estão as 3 telas que a varredura não resolveu e o código cortado em 1280 nos itens da Ordem de Compra e do Pedido (ver "Decidido, e ainda não feito de propósito").

**A. O exemplo de Comissões nasce também em navegador que já tinha pagamento** (§14.87). O usuário não viu os três
pagamentos da Marina Costa porque o navegador dele já guardava pagamentos dos testes da 2b e da 2c, e o bloco do exemplo
saía assim que a chave existia. Agora o exemplo tem marca própria (`deskComissoesExemplo`) e **acrescenta sem apagar**:
navegador com pagamento gravado ganha os três ao fim; navegador que já tinha os três antigos não duplica; excluído ou
cancelado, não volta; limpar o navegador traz de volta. O bloco é o mesmo nas seis telas.

**B. A varredura da barra de rolagem** (§14.88). Das **25 telas** com tabela rolando a 1280px, **22 foram consertadas**, todas
pelo mesmo CSS de Comissões (o `min-width` fixo sai, a coluna de texto e o cabeçalho quebram linha, o número fica numa linha),
sem precisar de mais nada. **3 não cabem só com o bloco e ficaram como estavam, esperando decisão dele:** Necessidades de
Compra, CRM e Metas (o que as segura é texto que não quebra: SKU, selos e linhas de apoio). **Segunda rodada, no mesmo dia:**
a tabela dos itens (`.itens-table`) dos detalhes da Ordem de Compra, do Pedido de Venda e do Rastreamento ganhou o mesmo
bloco, o detalhe do Controle de Estoques com registro aberto também cabe, e a data com hora de Conferência de Saída e de
Separação não quebra mais entre a data e a hora. A suíte nova, `teste_barra_tabelas.py`, mede as 83 telas e esses quatro
detalhes com registro aberto, a 1280 e a 1440, e exige que as 3 pendentes continuem como relatadas. Para ver uma
tela consertada: `http://localhost:3000/estoque/pagina-estoque-ordens-compra.html` (a tabela cabe no cartão, sem barra
embaixo; o mesmo vale para Contas a Pagar, Devolução e Pedidos de Venda).

**Antes disso, Comissões 2f, os pagamentos vencidos: testada e aprovada pelo usuário em 19/out** (§14.87), com a decisão B dele
de 15/out. A conta de comissão vencida **nunca se cancela sozinha**. A lista de Comissões Afiliados ganhou o quadro
**"Pagamentos vencidos"** (o mais atrasado primeiro, com os dias de atraso em vermelho) e três saídas: **dar baixa**
(abre a conta em Contas a Pagar com o painel da baixa aberto, e o pago volta para Comissões), **reprogramar** (o
vencimento novo, de hoje em diante; a conta muda de data em Contas a Pagar, e o histórico guarda de quando para
quando) e **cancelar** (o valor volta ao saldo, com senha). A conta do afiliado mostra "vencido há N dias" e, para o
cliente afiliado, o que a vitrine vai mostrar: **Disponível, Em pagamento e Pago** ("em atraso" quando vencido).
**Cancelar sozinho** é opção em Configurações → Cadastro de clientes → Programa de afiliados, **desligada**, com o
prazo em dias; ligada, só cancela o que não teve nenhuma baixa. Reprogramar entrou no catálogo de ações (Registro de
atividades), sem senha por padrão. Os dois ajustes que ele pediu no teste (o calendário no reprogramar e o espaço dos filtros do histórico) estão feitos e esperam a olhada dele.

Para dar o que ver, **três pagamentos de exemplo da vendedora Marina Costa** nascem sozinhos no navegador, contados
a partir de hoje: R$ 50,00 vencido há 12 dias, R$ 30,00 vencido há 4 e R$ 40,00 que vence em 5. Eles aparecem em
Contas a Pagar como COM-1 a COM-3, descem R$ 120,00 do saldo da Marina, e o Início soma as contas de comissão ao
número de contas a pagar atrasadas. **Achado no caminho:** o link do painel do fornecedor para Contas a Pagar
escondia a conta que vence no mês seguinte (a lista abria em "vencem neste mês"); está consertado. Para ver:
`http://localhost:3000/financas/pagina-financas-comissoes.html`, o quadro fica logo abaixo de "Pagamentos solicitados".

O balanço do projeto continua na seção "Balanço de 15/out/2026", logo abaixo de "Onde estamos".

**Histórico de Comissões sem barra de rolagem, e com filtro por tipo (2e): feito e esperando o teste do
usuário** (§14.86). A tabela do histórico rolava (até em 1440px); agora nenhuma tabela das telas de
Comissões rola de 1180px para cima, e o cabeçalho "Efeito no saldo" virou "Efeito". O histórico ganhou o
filtro por **tipo** (inscrição, venda, comissão, saque, pagamento, lançamento), junto de mês e ano, na conta
e no cadastro do cliente. **A regra "tabela sem barra a partir de 1280px" já existia na skill de QA e foi
reforçada** (design system, skills e a suíte). O levantamento das outras telas achou **25 de 83** com tabela
que rola em 1280px (em 1440, nenhuma); estão em "Esperando decisão".

**Comissões, ajustes do histórico (2d): feitos e esperando o teste do usuário** (§14.85). Ele testou a 2c e
pediu três coisas, as três feitas:

- **Data inicial e final no topo da conta do afiliado**, no lugar de mês e ano: o resumo, os pedidos, os
  lançamentos e os pagamentos passam a ser os do período. Abre no mês inteiro, aceita o que a lista manda
  (`?mes=` e `?ano=`), usa o calendário de Movimentação de Estoque e escreve o período sob o título, para sair
  no papel. "Mês atual" volta ao mês inteiro.
- **O histórico, melhorado, com filtro só de mês e ano** (fica embaixo, no próprio bloco): cada acontecimento
  tem o tipo, o valor, o **efeito no saldo** (+ entra, − sai) e o **saldo depois dele**, que fecha com o saldo
  de hoje linha a linha; pedido e conta a pagar viram link; entraram a comissão a liberar, a vencida, o saque
  aprovado e o pagamento excluído com o valor voltando.
- **O histórico no cadastro do cliente**: o que ele viu faltar. O cadastro só tinha o resumo (o combinado na
  barganha); agora a aba Afiliado mostra também o histórico, o mesmo da conta em Comissões, lido de lá, com o
  mesmo filtro de mês e ano e funcionando com o cadastro em modo leitura.

**Comissões, entrega 2c: feita e esperando o teste do usuário** (§14.84), com a barganha que ele aprovou em
15/out. A conta do afiliado ganhou o **Histórico** de todos os meses (inscrição, aprovação, vendas, comissões
liberadas, saques, pagamentos, baixas, cancelamentos e lançamentos). O cliente afiliado **pede o saque na
vitrine**, a partir do mínimo de Configurações (R$ 50): o pedido chega no quadro "Pagamentos solicitados" da
lista, e aprovar faz nascer a conta a pagar (recusar pede motivo). A **baixa em Contas a Pagar volta para
Comissões**: o pagamento aparece como pago, a conta continua paga ao recarregar, e o estorno desfaz. O cadastro
do cliente ganhou a **aba Afiliado** (loja, situação, comissão, saldo, pagamentos e o link para a conta), e o do
vendedor, o link para a conta dele. **E a limpeza**: o desvio para o Inventário saiu de 18 telas.

**Segunda rodada do teste de Comissões (15/out), consertada** (§14.82). O usuário quer o dropdown sempre para
baixo, mesmo com a tela baixa: agora ele abre para baixo e a página rola até o menu aparecer inteiro, também em
lista curta (para cima só dentro de painel lateral ou modal). E cancelar ou excluir a conta de comissão em Contas
a Pagar não gravava: a conta voltava, refeita a partir do pagamento. Agora cancelar cancela o pagamento em
Comissões (o valor volta ao saldo e a conta fica cancelada no histórico), reativar desfaz, e excluir tira os dois.
Ele testou e a conta cancelada não apareceu em "canceladas", embora o valor tivesse voltado: o Voltar do
navegador trazia a lista da memória, de antes do cancelamento. Contas a Pagar e Comissões passaram a recarregar
quando voltam da memória (§14.83).

**O usuário começou a testar Comissões Afiliados em 15/out e trouxe três pontos, consertados** (§14.81):

- **O menu de filtro abria para cima**, por cima dos indicadores, quando a barra ficava no pé da janela.
  Correção de componente, nas 81 telas que têm o dropdown: antes de abrir para cima, a página rola o que
  faltar; para cima só quando não rola mais, ou dentro de painel fixo.
- **A conta de comissão, editada em Contas a Pagar, voltava ao valor de Comissões.** O valor é de
  Comissões Afiliados: em Contas a Pagar ele fica travado, com o caminho de volta, e Comissões ganhou
  "cancelar" no pagamento, para refazer com o valor certo.
- **O item "Vendas Afiliados" saiu do menu**: abria a mesma tela de Pedidos de Venda. As vendas
  afiliadas seguem no filtro de origem de Pedidos, e Comissões Afiliados leva até lá.

**Comissões Afiliados, entregas 2a e 2b: feitas e esperando o teste do usuário** (§14.79 e §14.80). Duas telas novas
em Finanças: a lista, com uma linha por quem recebe comissão (vendedor do cadastro ou cliente aprovado
como afiliado de uma loja), e a conta do afiliado, nas linhas do Olist. O cliente pede pela vitrine,
aceitando as regras da loja; a aprovação é no quadro "Inscrições aguardando", e há "Incluir afiliado"
para convite. O percentual é por loja, em Configurações → Cadastro de clientes (Programa de
afiliados). O vendedor não gera link: vende pelo ERP. Editar, excluir e lançar comissão à mão pedem
motivo e senha. **Na 2b**, "realizar pagamento" na conta do afiliado: não passa do saldo de hoje,
pede senha, desce o saldo na hora e faz nascer a conta em Contas a Pagar, com o vendedor ou o cliente
afiliado como favorecido e a categoria nova "Comissões de vendedores e afiliados".

**Vendas Afiliados, entrega 1: testada pelo usuário em 14/out** (§14.78). Ele achou um defeito, a
barra de filtros quebrando de linha ao escolher a origem, que está consertado e espera o teste dele. A venda por link é
Pedido de Venda. A lista ganhou o filtro de origem e a marca "indicação de" na linha e no painel; o
item "Vendas Afiliados" do menu abria a lista filtrada nas vendas afiliadas (saiu do menu em 15/out); a página do pedido mostra quem indicou, num campo que não se digita. A aba Comissões passou
a seguir a regra de quem recebe: aplicava 5% e "integral no faturamento" a qualquer vendedor, e o
botão Faturar prometia liberar a comissão a todos. A entrega 2 é Comissões Afiliados.

Decidido pelo usuário em 14/out, com 12 prints de Comissões do Olist (lista por vendedor, impressão,
período por mês, conta do vendedor com pendentes, editar e excluir comissão, outro lançamento de
crédito ou débito, realizar pagamento) e os textos dos (i) das colunas:

- **Venda por link é Pedido de Venda**, com o mesmo funil. O pedido chega da vitrine dizendo que foi
  indicação e de quem; gerar o link e "minhas indicações" são da vitrine, fora do ERP. O item
  "Vendas Afiliados" do menu saiu em 15/out (abria Pedidos filtrado); a tela nova é só Comissões Afiliados,
  em Finanças, que lê os pedidos e cobre cliente afiliado e vendedor.
- **Afiliado é cliente aprovado** no cadastro (programa com aprovação). **Percentual padrão** em
  Configurações; o vendedor segue a regra do cadastro dele.
- **A comissão do link libera com o pedido entregue e 7 dias sem devolução**; devolução cancela.
- **O link vale 30 dias** (pedido do usuário; a recomendação era 7). O último link clicado vale, e
  compra pelo próprio link não gera comissão.
- **Pagar a comissão gera conta a pagar.** Crédito na loja fica para depois: é o vale-troca que
  Devolução, Formas de Recebimento e PDV já deixam reservado, e entra quando esse submódulo existir.
- **Lucro = venda − custo médio dos produtos − comissão.** Frete fora (quem foi indicado paga) e
  imposto fora (ainda não há nota fiscal).

- **Pagar gera a conta a pagar e o saldo de comissão desce na hora**; se a conta for cancelada, o
  valor volta. Contas a Pagar passa a aceitar vendedor e cliente afiliado como favorecido.
- **Uma pessoa recebe por pedido**, a indicação só chega pelo link (ninguém a digita), e o vendedor
  também gera link na vitrine, com a regra do cadastro dele.
- **A lista de Comissões Afiliados é enxuta** (opção B), com as colunas que forem necessárias. A conta
  inteira do afiliado, nas 9 linhas do Olist, fica ao abri-lo e no relatório impresso; os textos dos
  (i) viram a explicação de cada linha ("Comis. vencidas" = comissões vencidas ainda não pagas).
- **Editar, excluir e lançar comissão à mão** pede motivo, fica no histórico e entra em Confirmações
  com senha.
- **Vale-compra (crédito na loja) depois**, como submódulo próprio: liga o vale-troca que Devolução,
  Formas de Recebimento e PDV deixam reservado, e o pagamento de comissão como crédito.

- **Onde se aprova o afiliado** (usuário, 14/out): no ERP, dentro de Comissões Afiliados. O cliente
  pede pela vitrine, aceitando as regras da loja, e o botão de gerar link só aparece depois de
  aprovado. Há também "Incluir afiliado", para convite, escolhendo um cliente que já está no cadastro.
  O painel adm da vitrine não existe: pela arquitetura, a vitrine é só catálogo, carrinho e checkout.
- **O vendedor não gera link** (usuário, 14/out): ele tem acesso ao ERP e vende pelo pedido ou pelo
  PDV. O link é sempre de cliente afiliado.
- **O percentual do afiliado é por loja** (usuário, 14/out): cada vitrine tem as suas regras e a sua
  comissão.

**As melhorias do estoque (E2, E8 e E10 da lista) estão feitas e esperam o teste do usuário**,
junto com as da venda (V2, V3 e V5) e as de Finanças (F1 a F4), entregues antes no mesmo dia. Ele
mandou seguir a lista grupo a grupo; sobre Finanças, voltou com um ponto só, a barra de rolagem na
tabela de Caixa e Bancos, que entrou nesta entrega.

**O usuário já testou o estoque e voltou com três pontos. Os três estão feitos, e os dois últimos
esperam o teste dele.**

- **O link do Kit Home Office** abria uma lista vazia em Entrada de Notas. Era defeito, está
  consertado e ele deu ok (§14.58, no fim).
- **"Itens Bloqueados" passou a se chamar "Tratamento de Perdas"** (§14.59). Barganhado e fechado
  por ele em 12/out. Muda o nome da tela; "bloqueado" segue sendo a situação do saldo, e o arquivo
  continua `pagina-estoque-itens-bloqueados.html`.
- **A chegada da transferência virou conferência** (§14.60). Aprovado por ele em 12/out, com a
  opção (a): ao fechar com falta, a conferência pergunta se o resto ainda vem (segue em trânsito) ou
  se faltou (vai para Tratamento de Perdas, como falta a auditar).

**Ele testou a conferência e pediu um ajuste na baixa de Tratamento de Perdas, que está feito**
(§14.61): o campo abre em branco, o zero digitado vale como resposta, e o motivo da perda é o da
operação que criou o bloqueio.

**Em 13/out ele voltou com mais dois pontos de Tratamento de Perdas, e os dois estão feitos**
(§14.62): a linha dos Resolvidos abre o painel do bloqueio que saiu da fila, e o que se cadastra em
Configurações → Motivos de Perda passou a valer na baixa. Ele também mandou seguir a lista de
melhorias.

**Movimentação de Estoque é tela nova, feita em 13/out e à espera do teste dele** (§14.63). Ele
pediu em 12/out, com quatro prints de um kardex: o histórico individual de cada produto, do saldo de
antes até o saldo de hoje, com o documento inteiro de cada movimento. É só consulta. O item entrou no
menu de Estoque das 81 telas, logo depois de Controle de Estoques.

**Ele testou no mesmo dia e voltou com dois pedidos, que estão feitos e esperam o teste dele**
(§14.65): o produto passou a ser a busca padrão do sistema, no lugar da lista de escolha, e o período
ficou obrigatório, abrindo no mês atual.

**Ele confirmou os dois e mandou tirar a aba "Lançamentos" da página do produto, o que está feito e
espera o teste dele** (§14.66). O histórico do produto mora só na Movimentação de Estoque. A página
do produto, em Controle de Estoques, ficou com os indicadores, Endereços, Reservas e "Incluir
lançamento", e chega ao histórico pelo botão "Movimentações".

**No fim de 13/out ele testou o que saiu no dia, deu ok em tudo (inclusive no que a outra conversa
entregou) e fechou o que estava aberto.** As setas do teclado valem em toda busca de produto (feito,
§14.70). O filtro com data inicial e final fica onde já está. O kit na compra tem regra. O envio ao
GitHub voltou a ser feito a cada entrega; só a publicação na Cloudflare continua parada. Os links do
chat que não trazem o navegador para a frente ele vai olhar antes de mexermos. **O trabalho segue
numa conversa só**, e ele mandou seguir a fila do item 1 ao 6, começando pela página de detalhe
abrir o registro clicado.

**"Abrir o registro clicado" está feito onde valia a pena, e o resto da lista de melhorias saiu da
fila.** O usuário testou em 13/out e deu ok nas setas da busca, no "Ver cadastro completo" dos cinco
cadastros (§14.71) e na página da ordem de compra (§14.72). Na mesma conversa viu que quase tudo o
que restava esbarrava em dado de exemplo que não bate entre as telas, e decidiu: **os exemplos das
telas prontas ficam como estão, a tela nova já nasce no padrão, e corrige-se só o que precisa**
(§14.73). O que precisava era Pedidos de Venda: a lista mandava o número e a página ignorava. Está
feito e espera o teste dele, junto com o botão "Abrir o romaneio", que não mandava o id.

**O primeiro item da fila nova está feito e espera o teste dele** (§14.74). Parâmetros de estoque
tinha nove seções, e cinco não eram de estoque. Agora são duas telas: Parâmetros de estoque e
Parâmetros de logística. O bloqueio de cliente em atraso foi para Configurações do cadastro de
clientes, por decisão dele. Na mesma resposta ele tirou da fila as cópias do número da meta (R6),
pelo mesmo motivo dos outros alinhamentos de exemplo.

**A impressão em formato de relatório está nas 19 telas que imprimem** (§14.75 e §14.76). O usuário
testou o piloto de Ordens de Compra em 14/out, aprovou a folha como estava e mandou seguir. Nas 15
listas, a folha sai com título, data, quem emitiu, os filtros que estavam valendo e a quantidade,
sem caixa de seleção, seta de ordenação, abas nem indicadores; nos 4 documentos (Conferência, Nota
de Entrada, Ordem de Compra e Pedido de Venda), com a data e quem emitiu, mantendo o título da
página. Espera o teste dele nas outras listas.

**A segunda varredura está feita e os achados, consertados; testados e aprovados pelo usuário em 14/out** (§14.77).
Inventário, Acerto, PDV com caixa aberto e a contagem da Conferência de Entrada foram percorridos do
começo ao fim. Saíram seis defeitos e três decisões; ele mandou seguir as sugestões: entrada de
acerto em qualquer depósito, aviso do desconto da venda no campo, e uma confirmação por divergência
na conferência, como já era. O próximo passo, combinado com ele, é a barganha dos módulos novos.

**O `selo.py` voltou a fechar.** A suíte `teste_cad_melhorias.py` travava a rodada porque a prova por
defeitos injetados foi interrompida quando a conversa caiu, e o defeito ficou no arquivo de verdade
(a lixeira da aba nova não removia o produto). O arquivo foi restaurado, o teste ganhou teto no laço
que ficava preso, e a prova passou a rodar numa cópia das telas, fora do projeto (§14.67).

**A lista de melhorias chegou aos cadastros.** O usuário mandou seguir em 13/out, e o primeiro item,
C2 (o painel do fornecedor), está feito. Ele testou, deu ok no resto e pediu uma mudança: a lista
dos produtos sair do painel lateral e virar a aba "Produtos Fornecidos" dentro do cadastro do
fornecedor. Está feita e espera o teste dele (§14.67). Faltam C3 a C8.

**Ainda em 13/out ele voltou com um defeito e dois ajustes, e os três estão feitos e esperam o teste
dele** (§14.68). O Esc não fechava o painel lateral nos cadastros: medido nas 81 telas, eram 42
painéis em seis módulos, e o conserto foi de componente, nas 61 telas que têm painel. O campo de
produto da Movimentação de Estoque ganhou o "x" que tira o produto, e as sugestões de produto do PDV
ficaram com a cara da busca padrão.

**Três assuntos ele quis conversar antes de mexer, respondeu no mesmo dia, e os três estão feitos e
esperam o teste dele** (§14.69). O menu passou a seguir a sequência de trabalho, nas 81 telas, com a
regra escrita para módulo novo. Nos cinco cadastros com página própria, o painel traz "Ver cadastro
completo" e o "Editar cadastro" fica no topo da página. E a caixa de busca de produto do PDV ficou
no formato das outras.

**Duas conversas mexeram no projeto ao mesmo tempo em 13/out**: uma no painel dos resolvidos de
Tratamento de Perdas, outra na Movimentação de Estoque. Cada uma fez o commit só do que era dela, e
o selo completo rodou no fim, com as duas entregas no disco.

Dois itens do grupo da venda não entraram, e o motivo é o mesmo: o exemplo da tela de destino não
tem o registro. V4 (do painel de Metas para os pedidos do mês) e L4 (do Rastreamento para a conta a
receber e o romaneio) esperam o alinhamento dos dados de exemplo, que virou os itens X4 e X5.

A impressão em formato de relatório segue analisada e por fazer: ele pediu para deixar para depois.

### Onde estamos

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

### Balanço de 15/out/2026

Pedido do usuário no fim da semana: o que existe, o que ganhamos, quanto falta e quando termina. Os números
são medidos (telas, itens de menu, suítes, commits). A projeção é estimativa, com a premissa dita ao lado.

### O que existe

| | hoje |
|---|---|
| Telas de protótipo | 86 (85 telas e o molde de referência) |
| Itens de menu com tela | 43 de 55 itens (78%) |
| Telas que faltam para fechar o menu | cerca de 20 (12 itens × 1,5 tela, a média das já feitas) |
| Produção (o sistema de verdade) | **0%**: não começou |
| Verificação | 54 suítes, 5.787 asserções, 442 defeitos injetados de propósito e pegos, 2 auditorias nas 86 telas |
| Documentação | design system até a §14.89 |
| Trabalho | 88 commits desde 06/out; o projeto tem 32 dias (14/set a 15/out) |

### O que ganhamos desde 12/out (80 telas e 41 de 55 itens)

- **+4 telas e +2 itens de menu**: Movimentação de Estoque, Parâmetros de logística, e Comissões Afiliados
  (lista e conta do afiliado). O protótipo foi de 75% para 78%.
- **O programa de afiliados inteiro**: a venda por link é Pedido de Venda, a comissão segue a regra de quem
  recebe, o cliente pede para ser afiliado e a aprovação é em Comissões, o percentual é por loja, o saque é
  pedido na vitrine e vira conta a pagar, a baixa volta como "pago", e a conta tem histórico com saldo, período
  por data inicial e final e filtro por tipo, mês e ano. O cadastro do cliente mostra o mesmo histórico.
- **Os detalhes abrem o registro clicado** (cadastros, ordens de compra, pedidos de venda).
- **Impressão em formato de relatório** nas 19 telas de lista e de documento.
- **A segunda varredura**: seis defeitos de Inventário, Acerto e PDV consertados.
- **Regras novas de interface**: todo menu de filtro abre para baixo (81 telas) e a tabela não rola na
  horizontal de 1280 px para cima (regra reforçada; das 25 telas antigas que não cumpriam, 22 foram consertadas em 19/out e 3 esperam decisão).
- **Limpeza**: o desvio morto para o Inventário saiu de 18 telas.
- **Verificação**: de 50 para 52 suítes, de 5.090 para 5.344 asserções.

### Módulos: prontos e faltantes

| módulo | itens com tela | telas | falta |
|---|---|---|---|
| Início | 4 de 4 | 4 | nada |
| Cadastros | 12 de 13 | 17 | Relatórios de Cadastros |
| Estoque | 13 de 14 | 18 | Relatórios de Estoque |
| Vendas | 4 de 8 | 6 | Notas Fiscais, Margem de Contribuição, Custos do E-commerce, Relatórios de Vendas |
| Logística | 5 de 6 | 10 | Relatórios de Logística |
| Finanças | 4 de 5 | 10 | Relatórios Finanças |
| Integrações | 0 de 4 | 0 | Marketplaces e Hubs, Gateways de Pagamento, Emissão de Notas Fiscais, Relatórios de Integrações |
| Configurações | hub (1 item) | 20 | a lista fiscal da NF-e (Formas de pagamento) |

**Fora da contagem de 55**: o Vale-compra (decidido em 14/out; as 2 telas da entrega 1 e a aba do cliente estão feitas), a vitrine da Desk Shope (F3, app
separado, sem protótipo aqui) e as Ordens de Serviço da Desk Tech (F7, sem protótipo).

### Onde cada fase do roadmap está

| fase | protótipo | produção |
|---|---|---|
| F0 Fundação técnica | n/a | não começou (sem contas de Supabase e Cloudflare, por decisão dele) |
| F1 Acesso e Core | Dashboard, Interface do usuário, Confirmações com senha, Registro de atividades | não |
| F2 Cadastros base | 12 de 13 itens | não |
| F3 Vitrine MVP | **não existe**: a vitrine é outro app | não |
| F4 Fulfillment | Separação, Conferência de Saída, Expedição, Rastreamento, Devolução | não |
| F5 Estoque e Financeiro | Estoque 13 de 14, Finanças 4 de 5 | não |
| F6 Lançamento | n/a | não |
| F7 Réplica Desk Tech | **não existe**: Ordens de Serviço | não |
| F8 Pós-MVP | feito adiantado: CRM, PDV, Metas, Comissões; falta NF-e, Marketplaces, Relatórios, Margem, Custos | não |

Dos 12 itens que faltam, **só Gateways de Pagamento está no caminho do MVP** (F0 a F6). Os outros 11 são
pós-MVP (F8) pelo próprio roadmap. Para vender, o protótipo está praticamente completo; o que não existe é o
sistema de verdade.

### Projeção (estimativa)

- **Protótipo do menu inteiro.** Premissa: cada item novo leva de 1 a 3 dias (barganha, construção e uma a
  duas rodadas de teste dele), mais cerca de 7 dias dos itens já decididos (vale-compra, pagamentos vencidos,
  varredura da barra). São de 19 a 43 dias de trabalho. A partir de 19/out: **mais cedo, 13/nov; mais
  provável, entre 30/nov (5 dias por semana) e 11/dez (4 dias por semana); mais tarde, 3/jan.** Esta semana o
  limite semanal fechou na quinta, e é o que decide quantos dias por semana existem.
- **Produção F0 a F6**, sem medida própria (nada foi feito). Referência: o protótipo levou 32 dias para 84
  telas, e tela de verdade (banco, regra, teste, segurança) custa de 2 a 3 vezes o protótipo: de 3 a 5 meses
  depois de começar. **Começando agora, a primeira venda real (F6) cai entre fevereiro e abril/2027; começando
  depois do protótipo (dezembro), entre abril e junho/2027.** A meta do roadmap (F0 a F6 até dezembro/2026) não
  fecha nesse ritmo; dá para ter em dezembro F0, F1 e parte da F2 funcionando, se começar já.

### Prioridades dos próximos passos

1. **Decidir quando começar a produção** (F0: contas, esquema do banco, login). É o caminho crítico, e hoje
   está em 0%. Recomendação: começar já, em paralelo com o protótipo que sobra. Conta nova só nasce com o
   pedido dele.
2. **Vale-compra, entregas 2 e 3** (1 a 2 dias): usar o vale no PDV e no Pedido de Venda, e nascer da Devolução e da Comissão; liga o vale-troca que Devolução, Formas de Recebimento e PDV deixam reservado.
3. **Gateways de Pagamento**: o único item do menu que está no caminho do MVP.
4. **O protótipo da vitrine Desk Shope** (F3): não existe; decidir quando desenhar.
5. **Os 11 itens pós-MVP**, quando a produção estiver de pé: Margem de Contribuição e Custos do E-commerce
   (leem o que já existe), depois Relatórios, Notas Fiscais e Integrações.
6. **Parados de propósito**: kit com composição (depende do cadastro de produtos) e o alinhamento dos exemplos
   (volta com o banco).

### O que ficou pronto nesta conversa

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
  o enviado e o recebido, quem enviou, quem recebeu e o tempo em trânsito. (O recebimento que saía
  dali virou conferência: item 7.)
- **Tratamento de Perdas** (na época, Itens Bloqueados): "De onde veio" leva ao documento: a nota em Entrada de Notas e a ficha do
  pedido na Separação e na Conferência de Saída. Acerto, devolução e bloqueio manual seguem em
  texto.

**7. A chegada da transferência é uma conferência de entrada** (12/out, §14.60), pedido do usuário:

- **Na Transferência Entre Estoques** o painel "Confirmar recebimento", que já vinha com a
  quantidade preenchida, saiu. O botão é "Conferir chegada", na linha e no painel.
- **A contagem é a da nota de entrada**, na mesma tela: cega (a quantidade enviada fica escondida
  até contar, e não vaza pelo resumo), com motivo em toda divergência.
- **No fechamento, do que não veio a tela pergunta:** "o resto ainda vem" (segue em trânsito, e
  depois se confere só o resto) ou "faltou" (vai para Tratamento de Perdas, como falta a auditar).
  Avaria que ficou conosco também vai para lá; a que voltou com o transportador segue em trânsito.
- **Fechar devolve a pessoa para a lista de transferências**, que diz o que aconteceu, e o painel
  passa a mostrar quem recebeu, quando, e o que faltou ou veio avariado por item.
- **A fila da Conferência de Entrada mostra a transferência a caminho**, junto das notas e das
  devoluções, e leva à contagem dela. As colunas passaram a "Documento" e "De onde vem".
- **Em Tratamento de Perdas**, a origem "TR-0101" leva à transferência, e a tela ganhou a busca
  pelo endereço, como as outras listas.
- **A senha** é a mesma que o recebimento já pedia. Em Configurações ela agora se chama "Fechar
  conferência de chegada de transferência".

**8. Tratamento de Perdas: o zero e os motivos da baixa** (12/out, §14.61), pedido do usuário depois
de testar a conferência:

- **Os campos de "O que fazer" abrem em branco.** O "0" cinza que aparecia parecia valor, e confirmar
  era barrado.
- **Zero digitado é resposta.** 0 em "Volta para a venda" quer dizer que nada foi recuperado: a linha
  inteira vai para a baixa por perda, e a tela pede o motivo.
- **O motivo da perda é o da operação que criou o bloqueio.** Transferência: perda em trânsito,
  avaria no percurso, furto ou roubo no trajeto. Conferência de entrada: avaria do fornecedor, no
  recebimento, no transporte da compra. Separação e conferência de saída: avaria na separação, no
  picking, na embalagem, não encontrado no endereço. Eles vêm antes dos motivos gerais.
- **O cadastro de Motivos de Perda** (Configurações) ganhou o campo "Em que baixa o motivo aparece".
  Os dez motivos novos estão lá, e ele pode trocar, renomear ou criar outros.
- **Na ficha da Separação**, o campo "Quantidade que você achou" tinha o mesmo "0" cinza; saiu.
- **A linha dos Resolvidos abre o painel** (13/out, §14.62): de onde veio, quem bloqueou, quanto
  tempo ficou parado, quem liberou ou baixou, o desfecho, o valor e a história do bloqueio.
- **O cadastro de Motivos de Perda vale na baixa** (13/out): motivo criado, renomeado, inativado ou
  excluído em Configurações aparece assim na baixa de Tratamento de Perdas. A lista do Acerto de
  Estoque continua fixa.

**9. Movimentação de Estoque** (13/out, §14.63), módulo novo pedido pelo usuário:

- **A tela abre só com os filtros**, na ordem que ele pediu: depósito, produto, tipo de movimento,
  data inicial, data final e Buscar. O produto é a busca padrão do sistema: digitar nome, código (SKU)
  ou GTIN e escolher na sugestão. Produto e período são obrigatórios, e as datas abrem no mês atual.
  Vindo do botão "Movimentações" da página do produto, a tela já mostra o mês daquele produto.
- **Depois de Buscar:** o quadro do produto, cinco indicadores (estoque atual, reservado, disponível,
  custo médio e valor em estoque) e a lista em ordem de data, até o saldo de hoje. Cada linha traz
  data e hora, movimento, cliente ou fornecedor, saldo anterior, quantidade, saldo atual, valor
  unitário, custo médio e valor em estoque.
- **Clicar no movimento abre o documento inteiro**, no painel ao lado: de onde veio, para quem foi,
  quem lançou, peso, valor e todos os itens que foram junto, com o produto consultado marcado.
- **É só consulta.** O que sai da tela é papel e planilha: "Imprimir documento" manda só o documento
  aberto para a folha; a lista tem "Imprimir lista", "Baixar planilha" e "Resumo por tipo".
- **A tela não tem dado próprio de compra e venda.** Ela monta o histórico com o mesmo bloco de dados
  do Giro de Estoque e de Necessidades de Compra. Por isso o saldo final de cada produto, em cada
  depósito, é o do Controle de Estoques, e as vendas de um período são as que o Giro mostra.
- **As vizinhas levam para lá:** Controle de Estoques ("Mais ações"), a página do produto (botão
  "Movimentações") e o painel do Giro. A tela leva de volta à página do produto e ao Giro.
- **A aba "Lançamentos" saiu da página do produto** (13/out, §14.66), por decisão dele: eram duas
  listas para a mesma pergunta. Saíram junto os filtros de período e de tipo, que só serviam à lista.
  A página abre em Endereços, e "Incluir lançamento" passou a dizer no aviso o que gravou.

**10. Cadastros: o painel do fornecedor, item C2 da lista** (13/out, §14.64):

- **O painel mostra o que as outras telas têm do fornecedor:** ordens de compra em aberto e quanto
  falta receber, a última compra, as contas a pagar em aberto e quanto se deve, e de quantos produtos
  ele é o fornecedor padrão. Ordens e contas têm link.
- **A lista dos produtos mora no cadastro, na aba "Produtos Fornecidos"** (pedido dele, §14.67),
  antes de Observações. Cada linha tem o custo neste fornecedor e o pedido mínimo, que se editam, e
  o custo médio, o giro mensal, o preço de venda e o lucro por unidade caso a compra seja feita ali.
  Adiciona-se pela busca padrão de produto; a lixeira tira da lista.
- **O cadastro de exemplo passou a ser a TechParts**, que tem produtos; era um fornecedor de quem
  nunca se comprou.
- **O exemplo do cadastro foi alinhado.** Ele trazia nomes de cliente; seis registros viraram os
  fornecedores que Ordens de Compra, Entrada de Notas e Contas a Pagar usam, com o mesmo nome e o
  mesmo CNPJ, e a Papelaria Central perdeu o "Ltda" que só existia ali.

**11. Esc fecha o painel lateral, em toda tela** (13/out, §14.68), defeito relatado pelo usuário:

- **O Esc não fechava 42 painéis**, em seis módulos (12 só em Cadastros), embora todo painel mostre
  "ESC" ao lado de fechar. Cada tela escrevia o seu tratamento da tecla, e a maioria só fechava o
  modal de confirmação.
- **O conserto é um bloco comum**, nas 61 telas com painel e no molde: o Esc vale como clicar no
  "fechar" do painel aberto. Com menu, calendário, sugestão ou modal por cima, o de cima fecha
  primeiro.
- **Sete telas tinham tratamento próprio que fechava o painel com algo na frente** (Estágios do
  funil, Formas de recebimento, Contas a Pagar, Contas a Receber, Transferência, Conferência de
  Entrada e Inventário). O tratamento próprio saiu delas; ficou o bloco comum.
- **Movimentação de Estoque:** o campo de produto tem um "x" que tira o produto e deixa o cursor
  pronto para pesquisar outro.
- **PDV:** as sugestões de produto saem com o nome em cima e os dados embaixo, como na busca padrão.
  Lado a lado, o texto não cabia e a caixa ganhava barra de rolagem.

**12. O menu por sequência de trabalho, "Ver cadastro completo" e a busca do PDV** (13/out, §14.69):

- **O menu segue a sequência de trabalho, e não o alfabeto**, igual nas 81 telas. A regra: a tela de
  consulta do módulo, depois as telas na ordem em que o trabalho acontece, depois a análise, e
  Relatórios por último. Mudaram Cadastros, Estoque, Vendas, Finanças e Integrações.
- **Módulo ou item novo entra na posição da função dele.** A regra está no §4 do design system, no
  mapa dos módulos e nas skills, e a seção 11 de `teste_menu.py` reprova o menu fora da ordem.
- **Um nome de menu estava diferente em duas telas:** "Gateways de Recebimento" em Contas a Receber e
  na página da conta, contra "Gateways de Pagamento" nas outras 79. Voltou o nome comum.
- **"Ver cadastro completo"** no painel de Clientes, Fornecedores, Produtos, Vendedores e Lojas
  Desk. A página abre só para leitura, e o botão "Editar cadastro", no topo, destrava.
- **PDV:** a caixa de busca de produto é arredondada e tem a lupa, como as outras.
- **Setas do teclado em toda busca de produto** (§14.70): ↑ e ↓ andam pela lista de sugestões, dando
  a volta no fim, e o Enter escolhe o item marcado. Vale nas cinco telas que usam a busca padrão
  (Acerto, Nova Transferência, Tratamento de Perdas, Movimentação e Produtos Fornecidos); antes, só o
  PDV tinha.
- **O cadastro completo abre o registro clicado** (§14.71, item G3), nos cinco cadastros. A página
  mostra o que a lista sabe daquele registro (título, situação, documento, endereço, contato). Só o
  registro do exemplo tem o cadastro inteiro desenhado; nos outros, o que a lista não sabe fica em
  branco, em vez de herdar o dado do exemplo. No fornecedor, a aba Produtos Fornecidos traz os
  produtos de que ele é o fornecedor padrão.
- **Quatro defeitos de antes, achados no caminho:** trocar a loja ou a categoria no cadastro
  estragava o subtítulo ("Cadastro Manual — undefined", "Vinculado à undefined"); o cadastro novo
  herdava código, contatos, anexos e custo do exemplo; o documento duplicado do cliente acusaria o
  próprio cliente aberto; e o fornecedor do exemplo mostrava "Fornece para" e "Fornecedor desde" de
  outro registro.
- **Contas a Pagar e Contas a Receber** levam ao cadastro do fornecedor e do cliente pelo nome: a
  numeração delas não é a do cadastro.
- **A página da ordem de compra abre a ordem clicada** (§14.72): fornecedor, depósito, datas,
  situação, itens e total. O total da página fecha com o da lista nas 14 ordens. Clonar copia a
  ordem aberta, a Conferência leva à ordem da nota, e a ordem criada em Necessidades de Compra abre
  com os itens dela. Ordem atendida ou cancelada deixou de oferecer "Receber mercadorias".
- **A página do pedido de venda abre o pedido clicado** (§14.73): cliente, loja, vendedor, datas,
  situação, itens e total, nos 16 pedidos e na venda de balcão. O total da página fecha com o da
  lista. Pedido sem itens no exemplo mostra um "Item de exemplo" pelo valor dele, e não acusa falta
  de saldo. O clone parte do pedido aberto, e "Dados do cliente" abre o cadastro daquele cliente.
- **"Abrir o romaneio"** leva o id. A página do romaneio conhece 3 dos 9; para os outros ela abre o
  romaneio padrão e avisa.
- **Parâmetros de estoque se dividiu em dois** (§14.74). Em Parâmetros de estoque ficaram a
  conferência de compra, o endereçamento, a base de picking, a compra e o giro, e a reserva do
  pedido. Em Parâmetros de logística, tela nova, as filas do galpão, a expedição e o romaneio, o
  MDF-e e a devolução. "Bloquear novo pedido de cliente em atraso" está em Configurações do
  cadastro de clientes. Os 22 parâmetros continuam tendo tela, cada um numa só, e salvar numa tela
  não mexe no que é da outra.
- **Comissões Afiliados, entrega 2b** (§14.80). Realizar pagamento: a conta nasce em Contas a Pagar
  (lista e página da conta leem o mesmo bloco), a categoria nova está nas 8 telas que repetem as
  categorias, e a ação entrou no catálogo de senha.
- **Comissões Afiliados, entrega 2a** (§14.79). A lista e a conta do afiliado, as inscrições, o
  percentual por loja em Configurações e as ações com senha. Cada comissão é arredondada em centavos
  antes de somar.
- **Vendas Afiliados, entrega 1** (§14.78). A venda por link é Pedido de Venda, com filtro de origem
  e a marca de quem indicou; o item do menu abre a lista filtrada; a aba Comissões e o botão Faturar
  seguem a regra de quem recebe (cadastro do vendedor ou programa de afiliados).
- **Os achados da segunda varredura** (§14.77). Inventário: fechar sem senha diz por quê; cancelar com
  contagem pergunta; os códigos recusados do arquivo aparecem, com o motivo. Acerto: cada depósito
  uma vez; entrada em qualquer depósito; saída maior que o endereço para na linha. PDV: o desconto
  da venda acima do máximo avisa no campo. As duas telas que mostravam outro usuário mostram o mesmo
  das outras 80.
- **Impressão em formato de relatório nas 19 telas** (§14.75 e §14.76). O cabeçalho do relatório só
  existe no papel. "Imprimir", no menu, e o Ctrl+P dão a mesma folha, com a lista inteira. O
  código está no bloco comum de planilha e impressão, igual nas 19.

**13. A verificação.** Dezessete suítes novas: `teste_retorno.py`, `teste_fin_melhorias.py`,
`teste_venda_melhorias.py`, `teste_estoque_melhorias.py`, `teste_transf_conferencia.py`,
`teste_perdas_baixa.py`, `teste_movimentacao.py`, `teste_cad_melhorias.py`, `teste_esc_painel.py`,
`teste_busca_setas.py`, `teste_cad_detalhe.py`, `teste_doc_detalhe.py`, `teste_parametros.py` e
`teste_impressao.py`, `teste_varredura2.py`, `teste_afiliados.py` e `teste_comissoes.py`. Trezentos
e oitenta e sete defeitos injetados de propósito, um por vez; os trezentos e oitenta e sete são pegos. A auditoria do
projeto reprova qualquer menção à ferramenta que saiu e enxerga chave de armazenamento guardada em
constante.

**14. As skills do ERP** ganharam o que o retorno ensinou, na seção "A tela dentro do sistema" e no
"mapa de vizinhança". O texto está na cópia que o Claude carrega neste computador e em
`C:\Claude AI\Skills\Skills ERP System`.

**15. Comissões 2f: os pagamentos vencidos** (19/out, §14.87): o quadro "Pagamentos vencidos" com dar baixa,
reprogramar e cancelar, "vencido há N dias" na conta e no cadastro, o que a vitrine vai mostrar ao cliente, o
cancelar sozinho como opção desligada, reprogramar no catálogo de ações, o exemplo de fábrica em seis telas, o
Início somando as contas de comissão, e o link para Contas a Pagar que escondia a conta do mês seguinte. A seção 10
de `teste_comissoes.py` tem 71 asserções; 23 defeitos injetados e os 23 pegos. Selo: 52 suítes, 5.414 asserções.

**16. O exemplo de Comissões em navegador com pagamento** (19/out, §14.87): marca própria `deskComissoesExemplo`, que
acrescenta os três pagamentos sem apagar nem duplicar. Quatro asserções novas na seção 10 de `teste_comissoes.py`.

**17. A varredura da barra de rolagem** (19/out, §14.88): 22 das 25 telas com tabela rolando a 1280px consertadas pelo
bloco de Comissões, 3 pendentes de decisão, e a suíte `teste_barra_tabelas.py`. Na segunda rodada: a `.itens-table` dos
três detalhes de documento, a data com hora que não quebra em Conferência de Saída e Separação, e a suíte passou a medir
quatro detalhes com registro aberto (87 asserções). Selo: 53 suítes, 5.519 asserções.

**18. Vale-compra, entrega 1** (19/out, §14.89): a lista, a página do vale, a aba do cliente e a validade em Configurações; o vale é saldo do
cliente por loja, nasce como cortesia (com senha), cancela e reativa. `teste_vale_compra.py` tem 223 asserções; 23 defeitos injetados e os 23 pegos.
Selo: 54 suítes, 5.787 asserções.

### Próximo da fila

Refeita em 19/out, depois da varredura da barra (a lista completa e os porquês estão em "Prioridades dos próximos passos").

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

### Decidido, e ainda não feito de propósito

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

### Esperando decisão do usuário

Duas pendências, que são dele:

1. **Reenviar as skills do ERP pelo claude.ai, se quiser.** As regras que o Claude segue no ERP
   (o padrão de tela e o portão de qualidade) existem em dois lugares: nesta máquina, onde são
   atualizadas a cada entrega, e na conta dele no claude.ai, de onde o plugin foi enviado. A cópia
   da conta ficou com o texto antigo. Só faz diferença se ele trabalhar no ERP fora deste
   computador; para atualizar, reenvia por lá a pasta
   `C:\Claude AI\Skills\Skills ERP System\desk-company-erp`.

2. **Confirmar quatro escolhas da entrega 1 do Vale-compra** (§14.89): (a) a busca de cliente do "Incluir vale" é a busca padrão de produto, adaptada
   (nome, CPF/CNPJ ou e-mail), porque o sistema só tinha a de produto; (b) o "Voltar" da página do vale leva os filtros da lista pelo endereço, o que
   Comissões não fazia; (c) os três indicadores da lista não filtram ao clicar; (d) o uso do VC-3 é de 11 dias atrás, e não dos 10 do plano, para
   cair no dia do Pedido nº 10. De fábrica nenhum vale vence em 30 dias (o prazo é 180), então esse indicador abre em zero.

O defeito dos links do chat que não traziam o navegador para a frente era da sessão do editor e
sumiu sozinho (confirmado por ele em 13/out).

### O que continua sendo dado de exemplo

O usuário aceitou, em 10/out/2026, que isto fique assim nesta fase:

- **Cada tela tem os seus registros de exemplo.** Um link entre telas cai na lista vizinha já
  filtrada; quando o exemplo de lá não tem o registro, a faixa da lista explica isso.
- **O pedido não anda sozinho de uma fila para a outra.** Concluir a separação guarda o que foi
  feito, mas o pedido não aparece na fila da Conferência de Saída por causa disso.
- **Quatro títulos de Contas a Receber** têm cliente ou valor diferente do pedido que citam, e os
  romaneios da Expedição levam pedidos que o Pedido de Venda dá como em separação.
- **Nos cinco cadastros, só o registro do exemplo tem o cadastro inteiro:** dos outros a página
  mostra o que a lista sabe.
- **Doze dos 16 pedidos de venda não têm itens no exemplo.** O painel e a página mostram um "Item de
  exemplo" pelo valor do pedido. Do cliente, só o do exemplo tem contas em aberto e últimas vendas.
- **O pedido nº 2 existe em duas versões:** aberto pela lista, traz os itens e o total da lista; a
  página sem id abre o exemplo desenhado nela, com os mesmos produtos em outras quantidades e outro
  total.
- **O romaneio:** a página conhece 3 dos 9 da lista. Para os outros ela abre o romaneio padrão e
  avisa que o pedido não está naquela fila.
- **A Nota de Entrada não tem "abrir a nota":** a lista só leva à nota nova.
- **Dez das 14 ordens de compra não têm itens no exemplo.** O painel da lista e a página da ordem
  mostram um "Item de exemplo" pelo total da ordem. Escrever os itens de verdade mexe no "já pedido"
  de Necessidades de Compra e do Giro, e entra com os alinhamentos: é o item X7.
- **Conferência de Saída:** três dos nove pedidos da fila (os já conferidos) não estão na página do
  pedido, que avisa quando o pedido não existe nela.
- **Fornecedor ou cliente de Finanças que o cadastro não tem** (sete dos dez fornecedores de Contas
  a Pagar, e o "Consumidor Final" de Contas a Receber): "visualizar dados" abre o cadastro de
  exemplo. É o item X6.
- **A categoria do produto não aparece no cadastro completo:** a página só aceita categoria depois
  da Loja Desk, e a lista não diz a loja. Entra com o C3.
- **A venda do PDV e a ordem criada em Necessidades de Compra** não aparecem em todas as telas
  vizinhas (a ordem aparece em Ordens de Compra; a página dela abre o exemplo fixo).
- **Os valores financeiros do Dashboard** são próprios, e os de cada loja são uma fatia do total.
- **A conferência da transferência não mexe no saldo das outras telas.** A lista de transferências,
  a fila e Tratamento de Perdas enxergam o resultado; Necessidades de Compra continua contando a
  transferência como "a caminho", e o Controle de Estoques não recebe as unidades. "Registrar
  chegada", na fila, vale até recarregar a página, como já era com as notas.

- **Na Movimentação de Estoque, compra e venda vêm do bloco de dados do Giro**, que guarda dia e
  quantidade. Depósito, documento, cliente, preço e peso são montados pela própria tela, sempre do
  mesmo jeito. O exemplo guarda 12 meses: o que havia antes aparece como "saldo antes".
- **O documento do movimento não é link para a tela de origem.** A nota, o pedido e a transferência
  do histórico não existem no exemplo de Entrada de Notas, de Pedidos de Venda nem da Transferência.
  O painel mostra o documento inteiro; o link nasce quando os exemplos se alinharem.
- **Os três pagamentos de comissão de exemplo** (2f) nascem no primeiro acesso de cada navegador, contados a partir
  daquele dia; limpar o navegador traz de volta. O Início soma as contas de comissão ao número de contas a pagar, mas
  o resto daquele número é o do exemplo da própria tela.
- **Reservado aparece 0 em todo produto:** o Controle de Estoques ainda não calcula a reserva a
  partir dos pedidos, e a Movimentação lê de lá.
- **O lançamento feito na página do produto vale até recarregar a página**, como o saldo dela. O
  aviso diz o que foi gravado; ele não aparece na Movimentação de Estoque, que lê outro exemplo.

Quando o sistema rodar de verdade, o usuário limpa tudo e configura do zero.

### Ficou de fora da Movimentação de Estoque, de propósito

- **Lote:** o sistema não controla lote.
- **Multiplicador de embalagem**, que o print tinha na lista de itens: o cadastro do exemplo não tem.
- **O botão "Nota Fiscal" e os valores de ICMS:** são fiscais, e a NF-e não está habilitada. A linha
  aparece como reservada, igual aos outros campos fiscais.
- **Mudança de situação sem mudança de saldo** (endereçar, bloquear, reservar): a lista mostra o que
  entra e o que sai do saldo físico. Endereçar se vê em Endereçamento, e bloquear em Tratamento de
  Perdas; a página do produto mostra a situação de hoje, por endereço.

### Ficou de fora de Necessidades de Compra e Giro, de propósito

- **Tags** (filtrar por tags e "aplicar tags"): marcador não existe neste sistema (§12.1).
- **Natureza de operação:** é fiscal, e a NF-e não está habilitada.
- **Prazo de entrega do fornecedor:** não existe no cadastro; a data prevista da ordem é digitada.
- **Os pedidos que ainda vão sair** são dado de exemplo da própria tela: Pedidos de Venda tem outro
  cadastro de produtos.

### Para retomar numa conversa nova

1. Abra o editor na pasta `C:\Claude AI\Desk Company`.
2. Primeira mensagem: "vamos para onde paramos", com os prints do próximo módulo, se for o caso. É
   para ler este arquivo e seguir do próximo da fila.
3. Para ver as telas: `node _ferramentas/servidor.js` na pasta `ERP System`, e depois
   `http://localhost:3000/<pasta>/<arquivo>`. O servidor cai quando a sessão fecha.
4. Antes de dar algo por pronto: `python selo.py --rodar` na pasta `_ferramentas`.
5. Commit e envio ao GitHub a cada entrega (liberado pelo usuário em 13/out/2026). Nada é publicado
   na Cloudflare ainda.
