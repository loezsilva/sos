## Por quê

A plataforma ainda usa a identidade visual antiga do **Buzz** (tema escuro, Hanken Grotesk, neomorfismo). O `docs/DESIGN.md` define a nova marca **Cutuca.online** — tema claro, laranja `#FF6600`, roxo de apoio, tipografia Nunito e componentes acessíveis para crianças e idosos. É o momento de alinhar a UI ao design system oficial.

## O que muda

- **BREAKING (visual):** troca do tema escuro pelo tema claro Cutuca (fundo `#F8F9FA`, surfaces brancas).
- Tokens de cor, tipografia, raio e espaçamento alinhados ao Design System Cutuca.
- Fonte **Nunito** no lugar de Hanken Grotesk / JetBrains Mono.
- Copy e branding de “Buzz/buzina” → **Cutuca/cutucão** nas telas, PWA (manifest, títulos) e textos de UI.
- Componentes visuais (botão principal, cards de contato, avatares, toasts, skeletons) alinhados às specs do DESIGN.md.
- Remoção/adaptação de estilos neomórficos escuros e glass dark que conflitam com o tema claro.
- **Não inclui** reescrever a stack (continua Django + Tailwind + templates); a seção de arquitetura do DESIGN.md (React Native etc.) fica fora do escopo desta change.

## Capacidades

### Novas capacidades

- `design-system-cutuca`: tokens CSS/Tailwind, tipografia Nunito, componentes base (botão, card, avatar, toast, skeleton) e tema claro.

### Capacidades modificadas

- `layout`: base HTML, nav, menu e superfícies passam a usar tokens Cutuca (tema claro, tipografia, branding).
- `buzz`: terminologia e feedback visual da chamada/alerta alinhados à marca Cutuca (cutucão), sem mudar a lógica de negócio.

## Impacto

- `static/css/src/buzz.css` (+ CSS compilado), config Tailwind / tokens.
- `templates/**` (base, dashboard, partials, auth).
- `static/manifest.webmanifest`, ícones/theme-color, títulos.
- Textos de UI em templates e JS (labels “Buzz” → “Cutuca” onde for marca).
- App Capacitor (`appName`, splash/theme) de forma mínima para não divergir da marca.
- Sem mudança de modelos, APIs ou fluxos de push/WebSocket.
