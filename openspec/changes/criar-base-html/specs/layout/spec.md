## ADDED Requirements

### Requirement: Partials de layout reutilizáveis
O sistema SHALL extrair nav, sidebar, footer e menu em partials Django incluídos via `{% include %}`.

#### Scenario: Estrutura de arquivos
- **WHEN** o layout é implementado
- **THEN** existem `templates/partials/nav.html`, `sidebar.html`, `footer.html` e `menu.html`
- **AND** `base.html` os inclui nos blocks correspondentes

#### Scenario: Navegação ativa por rota
- **WHEN** o usuário está em uma rota (ex.: dashboard, círculos, configurações)
- **THEN** o item de menu correspondente recebe estilo ativo (cor secondary + inset shadow)
- **AND** os demais itens ficam em estado inativo

### Requirement: CSS compilado com Tailwind
O sistema SHALL compilar CSS a partir de Tailwind com tokens do DESIGN.md, sem CDN em produção.

#### Scenario: Build de estilos
- **WHEN** o desenvolvedor executa o build de CSS
- **THEN** gera `static/css/buzz.css` com cores, fontes, sombras neumórficas e animações ripple
- **AND** `base.html` referencia o arquivo via `{% static %}`

### Requirement: Context processor de navegação
O sistema SHALL disponibilizar a rota ativa para os partials de menu.

#### Scenario: Item ativo no menu
- **WHEN** qualquer template estende `base.html`
- **THEN** a variável `rota_ativa` identifica a seção atual (inicio, circulos, configuracoes)
- **AND** os partials usam essa variável para aplicar classes ativas

## MODIFIED Requirements

### Requirement: Navegação responsiva
A navegação SHALL funcionar em mobile e desktop com layouts distintos extraídos dos HTMLs de referência.

#### Scenario: Mobile
- **WHEN** a viewport é menor que 768px
- **THEN** exibe header compacto (`nav`) e menu inferior fixo (`menu` em `partials/menu.html`)
- **AND** sidebar permanece oculta

#### Scenario: Desktop
- **WHEN** a viewport é maior ou igual a 768px
- **THEN** exibe nav horizontal com links no topo e oculta menu inferior
- **AND** conteúdo centralizado em container max-width 1280px (max-w-7xl)
