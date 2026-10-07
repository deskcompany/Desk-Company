# Mapa dos módulos — ERP Desk Company
*Gerado em 02/out/2026, atualizado em 05/out com a Separação e a Conferência de Saída e em 06/out com a Expedição e o cadastro de Transportadoras. Lido do próprio menu do sistema (não de uma lista escrita à mão).*

**63 telas construídas** · ✅ tem tela · ❌ não existe ainda

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
| ✅ | Conferência de Compra *(+ a tela de contagem cega)* |
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

> **Metas** existe e funciona, mas **não tem item no menu** — só se chega por Lojas Desk, Vendedores ou Performance. Vale colocar no menu de Vendas.

## 🚚 Logística — 3 de 6
| | Submódulo |
|---|---|
| ✅ | Separação *(+ ficha do pedido e folha de impressão)* |
| ✅ | Conferência de Saída *(+ bancada, volumes e etiquetas; era "Etiquetagem")* |
| ✅ | Expedição *(+ o romaneio, com conferência de volumes e impressão em duas vias)* |
| ❌ | Rastreamento de Pedidos |
| ❌ | Devolução |
| ❌ | Relatórios de Logística |

## 💰 Finanças — 3 de 5
| | Submódulo |
|---|---|
| ✅ | Caixa e Bancos *(+ lançamento)* |
| ✅ | Contas a Pagar *(+ página da conta)* |
| ✅ | Contas a Receber *(+ página da conta)* |
| ❌ | Comissões Afiliados |
| ❌ | Relatórios Finanças |

## 🔧 Operacional — 1 de 6
| | Submódulo |
|---|---|
| ✅ | Transportadoras |
| ❌ | Formas de Pagamento |
| ❌ | Cupons |
| ❌ | Motivos de Devolução |
| ❌ | Motivos de Perda |
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

> **Dívida conhecida (06/out):** os seis parâmetros da Expedição — `expedicaoAlertaHoras`, `expedicaoCriticoHoras`, `romaneioSugereAutomatico`, `expedicaoDesvioPesoPct`, `mdfeRegraUF` e `mdfeRegraPadrao` — **existem no código e não aparecem em tela nenhuma** de Configurações. É o mesmo erro de `reservaExpiraDias`, que foi pago em 05/out. Fecha junto com a F4.

---

## Resumo

| Módulo | Feito | Falta |
|---|---|---|
| Início | 3 | 0 |
| Cadastros | 12 | 1 |
| Estoque | 9 | 3 |
| Vendas | 2 | 7 |
| **Logística** | **3** | **3** |
| Finanças | 3 | 2 |
| **Operacional** | **1** | **5** |
| Integrações | 0 | 4 |
| Configurações | 10 | 0 |
| **Total** | **43 entradas de menu · 63 telas** | **25** |

**Fases:** F2 (Cadastros) e F5 (Estoque + Financeiro) fechadas. **Em andamento: F4 — Logística**, com Separação, Conferência de Saída e Expedição prontas; faltam Rastreamento de Pedidos e Devolução.
