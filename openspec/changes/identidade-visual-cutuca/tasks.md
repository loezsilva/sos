## 1. Tokens e tipografia

- [x] 1.1 Atualizar `tailwind.config.js` com cores Cutuca (primary `#FF6600`, secondary `#8E24AA`, background `#F8F9FA`, surface `#FFFFFF`) e textos `on-*` com contraste adequado
- [x] 1.2 Trocar `fontFamily` para Nunito; ajustar radii (12px) se necessário
- [x] 1.3 Rebuild do CSS (`static/css/buzz.css`) a partir de `static/css/src/buzz.css`
- [x] 1.4 Remover/adaptar `.sombra-neumorfica`, `.efeito-vidro` e utilitários dark para elevação clara Cutuca

## 2. Base e branding

- [x] 2.1 Em `templates/base.html`: remover `class="dark"`, carregar Nunito, atualizar `theme-color` e títulos padrão para Cutuca
- [x] 2.2 Atualizar `static/manifest.webmanifest` (name, short_name, theme/background)
- [x] 2.3 Atualizar `mobile/capacitor.config.json` `appName` para Cutuca (mínimo)

## 3. Componentes CSS

- [x] 3.1 Criar/adaptar `.botao-cutuca` (primary, min 48×48, pressed scale 0.95); migrar botão principal da home
- [x] 3.2 Criar/adaptar `.card-cutuca` e aplicar em cards de círculo/contato
- [x] 3.3 Adaptar avatar e indicadores de status para tema claro
- [x] 3.4 Adaptar toast e, se couber, skeleton de lista

## 4. Templates e partials

- [x] 4.1 Atualizar nav, menu inferior e footer para tokens claros
- [x] 4.2 Atualizar alerta de cutucão recebido e chamada sainte (superfície clara, contraste)
- [x] 4.3 Atualizar páginas: index, círculos, chamar contato, configurações
- [x] 4.4 Atualizar templates de auth (login/registro) se herdarem o tema antigo

## 5. Copy de marca

- [x] 5.1 Substituir textos visíveis “Buzz”/“Buzina”/“buzinar” por “Cutuca”/“Cutucão”/“Cutucar” em templates
- [x] 5.2 Ajustar strings de UI em JS apenas onde forem exibidas ao usuário (toasts, labels)

## 6. Validação

- [x] 6.1 Checklist visual mobile + desktop (home, círculos, alerta, configs)
- [x] 6.2 Confirmar contraste de botões/textos e área mínima do botão principal
- [x] 6.3 Smoke: login, cutucar, receber alerta, toggle push — sem regressão funcional
