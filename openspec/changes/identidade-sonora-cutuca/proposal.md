## Por quê

O Cutuca ainda usa tons genéricos e um WAV legado, sem uma assinatura própria. Uma identidade sonora coerente reforça o reconhecimento imediato do alerta e diferencia o produto.

## O que muda

- Introduz uma assinatura orgânico-digital original e uma família de sons derivados.
- Substitui o alerta recebido genérico por um motivo curto, quente e reconhecível.
- Adiciona sons específicos para espera/envio, resposta e encerramento.
- Unifica a reprodução no navegador com pré-carregamento, fade e sem sobreposição.
- Reutiliza a assinatura recebida no push nativo (Android/iOS) com fallback do sistema.

## Capacidades

### Novas capacidades

- `identidade-sonora`: assinatura e família de sons do Cutuca, com comportamento de reprodução, acessibilidade e entrega nativa.

### Capacidades modificadas

- `buzz`: a tela de chamada recebida e os estados de chamada passam a usar a identidade sonora oficial.

## Impacto

- Assets em `static/sounds/` e gerador documentado em `scripts/`.
- Refatoração do núcleo de áudio em `static/js/buzz.js`.
- Push nativo e recursos Android/iOS alinhados à assinatura recebida.
- Specs OpenSpec e testes de payload/comportamento.
