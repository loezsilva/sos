## Por quê

“Próximos” soa restrito a família/amigos íntimos; “Contatos” cobre melhor quem precisa de ajuda. Em pedidos urgentes, a localização exata do remetente acelera o atendimento.

## O que muda

- Troca a copy visível de “Próximos” para “Contatos” em toda a UI (URLs/código internos preservados).
- Cutucões autenticados e públicos passam a aceitar latitude/longitude opcionais no envio.
- O overlay do destinatário exibe localização e link “Abrir no mapa” quando houver coords.
- Reforça a mensagem de privacidade: “Seus dados estão 100% seguros.”

## Capacidades

### Novas capacidades

- `localizacao-cutucao`: captura, persistência e exibição de coordenadas no cutucão.

### Capacidades modificadas

- `buzz`: overlay de chamada recebida inclui localização quando disponível; linguagem de produto usa Contatos.

## Impacto

- Models `Buzina` e `CutucaoPublico`, migration, views de envio.
- Templates de navegação, próximos, auth, landing e alerta.
- `static/js/buzz.js` e página pública para Geolocation API.
- Push/WebSocket payloads com coords.
