## Contexto

O projeto Django já possui `TEMPLATES['DIRS'] = ['templates']` e `STATICFILES_DIRS` configurados, mas nenhum template ou CSS existe. Os HTMLs em `docs/sos/` usam Tailwind via CDN com tokens inline — precisamos converter para assets estáticos versionáveis.

Referências visuais:
- `buzz_dashboard/code.html` — header fixo, bottom nav mobile, glow ambiente
- `my_circles/code.html` — nav desktop horizontal, bottom nav mobile com item ativo

## Objetivos / Não-objetivos

**Objetivos:**
- `base.html` modular com blocks Django
- Partials reutilizáveis para nav, sidebar, footer, menu
- CSS compilado com tokens Tactile Pulse
- Template de exemplo no dashboard validando o layout

**Não-objetivos:**
- Implementar lógica de buzina ou WebSockets
- Telas completas de círculos, alerta ou configurações
- Sidebar desktop com conteúdo (fica como block vazio/extensível)
- Internacionalização (i18n) — textos fixos em PT-BR por ora

## Decisões

### 1. Estrutura de templates

```
templates/
├── base.html
├── partials/
│   ├── nav.html      # header (mobile + desktop)
│   ├── sidebar.html  # reservado para desktop futuro
│   ├── footer.html   # rodapé opcional
│   └── menu.html     # bottom nav mobile
└── dashboard/
    └── index.html    # prova de conceito
```

**Por quê:** Separação por partials permite override de blocks sem duplicar markup. Sidebar fica como placeholder — os HTMLs de referência usam nav horizontal no desktop, não sidebar lateral.

### 2. Tailwind compilado (não CDN)

- `package.json` com `tailwindcss` como devDependency
- `tailwind.config.js` com tokens extraídos de `docs/DESIGN.md`
- `static/css/src/buzz.css` → compilado para `static/css/buzz.css`

**Alternativa rejeitada:** Manter CDN — inviável em produção (performance, CSP, offline).

### 3. Blocks Django

| Block | Conteúdo |
|-------|----------|
| `title` | Título da página |
| `extra_css` | CSS adicional por página |
| `nav` | Override do header (default: partial) |
| `sidebar` | Conteúdo lateral desktop (vazio por padrão) |
| `main` | Conteúdo principal |
| `footer` | Rodapé |
| `menu` | Override do bottom nav (default: partial) |
| `extra_js` | Scripts por página |

### 4. Navegação ativa

Context processor em `apps.core` expondo `rota_ativa` baseado em `request.resolver_match.url_name`.

**Por quê:** Evita lógica de menu em cada view — partials decidem o estilo ativo.

### 5. Animações CSS

Classes utilitárias em `buzz.css`:
- `.sombra-neumorfica` / `.sombra-neumorfica-inset`
- `.efeito-vidro` (glassmorphism)
- `.animacao-ripple` (botão buzz — para uso futuro no dashboard)

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Build CSS extra no deploy | Script `npm run build:css` documentado; CSS compilado commitado ou gerado no CI |
| Tailwind purge remove classes dinâmicas | `content` no config aponta para `templates/**/*.html` |
| Sidebar sem uso imediato | Block vazio — não adiciona complexidade, prepara telas futuras |

## Plano de migração

1. Criar estrutura de templates e static
2. Configurar Tailwind + build
3. Implementar base e partials
4. Criar view/template dashboard de exemplo
5. Validar visualmente contra HTMLs de referência

Rollback: remover templates/ e static/css/ — sem impacto em dados.

## Questões em aberto

- Commitar `buzz.css` compilado ou gerar no deploy? → **Decisão:** commitar para simplicidade no Heroku
- Logo Buzz: usar placeholder ou asset estático? → **Decisão:** ícone Material Symbols por ora
