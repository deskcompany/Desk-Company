# Plano: a revisão geral de novembro (16/nov/2026)

Os 19 itens da seção "Para a próxima revisão geral" do `PROGRESSO.md` (o 19 entra junto com este plano). O texto de cada
item lá é a especificação; aqui ficam a ordem, as decisões que o usuário tomou em 16/nov e o que vale para todos.

## Regras para todos os pacotes

- **Não retestar o que ele já aprovou** (pedido dele em 16/nov): rode a suíte de cada tela mexida e, no fim do pacote,
  `python selo.py --rodar` (ele só refaz o que mudou). Nada de varredura geral, foto de tela não mexida ou prova de tela
  que o pacote não tocou.
- Bloco comum: um bloco, idêntico em todas as cópias, trocado por script de texto exato; confira as cópias no fim.
- Todo item ganha asserção na suíte da tela (ou numa suíte de bloco, quando for de bloco comum), e o que é visual ganha
  foto nos dois temas no scratchpad.
- Cada pacote fecha com: suítes verdes, selo verde (só `teste_cpd.py` pode seguir vermelho até o pacote D), um parágrafo
  no §14 do design system (§14.113 em diante, um por pacote) e o item riscado do PROGRESSO (o item sai da lista e vai,
  numa linha, para "Onde paramos" como feito e esperando o teste dele). Sem commit: o agente principal revisa e envia.

## Pacote A: os blocos de interação do sistema todo (itens 5, 14 e 12)

- **Antes, o resto da correção do custo (16/nov):** a ficha do produto passou a gravar a aba Custos em
  `deskCustoProduto` e o mínimo do PDV e do Pedido lê de lá (§14.112). O mínimo de
  `telas/vendas/pagina-vendas-promocoes-detalhe.html` (perto de `return precoMinimo({ lojaId: pr.loja, custo: base ===`)
  ainda lê o custo do catálogo: passa a ler do mesmo jeito que o `promoMinimoCent` do PDV (a linha mais recente
  gravada, e o catálogo sem nada gravado), com uma asserção em `teste_promocoes.py`.

- **14. O menu que abre para cima.** Todo dropdown e todo "Mais ações" abre para baixo; **quando não cabe embaixo na
  janela, abre para cima** (como o "Por página" já faz). Vale para o bloco comum do dropdown e o do menu de ações.
  Atualize a regra escrita onde ela está: `C:\Claude AI\Desk Company\.claude\agents\executor.md` ("todo dropdown abre para
  baixo") e a mesma frase no design system, se houver. Caso que tem de passar: o "Adicionar recebimento (F4)" do PDV
  com a venda no pé da tela.
- **5. A página de trás não rola com o painel lateral aberto**, e volta ao mesmo ponto ao fechar. No bloco comum do
  painel; todas as telas com painel.
- **12. A bolinha dos itens de lista e das opções de marcar**, centralizada no texto e na caixa, igual em todo cartão,
  nos dois temas. Procure o mesmo marcador e a mesma opção nas outras telas e corrija num bloco comum.

## Pacote B: as tabelas (itens 16, 17, 18 e 4)

- **Regra:** nenhuma tabela rola na horizontal de 1280 px para cima, e o título da coluna fica numa linha só (a setinha
  de ordenar junto do nome). Para caber, nesta ordem: larguras mais justas, nome do título mais curto, duas informações
  empilhadas na mesma célula (nome em cima, código embaixo) e, por último, a coluna menos usada indo para o painel
  lateral da linha. Relate cada coluna que mudar de lugar.
- **16.** Registro de atividades sem barra com o registro cheio (126 linhas ou mais), junto do item 15 (a coluna "Ação"
  estreita com reticências).
- **17.** Necessidades de Compra, CRM e Metas sem barra a 1280 px. Mude também o "Decidido / A barra que ficou" do
  PROGRESSO (a decisão de 19/out caiu em 16/nov) e o que `teste_barra_tabelas.py` aceitava para as três.
- **18.** Os títulos que quebram (a lista do item). Em Usuários, o título vira **"Desconto sem liberação"** (escolha dele) e a
  coluna "Usuário" estreita. `teste_barra_tabelas.py` passa a medir também o título em uma linha, a 1280 e a 1440, e o
  Registro de atividades com o registro cheio.
- **4.** Texto e caixa na mesma altura e no mesmo lado nas tabelas editáveis (Promoção, Ordem de Compra, Entrada de Notas).

## Pacote C: telas, uma a uma (itens 15, 19, 6, 7, 8, 9, 10, 11 e 1)

- **15. Registro de atividades: o painel lateral** da linha, no padrão dos painéis da casa: a ação, o texto inteiro que
  a pessoa confirmou, quem fez (perfil), quem autorizou, onde (com o link da tela), quando (data e hora) e o registro.
- **19. Preview do Produto** (lista de Produtos), com os quatro blocos que ele marcou:
  - **Preços:** venda, promocional, atacado com "a partir de N un." e a promoção ativa, se houver.
  - **Custo e margem:** custo médio, margem sobre o preço de venda e o mínimo da calculadora.
  - **Estoque:** físico, disponível, mínimo e o saldo por depósito.
  - **Cadastro:** loja, marca, fornecedor padrão e embalagem.

  Os números vêm das mesmas fontes da ficha (`deskPrecoProduto`, `deskCustoProduto`, o cálculo guardado em
  `deskCalculoPreco`). Se o mínimo da calculadora não puder ser calculado na lista sem trazer o bloco inteiro, mostre o
  do cálculo guardado e, sem ele, "abra a calculadora na ficha"; relate. O painel cresce de largura se preciso, sem barra.
- **6. Painel da promoção** (escolha dele): "× fechar" no alto, como os outros painéis; embaixo, "Abrir promoção completa"
  em azul e, ao lado, um "Mais ações" com Antecipar para hoje, Prorrogar, Clonar, uma linha separando, e Encerrar
  agora. Cada ação mostra só quando vale hoje, como já mostra.
- **7.** Ficha do produto, aba Dados Complementares: a grade da aba Dados Gerais.
- **8.** O "Encerrar antes para este produto" com o botão do design system, e a procura das classes que só aparecem em
  string do JS sem CSS na tela (as 96 telas, por script, sem abrir navegador).
- **9.** Revisão da promoção: "Pronto" e "Corrigir" (etiqueta, filtro, frase, ajuda, suíte e §14.108).
- **10 e 11. Só no PDV** (escolha dele: o Pedido de Venda fica como está): o resumo "O que esta venda gerou" e a caixa
  "Desconto à vista" sem o nome da maquininha, o nível e a bandeira.
- **1.** Embalagens: os campos de tamanho numa linha, medido a 1152 e a 1280 px de largura e com zoom de 110%, nos dois
  temas, no cadastro novo e na edição, nos três tipos. O painel pode alargar até caber.

## Pacote D: Finanças (itens 2 e 13)

- **2.** A aba "atrasadas" de Contas a Pagar mostra toda conta vencida e não paga, fora do período; o card e a aba dão o
  mesmo número. O mesmo em Contas a Receber, se tiver a aba.
- **13.** Descubra por que o passo 15 de `teste_cpd.py` reprova. Se for a data (a conta de exemplo mudou de situação com o
  tempo), o teste passa a escolher a conta pela situação, não pelo número; se for a tela, conserte a tela. Depois disso o
  selo inteiro fica verde.

## Pacote E: a calculadora com mais de uma embalagem (item 3)

- O campo "Caixa" da calculadora vira uma lista com caixa de marcar: só as embalagens ativas com estoque; marca-se uma ou
  mais (a caixa e o saquinho da loja). Os insumos que entram sozinhos continuam entrando. O custo da embalagem é a soma.
- O cálculo guardado (`deskCalculoPreco`) passa a guardar a lista; o cálculo antigo, com uma caixa só, abre como lista de
  uma. O mínimo é bloco comum com Promoções e Encartes (§14.108): as telas do bloco leem a lista do mesmo jeito.
- Asserções: marcar duas soma os custos e sobe o mínimo; o cálculo antigo abre certo; promoção e venda usam o mínimo novo.
