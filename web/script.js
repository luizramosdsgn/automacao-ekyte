let pastaSelecionada = "";

const ICONS = {
    eye: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>`,
    eyeOff: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" y1="2" x2="22" y2="22"/></svg>`,
    stop: `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="18" height="18" x="3" y="3" rx="2"/></svg>`
};

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
    }
});

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
    const btnParar = document.getElementById("btn-parar");
    btnParar.classList.remove("hidden");
    btnParar.innerHTML = `${ICONS.stop} PARAR AUTOMAÇÃO`;
    btnParar.disabled = false;
    document.getElementById("btn-pasta").disabled = true;
    document.getElementById("btn-formatar").disabled = true;

    // Passando o novo parâmetro para o Python
    await eel.iniciar_automacao_py(email, senha, pastaSelecionada, texto, modoInvisivel, criarTarefas)();
}

async function pararRobo() {
    let btnParar = document.getElementById("btn-parar");
    btnParar.innerHTML = `${ICONS.stop} CANCELANDO...`;
    btnParar.disabled = true;
    await eel.parar_automacao_py()();
}

async function padronizarTexto() {
    let texto = document.getElementById("texto-docs").value;
    let textoLimpo = await eel.padronizar_texto_py(texto, pastaSelecionada)();
    if (textoLimpo) {
        document.getElementById("texto-docs").value = textoLimpo;
    }
}

function alternarVisibilidadeSenha() {
    let campoSenha = document.getElementById("senha");
    let btnToggle = document.getElementById("btn-toggle-senha");

    if (campoSenha.type === "password") {
        campoSenha.type = "text";
        btnToggle.innerHTML = ICONS.eyeOff;
        btnToggle.setAttribute("aria-label", "Ocultar senha");
        btnToggle.title = "Ocultar senha";
    } else {
        campoSenha.type = "password";
        btnToggle.innerHTML = ICONS.eye;
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
    const btnParar = document.getElementById("btn-parar");
    btnParar.classList.add("hidden");
    btnParar.innerHTML = `${ICONS.stop} PARAR AUTOMAÇÃO`;
    btnParar.disabled = false;
    document.getElementById("btn-pasta").disabled = false;
    document.getElementById("btn-formatar").disabled = false;
}
