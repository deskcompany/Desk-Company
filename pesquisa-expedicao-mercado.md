# Expedição — como o mercado resolve, e o que vamos usar

*Pesquisa de 06/out/2026, feita antes de desenhar a tela. Fontes no fim. Onde a fonte não existia ou estava bloqueada, está escrito "não encontrado" — nada aqui foi preenchido por suposição.*

Sistemas lidos: **Bling, Omie, TOTVS Protheus (SIGAACD, fonte secundária), Sankhya, Senior (WMS e Gestão de Fretes), CIGAM, Magis5, Expedy** · **Odoo, SAP EWM/S4, Microsoft Dynamics 365 SCM, Oracle NetSuite** · **ShipStation, Melhor Envio, Intelipost, Shippo** · legislação: **MDF-e, CT-e, DC-e, canhoto, romaneio**.

---

## 1. O modelo de camadas dos ERPs globais

Dynamics 365, SAP EWM, Odoo e NetSuite convergem em **sete camadas**, e a razão de cada uma existir é a cardinalidade — um pedido pode virar 3 volumes em 2 cargas; uma onda cobre 200 pedidos:

| camada | o que é | por que existe |
|---|---|---|
| Pedido / documento de saída | a obrigação comercial | é o que o cliente e o fiscal enxergam |
| **Onda (wave)** | lote de trabalho | a rota eficiente no armazém nunca coincide com a fronteira do pedido |
| **Trabalho (work/task)** | a instrução física (pegue X em Y) | para ser confirmada por leitura e gerar rastro |
| **Volume (handling unit / container / carton)** | o pacote real, com peso, dimensão e código único (SSCC / license plate) | transportadora, etiqueta, conferência e seguro operam por volume, não por item |
| **Remessa (shipment)** | o que vai junto para um destino | consolida vários pedidos do mesmo cliente/rota |
| **Carga (load) + doca + veículo** | o caminhão | o gargalo final é físico: peso, volume, porta |
| **Baixa fiscal (goods issue / packing slip)** | o lançamento | separado de propósito do "confirmou saída" |

**O achado mais importante é o último.** D365 confirma a remessa (`load → Shipped`) e **não baixa estoque**: a dedução vem depois, no *load packing slip posting*. A documentação de troubleshooting é explícita: confirmar remessa não posta packing slip nem deduz estoque. **Eles separam para que erro de doca não vire lançamento contábil errado.**

SAP é mais rígido: *goods issue* é tudo ou nada — "it is not possible to post a partial goods issue"; carga parcial exige *delivery split*. Odoo só tira do estoque da empresa na validação do último transfer (`WH/Output → Customers`).

---

## 2. O padrão dos ERPs brasileiros

**O agrupamento se forma a partir da NOTA FISCAL, não do pedido.** Senior ("Formar Romaneio por NF"), Magis5, Expedy (lista criada após a emissão), Omie (exige NF autorizada), Bling (aceita pedidos *ou* NFs). **O faturamento antecede a montagem da carga** em todos eles.

**Hierarquia de três níveis:** Pedido/NF → Lista de Separação (onda) → Romaneio/Carga. CIGAM explicita ("um Romaneio pode compreender várias listas"); Senior, Sankhya (onda → Ordem de Carga → doca) e Protheus repetem.

**Máquina de estados com um estado de conferência no meio, e "divergência" como estado de primeira classe** — não como erro. Sankhya: *Enviado para Separação → Aguardando Conferência → Conferência validada → Concluído*. Protheus por cor: azul não iniciado, amarelo em andamento, **vermelho divergência**, verde finalizado. Senior: separado → conferido → **pesado** → faturado.

**Conferência com código de barras é padrão — e no Brasil ela é por ITEM.** Sankhya diz com todas as letras que a Fila de Conferência *não* funciona com conferência de volumes. Bling bipa cada item separado e embalado. Conferência **por volume** (SSCC, license plate) é padrão **global**, não brasileiro.

**Peso e volume são bloqueantes.** Omie exige volume preenchido e cotação antes de gerar documento; Senior tem "pesado" como etapa do acompanhamento.

**O despacho tem gate manual explícito.** Sankhya: "liberação manual da doca". CIGAM: "Liberar p/ Faturar". Nada vira "enviado" sozinho.

**Um romaneio não mistura formas de envio.** Magis5 é o mais explícito: todas as vendas selecionadas precisam ter o mesmo tipo de entrega. Bling agrupa por serviço logístico; Omie por operadora.

**Cancelar depois de separado exige movimento físico reverso.** Sankhya tem "Endereço de Estorno" e tarefa de retorno no coletor.

**Lacuna real das fontes:** nenhum dos sistemas brasileiros documenta publicamente **em que momento o estoque baixa**, e nenhum documenta **frota própria** ou **retirada no balcão** como fluxo distinto.

---

## 3. Plataformas de envio — o que elas fazem que o ERP não faz

Fluxo comum: separar → conferir → **pesar e cubar** → **cotar** → gerar etiqueta + documento → imprimir → agrupar em manifesto/PLP → entregar ao transportador.

**Rate shopping acontece duas vezes:** estimativa no checkout e **recotação no empacotamento, com a caixa e o peso reais**. É a segunda que fecha o custo — e é ela que pode divergir do que o cliente pagou. Essa diferença é um custo que normalmente ninguém vê.

**PLP (Pré-Lista de Postagem):** agrupa objetos num lote com os rastreios já gerados. Na prática o operador leva **duas vias**; o atendente confere, carimba e devolve uma — **essa via é o comprovante de postagem**, base para reclamar extravio.

**Rastreio é por VOLUME, não por pedido.** Uma etiqueta e um código por volume, agrupados sob o pedido. Modelagem: `Pedido → Envio → Volume[]`, com o status do pedido sendo a agregação dos volumes.

**Divisão de trabalho:** a plataforma faz tarifa negociada, etiqueta homologada, PLP, tracking unificado e auditoria de frete. O ERP faz NF-e, estoque, financeiro e pedido. Nenhum dos dois faz o do outro.

*(A Kangu encerrou operações em 23/02/2025 — não serve mais de referência.)*

---

## 4. O que a lei realmente exige

| tema | regra | confiança |
|---|---|---|
| **DC-e** | Desde **06/04/2026** só vale a declaração de conteúdo **eletrônica** (modelo 99, Ajuste SINIEF 05/21). O transportador **não aceita envio sem chave de NF-e ou DC-e**. A DC-e **não desobriga** a NF-e: ela só substitui nota para remetente **não contribuinte**. | alta |
| **MDF-e intramunicipal** | Entrega na mesma cidade com veículo próprio/motoboy **não exige** MDF-e. | alta |
| **MDF-e interestadual** | SP (Portaria CAT 102/2013, red. SRE-28/24) obriga o emitente de NF-e que transporta em veículo próprio no **interestadual com mais de uma NF-e**. **RS exige até com uma nota só, e também no intermunicipal.** MG: intermunicipal desde 2015. | alta p/ SP, média p/ o resto |
| **CT-e** | Emitido pelo **prestador** do transporte. Varejista com frota própria faz carga própria e **não emite**. Só se preocupa como tomador. | alta |
| **Canhoto** | Desde **01/12/2021** o evento **"Comprovante de Entrega da NF-e"** (Ajuste SINIEF 38/2021) substitui o canhoto em papel. Guarda: **5 anos**. Digitalização permitida. | alta |
| **Romaneio** | **Controle interno**, não documento fiscal — exceto quando substitui a discriminação das mercadorias na nota, o que é raro com NF-e. | alta |

**A conclusão operacional:** o único bloqueio fiscal **duro** no despacho é **documento fiscal válido**. MDF-e tem de ser **regra configurável por UF e tipo de operação**, nunca trava fixa. CT-e e romaneio não bloqueiam nada.

---

## 5. O que isso muda (e o que confirma) no Desk Company

**Confirma três decisões nossas:**

1. **A nota sair na Conferência de Saída** nos coloca no padrão brasileiro — o agrupamento se forma sobre notas, e os pedidos chegam à Expedição já faturados.
2. **Divergência como estado de primeira classe** é o que todos fazem.
3. **O gate manual** antes de "enviado" é unânime.

**Muda uma:** a conferência de **volume** na carga é padrão **global** (SSCC / license plate), não brasileiro — os ERPs nacionais conferem item e param aí. Nossa escolha de 05/out segue D365 e SAP, e é defensável: é ela que pega o pacote que subiu no caminhão errado.

**Abre uma questão que não tínhamos:** D365 e SAP **separam** "confirmou a saída" de "baixou o estoque". No caso deles isso existe porque a baixa carrega o lançamento fiscal. **No nosso caso a nota já saiu na etapa anterior** — a baixa aqui é puramente física. Por isso os dois eventos podem ser um só, e o pedido que volta da doca **não precisa de estorno nenhum**, porque nada foi baixado ainda. É uma vantagem do nosso desenho, não uma simplificação.

**Traz duas regras novas:**

- **Um romaneio = uma forma de envio.** Não mistura Correios com transportadora.
- **Peso bruto é bloqueante** para fechar o romaneio.

**E expõe uma lacuna:** não existe cadastro de **Transportadoras**. Hoje a forma de envio é texto no mock.

---

## Fontes

**ERPs BR:** [Bling · romaneio](https://ajuda.bling.com.br/hc/pt-br/articles/360039266373) · [Bling · separação](https://www.bling.com.br/funcionalidades/separacao-pedidos) · [Omie · painel de frete](https://ajuda.omie.com.br/pt-BR/articles/9279485-acessando-o-painel-de-frete) · [Sankhya · expedição](https://ajuda.sankhya.com.br/hc/pt-br/articles/360044611474) · [Sankhya · fila de conferência](https://ajuda.sankhya.com.br/hc/pt-br/articles/360055358513) · [Senior WMS · romaneio](https://documentacao.senior.com.br/gestaodearmazenagemwms/8.12/manuais-wms/complementares/gestao-armazenagem-front-end/expedicao-romaneio-com-cobertura-fiscal.html) · [Senior · fretes](https://documentacao.senior.com.br/gestaodefretesfis/7.0.0/processo/romaneio.htm) · [CIGAM](https://www.cigam.com.br/wiki/index.php/EX_-_Como_Fazer_-_Lista_de_Separação_e_Romaneio) · [Magis5](https://ajuda.magis5.com.br/magis5-erp-como-gerar-um-romaneio-de-entrega) · [Expedy](https://ajuda.expedy.com.br/comece-a-usar/como-realizar-a-expedicao-na-expedy/) · [Protheus ACDA100 (secundária)](https://dothink.com.br/ordem-separacao-sigaacd-acda100-totvs-protheus-202506.html)

**ERPs globais:** [D365 · outbound load handling](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/outbound-load-handling) · [D365 · wave templates](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/wave-templates) · [D365 · packing containers](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/packing-containers) · [D365 · confirm and transfer](https://learn.microsoft.com/en-us/dynamics365/supply-chain/warehousing/confirm-and-transfer) · [D365 · shipment confirmed, no posting](https://learn.microsoft.com/en-us/troubleshoot/dynamics-365/supply-chain/warehousing/shipment-confirmed-no-posting) · [SAP · wave management](https://learning.sap.com/courses/processes-in-sap-s-4hana-ewm/applying-wave-management) · [SAP · posting a goods issue](https://learning.sap.com/courses/configuring-delivery-processing-in-sap-s-4hana-sales/posting-a-goods-issue) · [SAP · handling units](https://learning.sap.com/courses/implementing-sap-s-4hana-cloud-public-edition-warehouse-management/maintaining-handling-units-hu-_dcf41902-7052-4c3c-bbc0-2bab1a918e69) · [Odoo · wave picking](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping_receiving/picking_methods/wave.html) · [Odoo · dispatch](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory/shipping_receiving/setup_configuration/dispatch.html) · [NetSuite · wave](https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_1548078883.html) · [GS1 · SSCC](https://www.gs1.org/standards/id-keys/sscc)

**Envio:** [ShipStation · scan to verify](https://help.shipstation.com/hc/en-us/articles/360031021831) · [ShipStation · rate shopping](https://www.shipstation.com/guides/rate-shopping-in-action/) · [Melhor Envio · gerar envio](https://centraldeajuda.melhorenvio.com.br/hc/pt-br/articles/31220440109844) · [Intelipost · PLP](https://www.intelipost.com.br/blog/entenda-o-que-e-plp-pre-lista-de-postagem-e-quais-seus-beneficios/) · [Olist · multi-volumes](https://ajuda.olist.com/sobre-o-servico/saiba-como-funciona-o-multi-volumes-na-envios-da-olist)

**Legislação:** [SEFAZ-SP · Portaria CAT 102/2013](https://legislacao.fazenda.sp.gov.br/Paginas/pcat1022013.aspx) · [SEFAZ-RS · MDF-e carga própria](https://atendimento.receita.rs.gov.br/e-obrigatorio-emitir-o-mdf-e-em-operacoes-com-carga-propria) · [SEF/MG · obrigatoriedade MDF-e](https://portalsped.fazenda.mg.gov.br/spedmg/mdfe/Obrigatoriedade/) · [SPED/PR · manual DC-e](https://sped.fazenda.pr.gov.br/sites/sped/arquivos_restritos/files/documento/2024-05/Manual%20DC-e%20%E2%80%93%20Vis%C3%A3o%20Geral.pdf) · [SEFAZ-SC · canhoto e comprovante de entrega (COPAT 025/24)](https://legislacao.sef.sc.gov.br/Consulta/Views/Publico/DocumentoLegalViewer.ashx?id=0099BE0B-18F8-4B5B-9034-90A702D74243) · [RICMS/SC · romaneio](https://legislacao.sef.sc.gov.br/html/regulamentos/icms/ricms_01_05.htm)

**Não foi possível ler:** TDN da TOTVS (402/403), help.sap.com (robots), CONFAZ (Ajuste SINIEF 21/10), Manhattan e Blue Yonder (portal fechado). O que veio dessas fontes está marcado como secundário no texto.
