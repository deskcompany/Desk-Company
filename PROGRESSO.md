# Progresso do ERP Desk Company

*Atualizado em 10/out/2026, na entrega de Necessidades de Compra e Giro de Estoque.*

Esta página diz onde o projeto está, o que vem depois e o que está esperando decisão. Serve para
começar uma conversa nova sem reler o projeto inteiro. É **reescrita a cada entrega**, no mesmo
commit; o histórico de cada entrega fica no `git log`, e as regras do projeto no `CLAUDE.md`.

## Onde paramos

**Necessidades de Compra e Giro de Estoque estão construídas e esperam o teste do usuário.** As
duas telas, a suíte nova (`teste_compra_giro.py`) e os encaixes nas telas vizinhas estão em commit,
com o selo verde.

O usuário já testou a maior parte das duas telas e não apontou ajuste; falta ele terminar o teste
para aprovar. Em seguida pediu a varredura de melhorias dos módulos prontos, que está entregue como
lista e espera aprovação (item 5 de "Esperando decisão do usuário"). O próximo passo é dele: dizer
quais itens da lista entram, ou seguir para o próximo módulo da fila.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **45 de 59 (76%)**, em 81 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 76% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda,
então o projeto como um todo está bem antes de 76%. As fases de produção (F0 a F8)
estão em `docs/arquitetura-roadmap-desk-company.md`.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 12 de 13 | Relatórios de Estoque |
| Vendas | 5 de 10 | Notas Fiscais, Vendas Afiliados, Margem de Contribuição, Custos do E-commerce, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 3 de 5 | Comissões Afiliados, Relatórios Finanças |
| Integrações | 3 de 7 | Marketplaces e Hubs, Emissão de Notas Fiscais, Gateways de Pagamento, Relatórios de Integrações |
| Configurações | hub com 19 telas | Formas de pagamento (a lista fiscal da NF-e) |

Em Integrações, os 3 itens com tela são atalhos para Cadastros; o módulo não tem tela própria.
O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## O que ficou pronto nesta conversa

Duas telas de Estoque, feitas a partir de 31 prints do Olist e de quatro decisões do usuário
(§14.52 do design system):

- **Necessidades de Compra:** lista viva do que comprar hoje, com indicadores, abas, a conta de
  cada produto no painel lateral e a ordem de compra criada dali, uma por fornecedor.
- **Giro de Estoque:** a régua de faixas (encalhe, baixo giro, giro normal), os três quadros, a
  lista por produto e a planilha com as colunas do Olist.

As quatro decisões:

1. **Lista viva**, no padrão do sistema. Não há botão "gerar".
2. **Só o vendável conta como estoque** na compra: disponível mais o que aguarda endereço.
   Reservado e bloqueado ficam de fora. O aviso de mínimo do Controle de Estoques passou a usar a
   mesma regra.
3. **O painel cria a ordem**, e ela aparece em Ordens de Compra. Excluir ou cancelar a ordem lá
   devolve a necessidade aqui.
4. **O giro avisa na compra:** encalhe abaixo do mínimo entra sem quantidade sugerida. As faixas
   são parâmetro da empresa.

O que nasceu junto, porque as telas dependem:

- **Fornecedor padrão** no cadastro do produto (coluna Padrão na tabela de fornecedores).
- **Quatro parâmetros** em Parâmetros de estoque, seção Compra e giro de estoque.
- **Destino no menu** para os dois itens, nas 81 telas.

Um defeito antigo saiu no caminho: no cadastro do produto, adicionar um fornecedor apagava o nome
digitado nas outras linhas.

## Próximo da fila

Pela ordem sugerida em 09/out/2026, e ainda não confirmada pelo usuário: **Vendas Afiliados e
Comissões Afiliados**; depois Margem de Contribuição e Custos do E-commerce; Formas de pagamento;
Notas Fiscais e Integrações; e os relatórios de cada módulo por último. Começa pela barganha, com
os prints.

## Esperando decisão do usuário

Nenhuma destas trava o próximo módulo.

1. **GitHub:** o último envio foi em 09/out/2026. Os commits de 10/out estão só neste computador.
   Falta o usuário dizer se envia agora e se o envio passa a ser a cada entrega.
2. **Produção:** o Lovable saiu do projeto em 10/out/2026. Falta o usuário dizer com que
   ferramenta o ERP vira sistema de verdade.
3. **Filtro de período:** o intervalo com data inicial e final existe em Itens Bloqueados e no
   Giro de Estoque. As outras nove telas com esse filtro têm só as opções prontas; levar para elas
   é uma oferta em aberto.
4. **Kit na compra:** hoje o kit entra em Necessidades de Compra como um produto comum, porque a
   composição de kit ainda não existe. Quando existir, falta decidir se a compra sugere o kit ou
   os componentes.
5. **Melhorias nos módulos prontos:** o usuário pediu, em 10/out/2026, uma varredura do que pode
   melhorar, linkar ou sair em cada tela pronta. A lista está em
   `docs/melhorias-modulos-prontos.md`, com um código por item (G, C, E, V, L, F, I, K, R e D).
   **Nada dela foi feito.** Falta o usuário dizer quais códigos aprova; os quatro defeitos (D1 a
   D4) valem ser corrigidos de qualquer jeito.

## Ficou de fora de Necessidades de Compra e Giro, de propósito

- **Tags** (filtrar por tags e "aplicar tags"): marcador não existe neste sistema (§12.1).
- **Natureza de operação:** é fiscal, e a NF-e não está habilitada.
- **Prazo de entrega do fornecedor:** não existe no cadastro; a data prevista da ordem é digitada.
- **A página da ordem criada:** a lista de Ordens de Compra mostra a ordem nova, mas a página de
  detalhe continua abrindo o exemplo fixo dela.
- **Os pedidos que ainda vão sair** são dado de exemplo da própria tela: Pedidos de Venda tem outro
  cadastro de produtos.

**Já decidido, fica para depois:** os dados de exemplo (taxas do cartão, cadastros, saldos) não
serão ajustados agora. Quando o sistema rodar de verdade, o usuário limpa tudo e configura do zero.

## Para retomar numa conversa nova

1. Abra o editor na pasta `C:\Claude AI\Desk Company`.
2. Primeira mensagem: "vamos para onde paramos", com os prints do próximo módulo. É para ler este
   arquivo e seguir do próximo da fila.
3. Para ver as telas: `node _ferramentas/servidor.js` na pasta `ERP System`, e depois
   `http://localhost:3000/<pasta>/<arquivo>`. O servidor cai quando a sessão fecha.
4. Antes de dar algo por pronto: `python selo.py --rodar` na pasta `_ferramentas`.
5. Commit local a cada entrega. Push só quando o usuário decidir.
