## ADDED Requirements

### Requirement: Experiência visual unificada
As páginas autenticadas SHALL compartilhar hierarquia, espaçamento, superfícies e padrões de ação consistentes com a identidade Cutuca.

#### Scenario: Navegação entre páginas
- **QUANDO** o usuário navega entre início, próximos e configurações
- **ENTÃO** cabeçalhos, cards, botões e estados usam o mesmo vocabulário visual
- **E** a página atual permanece claramente identificada

### Requirement: Dashboard orientado à ação
O dashboard SHALL priorizar a ação de cutucar e explicar claramente sua disponibilidade.

#### Scenario: Favoritos disponíveis
- **QUANDO** existe ao menos um favorito que pode receber um cutucão
- **ENTÃO** o botão principal aparece como ação dominante
- **E** a interface informa que é necessário segurar por dois segundos

#### Scenario: Ação indisponível
- **QUANDO** não há favoritos ou eles estão offline
- **ENTÃO** o botão permanece visualmente desabilitado
- **E** a interface orienta a próxima ação possível

### Requirement: Estados vazios acionáveis
Listas e painéis sem conteúdo SHALL explicar o estado e oferecer uma próxima ação quando aplicável.

#### Scenario: Lista de próximos vazia
- **QUANDO** o usuário ainda não possui pessoas conectadas
- **ENTÃO** a página explica como convidar alguém
- **E** oferece acesso às ações de convite por usuário ou QR

### Requirement: Contratos funcionais preservados
A refatoração visual MUST preservar os elementos usados por JavaScript, WebSockets, push e testes.

#### Scenario: Interação após refatoração
- **QUANDO** um fluxo existente é acionado
- **ENTÃO** IDs, `data-attributes`, formulários e endpoints continuam disponíveis
- **E** o comportamento anterior permanece funcional
