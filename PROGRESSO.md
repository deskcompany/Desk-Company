# Progresso do ERP Desk Company

*Atualizado em 09/out/2026, depois do fechamento dos pontos em aberto de PDV, CRM e Itens Bloqueados.*

Esta página diz onde o projeto está, o que vem depois e o que está esperando decisão. Serve para
começar uma conversa nova sem reler o projeto inteiro. É **reescrita a cada entrega**, no mesmo
commit; o histórico de cada entrega fica no `git log`, e as regras do projeto no `CLAUDE.md`.

## Onde estamos

| etapa | o que mede | hoje |
|---|---|---|
| **Protótipo** | itens do menu que já têm tela HTML validada | **43 de 59 (73%)**, em 79 telas |
| **Produção** | o que já virou sistema de verdade no Lovable | **não começou** |

Os 73% medem só o protótipo. Nenhum documento do projeto registra tela que já tenha virado prompt
do Lovable, então o projeto como um todo está bem antes de 73%. As fases de produção (F0 a F8)
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

## Última entrega

**Fechamento dos pontos em aberto**, em 09/out/2026. Nenhum módulo novo; as três entregas do dia
ficaram sem pendência de tela:

- **PDV** (§14.48 e §14.49): fechado. As taxas do cartão por parcela são de exemplo, de propósito.
- **CRM** (§14.50): fechado. O relógio do horário anda de 5 em 5 minutos, e a **Agenda** passou a
  usar o mesmo relógio no lugar dos dois dropdowns.
- **Itens Bloqueados** (§14.51): fechado. O bloqueio é feito na própria fila, com a busca padrão de
  produto e a opção "Todos os endereços"; o painel de resolver tem três abas (Resolver, Manter
  bloqueado e Histórico).
- **Conferência de Saída:** o menu do motivo deixou de ser cortado pela tabela, e "Banco a
  contagem" virou "Confirmar contagem".

Verificação no fechamento: 32 suítes, 4.021 asserções, 0 falhas.

## Próximo da fila

**Necessidades de Compra e Giro de Estoque** (Estoque), escolhidos pelo usuário em 09/out/2026.
Os dois já têm item no menu e nenhuma tela. Ainda não há prints de referência nem decisões
tomadas: começa pela barganha.

## Esperando decisão do usuário

Nenhuma destas trava o próximo módulo.

1. **Lovable:** nenhum prompt foi pedido para PDV, CRM e Itens Bloqueados.
2. **GitHub:** o envio de 09/out/2026 foi autorizado para aquela rodada. Falta definir se passa a
   ser a cada entrega ou continua sob pedido.

**Já decidido, fica para depois:** os dados de exemplo (taxas do cartão, cadastros, saldos) não
serão ajustados agora. Quando o sistema rodar de verdade, o usuário limpa tudo e configura do zero.

## Para retomar numa conversa nova

1. Abra o editor na pasta `C:\Claude AI\Desk Company`.
2. Primeira mensagem: "Leia o PROGRESSO.md do ERP e vamos seguir do próximo da fila."
3. Para ver as telas: `node _ferramentas/servidor.js` na pasta `ERP System`, e depois
   `http://localhost:3000/<pasta>/<arquivo>`. O servidor cai quando a sessão fecha.
4. Antes de dar algo por pronto: `python selo.py --rodar` na pasta `_ferramentas`.
5. Commit local a cada entrega. Push só quando o usuário decidir.
