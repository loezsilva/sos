from django.urls import path

from apps.dashboard.views import (
    AlternarDisponibilidadeView,
    AlternarFavoritoView,
    EncerrarBuzinaView,
    EnviarBuzinaFavoritosView,
    EnviarBuzinaView,
    MarcarNotificacoesLidasView,
    NotificacoesView,
    PaginaChamarContatoView,
    PaginaCirculosView,
    PaginaConfiguracoesView,
    PaginaInicioView,
    RedirecionarPerfilParaChamarView,
    ResponderBuzinaView,
)

app_name = 'dashboard'

urlpatterns = [
    path('', PaginaInicioView.as_view(), name='index'),
    path('circulos/', PaginaCirculosView.as_view(), name='circulos'),
    path('circulos/<uuid:membro_id>/', RedirecionarPerfilParaChamarView.as_view(), name='perfil_contato'),
    path('circulos/<uuid:membro_id>/chamar/', PaginaChamarContatoView.as_view(), name='chamar_contato'),
    path('configuracoes/', PaginaConfiguracoesView.as_view(), name='configuracoes'),
    path('api/disponibilidade/', AlternarDisponibilidadeView.as_view(), name='alternar_disponibilidade'),
    path('api/buzina/enviar/', EnviarBuzinaView.as_view(), name='enviar_buzina'),
    path('api/buzina/enviar-favoritos/', EnviarBuzinaFavoritosView.as_view(), name='enviar_buzina_favoritos'),
    path('api/buzina/<uuid:buzina_id>/responder/', ResponderBuzinaView.as_view(), name='responder_buzina'),
    path('api/buzina/<uuid:buzina_id>/encerrar/', EncerrarBuzinaView.as_view(), name='encerrar_buzina'),
    path('api/membros/<uuid:membro_id>/favorito/', AlternarFavoritoView.as_view(), name='alternar_favorito'),
    path('api/notificacoes/', NotificacoesView.as_view(), name='notificacoes'),
    path('api/notificacoes/marcar-lidas/', MarcarNotificacoesLidasView.as_view(), name='marcar_notificacoes_lidas'),
]
