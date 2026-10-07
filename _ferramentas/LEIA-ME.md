# Ferramentas de verificação — ERP Desk Company

Scripts que conferem as telas. **Não são parte do sistema** — nenhuma tela depende deles, e apagar esta pasta não quebra nada. Eles existem para que uma sessão nova não precise reescrever a verificação do zero.

Criados em 23/set/2026, junto com Contas a Pagar. Apertados em 28/set/2026, na revisão completa da pasta.

## O SELO — o que já está provado não roda de novo (30/set/2026)

A verificação completa passou de **20 minutos**. Teste caro é teste que alguém começa a pular, e teste pulado não protege nada. Mas pular *por achismo* é pior: foi assim que a exclusão em massa ficou sem senha por 11 dias.

O `selo.py` resolve isso por uma regra mecânica, que não depende da memória de ninguém:

> **uma suíte só é pulada quando nada que ela cobre mudou desde que ela passou.**

O selo guarda, por suíte, o SHA-256 de cada arquivo que ela cobre e o da própria suíte. Na verificação:

| situação | o que acontece |
|---|---|
| nada mudou | **SELADA** — pula |
| uma tela coberta mudou | roda **só nessa tela**, quando a suíte varre a pasta; inteira, quando é de telas fixas |
| a própria suíte mudou | roda inteira — teste novo nunca nasce selado |
| tela nova apareceu | toda suíte que varre a pasta roda nela |
| `auditoria.py` ou a auditoria oficial mudaram | a auditoria correspondente roda inteira |
| `alvos.py` mudou | **todas** as suítes rodam — o filtro é o que decide o que elas veem |

```bash
python3 selo.py                 # o que está selado e o que precisa rodar
python3 selo.py --rodar         # roda só o que precisa, e sela o que passar
python3 selo.py --rodar --tudo  # ignora o selo, roda tudo
python3 selo.py --selar         # sela o estado atual sem rodar (só depois de uma rodada verde na mão)
```

**Medido em 30/set:** mexer em uma tela de detalhe acordou 8 suítes e deixou 7 seladas; as que varrem a pasta rodaram em **1 tela em vez de 54**. A rodada inteira leva ~7 min; a seletiva, 18 s.

### A cobertura sai do código, não de uma lista escrita à mão

Lista escrita à mão envelhece — foi ela que fez "8 telas com o problema" virar 23 sem ninguém perceber. O `selo.py` lê a cobertura **da própria suíte**: os nomes de `pagina-*.html` que ela cita, ou "a pasta toda" quando ela faz `glob`.

**E isso foi provado por observação, não por leitura.** Cada suíte foi rodada com o `Page.goto` do Playwright instrumentado, registrando as telas que ela realmente abriu, e o resultado comparado com a cobertura declarada: **nenhuma suíte abre tela fora da sua cobertura**. Algumas cobrem mais do que abrem (o `teste_menu` lê as 54 como texto, o `teste_integra` chega no Caixa por clique e não por `goto`) — e essa é a direção segura do erro: cobrir demais custa uma rodada a mais, cobrir de menos é selo mentiroso. **Repetir essa prova sempre que uma suíte nova entrar.** Feito em 30/set para o `teste_pedidos.py`: cobertura declarada e telas realmente abertas deram **exatamente as mesmas duas** — nenhuma fora, nenhuma coberta sem abrir.

### O que o selo NÃO cobre

Ele não olha para o `varredura_cliques.py` (é ferramenta de fechamento de módulo, roda sob demanda) nem julga se a suíte *testa a coisa certa* — só se o que ela testa continua igual. Suíte que nasceu fraca continua fraca, selada ou não.

## Como rodar

Os scripts acham a pasta sozinhos (sobem um nível a partir daqui) e acham o navegador sozinhos. Rodando de dentro desta pasta:

```bash
# auditoria estática de um arquivo (ou de vários)
python3 auditoria.py ../pagina-financas-contas-pagar.html

# a pasta inteira — uma chamada só, com o total no fim
python3 auditoria.py ../pagina-*.html

# um teste de navegador
python3 teste_cp.py
```

Se a pasta estiver em outro lugar: `DESK_PASTA=/caminho/para/a/pasta python3 teste_cp.py`.

Precisa de `playwright` instalado (`pip install playwright`) e de um Chromium. Se não houver um em `/opt/pw-browsers`, o script usa o que o Playwright trouxer.

## O que cada um cobre

| arquivo | o que verifica | asserções |
|---|---|---|
| `auditoria.py` | estática: tags balanceadas, sintaxe JS, ids órfãos, catálogo de senhas, chaves de `localStorage`, controles sem ação, **tag escrita dentro de texto de modal** | — |
| `teste_cp.py` | Contas a pagar (listagem): abas, situação derivada, expansão da linha, baixa, parcial, período fechado, cancelar/reativar | 53 |
| `teste_cpd.py` | Conta a pagar (página): as duas famílias de repetição, prévia, escopo em grupo, cancelar, estorno, layout do bloco | 68 |
| `teste_caixa.py` | Caixa: extrato, ordem, totais, transferência, fechamento, calendário | 54 |
| `teste_lanc.py` | Lançamento do Caixa | 44 |
| `teste_integra.py` | Contas a pagar **escreve** no Caixa e o Caixa **lê** | 14 |
| `teste_agenda_aviso.py` | recorrência que termina vira aviso na Agenda, e renovar cria o ano seguinte | 24 |
| `teste_menu.py` | o menu lateral navega de verdade entre as telas | 13 |
| `teste_datas.py` · `teste_pos.py` | o componente de data e o posicionamento do calendário | 24 |
| `teste_dropdown_todas.py` | clica no dropdown das **54 telas**: abre, escolhe, fecha — e, desde 02/out, confere com `elementFromPoint` que o menu **aparece de verdade**, não só no DOM (ver abaixo) | 54 telas |
| `teste_confirma_senha.py` | **(28/set)** modal de confirmação em **todas** as telas que carregam o bloco de senha — descobertas pelo próprio script, sem lista fixa: a trava trava, o Esc fecha, o "estou ciente" aparece com 2+, a ação entra no registro, e o despacho entrega o callback nas **três assinaturas** | 687 |
| `teste_mais_acoes.py` | **(28/set)** o menu "Mais ações": id, rótulo e estilo únicos, abre no clique, **fecha mutuamente** com os outros dropdowns, e a ação destrutiva está **dentro** dele com `item-perigo` | 132 |
| `teste_esc_dropdown.py` | **(28/set)** Esc fecha o dropdown aberto em todas as telas — e, sem dropdown aberto, continua fechando o modal | 120 |
| `teste_recibo_clone.py` | **(29/set)** clonar conta (copia a despesa, não a data) e imprimir recibo (travado sem baixa, valor por extenso com a regra do "e") | 30 |
| `teste_receber.py` | **(02/out)** Contas a Receber, listagem e página da conta — o que ele protege é o que separa o **receber** do **pagar**, que é o que um clone apaga em silêncio: a conta nasce do pedido e a Origem leva até ele; Valor, Líquido, Saldo e Recebido são quatro números diferentes; a **taxa retida quita o título sem entrar no Caixa**; **baixa é entrada e estorno é saída** (o clone trouxe invertido); recibo e duplicata têm travas **inversas**; o pedido define as parcelas e a sobra dos centavos fica na primeira; e cliente com conta vencida não compra de novo | 116 |
| `selo.py` · `alvos.py` | **(30/set)** o selo acima: decide o que roda e o que pula, e restringe as suítes que varrem a pasta às telas que mudaram (`DESK_ALVOS`) | — |
| `teste_becos.py` | **(29/set, noite)** nenhuma tela diz que outra tela "ainda não existe" ou que "a navegação só funciona no Lovable" (varre as 54); 20 botões levam ao destino certo; `?receber=1`, `?clonar=1` e `?nota=` chegam certos; os 5 cadastros abrem em edição pelo Incluir e pelo Editar, e em leitura (ou conforme a preferência) na consulta; a senha fica no modal que **exclui**, nunca no aviso de que nada pode ser excluído (OC, Depósitos, Endereços); cancelar OC recebida pede senha; competência em massa no Caixa; hub sem marcadores | 110 |
| `teste_pedidos.py` | **(30/set)** Pedidos de Venda, listagem e página do pedido — o que ele protege são as **decisões da barganha de 30/set**, não o desenho: as 11 abas cabem numa linha só e o que sobra vai para "mais"; contador e rodapé contam a mesma coisa e o cancelado fica fora do total; a reserva nasce com o pedido e volta no cancelamento; pedido expedido não se exclui; pedido sem saldo não nasce, e a mensagem diz **quanto existe**; os dois níveis de desconto, cada um na sua base; a loja escolhe o depósito; cadastro rápido nasce incompleto; comissão liberada no faturamento; campos fiscais visíveis e desabilitados. **(02/out)** mais 6 seções: o funil anda um passo por vez na ordem certa e termina em Entregue; avançar NÃO pede senha e alterar situação à mão PEDE; clonar abre o pedido preenchido com a data de hoje; os painéis de últimas vendas e de limite de crédito abrem sem sair do pedido; o limite bloqueia em boleto e deixa passar em Pix; e nenhum item do menu voltou a ser promessa vazia. **(02/out, noite)** situação virou filtro suspenso: as 10 opções abrem todas visíveis, os contadores acompanham os outros filtros, e devolução não é mais situação de pedido | 256 |

Total: **2.996 asserções** sob selo *(a contagem passou a ser medida pelo `selo.py` a cada rodada verde, em vez de somada à mão — os números antigos por suíte estavam defasados)*.

## Varredura de cliques (29/set/2026) — ferramenta de fechamento de módulo

`varredura_cliques.py` não é suíte do dia a dia: leva **uns 10 minutos**. Ela abre cada tela, clica em **cada controle da área principal, um por vez, recarregando a tela entre cliques**, abre a primeira linha da listagem e clica no que aparecer no painel. Relata três coisas: **erro de JavaScript**, **navegação para arquivo que não existe** e **aviso dizendo que uma tela existente "ainda não existe"** (a frase que escondeu 19 becos sem saída até 29/set).

```bash
python3 varredura_cliques.py            # as 54 telas
python3 varredura_cliques.py - estoque  # só as que têm "estoque" no nome
```

Rodar **antes de dar um módulo por pronto** e depois de qualquer mudança no bloco compartilhado. Em 29/set: 1.605 cliques em 52 telas, FALHAS: 0. Em 30/set, com Pedidos de Venda: **1.676 cliques em 54 telas, FALHAS: 0**.

**Lista escrita à mão envelhece.** `teste_confirma_senha.py` tinha as telas cravadas e foi assim que "8 telas com o problema" virou 23 sem ninguém perceber. Hoje ele varre a pasta e descobre sozinho quais testar — quando um teste novo puder fazer isso, faça.

## O `auditoria.py` foi apertado em 28/set/2026

Ele produzia quatro falsos positivos (mais um quinto que só apareceu depois), e por isso **superestimava a dívida** — numa sessão isso virou um "36 telas com dívida" que a verificação desmentiu. Auditoria que grita à toa é auditoria que ninguém lê. Os cinco foram resolvidos **no script**, não na tela:

| o que acusava | por que era falso | como foi resolvido |
|---|---|---|
| `<select>` nativo (15 telas) | era o texto dentro do comentário que descreve o dropdown customizado | as checagens de marcação passaram a olhar o texto **sem comentários** (`sem_comentarios`) |
| `getElementById` sem elemento: `menuMaisAcoes` (13) | o código tem `if (!raiz) return;` | `tem_guarda()` reconhece `if (!x) return`, `if (x)`, `x &&` e `?.` — antes era uma lista de dois ids escrita à mão |
| controle sem ação: `btnNovoCliente` e afins (6) | são `a href` que navegam | link com destino real sai da conta |
| checkbox sem classe do DS (20) | estilizados pelo pai (`.dropdown-multi-item input`) | `classes_que_estilizam_checkbox()` lê o CSS do próprio arquivo e aceita o filho |
| `selAno`, `selMes` e mais 4 em Metas | nascem de `innerHTML`, via `dropdownHtml('selMes', …)` | `ids_construidos_por_js()` acha a função que monta `id="' + param` e marca os ids que ela cria |

**Resultado: de 33 arquivos "com problema" para 0 falhas reais nas 53 (55 arquivos hoje).** O `pagina-molde-referencia.html` continua aparecendo, agora como **EXCEÇÃO** explícita (dois documentos no mesmo arquivo, de propósito) — visível, mas fora da contagem.

**O aperto foi provado nos dois sentidos.** Injetando defeito de verdade num arquivo de teste, o script continua reprovando: `select` nativo solto, `getElementById` sem guarda, checkbox sem classe e sem pai que o estilize, `a href="#"` sem listener, e `div` desbalanceada. **Auditoria mais quieta só vale se continuar mordendo** — quando mexer nela de novo, repetir essa prova.

## A checagem 10 nasceu de um bug que voltou (30/set/2026)

O modal de confirmação escreve com `textContent`. `<b>` escrito ali não vira negrito: aparece na cara do usuário como `</b>`. Isso foi corrigido à mão em 29/set numa tela e **voltou em 30/set** na página do pedido — o mesmo erro, no mesmo lugar, oito dias depois.

Correção à mão não impede a terceira vez. Virou a **checagem 10** do `auditoria.py`: ela recorta o argumento de texto de `avisar()`, `confirmarAcao()` e `abrirModalConfirmacao()` até onde a função executora começa, e reprova qualquer `b`, `i`, `strong`, `br`, `span` ou `div` escrito ali. O `innerHTML` de dentro do callback continua livre, que é onde tag é legítima.

Provada nos dois sentidos, como manda a seção acima: num arquivo com o defeito injetado ela reprova (`10 tag literal em texto de modal (avisar): </b>`); nas 55 reais, silêncio.

## Abrir não é aparecer (02/out/2026)

O menu *mais* das abas de Pedidos de Venda abria no DOM, respondia ao `click()` do Playwright, e **o usuário não via nada**: estava recortado por um `overflow:hidden` do container. O teste afirmava `classList.contains('open')` e passava em cima do bug.

A asserção agora é a do **dedo do usuário**: `document.elementFromPoint` no centro do primeiro item do menu, conferindo se o elemento ali dentro é o item. Ela entrou no `teste_dropdown_todas.py`, que varre as 55 telas — e **acusou mais dois casos no mesmo minuto**. Os dois eram falsos positivos (dropdown dentro de painel lateral fechado, deslocado para fora da tela), e por isso a regra tem duas metades:

> só cobre que o **menu** apareça quando o **próprio botão** estiver alcançável no ponto dele.

`offsetParent !== null` não basta: painel lateral fechado tem offsetParent. Com as duas metades: **41 telas testadas, 0 falhas** (eram 43 antes — as duas que saíram só têm dropdown dentro de painel fechado, que o usuário não alcança na abertura; os fluxos delas são cobertos pelas suítes próprias).

## O veredito da auditoria sai em toda chamada (02/out/2026)

O `auditoria.py` só imprimia `N arquivo(s) com falha real` quando recebia **2+ arquivos**. O `selo.py` lê essa linha — então, numa rodada restrita a um arquivo só, ele dava por **reprovada uma auditoria limpa**. Ferramenta certa, veredito ilegível.

Agora a linha sai sempre, e o **código de saída é o contrato**: `sys.exit(1)` quando há falha real, `0` quando não há. O `selo.py` passou a olhar o código primeiro e a linha como segunda confirmação. Provado nos dois sentidos, como manda a seção acima.

## Clonar uma tela de sentido OPOSTO (02/out/2026)

Contas a Receber nasceu de Contas a Pagar. O `pagar → receber` em bloco deixou o código compilando e **os lançamentos invertidos**: a baixa escrevia saída no Caixa, o estorno escrevia entrada. Auditoria nenhuma pega isso — tag balanceada, JS válido, id existente.

Duas coisas saíram daí:

1. **A lista do que conferir depois de clonar o oposto não é de nomes, é de DIREÇÕES** — o que entra, o que sai, o que soma, o que subtrai. Virou a seção 6 do `teste_receber.py`, que lê o próprio código da tela procurando `tipo: 'entrada'` na baixa e `tipo: 'saida'` no estorno.
2. **O rename também inventa palavra e atropela nome compartilhado.** `fornecedores → clientes` produziu `pagina-cadastros-clientees.html` (link para arquivo inexistente, pego pela auditoria oficial) e transformou os grupos de categoria em *"Custos e clientees"* e *"Receitas fixas"*. **Nome compartilhado se restaura copiando do arquivo canônico**, nunca reescrevendo à mão.

## Teste de negativa envelhece junto com o sistema (02/out/2026)

O `teste_menu` provava que item de menu sem tela fica inerte usando *Contas a Receber* — que acabou de ganhar tela. O teste passou a reprovar uma tela certa. Apontado para *Comissões Afiliados*, que de fato ainda não existe.

Na mesma rodada, o `teste_integra` tomou a **terceira mordida** do *"o mock envelhece"*: ele escolhia o primeiro título em aberto do mock, mas a listagem abre filtrada pelo mês corrente — em 30/set o alvo caía dentro, em 02/out não. Passou a escolher **entre as linhas que estão na tela**.

As três mordidas foram a mesma coisa: **o teste conhecia o dado, não a tela**.

## Exceções que continuam legítimas

- `pagina-molde-referencia.html` tem dois `body` e ids repetidos **de propósito** (são dois documentos no mesmo arquivo).
- ~~Seis classes-gancho~~ — **convertidas para `data-*` em 28/set/2026**; não existem mais. A convenção para gancho de JS é `data-*`, não classe vazia (§12.2 do design system).
