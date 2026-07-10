import base64

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from django.core.management.base import BaseCommand
from py_vapid import Vapid


class Command(BaseCommand):
    help = 'Gera par de chaves VAPID para Web Push (cole no .env)'

    def handle(self, *args, **options):
        vapid = Vapid()
        vapid.generate_keys()
        publico = base64.urlsafe_b64encode(
            vapid.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint),
        ).decode().rstrip('=')
        privado = vapid.private_pem().decode()

        self.stdout.write('VAPID_PUBLIC_KEY=' + publico)
        self.stdout.write('VAPID_PRIVATE_KEY="' + privado.replace('\n', '\\n') + '"')
        self.stdout.write('VAPID_ADMIN_EMAIL=suporte@buzz.app')
