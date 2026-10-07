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

**Os screenshots vão para o diretório temporário, não para a pasta do projeto** (06/out/2026).
Seis suítes tiram um `qa-*.png` no fim; com caminho relativo depois do `os.chdir(PASTA)`, elas
largavam 800 KB na raiz **a cada rodada** — e apagar à mão é tarefa que volta. Agora usam
`tempfile.gettempdir()`, a mesma convenção que o `varredura_cliques.py` já seguia para o JSON
dele. O `qa-*.png` continua no `.gitignore` como rede de segurança, para o caso de uma suíte
nova nascer gravando na raiz.

## Rodando no Windows (06/out/2026)

A pasta passou a ser trabalhada direto no Windows, do Antigravity, em vez de numa cópia
stageada no Linux do app da Claude. **O comando é `python`, não `python3`.**

Instalar não bastou. A suíte nasceu no Linux e tinha quatro coisas que só funcionavam lá —
nenhuma delas aparecia como "falta Python", todas apareciam como teste vermelho ou traceback:

| onde | o que quebrava | conserto |
|---|---|---|
| `auditoria.py` | `/tmp/` cravado → `FileNotFoundError` na primeira tela | `tempfile.gettempdir()` |
| `selo.py`, 3 chamadas | invocava `python3`, que no Windows cai no stub da Microsoft Store | `sys.executable` |
| `selo.py`, auditoria oficial | `/root/.claude/...` cravado | sai de `~/.claude` com glob da geração do plugin |
| `selo.py`, `gravar_selo()` | gravava o selo com o fim de linha da plataforma | `newline='\n'` |

O glob do `/opt/pw-browsers` nas 21 suítes **não precisou mudar**: ele volta vazio, `CHROME`
fica `None` e o Playwright usa o navegador dele. Era o comportamento já previsto acima.

### O encoding derrubou 6 suítes verdes, e isso é a lição

Numa rodada completa, 7 suítes ficaram vermelhas. Rodadas **à mão, uma por uma, passavam**.
A causa não estava em nenhuma delas: estava no `roda()` do `selo.py`, nas duas pontas do pipe.
O filho escrevia em cp1252 e **morria no primeiro caractere fora dele** — um sinal de menos
numa mensagem matou uma suíte de 24 asserções inteira. E o pai decodificava em cp1252, o que
fazia "asserções" chegar como `asser��es`: o mesmo texto de onde o selo **mede** o veredito e
conta as asserções.

Vale o mesmo que o resto deste arquivo prega: **teste vermelho nem sempre acusa a tela.** Antes
de caçar o bug na página, rode a suíte sozinha — se ela passar fora do selo e falhar dentro
dele, o defeito é do runner. Corrigido com `PYTHONIOENCODING=utf-8` no ambiente do filho e
`encoding='utf-8'` explícito na leitura do pai.

### O que foi medido aqui, e não herdado do Linux

Selo verde é promessa sobre a máquina que o selou. Vindo do Linux, ele dizia "21 seladas" numa
máquina que ainda não tinha navegador — **selo herdado é falsa segurança**. Por isso a
migração foi fechada com `--rodar --tudo`, ignorando o selo. A auditoria oficial da skill
(seções 5 e 6: runtime no navegador, contraste WCAG e layout nos dois temas a 1440px) passou
com **tudo limpo** nas 64 telas.

**A auditoria oficial vive no plugin**, em `~/.claude/plugins/synced/`, e lá ela também tinha
`/tmp` cravado. Foi corrigida nas duas gerações instaladas, com um `.linux.bak` ao lado — mas
**um re-sync do plugin reverte isso**. O conserto durável é atualizar o plugin na origem. Se a
auditoria oficial voltar a falhar com `FileNotFoundError: '/tmp/_aud.js'`, é isso.

### A URL que se monta não é a URL que o navegador devolve

`'file://' + PASTA` funciona no `goto` — o Chromium normaliza o que recebe. Mas o que ele
**devolve** em `pg.url` tem barras para frente, três barras depois do esquema e espaço como
`%20`. Em `/home/claude/desk-company` as duas formas coincidiam; em `C:\Claude AI\Desk Company`
não, e o `destino()` do `teste_becos` (um `pg.url.replace(URL, '')`) parou de casar: **20
falhas, todas em botões que levavam ao destino certo**. O conserto é montar a base com
`Path(PASTA).as_uri()`, que dá a forma do navegador nas duas plataformas.

O `varredura_cliques.py` tinha a versão pior do mesmo problema: além de nem iniciar
(`glob(...)[0]` de lista vazia → `IndexError`, enquanto as 21 suítes usam `[0] if lista else
None`), ela convertia URL em caminho com `.replace('file://', '')`. Num caminho com espaço isso
devolve `/C:/Claude%20AI/...`, e `os.path.exists` reprovaria **toda** navegação — a ferramenta
passaria a acusar beco sem saída em cada clique. Agora usa `url2pathname` + `urlparse`.

**Quem só faz `goto` não precisou mudar** e não mudou: o navegador normaliza a entrada, e as
suítes que montam `'file://' + abspath(...)` sem comparar continuam corretas. A regra de
propagar correção vale para o defeito, e aqui o defeito é a **comparação**, não a concatenação.

### Exit code virou contrato nas 7 suítes que mentiam

O `teste_becos` imprimia `FALHAS: 20` e **saía 0**. Conferir pelo exit code o dava verde; só o
selo pegava, porque ele lê o texto. Sete suítes estavam assim (as de Logística, Pedidos,
Receber, Transportadoras e o próprio becos) — todas as mais novas, nenhuma com `sys.exit`.

Agora terminam com `raise SystemExit(1 if falhas else 0)`, o mesmo contrato que a
`auditoria.py` já tinha. Provado nos dois sentidos: defeito injetado numa cópia descartável sai
**1**, arquivo real limpo sai **0**.

**A lição é mais ampla que o conserto:** teste que não propaga falha é pior que teste ausente,
porque o verde dele é afirmativo. Quando entrar suíte nova, confira o exit code nos dois
sentidos antes de confiar nela.

### A medição dependia de ter rede, e ninguém sabia

O `teste_pos.py` exigia o calendário a `0..12px` do **ícone** e no Windows media 13,5 —
reprovava por 1,5px, sem defeito visível. A tentação era alargar para 16. Medir o mecanismo
mostrou que alargar seria passar a borracha na coisa errada.

O CSS é `.date-pop { bottom: calc(100% + 6px) }` e o containing block é o `.date-field`. Então
**o contrato é 6px acima do CAMPO**, e ele é entregue exato em toda plataforma. A folga até o
*ícone* é `6 + o recuo do ícone dentro do campo` — e esse recuo sai da métrica da fonte, porque
o input **não tem altura fixa** (`padding:9px 11px` + `font-size:13.5px`).

A Nunito vem do Google Fonts **pela rede**. Medido nas duas pontas, na mesma tela:

| | altura do campo | recuo do ícone | campo → popup | ícone → popup |
|---|---|---|---|---|
| Nunito carregada | 39px | 7,5px | **6,00px** | 13,5px → reprovava |
| fonte em fallback | 35px | 5,5px | **6,00px** | 11,5px → passava |

Ou seja: a faixa `0..12` foi calibrada no Linux **sem rede**, contra uma renderização que o
usuário nunca vê. O vermelho no Windows estava mais perto da verdade de produção que o verde
de lá. A asserção passou a medir `campo → popup == 6px`: igualdade contra o contrato do CSS, não
faixa de tolerância — mais forte, e indiferente a fonte e plataforma. Provada nos dois sentidos,
com regressão de 20px injetada por `add_style_tag` numa cópia descartável.

**Duas regras saem daí.** A primeira: **meça contra o que o CSS promete, não contra o que estava
na tela no dia** — asserção ancorada no contrato é exata; ancorada no resultado observado, ela
só registra a plataforma de quem a escreveu. A segunda: **medição que depende de rede não é
medição.** A boa notícia é que a auditoria oficial foi rodada aqui **com** a Nunito real e passou
limpa nas 64 telas — como a Nunito é mais alta que o fallback, o estouro de largura medido no
Linux era, se algo, otimista, e com a fonte real as telas continuam limpas.

**Dívida aberta:** embarcar a Nunito local (`.woff2` + `@font-face`) em vez de depender do Google
Fonts tornaria toda medição determinística, eliminaria o FOUT e faria as telas abrirem offline.
Mexe nos 64 arquivos — é decisão de arquitetura, não conserto de teste.

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
| `teste_receber.py` | **(02/out)** Contas a Receber, listagem e página da conta — o que ele protege é o que separa o **receber** do **pagar**, que é o que um clone apaga em silêncio: a conta nasce do pedido e a Origem leva até ele; Valor, Líquido, Saldo e Recebido são quatro números diferentes; a **taxa retida quita o título sem entrar no Caixa**; **baixa é entrada e estorno é saída** (o clone trouxe invertido); recibo e duplicata têm travas **inversas**; o pedido define as parcelas e a sobra dos centavos fica na primeira; e cliente com conta vencida não compra de novo | 61 |
| `selo.py` · `alvos.py` | **(30/set)** o selo acima: decide o que roda e o que pula, e restringe as suítes que varrem a pasta às telas que mudaram (`DESK_ALVOS`) | — |
| `teste_becos.py` | **(29/set, noite)** nenhuma tela diz que outra tela "ainda não existe" ou que "a navegação só funciona no Lovable" (varre as 54); 20 botões levam ao destino certo; `?receber=1`, `?clonar=1` e `?nota=` chegam certos; os 5 cadastros abrem em edição pelo Incluir e pelo Editar, e em leitura (ou conforme a preferência) na consulta; a senha fica no modal que **exclui**, nunca no aviso de que nada pode ser excluído (OC, Depósitos, Endereços); cancelar OC recebida pede senha; competência em massa no Caixa; hub sem marcadores | 110 |
| `teste_pedidos.py` | **(30/set)** Pedidos de Venda, listagem e página do pedido — o que ele protege são as **decisões da barganha de 30/set**, não o desenho: as 11 abas cabem numa linha só e o que sobra vai para "mais"; contador e rodapé contam a mesma coisa e o cancelado fica fora do total; a reserva nasce com o pedido e volta no cancelamento; pedido expedido não se exclui; pedido sem saldo não nasce, e a mensagem diz **quanto existe**; os dois níveis de desconto, cada um na sua base; a loja escolhe o depósito; cadastro rápido nasce incompleto; comissão liberada no faturamento; campos fiscais visíveis e desabilitados. **(02/out)** mais 6 seções: o funil anda um passo por vez na ordem certa e termina em Entregue; avançar NÃO pede senha e alterar situação à mão PEDE; clonar abre o pedido preenchido com a data de hoje; os painéis de últimas vendas e de limite de crédito abrem sem sair do pedido; o limite bloqueia em boleto e deixa passar em Pix; e nenhum item do menu voltou a ser promessa vazia. **(02/out, noite)** situação virou filtro suspenso: as 10 opções abrem todas visíveis, os contadores acompanham os outros filtros, e devolução não é mais situação de pedido | 128 |

| `teste_rastreamento.py` | **(07/out)** Rastreamento de Pedidos — o que ele protege são as **quatro barganhas de 07/out**, não o desenho: pagamento é eixo SEPARADO (prova que existe pedido enviado e não pago, e pago e não enviado); o código é por VOLUME; cada evento carrega o marcador de quem o vê e o rótulo do cliente (Faturado é interno, Conferência de saída vira "Pedido embalado"); e a previsão é CONGELADA — o teste muda o prazo da transportadora para 99 e confirma que a previsão de quem já saiu não se move. Mais: a tabela cabe no card a 1440px, Esc fecha o painel, o dropdown aparece de verdade e as 4 ações entram no catálogo de senhas. **A partir de 07/out também guarda a divisão de quem escreve:** a listagem só lê (nenhum `data-confirmar`, nenhum `data-alterar` no painel) e o **detalhe** é a única tela que grava — inserir é rotina e grava direto, **alterar** um código que o cliente já recebeu para no modal e o código antigo sobrevive ao cancelamento, `?id=` inválido diz "não encontrado" e esconde todo card em vez de abrir o primeiro pedido, e venda de vitrine diz "Sem vendedor" em vez de deixar o campo vazio. E a divisao **nao se repete na tela**: a linha do volume mostra o codigo UMA vez — chip quando parada, campo quando em edicao — porque antes a coluna do codigo e a de acao traziam o mesmo numero lado a lado | 91 |

Total: **2.217 asserções** sob selo, medidas na rodada completa de 07/out/2026, em 22 suítes.

### O contador estava errado nas duas direções (06/out/2026)

A contagem automática do `selo.py` publicava **3.906**. Ela errava duas coisas ao mesmo tempo:

- **Dobrava quase tudo.** Era `count('  ok   ') + count('  ok ')`, e `'  ok   '` **contém**
  `'  ok '` como substring: cada asserção entrava duas vezes.
- **Zerava quem não imprime linha de `ok`.** O `teste_esc_dropdown` só imprime `FALHA` e declara
  o próprio total numa linha de resumo — entrava como **0** tendo 156.

O número publicado era o saldo líquido dos dois erros, ou seja, não media nada. Agora quem
declara o próprio total manda, e o resto tem as linhas de `ok` contadas **uma vez**.

**A prova de que o conserto está certo veio da própria tabela acima.** Os números contados à mão
antes do contador automático existir voltaram a bater **exatamente**: `teste_cp` 53, `teste_cpd`
68, `teste_caixa` 54, `teste_lanc` 44, `teste_integra` 14, `teste_mais_acoes` 132,
`teste_recibo_clone` 30, e `teste_datas` + `teste_pos` somando os 24 de sempre. Já os registrados
**depois** — `teste_pedidos` com 256 e `teste_receber` com 116 — eram exatamente o dobro do real
(128 e 61) e foram corrigidos na tabela. **Lição: número automático só substitui número à mão
depois de concordar com ele.** Trocar sem conferir foi o que escondeu o defeito por dias.

**Limitação conhecida:** o `teste_dropdown_todas` declara só **2**, porque imprime um resumo
próprio (`telas com dropdown testadas: N de M`) e linha de `ok` apenas para a sub-checagem do
toggle de tema — as 41 telas que ele varre não aparecem na conta. Suíte que faz trabalho por tela
deveria **declarar o próprio total**, como a do Esc faz; enquanto não declarar, ela está
subrepresentada aqui.

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
