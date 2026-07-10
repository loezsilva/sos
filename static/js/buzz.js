(function () {
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  const TEMPO_MAXIMO_ESPERA_MS = 45000;
  let buzinaRecebida = null;
  let buzinaSainte = null;
  let socket = null;
  let timeoutFecharChamada = null;
  let timeoutChamada = null;

  function obterCookie(nome) {
    return document.cookie.match(new RegExp(`${nome}=([^;]+)`))?.[1];
  }

  async function postForm(url, dados) {
    const form = new FormData();
    Object.entries(dados).forEach(([chave, valor]) => form.append(chave, valor));
    const resposta = await fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': obterCookie('csrftoken') || csrfToken },
      body: form,
    });
    return resposta.json();
  }

  function vibrar() {
    if (navigator.vibrate) navigator.vibrate([200, 100, 200, 100, 400]);
  }

  function bloquearScroll() {
    document.body.classList.add('overflow-hidden');
  }

  function liberarScroll() {
    document.body.classList.remove('overflow-hidden');
  }

  function definirAvatar(elemento, nome, urlAvatar) {
    if (!elemento) return;
    if (urlAvatar) {
      elemento.innerHTML = `<img class="w-full h-full object-cover" src="${urlAvatar}" alt="${nome}">`;
    } else {
      elemento.innerHTML = '<span class="material-symbols-outlined text-outline text-6xl">person</span>';
    }
  }

  function limparTimerChamada() {
    clearTimeout(timeoutChamada);
    timeoutChamada = null;
  }

  function mostrarAlertaRecebido(dados) {
    buzinaRecebida = dados.buzina_id;
    const alerta = document.getElementById('alerta-buzina');
    const nome = document.getElementById('alerta-remetente');
    const avatar = document.getElementById('alerta-avatar');
    const mensagem = document.getElementById('alerta-mensagem');

    if (!alerta || !nome) return;

    nome.textContent = dados.remetente_nome;
    definirAvatar(avatar, dados.remetente_nome, dados.remetente_avatar);

    if (mensagem) {
      const texto = (dados.mensagem || '').trim();
      if (texto) {
        mensagem.textContent = texto;
        mensagem.classList.remove('hidden');
      } else {
        mensagem.textContent = '';
        mensagem.classList.add('hidden');
      }
    }

    alerta.classList.remove('hidden');
    bloquearScroll();
    vibrar();
  }

  function ocultarAlertaRecebido() {
    document.getElementById('alerta-buzina')?.classList.add('hidden');
    if (!document.getElementById('chamada-sainte')?.classList.contains('hidden')) return;
    liberarScroll();
    buzinaRecebida = null;
  }

  function mostrarChamadaSainte(dados) {
    buzinaSainte = dados.buzina_id;
    const tela = document.getElementById('chamada-sainte');
    const titulo = document.getElementById('chamada-titulo');
    const subtitulo = document.getElementById('chamada-subtitulo');
    const destinatario = document.getElementById('chamada-destinatario');
    const mensagem = document.getElementById('chamada-mensagem');
    const respostaBox = document.getElementById('chamada-resposta');
    const respostaTexto = document.getElementById('chamada-resposta-texto');
    const encerrarLabel = document.getElementById('chamada-encerrar-label');

    if (!tela) return;

    limparTimerChamada();
    clearTimeout(timeoutFecharChamada);

    titulo.textContent = 'Buzinando...';
    subtitulo.textContent = 'Aguardando resposta';
    subtitulo.classList.add('animate-pulse', 'text-secondary');
    subtitulo.classList.remove('text-error', 'text-outline');
    destinatario.textContent = dados.destinatario_nome;
    const textoMensagem = (dados.mensagem || '').trim();
    mensagem.textContent = textoMensagem || 'chamando a atenção de';
    mensagem.classList.toggle('text-on-surface', Boolean(textoMensagem));
    mensagem.classList.toggle('text-on-surface-variant', !textoMensagem);
    mensagem.classList.remove('hidden');
    respostaBox.classList.add('hidden');
    respostaTexto.textContent = '';
    encerrarLabel.textContent = 'Encerrar';
    definirAvatar(
      document.getElementById('chamada-avatar'),
      dados.destinatario_nome,
      dados.destinatario_avatar,
    );

    tela.classList.remove('hidden');
    bloquearScroll();

    timeoutChamada = setTimeout(() => encerrarChamadaSainte('timeout'), TEMPO_MAXIMO_ESPERA_MS);
  }

  function mostrarRespostaNaChamada(dados) {
    if (!buzinaSainte || dados.buzina_id !== buzinaSainte) return;

    limparTimerChamada();

    const titulo = document.getElementById('chamada-titulo');
    const subtitulo = document.getElementById('chamada-subtitulo');
    const mensagem = document.getElementById('chamada-mensagem');
    const respostaBox = document.getElementById('chamada-resposta');
    const respostaTexto = document.getElementById('chamada-resposta-texto');
    const encerrarLabel = document.getElementById('chamada-encerrar-label');

    titulo.textContent = 'Resposta recebida';
    subtitulo.textContent = dados.destinatario_nome;
    subtitulo.classList.remove('animate-pulse', 'text-error');
    subtitulo.classList.add('text-secondary');
    mensagem.classList.add('hidden');
    respostaTexto.textContent = dados.resposta_rotulo;
    respostaBox.classList.remove('hidden');
    encerrarLabel.textContent = 'Fechar';

    if (navigator.vibrate) navigator.vibrate([100, 50, 100]);

    clearTimeout(timeoutFecharChamada);
    timeoutFecharChamada = setTimeout(ocultarChamadaSainte, 8000);
  }

  function mostrarDesfechoChamada(motivo) {
    if (!buzinaSainte) return;

    limparTimerChamada();

    const titulo = document.getElementById('chamada-titulo');
    const subtitulo = document.getElementById('chamada-subtitulo');
    const mensagem = document.getElementById('chamada-mensagem');
    const respostaBox = document.getElementById('chamada-resposta');
    const respostaTexto = document.getElementById('chamada-resposta-texto');
    const encerrarLabel = document.getElementById('chamada-encerrar-label');

    const perdida = motivo === 'perdida';
    titulo.textContent = perdida ? 'Chamada perdida' : 'Chamada cancelada';
    subtitulo.textContent = perdida
      ? 'Sem resposta a tempo'
      : 'Você encerrou a chamada';
    subtitulo.classList.remove('animate-pulse', 'text-secondary');
    subtitulo.classList.add(perdida ? 'text-error' : 'text-outline');
    mensagem.classList.add('hidden');
    respostaTexto.textContent = perdida
      ? 'A pessoa não respondeu'
      : 'Chamada encerrada';
    respostaBox.classList.remove('hidden');
    encerrarLabel.textContent = 'Fechar';

    clearTimeout(timeoutFecharChamada);
    timeoutFecharChamada = setTimeout(ocultarChamadaSainte, 5000);
  }

  function ocultarChamadaSainte() {
    limparTimerChamada();
    clearTimeout(timeoutFecharChamada);
    document.getElementById('chamada-sainte')?.classList.add('hidden');
    if (document.getElementById('alerta-buzina')?.classList.contains('hidden')) {
      liberarScroll();
    }
    buzinaSainte = null;
  }

  async function encerrarChamadaSainte(motivo = 'usuario') {
    if (!buzinaSainte) {
      ocultarChamadaSainte();
      return;
    }

    const id = buzinaSainte;
    limparTimerChamada();

    // Já em desfecho (Fechar após resposta/perda): só fecha UI
    const encerrarLabel = document.getElementById('chamada-encerrar-label');
    if (encerrarLabel?.textContent === 'Fechar') {
      ocultarChamadaSainte();
      return;
    }

    await postForm(`/api/buzina/${id}/encerrar/`, { motivo });
    if (motivo === 'timeout') {
      mostrarDesfechoChamada('perdida');
    } else {
      mostrarDesfechoChamada('cancelada');
    }
  }

  function tratarBuzinaEncerrada(dados) {
    if (buzinaRecebida && dados.buzina_id === buzinaRecebida) {
      ocultarAlertaRecebido();
    }
    if (buzinaSainte && dados.buzina_id === buzinaSainte) {
      const encerrarLabel = document.getElementById('chamada-encerrar-label');
      if (encerrarLabel?.textContent === 'Fechar') return;
      mostrarDesfechoChamada(dados.motivo);
    }
  }

  function ativarOndasChamada() {
    document.getElementById('ondas-chamada')?.classList.remove('hidden');
    const status = document.getElementById('status-chamada');
    if (status) {
      status.textContent = 'Buzinando...';
      status.className = 'font-headline-md text-headline-md text-secondary animate-pulse';
    }
  }

  async function enviarBuzina(botao) {
    const destinatarioId = botao.dataset.buzinar;
    const dados = { destinatario_id: destinatarioId };
    const campoMensagem = document.getElementById('mensagem-buzina');
    if (campoMensagem?.value.trim()) {
      dados.mensagem = campoMensagem.value.trim().slice(0, 80);
    }

    ativarOndasChamada();
    botao.disabled = true;

    const resultado = await postForm('/api/buzina/enviar/', dados);

    if (resultado.erro) {
      botao.disabled = false;
      return;
    }

    mostrarChamadaSainte({
      buzina_id: resultado.buzina_id,
      destinatario_nome: resultado.destinatario_nome || botao.dataset.buzinarNome || 'Contato',
      destinatario_avatar: resultado.destinatario_avatar || botao.dataset.buzinarAvatar || '',
      mensagem: dados.mensagem || '',
    });
  }

  async function responderBuzina(opcoes = {}) {
    if (!buzinaRecebida) return;
    await postForm(`/api/buzina/${buzinaRecebida}/responder/`, opcoes);
    ocultarAlertaRecebido();
  }

  function conectarWebSocket() {
    const protocolo = window.location.protocol === 'https:' ? 'wss' : 'ws';
    socket = new WebSocket(`${protocolo}://${window.location.host}/ws/buzz/`);

    socket.onmessage = (evento) => {
      const dados = JSON.parse(evento.data);
      if (dados.tipo === 'buzina_recebida') {
        mostrarAlertaRecebido(dados);
      } else if (dados.tipo === 'resposta_recebida') {
        mostrarRespostaNaChamada(dados);
      } else if (dados.tipo === 'buzina_encerrada') {
        tratarBuzinaEncerrada(dados);
      }
    };

    socket.onclose = () => setTimeout(conectarWebSocket, 3000);
  }

  document.addEventListener('click', (evento) => {
    const botaoBuzinar = evento.target.closest('[data-buzinar]');
    if (botaoBuzinar && !botaoBuzinar.disabled) {
      enviarBuzina(botaoBuzinar);
    }
  });

  document.getElementById('alerta-atender')?.addEventListener('click', () => responderBuzina({}));
  document.getElementById('alerta-recusar')?.addEventListener('click', () => responderBuzina({ recusar: '1' }));
  document.getElementById('chamada-encerrar')?.addEventListener('click', () => encerrarChamadaSainte('usuario'));

  document.querySelectorAll('.alerta-resposta').forEach((botao) => {
    botao.addEventListener('click', () => {
      responderBuzina({ resposta_rapida: botao.dataset.resposta });
    });
  });

  if (document.body.dataset.usuarioAutenticado === 'true') {
    conectarWebSocket();
  }
})();
