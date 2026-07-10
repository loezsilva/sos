## 1. Backend — disponibilidade e regras

- [x] 1.1 Adicionar `Presenca.alternar_disponibilidade(usuario, modo)` (disponivel/nao_perturbe) atualizando espelho ORM e notificando círculo
- [x] 1.2 Criar `AlternarDisponibilidadeView` (`POST /api/disponibilidade/`) e registrar rota
- [x] 1.3 Adicionar `MembroCirculo.remetente_eh_favorito_de(destinatario, remetente)` (ou equivalente no queryset)
- [x] 1.4 Ajustar `MembroCirculo.pode_buzinar` para considerar ocupado + relação VIP do ponto de vista do dono
- [x] 1.5 Ajustar `Buzina.enviar`: se destinatário ocupado e remetente não VIP → criar buzina silenciada (sem `_notificar` de alerta); retornar `silenciada: true` no JSON
- [x] 1.6 Garantir que buzina silenciada entra em histórico/notificações (`lida_em` null)

## 2. Navbar e pill interativo

- [x] 2.1 Transformar pill em botão com estados: Disponível (ciano), Não perturbe (âmbar), Offline (cinza)
- [x] 2.2 Expor status atual do usuário no context processor ou via data-attribute no pill
- [x] 2.3 `buzz.js`: clique alterna modo via `POST /api/disponibilidade/`; desabilitar toggle quando offline
- [x] 2.4 Sincronizar pill ao receber `presenca_atualizada` do próprio usuário (se aplicável)

## 3. UI do círculo e buzina

- [x] 3.1 Atualizar `atualizarCardPresenca` / `pode_buzinar` no JS para ocupado bloquear bolt (não-VIP já refletido pelo backend na página)
- [x] 3.2 Mensagens de estado: "Em não perturbe" no perfil/chamar quando aplicável
- [x] 3.3 Tratar resposta `silenciada: true` em `enviarBuzina` (feedback curto, sem overlay prolongado)
- [x] 3.4 Estilos do pill e estados em `buzz.css`; recompilar

## 4. Testes e validação

- [x] 4.1 Testes: toggle disponibilidade, `enviar` silenciado vs VIP, `pode_buzinar` com ocupado
- [x] 4.2 Teste de integração: pill → ocupado → buzina não-favorito silenciada → favorito com alerta
- [x] 4.3 `openspec validate nao-perturbe`
