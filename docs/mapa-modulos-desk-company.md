# Mapa dos módulos — ERP Desk Company
*Gerado em 02/out/2026, atualizado em 05/out com a Separação e a Conferência de Saída, em 06/out com a Expedição e o cadastro de Transportadoras em 09/out com o PDV, o CRM e Tratamento de Perdas e em 10/out com Necessidades de Compra e Giro de Estoque e com a primeira leva de melhorias dos módulos prontos, em 12/out com o retorno do usuário sobre ela, e em 13/out com a Movimentação de Estoque. Lido do próprio menu do sistema (não de uma lista escrita à mão).*

**81 telas construídas** · ✅ tem tela · ❌ não existe ainda

> **Onde estão os arquivos (desde 08/out/2026):** cada tela mora em `telas/<módulo>/`, na pasta do módulo em que este mapa a lista. O dashboard de KPIs fica em `telas/inicio/`. `telas/integracoes/` existe e está vazia. Ver §14.44 do design system.

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
| ✅ | Produtos *(+ detalhe)* |
| ✅ | Vendedores *(+ detalhe)* |
| ✅ | Embalagens |
| ✅ | Lojas Desk *(+ detalhe)* |
| ✅ | Depósitos |
| ✅ | Endereços de Estoque |
| ✅ | Marcas de Produtos |
| ✅ | Departamento de Produtos |
| ✅ | Seção de Produtos |
| ✅ | Categorias |
| ❌ | Relatórios de Cadastros |

## 📦 Estoque — 13 de 14
| | Submódulo |
|---|---|
| ✅ | Controle de Estoques *(+ detalhe)* |
| ✅ | Movimentação de Estoque *(13/out: o histórico individual de cada produto, só para consulta. Abre com os filtros; depois de Buscar mostra estoque atual, reservado, disponível, custo médio e valor em estoque, e cada movimento com o saldo de antes e o de depois. Clicar no movimento abre o documento inteiro, com todos os itens, e é o que se imprime)* |
| ✅ | Entrada de Notas *(+ detalhe)* |
| ✅ | Conferência de Entrada *(+ a tela de contagem cega; desde 12/out confere também a chegada de transferência entre estoques)* |
| ✅ | Endereçamento |
| ✅ | Reposição |
| ✅ | Ordens de Compra *(+ detalhe)* |
| ✅ | Transferência Entre Estoques *(+ nova transferência; a chegada é conferida na Conferência de Entrada)* |
| ✅ | Tratamento de Perdas *(chamava-se Itens Bloqueados até 12/out, quando o usuário trocou o nome; o arquivo segue `pagina-estoque-itens-bloqueados.html`. 09/out: a fila do saldo que está no estoque e não pode ser vendido. Avaria, falta a auditar, item em análise e produto travado por decisão; cada linha sai liberada para venda ou baixada como perda)* |
| ✅ | Acerto de Estoque |
| ✅ | Inventário |
| ✅ | Necessidades de Compra *(10/out: lista viva do que comprar hoje. A conta usa só o vendável, soma o que está chegando e desconta os pedidos que vão sair; mínimo e máximo ou dias de cobertura; a ordem de compra nasce dali, uma por fornecedor)* |
| ✅ | Giro de Estoque *(10/out: giro e DSI por produto no período, em três faixas com régua de dois pinos: encalhe, baixo giro e giro normal. A classificação é a que Necessidades de Compra usa para segurar a compra do que não vende)* |
| ❌ | Relatórios de Estoque |

> **Movimentação de Estoque nasceu em 13/out**, de quatro prints de um kardex e da descrição do usuário: histórico individual do produto, do saldo de antes ao saldo de hoje, com o pedido inteiro ao clicar, e sem poder de gerar ou mudar movimento. A tela não tem dado próprio de compra e venda: lê o mesmo bloco de dados do Giro de Estoque e de Necessidades de Compra, e por isso fecha no saldo do Controle de Estoques e nas vendas do Giro. Ficou de fora: lote, multiplicador de embalagem, o botão de nota fiscal com os valores de ICMS, e o link do documento para a tela de origem, que espera o alinhamento dos exemplos. Ver §14.63.
>
> **Necessidades de Compra e Giro de Estoque nasceram em 10/out**, de 31 prints do Olist e quatro decisões do usuário: **lista viva**, no padrão do sistema, sem botão "gerar"; **só o vendável conta como estoque** na compra (disponível mais o que aguarda endereço), e o aviso de mínimo do Controle de Estoques passou a usar a mesma regra; **o painel cria a ordem**, uma por fornecedor, e ela aparece em Ordens de Compra; e **o giro avisa na compra**: encalhe abaixo do mínimo entra sem quantidade sugerida. Nasceram junto o **fornecedor padrão** no cadastro do produto e a seção **Compra e giro de estoque** em Parâmetros de estoque (quatro parâmetros). Ficou de fora: tags (§12.1), natureza de operação (fiscal), prazo de entrega do fornecedor e a página de detalhe da ordem criada, que ainda abre o exemplo fixo. O kit entra na compra como produto comum, porque a composição de kit ainda não existe. Ver §14.52.
>
> **Tratamento de Perdas nasceu em 09/out**, de uma pergunta do usuário diante do "1 bloqueado" na página de um produto: onde eu resolvo isso? Não havia onde. O saldo bloqueado só saía pelo Acerto de Estoque, escolhendo a linha "Bloqueado" como origem; não existia caminho de volta para o disponível, nem tela que bloqueasse. E a falta da Separação e da Conferência de Saída virava uma "divergência aguardando reconferência" que nenhuma tela fechava. Duas decisões do usuário: **a falta bloqueia a unidade sozinha** (revê a regra de 05/out, que não mexia no saldo; continua não sendo baixa) e **o que não é avaria fica no próprio endereço, só travado**. O bloqueio manual é um tipo novo de lançamento na página do produto, em Controle de Estoques. Ver §14.51.

## 🛒 Vendas — 4 de 9
| | Submódulo |
|---|---|
| ✅ | Pedidos de Venda *(+ página do pedido)* |
| ✅ | PDV *(09/out: turno de caixa por loja, venda com várias formas de recebimento, sangria, reforço e fechamento cego; a venda vira Pedido de Venda já entregue)* |
| ✅ | Metas e Performance *(12/out: uma página só. A lista junta meta, realizado, atingimento, ritmo, vendas com ticket médio e devolução; o painel lateral traz a meta, como vendeu, a comparação com o mês e o ano anteriores e o botão de definir ou editar a meta. A tela de Performance de Vendas deixou de existir)* |
| ✅ | CRM *(+ tela do assunto; 09/out: funil de pré-venda com assuntos, estágios, ações com data na Agenda, linha do tempo, quadro por estágio, proposta e encerramento como ganho ou perdido)* |
| ❌ | Notas Fiscais |
| ❌ | Vendas Afiliados |
| ❌ | Margem de Contribuição |
| ❌ | Custos do E-commerce |
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
| ✅ | Separação *(+ ficha do pedido e folha de impressão)* |
| ✅ | Conferência de Saída *(+ bancada, volumes e etiquetas; era "Etiquetagem")* |
| ✅ | Expedição *(+ o romaneio, com conferência de volumes e impressão em duas vias)* |
| ✅ | Rastreamento de Pedidos *(o que acontece depois da doca: situação, pagamento, códigos por volume, previsão congelada e o histórico que a vitrine consome; **+ detalhe do pedido**, a única tela que escreve código — a listagem só lê)* |
| ✅ | Devolução *(+ detalhe; documento próprio que aponta para o pedido, estado por item, estoque lançado à mão e código da reversa próprio)* |
| ❌ | Relatórios de Logística |

## 💰 Finanças — 3 de 5
| | Submódulo |
|---|---|
| ✅ | Caixa e Bancos *(+ lançamento)* |
| ✅ | Contas a Pagar *(+ página da conta)* |
| ✅ | Contas a Receber *(+ página da conta)* |
| ❌ | Comissões Afiliados |
| ❌ | Relatórios Finanças |

## 🔧 Operacional — módulo apagado em 08/out/2026

> Por decisão do usuário: o que havia aqui é configuração da operação, que se faz uma vez. **Transportadoras, Motivos de Devolução e Motivos de Perda** foram para Configurações e abrem pelo hub, na aba Operacional. **Formas de Pagamento** nasce em Configurações → Finanças. **Cupons** fica para quando as vitrines forem construídas. **Relatórios Operacional** deixou de existir como entrada.

## 🔌 Integrações — 0 de 4
*Os atalhos para Lojas Desk, Depósitos e Endereços de Estoque saíram deste menu em 10/out: os três continuam em Cadastros.*

| | Submódulo |
|---|---|
| ❌ | Marketplaces e Hubs |
| ❌ | Emissão de Notas Fiscais |
| ❌ | Gateways de Pagamento |
| ❌ | Relatórios de Integrações |

## ⚙️ Configurações — 19 telas, abertas pelo hub
| | Submódulo |
|---|---|
| ✅ | Hub de Configurações |
| ✅ | Parâmetros de estoque · Interface do usuário · Confirmações por senha · Registro de atividades |
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
| Vendas | 4 | 5 |
| **Logística** | **5** | **1** |
| Finanças | 3 | 2 |
| Integrações | 0 | 4 |
| Configurações | 1 item de menu, 19 telas | 0 |
| **Total** | **42 itens de menu com tela · 81 telas** | **14** |

*Contado no menu em 13/out/2026: **56 itens, 42 com destino e 14 sem**, em 81 telas: a Movimentação de Estoque entrou. Em 12/out eram 55 itens, 41 com destino, em 80 telas (tinham sido 81: Performance de Vendas virou parte de Metas e Performance). Na primeira leva de melhorias nenhuma tela tinha saído: o menu perdeu os três atalhos de cadastro que se repetiam em Integrações, e Metas e Performance de Vendas viraram um item só. Antes da leva, já com Necessidades de Compra e Giro de Estoque, eram 59 itens, 45 com destino e 14 sem. Em 09/out, com o CRM e Tratamento de Perdas, eram 43 e 16. O "41 entradas" que estava aqui antes do PDV somava de outro jeito; pelo menu eram 40.*

**Fases:** F2 (Cadastros) e F5 (Estoque + Financeiro) fechadas. **F4 — Logística fechada em 07/out**: Separação, Conferência de Saída, Expedição, Rastreamento de Pedidos e Devolução, mais o cadastro de **Motivos de Devolução** em Operacional. Falta só **Relatórios de Logística**, que entra com os relatórios dos outros módulos.
