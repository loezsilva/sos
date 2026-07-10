(function () {
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  const TEMPO_MAXIMO_ESPERA_MS = 45000;
  const CIRCUNFERENCIA_ANEL = 2 * Math.PI * 46;
  let buzinaRecebida = null;
  let buzinaSainte = null;
  let socket = null;
  let timeoutFecharChamada = null;
  let timeoutChamada = null;
  let pressionarSegurar = null;

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
    if (textoMensagem) {
      mensagem.textContent = textoMensagem;
      mensagem.classList.remove('hidden');
    } else {
      mensagem.textContent = '';
      mensagem.classList.add('hidden');
    }
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

    if (estaNaPaginaChamar()) {
      buzinaSainte = null;
      restaurarPaginaChamar();
      const status = document.getElementById('status-chamada');
      if (status) {
        status.textContent = dados.resposta_rotulo || 'Resposta recebida';
        status.className = 'font-headline-md text-headline-md text-secondary';
      }
      if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
      return;
    }

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

  function restaurarPaginaChamar() {
    document.getElementById('ondas-chamada')?.classList.add('hidden');
    const status = document.getElementById('status-chamada');
    if (status) {
      if (status.dataset.statusOriginal) status.textContent = status.dataset.statusOriginal;
      if (status.dataset.classeOriginal) status.className = status.dataset.classeOriginal;
    }
    const dica = document.getElementById('dica-segurar');
    if (dica) dica.textContent = 'Segure 2s para chamar';
    resetarAnelProgresso();
    document.querySelectorAll('[data-buzinar]').forEach((botao) => {
      if (!botao.dataset.manterDesabilitado) botao.disabled = false;
    });
  }

  function obterAnelProgresso() {
    return document.getElementById('anel-progresso-carga');
  }

  function resetarAnelProgresso() {
    const anel = obterAnelProgresso();
    if (!anel) return;
    anel.classList.remove('carregando');
    anel.style.strokeDasharray = String(CIRCUNFERENCIA_ANEL);
    anel.style.strokeDashoffset = String(CIRCUNFERENCIA_ANEL);
  }

  function atualizarAnelProgresso(progresso) {
    const anel = obterAnelProgresso();
    if (!anel) return;
    const limitado = Math.min(1, Math.max(0, progresso));
    anel.style.strokeDashoffset = String(CIRCUNFERENCIA_ANEL * (1 - limitado));
  }

  function cancelarPressionarSegurar() {
    if (!pressionarSegurar) return;
    cancelAnimationFrame(pressionarSegurar.frame);
    clearTimeout(pressionarSegurar.timer);
    pressionarSegurar = null;
    resetarAnelProgresso();
  }

  function iniciarPressionarSegurar(botao) {
    if (botao.disabled || chamadaSainteAtiva()) return;

    const segundos = Number(botao.dataset.segurarBuzina || 2);
    const duracaoMs = segundos * 1000;
    const anel = obterAnelProgresso();
    const dica = document.getElementById('dica-segurar');
    const inicio = performance.now();

    cancelarPressionarSegurar();
    if (anel) anel.classList.add('carregando');
    if (dica) dica.textContent = 'Segurando...';

    pressionarSegurar = {
      botao,
      disparado: false,
      frame: null,
      timer: null,
    };

    const tick = (agora) => {
      if (!pressionarSegurar || pressionarSegurar.disparado) return;
      const progresso = (agora - inicio) / duracaoMs;
      atualizarAnelProgresso(progresso);
      if (progresso < 1) {
        pressionarSegurar.frame = requestAnimationFrame(tick);
      }
    };

    pressionarSegurar.frame = requestAnimationFrame(tick);
    pressionarSegurar.timer = setTimeout(() => {
      if (!pressionarSegurar || pressionarSegurar.disparado) return;
      pressionarSegurar.disparado = true;
      atualizarAnelProgresso(1);
      if (navigator.vibrate) navigator.vibrate(40);
      if (dica) dica.textContent = 'Chamando...';
      enviarBuzina(botao);
      pressionarSegurar = null;
    }, duracaoMs);
  }

  function chamadaSainteAtiva() {
    return Boolean(buzinaSainte);
  }

  function ocultarChamadaSainte() {
    limparTimerChamada();
    clearTimeout(timeoutFecharChamada);
    document.getElementById('chamada-sainte')?.classList.add('hidden');
    if (document.getElementById('alerta-buzina')?.classList.contains('hidden')) {
      liberarScroll();
    }
    buzinaSainte = null;
    restaurarPaginaChamar();
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

    if (motivo === 'timeout') {
      await postForm(`/api/buzina/${id}/encerrar/`, { motivo });
      if (estaNaPaginaChamar()) {
        buzinaSainte = null;
        restaurarPaginaChamar();
        const status = document.getElementById('status-chamada');
        if (status) {
          status.textContent = 'Sem resposta';
          status.className = 'font-headline-md text-headline-md text-error';
        }
        return;
      }
      mostrarDesfechoChamada('perdida');
      return;
    }

    // Cancela já: limpa estado antes do WS para não reabrir desfecho
    buzinaSainte = null;
    await postForm(`/api/buzina/${id}/encerrar/`, { motivo: 'usuario' });
    ocultarChamadaSainte();
  }

  function tratarBuzinaEncerrada(dados) {
    if (buzinaRecebida && dados.buzina_id === buzinaRecebida) {
      ocultarAlertaRecebido();
    }
    if (buzinaSainte && dados.buzina_id === buzinaSainte) {
      const encerrarLabel = document.getElementById('chamada-encerrar-label');
      if (encerrarLabel?.textContent === 'Fechar') return;
      if (estaNaPaginaChamar()) {
        buzinaSainte = null;
        restaurarPaginaChamar();
        return;
      }
      mostrarDesfechoChamada(dados.motivo);
    }
  }

  function estaNaPaginaChamar() {
    return Boolean(document.getElementById('status-chamada'));
  }

  function ativarOndasChamada() {
    document.getElementById('ondas-chamada')?.classList.remove('hidden');
    const status = document.getElementById('status-chamada');
    if (status) {
      if (!status.dataset.statusOriginal) {
        status.dataset.statusOriginal = status.textContent.trim();
        status.dataset.classeOriginal = status.className;
      }
      status.textContent = 'Buzinando...';
      status.className = 'font-headline-md text-headline-md text-secondary animate-pulse';
    }
    const dica = document.getElementById('dica-segurar');
    if (dica) dica.textContent = 'Toque para cancelar';
  }

  async function enviarBuzina(botao) {
    // Segundo clique enquanto buzina: cancela a chamada
    if (chamadaSainteAtiva()) {
      await encerrarChamadaSainte('usuario');
      return;
    }

    const destinatarioId = botao.dataset.buzinar;
    const dados = { destinatario_id: destinatarioId };
    const campoMensagem = document.getElementById('mensagem-buzina');
    if (campoMensagem?.value.trim()) {
      dados.mensagem = campoMensagem.value.trim().slice(0, 80);
    }

    ativarOndasChamada();

    const resultado = await postForm('/api/buzina/enviar/', dados);

    if (resultado.erro) {
      restaurarPaginaChamar();
      return;
    }

    const payload = {
      buzina_id: resultado.buzina_id,
      destinatario_nome: resultado.destinatario_nome || botao.dataset.buzinarNome || 'Contato',
      destinatario_avatar: resultado.destinatario_avatar || botao.dataset.buzinarAvatar || '',
      mensagem: dados.mensagem || '',
    };

    // Na página de chamar: fica na tela e permite cancelar no 2º clique
    if (estaNaPaginaChamar()) {
      buzinaSainte = payload.buzina_id;
      limparTimerChamada();
      timeoutChamada = setTimeout(() => encerrarChamadaSainte('timeout'), TEMPO_MAXIMO_ESPERA_MS);
      return;
    }

    mostrarChamadaSainte(payload);
  }

  async function responderBuzina(opcoes = {}) {
    if (!buzinaRecebida) return;
    await postForm(`/api/buzina/${buzinaRecebida}/responder/`, opcoes);
    ocultarAlertaRecebido();
  }

  const statusConhecidos = {};

  function estilosPresenca(status) {
    const mapa = {
      online: {
        cor: 'text-secondary',
        indicador: 'bg-secondary shadow-[0_0_8px_#4cd7f6]',
        rotulo: 'Online',
      },
      ocupado: {
        cor: 'text-tertiary',
        indicador: 'bg-tertiary shadow-[0_0_8px_#ffb784]',
        rotulo: 'Ocupado',
      },
      offline: {
        cor: 'text-outline',
        indicador: 'bg-outline',
        rotulo: 'Offline',
      },
    };
    return mapa[status] || mapa.offline;
  }

  function atualizarContadorOnline() {
    const cards = document.querySelectorAll('.card-membro[data-status]');
    const contador = document.getElementById('contador-online');
    const numero = document.getElementById('contador-online-numero');
    const inicio = document.getElementById('contador-online-inicio');

    if (cards.length) {
      let online = 0;
      cards.forEach((card) => {
        if (card.dataset.status === 'online') online += 1;
      });
      if (contador && numero) {
        numero.textContent = String(online);
        contador.dataset.total = String(online);
        contador.classList.toggle('hidden', online === 0);
      }
      if (inicio) {
        inicio.textContent = `${online} online`;
        inicio.dataset.total = String(online);
      }
      return;
    }

    if (inicio) {
      const online = Object.values(statusConhecidos).filter((s) => s === 'online').length;
      const total = Object.keys(statusConhecidos).length
        ? online
        : Number(inicio.dataset.total || 0);
      inicio.textContent = `${total} online`;
      inicio.dataset.total = String(total);
    }
  }

  function atualizarCardPresenca(card, status, rotulo) {
    const estilo = estilosPresenca(status);
    card.dataset.status = status;

    const indicador = card.querySelector('.card-membro-indicador');
    const statusEl = card.querySelector('.card-membro-status');
    const bolt = card.querySelector('.card-membro-bolt');
    const link = card.querySelector('a');
    const pode = status !== 'offline';

    if (indicador) {
      indicador.className = `card-membro-indicador absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-surface-container-highest ${estilo.indicador}`;
    }
    if (statusEl) {
      statusEl.textContent = rotulo || estilo.rotulo;
      statusEl.className = `card-membro-status font-label-bold text-label-bold ${estilo.cor} mt-1`;
    }

    card.classList.toggle('opacity-75', !pode);
    card.classList.toggle('grayscale-[0.2]', !pode);
    if (link) link.classList.toggle('pointer-events-none', !pode);

    if (bolt) {
      bolt.className = `card-membro-bolt shrink-0 w-10 h-10 rounded-full flex items-center justify-center sombra-neumorfica ${
        pode
          ? 'bg-primary-container text-on-primary-container pulso-buzz'
          : 'bg-surface-container text-outline'
      }`;
      const icone = bolt.querySelector('.material-symbols-outlined');
      if (icone) icone.style.fontVariationSettings = `'FILL' ${pode ? 1 : 0}`;
    }
  }

  function atualizarPaginaChamarPresenca(status, rotulo) {
    const statusEl = document.getElementById('status-chamada');
    if (!statusEl) return;

    const estilo = estilosPresenca(status);
    statusEl.dataset.status = status;
    if (!statusEl.dataset.statusOriginal || !chamadaSainteAtiva()) {
      statusEl.textContent = rotulo || estilo.rotulo;
      statusEl.className = `font-headline-md text-headline-md ${estilo.cor}`;
      statusEl.dataset.statusOriginal = rotulo || estilo.rotulo;
      statusEl.dataset.classeOriginal = statusEl.className;
    }

    const botao = document.getElementById('botao-buzinar-contato');
    const dica = document.getElementById('dica-segurar');
    if (!botao) return;

    const pode = status !== 'offline';
    if (!chamadaSainteAtiva()) botao.disabled = !pode;
    botao.classList.toggle('opacity-50', !pode);
    botao.classList.toggle('cursor-not-allowed', !pode);
    botao.classList.toggle('cursor-pointer', pode);
    botao.classList.toggle('hover:scale-105', pode);
    if (dica && !chamadaSainteAtiva()) {
      dica.textContent = pode ? 'Segure 2s para chamar' : 'Contato offline';
    }
  }

  function tratarPresencaAtualizada(dados) {
    const usuarioId = String(dados.usuario_id);
    const status = dados.status;
    const rotulo = dados.status_rotulo;
    const anterior = statusConhecidos[usuarioId];
    statusConhecidos[usuarioId] = status;

    document.querySelectorAll(`.card-membro[data-contato-id="${usuarioId}"]`).forEach((card) => {
      atualizarCardPresenca(card, status, rotulo);
    });

    const statusChamada = document.getElementById('status-chamada');
    if (statusChamada && statusChamada.dataset.contatoId === usuarioId) {
      atualizarPaginaChamarPresenca(status, rotulo);
    }

    const inicio = document.getElementById('contador-online-inicio');
    if (inicio && !document.querySelector('.card-membro') && anterior !== undefined) {
      let total = Number(inicio.dataset.total || 0);
      if (anterior === 'online' && status !== 'online') total = Math.max(0, total - 1);
      if (anterior !== 'online' && status === 'online') total += 1;
      inicio.dataset.total = String(total);
      inicio.textContent = `${total} online`;
      return;
    }

    atualizarContadorOnline();
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
      } else if (dados.tipo === 'presenca_atualizada') {
        tratarPresencaAtualizada(dados);
      }
    };

    socket.onclose = () => setTimeout(conectarWebSocket, 3000);
  }

  document.addEventListener('click', (evento) => {
    const botaoBuzinar = evento.target.closest('[data-buzinar]');
    if (!botaoBuzinar || botaoBuzinar.disabled) return;

    // Página chamar: clique simples só cancela se já estiver buzinando
    if (botaoBuzinar.dataset.segurarBuzina) {
      if (chamadaSainteAtiva()) encerrarChamadaSainte('usuario');
      return;
    }

    enviarBuzina(botaoBuzinar);
  });

  function configurarSegurarParaBuzinar() {
    const botao = document.getElementById('botao-buzinar-contato');
    if (!botao || !botao.dataset.segurarBuzina) return;

    const iniciar = (evento) => {
      if (evento.button != null && evento.button !== 0) return;
      if (botao.disabled) return;
      if (chamadaSainteAtiva()) return;
      evento.preventDefault();
      iniciarPressionarSegurar(botao);
    };

    const soltar = () => cancelarPressionarSegurar();

    botao.addEventListener('pointerdown', iniciar);
    botao.addEventListener('pointerup', soltar);
    botao.addEventListener('pointerleave', soltar);
    botao.addEventListener('pointercancel', soltar);
    botao.addEventListener('contextmenu', (evento) => evento.preventDefault());
  }

  document.getElementById('alerta-recusar')?.addEventListener('click', () => responderBuzina({ recusar: '1' }));
  document.getElementById('chamada-encerrar')?.addEventListener('click', () => encerrarChamadaSainte('usuario'));

  document.querySelectorAll('.alerta-resposta').forEach((botao) => {
    botao.addEventListener('click', () => {
      responderBuzina({ resposta_rapida: botao.dataset.resposta });
    });
  });

  configurarSegurarParaBuzinar();
  resetarAnelProgresso();

  if (document.body.dataset.usuarioAutenticado === 'true') {
    conectarWebSocket();
  }

  // Mantém TTL da presença no Redis enquanto a aba estiver aberta
  setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ tipo: 'ping' }));
    }
  }, 30000);
})();
