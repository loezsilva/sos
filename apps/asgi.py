import os
import django
from channels.routing import get_default_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.settings')
django.setup()

# Esta é a aplicação do Django Channels que lida com websocket e http
application = get_default_application()
