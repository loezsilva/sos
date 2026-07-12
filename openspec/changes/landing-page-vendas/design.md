## Contexto

Hoje `/` é `PaginaInicioView` (dashboard). Visitante anônimo vê o shell do app (nav/menu) com dashboard vazio — zero proposta de valor. Cadastro e login já existem em `/contas/cadastro/` e `/contas/login/`. Design system Cutuca: tema claro, primary `#FF6600`, Nunito, `botao-cutuca` / `card-cutuca` (`docs/DESIGN.md`).

## Objetivos / Não-objetivos

**Objetivos:**
- Landing pública de alta conversão (PAS/AIDA) na raiz para anônimos
- Autenticado em `/` continua no dashboard
- CTAs → cadastro (primário) e login (secundário)
- Visual Cutuca, mobile-first, sem bottom nav do app
- Copy em PT-BR focada em família/cuidadores/círculo íntimo (próximos)

**Não-objetivos:**
- Pricing/planos, checkout ou gate de pagamento
- CMS, A/B testing, analytics avançado (pode vir depois)
- Reescrever auth, PWA ou fluxos do app
- Depoimentos reais inventados — usar placeholders estruturados ou métricas honestas (“em tempo real”, “um toque”)

## Decisões

### 1. Rota: mesma `/`, view decide o template

`PaginaInicioView` (ou view em `core`) verifica `request.user.is_authenticated`:
- autenticado → `dashboard/index.html` (comportamento atual)
- anônimo → `landing/index.html`

**Por quê:** evita quebrar `dashboard:index` e bookmarks; zero redirect extra. Alternativa descartada: `/welcome/` + redirect — pior SEO e mais URLs.

### 2. Shell próprio da landing

Template estende `base.html` com `{% block nav %}{% endblock %}`, `{% block menu %}{% endblock %}` e header/footer de marketing inline (logo, Entrar, CTA Criar conta). Overflow scroll liberado (`body_overflow` vazio).

**Por quê:** o shell do app compete com a mensagem de vendas. Alternativa: `base_marketing.html` separado — mais DRY futuro, mas overkill no MVP; pode extrair depois.

### 3. Estrutura de seções (conversão)

Ordem fixa (uma job por seção; hero enxuto — ver regras de frontend):

1. **Hero** — marca Cutuca em destaque, 1 headline, 1 subtítulo, CTA group (Criar conta + Entrar), visual full-bleed (mock do botão cutucar / atmosfera) — sem cards no hero
2. **Problema** — chat demora / mensagem se perde / “preciso da sua atenção agora”
3. **Solução** — cutucão em um toque, presença, próximos opt-in
4. **Como funciona** — 3 passos (criar conta → convidar próximos → cutucar)
5. **Prova / confiança** — bullets de benefício + estrutura para depoimento (placeholder até ter reais)
6. **FAQ** — 5 objeções (é spam? gratuito? iPhone? privacidade? vs WhatsApp)
7. **CTA final** — repetir Criar conta

Copy framework: PAS no problema/solução; AIDA no fluxo da página. CTAs com verbos de ação (“Criar conta grátis”, “Começar agora”).

### 4. Motion

2–3 animações leves (respeitando `prefers-reduced-motion`): fade-in do hero, hover/press no CTA (`botao-cutuca`), opcional pulse suave no mock do botão cutucar. Sem glow/purple AI defaults.

### 5. Tokens e assets

Reusar CSS estático existente; sem novo framework. Logo `static/icons/logo-cutuca-online.png`. Screenshots do produto se houver em `static/icons/screenshot-*.png`; senão composição CSS do botão cutucar.

## Riscos / Trade-offs

- [Copy genérica] → Mitigação: personas concretas (filho cuidando da mãe; casal; amigo que não atende)
- [Dashboard anônimo some] → Mitigação: autenticados intactos; Entrar no header da landing
- [Hero poluído] → Mitigação: orçamento estrito do first viewport (marca + headline + subtítulo + CTAs + 1 visual)
- [Depoimentos falsos] → Mitigação: não inventar nomes; usar “Em breve histórias reais” ou só benefícios factuais

## Plano de migração

1. Template + ajuste da view
2. Testes: anônimo vê landing; autenticado vê dashboard; CTAs resolvem URLs
3. Deploy sem migration de banco
4. Rollback: reverter template da branch anônima na view

## Questões em aberto

- Pricing na landing: fora do MVP (não-objetivo)
- URL canônica `/` vs `/inicio` do app: manter `/` dual conforme decisão 1
