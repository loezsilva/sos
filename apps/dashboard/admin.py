from django.contrib import admin

from apps.dashboard.models import Buzina, ConviteCirculo, MembroCirculo


@admin.register(MembroCirculo)
class MembroCirculoAdmin(admin.ModelAdmin):
    list_display = ('contato', 'dono', 'status', 'eh_vip', 'updated_at')
    list_filter = ('status', 'eh_vip')
    search_fields = ('contato__name', 'contato__username', 'dono__username')
    autocomplete_fields = ('dono', 'contato')


@admin.register(ConviteCirculo)
class ConviteCirculoAdmin(admin.ModelAdmin):
    list_display = ('remetente', 'destinatario', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('remetente__username', 'destinatario__username')
    autocomplete_fields = ('remetente', 'destinatario')


@admin.register(Buzina)
class BuzinaAdmin(admin.ModelAdmin):
    list_display = (
        'remetente',
        'destinatario',
        'status',
        'resposta_rapida',
        'created_at',
    )
    list_filter = ('status', 'resposta_rapida')
    search_fields = ('remetente__username', 'destinatario__username')
    autocomplete_fields = ('remetente', 'destinatario')
