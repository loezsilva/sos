## 1. Modelo e API

- [x] 1.1 Adicionar campo `mensagem` (CharField, max 80, opcional) em `Buzina`
- [x] 1.2 Criar migration e aceitar `mensagem` no POST `/api/buzina/enviar/`

## 2. View e rota

- [x] 2.1 Criar `PaginaChamarContatoView` (LoginRequiredMixin, filtra membro do usuário)
- [x] 2.2 Adicionar rota `circulos/<uuid:membro_id>/chamar/` em `urls.py`
- [x] 2.3 Registrar `rota_ativa` como `circulos` no context processor

## 3. Template da página

- [x] 3.1 Criar `templates/dashboard/chamar_contato.html` sem nav/menu
- [x] 3.2 Layout: avatar + ripples, nome, botão BUZZ redondo central
- [x] 3.3 Seção personalização: textarea mensagem (80 chars), som e vibração desabilitados ("Em breve")
- [x] 3.4 Link voltar para `/circulos/`

## 4. Card clicável

- [x] 4.1 Transformar `card_membro.html` em link para página de chamar
- [x] 4.2 Remover `data-buzinar` do botão bolt (vira indicador visual)
- [x] 4.3 Desabilitar link ou estilo para contatos offline

## 5. JavaScript

- [x] 5.1 Atualizar `buzz.js` para ler mensagem do campo na página chamar
- [x] 5.2 Botão BUZZ da página dispara envio + overlay `chamada_sainte`

## 6. Validação

- [x] 6.1 Clicar card em `/circulos/` navega para página correta
- [x] 6.2 Buzinar com mensagem persiste no modelo
- [x] 6.3 Overlay de resposta funciona na nova página
