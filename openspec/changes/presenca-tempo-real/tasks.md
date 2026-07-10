## 1. Backend de presença

- [x] 1.1 Criar helper/serviço `Presenca` (Redis set de conexões + debounce disconnect)
- [x] 1.2 Em `connect`: registrar canal; se 0→1, espelhar online no ORM (respeitando ocupado) e notificar círculo
- [x] 1.3 Em `disconnect`: remover canal; se 1→0 após debounce, espelhar offline e notificar círculo
- [x] 1.4 Evento WS `presenca_atualizada` no consumer + payload (`usuario_id`, `status`)
- [x] 1.5 Atualizar `MembroCirculo` em massa com `filter(contato=...).update(...)` (sem loop)

## 2. Frontend

- [x] 2.1 Adicionar `data-contato-id` nos cards e pontos de status relevantes
- [x] 2.2 Em `buzz.js`, handler `presenca_atualizada` atualiza card, contador e `#status-chamada`
- [x] 2.3 Garantir que página chamar desabilita buzina quando status vira offline ao vivo

## 3. Dados e validação

- [x] 3.1 Ajustar seed demo para status inicial offline (presença sobe no login)
- [x] 3.2 Validar: admin e alex logados → cada um vê o outro online
- [x] 3.3 Validar: fechar abas → offline no outro lado após debounce
- [x] 3.4 Validar: duas abas → fecha uma → continua online
