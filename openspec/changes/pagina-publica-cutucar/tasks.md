## 1. Modelos e segurança

- [x] 1.1 Criar `CanalPublico` com proprietário, chave UUID única, estado ativo e regeneração
- [x] 1.2 Criar `CutucaoPublico` com destinatário, remetente opcional, nickname, status e payloads
- [x] 1.3 Gerar e aplicar migration dos novos modelos
- [x] 1.4 Implementar normalização de identidade e regra que impede uso do próprio canal
- [x] 1.5 Implementar rate limit por canal/origem e cooldown usando cache
- [x] 1.6 Cobrir models, chave revogável, identidade e limites com testes

## 2. Backend público

- [x] 2.1 Criar `FormCutucaoPublico` com validação de nickname anônimo
- [x] 2.2 Criar CBV pública para GET e POST usando thin view
- [x] 2.3 Adicionar URL não enumerável `/c/<uuid>/` e resposta 404 para canal inválido
- [x] 2.4 Persistir nickname anônimo válido na sessão
- [x] 2.5 Criar endpoints autenticados para ativar, desativar e regenerar o canal
- [x] 2.6 Criar view PNG do QR público e preservar a view de QR de conexão
- [x] 2.7 Cobrir fluxos anônimo, autenticado, inválido, próprio link e CSRF com testes

## 3. Entrega em tempo real e push

- [x] 3.1 Publicar `cutucao_publico_recebido` no grupo WebSocket do proprietário
- [x] 3.2 Adicionar payload e envio de Web Push para cutucões públicos
- [x] 3.3 Adicionar payload e envio de push nativo para cutucões públicos
- [x] 3.4 Incluir eventos públicos na central de atividades sem link de perfil inválido
- [x] 3.5 Cobrir payloads, entrega e atividades públicas com testes

## 4. Interface pública

- [x] 4.1 Preparar uso dos blocks de `base.html` para página pública sem shell autenticado
- [x] 4.2 Criar template público responsivo com identidade do proprietário e nickname condicional
- [x] 4.3 Implementar botão tátil com hold de dois segundos, progresso e feedback de envio
- [x] 4.4 Tratar erros de nickname, cooldown, rate limit e canal indisponível
- [x] 4.5 Garantir foco visível, alvos de 48 px e `prefers-reduced-motion`

## 5. Interface do proprietário

- [x] 5.1 Adicionar área para copiar, ativar, desativar e regenerar o link público
- [x] 5.2 Adicionar modal do QR “Cutucar” separado do QR “Conectar”
- [x] 5.3 Atualizar o overlay global para exibir origem pública sem respostas rápidas
- [x] 5.4 Atualizar notificações recentes para renderizar eventos públicos

## 6. Verificação

- [x] 6.1 Testar compartilhamento, leitura do QR e envio em mobile e desktop
- [x] 6.2 Validar que URLs antigas deixam de funcionar após regeneração
- [x] 6.3 Validar que presença e dados privados não aparecem na página pública
- [x] 6.4 Executar lints, testes Django e validação OpenSpec

## 7. Revisão pós-implementação

- [x] 7.1 Tornar rate limit e cooldown atômicos e endurecer resolução da origem
- [x] 7.2 Impedir vazamento de username e rejeitar controles Unicode no nickname
- [x] 7.3 Isolar falhas de push sem perder o evento persistido
- [x] 7.4 Alinhar página pública ao layout tátil e aos tokens visuais do app
- [x] 7.5 Validar layout, hold e movimento reduzido em desktop e mobile
- [x] 7.6 Recuperar cutucões públicos pendentes no reconnect e deep link
- [x] 7.7 Refinar copy, acessibilidade e metadados do overlay público
- [x] 7.8 Mover compartilhamento público para o modal unificado de QR
- [x] 7.9 Atualizar link público no modal sem recarregar a página

## 8. Resposta e cancelamento público

- [x] 8.1 Evoluir `CutucaoPublico` com estados, resposta rápida e token de visita
- [x] 8.2 Criar migration incremental e endpoints de status, encerrar e responder
- [x] 8.3 Autorizar acompanhamento por sessão/token ou remetente autenticado
- [x] 8.4 Atualizar página pública para estado de chamada com polling e cancelamento
- [x] 8.5 Liberar respostas rápidas no overlay para origem pública
- [x] 8.6 Cobrir autorização, concorrência, timeout e refresh com testes
