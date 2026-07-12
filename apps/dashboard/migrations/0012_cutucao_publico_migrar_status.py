from django.db import migrations


def migrar_status(apps, schema_editor):
    CutucaoPublico = apps.get_model('dashboard', 'CutucaoPublico')
    CutucaoPublico.objects.filter(status='enviado').update(status='pendente')
    CutucaoPublico.objects.filter(status='dispensado').update(status='recusada')


def reverter_status(apps, schema_editor):
    CutucaoPublico = apps.get_model('dashboard', 'CutucaoPublico')
    CutucaoPublico.objects.filter(status='pendente').update(status='enviado')
    CutucaoPublico.objects.filter(status='recusada').update(status='dispensado')


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0011_cutucao_publico_resposta_cancelamento'),
    ]

    operations = [
        migrations.RunPython(migrar_status, reverter_status),
    ]
