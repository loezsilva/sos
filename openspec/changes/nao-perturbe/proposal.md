## Por quê

O pill **"Disponível"** no navbar é decorativo hoje — não reflete nem controla a intenção do usuário. Quem precisa de foco (reunião, sono, trabalho) não tem como sinalizar ao círculo que não quer ser interrompido, exceto ficar offline (fechar o app), o que quebra presença e confiança do produto.

A spec principal já prevê **modo não perturbe inteligente** (bloquear não-VIP, liberar favoritos), e a infraestrutura de presença já trata `ocupado` como preferência manual que não é sobrescrita no connect. Falta ligar a UI ao comportamento de entrega da buzina.

## O que muda

- O pill do navbar vira **seletor de disponibilidade**: alternar entre **Disponível** (online) e **Não perturbe** (ocupado).
- **Offline** continua automático (sem conexão WebSocket).
- Em não perturbe: buzinas de **não-favoritos** são **silenciadas** — registradas no histórico/notificações, sem overlay, som ou vibração.
- **Favoritos (`eh_vip`)** continuam com fluxo normal (alerta fullscreen).
- Cards, perfil e página de chamar refletem **Ocupado** em tempo real; remetente não-favorito vê contato indisponível para buzina.
- Endpoint para alternar disponibilidade + atualização live via `presenca_atualizada`.

## Capacidades

### Novas capacidades

- `nao-perturbe`: toggle de disponibilidade no navbar, regras de silenciamento na entrega da buzina e feedback visual/UX para remetente e destinatário.

### Capacidades modificadas

- `buzz`: o requisito "Modo não perturbe inteligente" deixa de ser placeholder e passa a especificar silenciamento de não-VIP, bypass de favoritos e integração com o pill do navbar.

## Impacto

- **Models** (`apps/dashboard/models.py`): `Buzina.enviar` e `MembroCirculo.pode_buzinar` (ou método dedicado) consideram ocupado + relação VIP.
- **Presença** (`apps/dashboard/presenca.py`): método para alternar disponibilidade manual e notificar círculo.
- **Views/URLs**: `AlternarDisponibilidadeView` (`POST /api/disponibilidade/`).
- **Templates**: `partials/nav.html` — pill clicável com estados visuais distintos.
- **Frontend** (`static/js/buzz.js`): toggle, sincronização com `presenca_atualizada`, desabilitar buzina para ocupado (não-VIP).
- **Specs existentes**: favoritos na home e perfil já alimentam a lista VIP; nenhuma mudança de modelo de favorito nesta change.
