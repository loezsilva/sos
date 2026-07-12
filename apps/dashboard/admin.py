from django.contrib import admin

from apps.dashboard.models import (
    Buzina,
    CanalPublico,
    ConviteCirculo,
    CutucaoPublico,
    MembroCirculo,
)


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


@admin.register(CanalPublico)
class CanalPublicoAdmin(admin.ModelAdmin):
    list_display = ('proprietario', 'chave', 'ativo', 'regenerado_em', 'updated_at')
    list_filter = ('ativo',)
    search_fields = ('proprietario__username', 'proprietario__name')
    autocomplete_fields = ('proprietario',)
    readonly_fields = ('chave', 'regenerado_em')


@admin.register(CutucaoPublico)
class CutucaoPublicoAdmin(admin.ModelAdmin):
    list_display = (
        'nickname',
        'remetente',
        'destinatario',
        'status',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = (
        'nickname',
        'remetente__username',
        'destinatario__username',
    )
    autocomplete_fields = ('canal', 'destinatario', 'remetente')
