import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import re
import sys
import json
import base64
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from playwright.sync_api import sync_playwright

# Caminho do config.json
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(_BASE_DIR, "config.json")
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
CAROUSEL_MIN_IMAGES = 2


def chave_ordenacao_natural(valor):
    return tuple(
        (1, int(parte)) if parte.isdigit() else (0, parte.casefold())
        for parte in re.split(r"(\d+)", valor)
    )


def instalar_chromium_se_necessario(avisar):
    with sync_playwright() as playwright:
        executavel = playwright.chromium.executable_path

    if os.path.isfile(executavel):
        return

    avisar("Chromium não encontrado. Instalando automaticamente...")
    from playwright._impl.__main__ import main as playwright_main

    argumentos_originais = sys.argv
    sys.argv = ["playwright", "install", "chromium"]
    try:
        try:
            playwright_main()
        except SystemExit as erro:
            if erro.code not in (None, 0):
                raise RuntimeError("Não foi possível instalar o Chromium.") from erro
    finally:
        sys.argv = argumentos_originais

    avisar("Instalação do Chromium concluída.")

ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")

# =============================================
# ★ APLICAÇÃO PRINCIPAL (CustomTkinter)
# =============================================
class AppAutomaEkyte(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Robô eKyte - Automação de Tarefas")
        self.geometry("980x760")
        self.minsize(900, 680)
        self.resizable(True, True)

        self.pasta_imagens = ""
        self.is_running = False      
        self.stop_requested = False  

        self.criar_interface()
        self.carregar_config()

    def criar_interface(self):
        self.configure(fg_color="#16162a")

        # COLUNA ESQUERDA: CONFIGURAÇÕES
        # Largura aumentada de 260px para 340px para acomodar melhor os botões
        frame_config = ctk.CTkFrame(self, width=340, corner_radius=24, fg_color="#3179FF")
        frame_config.pack(side="left", fill="y", padx=18, pady=18)
        frame_config.pack_propagate(False)

        ctk.CTkLabel(
            frame_config,
            text="Configurações",
            font=("Segoe UI", 18, "bold"),
            text_color="#ffffff",
        ).pack(anchor="w", padx=18, pady=(22, 24))

        # E-mail
        ctk.CTkLabel(
            frame_config,
            text="E-MAIL DO EKYTE",
            font=("Segoe UI", 11, "bold"),
            text_color="#e8efff",
        ).pack(anchor="w", padx=18, pady=(0, 5))
        self.entry_email = ctk.CTkEntry(
            frame_config,
            height=40,
            placeholder_text="seu@email.com",
            fg_color="#3d77df",
            border_color="#77a1f1",
            text_color="#ffffff",
            placeholder_text_color="#c7d8ff",
            corner_radius=8,
        )
        self.entry_email.pack(padx=18, pady=(0, 16), fill="x")

        # Senha
        ctk.CTkLabel(
            frame_config,
            text="SENHA DO EKYTE",
            font=("Segoe UI", 11, "bold"),
            text_color="#e8efff",
        ).pack(anchor="w", padx=18, pady=(0, 5))
        frame_senha = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_senha.pack(padx=18, pady=(0, 16), fill="x")

        self.entry_senha = ctk.CTkEntry(
            frame_senha,
            height=40,
            show="*",
            placeholder_text="Sua senha",
            fg_color="#3d77df",
            border_color="#77a1f1",
            text_color="#ffffff",
            placeholder_text_color="#c7d8ff",
            corner_radius=8,
        )
        self.entry_senha.pack(side="left", fill="x", expand=True)

        self.btn_eye = ctk.CTkButton(
            frame_senha,
            text="👁",
            width=38,
            height=38,
            fg_color="#477edf",
            hover_color="#5c8fe6",
            corner_radius=8,
            command=self.toggle_senha,
        )
        self.btn_eye.pack(side="right", padx=(6, 0))

        # Pasta
        ctk.CTkLabel(
            frame_config,
            text="PASTA DAS IMAGENS",
            font=("Segoe UI", 11, "bold"),
            text_color="#e8efff",
        ).pack(anchor="w", padx=18, pady=(0, 5))
        self.btn_pasta = ctk.CTkButton(
            frame_config,
            text="Escolher Diretório",
            height=38,
            fg_color="#477edf",
            hover_color="#5c8fe6",
            corner_radius=8,
            command=self.selecionar_pasta,
        )
        self.btn_pasta.pack(padx=18, pady=(0, 6), fill="x")
        self.lbl_pasta = ctk.CTkLabel(
            frame_config,
            text="Nenhuma pasta selecionada",
            text_color="#d8e4ff",
            font=("Segoe UI", 10),
            wraplength=280,
            justify="left",
        )
        self.lbl_pasta.pack(padx=18, pady=(0, 16), anchor="w")

        # ==========================================
        # SWITCHES (Lado a Lado)
        # ==========================================
        frame_switches = ctk.CTkFrame(frame_config, fg_color="transparent")
        frame_switches.pack(padx=18, pady=(4, 0), fill="x")

        # Modo Headless
        self.switch_headless = ctk.CTkSwitch(
            frame_switches,
            text="Ocultar Chrome",
            progress_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#e8efff",
            text_color="#ffffff",
            font=("Segoe UI", 11),
        )
        self.switch_headless.pack(side="left", expand=True, anchor="w", pady=(0, 12))

        # Modo de Teste
        self.switch_criar = ctk.CTkSwitch(
            frame_switches,
            text="Criar tarefas",
            progress_color="#ffffff",
            button_color="#ffffff",
            button_hover_color="#e8efff",
            text_color="#ffffff",
            font=("Segoe UI", 11),
        )
        self.switch_criar.pack(side="right", expand=True, anchor="e", pady=(0, 12))
        # ==========================================

        # Botão Start/Stop
        self.btn_iniciar = ctk.CTkButton(
            frame_config,
            text="INICIAR AUTOMAÇÃO",
            height=48,
            font=("Segoe UI", 14, "bold"),
            fg_color="#ffffff",
            text_color="#3179FF",
            hover_color="#f0f0f8",
            corner_radius=14,
            command=self.toggle_automacao,
        )
        self.btn_iniciar.pack(side="bottom", padx=18, pady=18, fill="x")

        # COLUNA DIREITA: DADOS E LOGS
        frame_dados = ctk.CTkFrame(
            self,
            corner_radius=24,
            fg_color="#22223a",
            border_width=1,
            border_color="#3a3a5c",
        )
        frame_dados.pack(side="right", fill="both", expand=True, padx=(0, 18), pady=18)

        # ==========================================
        # HEADER DO DOCS COM BOTÃO DE PADRONIZAR
        # ==========================================
        frame_docs_header = ctk.CTkFrame(frame_dados, fg_color="transparent")
        frame_docs_header.pack(fill="x", padx=24, pady=(24, 8))

        ctk.CTkLabel(
            frame_docs_header,
            text="Texto do Planejamento",
            font=("Segoe UI", 14, "bold"),
            text_color="#f0f0f8",
        ).pack(side="left")

        self.btn_formatar = ctk.CTkButton(
            frame_docs_header,
            text="🧹 Padronizar Texto",
            width=140,
            height=34,
            font=("Segoe UI", 12, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            corner_radius=8,
            command=self.padronizar_texto,
        )
        self.btn_formatar.pack(side="right")
        # ==========================================

        self.textbox_docs = ctk.CTkTextbox(
            frame_dados,
            height=180,
            fg_color="#2e2e4a",
            text_color="#f0f0f8",
            border_width=1,
            border_color="#444466",
            corner_radius=14,
            font=("Segoe UI", 13),
            wrap="word",
        )
        self.textbox_docs.pack(padx=24, pady=(0, 18), fill="x")

        ctk.CTkLabel(
            frame_dados,
            text="Terminal de Execução",
            font=("Segoe UI", 14, "bold"),
            text_color="#f0f0f8",
        ).pack(anchor="w", padx=24, pady=(0, 8))
        self.textbox_log = ctk.CTkTextbox(
            frame_dados,
            fg_color="#16162a",
            text_color="#7eb0ff",
            border_width=1,
            border_color="#3a3a5c",
            corner_radius=14,
            font=("Consolas", 12),
            wrap="word",
        )
        self.textbox_log.pack(padx=24, pady=(0, 12), fill="both", expand=True)
        self.textbox_log.configure(state="disabled")

        # ==========================================
        # BARRA DE PROGRESSO COM TEXTO
        # ==========================================
        frame_progresso = ctk.CTkFrame(frame_dados, fg_color="transparent")
        frame_progresso.pack(padx=24, pady=(4, 22), fill="x")

        self.progressbar = ctk.CTkProgressBar(
            frame_progresso,
            height=10,
            fg_color="#3a3a5c",
            progress_color="#3179FF",
            corner_radius=20,
        )
        self.progressbar.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.progressbar.set(0)

        self.lbl_progresso = ctk.CTkLabel(
            frame_progresso,
            text="0%",
            font=("Segoe UI", 12, "bold"),
            text_color="#3179FF",
        )
        self.lbl_progresso.pack(side="right")
        # ==========================================

    # =============================================
    # ★ CONTROLES DA INTERFACE E ARQUIVO
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
        if threading.current_thread() is threading.main_thread():
            self._append_log(mensagem)
        else:
            self.after(0, self._append_log, mensagem)

    def _append_log(self, mensagem):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", mensagem + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")
        
    def atualizar_progresso_ui(self, valor, texto):
        self.progressbar.set(valor)
        self.lbl_progresso.configure(text=texto)

    def carregar_config(self):
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                
                email_salvo = cfg.get("email", "")
                senha_salva = cfg.get("senha", "")
                pasta_salva = cfg.get("pasta_imagens", "")
                
                if email_salvo:
                    self.entry_email.insert(0, email_salvo)
                
                if senha_salva:
                    try:
                        senha_limpa = base64.b64decode(senha_salva.encode('utf-8')).decode('utf-8')
                        self.entry_senha.insert(0, senha_limpa)
                    except Exception:
                        pass

                if pasta_salva and os.path.isdir(pasta_salva):
                    self.pasta_imagens = pasta_salva
                    caminho_curto = ".../" + os.path.basename(pasta_salva) if len(pasta_salva) > 30 else pasta_salva
                    self.lbl_pasta.configure(text=caminho_curto)
        except Exception:
            pass

    def salvar_config(self):
        try:
            senha_atual = self.entry_senha.get().strip()
            senha_b64 = base64.b64encode(senha_atual.encode('utf-8')).decode('utf-8') if senha_atual else ""

            cfg = {
                "email": self.entry_email.get().strip(), 
                "senha": senha_b64,
                "pasta_imagens": self.pasta_imagens
            }
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # =============================================
    # ★ SANITIZADOR DE TEXTO (Formatação Segura)
    # =============================================
    def padronizar_texto(self):
        try:
            conteudo = self.textbox_docs.get("1.0", "end").strip()
            if not conteudo:
                self.log("⚠️ Cole o texto na caixa antes de clicar em Padronizar.")
                return

            def formata_quebras(linha_texto):
                tags = ["IDEIA/OBJETIVO DO CONTEÚDO:", "TEMA:", "HEADLINE:", "LEGENDA:"]
                for tag in tags:
                    padrao = re.compile(f"(?<!^)({re.escape(tag)})", flags=re.IGNORECASE)
                    linha_texto = padrao.sub(r"\n\1", linha_texto)
                return linha_texto

            novo_conteudo = []
            for linha in conteudo.split('\n'):
                linha = linha.strip()
                if linha:
                    novo_conteudo.extend(formata_quebras(linha).split('\n'))

            texto_limpo = []
            precisa_mes = False
            
            for linha in novo_conteudo:
                linha = linha.strip()
                if not linha:
                    continue
                    
                linha_lower = linha.lower()
                if linha_lower.startswith(("data da publicação", "data da postagem", "dia ", "dia\t", "post ")):
                    match_data = re.search(r'(\d{1,2})(?:\s*/\s*(\d{1,2}))?', linha)
                    if not match_data:
                        texto_limpo.append(linha)
                        continue
                        
                    dia = match_data.group(1).zfill(2)
                    mes = match_data.group(2)
                    
                    if mes:
                        mes = mes.zfill(2)
                        nova_data = f"DATA DA PUBLICAÇÃO: {dia}/{mes}"
                    else:
                        precisa_mes = True
                        nova_data = f"DATA DA PUBLICAÇÃO: {dia}/[MES]"
                        
                    if texto_limpo and texto_limpo[-1] != "":
                        texto_limpo.append("") 
                        
                    texto_limpo.append(nova_data)
                    
                    fim_da_data_index = match_data.end()
                    resto_da_linha = linha[fim_da_data_index:].strip()
                    
                    resto_da_linha = re.sub(r'^(-\s*criativo feed\s*:?|:\s*|-\s*)', '', resto_da_linha, flags=re.IGNORECASE).strip()
                    if resto_da_linha.startswith(':'):
                        resto_da_linha = resto_da_linha[1:].strip()
                        
                    if resto_da_linha:
                        texto_limpo.append(resto_da_linha)
                else:
                    texto_limpo.append(linha)

            texto_final = "\n".join(texto_limpo).strip()

            if precisa_mes:
                mes_escolhido = None
                if self.pasta_imagens and os.path.exists(self.pasta_imagens):
                    for arq in os.listdir(self.pasta_imagens):
                        m = re.search(r"\d{2}-(\d{2})\.", arq)
                        if m:
                            mes_inferido = m.group(1)
                            msg = f"Identificamos que algumas postagens estão sem o mês.\n\nLocalizamos o mês '{mes_inferido}' nos arquivos da sua pasta de imagens.\n\nDeseja aplicar o mês {mes_inferido} para todas as datas incompletas?"
                            if messagebox.askyesno("Mês Ausente Detectado", msg):
                                mes_escolhido = mes_inferido
                            break
                
                if not mes_escolhido:
                    dialog = ctk.CTkInputDialog(text="Qual mês devemos usar para as datas que estão faltando? (Ex: 10)", title="Mês Ausente")
                    res = dialog.get_input()
                    if res and res.strip().isdigit():
                        mes_escolhido = res.strip().zfill(2)
                    else:
                        self.log("⚠️ Padronização parcial: Mês não foi informado.")
                        mes_escolhido = "[MES]"
                        
                texto_final = texto_final.replace("[MES]", mes_escolhido)

            self.textbox_docs.delete("1.0", "end")
            self.textbox_docs.insert("1.0", texto_final)
            self.log("✨ Texto padronizado com sucesso! Revise antes de iniciar.")
            
        except Exception as e:
            self.log(f"❌ Erro ao padronizar: {str(e)}")

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

            self.log("🔍 Extraindo tarefas do texto...")
            tarefas_preview = self.extrair_dados_do_texto(conteudo_texto)

            if not tarefas_preview:
                self.log("❌ Nenhuma tarefa válida encontrada (ou todas eram vídeos).")
                return

            qtd_feed = 0
            qtd_story = 0
            qtd_carrossel = 0

            for task in tarefas_preview:
                for tipo in task['tipos_formulario']:
                    tipo_min = tipo.lower()
                    if 'carrossel' in tipo_min:
                        qtd_carrossel += 1
                    elif 'story' in tipo_min or 'reel' in tipo_min or 'tiktok' in tipo_min or 'short' in tipo_min:
                        qtd_story += 1
                    elif 'feed' in tipo_min:
                        qtd_feed += 1

            modo_texto = "CRIANDO NOVAS TAREFAS" if self.switch_criar.get() else "EDITANDO TEMPLATE [ROBO]"

            msg_resumo = (
                f"Modo Atual: {modo_texto}\n\n"
                f"O robô identificou {len(tarefas_preview)} postagem(ns) neste lote.\n\n"
                f"Isso irá gerar os seguintes formulários:\n"
                f"   • Feed: {qtd_feed}\n"
                f"   • Stories/Reels: {qtd_story}\n"
                f"   • Carrossel: {qtd_carrossel}\n\n"
                "Deseja iniciar a automação para estas tarefas?"
            )
            
            resposta_resumo = messagebox.askyesno("Resumo das Tarefas", msg_resumo, icon="info")
            if not resposta_resumo:
                self.log("🛑 Automação cancelada pelo usuário no resumo de tarefas.")
                return

            if not self.pre_check_imagens(tarefas_preview):
                return

            self.is_running = True
            self.stop_requested = False
            self.progressbar.set(0)
            self.lbl_progresso.configure(text="0%")
            self.btn_iniciar.configure(text="🛑 PARAR AUTOMAÇÃO", fg_color="#ef4444", text_color="#ffffff", hover_color="#b91c1c")
            
            self.log("✅ Iniciando automação...")
            thread = threading.Thread(target=self.rodar_automacao_core, args=(conteudo_texto,))
            thread.start()

    def verificar_parada(self):
        if self.stop_requested:
            raise InterruptedError("Automação abortada manualmente pelo usuário.")

    def pre_check_imagens(self, tarefas):
        faltando = []
        for task in tarefas:
            for tipo_form in task["tipos_formulario"]:
                imagens = self.buscar_imagens(task["nome"], tipo_form)
                is_carrossel = "carrossel" in tipo_form.lower()
                if is_carrossel and len(imagens) < CAROUSEL_MIN_IMAGES:
                    faltando.append(
                        f"  • {task['nome']} (Carrossel: {len(imagens)}/{CAROUSEL_MIN_IMAGES} imagens)"
                    )
                elif not is_carrossel and not imagens:
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
    def extrair_workspace_da_pasta(self, caminho_pasta):
        try:
            caminho_limpo = caminho_pasta.replace("/", "\\")
            partes = caminho_limpo.split("\\")
            for i, parte in enumerate(partes):
                if parte.lower() == "planejamentos clientes":
                    if i + 1 < len(partes):
                        return partes[i + 1]
        except Exception as e:
            self.log(f"⚠️ Erro ao extrair workspace da pasta: {e}")
        return None


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
                self.log("Tarefa ignorada (conteúdo em vídeo detectado).")
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
        tipo_form_lower = tipo_form.casefold()
        is_carrossel = "carrossel" in tipo_form_lower or "carousel" in tipo_form_lower
        is_story = any(palavra in tipo_form_lower for palavra in ("story", "stories", "storie"))
        is_feed = "feed" in tipo_form_lower

        if not os.path.isdir(self.pasta_imagens):
            return []

        try:
            todos_arquivos = sorted(os.listdir(self.pasta_imagens), key=chave_ordenacao_natural)
        except OSError:
            return []

        def normalizar_nome(valor):
            return re.sub(r"[^a-z0-9]+", "-", valor.casefold()).strip("-")

        nome_tarefa_normalizado = normalizar_nome(nome_tarefa)
        partes_tarefa = nome_tarefa_normalizado.split("-")

        def contem_tarefa(nome):
            partes_nome = normalizar_nome(nome).split("-")
            return any(
                partes_nome[indice:indice + len(partes_tarefa)] == partes_tarefa
                for indice in range(max(0, len(partes_nome) - len(partes_tarefa) + 1))
            )

        def listar_imagens(pasta):
            try:
                nomes_imagem = [
                    nome for nome in os.listdir(pasta)
                    if os.path.isfile(os.path.join(pasta, nome))
                    and nome.casefold().endswith(IMAGE_EXTENSIONS)
                ]
            except OSError:
                return []
            return [
                os.path.join(pasta, nome)
                for nome in sorted(nomes_imagem, key=chave_ordenacao_natural)
            ]

        pastas = [
            nome for nome in todos_arquivos
            if os.path.isdir(os.path.join(self.pasta_imagens, nome))
        ]

        if is_carrossel:
            pastas_carrossel = []
            pastas_compativeis = []
            palavras_story = ("story", "stories", "storie")

            for nome in pastas:
                if not contem_tarefa(nome):
                    continue

                partes_nome = normalizar_nome(nome).split("-")
                tem_story = any(palavra in partes_nome for palavra in palavras_story)
                tem_feed = "feed" in partes_nome
                tem_carrossel = "carrossel" in partes_nome or "carousel" in partes_nome

                if tem_carrossel:
                    if is_story and tem_feed and not tem_story:
                        continue
                    if is_feed and tem_story and not tem_feed:
                        continue
                    prioridade = 0 if (is_story and tem_story) or (is_feed and tem_feed) else 1
                    pastas_carrossel.append((prioridade, nome))
                elif (
                    normalizar_nome(nome) == nome_tarefa_normalizado
                    or (is_story and tem_story)
                    or (is_feed and tem_feed)
                ):
                    pastas_compativeis.append(nome)

            pastas_carrossel.sort(key=lambda item: (item[0], chave_ordenacao_natural(item[1])))
            for _, nome in pastas_carrossel:
                imagens = listar_imagens(os.path.join(self.pasta_imagens, nome))
                if len(imagens) >= CAROUSEL_MIN_IMAGES:
                    return imagens

            for nome in sorted(pastas_compativeis, key=chave_ordenacao_natural):
                imagens = listar_imagens(os.path.join(self.pasta_imagens, nome))
                if len(imagens) >= CAROUSEL_MIN_IMAGES:
                    return imagens
            return []

        candidatos = [nome for nome in todos_arquivos if nome_tarefa.casefold() in nome.casefold()]
        arquivos_imagem = [
            nome for nome in candidatos
            if os.path.isfile(os.path.join(self.pasta_imagens, nome))
            and nome.casefold().endswith(IMAGE_EXTENSIONS)
        ]

        for nome in arquivos_imagem:
            nome_sem_extensao = os.path.splitext(nome)[0].casefold()
            if is_story and any(palavra in nome_sem_extensao for palavra in ("story", "stories", "storie")):
                return [os.path.join(self.pasta_imagens, nome)]
            if is_feed and "feed" in nome_sem_extensao:
                return [os.path.join(self.pasta_imagens, nome)]

        for nome in arquivos_imagem:
            if os.path.splitext(nome)[0].casefold() == nome_tarefa.casefold():
                return [os.path.join(self.pasta_imagens, nome)]

        for nome in pastas:
            if not contem_tarefa(nome):
                continue
            partes_nome = normalizar_nome(nome).split("-")
            tem_story = any(palavra in partes_nome for palavra in ("story", "stories", "storie"))
            if (
                (is_story and tem_story)
                or (is_feed and "feed" in partes_nome)
                or normalizar_nome(nome) == nome_tarefa_normalizado
            ):
                imagens = listar_imagens(os.path.join(self.pasta_imagens, nome))
                if imagens:
                    return imagens

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
            criar_tarefas = bool(self.switch_criar.get())
            total_tarefas = len(tarefas)

            self.log("📦 Inicializando o motor de automação...")
            instalar_chromium_se_necessario(self.log)

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

                # ==========================================
                # NOVO BLOCO: CRIAÇÃO E DUPLICAÇÃO
                # ==========================================
                if criar_tarefas:
                    self.log("➕ Iniciando fluxo de Criação de Tarefas...")
                    
                    self.log("Criando tarefa base [ROBO]...")
                    page.locator("a[title='Adicionar tarefa']").first.click()
                    page.wait_for_timeout(2000)
                    self.verificar_parada()

                    self.log("Selecionando equipe base (Equipe 1)...")
                    page.locator("input[placeholder='Pesquisar']").first.fill("Equipe 1")
                    page.wait_for_timeout(1000)
                    page.locator(".task-template-item").filter(has_text="Equipe 1").first.click()
                    page.wait_for_timeout(2000)
                    self.verificar_parada()

                    page.locator("input[name='title']").fill("[ROBO]")
                    
                    workspace_name = self.extrair_workspace_da_pasta(self.pasta_imagens)
                    if workspace_name:
                        self.log(f"Definindo Workspace para: {workspace_name}")
                        page.locator(".Select-multi-value-wrapper").click()
                        page.wait_for_timeout(1000)
                        page.keyboard.type(workspace_name)
                        page.wait_for_timeout(1000)
                        page.keyboard.press("Enter")
                    else:
                        self.log("⚠️ Não foi possível determinar o Workspace pela pasta. A tarefa será criada no Workspace atual.")
                    
                    self.verificar_parada()
                    page.locator("button.btn-primary:has-text('Criar')").click()
                    self.log("✅ Tarefa base [ROBO] criada.")
                    page.wait_for_timeout(3000)
                    
                    duplications_needed = total_tarefas - 1
                    if duplications_needed > 0:
                        self.log(f"🔄 Duplicando tarefa base {duplications_needed} vezes...")
                        for i in range(duplications_needed):
                            self.verificar_parada()
                            task_row = page.locator("text='[ROBO]'").first.locator("xpath=ancestor::tr")
                            task_row.locator("i.material-icons[title='Duplicar']").click(force=True)
                            page.wait_for_timeout(2000)
                            
                            page.locator("button.btn-primary:has-text('Avançar')").click()
                            page.wait_for_timeout(1000)
                            page.locator("button.btn-primary:has-text('Criar')").click()
                            self.log(f"✅ Duplicata {i+1}/{duplications_needed} criada.")
                            page.wait_for_timeout(3000)
                    
                    self.log("✅ Estrutura de tarefas pronta. Iniciando preenchimento...")
                # ==========================================

                page.locator("text='[ROBO]'").first.click()
                page.wait_for_timeout(2000)

                for index, task in enumerate(tarefas):
                    self.verificar_parada()

                    self.log(f"\n🔄 Processando Tarefa {index+1}/{total_tarefas}: {task['nome']}")
                    
                    titulo_header = page.locator(".title-header").first
                    titulo_header.wait_for(state="visible", timeout=10000)
                    texto_titulo_atual = titulo_header.inner_text()
                    
                    if "[ROBO]" not in texto_titulo_atual:
                        self.log(f"⚠️ Atenção: A tarefa aberta '{texto_titulo_atual}' não é o template [ROBO].")
                        self.log("🔙 Fechando tarefa atual e buscando o próximo [ROBO] na lista...")
                        
                        page.locator("li.close-modal").first.click()
                        page.wait_for_timeout(2000)
                        
                        self.verificar_parada()
                        
                        page.locator("text='[ROBO]'").first.click()
                        page.wait_for_timeout(3000)
                        
                        titulo_header.wait_for(state="visible", timeout=10000)

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
                        
                        if "carrossel" in tipo_form.lower():
                            tarefa_tem_carrossel = True
                        
                        page.locator("div.tab span:has-text('Formulários')").click()
                        page.wait_for_timeout(2000) 
                        
                        page.locator("a[title='Adicionar formulário']").first.click()
                        page.wait_for_timeout(3000) 
                        
                        page.locator("span.Select-value-label-tag", has_text=tipo_form).click()
                        page.wait_for_timeout(1000)
                        page.locator("span.span-tab", has_text="CRIAÇÃO").click()

                        is_carrossel = "carrossel" in tipo_form.lower()
                        imagens = self.buscar_imagens(task['nome'], tipo_form)

                        if is_carrossel and len(imagens) < CAROUSEL_MIN_IMAGES:
                            self.log(
                                f"Carrossel da tarefa {task['nome']} sem envio: "
                                f"selecione pelo menos {CAROUSEL_MIN_IMAGES} imagens."
                            )
                        elif imagens:
                            # ==========================================
                            # LOGICA DE UPLOAD (Simples x Sequencial)
                            # ==========================================
                            if is_carrossel:
                                self.log(f"   Iniciando upload sequencial de {len(imagens)} imagens do Carrossel...")
                                for i, imagem_path in enumerate(imagens):
                                    self.verificar_parada()
                                    page.locator("div.attachment-task").click()
                                    with page.expect_file_chooser() as fc_info:
                                        page.locator("button.upload-button").click(force=True)
                                    fc_info.value.set_files([imagem_path])
                                    
                                    current_count = str(i + 1)
                                    self.log(f"   ⏳ Enviando arquivo {current_count}/{len(imagens)}...")
                                    page.locator(f"xpath=//div[contains(@class, 'number-ball')]/span[text()='{current_count}']").wait_for(timeout=60000)
                                
                                self.log("   ✅ Upload do Carrossel concluído.")
                            else:
                                page.locator("div.attachment-task").click()
                                with page.expect_file_chooser() as fc_info:
                                    page.locator("button.upload-button").click(force=True)
                                fc_info.value.set_files(imagens)

                                qtd_imagens = str(len(imagens))
                                self.log(f"Aguardando o eKyte validar {qtd_imagens} arquivo(s)...")

                                self.verificar_parada()
                                page.locator(f"xpath=//div[contains(@class, 'number-ball')]/span[text()='{qtd_imagens}']").wait_for(timeout=30000)
                                self.verificar_parada()

                                if any(k in tipo_form.lower() for k in ["story", "stories", "storie"]):
                                    self.log("Aguardando o processamento das imagens do Story...")
                                    page.wait_for_timeout(2500)
                                    self.verificar_parada()

                            page.locator("button.btn-primary:has-text('Adicionar')").click()
                            page.wait_for_timeout(1000)
                        
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
                        self.log(f"Tarefa {task['nome']} retida para revisão do carrossel.")
                    
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
        
        except InterruptedError as e:
            self.log(f"🛑 {str(e)}")
        except Exception as e:
            self.log(f"❌ ERRO CRÍTICO: {str(e)}")
        
        finally:
            self.restaurar_botao()

    def restaurar_botao(self):
        self.is_running = False
        self.stop_requested = False
        self.btn_iniciar.configure(state="normal", text="INICIAR AUTOMAÇÃO", fg_color="#ffffff", text_color="#3179FF", hover_color="#f0f0f8")
        if self.progressbar.get() < 1.0:
            self.progressbar.set(0)
            self.lbl_progresso.configure(text="0%")

if __name__ == "__main__":
    app = AppAutomaEkyte()
    app.mainloop()