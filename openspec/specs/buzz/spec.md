## Purpose

Definir o comportamento core do Buzz — sistema de atenção imediata para círculos íntimos com comunicação de ultra-baixa latência.

## Requirements

### Requirement: Dashboard com botão de atenção
O usuário SHALL conseguir chamar a atenção do contato principal com um único toque em botão central de destaque.

#### Scenario: Buzinar contato principal
- **WHEN** o usuário pressiona o botão central no dashboard
- **THEN** uma notificação de alta prioridade é enviada ao contato principal em menos de 2 segundos
- **AND** o botão exibe feedback visual (ripple/neumorfismo pressionado)

#### Scenario: Selecionar outro contato
- **WHEN** o usuário escolhe um contato diferente no seletor rápido
- **THEN** o botão central passa a direcionar a buzina para o contato selecionado

### Requirement: Tela de chamada recebida
O destinatário SHALL receber uma interface de alta prioridade que ocupa a tela inteira.

#### Scenario: Receber buzina
- **WHEN** o usuário recebe uma buzina
- **THEN** a tela de alerta ocupa 100% da viewport com som e vibração
- **AND** exibe o nome/foto do remetente e ações de resposta rápida

#### Scenario: Resposta rápida
- **WHEN** o destinatário toca em "Já vou", "Tô ocupado" ou "Ligo em 5 min"
- **THEN** o remetente recebe a resposta em tempo real
- **AND** a tela de alerta é encerrada

### Requirement: Gerenciamento de círculo
O usuário SHALL visualizar e gerenciar pessoas do seu círculo íntimo.

#### Scenario: Listar contatos
- **WHEN** o usuário acessa a tela de círculos
- **THEN** vê lista de contatos com status (online, ocupado, offline)
- **AND** pode adicionar ou remover membros do círculo

### Requirement: Personalização
O usuário SHALL personalizar sons, temas e mensagens rápidas.

#### Scenario: Configurar som por contato
- **WHEN** o usuário define um som específico para um contato
- **THEN** buzinas desse contato usam o som configurado

### Requirement: Modo não perturbe inteligente
O usuário SHALL bloquear buzinas exceto de contatos VIP em horários definidos.

#### Scenario: VIP em horário de silêncio
- **WHEN** o modo não perturbe está ativo e um contato não-VIP buzina
- **THEN** a buzina é silenciada e registrada no histórico
- **AND** contatos VIP ainda conseguem buzinar normalmente

### Requirement: Histórico de chamados
O usuário SHALL consultar quem buzinou e quando.

#### Scenario: Ver histórico
- **WHEN** o usuário acessa o histórico
- **THEN** vê lista cronológica de buzinas recebidas e enviadas com timestamp e status

### Requirement: Layout base com blocks Django
Todas as telas SHALL herdar de um `base.html` modular.

#### Scenario: Estrutura de template
- **WHEN** uma nova tela é criada
- **THEN** estende `base.html` preenchendo blocks: `nav`, `sidebar`, `main`, `footer`, `menu`
- **AND** segue tokens visuais de `docs/DESIGN.md` e referência de `docs/sos/`
