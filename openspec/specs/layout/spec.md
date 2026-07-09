## Purpose

Definir a estrutura de templates Django e componentes visuais do design system Tactile Pulse para o Buzz.

## Requirements

### Requirement: base.html modular
O projeto SHALL ter um template base dividido em blocks Django reutilizáveis.

#### Scenario: Blocks obrigatórios
- **WHEN** o `base.html` é criado
- **THEN** define os blocks: `title`, `extra_css`, `nav`, `sidebar`, `main`, `footer`, `menu`, `extra_js`
- **AND** aplica dark mode com fundo `#0b1326` e fontes Hanken Grotesk + JetBrains Mono

#### Scenario: Referência visual
- **WHEN** um block é implementado
- **THEN** segue a estrutura visual dos HTMLs em `docs/sos/`
- **AND** usa tokens de cor/espaçamento de `docs/DESIGN.md`

### Requirement: Navegação responsiva
A navegação SHALL funcionar em mobile e desktop.

#### Scenario: Mobile
- **WHEN** a viewport é menor que 768px
- **THEN** sidebar colapsa e menu inferior (`footer`/`menu`) fica acessível

#### Scenario: Desktop
- **WHEN** a viewport é maior ou igual a 768px
- **THEN** sidebar fica visível com grid de 12 colunas (max-width 1280px)

### Requirement: Componentes táteis
Botões e cards SHALL seguir o design system Tactile Pulse.

#### Scenario: Botão primário Buzz
- **WHEN** renderizado
- **THEN** é pill-shaped ou circular com animação ripple
- **AND** usa sombras neumórficas (raised) e inset no estado pressionado

#### Scenario: Cards glassmorphism
- **WHEN** usados em modais ou alertas
- **THEN** aplicam `backdrop-filter: blur(20px)` e borda branca 10% opacidade
