# Mapa dos módulos — ERP Desk Company
*Gerado em 02/out/2026, atualizado em 05/out com a Separação e a Conferência de Saída, em 06/out com a Expedição e o cadastro de Transportadoras em 09/out com o PDV, o CRM e Tratamento de Perdas e em 10/out com Necessidades de Compra e Giro de Estoque e com a primeira leva de melhorias dos módulos prontos, em 12/out com o retorno do usuário sobre ela, e em 13/out com a Movimentação de Estoque e com a ordem nova do menu, por sequência de trabalho. Lido do próprio menu do sistema (não de uma lista escrita à mão).*

*Em 15/out/2026: Comissões Afiliados (lista e conta do afiliado) e a venda por link como filtro de Pedidos de Venda; 43 de 55 itens de menu com tela.*

*Em 30/out/2026 (depois da entrega 3): Custos do E-commerce, entrega 4, a embalagem automática: Cadastros › Embalagens ganhou custo e o tipo Insumo; a Separação escolhe a embalagem do pedido, a Conferência de Saída confirma, e Custos e a página do pedido leem o que foi confirmado, com o custo do dia. Nenhuma tela nova: 45 de 55 itens de menu com tela, em 90 telas (§14.99).*

*Em 30/out/2026: Custos do E-commerce, entrega 3 (os anúncios lidos de Contas a Pagar, o gráfico mês a mês, oito cards com "Abaixo da margem" e o módulo no perfil do vendedor) e a tela nova **Parâmetros de vendas**, em Configurações: 45 de 55 itens de menu com tela, em 90 telas (§14.98).*

*Em 22/out/2026: Custos do E-commerce, entrega 1 (a tela nova, a caixa "Resultado do pedido" na página do pedido e a conta única do lucro, que Comissões Afiliados passou a usar), em Vendas: 45 de 55 itens de menu com tela, em 89 telas (§14.95).*

*Em 20/out/2026: Gateways de Pagamento, entrega 1 (a lista e a página do gateway), em Integrações: 44 de 55 itens de menu com tela, em 88 telas. A conta financeira de cada gateway aparece em Configurações → Contas financeiras (§14.92).*

*Em 19/out/2026: Vale-compra, entrega 1 (a lista, a página do vale e a aba Vale-compra do cadastro do cliente), em Finanças. **O Vale-compra é fora da contagem de 55 itens**: ele não era um dos itens que faltavam, é um submódulo extra decidido em 14/out. Por isso os números abaixo seguem 43 de 55; o que sobe é o total de telas, de 84 para 86.*

**90 telas construídas** · ✅ tem tela · ❌ não existe ainda

> **A ordem das tabelas é a do menu** (desde 13/out/2026): primeiro a tela de consulta do módulo, depois as telas na ordem em que o trabalho acontece, depois a análise, e Relatórios por último. Módulo ou item novo entra na posição da função dele. A regra está no §4 do design system, e a seção 11 de `teste_menu.py` guarda a ordem.
>
> **Onde estão os arquivos (desde 08/out/2026):** cada tela mora em `telas/<módulo>/`, na pasta do módulo em que este mapa a lista. O dashboard de KPIs fica em `telas/inicio/`. `telas/integracoes/` tem desde 20/out as duas telas de Gateways de Pagamento. Ver §14.44 e §14.92 do design system.

---

## 🏠 Início — 4 de 4
| | Submódulo |
|---|---|
| ✅ | Página inicial *(a tela de boas-vindas; 10/out: os atalhos levam às telas, e o quadro "Pendências do Dia" leva a cada fila de trabalho, com a quantidade de cada uma)* |
| ✅ | Dashboard KPIs *(10/out: cada quadro leva à tela de origem)* |
| ✅ | Agenda |
| ✅ | Minha Conta |

## 📇 Cadastros — 12 de 13
| | Submódulo |
|---|---|
| ✅ | Clientes *(+ detalhe)* |
| ✅ | Fornecedores *(+ detalhe)* |
| ✅ | Vendedores *(+ detalhe)* |
| ✅ | Produtos *(+ detalhe)* |
| ✅ | Categorias |
| ✅ | Departamento de Produtos |
| ✅ | Seção de Produtos |
| ✅ | Marcas de Produtos |
| ✅ | Embalagens *(com custo, "cabe até" e o tipo Insumo, a tag, a fita e o saco, que entram sozinhos no pedido de uma loja ou de todas, desde 30/out)* |
| ✅ | Lojas Desk *(+ detalhe)* |
| ✅ | Depósitos |
| ✅ | Endereços de Estoque |
| ❌ | Relatórios de Cadastros |

## 📦 Estoque — 13 de 14
| | Submódulo |
|---|---|
| ✅ | Controle de Estoques *(+ detalhe; 13/out: a página do produto ficou sem a aba "Lançamentos": o histórico é o da Movimentação de Estoque)* |
| ✅ | Movimentação de Estoque *(13/out: o histórico individual de cada produto, só para consulta. Abre com os filtros: o produto pela busca padrão do sistema e o período obrigatório, no mês atual. Depois de Buscar mostra estoque atual, reservado, disponível, custo médio e valor em estoque, e cada movimento com o saldo de antes e o de depois. Clicar no movimento abre o documento inteiro, com todos os itens, e é o que se imprime)* |
| ✅ | Necessidades de Compra *(10/out: lista viva do que comprar hoje. A conta usa só o vendável, soma o que está chegando e desconta os pedidos que vão sair; mínimo e máximo ou dias de cobertura; a ordem de compra nasce dali, uma por fornecedor)* |
| ✅ | Ordens de Compra *(+ detalhe)* |
| ✅ | Entrada de Notas *(+ detalhe)* |
| ✅ | Conferência de Entrada *(+ a tela de contagem cega; desde 12/out confere também a chegada de transferência entre estoques)* |
| ✅ | Endereçamento |
| ✅ | Reposição |
| ✅ | Transferência Entre Estoques *(+ nova transferência; a chegada é conferida na Conferência de Entrada)* |
| ✅ | Inventário |
| ✅ | Acerto de Estoque |
| ✅ | Tratamento de Perdas *(chamava-se Itens Bloqueados até 12/out, quando o usuário trocou o nome; o arquivo segue `pagina-estoque-itens-bloqueados.html`. 09/out: a fila do saldo que está no estoque e não pode ser vendido. Avaria, falta a auditar, item em análise e produto travado por decisão; cada linha sai liberada para venda ou baixada como perda)* |
| ✅ | Giro de Estoque *(10/out: giro e DSI por produto no período, em três faixas com régua de dois pinos: encalhe, baixo giro e giro normal. A classificação é a que Necessidades de Compra usa para segurar a compra do que não vende)* |
| ❌ | Relatórios de Estoque |

> **Movimentação de Estoque nasceu em 13/out**, de quatro prints de um kardex e da descrição do usuário: histórico individual do produto, do saldo de antes ao saldo de hoje, com o pedido inteiro ao clicar, e sem poder de gerar ou mudar movimento. A tela não tem dado próprio de compra e venda: lê o mesmo bloco de dados do Giro de Estoque e de Necessidades de Compra, e por isso fecha no saldo do Controle de Estoques e nas vendas do Giro. Ficou de fora: lote, multiplicador de embalagem, o botão de nota fiscal com os valores de ICMS, e o link do documento para a tela de origem, que espera o alinhamento dos exemplos. Ver §14.63.
>
> **Necessidades de Compra e Giro de Estoque nasceram em 10/out**, de 31 prints do Olist e quatro decisões do usuário: **lista viva**, no padrão do sistema, sem botão "gerar"; **só o vendável conta como estoque** na compra (disponível mais o que aguarda endereço), e o aviso de mínimo do Controle de Estoques passou a usar a mesma regra; **o painel cria a ordem**, uma por fornecedor, e ela aparece em Ordens de Compra; e **o giro avisa na compra**: encalhe abaixo do mínimo entra sem quantidade sugerida. Nasceram junto o **fornecedor padrão** no cadastro do produto e a seção **Compra e giro de estoque** em Parâmetros de estoque (quatro parâmetros). Ficou de fora: tags (§12.1), natureza de operação (fiscal), prazo de entrega do fornecedor e a página de detalhe da ordem criada, que ainda abre o exemplo fixo. O kit entra na compra como produto comum, porque a composição de kit ainda não existe. Ver §14.52.
>
> **Tratamento de Perdas nasceu em 09/out**, de uma pergunta do usuário diante do "1 bloqueado" na página de um produto: onde eu resolvo isso? Não havia onde. O saldo bloqueado só saía pelo Acerto de Estoque, escolhendo a linha "Bloqueado" como origem; não existia caminho de volta para o disponível, nem tela que bloqueasse. E a falta da Separação e da Conferência de Saída virava uma "divergência aguardando reconferência" que nenhuma tela fechava. Duas decisões do usuário: **a falta bloqueia a unidade sozinha** (revê a regra de 05/out, que não mexia no saldo; continua não sendo baixa) e **o que não é avaria fica no próprio endereço, só travado**. O bloqueio manual é um tipo novo de lançamento na página do produto, em Controle de Estoques. Ver §14.51.

## 🛒 Vendas — 4 de 8
| | Submódulo |
|---|---|
| ✅ | CRM *(+ tela do assunto; 09/out: funil de pré-venda com assuntos, estágios, ações com data na Agenda, linha do tempo, quadro por estágio, proposta e encerramento como ganho ou perdido)* |
| ✅ | Pedidos de Venda *(+ página do pedido; 14/out: as vendas afiliadas, por link de indicação ou por vendedor, são o filtro de origem daqui. O item Vendas Afiliados saiu do menu em 15/out, porque abria esta mesma tela)* |
| ✅ | PDV *(09/out: turno de caixa por loja, venda com várias formas de recebimento, sangria, reforço e fechamento cego; a venda vira Pedido de Venda já entregue)* |
| ❌ | Notas Fiscais |
| ✅ | Metas e Performance *(12/out: uma página só. A lista junta meta, realizado, atingimento, ritmo, vendas com ticket médio e devolução; o painel lateral traz a meta, como vendeu, a comparação com o mês e o ano anteriores e o botão de definir ou editar a meta. A tela de Performance de Vendas deixou de existir)* |
| ❌ | Margem de Contribuição |
| ✅ | Custos do E-commerce *(as 3 entregas: **entrega 1, 22/out**: relatório vivo do lucro de cada pedido online, canal Loja virtual: venda, diferencial de frete, taxa do gateway, comissão, embalagem e custo, o lucro e a margem; cards, a barra de divisão do faturamento, agrupar por loja, vendedor ou forma de pagamento, painel do pedido e Configurar. **Entrega 2, 27/out (ajustes de 28/out, aprovada em 29/out)**: itens e estado de destino nos pedidos, a devolução na conta e na comissão, o vale de cortesia, agrupar e filtrar por produto, categoria e estado, pesquisa única. **Entrega 3, 30/out**: o campo Loja em Contas a Pagar e os anúncios (categoria 14) em Custos, com o lucro depois dos anúncios; oito cards, com "Abaixo da margem" no lugar de "No prejuízo" (a margem mínima vem de Parâmetros de vendas); o gráfico "Mês a mês" em abas no card da barra (os 5 meses anteriores são exemplo); e o módulo na lista de módulos do perfil do vendedor. Na mesma entrega nasceu a tela Parâmetros de vendas, em Configurações. **Entrega 4, 30/out**: a embalagem do pedido nasce na Separação, é confirmada na Conferência de Saída e entra na conta com os nomes e o custo do dia; o pedido ainda não confirmado mostra uma estimativa pelo cadastro de Embalagens, marcada "estimada")* |
| ❌ | Relatórios de Vendas |

> ~~**Metas** existe e funciona, mas **não tem item no menu**.~~ **Resolvido em 08/out:** o item existia em **6 telas** e faltava em **64** — quem estivesse em qualquer outra não chegava lá pelo menu. Agora são 70 de 70.
>
> **Metas e Performance refeitas em 08/out.** Metas virou listagem com painel lateral (loja e vendedor, realizado dos pedidos faturados, ritmo por dias corridos). Performance lê o **mesmo bloco de dados** e a suíte `teste_metas.py` compara os dois. Pendências: **Desk Flash não está no cadastro de Lojas Desk**, então Metas mostra 3 lojas; e o detalhe de Lojas Desk e o Dashboard de KPIs ainda têm números de meta próprios. Ver §14.42.

>
> **PDV construído em 09/out**, a partir de 34 prints do Olist e três decisões do usuário: a venda vira **Pedido de Venda já entregue** (não é lista à parte, por isso conta em Metas e Performance); a **loja é escolhida ao abrir o caixa** e decide produtos, depósito e vendedores; e o **ciclo entrou inteiro**. Os nove parâmetros nasceram no mesmo dia em Configurações do PDV. **Ficou de fora:** salvar a venda para depois, faturar pré-venda, vale-presente, lista de preços, item não cadastrado, enviar recibo por e-mail ou WhatsApp e NFC-e. **E a venda ainda não aparece nas outras telas** (Pedidos, Contas a Receber, Caixa, Metas): cada uma tem os seus dados de exemplo, e o PDV diz na conclusão o que gerou. Ver §14.48.
>
> A tabela acima passou a listar **Metas**, que tem item de menu desde 08/out e não estava nela.
>
> **CRM construído em 09/out**, a partir de 13 prints do Olist e quatro decisões do usuário: o **status do contato** (lead, prospect, cliente) mora em **Cadastros → Clientes** e o CRM lê e altera dali; **encerrar pergunta ganho ou perdido**, com motivo quando perde; a **próxima ação com data vira aviso na Agenda** do Início; e entram o **quadro por estágio**, WhatsApp e e-mail (abrem o aplicativo e registram o contato, o sistema não envia nada) e a **proposta** como registro do assunto. Nasceram junto, em Configurações, **Estágios do funil de vendas** (a ordem é o dado; o último encerra) e **Configurações do CRM** (dias para avisar assunto sem interação). Ficou de fora: marcadores, o módulo de Propostas comerciais com itens, o calendário "por período" e cadastro de motivos de perda (hoje é lista fechada).

> **Primeira leva de melhorias em 10/out**, depois de uma varredura das 80 telas prontas, que o usuário pediu e aprovou inteira. O que mudou de padrão: **o link entre telas cai numa lista já filtrada** (`?busca=` no endereço, em 30 listas), **imprimir e baixar planilha funcionam de verdade em 20 listas**, o menu ficou só com o que funciona, e os painéis de Ordens de Compra, Clientes, Pedidos de Venda e das filas de Logística passaram a levar às telas vizinhas. A lista, com o que entrou e o que falta, está em `docs/melhorias-modulos-prontos.md`. Ver §14.53.

> **Retorno do usuário em 12/out**, depois de testar a primeira leva: "incluir" abre em branco (ordem de compra e os cinco cadastros); listas numeradas abrem do nº 1; o filtro de período fecha quando outro filtro abre, nas doze telas que o têm; Necessidades de Compra abre em "A comprar" e digitar a quantidade marca o produto; concluir a separação volta para a fila e "devolver para a fila" funciona; a Conferência de Saída não leva de volta à Separação, e o Pedido de Venda mostra a etapa em que o pedido está; pedido cancelado não deve em Contas a Receber; no Dashboard, os botões 5/10/15/20 mostram mais itens e clicar na loja filtra o painel inteiro; e Boas-vindas ganhou o quadro "Pendências do Dia" com a quantidade de cada fila. Ver §14.54 e §14.55.

## 🚚 Logística — 5 de 6
| | Submódulo |
|---|---|
| ✅ | Separação *(+ ficha do pedido e folha de impressão; desde 30/out a ficha escolhe as embalagens do pedido, sem mostrar custo)* |
| ✅ | Conferência de Saída *(+ bancada, volumes e etiquetas; era "Etiquetagem"; desde 30/out recebe a embalagem da Separação, mostra os insumos e confirma, com a troca registrada)* |
| ✅ | Expedição *(+ o romaneio, com conferência de volumes e impressão em duas vias)* |
| ✅ | Rastreamento de Pedidos *(o que acontece depois da doca: situação, pagamento, códigos por volume, previsão congelada e o histórico que a vitrine consome; **+ detalhe do pedido**, a única tela que escreve código — a listagem só lê)* |
| ✅ | Devolução *(+ detalhe; documento próprio que aponta para o pedido, estado por item, estoque lançado à mão e código da reversa próprio)* |
| ❌ | Relatórios de Logística |

## 💰 Finanças — 4 de 5
| | Submódulo |
|---|---|
| ✅ | Contas a Receber *(+ página da conta)* |
| ✅ | Contas a Pagar *(+ página da conta)* |
| ✅ | Caixa e Bancos *(+ lançamento)* |
| ✅ | Comissões Afiliados *(+ conta do afiliado; 14/out: uma linha por vendedor ou cliente afiliado, com vendido, comissão do mês, lucro, a liberar e saldo; inscrições da vitrine aprovadas aqui; percentual por loja em Configurações; a conta nas linhas do Olist; 15/out: realizar pagamento faz nascer a conta em Contas a Pagar, o histórico de todos os meses, o saque pedido na vitrine, o pago vindo da baixa e a aba Afiliado no cadastro do cliente, com o histórico; a conta do afiliado filtra por data inicial e final, e o histórico, por mês e ano)* |
| ✅ | Vale-compra *(+ página do vale; **fora da contagem de 55 itens**, por isso o módulo continua em 4 de 5. 19/out, entrega 1: o vale é saldo do cliente, sem código, e só vale na loja que o emitiu; a lista traz o saldo em vales, os que vencem em 30 dias e os vencidos, com busca, loja, origem e abas por situação; o vale nasce à mão, como cortesia, com motivo e senha; a página do vale mostra os usos e o histórico, e cancela (só com saldo) e reativa (só vencido), os dois com senha; a validade é de Configurações → Cadastro de clientes, 180 dias de fábrica, e o cadastro do cliente ganhou a aba Vale-compra. Usar o vale no PDV e no Pedido de Venda, e nascer da Devolução e da Comissão, são as entregas 2 e 3)* |
| ❌ | Relatórios Finanças |

## 🔧 Operacional — módulo apagado em 08/out/2026

> Por decisão do usuário: o que havia aqui é configuração da operação, que se faz uma vez. **Transportadoras, Motivos de Devolução e Motivos de Perda** foram para Configurações e abrem pelo hub, na aba Operacional. **Formas de Pagamento** nasce em Configurações → Finanças. **Cupons** fica para quando as vitrines forem construídas. **Relatórios Operacional** deixou de existir como entrada.

## 🔌 Integrações — 1 de 4
*Os atalhos para Lojas Desk, Depósitos e Endereços de Estoque saíram deste menu em 10/out: os três continuam em Cadastros.*

| | Submódulo |
|---|---|
| ❌ | Marketplaces e Hubs |
| ✅ | Gateways de Pagamento *(20/out, entrega 1: a lista e a página do gateway; InfinitePay e Outro; cada gateway diz as lojas em que vale, guarda as condições comerciais dos cartões e cria a sua conta financeira. A entrega 2 liga Formas de Recebimento e o PDV a ele)* |
| ❌ | Emissão de Notas Fiscais |
| ❌ | Relatórios de Integrações |

## ⚙️ Configurações — 20 telas, abertas pelo hub
| | Submódulo |
|---|---|
| ✅ | Hub de Configurações |
| ✅ | Parâmetros de estoque · Parâmetros de logística *(nasceu em 13/out, da divisão da tela de estoque)* · Parâmetros de vendas *(nasceu em 30/out: o imposto padrão e a margem mínima)* · Interface do usuário · Confirmações por senha · Registro de atividades |
| ✅ | Configurações da conferência · do cadastro de produtos · do cadastro de clientes |
| ✅ | Contas financeiras · Contas bancárias · Categorias financeiras |
| ✅ | Nomes do sistema |
| ✅ | Transportadoras · Motivos de Devolução *(de quem é a conta e qual o destino sugerido no estoque)* · Motivos de Perda *(em que movimento vale e o que a baixa obriga)* — vieram de Operacional em 08/out |
| ✅ | Formas de recebimento *(08/out: para que a forma vale, se vira título ou entra direto na conta, taxa e limite de crédito; o Pedido, Contas a Receber e Contas a Pagar leem daqui. 09/out: forma com prazo fixo da operadora, que é o cartão, guarda em quantos dias úteis cai, até quantas parcelas aceita, a taxa de cada parcela e se a taxa é repassada ao cliente)* |
| ✅ | Configurações do PDV *(09/out: o que a venda de balcão exige, em que situação ela entra em Pedidos, desconto máximo sem liberação e fechamento cego; desligar o fechamento cego pede senha)* |
| ✅ | Estágios do funil de vendas · Configurações do CRM *(09/out: os estágios em ordem, com reordenação por seta e por arrastar, e em quantos dias um assunto parado passa a ser avisado)* |
| ❌ | Formas de pagamento *(a lista fiscal da NF-e: só habilita, desabilita e elege a padrão; cartão reservado no hub)* |

> ~~**Dívida conhecida (06/out):** os seis parâmetros da Expedição — `expedicaoAlertaHoras`, `expedicaoCriticoHoras`, `romaneioSugereAutomatico`, `expedicaoDesvioPesoPct`, `mdfeRegraUF` e `mdfeRegraPadrao` — **existem no código e não aparecem em tela nenhuma** de Configurações.~~
>
> **PAGA — conferido em 06/out/2026, no código, não de memória.** Os seis estão em tela: `expedicaoAlertaHoras`, `expedicaoCriticoHoras` e `expedicaoDesvioPesoPct` como campos rotulados na seção **"Expedição e romaneio"** de `pagina-configuracoes-parametros-estoque.html`; `romaneioSugereAutomatico` em `pagina-configuracoes-conferencia.html`; e `mdfeRegraUF` + `mdfeRegraPadrao` no **editor de mapa por UF** da mesma tela de parâmetros (`MDFE_MAPA`), com o aviso de que a Expedição alerta mas não emite. Todos gravam de volta no `PARAM`.

---

## Resumo

| Módulo | Feito | Falta |
|---|---|---|
| Início | 4 | 0 |
| Cadastros | 12 | 1 |
| Estoque | 13 | 1 |
| Vendas | 5 | 3 |
| **Logística** | **5** | **1** |
| Finanças | 4 | 1 |
| Integrações | 1 | 3 |
| Configurações | 1 item de menu, 20 telas | 0 |
| **Total** | **45 itens de menu com tela · 90 telas** | **10** |

*Contado no menu em 30/out/2026: **55 itens, 45 com destino e 10 sem**, em 90 telas: Parâmetros de vendas nasceu em Configurações, sem mudar o menu. Em 22/out/2026: **55 itens, 45 com destino e 10 sem**, em 89 telas: Custos do E-commerce ganhou a tela. Em 20/out/2026: **55 itens, 44 com destino e 11 sem**, em 88 telas: Gateways de Pagamento ganhou a lista e a página. Em 19/out/2026: **55 itens, 43 com destino e 12 sem**, em 86 telas. O item Vale-compra, de Finanças, não entra na conta (é o submódulo extra de 14/out, fora dos 55); as duas telas novas são a lista e a página do vale. Em 15/out/2026: **55 itens, 43 com destino e 12 sem**, em 84 telas: Vendas Afiliados saiu do menu (abria a mesma tela de Pedidos de Venda), e Comissões Afiliados nasceu, com a conta do afiliado. Em 13/out/2026 eram **56 itens, 42 com destino e 14 sem**, em 82 telas: a Movimentação de Estoque entrou no menu, e Parâmetros de logística nasceu em Configurações, sem mudar o menu. Em 12/out eram 55 itens, 41 com destino, em 80 telas (tinham sido 81: Performance de Vendas virou parte de Metas e Performance). Na primeira leva de melhorias nenhuma tela tinha saído: o menu perdeu os três atalhos de cadastro que se repetiam em Integrações, e Metas e Performance de Vendas viraram um item só. Antes da leva, já com Necessidades de Compra e Giro de Estoque, eram 59 itens, 45 com destino e 14 sem. Em 09/out, com o CRM e Tratamento de Perdas, eram 43 e 16. O "41 entradas" que estava aqui antes do PDV somava de outro jeito; pelo menu eram 40.*

**Fases:** F2 (Cadastros) e F5 (Estoque + Financeiro) fechadas. **F4 — Logística fechada em 07/out**: Separação, Conferência de Saída, Expedição, Rastreamento de Pedidos e Devolução, mais o cadastro de **Motivos de Devolução** em Operacional. Falta só **Relatórios de Logística**, que entra com os relatórios dos outros módulos.
