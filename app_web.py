import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import eel
from playwright.sync_api import sync_playwright

# Controle de estado do robô
stop_requested = False
is_running = False

# Inicializa a pasta Web
eel.init('web')

def log_to_ui(mensagem):
    """Envia texto para o terminal do HTML"""
    print(mensagem) # Aparece no seu console também
    eel.atualizarLog(mensagem)

# ==========================================
# EXPORTS (O que o JavaScript pode chamar)
# ==========================================

@eel.expose
def selecionar_pasta_py():
    """Abre uma janela nativa do Windows para escolher a pasta"""
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal do Tkinter
    root.attributes('-topmost', True) # Força a janela a abrir por cima do navegador
    pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens")
    root.destroy()
    return pasta

@eel.expose
def parar_automacao_py():
    global stop_requested
    stop_requested = True
    log_to_ui("⚠️ Solicitação de parada recebida. Interrompendo...")

@eel.expose
def padronizar_texto_py(conteudo, pasta_imagens):
    # A sua lógica perfeita de padronização continua aqui
    if not conteudo:
        log_to_ui("⚠️ Cole o texto na caixa antes de clicar em Padronizar.")
        return ""
    
    try:
        # AQUI VAI TODA AQUELA SUA LÓGICA DE REGEX DO ARQUIVO ANTIGO (padronizar_texto)
        # Para fins de exemplo, eu vou retornar o texto com as quebras corrigidas básicas.
        # (Copie o miolo da função "padronizar_texto" do seu app_ekyte.py para cá)
        
        texto_final = conteudo # Substitua por sua lógica de regex limpa
        
        log_to_ui("✨ Texto padronizado com sucesso (Via Python)!")
        return texto_final
    except Exception as e:
        log_to_ui(f"❌ Erro ao padronizar: {str(e)}")
        return conteudo

@eel.expose
def iniciar_automacao_py(email, senha, pasta, texto, modo_invisivel):
    global stop_requested, is_running
    
    if not email or not senha:
        log_to_ui("❌ ERRO: Preencha e-mail e senha.")
        eel.restaurarBotoes()
        return
    if not pasta:
        log_to_ui("❌ ERRO: Selecione a pasta de imagens.")
        eel.restaurarBotoes()
        return

    stop_requested = False
    is_running = True
    eel.atualizarProgresso(0, "0%")
    
    log_to_ui("✅ Iniciando automação pelo Backend Web...")
    
    # Roda o Playwright em uma Thread separada para não travar a interface Web!
    thread = threading.Thread(target=rodar_automacao_core, args=(email, senha, pasta, texto, modo_invisivel))
    thread.start()

# ==========================================
# MOTOR PLAYWRIGHT
# ==========================================

def verificar_parada():
    global stop_requested
    if stop_requested:
        raise InterruptedError("Automação abortada manualmente pelo usuário.")

def rodar_automacao_core(email, senha, pasta_imagens, conteudo_texto, modo_invisivel):
    global is_running, stop_requested
    
    try:
        log_to_ui("📦 Inicializando o motor Playwright...")
        
        # Aqui você insere seu bloco gigante 'with sync_playwright() as p:' 
        # que já criamos no app_ekyte.py, trocando 'self.log' por 'log_to_ui'
        # e 'self.atualizar_progresso_ui' por 'eel.atualizarProgresso'
        
        # Exemplo Simulado (substitua pela sua lógica completa do eKyte):
        total_tarefas = 5
        for i in range(total_tarefas):
            verificar_parada()
            log_to_ui(f"🔄 Processando tarefa simulada {i+1}...")
            import time; time.sleep(1) # Simula o Playwright trabalhando
            
            pct = int(((i + 1) / total_tarefas) * 100)
            eel.atualizarProgresso(pct, f"{pct}% ({i+1}/{total_tarefas})")
            
        log_to_ui("\n🎉 AUTOMAÇÃO FINALIZADA COM SUCESSO!")

    except InterruptedError as e:
        log_to_ui(f"🛑 {str(e)}")
    except Exception as e:
        log_to_ui(f"❌ ERRO CRÍTICO: {str(e)}")
    finally:
        is_running = False
        stop_requested = False
        eel.restaurarBotoes()

# ==========================================
# INICIAR APLICAÇÃO
# ==========================================
if __name__ == '__main__':
    # Abre uma janela simulando aplicativo desktop
    eel.start('index.html', size=(900, 750), port=0)