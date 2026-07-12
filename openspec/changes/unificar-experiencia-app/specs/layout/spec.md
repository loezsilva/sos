## MODIFIED Requirements

### Requirement: base.html modular
O projeto SHALL ter um template base dividido em blocks Django reutilizáveis e uma camada visual compartilhada.

#### Scenario: Blocks obrigatórios
- **QUANDO** o `base.html` é renderizado
- **ENTÃO** define os blocks: `title`, `extra_css`, `nav`, `sidebar`, `main`, `footer`, `menu`, `extra_js`
- **E** carrega os estilos compartilhados do app

#### Scenario: Referência visual
- **QUANDO** um block é implementado
- **ENTÃO** segue a hierarquia funcional dos HTMLs em `docs/sos/`
- **E** usa os tokens atuais de cor, tipografia e espaçamento de `docs/DESIGN.md`

### Requirement: Navegação responsiva
A navegação SHALL funcionar em mobile e desktop e identificar claramente a rota atual.

#### Scenario: Mobile
- **QUANDO** a viewport é menor que 768px
- **ENTÃO** o cabeçalho compacto e o menu inferior permanecem acessíveis
- **E** os alvos de toque têm no mínimo 48 por 48 pixels

#### Scenario: Desktop
- **QUANDO** a viewport é maior ou igual a 768px
- **ENTÃO** a navegação superior fica visível dentro de uma largura máxima consistente
- **E** status, notificações e rota ativa permanecem distinguíveis

### Requirement: Componentes táteis
Botões e cards SHALL seguir o design system Cutuca e usar movimento com significado funcional.

#### Scenario: Botão primário Cutuca
- **QUANDO** o botão principal é renderizado
- **ENTÃO** é pill-shaped ou circular com feedback pressionado
- **E** usa ripple apenas quando comunica uma ação ou alerta ativo

#### Scenario: Superfícies compartilhadas
- **QUANDO** cards, modais ou alertas são renderizados
- **ENTÃO** usam borda, raio, sombra e contraste consistentes
- **E** respeitam `prefers-reduced-motion` e foco visível
