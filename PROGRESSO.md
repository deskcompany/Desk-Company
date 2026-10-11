# Progresso do ERP Desk Company

*Atualizado em 10/out/2026, na primeira leva de melhorias dos módulos prontos.*

Esta página diz onde o projeto está, o que vem depois e o que está esperando decisão. Serve para
começar uma conversa nova sem reler o projeto inteiro. É **reescrita a cada entrega**, no mesmo
commit; o histórico de cada entrega fica no `git log`, e as regras do projeto no `CLAUDE.md`.

## Onde paramos

**A primeira leva de melhorias dos módulos prontos está feita e espera o teste do usuário.** Ele
aprovou a lista inteira de `docs/melhorias-modulos-prontos.md` em 10/out/2026 e pediu para fazer
por partes. Entraram 12 itens por inteiro e 15 no principal, com o resto de cada um anotado; o que
entrou e o que falta está no topo daquele documento.

Necessidades de Compra e Giro de Estoque, entregues no mesmo dia, foram testadas quase inteiras
pelo usuário, sem ajuste apontado. Falta ele terminar o teste para aprovar.

O próximo passo é dele: testar esta leva, responder às decisões abaixo (enviar ao GitHub e
hospedagem) e dizer se segue o resto da lista ou o próximo módulo.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **41 de 55 (75%)**, em 81 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 75% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda. As fases de produção
(F0 a F8) estão em `docs/arquitetura-roadmap-desk-company.md`.

O menu tinha 59 itens e passou a ter 55, sem perder tela nenhuma: saíram os três atalhos de
cadastro que se repetiam em Integrações, e Metas e Performance de Vendas viraram um item só.

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

**1. Necessidades de Compra e Giro de Estoque** (§14.52 do design system). A lista viva do que
comprar, com a conta de cada produto e a ordem de compra criada dali; e o giro por produto em três
faixas. Quatro decisões do usuário: lista viva; só o vendável conta como estoque; o painel cria a
ordem; o giro segura a compra do que não vende.

**2. A primeira leva de melhorias** (§14.53):

- **Os quatro defeitos da varredura.** A Conferência de Entrada abria a nota errada; o Pedido
  mandava o galpão para outro pedido; "Mais ações" de Clientes, Fornecedores e Produtos não fazia
  nada; cinco telas ainda citavam o Lovable.
- **Imprimir e baixar planilha de verdade em 20 listas**, com a lista inteira e os filtros da
  tela. Saíram do menu os itens que só mostravam um aviso, e o "Imprimir" repetido no topo.
- **A trilha entre as telas.** 30 listas aceitam abrir já filtradas (`?busca=` no endereço), com
  uma faixa dizendo de onde veio o filtro. Os painéis de Ordens de Compra, Entrada de Notas,
  Conferência de Entrada, Endereçamento, Reposição, Necessidades de Compra, Pedidos de Venda,
  Separação, Conferência de Saída, Expedição e Devolução ganharam links para as telas vizinhas.
- **Ordens de Compra:** o painel mostra recebido e a receber, o atraso e o botão "Receber
  mercadorias" quando a ordem está em aberto.
- **Controle de Estoques:** quatro indicadores no topo, o de "abaixo do mínimo" filtra a lista, e
  "Mais ações" leva às outras telas do estoque. A página do produto leva à compra e ao giro.
- **Clientes:** o painel mostra quantos pedidos o cliente fez, quanto comprou, o último pedido e
  quanto ainda deve, com links para os pedidos e as contas dele.
- **Início:** os 15 quadros do Dashboard e os 8 atalhos de Boas-vindas levam à tela de origem;
  Boas-vindas ganhou a lista "O que precisa de você hoje"; os alertas de estoque e o valor em
  estoque do Dashboard dizem o que o Controle de Estoques diz.
- **Metas e Performance** é um módulo só, com um item no menu e um seletor que troca de visão
  levando o mês e o nível.
- **Menu de Integrações** ficou só com o que é integração.

**3. A verificação que segura isso.** A auditoria do projeto ganhou duas checagens (11,
identificador repetido no dado de exemplo; 12, texto visível que cita o Lovable). Duas suítes
novas: `teste_planilha.py` e `teste_trilha.py`. Oito defeitos foram injetados de propósito, um por
vez, e os oito foram pegos.

**4. As skills do ERP** receberam o que a varredura ensinou: a seção "A tela dentro do sistema" no
portão de QA e "Tela nova nasce ligada: o mapa de vizinhança" na skill principal. O texto novo já
está na cópia que o Claude carrega neste computador e em `C:\Claude AI\Skills\Skills ERP System`.

## Próximo da fila

1. **O teste do usuário** nesta leva e nas duas telas novas.
2. **O resto da lista aprovada**, na ordem sugerida: Finanças (F1 a F4); o que falta da venda (V2 a
   V5 e L4); os indicadores (E2, V3 e F3); os cadastros (C2 a C8, que pedem alinhar os dados de
   exemplo antes); K1 e R6; e por último G3, a página de detalhe abrir o registro clicado.
3. **A segunda varredura**, combinada para a semana seguinte: o miolo de Inventário, Acerto e PDV,
   que a primeira não abriu.
4. **Módulo novo:** Vendas Afiliados e Comissões Afiliados; depois Margem de Contribuição e Custos
   do E-commerce; Formas de pagamento; Notas Fiscais e Integrações; e os relatórios por último.
   Começa pela barganha, com os prints.

## Esperando decisão do usuário

Nenhuma destas trava o teste.

1. **Enviar ao GitHub:** o último envio foi em 09/out/2026. Tudo de 10/out está em commit só neste
   computador. O usuário disse que o caminho será "commit no GitHub, e o GitHub espelha para a
   plataforma"; falta ele dizer "pode enviar" para o primeiro envio, e se passa a valer a cada
   entrega.
2. **Hospedagem:** o Lovable saiu em 10/out/2026 e o usuário pediu a comparação entre Vercel e
   Cloudflare para começar sem custo. A recomendação é **Cloudflare Pages ligada ao GitHub, com o
   banco no Supabase**, e está no topo da seção 2 de `docs/arquitetura-roadmap-desk-company.md`.
   Falta o "ok" dele e a criação da conta da Cloudflare no e-mail do ERP, que só ele pode fazer.
3. **Skill na origem:** o plugin das skills foi enviado pelo claude.ai. O texto novo vale neste
   computador; para valer também no app da Claude, o usuário reenvia a pasta
   `C:\Claude AI\Skills\Skills ERP System\desk-company-erp` por lá.
4. **Filtro de período:** o intervalo com data inicial e final existe em Itens Bloqueados e no
   Giro de Estoque. As outras nove telas com esse filtro têm só as opções prontas; levar para elas
   é uma oferta em aberto.
5. **Kit na compra:** hoje o kit entra em Necessidades de Compra como um produto comum, porque a
   composição de kit ainda não existe. Quando existir, falta decidir se a compra sugere o kit ou
   os componentes.

## O que continua sendo dado de exemplo

O usuário aceitou, em 10/out/2026, que isto fique assim nesta fase:

- **Cada tela tem os seus registros de exemplo.** Um link entre telas cai na lista vizinha já
  filtrada; quando o exemplo de lá não tem o registro, a faixa da lista explica isso.
- **11 páginas de detalhe abrem sempre o mesmo exemplo**, qualquer que seja a linha clicada (item
  G3 da lista).
- **A venda do PDV e a ordem criada em Necessidades de Compra** não aparecem em todas as telas
  vizinhas (a ordem aparece em Ordens de Compra; a página dela abre o exemplo fixo).
- **O Dashboard** tem números próprios. As contradições com o estoque saíram; ler tudo das outras
  telas é o item R6.

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
5. Commit local a cada entrega. Push só quando o usuário decidir.
