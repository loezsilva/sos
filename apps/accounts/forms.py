from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password

from apps.accounts.models import User


class CadastroForm(UserCreationForm):
    name = forms.CharField(
        label='Nome',
        max_length=255,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Como quer ser chamado',
                'autocomplete': 'name',
                'autofocus': True,
                'class': (
                    'w-full bg-surface-container-low rounded-full px-6 py-3 '
                    'text-on-surface font-body-md border border-outline-variant '
                    'focus:ring-2 focus:ring-primary focus:outline-none '
                    'placeholder-on-surface-variant min-h-[48px]'
                ),
            }
        ),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'voce@email.com',
                'autocomplete': 'email',
                'class': (
                    'w-full bg-surface-container-low rounded-full px-6 py-3 '
                    'text-on-surface font-body-md border border-outline-variant '
                    'focus:ring-2 focus:ring-primary focus:outline-none '
                    'placeholder-on-surface-variant min-h-[48px]'
                ),
            }
        ),
    )
    accepted_the_terms_of_use = forms.BooleanField(
        label='Aceito os termos de uso',
        required=True,
        error_messages={'required': 'É necessário aceitar os termos de uso.'},
        widget=forms.CheckboxInput(
            attrs={'class': 'mt-1 w-4 h-4 accent-primary shrink-0'}
        ),
    )

    class Meta:
        model = User
        fields = (
            'name',
            'username',
            'email',
            'password1',
            'password2',
            'accepted_the_terms_of_use',
        )
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'placeholder': 'seu.usuario',
                    'autocomplete': 'username',
                    'autocapitalize': 'none',
                    'class': (
                        'w-full bg-surface-container-low rounded-full px-6 py-3 '
                        'text-on-surface font-body-md border border-outline-variant '
                        'focus:ring-2 focus:ring-primary focus:outline-none '
                        'placeholder-on-surface-variant min-h-[48px]'
                    ),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for nome in ('password1', 'password2'):
            self.fields[nome].widget.attrs.update(
                {
                    'placeholder': '••••••••',
                    'class': (
                        'w-full bg-surface-container-low rounded-full px-6 py-3 '
                        'text-on-surface font-body-md border border-outline-variant '
                        'focus:ring-2 focus:ring-primary focus:outline-none '
                        'placeholder-on-surface-variant min-h-[48px]'
                    ),
                }
            )
        self.fields['username'].label = 'Username'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirmar senha'

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Este username já está em uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail já está em uso.')
        return email

    def clean_password1(self):
        senha = self.cleaned_data.get('password1')
        if senha:
            validate_password(senha)
        return senha

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.name = self.cleaned_data['name'].strip()
        usuario.email = self.cleaned_data['email']
        usuario.accepted_the_terms_of_use = True
        if commit:
            usuario.save()
        return usuario
