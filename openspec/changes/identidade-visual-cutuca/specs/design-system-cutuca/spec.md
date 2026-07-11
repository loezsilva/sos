## ADDED Requirements

### Requirement: Tokens Cutuca
O front-end SHALL expor tokens de cor, tipografia, espaçamento e raio alinhados ao Design System Cutuca em `docs/DESIGN.md`.

#### Scenario: Cores principais
- **WHEN** o CSS/Tailwind é carregado
- **THEN** `--color-primary` / `primary` é `#FF6600`
- **AND** `--color-secondary` / `secondary` é `#8E24AA`
- **AND** `--color-background` / `background` é `#F8F9FA`
- **AND** `--color-surface` / `surface` é `#FFFFFF`

#### Scenario: Tipografia
- **WHEN** qualquer página autenticada ou de auth é renderizada
- **THEN** a família tipográfica principal é Nunito
- **AND** o tamanho base de leitura é no mínimo 16px

### Requirement: Tema claro padrão
A interface SHALL usar tema claro por padrão, sem dark mode forçado no `html`.

#### Scenario: Carregar base
- **WHEN** o usuário abre qualquer tela
- **THEN** o fundo da página é claro (`#F8F9FA` ou token equivalente)
- **AND** o `html` não aplica a classe `dark`

### Requirement: Botão de ação Cutuca
O botão principal de cutucar SHALL ter área mínima de 48×48px, variante primary laranja e feedback pressed com scale 0.95.

#### Scenario: Pressionar botão principal
- **WHEN** o usuário pressiona o botão de cutucar
- **THEN** o botão escala para aproximadamente 0.95
- **AND** permanece legível e com contraste adequado no tema claro

### Requirement: Card de contato Cutuca
Cards de contato SHALL usar surface branca, sombra suave, avatar, nome e indicador de status.

#### Scenario: Listar contato
- **WHEN** a lista de círculos/contatos é exibida
- **THEN** cada contato aparece em card com fundo surface
- **AND** o status (online/ocupado/offline) é visível

### Requirement: Skeleton de carregamento
Listas de contatos SHALL poder exibir skeletons pulsantes no formato dos cards enquanto carregam.

#### Scenario: Carregamento inicial
- **WHEN** os contatos ainda não estão disponíveis
- **THEN** placeholders skeleton no formato de card/avatar são exibidos
- **OR** a tela evita layout shift equivalente

### Requirement: Branding Cutuca na UI
Textos de marca visíveis ao usuário SHALL usar “Cutuca” / “Cutucar” / “Cutucão” em vez de “Buzz” / “Buzina”.

#### Scenario: Título e PWA
- **WHEN** o usuário vê o título da página ou o nome do PWA
- **THEN** a marca exibida é Cutuca
