## Contexto

Login já existe via `django.contrib.auth.urls`. User custom exige `username` + `email`. Convites por username/QR pressupõem que a outra pessoa possa se cadastrar.

## Decisões

1. **Campos MVP:** `name`, `username`, `email`, `password1`, `password2`, `accepted_the_terms_of_use` (obrigatório).
2. **CBV:** `CreateView` + `ModelForm` em `accounts`.
3. **Pós-cadastro:** `login()` imediato → `LOGIN_REDIRECT_URL`.
4. **URL:** `/contas/cadastro/` (name `cadastro`), antes do include genérico de auth ou via `accounts.urls`.
5. **UI:** mesmo visual do login (card Cutuca, sem nav/menu).

## Não-objetivos

- Verificação de e-mail
- Captcha / OAuth
- Edição de perfil nesta change
