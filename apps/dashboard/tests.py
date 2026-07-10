import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.dashboard.models import Buzina, MembroCirculo, StatusPresenca


@pytest.fixture
def usuarios(db):
    alice = User.objects.create_user(
        username='alice', password='senha123', name='Alice', email='alice@test.local',
    )
    bob = User.objects.create_user(
        username='bob', password='senha123', name='Bob', email='bob@test.local',
    )
    return alice, bob


@pytest.fixture
def membro(usuarios):
    alice, bob = usuarios
    return MembroCirculo.objects.create(
        dono=alice,
        contato=bob,
        status=StatusPresenca.ONLINE,
    )


@pytest.fixture
def buzina_recebida(usuarios):
    alice, bob = usuarios
    return Buzina.objects.create(remetente=bob, destinatario=alice, mensagem='Oi')


@pytest.fixture
def buzina_enviada(usuarios):
    alice, bob = usuarios
    return Buzina.objects.create(
        remetente=alice,
        destinatario=bob,
        status=Buzina.Status.RESPONDIDA,
        resposta_rapida=Buzina.RespostaRapida.JA_VOU,
    )


@pytest.mark.django_db
class TestBuzinaQuerySet:
    def test_historico_de(self, usuarios, buzina_recebida, buzina_enviada):
        alice, _ = usuarios
        ids = set(Buzina.objects.historico_de(alice).values_list('id', flat=True))
        assert buzina_recebida.id in ids
        assert buzina_enviada.id in ids

    def test_entre(self, usuarios, buzina_recebida):
        alice, bob = usuarios
        assert Buzina.objects.entre(alice, bob).count() == 1

    def test_nao_lidas_de(self, usuarios, buzina_recebida, buzina_enviada):
        alice, _ = usuarios
        assert Buzina.objects.nao_lidas_de(alice).count() == 2

    def test_marcar_lidas(self, usuarios, buzina_recebida, buzina_enviada):
        alice, _ = usuarios
        atualizadas = Buzina.marcar_lidas(alice)
        assert atualizadas == 2
        assert Buzina.objects.nao_lidas_de(alice).count() == 0


@pytest.mark.django_db
class TestPerfilContatoView:
    def test_perfil_requer_login(self, client, membro):
        resposta = client.get(reverse('dashboard:perfil_contato', args=[membro.id]))
        assert resposta.status_code == 302

    def test_perfil_exibe_historico(self, client, usuarios, membro, buzina_recebida):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:perfil_contato', args=[membro.id]))
        assert resposta.status_code == 200
        assert 'Histórico de chamadas' in resposta.content.decode()
        assert 'Recebida' in resposta.content.decode()


@pytest.mark.django_db
class TestNotificacoesApi:
    def test_listar_notificacoes(self, client, usuarios, buzina_recebida):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:notificacoes'))
        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados['ok'] is True
        assert dados['nao_lidas'] == 1
        assert len(dados['itens']) == 1

    def test_marcar_lidas(self, client, usuarios, buzina_recebida):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.post(reverse('dashboard:marcar_notificacoes_lidas'))
        assert resposta.status_code == 200
        assert resposta.json()['nao_lidas'] == 0
