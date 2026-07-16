## ADDED Requirements

### Requirement: Localização no cutucão
O sistema SHALL aceitar coordenadas opcionais no envio de cutucão autenticado ou público e exibi-las ao destinatário.

#### Scenario: Envio com localização
- **WHEN** o remetente autoriza a geolocalização no momento do envio
- **THEN** o evento persiste latitude e longitude
- **AND** o overlay do destinatário mostra a localização com link para o mapa

#### Scenario: Envio sem localização
- **WHEN** a permissão de GPS é negada ou falha
- **THEN** o cutucão é enviado normalmente sem coordenadas
- **AND** o overlay não exibe o bloco de localização

#### Scenario: Coordenadas inválidas
- **WHEN** o cliente envia latitude ou longitude fora do intervalo válido
- **THEN** o sistema rejeita as coordenadas
- **AND** não persiste valores inválidos
