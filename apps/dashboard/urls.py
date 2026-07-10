"""
URL configuration for sonar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from apps.dashboard.views import (
    EncerrarBuzinaView,
    EnviarBuzinaView,
    PaginaChamarContatoView,
    PaginaCirculosView,
    PaginaConfiguracoesView,
    PaginaInicioView,
    ResponderBuzinaView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', PaginaInicioView.as_view(), name='index'),
    path('circulos/', PaginaCirculosView.as_view(), name='circulos'),
    path('circulos/<uuid:membro_id>/chamar/', PaginaChamarContatoView.as_view(), name='chamar_contato'),
    path('configuracoes/', PaginaConfiguracoesView.as_view(), name='configuracoes'),
    path('api/buzina/enviar/', EnviarBuzinaView.as_view(), name='enviar_buzina'),
    path('api/buzina/<uuid:buzina_id>/responder/', ResponderBuzinaView.as_view(), name='responder_buzina'),
    path('api/buzina/<uuid:buzina_id>/encerrar/', EncerrarBuzinaView.as_view(), name='encerrar_buzina'),
]
