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

## 4. Estrutura de Menu (9 módulos principais + rodapé)

```
Início — Dashboard KPIs, Agenda, Minha Conta
Cadastros — Clientes, Fornecedores, Produtos, Vendedores, Embalagens, Lojas Desk,
            Depósitos, Marcas de Produtos, Departamento de Produtos, Seção de Produtos,
            Categoria de Produtos, Relatórios de Cadastros
Estoque — Controle de Estoques, Entrada de Notas, Ordens de Compra,
          Transferência Entre Estoques, Necessidades de Compra, Giro de Estoque,
          Acerto de Estoque, Inventário, Relatórios de Estoque
Vendas — Vendas, CRM, PDV, Notas Fiscais, Vendas Afiliados, Metas, Performance de Vendas,
         Margem Contribuição, Custos do E-commerce, Relatórios de Vendas
Logística — Separação, Etiquetagem, Expedição, Rastreamento de Pedidos,
            Devolução, Relatórios de Logística
Finanças — Caixa, Contas a Pagar, Contas a Receber, Comissões Afiliados,
           Relatórios Finanças
Operacional — Transportadoras, Formas de Pagamento, Cupons, Motivos de Devolução,
              Motivos de Perda, Relatórios Operacional
Integrações — Lojas Desk, Marketplaces e Hubs, Emissão de Notas Fiscais,
              Gateways de Pagamento, Relatórios de Integrações
Configurações — Cadastro de Usuários, Permissões de Usuários,
                Cadastro de Contas Bancárias, Relatórios de Configurações
                (+ seletor de tema Auto/Claro/Escuro fixo no rodapé do painel)

Rodapé fixo: Notificações, Central de Suporte, interruptor "Fixar menu"
```

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
- **Números alinhados à direita, texto à esquerda** (`.col-texto`). `white-space:nowrap` em tudo — a largura da tabela é que se adapta, nunca o conteúdo quebra.
- **Ordenação por clique no cabeçalho**: `th.ordenavel` com uma seta (`.seta`) em opacidade baixa; a coluna ativa ganha `.ordenado` e a seta vira ▲/▼ na cor `--active-text`. Clicar de novo na mesma coluna inverte.
- **Sempre dentro de `.estoque-table-wrap` com `overflow-x:auto` e `min-width` na tabela** — a rolagem horizontal fica na tabela, **nunca na página**. Conferir com `document.documentElement.scrollWidth` no navegador, não no olho.
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

- **Abertura inteligente**: mede o espaço disponível abaixo antes de abrir; se não couber, adiciona `.abrir-para-cima` (abre pra cima). Regra vale pra qualquer dropdown novo, sem exceção.
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

**Botão cuja tela existe NAVEGA.** Aviso é para o que depende de servidor (upload de XML, persistência), de módulo que ainda não existe (Relatórios, Pedidos) ou de coisa externa (NF-e) — e o aviso **nunca promete data** ("no fim da fase" vence e vira mentira). Até 29/set, 19 botões em 10 telas do Estoque respondiam *"a navegação entre telas só passa a funcionar no Lovable"* ou *"é a próxima tela a ser construída"* para telas que já existiam — as listagens de Ordens de Compra e de Entrada de Notas nem tinham caminho para o próprio detalhe. `_ferramentas/teste_becos.py` reprova essas frases e confere cada destino.

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

No protótipo, detalhe que não lê `?id=` (Ordem de Compra, Nota de Entrada, os 5 Cadastros) mostra o registro de exemplo — inclusive no `?novo=1`. No Lovable o registro novo abre vazio. **Toda porta de entrada de um detalhe é testada** (Incluir, Editar, consulta): o modo leitura de 28/set fez o *Incluir* dos 5 cadastros cair num registro somente-leitura, e só um teste por porta pega isso.

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
| Controle de Estoques — detalhe do produto | `pagina-estoque-controle-estoques-detalhe.html` (menu Estoque) | **Construída em 15/set/2026.** Substitui o drawer de extrato da v1 — o drawer era a exceção num sistema onde todo o resto já tem `-detalhe`. Traz a **faixa de KPIs com a quebra completa dos estágios** (físico · a endereçar · bloqueado · reservado · disponível), mais **em conferência num painel separado, tracejado**, porque não é estoque. É essa faixa que permite a listagem ficar rasa em 9 colunas. Abas **Lançamentos / Reservas** (§7.2); reservas nasce com estado vazio explicando que depende de `orders`. Ledger com uma coluna que o Olist não tem — **em que estágio o saldo caiu**. O botão **Incluir lançamento** abre o acerto inline: tipo (Entrada/Saída/**Balanço**, que informa a contagem e o sistema deriva a diferença), depósito, data/hora automáticas, quantidade, **Preço unitário visível e travado** no custo médio vigente (§11), **Motivo estruturado e filtrado pelo tipo** — mesmo padrão da Conferência — e **seletor de origem que só aparece quando o produto tem saldo em mais de um estágio**. Saída nunca sai de reservado, e saída maior que o estágio é barrada com o número disponível na mensagem. Motivo com consequência fiscal pinta o **aviso de CFOP 5.927 + estorno de crédito** e, ao salvar, avisa que o lançamento entrou na fila de regularização **Atualizada em 15/set/2026 (fundação do saldo por endereço):** ganhou a aba **Endereços**, que mostra onde o saldo está — endereço, tipo, depósito, estágio e quantidade — marcando a **base de picking** e apontando **↓ repor** quando ela está abaixo do `minimoBase`. É a leitura que o módulo de Reposição vai consumir. O **Incluir lançamento** passou a obedecer a regra de entrada: uma **prévia ao vivo** diz, antes de salvar, para onde o saldo vai — base com espaço livre → *reposição, disponível na hora*; base cheia → *parte na base, excedente a endereçar*; sem base no depósito → *tudo a endereçar, não vende*. A origem da saída deixou de ser estágio solto e passou a ser **linha de saldo (endereço + estágio)**, porque com saldo por endereço o mesmo estágio existe em vários lugares. |
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
| Inventário de Estoque | `pagina-estoque-inventario.html` (menu Estoque) | **Construída em 16/set/2026 — última tela de estoque da F5.** Abre num **índice de três caminhos**, não numa lista: *Gerar inventário* (monta pelos filtros), *Importar por planilha* (CSV/XLS/XLSX até 2 MB, exige **depósito de destino** porque o arquivo não diz onde a contagem aconteceu) e *Importar por coletor* (TXT até 2 MB, **um código por linha — a repetição É a quantidade**, sem coluna de total; valida por GTIN/EAN, SKU ou ambos). O que separa esta tela do Acerto está escrito no topo dela: **o inventário bloqueia o saldo do depósito inteiro** da abertura ao fechamento — venda, transferência e acerto ali são recusados —, e por isso é último recurso, não ferramenta de rotina. Notas **em conferência** continuam entrando e ficam **fora da contagem**, coerente com a regra de que em conferência não é estoque físico. A lista abre em **modo leitura** (Produto · SKU · Preço · UN · Localização · Estoque atual · Estoque disponível); **Informar quantidades** revela as colunas *Qtde inventário* e *Diferença* e troca o próprio botão por **Salvar quantidades e fechar**. Filtros de geração (Busca, Categoria, Fornecedor, Tags, Exibir, Situação do produto e **Valor baseado em**, agrupado em Preço de compra / de custo / de venda) valem **só na geração**: depois de aberta, a lista é fixa — mexer no filtro com inventário em andamento trocaria o universo contado. **Ausência de leitura nunca vira zero automático** (decisão de 16/set/2026): produto com saldo no depósito que não apareceu no arquivo entra como **não contado**, e não contado **não mexe no saldo** no fechamento. Quem varreu o depósito inteiro usa **"Zerar os não contados"** em Mais ações, com confirmação que explica a consequência — a alternativa (assumir zero sozinho) apagaria saldo bom por causa de um corredor que o coletor não percorreu. No fechamento, **diferença positiva segue a mesma regra de entrada do item 19** (base de picking no depósito → nasce disponível até a capacidade, excedente e sem-base → *a endereçar*, não vende) e **não gera documento fiscal**; **diferença negativa** sai do disponível, base primeiro, e nasce com **pendência fiscal de NF-e CFOP 5.927** sem travar. **Reservado e bloqueado não são tocados** — inventário conta prateleira, não desfaz reserva de pedido nem libera avaria. Fechar exige **usuário + senha** e é **permissão de perfil** (`Fechar inventário de estoque`, agora ativa na lista de confirmações de Vendedores). **Cancelar inventário** destrava o depósito sem alterar nada. Mais ações traz ainda **Exibir/Ocultar filtros**, **Imprimir lista** (`@media print` deixa só a tabela) e **Baixar CSV** — os dois de verdade, não mocados. |
| Configurações do Sistema ERP *(hub)* | `pagina-configuracoes.html` (menu Configurações) | **Construída em 18/set/2026 — abre o módulo de Configurações.** É um **hub**, não uma área com abas internas: índice com **busca** e **nove abas que filtram uma lista de links**; cada link abre **página própria**, com breadcrumb e voltar — o padrão que o sistema já usa. **As abas são os NOSSOS módulos** (geral · cadastros · estoque · vendas · logística · finanças · operacional · **fiscal** · integrações), não os do Olist, onde *separação* e *expedição* vivem em Vendas e aqui são Logística. *Fiscal* ganhou aba própria: certificado, ambiente, naturezas de operação, intermediadores e RTC não cabem como sub-item de Vendas. Cada aba abre com um **banner de contexto** que diz a regra que importa naquele domínio (ex.: em Estoque, que os limiares de tempo passam a morar ali; em Integrações, que o disponível enviado ao canal é o nosso, menor que o de outros ERPs). **O badge de estado é DERIVADO, nunca escrito à mão:** item com destino está construído e não leva selo; item sem destino leva **"a construir"**. A primeira versão tinha badges escritos manualmente (*configuração pendente*, *ambiente de testes*) em telas que sequer existiam — o índice prometia estado de coisa inexistente. Derivar do `href` torna impossível uma tela nascer mentindo que está pronta, e transforma o índice num **mapa de progresso** real. A **busca varre todas as abas de uma vez** (nome e texto de ajuda, ignorando acento) e mostra a **aba de origem** ao lado de cada achado. O ícone `?` aparece só nos itens que têm explicação, no `title`. **Onde cada coisa mora — a régua é a FREQUÊNCIA de uso** *(decidido em 18/set/2026, a partir de pergunta do usuário)*: a primeira versão do hub trazia atalhos para Marcas, Categorias, Departamentos, Seções, Embalagens, Depósitos, Endereços de Estoque, Metas e Vendedores — o **mesmo arquivo** do módulo, alcançado por dois caminhos, como o Olist faz. O usuário perguntou se era a mesma tela; **se quem aprovou o desenho teve a dúvida, quem opera vai ter também**, e os atalhos saíram. **O critério não é "é lista auxiliar", é com que frequência se mexe:** cadastrar marca nova acontece toda vez que chega produto de fornecedor novo — isso é **operação** e pertence ao módulo; *Tipos de contato*, *Variações*, *Atributos*, *Linhas de produtos* e *Parâmetros de estoque* se definem uma vez e quase nunca se revisitam — isso é **configuração** e pertence ao hub. A regra que o usuário aprende numa vez: **cadastro fica no módulo, parâmetro fica em Configurações**. O único ganho real que os atalhos tinham era guiar o **setup inicial** — e isso passou a ser resolvido pelo **Guia de primeiros passos** (abaixo), que é a solução do próprio Olist e não suja a navegação do dia a dia. **Duplicar tela continua proibido** em qualquer hipótese: duas telas para o mesmo cadastro divergem em semanas. |
| Parâmetros de estoque *(Configurações → estoque)* | `pagina-configuracoes-parametros-estoque.html` | **Construída em 18/set/2026 — primeira tela filha do hub.** É a tela que tira de dentro do código os **três limiares de tempo** que as telas de Estoque usavam cravados: *Conferência de compra* (alerta/crítico de dias de espera na doca), *Endereçamento* (alerta/crítico de dias parado em `a_endereçar`) e *Estoque zero na base de picking* (dias com a base zerada). **Layout GNRE** (§6): campo à esquerda, explicação à direita, na grade `.par-linha` — porque parâmetro que ninguém entende é parâmetro que ninguém mexe. **A prova de que a tela não é decoração:** junto com ela, os **7 números cravados** em `pagina-estoque-enderecamento.html` (5) e `pagina-estoque-conferencia-entrada.html` (2) foram substituídos por um bloco `PARAM` nomeado, logo depois de `<script>`, com comentário dizendo de onde o valor vem no Lovable (`tabela parametros`, por chave). Sem esse refactor a tela salvaria um número que nenhuma outra leria. **Regra nova: número que decide cor, alerta ou bloqueio nunca nasce literal dentro de um `if`** — nasce em `PARAM`, ainda que a tela de configuração venha depois. **Prévia viva:** cada seção mede o efeito do número na fila de hoje (*"Na fila de hoje (6 saldos): 3 ficariam em alerta e 1 ficaria em situação crítica"*) e recalcula a cada tecla — o usuário vê a consequência antes de salvar, em vez de descobrir amanhã. **Validação:** crítico tem de ser maior que alerta (salvar é bloqueado com modal explicando qual par está invertido), inteiro de 0 a 365, não-numérico recusado. **Barra fixa de salvar** com contador de alterações não salvas e **Restaurar padrão** (1 · 3 · 2 · 7 · 7). O breadcrumb do meio volta para o hub. |
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

**A causa estava escrita no código.** A fila, ao mandar conferir, mostrava: *"a navegação entre telas só passa a funcionar de verdade no Lovable"* — texto que ficou obsoleto em **22/set**, quando o cross-link do menu passou a navegar nas 53 telas. O segundo item de menu nasceu como contorno de uma limitação que já não existia. **Mensagem de limitação tem prazo de validade: quando a limitação cai, ela vira mentira que gera desvio.**

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

A seção 5 da auditoria oficial diz *"todos os botões respondem"* — e respondiam: **19 botões em 10 telas do Estoque** abriam um aviso dizendo que a tela de destino *"é a próxima a ser construída"* ou que *"a navegação só funciona no Lovable"*, com a tela existindo havia semanas. As listagens de Ordens de Compra e de Entrada de Notas **não tinham caminho nenhum** para o próprio detalhe. As telas do Estoque nasceram entre 14 e 16/set; a navegação real chegou em 22/set, e a varredura daquele dia cobriu **o menu, não os botões de dentro das telas**.

**Regra: quando um pré-requisito passa a existir, procurar todo texto que dependia da ausência dele.** A mensagem da Conferência (29/set, tarde) era o primeiro caso; a pergunta *"em quantos arquivos isso existe?"* não foi feita naquela hora e deveria. `teste_becos.py` reprova as frases e confere os destinos.

### A senha armada no ramo errado

Em 18/set a exclusão passou a pedir senha, e a varredura pôs `armarSenhaModal()` antes do **primeiro** `abrirModalConfirmacao` de cada handler de exclusão em massa. Em três telas — **Ordens de Compra, Depósitos e Endereços** — o primeiro modal era o **aviso** de que nada podia ser excluído. Resultado invertido: o aviso pedia senha para fechar, e **a exclusão de verdade acontecia sem senha**. 687 asserções do `teste_confirma_senha.py` não pegaram porque exercitavam o detalhe, não a exclusão em massa com guarda.

**Regra: a senha é armada na linha imediatamente anterior ao modal que EXECUTA — nunca no topo do handler.** Handler com ramo de guarda tem dois modais, e só um deles faz alguma coisa.

### Recurso novo num ponto por onde passam várias portas

O modo leitura (28/set) entrou no carregamento do detalhe — e o detalhe é aberto por **Incluir**, por **Editar cadastro completo** e pela consulta. As três portas passaram a cair em leitura, e *"Incluir cliente"* abria um cliente existente sem poder editar. **Regra: mudança no carregamento de uma tela se testa por cada porta de entrada**, não pela tela aberta direto.

### Documento que diz "em aberto" para o que foi decidido

O roadmap tinha **17 perguntas marcadas "decidir antes de construir"** já respondidas pelo §12 — que ficava logo abaixo, no mesmo arquivo —, **9 cabeçalhos com ⏳** de coisas prontas ou aprovadas, e o *Estado atual* contava **31 telas quando eram 52**. Cada decisão foi escrita num lugar novo sem voltar à pergunta original. **Regra: ao decidir, anotar a pergunta de origem com a resposta e onde ela está** (`→ ✅ Resolvido (data): …`), senão o documento continua perguntando o que já foi respondido — e o prompt do Lovable herda a dúvida.

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
  de agora. `inicializarHoraField` mora na tela do assunto. A Agenda ainda usa dois dropdowns
  (Hora e Min): são dois desenhos para a mesma coisa, à espera de o usuário escolher um.
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
