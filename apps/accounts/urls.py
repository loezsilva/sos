from django.urls import path

from apps.accounts.views import CadastroView

urlpatterns = [
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
]
