## Contexto

Hoje a lista de conexões chama-se “Próximos” e o cutucão não carrega localização. Casos de ajuda/urgência pedem linguagem mais ampla e posição do remetente.

## Objetivos / Não-objetivos

**Objetivos:**
- Renomear a copy para Contatos.
- Anexar GPS opcional ao envio e mostrar no alerta.
- Manter envio mesmo se a geolocalização falhar.

**Não-objetivos:**
- Tracking contínuo ou histórico de trajetos.
- Renomear URLs (`/proximos/`) ou classes Python nesta mudança.
- Geocoding reverso (endereço textual).

## Decisões

1. **Copy apenas** — evita migração de rotas e quebra de deep links.
2. **Coords no momento do envio** — privacidade melhor que tracking em background.
3. **Campos nullable** — cutucão segue sem GPS se permissão negar.
4. **Mapa via Google Maps URL** — zero dependência de SDK de mapa.

## Riscos / Trade-offs

- [Permissão GPS negada] → envia sem coords, feedback discreto.
- [Coords falsas no POST] → validar ranges lat/lng no servidor.
- [Canal Android antigo] → payload inclui coords; UI web/nativa lê se presente.

## Plano de migração

1. Migration de campos.
2. Deploy de assets/JS e templates.
3. Sem backfill — eventos antigos ficam sem localização.

## Questões em aberto

- Nenhuma bloqueante.
