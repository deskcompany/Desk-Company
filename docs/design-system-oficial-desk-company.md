# Desk Company ERP — Design System Oficial (v2 — atualizado após módulo de Cadastros)

> **Papel deste arquivo dentro do conjunto de 3:** este é o único arquivo de **visual e componentes** — cores, fontes, medidas, e os padrões de UI (listagem, seleção em massa, modal, dropdown, drawer). Pra **schema, stack e roadmap do projeto**, ver `arquitetura-roadmap-desk-company.md`. Pra **ver os padrões funcionando de verdade**, ver `pagina-molde-referencia.html`. A skill `desk-company-erp` (Claude Skills) já traz um resumo executável deste conteúdo — este `.md` é a versão completa/humana de referência.

Este documento é a referência única de design do projeto. Qualquer página nova criada a partir de agora segue exatamente estes padrões — não é pra reabrir discussão de cor/fonte/espaçamento depois.

**v2:** seções 1–6 documentam a base (sidebar, cores, tipografia, Dashboard). Seções 7–13 documentam o padrão de Cadastros (listagem, seleção em massa, modal de confirmação, dropdown customizado, drawer, página de detalhe) — travado depois de construir Clientes, Fornecedores, Categorias e Produtos.

---

## 1. Cores

### Modo escuro (padrão do sistema)
| Token | Hex | Uso |
|---|---|---|
| `--page-bg` / `--panel-bg` | `#101010` | Fundo da página e dos painéis |
| `--border` | `#262626` | Bordas sutis, divisores |
| `--text` | `#AFADA2` | Texto padrão (itens de menu, corpo) |
| `--text-heading` | `#F5F4F1` | Títulos, textos de destaque |
| `--active-bg` | `#000C29` | Fundo de item selecionado/ativo |
| `--active-text` | `#9DB8F0` | Texto/ícone do item ativo (azul do Olist, tom claro pro escuro) |
| `--brand-blue` | `#4C8DFF` | Cor da marca (usada só na wordmark) |
| `--logo-color` (escuro) | `#FFFFFF` | Cor do "Desk Company" no modo escuro |

### Modo claro
| Token | Hex | Uso |
|---|---|---|
| `--page-bg` / `--panel-bg` | `#FCFBF8` | Fundo (bege bem claro, não branco puro) |
| `--border` | `#E9E7E0` | Bordas sutis |
| `--text` | `#3E3E3D` | Texto padrão |
| `--text-heading` | `#101010` | Títulos |
| `--active-bg` | `#E8EFFF` | Fundo de item ativo |
| `--active-text` | `#0A4EE4` | Texto/ícone do item ativo (azul exato do Olist) |
| `--brand-blue` | `#2979FF` | Cor da marca |
| `--logo-color` (claro) | `#2979FF` | Cor do "Desk Company" no modo claro |

**Regra de ouro da cor:** o azul de seleção/hover (`--active-bg`/`--active-text`) é sempre o tom "Olist" (validado por extração de pixel dos exemplos reais). A cor de marca (`--brand-blue`) só aparece na wordmark "Desk Company" — nunca nos estados de interação.

## 2. Tipografia

- **Fonte única do sistema: Nunito** (Google Fonts, pesos 400/600/700/800/900). Escolhida por ser a mais próxima disponível publicamente da fonte arredondada usada pelo Olist (não há como replicar a fonte proprietária exata).
- Wordmark "Desk Company": Nunito 900, 26px, cor `--logo-color`
- "ERP System" (subtítulo da marca): Nunito 400 (sem negrito), 16px, cor `--text-heading`
- Itens de menu principal: Nunito 600, 15px
- Itens de menu inferior (Notificações, Central de Suporte): Nunito 600, 14px
- Título de painel/flyout (ex: "Cadastros", "Vendas"): Nunito 800, 18px
- Itens de submenu (flyout): Nunito 600, 14.5px
- Título de página (H1 do conteúdo principal): Nunito 800, 22px
- Breadcrumb: Nunito 400/700 (segmento atual em negrito), 13px

## 3. Estrutura da Sidebar (cartão único flutuante)

- Sidebar e painel de submódulos (flyout) formam **um único cartão flutuante**: mesma borda, mesmo fundo, cantos arredondados (18px) só nas bordas externas, separados apenas por uma linha fina interna (`border-left: 1px solid var(--border)`) — nunca dois cartões com vão entre eles.
- Cartão fixo na tela (`position: fixed`), com margem de 18px do topo/esquerda, altura `calc(100vh - 36px)`.
- Largura da sidebar: **300px** (largura testada e validada para caber todos os nomes de submódulo sem quebrar linha, incluindo "Cadastro de Contas Bancárias").
- Largura do flyout quando aberto: também **300px**, mesma altura da sidebar.
- Conteúdo principal (`.main`) com `margin-left: 336px` pra não ficar embaixo do cartão.

### Comportamento do flyout
- **Clique** (não hover) no módulo abre o painel — clicar de novo no mesmo módulo fecha.
- Clicar num submódulo fecha o painel automaticamente e atualiza o breadcrumb + título da página.
- **Clicar fora do cartão inteiro fecha o painel**, sem precisar clicar em outro módulo.
- Transição de largura suave (0.2s) — texto sempre em uma linha só (`white-space: nowrap`) pra nunca quebrar durante a animação (evita bug de rolagem piscando).
- Hover num item do flyout: desliza 6px pra direita + fundo `--active-bg` + texto `--active-text`.

### Recolher menu ("Fixar menu")
- Interruptor no rodapé da sidebar. Quando desligado, a sidebar encolhe pra **74px**, escondendo todos os textos (só ícones ficam visíveis, incluindo "ERP System" que desaparece e o wordmark "Desk Company" some também).

### Breadcrumb
- Fica no topo do conteúdo principal, formato "Início › Módulo › Submódulo", com segmentos anteriores clicáveis (voltam pro nível daquele clique) e o atual em negrito.

## 4. Estrutura de Menu (8 módulos + rodapé)

**O menu segue a sequência de trabalho, e não o alfabeto** (decisão do usuário em 13/out/2026). A
regra vale para todo módulo e para todo item novo:

1. primeiro a tela de **consulta** do módulo, a que se abre para saber como as coisas estão;
2. depois as telas **na ordem em que o trabalho acontece**;
3. depois a **análise**;
4. **Relatórios** por último.

**Item novo entra na posição da função dele, e não no fim da lista.** Módulo novo nasce com a sua
sequência escrita na tabela abaixo. A ordem é guardada pela seção 11 de `teste_menu.py`: enquanto o
menu de uma tela e a lista de lá não disserem a mesma coisa, o selo reprova.

| módulo | a sequência | ordem |
|---|---|---|
| Início | o dia | Página inicial · Dashboard KPIs · Agenda · Minha Conta |
| Cadastros | quem → o quê, do geral para o detalhe → onde | Clientes · Fornecedores · Vendedores · Produtos · Categorias · Departamento de Produtos · Seção de Produtos · Marcas de Produtos · Embalagens · Lojas Desk · Depósitos · Endereços de Estoque · Relatórios de Cadastros |
| Estoque | consultar → comprar → receber → guardar e movimentar → corrigir → analisar | Controle de Estoques · Movimentação de Estoque · Necessidades de Compra · Ordens de Compra · Entrada de Notas · Conferência de Entrada · Endereçamento · Reposição · Transferência Entre Estoques · Inventário · Acerto de Estoque · Tratamento de Perdas · Giro de Estoque · Relatórios de Estoque |
| Vendas | antes da venda → a venda → o resultado | CRM · Pedidos de Venda · PDV · Notas Fiscais · Metas e Performance · Margem Contribuição · Custos do E-commerce · Relatórios de Vendas |
| Logística | o caminho do pedido no galpão, e a volta | Separação · Conferência de Saída · Expedição · Rastreamento de Pedidos · Devolução · Relatórios de Logística |
| Finanças | o título nasce → é pago → cai no caixa | Contas a Receber · Contas a Pagar · Caixa · Comissões Afiliados · Relatórios Finanças |
| Integrações | a venda entra → é paga → vira nota | Marketplaces e Hubs · Gateways de Pagamento · Emissão de Notas Fiscais · Relatórios de Integrações |
| Configurações | — | um atalho para o hub, que lista as telas por aba |

Rodapé fixo: Notificações, Central de Suporte, Configurações e o interruptor "Fixar menu". O módulo
Operacional saiu do menu em 08/out/2026 (§14.46).

## 5. Regras técnicas de proteção (aprendizados desta fase)

- Todo container com rolagem declara `overflow-x` e `overflow-y` explicitamente — nunca deixar implícito (causa barras de rolagem fantasmas).
- `user-select: none` em todo texto de navegação (sidebar, flyout, breadcrumb) — evita seleção acidental de texto ao clicar.
- Textos de item nunca quebram linha (`white-space: nowrap`) — a largura do container é que se adapta ao maior nome, não o contrário.
- Elementos clicáveis (nav-item, flyout-item) sempre com `cursor: pointer` e transições de 0.15s.
- **Bug real (Lojas Desk e Categorias):** o seletor de tema (Auto/Claro/Escuro) usa a classe `.theme-seg`. Qualquer toggle novo que reaproveite essa mesma classe (ex: Tipo, Pessoa Física/Jurídica, Categoria de Produtos/Fornecedores) faz o listener genérico do tema **limpar a classe `.active` de todos os `.theme-seg button` da página**, inclusive dos toggles novos — e, no caso de Categorias, também disparava a troca de tema (claro/escuro/auto) sem querer ao clicar no toggle de tipo, porque `data-theme` vinha `null` e caía no ramo "auto". Correção obrigatória: o listener do seletor de tema tem que ser escopado a `.theme-picker .theme-seg button`, nunca `.theme-seg button` sozinho — **Em setembro/2026 essa correção foi varrida e aplicada nos 22 arquivos do projeto de uma vez** (ver §14) — inclusive nas telas onde o bug ainda estava latente, isto é, o listener estava solto mas a tela ainda não tinha nenhum outro toggle usando `.theme-seg`. Hoje nenhum arquivo do sistema usa `.theme-seg button` sem o escopo `.theme-picker`, e a auditoria automatizada (seção 4B) reprova qualquer reintrodução. Qualquer toggle novo que reaproveite `.theme-seg` (visual) já nasce protegido.

## 6. Padrões de página de conteúdo (cards, cores semânticas, formatação)

Estabelecidos construindo a primeira página real (Dashboard KPIs) — valem para todas as próximas páginas do sistema.

### Cores semânticas (além das da sidebar)
| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `--success` | `#22C55E` | `#16A34A` | Variação positiva, valores bons |
| `--danger` | `#EF4444` | `#DC2626` | Variação negativa, alertas |
| `--warning` | `#F5A623` | `#F5A623` | Atenção (nem bom nem ruim) |
| `--chart-1` | `#9DB8F0` | `#0A4EE4` | Azul claro — 1ª série de gráfico/loja |
| `--chart-2` | `#4C6FC4` | — | Azul médio — 2ª série de gráfico/loja, **e cor de fundo dos botões pill ativos** (mais escuro que `--active-text`, dá mais contraste ao texto branco) |
| `--chart-3` | `#263A73` | — | Azul escuro — 3ª série de gráfico/loja |

### Cards
- `.card`: fundo `--card-bg`, borda `--border`, raio 14px, padding 18px
- `.card-head`: título (`.card-title`, Nunito 800/15px) + ações à direita, `justify-content:space-between`
- **Todo card de conteúdo tem um botão "•••"** (`.more-btn`) no canto superior direito do `card-head` — função ainda não implementada (fica pra quando entrarmos na tela de cada módulo), mas a presença dele já é padrão visual fixo
- Cards com filtro de quantidade (ex: "Mais Vendidos", "Alertas de Estoque") usam pills pequenas (`.pill-btn-sm`, 5/10/15/20) ao lado do "•••", não substituem ele
- Listas de itens dentro de um card (produtos, status, alertas) sempre com `border-top: 1px solid var(--border)` entre itens, removido só no `:first-of-type` — nunca deixar uma lista sem essa linha enquanto as outras têm
- Texto de "total" (ex: "Total do período: X", "Valor total em estoque: R$X") sempre no **rodapé** do card, não no topo — usa `margin-top:auto` com o card em `display:flex; flex-direction:column;`

### Botões de filtro (pills)
- `.pill-btn` (período: Hoje/7 dias/30 dias) e `.pill-btn-sm` (quantidade: 5/10/15/20): estado ativo = fundo `--chart-2` (azul médio sólido) + texto branco. **Não usar `--active-text` como fundo** (fica claro demais, texto branco perde contraste) — esse erro já foi cometido e corrigido uma vez.

### Formatação de quantidade (não é a mesma regra do dinheiro)

Dinheiro sempre tem 2 casas (ver abaixo). **Quantidade não** — quem manda é a **unidade de medida**:

- **Unidade contável** (`UN`, `CX`, `PC`, `PAR`…): número redondo, sem casas. Não existe meia cadeira — `21 UN`, nunca `21,00 UN`.
- **Unidade fracionável** (`M`, `M2`, `M3`, `CM`, `KG`, `G`, `TON`, `L`, `ML`): 2 casas, porque `128,50 m²` é um valor real de estoque.
- **Exceção proposital:** se um item de unidade contável aparecer com fração (anomalia de dado — meia caixa lançada por engano), as casas **são exibidas**. Arredondar esconderia o erro em vez de mostrar; o objetivo do formato é revelar o problema, não maquiar.

Implementado como `fmtQtd(n, unidade)` em Controle de Estoques (set/2026), com a lista `UNIDADES_FRACIONAVEIS` no próprio arquivo. Vale pra saldo, estoque mínimo, quantidade de movimentação e qualquer campo de quantidade das telas de Estoque, Logística e Vendas que vierem.

### Formatação de valores em R$
- **Todo valor monetário real tem 2 casas decimais**, sempre: `R$ 41.200,00`, nunca `R$ 41.200`
- Exceção: valores **abreviados** (formato "K", ex: `R$ 184,3K` no centro de um donut) e **marcadores de régua/eixo** de gráfico (ex: `R$ 8k`, `R$ 0` no eixo Y) — esses não levam ,00

### Barra de rolagem
- Customizada via `::-webkit-scrollbar` (Chrome/Edge/Safari desktop) e `scrollbar-width`/`scrollbar-color` (Firefox), sempre com fundo **sólido** `var(--page-bg)` (nunca `transparent` — pode vazar branco padrão do navegador em alguns contextos) e thumb `var(--border)`
- **Atenção:** o preview do Claude tem sua própria barra de rolagem ao redor do HTML, fora do nosso controle — não confundir com a barra real da página. Só validar a barra de verdade abrindo o arquivo direto no navegador (fora do preview).

## 7. Padrão de Listagem (módulos de Cadastros)

Estabelecido a partir de Clientes/Fornecedores e replicado em todo cadastro com múltiplos registros (Categorias, Produtos, e todo o que vier depois).

- **Toolbar**: busca (ícone de lupa + input arredondado) + filtro por tipo em pills (`.filtro-tipo`, fundo cinza translúcido, ativo = `--brand-blue` sólido) + dropdowns de ordenação/situação usando o **componente de dropdown customizado** (nunca `<select>` nativo — ver seção 11).
- **Card de item** (`.produto-card`/`.cliente-card`/etc.): checkbox customizado + avatar ou thumb de imagem + nome + tag de tipo + linha de meta (código/SKU/categoria) + badge de status colorido, tudo numa linha com `border-top` entre itens (mesma regra da seção 6).
- **Paginação**: resumo "Mostrando X–Y de Z" + seletor de itens por página (10/25/50/100, dropdown customizado) + navegação anterior/próxima. **Obrigatória em toda listagem, sem exceção** — inclusive nos cadastros "lista única" mais simples (Categorias, Departamento, Seção, Embalagens e Marcas de Produtos, ver §12). Quando existe paginação, o "Selecionar todos" (§8) passa a valer só pros itens **da página atual**, nunca da lista filtrada inteira. Todos os cadastros já seguem esse padrão desde setembro/2026 (Lojas Desk foi a última, alinhada na abertura de F5 — ver §14). **Exceção consciente:** `pagina-vendas-metas.html` e `pagina-vendas-performance-vendas.html` não têm paginação de propósito — operam sobre o conjunto fixo de 3 lojas, não sobre uma lista que cresce.
- **Filtro por Situação em abas** (além do filtro por tipo em pills): quando o cadastro tem estados diferentes de "ativo" que valem a pena separar (ex: Vendedores — ver §8.1), as abas ficam ao lado da busca, mesmo estilo dos `.filtro-tipo`, com uma aba marcada como padrão (a mais restritiva/relevante no dia a dia, não necessariamente "Todos").
- **Preview rápido**: clicar num item (fora do checkbox) abre o drawer lateral (seção 12) com resumo + botão "Editar cadastro completo" pro detalhe.

### 7.1 Listagem em tabela (telas de consulta, não de cadastro)

Cadastro usa **card de item** (uma linha visual por registro, avatar + nome + meta). Tela de **consulta numérica** — muitas colunas comparáveis entre si, onde o usuário lê coluna, não registro — usa **tabela** (`.estoque-table`, primeira em Controle de Estoques, set/2026). Segue as tabelas que já existiam dentro de páginas de detalhe (`.historico-table`, `.custos-table`):

- Cabeçalho `th` em 11px, 700, maiúsculas, `letter-spacing:0.3px`, cor `--text`, com `border-bottom` de 1px. Célula `td` em 13px, cor `--text-heading`, `border-bottom` entre linhas, removido na última.
- **Números alinhados à direita, texto à esquerda** (`.col-texto`). `white-space:nowrap` nas células de número; **a coluna de texto quebra linha** (`white-space:normal`) quando a tabela não cabe: a barra de rolagem é o último recurso, não o primeiro (§14.86).
- **Ordenação por clique no cabeçalho**: `th.ordenavel` com uma seta (`.seta`) em opacidade baixa; a coluna ativa ganha `.ordenado` e a seta vira ▲/▼ na cor `--active-text`. Clicar de novo na mesma coluna inverte.
- **Sempre dentro de `.estoque-table-wrap` com `overflow-x:auto`** — a rolagem horizontal fica na tabela, **nunca na página**, e **não aparece de 1280px para cima** (§14.86); abaixo disso é a degradação prevista. `min-width` só quando a tabela não consegue encolher sem perder a leitura. Conferir com `scrollWidth` no navegador, não no olho.
- **Cabeçalho longo custa largura mesmo quando a célula é curta.** Em Controle de Estoques, "Estoque reservado"/"Estoque disponível" (células só com "—") sozinhos empurravam a tabela 230px além do visível e escondiam a coluna Localização. Encurtados pra "Reservado"/"Disponível" com `title=` explicando, mais a Unidade virando sufixo do saldo em vez de coluna própria, a tabela passou a caber. **Medir a largura real das colunas antes de dar a tela por pronta.**
- Linha inteira clicável abre o drawer de detalhe/extrato. Tela de consulta **não tem checkbox nem barra de seleção** — a regra do §8 vale pra listagem com exclusão, e aqui não se exclui nada.
- **Paginação continua obrigatória** (§7), e o total do card vai no rodapé (§6).

### 7.2 Abas de situação **com contador** (padrão novo, Ordens de Compra — set/2026)

Quando a listagem tem um ciclo de vida com 3+ situações e o usuário precisa saber **quantos** existem em cada uma antes de clicar, as abas do §7 ganham um contador e um ponto colorido (`.abas-situacao` / `.aba-sit`). Diferente do `.filtro-tipo` (pílulas), estas abas ficam sobre uma linha de base (`border-bottom`), com a ativa sublinhada em `--active-text`.

- **O contador ignora a aba selecionada, mas respeita todos os outros filtros** (busca, período, depósito). Se o contador somasse a base inteira, ele mentiria sobre o que o filtro atual mostra; se respeitasse a própria aba, todas as outras zerariam.
- Cada situação tem cor própria, definida por tema (`.sit-*` para o ponto, `.bs-*` para o badge da linha) — mesma regra da paleta categórica do §14: os tokens `--chart-*` não servem como cor de texto.
- Use `.filtro-tipo` (pílulas) quando as opções forem **um recorte** (tipo de produto, tipo de endereço) e `.abas-situacao` quando forem **um ciclo de vida** com contagem relevante.

### 7.3 Filtro de período (popover próprio)

Período não é dropdown de valor: são opções em pílula dentro de um popover (`.periodo-menu`), porque as opções são curtas e o usuário compara antes de escolher. O botão-gatilho mostra o período ativo por extenso ("Últimos 7 dias"), nunca só um ícone. **Fecha mutuamente com os `.dropdown-select` da página** — abrir um fecha o outro, nos dois sentidos, e `Esc` fecha o popover quando não há modal nem drawer aberto.

## 8. Seleção em massa + Modal de Confirmação

Padrão fixo pra **toda** listagem que tiver exclusão — travado depois de testar em Clientes, Fornecedores, Categorias e Produtos.

### Checkbox customizado
Nunca usar o checkbox nativo do navegador (fica branco, destaca demais no tema escuro). Estilo fixo:
```css
.item-checkbox {
  appearance:none; -webkit-appearance:none; width:15px; height:15px; border-radius:4px;
  border:1.5px solid var(--border); background:var(--page-bg); cursor:pointer;
}
.item-checkbox:checked { background:var(--chart-2); border-color:var(--chart-2); }
.item-checkbox:checked::after { /* check branco desenhado via CSS, 2 bordas rotacionadas 45deg */ }
```
Usado em **todo** checkbox do sistema, incluindo o de dentro do modal de confirmação ("Estou ciente") e em checklists de linhas soltas fora de dropdown (ex: restrições de acesso e módulos permitidos de Vendedores, ver §11).

### Botão de opção (rádio) customizado
Primeiro uso em Vendedores → Comissionamento (`.radio-option`), mesma lógica visual do `.item-checkbox` só que círculo em vez de quadrado. Usar sempre que as opções forem mutuamente exclusivas **e** poucas o bastante pra caber lado a lado sem precisar de dropdown (ex: "Comissão com alíquota fixa" / "conforme descontos") — quando as opções são muitas ou exigem economizar espaço, o padrão continua sendo o dropdown de seleção única (§9).

### Barra de seleção
Fica no **rodapé da lista** (depois de todos os itens, antes da paginação) — nunca no topo. Mostra contagem + botões de ação (`Excluir selecionados` em vermelho `.btn-danger`, `Inativar selecionados` em `.btn-secundario` neutro quando o cadastro tem campo Situação) + link "Cancelar seleção".

**IDs/classes canônicos** (travados a partir de Fornecedores + Lojas Desk — usar exatamente estes em módulo novo):
- Checkbox "selecionar todos": `<div class="selecionar-todos-row"><input class="checkbox-todos" id="checkSelecionarTodos"><label for="checkSelecionarTodos">Selecionar todos</label></div>` — **não** é um `<label>` envolvendo o input, é `label for=` explícito.
- Barra: `<div class="selecao-bar" id="barraSelecao"><span class="selecao-info" id="selecaoInfo">` — fundo `var(--active-bg)` (destacado, sem borda), não `var(--panel-bg)`+borda.
- Botão cancelar: `id="btnCancelarSelecao"` (Fornecedores e Produtos, telas mais antigas, usam `btnLimparSelecao` — desvio de nomenclatura pequeno e sem impacto visual, não é prioridade corrigir; Lojas Desk também usa `btnLimparSelecao`, mesmo desvio).
- **Categorias, Departamento de Produtos, Seção de Produtos, Embalagens, Marcas de Produtos e Vendedores já usam a nomenclatura canônica correta** (`barraSelecao`/`selecaoInfo`/`checkbox-todos`) — Categorias foi alinhada em setembro/2026 (ver §12 e §14), depois de ter ficado um tempo com os nomes antigos (`selecaoBar`/`selecaoCount`).

### Loja(s) aplicável(is) — multi-seleção
Quando um cadastro precisa marcar **uma ou mais lojas** (não uma cascata única, e sim um conjunto), duas variantes visuais são aceitas — escolher conforme o espaço/densidade do formulário:
- **Lista de checkboxes inline** (`.loja-checkbox-row`) — mesmo visual do `.item-checkbox`, em classe própria (`.loja-checkbox`) pra não competir com o checkbox de seleção em massa da listagem. Um `<label class="loja-checkbox-row">` por loja. Usada em Categorias.
- **Dropdown multi-seleção** (ver §9.1) — o mesmo campo dentro de um `.dropdown-select`, com checkboxes no menu e o resumo separado por vírgula no botão fechado (ex: "Desk Shope, Desk Brands"). Usada em Marcas de Produtos desde setembro/2026 (decisão do usuário, pra deixar o formulário mais compacto), e também em Vendedores pro campo "Pode acessar contatos com o perfil" (§11).

Em ambas: campo obrigatório com mensagem "Selecione ao menos uma loja.", e a lista de lojas usada é sempre as **lojas de verdade** (Desk Shope, Desk Brands, Desk Tech), nunca inclui Desk Flash (é transportadora). **Exceção:** o campo "Loja Desk vinculada" de Vendedores (§11) não é multi-seleção nem obrigatório — é um vínculo opcional único, documentado à parte.

### Modal de confirmação (bottom-sheet)
Não é mais um cartão pequeno centralizado — é um **painel grande que sobe cobrindo a parte de baixo da tela inteira**, com fundo escurecido atrás:
```css
.modal-card { position:fixed; left:0; right:0; bottom:0; border-radius:20px 20px 0 0;
  padding:48px; transform:translateY(100%); transition:transform .25s ease; max-height:55vh; }
.modal-card.open { transform:translateY(0); }
```
- Título "Confirmação" (26px) + texto da pergunta (dinâmico) + botões.
- **Checkbox "Estou ciente destas ações e desejo continuar."** aparece só quando a ação afeta **2 ou mais** registros — trava o botão de confirmar até ser marcado. Some e desbloqueia automaticamente com 1 item só. Numa tela de detalhe que só exclui **um** registro por vez (ex: "Excluir vendedor" em Vendedores-detalhe), essa checkbox nem precisa existir no HTML — o modal já nasce sem ela.
- Cor do botão de confirmar muda com a ação: **vermelho** (`.btn-danger`) pra excluir, **azul** (`.btn-primary`) pra inativar ou criar algo novo (ação não-destrutiva).
- Botão "Cancelar" com indicador **ESC** ao lado — tecla Esc fecha o modal sem executar a ação.
- Reaproveitado também fora de exclusão em massa: confirmação de exclusão individual (1 item, sem checkbox) e confirmação de criação (ex: cadastrar uma Marca nova que ainda não existe).

### 8.1 Exclusão suave (soft-delete) — Vendedores

Vendedores é o primeiro módulo do sistema em que "Excluir" **não remove o registro** da lista de dados. Em vez de tirar o item do array (como em toda outra listagem até aqui), a exclusão marca um campo `excluido: boolean`, **independente** do campo `situacao`. O registro mantém o último valor de `situacao` que tinha — ex: um vendedor que já estava "Inativo" e é excluído continua "Inativo" por baixo, só ganha `excluido:true` por cima; um "Ativo" excluído continua "Ativo" por baixo.

- A listagem ganha **5 abas de filtro de situação** (ver §7) em vez das habituais: **"Ativos com acesso ao sistema"** (padrão/aba inicial — `situacao==='ativo_acesso' && !excluido`), **"Todos"** (sem filtro nenhum — inclui os excluídos), **"Ativos"** (`situacao` é `ativo_acesso` ou `ativo`, `&& !excluido`), **"Inativos"** (`situacao==='inativo' && !excluido`), **"Excluídos"** (`excluido===true`, qualquer que seja a `situacao` por baixo).
- "Excluir" — tanto individual (via "Mais ações → Excluir vendedor" na tela de detalhe) quanto em massa (barra de seleção da listagem) — só marca `excluido=true` nos registros afetados; não faz `splice`. O registro some das abas padrão mas continua acessível em "Todos"/"Excluídos", preservando o histórico (útil pra comissão já paga a um vendedor que saiu, por exemplo).
- **Segundo módulo com soft-delete: Depósitos** (setembro/2026, abertura de F5). Mesmo mecanismo (`excluido` independente de `situacao`), em versão mais enxuta: **3 abas** em vez de 5 — **"Ativos"** (padrão, `!excluido && situacao==='ativo'`), **"Todos"** (sem filtro, inclui excluídos) e **"Excluídos"** (`excluido===true`). O critério que justificou foi o mesmo escrito aqui: um depósito que fechou com histórico no ledger `stock_movements` não pode sumir, ou o extrato fica órfão. **Regra extra própria de Depósitos:** o **depósito principal** não pode ser excluído nem inativado — na seleção em massa ele é separado do lote e ignorado (o modal avisa pelo nome), e quando é o único selecionado o modal vira um aviso de uma via, com o botão "Entendi" em vez de "Confirmar"; na tela de edição o link "Excluir depósito" nem aparece pra ele.
- **Não é o padrão default do sistema** — todas as outras listagens (Clientes, Fornecedores, Produtos, Categorias etc.) continuam com exclusão definitiva (`splice`, some da lista de vez). Só adotar soft-delete num cadastro futuro quando reter o dado de um registro "excluído" importar de verdade pra relatório/auditoria — não trocar o padrão dos módulos existentes sem pedido explícito.

## 9. Componente de dropdown customizado (`.dropdown-select`)

Substitui **todo** `<select>` nativo do sistema, sem exceção. Estrutura: botão (`.dropdown-select-btn.form-style` em formulário, `.pill` em toolbar) + painel de opções (`.dropdown-select-menu`).

- **Abre sempre para baixo** (usuário, 15/out/2026, §14.82): fora de painel fixo, a página rola até o menu aparecer inteiro; `.abrir-para-cima` só dentro de painel fixo (painel lateral, modal), que não rola com a página, quando não cabe embaixo. Regra vale pra qualquer dropdown novo, sem exceção.
- **`max-height:240px; overflow-y:auto;` é obrigatório em `.dropdown-select-menu`, sem exceção.** Bug real (Lojas Desk detalhe): sem esse limite, uma lista longa (ex: 13 meses) cresce sem teto e não cabe nem abrindo pra baixo nem pra cima — a lógica de "abrir pra cima" fica parecendo quebrada, mas o problema de verdade é a altura ilimitada. Em setembro/2026 essa regra foi varrida e aplicada em **todas** as telas que tinham o componente e ainda estavam sem ela (Clientes, Clientes-detalhe, Fornecedores, Fornecedores-detalhe, Produtos-detalhe e o `pagina-molde-referencia.html`). A auditoria automatizada (seção 4B) agora reprova qualquer `.dropdown-select-menu` sem `max-height`.
- **Fechamento mútuo**: clicar em qualquer dropdown fecha todos os outros abertos na mesma página — implementado fechando todo `.dropdown-select-menu.open` ao abrir um novo. **Atenção ao integrar um dropdown "diferente" (ex: multi-seleção) — se ele usar uma classe de menu própria em vez de `.dropdown-select-menu`, não vai fechar nem ser fechado pelos outros.** (Bug real que já aconteceu com o campo Loja Desk quando ele ainda era multi-seleção com classe própria — corrigido convertendo pra usar exatamente o mesmo componente.)
- **Dropdowns em cascata** (um filtra as opções do próximo, ex: Loja → Categoria → Departamento → Seção): o dropdown "filho" nasce travado (`disabled`, texto tipo "Selecione X primeiro") até o "pai" ser escolhido; trocar o pai reseta todos os filhos em cascata.
- **Menu de ações (não é seleção)**: quando o dropdown não representa um valor de campo, e sim um menu tipo "Mais ações" (itens que disparam ações diferentes — ex: "Gerenciar comissões" / "Alterar senha de acesso" / "Excluir vendedor" em Vendedores-detalhe), ele **não** passa pelo `inicializarDropdownSelect` genérico (que espera um único `.dropdown-select-label` e marca item `.active`) — usa um bind próprio, só abrindo/fechando o menu e deixando cada item disparar sua própria ação e fechar o menu na sequência. **Precisa de `min-width` explícito no `.dropdown-select-menu`** (ex: `220px`) **+ `white-space:nowrap`** — sem isso, o menu herda a largura do próprio botão (`.dropdown-select` só é tão largo quanto o botão que envolve), e como um botão tipo "Mais ações" costuma ser mais estreito que os rótulos das ações, cada item quebra em 2 linhas (bug real, Vendedores-detalhe, corrigido em set/2026). Tudo bem o menu ficar mais largo que o botão e "vazar" por baixo de outro elemento da mesma linha (ex: o badge de status ao lado) — é abertura normal de dropdown, não um problema de sobreposição.
- **Nunca inicializar o mesmo elemento com duas funções de bind diferentes** — causa dois listeners de clique no mesmo botão, que se cancelam (abre e fecha no mesmo clique). Se um dropdown precisa de lógica especial (cascata, callback customizado, menu de ações), ele deve ser **excluído explicitamente** do loop de inicialização genérica.

### 9.1 Variante multi-seleção (checkboxes dentro do menu)

Pra campos que aceitam **mais de um valor** (ex: Loja(s) aplicável(is) de uma Marca; Perfis de contato acessíveis de um Vendedor), o mesmo componente visual (`.dropdown-select-btn.form-style` + `.dropdown-select-menu`) ganha uma variante multi-seleção: o menu tem um checkbox por opção (reaproveitando o estilo do `.item-checkbox`, envolvido num `<label class="dropdown-multi-item">` pra clicar no texto também marcar) em vez de itens de seleção única. O botão fechado mostra as opções marcadas separadas por vírgula (ex: "Desk Shope, Desk Brands") no lugar do texto único, com um placeholder (ex: "Selecione as lojas", "Qualquer perfil de contato") quando nada está marcado.

- **Recolhe automático a cada marcação/desmarcação** (ajustado em setembro/2026, a pedido do usuário) — diferente do comportamento original (menu ficava aberto até clicar fora), agora o menu fecha assim que uma opção é marcada ou desmarcada, igual a um dropdown de seleção única. Pra marcar mais de uma opção, o usuário reabre o dropdown e marca a próxima — o valor já marcado antes continua selecionado (é um conjunto de checkboxes, não se perde ao fechar). Implementado fechando o próprio `.dropdown-select-menu` (`classList.remove('open')`) dentro do handler `change` de cada checkbox, além do fechamento mútuo genérico ao abrir outro dropdown.
- **Por isso não passa pelo `inicializarDropdownSelect` genérico** (que assume um único item `.active` e tem seu próprio fechamento) — precisa de um bind próprio, igual qualquer dropdown com lógica especial (regra do fim da seção 9).
- **A classe do checkbox individual (ex: `.loja-checkbox`, `.perfil-checkbox`) é só um gancho de JS** — o visual vem do seletor genérico `.dropdown-multi-item input[type="checkbox"]`, não de uma regra própria por classe. Isso é esperado (a auditoria automática já tem essas classes na lista de exceção conhecida) — não é um "componente copiado pela metade" quando isso acontece com uma classe nova desse tipo.
- **Implementado em:** Marcas de Produtos, campo "Loja(s) aplicável(is)" (`#dropdownLojasMarca`) — substituiu, em setembro/2026, a lista de checkboxes solta (`.loja-checkbox-row`, ainda usada em Categorias) por decisão do usuário, pra deixar o formulário mais compacto (ver §8 e §12). Categorias **não foi alterada**. Também em Vendedores, campo "Pode acessar contatos com o perfil" (`#dropdownPerfisContato`, ver §11) — mesmo comportamento de recolhimento automático.

### 9.2 Campo de data com mini calendário (`.date-field`) — 22/set/2026

Quinto componente compartilhado do sistema, ao lado de dropdown, modal, drawer e checkbox. **Todo campo de data editável usa este componente** — `input type="date"` nativo está banido pela mesma regra do `<select>` nativo (o navegador desenha do jeito dele, não se estiliza, e o formato muda com o idioma da máquina).

```html
<div class="date-field" id="dfAlgumaData">
  <input type="text" id="inputAlgumaData" placeholder="dd/mm/aaaa" autocomplete="off">
  <button type="button" class="date-btn" aria-label="Abrir calendário"><svg .../></button>
  <div class="date-pop"></div>
</div>
```

```js
inicializarDataField(document.getElementById('dfAlgumaData'), {
  min: () => primeiroDiaLivre(),          // valor ISO ou FUNÇÃO
  motivoMin: () => 'Período financeiro fechado até ...',
  rodape: () => 'Fechado até <b>...</b>',
  aoMudar: (iso) => { ... }
});
```

- **O campo continua aceitando digitação.** O calendário é a segunda porta, não a única — quem sabe a data digita mais rápido.
- **`min` e `max` aceitam função**, e é assim que se usa quando o limite muda durante a sessão (fechamento financeiro, data da compra que limita a prevista). O calendário lê o limite **na hora em que abre**, não na hora em que a tela carregou.
- **Dia fora do limite aparece riscado, sem `data-iso` e sem clique**, com o motivo no `title` — e o rodapé do popover repete a regra. **É a regra do cadeado aplicada a datas: o controle diz o estado real antes do clique, em vez de reprovar depois.**
- **O popover é ancorado no ÍCONE, não no campo** (ajuste de 22/set/2026, pedido do usuário depois de ver a primeira versão). Duas regras:
  - **Horizontal: alinha pela direita**, que é onde o ícone fica. Alinhado pela esquerda do campo, o mouse atravessa o campo inteiro para chegar no dia — em campo largo isso são ~300px de percurso por clique.
  - **Vertical: abre para CIMA por padrão**, colado no ícone, e só desce (`.date-pop.abaixo`) quando o campo está no topo da tela e não há espaço acima. O raciocínio: num formulário preenchido de cima para baixo, quando se chega na data os campos acima já foram resolvidos — **cobrir o que já passou custa menos que cobrir o próximo passo e o botão de salvar**. É também o que resolve o popover cobrindo o rodapé do drawer.
  - **ESC fecha**, e clicar fora também.
- **Não substitui a agenda.** A grade de mês da Agenda é uma *visão*, não um seletor de campo; são componentes diferentes com trabalhos diferentes.
- **Campo de data somente leitura não recebe o componente** (data de criação, carimbos do sistema) — **mas tem de dizer por que é somente leitura**. O acerto inline do Controle de Estoques ganhou o hint *"o acerto entra com a data de hoje; estoque não se corrige no passado"*: campo travado sem explicação faz o usuário achar que está quebrado.

**Certificação de 22/set/2026 — a varredura completa.** Foram inventariados os 51 arquivos, procurando todo `input` cujo rótulo, id, placeholder ou valor se pareça com data (data, vencimento, emissão, entrada, nascimento, validade, competência, prazo, previsto, criação, fechamento). Resultado: **15 campos**, dos quais **10 editáveis — todos com o componente**, **3 carimbos somente leitura** e **2 falsos positivos** (*prazo de pagamento* e *prazo de entrega* são texto livre: "30 60, 3x", "5 a 10 dias úteis" — não são datas).

**E a varredura achou o que ninguém tinha visto: a Agenda tinha um calendário falso.** Um `.date-field-wrap` com o ícone de calendário em `pointer-events:none` sobre um `input readonly` — parecia exatamente o componente e não fazia nada; para trocar o dia era preciso fechar o painel e clicar em outro dia da grade. **Ícone que parece clicável e não é vale menos que ícone nenhum.** O wrapper e seu CSS morto foram removidos e o campo recebeu o componente de verdade, aceitando passado e futuro (compromisso pode ser registrado depois que aconteceu).


## 9.2 `inicializarDropdownSelect` — versão única, com delegação (23/set/2026)

**Havia três versões do mesmo componente nas 53 telas.** A mais antiga não tinha trava de inicialização nenhuma; a mais nova tinha trava só para o listener do botão. Todas ligavam **um listener por item**, fora da trava. Duas consequências reais:

1. **Chamar a função de novo acumulava listener.** Abrir o mesmo painel três vezes fazia o `aoMudar` disparar três vezes por clique. Invisível até hoje porque todos os `aoMudar` existentes são idempotentes — bomba armada para o primeiro que não fosse.
2. **Refazer o conteúdo do menu com `innerHTML` matava o comportamento**, porque os itens novos nasciam sem listener. Foi assim que a tentativa de inicializar os dropdowns de painel no carregamento quebrou a transferência do Caixa. **O teste pegou; a leitura do código não teria pegado.**

A versão canônica, agora **idêntica nas 51 telas que têm o componente** (três não têm dropdown nenhum):

- o callback mora **no elemento** (`raiz._aoMudarDropdown`) — a última chamada manda, sem empilhar;
- o clique é ouvido **no menu**, por delegação — sobrevive a `innerHTML` e a chamadas repetidas;
- a trava `dataset.dropdownInit` protege os dois listeners, não só o do botão.

**Regra que fica:** chamar `inicializarDropdownSelect` de novo é seguro e é o jeito de trocar o callback. Refazer o conteúdo do menu **não** exige re-inicializar.

## 9.3 Dropdown de painel nasce com a TELA, não com o painel

Dropdown que só ganha comportamento quando o painel abre é **botão mudo no carregamento** — a auditoria mede isso na seção 5, e ela está certa: painel fechado também faz parte da página. Os menus do painel de Pagamento e dos painéis do Caixa passaram a ser montados na abertura da tela; abrir o painel só atualiza o que está selecionado.

### 9.4 Menu **"Mais ações"** — um componente só (28/set/2026)

O menu de ações secundárias de uma tela existia em **quatro implementações**: quatro ids (`btnMaisAcoes`, `dropdownMaisAcoes`, `maisAcoes`, `menuAcoes`/`menuAcoesInv`), dois rótulos (*Mais ações* e *Ações*), três estilos de botão e **dois componentes de menu diferentes** — Clientes, Fornecedores e Produtos tinham um `.mais-acoes-menu` próprio, paralelo ao do design system. Nasceu por cópia, como quase tudo que divergiu.

O paralelo não era só estético: ele **não media o espaço antes de abrir**, não tinha `max-height` e **não fechava mutuamente** com os outros dropdowns da página — três regras do §9 quebradas de uma vez, invisíveis porque o menu "funcionava".

**O padrão, agora único em 18 telas:**

```html
<div class="dropdown-select" id="menuMaisAcoes">
  <button type="button" class="btn-ghost dropdown-select-btn">
    <span class="dropdown-select-label">Mais ações</span>
    <svg …><polyline points="6 9 12 15 18 9"/></svg>
  </button>
  <div class="dropdown-select-menu" style="right:0; left:auto; min-width:220px; white-space:nowrap;">
    <div class="dropdown-select-item" data-acao="…">Ação</div>
    <div class="dropdown-select-divider"></div>
    <div class="dropdown-select-item item-perigo" id="linkExcluirX">Excluir X</div>
  </div>
</div>
```

- **Id `menuMaisAcoes`, rótulo "Mais ações", botão `btn-ghost dropdown-select-btn`.** O `btn-ghost` é o que combina com os `btn-primary`/`btn-secundario-topo` vizinhos no cabeçalho — o `pill` é 12,5px/600 e foi desenhado para toolbar, então ficava menor e mais leve que os botões do lado.
- **A ação destrutiva mora aqui**, sempre por último, com `.item-perigo` (vermelho por **classe**, nunca `style` inline). Foi o que o usuário levantou: em `contas-pagar-detalhe`, `caixa-lancamento`, `produtos-detalhe` e `ordens-compra-detalhe` o *Excluir* estava solto no rodapé da página — e em Ordens de Compra **o menu já existia**, a ação é que não tinha ido para lá.
- **`min-width` é obrigatório** (§9): menu ancorado à direita cresce a partir de zero e os rótulos longos quebram em duas linhas.
- **O menu tem bind próprio e não pode passar pelo laço genérico de `inicializarDropdownSelect`.** Em Produtos-detalhe ele passou, ganhou dois listeners e abria e fechava no mesmo clique — o bug que o §9 descreve, cometido de novo e pego pelo teste.

**O que NÃO entra no menu**, e a régua é de quem é a ação:
- **ação de lote** (*Excluir selecionados*) fica na **barra de seleção** do rodapé da lista (§8) — é do lote, não do registro;
- **ação de tela** (*Reabrir o período*, no Caixa) fica onde está — não é de registro nenhum;
- **cadastro curto em drawer** (Categorias, Marcas, Depósitos, Endereços, Contas financeiras…) mantém o *Excluir X* no rodapé do painel: ali não há cabeçalho de registro, e esconder um botão atrás de outro num formulário de três campos é clique a mais sem ganho.

**Clonar e imprimir recibo entraram em 29/set/2026** (Conta a pagar), e as duas trazem regra:

- **Clonar copia o QUE se paga, nunca o QUANDO.** Fornecedor, categoria, valor, forma e histórico repetem; **vencimento nasce vazio** e documento não vem (cada conta tem a sua nota). Pagamento, cancelamento e grupo de recorrência são história da conta de origem e ficam lá. O clone **abre em edição e não está gravado** — abre `?clonar=<id>`, com faixa dizendo isso; salvar sem vencimento é barrado.
- **Recibo só existe com pagamento.** Conta sem baixa mostra o item **travado, com o motivo no `title`** — nunca escondido (§13). A folha é impressa por `@media print`, o mesmo caminho do Inventário, e o **valor por extenso** segue a regra do "e": *seis mil setecentos e quarenta*, mas *mil e quarenta* e *mil e setecentos* — o "e" antes do último grupo só entra quando o resto é menor que cem ou centena redonda. Recibo com português errado não vale como recibo.
- **O recibo é emitido pelo fornecedor**, não por nós: o corpo diz *Recebi(emos) de: \<a empresa\>* e a assinatura do rodapé é a dele.

**Tela de registro nova nasce com o menu**, mesmo que só tenha uma ação dentro. E o menu some quando não há registro carregado (`display = registro ? '' : 'none'`) — menu vazio é pior que menu ausente.

## 10. Drawer lateral (`.event-drawer`)

Painel de 400px deslizando da direita (`right:-420px` → `right:0`), com backdrop escurecido. Usos:
- **Preview rápido** nas listagens (resumo + link pro detalhe completo).
- **Edição secundária** dentro de uma página de detalhe (ex: editar uma combinação específica da grade de variações de um Produto).
- **Padrão único pra criar/editar registro em toda listagem de cadastro** — mesmo um formulário curto (ex: Marcas de Produtos, só 3 campos) usa o drawer completo, nunca um popover ou modal menor à parte. **Já existiu uma tentativa de popover leve** (`.marca-popover`, sem backdrop, 320px, ancorado no elemento clicado) especificamente pra Marcas — **revertida em setembro/2026 a pedido do usuário**, que preferiu manter o padrão único de drawer em todo o sistema (a "limpeza visual" desejada veio, em vez disso, do campo de Loja(s) virar dropdown — ver §9.1). Não reintroduzir popover de cadastro sem alinhar antes.
- **Painel mocado de credencial** (novo, Vendedores — ver §11): mesmo componente visual, usado pra pedir senha de acesso em vez de editar um registro.

## 10.1 Modo leitura × painel lateral (22/set/2026)

`body.modo-leitura` esconde os campos do **formulário** e mostra `.campo-leitura` no lugar. Mas um **painel lateral abre POR CIMA de um registro em leitura** — o painel de Pagamento da conta a pagar é o caso — e os campos dele têm de continuar vivos. Sem a regra abaixo o painel abre só com rótulos, e o defeito não aparece em teste de formulário nenhum: só quando alguém abre o painel sem ter clicado em *Editar* antes.

```css
body.modo-leitura .event-drawer .form-field input,
body.modo-leitura .event-drawer .form-field textarea,
body.modo-leitura .event-drawer .form-field .dropdown-select,
body.modo-leitura .event-drawer .form-field .auto-wrap,
body.modo-leitura .event-drawer .form-field .date-field,
body.modo-leitura .event-drawer .form-field .field-hint { display:block; }
body.modo-leitura .event-drawer .campo-leitura { display:none; }
```

**A regra é esta:** o modo leitura é do **documento**, não dos painéis. Toda tela de detalhe com modo leitura e painel com formulário precisa dela.

## 10.2 Cross-link do menu — `data-href` (22/set/2026)

O flyout do menu lateral sempre soube navegar:

```js
const destino = sub.getAttribute('data-href');
if (destino) { window.location.href = destino; return; }
path = [path[0], sub.getAttribute('data-label')];   // sem destino, só move o breadcrumb
```

Faltava o atributo. Em 22/set/2026 ele foi colocado em **31 itens** — todos cujos arquivos existem — nas **53 telas de uma vez**. **Tela nova nasce com o item apontando para ela:** ao construir uma tela, acrescente o `data-href` do item correspondente na varredura, senão ela nasce inalcançável pelo menu.

Item sem tela continua inerte, exatamente como antes. A mudança é **aditiva** — a auditoria rodou nas 53 telas antes e depois e o resultado foi idêntico.

## 10.3 Botão que leva a outra tela, e porta de entrada do detalhe (29/set/2026)

**Botão cuja tela existe NAVEGA.** Aviso é para o que depende de servidor (upload de XML, persistência), de módulo que ainda não existe (Relatórios, Pedidos) ou de coisa externa (NF-e) — e o aviso **nunca promete data** ("no fim da fase" vence e vira mentira). Até 29/set, 19 botões em 10 telas do Estoque respondiam *"a navegação entre telas só passa a funcionar no sistema de produção"* ou *"é a próxima tela a ser construída"* para telas que já existiam — as listagens de Ordens de Compra e de Entrada de Notas nem tinham caminho para o próprio detalhe. `_ferramentas/teste_becos.py` reprova essas frases e confere cada destino.

**Parâmetros de URL que as telas entendem** — quem navega passa, quem chega lê:

| Parâmetro | Tela | Efeito |
|---|---|---|
| `?novo=1` | os 5 detalhes de Cadastro | abre **em edição** (Incluir) |
| `?editar=1` | os 5 detalhes de Cadastro | abre **em edição** ("Editar cadastro completo" do painel da listagem) |
| — (sem parâmetro) | os 5 detalhes de Cadastro | segue a preferência **Ao abrir um cadastro existente** (Interface do usuário; padrão: visualização) |
| `?id=` · `?clonar=` · `?renovar=1` | Conta a pagar | abre a conta, o clone ou a renovação (§9.4) |
| `?clonar=1` | Ordem de Compra | clone em edição: número a gerar, data de hoje, previsão vazia, *em aberto* |
| `?receber=1` | Conferência de Entrada | chega com o modal *Receber mercadorias* aberto |
| `?nota=` | Conferência | conta a nota pedida (só as 4 conferíveis; outra cai na 9051, e o breadcrumb diz 9051) |
| `?clonar=<nº>` | Pedido de Venda | clone **já preenchido** em edição: mesmo cliente, loja, vendedor, itens, preços e descontos; número a gerar, data de hoje, *em aberto* |
| `?produto=` | Controle de Estoques — detalhe | abre o saldo do produto |

No protótipo, detalhe que não lê `?id=` (Ordem de Compra, Nota de Entrada, os 5 Cadastros) mostra o registro de exemplo — inclusive no `?novo=1`. No sistema de produção o registro novo abre vazio. **Toda porta de entrada de um detalhe é testada** (Incluir, Editar, consulta): o modo leitura de 28/set fez o *Incluir* dos 5 cadastros cair num registro somente-leitura, e só um teste por porta pega isso.

## 11. Padrão de página de Detalhe (Cadastro)

- Abas (`.tab-item`/`.tab-panel`) + dentro de cada aba, `.form-row`/`.form-field` + `.section-title` pra dividir blocos. Nem todo cadastro precisa de abas — só quando o formulário é grande o suficiente pra justificar (regra de bom senso, não numérica). Lojas Desk, por ter poucos campos, é o único cadastro de página única sem abas até a versão com Histórico de Metas — a partir dela, ganhou 2 abas (Dados Gerais + Histórico de Metas). Vendedores, por ter um formulário grande (fiel ao cadastro completo do Olist), usa **3 abas**: Dados Gerais, Acesso e Permissões, Comissionamento — divisão nossa (o Olist original usa rolagem única); ver §12.
- **Título (H1) dinâmico — regra dura, sem exceção, pra toda tela de detalhe nova:** atualiza ao vivo, a cada tecla, conforme o campo "Nome" é editado (`input` event, não `change`). Se o campo estiver vazio, mostra um placeholder tipo "Novo Produto"/"Nova Loja"/"Novo Vendedor" — mesma página serve pra criar e editar, não existe tela separada só pra digitar o nome. Confirmado em Produtos, Lojas Desk e Vendedores.
- **Cor automática por Tipo** (padrão novo, Lojas Desk): quando um cadastro tem um campo Tipo com poucas opções fixas, **não** oferecer campo de cor manual (swatch) — em vez disso, a cor do avatar de iniciais é derivada automaticamente do Tipo, via regra fixa no front (ex: Produtos = azul, Serviços = laranja, Trade Marketing = cinza). Zero campo, zero decisão manual do usuário, ainda dá variedade visual na lista. Usar sempre que o Tipo já teria poucas opções fixas — não vale a pena reintroduzir cor manual "pra ficar bonito". **Mesmo princípio aplicado em Departamento/Seção de Produtos: cor do dot/badge deriva da Categoria-mãe, sem swatch próprio (ver §12).** **A cor do TEXTO dentro do avatar não é branco fixo** — regra estabelecida em Depósitos (set/2026, ver §14): fundo e cor de texto vivem juntos numa classe CSS por tipo (`.av-geral`, `.av-galpao`…), com a cor do texto redefinida em `body.dark`, porque um mesmo token (`--chart-1`, `--text`, `--warning`) troca de claro pra escuro entre os temas e o branco deixa de ser legível em cima dele. O nome da classe é escrito por extenso num mapa em JS (`CLASSE_AVATAR`), nunca montado por concatenação (`'av-' + tipo`), senão a auditoria de "classe sem CSS" não consegue enxergá-la. Em Vendedores, a cor do avatar deriva do **tipo da Loja Desk vinculada** (ou de um tom neutro fixo quando é autônomo — ver abaixo), mesmo mecanismo.
- **Vínculo opcional a outro cadastro = "autônomo" quando vazio** (padrão novo, Vendedores → campo "Loja Desk vinculada"): quando um cadastro pode opcionalmente se ligar a outro (aqui, um Vendedor a uma Loja Desk de qualquer tipo — Produtos, Serviços ou Trade Marketing), usar um dropdown de seleção única comum (§9) com uma opção explícita no topo do menu tipo "Nenhuma — vendedor autônomo", em vez de um checkbox "sem vínculo" separado. Deixar esse campo vazio **não bloqueia nada** do cadastro — o vendedor continua acessando o sistema, vendendo e finalizando vendas normalmente conforme as permissões marcadas na aba Acesso e Permissões; o único efeito é que o resultado dele **não entra no faturamento nem nos relatórios de nenhuma Loja Desk** (fica "fora" da contabilização por loja).
- **Contato repetível (Rótulo + Número)** (padrão novo, Lojas Desk): quando um cadastro precisa de mais de um telefone/contato, usar uma lista repetível — cada linha com dois campos (`Rótulo`, ex: "Gerente", + `Número`) e um botão de remover, com um link "+ Adicionar contato" abaixo da lista. Versão simplificada da tabela de Pessoas de Contato do Fornecedores (que tem 5 colunas); usar essa versão enxuta sempre que só o contato básico for necessário, sem precisar de e-mail/setor/ramal.
- **Aba de histórico só-leitura** (padrão novo, Lojas Desk → Histórico de Metas): quando um cadastro tem dado periódico gerado por **outra tela** (ex: Metas, lançadas em Vendas), a aba dentro do cadastro só **exibe** esse dado (com filtro próprio, ex: Ano/Mês) — nunca escreve. Editar sempre acontece na tela de origem. No caso de Metas especificamente: mostra **Meta, Realizado e Situação** (Situação = Realizado − Meta, verde quando bateu/positivo, vermelho quando não bateu/negativo) + uma **linha de total** no rodapé da tabela somando as 3 colunas pro período filtrado.
- **Editar período já fechado** (padrão novo, Metas): quando a edição de um dado passado pode mascarar uma comparação/análise já feita (ex: mudar a meta de um mês que já virou histórico), a tela dispara o modal de confirmação padrão (§8) com um aviso explícito — **não** é senha nem permissão real (o sistema ainda não tem login/sessão), é só fricção proposital. Trocar por permissão de admin de verdade quando Configurações → Permissões de Usuários existir.
- **Checklist de módulos/permissões (linhas soltas, fora de dropdown)** (padrão novo, Vendedores → "Módulos que podem ser acessados pelo vendedor"): quando a lista de opções é longa e todas cabem visíveis de uma vez, sem precisar economizar espaço, usar `.item-checkbox` em linhas simples (`.checklist-row`, label + checkbox), **não** dentro de um dropdown — o dropdown multi-seleção (§9.1) é só pra quando o espaço é escasso e a lista precisa ficar compacta atrás de um resumo/botão. Mocado (não é permissão real ainda) até existir permissão de usuário de verdade em Configurações.
- **Painel "Criar/Alterar senha de acesso" (mocado)** (padrão novo, Vendedores): pra cadastros que representam alguém que vai logar no sistema, o botão "Salvar" do formulário, além de gravar o registro, abre um **drawer lateral dedicado** (§10) pedindo a nova senha do próprio cadastro + confirmação + a senha de quem está autorizando (gerente/owner) — tudo mocado (só valida formato/preenchimento: senha entre 12 e 32 caracteres, confirmação igual, senha do gerente não pode ficar em branco; nenhuma credencial real é checada) até o sistema de Usuários (Configurações → Cadastro de Usuários/Permissões de Usuários) existir de verdade. O mesmo drawer é reaproveitado — só trocando o título pra "Alterar senha de acesso" — a partir de "Mais ações" num cadastro já existente, sem passar pelo fluxo de Salvar. Usar esse padrão em qualquer cadastro futuro que também represente um login (ex: se Transportadora ganhar acesso próprio ao sistema). **Todo `input[type="password"]` dentro desse painel leva o "olhinho" de mostrar/ocultar** (`.input-senha` — wrapper relative + botão `.toggle-senha-btn` absoluto à direita, dois SVGs de olho aberto/fechado alternados via `display`, ajustado em set/2026 a pedido do usuário pra ficar "no mesmo padrão" de campo de senha esperado) — o campo nasce oculto (`type="password"`) e volta a nascer oculto toda vez que o drawer é reaberto (não herda o estado do uso anterior). Usar esse mesmo componente em **qualquer** campo de senha novo do sistema, não só neste painel. **A regra de estilo base do formulário (`.form-field input[...], .form-field select, .form-field textarea`) precisa listar `input[type="password"]` explicitamente ao lado de `input[type="text"]`** — não basta o campo estar dentro de `.form-field`/`.input-senha`; sem o seletor de tipo certo, o campo cai no estilo padrão do navegador (fundo branco) enquanto oculto, e só parece "correto" depois que o JS troca pra `type="text"` (ver bug corrigido em §14). Também recomendado neutralizar o autofill do navegador (`input:-webkit-autofill` com `-webkit-box-shadow` e `-webkit-text-fill-color` forçando as cores do tema) pra uma senha salva pelo navegador não vazar fundo claro por cima do tema escuro.
- **Campos fiscais reservados**: qualquer campo que só faça sentido com NF-e **emitida por nós** (NCM, CEST, IPI, SPED etc.) nasce **visível mas desabilitado**, com `field-hint` explicando "Reservado — usado quando a emissão de NF-e for habilitada." Mesmo padrão em Clientes e Produtos. **Exceção: documento de entrada.** Em Fornecedores, Ordens de Compra, Notas de Entrada e Conferência os campos fiscais (IPI, ICMS ST, base de cálculo) são **ativos** — eles descrevem o imposto que o *fornecedor* cobrou de nós, e isso existe independente de emitirmos NF-e. A regra dos campos reservados vale para a saída, não para a entrada.
- **Campos "mock, aguardando cadastro futuro"**: enquanto um módulo referenciado (Marcas, Embalagens, Vendedores, Transportadora) ainda não existia de verdade, o campo correspondente em Produtos-detalhe ficava **interativo** com uma lista de exemplo + `field-hint` avisando que a lista real viria do módulo. **Marcas, Embalagens e Vendedores já saíram dessa categoria** (ver §12) — o campo em Produtos-detalhe deve passar a consultar os cadastros reais assim que a integração for feita; só Transportadora continua nesse estado por enquanto.
- **Autocomplete com criação inline** (ex: campo Marca): digitar filtra uma lista já cadastrada; se não existir e o usuário der Enter, abre o modal de confirmação (seção 8) perguntando se quer criar — item novo entra na lista e fica selecionado.
- **Upload de imagem**: sempre upload direto do computador (dropzone), nunca pedir link manual — o arquivo sobe pro Supabase Storage por trás (bucket dedicado por módulo, ex: `product-images`), e só a URL resultante fica salva no registro.
- **Diagramas dinâmicos**: quando um campo tem opções com formatos visuais diferentes (ex: Tipo da embalagem: Caixa/Envelope/Rolo), o formulário troca tanto os campos exibidos quanto um SVG ilustrativo ao lado, conforme a opção escolhida. **Implementado de verdade em Embalagens de Produtos** (`DIMENSOES_CONFIG`/`renderDimensoes`, ver §12) — o mesmo padrão que já existia como preview em Produtos-detalhe.
- **Exclusão individual**: link "Excluir [item]" no fim da página, sempre abrindo o modal de confirmação (seção 8), nunca uma confirmação inline própria. Em Vendedores, esse gatilho fica dentro de "Mais ações → Excluir vendedor" (não um link solto no rodapé) e resulta em exclusão suave, não definitiva — ver §8.1.

## 11.1 Badge de situação e resumo de valores (22/set/2026)

Dois pedaços nascidos em Contas a Pagar, com uso geral em qualquer tela que tenha estado e dinheiro.

**`.sit-badge`** — a situação ao lado do título da página, com a mesma bolinha colorida das abas da listagem. Fica *dentro* do `<h1>`, não numa linha própria: a situação é parte do nome do registro, não um dado a mais.

```html
<h1>Conta a pagar <span class="sit-badge atrasada"><span class="sit-bola atrasada"></span>atrasada</span></h1>
```

Cores das bolinhas, valendo para o sistema inteiro: **em aberto** `#2E9E5B` · **atrasada** `var(--danger)` · **paga** `#9a9890` · **cancelada** `#4b4b52`.

**`.pg-resumo`** — a faixa de três números (valor · pago · saldo) no topo da aba de pagamentos. Rótulo pequeno em caixa alta, número grande com `tabular-nums`, e o saldo em `var(--danger)` quando sobra algo a pagar.

**`.cx-previa`** — a caixa *"o que vai acontecer"*, que já existia no painel de pagamento e virou padrão: antes de uma ação que escreve em outra tela, a prévia diz em uma frase o que vai ser criado e onde. Usada na baixa (*"sai R$ X de Caixa; no Caixa, uma saída de…"*) e na repetição (*"3 contas somando R$ 1.000,00…"*).

**A regra por trás das três:** o usuário não deve descobrir o que o sistema fez **depois** que ele fez.

## 11.2 Cadastro rápido de pessoa — onde entra e onde não entra (30/set/2026)

**Decisão do usuário, e ela corrige uma contradição minha.** Em 16/set eu havia registrado o cadastro rápido como *"componente compartilhado que qualquer campo de pessoa pode abrir"*; em 22/set eu o descartei — *"seria um segundo formulário de pessoa, e formulário duplicado diverge do original em semanas"*. As duas linhas viveram no mesmo arquivo por oito dias. A segunda foi tomada olhando só para o **lançamento do Caixa** e ficou registrada como decisão geral, que ela não era.

**A régua que faltava:** o cadastro rápido entra onde a pessoa é **parte obrigatória do documento**, e não entra onde ela é **anotação**.

| onde | a pessoa é | cadastro rápido |
|---|---|---|
| Pedido de Venda | obrigatória — sem cliente não há venda, e é dele o endereço de entrega, o CPF/CNPJ da nota e a conta a receber | **entra** |
| Conta a Receber | obrigatória, mesma razão | **entra** |
| Lançamento do Caixa | anotação num movimento (tarifa, sangria, aporte) | **não entra** — decisão de 22/set continua valendo |

Três amarras que eliminam o motivo da recusa original:

1. **É bloco dentro do próprio documento, não uma segunda tela.** Expande no lugar, abaixo da busca que não achou ninguém — é o que o Olist faz. Os campos saem da **mesma definição** do cadastro completo, renderizados em subconjunto: uma fonte só, então não há o que divergir.
2. **Conjunto mínimo é o que a venda exige:** tipo de pessoa, nome, CPF/CNPJ, CEP (que preenche cidade e UF), endereço e telefone. Contribuinte, inscrição estadual, limite de crédito e condição de pagamento ficam para o cadastro completo.
3. **O registro nasce marcado como incompleto e o sistema diz isso** — no documento (*"primeira venda para este cliente; clique para completar os dados"*) e na listagem de Clientes, com filtro próprio. Sem essa terceira amarra a base enche de cliente pela metade e ninguém descobre por meses: é ela que impede o atalho de virar dívida silenciosa.

## 11.3 Rodapé de salvar (`.barra-salvar`) — 08/out/2026

Um nome só, em todas as telas que gravam alguma coisa. **Isto é rodapé de
PÁGINA** — dentro de drawer e de modal o botão continua à direita, que é a
convenção de caixa de diálogo e está certa lá.

```html
<div class="barra-salvar" id="barraSalvar">
  <button class="btn-primary" id="btnSalvar">Salvar alterações</button>
  <!-- opcional: um ou mais .btn-secundario, ex. "Salvar e continuar depois" -->
  <div class="drawer-link" id="btnVoltarRodape">Voltar pras ordens de compra</div>
  <div class="barra-info" id="infoPendente">—</div>
</div>
```

```css
.barra-salvar { display:flex; align-items:center; gap:16px; position:sticky; bottom:0;
                background:var(--page-bg); border-top:1px solid var(--border);
                padding:14px 0; margin-top:26px; z-index:20; }
.barra-info   { font-size:12.5px; font-weight:700; color:var(--text); margin-left:auto; }
```

**Por que o botão fica à esquerda.** Direita é a convenção de **diálogo**: caixa
estreita, o olho termina no canto inferior direito. Um rodapé de página
atravessa ~1050px. Com o botão à direita, você edita um campo à esquerda e
viaja a tela inteira para confirmar — e a nota de estado não tem onde morar sem
espremer o botão. Com ele à esquerda, o `margin-left:auto` da nota lhe dá a
ponta direita inteira.

**O link do meio diz para onde vai, nunca "Cancelar".** "Cancelar" ao lado de
"Salvar" parece desfazer, e nas seis telas onde ele existia era um `<a href>`
puro: saía da página levando junto tudo o que não tinha sido gravado, calado.
Escreva o destino — "Voltar pra listagem", "Voltar pro caixa", "Voltar para a
fila". Quando o botão **de fato** descarta as alterações sem sair (Minha
Conta), o nome é "Descartar alterações"; aí ele está dizendo a verdade.

**Sair com alteração pendente para e pergunta**, pelo modal de confirmação da
§8 em vermelho. Vale nos **dois** caminhos de saída, o link do rodapé e o do
topo (`a.voltar-link`): avisar só num deles é pior que não avisar, porque
ensina que a tela avisa.

**A nota conta, não adjetiva.** "3 campos alterados, ainda não salvo." é melhor
que "alterações não salvas" — com o número dá para saber se o pendente é o
campo que você acabou de mexer ou mais quatro que ficaram numa aba fechada.
Limpa, ela diz "Nenhuma alteração pendente." e **nunca fica vazia**: vazio não
informa, pode ser "nada mudou" ou "a tela parou de olhar". Cada tela escolhe o
substantivo — campo, parâmetro, meta, código, quantidade.

**A referência nasce depois de a tela se montar.** Esta é a armadilha, e ela é
silenciosa:

```js
if (document.readyState === 'complete') setTimeout(marcarSalvo, 0);
else window.addEventListener('load', () => setTimeout(marcarSalvo, 0));
```

Medida cedo demais, a referência congela um formulário vazio. A nota continua
dizendo "Nenhuma alteração pendente" — não porque seja verdade, mas porque
parou de olhar — e só se descobre quando alguém digita. Aconteceu em Pedidos de
Venda, onde o cliente e os itens entram depois. `teste_rodape.py` [3] mede
exatamente isso: a referência guardada tem de descrever a tela que está ali.

**A raiz do rastreio é `.main`, não `#card`.** Nesta família de telas `#card` é
a **sidebar**. Com a raiz errada o rastreio escuta os campos do menu e nunca vê
o formulário.

**Nomes aposentados, que `teste_rodape.py` [1] impede de voltar:**
`.form-footer-bar`, `.par-barra`, `.par-barra-nota`, e `.form-actions` servindo
de rodapé de página. O preço de ter mais de um nome já foi cobrado: em Pedidos
de Venda alguém renomeou o CSS para `.barra-salvar` e esqueceu o HTML, que
ficou em `.form-footer-bar` — classe que naquela tela só existia dentro de
`body.modo-leitura`, para esconder. Em modo de edição a barra era uma `div`
crua, sem sticky, sem borda, sem espaçamento, e ninguém percebeu. Ver §14.

## 12. Módulos de Cadastro construídos até aqui

| Módulo | Arquivo(s) | Observação |
|---|---|---|
| Clientes | `pagina-cadastros-clientes.html` + `-detalhe.html` | Listagem com paginação + detalhe com abas |
| Fornecedores | `pagina-cadastros-fornecedores.html` + `-detalhe.html` | Campos fiscais ativos (não reservados — precisa pra NF-e de entrada) |
| Categorias | `pagina-cadastros-categorias.html` | Lista única — sem subcategoria; tipo Produtos/Fornecedores; loja aplicável só quando tipo=Produtos (checkboxes inline, §8). **Alinhada ao padrão canônico em setembro/2026**: nomenclatura de seleção (`barraSelecao`/`selecaoInfo`), paginação padrão (§7) com "Selecionar todos" escopado à página atual, e o bug do `.theme-seg` corrigido (ver §14) |
| Produtos | `pagina-cadastros-produtos.html` + `-detalhe.html` | O mais completo: 6 abas, variações com grade dinâmica, cascata Loja→Categoria→Departamento→Seção |
| Lojas Desk | `pagina-cadastros-lojas-desk.html` + `-detalhe.html` | Preview lateral (não drawer de edição) + detalhe com 2 abas (Dados Gerais, Histórico de Metas); cor automática por Tipo; contato repetível. **Campo "Depósito padrão" adicionado em set/2026** — define de qual depósito saem os pedidos vendidos por esta loja (roadmap §3 item 20). **Paginação padrão (§7) adicionada em set/2026**, junto com o componente `.dropdown-select` completo que a página ainda não tinha — era a última listagem de cadastro sem o rodapé (ver §14) |
| Metas | `pagina-vendas-metas.html` (menu Vendas) | 4 modos de preenchimento (Mensal/Trimestral/Anual/Progressivo), sempre grava por mês; único ponto de escrita — Lojas Desk só lê via aba Histórico |
| Departamento de Produtos | `pagina-cadastros-departamento-produtos.html` | Lista única, mesmo padrão de Categorias mas com nomenclatura de seleção **canônica** (`barraSelecao`/`selecaoInfo`/`checkbox-todos`) + campo `status`/"Inativar selecionados" (Categorias não tem); cor do dot deriva da Categoria-mãe, sem swatch próprio; **paginação padrão (§7) adicionada em set/2026** — "Selecionar todos" passou a valer só pra página atual |
| Seção de Produtos | `pagina-cadastros-secao-produtos.html` | Igual a Departamento, com cascata Categoria→Departamento no filtro e no drawer; **paginação padrão adicionada em set/2026** (mesmo padrão) |
| Embalagens de Produtos | `pagina-cadastros-embalagens.html` | Sem cascata (não depende de outro cadastro); campo Tipo (Pacote/Caixa, Envelope, Rolo/Cilindro) troca os campos de dimensão exibidos E o diagrama SVG ao lado (`DIMENSOES_CONFIG`/`renderDimensoes`, mesmo padrão já usado como preview em Produtos-detalhe); campo de peso próprio; **paginação padrão adicionada em set/2026**; teve um bug real de wrapper CSS errado ("Selecionar todos" fora do lugar) corrigido no mesmo mês (ver §14) |
| Marcas de Produtos | `pagina-cadastros-marcas.html` | Cadastro simples: nome + Loja(s) aplicável(is) — usa a variante **dropdown multi-seleção** (§9.1) em vez da lista de checkboxes inline, pra deixar o formulário mais compacto. O dropdown **recolhe automático a cada loja marcada/desmarcada** (ajustado em set/2026 — ver §9.1); pra marcar mais de uma loja, o usuário reabre o dropdown e marca de novo. O filtro de Loja na toolbar usa o mesmo mecanismo que, dentro do cadastro de Produtos, deve pré-filtrar a lista de Marcas disponíveis pela loja de origem escolhida; **paginação padrão adicionada em set/2026**; criação/edição usa o **drawer lateral padrão** (§10, igual às outras listagens) — um popover mais leve foi testado em set/2026 e revertido a pedido do usuário, que preferiu manter o padrão único de drawer |
| Depósitos | `pagina-cadastros-depositos.html` | Lista única + drawer (sem página de detalhe — cadastro curto). **Interruptor "Usa endereçamento" adicionado em set/2026** (nasce ligado; desligado aparece como "sem endereçamento" na meta da listagem) — é ele que decide se o saldo daquele lugar precisa de endereço pra ficar vendável (roadmap §3 item 19). Campos: nome, `tipo` (Geral/Galpão/Loja Física/Trade Marketing/Trânsito, com **cor automática por Tipo**, §11), Loja Desk vinculada **opcional** (vazio = "Depósito do hub", mesmo padrão do "autônomo" de Vendedores), **interruptor "Depósito principal"** (um só no sistema — marcar aqui desmarca o atual, e o principal é forçado a `ativo`), endereço opcional, situação. **Segundo módulo com exclusão suave** (§8.1), com 3 abas de filtro. Primeira tela a usar o interruptor `.switch` dentro de um formulário (`.switch-row`) e a resolver a cor de texto do avatar por contraste real de tema (§11) |
| Vendedores | `pagina-cadastros-vendedores.html` + `-detalhe.html` | Cadastro completo, seguindo fielmente o modelo de campos do Olist (referência enviada pelo usuário) — listagem com paginação + detalhe com **3 abas** (Dados Gerais, Acesso e Permissões, Comissionamento; ver §11 sobre a divisão em abas ser decisão nossa, não do Olist). Campo próprio, fora da referência: **"Loja Desk vinculada"** — opcional, qualquer tipo de loja; vazio = vendedor "autônomo" (vende e acessa o sistema normalmente, mas não gera resultado de faturamento/relatório pra nenhuma loja). **Primeiro módulo do sistema com exclusão suave** (`excluido`, independente da `situacao` — ver §8.1), com 5 abas de filtro na listagem em vez das habituais. Ao clicar em Salvar, abre o painel mocado "Criar senha de acesso" (§10/§11), exigindo a senha do vendedor + a senha do gerente/owner autorizando — também reaproveitado via "Mais ações → Alterar senha de acesso" pra cadastro já existente. Checklist de módulos acessíveis (`.checklist-row`, 11 itens fiéis ao Olist) e dropdown multi-seleção pra "Perfis de contato acessíveis" (§9.1); primeiro uso de botão de opção (rádio) customizado (§8) e de campo com sufixo percentual (`.input-percent`) no Comissionamento |
| Endereços de Estoque | `pagina-cadastros-enderecos-estoque.html` | Lista única + **dois drawers** (editar e gerar em massa) — primeira tela do sistema com dois painéis laterais distintos dividindo o mesmo backdrop. O **código é derivado** de 4 campos curtos (Corredor · Estante · Nível · Posição) com **preview ao vivo a cada tecla** (mesma regra do título dinâmico, §11); só o corredor é obrigatório. Valida **duplicidade dentro do mesmo depósito**. **Gerador em massa** monta o produto cartesiano das faixas, mostra quantos serão criados, de qual até qual e quantos já existem e serão ignorados; a criação passa pelo modal azul com trava do "estou ciente" (§8). Exclusão definitiva (não soft-delete: com gerador em massa a lista encheria de registros mortos), bloqueada quando o endereço tem produto alocado. Primeira tela com **paleta categórica própria** (`.tt-*`, 6 tipos) — os tokens do design system não serviam como cor de texto, ver §14 **Aviso de configuração faltando** (set/2026): o cadastro passa a apontar, no topo, os depósitos que **usam endereçamento e não têm nenhuma posição ativa** — essa combinação trava todo o saldo daquele depósito calada, porque a mercadoria entra, é conferida e morre na fila de endereçar sem nunca ficar disponível. Aponta também o inverso, depósito com posição cadastrada que não usa endereçamento, onde as posições não servem a ninguém. O aviso ignora o filtro da tela: a configuração que falta continua faltando mesmo que você esteja olhando outro depósito. |
| Ordens de Compra | `pagina-estoque-ordens-compra.html` (menu Estoque) | Listagem em tabela (§7.1) com **abas de situação contadoras** (§7.2) — Todos / Em aberto / Em andamento / Atendidas / Canceladas — e **filtro de período em popover** (§7.3). Colunas: Número, Data, Previsto, Fornecedor, **Depósito**, Total, Marcadores, Situação. Ciclo confirmado pelos prints: *em aberto → em andamento (recebida em parte) → atendida*, fora de cancelada. **Campo próprio nosso: Depósito de destino** — o Olist só o traz na nota de entrada, mas com saldo por depósito e endereçamento obrigatório a OC já precisa dizer para onde a mercadoria vai, senão a nota não sabe onde criar o saldo `em_conferencia`. Rodapé com contagem + valor total, que **exclui as canceladas** (ordem cancelada não vira compra). Ordem já recebida (em andamento/atendida) **não pode ser excluída** — a seleção em massa a separa do lote e o modal diz quantas foram ignoradas; a saída é cancelar. Preview lateral mostra os itens com o **recebimento parcial por item** ("recebido 12 de 30"), que é o que a conferência confere contra |
| Ordens de Compra — detalhe | `pagina-estoque-ordens-compra-detalhe.html` (menu Estoque) | Formulário completo, a maior tela do módulo. **Primeira tabela editável do sistema** (`.itens-table`): cada célula é um input, os totais recalculam a cada tecla e **só o total da linha é reescrito**, nunca a tabela inteira — reescrever tudo faria o campo perder o foco a cada dígito (regra dura para qualquer tabela editável futura). **Grade de totais** (`.totais-grid`) mistura valores calculados (produtos, IPI, geral) e editáveis (desconto, frete, ICMS ST), com o Total geral em destaque. **Parcelas geradas da condição de pagamento**: aceita prazos em dias ("30 60 90") ou número de parcelas ("3x" → 30/60/90), e **a última parcela absorve a sobra do arredondamento** para a soma bater com o total exato. **Blocos expansíveis do fornecedor** (`.bloco-expansivel`) — dados e pessoas de contato abrem no lugar, um fecha o outro; últimas compras abre em drawer. **Busca avançada de itens** mostra saldo, localização e custo médio de cada produto: quem compra precisa ver o estoque antes de pedir. Campos fiscais **ativos** (§11) com aviso explicando por quê. Excluir bloqueado quando a ordem já recebeu mercadoria, mesma regra da listagem |
| Controle de Estoques | `pagina-estoque-controle-estoques.html` (menu Estoque) | Primeira tela de **consulta em tabela** do sistema (§7.1) e primeira do módulo Estoque. Colunas: Produto (com tipo + GTIN na sublinha), Código (SKU), Preço, Custo médio, **Estoque físico** (com a unidade como sufixo, e a quantidade formatada conforme a unidade — ver §6), Mínimo, **Reservado** e **Disponível** (desabilitados, ver abaixo), Localização — todas ordenáveis por clique. Filtros: busca com **refinar** (não refinar / SKU / GTIN-EAN / descrição / localização), **Depósito**, situação do saldo (todos / com saldo / sem saldo / abaixo do mínimo / negativo) e abas de tipo (todos / simples / kits / matéria-prima). Saldo é **derivado por par (produto, depósito)**: com "Todos os depósitos" soma, com um depósito escolhido mostra só o dele — e o produto some da lista se não existir naquele depósito. Alerta em vermelho com ícone quando o saldo fica abaixo do mínimo ou negativo. Rodapé com contagem de produtos e **valor total em estoque** (soma de saldo × custo médio do filtro inteiro, nunca só da página). Clicar na linha abre o drawer de **extrato**: saldo por depósito + últimas movimentações, tudo somente leitura. **Reservado e Disponível nascem desabilitados** com uma nota explicativa acima da tabela — dependem de `orders` (F3/F4); mesmo tratamento dos campos fiscais (§11) |
| Controle de Estoques — detalhe do produto | `pagina-estoque-controle-estoques-detalhe.html` (menu Estoque) | **Construída em 15/set/2026.** Substitui o drawer de extrato da v1 — o drawer era a exceção num sistema onde todo o resto já tem `-detalhe`. Traz a **faixa de KPIs com a quebra completa dos estágios** (físico · a endereçar · bloqueado · reservado · disponível), mais **em conferência num painel separado, tracejado**, porque não é estoque. É essa faixa que permite a listagem ficar rasa em 9 colunas. Abas **Lançamentos / Reservas** (§7.2); reservas nasce com estado vazio explicando que depende de `orders`. Ledger com uma coluna que o Olist não tem — **em que estágio o saldo caiu**. O botão **Incluir lançamento** abre o acerto inline: tipo (Entrada/Saída/**Balanço**, que informa a contagem e o sistema deriva a diferença), depósito, data/hora automáticas, quantidade, **Preço unitário visível e travado** no custo médio vigente (§11), **Motivo estruturado e filtrado pelo tipo** — mesmo padrão da Conferência — e **seletor de origem que só aparece quando o produto tem saldo em mais de um estágio**. Saída nunca sai de reservado, e saída maior que o estágio é barrada com o número disponível na mensagem. Motivo com consequência fiscal pinta o **aviso de CFOP 5.927 + estorno de crédito** e, ao salvar, avisa que o lançamento entrou na fila de regularização **Atualizada em 15/set/2026 (fundação do saldo por endereço):** ganhou a aba **Endereços**, que mostra onde o saldo está — endereço, tipo, depósito, estágio e quantidade — marcando a **base de picking** e apontando **↓ repor** quando ela está abaixo do `minimoBase`. É a leitura que o módulo de Reposição vai consumir. O **Incluir lançamento** passou a obedecer a regra de entrada: uma **prévia ao vivo** diz, antes de salvar, para onde o saldo vai — base com espaço livre → *reposição, disponível na hora*; base cheia → *parte na base, excedente a endereçar*; sem base no depósito → *tudo a endereçar, não vende*. A origem da saída deixou de ser estágio solto e passou a ser **linha de saldo (endereço + estágio)**, porque com saldo por endereço o mesmo estágio existe em vários lugares. **Atualizada em 13/out/2026:** a aba **Lançamentos** e os movimentos de exemplo saíram, com os filtros de período e de tipo; o histórico do produto mora em **Movimentação de Estoque**, a página abre em **Endereços**, e todo lançamento fecha com um aviso do que gravou (§14.66). |
| Entrada de Notas | `pagina-estoque-entrada-notas.html` (menu Estoque) | Listagem do documento fiscal que chega do fornecedor. Abas contadoras com o ciclo da nota: **A conferir → Em conferência → Com divergência / Lançada / Recusada** — "lançada" é o único estado que gerou estoque, porque a mercadoria só entra quando a conferência fecha. Coluna nova e específica desta tela: **Manifestação do Destinatário** (badge do evento + prazo que ainda corre), com os prazos legais reais — **10 dias** para Ciência da Emissão, **180 dias** para a definitiva (NT 2020.001 / Ajuste SINIEF 44/20) — contados e pintados de alerta quando vencem. Nome curto do evento na célula, nome oficial no `title` e no drawer: a primeira versão usava o nome completo com `nowrap` e empurrou a tabela 110px além do card (§14). Filtro próprio de manifestação (sem manifestação / prazo vencendo / já manifestada). **Chave de acesso com 44 dígitos e DV calculado de verdade** (módulo 11, pesos 2..9) — chave de mock não é número inventado. Ação em massa de **Ciência da Emissão**, que só se aplica a nota ainda não manifestada; exclusão bloqueada para nota que já lançou estoque. O drawer da nota divergente traz o **procedimento escrito na tela** (escriturar pelo recebido, comunicar o fornecedor, NF complementar ou abatimento, carta de correção não serve) |
| Conferência | `pagina-estoque-conferencia.html` (aberta pela fila de Conferência de Entrada — **sem item de menu**, §12.3) | A tela onde a mercadoria vira estoque. **Conferência cega ligada por padrão, e cega de verdade**: a quantidade da nota só aparece quando não há mais o que esconder — contagem batendo, ou divergência que o conferente **confirmou**. Enquanto a divergência não é confirmada, a tela diz apenas que ela existe (sem o número), esconde a quantidade da nota, segura o "Valor conferido" do resumo e oferece **Recontar** ou **Confirmar contagem** no lugar do motivo; editar a contagem derruba a confirmação. Desligar o modo cego exige confirmação explícita — quem confere conta o que vê, não o que o papel diz. Tabela editável com **Qtde da nota / Conferida / Divergência / Motivo**; `conferida = null` ("não contado") é diferente de zero contado, e fechar com item não contado é barrado. **O motivo é filtrado pelo sinal da divergência** — não existe "faltou" numa sobra nem "chegou a mais" numa falta — e trocar o sinal derruba um motivo que deixou de fazer sentido. **Avaria abre um segundo campo, Destino**: *ficou conosco* (endereço de Avaria, saldo bloqueado) ou *voltou com o transportador* (recusa, em que o **fornecedor** emite a NF-e de entrada) — é a distinção que a pesquisa na legislação trouxe, e a única que a Desk consegue operar hoje sem emitir NF-e. O fechamento abre um **drawer de fechamento**, não um modal: diz para onde cada item vai, pergunta o **saldo da ordem de compra** (manter pendente / encerrar — decisão humana, o sistema não adivinha) e mostra o **comunicado ao fornecedor** já montado. Depois de finalizada a tela trava inteira e só o comunicado continua acessível |
| Nova transferência | `pagina-estoque-transferencia-nova.html` (menu Estoque) | **Construída em 16/set/2026.** Montagem da transferência com a lista na **área principal**, mesmo desenho do Acerto multi-produto: cartão de Origem/Destino, cartão de busca, tabela de itens, rodapé com total. A **busca nasce desabilitada** e só libera quando origem e destino formam um par válido — pedir produto antes de saber de onde ele sai não faz sentido, e o hint explica o porquê em vez de deixar o campo morto sem motivo. Colunas: Produto · Sai de · Estágio · Transferível · Quantidade · **Cai no destino como** · Correção. Essa penúltima coluna calcula a regra do item 19 **antes de enviar**: na mesma tela dá para ver um item indo para a base como *disponível* e outro ficando *a endereçar* por não ter base no destino. O drawer aqui é só a **linha do item** (endereço de origem + quantidade), igual ao Acerto — o seletor de endereço só aparece com mais de um elegível. **Trava de acúmulo:** duas linhas do mesmo produto no mesmo endereço não podem somar mais que o saldo — a segunda já abre mostrando só o que sobrou. Botões **Editar** e **Remover** por linha, com `.btn-mini`; nada sai do estoque até "Enviar para trânsito" |
| Transferência Entre Estoques | `pagina-estoque-transferencia.html` (menu Estoque) | **Construída em 16/set/2026.** Duas etapas, com a viagem acontecendo no **depósito de Trânsito** — tipo que já existia no cadastro de Depósitos, reaproveitado justamente para não precisar de estágio novo. Listagem com abas contadoras (§7.2): **Todas / Em trânsito / Recebidas em parte / Recebidas**. Enviar tira o saldo da origem na hora (a mercadoria foi mesmo) e joga no Trânsito; o destino **não vê nada** até confirmar — se visse, o separador de lá seria mandado a um endereço vazio. Só saldo `disponivel` e `a_enderecar` transferem: reservado está comprometido com pedido e bloqueado é avaria, que transferida só espalha o problema. **Origem = destino** e **empresas diferentes** (item 22) são barrados com mensagem própria; o segundo caminho existe no código e hoje nunca dispara, porque é 1 CNPJ. No recebimento, cada item tem campo editável **pré-preenchido com o que está em trânsito**, uma **prévia ao vivo** dizendo quanto cai na base e quanto fica a endereçar (regra do item 19), e **recebimento parcial é permitido**: o que faltar continua visível em trânsito e a transferência vai para "Recebidas em parte" — quem resolve é um **Acerto** a partir do Trânsito, sem reconstruir a máquina de divergência da Conferência uma terceira vez. Confirmar exige **usuário + senha** e é **permissão de perfil**: sem ela o botão aparece desabilitado com o motivo no `title`, em vez de sumir **Alterada em 16/set/2026 a pedido do usuário:** a montagem da transferência **saiu do painel lateral e virou página própria** (`pagina-estoque-transferencia-nova.html`), nos moldes do Acerto multi-produto — lista de itens na **área principal**, não em drawer. Esta tela ficou só com a listagem e a confirmação de recebimento; o botão "Nova transferência" navega, e o drawer antigo foi **removido inteiro** (markup, JS e variáveis órfãs) em vez de ficar como código morto. |
| Vendedores — checklist de confirmações | `pagina-cadastros-vendedores-detalhe.html`, aba Acesso e Permissões | **Adicionado em 16/set/2026.** Bloco **"O que este usuário pode confirmar com a própria senha"**, logo abaixo dos módulos acessíveis, reaproveitando o mesmo `.checklist-row`. Lista **toda** ação do sistema que pede senha, inclusive as de telas **ainda não construídas** — essas aparecem esmaecidas e desabilitadas, com "tela ainda não construída" na sublinha, em vez de sumirem: lista que esconde o que falta mente sobre o tamanho do sistema. **Regra de ouro:** toda tela nova que pedir senha entra aqui **e** no inventário do roadmap no mesmo passo; confirmação que não aparece no perfil é permissão invisível, e ninguém consegue auditar quem pode o quê |
| Acerto de Estoque (multi-produto) | `pagina-estoque-acerto.html` (menu Estoque) | **Construída em 15/set/2026.** O segundo ponto de entrada do acerto — o primeiro é o "incluir lançamento" inline na página de detalhe do produto. Busca por descrição/SKU/GTIN com **sugestões ao vivo** e **Enter escolhendo a primeira**; selecionar abre o drawer da linha, idêntico ao inline (tipo, depósito, quantidade, preço travado no custo médio, motivo estruturado filtrado pelo tipo, origem por endereço, prévia da regra de entrada, aviso fiscal). "Gravar produto" empilha a linha numa tabela — **nada toca o saldo até finalizar**. O botão Finalizar nasce desabilitado e só liga com pelo menos uma linha. **O lote é atômico:** `validarLote()` percorre tudo ANTES de tocar em qualquer saldo e **soma as saídas do mesmo endereço** (duas linhas de 4 num endereço de 6 não cabem) — se falhar, nada é gravado, a mensagem diz **qual linha** ajustar e as linhas ficam preservadas para correção. Passando, tudo é aplicado de uma vez sob **um número de documento único** (`AC-nnnn`). A confirmação pede **usuário + senha**, reaproveitando o painel de Vendedores (mocado até Configurações → Usuários existir). **Pendência fiscal é parcial:** o resumo do lote conta quantas linhas vão para a fila de NF-e 5.927, e as demais não geram documento nenhum |
| Reposição | `pagina-estoque-reposicao.html` (menu Estoque) | **Construída em 15/set/2026.** A lista é **derivada, não é tabela de tarefas**: sai de `produto_enderecos` e do saldo por endereço, e se atualiza sozinha — sem ciclo de vida para manter sincronizado. **Duas abas, e só duas** (§7.2): **Todos** (todo endereço de picking cadastrado, base cheia ou vazia) e **Necessidade Reposição** (abaixo do mínimo **E** com saldo guardado fora da base — o que dá para repor hoje). Uma terceira aba de "base vazia sem nada guardado" foi construída e **removida a pedido do usuário**: essa lista é, por definição, a da **Necessidade de Compra**, que tem módulo próprio, e duas telas mostrando a mesma coisa é a receita para as duas divergirem depois. Colunas: Produto · Depósito · **Endereço Picking** · Na base · Mínimo · Faltam · Fora da base. Base saudável mostra **—** em Faltam, para a aba Todos não virar um mar de zeros. Clicar abre o drawer de coleta: cada endereço de origem é uma linha com **campo de quantidade editável e pré-preenchido** — a sugestão enche a base até a capacidade, limitada ao que existe naquela origem, porque repor só até o mínimo faria o repositor voltar no dia seguinte; há atalho **"tudo (N)"**. Uma **prévia ao vivo** diz com quanto a base fica e se ela sai da fila, e o botão trava em três casos: quantidade maior que a origem, base estourando a capacidade, e total zero. **Reposição não muda o físico nem o estágio** — move entre endereços, os dois `disponivel` — e a mensagem de confirmação diz isso com todas as letras, porque é a dúvida que o operador teria. **Coleta total encerra o endereço de origem**, que some da lista de saldo e fica livre para outro produto: é o mesmo mecanismo da futura aba Estoque Zero, visto do outro lado. Saldo **bloqueado nunca é origem** — avaria não vira estoque de venda por reposição |
| Endereçamento *(renomeado em 15/set/2026; era "Produtos sem Endereço")* | `pagina-estoque-enderecamento.html` (menu Estoque) | A fila que trava a venda: saldo que entrou, foi conferido e ainda não ganhou endereço — e por isso **não aparece como disponível**, nem no ERP nem nas vitrines. O aviso do topo diz isso com todas as letras, porque é a única tela do sistema cuja lista vazia é a situação boa. Coluna **Parado** conta os dias desde a entrada e **muda de cor sozinha** (>2 dias alerta, >7 crítico): endereçar é tarefa com relógio, não fila infinita. Duas regras duras no drawer de endereçamento, as duas herdadas do cadastro de Endereços: (1) **endereço pertence a um depósito**, então selecionar itens de depósitos diferentes e pedir "o mesmo endereço" é barrado com explicação, não com erro genérico; (2) **saldo bloqueado por avaria só entra em endereço do tipo Avaria**, e continua bloqueado depois de endereçado — misturar com saldo bom num endereço de picking é exatamente como um item avariado acaba vendido. Endereçar dá baixa na fila; o estado vazio explica que aí sim o saldo está disponível **Aba Estoque Zero adicionada em 15/set/2026 — a fila inversa da tela:** endereço de picking existente e reservado ao produto, com saldo **zerado há mais de 7 dias**. A ação fica na coluna **Correção**, como botão **`.btn-mini`** (componente que já existia em Conferência e Entrada de Notas — reaproveitado em vez de criar variante nova) rotulado **"Liberar vaga"**, e **desabilitado** quando há OC em aberto, em vez de sumir: ação que existe mas não cabe agora se mostra travada, não escondida. O verbo continua sendo **desvincular**, nunca "excluir endereço": a prateleira física continua no cadastro, o que sai é o vínculo — e é justamente isso que destrava a regra do cadastro de Endereços, onde a exclusão é bloqueada quando há produto alocado. **Produto com ordem de compra em aberto não é sugerido** (aparece marcado "não sugerido", com o número da OC): a mercadoria está a caminho e liberar a vaga só obrigaria a reendereçar na chegada. A aba **troca a tela inteira** — outra tabela, outra ação e **sem seleção em massa**, porque "endereçar selecionados" não faz sentido para vaga vazia e misturar duas semânticas de seleção numa tela só convida ao erro. Pelo mesmo motivo ela **não entra na contagem de "Todos"**: Todos conta saldo esperando endereço, Estoque Zero conta endereço esperando saldo — somar os dois daria um número que não é fila de nada. O limiar de 7 dias é constante e vai para Configurações → Parâmetros de Estoque. |
| Conferência de Entrada | `pagina-estoque-conferencia-entrada.html` (menu Estoque) | **A fila do galpão** — a tela que vem ANTES da conferência operacional, e que faltava. A mesma nota que Entrada de Notas mostra pelo lado do documento (manifestação, prazos, valor) aparece aqui pelo lado do trabalho físico: **aguardando entrada → pronto para conferir → em conferência → conferida**. Coluna **Espera** conta os dias desde a chegada e muda de cor sozinha (>1 dia alerta, >3 crítico) — e só existe depois que a mercadoria chegou: nota a caminho não está atrasada, está viajando, e conferência fechada para o relógio. O botão **Receber mercadorias** abre um bottom-sheet de leitura feito para quem está com as mãos ocupadas: campo já focado, busca ao vivo por fornecedor, número ou **chave de acesso de 44 dígitos**, primeiro candidato pré-marcado e **Enter resolve** — é o fluxo do leitor de código de barras, que "digita" a chave e dá Enter. Nota já pronta avisa em vez de duplicar o recebimento; nada encontrado sugere importar o XML. Registrar chegada é a única ação em massa — conferir é um a um |
| Nota de Entrada — detalhe | `pagina-estoque-entrada-notas-detalhe.html` (menu Estoque) | O cadastro da nota. A novidade de padrão é o **bloco de pendências no topo** (`.bloco-erros`), no formato do print de referência: aparece só depois da primeira tentativa de salvar, conta quantas são, lista todas de uma vez e **cada item leva ao campo** — inclusive abrindo o bloco expansível do endereço, porque mandar o usuário para um campo invisível é pior que não mandar. As duas camadas convivem: a marca vermelha no campo serve a quem já está olhando pro campo, o bloco serve a quem clicou em salvar e precisa ver o tamanho do problema. Depois da primeira tentativa a lista **encolhe ao vivo** conforme os campos são corrigidos, e some (limpa) quando zera. Validações que valem o nome: **dígito verificador da chave de acesso conferido de verdade** (módulo 11 — chave digitada errada é o erro mais comum de quem lança nota na mão), data impossível reprovada, **data de entrada não pode anteceder a emissão**, item sem nome e item com quantidade zerada. Escolher o fornecedor preenche CEP, endereço, número, bairro, cidade e UF de uma vez — resolve seis pendências num clique. Campos fiscais **ativos** (§11) |
| Tratamento de Perdas *(chamava-se Itens Bloqueados até 12/out/2026)* | `pagina-estoque-itens-bloqueados.html` (menu Estoque) | **Construída em 09/out/2026.** A fila do saldo que está no estoque e não pode ser vendido, com abas por motivo e uma aba de histórico (Resolvidos) que troca a tabela. O painel de resolver tem três abas (Resolver, Manter bloqueado e Histórico) e reparte a quantidade entre liberar e dar baixa; o de bloquear usa a busca padrão de produto e bloqueia ali mesmo. Recebe os bloqueios das outras telas por uma caixa de entrada. Ver §14.51. |
| Necessidades de Compra | `pagina-estoque-necessidades-compra.html` (menu Estoque) | **Construída em 10/out/2026.** Lista **derivada**, como a Reposição: abre já calculada, sem botão "gerar". Quatro indicadores (a comprar, compra sugerida, em falta, segurados pelo giro), cinco abas e a tabela com a coluna **Comprar** editável. **Só o vendável conta como estoque** (disponível mais o que aguarda endereço); o que está chegando soma e os pedidos que vão sair descontam. A conta é por **mínimo e máximo** ou por **dias de cobertura**. Clicar na linha abre **a conta do produto**, que é onde se edita mínimo e máximo. A seleção em massa abre o painel **Ordem de compra**, com um bloco por fornecedor padrão. Ver §14.52 |
| Giro de Estoque | `pagina-estoque-giro-estoque.html` (menu Estoque) | **Construída em 10/out/2026.** Giro (vendas ÷ estoque médio) e DSI por produto, no período escolhido, em **três faixas** com régua de dois pinos: encalhe, baixo giro e giro normal. Cada faixa tem um quadro com giro médio, DSI médio, quantidade e custo em estoque. A régua **simula na tela**; só "Salvar faixas" muda o parâmetro da empresa, que é o que Necessidades de Compra lê. Lê o **mesmo bloco de dados** da tela de compra, e a suíte compara o texto dos dois. Ver §14.52 |
| Movimentação de Estoque | `pagina-estoque-movimentacao.html` (menu Estoque) | **Construída em 13/out/2026.** O histórico individual de cada produto, **só para consulta**. Abre com os filtros (depósito, produto, tipo de movimento, data inicial, data final). O produto é a **busca padrão** do sistema (nome, código ou GTIN, com sugestões); produto e período são obrigatórios, e as datas abrem no mês atual (§14.65). Cinco indicadores, lidos do Controle de Estoques, e a lista em ordem de data com saldo anterior, quantidade, saldo atual, valor unitário, custo médio e valor em estoque. Clicar no movimento abre o **documento inteiro** num painel largo, com todos os itens; "Imprimir documento" manda só ele para o papel. **Não tem dado próprio de compra e venda:** deriva do bloco comum de compra e giro. Suíte: `teste_movimentacao.py`. Ver §14.63. |
| Inventário de Estoque | `pagina-estoque-inventario.html` (menu Estoque) | **Construída em 16/set/2026 — última tela de estoque da F5.** Abre num **índice de três caminhos**, não numa lista: *Gerar inventário* (monta pelos filtros), *Importar por planilha* (CSV/XLS/XLSX até 2 MB, exige **depósito de destino** porque o arquivo não diz onde a contagem aconteceu) e *Importar por coletor* (TXT até 2 MB, **um código por linha — a repetição É a quantidade**, sem coluna de total; valida por GTIN/EAN, SKU ou ambos). O que separa esta tela do Acerto está escrito no topo dela: **o inventário bloqueia o saldo do depósito inteiro** da abertura ao fechamento — venda, transferência e acerto ali são recusados —, e por isso é último recurso, não ferramenta de rotina. Notas **em conferência** continuam entrando e ficam **fora da contagem**, coerente com a regra de que em conferência não é estoque físico. A lista abre em **modo leitura** (Produto · SKU · Preço · UN · Localização · Estoque atual · Estoque disponível); **Informar quantidades** revela as colunas *Qtde inventário* e *Diferença* e troca o próprio botão por **Salvar quantidades e fechar**. Filtros de geração (Busca, Categoria, Fornecedor, Tags, Exibir, Situação do produto e **Valor baseado em**, agrupado em Preço de compra / de custo / de venda) valem **só na geração**: depois de aberta, a lista é fixa — mexer no filtro com inventário em andamento trocaria o universo contado. **Ausência de leitura nunca vira zero automático** (decisão de 16/set/2026): produto com saldo no depósito que não apareceu no arquivo entra como **não contado**, e não contado **não mexe no saldo** no fechamento. Quem varreu o depósito inteiro usa **"Zerar os não contados"** em Mais ações, com confirmação que explica a consequência — a alternativa (assumir zero sozinho) apagaria saldo bom por causa de um corredor que o coletor não percorreu. No fechamento, **diferença positiva segue a mesma regra de entrada do item 19** (base de picking no depósito → nasce disponível até a capacidade, excedente e sem-base → *a endereçar*, não vende) e **não gera documento fiscal**; **diferença negativa** sai do disponível, base primeiro, e nasce com **pendência fiscal de NF-e CFOP 5.927** sem travar. **Reservado e bloqueado não são tocados** — inventário conta prateleira, não desfaz reserva de pedido nem libera avaria. Fechar exige **usuário + senha** e é **permissão de perfil** (`Fechar inventário de estoque`, agora ativa na lista de confirmações de Vendedores). **Cancelar inventário** destrava o depósito sem alterar nada. Mais ações traz ainda **Exibir/Ocultar filtros**, **Imprimir lista** (`@media print` deixa só a tabela) e **Baixar CSV** — os dois de verdade, não mocados. |
| Configurações do Sistema ERP *(hub)* | `pagina-configuracoes.html` (menu Configurações) | **Construída em 18/set/2026 — abre o módulo de Configurações.** É um **hub**, não uma área com abas internas: índice com **busca** e **nove abas que filtram uma lista de links**; cada link abre **página própria**, com breadcrumb e voltar — o padrão que o sistema já usa. **As abas são os NOSSOS módulos** (geral · cadastros · estoque · vendas · logística · finanças · operacional · **fiscal** · integrações), não os do Olist, onde *separação* e *expedição* vivem em Vendas e aqui são Logística. *Fiscal* ganhou aba própria: certificado, ambiente, naturezas de operação, intermediadores e RTC não cabem como sub-item de Vendas. Cada aba abre com um **banner de contexto** que diz a regra que importa naquele domínio (ex.: em Estoque, que os limiares de tempo passam a morar ali; em Integrações, que o disponível enviado ao canal é o nosso, menor que o de outros ERPs). **O badge de estado é DERIVADO, nunca escrito à mão:** item com destino está construído e não leva selo; item sem destino leva **"a construir"**. A primeira versão tinha badges escritos manualmente (*configuração pendente*, *ambiente de testes*) em telas que sequer existiam — o índice prometia estado de coisa inexistente. Derivar do `href` torna impossível uma tela nascer mentindo que está pronta, e transforma o índice num **mapa de progresso** real. A **busca varre todas as abas de uma vez** (nome e texto de ajuda, ignorando acento) e mostra a **aba de origem** ao lado de cada achado. O ícone `?` aparece só nos itens que têm explicação, no `title`. **Onde cada coisa mora — a régua é a FREQUÊNCIA de uso** *(decidido em 18/set/2026, a partir de pergunta do usuário)*: a primeira versão do hub trazia atalhos para Marcas, Categorias, Departamentos, Seções, Embalagens, Depósitos, Endereços de Estoque, Metas e Vendedores — o **mesmo arquivo** do módulo, alcançado por dois caminhos, como o Olist faz. O usuário perguntou se era a mesma tela; **se quem aprovou o desenho teve a dúvida, quem opera vai ter também**, e os atalhos saíram. **O critério não é "é lista auxiliar", é com que frequência se mexe:** cadastrar marca nova acontece toda vez que chega produto de fornecedor novo — isso é **operação** e pertence ao módulo; *Tipos de contato*, *Variações*, *Atributos*, *Linhas de produtos* e *Parâmetros de estoque* se definem uma vez e quase nunca se revisitam — isso é **configuração** e pertence ao hub. A regra que o usuário aprende numa vez: **cadastro fica no módulo, parâmetro fica em Configurações**. O único ganho real que os atalhos tinham era guiar o **setup inicial** — e isso passou a ser resolvido pelo **Guia de primeiros passos** (abaixo), que é a solução do próprio Olist e não suja a navegação do dia a dia. **Duplicar tela continua proibido** em qualquer hipótese: duas telas para o mesmo cadastro divergem em semanas. |
| Parâmetros de estoque *(Configurações → estoque)* | `pagina-configuracoes-parametros-estoque.html` | **Construída em 18/set/2026 — primeira tela filha do hub.** É a tela que tira de dentro do código os **três limiares de tempo** que as telas de Estoque usavam cravados: *Conferência de compra* (alerta/crítico de dias de espera na doca), *Endereçamento* (alerta/crítico de dias parado em `a_endereçar`) e *Estoque zero na base de picking* (dias com a base zerada). **Layout GNRE** (§6): campo à esquerda, explicação à direita, na grade `.par-linha` — porque parâmetro que ninguém entende é parâmetro que ninguém mexe. **A prova de que a tela não é decoração:** junto com ela, os **7 números cravados** em `pagina-estoque-enderecamento.html` (5) e `pagina-estoque-conferencia-entrada.html` (2) foram substituídos por um bloco `PARAM` nomeado, logo depois de `<script>`, com comentário dizendo de onde o valor vem no sistema de produção (`tabela parametros`, por chave). Sem esse refactor a tela salvaria um número que nenhuma outra leria. **Regra nova: número que decide cor, alerta ou bloqueio nunca nasce literal dentro de um `if`** — nasce em `PARAM`, ainda que a tela de configuração venha depois. **Prévia viva:** cada seção mede o efeito do número na fila de hoje (*"Na fila de hoje (6 saldos): 3 ficariam em alerta e 1 ficaria em situação crítica"*) e recalcula a cada tecla — o usuário vê a consequência antes de salvar, em vez de descobrir amanhã. **Validação:** crítico tem de ser maior que alerta (salvar é bloqueado com modal explicando qual par está invertido), inteiro de 0 a 365, não-numérico recusado. **Barra fixa de salvar** com contador de alterações não salvas e **Restaurar padrão** (1 · 3 · 2 · 7 · 7). O breadcrumb do meio volta para o hub. |
| Interface do usuário *(Configurações → geral)* | `pagina-configuracoes-interface-usuario.html` | **Construída em 18/set/2026 — a primeira tela de preferência POR USUÁRIO.** A distinção que ela cria vale para todo o hub: *Parâmetros de estoque* é da **empresa** (o prazo da doca é o mesmo para todos); *Interface do usuário* é de **quem está logado** — no banco, `parametros` ganha `usuario_id` **anulável**: nulo = valor da empresa, preenchido = preferência daquele usuário. **Quatro preferências (a quarta desde 29/set/2026), e só as que alguma tela lê:** *Registros por página* (10/25/50/100 — **não** 20/50 como no Olist: o global tem de falar o mesmo vocabulário do dropdown do rodapé, senão o usuário escolhe um padrão que nenhuma tela consegue mostrar), *Ao abrir um cadastro existente* (visualização / edição — entrou quando o modo leitura passou a existir, §10.3), *Ao salvar um cadastro* (voltar para a listagem / continuar no cadastro) e *Aparência* (tema). **A regra da paginação (opção B) virou código:** o valor daqui é o **padrão de abertura** das 17 listagens; o dropdown do rodapé **sobrepõe enquanto durar a sessão e não grava** — testado no navegador: trocar para 25 no rodapé deixa o valor salvo intacto. **O tema aplica na hora, sem passar pelo Salvar** — é o mesmo controle do seletor do menu, e se esperasse confirmação aqui e não lá, o mesmo controle teria dois comportamentos. Os dois caminhos escrevem no mesmo valor e se refletem um no outro. **A prévia mede o que o usuário vai sentir, não um número abstrato:** *"com 50 por página a primeira página tem cerca de 6,3 telas de rolagem"* — medido no navegador a 1440×900 (Produtos 7 linhas visíveis, Clientes 8, Controle de Estoques 8, Categorias 9; média 8), não estimado. **O vermelho só aparece a partir de 50:** marcar o padrão de fábrica como alerta ensina o usuário a ignorar a cor. **Bloco "Ainda não estão nesta tela"**, com as duas preferências do Olist que ficaram de fora e o motivo: *abrir cadastro em edição ou visualização* (não existe modo somente-leitura para escolher) e *lembrar a última tela ao logar* (não existe login). **Parâmetro que ninguém lê é enfeite** — e dizer por que ele não está ali é mais honesto que mostrá-lo desligado. |
| Confirmações por senha *(Configurações → geral)* | `pagina-configuracoes-confirmacoes-senha.html` | **Construída em 18/set/2026.** Decide **quais ações exigem a senha de quem executa**. A tela não tem lista própria: ela edita o **catálogo compartilhado `ACOES_SENHA`**, que agora vive no bloco comum dos 40 arquivos e é lido por três lugares — esta tela, as quatro telas que pedem senha, e o checklist do perfil em Vendedores. **Uma lista, duas perguntas:** aqui se decide **se a ação pede senha**; em *Permissões de usuários* (hoje espelhado em Vendedores → Acesso e Permissões), **quem pode confirmar**. Eram duas listas digitadas à mão em lugares diferentes — a de Vendedores tinha os cinco itens copiados. Duas cópias divergem em semanas e uma ação acaba existindo numa tela e não na outra; agora Vendedores renderiza a partir do catálogo, e ação desligada aparece lá desabilitada com *"não exige senha hoje"*, porque não há o que permitir. **A prova de que não é decoração:** desligar *Finalizar acerto de estoque* e reabrir o Acerto faz o painel de confirmação abrir **sem o campo de senha** — e gravar direto. Testado nos dois sentidos. **O painel continua abrindo:** o resumo do lote (*"1 linha · 2 vão para a fila fiscal"*) é o motivo de ele existir; a senha é só a trava. **Some o campo, nunca a conferência.** **Ação de tela que ainda não existe não ganha interruptor — ganha cadeado.** A primeira versão mostrava um switch desabilitado: ele lia como "desligado" ao lado de um texto dizendo *"nasce exigindo senha"*. **Controle que não controla nada mente sobre o estado.** **A prévia nomeia o risco em vez de contar quantos:** *"1 de 4 passa a acontecer sem confirmação: finalizar acerto de estoque. Quem alcançar a tela executa direto, e o histórico não guarda quem autorizou"* — desligar aqui é sempre redução de segurança e isso tem de estar escrito, não subentendido. | **Ampliada no mesmo dia (18/set/2026) para incluir EXCLUSÃO, por decisão do usuário:** o catálogo passou de 5 para **19 ações** — as 14 exclusões reais do sistema (12 cadastros + Notas de Entrada + Ordens de Compra), **uma por módulo, não uma genérica**: o perfil precisa poder liberar excluir cliente e travar excluir produto, e uma ação única não permitiria isso. Todas **nascem exigindo senha** — desligar é um interruptor e fica registrado; ligar exige lembrar que a tela existe, e o padrão vence sempre. Com 19 itens a lista passou a ser **agrupada por módulo**, nas duas telas, com o grupo saindo do próprio catálogo (campo `modulo`). **O campo de senha foi para dentro do modal de confirmação que já existe** — não um segundo diálogo em cima do primeiro. O modal existe em 24 arquivos com **três assinaturas diferentes** (`texto,qtd,cb` · `texto,qtd,cor,cb` · `texto,qtd,cor,cb,modo`); mudar a assinatura nos 24 seria trocar 24 chamadas por um bug. A solução: quem vai excluir **arma** a senha numa linha antes (`armarSenhaModal('marcasExclui')`), um envelope sobre `abrirModalConfirmacao` mostra ou esconde o campo na abertura, e a trava roda **na fase de captura** do botão Confirmar — antes do handler de cada tela, cancelando a confirmação com `stopImmediatePropagation()` se a senha estiver vazia. **Nenhuma tela mudou de assinatura, e 24 pontos de exclusão foram ligados com uma linha cada.** Teste que importa: o modal de **Inativar**, aberto logo depois do de Excluir, **não herda** o campo de senha — o envelope limpa o estado a cada abertura. **Virou MATRIZ em 21/set/2026.** O catálogo passou a ser **módulo × verbo** (criar · editar · excluir) mais as ações específicas que verbo nenhum descreve — **47 células** hoje, contra 19 itens na lista chapada. `ACOES_SENHA` **não é mais escrita à mão: é derivada** de `MODULOS_SENHA × VERBOS_SENHA + ACOES_ESPECIFICAS`, então quem já lia o catálogo (as telas que pedem senha, o checklist do perfil) não precisou mudar uma linha. **A mesma grade renderiza nas duas telas** — em Configurações com interruptores (*a ação exige senha?*) e no perfil do Vendedor com caixas de seleção (*este perfil pode confirmar?*). Uma lista, duas perguntas. **O campo `ligado` é o que impede a matriz de mentir:** ele diz se a TELA daquele módulo já chama a verificação naquele verbo. Célula não ligada aparece com **cadeado e o motivo no `title`**, nunca como interruptor que não faz nada — é a mesma regra do badge derivado do hub, aplicada a uma grade. Hoje `excluir` está ligado nos 14 módulos; `criar` e `editar` só em **Marcas**, que é o piloto. **Marcas é a implementação de referência:** o `btnSalvarMarca` passou a chamar `confirmarAcao(chave, texto, executar)` — helper compartilhado que executa direto quando a trava está desligada e, quando ligada, abre o modal com o campo de senha e só grava dentro do callback. Ele despacha as **três assinaturas** de `abrirModalConfirmacao` lendo `.length` da função, em vez de adivinhar. Testado nos dois sentidos: desligado cria sem modal; ligado não cria sem senha e cria com senha. **A prévia aprendeu a diferença entre desligado e desprotegido:** o vermelho só aparece quando uma **proteção de fábrica foi retirada** (ação cujo padrão é exigir e que foi desligada ali). Criar e editar nascem desligados de propósito — pintá-los de alerta ensinaria o usuário a ignorar a cor, o mesmo erro já corrigido na prévia de Parâmetros de estoque.
| Registro de atividades *(Configurações → geral)* | `pagina-configuracoes-registro-atividades.html` | **Construída em 21/set/2026.** Quem fez o quê, quando e em qual registro. **Nenhuma das 41 telas precisou saber que ele existe:** a gravação mora nos dois lugares por onde toda ação do catálogo já passava — o `confirmarAcao` (quando não exige senha) e a fase de captura do botão Confirmar do modal compartilhado (quando exige). Uma ação nova passa a ser registrada só por entrar no catálogo. **Grava com senha e sem senha.** É o que muda o sentido do catálogo: ele deixa de ser *"a lista do que pede senha"* e vira **a lista do que é auditável**, com a senha virando uma **coluna** do registro. **A linha de detalhe é o texto exato que a pessoa confirmou**, não um resumo escrito depois — é o que um auditor quer saber: o que foi mostrado a quem clicou. **Nada é semeado.** Abrir pela primeira vez mostra o vazio de verdade, com instrução do que fazer para ver o registro funcionando. **Registro com evento de exemplo é registro que mente** — o mesmo princípio da prévia que media fila inventada. **Duas decisões ficaram escritas na própria tela:** não existe botão de apagar (registro que quem agiu consegue limpar é rascunho — expurgo por tempo é rotina de servidor, nunca botão), e no sistema real **quem grava é o servidor** (log gravado pelo cliente é log que o usuário apaga depois de agir). Listagem com busca sem acento, filtro por módulo e período, e o rodapé de paginação padrão (§7) — que **herda o padrão de abertura** de *Interface do usuário*, fechando o circuito das três telas de configuração. |
| Configurações da conferência *(Configurações → estoque)* | `pagina-configuracoes-conferencia.html` | **Construída em 21/set/2026.** Três parâmetros que respondem à mesma pergunta em níveis diferentes: **quanto da expectativa a pessoa vê antes de contar**. **Conferência cega** (padrão ligado) — o `let cego = true` que estava cravado em `pagina-estoque-conferencia.html` virou `PARAM.conferenciaCega`, e o interruptor da própria conferência continua permitindo a **exceção pontual**: mesma regra da paginação, o global manda na abertura e a tela manda naquela sessão. Provado no navegador: com o parâmetro ligado as quantidades da nota abrem como **OCULTA**; desligado, aparecem os números desde a abertura. **Ocultar itens** e **ocultar volumes na fila** (padrão desligado) — a conferência cega esconde o esperado *item a item dentro da nota*; estes dois escondem os *totais na fila da doca*, que é onde alguém lê "9 volumes" e já desce contando para dar nove. A célula some com `title` explicando por quê, em vez de sumir sem aviso. **Desligar a conferência cega virou ação do catálogo** (`conferenciaCegaDesliga`), **sem exigir senha mas gravando no Registro de atividades** — é o primeiro caso que prova na prática a regra de que o log grava com senha e sem. **Uma tela para dois escopos:** o hub tinha dois links (*conferência* e *conferência de compra*) e agora tem um — três parâmetros não justificam duas telas, e as seções (*Dentro da conferência* / *Na fila da doca*) dizem o escopo melhor que dois links diriam. **A tela também registra o que NÃO virou parâmetro, de propósito:** as cinco opções de *"lançamento para entradas"* do Olist (aqui é regra dura: estoque nasce ao finalizar a conferência) e *"permitir editar a quantidade lida na importação"* (aqui a importação abre em modo revisão). **Dizer por que uma opção não existe vale mais que oferecê-la desligada.** |
| Configurações do cadastro de produtos *(Configurações → cadastros)* | `pagina-configuracoes-cadastro-produtos.html` | **Construída em 21/set/2026.** Casas decimais da **quantidade** (0–4) e do **preço unitário** (0–10) — os dois números estavam cravados em **14 arquivos**. **A separação que importa:** `fmtNum` de cada tela formatava quantidade E dinheiro; se o parâmetro entrasse lá, mudar a casa da quantidade mudaria a moeda junto. Por isso nasceram **`fmtQtdNum` e `fmtPrecoNum`** no bloco compartilhado, e `fmtQtd` passou a chamar o primeiro. Provado no navegador: com 3 casas, `fmtQtd(12,5)` vira **12,500** e `fmtMoeda(1.234,5)` continua **R$ 1.234,50**. **A prévia mostra o mesmo número escrito das duas formas** — explicar casa decimal com texto não convence ninguém; ver *12,5 kg* virar **13** convence na hora, e é por isso que **zero casas** é o único valor que acende alerta. O caso real do preço com 4 casas está escrito na tela: embalagem comprada a **R$ 0,0125** a unidade vira R$ 0,01 com duas casas, e o custo do pedido inteiro sai errado. **Três parâmetros do Olist ficaram de fora com o motivo escrito:** custo de kits (entra com o cadastro de Kit, que é quem vai lê-lo — e ficou mais importante depois da decisão dos dois tipos de kit), cadastro automático a partir de compras e vendas (depende de Vendas) e somar peso (depende de Expedição). |
| Configurações do cadastro de clientes *(Configurações → cadastros)* | `pagina-configuracoes-cadastro-clientes.html` | **Construída em 21/set/2026.** Dois parâmetros — e um deles **veio com a regra que ele configura**. **Permitir CPF/CNPJ repetido** nasce **desligado**, e a checagem de duplicidade **não existia**: até hoje o sistema aceitava o mesmo documento em dois cadastros sem dizer nada. Construí as duas coisas juntas, que é a regra da casa — parâmetro e leitor no mesmo passo. A mensagem de bloqueio **diz em qual cadastro o documento já está** (*"já está em Marina Duarte"*): erro que não aponta o caminho vira chamado de suporte. O cadastro aberto sai da comparação, senão acusaria a si mesmo. **Mostrar observações do cliente** (padrão ligado) controla a **aba inteira**, que some em vez de ficar vazia — aba morta é pior que aba ausente, e o texto já escrito não é apagado. **Três do Olist ficaram fora:** *restringir o vendedor aos clientes dele* é **permissão por registro** (row-level) — não cabe na matriz módulo × verbo, é um refinamento dela e entra com Permissões de usuários; *vincular automaticamente ao vendedor* e *cadastrar cliente a partir de pedido ou nota* dependem de Vendas. |
| Contas financeiras *(Configurações → finanças)* | `pagina-configuracoes-contas-financeiras.html` | **Construída em 21/set/2026, a partir dos prints** — é o cadastro que abre Finanças. **Conta financeira é o guarda-chuva e é ela que carrega o saldo**; a conta bancária é uma *extensão* dela, com banco e agência. Por isso o cadastro é enxuto e não pede dado bancário nenhum. **Primeiro módulo nascido depois da matriz** — entrou no catálogo com os **três verbos ligados desde o primeiro dia**, e por isso já nasce auditado: criar e excluir aparecem no Registro de atividades sem uma linha de código de log na tela. É a regra *"a trava nasce com a tela"* no caso fácil. **O valor da tela são as quatro travas de integridade**, e todas dizem o motivo *antes* do clique, no painel: **Caixa não se exclui nem se inativa** (nasce com a empresa — é o cadeado do print); **conta com saldo não se inativa nem se exclui** (*dinheiro não some junto com o cadastro*); **conta com bancária vinculada não se exclui** (deixaria a bancária órfã); e **a preferencial não sai de circulação** sem outra ser eleita. O mock tem **uma conta que passa nas quatro** (*Conta teste*, zerada e sem vínculo) — sem ela o caminho de exclusão nunca seria testado, e **trava que nunca deixa passar também é bug**. **O KPI do topo existe para dar sentido ao interruptor** *fora do fluxo de caixa*: sem ele, o flag seria uma caixinha que não muda nada na tela. Ligar um e o saldo considerado cai na hora. **Duas escolhas em que saímos do Olist, de propósito:** lá o formulário é **página própria** e o número contábil é um **drawer separado** acionado por menu `···` na linha — aqui é **um drawer só**, com a contabilidade como seção, porque dois campos não justificam duas telas e o menu `···` por linha seria um componente novo no sistema inteiro (o mesmo motivo que barrou a edição inline). |
| Contas bancárias *(Configurações → finanças)* | `pagina-configuracoes-contas-bancarias.html` | **Construída em 21/set/2026, com a documentação do Olist consultada antes** — e foi ela que mudou o desenho: o print mostrava só *Banco* e *Descrição da conta*, mas a doc acrescenta **chave Pix com tipo** (e-mail · CPF · CNPJ · telefone · aleatória) e diz para que a conta serve no dia a dia — *"emitir boletos"* e *"enviar remessas e ler retornos dos principais bancos"* (CNAB). **Sem consultar, a tela teria nascido com dois campos e sem Pix.** **A conta bancária não tem saldo** — é a ficha de dados de uma **conta financeira**, que é quem guarda o saldo. Isso está dito no topo da tela e repetido na nota do painel, porque é a confusão mais provável de quem chega. **O vínculo é 1:1 e a tela impede o erro antes dele acontecer:** o seletor de conta financeira mostra **apenas as que ainda não têm bancária**. Duas bancárias na mesma financeira fariam o saldo perder o dono — e oferecer uma já vinculada seria oferecer um erro que o usuário só descobriria ao salvar. Campos: conta financeira · banco (código + nome) · descrição · agência · conta com dígito · tipo (corrente/poupança/pagamento) · tipo e valor da chave Pix. **Tipo de chave escolhido obriga a chave** — chave pela metade é pior que chave nenhuma. Segundo módulo nascido depois da matriz: **três verbos ligados e auditado desde o primeiro dia**. |
| Categorias financeiras *(Configurações → finanças)* | `pagina-configuracoes-categorias-financeiras.html` | **Construída em 21/set/2026, com a doc do Olist consultada antes** (`configuracoes-financeiras/categorias-de-receitas-e-despesas`). **A conta diz onde o dinheiro está; a categoria diz o que foi** — e ela carrega as duas regras que poupam trabalho em cada lançamento: a **posição no DRE** e a **competência padrão** (*mês do vencimento · mês anterior ao vencimento · mês da emissão*), que é o que resolve o `data ≠ competência` sem perguntar nada a quem lança. **Uma tela, duas visões** (`categorias ↔ grupos`, o mesmo par do print): grupo tem **um campo só**, e tela inteira para ele seria mais um arquivo para manter, mais um item no hub e nada a mais na frente do usuário. **Componente novo `.visao-tabs`** — duas abas em pill, a ativa em `--brand-blue` — reutilizável em qualquer tela com duas listas irmãs. **O hint muda com o valor escolhido:** cada opção de *Considera no DRE* tem regra de sinal própria (deduções, operacionais, tributos e taxas só consideram **saídas**; *outras receitas ou despesas* considera os dois sentidos), e sem o hint a escolha vira chute que só aparece errado no relatório. **A barra de seleção diz a verdade antes do clique:** com 3 marcadas e 2 em uso, ela mostra *"2 em lançamentos, fora da exclusão"* e o link vira *"Excluir selecionadas (1)"* — link que parece funcionar e não funciona é a mesma mentira do interruptor que não controla nada. **Trava de exclusão por uso (divergência deliberada do Olist, que não tem situação):** categoria citada em lançamento **não mostra o link de excluir**, e a nota diz quantos lançamentos são e oferece *Inativar*; com uso zero exclui de verdade — e o mock tem uma categoria zerada de propósito. **Excluir um grupo não apaga categoria nenhuma:** elas voltam para *Sem grupo*, e a confirmação diz quantas. **Padrão de vendas / padrão de compras são exclusivos na hora** (marcar um desmarca o outro), mesma regra da conta preferencial. Terceiro módulo nascido depois da matriz: três verbos ligados e auditado desde o primeiro dia — inclusive a **movimentação em massa**, que não pede senha e mesmo assim entra no Registro de atividades. |
| Caixa e Bancos *(Finanças)* | `pagina-financas-caixa.html` | **Construída em 22/set/2026.** **É extrato de uma conta, não lista de lançamentos** — e essa frase decidiu metade do desenho: **ordem crescente por data** (extrato se lê do saldo antigo para o atual), **primeira linha = saldo anterior ao período** (só na página 1; na página 2 ela mentiria), e **rodapé com cinco totais** (saldo inicial · entradas · saídas · saldo final · nº de lançamentos), com saldo negativo em vermelho. **`N selecionados` entra no rodapé quando há seleção** — detalhe barato do print que responde *"quanto dá o que marquei?"* sem exportar nada. **Com filtro ativo o rodapé avisa que os totais são do que está filtrado** — sem essa linha o número mente com cara de verdade. **Entrada e saída são duas colunas**, não um valor com sinal. **Divergência medida, não achada:** a coluna *Cliente* do print virou a **segunda linha da célula de Histórico**, porque com ela separada a tabela passava dos ~1040px úteis e a rolagem esconderia Entradas e Saídas (mediu-se 986px em 986px). **Componentes novos:** `.cx-totais` (barra de totais à direita), `.cx-conta-bar` (seletor de conta + saldo), `.cx-saldo-row` (linha de abertura dentro da tabela) e `.dropdown-grupo` (cabeçalho de grupo dentro do menu do dropdown). **A transferência é a única ação do sistema que cria dois registros** — saída na origem e entrada no destino, ligadas por `parId`, com a explicação no painel. **Fechamento financeiro** é uma data em `PARAM.fechamentoFinanceiro` (fora do `PARAM_PADRAO`, como `confirmacoes`), aparece no rodapé como estado, exige senha por padrão, tem **reabrir** (trava sem saída é armadilha) e **pega em três lugares testados**: lançamento manual, transferência e exclusão em massa. **A fila de movimentações bloqueadas nasce vazia e explica quem vai enchê-la** — e diz que lançamento manual nunca cai ali, porque é barrado na hora. |
| Lançamento no caixa *(Finanças → Caixa)* | `pagina-financas-caixa-lancamento.html` | **Construída em 22/set/2026.** Página própria com quatro abas (*dados do lançamento · competência · anexos · marcadores*) e **dois modos: leitura e edição**, como o print — o modo leitura troca campo por rótulo e valor com **um seletor só** (`body.modo-leitura`), sem duplicar marcação no HTML. **Caixa de erro no topo + campo marcado** (`.erro-topo`), padrão adotado do Olist: erro só no campo faz procurar, erro só no topo não diz onde. **`Tipo = Saldo` lança a DIFERENÇA** — a tela mostra antes de salvar qual entrada ou saída vai nascer, e diz *"não há o que lançar"* quando o saldo informado é igual ao atual, em vez de gravar zero. **A competência vem da regra da categoria** (o dividendo da tela de Categorias financeiras): mudar a categoria recalcula, mexer nas setas desliga a regra para aquele lançamento, e a nota admite que **no Caixa existe uma data só**, então *mês do vencimento* e *mês da emissão* dão o mesmo mês — a diferença aparece em Contas a Pagar e a Receber. **+ Adicionar nova categoria mora dentro do menu de Categoria** e abre o mesmo drawer de Configurações: quem lança não vai a Configurações no meio do trabalho, e a categoria criada vale no sistema inteiro. **Componentes novos:** `.tabs-row`/`.tab-item`/`.tab-panel` trazidos para o padrão de Finanças, `.campo-leitura`, `.comp-nav`, `.chip-marcador`, `.anexo-item` e `.auto-menu` (busca de pessoa). **Ficou de fora de propósito:** menu `⋯` por registro (componente novo no sistema inteiro), cadastro rápido de pessoa (formulário duplicado diverge) e imprimir/exportar (botão morto é bug). |
| Início | `pagina-dashboard-kpis.html`, `pagina-inicio-boas-vindas.html`, `pagina-inicio-agenda.html`, `pagina-inicio-minha-conta.html` | Construído antes do padrão de seleção em massa existir — não têm listagem com exclusão |
| Contas a pagar | `pagina-financas-contas-pagar.html` (menu Finanças) | **Construída em 23/set/2026.** Listagem com **situação derivada** (nunca gravada): vence hoje, vencida, paga, parcial, cancelada saem da data e do valor baixado. Linha expande no lugar, sem sair da tela. Baixa total e **baixa parcial**, período financeiro fechado bloqueando, cancelar e reativar |
| Conta a pagar — página | `pagina-financas-contas-pagar-detalhe.html` (menu Finanças) | **Construída em 23/set/2026.** As **duas famílias de repetição** — parcelamento (um valor dividido) e recorrência (o mesmo valor repetido) — com prévia antes de gravar e escopo (só esta / esta e as próximas / todas) ao editar em grupo. Clonar copia a despesa e **não** a data. Recibo travado sem baixa, valor por extenso |
| Lojas Desk — detalhe | `pagina-cadastros-lojas-desk-detalhe.html` | Duas abas (Dados Gerais, Histórico de Metas). Só **lê** metas — o único ponto de escrita é `pagina-vendas-metas.html` |
| Pedidos de Venda | `pagina-vendas-pedidos.html` (menu Vendas) | **Construída em 30/set/2026; abas trocadas por filtro em 02/out.** **Situação é um filtro suspenso**, ao lado de Loja e Vendedor, com os **contadores dentro da lista** — eles acompanham os outros filtros. Eram abas contadoras numa linha, mas **9 situações + Todas não cabem a 1440px** (1.395px num espaço de 1.024). Período filtra por **data da venda** ou **data de faturamento**, em abas dentro do popover. Rodapé soma **excluindo cancelados**, e diz que exclui. Linha de pedido reservado mostra *estoque reservado*. Excluir pede senha e avisa que a reserva volta; **pedido expedido não se exclui** — o caminho é devolução |
| Pedido de Venda — página | `pagina-vendas-pedidos-detalhe.html` (menu Vendas) | **Construída em 30/set/2026, com o funil e os painéis do cliente em 02/out.** **O pedido anda pelo botão de próximo passo** no cabeçalho, um passo por vez, com o rótulo dizendo o efeito (*Faturar* avisa que libera a comissão; *Confirmar envio* avisa que é a baixa física). *Alterar situação* é a correção livre, com senha. **Clonar venda** abre um pedido novo já preenchido. Dois painéis laterais de consulta: **últimas vendas do cliente** (abas Produtos/Financeiro, 10 últimas) e **limite de crédito** (limite, usado, disponível real e o que compõe o usado). **Bloqueia o salvamento por limite** quando a forma de recebimento valida limite. Abas Itens / Comissões / Impostos. **Pedido não nasce sem saldo**, e a mensagem diz de qual depósito e quanto existe. Salvar **reserva o estoque e faz nascer a conta a receber**. Dois níveis de desconto, cada um na sua base: o do item forma o preço unitário, o do pedido incide sobre o total. A **loja escolhe o depósito** (alterável na mão) e o pedido é de uma loja só. Cadastro rápido de cliente no próprio pedido, nascendo com **cadastro incompleto** (§11.2). Campos fiscais visíveis e desabilitados (§11) |

| Contas a receber | `pagina-financas-contas-receber.html` (menu Finanças) | **Construída em 02/out/2026 — fecha a F5.** A conta **nasce do pedido de venda**, e a coluna *Origem* é link para ele. **Quatro valores por linha** (§12.4): Valor, **Líquido**, Saldo e Recebido — e eles não são o mesmo número. Receber em massa, período por vencimento ou competência, situação derivada (atrasada nunca é gravada). A **taxa retida quita o título sem entrar no Caixa** |
| Conta a receber — página | `pagina-financas-contas-receber-detalhe.html` (menu Finanças) | **Construída em 02/out/2026.** Taxas, valor líquido **gravado** (não calculado) e antecipado, além do que o a pagar já tinha. **Baixa é entrada no Caixa; estorno é saída** — o inverso do a pagar, e por isso sob teste. **Recibo e duplicata têm travas inversas**: sem baixa não há recibo, sem saldo não há o que cobrar |
## 12.1 Decisão: marcadores NÃO existem neste sistema (22/set/2026)

O Olist tem marcador em quase tudo — e em cada módulo com cadastro próprio (financeiros, na separação, padrão do PDV, na integração). **Nós descartamos o mecanismo inteiro.** O raciocínio completo está no roadmap; o resumo que importa para quem desenha tela:

- **Não existe aba, coluna, filtro, cadastro nem ação em massa de marcador.** Se um print mostrar, é para ignorar de propósito — está escrito no comentário de cabeçalho da tela de lançamento do caixa, exatamente para evitar reintrodução por imitação.
- **O que parece pedir marcador quase sempre pede outra coisa:** exceção operacional (frágil, prioritário) é **campo**, porque fila se ordena por campo e não por etiqueta livre; origem e canal já têm campo; "conferir depois" é agenda.
- **A saída provisória para agrupar evento transversal** (uma campanha, uma obra) é escrever `#algumacoisa` no histórico — a busca das listagens ignora acento e varre esse texto. Custa zero e serve de termômetro.
- **Gatilho para reabrir a discussão:** a terceira necessidade real de agrupar algo que categoria não agrupa. Aí entra com **uma tabela só, com `escopo`** — nunca uma por módulo.
- **Print com marcador se ignora, sempre (30/set/2026).** O usuário fechou o assunto: *"todo o ecossistema do Olist tem, então será inevitável print com marcadores; o que vamos fazer é ignorar essa parte."* Não é exceção por tela, é regra de leitura — marcador em print de Pedido de Venda, de Nota Fiscal ou de qualquer módulo futuro passa direto, sem levantar a discussão de novo. **A exceção é o badge que o sistema calcula sozinho** (o `1ª venda` do print nasce do dado, não de alguém digitando): isso é badge derivado, mesma família do *atrasada* em Contas a Pagar, e não tem cadastro nenhum por trás.
- **Vale também para tags de produto (decisão do usuário, 29/set/2026).** Tag é o mesmo mecanismo com outro nome. O hub de Configurações deixou de listar *Tags de produtos* e as quatro telas *Marcadores…* (ordens de compra, vendas, separação, financeiros) — índice que promete tela descartada mente do mesmo jeito que selo escrito à mão.

## 12.2 Classes-gancho (exceção consciente da seção 3 da auditoria)

> ✅ **Resolvido em 28/set/2026:** as seis viraram `data-*` (`data-check="mov"`, etc.) e **não existem mais em tela nenhuma** — a auditoria oficial não acusa nada na seção 3. A tabela abaixo fica como histórico, e a regra continua valendo: gancho de JS é `data-*`, classe é estilo.

A seção 3 da auditoria acusa classe usada no HTML sem CSS — a rede que pega **componente copiado pela metade**. Seis classes aparecem lá de propósito, porque existem **só para o JS achar o elemento** e o visual vem de outra classe:

| gancho | quem pinta |
|---|---|
| `tit-check` · `mov-check` · `cat-check` · `escopo-check` | `.item-checkbox` |
| `pg-estornar` | `.link-perigo` |
| `tit-linha` | `.estoque-table tbody tr` |

**Não inventar CSS vazio para calar o aviso** — regra que não pinta nada é pior que o aviso. Ao ler a auditoria, conferir se a classe acusada está nesta tabela; se não estiver, é componente copiado sem o CSS, e aí é bug de verdade. Foi exatamente assim que apareceu o `textarea` sem estilo no painel de Pagamento (§14.2).

## 12.3 Conferência — uma entrada de menu, duas telas (29/set/2026)

O menu tinha **dois itens para um módulo**, e o segundo apontava para uma tela de detalhe — único lugar do sistema onde isso acontecia. Clicar em *Conferência* largava o usuário na **nota 9051**, que ninguém escolheu.

As duas telas se justificam, e os breadcrumbs já diziam a verdade antes da correção:

| tela | o que é | breadcrumb |
|---|---|---|
| `pagina-estoque-conferencia-entrada.html` | a **fila** do galpão — 14 notas, 5 abas de situação | Estoque › Conferência de Entrada |
| `pagina-estoque-conferencia.html` | a **contagem de UMA nota** | Estoque › Conferência de Entrada › Nota N |

É **listagem + detalhe**, igual a Controle de Estoques e Ordens de Compra. O que estava errado era o caminho até elas.

**A causa estava escrita no código.** A fila, ao mandar conferir, mostrava: *"a navegação entre telas só passa a funcionar de verdade no sistema de produção"* — texto que ficou obsoleto em **22/set**, quando o cross-link do menu passou a navegar nas 53 telas. O segundo item de menu nasceu como contorno de uma limitação que já não existia. **Mensagem de limitação tem prazo de validade: quando a limitação cai, ela vira mentira que gera desvio.**

**O que ficou:**

- **Um item de menu**, *Conferência de Entrada*, apontando para a fila — removido das 53 telas o item que apontava para a contagem.
- **A fila navega**: `pagina-estoque-conferencia.html?nota=<numero>`.
- A contagem **lê a nota da URL**. Estão montadas as **4 notas que a fila oferece para conferir** (situação *pronto* ou *em conferência*); as demais estão aguardando chegada ou já conferidas, e conferir uma delas não é caminho que existe.
- **Nomenclatura alinhada**: H1, item de menu e breadcrumb dizem *Conferência de Entrada* na fila; a contagem é *Conferência da nota N*.

**A regra que fica: item de menu aponta para listagem, nunca para detalhe.** Detalhe se alcança pela listagem.

### O mock da nota 9051 não fechava

Achado ao montar as outras três notas: os itens da 9051 somavam **R$ 28.451,90** contra uma nota de **R$ 24.890,00** — e o valor da nota bate com a fila e com a OC 3, então o errado era a lista de itens. **A tela compara conferido × nota**: um mock que não fecha faz essa comparação mentir desde a primeira contagem, e o conferente veria uma divergência que não existe. Quantidades e um preço ajustados; as quatro notas agora fecham exato.

**Mock de tela que compara dois números tem de fechar.** É primo da lição da prévia que media outra fila (§14).

## 13. Pendências conhecidas (não são bugs — decisões conscientemente adiadas)

- **Categorias fica com a lista de checkboxes inline — decidido em 29/set/2026, com as duas telas lado a lado.** A migração para o dropdown multi-seleção de Marcas (§9.1) foi montada e comparada por imagem: o dropdown economiza ~110px num painel de três campos, e cobra por isso o **recolhimento automático** — para marcar duas lojas o usuário abre, marca, o menu fecha, abre de novo e marca a outra. Em Marcas o ganho pagava, porque o formulário é grande; em Categorias não. **A régua que fica: o dropdown multi-seleção é para quando o espaço é escasso, e a lista inline para quando não é.**

- **O mock envelhece, e a lista abre no mês corrente (achado em 28/set/2026).** As datas dos títulos são fixas no arquivo; a listagem de Contas a Pagar abre no **mês corrente** (barganha de 23/set). Passadas algumas semanas, todo título "em aberto" daquele mês vira **atrasado** sozinho, e a demonstração passa a mostrar um sistema só com contas vencidas. Foi isso que quebrou um passo do `teste_cp.py` quatro dias depois de ele passar — **o teste não mudou, o calendário mudou**. O teste já foi desamarrado da data; o mock não. A saída, quando incomodar, é gerar as datas relativas a hoje (`hoje + 5`, `hoje - 3`) em vez de escrevê-las fixas — vale para qualquer tela nova com data no mock.

- **Kit virtual quebra Inventário e Acerto — correção obrigatória quando o kit for construído (decidido em 21/set/2026).** O kit passa a ter duas formas: **montado** (saldo próprio, se comporta como produto) e **virtual** (sem saldo; disponível derivado de `min(piso(saldo_componente ÷ qtd))`). Hoje as duas telas tratam kit como produto comum — correto para o montado, **bug garantido para o virtual**, porque contar um kit virtual conta o mesmo saldo duas vezes. A correção entra junto com o cadastro de Kit, nunca depois.

- **`pagina-molde-referencia.html` — divisão adiada para o fim do projeto (decidido em 29/set/2026), por ser a última coisa que falta e haver muito a construir antes.** O molde é **dois documentos HTML completos no mesmo arquivo** (exceção já conhecida da auditoria): inserir o bloco nas duas metades criaria `const PARAM` duplicado no mesmo parse, e inserir em uma só deixaria o arquivo mentindo pela metade. Ele segue como referência **visual** congelada — tela nova nasce copiada de uma tela recente, não do molde. Se o molde voltar a ser ponto de partida, ele precisa ser dividido em dois arquivos antes.

- **Guia de primeiros passos — espera a tela de Usuários (confirmado em 29/set/2026).** Dá para construir o interruptor em Configurações e o desligar-sozinho, mas o terceiro ponto (a caixa no cadastro de usuário) depende de *Usuários do sistema*, que não existe — e um interruptor que liga um guia que ninguém recebe é controle que não controla nada. Os três pontos nascem juntos. Desenho fechado em 18/set/2026: É a faixa de progresso que o Olist mostra no topo de todas as telas (*"Etapa atual · Configure a emissão da nota fiscal · 2 de 4 ▓▓░░ · acessar o guia"*), levando o usuário novo pela configuração na ordem certa. **Nasce DESLIGADO**, por decisão do usuário: a Desk não vai usá-lo agora, sobretudo a parte de NF-e, e um guia que aponta para telas inexistentes é pior que guia nenhum. O ciclo de vida acordado tem três pontos: (1) item próprio em **Configurações → geral → Guia de primeiros passos**, onde se liga e desliga a qualquer momento; (2) **caixa de seleção no cadastro de usuário**, antes de finalizar — *"ativar o guia de primeiros passos"* —, para que cada usuário novo comece com ou sem ele; (3) quem recebeu o guia pode desligá-lo sozinho pelas Configurações. A caixa (2) é **requisito da tela *Usuários do sistema***, ainda a construir. O item já aparece no hub como `a construir`.

- **Devolução de compra ao fornecedor fica bloqueada** enquanto a Desk não emitir NF-e: a devolução exige NF-e **nossa** referenciando a original, então a mercadoria avariada entra, vai para endereço de Avaria e fica com saldo `bloqueado` — a saída dela é barrada com mensagem explícita, mesmo padrão da transferência entre CNPJs. O caminho que funciona hoje é **recusa na doca**, onde o fornecedor emite a NF-e de entrada. **Atualizado em 15/set/2026:** o saldo `bloqueado` deixou de ser beco sem saída — a **baixa por perda do Acerto de Estoque** é a saída dele, registrada com pendência fiscal (NF-e CFOP 5.927 devida) em vez de bloqueada. Ver roadmap §3 item 23 e o bloco "Acerto de Estoque".
- **Recusa parcial (recebo parte, recuso parte no ato) precisa de confirmação do contador**: o evento de Manifestação do Destinatário é por nota inteira, não existe "recusei parte". É o único ponto do procedimento de divergência que a pesquisa na legislação não fechou — as respostas a consulta tratam de recusa total. Ver roadmap §3 item 23.
- **Lista de preço fica de fora — decidido em 30/set/2026, com o campo órfão removido junto.** O cadastro já estava mapeado desde 16/set (roadmap §13, aba *cadastros*): descrição, acréscimo/desconto em %, e a tabela de produtos com preço próprio. O que não existe é o **caso de uso**: produto pertence a uma loja só, então preço por frente já sai do próprio produto; **preço promocional já existe por produto** (`inputPrecoPromocional`), que é o que mais se quer de uma lista; e não há operação de atacado no projeto. O markup de marketplace, que parece pedir lista, é outro problema e já tem solução — `valor_taxas`/`valor_liquido` do §12.4 do roadmap. **Gatilho para entrar:** a primeira venda com preço diferente por cliente ou por canal. `customers.lista_preco_id` é aditivo. **E o campo saiu do cadastro de Clientes** (`inputListaPreco`, com Padrão/Atacado/Varejo escritos na mão e nenhuma tela lendo): campo que aponta para cadastro que ninguém decidiu construir é promessa falsa, a mesma da lição do badge escrito à mão (§14). Na mesma passagem, o id `inputListaPreco` que tinha sobrado num campo de **Prazo médio de entrega** em Fornecedores foi renomeado para `inputPrazoEntrega` — id que mente sobre o campo é bomba armada para o primeiro `getElementById` que acreditar nele.
- **Variações de produto: grade dentro do produto — decidido em 29/set/2026 pelo usuário.** O Olist tem também um cadastro global de variações, reaproveitável entre produtos. **Entra só quando houver saldo por variação ou integração com marketplace** — acrescentar a biblioteca depois é aditivo: a grade passa a escolher dela, nenhum produto muda. Até lá, *Variações dos produtos* e *Atributos dos produtos* ficam no hub como telas a construir.
- **Editor de texto rico** (negrito/itálico/cor) nas descrições de Produto: virou textarea simples por complexidade. Reavaliar se for pedido de volta.
- **Composição de Kit** (selecionar quais produtos entram, quantidade de cada): Tipo do Produto já aceita "Kit", mas a tela de montagem em si ainda não foi desenhada.
- **Módulos ainda não construídos**, hoje representados como mock em Produtos: Transportadora (Desk Flash). (Marcas, Embalagens e Vendedores saíram dessa lista — já construídos, ver §12.)
- **Transportador é campo de texto livre** em Ordens de Compra e Nota de Entrada, por decisão do usuário (set/2026) — aponta para o cadastro de **Transportadora**, que é a última pendência de F2 e ficou por último de propósito. Trocar por vínculo real quando esse cadastro existir.
- **Painel de filtros avançados do Controle de Estoques — parado por falta de necessidade, não de decisão (29/set/2026).** Dos quatro filtros do Olist, **tags morreram junto com os marcadores** (§12.1) e **variações** só faz sentido quando o saldo for por variação, que não é o caso. Sobram categoria e fornecedor — úteis, mas ninguém sentiu falta ainda. Entra como drawer (§10) no dia em que alguém precisar filtrar por fornecedor. Descrição original: (Categoria, Fornecedor, Tags, Variações) — existe no Olist como popover atrás do botão "filtros" e ainda não foi construído. A toolbar atual cobre busca refinada, depósito, situação do saldo e tipo de produto, que é o filtro do dia a dia. Quando entrar, vira **drawer** (§10), não popover.
- **Regra de integridade referencial** (ex: impedir excluir uma Categoria/Marca/Embalagem que já está em uso por produtos) — ainda não implementada, só faz sentido quando o schema estiver no Supabase de verdade.
- **Permissão real de edição de período fechado em Metas**: hoje é só um modal de aviso (sem login/sessão de verdade). Trocar por checagem de permissão real quando Configurações → Permissões de Usuários existir.
- **Módulos que podem ser acessados (Vendedores) e demais checkboxes de permissão são mocados**: viram permissão de verdade só quando Configurações → Permissões de Usuários existir de verdade (mesma ressalva do painel de senha, §11).

**Nota de layout (15/set/2026):** na v2 o cabeçalho da coluna de código mostra **"SKU"**, não "Código (SKU)". As três colunas de estágio ganharam seta de ordenação e a tabela passou a estourar o card em **4px** a 1440px. Descartadas as saídas que apertavam `.estoque-table` (componente compartilhado com as outras telas de Estoque) e as que mexiam na nomenclatura travada dos prints; encurtar esse cabeçalho é a única que não custa nada — o dado embaixo é um SKU e o nome completo ficou no `title`.

## 14. Bugs corrigidos (histórico de lições resolvidas)

- **Cabeçalho de grupo dentro de `.estoque-table` nasce alinhado à direita (Categorias financeiras, 21/set/2026).** A regra geral da tabela é `td { text-align:right }` (é tabela de números), e o `td` de `colspan` do cabeçalho de grupo herdou isso — o nome do grupo aparecia colado na borda direita, longe das descrições que ele agrupa. **Pego no print de QA, não na auditoria**, porque nada estourava. **Lição: linha que não é linha de dado (cabeçalho de grupo, subtotal, separador) precisa desfazer explicitamente o alinhamento da tabela.**
- **Tag literal dentro de comentário reprova a auditoria (recorrência, 21/set/2026).** O comentário `substitui <select> nativo` faz o contador de tags acusar `<select>` nativo na tela — o mesmo defeito do `<body>` em comentário que reprovou 40 arquivos. O contador lê o **texto do arquivo**, não o HTML. Corrigido na tela nova (*"substitui o select nativo"*); **os 48 arquivos antigos ainda carregam o comentário original** — é ruído conhecido da auditoria, não bug de tela, e será limpo numa passagem única.
- **Função compartilhada cortada junto com o bloco da tela (Caixa → Lançamento, 22/set/2026).** Ao clonar o extrato para gerar a tela de lançamento, o corte começou no marcador `// ===== EXTRATO =====` e **levou junto `saldoAte`**, que é utilitário de dado, não parte do extrato. A tela nova quebrou em `ReferenceError` no primeiro uso do tipo *Saldo* — e **a auditoria passou**, porque a sintaxe estava correta; quem pegou foi o teste no navegador. **Correção aplicada nos dois arquivos**, movendo a função para junto dos demais utilitários, para que o próximo clone já a leve. **Terceira ocorrência da mesma lição: ao clonar, o corte é por RESPONSABILIDADE, não por marcador de seção** — e função que outra tela vai querer mora com os utilitários, nunca dentro da seção de uma tela.
- **Teste que clica num campo escondido por aba (22/set/2026).** O roteiro trocava para a aba *competência* e depois tentava clicar no dropdown de Categoria, que vive na aba *dados* — trinta segundos de timeout até falhar. **Não era bug da tela: era o teste mentindo sobre o estado.** **Lição: em tela com abas, todo passo do teste declara em qual aba está antes de clicar** — do mesmo jeito que se assere o `display` computado em vez de confiar em `is_visible`.
- **Botão que só ganha ação depois de outro clique é botão morto (21/set/2026).** Os dois dropdowns do painel de Contas bancárias eram montados dentro de `abrirDrawerConta` — antes de o drawer abrir, existiam na tela sem listener. A auditoria os marcou como *botões sem ação*, **com razão**: para quem audita (e para leitor de tela) eles são controles inertes. Corrigido montando os menus também na abertura da página. **Lição: componente que existe no DOM desde o carregamento se inicializa no carregamento**, mesmo que só vá ser visto depois.

- **Copiar uma tela como base trouxe junto o código da tela antiga (21/set/2026).** Ao gerar Contas financeiras a partir de Marcas, substituí o bloco de script inteiro entre dois marcadores — e levei embora o **componente de dropdown** e o **modal de confirmação**, que são genéricos. Ao devolvê-los, trouxe junto os **handlers específicos de Marcas** (`filtroLoja`, `linkExcluirMarca`, seleção em massa), que referenciam elementos inexistentes: `inicializarDropdownSelect is not defined`, depois `Cannot read properties of null`. **Lição: ao clonar uma tela, o corte é por RESPONSABILIDADE, não por marcador** — bloco genérico fica, bloco de domínio sai, e a fronteira entre os dois quase nunca coincide com o comentário de seção. Três rodadas de auditoria até limpar.

- **`.main` envolve o drawer e o modal — e eu fechei antes (21/set/2026).** Nas listagens de cadastro, `<div class="main">` só fecha **no fim do body**, depois do painel lateral e do modal. Meu conteúdo novo fechou a `.main` antes do drawer, e sobrou um `</div>`: **166/167** no balanceamento. Corrigido, e fica a nota estrutural — em tela de listagem, **o drawer mora DENTRO da `.main`**.

- **Assinatura do modal difere entre telas, e a chamada precisa combinar com a do arquivo.** Contas financeiras herdou de Marcas a variante de **3 argumentos** (`texto, qtd, callback`), mas eu escrevi as chamadas na variante de 4 (`texto, qtd, cor, callback`) — o `'danger'` entraria como callback e nada aconteceria ao confirmar. O helper `confirmarAcao` já resolve isso sozinho lendo `.length`; **chamada direta ao modal, não** — essa tem de seguir a assinatura do arquivo.

- **Uma âncora de substituição comeu a seta de uma arrow function (21/set/2026).** Ao inserir um helper antes de `const classeEspera = (d) => ...`, a troca deixou `(d) = d < 0 ? ...` — a tela inteira caiu com `d is not defined`. **A auditoria pegou no bloco de runtime.** Lição, irmã das outras três: **âncora de inserção não termina no meio de um operador**. Termina em fim de linha, ou em um token que não pode ser partido.

- **Redesenho chamado antes da tabela existir (Conferência, 21/set/2026).** Ao ligar o interruptor da conferência cega ao parâmetro, acrescentei um `ITENS.forEach(atualizarLinha)` logo depois de ajustar o interruptor — só que naquele ponto do script a tabela ainda não foi montada, e `atualizarLinha` procurava uma célula nula: `Cannot set properties of null`. **Quem redesenha é o render inicial, que já lê o parâmetro.** Lição: ao ligar um parâmetro a uma tela pronta, **o lugar certo é a leitura do estado, não uma chamada nova de render** — o render já existe e já roda depois.

- **`USUARIO_ATUAL` duplicado derrubou a Agenda inteira (21/set/2026).** O bloco compartilhado ganhou `const USUARIO_ATUAL` para o registro de atividades — e `pagina-inicio-agenda.html` **já tinha** um `const USUARIO_ATUAL`, uma string, usada para filtrar os compromissos do dia. `const` duplicado no mesmo escopo é erro de sintaxe: a tela abria morta. **Quem pegou foi a auditoria**, no bloco de runtime. **Lição, terceira do mesmo tipo:** bloco que vive em 41 arquivos **não usa nome genérico** — nome de lá tem prefixo do bloco (`PARAM_`, `ACOES_`, `USUARIO_SESSAO`). As duas anteriores foram o `const PARAM` em escopo de função e o literal de `id` repetido: os três são a mesma família — **código compartilhado colidindo com código de tela**.

- **Coluna importante escondida pela rolagem horizontal (Registro de atividades, 21/set/2026).** O texto confirmado é longo (a mensagem inteira do modal) e empurrou *Onde* e *Confirmação* para fora do cartão. Como `.estoque-table-wrap` tem `overflow-x:auto`, **nada estourou e a auditoria passou** — a tabela só rolava. Mas o selo *com senha / sem senha*, que é a informação mais importante da linha, ficava invisível sem rolar. Corrigido com `max-width` + `text-overflow:ellipsis` no detalhe e o texto completo no `title`. **Lição: `overflow:auto` esconde o problema em vez de resolver** — coluna que carrega a informação principal tem de caber na largura de referência, e isso se mede (`scrollWidth > clientWidth`), não se confia.

- **O mesmo literal de `id` em dois emissores reprovou a auditoria (21/set/2026).** Ao montar a grade do perfil, escrevi `'id="chkConf' + n + '"'` em dois lugares — na célula da matriz e na linha das ações específicas. A checagem de IDs duplicados lê o arquivo, vê o mesmo literal duas vezes e acusa. **A saída certa não é driblar a auditoria escrevendo diferente nos dois lugares** (foi o que o código antigo fazia, com um comentário explicando o drible): é ter **um emissor só**. Virou a função `caixa(chave, podeMarcar)`, usada pelos dois. O falso positivo sumiu porque a duplicação real sumiu junto.

- **Campo de senha ocupando 1.400px para caber 12 caracteres (18/set/2026).** O modal de confirmação é um **bottom sheet**: `left:0; right:0; bottom:0`, largura inteira da tela, deslizando de baixo (§8). Estilizei o campo novo com `width:100%` por reflexo, e ele virou uma faixa da largura do monitor. **Lição: `width:100%` só é inofensivo dentro de um container estreito — dentro de uma folha que ocupa a tela toda, todo campo precisa de `max-width`.** Corrigido com `max-width:420px`. Achado no screenshot de QA, não na auditoria: largura de campo não estoura layout, então nenhum bloco reclamou.

- **Um teste que passou verde quando devia falhar (18/set/2026).** Ao validar a exigência de senha, o teste afirmava `is_visible('#campoSenhaWrap')` e dava **verdadeiro nos dois cenários** — com e sem exigência. Dois erros somados: (1) o painel lateral fechado fica **fora da tela, mas com caixa**, e o Playwright chama isso de visível; (2) o teste chamava `abrirConfirmacao()` com o lote **vazio**, e a função tem `if (!LINHAS.length) return;` logo na primeira linha — nunca chegava no código sob teste. **Lição: teste de visibilidade se faz no `display` computado e no estado do componente (`.open`), nunca em "aparece na tela"; e teste que nunca vê a função rodar não é teste, é conforto.** Refeito semeando uma linha real no lote: aí o cenário ligado exigiu senha, e o desligado gravou direto.

- **"1 linha aplicadas de uma vez" (Acerto de Estoque).** Concordância quebrada no aviso de gravação: o plural estava só em `linha/linhas`, e o particípio ficou fixo no plural. Corrigido para `linha aplicada / linhas aplicadas`. Bug antigo, encontrado porque o teste desta entrega leu a mensagem inteira em vez de só conferir que ela apareceu.

- **O tema voltava ao escuro a cada troca de tela (18/set/2026).** O seletor do menu mudava `body.dark` e mais nada: navegar para a próxima tela recarregava o arquivo e o tema de fábrica voltava. Ninguém tinha reclamado porque ninguém tinha usado o claro por mais de uma tela. **Preferência que não sobrevive à navegação não é preferência, é um botão de brincadeira.** Corrigido junto com *Interface do usuário*: o tema passou a ser gravado e é aplicado **logo depois do `<body>`, antes da pintura** — se fosse aplicado no script do fim da página, a tela piscaria no tema errado a cada abertura.

- **A prévia media uma fila que não existia (18/set/2026).** *Parâmetros de estoque* nasceu com três listas de exemplo (`[0,1,3,3,5,9]`…) e anunciava *"na fila de hoje (6 saldos)"* enquanto o Endereçamento ao lado tinha **10**. Os números eram plausíveis, o que é o pior caso: **prévia que mede outro dado é pior que prévia nenhuma, porque dá confiança no número errado.** Corrigido extraindo as filas reais das telas de origem — hoje a prévia diz *5 em alerta, 4 em crítico* e a tela mostra exatamente 5 e 4, conferido no navegador. **Regra: dado de exemplo em prévia tem de ser o dado da tela que ele descreve, copiado de lá.**

- **Um comentário com `<body>` dentro reprovou 40 arquivos na auditoria (18/set/2026).** O bloco compartilhado novo trazia a frase *"o tema já foi aplicado no `<body>` antes da pintura"*; o bloco 1B conta ocorrências de `<body` e passou a ver duas por arquivo — *preâmbulo duplicado* em 40 telas de uma vez. Nada estava quebrado. **Lição: comentário é texto dentro do arquivo e a auditoria lê o arquivo, não o HTML renderizado** — não escrever tag literal em comentário. E o contrário também vale: 40 arquivos reprovando **ao mesmo tempo**, logo depois de uma inserção mecânica, é sinal de falso positivo, não de catástrofe; a leitura do primeiro caso resolveu em um minuto.

- **`const PARAM` caiu dentro de uma função e a tela quebrou inteira (18/set/2026).** Ao inserir o bloco de parâmetros nas duas telas de Estoque, usei como âncora a primeira ocorrência de `renderBreadcrumb();` — que estava **dentro do handler de clique do breadcrumb**, não no escopo do arquivo. O `const` nasceu com escopo de função e todo uso fora dela virou `PARAM is not defined`; a tela abria em branco. **Quem pegou foi a auditoria** (`erros_js=['PARAM is not defined']`), não a leitura do diff — o diff parecia perfeito, porque o texto inserido estava certo, só o *lugar* estava errado. **Correção:** remover e reinserir logo após `<script>\n`, e depois **provar** por índice de string que a definição vem antes do primeiro uso (`i_def < i_uso`) nos dois arquivos. **Lição:** âncora de inserção em arquivo grande tem de ser **única e no escopo certo** — `grep -c` antes de inserir, e conferência de escopo depois. E: **toda inserção de código roda a auditoria**, mesmo quando é "só mover uma constante".

- **A pasta do usuário tinha o Endereçamento DESATUALIZADO há três dias (18/set/2026).** O Passo 0 comparou tamanho por tamanho e achou 202 bytes de diferença em `pagina-estoque-enderecamento.html`. O diff mostrou que a pasta dele ainda tinha a **versão anterior à correção que ele mesmo pediu** em 15/set: o "desvincular" como texto cru, sem a coluna **Correção** e sem o botão `.btn-mini` **"Liberar vaga"**. A tela foi corrigida, ele aprovou no chat — e o arquivo **nunca foi gravado na pasta**. É exatamente o cenário que o Passo 0 existe para pegar, e a terceira vez que o chat disse "entregue" sem o arquivo ter aterrissado. **Regra reforçada: comparar a listagem real com o esperado ANTES de construir qualquer coisa, e conferir tamanho, não só a existência do arquivo.**
- **Badge de estado escrito à mão mente (18/set/2026).** O hub de Configurações nasceu com selos manuais — *configuração pendente*, *ambiente de testes*, *desabilitado* — copiados do Olist, em itens cujas telas **não existem**. Um item sem selo parecia pronto; um item com *"configuração pendente"* prometia uma tela que ninguém pode abrir. Corrigido derivando o selo do próprio destino: **tem `href` → construído, sem selo; não tem → "a construir"**. **Regra: estado exibido se deriva do dado, não se digita** — enquanto for campo livre, alguém vai esquecer de atualizar.

- **`opacity` esconde texto do auditor de contraste (16/set/2026).** `.inv-nao-contado` nasceu como `color: var(--text); opacity: 0.55` e **passou na auditoria** — o bloco 6 só descarta elemento com `opacity < 0.3` e mede a cor **declarada**, sem misturá-la com o fundo. Medido de verdade (cor efetiva = cor × opacidade + fundo × (1 − opacidade)), o rótulo dava **3.28:1 no escuro e 3.00:1 no claro**, reprovado nos dois temas. Corrigido tirando a opacidade e diferenciando por **tamanho** (12px) em vez de brilho. **Regra nova: texto de conteúdo nunca é apagado com `opacity`** — só cor de token. `opacity` continua válido para controle desabilitado (`.btn-mini:disabled`), onde contraste baixo é a informação. **A auditoria não pega isto** — é o mesmo tipo de ponto cego do `.mov-entrada`: classe existe, CSS existe, e o defeito só aparece quando alguém mede o resultado renderizado.
- **Aviso de importação disparando no caminho errado (16/set/2026).** O alerta "N produtos não apareceram no arquivo" foi escrito dentro de `abrirInventario()` sem escopo de origem. No caminho *Gerar*, **toda** linha nasce sem contagem — então ele disparava sempre, abrindo um modal por cima da tela recém-aberta e, de quebra, bloqueando o clique seguinte. Corrigido com `INV.origem === 'gerar' ? 0 : …`. Encontrado no teste de navegador, não na auditoria: não é erro de JS nem de contraste, é **um modal que não devia estar ali**.

Diferente da seção 13 (pendências conscientes, ainda em aberto), esta seção registra bugs que **já aconteceram e já foram corrigidos** — fica registrado pra reconhecer o padrão se acontecer de novo em outro lugar.

- **Modal aberto de dentro do `confirmar` de outro modal, fechado na mesma linha (Endereçamento, setembro/2026).** O handler do botão Confirmar é `if (acaoConfirmada) acaoConfirmada(); fecharModalConfirmacao();` — roda a ação **e depois fecha**. A ação de desvincular chamava `avisar(...)` no fim, que reabre o mesmo modal: ele abria e era fechado pela linha seguinte. O sintoma foi enganoso — a ação funcionava, o saldo mudava, só a confirmação não aparecia, e no teste automatizado o botão aparecia como "fora da viewport" (o modal estava com `translateY(100%)`).
  - **Correção:** o aviso sai **adiado** (`setTimeout` de 280ms, depois da transição de fechamento).
  - **Lição:** dentro do callback de confirmação de um modal, nunca abrir outro modal de forma síncrona — quem fecha é o handler externo, e ele roda depois de você.

- **Gancho de JS escrito como classe CSS, três vezes seguidas (Endereçamento, Transferência — setembro/2026).** `.desvincular-link`, `.item-qtd` e `.rec-qtd` foram criadas só para o `querySelectorAll` encontrar o elemento, sem nenhum estilo. A auditoria acusou "classe usada sem CSS" nas três — **com razão**: é exatamente a assinatura do componente copiado pela metade, e um gancho sem estilo torna esse check ruidoso e, portanto, menos confiável.
  - **Correção:** todos viraram `data-*` (`data-acao="desvincular"`, `data-campo="item-qtd"`, `data-campo="rec-qtd"`).
  - **Convenção, a partir daqui:** **classe é para estilo, `data-*` é para comportamento.** Se o seletor existe só para o JS achar o elemento, é atributo — nunca classe. Assim a seção 3 da auditoria continua significando uma coisa só: CSS que ficou para trás.
- **Falso positivo de ID duplicado criado por template string repetido (Vendedores — detalhe, setembro/2026).** O segundo checklist da tela montava o input com o mesmo literal `id="' + id + '"` do primeiro; a checagem de IDs duplicados lê o texto do arquivo e viu a string duas vezes. Os ids gerados eram diferentes (`chkModulo0`, `chkConf0`) — o duplicado era o **molde**, não o id.
  - **Correção:** o segundo template monta o id inline (`id="chkConf' + i + '"`), ficando textualmente diferente do primeiro.
  - **Lição:** quando a auditoria acusa algo que não é bug, a saída é **escrever diferente**, não ensinar a auditoria a ignorar. Cada exceção adicionada é um lugar onde ela deixa de avisar de verdade.

- **Nome de classe colidindo com componente existente, pintando fundo onde só se queria cor de texto (Acerto multi-produto e Controle de Estoques — detalhe, setembro/2026).** O CSS base — presente em **11 arquivos** — já define `.mov-entrada`/`.mov-saida` como **pill com fundo** (`background: rgba(34,197,94,0.15)`). Ao montar a coluna de quantidade, esses nomes foram reaproveitados só pela cor do texto; as regras novas sobrepuseram `color` mas **herdaram o `background`**, e a célula virou um retângulo verde/vermelho no meio da tabela.
  - **Onde escapou:** a auditoria não pega — a classe existe e tem CSS, então o check "classe sem CSS" passa; e o contraste do texto continuava aprovado, porque o fundo é translúcido e claro o bastante. Só apareceu **olhando o screenshot**. E tinha passado despercebido na entrega anterior: o detalhe do produto já estava assim havia um dia.
  - **Correção aplicada:** as regras novas passaram a se chamar `.qtd-entrada`/`.qtd-saida`, nos **dois** arquivos; o componente `.mov-*` original ficou intacto para quem o usa como pill.
  - **Lição:** antes de reaproveitar um nome de classe curto e genérico, conferir se ele já existe no CSS base — herdar `background`, `display` ou `position` de um componente homônimo é a mesma família do bug do `.floating-card` (§14). E screenshot continua sendo o único check que pega isso.

- **A mesma função de bind sem guarda derrubando uma tela inteira, pela segunda vez (Reposição, setembro/2026).** O bloco `bindMenuAcoes` foi copiado junto com o componente de dropdown para a tela nova, que não tem menu "Mais ações" — `getElementById(...).querySelector(...)` em `null` matou o script no carregamento, e **nada depois daquela linha rodou**: a fila veio com 0 bases, os contadores zerados, nenhum clique respondendo. A tela parecia simplesmente vazia, sem erro visível.
  - **Por que reincidiu:** na primeira vez (Controle de Estoques — detalhe) a guarda foi posta **só naquele arquivo**. Como o bloco é copiado entre telas, o arquivo de origem continuou sem guarda e replicou o defeito na cópia seguinte.
  - **Correção aplicada:** a guarda `if (!raiz) return;` entrou nos **9 arquivos** que têm `bindMenuAcoes`, nas duas variantes de id (`menuMaisAcoes` e `menuAcoes`). Nenhum ficou de fora.
  - **Lição, que vale além deste bloco:** corrigir só onde o bug apareceu é o mesmo que não corrigir, quando o código é copiado entre telas. A correção tem de ir para **o arquivo de onde se copia**, senão a próxima cópia traz o defeito de volta.

- **`innerHTML` destruindo o próprio elemento que a linha seguinte procura (Controle de Estoques — detalhe, setembro/2026).** O render dos KPIs fazia `getElementById('unFisico').textContent = ...` e, na linha seguinte, reescrevia o `innerHTML` do KPI pai — que **continha** esse `span#unFisico`. No primeiro render funcionava (o elemento vinha do HTML); a partir do segundo, `getElementById` devolvia `null` e o render inteiro morria com *"Cannot set properties of null"*. O sintoma era traiçoeiro: a tela abria perfeita e só parava de atualizar **depois da primeira ação do usuário**, sem nada visível quebrado.
  - **Correção:** a linha redundante saiu (o `innerHTML` já escreve a unidade) e o `id` interno foi removido do HTML, pra ninguém voltar a mirar nele.
  - **Lição geral:** nunca guardar referência — nem por `id` — a elemento que vive **dentro** de um container cujo `innerHTML` você reescreve. Ou o filho fica fora do container reescrito, ou é recriado e rebuscado a cada render. Vale para qualquer tela com render repetido.
- **Dropdown de formulário montado dinamicamente sem ligar o botão (mesma tela).** Os menus de Depósito, Motivo e Origem são preenchidos só quando o drawer abre, e a primeira versão ligou **só os itens**, na mão, sem passar pelo `inicializarDropdownSelect` — resultado: o menu nunca abria, porque ninguém tinha ligado o clique do botão. A auditoria pegou como *botão sem ação*.
  - **Correção:** os três passaram a usar o componente oficial (§9), chamado **no carregamento** (liga o botão) **e de novo a cada remontagem do menu** (religa os itens). O componente já se protege de bind duplo no botão via `dataset.dropdownInit`, então rechamar é seguro.
  - **Lição:** menu montado em runtime continua sendo `.dropdown-select` — nunca ligar item na mão; chamar o componente de novo depois do `innerHTML`.
- **Função de bind assumindo elemento opcional (mesma tela).** O bloco `bindMenuAcoes` foi copiado junto com o componente de dropdown e fazia `getElementById('menuMaisAcoes').querySelector(...)` sem guarda. A tela de detalhe não tem "Mais ações", então o script inteiro morria no carregamento — nenhum KPI, nenhum lançamento, nada, sem erro visível na tela.
  - **Correção:** `if (!raiz) return;` no começo do bloco.
  - **Lição:** ao copiar blocos de fiação entre telas, todo `getElementById` de elemento que pode não existir naquela tela precisa de guarda — senão um elemento ausente derruba tudo que vem depois dele no mesmo `<script>`.

- **Preâmbulo HTML duplicado quebrando a fonte Nunito e o box-sizing (Departamento de Produtos e Seção de Produtos, setembro/2026).** As duas telas foram montadas por um script que concatenava blocos de HTML/CSS reaproveitados de Categorias (cabeçalho, sidebar) em vez de editar o arquivo direto. O bloco de cabeçalho reaproveitado já vinha com seu próprio `<!DOCTYPE html><html><head>...<style>` de abertura completo, e o script prefixava um segundo por cima. Como a tag `<style>` em HTML é um elemento de "texto puro" (o navegador não interpreta tags dentro dela, só procura o próximo `</style>`), o segundo preâmbulo inteiro virou texto literal **dentro** do primeiro `<style>` já aberto — e por regra de recuperação de erro do CSS, o navegador descartou a primeira regra real do arquivo (o reset universal `* { box-sizing:border-box; margin:0; padding:0; font-family:'Nunito',... }`) junto com esse lixo. Resultado visível: a página inteira perdeu a fonte Nunito (caiu pro padrão do navegador, Times New Roman) e o `box-sizing:border-box`, o que também deslocou textos, nomes e a barra de busca — tudo sem nenhum erro no console e sem pegar nos checks automáticos existentes na época (JS válido, toda classe com CSS, "Nunito" citado em outras regras do arquivo). Só apareceu comparando o **estilo computado de verdade** (`getComputedStyle`) contra uma página já aprovada.
  - **Correção aplicada:** removido o preâmbulo duplicado; as duas páginas foram regeradas e re-entregues.
  - **Proteção adicionada** (`assets/auditoria.py`, seção 1B + seção 5, e checklist da skill `desk-company-page-qa`): toda auditoria agora conta `<!DOCTYPE>`/`<html>`/`<head>`/`<style>`/`<body>` e reprova se algum aparecer mais de uma vez, **e** testa o `fontFamily`/`boxSizing` computado real do `<body>` num navegador de verdade — não só o texto do CSS-fonte. Isso vale pra qualquer página, gerada por script ou não.
  - **Validação de reforço:** Embalagens de Produtos e Marcas de Produtos (mesmo gerador de script, já com a correção e a auto-checagem embutida) passaram por essa auditoria 1B + o teste de estilo computado antes de serem entregues, e ambos vieram limpos de primeira.
- **"Selecionar todos" renderizando no meio da lista em vez do topo (Embalagens de Produtos, setembro/2026).** O wrapper da listagem usava por engano a classe `.floating-card` (com `style="position:static; width:auto; height:auto"` pra tentar neutralizar o `position:fixed` dela) em vez de `.card`. O problema é que `.floating-card` é a classe real da **sidebar flutuante** (§3) e já vem com `display:flex` sem `flex-direction` definido (= `row` por padrão) — isso transformou os filhos diretos do wrapper ("Selecionar todos", a lista de itens, o estado vazio, a barra de seleção) em itens flex **lado a lado** em vez de empilhados verticalmente. Com `align-items` no valor padrão (`stretch`), a linha "Selecionar todos" esticou pra altura inteira do container e, por ter seu próprio `align-items:center`, seu conteúdo (checkbox + texto) ficou centralizado verticalmente **no meio da tela**, deslocado à esquerda da coluna de itens — exatamente o bug relatado pelo usuário. Não foi pego pela auditoria automática porque `.floating-card` é uma classe real com CSS de verdade (o check "classe sem CSS" não se aplica) — só apareceu comparando o **layout renderizado de verdade** (screenshot) contra o padrão esperado.
  - **Correção aplicada:** wrapper trocado pra `<div class="card">` (igual às outras 3 listagens de módulo único); "Selecionar todos" voltou a ficar empilhado no topo da lista, confirmado por screenshot.
  - **Lição:** ao copiar/gerar uma listagem nova, **sempre conferir visualmente** (screenshot, não só o texto do HTML) que o wrapper do card é `.card` — nunca reaproveitar `.floating-card` (exclusiva da sidebar) mesmo neutralizando `position`/`width`/`height` via `style` inline, porque o `display:flex` dela continua ativo por baixo e muda o comportamento dos filhos diretos.
- **Categorias desalinhada do padrão canônico (nomenclatura de seleção, sem paginação, e o bug do `.theme-seg`), corrigido em setembro/2026.** Categorias era a única listagem que ainda faltava três coisas já padronizadas nas outras 4 "lista única": (1) os IDs `selecaoBar`/`selecaoCount` em vez dos canônicos `barraSelecao`/`selecaoInfo` (ver §8); (2) o rodapé de paginação do §7; e (3) o bug real do `.theme-seg` (ver §5) — o toggle "Categoria de Produtos/Categoria de Fornecedores" dentro do drawer reaproveita a classe visual `.theme-seg`, e o listener genérico do seletor de tema (não escopado a `.theme-picker`) disparava junto: como esses botões não têm `data-theme`, `mode` vinha `null`/`undefined` e o código caía no ramo "auto", forçando `document.body.classList.toggle('dark', ...)` conforme a preferência do sistema operacional — ou seja, **clicar em "Categoria de Fornecedores" podia trocar o tema claro/escuro da tela inteira sem o usuário pedir**. O `.active` do toggle de tipo não quebrava visualmente (o bind próprio do toggle, registrado depois, corrigia o estado por cima), o que tornou o bug fácil de não notar sem testar interativamente.
  - **Correção aplicada:** o listener do tema foi escopado a `.theme-picker .theme-seg button` (nos dois pontos: ao ler os botões e ao limpar `.active`); os IDs/classes de seleção foram renomeados para o padrão canônico; e o rodapé de paginação (resumo + dropdown 10/25/50/100 + anterior/próxima, com "Selecionar todos" escopado à página atual) foi adicionado, incluindo o componente `.dropdown-select` que essa página ainda não tinha.
  - **Validação:** auditoria automatizada limpa + testes interativos confirmando que clicar no toggle de tipo não altera mais `document.body.classList` nem o botão ativo do seletor de tema real, e que o seletor de tema real continua funcionando normalmente.
- **Falso positivo na auditoria automática por texto literal `<select>` dentro de comentário CSS (Vendedores, setembro/2026).** Ao copiar o bloco de CSS de paginação/dropdown de Categorias pra Vendedores, o comentário ficou como `/* ===== Dropdown customizado (nunca <select> nativo — §9) ===== */` — um comentário de **bloco CSS** (`/* */`), não de linha JS (`//`). A checagem "§4: aderência ao design system" do `assets/auditoria.py` já sabe ignorar `<select>` citado dentro de comentário `//` (padrão usado em todo comentário JS equivalente do sistema), mas não removia comentários `/* */` antes de procurar `<select`, então acusou "`<select>` nativo" numa página que não tinha nenhum `<select>` de verdade.
  - **Correção aplicada:** reescrito o comentário sem os sinais de menor/maior (`nunca select nativo`, sem `<>`) — resolve o caso sem mudar o comportamento da auditoria. Também foi adicionada a classe-gancho nova `perfil-checkbox` (dropdown multi-seleção de Perfis de Contato, §9.1) à lista de exceções conhecidas do checador de "classe sem CSS", pelo mesmo motivo já registrado pra `loja-checkbox`.
  - **Lição:** ao escrever comentário novo (CSS ou JS) que cite `<select>`, `<div>` ou qualquer tag entre `<>` só como texto explicativo, preferir escrever sem os sinais de `<>` — evita falso positivo em qualquer checagem futura baseada em regex simples, sem precisar tocar no script de auditoria toda vez.
- **Menu "Mais ações" quebrando texto em 2 linhas por item (Vendedores-detalhe, setembro/2026).** O `.dropdown-select-menu` do menu de ações (§9) foi só reposicionado com `right:0; left:auto;` (pra abrir alinhado à direita do botão, já que "Mais ações" fica no canto direito do cabeçalho), sem definir uma largura própria. Como `.dropdown-select` (o container relative que serve de referência de posicionamento) só é tão largo quanto o próprio botão "Mais ações" — bem mais estreito que rótulos como "Alterar senha de acesso" — o cálculo de shrink-to-fit do navegador para um elemento absolutamente posicionado usa a largura do container como teto, e cada item de texto mais longo que esse teto quebrava em 2 linhas dentro do menu.
  - **Correção aplicada:** adicionado `min-width:220px; white-space:nowrap;` no `.dropdown-select-menu` desse dropdown específico — cada item passou a ficar numa única linha, mesmo que o menu (agora mais largo que o botão) avance por baixo do badge de status ao lado. Confirmado que isso é o comportamento esperado, não um bug de sobreposição: um menu suspenso pode perfeitamente ficar mais largo que o botão que o abre.
  - **Lição:** todo dropdown de "menu de ações" (não dropdown de seleção de valor) precisa de `min-width` explícito — o problema só aparece quando o botão-gatilho é mais estreito que o maior rótulo do menu, o que não acontecia nos dropdowns de seleção de valor já existentes (o botão ali já nasce largo o bastante pro valor escolhido). Ver a regra já adicionada em §9.
- **Seletor de tema não escopado em 15 dos 22 arquivos — 2 com bug ativo, 13 latentes (varredura de setembro/2026).** Depois de corrigir o caso de Categorias, ficou registrado que só faltava `pagina-cadastros-fornecedores-detalhe.html`. Uma varredura completa mostrou que a estimativa estava muito subdimensionada: **15 arquivos** ainda tinham `document.querySelectorAll('.theme-seg button')` sem o escopo `.theme-picker`. Em **2 deles o bug estava ativo** — `pagina-cadastros-clientes-detalhe.html` (nunca tinha sido registrado em lugar nenhum) e `pagina-cadastros-fornecedores-detalhe.html`, os dois com o toggle Pessoa Física/Jurídica (`#tipoPessoaToggle`) reaproveitando a classe visual `.theme-seg`: clicar em "Pessoa Jurídica" caía no listener do tema e, como o botão não tem `data-theme`, `mode` vinha `null` e o código entrava no ramo "auto", trocando o tema claro/escuro da tela inteira sem o usuário pedir. Nos outros **13 o bug estava latente** — o listener solto, mas nenhum outro elemento usando `.theme-seg` ainda, então o defeito só apareceria no dia em que alguém adicionasse um toggle novo nessa tela.
  - **Correção aplicada:** os 15 arquivos foram corrigidos de uma vez (`.theme-picker .theme-seg button` nos dois pontos: ao registrar o listener e ao limpar o `.active`), com um comentário explicativo no código pra não regredir. Validado interativamente: nas 4 telas que reaproveitam `.theme-seg` num toggle próprio, clicar no toggle não altera mais `document.body.classList` nem o `.active` dos botões de tema, e o seletor de tema real continua funcionando.
  - **Lição:** quando um bug do tipo "esta tela tem X" for encontrado, a pergunta seguinte é **"em quantos arquivos isso existe?"**, não "está corrigido aqui?". Contar por `grep` custa segundos; confiar na anotação anterior custou 14 arquivos passarem batido. E vale corrigir também o **latente**: um listener solto numa tela sem toggle hoje é uma armadilha pronta pra próxima pessoa que adicionar um.
- **`.dropdown-select-menu` sem `max-height` em 6 telas ao mesmo tempo (setembro/2026).** A regra `max-height:240px; overflow-y:auto` (§9) faltava em Clientes, Clientes-detalhe, Fornecedores, Fornecedores-detalhe, Produtos-detalhe e no molde de referência — todas descendentes de um mesmo arquivo antigo copiado antes da correção existir. O registro anterior citava só 3 dessas telas. Corrigido nas 6 e coberto pela auditoria automatizada.
- **Arquivos "entregues" que nunca chegaram na pasta do usuário (descoberto em setembro/2026).** Três módulos dados por prontos — Embalagens, Departamento de Produtos e Seção de Produtos — tiveram o `device_commit_files` aterrissado numa subpasta `Claude outputs\` em vez da pasta principal `C:\Claude AI\Desk Company\`. Resultado: a pasta real do usuário ficou com Departamento e Seção **na versão anterior à paginação** (documentada aqui como pronta desde set/2026) e **sem o arquivo de Embalagens**, enquanto a conversa registrava tudo como entregue. Não é bug de código — é bug de processo, e o mais perigoso do tipo, porque a documentação e a conversa concordavam entre si enquanto o disco discordava dos dois.
  - **Correção aplicada:** as versões corretas foram gravadas na pasta principal e conferidas por tamanho via `device_list_dir` (não só pela resposta do commit).
  - **Lição:** entrega só conta depois de **confirmada no destino**. Depois de qualquer commit, listar a pasta e conferir que o arquivo aparece com o tamanho novo. E ao abrir sessão, comparar a listagem da pasta com a tabela de módulos do §12 — um arquivo faltando ou menor que o esperado aparece na hora.
- **Os tokens do design system não servem como paleta categórica de texto (descoberto construindo Endereços, setembro/2026).** Endereços precisava de 6 cores distinguíveis, uma por tipo de posição, aplicadas como **tag de contorno** (a cor é do texto e da borda; o fundo continua o da página). Medindo antes de codar — lição do bug do avatar, logo acima — só **4 tokens** passavam de 4,5:1 nos dois temas: `--active-text`/`--chart-1`, `--danger`, `--text` e `--text-heading`. `--chart-2` dava 2,87 no claro, `--chart-3` 1,62 e `--warning` 1,96. Não dava pra tirar 6 cores dali.
  - **Solução:** uma **paleta categórica própria** (`.tt-picking`, `.tt-pulmao`, `.tt-avaria`, `.tt-quarentena`, `.tt-recebimento`, `.tt-expedicao`), com um valor por tema, escolhida medindo o contraste contra o fundo da página. Pior caso aferido: **4,67:1** (Avaria no tema claro).
  - **Lição:** os tokens `--chart-*` foram desenhados como **cor de preenchimento** (fundo de barra, fatia de gráfico, avatar) e funcionam bem nesse papel. Como **cor de texto** eles não sustentam contraste — texto pequeno precisa de um valor mais escuro no tema claro e mais claro no escuro. Quando uma tela nova precisar de cores categóricas em texto, definir uma paleta própria e medir, em vez de reaproveitar `--chart-*`.
- **Iniciais do avatar em branco fixo sobre fundos claros — contraste de até 1,68:1 (descoberto construindo Depósitos, setembro/2026).** O padrão "cor automática por Tipo" (§11) nasceu em Lojas Desk pintando o fundo do `.profile-avatar` com um token de tema (`var(--chart-2)`, `var(--warning)`, `var(--text)`) e deixando `color:#fff` fixo no `.profile-avatar`. O problema é que esses tokens **trocam de luminosidade entre os temas**: `--text` é `#3E3E3D` no claro (branco por cima lê bem, 10,71:1) e `#AFADA2` no escuro (branco por cima cai pra **2,25:1**); `--chart-3` é `#B7C7F5` no claro (**1,68:1**) e `#263A73` no escuro (10,85:1); `--warning` é `#F5A623` nos dois (**2,03:1** sempre). Medido tipo a tipo, **6 das 10 combinações tema × tipo estavam abaixo de 3:1** — iniciais praticamente ilegíveis, sem nenhum erro no console e sem reprovar em nenhuma checagem existente.
  - **Correção aplicada (em Depósitos):** fundo e cor de texto passaram a viver juntos numa classe por tipo (`.av-geral`, `.av-galpao`, `.av-loja_fisica`, `.av-trade_marketing`, `.av-transito`), com a cor do texto redefinida em `body.dark`. Escolha feita medindo o contraste real de cada combinação e ficando com a melhor das duas (`#FFFFFF` ou `#101010`). Resultado aferido no navegador: pior caso **4,80:1**, todos os outros acima de 6:1, nos dois temas.
  - **Efeito colateral da auditoria:** montar a classe por concatenação (`'av-' + dep.tipo`) fez a checagem "classe sem CSS" reprovar o literal `av-`, que sozinho não existe no CSS — mesmo tipo de falso positivo já registrado pra `loja-checkbox`. Resolvido escrevendo os nomes por extenso num mapa (`CLASSE_AVATAR`), sem mexer no script de auditoria.
  - **Propagado no mesmo dia** (a pedido do usuário, pra não acumular pendência): `pagina-cadastros-lojas-desk.html` e `pagina-cadastros-vendedores.html` — as duas únicas telas além de Depósitos que usavam o padrão antigo (`COR_POR_TIPO`/`corAvatar` + `color:#fff` fixo). As páginas `-detalhe.html` das duas não têm avatar, então não foram tocadas. Em Lojas Desk os mapas viraram `CLASSE_AVATAR`; em Vendedores, `CLASSE_POR_TIPO_LOJA` + `CLASSE_AUTONOMO` e a função `corAvatar()` virou `classeAvatar()`. **O `.origem-badge` do drawer de preview das duas telas tinha exatamente o mesmo defeito** (mesmo fundo derivado do tipo, com `color:#fff` fixo na regra da classe) e foi corrigido junto, reaproveitando as mesmas classes `.av-*`.
  - **Detalhe de cascata que quase passou batido:** `.profile-avatar`, `.origem-badge` e `.av-*` têm todos especificidade 0,1,0 — quem vence é a **última regra do arquivo**. Na primeira tentativa em Vendedores o bloco `.av-*` foi inserido logo depois de `.profile-avatar`, mas **antes** de `.origem-badge`, então o `color:#fff` do badge continuava ganhando e o badge seguia ilegível enquanto o avatar já estava certo. Corrigido movendo o bloco `.av-*` pra depois das duas regras-base. Ao adicionar uma classe modificadora de mesma especificidade, conferir a **posição no arquivo**, não só o conteúdo da regra.
  - **Verificação:** contraste medido no navegador (`getComputedStyle`, não o CSS-fonte) em todas as combinações tema × tipo das 3 telas, incluindo os badges dentro dos drawers: **pior caso 4,80:1**, nenhum reprovado, zero erro de runtime.
  - **Lição:** um token de tema serve como **fundo** em ambos os temas, mas a cor do texto por cima dele **não pode ser fixa** — tem que virar par (fundo + texto) e ser redefinida junto com o tema. É a mesma família do bug do `--active-bg` no §1, só que uma casa adiante: lá o erro foi usar cor de fundo como cor de texto; aqui foi assumir que uma cor de texto vale pros dois temas.
- **Nome da loja grafado errado em 56 lugares: "Desk Shop" em vez de "Desk Shope" (setembro/2026).** O nome real da loja é **Desk Shope**, com "e" no fim. As 4 telas de Início (`pagina-dashboard-kpis`, `-boas-vindas`, `-agenda`, `-minha-conta`), que foram as primeiras construídas, sempre grafaram certo — 13 ocorrências. Da primeira tela de Cadastros em diante o nome derivou pra "Desk Shop" e o erro se propagou por cópia entre arquivos, chegando a **56 ocorrências em 13 `.html` + os 2 `.md`**, incluindo os dados mocados, os filtros de loja e o próprio texto das decisões de arquitetura. Ninguém notou porque toda tela nova era copiada de uma tela já errada — a consistência interna do erro é o que o escondeu.
  - **Correção aplicada:** substituição em massa com `Desk Shop(?!e)` (lookahead negativo, pra não transformar as 13 ocorrências já corretas em "Desk Shopee") nos 15 arquivos, mais as duas menções abreviadas do roadmap ("Pedidos da Shope", "Pedido de Produto (Shope/Brands)"). A menção a **Shopee** (o marketplace, em F8) foi deixada intacta de propósito.
  - **Lição:** nome próprio de loja/marca é dado, não texto livre — vale conferir a grafia contra uma fonte única antes de propagar. E quando a correção envolve um nome que é **prefixo de outro** ("Desk Shop" dentro de "Desk Shope"), a substituição precisa de lookahead, senão ela corrompe justamente os arquivos que já estavam certos.
- **Lojas Desk sem o rodapé de paginação, enquanto a doc dizia que todos os cadastros tinham (setembro/2026, abertura de F5).** A listagem de Lojas Desk nasceu antes do padrão de paginação virar obrigatório no §7 e nunca foi revisitada — e, diferente de Categorias (que só estava com nomenclatura antiga), ela sequer tinha o componente `.dropdown-select` no arquivo: nem o CSS, nem a função `inicializarDropdownSelect`. O §12 e o §7 já afirmavam que "todos os cadastros seguem esse padrão", então o desvio era invisível pela documentação; só apareceu num `grep` por `paginacao|Mostrando` rodado em todas as listagens de uma vez, como parte da auditoria de abertura de fase.
  - **Correção aplicada:** adicionados o bloco CSS de `.dropdown-select*` (já com `max-height:240px; overflow-y:auto`, §9) e de `.paginacao-*`, o rodapé de paginação (resumo + dropdown 10/25/50/100 + anterior/próxima), a função `inicializarDropdownSelect` com abertura inteligente e fechamento mútuo, e o escopo de "Selecionar todos" à página atual (`lojasPagina().lista` em vez de `lojasFiltradas()`), além do reset de `paginaAtual` ao buscar ou trocar o filtro de tipo.
  - **Validação:** auditoria automatizada limpa nos 22 arquivos + teste interativo no navegador (dropdown abre/fecha, `max-height` computado em 240px, escolher 25 atualiza o resumo, selecionar todos/cancelar, filtro de tipo não altera `document.body.classList`) + screenshot confirmando o rodapé no fim do card e o "Selecionar todos" empilhado no topo.
  - **Lição:** a auditoria automatizada cobre o que já virou regra no script; um padrão que só está escrito no `.md` continua invisível até alguém contá-lo por `grep`. Ao abrir fase nova, vale rodar uma varredura dos padrões **textuais** do design-system (paginação, nomenclatura, componentes obrigatórios) além do script — foi assim que este apareceu.
- **Contraste: texto branco sobre fundo claro, em todo o sistema (setembro/2026).** Uma varredura que mede o contraste **computado** de todo texto das 29 telas, nos dois temas, achou 29 grupos reprovando em 4,5:1 — de 1,20 (o "›" do breadcrumb, que usava a cor de BORDA como cor de texto) a 3,98. Três naturezas diferentes, cada uma corrigida no nível certo:
  - **Token.** O azul da marca (`#2979FF` claro / `#4C8DFF` escuro) era claro demais atrás de texto branco — botão primário dava **2,97 em 17 telas**, aba ativa 3,20/3,98 em 29. Virou `#2563EB` nos dois temas (branco = 5,17). O verde de sucesso `#16A34A` como **texto** sobre branco dava 3,30; virou `#15803D` (5,02). O `--negativo` do tema escuro dava 3,57; virou `#D96B80` (5,38).
  - **Regra.** `btn-primary` e `pill-btn.active` usavam o azul de **gráfico** como fundo sólido; passaram a usar o azul da marca. `btn-danger` ganhou `--danger-solid` (`#DC2626`), porque o vermelho bom como **texto** no tema escuro (`#EF4444`, 4,71) é ruim como **fundo** (3,76) — são papéis diferentes e precisam de tokens diferentes.
  - **Runtime.** Avatares e badges recebem a cor de fundo por `style` inline, vinda de mapas de cor em JS — **nenhuma regra de CSS alcança isso**. Em vez de decidir cor a cor e errar de novo no próximo chip, entrou em todas as telas um helper de **tinta automática**: lê a luminância do fundo que de fato ficou aplicado, calcula o contraste com a tinta atual e **só troca quando o par reprova em 4,5:1**. O que já passa não é tocado — isso preserva texto colorido proposital e mexe apenas no que estava ilegível. Roda no carregamento, a cada render (MutationObserver) e ao trocar de tema.
  - **Resultado aferido:** zero reprovações nas 31 telas, nos dois temas. **Lição:** contraste é medição, não opinião — e a regra do sistema agora é "a tinta segue a luminância do fundo", não "esse chip usa branco".
- **Telas do mesmo fluxo com mock que não conversa (Endereçamento, setembro/2026).** Endereçamento oferecia códigos de endereço que **não existem** no cadastro (`ADM-01-A`, `A-01-01-P`, `LJ-VIT-01`), oferecia endereço **inativo** e de **Quarentena** para saldo bom, e listava saldo de um depósito que **não usa endereçamento** — depósito sem endereçamento libera o saldo direto na conferência e nunca tem fila. É só mock, mas engana exatamente quem está validando o fluxo, que é o pior momento para enganar.
  - **Correção aplicada:** o mock virou espelho do cadastro (mesmos códigos, tipos e situação), saldo bom só entra em **Picking ou Pulmão**, bloqueado só em **Avaria**, inativo não é oferecido pra nada, e a fila só aceita depósito com endereçamento ligado. Recebimento e Expedição ficaram de fora de propósito: são áreas de passagem, e endereçar saldo ali seria dizer que a mercadoria mora na doca.
  - **Lição:** quando duas telas leem o mesmo cadastro, o mock de uma tem de ser cópia do da outra — divergência aqui não é detalhe de protótipo, é regra de negócio inventada sem querer.
- **Lista de erros escondida com conteúdo velho (Nota de Entrada, setembro/2026).** O bloco de pendências era escondido quando tudo estava certo, mas o `<ul>` continuava preenchido. Reaparecia mentindo na falha seguinte, e leitor de tela continuava lendo o que já tinha sido resolvido. **Lição:** esconder não é limpar — componente que guarda conteúdo derivado precisa zerar junto.
- **A conferência cega não era cega (Conferência, setembro/2026).** Bastava digitar qualquer número para a tela revelar na hora a quantidade da nota **e o tamanho exato da diferença** (`14` e `-12`). Com esses dois números na tela, "conferir" vira ajustar a contagem até o sistema parar de reclamar — que é exatamente o que a conferência cega existe para impedir. Pior: dava para **descobrir a quantidade da nota por tentativa**, digitando valores e olhando a divergência mudar.
  - **Correção aplicada:** com divergência, a tela informa **apenas que ela existe** (etiqueta "divergência", sem número), mantém a quantidade da nota oculta e oferece duas saídas no lugar do motivo — **Recontar** ou **Confirmar contagem**. Só depois da confirmação explícita os números aparecem, o motivo passa a ser obrigatório e o fluxo com o fornecedor começa. Editar a contagem **derruba a confirmação** e esconde tudo de novo, o que fecha a porta do chute por tentativa. O resumo acompanha: enquanto houver divergência não confirmada, "Valor conferido" mostra *aguardando confirmação*, porque valor da nota menos valor conferido entregaria a quantidade que falta. Fechar a conferência com divergência não confirmada é bloqueado.
  - **Lição:** numa tela que existe para esconder um número, **todo lugar onde esse número pode ser derivado conta como vazamento** — o total do rodapé e a diferença de valores tanto quanto a coluna. E quando a validação depende de um dado oculto, a ordem certa é *contar → confirmar → revelar*, nunca *contar → revelar → corrigir*.
- **Corte errado do "trecho genérico" ao derivar uma tela de outra (Conferência, setembro/2026).** As telas novas são montadas reaproveitando fatias da irmã mais parecida: cabeça/CSS, casca (sidebar + flyouts), JS de navegação e o **bloco genérico** (modal + componente de dropdown). O corte do bloco genérico foi feito de marcador de seção a marcador de seção (`// ===== MODAL =====` até `// ===== SALVAR =====`), e entre os dois havia código **específico da tela de origem** sem marcador próprio — o bind do menu de ações e os `inicializarDropdownSelect` dos campos da Ordem de Compra. Resultado: `document.getElementById('inputFornecedor')` veio junto, deu `null`, e o erro parou o script **antes** do `renderItens()` — a página abria com a tabela vazia e sem nenhum erro visível na tela.
  - **Correção aplicada:** o corte passou a terminar no início do bloco específico (`// "Ações" e MENU DE AÇÕES`), não no próximo marcador `=====`.
  - **Lição:** ao reaproveitar um trecho de outra tela, o limite é onde o código **deixa de ser componente e vira tela** — marcador de seção é pista, não garantia. E o sintoma a reconhecer: página que carrega bonita com uma região vazia normalmente é exceção de JS no carregamento, não CSS.
- **Classe usada no HTML sem nenhuma regra de CSS (Conferência, setembro/2026).** `cel-nota`, `cel-dif`, `cel-motivo` e `motivo-op` existiam só como gancho de `querySelector`. A auditoria reprova isso (seção 3) porque é exatamente a assinatura de componente copiado pela metade. **Correção:** as três células ganharam o CSS que já era delas (`white-space:nowrap`, `min-width`), e o filtro de motivo passou a selecionar por `[data-sinal]` — o dado de verdade — em vez de uma classe decorativa. **Lição:** gancho de seletor deve ser atributo de dado, não classe vazia.
- **Campo dependente que não revalidava (Conferência, setembro/2026).** Escolher o Destino da avaria gravava o valor e recalculava o resumo, mas não chamava `atualizarLinha`, que é quem tira a borda vermelha de "campo pendente" — o usuário preenchia e o campo continuava acusando erro. **Lição:** todo `onChange` que satisfaz uma obrigatoriedade tem de reexecutar a validação daquela linha, não só recalcular totais.
- **`textarea` com fundo branco no tema escuro (Ordens de Compra — detalhe, setembro/2026).** Exatamente o mesmo bug do campo de senha registrado logo abaixo, com outro tipo de campo: a regra base do formulário listava `input[type="text"]` e `textarea` ficou de fora, então os dois campos de observação caíam no estilo nativo do navegador — fundo branco, texto preto, sem borda do tema. **Desta vez a auditoria automatizada pegou sozinha**, antes de qualquer teste manual: o check de "fundo computado dos campos de formulário" (seção 5) reprovou a página nomeando os dois `textarea`.
  - **Correção aplicada:** `textarea` adicionado ao lado de `input[type="text"]` nas três regras compartilhadas (base, `:focus`, `.has-error`), mais `resize:vertical` e `min-height`.
  - **Lição confirmada pela segunda vez:** ao usar um tipo de campo novo numa tela, conferir se ele está listado nas regras compartilhadas de `.form-field`. Não existe herança por estar dentro do mesmo container — cada seletor de tipo precisa ser explícito. O padrão já pegou `password` e agora `textarea`; o próximo candidato é `input[type="number"]` ou `select` nativo, se algum dia entrar.
- **Campo de senha com fundo branco enquanto oculto, só ficando no padrão escuro depois de revelado (Vendedores-detalhe, setembro/2026).** A regra base de estilo de formulário (`.form-field input[type="text"], .form-field select, .form-field textarea { ... }`) listava só `input[type="text"]` — nunca precisou de `input[type="password"]` porque Vendedores foi o primeiro cadastro do sistema com campo de senha. Resultado: enquanto o campo estava com `type="password"` (estado padrão, oculto), ele não batia com nenhum seletor do CSS do projeto e caía no estilo nativo do navegador (fundo branco, texto preto, sem a borda/foco do tema) — quebrando completamente o visual escuro. No instante em que o usuário clicava no "olhinho" (§11) e o JS trocava o `type` pra `text`, o campo passava a bater com `input[type="text"]` e ficava correto na hora — o que tornou o bug fácil de não perceber numa checagem rápida (parecia certo assim que se testava o próprio olhinho) e só ficou óbvio comparando print a print os dois estados lado a lado.
  - **Correção aplicada:** `input[type="password"]` adicionado ao lado de `input[type="text"]` nas três regras relevantes (estilo base, `:focus`, `.has-error`) — os dois tipos agora têm exatamente o mesmo visual em qualquer estado. Também adicionado um reset de autofill (`input:-webkit-autofill`) nos campos de senha, pra uma senha salva pelo navegador não reintroduzir fundo claro por cima do tema escuro.
  - **Lição:** ao estilizar um tipo de input que é novo no projeto (aqui, `password`), nunca assumir que ele "herda" o estilo de `input[type="text"]` por estar dentro do mesmo `.form-field` — cada seletor de tipo (`[type="..."]`) tem que ser listado explicitamente nas regras compartilhadas do formulário, ou o navegador aplica o próprio padrão nesse tipo específico sem avisar nada no console.

## 14.1 Lições de 22/set/2026 (Contas a Pagar)

- **Mock que marca o efeito sem registrar a causa mente.** O título nascia com `pago = 6740` e `pagamentos = []`: conta paga sem linha de pagamento, que não se explica e não se estorna — o estorno trabalha em cima do pagamento, não do campo `pago`. Regra: **quando o mock grava um efeito, ele grava o evento que o causou.**
- **Nome de constante colide entre componente e tela.** `DIAS_SEMANA` já era do calendário (as letras do cabeçalho). A auditoria pegou antes do navegador — mas o nome certo diz o que é: `DIAS_SEMANA_NOME`.
- **Campo de data precisa do `<div class="date-pop"></div>` no HTML.** `inicializarDataField` sai calado se ele faltar (`if (!input || !btn || !pop) return;`): o ícone aparece, o clique não faz nada e nenhum erro é lançado. **Componente que sai calado só é pego por teste que abre o calendário** — foi assim que este foi.
- **Teste em tela com abas declara em qual aba está.** Já era lição; nesta tela virou função (`def aba(pg, nome)`), porque são quatro abas e o painel de pagamento abre por cima de uma delas.
- **`aoSalvarCadastro` navega**, a menos que o parâmetro *"ao salvar: ficar na tela"* esteja ligado. Teste que confere o que foi gravado tem de ligar o parâmetro — senão lê o mock da tela seguinte e acha que nada foi salvo.

## 14.2 Lições de 23/set/2026 (repetição, escopo e a auditoria completa)

- **Painel copiado sem o CSS do `textarea`.** A listagem de Contas a Pagar nasceu do extrato do Caixa, que não tinha textarea nenhum. O painel de Pagamento trouxe um, e o campo ficou com o estilo nativo do navegador: **fundo claro vazando no tema escuro**. Não aparece lendo código, não aparece na seção 3 (a classe `.form-field` existe) — só na medição de estilo computado. **Componente novo numa tela: conferir o CSS de cada elemento que ele trouxe, um por um.**
- **`.num` não existe no design system.** Usei `class="num"` na tabela de pagamentos; célula numérica é **`.cx-num`**, e o `th` já é à direita por padrão. Sem CSS, a coluna de dinheiro ficava alinhada à esquerda — erro visível na tela e invisível no código.
- **`empty-state-text` não existe; é `empty-state-sub`.** Mesma família de erro: nome plausível, classe inexistente.
- **Nomenclatura `selecaoBar` era desvio.** O canônico das telas novas é **`barraSelecao`**. Três telas de Finanças nasceram com o nome antigo — desvio que só aparece comparando telas (seção 4B), nunca lendo uma.
- **Menu ancorado à direita precisa de `min-width`.** Sem ele os rótulos longos quebram em duas linhas, porque o menu cresce para a esquerda a partir de zero.
- **Asserção de texto de tela não pode olhar `pg.content()`** — ele traz o `<script>` junto, e neste caso foi o **próprio comentário do código** que derrubou o teste (`// Sem "3/12"...`). Texto renderizado se confere em `pg.text_content(...)`.
- **Teste que clica em linha de lista tem de escolher entre as linhas VISÍVEIS.** Com filtro inicial no mês e paginação, o primeiro item do array pode estar na página 2 — e `querySelector(...).click()` em `null` derruba o teste. Pegar o alvo do DOM, não do mock.
- **`aoSalvarCadastro` navega** a menos que o parâmetro *"ao salvar: ficar na tela"* esteja ligado. Teste que confere o que foi gravado tem de ligar o parâmetro, senão lê o mock da tela seguinte e conclui que nada foi salvo.
- **Mock que marca o efeito sem registrar a causa mente** (já era lição, reincidiu): título com `pago` preenchido e `pagamentos` vazio é conta paga que não se explica e, pior, não se estorna.
- **`style.display = 'flex'` num `.form-field` quebra o campo inteiro.** O `.form-field` é **bloco** (`margin-bottom:18px`), com rótulo em cima, campo no meio e dica embaixo. Ao mostrar/esconder campos por JS eu escrevi `display = sim ? 'flex' : 'none'` — e rótulo, campo e dica foram para a mesma linha, com o campo esticando e o ícone do calendário desalinhado junto. **Para mostrar de volta, use `''`**, que devolve o display da folha de estilo; nunca chute um valor. O teste antigo só perguntava `!== 'none'`, então passava — hoje a asserção é `display === 'block'` **e** rótulo acima do campo.
- **Campo estreito em `.form-row` precisa de teto.** `.form-row .form-field { flex:1 }` faz um campo sozinho esticar pelos 986px do card. Os campos do bloco de Repetição ganharam `max-width` próprio (420 · 250 · 210 · 200 · 190), e a linha ficou com `flex-wrap:wrap` para degradar sem estourar.
- **Ícone do calendário era 25% maior que a seta do dropdown, e 2px mais para dentro.** Medido: seta 12px com centro a **18px** da borda; calendário 15px com centro a **20px**. Dois campos que parecem do mesmo tipo tinham a afordância da direita em tamanho e distância diferentes — o usuário viu isso na tela antes de qualquer medição. Corrigido nas 8 telas com campo de data: botão de **24px** (centro a 18px, igual) e ícone de **13px** — o calendário é um desenho mais leve que a seta, então 13 fecha opticamente com 12.
- **Escolha entre N valores é dropdown, não caixa de texto.** *Dia do vencimento* era `input` livre: digitar "45" só era barrado no salvar, e era o único controle do bloco fora do padrão. Virou `.dropdown-select` de 1 a 31, igual ao *Dia da semana*, com a observação *(mês curto: último dia)* nos dias 29, 30 e 31 — a regra já existia no código e agora aparece **antes** de salvar.
- **Conferir entrega por tamanho não basta.** As trocas do ícone (`28px`→`24px`, `15px`→`13px`) têm exatamente o mesmo número de bytes: o arquivo muda e o tamanho não. Para saber se o que está na pasta do usuário é o que foi gerado, **comparar hash**, não tamanho.
- **Dropdown de painel fechado ainda está no DOM — e seu callback roda.** No **Acerto de Estoque**, trocar o *Tipo* com o painel fechado estourava `produtoLinha` nulo (`Cannot read properties of null (reading 'saldos')`). Um usuário não chega ali (o campo mora no painel), mas a função mentia sobre o que precisa para rodar. Defeito **anterior** à troca do componente — confirmado rodando na cópia antiga. Corrigido com guarda nas duas entradas (`atualizarOrigem`, `atualizarPrevia`). **Lição: callback de dropdown de painel tem de aguentar ser chamado antes de o painel abrir.**
- **Teste que clica em TODOS os dropdowns das 53 telas vale o que custa.** Foi ele que achou o item acima, e foi ele que provou que a troca do componente não quebrou nada. Dois contratos diferentes, os dois corretos: dropdown de **seleção** grava o `data-value` escolhido; **menu de ações** (*Ações*, *Mais ações*, `+ Adicionar nova categoria`) continua vazio e **repõe o rótulo**, para a mesma ação poder ser escolhida de novo. Asserção sobre o rótulo reprova o segundo tipo sem que haja bug — asserte o contrato, não a aparência.
- **Estado alcançável só pelo mock é estado que não existe.** A aba *canceladas* tinha contador, bolinha e uma conta — e nenhuma ação que cancelasse. Ao criar uma situação, criar no mesmo dia a ação que leva a ela.

## 14.3 Lições de 28/set/2026 (revisão completa da pasta)

A sessão que estava combinada para ser mecânica — colar ~20 linhas em 8 telas e apertar o script de auditoria. Nenhuma das duas coisas era o que parecia.

### O bloco de senha não estava em 8 telas: estava em 23. E o sintoma era o oposto do registrado.

O handoff de 23/set dizia que 8 telas tinham `confirmarAcao` sem `#confirmModal`, e que a consequência seria a ação **não acontecer** sem erro visível. Medido arquivo por arquivo:

- **São 23 telas**, não 8. Além das 8 sem marcação nenhuma, outras **15** têm `#confirmModal` no HTML — mas servindo de **modal de aviso** (`avisar()`, botão "Entendi"/"Fechar"), não de confirmação. Mesmo id, propósito diferente: `configuracoes` e as 7 `configuracoes-*`, `estoque-acerto`, `controle-estoques` (+detalhe), `inventario`, `reposicao`, `transferencia` (+nova).
- **O bloco é bem guardado** (`if (!btn) return`, `if (!raiz) return`) — nada quebra. O que havia era esta linha dentro de `confirmarAcao`:

```js
if (typeof abrirModalConfirmacao !== 'function') { executar(); return; }
```

**A ação executava direto — sem pedir senha e sem gravar no registro de atividades.** A trava não travava: ela sumia em silêncio. Num sistema onde exclusão exige senha e tudo é auditável, isso é pior que a tela travar.

- **E a correção proposta não resolveria:** colar a marcação não cria `abrirModalConfirmacao`, então `confirmarAcao` continuaria caindo no mesmo escape. O CSS do modal também faltava em 7 das 8.

**Correção aplicada, em duas camadas:**

1. **Falhar fechado, nas 52 telas que têm o bloco.** A linha virou uma que **não executa** quando a ação exige senha e não há modal, gritando no console com o nome da chave. Falha barulhenta é melhor que destrave calado — quem puser uma ação com trava numa tela sem modal vê o erro na hora, em vez de descobrir na auditoria que a senha nunca foi pedida.
2. **Modal completo nas 8 sem marcação nenhuma** — CSS (só as regras que faltavam em cada arquivo), marcação e a função canônica de 4 argumentos. Três delas são telas `-detalhe`, que vão ganhar Excluir/Inativar com certeza. As 15 de aviso ficam protegidas pela camada 1 e ganham o modal junto com a primeira ação com trava.

**Regra que fica: um helper compartilhado nunca degrada para "faz sem a proteção".** Se a proteção não pode ser aplicada, a ação não acontece.

### O teste achou a segunda bomba — e essa nenhuma leitura de código acharia

O envelope de senha (§12, *Confirmações por senha*) embrulha `abrirModalConfirmacao` para mostrar ou esconder o campo. Ele fazia:

```js
abrirModalConfirmacao = function () { …; return _abrirOriginal.apply(this, arguments); };
```

`function ()` sem parâmetros declarados tem **`.length === 0`**. E `confirmarAcao` escolhe como chamar o modal lendo exatamente esse `.length`:

```js
if (abrirModalConfirmacao.length >= 4) abrirModalConfirmacao(texto, 1, 'primary', executar);
else abrirModalConfirmacao(texto, 1, executar);
```

**O ramo de 4 argumentos era inalcançável.** Toda chamada ia para o de 3 — e nas telas cuja assinatura é de 4 ou 5 parâmetros, o callback caía na posição da **cor** e `aoConfirmar` chegava `undefined`: a ação não acontecia depois de confirmar. **25 telas** (16 de 4 args + 9 de 5) estavam nessa condição.

Ninguém viu porque as 8 telas que usam `confirmarAcao` hoje têm, por coincidência, a assinatura de 3. **Coincidência não é proteção.**

**Correção:** o envelope passou a **herdar a aridade do original** (`Object.defineProperty(_envelopeSenha, 'length', { value: _abrirOriginal.length })`), nas 52 telas. As três assinaturas voltaram a funcionar, sem reescrever nenhuma delas. Provado no navegador nas três.

**Lição: quando um despacho lê `.length`, todo envelope sobre a função tem de preservar a aridade** — senão o embrulho, que existia para não mudar nada, muda o caminho que o despacho escolhe. E a lição mais geral, terceira vez no projeto: **o teste de navegador achou o que a leitura do código não acharia**, porque o defeito estava na diferença entre o que o código diz e o que a linguagem faz.

### `auditoria.py`: de 33 arquivos "com problema" para 0 falhas reais

Os quatro falsos positivos conhecidos foram resolvidos **no script**, mais um quinto que apareceu no caminho (ids nascidos de `innerHTML`, em Metas). A tabela de antes/depois está no `_ferramentas/LEIA-ME.md`. Dois pontos que valem para qualquer mexida futura:

- **Nenhuma exceção foi escrita à mão.** Onde antes havia uma lista de dois ids cravados, agora há uma função que pergunta ao arquivo se a busca tem guarda. Exceção por lista envelhece; exceção por regra, não.
- **O aperto foi provado nos dois sentidos.** Injetando defeito de verdade — `select` nativo solto, `getElementById` sem guarda, checkbox órfão, `a href="#"` mudo, `div` desbalanceada — o script continua reprovando os cinco. **Auditoria mais quieta só vale se continuar mordendo**; quando mexer nela de novo, repetir essa prova.

O `pagina-molde-referencia.html` deixou de contar como falha e passou a aparecer como **EXCEÇÃO** nomeada — visível, fora da contagem. Silenciar teria escondido um preâmbulo duplicado de verdade se algum dia aparecer ali.

### O que a auditoria oficial disse, antes e depois

Idêntico: as **6 classes-gancho** do §12.2, e nada mais. As 53 telas passam limpas nas seções 1, 1B, 2, 4, 4B, 5 e 6 — incluindo contraste medido e estouro de largura a 1440px, nos dois temas. As **410 asserções** de `_ferramentas/` também passam, as 294 que já existiam mais as 116 novas.

## 14.4 Lições de 28/set/2026 (o "Mais ações" e a varredura de pendências)

### O contador das abas contava outra coisa que não a lista

Contas a Pagar anunciava **"em aberto 07"** com a tela mostrando **zero**. O contador somava `TITULOS` inteiro; a lista respeitava o filtro de período, que abre no **mês corrente**. O §7.2 já dizia, desde Ordens de Compra, que *"o contador ignora a aba selecionada e respeita todos os outros filtros"* — a tela nascida depois não seguiu.

**Ele só apareceu porque o tempo passou.** Em 23/set havia títulos em aberto dentro do mês; em 28/set os mesmos títulos tinham vencido e viraram *atrasados*. O número do contador vinha do ano inteiro, o da lista vinha do mês. **Contador que discorda da lista é pior que contador nenhum**, e este mentia em silêncio.

Corrigido extraindo `listaSemAba()` — a base com todos os filtros **menos** a aba —, que é sobre o que os contadores contam. Conferido nas cinco abas: contador e lista batem.

E ficou uma pendência de dado, não de código: **mock com data fixa envelhece** (§13).

### A auditoria oficial reprovou o meu próprio código, e estava certa

Para o modo leitura eu escrevi `document.querySelectorAll('.theme-seg')` — exatamente o seletor que já trocou o tema da tela ao clicar no toggle de tipo de pessoa (§5 e §14), e que a seção 4B reprova desde então. Meu código pulava o `.theme-picker`, então não tinha o bug; **mas o seletor é a assinatura do bug**, e uma auditoria que aceita a assinatura para de pegar a próxima ocorrência.

Reescrevi para selecionar pelas classes dos toggles que sei rotular, montadas do próprio mapa de rótulos. **A regra do §14 valeu para mim: quando a auditoria acusa algo que não é bug, a saída é escrever diferente, não ensinar a auditoria a ignorar.**

### Modo leitura: o valor é DERIVADO do campo, não uma segunda marcação

São **174 campos** nas cinco telas de detalhe antigas. Escrever um `.campo-leitura` por campo no HTML seria duplicar o valor em dois lugares — e texto duplicado diverge do campo na primeira edição. O bloco compartilhado **lê o próprio campo** (`input`, `textarea`, `.dropdown-select-label`, senha como `••••••••`, checkbox como Sim/Não) e cria o texto de leitura na hora.

**O print pegou três coisas que nenhum teste pegaria:** o botão *Editar* com o rótulo embaixo do ícone (faltava `.btn-secundario-topo` nas cinco telas — a regra existia só nas de Finanças), o toggle *Pessoa Física/Jurídica* ainda clicável em leitura (não é `.form-field`, então ficou fora da regra), e o rodapé *Cancelar/Salvar* visível numa tela sem nada para salvar.

### Teste que segue o código, não o contrário

Converter as seis classes-gancho para `data-*` quebrou três testes, que ainda procuravam `.tit-check`, `.mov-check` e `.cat-check`. Mover a exclusão para dentro do "Mais ações" quebrou outros dois, que clicavam direto no link. **Nos dois casos o certo foi atualizar o teste** — ele descreve o sistema, não o congela. O que **não** se faz é afrouxar a asserção para ela passar: `teste_lanc.py` deixou de conferir que o *link* some e passou a conferir que o **menu** some, que é a regra nova, com a mesma força da antiga.

E uma lição de ferramenta: `teste_confirma_senha.py` tinha a lista das telas escrita à mão. Virou descoberta automática — **lista escrita à mão envelhece, e foi assim que "8 telas" virou 23 sem ninguém perceber**.

### O rename atropelou o bloco compartilhado

Ao dar ids próprios ao modal de aviso, a substituição pegou `btnConfirmModalConfirmar` e `confirmModalTexto` **dentro do bloco de senha compartilhado** — a trava passou a ouvir um botão que não era mais o de confirmar, e a senha vazia deixou de travar em 15 telas. Passou na auditoria (nada quebrou) e só apareceu no teste de navegador.

**Lição: rename global em arquivo que hospeda bloco compartilhado precisa de fronteira.** O bloco é código de fora; o que a tela renomeia não é dela para renomear.

## 14.5 Lições de 29/set/2026 (clonar, recibo e uma deleção não anunciada)

### A âncora de inserção errou o escopo pela segunda vez

O bloco do clone e do recibo entrou antes de `// ===== MENU "MAIS AÇÕES"`, que nessa tela é o **primeiro** comentário do script. Lá em cima, `let conta` ainda está na zona morta temporal: `atualizarItemRecibo()` leu `conta`, estourou `Cannot access 'conta' before initialization` e **derrubou o script inteiro**. A tela abria, o menu aparecia (é marcação estática) e `porExtenso` respondia no console (declaração de função é içada) — três sinais de vida numa página morta.

É a mesma família do `const PARAM` que caiu dentro de uma função em 18/set. **Regra reforçada: âncora de inserção não é só única, ela tem de estar DEPOIS de tudo que o bloco lê.** Bloco que usa estado da tela vai para o fim do script, junto do modo leitura — nunca para o topo.

E o que pegou não foi a auditoria estática (sintaxe correta), foi o teste de navegador.

### Uma deleção correta que entrou sem ser anunciada

Os marcadores de Ordens de Compra — CSS, coluna, mock e render — foram removidos numa das rodadas de 28/set **sem aparecer em nenhum relato**. O resultado está certo (é o que o §12.1 manda) e a remoção está limpa, conferida linha a linha contra a versão original: zero referências órfãs, as duas telas rodam sem erro.

**Mas entrega correta e não anunciada é o mesmo risco de sempre com outra roupa:** em 18/set o chat dizia "entregue" e o arquivo não tinha aterrissado; aqui o arquivo mudou e o chat não disse. As duas quebram a mesma coisa — a correspondência entre o que foi dito e o que existe no disco. **Toda varredura em lote lista o que tocou, mesmo o que ninguém pediu para olhar.**

## 14.6 Lições de 29/set/2026 (noite — a limpeza para voltar a construir)

### Aviso que mente passa em toda auditoria

A seção 5 da auditoria oficial diz *"todos os botões respondem"* — e respondiam: **19 botões em 10 telas do Estoque** abriam um aviso dizendo que a tela de destino *"é a próxima a ser construída"* ou que *"a navegação só funciona no sistema de produção"*, com a tela existindo havia semanas. As listagens de Ordens de Compra e de Entrada de Notas **não tinham caminho nenhum** para o próprio detalhe. As telas do Estoque nasceram entre 14 e 16/set; a navegação real chegou em 22/set, e a varredura daquele dia cobriu **o menu, não os botões de dentro das telas**.

**Regra: quando um pré-requisito passa a existir, procurar todo texto que dependia da ausência dele.** A mensagem da Conferência (29/set, tarde) era o primeiro caso; a pergunta *"em quantos arquivos isso existe?"* não foi feita naquela hora e deveria. `teste_becos.py` reprova as frases e confere os destinos.

### A senha armada no ramo errado

Em 18/set a exclusão passou a pedir senha, e a varredura pôs `armarSenhaModal()` antes do **primeiro** `abrirModalConfirmacao` de cada handler de exclusão em massa. Em três telas — **Ordens de Compra, Depósitos e Endereços** — o primeiro modal era o **aviso** de que nada podia ser excluído. Resultado invertido: o aviso pedia senha para fechar, e **a exclusão de verdade acontecia sem senha**. 687 asserções do `teste_confirma_senha.py` não pegaram porque exercitavam o detalhe, não a exclusão em massa com guarda.

**Regra: a senha é armada na linha imediatamente anterior ao modal que EXECUTA — nunca no topo do handler.** Handler com ramo de guarda tem dois modais, e só um deles faz alguma coisa.

### Recurso novo num ponto por onde passam várias portas

O modo leitura (28/set) entrou no carregamento do detalhe — e o detalhe é aberto por **Incluir**, por **Editar cadastro completo** e pela consulta. As três portas passaram a cair em leitura, e *"Incluir cliente"* abria um cliente existente sem poder editar. **Regra: mudança no carregamento de uma tela se testa por cada porta de entrada**, não pela tela aberta direto.

### Documento que diz "em aberto" para o que foi decidido

O roadmap tinha **17 perguntas marcadas "decidir antes de construir"** já respondidas pelo §12 — que ficava logo abaixo, no mesmo arquivo —, **9 cabeçalhos com ⏳** de coisas prontas ou aprovadas, e o *Estado atual* contava **31 telas quando eram 52**. Cada decisão foi escrita num lugar novo sem voltar à pergunta original. **Regra: ao decidir, anotar a pergunta de origem com a resposta e onde ela está** (`→ ✅ Resolvido (data): …`), senão o documento continua perguntando o que já foi respondido — e o prompt do sistema de produção herda a dúvida.

## 14.7 O selo de verificação (30/set/2026)

A verificação completa chegou a 20 minutos, e **teste caro é teste que alguém começa a pular**. A saída não foi pular por bom senso — foi tornar o pulo mecânico e auditável: `_ferramentas/selo.py` guarda o SHA-256 de cada arquivo que cada suíte cobre, e **só pula a suíte quando nada que ela cobre mudou**. Quem muda uma tela não escolhe o que retestar; o selo escolhe, e erra para o lado de rodar demais.

Três decisões que valem além desta ferramenta:

- **Cobertura se deduz do código, nunca de uma lista escrita à mão.** O `selo.py` lê os `pagina-*.html` citados por cada suíte, ou "a pasta toda" quando ela faz `glob`. Lista manual é a mesma armadilha do `teste_confirma_senha` com telas cravadas, que escondeu 15 telas com problema.
- **Cobertura declarada tem de ser provada por observação.** Cada suíte rodou com o `Page.goto` instrumentado, e nenhuma abriu tela fora da sua cobertura. Cobrir demais custa uma rodada; cobrir de menos é selo que mente — e selo que mente é pior que não ter selo.
- **O selo segue também as ferramentas**, não só as telas: mudou a suíte, o `auditoria.py`, a auditoria oficial da skill ou o filtro `alvos.py`, tudo que depende delas volta a rodar.

### A segunda mordida do calendário

A primeira rodada do selo reprovou o `teste_caixa.py`, verde no dia anterior: ele fecha o período financeiro **em hoje** e depois exige que o calendário da transferência tenha dias livres. Em 30/set — último dia do mês — o mês inteiro estava fechado e sobraram zero dias. **O teste passava 29 dias por mês e reprovava no trigésimo.** A tela estava certa: com o período fechado até hoje, quem transfere avança um mês, e o rodapé do calendário diz o motivo. O teste é que supunha um calendário que sempre sobra dia. Corrigido avançando o mês quando o corrente está todo fechado.

É a mesma família do *"o mock envelhece"* (§13) e a segunda vez que ela aparece: **o teste não mudou, o calendário mudou.** Toda asserção que depende de "hoje" precisa valer no dia 1, no dia 28 e no último dia do mês.

## 14.8 Lições de 30/set/2026 (Pedidos de Venda — o que clonar cobra)

**1. Depois de clonar uma tela, procure todo identificador que cite o domínio da tela velha.** As duas telas de Pedidos de Venda nasceram de `pagina-estoque-ordens-compra*.html`. Três defeitos herdados sobreviveram à leitura e caíram na busca por nome: `dfDataCompra`/`dfDataPrevista` ainda ligados no lugar de `dfDataVenda`/`dfPrevisto`; `inputListaPreco` num campo que hoje é "Prazo médio de entrega"; e um **segundo `bindMenuAcoes` no mesmo `#menuMaisAcoes`** — o bug conhecido de "o dropdown abre e se fecha no mesmo clique". Nenhum dos três aparece lendo o arquivo de cima a baixo; os três aparecem em dez segundos de `grep`.

**2. `Set` não é array-like.** `[].slice.call(umSet)` devolve `[]`, sem erro e sem aviso. O código lê certo e roda errado — quatro ocorrências, achadas no navegador. **Execução não é conferência do que você já leu: é a única leitura que conta.**

**3. Erro que volta não pede correção, pede verificação.** Tag escrita dentro de texto de modal (`confirmModalTexto` usa `textContent`, então `<b>` vira `</b>` na tela) foi corrigida à mão em 29/set e **voltou em 30/set**. Virou a **checagem 10** do `auditoria.py`, provada nos dois sentidos. Correção à mão não impede a terceira vez.

**4. Nome montado com `+` é nome que a auditoria não vê.** `'bs-' + situacao` passa por qualquer busca por classe. Convertido para mapa explícito (`SIT_BADGE`), com todos os nomes **escritos**. A alternativa — ensinar a auditoria a entender concatenação — é a errada: **escrever diferente, não ensinar a auditoria a ignorar.**

**5. Listagem e página nascem no mesmo passo.** Listagem sozinha teria *Incluir pedido* e *abrir pedido* sem destino, que é o beco que a varredura de 29/set eliminou. **Tela que cria botão sem destino não está pronta, está adiada.**

## 14.9 Lições de 02/out/2026 (Pedidos de Venda — o que o usuário viu e o teste não)

**1. `overflow:hidden` no pai e painel flutuante no filho não convivem.** O menu *mais* das abas abria no DOM, respondia a `click()` do Playwright e **o usuário não via nada** — recortado pelo `overflow:hidden` que existia para as abas não quebrarem a linha. O recorte passou para uma **trilha interna**; o dropdown ficou fora dela. **Regra: elemento que abre painel flutuante nunca mora dentro da caixa que recorta.**

**2. Abrir não é aparecer — e `querySelector` não sabe a diferença.** O teste afirmava `classList.contains('open')` e passava em cima do bug. A asserção certa é a do dedo do usuário: `document.elementFromPoint` no centro do item, conferindo se o alvo está dentro dele. Posta no `teste_dropdown_todas.py`, que roda nas 55 telas, **a mesma checagem acusou mais dois casos no mesmo minuto** — os dois falsos positivos (dropdown dentro de painel lateral fechado), o que obrigou a segunda metade da regra: **só cobre que o menu apareça quando o próprio botão estiver alcançável**.

**3. Dois listeners no mesmo elemento, pela terceira vez.** `linkUltimasVendas` ganhou o painel novo e **manteve o `window.location.href` antigo**: o painel abria e a página navegava embora. É o mesmo defeito do `bindMenuAcoes` duplicado (§14.8). **Ao dar comportamento novo a um elemento que já tinha um, procurar o listener velho é parte da tarefa, não zelo extra.**

**4. Um `avisar` por motivo faz o segundo apagar o primeiro.** Pedido estourando saldo **e** limite de crédito mostrava só o limite: o usuário consertaria a coisa errada e bateria na outra trava em seguida. Os motivos passaram a ser **acumulados e numerados numa mensagem só**. **Quando duas validações podem valer juntas, elas se somam, nunca se sobrescrevem.**

**5. Ferramenta que julga precisa responder em toda chamada.** O `auditoria.py` só imprimia o veredito com 2+ arquivos; numa rodada de um arquivo só, o `selo.py` lia a ausência da linha como reprovação — **auditoria limpa, selo vermelho**. Agora o resumo sai sempre e o **código de saída** é o contrato (`sys.exit(1)` com falha), com a linha de texto como segunda confirmação.

**6. Aviso que descreve o futuro é beco com outro nome.** Quatro itens do menu *Mais ações* só abriam um aviso explicando o que aconteceria um dia. Três viraram ação de verdade (funil, clonar, alterar situação) e um virou painel (ver conta a receber). **Sobraram dois, e os dois são sobre módulo que não existe** — fiscal e relatórios —, não sobre tela construída e não ligada. Essa é a diferença que decide se o aviso é honesto.

## 14.10 Quando o componente não cabe, troque o componente (02/out/2026)

A linha de abas contadoras de Pedidos de Venda não cabia a 1440px: **as 11 abas pediam 1.537px num espaço de 1.024**. A primeira saída foi o menu *mais* — que abriu escondido (§14.9) e, consertado, continuou estranho para o usuário.

**A medição é que decidiu.** Tirando a devolução sobravam 10 abas pedindo 1.395px; sem a bolinha colorida, 1.269px; apertando padding e fonte, 1.100px; encolhendo o contador, 1.050px — contra 1.024 disponíveis. **Dava para espremer com 20px de folga**, e qualquer rótulo novo ou contador de 3 dígitos quebraria de novo.

**Decisão: situação virou o terceiro filtro suspenso**, ao lado de Loja e Vendedor. O que a aba dava de graça — o número por situação — foi junto, **dentro da lista**, e é remontado a cada abertura porque depende dos outros filtros. Contador congelado mente.

**A regra que fica: antes de espremer um componente para caber, meça o quanto falta.** Se a folga depender de encurtar rótulo, o componente está errado para aquele lugar — e o conserto é trocar o componente, não encolher o conteúdo. Dois detalhes que vieram de regras já escritas e quase passaram: o teto de `max-height:240px` do dropdown compartilhado cortava 3 das 10 opções (ganhou teto próprio **escopado**, sem mexer no compartilhado), e o bind próprio deste filtro nasceu **sem medir o espaço antes de abrir** — regra não-negociável do design system, que vale para dropdown com bind próprio igual aos outros.

## 14.11 Devolução não é situação de pedido de venda (02/out/2026)

Devolução era a 10ª situação do funil. **Saiu.** Ela é **documento próprio**, do módulo de Devoluções, e aponta para o pedido — o pedido devolvido **mantém a situação que tem**.

O motivo não é arrumação: marcar o pedido como *devolução* **apagaria a venda que de fato aconteceu**. O faturamento aconteceu, a comissão foi liberada, a baixa física saiu — nada disso deixa de ser verdade porque a mercadoria voltou. Situação é o estado do pedido; devolução é um fato novo, com data, motivo e itens próprios, que pode inclusive ser parcial.

Sai da listagem, do funil e do painel *Alterar situação*. As frases que apontam para a devolução como caminho (cancelar pedido expedido, excluir pedido expedido, voltar de *Enviado*) **continuam**, porque continuam verdadeiras — agora apontando para o módulo, não para uma situação.

## 14.12 Lições de 02/out/2026 (Contas a Receber — o preço de clonar o oposto)

Contas a Receber nasceu de Contas a Pagar. São a mesma forma — título, vencimento, baixa, escopo em grupo — mas **sentido contrário**, e é aí que o clone cobra.

**1. Renomear em bloco acerta o nome e erra o sentido.** `pagar → receber` deixou o código compilando e os lançamentos invertidos: a baixa continuava escrevendo **saída** no Caixa, e o estorno, **entrada**. Nenhuma auditoria pega isso — tag balanceada, JS válido, id existente. **Depois de clonar uma tela de sentido oposto, a lista do que conferir não é de nomes, é de direções**: o que entra, o que sai, o que soma, o que subtrai. Virou seção própria do teste.

**2. O rename em bloco também inventa palavra.** `fornecedores → clientes` produziu `pagina-cadastros-clientees.html` — link para arquivo que não existe, em duas telas. **A auditoria oficial pegou**, na seção de links quebrados. Também atropelou nomes **compartilhados**: os grupos de categoria viraram *"Custos e clientees"*, *"Receitas fixas"*, e o item de menu *Contas a Pagar* virou um segundo *Contas a Receber*. **Nome compartilhado não é texto da tela: ele tem de voltar exatamente ao que as outras 56 dizem**, e a forma segura de restaurar é copiar do arquivo canônico, não reescrever à mão.

**3. O controle tem de dizer o estado em que a tela abriu.** Clonar revelou um defeito que estava em Contas a Pagar desde 23/set: a lista abria filtrada pelo mês corrente e a pill dizia *"Sem filtro de período"*. A tela escondia linhas e o controle jurava que não escondia nenhuma. Corrigido **nas duas**, com a pill sincronizada na carga. **Quem não confere o resultado contra o filtro nunca descobre.**

**4. Recursão nasce de uma função que desenha chamando a que calcula.** `renderParcelas()` chamava `recalcularTotais()`, que chamava `renderParcelas()`. **Quem calcula passa o número; quem desenha recebe** — a prévia nunca recalcula por conta própria.

**5. Trava que só aparece no fim é trabalho jogado fora.** O bloqueio por conta em atraso aparecia só ao clicar em *Salvar*, depois de o pedido inteiro estar montado. Passou a avisar **na abertura**, no campo do cliente, dizendo quanto, há quantos dias e que o pedido não vai salvar. **Erro de validação é mensagem de fim; impedimento conhecido é aviso de começo.**

**6. Teste que prova "não acontece" precisa trocar de alvo quando o alvo muda.** O `teste_menu` provava que item sem tela fica inerte usando *Contas a Receber* — que acabou de ganhar tela. Apontado para *Comissões Afiliados*, que de fato ainda não existe. **Teste de negativa envelhece junto com o sistema**, e sem trocar o alvo ele vira teste de nada.

**7. O mock envelhece — terceira mordida.** O `teste_integra` escolhia o primeiro título em aberto do mock, mas a listagem abre filtrada pelo mês: em 30/set o alvo caía dentro, em 02/out não. Passou a escolher **entre as linhas que estão na tela**. As três mordidas foram a mesma: o teste conhecia o dado, não a tela.

## 14.13 Três padrões que estavam soltos — travados em 02/out/2026

O usuário notou o mesmo elemento mudando de lugar conforme a tela. Os três viraram regra escrita **e asserção que varre a pasta inteira**, não lista de telas à mão.

**1. "Mais ações" é SEMPRE o último botão do cabeçalho.** A ordem canônica é **ações azuis → Editar → Mais ações**. Dez telas já faziam assim; *Caixa e Bancos* e as duas páginas de conta tinham o dropdown em primeiro. **Botão que muda de posição conforme a tela obriga o usuário a procurar o que ele já sabe onde fica.**

**2. Filtros ACIMA, situação com as bolinhas ABAIXO.** As telas de Estoque já faziam assim; Contas a Pagar e Contas a Receber estavam invertidas. A ordem é a da leitura: primeiro se restringe o conjunto (busca, período, categoria), depois se escolhe o recorte dentro dele.

**3. Nenhum item de menu aparece duas vezes no mesmo flyout.** Este não é estética, é defeito: o rename em bloco de 02/out transformou *Contas a Pagar* num segundo *Contas a Receber*, e **um módulo inteiro sumiu do menu** — com os dois itens apontando para arquivo existente, nenhuma checagem de link quebrado acusava. Virou a **checagem 11** do `auditoria.py`, e ela achou na hora um segundo caso que havia passado (*Clientes* duplicado, no lugar de *Fornecedores*).

**O padrão das três:** cada uma nasceu de o usuário ver a mesma coisa em dois lugares diferentes. **Inconsistência não aparece lendo uma tela — só comparando duas**, e é por isso que as três asserções varrem a pasta em vez de checar o arquivo da vez.

## 15. Arquivos de referência

- **Sidebar + navegação:** incorporada em todos os arquivos abaixo — não existe mais um arquivo isolado só de sidebar.
- **Página mais completa pra estudar o padrão de Detalhe:** `pagina-cadastros-produtos-detalhe.html` (mais rica: abas, cascata, variações, autocomplete, diagrama dinâmico).
- **Página mais completa pra estudar o padrão de Listagem + seleção em massa:** `pagina-cadastros-fornecedores.html` ou `pagina-cadastros-produtos.html`.
- **Página mais completa pra estudar diagrama dinâmico por Tipo com implementação real (não só preview):** `pagina-cadastros-embalagens.html`.
- **Página mais completa pra estudar o dropdown multi-seleção (checkboxes dentro do menu, recolhimento automático):** `pagina-cadastros-marcas.html` (`#dropdownLojasMarca`, ver §9.1).
- **Página mais completa pra estudar exclusão suave (soft-delete), vínculo opcional a outro cadastro ("autônomo"), o painel mocado de criação de senha de acesso e o botão de opção (rádio) customizado:** `pagina-cadastros-vendedores.html` + `-detalhe.html` (ver §8.1, §9.1 e §11).
- **Todos os arquivos `.html`** vivem juntos e devem ser lidos como um conjunto — qualquer revisão de consistência precisa comparar os componentes compartilhados (checkbox, modal, drawer, dropdown) entre eles, já que cada um foi copiado de um anterior e pequenas divergências podem ter passado despercebidas (já aconteceu mais de uma vez: CSS de modal/drawer inteiro faltando em Produtos-detalhe por ter sido copiado de um arquivo que nunca teve esses componentes; o preâmbulo HTML duplicado registrado em §14; o wrapper `.floating-card` errado em Embalagens; e o desalinhamento de Categorias, também em §14).

## 14.14 Divergência não é acerto — ela vira um pedido de acerto (02/out/2026)

Na Conferência de Saída, o conferente digita a quantidade que está na caixa. Quando o número é menor que o do pedido, existe a tentação de baixar o estoque na hora: "se o item não estava lá, o saldo estava errado".

**Está errado, e o motivo é que a divergência tem três causas que são indistinguíveis no momento da contagem:**

1. o saldo estava errado mesmo — o item não existe no galpão;
2. o separador coletou errado — levou a quantidade ou a referência errada, e o item continua na prateleira;
3. o conferente contou errado — o item está na caixa.

Só a primeira é acerto de estoque. Nas outras duas **o saldo estava correto** e a baixa automática o corrompe: o sistema erra o estoque para consertar um erro que não era do estoque.

**O argumento que fecha:** os motivos de saída do `pagina-estoque-acerto.html` carregam `fiscal: 'nfe'` — `perda`, `extravio`, `quebra`, `furto`. Baixa por perda **exige nota fiscal de saída**. Um acerto automático não produz só um saldo errado: produz uma **obrigação fiscal** nascida da contagem apressada de uma pessoa. É exatamente o que a Conferência de Entrada se recusa a fazer quando não deixa o conferente decidir sozinho.

### A regra

> **Divergência registra, libera e espera. Estoque só se move depois que alguém que pode ir até a prateleira diz qual foi a causa.**

A Conferência de Saída cria um **acerto na situação `aguardando reconferência`** — não um acerto efetivado. O pedido do cliente **não trava**: é ajustado, o valor recalculado, e segue. Quem fecha a reconferência **não responde sim ou não — responde qual das três causas**, e só uma delas movimenta:

| causa apontada na reconferência | estoque | registro |
|---|---|---|
| item não estava na prateleira | **gera o acerto de saída**, com motivo e aviso fiscal | ligado à divergência de origem |
| item estava lá — erro de separação | não se move | erro atribuído à separação |
| item estava lá — erro de contagem | não se move | erro atribuído à conferência |

**Fechar tudo como "acerto" apaga a informação mais útil que a divergência produz:** qual das três acontece mais. As três têm donos diferentes e correções diferentes.

### O corolário no pedido do cliente

Abater o item faltante e recalcular o valor é só cobrar o que foi entregue — isso o sistema faz sozinho. **O que o sistema não pode fazer sozinho é escolher a compensação.** CDC art. 35: na entrega parcial, quem escolhe entre **restituição**, **crédito** ou **reenvio do item** é o consumidor. O pedido guarda a escolha como pendência, com restituição sugerida quando já estava pago. Crédito que o cliente não pediu é saldo preso na nossa mão — e um passivo que ninguém lançou.

> **Revisto em 09/out/2026.** A divergência deixou de só esperar: a unidade que faltou fica **bloqueada**, e a
> reconferência, que não tinha tela, é feita em Estoque → Itens Bloqueados. Liberar uma falta pede a causa; a
> causa "não estava no endereço" é a baixa. Ver §14.51.

## 14.15 Riscado quer dizer RESPONDIDO, não "deu tudo certo" (05/out/2026)

Na ficha de Separação, item coletado por inteiro ficava riscado e item com falta registrada ficava **com a mesma cara de item intocado**. O operador respondia a falta, olhava a lista e não via diferença nenhuma — e varria tudo de novo procurando o que já tinha resolvido.

O erro foi de conceito, não de CSS: eu usei um sinal só (`.coletado`) para duas informações diferentes.

> **Um sinal por informação.** "Eu respondi este item" e "veio tudo" são duas perguntas, e a linha precisa responder as duas sem que uma apague a outra.

| estado | marca | linha |
|---|---|---|
| sem resposta | vazia | normal |
| coletado por inteiro | cheia | riscada |
| respondido com falta | **intermediária** | riscada + borda de alerta + selo |

### O terceiro estado é do COMPONENTE

A marca intermediária (`:indeterminate`) entrou no `.item-checkbox` das **59 telas**, não só na que precisava. Marca cheia diria *"coletei tudo"* e marca vazia diria *"nem olhei"* — as duas mentem sobre um item incompleto de propósito, e qualquer tela de conferência vai cair no mesmo caso. **Componente que existe diferente num arquivo é o começo de dois componentes.**

Vale a distinção que §13 já fazia: propagar **correção de componente** é obrigação; propagar **estado novo de componente** é escolha, e se justifica quando a próxima tela já é conhecida — aqui, a Conferência de Saída.

## 14.16 O que o Olist faz na saída, conferido na fonte (05/out/2026)

Antes de desenhar a Conferência de Saída, fomos ler a documentação em vez de deduzir dos prints:

- **Separação** mostra produto, SKU, GTIN, quantidade, lote, destino, forma de envio e número de série; o operador marca *separado* ou *lido*. Ao concluir, o pedido vai para **separado**, e a fase seguinte é **embalagem** — "os itens são verificados e embalados". Nada documentado sobre item em falta.
- **Expedição** tem inclusão → dados logísticos → **conferência de pedidos** (etapa própria, por agrupamento, manual ou bipagem) → conclusão → etiquetas → marcar enviados.
- A **NF-e já existe** antes da expedição: *"DANFE emitida"* é pré-requisito, não resultado.

**Duas consequências:**

1. **O Olist confere DUAS vezes** — na embalagem (por pedido) e na expedição (por romaneio). Nossa barganha de 02/out previa uma só, e estava errada. Mas repetir a mesma conferência é desperdício: as perguntas são diferentes. *"Os itens certos estão nesta caixa?"* com a caixa aberta; *"os volumes deste romaneio estão no caminhão, cada um na transportadora certa?"* com a caixa lacrada. A segunda custa dois segundos por caixa e pega o erro mais caro do galpão — o pacote que foi para a transportadora errada.
2. **A nota continua saindo na Conferência de Saída, ao contrário do Olist.** Emitir antes de conferir é emitir nota de uma caixa que pode estar faltando item, e nota errada vira carta de correção ou cancelamento. O custo honesto: pedido de marketplace que já chega com nota emitida pela integração vai **importar** a nota em vez de emitir — caso do módulo fiscal, não desta tela.

## 14.17 Ação dentro de linha é botão, e o botão diz o que faz AGORA (05/out/2026)

O usuário abriu a ficha de Separação e não viu um botão onde havia um. Declarar falta era **texto laranja sem borda** — a mesma cor que o sistema usa para alerta, no meio de uma linha cheia de texto. Ele leu como rótulo, não como controle.

> **Ação que mora dentro de uma linha é botão, com borda.** Texto colorido é informação; só borda e fundo dizem "clique aqui".

E o controle veio de `.pill-btn-sm`, que **já existia** no sistema. Classe nova para um botão pequeno teria sido o terceiro tamanho de botão sem motivo.

### O rótulo acompanha a função

O mesmo botão faz duas coisas diferentes conforme o estado da linha, e o rótulo tem que dizer qual delas está disponível **agora**:

| estado | rótulo | tinta |
|---|---|---|
| sem falta | *não achei tudo* | neutra |
| com falta registrada | *corrigir separação* | alerta |

## 14.18 O número grande responde à pergunta da ETAPA SEGUINTE (05/out/2026)

A coluna de quantidade mostrava **6** em corpo grande e *"coletou 5"* em miúdo. Está invertido: quem lê essa linha depois — o conferente de saída, o cliente no histórico — pergunta **"quantas peças estão na caixa?"**, não "quantas o pedido pediu".

> **O número em corpo grande é o número real.** O planejado vira linha de apoio.

Vale para qualquer tela onde o executado difere do previsto: conferência, inventário, recebimento parcial.

## 14.19 Linha é grid próprio — coluna `auto` desalinha a lista inteira (05/out/2026)

Cada `.sep-item` é um grid independente. Com a última coluna em `auto`, a linha que ganhou um selo extra ficou **78px fora** do alinhamento das outras, e a lista passou a serrilhar na vertical.

> **Numa lista de linhas-grid, toda coluna tem largura fixa, menos uma.** `auto` só funciona quando todas as linhas têm exatamente o mesmo conteúdo — e é justamente o estado diferente que faz a lista existir.

Medir resolve o que olhar não resolve: a asserção compara o `left` da mesma coluna em todas as linhas e exige um valor só.

## 14.20 Trabalho longo precisa de "guardar", e guardar não é devolver (05/out/2026)

A ficha de Separação só oferecia **concluir**. Pedido de 40 itens não cabe num turno, e galpão tem intervalo, troca de turno e prioridade que fura a fila. Sem um terceiro caminho, a escolha do operador era **concluir mentindo** ou **devolver para a fila e jogar fora o que já tinha andado**.

São duas ações diferentes e precisam continuar diferentes:

| ação | o pedido | as marcas |
|---|---|---|
| **Guardar e continuar depois** | continua em separação, **no nome dele** | ficam |
| **Devolver para a fila** | volta para a fila de todos | somem |

A confirmação de guardar diz as duas coisas, e aponta qual usar quando a intenção for a outra — porque o nome dos dois botões, sozinho, não distingue.

## 14.21 O catálogo de ações é UMA lista — e entra nas telas que o LEEM (05/out/2026)

Em 02/out o módulo de Separação nasceu com as quatro ações no catálogo — **só nas duas telas dele**. As telas que *leem* o catálogo (Configurações → Confirmações por senha, Vendedores → Acesso e Permissões, Registro de Atividades) não souberam delas.

O efeito é pior que uma célula faltando: a ação **acontecia e gravava no registro**, e não havia onde ligar a trava. A matriz dizia que aquilo não existia.

> A regra de §catálogo já dizia *"a trava nasce com a tela"*. Faltava a metade de trás: **o módulo novo entra no catálogo de quem usa E de quem lê.**

Virou asserção: a suíte do módulo abre as três telas consumidoras e exige que cada chave esteja lá. Lista escrita à mão num arquivo só é a forma mais silenciosa de uma permissão sumir.

## 14.22 Contagem cega na SAÍDA é mais necessária que na entrada (05/out/2026)

Na entrada, quem confere não sabe o que deveria vir. Na saída, ele tem a lista do pedido na mão — e é justamente por isso que a cega importa mais aqui: **a etapa existe para pegar erro da separação**, e com o número à vista a pessoa digita o número em vez de contar. A conferência passaria a confirmar o erro em vez de achá-lo.

A bipagem é o que tira o atrito: **cada leitura soma uma peça**, e a contagem se constrói sem ninguém digitar nada.

### Três estados, e um deles é uma decisão

| estado | o que a tela mostra |
|---|---|
| não contado | esperado **oculto**, divergência `—` |
| contado e bateu | esperado **aparece**, `confere` |
| contado e não bateu | esperado **continua oculto**, e a tela diz só **"divergência"** |

> **O tamanho da diferença é exatamente o que não pode vazar antes da decisão.** Com ele na tela, ajustar a contagem até o sistema calar é trivial.

O conferente escolhe **recontar** ou **banco a contagem**. Só depois de bancar o número aparece e o motivo vira obrigatório. E **mexer na contagem depois de bancar reabre a decisão** — senão bastaria bancar uma vez e corrigir o número em seguida.

Os motivos mudam com o **sinal** da divergência: faltando, só os motivos de falta; sobrando, só os de sobra. Lista única com motivos impossíveis é lista que ensina a escolher qualquer um.

### Quem é conferido não desliga o próprio controle

A bancada **não tem interruptor de contagem cega**, e isso é decisão, não esquecimento. A Conferência de Entrada tem — e está certa em ter, porque lá o erro que a cega pega é do **fornecedor**, um terceiro.

> **Na saída, o erro que a cega pega é do colega que separou — e, no limite, do próprio conferente.** Dar o interruptor a quem está sendo conferido é entregar a chave do controle para o controlado.

O parâmetro continua existindo e vive só em **Configurações → Conferência**, que é tela de outro perfil. Lá, desligar **pede senha** e **entra no registro de atividades** — é a única mudança daquela tela que *apaga um controle* em vez de ajustar um padrão. A bancada, em troca, **diz em que estado está e onde isso se muda**: controle invisível vira suporte, não disciplina.

## 14.23 A nota sai pelo que está na caixa (05/out/2026)

> **O que vai na caixa é o que vai na nota.** Cobrar o que não foi entregue é o erro que vira devolução, carta de correção e cliente ligando.

A conferência **nunca trava**: divergente, o pedido é ajustado, o valor recalculado, e a diferença vira divergência aguardando reconferência de estoque (§14.14) — nenhum saldo é baixado ali.

**Os itens não mostram preço; o resumo mostra.** Quem conta não precisa de preço — é a mesma regra da Separação. Mas é esta tela que emite a nota, e quem fecha precisa ver o que está prestes a faturar. A exceção é consciente e tem um lugar só: o rodapé.

**A compensação é escolha do cliente, não do sistema.** CDC art. 35: na entrega parcial ele escolhe entre restituição, crédito e reenvio. A tela **trava o fechamento** até alguém registrar o que ele escolheu, e sugere restituir quando o pedido já está pago — crédito que o cliente não pediu é dinheiro dele preso na nossa mão.

## 14.24 Função içada não alcança o `const` que ela usa (05/out/2026)

A ficha chamava `avisar(...)` no fim do próprio bloco, antes do bloco compartilhado do modal. `avisar` é declaração de função e sobe; `confirmModal` e `acaoConfirmada` são `const`/`let` e ficam na **zona morta temporal** até a linha delas executar.

O sintoma foi cruel e silencioso: a **primeira** linha da função escrevia o texto do aviso, e a **segunda** estourava. A folha nunca abria, mas o texto estava lá — qualquer teste que lesse `#confirmModalTexto` passaria.

> **Chamada de arranque vai depois do bloco que ela usa.** Içamento vale para a função, não para as constantes que ela fecha.

É o mesmo formato de §14.9 e do bug da folha que se fechava sozinha: a asserção precisa olhar **o estado da tela** (`classList.contains('open')`), não o conteúdo que a função escreveu antes de falhar.

## 14.25 Guarda de propagação olha a DECLARAÇÃO, não o uso (05/out/2026)

Ao levar o catálogo de ações para as telas, a guarda foi `if 'confSaidaFecha' not in arquivo`. A chave **já estava** no arquivo — em `armarSenhaModal('confSaidaFecha')`, o código que **usa** a ação. Resultado: a tela que mais precisava do catálogo foi a única a ficar sem ele.

> **Para saber se uma chave existe no catálogo, procure `chave:'...'`, não o nome solto.** Nome solto aparece em quem declara e em quem usa, e são coisas diferentes.

O que salvou foi a trava desenhada em setembro: `exigeSenha` devolve `true` para chave desconhecida, então a ação **parou de funcionar visivelmente** em vez de rodar sem registro. **Falhar fechado e barulhento** é o que transforma um esquecimento em bug de dois minutos.

## 14.26 O modelo de camadas da saída, e por que o nosso tem quatro (06/out/2026)

Antes de desenhar a Expedição, lemos doze sistemas — oito brasileiros e quatro globais. A pesquisa inteira está no Projeto (`claude/pesquisa-expedicao-mercado.md`). O que ela mudou, confirmou e abriu está aqui.

Dynamics 365, SAP EWM, Odoo e NetSuite convergem em **sete camadas**: pedido → onda → trabalho → volume → remessa → carga → baixa fiscal. Cada uma existe por uma cardinalidade diferente: um pedido vira três volumes em duas cargas; uma onda cobre duzentos pedidos.

**O nosso tem quatro:** Pedido → Separação → Volume → Romaneio.

Juntamos *remessa* e *carga* num objeto só porque separar as duas só paga quando existe consolidação multi-pedido por cliente **e** mais de um veículo por remessa. E não temos *onda* como objeto: a Separação faz esse papel, um pedido por vez. **Quando a fila do galpão passar de algumas dezenas por turno, a onda vira o próximo objeto a nascer** — é o que os quatro globais fazem, e a razão é sempre a mesma: a rota eficiente no armazém não respeita a fronteira do pedido.

### Confirmar a saída e baixar o estoque: por que lá são dois eventos e aqui é um

O Dynamics confirma a carga (`load → Shipped`) e **não baixa estoque** — a dedução vem depois, no lançamento do packing slip. Eles separam para que **erro de doca não vire lançamento contábil errado**.

> **Isso não se aplica a nós, e é mérito do nosso desenho: a nota já saiu na Conferência de Saída.** A baixa da Expedição é puramente física, sem documento a postar junto. Os dois eventos podem ser um só.

E o ganho de brinde: **pedido que volta da doca não precisa de estorno nenhum**, porque nada foi baixado ainda. O Sankhya precisa de um "Endereço de Estorno" e de tarefa de retorno no coletor justamente porque na arquitetura dele o estoque já se mexeu.

### As regras que a pesquisa trouxe

> **Um romaneio = uma forma de envio.** Não mistura Correios com transportadora. O romaneio é a folha que o motorista assina, e ele leva uma carga só.

> **Peso bruto é bloqueante para fechar o romaneio** — e é aqui, não na conferência, porque é aqui que a balança está.

> **O romaneio sai em duas vias, com assinatura.** É o padrão do PLP: o atendente confere, carimba e devolve uma via, e **essa via é o comprovante de postagem** — a prova para reclamar extravio.

**Conferência de volume é escolha deliberada e minoritária no Brasil.** O Sankhya diz com todas as letras que a fila de conferência dele não funciona com volumes; os nacionais conferem item e param. Quem confere volume é D365 e SAP, por SSCC / license plate. Seguimos os globais: é a única conferência que pega o pacote que subiu no caminhão errado.

## 14.27 O que a lei trava no despacho, e o que ela não trava (06/out/2026)

Pesquisa de 06/out, com as fontes no doc do Projeto. Três achados que mudam a tela:

**Documento fiscal é o único bloqueio duro.** Desde **06/04/2026** a declaração de conteúdo em papel acabou — só vale a **DC-e** eletrônica (modelo 99, Ajuste SINIEF 05/21), e o transportador **não aceita envio sem chave de NF-e ou DC-e**. No nosso fluxo a nota nasce na Conferência de Saída, então ela sempre existe; a trava é de verdade, mas nunca deveria disparar.

**MDF-e não pode ser trava fixa.** Entrega intramunicipal com veículo próprio **não exige**. Interestadual com veículo próprio exige em SP (Portaria CAT 102/2013). Mas o **RS exige até com uma nota só e também no intermunicipal**, e MG no intermunicipal desde 2015.

> **Regra que muda de estado não vira `if` — vira parâmetro por UF.** E a tela **avisa**; quem emite é o módulo fiscal.

**O canhoto de papel também acabou:** desde 01/12/2021 o evento *Comprovante de Entrega da NF-e* (Ajuste SINIEF 38/2021) substitui ele, com guarda de 5 anos. Isso pertence a **Rastreamento de Pedidos**, não à Expedição — é o que acontece **depois** que a carga saiu.

**E o romaneio não é documento fiscal**, é controle interno. O formato é nosso.

## 14.28 O tipo decide o formulário — campo que não se aplica SOME (06/out/2026)

O cadastro de Transportadoras tem quatro tipos, e eles não são rótulo: são o que decide o que a Expedição vai cobrar daquela forma de envio.

| tipo | coleta e prazo | limite de peso | CNPJ | MDF-e |
|---|---|---|---|---|
| Correios | sim | sim | não (não é CNPJ nosso nem de terceiro que a gente controle) | não |
| Transportadora | sim | sim | **sim** | não — o documento é do prestador |
| Frota própria | sim | sim | não (o veículo é da empresa) | **sim** |
| Retirada no balcão | **não** | **não** | não | não |

> **Campo que não se aplica some, em vez de ficar cinza pedindo para ser preenchido.** E no lugar dele entra a frase que explica por quê — não um espaço vazio.

**Retirada no balcão não entra em romaneio.** Não tem carga, não tem motorista, não tem coleta: o pedido conferido fica aguardando retirada, e a baixa física acontece na entrega ao cliente. Isso é **derivado do tipo**, não um interruptor separado — dois lugares dizendo a mesma coisa é um lugar para elas discordarem.

**O MDF-e só aparece em frota própria** porque é o único caso em que o documento é nosso. Com Correios e com transportadora quem emite CT-e e MDF-e é o prestador do transporte.

## 14.29 A regra do MDF-e virou parâmetro de verdade (06/out/2026)

§14.27 disse que a obrigação muda por estado e que isso não pode virar `if`. Aqui está como ficou:

```js
mdfeRegraUF: { SP: 'interestadualMulti', RS: 'intermunicipal', MG: 'intermunicipal' },
mdfeRegraPadrao: 'interestadual',
```

UF que não está no mapa **herda o padrão conservador** — a tela nunca inventa uma regra para um estado que ninguém configurou. E a frase que o usuário lê é montada a partir do parâmetro, então **trocar a UF muda a frase**: parâmetro que não muda nada na tela é enfeite, e a suíte testa exatamente isso.

As três frases terminam sempre com as duas ressalvas que a pesquisa trouxe: **intramunicipal com veículo próprio não exige**, e **quem emite é o módulo fiscal** — a Expedição só avisa.

## 14.30 Duas coisas que o menu e o CSS ensinaram nesta rodada (06/out/2026)

**O menu já sabia onde a tela morava.** Comecei a construir Transportadoras como `pagina-cadastros-transportadoras.html` e inseri o item no flyout de Cadastros em 62 arquivos. O sistema já tinha uma entrada **Transportadoras** parada em **Operacional**, sem destino, desde o primeiro desenho do menu — junto com Formas de Pagamento, Cupons e Motivos de Devolução, que são o mesmo tipo de coisa. Desfiz tudo e liguei a entrada que já existia.

> **Antes de escolher o módulo de uma tela nova, leia o menu.** Entrada sem destino não é lugar vago: é decisão tomada e esperando tela.

**`:first-of-type` conta o TIPO da tag, não a classe.** `.form-secao:first-of-type` nunca pegava, porque o primeiro `div` do painel é o `.drawer-header`. A regra existia, estava escrita, e não fazia nada — a primeira seção vinha com linha e espaço de separador sem ter nada acima para separar. Classe explícita (`.form-secao.primeira`) resolve e não depende da ordem das tags irmãs.

## 14.31 O romaneio nasce sugerido, e a sugestão tem dois eixos (06/out/2026)

A fila da Expedição não abre vazia esperando alguém montar carga. Ela abre com os romaneios **já montados**, e a pessoa confirma ou tira pedido. A regra de agrupamento tem **dois eixos e só dois**:

> **forma de envio × dia de coleta.**

O dia de coleta não é escolha livre: sai do cadastro da transportadora, com as duas regras que moram lá — **só vale dia em que ela coleta**, e **hoje só vale se o pedido ficou pronto antes do horário de corte**. Pedido conferido às 16h30 para os Correios (corte 16h) cai no romaneio de amanhã, e isso acontece sozinho.

Transportadora sem dia de coleta devolve **nulo**, e nulo quer dizer **"não entra em romaneio"** — não "erro". É assim que a retirada no balcão fica de fora sem precisar de `if` com o nome dela dentro.

**A sugestão é uma função, não um estado.** Ela roda na abertura quando `PARAM.romaneioSugereAutomatico` manda, e roda de novo por *Mais ações → Rodar a sugestão do dia* — porque pedido continua chegando durante o dia. Desligar o parâmetro não quebra nada: a tela passa a abrir só com o que foi montado à mão.

**E a tela diz o que ficou fora, em palavras.** A pergunta de todo dia no galpão é "cadê o pedido do fulano?", e a resposta quase sempre é "a transportadora dele não coleta hoje". Isso é uma frase na tela, computada, não uma dedução de quem olha:

> *Na doca agora: 11 pedidos conferidos — 7 saem hoje, 3 esperam o próximo dia de coleta (quarta 07/10), 1 não entra em romaneio (retirada no balcão).*

## 14.32 A conferência é por VOLUME, mas a carga é por PEDIDO (06/out/2026)

Esta é a regra que o romaneio inteiro gira em torno, e ela vale a pena ser dita duas vezes.

**Conferir por volume** é escolha deliberada e minoritária no Brasil (§14.26): é a única conferência que pega a caixa que subiu no caminhão errado. Cada volume tem etiqueta própria (`VOL-0026-3`), e é ela que o leitor lê.

**Mas ninguém despacha meio pedido.** Caixa "2 de 4" sozinha no caminhão não é meia entrega — é um pedido quebrado no meio do caminho, com o cliente recebendo parte e abrindo reclamação pelo resto. Então:

> **pedido só embarca com TODOS os seus volumes bipados. Pedido incompleto volta inteiro para a fila de prontos.**

É por isso que o volume mora dentro do bloco do pedido na tela, e é o bloco — não a linha — que carrega a marca `completo` / `incompleto`.

E a carga parcial sai barata justamente por causa de §14.26: **nada precisa ser estornado**, porque a baixa do estoque só acontece no despacho. Tirar um pedido do romaneio, cancelar um romaneio inteiro ou despachar deixando dois pedidos para trás são todas operações sem rastro contábil — e a confirmação diz isso com todas as letras, para que ninguém hesite achando que vai sujar alguma coisa.

## 14.33 Duas travas no despacho, e o resto é aviso (06/out/2026)

O botão "Despachar a carga" recusa em exatamente dois casos:

1. **peso bruto não informado** — é o número que vai no romaneio e é por ele que a transportadora cobra;
2. **nenhum pedido completo** — romaneio sem carga não é despacho.

Todo o resto **avisa e deixa passar**: volume acima do limite de peso da transportadora, carga saindo incompleta, MDF-e em carga própria, balança fora da soma dos volumes. Quem está olhando para a caixa decide; a tela informa.

**A soma dos volumes é referência, não verdade.** Pallet, filme e caixa-mãe pesam. Por isso existe `PARAM.expedicaoDesvioPesoPct` (15%) e não um `if` com um número dentro — e a comparação é contra **o que foi bipado**, não contra o romaneio inteiro. Comparar com o total acusaria 37% de desvio justamente quando um pedido fica para trás de propósito, que é o caso em que a tela mais precisa estar certa.

**Bipar o primeiro volume move o romaneio de "em montagem" para "conferindo".** A situação acompanha o trabalho; não existe botão "iniciar conferência" que alguém precisa lembrar de apertar.

**Etiqueta já bipada avisa, não desmarca.** Na doca o leitor dispara duas vezes com facilidade, e desmarcar calado transformaria caixa conferida em caixa esquecida.

## 14.34 O romaneio sai em duas vias, e não é documento fiscal (06/out/2026)

O formato é nosso porque o romaneio é **controle interno** (§14.27). O que a pesquisa trouxe foi o uso, não o layout: é o padrão do PLP dos Correios — o transportador confere, assina e devolve uma via, e **essa via carimbada é o comprovante de que a carga saiu**, a base para reclamar extravio.

Então as duas vias são "Via do galpão" e "Via do transportador", cada uma com a tabela de pedidos (pedido, cliente, NF-e, destino, volumes, peso), o peso bruto, motorista e placa, e **duas linhas de assinatura**. O rodapé diz, em letra pequena e sem rodeio, que o documento não tem validade fiscal — porque uma folha com tabela e assinatura é exatamente o tipo de papel que alguém assume ser nota.

## 14.35 Quatro nomes para um componente, e o que isso custou (08/out/2026)

O rodapé de salvar existia em 22 telas com **quatro** nomes: `.barra-salvar`,
`.par-barra` (Configurações), `.form-footer-bar` (os cadastros) e dois rodapés
soltos vestidos de `.form-actions` e `.drawer-footer`. Três dos quatro já
punham o botão à esquerda — o "padrão antigo" era a minoria, com 6 telas.

A conta chegou em **Pedidos de Venda**. Alguém renomeou o CSS para
`.barra-salvar` e esqueceu o HTML, que ficou em `.form-footer-bar` — classe que
naquela tela só existia dentro de `body.modo-leitura`, para esconder. Resultado:
em modo de edição a barra era uma `div` crua, sem sticky, sem borda, sem
espaçamento, com o CSS certo morto duas telas acima. Nenhuma auditoria pegou:
a checagem de "classe sem CSS" encontra o nome dentro de
`body.modo-leitura .form-footer-bar` e dá por satisfeita.

A lição não é "renomeie com cuidado", é **não ter dois nomes**. Enquanto os dois
existirem, a próxima tela copia o que estiver mais perto. Hoje é um nome só
(§11.3) e `teste_rodape.py` [1] reprova se qualquer aposentado voltar.

## 14.36 "Cancelar" num rodapé de cadastro não cancela nada (08/out/2026)

Em seis telas o "Cancelar" ao lado de "Salvar" era um `<a href>` puro. Ele não
desfazia: **saía da página, levando junto tudo o que não tinha sido gravado, sem
aviso nenhum.** Em Produtos dava para preencher sessenta campos, clicar nele
achando que desfazia a última alteração, e perder a tela inteira.

Duas regras saíram daí. O link **diz o destino** ("Voltar pras ordens de
compra", "Voltar pro caixa") — e só se chama "Descartar alterações" quando de
fato descarta sem sair, que é o caso de Minha Conta. E **sair com pendência para
e pergunta**, nos *dois* caminhos de saída, o link do rodapé e o do topo:
avisar só num deles é pior que não avisar, porque ensina que a tela avisa.

## 14.37 Referência medida cedo demais mente calada (08/out/2026)

A nota do rodapé compara a tela com uma referência tirada na abertura. Em
Pedidos de Venda a referência era tirada **antes de a tela se montar**: ela
congelou um formulário vazio, e a nota passou a dizer "Nenhuma alteração
pendente" — não porque fosse verdade, mas porque nunca mais olhou.

O que torna esse bug caro é que ele **passa no teste óbvio**. A asserção "a nota
abre dizendo que nada está pendente" fica verde com o defeito instalado: a nota
diz exatamente isso. Só reprova quem compara a referência guardada com a tela já
montada — `teste_rodape.py` [3]. Reinjetado, o defeito derruba a [3] e deixa a
outra passando.

Vale o mesmo para qualquer estado tirado na abertura: **meça depois do
`load`**, não no fim do script.

```js
if (document.readyState === 'complete') setTimeout(marcarSalvo, 0);
else window.addEventListener('load', () => setTimeout(marcarSalvo, 0));
```

E a variação disso que apareceu na mesma rodada: nas telas de Configurações a
nota nascia **vazia**, porque a função que a escreve só rodava quando alguém
mexia em algo. Vazio não informa — pode ser "nada mudou" ou "a tela parou de
olhar", e é exatamente essa diferença que a nota existe para contar. A nota
nasce escrita.

## 14.38 A devolução entra pelo mesmo caminho da compra (08/out/2026)

Devolução de venda é, fiscalmente, uma **nota de entrada** — é assim no Bling e
no Tiny/Olist. O "Lançar estoque" que a tela de Devolução tinha era um atalho
que pulava o documento que a lei espera, e tinha um segundo defeito mais caro:
deixava alguém declarar o **estado da mercadoria** antes de ter aberto a caixa.

O fluxo passou a ser:

```
devolução salva → nota de entrada EM TRÂNSITO (documento existe, mercadoria na rua)
   → "confirmar chegada" → fila de Conferência de Entrada
      → confere com o produto na mão → o saldo sobe
```

Três coisas que esse desenho resolveu e vale não desfazer:

**Confirmar chegada não é lançar saldo.** Chegada é fato da portaria e não pede
senha — quem recebe caixa faz isso dezenas de vezes por dia, e senha a cada
caixa vira senha compartilhada, que é pior que senha nenhuma. Lançar saldo é
consequência de ter contado, e acontece na conferência.

**"Em trânsito" é situação de verdade, não enfeite.** Sem ela, uma devolução
aberta hoje com a caixa chegando em oito dias fica indistinguível de uma que já
está no galpão esperando contagem.

**Manifestação do Destinatário não se aplica.** Ela é evento sobre nota de
*terceiro* contra o nosso CNPJ; numa devolução a nota é nossa ou do cliente. O
bloco inteiro some do painel (§14.28). Antes ele aparecia, mostrava "Registrada
como **undefined**", inventava um prazo de 205 dias, e ao ser clicado gravava um
evento que a coluna da listagem — corretamente — ignorava: **a tela gravava uma
coisa e mostrava outra**.

E uma regra fiscal que o modelo precisou saber: **cliente pessoa física não
emite NF-e**. Quando o cliente é PF, quem emite a nota de entrada somos nós,
contra o nosso próprio CNPJ. Cliente PJ emite a dele.

O nome `pagina-estoque-conferencia-entrada.html` **ficou como está** de propósito:
não aparece para quem usa, não causa bug, e renomeá-lo mexeria no `data-href` de
70 telas e na cobertura do selo. Decisão, não esquecimento.

## 14.39 Logística reversa: o que a pesquisa derrubou do desenho (08/out/2026)

Duas descobertas mudaram a tela, e as duas são contraintuitivas.

**Não se imprime etiqueta na reversa dos Correios.** O que sai é um **código de
autorização de postagem**: o cliente leva o código à agência. O que se imprime é
a **declaração de conteúdo**, que é obrigatória e acompanha a encomenda, mesmo
quando a ida saiu com NF-e. A etiqueta vale 20 dias.

**Mas isso não vale para todas as plataformas.** A central de ajuda do SuperFrete
diz que eles não têm recurso direto de reversa: o caminho é gerar uma **etiqueta
normal com remetente e destinatário trocados** — e aí o cliente **precisa de
impressora**. Um cliente sem impressora não consegue devolver por essa via, e é
justamente a oferta mais barata da lista. Por isso cada oferta carrega a marca
do que ela exige: `Código de postagem`, `Etiqueta para imprimir` ou `Coleta nossa`.

**O estado do meio.** Entre "pedir" e "o cliente pode postar" existe um buraco
que o fluxo implica e que ninguém nomeia: o pedido foi gerado na plataforma mas
**o código não saiu**, porque falta pagar ou falta saldo. Sem esse estado
visível, alguém pede a reversa, avisa o cliente, e o código nunca aparece. A
tela diz, com todas as letras, que o cliente **não foi avisado** ainda.

**O código nasce vazio.** Ele só existe depois que a plataforma cobra e gera.
Inventar um número ali seria pior que o campo em branco: alguém repassaria ao
cliente um código que a agência não reconhece.

**Registrar e alterar são atos diferentes.** Registrar preenche campo vazio e é
rotina; **alterar** troca um número que o cliente já viu na vitrine e pode estar
anotado no bolso dele a caminho da agência — então pede senha, guarda o código
antigo no histórico, e a correção vai **para a vitrine**. Esconder a troca do
cliente o deixaria com um código que não funciona mais.

A ordem da lista é por **preço**, com a coleta própria por último mesmo custando
zero: "sem custo" ali quer dizer "não cobrado por terceiro", e deixá-la no topo
faria a lista mentir sobre qual é a oferta mais barata.

## 14.40 Frete é cobrado por peso FATURADO, e a conta volta depois (08/out/2026)

Duas coisas que a cotação precisa saber e que não são óbvias.

**O frete não sai do peso da balança.** Ele sai do **peso faturado**, que é o
maior entre o peso real e o **peso cubado** — `(C × L × A) ÷ 6.000` nos
Correios. Uma caixa grande e leve paga pelo volume. Com uma exceção que muda a
conta: nos **Correios, Jadlog e Loggi**, cubagem de **até 5 kg é desconsiderada**
e vale o peso real. Então a regra não é "sempre o maior" — é "o maior, acima de
5 kg de cubagem".

Cotar só pelo peso real subestima tudo o que é volumoso, e a diferença volta
depois como débito. A tela mostra a conta inteira (real, cubado, qual mandou e
o faturado) em vez de entregar um número que ninguém consegue conferir. Item sem
peso no cadastro é avisado, não somado como zero.

**A transportadora reafere na postagem.** O pacote é pesado e medido de novo na
agência, e a diferença é repassada: no Melhor Envio porque a própria plataforma
foi cobrada; na SuperFrete debitando a carteira e, sem saldo, o cartão.

Isso abria um buraco no ERP: a reversa gravava **um** valor, o cotado. Quando a
cobrança real chega, se o frete era do cliente a conta a receber fica errada, e
se era nosso a despesa fica subdimensionada. Agora são **dois campos** — cotado
e real — com a diferença visível e o ajuste indo para quem paga.

O evento da reaferição é **interno**: é conversa nossa com a transportadora, e o
cliente não tem o que fazer com ela. Se o frete era dele, a mudança aparece na
conta a receber, que é onde ele de fato vê.

**O valor real não tem como vir sozinho.** A API do Melhor Envio tem saldo,
recarga e pagamento de etiquetas, mas **não tem endpoint de extrato** — e é no
extrato que a cobrança da reaferição aparece. O campo manual não é provisório:
é a única via. O que a integração pode fazer é avisar que vale olhar, pelo
status da etiqueta.

E duas armadilhas da integração, para quando ela vier:

- **O webhook só atende etiqueta gerada pelo próprio aplicativo.** Etiqueta
  criada pelo site do Melhor Envio, ou por outro app na mesma conta, **não
  dispara webhook**. Quem gerar uma reversa direto no painel deles fica
  invisível para o ERP — mais uma razão para o campo manual existir sempre.
- **O sandbox não cobre o que importa:** só Correios e JadLog, e não gera o
  código de reversa. O fluxo que mais precisa de teste é o que menos dá para
  testar fora de produção.

## 14.41 Motivo sem cadastro é regra sem dono (08/out/2026)

Os motivos de perda viviam escritos no código do Acerto de Estoque, e um dos
campos **não era rótulo**: `fiscal` decide se a baixa exige NF-e própria (CFOP
5.927, sem destaque de ICMS, com estorno do crédito aproveitado na entrada), se
resolve com documento interno, ou se depende da diferença apurada.

Isso é o mesmo padrão do cadastro de Motivos de Devolução, que nasceu dois dias
antes: a lista parece texto, mas cada entrada **dispara um comportamento**.
Enquanto ela vive dentro de uma tela, mudar a regra fiscal é editar JavaScript —
e ninguém fora do código sabe que a regra existe.

O cadastro tem dois eixos, e o segundo é o que importa:

| eixo | o que decide |
|---|---|
| Em que movimento vale | o Acerto só oferece os motivos do movimento escolhido |
| **O que a baixa obriga** | NF-e própria · documento interno · depende · nenhuma |

**A asserção que justifica o cadastro existir** compara o que o cadastro diz com
o que o Acerto oferece, código a código e tratamento a tratamento. Sem ela, as
duas listas divergem em silêncio e o motivo escolhido no Acerto deixa de ser o
que o cadastro descreve — com o tratamento fiscal errado junto. Ela foi provada
nos dois sentidos: mudar `Furto ou roubo` de `nfe` para `interno` só no Acerto
faz a suíte reprovar.

Enquanto não há backend, a lista do Acerto fica como **espelho** do cadastro, e
isso está escrito lá: mesma ordem, mesmos códigos, mesmo tratamento. Quando o
backend entrar, ela some.

**Dois erros ao clonar um cadastro, que valem para o próximo:**

- Substituir o nome por texto renomeia **também o item de menu** do cadastro de
  origem, criando item duplicado no flyout. A checagem 11 da auditoria pega.
- Os **valores padrão do formulário** continuam apontando para chaves do
  cadastro antigo (`revendavel` num cadastro que não tem destino de estoque).
  O dropdown abre vazio e o aviso condicional não aparece ao criar um registro
  novo — e isso passa despercebido, porque editar um registro existente
  funciona.

## 14.42 Meta é listagem com painel, e o número tem uma casa só (08/out/2026)

A primeira tela de Metas era um formulário solto: escolhia a loja, digitava o
valor, salvava. Funcionava, e era **mais rasa que qualquer outro cadastro do
sistema** — não mostrava quem estava batendo, quem estava atrás, nem quanto
faltava. O usuário chamou de vaga, e era.

O desenho que ficou é o mesmo do Rastreamento e da Devolução: **a listagem lê,
o painel lateral escreve**. A tela principal mostra as metas do mês com o
realizado ao lado; definir ou alterar abre o painel.

O que a pesquisa em Olist e Bling trouxe, e o que virou regra aqui:

| decisão | o que ficou |
|---|---|
| Níveis | loja e vendedor, em abas |
| De onde vem o realizado | Pedidos de Venda **faturados** — orçamento e pedido em aberto não contam |
| Ritmo | **dias corridos**: no dia 8 de um mês de 31, o esperado é 8/31 da meta |
| Loja x vendedores | **independentes**. A soma dos vendedores não precisa fechar com a loja; quando não fecha, a tela **avisa a diferença** e não corrige nada sozinha |
| Como se define | mensal, trimestral (divide por 3), anual (divide por 12) ou progressivo (cresce X% ao mês), sempre com **prévia** dos meses que serão gravados |
| Mês fechado | alterar meta de mês que já passou **pede senha** (`metasAlteraFechado`); definir meta futura é trabalho normal (`metasDefine`) |

A situação tem seis valores e a ordem importa: sem meta, futuro, batida, não
batida, no ritmo, abaixo do ritmo. **"Abaixo do ritmo" só existe no mês
corrente** — mês fechado é batida ou não batida, e mês futuro não tem ritmo
para medir. Os seis rótulos estão no dicionário de nomes (`metas.situacao.*`).

**A lição que vale para o próximo par de telas.** Performance de Vendas tinha a
**sua própria cópia** dos números de meta. As duas telas mostravam a mesma
loja, no mesmo mês, e podiam discordar sem que nada reclamasse. Agora as duas
carregam o mesmo bloco de dados e a mesma função `situacaoDaMeta`, e a suíte
compara os dois — os dados e o **texto da função**. Provada nos dois sentidos:
mudar uma meta só em Performance faz ela reprovar.

Enquanto não há backend, isso é espelho, como a lista de motivos do Acerto
(§14.41). **Ainda há duas cópias fora do espelho:** `HISTORICO_METAS` no
detalhe de Lojas Desk e os números do Dashboard de KPIs. Elas não foram
conferidas contra Metas; quem mexer em uma das duas confere antes.

**Performance perdeu duas coisas na reconstrução**, de propósito e à vista: o
botão "Colunas" e os filtros de status e tipo. No lugar entrou o seletor de
visão (resultado, devoluções, comparativo), que troca o conjunto de colunas
inteiro. Se o usuário sentir falta, volta — não foi esquecimento.

**Um bug que a tela-molde carregava.** Metas foi gerada a partir da listagem de
Devolução, e lá o Esc chamava `fecharDrawer()`, função que **não existe** — o
nome certo é `fecharPainel()`. O painel não fechava no Esc e o console acusava
erro a cada tecla. Nenhuma suíte apertava Esc com o painel aberto; agora a de
Devolução aperta. Clonar uma tela copia também o que ninguém testou nela.

## 14.43 Botão que é link: uma regra só, e o link leva o contexto (08/out/2026)

O sublinhado em botão voltou **duas vezes no mesmo dia** — primeiro no
`.btn-mini`, depois no "Definir metas" de Performance. A primeira correção
acrescentou uma classe a uma lista, e a lista não existia em todas as telas.
Medido no navegador: em **10 das 71 telas** alguma classe `btn-*` sublinhava
quando usada num link, a maioria em estado latente.

Agora toda tela carrega uma regra só, que não depende de lembrar a classe:

```css
a[class^="btn-"], a[class*=" btn-"],
a[class^="btn-"]:hover, a[class*=" btn-"]:hover { text-decoration:none; }
```

A seção 6 de `teste_menu.py` mede isso nas 71 telas com **toda** classe `btn-*`
que a tela declara, não só com as que hoje aparecem em link. Provada nos dois
sentidos.

**A segunda metade do mesmo botão.** Ele levava para a listagem de Metas
inteira, e a pessoa tinha de achar de novo a loja em que já estava. Botão
dentro do painel de um registro **leva o registro junto**:
`pagina-vendas-metas.html?definir=loja:2&mes=10&ano=2026` abre Metas na aba,
no período e com o painel de definição já naquele alvo. Alvo que não existe
avisa, em vez de abrir painel vazio. É a mesma lição do "Ver a devolução" que
caía na listagem, pela segunda vez no dia; vale conferir todo link que sai
de dentro de um painel.

## 14.44 As telas ganharam pasta, e o que a mudança cobrou (08/out/2026)

As 71 telas viviam soltas na raiz do projeto. Agora o projeto é `ERP System`, e cada tela mora em
`telas/<módulo>/`, na pasta do módulo em que o **menu** a mostra.

```
telas/inicio  cadastros  estoque  vendas  logistica  financas  operacional  configuracoes
      integracoes (vazia)   _molde   fontes
```

O nome do arquivo não mudou e continua único no sistema. Foi essa decisão que deixou a mudança
barata: documento, suíte e selo citam a tela pelo nome, e só um arquivo (`_ferramentas/localiza.py`)
precisou aprender onde cada uma está.

**O que mudou dentro das telas, nas 71:**

| o quê | antes | agora |
|---|---|---|
| link para outra tela (3.360 ocorrências) | `pagina-vendas-metas.html` | `../vendas/pagina-vendas-metas.html` |
| fonte | `url('fontes/...')` | `url('../fontes/...')` |
| guarda do breadcrumb "Início" | `pathname.endsWith(destino)` | `pathname.endsWith(destino.split('/').pop())` |

O link leva a pasta **sempre**, mesmo entre duas telas do mesmo módulo. Uma regra só é mais fácil
de conferir do que uma regra com exceção, e a tela copiada de outro módulo já nasce certa.

A terceira linha é a que não aparece em busca por nome de arquivo. A guarda comparava o endereço
atual com o destino para não recarregar a própria tela de Início. Com o destino ganhando
`../inicio/` na frente, a comparação passaria a dar falso **sempre**, e o clique recarregaria a
página em silêncio. Reescrever um caminho exige olhar onde ele é **comparado**, não só onde ele
é usado para navegar.

**O que a verificação quase deixou passar, e que vale além desta mudança:**

- **Um verde sem contagem.** A auditoria oficial da skill varre `pagina-*.html` numa pasta única.
  Apontada para `telas/`, ela não achou arquivo nenhum e respondeu "tudo limpo". Não era mentira,
  era zero de zero. O selo agora só aceita o verde dela se a saída disser que viu as 71. Vale para
  qualquer checagem que varre pasta: **"nenhuma falha" precisa vir com "em quantos"**.
- **Caminho no lugar de nome.** Onde a suíte listava a pasta e comparava com um nome
  (`arq == 'pagina-molde-referencia.html'`), a comparação virou falsa calada quando a lista passou
  a trazer caminho. A suíte passaria a reprovar o molde por um item "duplicado" que sempre esteve certo.
- **A auditoria oficial audita um espelho.** Ela mora fora do projeto e não pode ser ensinada
  daqui. Recebe as mesmas telas copiadas para uma pasta só, com os links de volta ao formato
  antigo. É dívida declarada: some quando a skill for atualizada na origem.

A regra do link ganhou guarda própria (`teste_menu.py`, seção 7): toda citação a uma tela diz a
pasta, e a pasta tem a tela dentro. Provada nos dois sentidos.

## 14.45 A varredura que quebrou no fim, e o que ela quase escondeu (08/out/2026)

A varredura de cliques é a ferramenta de fechamento de módulo: abre cada tela e clica em tudo.
Rodada depois da mudança de pastas, ela confirmou o que interessava (2.362 cliques em 70 telas,
nenhuma navegação para arquivo inexistente) e achou o que ninguém procurava: **20 erros de
JavaScript na listagem de Devolução**.

Os três filtros da listagem (responsável, motivo, forma de ressarcimento) e o "Limpar filtros"
chamavam `setDropdownValor`. A função existe em cinco telas de cadastro. Na de Devolução, nunca
existiu. Escolher uma opção dava erro **antes** de filtrar: o botão não mudava, a lista ficava
igual, e a tela parecia só não ter nada para filtrar.

É a **segunda função inexistente nesta mesma tela** no mesmo dia (a primeira foi a do Esc, §14.42).
As duas vieram do mesmo jeito: a tela nasceu de cópia, e a cópia trouxe a chamada sem trazer a
definição. Nenhuma suíte apertava esses controles, e uma chamada que ninguém dispara não quebra
nada à vista.

**Quase não apareceu.** Na primeira rodada do dia a varredura clicou por dez minutos e quebrou na
última linha, ao gravar o resultado: arquivo aberto sem `encoding`, cp1252 por padrão no Windows,
e um texto de tela com seta derrubou a gravação. O relatório não saiu. Não se sabe desde quando
ela quebrava assim; o defeito só dispara quando algum controle tem caractere fora do cp1252.

Três regras que ficam:

- **Ferramenta que não termina não acha nada, e o silêncio dela parece aprovação.** Ao rodar uma
  verificação, confira que ela imprimiu o resumo final, não só que não reclamou.
- **Tela copiada: procure chamada sem definição.** Antes de dar a tela por pronta, a varredura
  roda nela (`python varredura_cliques.py - <nome>`), porque é a única que aperta tudo.
- **Todo `open()` de script daqui diz o `encoding`.** O padrão do Windows não é o do Linux onde
  as ferramentas nasceram.

## 14.46 Cadastro que se configura uma vez não é item de menu (08/out/2026)

O módulo **Operacional** saiu do menu lateral. O usuário olhou o que sobrava nele (Transportadoras,
Motivos de Devolução, Motivos de Perda) e disse o que era: "configuração da operação, configura uma
vez, já era". O Olist guarda essas listas em Configurações, e o nosso hub **já tinha** uma aba
Operacional com os três nomes.

O que mudou:

| o quê | antes | agora |
|---|---|---|
| os três cadastros | item do menu lateral, em Operacional | cartão no hub de Configurações, aba Operacional |
| os arquivos | `telas/operacional/pagina-operacional-*.html` | `telas/configuracoes/pagina-configuracoes-*.html` |
| Formas de Pagamento | item sem tela em Operacional | nasce em Configurações → Finanças |
| Cupons | item sem tela em Operacional | adiado para as vitrines: hoje nenhuma tela lê cupom |
| caminho da tela | Operacional › Transportadoras | Configurações › Configurações ERP › Transportadoras |

No catálogo de senhas, `onde` passou a dizer `Configurações → ...` e `grupo` continuou `Operacional`:
o grupo é a área do assunto (é o nome da aba do hub), não o lugar do menu. É a mesma forma de
Contas financeiras, que mora em Configurações e é do grupo Finanças.

**O defeito que a mudança revelou.** O hub listava os três cadastros como cartão **sem destino**, com
a etiqueta de "a construir", e as três telas estavam prontas havia dias. Cartão morto para tela que
existe é beco do mesmo tipo do item de menu sem `data-href`, só que num lugar que nenhuma suíte
olhava. Agora `teste_menu.py` (seção 8) cobra que **toda tela da pasta de Configurações tenha cartão
com destino no hub**, e que o módulo apagado não volte numa tela copiada de versão antiga.

**Regra para a próxima lista auxiliar:** se a pessoa configura uma vez e a operação só lê, a tela
nasce em Configurações, com cartão no hub. Item de menu lateral é para o que se usa no dia a dia.

**Nome antigo de arquivo não redireciona.** O servidor redireciona endereço sem pasta, não arquivo
renomeado: `/operacional/pagina-operacional-transportadoras.html` agora dá 404.

## 14.47 Forma de recebimento decide para onde o dinheiro vai (08/out/2026)

O cadastro nasceu em Configurações → Finanças, no cartão que o hub já reservava. A pesquisa do
Olist estava feita desde 17/set (arquitetura, lote da aba finanças); o que faltava era a tela.

**As seis listas do código eram três coisas diferentes**, e só olhando as seis lado a lado isso
apareceu:

| onde | o que era | o que virou |
|---|---|---|
| Contas a Receber (2 telas) | como recebemos: 10 formas | espelho do cadastro, as que valem para receber |
| Contas a Pagar (2 telas) | como pagamos: 5 formas | espelho do cadastro, as que valem para pagar |
| Devolução (2 telas) | formas de ressarcimento: 4 | **fica no código**: é lista fechada, cada opção dispara um comportamento |
| Pedido de Venda | 6 formas e quais validam limite de crédito | espelho do cadastro, com a regra junto |

O que a forma decide, e por isso tem dono:

- **Vale para** receber, pagar ou os dois. As formas de Contas a Pagar entraram no mesmo cadastro
  por decisão do usuário: uma lista só para manter. Forma que só paga não tem destino, taxa nem
  limite, e esses campos **somem** (§14.28).
- **Destino dos valores:** vira título em Contas a Receber, ou entra direto numa conta financeira.
  Com destino em conta, a conta é obrigatória: sem ela a venda não tem onde cair.
- **Taxa**, em percentual, valor fixo ou os dois, e **quando** é descontada.
- **Validar limite de crédito**, que o Pedido lê. Cheque não valida (decisão do usuário).

**Senha: a matriz do módulo e a regra de dinheiro são coisas diferentes.** No sistema, criar e
editar nascem sem senha e excluir nasce com. Aqui isso vale para incluir uma forma e para mudar o
nome dela. Mexer no destino, na taxa ou no limite de uma forma que já existe muda para onde vai o
dinheiro das próximas vendas: tem ação própria (`formasRecebimentoRegra`), que pede senha por
padrão. É o mesmo desenho de "alterar meta de mês fechado" (§14.42).

**Forma do sistema** pode ser desabilitada, nunca excluída nem renomeada: as outras telas a
reconhecem pela chave. **Vale-troca** está no catálogo como reservada, do mesmo jeito que a
Devolução já a oferece como ressarcimento reservado; as duas pontas ligam juntas.

**Ficou de fora, com o usuário sabendo:** o painel "preferências" do Olist e a tabela de várias
contas por forma (dependem de Gateways, que não existe); prazo de recebimento e parcelas (entram
com o PDV); cashback e vale-presente (entram com as vitrines); a opção "usar como forma padrão";
e os rótulos das listas fechadas desta tela, que ainda não estão em Nomes do sistema.

**Enquanto não há backend, as cinco telas ficam como espelho**, como o Acerto com os Motivos de
Perda (§14.41), e a seção 12 da suíte compara tudo. Forma criada pelo usuário ainda não chega
sozinha a Contas a Receber e Contas a Pagar: o espelho cobre as formas do sistema.

## 14.48 PDV: a venda de balcão é Pedido de Venda, e o caixa é turno (09/out/2026)

`telas/vendas/pagina-vendas-pdv.html` e `telas/configuracoes/pagina-configuracoes-pdv.html`.
Referência: 34 prints do PDV do Olist. Três decisões do usuário, que não se reabrem:

1. **A venda vira Pedido de Venda já entregue.** Não existe "venda de balcão" como lista à
   parte. É por isso que ela conta em Metas e em Performance, que leem os pedidos faturados. A
   situação em que entra é parâmetro (`pdvSituacaoVenda`), e só as de faturado em diante servem.
2. **A loja é escolhida ao abrir o caixa.** Produto pertence a uma loja só, então a loja do turno
   decide o que a busca acha, o depósito de onde sai o estoque e os vendedores oferecidos.
3. **O ciclo entrou inteiro:** abrir o caixa, vender, receber, concluir, sangria, reforço e fechar.

**Uma tela, quatro momentos:** caixa fechado, venda, finalização e venda concluída. O estado fica
em `deskPdv` no navegador e sobrevive ao F5: recarregar a página no meio do turno não fecha o caixa.

**O caixa do PDV não é o Caixa de Finanças.** Um é o turno do operador (gaveta, troco, abertura e
fechamento); o outro é o extrato das contas. A tela e as Configurações dizem isso com todas as
letras, porque o nome é o mesmo. O dinheiro da venda entra na conta financeira "Caixa" e a sangria
sai dela para o cofre.

**Quem decide o recebimento é o cadastro de Formas de recebimento (§14.47), não o PDV:**

- forma com destino em conta entra na hora, sem título;
- forma com destino em título gera Contas a Receber, e por isso **exige cliente identificado**,
  com "cliente obrigatório" ligado ou não: título precisa de devedor. **Menos no cartão**
  (forma com prazo fixo da operadora): ali quem deve para a loja é a operadora, o título nasce
  "a receber" dela e a venda passa para consumidor final (decisão do usuário em 09/out);
- forma que valida limite barra a venda com os quatro números (limite, usado, disponível, pedido);
- as parcelas são digitadas na venda, como `3x` ou `30 60 90`, **só nas formas de vencimento
  combinado** (boleto, crediário, cheque). Cartão tem prazo fixo da operadora e segue o §14.49.

**Fechamento cego é a mesma regra da conferência: contagem sabendo o número é cópia.** Com o caixa
aberto, Detalhes do caixa não mostra o esperado por forma. Contagem que não bate diz **em qual
forma**, nunca quanto era. Sangria maior que a gaveta é barrada sem revelar quanto há. Fechar com
diferença pede senha, e só quem libera vê contado e esperado. Desligar o fechamento cego é a única
mudança das Configurações do PDV que pede senha (`pdvCegoDesliga`).

**Desconto acima do máximo não é proibido: é liberado.** Até `pdvDescontoMaximoPct` o operador
aplica sozinho; acima, o PDV pede a senha de quem pode (`pdvDescontoAcima`). Vale para o item e
para a venda inteira.

**Senhas do PDV:** sangria e fechar com diferença pedem; reforço não pede por padrão. As cinco
ações estão no catálogo, nas três telas que o exibem.

**Lição de componente: `stopPropagation` não cala ouvinte do mesmo nó.** O Esc dos dropdowns roda
na captura do `document` e para a propagação quando fecha um menu. Os atalhos do PDV também estão
na captura do `document`, e rodavam em seguida: um Esc fechava o menu **e** voltava da finalização
para os itens. Quem registrar atalho de Esc na captura confere `e.cancelBubble` antes de agir.

**Espelhos, enquanto não há backend:** catálogo, lojas e depósitos (Pedido de Venda), vendedores
(Metas), clientes (Cadastros), formas de recebimento, contas e categorias financeiras. A seção 9
de `teste_pdv.py` compara cada um com o cadastro de origem. Das categorias entram as de receita de
vendas, fora as de dedução.

**Ficou de fora, com o usuário sabendo:** salvar a venda para depois, faturar pré-venda,
vale-presente, lista de preços, item não cadastrado, enviar o recibo por e-mail ou WhatsApp e
NFC-e. **E a venda ainda não chega às outras telas**: Pedidos, Contas a Receber, Caixa e Metas
têm cada uma os seus dados de exemplo. O PDV diz, na conclusão, o que a venda gerou; a ligação de
verdade é do backend.

## 14.49 Cartão no PDV: prazo da operadora, taxa por parcela e repasse (09/out/2026)

Nasceu do primeiro teste do usuário no PDV. O cartão vinha tratado como crediário: o operador
digitava "30 dias" e o valor de cada parcela. Quatro decisões do usuário mudaram isso.

**Forma de recebimento ganha "vencimento do título"** (Configurações → Formas de recebimento):

- **combinado na venda**: dias e parcelas são digitados no PDV. Boleto, crediário, cheque;
- **prazo fixo da operadora**: o cadastro guarda em quantos **dias úteis** o valor cai, até
  quantas parcelas a forma aceita, **a taxa de cada número de parcelas** (1x é o percentual da
  forma; de 2x em diante, uma grade) e se a taxa é **repassada ao cliente**. É o caso dos cartões.

Campo que não se aplica some (§14.28): sem prazo fixo não há dias úteis, parcelas nem repasse; sem
taxa não há grade nem repasse. Mexer em qualquer um deles é regra de dinheiro e pede senha, pela
mesma ação `formasRecebimentoRegra`.

**No PDV, forma de prazo fixo não tem campo de dia nem de valor de parcela.** O operador informa o
valor e escolhe as parcelas num menu. A tela mostra, só para leitura: a taxa da operadora, quanto
passar no cartão do cliente e quanto a loja recebe, com a data. Nasce **um título só**, no valor
que passou no cartão, seja qual for o número de parcelas: a operadora paga tudo no prazo.

**Repasse é dividir, não somar.** Com repasse, o valor a passar é `venda ÷ (1 − taxa)`, para que
tirada a taxa sobre exatamente o valor da venda. Somar a taxa por cima deixa a loja com menos:
R$ 1.000 a 3,49% viram R$ 1.036,16 no cartão, e não R$ 1.034,90. O cadastro define o padrão e o
operador pode trocar na venda. A diferença aparece como **acréscimo do cartão**, linha própria no
resumo, no recibo e no total da venda. O que falta receber é medido pela venda, nunca pelo
acréscimo; no fechamento do caixa, o esperado do cartão é o que passou na maquininha.

**Dia útil** pula sábado, domingo e feriado nacional de data fixa. Carnaval, Sexta-feira Santa,
Corpus Christi e feriado local esperam um calendário de feriados, que ainda não existe.

**Cartão não confere o limite de crédito do cliente:** o risco é da operadora. O limite vale para
boleto e crediário, no PDV e no Pedido de Venda, que espelha o cadastro.

**O que falta receber entra sozinho.** Dividindo a venda em mais de uma forma, a primeira forma em
que ninguém digitou valor recebe o restante toda vez que outra muda. Forma com valor digitado
nunca é mexida; apagar o campo devolve a forma ao automático. Forma que ficou sem valor diz o que
fazer, em vez de só pedir o valor.

**Menu de ações não é menu de escolha.** O "Mais ações" do PDV usava o componente de dropdown de
seleção, que troca o rótulo do botão pelo item clicado: depois de lançar um reforço, o botão
passava a se chamar "Lançar reforço de caixa". Menu de ações tem rótulo fixo e nenhum item
marcado, como nas outras telas. **Fechar caixa** virou botão próprio no topo.

**Detalhes do caixa** segue o desenho do Olist: painel largo, situação do caixa com a data, fatos
em grade (loja, operador, troco inicial, vendas, sangrias, reforços), resumo por forma em tabela e
fechar caixa no rodapé. A aba de sangrias e reforços lança direto dali, e a de vendas reimprime o
recibo de qualquer venda do turno. Com o fechamento cego ligado e o caixa aberto, o resumo mostra
as formas usadas e quantas vendas, **sem valor**.

**Editar produto** também segue o print: painel largo com o nome, o código e o saldo no depósito
da venda; linhas de rótulo à esquerda e campo à direita (quantidade, preço do cadastro só para
leitura, editar preço); desconto ou acréscimo em **botões de opção à vista**, sem menu para abrir;
o valor do ajuste calculado ao lado do título da seção; o preço total em destaque; e Aplicar,
Remover e Cancelar no rodapé. Não existe a opção "sem ajuste": **campo em branco é sem ajuste**.
O botão de opção é o da casa (`.radio-option`, o mesmo de Cadastros → Vendedores).

**Ação de todo turno é botão, não item de menu.** Sangria e Fechar caixa ficam no topo, ao lado de
Detalhes do caixa. Fechar caixa e Remover item usam contorno e texto na cor de perigo
(`.pdv-btn-perigo`), a mesma do item de perigo do "Mais ações".

**Barra fixa de rodapé fica abaixo do menu lateral.** O cartão do menu lateral tem `z-index: 30`
e o submenu dele abre por cima do conteúdo. A barra do PDV nasceu com o mesmo 30 e, por vir depois
na página, passava na frente do submenu. Barra fixa usa `z-index: 20`, como a `.barra-salvar` das
outras telas.

Ficou de fora: o Pedido de Venda ainda não usa prazo fixo, taxa por parcela nem repasse; ele só
deixou de conferir limite no cartão. As taxas por parcela do cadastro são exemplo. Os atalhos do
Olist para remover item (Ctrl+Backspace) e trocar valor fixo por porcentagem (Ctrl+A, Ctrl+B) não
entraram: são teclas que o campo de texto já usa para apagar palavra e selecionar tudo.

## 14.50 CRM: assunto, estágio, ação e linha do tempo (09/out/2026)

Funil de pré-venda em Vendas → CRM, construído sobre 13 prints do Olist. Um **assunto** é uma
conversa de venda com um cliente: tem estágio, ações (o que fazer e quando) e uma linha do tempo
com tudo que aconteceu. Quatro decisões do usuário mudam o que o print mostra.

**O status do contato é do cliente, não do CRM.** Lead, prospect e cliente são o campo
`contato` de Cadastros → Clientes; "inativo" é a situação que o cadastro já tinha. O CRM lê e
altera esse campo pelo menu da linha, e o rodapé da lista conta os contatos por status. Cadastro
inativo conta como inativo, seja qual for o status do contato.

**Encerrar pede resultado.** O último estágio do funil encerra o assunto, e encerrar pergunta se
foi **ganho ou perdido**; perdido pede o motivo. Por isso ninguém chega ao último estágio por
atalho: o botão do próximo estágio, o menu "mais" e o quadro abrem o painel de encerrar. Assunto
encerrado não recebe ação nova; **reabrir** devolve ao estágio em que estava. Motivo de perda é
lista fechada no código, até a operação querer editar.

**Ação com data vira aviso na Agenda.** A próxima ação tem "previsto para": data, quanto antes,
esperar ou sem data. Campo que não se aplica some: data e horário só existem em "data". A ação
pendente com data, de assunto aberto, é publicada em `deskAvisos` (o mesmo caminho de Contas a
Pagar) e o aviso leva para o assunto. Concluir, excluir, encerrar ou arquivar tira o aviso.

**Ação nova nasce no cartão da tela; a edição abre o painel "Ação do CRM".** É o desenho do
print. Os dois usam o mesmo formulário, com o campo de data da casa.

**WhatsApp e e-mail abrem o aplicativo e registram.** O sistema não envia nada sozinho: monta o
link (`wa.me` com o telefone do cliente, `mailto` com o e-mail e o assunto) e guarda o contato na
linha do tempo. **Proposta** é registro do assunto: valor, validade, condições e situação;
aceita, oferece o pedido de venda. O módulo de Propostas comerciais com itens não existe.

**A ordem é o dado.** Configurações → Estágios do funil de vendas é o único cadastro em que a
posição significa algo. Reordena por seta e por arrastar; o estágio que encerra não sai do fim
nem é excluído, e estágio com assunto dentro também não. O quadro por estágio mostra uma coluna
por estágio, nessa ordem.

**Aviso de assunto parado obedece a um parâmetro.** `crmDiasSemInteracao` (30 por padrão),
gravado em Configurações → Configurações do CRM. Interação é qualquer registro no assunto.

**Lista e assunto dividem o estado** em `deskCrm`: a ação criada no assunto aparece na lista ao
voltar. Estágios, clientes, vendedores, pedidos e contas em aberto são espelhos, e a seção 16 de
`teste_crm.py` compara cada um com o cadastro de origem.

**Lição de código:** a chave do armazenamento ficou sem declarar, e os dois `try/catch` vazios em
volta de `localStorage` engoliram o `ReferenceError`. Nada era gravado e nenhuma tela reclamava;
quem acusou foi a asserção "sobrevive ao F5". `catch` vazio em volta de armazenamento esconde erro
de digitação junto com o bloqueio do navegador.

**Ajustes do primeiro teste do usuário (09/out).**

- **O calendário não abria.** Os dois campos de data do CRM nasceram sem a `.date-pop`, e
  `inicializarDataField` desiste calado quando falta uma das três peças (campo, botão, caixa): o
  botão existia e não fazia nada. `teste_datas.py` passou a abrir toda tela que tem campo de data
  e cobrar as três peças.
- **Horário com relógio.** O campo continua digitável; o relógio abre uma caixa pequena
  (`.date-pop.hora-pop`, 128px) com setas de hora (1 em 1) e de minuto (5 em 5, dando a volta).
  A caixa mostra o que está no campo, sem estado próprio; aberta com o campo vazio, parte da hora
  de agora. `inicializarHoraField` mora na tela do assunto. **Fechado pelo usuário em 09/out:** o
  passo de 5 em 5 minutos fica, e a **Agenda passou a usar o mesmo relógio**, no lugar dos dois
  dropdowns (hora, e minuto de 15 em 15). O componente foi copiado letra a letra, e a seção 18 de
  `teste_crm.py` compara as duas cópias. Como o horário da Agenda virou campo digitável, salvar
  passou a conferir o formato.
- **Esc fecha o que está por cima.** Com calendário ou horário aberto, o Esc fecha a caixa e o
  formulário fica, com o que foi escrito. Antes levava os dois.
- **No cartão do quadro nada fica em linha única.** "Perdido · Prazo de entrega" e "avançar →"
  não cabiam na coluna, vazavam do cartão e criavam a barra de rolagem. A etiqueta do resultado
  virou só "Ganho" ou "Perdido", com o motivo ao lado em texto que quebra; "Avançar" e "Encerrar"
  viraram botão, sem seta; e o rodapé do cartão quebra linha. Cinco colunas cabem sem rolagem a
  partir de 1366; abaixo disso a rolagem dentro do quadro é a degradação prevista.
- **O menu lateral marca o módulo da pasta da tela.** Pedidos de Venda e a página do pedido
  marcavam "Estoque" (herança da tela de que nasceram), e Transportadoras e os dois Motivos, que
  vieram de Operacional, não marcavam nada. A seção 9 de `teste_menu.py` cobra isso em toda tela.

Ficou de fora, com o usuário sabendo: marcadores, a visão "por período", cadastro de motivos de
perda, cadastro rápido de cliente dentro do CRM e o módulo de Propostas comerciais.

## 14.51 Itens Bloqueados: a fila do que está no estoque e não pode ser vendido (09/out/2026)

Nasceu de uma pergunta do usuário diante do "1 bloqueado" na página de um produto: *onde eu acerto
isso, onde eu digo que essa quantidade sai do estoque ou volta para o disponível?* Não havia onde.

**O que faltava, medido no código antes de construir:**

- o saldo `bloqueado` só tinha uma saída, escondida: Acerto de Estoque → Saída → escolher a linha
  "Bloqueado" como origem;
- não existia caminho de volta para o disponível;
- nenhuma tela bloqueava: o bloqueio só nascia sozinho, na conferência de entrada e na devolução;
- a falta da Separação e da Conferência de Saída virava "divergência aguardando reconferência"
  (§14.14), e **nenhuma tela fechava essa reconferência**.

**A regra.** Tudo que bloqueia deságua na mesma fila, e só há duas saídas. A quantidade se reparte
entre elas de uma vez só (de 3 peças, 2 recuperadas e 1 perdida), e o que sobra continua bloqueado:

| saída | o que acontece | senha por padrão |
|---|---|---|
| **liberar** | a quantidade volta para o disponível | não |
| **dar baixa** | gera o acerto de saída, com o motivo e a consequência fiscal do Acerto de Estoque | sim |

**Quatro motivos, lista fechada no código**, porque cada um carrega comportamento: Avaria, Falta a
auditar, Em análise e Travado por decisão. Vira cadastro quando a operação pedir um motivo novo.

**Duas decisões do usuário:**

1. **A falta bloqueia a unidade sozinha.** Revê a regra de 05/out, que não mexia no saldo. O motivo
   daquela recusa continua de pé, porque bloquear não é baixar: o físico não muda e nenhuma
   obrigação fiscal nasce. O que muda é que o próximo pedido deixa de reservar uma peça que talvez
   não exista. A Separação bloqueia ao concluir, no endereço do item; a Conferência de Saída, ao
   fechar, e só a diferença para menos.
2. **O que não é avaria fica no próprio endereço, só travado.** Liberar é destravar no mesmo lugar.
   Avaria continua indo para endereço de Avaria (ou esperando um, na fila do Endereçamento) e,
   liberada, volta pela regra de entrada do item 19: base de picking no depósito, ou fila de
   endereçar.

**Liberar uma falta pede a causa.** São as causas de §14.14: erro de separação, erro de
conferência, e uma terceira que o bloqueio manual trouxe, "foi encontrado em outro lugar". A causa
"não estava no endereço" é a baixa. A aba **Resolvidos** guarda o desfecho de cada caso; ela não
entra em "Todos", porque é histórico, não fila.

**O total soma os endereços; o bloqueio sai do endereço escolhido.** O usuário viu "38 UN livre
para bloquear" e, ao pedir 25, "só há 4 UN livres neste endereço". Os dois números estavam certos e
a tela não dizia a diferença. O total passou a dizer "somando N endereços", o campo diz quanto há
neste e quanto há nos outros, e o erro aponta o caminho. Para travar o produto inteiro, "De qual
endereço" ganhou a opção **"Todos os endereços"**, que só aparece quando o depósito tem mais de um
endereço com saldo livre: o limite passa a ser o do depósito, a prévia mostra a divisão antes de
confirmar (picking primeiro, depois pulmão) e a fila ganha **uma linha por endereço**. Um endereço
só continua sendo o padrão: repartir em silêncio foi descartado, porque quem bloqueia precisa saber
de qual prateleira a peça saiu. Outro depósito é sempre outro bloqueio.

**O bloqueio manual é feito na própria fila.** O painel "Bloquear item" usa a busca padrão de
produto (a do Acerto de Estoque: descrição, SKU ou GTIN, Enter escolhe o primeiro), mostra quanto
está livre e quanto já está na fila, e pede depósito, endereço de origem, quantidade, motivo e
observação. Não é acerto: não muda o estoque físico nem o custo, só passa a quantidade de
disponível (ou a endereçar) para bloqueado. Nunca tira do reservado. Travar por decisão exige
observação. A primeira versão mandava o usuário para a página do produto; ele pediu para bloquear
ali mesmo, e tinha razão: quem está olhando a fila não quer sair dela. O tipo **Bloqueio** do
lançamento da página do produto, em Controle de Estoques, continua existindo, e o número
"bloqueado" de lá virou atalho para a fila, filtrada no produto.

**O painel "Resolver bloqueio" tem três abas.** A primeira versão era um par de opções com uma
quantidade, e o usuário achou pobre.

- **Resolver:** o retrato do bloqueio (quanto, custo parado, há quanto tempo, onde está, de onde
  veio), a quantidade repartida entre "volta para a venda" e "baixa por perda", com o resto
  calculado, e o **estoque do produto no depósito, hoje e depois**: quem decide vê o disponível
  subir e o físico cair antes de confirmar. Uma confirmação só para as duas saídas; vale a mais
  exigente das duas na matriz de senhas, e as duas vão para o registro de atividades. O que veio
  de nota de compra mostra "Devolver ao fornecedor" visível e sem ação, como os campos fiscais.
- **Manter bloqueado:** corrige o motivo ou anota o andamento da auditoria, sem tirar o item da
  fila. Virar avaria tira o item do endereço de venda; deixar de ser avaria não o move.
- **Histórico:** o bloqueio, as anotações e o que já foi resolvido em parte, do mais antigo para o
  mais novo, com o caminho para a página do produto.

**O saldo livre é derivado, não guardado.** A tela carrega um espelho do saldo de Controle de
Estoques (produto, depósito, endereço e estágio) que nunca muda. O que está livre num endereço é o
saldo do espelho menos o que a fila travou ali e menos o que já foi baixado dali; por isso liberar
devolve o saldo livre e dar baixa não devolve. Cada bloqueio guarda `saiuDe`, o endereço de onde a
quantidade saiu, que para avaria é diferente de onde ela está.

**Como as telas conversam no protótipo.** Quem bloqueia (página do produto, Separação, Conferência
de Saída) não conhece a fila: deixa o caso em `deskBloqueiosEntrada`, e Itens Bloqueados recolhe ao
abrir, guardando a chave de cada caso para não entrar duas vezes. O estado da fila mora em
`deskBloqueados`. No sistema de produção isso é o ledger `stock_movements`, com dois movimentos novos de
estágio, bloqueio e liberação, e a baixa como acerto de saída ligado ao bloqueio de origem.

**O tempo bloqueado muda de cor pelos mesmos prazos do Endereçamento** (`enderecamentoAlerta` e
`enderecamentoCritico`, em Parâmetros de estoque). Saldo parado é saldo parado; se um dia os dois
prazos precisarem ser diferentes, nasce um par próprio.

**O que as outras telas mostram.** Cada protótipo de Estoque guarda os próprios dados de exemplo:
liberar ou baixar aqui não muda o saldo que o Controle de Estoques exibe. A semente da fila repete
o que as outras telas já mostravam bloqueado, e a seção 14 de `teste_bloqueados.py` compara.

**Dropdown dentro de tabela com rolagem é cortado pela tabela** (achado pelo usuário na
Conferência de Saída, no mesmo dia). `.itens-table-wrap` declara `overflow-x:auto` e
`overflow-y:visible`, mas quando um eixo não é `visible` o navegador calcula o outro como `auto`:
o menu do motivo abria dentro da área da tabela, era cortado, e a tabela ganhava uma barra de
rolagem própria. O componente media o espaço da janela, não o da área que corta. Nas duas telas
em que isso acontece (Conferência de Saída e Conferência de Entrada), o menu de um dropdown dentro
de `.itens-table-wrap` passa a sair do fluxo (`position:fixed`) e ancorar no botão; rolar a tela
fecha o menu. A varredura das 79 telas não achou o caso em mais nenhuma. No mesmo ajuste, "Banco a
contagem" virou **"Confirmar contagem"**, no botão, nos avisos e no nome da ação em Confirmações por
senha.

**Calendário cortado pela borda do painel** (achado pelo usuário na Agenda, em 10/out). A caixa do
calendário tem 252px e abria alinhada pela direita do campo, sem medir se cabia. Na Agenda o campo
de data fica colado na borda esquerda do painel e é mais estreito que a caixa: a primeira coluna,
domingo, saía cortada. O componente passou a medir depois de abrir e, se a caixa passar da borda da
área que a contém, alinha pela esquerda do campo (`.date-pop.esquerda`). A correção entrou nas
15 telas que têm o componente; a varredura achou o mesmo corte no painel de transferência do Caixa
e Bancos. `teste_datas.py` agora abre cada calendário de cada tela, inclusive os de formulário que
nasce escondido, e cobra que a caixa caiba.

**Filtro de período na fila** (pedido do usuário em 10/out, para a fila e o histórico não virarem
uma lista sem fim). É o popover de período da casa, o mesmo de Entrada de Notas: sem filtro, do
dia, últimos 7 dias, últimos 30 dias, do mês, e mais "mês passado", que serve ao fechamento das
perdas. Vale para a data que a aba mostra: a do bloqueio, na fila; a da resolução, em Resolvidos,
onde o total baixado como perda acompanha o período.

No mesmo dia o usuário pediu **data inicial e data final**, para olhar 3 meses, 6 meses ou um ano
de histórico, e mandou tirar o filtro "há mais de N dias", que não servia. O popover ganhou
"Entre datas": dois campos de data da casa e o botão Aplicar. Uma data só também vale (desde, ou
até); o calendário de cada campo risca os dias que o outro proíbe; opção pronta e intervalo são um
filtro só, e escolher um limpa o outro. Aqui o calendário abre para baixo do campo, porque para
cima cobria as opções prontas. O tempo bloqueado continua mudando de cor na coluna; só o filtro
por dias saiu. É a única tela em que o popover de período tem intervalo livre.

**O popover de período ficava aberto por baixo do dropdown vizinho** (print do usuário, 10/out). Os
dropdowns param a propagação do clique, então o fechamento geral da tela nunca chegava ao popover.
Das dez telas com filtro de período, o defeito estava em **quatro**: Itens Bloqueados, Devolução,
Expedição e Rastreamento. Nas outras seis o próprio dropdown já fechava o período. Nas quatro, na
fase de captura, todo clique fora do popover o fecha antes de qualquer outro menu abrir.
`teste_datas.py` varre as dez. **Lição:** a primeira conta dizia dez, por semelhança do código; a
prova do avesso feita em Entrada de Notas passou sem acusar nada, e só medindo tela por tela, sem o
conserto, o número certo apareceu. Conserto que não muda o resultado de teste nenhum não era
conserto.

Ficou de fora, com o usuário sabendo: cadastro de motivos de bloqueio, devolução ao fornecedor
(depende de NF-e), resolver vários bloqueios de uma vez, mover para endereço de Quarentena no ato
do bloqueio, abrir o histórico de um bloqueio já resolvido, e o excedente de nota ("chegou a
mais"), que depende da nota complementar.

## 14.52 Necessidades de Compra e Giro de Estoque: a conta que só olha o vendável (10/out/2026)

As duas telas nasceram juntas, de 31 prints do Olist e de quatro decisões do usuário, tomadas na
barganha antes de qualquer código.

**1. Lista viva, não relatório.** O Olist abre um formulário de filtros, espera o "gerar" e só então
mostra a tabela. Lá a conta roda no servidor e demora; aqui ela sai na hora, e o botão seria um
clique sem ganho. As duas telas seguem o padrão do sistema: indicadores no topo, busca e filtros na
barra, abas com contador, tabela e painel lateral. Os filtros do dia a dia ficam na barra (loja,
depósito, fornecedor); os de cálculo ficam no painel **Filtros e cálculo**, e o botão mostra quantos
ajustes estão fora do padrão. O conteúdo dos prints está todo lá; o que mudou foi o lugar.

**2. Só o vendável conta como estoque.** Vendável é disponível mais o que aguarda endereço.
Reservado já tem dono e bloqueado não pode ser vendido: contar os dois escondia a necessidade de
compra. O **projetado** é o vendável, mais o que está chegando (em conferência, a receber de ordens
de compra e em trânsito entre depósitos), menos os pedidos que ainda vão sair. A compra é sugerida
quando o projetado cai abaixo do mínimo, e a quantidade leva o estoque até o máximo; sem máximo,
até o mínimo. No modo **dias de cobertura**, a sugestão cobre N dias da venda média.

São dois conceitos, e cada um tem a sua aba: **abaixo do mínimo** olha o vendável de hoje, e é a
mesma regra do aviso do Controle de Estoques (`abaixoDoMinimo`, que deixou de usar o físico);
**a comprar** olha o projetado. Um produto pode estar abaixo do mínimo e não precisar de compra,
porque a reposição já está a caminho. A suíte compara a aba com o aviso do Controle de Estoques, e
usa o caso que separa as duas regras: mínimo 8 para um produto com físico 9 e dois bloqueados.

**3. O painel cria a ordem.** A seleção em massa abre o painel **Ordem de compra**, com um bloco
por fornecedor padrão. Produto sem fornecedor padrão cai num bloco próprio, e o fornecedor se
escolhe ali. Blocos com o mesmo fornecedor viram uma ordem só. Nada nasce pela metade: um bloco
inválido trava todos. A ordem nasce em aberto, com o custo médio como preço, e aparece em Ordens de
Compra, que lê a chave `deskOrdensGeradas`. Excluir ou cancelar a ordem lá a tira dessa chave, e a
necessidade volta aqui. O que foi pedido passa a contar como "chegando", então a mesma compra não é
sugerida duas vezes.

**4. O giro avisa na compra.** O "aplicar tags" do Olist não existe aqui (§12.1). No lugar, a
classificação do giro entra na conta: produto em **encalhe** que cai abaixo do mínimo aparece na
aba **Segurados pelo giro**, sem quantidade sugerida e com o motivo na linha. Não é trava: digitar a
quantidade é a decisão de comprar mesmo assim. As faixas são parâmetro da empresa
(`giroEncalheAte`, `giroBaixoAte`), e o período do giro também (`giroJanelaDias`). A régua da tela
do Giro simula outras faixas sem mudar nada; só "Salvar faixas" grava.

**Mínimo e máximo se editam no painel, não na linha.** O print do Olist edita os dois na própria
tabela. Aqui vale "a listagem lê, o detalhe escreve": a linha mostra, e o painel da conta do produto
edita. O novo mínimo fica em `deskMinMax`, que o Controle de Estoques lê.

**Um bloco de dados, duas telas.** Produtos, ficha de compra, movimento de vendas e entradas e a
função do giro moram num bloco que é igual, letra por letra, nas duas telas. `PRODUTOS` é espelho do
Controle de Estoques. O movimento usa datas relativas a hoje (`[dias atrás, quantidade]`), para o
período ter venda em qualquer dia que a tela abrir. A suíte compara o texto do bloco, o espelho de
produtos, o de ordens de compra e o de transferências, e confere que em nenhum dia do último ano o
saldo de um produto fica negativo.

**O que nasceu junto, porque as telas dependem:** o **fornecedor padrão** no cadastro do produto
(coluna Padrão, botão de opção da casa; enquanto houver fornecedor, um é o padrão) e a seção
**Compra e giro de estoque** em Parâmetros de estoque, com quatro parâmetros no mesmo dia do código
que os lê. No caminho saiu um defeito antigo do cadastro do produto: adicionar um fornecedor
redesenhava a tabela a partir da lista e apagava o nome digitado nas outras linhas.

**A tabela precisa caber no card a 1440px.** A primeira versão tinha onze colunas em linha única e
empurrava a coluna Comprar, que é a que importa, para fora da área visível. O cabeçalho passou a
quebrar em duas linhas, como no print, e as colunas de texto deixaram de ser `nowrap`. A suíte mede
a largura da tabela contra a do card, nos dois temas, e a posição do campo Comprar.

**Três coisas que a suíte ensinou sobre o próprio teste:**

- `inner_text` devolve o texto **desenhado**: cabeçalho e etiqueta em maiúsculas pelo CSS chegam em
  maiúsculas, e texto dentro de bloco escondido não chega. Para comparar o que está no documento,
  `text_content`.
- `page.evaluate` **executa** a expressão quando ela devolve uma função. Trocar `window.print` por
  uma função espiã, numa linha solta, contava uma impressão a mais. A troca vai dentro de uma função.
- A linha pedida pode estar na segunda página da lista. O ajudante da suíte passa para 25 por página
  quando não a encontra, em vez de falhar com erro de elemento nulo.

**O que o portão pegou antes da entrega:**

- **Na impressão, o campo Comprar saía como caixa preta.** A regra de impressão tirava o fundo do
  campo, mas a regra da tela vinha depois dela no arquivo e ganhava. No tema escuro, o número que
  mais importa no papel ficava ilegível. A regra de impressão passou a usar `!important`, o texto
  de toda a área impressa sai escuro, e o menu lateral deixa de ocupar a margem. A suíte mede o
  fundo e a cor do campo com a página em modo de impressão.
- **A auditoria leu um `id` repetido** onde havia dois trechos de código iguais montando `id` a
  partir de uma variável com o mesmo nome. Não era defeito na tela, mas a checagem é por texto: o
  segundo ajudante mudou o nome da variável.
- **Chave nova de armazenamento precisa ser registrada.** A auditoria reprovou `deskMinMax` no
  Controle de Estoques, e estava certa: a lista de depósitos compartilhados existe para que tela
  nenhuma guarde estado por conta própria sem alguém decidir. As duas chaves novas entraram na
  lista, com o motivo.

**Provado nos dois sentidos.** Sete defeitos injetados, um por vez, e a suíte reprovou os sete: o
aviso de mínimo de volta ao físico; o bloqueado contando como vendável; o encalhe sem segurar a
sugestão; um dado diferente só no Giro; Ordens de Compra sem devolver a ordem cancelada; a ordem
sem fornecedor passando na validação; e a regra de impressão sem o `!important`.

Ficou de fora, com o usuário sabendo: tags; natureza de operação (fiscal, depende da NF-e); prazo de
entrega do fornecedor, que não existe no cadastro; a página de detalhe da ordem criada, que ainda
abre o exemplo fixo; e os pedidos que vão sair, que são dado de exemplo da própria tela. O kit entra
na compra como produto comum, porque a composição de kit ainda não existe.

## 14.53 A tela dentro do sistema: a primeira leva de melhorias dos módulos prontos (10/out/2026)

O usuário pediu uma varredura das telas prontas: o que o painel lateral mostra, o que poderia
mostrar, o que dá para ligar e o que se repete. As 80 telas foram abertas uma a uma, com clique em
cada linha, cada aba e cada item de menu. Todas passavam na auditoria, e o que apareceu não se vê
olhando um arquivo só. A lista está em `docs/melhorias-modulos-prontos.md`; o usuário aprovou
inteira e pediu para fazer por partes. Esta seção registra o que a primeira leva deixou de padrão.

**1. O link entre telas cai numa lista filtrada.** Bloco comum `BUSCA PELO ENDERECO`, igual em 30
listas: lê `?busca=` do endereço, solta o período padrão da tela (senão o registro antigo some),
preenche a busca e mostra a faixa "Lista filtrada por ...", com "Mostrar tudo". Quando o exemplo
daquela lista não tem o registro, a faixa diz isso, em vez de mostrar uma lista vazia sem
explicação. O link vai para a lista, e não para a página do registro, porque 11 páginas de detalhe
ainda abrem sempre o mesmo exemplo.

**2. Link só onde o destino tem o registro.** Os dados de exemplo de cada tela nasceram separados.
Antes de ligar duas telas, confere-se que o valor existe do outro lado: o número da ordem de compra
nas notas, o nome do cliente entre Pedidos, Separação, Conferência de Saída e Clientes, o número do
pedido entre Devolução e Rastreamento. Os painéis de Fornecedores e de Produtos ficaram de fora por
isso: o cadastro tem outros fornecedores e outros produtos, diferentes dos do estoque.

**3. Imprimir e baixar planilha são um bloco só.** `PLANILHA E IMPRESSAO DA TELA`, igual em 20
listas. A tela declara três coisas: `PLANILHA_NOME` (o nome do arquivo), `PLANILHA_REFAZ` (a função
que redesenha a lista) e `PLANILHA_PAGINA` (como ler e mudar a paginação dela, que tem nomes
diferentes de tela para tela). O bloco tira a paginação, lê a tabela inteira com os filtros da tela
e devolve a paginação. A primeira versão supunha `renderTabela` e quebrou quatro telas que usam
`render`; daí o adaptador. Tela com coluna que não é texto define `linhasDaPlanilha()`.

**4. Menu só com o que funciona.** 33 itens só mostravam um aviso ("entra junto com Relatórios") e
12 fechavam o menu sem fazer nada. Saíram os que não têm como funcionar agora (importar planilha,
buscar nota na Sefaz, vale-troca); os de imprimir e exportar passaram a usar o bloco comum. O
"Imprimir" do topo saiu de cinco telas que já o tinham no menu.

**5. Duas telas com os mesmos dados são um módulo com duas visões.** Metas e Performance de Vendas
viraram **Metas e Performance**: um item no menu, o mesmo título e um seletor no topo. Continuam
dois arquivos; o seletor navega de um para o outro levando mês, ano e nível no endereço.

**6. Número em duas telas tem uma dona.** O Dashboard dizia R$ 312.480,00 em estoque, e o Controle
de Estoques soma R$ 81.103,75; trazia a Cadeira Ergonômica com 5 unidades, e o estoque tem 24;
punha a Luminária entre os mais vendidos, e o Giro a classifica como encalhe. Os três foram
alinhados ao estoque, e a suíte compara. O painel de Clientes lê um espelho declarado de Pedidos de
Venda (`PEDIDOS_DO_CADASTRO`), que a suíte também compara. A lista "O que precisa de você hoje", em
Boas-vindas, não traz quantidade em cada fila, de propósito.

**7. Quadro com `data-href` leva à tela de origem.** Bloco `QUADRO QUE LEVA A TELA DE ORIGEM`, no
Dashboard e em Boas-vindas: o quadro inteiro é clicável e alcançável pelo teclado; botão dentro
dele continua fazendo o que fazia.

**Os defeitos que a varredura achou.** Duas notas de devolução da Conferência de Entrada tinham o
mesmo identificador de duas notas de compra, e clicar numa abria o painel da outra: a lista foi
acrescida sem continuar a numeração. A página do Pedido mandava `PEDIDO.id` para a Separação, e o
campo se chama `numero`: o link saía com `undefined`. E cinco telas ainda diziam que algo só
funcionaria numa ferramenta que já tinha saído do projeto.

**O que virou verificação.** Na auditoria do projeto: checagem **11** (identificador repetido numa
lista de exemplo) e **12** (tela que cita a ferramenta que saiu do projeto). Suítes novas: `teste_planilha.py`
(todo item de "Mais ações" navega, abre algo, baixa ou imprime; a planilha leva a lista inteira; o
bloco é igual em todas as telas) e `teste_trilha.py` (a busca pelo endereço, os links de cada
painel caindo no registro certo, os indicadores do Controle de Estoques batendo com a lista).

**Provado nos dois sentidos.** Oito defeitos injetados, um por vez, e os oito foram pegos: o
identificador repetido de volta; o aviso citando a ferramenta que saiu; a planilha levando só a página visível;
um item de menu sem ação em Clientes; a busca pelo endereço sem soltar o período; a ordem de compra
de volta a texto; o Pedido mandando `id`; e o seletor de visão sem levar o mês.

**O que mudou no modo de construir.** As duas skills do ERP ganharam o que a varredura ensinou: a
seção "Tela nova nasce ligada: o mapa de vizinhança", que se responde antes de desenhar a tela, e
"A tela dentro do sistema", que o portão de QA confere antes de entregar.

Ficou para as próximas levas, com o usuário sabendo: Finanças inteira (F1 a F4), os painéis dos
outros cadastros (C2 a C8), os indicadores de Ordens de Compra, Pedidos e Contas, a página de
detalhe abrir o registro clicado (G3), e a segunda varredura, do miolo de Inventário, Acerto e PDV.

## 14.54 O que o usuário devolveu ao testar a primeira leva (12/out/2026)

O usuário testou a leva do §14.53 e voltou com uma lista. Nenhum item era gosto: cada um apontava
uma regra que a primeira leva tinha deixado pela metade. Esta seção registra a regra de cada um.

**1. Conserto de componente vai para todas as telas.** O popover de período ficava aberto por baixo
do filtro vizinho. Isso tinha sido consertado em 10/out, em seis das doze telas que têm o popover;
o usuário achou uma das outras seis. O bloco `O POPOVER DE PERIODO FECHA QUANDO OUTRO MENU ABRE`
está agora nas doze e vale nos dois sentidos: abrir outro filtro fecha o período, e abrir o período
fecha o outro filtro. A suíte varre toda tela que tem o popover, e não uma lista de nomes.

**2. "Incluir" abre em branco.** O botão "Incluir ordem de compra" abria a ordem nº 2 de exemplo. O
mesmo defeito estava nos cinco cadastros com página própria (Clientes, Fornecedores, Lojas Desk,
Produtos e Vendedores), que abriam o registro de exemplo em modo de edição. As seis páginas passam a
abrir vazias no `?novo=1`, com o título "Novo ..." e sem as ações de registro que já existe.

**3. Lista numerada abre do nº 1 para o maior.** Ordens de Compra e Pedidos de Venda. As filas, que
abrem pelo que espera há mais tempo, ficaram como estavam.

**4. Necessidades de Compra abre no que falta comprar.** A tela abria em "Todos", e o produto com a
ordem recém-gerada continuava na lista, parecendo pendente. Ela passa a abrir em "A comprar": gerada
a ordem, o produto sai. Quem chega por link com busca vê "Todos". Em "Todos", o produto já pedido
diz em que ordem está. E digitar a quantidade com Enter marca o produto; zerar desmarca.

**5. Quanto o cliente deve é número de Contas a Receber.** O painel do cliente calculava a dívida
pelos pedidos, e Contas a Receber tinha outros títulos: o título em aberto da Marina Duarte apontava
para o pedido nº 15, cancelado. O título passou para o pedido nº 1, o nº 15 virou o título
cancelado, o da Tech Solutions passou a ser o do pedido nº 2 (o mesmo erro estava espelhado no
CRM), e o painel do cliente lê um espelho dos títulos com saldo (`TITULOS_DO_CADASTRO`). A regra que
a suíte guarda: pedido cancelado não tem título em aberto, e o painel diz o que a tela dona diz.

**6. Concluir volta para a fila, e o que foi feito fica guardado.** A ficha da Separação ficava
aberta depois de concluir, e "Devolver este pedido para a fila" só explicava que não podia. A ficha
passa a gravar o que fez na chave `deskSeparacao` (bloco comum `O QUE A FICHA JA FEZ COM O PEDIDO`,
igual na fila e na ficha) e a voltar para a fila, que mostra uma faixa com o que aconteceu. Devolver
funciona nos dois casos: em andamento, libera o pedido; concluído, reabre, com a senha de reabertura
e registro. A auditoria passou a enxergar chave de armazenamento guardada em constante.

**7. Etapa que passou não volta.** A Conferência de Saída oferecia "Ver na Separação". Saiu: nas
filas do galpão o pedido só avança. O acompanhamento mora no Pedido de Venda, que mostra Separação,
Conferência de Saída e Expedição como "ainda não chegou", "em andamento" ou "concluída", e leva
para a ficha daquele pedido (`?id=N&de=pedido`). A ficha ganha "Voltar para o pedido de venda"
quando a pessoa veio de lá.

**8. Um assunto, uma página.** O seletor que trocava entre Metas e Performance de Vendas foi
recusado: "não teve muito ganho". A tela de Performance deixou de existir. Metas e Performance é uma
lista com as colunas juntas (meta, realizado, atingimento, ritmo, vendas com ticket, devolução e
situação), seis indicadores, e o painel lateral com a meta, como vendeu, a comparação com o mês e o
ano anteriores e o botão "Definir meta" ou "Editar meta". São 80 telas.

**9. Todo controle da tela faz alguma coisa.** No Dashboard, os botões 5/10/15/20 só trocavam de
cor. Agora mostram mais itens, e quando o exemplo tem menos que o pedido a lista mostra todos e diz
isso. "Mais Vendidos" lê as unidades vendidas em 30 dias do Giro de Estoque, e "Alertas de Estoque",
o que Necessidades de Compra tem abaixo do mínimo. Clicar numa loja em "Vendas por Loja" redesenha o
painel inteiro com os números dela, e clicar de novo desfaz; o quadro tinha virado link em 10/out, e
o link atropelava esse clique. Os valores financeiros por loja são fatia do total, e as três somam o
todo.

**10. Quadro novo é quadro próprio.** "O que precisa de você hoje" estava pendurado embaixo dos
atalhos de Boas-vindas. Virou um quadro de lado a lado, em três colunas (entrada e estoque, saída dos
pedidos, financeiro), com a quantidade de cada fila lida da aba da tela dona. Os atalhos ganharam
dois botões e fecham na altura da agenda.

**11. A ferramenta de construção saiu do texto.** O usuário pediu para apagar toda menção a ela, em
todas as pastas. Nas telas eram 211 comentários de código; viraram "sistema de producao". A checagem
12 da auditoria passou a reprovar qualquer menção numa tela, comentário inclusive. A hospedagem ficou
decidida (Cloudflare Pages e Supabase; nada criado ainda) e está na seção 2 do roteiro.

**Provado nos dois sentidos.** Quinze defeitos injetados, um por vez, contra `teste_retorno.py`.
Catorze foram pegos de primeira. O do filtro de período passou: o teste abria o primeiro dropdown
da tela, o "Mais ações", que fecha o período por outro caminho, e não o filtro de depósito, que era
o do defeito. O teste passou a conferir todos os filtros de cada tela (46 pares em 11 telas), e
pegou. É o mesmo erro do item 1, do lado do teste: conferir um caso e dar a família por conferida.

**Analisado e deixado para depois, a pedido do usuário:** a impressão. A folha de hoje é o desenho
da tela sem o menu: ainda leva a caixa "Selecionar todos", a seta de ordenação e o espaçamento de
tela, e não leva título com data, filtros nem cabeçalho repetido por página. O formato de relatório
entra no bloco comum de impressão, e por isso chega às 20 listas de uma vez.

**Continua sendo dado de exemplo:** os títulos de Contas a Receber não batem todos com os pedidos
(valor e cliente de quatro deles); a Expedição tem pedidos que o Pedido de Venda ainda dá como em
separação; e o pedido separado numa tela não aparece sozinho na fila da Conferência de Saída.

## 14.55 O quadro não cresce, e os vizinhos fecham na mesma altura (12/out/2026)

O usuário testou o §14.54, deu ok em sete dos nove pontos e devolveu dois, os dois no Início.

**O quadro não muda de tamanho com o conteúdo.** No Dashboard, pedir 10, 15 ou 20 itens esticava
"Mais Vendidos" e "Alertas de Estoque", e os quadros vizinhos da linha se deformavam junto. A lista
passou a ficar presa na altura com que a tela abre, a dos 5 primeiros itens, e o resto rola por
dentro dela (`.lista-rolavel`). A altura é **medida**, e não fixa em CSS: nome comprido quebra em
duas linhas, e um número fixo cortaria o quinto item. Ela é medida de novo quando a fonte termina de
carregar e quando a janela muda de largura; a primeira versão media antes de a fonte chegar e
deixava 27px do quinto item de fora. A nota "Mostrando os 6 que há..." vai dentro da lista, como
última linha: fora dela, voltava a esticar o quadro.

**Quadros lado a lado fecham na mesma altura.** Em Boas-vindas a agenda tinha 493px e os atalhos,
498. A linha passou a esticar os dois (`align-items:stretch`), o rodapé da agenda desce para o pé do
quadro e os atalhos ocupam a altura toda. A suíte mede a diferença, e ela é zero.

**Nome de quadro é formal.** "O que precisa de você hoje" virou **Pendências do Dia**, no tom dos
vizinhos ("Agenda de Hoje", "Atalhos Rápidos").

Provado nos dois sentidos: três defeitos injetados (a altura destravada, a linha sem esticar e o
nome antigo), e os três foram pegos. Com os quinze do §14.54, são dezoito.

## 14.56 Finanças: a conta ao lado, a origem com link e os indicadores que filtram (12/out/2026)

Os itens F1 a F4 da lista de melhorias, aprovados em 10/out. Entrou junto o terceiro acerto do
Dashboard: as listas roláveis ficaram sem barra de rolagem à vista (`scrollbar-width:none`), e a
altura travada passou a arredondar para cima, porque com o zoom do navegador meio pixel de sobra já
fazia a lista de 5 itens rolar.

**O painel da conta (F1).** Em Contas a Pagar e em Contas a Receber o clique na linha saía da lista
e abria a página da conta. Passou a abrir a conta ao lado, no padrão das outras listas: situação com
o prazo ("atrasada há 2 dias", "vence em 6 dias"), valor, pago e saldo, os dados, de onde veio, os
pagamentos, e os botões da situação: "Pagar" ou "Receber" só quando há saldo, "Abrir a conta"
sempre. O botão de baixa reaproveita o painel de pagamento que a lista já tinha. A seta que expande
a linha no lugar e a caixa de seleção continuam fazendo só o que faziam.

**A origem com link (F2), e o exemplo alinhado antes.** As contas a pagar do exemplo tinham outros
fornecedores e outros documentos, diferentes dos da Entrada de Notas: não havia nota para onde levar.
Em vez de ligar a um registro que não existe, nasceram três contas de notas que a Entrada de Notas
tem como lançadas (6614, 736 e 4482), com o mesmo fornecedor, o mesmo valor e a mesma ordem de
compra. A conta leva à nota e à ordem; a nota ganhou "Ver a conta desta nota" (`NOTAS_COM_CONTA`,
espelho que a suíte compara); nota sem ordem diz "nota sem ordem vinculada"; conta lançada à mão diz
que não veio de nota. A conta a receber leva ao pedido e ao cadastro do cliente.

**Indicador que filtra é filtro de alternar (F3).** Quatro indicadores em cada lista: vencidas,
vencem hoje, próximos 7 dias e total. Eles somam o ano inteiro, sem a busca e sem o período da
lista. Clicar num deles limpa os outros filtros e ajusta o período e a aba, e a lista passa a
mostrar **exatamente** as contas que ele somou; ele fica aceso enquanto a lista é a dele. Clicar de
novo desfaz, e mexer na aba ou no período à mão apaga o indicador. O de total precisou de um filtro
próprio (`soEmAberto`), porque nenhuma aba junta "em aberto" e "atrasadas". O filtro de período
ganhou a opção "Vencem hoje".

**A origem do lançamento no Caixa (F4).** A baixa já gravava a origem como "CP 6" ou "CR 3". Virou
link para a página da conta; os dois pagamentos do extrato de exemplo que são baixa de conta a pagar
ganharam a origem. Transferência e lançamento à mão continuam sem link.

**Provado nos dois sentidos.** A suíte `teste_fin_melhorias.py` passou inteira na primeira rodada,
o que não prova nada. Dez defeitos injetados, um por vez, e os dez foram pegos.

Ficou de fora, com o usuário sabendo: os valores e clientes de quatro títulos de Contas a Receber
ainda não batem com os pedidos (item X1), e o fornecedor das contas a pagar não é link, porque o
cadastro de Fornecedores tem outros nomes.

## 14.57 A venda: o caminho inteiro no pedido, os indicadores e o balcão que aparece (12/out/2026)

Itens V2, V3 e V5 da lista de melhorias. V4 e L4 ficaram de fora, e o motivo está no fim.

**O acompanhamento mora no documento de origem (V2).** A página do pedido ganhou o quadro
"Acompanhamento", com seis paradas: Separação, Conferência de Saída, Expedição, Rastreamento, Contas
a Receber e Devolução. Cada uma diz se o pedido ainda não chegou nela, se está nela ou se já passou;
só vira link a etapa alcançada. O menu tinha "Acompanhar no galpão" e "Acompanhar na bancada", cada
um visível numa situação só; saíram, porque a mesma ação não aparece duas vezes na tela. "Ver conta
a receber" abria o financeiro do cliente num painel, e passou a se chamar "Financeiro do cliente".

**Indicadores em Pedidos de Venda (V3).** A aprovar, a faturar, atrasados para entrega e vendido em
30 dias, no mesmo padrão de Finanças: filtro de alternar, aceso enquanto a lista é a dele.

**A venda de balcão aparece (V5).** O PDV já guardava as vendas na chave `deskPdv`. Pedidos de Venda
passou a ler dali: a venda entra como "PDV-0001", já entregue, com os itens no painel, e na ordem do
número vem depois dos pedidos numerados (campo `seq`). O dinheiro recebido na hora vai para o Caixa
de Finanças pelo mesmo depósito que a baixa de contas usa (`deskCaixaExtras`), com a origem ligada
ao pedido; a tela do PDV já dizia "aparece no Caixa", e não aparecia. A conclusão da venda ganhou o
link para o pedido.

**Estado que a lista usa na abertura nasce antes da lista.** A primeira versão dos indicadores
declarava `filtroKpi` no bloco dos indicadores, mais abaixo no arquivo, e a lista é desenhada uma
vez antes dele: a tela abria com erro e sem indicador nenhum. A auditoria estática deu a tela por
boa; quem pegou foi a suíte, abrindo a tela. A declaração subiu para junto das outras variáveis de
filtro. É o mesmo aviso do §14.5, de novo: `let` lido antes de existir.

**O nome de uma tela que saiu fica em texto.** "Performance de Vendas" continuava no checklist de
acessos do vendedor, nas Configurações do PDV e na conclusão da venda. Os três dizem "Metas e
Performance".

**Provado nos dois sentidos.** Onze defeitos injetados contra `teste_venda_melhorias.py`, um por
vez, e os onze foram pegos.

**Dois itens não entraram, pela regra de só ligar onde o destino tem o registro.** V4 pedia "ver os
pedidos do mês" a partir do painel de Metas: o realizado de cada loja é número próprio da tela, e a
lista de pedidos não fecharia com ele. L4 pedia, no Rastreamento, o link para a conta a receber e
para o romaneio: o Rastreamento usa outra numeração de pedidos e outros clientes. Os dois viraram
dependentes dos alinhamentos X4 e X5.

## 14.58 O estoque: indicadores na compra, a transferência ao lado e a origem do bloqueio (12/out/2026)

Itens E2, E8 e E10 da lista de melhorias, e um ajuste que o usuário pediu em Caixa e Bancos.

**Tabela que não cabe: quem cede é o texto.** A tabela do Caixa tinha barra de rolagem: o histórico
que a baixa de conta e o PDV gravam é comprido ("Liquidação de conta a receber — ..."), e as células
não quebravam de linha. O usuário sugeriu tirar o ano da data, já que a competência ao lado o mostra.
Entrou assim: a data vai como dia e mês, com a data inteira na dica; o histórico e a categoria
quebram de linha; e a largura mínima da tabela caiu de 900 para 760 px. Medida com um histórico
comprido, ela cabe em 1440, 1366 e 1280 de largura. Vale como regra para a próxima tabela apertada:
coluna de texto quebra, e dado que a coluna vizinha repete sai.

**Indicadores em Ordens de Compra (E2).** Valor em aberto, a receber em 7 dias, atrasadas e sem data
prevista, no padrão de Finanças e de Pedidos de Venda: filtro de alternar, aceso enquanto a lista é
a dele, e o total do rodapé fecha com o valor do indicador. "Em aberto" é a ordem que não foi
atendida nem cancelada, e cada uma cai numa faixa só. O exemplo não tinha ordem atrasada; a nº 6
passou a ter a entrega prevista para antes do "hoje" da tela.

**A transferência ao lado (E8).** A linha da Transferência Entre Estoques já tinha o cursor de
clique e não abria nada; os itens só apareciam dentro de "Confirmar recebimento", e transferência
recebida não tinha como ser vista. Clicar na linha abre o painel: situação, de onde saiu e para onde
vai, quem enviou e quando, quem recebeu, o tempo em trânsito e os itens com o enviado, o recebido e
o que ainda está a caminho. O botão da linha continua abrindo só o recebimento. Confirmar o
recebimento passou a guardar quem recebeu e quando, que é o que o painel mostra depois.

**A origem do bloqueio como link (E10).** No painel do item bloqueado, "De onde veio" leva à nota em
Entrada de Notas e à ficha do pedido na Separação e na Conferência de Saída. Duas notas do exemplo
não existiam em lugar nenhum ("NF-e 12.951" e "NF-e 13.240"); viraram as notas 4468 e 9051, que a
Entrada de Notas tem, no mesmo depósito do bloqueio. Acerto, devolução e bloqueio manual seguem em
texto, pela regra de só ligar onde o destino tem o registro: o Acerto não tem lista, e o exemplo de
Devolução tem outros produtos.

**A busca de uma lista olha mais de um campo.** A suíte pedia "uma linha só" ao buscar a nota 1182
em Entrada de Notas, e vieram duas: a busca também acha a nota 2301 por outro campo. O teste passou
a procurar a linha cujo número é o pedido. Fica o aviso para o próximo link por busca: o destino
pode trazer vizinhos junto do registro.

**Provado nos dois sentidos.** Dezoito defeitos injetados, um por vez, contra
`teste_estoque_melhorias.py` e a seção nova de `teste_fin_melhorias.py`, e os dezoito foram pegos.

**O exemplo mudou, e o navegador do usuário guardava o antigo.** No teste dele, a origem do Kit Home
Office abriu a Entrada de Notas buscando "951", com a lista vazia. Dois defeitos somados. A tela de
Itens Bloqueados guarda o próprio estado no navegador (`deskBloqueados`), com o exemplo dentro: quem
já a tinha aberto continuava com "NF-e 12.951", e a troca do exemplo no arquivo não chegava a ele. E
o link tirava o número dos dígitos do fim de qualquer texto, de onde saiu "951". Conserto: o número
só sai do documento escrito no formato que a tela de origem grava ("Nota 4468", "Pedido #23"), e
formato desconhecido fica em texto; e a troca das duas notas vale também para o estado guardado. A
suíte começava sempre com o navegador limpo, por isso não viu; agora abre também com o exemplo
antigo guardado. Regra que fica: **mudou o exemplo de tela que guarda o próprio estado, o teste abre
com o estado de antes da mudança**. Dois defeitos injetados contra as duas checagens novas, e os
dois pegos.

## 14.59 "Itens Bloqueados" passa a se chamar "Tratamento de Perdas" (12/out/2026)

Decisão do usuário, barganhada. O nome antigo dizia o estado da mercadoria e era o único item do
menu do Estoque que não era nome de atividade; o novo diz o trabalho, como Conferência,
Endereçamento e Reposição.

**Muda o nome da tela, e só ele.** O item do menu nas 80 telas, o título, o caminho e os textos das
outras telas que mandam para lá ("tratar em Tratamento de Perdas", "Abrir o Tratamento de Perdas",
"Estoque → Tratamento de Perdas").

**"Bloqueado" segue sendo o nome da situação do saldo.** O Controle de Estoques continua mostrando
"Bloqueado", a página do produto "bloqueado", e Pendências do Dia "itens bloqueados esperando
decisão". O botão "Bloquear item" e o painel "Resolver bloqueio" não mudam. O subtítulo da tela
amarra as duas palavras: "O que está bloqueado para venda e pode virar perda".

**O arquivo não muda de endereço:** continua `pagina-estoque-itens-bloqueados.html`, e a suíte
continua `teste_bloqueados.py`. As seções deste documento anteriores a esta data citam a tela pelo
nome que ela tinha.

**Guardado.** A seção 4 de `teste_estoque_melhorias.py` reprova se alguma tela voltar a dizer o nome
antigo, se o menu de alguma perder o item, ou se a situação do saldo deixar de se chamar
"bloqueado". Cinco defeitos injetados, um por vez, e os cinco pegos.

## 14.60 A chegada da transferência é uma conferência de entrada (12/out/2026)

Pedido do usuário, barganhado: "querendo ou não ela é uma conferência de entrada". O painel
"Confirmar recebimento" da Transferência Entre Estoques vinha com a quantidade enviada já preenchida;
bastava um clique, e ninguém precisava contar.

**Uma contagem só para tudo que entra.** A tela que confere a nota confere a transferência
(`pagina-estoque-conferencia.html?transf=TR-0101`): cega, com recontar ou confirmar, e motivo em toda
divergência. Mudam os nomes: "Qtde enviada" no lugar de "Qtde da nota", "Saiu de" e "Enviada em" no
lugar de fornecedor e ordem de compra, e nada de valor. O resumo mostra só as unidades contadas: o
total enviado ficaria à vista e entregaria a contagem cega.

**Do que não veio, a tela pergunta.** É a mesma pergunta que o fechamento da nota já fazia sobre o
saldo da ordem de compra, porque só quem recebeu sabe: "o resto ainda vem" deixa a diferença em
trânsito, e a transferência fica em "Recebidas em parte" até uma segunda conferência, que traz só o
resto; "faltou" manda a diferença para Tratamento de Perdas como falta a auditar e encerra a
transferência. Avaria que ficou conosco vai para lá como avaria; avaria que voltou com o
transportador, recusa na doca e item trocado seguem em trânsito.

**Concluir devolve a pessoa para a lista** (regra do §14.54): fechar leva à Transferência Entre
Estoques, que diz quanto entrou, o que faltou, o que veio avariado e o que segue na estrada. O painel
da transferência mostra quem recebeu e quando, e a falta e a avaria por item.

**A fila mostra a transferência.** Na Conferência de Entrada ela aparece como "Aguardando entrada",
com o depósito de origem no lugar do fornecedor, e segue os mesmos passos da nota: registrar a
chegada, iniciar a conferência. As colunas viraram "Documento" e "De onde vem", e o rodapé conta
"entradas". O rótulo "Transferência entre estoques" é fixo (atalho anotado no código); as outras
duas origens continuam vindo do catálogo de nomes.

**Como as telas conversam.** A transferência mora numa tela e é conferida em outra. Quem fecha a
conferência guarda o que apurou, item a item, na chave `deskTransferencias`; a lista, a fila e a
contagem leem dali por um bloco idêntico nas três ("O QUE A CONFERENCIA JA FEZ COM A
TRANSFERENCIA"). A fila e a contagem carregam um espelho das transferências a caminho, que a suíte
compara com a tela de origem. O número que chega pelo endereço (`?transf=`) só vale no formato de
número de transferência; fora disso é ignorado, e número que não existe abre uma tela que diz isso.

**A senha é a de antes.** Fechar a conferência da transferência pede a confirmação que o recebimento
já pedia (`transfRecebe`). No catálogo das 79 telas ela passou a se chamar "Fechar conferência de
chegada de transferência", em Estoque → Conferência de Entrada.

**O que saiu.** O painel de recebimento e o código dele. `PRODUTOS` e `BASES` ficaram sem uso na
tela de Transferência, com um comentário dizendo isso, para a limpeza de código das telas.

**Quatro coisas que a construção ensinou.**

- *Texto de opção se mede no lugar onde abre.* O rótulo "Faltou (vai para Tratamento de Perdas, como
  falta a auditar)" saía do painel lateral. O rótulo encurtou, a explicação foi para a frase de cima,
  e a suíte mede se o menu cabe no painel.
- *Ensaiar numa cópia.* As quatro edições foram escritas como roteiros, aplicadas numa cópia das
  telas fora do projeto e testadas ali por `file://`, enquanto a verificação da entrega anterior
  ainda rodava. Chegaram ao projeto já passando.
- *Título em caixa alta engana o teste.* `inner_text` devolve o texto como a pessoa vê; título que o
  CSS põe em maiúsculas chega em maiúsculas, e uma checagem de "não contém Comunicado" passava sem
  olhar nada. Onde o estilo muda a caixa, a suíte lê o conteúdo do elemento.

- *O resultado do selo se lê do selo.* A primeira rodada completa parou com a suíte do CRM passando
  do tempo limite (sozinha ela fecha em 75 segundos: foi travamento passageiro), e o comando tinha
  sido encadeado com um corte da saída, que devolve "sucesso" mesmo quando o selo falha. A segunda
  rodada guardou o código de saída do próprio selo, e foi ele que mostrou a auditoria reprovando: os
  dois painéis de fechamento (o da nota e o da transferência) montavam botões com o mesmo
  identificador. Os da transferência ganharam nome próprio.

**Provado nos dois sentidos.** Vinte e três defeitos injetados, um por vez, contra
`teste_transf_conferencia.py` (74 asserções), e os vinte e três foram pegos.

**Fica como dado de exemplo.** A conferência não mexe no saldo das outras telas: Necessidades de
Compra segue contando a transferência como "a caminho", e o Controle de Estoques não recebe as
unidades. Transferência criada em "Nova transferência" continua não entrando na lista.

## 14.61 Tratamento de Perdas: o zero é resposta, e o motivo é o da operação (12/out/2026)

Pedido do usuário depois de testar a conferência da transferência, com print do painel "Resolver
bloqueio".

**Campo onde zero é resposta abre em branco.** Os campos "Volta para a venda" e "Baixa por perda"
mostravam um "0" cinza de exemplo. Parecia valor: ele confirmou com o "0" na tela e foi barrado. O
exemplo saiu. Vazio é "não respondi"; zero digitado é resposta. O mesmo "0" estava no campo
"Quantidade que você achou" da ficha da Separação, onde a tela já dizia que "zero é uma resposta
válida"; saiu de lá também. Os outros campos com "0" de exemplo são de formulário (estoque mínimo,
quantidade a bloquear), onde zero não é uma decisão, e ficaram.

**Zero em "Volta para a venda" quer dizer que nada foi recuperado.** A linha inteira vai para a baixa
por perda, a tela diz o que entendeu ("Nada voltou para a venda: 2 UN vão para a baixa por perda.
Informe o motivo.") e pede o motivo. A baixa posta assim acompanha o zero: se ele vira outro número,
ela volta a ficar em branco; corrigida à mão, passa a ser da pessoa e não some mais. Zero nas duas
saídas não resolve nada, e a mensagem manda para a aba "Manter bloqueado".

**O motivo da perda é o da operação que criou o bloqueio.** A baixa oferecia sempre os sete motivos
do Acerto de Estoque. Agora vêm primeiro os da operação, e depois os gerais:

| de onde veio o bloqueio | motivos |
|---|---|
| transferência entre estoques | Perda em trânsito · Avaria no percurso · Furto ou roubo no trajeto |
| conferência de entrada (nota) | Avaria do fornecedor · Avaria no recebimento · Avaria no transporte da compra |
| separação e conferência de saída | Avaria na separação · Avaria no picking · Avaria na embalagem · Não encontrado no endereço |

Bloqueio manual, de acerto ou de devolução não tem operação, e segue só com os gerais. A
transferência chega pela conferência de entrada; quem a distingue da nota é o número ("TR-0101").

**O motivo é cadastro, não texto de tela.** Os dez motivos novos moram em Configurações → Motivos de
Perda, com o campo novo "Em que baixa o motivo aparece" (todas as baixas, ou uma operação só), que a
lista mostra e o formulário edita. Tratamento de Perdas carrega um espelho, que a suíte compara. O
Acerto de Estoque continua oferecendo só os de todas as baixas. A opção menor era deixar os motivos
escritos no painel; ficou no cadastro porque é lá que o usuário troca nome e cria outros.

**Provado nos dois sentidos.** Quinze defeitos injetados, um por vez, contra `teste_perdas_baixa.py`
(40 asserções), e os quinze foram pegos.

## 14.62 Tratamento de Perdas: o resolvido abre painel, e o cadastro de motivos vale na baixa (13/out/2026)

Dois pontos do usuário, com print da aba Resolvidos.

**Linha de histórico também abre painel.** A linha dos Resolvidos não abria nada. Agora abre "Bloqueio
resolvido": quantidade, valor (da perda ou que voltou), quantos dias ficou parado, depósito; de onde
veio (com o link), quem bloqueou e quando, quem liberou ou baixou e quando; na liberação, o que a
auditoria achou e para onde voltou; na baixa, o motivo, o acerto de saída e o que ela obriga; e a
história do bloqueio, com as anotações. O painel só lê.

**Para contar a história, o registro precisa guardá-la.** A resolução passou a levar a data do
bloqueio, quem bloqueou, a observação e as anotações. Resolvido guardado no navegador antes desta
data não tem isso: quando o bloqueio ainda está na fila, a data sai dele; quando já saiu, o painel
diz "não registrado" e não inventa. A suíte abre com esse estado antigo. O exemplo citava o pedido
19, que a Conferência de Saída não tem; virou o 25, e a troca vale também para o guardado.

**O cadastro de motivos vale na baixa.** O usuário perguntou se os motivos iam para Configurações,
"para podermos fazer esses cadastros". Já estavam lá, mas o cadastro vivia só na tela dele, até
recarregar. Agora o que é criado, alterado, inativado ou excluído em Motivos de Perda fica guardado
(`deskMotivosPerda`), e a baixa de Tratamento de Perdas oferece o que o cadastro diz: primeiro os da
operação, depois os de todas as baixas. Enquanto ninguém mexe no cadastro, valem os espelhos.
Cadastro guardado ilegível não derruba a tela. A lista do Acerto de Estoque continua fixa, e o
formulário do cadastro diz isso.

**Três avisos da construção.**

- *Dois painéis na mesma tela não repetem identificador.* Aconteceu pela segunda vez em dois dias: o
  painel novo reaproveitou `linkProduto` e o mesmo trecho de montagem do vizinho. A auditoria estrita
  pegou. Painel novo nasce com prefixo próprio nos identificadores.
- *Mutação que a correção desfaz não é defeito.* Voltar o exemplo para "Pedido #19" não reprovou
  nada: a correção do guardado conserta ao abrir. O defeito de verdade era perder essa correção, e é
  ele que a prova injeta.
- *Duas sessões no mesmo repositório.* Outra sessão construía a tela Movimentação de Estoque e
  alterou o menu das 80 telas no meio desta entrega. Daqui saiu só o que era desta entrega: nos dois
  arquivos em comum, o commit levou os trechos desta entrega e deixou a linha de menu da outra
  sessão para ela commitar. O selo completo não foi rodado, e o `selo.json` não foi commitado.

**Provado nos dois sentidos.** Nove defeitos injetados, um por vez, contra as seções 4 e 5 de
`teste_perdas_baixa.py` (54 asserções na suíte), e os nove foram pegos.

## 14.63 Movimentação de Estoque: o histórico do produto, só para consulta (13/out/2026)

Pedido do usuário em 12/out, com quatro prints de um kardex de outro sistema e a descrição do que
queria: o histórico individual de cada produto, com estoque atual, reservado e disponível, e todas
as movimentações desde a primeira entrada; uma tela inicial simples, só com os filtros; e, ao clicar
num movimento, o pedido inteiro que o gerou. Ele reforçou no meio da construção que os prints eram
só a noção do conteúdo: arquitetura e estilo são os nossos.

**O mapa de vizinhança, respondido antes de desenhar.**

| pergunta | resposta |
|---|---|
| de onde vem e para onde vai | de Controle de Estoques ("Mais ações"), da página do produto (botão "Movimentações") e do painel do Giro; volta para a página do produto e para o Giro, no mesmo produto |
| que número divide | saldo por depósito e custo médio são do Controle de Estoques; vendas e entradas do período são as do Giro |
| o exemplo conversa | sim, por construção: a tela carrega o bloco comum de compra e giro, e não tem compra nem venda próprias |
| que cadastro e parâmetro lê | depósitos e produtos do bloco comum, e itens por página de Interface do usuário. Nenhum parâmetro novo |
| ações do menu | nenhuma grava. Buscar, limpar, resumo por tipo, imprimir a lista, baixar planilha e imprimir o documento |
| o que o print tem | filtros, quadro de saldos, lista de movimentos, sintético por tipo e o documento com itens. O que ficou de fora está abaixo |
| que tela repete | a aba "Lançamentos" da página do produto. Ver "A decisão que ficou com o usuário" |
| depois da ação principal | Buscar mostra o produto, os indicadores e a lista; o filtro só vale quando se busca de novo |
| etapa do fluxo | nenhuma: é consulta, não fila |

**A tela não tem dado próprio de compra e venda.** O `MOVIMENTO` do bloco comum (dias atrás e
quantidade, por produto) já existia para o Giro e para Necessidades de Compra. A tela nova carrega o
mesmo bloco, o terceiro texto idêntico, e deriva dele o histórico. O bloco ganhou uma linha, nas
três telas: a função que liga o menu "Mais ações" passou a prever a tela que não tem o menu, que é o
caso desta; sem a guarda, a auditoria do projeto reprovava a tela nova. O saldo de partida é o saldo de
hoje menos tudo que o histórico moveu, a mesma conta que o Giro faz em `saldoHa`. Daí saem as três
igualdades que a suíte confere: a última linha de cada produto, em cada depósito, é o físico do
Controle de Estoques; o custo médio da última linha é o de lá; e vendas, entradas e saldo de partida
de um período são os do Giro.

**O que o bloco comum não guarda é montado na tela, sempre do mesmo jeito.**

- **Depósito.** Compra e venda acontecem no depósito de maior saldo do produto. O saldo dos outros
  depósitos chegou por transferência, que não muda o total; a venda de balcão sai do depósito da loja.
- **Documento.** Mesma loja no mesmo dia é um pedido só; mesmo fornecedor no mesmo dia é uma nota só.
  É o que faz o documento ter outros itens. No exemplo são 372 documentos, 19 com mais de um produto.
- **Custo médio.** Média móvel: só a compra muda. As notas antigas entram 1% mais baratas a cada
  passo, e o custo da última é calculado para a média fechar exatamente no custo médio do Controle
  de Estoques. Nenhuma nota fica a mais de 10% dele.
- **O que o Giro não conhece** (devolução que virou perda, acerto corrigido, inventário que achou num
  depósito o que faltava no outro) soma zero por produto e por dia. O saldo de cada dia continua o
  que o Giro calcula.

**Filtrar esconde linha, não refaz saldo.** O saldo anterior e o atual de cada linha são os do
histórico inteiro do produto naquele depósito. Com o filtro de tipo ou de data, a linha continua
mostrando o saldo que tinha de verdade; o que estava antes do período aparece como "saldo antes".

**O painel do documento abre mais largo** (860px contra 620px), porque leva tabela de itens. O
resumo por tipo usa a largura normal. É o mesmo painel lateral, com uma classe a mais.

**Imprimir o documento manda só o documento para o papel.** Uma marca no corpo da página, posta só
durante a impressão, esconde tudo que não é o painel e solta o painel na folha, sem fundo e com texto
escuro. A impressão foi vista saindo do tema escuro.

**O documento não é link para a tela de origem.** A regra da casa é não criar link que cai em lista
sem o registro, e os documentos do histórico não existem no exemplo de Entrada de Notas, de Pedidos
de Venda nem da Transferência. A primeira versão tinha o link; saiu no portão de qualidade. O painel
mostra o documento inteiro, que é o que o usuário pediu.

**A lista abre do mais antigo para o mais novo**, como ele pediu ("até chegar na situação atual").
Clicar em "Data e hora" inverte, e a primeira linha passa a ser a de hoje.

**Cabe em 1440, 1366 e 1280.** Abaixo de 1440 quem cede é o texto: o nome do movimento quebra de
linha, a unidade sai da coluna do saldo (já está nos indicadores) e as duas datas descem juntas para
a linha de baixo dos filtros. No campo do produto fica só o nome, sem o SKU, que cortava o texto.

**Ficou de fora, de propósito:** lote (o sistema não controla), multiplicador de embalagem (o
cadastro do exemplo não tem), o botão de nota fiscal e os valores de ICMS (fiscais; a linha aparece
como reservada) e as mudanças de situação sem mudança de saldo, que continuam na página do produto.

**A decisão que ficou com o usuário.** A aba "Lançamentos" da página do produto, em Controle de
Estoques, mostra movimentos de exemplo próprios, e por isso responde à mesma pergunta com outros
dados. Ela ficou como estava, porque é nela que aparece o lançamento feito ali; a página ganhou o
botão "Movimentações". Tirar a aba ou mantê-la é escolha dele, e está no `PROGRESSO.md`.

**Duas conversas no mesmo projeto.** Enquanto esta tela era construída, outra conversa entregou o
§14.62. O item de menu já estava nas 80 telas, duas delas em edição pela outra conversa. Cada uma
fez o commit só do que era dela. O que vale levar: antes de uma troca em todas as telas, olhar se há
arquivo alterado que não é seu, e no commit escolher arquivo por arquivo.

**Provado nos dois sentidos.** `teste_movimentacao.py` tem 95 asserções em oito seções. Vinte e oito
defeitos injetados, um por vez, e os vinte e oito foram pegos: venda que entra em vez de sair,
histórico que parte de zero, filtro que não filtra, documento que mostra só um item, impressão que
leva a lista junto, tela que grava no navegador, planilha só com a página, tela vizinha sem o link.

## 14.64 Cadastros: o painel do fornecedor mostra o que as outras telas têm dele (13/out/2026)

Item C2 da lista de melhorias. O painel do fornecedor só tinha os dados de cadastro.

**Primeiro o exemplo, depois o painel.** O cadastro de Fornecedores trazia nomes de cliente (Marina
Duarte, Rafael Nogueira...) e nenhum dos sete fornecedores que Ordens de Compra, Entrada de Notas,
Necessidades de Compra e Contas a Pagar usam. Sem alinhar, o painel mostraria "nenhuma ordem" para
todo mundo. Seis registros viraram esses fornecedores, com o nome, o CNPJ e a UF que a Conferência de
Entrada já usava, e a Papelaria Central perdeu o "Ltda" que só existia ali. Dois deles estavam
inativos no exemplo, com ordem de compra em aberto; ficaram ativos.

**O painel.** Três blocos depois dos dados de cadastro: Compras (ordens em aberto, com link; quanto
falta receber; a última compra, com data, valor e número), Financeiro (contas a pagar em aberto, com
link, e quanto se deve) e "Fornecedor padrão de" (os produtos, cada um com link para Necessidades de
Compra). Fornecedor de quem nunca se comprou diz "nunca comprou" e "nenhuma", sem link para lista
vazia.

**Cada número tem uma dona.** O cadastro carrega três espelhos: as ordens (de Ordens de Compra), as
contas com saldo (de Contas a Pagar) e o fornecedor padrão de cada produto (de Necessidades de
Compra). "Falta receber" é o que ainda não chegou pelo preço dos itens; ordem em aberto sem
recebimento deve o total. A suíte lê cada tela de origem e compara.

**Provado nos dois sentidos.** Seis defeitos injetados, um por vez, contra `teste_cad_melhorias.py`
(16 asserções), e os seis foram pegos.

**Fica anotado.** Oito registros do cadastro seguem com nome de pessoa e sem compra nenhuma; a página
de detalhe do fornecedor abre o exemplo fixo (item G3).

## 14.65 Movimentação de Estoque: o produto pela busca padrão, e o período obrigatório (13/out/2026)

Retorno do usuário no mesmo dia em que a tela nasceu (§14.63), depois de testar.

**O produto é a busca padrão do sistema, e não uma lista de escolha.** A primeira versão trazia um
dropdown com os 15 produtos do exemplo, com a troca por busca anotada como oferta. Ele pediu a busca
de primeira: "se vamos usar esse módulo, certamente já sabemos o produto". O campo agora é o do
Acerto de Estoque, com o texto do Controle de Estoques: digitar nome, código (SKU) ou GTIN abre até
oito sugestões, na ordem do cadastro; clicar ou dar Enter escolhe a primeira. O que vale levar:

- **Mexer no texto desfaz a escolha.** Produto digitado e não escolhido não busca; a tela diz para
  escolher na lista. Texto que só casa com um produto já é a escolha.
- **Com o produto escolhido, Enter busca.** O primeiro Enter escolhe, o segundo busca.
- **As sugestões fecham quando outro filtro abre.** Os dropdowns e o calendário param a propagação do
  clique; o fechamento escuta na fase de captura, como o do popover de período (§14.54).

**Campo de escolher um produto é sempre esta busca.** Lista de escolha só serve ao exemplo: com o
cadastro de verdade são milhares de itens. Vale para toda tela nova que comece por um produto.

**O período é obrigatório e abre no mês atual.** Ele testou buscar sem data, veio o histórico
inteiro, e pediu a trava. Sem ela, uma busca sem data traria a vida inteira do produto de uma vez.
A trava sozinha custaria dois campos a preencher em toda consulta; por isso as datas já abrem do dia
1 do mês até hoje, que é também o que ele pediu para quem chega pelo botão "Movimentações" do
Controle de Estoques. Sem uma das datas a busca é barrada e o campo que falta fica marcado. Limpar
devolve o mês atual, que é o estado em que a tela abre. Para ver mais, muda-se a data inicial; o que
ficou antes do período continua aparecendo como "saldo antes".

**A decisão que continua com ele.** Sobre a aba "Lançamentos" da página do produto ele pediu opinião.
A recomendação foi tirar a aba e deixar só o botão "Movimentações": são duas listas para a mesma
pergunta, com números diferentes, que é o que a regra da página única existe para evitar. O custo
dito a ele: o lançamento feito na página passa a aparecer só no aviso de gravado. Nada foi tirado.

**Provado nos dois sentidos.** `teste_movimentacao.py` foi a 109 asserções. A prova do avesso foi
refeita inteira no estado final: 35 defeitos injetados, um por vez, e os 35 pegos. Os novos: busca
sem data que traz tudo, datas que abrem em branco, busca que não acha pelo GTIN, texto mexido que
mantém o produto antigo, sugestões abertas por baixo do filtro vizinho, Limpar que apaga as datas e
chegada pelo Controle de Estoques que abre o histórico inteiro.

## 14.66 A aba "Lançamentos" sai da página do produto: o histórico mora num lugar só (13/out/2026)

A página do produto, em Controle de Estoques, tinha a aba "Lançamentos": uma lista de movimentos de
exemplo, com dados próprios. Com a Movimentação de Estoque (§14.63) passaram a existir duas listas
para a mesma pergunta, com números diferentes para o mesmo produto. A primeira entrega deixou a aba
como estava e levou a escolha ao usuário. Ele pediu opinião, ouviu a recomendação de tirar e decidiu:
"podemos apagar a aba de lançamentos, deixa só a nova que acabamos de criar, ela é até mais completa".
É a regra da página única (§14.54) aplicada a uma lista dentro de uma página.

**O que saiu.** A aba, a tabela, os movimentos de exemplo (dois produtos tinham lista própria; os
outros treze dividiam a mesma), os filtros de período e de tipo de movimento, que só serviam à lista,
e o estilo dela. Saíram 181 linhas.

**O que ficou.** Os indicadores por situação, o filtro de depósito, as abas Endereços e Reservas, e
os botões do topo: Compra, Giro, Movimentações, Abrir no cadastro e Incluir lançamento. A página
abre em Endereços.

**Sem a lista, o aviso diz o que foi gravado.** Antes, a linha nova na lista era a confirmação do
lançamento, e só o que tinha consequência fiscal abria aviso. Agora todo lançamento fecha com o que
gravou (entrada ou saída, quantidade, endereço e motivo) e lembra que os indicadores já mostram o
saldo novo. O aviso fiscal continua, junto. O bloqueio já avisava. O que vale levar: **tirar uma
lista que servia de confirmação obriga a pôr a confirmação em outro lugar.**

**O custo, dito ao usuário antes.** O lançamento feito na página não aparece na Movimentação de
Estoque, que lê outro exemplo: no protótipo ele vale até recarregar a página, como o saldo dela. E o
histórico de endereçar e de bloquear, que só a aba mostrava, fica nas telas de Endereçamento e de
Tratamento de Perdas.

**Também confirmado por ele no mesmo retorno:** a busca de produto como ficou, as datas abrindo no
mês atual, sem ressalva, e as sugestões na ordem do cadastro, sem pôr na frente o nome que começa
pelo termo.

**Um reinício no meio da prova do avesso.** A sessão caiu enquanto um defeito estava injetado na
página do produto, e o arquivo ficou com ele: a restauração do script não roda quando o processo é
morto. Foi achado na retomada, por busca do trecho injetado, e desfeito. O servidor de preview
também tinha caído, e `teste_bloqueados.py`, que abre as telas por ele, reprovava com o arquivo
certo: o "pego" daquele defeito só valeu depois de subir o servidor e rodar de novo. O que vale
levar: **ao retomar depois de uma queda, procure defeito injetado antes de qualquer outra coisa, e
uma suíte que reprova por falta de servidor não prova que pegou defeito nenhum.**

**Provado nos dois sentidos.** Seção 9 de `teste_movimentacao.py`, que foi a 117 asserções, e uma
asserção em `teste_bloqueados.py` (175). Sete defeitos injetados, um por vez, e os sete pegos: a aba
que volta, o filtro que volta, a lista que volta, Endereços escondido ao abrir, lançamento que não
diz o que gravou, aviso fiscal que some e lançamento que não mexe no saldo da página.

**O selo não fechou, por causa de uma suíte que não é desta entrega.** `teste_cad_melhorias.py`, de
uma entrega de cadastros em andamento em outra conversa, trava até estourar os 900 segundos, e o
`selo.py` cai junto, sem gravar nada. As 20 suítes que alcançam a página do produto rodaram uma a
uma, restritas a ela como o selo faz, mais a auditoria do projeto e a oficial: tudo verde. O
`selo.json` ficou como estava. O que vale levar: **uma suíte que trava derruba o selo inteiro, e a
rodada perde também o que já tinha passado.**

## 14.67 Fornecedores: a lista dos produtos mora no cadastro, na aba Produtos Fornecidos (13/out/2026)

Retorno do usuário sobre o painel do fornecedor (§14.64): o resto ok, e a lista "Fornecedor padrão
de" ficaria melhor dentro do cadastro, numa aba antes de Observações, "coisa simples".

**Painel resume, cadastro detalha.** O painel lateral ficou com a contagem ("fornecedor padrão de 6
produtos") e a frase dizendo onde a lista está. A lista foi para a aba "Produtos Fornecidos" da
página do cadastro.

**A linha separa o que é do fornecedor do que é do produto.** Do fornecedor, e por isso editáveis: o
custo ali e o pedido mínimo. Do produto, só leitura: custo médio, giro mensal e preço de venda. E o
lucro por unidade "caso compre naquele fornecedor": preço de venda menos o custo ali, com a
porcentagem do preço; custo acima do preço aparece como prejuízo. O produto em que ele é o fornecedor
padrão leva a marca. Matéria-prima não é vendida: sem preço e sem lucro.

**Adicionar é pela busca padrão de produto**, a mesma do Acerto e do bloqueio: nome, SKU ou GTIN,
clique ou Enter no primeiro. O produto desce para a lista com o custo médio como custo e pedido
mínimo 1, e o foco vai para o custo. A busca não oferece o que já está na lista. A lixeira tira, na
hora, como a tabela de contatos da mesma página; quem grava é "Salvar alterações".

**Vazio não é zero.** Custo ou pedido mínimo em branco não vira zero: o lucro fica sem número, o campo
é marcado, e salvar não passa. Só a célula do lucro é reescrita ao digitar, para o campo não perder o
foco. Em leitura a lista aparece inteira, sem busca e sem lixeira. Fornecedor novo abre sem produto.

**O exemplo.** A página de cadastro mostrava a Distribuidora Nordeste, de quem nunca se comprou; a
aba ficaria vazia. O exemplo fixo passou a ser a TechParts, com os mesmos dados que ela tem na lista.
O catálogo da aba é espelho de Necessidades de Compra, e a suíte compara. O preço de venda ainda não
tem dona no protótipo (o cadastro de Produtos traz outro exemplo, item C3) e mora na aba por ora.

**O defeito injetado que ficou no arquivo.** A prova por defeitos alterava o arquivo de verdade. Um
dos casos (a lixeira que não remove) prendia a suíte num laço sem fim; a conversa caiu com ele em
andamento, a restauração não rodou, e a tela ficou com a lixeira quebrada. A outra conversa notou
porque a suíte passou a travar o selo inteiro. Três consertos: a linha voltou; o laço do teste ganhou
teto, para defeito virar reprovação e não espera; e **a prova passou a rodar numa cópia das telas,
fora do projeto**, por `file://`, com limite de tempo por caso. O roteiro recusa rodar fora da pasta
de rascunho.

**Provado nos dois sentidos.** Treze defeitos injetados, um por vez, contra `teste_cad_melhorias.py`
(36 asserções), e os treze foram pegos.

**Fica anotado.** A página de cadastro abre sempre a TechParts, qualquer que seja o fornecedor
clicado (item G3). O que se edita na aba vale até recarregar, como o resto do formulário.

## 14.68 Esc fecha o painel lateral em toda tela, o x do produto e a busca do PDV (13/out/2026)

**O relato.** O usuário apontou que o Esc não funcionava em nenhum painel lateral de Cadastros. O
painel mostra "ESC" ao lado de fechar, então a tela prometia e não cumpria.

**Em quantos lugares.** Medido nas 81 telas, abrindo cada painel e apertando a tecla: 89 painéis, e
em 42 o Esc não fechava. Doze em Cadastros, treze em Finanças, sete em Configurações, cinco em
Estoque, dois no Início, dois em Logística e o do molde. A causa era a mesma em todas: cada tela
escrevia o próprio tratamento da tecla, e a maioria só fechava o modal de confirmação.

**O conserto é de componente.** Um bloco comum, "ESC FECHA O PAINEL LATERAL", nas 61 telas que têm
painel na marcação: o Esc vale como clicar no "fechar" do painel aberto. Assim cada tela continua
dona do seu fechamento (limpar formulário, tirar o fundo escuro), e painel novo não precisa de
tratamento próprio; basta ter o controle `.drawer-close`. Três decisões do bloco:

- **Roda na captura e vem antes do bloco do dropdown.** Com menu, calendário, sugestão ou modal por
  cima, não faz nada: o que está por cima fecha primeiro. Se viesse depois, o bloco do dropdown já
  teria fechado o menu, e o mesmo Esc fecharia o painel junto.
- **Depois de fechar, para a propagação.** Senão o tratamento antigo da tela rodaria em seguida, e
  numa página de detalhe ele pode significar "voltar".
- **Com dois painéis abertos, fecha o último da página**, que é o de cima.

**Sete telas tinham um tratamento próprio que fechava o painel com algo na frente.** A suíte nova
abriu cada painel com cada modal e com um menu por cima, 191 combinações, e achou: Estágios do
funil, Formas de recebimento, Contas a Pagar, Contas a Receber, Transferência, Conferência de
Entrada e Inventário. Dois motivos. Uns só conheciam o modal de confirmação e fechavam o painel com
o aviso aberto; outros rodavam depois de o modal fechar, viam "nenhum modal" e fechavam o painel no
mesmo Esc. O tratamento próprio saiu das sete: com o bloco comum ele era redundante, e era ele que
errava. O que vale levar: **quando o componente passa a cuidar de uma coisa, o tratamento antigo de
cada tela sai junto; dois donos para a mesma tecla é onde a regra quebra.**

**O molde tem dois documentos.** O segundo é referência dentro de comentário e não executa. O
A primeira aplicação do bloco caiu nele; a medição mostrou que o painel do molde continuava sem
fechar, e o bloco foi para o script que roda. A suíte confere isso.

**O x do produto, na Movimentação de Estoque.** Pedido do usuário: uma bolinha com "x" dentro do
campo, que tira o produto e deixa o cursor pronto para o próximo. Só aparece com texto no campo. A
lista que está na tela fica até a próxima busca, como qualquer filtro desta tela. Nas outras buscas
de produto o campo se esvazia sozinho depois da escolha, e por isso o x é só aqui.

**A sugestão de produto do PDV.** No print dele, nome e dados vinham lado a lado, não cabiam no
campo e a caixa ganhava barra de rolagem. Passou a ter a cara da busca padrão: nome em cima, código,
preço e saldo embaixo. O comportamento do PDV não mudou (setas, Enter no código exato).

**O que ele quis conversar antes de mexer**, e está no `PROGRESSO.md`:

- **Um padrão de busca só?** A opinião dada foi manter dois, porque são dois trabalhos. Filtrar a
  lista que já está na tela não abre sugestões: a própria lista embaixo é a resposta. Escolher um
  item para agir, numa tela sem lista, abre sugestões. O que tem de ser igual é cada padrão dentro
  dele mesmo. O segundo existe em seis telas; cinco usam o mesmo componente e o PDV era a exceção.
- **O botão do painel dos cadastros.** Hoje "Editar cadastro completo" abre a página já editável. A
  proposta dele, "Ver cadastro completo" com o editar dentro, custa pouco: a página já abre em
  leitura e já tem o botão de editar.
- **A ordem do menu**, por sequência de trabalho.

**Provado nos dois sentidos, numa cópia.** `teste_esc_painel.py` tem 12 asserções em quatro seções;
`teste_movimentacao.py` foi a 122 e `teste_pdv.py` a 199. Onze defeitos injetados, um por vez, e os
onze pegos. Dez rodaram numa cópia das telas fora do projeto, com `DESK_PASTA`, depois de conferir
que as suítes passam na cópia intacta. O do PDV rodou no arquivo de verdade, porque a suíte dele
abre a tela pelo servidor de preview: em primeiro plano, com a restauração conferida byte a byte.

## 14.69 O menu por sequência de trabalho, "Ver cadastro completo" e a caixa de busca do PDV (13/out/2026)

Três decisões do usuário no mesmo dia, depois de ler as propostas da §14.68.

**O menu segue a sequência de trabalho.** A ordem antiga era a de construção: cada tela entrava onde
dava. Ele pediu "algo relacionado a sequências, e que faça sentido", para todos os módulos, e que
módulo novo já nasça assim. A regra e a ordem inteira estão no §4. Mudaram Cadastros, Estoque,
Vendas, Finanças e Integrações; Início e Logística já estavam na sequência. Três pontos:

- **No Estoque, contar vem antes de corrigir:** Inventário, Acerto de Estoque e Tratamento de Perdas,
  nessa ordem. A decisão de 09/out, que punha Tratamento de Perdas logo acima do Acerto, deu lugar à
  sequência.
- **Em Finanças, o Caixa foi para o terceiro lugar:** o título nasce em Contas a Receber e a Pagar e
  é no caixa que ele cai. Foi dito a ele que o Caixa podia continuar em primeiro; ele seguiu a
  proposta.
- **A regra tem guarda.** A seção 11 de `teste_menu.py` confere a ordem inteira, em toda tela. Item
  novo que entra no fim da lista sem estar na ordem combinada reprova o selo.

**A troca achou um nome de menu diferente em duas telas.** Em Contas a Receber e na página da conta,
o item de Integrações se chamava "Gateways de Recebimento"; nas outras 79, "Gateways de Pagamento".
A tela foi clonada de Contas a Pagar e a palavra foi trocada no arquivo todo, menu incluído. Voltou
o nome das outras. Antes disto nenhuma verificação comparava os nomes do menu entre as telas; a
seção 11 passou a comparar.

**"Ver cadastro completo".** O painel dos cadastros tinha "Editar cadastro completo", e a página
abria já editável. Ele pediu "Ver cadastro completo", com o editar dentro da página, no topo. A
página já tinha as duas peças: abre só para leitura, seguindo a preferência "Ao abrir um cadastro
existente", e tem o botão de editar no cabeçalho. O painel é que pulava a etapa, mandando
`?editar=1`. Mudou nos cinco cadastros com página própria (Clientes, Fornecedores, Produtos,
Vendedores e Lojas Desk): o botão do painel troca de nome e deixa de mandar o parâmetro, e o botão
da página passou de "Editar" para "Editar cadastro". O endereço com `?editar=1` continua valendo
para quem já chega querendo editar.

**A caixa de busca de produto do PDV** ganhou o formato das outras: arredondada, com a lupa e o
mesmo texto ("Pesquise por nome, código (SKU) ou GTIN/EAN"). Com a lista de sugestões da §14.68, a
busca de produto do PDV ficou igual à das outras cinco telas no que se vê; as setas do teclado
continuam sendo só dele.

**O padrão de busca ficou decidido:** ele concordou em manter os dois jeitos. Lista que já está na
tela filtra enquanto se digita; escolher um item para agir abre sugestões.

**Provado nos dois sentidos.** Seção 11 de `teste_menu.py`, seção 9 de `teste_retorno.py` e mais uma
asserção em `teste_pdv.py` (200). Sete defeitos injetados, um por vez, e os sete pegos. Quatro, os do
menu, numa cópia das telas fora do projeto. Os três das suítes que abrem a tela pelo servidor de
preview rodaram no arquivo de verdade, em primeiro plano, com a restauração conferida byte a byte.

## 14.70 As setas do teclado em toda busca que abre sugestões (13/out/2026)

Última diferença entre a busca de produto do PDV e a das outras telas (§14.68 e §14.69): no PDV dá
para andar pela lista com as setas; nas outras cinco o Enter escolhia sempre o primeiro. O usuário
mandou levar para o padrão.

**O conserto é de componente, e só mexe na marcação.** As cinco telas escrevem a busca cada uma do
seu jeito (variáveis, nomes e o que acontece ao escolher são diferentes). Um bloco comum, "SETAS NA
BUSCA COM SUGESTOES", não precisa saber de nada disso: a seta leva a classe `ativo` para o item de
baixo ou de cima, dando a volta no fim da lista, e o Enter clica no item ativo. Quem escolhe o item
continua sendo a tela, pelo clique que ela já trata.

- **O Enter para a propagação.** Senão o tratamento da tela rodaria em seguida e escolheria de novo,
  e sempre o primeiro.
- **Só vale com a lista aberta e dentro de `.busca-produto-wrap`.** Com a lista fechada as teclas
  seguem o caminho de antes: na Movimentação de Estoque, o Enter com o produto escolhido busca.
- **Sem mexer nas setas, nada muda:** o primeiro item nasce ativo, e o Enter escolhe o primeiro.

**As dicas das telas** diziam "Enter escolhe o primeiro da lista"; passaram a dizer que as setas
andam pela lista e o Enter escolhe.

**Busca nova com sugestões** usa `.busca-produto-wrap`, `.sugestoes`, `.sugestao-item` e a classe
`ativo` no primeiro item, e leva este bloco. `teste_busca_setas.py` confere que toda tela com a
caixa de sugestões tem o bloco e percorre cada uma.

**As decisões que ele fechou junto**, e que estão no `PROGRESSO.md`: o filtro com data inicial e
final fica onde já existe; o kit entra na compra como item individual, e a necessidade do
componente junta o mínimo dele com o que falta para o mínimo do kit (entra com a composição do kit,
que ainda não existe); e o envio ao GitHub volta a ser feito a cada entrega.

**Provado nos dois sentidos, numa cópia.** `teste_busca_setas.py` tem 27 asserções em três seções.
Cinco defeitos injetados, um por vez, e os cinco pegos: tela sem o bloco, Enter que escolhe o
primeiro, seta que não dá a volta, seta que deixa dois itens ativos e Enter que deixa a tela
escolher de novo.

## 14.71 O cadastro completo abre o registro clicado (item G3, nos cinco cadastros — 13/out/2026)

Primeiro item da fila que o usuário mandou seguir. Com "Ver cadastro completo" (§14.69), clicar em
qualquer fornecedor abria a TechParts: a página de detalhe desenhava um exemplo fixo. Valia para
Clientes, Fornecedores, Produtos, Vendedores e Lojas Desk.

**Como ficou.** O link do painel leva `?id=`. A página de detalhe tem `REGISTROS`, espelho do array
da lista, e um bloco "O CADASTRO QUE VEIO DA LISTA" que põe o registro na tela antes de qualquer
coisa ser desenhada: título, subtítulo, situação, tipo de pessoa e os campos que a lista conhece.
Sem `?id=`, ou com um que não existe, abre o exemplo de antes.

**Só o exemplo tem cadastro completo.** A página desenha um registro por inteiro (nome fantasia,
CEP, pessoas de contato, anexos). Dos outros ela mostra o que a lista sabe e deixa o resto em
branco: herdar o contato da TechParts no cadastro da Móveis Nordeste seria dado falso. Vendedores
e Lojas Desk não têm essa diferença nos campos, porque a lista deles já guarda o cadastro inteiro;
na loja, ficam em branco o depósito padrão e o histórico de metas.

**O que a página deriva.** No fornecedor, a aba Produtos Fornecidos traz os produtos de que ele é
o fornecedor padrão no catálogo, que é o número que o painel da lista mostra. Custo e pedido mínimo
dele a lista não sabe: entram o custo médio e 1, editáveis. No cliente, quem veio de uma loja tem
"Cadastro pela loja — Desk Tech" no subtítulo e a loja no campo; no cadastro manual a lista não
diz a loja, e fica a do formulário.

**Quatro defeitos que apareceram no caminho, todos de antes:**

- Trocar a loja ou a categoria no cadastro estragava o subtítulo: "Cadastro Manual — undefined" no
  cliente, "Vinculado à undefined" no vendedor, em branco no fornecedor. A tela lia um segundo
  argumento que o dropdown nunca mandou. Agora lê o rótulo do próprio dropdown.
- O cadastro novo herdava do exemplo o código, a data, dois contatos em branco, dois anexos e a
  faixa das lojas (cliente e fornecedor); a linha de custo e o fornecedor (produto); o histórico de
  metas (loja). Abre vazio.
- O documento duplicado do cliente comparava com seis nomes fixos e poupava sempre o CNPJ da
  Distribuidora Nordeste: aberto outro cliente, salvar acusaria o documento dele mesmo. Passou a
  usar o espelho e a poupar o registro aberto.
- No cadastro do fornecedor, a faixa "Fornece para" e a data "Fornecedor desde" eram as do cliente
  de quem a página foi copiada, e não as da TechParts na lista. Passaram a vir do registro.

**De outra tela, o link vai pelo nome.** Contas a Pagar e Contas a Receber já mandavam `?id=`, mas
com a numeração delas, que não é a do cadastro (a TechParts é 10 lá e 2 aqui): com a página
passando a obedecer o id, abririam o registro errado. Mandam `?nome=`. Nome que o cadastro não tem
abre o exemplo, como antes; isso é dado de exemplo por alinhar, e virou o item X6.

**Regras que ficam:**

- Página de detalhe nova lê o registro do endereço. O espelho da lista é declarado e tem suíte que
  compara.
- O que a lista não sabe fica em branco. Não se completa um registro com o dado do exemplo.
- Link entre telas com numeração diferente vai pelo nome, e isso fica dito num comentário.
- Dropdown sem valor fica em branco, com a altura dos outros.

**Ficou de fora:** a categoria do produto, que a página só aceita depois de escolhida a Loja Desk,
e a lista não diz a loja (entra com o C3); e as outras seis páginas de detalhe do G3 (Pedidos de
Venda, Ordens de Compra, Entrada de Notas, lançamento do Caixa, Conferência de Saída e Romaneio).

**Provado nos dois sentidos, numa cópia.** `teste_cad_detalhe.py` tem 68 asserções em nove seções,
e abre os 49 registros dos cinco cadastros um por um. Quatorze defeitos injetados, um por vez, e os
quatorze pegos.

## 14.72 A página da ordem de compra abre a ordem clicada (item G3, segunda parte — 13/out/2026)

Continuação do §14.71. Em Ordens de Compra, "Abrir ordem completa" abria sempre a nº 2: o botão do
painel não mandava o número, e a página desenhava um exemplo fixo.

**Antes de mexer, medir.** A lista de melhorias dava seis páginas como presas no exemplo. Uma sonda
no navegador, abrindo cada uma com quatro ids, mostrou que duas já abriam o registro certo
(lançamento do Caixa e Conferência de Saída) e que o Romaneio já lê o id, só não o recebe. Presas
de verdade: Pedidos de Venda, Ordens de Compra e a Nota de Entrada, que nem tem como abrir uma nota.

**Como ficou.** O botão do painel leva `?id=`. A página tem `ORDENS_DA_LISTA` e `ITENS_DA_LISTA`,
espelhos de `ORDENS` e `ITENS_OC` da lista, e o bloco "A ORDEM QUE VEIO DA LISTA" põe na tela o
título, o fornecedor, o depósito, as datas, a situação, o frete, o desconto e os itens, antes de
qualquer coisa ser desenhada.

**O total da página fecha com o da lista.** A página soma os itens; a lista guardava só o total, e
em três das quatro ordens com itens os dois não batiam (a própria nº 2 fechava em R$ 7.332,00 na
página e R$ 7.310,50 na lista). A lista ganhou `frete` e `desconto` nas ordens em que eles separam
a soma dos itens do total, e a página os lê. A suíte confere o total das 14.

**Ordem sem itens no exemplo.** Dez das 14 só têm o total. O painel da lista já mostrava um "Item
de exemplo", com preço zero; agora ele leva o total da ordem, no painel e na página, e a conta
fecha. Escrever os itens de verdade mexe no "já pedido" de Necessidades de Compra e do Giro, que
são conferidos contra as ordens em aberto: ficou como item X7, junto dos alinhamentos.

**O que veio junto:**

- Dois fornecedores da lista não existiam na página da ordem (Papelaria Central e Luminárias
  Brasil). Entraram, com o documento e a cidade de Cadastros > Fornecedores.
- Ordem atendida ou cancelada oferecia "Receber mercadorias" e "Receber parcialmente". Deixou de
  oferecer, como o painel da lista já fazia.
- "Clonar compra" copiava sempre a nº 2. Leva o número da ordem aberta.
- Da Conferência de Compra, "ver a ordem" abria a nº 2 qualquer que fosse a nota. Leva o número da
  ordem da nota.
- A ordem criada em Necessidades de Compra aparecia na lista e a página dela abria a nº 2. A página
  lê a mesma chave do navegador que a lista lê, e abre a ordem criada, com os itens.

**Regra que fica:** quando a página soma e a lista guarda o total, os dois têm de fechar em todos
os registros, e a suíte confere um por um. O que os separa (frete, desconto) é dado declarado na
lista, e não conta feita na página para dar certo.

**Provado nos dois sentidos, numa cópia.** `teste_doc_detalhe.py` tem 19 asserções em seis seções
e abre as 14 ordens uma por uma. Treze defeitos injetados, um por vez, e os treze pegos.

## 14.73 Os exemplos ficam como estão; a tela nova nasce no padrão (decisão do usuário, 13/out/2026)

Depois dos §14.71 e §14.72 ficou claro que quase tudo o que restava da lista de melhorias esbarrava
na mesma coisa: cada tela pronta tem o seu dado de exemplo, e eles não batem entre si. O pedido nº 1
somava R$ 890,00 em itens e mostrava R$ 1.890,00 de total; a página do romaneio conhecia 3 dos 9
romaneios da lista; o realizado de Metas não é a soma dos pedidos. Alinhar tudo eram sete entregas.

**A decisão.** Posta a escolha ao usuário, ele respondeu: "telas mais simples, sem muita
complexidade para teste, pode deixar os exemplos como estão, mas deixe registrado também que as
próximas telas devem seguir um padrão melhor, corrija as que realmente precisa agora". Exemplo
desalinhado some quando houver banco de dados; arrumar exemplo que vai ser jogado fora atrasa os
módulos novos.

**Regra para a tela pronta.** Não se abre entrega para alinhar exemplo entre telas. Achou número
que não bate, vai para "O que continua sendo dado de exemplo", no `PROGRESSO.md`. Conserto que mexe
em exemplo só entra quando a tela fica errada sem ele, e pelo mínimo que fecha a conta.

**Regra para a tela nova.** O exemplo nasce certo, porque nascer certo custa pouco e consertar
depois custa uma entrega:

1. A página de detalhe lê o `?id=` e abre o registro clicado.
2. Todo registro da lista tem os seus itens, e itens mais frete menos desconto fecham no total.
3. Registro que já existe em outra tela (cliente, fornecedor, produto, pedido, ordem) é copiado de
   lá com o mesmo nome e o mesmo número, num espelho declarado que a suíte compara.
4. Número que a tela divide com outra tem uma dona; a outra lê dela.
5. O que a tela não sabe fica em branco. Não se completa um registro com o dado do exemplo.

**O que precisava de conserto agora: Pedidos de Venda.** A lista já mandava `?id=`, e a página
ignorava: qualquer pedido abria o nº 2. É a tela mais testada e a que alimenta seis outras.

- A página tem `PEDIDOS_DA_LISTA` e `ITENS_DA_LISTA`, espelhos da lista, e o `carregar()` troca o
  exemplo pelo pedido pedido: cliente, documento, loja, vendedor, depósito padrão da loja, datas,
  situação, frete, desconto e itens. A venda de balcão, que mora no navegador, abre do mesmo jeito.
- **O total fecha nos 16.** A lista ganhou `frete` onde ele separa os itens do total. No pedido
  nº 1 a diferença era de R$ 1.000,00, e frete não explica isso: ele ganhou um item (duas cadeiras)
  e R$ 10,00 de frete. O pedido nº 2 levava dois produtos que o catálogo da página não tem; passou a
  levar os três produtos do exemplo desenhado, em quantidades que fecham. Nenhum total mudou, porque
  eles estão copiados em seis telas; os itens só existem na lista.
- **Pedido sem itens no exemplo** (12 dos 16) mostra um "Item de exemplo" pelo valor dele, no
  painel e na página.
- **O saldo não é conferido onde não faz sentido.** A página confere cada item contra o disponível
  e trava o salvamento. O item de exemplo e a venda de balcão, que já saiu do estoque, levam a marca
  `foraDoSaldo` e ficam fora da conferência. Item de pedido de verdade continua conferido.
- **Do cliente, só o do exemplo tem contas em aberto e últimas vendas.** Aberto o pedido de outro
  cliente, os dois quadros ficam vazios, em vez de mostrar a conta vencida do cliente errado. E
  cliente que tem pedido não cai no "cadastro rápido".
- O clone copia o pedido que está aberto: o link leva o `?id=` junto. Antes copiava sempre o
  exemplo. "Dados do cliente" leva o nome, e abre o cadastro daquele cliente.
- Sem `?id=`, a página segue abrindo o exemplo desenhado nela. É o que as suítes antigas usam, e é
  diferente do pedido nº 2 da lista: ficou anotado como dado de exemplo.

**O botão do romaneio.** A página do romaneio já lia o id e o botão "Abrir o romaneio" não mandava.
Manda. A página conhece 3 dos 9; para os outros, ela abre o romaneio padrão e avisa. Dar a ela os
nove é alinhamento de exemplo, e ficou fora.

**Achado e não mexido:** em modo de leitura, o campo "Número do pedido" mostra o rótulo e nenhum
valor. É de antes, e o número está no título.

**Duas suítes antigas pegaram o que a nova não via,** e por isso a suíte nova nunca é a única a
rodar antes do selo. `teste_pedidos.py` acusou que clonar o exemplo aberto sem id passara a copiar
a versão da lista: o clone ganhou o `?id=`. `teste_pdv.py` acusou que o catálogo do PDV, que é
cópia do catálogo do pedido, deixara de bater, porque eu tinha posto dois produtos no do pedido:
saíram, e quem mudou foram os itens do pedido nº 2.

**Provado nos dois sentidos, numa cópia.** `teste_doc_detalhe.py` ganhou cinco seções e passou a
39 asserções; abre os 16 pedidos um por um. Quinze defeitos injetados, um por vez, e os quinze
pegos.

## 14.74 Parâmetros de estoque deixou de ser gaveta (item K1 — 13/out/2026)

A tela tinha nove seções, e cinco não eram de estoque: filas do galpão, reserva e bloqueio por
atraso, expedição e romaneio, MDF-e e devoluções de venda. Cada tela nova de Logística foi pondo o
seu parâmetro ali, porque era a única tela de parâmetros que existia. Quem procurava o prazo da
devolução não pensava em estoque.

**Decisão do usuário.** Duas telas, estoque e logística. E o parâmetro que não é de nenhuma das
duas, "Bloquear novo pedido de cliente em atraso", vai para Configurações do cadastro de clientes,
que já existia: é regra sobre o cliente, e não pede tela nova.

| tela | o que ficou |
|---|---|
| Parâmetros de estoque | Conferência de compra · Endereçamento · Estoque zero na base de picking · Compra e giro · Reserva de estoque |
| Parâmetros de logística (nova) | Filas do galpão · Expedição e romaneio · MDF-e na carga própria · Devoluções de venda |
| Configurações do cadastro de clientes | ganhou a seção "Cliente em atraso" |

**Como foi feito.** A tela nova é a antiga sem as seções de estoque, e a antiga perdeu as de
logística. O código da tela tratava as nove seções num bloco só (uma validação, uma função de
prévias, uma lista de chaves); cada tela ficou com a sua parte, sem código morto da outra. A chave
do parâmetro não mudou: quem lê `PARAM.devolucaoPrazoDias` continua lendo o mesmo valor.

**Salvar numa tela não mexe no que é da outra.** Cada tela grava o objeto de parâmetros inteiro,
que ela monta juntando o padrão dela com o que já estava salvo. O que é da outra tela vem do que
estava salvo e volta igual. A suíte grava um prazo de logística, salva o estoque e confere que o
prazo continua lá.

**O que apareceu no caminho:**

- O padrão de fábrica de cada tela é só o das chaves que ela conhece. O cadastro de clientes não
  tinha o do bloqueio por atraso: sem ele, o campo abriria vazio num navegador que nunca salvou
  nada. Ganhou o mesmo padrão que o Pedido de Venda lê (1 dia), e a suíte compara os dois.
- A seção "Reserva de estoque e bloqueio por atraso" tinha uma prévia só, a do bloqueio. A reserva,
  que ficou sozinha, ganhou a dela: "pedido sem pagamento há mais de N dias libera a reserva".
- Duas suítes antigas abriam a tela única para procurar parâmetros que saíram dela. Passaram a
  procurar onde cada um foi morar, e uma delas agora exige que o parâmetro esteja numa tela só.
- A Devolução mandava para Parâmetros de estoque em "Abrir parâmetros da devolução". Manda para
  logística.

**Regra que fica:** parâmetro novo entra na tela do módulo que o lê, e não na tela de parâmetros
que já existe. Se o módulo ainda não tem tela de parâmetros, ela nasce com o primeiro parâmetro.
Cada parâmetro tem uma tela só; `teste_parametros.py` confere os 22 que a tela única guardava.

**Na mesma resposta o usuário tirou da fila as cópias do número da meta (R6):** fazer a página da
loja e o Dashboard lerem de Metas é arrumar exemplo entre telas prontas (§14.73).

**Provado nos dois sentidos, numa cópia.** `teste_parametros.py` tem 37 asserções em cinco seções.
Dezessete defeitos injetados, um por vez. Dezesseis foram pegos de primeira. O que escapou tirava da
prévia da reserva o efeito ("libera a reserva sozinho") e deixava o prazo, e a asserção só olhava o
prazo: passou a exigir os dois, e o defeito foi pego na segunda rodada.

## 14.75 A impressão vira relatório: o piloto em Ordens de Compra (item P1 — 14/out/2026)

Até aqui, imprimir uma lista dava o desenho da tela sem o menu: a folha levava a caixa "Selecionar
todos", a seta de ordenação, as abas e os indicadores, e não dizia o que era, quando foi emitida nem
que filtro estava valendo. Combinado com o usuário: o formato nasce numa lista, ele vê a folha, e só
então vai para as outras 19.

**A folha.**

- **Cabeçalho do relatório**, que só existe no papel: "Desk Company · ERP System", o título da
  lista, "Emitido em 14/10/2026 às 10:06, por Administrador Desk", os filtros e a quantidade de
  registros. Sem filtro, diz "nenhum, a lista inteira".
- **Os filtros são lidos da própria tela:** a aba, os dropdowns e a busca da barra, o período e o
  indicador clicado. O primeiro item de cada filtro é o "todos", e não aparece. Ler da tela, e não de
  uma lista feita à mão, é o que deixa o mesmo código servir nas 20 listas.
- **Não vai para o papel:** menu, barra de filtros, abas, indicadores, "Selecionar todos", a coluna
  das caixas de seleção, as setas de ordenação e a bolinha da situação. A situação vai como texto.
- **A tabela** começa alinhada com o cabeçalho, com linhas finas e letra menor, e o cabeçalho dela
  se repete em cada folha.

**O Ctrl+P dá a mesma folha que o menu.** "Imprimir", no menu, já mandava a lista inteira para o
papel; o Ctrl+P imprimia só a página aberta (10 das 14 ordens), e a contagem do cabeçalho diria 10.
Agora a lista se abre inteira antes da impressão e volta à página depois, pelas duas vias.

**Por que é um bloco da tela, e não o bloco comum.** O bloco de planilha e impressão é idêntico nas
20 listas, e `teste_planilha.py` exige isso. O piloto entrou como um complemento só de Ordens de
Compra, logo abaixo do bloco comum, e escuta a impressão do navegador (`beforeprint`). Aprovado, ele
passa para dentro do bloco comum e chega às outras 19 de uma vez.

**Provado nos dois sentidos, numa cópia.** `teste_impressao.py` tem 16 asserções em quatro seções e
mede a folha com a mídia de impressão emulada. Doze defeitos injetados, um por vez, e os doze pegos.

**Achado na virada do dia, consertado junto.** O espelho das contas a pagar no cadastro de
fornecedores (item C2, de 13/out) guardava o vencimento com data cravada, e Contas a Pagar calcula
o vencimento a partir de hoje. Em 13/out os dois batiam; em 14/out ficaram um dia longe, e
`teste_cad_melhorias.py` reprovou. O painel nem mostra essa data: ela saiu do espelho e da
comparação. É a regra do §13 de novo, agora num espelho: dado de exemplo com data fixa envelhece.
Espelho de tela que conta datas a partir de hoje guarda a distância em dias, ou não guarda a data.

## 14.76 O relatório da impressão nas 19 telas (item P1 — 14/out/2026)

O usuário testou o piloto de Ordens de Compra (§14.75), aprovou a folha como estava e mandou
seguir. O relatório saiu do bloco próprio daquela tela e entrou no bloco comum de planilha e
impressão, que 19 telas compartilham: 15 listas e 4 documentos.

**Lista e documento não imprimem igual.** Na lista, o cabeçalho do relatório leva o título, os
filtros e a quantidade, e o título da tela sai do papel para não aparecer duas vezes. No documento
(Conferência, Nota de Entrada, Ordem de Compra e Pedido de Venda) não existe filtro nem quantidade:
o cabeçalho leva só a empresa, a data e quem emitiu, e o título da página fica, com a situação ao
lado. Quem decide é a própria tela: documento é a que não tem lista para redesenhar
(`PLANILHA_REFAZ` nulo).

**O que mudou do piloto para o comum:**

- **"Sem filtro" deixou de ser "o primeiro item".** O piloto pulava o primeiro item de cada filtro,
  porque em Ordens de Compra o primeiro é sempre o "todos". Nas filas não é: a tela abre no que
  falta fazer, e esse primeiro item é um filtro de verdade. Agora pula o que diz "todos", "todas",
  "sem filtro" ou "qualquer", e o "ordenar por", que é ordem e não filtro.
- **Os botões de filtro da barra** (Pessoa Física, Pessoa Jurídica, nos cadastros) entram nos
  filtros, como as abas e os dropdowns.
- **A quantidade vem do que a tela exporta para a planilha** (a mesma função), e não das linhas de
  uma tabela: os cadastros não têm tabela.
- **A coluna da caixa de seleção** some com o título junto só quando as células dela têm a caixa.
  O piloto sumia com o primeiro título vazio de qualquer tabela, o que desalinharia as colunas numa
  tabela cujo primeiro título vazio fosse de outra coisa.
- **O CSS do relatório é um bloco igual nas 19**, como o código, e a suíte compara.

**Provado nas 19, uma por uma.** `teste_impressao.py` passou a 21 asserções: abre cada tela, imprime
com a mídia de papel emulada e confere o cabeçalho, a quantidade, a falta de caixa de seleção, o
alinhamento das colunas e a volta à página depois do Ctrl+P; e, em 13 listas, escolhe um filtro e
confere que ele aparece no cabeçalho. Oito defeitos injetados em telas diferentes, um por vez, e os
oito pegos.

## 14.77 A segunda varredura e os seus consertos (14/out/2026)

A primeira varredura dos módulos prontos deixou de fora o miolo dos fluxos longos. A segunda abriu
Inventário, Acerto, PDV com caixa aberto e a contagem da Conferência de Entrada no navegador e fez
cada fluxo do começo ao fim, só observando. Os quatro se defendem bem: nada fecha sem contagem,
divergência pede confirmação e motivo, o caixa fecha às cegas, desconto acima do máximo pede a senha
do gerente, e nenhum deu erro de JavaScript. Saíram nove pontos pequenos; a lista está em
`docs/melhorias-modulos-prontos.md`, seção "Segunda varredura".

**Os seis defeitos, consertados:**

- **Inventário, fechar sem senha:** o campo ficava com a borda vermelha e a mensagem não aparecia.
  Aparece, e some quando a senha é digitada.
- **Inventário, cancelar:** com quantidade já informada, um clique jogava fora a contagem inteira.
  Agora pergunta, dizendo quantas quantidades vão embora; sem nada contado, cancela direto.
- **Inventário, códigos recusados do arquivo:** a tela prometia a lista com o motivo e mostrava só a
  quantidade. O aviso depois da importação e o painel de fechamento listam os códigos, com o motivo
  (os cinco primeiros). No painel, que escreve HTML, o código, que veio do arquivo, é escapado.
- **Inventário e Acerto, o usuário:** as duas mostravam "Walysson Santos"; as outras 80 e o
  relatório impresso, "Administrador Desk". Passaram a usar o mesmo; o do Inventário vem de
  `USUARIO_SESSAO`.
- **Acerto, depósito repetido:** a lista vem dos saldos, um por endereço, e a limpeza dos repetidos
  comparava o HTML do item, que no primeiro tinha uma classe a mais. A limpeza passou a ser pelo
  número do depósito.
- **Acerto, saída maior que o endereço:** entrava na lista e só era recusada ao gravar o lote. Agora
  para na própria linha, com o que o endereço tem, contando o que outras linhas do lote já tiram
  dele. A validação do lote continua lá.

**As três decisões do usuário:**

- **Entrada de acerto em qualquer depósito.** Uma sobra pode aparecer onde o produto não tinha nada.
  A lista de depósitos passou a depender do tipo: entrada mostra todos, saída e balanço só onde há
  saldo. Trocar o tipo refaz a lista, e o depósito escolhido volta para um que sirva.
- **O desconto da venda acima do máximo avisa no campo**, enquanto se digita, como no item. A senha
  do gerente continua sendo pedida ao finalizar.
- **Uma confirmação por divergência na conferência** ficou como está: é o que faz quem confere olhar
  de novo cada item.

**Regras que ficam:**

- Ação que descarta o que a pessoa digitou (cancelar um inventário, limpar uma contagem) pergunta
  antes, dizendo o que vai embora. Sem nada digitado, não pergunta.
- Erro que dá para ver na linha é dito na linha, e não só no fim do lote.
- Campo com erro mostra a mensagem, e não só a cor.

**Provado nos dois sentidos, numa cópia.** `teste_varredura2.py` tem 22 asserções em três seções.
Treze defeitos injetados, um por vez, e os treze pegos.

## 14.78 Vendas Afiliados é Pedido de Venda, e a comissão segue a regra de quem recebe (14/out/2026)

O escopo inicial era uma tela "Vendas Afiliados" com lista própria. Na barganha de 14/out o usuário
contou o que ela é: as vendas feitas pelos links que o cliente logado gera na página do produto da
vitrine, como na Shopee, e as dos vendedores, com o mesmo funil do pedido (aprovar pagamento,
separação, expedição). Uma segunda lista de pedidos repetiria o funil, a reserva de estoque e a conta a
receber, e cada conserto teria de ser feito duas vezes. **Por isso não há tela nova:** a venda por
link é Pedido de Venda, e o item "Vendas Afiliados" do menu abria a lista de pedidos filtrada (saiu do menu em 15/out, §14.81).

**O que mudou:**

- **O pedido diz quem indicou** (`ind`). A indicação chega da vitrine com o pedido e não se digita:
  na página do pedido é um campo só de leitura. Cliente afiliado traz o percentual do programa no dia
  da venda; vendedor segue o cadastro dele. Uma pessoa recebe por pedido, e o link vale sobre o
  vendedor marcado. Quem compra pelo próprio link não gera comissão, e o clone de um pedido por link
  nasce sem indicação, porque é pedido digitado.
- **A lista ganhou o filtro de origem** (todas, afiliadas por link ou vendedor, só link, sem afiliado)
  e a marca "indicação de" na linha e no painel. O menu leva `?origem=afiliadas`, nas 82 telas.
- **A aba Comissões segue a regra de quem recebe.** Ela aplicava 5% e "integral no faturamento" a
  qualquer vendedor, e o cadastro tem quatro regras de liberação. A regra de cada vendedor é espelho
  do cadastro (`COMISSAO_DO_VENDEDOR`); vendedor com 0% diz que o pedido não gera comissão; o cliente
  afiliado libera com o pedido entregue e 7 dias sem devolução.
- **Faturar diz o efeito certo na comissão.** O texto prometia "libera a comissão do vendedor" a todos;
  a Marina, no cadastro, libera por parcela paga. Agora o texto e o aviso depois do passo dependem de
  quem recebe e da regra dele.

**Regras que ficam:** texto que anuncia um efeito que depende de uma regra de cadastro lê a regra, e não
promete o caso comum. E rótulo de opção de filtro não passa da largura do rótulo padrão: o usuário
testou e viu a barra quebrar de linha ao escolher "Afiliadas: link ou vendedor", mais largo que "Todas
as origens". Os rótulos viraram "Vendas afiliadas" e "Só por link", e a suíte varre larguras de tela de
20 em 20 px conferindo que nenhuma escolha soma linha à barra.

**O que fica para a entrega 2:** Comissões Afiliados, em Finanças (lista enxuta, conta do afiliado com
as 9 linhas do Olist, pagamento por conta a pagar, lançamento à mão com motivo e senha), e Contas a
Pagar aceitando vendedor e cliente afiliado como favorecido. O gerar link e o "minhas indicações" são
da vitrine, fora do ERP.

**Provado nos dois sentidos, numa cópia.** `teste_afiliados.py` tem quatro seções (lista, menu,
página do pedido e espelhos). Vinte e um defeitos injetados, um por vez, e os vinte e um pegos.

## 14.79 Comissões Afiliados: a lista, a conta do afiliado e as inscrições (14/out/2026)

Barganhada com o usuário em 14/out, com 12 prints de Comissões do Olist e os textos dos (i) das
colunas. Ele decidiu: a lista enxuta, com as colunas necessárias (opção B), e a conta inteira ao abrir
o afiliado; a aprovação do afiliado no ERP; o percentual por loja; e o vendedor sem link.

**Duas telas novas, em Finanças**, montadas a partir de Metas e Performance:

- **A lista** (`pagina-financas-comissoes.html`): uma linha por quem recebe comissão, vendedor do
  cadastro (os não excluídos) ou cliente aprovado como afiliado de uma loja. Colunas: pedidos do mês,
  vendido (sem frete), percentual, comissão do mês, lucro, a liberar e saldo a pagar. Indicadores do
  mês, filtro de mês, ano e tipo, painel lateral com a conta do mês e o caminho para a conta inteira.
- **As inscrições**: o cliente pede pela vitrine de uma loja, aceitando as regras dela; o pedido chega
  no quadro "Inscrições aguardando", com CPF e chave PIX. Aprovar pergunta antes, dizendo a loja e o
  percentual; recusar pede o motivo, que volta para o cliente. "Incluir afiliado" é para convite: um
  cliente que já está no cadastro, numa loja em que ainda não é afiliado.
- **A conta do afiliado** (`pagina-financas-comissoes-detalhe.html?id=v1` ou `a1`): o resumo nas linhas
  do Olist, com os textos dos (i) (saldo anterior e saldo sempre; as outras, só com valor), os pedidos
  do mês (cada um abre o pedido), as comissões pendentes (vermelho venceu sem o cliente pagar, amarelo
  a liberar) e os outros créditos e débitos. Editar ou excluir comissão e lançar à mão pedem motivo,
  passam por Confirmações com senha e ficam no registro de atividades. Cliente afiliado pode ser
  suspenso e reativado.

**As regras:** o cliente afiliado libera com o pedido entregue e 7 dias sem devolução; o vendedor
segue a regra do cadastro. O lucro é a venda sem frete, menos o custo dos produtos (congelado no
pedido, campo `custo`) e a comissão. Cada comissão é arredondada em centavos antes de somar: sem
isso, o saldo da Marina saía R$ 352,99 num mês cujas linhas somam R$ 353,00.

**Ligadas:** os pedidos são espelho de Pedidos de Venda; os vendedores, do cadastro de vendedores; os
clientes, do cadastro de clientes; o percentual de cada loja e a validade do link, de Configurações →
Cadastro de clientes (seção Programa de afiliados). O bloco de dados e regras é idêntico nas duas
telas. O item do menu ganhou destino em todas as telas, e as três ações novas (aprovar afiliado,
ajustar comissão, lançar na conta) entraram no catálogo das 15 telas que o carregam.

**Fica para a entrega 2b:** "realizar pagamento", com a conta nascendo em Contas a Pagar e o
pagamento no resumo. **Fica para o vale-compra:** pagar a comissão como crédito na loja.

**Provado nos dois sentidos, numa cópia.** `teste_comissoes.py` refaz a conta em Python a partir dos
pedidos e compara cada linha; tem cinco seções. Vinte e três defeitos injetados, um por vez, e os
vinte e três pegos.

## 14.80 Comissões Afiliados: o pagamento vira conta a pagar (15/out/2026)

Decidido na barganha de 14/out: pagar a comissão gera conta a pagar, e o saldo desce na hora.

- **Realizar pagamento**, no "Mais ações" da conta do afiliado, abre com o saldo de hoje (o pagamento é
  feito hoje, qualquer que seja o mês aberto na tela) e vencimento hoje. Dá para pagar menos, nunca
  mais, e o vencimento é de hoje em diante. Pede senha (Confirmações com senha, ação "Realizar
  pagamento de comissão"). Feito, o resumo ganha "(−) Pagamentos", e o bloco Pagamentos leva à conta.
- **A conta nasce em Contas a Pagar**: um bloco igual na lista e na página da conta lê o pagamento e
  cria a conta 9000 + n, documento COM-n, a pagar, com o vendedor ou o cliente afiliado como favorecido
  (Contas a Pagar só conhecia fornecedor) e a categoria nova "Comissões de vendedores e afiliados"
  (despesa variável), que entrou em Configurações e nas 7 telas que repetem as categorias.
- **Fica para depois:** pagar como crédito na loja (o vale-compra) e o saldo voltar quando a conta for
  cancelada em Contas a Pagar, que no protótipo não guarda o cancelamento de uma tela para a outra.

**Provado nos dois sentidos, numa cópia.** A seção 6 de `teste_comissoes.py` cobre o pagamento. Oito
defeitos injetados, um por vez, e os oito pegos.

## 14.81 O teste de Comissões: o menu que abria para cima, o valor da conta e um item a menos no menu (15/out/2026)

O usuário começou a testar Comissões Afiliados e trouxe três pontos.

- **O dropdown abria para cima por cima da lista.** A regra do componente olhava só o espaço que sobra
  na janela; com a barra de filtros no pé da janela, o menu de situações de Pedidos de Venda subia e
  cobria os indicadores. **Correção de componente, nas 81 telas** (106 dropdowns): antes de abrir para
  cima, a página rola o que faltar e o menu abre para baixo. Para cima só quando a página não rola mais,
  ou quando o dropdown está dentro de painel fixo (painel lateral, modal), que não rola com a página.
- **A conta de comissão voltava ao valor de Comissões.** Ele editou a COM-1 de R$ 353 para R$ 100 em
  Contas a Pagar, e ela voltou a R$ 353: no protótipo, Contas a Pagar não guarda edição de uma tela para
  a outra, e a conta é refeita a partir do pagamento. O número tem um dono só: a conta de comissão diz
  que veio de Comissões Afiliados, com o link, e o valor fica travado. Para pagar outro valor, o
  pagamento é cancelado em Comissões (o valor volta ao saldo e a conta sai de Contas a Pagar) e feito
  de novo. O registro cancelado fica, para o número COM-n não se repetir.
- **O item "Vendas Afiliados" saiu do menu.** Abria a mesma tela de Pedidos de Venda, e tela que repete
  outra vira uma página só, sem item no menu. O filtro de origem continua em Pedidos, e Comissões
  Afiliados leva até ele. O caminho no topo de Pedidos deixou de repetir o filtro, que ficava velho
  quando a origem mudava. O menu passou a ter 55 itens, 43 com tela.

**Provado nos dois sentidos, numa cópia.** `teste_afiliados.py` (seção 2) mede o menu no pé da janela e
procura a correção em todo dropdown; `teste_comissoes.py` (seção 6) cobre a conta travada e o cancelar.
Sete defeitos injetados, um por vez, e os sete pegos.

## 14.82 Dropdown sempre para baixo, e a conta de comissão que voltava (15/out/2026)

Segunda rodada do teste de Comissões Afiliados.

- **"Quero que o filtro fique para baixo, independente se a tela tá mais baixa ou não."** A primeira
  correção (§14.81) rolava a página o que ela tinha para rolar; numa lista curta não havia o que rolar, e o
  menu ainda subia. A regra mudou: **todo dropdown abre para baixo.** Fora de painel fixo, o menu aberto já
  estica a página, e ela rola até ele aparecer inteiro. `.abrir-para-cima` ficou só para dropdown dentro de
  painel fixo (painel lateral, modal), que não rola com a página e cortaria o menu. Nas 81 telas, nos 106
  dropdowns, e nas duas skills (o não-negociável, o portão de QA e o código de referência do componente).
- **Cancelar ou excluir a conta de comissão em Contas a Pagar não gravava.** No protótipo, Contas a Pagar
  só muda a memória da página, e a conta de comissão é refeita a partir do pagamento ao recarregar. Agora os
  quatro botões (cancelar e excluir, na página da conta e na seleção da lista) gravam no pagamento de
  Comissões: cancelar cancela o pagamento, o valor volta ao saldo e a conta fica cancelada no histórico;
  reativar desfaz; excluir tira o pagamento e a conta. Cancelar pelo lado de Comissões dá o mesmo resultado.

**Provado nos dois sentidos, numa cópia.** `teste_afiliados.py` (seção 2) mede o menu também em lista curta;
`teste_comissoes.py` (seção 6) cancela, reativa e exclui em Contas a Pagar e confere, depois de recarregar,
o saldo em Comissões. Cinco defeitos injetados, um por vez, e os cinco pegos.

## 14.83 O Voltar do navegador e a tela que mostra dado de outra tela (15/out/2026)

O usuário cancelou a conta de comissão em Contas a Pagar e ela não apareceu em "canceladas", embora o valor
tivesse voltado ao saldo em Comissões. Testado do zero, os dois caminhos (a página da conta e a seleção da lista)
põem a conta em "canceladas". A diferença é o Voltar do navegador: ele traz a página da memória, como estava antes
do cancelamento, sem rodar a tela de novo. Comissões, aberta do zero, já mostrava o certo.

**Regra que fica:** tela que monta a lista com o que outra tela grava no navegador (aqui, os pagamentos de comissão)
recarrega quando volta da memória (`pageshow` com `persisted`). Vale para Contas a Pagar (lista e página da conta)
e para as duas telas de Comissões. A seção 6 de `teste_comissoes.py` simula a volta e confere a recarga nas quatro.

## 14.84 Comissões 2c: o histórico, o saque pedido e o pago que volta da baixa (15/out/2026)

Barganha aprovada pelo usuário em 15/out ("concordo com o recomendado"):

- **O histórico é de Comissões.** A conta do afiliado ganhou o bloco Histórico, de todos os meses, do mais novo
  para o mais velho: inscrição e aprovação (e recusa, suspensão, reativação, com o motivo), cada venda, cada
  comissão liberada, os ajustes e lançamentos à mão, os saques pedidos (e recusados), os pagamentos, as baixas e
  os cancelamentos. "Afiliado desde" passou a ser o dia da aprovação, e não o do pedido de inscrição.
- **O cadastro só lê.** O cadastro do cliente ganhou a aba Afiliado (loja, situação, comissão, saldo a pagar
  hoje, pagamentos feitos, já pago e o link para a conta), com o mesmo bloco de regras das telas de Comissões;
  a suíte compara as três cópias. O cadastro do vendedor ganhou o link para a conta dele.
- **O cliente afiliado pede o saque** na vitrine, a partir do mínimo de Configurações → Programa de afiliados
  (R$ 50). O pedido chega no quadro "Pagamentos solicitados" da lista; aprovar (com senha) faz o pagamento e a
  conta a pagar, e não passa do saldo de hoje; recusar pede o motivo, que volta para o cliente. A conta mostra
  uma faixa enquanto o pedido espera. O vendedor continua pago pela empresa.
- **O pago volta da baixa.** A baixa da conta de comissão em Contas a Pagar (na página da conta ou em lote, na
  lista) grava no pagamento de Comissões, que passa a mostrar "pago em dd/mm"; a conta continua paga ao
  recarregar, e o estorno a devolve para "a pagar". Pagamento pago não se cancela por Comissões: estorna-se a
  baixa antes.
- **Na vitrine**, "Minhas indicações" mostra ao cliente o mesmo acompanhamento, lendo do mesmo banco. Fica
  para quando a vitrine for construída.

**Provado nos dois sentidos, numa cópia.** A seção 7 de `teste_comissoes.py` cobre o histórico, o saque
(recusar e aprovar), a baixa e o estorno, a aba Afiliado e o link do vendedor. Treze defeitos injetados, um por
vez, e os treze pegos.

## 14.85 O período por data inicial e final, e o histórico que fecha a conta (15/out/2026)

O usuário testou a 2c e pediu: data inicial e final no topo da conta do afiliado, filtro só de mês e ano no
histórico, o histórico melhor, e o histórico também no cadastro do cliente.

- **O período da conta é data inicial e final.** A conta é a de um período qualquer (`contaDoPeriodo`); o mês
  inteiro continua existindo (`contaDoMes`), e a lista, o painel lateral e o cadastro do cliente seguem por mês.
  A linha de comissões se chama "do mês" quando o período é um mês inteiro, e "do período" nos outros casos.
  **Lançamento à mão vale pelo mês a que se refere**, não pelo dia em que foi feito: entra em todo período que
  toca esse mês, e no saldo anterior quando o mês terminou antes da data inicial. Por isso, dois períodos
  seguidos fecham (o saldo anterior de um é o saldo do outro), fora os lançamentos do mês.
- **O período aparece escrito sob o título** ("Período: 01/10/2026 a 31/10/2026"). A barra de filtros não vai
  para o papel, e a conta impressa não dizia de que período era.
- **O histórico é um extrato.** Tipo (inscrição, venda, comissão, saque, pagamento, lançamento), valor, efeito
  no saldo e saldo depois do acontecimento. O saldo se conta do mais velho para o mais novo, e o do mais novo é o
  saldo de hoje: a conta fecha linha a linha, e a suíte confere isso, inclusive depois de um pagamento excluído.
  O filtro de mês e ano só recorta a lista; o saldo de cada linha continua o verdadeiro.
- **O cadastro do cliente também conta o que aconteceu.** A barganha previa só o resumo; o usuário viu faltar o
  pagamento que ele excluiu. A aba Afiliado ganhou o histórico, o mesmo da conta, lido de lá (uma função, três
  cópias do bloco, comparadas pela suíte). O filtro fica fora de `.form-field`, que no modo leitura esconde todo
  dropdown. Ao voltar da memória do navegador, o cadastro refaz só a aba, para não perder o que se digita.

**Regra que fica:** acontecimento que muda o saldo mostra o efeito e o saldo depois dele; histórico que não
fecha com o saldo de hoje está errado.

**Provado nos dois sentidos, numa cópia.** A seção 8 de `teste_comissoes.py` cobre o período, o histórico e o
cadastro; o oráculo refaz os pedidos do período em Python. Treze defeitos injetados, um por vez, e os treze
pegos (um escapou na primeira rodada, o do saldo depois do pagamento excluído, e fechou a lacuna da suíte).

## 14.86 A tabela não rola na horizontal, e o histórico filtra por tipo (15/out/2026)

O usuário viu a barra de rolagem no histórico da conta do afiliado e pediu: tirar, registrar a regra, e
filtrar o histórico por tipo.

- **A regra já existia e não foi aplicada.** A skill de QA pedia, desde 12/out, que a tabela não tivesse barra
  com o dado mais comprido, em 1440, 1366 e 1280. As telas de Comissões foram medidas só com o exemplo curto, e o
  histórico rolava até em 1440 (1068px de tabela num cartão de 986). Acima do exemplo, a causa mais comum é
  anterior: o CSS comum fixa `min-width:920px` nas tabelas, e abaixo de uma janela de 1374px isso vira barra.
- **Como ficou nas telas de Comissões.** O `min-width` fixo saiu; a coluna de texto e o cabeçalho quebram
  linha; o número fica numa linha; o cabeçalho "Efeito no saldo" virou "Efeito" (o nome inteiro na dica).
  Nenhuma tabela das duas telas nem o histórico do cadastro rolam de 1180px para cima, e a suíte mede de 1280 e
  1440, no pior caso do histórico (saque aprovado e pagamento excluído, a frase mais comprida).
- **Levantamento das outras telas (somente leitura).** Em janela de 1280px, 25 das 83 telas ainda têm tabela
  que rola, no estado em que abrem: 11 de Estoque, 5 de Logística, 4 de Configurações, 3 de Vendas (CRM, Metas e
  Pedidos) e 2 de Finanças (Contas a Pagar e a Receber). Em 1440px, nenhuma. Não foram mexidas: esperam a decisão
  do usuário (PROGRESSO).
- **O histórico filtra por tipo**, além de mês e ano: inscrição, venda, comissão, saque, pagamento e
  lançamento, na conta do afiliado e na aba Afiliado do cadastro. Os três filtros se combinam, e o saldo de cada
  linha continua o verdadeiro.

**Provado nos dois sentidos, numa cópia.** As seções 8 e 9 de `teste_comissoes.py` cobrem o filtro por tipo e a
barra (nas quatro telas, em 1280 e 1440). Sete defeitos injetados, um por vez, e os sete pegos.

## 14.87 Comissões 2f: o pagamento vencido (19/out/2026)

Decisão B do usuário, de 15/out: a conta a pagar de comissão que vence **nunca se cancela sozinha**, porque o Pix pode já ter
saído sem a baixa lançada, e devolver o valor ao saldo faria pagar duas vezes.

- **O que é vencido.** O pagamento passou do vencimento, não está cancelado nem excluído, e a baixa não cobre o valor. Ele
  mostra "vencido há N dias" em vermelho (`.com-atraso`, o vermelho de texto, `--danger`). Pago em parte e vencido diz as duas
  coisas. O cálculo (`diasDeAtraso`, `situacaoDoPagamento`, `situacaoHtml`) é um bloco só, igual na lista, na conta do
  afiliado e no cadastro do cliente.
- **O quadro "Pagamentos vencidos"**, na lista de Comissões Afiliados, logo depois de "Pagamentos solicitados": o mais
  atrasado primeiro, com a conta, o que falta pagar, o vencimento e os dias de atraso. Três saídas:
  - **Dar baixa** abre a conta em Contas a Pagar com o painel da baixa já aberto (`?baixar=1`). A baixa continua tendo um
    dono só, que escreve no Caixa, e o pago volta para Comissões em `baixas` (§14.84).
  - **Reprogramar** pede o vencimento novo, de hoje em diante, pergunta antes e grava; a conta muda de data em Contas a
    Pagar, e o histórico guarda de quando para quando. É ação nova do catálogo (`comissaoReprograma`, "Reprogramar o
    vencimento de pagamento de comissão"), sem senha por padrão, nas 15 telas que carregam o catálogo: entra no Registro
    de atividades, e a senha pode ser ligada em Confirmações com senha.
  - **Cancelar** devolve o valor ao saldo e deixa a conta cancelada em Contas a Pagar, com senha (a mesma de realizar
    pagamento). Não aparece quando já houve baixa: estorna-se a baixa antes.
- **A conta do afiliado** mostra o atraso em vermelho, um aviso com quantos estão vencidos e quanto somam, e "dar baixa ·
  reprogramar" só no pagamento vencido. Para o cliente afiliado, uma linha diz o que a vitrine vai mostrar a ele:
  **Disponível** (o saldo de hoje), **Em pagamento** (o que falta pagar, com "em atraso" quando vencido) e **Pago**. A
  vitrine ainda não existe; a linha lê o mesmo banco que ela vai ler. O cadastro do cliente, na aba Afiliado, avisa
  "1 vencido".
- **Cancelar sozinho é opção, desligada.** Configurações → Cadastro de clientes → Programa de afiliados: "Cancelar sozinho o
  pagamento vencido", com o prazo (1 a 365 dias, 30 de fábrica). Ligada, cancela só o que não teve **nenhuma** baixa e venceu
  há o prazo ou mais; com baixa, o dinheiro saiu, e ele fica no quadro. O histórico diz "cancelado sozinho, vencido há N
  dias". No protótipo roda quando Comissões abre; no sistema de verdade será uma tarefa diária. Os dois parâmetros nasceram
  no mesmo dia que o código que os lê.
- **O exemplo de fábrica.** O vencimento de um pagamento feito na tela é sempre de hoje em diante, então sem exemplo não
  haveria como ver um vencido. Três pagamentos da vendedora Marina Costa nascem uma vez por navegador, contados a partir de
  hoje: R$ 50,00 vencido há 12 dias, R$ 30,00 vencido há 4 e R$ 40,00 que vence em 5. O bloco é o mesmo nas seis telas que
  leem os pagamentos (as duas de Comissões, o cadastro do cliente, as duas de Contas a Pagar e o Início). Efeito nas
  vizinhas: Contas a Pagar ganha COM-1 a COM-3, o saldo da Marina desce R$ 120,00, e o Início soma as contas de comissão ao
  número de contas a pagar atrasadas e ao de "em aberto, ainda no prazo" (lendo os pagamentos, e não um número digitado,
  para não desmentir Contas a Pagar quando alguém cancela ou dá baixa).
- **Achado no caminho: o link para Contas a Pagar escondia a conta.** O painel do fornecedor leva a Contas a Pagar com
  `?busca=`; o bloco comum da busca tira o período padrão clicando no botão "todos", mas em Contas a Pagar o período é um
  dropdown, e a lista abria em "vencem neste mês". A conta da TechParts, que vence em novembro, sumia em outubro. Agora o
  link abre em todos os períodos. A suíte `teste_cad_melhorias.py` já reprovava isso desde que a data virou.

**Regra que fica:** tela que mostra passagem do tempo (vencido, atrasado, há N dias) nasce com exemplo que já passou do
prazo, contado a partir de hoje; senão o usuário não tem como testar. Suíte que conta as contas de uma tela parte sem os
pagamentos de exemplo, e a suíte das comissões testa o estado de fábrica.

**Provado nos dois sentidos, numa cópia.** A seção 10 de `teste_comissoes.py` (71 asserções) cobre o exemplo de fábrica, o
quadro, a conta, a vitrine, dar baixa, reprogramar, cancelar, cancelar sozinho, Configurações, o catálogo, o Início, os
blocos repetidos e a barra de rolagem. Vinte e três defeitos injetados, um por vez, e os vinte e três pegos.

**Ajustes do teste (19/out/2026).** O usuário testou a 2f e aprovou. O "Reprogramar o vencimento" ganhou o calendário padrão (o mesmo campo de data de "Data inicial" e "Data final", com os dias antes de hoje riscados e não clicáveis), na lista e na conta, e os filtros do histórico deixaram de encostar no cabeçalho da tabela (16px na conta; a aba Afiliado do cadastro já tinha 14px). A seção 10 de `teste_comissoes.py` passou a ter 85 asserções, e os três defeitos injetados numa cópia (calendário ausente na lista, dia passado clicável, filtros colados na conta) foram pegos.

**Conserto de 19/out: o exemplo não nascia em navegador com pagamento gravado.** O usuário não viu os três pagamentos de exemplo: o bloco `semearPagamentosDeExemplo` saía assim que existia a chave `deskComissoesPagas`, e o navegador dele já tinha pagamentos gravados nos testes da 2b e da 2c. A regra nova: o exemplo tem **marca própria**, `deskComissoesExemplo` (valor `'1'`), e **acrescenta sem apagar**. Com a marca, sai. Sem ela, lê os pagamentos (ausente ou ilegível vale lista vazia); se já estão lá os três do exemplo antigo (Marina Costa, R$ 50, R$ 30 e R$ 40, num navegador semeado antes do conserto), só grava a marca e não duplica; senão acrescenta os três ao fim, com o `n` seguindo o maior que existe (lista vazia continua dando 1, 2 e 3). Excluído ou cancelado, o exemplo não volta; limpar o navegador traz de volta. O bloco continua o mesmo nas seis telas (a seção 10 de `teste_comissoes.py` confere o texto), e a chave entrou em `OK_LS` da auditoria. As suítes que partem de uma conta sem pagamentos gravam também a marca (`limpar()` de `teste_comissoes.py` e `teste_cp.py`), senão o exemplo nasceria em cima da lista vazia. A seção 10 ganhou quatro asserções: navegador com um pagamento e sem a marca recebe os três com n 2, 3 e 4; navegador com os três antigos continua com três; abrir de novo não duplica; cancelar e excluir não trazem o exemplo de volta.

## 14.88 A varredura da barra de rolagem (19/out/2026)

O usuário decidiu fazer a varredura que o levantamento de 15/out (§14.86) deixou esperando: nenhuma tabela rola na horizontal de 1280px de janela para cima, e a página nunca rola na horizontal.

- **Antes.** Medidas de novo, a 1280px (caixa de 826px), no estado em que a tela abre: **25 de 83 telas** tinham tabela rolando, e a 1440px nenhuma. Configurações (4): Categorias Financeiras, Contas Bancárias, Contas Financeiras e Formas de Recebimento. Estoque (11): Conferência de Entrada, Controle de Estoques e o detalhe, Endereçamento, Entrada de Notas, Giro de Estoque, Itens Bloqueados, Necessidades de Compra, Ordens de Compra, Reposição e Transferência. Finanças (2): Contas a Pagar e a Receber. Logística (5): Conferência de Saída, Devolução, Expedição, Rastreamento e Separação. Vendas (3): CRM, Metas e Pedidos. Quase todas com 920px de tabela, o `min-width` comum; as que passavam disso: Controle de Estoques 975, Devolução 986, Metas 984, Separação 966, Entrada de Notas 960 e Expedição 950.
- **O que foi feito.** Nas 22 telas que o bloco resolve, logo depois da regra comum `.estoque-table { min-width:920px }`, entrou o mesmo bloco de Comissões (`.main .estoque-table { min-width:0 }`, cabeçalho que quebra linha, coluna de texto que quebra linha), com o mesmo comentário. O CSS comum das outras 59 telas não foi mexido, nem o das que já passavam. **Nenhuma das 22 precisou de mais nada**: nem classe `col-texto` a mais, nem `min-width` próprio, nem cabeçalho encurtado.
- **O que o bloco não resolve (3 telas, esperam decisão do usuário).** Nelas o que segura a largura não é o `min-width` e sim texto que não quebra, e a tela ficou **como estava**. Necessidades de Compra (923px): o SKU e o código de barras sob o nome do produto, em uma linha só (regra da própria tela), e a caixa da quantidade a comprar, de 74px fixos; só com o SKU quebrando ela vai a 838px. CRM (920px): o `min-width:120px` das quatro colunas de texto, e os selos (`SEM INTERAÇÃO HÁ 40 DIAS`, `PERDIDO · PREÇO`, `ATRASADA · 17/10`) que não quebram; sem o `min-width` vai a 855px. Metas (984px): a barra de atingimento com `min-width:150px`, e as linhas de apoio sob o valor ("faltam R$ 20.900,00", "R$ 1.482,61 por dia para bater", "ticket R$ 159,38"); sem o `min-width` da barra vai a 868px. Em cada uma, deixar também a linha de apoio ou o selo quebrar linha (e, em Necessidades, a caixa de quantidade mais estreita) leva a tabela a 826px, medido numa janela de 1280.
- **Achados da primeira rodada.** (1) Três telas de documento têm outra classe de tabela, `.itens-table`, e ela rolava a 1280px (880px numa caixa de 826): o detalhe da Ordem de Compra, o do Pedido de Venda e o do Rastreamento. (2) Em Conferência de Saída e em Separação, a data com hora ("Fechou em", "Liberado em") passou a quebrar entre a data e a hora. (3) Em Devolução, a data de abertura quebra depois do "aberta em", com a data inteira; não é número quebrado. (4) Em Giro de Estoque o cabeçalho de oito colunas ficou em três linhas a 1280px (não mexido).
- **Segunda rodada, no mesmo dia.** (1) A `.itens-table` dos três detalhes ganhou o mesmo bloco, escrito para ela (`.main .itens-table`, com o mínimo comum de 880px que sai), e coube a 826px sem mais nada. (2) O detalhe do Controle de Estoques, aberto com registro (`?id=`), também cabe: o que se media como 920px era a medição de antes do bloco. (3) A data com hora das duas telas de Logística ganhou a classe `col-nowrap` (`white-space:nowrap`, no bloco da varredura) na célula daquela coluna, e a tabela continua cabendo. (4) **O campo cortado, achado na revisão.** Nos detalhes da Ordem de Compra e do Pedido de Venda, o campo do nome do produto tinha a largura dos outros e cortava o nome, e isso já acontecia antes da varredura, até em 1440. O nome ganhou largura (`th:nth-child(1) { width:19% }` na Ordem, `th:nth-child(2) { width:30% }` no Pedido) e o campo pode encolher (`min-width:0`): em 1440 nenhum campo corta, com registro aberto ou sem. Em 1280 os campos inteiros pedem uns 986px de tabela para 826 de cartão; sem barra, o código comprido (SKU, GTIN) corta alguns caracteres. O usuário decidiu no mesmo dia deixar assim, e também a barra das 3 pendentes: o custo é só de leitura em 1280, e volta na produção. A suíte passou a medir também o campo cortado na tabela dos itens, a 1280 e 1440, e nesses dois detalhes só a 1440; sem a largura do nome, ela reprova.
- **A suíte.** `teste_barra_tabelas.py`, no selo (varre a pasta): abre cada tela no estado em que ela abre, a 1280 e a 1440 de largura, e mede o que a seção 9 de `teste_comissoes.py` mede (cada `.estoque-table-wrap` e `.contatos-table` visível, tabela contra a caixa, e a própria página), mais a `.itens-table`. Desde a segunda rodada mede também os quatro detalhes que só mostram a tabela com registro aberto (`?id=1`): Ordem de Compra, Pedido de Venda, Rastreamento e Controle de Estoques. Uma asserção por tela (87 ao todo), com a medida na mensagem. As três telas pendentes ficam numa lista `PENDENTES`, e a suíte exige que **continuem rolando**: no dia em que uma passar, ela reprova até a tela sair da lista, para a exceção não ficar esquecida. Limite: mede só o estado em que a tela abre; aba, painel e modal têm a medida na suíte de cada tela.

**Provado nos dois sentidos, numa cópia.** Tirar o bloco de Ordens de Compra (920 > 826) e depois o de Contas a Pagar (900 > 826), um por vez, fez a suíte sair com 1 e reprovar a tela certa; o projeto real sai com 0. Na segunda rodada, tirar o tratamento de cada um dos quatro detalhes, um por vez, reprovou o detalhe certo, com e sem `?id=1` onde a tela mostra a tabela sem registro (880 > 826 na `.itens-table`, 920 > 826 no Controle de Estoques).


## 14.89 Vale-compra, entrega 1: o vale nasce à mão e se vê (19/out/2026)

Barganha aprovada pelo usuário em 19/out, com as quatro recomendações dele. O vale-compra (crédito na loja) liga o "Vale-troca" que Devolução, Formas de Recebimento e PDV deixam reservado, e o pagamento de comissão como crédito. Ele é feito em **três entregas**; esta é a primeira: (1) o vale nasce à mão e se vê; (2) o vale se usa, no PDV e no Pedido de Venda; (3) o vale nasce da Devolução e do pagamento de Comissão. Ele não mandou prints do Olist: a tela é desenho nosso, no molde de Comissões Afiliados.

**Decisões dele (não se reabrem):**

- **O vale é saldo do cliente, sem código.** Cada vale tem número (VC-1, VC-2…), cliente, **loja que emitiu**, origem (devolução, comissão ou cortesia), valor, emissão, vencimento, usos e situação. Só vale na loja que o emitiu, porque cada loja tem o seu caixa e a comissão de afiliado já é por loja.
- **Situações:** *disponível* (tem saldo e não venceu), *usado* (saldo zero), *vencido* (passou do vencimento com saldo) e *cancelado*. **Saldo do vale** = valor menos a soma dos usos. **Saldo do cliente numa loja** = a soma do saldo dos vales *disponíveis* dele naquela loja. O cálculo mora num bloco só (`valeSituacao`, `valeSaldo`, `valeSaldoDoCliente`), igual nas três telas.
- **Validade ajustável**, em Configurações → Cadastro de clientes → seção **Vale-compra**: "Validade do vale", em dias, de 1 a 3650, **180 de fábrica**, gravada em `deskParametros.valeCompraValidadeDias`, o mesmo lugar dos outros parâmetros de lá. Um prazo só, para todas as lojas. **O vencimento é fixado na emissão:** mudar o prazo vale para os vales novos e não muda os que já existem (a dica do campo diz isso). O parâmetro nasceu no mesmo dia que o código que o lê.
- **Menu: Finanças, logo depois de Comissões Afiliados**, com o nome "Vale-compra", nas 86 telas (as duas novas e o molde de referência entre elas). O Vale-compra é **fora da contagem de 55 itens** do roadmap: era um submódulo extra, decidido em 14/out. A seção 10 de `teste_menu.py` passou a descontá-lo, e o `PROGRESSO.md` segue dizendo 43 de 55.

**A lista** (`pagina-financas-vale-compra.html`). Três indicadores, que somam **todos** os vales e não se mexem com a busca, a loja nem a aba: o **saldo em vales** (R$ e quantos vales disponíveis), **os que vencem em 30 dias** (quantos, e quanto somam; entra o que vence hoje e o que vence no trigésimo dia) e **os vencidos com saldo** (quantos e quanto). Filtros como as outras listas: busca por cliente, documento ou número do vale (sem acento, "VC-3" acha o VC-3; texto com letra não procura documento), **loja** e **origem** em dropdown próprio, e as **abas de situação com contagem** (todos, disponíveis, usados, vencidos, cancelados), cujos contadores contam o que a busca, a loja e a origem deixam passar. A tabela tem nº, cliente (com o documento abaixo, como Pedidos), loja, origem, emitido, vence, valor, usado, saldo e situação; "vence em N dias" e "vencido há N dias" como na 2f, **o vencido em vermelho** (`.com-atraso`, `--danger`). Abre do mais novo para o mais velho; a primeira coluna de número clica do maior para o menor, como as outras. A linha abre a página do vale. O recuo lateral das células desta tabela é de 6px (o comum é 8px): com dez colunas, é o que faz caber R$ 12.345,67 e nome longo no cartão de 826px a 1280px de janela, sem barra. A impressão é a do bloco comum (§14.75): título, data, quem emitiu, os filtros e a quantidade; a planilha leva as colunas e as linhas da tela. Sem paginação: o exemplo tem cinco vales, e a lista só vai precisar dela com o banco.

**Incluir vale** (cortesia), botão do topo e painel lateral: **cliente** pela busca padrão (a de produto de Movimentação de Estoque, agora de cliente: nome, CPF/CNPJ ou e-mail, até oito sugestões, Enter escolhe a primeira, mexer no texto desfaz a escolha, o "x" tira o cliente; texto que só casa com um cliente já é a escolha), **loja**, **valor** maior que zero com até duas casas e **motivo** obrigatório. **O vencimento** (hoje mais o prazo de Configurações) **aparece no painel antes de confirmar**, com o link para a configuração. Ação nova do catálogo, `valeCompraIncluir`, **com senha por padrão**. Feito o vale, a lista limpa os filtros e abre nele.

**A página do vale** (`pagina-financas-vale-compra-detalhe.html?id=n`). Dados (cliente, que é link para o cadastro dele na aba Vale-compra; loja; origem, com o motivo se for cortesia e o documento de onde nasceu quando houver, que é link; valor; emitido; vence, com "vence em N dias" ou "vencido há N dias"; usado; saldo; situação), **Usos** (data, documento, valor usado e o saldo depois de cada um; o documento é link para o pedido) e **Histórico** (emitido, usado, venceu, reativado de quando para quando, cancelado com o motivo), do mais novo para o mais velho. Um aviso diz o que a situação pede (o vencido explica o que reativar faz; o cancelado diz o motivo). Endereço sem vale que exista diz isso, esconde os quadros e não abre outro vale no lugar. **O "Voltar" leva de volta o estado da lista** (busca, loja, origem e aba), que a lista passa no endereço (`q`, `loja`, `origem`, `sit`); a lista abre com o que o endereço traz e ignora o que não existe. **Cancelar** só com saldo, cancela o saldo que resta (o valor e os usos ficam como estavam), pede motivo e senha, e **não se desfaz**; **Reativar** só vale para o vencido, dá o vencimento novo de hoje mais o prazo de Configurações e pede senha. A ação que não vale para a situação do vale some do "Mais ações" e também não abre por fora do menu. As duas são ações novas do catálogo, `valeCompraCancelar` e `valeCompraReativar`, **com senha por padrão**, e entram no Registro de atividades.

**A aba Vale-compra do cadastro do cliente**, ao lado de Afiliado: **saldo por loja** (só os vales disponíveis daquela loja; não há linha de total, porque o vale não se junta entre lojas), a **lista dos vales** dele (o número é link para a página do vale) e o link **"Ver em Vale-compra"**, que abre a lista filtrada pelo cliente com a faixa "Mostrar tudo" do bloco comum de busca pelo endereço. `?aba=vale` abre o cadastro já nela (é o link que a página do vale usa). **Só lê**, e funciona com o cadastro em modo leitura e em edição.

**O catálogo de ações auditáveis** ganhou `valeCompraIncluir` ("Incluir vale-compra de cortesia"), `valeCompraCancelar` ("Cancelar vale-compra") e `valeCompraReativar` ("Reativar vale-compra vencido"), nas **17 telas** que o carregam: as 15 que já tinham `comissaoReprograma` (Confirmações com senha e Registro de atividades entre elas) e as duas novas. As três aparecem em Configurações → Confirmações com senha, onde se liga e se desliga a senha de cada uma; desligada, a confirmação aparece sem o campo de senha e o registro grava a ação sem a marca de senha.

**Os dados.** Uma chave só no navegador, `deskValesCompra` (`{ vales: [...] }`), lida pelas três telas com um bloco idêntico (`VALE-COMPRA: DADOS E REGRAS`), como o bloco dos pagamentos de comissão; escrevem a lista (incluir) e a página do vale (cancelar e reativar), o cadastro só lê. A chave e a marca do exemplo entraram em `OK_LS` da `auditoria.py`. Cada vale: `{ n, clienteId, cliente, doc, loja, origem, motivo, ref, valor, emitido, venc, usos, reativacoes, cancelado }`; `ref` (`{ texto, href }`) é o documento de onde o vale nasce nas origens devolução e comissão, que as entregas seguintes vão preencher.

**Os exemplos** nascem **uma vez por navegador**, com marca própria (`deskValesCompraExemplo`) e **acrescentando sem apagar**, o mesmo desenho do conserto de 19/out da §14.87: com a marca, saem; sem ela, lê o que há (ausente ou ilegível vale lista vazia) e acrescenta os cinco ao fim, com o `n` seguindo o maior que existe; tirado ou cancelado, o exemplo não volta; limpar o navegador traz de volta. Contados a partir de hoje, com o prazo de fábrica de 180 dias, e numerados na ordem em que foram emitidos:

| nº | cliente (id no cadastro) | loja | valor | situação |
|---|---|---|---|---|
| VC-1 | Camila Rêgo (7) | Desk Brands | R$ 50,00, emitido há 200 dias | **vencido** com saldo: venceu há 20 dias |
| VC-2 | Rafael Nogueira (2) | Desk Shope | R$ 40,00, emitido há 60 dias | **usado** inteiro: R$ 25,00 no Pedido nº 16 (há 28 dias) e R$ 15,00 no Pedido nº 3 (há 2 dias) |
| VC-3 | Auto Peças Imperatriz Ltda (11) | Desk Tech | R$ 80,00, emitido há 40 dias | **disponível**, usado em parte: R$ 30,00 no Pedido nº 10 (há 11 dias), saldo R$ 50,00 |
| VC-4 | Marina Duarte (1) | Desk Shope | R$ 120,00, emitido há 20 dias | **disponível** |
| VC-5 | Juliana Prado (4) | Desk Brands | R$ 60,00, emitido há 15 dias | **cancelado**, com o motivo "Emitido em duplicidade" |

Os cinco são cortesia: a Devolução de exemplo só tem clientes que não estão no cadastro (Mariana Rocha, Pedro Antunes…), então nenhuma devolução vira vale agora. Os clientes (id, nome e documento) são os do cadastro de Clientes e as lojas são as de Lojas Desk; os três usos citam pedidos que existem em Pedidos de Venda, **do mesmo cliente, da mesma loja e no dia da venda** (a data do uso é a data do pedido; por isso o uso do VC-3 é de 11 dias atrás, e não dos 10 do plano: o Pedido nº 10 é de 11 dias atrás). A suíte confere tudo isso contra as telas donas. **O exemplo não altera nenhuma outra tela.** Com ele, de fábrica, o saldo em vales é R$ 170,00 (2 vales), nenhum vale vence em 30 dias (o prazo é de 180 e o mais antigo que tem saldo foi emitido há 40 dias) e há 1 vencido de R$ 50,00. As suítes que contam coisas dessas telas partem sem os exemplos (gravando a marca); a suíte nova testa o estado de fábrica.

**O que ficou para as entregas 2 e 3.** Entrega 2: usar o vale como forma de pagamento no PDV e no Pedido de Venda (em parte, se o cliente quiser, e a sobra continua valendo), em Configurações → Formas de recebimento, e o desaparecimento do "Vale-troca" reservado que Devolução, Formas de Recebimento e PDV mostram desabilitado. Entrega 3: o vale nascer da Devolução (o ressarcimento que vira crédito) e do pagamento de comissão de afiliado como crédito na loja, com os documentos de origem como link. Nesta entrega os usos são só os de exemplo, e as origens devolução e comissão existem no filtro e no desenho, mas nenhum vale tem essas origens ainda. Nada de PDV, Pedidos, Devolução, Formas de Recebimento, Contas a Receber nem do "Vale-troca" reservado foi mexido.

**Decisões que couberam a quem construiu, para o usuário confirmar:** (1) **a busca padrão de cliente**: o sistema só tem a busca padrão de produto, então o cliente ganhou a mesma, com nome, CPF/CNPJ ou e-mail; (2) **os filtros voltam pelo endereço**, porque Comissões não guarda filtro nenhum entre a lista e a conta, e o "mantendo os filtros" pedia um mecanismo; (3) os indicadores **não filtram** a lista ao clicar (o plano pediu só os números); (4) a data do uso do VC-3 (11 dias, e não 10), pelo motivo acima.

**O que a entrega mexeu nas suítes que já existiam, e por quê.** `teste_menu.py`: a lista de ordem do menu de Finanças ganhou "Vale-compra" depois de "Comissões Afiliados", e a seção 10 desconta o Vale-compra da contagem de itens (continua 43 de 55). `teste_comissoes.py`: o catálogo está em 17 telas, e não mais em 15 (as duas novas carregam o catálogo inteiro). `teste_impressao.py`: 23 telas com o bloco comum, 17 listas e 6 documentos; o CSS do vale entra **antes** do bloco do relatório de impressão, porque a suíte compara o CSS do relatório do marcador dele até o fim da folha de estilo, e CSS acrescentado depois dele a faria divergir. `teste_busca_setas.py`: a busca de cliente do Incluir vale é a sexta caixa de sugestões do sistema, e a lista ganhou o bloco das setas do teclado (o mesmo das outras cinco). `auditoria.py`: as duas chaves entraram em `OK_LS`. **Achado da auditoria oficial:** a classe da situação, montada como `class="badge-situacao vc-sit-' + s + '"`, aparece para ela como a classe `vc-sit-` sem CSS; o nome da classe passou a ser montado por `valeClasseSit(s)`, no bloco comum, e o atributo `class` só traz nomes inteiros.

**Provado nos dois sentidos, numa cópia.** `teste_vale_compra.py` (entra no selo, 223 asserções) tem nove seções: o exemplo de fábrica e os espelhos, os indicadores refeitos em Python, a busca e as abas e o estado pelo endereço, incluir, a página do vale com cancelar e reativar, Configurações, a aba do cliente, o menu e o catálogo, e o bloco idêntico, a impressão e a barra de rolagem. Numa cópia das telas fora do projeto, com `DESK_PASTA`, **23 defeitos injetados, um por vez, e os 23 pegos** (a cópia sem defeito passa nas nove seções): o vencido sem vermelho, cancelar sem senha, reativar sem vencimento novo, o saldo do cliente somando outra loja (nas três cópias do bloco), o prazo ignorado (nas três), o exemplo duplicando (nas três), o item de menu fora de posição, "usado" que não vira usado (nas três), cancelar sem motivo, os vencidos contando nos que vencem em 30 dias, incluir aceitando valor zero, o "Voltar" que perde os filtros, a aba do cliente sumindo em modo leitura, reativar aparecendo em todo vale, cancelar levando o valor inteiro e não o saldo, a ação sem senha que não vai para o registro, Configurações aceitando prazo zero, uma tela sem uma das três ações no catálogo, o filtro de origem ignorado, os contadores das abas ignorando a loja, o bloco divergente só no cadastro do cliente, a barra de rolagem voltando e o vencimento do exemplo que deixa de ser fixado na emissão. Selo: 54 suítes, 5.787 asserções.

**Ajustes do teste (19/out/2026).** O usuário testou a entrega 1 e pediu três ajustes na lista, mais a mesma barra de paginação em quatro outras listas, tudo na mesma rodada. **(1) O painel lateral ao clicar na linha**, no padrão de Comissões Afiliados (`#drawerBackdrop` + `#eventDrawer`, fechar pelo "fechar", pelo fundo e pelo Esc do componente comum da §14.68): título "Vale-compra VC-n" com o selo da situação; cliente (com documento, link para a aba Vale-compra do cadastro, `?aba=vale`), loja ("o vale só vale nesta loja"), origem (cortesia com o motivo), valor, usado, saldo, emitido, vence ("vence em N dias" ou "vencido há N dias" em vermelho, a mesma função da lista) e os três últimos usos (data, documento, valor; o documento é link para o pedido, como na página do vale). O botão principal, "Ver vale completo", é o endereço que a linha usava, com os filtros, e o "Voltar" continua devolvendo a lista como estava. Cancelar e Reativar **ficam só na página do vale**; a aba do cadastro do cliente continua indo direto para a página. **(2) Os indicadores filtram a lista**, no padrão de Contas a Pagar (cartão com `role="button"`, cursor de mão, estado aceso `.on` + `aria-pressed`, clicar de novo desfaz, Enter e espaço funcionam): *Saldo em vales* acende a aba Disponíveis; *Vencem em 30 dias* mostra os disponíveis que vencem em até 30 dias (não há aba para isso: a aba Disponíveis acende e o cartão marca o recorte, e a folha impressa diz "Indicador: Vencem em 30 dias"); *Vencidos com saldo* acende a aba Vencidos. O indicador combina com a busca, a loja e a origem (diferente de Contas a Pagar, que limpa a busca: aqui a busca e os filtros ficam); clicar numa aba, ou em Limpar filtros, tira o recorte. O recorte vai no endereço (`kpi=saldo|venc30|vencido`) para a página do vale e volta no "Voltar". Os números dos indicadores continuam os de sempre, sobre todos os vales. **(3) A barra de paginação padrão** (`.paginacao-bar`, copiada de Contas a Pagar e de Controle de Estoques: "Mostrando 1–10 de N", "Por página" 10, 25, 50 e 100 com o padrão de Configurações → Interface do usuário, anterior, "Página 1 de N", próxima), com a contagem e o "Saldo do filtro" mantidos e somando o **filtro inteiro**; a página volta a 1 quando muda a busca, a loja, a origem, a aba, o indicador ou a ordem, e a planilha e a impressão leem a lista inteira pelo adaptador `PLANILHA_PAGINA` do bloco comum.

**A mesma barra de paginação em mais quatro listas** (pedido do usuário na mesma rodada, cópia da de Contas a Pagar, com a contagem e o total do rodapé mantidos e somando o filtro inteiro): **Comissões Afiliados** (só a lista principal; os quadros de inscrições, pagamentos solicitados e pagamentos vencidos não paginam), **Reposição**, **Transferência Entre Estoques** e **Metas e Performance** (a lista de lojas ou de vendedores é uma lista como as outras: nenhuma linha depende das outras na tela, o aviso de metas que não fecham e os indicadores leem os dados e não a tabela). Reposição e Transferência não têm planilha nem impressão (o menu só avisa que entram com Relatórios de Estoque), então nelas não há o que ligar ao adaptador; Comissões e Metas ligaram `PLANILHA_PAGINA`. **Achado em Comissões:** a planilha e a impressão levavam a *primeira tabela a vista*, que com inscrição pendente era a das inscrições, e não a lista. A tela ganhou `linhasDaPlanilha()` (o gancho que o bloco comum já aceita), que lê a tabela da lista.

**Provado nos dois sentidos, numa cópia.** `teste_vale_compra.py` ganhou três seções (10: o painel; 11: os indicadores; 12: a paginação, com 27 vales semeados), `teste_comissoes.py` a 11 (22 afiliados semeados), `teste_transf_conferencia.py` a 8 (12 transferências), `teste_metas.py` a 13 (12 vendedores) e a suíte nova `teste_reposicao.py` (as 18 bases de exemplo já dão duas páginas). Defeitos injetados numa cópia, um por vez, e **22 pegos**: no Vale-compra, 13 (a linha ainda navega direto, o Esc não fecha, o painel com saldo errado, "Ver vale completo" sem os filtros, o indicador que não filtra, o recorte de 30 dias que inclui o vencido, o recorte fora do endereço, o "Voltar" que perde o indicador, a aba que não tira o recorte, o seletor de quantidade sem efeito, o saldo do filtro somando só a página, a impressão só com a página, a loja que não volta à página 1); em Comissões, 4 (o saldo só da página, a impressão só da página, a planilha na tabela errada, o tipo que não volta à página 1); em Transferência, 2; em Reposição, 2; em Metas, 1. Dois defeitos escaparam na primeira rodada (o recorte de 30 dias e a loja que não volta à página 1), porque a aba e o ajuste da última página os escondiam; as suítes ganharam as asserções que os pegam (o recorte pelo endereço sem aba, os números absolutos dos indicadores, e a busca que ainda deixa todas as linhas). Um defeito de Metas (trocar de aba sem voltar à página 1) é equivalente ao certo: a aba Lojas tem uma página só e ajusta a página sozinha. `teste_vale_compra.py` passou a 317 asserções; `teste_comissoes.py`, 256; `teste_transf_conferencia.py`, 87; `teste_metas.py`, a lista com a seção 13; `teste_reposicao.py`, 17 (entra no selo); `teste_esc_painel.py` e `teste_barra_tabelas.py` (89) e o selo, verdes.

## 14.90 Vale-compra, entrega 2: o vale se usa (19/out/2026)

Decisões do usuário (não se reabrem): no **PDV**, o cliente escolhido mostra o saldo de vale dele **na loja do PDV**, e dá para usar tudo ou **uma parte** (a sobra continua no vale); no **Pedido de Venda**, o vale **desconta ao salvar** e **cancelar o pedido devolve**; a parte paga com vale **aparece em Contas a Receber como título já recebido**, forma "Vale-compra", e **não entra no Caixa** (o vale não é dinheiro novo); o nome é **Vale-compra** onde estava "Vale-troca" (a chave interna `valetroca` fica). A Devolução continua com o vale reservado e o nome antigo: é a entrega 3.

**O bloco comum** (`VALE-COMPRA: DADOS E REGRAS`) passou de 3 para **8 cópias idênticas** (lista e página do vale, cadastro do cliente, PDV, Pedido de Venda lista e página, Contas a Receber lista e detalhe) e ganhou o uso. O uso é `{ data, valor, doc: { tipo: 'pedido' | 'pdv', id, rotulo }, estornado?: { em, motivo }, perdido?: { em, motivo } }`; uso gravado antes (`{ documento, pedidoId }`) é convertido na leitura. `usarVale(cliId, lojaId, valor, doc)` gasta do vale que **vence primeiro** e segue para o próximo, devolve `[{ n, valor }]` e, se passa do saldo da loja ou não grava, lança erro sem gravar nada. `estornarUsos(doc, motivo)` marca o uso como estornado e o valor volta ao saldo; vale vencido recebe e continua vencido; **vale cancelado não recebe**: o uso fica `perdido` (continua contando como usado, o saldo segue em zero) e o histórico diz que o valor não voltou. Saldo e situação ignoram o estornado. Também `valeUsosDoDoc`, `valeTodosUsos` e `valeDocHref` (o pedido abre na página dele; a venda do balcão, no Pedido que o PDV gera, `900000 + número`).

**PDV.** No cartão de Recebimentos, o quadro "Vale-compra disponível R$ X, vence dd/mm/aaaa", com o campo (de fábrica o menor entre o saldo e o que falta pagar, sem contar o vale) e "Usar". Vale só de outra loja vira a linha "R$ X em vales da <loja>, que não valem nesta loja"; sem cliente ou sem saldo, nada. "Usar" valida (maior que zero, até o saldo na loja, até o que falta) e vira um recebimento Vale-compra (destino `vale`: nem conta, nem título em aberto); o vale não está no menu "Adicionar recebimento". Trocar de cliente tira o vale da venda; a pendência acusa saldo que mudou em outra aba. O uso só é gravado em `gravarVenda` (se falhar, a venda não grava), com `doc = PDV-000n`; "o que a venda gerou" diz "R$ X pagos com vale-compra (VC-n); o saldo do vale fica em R$ Y. Título já recebido em Contas a Receber, sem entrar no Caixa". Cancelar a venda só vale antes de gravar: nada a estornar. **Turno:** o vale não entra na gaveta nem pede contagem (`esperadoPorForma` o pula); "Detalhes do caixa" mostra uma nota "Vale-compra: R$ X usados em N vendas".

**Pedido de Venda.** Abaixo de Forma de recebimento e Condição de pagamento, o quadro com o saldo do cliente **na loja do pedido** (o cliente se acha pelo nome: o pedido não guarda o número do cadastro) e o campo "Usar do vale"; mudar cliente ou loja refaz o quadro. As parcelas e a prévia valem só para **o que falta** (total menos vale), e a prévia diz "R$ X pagos com vale-compra"; o limite de crédito também olha só o que falta. O pedido aberto com usos mostra "Pago com vale-compra: R$ 30,00 (VC-3)", com link para o vale (em leitura o quadro vira só o texto). Salvar valida (até o saldo mais o que o próprio pedido já usava, até o total), estorna o uso anterior ("pedido alterado") e grava o novo; o valor igual ao que já estava não refaz nada; se o uso falhar, o armazenamento volta como estava e o pedido não salva. Pedido novo ganha o número seguinte ao maior da lista ou do vale (o pedido não é gravado). Cancelar estorna ("pedido cancelado") e a confirmação diz "R$ X voltam para o vale VC-n" (ou "não voltam: o vale está cancelado"). Venda do balcão aberta no Pedido só mostra o texto.

**Formas de Recebimento.** `valetroca` virou Vale-compra, do sistema, habilitada, destino `vale` ("Consome o vale do cliente"): conta, vencimento, taxa, antecipação e limite somem no painel, e a opção de destino só existe para ela. Os dois avisos de "reservada" saíram. O espelho do PDV é igual ao cadastro (a suíte compara), o do Pedido é `FORMA_VALE`.

**Contas a Receber.** Cada uso vira um título **já recebido** (forma Vale-compra, categoria Venda de mercadorias, cliente do vale, emissão e vencimento no dia do uso, "Pago com vale-compra VC-n"); uso estornado ou perdido vira título **cancelado**. Id `9000 + n do vale × 100 + posição do uso` (estável: o uso só se acrescenta), recebimento sem conta, nada no Caixa. O detalhe é **só leitura** (sem baixa, estorno, edição, cancelar nem excluir; faixa com o caminho "o valor muda no pedido ou no vale"), e a seleção em massa não cancela nem exclui título de vale. O título de exemplo 9 (PV 7) passou de Vale-troca em aberto para **Crediário**.

**Decisões que couberam a quem construiu, para o usuário confirmar:** (1) o id do título é `9000 + n×100 + posição`, e não `9000 + n`, porque um vale tem vários usos; (2) o histórico do vale lista o estorno no lugar do "Usado" do uso estornado, e o perdido como "Perdido"; (3) o limite de crédito do Pedido passa a olhar só o que falta depois do vale; (4) o resumo do turno leva uma nota para o vale, em vez de uma linha na tabela de contagem; (5) o cliente do Pedido se acha pelo nome.

**Conserto na revisão: todo caminho que tira o pedido devolve o vale.** Antes só o botão Cancelar devolvia. Agora **excluir o pedido** ("pedido excluído") e **mudar a situação para Cancelado à mão** ("pedido cancelado") chamam `estornarUsos`, com a mesma frase na confirmação ("R$ X voltam para o vale VC-n" ou "não voltam: o vale está cancelado"); na **lista de Pedidos**, excluir e cancelar em massa fazem o mesmo, e não tocam no vale de pedido que a seleção pula. Se a situação sair de Cancelado para outra, o vale **não** volta a ser usado sozinho: o quadro abre vazio e diz "O vale deste pedido foi devolvido; para usar de novo, informe o valor e salve". A lista de Pedidos ganhou a 8ª cópia do bloco comum.

**Provado nos dois sentidos, numa cópia.** `teste_vale_uso.py` (entra no selo) e as suítes que mexeram: `teste_vale_compra.py` (bloco idêntico nas oito cópias e uso no formato novo) e `teste_formas_recebimento.py` (Vale-compra habilitada, destino próprio, desabilitar). Defeitos injetados: 8 por vez, numa cópia das telas fora do projeto (a cópia sem defeito passa nas sete seções), e os 8 foram pegos: vale de outra loja usável (o filtro de loja some de `usarVale`), uso passando do saldo, estorno que não volta ao saldo, cancelar o pedido sem estornar, parcelas pelo total e não pelo que falta, editar o pedido sem estornar o uso antigo, vale entrando no Caixa pela venda do PDV, e título de vale editável. No conserto, mais 4, também pegos: excluir o pedido sem devolver, situação à mão sem devolver, e excluir e cancelar em massa na lista sem devolver. `teste_vale_uso.py`: 146 asserções; `teste_vale_compra.py`, 317; `teste_formas_recebimento.py`, 130; PDV 200, Pedidos 128, Contas a Receber 61. Selo: 56 suítes, 6.110 asserções, nenhuma falha. **De passagem:** `teste_comissoes.py` reprovou quando o dia virou para 20/out, sem mudança na tela. A seção 8 usava os dias 1 a 5 do mês, e o exemplo é datado a partir de hoje: nessa janela não sobrou comissão liberada e a linha "(+) Comissões do período" some quando é zero. A janela passou a ser a primeira do mês com comissão liberada; a asserção é a mesma.

## 14.91 Vale-compra, entrega 3: o vale nasce da Devolução e do pagamento de Comissão (20/out/2026)

Barganha aprovada pelo usuário em 20/out, com as cinco recomendações dele (não se reabrem): **(1)** Devolução: o vale nasce **ao finalizar**, com o total da devolução (itens mais frete devolvido, menos desconto), na loja do pedido de origem; escolher a forma só anota. **(2)** Devolução finalizada com vale e depois cancelada: o vale intacto é cancelado junto; vale já usado, mesmo em parte, **impede** cancelar a devolução (o caminho é um acerto). **(3)** Comissão: **só o afiliado** recebe em vale (vendedor é funcionário, e comissão de funcionário é salário, em dinheiro). **(4)** Sem bônus: R$ 100 de comissão são R$ 100 de vale, na loja da comissão. **(5)** A comissão paga em vale aparece em Contas a Pagar **já paga**, forma Vale-compra, só leitura, sem saída do Caixa nem de conta financeira (o espelho do que a entrega 2 fez em Contas a Receber).

**O bloco comum** (`VALE-COMPRA: DADOS E REGRAS`) passou de 8 para **10 cópias idênticas** (as oito de antes mais o detalhe da Devolução e o detalhe de Comissões Afiliados) e ganhou três funções. A `ref` do vale ganhou `tipo` (`devolucao` ou `comissao`) e `id` (o id da devolução; o `n` do pagamento COM-n): `{ tipo, id, texto, href }`. **`valeDaOrigem(tipo, id)`** acha o vale do documento (o mais novo, em qualquer situação) ou devolve `null`. **`emitirVale({ clienteId, cliente, doc, loja, origem, ref, valor })`** valida (valor maior que zero, loja em `VALE_LOJAS`, cliente presente, documento de origem presente e **nenhum vale não cancelado com a mesma ref**, a trava contra emitir duas vezes), cria o vale com o `n` seguinte, emissão de hoje e vencimento de hoje mais o prazo de Configurações, grava e devolve; falhando, lança erro e **não grava nada**. **`cancelarValeDaOrigem(tipo, id, motivo)`** lança erro com o valor usado se o vale já foi usado (mesmo em parte); senão grava `cancelado = { em, motivo, saldo }`; sem vale, ou com o vale já cancelado, não faz nada. No detalhe de Comissões o bloco mora logo depois do bloco "Comissões: dados e regras" (que a suíte compara até o marcador seguinte), e não dentro dele.

**Devolução** (`pagina-logistica-devolucao-detalhe.html`, mais o rótulo na lista). A forma `valetroca` virou **Vale-compra** ("gera um vale-compra para o cliente, na loja do pedido"); o bloco "Reservado" e o aviso de reservado saíram, e o ramo morto "Vales-troca ainda não tem tela" da lista também. A opção fica **marcada como indisponível**, com o motivo no hint da forma e num aviso a quem a escolhe, quando: a forma Vale-compra está desabilitada em Formas de Recebimento (espelho `FORMA_VALE`); o cliente da venda não está no cadastro (achado por CPF/CNPJ num espelho de Clientes, `CLIENTES_VALE`); a loja não emite vale (a Desk Flash); ou o total a devolver é zero. **Finalizar** com a forma Vale-compra confirma "Gera o vale-compra de R$ X para <cliente>, na <loja>, válido até dd/mm/aaaa" (a senha de `devolucaoFinaliza` continua) e chama `emitirVale` (origem devolução, ref com o link da devolução); **se o vale não puder nascer, a devolução não finaliza** e a tela diz o motivo. O histórico diz "Finalizada. Vale-compra VC-n de R$ X", e o cartão de valores ganha a linha "Vale-compra VC-n · R$ X · saldo R$ Y" com o link para `pagina-financas-vale-compra-detalhe.html?id=n`. A devolução de exemplo não é gravada, o vale é: ao abrir, se `valeDaOrigem('devolucao', id)` existe, a devolução aparece **finalizada** com a forma Vale-compra (ou **cancelada**, se o vale foi cancelado pelo cancelamento da devolução, o que se distingue pelo motivo `devolução cancelada`), e por isso recarregar não deixa finalizar de novo nem gerar outro vale. **A forma não muda depois de finalizada com vale** (o campo trava). **Cancelar:** com o vale intacto, a confirmação acrescenta "O vale-compra VC-n (R$ X) é cancelado junto." e o vale é cancelado; com vale usado, o aviso diz "O vale-compra VC-n já foi usado (R$ X de R$ Y). O crédito foi gasto: cancelar a devolução agora deixaria o cliente com a compra e o ressarcimento. O caminho é um acerto." As travas de antes (estoque já lançado) continuam na frente. Cancelar o vale à mão, na página do Vale-compra, **não** cancela a devolução.

**Comissões Afiliados** (`pagina-financas-comissoes-detalhe.html`). O menu da forma do "Realizar pagamento" ganha **Vale-compra só para o afiliado** cuja forma está habilitada, que tem cliente no cadastro e loja que emite vale; **para o vendedor a opção nem existe no menu** (e, forçada, é recusada). Escolhida, o hint diz "Vira vale-compra de R$ X na <loja>, válido até dd/mm/aaaa. Nada sai do Caixa.", o vencimento fica hoje e travado e a chave Pix some do painel. Ao realizar, a ordem é atômica: guarda o texto dos vales, emite o vale (origem comissão, ref `Comissão COM-n`, link para a conta do afiliado) e grava o pagamento, que **nasce pago**: `forma: 'Vale-compra'`, `vale: n`, `venc: hoje` e `baixas: [{ data, valor, contaId: null, juros: 0, desconto: 0, forma: 'Vale-compra', vale: n }]`, no mesmo formato das baixas de Contas a Pagar, sem conta financeira. Se o pagamento não gravar, os vales voltam ao texto guardado e nada se registra; se o vale não nascer, o pagamento não é registrado. Aviso: "Pagamento COM-n: R$ X em vale-compra VC-n para <nome>, na <loja>. Nada saiu do Caixa." A lista de pagamentos e o histórico (nas três cópias do bloco de dados: as duas telas de Comissões e a aba Afiliado do cadastro do cliente) dizem "pago em vale-compra VC-n", com link para o vale. **Cancelar o pagamento em vale** (`cancelarPagamentoEmVale`, só na conta do afiliado; o bloco das ações, igual na lista, encaminha para ela): vale intacto, a confirmação diz "O vale-compra VC-n (R$ X) é cancelado e o valor volta ao saldo de comissão", o vale é cancelado ("pagamento de comissão cancelado") e o valor volta ao saldo; vale usado bloqueia ("O pagamento não se cancela"). Como a baixa do pagamento cobre o valor inteiro, ele **conta como pago** em todo lugar que lê `deskComissoesPagas`: não é vencido, o "cancelar sozinho" não o pega, a tela inicial não o conta como conta a pagar atrasada, a vitrine do afiliado o soma em "Pago".

**Contas a Pagar** (lista e detalhe, bloco `CONTAS DE COMISSAO`, igual nas duas). O título 9000+n de pagamento com `p.vale` nasce **pago**, forma Vale-compra, histórico "Comissão de <mês> — <nome> · Pago com vale-compra VC-n", marcado com `vale: n`. A baixa dele **não entra no Caixa, no extrato nem no saldo de conta financeira**: o título já nasce pago a partir do pagamento, sem passar pela baixa que escreve em `deskCaixaExtras`. Continua contando como pago nos totais e na aba Pagas. O detalhe é **só leitura**: sem dar baixa, editar nem o menu de cancelar, excluir e clonar, sem estornar a baixa (a coluna diz "—" e a conta, "Vale-compra"), nem pelo endereço `?baixar=1`; a faixa do topo diz "Pago com vale-compra VC-n: ... O valor muda em Comissões Afiliados ou no vale." com o link do vale. Na lista, o painel lateral mostra a linha do vale e a baixa em "Vale-compra", e a seleção em massa **não cancela nem exclui** o título (o mesmo padrão de Contas a Receber na entrega 2).

**Conserto na revisão: finalizar com alteração não salva.** Finalizar usa o que está gravado, e antes ignorava o rascunho em silêncio: quem escolhia Vale-compra e finalizava sem salvar finalizava com a forma antiga, sem vale. Agora, com qualquer alteração pendente (quantidade, estado, motivo, forma ou descrição), finalizar avisa "Há alterações não salvas nesta devolução. Salve antes de finalizar" e não faz nada. A seção 2 de `teste_vale_origem.py` ganhou a asserção.

**O exemplo que mudou.** Os clientes das vendas de exemplo da Devolução não estavam no cadastro. A venda **PV-4903** (loja 1, Desk Shope; devolução **DV-0009**, extravio, sem mercadoria a lançar no estoque, total R$ 414,80) passou de Pedro Antunes para **Bruno Carvalho** (cliente 12, 890.123.456-77, contato (99) 98234-5512), na tela de detalhe e na lista. As outras quatro vendas ficam com clientes de fora do cadastro, e a opção Vale-compra mostra o motivo nelas.

**Decisões que couberam a quem construiu, para o usuário confirmar:** (1) **cancelar o pagamento de comissão em vale** é permitido enquanto o vale está intacto (o vale é cancelado junto e o valor volta ao saldo) e bloqueado com o vale usado, por simetria com a regra da Devolução; antes, pagamento com baixa não se cancelava. (2) **Vale cancelado à mão no Vale-compra não cancela a devolução nem o pagamento**: a devolução segue finalizada (a linha do vale passa a dizer "cancelado") e, depois, ela ainda pode ser cancelada, sem mexer no vale que já estava cancelado; o pagamento de comissão idem, só devolve o valor ao saldo. (3) **A devolução de exemplo não é gravada, o vale é**, e a tela sabe que a devolução foi finalizada pelo vale que tem o `id` dela. Limite do protótipo: a devolução nova, aberta a partir de uma venda, recebe o `id` máximo mais 1 e também não é gravada, então um `id` reaproveitado em outra sessão herdaria o vale da devolução anterior; some com o banco (está comentado no código). (4) A **senha de finalizar a devolução** continua a de antes (`devolucaoFinaliza`, com senha por padrão) e a de pagar comissão, a de `comissaoPaga`; nenhuma ação nova entrou no catálogo. (5) A **forma da devolução só vale como "anotada" até finalizar**: quem escolhe Vale-compra e finaliza sem salvar a escolha finaliza com a forma que estava salva (comportamento de antes para todas as formas). (6) A seleção em massa de Contas a Pagar já deixava de fora o título com pagamento; o `!t.vale` foi posto assim mesmo, para não depender disso (um defeito só nesse ponto é equivalente ao certo).

**Provado nos dois sentidos, numa cópia.** `teste_vale_origem.py` (entra no selo, 173 asserções) tem cinco seções: o bloco (`emitirVale`, `valeDaOrigem`, `cancelarValeDaOrigem`, a validade de Configurações, o armazenamento que falha); a Devolução (a opção pelos quatro motivos, finalizar, os links nos dois sentidos, recarregar, o vale que falha, cancelar com o vale intacto, usado em parte e cancelado à mão); Comissões (o vendedor sem a opção, o afiliado com ela, o pagamento que nasce pago, a ordem atômica, cancelar); Contas a Pagar (o título pago, só leitura, fora do Caixa, a seleção em massa e a baixa normal como controle); e as outras telas (cancelar sozinho, vencidos, tela inicial, o cadastro do cliente, a barra de rolagem a 1280 e 1440, o bloco idêntico). Numa cópia das telas fora do projeto, **10 defeitos injetados, um por vez, e os 10 pegos** (a cópia sem defeito passa nas cinco seções): emitirVale sem a trava de duplicidade (nas 10 cópias), o vale da devolução na loja errada, finalizar mesmo com o emitirVale falhando, o vendedor com a opção Vale-compra, a baixa do vale entrando no Caixa (nas duas Contas a Pagar), cancelar a devolução com o vale usado permitido (a guarda da tela e a do bloco), cancelar o pagamento sem cancelar o vale, a validade fixa em 180 ignorando Configurações (nas 10 cópias), o título do vale editável em Contas a Pagar e a comissão em vale com bônus.. Nenhum escapou, e nenhuma asserção precisou ser acrescentada depois. Um defeito só na seleção em massa de Contas a Pagar (tirar o `!t.vale`) seria equivalente ao certo, porque o título com pagamento já fica de fora da conta, e por isso não foi injetado. `teste_vale_compra.py` (317), `teste_vale_uso.py` (146) e `teste_devolucao.py` (a seção 11, de "reservado", virou "Vale-compra é forma como as outras") foram atualizadas para as dez cópias. Selo: 57 suítes, 6.284 asserções, nenhuma falha (a auditoria estrita e a oficial limpas).

**Conserto do teste do usuário (20/out): a devolução passa a ser gravada.** Na DV-0009 o usuário escolheu Vale-compra e clicou em "Salvar alterações": a tela mostrou como salvo, mas a lista do Vale-compra não tinha vale (o vale só nasce ao finalizar, e Finalizar fica em "Mais ações") e, ao voltar, a devolução estava como antes, porque ela vivia só na memória (`DEVOLUCOES`, sem `localStorage`). A regra não mudou: o vale continua nascendo ao finalizar. Mudou o resto. **(1) Gravação:** a chave `deskDevolucoes` guarda `{ devolucoes: { <id>: <devolução inteira> } }`. O detalhe chama `gravarDevolucao()` no fim de cada ação que muda a devolução e foi confirmada (salvar, abrir a nova, confirmar a chegada, pedir a reversa, informar ou corrigir o código, registrar o frete real, finalizar com ou sem vale, cancelar); o rascunho não entra, e abrir a tela não grava. Se o navegador não grava, o aviso diz "Ela vale só até recarregar a tela" e a tela segue na memória (try/catch, como os outros blocos). **(2) Leitura:** um bloco `DEVOLUCOES GRAVADAS NO NAVEGADOR`, igual no detalhe e na lista, logo depois do array de exemplo: a gravada **substitui** a de exemplo de mesmo id e a que não existe no exemplo (devolução nova) **entra**; gravação estragada (sem `id` inteiro, `itens` ou `eventos`) é ignorada só ela, e JSON quebrado volta o exemplo. O id da nova é o maior entre exemplo e gravadas mais 1 (e o número `DV-` acompanha), o que **resolve o limite do id reaproveitado herdando o vale** descrito acima: o comentário `shortcut` saiu do código. Resta só o caso de quem limpa `deskDevolucoes` e mantém os vales (o id volta a ser reaproveitado). Não há botão de limpar: limpar os dados do navegador traz o exemplo de fábrica de volta (comentado no código). **(3) Restaurar pelo vale** segue valendo (`valeDaOrigem('devolucao', id)` finaliza ou cancela a devolução ao abrir), mas agora **não duplica** o histórico (a gravada já traz o evento de finalizar e o de cancelar) e respeita a gravada cancelada: vale cancelado à mão e devolução cancelada depois continua cancelada ao recarregar, em vez de voltar a finalizada. **(4) A lista** lê o mesmo gravado, então situação, forma e valores não divergem do detalhe. **(5) O próximo passo visível:** com a forma Vale-compra salva e a devolução ainda não finalizada, o hint da forma acrescenta "O vale-compra de R$ X nasce quando a devolução for finalizada (Mais ações → Finalizar)." (`fraseValeNasce`; some ao finalizar, ao cancelar, com o vale já emitido ou com a opção indisponível), e o aviso de salvo, que só aparece nesse caso, traz a mesma frase depois de "Alterações salvas na devolução DV-0009." Nas outras formas o salvar segue sem aviso, como antes.

**Provas do conserto.** `teste_devolucao.py` ganhou a seção 23 (172 asserções no total): salvar a forma e recarregar; rascunho que não grava; confirmar a chegada, finalizar e cancelar gravados e a lista mostrando o mesmo; duas devoluções novas, com ids 7 e 8 e números DV-0019 e DV-0020 sem colidir, abertas pelo id e na lista; gravação estragada e JSON quebrado; dados do navegador limpos (volta o exemplo); e o `setItem` falhando (o aviso aparece e a tela segue sem erro de JS). As demais seções dela abrem as telas com `deskDevolucoes` limpo (script de inicialização da página), porque assumem o exemplo de fábrica. A seção 2 de `teste_vale_origem.py` ganhou a 2k (190 asserções no total, 17 a mais): Vale-compra salvo, hint e aviso do próximo passo, recarregar, a lista igual, finalizar, o hint some, recarregar sem duplicar o histórico, e o vale cancelado à mão com a devolução cancelada depois; `deskDevolucoes` entrou no `limpar()`. `auditoria.py` ganhou `deskDevolucoes` na lista de chaves conhecidas do `localStorage`. As outras suítes que abrem as telas de devolução (`teste_pedidos`, `teste_rastreamento`, `teste_trilha`, `teste_vale_compra`, `teste_vale_uso` e as demais) passaram sem mudar. **Numa cópia das telas fora do projeto, 8 defeitos injetados, um por vez, e os 8 pegos** (a cópia sem defeito passa nas duas suítes): salvar sem gravar; a lista sem ler o gravado; o id da nova ignorando as gravadas (colide); o exemplo vencendo o gravado no detalhe; o hint do próximo passo ausente; finalizar em vale sem gravar; restaurar pelo vale duplicando o evento; e a tela gravando o rascunho ao abrir. Selo: 57 suítes, 6.327 asserções, nenhuma falha (a auditoria estrita e a oficial limpas).

## 14.92 Gateways de Pagamento, entrega 1: a lista, a página, o menu e a conta financeira (20/out/2026)

*Nome corrigido em 21/out/2026: o gateway se chama **InfinitePay** (a primeira versão escrevia "InfinityPay"). O texto abaixo já usa o nome certo; o tipo interno passou de `infinitypay` para `infinitepay` (o gravado antigo é convertido na leitura). Ver §14.94.*

Barganha aprovada pelo usuário em 20/out, com as quatro recomendações dele (não se reabrem), a partir dos prints do Olist (lista, página com Pagar.me, Pagar.me 2.0, Outro, os menus). Ele decidiu fazer este item antes da F0, o único item do menu no caminho do MVP. **Duas entregas:** esta é a primeira (a lista e a página do gateway, o menu ligado nas telas e a conta em Contas financeiras); a segunda liga Formas de Recebimento e o PDV às condições do gateway.

**Decisões dele (não se reabrem):**

- **O gateway é dono das taxas e dos prazos dos cartões.** A tabela "Condições comerciais" (forma, bandeira, parcelas, prazo, taxa, tarifa) mora no gateway. Em Formas de Recebimento o cartão passará a escolher o gateway e mostrar as condições só para leitura: isso é a entrega 2, e **nada em Formas de Recebimento nem no PDV mudou agora**.
- **Dois gateways: InfinitePay e Outro** (maquininha ou banco sem integração, condições à mão). Sem Pagar.me.
- **Cada gateway diz as lojas em que vale** ("Vale para", ao menos uma).
- **A conta financeira do gateway nasce sozinha ao salvar**, com a descrição dele, e aparece em Configurações → Contas financeiras. Fica de fora do Olist a faixa "Etapa atual · 1 de 4" (tutorial) e o caminho "finanças › configurações": aqui o item é de Integrações.

**As telas** (`telas/integracoes/`, a primeira tela da pasta). **`pagina-integracoes-gateways.html`**, a lista: colunas Descrição, Gateway, Vale para, Conta financeira e Situação; busca por descrição ou tipo; o filtro de situação abre em **Habilitados** (como o pill do Olist), com Desabilitados e Todos; "limpar filtros" na barra e no estado vazio, que devolve a lista como ela abre (só os habilitados, sem busca); ordenar por descrição, gateway ou situação; paginação; "Baixar planilha" e "Imprimir" pelo bloco comum (a folha sai como relatório); clicar na linha abre a página; "Incluir gateway" abre a página em branco (`?novo=1`). O estado vazio diz se não há gateway nenhum ou se é o filtro. **`pagina-integracoes-gateways-detalhe.html`**, a página (`?id=`): o botão "Voltar para Gateways" à direita do título (padrão do Vale-compra) e "Mais ações → Excluir o gateway" só no gateway que já existe; o rodapé sticky com Salvar, Cancelar e a nota "Nenhuma alteração pendente" / "Há alterações ainda não salvas". Sair com alteração pendente pergunta nos dois caminhos (o botão do topo e o Cancelar do rodapé). Endereço sem gateway que exista diz isso e não mostra nada.

**A página, por tipo.** O topo é de todos: Gateway (InfinitePay ou Outro), Descrição (nasce com o nome do tipo, editável, obrigatória e única), Situação, **Vale para** (multiseleção das três lojas, com o menu aberto enquanto se marca) e a **Conta financeira para lançamentos**, só leitura, igual à descrição ("Conta de extrato do saldo disponível no gateway"). Sem escolher o gateway só o topo aparece; escolher refaz os blocos. **InfinitePay** (molde: o Pagar.me 2.0): *Recebimento* (categoria padrão das contas a receber, conta financeira para crédito, data da baixa), *Dados adicionais* (taxa mensal de juros, multa, dias para multa, interruptor "Calcular juros e multas após o vencimento"), *Sped* (CNPJ com máscara, endereço, município), *Configurações do Gateway* com a **Chave da API**, o link de conciliação e o "testar conexão"; sem "Versão da API", que é do Pagar.me. **Outro** (molde: os prints de Outro): *Configurações das tarifas* (Tarifação em quatro opções; **Dia para débito** só com "Em dia específico", de 1 a 31; categoria das tarifas, de despesa), o Sped e as *Configurações do Gateway* sem chave. **Dos dois:** *Bandeiras atendidas* (multiseleção com "Selecionar todas"), *Bandeira padrão* (entre as escolhidas), *Antecipação dos recebíveis* (com o ícone de ajuda que explica), o interruptor do próximo dia útil e **Condições comerciais das formas selecionadas**: *Repassar taxas para o cliente* (Não, Sim, Opcional, Opcional com liberação do gerente), *Repassar taxas a partir da* (1ª a 12ª parcela, **desabilitado com "Não"**) e a dica "Neste momento, o repasse de taxas é exclusivo para PDV."

**A tabela de condições.** Linhas fixas de débito (prazo 2, tarifa R$ 2,00), boleto (2, R$ 2,00) e Pix (0, R$ 0,00), taxa zero; e, para cada bandeira escolhida, o crédito de 1x a 12x com prazo 31 (30 na 12x), tarifa zero e as taxas de fábrica 3 · 3,6 · 4,25 · 4,9 · 5,5 · 6,15 · 6,8 · 7,45 · 8 · 8,7 · 9,35 · 10 (do print). São até 99 linhas (3 + 8 × 12), então a tabela vem **agrupada**: uma faixa "Débito, boleto e Pix" e uma por bandeira, cada uma com o resumo (quantas condições, de que taxa a que taxa, quantas editadas), que **recolhe e abre** as linhas dela; com mais de duas bandeiras as faixas de crédito abrem recolhidas, e "Recolher todas / Expandir todas" mexe em todas. Nenhum campo do print se perdeu: forma, bandeira, parcelado até, prazo (com "dias"), taxa (com "%"), tarifa (com "R$") e a lixeira de cada linha. **Tirar uma bandeira tira as linhas dela**: sem edição, na hora; com linha editada (prazo, taxa ou tarifa diferentes da fábrica) o painel diz quantas e avisa que o editado se perde, e cancelar mantém tudo. **Adicionar condição comercial** abre uma linha de escolha (forma; bandeira e parcela só no crédito, entre as bandeiras escolhidas) e **recusa a repetida** dizendo qual é. Validação: prazo inteiro de 0 a 9999, taxa de 0 a 100 com até duas casas, tarifa de 0 em diante com até duas casas; o erro aparece na célula, com a mensagem, e a faixa recolhida onde ele está se abre.

**A chave da API.** Gravada, **nunca volta inteira**: a tela mostra só `••••` e os quatro últimos caracteres, com "Trocar chave"; a caixa de senha só existe quando a pessoa vai digitar uma chave nova (no gateway novo ela já abre). Nem a tela, nem o código da página, nem a impressão, nem a planilha, nem o painel de confirmação, nem o Registro de atividades a trazem inteira. Formato: letras, números, `_` e `-`, de 16 caracteres em diante. **testar conexão** (simulado): chave vazia, curta ou com caracteres que não servem dão erro dizendo o quê; chave com formato válido diz "Conexão ok (simulada no protótipo)". O **link de conciliação** gera um endereço fictício (`https://erp.deskcompany.example/conciliacao/<id>`) com "copiar" e o aviso de que a InfinitePay o chama para avisar os pagamentos; gerar outro invalida o anterior. `shortcut:` no código (bloco comum): no protótipo a chave fica inteira no `localStorage`; na produção ela vai para o servidor como segredo e a tela só recebe a máscara.

**A gravação.** Chave `deskGateways` (`{ gateways: [...] }`), um bloco de dados e regras **idêntico nas duas telas** (`GATEWAYS: DADOS E REGRAS`). Cada gateway: `id`, `tipo`, `descricao`, `situacao`, `lojas`, os campos do tipo (InfinitePay: `categoriaId`, `contaCreditoId`, `baixa`, `juros`, `multa`, `diasMulta`, `calculaAtraso`, `chave`, `conciliacao`; Outro: `tarifacao`, `diaDebito`, `categoriaTarifaId`), os comuns (`cnpj`, `endereco`, `municipio`, `bandeiras`, `bandeiraPadrao`, `antecipacao`, `proximoDiaUtil`, `repassar`, `repassarAPartir`) e `condicoes: [{ forma, bandeira, parcelas, prazo, taxa, tarifa }]`, com números de verdade. **A condição** é identificada por forma, bandeira e parcelas, e a repetida é a que repete as três. **O exemplo de fábrica** nasce uma vez por navegador (marca `deskGatewaysExemplo`): **InfinitePay — loja virtual** (Desk Shope e Desk Brands, habilitado, Visa, Mastercard e Elo, com a chave já guardada e mascarada), **Stone — maquininha da loja** (Outro, Desk Shope, todas as oito bandeiras: 99 linhas) e **Cielo (antiga)** (Outro, desabilitado). Ele acrescenta sem apagar, e o que está gravado vence: excluído não volta, renomeado continua renomeado.

**A conta financeira.** Ela **é o gateway gravado**: nasce com ele, leva o nome (a descrição) e a situação dele, muda de nome quando a descrição muda e some quando ele é excluído; não há segunda cópia para ficar velha. **Configurações → Contas financeiras** passa a mostrar, depois das seis de sempre, uma conta por gateway, com o selo "gateway", "criada pelo gateway <descrição>" e o link para a página dele, só leitura (a linha não abre o painel). Ela não entra no saldo: `shortcut:` no código, porque no protótipo não há lançamento numa conta de gateway; na produção, excluir um gateway com lançamento na conta passa a ser bloqueado (inativar é a saída). **As outras telas que têm espelho de Contas financeiras não mudam**, e as suítes que comparam os espelhos seguem sobre a lista fixa: ligar o gateway a elas é a entrega 2. A descrição também não repete o nome de nenhuma conta que já existe.

**As confirmações de senha.** Quatro ações novas no catálogo, grupo **Integrações**, nas 17 telas que carregam as ações de Vale-compra e nas duas telas novas: `gatewayIncluir` e `gatewayEditar` (sem senha de fábrica, entram no Registro de atividades), `gatewayChave` (guardar, trocar ou apagar a chave: **pede senha**, inclusive ao criar um InfinitePay, e ao mudar um gateway de InfinitePay para Outro, que apaga a chave) e `gatewayExcluir` (**pede senha**, e o painel diz que a conta financeira sai junto). Sem senha ligada, salvar grava direto, sem painel; o texto da ação, sem a chave, vai para o registro.

**O menu.** O item "Gateways de Pagamento" (Integrações) existia sem destino em todas as telas; ganhou `data-href` para a lista nas **86 telas** que já existiam (uma delas, o molde, guarda uma segunda cópia do menu dentro do comentário) e nas duas novas: **88 telas**, **44 de 55 itens de menu com tela**, faltam 11. A seção 10 de `teste_menu.py` lê esses números do `PROGRESSO.md`, então não tinha número a trocar no arquivo.

**Decisões que couberam a quem construiu, para o usuário confirmar:** (1) o plano mandava copiar "o componente e o espelho de lojas" de Formas de Recebimento, mas **ali "Vale para" é receber ou pagar e não há lojas**; o componente de várias lojas é o de Marcas (caixas de marcar dentro do dropdown) e o espelho de lojas é o de Lojas Desk e do Vale-compra (Desk Shope, Desk Brands, Desk Tech; a Desk Flash não é loja que emita). (2) **"Dinners Club" do print está escrito "Diners Club"**, que é o nome da bandeira. (3) **CNPJ:** o projeto não tem validação de CNPJ, então há máscara e a exigência de 14 números; sem conferir os dígitos verificadores. (4) **Obrigatórios:** no InfinitePay, a categoria, a conta para crédito e a chave (sem eles a integração não funciona); no Outro, a categoria das tarifas; em ambos, o Dia para débito só quando a tarifação é "Em dia específico". As bandeiras podem ficar vazias (o gateway fica só com débito, boleto e Pix). (5) **A página abre sempre editável**, sem o modo leitura dos cadastros: é configuração. (6) **Salvar não abre painel** quando a ação não pede senha (padrão do catálogo); a conta nascer fica dito no Registro e na dica do campo ("nasce ao salvar"). (7) Contas para crédito: as contas bancárias ativas de Contas financeiras (Banco Inter e Mercado Pago). Categorias: as cinco de receita e as de despesa listadas no bloco, com suíte comparando com Categorias financeiras. (8) A lista usa o bloco comum de planilha e impressão e a página do gateway não (é formulário): `teste_impressao.py` passou de 23 para 24 telas com o bloco, e de 17 para 18 listas. (9) O exemplo de Contas financeiras só mostra a conta dos gateways depois que a lista ou a página de Gateways foi aberta uma vez no navegador (é quando o exemplo nasce).

**Provado nos dois sentidos, numa cópia.** `teste_gateways.py` (entra no selo, 311 asserções) tem sete seções: a lista (colunas, filtro, busca, vazio, limpar, abrir, ordem, incluir); a página por tipo (o que aparece e some, a descrição que acompanha o tipo, o Dia para débito, os campos de cada bloco, as validações do topo); a tabela (geração por bandeira, 99 linhas, faixas, tirar com e sem edição, padrão que acompanha, adicionar, repetida, validações por célula, "a partir da"); a chave (máscara, nunca inteira em tela, código, impressão, planilha, painel e registro; trocar; testar conexão; link; copiar); gravar e recarregar, sair com pendência, excluir, senhas e registro; a conta financeira (nasce, renomeia, acompanha a situação, some, nome com marca de página, lista fixa); e o menu, o bloco comum, o catálogo, os espelhos (lojas, categorias, contas), o exemplo que o gravado vence, o armazenamento que falha, a barra de rolagem a 1280 e 1440 e os dois temas. Onze defeitos foram injetados na lógica nova, numa cópia das telas fora do projeto (cada um desfeito antes do seguinte), e **os onze foram pegos**: a chave inteira na tela depois de salva (6 asserções reprovam); a bandeira tirada deixando as linhas dela (7); a condição repetida aceita (6); o "a partir da" habilitado com "Não" (3); a conta financeira que não renomeia (3); a conta financeira que não nasce (3); o Dia para débito aparecendo fora de "Em dia específico" (4); o exemplo que vence o gravado, voltando a cada abertura (14); a chave indo parar no Registro de atividades (3); sair com alteração pendente sem avisar (3); e o prazo negativo aceito na tabela (5). Em três deles (a conta que não nasce, o aviso de saída e o prazo negativo) a suíte caía com um erro de navegador antes de contar: cada seção agora é protegida, o erro vira uma falha com o número da seção, e a espera por um elemento caiu para 8 segundos. Fora da suíte nova: `teste_comissoes.py` e `teste_vale_compra.py` contavam o catálogo em 17 telas e passaram a contar 19 (as duas de Gateways entram); `teste_impressao.py` foi de 23 para 24 telas com o bloco de planilha e impressão (de 17 para 18 listas); e a auditoria do projeto ganhou `deskGateways` e `deskGatewaysExemplo` entre as chaves de estado compartilhado. **O selo fecha em 58 suítes seladas e nenhuma falha** (a auditoria estrita e a oficial, com contraste nos dois temas, limpas nas 88 telas). Uma lição que custou uma volta: as peças das telas novas nasceram com fim de linha CRLF (o `Write` desta máquina) e o projeto é LF; a prova só achou o trecho a trocar quando isso foi normalizado, e as duas telas estão em LF.


## 14.93 Gateways de Pagamento, entrega 2: Formas de Recebimento e o PDV leem as condições do gateway (21/out/2026)

*Nome corrigido em 21/out/2026: **InfinitePay**, não "InfinityPay"; tipo interno `infinitepay`. Depois do teste do usuário, também mudaram o prazo (agora em **dias úteis**, não corridos: a decisão (3) de quem construiu, abaixo, ficou superada), o exemplo de fábrica (a Stone e a Cielo saíram; entrou a InfinitePay real em quatro níveis) e o PDV ganhou o desconto Pix/dinheiro. Tudo em §14.94.*

Barganha aprovada pelo usuário em 20/out, com as três recomendações dele (não se reabrem), depois de aprovar a entrega 1 (§14.92). **Decisões dele:** **(1) Só os cartões** (as chaves `debito` e `credito`) passam a ler o gateway; Pix e boleto seguem como eram, e as linhas deles na tabela do gateway ficam para a vitrine. **(2) No PDV o caixa escolhe a maquininha** entre os gateways habilitados da loja do PDV, só os do tipo Outro (a InfinitePay é da loja virtual), com o gateway padrão da forma já marcado; com uma só, o campo não aparece. **(3) O caixa marca a bandeira**, com a bandeira padrão do gateway já marcada; trocar recalcula a taxa e o repasse.

**O bloco comum** (`GATEWAYS: LEITURA`, em `// ===== GATEWAYS: LEITURA` até `// ===== FIM DO BLOCO GATEWAYS: LEITURA =====`), **idêntico em duas cópias**: o PDV e Formas de Recebimento. Só lê `deskGateways` (o dono continua sendo Integrações → Gateways de Pagamento) e **só escreve a semente do exemplo**, com a mesma marca (`deskGatewaysExemplo`) e os mesmos três gateways da entrega 1: sem ela, um navegador que nunca abriu Gateways deixaria o PDV sem maquininha. A suíte confere que os dados semeados pelo PDV e por Formas são, campo a campo, os que a página do gateway semeia. Funções: `gwlHabilitados(loja, tipo)`, `gwlCondicao(gateway, forma, bandeira, vezes)` → `{ prazo, taxa, tarifa }` ou nulo, `gwlVezes(gateway, bandeira)`, `gwlRepasse(gateway)` → `{ modo, aPartirDa }`, `gwlConta(gateway)` (`gw<n>`) e `gwlPadraoDaForma(chave)`. **O gateway padrão de cada cartão** mora em `deskParametros.formaGatewayPadrao` (`{ debito: id, credito: id }`), gravado em Formas de Recebimento; sem escolha gravada, ou com o escolhido desabilitado ou excluído, vale o de fábrica: o primeiro habilitado do tipo Outro (a Stone do exemplo).

**Formas de Recebimento.** O débito e o crédito ganham o campo **Gateway padrão** (os gateways habilitados, cada um com o tipo e as lojas), com o aviso e o link para incluir um quando não há nenhum. Os campos que guardavam prazo, parcelas, taxa de cada parcela, tarifação, repasse, antecipação e conta **deixam de ser editáveis** nos cartões e viram um **resumo só de leitura** das condições do gateway padrão (prazo, parcela em até, taxa em 1x e nas demais, tarifa, quando a tarifa é debitada, repasse e "a partir da", antecipação e a conta do gateway), com o link **"editar no gateway"** para a página dele; o resumo muda na hora quando se escolhe outro gateway. A lista mostra, nos cartões, a conta do gateway no lugar da conta preferencial e as condições dele no lugar da taxa ("3,00% a 10,00% · pelo gateway"); a busca por conta acha o cartão pelo nome da conta do gateway. As linhas dos dois cartões ficaram sem nada de fábrica (`viaGateway: true`, taxa, prazo e conta zerados): **a taxa do exemplo mudou**: os 3,49% do crédito (e os 1,39% do débito) saíram, e o PDV passa a mostrar a Stone, que tem 3,00% em 1x e de 3,60% a 10,00% nas demais parcelas, prazo de 31 dias corridos (30 na 12x), e débito de 0,00% com tarifa de R$ 2,00 em 2 dias. Trocar o gateway padrão é mexer em regra de dinheiro: o painel diz e pede senha (`formasRecebimentoRegra`). Pix, boleto e a forma criada pelo usuário seguem com o painel de sempre.

**PDV.** No recebimento em débito ou crédito: a **Maquininha** (gateways habilitados do tipo Outro na loja do turno; o padrão é o gateway padrão da forma se for dessa loja e tipo, senão o primeiro; com uma só, sem campo, e o nome dela vem no resumo) e a **Bandeira** (as bandeiras atendidas pela maquininha; a padrão do gateway já vem marcada). **A taxa, a tarifa e o prazo vêm da condição** (forma, bandeira, vezes): o crédito é por bandeira e por número de vezes, e o menu de parcelas oferece só as vezes que o gateway tem para a bandeira (a venda que estava em 7x, quando a linha some, passa para a mais próxima que existe); o débito usa a linha "Cartão de débito", sem bandeira na tabela, e a tela diz que **a bandeira não muda a taxa do débito**. Crédito numa bandeira ou parcela sem linha no gateway **não fecha a venda** (o motivo aparece na venda e na pendência). **O repasse segue as regras do gateway:** *Não* (sem repasse, o switch some); *Sim* (repassa sempre, o switch aparece ligado e travado); *Opcional* (switch livre, desligado de fábrica); *Opcional com liberação do gerente* (ligar pede senha, desligar não); e **abaixo da parcela "a partir da" não há repasse** (a tela avisa), inclusive no débito (1x). **O título** nasce com o vencimento pelo prazo do gateway, em dias corridos (com "considerar próximo dia útil" ligado no gateway, o dia sem expediente passa para o dia útil seguinte, pelo helper de dias úteis do PDV, que pula sábado, domingo e feriado nacional de data fixa), a taxa e a tarifa da condição, a **conta do gateway** e, no registro da venda, `gatewayId`, `gatewayNome`, `bandeira`, `bandeiraNome`, `vencimento` e o `historico` ("Cartão de crédito · American Express · 3x · Stone — maquininha da loja"). A tela da venda concluída diz o título, a conta do gateway, a maquininha, a bandeira e o vencimento. Trocar a maquininha ou a bandeira depois de calcular recalcula tudo (taxa, tarifa, prazo, repasse e título), como mudar as parcelas já fazia. **Loja sem maquininha:** o cartão sai do menu de recebimentos, um aviso fica à vista com o motivo e o link para Gateways, e recebimento de cartão que ficou sem maquininha (o gateway foi desabilitado) trava a venda. Venda em andamento gravada antes desta entrega, com o cartão sem maquininha nem bandeira, abre em ordem (a maquininha e a bandeira padrão) e ignora o repasse antigo. O caixa continua certo: o cartão não entra na gaveta e aparece por forma, pelo valor que passou na maquininha. **Uma ação nova no catálogo**, `pdvRepasseTaxa` ("Liberar o repasse da taxa do cartão ao cliente no PDV", grupo Vendas, com senha por padrão), nas quatro telas que carregam as ações do PDV (o PDV, Confirmações de senha, Registro de atividades e o detalhe de Vendedores).

**O que não mudou, e por quê.** O **Pedido de Venda** só lê o total da venda do PDV (o `deskPdv`, `total`); nenhuma tela além do PDV e de Formas lê `prazoUteis`, `parcelasMax` ou `taxasParcela` dos cartões (a suíte confere), então ele não precisou de ajuste, e a venda com repasse entra nele pelo total que o cliente pagou. **A vitrine** (InfinitePay) e as linhas de Pix e boleto do gateway ficam para depois. O PDV ainda não grava título em Contas a Receber de verdade (a tela de Contas a Receber não lê as vendas do balcão): o "título" é o recebimento gravado na venda, com as parcelas, o vencimento, a conta e o histórico, como já era.

**Decisões que couberam a quem construiu, para o usuário confirmar:** (1) **Onde mora o gateway padrão da forma:** em `deskParametros.formaGatewayPadrao`, porque Formas de Recebimento não grava nada de si (a lista de formas vive na memória da tela); só essa escolha persiste. (2) **O padrão de fábrica** é o primeiro habilitado do tipo Outro, e a lista de escolha em Formas traz **todos** os habilitados (a InfinitePay também, com o tipo à vista, como o pedido dizia), enquanto o PDV só usa os do tipo Outro: se o padrão for a InfinitePay, o PDV usa a primeira maquininha da loja. (3) **Prazo em dias corridos** (o do gateway), e não mais em dias úteis como o cadastro antigo; o "próximo dia útil" é o botão do gateway. (4) **Gateway sem a linha** de débito, ou de crédito para a bandeira e as vezes: a venda não fecha (em vez de usar taxa zero calada). (5) A **bandeira do débito é marcada e gravada**, mas não muda a taxa. (6) **O repasse "opcional" nasce desligado** e a escolha do caixa fica na venda; o antigo "repassa por padrão" da forma deixou de existir nos cartões. (7) O **resumo do turno continua por forma**, e não por maquininha. (8) Gateway padrão **desabilitado ou excluído cai no de fábrica**, sem aviso. (9) Saíram do PDV `maisDiasUteis` e `prazoTexto` (sem uso). (10) A senha do gerente é a ação `pdvRepasseTaxa`, no grupo Vendas, pedida também quando a pessoa do caixa é a própria gerente: a senha é um cadeado mocado, como as outras.

**Provado nos dois sentidos, numa cópia.** `teste_gateway_uso.py` (entra no selo; eram 130 asserções, hoje 209, §14.94) tem seis seções: o bloco (cópias idênticas, a semente igual à da página do gateway, as funções, o padrão da forma e o dado estragado); Formas (o campo e o resumo só de leitura, o que sumiu, o link, trocar e salvar com senha, Pix e boleto como eram, sem gateway); o PDV, a maquininha e a bandeira (quais aparecem, a de outra loja não, o padrão, trocar recalcula o crédito e não o débito, parcelas só com condição, loja sem maquininha, venda guardada antes); o repasse (as quatro regras, o "a partir da" e a senha do gerente, no registro de atividades); o título (vencimento, o dia útil, a conta, a maquininha e a bandeira gravadas, o caixa); e o catálogo, o Pedido de Venda e a conferência de quem lê os campos. Doze defeitos foram injetados na lógica nova, numa cópia das telas fora do projeto (cada um desfeito antes do seguinte), e **os doze foram pegos** (as falhas de cada um entre parênteses): a taxa da bandeira padrão no lugar da escolhida (8); a InfinitePay oferecida como maquininha no PDV (10); o repasse abaixo do "a partir da" (4); o Opcional com gerente ligando sem senha (3); o vencimento ignorando o prazo do gateway (11); a parcela sem condição aceita (3); Formas deixando editar a taxa do cartão (1); a maquininha de outra loja aparecendo (8); o próximo dia útil ignorado (2); a conta do título que não é a do gateway (2); a troca de maquininha que não refaz a bandeira (2); e o gateway padrão da forma ignorado (3).  Os ajustes em suítes que já existiam: `teste_pdv.py` (201 asserções) passou a esperar os números da Stone no lugar dos 3,49%, ganhou o auxiliar que põe a Stone em "opcional" para exercer o switch e a ação nova no catálogo; `teste_formas_recebimento.py` passou a vitrine do prazo fixo, das parcelas e do repasse do Crédito para o Cheque (a mecânica segue valendo para as outras formas), e o crédito e o débito passaram a ser lidos pelo que mostram do gateway. **O selo fecha em 59 suítes seladas e nenhuma falha** (a auditoria estrita e a oficial, com contraste nos dois temas, limpas).

## 14.94 Gateways, ajustes do teste: dias úteis, a InfinitePay real e o desconto Pix/dinheiro (21/out/2026)

Depois de aprovar a entrega 2 (§14.93) e testá-la, o usuário decidiu quatro mudanças (não se reabrem). Esta seção diz o que ficou, de onde vêm os números e o que ele precisa conferir na conta da InfinitePay.

**Decisões dele.**

1. **O prazo é em dias úteis.** A coluna da tabela do gateway chama-se **"Prazo (dias úteis)"**, todo vencimento (PDV, resumo em Formas de Recebimento) usa o ajudante `diaUtil` do projeto (sábado, domingo e feriado nacional de data fixa não contam; venda numa sexta com prazo de 1 dia útil vence na segunda; prazo zero é o mesmo dia) e o interruptor "Considerar próximo dia útil para parcelas e tarifas" **saiu** da página do gateway. O campo `proximoDiaUtil` que estiver gravado é ignorado (apagado na leitura). Formas mostra "N dias úteis". Isto supera a decisão (3) de quem construiu na §14.93 (dias corridos).
2. **O nome é InfinitePay**, e não "InfinityPay". Renomeado nas telas, nas suítes, em §14.92/§14.93 (com a nota "nome corrigido em 21/out"), na arquitetura e no PROGRESSO; o tipo interno passou de `infinitypay` para `infinitepay`, e o gravado antigo é convertido na leitura. O HISTORICO.md não mudou (é o registro do que se escreveu na época). A grafia antiga só sobrou onde a conversão precisa dela: o tipo e a descrição do exemplo antigo.
3. **O exemplo de fábrica é a configuração real da Desk**, não mais o de demonstração (a Stone e a Cielo saíram).
4. **No PDV, Pix e dinheiro descontam a taxa do crédito à vista** (abaixo).

**O exemplo de fábrica (marca `deskGatewaysExemplo` = `'2'`).** Cinco gateways, ids de fábrica 1 a 5:

- **1 · "InfinitePay — loja virtual"** (tipo InfinitePay, com a chave de antes, habilitado, lojas 1 e 2, repasse Opcional): as taxas do **Link de Pagamento** da tabela geral "Em 1 dia útil", crédito de 1x a 12x (**4,20% em 1x, 6,09, 7,01, 7,91, 8,80, 9,67, 12,59, 13,42, 14,25, 15,06, 15,87 e 16,66% em 12x**), Visa, Mastercard, Elo e American Express, Pix grátis, **sem débito**, 1 dia útil.
- **2 a 5 · "InfinitePay Maquininha — Bronze / Prata / Ouro / Infinite"** (tipo Outro; **só a Bronze nasce habilitada**): lojas 1, 2 e 3; bandeiras Visa, Mastercard, Elo, American Express e Hipercard (padrão Visa); Antecipado; tarifação "No dia do pagamento (somada à taxa)"; categoria das tarifas 17; repasse **Opcional a partir da 1ª parcela**; sem tarifa fixa; Pix grátis e no mesmo dia; **débito e crédito de 1x a 12x em 1 dia útil**; 66 condições cada (Pix e 13 por bandeira).

Taxas oficiais da maquininha, em % (a página agrupa a Hipercard com a Elo e a American Express). Bronze é o "Plano Inicial" (até R$ 20 mil por mês); Prata, acima de 20 mil; Ouro, acima de 40 mil; Infinite, acima de 80 mil:

| nível | Visa e Mastercard: débito · 1x · 12x | Elo, American Express e Hipercard: débito · 1x · 12x |
|---|---|---|
| Bronze | 1,37 · 3,15 · 12,40 | 2,58 · 4,91 · 13,41 |
| Prata | 0,85 · 2,89 · 10,12 | 2,08 · 4,65 · 11,88 |
| Ouro | 0,79 · 2,79 · 9,56 | 1,98 · 4,56 · 11,33 |
| Infinite | 0,75 · 2,69 · 8,99 | 1,88 · 4,46 · 10,77 |

As doze parcelas de cada nível estão no código (`GW_TAXAS_INFINITEPAY`, no bloco `GATEWAYS: DADOS E REGRAS`, comentário com a fonte). **Fonte: página de taxas da InfinitePay (infinitepay.io/taxas), consultada em 21/out/2026**, linha "maquininha, em 1 dia útil, parcelas antecipadas".

**Troca do exemplo antigo.** Um navegador que já tem o exemplo antigo (marca `'1'`) é migrado ao abrir qualquer das telas que carregam o bloco (Gateways, a página do gateway, Formas, PDV, Configurações › PDV: o resultado é o mesmo, a suíte confere nas quatro): saem a Stone (id 2) e a Cielo (id 3), achadas pelo id **e** pela descrição de fábrica; a loja virtual (id 1, com a descrição antiga) é atualizada **mantendo a chave e o link de conciliação**; entram os quatro níveis com ids novos, depois do maior que já havia; o gateway que o usuário criou **não é tocado**; o gateway padrão de Formas que apontava para a Stone ou a Cielo é apagado e cai no de fábrica (o primeiro habilitado do tipo Outro: a Bronze). Sem marca nenhuma, o exemplo nasce inteiro, acrescentando sem apagar nem duplicar por descrição.

**O débito é por bandeira.** A InfinitePay cobra débito diferente por bandeira (Visa 1,37% na Bronze, Elo 2,58%). Um gateway novo nasce com as três linhas sem bandeira (débito, boleto e Pix) mais, **por bandeira escolhida, o débito dela e o crédito de 1x a 12x** (13 linhas); a tabela agrupa em "Sem bandeira (débito, boleto e Pix)" e "Cartão · <bandeira>", e a linha única sem bandeira continua valendo como reserva, para o gateway que não separa o débito. `gwlCondicao` usa a linha da bandeira escolhida e, não achando, a linha única. No PDV o débito passa a usar a bandeira marcada (a dica diz "O débito usa a taxa da bandeira escolhida" ou, no gateway de linha única, que a bandeira não muda a taxa); em Formas o resumo do débito mostra a linha da bandeira padrão. Ao adicionar uma condição de débito, escolhe-se a bandeira ou "Sem bandeira (linha única)".

**O desconto Pix/dinheiro no PDV.** O preço já embute a taxa do cartão; quem paga à vista não a usa, e leva o desconto.

- **O percentual não é digitado**: é a taxa do **crédito em 1x da bandeira padrão da maquininha padrão da loja do PDV**, lida do gateway (`gwlDescontoAVista(loja)`, no bloco de leitura). A maquininha padrão é o gateway padrão do crédito em Formas, se for do tipo Outro, habilitado e da loja; senão a primeira maquininha habilitada da loja; **loja sem maquininha não tem desconto**. Hoje: 3,15% (Bronze, Visa). Subir de nível (habilitar a Prata e desabilitar a Bronze) muda o desconto sozinho (2,89%).
- **Só no Pix e no dinheiro**, e sobre o **valor cheio que o recebimento quita**: o recebimento diz "Quita R$ 50,00 · com o desconto à vista de 3,15% o cliente paga R$ 48,43". Pix de R$ 100,00 = R$ 96,85. Venda dividida: desconta só a parte do Pix/dinheiro. Vale-compra, crediário, cheque, boleto, depósito e cartão **não** têm desconto.
- **Centavos**: o cálculo é em centavos inteiros, meio centavo sobe, e o total a pagar é a venda mais o repasse do cartão menos o desconto, sem sobrar centavo. O **troco é sobre o valor descontado** (entrega 100,00 para 48,43: troco 51,57). A **gaveta e a conta do Pix recebem o valor descontado**.
- **O desconto manual da venda vem primeiro**: a base é o total já com ele.
- Na tela de finalizar: a linha **"Desconto Pix/dinheiro (3,15%) − R$ X"**, o aviso com a maquininha e a bandeira de onde vem o percentual e o botão **"Tirar o desconto desta venda"**; o recibo traz a mesma linha.
- **A venda grava** `descontoAVista: { pct, valor, gatewayId }` (nulo quando não houve) e `descontoAVistaTirado`; cada recebimento grava `cobrado` (o que o cliente pagou) e `desconto`. O `total` da venda já é o descontado.
- **Tirar o desconto da venda é ação com senha**: nova ação do catálogo, **`pdvDescontoAVistaTira`** ("Tirar o desconto à vista (Pix e dinheiro) de uma venda no PDV", grupo Vendas, exige senha por padrão), nas quatro telas que carregam as ações do PDV; o Registro de atividades guarda quem tirou.
- **Configurações › PDV** ganhou a seção **"Pagamento à vista"** com o interruptor **"Desconto Pix e dinheiro igual à taxa do crédito à vista"** (parâmetro `pdvDescontoAVista`, ligado de fábrica; agora são dez parâmetros do PDV nas duas telas) e uma prévia do percentual de hoje por loja, lido do gateway.
- **Só o PDV** por enquanto (Pedido de Venda e vitrine não aplicam; o Pedido só lê o total gravado).

**Decisões que couberam a quem construiu, para o usuário confirmar.** (1) **A comissão do vendedor é sobre o valor com desconto**: ela lê o `total` gravado da venda, que já é o descontado (o desconto à vista sai da loja, não do vendedor, só se o usuário disser o contrário). (2) **As taxas da loja virtual** são as da tabela geral "Em 1 dia útil" do Link de Pagamento: a página pública não traz a do Plano Inicial por nível. **Conferir na conta da InfinitePay antes de usar de verdade**, e idem a lista de bandeiras que o link aceita. (3) Os **feriados** são os nacionais de data fixa (1/1, 21/4, 1/5, 7/9, 12/10, 2/11, 15/11, 20/11, 25/12); Carnaval, Sexta-feira Santa, Corpus Christi e feriado municipal não entram (*shortcut*: na produção o calendário vem de uma tabela). (4) Os **ids de fábrica** (1 a 5) valem para navegador novo; no navegador migrado, os níveis ficam com ids depois do maior existente. (5) **A Hipercard** entra no grupo da Elo e da American Express, como a página de taxas.

**Provado nos dois sentidos, numa cópia fora do projeto.** `teste_gateways.py` (357 asserções, seção [8] nova: o exemplo real, amostras de taxa por nível e bandeira, Visa = Mastercard, o tipo antigo convertido, a troca do exemplo antigo com o gateway do usuário preservado) e `teste_gateway_uso.py` (209; seções [7] o exemplo real no PDV, [8] o desconto, [9] Configurações › PDV e a troca vista pelas quatro telas). As seções 1 a 6 rodam numa **bancada** de três gateways de números redondos (para testar o mecanismo sem depender das taxas oficiais), com o desconto desligado; o cenário "loja sem maquininha" desabilita a Bronze dentro do próprio teste. `teste_pdv.py` (201) e `teste_formas_recebimento.py` (130) foram ajustados para a Bronze e o desconto. Defeitos injetados numa cópia das telas (fora do projeto), **oito, todos pegos**: prazo em dias corridos (10 falhas); desconto sobre a venda toda e não só sobre o Pix/dinheiro (8); desconto também no cheque (1); débito ignorando a bandeira (5); a troca do exemplo apagando o gateway do usuário (3); tirar o desconto sem pedir senha (4); troco sobre o valor cheio (1); percentual fixo que não acompanha o nível (3).

**O que conferir** (também no PROGRESSO): o Pix e a venda dividida no PDV, o débito na Elo, o interruptor em Configurações › PDV e os quatro níveis na lista de Gateways.


## 14.95 Custos do E-commerce, entrega 1: o lucro de cada pedido online (22/out/2026)

Barganha aprovada pelo usuário em 21/out (as decisões abaixo não se reabrem). O módulo é um **relatório vivo do lucro de cada pedido online**: dos pedidos do canal **Loja virtual** (as vitrines da Desk Shope e da Desk Brands; marketplace só no futuro), desconta o que saiu do bolso e mostra o lucro e a margem. **Não é cadastro de custos.** PDV e venda manual ficam de fora (vão para a Margem de Contribuição); o imposto também. O módulo tem 3 entregas; esta é a 1. A entrega 2 (devolução, antecipação, vale de cortesia, itens nos pedidos online, agrupar e filtrar por Produto, Categoria e Estado) e a 3 (anúncios, gráfico mês a mês, Parâmetros de Vendas com imposto padrão e margem mínima, o módulo no perfil) **não começaram**.

**O que nasceu.**

- **A tela** `telas/vendas/pagina-vendas-custos-ecommerce.html` (menu Vendas › Custos do E-commerce; o item ganhou `data-href` nas 89 telas): lista viva, sem botão de gerar. Filtros: **período** (o componente do Giro, com "Do mês" e De/Até, abrindo no mês atual), **loja** e **busca** (nº do pedido, exata, ou cliente). **Seis cards**: Faturamento, Custos, Lucro, Margem, e os dois de alerta que filtram (**No prejuízo** e **Produto sem custo**, com a borda azul quando ativos, como em Contas a Pagar). **A barra "Divisão do faturamento"** (nome e legenda mudaram em §14.96; custo dos produtos, frete, taxa, comissão, embalagem e lucro, com legenda em R$ e %; lucro negativo fica só na legenda, "fora da barra"). **Agrupar por** Pedido (padrão), Loja, Vendedor/Afiliado e Forma de pagamento; clicar numa linha agrupada volta para Pedido, filtrado por aquele grupo. Colunas por pedido: Pedido (nº, e a data e o cliente embaixo), Loja, Venda, Frete cobrado, Dif. de frete, Taxa, Comissão, Embalagem, Custo, Lucro e Margem; a **Comissão de marketplace** existe e só aparece quando algum pedido tiver valor (hoje é zero em tudo). **Clicar no pedido** abre o painel lateral com a conta e o link `../vendas/pagina-vendas-pedidos-detalhe.html?id=<id>` (e atalhos para Gateways, de onde sai a taxa, e Comissões, de onde sai a regra). **Mais ações**: Configurar, Baixar planilha e Imprimir (os dois últimos, do bloco compartilhado).
- **Configurar** (painel "Configurações"): **Situações dos pedidos** (multi-seleção; de fábrica, todas menos Cancelado), **Custo baseado em** (Custo da compra, que é o padrão, ou Custo médio) e **Embalagem por loja** (R$ por unidade: Shope 5,00, Brands 8,00, Tech 0,00). **Aplicar** grava em `deskParametros.custosEcommerce` e registra no Registro de atividades (ação nova `custosEcomConfig`, grupo Vendas, sem senha de fábrica, nas 20 telas que carregam o catálogo); **Cancelar** descarta. A calculadora de preço vai ler `deskParametros.custosEcommerce.embalagemPorLoja`.
- **A conta única**, o bloco comum **`RESULTADO DO PEDIDO`** (`resultadoDoPedido(p)`), idêntico em cinco telas: a nova, a página do pedido, as duas de Comissões e o cadastro do cliente. `venda` = total menos o frete cobrado; `difFrete` = frete pago pela loja menos o cobrado (sem o dado, 0; pode ser negativo); `taxa` = a do gateway da loja virtual (habilitado na loja do pedido, lido do bloco `GATEWAYS: LEITURA`) **sobre o total**, na condição do pagamento, mais a tarifa (pix na InfinitePay é 0; sem `pagamento`, 0 e "sem dado"); `comissao` = a **soma** de `comissaoDoPedido` de quem recebe no pedido, pela regra de Comissões (o bloco `COMISSOES: DADOS E REGRAS`, que a conta só aplica, sem reescrever); `comissaoMarketplace` = 0; `embalagem` = a da loja × as unidades; `custo` = o da compra ou o médio; `lucro` = venda − difFrete − taxa − comissão − marketplace − embalagem − custo; `margem` = lucro ÷ venda. Cada parcela é arredondada no centavo antes de somar. Cada tela que ganhou a conta ganhou também, idênticos, os blocos de que ela depende (`GATEWAYS: LEITURA` e `COMISSOES: DADOS E REGRAS`); o de `PARÂMETROS DO SISTEMA` já estava em todas.
- **Os pedidos** (Pedidos de Venda é a dona do dado; os espelhos são a página do pedido, o bloco de Comissões nas três telas que o têm e a tela nova): `canal` (`loja_virtual` nos pedidos 1, 3, 4, 8, 9, 11, 12 e 16; `manual` nos outros; 4, 8 e 12 vêm de link de afiliado, e a Desk Tech, loja 3, não tem vitrine), `custoMedio` (nos manuais, igual ao `custo`: sem histórico diferente no exemplo), `fretePagoLoja` e `pagamento` { forma, bandeira, vezes } só nos online. **O pedido 11 está no prejuízo de propósito** (frete grátis para longe: a loja pagou R$ 95,00 por um pedido de R$ 219,90; lucro − R$ 32,49).
- **A página do pedido**: o campo **"Frete pago pela loja"** ao lado de "Frete pago pelo cliente" (mesmo componente; vazio e "—" em leitura nos pedidos manuais, porque não sabemos); o **canal** no cabeçalho ("Canal: Loja virtual" ou "Venda manual"); a caixa **"Resultado do pedido"** (venda, frete cobrado, diferencial, taxa, comissão, embalagem, custo, lucro e margem, com o link "ver em Custos do E-commerce"), em todos os pedidos da lista, manuais inclusive, com "—" no que é sem dado; e a **forma de recebimento e as parcelas** alimentadas pelo `pagamento` do pedido online.
- **Comissões** passou a usar `resultadoDoPedido(p).lucro` no lugar do `lucroDe` (venda − custo − comissão), que saiu; o título da coluna Lucro (e o do card) diz a conta nova. O pedido 3, por exemplo, que dava R$ 132,50 de lucro em Comissões, agora dá R$ 105,50.

**Contas à mão** (as de `teste_custos_ecommerce.py`): pedido 3 (pix, Marina 5%) vende 349,90, dif. 22,00, comissão 17,50, embalagem 5,00, custo 199,90 e lucra **105,50**; pedido 12 (crédito Visa 10x, afiliado Bruno 5%, Brands) tem taxa 15,06% de 1.024,00 = 154,21, comissão 51,20, embalagem 8,00 e lucra **180,09**; pedido 11 (crédito Elo 2x) tem taxa 13,39, comissão 11,00 (10,995 sobe) e lucra **− 32,49**; pedido 1 (crédito Visa 3x, 8 unidades, frete cobrado 10,00 e pago 18,50) tem taxa 132,49 **sobre o total de 1.890,00**, comissão 94,00 **sobre a venda de 1.880,00**, embalagem 8 × 5,00 e lucra **477,01** (500,01 em custo médio). Lucro dos oito online, em custo da compra: 1 → 477,01 · 3 → 105,50 · 4 → 160,60 · 8 → 158,46 · 9 → 158,00 · 11 → − 32,49 · 12 → 180,09 · 16 → 366,16.

**Decisões que couberam ao executor (para o usuário confirmar).**

1. **A página do pedido não podia receber o bloco de Comissões como estava**: `brDe` (recebia um `Date`, e o bloco recebe texto ISO) e `diasDeAtraso` (outra conta, de outro assunto) tinham o mesmo nome. A saída escolhida (A) foi **renomear só na página do pedido**, sem mudar comportamento (`brDe` → `brData`, `diasDeAtraso` → `diasDeAtrasoConta`, e o `isoDe` repetido saiu), e colar o bloco idêntico. `teste_pedidos.py` passou a chamar `brData`.
2. **A comissão do pedido é a soma** de todos os beneficiários cujo `pedidosDe(b)` tem o pedido (vendedor e afiliado), achados pelo número do pedido. Hoje a regra de Comissões deixa um só por pedido (o link do afiliado vale sobre o vendedor).
3. **As unidades** do pedido são o campo `unidades`, só onde o exemplo tem itens (pedidos 1, 2, 6 e 10: 8, 23, 14 e 32, a soma das quantidades de `ITENS_PEDIDO`); nos outros, 1, coerente com o "Item de exemplo" da página do pedido. Os itens dos pedidos online só chegam na entrega 2.
4. **O padrão da configuração mora no bloco** `RESULTADO DO PEDIDO` (`custosEcomLer()`), e não em `PARAM_PADRAO`: assim nenhuma das 80 telas que carregam os parâmetros foi tocada. O bloco lê `deskParametros.custosEcommerce` direto do navegador, na hora de cada conta.
5. **A caixa da página do pedido é ao vivo**: lê o total, o frete cobrado, o frete que a loja pagou e as unidades que estão na tela, e muda enquanto se digita. O que a página não edita (custo, custo médio, forma de pagamento, quem recebe a comissão) vem do pedido da lista. **Pedido novo, clonado, venda de balcão (PDV) e o exemplo sem `?id=` não têm registro**: a caixa diz isso, em vez de inventar número (o clone de um pedido online vira venda manual e não herda o canal, o custo, o frete da loja nem o pagamento).
6. **O pagamento do pedido online alimenta a forma e as parcelas da página** (crédito, 10x etc.); a lista de condições da página não tem todas as vezes, então a que falta (o 10x do pedido 12) entra no menu só nesse pedido.
7. **Os cards**: Faturamento, Custos, Lucro e Margem, e as contagens dos dois de alerta, somam a lista inteira (período, loja, busca), sem o filtro do próprio card; **a barra segue a lista que a tabela mostra**, com o card ligado, e diz isso no título ("só os pedidos no prejuízo"). **Custos** é tudo o que saiu: diferencial de frete, taxa, comissão, embalagem e custo (faturamento − custos = lucro).
8. **Agrupar**: "Vendedor/Afiliado" agrupa por quem recebe a comissão do pedido (o afiliado do link, ou o vendedor marcado; sem nenhum, "Sem vendedor ou afiliado"); "Forma de pagamento" separa o crédito por parcelamento (Pix, crédito à vista, 3x, 10x...). Agrupado, a coluna Loja sai e a primeira vira o nome do grupo, e a ordem de fábrica passa a ser a de maior venda. Clicar em loja volta para Pedido com o filtro de loja; clicar em vendedor ou forma volta com uma faixa "Mostrando só ...: ..." e o botão "Tirar o filtro".
9. **O período**: "Do mês" é do dia 1 até hoje (como em Movimentação de Estoque); o link da página do pedido (`?busca=<nº>`) abre a tela no pedido, e se ele é de um mês anterior o período abre no mês dele (o exemplo guarda um ano).
10. **Largura**: sem barra a 1280px (com o menu aberto) até R$ 12.345,67 em todas as colunas e um cliente de 41 letras; com valores de R$ 99.999,99 em tudo a tabela passaria de 1280. A suíte guarda o caso de R$ 12.345,67.
11. **Cada Aplicar** do painel grava e registra, mesmo sem mudança; embalagem aceita zero ou mais, com até duas casas (vírgula ou ponto).
12. **O cancelado**: nenhum pedido online do exemplo está cancelado (o 15, que está, é manual); a suíte prova o "sai de fábrica e volta ao marcar" cancelando o pedido 9 na própria página. **O produto sem custo** idem: o exemplo não tem custo zero, a suíte zera o do pedido 9.
13. **A Rastreamento não foi tocada**: o `PEDIDOS` dela é de outra forma (o canal é um texto da vitrine, o pagamento é "pago") e nenhuma suíte o compara com a lista.

**Suíte e prova.** `teste_custos_ecommerce.py` (122 asserções, entra no selo): a conta de quatro pedidos contra o valor feito à mão no comentário do arquivo e dos 16 contra o oráculo em Python (`_ferramentas/oraculo_custos.py`, Decimal, meio para cima; `teste_comissoes.py` usa o mesmo); só os online; o cancelado e as situações; o custo médio; a embalagem por loja, que grava e muda o lucro; Cancelar descarta; a validação; o registro; os cards que filtram; o agrupar e o clique de volta; o painel e o link; a planilha; a largura; a página do pedido nos 16 pedidos, igual à lista e ao vivo; o lucro de Comissões; os blocos idênticos, os espelhos, o menu nas 89 telas e o catálogo. Ajustadas: `teste_comissoes.py` (o oráculo do lucro novo, o bloco idêntico em cinco telas, o catálogo em 20 telas), `teste_gateway_uso.py` (o bloco `GATEWAYS: LEITURA` em oito telas), `teste_pedidos.py` (`brData`), `teste_menu.py` (o PROGRESSO diz 45 de 55, 89 telas), `teste_gateways.py` (o item de menu existe nas 89 telas), `teste_vale_compra.py` (o catálogo está em 20 telas) e `teste_impressao.py` (25 telas com o bloco de planilha e impressão, 19 listas; o CSS próprio da tela entra antes do CSS do relatório, que é o bloco comum que fecha o `style`). **Defeitos injetados numa cópia fora do projeto, nos cinco blocos ao mesmo tempo (para a comparação dos blocos não ajudar), todos pegos:** a taxa sobre a venda em vez do total (16 falhas); o diferencial de frete com o sinal trocado (28); o custo médio ignorado (3); a embalagem sem as unidades (18).

**O que conferir** (também no PROGRESSO): a lista e os cards, a barra, o agrupar e o clique de volta, o painel do pedido, Mais ações › Configurar (custo médio, embalagem, situação Cancelado), a página do pedido (o campo, o canal, a caixa ao vivo, as parcelas) e se o lucro de Comissões agora faz sentido para você.

## 14.96 Custos do E-commerce, ajustes do teste: a barra e o pedido no cartão (26/out/2026)

Ajustes pedidos pelo usuário ao testar a entrega 1 (§14.95), decididos com ele; as decisões abaixo não se reabrem. Dois itens.

**1. A barra de Custos do E-commerce.** O título "Para onde vai cada R$ 100 vendidos" não ficou claro: agora é **"Divisão do faturamento"**, com a linha de apoio embaixo, menor e em cinza (`.ce-barra-apoio`): "De tudo o que foi vendido, quanto foi para cada custo e quanto ficou de lucro." O `escopoBarra` ("· só os pedidos no prejuízo") segue no título. A **legenda** deixou de correr em linha (quebrava desalinhada) e virou uma **grade de 3 colunas iguais**, 2 linhas para os 6 itens (Custo dos produtos, Frete, Taxa do gateway / Comissão, Embalagem, Lucro): cada item com a bolinha da cor, o nome e, embaixo, o valor em negrito e o %. O bloco fica **centralizado** sob a barra (largura máxima de 720px, `margin: 0 auto`) e, **abaixo de 900px, cai para 2 colunas**. O lucro (ou o frete) negativo continua na legenda, com "fora da barra". Só o HTML, o CSS (`ce-barra*`, `ce-leg*`) e o `renderBarra` dessa tela mudaram.

**2. O pedido no cartão: as contas a receber pelo gateway** (`pagina-vendas-pedidos-detalhe.html`). Antes, `planoDeParcelas` dividia o total pelo número de parcelas, uma por mês, e dizia "Salvar faz nascer N contas a receber": errado para o cartão. Com gateway **antecipado** (a InfinitePay) o dinheiro cai inteiro, menos a taxa, no dia útil seguinte. Regra nova, **só quando a forma de recebimento é cartão de crédito ou de débito** (Pix, dinheiro, boleto e crediário seguem exatamente como antes):

- **Qual gateway.** Pedido do canal **Loja virtual**: a InfinitePay habilitada na loja do pedido (o mesmo `gwlHabilitados(loja, 'infinitepay')[0]` de `resultadoDoPedido`). Outro pedido: o gateway padrão da forma (`gwlPadraoDaForma`, como o PDV). Bandeira: a do `pagamento` do pedido; sem ela, a padrão do gateway. A condição (taxa, tarifa e prazo em dias úteis) vem de `gwlCondicao(gateway, forma, bandeira, vezes)`; o débito não usa as parcelas do cliente.
- **A taxa é o mesmo número do "Resultado do pedido"**: total × taxa% + tarifa, no centavo (`resCent(resPct(...))`, as mesmas funções do bloco comum). A suíte confere nos pedidos online.
- **Gateway antecipado: uma conta só**, o valor bruto, a taxa e o líquido (bruto − taxa), vencendo hoje + o prazo em **dias úteis**, na conta do gateway (`gwlConta`). O chip mostra "1/1", o líquido em negrito e a data (com o bruto, a taxa e o líquido na dica do chip). A nota: "No cartão em **3x** do cliente, o gateway antecipado deposita tudo de uma vez: nasce **1 conta a receber** de R$ bruto, com R$ taxa de taxa, **R$ líquido** em DD/MM, na conta <nome>." (à vista: "No cartão à vista do cliente"; débito: "No débito do cliente").
- **Gateway sem antecipação: uma conta por parcela**, com a divisão de centavos de sempre (a sobra na primeira), cada uma com a sua parte da taxa (a taxa total repartida em centavos do mesmo jeito, para a soma ser a do Resultado), a primeira vencendo no prazo do gateway em dias úteis e as seguintes um mês depois, passadas pelo dia útil. A nota diz quantas e o líquido total.
- **Sem condição** (sem gateway habilitado, ou o gateway sem a linha para a forma, a bandeira e as vezes): aviso à vista (`#erroCartao`) com o motivo e o link para Gateways, e **o Salvar bloqueia**, com o mesmo motivo (a regra do PDV, §14.93, decisão 4).
- **O Salvar não grava conta em lugar nenhum** (no protótipo nada persiste): só a pergunta de confirmação e a mensagem "Pedido salvo..." seguem o mesmo plano (bruto, taxa, líquido, vencimento e conta). Quando a conta a receber de verdade existir (arquitetura, §11), ela herda esses campos.
- O **vale-compra** continua como era: as parcelas valem para o que falta receber, e **a taxa é sobre essa parte** (o pedido nº 16, com R$ 25,00 em vale no exemplo, tem conta de R$ 2.315,00). O limite de crédito não mudou. A forma e a loja agora recalculam as parcelas (antes só a condição e os valores recalculavam).

**Conferência à mão** (pedido nº 1, crédito Visa 3x, R$ 1.890,00, InfinitePay da loja virtual): a taxa é **7,01%** (a tabela de fábrica do Link tem 4,20% em 1x, 6,09% em 2x e 7,01% em 3x), logo **1 conta de R$ 1.890,00, taxa R$ 132,49, líquido R$ 1.757,51**, no dia útil seguinte a hoje. O 6,09% e o R$ 115,10 do pedido de ajuste eram o 2x; a regra "o mesmo número do Resultado do pedido" (R$ 132,49 desde a entrega 1) manda.

**Decisões que couberam ao executor (para o usuário confirmar).** (1) **A página do pedido não tinha `diaUtil`**: o ajudante só existia no PDV; ela ganhou a mesma cópia (`diaUtil`, `maisDiasUteis`, a lista de feriados nacionais de data fixa, com o mesmo `shortcut`: Carnaval, Sexta-feira Santa e Corpus Christi ainda não contam). (2) **As parcelas seguintes** são o primeiro vencimento mais N meses (o dia 31 cai no último dia do mês curto), passadas pelo dia útil: ancoradas na primeira, e não encadeadas, para um fim de semana não empurrar todas as seguintes. (3) **A taxa por parcela** é a taxa total repartida em centavos (a sobra na primeira), e não a taxa de cada parcela recalculada: assim a soma é sempre a do Resultado. (4) **O "Resultado do pedido" não segue a tela**: continua usando o `pagamento` original do pedido, então, se o usuário trocar a forma ou as parcelas na tela de um pedido online, a conta a receber muda e a taxa do Resultado não. (5) Trocar a **forma** ou a **loja** passou a recalcular as parcelas. (6) O pedido manual usa o gateway padrão da forma **mesmo que ele não esteja habilitado na loja do pedido** (como o plano pediu); o PDV, que filtra pela loja, é mais estrito.

**Suíte.** `teste_custos_ecommerce.py` (133 asserções) ajustou o título e a legenda: os 6 itens na grade e na ordem, cada valor junto do seu nome e da sua cor, 3 colunas alinhadas e iguais, 2 linhas, o bloco centralizado e a queda para 2 colunas em tela estreita. **`teste_pedido_cartao.py`** (suíte nova, 78 asserções, entra no selo) fixa o relógio do navegador numa sexta (30/10/2026) e refaz a conta em Python: os 6 pedidos online no crédito (1 conta, taxa igual à do Resultado, vencimento em 03/11, que pula o fim de semana e o feriado de Finados), o pedido manual no crédito (à vista e parcelado) e no débito, o gateway sem antecipação (a cópia do gateway mexida dentro do teste: 3 contas, a divisão de centavos, a taxa repartida, os vencimentos 03/11, 03/12 e 04/01), os bloqueios (bandeira sem linha, débito no Link, InfinitePay desabilitada, nenhum gateway, o padrão sem a linha), as outras formas como eram, o vale-compra e a mensagem do Salvar. **Três defeitos injetados** numa cópia fora do projeto, **todos pegos**: a taxa sobre o valor da parcela (19 falhas), o antecipado ainda gerando N contas (13) e o vencimento em dias corridos (14).

## 14.97 Custos do E-commerce, entrega 2: itens, destino, devolução, cortesia, produto/categoria/estado (27/out/2026)

Plano decidido com o usuário; as decisões abaixo não se reabrem. Fora desta entrega: a antecipação (saiu do módulo: o cadastro de gateway não tem taxa de antecipação à parte, e na InfinitePay ela já está na taxa) e a entrega 3 (anúncios, mês a mês, Parâmetros de Vendas, acesso por perfil).

**1. Itens e destino nos pedidos online.** Os pedidos 3, 4, 8, 9, 11, 12 e 16 ganharam itens em `ITENS_PEDIDO` (lista de Pedidos de Venda, a dona) e `ITENS_DA_LISTA` (espelho da página do pedido), com produtos de Cadastros › Produtos (mesmo SKU, nome e categoria; a suíte compara). Cada item traz também a `categoria` e o custo de **uma unidade** (`custo`, o da compra, e `custoMedio`): é como o pedido congela o custo. Itens mais frete menos desconto fecham no `total`; a soma do custo dos itens fecha no `custo` e a do custo médio no `custoMedio` (nenhum `total` nem `custo` mudou). Unidades de cada pedido online (a soma das quantidades): 1 → 8, 3 → 1, 4 → 10, 8 → 10, 9 → 8, 11 → 5, 12 → 10, 16 → 16; o campo `unidades` saiu dos online e segue nos manuais 2, 6 e 10. O pedido 1 já fechava (1.880,00 em itens + 10,00 de frete): só ganhou categoria e custo por unidade. Os 8 online ganharam `ufEntrega` (SP, MG, RJ, PR, BA, **AM** no 11, PE, SP), mostrado na página do pedido junto do canal ("Canal: Loja virtual · Entrega em AM"). Os itens também moram, como espelho declarado, em `ITENS_ONLINE` (bloco novo abaixo).

**2. O bloco novo `DEVOLUCOES: LEITURA`**, idêntico nas 5 telas que carregam a conta (Custos, página do pedido, as duas de Comissões, cadastro do cliente). Tem: `ITENS_ONLINE`; `DEVOLUCOES_C`, espelho das 6 devoluções do exemplo de Logística › Devolução (id, número, venda, abertura, situação, itens com estado e a `reversa` com `paga` e `valor`); `ENTREGA_DA_VENDA` (o `entregaEm` das vendas 1, 3 e 4); `devolucoesLidas()` (a gravada em `deskDevolucoes` vence a de exemplo de mesmo id e a nova entra, como na Devolução); `totalItensDev` (o mesmo corpo de `totalItens`/`totalItensDev` da Devolução; a suíte compara) e `devolucoesDoPedido`. **Conta a devolução aceita**: em andamento ou finalizada. Aberta (em análise), cancelada e qualquer outra (a Devolução não tem "recusada"; a suíte prova com uma situação `recusada` gravada) não contam; a aberta aparece só como aviso ("Devolução em análise"). A devolução só vale para o pedido quando todos os itens dela existem nele: as vendas 2 e 5 da Devolução não são pedidos de Pedidos de Venda e ficam de fora.

**3. A devolução na conta** (`RESULTADO DO PEDIDO`). `devolucao` = valor devolvido − custo que voltou + frete da volta pago pela loja; o lucro desconta isso. Item **revendável** devolve o custo dele (o do item, do pedido, no custo da compra ou no médio, conforme a configuração); **avariado** ou perdido (`nenhum`) não devolve: o custo fica como perda ("Perda do avariado"). Frete da volta: o da `reversa` quando `reversa.paga` é `'nos'`; pago pelo cliente (`'cliente'`) ou coleta da nossa frota (valor 0), nada. **A taxa do gateway não volta** (não achamos a regra da InfinitePay; considerar que fica é o lado seguro). Painel do pedido (Custos) e caixa "Resultado do pedido" mostram valor devolvido, custo recuperado, perda do avariado e frete da volta. Na tela de Custos: a coluna **Devolução** (escondida quando zero em tudo, como a de marketplace) e o item "Devolução" na legenda da barra; "Custos" dos cards passou a incluir a devolução.

**4. O exemplo da Devolução** (lista e detalhe) aponta para os pedidos online 1, 3 e 4 com itens que existem neles, número, datas e situação como estavam. DV-0011 (pedido 1, em andamento): 1 fone e 2 carregadores **revendáveis** (445,00), reversa **paga pelo cliente** (24,50). DV-0010 (pedido 3, finalizada): o kit inteiro **avariado** (349,90), reversa **paga pela loja** (38,90); para o texto fazer sentido o motivo virou "Avaria no transporte", a forma "Dinheiro" e a descrição e dois eventos foram reescritos. DV-0009 (pedido 4, aberta): 1 tênis extraviado. DV-0007 (pedido 3, cancelada): o kit. As vendas 1, 3 e 4 da Devolução passaram a ter os itens e o total dos pedidos 1, 3 e 4 (o cliente e o número `PV-` delas não mudaram). Toda `reversa` ganhou `paga` e `valor`. Efeito: o pedido 3 ficou no prejuízo (devolvido inteiro e avariado).

**5. A comissão cai com a devolução dentro do prazo** (bloco `COMISSOES: DADOS E REGRAS`, em todas as cópias). `comissaoDoPedido` = comissão × (1 − valor devolvido ÷ base da comissão), em centavos, meio para cima; voltou tudo, zero. **Prazo** = `deskParametros.devolucaoPrazoDias` (Configurações › Parâmetros de Logística; 7 de fábrica, o arrependimento do CDC; o 7 do código é só o padrão de fábrica quando a chave não existe), contado da **entrega** (o `entregaEm` da venda na Devolução; sem ele, a previsão de entrega do pedido) até a **abertura** da devolução; fora do prazo a comissão fica inteira. A **comissão já liberada antes da abertura** não some do saldo: a diferença vira **estorno** (`estornosDe`), uma linha "Estorno: devolução do pedido nº X (DV-nnnn)" que desconta do saldo (entra na linha "(−) Débitos de devoluções" da conta, que já existia e valia zero, e portanto no próximo pagamento) e aparece no histórico do afiliado ou vendedor (tipo Comissão, efeito negativo). A que ainda não liberou apenas sai menor. **O afiliado** libera na entrega + o prazo de devolução (antes, entrega + 7 fixo); a página do pedido e a nota de Configurações › Cadastro de clientes dizem o prazo. Como `resultadoDoPedido` soma `comissaoDoPedido`, o lucro acompanha sozinho. Na aba Comissão da página do pedido o valor também cai (linha "Devolução dentro do prazo"). A comissão reduzida mostra "(menos a devolução)" na descrição.

**6. O vale de cortesia é desconto.** `venda` = total − frete − cortesia, em que a cortesia é o uso, não estornado nem perdido, de vale de origem **cortesia** no pedido (a leitura de `valeUsosDoDoc`, refeita no bloco porque Custos e as listas de Comissões não carregam o bloco do Vale-compra; `RES_VALES_EXEMPLO` é o espelho do que o exemplo grava e só vale enquanto a marca `deskValesCompraExemplo` não existe). Vale de devolução e de comissão não mudam nada. No exemplo: pedido 3 (15,00) e pedido 16 (25,00). **A comissão não mudou por isso**: é o item 9 da revisão geral, que continua lá. Coluna **Cortesia** em Custos (escondida quando zero em tudo) e, na legenda, o item Cortesia entra antes do Lucro quando há valor, fora da barra ("já fora do faturamento").

**7. Produto, categoria e estado na tela de Custos.** Agrupar por ganhou **Produto**, **Categoria** e **Estado de destino**; filtros novos: **Produto** (busca por nome ou SKU, sem acento) e **Categoria** (dropdown). A repartição (`partesDoPedido`) divide os custos do pedido entre os itens: frete cobrado, diferencial de frete, taxa, comissão, devolução, cortesia e venda na proporção do valor do item; a embalagem pela quantidade; o custo é o de cada item; a sobra de centavos fica na primeira linha e a soma das partes é o total do pedido a cada centavo. Com filtro de produto ou categoria ligado a lista mostra só os pedidos que têm o item, e a linha, os cards e a barra somam só a parte daquele item; o título da barra diz ("só a parte do produto ... em cada pedido"). Clicar numa linha de produto ou categoria volta para Pedido com o filtro ligado; estado volta com a faixa "Mostrando só estado de destino: ...". **A legenda da barra** passou a grade de **4 colunas** (4 itens em cima e 3 embaixo; 4 e 4 com a Cortesia); em tela estreita cai para 2.

**8. Conserto pequeno.** Na página do pedido, com o vale pagando o pedido inteiro e a condição em 3x, não nascem mais 3 chips de R$ 0,00 nem "Salvar faz nascer 3 contas": nenhum chip, e a nota "o pedido inteiro, sem conta a receber em aberto" do vale (`planoDeParcelas` devolve lista vazia quando não há o que parcelar).

### Ajustes do cartão (pedidos de 26/out, feitos na mesma rodada)

1. **Pedido online: forma de recebimento e condição travadas.** Quando `canal === 'loja_virtual'` os dois campos ficam só de leitura (o padrão `campo-leitura` da página), com a nota "pago na loja virtual"; o pagamento vem da vitrine, então a conta a receber e o Resultado do pedido nunca divergem. Pedido manual, pedido novo e o clone de um online (que vira manual) seguem editáveis.
2. **Pedido manual no cartão: gateway igual ao PDV.** O gateway padrão da forma, se estiver habilitado na loja do pedido; senão a primeira maquininha (tipo Outro) habilitada nela; sem nenhuma, o aviso `#erroCartao` com o link para Gateways e o Salvar bloqueado no cartão. Trocar a loja do pedido recalcula. (Antes usava o padrão da forma mesmo fora da loja: §14.96, decisão 6.)

**Decisões que couberam ao executor (para o usuário confirmar).**

1. **Os produtos novos não existem no catálogo da página do pedido** (`CATALOGO`, cópia do catálogo do PDV). Em vez de mexer no catálogo do PDV, o item de um produto que a página não conhece fica `foraDoSaldo` (sem conferência de saldo): o pedido online já foi feito na vitrine. `teste_doc_detalhe.py` deixou de exigir "todo produto no catálogo" e passou a exigir "no catálogo ou em Cadastros › Produtos".
2. **Os SKUs do pedido 1** (`FON-BT-200`, `CAR-33W-01`, `CAD-EXE-PT`) são os do catálogo do pedido e não existem em Cadastros › Produtos (o fone de lá é `ELE-1001`, a 129,90); a categoria deles é a mais próxima (Eletrônicos, Eletrônicos, Mobiliário e Decoração).
3. **A entrega para o prazo** é o `entregaEm` da venda na Devolução (a data que o sistema já tem); sem ele, a previsão do pedido. O espelho `ENTREGA_DA_VENDA` leva as vendas 1, 3 e 4. As datas do exemplo da Devolução são absolutas e as dos pedidos são relativas a hoje, então a devolução do exemplo "abre" antes da entrega prevista do pedido; mantidas porque o plano mandou manter as datas. As suítes provam o prazo com devoluções gravadas.
4. **O frete da volta usa a cobrança real** (`reversa.real`) quando ela foi registrada, e o `valor` cotado quando não: é o que a própria Devolução diz ("a despesa do frete acompanha o valor real").
5. **A data do estorno é a da abertura da devolução** (o protótipo não guarda a data em que ela foi aceita). A comissão liberada no mesmo dia da abertura ou depois sai já reduzida.
6. **As quantidades dos itens** foram escolhidas só entre os produtos ativos e vendáveis de Cadastros › Produtos, a preço de lista, para fechar o total sem mexer nele; o pedido 16 (R$ 2.340,00) tem 16 unidades, o menor possível com esses preços, e o 8 tem 10.
7. **Largura da tabela.** Com as colunas Cortesia e Devolução a tabela passou de 826 px a 1280; a fonte das células ficou em 11,5 px (antes 12), a do cabeçalho em 9,5 px e a da coluna Loja em 10,5 px. Cabe com o exemplo; com R$ 99.999,99 em todas as colunas e as duas colunas visíveis não cabe (a suíte guarda o pior caso com Cortesia e Devolução escondidas, as 11 colunas de antes).
8. **O Produto filtra por texto** (nome ou SKU), não por uma lista, e o Categoria por dropdown; a cor do item Cortesia na legenda é um violeta fixo (não há um quinto tom nas variáveis).

**Suítes e prova.** `teste_custos_ecommerce.py` (205 asserções; seções novas 9 a 13): os itens fecham (total, custo, custo médio), as unidades, as UFs, os espelhos (lista, página do pedido, 4 telas, Devolução, Cadastros › Produtos); a devolução contra o oráculo (revendável, avariado, frete da loja e do cliente, aberta, cancelada, recusada, item fora do pedido, custo médio, a gravada que vence); a cortesia (só a de origem cortesia, não estornada) e o espelho do exemplo; a repartição por item contra o oráculo e fechando no pedido; agrupar e filtrar. `oraculo_custos.py` ganhou os itens, as devoluções, a cortesia e a repartição. `teste_comissoes.py` (seção 12 nova): dentro do prazo, fora, o prazo do parâmetro trocado, o estorno da já liberada (saldo, conta e histórico) e o afiliado pelo parâmetro. `teste_pedido_cartao.py` (seção 7): os campos travados no online e livres no manual, no novo e no clone; o gateway da loja certa, o fallback e o bloqueio. `teste_vale_uso.py`: o vale que paga tudo em 3x. Ajustadas: `teste_afiliados.py`, `teste_doc_detalhe.py`, `teste_vale_origem.py` (DV-0009 agora vale 224,80) e o oráculo de `teste_comissoes.py`. **Defeitos injetados numa cópia fora do projeto, todos pegos:** o custo do avariado devolvido (26 falhas em Custos); a comissão caindo fora do prazo (2 falhas em Comissões); o frete da volta pago pelo cliente cobrado da loja (26 falhas em Custos); a repartição por item que não fecha no pedido (7 falhas em Custos).

**O que conferir** (também no PROGRESSO): a tela de Custos (as colunas Cortesia e Devolução, a legenda em 4 colunas, agrupar por Produto, Categoria e Estado, os filtros), o painel dos pedidos 1, 3 e 4, a página do pedido (UF, a caixa com a devolução, a forma e a condição travadas no online), Comissões da Marina (pedidos 1 e 3 reduzidos), e, num pedido manual no cartão, o gateway da loja certa.
