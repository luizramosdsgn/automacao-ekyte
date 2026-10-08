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
            document.getElementById("caminho-pasta").innerText = caminhoCurto;
        }
    }
});

async function escolherPasta() {
    let caminho = await eel.selecionar_pasta_py()();
    if (caminho) {
        pastaSelecionada = caminho;
        document.getElementById("caminho-pasta").innerText = caminho.length > 30 ? ".../" + caminho.split(/[\\/]/).pop() : caminho;
    }
}

async function iniciarRobo() {
    let email = document.getElementById("email").value;
    let senha = document.getElementById("senha").value;
    let texto = document.getElementById("texto-docs").value;
    let modoInvisivel = document.getElementById("modo-invisivel").checked;
    
    document.getElementById("btn-iniciar").classList.add("hidden");
    document.getElementById("btn-parar").classList.remove("hidden");
    document.getElementById("btn-parar").innerText = "🛑 PARAR AUTOMAÇÃO";

    await eel.iniciar_automacao_py(email, senha, pastaSelecionada, texto, modoInvisivel)();
}

async function pararRobo() {
    document.getElementById("btn-parar").innerText = "🛑 CANCELANDO...";
    await eel.parar_automacao_py()();
}

async function padronizarTexto() {
    let texto = document.getElementById("texto-docs").value;
    let textoLimpo = await eel.padronizar_texto_py(texto, pastaSelecionada)();
    if(textoLimpo) {
        document.getElementById("texto-docs").value = textoLimpo;
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
}