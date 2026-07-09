from typing import OrderedDict
import requests
import os
import uuid
from django.core.files import File

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework import pagination
from django.contrib.auth.mixins import PermissionRequiredMixin


class CheckHasPermission(PermissionRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not self.has_permission():
            messages.error(request, "Você não tem permissão para acessar essa página.")
            return redirect(settings.LOGOUT_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)


class SimpleAPIPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ('page_size', self.get_page_size(self.request)),
                    ('count', self.page.paginator.count),
                    ('next', self.get_next_link()),
                    ('previous', self.get_previous_link()),
                    ('results', data),
                ]
            )
        )


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


def download_file(url, filename_prefix=''):
    resposta = requests.get(url)

    if resposta.status_code == 200:
        filename = (
            filename_prefix + str(uuid.uuid4()) + url[-4:]
        )  # Obtém o nome do arquivo a partir da URL

        os.makedirs('tmp', exist_ok=True)

        file_path = os.path.join(
            'tmp', filename
        )  # Substitua 'caminho_para_salvar' pelo caminho desejado para salvar o arquivo

        # Salva o arquivo no caminho especificado
        with open(file_path, 'wb') as file:
            file.write(resposta.content)

        # os.remove(file_path)

        return File(open(file_path, 'rb'))

    else:
        print("Falha ao baixar o arquivo. Código de status:", resposta.status_code)

    return None
