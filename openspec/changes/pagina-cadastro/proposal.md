## Por quê

Sem cadastro público, novos usuários só entram via admin. Para o Cutuca crescer (convites por QR/username), quem recebe o link precisa criar conta sozinho.

## O que muda

- Página de cadastro em `/contas/cadastro/`
- Formulário: nome, username, e-mail, senha, confirmação e aceite dos termos
- Após sucesso: login automático e redirect para o início
- Link entre login ↔ cadastro

## Capacidades

### Novas capacidades
- `cadastro-conta`: criação de conta pelo app

### Capacidades modificadas
- (nenhuma)

## Impacto

- `apps/accounts` (forms, views, urls)
- Templates `registration/`
- `apps/urls.py`
