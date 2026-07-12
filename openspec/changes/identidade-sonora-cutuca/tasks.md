## 1. Specs e assets

- [x] 1.1 Registrar proposta, design e specs da identidade sonora
- [x] 1.2 Criar gerador Python da família de sons
- [x] 1.3 Gerar WAVs em `static/sounds/` e alias `buzina.wav`

## 2. Cliente web

- [x] 2.1 Refatorar `SomBuzz` para assets pré-carregados, fade e sem sobreposição
- [x] 2.2 Ligar sons aos estados: sainte, recebido, resposta e encerramento
- [x] 2.3 Manter Web Audio apenas como fallback exclusivo

## 3. Nativo

- [x] 3.1 Atualizar `res/raw/buzina.wav` no Android
- [x] 3.2 Confirmar referência iOS/Android do som no push nativo

## 4. Verificação

- [x] 4.1 Cobrir payload nativo e ausência de regressões Django
- [x] 4.2 Validar OpenSpec, Ruff e testes
