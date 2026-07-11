(function () {
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1];
  const TEMPO_MAXIMO_ESPERA_MS = 45000;
  const CIRCUNFERENCIA_ANEL = 2 * Math.PI * 46;
  const INTERVALO_SLIDER_MS = 2200;
  let buzinaRecebida = null;
  let buzinaSainte = null;
  let buzinasSaintes = [];
  let socket = null;
  let timeoutFecharChamada = null;
  let timeoutChamada = null;
  let pressionarSegurar = null;
  let intervaloSlider = null;
  let indiceSlider = 0;
  let suprimirCliqueAposSegurar = false;

  function obterCookie(nome) {
    return document.cookie.match(new RegExp(`${nome}=([^;]+)`))?.[1];
  }

  function obterCsrfToken() {
    return (
      obterCookie('csrftoken')
      || csrfToken
      || document.querySelector('[name=csrfmiddlewaretoken]')?.value
      || ''
    );
  }

  async function postForm(url, dados) {
    const form = new FormData();
    Object.entries(dados).forEach(([chave, valor]) => form.append(chave, valor));
    const token = obterCsrfToken();
    if (token) form.append('csrfmiddlewaretoken', token);
    const resposta = await fetch(url, {
      method: 'POST',
      headers: token ? { 'X-CSRFToken': token } : {},
      body: form,
      credentials: 'same-origin',
    });
    const tipo = resposta.headers.get('content-type') || '';
    if (!tipo.includes('application/json')) {
      return { erro: resposta.ok ? 'Resposta inválida.' : `Erro ${resposta.status}` };
    }
    return resposta.json();
  }

  let gestoDoUsuarioAtivo = false;

  function marcarGestoDoUsuario() {
    gestoDoUsuarioAtivo = true;
  }

  function vibrar() {
    if (window.BuzzNativo?.ehAppNativo) {
      window.BuzzPushNativo?.vibrarNativo?.();
      return;
    }
    if (!gestoDoUsuarioAtivo || !navigator.vibrate) return;
    try {
      navigator.vibrate([200, 100, 200, 100, 400]);
    } catch {
      /* Chrome bloqueia sem gesto prévio no frame */
    }
  }

  const SomBuzz = (() => {
    let contexto = null;
    let loopSainte = null;
    let loopRecebido = null;

    function obterContexto() {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return null;
      if (!contexto) contexto = new AudioCtx();
      if (contexto.state === 'suspended') contexto.resume();
      return contexto;
    }

    function tocarTom(destino, freq, inicio, duracao, volume) {
      const osc = destino.context.createOscillator();
      const gain = destino.context.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0, inicio);
      gain.gain.linearRampToValueAtTime(volume, inicio + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, inicio + duracao);
      osc.connect(gain);
      gain.connect(destino);
      osc.start(inicio);
      osc.stop(inicio + duracao + 0.05);
    }

    function pararLoop(loop) {
      if (!loop) return;
      clearInterval(loop.intervalo);
      try {
        loop.master.gain.exponentialRampToValueAtTime(0.001, loop.ctx.currentTime + 0.06);
      } catch {
        /* osciladores curtos já encerraram */
      }
    }

    function pararSainte() {
      pararLoop(loopSainte);
      loopSainte = null;
    }

    function pararRecebido() {
      pararLoop(loopRecebido);
      loopRecebido = null;
    }

    function pararTodos() {
      pararSainte();
      pararRecebido();
    }

    function iniciarPadrao(pararFn, volume, intervaloMs, sequencia) {
      pararFn();
      const ctx = obterContexto();
      if (!ctx) return;

      const master = ctx.createGain();
      master.gain.value = volume;
      master.connect(ctx.destination);
      const loop = { ctx, master, intervalo: null };

      const tocarCiclo = () => {
        const t = ctx.currentTime;
        sequencia.forEach(([freq, offset, dur, vol]) => {
          tocarTom(master, freq, t + offset, dur, vol);
        });
      };

      tocarCiclo();
      loop.intervalo = setInterval(tocarCiclo, intervaloMs);
      return loop;
    }

    return {
      obterContexto,
      async iniciarRecebido() {
        const ctx = obterContexto();
        if (ctx?.state === 'suspended') {
          try {
            await ctx.resume();
          } catch {
            /* autoplay bloqueado até gesto do usuário */
          }
        }
        loopRecebido = iniciarPadrao(
          pararRecebido,
          0.2,
          1300,
          [
            [659.25, 0, 0.14, 0.55],
            [783.99, 0.16, 0.14, 0.5],
            [987.77, 0.32, 0.22, 0.45],
          ],
        );
      },
      iniciarSainte() {
        loopSainte = iniciarPadrao(
          pararSainte,
          0.14,
          1800,
          [
            [392, 0, 0.2, 0.4],
            [523.25, 0.24, 0.22, 0.38],
          ],
        );
      },
      pararSainte,
      pararRecebido,
      pararTodos,
    };
  })();

  async function desbloquearAudio() {
    marcarGestoDoUsuario();
    const ctx = SomBuzz.obterContexto();
    if (ctx?.state === 'suspended') {
      try {
        await ctx.resume();
      } catch {
        /* ignora */
      }
    }
  }

  let audioFallbackRecebido = null;

  async function tocarSomAlertaRecebido() {
    await desbloquearAudio();
    await SomBuzz.iniciarRecebido();

    if (!audioFallbackRecebido) {
      audioFallbackRecebido = new Audio('/static/sounds/buzina.wav');
      audioFallbackRecebido.loop = true;
    }
    try {
      audioFallbackRecebido.currentTime = 0;
      await audioFallbackRecebido.play();
    } catch {
      /* Web Audio ou gesto do usuário cobre depois */
    }
  }

  function pararSomAlertaRecebido() {
    SomBuzz.pararRecebido();
    if (audioFallbackRecebido) {
      audioFallbackRecebido.pause();
      audioFallbackRecebido.currentTime = 0;
    }
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

  function pararSliderNomes() {
    clearInterval(intervaloSlider);
    intervaloSlider = null;
    indiceSlider = 0;
    const slider = document.getElementById('chamada-slider');
    const destinatario = document.getElementById('chamada-destinatario');
    if (slider) slider.classList.add('hidden');
    if (destinatario) destinatario.classList.remove('hidden');
  }

  function mostrarNomeSlider(nome) {
    const el = document.getElementById('chamada-slider-nome');
    if (!el) return;
    el.classList.remove('slider-nome-ativo', 'slider-nome-sair');
    // Força reflow para reiniciar animação
    void el.offsetWidth;
    el.textContent = nome;
    el.classList.add('slider-nome-ativo');
  }

  function iniciarSliderNomes(nomes) {
    pararSliderNomes();
    const lista = (nomes || []).filter(Boolean);
    const slider = document.getElementById('chamada-slider');
    const destinatario = document.getElementById('chamada-destinatario');
    if (!lista.length) return;

    if (lista.length === 1) {
      if (destinatario) {
        destinatario.textContent = lista[0];
        destinatario.classList.remove('hidden');
      }
      if (slider) slider.classList.add('hidden');
      return;
    }

    if (destinatario) destinatario.classList.add('hidden');
    if (slider) slider.classList.remove('hidden');
    indiceSlider = 0;
    mostrarNomeSlider(lista[0]);
    intervaloSlider = setInterval(() => {
      indiceSlider = (indiceSlider + 1) % lista.length;
      const el = document.getElementById('chamada-slider-nome');
      if (!el) return;
      el.classList.remove('slider-nome-ativo');
      el.classList.add('slider-nome-sair');
      setTimeout(() => mostrarNomeSlider(lista[indiceSlider]), 320);
    }, INTERVALO_SLIDER_MS);
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
    tocarSomAlertaRecebido();
    alerta.addEventListener('pointerdown', () => tocarSomAlertaRecebido(), { once: true });
    incrementarContadorNotificacoes();
    window.BuzzPush?.fecharNotificacoesPorTag(dados.buzina_id);
  }

  function ocultarAlertaRecebido() {
    pararSomAlertaRecebido();
    document.getElementById('alerta-buzina')?.classList.add('hidden');
    if (!document.getElementById('chamada-sainte')?.classList.contains('hidden')) return;
    liberarScroll();
    buzinaRecebida = null;
  }

  function mostrarChamadaSainte(dados) {
    buzinaSainte = dados.buzina_id;
    buzinasSaintes = dados.buzinas || [{
      buzina_id: dados.buzina_id,
      destinatario_nome: dados.destinatario_nome,
      destinatario_avatar: dados.destinatario_avatar,
    }];
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

    const nomes = buzinasSaintes.map((b) => b.destinatario_nome);
    const multi = buzinasSaintes.length > 1;

    titulo.textContent = multi ? 'Cutucando favoritos...' : 'Cutucando...';
    subtitulo.textContent = multi
      ? `${buzinasSaintes.length} contatos`
      : 'Aguardando resposta';
    subtitulo.classList.add('animate-pulse', 'text-secondary');
    subtitulo.classList.remove('text-error', 'text-outline');
    destinatario.textContent = nomes[0] || '—';
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
      nomes[0] || 'Contato',
      buzinasSaintes[0]?.destinatario_avatar || '',
    );

    iniciarSliderNomes(nomes);

    tela.classList.remove('hidden');
    bloquearScroll();
    SomBuzz.iniciarSainte();

    timeoutChamada = setTimeout(() => encerrarChamadaSainte('timeout'), TEMPO_MAXIMO_ESPERA_MS);
  }

  function mostrarRespostaNaChamada(dados) {
    if (!chamadaSainteAtiva()) return;
    const aindaPendente = buzinasSaintes.some((b) => b.buzina_id === dados.buzina_id);
    if (!aindaPendente && dados.buzina_id !== buzinaSainte) return;

    // Em lote: remove quem respondeu e continua se restarem
    if (buzinasSaintes.length > 1) {
      buzinasSaintes = buzinasSaintes.filter((b) => b.buzina_id !== dados.buzina_id);
      if (buzinasSaintes.length) {
        buzinaSainte = buzinasSaintes[0].buzina_id;
        iniciarSliderNomes(buzinasSaintes.map((b) => b.destinatario_nome));
        const subtitulo = document.getElementById('chamada-subtitulo');
        if (subtitulo) {
          subtitulo.textContent = `${buzinasSaintes.length} aguardando · ${dados.resposta_rotulo || 'respondeu'}`;
        }
        if (navigator.vibrate) navigator.vibrate([80, 40, 80]);
        incrementarContadorNotificacoes();
        return;
      }
    }

    limparTimerChamada();
    pararSliderNomes();
    SomBuzz.pararSainte();

    if (estaNaPaginaChamar()) {
      buzinaSainte = null;
      buzinasSaintes = [];
      restaurarPaginaChamar();
      const status = document.getElementById('status-chamada');
      if (status) {
        status.textContent = dados.resposta_rotulo || 'Resposta recebida';
        status.className = 'font-headline-md text-headline-md text-secondary';
      }
      if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
      incrementarContadorNotificacoes();
      return;
    }

    const titulo = document.getElementById('chamada-titulo');
    const subtitulo = document.getElementById('chamada-subtitulo');
    const mensagem = document.getElementById('chamada-mensagem');
    const respostaBox = document.getElementById('chamada-resposta');
    const respostaTexto = document.getElementById('chamada-resposta-texto');
    const encerrarLabel = document.getElementById('chamada-encerrar-label');
    const destinatario = document.getElementById('chamada-destinatario');

    titulo.textContent = 'Resposta recebida';
    subtitulo.textContent = dados.destinatario_nome;
    subtitulo.classList.remove('animate-pulse', 'text-error');
    subtitulo.classList.add('text-secondary');
    if (destinatario) {
      destinatario.textContent = dados.destinatario_nome || '—';
      destinatario.classList.remove('hidden');
    }
    mensagem.classList.add('hidden');
    respostaTexto.textContent = dados.resposta_rotulo;
    respostaBox.classList.remove('hidden');
    encerrarLabel.textContent = 'Fechar';

    if (navigator.vibrate) navigator.vibrate([100, 50, 100]);

    clearTimeout(timeoutFecharChamada);
    timeoutFecharChamada = setTimeout(ocultarChamadaSainte, 8000);
    incrementarContadorNotificacoes();
  }

  function mostrarDesfechoChamada(motivo) {
    if (!chamadaSainteAtiva()) return;

    limparTimerChamada();
    pararSliderNomes();

    const titulo = document.getElementById('chamada-titulo');
    const subtitulo = document.getElementById('chamada-subtitulo');
    const mensagem = document.getElementById('chamada-mensagem');
    const respostaBox = document.getElementById('chamada-resposta');
    const respostaTexto = document.getElementById('chamada-resposta-texto');
    const encerrarLabel = document.getElementById('chamada-encerrar-label');
    const destinatario = document.getElementById('chamada-destinatario');

    const perdida = motivo === 'perdida';
    titulo.textContent = perdida ? 'Chamada perdida' : 'Chamada cancelada';
    subtitulo.textContent = perdida
      ? 'Sem resposta a tempo'
      : 'Você encerrou a chamada';
    subtitulo.classList.remove('animate-pulse', 'text-secondary');
    subtitulo.classList.add(perdida ? 'text-error' : 'text-outline');
    if (destinatario) destinatario.classList.remove('hidden');
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
    if (dica) {
      dica.textContent = document.getElementById('botao-buzz-inicio')
        ? (document.getElementById('botao-buzz-inicio').disabled
          ? dica.dataset.dicaOriginal || 'Marque favoritos em Próximos'
          : 'Segure 2s para chamar favoritos')
        : 'Segure 2s para chamar';
    }
    resetarAnelProgresso();
    document.querySelectorAll('[data-buzinar], [data-buzinar-favoritos]').forEach((botao) => {
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
      // Evita que o pointerup/click ao soltar cancele a chamada recém-iniciada
      suprimirCliqueAposSegurar = true;
      setTimeout(() => { suprimirCliqueAposSegurar = false; }, 500);
      enviarBuzina(botao);
      pressionarSegurar = null;
    }, duracaoMs);
  }

  function chamadaSainteAtiva() {
    return Boolean(buzinaSainte) || buzinasSaintes.length > 0;
  }

  function ocultarChamadaSainte() {
    SomBuzz.pararSainte();
    limparTimerChamada();
    clearTimeout(timeoutFecharChamada);
    pararSliderNomes();
    document.getElementById('chamada-sainte')?.classList.add('hidden');
    if (document.getElementById('alerta-buzina')?.classList.contains('hidden')) {
      liberarScroll();
    }
    buzinaSainte = null;
    buzinasSaintes = [];
    restaurarPaginaChamar();
  }

  async function encerrarChamadaSainte(motivo = 'usuario') {
    SomBuzz.pararSainte();
    if (!chamadaSainteAtiva()) {
      ocultarChamadaSainte();
      return;
    }

    const ids = buzinasSaintes.length
      ? buzinasSaintes.map((b) => b.buzina_id)
      : [buzinaSainte].filter(Boolean);
    limparTimerChamada();

    // Já em desfecho (Fechar após resposta/perda): só fecha UI
    const encerrarLabel = document.getElementById('chamada-encerrar-label');
    if (encerrarLabel?.textContent === 'Fechar') {
      ocultarChamadaSainte();
      return;
    }

    if (motivo === 'timeout') {
      await Promise.all(ids.map((id) => postForm(`/api/buzina/${id}/encerrar/`, { motivo })));
      if (estaNaPaginaChamar()) {
        buzinaSainte = null;
        buzinasSaintes = [];
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
    buzinasSaintes = [];
    await Promise.all(ids.map((id) => postForm(`/api/buzina/${id}/encerrar/`, { motivo: 'usuario' })));
    if (estaNaPaginaChamar()) {
      restaurarPaginaChamar();
      return;
    }
    ocultarChamadaSainte();
  }

  function tratarBuzinaEncerrada(dados) {
    if (buzinaRecebida && dados.buzina_id === buzinaRecebida) {
      ocultarAlertaRecebido();
    }
    if (
      dados.motivo === 'perdida'
      && (chamadaSainteAtiva() || !document.getElementById('chamada-sainte')?.classList.contains('hidden'))
    ) {
      incrementarContadorNotificacoes();
    }
    if (!chamadaSainteAtiva()) return;

    const estavaNoLote = buzinasSaintes.some((b) => b.buzina_id === dados.buzina_id)
      || dados.buzina_id === buzinaSainte;
    if (!estavaNoLote) return;

    const encerrarLabel = document.getElementById('chamada-encerrar-label');
    if (encerrarLabel?.textContent === 'Fechar') return;

    if (buzinasSaintes.length > 1) {
      buzinasSaintes = buzinasSaintes.filter((b) => b.buzina_id !== dados.buzina_id);
      if (buzinasSaintes.length) {
        buzinaSainte = buzinasSaintes[0].buzina_id;
        iniciarSliderNomes(buzinasSaintes.map((b) => b.destinatario_nome));
        return;
      }
    }

    if (estaNaPaginaChamar()) {
      buzinaSainte = null;
      buzinasSaintes = [];
      restaurarPaginaChamar();
      return;
    }
    mostrarDesfechoChamada(dados.motivo);
  }

  function estaNaPaginaChamar() {
    return Boolean(document.getElementById('mensagem-buzina'));
  }

  function atualizarPerfilPresenca(status, rotulo) {
    const statusEl = document.getElementById('status-chamada');
    if (!statusEl) return;

    const estilo = estilosPresenca(status);
    statusEl.dataset.status = status;
    if (!chamadaSainteAtiva()) {
      statusEl.textContent = rotulo || estilo.rotulo;
      statusEl.className = `font-headline-md text-headline-md ${estilo.cor} mt-2`;
    }

    const indicador = document.getElementById('perfil-indicador-status');
    if (indicador) {
      indicador.className = `perfil-indicador-status absolute bottom-1 right-1 w-4 h-4 rounded-full border-2 border-surface-container-highest ${estilo.indicador}`;
    }
  }

  function ativarOndasChamada() {
    document.getElementById('ondas-chamada')?.classList.remove('hidden');
    const status = document.getElementById('status-chamada');
    if (status) {
      if (!status.dataset.statusOriginal) {
        status.dataset.statusOriginal = status.textContent.trim();
        status.dataset.classeOriginal = status.className;
      }
      status.textContent = 'Cutucando...';
      status.className = 'font-headline-md text-headline-md text-secondary animate-pulse';
    }
    const dica = document.getElementById('dica-segurar');
    if (dica) dica.textContent = 'Toque para cancelar';
  }

  function mensagemDicaChamar(status, souFavorito, mutuos = false) {
    if (status === 'offline') return 'Contato offline';
    if (status === 'ocupado' && !podeBuzinarContato(status, souFavorito, mutuos)) {
      return 'Em não perturbe — só favoritos podem chamar';
    }
    return 'Segure 2s para chamar';
  }

  let timeoutToast = null;

  function mostrarToast(mensagem) {
    const toast = document.getElementById('toast-buzz');
    if (!toast) return;
    clearTimeout(timeoutToast);
    toast.textContent = mensagem;
    toast.classList.remove('hidden', 'visivel');
    void toast.offsetWidth;
    toast.classList.add('visivel');
    timeoutToast = setTimeout(() => {
      toast.classList.add('hidden');
      toast.classList.remove('visivel');
    }, 3200);
  }

  async function enviarBuzina(botao) {
    // Segundo clique enquanto buzina: cancela a chamada
    if (chamadaSainteAtiva()) {
      await encerrarChamadaSainte('usuario');
      return;
    }

    if (botao.dataset.buzinarFavoritos) {
      await enviarBuzinaFavoritos(botao);
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

    if (resultado.silenciada) {
      restaurarPaginaChamar();
      mostrarToast('Mensagem registrada — contato em não perturbe');
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
      buzinasSaintes = [payload];
      limparTimerChamada();
      SomBuzz.iniciarSainte();
      timeoutChamada = setTimeout(() => encerrarChamadaSainte('timeout'), TEMPO_MAXIMO_ESPERA_MS);
      return;
    }

    mostrarChamadaSainte(payload);
  }

  async function enviarBuzinaFavoritos() {
    ativarOndasChamada();

    const resultado = await postForm('/api/buzina/enviar-favoritos/', {});

    if (resultado.erro) {
      restaurarPaginaChamar();
      const dica = document.getElementById('dica-segurar');
      if (dica) dica.textContent = resultado.erro;
      return;
    }

    const buzinas = resultado.buzinas || [];
    if (!buzinas.length) {
      restaurarPaginaChamar();
      return;
    }

    mostrarChamadaSainte({
      buzina_id: buzinas[0].buzina_id,
      destinatario_nome: buzinas[0].destinatario_nome,
      destinatario_avatar: buzinas[0].destinatario_avatar,
      buzinas,
    });
  }

  async function responderBuzina(opcoes = {}) {
    if (!buzinaRecebida) return;
    await postForm(`/api/buzina/${buzinaRecebida}/responder/`, opcoes);
    ocultarAlertaRecebido();
  }

  async function alternarFavorito(botao) {
    const membroId = botao.dataset.alternarFavorito;
    if (!membroId) return;
    const resultado = await postForm(`/api/membros/${membroId}/favorito/`, {});
    if (resultado.erro) return;

    const ativo = Boolean(resultado.eh_favorito);
    botao.setAttribute('aria-pressed', ativo ? 'true' : 'false');
    botao.setAttribute('aria-label', ativo ? 'Remover dos favoritos' : 'Marcar como favorito');
    botao.classList.toggle('bg-tertiary-container', ativo);
    botao.classList.toggle('text-on-tertiary-container', ativo);
    botao.classList.toggle('bg-surface-container', !ativo);
    botao.classList.toggle('text-outline', !ativo);
    const icone = botao.querySelector('.material-symbols-outlined');
    if (icone) icone.style.fontVariationSettings = `'FILL' ${ativo ? 1 : 0}`;
  }

  function definirContadorNotificacoes(total) {
    const valor = Math.max(0, total);
    document.querySelectorAll('.central-notificacoes-contador').forEach((el) => {
      el.textContent = String(valor);
      el.classList.toggle('hidden', valor === 0);
    });
    document.querySelectorAll('.central-notificacoes-botao').forEach((btn) => {
      btn.setAttribute(
        'aria-label',
        valor ? `Notificações (${valor} não lidas)` : 'Notificações',
      );
    });
  }

  function incrementarContadorNotificacoes(delta = 1) {
    const el = document.querySelector('.central-notificacoes-contador:not(.hidden)');
    const atual = el ? Number(el.textContent || 0) : 0;
    definirContadorNotificacoes(atual + delta);
  }

  function formatarTempoRelativo(iso) {
    const diff = Date.now() - new Date(iso).getTime();
    const min = Math.floor(diff / 60000);
    if (min < 1) return 'agora';
    if (min < 60) return `${min} min atrás`;
    const h = Math.floor(min / 60);
    if (h < 24) return `${h} h atrás`;
    return `${Math.floor(h / 24)} d atrás`;
  }

  function renderizarItemNotificacao(item) {
    const avatar = item.contato_avatar
      ? `<img class="w-full h-full object-cover" src="${item.contato_avatar}" alt="${item.contato_nome}">`
      : '<span class="material-symbols-outlined text-outline">person</span>';
    const href = item.membro_id ? `/proximos/${item.membro_id}/chamar/` : '#';
    const naoLida = !item.lida;
    return `<a href="${href}" class="item-notificacao flex items-center gap-3 px-4 py-3 hover:bg-surface-container-low transition-colors no-underline ${naoLida ? 'bg-primary-container/10' : ''}" data-buzina-id="${item.buzina_id}">
      <div class="w-10 h-10 rounded-full bg-surface-container-high flex items-center justify-center shrink-0 overflow-hidden border border-white/10">${avatar}</div>
      <div class="min-w-0 flex-1">
        <p class="font-button-text text-button-text text-on-surface truncate">${item.contato_nome}</p>
        <p class="font-label-bold text-label-bold text-on-surface-variant text-xs mt-0.5 truncate">${item.rotulo}</p>
      </div>
      <time class="font-label-bold text-label-bold text-outline text-xs shrink-0">${formatarTempoRelativo(item.horario)}</time>
    </a>`;
  }

  async function carregarNotificacoes() {
    const listas = document.querySelectorAll('.central-notificacoes-lista');
    if (!listas.length) return null;

    const resposta = await fetch('/api/notificacoes/', { credentials: 'same-origin' });
    const dados = await resposta.json();
    if (dados.erro) return null;

    definirContadorNotificacoes(dados.nao_lidas || 0);
    const html = !dados.itens?.length
      ? '<p class="central-notificacoes-vazio px-4 py-8 text-center text-on-surface-variant font-body-md text-sm">Nenhuma atividade recente</p>'
      : dados.itens.map(renderizarItemNotificacao).join('');
    listas.forEach((lista) => { lista.innerHTML = html; });
    return dados;
  }

  async function alternarCentralNotificacoes(botao) {
    const container = botao.closest('.central-notificacoes');
    if (!container) return;

    const painel = container.querySelector('.central-notificacoes-painel');
    const aberto = painel && !painel.classList.contains('hidden');

    document.querySelectorAll('.central-notificacoes-painel').forEach((p) => p.classList.add('hidden'));
    document.querySelectorAll('.central-notificacoes-botao').forEach((b) => b.setAttribute('aria-expanded', 'false'));

    if (aberto) return;

    painel.classList.remove('hidden');
    botao.setAttribute('aria-expanded', 'true');
    await postForm('/api/notificacoes/marcar-lidas/', {});
    definirContadorNotificacoes(0);
    await carregarNotificacoes();
  }

  function configurarCentralNotificacoes() {
    document.querySelectorAll('.central-notificacoes-botao').forEach((botao) => {
      botao.addEventListener('click', (evento) => {
        evento.stopPropagation();
        alternarCentralNotificacoes(botao);
      });
    });

    document.addEventListener('click', (evento) => {
      if (evento.target.closest('.central-notificacoes')) return;
      document.querySelectorAll('.central-notificacoes-painel').forEach((p) => p.classList.add('hidden'));
      document.querySelectorAll('.central-notificacoes-botao').forEach((b) => b.setAttribute('aria-expanded', 'false'));
    });
  }

  const statusConhecidos = {};
  const favoritosMeta = {};

  function podeBuzinarContato(status, souFavorito, mutuos = false) {
    if (status === 'offline') return false;
    if (status === 'ocupado') {
      return souFavorito === true || souFavorito === 'true' || mutuos === true || mutuos === 'true';
    }
    return true;
  }

  function carregarPresencaInicial() {
    const proximos = document.getElementById('proximos-presenca');
    if (proximos) {
      try {
        JSON.parse(proximos.textContent).forEach((membro) => {
          statusConhecidos[String(membro.contato_id)] = membro.status || 'offline';
        });
      } catch {
        /* ignora JSON inválido */
      }
    }

    document.querySelectorAll('.card-membro[data-contato-id]').forEach((card) => {
      statusConhecidos[card.dataset.contatoId] = card.dataset.status || 'offline';
    });

    const el = document.getElementById('favoritos-presenca');
    if (!el) return;
    try {
      JSON.parse(el.textContent).forEach((fav) => {
        const id = String(fav.contato_id);
        favoritosMeta[id] = {
          souFavorito: fav.sou_favorito,
          mutuos: fav.mutuos,
        };
        statusConhecidos[id] = fav.status || statusConhecidos[id] || 'offline';
      });
    } catch {
      /* ignora JSON inválido */
    }
  }

  function atualizarBotaoBuzzInicio() {
    const botao = document.getElementById('botao-buzz-inicio');
    const dica = document.getElementById('dica-segurar');
    if (!botao) return;

    const ids = Object.keys(favoritosMeta);
    if (!ids.length) return;

    const algumDisponivel = ids.some((id) => {
      const meta = favoritosMeta[id];
      const status = statusConhecidos[id] || 'offline';
      return podeBuzinarContato(status, meta.souFavorito, meta.mutuos);
    });

    botao.disabled = !algumDisponivel;
    if (algumDisponivel) {
      botao.removeAttribute('data-manter-desabilitado');
      botao.classList.remove('opacity-50', 'cursor-not-allowed');
      botao.classList.add('hover:scale-105', 'active:scale-95', 'cursor-pointer');
    } else {
      botao.setAttribute('data-manter-desabilitado', '1');
      botao.classList.add('opacity-50', 'cursor-not-allowed');
      botao.classList.remove('hover:scale-105', 'active:scale-95', 'cursor-pointer');
    }

    if (dica) {
      dica.textContent = algumDisponivel
        ? 'Segure 2s para chamar favoritos'
        : 'Favoritos offline';
    }
  }

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

  function atualizarPillDisponibilidade(status, conectado) {
    const mapa = {
      online: {
        classePill: 'pill-disponivel text-on-surface-variant',
        indicador: 'bg-secondary shadow-[0_0_8px_rgba(76,215,246,0.6)] animate-pulse',
        texto: 'Disponível',
        aria: 'Disponível — clique para ativar não perturbe',
      },
      ocupado: {
        classePill: 'pill-nao-perturbe text-on-surface-variant',
        indicador: 'bg-tertiary shadow-[0_0_8px_rgba(255,183,132,0.6)]',
        texto: 'Não perturbe',
        aria: 'Não perturbe — clique para ficar disponível',
      },
      offline: {
        classePill: 'pill-offline text-outline cursor-not-allowed opacity-80',
        indicador: 'bg-outline',
        texto: 'Offline',
        aria: 'Offline',
      },
    };
    const estilo = mapa[status] || mapa.offline;

    document.querySelectorAll('[data-pill-disponibilidade]').forEach((pill) => {
      pill.dataset.status = status;
      if (conectado !== undefined) {
        pill.dataset.conectado = conectado ? 'true' : 'false';
        pill.disabled = !conectado;
        pill.setAttribute('aria-disabled', conectado ? 'false' : 'true');
      }
      if (status === 'ocupado') pill.dataset.preferencia = 'ocupado';
      else if (status === 'online') pill.dataset.preferencia = 'online';

      pill.className = `pill-disponibilidade flex items-center gap-xs px-3 py-1 rounded-full bg-surface-container-high border border-white/5 sombra-neumorfica text-xs font-label-bold transition-colors ${estilo.classePill}`;

      const indicador = pill.querySelector('.pill-disponibilidade-indicador');
      const texto = pill.querySelector('.pill-disponibilidade-texto');
      if (indicador) indicador.className = `pill-disponibilidade-indicador w-2 h-2 rounded-full ${estilo.indicador}`;
      if (texto) texto.textContent = estilo.texto;
      pill.setAttribute('aria-label', estilo.aria);
    });
  }

  function sincronizarPillAoConectar() {
    document.querySelectorAll('[data-pill-disponibilidade]').forEach((pill) => {
      const pref = pill.dataset.preferencia === 'ocupado' ? 'ocupado' : 'online';
      atualizarPillDisponibilidade(pref, true);
    });
  }

  function sincronizarPillAoDesconectar() {
    atualizarPillDisponibilidade('offline', false);
  }

  async function alternarDisponibilidadePill(pill) {
    if (pill.disabled || pill.dataset.conectado !== 'true') return;
    const modo = pill.dataset.status === 'ocupado' ? 'disponivel' : 'nao_perturbe';
    const resultado = await postForm('/api/disponibilidade/', { modo });
    if (resultado.erro) {
      mostrarToast(resultado.erro);
      return;
    }
    const status = resultado.status || (modo === 'nao_perturbe' ? 'ocupado' : 'online');
    atualizarPillDisponibilidade(status, true);
  }

  function configurarPillDisponibilidade() {
    document.querySelectorAll('[data-pill-disponibilidade]').forEach((pill) => {
      pill.addEventListener('click', () => alternarDisponibilidadePill(pill));
    });
  }

  function atualizarCardPresenca(card, status, rotulo) {
    const estilo = estilosPresenca(status);
    card.dataset.status = status;

    const indicador = card.querySelector('.card-membro-indicador');
    const statusEl = card.querySelector('.card-membro-status');
    const bolt = card.querySelector('.card-membro-bolt');
    const link = card.querySelector('a.flex-1');
    const souFavorito = card.dataset.souFavorito === 'true';
    const mutuos = card.dataset.favoritosMutuos === 'true';
    const pode = podeBuzinarContato(status, souFavorito, mutuos);
    const offline = status === 'offline';

    if (indicador) {
      indicador.className = `card-membro-indicador absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-surface-container-highest ${estilo.indicador}`;
    }
    if (statusEl) {
      statusEl.textContent = rotulo || estilo.rotulo;
      statusEl.className = `card-membro-status font-label-bold text-label-bold ${estilo.cor} mt-1`;
    }

    card.classList.toggle('opacity-75', offline);
    card.classList.toggle('grayscale-[0.2]', offline);
    card.classList.toggle('border-l-4', status === 'ocupado');
    card.classList.toggle('border-l-tertiary', status === 'ocupado');
    if (link) link.classList.toggle('pointer-events-none', offline);

    if (bolt) {
      bolt.className = `card-membro-bolt shrink-0 w-10 h-10 rounded-full flex items-center justify-center sombra-neumorfica no-underline ${
        pode
          ? 'bg-primary-container text-on-primary-container pulso-buzz'
          : 'bg-surface-container text-outline pointer-events-none'
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
    const indicadorPerfil = document.getElementById('perfil-indicador-status');
    if (indicadorPerfil) {
      indicadorPerfil.className = `perfil-indicador-status absolute bottom-1 right-1 w-4 h-4 rounded-full border-2 border-surface-container-highest ${estilo.indicador}`;
    }
    if (!botao) return;

    const souFavorito = statusEl?.dataset.souFavorito === 'true';
    const mutuos = statusEl?.dataset.favoritosMutuos === 'true';
    const pode = podeBuzinarContato(status, souFavorito, mutuos);
    if (!chamadaSainteAtiva()) botao.disabled = !pode;
    botao.classList.toggle('opacity-50', !pode);
    botao.classList.toggle('cursor-not-allowed', !pode);
    botao.classList.toggle('cursor-pointer', pode);
    botao.classList.toggle('hover:scale-105', pode);
    if (dica && !chamadaSainteAtiva()) {
      dica.textContent = mensagemDicaChamar(status, souFavorito, mutuos);
    }
  }

  function tratarPresencaAtualizada(dados) {
    const usuarioId = String(dados.usuario_id);
    const status = dados.status;
    const rotulo = dados.status_rotulo;
    const meuId = document.body.dataset.usuarioId;

    if (meuId && usuarioId === meuId) {
      if (status === 'offline') {
        sincronizarPillAoDesconectar();
      } else {
        atualizarPillDisponibilidade(status, true);
      }
    }

    statusConhecidos[usuarioId] = status;

    document.querySelectorAll(`.card-membro[data-contato-id="${usuarioId}"]`).forEach((card) => {
      atualizarCardPresenca(card, status, rotulo);
    });

    const statusChamada = document.getElementById('status-chamada');
    if (statusChamada && statusChamada.dataset.contatoId === usuarioId) {
      if (estaNaPaginaChamar()) {
        atualizarPaginaChamarPresenca(status, rotulo);
      } else {
        atualizarPerfilPresenca(status, rotulo);
      }
    }

    atualizarContadorOnline();
    atualizarBotaoBuzzInicio();
  }

  function conectarWebSocket() {
    const protocolo = window.location.protocol === 'https:' ? 'wss' : 'ws';
    socket = new WebSocket(`${protocolo}://${window.location.host}/ws/buzz/`);

    socket.onopen = () => sincronizarPillAoConectar();

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

    socket.onclose = () => {
      sincronizarPillAoDesconectar();
      setTimeout(conectarWebSocket, 3000);
    };
  }

  document.addEventListener('click', (evento) => {
    const botaoFavorito = evento.target.closest('[data-alternar-favorito]');
    if (botaoFavorito) {
      evento.preventDefault();
      evento.stopPropagation();
      alternarFavorito(botaoFavorito);
      return;
    }

    const botaoBuzinar = evento.target.closest('[data-buzinar], [data-buzinar-favoritos]');
    if (!botaoBuzinar || botaoBuzinar.disabled) return;

    // Hold 2s: clique simples só cancela se já estiver buzinando
    if (botaoBuzinar.dataset.segurarBuzina) {
      if (suprimirCliqueAposSegurar) return;
      if (chamadaSainteAtiva()) encerrarChamadaSainte('usuario');
      return;
    }

    enviarBuzina(botaoBuzinar);
  });

  function configurarSegurarParaBuzinar() {
    document.querySelectorAll('[data-segurar-buzina]').forEach((botao) => {
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
    });
  }

  document.getElementById('alerta-recusar')?.addEventListener('click', () => responderBuzina({ recusar: '1' }));
  document.getElementById('chamada-encerrar')?.addEventListener('click', () => encerrarChamadaSainte('usuario'));

  document.querySelectorAll('.alerta-resposta').forEach((botao) => {
    botao.addEventListener('click', () => {
      responderBuzina({ resposta_rapida: botao.dataset.resposta });
    });
  });

  configurarSegurarParaBuzinar();
  configurarCentralNotificacoes();
  configurarPillDisponibilidade();
  carregarPresencaInicial();
  atualizarBotaoBuzzInicio();
  resetarAnelProgresso();

  if (document.body.dataset.usuarioAutenticado === 'true') {
    const ativarGesto = () => marcarGestoDoUsuario();
    if (!window.Capacitor?.isNativePlatform?.()) {
      document.addEventListener('pointerdown', ativarGesto, { once: true });
      document.addEventListener('keydown', ativarGesto, { once: true });
      document.addEventListener('pointerdown', desbloquearAudio, { once: true });
      document.addEventListener('keydown', desbloquearAudio, { once: true });
    } else {
      marcarGestoDoUsuario();
      desbloquearAudio();
    }
    conectarWebSocket();
    window.mostrarToastPush = mostrarToast;
    window.BuzzSom = {
      desbloquear: desbloquearAudio,
      tocarRecebido: tocarSomAlertaRecebido,
      pararRecebido: pararSomAlertaRecebido,
    };
    window.BuzzPushNativo?.iniciar(mostrarAlertaRecebido);
    window.BuzzPush?.iniciar(mostrarAlertaRecebido);
  }

  // Mantém TTL da presença no Redis enquanto a aba estiver aberta
  setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ tipo: 'ping' }));
    }
  }, 30000);
})();
