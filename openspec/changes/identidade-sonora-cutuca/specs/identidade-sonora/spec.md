## ADDED Requirements

### Requirement: Assinatura sonora oficial
O sistema SHALL usar uma assinatura sonora original e reconhecível como identidade auditiva do Cutuca.

#### Scenario: Alerta recebido
- **WHEN** o destinatário recebe um cutucão autenticado ou público
- **THEN** toca a assinatura recebida em loop até resposta, cancelamento ou timeout
- **AND** vibra conforme o canal disponível

#### Scenario: Chamada enviada
- **WHEN** o remetente entra no estado de espera
- **THEN** toca o padrão de espera derivado da mesma assinatura, em volume mais discreto

#### Scenario: Resposta recebida
- **WHEN** chega uma resposta rápida ou atendimento
- **THEN** interrompe o som de espera
- **AND** toca o one-shot de resposta

#### Scenario: Encerramento
- **WHEN** a chamada é cancelada ou perde por timeout
- **THEN** interrompe loops ativos
- **AND** toca o one-shot de encerramento

### Requirement: Reprodução sem sobreposição
O cliente web SHALL evitar sons concorrentes e respeitar restrições de autoplay.

#### Scenario: Troca de estado
- **WHEN** um novo estado sonoro inicia
- **THEN** qualquer loop anterior é parado com fade curto
- **AND** o Web Audio de fallback não toca junto com o WAV

#### Scenario: Autoplay bloqueado
- **WHEN** o navegador bloqueia áudio antes de um gesto
- **THEN** o sistema tenta novamente no próximo gesto do usuário
- **AND** não falha a exibição do overlay

### Requirement: Entrega nativa da assinatura
O push nativo SHALL usar a assinatura recebida oficial quando o SO permitir som customizado.

#### Scenario: Push em Android/iOS
- **WHEN** uma notificação nativa de cutucão é enviada
- **THEN** o payload/canal referencia o asset da assinatura recebida
- **AND** cai no som do sistema se o customizado estiver indisponível
