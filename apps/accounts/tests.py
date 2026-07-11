import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
class TestCadastro:
    def test_cadastro_valido_autentica(self, client):
        resposta = client.post(
            reverse('cadastro'),
            {
                'name': 'Ana Silva',
                'username': 'ana',
                'email': 'ana@test.local',
                'password1': 'SenhaForte123!',
                'password2': 'SenhaForte123!',
                'accepted_the_terms_of_use': True,
            },
        )
        assert resposta.status_code == 302
        assert resposta.url == reverse('dashboard:index')
        usuario = User.objects.get(username='ana')
        assert usuario.email == 'ana@test.local'
        assert usuario.name == 'Ana Silva'
        assert usuario.accepted_the_terms_of_use is True
        assert str(client.session.get('_auth_user_id')) == str(usuario.pk)

    def test_username_duplicado(self, client):
        User.objects.create_user(
            username='ana',
            email='outra@test.local',
            password='SenhaForte123!',
        )
        resposta = client.post(
            reverse('cadastro'),
            {
                'name': 'Ana',
                'username': 'ana',
                'email': 'ana@test.local',
                'password1': 'SenhaForte123!',
                'password2': 'SenhaForte123!',
                'accepted_the_terms_of_use': True,
            },
        )
        assert resposta.status_code == 200
        assert User.objects.filter(email='ana@test.local').count() == 0

    def test_sem_termos_falha(self, client):
        resposta = client.post(
            reverse('cadastro'),
            {
                'name': 'Ana',
                'username': 'ana2',
                'email': 'ana2@test.local',
                'password1': 'SenhaForte123!',
                'password2': 'SenhaForte123!',
            },
        )
        assert resposta.status_code == 200
        assert not User.objects.filter(username='ana2').exists()

    def test_pagina_cadastro_get(self, client):
        resposta = client.get(reverse('cadastro'))
        assert resposta.status_code == 200
        assert b'Criar conta' in resposta.content
