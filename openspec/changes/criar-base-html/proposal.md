## Por quê

O projeto Buzz não possui estrutura de templates Django. Sem um `base.html` modular, cada tela reimplementaria nav, sidebar, footer e tokens visuais — gerando inconsistência e retrabalho. Esta é a fundação visual necessária antes de implementar dashboard, círculos e configurações.

## O que muda

- Criação de `templates/base.html` com blocks Django reutilizáveis
- Criação de partials: `nav`, `sidebar`, `footer`, `menu`
- CSS estático com tokens do design system Tactile Pulse (neumorfismo, glassmorphism, ripple)
- Configuração Tailwind compilado (substituindo CDN dos HTMLs de referência)
- Template de exemplo `dashboard/index.html` estendendo o base

## Capacidades

### Novas capacidades

_Nenhuma — a capacidade `layout` já existe em `openspec/specs/layout/`._

### Capacidades modificadas

- `layout`: adiciona requisitos concretos de partials, arquivos estáticos e navegação ativa por rota

## Impacto

- `templates/` — novo diretório com base e partials
- `static/css/` e `static/js/` — estilos e scripts do design system
- `package.json` + `tailwind.config.js` — build de CSS (nova dependência de dev)
- `apps/settings.py` — possível ajuste em `STATICFILES_DIRS` (já configurado)
- `apps/dashboard/` — primeira view/template consumindo o base
- Sem impacto em APIs, models ou WebSockets nesta mudança
