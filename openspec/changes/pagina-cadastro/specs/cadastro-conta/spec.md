## ADDED Requirements

### Requirement: Cadastro de conta
O visitante SHALL poder criar uma conta com nome, username, e-mail e senha.

#### Scenario: Cadastro válido
- **WHEN** o visitante envia o formulário com dados válidos e aceita os termos
- **THEN** a conta é criada
- **AND** o usuário fica autenticado
- **AND** é redirecionado para o início

#### Scenario: Username ou e-mail duplicado
- **WHEN** username ou e-mail já existem
- **THEN** o formulário exibe erro e a conta não é criada

#### Scenario: Termos não aceitos
- **WHEN** o visitante não marca o aceite dos termos
- **THEN** o cadastro é rejeitado

### Requirement: Navegação login e cadastro
As telas de entrar e cadastrar SHALL se referenciar mutuamente.

#### Scenario: Link no login
- **WHEN** o visitante está em `/contas/login/`
- **THEN** vê um link para criar conta
