## Contexto

O front atual é **tema escuro Tactile Pulse** (`tailwind.config.js` + `static/css/src/buzz.css` + templates Django). O `docs/DESIGN.md` redefine a marca como **Cutuca.online**: tema claro, primary `#FF6600`, secondary `#8E24AA`, Nunito, componentes grandes e acessíveis.

A stack permanece Django + Tailwind + templates. A parte de arquitetura do DESIGN.md (React Native, NestJS etc.) **não** entra nesta change.

## Objetivos / Não-objetivos

**Objetivos:**
- Mapear tokens Cutuca no Tailwind e CSS.
- Migrar todas as telas autenticadas e auth para tema claro.
- Trocar tipografia para Nunito; theme-color / PWA / títulos para Cutuca.
- Adaptar botão principal, cards, avatares, toasts e skeletons ao design system.
- Atualizar copy de marca (Buzz → Cutuca; buzina → cutucão) na UI.

**Não-objetivos:**
- Renomear modelos/APIs/JS internos (`Buzina`, `buzz.js`, URLs `/api/buzina/`).
- Reescrever em React/Vue/RN.
- Redesign de fluxos (presença, push, não perturbe).
- Ícones de loja/App Store finais (pode usar placeholder atualizado).

## Decisões

### 1. Tokens no Tailwind (fonte da verdade)

Atualizar `tailwind.config.js`:
- `primary` → `#FF6600` / hover `#E65C00`
- `secondary` → `#8E24AA`
- `background` → `#F8F9FA`
- `surface` → `#FFFFFF`
- textos `on-*` recalculados para contraste AA em tema claro
- `fontFamily` → Nunito
- `borderRadius.xl` alinhado a `--radius-md` (12px)

**Por quê:** o projeto já consome tokens via classes Tailwind; trocar na config propaga com rebuild do CSS.

### 2. Remover `class="dark"` do `html`

Tema claro é o padrão. Manter `darkMode: 'class'` no Tailwind, mas sem aplicar `dark` no `base.html`.

### 3. Componentes via classes CSS (não React)

DESIGN.md descreve `<CutucaButton>` etc. No Django, mapear para classes utilitárias / `@layer components`:
- `.botao-cutuca` (primary, pressed scale 0.95, min 48×48)
- `.card-cutuca` (surface, sombra leve, radius 12)
- `.avatar-cutuca`, `.toast-cutuca`, `.skeleton-cutuca`

**Por quê:** zero nova dependência; reaproveita templates.

### 4. Branding gradual

| Camada | Ação |
|--------|------|
| UI visível | “Cutuca”, “Cutucar”, “Cutucão” |
| Código interno | Mantém `Buzina` / `buzz.js` |
| PWA / Capacitor | `name`/`appName` → Cutuca |

### 5. Sombras

Substituir neomorfismo escuro por elevação suave clara (`0 2px 8px rgba(0,0,0,.08)`). Glass dark → surface branca com borda sutil.

### 6. HTMLs de inspiração

`docs/sos/*/code.html` ficam como referência histórica; a fonte normativa passa a ser `docs/DESIGN.md` (seção UI Design System).

## Riscos / Trade-offs

| Risco | Mitigação |
|-------|-----------|
| Contraste insuficiente em tokens derivados | Validar texto/ícones em fundo claro; ajustar `on-surface` |
| Classes hardcoded com cores antigas | Grep por `#0b1326`, `efeito-vidro`, `sombra-neumorfica` |
| Usuários acostumados ao dark | Aceito — rebrand intencional |
| Nome de arquivo `buzz.css` | Manter path por agora; opcional renomear depois |

## Plano de migração

1. Atualizar tokens + rebuild CSS.
2. `base.html` (fonte, theme-color, remover dark).
3. Partials (nav, menu, alerta, chamada).
4. Páginas dashboard + auth.
5. Manifest / PWA / Capacitor appName.
6. Passada de copy de marca.
7. Checklist visual mobile/desktop.

Rollback: reverter commit de tokens + templates.

## Questões em aberto

- Domínio/URL pública `cutuca.online` vs ambiente atual — fora do escopo de UI.
- Pacote de ícones maskable novos — usar recolor do ícone atual se arte final não existir.
