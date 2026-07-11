# 👆 System Design: Cutuca.online

## 1. Visão Geral (Overview)
O **Cutuca.online** é um aplicativo/PWA de notificações de ação rápida (One-Tap Notification). O objetivo principal é permitir que usuários (com foco em acessibilidade para crianças e idosos) enviem um alerta instantâneo ("Cutucão") para uma lista pré-definida de contatos favoritos com apenas um clique.

**Requisitos Não Funcionais Críticos:**
* **Baixa Latência:** A notificação deve chegar em tempo real (menos de 2 segundos).
* **Alta Disponibilidade:** O sistema precisa estar sempre online (99.9% uptime).
* **Acessibilidade:** Interface front-end extremamente simplificada.
* **Baixo Consumo de Bateria/Dados:** O app ficará em background aguardando push notifications.

---

## 2. Arquitetura de Alto Nível

A arquitetura segue um modelo baseado em microsserviços simples (ou Monólito Modular inicial) hospedado na nuvem (Cloud-native).

### 2.1. Componentes do Sistema
1.  **Client Application (Front-end):**
    * PWA (Progressive Web App) desenvolvido em React, Vue ou Svelte para acesso universal via browser (`.online`).
    * App Nativo/Híbrido (React Native ou Flutter) focado em integração profunda com os recursos do SO (Push Notifications, vibração, ignorar modo "Não Perturbe" se configurado).
2.  **API Gateway:**
    * Ponto de entrada para todas as requisições do cliente. Gerencia autenticação de rotas e Rate Limiting (prevenção de spam de botões).
3.  **Application Server (Backend):**
    * Gerencia a lógica de negócios: Contas de usuários, listas de contatos favoritos e disparos de eventos.
4.  **Database (Banco de Dados):**
    * **PostgreSQL:** Banco relacional para armazenar Usuários, Relações de Contatos (quem autorizou quem) e Logs de eventos.
    * **Redis:** Banco em memória para gerenciar sessões, cache de contatos frequentes e controle de Rate Limiting.
5.  **Notification Engine (Serviço de Mensageria):**
    * Serviço dedicado à entrega da mensagem usando **Firebase Cloud Messaging (FCM)** (para Android/Web) e **Apple Push Notification service (APNs)** (para iOS).

---

## 3. Fluxo de Dados (Data Flow)

### Cenário: Envio de um "Cutucão"
1.  **Ação:** O Usuário A (Remetente) abre o app e clica no botão principal "Cutucar".
2.  **Requisição:** O Client envia uma requisição `POST /api/v1/cutuca` para o API Gateway contendo o `user_id` e possivelmente coordenadas de GPS (opcional).
3.  **Validação (Gateway/Redis):** O sistema checa no Redis se o Usuário A não excedeu o limite de cliques (ex: max 3 cliques por minuto) para evitar spam involuntário (criança apertando várias vezes).
4.  **Processamento (Backend):** O Backend busca no PostgreSQL/Redis a lista de `favorite_contacts` atrelada ao Usuário A.
5.  **Disparo:** O Backend constrói o payload da notificação (Título: *"Ei!"*, Corpo: *"João está te cutucando!"*) e envia para o **Notification Engine**.
6.  **Entrega:** O FCM/APNs entrega a notificação via Push para os dispositivos dos contatos favoritos.
7.  **Confirmação (Opcional):** O app do contato envia um webhook de volta confirmando o recebimento ("Delivered"), atualizando a tela do Remetente em tempo real via WebSockets/Server-Sent Events (SSE).

---

## 4. Stack Tecnológica Recomendada

| Camada | Tecnologia Sugerida | Justificativa |
| :--- | :--- | :--- |
| **Front-end / App** | React Native / Expo | Código único para iOS, Android e Web. Ótima gestão de Push Notifications via Expo. |
| **Back-end** | Node.js (Express/NestJS) ou Go | Excelente para lidar com alta concorrência de I/O (disparos paralelos de notificações). |
| **Banco de Dados** | PostgreSQL | Robusto para gerenciar as permissões e amizades (Modelo Relacional). |
| **Cache / Fila** | Redis | Essencial para Rate Limiting rápido e cache de sessões ativas. |
| **Notificações** | Firebase (FCM) | Padrão da indústria, gratuito para mensagens de push e fácil integração com web/mobile. |
| **Hospedagem** | AWS, Vercel ou Render | Foco em infraestrutura escalável (Serverless ou Containers). |

---

## 5. Design do Banco de Dados (Entidades Principais)

* **`Users`**: `id`, `name`, `phone`, `push_token`, `created_at`
* **`Connections`** (Relação muitos-para-muitos): `user_id`, `contact_id`, `status` (pending, accepted)
* **`EventsLog`**: `id`, `sender_id`, `recipient_id`, `timestamp`, `status` (sent, delivered, read)

---

## 6. Considerações de Segurança e Privacidade
* **Token de Push Rotativo:** Os `push_tokens` devem ser atualizados regularmente e armazenados com segurança.
* **Consentimento (Opt-in):** Um usuário só pode receber um "Cutucão" se tiver aceitado previamente o convite de conexão do remetente. Não há envio aberto baseado apenas no número de telefone para evitar abusos.
* **Rate Limiting Severo:** Implementar regras rígidas no Redis para evitar sobrecarga no disparo de mensagens caso um dispositivo entre em loop ou um usuário faça spam do botão.

# 🎨 UI Design System: Cutuca.online

## 1. Design Tokens (Fundações)

Estes valores globais devem ser mapeados como variáveis CSS (ou no seu arquivo de configuração do Tailwind, por exemplo) para garantir consistência.

*   **Cores Principais:**
    *   `--color-primary`: `#FF6600` (Laranja Cutuca - Ações principais)
    *   `--color-primary-hover`: `#E65C00`
    *   `--color-secondary`: `#8E24AA` (Roxo Apoio - Elementos neutros e fundos)
    *   `--color-background`: `#F8F9FA` (Cinza muito claro, quase branco)
    *   `--color-surface`: `#FFFFFF` (Cards e Modais)
*   **Tipografia:**
    *   `--font-family`: `'Nunito', sans-serif` (Arredondada e amigável)
    *   `--text-base`: `16px` (Maior legibilidade)
    *   `--text-lg`: `20px`
    *   `--text-xl`: `24px`
*   **Espaçamento & Layout:**
    *   `--spacing-base`: `8px`
    *   `--radius-md`: `12px` (Bordas arredondadas)
    *   `--radius-full`: `9999px` (Para botões de ação circulares)

---

## 2. Especificação de Componentes

### 2.1. Botões (`<CutucaButton>`)
O componente mais importante do sistema. Deve ser impossível de errar o clique.

**Anatomia:**
Área clicável mínima de 48x48px (padrão de acessibilidade mobile). Pode conter um ícone (à esquerda ou direita) e texto.

**Props (API do Componente):**

| Propriedade | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `variant` | `String` | `'primary'` | Define a cor (`'primary'`, `'secondary'`, `'ghost'`, `'danger'`). |
| `size` | `String` | `'lg'` | Tamanho do botão (`'sm'`, `'md'`, `'lg'`, `'xl-circle'`). |
| `block` | `Boolean` | `false` | Se `true`, ocupa 100% da largura do contêiner. |
| `isLoading` | `Boolean` | `false` | Substitui o texto/ícone por um *spinner* e desabilita o clique. |
| `icon` | `String` | `null` | Nome do ícone (ex: `mdi-hand-pointing-up`). |

**Comportamento (Estados):**
*   **Active/Pressed:** Escala reduzida para `0.95` (Feedback tátil visual).
*   **Disabled:** Opacidade em `50%`, cursor `not-allowed`.

---

### 2.2. Cards de Contato (`<CutucaCard>`)
Usado para exibir a lista de contatos favoritos na tela inicial. Precisa ser altamente legível.

**Anatomia:**
Fundo branco (`surface`), sombra suave (`elevation`), foto do contato (Avatar), nome e indicador de status.

**Slots:**
*   `prepend`: Área para o Avatar.
*   `default`: Título (Nome do contato) e Subtítulo (Relação/Status).
*   `append`: Área para ações (ex: botão de configuração ou botão de chamar direto).

**Props (API do Componente):**

| Propriedade | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `interactive` | `Boolean` | `true` | Se `true`, o card inteiro é clicável (adiciona estado de hover/active). |
| `status` | `String` | `'offline'` | Bolinha de status (`'online'`, `'offline'`, `'busy'`). |
| `elevation` | `Number` | `1` | Nível da sombra (0 a 3). |

---

### 2.3. Dropdown / Menu de Ações (`<CutucaDropdown>`)
Utilizado para ações secundárias, como configurações do perfil ou exclusão de contatos.

**Anatomia:**
Um botão *trigger* (geralmente ícone de 3 pontos verticais ou engrenagem) que abre uma lista flutuante.

**Props & Emits:**

| Propriedade/Evento | Tipo | Descrição |
| :--- | :--- | :--- |
| `items` (Prop) | `Array` | Lista de objetos: `[{ label: 'Editar', icon: 'edit', action: 'edit_user' }]` |
| `placement` (Prop) | `String` | Posição do menu flutuante (`'bottom-end'`, `'bottom-start'`). |
| `@select` (Emit) | `Event` | Dispara o `action` do item clicado para o componente pai tratar. |

---

### 2.4. Select / Seletor de Opções (`<CutucaSelect>`)
Substituto para o `<select>` nativo, otimizado para o dedo (Touch). Usado, por exemplo, para definir o "grau de parentesco" ao adicionar um contato.

**Anatomia:**
Campo de input que, ao ser tocado, abre um *Bottom Sheet* (no mobile) ou um *Popover* (no desktop) com as opções em formato de lista larga.

**Props & Emits:**

| Propriedade/Evento | Tipo | Descrição |
| :--- | :--- | :--- |
| `options` (Prop) | `Array` | Array de objetos `[{ text: 'Mãe', value: 'mother' }, ...]` |
| `modelValue` (Prop) | `String/Number`| Valor atualmente selecionado (v-model / bind duplo). |
| `placeholder` (Prop)| `String` | Texto exibido quando nada está selecionado. |
| `@update:modelValue`| `Event` | Atualiza a seleção no estado global/pai. |

**Consideração Mobile:**
Para idosos, menus *dropdown* tradicionais são difíceis de rolar. Transformar o `<CutucaSelect>` em um modal de tela inteira ou *Bottom Sheet* na versão mobile reduz drasticamente o atrito de uso.

---

### 2.5. Avatar (`<CutucaAvatar>`)
Representação visual dos usuários.

**Props:**

| Propriedade | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `src` | `String` | `null` | URL da foto do contato. |
| `name` | `String` | `''` | Nome usado para gerar iniciais (ex: "Maria" -> "M") se não houver foto. |
| `size` | `Number` | `48` | Tamanho em pixels. Opções: 32, 48, 64. |
| `color` | `String` | `random`| Cor de fundo gerada deterministicamente baseada no nome se não houver foto. |

---

### 2.6. Alertas e Toast Notifications (`<CutucaToast>`)
Feedback não-obstrutivo do sistema (ex: "Fulano aceitou seu convite", "Sem conexão com a internet").

**Props:**

| Propriedade | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `type` | `String` | `'info'` | `'success'`, `'error'`, `'warning'`, `'info'`. |
| `message` | `String` | `''` | O texto do alerta. |
| `duration` | `Number` | `3000` | Tempo em milissegundos até sumir automaticamente da tela. |

## 3. Estados de Carregamento (Skeleton Loaders)
Para evitar que o layout pule enquanto os contatos são carregados do banco de dados, o design prevê o uso de **Skeletons** pulsantes nos mesmos formatos dos cards e avatares (cinza claro no fundo branco), melhorando a percepção de performance.

## Logo marca:
static/logo-cutuca-online.png