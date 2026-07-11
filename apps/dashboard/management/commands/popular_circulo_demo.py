from django.core.management.base import BaseCommand

from apps.accounts.models import User
from apps.dashboard.models import MembroCirculo, StatusPresenca


class Command(BaseCommand):
    help = 'Popula círculos mútuos de demonstração (status inicial offline).'

    def handle(self, *args, **options):
        contatos_demo = [
            ('elena', 'Elena Rostova', True),
            ('marcus', 'Marcus Vance', False),
            ('sarah', 'Sarah Jenkins', False),
            ('alex', 'Alex Thorne', False),
        ]

        # Donos: primeiro usuário + admin (se existir)
        donos = []
        primeiro = User.objects.order_by('date_joined').first()
        if primeiro:
            donos.append(primeiro)
        admin = User.objects.filter(username='admin').first()
        if admin and admin not in donos:
            donos.append(admin)

        if not donos:
            self.stderr.write('Nenhum usuário encontrado. Crie um usuário primeiro.')
            return

        contatos = []
        for username, nome, vip in contatos_demo:
            contato, criado = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@buzz.demo',
                    'name': nome,
                    'is_active': True,
                },
            )
            contato.set_password('demo1234')
            contato.name = nome
            contato.save()
            contatos.append((contato, vip))

        for dono in donos:
            for contato, vip in contatos:
                if contato.pk == dono.pk:
                    continue
                MembroCirculo.objects.update_or_create(
                    dono=dono,
                    contato=contato,
                    defaults={'status': StatusPresenca.OFFLINE, 'eh_vip': vip},
                )
                MembroCirculo.objects.update_or_create(
                    dono=contato,
                    contato=dono,
                    defaults={'status': StatusPresenca.OFFLINE, 'eh_vip': False},
                )
                self.stdout.write(f'  {dono.username} ↔ {contato.username}')

            # Donos também se veem entre si (ex.: demo ↔ admin)
            for outro in donos:
                if outro.pk == dono.pk:
                    continue
                MembroCirculo.objects.update_or_create(
                    dono=dono,
                    contato=outro,
                    defaults={'status': StatusPresenca.OFFLINE, 'eh_vip': False},
                )

        self.stdout.write(
            self.style.SUCCESS('Círculos mútuos populados (presença sobe no login).')
        )
