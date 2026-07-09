from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.dashboard.models import MembroCirculo, StatusPresenca


class Command(BaseCommand):
    help = 'Popula o círculo do primeiro usuário com contatos de demonstração.'

    def handle(self, *args, **options):
        dono = User.objects.order_by('date_joined').first()
        if not dono:
            self.stderr.write('Nenhum usuário encontrado. Crie um usuário primeiro.')
            return

        contatos_demo = [
            ('elena', 'Elena Rostova', StatusPresenca.ONLINE, True),
            ('marcus', 'Marcus Vance', StatusPresenca.OCUPADO, False),
            ('sarah', 'Sarah Jenkins', StatusPresenca.OFFLINE, False),
            ('alex', 'Alex Thorne', StatusPresenca.ONLINE, False),
        ]

        for username, nome, status, vip in contatos_demo:
            contato, criado = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@buzz.demo',
                    'name': nome,
                    'is_active': True,
                },
            )
            contato.set_password('demo1234')
            if criado:
                contato.save()
            else:
                contato.save(update_fields=['password'])

            membro, _ = MembroCirculo.objects.update_or_create(
                dono=dono,
                contato=contato,
                defaults={'status': status, 'eh_vip': vip},
            )
            self.stdout.write(f'  {membro.nome_exibicao} — {membro.get_status_display()}')

        self.stdout.write(self.style.SUCCESS(f'Círculo de {dono} populado com sucesso.'))
