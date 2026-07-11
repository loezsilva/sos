## Contexto

`MembroCirculo` é direcional (`dono` → `contato`). Cutucar exige o vínculo. DESIGN.md exige opt-in (`pending`/`accepted`). Hoje só admin/seed cria membros.

## Objetivos

- Permitir adicionar pessoas por QR e por username, com aceite
- Manter Fat Models: criar/aceitar/recusar no model
- UI mínima na página `/circulos/`

## Não-objetivos

- Remover membros (pode vir depois)
- Notificação push do convite (toast/lista na página basta no MVP)
- Deep link nativo Capacitor além da URL HTTPS

## Decisões

1. **Model `ConviteCirculo`**: `remetente`, `destinatario`, `status` (pendente/aceito/recusado), unique (remetente, destinatario) enquanto pendente/aceito.
2. **Aceite cria vínculo mútuo**: `MembroCirculo` nos dois sentidos (get_or_create).
3. **QR**: URL ` /conectar/<username>/ ` com PNG gerado sob demanda (`qrcode` + Pillow). Quem escaneia envia convite **para** o dono do QR (remetente=scanner, destinatario=dono do QR).
4. **Busca**: endpoint/form na página Círculos busca `User` por username exato (case-insensitive), exclui self e já-membros; botão “Convidar”.
5. **Convites recebidos**: lista no topo de `/circulos/` com Aceitar/Recusar.

## Riscos

- Username tipável facilita spam → rate limit leve depois; unique + não reenviar pendente.
- QR sem login: landing pede login e redireciona de volta.

## Migração

- Migration Django para `ConviteCirculo`
- `qrcode` em `requirements.txt`
