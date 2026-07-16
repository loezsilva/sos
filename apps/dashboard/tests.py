import pytest
from django.test import Client
from django.urls import reverse
from unittest.mock import patch

from apps.accounts.models import User
from apps.dashboard.models import (
    Buzina,
    CanalPublico,
    ConviteCirculo,
    CutucaoPublico,
    MembroCirculo,
    StatusPresenca,
)
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
def proximos_bidirecional(usuarios):
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
        self, mock_alcancavel, usuarios, proximos_bidirecional
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = proximos_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        alice_bob.refresh_from_db()

        assert alice_bob.pode_buzinar is False

        bob_alice.eh_vip = True
        bob_alice.save(update_fields=['eh_vip'])
        assert alice_bob.pode_buzinar is True

    @patch('apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True)
    def test_favoritos_mutuos_veem_online_em_nao_perturbe(
        self, mock_alcancavel, usuarios, proximos_bidirecional
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = proximos_bidirecional
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
        proximos_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, _ = proximos_bidirecional
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
        proximos_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = proximos_bidirecional
        MembroCirculo.objects.filter(contato=bob).update(status=StatusPresenca.OCUPADO)
        bob_alice.eh_vip = True
        bob_alice.save(update_fields=['eh_vip'])
        alice_bob.refresh_from_db()

        buzina = Buzina.enviar(alice, bob.id)
        assert buzina.silenciada is False
        mock_notificar.assert_called_once()

    @patch('apps.dashboard.presenca.Presenca.notificar_proximos')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=True)
    def test_api_alternar_disponibilidade(
        self, mock_conectado, mock_notificar, client, usuarios, proximos_bidirecional
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
    @patch('apps.dashboard.presenca.Presenca.notificar_proximos')
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
        proximos_bidirecional,
    ):
        alice, bob = usuarios
        alice_bob, bob_alice = proximos_bidirecional

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
    @patch('apps.dashboard.presenca.Presenca.notificar_proximos')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=False)
    def test_push_mantem_online_sem_websocket(
        self,
        mock_conectado,
        mock_notificar,
        usuarios,
        proximos_bidirecional,
    ):
        from apps.dashboard.models import InscricaoPush

        alice, bob = usuarios
        alice_bob, _ = proximos_bidirecional
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

    @patch('apps.dashboard.presenca.Presenca.notificar_proximos')
    @patch('apps.dashboard.presenca.Presenca.esta_conectado', return_value=False)
    def test_confirmar_offline_nao_apaga_quem_tem_push(
        self,
        mock_conectado,
        mock_notificar,
        usuarios,
        proximos_bidirecional,
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
        proximos_bidirecional,
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
        proximos_bidirecional,
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
        proximos_bidirecional,
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

    def test_assinatura_sonora_nativa(self):
        from pathlib import Path

        assert ServicoPushNativo.SOM_ASSINATURA == 'buzina.wav'
        raiz = Path(__file__).resolve().parents[2]
        sons = raiz / 'static' / 'sounds'
        for nome in (
            'buzina.wav',
            'cutuca_recebido.wav',
            'cutuca_sainte.wav',
            'cutuca_resposta.wav',
            'cutuca_encerrar.wav',
        ):
            assert (sons / nome).is_file()
        assert (
            raiz
            / 'mobile'
            / 'android'
            / 'app'
            / 'src'
            / 'main'
            / 'res'
            / 'raw'
            / 'buzina.wav'
        ).is_file()

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
        proximos_bidirecional,
    ):
        alice, bob = usuarios
        buzina = Buzina.enviar(alice, bob.id)
        mock_push_web.assert_called_once_with(buzina)
        mock_push_nativo.assert_called_once_with(buzina)


@pytest.mark.django_db
class TestConviteCirculo:
    def test_aceitar_cria_membros_mutuos(self, client, usuarios):
        alice, bob = usuarios
        convite = ConviteCirculo.enviar(alice, bob)
        client.force_login(bob)
        resposta = client.post(
            reverse('dashboard:responder_convite', kwargs={'convite_id': convite.id}),
            {'acao': 'aceitar'},
        )
        assert resposta.status_code == 302
        assert MembroCirculo.objects.filter(dono=alice, contato=bob).exists()
        assert MembroCirculo.objects.filter(dono=bob, contato=alice).exists()

    def test_recusar_nao_cria_membros(self, client, usuarios):
        alice, bob = usuarios
        convite = ConviteCirculo.enviar(alice, bob)
        client.force_login(bob)
        client.post(
            reverse('dashboard:responder_convite', kwargs={'convite_id': convite.id}),
            {'acao': 'recusar'},
        )
        assert not MembroCirculo.objects.filter(dono=alice, contato=bob).exists()
        convite.refresh_from_db()
        assert convite.status == 'recusado'

    def test_convidar_por_username(self, client, usuarios):
        alice, bob = usuarios
        client.force_login(alice)
        resposta = client.post(
            reverse('dashboard:convidar_username'),
            {'username': 'bob'},
        )
        assert resposta.status_code == 302
        assert ConviteCirculo.objects.filter(
            remetente=alice, destinatario=bob, status='pendente'
        ).exists()

    def test_conectar_nao_permite_self(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(
            reverse('dashboard:conectar_usuario', kwargs={'username': 'alice'})
        )
        assert resposta.status_code == 302
        assert resposta.url == reverse('dashboard:proximos')

    def test_meu_qr_retorna_png(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:meu_qr'))
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'image/png'
        assert resposta.content[:8] == b'\x89PNG\r\n\x1a\n'

    def test_compartilhamento_fica_no_modal_de_qr(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)

        resposta = client.get(reverse('dashboard:proximos'))
        html = resposta.content.decode()

        assert 'id="modal-meu-qr"' in html
        assert 'id="painel-cutucar"' in html
        assert 'id="painel-conectar"' in html
        assert 'Receber cutucões sem conexão' not in html


@pytest.mark.django_db
class TestLandingVendas:
    def test_anonimo_ve_landing(self, client):
        resposta = client.get(reverse('dashboard:index'))
        assert resposta.status_code == 200
        html = resposta.content.decode()
        assert 'Criar conta' in html
        assert 'Chame a atenção' in html
        assert 'Perguntas frequentes' in html
        assert 'home_app_logo' not in html
        assert reverse('cadastro') in html or '/contas/cadastro/' in html
        assert 'Criar conta grátis' not in html

    def test_autenticado_ve_dashboard(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:index'))
        assert resposta.status_code == 200
        html = resposta.content.decode()
        assert 'Criar conta grátis' not in html
        assert 'landing-fade' not in html
        assert 'home_app_logo' in html


@pytest.mark.django_db
class TestCanalPublico:
    def test_criar_e_regenerar(self, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        chave = canal.chave
        canal.regenerar()
        assert canal.chave != chave
        assert canal.ativo is True
        assert CanalPublico.ativo_por_chave(chave) is None

    def test_desativar_retorna_404(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        canal.desativar()
        resposta = client.get(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        assert resposta.status_code == 404

    def test_normalizar_nickname(self):
        assert CutucaoPublico.normalizar_nickname('  Ana  Maria ') == 'Ana Maria'
        with pytest.raises(ValueError):
            CutucaoPublico.normalizar_nickname('a')
        with pytest.raises(ValueError):
            CutucaoPublico.normalizar_nickname('x' * 41)
        with pytest.raises(ValueError):
            CutucaoPublico.normalizar_nickname('Visitante\u202e')

    def test_nome_publico_nao_expoe_username(self, usuarios):
        alice, _ = usuarios
        alice.name = ''
        alice.save(update_fields=['name'])
        canal = CanalPublico.obter_ou_criar_para(alice)

        assert canal.nome_publico == 'alguém'
        assert alice.username not in canal.nome_publico

    def test_impede_proprio_canal(self, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        with pytest.raises(ValueError):
            CutucaoPublico.enviar(canal, remetente=alice)


@pytest.mark.django_db
class TestPaginaCutucarPublico:
    def test_get_anonimo(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        resposta = client.get(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        assert resposta.status_code == 200
        html = resposta.content.decode()
        assert 'Alice' in html
        assert 'nickname' in html or 'Seu nome' in html
        assert alice.email not in html
        assert f'@{alice.username}' not in html
        assert 'css/app.css' in html

    def test_get_autenticado_sem_nickname(self, client, usuarios):
        alice, bob = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        client.force_login(bob)
        resposta = client.get(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        assert resposta.status_code == 200
        html = resposta.content.decode()
        assert 'Como quer ser chamado' not in html
        assert 'Bob' in html

    def test_post_anonimo(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            resposta = client.post(
                url,
                {'nickname': 'Visitante'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            )
        assert resposta.status_code == 200
        dados = resposta.json()
        assert dados['ok'] is True
        cutucao = CutucaoPublico.objects.get()
        assert cutucao.nickname == 'Visitante'
        assert cutucao.remetente_id is None
        assert client.session.get('cutucao_publico_nickname') == 'Visitante'

    def test_post_autenticado_ignora_nickname(self, client, usuarios):
        alice, bob = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        client.force_login(bob)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            resposta = client.post(
                url,
                {'nickname': 'Fake'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            )
        assert resposta.status_code == 200
        cutucao = CutucaoPublico.objects.get()
        assert cutucao.remetente_id == bob.id
        assert cutucao.nickname == ''
        assert cutucao.nome_exibicao == 'Bob'

    def test_post_proprio_link(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        client.force_login(alice)
        resposta = client.post(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave}),
            {},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_ACCEPT='application/json',
        )
        assert resposta.status_code == 400
        assert CutucaoPublico.objects.count() == 0

    def test_csrf_obrigatorio(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        client.handler.enforce_csrf_checks = True
        resposta = client.post(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave}),
            {'nickname': 'X'},
        )
        assert resposta.status_code == 403

    def test_rate_limit(self, client, usuarios, settings):
        settings.CUTUCAO_PUBLICO_MAX_POR_MINUTO = 2
        settings.CUTUCAO_PUBLICO_COOLDOWN_SEGUNDOS = 0
        settings.CUTUCAO_PUBLICO_CONFIAR_X_FORWARDED_FOR = False
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            for indice in range(2):
                resposta = client.post(
                    url,
                    {'nickname': 'Spam'},
                    HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                    HTTP_ACCEPT='application/json',
                    HTTP_X_FORWARDED_FOR=f'198.51.100.{indice}',
                )
                assert resposta.status_code == 200
            resposta = client.post(
                url,
                {'nickname': 'Spam'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
                HTTP_X_FORWARDED_FOR='203.0.113.50',
            )

        assert resposta.status_code == 429
        assert resposta.json()['codigo'] == 'rate_limit'
        assert CutucaoPublico.objects.count() == 2

    def test_qr_publico_png(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:qr_publico'))
        assert resposta.status_code == 200
        assert resposta['Content-Type'] == 'image/png'

    def test_qr_publico_inativo_retorna_404(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        canal.desativar()
        client.force_login(alice)

        assert client.get(reverse('dashboard:qr_publico')).status_code == 404

    def test_regenerar_invalida_url(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        canal = CanalPublico.obter_ou_criar_para(alice)
        antiga = canal.chave
        client.post(
            reverse('dashboard:gerenciar_canal_publico'),
            {'acao': 'regenerar'},
        )
        canal.refresh_from_db()
        assert canal.chave != antiga
        assert (
            client.get(
                reverse('dashboard:cutucar_publico', kwargs={'chave': antiga})
            ).status_code
            == 404
        )

    def test_gerenciar_canal_ajax_retorna_estado_sem_redirecionar(
        self, client, usuarios
    ):
        alice, _ = usuarios
        client.force_login(alice)
        canal = CanalPublico.obter_ou_criar_para(alice)

        resposta = client.post(
            reverse('dashboard:gerenciar_canal_publico'),
            {'acao': 'desativar'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
            HTTP_ACCEPT='application/json',
        )

        canal.refresh_from_db()
        assert resposta.status_code == 200
        assert resposta.json()['ativo'] is False
        assert canal.ativo is False


@pytest.mark.django_db
class TestCutucaoPublicoEntrega:
    def test_payload_e_atividades(self, client, usuarios):
        alice, bob = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        with (
            patch.object(CutucaoPublico, '_notificar') as notificar,
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico') as push_web,
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ) as push_nat,
        ):
            cutucao = CutucaoPublico.enviar(canal, nickname='Lia')
        notificar.assert_called_once()
        push_web.assert_called_once_with(cutucao)
        push_nat.assert_called_once_with(cutucao)
        payload = cutucao.payload_recebida()
        assert payload['tipo'] == 'cutucao_publico_recebido'
        assert payload['origem_publica'] is True
        assert payload['remetente_nome'] == 'Lia'

        client.force_login(alice)
        resposta = client.get(reverse('dashboard:notificacoes'))
        dados = resposta.json()
        assert any(i.get('origem_publica') for i in dados['itens'])
        assert dados['nao_lidas'] >= 1

    def test_cutucao_publico_entra_no_catch_up(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        cutucao = CutucaoPublico.objects.create(
            canal=canal,
            destinatario=alice,
            nickname='Lia',
        )
        client.force_login(alice)

        resposta = client.get(reverse('dashboard:buzinas_pendentes'))

        assert resposta.status_code == 200
        assert resposta.json()['pendentes'] == [cutucao.payload_recebida()]

    def test_dispensar_remove_cutucao_do_catch_up(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        cutucao = CutucaoPublico.objects.create(
            canal=canal,
            destinatario=alice,
            nickname='Lia',
        )
        client.force_login(alice)

        resposta = client.post(
            reverse('dashboard:dispensar_cutucao_publico', args=[cutucao.id])
        )

        assert resposta.status_code == 200
        assert CutucaoPublico.pendentes_para(alice).count() == 0

    def test_marcar_atividades_publicas_como_lidas(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        cutucao = CutucaoPublico.objects.create(
            canal=canal,
            destinatario=alice,
            nickname='Lia',
        )
        client.force_login(alice)

        resposta = client.post(reverse('dashboard:marcar_notificacoes_lidas'))

        cutucao.refresh_from_db()
        assert resposta.status_code == 200
        assert cutucao.lida_em is not None

    def test_falha_de_push_nao_descarta_envio(self, client, usuarios, settings):
        settings.CUTUCAO_PUBLICO_COOLDOWN_SEGUNDOS = 0
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})

        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch(
                'apps.dashboard.push.ServicoPush.enviar_cutucao_publico',
                side_effect=RuntimeError('push indisponível'),
            ),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            resposta = client.post(
                url,
                {'nickname': 'Lia'},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            )

        assert resposta.status_code == 200
        assert CutucaoPublico.objects.filter(nickname='Lia').count() == 1


@pytest.mark.django_db
class TestRespostaCutucaoPublico:
    def _enviar(self, client, canal, nickname='Visitante'):
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            resposta = client.post(
                url,
                {'nickname': nickname},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            )
        return resposta

    def test_post_retorna_token_e_autoriza_sessao(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        resposta = self._enviar(client, canal)
        dados = resposta.json()
        cutucao = CutucaoPublico.objects.get()

        assert dados['ok'] is True
        assert dados['cutucao_id'] == str(cutucao.id)
        assert dados['token']
        assert cutucao.conferir_token(dados['token'])
        assert cutucao.status == CutucaoPublico.Status.PENDENTE
        assert str(cutucao.id) in client.session.get('cutucao_publico_tokens', {})

    def test_status_sem_autorizacao_retorna_404(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        cutucao = CutucaoPublico.objects.create(
            canal=canal,
            destinatario=alice,
            nickname='Lia',
            token_visita=CutucaoPublico.hash_token('segredo'),
        )
        resposta = client.get(
            reverse('dashboard:status_cutucao_publico', args=[cutucao.id])
        )
        assert resposta.status_code == 404

    def test_status_com_token_na_sessao(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        envio = self._enviar(client, canal).json()
        resposta = client.get(
            reverse('dashboard:status_cutucao_publico', args=[envio['cutucao_id']])
        )
        assert resposta.status_code == 200
        assert resposta.json()['pendente'] is True

    def test_status_com_token_query(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        token = 'token-visita-xyz'
        cutucao = CutucaoPublico.objects.create(
            canal=canal,
            destinatario=alice,
            nickname='Lia',
            token_visita=CutucaoPublico.hash_token(token),
        )
        outro = Client()
        resposta = outro.get(
            reverse('dashboard:status_cutucao_publico', args=[cutucao.id]),
            {'token': token},
        )
        assert resposta.status_code == 200
        assert resposta.json()['status'] == 'pendente'

    def test_cancelar_pelo_visitante(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        envio = self._enviar(client, canal).json()
        with patch.object(CutucaoPublico, '_notificar') as notificar:
            resposta = client.post(
                reverse(
                    'dashboard:encerrar_cutucao_publico',
                    args=[envio['cutucao_id']],
                ),
                {'motivo': 'usuario', 'token': envio['token']},
            )
        cutucao = CutucaoPublico.objects.get(id=envio['cutucao_id'])
        assert resposta.status_code == 200
        assert cutucao.status == CutucaoPublico.Status.CANCELADA
        assert notificar.called

    def test_timeout_marca_perdida(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        envio = self._enviar(client, canal).json()
        with patch.object(CutucaoPublico, '_notificar'):
            resposta = client.post(
                reverse(
                    'dashboard:encerrar_cutucao_publico',
                    args=[envio['cutucao_id']],
                ),
                {'motivo': 'timeout', 'token': envio['token']},
            )
        assert resposta.status_code == 200
        assert resposta.json()['status'] == 'perdida'

    def test_responder_rapida(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        envio = self._enviar(client, canal).json()
        client.force_login(alice)
        with patch.object(CutucaoPublico, '_notificar'):
            resposta = client.post(
                reverse(
                    'dashboard:responder_cutucao_publico',
                    args=[envio['cutucao_id']],
                ),
                {'resposta_rapida': 'ja_vou'},
            )
        cutucao = CutucaoPublico.objects.get(id=envio['cutucao_id'])
        assert resposta.status_code == 200
        assert cutucao.status == CutucaoPublico.Status.RESPONDIDA
        assert cutucao.resposta_rapida == 'ja_vou'

        client.logout()
        status = client.get(
            reverse('dashboard:status_cutucao_publico', args=[envio['cutucao_id']]),
            {'token': envio['token']},
        )
        assert status.json()['resposta_rotulo'] == 'Já vou'
        assert status.json()['pendente'] is False

    def test_corrida_resposta_e_cancelamento(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        envio = self._enviar(client, canal).json()
        client.force_login(alice)
        with patch.object(CutucaoPublico, '_notificar'):
            ok_resposta = client.post(
                reverse(
                    'dashboard:responder_cutucao_publico',
                    args=[envio['cutucao_id']],
                ),
                {'resposta_rapida': 'ocupado'},
            )
            ok_cancel = client.post(
                reverse(
                    'dashboard:encerrar_cutucao_publico',
                    args=[envio['cutucao_id']],
                ),
                {'motivo': 'usuario', 'token': envio['token']},
            )
        cutucao = CutucaoPublico.objects.get(id=envio['cutucao_id'])
        assert ok_resposta.status_code == 200
        assert cutucao.status == CutucaoPublico.Status.RESPONDIDA
        assert ok_cancel.json()['ja_encerrada'] is True

    def test_remetente_autenticado_consulta_sem_token(self, client, usuarios):
        alice, bob = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        client.force_login(bob)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            envio = client.post(
                url,
                {},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            ).json()

        session = client.session
        session.pop('cutucao_publico_tokens', None)
        session.save()

        status = client.get(
            reverse('dashboard:status_cutucao_publico', args=[envio['cutucao_id']])
        )
        assert status.status_code == 200
        assert status.json()['pendente'] is True

    def test_refresh_recupera_chamada_pendente(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        self._enviar(client, canal)
        pagina = client.get(
            reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        )
        html = pagina.content.decode()
        assert 'painel-chamada-publico' in html
        assert 'data-pendente="1"' in html
        assert 'Cancelar' in html


@pytest.mark.django_db
class TestLocalizacaoCutucao:
    def test_normalizar_coordenadas_validas(self):
        from apps.dashboard.models import normalizar_coordenadas

        dados = normalizar_coordenadas('-23.55052', '-46.633308', '12.5')
        assert dados['latitude']
        assert dados['longitude']
        assert dados['precisao_metros']

    def test_coordenadas_invalidas(self):
        from apps.dashboard.models import normalizar_coordenadas
        import pytest as pt

        with pt.raises(ValueError):
            normalizar_coordenadas('999', '0')

    def test_buzina_com_localizacao(self, usuarios, proximos_bidirecional):
        alice, bob = usuarios
        with (
            patch(
                'apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True
            ),
            patch('apps.dashboard.push.ServicoPush.enviar_buzina'),
            patch('apps.dashboard.push_nativo.ServicoPushNativo.enviar_buzina'),
            patch.object(Buzina, '_notificar'),
        ):
            buzina = Buzina.enviar(
                alice,
                bob.id,
                latitude='-23.55052',
                longitude='-46.633308',
                precisao_metros='10',
            )
        payload = buzina.payload_recebida()
        assert payload['tem_localizacao'] is True
        assert 'maps.google.com' in payload['mapa_url']
        assert buzina.latitude is not None

    def test_cutucao_publico_com_localizacao(self, client, usuarios):
        alice, _ = usuarios
        canal = CanalPublico.obter_ou_criar_para(alice)
        url = reverse('dashboard:cutucar_publico', kwargs={'chave': canal.chave})
        with (
            patch.object(CutucaoPublico, '_notificar'),
            patch('apps.dashboard.push.ServicoPush.enviar_cutucao_publico'),
            patch(
                'apps.dashboard.push_nativo.ServicoPushNativo.enviar_cutucao_publico'
            ),
        ):
            resposta = client.post(
                url,
                {
                    'nickname': 'Lia',
                    'latitude': '-23.55',
                    'longitude': '-46.63',
                },
                HTTP_X_REQUESTED_WITH='XMLHttpRequest',
                HTTP_ACCEPT='application/json',
            )
        assert resposta.status_code == 200
        cutucao = CutucaoPublico.objects.get()
        assert cutucao.latitude is not None
        assert cutucao.payload_recebida()['tem_localizacao'] is True

    def test_coords_invalidas_nao_bloqueiam_envio(
        self, client, usuarios, proximos_bidirecional
    ):
        alice, bob = usuarios
        client.force_login(alice)
        with (
            patch(
                'apps.dashboard.presenca.Presenca.esta_alcancavel', return_value=True
            ),
            patch('apps.dashboard.push.ServicoPush.enviar_buzina'),
            patch('apps.dashboard.push_nativo.ServicoPushNativo.enviar_buzina'),
            patch.object(Buzina, '_notificar'),
        ):
            resposta = client.post(
                reverse('dashboard:enviar_buzina'),
                {
                    'destinatario_id': str(bob.id),
                    'latitude': '999',
                    'longitude': '0',
                },
            )
        assert resposta.status_code == 200
        assert resposta.json()['ok'] is True
        assert Buzina.objects.get().latitude is None

    def test_copy_contatos_na_nav(self, client, usuarios):
        alice, _ = usuarios
        client.force_login(alice)
        resposta = client.get(reverse('dashboard:proximos'))
        html = resposta.content.decode()
        assert 'Contatos' in html
        assert 'Meus contatos' in html
        assert 'Meus próximos' not in html
