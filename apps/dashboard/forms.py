from django import forms


class FormCutucaoPublico(forms.Form):
    nickname = forms.CharField(
        label='Seu nome',
        required=False,
        max_length=40,
        widget=forms.TextInput(
            attrs={
                'autocomplete': 'nickname',
                'placeholder': 'Ex.: Ana, vizinho do 302…',
                'maxlength': '40',
                'class': 'publico-campo',
                'aria-required': 'true',
                'aria-describedby': 'feedback-publico',
            }
        ),
    )

    def __init__(self, *args, autenticado=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.autenticado = autenticado
        if autenticado:
            self.fields['nickname'].widget = forms.HiddenInput()

    def clean_nickname(self):
        if self.autenticado:
            return ''
        from apps.dashboard.models import CutucaoPublico

        valor = self.cleaned_data.get('nickname', '')
        try:
            return CutucaoPublico.normalizar_nickname(valor)
        except ValueError as erro:
            raise forms.ValidationError(str(erro)) from erro
