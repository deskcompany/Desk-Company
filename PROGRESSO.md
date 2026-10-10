# Progresso do ERP Desk Company

*Atualizado em 10/out/2026, no fechamento da conversa de 06 a 10/out.*

Esta página diz onde o projeto está, o que vem depois e o que está esperando decisão. Serve para
começar uma conversa nova sem reler o projeto inteiro. É **reescrita a cada entrega**, no mesmo
commit; o histórico de cada entrega fica no `git log`, e as regras do projeto no `CLAUDE.md`.

## Onde paramos

A conversa anterior foi fechada em 10/out/2026 com **tudo em commit** e a **auditoria completa
verde** (as 32 suítes e as duas auditorias, sem pular nenhuma: 4.039 asserções, 0 falhas). Não ficou tela pela metade nem ajuste pendente.

O próximo passo é construir **Necessidades de Compra e Giro de Estoque**. O usuário abre a próxima
conversa dizendo "vamos para onde paramos", já com os prints do Olist; começa pela barganha.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **43 de 59 (73%)**, em 79 telas |
| **Produção** | o que já virou sistema de verdade | **não começou** |

Os 73% medem só o protótipo. Nenhuma tela virou sistema de verdade ainda,
então o projeto como um todo está bem antes de 73%. As fases de produção (F0 a F8)
estão em `docs/arquitetura-roadmap-desk-company.md`.

| módulo | com tela | falta |
|---|---|---|
| Início | 4 de 4 | nada |
| Cadastros | 12 de 13 | Relatórios de Cadastros |
| Estoque | 10 de 13 | Necessidades de Compra, Giro de Estoque, Relatórios de Estoque |
| Vendas | 5 de 10 | Notas Fiscais, Vendas Afiliados, Margem de Contribuição, Custos do E-commerce, Relatórios de Vendas |
| Logística | 5 de 6 | Relatórios de Logística |
| Finanças | 3 de 5 | Comissões Afiliados, Relatórios Finanças |
| Integrações | 3 de 7 | Marketplaces e Hubs, Emissão de Notas Fiscais, Gateways de Pagamento, Relatórios de Integrações |
| Configurações | hub com 19 telas | Formas de pagamento (a lista fiscal da NF-e) |

Em Integrações, os 3 itens com tela são atalhos para Cadastros; o módulo não tem tela própria.
O detalhe de cada tela está em `docs/mapa-modulos-desk-company.md`.

## O que ficou pronto na última conversa

Três módulos novos, todos testados pelo usuário e sem pendência de tela:

- **PDV** (Vendas, §14.48 e §14.49): venda de balcão, turno de caixa, cartão com prazo e repasse
  de taxa. As taxas por parcela são de exemplo, de propósito.
- **CRM** (Vendas, §14.50): assuntos, estágios, ações com data na Agenda, quadro por estágio. O
  relógio do horário anda de 5 em 5 minutos e é o mesmo na Agenda.
- **Itens Bloqueados** (Estoque, §14.51): a fila do que está no estoque e não pode ser vendido. O
  bloqueio é feito na própria fila, o painel de resolver tem três abas, e o filtro de período
  aceita data inicial e final. A falta da Separação e da Conferência de Saída bloqueia a unidade.

Correções que valeram para o sistema, achadas nos testes do usuário:

- o menu lateral marcava o módulo errado em cinco telas;
- o calendário saía cortado pela borda do painel (componente de data, 15 telas);
- o menu de um dropdown dentro de tabela era cortado por ela (as duas Conferências);
- o filtro de período ficava aberto por baixo do dropdown vizinho (quatro telas);
- "Banco a contagem" virou "Confirmar contagem".

Cada uma ganhou um teste que varre o sistema inteiro, para o defeito não voltar numa tela nova.

## Próximo da fila

**Necessidades de Compra e Giro de Estoque** (Estoque), escolhidos pelo usuário em 09/out/2026.
Os dois já têm item no menu e nenhuma tela. Ainda não há prints de referência nem decisões
tomadas: começa pela barganha.

Depois deles, pela ordem sugerida: Vendas Afiliados e Comissões Afiliados; Margem de Contribuição
e Custos do E-commerce; Formas de pagamento; Notas Fiscais e Integrações; e os relatórios de cada
módulo por último.

## Esperando decisão do usuário

Nenhuma destas trava o próximo módulo.

1. **GitHub:** o último envio foi em 09/out/2026. Os commits de 10/out estão só neste computador.
   Falta o usuário dizer se envia agora e se o envio passa a ser a cada entrega.
2. **Produção:** o Lovable saiu do projeto em 10/out/2026. Falta o usuário dizer com que
   ferramenta o ERP vira sistema de verdade.
3. **Filtro de período:** o intervalo com data inicial e final existe só em Itens Bloqueados. As
   outras nove telas com esse filtro têm só as opções prontas; levar para elas é uma oferta em aberto.

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
