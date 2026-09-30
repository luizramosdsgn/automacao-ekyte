// VARIÁVEL GLOBAL
let pastaSelecionada = "";

// 1. Funções que o HTML chama (Envia para o Python)
async function escolherPasta() {
    let caminho = await eel.selecionar_pasta_py()(); // Chama a função no Python
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
    
    // Opcional: Adicionar validações de campos vazios aqui no JS antes de mandar pro Python

    document.getElementById("btn-iniciar").classList.add("hidden");
    document.getElementById("btn-parar").classList.remove("hidden");

    // Aciona a automação no Python
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

// 2. Funções que o Python chama (Altera o HTML)
eel.expose(atualizarLog);
function atualizarLog(mensagem) {
    let terminal = document.getElementById("terminal-log");
    terminal.value += mensagem + "\n";
    terminal.scrollTop = terminal.scrollHeight; // Rola pro final
}

eel.expose(atualizarProgresso);
function atualizarProgresso(porcentagem, texto) {
    document.getElementById("barra-progresso").style.width = porcentagem + "%";
    document.getElementById("texto-progresso").innerText = texto;
}

eel.expose(restaurarBotoes);
function restaurarBotoes() {
    document.getElementById("btn-iniciar").classList.remove("hidden");
    document.getElementById("btn-parar").classList.add("hidden");
    document.getElementById("btn-parar").innerText = "🛑 PARAR AUTOMAÇÃO";
}