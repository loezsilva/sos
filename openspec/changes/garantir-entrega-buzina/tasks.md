## 1. Modelo e migration

- [x] 1.1 Adicionar status `cancelada` e `perdida` em `Buzina.Status`
- [x] 1.2 Criar migration e constante `TEMPO_MAXIMO_ESPERA` (45s) no model
- [x] 1.3 Implementar `cancelar()`, `marcar_perdida()` e `pendentes_ativas_para(usuario)` no model
- [x] 1.4 Em `enviar()`, cancelar pendentes anteriores do mesmo par remetente→destinatário

## 2. API e WebSocket

- [x] 2.1 Criar `POST /api/buzina/<id>/encerrar/` (motivo `usuario` → cancelada, `timeout` → perdida)
- [x] 2.2 Notificar destinatário com evento `buzina_encerrada` e remetente quando aplicável
- [x] 2.3 No `BuzzConsumer.connect`, fazer catch-up: expirar pendentes velhas e reenviar pendentes ativas
- [x] 2.4 Handler `buzina_encerrada` no consumer

## 3. Frontend

- [x] 3.1 Em `buzz.js`, tratar `buzina_encerrada` (fechar alerta / atualizar tela sainte)
- [x] 3.2 Timer de 45s na chamada sainte; ao expirar chamar encerrar com `motivo=timeout`
- [x] 3.3 “Encerrar” do chamador chama API de encerrar (não só fecha UI)
- [x] 3.4 Feedback visual na tela sainte para estados perdida/cancelada
- [x] 3.5 Garantir que catch-up dispara `mostrarAlertaRecebido` com mensagem

## 4. Validação

- [x] 4.1 Destinatário offline → abre app → vê alerta da buzina pendente
- [x] 4.2 Remetente encerra → alerta some no destinatário
- [x] 4.3 Timeout 45s → ambos veem desfecho “perdida”
- [x] 4.4 Resposta rápida continua notificando o remetente normalmente
