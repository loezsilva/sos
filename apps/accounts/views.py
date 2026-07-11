from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.accounts.forms import CadastroForm


class CadastroView(CreateView):
    form_class = CadastroForm
    template_name = 'registration/cadastro.html'
    success_url = reverse_lazy('dashboard:index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            from django.shortcuts import redirect

            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        resposta = super().form_valid(form)
        login(
            self.request,
            self.object,
            backend='apps.accounts.backends.EmailOrUsernameModelBackend',
        )
        return resposta
