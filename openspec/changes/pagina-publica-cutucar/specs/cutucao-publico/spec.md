## ADDED Requirements

### Requirement: Canal público compartilhável
O sistema SHALL permitir que cada usuário disponibilize um canal público revogável para receber cutucões.

#### Scenario: Criar link público
- **WHEN** um usuário autenticado acessa a área de compartilhamento pela primeira vez
- **THEN** o sistema cria uma chave pública aleatória e não previsível
- **AND** exibe uma URL que pode ser copiada e compartilhada

#### Scenario: Desativar link público
- **WHEN** o proprietário desativa seu canal público
- **THEN** novos acessos à URL retornam página não encontrada
- **AND** nenhum cutucão pode ser enviado pelo canal

#### Scenario: Regenerar link público
- **WHEN** o proprietário solicita uma nova chave
- **THEN** o sistema invalida imediatamente a URL anterior
- **AND** disponibiliza uma nova URL e um novo QR Code

### Requirement: Página pública de cutucão
O sistema SHALL exibir uma página pública focada em cutucar o proprietário do link.

#### Scenario: Visitante anônimo abre link válido
- **WHEN** uma pessoa não autenticada acessa uma URL pública ativa
- **THEN** vê a identificação pública do proprietário
- **AND** vê um campo obrigatório de nickname e o botão de cutucar
- **AND** não vê navegação, presença ou dados privados do proprietário

#### Scenario: Visitante autenticado abre link válido
- **WHEN** um usuário autenticado acessa uma URL pública ativa
- **THEN** vê diretamente o botão de cutucar
- **AND** o campo de nickname não é exibido
- **AND** sua conta será usada como identidade do envio

#### Scenario: Link inválido ou inativo
- **WHEN** alguém acessa uma chave inexistente, antiga ou desativada
- **THEN** o sistema retorna página não encontrada
- **AND** não revela se existe um usuário associado

### Requirement: Identificação do visitante
O sistema SHALL identificar a origem pública sem criar contas artificiais.

#### Scenario: Nickname anônimo válido
- **WHEN** um visitante anônimo informa um nickname entre 2 e 40 caracteres
- **THEN** o sistema normaliza espaços e usa esse nickname no alerta
- **AND** pode manter o nickname na sessão do navegador

#### Scenario: Nickname anônimo inválido
- **WHEN** o nickname está vazio, fora do limite ou contém caracteres de controle
- **THEN** o sistema não cria o cutucão
- **AND** exibe uma mensagem de correção junto ao campo

#### Scenario: Tentativa de sobrescrever identidade autenticada
- **WHEN** um usuário autenticado envia manualmente um nickname no POST
- **THEN** o sistema ignora o valor informado
- **AND** identifica o cutucão pelo nome ou username da conta

### Requirement: Envio de cutucão público
O sistema SHALL registrar e tentar entregar um cutucão público ao proprietário do canal.

#### Scenario: Envio anônimo aceito
- **WHEN** um visitante anônimo válido segura o botão pelo tempo solicitado
- **THEN** o sistema registra um evento público com destinatário e nickname
- **AND** envia alerta WebSocket e push ao proprietário
- **AND** autoriza o visitante a acompanhar a chamada na sessão do navegador
- **AND** mostra o estado de chamada aguardando resposta

#### Scenario: Envio autenticado aceito
- **WHEN** um usuário autenticado aciona o botão público
- **THEN** o sistema registra a conta como origem do evento
- **AND** envia alerta WebSocket e push ao proprietário
- **AND** mostra o estado de chamada aguardando resposta

#### Scenario: Uso do próprio link
- **WHEN** o proprietário autenticado tenta cutucar pelo próprio canal
- **THEN** o sistema não cria o evento
- **AND** orienta que aquele é seu próprio link

#### Scenario: Proprietário sem conexão em tempo real
- **WHEN** o proprietário não possui WebSocket ativo
- **THEN** o evento permanece registrado
- **AND** o sistema tenta entregar por push sem revelar presença ao visitante

### Requirement: Acompanhamento e cancelamento público
O sistema SHALL permitir que o visitante autorizado acompanhe e cancele um cutucão público pendente.

#### Scenario: Cancelar enquanto pendente
- **WHEN** o visitante autorizado cancela a chamada ainda pendente
- **THEN** o evento muda para cancelado
- **AND** o overlay do destinatário é encerrado
- **AND** o visitante vê confirmação de cancelamento

#### Scenario: Timeout sem resposta
- **WHEN** o tempo máximo de espera termina sem resposta
- **THEN** o evento muda para perdido
- **AND** o visitante vê indicação de sem resposta
- **AND** o overlay do destinatário é encerrado

#### Scenario: Acesso sem autorização
- **WHEN** alguém consulta ou cancela um cutucão sem sessão válida nem autoria autenticada
- **THEN** o sistema retorna não encontrado
- **AND** não revela detalhes do evento

### Requirement: Respostas rápidas ao cutucão público
O sistema SHALL aceitar as mesmas respostas rápidas do fluxo autenticado para cutucões públicos.

#### Scenario: Destinatário responde com resposta rápida
- **WHEN** o proprietário escolhe “Já vou”, “Tô ocupado” ou “Ligo em 5 min”
- **THEN** o visitante autorizado vê o rótulo correspondente
- **AND** a chamada pública deixa de estar pendente

#### Scenario: Destinatário recusa
- **WHEN** o proprietário recusa o cutucão público
- **THEN** o visitante autorizado vê a recusa
- **AND** a chamada pública deixa de estar pendente

### Requirement: Proteção contra abuso
O sistema MUST limitar envios públicos por origem e canal.

#### Scenario: Limite excedido
- **WHEN** uma origem excede o limite configurado de envios para o mesmo canal
- **THEN** o sistema rejeita temporariamente novos eventos
- **AND** informa quando o visitante poderá tentar novamente

#### Scenario: Toques repetidos no cooldown
- **WHEN** o visitante tenta reenviar durante o cooldown
- **THEN** o sistema não cria eventos duplicados
- **AND** mantém feedback de envio anterior

#### Scenario: Requisição sem CSRF
- **WHEN** um POST público é enviado sem token CSRF válido
- **THEN** o sistema rejeita a requisição

### Requirement: QR Code público
O sistema SHALL gerar um QR Code que aponta para o canal público ativo.

#### Scenario: Ler QR público
- **WHEN** uma pessoa escaneia o QR Code público
- **THEN** o navegador abre a página pública do proprietário
- **AND** aplica o fluxo anônimo ou autenticado correspondente

#### Scenario: Diferenciar QR público e QR de conexão
- **WHEN** o proprietário acessa as opções de compartilhamento
- **THEN** o sistema identifica claramente o QR para “Cutucar” e o QR para “Conectar”
- **AND** preserva o fluxo existente de convite de conexão

### Requirement: Gestão de atividades públicas
O sistema SHALL mostrar os cutucões públicos ao proprietário em sua central de atividades.

#### Scenario: Atividade de visitante anônimo
- **WHEN** um cutucão público anônimo é registrado
- **THEN** a central mostra o nickname e a indicação “pelo link público”
- **AND** não oferece navegação para um perfil inexistente

#### Scenario: Atividade de usuário autenticado
- **WHEN** um cutucão público autenticado é registrado
- **THEN** a central mostra a identidade da conta e a origem pública
