# ERP Desk Company — contexto da pasta local

ERP multi-loja (Desk Shope, Desk Brands, Desk Tech, Desk Flash). Protótipos em HTML/CSS/JS
puros, sem build e sem framework: cada `pagina-*.html` é um arquivo autocontido. Eles são
validados aqui e só depois viram prompt pro Lovable.

**Regra de ouro:** protótipo HTML → aprovação do usuário → prompt pro Lovable. Nunca pular etapa.

Quando o usuário disser **"vamos barganhar"**, pare e negocie antes de implementar: apresente
trade-offs, pergunte o que estiver ambíguo e só construa depois do aval.

O design system, os componentes, os não-negociáveis e o portão de QA vivem nas skills
`desk-company-erp` e `desk-company-page-qa` (plugin instalado, carregam sozinhas). **Este
arquivo não repete nada disso** — ele cobre apenas o que é específico desta máquina.

---

## Onde fica cada coisa (desde 08/out/2026)

O projeto mora em `C:\Claude AI\Desk Company\ERP System`, e essa pasta é a raiz do git.
Até 08/out as 71 telas ficavam soltas na raiz; agora cada uma mora na pasta do seu módulo.

```
ERP System\
├── CLAUDE.md
├── telas\                 o que o servidor de preview entrega
│   ├── inicio\            boas-vindas, agenda, minha conta e o dashboard de KPIs
│   ├── cadastros\  estoque\  vendas\  logistica\  financas\
│   ├── configuracoes\     abre pelo hub; guarda também Transportadoras e os Motivos
│   ├── integracoes\       vazia: nenhuma tela construída ainda
│   ├── _molde\            pagina-molde-referencia.html
│   └── fontes\            Nunito, usada por todas as telas
├── docs\                  design system, arquitetura, mapa dos módulos, pesquisas
└── _ferramentas\          selo, suítes, auditoria e servidor de preview
```

Quatro regras seguram essa estrutura:

- **O nome do arquivo continua único no sistema inteiro.** `pagina-vendas-metas.html` existe
  uma vez só. É por isso que as suítes, o selo e os documentos seguem citando a tela pelo nome.
- **A pasta é o módulo do MENU, não o prefixo do arquivo.** Quase sempre coincidem. A exceção
  é `pagina-dashboard-kpis.html`, que fica em `inicio\` porque é lá que o menu a mostra.
- **Link entre telas é sempre `../<pasta>/<arquivo>`**, mesmo quando as duas estão na mesma
  pasta. Uma regra só, sem caso especial. Vale para `href`, `data-href` e `location.href`.
  As fontes são `../fontes/...`.
- **Só `_ferramentas/localiza.py` sabe onde cada tela mora.** Suíte nova pede a tela pelo
  nome: `localiza.uri('pagina-x.html')`, `localiza.http(...)`, `localiza.caminhos()`. Nunca
  `glob('pagina-*.html')` nem caminho montado à mão.

**Tela nova nasce na pasta do módulo dela.** Copiou uma tela de outro módulo como base: os
links já estão no formato `../<pasta>/`, então continuam certos. O que muda é só o arquivo.

---

## Passo 0 aqui é diferente do Passo 0 da skill

A skill descreve o fluxo do app da Claude: `device_stage_files` → trabalhar numa cópia em
`/home/claude/desk-company/` → `device_commit_files` de volta. **Nada disso se aplica aqui.**

Neste ambiente (Antigravity + extensão do Claude) a pasta do projeto é
`C:\Claude AI\Desk Company\ERP System`. Leitura e escrita acontecem **direto no arquivo final**.
Não existe staging, não existe commit de volta, e não existe a classe de bug que vinha dessa
ponte (três entregas que aterrissaram em `Claude outputs\` e ficaram semanas defasadas sem
ninguém notar — ver `_ferramentas/LEIA-ME.md`).

Também não existem aqui: `present_files`, `SendUserFile`, `device_list_dir`,
`device_commit_files`, `mcp__remote-devices__*`. Não tente usá-los.

## Como o usuário vê uma tela

O servidor de preview é Node puro, sem dependências:

```bash
node _ferramentas/servidor.js        # porta 3000 (PORT=3001 muda)
```

Depois é só abrir `http://localhost:3000/vendas/pagina-vendas-pedidos.html`: o endereço é
`/<pasta>/<arquivo>` (a raiz `/` cai no dashboard). O endereço antigo, sem a pasta
(`/pagina-vendas-pedidos.html`), **redireciona** para o novo, então link velho em conversa ou
documento continua abrindo. Salvar o arquivo basta — um F5 já mostra a mudança. Não anuncie
"entreguei" sem dizer qual URL abrir.

## Verificação — rodar sempre antes de dar algo por pronto

A suíte é Python + Playwright e vive em `_ferramentas/`. Rodando de dentro dessa pasta:

```bash
python selo.py                  # o que está selado e o que precisa rodar
python selo.py --rodar          # roda só o que mudou, e sela o que passar
python selo.py --rodar --tudo   # ignora o selo (~7 min)
python auditoria.py ../telas/*/pagina-*.html    # auditoria estática de todas as telas
python localiza.py              # quantas telas há em cada pasta
python varredura_cliques.py     # ~10 min, antes de fechar um módulo
```

No Windows o comando é `python`, não `python3` — os exemplos da skill e do LEIA-ME usam
`python3` porque nasceram em Linux. Python 3.13.15 e Playwright + Chromium foram instalados
em 06/out/2026 e a toolchain **roda nativa aqui**, provada nesta ordem: auditoria estática
(0 falhas reais em 64), `selo.py` (21 suítes seladas, detectando sozinho o que mudou) e
`teste_cp.py` no navegador (53 asserções, 0 falhas).

**Se `python --version` responder "Python was not found" e falar da Microsoft Store**, não
conclua que falta instalar. O Python está em `%LOCALAPPDATA%\Programs\Python\Python313` e já
vem antes do `WindowsApps` no PATH do usuário; o que acontece é que o processo do editor
guardou um PATH antigo. **Reiniciar o Antigravity resolve.** Até lá, use o caminho absoluto:

```bash
"$LOCALAPPDATA/Programs/Python/Python313/python.exe" selo.py
```

Nunca instale Python de novo por causa disso — daria duas instalações concorrentes.

### Existem duas `auditoria.py` diferentes — use a do projeto

| onde | tem | não tem |
|---|---|---|
| `_ferramentas/auditoria.py` | checagem 10 (tag literal em texto de modal) | — |
| `assets/auditoria.py` da skill | seções 4B/5/6 (contraste WCAG medido) | checagem 10 |

**A da skill não conhece a estrutura por módulo.** Ela mora fora do projeto, varre
`pagina-*.html` numa pasta única e compara as telas entre si. Por isso o `selo.py` entrega a
ela um **espelho plano**: as mesmas telas copiadas para uma pasta temporária, com os links de
volta ao formato sem pasta (`localiza.espelho_plano()`). O HTML, o CSS e o JS auditados são os
mesmos; só o endereço das vizinhas muda. Para rodá-la à mão, aponte para o espelho, nunca para
`telas\` — lá ela encontra zero arquivos e sai dizendo que está tudo limpo. Quando a skill for
atualizada na origem para entender as pastas, o espelho some.

Nenhuma das duas é superconjunto da outra. **A do projeto é a canônica** para o dia a dia,
porque é a que o `selo.py` lê e a que cobre o bug que já voltou duas vezes. Vale rodar a da
skill também quando o assunto for contraste ou estouro de largura. Unificar as duas é dívida
aberta — quando mexer nisso, siga a regra da casa: provar nos dois sentidos (injetar o defeito
e confirmar que reprova; rodar nas 64 telas e confirmar o silêncio).

**A dívida cobrou três vezes só em 07–08/out, sempre no mesmo lugar: tela nova.** A do projeto
deu OK e a da skill reprovou, em `campo-qtd` sem CSS (Devolução detalhe), e de novo nos campos
de texto de Nomes do sistema, com o fundo branco nativo vazando no tema escuro. O padrão é
claro: **a do projeto é cega para "classe sem CSS" e para campo sem estilo** — as duas coisas
que mais aparecem quando se copia uma tela. Até a unificação existir, **rode as duas em toda
tela nova**, não só quando o assunto for contraste. O `selo.py` já roda as duas; o risco é
auditar à mão só com a do projeto e achar que passou.

## Git existe desde 06/out/2026

A pasta ficou até hoje sem versionamento. O commit inicial (`862c9ce`) é o estado de
06/out/2026, antes de qualquer alteração feita daqui.

- **A raiz do repositório é `ERP System`** desde 08/out/2026. O que está acima dela
  (`Desk Flash`, `C:\Claude AI\Skills`, os mapas) **não** é versionado aqui e não sobe para o
  GitHub. O remoto (`deskcompany/Desk-Company`) guarda só o ERP.

- `core.autocrlf=false` e `.gitattributes` com `* -text`: os arquivos nasceram com LF num
  ambiente Linux e os bytes ficam como estão. **Não mexa nisso** — mudar converteria 11 MB de
  HTML num único checkout e sujaria todo diff futuro.
- Commite por tela ou por módulo fechado, depois da verificação verde — não no meio.
- Antes de qualquer `sed`/substituição em massa nas telas, confirme que a árvore está
  limpa (`git status`). O desfazer agora existe; use-o em vez de confiar na sorte.

## Estado atual (06/out/2026)

**71 telas construídas**, 41 entradas de menu, 18 submódulos a fazer. F2 (Cadastros), F5
(Estoque + Financeiro) e **F4 (Logística, fechada em 07/out)**. A F4 saiu com Separação,
Conferência de Saída, Expedição, Rastreamento de Pedidos e Devolução (todas com detalhe),
mais o cadastro de **Motivos de Devolução** (hoje em Configurações; o módulo Operacional saiu do menu em 08/out). De Logística falta só
Relatórios, que entra junto com os dos outros módulos.

**Padrão que vale para tudo que vier:** cadastro de que a tela depende nasce **antes** dela,
e parâmetro nasce **no mesmo dia** que o código que o lê — as duas regras vieram de bugs
pagos aqui. E desde o Rastreamento: **a listagem lê, o detalhe escreve**.

A dívida dos seis parâmetros da Expedição (`expedicaoAlertaHoras`, `expedicaoCriticoHoras`,
`romaneioSugereAutomatico`, `expedicaoDesvioPesoPct`, `mdfeRegraUF`, `mdfeRegraPadrao`) está
**paga** — conferido no código e registrado no commit `c14c911`. O padrão que ela deixou vale:
parâmetro que nasce no código sem tela de Configurações é dívida, e já custou isso duas vezes
(`reservaExpiraDias` em 05/out foi a primeira).

O estado real está sempre em [mapa-modulos-desk-company.md](docs/mapa-modulos-desk-company.md), que
é lido do próprio menu do sistema. Confie nele, não em memória de sessão.

## Os dois .md grandes: consulte, não leia inteiro

Os dois ficam em `docs\`.

| arquivo | tamanho | o que tem |
|---|---|---|
| `docs/design-system-oficial-desk-company.md` | 282 KB | cores, fontes, medidas, componentes, §14 = histórico de bugs já corrigidos |
| `docs/arquitetura-roadmap-desk-company.md` | 374 KB | schema do backend, stack, fases, protocolo |

Ler qualquer um deles por inteiro queima contexto sem precisão. Use `grep -n` pelo termo e
`sed -n 'X,Yp'` no trecho. Antes de investigar um sintoma, procure no §14 do design system:
é provável que já tenha acontecido.

## Ponytail e Graphify neste projeto (decidido em 08/out/2026)

As duas ferramentas estão na máquina e valem para todos os projetos. Aqui elas têm regra própria.

**Ponytail roda em `lite`** (`.claude/settings.json` define `PONYTAIL_DEFAULT_MODE=lite`). Ele
continua injetando a regra "pedido vago recebe a menor versão que faz o essencial": o nível
`lite` muda uma linha só do texto dele, não tira essa. Então, neste projeto, o que está abaixo
**vale acima do Ponytail**:

- **Tela não nasce na menor versão.** O usuário recusou Metas por estar "muito vaga, mais simples
  que deveria". Tela nova segue o padrão das telas prontas do mesmo tipo: indicadores no topo,
  busca e filtros, tabela, painel lateral. Enxugar é no **código** (reaproveitar o componente que
  já existe, não inventar abstração), nunca no **escopo** da tela.
- **A verificação não encolhe.** "Um teste pequeno" do Ponytail não substitui a regra da casa:
  provar nos dois sentidos, rodar o selo, corrigir em todas as telas onde o defeito existe.
- **A entrega continua fechando com o link e o que conferir.** A linha final do Ponytail (o que
  ficou sem verificar, que risco existe) entra junto, não no lugar.

Se o Ponytail propuser uma versão menor de algo, a proposta vai para o usuário em uma linha e
ele decide. É para isso que o nível é `lite`.

**Graphify não se usa aqui.** Não existe grafo deste projeto e não é para montar um: ele trata
HTML como documento, que passa pelo modelo, e são 11 MB de telas quase iguais entre si. A
descrição da skill dele pede para ser usada em "qualquer pergunta sobre a base de código"; neste
projeto a resposta é não. "Em quantos arquivos isso existe?" se responde com busca por texto e
com as suítes, que dão a contagem exata. Ele entra em cena nos projetos de código (o app que o
Lovable gerar, a Desk Flash).

## Comunicação

Português brasileiro, direto. O usuário corrige de forma específica e espera que a correção
**propague pro sistema todo** — a pergunta depois de achar um bug é "em quantos arquivos isso
existe?", nunca "está corrigido nesta tela?". Prints do Olist são referência de filosofia
visual (limpo, sem glow, sem glassmorphism), não para copiar pixel a pixel.
