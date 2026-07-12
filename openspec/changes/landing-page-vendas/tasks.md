## 1. Roteamento e view

- [x] 1.1 Ajustar `PaginaInicioView` para servir `landing/index.html` a anônimos e `dashboard/index.html` a autenticados
- [x] 1.2 Garantir `body` com scroll na landing (`body_overflow` vazio) e sem nav/menu do app

## 2. Template e copy

- [x] 2.1 Criar `templates/landing/index.html` com header de marketing (logo, Entrar, Criar conta)
- [x] 2.2 Implementar hero (marca + headline + subtítulo + CTAs + visual) sem cards/nav do app
- [x] 2.3 Implementar seções: problema, solução, como funciona (3 passos), confiança, FAQ, CTA final
- [x] 2.4 Escrever copy PT-BR (PAS/AIDA) alinhada a Cutuca e personas (família/cuidadores/próximos)
- [x] 2.5 Linkar CTAs para `{% url 'cadastro' %}` e `{% url 'login' %}`; rodapé com termos de uso

## 3. Visual e motion

- [x] 3.1 Aplicar tokens Cutuca (`botao-cutuca`, cores, Nunito) e layout responsivo mobile-first
- [x] 3.2 Adicionar 2–3 motions leves (fade hero, press CTA, pulse opcional) com `prefers-reduced-motion`

## 4. Testes e verificação

- [x] 4.1 Teste: anônimo em `/` recebe landing (200) sem bottom nav
- [x] 4.2 Teste: autenticado em `/` recebe dashboard
- [x] 4.3 Checklist visual mobile + desktop (hero, CTAs, FAQ, scroll)
