let pastaSelecionada = "";

// Carrega os dados salvos do JSON automaticamente ao abrir o app
window.addEventListener("DOMContentLoaded", async () => {
    let config = await eel.carregar_config_py()();
    if (config) {
        document.getElementById("email").value = config.email;
        document.getElementById("senha").value = config.senha;
        if (config.pasta_imagens) {
            pastaSelecionada = config.pasta_imagens;
            let caminhoCurto = pastaSelecionada.length > 30 ? ".../" + pastaSelecionada.split(/[\\/]/).pop() : pastaSelecionada;
            let elemCaminho = document.getElementById("caminho-pasta");
            elemCaminho.innerText = caminhoCurto;
            elemCaminho.title = pastaSelecionada;
        }
        // Restaura modo vídeo salvo
        if (config.modo_video) {
            document.getElementById("modo-video").checked = true;
            document.body.classList.add("light-mode");
        }
        // Restaura altura do planejamento
        if (config.altura_planejamento) {
            document.documentElement.style.setProperty('--plan-height', config.altura_planejamento + 'px');
        }
    }

    // Toggle modo vídeo (light/dark)
    document.getElementById("modo-video").addEventListener("change", function () {
        if (this.checked) {
            document.body.classList.add("light-mode");
        } else {
            document.body.classList.remove("light-mode");
        }
        salvarPreferencias();
    });

    // Altura do textarea configurável via resize com duplo clique
    let textoDocs = document.getElementById("texto-docs");
    textoDocs.style.resize = "vertical";
    textoDocs.style.minHeight = "120px";
    textoDocs.style.maxHeight = "80vh";
    textoDocs.style.height = getComputedStyle(textoDocs).height;

    // Salva a altura quando o usuário redimensiona
    new ResizeObserver(() => {
        let alturaAtual = parseInt(textoDocs.style.height || textoDocs.offsetHeight);
        if (alturaAtual > 0) {
            document.documentElement.style.setProperty('--plan-height', alturaAtual + 'px');
            salvarPreferencias();
        }
    }).observe(textoDocs);
});

// Salva preferências visuais (modo vídeo, altura)
let _salvarTimeout = null;
function salvarPreferencias() {
    clearTimeout(_salvarTimeout);
    _salvarTimeout = setTimeout(async () => {
        let modoVideo = document.getElementById("modo-video").checked;
        let altura = parseInt(getComputedStyle(document.getElementById("texto-docs")).height);
        await eel.salvar_preferencias_py(modoVideo, altura)();
    }, 500);
}

async function escolherPasta() {
    let caminho = await eel.selecionar_pasta_py()();
    if (caminho) {
        pastaSelecionada = caminho;
        let elemCaminho = document.getElementById("caminho-pasta");
        elemCaminho.innerText = caminho.length > 30 ? ".../" + caminho.split(/[\\/]/).pop() : caminho;
        elemCaminho.title = caminho;
        await eel.salvar_config_py(
            document.getElementById("email").value,
            document.getElementById("senha").value,
            pastaSelecionada
        )();
    }
}

async function iniciarRobo() {
    let email = document.getElementById("email").value;
    let senha = document.getElementById("senha").value;
    let texto = document.getElementById("texto-docs").value;
    let modoInvisivel = document.getElementById("modo-invisivel").checked;
    let criarTarefas = document.getElementById("criar-tarefas").checked;
    
    document.getElementById("btn-iniciar").classList.add("hidden");
    document.getElementById("btn-parar").classList.remove("hidden");
    document.getElementById("btn-parar").innerText = "🛑 PARAR AUTOMAÇÃO";
    document.getElementById("btn-parar").disabled = false;
    document.getElementById("btn-pasta").disabled = true;
    document.getElementById("btn-formatar").disabled = true;

    // Passando o novo parâmetro para o Python
    await eel.iniciar_automacao_py(email, senha, pastaSelecionada, texto, modoInvisivel, criarTarefas)();
}

async function pararRobo() {
    let btnParar = document.getElementById("btn-parar");
    btnParar.innerText = "🛑 CANCELANDO...";
    btnParar.disabled = true;
    await eel.parar_automacao_py()();
}

async function padronizarTexto() {
    let texto = document.getElementById("texto-docs").value;
    let textoLimpo = await eel.padronizar_texto_py(texto, pastaSelecionada)();
    if(textoLimpo) {
        document.getElementById("texto-docs").value = textoLimpo;
    }
}

function alternarVisibilidadeSenha() {
    let campoSenha = document.getElementById("senha");
    let btnToggle = document.getElementById("btn-toggle-senha");

    if (campoSenha.type === "password") {
        campoSenha.type = "text";
        btnToggle.innerText = "🙈";
        btnToggle.setAttribute("aria-label", "Ocultar senha");
        btnToggle.title = "Ocultar senha";
    } else {
        campoSenha.type = "password";
        btnToggle.innerText = "👁️";
        btnToggle.setAttribute("aria-label", "Mostrar senha");
        btnToggle.title = "Mostrar senha";
    }
}

eel.expose(atualizarLog);
function atualizarLog(mensagem) {
    let terminal = document.getElementById("terminal-log");
    terminal.value += mensagem + "\n";
    terminal.scrollTop = terminal.scrollHeight;
}

eel.expose(atualizarProgresso);
function atualizarProgresso(porcentagem, texto) {
    document.getElementById("barra-progresso").style.width = porcentagem + "%";
    let container = document.getElementById("barra-progresso-container");
    if (container) {
        container.setAttribute("aria-valuenow", porcentagem);
    }
    document.getElementById("texto-progresso").innerText = texto;
}

eel.expose(restaurarBotoes);
function restaurarBotoes() {
    document.getElementById("btn-iniciar").classList.remove("hidden");
    document.getElementById("btn-parar").classList.add("hidden");
    document.getElementById("btn-parar").disabled = false;
    document.getElementById("btn-pasta").disabled = false;
    document.getElementById("btn-formatar").disabled = false;
}

// Modal de timeout — chamada pelo Python via eel
eel.expose(pedirAguardoTimeout);
function pedirAguardoTimeout() {
    return new Promise((resolve) => {
        let modal = document.getElementById("modal-timeout");
        modal.classList.remove("hidden");

        let btnEsperar = document.getElementById("btn-timeout-esperar");
        let btnCancelar = document.getElementById("btn-timeout-cancelar");

        function limpar() {
            modal.classList.add("hidden");
            btnEsperar.removeEventListener("click", onEsperar);
            btnCancelar.removeEventListener("click", onCancelar);
        }

        function onEsperar() {
            limpar();
            resolve(true);
        }

        function onCancelar() {
            limpar();
            resolve(false);
        }

        btnEsperar.addEventListener("click", onEsperar);
        btnCancelar.addEventListener("click", onCancelar);
    });
}
