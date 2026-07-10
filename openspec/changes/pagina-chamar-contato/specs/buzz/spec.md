## ADDED Requirements

### Requirement: Página dedicada para chamar contato
O usuário SHALL acessar uma página dedicada ao clicar em um card de membro do círculo.

#### Scenario: Navegar pelo card
- **WHEN** o usuário clica em um card de contato em `/circulos/`
- **THEN** é redirecionado para `/circulos/<membro_id>/chamar/`
- **AND** vê o nome, avatar e status do contato

#### Scenario: Contato offline
- **WHEN** o membro está com status offline
- **THEN** a página exibe aviso de indisponibilidade
- **AND** o botão BUZZ permanece desabilitado

### Requirement: Interface de chamada com botão central
A página de chamar SHALL exibir layout estilo chamada sainte com botão BUZZ redondo central.

#### Scenario: Layout da página
- **WHEN** a página de chamar é carregada
- **THEN** exibe avatar com ripples animados, nome do contato e botão BUZZ circular
- **AND** oculta nav e menu inferior para foco na ação

#### Scenario: Disparar buzina
- **WHEN** o usuário pressiona o botão BUZZ em contato disponível
- **THEN** envia buzina via API existente
- **AND** exibe overlay de chamada sainte aguardando resposta

### Requirement: Mensagem curta opcional
O usuário SHALL poder escrever uma mensagem curta antes de buzinar.

#### Scenario: Campo de mensagem
- **WHEN** a página de chamar é exibida
- **THEN** há campo de texto com limite de 80 caracteres abaixo do botão BUZZ
- **AND** a mensagem é enviada junto com a buzina quando preenchida

### Requirement: Placeholders de personalização
A página SHALL exibir campos de som e vibração como placeholders desabilitados.

#### Scenario: Campos futuros
- **WHEN** a página de chamar é exibida
- **THEN** exibe seletores de tipo de som e vibração desabilitados com indicação "Em breve"
- **AND** não persiste nem aplica configuração nesta versão
