import pytest
from django.urls import reverse
from unittest.mock import patch

from apps.accounts.models import User
from apps.dashboard.models import Buzina, MembroCirculo, StatusPresenca
from apps.dashboard.presenca import Presenca
from apps.dashboard.push_nativo import ServicoPushNativo


@pytest.fixture
def usuarios(db):
    alice = User.objects.create_user(
        username='alice',
        password='senha123',
        name='Alice',
        email='alice@test.local',
    )
    bob = User.objects.create_user(
        username='bob',
        password='senha123',
        name='Bob',
        email='bob@test.local',
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
class TestRedirecionarPerfil:
    def test_perfil_redireciona_para_chamar(self, client, membro):
        alice = membro.dono
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:perfil_contato', args=[membro.id]))
        assert resposta.status_code == 302
        assert resposta.url == reverse('dashboard:chamar_contato', args=[membro.id])

    def test_perfil_requer_login(self, client, membro):
        resposta = client.get(reverse('dashboard:perfil_contato', args=[membro.id]))
        assert resposta.status_code == 302
        assert 'login' in resposta.url


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


@pytest.fixture
def circulo_bidirecional(usuarios):
    alice, bob = usuarios
    alice_bob = MembroCirculo.objects.create(
        dono=alice,
        contato=bob,
        status=StatusPresenca.ONLINE,
    )
    bob_alice = MembroCirculo.objects.create(
        dono=bob,
        contato=alice,
        status=StatusPresenca.ONLINE,
    )
    return alice_bob, bob_alice


@pytest.mark.django_db
class TestNaoPerturbe:
    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    def test_pode_buzinar_ocupado_apenas_favorito(
        self, mock_alcancavel, usuarios, circulo_bidirecional
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = circulo_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        alice_bob.refresh_from_db()

        assert alice_bob.pode_buzinar is False

        bob_alice.eh_vip = True
        bob_alice.save(update_fields=['eh_vip'])
        assert alice_bob.pode_buzinar is True

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    def test_favoritos_mutuos_veem_online_em_nao_perturbe(
        self, mock_alcancavel, usuarios, circulo_bidirecional
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = circulo_bidirecional
        alice_bob.eh_vip = True
        bob_alice.eh_vip = True
        alice_bob.save(update_fields=['eh_vip'])
        bob_alice.save(update_fields=['eh_vip'])
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        alice_bob.refresh_from_db()

        assert alice_bob.status_para_dono() == StatusPresenca.ONLINE
        assert (
            Presenca.status_para_espectador(
                bob.id,
                alice.id,
                StatusPresenca.OCUPADO,
            )
            == StatusPresenca.ONLINE
        )

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch.object(Buzina, '_notificar')
    def test_enviar_silenciada_quando_ocupado_nao_vip(
        self,
        mock_notificar,
        mock_alcancavel,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, _ = circulo_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        alice_bob.refresh_from_db()

        buzina = Buzina.enviar(alice, bob.id, mensagem='Oi')
        assert buzina.silenciada is True
        assert buzina.lida_em is None
        mock_notificar.assert_not_called()

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch.object(Buzina, '_notificar')
    def test_enviar_normal_quando_vip_em_nao_perturbe(
        self,
        mock_notificar,
        mock_alcancavel,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = circulo_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        bob_alice.eh_vip = True
        bob_alice.save(update_fields=['eh_vip'])
        alice_bob.refresh_from_db()

        buzina = Buzina.enviar(alice, bob.id)
        assert buzina.silenciada is False
        mock_notificar.assert_called_once()

    @patch('apps.dashboard.presenca.Presenca.notificar_circulo')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=True)
    def test_api_alternar_disponibilidade(
        self, mock_conectado, mock_notificar, client, usuarios, circulo_bidirecional
    ):
        alice, _ = usuarios
        client.force_login(alice)

        resposta = client.post(
            reverse('dashboard:alternar_disponibilidade'),
            {'modo': 'nao_perturbe'},
        )
        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados['ok'] is True
        assert dados['status'] == StatusPresenca.OCUPADO
        assert MembroCirculo.objects.filter(
            contato=alice,
            status=StatusPresenca.OCUPADO,
        ).exists()

        resposta = client.post(
            reverse('dashboard:alternar_disponibilidade'),
            {'modo': 'disponivel'},
        )
        assert resposta.json()['status'] == StatusPresenca.ONLINE

    @patch.object(Buzina, '_notificar')
    @patch('apps.dashboard.presenca.Presenca.notificar_circulo')
    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=True)
    def test_fluxo_nao_perturbe_integracao(
        self,
        mock_conectado,
        mock_alcancavel,
        mock_presenca,
        mock_notificar,
        client,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = circulo_bidirecional

        client.force_login(alice)
        client.post(
            reverse('dashboard:alternar_disponibilidade'), {'modo': 'nao_perturbe'}
        )
        MembroCirculo.objects.filter(contato=alice).update(
            status=StatusPresenca.OCUPADO
        )

        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.ONLINE)
        alice_bob.refresh_from_db()
        buzina = Buzina.enviar(bob, alice.id)
        assert buzina.silenciada is True
        mock_notificar.assert_not_called()

        mock_notificar.reset_mock()
        MembroCirculo.objects.filter(dono=alice, contato=bob).update(eh_vip=True)
        buzina_vip = Buzina.enviar(bob, alice.id)
        assert buzina_vip.silenciada is False
        mock_notificar.assert_called_once()


@pytest.mark.django_db
class TestPresencaPush:
    @patch('apps.dashboard.presenca.Presenca.notificar_circulo')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=False)
    def test_push_mantem_online_sem_websocket(
        self,
        mock_conectado,
        mock_notificar,
        usuarios,
        circulo_bidirecional,
    ):
        from apps.dashboard.models import InscricaoPush

        alice, bob = usuarios
        alice_bob, _ = circulo_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OFFLINE)
        alice_bob.refresh_from_db()

        assert alice_bob.status_para_dono() == StatusPresenca.OFFLINE
        assert alice_bob.pode_buzinar is False

        InscricaoPush.objects.create(
            usuario=bob,
            endpoint='https://push.example.com/bob',
            p256dh='chave',
            auth='auth',
        )
        Presenca.sincronizar_por_push(bob.id)
        alice_bob.refresh_from_db()

        assert Presenca.esta_alcancavel(bob.id) is True
        assert alice_bob.status_para_dono() == StatusPresenca.ONLINE
        assert alice_bob.pode_buzinar is True
        assert alice_bob.status == StatusPresenca.ONLINE
        mock_notificar.assert_called()

    @patch('apps.dashboard.presenca.Presenca.notificar_circulo')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=False)
    def test_confirmar_offline_nao_apaga_quem_tem_push(
        self,
        mock_conectado,
        mock_notificar,
        usuarios,
        circulo_bidirecional,
    ):
        from apps.dashboard.models import InscricaoPush

        _, bob = usuarios
        InscricaoPush.objects.create(
            usuario=bob,
            endpoint='https://push.example.com/bob2',
            p256dh='chave',
            auth='auth',
        )
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.ONLINE)

        assert Presenca.confirmar_offline(bob.id) is False
        assert MembroCirculo.objects.filter(
            contato=bob,
            status=StatusPresenca.ONLINE,
        ).exists()

    @patch('apps.dashboard.push_nativo.ServicoPushNativo.enviar_buzina')
    @patch('apps.dashboard.push.ServicoPush.enviar_buzina')
    @patch.object(Buzina, '_notificar')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=False)
    def test_buzina_para_usuario_so_com_push(
        self,
        mock_conectado,
        mock_notificar,
        mock_push,
        mock_nativo,
        usuarios,
        circulo_bidirecional,
    ):
        from apps.dashboard.models import InscricaoPush

        alice, bob = usuarios
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OFFLINE)
        InscricaoPush.objects.create(
            usuario=bob,
            endpoint='https://push.example.com/bob3',
            p256dh='chave',
            auth='auth',
        )

        buzina = Buzina.enviar(alice, bob.id)
        assert buzina.silenciada is False
        mock_notificar.assert_called_once()
        mock_push.assert_called_once_with(buzina)


@pytest.mark.django_db
class TestPushApi:
    SUBSCRIPTION = {
        'endpoint': 'https://push.example.com/sub/abc',
        'keys': {
            'p256dh': 'BGxYx' + 'a' * 80,
            'auth': 'authkey123',
        },
    }

    def test_chave_vapid(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:push_vapid'))
        assert resposta.status_code == 200
        assert resposta.json()['chave_publica']

    def test_inscrever_e_desinscrever(self, client, usuarios):
        from apps.dashboard.models import InscricaoPush

        alice, _ = usuarios
        client.force_login(alice)

        resposta = client.post(
            reverse('dashboard:push_inscrever'),
            {
                'endpoint': self.SUBSCRIPTION['endpoint'],
                'p256dh': self.SUBSCRIPTION['keys']['p256dh'],
                'auth': self.SUBSCRIPTION['keys']['auth'],
            },
        )
        assert resposta.status_code == 200
        assert InscricaoPush.objects.filter(usuario=alice).count() == 1

        resposta = client.post(
            reverse('dashboard:push_desinscrever'),
            {'endpoint': self.SUBSCRIPTION['endpoint']},
        )
        assert resposta.status_code == 200
        assert InscricaoPush.objects.filter(usuario=alice).count() == 0

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch('apps.dashboard.push.ServicoPush.enviar_buzina')
    @patch.object(Buzina, '_notificar')
    def test_push_nao_enviado_em_buzina_silenciada(
        self,
        mock_notificar,
        mock_push,
        mock_alcancavel,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)

        buzina = Buzina.enviar(alice, bob.id)
        assert buzina.silenciada is True
        mock_push.assert_not_called()

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch('apps.dashboard.push.ServicoPush.enviar_buzina')
    @patch.object(Buzina, '_notificar')
    def test_push_enviado_em_buzina_normal(
        self,
        mock_notificar,
        mock_enviar,
        mock_alcancavel,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        buzina = Buzina.enviar(alice, bob.id)
        assert buzina.silenciada is False
        mock_enviar.assert_called_once_with(buzina)

    def test_service_worker_na_raiz(self, client):
        resposta = client.get(reverse('dashboard:service_worker'))
        assert resposta.status_code == 200
        assert 'workbox' in resposta.content.decode().lower()
        assert resposta['Service-Worker-Allowed'] == '/'


@pytest.mark.django_db
class TestPushNativoApi:
    TOKEN = 'fcm-token-exemplo-abc123'

    def test_inscrever_sem_firebase(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        with patch.object(ServicoPushNativo, 'configurado', return_value=False):
            resposta = client.post(
                reverse('dashboard:push_nativo_inscrever'),
                {'token': self.TOKEN, 'plataforma': 'android'},
            )
        assert resposta.status_code == 503

    def test_inscrever_e_desinscrever(self, client, usuarios):
        from apps.dashboard.models import InscricaoNativa

        alice, _ = usuarios
        client.force_login(alice)

        with patch.object(ServicoPushNativo, 'configurado', return_value=True):
            resposta = client.post(
                reverse('dashboard:push_nativo_inscrever'),
                {'token': self.TOKEN, 'plataforma': 'android'},
            )
        assert resposta.status_code == 200
        assert InscricaoNativa.objects.filter(usuario=alice, token=self.TOKEN).exists()

        resposta = client.post(
            reverse('dashboard:push_nativo_desinscrever'),
            {'token': self.TOKEN},
        )
        assert resposta.status_code == 200
        assert InscricaoNativa.objects.filter(usuario=alice).count() == 0

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    @patch('apps.dashboard.push_nativo.ServicoPushNativo.enviar_buzina')
    @patch('apps.dashboard.push.ServicoPush.enviar_buzina')
    @patch.object(Buzina, '_notificar')
    def test_buzina_dispara_push_nativo(
        self,
        mock_notificar,
        mock_push_web,
        mock_push_nativo,
        mock_alcancavel,
        usuarios,
        circulo_bidirecional,
    ):
        alice, bob = usuarios
        buzina = Buzina.enviar(alice, bob.id)
        mock_push_web.assert_called_once_with(buzina)
        mock_push_nativo.assert_called_once_with(buzina)
