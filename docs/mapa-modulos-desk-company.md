# Mapa dos módulos — ERP Desk Company
*Gerado em 02/out/2026, atualizado em 05/out com a Separação e a Conferência de Saída, em 06/out com a Expedição e o cadastro de Transportadoras e em 09/out com o PDV e o CRM. Lido do próprio menu do sistema (não de uma lista escrita à mão).*

**78 telas construídas** · ✅ tem tela · ❌ não existe ainda

> **Onde estão os arquivos (desde 08/out/2026):** cada tela mora em `telas/<módulo>/`, na pasta do módulo em que este mapa a lista. O dashboard de KPIs fica em `telas/inicio/`. `telas/integracoes/` existe e está vazia. Ver §14.44 do design system.

---

## 🏠 Início — 3 de 3
| | Submódulo |
|---|---|
| ✅ | Dashboard KPIs |
| ✅ | Agenda |
| ✅ | Minha Conta |

*Também construída: tela de boas-vindas (sem item de menu, abre pelo logo).*

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

## 📦 Estoque — 9 de 12
| | Submódulo |
|---|---|
| ✅ | Controle de Estoques *(+ detalhe)* |
| ✅ | Entrada de Notas *(+ detalhe)* |
| ✅ | Conferência de Entrada *(+ a tela de contagem cega)* |
| ✅ | Endereçamento |
| ✅ | Reposição |
| ✅ | Ordens de Compra *(+ detalhe)* |
| ✅ | Transferência Entre Estoques *(+ nova transferência)* |
| ✅ | Acerto de Estoque |
| ✅ | Inventário |
| ❌ | Necessidades de Compra |
| ❌ | Giro de Estoque |
| ❌ | Relatórios de Estoque |

## 🛒 Vendas — 5 de 10
| | Submódulo |
|---|---|
| ✅ | Pedidos de Venda *(+ página do pedido)* |
| ✅ | PDV *(09/out: turno de caixa por loja, venda com várias formas de recebimento, sangria, reforço e fechamento cego; a venda vira Pedido de Venda já entregue)* |
| ✅ | Metas |
| ✅ | Performance de Vendas |
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

## 🔌 Integrações — 0 de 4 próprias
*Lojas Desk, Depósitos e Endereços de Estoque aqui são atalhos para Cadastros, não telas próprias.*

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
| Início | 3 | 0 |
| Cadastros | 12 | 1 |
| Estoque | 9 | 3 |
| Vendas | 5 | 5 |
| **Logística** | **5** | **1** |
| Finanças | 3 | 2 |
| Integrações | 0 | 4 |
| Configurações | 19 | 0 |
| **Total** | **42 itens de menu com tela · 78 telas** | **16** |

*Contado no menu em 09/out/2026, já com o CRM: 58 itens, 42 com destino e 16 sem. O "41 entradas" que estava aqui antes do PDV somava de outro jeito; pelo menu eram 40.*

**Fases:** F2 (Cadastros) e F5 (Estoque + Financeiro) fechadas. **F4 — Logística fechada em 07/out**: Separação, Conferência de Saída, Expedição, Rastreamento de Pedidos e Devolução, mais o cadastro de **Motivos de Devolução** em Operacional. Falta só **Relatórios de Logística**, que entra com os relatórios dos outros módulos.
