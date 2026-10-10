# Ferramentas de verificação — ERP Desk Company

Scripts que conferem as telas. **Não são parte do sistema** — nenhuma tela depende deles, e apagar esta pasta não quebra nada. Eles existem para que uma sessão nova não precise reescrever a verificação do zero.

Criados em 23/set/2026, junto com Contas a Pagar. Apertados em 28/set/2026, na revisão completa da pasta.

## ONDE MORA CADA TELA — `localiza.py` (08/out/2026)

Até 08/out as 71 telas ficavam soltas na raiz do projeto, e cada suíte achava a sua do jeito que
quis: `glob('pagina-*.html')`, `os.path.abspath('pagina-x.html')`, `'file://' + PASTA + '/' + nome`,
`URL + 'pagina-x.html'`. Eram sete formas para a mesma pergunta. No dia em que as telas foram para
`telas/<módulo>/`, as sete quebraram juntas.

Agora a pergunta tem um dono só. O nome do arquivo continua único no sistema, então a suíte cita a
tela pelo **nome** e o `localiza.py` responde onde ela está:

| chamada | devolve |
|---|---|
| `localiza.caminhos()` | caminho absoluto de todas as telas, na ordem alfabética do nome |
| `localiza.nomes()` | só os nomes, na mesma ordem |
| `localiza.onde('pagina-x.html')` | caminho no disco. **Falha alto** se a tela não existe |
| `localiza.uri('pagina-x.html?id=3')` | endereço `file://` para o navegador, com a query |
| `localiza.http('pagina-x.html')` | endereço no servidor de preview |
| `localiza.nome(href)` | de um `href`, `data-href` ou URL, só o arquivo e a query |
| `localiza.resolve(href, de)` | para onde um link relativo aponta, a partir da tela `de` |
| `localiza.espelho_plano()` | cópia das telas numa pasta única, para a auditoria oficial |

**Três coisas que a mudança ensinou, e que valem para a próxima suíte:**

- **Comparar `href` com o nome da tela não funciona mais.** O link agora é
  `../vendas/pagina-vendas-metas.html`. Quem quer saber "o item do menu leva a esta tela" compara
  `localiza.nome(href)`. A pasta é conferida por quem navega de verdade e pela checagem de que
  todo destino existe (`teste_menu.py`, seção 5).
- **Lista de telas vinda do disco é caminho, não nome.** `arq == 'pagina-molde-referencia.html'`
  virava falso calado quando `arq` passou a ser caminho absoluto. Se o código compara, imprime ou
  monta mensagem, itere `localiza.nomes()` e abra com `localiza.onde(nome)`.
- **A auditoria oficial audita ZERO arquivos e diz "tudo limpo"** quando recebe uma pasta em que
  as telas estão em subpastas. Provado em 08/out: apontada para `telas/`, saiu verde sem abrir
  nada. Por isso o selo entrega a ela o espelho plano **e** exige que a saída diga quantos
  arquivos viu. Verde sem contagem não é verde.

O servidor (`servidor.js`) entrega `telas/`, então o endereço é `/<pasta>/<arquivo>`. O endereço
antigo, sem pasta, redireciona — de verdade, com 302, porque os links de uma tela são relativos à
pasta dela e só resolvem certo se o navegador souber em que pasta está.

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
| `alvos.py` ou `localiza.py` mudou | **todas** as suítes rodam — o filtro decide o que elas veem, e o localizador decide ONDE elas olham |

```bash
python3 selo.py                 # o que está selado e o que precisa rodar
python3 selo.py --rodar         # roda só o que precisa, e sela o que passar
python3 selo.py --rodar --tudo  # ignora o selo, roda tudo
python3 selo.py --selar         # sela o estado atual sem rodar (só depois de uma rodada verde na mão)
```

**Medido em 30/set:** mexer em uma tela de detalhe acordou 8 suítes e deixou 7 seladas; as que varrem a pasta rodaram em **1 tela em vez de 54**. A rodada inteira leva ~7 min; a seletiva, 18 s.

### A cobertura sai do código, não de uma lista escrita à mão

Lista escrita à mão envelhece — foi ela que fez "8 telas com o problema" virar 23 sem ninguém perceber. O `selo.py` lê a cobertura **da própria suíte**: os nomes de `pagina-*.html` que ela cita, ou "a pasta toda" quando ela pede `localiza.caminhos()` ou `localiza.nomes()` (até 08/out o sinal era um `glob`).

**E isso foi provado por observação, não por leitura.** Cada suíte foi rodada com o `Page.goto` do Playwright instrumentado, registrando as telas que ela realmente abriu, e o resultado comparado com a cobertura declarada: **nenhuma suíte abre tela fora da sua cobertura**. Algumas cobrem mais do que abrem (o `teste_menu` lê as 54 como texto, o `teste_integra` chega no Caixa por clique e não por `goto`) — e essa é a direção segura do erro: cobrir demais custa uma rodada a mais, cobrir de menos é selo mentiroso. **Repetir essa prova sempre que uma suíte nova entrar.** Feito em 30/set para o `teste_pedidos.py`: cobertura declarada e telas realmente abertas deram **exatamente as mesmas duas** — nenhuma fora, nenhuma coberta sem abrir.

### O que o selo NÃO cobre

Ele não olha para o `varredura_cliques.py` (é ferramenta de fechamento de módulo, roda sob demanda) nem julga se a suíte *testa a coisa certa* — só se o que ela testa continua igual. Suíte que nasceu fraca continua fraca, selada ou não.

## Como rodar

Os scripts acham a pasta sozinhos (sobem um nível a partir daqui) e acham o navegador sozinhos. Rodando de dentro desta pasta:

```bash
# auditoria estática de um arquivo (ou de vários)
python3 auditoria.py ../telas/financas/pagina-financas-contas-pagar.html

# a pasta inteira — uma chamada só, com o total no fim
python3 auditoria.py ../telas/*/pagina-*.html

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
| `teste_menu.py` | o menu lateral navega de verdade entre as telas. Desde 08/out guarda tambem duas regras do sistema inteiro: nenhuma classe de botao sublinha quando vira link (secao 6), e **todo link entre telas diz a pasta, e a pasta tem a tela dentro** (secao 7, estatica, cobre as 3.360 citacoes e as fontes). As duas provadas nos dois sentidos. A secao 8 (08/out) cobra que toda tela de Configuracoes tenha cartao com destino no hub, e que o modulo Operacional, apagado do menu, nao volte numa tela copiada. A secao 9 (09/out) cobra que toda tela marque no menu lateral o modulo da propria pasta, e so ele: Pedidos de Venda marcava Estoque. A secao 10 (09/out) confere os numeros do `PROGRESSO.md` (itens de menu com tela, percentual e total de telas) contra o proprio sistema | 22 |
| `teste_datas.py` · `teste_pos.py` | o componente de data e o posicionamento do calendário. Desde 09/out abre toda tela que tem campo de data e cobra as três peças (campo, botão e caixa): o CRM nasceu sem a caixa e o botão não abria nada | 25 |
| `teste_dropdown_todas.py` | clica no dropdown das **54 telas**: abre, escolhe, fecha — e, desde 02/out, confere com `elementFromPoint` que o menu **aparece de verdade**, não só no DOM (ver abaixo) | 54 telas |
| `teste_confirma_senha.py` | **(28/set)** modal de confirmação em **todas** as telas que carregam o bloco de senha — descobertas pelo próprio script, sem lista fixa: a trava trava, o Esc fecha, o "estou ciente" aparece com 2+, a ação entra no registro, e o despacho entrega o callback nas **três assinaturas** | 1025 |
| `teste_mais_acoes.py` | **(28/set)** o menu "Mais ações": id, rótulo e estilo únicos, abre no clique, **fecha mutuamente** com os outros dropdowns, e a ação destrutiva está **dentro** dele com `item-perigo`. Em 09/out entrou o PDV, cujo menu trocava o rótulo pelo item clicado, e a tela do assunto do CRM | 159 |
| `teste_esc_dropdown.py` | **(28/set)** Esc fecha o dropdown aberto em todas as telas — e, sem dropdown aberto, continua fechando o modal | 192 |
| `teste_recibo_clone.py` | **(29/set)** clonar conta (copia a despesa, não a data) e imprimir recibo (travado sem baixa, valor por extenso com a regra do "e") | 30 |
| `teste_receber.py` | **(02/out)** Contas a Receber, listagem e página da conta — o que ele protege é o que separa o **receber** do **pagar**, que é o que um clone apaga em silêncio: a conta nasce do pedido e a Origem leva até ele; Valor, Líquido, Saldo e Recebido são quatro números diferentes; a **taxa retida quita o título sem entrar no Caixa**; **baixa é entrada e estorno é saída** (o clone trouxe invertido); recibo e duplicata têm travas **inversas**; o pedido define as parcelas e a sobra dos centavos fica na primeira; e cliente com conta vencida não compra de novo | 61 |
| `localiza.py` | **(08/out)** o único lugar que sabe em que pasta cada tela mora. Ver a seção no topo | — |
| `selo.py` · `alvos.py` | **(30/set)** o selo acima: decide o que roda e o que pula, e restringe as suítes que varrem a pasta às telas que mudaram (`DESK_ALVOS`) | — |
| `teste_becos.py` | **(29/set, noite)** nenhuma tela diz que outra tela "ainda não existe" ou que "a navegação só funciona no Lovable" (varre as 54); 20 botões levam ao destino certo; `?receber=1`, `?clonar=1` e `?nota=` chegam certos; os 5 cadastros abrem em edição pelo Incluir e pelo Editar, e em leitura (ou conforme a preferência) na consulta; a senha fica no modal que **exclui**, nunca no aviso de que nada pode ser excluído (OC, Depósitos, Endereços); cancelar OC recebida pede senha; competência em massa no Caixa; hub sem marcadores | 136 |
| `teste_pedidos.py` | **(30/set)** Pedidos de Venda, listagem e página do pedido — o que ele protege são as **decisões da barganha de 30/set**, não o desenho: as 11 abas cabem numa linha só e o que sobra vai para "mais"; contador e rodapé contam a mesma coisa e o cancelado fica fora do total; a reserva nasce com o pedido e volta no cancelamento; pedido expedido não se exclui; pedido sem saldo não nasce, e a mensagem diz **quanto existe**; os dois níveis de desconto, cada um na sua base; a loja escolhe o depósito; cadastro rápido nasce incompleto; comissão liberada no faturamento; campos fiscais visíveis e desabilitados. **(02/out)** mais 6 seções: o funil anda um passo por vez na ordem certa e termina em Entregue; avançar NÃO pede senha e alterar situação à mão PEDE; clonar abre o pedido preenchido com a data de hoje; os painéis de últimas vendas e de limite de crédito abrem sem sair do pedido; o limite bloqueia em boleto e deixa passar em Pix; e nenhum item do menu voltou a ser promessa vazia. **(02/out, noite)** situação virou filtro suspenso: as 10 opções abrem todas visíveis, os contadores acompanham os outros filtros, e devolução não é mais situação de pedido | 128 |

| `teste_rastreamento.py` | **(07/out)** Rastreamento de Pedidos — o que ele protege são as **quatro barganhas de 07/out**, não o desenho: pagamento é eixo SEPARADO (prova que existe pedido enviado e não pago, e pago e não enviado); o código é por VOLUME; cada evento carrega o marcador de quem o vê e o rótulo do cliente (Faturado é interno, Conferência de saída vira "Pedido embalado"); e a previsão é CONGELADA — o teste muda o prazo da transportadora para 99 e confirma que a previsão de quem já saiu não se move. Mais: a tabela cabe no card a 1440px, Esc fecha o painel, o dropdown aparece de verdade e as 4 ações entram no catálogo de senhas. **A partir de 07/out também guarda a divisão de quem escreve:** a listagem só lê (nenhum `data-confirmar`, nenhum `data-alterar` no painel) e o **detalhe** é a única tela que grava — inserir é rotina e grava direto, **alterar** um código que o cliente já recebeu para no modal e o código antigo sobrevive ao cancelamento, `?id=` inválido diz "não encontrado" e esconde todo card em vez de abrir o primeiro pedido, e venda de vitrine diz "Sem vendedor" em vez de deixar o campo vazio. E a divisao **nao se repete na tela**: a linha do volume mostra o codigo UMA vez — chip quando parada, campo quando em edicao — porque antes a coluna do codigo e a de acao traziam o mesmo numero lado a lado. Guarda também a revisão de 07/out em que a **nota fiscal deixou de ser interna** (nenhum passo do funil fica escondido; o marcador "só interno" passou a viver na NOTA de operação) e a **previsão por volume**: cada caixa tem a sua, a do pedido é a mais distante delas, alterar exige senha e gera **um** evento público por salvada — não um por caixa. A [26] cobre o caminho do **calendário** (a [23] e a [24] digitam), que era o único sem teste e foi exatamente onde o bug apareceu | 127 |

| `teste_motivos_devolucao.py` | **(07/out)** Operacional → Motivos de Devolução. Nasceu **antes** da tela de Devolução usar o cadastro, de propósito: campo que aponta para cadastro inexistente já custou caro duas vezes aqui. Guarda que o motivo diz **de quem é a conta** (os quatro responsáveis existem e nenhum motivo aponta para fora); que ele **sugere o destino no estoque** nos três casos reais, extravio inclusive (mercadoria que não volta); que destino que mexe no estoque **avisa antes de salvar**, e trocar de aviso esconde o anterior em vez de empilhar; que nome repetido é barrado mesmo com outra caixa; que **excluir avisa que inativar guarda a história**; e que a trava nasce com a tela — nos três verbos e nas telas que **leem** o catálogo, não só na que o usa | 40 |

| `teste_devolucao.py` | **(07/out)** Devolução de venda, listagem e documento. Protege as **quatro decisões barganhadas**: a volta ao estoque é **ação explícita** (e o saldo sobe uma vez só, não a cada salvada); o estado da mercadoria é **por item**, na linha, porque a mesma devolução mistura revendável e avaria; o código da reversa mora **aqui**, não no Rastreamento; e **Vale-troca** aparece visível e desabilitado enquanto o submódulo não existe — opção que não funciona e não se explica é pior que opção ausente. Mais: devolução é **documento próprio** e aponta para o pedido (não é situação de pedido, decisão de 02/out); a listagem só lê e o detalhe escreve; devolver mais do que foi vendido é barrado; motivo que **exige descrição** não salva sem ela; finalizar com estoque pendente é barrado e cancelar depois de lançar o estoque também; `?venda=` nasce com tudo o que foi vendido; a nota de devolução fica reservada; os dois parâmetros nasceram **no mesmo dia** em Configurações e a tela obedece a eles de verdade (depósito e prazo lidos do que foi salvo, não do padrão); e `origem` já nasce no modelo, antes do Help Desk existir A **[22]** (08/out) escolhe uma opção em cada um dos três filtros da listagem e aperta "Limpar filtros": eles davam erro de JS antes de filtrar, e nenhuma seção os tocava. Provada nos dois sentidos | 145 |

| `teste_rodape.py` | **(08/out)** O rodapé de salvar, varrendo a pasta inteira — tela nova entra na conta sem ninguém lembrar. Nasceu de uma observação do usuário sobre **alinhamento de botão** e acabou em três bugs. Guarda que os quatro nomes do componente viraram **um** (`.form-footer-bar`, `.par-barra`, `.par-barra-nota` e `.form-actions` como rodapé de página estão mortos, e a [1] reprova se voltarem) — o preço de ter mais de um já tinha sido cobrado em Pedidos de Venda, onde o CSS foi renomeado e o HTML não, deixando a barra sem estilo nenhum em modo de edição; que o botão encosta na esquerda e a nota na direita; que a nota **conta** em vez de adjetivar e nunca fica vazia; e que sair com alteração pendente **para e pergunta** em vez de levar embora o que não foi salvo — era isso que o antigo "Cancelar" fazia, calado, num `<a href>`. A [3] é a que pega o bug silencioso: a referência da nota medida **antes de a tela se montar** congela um formulário vazio, e aí a nota diz "nenhuma alteração pendente" por ter parado de olhar. Com o defeito reinjetado, a asserção óbvia continua verde e só a [3] reprova | 547 |

| `teste_nomes_sistema.py` | **(08/out)** Configurações → Nomes do sistema. O sistema tinha **28 conjuntos de rótulos escritos no código**; lista que CRESCE (motivos, depósitos) já era cadastro, e o problema eram as listas FECHADAS, em que cada entrada dispara um comportamento — `revendavel` segue a regra de entrada, `avaria` bloqueia o saldo. Elas não podem virar cadastro: um quarto estado inventado não teria código que o entendesse. A saída foi separar **chave** de **rótulo**, e a suíte guarda as duas metades dessa promessa. A que importa mais é a **[7]**: depois de renomear, a chave e o destino no estoque continuam exatamente os mesmos — renomear muda o que aparece, não o que o sistema faz. Mais: o rótulo novo chega em **todas** as telas que o mostram, não só na que foi editada [6][8]; o nome interno fica à vista ao lado do campo [2]; dois rótulos iguais no mesmo grupo são barrados antes de salvar [4], senão a pessoa escolhe entre opções idênticas sem saber qual faz o quê; e renomear **pede senha** [5] | 19 |

| `teste_motivos_perda.py` | **(08/out)** Operacional → Motivos de Perda. O item já existia no menu de Estoque, em Acerto e Inventário, **apontando para lugar nenhum** — e os motivos viviam escritos no código do Acerto, com um campo que **não é rótulo**: `fiscal` decide se a baixa exige NF-e própria (CFOP 5.927, com estorno do crédito), se resolve com documento interno, ou se depende da diferença. Motivo sem cadastro é regra fiscal sem dono. A suíte guarda que movimento é eixo de verdade (furto não serve para entrada), que tratamento com obrigação **avisa antes de salvar** e trocar de aviso esconde o anterior, que nome repetido é barrado mesmo com outra caixa, e que a trava nasce com a tela. A **[8] é a que justifica o cadastro existir**: compara o que o cadastro diz com o que o Acerto oferece, código a código e tratamento a tratamento. Provada nos dois sentidos — mudar o "Furto ou roubo" para `interno` só no Acerto faz ela reprovar | 48 |

| `teste_metas.py` | **(08/out)** Vendas → Metas e Performance de Vendas. Metas era um formulário solto e virou listagem com painel lateral: a listagem lê, o painel escreve. A suíte guarda os dois níveis (loja e vendedor), o ritmo por **dias corridos**, que "abaixo do ritmo" só existe no mês corrente, o aviso de diferença entre a meta da loja e a soma dos vendedores, os quatro modos de definir (mensal, trimestral, anual, progressivo) com a prévia do que será gravado, e que alterar meta de mês fechado **pede senha**. A **[9] é a que justifica as duas telas serem refeitas juntas**: compara o bloco de dados e o texto de `situacaoDaMeta` entre Metas e Performance. Performance tinha a sua própria cópia dos números e podia discordar calada. Provada nos dois sentidos — mudar uma meta só em Performance faz ela reprovar. A **[12]** guarda o link que sai de Performance: "Definir meta" chega em Metas com o painel aberto naquela loja e naquele mês | 74 |

| `teste_formas_recebimento.py` | **(08/out)** Configurações → Formas de recebimento. A lista de formas vivia escrita no código de cinco telas, e a regra "esta forma valida o limite de crédito" morava dentro do Pedido de Venda, com um comentário prometendo sair dali quando o cadastro existisse. A suíte guarda que cada linha diz o que a forma **decide** (para que vale, se vira título ou entra direto na conta, a taxa), que campo que não se aplica some (forma que só paga não mostra destino, taxa nem limite), que forma do sistema desabilita mas não exclui nem renomeia, e que **mexer em regra de dinheiro pede senha** enquanto incluir e renomear seguem a matriz do módulo. A **[12] é a que justifica o cadastro existir**: Contas a Receber e Contas a Pagar oferecem as mesmas formas do cadastro, e o Pedido valida limite nas mesmas formas que o cadastro manda. Provada nos dois sentidos — desligar a validação do boleto só no Pedido faz ela reprovar. O link de excluir aparece em toda forma; nas do sistema ele explica por que não pode, em vez de sumir. **(09/out)** Seção 8b: forma com **prazo fixo da operadora** guarda dias úteis, parcelas, taxa por parcela e repasse; sem prazo fixo esses campos somem, prazo fora de 0 a 60 e taxa que não é número são barrados, repasse com taxa de 100% também, e ligar o repasse pede senha. O cartão de crédito **não valida mais limite** | 122 |

| `teste_pdv.py` | **(09/out)** Vendas → PDV e Configurações → Configurações do PDV. Guarda as três decisões do usuário (a venda vira Pedido de Venda já entregue, a loja é escolhida ao abrir o caixa, o ciclo entra inteiro) e o que vem delas: caixa fechado não vende e o turno sobrevive ao F5; a busca só acha produto da loja do turno, o leitor entra por código exato, a quantidade segue a unidade e o bloqueio de estoque diz os números; desconto no limite passa e acima dele **pede senha**, no item e na venda inteira; as formas oferecidas são as do cadastro, forma que vira título **exige cliente** e a que valida limite barra com os quatro números; o recibo para troca sai **sem nenhum valor**. O turno é o que mais importa: com o **fechamento cego**, Detalhes do caixa não mostra o esperado, contagem que não bate diz em qual forma e nunca quanto era, sangria maior que a gaveta barra sem revelar o saldo, e fechar com diferença pede senha. A **[9]** compara os sete espelhos do PDV com o cadastro de origem, campo a campo, e a **[10]** confere que os nove parâmetros existem nas duas telas e que o PDV obedece ao que foi salvo. Provada nos dois sentidos em quatro regras: mostrar o esperado com o caixa aberto, mudar a taxa do cartão só no PDV, parar de conferir o limite e desligar o bloqueio de estoque fazem ela reprovar. As duas abas da suíte usam **o mesmo contexto** do navegador: `nav.new_page()` abre um contexto isolado a cada chamada, e o que uma tela salva não chega à outra. Também cobra que o cadastro de Categorias financeiras **não tenha id repetido** (tinha dois com 21, e excluir o segundo apagava o primeiro). **Segunda rodada de 09/out, depois do teste do usuário:** cartão sem campo de dia nem de parcela de título, vencendo no **próximo dia útil** (sexta 09/10 cai na terça 13/10, porque 12/10 é feriado); taxa do parcelado vinda da **tabela de parcelas**; **repasse** dividindo por (1 − taxa), com o acréscimo no resumo, no recibo, no total e no esperado do fechamento; cartão **fora do limite de crédito**; o que falta receber **entra sozinho** na forma sem valor digitado, e a digitada não é mexida; "Mais ações" continua com esse nome depois de usado e Fechar caixa é botão próprio; Detalhes do caixa largo, com fatos, tabelas, recibo por venda e, no cego, formas e contagem de vendas sem valor. Seis regras novas provadas nos dois sentidos. **Terceira rodada de 09/out:** painel "Editar produto" no desenho do print (código, saldo, preço do cadastro, desconto e acréscimo em botões de opção, campo em branco como "sem ajuste", Ctrl+Enter aplica, Remover tira só aquele item); Sangria e Fechar caixa como botões do topo, o segundo na cor de perigo; e o submenu do menu lateral **por cima** da barra do PDV. Por fim, **cartão passa sem cliente identificado** (o título nasce a receber da operadora) e boleto continua pedindo cliente | 198 |
| `teste_crm.py` | **(09/out)** Vendas → CRM (lista e tela do assunto), Configurações → Estágios do funil de vendas e Configurações do CRM, e o status do contato em Cadastros → Clientes. Guarda as quatro decisões do usuário: o status do contato **mora no cadastro de Clientes**; encerrar **pede ganho ou perdido**, e perdido pede motivo; ação pendente **com data** de assunto aberto vira **aviso na Agenda**, e concluir ou arquivar tira o aviso; quadro por estágio, WhatsApp e e-mail (o link aberto é conferido letra a letra) e proposta. Cobra também a ordem da lista, os filtros, a seleção com senha para excluir, o formulário de ação (texto, data que não existe, horário, campo que some), a edição pelo painel "Ação do CRM", o parâmetro de dias sem interação nas três telas, a reordenação dos estágios com o último preso no fim, e os **espelhos**: estágios, clientes, vendedores, pedidos e contas em aberto contra o cadastro de origem. Provada nos dois sentidos em sete regras. Foi ela que achou a chave de armazenamento sem declarar: nada era gravado e nenhuma tela reclamava. No mesmo dia ganhou o calendário que abre e escolhe o dia, o horário pelas setas, o Esc que fecha só a caixa e o cartão do quadro sem texto vazando, no pior caso e em 1280. A seção 18 cobra o relógio na Agenda: o mesmo componente da tela do assunto, e horário que não existe não salva | 167 |
| `teste_bloqueados.py` | **(09/out)** Estoque → Itens Bloqueados, o tipo Bloqueio no lançamento do Controle de Estoques e o bloqueio da falta na Separação e na Conferência de Saída. Guarda as duas decisões do usuário: **a falta bloqueia a unidade** (não é baixa, o físico não muda) e **o que não é avaria fica no próprio endereço**. Cobra o painel de resolver nas três abas: a quantidade repartida entre liberar e dar baixa numa confirmação só (vale a senha mais exigente), o retrato do estoque hoje e depois, a causa obrigatória ao liberar uma falta, a baixa com motivo e aviso fiscal, a unidade fracionável, o destino de quem não tem base de picking, manter bloqueado com anotação ou motivo corrigido, e o histórico da linha. Cobra o bloqueio feito na própria fila: a busca padrão de produto (nome, SKU e GTIN), o saldo livre descontado do que a fila travou, os limites de quantidade, a observação obrigatória para travar por decisão e o endereço de Avaria. E ainda o que sobrevive ao F5, a caixa de entrada que não repete o mesmo caso nem aceita caso torto, e os **espelhos**: motivos de baixa contra o Acerto, produtos, saldo por endereço e bases contra o Controle de Estoques, a avaria sem endereço contra o Endereçamento e a falta contra a Conferência. Provada nos dois sentidos em vinte e sete regras. No fechamento ganhou a opção "Todos os endereços": só aparece com mais de um endereço livre, reparte começando pelo picking e cria uma linha por endereço | 160 |

Total: **4.021 asserções** sob selo, medidas em 09/out/2026 (com o PDV, o CRM e Itens Bloqueados), em 32 suítes.

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
python3 varredura_cliques.py            # todas as telas, menos o molde
python3 varredura_cliques.py - estoque  # só as que têm "estoque" no nome
```

Rodar **antes de dar um módulo por pronto** e depois de qualquer mudança no bloco compartilhado. Em 29/set: 1.605 cliques em 52 telas, FALHAS: 0. Em 30/set, com Pedidos de Venda: **1.676 cliques em 54 telas, FALHAS: 0**.

**Em 08/out/2026, depois da mudança das telas para `telas/<módulo>/`: 2.362 cliques em 70 telas, nenhuma navegação para arquivo inexistente** — e 20 erros de JavaScript, todos numa tela só. Os três filtros da listagem de Devolução (responsável, motivo, forma) chamavam `setDropdownValor`, que a tela nunca definiu: o clique dava erro antes de filtrar. Corrigido, e coberto pela seção 22 de `teste_devolucao.py`.

**A varredura quebrou no fim, no Windows.** Em 08/out ela clicou tudo por 10 minutos e quebrou na última linha, ao gravar o JSON: `open(SAIDA, 'w')` sem `encoding` usa cp1252 no Windows, e bastava um texto de tela com seta (→) para derrubar a gravação. O relatório não saiu. Não sei desde quando isso acontecia: o defeito só dispara quando algum controle tem caractere fora do cp1252. **Ferramenta que não termina não acha nada, e o silêncio dela parece aprovação.** Corrigido com `encoding='utf-8'`.

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
