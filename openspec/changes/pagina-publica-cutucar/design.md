## Contexto

O Cutuca exige hoje uma conta e um `MembroCirculo` para enviar uma `Buzina`. O QR atual leva ao convite de conexão e também exige autenticação. A nova página representa um consentimento explícito do proprietário do link para receber um contato pontual de alguém que pode não possuir conta.

O fluxo público não pode criar usuários artificiais nem enfraquecer as invariantes de `Buzina`, que pressupõe remetente autenticado e vínculo. Também precisa limitar spam, evitar enumeração de usuários e entregar o alerta pelos canais atuais de WebSocket e push.

## Objetivos / Não-objetivos

**Objetivos:**

- Oferecer uma URL pública, compartilhável e revogável por usuário.
- Identificar visitantes anônimos por nickname e autenticados pela conta.
- Entregar ao proprietário um alerta imediato com a origem pública claramente indicada.
- Gerar QR Code para a URL pública.
- Preservar o fluxo de conexão por username/QR existente como ação separada.
- Aplicar rate limiting, cooldown e validação antes de gerar qualquer alerta.
- Reutilizar o design tátil do Cutuca, incluindo botão circular, progresso ao segurar e `prefers-reduced-motion`.

**Não-objetivos:**

- Criar conta automaticamente para visitantes anônimos.
- Criar conexão ou adicionar alguém aos próximos ao usar o link.
- Exibir presença, e-mail, username ou outros dados privados do proprietário.
- Transformar o link em canal de emergência ou garantir entrega quando push não estiver configurado.
- Abrir WebSocket anônimo; o visitante acompanha a chamada por sessão e polling.

## Decisões

### 1. Canal público separado da relação entre usuários

Criar `CanalPublico` com relação `OneToOne` ao proprietário, chave UUID aleatória única, estado ativo e data de regeneração. A URL será curta e não enumerável, como `/c/<uuid>/`.

O canal será criado sob demanda ao abrir o compartilhamento. Desativar preserva a chave; regenerar troca a chave e invalida imediatamente URLs e QRs anteriores.

**Por quê:** username em URL é previsível e expõe quem possui conta. Um token aleatório funciona como capacidade revogável. Foi descartado usar o username ou o ID do usuário.

### 2. Evento público próprio

Criar `CutucaoPublico` com destinatário obrigatório, remetente autenticado opcional, nickname normalizado, canal usado, status e timestamps. O nome exibido será:

- usuário autenticado: `name` ou `username` da conta;
- visitante anônimo: nickname informado e validado.

O model/manager concentrará criação, validação de canal e payloads. A view apenas validará o form, aplicará limite e orquestrará a resposta.

**Por quê:** tornar `Buzina.remetente` nulo quebraria métodos, histórico e respostas que pressupõem dois usuários. O evento separado mantém o domínio autenticado íntegro.

### 3. Entrega pelos canais existentes, com tipo próprio

Após persistir o evento, o serviço enviará:

- WebSocket ao grupo do proprietário com `tipo: cutucao_publico_recebido`;
- Web Push e push nativo com título contendo o nome público;
- registro na central de atividades do proprietário.

O overlay global tratará o novo tipo e mostrará “Cutucão pelo link público”, nome do visitante e as mesmas respostas rápidas do fluxo autenticado. Cancelamento e timeout fecham o overlay.

**Por quê:** reutilizar o pipeline reduz latência, mas um tipo explícito evita que o frontend chame endpoints de resposta de `Buzina`.

### 4. Identidade anônima curta e temporária

Um form Django aceitará nickname de 2 a 40 caracteres, removerá espaços excedentes e rejeitará caracteres de controle. Após envio válido, o nickname poderá ser mantido na sessão para novas visitas no mesmo navegador.

Visitantes autenticados não verão o campo; o backend ignorará qualquer nickname enviado manualmente e usará a identidade da conta.

### 5. Proteção em camadas contra abuso

- POST protegido por CSRF.
- Rate limit via cache por canal + IP transformado em hash, sem persistir IP bruto.
- Cooldown por sessão/origem para impedir múltiplos toques acidentais.
- Limite inicial: 3 envios por minuto por origem e canal, configurável.
- Uma nova tentativa dentro do cooldown retorna feedback claro sem criar evento.
- Canal inativo ou chave antiga responde 404 para não revelar o proprietário.
- Nickname é texto simples e sempre escapado pelo template/JSON.

O botão exigirá segurar por dois segundos, coerente com o fluxo atual, mas isso é apenas proteção de UX; o backend continua sendo a autoridade.

### 6. Chamada pública com acompanhamento seguro

Após o envio, a página pública entra em estado de chamada: “Cutucando…”, countdown, cancelamento e desfecho. A página não revela presença do proprietário.

O visitante autoriza acompanhamento e cancelamento por uma referência na sessão do navegador; usuário autenticado também prova autoria pelo `remetente`. IDs sem sessão/autoria retornam 404. Visitantes anônimos consultam status por polling curto; remetentes autenticados também podem receber o desfecho via WebSocket.

**Por quê:** presença é informação privada e o visitante anônimo não possui canal WebSocket autenticado.

### 7. Compartilhamento e QR

A seção de próximos/configurações oferecerá:

- copiar link público;
- mostrar QR para cutucar;
- ativar/desativar;
- gerar novo link;
- acesso separado ao QR de conexão existente.

O QR público será PNG gerado sob demanda com `qrcode`, já presente no projeto.

### 8. Template público

O template estenderá `base.html`, mas removerá `nav`, `menu` e `footer` do app. Usará os blocks `title`, `body_overflow`, `main_padding`, `extra_css`, `main` e `extra_js`, com logo, identificação mínima do proprietário, nickname quando necessário e botão tátil central.

## Riscos / Trade-offs

- [Link público compartilhado fora do contexto] → proprietário pode desativar ou regenerar a chave.
- [Spam distribuído] → rate limit por origem e canal; limites globais e captcha podem ser adicionados depois.
- [Nickname ofensivo ou enganoso] → tamanho/normalização e indicação explícita de “nome informado pelo visitante”; moderação avançada fica fora do MVP.
- [Evento separado duplicar partes de notificação] → métodos de payload no model e pequenos adaptadores nos serviços existentes.
- [Visitante interpretar aceite como entrega garantida] → copy informa apenas envio, sem prometer leitura.
- [QR atual mudar de significado] → manter “Conectar” separado e rotular claramente os dois QRs.

## Plano de migração

1. Criar migration para `CanalPublico` e `CutucaoPublico`.
2. Adicionar forms, serviços, views e URLs sem alterar rotas atuais.
3. Integrar WebSocket/push e overlay.
4. Adicionar controles de compartilhamento e QR.
5. Implantar com canais criados apenas sob demanda.
6. Rollback: desativar a rota pública e os controles; tabelas podem permanecer sem afetar `Buzina`.

## Questões em aberto

- Captcha será avaliado se os limites por cache não forem suficientes em produção.
