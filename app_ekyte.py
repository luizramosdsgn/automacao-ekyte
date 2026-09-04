import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import re
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog
from playwright.sync_api import sync_playwright

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

class AppAutomaEkyte(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Robô eKyte - Automação de Tarefas")
        self.geometry("800x700")
        self.resizable(False, False)

        self.pasta_imagens = ""
        self.criar_interface()

    def criar_interface(self):
        # COLUNA ESQUERDA: CONFIGURAÇÕES
        frame_config = ctk.CTkFrame(self, width=350, corner_radius=10)
        frame_config.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(frame_config, text="⚙️ Configurações", font=("Arial", 18, "bold")).pack(pady=(20, 15))

        ctk.CTkLabel(frame_config, text="E-mail do eKyte:").pack(anchor="w", padx=20)
        self.entry_email = ctk.CTkEntry(frame_config, width=300, placeholder_text="seu@email.com")
        self.entry_email.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(frame_config, text="Senha do eKyte:").pack(anchor="w", padx=20)
        
        # Frame horizontal para acomodar a senha e o botão do olho juntos
        frame_senha = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_senha.pack(padx=20, pady=(0, 15), fill="x")
        
        self.entry_senha = ctk.CTkEntry(frame_senha, width=255, show="*", placeholder_text="Sua senha")
        self.entry_senha.pack(side="left")
        
        self.btn_eye = ctk.CTkButton(frame_senha, text="👁", width=40, fg_color="#555555", hover_color="#333333", command=self.toggle_senha)
        self.btn_eye.pack(side="right")

        ctk.CTkLabel(frame_config, text="Pasta das Imagens:").pack(anchor="w", padx=20)
        self.btn_pasta = ctk.CTkButton(frame_config, text="📁 Escolher Pasta", fg_color="#4CAF50", hover_color="#45a049", command=self.selecionar_pasta)
        self.btn_pasta.pack(padx=20, pady=(0, 5), fill="x")
        self.lbl_pasta = ctk.CTkLabel(frame_config, text="Nenhuma pasta selecionada", text_color="gray", font=("Arial", 10))
        self.lbl_pasta.pack(padx=20, pady=(0, 15))

        self.switch_headless = ctk.CTkSwitch(frame_config, text="Rodar em 2º plano (Invisível)")
        self.switch_headless.pack(padx=20, pady=10, anchor="w")

        # Botão com a cor personalizada #3179FF
        self.btn_iniciar = ctk.CTkButton(frame_config, text="🚀 INICIAR AUTOMAÇÃO", height=50, font=("Arial", 14, "bold"), fg_color="#3179FF", hover_color="#2562d4", command=self.iniciar_thread)
        self.btn_iniciar.pack(padx=20, pady=30, fill="x")

        # COLUNA DIREITA: DADOS E LOGS
        frame_dados = ctk.CTkFrame(self, corner_radius=10)
        frame_dados.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(frame_dados, text="📝 Cole aqui o texto do Google Docs:", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.textbox_docs = ctk.CTkTextbox(frame_dados, height=250)
        self.textbox_docs.pack(padx=20, pady=(0, 15), fill="x")

        ctk.CTkLabel(frame_dados, text="🖥️ Status do Robô:", font=("Arial", 14, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        
        # Log com texto na cor personalizada #3179FF
        self.textbox_log = ctk.CTkTextbox(frame_dados, height=200, fg_color="#1e1e1e", text_color="#3179FF", font=("Consolas", 12))
        self.textbox_log.pack(padx=20, pady=(0, 20), fill="both", expand=True)
        self.textbox_log.configure(state="disabled") 

    def toggle_senha(self):
        """Alterna a visibilidade da senha e o ícone do botão"""
        if self.entry_senha.cget("show") == "*":
            self.entry_senha.configure(show="")
            self.btn_eye.configure(text="🙈")
        else:
            self.entry_senha.configure(show="*")
            self.btn_eye.configure(text="👁")

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens")
        if pasta:
            self.pasta_imagens = pasta
            caminho_curto = ".../" + os.path.basename(pasta) if len(pasta) > 30 else pasta
            self.lbl_pasta.configure(text=caminho_curto)

    def log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end") 
        self.textbox_log.configure(state="disabled")

    def iniciar_thread(self):
        if not self.entry_email.get() or not self.entry_senha.get():
            self.log("❌ ERRO: Preencha e-mail e senha.")
            return
        if not self.pasta_imagens:
            self.log("❌ ERRO: Selecione a pasta de imagens.")
            return
        
        conteudo_texto = self.textbox_docs.get("1.0", "end").strip()
        if not conteudo_texto:
            self.log("❌ ERRO: Cole o texto do Google Docs na caixa acima.")
            return

        self.btn_iniciar.configure(state="disabled", text="⏳ RODANDO...", fg_color="#555555")
        thread = threading.Thread(target=self.rodar_automacao_core, args=(conteudo_texto,))
        thread.start()

    def identificar_tipos_formulario(self, texto):
        texto_min = texto.lower()
        tipos = []
        
        if "feed e story" in texto_min or "story e feed" in texto_min:
            tipos.append("Post Único: Feed")
            tipos.append("Post Único: Story, Reel, Short, TikTok")
            return tipos
            
        if "carrossel" in texto_min and "story" in texto_min or "carrossel stories" in texto_min:
            tipos.append("Post Carrossel: Story")
        elif "carrossel" in texto_min:
            tipos.append("Post Carrossel: Feed")
        elif any(palavra in texto_min for palavra in ["story", "stories", "reel", "tiktok", "shorts"]):
            tipos.append("Post Único: Story, Reel, Short, TikTok")
        elif "arte gráfica" in texto_min:
            tipos.append("Arte Gráfica")
        else:
            tipos.append("Post Único: Feed") 
            
        return tipos

    def extrair_dados_do_texto(self, conteudo):
        blocos = conteudo.split("DATA DA PUBLICAÇÃO:")[1:] 
        tarefas = []
        for bloco in blocos:
            texto_completo = "DATA DA PUBLICAÇÃO:" + bloco.strip()
            texto_min = texto_completo.lower()
            
            if "vídeo" in texto_min or "video" in texto_min:
                self.log("⚠️ Tarefa ignorada (Conteúdo em vídeo detectado).")
                continue 

            data_match = re.search(r'(\d{2}/\d{2})', bloco)
            if data_match:
                data_formatada = data_match.group(1) 
                nome_tarefa = data_formatada.replace('/', '-') 
                tarefas.append({
                    "nome": nome_tarefa,
                    "data": data_formatada,
                    "descricao": texto_completo,
                    "tipos_formulario": self.identificar_tipos_formulario(texto_completo) 
                })
        return tarefas

    def buscar_imagens(self, nome_tarefa):
        caminho_alvo = os.path.join(self.pasta_imagens, nome_tarefa)
        if os.path.isdir(caminho_alvo):
            return [os.path.join(caminho_alvo, f) for f in os.listdir(caminho_alvo) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        
        for ext in ['.jpg', '.png', '.jpeg', '.webp', '.JPG', '.PNG', '.JPEG']:
            arquivo_unico = caminho_alvo + ext
            if os.path.isfile(arquivo_unico):
                return [arquivo_unico]
        return []

    def rodar_automacao_core(self, conteudo_texto):
        try:
            self.log("🔍 Analisando texto...")
            tarefas = self.extrair_dados_do_texto(conteudo_texto)
            if not tarefas:
                self.log("❌ Nenhuma tarefa válida encontrada (ou todas eram vídeos).")
                self.restaurar_botao()
                return

            email = self.entry_email.get()
            senha = self.entry_senha.get()
            modo_invisivel = bool(self.switch_headless.get())

            # ==========================================
            # INSTALADOR AUTOMÁTICO PARA A SUA EQUIPE
            # ==========================================
            self.log("📦 Verificando/Atualizando motor do navegador...")
            try:
                from playwright._impl.__main__ import main as playwright_main
                
                original_argv = sys.argv
                sys.argv = ["playwright", "install", "chromium"]
                try:
                    playwright_main()
                except SystemExit:
                    pass 
                finally:
                    sys.argv = original_argv
            except Exception as e:
                self.log(f"⚠️ Aviso na instalação do navegador: {e}")
            # ==========================================

            with sync_playwright() as p:
                self.log(f"🌐 Iniciando navegador (Invisível: {modo_invisivel})...")
                browser = p.chromium.launch(headless=modo_invisivel, slow_mo=500) 
                context = browser.new_context()
                page = context.new_page()

                self.log("🔐 Fazendo login no eKyte...")
                page.goto("https://app.ekyte.com")
                page.fill("input[name='email']", email)
                page.fill("input[name='password']", senha)
                page.click("button:has-text('Entrar')")
                page.wait_for_timeout(5000) 

                try:
                    page.wait_for_selector("div[title*='Audácia Mkt&Co']", timeout=5000)
                except:
                    self.log("⚠️ AVISO: Empresa Audácia Mkt&Co pode não estar selecionada.")
                
                self.log("📂 Indo para as Tarefas...")
                page.locator("a[href*='#/tasks/list']").click()
                page.wait_for_timeout(3000) 

                self.log("🎯 Buscando a primeira tarefa [ROBO]...")
                page.locator("text='[ROBO]'").first.click()
                page.wait_for_timeout(2000)

                for index, task in enumerate(tarefas):
                    self.log(f"🔄 [{index+1}/{len(tarefas)}] Processando: {task['nome']}")
                    
                    page.locator(".title-header").click()
                    page.locator(".title-input input").fill(task['nome'])
                    page.keyboard.press("Enter")
                    
                    page.locator(".body-item-taskduedate").click()
                    page.locator("#input-taskDueDate").fill(task['data'] + "/2026")
                    page.keyboard.press("Enter")
                    
                    page.locator(".actions-description").click() 
                    page.locator(".ql-editor[contenteditable='true']").fill(task['descricao'])
                    page.locator("button.button-save-big").click()
                    page.wait_for_timeout(1000)

                    tarefa_tem_carrossel = False

                    for tipo_form in task['tipos_formulario']:
                        self.log(f"   ↳ Criando formulário: {tipo_form}")
                        
                        if "Carrossel" in tipo_form:
                            tarefa_tem_carrossel = True
                        
                        page.locator("div.tab span:has-text('Formulários')").click()
                        page.wait_for_timeout(2000) 
                        
                        page.locator("a[title='Adicionar formulário']").first.click()
                        page.wait_for_timeout(3000) 
                        
                        page.locator("span.Select-value-label-tag", has_text=tipo_form).click()
                        page.wait_for_timeout(1000)
                        page.locator("span.span-tab", has_text="CRIAÇÃO").click()

                        if "Carrossel" not in tipo_form:
                            imagens = self.buscar_imagens(task['nome'])
                            if imagens:
                                self.log("   ↳ Subindo imagens...")
                                page.locator("div.attachment-task").click()
                                
                                with page.expect_file_chooser() as fc_info:
                                    page.locator("button.upload-button").click(force=True)
                                fc_info.value.set_files(imagens)
                                
                                page.wait_for_timeout(4000) 
                                page.locator("button.btn-primary:has-text('Adicionar')").click()
                                page.wait_for_timeout(1000)
                        else:
                            self.log("   ↳ Upload pulado (Será inserido manualmente).")

                        page.locator("div.button-save button:has-text('Salvar')").click()
                        page.wait_for_timeout(2000)
                        
                        page.locator("a.back-task").click()
                        page.wait_for_timeout(2000)
                    
                    if not tarefa_tem_carrossel:
                        page.locator("a.next-phase").click()
                        page.wait_for_timeout(1000)
                        page.locator("button:has-text('Continuar sem apontar')").click()
                        self.log(f"✅ {task['nome']} finalizada e avançada!")
                    else:
                        self.log(f"⚠️ {task['nome']} mantida na fase atual (Requer ação manual).")
                    
                    page.wait_for_timeout(2000)

                    if index < len(tarefas) - 1:
                        page.locator("#navigation-next--task").click()
                        page.wait_for_timeout(3000) 

                self.log("🎉 AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
                browser.close()
        
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO: {str(e)}")
        
        finally:
            self.restaurar_botao()

    def restaurar_botao(self):
        self.btn_iniciar.configure(state="normal", text="🚀 INICIAR AUTOMAÇÃO", fg_color="#3179FF")

if __name__ == "__main__":
    app = AppAutomaEkyte()
    app.mainloop()