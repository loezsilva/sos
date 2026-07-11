## MODIFIED Requirements

### Requirement: Dashboard com botão de atenção
O usuário SHALL conseguir chamar a atenção do contato principal com um único toque em botão central de destaque.

#### Scenario: Buzinar contato principal
- **WHEN** o usuário pressiona o botão central no dashboard
- **THEN** uma notificação de alta prioridade é enviada ao contato principal em menos de 2 segundos
- **AND** o botão exibe feedback visual Cutuca (scale ≈ 0.95 / estado pressed do design system)

#### Scenario: Selecionar outro contato
- **WHEN** o usuário escolhe um contato diferente no seletor rápido
- **THEN** o botão central passa a direcionar a buzina para o contato selecionado

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira.

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina
- **THEN** a tela de alerta ocupa 100% da viewport com som e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida
- **AND** o alerta usa superfície clara Cutuca (legível em tema claro)

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente recebe a resposta em tempo real
- **AND** a tela de alerta é encerrada

### Requirement: Layout base com blocks Django
Todas as telas SHALL herdar de um `base.html` modular.

#### Scenario: Estrutura de template
- **WHEN** uma nova tela é criada
- **THEN** estende `base.html` preenchendo blocks: `nav`, `sidebar`, `main`, `footer`, `menu`
- **AND** segue tokens e componentes do Design System Cutuca em `docs/DESIGN.md`
