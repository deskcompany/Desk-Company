# Desk Company ERP — Arquitetura, Roadmap & Protocolo (consolidado)

> **Papel deste arquivo dentro do conjunto de 3:** aqui vive tudo que é **projeto/gestão** — visão geral, schema de backend (além do que já está em produção nos Cadastros), fases, e as regras de execução do dia a dia. Pra **visual e componentes**, ver `design-system-oficial-desk-company.md`. Pra **ver os padrões funcionando**, ver `pagina-molde-referencia.html`.
>
> Este arquivo substitui e consolida 4 documentos anteriores (checklist-v3, arquitetura-roadmap-v3, protocolo-anti-retrabalho, resumo-continuidade) — nada foi descartado, só organizado num lugar só.

---

## 1. Visão geral

**Desk Company ERP** — sistema central de gestão do ecossistema Desk (Desk Shope, Desk Brands, Desk Tech e futuras marcas), com padrão de qualidade inspirado no Olist/Bling/Tiny.

**Arquitetura hub-and-spoke:**
- **Hub (Desk Company ERP):** fonte única da verdade — produtos, estoque, clientes, financeiro.
- **Vitrines simples** (Desk Shope, Desk Brands, futuras Desk Make/Desk Food): catálogo/carrinho/checkout, sem estoque ou operação própria — compartilham o mesmo Supabase em tempo real com o hub.
- **Negócios-satélite com sistema próprio** (Desk Tech = ordens de serviço; Desk Flash = transportadora): projetos completos à parte, cada um com seu domínio. Não compartilham o banco operacional — só sincronizam **identidade do cliente** (cadastro mestre fica na Desk Company) e **números consolidados** (vendas, faturamento, lucro) pro financeiro central.

**Ponto de atenção já decidido:** Desk Tech **não é** uma loja de produto — é assistência técnica (ordem de serviço: diagnóstico, técnico, peças, aprovação de orçamento). Nunca construir em cima do módulo "Pedidos" da Shope, ou vai quebrar/deformar quando chegar a vez da Tech. O hub terá dois tipos de "venda" desde o schema: **Pedido de Produto** (Shope/Brands) e **Ordem de Serviço** (Tech), compartilhando clientes/financeiro/estoque mas com fluxo e telas próprias.

## 2. Stack e plataformas (travado)

- **Lovable** (build) + **GitHub** (versionamento, sincroniza automático) + **Supabase** (banco/auth/edge functions) + **Vercel** (hospedagem, zero-config pra projetos Lovable)
- React + TypeScript + Vite + TanStack Router + Tailwind CSS v4 (CSS-based, sem `tailwind.config`)
- **1 projeto Supabase único**, compartilhado pelo ERP e todas as vitrines. **Projetos separados** no Lovable/Vercel por app (ERP, Desk Shope, depois Desk Tech) — não usar monorepo, isola o "raio de explosão" de uma mudança.
- Integrações com transportadoras (Correios, Melhor Envio) ficam em **Supabase Edge Functions**, reaproveitável por ERP e vitrines.
- Gateway de pagamento: **InfinityPay** (Checkout Integrado — Pix + cartão em até 12x, webhook de confirmação + fallback `payment_check`)
- Frete: **Melhor Envio** (agrega Correios e outras transportadoras numa API só)
- SMTP transacional: **Resend**
- **NF-e:** fora de escopo por enquanto (negócio no MEI). Schema já nasce preparado (`orders.nfe_status`, stub de `invoices`, campos fiscais reservados nos Cadastros) — integração (Focus NFe/eNotas) entra em F8, quando migrarem pra PJ.
- Antigravity (Google): só cogitado pra **operação/manutenção pós-lançamento**, não construção.

## 3. Schema de backend — decisões que precisam nascer certas

Além do schema de Cadastros já em produção (`products`, `categories`, `customers`, `suppliers` — ver `design-system-oficial-desk-company.md` §12 e a skill `desk-company-erp/references/arquitetura.md`), o hub como um todo precisa destas tabelas, decididas **antes** de qualquer tela de Vendas/Estoque/Financeiro ser construída:

> **Legenda (29/set/2026):** ✅ = já tem tela no protótipo · ⬜ = decidido, sem tela ainda — nasce no Supabase ou junto com o módulo dono. **Nenhum item desta lista é decisão pendente.** O único ponto sem fonte fechada (recusa parcial, item 23) espera o contador, não o usuário.

1. **`stores`** ✅ construído (`pagina-cadastros-lojas-desk.html` + `-detalhe.html`) — Desk Shope, Desk Tech, Desk Brands. **Desk Flash NÃO entra aqui** — é transportadora, não loja. Campos: `nome`, `tipo` (`produto`/`servico`/`trade_marketing` — trade_marketing é ponto de exposição/venda em estabelecimento parceiro), `status`, `tipo_pessoa`+`documento` (opcional), endereço (opcional), `contato` (lista de `{rotulo, numero}`, repetível). **Sem campo de cor manual** — cor do avatar é derivada automaticamente do `tipo` (regra fixa no front, não é dado salvo).
2. **`products.store_id`** — um único FK (1 produto = 1 loja, decisão já confirmada e implementada nos Cadastros). **O saldo NÃO é mais um campo central único em `products`** — decisão revista em setembro/2026, na abertura de F5: o saldo é derivado do ledger `stock_movements` **por par (produto, depósito)**, ver itens 5, 15 e 16 abaixo. `products.estoque_atual`, se existir, passa a ser no máximo um cache/view do total somado, nunca o dado de origem.
3. **`customers`** — tabela única do ecossistema, com `origem` (qual vitrine cadastrou primeiro). Já implementado nos Cadastros.
4. **`orders`** com `origem_loja_id` + `status` enum completo: `Pendente → Confirmado → Separação → Etiquetagem → Expedição → Entregue` (+ `Cancelado`, `Devolução`) — mesmo funil do painel "Pedidos por Status" do Dashboard.
5. **`stock_movements`** — ledger único de entrada/saída/perda/devolução/transferência. Saldo de estoque é **derivado** desse ledger (trigger ou view), nunca um campo solto sobrescrito direto por uma tela. Campos de chave: `produto_id`, **`deposito_id`** (FK obrigatória, ver item 15), **`lote_id`** (FK **nullable**, ver item 16), `tipo`, `quantidade` (assinada), `custo_unitario`, `documento_origem`, `usuario_id`, `data`. A derivação do saldo tem que tratar `lote_id IS NULL` normalmente — a maior parte dos produtos Desk nunca vai ter lote, e isso não pode virar exceção no cálculo.
6. **`shipping_carriers`** — `nome`, `tipo` (`api_externa` / `interna`), `config` (chaves de API), `ativo`. Correios/Melhor Envio/Frete Top entram como `api_externa`; quando Desk Flash existir, entra como `interna` — **sem mexer no código de Expedição**.
7. **`metas`** ✅ construído (`pagina-vendas-metas.html`, dentro do menu Vendas) — `loja_id` (FK pra `stores`, qualquer tipo), `mes`, `ano`, `valor`. Sempre granularidade mensal, não importa o modo de preenchimento usado (ver design-system §11-B). **Único ponto de escrita**; a aba "Histórico de Metas" dentro do detalhe de Loja só lê — nunca escreve, evita duas telas mexendo no mesmo dado e desencontrando.
8. **`departamentos`** ✅ construído (`pagina-cadastros-departamento-produtos.html`) — `categoria_id` (FK `categories`, só tipo=produto), `nome`, `status`. Sem `cor` própria — badge exibido usa a cor da Categoria-mãe.
9. **`secoes`** ✅ construído (`pagina-cadastros-secao-produtos.html`) — `departamento_id` (FK `departamentos`), `nome`, `status`. Categoria é sempre derivada do departamento, nunca gravada direto na seção.
10. **`embalagens`** ✅ construído (`pagina-cadastros-embalagens.html`) — `nome`, `tipo` (`pacote`/`envelope`/`rolo` — cada um com campos de dimensão e diagrama SVG próprios), `largura`/`altura`/`comprimento`/`diametro` (conforme o tipo), `peso`, `status`.
11. **`marcas`** ✅ construído (`pagina-cadastros-marcas.html`) — `nome`, `lojas[]` (uma ou mais), `status`. `products.marca_id` referencia esta tabela; o cadastro de Produto filtra o dropdown de Marca pela loja de origem escolhida (só mostra marcas com aquela loja em `lojas[]`).
12. **`vendedores`** ✅ construído (`pagina-cadastros-vendedores.html` + `-detalhe.html`) — `nome`/`fantasia`/`codigo`, `tipo_pessoa`+`documento`, endereço (opcional), `situacao` (`ativo_acesso`/`ativo`/`inativo`), `excluido` (boolean, **independente** de `situacao` — primeiro cadastro do sistema com exclusão suave: o registro nunca é removido de verdade, só marcado; ver design-system §8.1), `loja_vinculada_id` (FK **opcional** pra `stores`, aceita qualquer `tipo` — nulo = vendedor "autônomo": vende e acessa o sistema normalmente conforme suas permissões, mas não gera faturamento/relatório atribuído a nenhuma loja), permissões de acesso (restrição por horário/IP, perfis de contato permitidos, módulos habilitados — hoje mocado no front, vira permissão real quando `Permissões de Usuários` existir de verdade), regras de comissionamento (`regra_liberacao`, `tipo_aliquota` fixa/conforme-descontos, `aliquota`). **Não é mais uma extensão dos registros `trade_marketing` de `stores`** (esse era o plano antigo, revisto na construção real) — é cadastro próprio e independente; o vínculo com uma Loja Desk é opcional e não exclusivo do tipo `trade_marketing`. Criar/editar um vendedor também acopla um fluxo mocado de credencial (senha do vendedor + senha de quem autoriza) que só passa a validar de verdade quando a tabela de usuários/auth existir (ver design-system §11).
13. **Devolução** (referenciada na visão "Devoluções" de `pagina-vendas-performance-vendas.html`, ainda mock) — hoje só existe como `valor` e `quantidade` soltos no mock de performance; quando `orders` nascer de verdade (F3+), devolução deve ser um `status` do próprio pedido (`Devolução`, já previsto no enum do item 4 acima), não uma tabela separada — os agregados de R$/quantidade da Performance de Vendas viram uma query sobre `orders where status = 'Devolução'`, não um novo cadastro.
15. **`depositos`** ✅ construído (`pagina-cadastros-depositos.html`, setembro/2026) — inclui **`usa_enderecamento`** (boolean, **default `true`**, ver item 19) — o saldo de estoque é **por depósito nomeado**, não um saldo único central. Campos: `nome`, `tipo` (`galpao`/`loja_fisica`/`trade_marketing`/`transito`), `loja_id` (FK **opcional** pra `stores` — um depósito pode ser do hub e não de nenhuma loja), `endereco` (opcional), `principal` (boolean, um único por sistema — é o destino padrão de toda entrada que não escolher outro), `status`. Consequências já sabidas: (a) **Transferência Entre Estoques** (já no menu Estoque) passa a ser uma tela real e não decorativa — é um par de movimentos no ledger, saída de um depósito e entrada em outro, mesma `quantidade`, nunca dois lançamentos soltos; (b) toda tela de Estoque ganha um filtro de Depósito; (c) o card "Alertas de Estoque" do Dashboard e a tela Necessidades de Compra passam a somar o saldo de **todos** os depósitos antes de comparar com o mínimo, senão um produto bem abastecido em dois lugares aparece como crítico nos dois.
16. **`lotes`** ⬜ a construir (decidido em setembro/2026, na abertura de F5) — **nasce agora, mas 100% opcional**. Campos: `produto_id`, `codigo_lote`, `validade` (date, opcional), `fabricacao` (date, opcional), `observacoes`. Nenhum campo de lote é obrigatório em lugar nenhum: cadastrar produto, dar entrada, separar e vender funcionam com `lote_id` nulo do começo ao fim, e nenhuma validação de tela pode travar por causa disso. A razão de já existir é evitar migração de dados quando Desk Make / Desk Food (perecíveis, sem data marcada) entrarem — o schema e os campos de tela já estarão prontos, só passam a ser preenchidos. Alerta de vencimento e FEFO (primeiro que vence, primeiro que sai) ficam pra F8: hoje o lote é só um dado que se guarda, não uma regra que se aplica.
17. **`enderecos`** ✅ construído (`pagina-cadastros-enderecos-estoque.html`, setembro/2026) — posição física **dentro de um depósito**. Campos: `deposito_id` (FK obrigatória), `corredor` (obrigatório), `estante`, `nivel`, `posicao` (todos opcionais), `tipo` (`picking`/`pulmao`/`recebimento`/`expedicao`/`avaria`/`quarentena`), `capacidade` (opcional), `situacao`. O **código é derivado** das partes (`A-03-2-05`), nunca digitado solto — é o que garante que a mesma posição não vire três registros por variação de digitação; e é **único por depósito** (dois depósitos podem ter "A-01-1", o mesmo depósito não). Exclusão definitiva (não é soft-delete), bloqueada quando o endereço tem produto alocado; a alternativa é inativar. A tela traz um **gerador em massa** (faixas de corredor × estante × nível × posição) — sem ele ninguém cadastra 160 posições à mão e o módulo nasce morto.
18. **`produto_enderecos`** ✅ na tela de Endereçamento (alocação, base de picking, Estoque Zero) — a tabela nasce no Supabase — a alocação de um produto num endereço. Chave: `produto_id` + `deposito_id` + `endereco_id`. **O mesmo produto tem endereços diferentes em depósitos diferentes** (produto X em `A-01-1` no Imperatriz e em `B-03-2` no Ribeirãozinho) e **pode ocupar mais de um endereço no mesmo depósito** (picking + pulmão), com um marcado como principal. Substitui o campo texto `Localização` que hoje mora em `products` — que passa a ser derivado do endereço principal.
19. **Situação do saldo** ✅ nas telas de Estoque — Controle de Estoques v2 mostra os estágios (decidido em setembro/2026, **fechado em 14/set/2026** na barganha do Controle de Estoques v2) — a decisão estrutural que sai do fluxo de recebimento: o saldo deixa de ser só um número e passa a ter **estágio**, porque "chegou" não é a mesma coisa que "pode vender". Estágios: **`a_enderecar`** (conferido, sem endereço), **`disponivel`** (endereçado — vendável), **`reservado`** (em pedido confirmado, não expedido), **`bloqueado`** (avaria/quarentena). Mais um **pré-estágio**, **`em_conferencia`** (mercadoria chegou, ninguém contou), que **não é estoque** — ver abaixo. Consequências:
    - **Os estágios são baldes mutuamente exclusivos.** Cada unidade está em **exatamente um** estágio; mudar de estágio é movimento no ledger `stock_movements`, nunca campo sobrescrito. A soma fecha: `físico = a_enderecar + disponivel + reservado + bloqueado`.
    - **`em_conferencia` fica FORA do estoque físico** (decidido em 14/set/2026). A mercadoria chegou, mas a quantidade que existe no sistema é **a alegação do fornecedor**, não uma contagem — e a conferência cega existe justamente porque a nota erra (falta, sobra, avaria). Contar isso como estoque seria publicar como fato o número que a tela seguinte foi construída para duvidar. Três consequências práticas: (a) o físico só muda por evento real, nunca **retroage** quando a conferência acha uma falta; (b) o **valor total em estoque** deixa de incluir mercadoria que pode nunca ser recebida ou que vai ser recusada; (c) a regra do item 19 fica coerente uma casa antes — "chegou" não é "pode vender", e também não é "é estoque". O ledger registra a chegada (é preciso saber que ela existe), mas ela só vira saldo quando a conferência fecha.
    - **Ressalva contábil:** durante a janela de conferência o físico do ERP e a escrituração fiscal **divergem de propósito** — a nota já foi escriturada, o estoque ainda não nasceu. É diferença de **tempo**, não erro, e é o equivalente à conta de "mercadoria a conferir" de qualquer sistema de inventário; a janela é curta e a tela de Conferência de Compra já tem relógio (>1 dia alerta, >3 crítico) para mantê-la curta. **Mostrar ao contador** — mesma ressalva honesta do item 23: o fechamento fiscal não passa por este sistema.
    - **`Estoque disponível` ganha definição própria:** `disponível = endereçado − reservado − bloqueado`. Deixa de depender exclusivamente de `orders` — a coluna que nasceu desabilitada em Controle de Estoques passa a ter metade do cálculo funcionando antes de F3/F4.
    - **Trava de venda:** produto sem endereço **não fica disponível para venda**. A regra é global **como política** (`depositos.usa_enderecamento` já nasce `true`); a exceção é mecânica, não é uma segunda regra — um depósito com o endereçamento desligado não tem endereço a cobrar, então não há o que travar. Desligar é decisão consciente, visível no cadastro, e vale só pra aquele lugar (bancada da Desk Tech, ponto de Trade Marketing).
    - **A vitrine precisa saber disso.** A view/RLS que o Desk Shope (F3) consulta tem que filtrar por **saldo disponível endereçado**, nunca pelo saldo físico. Se ficar pra depois, quebra no lançamento.
20. **`stores.deposito_padrao_id`** ✅ campo na tela de Lojas Desk (decidido em setembro/2026; o roteamento de pedido nasce com Pedidos de Venda) — **a loja define de qual depósito saem os pedidos dela**. Venda da Desk Shope sai do depósito dela, venda da Desk Brands do dela. É o que decide a origem da separação quando o pedido é confirmado. Descartadas por ora: roteamento por saldo disponível e por proximidade de CEP (esta fica pra F8). Campo já adicionado à tela de Lojas Desk (detalhe).
21. **`ordens_compra`** ✅ construído (`pagina-estoque-ordens-compra.html` + `-detalhe.html`), **`notas_entrada` e `conferencias`** ✅ construídos (Entrada de Notas + Conferência de Compra; decidido em setembro/2026) — o fluxo de recebimento passa a ser **Ordem de Compra → Entrada de Nota → Conferência → Endereçamento → Vendas → pós-venda**, e cada etapa move o saldo de um estágio pro outro (item 19). **Ordem de Compra entra agora**, não em F8 — decisão do usuário; a nota de entrada nasce vinculada a ela, o que permite conferir contra o que foi *pedido*, não só contra o que foi *faturado*. A **conferência é cega**: o conferente conta sem ver a quantidade que a nota declara, e o sistema compara depois — vendo o número esperado, a tendência é confirmar o que está escrito em vez de contar. É na conferência que o **custo médio** entra no sistema de verdade (hoje é número mocado). Entrada manual no fluxo inicial; integração por API fica pra quando existir.

    **O que os prints de referência confirmaram (set/2026):**
    - **As abas da Conferência são, literalmente, os estágios do saldo do item 19.** *aguardando entrada* (nada no estoque ainda) → *pronto para conferir* e *em conferência* (`em_conferencia`) → *conferidos* (`a_enderecar`). A ação **"receber mercadorias"** é o que faz o registro nascer como `em_conferencia` — **registro, não saldo**: `em_conferencia` não entra no estoque físico (item 19, fechado em 14/set/2026). Isso resolve a contradição que existia entre esta linha e o design-system §12, onde Entrada de Notas já dizia que *"lançada é o único estado que gerou estoque, porque a mercadoria só entra quando a conferência fecha"* — vale o §12: **o estoque nasce no fechamento da conferência**. O desenho foi decidido por raciocínio e o produto de referência bate quase termo a termo.
    - **`ordens_compra.situacao`**: `aberto → andamento → atendida`, fora de `cancelada`. "Em andamento" é exatamente a ordem recebida em parte — o menu de ações traz **"receber parcialmente"**, o que responde a pergunta de recebimento parcial: **aceita**, e a OC segue aberta até completar.
    - **`ordens_compra.deposito_id`**: o Olist traz Depósito na *nota de entrada* (Dados adicionais → Depósito). Nós puxamos um passo antes, pra OC, porque a nota precisa saber onde criar o saldo.
    - **Conferência é operação de teclado, não de mouse:** atalhos (`CTRL+X` importar XML, `CTRL+I` conferir itens, `CTRL+E` receber mercadorias, `ENTER` confirmar, `ESC` cancelar) e um **overlay de tela cheia com um campo só** ("Escaneie a nota de entrada para começar", buscando por fornecedor, número ou chave de acesso). Quem confere mercadoria trabalha com coletor; a tela precisa acompanhar. **Padrão novo do sistema**, a ser aplicado em Conferência e depois em Separação.
    - **Nota de entrada** tem `tipo_entrada` (emissão própria / importação / emitida por terceiros / CT-e de terceiros), `finalidade` (transcrita da tela de referência: NF-e normal, de ajuste, devolução, nota de crédito, com chave referenciada — **atenção:** o campo `finNFe` do layout da NF-e só tem *1 Normal, 2 Complementar, 3 Ajuste, 4 Devolução/Retorno*; a **complementar** é exatamente o instrumento que o item 23 usa para resolver falta na entrega, e é ela que precisa existir aqui), regime tributário, e um bloco de imposto completo com interruptor de **cálculo automático**. Entrada por **XML** (arquivo até 2 MB) ou manual; o "buscador de notas" que puxa da Sefaz fica pra F8, junto com a NF-e.
22. **`empresas`** ⬜ a construir — **sem tela por enquanto** (decidido em setembro/2026). Uma única linha (Desk Company + CNPJ), mais o campo **`empresa_id`** em `depositos` e em `stores`, já preenchido com ela. Depósito e CNPJ são coisas independentes: um CNPJ tem vários depósitos, um depósito pertence a um CNPJ. Hoje é 1 CNPJ com N depósitos; quando o usuário dividir o grupo, cada depósito só passa a apontar para outra empresa — **nenhuma regra nova**.
    - **Por que agora e não depois:** com 2 CNPJs, **transferir mercadoria entre depósitos de empresas diferentes deixa de ser movimento interno e vira operação fiscal** (nota de transferência, CFOP próprio, imposto). Com o campo existindo, a tela de Transferência Entre Estoques só pergunta "mesma empresa?" e escolhe o caminho; sem ele, refaz-se Transferência, Notas de Entrada e os relatórios financeiros. O custo hoje é um campo que ninguém vê.
    - **Regra documentada:** transferência entre depósitos da **mesma** empresa = movimento interno no ledger; entre empresas **diferentes** = operação fiscal, **bloqueada com mensagem explícita** enquanto o módulo fiscal não existir.
    - A tela de cadastro de Empresas entra em **Configurações** no dia em que o segundo CNPJ existir de verdade — não antes.
23. **Divergência na conferência** ✅ na tela de Conferência — taxonomia de motivos, destino da avaria e comunicado ao fornecedor (decidido em setembro/2026, **reescrito em setembro/2026 após pesquisa na legislação** — o que estava aqui antes era dedução minha; agora tem base citada). A conferência **nunca trava**: o que chegou entra, o resto vira registro. Cada item tem **Qtde da nota | Qtde conferida | Divergência**, e divergência diferente de zero exige um **motivo**.
    - **O que a pesquisa confirmou e o que ela corrigiu.** A regra que tínhamos deduzido — *faltou não é devolução* — está certa e tem base legal. Mas o instrumento que eu havia chamado de **"nota de crédito" não existe no fiscal brasileiro**: era vocabulário de ERP estrangeiro. Os caminhos reais são os dois descritos abaixo, e o sistema passa a falar o nome certo deles.
    - **Falta na entrega (nota diz 10, chegaram 8) — procedimento padrão.** O destinatário (nós) **escritura a nota pelo valor efetivamente recebido**, credita imposto só sobre o que recebeu, **anota a divergência** (coluna Observações do livro de Entradas, ou Registro C195 na EFD-ICMS/IPI) e **comunica formalmente o fornecedor**. O fornecedor então escolhe um de dois: (a) manda o faltante com **NF complementar referenciando a NF original e com CFOP de venda** — não "outras saídas" —, ou (b) as partes **se compõem financeiramente** (abatimento no título) e ele pede restituição do imposto pago a maior. Base: Respostas à Consulta Tributária 23947/2021 e 14439/2016, arts. 61, 63 e 204 do RICMS/SP; Portaria CAT 147/2011 estende o procedimento ao Simples Nacional.
    - **Carta de correção NÃO resolve divergência de quantidade.** O Ajuste SINIEF 01/2007 proíbe a CC-e de mexer nas "variáveis que determinam o valor do imposto": base de cálculo, alíquota, diferença de preço e **quantidade**. Regra dura de tela: em divergência de quantidade ou de valor, o sistema **nunca** oferece "pedir carta de correção" — seria ensinar o usuário a fazer errado.
    - **Devolução simbólica é vedada** (art. 204 do RICMS/SP): nota fiscal sem circulação real de mercadoria não pode existir. Isso fecha a porta do atalho preguiçoso de "emitir uma devolução das 2 unidades que nunca chegaram".
    - **Recusa e devolução são caminhos diferentes — e só um funciona para a Desk hoje:**
      - **Recusa** (a mercadoria volta com o transportador, no ato): motivo escrito **no verso do DANFE**, evento de **Manifestação do Destinatário = "Operação não Realizada"**, e **o FORNECEDOR emite a NF-e de entrada** referenciando a original, figurando como remetente e destinatário ao mesmo tempo, com CFOP correlato (saída 6.101 → entrada 2.101) e o motivo no campo Informações Adicionais. **Não exige NF-e nossa** — é o caminho viável enquanto a Desk não emite nota. Base: RC 27259/2023, arts. 204, 453, 57 e 63 do RICMS/SP.
      - **Devolução** (a mercadoria entrou e depois volta): **nós** temos de emitir a NF-e de devolução referenciando a original. **Não conseguimos hoje.** O sistema trata isso como o item 22 trata transferência entre CNPJs: registra a intenção, deixa o saldo `bloqueado` e **bloqueia a saída com mensagem explícita** até o módulo fiscal existir.
      - **Isso refina o que já havíamos aprovado sobre avaria:** avaria **vista na doca** é **recusa** (volta no caminhão, o fornecedor resolve o papel, nada entra no estoque); avaria **descoberta depois** é que entra e vai para o endereço de **Avaria** com saldo **`bloqueado`**, esperando o módulo de devolução. A tela de conferência oferece as duas saídas conforme o transportador ainda estar ou não na doca.
    - **Chegou a MAIS do que a nota.** Caso real e o inverso do anterior: existe mercadoria física sem documento que a cubra. O excedente é registrado, **não é endereçado** e fica **`bloqueado`** até o fornecedor emitir a NF complementar ou o excedente voltar. Nunca virar estoque disponível "porque chegou".
    - **Prazos de manifestação são prazos reais e o sistema vai contá-los:** Ciência da Emissão **10 dias**; Confirmação da Operação, Desconhecimento da Operação e Operação não Realizada **180 dias**, todos contados da autorização da NF-e (NT 2020.001 / Ajuste SINIEF 44/20). Cancelamento da NF-e só cabe **sem** circulação da mercadoria e dentro do prazo legal (em SP, 480 horas). Esses prazos entram como contagem visível em **Entrada de Notas**, não em Conferência — quem manifesta é quem recebe o documento, antes de conferir a carga.
    - **Taxonomia oficial de motivo de divergência** (a lista da tela, fechada): `faltou_na_entrega`, `avaria`, `item_divergente` (veio outro produto), `excedente` (chegou a mais), `recusado`. Cada motivo já sabe que caminho abre — nenhum deles deixa o usuário escolher um caminho fiscalmente errado.
    - **Comunicado de divergência ao fornecedor** deixa de ser educação e passa a ser **exigência do procedimento**: o fisco manda comunicar. A conferência gera esse registro (chave da NF, itens, quantidade da nota, quantidade recebida, motivo), imprimível e enviável, e ele fica anexado à conferência. **Não é tela nova**, é saída da tela de Conferência.
    - **A conta a pagar nasce pelo VALOR DA NOTA**, não pelo conferido, com a diferença virando **pendência visível com o fornecedor** — é o que o fornecedor vai cobrar de fato. A **escrituração fiscal**, essa sim, é pelo valor recebido. São dois livros diferentes e é normal divergirem nesse intervalo; o que não pode é o sistema editar a nota. Nota fiscal é documento, não campo editável: se o sistema "corrigir" a nota sozinho, sistema e contabilidade divergem e ninguém descobre por meses.
    - **Ponto ainda aberto, único da lista sem fonte oficial fechada:** as respostas a consulta tratam de recusa **total**. A recusa **parcial** (recebo 8, recuso 2 no ato) é prática corrente de mercado, mas o evento de manifestação é **por nota inteira** — não existe evento "recusei parte". O registro que faz sentido é Confirmação da Operação + comunicado de divergência + NF de entrada do fornecedor pela parte recusada. **Confirmar com o contador da Desk antes de fechar essa tela.**
    - **Ressalva honesta:** não sou contador. As respostas a consulta citadas são de **São Paulo** e a regra de escrituração pode variar por estado; já a proibição da carta de correção e os prazos de manifestação são **nacionais**. O desenho acima existe para o sistema não induzir erro — o fechamento fiscal passa pelo contador.
    - **Não confundir com o item 13:** aquele "Devolução" é status de `orders` — devolução de **venda** (cliente devolve para nós). Devolução de **compra** (nós devolvemos ao fornecedor) é outra coisa, ainda não existe no schema, e entra junto com o módulo fiscal.

24. **RLS desde o dia 1** em toda tabela: vitrines só **leem** produto ativo/com estoque, só **inserem** cliente/pedido, só **leem** o status do próprio pedido via Realtime. Sem acesso a financeiro, estoque de outra loja, ou dados de outra origem.

## 4. Roadmap — fases-portão

Cada fase só fecha quando funciona **de ponta a ponta**, não quando as telas existem.

| Fase | Portão de saída | O que entra |
|---|---|---|
| **F0 — Fundação técnica** | Push no GitHub → deploy automático na Vercel funcionando pro ERP E pra 1 vitrine, ambos lendo/escrevendo no mesmo Supabase com RLS ativo | Schema da seção 3, RLS, Design System, pipelines |
| **F1 — Acesso & Core** | Login funcional + Dashboard (já pronto) + Permissões básicas | Auth JWT, Roles (Owner/Admin/Usuário), SMTP Resend, Central de Notificações, Logs |
| **F2 — Cadastros base** ⏳ *em andamento* | Um produto cadastrado no ERP já aparece na vitrine certa | Clientes ✅, Fornecedores ✅, Categorias ✅, Produtos ✅, Lojas Desk ✅, Departamento de Produtos ✅, Seção de Produtos ✅, Embalagens ✅, Marcas de Produtos ✅, Vendedores ✅, Depósitos ✅ — falta: Transportadora (Desk Flash). *Metas e Performance de Vendas (menu Vendas) também já construídos, adiantados por dependerem de Lojas Desk.* |
| **F3 — Vitrine MVP (Desk Shope)** | Cliente real navega, compra com pagamento real, vê status mudar em tempo real | Storefront (catálogo/carrinho/checkout), InfinityPay + webhook + `payment_check`, cadastro automático no checkout, "Meus Pedidos" com Realtime |
| **F4 — Fulfillment** | Pedido sai de "Confirmado" até "Entregue" com etiqueta real e rastreio | Separação (pick and pack, bipagem), Etiquetagem, Expedição + Melhor Envio, status em tempo real na vitrine |
| **F5 — Estoque & Financeiro básico** ⏳ *em andamento* | Estoque baixa sozinho ao separar; Caixa reflete a venda | Depósitos ✅, Controle de Estoques ✅, Endereços de Estoque ✅, Ordens de Compra ✅, Entrada de Notas ✅ (listagem + detalhe), Conferência de Compra ✅ (fila + contagem), Endereçamento ✅ (ex-"Produtos sem Endereço", renomeado em 15/set/2026) — Controle de Estoques v2 ✅ (listagem + detalhe + acerto inline, 15/set/2026) — **Reposição** ✅ (novo), **Acerto de Estoque** ✅ (inline + multi-produto, 15/set/2026) — **Transferência Entre Estoques** ✅ (16/set/2026), **Inventário de Estoque** ✅ (16/set/2026 — fecha a parte de estoque da fase) — Financeiro: **Contas Financeiras** ✅, **Contas Bancárias** ✅, **Categorias Financeiras** ✅, **Caixa e Bancos** ✅ (extrato + lançamento), **Contas a Pagar** ✅ (listagem + conta, **aprovado em 29/set/2026**) — falta: **Contas a Receber**, que espera Pedidos de Venda |
| **F6 — Lançamento Desk Shope** | Primeira venda real em produção, domínio próprio | Testes E2E, deploy final, ajustes finos |
| **F7 — Réplica Desk Tech** | Módulo de Ordens de Serviço rodando (não reaproveita "Pedidos") | OS, diagnóstico, técnicos, peças do estoque central, sync de identidade/números com o hub |
| **F8 — Pós-MVP** | Sem prazo fixo | Devoluções completas, **NF-e**, comissões, Programa de Indicação/Cashback, relatórios avançados, import/export, CRM, PDV, Marketplaces (Shopee/ML/Amazon/Magalu), Desk Flash como transportadora própria, Conciliação bancária, testes E2E/segurança/CI-CD completos |

**Meta:** F0–F6 concluídas até dezembro/2026 — Desk Shope rodando de ponta a ponta, vendendo de verdade. F7 e F8 ficam pra 2027, como sequência natural, não como fracasso.

## 5. Regras de Ouro

1. Não pular fases — uma depende da outra.
2. Schema do banco completo ANTES de qualquer tela.
3. Uma conta, um ambiente, do início ao fim.
4. Se quebrar, para, analisa, conserta — não acumula.
5. Toda tabela já nasce com RLS configurado.
6. Nada de "depois a gente arruma".
7. Cada dia termina com revisão do que aprendemos.
8. Funciona > Perfeito (MVP first).
9. Escopo da fase atual congelado — ideias novas viram item de F8, não interrupção.
10. Documentar as decisões antes de virarem prompt pro Lovable.

## 6. Protocolo Anti-Retrabalho

Baseado em fricções reais das duas tentativas anteriores — cada regra existe porque algo específico já deu retrabalho.

1. **Visual antes de código.** Toda mudança de UI passa por preview/HTML validado aqui antes de virar prompt pro Lovable.
2. **Schema primeiro, tela depois.** Nenhuma tela nova vai pro Lovable antes do schema das tabelas envolvidas estar decidido e documentado.
3. **Ler o código existente antes de prescrever.** Nunca assumir estrutura de um componente que já existe — pedir/ler o código atual primeiro.
4. **Uma decisão, um lugar.** Toda decisão de plataforma/gateway/schema/arquitetura fecha no estúdio (aqui), documentada, e só depois vira prompt. Nunca decidir estrutural direto na conversa com o Lovable.
5. **Escopo da fase é congelado.** "Já que estamos aqui, vamos fazer também" vira item de backlog em F8, não interrupção no prompt atual.
6. **Portão de fase = testado de ponta a ponta.** "As telas existem" não é sinônimo de "a fase está pronta".
7. **Quebrou, para.** Se uma mudança nova quebrar algo que já funcionava, conserta antes de seguir adiante.
8. **Prompt enviado = prompt registrado.** Todo prompt real mandado pro Lovable é colado de volta aqui.
9. **Correções do Lovable são bem-vindas, mas revisadas** — aceitas e registradas, nunca silenciosamente ignoradas.
10. **Um responsável final por decisão de arquitetura** — aprovação explícita antes de virar prompt, nunca decidido "no calor" de uma correção pontual.

### Checklist rápido antes de mandar qualquer prompt pro Lovable
- [ ] Depende de schema ainda não decidido? → decide aqui primeiro
- [ ] Envolve UI? → tem preview/HTML aprovado?
- [ ] Mexe em componente que já existe? → já vi o código atual?
- [ ] Está dentro do escopo da fase atual? → se não, vai pro backlog (F8)
- [ ] O prompt final está registrado aqui depois de enviado?

**Regra de pesquisa — a documentação do Olist vem antes do palpite (21/set/2026, pedido do usuário):** sempre que houver dúvida sobre o que um módulo, campo ou função faz, **consultar `ajuda.olist.com` antes de decidir**, e registrar o que a fonte disse. Já mudou o desenho três vezes: confirmou que *conta financeira é o guarda-chuva e carrega o saldo*, entregou o fluxo inteiro da **conciliação de extrato** (com os campos de taxa, juros, desconto e acréscimo), e acrescentou a **chave Pix** ao cadastro de contas bancárias, que o print sozinho não mostrava. Palpite plausível é o tipo de erro que só aparece depois de a tela estar pronta.

**Regra de entrega — imagens (21/set/2026, pedido do usuário):** screenshot de QA **só quando a tela ainda vai ser analisada antes de existir** — proposta visual, comparação de layout, decisão a tomar. **Se a página já está pronta, manda só o HTML.** O print continua sendo tirado e lido por mim no portão de qualidade (foi ele que pegou o campo de senha de 1.400px); o que muda é não anexar junto com o arquivo pronto.

## 7. Estado atual do projeto (atualizado)

- ✅ **F0 (parcial):** Design System travado e em produção nos protótipos — mas **não é mais "Cyber-Corporate"**. Isso foi abandonado; o padrão atual é **clean, sem glow, sem glassmorphism, inspirado no Olist** (fundo escuro `#101010`, fonte Nunito, sidebar cartão único flutuante). Ver `design-system-oficial-desk-company.md` pro padrão real e completo.
- ✅ **F1 (parcial):** Sidebar completa (9 módulos, flyouts, tema claro/escuro, recolher menu) + Dashboard KPIs funcionando com dado mock.
- ⏳ **F2 (em andamento):** Cadastros de Clientes, Fornecedores, Categorias, Produtos, Lojas Desk, Departamento de Produtos, Seção de Produtos, Embalagens, Marcas de Produtos e Vendedores prontos, testados, com seleção em massa e modais de confirmação padronizados (Vendedores é o primeiro módulo do sistema com exclusão suave — ver design-system §8.1). Metas e Performance de Vendas (menu Vendas) também prontos. Falta: Transportadora (Desk Flash) — combinado deixar por último, já que a Desk Flash como transportadora própria ainda precisa ser desenhada.
- ⏳ **F5 (em andamento):** Estoque completo — 14 telas, de Ordens de Compra a Inventário — e o Financeiro sem Contas a Receber: Contas Financeiras, Contas Bancárias, Categorias Financeiras, Caixa e Bancos (extrato + lançamento) e Contas a Pagar (listagem + conta, **aprovado em 29/set/2026**). Contas a Receber espera Pedidos de Venda.
- ✅ **Configurações (adiantado, 18–21/set/2026):** hub com busca e nove abas + Parâmetros de estoque, Interface do usuário, Confirmações por senha, Registro de atividades, Configurações da conferência e dos cadastros de clientes e de produtos.
- ⬜ F3 em diante: não iniciado. **Próximo módulo: Vendas / Pedidos de Venda** — é a dependência de Contas a Receber, da aba de reservas do estoque e do Desk Help.

**Contagem oficial de páginas construídas até aqui: 52** *(atualizada em 29/set/2026; eram 31 no texto até esta data)* (ver tabela completa em `design-system-oficial-desk-company.md` §12). Não conta o `pagina-molde-referencia.html` (é molde/exemplo, não uma tela funcional do sistema):
1-2. Clientes (listagem + detalhe)
3-4. Fornecedores (listagem + detalhe)
5. Categorias (listagem única)
6-7. Produtos (listagem + detalhe)
8-9. Lojas Desk (listagem + detalhe)
10. Metas
11. Performance de Vendas
12-15. Início (Dashboard KPIs, Boas-vindas, Agenda, Minha Conta)
16. Departamento de Produtos (listagem única)
17. Seção de Produtos (listagem única, com cascata Categoria→Departamento)
18. Embalagens de Produtos (listagem única, com Tipo→campos/diagrama dinâmico)
19. Marcas de Produtos (listagem única, com Loja(s) aplicável(is) multi-seleção)
20-21. Vendedores (listagem + detalhe — exclusão suave, vínculo opcional a Loja Desk/"autônomo", painel mocado de senha de acesso)
22. Depósitos (listagem única + drawer — primeira tela da F5; exclusão suave em 3 abas, depósito principal protegido, cor do avatar por Tipo com contraste resolvido por tema)
23. Controle de Estoques (menu Estoque — primeira tela de consulta em tabela do sistema; saldo por depósito, alerta de mínimo, drawer de extrato, reservado/disponível desabilitados)
24. Endereços de Estoque (código composto derivado das partes, único por depósito; gerador em massa por faixas; 6 tipos com paleta categórica própria aferida por contraste; exclusão bloqueada quando há produto alocado)
25-26. Ordens de Compra (listagem + detalhe) — abas de situação contadoras e filtro de período em popover na listagem; no detalhe, primeira tabela editável do sistema, totais ao vivo, parcelas geradas da condição de pagamento e busca de itens mostrando saldo
27. Entrada de Notas (menu Estoque) — o documento fiscal que chega do fornecedor, com a **coluna de Manifestação do Destinatário contando os prazos reais** (10 dias de Ciência, 180 da definitiva), chave de acesso com DV calculado de verdade, e o drawer da nota divergente trazendo o procedimento escrito na tela
28. Conferência (aberta pela fila de Conferência de Compra — não tem item de menu, design system §12.3) — a tela onde a mercadoria vira estoque: **conferência cega por padrão**, motivo filtrado pelo sinal da divergência, avaria perguntando se ficou conosco ou voltou no caminhão, e o **comunicado ao fornecedor gerado no fechamento**
29. Endereçamento (menu Estoque) — a fila que trava a venda, com o tempo parado mudando de cor sozinho; endereço é por depósito, e saldo bloqueado por avaria só entra em endereço de Avaria
30. Conferência de Compra (menu Estoque) — **a fila do galpão**, que faltava antes da conferência operacional: abas aguardando entrada / pronto para conferir / em conferência / conferidas, coluna de espera que muda de cor, e o **modal de receber mercadorias** com busca por fornecedor, número ou chave de acesso (o leitor de código bipa a chave e dá Enter)
31. Nota de Entrada — detalhe (menu Estoque) — o cadastro da nota, com **bloco de pendências no topo** listando tudo que falta de uma vez, cada item levando ao campo; chave de acesso com dígito verificador conferido de verdade e data de entrada que não pode anteceder a emissão
32. Controle de Estoques — detalhe (saldo por depósito e estágio, extrato, acerto inline)
33. Reposição (bases de picking abaixo do mínimo, coleta total ou parcial)
34. Acerto de Estoque (multi-produto, baixa por perda com pendência fiscal)
35-36. Transferência Entre Estoques (listagem + nova transferência)
37. Inventário de Estoque (gerar, planilha ou coletor)
38. Configurações ERP — o hub
39. Parâmetros de estoque
40. Interface do usuário
41. Confirmações por senha (matriz módulo × verbo)
42. Registro de atividades
43. Configurações da conferência
44. Configurações do cadastro de clientes
45. Configurações do cadastro de produtos
46. Contas financeiras
47. Contas bancárias
48. Categorias financeiras
49-50. Caixa e Bancos (extrato + lançamento)
51-52. Contas a Pagar (listagem + conta a pagar)

**Varredura de consistência concluída em setembro/2026** — antes de seguir pros próximos módulos, os 22 arquivos do projeto passaram por uma auditoria completa que fechou todas as pendências técnicas que estavam em aberto: o seletor de tema foi escopado nos 15 arquivos que ainda estavam soltos (2 com bug ativo, 13 latentes), o `max-height` do dropdown foi aplicado nas 6 telas que faltavam, e três arquivos que constavam como entregues mas nunca tinham chegado na pasta do usuário foram regravados no lugar certo (ver `design-system-oficial-desk-company.md` §14). O plugin/skill subiu pra 0.4.0: a auditoria automatizada ganhou uma seção 4B (consistência entre telas) e um teste de fundo computado dos campos de formulário, então esses quatro tipos de desvio agora reprovam sozinhos, sem depender de alguém lembrar do checklist. **Nenhuma pendência técnica em aberto nos módulos já construídos.**

**Abertura de F5 (setembro/2026):** antes de abrir Estoque, a auditoria completa foi re-rodada nos 22 arquivos e apontou um único gap real — `pagina-cadastros-lojas-desk.html` era a última listagem de cadastro **sem o rodapé de paginação** do design-system §7, embora o §12 já afirmasse que todos os cadastros seguiam o padrão. Corrigido no mesmo dia: paginação padrão adicionada (resumo + dropdown 10/25/50/100 + anterior/próxima), "Selecionar todos" escopado à página atual, e o componente `.dropdown-select` completo (CSS + `inicializarDropdownSelect`, com `max-height:240px`) que essa página ainda não tinha. Validado por auditoria automatizada limpa + teste interativo no navegador + screenshot. Metas e Performance de Vendas seguem sem paginação de propósito — operam sobre o conjunto fixo de 3 lojas, não sobre uma lista que cresce; exceção consciente, não pendência.

**Lição de contraste de cor documentada em `design-system-oficial-desk-company.md` §1** (`--active-bg` nunca é cor de texto, só fundo — bug real que aconteceu e foi corrigido) — vale ler antes de codar qualquer tela nova que use cor pra indicar positivo/negativo.

## 8. Como continuar num chat novo

**Já está tudo montado — não precisa refazer nada disso.** Os 3 arquivos abaixo estão anexados ao Contexto do Projeto de forma permanente, valendo pra todo chat novo dentro dele:
1. Este arquivo (`arquitetura-roadmap-desk-company.md`)
2. `design-system-oficial-desk-company.md`
3. `pagina-molde-referencia.html`

E o plugin **`desk-company-erp` (hoje na versão 0.4.0)** está instalado, trazendo as duas skills: `desk-company-erp` (design system + como construir) e `desk-company-page-qa` (portão de qualidade). Elas entram sozinhas quando a conversa falar de Desk Company — não precisa invocar.

> ⚠️ O antigo instalador `desk-company-erp.skill` **não existe mais** e não deve ser procurado: foi substituído pelo formato `.plugin`, que inclui a skill de QA (o `.skill` só tinha a primeira). Ao atualizar as skills, o que se entrega é um arquivo `.plugin` novo, que o usuário instala clicando no card do chat.

**Como abrir um chat novo:** basta dizer o que quer ("vamos construir o módulo X", "ajusta tal campo"). A skill carrega sozinha e o Passo 0 dela lista a pasta local antes de qualquer coisa. Não cole resumo manual da sessão anterior — se algo importante não estiver nestes 2 `.md`, o erro foi não ter documentado, e a solução é documentar, não repetir na conversa.

**Os 2 `.md` são atualizados direto no Projeto** (via `project_write`) ao fim de cada sessão que muda algo — não é preciso reanexar arquivo. Quem escreve tem que gravar nos dois lugares: no Projeto **e** na pasta local do usuário.

> **Atualizado em 29/set/2026:** a F5 fechou tudo o que não depende de venda. **O próximo módulo é Vendas / Pedidos de Venda.** O parágrafo abaixo é o histórico da abertura da F5.

**Próximo passo (em andamento, set/2026):** **F5 — Estoque**, aberta em setembro/2026. Já construídas: **Depósitos**, **Controle de Estoques** e **Endereços de Estoque**, mais os ajustes de Depósitos (interruptor de endereçamento) e Lojas Desk (depósito padrão). Ordens de Compra está **completa** (listagem + detalhe), e **Entrada de Notas** e **Conferência** também — as duas construídas em cima das regras de divergência do §3 item 23, depois da pesquisa na legislação. O fluxo **entrada → conferência → endereçamento → vendas** está fechado de ponta a ponta: Nota de Entrada (listagem + cadastro) → Conferência de Compra (fila) → Conferência (contagem cega) → Endereçamento. A próxima é **Controle de Estoques v2**, com as colunas de situação do saldo. Os prints de referência de Ordens de Compra e de Conferência já foram recebidos e estão destrinchados no §3 item 21. Duas decisões de schema fechadas na abertura, ambas já registradas no §3: saldo **por depósito nomeado** (item 15, revisando o saldo central do item 2) e tabela **`lotes` opcional desde já** (item 16), pra Desk Make/Desk Food não custarem migração depois. Pelo §3 item 5, Controle de Estoques é tela de **leitura + extrato** — quem escreve no ledger é Acerto de Estoque, Entrada de Notas e Transferência Entre Estoques. O usuário envia prints de referência (padrão Olist) antes de cada módulo novo; a construção só começa depois deles.

**Ordem de construção da F5 (definida em setembro/2026, depois dos prints do Olist):** `depositos` **vem antes de Controle de Estoques** — ✅ **feito**, é a primeira tela da fase. Nos prints, toda tela de estoque do Olist aterrissa num depósito ("Depósito de destino: Geral" na importação por planilha e por coletor), e o próprio saldo é por depósito — construir a listagem primeiro obrigaria a re-fazer filtro, colunas e drawer depois. Sequência **revisada em setembro/2026**, depois que o usuário trouxe o fluxo de recebimento completo (ver §3 itens 17–21): **1) Endereços de Estoque ✅ → 2) ajuste em Depósitos (interruptor de endereçamento) e Lojas Desk (depósito padrão) ✅ → 3) Ordens de Compra ✅ (listagem + detalhe) → 4) Entrada de Notas ✅ → 5) Conferência (cega) ✅ → 6) Endereçamento + aba Endereços no Produtos-detalhe → 7) Controle de Estoques v2 (colunas de situação do saldo) → 8) Acerto de Estoque → 9) Transferência Entre Estoques → 10) Inventário de Estoque**.

**Acerto de Estoque perdeu a primeira posição de propósito:** quem alimenta a fila de endereçamento é a Entrada de Notas, e sem ela a tela de **Endereçamento** nasce vazia. **Essa tela não é um extra** — é o que torna a trava de venda sobrevivível: sem uma fila visível, alguém esquece de endereçar, o produto some da vitrine e ninguém sabe por quê. Ela mostra produto, depósito, quantidade parada, nota de origem e **há quanto tempo está esperando** (a coluna que gera ação), com o botão de endereçar sem sair da tela. Inventário fica por último por decisão do usuário (é um fluxo próprio de 3 caminhos — gerar/planilha/coletor — e só faz sentido com saldo real pra conferir).

**Nomenclatura travada a partir dos prints:** as colunas de saldo usam os nomes do Olist — **Estoque físico**, **Estoque reservado**, **Estoque disponível**. Não usar "Saldo atual". **A fórmula do Olist (`disponível = físico − reservado`) foi DESCARTADA em 14/set/2026** — ela funciona lá porque o Olist não tem endereçamento obrigatório; aqui daria disponível demais e mataria a trava de venda, que é o motivo da tela existir. Vale a do item 19: **`disponível = endereçado − reservado − bloqueado`**, ou seja, `físico − a_enderecar − reservado − bloqueado`. As abas da listagem de Controle de Estoques são `todos / simples / kits / matéria-prima`, que já batem com os tipos existentes no cadastro de Produtos. **Estoque reservado e disponível nascem como coluna visível e desabilitada**, com o hint de "Reservado — calculado quando o módulo de Pedidos existir", mesmo tratamento dos campos fiscais (§11 do design-system): dependem de `orders`, que só existe em F3/F4, e mocar número numa tela cuja função é ser a fonte da verdade do saldo seria pior que não ter.

**Inventário de Estoque ✅ construído em 16/set/2026** (`pagina-estoque-inventario.html`) — o que os prints traziam: índice com 3 caminhos — *Gerar inventário*, *Importar por planilha* (CSV/XLS/XLSX até 2mb, com **Depósito de destino**), *Importar por coletor* (TXT até 2mb, validando por GTIN/EAN, SKU ou ambos, também com Depósito de destino). O arquivo do coletor é **um código de barras por linha, repetido** — a repetição É a quantidade (3 linhas iguais = 3 unidades), não precisa de resumo. O inventário gerado abre em modo leitura (Produto, Código SKU, Preço, UN, Localização, Estoque atual, Estoque disponível) com os botões *exibir filtros / imprimir / download / informar quantidades*; "informar quantidades" acrescenta a coluna editável **Qtde inventário** e troca o botão por "salvar quantidades", que reescreve o saldo. Os filtros de geração incluem Busca, Tags, **Categoria** (drawer lateral com busca + botão "atribuir categoria"), Exibir (todos / com saldo / sem saldo), Situação do produto (Ativos / Inativos / Todos exceto excluídos), Fornecedor e **Valor baseado em** (dropdown agrupado: Preço de compra → última compra; Preço de custo → custo atual, custo médio atual; Preço de venda → venda atual).

**Decisões nossas em cima desses prints (16/set/2026) — é aqui que o Inventário deixa de ser cópia:**

24. **O inventário bloqueia o depósito inteiro, da abertura ao fechamento.** É a única diferença estrutural entre ele e o Acerto, e é o que justifica ele existir tendo Acerto: contagem com movimentação acontecendo no meio não é contagem, é ficção com carimbo. Venda, transferência e acerto naquele depósito são recusados enquanto houver inventário aberto. **Nota em conferência continua entrando** (o galpão não para de receber) mas fica **fora da contagem** — coerente com o item 19, onde `em_conferencia` não é estoque físico. Consequência a implementar no Lovable: toda escrita no ledger passa a checar se existe inventário aberto no depósito alvo.

25. **Ausência de leitura não é zero.** Produto com saldo no depósito que não apareceu no arquivo do coletor ou da planilha entra como **não contado**, e não contado **não mexe no saldo** no fechamento. Zerar automaticamente seria correto só se toda importação fosse varredura completa do depósito — e não é: coletor que não passou num corredor produziria baixa total de produtos bons, sem ninguém decidir nada. A varredura completa continua possível, mas **explícita**: ação **"Zerar os não contados"** em Mais ações, com confirmação que diz o que vai acontecer. Regra geral que sai daqui: **o sistema nunca infere uma baixa a partir de silêncio.**

26. **A diferença do inventário não é um tipo novo de movimento.** Positiva entra pela **mesma regra de entrada do item 19** (base de picking no depósito → nasce `disponivel` até a capacidade; excedente e produto sem base → `a_enderecar`, não vende) e **não gera documento fiscal** — sobra não tem nota. Negativa sai do `disponivel`, base de picking primeiro, e nasce com **pendência fiscal de NF-e CFOP 5.927** (mesmo tratamento do Acerto, item 23), sem travar. **`reservado` e `bloqueado` não são tocados:** inventário conta prateleira, não desfaz reserva de pedido nem libera avaria — quem faz isso é o Acerto, com motivo próprio. Se a falta não tiver lastro nas linhas disponíveis, **o saldo fica negativo e visível**, de propósito.

27. **Contagem é por produto no depósito; o endereço é derivado.** Os prints contam por produto (é o que o coletor produz — um código, não um código + posição), mas nosso saldo vive por **(produto, depósito, endereço)**. A ponte é a base de picking: a diferença é aplicada na base quando ela existe, e cai em `a_enderecar` quando não existe ou não cabe. **Isto é uma simplificação consciente** — inventário por endereço (contar posição por posição) é o que a Unidade Logística destrava quando o galpão tiver coletor, e fica registrado aqui como o ponto exato onde a UL muda esta tela. Até lá, a regra vale e está escrita na tela.

**Duas defasagens de sidebar achadas e corrigidas no passe de 15/set/2026** (apareceram só porque o rename obrigou a varrer os 33 arquivos):

- **A `Conferência de Compra` nunca teve entrada no menu**, em tela nenhuma — a tela está construída desde setembro e só era alcançável por link direto. Entrou nas 32 telas, na posição do fluxo (depois de Entrada de Notas, antes da Conferência).
- **O molde consolidado estava com a sidebar congelada antes do módulo de Estoque existir**: faltavam Conferência, Conferência de Compra, Endereçamento e Reposição. Como ele é a referência de onde se copia tela nova, qualquer tela nascida dele viria com menu incompleto. As **duas cópias do menu** (o molde tem dois preâmbulos, exceção conhecida da auditoria §1B) foram sincronizadas.
- **Lição:** a auditoria não pega isso — menu faltando não é erro de sintaxe, de contraste nem de runtime. Só aparece comparando o grupo de menu entre o molde e uma tela real. Vale incluir essa comparação no Passo 0 junto com a conferência do §12.

**Saldo por endereço + módulo de Reposição — decidido em 15/set/2026 (barganha):**

- **O saldo passa a ser por (produto, depósito, `endereco_id`)**, não mais só por (produto, depósito). É o **pré-requisito real** do módulo de Reposição: sem isso não há como responder "onde estão as 180 unidades que não estão na base". Ganhos imediatos, sem precisar de mais nada: coleta total (esvazia o endereço) ou parcial (abate a quantidade), inventário por endereço, e a coluna `Localização` deixando de ser texto para virar derivação do endereço principal (fecha o item 18).
- **Módulo de Reposição ✅ construído em 15/set/2026.** Mostra as bases de picking **abaixo do `minimo_base`**, diz **em quais endereços está o resto** do saldo daquele produto naquele depósito, e permite a coleta **total ou parcial** para repor a base — encerrando o endereço de origem ou abatendo a quantidade dele.
- **Acompanhamento base × total:** por par (produto, depósito), a tela compara o que está **na base de picking** contra o **saldo total do depósito**, e mostra a diferença como "aguardando reposição", com o endereço onde está guardada (recebimento, pulmão, aéreo).

**Unidade Logística (LPN) — ADIADO com gatilho definido, decidido em 15/set/2026:**

- **Não será construído agora.** Hoje a operação **não tem coletor nem impressora de etiqueta** (confirmado pelo usuário), e LPN sem bipe vira ficção: um palete movido na mão sem leitura deixa o sistema mentindo com confiança, o que é pior que não ter o recurso.
- **Gatilho para entrar (não é "algum dia"):** quando a **primeira movimentação for bipada em vez de digitada**, ou quando o mesmo produto passar a chegar em **lotes que precisem ser distinguidos**.
- **Costura deixada agora, para não virar reescrita depois:** todo movimento em `stock_movements` já nasce com **endereço de origem e destino**; acrescentar `unidade_id` mais tarde é **aditivo** e não quebra tela nenhuma. **Proibido desde já:** qualquer lógica que assuma "um produto por endereço" — é exatamente isso que impediria a unidade de carga de existir depois.
- **Nome escolhido:** **Unidade Logística (UL)**, com código próprio no padrão `DK-000148`. **Não usar "volume"** — o termo já está ocupado por nota fiscal e transporte ("Transportador / Volumes"), e a colisão confundiria a operação.

**Ordem de construção definida em 15/set/2026** (o usuário delegou a ordem, com o critério "nada quebrado, zero retrabalho"):

1. **Fundação** — sem tela nova: os rótulos de sidebar de todos os arquivos de uma vez (rename de Endereçamento + entrada de Reposição no menu), o rename do arquivo, e o saldo por endereço + `produto_enderecos` chegando às duas telas já construídas. **Vem primeiro porque toda tela nova nasceria com o rótulo velho e com a regra de entrada velha** — construir antes garantiria retrabalho nas telas seguintes.
2. **Reposição** — é o módulo que exercita o saldo por endereço com mais força; se o modelo estiver errado, é melhor descobrir aqui do que depois de mais uma tela em cima.
3. **Acerto de Estoque multi-produto** — passa a ser construído **uma vez só**, já com a regra final de entrada (consulta a base de picking) e com a origem da saída por endereço.
4. **Estoque Zero** ✅ — aba no Endereçamento, construída em 15/set/2026.

**Endereçamento (ex-"Produtos sem Endereço") — decisões fechadas em 15/set/2026:**

- **Módulo renomeado para `Endereçamento`**, arquivo `pagina-estoque-enderecamento.html` → **`pagina-estoque-enderecamento.html`**. Motivo: a tela deixa de ser só "saldo sem endereço" e passa a cuidar da relação **saldo ↔ endereço nos dois sentidos** — saldo sem endereço (precisa endereçar) e endereço sem saldo (precisa liberar a vaga). Com a aba nova, o nome antigo passaria a mentir.
- **O rename é propagação, não um arquivo:** **32 arquivos** carregavam o rótulo "Produtos sem Endereço" na sidebar (contagem real na execução, em 15/set/2026). Todos mudaram no mesmo passo, mais as referências nos dois `.md`, mais a mensagem de fechamento da Conferência de Compra que citava a tela pelo nome antigo. (Os `href` da sidebar são placeholder `#`, então o rename do arquivo não quebra link nenhum.)
- **Aba nova `Estoque Zero`**, depois de `Bloqueado`: produto **com endereço e sem saldo há mais de 7 dias**, ocupando vaga à toa. Conta os dias desde o movimento que zerou o saldo (derivável do ledger, não precisa de campo novo); **o contador zera se o produto receber saldo antes do prazo**.
- **A ação é `desvincular`, NUNCA `excluir endereço`.** A prateleira física não deixa de existir — excluir o endereço apagaria o mapa do galpão. Desvincular libera a vaga, e é exatamente o que destrava a regra já existente no cadastro de Endereços, onde a exclusão é bloqueada quando há produto alocado.
- **Não sugerir liberação quando existe Ordem de Compra em aberto para o produto.** Item que gira rápido zera e volta na semana seguinte; liberar o picking dele obriga a reposição a reendereçar, possivelmente num lugar pior. A checagem sai de graça porque o módulo de Ordens de Compra já existe.
- **✅ RESOLVIDO em 15/set/2026 — a aba `Estoque Zero` NÃO entra na contagem de `Todos`.** Hoje `Todos` = *a endereçar* + *bloqueado*, que são a mesma fila de trabalho (saldo esperando endereço). *Estoque Zero* é a fila inversa (endereço esperando saldo). Somar as duas num "Todos" produz um número que não é fila de nada. Decidir na construção: ou `Todos` continua cobrindo só o lado do endereçamento e `Estoque Zero` fica com contador próprio à parte, ou elimina-se o `Todos` e ficam as três abas explícitas.

**Transferência Entre Estoques — decisões fechadas em 15/set/2026 (barganha, antes de construir):**

- **Duas etapas, não uma.** Os depósitos são lugares físicos diferentes (Galpão Centro, Loja Física Aldeota, Showroom Parceiro Norte) e a viagem leva horas. Transferência imediata faria o saldo aparecer disponível no destino enquanto a mercadoria está no carro — e o separador do destino seria guiado até um endereço vazio, que é exatamente o modo de falha que a regra da base de picking existe para evitar.
- **A viagem acontece num depósito de `Trânsito`**, tipo que **já existe** no cadastro de Depósitos: `origem → depósito de Trânsito → destino`. Saldo em trânsito é saldo normal, num depósito normal.
    - **Por que assim e não com um estágio `em_transito`:** um estágio novo mexeria nos quatro baldes exclusivos do item 19 e nas cinco telas que leem estágio. Usando o depósito de Trânsito, **nenhuma regra existente muda** — só a tela de Transferência é nova.
- **Na confirmação do recebimento vale a regra de entrada do item 19:** tem base de picking no destino → `disponivel`; não tem → `a_enderecar`. Transferência é entrada no destino como qualquer outra.
- **Recebimento parcial é permitido e o resto FICA em trânsito.** Se saíram 10 e chegaram 8, as 2 continuam visíveis no depósito de Trânsito em vez de sumirem — quem resolve é um **Acerto** a partir do Trânsito, que já tem motivo estruturado e consequência fiscal. Sem reconstruir a máquina de divergência da Conferência uma terceira vez.
- **Empresa:** a regra do item 22 já está pronta — mesma `empresa_id` = movimento interno; diferente = operação fiscal, **bloqueada com mensagem explícita**. Hoje é 1 CNPJ, então o caminho existe e nunca dispara. Nada de novo a decidir.
- **Saldo `reservado` e `bloqueado` não transferem** — mesma regra do acerto. Reservado está comprometido com pedido; avaria transferida só espalharia o problema.

**Padrão de montagem de documento (decidido em 16/set/2026, a pedido do usuário):** quando a tela monta um **documento com várias linhas** — acerto, transferência, e daqui pra frente inventário — a lista de linhas fica na **área principal, em página própria**, nunca dentro de um painel lateral. O drawer serve só para **uma linha por vez**. Motivo: a lista é o objeto que a pessoa está construindo e precisa de largura, comparação entre linhas e rodapé de totais; painel lateral espreme tudo isso. A listagem do módulo e a página de montagem ficam **separadas**, e o botão de criar navega entre elas. Já aplicado em Acerto de Estoque e Transferência.

**Confirmações por usuário + senha — inventário vivo (decidido em 15/set/2026):** o usuário definiu que **cada ação que exige confirmação por senha vira um item com caixa de seleção no perfil de permissões** — o perfil diz o que aquele usuário pode ou não confirmar. Enquanto Configurações → Permissões de Usuários não existe, o checklist mora na aba **Acesso e Permissões** de Vendedores (mocado, mesmo padrão dos módulos acessíveis) — **construído em 16/set/2026**, e já mostra as ações de telas que ainda não existem, esmaecidas. Lista do que já existe:

| Ação | Onde | Situação |
|---|---|---|
| Criar / alterar senha de acesso de vendedor | Vendedores — detalhe | ✅ construída (pede senha do gerente/owner) |
| Finalizar acerto de estoque (lote) | Acerto de Estoque | ✅ construída |
| Confirmar recebimento de transferência | Transferência Entre Estoques | ✅ construída (16/set/2026) |
| Fechar inventário | Inventário de Estoque | ✅ 16/set/2026 |
| Cancelar ordem de compra já recebida | Ordens de Compra | ✅ 29/set/2026 (pede senha na listagem quando a seleção inclui ordem recebida) |

**Regra de ouro deste inventário:** toda vez que uma tela nova pedir senha para confirmar algo, **a ação entra nesta lista E no checklist do perfil no mesmo passo**. Confirmação que não aparece no perfil é permissão invisível — ninguém consegue auditar quem pode o quê.

**Atualização de 18/set/2026 — a lista virou código.** O inventário agora é o catálogo `ACOES_SENHA`, no bloco compartilhado dos 40 arquivos: `chave`, `nome`, `onde`, `pronto`, `exigePadrao`. Três leitores, **nenhuma cópia**: `pagina-configuracoes-confirmacoes-senha.html` (a ação exige senha?), as quatro telas que pedem senha (`exigeSenha(chave)` decide se o campo aparece) e o checklist do perfil em Vendedores (quem pode confirmar). No Lovable: `acoes_confirmacao` para o catálogo e `parametros.confirmacoes` para o que a empresa ligou ou desligou — **configuração da empresa, `usuario_id` nulo**. Acrescentar uma ação passa a ser **uma linha em um lugar só**, e ela aparece nas três telas no mesmo instante.

**Configurações → Parâmetros de Estoque (decidido em 15/set/2026 — ✅ construído em 18/set/2026; os números saíram das telas para o bloco `PARAM`):** os limiares de tempo hoje estão **cravados no código, espalhados por várias telas**. Quando o módulo de Configurações for desenhado, todos migram para lá. Lista viva do que já existe:

| Tela | Parâmetro cravado hoje |
|---|---|
| Conferência de Compra | Espera > 1 dia alerta, > 3 dias crítico |
| Endereçamento | Parado > 2 dias alerta, > 7 dias crítico |
| Endereçamento | Estoque zero > 7 dias (novo) |
| Controle de Estoques | Estoque mínimo — **já é por produto**, fica no cadastro, não vira parâmetro global |

**Não entram:** os prazos de Manifestação do Destinatário (10 e 180 dias) são **legais**, não configuráveis. Usuário vai mandar referências do módulo de Configurações depois; a intenção declarada é que ele configure várias ferramentas do sistema, não só estoque.

**Acerto de Estoque — decisões fechadas em 15/set/2026 (barganha, antes de construir):**

*Pesquisa fiscal (feita em 15/set/2026, fontes no fim do bloco).* Os dois lados do acerto **não são simétricos**:

- **Acerto que AUMENTA saldo (sobra de contagem):** não exige documento fiscal. Diferença positiva entre contagem física e contábil resolve-se por lançamento contábil. **Funciona hoje, sem trava.**
- **Acerto que DIMINUI saldo (perda, quebra, furto, extravio, consumo próprio):** exige **NF-e nossa**, **CFOP 5.927**, sem destaque de ICMS, destinatário a própria empresa, valor o **da última entrada**, mais **estorno do crédito** de ICMS/IPI/PIS/COFINS aproveitado na entrada. Exceção: produto **deteriorado ou vencido** não gera NF (deixou de ser mercadoria) — resolve com documento interno.
- **É a mesma parede da devolução ao fornecedor** (item 23), com uma diferença cruel: na devolução existe a saída da recusa, onde o fornecedor emite; na baixa por perda **não há terceiro que emita por nós**.
- **Decisão: registra, não bloqueia.** Produto quebrado já quebrou; travar a saída faz o operador mentir para o sistema, o que é pior que o problema fiscal. A saída é registrada, o saldo sai, e o acerto entra numa fila de **baixas pendentes de regularização fiscal** que o contador zera quando a NF-e existir. Mesma filosofia do resto do módulo: o sistema não induz erro, ele deixa a obrigação visível.
- **Ressalva honesta:** não sou contador, e as fontes consultadas são de **São Paulo**. O CFOP 5.927 e o estorno de crédito são do RICMS/SP; confirmar com o contador antes do fechamento fiscal.

*Regras de saldo:*

- **O acerto de saída destrava o beco sem saída da avaria.** Até aqui o saldo `bloqueado` não tinha saída nenhuma (item 23: a devolução está barrada). A baixa por perda é exatamente a saída dele — e como a decisão acima é registrar em vez de bloquear, **o acerto é o que finalmente fecha esse buraco**. Atualiza o item 23.
- **Origem da saída:** padrão **disponível**. O drawer mostra um **seletor de origem apenas quando o produto tem saldo em mais de um estágio elegível** (disponível / a endereçar / bloqueado) — na maioria esmagadora dos casos o operador não vê nada a mais. **Nunca sai de `reservado`**: esse saldo está comprometido com pedido confirmado e tirar dali quebraria o pedido de um cliente calado; se o único saldo for reservado, barra com mensagem explícita.
- **Entrada NÃO cai automaticamente em `a_enderecar`** — regra corrigida em 15/set/2026, depois da barganha da reposição. A versão anterior desta linha dizia "toda entrada, sem exceção", e estava errada: ignorava o item 18 e tratava produto conhecido igual a produto novo. A regra real, na entrada em um depósito **D** (o informado na nota):
    - **o produto TEM alocação de picking em D** (`produto_enderecos`) → fluxo de **reposição**, e o saldo nasce **`disponivel`**, vendável na hora;
    - **não tem** → nasce **`a_enderecar`** e trava a venda até ser endereçado.
    - **Endereço é por depósito, sempre.** Ter picking no Galpão Centro não vale nada quando a nota entrou na Bancada Desk Tech — lá é produto novo e trava. Vale para entrada por nota, por acerto e por devolução, sem distinção.
    - **Avaria não muda:** continua nascendo `bloqueado` e só entra em endereço de Avaria, tenha o produto base de picking ou não.
    - **Capacidade (decidido em 15/set/2026):** `enderecos.capacidade` já existe e hoje está vazia. Quando estiver **preenchida** e a chegada exceder o espaço livre da base, **o excedente cai em `a_enderecar`** (precisa de pulmão); **vazia**, tudo vai para `disponivel`. Assim a regra não faz nada até alguém decidir preencher capacidade, e passa a funcionar sozinha quando preencher.

- **`a_enderecar` e reposição são filas diferentes, e só uma trava venda** (15/set/2026):

    | Fila | O que é | Trava a venda? |
    |---|---|---|
    | **A endereçar** | produto sem base de picking naquele depósito | **sim** |
    | **Reposição** | produto com base, mercadoria a guardar/repor | **não** |

- **O separador é sempre guiado à base de picking**, independente de haver saldo guardado em outro endereço. A base é a **única face de separação**; todo o resto (pulmão, aéreo, recebimento) é **reserva** e não entra na separação. Regra escrita agora para a F4 herdar pronta.

- **Dois "mínimos" diferentes, que NUNCA podem virar o mesmo campo** (15/set/2026):

    | Campo | Onde mora | O que dispara | Dono |
    |---|---|---|---|
    | `estoque_minimo` | produto (já existe em `pagina-cadastros-produtos-detalhe.html`) | **comprar** — gerar ordem de compra | comprador |
    | `minimo_base` | `produto_enderecos` (produto × endereço de picking) | **repor** — mover do pulmão para a base | repositor |

    Mesma palavra, ações diferentes, donos diferentes. Se virarem um campo só, comprador e repositor brigam pelo mesmo número para sempre.
- **Custo médio:** entrada de acerto entra pelo **custo médio vigente**, não por preço novo. Motivo: a sobra de contagem **não é mercadoria nova** — aquelas unidades já foram compradas e o custo delas já passou pela média quando a nota foi lançada; trazer por preço novo **contaria o custo duas vezes**. O campo **Preço unitário fica visível e desabilitado** com a dica explicando (mesmo tratamento dos campos fiscais, §11 do design-system); ele destrava quando existir entrada com custo próprio de verdade — **Composição de Kit** (custo é a soma dos componentes) ou entrada sem nota. **Saída nunca move o custo médio.** A NF-e da baixa usa o **valor da última entrada**, que é outro número, guardado à parte no registro da pendência.
- **Motivo é campo estruturado, não texto livre** — é ele que decide se nasce NF-e, se estorna crédito ou se é só documento interno. **Filtrado pelo tipo** (entrada/saída), reaproveitando exatamente o padrão já construído na Conferência, onde o motivo é filtrado pelo sinal da divergência.

*Dois pontos de entrada, de propósito:*

1. **Inline em Controle de Estoques** — botão "incluir lançamento" na página de detalhe do produto, caminho rápido para um produto só (modelo do Olist).
2. **Tela própria de Acerto de Estoque, multi-produto** — barra de busca (descrição / SKU / GTIN, mesmo padrão da busca de itens de Ordens de Compra) → selecionar produto abre o drawer idêntico ao inline → "gravar produto" joga a linha numa tabela → repete → **"finalizar acerto de estoque"** pede confirmação com **usuário + senha** (reaproveita o painel já construído em Vendedores) e grava o lote.
   - **O lote é atômico**: ou grava tudo ou não grava nada, com **um número de documento único**. É isso que faz a tela valer como visão consolidada — o acerto em massa vira documento auditável, não N eventos soltos. O acerto inline também recebe número; o multi-produto só agrupa várias linhas sob um.
   - **Lote misto gera pendência fiscal parcial**: só as linhas de saída por perda entram na fila de regularização.
   - **Não é inventário.** Inventário bloqueia o saldo inteiro até o fechamento; o acerto não bloqueia nada. São módulos diferentes e o Inventário continua na fila da F5.
   - **Pendência:** como não trava saldo, duas pessoas podem acertar o mesmo produto ao mesmo tempo. No protótipo não aparece; no Lovable exige **trava otimista no ledger**.

*Fontes da pesquisa fiscal:* netcpa "ICMS/SP — Quebra ou Perda de Estoque"; rotinafiscal "Baixa de Estoque"; SEFAZ/SP Resposta à Consulta 23372/2021.

**Controle de Estoques v2 — decisões fechadas em 14/set/2026 (barganha, antes de construir):**

- **Colunas (9, medidas a 1440px: 986px de card, 0px de estouro):** Produto · Código (SKU) · Custo médio · Estoque físico · Mínimo · **A endereçar** · **Bloqueado** · Reservado · Disponível.
- **Saem da tabela:** **Preço** (é preço de venda; esta tela é a fonte da verdade do saldo, preço mora em Produtos) e **Localização**. A Localização sai por consequência do desenho, não por espaço: com estágios, uma linha tem saldo em vários endereços ao mesmo tempo (disponível no picking, bloqueado na Avaria, *a endereçar* em endereço nenhum) — uma célula só passaria a mentir. Endereço passa a ser assunto do **drawer de extrato**, que já mostra saldo por depósito.
- **`em conferência` não vira coluna** — não é estoque (item 19), então não pode ocupar coluna de estoque. Aparece como **marcador discreto na célula de Estoque físico** ("+30 a conferir", cor apagada) e como bloco próprio no drawer de extrato, fora do saldo. Quem monitora a fila é a tela de Conferência de Compra.
- **Medição (não estimativa):** 12 colunas estouram 266px; 11 estouram 120px; as variantes de 10 colunas estouram 38–71px. Só a de 9 cabe. Os 38px que faltavam na melhor variante de 10 só sairiam apertando o padding da `.estoque-table`, que é **componente compartilhado** com as outras telas de Estoque — descartado: apertar componente do sistema para caber uma tela volta como bug em outro lugar.
- **Dois filtros, nomes desambiguados** (colidiam, os dois se chamariam "situação do saldo"):
  - **Nível do saldo** (quantidade — é o filtro que já existia, renomeado): todos · com saldo · sem saldo · abaixo do mínimo · negativo.
  - **Situação do saldo** (estágio — novo, e fica com o nome do item 19): todos · em conferência · a endereçar · disponível · reservado · bloqueado.
  - As abas de tipo (`todos / simples / kits / matéria-prima`) não colidem e ficam como estão.
- **Vocabulário travado:** `bloqueado` é **só** avaria/quarentena/excedente sem NF. O estágio *a endereçar* **nunca** é chamado de "bloqueado" na tela — senão ninguém distingue "preso na fila" de "avariado". A palavra do projeto para a fila que segura a venda é **travar** ("a fila que trava a venda").
- **Coluna *A endereçar* pinta por tempo**, na mesma lógica da coluna "Parado" de Endereçamento: saldo travado com data é problema, sem data é rotina.
- **Teste de integridade de graça:** a soma da coluna *A endereçar* tem de bater com a fila de Endereçamento.

**Controle de Estoques v2 — o que mudou em 15/set/2026, depois dos prints do Olist:**

- **O drawer de extrato morre; vira página de detalhe** — `pagina-estoque-controle-estoques-detalhe.html`. Não é só cópia do Olist: é o que deixa a tela **consistente com o resto do sistema** (produtos, clientes, fornecedores, ordens de compra e entrada de notas já têm `-detalhe`); o drawer era a exceção.
- **A faixa de KPIs do detalhe é onde mora a quebra completa dos estágios** (físico · a endereçar · bloqueado · reservado · disponível, mais *em conferência* por fora). Isso resolve o aperto de largura da listagem sem mexer nas 9 colunas medidas: a listagem fica rasa, o detalhe carrega a profundidade.
- **Abas no detalhe:** `lançamentos` (o ledger) e `reservas`.
- **Ledger** com as colunas do print (Data e hora · Entrada · Saída · Valor · Observação · Tipo) **mais uma que o Olist não tem: em que estágio o saldo caiu** — porque entrada nossa cai em *a endereçar*, não em disponível.
- **Sai o "disponível multiempresa"** do print: é multi-CNPJ do Olist; produto nosso pertence a uma loja só.
- **Botão "gerenciar produtos"** na toolbar da listagem, apontando para o cadastro de Produtos (confirmado pelo usuário, igual ao Olist).
- **Aba `reservas` nasce com estado vazio e a explicação** — depende de `orders` (F3/F4). Sem histórico de venda inventado, mesmo tratamento da coluna Reservado.
- **A tela vai parecer "errada" perto do print, de propósito:** no Olist um lançamento de entrada de 2 sobe físico e disponível juntos; aqui o físico sobe, *a endereçar* recebe os 2 e o **disponível não se move** até alguém endereçar.

**Achado dos prints:** o campo **Estoque mínimo já existe** em `pagina-cadastros-produtos-detalhe.html` (aba Dados Gerais → seção Estoque, `#inputEstoqueMinimo`), junto com Estoque máximo, Controlar lotes, Localização, Sob encomenda e Dias para preparação. Não precisa ser criado — o card "Alertas de Estoque" do Dashboard é que ainda usa número inventado e passa a ler daí. **Ressalva com a decisão de depósito (item 15):** `Localização` (ex: "Corredor A1", "Prateleira 5") e o saldo são, na verdade, do par **(produto, depósito)** — o CSV de inventário do Olist confirma isso, e a importação por planilha diz "apenas a localização e o saldo em estoque podem ser atualizados", sempre com um depósito de destino escolhido. Hoje esses dois campos estão no produto; quando `depositos` existir, eles migram pra tabela de saldo por depósito, e o campo em Produtos-detalhe vira o valor do depósito principal.

**Histórico:** Vendedores foi concluído em setembro/2026 — cadastro próprio e independente (não mais uma extensão dos registros Trade Marketing de Lojas Desk, que era o plano antigo), com exclusão suave, vínculo opcional a Loja Desk ("autônomo" quando vazio) e painel mocado de criação/alteração de senha de acesso (ver design-system §8.1, §9.1, §11 e §12). Em setembro/2026, antes de abrir qualquer módulo novo, foi feita uma varredura de consistência nos 22 arquivos que zerou as pendências técnicas dos módulos já construídos (ver §7 e o §14 do design-system). Falta só **Transportadora (Desk Flash)** pra fechar F2 por completo — o usuário já sinalizou que essa tela fica por último, porque a Desk Flash como transportadora própria ainda precisa ser desenhada/definida ("ainda temos que desenhar ela e criar o app de como ela vai ser"). As pendências de Categorias, do seletor de tema e do `max-height` dos dropdowns foram todas fechadas em setembro/2026 — ver §14 do design-system. **Não há desvio técnico conhecido em aberto nos módulos já construídos.** A pasta local também foi higienizada em setembro/2026: a subpasta `Claude outputs\` (com cópias defasadas), o instalador antigo `.skill` e um SVG de 95 MB de uma tentativa anterior do sistema foram removidos. Hoje ela tem exatamente **24 arquivos — as 21 páginas de módulo, o molde e os 2 `.md` — somando 1,9 MB**; qualquer coisa fora dessa lista é resíduo e deve ser investigado, não copiado. Só depois de F2 fechado por completo considerar gerar os prompts reais pro Lovable.


---

## 9. Caixa e Bancos — prints de referência (lote 1, recebido em 16/set/2026) ✅ *completado em 22/set/2026 — ver o bloco do lote 2 no fim do arquivo*

**Nada construído. Registro dos prints enquanto o usuário envia o restante.**

### O que as telas mostram

- **Listagem `início › finanças › caixa`.** Ações do topo: `imprimir` · `transferir` · **incluir lançamento** (primário) · `mais ações ⋯`. Busca "Pesquise por cliente", seletor de colunas, e três pills: **período** ("Últimos 30 dias"), **filtros**, **limpar filtros**. Abaixo, uma pill por conta — hoje só **Caixa** — com `saldo atual (R$)` ao lado. Dois estados vazios diferentes: *"Sua pesquisa não retornou resultados"* (com filtro) e *"Você não possui nenhum item cadastrado"* (sem nada).
- **Imprimir** abre uma pré-visualização em tela cheia (`imprimir CTRL+ENTER` / `fechar ESC`) com cabeçalho de razão social + CPF/CNPJ e título "Caixa Últimos 30 dias". Colunas **Data · Histórico · Cliente · Categoria · Entrada · Saída**, e três linhas de fechamento: **Totais**, **Saldo inicial**, **Saldo final**.
- **Transferência entre contas** — painel lateral: Data, Valor, **Conta de origem**, **Conta de destino**, Histórico (já pré-preenchido com "Transferência entre contas"). Os dois dropdowns listam só *Caixa*, porque não há conta bancária cadastrada.
- **Incluir lançamento** — **página própria, não drawer** (tem "voltar" no breadcrumb), com abas **dados do lançamento · competência · anexos · marcadores**. Campos: **Categoria**, **Tipo**, Data, Valor, Histórico, **Cliente ou Fornecedor** (busca + dois botões: *cadastro rápido* e *pesquisar*). salvar/cancelar fixos no rodapé.
  - **Categoria**: agrupada — cabeçalho "Sem grupo" e os itens *Água, luz · Aluguéis e condomínio · Compras · Impostos, taxas · Serviços gerais · Telecomunicação, internet · Veículos, transportes*, separador, e **Adicionar nova categoria** dentro do próprio dropdown.
  - **Tipo**: **Saída · Entrada · Saldo**.
  - **competência**: um único campo `‹ 09/2026 ›`, navegável por mês.
  - **anexos**: "procurar arquivo", limite de **2 MB** (mesmo limite do XML da nota e dos arquivos do inventário).
- **Pesquisar Cadastro** (lupa) — painel com busca por "nome, cód., fantasia, email ou CPF/CNPJ" e seletor de colunas.
- **Cadastro rápido** (lápis) — painel com Nome, Código, Tipo da Pessoa, CNPJ, Inscrição Estadual, CEP (com busca), Cidade, UF, Endereço, Bairro, Número, Complemento, Fone, Email, Celular.
- **mais ações ⋯**: transferir entre contas · imprimir relatório — exportar lançamentos para planilha · importar lançamentos de uma planilha · **importar extrato OFX** — **gerenciar fechamento financeiro** · **movimentações financeiras bloqueadas**.
- **filtros**: Categoria (Todas / grupo / **Sem categoria**).
- **período**: abas **por emissão** e **por competência**; opções *últimos 30 dias · sem filtro · do dia · da semana · do mês · intervalo*.

### O que já dá para decidir a partir daqui *(fechado pelo §12 e pelos prints de 22/set)*

- **Data ≠ competência, e isso é schema, não enfeite.** O filtro de período tem as duas abas e o lançamento tem a aba própria: são **regime de caixa** e **regime de competência**, os dois. Nascem como **dois campos** (`data_movimento` e `competencia`), e todo relatório declara por qual está filtrando. Inventar depois significa reescrever todo relatório financeiro.
- **`Tipo = Saldo` é o "Balanço" do financeiro.** Mesma ideia do acerto de estoque: informa-se o saldo e o sistema deriva a diferença, em vez de pedir a diferença ao usuário. Vale reaproveitar a semântica e o texto.
- **"Incluir lançamento" é página própria** — confirma o padrão já adotado no Acerto, na Nova transferência e no Inventário: documento com abas e anexos não cabe em drawer.
- **Fechamento financeiro é o bloqueio do Inventário, no financeiro.** "gerenciar fechamento financeiro" + "movimentações financeiras bloqueadas" = período fechado não aceita lançamento novo. Mesma família da trava de depósito; precisa existir no schema desde o começo, não depois.
- **O extrato impresso tem saldo inicial e final** — ou seja, a listagem não é lista, é **extrato de um período**. Saldo de abertura precisa ser calculável para qualquer data.

### Perguntas que estavam em aberto — ✅ todas respondidas *(anotado em 29/set/2026)*

1. **Cadastro de Contas Bancárias vem antes do Caixa?** Nos prints só existe "Caixa" porque não há banco cadastrado — exatamente a armadilha de `depositos` vs Controle de Estoques. **Recomendação: sim, vem antes**, senão filtro por conta, transferência entre contas e saldo nascem torto. O item já está no menu Configurações. → ✅ **Resolvido (16 e 21/set):** sim, e com o nome certo — Contas Financeiras → Contas Bancárias → Categorias Financeiras → Caixa (§12.11 e decisões de 21/set, item 3). Construído nessa ordem.
2. **Cliente ou Fornecedor: um cadastro ou dois?** O Olist tem cadastro único de pessoas; nós temos **Clientes** e **Fornecedores** separados e já construídos. O "cadastro rápido" precisa saber em qual tabela grava. → ✅ **Resolvido (21/set, item 2):** dois cadastros, `pessoas` descartada. E sem cadastro rápido no lançamento: o campo busca quem já existe (22/set, *O que ficou de fora*).
3. **Categoria financeira é cadastro novo** (não é a Categoria de Produtos, que já existe). Tem **grupo** de verdade ("Sem grupo" sugere que sim)? Vai virar plano de contas / DRE depois? → ✅ **Resolvido (§12.9):** cadastro novo, com grupo e natureza; construído em 21/set com posição no DRE e competência padrão.
4. **`Tipo = Saldo` ajusta para o valor informado ou lança a diferença?** Muda o texto da tela e o registro no histórico. → ✅ **Resolvido (22/set):** lança a diferença, como entrada ou saída de verdade — ver *`Tipo = Saldo` lança a diferença*.
5. **O caixa é por loja ou único?** São três frentes (Desk Shope, Desk Brands, Desk Tech) e um CNPJ. Se for por loja, isso entra no schema agora. → ✅ **Resolvido (§12.8):** o saldo é por conta financeira; a frente (loja) é dimensão opcional de relatório.
6. **Conciliação bancária existe na F5?** O "importar extrato OFX" aponta para ela; pode ficar para depois, mas o formato do lançamento muda se ele precisar guardar o identificador do OFX. → ✅ **Resolvido (21/set, item 4):** os campos nascem agora (`origem`, `id_externo`, `conciliado_em`); a tela fica para depois da F5.


---

## 10. Contas a Pagar — prints de referência (lote 2, recebido em 16/set/2026) ✅ *construído em 22/set e aprovado por inteiro em 29/set/2026*

**Nada construído.** Companheira do §9 — os dois módulos são o mesmo dinheiro visto de ângulos diferentes.

### O que as telas mostram

- **Listagem `início › finanças › contas a pagar`.** Topo: `imprimir` · **`$ gerenciar pagamentos`** · **incluir conta a pagar** (primário) · `mais ações ⋯`. Busca "Pesquise por fornecedor ou nº doc" + seletor de colunas. Pills: **contas a pagar** (parece seletor de a pagar / a receber), **Últimos 30 dias**, **filtros**, **limpar filtros**. Abas: **todas · em aberto · emitidas · pagas · atrasadas · canceladas**.
- **Imprimir**: "Contas a Pagar — 17/08/2026 a 16/09/2026", colunas **Fornecedor · Histórico · Nº documento · Vencimento · Situação · Saldo**, com linha **Total**. O título carrega o intervalo; o relatório é sempre de um período.
- **Conta a pagar** — **página própria** ("voltar" no breadcrumb), abas **dados da conta · competência · anexos · marcadores**. Campos: **Forma Pagamento**, **Fornecedor** (busca + cadastro rápido + lupa, igual ao §9), **Vencimento** (date picker), **Valor**, **Data de emissão** (já preenchida com hoje), **Nº do documento**, **Histórico**, **Categoria** (o mesmo dropdown agrupado do Caixa) e **Ocorrência**, com o hint "Única ou recorrente".
  - **Forma Pagamento**: apenas **Boleto** e **Pix**.
  - **Ocorrência**: **Única · Semanal · Quinzenal · Mensal · Trimestral · Semestral · Anual · Parcelada**.
- **mais ações**: gerenciar pagamentos · imprimir relatório · **imprimir agrupado por fornecedor** — exportar lançamentos para planilha · importar lançamentos de uma planilha.
- **filtros**: Categoria (Todas / grupo / Sem categoria) · **Forma de pagamento** (Boleto / Pix) · **Situação do pagamento** (Todas / **Processando** / **Agendado**), com aplicar/cancelar.
- **Pagamentos** (tela do "gerenciar pagamentos") — tela própria: busca, pill de período (**do mês · do dia · da semana · do período**, com navegador `‹ 09/2026 ›` e aplicar/cancelar) e tabela com **seleção em massa** e colunas ordenáveis **Data · Histórico · Categoria · Valor**. Mais ações: imprimir relatório · exportar pagamentos para planilha.

### O que já dá para decidir a partir daqui *(fechado pelo §12 e pelos prints de 22/set)*

- **"Ocorrência" é a decisão que mata o módulo se ficar para depois.** Conta *Mensal* ou *Parcelada* não é um registro — são N. Ou o sistema **materializa as N parcelas na hora** (com `conta_pai_id` e `parcela X de Y`), ou guarda uma regra e gera na virada do mês. **Recomendação: materializar**, porque sem as parcelas gravadas não existe fluxo de caixa futuro — e fluxo de caixa futuro é metade do motivo de ter contas a pagar. Isso obriga a responder, no mesmo momento: editar a recorrência mexe nas parcelas futuras? Cancelar cancela quantas?
- **São quatro datas, não uma.** `data_emissao`, `vencimento`, **competência** (aba própria) e a data do pagamento, que só nasce quando a conta é paga. Todo relatório declara por qual filtra — mesma regra do §9.
- **"Atrasadas" é derivada, não é estado gravado** (`vencimento < hoje` E não paga). Gravar como situação é garantia de lista mentindo no dia seguinte. As abas viram contadores (§7.2 do design-system), como nas outras telas.
- **Há duas máquinas de estado, não uma.** A **conta** (em aberto / paga / cancelada) e o **pagamento** (agendado / processando / efetivado). "Emitidas" é a terceira peça: boleto emitido / remessa gerada. As duas últimas só existem de verdade com integração bancária.
- **"Gerenciar pagamentos" é o lote.** Seleção em massa para pagar várias contas de uma vez — mesma família do lote atômico do Acerto de Estoque: valida tudo antes, grava tudo junto.
- **Forma de pagamento só Boleto/Pix é limitação do Olist, não requisito nosso.** Dinheiro, transferência, cartão e débito automático existem na vida real da Desk e precisam entrar.

### Perguntas que estavam em aberto — ✅ todas respondidas *(anotado em 29/set/2026)*

1. **Pagar uma conta escreve no Caixa automaticamente?** **Recomendação: sim** — o pagamento é um lançamento de saída na conta escolhida (§9). Se não escrever, o saldo do Caixa mente e os dois módulos divergem em uma semana. Isso é o que amarra §9 e §10 num ledger só. → ✅ **Resolvido (§12.7):** sim — e é real no protótipo desde 22/set.
2. **Conta a pagar nasce da Nota de Entrada?** Já temos **Ordens de Compra** ✅ e **Entrada de Notas** ✅, e a NF-e traz **duplicatas** (parcelas). Digitar a conta de novo à mão é retrabalho e fonte de divergência. Precisa decidir se a nota gera as contas e se dá para editar depois. → ✅ **Resolvido (§12.5):** documento gera título; título nascido de documento tem valor e vencimento travados, com link para a origem.
3. **Recorrente/parcelada: materializa N linhas ou guarda regra?** (recomendação acima: materializa, com vínculo à conta-mãe). → ✅ **Resolvido (§12.6 e barganha de 23/set):** materializa; parcelada divide, recorrência repete.
4. **"Emitidas", "Processando" e "Agendado" dependem de integração bancária que não existe.** Nascem **visíveis e desabilitadas** com o motivo no `title` (padrão §11 do design-system, igual a Reservado no estoque) ou ficam fora da tela por enquanto? → ✅ **Resolvido (§12.10):** ficam fora da tela.
5. **Contas a Receber é o mesmo módulo com um seletor** (a pill "contas a pagar" sugere isso) **ou tela separada?** → ✅ **Resolvido (§12.3):** uma tabela (`titulos.natureza`), duas telas.
6. **Multi-loja de novo:** a conta é da empresa ou da frente (Desk Shope / Brands / Tech)? Mesma pergunta do §9, e as duas têm que ter a mesma resposta. → ✅ **Resolvido (§12.8):** o título é da empresa; a loja é dimensão.


---

## 11. Contas a Receber — prints de referência (lote 3, recebido em 16/set/2026)

**Nada construído.** Fecha o trio do módulo Finanças com o §9 (Caixa) e o §10 (Contas a Pagar). É o lote mais rico — os únicos prints com **dado real na tela**, e é isso que revela o que os outros dois esconderam.

### O que as telas mostram

- **Listagem `início › finanças › contas a receber`.** Topo: `imprimir` · **`$ gerenciar recebimentos`** · **incluir conta a receber** · `mais ações ⋯`. Busca por "cliente, nº no banco ou nº doc". Pills: **por meio de recebimento**, **Últimos 30 dias**, **filtros**, **limpar filtros**. Abas **com contador** (em aberto 01 · emitidas 01 · recebidas · atrasadas 01 · canceladas) — exatamente o §7.2 do design-system.
- **Colunas:** Cliente · Histórico · Vencimento · **Valor** · **Saldo** · **Valor líquido** · **Recebido** · **Valor antecipado** · Data Emissão · **Documento Origem** · Marcadores · **Meio** · **Integrações**. Rodapé com **quantidade** e **valor total (R$)**. Seleção em massa na primeira coluna e menu `⋯` por linha.
- **A linha real:** cliente *Consumidor Final*, histórico **"Ref. ao pedido de venda nº 1, Consumidor Final"**, **Documento Origem = `Pedido 1` (link clicável)**. A conta **nasceu do pedido de venda** — não foi digitada.
- **Imprimir**: "Contas a Receber — 17/08/2026 a 16/09/2026", colunas Cliente · Histórico · **Antecipada** · **Nro. no banco** · Nº documento · Vencimento · Emissão · Recebimento · Situação · Valor · Saldo · Recebido, com linha **Total**.
- **Conta a receber — cadastro**: página própria, abas **dados da conta · competência · anexos · marcadores**. Cliente (busca + cadastro rápido + lupa), Vencimento (date picker), Valor, Data emissão, Nº documento, Histórico, Categoria (o mesmo dropdown agrupado), **Forma de recebimento** e **Ocorrência** (a mesma lista do §10: Única → Parcelada).
- **Conta a receber — detalhe (leitura)**: badge de situação **● atrasada** ao lado do título, campos em modo leitura, link **"dados do cliente"**. Ações no topo: **`✓ receber (baixar conta)`** · **editar** · `mais ações`.
  - **mais ações do detalhe**: receber (baixar conta) · **clonar conta** · **imprimir recibo** · **imprimir duplicata** · editar marcadores · **cancelar conta** · **excluir conta**.
- **Erro de validação**: caixa vermelha no topo — *"Não foi possível salvar a conta a receber / Verifique os campos destacados. / Preencha um valor válido."* — com o campo problemático contornado de vermelho.
- **Filtros**: Categoria (igual §9/§10) e **Forma de recebimento** com a lista **completa**: Dinheiro · Cartão de crédito · Cartão de débito · Boleto · Cheque · Depósito · Crediário · **Vale-troca** · Pix · **Não informada**.
- **Período**: abas **por vencimento** / **por competência** (no Caixa era *por emissão*), com últimos 30 dias · sem filtro · do dia · da semana · do mês · intervalo.
- **mais ações da listagem**: gerenciar recebimentos · imprimir · **imprimir agrupado por cliente** · **conciliar boletos com o banco** · **conciliar contas com o gateway** · exportar/importar planilha.

### O achado grande: **Valor ≠ Valor líquido ≠ Recebido**

São três números diferentes na mesma linha, mais **Valor antecipado** e **Saldo**. Isso não é enfeite de tela, é a realidade de quem vende em marketplace: o pedido vale X, o marketplace desconta comissão, o gateway desconta taxa, e **o que cai na conta é outro número** — em outra data, se houver antecipação. A Desk vende em marketplace; se a conta a receber nascer com **um** campo de valor, o dinheiro nunca vai bater com o extrato, e o problema só aparece quando já houver centenas de contas.

Por isso as duas opções de **conciliação** (`conciliar boletos com o banco`, `conciliar contas com o gateway`) e a coluna **Integrações** existem: a conta a receber é a única das três telas que precisa reconciliar o que foi prometido com o que entrou.

### Outras leituras

- **A conta nasce do documento, não da digitação.** "Documento Origem = Pedido 1" do lado de receber é o espelho da duplicata da NF-e do lado de pagar (§10, pergunta 2). A mesma decisão resolve os dois: **documento gera conta**, e o cadastro manual é a exceção.
- **Cancelar ≠ excluir**, e as duas coexistem no menu — é a **exclusão suave** que já adotamos em Vendedores (design-system §8.1). Chega pronta.
- **"Atrasada" aparece como badge de situação na tela de detalhe**, mas continua sendo **derivada** (vencimento < hoje e não recebida). Mostrar como badge é certo; gravar como estado não.
- **Forma de recebimento no cadastro tem só Dinheiro/Cheque, mas o filtro tem dez opções.** É inconsistência do Olist — a lista do filtro é a boa: conta vinda de pedido traz o meio real, conta digitada à mão só oferece o que dá para digitar. **Vale-troca** e **Crediário** merecem atenção: são meios que a Desk pode usar e que não são dinheiro entrando de fato.
- **O período filtra por *vencimento* aqui e por *emissão* no Caixa.** Faz sentido e deve ser respeitado: cada tela tem a data que interessa a ela, e a competência é sempre a segunda opção.
- **Abas com contador de dois dígitos (01)** — mesma convenção que já usamos.

### Perguntas que estavam em aberto — ✅ todas respondidas *(anotado em 29/set/2026)*

1. **Quantos campos de valor a conta a receber tem?** (proposta: `valor_bruto`, `taxas`, `valor_liquido`, `valor_recebido`, `valor_antecipado`, e `saldo` derivado). É a decisão mais cara de mudar depois. → ✅ **Resolvido (§12.4).**
2. **Conciliação com gateway/marketplace entra na F5 ou fica para quando houver integração?** Sem ela, `valor_liquido` é digitado à mão — o que pelo menos deixa o campo existir. → ✅ **Resolvido (§12.4 e 21/set, item 4):** depois, com a integração.
3. **Pedido de venda gera conta a receber automaticamente?** Hoje **`orders` não existe** (F3/F4). Ou seja: **contas a receber nasce sem sua principal fonte**, e por enquanto só aceita lançamento manual. Precisa decidir se vale construir agora ou depois de Pedidos. → ✅ **Resolvido (§12.5 e §12.11):** sim — e é por isso que Contas a Receber espera Pedidos de Venda.
4. **Recibo e duplicata são documentos impressos** — entram junto ou ficam para Relatórios? → ✅ **Resolvido (29/set):** o recibo foi construído em Conta a pagar → Mais ações → *Imprimir recibo*, por `@media print`; a duplicata nasce com Contas a Receber, no mesmo padrão.
5. Mesmas três perguntas herdadas dos §9 e §10: **baixa escreve no Caixa?** (sim), **conta é da empresa ou da frente?**, **recorrência materializa parcelas?** (sim). → ✅ **Resolvido:** §12.7, §12.8 e §12.6.


---

## 12. Módulo Finanças — decisões fechadas na barganha de 16/set/2026

Fechadas **antes de construir qualquer tela**, a pedido do usuário. Valem para os §9, §10 e §11.

### 1. Duas tabelas, não três: **compromisso** e **extrato**

São duas coisas com vidas diferentes:

- **Título** — a obrigação (pagar) ou o direito (receber). Existe **antes** de o dinheiro se mover: tem vencimento, vence, atrasa, pode ser cancelado.
- **Movimento financeiro** — o dinheiro efetivamente entrando ou saindo de uma conta, com data e saldo. É o ledger do Caixa (§9).

Baixar um título **cria** um movimento. Mas um movimento existe sem título (tarifa bancária, sangria, aporte) e um título recebe vários movimentos (baixa parcial).

**Por que não uma tabela só:** comprar 3.000 em 30/60/90 criaria três linhas no Caixa no dia da compra, e o saldo cairia 3.000 antes de qualquer pagamento sair. O saldo do banco passaria a mentir — o mesmo erro de tratar saldo de estoque como campo solto em vez de derivar do ledger.

**Por que não três tabelas soltas:** o pagamento seria escrito duas vezes, como "conta paga" e como "saída de caixa", sem ligação. Na primeira correção de um lado só, os dois números divergem e ninguém sabe qual vale.

### 2. A ligação é uma tabela própria (`baixas`)

Não basta um `titulo_id` no movimento, porque os dois casos reais são N:N:

- **Lote de pagamento** (a tela "gerenciar pagamentos" dos prints): um PIX de 4.500 quita seis boletos. Um movimento, seis títulos.
- **Baixa parcial:** cliente devia 1.000, pagou 600 hoje e 400 depois. Um título, dois movimentos.

`baixas` = *tal movimento quitou tal valor de tal título, em tal data*. É o mesmo princípio do recebimento parcial da Transferência: o que falta continua visível em vez de sumir.

### 3. Uma tabela de títulos, duas telas

`titulos` com campo `natureza` (pagar / receber). O dado tem a mesma forma; as telas divergem o bastante (receber tem líquido, antecipado e conciliação; pagar tem agrupado por fornecedor) para que uma tela só piorasse as duas.

### 4. Campos de valor — nascem agora, mesmo sem marketplace

`valor_bruto` · `valor_taxas` · `valor_liquido` (**gravado**, não calculado — a taxa vem do extrato e diverge da conta) · `valor_baixado` (derivado das baixas) · `saldo` (derivado) · `antecipado` (flag + data).

**Confirmado pelo usuário em 16/set/2026:** *"a venda em marketplace será bem no futuro, nada pra agora, mas queria já ir padronizando pra deixar tudo ok."* Os campos existem desde já; o cadastro manual mostra **só Valor**, e taxas/líquido só aparecem em título vindo de pedido ou integração — mesma regra do seletor de origem que só aparece quando há mais de um estágio. **As telas de conciliação (boleto/banco, gateway) ficam para quando houver integração.**

### 5. Documento gera título — **já estava decidido e escrito na tela**

`pagina-estoque-entrada-notas-detalhe.html` já tem o campo **Condição de pagamento** ("30 60 90, ou 3x") com o hint *"As parcelas nascem em Contas a Pagar quando a nota for lançada"*, e o aviso *"As parcelas nascem em Contas a Pagar pelo VALOR DA NOTA. Se a conferência achar divergência, a diferença vira pendência com o fornecedor — a nota não é editada."* A Ordem de Compra já tem "Gerar parcelas" com tabela Nº · Vencimento · Valor.

Do lado de receber, o print confirma o espelho: **Documento Origem = `Pedido 1`**, clicável, com histórico automático.

**Consequência que não se pode furar:** título nascido de documento tem **valor e vencimento travados**, com link para a origem. Mudança se faz no documento. Título digitado à mão é livre.

### 6. Recorrência: **materializa** (opção A), e Parcelada é caso à parte

- **Parcelada** — valor dividido, com fim. Pede um campo extra (**em quantas vezes?**) que as outras opções não pedem: a tela reage à escolha. Gera N títulos com `titulo_pai_id` e `parcela X de Y`.
- **Recorrente** (Semanal → Anual) — mesmo valor repetido, sem fim. Materializa uma **janela de 12 meses** e vai regenerando.

**Por que materializar:** título que existe de verdade pode ser editado só naquele mês (aluguel subiu), cancelado só naquele mês, receber anexo próprio, e o fluxo de caixa futuro é leitura direta da tabela. Guardar só a regra transforma cada um desses casos em exceção.

**Preço aceito:** alguém gera a próxima janela, e alterar valor obriga a perguntar *"muda só esta ou as futuras?"* — a pergunta do Google Calendar. Ela existe nos dois caminhos; guardando só a regra ela chega mais tarde e pior.

### 7. Baixa escreve no Caixa, sempre

Baixar pede a **conta bancária** e cria o movimento. Sem isso o saldo do Caixa mente. É o que obriga **Contas Bancárias** a existir antes.

### 8. Título é da empresa; a frente é dimensão

1 CNPJ, 3 frentes. O título pertence à empresa; `loja_id` é **opcional e serve a relatório**, nunca a separação de saldo — saldo é sempre por conta bancária. Se um dia virarem CNPJs separados, a dimensão vira separação e o campo já existe (mesma jogada do `empresa_id` do item 22).

### 9. `categorias_financeiras` é cadastro novo, com `natureza`

Não é a Categoria de Produtos (que já existe e tem tipo Produtos/Fornecedores). Campos: nome, **grupo**, **natureza** (receita / despesa / ambas). **Falha do Olist corrigida:** no print de Contas a *Receber* o dropdown oferece "Água, luz", "Aluguéis", "Compras", "Impostos" — todas despesas. A natureza filtra pelo lado do título.

### 10. O que fica de fora por enquanto

**"Emitidas", "Processando", "Agendado"** saem da tela. Diferente de *Reservado* no estoque, que nasceu **visível e desabilitado** porque é um número que existe conceitualmente e será calculado: nenhum evento do nosso sistema produz esses estados hoje, e aba vazia para sempre é pior que aba ausente. **É julgamento, não regra** — reversível se o usuário preferir mostrá-las desabilitadas para comunicar o roadmap.

### 11. Ordem de construção

**Contas Bancárias → Categorias Financeiras → Caixa → Contas a Pagar → Contas a Receber.**

Os dois cadastros são pequenos e destravam o resto. Caixa antes dos títulos porque a baixa escreve nele. **Contas a Receber por último** porque a fonte principal dela — `orders` — só existe em F3/F4, e ela vai nascer aceitando apenas lançamento manual.

> **Revisto em 16/set/2026, logo depois desta barganha:** o usuário sinalizou que **Contas Bancárias pertence ao módulo de Configurações**, que vai ser reorganizado numa área própria com muitas abas. A ordem acima continua válida na dependência, mas o ponto de partida passa a depender do desenho de Configurações — ver §13.

---

## 13. Configurações — reorganização anunciada (16/set/2026) ✅ *virou o hub — estrutura aprovada em 18/set/2026, ver §14*

O usuário avisou que Configurações deixa de ser um flyout com quatro itens e vira **uma área própria com muitas abas**. Isso mexe em estrutura, não em uma tela.

**O que Configurações tem hoje** (design-system §4, congelado no molde e replicado nos 38 arquivos): Cadastro de Usuários · Permissões de Usuários · **Cadastro de Contas Bancárias** · Relatórios de Configurações, mais o seletor de tema fixo no rodapé do painel.

**Por que isto não é uma tela a mais:**

1. **A sidebar vive em todos os arquivos.** Mudar a estrutura de Configurações significa reescrever o bloco de menu em **todas as páginas** — a mesma armadilha que já mordeu duas vezes (Conferência de Compra sem entrada no menu; o molde congelado antes do módulo Estoque existir). Entra no Passo 0 obrigatoriamente.
2. **Um módulo de 9 itens virando área com abas é padrão novo de navegação.** Hoje todo módulo abre flyout e cada item é uma página. Uma área com abas internas não tem precedente no sistema e precisa de decisão de padrão, não de improviso por tela.
3. **Contas Bancárias muda de dono.** Ela é pré-requisito do Caixa (§12 item 7) e passa a morar em Configurações — o que reordena o início do módulo Finanças.

**Já reservado para Configurações — lista viva a consolidar quando os prints chegarem:**

- **Parâmetros de Estoque** (decidido em 15/set/2026): Conferência de Compra > 1 dia alerta / > 3 crítico · Endereçamento parado > 2 / > 7 · Estoque zero > 7 dias. *Não entram:* prazos de Manifestação do Destinatário (10 e 180 dias) — são legais, não configuráveis. Estoque mínimo continua por produto, no cadastro.
- **Registro de confirmações por senha** — a lista de ações que exigem usuário + senha, espelhada no checklist do perfil (hoje em `pagina-cadastros-vendedores-detalhe.html`, item a item).
- **Cadastro de Contas Bancárias** e, possivelmente, **Categorias Financeiras**.
- **Permissões de Usuários** — hoje mocada em toda tela que pede senha.

### Prints — lote 1 de Configurações (20 telas, recebido em 16/set/2026) 📁 *referência — o mapeamento das abas fechou em 17/set*

**Correção do que eu disse antes de ver os prints:** eu registrei que "um módulo virando área com abas é padrão novo de navegação, sem precedente". **Não é.** O que os prints mostram é um **hub**: uma página índice com abas que apenas **filtram uma lista de links**, e cada link abre uma **página própria** com breadcrumb `início › configurações › <tela>` e botão "voltar" — exatamente o padrão que o sistema já usa. O impacto estrutural é bem menor do que eu supus.

**Como se chega lá.** O flyout de Configurações **deixa de listar páginas**: passa a ter um único atalho **"Configurações ERP"** mais o bloco **Preferências → Tema (auto/claro/escuro)**. Isso *simplifica* a sidebar em vez de complicá-la, e o nosso seletor de tema já mora exatamente nesse lugar.

**A página índice — "Configurações do Sistema ERP":** breadcrumb `início › configurações` (sem voltar), busca **"Busque pela funcionalidade ou dúvida"**, e abas **geral · cadastros · suprimentos · vendas · notas fiscais · finanças · e-commerce · tributação (RTC)** `Novo`. **As abas são os módulos do menu**, não categorias inventadas — no nosso caso viram *geral · cadastros · estoque · vendas · logística · finanças · operacional · integrações*, e é aí que os **Parâmetros de Estoque** ganham lugar natural.

A aba *geral* é uma lista de links separados por divisória: Alterar dados da empresa · Alterar dados do usuário · Cadastro de usuários do sistema · Configurações do servidor de e-mail · Configurações do envio de documentos · Configurações das etiquetas · Configurações da agenda · Encerrar assinatura. Depois de um separador vem o cabeçalho **"Outras configurações"** (texto, não link) com: Interface do usuário · Central de notificações · Impressão PrintNode · Multiempresa · Aplicativos · Token API · Configurações de API.

**As telas do lote:**

- **Dados da empresa** — a mais longa. Razão social, Fantasia (*"será exibido no topo das telas do sistema"*), endereço completo, contatos, Segmento de atuação, Tipo da Pessoa, CNPJ, **Inscrição Estadual + checkbox IE Isento**, Inscrição Municipal, **Inscrição Suframa** ⓘ, CNAE, **Código de regime tributário** ⓘ (Simples nacional), link *Alterar senha*, bloco repetível **Inscrições Estaduais dos Substitutos Tributários** (Estado + IE + lixeira + "adicionar outra inscrição"), **Logo da empresa** (upload, 2 MB), **Preferências de Contato** (como deseja ser chamado + canal), **Pessoa administradora**. Topo informa que o ERP consulta a Receita Federal pelo CNPJ. A barra **salvar/cancelar é fixa (sticky) no meio da tela**, não no fim.
- **Dados do usuário** — avatar de iniciais, Nome e E-mail **desabilitados**, "escolher foto", **Verificação em duas etapas** (Google Authenticator), "alterar senha de acesso", e **Código para liberação de desconto em vendas** — *"código utilizado pelo gerente para liberar descontos em vendas acima do permitido"*.
- **Usuários do sistema** — **grid de cards, não tabela** (primeira do sistema). Topo: `perfil de usuários` · **+ incluir usuário** · mais ações. Painel de contadores **Usuários cadastrados 1 · Vendedores 3** (com link externo). Cada card: avatar com inicial, nome, e-mail, badge **ADMIN/VENDEDOR** e link *gerenciar* — nos vendedores o *gerenciar* tem ícone de **link externo**, levando ao cadastro de Vendedores.
- **Servidor de e-mail** — Tipo de envio, bloco *Teste de envio* recolhível ("ocultar"), e-mail do destinatário, **testar configurações**.
- **Envio de documentos** — um único toggle: *Compartilhar documento via Whatsapp*.
- **Etiquetas** — listagem (Descrição · Tipo de etiqueta) com ícone por linha; topo "alterar logo para ZPL" e **incluir etiqueta**. O incluir abre painel com **seleção de tipo**: Clientes e fornecedores · Produtos · Volumes · Transportadora · Separação.
- **Editor de etiqueta** — Descrição, **Modo de impressão** (Página/Bobina), **Orientação** (Retrato/Paisagem), **Dimensões** (dropdown enorme com modelos **Pimaco Carta e A4** + Personalizados). Rodapé: salvar · **imprimir página de testes** · cancelar. O drawer **Modelo de dimensões** pede Largura/Altura/Espaçamento e Margens/Colunas, **com diagramas ilustrativos** ao lado.
- **Conteúdo da etiqueta** — **editor visual em grade** com blocos de texto e **placeholders**: `[produto]`, `SKU [codigo]`, `[numero]`, código de barras, `[destinatario_cliente]`, `[destinatario_endereco]`, `[destinatario_bairro]`, `[destinatario_cidade] - [destinatario_uf]`, `[destinatario_cep]`, `[transportadora]`, `[volume]`. Botão **+ inserir ▾**: descrição do produto · código (sku) · volume · outros dados · código de barras · logo da empresa.
- **Agenda** — três toggles: Exibir Contas a Pagar · Ordens de Serviço · clientes de aniversário. Conversa direto com a nossa `pagina-inicio-agenda.html`, já construída.
- **Interface do usuário** — **rádios**: *Ao salvar* (visualizar cadastro / voltar para a listagem) · *Ao acessar um cadastro* (modo de edição / modo de visualização) · *Número de registros por página* (20 / 50); mais o toggle *Lembrar última tela ao logar novamente*.

**Achados que mexem em coisa já construída:**

1. **"Número de registros por página" (20/50) conflita com o nosso dropdown de paginação 10/25/50/100**, que está em toda listagem do design-system §7. Precisa de regra: o global é o **padrão de abertura** e o dropdown da tela **sobrepõe** enquanto durar a sessão — ou o global manda e o dropdown some. ~~A decidir.~~ → ✅ **Resolvido (18/set, opção B):** o global é o padrão de abertura e o dropdown sobrepõe na sessão — ver §14.
2. **"Ao acessar um cadastro: modo de edição ou de visualização"** explica o print de Contas a Receber que abre em leitura com botão *editar*: **é configurável**. Isso vira parâmetro global, não decisão por tela.
3. **Vendedor × Usuário fica resolvido pelo print:** os dois aparecem na mesma lista, mas o vendedor é **gerenciado no cadastro dele**, por link externo. É exatamente o que já fizemos — `pagina-cadastros-vendedores-detalhe.html` já tem a aba *Acesso e Permissões* com o checklist de confirmações.
4. **"Código para liberação de desconto" é um segundo mecanismo de autorização**, diferente de senha: senha confirma *quem é você*, o código libera *uma exceção pontual*. Entra no registro de confirmações como categoria própria.
5. **Duas telas fogem do padrão e merecem tratamento à parte:** *Usuários do sistema* (grid de cards, primeiro do sistema) e o **construtor de etiqueta** (editor WYSIWYG com grade, placeholders e inserção de campos) — de longe a tela mais complexa deste lote e possivelmente de toda a fase.

**Fecho da aba *geral* (lote 2, 16/set/2026) — as telas restantes:**

- **Central de notificações** — tabela **Tipo de notificação × duas colunas de toggle**: *Notificação no Sistema ERP* e *Notificação no navegador*. Topo: `gerenciar dispositivos` · **ativar notificações** (botão primário que vira secundário depois de ativado). Ativar abre um **bottom-sheet** "Adicionar dispositivo" → "Identificar dispositivo" com o **Nome do dispositivo já preenchido** ("Windows - Opera"). O `gerenciar dispositivos` abre painel **Dispositivos configurados** (Dispositivo · Data de registro · lixeira) com botão **outline vermelho** "remover este dispositivo". Hoje existe **um único tipo** de notificação — a tabela nasce preparada para crescer.
- **Impressão PrintNode** — página de texto explicativo com links externos, campo **API Key** (com botão de limpar) e **testar integração**. Banner "Novidade" dismissível no topo. Menciona que as etiquetas saem em **ZPL** e exigem impressora **ZEBRA**. *Inconsistência do Olist:* o índice chama "Impressão PrintNode" e o breadcrumb diz "impressão automática".
- **Aplicativos API** — estado vazio ilustrado com card e "novo aplicativo". O cadastro tem Nome, **URL de Redirecionamento**, **Chaves de acesso** (geradas só depois de salvar) e a **matriz de permissões**.
- **Configurações de API** — seção *Estoque API* com dois toggles, cada um com **descrição explicativa abaixo**: *forçar criação de novo registro de balanço quando preço e quantidade são iguais aos da última atualização* e *sincronizar estoque de anúncios ao gerar balanço via API*. Note que **"balanço de estoque" é o nome do Olist para o nosso Inventário**.

### A matriz de permissões — o achado mais reaproveitável do lote

O cadastro de Aplicativo traz **Acesso ao módulo × Leitura / Incluir e editar / Excluir**, com um toggle *Marcar todos*. Os módulos listados: Contatos · Produtos · Notas Fiscais · Expedição · Pedidos · Separação · Marcas · Estoque · Lista de Preços · Forma de Envio · Forma de Pagamento · Intermediadores · Categorias · Informações da Conta · Gatilhos · Contas Receber · Contas a Pagar · Ordem de Serviço · Ordem de Compra · Serviços · Forma de Recebimento · CRM · Usuários · Depósitos · Orçamentos · Anúncios · Caixa.

**A matriz é esparsa, e a esparsidade é a informação:** *Forma de Envio* só tem Leitura; *Estoque* tem Leitura e Incluir/editar mas **não** Excluir; *Categorias* tem as três. Cada módulo declara o que admite — não é um grid cheio com caixas desabilitadas.

**Isto resolve a estrutura de Permissões de Usuários**, que estava em aberto desde setembro. E deixa claro que o sistema tem **três camadas de autorização, que não se confundem**:

| Camada | Pergunta que responde | Onde já apareceu |
|---|---|---|
| **Módulo × ação** (ler / incluir e editar / excluir) | *o que este perfil alcança* | matriz do Aplicativo API |
| **Confirmação por senha** | *é você mesmo fazendo isto* | nosso checklist em Vendedores → Acesso e Permissões |
| **Código de liberação** | *um gerente autoriza esta exceção pontual* | "Código para liberação de desconto em vendas", em Dados do usuário |

A matriz é do **aplicativo**, não do usuário — mas a estrutura serve aos dois, e as três camadas somadas são o modelo de permissão do sistema. **Registrar isso agora evita desenhar Permissões de Usuários do zero depois.**

**Dois padrões de tela que valem adotar:** o **toggle com descrição explicativa abaixo** (Configurações de API) é o formato certo para os Parâmetros de Estoque; e a **tabela de toggles por canal** (Central de notificações) é o formato certo para qualquer preferência que se repita por tipo.

**Aba *geral* completa.**

### Prints — aba *cadastros* (lote 1: 20 telas, 16/set/2026) 📁 *referência — o resto dos prints desta aba é pedido quando a tela for construída*

**Mudança de breadcrumb:** nas telas desta aba o caminho vira `início › cadastros › configurações › cadastro de clientes` — **o módulo entra no breadcrumb antes de "configurações"**, diferente da aba *geral* (`início › configurações › dados da empresa`). A aba contextualiza.

- **Configurações do cadastro de clientes** — toggles: *Restringir acesso dos vendedores aos contatos vinculados a ele* · *Vincular automaticamente ao vendedor ao criar contato* · *Permitir CPF/CNPJ duplicado* · *Mostrar observações do contato*. Bloco **Permitir o cadastro automático de clientes** (a partir de Pedido/Proposta e de Nota Fiscal/Serviço), com texto explicativo na coluna da direita. **Código do contato**: rádio *Manual / Sequencial*. **Tipo de pessoa padrão** (Física · Jurídica · Estrangeiro). **Tipo de contato padrão**, agrupado sob "Aplicar marcador": *Cliente · Fornecedor · Transportador · Outro*. **Limite de crédito padrão para novos cadastros**.
- **Configurações do cadastro de produtos** — **casas decimais na quantidade** (0–4) e **no preço** (0–10) · *Somar peso dos produtos* (Sim / Somente peso líquido / Não) · Código (SKU) do produto · **Considerar para o cálculo do custo de kits e produtos fabricados: Custo da compra / Custo médio** · *Cadastrar automaticamente produtos a partir de compras, vendas e ordens de serviço* · *Exibir estoque do produto na lista de preços* · Unidade de medida padrão · **NCM padrão** · **Origem padrão** (tabela oficial de origem do ICMS, códigos 0 a 8).
- **Variações dos produtos** — cadastro **global** de variações: listagem com busca, drawer *Variação de Produto* (Nome + Valor, "separados por vírgula ou tab", valores viram **chips**) e drawer *Ajustar variações* (Variação Origem → Variação Destino + "mover selecionados"), que é a ferramenta de consolidar duas variações duplicadas.
- **Atributos dos produtos** — Nome + **Campo equivalente no produto** (Nenhum · GTIN · Código (SKU) · Marca · Unidade · Fornecedor · Peso Bruto · Peso Líquido · Altura/Largura/Comprimento Embalagem). É mapeamento de atributo livre para campo nativo — serve a integração e marketplace.
- **Marcas de Produtos** — listagem + **bottom-sheet** "Incluir marca" com um único campo Nome e *confirmar / cancelar ESC*.
- **Tabelas de Medidas** — wizard (botão *continuar*): Nome, Marca (opcional), Gênero, Tipo de tabela; depois **Medidas do Corpo** (altura, comprimento da perna e do pé, cintura, peito, pescoço, quadril, largura do pé, peso), **Medidas da Peça** (manga, comprimento, cintura, quadril, largura da coxa, comprimento interno, foto frontal) e **Correspondências de tamanho** (BR · EUA · EUR · UK · Referência). Direto ao ponto para a **Desk Brands**, que vende vestuário.

### Quatro conflitos com tela já construída — verificados no código, não supostos

1. **Cliente e Fornecedor: o Olist tem UM cadastro com marcador; nós temos DOIS.** O campo "Tipo de contato padrão → Aplicar marcador: Cliente · Fornecedor · Transportador · Outro" confirma o modelo deles. Nós já construímos `pagina-cadastros-clientes.html` e `pagina-cadastros-fornecedores.html` **separados**, e "Transportador" no nosso sistema é só o item de menu *Transportadoras* (Operacional), não um marcador de contato. **É a pergunta 2 do §10, que continuava aberta — agora com o modelo de referência à vista, mas divergente do nosso.** Decidir: manter dois cadastros e mapear marcador só onde precisar, ou unificar. → ✅ **Resolvido (21/set, item 2):** seguem separados.
2. **Casas decimais são parâmetro; hoje estão cravadas.** As telas de estoque formatam quantidade com `maximumFractionDigits: 2` no código, e o design-system §6 tem regra própria de formatação de quantidade. Passa a ser configuração (0–4 na quantidade, 0–10 no preço) e todas as telas passam a lê-la.
3. **Variações: biblioteca global lá, grade inline aqui.** Nosso `pagina-cadastros-produtos-detalhe.html` monta variações **dentro do produto** — grupos com chips e "gerar grade" —, mecanismo idêntico ao do drawer do print, mas **local**. O Olist mantém um cadastro global reutilizável, mais o *Ajustar variações* para consolidar duplicatas. Decidir se a nossa grade passa a consumir uma biblioteca. → ✅ **Resolvido (29/set/2026, decisão do usuário):** a grade continua **dentro do produto**. O cadastro global de variações só entra quando houver **saldo por variação** ou **integração com marketplace** — acrescentar depois é aditivo, não quebra nada.
4. **Marcas aparece em dois lugares.** Nós temos `pagina-cadastros-marcas.html` no menu **Cadastros**; o print mostra a mesma lista dentro de **Configurações → cadastros**. Decidir: um caminho só, ou dois caminhos para a mesma tela (e, nesse caso, registrar que é a mesma, para não virarem duas telas divergentes). → ✅ **Resolvido (18/set):** um caminho só — Marcas fica no menu Cadastros, pela régua da frequência de uso (§14, *Atalhos para cadastros saíram do hub*).

**Mais dois achados sem conflito:** *"Restringir acesso dos vendedores aos contatos vinculados a ele"* é **permissão por registro** (row-level), que não cabe na matriz módulo × ação — é um refinamento dela, e vale registrar junto das três camadas. E *"Considerar para o cálculo do custo de kits e produtos fabricados"* define como custear o tipo `kit`, que já existe no nosso cadastro de Produtos.

**Lote 2 — fecha a aba *cadastros*:**

- **Tags para produtos** — tags vivem **dentro de grupos**: a listagem mostra os grupos (ex.: *Grupo*, *Marca*, *Smartwatch*) e o drawer *Grupo de tags* tem Nome + lista de tags com `⊕ incluir tag` e lixeira por linha. Grupo é o eixo; tag é o valor.
- **Tipos de contato** — listagem *Cliente · Fornecedor · Transportador · Outro*, e o drawer tem **Descrição** (livre, o usuário cria os que quiser) + **Perfil do contato**, este sim uma lista fixa do sistema: **Cliente · Fornecedor · Vendedor · Transportador · Funcionário · Outro**.
- **Linhas de produtos** — Descrição + **Comissionamento**: *Comissão com alíquota fixa* (um campo de alíquota) ou *Comissão com alíquota conforme descontos*, que abre a tabela **Desconto de até (%) × % Comissão** com lixeira e "adicionar outro desconto".
- **Listas de preços** — topo `preferências` · `importar planilha` · **incluir lista de preço**. Cadastro: Descrição + **Acréscimo / desconto (%)** (*"valores positivos para acréscimos, negativos para descontos"*), e o bloco **Produtos com preços diferentes** — tabela Produto · Código (SKU) · **Preço** · **Preço promocional** com **edição inline e link "salvar" por linha**, lixeira na linha já gravada e `⊕ adicionar item`. Rodapé avisa que acréscimos e descontos **não valem para vendas do app móvel e da API**.

### Fechamento da aba *cadastros* — cinco leituras

1. **"Tipos de contato" fecha a pergunta do cliente/fornecedor — e aumenta o problema.** O perfil do contato tem **seis** valores, entre eles **Vendedor** e **Funcionário**. Não são dois cadastros que o Olist unifica: são cinco. Nós temos **Clientes**, **Fornecedores** e **Vendedores** como três cadastros separados já construídos e validados, mais **Transportadoras** no Operacional.
   **Posição:** *não unificar as telas.* Os três têm campos que não se sobrepõem — fornecedor tem bloco fiscal ativo, vendedor tem acesso, permissões, comissionamento e metas, cliente tem limite de crédito e vínculo com vendedor. Unificar custa refazer seis telas validadas.
   **O custo de não unificar, que não dá para esconder:** se o mesmo CNPJ for cliente e fornecedor, viram dois registros que divergem de cadastro, e o **financeiro não consegue compensar** conta a pagar contra conta a receber da mesma pessoa — justo o módulo que vem a seguir.
   **Meio-termo proposto:** uma tabela `pessoas` por baixo, **chave única por CPF/CNPJ**, com cada cadastro sendo uma *faceta* dela. As telas continuam especializadas, e o financeiro enxerga que é a mesma pessoa. É a mesma jogada do ledger de estoque: um dado embaixo, muitas telas em cima. ~~A decidir com o usuário.~~ → ✅ **Resolvido (21/set, item 2):** `pessoas` descartada — a Desk só compra de fornecedor, não vende para ele. A tabela-faceta fica registrada como caminho, não como pendência.
2. **O comissionamento por faixa de desconto já existe no nosso sistema — no vendedor.** `pagina-cadastros-vendedores-detalhe.html` já traz os mesmos dois rádios (*alíquota fixa* / *alíquota conforme descontos*) e o campo de alíquota. O Olist repete a mecânica na **linha de produtos**. Se as duas existirem, **é preciso uma regra de precedência** — produto define o teto e vendedor o praticado, ou uma sobrepõe a outra. Sem isso, duas fontes calculam comissões diferentes para a mesma venda.
3. **Tags: temos, mas soltas; lá são agrupadas.** Nosso produto-detalhe guarda tags como chips livres (`tagsProduto`). Grupo de tags é melhor: evita "azul" e "Azul" virarem duas, e permite filtrar por eixo.
4. **Padrão de tabela novo: edição inline com "salvar" por linha.** A linha em edição vira inputs com link *salvar*; a gravada vira texto com lixeira. **Não existe no nosso sistema** — nossas tabelas de montagem usam drawer (Acerto, Nova transferência) ou input direto sem confirmação (Inventário). Seria um terceiro padrão: adotar só se ganhar algo que os dois atuais não dão.
5. **"Linha de produtos" é um quinto agrupador.** Já temos Categoria, Departamento, Seção e Marca. Linha é agrupamento **comercial** (existe para carregar a regra de comissão), não merceológico — registrar isso agora evita que vire "mais uma categoria" depois.

**Aba *cadastros* completa.**

### Prints — aba *suprimentos* (completa, 16/set/2026)

A aba que mais toca no que já está construído. Índice: Depósitos de estoque · Configurações de estoque · Configurações do envio de documentos · Marcadores nas ordens de compra · Marcadores nos serviços tomados · Configurações de ordens de compra · Configurações de conferência de compra.

- **Depósitos de estoque** — listagem com busca + pill *Ativos*, linha com badge **Depósito Padrão**, rodapé com contagem. Topo: `⚙ configurações` + **incluir depósito**.
  - *Configurações adicionais de depósitos* (drawer): toggle **"Reserva de estoque individual por depósito"** — cada depósito com controle próprio de reserva.
  - *Depósito* (drawer): Descrição, **Tipo** (**Próprio** / **Exclusivo para um canal de venda**) e toggle **"Desconsiderar saldo deste depósito"**. Com o tipo *canal de venda*, abrem **CNPJ destinatário** (repetível), **CNPJ Remetente** e o toggle **"Criar transferências de estoque para notas fiscais com os CNPJs informados acima"**.
- **Configurações de estoque** — a mais densa do lote. **Permite estoque negativo** (Sim / Não – validar todos os depósitos com saldos a considerar / Não – validar o depósito selecionado na venda). **Lançamento para saídas** (Manual · ao autorizar a NF · ao salvar a NF · ao salvar o pedido · ao marcar pedido como enviado), com aviso contextual de que o automático ao salvar o pedido **invalida a reserva de estoque**. **Lançamento para entradas** (Manual · ao autorizar a NF · ao salvar a NF · **ao salvar a ordem de compra** · **ao finalizar conferência de compra**). **Lançamento para serviços** e **Estorno** (manual / ao cancelar NF). Toggles: exibir estoque na lista de preços · estornar ao cancelar pedido · **e-mail de produtos abaixo do mínimo** (+ endereço) · **quantidade enviada ao e-commerce quando sob encomenda** (99) · considerar saldo no sob encomenda · **confirmar lotes e validades ao lançar estoque individualmente** · **permitir editar quantidade lida na importação de inventário**.
- **Envio de documentos (suprimentos)** — Ordem de compra: *enviar apenas link* / *link e PDF em anexo*, **Assunto padrão** e **Mensagem padrão** com placeholder `[NOME_FORNECEDOR]`. *Nome igual ao da tela da aba geral (que é sobre WhatsApp) — ruído do Olist.*
- **Marcadores** — duas telas idênticas, escopos diferentes (*Ordens de compra* e *Serviços tomados*), com **título + subtítulo de escopo**. Cadastro: Descrição + **Cor do marcador** (paleta); a listagem mostra o quadrado de cor ao lado da descrição.
- **Ordens de compra** — **Numeração** (Sequencial / Manual) · **Preço na ordem de compra** (última entrada / preço de custo / zerado) · toggle de imprimir imagem dos produtos.
- **Conferência de compras** — dois toggles: **"Ocultar quantidade de itens para conferência"** e **"Ocultar quantidade de volumes para recebimento"**, ambos **desligados por padrão**.

### Fechamento da aba *suprimentos* — seis leituras

1. **A conferência cega: nós já temos, e melhor.** `pagina-estoque-conferencia.html` já traz o interruptor **"Conferência cega"** *ligado por padrão*, com o hint *"quem confere conta o que vê, não o que o papel diz"*. O Olist tem o mesmo parâmetro **global e desligado**. **Proposta:** o global em Configurações define o **padrão**, e o interruptor da tela permite a **exceção pontual** — os dois níveis, em vez de escolher um. E como lá são **dois** toggles (itens na conferência, volumes no recebimento) e nós temos as duas telas separadas, vale separar também.
2. **Nem todo parâmetro deles merece virar parâmetro nosso.** *"Lançamento para entradas: automático ao finalizar conferência de compra"* é **uma das cinco opções** lá e é **regra dura** aqui. Aqui eu **não** transformaria em parâmetro: as outras quatro opções desmontam o que já construímos — estoque nascendo "ao salvar a nota" deixa a fila de Conferência de Compra sem função, o Endereçamento nasce vazio e `em_conferencia` vira estado morto. **O contraste com o item 1 é a leitura central deste lote:** lá o parâmetro muda um comportamento local; aqui ele derruba quatro telas. Vários parâmetros do Olist existem porque o Olist **não tem** as etapas que nós temos.
3. **"Desconsiderar saldo deste depósito" é algo que precisamos e não temos.** O nosso depósito de **Trânsito** é, por definição, um depósito cujo saldo não conta como disponível — hoje isso vive como regra no código da Transferência. Como **flag no cadastro** fica explícito, e serve também ao depósito de canal de venda. E repare que ele se amarra ao *"validar os saldos de todos os depósitos **com saldos a considerar**"*: um parâmetro depende do outro.
4. **"Exclusivo para um canal de venda" é fulfillment (Full / FBA).** Depósito com **CNPJ destinatário e remetente** e transferência automática quando a NF-e bate com esses CNPJs é a mecânica de mandar estoque para o CD do marketplace. Nosso cadastro tem *galpão · loja física · trade marketing · trânsito*. **Registrar como tipo previsto** — quando a Desk entrar em marketplace com fulfillment, ele muda a listagem de Depósitos que já existe.
5. **"Permitir editar quantidade lida na importação de inventário" julga uma decisão que tomei sozinho.** No Inventário construído em 16/set eu deixei a quantidade importada **editável**, sem perguntar. O Olist faz disso um parâmetro e o entrega **desligado** — o default deles é *não deixar mexer no que o coletor leu*, e a lógica é boa: leitura editável deixa de ser evidência. **Mantenho editável** porque a nossa importação abre em modo revisão e o operador precisa corrigir leitura duplicada, mas fica **registrado como parâmetro futuro** e com a ressalva de que o default deles tem fundamento. *(Decidido — o parâmetro entra junto com "Configurações de estoque", que espera Vendas.)*
6. **Marcadores com cor escolhida a dedo pedem cuidado.** Nós resolvemos cor por tema, com **contraste medido** (a tinta automática do design-system). Um seletor de cor livre reabre exatamente o bug do texto branco em fundo claro — se adotarmos, a tinta automática tem que continuar valendo sobre a cor escolhida. **Padrão útil daqui:** título com **subtítulo de escopo**, para telas iguais que servem a domínios diferentes.

**Onde os nossos limiares se encaixam:** os três parâmetros que guardávamos (Conferência de Compra > 1 / > 3 dias · Endereçamento parado > 2 / > 7 · Estoque zero > 7) moram nesta aba. O Olist **não tem** nenhum deles — são nossos, e continuam sendo.

**Abas *geral*, *cadastros* e *suprimentos* completas.**

### Prints — aba *vendas* (lote 1: 20 telas, 16/set/2026) 📁 *referência — o resto dos prints desta aba é pedido quando a tela for construída*

**Novidade estrutural:** esta aba **agrupa em subseções com cabeçalho** — um bloco solto no topo, depois **Expedição e Logística** (Formas de envio · Gateways logísticos · Expedição · Separação · Marcadores na separação · Intelipost) e **CRM** (Configurações do CRM · Marcadores no CRM · **Estágios no funil do CRM**). As abas anteriores eram lista plana. E repare que **os grupos não batem com os módulos**: Logística e CRM são módulos próprios no nosso menu, e aqui vivem dentro de *vendas*.

- **Configurações do PDV** — a mais longa do lote. **Situação padrão para vendas finalizadas** (Em aberto · Aprovado · Preparando envio · Faturado · Pronto para envio · Enviado · Entregue — *é o ciclo de vida do pedido*). Marcador padrão · Lista de preço preferencial · **Natureza de operação padrão para NFC-e** (lista fiscal completa). Bloqueio de venda sem estoque com a opção **"Utilizar configuração padrão dos pedidos de venda"**, com link para a outra tela. Depósito padrão. **Fechamento de venda:** vendedor obrigatório · cliente obrigatório · bloquear venda com total recebido inferior · permitir produto não cadastrado · bloquear alteração de preço unitário · agrupamento automático de produtos iguais · mostrar tela de formas de recebimento. **Tipo de nota** (emitir NFC-e automaticamente / permitir NF-e) e **Impressão automática ao finalizar venda** `BETA`, num **dropdown multi-seleção com checkboxes** (Selecionar todas · Recibo · NFCe · Recibo de troca). **Desconto máximo nos itens** e **Desconto máximo nos itens para gerente**. **Fechamento de caixa:** controlar abertura/fechamento · considerar recebimentos do "faturar pré-venda" · compartilhamento de caixa entre usuários · exibir valores por forma de recebimento · abrir caixa com o último valor de fechamento. **Separação de recebimento** (venda do vendedor vai para o operador de caixa, que confirma e emite a nota). Código de barras da balança (por preço / por peso). Atalhos na tela de vendas.
- **Propostas comerciais** — Numeração (Sequencial/Manual) · toggles de impressão (NCM, descrição complementar, e-mail do usuário, impostos) · **Calcular impostos nas propostas** · replicar marcadores da proposta no pedido · **Imprimir imagens** (não imprimir / ao lado da descrição / em seção separada) · Observação padrão · Desconto máximo (itens e gerente).
- **Pedidos de venda** — a mais densa. *Exibição:* preço de lista e desconto · alerta de endereço incompleto · **alerta de comissão zerada** · **visualizar contas a receber em aberto no pedido/nota** · marcador com status do pagamento; blocos com a opção **"Exibir recolhido"** além de Sim/Não. *Impressão:* código de barras do número, cabeçalho para produção, **campos de data e assinatura para comprovação de entrega**, endereço da empresa, imagem dos produtos, nome fantasia em vez de razão social, **calcular impostos nas vendas**; **Ordenação dos itens** (inclusão / SKU / descrição). *Outras:* **bloquear emissão de pedidos cujo cliente possui contas em atraso** · bloquear sem forma de recebimento · permitir edição pelo vendedor · **inserir automaticamente o marcador "1ª venda"** · replicar marcadores na NF · bloquear exclusão de ocorrência · **mudar status de "em aberto" para "aprovado" após a identificação do pagamento** · considerar peso das embalagens no peso bruto. Numeração · **bloquear pedido com estoque que não pode ser atendido** (com a ressalva de que *não vale para API, app e e-commerce*) · **campo vendedor via API** (não aceita se não existe / aceita sem / cadastra automaticamente) · quantidade de volumes padrão · **aviso de contas a receber em atraso** (não avisar / a partir de 1 a 10 dias) · desconto máximo · observação padrão · **depósito para lançamento de estoque de devoluções de vendas** (mesmo depósito da venda/nota · padrão · geral).
- **Envio de documentos (vendas)** — quatro seções: **DANFE · Vendas · Propostas comerciais · Devoluções de venda**, cada uma com compartilhamento por e-mail, assunto, mensagem e **"Defina como os arquivos PDF serão nomeados"**. O link **"Exibir variáveis disponíveis"** abre um painel listando cada placeholder **com a descrição ao lado** — `[NOME_CLIENTE]`, `[DOCUMENTO_CLIENTE]`, `[NUMERO_PEDIDO]`, `[LINK]`, `[DATA_VENDA]`, `[DATA_ENTREGA]`, e todo o bloco de cobrança: `[CHAVE_PIX]`, `[EXPIRACAO_PIX]`, `[VALOR_PIX]`, `[LINK_PIX]`, `[VENCIMENTO_LINK_PAGAMENTO]`, `[LINK_PAGAMENTO]`. A DANFE ainda tem os toggles *enviar PDF em anexo* e *enviar DANFE no corpo do e-mail*.

**Três avisos que já dá para dar (o resto fica para o fechamento da aba):**

1. **Existem DOIS "caixas" com o mesmo nome, e vamos construir um deles.** O **fechamento de caixa do PDV** (gaveta, turno, abertura e fechamento por operador) não é o **Caixa e Bancos** do §9 (extrato de conta, saldo, transferência entre contas). São coisas diferentes com o mesmo rótulo — e como o §9 entra em seguida, **decidir o nome agora** evita que as duas telas nasçam se confundindo. Sugestão: *Caixa e Bancos* (financeiro) e *Caixa do PDV* / *Turno de caixa* (operação). → ✅ **Resolvido na construção (22/set):** a tela financeira se chama **Caixa e Bancos** (item *Caixa* no menu Finanças); o do PDV é **turno de caixa**, e o hub já diz isso em *Configurações do PDV*.
2. **"Depósito para lançamento de estoque de devoluções de vendas" toca a regra de entrada (item 19), que já está viva em cinco telas.** Devolução é entrada, e entrada obedece base de picking → `disponivel`, sem base → `a_enderecar`. Escolher o depósito é uma coisa; **o destino dentro dele continua sendo a nossa regra**, e não pode virar exceção silenciosa.
3. **Três parâmetros amarram Vendas a Contas a Receber antes de Contas a Receber existir:** *bloquear pedido de cliente com contas em atraso*, *avisar a partir de N dias de atraso* e *mudar o status do pedido para aprovado quando o pagamento for identificado*. Entram no §11 como requisitos que a tela de Contas a Receber tem de suportar desde o desenho.

**Padrão que vale roubar:** o link **"Exibir variáveis disponíveis"**, com painel recolhível listando placeholder + descrição ao lado do campo que os aceita. Melhor que documentação externa — e note que o Olist resolve a mesma ideia de **duas formas diferentes** no mesmo sistema (aqui, lista recolhível; no construtor de etiqueta, menu *+ inserir*). **Escolher uma só.**

**Lote 2 da aba *vendas* (mais 20 telas, 16/set/2026):**

- **Marcadores nos pedidos de venda / nas propostas comerciais** — mesmas telas de marcador já vistas em *suprimentos*, com escopo no subtítulo. A seleção em massa abre **barra inferior com contador (`↑ 01`) e um botão primário AZUL "🗑 excluir marcadores"**.
- **Formas de envio** — listagem **Descrição · Tipo logística · Gateway logístico** com bolinha de status por linha; pill *habilitadas*; topo com **"✎ editar usuário de rastreamento"** (drawer com Usuário + Senha — credencial de rastreio), **incluir forma de envio** e `mais ações`. Linhas de exemplo: *Correios* (Correios), *Transportadora* (Transportadora), **"Retirar pessoalmente" (Customizado)**.
- **Forma de Envio** (página) — **Tipo logística**: Correios · Transportadora · **Mercado Envios** · Jadlog · Total Express · **Gateway logístico** · Customizado · Loggi · Mandaê (beta) · Posta Já · Nuvem Envio · Enviali. Mais Descrição, **URL de rastreamento padrão**, **Imprimir automaticamente ao finalizar embalagem** e **ao finalizar expedição** (dropdown multi-checkbox: DANFE · Etiqueta de envio), **Modelo da etiqueta para impressão** e o bloco **Configurações das formas de frete** com `⊕ adicionar forma de frete`.
  - *Configuração da forma de frete* (drawer): Descrição · **Código do serviço** · **Tipo de entrega** (Não definida · Normal · Expressa · Agendada · Econômica · Super Expressa · Retirada em mãos) · **Transportador**, com botão que abre o **Cadastro rápido**.
- **Gateways logísticos** — **Tipo**: Melhor Envio · Frenet · Datafrete · Frete Rápido · Flixlog · SmartEnvios (beta) · Super Frete (beta) · InteliPost. **Configurações de autenticação** com painel de estado *"Você não está logado — os dados de autenticação não foram informados"* e ação **efetuar login**. **Adicionais:** modelo da etiqueta (**ZPL / PDF**), **habilitar atualização automática de rastreios**, **dimensões para cotação** (as da tela de cotação / as dos produtos) e **nome da empresa na impressão de etiquetas** (razão social / fantasia).

**Três leituras deste lote:**

1. **Forma de envio, gateway logístico e transportadora são TRÊS coisas.** A *forma de envio* é o serviço vendido ao cliente (PAC, Sedex, retirada); o *gateway* é o intermediador que cota e emite etiqueta; a *transportadora* é quem carrega. A forma de envio aponta para o transportador, e pode apontar para um gateway. **Isto afeta a Transportadora (Desk Flash), que é o último item pendente da F2** — ela é *transportadora*, e vai precisar de uma *forma de envio* que a referencie, não é a mesma coisa. Registrar antes de construir.
2. **"Retirar pessoalmente" é uma forma de envio de tipo Customizado** — retirada em loja não é ausência de envio, é um envio com transporte nulo. Detalhe pequeno que evita um `if` espalhado depois.
3. **O Cadastro rápido apareceu pela terceira vez** (Caixa §9, Contas a Pagar §10, forma de frete). Não é tela: é **componente compartilhado** que qualquer campo de pessoa pode abrir. Entra no design-system como componente, não como página.

**Duas observações de padrão:**

- **O Olist é inconsistente consigo mesmo na ação destrutiva:** aqui a exclusão em massa é **botão primário azul com lixeira**; na Central de notificações (aba geral) o "remover dispositivo" era **outline vermelho**. Nós já temos `.btn-danger` na barra de seleção (`Excluir selecionados`, ao lado de `Inativar selecionados` em `.btn-secundario`) — **mantemos o nosso**: ação destrutiva em vermelho, sempre.
- **Painel de estado "não configurado" com ação** (*Você não está logado → efetuar login*) é um padrão melhor que campo vazio, e serve às nossas telas que dependem de módulo inexistente — hoje resolvidas com hint e campo desabilitado.

**Lote 3 — fecha a aba *vendas*:**

- **Configurações da expedição** — **Envio para a expedição** (Manual · ao salvar o pedido · ao aprovar o pedido · ao salvar a NF · ao autorizar a NF) · impressão automática (DANFE / Etiqueta de envio) · **Valor declarado** (sem valor declarado / o informado na venda e, se vazio, o total dos produtos) · imprimir valor declarado nas etiquetas · mostrar valor das mercadorias · **habilitar conferência de pedidos na expedição** · **e-mail do código de rastreio** (`[IDENTIFICACAO]`, `[CODIGO_RASTREIO]`) · **e-mail de entrega** (`[NOME_CLIENTE]`, `[NUMERO_PEDIDO_ECOMMERCE]`) · **envio do XML para a transportadora**, com toggle de envio automático ao concluir a expedição, para o e-mail de NF-e do cadastro do contato da transportadora.
- **Configurações da separação** — mesma lista de cinco gatilhos · impressão ao finalizar embalagem · toggles de impressão (observações internas, imagem do produto, GTIN, código de barras da venda, estoque disponível) · **reservar lotes automaticamente ao separar** · **substituir kits pelos seus componentes na separação e embalagem** *(já vem LIGADO)* · autorizar NF ao separar / ao concluir embalagem · criar e concluir expedições ao iniciar embalagem · **confirmar número de volumes ao término da embalagem** · ocultar adicionar itens manualmente · receber marcadores da venda/NF · **impedir que mais de um usuário separe ou embale o mesmo pedido** · **separador entre pedidos na impressão térmica** (pontilhado / quebra de página).
- **Configurações da Intelipost** — abas *dados gerais* / *transportadoras*. Chave da API + **testar configurações**, checkbox de endereço de origem diferente, toggles de integração, e **"Marcação de pedidos como entregues"**: campo somente-leitura com **botão de copiar** (é uma URL de webhook). A aba *transportadoras* sem chave mostra **"Erro ao obter mapeamento das transportadoras / Preencha a chave da API / fechar ESC"**.
- **Configurações do CRM** — um único campo: **nº de dias para indicar que o CRM está sem interação** (30).
- **Estágios do funil de vendas** — lista **reordenável por arrastar** (handle `=`), numerada: 1 Prospecção · 2 Contato realizado · 3 Proposta apresentada · 4 Negociação · 5 Encerrado. Drawer com um campo (Descrição do estágio).

### Fechamento da aba *vendas* — cinco leituras

1. **A mesma lista de cinco gatilhos aparece três vezes** — em *separação*, em *expedição* e no *lançamento de estoque* (aba suprimentos): Manual · ao salvar o pedido · ao aprovar o pedido · ao salvar a NF · ao autorizar a NF. Não é coincidência: são **pontos de engate no ciclo de vida do pedido**, e três consumidores diferentes assinam o mesmo conjunto. **Isso pede um conceito único de "eventos do pedido"** em vez de três listas iguais mantidas em paralelo — e no nosso caso o mesmo conceito já existe do lado da entrada (o estoque nasce no fechamento da conferência).
2. **"Impedir que mais de um usuário separe ou embale o mesmo pedido" é o nosso bloqueio de inventário, em escala menor.** Lá travamos o **depósito inteiro**; aqui trava-se **o pedido**. É a mesma família de problema — trabalho concorrente sobre o mesmo registro — e merece **um mecanismo só**, não um `if` por tela. Registrar como conceito: *bloqueio de registro em operação*, com dono e hora.
3. **"Substituir kits pelos seus componentes na separação" nasce ligado, e isso levanta uma pergunta que ainda não respondemos: o kit tem saldo próprio ou derivado?** No nosso mock, *Kit Home Office Completo* e *Kit Manutenção Desk Tech* têm **saldo próprio por endereço**, e o Acerto e o Inventário os tratam como produto comum. Se o kit é **montado e guardado** na prateleira, saldo próprio está certo. Se ele só é **juntado na hora de separar**, o saldo tem de ser derivado dos componentes — e aí o Inventário não deveria deixar contar "kit" como item. **A decidir com o usuário; é pergunta de operação, não de tela.** → ✅ **Resolvido (21/set, item 5):** o kit tem as duas formas, montado (saldo próprio) e derivado (sem saldo).
4. **Reordenação por arrastar é padrão que não temos.** Nos estágios do funil, **a ordem é o dado** (funil é sequencial), e a tela tem handle e número. É o único lugar de todo o lote onde a posição significa algo. Fica registrado como padrão pendente — a construir só quando o CRM existir. ⏸ *espera o CRM.*
5. **Expedição e Separação estão na aba *vendas* do Olist, mas são Logística no nosso menu** — confirma o que a estrutura da aba já indicava: os agrupamentos do hub deles não são os nossos módulos. **A nossa aba de configuração segue o NOSSO menu**, senão o usuário procura "separação" em Vendas e não acha.

**Padrão útil:** o **erro com causa e ação** da aba *transportadoras* da Intelipost (*"Erro ao obter mapeamento — preencha a chave da API"*) e o **campo somente-leitura com botão de copiar** (webhook) são os dois melhores detalhes do lote. O primeiro serve a toda tela nossa que depende de algo ainda não configurado.

**Abas *geral*, *cadastros*, *suprimentos* e *vendas* completas.**

### Prints — aba *notas fiscais* (lote 1: 20 telas, 17/set/2026) 📁 *referência — o resto dos prints desta aba é pedido quando a tela for construída*

**Padrão novo e muito útil: badge de estado no próprio índice.** Os itens trazem etiquetas âmbar — *Dados da empresa* `Configuração pendente`, *Certificado digital* `Configuração pendente`, *Ambiente das notas fiscais* `Ambiente de testes`. **O índice diz o que falta configurar**, sem o usuário ter que entrar em cada tela para descobrir. Não temos nada parecido.

Subgrupos da aba: **Configurações gerais** (dados da empresa · certificado digital · ambiente · naturezas de operação de **entrada** · naturezas de operação de **saída**) · **Notas fiscais de venda** (NFe · ICMS DIFAL para não contribuinte · cálculo diferenciado de ST para contribuintes · **GNRE** · **cadastro de intermediadores** · marcadores) · **Notas fiscais de entrada** · **Notas fiscais de serviço**.

- **Dados da empresa** — **a mesma tela da aba *geral*, repetida aqui**. Terceira ocorrência de tela compartilhada entre abas (junto com *envio de documentos*, que aparece em três, e *Marcas*, que aparece em Cadastros e em Configurações). Faz sentido: a NF-e depende desses dados. **Confirma que uma tela pode aparecer em várias abas do hub.** Campos que só deram para ver agora: **Segmento de atuação** (lista longa de segmentos de e-commerce), **Código de regime tributário** (Simples nacional · Simples nacional — excesso de sublimite · Regime normal · MEI), **Canal de Comunicação** como dropdown multi-checkbox, e a lista de UFs das IEs de substituto incluindo **EX** (exterior).
- **Certificado digital** — escolha entre dois cards grandes com ícone: **A1** (arquivo digital, fica armazenado no servidor) e **A3** (cartão ou token, precisa estar conectado na hora da emissão), com texto explicativo abaixo. Mesmo padrão do nosso índice de Inventário.
- **Ambiente da Nota Fiscal** — dois **cards-rádio** lado a lado: **produção** (emissão com validade jurídica) e **homologação** (testar emissão), com o aviso *"As notas cadastradas em um ambiente não são exibidas no outro"*. Botão **testar ambiente** devolve status inline: **"Serviço em Operação — tempo médio de resposta: 1s"**, com sinal verde.
- **Naturezas de operação (Tributação)** — listagem **Descrição · Padrão · Série · Consumidor final** + status, com `⚙ configurações`, **incluir natureza de operação**, pill *ativas* e `⊖ limpar filtros`. Exemplos reais: devolução de venda de produção própria e de terceiros, entrada de bonificação/doação/brinde, retorno de mercadoria de depósito fechado, retorno de conserto.
- **Natureza de operação — cadastro.** Descrição · **Finalidade** (Normal · Devolução · Bonificação · Remessa) · Código de regime tributário · **Série** · **Consumidor final** · **Observações padrões** com *variáveis disponíveis*. Abas de imposto: **Simples · IPI · ISSQN · PIS · COFINS · importação**. Na aba Simples: **CSOSN** (101 · 102 · 103 · 201 · 202 · 203 · 300 · 400 · 500 · 900), **CFOP**, **ICMS DIFAL para não contribuinte**, *Observações do Simples* e *Informações ao Fisco*. No fim, **Exceções** e **Configurações avançadas** (recolhido).

### Dois achados que valem mais que o resto do lote

1. **O `?` do CFOP é curinga, e isso é uma sacada.** O campo vem preenchido como **`?.201`** — o primeiro dígito do CFOP muda conforme a operação: **5** dentro do estado, **6** interestadual, **7** exterior. Em vez de obrigar o usuário a cadastrar três naturezas quase idênticas, o Olist deixa escrever `?` e resolve na emissão. **Vale adotar**, e afeta o que já registramos: a baixa por perda do Acerto usa **CFOP 5.927**, que no nosso cadastro passaria a ser **`?.927`**.
2. **"Exceções" não é um campo, é um motor de regras fiscais.** O drawer é um **wizard** (botão *próximo*): *quando o destinatário for um destes **estados*** (multi-checkbox de UFs) · *para os seguintes **produtos*** · *para as seguintes **origens*** (a tabela oficial de origem do ICMS, **0 a 8**, com o texto legal completo de cada código) · *para as seguintes **NCMs*** (campo com *salvar* inline e `⊕ adicionar`). Ou seja: **a mesma natureza de operação tributa diferente conforme destino, produto, origem e NCM.** É de longe a peça mais complexa do módulo fiscal, e é o que permite uma natureza servir ao país inteiro em vez de virar dezenas de cadastros.

**Um cuidado de nomenclatura:** a **Finalidade** aqui (*Normal · Devolução · Bonificação · Remessa*) **não é** o campo `finNFe` do layout da NF-e (*1 Normal, 2 Complementar, 3 Ajuste, 4 Devolução/Retorno*), que a nossa **Entrada de Notas já usa** e está registrado no §3 item 21. São dois campos com o mesmo nome e valores diferentes — **têm de ter rótulos distintos no nosso sistema**, senão alguém vai preencher um achando que é o outro.

**Lote 2 da aba *notas fiscais* (mais 20 telas, 17/set/2026):**

- **Naturezas de operação de SAÍDA** — a listagem agora com a coluna **Padrão preenchida**: *"Padrão para venda"* e *"Padrão para NFCe"*. **Padrão não é booleano, é papel:** cada tipo de documento tem a sua natureza default. Na lista: venda de terceiros e de produção própria (para consumidor final, consumidor final contribuinte e contribuinte), devolução de compra para comercialização e para industrialização, remessa para conserto, remessa em bonificação/doação/brinde e remessa para depósito fechado.
- **Natureza preenchida de verdade — "(NF-e) Venda de mercadorias de terceiros para consumidor final"**: Finalidade *Normal*, Simples nacional, Série 1, Consumidor final *Sim*, e a observação padrão com o **texto legal do Simples**: *"Documento emitido por ME ou EPP optante pelo Simples Nacional. Não gera direito a crédito fiscal de ICMS, ISS e IPI."* CSOSN **102**, **CFOP 5.102 fixo**. As abas de imposto aqui são **Simples · IPI · ISSQN · PIS · COFINS** — **sem a aba *importação***, que só aparece na natureza de **entrada**.
- **Exceções, agora com dado:** tabela **Destino(s) · Produto(s) · CFOP · Situação tributária**, com **duplicar** e **excluir** por linha. A linha real lista **26 UFs (todas menos a da empresa)**, *Qualquer produto*, CFOP **6.108**, ST 102.
- **Outras naturezas:** *Remessa em bonificação* → Finalidade **Bonificação**, CSOSN **400 — Não tributada**, CFOP **`?.910`**. Natureza nova em branco → CSOSN 400, CFOP **`?.102`**, ICMS DIFAL **Sim**.
- **Configurações adicionais de tributação** (o `⚙` do topo da listagem) — drawer com **um único toggle**: *Preencher IPI devolvido nas devoluções*.
- **Configuração da NF-e** — **Número da primeira nota fiscal**; **Automações** (gerar NF ao aprovar pedido · autorizar automaticamente NF gerada da venda · **cancelar automaticamente a NF ao cancelar a venda vinculada**); e um bloco **Configurações adicionais** recolhível com: e-mail em cópia · **padrão do campo "frete por conta"** (CIF · FOB · terceiros · transporte próprio do remetente · do destinatário · **sem ocorrência de transporte**) · espécie padrão dos volumes · **validar NCM** (ligado) · importar nº da OC nas observações · campos de combustíveis, defensivos agrícolas e guia de trânsito · substituir endereço do destinatário pelo de entrega · **bloquear edição do número da NF** (ligado) · bloquear NF com menos itens que a venda · **indicador de presença do comprador** (não se aplica · presencial · pela Internet · teleatendimento · outros) · **CNPJ/CPF da Contabilidade** · **markup para formação do preço de venda** · UF exige código de benefício fiscal. Mais o bloco **DANFE** (itens na 1ª página = 7, nas demais = 47, fonte **Arial / Times New Roman**) e **Impressão** (remover endereço do destinatário, do emitente, valor total e GTIN/EAN no layout etiqueta).
- **ICMS DIFAL para não contribuinte** e **Cálculo diferenciado de ST para consumidor contribuinte** — uma tela inteira para **um único toggle** cada.
- **Configuração da GNRE** — layout de **duas colunas**: campo à esquerda, **explicação longa à direita**. Categoria padrão para as contas a pagar das GNREs · **enviar a NF ao módulo GNRE ao autorizar** (ligado) · gerar as guias automaticamente · **marcador padrão** para essas contas · **forma de pagamento padrão da guia** (Boleto, com a ressalva de cair no boleto quando não houver PIX) · **data de vencimento padrão** (data de saída/emissão da NF) · **Configurações adicionais de estados** com `⊕ editar regras`.

### Três leituras deste lote

1. **Agora dá para ver por que existem DUAS mecânicas para o CFOP.** A natureza padrão traz **5.102** (venda dentro do estado) e uma **exceção** cobrindo as outras 26 UFs com **6.108**. Se fosse só o primeiro dígito, o curinga `?.102` resolveria — mas **6.108 não é "5.102 com 6 na frente"**: o final do código também muda, porque a operação interestadual para não contribuinte tem CFOP próprio. **Conclusão: o curinga serve quando só o primeiro dígito muda; a exceção serve quando o código inteiro muda.** As duas precisam existir, e isso não é redundância do Olist.
2. **A GNRE gera CONTA A PAGAR automaticamente — é a ponte fiscal → financeiro que ainda não tínhamos mapeado.** Categoria, marcador, forma de pagamento e data de vencimento da conta são configurados *na tela fiscal*, e a conta nasce em Contas a Pagar (§10). E a lista de categorias oferecida é **a mesma** `categorias_financeiras` do Caixa — confirma que o cadastro é compartilhado. **Registrar como quarta fonte de título:** além de nota de entrada (duplicatas), pedido de venda (a receber) e lançamento manual, **imposto apurado também vira título**.
3. **Uma tela inteira para um toggle é decisão deliberada, não preguiça.** *ICMS DIFAL para não contribuinte* e *Cálculo diferenciado de ST* têm página própria com título completo e referência legal (EC 87/2015). Para parâmetro fiscal isolado, isso é melhor que enterrá-lo numa lista — o nome da tela vira a documentação.

**Padrão de layout a adotar:** **campo à esquerda, explicação à direita** (duas colunas), usado na GNRE. Nosso `field-hint` embaixo do campo funciona para uma linha; para texto longo, a coluna da direita é muito superior — e o módulo fiscal é todo feito de explicações longas.

**Lote 3 — fecha a aba *notas fiscais*:**

- **GNRE, detalhes dos campos:** *Forma de pagamento padrão da guia* = **Boleto / Pix**; *Data de vencimento padrão* = **data de saída/emissão da NF** ou **data de geração da guia**; *Marcador padrão* oferece só "Sem marcador" porque nenhum marcador foi cadastrado ainda.
- **Configurações adicionais de estados (GNRE)** — modal com dropdown de UFs em que **cada estado carrega seu próprio badge `configuração pendente`**. Alguns aparecem configurados (Amapá, Ceará, Paraíba, Paraná, Rio de Janeiro, Rondônia, Rio Grande do Sul, Sergipe), os demais pendentes.
- **Intermediadores** — listagem com busca por nome ou CNPJ e pill *filtros*, com estado vazio que diz **"Selecione um filtro para a pesquisa"** (a lista não carrega sozinha). Cadastro: **Nome** (ⓘ *"nome do usuário ou identificação do seu perfil no site do intermediador"*), **Canal de venda** (lista enorme de marketplaces — Amazon, Shopee, Mercado, Magalu, Carrefour, Casas Bahia, TikTok, Temu, VTEX, Wish…), **CNPJ do intermediador da transação** e **CNPJ da instituição de pagamento**.
- **Marcadores** em três escopos — *Notas Fiscais* (saída), *Notas Fiscais de entrada* e *Notas de Serviço* —, mesmas telas já vistas, escopo no subtítulo.
- **Configurações de notas fiscais de entrada** (`início › suprimentos › configurações`), título *"Configurações gerais"*: **Envio para a conferência de compra** (*Manual* / *Automático ao salvar a nota*) e **Considerar código do fornecedor** — *"preencher código (SKU) do produto com código do fornecedor ao importar xml da nota"*.

### Fechamento da aba *notas fiscais* — cinco leituras

1. **"Envio para a conferência de compra" é o contra-exemplo perfeito do que discutimos em *suprimentos*.** Nossa Entrada de Notas manda para a conferência por **ação manual** (`Enviar para conferência`, no menu). O Olist faz disso parâmetro *Manual / Automático ao salvar*. **Aqui vale virar parâmetro**, ao contrário do "lançamento de estoque ao finalizar conferência": as duas opções convivem sem desmontar tela nenhuma — muda *quando* a nota entra na fila, não *o que* a fila significa. **A régua fica assim: parâmetro que muda o momento, sim; parâmetro que apaga uma etapa, não.**
2. **"Considerar código do fornecedor" expõe um buraco real na nossa Entrada de Notas.** Nosso botão **Importar XML** já existe, mas o XML traz o código do produto **no cadastro do fornecedor** — que não é o nosso SKU. Hoje não tratamos isso: ou o item não casa, ou casa errado. O toggle do Olist é a solução grosseira (sobrescrever o SKU pelo código deles). **A solução certa é uma tabela de-para `produto_fornecedor` (produto, fornecedor, código do fornecedor, GTIN do fornecedor)**, preenchida na primeira conferência e reutilizada nas próximas — o mesmo produto tem um código em cada fornecedor. **Registrar como pendência da Entrada de Notas.**
3. **Intermediadores é obrigação fiscal, não cadastro opcional.** *CNPJ do intermediador da transação* + *identificação do perfil no site* são exatamente os campos **`CNPJIntermediador` e `idCadIntTran`** do grupo de intermediador da NF-e, exigidos em venda por marketplace. Sem eles, a NF-e de venda por marketplace é rejeitada. **Amarra com o §11:** o mesmo intermediador que desconta a comissão (`valor_taxas`, `valor_liquido`) é o que precisa constar na nota. Quando o marketplace entrar, **as duas pontas nascem juntas**.
4. **O badge de estado aparece pela terceira vez** — no índice da aba, nos itens *Dados da empresa* e *Certificado digital*; e agora **dentro de um dropdown, por UF**. É padrão sistêmico deles: **o item diz o próprio estado de preenchimento**, em vez de o usuário ter que entrar para descobrir. **Adotar de vez**, começando pelos Parâmetros de Estoque.
5. **Estado vazio que pede filtro em vez de listar tudo** (*"Selecione um filtro para a pesquisa"*) é a escolha certa para lista grande. Nossas listagens carregam tudo e paginam — o que serve enquanto os volumes são pequenos, mas vale ter esse padrão no bolso.

**Abas *geral*, *cadastros*, *suprimentos*, *vendas* e *notas fiscais* completas.**

### Prints — aba *finanças* (lote 1: 20 telas, 17/set/2026) 📁 *referência — o resto dos prints desta aba é pedido quando a tela for construída*

A aba que mais confirma — e em um ponto **melhora** — as decisões já fechadas no §12.

Subgrupos: **Geral** (configurações gerais · categorias de receita e despesa) · **Contas e caixa** (**cadastro de contas bancárias** e **cadastro de contas financeiras** — são **duas telas distintas**) · **Recebimentos e pagamentos** (formas de recebimento · formas de pagamento · **cadastro de gateways** · **configurações das maquininhas de cartão**) · **Avisos e emails** (contas a pagar · contas a receber · envio de documentos) · **Marcadores**.

- **Configurações gerais (finanças)** — a tela central. **Lançamento de contas a receber**: Manual · ao salvar o pedido · ao aprovar o pedido · ao salvar a NF · **ao autorizar a NF** (selecionado). **Lançamento de contas a pagar**: Manual · ao autorizar a NF · ao salvar a NF · **ao salvar a ordem de compra**. **Lançamento de contas nos serviços** (quatro variantes de OS/NFS). **Estorno de contas**: automático ao cancelar pedido / ao cancelar pedido ou NF, com a nota de que excluir a NF também estorna. **Forma de pagamento padrão** (Boleto/Pix) e **forma de recebimento padrão** (Dinheiro · Cheque · **Múltiplas**). **Padrão data de recebimento**: **Pagamento / Crédito** — *"considerado na baixa de um retorno"*. **Baixa de títulos**: **Agrupado / Individual**. Toggles de boleto (histórico e logo na impressão, **enviar linha digitável no histórico**) e **atualizar datas de vencimento das parcelas ao gerar notas fiscais**. E o bloco **Retorno Bancário**: **categoria padrão das liquidações do retorno**, **lançar tarifas no caixa** (ligado) com **categoria padrão das tarifas**, e **marcar como cancelados os títulos baixados no banco**.
- **Categorias de receitas e despesas** — listagem agrupada, colunas **Descrição · Categoria no DRE · Competência padrão**; topo com **grupos**, **incluir categoria** e mais ações, e uma tela irmã **Grupos de categorias** com alternância `grupos ↔ categorias`. O drawer de categoria tem **Descrição**, **Grupo** e a seção **Demonstração do resultado do exercício**: **Considera no DRE** (Não considera · Como deduções · Como despesas operacionais · Como outras receitas ou despesas · **Como tributos** · **Como taxas e tarifas**) e **Competência padrão** (Sem competência padrão · **Mês do vencimento** · **Mês anterior ao vencimento** · **Mês da emissão**).
- **Contas bancárias** — cadastro enxuto: **Banco** (lista com Banco do Brasil, Bradesco, Itaú, Santander, Inter, Safra, Banrisul, Banco do Nordeste, Caixa SICOB e SIGCB, HSBC, Sicoob, Sicredi, Olist Conta Digital) e **Descrição da conta**. A tela ainda carrega um bloco publicitário da conta digital do próprio Olist.

### Quatro leituras que mexem no §12

1. **"Baixa de títulos: Agrupado / Individual" e "Lançar tarifas no caixa" confirmam, literalmente, as duas decisões estruturais.** O parâmetro *Agrupado* só existe porque **uma baixa pode cobrir vários títulos** — é a tabela `baixas` N:N da decisão 2. E **tarifa bancária lançada no caixa é movimento sem título**, exatamente o exemplo que usei para justificar as duas tabelas da decisão 1. O modelo de referência chegou à mesma estrutura por outro caminho.
2. **A categoria financeira carrega a posição no DRE — e isso é melhor que a minha proposta.** Eu tinha proposto `natureza` (receita/despesa/ambas) na decisão 9. O Olist usa **Considera no DRE** com seis valores (*não considera · deduções · despesas operacionais · outras receitas ou despesas · tributos · taxas e tarifas*). **É superior:** carrega a mesma informação de sinal e ainda serve ao relatório de resultado, em vez de exigir um segundo campo depois. **Substituir `natureza` por `posicao_dre` no §12.**
3. **"Competência padrão" mora na categoria — e resolve o data ≠ competência sem encher o saco do usuário.** A decisão 1 do §12 criou `data_movimento` e `competencia` como campos separados, mas não disse quem preenche a competência. A resposta está aqui: **a categoria traz a regra** (mês do vencimento · mês anterior ao vencimento · mês da emissão), e o lançamento só a sobrescreve quando for exceção. Aluguel de dezembro pago em janeiro fica na competência certa sem ninguém pensar.
4. **"Padrão data de recebimento: Pagamento ou Crédito" é a quinta data.** Pagamento é quando o cliente pagou; **crédito é quando o dinheiro caiu na conta** — e em cartão, boleto e gateway são dias diferentes. Amarra direto com `valor_antecipado` do §11: antecipar recebível é justamente trocar a data de crédito por um desconto. **Entra na lista de datas do título.**

**Mais um achado a confirmar** *(→ ✅ confirmado na documentação do Olist em 21/set, item 3)*: o índice separa **"contas bancárias"** de **"contas financeiras"** — são duas telas. A segunda ainda não apareceu; a hipótese é que *conta financeira* seja o conceito amplo (caixa, carteira, conta de gateway, conta bancária) e *conta bancária* o subtipo com banco e agência. Se for isso, **é a conta financeira que o saldo do Caixa (§9) referencia**, não a bancária.

**Lote 2 da aba *finanças* (mais 20 telas, 17/set/2026):**

- **Conta bancária — cadastro completo:** Banco · Descrição · **Agência - Dígito** · e **"Conta financeira para o registro de lançamentos"**, campo somente-leitura com link *Alterar esta conta*. **Configurações do Pix**: tipo da chave (E-mail · CPF · CNPJ · Telefone · Chave aleatória) e a chave. **Configuração para cobrança como meio de recebimento**: *não emite boletos através desta conta* · *emissão de boletos **sem registro*** · *emissão de boletos **com registro (cobrança registrada)***, que abre CNPJ e endereço da instituição. Mais um bloco **Configurações do Sped**.
- **Contas financeiras** — subtítulo da própria tela: *"As contas financeiras são utilizadas no caixa, contas a receber e a pagar para classificar as receitas e despesas"*. Colunas **Descrição da conta · Número da conta na contabilidade**. A conta **Caixa** vem com **cadeado** (do sistema, não se exclui); as demais, não. O cadastro tem só **Nome da conta** e o checkbox **"Não considerar esta conta no saldo para fluxo de caixa e no saldo inicial do caixa"**.
- **Formas de recebimento** — catálogo do sistema com ícone por linha e colunas **Forma · Banco ou Gateway preferencial · Status**, todas ordenáveis: Dinheiro · Cartão de crédito · Cartão de débito · Boleto · Cheque · Depósito · Crediário · Vale-troca · Pix · **Cashback** · **Vale-presente**. Topo: **preferências** e **incluir forma de recebimento** — ou seja, o catálogo é fixo **mas extensível**.
- **Forma de recebimento — detalhe:** **Situação** (habilitada/desabilitada) · **Validar limite de crédito** (validar / não validar) · **Destino dos valores**: **Contas a receber** ou **Conta financeira**. Nas formas customizadas, um bloco **Configurações adicionais** com **Tarifação** (*sem taxas ou tarifas · em dia específico · no dia da transação · dia seguinte após a transação · no dia do pagamento, somada à taxa*) e **Antecipação dos recebíveis** (*sem antecipação / antecipado*).
- **Pix** e **Depósito** trazem ainda a tabela **"contas bancárias e gateways habilitados"** (Banco ou Gateway · Gateway preferencial · Ações), com *adicionar conta bancária* e *adicionar gateway*. **Vale-presente** só tem situação e validação de limite.

### Três respostas a perguntas que estavam abertas

1. **Hipótese confirmada: a conta bancária APONTA para a conta financeira.** O campo *"Conta financeira para o registro de lançamentos"* fecha a questão — **o lançamento e o saldo moram na conta financeira**; a conta bancária guarda o que é bancário (banco, agência, chave Pix, convênio de boleto, Sped). Então **é a conta financeira que o Caixa (§9) referencia**, e é ela que o título usa na baixa (§12, decisão 7). A conta financeira ainda carrega o **número da conta na contabilidade** — a ponte com o plano de contas — e o checkbox de **não entrar no fluxo de caixa**, que é o mesmo conceito do *"desconsiderar saldo deste depósito"* do estoque. **Padrão repetido no sistema: toda entidade que soma tem uma forma explícita de ficar fora da soma.**
2. **Nem toda venda gera conta a receber — e quem decide é a forma de recebimento.** O campo **Destino dos valores** (*Contas a receber* ou *Conta financeira*) é a chave: venda em **dinheiro** cai direto na conta financeira (vira movimento, o dinheiro já está lá); **cartão, boleto e crediário** viram **título**, porque o dinheiro só chega depois. Isso não estava no §12 e é decisão de modelagem: **a forma de recebimento determina se nasce título ou movimento.**
3. **`valor_taxas` e `valor_antecipado` do §11 têm origem — a forma de recebimento.** O bloco **Tarifação** define **quando** a taxa incide (dia da transação · dia seguinte · dia do pagamento) e **Antecipação dos recebíveis** marca se aquela forma é antecipada. Ou seja, **a regra não é digitada no título nem depende só do extrato do gateway**: ela vem da forma de recebimento e o sistema aplica. Isso torna os campos de valor do §11 **preenchíveis desde já**, mesmo sem integração de marketplace — que era a ressalva que o usuário levantou ao aprovar a decisão 4.

**Amarração de brinde:** **"Validar limite de crédito"** por forma de recebimento conversa com o **"Limite de crédito padrão para novos cadastros"** visto na aba *cadastros*. Faz sentido: **crediário** valida limite, **dinheiro** não precisa. É o mesmo limite, checado só onde importa.

**Lote 3 da aba *finanças* (17/set/2026):**

- **Meios de recebimento preferenciais** (drawer do botão *preferências*) — um dropdown para cada: **Boleto via banco · Boleto via gateway · Pix via banco · Pix via gateway · Crédito · Débito · Depósito**. É o **de-para meio → conta ou gateway padrão**, e repare no recorte: não é por forma, é por **meio × canal** — boleto *via banco* e boleto *via gateway* caem em lugares diferentes.
- **Formas de pagamento** — lista **diferente** da de recebimento: Boleto · Cheque · Crediário · Cartão de crédito · Cartão de débito · Depósito · **Depósito Bancário** · Dinheiro · **Duplicata Mercantil** · **Programa de fidelidade, Cashback, Crédito Virtual** · Pix · Vale-troca · **Vale Alimentação** · **Vale Combustível** · **Vale Presente** · **Vale Refeição** · **Transferência bancária, Carteira Digital** · **Outros**. O menu `⋯` de cada linha só oferece **"habilitar forma pagamento"** — não há tela de detalhe.
- **Gateways** — subtítulo explicando o conceito (*"intermediários entre as operadoras de cartões e a sua empresa. Exemplo: Cielo, Rede, Pagar.me"*). Cadastro minúsculo: **Gateway** (Pagar.me · Pagar.me 2.0 · Outro) · Descrição · Situação. O estado vazio **com filtro** vem com borda **âmbar** (*"Sua pesquisa não retornou resultados"*), diferente do estado vazio sem registros, que é azul.
- **Maquininhas de cartão** — página de integração com grid de marcas e modelos (Bin, Caixa, Cielo, GetNet, PagSeguro, PicPay, Rede, SafraPay, Sicredi, Sipag, Stone, Vero) e contador **"Maquininhas cadastradas 00/01"**. O fluxo é um wizard: **Termos de Uso** em painel rolável com checkbox *"Li e aceito"* travando o botão *avançar* → card da maquininha escolhida com **passos numerados 01/02/03** para instalar o app parceiro (*Smart TEF*) → botão *já instalei o app*. Tem ainda um painel **"Não encontrei o aplicativo parceiro"** com passo a passo 01–04 e link para abrir chamado, e uma tela de **erro de ativação** que mostra a mensagem amigável **e a mensagem técnica crua do parceiro** (*"Access denied due to invalid subscription key"*).

### Uma correção ao que registrei no §10

**"Boleto e Pix" não é limitação do Olist — eu li errado.** A lista completa de **formas de pagamento** é a **tabela oficial do campo `tPag` da NF-e**: dinheiro, cheque, cartão de crédito, cartão de débito, crédito loja (crediário), vales alimentação/refeição/presente/combustível, duplicata mercantil, boleto, depósito bancário, Pix, transferência/carteira digital, programa de fidelidade/cashback, e outros. O que eu vi no §10 era a lista **filtrada** daquele contexto.

**Isso muda a leitura do par:** *forma de recebimento* e *forma de pagamento* **não são espelhos**.

| | Forma de **recebimento** | Forma de **pagamento** |
|---|---|---|
| Natureza | **operacional** | **fiscal** |
| Serve a | como o dinheiro entra | o que vai no XML da NF-e |
| Configuração | destino dos valores, tarifação, antecipação, contas e gateways habilitados | **só habilita ou desabilita** |

Por isso a de pagamento não tem tela de detalhe: **não há o que configurar num código fiscal.** Registrar assim evita construirmos duas telas iguais para coisas diferentes — e evita inventar campos numa lista que é tabelada por lei.

**Dois padrões que valem levar:**

- **Contador de limite visível** (*"Maquininhas cadastradas 00/01"*) — diz quanto já se usou e quanto cabe, antes de a pessoa tentar e receber um erro.
- **Troubleshooting inline**: o link *"não encontrei o aplicativo"* abre um passo a passo numerado dentro da própria tela, em vez de mandar para a documentação. E o erro de integração mostra a mensagem amigável **junto** com a técnica. **A ideia é boa, a execução não:** despejar *"Access denied due to invalid subscription key"* no meio da tela é feio. A nossa versão é mensagem amigável com um **"detalhes técnicos"** recolhível — quem vai abrir chamado encontra, quem não vai não tropeça.
- **Estado vazio com cor por causa**: âmbar quando o filtro não achou, azul quando não existe nada cadastrado. Distinção útil e barata.

**Lote 4 — fecha a aba *finanças*:**

- **Configurações do contas a pagar** — **um único toggle**: *"Avisar por e-mail das contas a pagar na sua data de vencimento"*, com o endereço de destino.
- **Configurações do contas a receber** — **Avisar cliente por e-mail sobre contas a receber em aberto** (*não avisar · no dia do vencimento · no dia anterior · 2 dias antes · 5 dias antes*), com a ressalva de que só sai se o **SMTP estiver configurado**, e **Emissão automática de boletos** (*manual* / *automático ao salvar a conta a receber*).
- **Envio de documentos (finanças)** — **quarta tela com esse nome** (geral = WhatsApp, suprimentos = ordem de compra, vendas = DANFE/vendas/propostas/devoluções, finanças = boletos/Pix). Seção **Boletos**: `[NOME_CLIENTE]` `[DOCUMENTO_CLIENTE]` `[HISTORICO_BOLETO]` `[DATA_VENCIMENTO]` `[NUMERO_DOCUMENTO]` `[LINK]`, mais o toggle *enviar boletos junto com as notas fiscais, notas de serviço e pedidos de venda*. Seção **Pix**: `[CHAVE_PIX]` (ao usar a variável, **o QR Code também vai no e-mail**), `[EXPIRACAO_PIX]`, `[VALOR_PIX]`, `[LINK_PIX]` (página de cobrança com QR e copia-e-cola).
- **Marcadores (finanças)** — aqui eles fizeram **melhor que nas outras abas**: em vez de três telas separadas, é **uma tela com três abas** (*caixa · contas a pagar · contas a receber*) e o drawer traz **"Replicar este marcador também para"** com checkboxes. Em *suprimentos* e *vendas* os marcadores são telas independentes por escopo. **O Olist é inconsistente consigo mesmo — e a versão boa é esta.** Adotar a de abas + replicação.

**Assimetria deliberada e correta:** contas a **pagar** avisa **você**; contas a **receber** avisa **o cliente** — e só o aviso ao cliente tem antecedência configurável. Faz sentido: o vencimento da sua conta você já conhece; o do cliente é você que precisa lembrar.

**Aba *finanças* completa.**

### Prints — aba *e-commerce* (completa, 17/set/2026)

Índice curto: **Configurações gerais · Integrações · Token API**.

- **Configurações gerais (e-commerce)** — *número do pedido nas observações* · **Substituir kits pelos seus componentes nas integrações via API e na importação do e-commerce** (*sim, para kits e fabricados* / *sim, apenas para kits* / *não*) · **Buscar produtos por** (código ou descrição / apenas código) · **Preenchimento do campo "Nº do pedido no e-commerce ou Nº da ordem de compra"** (identificador do pedido no e-commerce / número do pedido no canal de venda).
- **Minhas Integrações** — cards com logo, nome e tipo, link *gerenciar*, e menu `⋯` com **ações destrutivas graduadas**: *inativar integração* → *excluir todos os anúncios no ERP* → *excluir integração*.
- **Integração (detalhe)** — **abas horizontais + menu lateral dentro de cada aba**, o nível de navegação mais profundo de todo o sistema: **Conexão** (nome + **credenciais**: identificador e token, somente-leitura com botão copiar) · **Produtos** → *Regras de Estoque / Preços / Fluxo de Produtos* · **Pedidos** → *Fluxo de Pedidos / Dados Fiscais* · **Notificações** → *URLs de notificações / Notificações de e-mail* (webhook de mudança de situação do pedido).
  - **Regras de Estoque:** *Atualizar estoque na loja virtual a partir do ERP* — **não atualizar / enviar saldo físico / enviar saldo disponível** · **Depósito a ser considerado na integração** (*Todos próprios*) · lançamento de estoque para saídas · **Utilizar estoque de segurança**.
  - **Fluxo de Pedidos:** enviar rastreamento ao marcar como enviado · **Intermediador** · e **"Defina como processar valores diferentes entre nota fiscal e pagamento integrado"** (*utilizar o valor do pagamento integrado enviado pelo canal — recomendado* / *considerar o pagamento como "não integrado"*).
- **Adicionar integração** — catálogo enorme com abas *todas · marketplaces e hubs · plataformas e-commerce · outras integrações*, centenas de cards com botão *instalar*.
- **Token API** — token somente-leitura, **gerar token API** e **remover token API** (link vermelho), com aviso explícito de que compartilhar o token dá acesso aos dados da conta.

### Fechamento da aba *e-commerce* — quatro leituras

1. **A definição de "disponível" deles aparece escrita na tela — e é a que nós descartamos.** O texto diz: *"A opção de estoque disponível equivale ao físico menos as reservas de estoque."* É exatamente a fórmula do Olist que rejeitamos em 14/set/2026. A nossa é `físico − a_enderecar − reservado − bloqueado`. **Consequência prática:** quando a Desk integrar com marketplace, o número que sai daqui vai ser **menor** que o que o Olist mandaria — e isso está **certo**, porque produto a endereçar não pode ser vendido. Registrar explicitamente: **a integração envia o NOSSO disponível**, e a diferença é proposital, não um bug a ser "corrigido" depois.
2. **"Estoque de segurança" é um conceito que não temos e vamos precisar.** É uma quantidade que nunca é oferecida ao canal — proteção contra venda simultânea em vários lugares, onde o tempo de sincronização cria overselling. Diferente de reserva (que é de um pedido concreto). **Entra na lista de estágios/parâmetros a decidir quando o marketplace entrar.** *(Espera marketplace — está no quadro do que está aberto, no fim do arquivo.)*
3. **"Substituir kits pelos seus componentes" aparece pela segunda vez, com escopo e opções diferentes.** Em *vendas* (separação e embalagem) era um toggle ligado; aqui (API e e-commerce) são **três opções**, incluindo *"kits e fabricados"*. **São dois parâmetros distintos com o mesmo nome** — e isso reforça a pergunta que fiz no fechamento de *vendas*: **o kit tem saldo próprio ou derivado?** Se tiver saldo próprio, mandar "componentes" para o canal e "kit" para a separação são duas mentiras diferentes sobre o mesmo estoque. → ✅ **Resolvido (21/set, item 5):** obrigatório para kit derivado, opcional para montado.
4. **"Valores diferentes entre nota fiscal e pagamento integrado" é a mesma família do `valor_liquido` do §11.** O canal manda quanto o cliente pagou; a NF diz outro valor; alguém tem de decidir qual vale. O default deles é **acreditar no canal**. É o mesmo problema visto do lado fiscal em vez do financeiro — e as duas pontas precisam da mesma resposta.

**Padrão de navegação registrado:** a tela de integração usa **abas horizontais + menu lateral dentro de cada aba**. É o nível mais profundo do sistema inteiro e existe **só ali**, onde há muita configuração por integração. Vale como precedente para uma tela específica, **não** como padrão geral.

### Prints — aba *tributação (RTC)* (completa, 17/set/2026) — **última aba**

Aba marcada com badge **`Novo`** e banner explicativo com link para guias. Índice em dois grupos: **NFe e NFCe** (*configuração dos tributos e códigos de classificação* · *habilitar cálculo de tributos da Reforma Tributária* `desabilitado` · *cadastro de regras tributárias*) e **NFSe** (as duas primeiras).

- **Configurações gerais para IBS/CBS da NF-e/NFC-e** — o texto diz que estas escolhas formam a **"Regra Geral", a configuração padrão de CST, cClassTrib e alíquotas para a maioria dos produtos e operações**.
  - **CST IBS/CBS**: 000 tributação integral · 010 alíquotas uniformes · 011 uniformes reduzidas · 200 alíquota reduzida · 221 alíquota fixa proporcional · 400 isenção · 410 imunidade e não incidência · 510 diferimento · 515 diferimento com redução · 550 suspensão · 620 tributação monofásica · 800 transferência de crédito · **810 ajuste de IBS na ZFM** · 811 ajustes · 820 tributação em documento específico · 830 exclusão da base de cálculo.
  - **cClassTrib** — campo com busca em painel próprio, onde cada código vem com **o texto legal completo** (*"000003 — Regime automotivo, projetos incentivados, observado o art. 311 da Lei Complementar nº 214, de 2025"*).
  - **CBS** — federal, **substitui PIS e COFINS**; alíquota exibida **0,90%**. **IBS UF** — estadual e municipal, **substitui ICMS e ISS**; alíquota **0,10%**.
  - **Outras configurações:** *"As alíquotas de IBS municipal e IS passarão a ser aplicadas a partir de janeiro de 2027 (art. 344, LC 214/2025)"*, com **Configurações do IBS Municipal** `em breve` e **Configurações do IS** `em breve`.
- **Habilitar cálculo de tributos da Reforma Tributária** — a tela explica os dois regimes: **Regime Normal (Lucro Real e Presumido)** tem obrigatoriedade a partir de **janeiro de 2026**; **Simples Nacional e MEI** podem habilitar para **simular**, com obrigatoriedade só em **2027** e a recomendação de *"confirmar com a sua contabilidade"* antes. O toggle avisa que o sistema passa a **calcular e enviar ao SEFAZ** IBS e CBS de todas as notas.
- **Cadastro de Regras Tributárias** — busca por **produto ou NCM**, seletor de colunas e pill *todas as naturezas de operação*. O cadastro é um **wizard** (avançar/voltar): *Dados do IBS/CBS* (CST + cClassTrib) → **Alíquotas do CBS** → **Alíquotas do IBS UF** → **Alíquotas do IBS Municipal** (principal, **de diferimento** e **redução**) → **Alíquotas do IS**.
- **NFSe** — as mesmas telas, com um campo a mais: **Código Indicador de Operação (cIndOp)**, seis dígitos, conforme tabela do Ambiente Nacional.

### Leituras da aba

1. **A Desk é Simples Nacional** (o campo *Código de regime tributário* em Dados da empresa diz isso), então: obrigatoriedade **só em 2027**, mas dá para habilitar antes **para simular**. As alíquotas exibidas (CBS 0,90% / IBS UF 0,10%) são as do **período de teste**, não as definitivas.
2. **Os campos de IBS/CBS precisam nascer no schema, mesmo desligados.** Mesma lógica da tabela `lotes` e dos campos de taxa do §11 — com uma diferença que pesa mais: aqui **a data é de lei**, não de conveniência. Adicionar depois significa migrar histórico fiscal.
3. **"Regra Geral + exceções por chave" é o terceiro sistema com a mesma forma.** Natureza de operação + *Exceções* (por UF, produto, origem, NCM); GNRE + *configurações adicionais por estado*; e agora RTC + *regras tributárias por produto ou NCM*. **Não é coincidência: é o padrão de todo cadastro fiscal brasileiro** — um default que cobre a maioria e uma tabela de exceções que cobre o resto. Vale construir **um componente só** para isso, e não três.
4. **Badge `em breve` com a citação do artigo** é honestidade barata e útil: diz o que não existe ainda e **por que**, com a fonte. Adotar.

---

## 14. Configurações — proposta de estrutura (17/set/2026) ✅ *aprovada em 18/set/2026*

Com as **oito abas mapeadas** (≈150 telas), dá para propor. *(Texto original da proposta. Aprovada em 18/set/2026 — o hub e 10 telas filhas já estão construídos.)*

### A forma

**Configurações deixa de listar páginas no flyout** e passa a ter **um atalho — "Configurações ERP" — mais o bloco Preferências (tema)**, que já mora ali. Isso **simplifica** a sidebar dos 38 arquivos em vez de complicá-la.

O destino é um **hub**: página índice com **busca** e **abas que filtram uma lista de links**. Cada link abre **página própria**, com breadcrumb `início › <módulo> › configurações › <tela>` e botão voltar — **o padrão que o sistema já usa**. Nada de navegação nova.

### As abas = os nossos módulos, não os deles

Os agrupamentos do Olist não são os nossos (lá *separação* e *expedição* vivem em Vendas; aqui são **Logística**). **A nossa aba segue o NOSSO menu**, senão o usuário procura onde não está:

**geral · cadastros · estoque · vendas · logística · finanças · operacional · fiscal · integrações**

*Fiscal ganha aba própria* — no Olist é "notas fiscais", e no nosso menu Notas Fiscais está dentro de Vendas, mas o volume (naturezas de operação, certificado, ambiente, intermediadores, RTC) não cabe como sub-item de vendas.

### O que já tem endereço

| Aba | Entra aqui |
|---|---|
| **geral** | Dados da empresa · Dados do usuário · Usuários do sistema · **Permissões de Usuários** · **Registro de confirmações por senha** · Interface do usuário · Central de notificações · Servidor de e-mail · Etiquetas |
| **cadastros** | Cadastro de clientes · Cadastro de produtos · Variações · Atributos · ~~Tags~~ *(fora — 29/set, mesma decisão dos marcadores)* · Tipos de contato |
| **estoque** | **Parâmetros de Estoque** (os três limiares hoje cravados no código) · Conferência (cega, padrão) · Conferência de compra · Ordens de compra · Notas de entrada |
| **finanças** | Configurações gerais · **Categorias financeiras** · **Contas financeiras** · **Contas bancárias** · Formas de recebimento · Formas de pagamento · Gateways · Avisos de vencimento |
| **fiscal** | Certificado · Ambiente · Naturezas de operação · Intermediadores · **RTC (IBS/CBS)** |
| **logística** | Formas de envio · Gateways logísticos · Expedição · Separação |

### Três componentes a construir uma vez e reusar

1. **Regra geral + exceções por chave** — serve a naturezas de operação, GNRE por estado e regras tributárias por produto/NCM. Três telas do Olist, **um componente nosso**.
2. ~~**Marcadores com abas de escopo + replicação**~~ — *descartado em 22/set: marcadores não existem neste sistema (design system §12.1).*
3. **Toggle com descrição explicativa abaixo**, e **campo à esquerda + explicação longa à direita** para o que exige texto — os dois formatos que o módulo inteiro pede.

### Padrões a adotar do que foi visto

- **Badge de estado no item do índice** (`configuração pendente`, `ambiente de testes`, `em breve` **com a citação legal**) — o índice diz o que falta, sem entrar em cada tela.
- **Erro com causa e ação**, e mensagem técnica em **"detalhes técnicos" recolhível** — nunca crua no meio da tela.
- **Contador de limite visível** e **estado vazio com cor por causa** (âmbar = filtro não achou; azul = nada cadastrado).
- **Ação destrutiva sempre em vermelho** — o Olist oscila; nós não.

### Um conflito a resolver antes — ✅ resolvido logo abaixo (opção B)

**"Número de registros por página" (global) × o nosso dropdown 10/25/50/100 em toda listagem.** São duas fontes de verdade para o mesmo número. Proposta: **o global é o padrão de abertura; o dropdown da tela sobrepõe enquanto durar a sessão.**

**Estrutura aprovada pelo usuário em 18/set/2026**, com a instrução de seguir **o máximo do padrão Olist possível**, construir **tela por tela**, e migrar para dentro de Configurações qualquer módulo já criado que pertença ali.

### Decisões fechadas junto com a aprovação

- **Paginação (opção B):** o parâmetro global em *Interface do usuário* é o **padrão de abertura** de toda listagem; o dropdown 10/25/50/100 do rodapé **sobrepõe enquanto durar a sessão** e some ao sair. É a única das três alternativas em que o global sempre faz o que promete — na A ele manda a um custo alto (tira o dropdown de 20 telas), e na C ele vira decorativo (mudar o global não afeta telas já ajustadas).
- **Badge de estado é derivado, não digitado.** Ver design-system §14.

### Construído

**Hub — `pagina-configuracoes.html`** ✅ 18/set/2026. Índice com busca e as nove abas, banner de contexto por aba, badge derivado, e navegação real para as telas que já existem. O flyout de **Configurações deixou de listar páginas** nos 39 arquivos: agora tem o atalho **"Configurações ERP"** mais o bloco Preferências (tema). Junto veio uma mudança genérica no bloco de sidebar compartilhado — **`flyout-item` com `data-href` passa a navegar** —, aplicada nos 39 arquivos; é o que abre caminho para ligar o menu às telas daqui em diante.

### Duas decisões tomadas depois do hub pronto (18/set/2026)

- **Atalhos para cadastros saíram do hub.** A régua é a **frequência de uso**: cadastro que se mexe no dia a dia (Marcas, Categorias, Departamentos, Seções, Embalagens, Depósitos, Endereços, Metas, Vendedores) pertence ao **módulo**; o que se define uma vez e não se revisita pertence ao **hub**. O usuário resumiu assim: *"os módulos que de fato vamos ter que configurar diariamente seguem no painel principal; os mais comuns e raros de alteração seguem no hub"*. Ver design-system §12.
- **Guia de primeiros passos: desenho fechado, construção adiada, nasce desligado.** Item próprio em *Configurações → geral*; caixa de seleção no **cadastro de usuário** para ligá-lo por usuário novo; desligável a qualquer momento. Ver design-system §13.

### Parâmetros de estoque — o que a construção ensinou (18/set/2026)

- **Tela de parâmetro sem refactor é decoração.** O valor da tela não está no formulário, está nos **7 números cravados** que ela substituiu. Antes de desenhar qualquer tela de configuração, a primeira pergunta é *quem lê esse número hoje* — se a resposta for "um `if` dentro de outra tela", o refactor faz parte da entrega, não é trabalho de depois.
- **Contrato com o Lovable:** cada bloco `PARAM` leva comentário dizendo que, no banco, aquilo é leitura da tabela `parametros` por chave. As chaves desta tela: `conferenciaCompraAlerta` (1), `conferenciaCompraCritico` (3), `enderecamentoAlerta` (2), `enderecamentoCritico` (7), `estoqueZeroLimite` (7).
- **Prévia viva como forma de explicar parâmetro.** Em vez de texto dizendo o que o número faz, a tela mede o efeito na fila de hoje e mostra quantos itens mudariam de cor. É o mesmo princípio do diagrama dinâmico de Embalagens: mostrar a consequência, não descrevê-la.
- **Regra que vale para as próximas telas do hub:** parâmetro que forma par (alerta/crítico, mínimo/máximo) valida a ordem no salvar, com modal dizendo **qual** par está invertido — não um "valores inválidos" genérico.

### Interface do usuário — três decisões que valem para todo o resto (18/set/2026)

- **`parametros` tem `usuario_id` anulável.** Nulo = valor da **empresa** (prazos, regras de estoque); preenchido = preferência **daquele usuário** (paginação, ao salvar, tema). É a diferença entre *Parâmetros de estoque* e *Interface do usuário*, e ela decide onde cada configuração futura vai morar. Toda tela nova do hub responde primeiro a esta pergunta: isso é da empresa ou de quem está logado?
- **O protótipo passou a ter uma tabela `parametros` de verdade.** Como cada tela é um arquivo solto, a configuração era gravada e nenhuma outra tela lia — a tela de configuração era uma maquete. Agora o bloco compartilhado guarda o mesmo JSON no navegador (`deskParametros`), com `try/catch` caindo no padrão de fábrica se o navegador bloquear. **No Lovable isso é `SELECT` na tabela `parametros`; aqui é a única forma de validar a configuração de ponta a ponta** — e foi validando assim que se descobriu que a prévia media uma fila inventada. Vale para todas as telas do hub daqui em diante: **configuração que não se prova mexendo em outra tela não está pronta.**
- **Vocabulário do global tem de bater com o do controle local.** O Olist oferece 20/50 no global e outro conjunto no rodapé. Nós usamos **10/25/50/100 nos dois**, senão o usuário escolhe um padrão que nenhuma listagem consegue mostrar. Regra geral: **parâmetro global e controle da tela falam a mesma lista de valores.**

### Exclusão passa a exigir senha — decisão de 18/set/2026

O usuário decidiu que **excluir cadastro exige senha**, configurável **por módulo** (não uma chave genérica), porque o perfil precisa poder liberar *excluir cliente* e travar *excluir produto*. As 14 exclusões reais entraram no catálogo `ACOES_SENHA` **nascendo ligadas**.

**As três camadas que protegem um cadastro — e a senha é a mais fraca delas.** Registrado aqui para não se confundir depois:

1. **Integridade referencial** — impedir excluir o que já tem movimento (produto com venda, fornecedor com nota). É a que protege o histórico de verdade, e só fica real com FK no Supabase. Continua pendente. ⏸ *espera o Supabase.*
2. **Exclusão suave** — hoje existe em **2 dos 14** pontos: `Depósitos` e `Vendedores` (campo `excluido`, aba "Excluídos", registro preservado). Nos outros 12, excluir apaga de vez. **A barganha da exclusão suave nos 12 restantes ainda não foi feita** — é mudança de modelo de dados, não cabe de rabo de olho.
3. **Senha** — confirma *quem é você*. Construída em 18/set/2026.

**A senha sozinha dá sensação de proteção que ela não entrega:** excluir com senha, nos 12 pontos sem exclusão suave, continua sendo apagar de vez — só que com identidade confirmada. Fazer a 2 e a 3 sem a 1 seria proteger a porta e deixar a parede aberta.

**Como acrescentar uma ação nova ao catálogo** (a pergunta do usuário que originou tudo isto): duas linhas. Uma no catálogo (`chave`, `nome`, `onde`, `modulo`, `pronto`, `exigePadrao`) e uma na tela que executa a ação — `armarSenhaModal('chave')` antes do modal, ou `aplicarExigenciaSenha('chave')` + `exigeSenha('chave')` nos painéis de confirmação com drawer. **Não existe passo 3:** a ação aparece sozinha em Configurações e no checklist do perfil. No Lovable, `acoes_confirmacao` nasce por *migration* junto com a tela — **quem cadastra ação é quem constrói a ação**, nunca o usuário final, senão a linha existe e nenhum código a lê.

### Barganha fechada — confirmações e permissões viram MATRIZ (18/set/2026)

O usuário perguntou como criar travas de senha novas no futuro. A barganha foi feita antes de qualquer código. **Decisão: opção B — matriz módulo × verbo.**

**A forma.** O catálogo chapado (19 ações hoje; estimativa de 60+ com o sistema inteiro — estimativa, não medição) vira uma **grade**: linha = módulo, colunas = **criar · editar · excluir**, mais as **ações específicas** de cada módulo, que continuam como itens próprios (fechar inventário, confirmar recebimento de transferência, cancelar OC já recebida, criar/alterar senha de vendedor). Os três verbos entram completos, por decisão do usuário.

**A ideia central, que é a resposta à pergunta dele:** *não se cria trava depois — liga-se uma que já veio com a tela.* Cada tela, ao ser construída, **declara quais verbos ela tem**, e as células aparecem sozinhas em Configurações no mesmo dia em que o módulo nasce. Quando Finanças existir, as travas de Finanças já estarão lá. Ninguém precisa pedir build para proteger algo novo.

**Permissões de Usuários é o MESMO eixo e o mesmo módulo.** Duas perguntas sobre a mesma célula: *a ação exige senha?* (da empresa) e *este perfil pode executá-la?* (do perfil). Isso foi decidido **antes** de Permissões existir, de propósito: se ficasse para depois, uma das duas telas teria de ser refeita, e refazer Permissões é caro. O checklist do perfil em Vendedores passa a ser a mesma grade com outra coluna.

**Opção C descartada — e por quê.** Regras condicionais criadas pelo usuário (*"exigir senha quando o desconto passar de 10%"*) só valem se a tela souber avaliar aquele campo, ou seja, continuam dependendo de código. A diferença é que a regra *parece* criada e pode simplesmente não valer, sem avisar — trava que dá sensação de segurança e não trava nada. Limiar por valor entra **declarado em código, ponto a ponto**, quando Vendas existir e se souber qual campo compara com qual valor. Cobre também o *código de liberação de desconto* visto nos prints, que é mecanismo à parte (senha diz *quem é você*; o código libera *uma exceção pontual*).

**Consequência técnica a executar.** `ACOES_SENHA` ganha eixo `(modulo, verbo)` ao lado das chaves específicas; `exigeSenha()` passa a aceitar as duas formas. No Lovable: `acoes_confirmacao(modulo, verbo|chave)` e `permissoes(perfil, modulo, verbo|chave)` — mesma chave lógica nas duas tabelas.

~~Ponto em aberto, a confirmar na retomada:~~ → ✅ **Resolvido em 21/set (item 1): criar e editar nascem desligados.** O texto original: o **estado inicial de criar e editar**. *Excluir* nasce ligado (decidido em 18/set). Minha recomendação é que **criar e editar nasçam desligados** — exigir senha para editar um cadastro é atrito diário pesado —, com a célula existindo desde o primeiro dia para ser ligada quando quiser. O usuário aprovou "criar/editar e excluir" completos, mas isso responde *quais colunas existem*, não *como nascem*; por isso fica registrado como pergunta, não como decisão tomada.

### Onde paramos — retomada de 22/set/2026 (segunda)

**Construído nesta semana:** hub de Configurações · Parâmetros de estoque · Interface do usuário · Confirmações por senha · exclusão exigindo senha nos 24 pontos reais do sistema. Junto veio a infraestrutura que faltava: o bloco compartilhado de `PARAM` nos 40 arquivos (com persistência no protótipo), o catálogo `ACOES_SENHA` e o envelope de senha no modal de confirmação.

**Primeira decisão da retomada: a matriz vem ANTES de seguir a ordem das telas.** Cada tela nova que nascer no formato de lista chapada vira retrabalho quando a matriz entrar — e retrabalho é exatamente o que este canal existe para evitar. Depois dela, retomar a ordem em **4. Configurações de estoque e da conferência**.

**Fila depois disso:** 5. Cadastro de clientes e de produtos (casas decimais) · Caixa, Contas a Pagar e Contas a Receber (F5) · Transportadora Desk Flash (última de F2). E as duas camadas de proteção que a senha **não** cobre continuam pendentes: **integridade referencial** (só real com FK no Supabase) e **exclusão suave nos 12 pontos que não têm** (hoje só Depósitos e Vendedores têm) — essa segunda precisa de barganha própria, é mudança de modelo de dados.

## Decisões de 21/set/2026 — rodada de desbloqueio

### 1. Matriz de senha: *criar* e *editar* nascem DESLIGADOS

*Excluir* nasce ligado (18/set). **Criar e editar nascem desligados**, com a célula existindo desde o primeiro dia. A grade mostra **só os módulos que já têm tela**, mais as ações específicas travadas — grade com 9 linhas vazias promete o que não existe. Decisão do usuário; fecha o último ponto da barganha da matriz.

### 2. Cliente e Fornecedor seguem SEPARADOS — a tabela `pessoas` está descartada

**Decisão do usuário:** *"não temos planos de vender para nossos fornecedores, até porque vamos apenas comprar"*. Some o único custo real de não unificar (compensar conta a pagar contra conta a receber da mesma pessoa). **`pessoas` por CPF/CNPJ não será construída.** Se um dia a Desk vender a um fornecedor, o problema volta — e a saída continua sendo a tabela-faceta, que fica aqui registrada como caminho, não como pendência.

### 3. Conta financeira × conta bancária — CONFIRMADO na documentação do Olist

A hipótese registrada em §12/§13 estava certa, agora com fonte (`ajuda.olist.com`):

- **Conta financeira é o guarda-chuva.** A doc diz que elas *"ajudam a organizar as movimentações da empresa, **incluindo suas contas bancárias**"*. **Caixa já vem pré-cadastrada.** O cadastro é mínimo: **"Nome da conta"** mais a caixa **"Não considerar esta conta no saldo para fluxo de caixa"**.
- **Conta bancária é o subtipo com dados bancários** — e é ela que precisa existir para importar extrato (`Finanças > Contas bancárias`).
- **O saldo e o lançamento vivem na conta financeira.** A tela de Caixa filtra pela seleção lateral **entre contas financeiras e contas bancárias**, e o lançamento guarda *Categoria, Tipo, Data, Valor, Histórico e Cliente ou Fornecedor*, mais abas de **competência**, anexos e marcadores.
- **Duas travas de integridade que a doc entrega de graça:** conta financeira **não pode ser excluída** se estiver vinculada a uma bancária, e **o saldo precisa estar zerado** para inativar.

**Consequência para nós:** `contas_financeiras` é o cadastro que abre Finanças (nome + flag de fluxo de caixa + tipo), e `contas_bancarias` é uma **extensão** dela com banco/agência/conta. O saldo do Caixa é **por conta financeira**. A ordem do §12 continua válida com essa correção de nome: **Contas Financeiras → Contas Bancárias → Categorias Financeiras → Caixa → Contas a Pagar → Contas a Receber**.

### 4. Conciliação — campos agora, tela depois

A doc do Olist (`gestao-financeira/extratos-bancarios`) mostra o fluxo inteiro: importa **.ofx**, o sistema faz o **casamento automático por valor + contato vinculado**, e cada linha oferece **"Incluir este lançamento"**, **"Ignorar / já foi lançado"**, **"Lançar e receber conta correspondente (crédito)"** / **"Lançar e pagar conta correspondente (débito)"** e **"Conciliar lançamento"** (busca por data, descrição ou nome). **Quando o valor não bate, aparecem campos de taxa, juros, desconto e acréscimo**, e o pagamento parcial marca a conta como **"paga parcialmente"**.

**Duas leituras que mudam o nosso schema agora:**

1. **Os campos de divergência da conciliação são os mesmos do §11** (`valor_taxas`, e agora também juros/desconto/acréscimo). O modelo de `baixas` N:N já cobre baixa parcial — a conciliação é só mais uma origem de baixa, não um módulo paralelo.
2. **O lançamento precisa nascer com `origem` (manual / ofx / gateway), `id_externo` (o FITID da linha do OFX) e `conciliado_em`.** São três campos baratos hoje e **impossíveis de retroagir**: sem `id_externo`, reimportar o mesmo extrato duplica lançamento, e ninguém descobre até o saldo divergir. **Decisão: os campos entram agora; a tela de conciliação fica para depois da F5.**

### 5. Kit tem as DUAS formas — montado e virtual

**Decisão do usuário.** O kit passa a ter `tipo_kit`:

- **Montado** — alguém monta a caixa e guarda. **Tem saldo próprio por endereço**, é conferido, endereçado e inventariado como qualquer produto. É o que o nosso mock já faz hoje.
- **Virtual (derivado)** — o kit é uma **receita**, não existe fisicamente. **Não tem saldo**: o disponível é `min(piso(saldo_componente ÷ qtd_no_kit))` entre os componentes. Vender baixa **os componentes**, nunca o kit.

São os casos que o usuário descreveu: *3 blusas do mesmo modelo formam um kit com desconto* (componente é a mesma SKU × 3), *bermuda + blusa X vira kit com preço próprio* (Desk Brands), *fone + smartwatch forma o kit Z* (raro, Desk Shope). O cadastro do kit **lista os produtos que podem compô-lo e a quantidade de cada**, e o kit **só é oferecido se todos os componentes tiverem saldo**.

**Três consequências que precisam estar escritas antes de qualquer tela:**

- **Preço do kit é próprio, não é a soma.** É o motivo de o kit existir — o desconto automático. O cadastro guarda preço ou regra de desconto.
- **Kit virtual não entra em Inventário nem em Acerto.** Contar um kit virtual é contar duas vezes o mesmo saldo. **Hoje o nosso Inventário e o Acerto tratam kit como produto comum** — isso vale só para o montado, e vira bug no dia em que o virtual existir. Fica registrado como correção obrigatória junto com a construção do kit.
- **Montar e desmontar é um evento de estoque**, não um cadastro: consome componentes e cria saldo de kit montado (e o inverso). É um acerto especializado no ledger, com as duas pernas no mesmo documento — mesma família da transferência.
- O toggle *"substituir kits pelos componentes na separação"* visto nos prints deixa de ser preferência: é **obrigatório** para kit virtual e **opcional** para kit montado.
- **Inventário olha SÓ para kit de estoque próprio** *(confirmado pelo usuário em 21/set/2026)*. Kit derivado não é contado como item: seus componentes já entram na contagem individual. A escolha é feita **no cadastro do kit** — *estoque próprio* segue com os campos normais de produto; *derivado* passa a exigir **quais produtos o compõem e em que quantidade**.
- **O preço do kit derivado é resolvido no carrinho, ao vivo.** A vitrine consulta o ERP, o ERP reconhece que aquele conjunto de peças **fecha o formato de um kit cadastrado** e devolve o **valor atualizado do kit** no lugar da soma dos itens. Isso tem duas consequências: (a) o kit derivado é, na prática, uma **regra de preço reconhecida por composição** — e não um produto vendável isolado; (b) **a vitrine nunca calcula preço de kit por conta própria**, senão os dois lados divergem no dia em que o valor mudar. Uma fonte, consultada no momento da venda.

### 6. Registro de atividades (log) — aprovado, e é mais importante que a exclusão suave

**Pedido do usuário:** um lugar que mostre o que foi excluído, por quem, com data e hora, visível só a supervisor / gerente / owner.

**Decisão: construir como LOG DE AUDITORIA, não como "log de exclusões".** O mecanismo é idêntico e o escopo maior custa o mesmo: **toda ação do catálogo `ACOES_SENHA` grava no log** — quem, o quê, quando, em qual registro. Isso dá sentido definitivo ao catálogo: ele deixa de ser "a lista do que pede senha" e vira **a lista do que é auditável**, com a senha sendo uma das colunas da matriz.

- **Onde mora:** `Configurações → geral → Registro de atividades`. É consulta rara e de público administrativo — pela régua da frequência de uso (§12 do design-system), pertence ao hub.
- **Quem vê:** célula própria na matriz de permissões. O log não é aberto a todo mundo, e essa restrição é ela mesma uma permissão.
- **Relação com exclusão suave:** são complementares e resolvem coisas diferentes — **o log diz o que aconteceu; a exclusão suave permite desfazer**. O log é mais barato, é universal e não mexe no modelo de dados. **Com o log no ar, a urgência da exclusão suave cai muito**, e ela passa a valer a pena só onde desfazer importa de verdade (cadastro com movimento). A barganha da exclusão suave continua aberta, mas deixa de ser bloqueio.
- **Em aberto para depois:** retenção (por quanto tempo o log guarda) e expurgo. No protótipo é infinito; no Supabase é tabela que cresce sozinha.

### 7. Central de ajuda e o "agente tipo Lis" — pesquisado, com proposta

O usuário levantou a ideia de, no fim do projeto, ter um sistema que ensine a usar o ERP passo a passo, *"e até uma IA pra responder as perguntas, igual a Lis, do Olist"*. **O que a Lis é de fato**, pela documentação e pelo material da própria Olist: uma **plataforma de agentes de IA** com interface de chat em menu próprio do ERP, onde **Lis é o agente supervisor** que orquestra agentes especializados. Eles **respondem dúvidas de uso E executam ações** (estoque, pedidos, categorização, relatórios), com **cobrança por créditos** por tarefa, escolha de modelo (ChatGPT, Gemini) e status **beta**, com meta declarada de 90% de execução sem erro.

**Proposta: separar o que o Olist juntou.** São dois produtos com custo e risco muito diferentes.

1. **Ajuda e treinamento (fazer desde já, de graça).** Não precisa de IA e não pode virar manual paralelo — manual escrito à mão mente em três meses. **A ajuda nasce com a tela**, exatamente como a trava de senha: cada tela declara seu texto de ajuda e seus passos, e a central de ajuda monta a página sozinha. Os ganchos já existem e estão construídos: o **ícone `?` do hub**, os **textos de explicação ao lado de cada campo** (layout GNRE) e o **Guia de primeiros passos** (decidido, nasce desligado). Falta só juntar num lugar consultável.
2. **Agente conversacional (depois do ERP no ar).** Escopo inicial **somente leitura**: responde "como faço X" e pergunta sobre os dados. Executar ação só numa segunda fase — e aqui está a amarração que torna isso viável: **o agente entra pelo mesmo portão que um usuário**, a matriz de permissões e as confirmações por senha. Um agente que executa sem passar por esse portão é um usuário sem perfil, e aí não há auditoria possível. **O log do item 6 é o que torna o agente auditável.**

**Leitura estratégica, registrada de propósito:** os três itens desta rodada — matriz de permissões, log de auditoria e agente — são **a mesma infraestrutura vista de três ângulos**. Construir a matriz e o log agora não é desvio do roadmap: é o que faz o agente ser possível depois sem refazer nada.

### Matriz construída — 21/set/2026

`MODULOS_SENHA` (14 módulos) × `VERBOS_SENHA` (criar · editar · excluir) + `ACOES_ESPECIFICAS` (5) = **47 células**, e `ACOES_SENHA` virou array **derivado** — quem já lia não mudou.

- **`ligado` é o campo que sustenta a honestidade da grade.** Diz se a tela daquele módulo já chama a verificação naquele verbo. Hoje: `excluir` ligado nos 14, `criar`/`editar` só em **Marcas** (piloto). Os outros 26 pares aparecem com cadeado — **e essa é a lista de trabalho**: cada módulo liga os dois verbos quando a tela for revisitada, que é a regra "a trava nasce com a tela" aplicada a tela que já existia.
- **Por que não liguei os 14 de uma vez:** só 4 das 12 telas de cadastro compartilham a mesma forma de handler de salvar; as outras divergem. Transformação mecânica em cima de forma divergente é como se quebra tela validada. O piloto prova o padrão; a extensão é por tela, com teste.
- **`confirmarAcao(chave, texto, executar)`** é o helper novo: executa direto quando a trava está desligada, e quando ligada abre o modal com senha, gravando só dentro do callback. Despacha as três assinaturas de `abrirModalConfirmacao` por `.length`.
- **Próximo passo natural:** o **Registro de atividades (log)**, que já está decidido e é o que fecha o tripé matriz + log + agente.

### Help Desk / Atendimento ao cliente ("Desk Help") — LACUNA confirmada (21/set/2026)

**Nome provisório dado pelo usuário: "Desk Help"** — o SAC da Desk, para resolver trocas, devoluções, reclamações e dúvidas. Desenho fica para depois de Pedidos; a conversa de escopo foi adiada por ele mesmo.

O usuário perguntou se o projeto tem um módulo onde **o cliente abre reclamação, dúvida ou pedido de devolução**. **Não tem, e nunca foi discutido** — varri os dois documentos e o menu dos 9 módulos. O que existe é adjacente, e nenhum dos três é isso:

- **Logística → Devolução** e **Operacional → Motivos de Devolução**: a **execução** da devolução (mercadoria voltando) e o cadastro de motivos. A **solicitação** não tem porta de entrada.
- **Central de Suporte** (rodapé das 42 telas): é o suporte **do ERP para o operador**, não do cliente para a Desk. Sentido oposto.
- **Vendas → CRM** (no menu, não construído): é **pré-venda**, funil. Atendimento é pós-venda.

**O Olist também não tem.** A doc (`ajuda.olist.com/pedidos/devolucoes-de-vendas`) é explícita: a devolução nasce **do pedido**, em `Vendas > Pedidos de Venda > Devolver produtos`, com *"Sem pagamento / Dinheiro / Vale-troca / Contas a pagar"* e *"Forma de envio (reversa)"*, passando por *Em andamento* → *Finalizada* na autorização da SEFAZ. **Não existe ocorrência nem ticket** para iniciar o processo. Ou seja: aqui **não há print para copiar** — é desenho nosso, a partir da operação da Desk.

**Três amarrações que precisam estar certas antes de qualquer tela:**

1. **O módulo tem duas faces.** A do cliente vive **fora do ERP** (vitrine, e-mail, WhatsApp, mensagem de marketplace); a nossa é **a fila** dentro dele. Confundir as duas é o erro clássico — o ERP não é o site.
2. **Quase todo chamado é sobre um pedido, e `orders` não existe** (F3/F4). Help Desk construído agora seria fila de chamados presos a nada. **Desenhar agora, construir depois de Pedidos.**
3. **A devolução passa a ter duas origens.** Hoje ela nasceria só do pedido, como no Olist. Com Help Desk, nasce também de um chamado aprovado. **Decisão registrada agora, barata agora e cara depois:** a Devolução em Logística nasce com o campo `origem` (`pedido` | `chamado`) e `chamado_id` anulável, mesmo antes do Help Desk existir — é a mesma jogada do `empresa_id` do item 22 e do `loja_id` do §12. **Uma devolução, duas portas — nunca duas telas de devolução.**

**Onde ficaria no menu:** proposta é **Vendas → Atendimento**, ou módulo próprio se a operação de SAC tiver gente dedicada. Não precisa decidir agora; precisa só não construir Devolução sem o campo `origem`.

### Registro de atividades construído — 21/set/2026

`Configurações → geral → Registro de atividades`. Fecha o segundo pé do tripé **matriz + log + agente**.

- **Nenhuma das 41 telas precisou mudar.** A gravação entrou nos dois pontos por onde toda ação do catálogo já passava: `confirmarAcao` (caminho sem senha) e a fase de captura do Confirmar do modal (caminho com senha). **Ação nova passa a ser auditada só por entrar no catálogo** — é o mesmo ganho da matriz, aplicado ao log.
- **O catálogo mudou de sentido.** Deixou de ser "a lista do que pede senha" e virou **a lista do que é auditável**; a senha virou uma coluna do registro.
- **Contrato com o Lovable escrito no código:** `log_atividades` é gravada **no servidor**. Log escrito pelo cliente é log que o próprio usuário apaga depois de agir. No protótipo grava no navegador (últimas 300) só para a tela poder ser avaliada de verdade.
- **Nada foi semeado de exemplo** — a tela abre vazia e explica o que fazer para vê-la funcionando. Registro com evento fabricado é registro que mente.

**Descoberta que muda Permissões de Usuários, e vale registrar antes de construí-la:** a matriz de **permissão** tem um verbo que a matriz de **senha** não tem — **ver**. Ninguém confirma "visualizar" com senha, mas *quem pode ver* é exatamente a pergunta do Registro de atividades (supervisor/gerente/owner) e de qualquer relatório. Então as duas grades compartilham módulos e linhas, mas **a de permissão tem uma coluna a mais**. Desenhar assim desde o começo evita descobrir isso depois de a tela estar pronta.

## Finanças — módulo aberto em 21/set/2026

### Decisões tomadas antes da primeira tela

- **`Tipo = Saldo` lança a diferença**, não carimba o valor. O histórico fica com o movimento real (*"ajuste de −R$ 240,00"*) em vez de um número que apaga o rastro. Mesma escolha do acerto de estoque.
- **Contas a Pagar e Contas a Receber são DUAS telas**, não uma com seletor. Os títulos compartilham a tabela (`natureza` pagar/receber), mas a operação é outra: quem paga olha vencimento e fornecedor; quem recebe olha cliente, antecipação e taxa. Uma tela só vira um monte de `if` escondendo coluna — que é como uma tela boa vira duas ruins.

### Contas financeiras ✅ construída — o que os prints ensinaram

Os prints de 21/set fecharam a última lacuna de referência do módulo. O que eles confirmaram e o que acrescentaram:

- **Confirmado:** o cadastro é enxuto — **Nome da conta** e a caixa *"Não considerar esta conta no saldo para fluxo de caixa **e no saldo inicial do caixa**"* (o print traz a frase completa, mais longa que a da documentação). Nenhum campo de banco, o que fecha a questão: **`contas_bancarias` é extensão de `contas_financeiras`**.
- **Novo:** **"Número da conta na contabilidade"** — o código no plano de contas, que nem a doc nem a hipótese previam. Lá ele é preenchido num **drawer à parte**, acionado por *"informar número da conta"* no menu da linha. A leitura por trás disso é boa e vale registrar: **quem cria a conta não é quem sabe o número contábil** — ele chega depois, pela contabilidade. Aqui virou uma **seção do mesmo drawer**, com o hint dizendo isso.
- **Novo:** **"preferencial para movimentações"** — uma conta vem escolhida por padrão em todo lançamento novo. É exclusiva: marcar uma desmarca a outra, **na hora**, não na tela seguinte. Duas preferenciais é o mesmo que nenhuma.
- **Confirmado pelo cadeado na linha do Caixa:** a conta Caixa **nasce com a empresa** e não pode ser removida.
- **Ruído do Olist corrigido:** o subtítulo deles diz que as contas financeiras servem *"para classificar as receitas e despesas"* — isso é o papel da **categoria**. A conta diz **onde** o dinheiro está; a categoria diz **o que** foi. Nosso subtítulo diz isso.

**O que a tela prova além dela mesma:** é o primeiro módulo criado depois da matriz de senha e do registro de atividades, e nasceu com os três verbos ligados. Criar e excluir uma conta **já aparecem no Registro de atividades sem uma linha de código de log na tela** — a infraestrutura das duas semanas anteriores pagou o primeiro dividendo.

### Contas bancárias ✅ construída — e a doc mudou o desenho

O print mostrava **Banco** e **Descrição da conta**. A documentação (`configuracoes-financeiras/contas-bancarias`) acrescentou o que faltava: **chave Pix com tipo** (e-mail · CPF · CNPJ · telefone · aleatória) e o **propósito da conta** — *"emitir boletos"* e *"enviar remessas e ler retornos dos principais bancos"*, ou seja **CNAB**. Também registrou que, lá, boleto exige a extensão *Cobranças Bancárias*.

- **Conta bancária não tem saldo.** É a ficha de dados de uma conta financeira. Dito no topo da tela e na nota do painel.
- **Vínculo 1:1, imposto pela interface:** o seletor só oferece contas financeiras **sem bancária**. Duas bancárias na mesma financeira fariam o saldo perder o dono.
- **O que fica para Contas a Receber:** boleto, remessa e retorno CNAB. Os campos de convênio e carteira nascem com o módulo que os lê — não agora.

**Próximas do módulo:** ~~Categorias Financeiras~~ ✅ → ~~Caixa~~ ✅ → **Contas a Pagar** → **Contas a Receber**.

### Ordem de construção das telas

1. ~~**Parâmetros de estoque**~~ ✅ **construída em 18/set/2026** — `pagina-configuracoes-parametros-estoque.html`. Os três limiares saíram do código: as telas de Endereçamento e Conferência de compra agora leem um bloco `PARAM` nomeado (7 números literais substituídos), e a tela de configuração escreve nele. Ver design-system §12 e §14.
2. ~~**Interface do usuário**~~ ✅ **construída em 18/set/2026** — `pagina-configuracoes-interface-usuario.html`. A regra B da paginação virou código nas 17 listagens; o tema passou a ser preferência gravada; o "ao salvar" saiu de dentro das 5 telas de detalhe. Ver design-system §12.
3. ~~**Confirmações por senha**~~ ✅ **construída em 18/set/2026** — `pagina-configuracoes-confirmacoes-senha.html`. O inventário virou **catálogo em código** (`ACOES_SENHA`), lido pela tela de configuração, pelas quatro telas que pedem senha e pelo checklist do perfil. Ver design-system §12.
4. ~~**Configurações da conferência**~~ ✅ **construída em 21/set/2026** — `pagina-configuracoes-conferencia.html`. Cobre a conferência e a conferência de compra numa tela só. **Configurações de estoque NÃO foi construída, por decisão minha registrada:** levantei os leitores e ela não tem nenhum hoje. *Permitir estoque negativo* e *lançamento para saídas* só fazem sentido quando existir venda — nossa única saída hoje é o Acerto, onde tirar mais do que existe é erro de dado, não política. E *"desconsiderar saldo deste depósito"*, que a gente precisa de verdade (a regra do depósito de Trânsito está cravada em `depsSelecionaveis` de duas telas), **é campo do cadastro de Depósito**, não parâmetro global. A tela entra com Vendas; o campo entra quando Depósitos for revisitado.
5. ~~**Configurações do cadastro de clientes e de produtos**~~ ✅ **construídas em 21/set/2026**. As casas decimais saíram de 14 arquivos, com **quantidade e dinheiro separados** (`fmtQtdNum` × `fmtNum`) — o erro fácil aqui seria um parâmetro só mexendo nos dois. Em Clientes, a **checagem de CPF/CNPJ duplicado foi construída junto com o parâmetro**: ela não existia, e parâmetro sem leitor é enfeite. Ver design-system §12.

**Com isso a fila de telas de configuração com leitor acabou.** Sobrou o que espera módulo: *Configurações de estoque* (Vendas), *Usuários do sistema* e *Permissões de usuários* (login), *Guia de primeiros passos* (decidido, nasce desligado), e as abas de finanças, fiscal e integrações. **O próximo passo natural é voltar aos módulos** — Finanças abre com Contas Financeiras, conforme §12 corrigido em 21/set.
6. Finanças, quando o módulo entrar; fiscal e integrações, por último.


### Categorias financeiras ✅ construída — 21/set/2026

`pagina-configuracoes-categorias-financeiras.html`. Consultei a documentação antes de desenhar (`ajuda.olist.com/configuracoes-financeiras/categorias-de-receitas-e-despesas`), como combinado — e de novo ela mudou o desenho.

**O que a doc acrescentou ao print:**

- **Grupo é entidade própria**, com cadastro separado e **um campo só** (descrição). E o ponto que importa: *"ao excluir um grupo que possui categorias vinculadas, as categorias não serão apagadas, mas passarão a ser da classificação Sem grupo"*. Está implementado assim, e a confirmação diz quantas vão se mover.
- **Cada valor de *Considera no DRE* tem regra de sinal.** Deduções, despesas operacionais, tributos e taxas consideram **apenas lançamentos de saída**; *outras receitas ou despesas* considera os **dois sentidos** (entrada vira *Outras receitas*, saída vira *Outras despesas*). Isso virou **hint que muda com o valor escolhido** — sem ele, a escolha é chute e o erro só aparece no relatório, meses depois.
- **"Agrupar categorias"** existe lá como ação em massa, para mover várias de uma vez. Virou o menu **Mover para grupo** da barra de seleção.
- **Categoria pode ser padrão de uma operação** (venda, compra, PDV). PDV não existe no nosso projeto; ficaram **padrão de vendas** e **padrão de compras**, exclusivos na hora — marcar um desmarca o outro, mesma regra da conta preferencial.
- **Importar e exportar por planilha** (com o detalhe de que a atualização casa pela dupla *descrição + grupo*): registrado, não construído. Entra junto com o resto das importações.

**Três decisões minhas, com o motivo:**

1. **O nome é *Categorias financeiras*.** Lá a tela se chama *"Categorias de receitas e despesas"*, mas o campo em todas as outras telas deles é *"categoria financeira"* — inclusive *"categoria financeira padrão dos pedidos"*. Fiquei com o nome do campo, que é o que o usuário vê no dia a dia, e que ainda distingue de **Cadastros → Categorias**, que é de produto. O item do hub foi renomeado junto.
2. **Uma tela, duas visões.** A alternância `grupos ↔ categorias` do print virou duas abas na mesma tela. Grupo tem um campo; tela inteira para ele seria mais um arquivo para manter, mais um item no hub, e nada a mais na frente do usuário.
3. **Situação (ativa/inativa) e trava de exclusão por uso — divergência deliberada.** Lá não existe. Aqui existe porque **categoria citada em lançamento não pode sumir sem deixar histórico órfão**: quem tem uso não mostra o link de excluir, e a nota diz quantos lançamentos são e oferece *Inativar*; quem tem uso zero exclui de verdade. O mock tem uma categoria zerada de propósito — **trava que nunca deixa passar também é bug**.

**O CMV, que a doc não diz e o desenho precisava dizer:** *Não considera* é o valor certo para **compra de mercadoria para revenda**. O custo dela chega ao resultado pelo **CMV, na venda**; classificar a mesma saída também como despesa operacional conta duas vezes. Está escrito no hint da opção, com esse exemplo.

**Prova de infraestrutura, terceira vez:** a tela não tem uma linha de código de log. Criar, editar, **mover em massa** e excluir já aparecem no Registro de atividades — inclusive o movimento em massa, que **não pede senha** (editar nasce desligado) e mesmo assim fica registrado. Era exatamente isso que o log tinha de provar.

### Prints — Ordem de compra em uso (21/set/2026): o Olist DEPOIS que a ordem está salva

Dois lotes, e juntos eles valem mais que qualquer tela de configuração: mostram o que acontece **depois** de salvar uma ordem de compra — que é a parte que a gente ainda não desenhou.

**Lote A — consulta de CNPJ na Receita Federal (a função nova).**

- Dentro do **campo CNPJ do bloco do fornecedor**, na própria ordem de compra, existe **consultar na receita federal**. Abre um painel à direita com **CNPJ + UF** e o botão *consultar cadastro*.
- E o print devolve a informação mais importante: **"Atenção! O certificado digital ainda não foi configurado."** Ou seja, **não é API pública** — é a consulta de cadastro do SEFAZ/Receita, **assinada com o certificado A1/A3 da empresa**. **Consequência direta para nós: essa função não pode nascer antes da aba fiscal com o certificado.** Fica registrada como **dependência**, não como tela — e quando entrar, entra como botão dentro do campo CNPJ de Fornecedores e da Ordem de Compra, não como tela separada.
- Outros deltas do mesmo lote, contra a nossa Ordem de Compra: **bloco *Dados do fornecedor* inline** dentro da ordem (tipo de pessoa, CNPJ, contribuinte, IE, CEP, cidade, UF, endereço, telefone, celular, e-mail); **caixa de erro no topo** listando o que reprovou (*"Não foi possível salvar a ordem de compra · Verifique os campos destacados · CNPJ incorreto"*); **itens** com Cód (SKU), **GTIN/EAN** e **IPI %**; **totais** com nº de itens, soma das quantidades, total dos produtos, desconto, frete, **total do IPI**, **total do ICMS ST** e total geral; **pagamento** com *condição de pagamento* + botão **gerar parcelas** e a sintaxe do campo (*"30 60, 3x ou 15 +2x"*); drawer **Pesquisar cadastro** (código · nome · fantasia · CPF/CNPJ); e **EX** na lista de UF, para exterior.

**Lote B — o menu `⋯` da linha, e o que ele revela.**

Menu da ordem salva: *gerar nota fiscal · lançar contas · lançar estoque · clonar compra · receber parcialmente* | *excluir compra · compartilhar · imprimir · salvar em PDF · imprimir etiquetas · formação de preços · tags de produtos* | *alterar situação* (quatro cores) | *marcadores*.

1. **O menu muda com o estado — e essa é a melhor ideia do lote.** Depois de lançar o estoque, *lançar estoque* vira **estornar estoque**, aparece **gerenciar lotes e validades**, e *gerar nota fiscal* e *receber parcialmente* somem. **O menu não oferece o que não cabe mais, e oferece o desfazer do que foi feito.** Adotar na nossa Ordem de Compra, na Entrada de Notas e na Conferência — é a mesma família do cadeado da matriz e do badge derivado do hub: **o controle diz o estado real em vez de mentir**.
2. **"Lançar contas" sem parcelas dá aviso, não erro:** *"Não existem parcelas cadastradas! É necessário que você inclua parcelas para integrar o financeiro."* Isso **confirma a decisão 5 do §12** (documento gera título) **e acrescenta a pré-condição que faltava**: o título nasce das **parcelas** da ordem, não do total dela. Nossa Ordem de Compra não tem parcelas hoje — **entra na lista, junto com o botão *gerar parcelas* do lote A**. Sem isso, Contas a Pagar não tem de onde nascer.
3. **"Lançar estoque" tem o de-para de produto embutido.** No menu de cada item: *editar dados do produto · vincular a produto existente · cadastrar como produto novo · não lançar estoque*. É exatamente a tabela **`produto_fornecedor`** que registrei como pendência da Entrada de Notas — e o print mostra **onde** ela é preenchida: **no momento do lançamento, item a item**, com a opção de deixar um item de fora. A pendência deixa de ser hipótese minha e passa a ter desenho de referência.
4. **"Gerar nota fiscal" leva para *notas de entrada*** com *Tipo de entrada: emissão própria*, série, número, natureza da operação e data/hora de emissão e de entrada — e **dois avisos que valem ouro**: **"Você está no ambiente para testes de notas fiscais"** (homologação × produção, com botão *alterar ambiente*) e **"Não existe Operação Fiscal Padrão para compra cadastrada"** (um cadastro fiscal que a nota de entrada exige **antes**). **Dois itens novos para a aba fiscal**, e o primeiro deles é uma regra de segurança que a gente precisa copiar: **nota fiscal nasce em homologação e a troca para produção é explícita**.
5. **O estado aparece na listagem, não só no menu:** a linha ganha o badge **E** com tooltip *"Estoque lançado"*. Mesma família do badge de preenchimento visto na aba de notas fiscais.
6. **O Controle de estoques mostra a ORIGEM de cada movimento:** na coluna *Tipo*, badge **P 1** (pedido de compra nº 1), **V 1** (venda nº 1) e *Balanço*. Além disso a tela tem **aba reservas** e o KPI **disponível multiempresa**, ao lado de saldo físico, total reservado e total disponível. Nosso Controle de Estoques tem saldo e movimentos; **a coluna que aponta para o documento de origem é a que falta** — e ela é o que transforma a tela em rastro auditável.
7. **Detalhes menores, mas já mapeados:** abas com contador por situação (*todos · em aberto · em andamento · atendidas · canceladas* — já temos, §7.2 do design system), **totalizador no rodapé da listagem** (quantidade e valor total), **alterar situação por cor** e o guia fixo no topo (*"Etapa atual · 2 de 4 · acessar o guia"*) — que é o nosso **Guia de primeiros passos**, já decidido e nascendo desligado.

### Sobre testar sem cadastro real — e por que isso não atrapalha a revisão

O usuário levantou que não tem cadastros reais no Olist e que isso dificulta tirar informação precisa. Os prints do lote B respondem sozinhos: **o fornecedor se chama "Teste 1", o produto se chama "Teste 1", a ordem tem R$ 95,80 — e mesmo assim os prints ensinaram sete coisas que nenhuma tela de configuração ensinaria.**

A revisão completa que combinamos (ao fechar Finanças, antes de abrir Vendas) **não depende de dado real**: ela compara **fluxo com fluxo**, e para isso um cadastro de teste basta — aliás é melhor, porque deixa apertar qualquer botão sem medo. O que ela precisa é de **um ciclo inteiro percorrido uma vez**: ordem de compra → lançar estoque → gerar nota de entrada → lançar contas → baixar o título. Onde o Olist reclamar (*"não existem parcelas"*, *"não existe operação fiscal padrão"*), a reclamação **é o achado** — é ele dizendo qual pré-cadastro a gente esqueceu.

**Combinado prático:** nada de tentar preencher com dado fiel à realidade. Fornecedor "Teste", produto "Teste", valor qualquer — e print de cada aviso que aparecer. Aviso do sistema vale mais que tela preenchida certo.

### Pendências novas registradas hoje (21/set/2026) — *situação anotada em 29/set/2026*

- **Parcelas na Ordem de Compra** — campo *condição de pagamento* + botão *gerar parcelas* (sintaxe `30 60`, `3x`, `15 +2x`). **Pré-condição para Contas a Pagar nascer de uma ordem.** ✅ *construído — "Gerar parcelas" na Ordem de Compra.*
- **Consulta de CNPJ na Receita Federal** — **depende do certificado digital**; entra com a aba fiscal, como botão dentro do campo CNPJ (Fornecedores e Ordem de Compra), nunca como tela. ⏸ *espera certificado digital.*
- **Operação Fiscal Padrão para compra** — cadastro fiscal que a nota de entrada exige antes de ser gerada. ⏸ *espera o módulo fiscal (NF-e).*
- **Ambiente de homologação × produção para nota fiscal**, com troca explícita e faixa de aviso permanente. ⏸ *espera o módulo fiscal (NF-e).*
- **Menu de ações dependente do estado** (lançar ↔ estornar), na Ordem de Compra, Entrada de Notas e Conferência. ⏸ *espera o ledger de estoque real: estornar é desfazer movimento, e no protótipo o estoque não é compartilhado entre telas.*
- **Coluna de origem no Controle de Estoques** (badge do documento que gerou o movimento) + **aba reservas**. ⏸ *espera o ledger de estoque real (origem) e Pedidos de Venda (reservas). No Caixa a coluna Origem já existe.*
- **De-para `produto_fornecedor` no momento do lançamento de estoque** (vincular a existente · cadastrar novo · não lançar este item). ⏸ *espera a importação de XML, que roda no servidor.*
- **Totalizador no rodapé das listagens** (quantidade e valor total) — padrão a avaliar para as nossas. ✅ *adotado — Ordens de Compra, Caixa e Contas a Pagar.*

### Nota de processo — armadilha da ferramenta (21/set/2026)

Gravar na pasta do usuário a partir do **mesmo caminho intermediário** usado numa gravação anterior **reaproveita o conteúdo antigo**: as duas telas da matriz voltaram para o disco sem a alteração, com data nova e tamanho velho. **Só o tamanho do arquivo denunciou.** Regra daqui para frente: **conferir o tamanho listado depois de gravar**, e gravar sempre de um caminho novo quando o arquivo mudou no mesmo dia.


## Caixa — lote 2 de prints (22/set/2026): o módulo fechou

Vinte e um prints, agora **com dado real na tela** (três lançamentos, três contas, período fechado e um erro de verdade). Respondem as três perguntas que faltavam e trazem quatro coisas que eu não teria desenhado sozinho.

### O que a listagem mostra, com dado

- Colunas: **Data · Competência · Histórico · Cliente · Categoria · Entradas · Saídas · Marcadores · Origem** — todas ordenáveis. **Entrada e saída são DUAS colunas**, não um valor com sinal. E **existe a coluna `Origem`**, vazia nos lançamentos manuais: é ela que aponta para o documento que gerou o movimento — a mesma coluna que eu apontei como faltando no nosso Controle de Estoques. Aqui ela já existe, o que confirma que o padrão é do sistema, não da tela.
- **A primeira linha não é um lançamento: é o saldo de abertura** — faixa cinza fixa com *"saldo em 21/08/2026 · R$ 0,00"*. O período filtrado é *últimos 30 dias*, então a linha é o saldo em D-30. **A listagem é extrato, não lista.**
- **Rodapé fixo com cinco totais:** *saldo inicial · entradas · saídas · saldo final · N lançamentos*. **Saldo negativo aparece em vermelho** nos dois lugares (na pill da conta e no rodapé) — `-400,00` no print do primeiro estado.
- **A pill da conta mostra a conta selecionada com o saldo atual ao lado** — mesmo com três contas cadastradas (Caixa · Conta teste · Teste 3, vistas nos dropdowns de transferência), a barra exibe uma. **Não é uma pill por conta: é o seletor da conta do extrato.** Faz sentido: extrato é de uma conta.

### Seleção em massa — e um detalhe que vale copiar

- Barra inferior: **`↑ 02 de 100 Lançamentos ×`** · **alterar marcadores** (primário) · imprimir · **mais ações ⋯**. O `100` é o teto da operação em massa; a seta é *selecionar todos*.
- **O rodapé ganha uma coluna nova quando há seleção: `selecionados (R$) 200,00`.** Custa nada e responde a pergunta que a pessoa tem na cabeça (*"quanto dá o que eu marquei?"*) sem exportar nada. **Adotar.**
- `mais ações` da seleção: **alterar marcadores · alterar categoria · alterar conta financeira · imprimir recibos · excluir lançamentos · imprimir relatório · exportar lançamentos para planilha**.
- **Alterar marcadores em massa usa rádio *Incluir* / *Remover***, com a frase explicando cada um (*"os marcadores informados serão adicionados/removidos dos lançamentos"*). É melhor que um multi-seleção para operação em massa, porque o multi-seleção não distingue *acrescentar* de *substituir*.
- **Excluir em massa é um modal de rodapé** — *"Confirma exclusão dos lançamentos selecionados?"* com confirmar / cancelar ESC. Mesmo componente que o nosso.

### Alterar conta financeira — o achado silencioso

Existe nos dois níveis: no `⋯` da linha (*alterar conta*) e em massa (*alterar conta financeira*). O drawer traz **Conta atual** (somente leitura) e **Nova conta**.

**Isso não é um campo editável qualquer: mudar a conta de um lançamento move dinheiro entre dois saldos.** Dois extratos mudam de uma vez, e nenhum deles registra por quê. **Decisão nossa: `alterar conta` nasce como ação do catálogo auditável** (entra no Registro de atividades com a conta de origem e a de destino no detalhe), e não como edição solta de campo.

### Fechamento financeiro — a resposta que eu tinha pedido, e ela é melhor que o esperado

- **É uma data, não um período.** O drawer diz: *"O fechamento de período financeiro é recomendado para as empresas que fazem a conciliação financeira periodicamente e desejam bloquear lançamentos retroativos ao período de fechamento de caixa."* O campo é **Data de fechamento**, com o hint *"os lançamentos serão bloqueados até a data informada"*, e o botão é **fechar período financeiro**. Um campo só — `data_fechamento_financeiro` — resolve.
- **O estado aparece no rodapé da listagem**, como mais um bloco de totais: **`21/09/2026 · financeiro fechado`**. De novo o padrão do sistema: *o rodapé diz o estado real*, em vez de o usuário descobrir ao tentar salvar.
- **A trava é validação de campo, não bloqueio de tela.** A tela de lançamento abre normalmente; ao salvar numa data fechada vem a **caixa de erro no topo** — *"Não foi possível salvar o lançamento · Verifique os campos destacados. · Não é possível incluir o lançamento na data, pois o período financeiro está fechado."* — **com o campo Data contornado de vermelho**. Trocando para o dia seguinte (22/09), salva. Mesmo padrão de erro da ordem de compra: caixa no topo + campo marcado.
- **E o achado grande: `movimentações financeiras bloqueadas` é uma FILA.** O drawer diz: *"As movimentações financeiras automáticas abaixo não foram realizadas, devido ao fechamento do período financeiro."* Ou seja: quando uma baixa de título, um lançamento de ordem de compra ou uma comissão cai em período fechado, **o sistema não descarta em silêncio nem fura a trava — ele guarda o que deixou de fazer e mostra**. Sem isso, fechar o período faria movimento automático sumir sem rastro, e o saldo divergiria sem ninguém saber de onde.
  - **Consequência de schema, agora:** o movimento automático bloqueado é **registro próprio** (o que seria lançado, de qual documento, em que data, por que não entrou), não um erro de log. Nasce com o Caixa, não depois.

### O que os prints ensinaram sobre a tela de lançamento

- **O detalhe abre em modo LEITURA** (rótulo e valor, sem campo), com **editar** e **ações ⋯** no topo. `editar` transforma a mesma página em formulário, com salvar/cancelar no rodapé. É o padrão que já usamos nas telas de detalhe.
- **`ações` do lançamento:** *imprimir recibo · excluir registro · alterar conta · marcadores*.
- **`Adicionar nova categoria` está dentro do dropdown de Categoria** e abre o drawer **"Inclusão de nova categoria"** — com **Descrição · Grupo** e a seção **Demonstração do resultado do exercício** (*Considera no DRE* + *Competência padrão*, com os quatro valores: sem competência · mês do vencimento · mês anterior ao vencimento · mês da emissão). **É exatamente a tela que construímos ontem, chamada de dentro do Caixa.** Duas leituras: (1) o desenho do nosso drawer bate campo a campo com o deles, incluindo a seção de DRE; (2) **o Caixa precisa poder criar categoria sem sair da tela** — quem está lançando não vai a Configurações no meio do trabalho. Entra na construção.
- **`Tipo = Saldo` é guardado como tipo próprio no registro** — o print do lançamento salvo mostra *Tipo: Saldo · Valor: R$ 150,00*. O que o print **não** mostra é o efeito no extrato (em qual coluna ele entra). **Nossa decisão continua valendo e diverge:** aqui o tipo Saldo **lança a diferença** e o histórico guarda o movimento real (*"ajuste de −R$ 240,00"*), igual ao acerto de estoque. Registrado como divergência deliberada, não como desconhecimento.

### O que ficou de fora — e por que não bloqueia

1. **Em qual coluna um lançamento `Tipo = Saldo` aparece no extrato.** Não bloqueia porque a nossa regra é outra: ele vira um movimento de entrada ou de saída pela diferença, e é isso que o extrato mostra.
2. **O conteúdo do seletor de colunas e do drawer de filtros com dado.** Sei que filtros tem Categoria e que o período tem *por emissão* / *por competência*; o resto é escolha nossa.
3. **Importar extrato OFX.** Já decidido em 21/set: campos de conciliação agora, tela depois.

**Com isso o Caixa está fechado para construção**, e ele entra com duas telas: `pagina-financas-caixa.html` (extrato + drawers de transferência, alterar conta, fechamento e movimentações bloqueadas) e `pagina-financas-caixa-lancamento.html` (página própria com as quatro abas), seguindo o padrão já usado em Acerto, Nova transferência e Inventário.

### Pendências novas deste lote

- **`data_fechamento_financeiro`** na empresa + validação no salvar de todo lançamento (manual e automático). ✅
- **Fila de movimentações automáticas bloqueadas** — registro próprio, criado quando a trava impede um lançamento automático. ✅
- **`alterar conta` como ação auditável**, individual e em massa, com origem e destino no detalhe do registro. ✅
- **Totalizador `selecionados (R$)`** na barra de seleção — avaliar para as nossas listagens de valor. ✅ *Caixa e Contas a Pagar.*
- **Coluna `Origem`** no extrato e no Controle de Estoques, apontando o documento que gerou o movimento. ✅ *no extrato;* ⏸ *no Controle de Estoques, espera o ledger real.*
- **Criar categoria a partir do Caixa** (o drawer de Categorias financeiras chamado de dentro do lançamento). ✅
- ~~**Marcadores em massa com rádio incluir/remover**~~ — *descartado junto com os marcadores (22/set).*


## Caixa e Bancos ✅ construído — 22/set/2026

Duas telas: **`pagina-financas-caixa.html`** (o extrato) e **`pagina-financas-caixa-lancamento.html`** (o lançamento, página própria com as quatro abas). A pasta foi de 49 para **51 telas**.

### O que a tela é — e tudo o que vem disso

**É extrato de UMA conta, não lista de lançamentos.** Essa frase decidiu metade do desenho:

- **Ordem crescente por data.** Extrato se lê de cima para baixo, do saldo antigo para o atual. Listagem comum ordena do mais novo; aqui seria ilegível.
- **A primeira linha é o saldo anterior ao período**, e só aparece na **página 1** — na página 2 ela mentiria, porque as linhas que a explicam ficaram para trás.
- **Rodapé com cinco totais** (saldo inicial · entradas · saídas · saldo final · nº de lançamentos), saldo negativo em vermelho, e o bloco **`N selecionados`** aparecendo quando há seleção — detalhe barato do print que responde *"quanto dá o que eu marquei?"* sem exportar nada.
- **Os totais fecham, e isso está no teste:** `saldo inicial + entradas − saídas = saldo final`, e **sem filtro o saldo final bate com o saldo atual da conta**. Conferido nas duas contas com movimento.
- **Com filtro de busca ou de categoria, o rodapé avisa:** *"totais do que está filtrado, não da conta inteira"*. Sem essa linha o número mente com cara de verdade.
- **Entrada e saída são duas colunas**, como no print — não um valor com sinal.

**Divergência medida, não achada:** a coluna **Cliente** do print virou a **segunda linha da célula de Histórico**. Com ela separada, a tabela passava dos ~1040px úteis na largura de referência e a rolagem horizontal esconderia justamente **Entradas e Saídas**. Com o recorte atual a tabela mede **986px em 986px de espaço** — cabe sem rolar. É a lição do Registro de atividades aplicada antes do erro.

### Transferência: a única ação que cria dois registros

Saída na origem, entrada no destino, **ligadas por `parId`**. Está escrito no próprio painel: *"uma transferência não é um lançamento: são dois — é por isso que ela não aparece como receita nem como despesa em relatório nenhum: o dinheiro mudou de lugar, não de dono"*. O teste confirma que os dois nascem juntos, com tipos opostos e apontando um para o outro.

### Alterar conta financeira virou ação auditável

`caixaAlterarConta` **nasce sem senha** — é correção de digitação, não ato destrutivo — mas **sempre registrada**, com as duas contas no detalhe. Quem quiser senha liga na matriz; é exatamente para isso que ela existe. E o painel diz antes do clique: **muda dois saldos de uma vez**. Lançamento em período fechado não vai junto, e a nota diz quantos ficaram para trás.

### Fechamento financeiro — a trava, e os três lugares onde ela pega

- **Uma data**, gravada em `PARAM.fechamentoFinanceiro`. **Fora do `PARAM_PADRAO`**, pelo mesmo motivo de `confirmacoes`: é escrita por uma tela e lida com defesa (`|| ''`) por quem precisa — valor de fábrica ela não tem.
- **`caixaFechaPeriodo` exige senha por padrão.** Fechar trava todo mundo, inclusive lançamento automático: é ato administrativo, não ajuste.
- **O rodapé mostra o estado** (`22/09/2026 · financeiro fechado`), como no print. O usuário não descobre a trava ao tentar salvar.
- **A trava pega em três lugares, e os três estão testados:** lançamento manual (erro **no campo Data** + caixa de erro no topo, como no print), transferência (mesmo erro, mesmo campo) e exclusão em massa (a barra diz *"2 em período fechado, fora de qualquer alteração"* e o link vira *"Nenhum pode ser excluído"*).
- **Reabrir existe.** O print não mostra, mas **trava sem saída é armadilha**: é a mesma ação, com senha, e o texto avisa que um período já conciliado pode mudar de saldo.

### Movimentações bloqueadas — nasceu vazia, e dizendo o que só ela pode dizer

O painel abre com o vazio de verdade e explica **quem vai enchê-lo** (Contas a Pagar, Contas a Receber, ordem de compra) e, principalmente, **quem nunca cai ali**: o lançamento manual, que é barrado na hora, no campo. Semear a fila seria mostrar rastro de tela que não existe — o mesmo erro da prévia que media fila inventada.

### `Tipo = Saldo` lança a diferença — e agora a divergência está confirmada

O print de 22/set mostrou que **lá o tipo *Saldo* fica gravado no registro**. Aqui ele é uma **forma de informar**: a tela calcula e mostra *antes de salvar* — *"Saldo desta conta em 22/09/2026: R$ 252,25. Informando R$ 100,00, o sistema lança uma saída de R$ 152,25 — e é esse movimento que fica no extrato."* Se o saldo informado for igual ao atual, ela diz **"não há o que lançar"** em vez de gravar um zero. Mesma escolha do acerto de estoque, agora com o texto na tela.

### A competência é o dividendo da tela de ontem

A categoria traz a regra e o lançamento a aplica sozinho. Testado: **Energia elétrica** (*mês anterior ao vencimento*) → competência do mês anterior; trocar para **Venda de mercadorias** (*mês do vencimento*) → mês da data. Mexer nas setas **desliga a regra** para aquele lançamento, e a nota passa a dizer *"definida à mão"*.

E a nota diz a verdade incômoda em vez de esconder: **no Caixa existe uma data só**, então *mês do vencimento* e *mês da emissão* caem no mesmo mês — a diferença entre as duas só aparece em **Contas a Pagar e a Receber**, onde emissão e vencimento são datas diferentes. Campo que finge precisão que não tem é pior que campo ausente.

### Criar categoria sem sair da tela

O menu de Categoria termina com **+ Adicionar nova categoria**, que abre o **mesmo drawer de Configurações** — Descrição, Grupo, Considera no DRE e Competência padrão. A categoria criada aqui **vale no sistema inteiro**, já fica escolhida no lançamento e **já manda na competência dele**. Testado ponta a ponta, inclusive o registro no log. Quem está lançando não vai a Configurações no meio do trabalho.

### O que ficou de fora, de propósito

- **Menu `⋯` por linha** — seria componente novo no sistema inteiro; mesma decisão tomada em Contas financeiras. Excluir mora no rodapé da tela de detalhe, como em todos os nossos cadastros.
- **Cadastro rápido de cliente/fornecedor** — seria um segundo formulário de pessoa, e formulário duplicado diverge do original em semanas. O campo busca quem já existe.
- **Imprimir e exportar** — não existe motor de impressão no protótipo, e **botão morto é bug**.

### Pendências novas

- **Cross-link entre as telas do protótipo.** Hoje só *Configurações ERP* e agora *Finanças → Caixa* navegam de verdade; o resto do flyout só move o breadcrumb. Vale uma passagem única, em todos os arquivos, quando a navegação real entrar. ✅ *menu em 22/set; botões dentro das telas em 29/set.*
- **Clicar no primeiro item do breadcrumb cai em *Início***, em todas as 51 telas (`renderBreadcrumb` trata `path.length === 1` como raiz). Defeito sistêmico pequeno; corrigir em uma passagem só, nunca em um arquivo isolado. ✅ *28/set.*
- **Competência em massa** — hoje a barra de seleção altera categoria e conta; mudar competência de vários ainda não. ✅ *29/set — "Alterar competência" na barra de seleção do Caixa.*
- **Importar extrato OFX** — segue adiado, junto com a conciliação. ⏸

### Nota de processo — a terceira mordida do mesmo cão (22/set/2026)

Ao clonar o extrato para gerar a tela de lançamento, cortei a partir do marcador `// ===== EXTRATO =====` e **levei junto `saldoAte`**, que é utilitário compartilhado e não parte do extrato. A tela de lançamento quebrou em `ReferenceError` no primeiro uso do tipo *Saldo* — e **quem pegou foi o teste, não a auditoria**, porque sintaxe estava correta. Corrigido movendo a função para junto dos utilitários **nos dois arquivos**, e não só no que quebrou. **Terceira ocorrência da mesma lição: ao clonar, o corte é por responsabilidade, não por marcador de seção.**


## Barganha de 22/set/2026 — marcadores fora, calendário dentro

### 1. Marcadores: DESCARTADOS do sistema inteiro

O usuário levantou que marcador "parece meio chato de fazer, e tem que cadastrar pra tudo que é negócio". Está certo, e a conversa mudou a decisão. O que pesou:

- **Eu tinha exagerado o risco de schema e corrigi isso na hora.** Marcador **não altera tabela existente** — é tabela nova mais tabela de vínculo, puramente aditivo. Então o argumento "decide agora para não pagar depois" simplesmente não se aplicava. Com ele fora, o melhor motivo para mexer nisso agora caiu.
- **Os casos de uso, testados um a um, sobram pouco.** Agrupar evento transversal (Black Friday) é o único legítimo — e é raro, duas ou três vezes por ano, e o filtro de **período + categoria** que o Caixa já tem cobre a maior parte. Exceção operacional (frágil, prioritário) **é campo, não etiqueta**: fila de separação precisa ser *ordenada* por prioridade, e não se ordena por tag livre. Origem e canal já têm campo. "Conferir depois" é agenda, não etiqueta.
- **O custo se espalha para sempre.** No Olist não é um cadastro: são marcadores financeiros, marcadores na separação, marcador padrão do PDV, marcadores na integração. Cada módulo novo herda cadastro, coluna, filtro e ação em massa — **pedágio em toda tela nova**, para um ganho que aparece duas vezes por ano.
- **E o argumento que decidiu:** marcador existe porque, em empresa grande, o usuário não pode pedir campo novo ao TI e recebe uma etiqueta genérica para se virar. **O ERP aqui é nosso.** Quando precisar de um recorte, criamos o campo certo, com nome certo, ordenável e filtrável. Válvula de escape genérica é para quem não tem roadmap.

**Saída provisória, que já existe e custou zero:** a busca do extrato ignora acento e varre o histórico. Escrever `#blackfriday` no histórico e buscar por isso funciona hoje. Serve também de termômetro: se isso for usado três vezes, o marcador se justifica **e a gente já saberá qual relatório ele precisa alimentar**.

**O que foi feito:** a aba *marcadores* saiu da tela de lançamento do caixa — era o único lugar onde existia. Nenhum cadastro, coluna, filtro ou ação em massa foi construído. O motivo está escrito **dentro do código** da tela, no comentário de cabeçalho, para que ninguém reintroduza por imitação do print.

**Gatilho para revisitar:** quando aparecer a terceira necessidade real de agrupar algo que categoria não agrupa. Aí entra com tabela única e `escopo`, nunca uma por módulo.

### 2. Campo de data com mini calendário: ADOTADO em todo campo de data

Observação do usuário: o Olist põe o ícone de calendário no canto do campo e abre um mini calendário do mês. Adotado, e por três razões:

1. **Conta, não estética.** Contas a Pagar tem três datas por título e Contas a Receber outras três. Construir as duas com campo de texto e trocar depois é retrabalho em seis campos.
2. **`<input type="date">` nativo está fora** pela mesma regra que baniu o `<select>` nativo: o navegador desenha do jeito dele, não se estiliza e o formato muda com o idioma da máquina.
3. **É onde a trava fica visível.** Dia dentro de período financeiro fechado aparece **riscado e não clicável**, com o motivo no `title` e a data do fechamento no rodapé do calendário. A trava deixa de ser descoberta no salvar.

**O campo continua aceitando digitação** — quem sabe a data digita mais rápido. Os dois caminhos, como lá.

**Onde entrou, na mesma passagem (a varredura inteira, não meia):**

| Tela | Campo | Regra do calendário |
|---|---|---|
| Caixa — transferência | Data | mínimo = dia seguinte ao fechamento financeiro |
| Caixa — fechamento | Data de fechamento | máximo = hoje (não se fecha período que não terminou) |
| Caixa — lançamento | Data | mínimo = dia seguinte ao fechamento |
| Ordens de compra (detalhe) | Data da compra | livre |
| Ordens de compra (detalhe) | Data prevista | **mínimo = data da compra** |
| Entrada de notas (detalhe) | Emissão | máximo = hoje |
| Entrada de notas (detalhe) | Entrada | **mínimo = data de emissão** |
| Clientes (detalhe) | Data de nascimento | máximo = hoje |

**Oito campos, cinco telas, um componente.** As regras de mínimo e máximo aceitam **função**, não só valor — é o que permite o limite mudar durante a sessão (o fechamento financeiro muda, a data da compra muda) e o calendário refletir o estado da hora em que abre, não o da hora em que a tela carregou.

**Campos que NÃO ganharam calendário, de propósito:** *data de criação* em Clientes e Fornecedores (carimbo do sistema, somente leitura), a data do lançamento inline no Controle de Estoques (é sempre hoje, por decisão) e a **agenda**, que já tem a própria grade de mês — são componentes diferentes com trabalhos diferentes, e o mini calendário não tenta substituir a agenda.

**Detalhe de comportamento que veio do teste:** dentro de painel lateral o calendário aberto cobre os botões do rodapé.

**E o ajuste que veio do usuário, olhando a primeira versão:** o ícone fica na **direita** do campo e o calendário abria na **esquerda** — o mouse atravessava o campo inteiro para chegar no dia. Corrigido: o popover agora **ancora no ícone**, alinhado pela direita, e **abre para cima** por padrão, descendo só quando o campo está no topo da tela. A razão de subir em vez de descer: num formulário preenchido de cima para baixo, quando se chega na data os campos de cima já foram resolvidos — **cobrir o que já passou custa menos que cobrir o próximo passo e o botão de salvar**.


## Contas a Pagar — prints do sistema em uso (22/set/2026): as quatro perguntas respondidas

O usuário criou uma conta a pagar mensal de R$ 1.000,00 no Olist de teste e mandou onze prints do ciclo inteiro — inclusão, listagem, menu, pagamento e o efeito no Caixa. **Eles respondem as quatro perguntas que eu tinha aberto, e duas delas eu teria errado.**

### 1. Recorrência: doze ocorrências, e o valor REPETE — não divide

A conta mensal de R$ 1.000,00 gerou **12 títulos de R$ 1.000,00 cada**, com o rodapé somando **12.000,00**. Confirma o horizonte de um ano que a documentação já indicava, e acrescenta o que ela não dizia: **recorrência não é parcelamento**. Mensal repete o valor (é a mesma despesa todo mês); *parcelada* é que divide um valor em N. São dois campos diferentes no mesmo seletor, e tratá-los igual seria o erro clássico.

### 2. "Dia do vencimento" é campo próprio — e isso eu não teria inventado

O detalhe mostra **Ocorrência: Mensal** e, ao lado, **Dia do vencimento: 15**. E a listagem prova o efeito: **o primeiro título venceu em 30/09** (a data digitada) e **os onze seguintes vencem todo dia 15** — 15/10, 15/11, 15/12, 15/01/2027… até 15/08/2027.

**Por que isso é melhor que repetir o dia do primeiro vencimento:** aluguel vence dia 15, mas o primeiro pode ser proporcional e cair em outra data; e repetir "dia 30" quebraria em fevereiro. **Adotado: `dia_vencimento` é campo do título recorrente, separado da data do primeiro vencimento.**

### 3. O painel de Pagamento — e a resposta sobre juros

O botão é **pagar (baixar conta)** e abre um painel chamado **Pagamento** com, nesta ordem:

- **Origem** — dropdown das **contas financeiras** (Caixa · Conta teste · Teste 3). É de onde o dinheiro sai.
- **Data** — com o ícone de calendário (o mesmo padrão que acabamos de adotar).
- **Histórico** — já preenchido: *"Liquidação de conta a pagar - Teste 2"*.
- **Categoria** — herdada do título, editável, e com **"Adicionar nova categoria"** no fim do menu, igual ao Caixa.
- **Valor total** — campo **desabilitado**, mostrando o valor do título.
- Rodapé: **pagar** · cancelar · e o link **mais opções** à direita.

**Juros, multa e desconto não aparecem no painel.** Pela documentação, o que *mais opções* revela é o **Valor pago**, usado para pagamento parcial. **Então o Olist não separa juro do principal: quem paga R$ 1.050 numa conta de R$ 1.000 registra "pago 1.050" e o juro entra na categoria do título.**

**Nossa divergência fica registrada e mantida:** vamos ter **juros/multa e desconto como campos próprios na baixa**, porque criamos a categoria *Juros e multas pagos* justamente para o juro aparecer como despesa financeira no DRE. Somar no principal infla a despesa com o fornecedor e esconde o custo do atraso — que é o número que diz se vale a pena atrasar. É divergência deliberada, igual às outras.

### 4. A baixa escreve no Caixa — confirmado com dado na tela

Depois de pagar, o print do Caixa mostra a linha nova: **22/09/2026 · competência 09/2026 · "Liquidação de conta a pagar - Teste 2" · Teste 2 · Aluguéis e condomínio · saída de 1.000,00**, e na coluna **Origem** um badge **"B"** — de baixa. E a linha da conta a pagar passou a **Valor 1.000,00 · Saldo 0,00 · Pago 1.000,00**, com a aba *pagas* em 01.

**A decisão 7 do §12 estava certa, e a coluna `Origem` que construímos no extrato ganhou seu primeiro caso real.** É exatamente o que ela existe para carregar.

### O que os prints acrescentaram além das quatro perguntas

- **Situações: todas · em aberto · emitidas · pagas · atrasadas · canceladas**, com contador em cada aba e **bolinha colorida** por situação. *Cancelada* e *excluída* são coisas diferentes: o menu da linha tem **cancelar conta** e **excluir conta** separados.
- **A linha tem três valores: Valor · Saldo · Pago.** É o *"Valor ≠ Valor líquido ≠ Recebido"* do §11, do lado de pagar — e é o que sustenta o pagamento parcial.
- **Colunas da listagem:** Fornecedor · Histórico · Nº documento · Vencimento · Competência · Valor · Saldo · Pago · Buscador · Marcadores · Forma.
- **A linha expande no lugar** (chevron à direita) mostrando *Nome fantasia* e *Categoria* — dado a mais sem sair da tela. Padrão novo, e bom.
- **Menu da linha:** pagar com cartão *(até 12x)* · pagar (baixar conta) · clonar conta · editar anexos · editar marcadores · cancelar conta · excluir conta.
- **Mais ações do topo:** gerenciar pagamentos · imprimir relatório · **imprimir agrupado por fornecedor** · exportar lançamentos para planilha · importar lançamentos de uma planilha.
- **O detalhe tem badge de situação embaixo do título** (*em aberto*, com bolinha verde) e o link **"visualizar dados do fornecedor"** ao lado do nome — atalho para o cadastro sem perder a conta de vista.

### Uma divergência no CAIXA que o print levantou — ✅ resolvida no mesmo dia

O print do Caixa depois do pagamento mostra duas coisas diferentes do que construímos:

1. **A ordem parece ser decrescente** — o lançamento de 22/09 aparece **acima** dos de 21/09. Nosso extrato é crescente, porque extrato se lê do saldo antigo para o atual.
2. **Há mais de uma faixa de saldo**: *"saldo em 22/08/2026 · R$ 0,00"* no topo e *"saldo em 22/09/2026 · R$ −850,00"* no meio da lista. O nosso tem uma só, no topo.

**Resolvido no mesmo dia, com o print certo.** O usuário mandou o Caixa com **quatro dias distintos e sem filtro de período**, e a regra ficou clara:

1. **A ordem é decrescente**: 10/10 · 27/09 · 22/09 · 21/09, de cima para baixo. **Nosso extrato foi corrigido.** Quem abre o caixa quer ver o que acabou de acontecer — e a linha de saldo anterior, que abria a tabela, passou a **fechá-la**: com ordem decrescente o ponto de partida é a linha mais antiga, que fica embaixo.
2. **A faixa de saldo só existe quando há filtro de período.** Sem filtro, o print não traz faixa nenhuma — e faz sentido: o começo é o saldo de abertura da conta, que o rodapé já mostra como *saldo inicial*. Implementado assim.

**E o print trouxe três achados que ninguém procurava:**

- **Lançamento com data FUTURA aparece no extrato e já entra no saldo.** Há linhas de 27/09 e 10/10 num print tirado em 22/09, e o saldo atual (1.150,00) as inclui. O nosso já fazia isso, por acaso — agora é por decisão.
- **O lançamento de `Tipo = Saldo` aparece no extrato SEM valor em entrada nem em saída**, e não soma nos totais: são 8 lançamentos, mas só 7 têm valor. **Isso fecha a discussão do tipo Saldo a nosso favor** — lá ele vira uma linha fantasma que não explica nada; aqui ele lança a diferença como entrada ou saída de verdade, e o extrato mostra o movimento.
- **Competência é opcional lá:** duas linhas do print estão com a coluna vazia. Aqui a categoria sempre resolve a competência, e quem lança pode sobrepor — campo em branco num relatório de competência é buraco no DRE.


## Contas a Pagar ✅ construído — 22/set/2026 (listagem + página da conta)

Duas telas: `pagina-financas-contas-pagar.html` (a lista) e `pagina-financas-contas-pagar-detalhe.html` (a conta). Auditoria **OK** nas duas; **30 asserções** na listagem, **44** na página da conta, **16** no teste de integração com o Caixa — todas passando.

### O que a listagem faz

- **Cinco abas de situação com contador e bolinha**: todas 22 · em aberto 15 · atrasadas 03 · pagas 03 · canceladas 01.
- **Três valores por linha** — Valor · Saldo · Pago —, com a marca *parcial* quando o pagamento não fechou.
- **A linha expande no lugar** (chevron), mostrando nome fantasia, categoria e ocorrência sem sair da tela. Expandir **não navega**; abrir a conta é clicar na linha.
- **Seleção em massa → painel Pagamento**, que baixa várias contas de uma vez.
- Filtros: busca (fornecedor · nº do documento · histórico · categoria), período, **base da data (vencimento × competência)** e categoria.

### O que a página da conta faz

Quatro abas — **dados da conta · competência · pagamentos · anexos** — e dois modos, leitura e edição, com **badge de situação ao lado do título**.

- **Fornecedor** com busca e o link **"visualizar dados do fornecedor"**, que leva ao cadastro real (o print do Olist tem esse atalho e ele é bom).
- **Repetição** é um bloco próprio: Ocorrência · Dia do vencimento · Dia da semana · Nº de parcelas, cada campo aparecendo só quando a ocorrência escolhida o usa.
- **Prévia do que será criado**, antes de salvar: *"3 contas somando R$ 1.000,00 (a última com R$ 333,34). Primeiro vencimento em 22/09/2026, último em 22/11/2026."* Recorrência que só se entende depois de criada é a forma mais rápida de encher a lista de lixo.
- **Aba pagamentos** com resumo (valor · pago · saldo), uma linha por baixa e o link **estornar**.
- **Excluir conta com pagamento é barrado** — e a mensagem manda estornar, em vez de só proibir.

### A pesquisa na documentação do Olist (API 2.0), e o que ela mudou

Consultadas `contas-pagar-incluir` e `contas-pagar-obter` em 22/set/2026. Quatro achados:

1. **Ocorrência tem sete valores** — U única · W semanal · P parcelada · M mensal · T trimestral · S semestral · A anual. São exatamente os que já tínhamos.
2. **`numero_parcelas` vai até 100** e é ele que diz **quantos títulos nascem**. Adotado: o campo vale para toda ocorrência repetida, não só para a parcelada.
3. **`dia_vencimento` é obrigatório para M e P**; para W existe **`dia_semana_vencimento` (0–6)**, que nós não tínhamos. **Campo novo, adotado.** Para T, S e A o dia vem do primeiro vencimento.
4. **A situação devolvida é `aberto · pago · cancelada · parcial`.** Não existe "atrasado" na API — **confirma a nossa regra**: atraso é derivado do vencimento, nunca um estado gravado.

### Duas divergências para combinar — ✅ fechadas na barganha de 23/set

**1. `parcial` é situação lá; aqui é marca dentro de "em aberto".** A API devolve *parcial* como um dos quatro estados. Nossa listagem mostra a conta parcial dentro de *em aberto*, com a palavra *parcial* na coluna de valores. Como a nossa situação é **sempre derivada**, virar aba custa uma linha (`pago > 0 && pago < valor`). A pergunta é se vale uma sexta aba — o argumento a favor é que "quanto ainda devo desta conta" some hoje dentro de quinze contas em aberto.

**2. Parcelada DIVIDE, recorrência REPETE.** Doze parcelas de uma nota de 1.200 são doze títulos de 100; doze meses de aluguel de 4.200 são doze títulos de 4.200. A documentação chama os dois de `valor` sem dizer qual é qual. **Decidimos assim e a tela anuncia a regra na prévia**, em vez de decidir escondido — na divisão, a última parcela absorve o centavo (333,33 · 333,33 · **333,34**).

### A integração com o Caixa é REAL no protótipo, não um texto dizendo que seria

Cada tela é um arquivo solto, então a baixa grava o movimento num depósito compartilhado no navegador (`deskCaixaExtras`) e o extrato lê esse depósito junto com o mock dele — mesma ideia do `deskParametros` e do `deskLog`. **No Lovable isso não existe: é a mesma tabela `movimentos`, escrita pela baixa.**

O teste de integração faz o caminho do usuário: baixa a conta, clica no aviso *"Abrir o Caixa"* e confere que os dois lançamentos estão lá, com o valor certo, a categoria certa e a origem apontando para a conta.

**O juro vira lançamento separado, na categoria `Juros e multas pagos` (id 20).** É a divergência deliberada já registrada: somar o juro no principal infla a despesa com o fornecedor e esconde o custo do atraso, que é justamente o número que diz se vale a pena atrasar.

**E o estorno devolve o dinheiro como ENTRADA no Caixa**, com a origem apontando para a mesma conta. Baixa errada apagada em silêncio é a forma mais limpa de o extrato deixar de bater com o banco.

### Três defeitos que a construção encontrou — e o que foi feito

1. **Painel lateral morto em modo leitura.** `body.modo-leitura` escondia os campos do formulário — e o painel de Pagamento, que abre **por cima** de uma conta em leitura, abria só com rótulos. Regra nova no design system, propagada para as duas telas que têm modo leitura.
2. **Conta paga sem linha de pagamento.** O mock marcava `pago` sem registrar a baixa, então uma conta paga não se explicava — e, pior, não se estornava, porque o estorno trabalha em cima do pagamento. Corrigido no mock compartilhado das duas telas.
3. **`DIAS_SEMANA` já era do calendário.** O componente de data usa esse nome para as letras do cabeçalho. Colisão pega pela auditoria antes do navegador.

## Cross-link do menu ✅ resolvido — 22/set/2026 (as 53 telas de uma vez)

Pendência aberta desde a primeira varredura. O flyout **já sabia navegar** — item com `data-href` navega, item sem `data-href` só move o breadcrumb —, faltava o atributo. Agora **31 itens de menu apontam para a tela real**, nas 53 páginas de uma vez, e item sem tela continua inerte como antes: a mudança é aditiva, não muda comportamento nenhum existente.

Isso importa para a validação: até aqui cada tela era uma ilha e conferir duas telas juntas exigia abrir dois arquivos à mão. **Agora o protótipo se navega.**

**A auditoria rodou nas 53 telas antes e depois da varredura e o resultado é idêntico** — nenhum problema novo. O que ela acusa é dívida antiga, concentrada nas telas mais velhas: 23 `getElementById` sem elemento, 20 checkboxes sem a classe do design system, 15 `<select>` nativos, 6 controles sem ação. **São 18 telas limpas de 53.** Não é urgente — nenhum desses quebra a tela —, mas é o tamanho real do retrabalho que sobra quando essas telas forem para o Lovable, e é bom saber disso agora e não lá.

*(O `pagina-molde-referencia.html` aparece com "dois `<body>`" e ids duplicados: é esperado, ele são dois documentos no mesmo arquivo — exceção já registrada.)*


## Barganha de 23/set/2026 — as duas famílias de repetição, escopo em grupo e cancelar

Cinco rodadas de barganha antes de uma linha de código. O que ficou decidido, e por quê.

### 1. A aba *parcial* não entra — e o motivo é estrutural, não estético

A API do Olist devolve quatro situações: `aberto · pago · cancelada · parcial`. Eu levantei isso como divergência; **o usuário decidiu não criar a aba, e ele está certo por um motivo mais forte que "não vale a pena".**

**Abas particionam.** Uma conta está em exatamente uma delas e a soma dos contadores fecha com *todas*. "Parcial" não é um quinto estado — é um **grau dentro de em aberto**, e cruza com *atrasada*: a conta de 1.180 com 400 pagos e vencimento passado é parcial **e** atrasada. Virando aba, ou ela sai de *atrasadas* (escondendo justamente o que importa) ou aparece nas duas (e os contadores param de fechar).

**E a tela do Olist também não tem essa aba** — os prints mostram *todas · em aberto · emitidas · pagas · atrasadas · canceladas*. O `parcial` é valor de campo na API, para quem consome dado; não é aba na tela de ninguém. A divergência era menor do que eu pintei.

Fica como está: a palavra *parcial* na linha e a coluna **Saldo**, que é onde mora "quanto ainda devo". Se um dia incomodar, a saída barata é um número na barra de totais, que não cria aba nem quebra a partição.

### 2. Duas famílias de repetição — a decisão central da tela

Aqui a conversa deu três voltas, e a volta final é a certa. O Olist trata os dois casos com o mesmo campo `numero_parcelas`; nós separamos:

| | **Parcelada** | **Recorrente** (semanal · mensal · trimestral · semestral · anual) |
|---|---|---|
| o que é | uma **compra** dividida | uma **despesa** que volta |
| quantas | **quantidade** — 3x é 3, e acaba | **horizonte** — vai *até* uma data |
| o valor | total a dividir **ou** por parcela (o usuário escolhe) | sempre o de cada uma, repete |
| termina | porque a compra acabou | porque o ano acabou — e aí **renova** |

**O que o usuário corrigiu em mim:** eu propus "parcelada divide, recorrência repete" e amarrei isso na palavra *Parcelada*. Ele mandou tirar a Parcelada e usar sempre o valor do mês; depois, pensando numa compra de verdade (3.000 em 3x), voltou atrás. **A conclusão dele é melhor que as duas anteriores:** a Parcelada volta, e **um dropdown ao lado do valor diz o que o número significa** — `parcelar valor total` (padrão) ou `valor por parcela`. O que varia é o SIGNIFICADO DO NÚMERO, e o lugar honesto de dizer isso é junto do número, não escondido três campos acima. O rótulo do campo muda junto: *Valor (R$)* vira **Valor total (R$)** quando vai dividir.

**Aluguel de 1.200 começando em março gera DEZ contas, não doze** — o ano acabou. Mentir "12 parcelas" seria inventar um fim que o contrato não tem. O `Repetir até` nasce em **31/12 do ano corrente**.

**O centavo:** arredonda para **baixo** e a **última** parcela absorve. 1.000 em 3x = 333,33 · 333,33 · **333,34**. A soma bate exata com a nota, que é o que a conciliação com o fornecedor cobra.

**Consequência adotada: o contador "parcela 3 de 12" saiu do sistema.** Com horizonte no lugar de contagem ele não diz nada — quem identifica a conta é o **mês**, e disso a competência já cuida. Um campo a menos para manter verdadeiro. Na lista, a conta que se repete ganha o ícone ⟳ e o grupo aparece na linha expandida.

**E `Dia do vencimento` não foi removido** — ele passou a vir **pré-preenchido com o dia do primeiro vencimento**. No caso comum (10/10 repete dia 10) ninguém toca; quando a primeira parcela é proporcional e cai fora do dia, troca. Foi para isso que o Olist separou os dois campos, e o print provava: primeiro em 30/09, os onze seguintes no dia 15.

### 3. Escopo de alteração em grupo — o padrão do Google Calendar

O aluguel reajusta em julho. Antes, mudar o valor abria cinco telas. Agora, mexer numa conta que se repete pergunta **primeiro** em quais contas isso vale: **só esta · esta e as seguintes · todas do grupo**.

**Decisão de schema: grupo é ETIQUETA, não registro.** Cada conta carrega `grupo` e mais nada; "as seguintes" é um update em quem tem o mesmo grupo e vence a partir desta. Sem tabela de recorrência. Se um dia virar registro, a etiqueta continua valendo e nada precisa ser desfeito — a alternativa (tabela `recorrencia` com regra viva) só se paga se quisermos mexer na recorrência como conceito, e hoje o que se quer é corrigir um valor daqui pra frente.

**A regra do que propaga**, escrita na própria tela: propaga o que é da **despesa** (fornecedor, documento, categoria, forma, histórico, valor); **não** propaga o que é da **parcela** (vencimento, emissão, competência) — senão as doze contas do aluguel venceriam todas no mesmo dia. **E conta paga ou cancelada fica fora de qualquer escopo em massa**: mudar o valor de uma conta já paga faria o saldo mentir. O modal diz quantas ficam de fora e por quê.

**Estender o horizonte CRIA as contas que faltam.** É isso que faz a renovação existir: o aluguel ia até 15/12, você põe 31/12 do ano seguinte e as doze de 2027 nascem no mesmo grupo, continuando de onde parou. **Encurtar não apaga nada** — apagar conta se faz de propósito, pelo escopo de exclusão, nunca como efeito colateral de trocar uma data.

### 4. Cancelar conta — uma falha minha, confessada e corrigida

A aba **canceladas** existia desde o início, com contador e bolinha, e uma conta cancelada no mock. **Mas não havia nenhuma ação que cancelasse uma conta** — ela nascia cancelada e ninguém podia chegar naquele estado. Estado alcançável só pelo mock é estado que não existe.

Agora existe, com a distinção que o print do Olist já mostrava separada:

- **Cancelar** — a conta não vai ser paga, mas **fica no histórico**. O fornecedor cancelou o pedido, a compra caiu. Sai do *a pagar*, não soma em nada.
- **Excluir** — foi **erro de digitação**. Some do sistema. Só para conta sem pagamento.

Os dois na listagem (seleção em massa) e na página da conta, com chave própria `contasPagarCancela` no catálogo. **E cancelada volta atrás** — pedido cancelado às vezes é retomado: o mesmo link troca de rótulo para *Reativar*, em vez de virar dois controles. Conta com pagamento não cancela: a mensagem manda **estornar** primeiro.

### 5. A listagem abre no mês corrente

Com recorrência indo até 31/12, abrir em "todos" mostra o ano inteiro e a tela deixa de responder *"o que eu pago agora"*. O filtro de período nasce em **este mês**; a lista inteira está a um clique.

### 6. Renovação aparece na Agenda — e não precisou de máquina nova

Quando a última conta de um grupo recorrente vence nos próximos **90 dias** (contrato de aluguel se renegocia com meses de antecedência, não com dias), Contas a Pagar publica um aviso e a **Agenda** mostra: *"Renovar aluguel do galpão — última conta vence em 15/12/2026"*, com seta indicando que o item leva para fora da agenda. Clicar abre a conta **em edição**, com o `Repetir até` já apontando para o fim do ano seguinte e uma faixa explicando que salvar cria as contas que faltam.

**Mecanismo novo, deliberadamente geral:** `deskAvisos` é um mapa no navegador com chave por origem — recarregar reescreve em vez de duplicar. Estoque mínimo, contas a receber e conferência vão usar o mesmo caminho. **No Lovable isso não é tabela escrita por tela: é uma consulta** — "grupos cuja última conta vence nos próximos 90 dias e não foram renovados". Parcelada não entra: ela acaba porque a compra acabou, não porque precisa renovar.

### Contas a Receber fica para depois, por dependência

A conta a pagar nasce de alguém digitando; **a conta a receber nasce de uma venda**, e Pedidos de Venda não existe. Construir agora seria uma tela cuja origem principal é mock de algo inexistente — o erro que já evitamos na coluna *Origem* do Caixa. Decidido: **pula e volta depois**, quando Vendas existir.


---

# ESTADO EM 23/set/2026 — por onde retomar

> ⚠️ **Superado pelo bloco "ESTADO EM 28/set/2026", no fim do arquivo.** Os itens 3(a) e 3(b) abaixo foram resolvidos — e os dois eram maiores do que estão descritos aqui. Mantido como histórico.

Bloco de handoff: o chat ficou longo e o trabalho continua em outra sessão.

## O que está pronto e validado

**53 telas na pasta.** Finanças fechou quatro: *Categorias financeiras*, *Caixa*, *Lançamento do Caixa* e *Contas a Pagar* (listagem + página da conta). As quatro passam limpas na auditoria oficial e na estática.

**Três integrações são reais no protótipo, não texto dizendo que seriam:**

- a **baixa** de Contas a Pagar escreve no extrato do **Caixa** (`deskCaixaExtras`), com o juro em lançamento separado na categoria *Juros e multas pagos*, e o estorno devolve como entrada;
- a **recorrência que termina** vira aviso na **Agenda** (`deskAvisos`), e clicar nele abre a conta pronta para renovar;
- o **menu lateral navega de verdade** entre as 53 telas (31 itens com destino).

**Verificação:** 294 asserções de navegador, em `_ferramentas/` (ver o `LEIA-ME.md` de lá). Rodam em qualquer sessão — acham a pasta e o navegador sozinhos.

## O que está aberto

### 1. Aprovação de Contas a Pagar
A regra de ouro é protótipo → aprovação do usuário → prompt do Lovable. As telas foram entregues; **a aprovação ainda não foi dada em palavras**. Confirmar antes de gerar qualquer prompt.

### 2. Contas a Receber — adiada por dependência
A conta a pagar nasce de alguém digitando; **a conta a receber nasce de uma venda**, e Pedidos de Venda não existe. Construir agora seria uma tela cuja origem principal é mock de algo inexistente. **Decidido: pular e voltar depois de Vendas.**

### 3. Revisão completa da pasta — combinada para uma sessão nova
Duas coisas, as duas mecânicas, nenhuma precisa de decisão:

**(a) O bloco de senha viajou sem a marcação do modal, em 8 telas.**
`clientes-detalhe`, `fornecedores-detalhe`, `lojas-desk-detalhe`, `dashboard-kpis`, `agenda`, `boas-vindas`, `minha-conta` e `performance-vendas` definem `confirmarAcao` e `abrirModalConfirmacao`, mas não têm `#confirmModal` no HTML. **Hoje é código morto** — conferido: nenhuma dessas telas chama a função. **É uma bomba armada:** a primeira ação com trava que alguém puser numa delas vai chamar o modal, `getElementById('confirmModalTexto')` volta `null` e a ação não acontece, sem erro visível. Correção recomendada: colar a marcação do modal nas 8 (≈20 linhas já conhecidas), não remover o bloco.

**(b) Apertar o `auditoria.py`**, que hoje produz quatro falsos positivos (todos verificados arquivo por arquivo, lista completa no `_ferramentas/LEIA-ME.md`): `<select>` dentro de comentário, `menuMaisAcoes` com guarda, `<a href>` lido como controle mudo, e checkbox estilizado pelo pai. Enquanto não for apertado, **o número que ele dá superestima a dívida** — foi o que aconteceu nesta sessão, quando reportei "36 telas com dívida" e a verificação mostrou que quase tudo era ruído do próprio script.

### 4. Pendências antigas, já registradas
Exclusão suave nos 12 pontos · integridade referencial (FK/Supabase) · Permissões de Usuários (4º verbo *ver*) · `produto_fornecedor` de-para · Desk Help · o primeiro crumb do breadcrumb cair em *Início* · competência em massa · OFX · parcelas na Ordem de Compra · consulta CNPJ (depende do certificado digital) · Operação Fiscal Padrão · homologação × produção · ESC não fecha dropdown aberto.

## Como a próxima sessão deve começar

1. `device_list_dir` na pasta e comparar com o esperado — já houve caso de commit cair em subpasta e a pasta ficar defasada por semanas. **Comparar por hash, não por tamanho:** as correções de ícone desta sessão (`28px`→`24px`, `15px`→`13px`) mudaram o arquivo sem mudar o tamanho.
2. Rodar a auditoria oficial da skill na pasta inteira, e os testes de `_ferramentas/`.
3. Ler os blocos desta sessão: *"Contas a Pagar ✅ construído"*, *"Barganha de 23/set/2026"* e *"Cross-link do menu ✅ resolvido"*, mais §9.2, §9.3, §12.2, §14.1 e §14.2 do design system.

**A pasta `Claude outputs` continua sendo lixo de app — ignorar.**


---

# ESTADO EM 28/set/2026 (manhã) — por onde retomar

> ⚠️ **Superado pelo bloco do fim do arquivo.** Mantido como histórico.

A revisão completa da pasta, que estava combinada para uma sessão nova. **Leia este bloco primeiro.**

## O que foi feito

**A pasta estava íntegra na abertura:** 53 telas + os 2 `.md`, nada faltando, nada defasado — o Passo 0 passou limpo pela primeira vez desde que existe.

**Item 3(a) — o bloco de senha sem modal.** Não eram 8 telas: eram **23**. E o sintoma registrado estava invertido — a ação não deixava de acontecer, ela **acontecia sem pedir senha e sem entrar no registro de atividades**. A correção proposta (colar a marcação) não teria resolvido. Foi fechado em duas camadas: **falhar fechado nas 52** telas que têm o bloco, e **modal completo nas 8** que não tinham marcação nenhuma. Detalhe completo no §14.3 do design system.

**Uma segunda bomba, achada pelo teste.** O envelope de senha zerava o `.length` de `abrirModalConfirmacao`, e é por `.length` que `confirmarAcao` decide como chamar o modal. O ramo de 4 argumentos era **inalcançável**: em **25 telas** (as de assinatura 4 e 5) o callback teria caído na posição da cor e a ação não aconteceria depois de confirmar. Corrigido preservando a aridade do original, nas 52. As três assinaturas foram provadas no navegador.

**Item 3(b) — apertar o `auditoria.py`.** Os quatro falsos positivos conhecidos, mais um quinto (ids nascidos de `innerHTML`, em Metas), foram resolvidos **no script** — nenhuma exceção escrita à mão. **De 33 arquivos "com problema" para 0 falhas reais nas 53.** O aperto foi provado nos dois sentidos: com defeito injetado, o script continua reprovando os cinco casos.

**Verificação:** auditoria oficial da skill limpa nas 53 (só as 6 classes-gancho do §12.2, exceção conhecida), **410 asserções** de navegador passando — as 294 que já existiam mais as **116** do `teste_confirma_senha.py`, novo.

## O que continua aberto

### 1. Aprovação de Contas a Pagar
Segue sendo o item que destrava a saída de Finanças. As telas foram entregues em 23/set; **a aprovação em palavras ainda não foi dada.** Confirmar antes de gerar qualquer prompt do Lovable.

### 2. Contas a Receber — adiada por dependência
Sem mudança: a conta a receber nasce de uma venda, e Pedidos de Venda não existe. **Pular e voltar depois de Vendas.**

### 3. Dívida das telas antigas — medida de novo, e é menor do que parecia
Com o `auditoria.py` apertado, o número que sobra é **zero falha real**. O que existia era ruído do próprio script. **A dívida real das telas antigas, hoje, é a que está nomeada nas pendências do §13 do design system** — não um número solto de auditoria.

### 4. As 15 telas com `#confirmModal` servindo de aviso
Protegidas pela camada de falhar fechado, mas ainda sem modal de confirmação de verdade. **Quando uma delas ganhar a primeira ação com trava, o modal entra junto** — e aí é preciso resolver a colisão entre `avisar()` e a confirmação sobre a mesma marcação. Não é urgente e não é bug hoje.

### 5. Classes-gancho e a seção 3 da auditoria oficial
As 6 classes-gancho (§12.2) continuam sendo o único apontamento da auditoria oficial, em 4 arquivos. A convenção do projeto já é **`data-*` para comportamento, classe para estilo** — converter as 6 deixaria a auditoria oficial verde sem enfraquecê-la. **É mexer em tela que funciona, então fica para barganha**, não para decisão minha.

### 6. Pendências antigas, já registradas
Exclusão suave nos 12 pontos · integridade referencial (FK/Supabase) · Permissões de Usuários (4º verbo *ver*) · `produto_fornecedor` de-para · Desk Help · o primeiro crumb do breadcrumb cair em *Início* · competência em massa · OFX · parcelas na Ordem de Compra · consulta CNPJ (depende do certificado digital) · Operação Fiscal Padrão · homologação × produção · ESC não fecha dropdown aberto.

## Como a próxima sessão deve começar

1. `device_list_dir` na pasta e comparar com o esperado. **Comparar por hash, não por tamanho** — as correções desta sessão mudam tamanho, mas as de 23/set (`28px`→`24px`) não mudavam.
2. Rodar `python3 auditoria.py ../pagina-*.html` (uma chamada, total no fim) e os testes de `_ferramentas/` — inclusive o `teste_confirma_senha.py`.
3. Rodar a auditoria oficial da skill na pasta inteira.
4. Ler o §14.3 do design system, que é onde as duas lições desta sessão estão escritas.

**A pasta `Claude outputs` continua sendo lixo de app — ignorar.**


---

# ESTADO EM 28/set/2026 (tarde) — o "Mais ações" e a varredura de pendências

> ⚠️ Superado pelo bloco do fim do arquivo.

Sessão de pôr em dia. **Leia este bloco primeiro.**

## O que foi feito

**1. "Mais ações" virou um componente só — 18 telas.** Existiam **quatro implementações** do mesmo menu: quatro ids, dois rótulos (*Mais ações* e *Ações*), três estilos de botão e **dois componentes de menu diferentes**. O paralelo de Clientes/Fornecedores/Produtos não media espaço, não tinha `max-height` e **não fechava mutuamente** com os outros dropdowns. Padrão único escrito no §9.4 do design system.

**2. A ação destrutiva saiu do rodapé e foi para o menu, nas 4 páginas de registro** — `contas-pagar-detalhe` (Cancelar + Excluir), `caixa-lancamento`, `produtos-detalhe` e `ordens-compra-detalhe`, esta última com o menu **já existente** e a ação do lado de fora. Três ganharam o menu do zero. Barra de seleção em massa e drawer de cadastro curto ficam como estão, e o §9.4 diz por quê.

**3. ESC fecha dropdown — 49 telas.** Pendência aberta desde sempre. Handler em fase de captura que **só engole o Esc quando havia menu aberto**, então o Esc de modal e drawer continua intacto.

**4. O primeiro crumb do breadcrumb leva ao Início — 52 telas.** Antes só abria o flyout: um caminho que não chega a lugar nenhum.

**5. As 6 classes-gancho viraram `data-*`** (§12.2). Com isso a **auditoria oficial ficou 100% limpa pela primeira vez** — as oito seções verdes, incluindo a seção 3, que acusava 4 arquivos desde que os ganchos existiam.

**6. Aviso e confirmação deixaram de dividir o mesmo modal — 15 telas.** O aviso virou `#avisoModal` com ids próprios e cada tela ganhou confirmação de verdade, com campo de senha. **As 52 telas com o bloco de senha agora têm confirmação real**: a falha fechada de 28/set (manhã) virou só rede de segurança.

**7. Categoria financeira real na Ordem de Compra.** A lista provisória saiu; a OC lê o espelho de *Configurações → Categorias financeiras*, agrupado e só com categorias de saída — ordem de compra vira conta a pagar.

**8. Modo leitura nas 5 telas de detalhe antigas.** Registro carregado abre em leitura e vira formulário no botão *Editar*. O valor exibido é **derivado do campo**, não marcação duplicada — são 174 campos. Com os dois modos existindo, a preferência *"ao acessar um cadastro: edição ou visualização"* de Interface do usuário passa a ter onde pegar.

**9. Dois bugs achados no caminho.** O contador das abas de Contas a Pagar contava a base inteira e **discordava da lista** (§14.4) — só aparecia em certas datas. E o rename do modal de aviso atropelou o bloco de senha compartilhado, derrubando a trava em 15 telas: passou na auditoria e foi o teste de navegador que pegou.

**Verificação:** auditoria oficial **tudo limpo ✓** nas 53 · auditoria estrita **0 falhas reais** · **todas** as suítes de `_ferramentas/` passando, incluindo duas novas (`teste_mais_acoes.py`, `teste_esc_dropdown.py`).

## O que continua aberto

### 1. Aprovação de Contas a Pagar
Ainda o item que destrava a saída de Finanças. As telas estão entregues desde 23/set; **a aprovação em palavras não foi dada.** Confirmar antes de gerar prompt do Lovable.

### 2. Contas a Receber — adiada por dependência de Vendas
Sem mudança.

### 3. Barganhas abertas (dependem de decisão, não de trabalho)
Controle de Estoques v2 (colunas de situação do saldo, decidido em 14/set e nunca construído) · painel de filtros avançados do Controle de Estoques · Categorias migrar para dropdown multi-seleção · Guia de primeiros passos · dividir o `pagina-molde-referencia.html` em dois arquivos.

### 4. Travadas por módulo que não existe
Kit virtual quebra Inventário e Acerto · Composição de Kit · Transportadora (Desk Flash, última de F2) · permissão real em Metas e Vendedores · integridade referencial (FK/Supabase) · exclusão suave nos 12 pontos · `produto_fornecedor` de-para · Desk Help · competência em massa · OFX · parcelas na Ordem de Compra.

### 5. Travadas por coisa externa
Devolução ao fornecedor e recusa parcial (NF-e / contador) · consulta CNPJ (certificado digital) · Operação Fiscal Padrão · homologação × produção.

### 6. Pendência nova de dado: **o mock envelhece**
Datas fixas + listagem abrindo no mês corrente = em algumas semanas tudo vira *atrasado*. Quando incomodar, gerar as datas relativas a hoje. Detalhe no §13 do design system.

## Como a próxima sessão deve começar

1. `device_list_dir` na pasta e comparar **por hash**.
2. `python3 auditoria.py ../pagina-*.html` e os testes de `_ferramentas/`.
3. Auditoria oficial da skill na pasta inteira.
4. Ler o **§9.4** (o padrão do "Mais ações") e o **§14.4** (as lições desta sessão) do design system.

**A pasta `Claude outputs` continua sendo lixo de app — ignorar.**


---

# ESTADO EM 29/set/2026 — barganhas resolvidas, clonar e recibo

> ⚠️ **Superado pelo bloco do fim do arquivo.** Os dois itens abertos daqui (aprovação de Contas a Pagar e as duas Conferências) foram fechados na mesma tarde. Mantido como histórico.

## As cinco barganhas, decididas

1. **Controle de Estoques v2 — APROVADO.** E ele já estava construído: a listagem tem as 9 colunas decididas em 14/set e os dois filtros renomeados. O §13 dizia "ainda não construído" — **terceira entrada mentirosa do §13 nesta semana**, junto com Registro de atividades e Matriz módulo × verbo.
2. **Painel de filtros avançados — parado**, e por falta de necessidade, não de decisão. Tags morreram com os marcadores; variações depende de saldo por variação. Sobram categoria e fornecedor, e ninguém sentiu falta.
3. **Categorias fica como está.** As duas versões foram montadas e comparadas por imagem. O dropdown economiza ~110px e cobra o recolhimento automático — em formulário de três campos não paga. Régua registrada no §13.
4. **Guia de primeiros passos — espera Usuários.** Dois dos três pontos dão para construir; o terceiro depende da tela de Usuários, e interruptor que liga um guia que ninguém recebe não controla nada.
5. **Dividir o molde — adiado para o fim do projeto**, por decisão do usuário: há muito a construir antes.

## O que foi construído

**Clonar conta** e **Imprimir recibo**, os dois dentro do "Mais ações" de Conta a pagar (regras no §9.4 do design system). O recibo imprime por `@media print`, com valor por extenso; o item fica **travado com motivo** quando a conta não tem baixa. O clone abre em edição, com vencimento vazio, e não está gravado.

**30 asserções novas** em `_ferramentas/teste_recibo_clone.py`.

## O que foi conferido, não construído

**Os marcadores de Ordens de Compra já estavam removidos** — a remoção entrou numa rodada de 28/set sem ser anunciada. Conferida linha a linha contra a versão original do computador: limpa, sem referências órfãs. Lição no §14.5.

## Aberto — e o novo

### 1. Aprovação de Contas a Pagar
Continua sendo o item que destrava a saída de Finanças.

### 2. As duas Conferências — desvio confirmado em 29/set
O menu tem **dois itens** para **um módulo**, e o segundo aponta para uma tela de detalhe:

| tela | o que é | breadcrumb |
|---|---|---|
| `conferencia-entrada.html` | a **fila** — notas de compra E de devolução, 5 abas de situação | Estoque › Conferência de Entrada |
| `conferencia.html` | a **contagem de UMA nota** | Estoque › Conferência › Nota 9051 |

Os breadcrumbs já dizem a verdade: é listagem + detalhe, como Controle de Estoques. **O menu é que mente** — clicar em *Conferência* larga o usuário na nota 9051, que ninguém escolheu. É o único lugar do sistema onde um item de menu aponta para tela de detalhe.

**E a causa está escrita no código:** a fila, ao mandar conferir, mostra *"a navegação entre telas só passa a funcionar de verdade no Lovable"* — mensagem que ficou obsoleta em 22/set, quando o cross-link do menu passou a navegar de verdade. O segundo item de menu nasceu como contorno disso.

**Proposta:** a fila navega para a contagem (`?nota=<numero>`), e o menu volta a ter um item só, apontando para a fila. ~~Aguardando aval.~~ → ✅ *aprovado e feito na mesma tarde.*

### 3. Barganhas e dependências
Sem mudança: Contas a Receber espera Vendas; kit, transportadora, permissões, integridade referencial e exclusão suave esperam seus módulos; devolução, recusa parcial e consulta CNPJ esperam NF-e, contador e certificado.

## Como a próxima sessão deve começar

1. `device_list_dir` e comparar **por hash**.
2. `python3 auditoria.py ../pagina-*.html` e os testes de `_ferramentas/`.
3. Auditoria oficial da skill.
4. Ler **§9.4** (o "Mais ações", agora com clonar e recibo) e **§14.5** (as lições de hoje).


---

# 29/set/2026 (tarde) — Contas a Pagar aprovado e a Conferência corrigida

> ⚠️ **O "Aberto" deste bloco foi substituído pelo quadro único do bloco seguinte.** Mantido como histórico.

## Contas a Pagar: APROVADO por inteiro

O usuário aprovou o módulo completo — listagem, página da conta, baixa, recorrência, clonar e recibo. **A regra de ouro cumpriu o ciclo: protótipo → aprovação → prompt do Lovable.** É o primeiro módulo de Finanças liberado para virar prompt, e a pendência aberta desde 23/set está fechada.

## Conferência: uma entrada de menu, duas telas

Pergunta do usuário: *"se faz sentido ficar as duas telas ou não"*. **Faz** — é fila + contagem de uma nota, listagem e detalhe como no resto do sistema. O que não fazia sentido era o caminho. Detalhe completo no **§12.3** do design system. Em resumo:

- item de menu duplicado removido das **53 telas** — sobra *Conferência de Compra*, apontando para a fila;
- a fila **navega** para a contagem da nota escolhida (`?nota=`);
- a contagem lê a nota da URL, com as **4 notas conferíveis** montadas;
- o aviso obsoleto de 22/set (*"a navegação só funciona no Lovable"*), que foi o que gerou o segundo item, saiu;
- **achado no caminho:** o mock da nota 9051 não fechava — itens somavam 28.451,90 contra nota de 24.890,00, numa tela que compara justamente esses dois números.

**Regra nova: item de menu aponta para listagem, nunca para detalhe.**

## Verificação

Auditoria oficial **tudo limpo ✓** · estrita 0 falhas em 53 · todas as suítes de `_ferramentas/` passando.

## Aberto

Contas a Receber (espera Vendas) · kit, transportadora, permissões, integridade referencial e exclusão suave (esperam seus módulos) · devolução, recusa parcial e consulta CNPJ (NF-e, contador, certificado) · filtros avançados e guia de primeiros passos (parados por decisão de 29/set) · dividir o molde (adiado para o fim).

**Próximo módulo natural: Vendas / Pedidos de Venda** — é a dependência que trava Contas a Receber.


---

# ESTADO EM 29/set/2026 (noite) — a limpeza para voltar a construir

**Leia este bloco primeiro.** O usuário pediu, antes de voltar a construir, *"100% alinhado, sem pendências ou decisões pendentes"*. Três frentes: o documento, as telas e os testes.

## Nenhuma decisão pendente do usuário

As duas que restavam foram fechadas hoje, pelo usuário:

- **Variações de produto: a grade fica dentro do produto.** O cadastro global entra só com saldo por variação ou marketplace (design system §13).
- **Tags de produto seguem os marcadores: fora.** O hub deixou de listar *Tags de produtos* e as quatro telas *Marcadores…* (design system §12.1).

Tudo o que continua aberto é **construção com gatilho** — o quadro abaixo diz o que espera o quê. Se aparecer um "a decidir" em qualquer outro ponto deste arquivo sem `→ ✅ Resolvido` ao lado, é defeito do documento.

## 1. O documento dizia "em aberto" para o que estava decidido

- **17 perguntas** "decidir antes de construir" nos §9, §10 e §11, respondidas pelo §12 e pela rodada de 21/set — cada uma ganhou a resposta e onde ela está.
- **8 cabeçalhos com ⏳** de coisas prontas, aprovadas ou que viraram referência.
- Os "a decidir" das leituras dos prints de Configurações e **as listas de pendências de 21 e 22/set**, item por item: ✅ feito, ⏸ espera algo, ou ~~riscado~~ quando a decisão foi descartar.
- **§7** contava **31 telas; são 52** (mais o molde). **§4** dizia que faltava Caixa e Contas a Pagar. **§3** tinha ⬜ em cinco itens que já têm tela, e ganhou legenda.
- Design system: **§12.2** descrevia seis classes-gancho que não existem desde 28/set; a linha da Conferência no §12 ainda dizia "menu Estoque".

## 2. As telas: becos sem saída e uma trava no lugar errado

Achados por varredura, não por lista — detalhe e regras nas lições **§14.6** e na regra nova **§10.3** do design system.

| o quê | onde | agora |
|---|---|---|
| **19 botões** respondendo *"é a próxima tela a ser construída"* / *"a navegação só funciona no Lovable"* para telas que existem | 10 telas do Estoque; as listagens de Ordens de Compra e de Entrada de Notas **não tinham caminho para o próprio detalhe** | navegam |
| **Exclusão em massa sem senha** — a senha estava armada no aviso de "nada pode ser excluído", e o modal que exclui passava direto | Ordens de Compra, Depósitos, Endereços | senha no modal que exclui |
| Cancelar ordem de compra **já recebida** sem senha (catálogo `ocCancelaRecebida` estava `pronto:false`) | Ordens de Compra | pede senha e diz o que acontece com o estoque |
| **Incluir** dos 5 cadastros abria um registro existente **em modo leitura** — regressão do modo leitura de 28/set | Clientes, Fornecedores, Produtos, Vendedores, Lojas | `?novo=1` e `?editar=1` abrem em edição |
| Interface do usuário dizia *"não existe modo somente-leitura"* | Configurações | preferência nova: **Ao abrir um cadastro existente** — visualização (padrão) ou edição |
| *Clonar compra* e *Receber mercadorias* só avisavam | Ordem de Compra | clone em edição (`?clonar=1`); receber abre o modal na fila (`?receber=1`) |
| **Competência em massa** — pendência de 22/set | Caixa | "Alterar competência" na barra de seleção |
| **23 avisos prometendo "no fim da fase"** — prazo que venceu | 21 telas | "junto com Relatórios", sem data |
| Nota fora das conferíveis mostrava a 9051 com o breadcrumb dizendo outra | Conferência | breadcrumb diz a nota carregada |
| Hub prometia 4 telas de marcador + tags | Configurações | fora |

**Já estavam prontos e o documento não sabia:** parcelas na Ordem de Compra, totalizador no rodapé e *selecionados (R$)* no Caixa e em Contas a Pagar, coluna Origem no extrato.

## 3. Verificação

- Auditoria oficial da skill: **tudo limpo ✓** · `auditoria.py` estrita: **0 falhas reais em 53**.
- **15 suítes** em `_ferramentas/`, **1.373 asserções**, FALHAS: 0 em todas. Nova: `teste_becos.py` (110) — prova os destinos, as portas de entrada dos cadastros e a senha no modal certo.
- **Varredura de cliques nas 52 telas** (`_ferramentas/varredura_cliques.py`, nova): **1.605 cliques**, cada um com a tela recarregada — **zero erro de JavaScript, zero navegação para arquivo inexistente, zero aviso dizendo que uma tela existente não existe**. E os **318 controles da área principal** das 52 telas aceitam clique: nenhum coberto, nenhum fora de alcance. O que mora dentro de modal, painel e menu fechados é coberto pelas suítes dedicadas.

## O que está aberto — quadro único

Substitui as listas "Aberto" dos blocos anteriores.

**Próximo módulo: Vendas / Pedidos de Venda.** É a dependência da maior parte da primeira tabela.

**Espera um módulo que ainda não existe**

| item | espera |
|---|---|
| Contas a Receber (e *imprimir duplicata*) | Pedidos de Venda |
| Reservas: coluna *Reservado* e aba de reservas no Controle de Estoques | Pedidos de Venda |
| Desk Help (atendimento pós-venda) — desenho e menu | Pedidos de Venda |
| Configurações de estoque (estoque negativo, saídas, "editar quantidade lida na importação") | Vendas |
| Composição de Kit, kit derivado e a correção obrigatória de Inventário e Acerto | cadastro de Kit |
| Transportadora e o vínculo em Ordem de Compra e Nota de Entrada | desenho da Desk Flash (última de F2) |
| Usuários do sistema, Permissões de Usuários (com o verbo *ver*), permissão real em Metas e Vendedores, Guia de primeiros passos, "lembrar a última tela" | login (Usuários do sistema) |
| Integridade referencial e exclusão suave nos 12 pontos | Supabase |
| Menu lançar ↔ estornar; coluna Origem no Controle de Estoques | ledger de estoque real (Supabase) |
| Importar XML e o de-para `produto_fornecedor` | importação no servidor (Lovable) |
| Conciliação bancária e OFX | depois da F5 (os campos já existem) |
| Relatórios — imprimir/exportar das listagens, romaneio, Giro de Estoque, Necessidades de Compra | módulo de Relatórios, sem data; os botões avisam |
| Cadastro global de variações; estoque de segurança; valor da NF × pagamento integrado | saldo por variação / marketplace |
| Reordenar por arrastar (estágios do funil) | CRM |

**Espera algo de fora**

| item | espera |
|---|---|
| Devolução ao fornecedor, NF-e da baixa por perda, Operação Fiscal Padrão, homologação × produção | módulo fiscal (NF-e) |
| Consulta de CNPJ na Receita | certificado digital |
| Recusa parcial na doca | confirmação do contador |

**Adiado por decisão do usuário**

| item | quando |
|---|---|
| Dividir o `pagina-molde-referencia.html` | fim do projeto (29/set) |
| Central de ajuda e agente tipo Lis | fim do projeto (21/set) |
| Painel de filtros avançados do Controle de Estoques | quando alguém sentir falta (29/set) |
| Datas do mock relativas a hoje | quando incomodar (28/set) |

**Fora do sistema por decisão:** marcadores e tags (22, 29 e 30/set — print com marcador se ignora, é regra de leitura) · cadastro rápido de pessoa **no lançamento do Caixa** (22/set; no Pedido de Venda ele **entra**, ver design system §11.2) · tabela `pessoas` unificada (21/set) · **lista de preço** (30/set, com gatilho).

## Como a próxima sessão deve começar

1. `device_list_dir` e comparar com o esperado — os 53 `pagina-*.html`, os 2 `.md` e as **15** suítes.
2. **`python3 selo.py`** — ele diz o que está provado e o que precisa rodar. `--rodar` executa só isso e sela o que passar. Não rodar tudo à mão: o selo existe para isso (§14.7 do design system).
3. Antes de dar um módulo por pronto, `varredura_cliques.py` (~10 min) — essa fica fora do selo, por ser de fechamento.
4. Ler **§10.3** (botão que leva a outra tela, parâmetros de URL), **§14.6** e **§14.7** do design system.
5. Abrir Vendas / Pedidos de Venda pelo protocolo de sempre: prints do Olist → barganha → construção.

**A pasta `Claude outputs` continua sendo lixo de app — ignorar.**


---

# 30/set/2026 — o selo de verificação

**O que mudou no jeito de verificar.** A verificação completa passou de 20 minutos: 15 suítes + 2 auditorias, quase tudo repetindo prova já feita. Agora existe `_ferramentas/selo.py`, que guarda o SHA-256 de cada arquivo coberto por cada suíte e **só roda o que deixou de estar provado**. Detalhe e as três decisões no **§14.7** do design system.

- Mexer numa tela de detalhe acordou **8 suítes e deixou 7 seladas**; as que varrem a pasta rodaram em **1 tela em vez de 52**. Rodada completa ~7 min, seletiva 18 s.
- A cobertura **sai do código de cada suíte**, não de lista escrita à mão, e foi **provada por observação**: cada suíte rodou com o `Page.goto` instrumentado e nenhuma abriu tela fora da sua cobertura.
- O selo segue também as ferramentas: suíte, `auditoria.py`, auditoria oficial da skill ou `alvos.py` mudaram → o que depende delas volta a rodar.
- Estado selado hoje: **15 suítes · 2.510 asserções · 2 auditorias**, todas verdes.

**Um achado na primeira rodada:** o `teste_caixa.py`, verde ontem, reprovou hoje — ele fecha o período financeiro em *hoje* e exigia dias livres no calendário do mês corrente. Em 30/set, último dia do mês, sobraram zero. Passava 29 dias por mês e reprovava no trigésimo. Corrigido no teste (a tela estava certa); lição no §14.7.

**Vendas / Pedidos de Venda:** prints recebidos em 30/set (dois lotes). Nada construído — a barganha vem antes.


---

# 30/set/2026 (tarde) — três decisões antes de abrir Pedidos de Venda

O usuário mandou 27 prints de **Vendas → Pedidos de Venda** e fechou três pontos que apareceram neles. Nenhuma tela construída — a barganha do módulo ainda não aconteceu.

## 1. Lista de preço: fica de fora, e o campo órfão saiu junto

O cadastro já estava mapeado desde 16/set (§13, aba *cadastros*). O que falta é o **caso de uso**, não o desenho: produto pertence a uma loja só (preço por frente sai do produto), **preço promocional já existe por produto**, e não há operação de atacado no projeto. O markup de marketplace — o caso que de fato vem — é `valor_taxas`/`valor_liquido` do §12.4, não lista de preço.

**Gatilho:** a primeira venda com preço diferente por cliente ou por canal. `customers.lista_preco_id` é aditivo.

**E o Clientes tinha um campo apontando para esse cadastro inexistente** — `inputListaPreco`, com Padrão/Atacado/Varejo escritos na mão e nenhuma tela lendo. Removido. Na mesma passagem, o id `inputListaPreco` que tinha sobrado num campo de **Prazo médio de entrega** em Fornecedores virou `inputPrazoEntrega`: id herdado de clonagem que descreve outro campo é bomba armada para o primeiro `getElementById` que acreditar nele. Detalhe no §13 do design system.

## 2. Marcadores: print com marcador se ignora — regra, não exceção

Decisão do usuário: *"todo o ecossistema do Olist tem, então será inevitável print com marcadores; o que vamos fazer é ignorar essa parte."* Vale para Pedido de Venda e para todo módulo futuro, sem reabrir a discussão a cada lote de prints. **Ressalva única:** badge que o sistema calcula sozinho (o `1ª venda` do print) não é marcador — é derivado, como *atrasada* em Contas a Pagar. Ver design system §12.1.

## 3. Cadastro rápido de pessoa: entra no Pedido de Venda — e uma contradição minha, corrigida

Em **16/set** eu registrei o cadastro rápido como componente compartilhado a construir; em **22/set** eu o descartei. As duas linhas conviveram oito dias neste arquivo. A segunda foi decidida olhando só o lançamento do Caixa e ficou escrita como decisão geral, que não era.

A régua que faltava: **entra onde a pessoa é parte obrigatória do documento, não entra onde ela é anotação.** Pedido de Venda e Conta a Receber: entra. Lançamento do Caixa: continua fora, pelo motivo certo. As três amarras que matam o risco de formulário duplicado (bloco no próprio documento com a mesma definição de campos, conjunto mínimo, registro nascendo marcado como incompleto com filtro na listagem) estão no **§11.2 do design system**.

## Lição de processo: decisão que contradiz outra precisa citar a que ela substitui

As duas linhas sobre cadastro rápido não se contradiziam por descuido de escrita — a de 22/set **não sabia** da de 16/set. É a mesma família do §14.6 (*documento que diz "em aberto" para o que foi decidido*), vista do outro lado: lá a pergunta não sabia que já tinha resposta; aqui a resposta nova não sabia que já existia outra. **Regra: ao decidir algo que já foi decidido antes, achar a decisão anterior e escrever qual das duas vale.** Uma busca no arquivo antes de escrever a decisão custa menos que oito dias de contradição.


---

# Barganha de 30/set/2026 — Vendas / Pedidos de Venda, antes de construir

27 prints do Olist, cinco pontos negociados. **Nenhuma tela construída ainda.** Isto é o contrato do módulo.

## 1. O funil — nossos nomes, a sequência que a lei impõe

O usuário levantou, com razão, que o Olist embola o processo. Mas parte do que parece passo a mais **é sequência fiscal, não burocracia**: o `faturado` fica antes de `pronto para envio` e `enviado` porque **a mercadoria não circula sem a nota**. O DANFE viaja com a carga; nota emitida depois da saída é mercadoria desacompanhada. É o espelho do art. 204 do RICMS/SP que já citamos no §3 item 23 (nota sem circulação é vedada — circulação sem nota também).

**Correção registrada:** o usuário havia proposto *"a expedição confirma o faturamento"*. É o inverso — **fatura, depois expede**. Ele mesmo reconheceu ("posso ter me equivocado na última frase"). A baixa física continua na expedição, como ele propôs.

| Olist | nosso nome | o que dispara |
|---|---|---|
| em aberto | **Em aberto** | pedido existe → **reserva o estoque** · **nasce a conta a receber** |
| aprovado | **Aprovado** | pagamento confirmado |
| preparando envio | **Separação** | tela de F4 (pick and pack) |
| — | **Etiquetagem** | tela de F4 — o Olist junta com a anterior; nós temos duas telas e dois operadores |
| faturado | **Faturado** | nota emitida. **Hoje marcado à mão, sem emitir nada.** Libera a comissão |
| pronto para envio | **Pronto para envio** | embalado, esperando coleta |
| enviado | **Enviado** | saiu → **baixa física do estoque** |
| entregue | **Entregue** | fim |
| cancelado · devolução | **Cancelado** · **Devolução** | terminais; cancelado devolve a reserva |

**Entre `faturado` e `enviado` o estoque está fiscalmente vendido e fisicamente presente.** É divergência de **tempo, não erro** — a mesma ressalva contábil já aceita na janela de conferência (§3 item 19).

**`Faturado` nasce agora, mesmo sem NF-e**, por dois motivos: a regra de comissão *"liberação integral no faturamento"* já está construída em Vendedores e precisa desse estado; e refazer o funil depois custa mais que mantê-lo. Não é aba vazia para sempre (§12.10) — é alcançada por ação manual desde o primeiro dia.

**Consequência de layout a resolver na construção:** 10 situações não cabem como abas a 1440px. O Olist já precisou de `mais ⋯`. Decidir na tela, não aqui.

## 2. Reserva de estoque — a regra

- **Pedido criado reserva**, venha do site, do balcão, do vendedor ou de vitrine. Bate com a definição de `reservado` já escrita no §3 item 19 ("em pedido confirmado, não expedido") e mantém o invariante `físico = a_endereçar + disponível + reservado + bloqueado`.
- **Cancelado ou não pago devolve para `disponivel`.**
- **Baixa física só em `enviado`.** Pagar, separar e etiquetar não tiram nada do físico — a mercadoria ainda está no galpão.
- **Reserva sem pagamento expira em 3 dias** (decisão do usuário), volta para disponível sozinha e o pedido vai para cancelado. Vira parâmetro em **Configurações → Estoque → Parâmetros de estoque**, ao lado dos outros três limiares, chave `reservaExpiraDias` (padrão 3). **A mesma regra vale para carrinho abandonado** quando as vitrines existirem (F3) — registrado agora para nascer junto.
- **Sem knob de "bloquear venda sem estoque".** O Olist faz disso configuração; aqui a reserva é regra dura. O ERP é nosso.

## 3. Conta a receber nasce com o pedido

Com dois ajustes sobre a proposta original:

- **A pendência aparece em Contas a Receber, não no Caixa.** São duas tabelas (§12.1): título é o direito, movimento é o dinheiro. O Caixa só recebe lançamento **na baixa** (§12.7). Título aparecendo no Caixa ao nascer faria o saldo mentir.
- **Cancelar o pedido cancela o título, não apaga** — mesmo mecanismo de Contas a Pagar.

O gatilho nasce como parâmetro (*ao criar · ao aprovar · ao faturar*), fixo em **ao criar**. Na venda do site o título nasce e é baixado quase junto (pagamento no checkout, F3); quem fica pendente de verdade é balcão e vendedor, que é onde a visibilidade importa.

## 4. `orders.loja_id` — automático, editável

Preenchido pela origem do pedido, alterável à mão. **Destrava `stores.deposito_padrao_id`**, construído em 15/set e até hoje sem consumidor: a cadeia vira **loja → depósito padrão dela → editável**, melhor que o Olist, onde o depósito é escolhido do zero.

**Um pedido, uma loja** (aprovado pelo usuário). Como produto pertence a uma loja só, a busca de itens filtra pela loja do pedido, e venda de balcão com peça de duas frentes vira dois pedidos. A separação e a nota exigiriam isso de qualquer forma.

## 5. Desconto nos dois níveis

Confirmado pelos prints do painel do item (**Preço lista → Desconto % → Preço unitário → Preço total**) e do cabeçalho (Total produtos 250,00 · desconto 10% · Total da venda 225,00).

**Regra para os dois não se atropelarem:** o desconto do item forma o preço unitário e soma em *Total produtos*; o desconto do pedido incide sobre *Total produtos* e produz o *Total da venda*. **Nunca os dois sobre a mesma base.**

**Comissão é por item.** O painel do item tem abas próprias — *dados do item · comissões · impostos*; o pedido consolida. Encaixa no que Vendedores já tem construído: liberação parcial por parcela · integral no faturamento · integral após a primeira parcela, com alíquota fixa ou conforme descontos.

## 6. Como ler print do Olist, daqui em diante

O usuário perguntou se espelhar o Olist nos deixaria com telas sem uso. **Não deixa, e a disciplina já tem histórico:** marcadores (7 telas lá), tags, listas de preço, cadastro rápido no Caixa, as abas *Emitidas/Processando/Agendado* e a tabela `pessoas` — tudo recusado. O hub de Configurações usa **as nossas abas**, não as deles.

**O teste continua sendo o do §12.10: algum evento do nosso sistema produz esse estado ou essa tela?** Se não produz, fica fora. E a contrapartida, aprendida hoje: **antes de chamar um passo do Olist de burocracia, verificar se não é exigência legal** — foi o caso do `faturado`.

## 7. Propostas comerciais — FORA, com gatilho

O usuário levantou construí-las agora, "para estarem lá quando precisar". **Decidido não construir**, e ele concordou: *"realmente não faz sentido, e caso algum dia for viável podemos construir."*

O motivo não é o custo de construir, é o de **manter**: cada tela entra na varredura do bloco compartilhado, nas 15 suítes, nas duas auditorias, no selo e em toda propagação futura. A 54ª tela precisa se pagar. E a operação da Desk não tem proposta — Desk Shope é e-commerce (o cliente compra, não pede orçamento), Brands é varejo, Tech vende e conserta. Proposta é ciclo B2B com negociação, que não aparece em lugar nenhum do projeto.

**Gatilho para entrar:** a primeira venda que precise de aprovação do cliente antes de virar pedido. Quando entrar, custa `orders.proposta_id` anulável — aditivo, não refaz nada. Mesma jogada do `empresa_id` (§3 item 22) e do `origem` da Devolução.

**Consequência imediata:** sem propostas, **todo pedido é pedido de verdade**, e por isso `em aberto` já reserva. Se um dia a proposta existir, **proposta não reserva** — escrito agora para não ser descoberto depois.

## 8. Pedido sem saldo disponível: BLOQUEIA

Decisão do usuário: *"bloqueia, melhor que evita transtornos com cliente e reembolsos desnecessários."* — e ele está certo pelo motivo mais caro: vender o que não existe custa reembolso, reputação e, em marketplace, penalidade.

- **Só acontece em balcão e vendedor.** A vitrine nunca cai nesse caso: ela já filtra por saldo **disponível endereçado** (§3 item 19).
- A mensagem diz **quanto existe**, não só que não dá — mesmo padrão da transferência entre CNPJs e da exclusão de OC já recebida.
- **Venda sob encomenda** nasce como parâmetro existindo e **desligado**, para o dia em que a Desk quiser aceitar pedido de mercadoria que ainda vai chegar.

---

# 30/set/2026 (noite) — Pedidos de Venda entregue: duas telas, e o que elas provaram

A barganha acima virou tela no mesmo dia. **As duas telas nasceram juntas de propósito:** listagem sozinha teria dois botões sem destino — *Incluir pedido* e *abrir o pedido* — que é exatamente o beco sem saída que a varredura de 29/set acabou de eliminar. **Tela que cria botão sem destino não está pronta, está adiada.**

| arquivo | o que é |
|---|---|
| `pagina-vendas-pedidos.html` | a listagem — 10 situações + Todos, período pelas duas datas, rodapé que exclui cancelados |
| `pagina-vendas-pedidos-detalhe.html` | a página do pedido — itens, comissões, impostos, bloqueio por saldo, cadastro rápido |

Clonadas de `pagina-estoque-ordens-compra*.html`, que é o par mais próximo em forma: listagem com abas contadoras e formulário com itens e totais. **Clonar acelera e cobra o preço na mesma moeda** — três defeitos herdados apareceram, todos do mesmo tipo (pedaço do original que não foi renomeado):

- `dfDataCompra` / `dfDataPrevista` ainda ligados no lugar de `dfDataVenda` / `dfPrevisto`;
- um **segundo `bindMenuAcoes` no mesmo `#menuMaisAcoes`** — o bug documentado de "o dropdown abre e se fecha no mesmo clique";
- `inputListaPreco` sobrevivendo num campo que hoje é "Prazo médio de entrega" em Fornecedores.

**Regra que sai disto: depois de clonar, procurar no arquivo novo todo identificador que cite o domínio do arquivo velho.** Os três foram achados por busca de nome, não por leitura linha a linha.

## O que o navegador pegou e a leitura não pegaria

`[].slice.call(itensSelecionados)` devolvendo `[]`: `Set` **não é** array-like. O código lê certo, roda errado. Trocado por `Array.from()` em 4 pontos. **Leitura de código não substitui execução** — e foi por isso que a suíte nova nasceu antes do commit, não depois.

## A tag literal no modal, pela segunda vez

`<b>` escrito dentro de texto que vai para `confirmModalTexto.textContent` aparece como `</b>` na cara do usuário. Corrigido à mão em 29/set numa tela; **voltou em 30/set** na página do pedido.

Da segunda vez virou **checagem 10 do `auditoria.py`**, e não outra correção à mão: ela recorta o argumento de texto de `avisar()`, `confirmarAcao()` e `abrirModalConfirmacao()` até onde a função executora começa, e reprova tag escrita ali — deixando livre o `innerHTML` de dentro do callback, que é onde tag é legítima. Provada nos dois sentidos (defeito injetado reprova; as 55 reais passam).

**O padrão, que já apareceu três vezes neste projeto: erro que volta não pede correção, pede verificação.**

## Estado no fim do dia

- **54 telas** + o molde de referência. Todas passam nas duas auditorias.
- **16 suítes, 2.706 asserções sob selo, 0 falhas.** A suíte nova (`teste_pedidos.py`, 140 asserções) protege as **decisões** da barganha, não o desenho: reserva que nasce e volta, expedido que não se exclui, mensagem de saldo que diz quanto existe, os dois níveis de desconto em bases diferentes.
- **Prova de cobertura repetida para a suíte nova**, como o `LEIA-ME` manda: cobertura declarada e telas realmente abertas deram exatamente as mesmas duas.
- **Varredura de cliques: 1.676 cliques em 54 telas, 0 erro de JS, 0 navegação para arquivo inexistente, 0 aviso mentindo que uma tela não existe.**

**Fica aberto só o que depende do usuário:** aprovar o módulo para virar prompt do Lovable. Nenhuma decisão de produto pendente.

---

# 02/out/2026 — o pedido anda: funil, cliente e limite de crédito

O usuário abriu um pedido em *Separação* e não achou como mandar para etiquetagem. Tinha razão: o menu *Mais ações* oferecia *Enviar para separação*, e clicar nisso abria um **aviso** explicando que Logística moveria o pedido um dia. Quatro das seis ações do menu eram assim.

## Barganha — duas decisões

**1. Quem anda o funil.** Separação, Etiquetagem e Expedição são telas de F4 e não existem. Três caminhos estavam na mesa: só o botão de próximo passo (seguro, mas pedido parado na situação errada só sai com acesso ao banco), só *Alterar situação* livre (flexível, sem nenhuma barreira contra pular o faturamento), ou os dois. **Decidido: os dois.**

- **Botão de próximo passo** no cabeçalho, um passo por vez, na ordem do funil. O rótulo é o **efeito**, não o nome da situação seguinte: *Faturar* avisa que libera a comissão, *Confirmar envio* avisa que é a baixa física e que dali em diante o caminho é devolução. Confirma e registra; **não pede senha** — é operação normal.
- **Alterar situação** vira painel lateral com as 10 situações **na ordem do funil**, para correção: pular etapa que aconteceu fora do sistema, ou voltar passo dado por engano. **Pede senha**, porque situação mexe em comissão, em conta a receber e em saldo. Voltar de *Enviado* avisa, no próprio texto da confirmação, que o estoque **não volta sozinho** — isso é devolução.
- Quando as telas de F4 existirem, elas viram o caminho normal e o botão continua como atalho.

**2. Limite de crédito.** O roadmap já tinha decidido que *"Validar limite de crédito"* é configuração **por forma de recebimento** (crediário valida, dinheiro não). **Decidido: bloqueia o salvamento quando a forma valida e o pedido estoura o disponível** — mesma forma do bloqueio de saldo, com a mensagem dizendo os números (limite, usado, disponível, este pedido), não só que estourou. Em Pix ou dinheiro o painel mostra tudo e não trava nada.

**Composição do usado, registrada:** contas a receber em aberto **mais** pedidos reservados ainda não faturados. Disponível real = limite − usado. O usuário descreveu isso como *"contas a pagar"* — do lado dele é o que o cliente deve; do nosso é **conta a receber**. Mesmo número, nome diferente, e o sistema usa o nosso.

## Construído

| o quê | onde |
|---|---|
| botão de próximo passo + 7 transições | `pagina-vendas-pedidos-detalhe.html`, cabeçalho |
| painel *Alterar situação* (10 situações, com senha) | idem, *Mais ações* |
| **Clonar venda**: confirma e abre pedido novo **já preenchido** (`?clonar=<nº>`) | idem |
| painel *Últimas vendas do cliente* (abas Produtos/Financeiro, 10 últimas) | idem, links do cliente |
| painel *Limite de crédito* + bloqueio no salvamento | idem |
| menu *mais* das abas, que abria invisível | `pagina-vendas-pedidos.html` |

**Duas chaves novas no catálogo de senhas:** `pedidosPasso` (nasce **sem** senha) e `pedidosSituacao` (nasce **com**). `pedidosClona` entra sem senha, só para registro.

## O que isso custou — e o que virou verificação

O menu *mais* abria no DOM e o usuário não via nada: `overflow:hidden` no container das abas recortava o painel. **O teste passava em cima do bug**, porque afirmava `classList.contains('open')`. A asserção virou `elementFromPoint` — e, levada para o `teste_dropdown_todas.py`, que roda nas 55 telas, acusou mais dois casos no mesmo minuto (falsos positivos, dropdown dentro de painel fechado), o que obrigou a segunda metade da regra.

Outros três: `linkUltimasVendas` ficou com **dois listeners** (o painel novo e o `location.href` velho) — terceira vez desse defeito no projeto; saldo e limite estourando juntos mostravam **só o segundo motivo**, porque cada um chamava `avisar` por conta própria; e o `auditoria.py` só imprimia veredito com 2+ arquivos, fazendo o selo reprovar uma auditoria limpa. Os três estão em §14.9 do design system.

## Estado

- **54 telas.** Duas auditorias limpas nas 55 (as 54 + o molde).
- **16 suítes, 2.812 asserções sob selo, 0 falhas.** O `teste_pedidos.py` passou de 140 para **246** asserções — 6 seções novas, todas sobre as decisões acima.
- **Varredura de cliques: 1.677 cliques em 54 telas, 0 falhas.**

**Anotado para o próximo passo:** quando F4 (Logística) entrar, *Separação*, *Etiquetagem* e *Expedição* passam a mover o pedido, e o botão de próximo passo vira atalho — nada do que foi construído aqui se perde, mas o texto de cada passo precisa deixar de falar em "fila do galpão" como promessa e passar a apontar a tela.

---

# 02/out/2026 (noite) — as abas de situação saíram, e a devolução saiu com elas

O usuário pediu para remover o menu *mais* das abas: *"acho que ficou estranho"*. E acrescentou a leitura dele: *"pelo que entendi mostrou só pq tem os em devolução... vamos ter um módulo exclusivo pra isso"*.

**A leitura estava meio certa.** O *mais* não apareceu por causa da devolução — apareceu porque as abas não cabem. **Medido: 11 abas pedem 1.537px num espaço útil de 1.024px.** Tirando a devolução, 10 abas ainda pedem 1.395px. Espremendo tudo — sem bolinha colorida, padding menor, fonte menor, contador menor — chega a 1.050px, ainda 26px acima, e qualquer rótulo novo quebraria de novo.

Com os números na mesa, três saídas: duas linhas fixas, abas espremidas numa linha, ou situação virar filtro suspenso. **O usuário escolheu o filtro suspenso.**

## 1. Situação virou o terceiro filtro

Ao lado de Loja e Vendedor. Os contadores foram junto, **dentro da lista**, porque eram o que a aba dava de graça — e são remontados a cada abertura, já que dependem do período, da loja e do vendedor. O menu ganhou **teto de altura próprio** (as 10 opções são contadas e sabidas; o teto de 240px do componente compartilhado cortaria três) e passou a **medir o espaço antes de abrir**, como manda o design system.

**Custo aceito:** trocar de situação passou de um clique para dois, e os números deixaram de ficar à vista na tela — ficam a um clique. **Ganho:** a barra de filtros virou uma linha só, sem nada escondido atrás de um *mais*.

## 2. Devolução não é situação de pedido de venda

O usuário disse que devolução terá módulo exclusivo e que o módulo de Vendas pode ficar sem ela. **Registrado como decisão de modelo, não só de tela:**

> **Devolução é documento próprio**, do módulo de Devoluções, apontando para o pedido. O **pedido devolvido mantém a situação que tem**.

O motivo é mais forte do que arrumação de tela: marcar o pedido como *devolução* **apagaria a venda que aconteceu**. O faturamento aconteceu, a comissão foi liberada, a baixa física saiu — nada disso deixa de ser verdade porque a mercadoria voltou. E devolução pode ser **parcial**, o que uma situação única não sabe representar.

**Consequências já aplicadas:** sai da listagem (9 situações + Todas), do funil e do painel *Alterar situação*; `SIT_COM_SAIDA` passa a ser `['enviado','entregue']`; o CSS das classes `sit-devolucao`/`bs-devolucao` saiu junto, porque classe sem uso faz quem vier depois achar que a situação existe. As frases que apontam a devolução como caminho (cancelar ou excluir pedido expedido, voltar de *Enviado*) **continuam** — agora apontando para o módulo.

**Fica para o módulo de Devoluções:** `devolucoes` com `pedido_id`, data, motivo (vem de *Motivos de Devolução*, já no menu), itens e quantidades devolvidas, e o que a devolução faz com estoque (entrada em depósito de devolução, não no disponível direto) e com a conta a receber.

## Estado

- **54 telas**, duas auditorias limpas, **16 suítes · 2.822 asserções sob selo · 0 falhas** (o `teste_pedidos.py` foi a 256).
- **Varredura: 1.682 cliques em 54 telas, 0 falhas.**

---

# 02/out/2026 (madrugada) — Contas a Receber: a F5 fecha

A última peça da F5, travada esperando Vendas desde 16/set. Os prints (lote 3, §11) já estavam destrinchados e as cinco perguntas já respondidas, então não houve material novo a pedir — só duas decisões a fechar.

## Barganha — duas decisões

**1. Venda a prazo: o PEDIDO define as parcelas.** O Pedido de Venda ganhou *Condição de pagamento* (à vista · 2x · 3x · 6x · 12x) com prévia dos vencimentos, e salvar faz nascer **N contas a receber**, uma por parcela, ligadas ao pedido. É onde a decisão realmente acontece — quem combina o prazo é o vendedor, na venda. A alternativa (um título que se parcela depois) deixava o limite de crédito do cliente consumido pelo valor cheio num vencimento só até alguém lembrar de dividir.

**A regra dos centavos, registrada:** a divisão é em centavos e **a sobra vai toda para a primeira parcela**. 1.000,00 em 3x são 333,34 + 333,33 + 333,33, nunca 333,33 três vezes. Espalhar a diferença produz parcelas de centavos diferentes que o cliente não entende e o extrato não casa. A regra vive em dois lugares (o mock de Contas a Receber e o plano do Pedido) e os dois estão sob teste.

**2. Cliente com conta vencida não compra de novo.** Terceira trava do salvamento, ao lado de saldo e limite. É diferente do limite: ali o cliente tem saldo, aqui ele tem conta vencida. A tolerância é `PARAM.bloquearPedidoAtrasoDias`, nascendo em **1** — e com **0 a trava desliga**, porque número que decide bloqueio não nasce dentro de um `if`. **O aviso aparece na abertura do pedido**, não só ao salvar.

## Construído

| o quê | onde |
|---|---|
| listagem, com quatro valores por linha e Origem linkando o pedido | `pagina-financas-contas-receber.html` |
| página da conta, com taxas, líquido gravado, antecipado e duplicata | `pagina-financas-contas-receber-detalhe.html` |
| condição de pagamento + prévia das parcelas | `pagina-vendas-pedidos-detalhe.html` |
| bloqueio por conta em atraso + aviso na abertura | idem |
| categoria **Juros e multas recebidos** (id 21) | as 6 telas que carregam `CATS_FIN` + o cadastro de Categorias financeiras |

**A taxa retida é o achado que o §11 já previa e agora tem mecânica:** ela **quita o título sem entrar no Caixa**. Receber o líquido de 8.167,52 numa conta de 8.975,30 sem lançar os 807,78 de taxa deixaria 807,78 de saldo eterno numa conta que acabou.

## Dois defeitos que o clone revelou — um deles antigo

**A pill de período mentia em Contas a Pagar desde 23/set:** a lista abria filtrada pelo mês corrente e o controle dizia *"Sem filtro de período"*. Corrigido nas duas telas. **Contas a Receber abre sem filtro de período, ao contrário do a pagar** — a pergunta é outra: conta vencida há dois meses continua sendo dinheiro a cobrar e sumiria da tela.

**O rename em bloco inverteu o sentido dos lançamentos** (baixa escrevia saída, estorno escrevia entrada) e **inventou um link quebrado** (`pagina-cadastros-clientees.html`), além de atropelar nomes compartilhados — grupos de categoria e o item de menu *Contas a Pagar*. A auditoria oficial pegou o link; o sentido dos lançamentos só caiu porque virou asserção. Está em §14.12 do design system.

## Pendência honesta, anotada

**`reservaExpiraDias` e `bloquearPedidoAtrasoDias` existem no `PARAM` e não existem em tela nenhuma de Configurações.** A nota da listagem de Pedidos já diz *"Configurações → Parâmetros de estoque"* para o primeiro, e lá ele não está. **São dois parâmetros apontando para um lugar que não os mostra** — a mesma promessa falsa do campo órfão de 30/set. Entram na próxima passagem por Configurações, junto com a tela de **Formas de recebimento**, que é de onde `validar limite de crédito` e a tarifação deveriam vir.

## Estado

- **56 telas** + o molde. Duas auditorias limpas nas 57.
- **17 suítes · 2.996 asserções sob selo · 0 falhas.** A suíte nova (`teste_receber.py`, 116 asserções) protege o que separa o receber do pagar, que é exatamente o que um clone apaga sem fazer barulho.
  > **Correção de 06/out/2026:** as contagens desta linha estão infladas. O contador do `selo.py` somava `count('  ok   ') + count('  ok ')` e, como o primeiro **contém** o segundo, dobrava cada asserção. O `teste_receber` tem **61**, não 116. O total real sob selo, medido depois do conserto, é **2.109** em 21 suítes. Ver `_ferramentas/LEIA-ME.md`, §"O contador estava errado nas duas direções".
- **Varredura de cliques: 1.908 cliques em 56 telas, 0 falhas.**
- **F5 fechada.** O que sobra dela é a dívida de Configurações acima, não módulo.

---

# 02/out/2026 — três padrões soltos, e um bug que eu criei

O usuário abriu as telas novas e viu três coisas fora do lugar. Duas eram padrão não escrito; a terceira era defeito meu.

**1. "Mais ações" mudava de posição conforme a tela.** Decidido: **ações azuis → Editar → Mais ações**, sempre, com o dropdown por último. Corrigido em *Caixa e Bancos* e nas duas páginas de conta; as outras dez já estavam certas.

**2. Filtros e abas de situação trocavam de ordem entre módulos.** Decidido: **filtros em cima, situação com as bolinhas embaixo** — a ordem da leitura, primeiro restringe o conjunto, depois escolhe o recorte. Corrigido em Contas a Pagar e Contas a Receber; as de Estoque já faziam assim.

**3. O menu lateral duplicava "Contas a Receber" — culpa do rename em bloco de ontem.** Eu consertei o item atropelado só na **listagem** e não no **detalhe**: lá o módulo *Contas a Pagar* virou um segundo *Contas a Receber*, e **sumiu do menu**. Como os dois itens apontavam para arquivo existente, nenhuma checagem de link quebrado acusava.

Virou a **checagem 11** do `auditoria.py` — item de menu repetido dentro do mesmo flyout — e ela **achou na hora um segundo caso que eu não tinha visto**: *Clientes* duplicado no menu de Cadastros, no lugar de *Fornecedores*. O mesmo erro, duas vezes, em telas diferentes.

**Consertar à mão o caso que o usuário apontou teria deixado o outro em pé.** É o mesmo padrão de §14.9: erro que volta não pede correção, pede verificação.

## As três viraram asserção que varre a pasta

Não lista de telas escrita à mão — lista escrita à mão foi o que fez "8 telas com o problema" virar 23 em setembro. As três checagens abrem as 56 telas e conferem: a posição do *Mais ações*, a ordem das duas linhas, e rótulo de menu repetido. **Inconsistência não aparece lendo uma tela — só comparando duas.**

**Estado:** 56 telas, duas auditorias limpas nas 57, **17 suítes · 3.002 asserções sob selo · 0 falhas**.

---

# 02/out/2026 — F4 Logística: a barganha antes da primeira tela

O usuário mandou 39 prints do Olist (Separação, Imprimir separação, Expedição) e, em vez de pedir cópia, descreveu o fluxo que ele quer. Pediu para eu confrontar com o do Olist e dar opinião honesta. O que saiu da conversa não é o fluxo dele nem o do Olist.

## O fluxo fechado

| etapa | o que acontece | o que dispara |
|---|---|---|
| Pagamento confirmado | **manual:** dropdown pergunta se vai para a separação · **vitrine:** automático após pix/cartão | entra na fila |
| **Separação** | só cliente, pedido, produto, **localização** e quantidade — sem valores, sem descontos | reserva mantida |
| **Conferência de Saída** | digita a quantidade por item · escolhe embalagem · imprime etiquetas · **emite a NF** | `faturado` · divergência vira ajuste |
| **Expedição** | agrupa pedidos num romaneio e confirma a saída do galpão | **baixa física** · faturamento do dia |

**O operador da separação não vê dinheiro.** Foi a primeira coisa que ele pediu e está certa: valor na tela de separação só serve para vazar margem para quem não precisa dela.

**"Etiquetagem" virou "Conferência de Saída".** O nome dele descrevia o acessório (imprimir etiqueta) e escondia o que a etapa faz de importante, que é conferir. E ganha simetria com a *Conferência de Compra*: entra conferindo, sai conferindo.

**A NF sai na Conferência de Saída, não na Expedição.** Mantém a ordem fiscal fechada em 30/set: a nota acompanha a mercadoria, e a mercadoria só está pronta quando a conferência fechou.

**A conferência usa o padrão da Entrada de Notas:** lista de itens e um campo de quantidade que **nasce vazio**. Campo pré-preenchido com o número esperado não é conferência, é confirmação — a pessoa dá Enter em tudo.

## A decisão que mudou de dono: a falta

Eu defendi que a falta precisa virar acerto de estoque automático, porque "se o item não estava lá, o saldo já estava errado antes, e o próximo pedido bate na mesma parede".

**O usuário recusou o automático, com um motivo que eu não tinha considerado:** a divergência pode ser erro do separador ou erro de contagem do conferente — e aí o saldo estava certo, e a baixa automática o corrompe. Ele propôs um **pedido de acerto aguardando reconferência de estoque**, com um responsável analisando antes de autorizar a baixa.

**Ele está certo, e tem um argumento a mais na nossa própria tela:** os motivos de saída do Acerto carregam `fiscal: 'nfe'`. Acerto automático por perda cria **obrigação fiscal** a partir de uma contagem apressada.

O ajuste que entrou em cima da proposta dele: **quem fecha a reconferência escolhe a causa, não responde sim/não** — item ausente (gera o acerto), erro de separação, erro de conferência. Só a primeira movimenta estoque. Fechar tudo como "acerto" apagaria a única informação útil que a divergência produz, que é saber qual das três acontece mais. Está em **§14.14** do design system.

**Ponto meu que ficou:** o crédito de devolução não pode ser automático — CDC art. 35, a escolha entre restituição, crédito e reenvio é do consumidor. O pedido guarda a escolha como pendência, com restituição sugerida quando já pago.

## Ordem de construção

**Separação → Conferência de Saída → Expedição.** Nessa ordem porque cada uma consome o estado que a anterior produz, e porque a Separação é a única que dá para testar sem as outras duas existirem.

---

# 02/out/2026 — Separação, e um defeito que estava comendo os avisos do sistema inteiro

A primeira tela da F4. Duas: a **fila** (`pagina-logistica-separacao.html`) e a **ficha do pedido** (`pagina-logistica-separacao-detalhe.html`), com a folha de impressão junto.

## O que a tela faz, e o que ela se recusa a fazer

**Não mostra valor nenhum.** Não é campo escondido: a tela nunca carregou preço. Foi a primeira coisa que o usuário pediu, e é por isso que a ficha não reaproveita a página do Pedido de Venda — reaproveitar traria tudo junto, e aí esconder vira trabalho permanente. A asserção varre o texto renderizado das duas telas e da folha impressa procurando `R$`.

**Os itens saem na ordem do ENDEREÇO, não na ordem do pedido.** Separar na ordem em que o cliente escolheu faz o operador atravessar o galpão de ida e volta. É `PARAM.separacaoOrdemPorEndereco`, porque galpão pequeno não precisa.

**Bipar coleta o item inteiro; falta se declara com a mão.** O operador está com a caixa, não com o mouse. Mas a falta é a única coisa ali que vira divergência de estoque — ela não pode acontecer por acidente de leitor.

**O campo da quantidade encontrada nasce vazio**, e **item sem resposta trava a conclusão**. Campo pré-preenchido com o esperado não é conferência, é confirmação; e item intocado não é item sem falta, é item que ninguém olhou. Responder "zero" leva meio segundo — descobrir a falta na conferência, com o cliente esperando, não.

**"Separar o próximo" escolhe pela espera, não pela pessoa.** Senão ninguém pega o pedido de doze itens.

**Falta não trava e não baixa estoque:** o pedido segue para a Conferência de Saída com a quantidade encontrada, e a diferença vira divergência aguardando reconferência (§14.14).

## A trava nasceu com a tela

Quatro ações novas no catálogo — `separacaoAssume`, `separacaoConclui`, `separacaoFalta`, `separacaoReabre` —, as três primeiras sem senha e todas com registro. Trabalho de galpão não pede senha: pede **rastro**. A exceção é reabrir separação concluída, que desfaz o que a etapa seguinte já pode ter usado.

## "Etiquetagem" virou "Conferência de Saída" em todo o sistema

O nome antigo descrevia o acessório. Trocado no menu das 57 telas e, nas duas de Vendas, também a **situação do pedido** (`etiquetagem` → `conferenciasaida`). O rename em bloco produziu na hora *"Enviar para conferenciasaida"* no texto que o usuário lê — o mesmo mordida de §14.12, encontrada porque eu fui olhar, não porque algo acusou.

## O achado da noite: a folha de confirmação comia o próprio aviso

O botão Confirmar executava o callback e **só então** fechava a folha:

```js
if (acaoConfirmada) acaoConfirmada();   // o callback chama avisar(...) e ABRE a folha
fecharModalConfirmacao();               // e esta linha FECHA ela de novo
```

Callback que termina em `avisar(...)` tinha a explicação **escrita e apagada antes de qualquer pessoa ler**. Valia em **8 telas** — o funil do Pedido de Venda era uma delas, então *"a comissão do vendedor está liberada"* e *"esta é a BAIXA FÍSICA do estoque"* **nunca apareceram para ninguém** desde que o funil nasceu, em 30/set.

Nenhum teste pegava porque **o texto estava lá** — só a folha é que não estava aberta. Os testes liam `#confirmModalTexto`, não `.classList`. É o mesmo formato do menu "mais >" de ontem: a asserção olhava para o atributo e não para a tela.

Corrigido nos 13 arquivos que têm o modal — fecha **antes** de executar —, e virou a **checagem 12** do `auditoria.py`, que reprova o código antigo (verificado contra uma cópia com ele de volta).

## Dois defeitos meus que a auditoria oficial pegou

Ao trocar o bloco de CSS da tela clonada eu levei junto **dois componentes compartilhados que moravam no fim dele**: o campo de senha do modal (que apareceu com fundo branco no tema escuro) e a regra que impede botão sublinhado. E usei **fonte monoespaçada** no endereço de estoque para alinhar o código — a regra do sistema é **uma fonte**, e o alinhamento saiu de `tabular-nums` com espaçamento, sem trocar a família. §14.8 de novo: clone cobra o que você apagou sem olhar.

## Estado

- **58 telas** + o molde. Duas auditorias limpas nas 59.
- **18 suítes sob selo.** A nova (`teste_separacao.py`) protege as sete decisões acima, não o desenho.
- **F4 aberta.** Próximas: **Conferência de Saída** e **Expedição**, nessa ordem.

## Pendência que esta tela criou

`separacaoAlertaHoras`, `separacaoCriticoHoras` e `separacaoOrdemPorEndereco` entram no `PARAM` e **não existem em tela de Configurações** — exatamente a dívida que 02/out já tinha anotado com `reservaExpiraDias` e `bloquearPedidoAtrasoDias`. Agora são **cinco** parâmetros órfãos. A próxima passagem por Configurações não é opcional.

---

# 05/out/2026 — o sinal que faltava, e a barganha da Conferência de Saída

## O bug que o usuário viu em dois minutos de uso

Item com falta registrada ficava com a mesma cara de item intocado na ficha de Separação. Riscado só acontecia na coleta inteira. Ele respondia a falta e não via diferença nenhuma.

**A causa é conceitual:** eu usei um sinal só para duas informações diferentes — "respondi" e "veio tudo". Agora são três estados, com a marca intermediária (`:indeterminate`) entrando no componente das **59 telas**, porque a Conferência de Saída vai precisar do mesmo estado. Em **§14.15** do design system.

## O Olist, conferido na fonte

Antes de desenhar, lemos a documentação em vez de deduzir dos prints. O resumo e as duas consequências estão em **§14.16**. O que importa aqui:

- **Não existe "Conferência de Saída" como módulo no Olist** — o usuário estava certo. A função existe partida em dois: **embalagem** (por pedido) e **conferência de pedidos** (por romaneio, dentro da Expedição).
- **O Olist confere duas vezes.** Nossa barganha de 02/out previa uma só, e estava errada.
- **A NF-e já existe** antes da expedição lá; aqui ela continua saindo na conferência.

## As quatro decisões fechadas

| decisão | escolha |
|---|---|
| quantas conferências | **duas, com perguntas diferentes** — itens na Conferência de Saída (caixa aberta), volumes na Expedição (caixa lacrada, bipa etiqueta, checa transportadora) |
| contagem | **cega** — o campo nasce vazio e o esperado só aparece depois que o item fecha, reusando `conferenciaCega` |
| multi-volume | **agora**, junto com a tela — caixa 1 de 2 muda a etiqueta, o romaneio e a conferência da expedição; entrar depois é refazer os três |
| parâmetros órfãos | **entram nesta rodada**, em Configurações → Conferência, que já existe |

**Por que cega aqui, se o conferente veio da separação e já viu a lista?** Porque esta etapa existe para pegar o erro da separação. Com o número à vista, a pessoa digita o número em vez de contar — e aí a conferência confirma o erro em vez de achá-lo. A bipagem resolve o atrito: cada peça lida soma sozinha.

## A tela se monta do que já existe

| bloco | de onde vem |
|---|---|
| a fila | Separação (mesmo esqueleto, outras situações) |
| lista de itens com campo de quantidade | Entrada de Notas (detalhe) |
| bipagem e folha de impressão | Separação (ficha) |
| escolha da embalagem | Cadastros → Embalagens (nome, tipo, medidas, peso) |
| contagem cega | Configurações → Conferência (`conferenciaCega` já existe) |
| marca intermediária por item | o componente, desde §14.15 |

## A dívida de Configurações fecha junto

Os cinco parâmetros órfãos — `reservaExpiraDias`, `bloquearPedidoAtrasoDias`, `separacaoAlertaHoras`, `separacaoCriticoHoras`, `separacaoOrdemPorEndereco` — mais os novos da conferência entram em **Configurações → Conferência** e **Parâmetros de estoque**, nesta rodada. Era a pendência aberta desde 02/out.

---

# 05/out/2026 — a ficha de Separação depois de dois minutos de uso real

Três coisas que só aparecem quando alguém usa a tela, e uma quarta que eu devia ter feito ontem.

## O que o usuário pediu

**1. "Não achei tudo" virou botão.** Era texto laranja sem borda — ele leu como rótulo, não como controle. Agora é `.pill-btn-sm`, que já existia no sistema, e **o rótulo acompanha a função**: vira *"corrigir separação"* depois de usado, com tinta de alerta. §14.17.

**2. O número grande passou a ser o número real.** Mostrava `6` em corpo grande e *"coletou 5"* em miúdo. Quem lê a linha depois — o conferente de saída, o cliente no histórico — pergunta *"quantas peças estão na caixa?"*. Agora: **5** grande, *"de 6 · falta 1"* em miúdo. §14.18.

**3. Separação parcial.** A ficha só oferecia concluir. Pedido de 40 itens não cabe num turno, e a escolha do operador era concluir mentindo ou devolver para a fila e perder o que já tinha andado. **Guardar não é devolver** — guardando, o pedido continua no nome dele e as marcas ficam; devolvendo, volta para todos e começa do zero. A confirmação diz as duas coisas e aponta qual botão serve para a outra intenção. §14.20.

## O que apareceu de quebra

**O alinhamento da lista serrilhava.** Cada linha é um grid próprio; com a última coluna em `auto`, a linha que ganhou um selo extra ficou **78px fora** das outras. Colunas fixas, e uma asserção que compara o `left` da mesma coluna em todas as linhas. §14.19. O selo FALTA saiu da linha aberta junto: ela já dizia a mesma coisa quatro vezes — riscada, marca intermediária, quantidade em alerta e o botão mudando de nome e de cor.

## A dívida de ontem, paga

**O catálogo de ações da Separação existia só nas duas telas do módulo.** Configurações → Confirmações por senha, Vendedores → Acesso e Registro de Atividades não conheciam `separacaoAssume`, `separacaoConclui`, `separacaoFalta` e `separacaoReabre` — a ação acontecia, gravava no registro, e **não havia onde ligar a trava**.

A regra do catálogo dizia *"a trava nasce com a tela"*; faltava a metade de trás: **entra no catálogo de quem usa E de quem lê**. As cinco chaves (com a nova `separacaoParcial`) estão nas três telas consumidoras, e a suíte do módulo agora abre as três e exige cada uma. §14.21.

## Estado

- **58 telas** + o molde. **18 suítes sob selo**, a de Separação com as asserções novas de botão, quantidade, alinhamento, parcial e catálogo.
- **Próximo:** Conferência de Saída (fila + ficha), com as quatro decisões já fechadas e os cinco parâmetros órfãos indo junto para Configurações → Conferência.

---

# 05/out/2026 — Conferência de Saída, e a dívida de Configurações paga

A segunda peça da F4, com as quatro decisões da barganha já fechadas. Duas telas: a **fila da bancada** (`pagina-logistica-conferencia-saida.html`) e a **bancada** (`pagina-logistica-conferencia-saida-detalhe.html`).

## O que a tela faz

**Confere cego, e a bipagem constrói a contagem.** Cada leitura soma uma peça; a quantidade que a separação entregou só aparece quando não há mais o que esconder. Quando a contagem não bate, a tela diz **que** existe divergência e **nunca quanto** — o conferente primeiro escolhe recontar ou bancar a contagem, e só depois o número aparece e o motivo vira obrigatório. Mexer na contagem depois de bancar **reabre a decisão**. Em **§14.22**.

**A nota sai pelo que está na caixa.** Valor do pedido e valor a faturar são dois números na tela, e eles divergem quando a caixa leva menos do que foi vendido. Os itens não mostram preço; o resumo mostra — porque é esta tela que fatura. **§14.23**.

**A compensação é do cliente.** CDC art. 35: falta para o cliente **trava o fechamento** até alguém registrar se ele escolheu restituição, crédito ou reenvio, com restituição sugerida quando o pedido já está pago.

**Volumes e etiquetas.** Cada volume escolhe a embalagem no cadastro (nunca texto solto), e vira **uma etiqueta numerada** "1 de 2" e **uma linha no romaneio** da Expedição — que é quem confere volume na saída do galpão, não item.

## A dívida de Configurações, paga

Os cinco parâmetros órfãos ganharam tela, junto com os quatro novos:

| onde | parâmetros |
|---|---|
| **Parâmetros de estoque** → *Filas do galpão* | `separacaoAlertaHoras`, `separacaoCriticoHoras`, `conferenciaSaidaAlertaHoras`, `conferenciaSaidaCriticoHoras` |
| **Parâmetros de estoque** → *Reserva e bloqueio* | `reservaExpiraDias`, `bloquearPedidoAtrasoDias` (com **zero desligando** a trava, e a prévia dizendo isso em palavras) |
| **Configurações → Conferência** → *Na saída do galpão* | `conferenciaSaidaCega`, `sugerirEmbalagem`, `separacaoOrdemPorEndereco` |

A nota da listagem de Pedidos apontava para "Configurações → Parâmetros de estoque" desde 02/out, e eles não estavam lá. **Parâmetro órfão é promessa falsa** — agora a promessa é verdadeira.

## Três defeitos meus, e o que pegou cada um

**A folha de aviso nunca abria com id inválido.** `avisar` é função içada, mas `confirmModal` é `const` no bloco seguinte: a primeira linha escrevia o texto e a segunda estourava na zona morta temporal. O texto aparecia, a folha não. **§14.24** — e a asserção certa olha `classList.contains('open')`, não o texto.

**O catálogo não entrou na tela que mais precisava dele.** A guarda da propagação procurava `'confSaidaFecha'` no arquivo, e a chave já estava lá — no código que **usa** a ação. O que denunciou foi a trava de setembro: `exigeSenha` devolve `true` para chave desconhecida, então o botão **parou de funcionar visivelmente**. **§14.25**.

**A tabela da fila estourava o card em 79px.** Saiu a coluna *Depósito*: ela já é filtro ali em cima, e a bancada é uma só.

## Estado

- **60 telas** + o molde. Duas auditorias limpas nas 61.
- **19 suítes sob selo**, com a nova (`teste_conferencia_saida.py`) protegendo a cega, o vazamento do tamanho da divergência, a reabertura da decisão, o CDC e a etiqueta sem valor.
- Varredura de cliques limpa nas duas telas novas.
- **Falta da F4: Expedição** — romaneio, conferência de volume, confirmação da saída do galpão e a **baixa física** do estoque.

---

# 05/out/2026 (noite) — o interruptor que estava do lado errado do balcão

O usuário olhou a bancada e viu o problema em uma frase: *"essa opção não deveria mostrar aqui, porque dá a opção do conferente desativar"*.

Ele está certo, e eu copiei o interruptor da Conferência de Compra sem perguntar se o caso era o mesmo. **Não é.** Na entrada, o erro que a contagem cega pega é do **fornecedor** — um terceiro. Na saída, é do **colega que separou** e, no limite, do **próprio conferente**. Dar o botão a quem está sendo conferido é entregar a chave do controle para o controlado.

**O que mudou:**

- O interruptor **saiu da bancada**. No lugar dele, a tela **diz o estado** ("a contagem está cega…") e **onde isso se muda** — controle invisível vira chamado de suporte, não disciplina.
- O parâmetro `conferenciaSaidaCega` vive só em **Configurações → Conferência**, tela de outro perfil.
- Lá, desligar passou a **pedir senha** e a **entrar no registro de atividades**: é a única mudança daquela tela que *apaga um controle* em vez de ajustar um padrão. A ação `confSaidaCegaDesliga` mudou de lugar no catálogo — de *Logística → Conferência de Saída* para *Configurações → Conferência* — e de `exigePadrao: false` para `true`.

**A auditoria pegou a metade que eu ia esquecer:** a tela de Configurações passou a *usar* a ação e não tinha a célula no catálogo — checagem 7, na hora. É §14.25 de novo, no mesmo dia.

**A Conferência de Compra fica como está**, de propósito: lá o interruptor na tela continua defensável. Se um dia a decisão for uniformizar, é barganha nova — não propagação silenciosa.

Está em **§14.23** do design system. **19 suítes · 0 falhas**, duas auditorias limpas nas 61.

---

# 06/out/2026 — a pasta desatualizada, e a Expedição pesquisada antes de desenhada

## A pasta do usuário estava mentindo

Ele abriu a pasta e não achou as telas novas. Estava certo, e era pior: além das quatro de Logística faltarem, **várias telas lá eram de 30/set** — antes do funil renomeado e antes da correção da folha de confirmação. A `Claude outputs` continuava lá, com seis HTMLs de setembro e sete prints de QA, todos superados.

Gravei o projeto inteiro — **61 telas, 3 `.md` e as 25 ferramentas** — e **conferi a pasta depois de gravar**. É a armadilha que a skill do projeto já descrevia: `device_commit_files` aterrissando em subpasta enquanto o chat diz "entregue". **Conferir depois de gravar passa a ser parte da entrega**, não zelo extra.

## A pesquisa: doze sistemas, não um

A pedido dele, a Expedição foi pesquisada antes de desenhada — Bling, Omie, Sankhya, Senior, CIGAM, Magis5, Expedy, Protheus, mais Odoo, SAP EWM, Dynamics 365 e NetSuite, mais as plataformas de envio e a legislação. Está em `claude/pesquisa-expedicao-mercado.md`, com fonte para cada afirmação e com as lacunas declaradas.

**O que ela confirmou:** o agrupamento se forma sobre **nota fiscal**, não sobre pedido (cinco sistemas brasileiros) — que é a ordem fiscal que fechamos em 30/set; divergência como estado de primeira classe; e o gate manual antes de "enviado".

**O que ela mudou:** o Dynamics **não baixa estoque ao confirmar a saída** — a dedução vem no lançamento do packing slip, para que erro de doca não vire lançamento errado. Isso **não se aplica a nós** porque a nota já saiu antes, e o efeito colateral é bom: **pedido que volta da doca não precisa de estorno**. Em §14.26.

**O que ela trouxe de novo:** um romaneio = uma forma de envio; peso bruto bloqueante; romaneio em duas vias com assinatura (o padrão do PLP, onde a via carimbada é o comprovante de postagem).

**E a parte fiscal, que eu não ia adivinhar:** desde **06/04/2026** só vale a **DC-e** eletrônica e o transportador não aceita envio sem chave de NF-e ou DC-e; o **MDF-e varia por estado** (intramunicipal nunca exige; SP exige interestadual com mais de uma nota; RS exige até com uma só, e no intermunicipal); e o **canhoto de papel acabou** em 2021, substituído pelo evento da NF-e. Em §14.27.

## As quatro decisões fechadas

| decisão | escolha |
|---|---|
| como o romaneio nasce | **sugerido pelo dia e pela forma de envio** — a tela abre com os romaneios montados e a pessoa confirma ou tira pedido |
| transportadoras | **cadastro novo agora**, junto com a Expedição — é dele que o romaneio agrupa, e Devolução e Rastreamento vão precisar |
| carga parcial | **fecha com o que saiu; o resto volta para a fila** — e nada precisa ser estornado, porque a baixa ainda não aconteceu |
| conferência de volume | **sempre, bipando a etiqueta de cada volume** |

## O que fica de fora, e por quê

PLP, ARs, DACE, DANFE, declaração de conteúdo, Intelipost e **rate shopping** são de **integração** com transportadora e módulo fiscal. Botão que não faz nada é a promessa falsa que acabamos de pagar com os parâmetros órfãos.

Um achado guardado para quando a integração entrar: **a recotação no empacotamento, com a caixa real, é o que fecha o custo do frete** — e a diferença para o que o cliente pagou é um custo que hoje ninguém enxerga.

# 06/out/2026 (noite) — a Expedição construída, e o menu que já sabia

## Três telas novas

**Operacional → Transportadoras** (`pagina-operacional-transportadoras.html`). Nome no galpão, tipo, CNPJ, dias de coleta, horário de corte, prazo em dias úteis, peso máximo por volume, UF de origem, contato e observação para o galpão. O **tipo decide o formulário**: retirada no balcão não tem coleta nem limite de carga, e frota própria é o único tipo que fala de MDF-e (§14.28).

**Logística → Expedição** (`pagina-logistica-expedicao.html`). A fila da doca, por **romaneio**, não por pedido. Abre com as cargas já sugeridas pelo dia e pela forma de envio, e diz em uma frase o que ficou de fora e por quê (§14.31).

**O romaneio** (`pagina-logistica-expedicao-detalhe.html`). Conferência por volume bipando etiqueta, peso bruto na balança, despacho com baixa do estoque físico e impressão em duas vias com assinatura (§14.32 a §14.34).

## O menu já sabia onde a tela morava

Comecei Transportadoras como `pagina-cadastros-transportadoras.html` e cheguei a inserir o item no flyout de Cadastros nos 62 arquivos. **O sistema já tinha uma entrada "Transportadoras" em Operacional**, sem destino, desde o primeiro desenho do menu — ao lado de Formas de Pagamento, Cupons e Motivos de Devolução, que são exatamente o mesmo tipo de cadastro auxiliar. Desfiz e liguei a entrada que já existia. Virou regra em §14.30: **entrada de menu sem destino não é lugar vago, é decisão tomada esperando tela.**

Operacional sai de **0 de 6** para **1 de 6**, e Logística de **2 de 6** para **3 de 6**.

## O que a construção decidiu, além da barganha

**Retirada no balcão não entra em romaneio** — derivado do tipo, não um interruptor separado. Dois lugares dizendo a mesma coisa é um lugar para elas discordarem.

**Pedido só embarca com todos os volumes bipados.** A conferência é por volume; a carga é por pedido. Caixa "2 de 4" sozinha no caminhão não é meia entrega. Incompleto volta inteiro para a fila — e sai barato porque nada foi baixado ainda.

**Duas travas no despacho** (peso bruto e pelo menos um pedido completo). Todo o resto avisa e deixa passar.

**O desvio de peso compara com o que foi BIPADO**, não com o romaneio inteiro — senão a tela acusaria 37% de erro justamente quando um pedido fica para trás de propósito. Foi um bug real, pego no navegador.

## Parâmetros novos

`expedicaoAlertaHoras` (8), `expedicaoCriticoHoras` (24), `romaneioSugereAutomatico` (ligado), `expedicaoDesvioPesoPct` (15) e o par `mdfeRegraUF` / `mdfeRegraPadrao`.

> **Dívida declarada:** nenhum deles tem tela em Configurações ainda. É exatamente o erro que pagamos em 05/out com `reservaExpiraDias`. Entra na mesma rodada que fecha a F4.

## Catálogo

Módulo `transportadoras` nasce com os três verbos ligados, em um grupo novo (**Operacional**) que as telas leitoras renderizam sozinhas. Cinco ações específicas de Expedição: `expedicaoMonta`, `expedicaoTiraPedido`, `expedicaoCancela`, `expedicaoDespacha` (nenhuma pede senha — é trabalho normal de doca) e `expedicaoReabre`, que **pede**, porque devolve peças ao estoque depois de o veículo ter saído.
