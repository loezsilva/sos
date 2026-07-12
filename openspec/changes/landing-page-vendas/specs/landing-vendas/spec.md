## ADDED Requirements

### Requirement: Landing para visitantes anônimos
O sistema SHALL exibir uma landing page de vendas em `/` quando o visitante não estiver autenticado.

#### Scenario: Visitante anônimo na raiz
- **WHEN** um visitante não autenticado acessa `/`
- **THEN** a landing de vendas é renderizada
- **AND** o menu inferior do app não é exibido

#### Scenario: Usuário autenticado na raiz
- **WHEN** um usuário autenticado acessa `/`
- **THEN** o dashboard do app é renderizado (comportamento atual)

### Requirement: Conversão para cadastro
A landing SHALL oferecer CTAs claros que levam ao cadastro e ao login.

#### Scenario: CTA primário
- **WHEN** o visitante aciona o CTA principal (ex.: “Criar conta”)
- **THEN** é direcionado para `/contas/cadastro/`

#### Scenario: CTA secundário
- **WHEN** o visitante aciona o CTA de entrar
- **THEN** é direcionado para `/contas/login/`

### Requirement: Seções de alta conversão
A landing SHALL apresentar, em ordem, seções de hero, problema, solução, como funciona, confiança/FAQ e CTA final, com copy em português do Brasil alinhada à marca Cutuca.

#### Scenario: Conteúdo mínimo do hero
- **WHEN** o visitante carrega a landing
- **THEN** o primeiro viewport exibe a marca Cutuca, uma headline, um subtítulo curto e o grupo de CTAs
- **AND** não exibe o shell de navegação do app (bottom nav)

#### Scenario: FAQ responde objeções
- **WHEN** o visitante rola até o FAQ
- **THEN** vê respostas a dúvidas comuns (privacidade, diferença de chat, dispositivos, convite opt-in)

### Requirement: Identidade visual Cutuca
A landing SHALL usar tokens e componentes do design system Cutuca (tema claro, primary laranja, Nunito, botões acessíveis).

#### Scenario: Consistência visual
- **WHEN** a landing é exibida em mobile ou desktop
- **THEN** tipografia, cores e CTAs seguem `docs/DESIGN.md` e classes Cutuca existentes
