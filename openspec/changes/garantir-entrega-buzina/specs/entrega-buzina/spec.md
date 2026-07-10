## Purpose

Garantir que a buzina não seja em vão enquanto o destinatário usa o app: recuperação de pendentes, cancelamento simétrico e timeout com feedback nos dois lados.

## Requisitos ADICIONADOS

### Requirement: Recuperação de buzina pendente
O sistema SHALL entregar ao destinatário qualquer buzina ainda `pendente` e não expirada assim que o WebSocket conectar ou reconectar, em qualquer tela autenticada.

#### Scenario: Destinatário abre o app após a buzina
- **WHEN** existe uma buzina `pendente` para o usuário e ele conecta o WebSocket
- **THEN** o alerta fullscreen é exibido com nome, avatar e mensagem do remetente
- **AND** o remetente permanece na tela “Buzinando…” até resposta, cancelamento ou timeout

#### Scenario: Pendente expirada no catch-up
- **WHEN** a buzina pendente ultrapassou o tempo máximo de espera
- **THEN** o sistema marca-a como `perdida` e NÃO reabre o alerta
- **AND** notifica o remetente se ainda estiver aguardando

### Requirement: Cancelamento pelo remetente
O remetente SHALL poder encerrar a chamada sainte; o destinatário SHALL deixar de ver o alerta correspondente.

#### Scenario: Encerrar enquanto destinatário vê o alerta
- **WHEN** o remetente toca em “Encerrar” com buzina ainda `pendente`
- **THEN** o status passa a `cancelada`
- **AND** o destinatário recebe evento em tempo real e o alerta é fechado
- **AND** a tela do remetente é encerrada

#### Scenario: Encerrar após resposta
- **WHEN** a buzina já não está `pendente`
- **THEN** o encerramento apenas fecha a UI do remetente sem alterar o status final

### Requirement: Timeout de chamada
Uma buzina `pendente` SHALL expirar após o tempo máximo configurado (padrão 45s) e NÃO deixar o remetente aguardando indefinidamente.

#### Scenario: Ninguém responde a tempo
- **WHEN** o tempo máximo se esgota sem resposta nem cancelamento
- **THEN** o status passa a `perdida`
- **AND** o remetente vê feedback de chamada perdida
- **AND** o alerta do destinatário é removido se ainda estiver aberto

### Requirement: Estados na tela Buzinando
A tela sainte do remetente SHALL refletir o ciclo de vida da buzina de forma clara.

#### Scenario: Aguardando
- **WHEN** a buzina foi enviada e ainda está `pendente`
- **THEN** exibe “Buzinando...” / “Aguardando resposta” e a mensagem curta se houver

#### Scenario: Resposta recebida
- **WHEN** o destinatário atende ou envia resposta rápida
- **THEN** a tela mostra a resposta e permite fechar

#### Scenario: Perdida ou cancelada
- **WHEN** a buzina termina como `perdida` ou `cancelada`
- **THEN** a tela informa o desfecho e deixa de indicar espera ativa
