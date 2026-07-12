## Por quê

Visitantes anônimos caem direto no dashboard do app, sem proposta de valor nem CTA de cadastro. Sem uma landing de alta conversão, o Cutuca perde o funil de aquisição (descoberta → desejo → cadastro) e compete mal com apps de chat genéricos. Precisamos de uma página de vendas moderna, alinhada ao design system Cutuca, que converta tráfego em contas.

## O que muda

- Nova **landing page de vendas** pública (visitante não autenticado) com copy de alta conversão (PAS/AIDA)
- Visitante em `/` vê a landing; usuário autenticado continua no dashboard
- CTAs primários levam a **Criar conta** (`/contas/cadastro/`); secundários a **Entrar**
- Seções: hero, problema, solução/benefícios, como funciona, prova social (estrutura), FAQ e CTA final
- Layout próprio (sem menu do app / bottom nav), responsivo mobile-first
- **BREAKING** (comportamento de rota): `/` deixa de mostrar o dashboard vazio para anônimos e passa a servir a landing

## Capacidades

### Novas capacidades
- `landing-vendas`: página pública de marketing/vendas do Cutuca com seções de conversão e roteamento inteligente na raiz

### Capacidades modificadas
- _(nenhuma — o dashboard autenticado permanece; só muda o que anônimos veem em `/`)_

## Impacto

- `apps/core` ou `apps/dashboard`: view/rota da landing e lógica “anônimo → landing / autenticado → dashboard”
- Templates: novo `templates/landing/` (ou similar), possível `base_landing.html` sem shell do app
- CSS/tokens: `docs/DESIGN.md` e classes Cutuca existentes (`botao-cutuca`, `card-cutuca`, Nunito, laranja `#FF6600`)
- Links para `cadastro`, `login`, `core:termos_de_uso`
- SEO básico: title, meta description, OG quando possível
- Sem mudança de models, WebSockets ou APIs de buzina
