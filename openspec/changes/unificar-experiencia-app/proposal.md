## Por quê

As páginas autenticadas cresceram por fluxo e hoje apresentam hierarquia, espaçamento, estados vazios e componentes inconsistentes entre si. Depois da evolução da landing e da autenticação, o produto precisa levar a mesma clareza e personalidade para a experiência principal sem alterar seus contratos funcionais.

## O que muda

- Unificar o shell autenticado, navegação, cabeçalhos de página e superfícies com a identidade Cutuca.
- Reorganizar o dashboard para deixar estado, destinatários e ação principal mais fáceis de entender.
- Padronizar próximos, perfil/chamada, notificações e configurações com componentes reutilizáveis.
- Melhorar estados vazios, mensagens de orientação, affordances, foco por teclado e áreas de toque.
- Preservar IDs, `data-attributes`, endpoints e comportamentos usados por JavaScript, WebSockets e testes.
- Garantir layout mobile-first e adaptação consistente para desktop.

## Capacidades

### Novas capacidades
- `experiencia-app`: experiência visual e de interação consistente para todas as páginas autenticadas.

### Capacidades modificadas
- `layout`: o shell e os componentes compartilhados passam a exigir hierarquia, responsividade e acessibilidade consistentes.

## Impacto

- Templates em `templates/dashboard/` e `templates/partials/`.
- Shell em `templates/base.html` e estilos compartilhados em `static/css/`.
- JavaScript existente permanece funcional por preservação dos contratos DOM.
- Sem alterações de API, banco de dados, WebSockets ou dependências.
