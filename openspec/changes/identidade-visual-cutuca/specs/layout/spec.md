## MODIFIED Requirements

### Requirement: base.html modular
O projeto SHALL ter um template base dividido em blocks Django reutilizáveis.

#### Scenario: Blocks obrigatórios
- **WHEN** o `base.html` é criado
- **THEN** define os blocks: `title`, `extra_css`, `nav`, `sidebar`, `main`, `footer`, `menu`, `extra_js`
- **AND** aplica tema claro Cutuca com fundo `#F8F9FA` e fonte Nunito

#### Scenario: Referência visual
- **WHEN** um block é implementado
- **THEN** segue o Design System Cutuca em `docs/DESIGN.md`
- **AND** usa tokens de cor/espaçamento/tipografia definidos nesse documento

### Requirement: Navegação responsiva
A navegação SHALL funcionar em mobile e desktop.

#### Scenario: Mobile
- **WHEN** a viewport é menor que 768px
- **THEN** sidebar colapsa e menu inferior (`footer`/`menu`) fica acessível

#### Scenario: Desktop
- **WHEN** a viewport é maior ou igual a 768px
- **THEN** sidebar fica visível com grid de 12 colunas (max-width 1280px)

### Requirement: Componentes táteis
Botões e cards SHALL seguir o design system Cutuca (acessível, tema claro).

#### Scenario: Botão primário Cutuca
- **WHEN** renderizado
- **THEN** usa primary `#FF6600`, área mínima 48×48px
- **AND** no estado pressionado aplica scale ≈ 0.95

#### Scenario: Cards de superfície
- **WHEN** usados em listas, modais ou alertas
- **THEN** usam fundo surface `#FFFFFF`, raio ~12px e sombra suave clara
- **AND** não dependem de glassmorphism escuro nem neomorfismo dark
