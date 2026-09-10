import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import re
import sys
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from playwright.sync_api import sync_playwright

# Caminho do config.json
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_BASE_DIR, "config.json")

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# =============================================
# ★ APLICAÇÃO PRINCIPAL
# =============================================
class AppAutomaEkyte(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Robô eKyte - Automação de Tarefas")
        self.geometry("850x720")
        self.resizable(False, False)

        self.pasta_imagens = ""
        self.is_running = False      # Controle de estado do robô
        self.stop_requested = False  # Gatilho do botão de pânico

        self.criar_interface()
        self.carregar_config()

    def criar_interface(self):
        # COLUNA ESQUERDA: CONFIGURAÇÕES
        frame_config = ctk.CTkFrame(self, width=350, corner_radius=10)
        frame_config.pack(side="left", fill="y", padx=20, pady=20)

        ctk.CTkLabel(frame_config, text="Configurações", font=("Segoe UI", 18, "bold")).pack(pady=(20, 15))

        # E-mail
        ctk.CTkLabel(frame_config, text="E-mail do eKyte:", font=("Segoe UI", 12)).pack(anchor="w", padx=20)
        self.entry_email = ctk.CTkEntry(frame_config, width=300, placeholder_text="seu@email.com")
        self.entry_email.pack(padx=20, pady=(0, 15))

        # Senha
        ctk.CTkLabel(frame_config, text="Senha do eKyte:", font=("Segoe UI", 12)).pack(anchor="w", padx=20)
        frame_senha = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_senha.pack(padx=20, pady=(0, 15), fill="x")
        
        self.entry_senha = ctk.CTkEntry(frame_senha, width=255, show="*", placeholder_text="Sua senha")
        self.entry_senha.pack(side="left")
        
        self.btn_eye = ctk.CTkButton(frame_senha, text="👁", width=40, fg_color="#444444", hover_color="#333333", command=self.toggle_senha)
        self.btn_eye.pack(side="right")

        # Pasta
        ctk.CTkLabel(frame_config, text="Pasta das Imagens:", font=("Segoe UI", 12)).pack(anchor="w", padx=20)
        self.btn_pasta = ctk.CTkButton(frame_config, text="Escolher Diretório", fg_color="#10b981", hover_color="#059669", command=self.selecionar_pasta)
        self.btn_pasta.pack(padx=20, pady=(0, 5), fill="x")
        self.lbl_pasta = ctk.CTkLabel(frame_config, text="Nenhuma pasta selecionada", text_color="gray", font=("Segoe UI", 11))
        self.lbl_pasta.pack(padx=20, pady=(0, 15))

        # ==========================================
        # SWITCHES (Lado a Lado)
        # ==========================================
        frame_switches = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_switches.pack(padx=20, pady=10, fill="x")

        # Modo Headless
        self.switch_headless = ctk.CTkSwitch(frame_switches, text="Ocultar Chrome", progress_color="#3179FF")
        self.switch_headless.pack(side="left", expand=True, anchor="w")

        # Modo de Teste
        self.switch_teste = ctk.CTkSwitch(frame_switches, text="Vídeo (dev)", progress_color="#3179FF")
        self.switch_teste.pack(side="right", expand=True, anchor="e")
        # ==========================================

        # Botão Start/Stop
        self.btn_iniciar = ctk.CTkButton(frame_config, text="INICIAR AUTOMAÇÃO", height=50, font=("Segoe UI", 14, "bold"), fg_color="#3179FF", hover_color="#2562d4", command=self.toggle_automacao)
        self.btn_iniciar.pack(padx=20, pady=30, fill="x")

        # COLUNA DIREITA: DADOS E LOGS
        frame_dados = ctk.CTkFrame(self, corner_radius=10)
        frame_dados.pack(side="right", fill="both", expand=True, padx=(0, 20), pady=20)

        ctk.CTkLabel(frame_dados, text="Texto do Planejamento (Google Docs):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.textbox_docs = ctk.CTkTextbox(frame_dados, height=200)
        self.textbox_docs.pack(padx=20, pady=(0, 15), fill="x")

        ctk.CTkLabel(frame_dados, text="Terminal de Execução:", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.textbox_log = ctk.CTkTextbox(frame_dados, fg_color="#1e1e1e", text_color="#3179FF", font=("Consolas", 12))
        self.textbox_log.pack(padx=20, pady=(0, 15), fill="both", expand=True)
        self.textbox_log.configure(state="disabled") 

        # ==========================================
        # BARRA DE PROGRESSO COM TEXTO
        # ==========================================
        frame_progresso = ctk.CTkFrame(frame_dados, fg_color="transparent")
        frame_progresso.pack(padx=20, pady=(0, 20), fill="x")
        
        self.progressbar = ctk.CTkProgressBar(frame_progresso, height=12, progress_color="#3179FF")
        self.progressbar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.progressbar.set(0) # Inicia vazia

        self.lbl_progresso = ctk.CTkLabel(frame_progresso, text="0%", font=("Segoe UI", 12, "bold"), text_color="#3179FF")
        self.lbl_progresso.pack(side="right")
        # ==========================================

    # =============================================
    # ★ CONTROLES DA INTERFACE
    # =============================================
    def toggle_senha(self):
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
            self.salvar_config()

    def log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end") 
        self.textbox_log.configure(state="disabled")
        
    def atualizar_progresso_ui(self, valor, texto):
        """Atualiza a barra de progresso e o texto (Thread safe)"""
        self.progressbar.set(valor)
        self.lbl_progresso.configure(text=texto)

    def carregar_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                email_salvo = cfg.get("email", "")
                pasta_salva = cfg.get("pasta_imagens", "")
                if email_salvo:
                    self.entry_email.insert(0, email_salvo)
                if pasta_salva and os.path.isdir(pasta_salva):
                    self.pasta_imagens = pasta_salva
                    caminho_curto = ".../" + os.path.basename(pasta_salva) if len(pasta_salva) > 30 else pasta_salva
                    self.lbl_pasta.configure(text=caminho_curto)
        except Exception:
            pass

    def salvar_config(self):
        try:
            cfg = {"email": self.entry_email.get().strip(), "pasta_imagens": self.pasta_imagens}
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # =============================================
    # ★ O BOTÃO DO PÂNICO (Start / Stop)
    # =============================================
    def toggle_automacao(self):
        if self.is_running:
            self.stop_requested = True
            self.btn_iniciar.configure(text="🛑 CANCELANDO...", fg_color="#555555", hover_color="#333333", state="disabled")
            self.log("⚠️ Solicitação de parada recebida. Interrompendo imediatamente...")
        else:
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

            self.salvar_config()

            self.log("🔍 Analisando texto para pré-check de imagens...")
            tarefas_preview = self.extrair_dados_do_texto(conteudo_texto)

            if not tarefas_preview:
                self.log("❌ Nenhuma tarefa válida encontrada (ou todas eram vídeos).")
                return

            if not self.pre_check_imagens(tarefas_preview):
                return

            self.is_running = True
            self.stop_requested = False
            self.progressbar.set(0)
            self.lbl_progresso.configure(text="0%")
            self.btn_iniciar.configure(text="🛑 PARAR AUTOMAÇÃO", fg_color="#ef4444", hover_color="#b91c1c")
            
            self.log("✅ Iniciando automação...")
            thread = threading.Thread(target=self.rodar_automacao_core, args=(conteudo_texto,))
            thread.start()

    def verificar_parada(self):
        """Dispara um erro forçado se o usuário clicar no botão de parada."""
        if self.stop_requested:
            raise InterruptedError("Automação abortada manualmente pelo usuário.")

    def pre_check_imagens(self, tarefas):
        faltando = []
        for task in tarefas:
            for tipo_form in task["tipos_formulario"]:
                if "Carrossel" in tipo_form:
                    continue
                imagens = self.buscar_imagens(task["nome"], tipo_form)
                if not imagens:
                    tipo_curto = "Story" if "Story" in tipo_form else "Feed"
                    faltando.append(f"  • Tarefa {task['nome']} ({tipo_curto})")

        if faltando:
            lista_txt = "\n".join(faltando)
            mensagem = f"⚠️ Faltam imagens para {len(faltando)} formulário(s):\n\n{lista_txt}\n\nDeseja continuar mesmo assim?"
            resposta = messagebox.askyesno("Pré-Check de Imagens", mensagem, icon="warning")
            if not resposta:
                self.log("🛑 Automação cancelada pelo usuário (imagens faltando).")
                return False
            else:
                self.log(f"⚠️ Usuário optou por continuar sem {len(faltando)} imagem(ns).")
        return True

    # =============================================
    # ★ LÓGICA CORE (Mapeamento de texto e imagens)
    # =============================================
    def identificar_tipos_formulario(self, texto):
        texto_min = texto.lower()
        tipos = []
        if "feed e story" in texto_min or "story e feed" in texto_min or "stories e feed" in texto_min or "feed e stories" in texto_min:
            tipos.append("Post Único: Feed")
            tipos.append("Post Único: Story, Reel, Short, TikTok")
            return tipos
        if "carrossel" in texto_min and any(p in texto_min for p in ["story", "stories", "storie"]):
            tipos.append("Post Carrossel: Story")
        elif "carrossel" in texto_min:
            tipos.append("Post Carrossel: Feed")
        elif any(palavra in texto_min for palavra in ["story", "stories", "storie"]):
            tipos.append("Post Único: Story, Reel, Short, TikTok")
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

    def buscar_imagens(self, nome_tarefa, tipo_form):
        tipo_form_lower = tipo_form.lower()
        is_story = "story" in tipo_form_lower
        is_feed = "feed" in tipo_form_lower

        if not os.path.exists(self.pasta_imagens):
            return []
            
        todos_arquivos = os.listdir(self.pasta_imagens)
        candidatos = [f for f in todos_arquivos if nome_tarefa in f]
        
        for candidato in candidatos:
            caminho_completo = os.path.join(self.pasta_imagens, candidato)
            nome_sem_ext = os.path.splitext(candidato)[0].lower()
            if os.path.isfile(caminho_completo) and candidato.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if is_story and any(k in nome_sem_ext for k in ["story", "stories", "storie"]):
                    return [caminho_completo]
                if is_feed and "feed" in nome_sem_ext:
                    return [caminho_completo]

        for candidato in candidatos:
            caminho_completo = os.path.join(self.pasta_imagens, candidato)
            nome_sem_ext = os.path.splitext(candidato)[0].lower()
            if os.path.isfile(caminho_completo) and candidato.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                if nome_sem_ext == nome_tarefa: 
                    return [caminho_completo]

        for candidato in candidatos:
            caminho_completo = os.path.join(self.pasta_imagens, candidato)
            nome_sem_ext = candidato.lower()
            if os.path.isdir(caminho_completo):
                if (is_story and any(k in nome_sem_ext for k in ["story", "stories", "storie"])) or \
                   (is_feed and "feed" in nome_sem_ext) or \
                   (nome_sem_ext == nome_tarefa):
                    return [os.path.join(caminho_completo, f) for f in os.listdir(caminho_completo) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

        return []

    # =============================================
    # ★ EXECUÇÃO DO PLAYWRIGHT (Thread Segura)
    # =============================================
    def rodar_automacao_core(self, conteudo_texto):
        try:
            tarefas = self.extrair_dados_do_texto(conteudo_texto)
            email = self.entry_email.get()
            senha = self.entry_senha.get()
            modo_invisivel = bool(self.switch_headless.get())
            total_tarefas = len(tarefas)

            self.log("📦 Inicializando o motor de automação...")
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
                pass 

            with sync_playwright() as p:
                self.log("🌐 Abrindo Navegador...")
                browser = p.chromium.launch(headless=modo_invisivel, slow_mo=500) 
                context = browser.new_context()
                page = context.new_page()

                self.verificar_parada()

                self.log("🔐 Autenticando no eKyte...")
                page.goto("https://app.ekyte.com")
                page.fill("input[name='email']", email)
                page.fill("input[name='password']", senha)
                page.click("button:has-text('Entrar')")
                
                self.verificar_parada()

                # ==========================================
                # LÓGICA INTELIGENTE DE MUDANÇA DE EMPRESA
                # ==========================================
                self.log("🏢 Verificando workspace ativo...")
                btn_empresa = page.locator("div.menu-select-simple__link div[title*='Clique para trocar empresa']")
                btn_empresa.wait_for(state="visible", timeout=15000)
                
                self.verificar_parada()
                
                titulo_atual = btn_empresa.get_attribute("title") or ""
                
                if "Audácia" not in titulo_atual:
                    empresa_nome = titulo_atual.split('.')[0].replace("Empresa: ", "")
                    self.log(f"🔄 Empresa atual: {empresa_nome}. Trocando para Audácia Mkt&Co...")
                    
                    btn_empresa.click()
                    page.wait_for_timeout(1000)
                    
                    self.verificar_parada()
                    
                    page.locator("li.menu-select-simple__item span").filter(has_text=re.compile(r"Audácia", re.IGNORECASE)).click()
                    
                    self.log("⏳ Aguardando recarregamento da página...")
                    page.wait_for_timeout(6000)
                else:
                    self.log("✅ Workspace 'Audácia Mkt&Co' já está ativo.")
                
                self.verificar_parada()

                self.log("📂 Indo para as Tarefas...")
                page.get_by_role("link", name="Tarefas").first.click()
                page.wait_for_timeout(3000) 

                self.verificar_parada()

                # ==========================================
                # LÓGICA DO FILTRO DE DATA
                # ==========================================
                self.log("📅 Verificando filtro de data...")
                btn_filtro_data = page.locator("button.DateRangePickerInput_calendarIcon").first
                btn_filtro_data.wait_for(state="visible", timeout=10000)
                
                span_filtro = btn_filtro_data.locator("span").first
                texto_filtro_atual = span_filtro.inner_text().lower()

                self.verificar_parada()

                if "todo o período" not in texto_filtro_atual:
                    self.log(f"🔄 Filtro atual detectado: '{texto_filtro_atual}'. Ajustando para 'Todo o período'...")
                    btn_filtro_data.click()
                    page.wait_for_timeout(1000) 
                    
                    page.locator("div.date-picker-lateral-infos a").filter(has_text="Todo o período").click()
                    page.wait_for_timeout(500)
                    
                    page.locator("div.console-footer-apply button.btn-primary:has-text('Aplicar')").click()
                    
                    self.log("⏳ Aguardando tarefas carregarem após mudança de filtro...")
                    page.wait_for_timeout(3000) 
                    self.log("✅ Filtro ajustado com sucesso.")
                else:
                    self.log("✅ Filtro de data já está configurado para 'Todo o período'.")
                
                self.verificar_parada()

                page.locator("text='[ROBO]'").first.click()
                page.wait_for_timeout(2000)

                for index, task in enumerate(tarefas):
                    self.verificar_parada()

                    self.log(f"\n🔄 Processando Tarefa {index+1}/{total_tarefas}: {task['nome']}")
                    
                    page.locator(".title-header").click()
                    page.locator(".title-input input").fill(task['nome'])
                    page.keyboard.press("Enter")
                    
                    page.locator(".body-item-taskduedate").click()
                    page.locator("#input-taskDueDate").fill(task['data'] + "/2026")
                    page.keyboard.press("Enter")
                    
                    self.verificar_parada()

                    page.locator(".actions-description").click() 
                    page.locator(".ql-editor[contenteditable='true']").fill(task['descricao'])
                    page.locator("button.button-save-big").click()
                    page.wait_for_timeout(1000)

                    tarefa_tem_carrossel = False

                    for tipo_form in task['tipos_formulario']:
                        self.verificar_parada()

                        self.log(f"   ↳ {tipo_form}")
                        
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
                            imagens = self.buscar_imagens(task['nome'], tipo_form)
                            
                            if imagens:
                                page.locator("div.attachment-task").click()
                                
                                with page.expect_file_chooser() as fc_info:
                                    page.locator("button.upload-button").click(force=True)
                                fc_info.value.set_files(imagens)
                                
                                qtd_imagens = str(len(imagens))
                                self.log(f"   ⏳ Aguardando eKyte validar ({qtd_imagens} arquivo(s))...")
                                
                                self.verificar_parada()
                                page.locator(f"xpath=//div[contains(@class, 'number-ball')]/span[text()='{qtd_imagens}']").wait_for(timeout=30000)
                                self.verificar_parada()

                                page.locator("button.btn-primary:has-text('Adicionar')").click()
                                page.wait_for_timeout(1000)
                        else:
                            self.log("   ↳ (Manual) Upload de Carrossel.")
                        
                        self.verificar_parada()

                        page.locator("div.button-save button:has-text('Salvar')").click()
                        page.wait_for_timeout(2000)
                        
                        page.locator("a.back-task").click()
                        page.wait_for_timeout(2000)
                    
                    self.verificar_parada()

                    if not tarefa_tem_carrossel:
                        page.locator("a.next-phase").click()
                        page.wait_for_timeout(1000)
                        page.locator("button:has-text('Continuar sem apontar')").click()
                        self.log(f"✅ {task['nome']} Avançada!")
                    else:
                        self.log(f"⚠️ {task['nome']} Retida (Aguardando Imagens do Carrossel).")
                    
                    # Atualiza o progresso visualmente enviando o valor e o texto
                    progresso_atual = (index + 1) / total_tarefas
                    pct = int(progresso_atual * 100)
                    texto_progresso = f"{pct}% ({index + 1}/{total_tarefas})"
                    self.after(0, self.atualizar_progresso_ui, progresso_atual, texto_progresso)
                    
                    page.wait_for_timeout(2000)

                    if index < len(tarefas) - 1:
                        self.verificar_parada()
                        page.locator("#navigation-next--task").click()
                        page.wait_for_timeout(3000) 

                self.log("\n🎉 AUTOMAÇÃO FINALIZADA COM SUCESSO!")
                browser.close()
        
        # TRATAMENTO EXCLUSIVO PARA O BOTÃO DE PARADA
        except InterruptedError as e:
            self.log(f"🛑 {str(e)}")
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO: {str(e)}")
        
        finally:
            self.restaurar_botao()

    def restaurar_botao(self):
        self.is_running = False
        self.stop_requested = False
        self.btn_iniciar.configure(state="normal", text="INICIAR AUTOMAÇÃO", fg_color="#3179FF", hover_color="#2562d4")
        if self.progressbar.get() < 1.0:
            self.progressbar.set(0)
            self.lbl_progresso.configure(text="0%")

if __name__ == "__main__":
    app = AppAutomaEkyte()
    app.mainloop()