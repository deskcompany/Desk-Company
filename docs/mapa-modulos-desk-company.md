# Mapa dos módulos — ERP Desk Company
*Gerado em 02/out/2026, atualizado em 05/out com a Separação e a Conferência de Saída e em 06/out com a Expedição e o cadastro de Transportadoras. Lido do próprio menu do sistema (não de uma lista escrita à mão).*

**65 telas construídas** · ✅ tem tela · ❌ não existe ainda

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

## 🛒 Vendas — 2 de 9
| | Submódulo |
|---|---|
| ✅ | Pedidos de Venda *(+ página do pedido)* |
| ✅ | Performance de Vendas |
| ❌ | CRM |
| ❌ | PDV |
| ❌ | Notas Fiscais |
| ❌ | Vendas Afiliados |
| ❌ | Margem de Contribuição |
| ❌ | Custos do E-commerce |
| ❌ | Relatórios de Vendas |

> ~~**Metas** existe e funciona, mas **não tem item no menu**.~~ **Resolvido em 08/out:** o item existia em **6 telas** e faltava em **64** — quem estivesse em qualquer outra não chegava lá pelo menu. Agora são 70 de 70.
>
> **Metas e Performance refeitas em 08/out.** Metas virou listagem com painel lateral (loja e vendedor, realizado dos pedidos faturados, ritmo por dias corridos). Performance lê o **mesmo bloco de dados** e a suíte `teste_metas.py` compara os dois. Pendências: **Desk Flash não está no cadastro de Lojas Desk**, então Metas mostra 3 lojas; e o detalhe de Lojas Desk e o Dashboard de KPIs ainda têm números de meta próprios. Ver §14.42.

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

## 🔧 Operacional — 3 de 6
| | Submódulo |
|---|---|
| ✅ | Transportadoras |
| ❌ | Formas de Pagamento |
| ❌ | Cupons |
| ✅ | Motivos de Devolução *(de quem é a conta e qual o destino sugerido no estoque; nasceu antes da Devolução usá-lo)* |
| ✅ | Motivos de Perda *(em que movimento o motivo vale e o que a baixa obriga; os motivos vieram do código do Acerto, onde viviam sem dono)* |
| ❌ | Relatórios Operacional |

## 🔌 Integrações — 0 de 4 próprias
*Lojas Desk, Depósitos e Endereços de Estoque aqui são atalhos para Cadastros, não telas próprias.*

| | Submódulo |
|---|---|
| ❌ | Marketplaces e Hubs |
| ❌ | Emissão de Notas Fiscais |
| ❌ | Gateways de Pagamento |
| ❌ | Relatórios de Integrações |

## ⚙️ Configurações — 10 de 10
| | Submódulo |
|---|---|
| ✅ | Hub de Configurações |
| ✅ | Parâmetros de estoque · Interface do usuário · Confirmações por senha · Registro de atividades |
| ✅ | Configurações da conferência · do cadastro de produtos · do cadastro de clientes |
| ✅ | Contas financeiras · Contas bancárias · Categorias financeiras |

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
| Vendas | 2 | 7 |
| **Logística** | **5** | **1** |
| Finanças | 3 | 2 |
| **Operacional** | **3** | **3** |
| Integrações | 0 | 4 |
| Configurações | 10 | 0 |
| **Total** | **47 entradas de menu · 71 telas** | **21** |

**Fases:** F2 (Cadastros) e F5 (Estoque + Financeiro) fechadas. **F4 — Logística fechada em 07/out**: Separação, Conferência de Saída, Expedição, Rastreamento de Pedidos e Devolução, mais o cadastro de **Motivos de Devolução** em Operacional. Falta só **Relatórios de Logística**, que entra com os relatórios dos outros módulos.
