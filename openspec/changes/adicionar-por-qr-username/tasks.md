## 1. Modelo e migration

- [x] 1.1 Criar `ConviteCirculo` com status e métodos `enviar`, `aceitar`, `recusar`
- [x] 1.2 Migration + admin básico
- [x] 1.3 Adicionar `qrcode` em `requirements.txt`

## 2. Views e URLs

- [x] 2.1 Landing `/conectar/<username>/` (GET confirmação, POST envia convite)
- [x] 2.2 PNG do QR `/circulos/meu-qr.png`
- [x] 2.3 POST convidar por username e aceitar/recusar
- [x] 2.4 Incluir convites recebidos no contexto de `PaginaCirculosView`

## 3. UI

- [x] 3.1 Botão Meu QR + modal com imagem, username e link
- [x] 3.2 Formulário “Adicionar por username”
- [x] 3.3 Lista de convites pendentes recebidos
- [x] 3.4 Atualizar empty state

## 4. Testes

- [x] 4.1 Teste: convidar → aceitar cria membros mútuos
- [x] 4.2 Teste: recusar não cria membros
- [x] 4.3 Teste: QR/conectar exige auth e não permite self
