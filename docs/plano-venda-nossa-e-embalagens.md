# Plano: o desconto da venda nossa e a rodada do estoque das embalagens (20/nov/2026)

Barganha fechada com o usuário em 20/nov/2026 ("tranquilo, pode seguir com a construção"). Duas entregas, nesta ordem, e
uma de cada vez (as duas mexem no PDV e no Pedido de Venda, e o selo não roda em dobro):

1. **Entrega 1: o desconto da venda nossa** (PDV e Pedido de Venda). Pequena.
2. **Entrega 2: a rodada do estoque das embalagens**, em dois pacotes: o pacote 1 (código, movimento, motivos, acerto,
   prejuízo e Movimentação) e o pacote 2 (Necessidades de Compra, Ordem de Compra, nota, entrada sem nota, baixa no pedido e
   Inventário).

## Regras para todas

- Leia por trecho (grep e faixa de linhas), nunca a tela inteira. Script de troca em massa com `newline=''`, e assert de
  contagem 1 em cada troca.
- Bloco comum: um bloco, idêntico em todas as cópias, trocado por script de texto exato; confira as cópias no fim (a suíte
  que compara as cópias tem que seguir verde).
- Todo item ganha asserção. Regra de dinheiro ganha 3 a 4 defeitos injetados: cada um tem que reprovar a suíte, e o
  defeito sai depois. O que é visual ganha foto nos dois temas no scratchpad.
- Durante o trabalho, rode só as suítes das telas mexidas; no fim de cada entrega (ou pacote), `python selo.py --rodar`,
  uma vez, com a saída gravada num arquivo. Não retestar o que o usuário já aprovou.
- Fecha com: suítes verdes, selo verde, um parágrafo no §14 do design system (§14.118 para a entrega 1, §14.119 para o
  pacote 1, §14.120 para o pacote 2), o PROGRESSO reescrito ("Onde paramos" com a entrega esperando o teste dele, os links
  inteiros `http://localhost:3000/<pasta>/<arquivo>` e o que conferir; a fila atualizada). **Sem commit e sem `git add`:**
  o agente principal revisa e envia.

---

## Entrega 1: o desconto da venda nossa

### O que ele decidiu

1. **É uma opção que se aplica, não automática.** Aparece "Dar o desconto da venda nossa (5%)" só quando a venda está
   **sem vendedor** (no Pedido, também **sem indicação**) e tem pagamento **no Pix ou no dinheiro**.
2. **Pix e dinheiro**, como o desconto à vista.
3. **Trava:** o desconto nunca leva um produto abaixo do **preço mínimo da calculadora** (o do bloco PRECO MINIMO,
   `promoMinimoCent(promoProdutoId(...))`). Em produto de promoção ou de atacado ele soma até o mínimo; o que passar é
   cortado, e um aviso diz quanto foi cortado e em qual produto.
4. **Não pede código** e **não conta no limite de desconto** de ninguém (o "Desconto sem liberação"), como o desconto à vista.
   Se alguém escolher um vendedor depois (ou, no Pedido, chegar uma indicação), o desconto sai sozinho, com aviso.

### O percentual

É o `comissaoPadraoPct` de Configurações → Parâmetros de vendas (`deskParametros`; de fábrica 5), o mesmo que a calculadora
usa no bloco "Venda nossa, sem comissão" da ficha do produto. Leia pelo mesmo leitor de parâmetros que o bloco PRECO MINIMO já
usa (o que vale o de fábrica quando o guardado está estragado). Mudou lá, muda aqui; o rótulo mostra o percentual em vigor.
Nada muda em Configurações: o parâmetro já existe.

### A conta (bloco comum novo, idêntico no PDV e no Pedido)

Crie o bloco `// ===== VENDA NOSSA (bloco comum, 20/nov/2026) =====` ... `// ===== FIM DO BLOCO VENDA NOSSA =====`, com uma
função pura que recebe as linhas e devolve o desconto. Tudo em centavos inteiros.

- **fatia** = a parte da venda paga no Pix ou no dinheiro, de 0 a 1.
  - PDV: a soma do `valor` dos recebimentos Pix e dinheiro dividida pelo total da venda.
  - Pedido: forma de recebimento Pix ou dinheiro → (total − vale-compra) ÷ total; qualquer outra forma → 0.
- **Por linha:**
  - `base` = o valor da linha já com promoção, atacado, preço digitado e a parte dela no desconto manual da venda (rateado
    pelo valor das linhas);
  - `desejado` = base × fatia × pct;
  - `pagoSemEle` = base × (1 − fatia × pctAVista). `pctAVista` é o do desconto à vista do PDV (`descontoAVistaPct()`); no
    Pedido é 0, porque o Pedido não tem desconto à vista;
  - `folga` = sem limite quando o produto não tem mínimo (sem custo); senão max(0, pagoSemEle − mínimo × quantidade);
  - `valor` = min(desejado, folga).
- O desconto é a soma dos valores; `cortado` = soma dos desejados − soma dos valores. Cortado > 0 → o aviso, com os nomes
  dos produtos cortados.

### Onde entra

- **PDV** (`telas/vendas/pagina-vendas-pdv.html`):
  - O desconto cai nos recebimentos Pix e dinheiro, na proporção do `valor` de cada um, como o à vista; o centavo que
    sobrar vai para o maior.
  - `pagoDe(r)` passa a descontar os dois, e `totalAPagar()` também.
  - Confira todo uso de `descontoDe`, `descontosAVista`, `pagoDe` e `totalAPagar`: caixa, troco, título, recibo e resumo
    precisam bater.
  - Na cobrança, logo abaixo da linha "Desconto Pix/dinheiro", fica o link "Dar o desconto da venda nossa (5%)" quando
    cabe. Aplicado, ele vira a linha "Desconto da venda nossa (5%) − R$ X", com "tirar" (sem código).
- **Pedido de Venda** (`telas/vendas/pagina-vendas-pedidos-detalhe.html`):
  - O mesmo link, e depois a mesma linha, entre os totais (`total-item`).
  - `geral`, em `recalcularTotais`, desconta o valor. A prévia das parcelas, o RESULTADO DO PEDIDO e as contas a receber
    seguem o `geral`.
- **O registro:**
  - A venda e o pedido gravam `vendaNossa: { pct, valor, cortado }`.
  - O desconto aparece onde o desconto à vista aparece, logo abaixo dele, com o rótulo próprio: o resumo da cobrança,
    "O que esta venda gerou", o recibo e o registro da venda.
  - Não entra no catálogo de ações auditáveis, porque não pede código.
- **Avisos:**
  - Com corte: "O desconto da venda nossa ficou em R$ X (R$ Y cortados): <produto> chegou ao preço mínimo."
  - Vendedor escolhido depois: "O desconto da venda nossa saiu: a venda agora tem vendedor, que recebe comissão." No Pedido
    vale o mesmo para a indicação.
  - O Pix saiu da venda: a linha some (valor 0) e volta quando o Pix volta. Só o vendedor tira a opção de vez.

### Asserções (suíte nova `_ferramentas/teste_venda_nossa.py`, nas duas telas)

1. O link só aparece sem vendedor (e sem indicação, no Pedido) e com Pix ou dinheiro; com cartão só, não aparece.
2. O valor é 5% da parte paga no Pix ou no dinheiro. Com 4% em Parâmetros de vendas, o desconto é de 4%.
3. Pagamento dividido (metade no Pix, metade no cartão) desconta só a metade.
4. A trava corta e avisa: monte uma linha no limite do mínimo, por exemplo com o preço digitado perto dele.
5. Escolher o vendedor tira o desconto e avisa.
6. Não pede código e não conta no limite de desconto.
7. O total a pagar, o troco e o título batem.
8. O bloco VENDA NOSSA é idêntico nas duas telas.

Defeitos injetados: (a) sem a trava; (b) sem a fatia; (c) sem a condição do vendedor. Cada um reprova a suíte.

---

## Entrega 2: a rodada do estoque das embalagens

### O que ele decidiu

1. **Motivos:** o acerto escolhe o motivo da lista de Motivos de Perda. Cada motivo ganha a marca "vale para embalagens";
   já vêm marcados quebra ou avaria, perda, furto, extravio, consumo próprio, sobra de contagem, correção de lançamento e
   contagem física (ids 1, 2, 3, 4, 5, 7, 8 e 10). Embalagem é material de uso, não mercadoria: não vai para fila fiscal (o
   destino fiscal do motivo não vale aqui).
2. **Prejuízo:** o acerto para menos, com motivo de saída (ou de balanço), é prejuízo: a quantidade vezes o custo médio. Ele
   aparece na Movimentação de Estoque, com o valor, e num card "Prejuízo com embalagens no mês" na tela de Embalagens.
3. **Inventário:** as embalagens entram no mesmo Inventário, com a escolha "Produtos / Embalagens". A diferença contada vira
   acerto, com o motivo "Contagem física".
4. **Código:** a embalagem ganha um código próprio, na sequência **EMB-001**, e entra na ordem de compra, na nota e na
   entrada como qualquer item. Quando a nota chega, a linha da embalagem soma ao saldo e recalcula o custo médio. O "Dar
   entrada" de hoje fica só para compra sem nota, com o nome "Dar entrada sem nota".
5. **Movimentação:** entram a entrada (pela nota ou sem nota), a baixa no pedido (na Conferência de Saída), o acerto e a
   contagem, com a escolha "Produtos / Embalagens".

### O que já existe (conferido em 20/nov)

- O bloco comum `EMBALAGENS: LEITURA` está em 13 telas: `grep -rl "EMBALAGENS: LEITURA (bloco comum" telas`. Ele tem o cadastro
  de exemplo `EMBALAGENS_PADRAO` (ids 1 a 14), `embalagensLer`, `embalagensGravar`, `embRende`, `embCustoUso` e
  `embBaixar(itens)`. Quem chama o `embBaixar` é só a Conferência de Saída, ao fechar
  (`telas/logistica/pagina-logistica-conferencia-saida-detalhe.html`).
- Em Embalagens (`telas/cadastros/pagina-cadastros-embalagens.html`):
  - o acerto é texto solto (`inputMotivoAcerto`, perto da linha 2146), gravado com `confirmarAcao('embalagensEditar', ...)`;
  - o "Dar entrada" (`abrirEntrada`, `entradaCalc`, `previaEntrada`) recalcula o custo médio no campo `custo`;
  - a tela não tem fileira de cards (o CSS `.kpi-card` existe).
- Motivos de Perda (`telas/configuracoes/pagina-configuracoes-motivos-perda.html`) guarda o cadastro em `deskMotivosPerda`.
  Tratamento de Perdas (`telas/estoque/pagina-estoque-itens-bloqueados.html`, `motivosDoCadastro`) lê esse cadastro conferido,
  com o espelho de fábrica quando não há nada guardado. Embalagens passa a ler do mesmo jeito.
- A Movimentação (`telas/estoque/pagina-estoque-movimentacao.html`) é a ficha de um produto escolhido na busca, com Data e
  hora, Movimento, Cliente ou fornecedor, Saldo anterior, Quantidade, Saldo atual, Valor unitário, Custo médio e Valor em
  estoque. Hoje é só exemplo (`MOVIMENTO`) e não lê nada guardado.
- Necessidades de Compra (`telas/estoque/pagina-estoque-necessidades-compra.html`):
  - o bloco "embalagens abaixo do mínimo" (`embalagensAbaixoDoMinimo`) tem o link "Dar entrada" e a frase "Aqui não se gera
    ordem de compra";
  - as ordens de produto nascem no painel `abrirOrdem` / `gerarOrdens` e se gravam em `deskOrdensGeradas`.
- Ordens de Compra (lista e detalhe) leem `deskOrdensGeradas`, mas o detalhe entra com `recebido: 0` e a lista com
  "aberto". "Lançar nota" vai para `pagina-estoque-entrada-notas-detalhe.html` sem dizer qual ordem.
- Entrada de Notas (detalhe):
  - os itens são digitados (nome, SKU, quantidade, un, preço);
  - o campo "Ordem de compra (opcional)" só lista exemplos (2, 3 e 11);
  - salvar só avisa que a nota vai para a Conferência de Entrada; nada é gravado;
  - o fornecedor 5 é a "Embalagens do Vale".
- O Inventário (`telas/estoque/pagina-estoque-inventario.html`) trabalha por depósito, com três caminhos: gerar pelos
  filtros, planilha e coletor. Os dois últimos casam pelo código.

### Pacote 1: código, movimento, motivos, acerto, prejuízo e Movimentação

1. **Código EMB.**
   - `embCodigo(e)` entra no bloco `EMBALAGENS: LEITURA`, em todas as cópias. A sequência é EMB-001, EMB-002...: as de
     exemplo vão do id 1 = EMB-001 até o id 14 = EMB-014.
   - **Um código nunca se reaproveita.** Veja como o cadastro dá o id à embalagem nova e o que a exclusão faz. Se excluir e
     criar puder repetir o número, grave o código na embalagem quando ela nasce, a partir da maior sequência já usada.
   - Na tela é "Código": só leitura, com a dica "gerado pelo sistema". Aparece na lista, no painel e em toda tela onde a
     embalagem aparece, e a busca acha por ele.
2. **Movimento.**
   - A chave nova `deskMovEmbalagens`, uma lista, gravada por `embMovRegistrar(m)` e lida por `embMovLer()`, no mesmo bloco
     comum.
   - Os campos: `{ em, embId, tipo, qtd, custoUnit, custoMedio, motivoId, motivo, obs, prejuizo, ref: { tipo, numero, texto },
     fornecedor, quem }`.
     - `tipo`: `entrada_nota`, `entrada_sem_nota`, `baixa_pedido`, `acerto` ou `contagem`;
     - `qtd`: com sinal, 4 casas;
     - `custoMedio`: o custo médio depois do movimento.
   - **O saldo de antes e o de depois não se gravam.** A ficha deriva de trás para a frente a partir do saldo atual, e a
     primeira linha é "Saldo de abertura". Assim a ficha nunca desmente o cadastro.
   - **O exemplo de fábrica**, quando a chave não existe: alguns movimentos dos últimos 60 dias, com entradas pela nota da
     Embalagens do Vale e baixas em pedidos, e um acerto por quebra ou avaria de 2 Flex M **hoje, às 09:15**. Ele já acende o
     card do mês, em qualquer dia.
3. **Motivos de Perda.**
   - O campo `embalagem` vira a caixa "Vale para embalagens" no formulário e uma marca na lista.
   - Vêm marcados de fábrica os motivos 1, 2, 3, 4, 5, 7, 8 e 10.
   - Um motivo guardado sem o campo usa o de fábrica, pelo id; um motivo novo nasce desmarcado.
4. **Acerto em Embalagens.**
   - O motivo vira uma lista, só com os ativos que valem para embalagens. A dica do motivo (`obs`) aparece embaixo, e
     `exigeObs` pede a observação.
   - O grupo do motivo manda na direção: saída pede saldo menor, entrada pede maior, balanço aceita os dois. A mensagem de
     erro fica no campo.
   - A falta com motivo de saída ou de balanço gera prejuízo = quantidade × `custo`. Ele aparece na confirmação e grava o
     movimento `acerto`.
5. **Card "Prejuízo com embalagens no mês"**, no topo de Embalagens.
   - Soma o prejuízo dos acertos e das contagens do mês; embaixo, "N acertos · o maior: <nome>".
   - Clicar abre a Movimentação nas embalagens.
   - A fileira nasce com ele e com mais dois que a tela já sabe calcular: "Abaixo do mínimo" e "Valor em estoque" (saldo ×
     custo).
6. **Movimentação.**
   - "Produtos / Embalagens" fica junto da busca.
   - Em Embalagens, a busca acha pelo nome ou pelo código, o filtro de depósito some e a ficha usa as mesmas colunas.
   - O Movimento diz "Entrada pela nota nº X", "Entrada sem nota", "Baixa no pedido nº X", "Acerto: <motivo>" ou "Contagem
     física". O prejuízo vai no Movimento, em vermelho: "prejuízo de R$ X".
   - O filtro de tipo de movimento vale para os dois. A frase "É só consulta" continua.

Asserções do pacote 1:
- o código segue a sequência e não se repete;
- a lista de motivos só tem os que valem para embalagens;
- a direção barra o motivo errado;
- a observação é obrigatória quando o motivo pede;
- o prejuízo é a quantidade vezes o custo;
- o movimento grava os campos;
- a ficha bate com o saldo atual, saldo de abertura incluído;
- o card soma o mês;
- o bloco comum continua idêntico.

Defeitos injetados: (a) o prejuízo sem o custo; (b) a direção desligada; (c) a ficha sem o saldo de abertura.

### Pacote 2: compra, nota, entrada sem nota, baixa no pedido e Inventário

1. **Necessidades de Compra, o bloco das embalagens.**
   - Ganha a coluna Código e o "Chegando": o que as ordens geradas em aberto e em andamento ainda têm a receber
     (qtd − recebido), com o nº da ordem.
   - Comprar = max(0, ⌈mínimo − saldo − chegando⌉).
   - Cada linha ganha a caixa de marcar, e "Gerar ordem de compra" usa o mesmo painel das ordens de produto: fornecedor
     obrigatório, previsto e quantidade editável.
   - A ordem nasce em `deskOrdensGeradas` só com embalagens: itens `{ nome, sku: código, qtd, un: 'UN', preco: custo,
     recebido: 0, embId }`.
   - Saem o link "Dar entrada" e a frase "Aqui não se gera ordem de compra".
2. **Ordens de Compra, a lista e o detalhe.**
   - A ordem gerada passa a ler o `recebido` e a `situacao` gravados.
   - A linha de embalagem mostra o código.
   - "Lançar nota" leva `?oc=<número>`.
3. **Entrada de Notas, o detalhe.**
   - O campo "Ordem de compra" lista também as ordens geradas em aberto e em andamento, e `?oc=` já vem com ela escolhida.
   - Escolher uma ordem gerada preenche o fornecedor e põe os itens pendentes (qtd − recebido).
   - Um item com código EMB-xxx é embalagem; o nome vem do cadastro.
   - Ao salvar a nota completa, cada linha de embalagem:
     - soma ao saldo;
     - recalcula o custo médio, com a mesma conta do "Dar entrada" (reuse `entradaCalc`, ou a conta dele);
     - grava o movimento `entrada_nota`, com a série, o número e o fornecedor;
     - soma ao `recebido` da ordem: em andamento enquanto falta, atendida quando tudo chegou.
   - **A mesma nota não entra duas vezes:** a chave é o CNPJ do fornecedor + a série + o número.
   - O aviso diz quantas embalagens entraram no saldo: embalagem é material de uso e não passa pela conferência. Os produtos
     seguem para a Conferência de Entrada, como hoje.
   - Esta tela não tem o bloco das embalagens: entra a cópia dele.
4. **Embalagens.**
   - "Dar entrada" vira "Dar entrada sem nota": o botão, o painel e os textos.
   - O campo "Nota" vira "Comprovante (opcional)", com a dica de que compra com nota entra pela Entrada de Notas.
   - Grava o movimento `entrada_sem_nota`.
5. **Conferência de Saída.**
   - `embBaixar(itens, ref)` (bloco comum, todas as cópias) grava um movimento `baixa_pedido` por embalagem, com o nº do
     pedido.
   - Só a Conferência passa o `ref`.
6. **Inventário.**
   - Ao gerar, escolhe-se o que contar: "Produtos / Embalagens".
   - Embalagens não têm depósito. A lista traz as ativas, insumos inclusive, com código, nome, tipo, saldo da abertura,
     contado, diferença e o valor da diferença (× custo).
   - Fechar aplica a diferença (contado − saldo da abertura) como movimento `contagem`, com o motivo "Contagem física"; a
     falta vira prejuízo.
   - O inventário de embalagens não trava a baixa dos pedidos, e por isso a diferença é contra o saldo da abertura, não
     contra o de agora. O texto da tela diz isso.
   - Planilha e coletor seguem só para produtos: código de embalagem no arquivo é recusado com o motivo "código de
     embalagem: conte no inventário de embalagens".

Asserções do pacote 2:
- a ordem nasce com o código, e o "chegando" desconta a sugestão;
- a nota com embalagem soma o saldo, calcula o custo médio certo e marca a ordem;
- a mesma nota não entra duas vezes;
- a entrada sem nota grava o movimento;
- a baixa da Conferência de Saída grava o movimento com o pedido;
- o inventário de embalagens aplica a diferença contra a abertura e gera o prejuízo;
- o coletor recusa o código de embalagem;
- os blocos comuns continuam idênticos.

Defeitos injetados: (a) o custo médio da nota com o preço no lugar da média; (b) a nota entrando duas vezes; (c) o
inventário contra o saldo de agora.
