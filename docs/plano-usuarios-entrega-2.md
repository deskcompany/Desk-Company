# Usuários do sistema e Permissões de usuários — entrega 2: o código de autorização e o pacote do gerente

Plano da entrega 2. Decidido pelo agente principal em 11/nov/2026, a partir do que o usuário
aprovou na barganha de 10/nov (PROGRESSO.md, "Decidido"). O executor **implementa**: não decide
produto, não redesenha, não abre escopo novo.

## Onde está hoje (leitura, nãoPlanner)

- `telas/configuracoes/pagina-configuracoes-usuarios.html`, `...-usuarios-detalhe.html`,
  `...-perfis-usuario.html`, `...-perfis-usuario-detalhe.html`: entrega 1 (11/nov).
- `telas/cadastros/pagina-cadastros-vendedores-detalhe.html`: a aba "Acesso e Permissões"
  mostra o usuário vinculado; a aba "Confirmações por senha" (`PODE_CONFIRMAR`) e
  `PODE_NA_HORA_IDS` ainda são mocadas.
- 95 telas têm o bloco compartilhado da senha (`exigeSenha`, `confirmarAcao`, `travaSenhaModal`,
  `registrarLog`) e o markup `<div class="confirm-senha-row" id="campoSenhaModal">` com o
  rótulo "Sua senha" (idêntico nas 95) e o erro "Informe sua senha para confirmar esta
  exclusão." (69) / "…esta ação." (26).
- 29 telas já têm `promocaoNaHora` no catálogo (as do catálogo completo); as outras 66 têm só
  as ações de módulo.
- Blocos de dados: `PERMISSOES: O CATALOGO` (4 telas de usuários), `USUARIOS E PERFIS: DADOS E
  LEITURA` (4 telas de usuários + a do vendedor), `PROMOCOES: NA VENDA` (PDV e Pedido de Venda).

## Decisão 1 — o código de autorização no lugar da senha mocada (todas as telas)

**O que muda:** o modal de confirmação passa a pedir o **código de autorização** de quem
autoriza, em vez de uma senha qualquer. O sistema passa a saber **quem** autorizou.

- Novo bloco comum `AUTORIZACAO: O CODIGO`, **idêntico nas 95 telas** que têm o envelope da
  senha. Inserção: imediatamente **antes** da linha `// ===== REGISTRO DE ATIVIDADES =====`
  (esse marcador existe nas 95 — use-o como âncora). Leitura e gravação de arquivo em modo
  binário/texto com `newline=''` (a regra do §14.109: script em massa não troca CRLF por LF).
- O bloco **não** repete o `PERMISSOES: O CATALOGO` (que fica nas 4 telas de usuários). Ele
  guarda só o que a autorização precisa:
  - `autoHash(texto, sal)`: **a mesma** FNV-1a de 32 bits do `upHash` (prefixo `fnv1a:`, 8 hex),
    com o sal do jeito que o produto grava: `upHash(novo, 'codigo|' + U.login)`. **O sal é
    `'codigo|' + login`** — o mesmo `upHash` calcula `sal + '|' + texto`, ou seja
    `'codigo|administrador@desk|1234'`. Nome novo (`autoHash`), para não colidir com `upHash` nas 5 telas
    que já têm o bloco `USUARIOS E PERFIS`.
  - `autoUsuarios()` / `autoPerfis()`: leem `deskUsuarios` e `deskPerfis` do navegador; se
    não houver nada gravado, usam a **fábrica** (a mesma da entrega 1, ver abaixo). O Owner
    nunca vem do armazenamento: o que estiver gravado para o perfil 1 é ignorado e ele volta
    como de fábrica (`perms: ['*']`, sem limite de desconto).
  - `autoAutorizado(codigo, acaoChave)`: devolve `{ ok, usuario, mensagem }`.
    1. O código precisa ter de 4 a 6 números (só números).
    2. Acha o usuário **ativo**, com código definido, cujo `codigoHash` bate com
       `autoHash(codigo, 'codigo|' + usuario.login)`.
    3. Esse usuário precisa ter a ação na permissão efetiva (perfil + avulsas). A ação está
       liberada quando as permissões efetivas têm `'*'` (Owner), `'@' + acaoChave` (avulsa
       exata) ou `'@grupo:' + grupoDaAcao`, onde `grupoDaAcao` é o `grupo` da ação no
       `ACOES_SENHA` **da tela onde o código está sendo pedido**. **`modulo:` NÃO concede
       ação** — como na grade de Permissões, `modulo:` dá acesso às telas do módulo e as ações
       vêm de `@grupo:` (é assim que o perfil Gerente libera ação: `@grupo:Vendas` etc.).
       Ação que não existe no `ACOES_SENHA` da tela não tem grupo: só `'*'` ou `'@chave'`.
    4. `ok: true` devolve o usuário (o log passa a guardar **quem** autorizou).
  - **Não existe o atalho "sem usuário nenhum cadastrado"**: o bloco traz a fábrica, e o
    `localStorage` vazio cai nela — sempre há alguém. O caminho "aceita qualquer código" é
    código morto e não se implementa.
- **A fábrica dentro do bloco:** os 7 usuários e os 6 perfis da entrega 1, com os mesmos
  campos. Cuidado com os hashes: a entrega 1 gravou *placeholders* (`'fnv1a:1c2f8a90'`), que
  ninguém pode digitar. **Troque pelos hashes reais dos códigos de exemplo**, calculados com
  a mesma FNV-1a e o sal `'codigo|' + login` (ver `autoHash` acima):
  - Administrador Desk (Owner, perfil 1) — código **1234** → `fnv1a:805464f4`
  - Carlos Mendes (Gerente, perfil 2) — código **2468** → `fnv1a:29085c4f`
  - Marina Costa (Supervisor, perfil 3) — código **3456** → `fnv1a:35a61599`
  - Ana Souza (Vendedor interno, perfil 4) — código **4567** → `fnv1a:fe7ed2a1`
  - Rafael Andrade (Representante externo, perfil 6) — código **5678** → `fnv1a:10e9bbf5`.
    Ele está **bloqueado**, então não autoriza mesmo.
  - **Bianca Furtado e Fernanda Lima continuam sem código** (`codigoHash: null`). São os dois
    que a entrega 1 já deixou sem código, e é o que o painel de Usuários mostra
    ("Sem código de autorização: 2" e a lista de quem é). **Rafael Andrade tem código e
    está bloqueado** — não confundir: "sem código" e "bloqueado" são coisas diferentes.
  Os códigos de exemplo são dado de exemplo (§14.73): registre-os no HISTORICO.md e no
  PROGRESSO.md ("para testar: 1234 do Administrador Desk, 2468 do Carlos Mendes").
- **A fábrica da entrega 1** (`UP_USUARIOS_FABRICA` / `UP_PERFIS_FABRICA`, nas 5 telas que têm
  `USUARIOS E PERFIS`) **precisa ficar igual** à do bloco novo, nos campos que importam
  (id, nome, login, situacao, perfilId, perms, descontoPct, vendedorId, codigoHash) — e os
  `codigoHash` placeholder de lá também viram os hashes reais, senão as duas fábricas
  divergem. A suíte compara as duas fábricas; se divergirem, o selo reprova.
- **O modal (markup das 95 telas):** o rótulo "Sua senha" vira **"Código de autorização"**; o
  placeholder "Informe sua senha para confirmar" vira **"Informe o código de quem autoriza"**;
  o texto de erro ("Informe sua senha para confirmar esta exclusão." / "…esta ação.") vira
  ("Informe o código de autorização para confirmar esta exclusão." / "…esta ação."). O campo
  continua sendo `type="password"`, o id continua `inputSenhaModal` e o container
  `campoSenhaModal` (a regra dos ids continua valendo: o `id` não muda).
- **A trava (fase de captura), dentro do envelope da senha:** hoje o bloco só exige que o
  campo não esteja vazio. Passa a exigir o código:
  - ação sem senha → segue direto (não pede nada);
  - ação com senha → o código é conferido por `autoAutorizado(codigo, acao)`. Se `ok`, a ação
    acontece e o registro de atividades guarda `autorizadoPor: <nome do usuário>`;
  - se não `ok`, o modal **não fecha**, o campo ganha o estado de erro e a mensagem é a do
    `autoAutorizado` ("Código inválido." / "Esse código não libera esta ação."), e a ação
    **não** acontece nem é registrada.
- **O registro de atividades:** `registrarLog` passa a gravar `autorizadoPor` (o nome de quem
  autorizou) quando houver. O `senha: true` continua (é a trava), mas o nome do campo na tela
  do Registro de atividades passa a mostrar **quem autorizou** quando houver.
- **A ação nova no catálogo:** a autorização por código é a ação `authAutoriza`? **Não**:
  **não crie ação nova**. A ação que pede autorização continua sendo a mesma
  (`clientesExclui`, `promocaoAprova`, `pdvDescontoAcima`…): o que muda é **quem** libera
  (o código de quem tem a permissão) e **como** o registro identifica o autorizador.
- **O que NÃO muda:** `exigeSenha` (a trava por ação continua vindo de Configurações →
  Confirmações por senha), a assinatura do `abrirModalConfirmacao` (3 assinaturas no sistema),
  o `confirmarAcao`, o catálogo ACOES_SENHA e a tela de Confirmações por senha.

### As suítes que o código de verdade quebra (achado na auditoria, 12/nov)

Com o código conferido de verdade, **preencher o campo com uma senha qualquer deixa de
autorizar**. São ~42 pontos em 28 arquivos de suíte que hoje preenchem `'senha-de-teste'`,
`'senha'`, `'senha123'`, `'seiasenha'`, `'x'`, `'123456'` e `'1234'`. Sem mexer neles, o selo
reprova em 28 arquivos — e a peça A não fecha.

A troca é pelo **código 1234** (Administrador Desk, perfil Owner, `perms: ['*']` — libera
qualquer ação, inclusive as chaves de teste que não estão no catálogo). Regras:

- o caso em que o teste preenche **vazio** e espera que a ação seja barrada
  (`teste_vale_compra.py`, linha ~149) **continua vazio**;
- `'x'` vira `'1234'` onde o teste espera que a ação **aconteça** (`teste_gateways.py`,
  `teste_vale_uso.py`);
- onde o valor vem de uma variável (`senha`), troca-se a atribuição;
- `teste_confirma_senha.py` usa a chave `'__teste_qa__'`, que não existe no catálogo: o
  código 1234 (Owner) libera, e a asserção do registro (`log.chave == '__teste_qa__'`)
  continua válida.

Nenhum teste pode ser **enfraquecido** para passar: só o valor do código muda.

## Decisão 2 — o limite de desconto por pessoa (PDV e Pedido de Venda)

- **Quem é a pessoa:** o **vendedor da venda** (PDV: `venda.vendedorId`; Pedido de Venda: o
  vendedor do pedido). O usuário do sistema é encontrado pelo `vendedorId` do usuário (o
  vínculo que a entrega 1 já gravou).
  - **Atenção ao espelho (achado na auditoria, 12/nov):** o PDV tem a lista própria
    `VENDEDORES` (ids 1 Marina, 5 Rafael Tenório, 6 Bianca, 2 Ponto, 3 Rafael Andrade) e o
    Pedido tem `VENDEDORES_C` (ids 1, 2, 3). O vínculo com o usuário é pelo **nome do
    vendedor**, não pelo id: `UP_VENDEDORES` (o espelho de Cadastros → Vendedores, ids 1
    Marina, 2 Ponto, 3 Rafael Andrade) é a única lista que casa com o `vendedorId` gravado
    no usuário. Rafael Tenório e Bianca no PDV (ids 5 e 6) **não têm usuário vinculado** —
    caem no limite do sistema, como o texto já diz.
- **O limite:** o **próprio** da pessoa (`descontoPct`), se tiver; senão o do **perfil**; senão
  o de **Configurações → PDV** (`pdvDescontoMaximoPct`, hoje 10%). O **Owner não tem limite**.
  A ordem é a mesma de `upDesconto` da entrega 1, com o parâmetro do PDV como último recurso.
  A tela do vendedor NÃO entra: o vendedor sem usuário cai no `pdvDescontoMaximoPct`.
- **O PDV:** hoje compara com `PARAM.pdvDescontoMaximoPct` em 4 lugares (desconto do item,
  desconto da venda inteira, e as duas mensagens). Passa a comparar com o limite da pessoa.
  A mensagem diz o limite de quem vende ("o máximo sem liberação é 18% (limite de Marina
  Costa)") e, quando o limite é o do sistema, diz isso ("o limite de Configurações → PDV").
- **O Pedido de Venda:** hoje **não tem** limite de desconto. Passa a ter o mesmo (no item e
  na venda), com a mesma mensagem.
- **Quem libera:** continua a ação `pdvDescontoAcima` (agora com código, pela Decisão 1).
  O `PDV` e o `Pedido` passam a ter o mesmo limite e a mesma liberação — inclusive o Pedido,
  que hoje libera qualquer desconto.

## Decisão 3 — o pacote do gerente na promoção

### 3a. "Aplicar preço promocional" fora da promoção só com o gerente

- O **vendedor** é quem pede; quem **libera** é quem tem a ação `promocaoNaHora` na permissão
  efetiva (o perfil Gerente tem `@grupo:Vendas`, que inclui essa ação).
- `PROMO_PODE_NA_HORA = ['Marina Costa']` (mocado, em 3 telas: PDV, Pedido, ficha do vendedor)
  **sai**. No lugar: o bloco `AUTORIZACAO: O CODIGO` diz **quem pode liberar** a ação; a tela
  mostra o nome de quem autorizou depois.
- A ficha do vendedor (Cadastros › Vendedores): a aba "Confirmações por senha"
  (`PODE_CONFIRMAR` / `PODE_NA_HORA_IDS`) **vira** a ponte para o usuário vinculado — a tela
  mostra o que o usuário vinculado tem e o link para a página dele. Não é mais a fonte da
  permissão.
- **Dado de exemplo:** Marina Costa deixa de ter a permissão avulsa `@promocaoNaHora` (ela é
  vendedora; a permissão é do gerente). Carlos Mendes (Gerente) libera pelo `@grupo:Vendas`.
- O **preço mínimo** (trava da calculadora) continua valendo antes da autorização: a ordem é
  mínimo → permissão → código.

### 3b. O botão do gerente no excedente do limite por cliente

- A linha que entrou **pelo preço de venda** por passar do limite por cliente (a que hoje
  carrega a nota "Pelo preço de venda: passou do limite de N por cliente…") ganha o botão
  **"Aplicar preço promocional no excedente"**, no painel do item (PDV) e no painel do item
  (Pedido de Venda). O botão **só aparece** para quem pode liberar a ação `promocaoExcedente`
  (o gerente) — os outros veem a linha e o motivo, sem o botão.
- **A ação nova no catálogo:** `promocaoExcedente` — "Liberar o preço promocional no excedente
  do limite por cliente", grupo Vendas, `pronto: true`, `exigePadrao: true`, `onde: 'Vendas →
  PDV e Pedidos de Venda'`. Ela entra nas **28 telas com o catálogo completo** (junto das
  outras `promocao*`), no mesmo formato delas (o bloco `ACOES_ESPECIFICAS`).
- **O que o gerente informa:** quantas peças recebem o preço promocional (todas as peças da
  linha, ou um número menor). O pedido é feito **com o código de autorização** (a mesma
  captura da Decisão 1).
- **A regra do limite total:** a peça liberada **conta no limite total da promoção** e
  **não passa dele**. Se o limite total já estiver completo, o botão **não aparece** e a
  linha diz por quê ("o limite total da promoção nº 1 já está completo"). O que a peça
  liberada **não** faz é consumir a cota do **cliente** (é uma exceção autorizada): a cota do
  cliente continua valendo para as vendas seguintes.
- **A linha se divide:** N peças pelo preço da promoção (com a marca `excedente` e o nome de
  quem liberou) e o resto pelo preço de venda, com a nota original.
- **O registro de atividades:** "Liberou 2 un. de <produto> no excedente da promoção nº 1,
  por <nome> (Gerente)" — com quem e quantas.
- **O que muda no bloco `PROMOCOES: NA VENDA`** (idêntico no PDV e no Pedido):
  - a contagem do **vendido** distingue a peça de **excedente**: ela conta no **total** da
    promoção e **não** conta na cota do **cliente**. A peça gravada leva a marca
    (`excedente: true`) e o `promoVendido` soma as duas contagens separadamente.
  - a conferência do limite (`promoCabe`) passa a contar as peças de excedente da venda só no
    total, e só as peças normais na cota do cliente.
- **O botão só aparece onde há gerente:** o PDV e o Pedido de Venda são as duas telas da venda
  (as outras telas de promoção não vendem).

## Arquivos

| arquivo | o que muda |
|---|---|
| as 95 telas com o envelope da senha | bloco `AUTORIZACAO: O CODIGO` (antes de `// ===== REGISTRO DE ATIVIDADES =====`), o rótulo/placeholder/erro do modal, a trava da fase de captura, o `registrarLog` com `autorizadoPor` |
| `telas/vendas/pagina-vendas-pdv.html` | limite de desconto por pessoa (4 pontos), o `promoPodeNaHora` pela permissão, o botão do excedente, a marca `excedente` na linha, o registro |
| `telas/vendas/pagina-vendas-pedidos-detalhe.html` | o mesmo do PDV (limite de desconto, que não existia, o excedente, a marca) |
| `telas/cadastros/pagina-cadastros-vendedores-detalhe.html` | a aba de confirmações vira ponte para o usuário; sai `PROMO_PODE_NA_HORA` / `PODE_NA_HORA_IDS` |
| `telas/configuracoes/pagina-configuracoes-usuarios.html` e as outras 3 de usuários/perfis | a fábrica de exemplo (hashes reais, permissões) |
| as 29 telas que já têm `promocaoNaHora` no catálogo | a ação `promocaoExcedente` no `ACOES_ESPECIFICAS` |
| `_ferramentas/teste_usuarios.py` | seções novas: o código de autorização e o limite por pessoa |
| `_ferramentas/teste_promocoes.py` | seção nova: o excedente e o limite por pessoa |
| as 28 suítes que preenchem o campo de senha (bloqueados, caixa, comissões, compra_giro, conferência_saida, confirma_senha, crm, devolução, embalagem_pedido, expedicao, fin_melhorias, formas_recebimento, gateway_uso, gateways, metas, nomes_sistema, pdv, pedidos, perdas_baixa, promoções, rastreamento, retorno, transf_conferencia, transportadoras, usuários, vale_compra, vale_origem, vale_uso) | o valor preenchido vira o código 1234 (fora o caso vazio, que continua vazio) |
| `_ferramentas/auditoria.py` | as chaves `deskUsuarios` e `deskPerfis` já estão na lista de chaves permitidas (a entrega 1 já as colocou — confira e não duplique) |
| `docs/design-system-oficial-desk-company.md` | §14.111 (o texto técnico da entrega) |
| `PROGRESSO.md`, `HISTORICO.md` | o estado de hoje e o texto da entrega (ver "Fim") |

## Ordem de execução (uma peça por vez, com a suíte da peça rodando antes da próxima)

1. **A — o código no lugar da senha (95 telas).** O bloco novo, o modal, a trava, o log.
   Suíte: `teste_usuarios.py` (seção nova) + `selo.py --rodar`.
2. **B — o limite de desconto por pessoa (PDV e Pedido).** Suíte: `teste_pdv.py`, a seção nova
   do `teste_usuarios.py`, `selo.py --rodar`.
3. **C — o pacote do gerente (promoção).** O `promocaoNaHora` pela permissão, o botão do
   excedente, a marca `excedente`, o registro. Suíte: `teste_promocoes.py`, `selo.py --rodar`.
4. **D — a ficha do vendedor e as fábricas de exemplo.** Suíte: `teste_usuarios.py`, `selo.py --rodar`.
5. **E — selo completo** (`python selo.py --rodar --tudo`) e a documentação.

## Regras da casa (vale para todas as peças)

- **Provar nos dois sentidos:** cada regra nova entra com um defeito injetado que a suíte
  tem de reprovar (3 a 4 defeitos, só onde há dinheiro ou regra nova). Desfeito, a suíte volta
  ao verde. Escreva o que foi injetado no §14.111.
- **A suíte compara as cópias:** o bloco novo é idêntico nas 95 telas (a suíte compara, como
  faz com os outros blocos comuns). A fábrica nova é igual à da entrega 1.
- **Id único no sistema:** o botão novo do excedente tem id próprio, escrito por inteiro, e o
  código usa `document.getElementById` (a auditoria do projeto só enxerga id literal).
- **O botão novo usa o design system:** `.btn-secundario` da própria tela (a regra de 09/nov:
  classe que só aparece em string do JS sem CSS na tela é defeito).
- **Nada de tela nova:** esta entrega mexe em telas que já existem.
- **Nada de conta, nada de publicação.**
- **Leitura por trecho:** `grep -n` e `sed -n 'X,Yp'`; nunca leia a tela inteira.
- **Script em massa:** lê e grava com `newline=''` (não troca CRLF por LF).

## Fim

- `python selo.py --rodar --tudo` verde, e a árvore do git limpa.
- Commit: "Usuários e Permissões, entrega 2: o código de autorização e o pacote do gerente".
- **PROGRESSO.md reescrito** (não acrescentado) no mesmo commit: a entrega 2 sai de "Próximo da
  fila"; o próximo da fila vira o **preço de atacado** (item 2 da fila atual); as regras
  decididas que foram implementadas saem do "Decidido" ou ganham "(feito)"; os códigos de
  exemplo entram para o usuário saber como testar.
- **HISTORICO.md**: a entrega **entra** só quando o usuário testar e aprovar (a entrega 1 foi
  para o HISTORICO já testada). Enquanto isso, deixe o HISTORICO como está.
- **§14.111** no design system: o texto técnico (blocos novos, o que mudou em cada tela, as
  regras, as suítes, o que ficou de fora).
