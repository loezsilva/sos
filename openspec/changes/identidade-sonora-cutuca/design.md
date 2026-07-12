## Contexto

Hoje o alerta usa osciladores sine genéricos e um `buzina.wav` legado, com risco de tocar Web Audio e WAV ao mesmo tempo. O app nativo já referencia `R.raw.buzina` e `sound='buzina.wav'`.

## Objetivos / Não-objetivos

**Objetivos:**
- Criar assinatura orgânico-digital original e família coerente (envio, recebido, resposta, encerramento).
- Reproduzir no navegador com pré-carregamento, fade e sem sobreposição.
- Reutilizar a assinatura recebida no push nativo.

**Não-objetivos:**
- Sons personalizados por contato.
- Compositor visual ou biblioteca de áudio de terceiros.
- Garantir som customizado em todos os modos silenciosos do SO.

## Decisões

1. **Motivo de três notas** (F#4 → A4 → C#5) com ataque macio e harmônicos leves — reconhecível sem parecer ringtone genérico.
2. **Assets WAV 44.1 kHz mono** gerados por script Python versionado; `buzina.wav` permanece como alias do alerta recebido para não quebrar canais Android/iOS existentes.
3. **HTMLAudioElement pré-carregado** como fonte principal no web; Web Audio só como fallback, nunca em paralelo.
4. **Estados**: `sainte` em loop discreto, `recebido` em loop presente, `resposta` one-shot positivo, `encerrar` one-shot suave.

## Riscos / Trade-offs

- [Autoplay bloqueado] → desbloquear no gesto e manter fallback silencioso até interação.
- [Canal Android já criado] → manter nome `buzina` no raw; conteúdo novo vale para instalações novas/reinstalação.
- [Fadiga em loop] → ciclo curto, volume controlado e fade ao parar.

## Plano de migração

1. Gerar e publicar assets.
2. Atualizar `buzz.js` e push nativo.
3. Copiar assinatura para `mobile/.../res/raw/buzina.wav`.
4. Validar web + payload nativo.

## Questões em aberto

- Nenhuma bloqueante; personalização por contato fica para mudança futura.
