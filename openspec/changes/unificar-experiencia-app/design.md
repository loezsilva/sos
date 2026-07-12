## Contexto

O app autenticado usa Tailwind compilado e componentes Cutuca, mas cada template compõe sua própria hierarquia. O resultado preserva a função, porém dashboard, próximos, configurações e fluxos focados parecem produtos diferentes. IDs e `data-attributes` são contratos ativos com `static/js/buzz.js`, presença em tempo real, push e testes.

## Objetivos / Não-objetivos

**Objetivos:**
- Criar uma camada visual semântica compartilhada para shell, cabeçalhos, superfícies, ações e estados vazios.
- Dar ao dashboard uma hierarquia centrada na ação principal e no estado dos favoritos.
- Aplicar o mesmo vocabulário visual aos fluxos de próximos, conexão, chamada e configurações.
- Manter acessibilidade, áreas de toque de 48 px e `prefers-reduced-motion`.
- Preservar integralmente os contratos DOM e comportamentos existentes.

**Não-objetivos:**
- Alterar regras de negócio, modelos, views, endpoints, WebSockets ou push.
- Introduzir framework, biblioteca ou pipeline de frontend.
- Redesenhar landing e autenticação já atualizadas.
- Implementar funcionalidades ainda marcadas como “em breve”.

## Decisões

### 1. Camada CSS semântica isolada

Adicionar `static/css/app.css` carregado por `base.html`, com classes prefixadas por `app-`. A camada usa os tokens de `docs/DESIGN.md`, sem editar manualmente o CSS compilado do Tailwind.

**Por quê:** permite consistência e iteração sem depender de recompilar Tailwind nem afetar landing/auth. Alternativa descartada: repetir estilos em cada template, por aumentar divergência.

### 2. Shell claro, tátil e orientado a estado

Manter Nunito, laranja `#FF6600`, superfícies claras e roxo de apoio definidos no design system vigente. Navegação recebe seleção mais explícita, largura útil consistente e ações de status agrupadas.

**Por quê:** o design atual do produto e da landing já convergiu para esses tokens. As referências em `docs/sos/` orientam hierarquia e feedback tátil, não uma troca para o dark mode legado.

### 3. Assinatura visual: pulso funcional

O pulso fica concentrado no botão de cutucar e nos estados que exigem atenção. Cards comuns deixam de pulsar para reduzir ruído. Ripple, sombra elevada e estado pressionado continuam no fluxo principal.

**Por quê:** movimento comunica urgência quando associado à ação central; repetido em toda a interface perde significado.

### 4. Templates preservam contratos

IDs como `botao-buzz-inicio`, `ondas-chamada`, `contador-online`, `botao-push`, modais e todos os `data-*` permanecem. A refatoração altera estrutura visual e classes, não os pontos de integração.

### 5. Blocks Django

`base.html` continua expondo `title`, `extra_css`, `nav`, `sidebar`, `main`, `footer`, `menu` e `extra_js`. Páginas focadas, como chamar contato, podem sobrescrever shell e padding como já fazem.

## Riscos / Trade-offs

- [CSS novo conflitar com utilitários] → seletores `app-*` de baixa especificidade e escopo explícito.
- [Quebra de JS por mudança estrutural] → preservar IDs/atributos e validar os fluxos no navegador.
- [Refatoração ampla dificultar revisão] → organizar por shell compartilhado e depois por página.
- [Layout desktop comprometer mobile] → mobile-first, áreas de toque mínimas e verificação em 390 px e desktop.

## Plano de migração

1. Adicionar a camada CSS e atualizar o shell.
2. Refatorar dashboard, próximos e cards.
3. Refatorar configurações, conectar e chamar contato.
4. Validar navegação, modais, estados e responsividade.
5. Rollback por remoção do link de `app.css` e reversão dos templates, sem migração de dados.

## Questões em aberto

- Métricas de uso poderão orientar uma segunda rodada de refinamento após analytics.
