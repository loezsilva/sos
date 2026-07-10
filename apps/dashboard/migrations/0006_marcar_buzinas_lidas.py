from django.db import migrations
from django.utils import timezone


def marcar_buzinas_antigas_como_lidas(apps, schema_editor):
    Buzina = apps.get_model('dashboard', 'Buzina')
    Buzina.objects.filter(lida_em__isnull=True).update(lida_em=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_buzina_lida_em'),
    ]

    operations = [
        migrations.RunPython(marcar_buzinas_antigas_como_lidas, migrations.RunPython.noop),
    ]
