## 1. Setup Tailwind e assets

- [x] 1.1 Criar `package.json` com tailwindcss e script `build:css`
- [x] 1.2 Criar `tailwind.config.js` com tokens de `docs/DESIGN.md`
- [x] 1.3 Criar `static/css/src/buzz.css` com `@tailwind` directives e classes utilitárias (neumorfismo, vidro, ripple)
- [x] 1.4 Compilar CSS para `static/css/buzz.css`

## 2. Templates base

- [x] 2.1 Criar `templates/base.html` com blocks: title, extra_css, nav, sidebar, main, footer, menu, extra_js
- [x] 2.2 Criar `templates/partials/nav.html` (header mobile + desktop, baseado em buzz_dashboard e my_circles)
- [x] 2.3 Criar `templates/partials/menu.html` (bottom nav mobile com itens Início, Círculos, Configurações)
- [x] 2.4 Criar `templates/partials/sidebar.html` e `footer.html` (placeholders extensíveis)

## 3. Context processor e view de exemplo

- [x] 3.1 Criar context processor `rota_ativa` em `apps/core/context_processors.py`
- [x] 3.2 Registrar context processor em `apps/settings.py`
- [x] 3.3 Criar view e template `templates/dashboard/index.html` estendendo base.html
- [x] 3.4 Configurar URL no `apps/dashboard/urls.py`

## 4. Validação

- [x] 4.1 Verificar renderização do dashboard em `/` (ou rota definida)
- [x] 4.2 Validar nav ativa muda conforme rota
- [x] 4.3 Comparar visual com `docs/sos/buzz_dashboard/code.html`
