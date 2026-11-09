import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

import re
import sys
import json
import base64
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import eel
from playwright.sync_api import sync_playwright

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

stop_requested = False
is_running = False

eel.init('web')

def log_to_ui(mensagem):
    print(mensagem)
    eel.atualizarLog(mensagem)

# ==========================================
# EXPORTS (Chamadas do JavaScript)
# ==========================================
@eel.expose
def carregar_config_py():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            
            senha_decodificada = ""
            if cfg.get("senha", ""):
                try:
                    senha_decodificada = base64.b64decode(cfg.get("senha").encode('utf-8')).decode('utf-8')
                except:
                    pass

            return {
                "email": cfg.get("email", ""),
                "senha": senha_decodificada,
                "pasta_imagens": cfg.get("pasta_imagens", "")
            }
    except Exception:
        pass
    return None

def salvar_config(email, senha, pasta):
    try:
        senha_b64 = base64.b64encode(senha.encode('utf-8')).decode('utf-8') if senha else ""
        cfg = {"email": email.strip(), "senha": senha_b64, "pasta_imagens": pasta}
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

@eel.expose
def salvar_config_py(email, senha, pasta):
    salvar_config(email, senha, pasta)

@eel.expose
def selecionar_pasta_py():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens")
    root.destroy()
    return pasta

@eel.expose
def parar_automacao_py():
    global stop_requested
    stop_requested = True
    log_to_ui("⚠️ Solicitação de parada recebida. Interrompendo imediatamente...")

@eel.expose
def padronizar_texto_py(conteudo, pasta_imagens):
    if not conteudo:
        log_to_ui("⚠️ Cole o texto na caixa antes de clicar em Padronizar.")
        return ""
    
    try:
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
            if pasta_imagens and os.path.exists(pasta_imagens):
                for arq in os.listdir(pasta_imagens):
                    m = re.search(r"\d{2}-(\d{2})\.", arq)
                    if m:
                        mes_inferido = m.group(1)
                        root = tk.Tk()
                        root.withdraw()
                        root.attributes('-topmost', True)
                        msg = f"Identificamos postagens sem mês.\n\nLocalizamos o mês '{mes_inferido}' na sua pasta.\nDeseja aplicá-lo?"
                        if messagebox.askyesno("Mês Ausente", msg):
                            mes_escolhido = mes_inferido
                        root.destroy()
                        break
            
            if not mes_escolhido:
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)
                try:
                    resposta = simpledialog.askstring(
                        "Mês Ausente",
                        "Qual mês devemos usar para as datas que estão faltando? (Ex: 10)",
                        parent=root,
                    )
                finally:
                    root.destroy()

                if resposta and resposta.strip().isdigit():
                    mes_escolhido = resposta.strip().zfill(2)
                else:
                    log_to_ui("Padronização parcial: mês não informado.")
                    mes_escolhido = "[MES]"
                    
            texto_final = texto_final.replace("[MES]", mes_escolhido)

        log_to_ui("✨ Texto padronizado com sucesso! Revise antes de iniciar.")
        return texto_final
    except Exception as e:
        log_to_ui(f"❌ Erro ao padronizar: {str(e)}")
        return conteudo

@eel.expose
def iniciar_automacao_py(email, senha, pasta, texto, modo_invisivel, criar_tarefas):
    global stop_requested, is_running
    
    if not email or not senha:
        log_to_ui("❌ ERRO: Preencha e-mail e senha.")
        eel.restaurarBotoes()
        return
    if not pasta:
        log_to_ui("❌ ERRO: Selecione a pasta de imagens.")
        eel.restaurarBotoes()
        return
    if not texto:
        log_to_ui("❌ ERRO: Cole o texto do Google Docs.")
        eel.restaurarBotoes()
        return

    salvar_config(email, senha, pasta)
    log_to_ui("🔍 Analisando texto...")
    tarefas_preview = extrair_dados_do_texto(texto)

    if not tarefas_preview:
        log_to_ui("❌ Nenhuma tarefa válida encontrada.")
        eel.restaurarBotoes()
        return
        
    equipe_selecionada = "Equipe 1"
    
    if criar_tarefas:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        resposta_equipe = simpledialog.askstring(
            "Seleção de Equipe",
            "Qual equipe deve ser utilizada para criar as tarefas? (Ex: Equipe 1, Equipe 2)",
            initialvalue="Equipe 1",
            parent=root
        )
        root.destroy()
        
        if not resposta_equipe:
            log_to_ui("🛑 Automação cancelada. A equipe não foi informada.")
            eel.restaurarBotoes()
            return
        equipe_selecionada = resposta_equipe.strip()

    qtd_feed = sum(1 for t in tarefas_preview for f in t['tipos_formulario'] if 'feed' in f.lower() and 'carrossel' not in f.lower())
    qtd_story = sum(1 for t in tarefas_preview for f in t['tipos_formulario'] if any(x in f.lower() for x in ['story', 'reel', 'tiktok', 'short']) and 'carrossel' not in f.lower())
    qtd_carrossel = sum(1 for t in tarefas_preview for f in t['tipos_formulario'] if 'carrossel' in f.lower())

    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    modo_texto = f"CRIANDO NOVAS TAREFAS ({equipe_selecionada})" if criar_tarefas else "EDITANDO TEMPLATES EXISTENTES [ROBO]"
    msg_resumo = (
        f"Modo: {modo_texto}\n\n"
        f"Foram identificadas {len(tarefas_preview)} postagem(ns).\n\n"
        f"Formulários gerados:\n"
        f"   • Feed: {qtd_feed}\n"
        f"   • Stories/Reels: {qtd_story}\n"
        f"   • Carrossel: {qtd_carrossel}\n\n"
        "Deseja iniciar a automação?"
    )
    if not messagebox.askyesno("Resumo das Tarefas", msg_resumo, icon="info"):
        log_to_ui("🛑 Automação cancelada pelo usuário no resumo.")
        eel.restaurarBotoes()
        root.destroy()
        return

    if not pre_check_imagens(tarefas_preview, pasta):
        eel.restaurarBotoes()
        root.destroy()
        return
        
    root.destroy()
    stop_requested = False
    is_running = True
    eel.atualizarProgresso(0, "0%")
    
    log_to_ui("✅ Iniciando automação...")
    thread = threading.Thread(target=rodar_automacao_core, args=(email, senha, pasta, texto, modo_invisivel, criar_tarefas, equipe_selecionada))
    thread.start()

# ==========================================
# LÓGICA ESTRUTURAL
# ==========================================
def verificar_parada():
    global stop_requested
    if stop_requested:
        raise InterruptedError("Automação abortada manualmente pelo usuário.")

def extrair_workspace_da_pasta(caminho_pasta):
    try:
        partes = os.path.normpath(caminho_pasta).split(os.sep)
        for i, parte in enumerate(partes):
            # Usando 'in' fica muito mais seguro contra espaços extras ou formatações invisíveis
            if "planejamentos clientes" in parte.lower():
                if i + 1 < len(partes):
                    return partes[i + 1]
    except Exception as e:
        log_to_ui(f"⚠️ Erro ao extrair workspace da pasta: {e}")
    return None

def pre_check_imagens(tarefas, pasta_imagens):
    faltando = []
    for task in tarefas:
        for tipo_form in task["tipos_formulario"]:
            imagens = buscar_imagens(task["nome"], tipo_form, pasta_imagens)
            is_carrossel = "carrossel" in tipo_form.lower()
            if is_carrossel and len(imagens) < CAROUSEL_MIN_IMAGES:
                faltando.append(
                    f"  • {task['nome']} (Carrossel: {len(imagens)}/{CAROUSEL_MIN_IMAGES} imagens)"
                )
            elif not is_carrossel and not imagens:
                tipo_curto = "Story" if "Story" in tipo_form else "Feed"
                faltando.append(f"  • {task['nome']} ({tipo_curto})")

    if faltando:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        lista_txt = "\n".join(faltando)
        msg = f"⚠️ Faltam imagens para {len(faltando)} formulário(s):\n\n{lista_txt}\n\nDeseja continuar mesmo assim?"
        res = messagebox.askyesno("Pré-Check", msg, icon="warning")
        root.destroy()
        if not res:
            log_to_ui("🛑 Automação cancelada (imagens faltando).")
            return False
        else:
            log_to_ui(f"⚠️ Continuado sem {len(faltando)} imagem(ns).")
    return True

def identificar_tipos_formulario(texto):
    texto_min = texto.lower()
    tipos = []
    if any(x in texto_min for x in ["feed e story", "story e feed", "stories e feed", "feed e stories"]):
        return ["Post Único: Feed", "Post Único: Story, Reel, Short, TikTok"]
    if "carrossel" in texto_min and any(p in texto_min for p in ["story", "stories", "storie"]):
        return ["Post Carrossel: Story"]
    if "carrossel" in texto_min:
        return ["Post Carrossel: Feed"]
    if any(p in texto_min for p in ["story", "stories", "storie"]):
        return ["Post Único: Story, Reel, Short, TikTok"]
    return ["Post Único: Feed"]

def extrair_dados_do_texto(conteudo):
    blocos = conteudo.split("DATA DA PUBLICAÇÃO:")[1:] 
    tarefas = []
    for bloco in blocos:
        texto_completo = "DATA DA PUBLICAÇÃO:" + bloco.strip()
        if "vídeo" in texto_completo.lower() or "video" in texto_completo.lower():
            log_to_ui("Tarefa ignorada (conteúdo em vídeo detectado).")
            continue 
        data_match = re.search(r'(\d{2}/\d{2})', bloco)
        if data_match:
            data_formatada = data_match.group(1) 
            nome_tarefa = data_formatada.replace('/', '-') 
            tarefas.append({
                "nome": nome_tarefa,
                "data": data_formatada,
                "descricao": texto_completo,
                "tipos_formulario": identificar_tipos_formulario(texto_completo) 
            })
    return tarefas

def buscar_imagens(nome_tarefa, tipo_form, pasta_imagens):
    tipo_form_lower = tipo_form.casefold()
    is_carrossel = "carrossel" in tipo_form_lower or "carousel" in tipo_form_lower
    is_story = any(palavra in tipo_form_lower for palavra in ("story", "stories", "storie"))
    is_feed = "feed" in tipo_form_lower

    if not os.path.isdir(pasta_imagens):
        return []

    try:
        todos_arquivos = sorted(os.listdir(pasta_imagens), key=chave_ordenacao_natural)
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
        if os.path.isdir(os.path.join(pasta_imagens, nome))
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
            imagens = listar_imagens(os.path.join(pasta_imagens, nome))
            if len(imagens) >= CAROUSEL_MIN_IMAGES:
                return imagens

        for nome in sorted(pastas_compativeis, key=chave_ordenacao_natural):
            imagens = listar_imagens(os.path.join(pasta_imagens, nome))
            if len(imagens) >= CAROUSEL_MIN_IMAGES:
                return imagens
        return []

    candidatos = [nome for nome in todos_arquivos if nome_tarefa.casefold() in nome.casefold()]
    arquivos_imagem = [
        nome for nome in candidatos
        if os.path.isfile(os.path.join(pasta_imagens, nome))
        and nome.casefold().endswith(IMAGE_EXTENSIONS)
    ]

    for nome in arquivos_imagem:
        nome_sem_extensao = os.path.splitext(nome)[0].casefold()
        if is_story and any(palavra in nome_sem_extensao for palavra in ("story", "stories", "storie")):
            return [os.path.join(pasta_imagens, nome)]
        if is_feed and "feed" in nome_sem_extensao:
            return [os.path.join(pasta_imagens, nome)]

    for nome in arquivos_imagem:
        if os.path.splitext(nome)[0].casefold() == nome_tarefa.casefold():
            return [os.path.join(pasta_imagens, nome)]

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
            imagens = listar_imagens(os.path.join(pasta_imagens, nome))
            if imagens:
                return imagens

    return []

# ==========================================
# MOTOR PLAYWRIGHT EKYTE
# ==========================================
def rodar_automacao_core(email, senha, pasta_imagens, conteudo_texto, modo_invisivel, criar_tarefas, equipe_selecionada):
    global is_running, stop_requested
    try:
        tarefas = extrair_dados_do_texto(conteudo_texto)
        total_tarefas = len(tarefas)

        log_to_ui("Inicializando o motor de automação...")
        instalar_chromium_se_necessario(log_to_ui)

        with sync_playwright() as p:
            log_to_ui("🌐 Abrindo Navegador...")
            browser = p.chromium.launch(headless=modo_invisivel, slow_mo=500) 
            context = browser.new_context()
            page = context.new_page()

            verificar_parada()

            log_to_ui("🔐 Autenticando no eKyte...")
            page.goto("https://app.ekyte.com")
            page.fill("input[name='email']", email)
            page.fill("input[name='password']", senha)
            page.click("button:has-text('Entrar')")
            
            verificar_parada()

            log_to_ui("🏢 Verificando workspace ativo...")
            btn_empresa = page.locator("div.menu-select-simple__link div[title*='Clique para trocar empresa']")
            btn_empresa.wait_for(state="visible", timeout=15000)
            
            verificar_parada()
            titulo_atual = btn_empresa.get_attribute("title") or ""
            if "Audácia" not in titulo_atual:
                empresa_nome = titulo_atual.split('.')[0].replace("Empresa: ", "")
                log_to_ui(f"🔄 Empresa atual: {empresa_nome}. Trocando para Audácia Mkt&Co...")
                btn_empresa.click()
                page.wait_for_timeout(1000)
                verificar_parada()
                page.locator("li.menu-select-simple__item span").filter(has_text=re.compile(r"Audácia", re.IGNORECASE)).click()
                log_to_ui("⏳ Aguardando recarregamento...")
                page.wait_for_timeout(6000)
            else:
                log_to_ui("✅ Workspace 'Audácia Mkt&Co' já está ativo.")
            
            verificar_parada()

            log_to_ui("📂 Indo para as Tarefas...")
            page.get_by_role("link", name="Tarefas").first.click()
            page.wait_for_timeout(3000) 

            verificar_parada()

            log_to_ui("📅 Verificando filtro de data...")
            btn_filtro_data = page.locator("button.DateRangePickerInput_calendarIcon").first
            btn_filtro_data.wait_for(state="visible", timeout=10000)
            texto_filtro_atual = btn_filtro_data.locator("span").first.inner_text().lower()

            verificar_parada()

            if "todo o período" not in texto_filtro_atual:
                log_to_ui(f"🔄 Filtro atual: '{texto_filtro_atual}'. Ajustando para 'Todo o período'...")
                btn_filtro_data.click()
                page.wait_for_timeout(1000) 
                page.locator("div.date-picker-lateral-infos a").filter(has_text="Todo o período").click()
                page.wait_for_timeout(500)
                page.locator("button.btn-primary", has_text=re.compile(r"^Aplicar$")).first.click()
                page.wait_for_timeout(3000) 
                log_to_ui("✅ Filtro ajustado com sucesso.")
            
            verificar_parada()

            # ==========================================
            # NOVO BLOCO: CRIAÇÃO E DUPLICAÇÃO
            # ==========================================
            if criar_tarefas:
                log_to_ui("➕ Iniciando fluxo de Criação de Tarefas...")
                log_to_ui("Criando tarefa base [ROBO]...")
                page.locator("a[title='Adicionar tarefa']").first.click()
                page.locator("text='Adicionar tarefa'").first.wait_for(state="visible", timeout=10000)
                page.wait_for_timeout(1500)
                verificar_parada()

                log_to_ui(f"Selecionando equipe base ({equipe_selecionada})...")
                page.locator("input[placeholder='Buscar tipo de tarefa']").first.fill(equipe_selecionada)
                page.wait_for_timeout(1500)
                cartao_equipe = page.locator("div.task-type-item").filter(has_text=equipe_selecionada).first
                if not cartao_equipe.is_visible(timeout=2000):
                    cartao_equipe = page.locator("div").filter(has_text=equipe_selecionada).nth(-1)
                
                cartao_equipe.click(force=True)
                page.wait_for_timeout(2500)
                verificar_parada()

                log_to_ui("Preenchendo detalhes...")
                page.locator("input[name='title']").wait_for(state="visible", timeout=10000)
                page.locator("input[name='title']").fill("[ROBO]")
                
                workspace_name = extrair_workspace_da_pasta(pasta_imagens)
                
                if workspace_name:
                    log_to_ui(f"Definindo Workspace para: {workspace_name}")
                    try:
                        # 1. Clica exatamente na template de valor do Workspace mapeada por você
                        page.locator("label", has_text="Workspace").locator("xpath=..").locator(".Select-value-template").first.click(force=True)
                    except:
                        # Fallback
                        page.locator(".Select-value-template").first.click(force=True)
                        
                    page.wait_for_timeout(1500)
                    
                    try:
                        # 2. Preenche DIRETAMENTE a barra de pesquisa flutuante pelo ID exato
                        barra_pesquisa = page.locator("input#Select-input").first
                        barra_pesquisa.fill(workspace_name)
                    except:
                        # Fallback se a barra demorar a focar
                        page.keyboard.type(workspace_name)
                        
                    page.wait_for_timeout(1500)
                    page.keyboard.press("Enter")
                else:
                    log_to_ui("⚠️ Workspace não extraído. Usando o atual.")
                
                verificar_parada()
                
                # CLIQUE NO FLUXO DE TRABALHO ANTES DE CRIAR
                log_to_ui("Acessando aba Fluxo de Trabalho...")
                page.locator("span", has_text="Fluxo de trabalho").first.click(force=True)
                page.wait_for_timeout(1000)
                
                # Clique em Criar
                page.locator("button.btn-primary", has_text=re.compile(r"^Criar$")).first.click()
                
                log_to_ui("✅ Tarefa base [ROBO] criada.")
                page.wait_for_timeout(3500)
                
                duplications_needed = total_tarefas - 1
                if duplications_needed > 0:
                    log_to_ui(f"🔄 Duplicando tarefa base {duplications_needed} vezes...")
                    for i in range(duplications_needed):
                        verificar_parada()
                        linha_tarefa = page.locator("text='[ROBO]'").first.locator("xpath=ancestor::tr")
                        linha_tarefa.locator("i.material-icons[title='Duplicar']").click(force=True)
                        page.locator("input[name='title']").wait_for(state="visible", timeout=10000)
                        page.wait_for_timeout(1500)
                        
                        # Acessa Fluxo de Trabalho na duplicação também, como medida de segurança
                        page.locator("span", has_text="Fluxo de trabalho").first.click(force=True)
                        page.wait_for_timeout(1000)
                        
                        page.locator("button.btn-primary", has_text=re.compile(r"^Criar$")).first.click()
                        log_to_ui(f"✅ Duplicata {i+1}/{duplications_needed} criada.")
                        page.wait_for_timeout(3500)
                
                log_to_ui("✅ Estrutura de tarefas pronta. Iniciando preenchimento...")
            # ==========================================
            
            page.locator("text='[ROBO]'").first.click()
            page.wait_for_timeout(2000)

            for index, task in enumerate(tarefas):
                verificar_parada()
                
                log_to_ui(f"\n🔄 Processando Tarefa {index+1}/{total_tarefas}: {task['nome']}")
                
                titulo_header = page.locator(".title-header").first
                titulo_header.wait_for(state="visible", timeout=10000)
                texto_titulo_atual = titulo_header.inner_text()
                
                if "[ROBO]" not in texto_titulo_atual:
                    log_to_ui(f"⚠️ Atenção: A tarefa '{texto_titulo_atual}' não é o template.")
                    log_to_ui("🔙 Buscando o próximo [ROBO] na lista...")
                    page.locator("li.close-modal").first.click()
                    page.wait_for_timeout(2000)
                    verificar_parada()
                    page.locator("text='[ROBO]'").first.click()
                    page.wait_for_timeout(3000)
                    titulo_header.wait_for(state="visible", timeout=10000)

                page.locator(".title-header").click()
                page.locator(".title-input input").fill(task['nome'])
                page.keyboard.press("Enter")
                
                page.locator(".body-item-taskduedate").click()
                page.locator("#input-taskDueDate").fill(task['data'] + "/2026")
                page.keyboard.press("Enter")
                
                verificar_parada()
                page.locator(".actions-description").click() 
                page.locator(".ql-editor[contenteditable='true']").fill(task['descricao'])
                page.locator("button.button-save-big").click()
                page.wait_for_timeout(1000)

                tarefa_tem_carrossel = False

                for tipo_form in task['tipos_formulario']:
                    verificar_parada()
                    log_to_ui(f"   ↳ {tipo_form}")
                    
                    if "carrossel" in tipo_form.lower(): tarefa_tem_carrossel = True
                    
                    page.locator("div.tab span:has-text('Formulários')").click()
                    page.wait_for_timeout(2000) 
                    page.locator("a[title='Adicionar formulário']").first.click()
                    page.wait_for_timeout(3000) 
                    page.locator("span.Select-value-label-tag", has_text=tipo_form).click()
                    page.wait_for_timeout(1000)
                    page.locator("span.span-tab", has_text="CRIAÇÃO").click()

                    is_carrossel = "carrossel" in tipo_form.lower()
                    imagens = buscar_imagens(task['nome'], tipo_form, pasta_imagens)

                    if is_carrossel and len(imagens) < CAROUSEL_MIN_IMAGES:
                        log_to_ui(
                            f"Carrossel de {task['nome']} sem upload: são necessárias pelo menos "
                            f"{CAROUSEL_MIN_IMAGES} imagens."
                        )
                    elif imagens:
                        if is_carrossel:
                            # ==========================================
                            # LOGICA DE UPLOAD CARROSSEL
                            # ==========================================
                            log_to_ui(f"   Iniciando upload sequencial de {len(imagens)} imagens do Carrossel...")
                            for i, imagem_path in enumerate(imagens):
                                verificar_parada()
                                area_upload = page.locator("div.attachment-task")
                                area_upload.wait_for(state="visible")
                                
                                with page.expect_file_chooser() as fc_info:
                                    page.locator("button.upload-button").click(force=True)
                                fc_info.value.set_files([imagem_path])
                                
                                current_count = str(i + 1)
                                log_to_ui(f"   ⏳ Enviando arquivo {current_count}/{len(imagens)}...")
                                
                                page.locator(f"xpath=//div[contains(@class, 'number-ball')]/span[text()='{current_count}']").wait_for(timeout=60000)
                                
                                # ESPERA OBRIGATÓRIA: Delay de 1s p/ o eKyte estabilizar após a bolinha
                                page.wait_for_timeout(1000)
                            
                            log_to_ui("   ✅ Upload do Carrossel concluído.")
                        else:
                            # ==========================================
                            # LOGICA DE UPLOAD COMUM (Story/Feed)
                            # ==========================================
                            area_upload = page.locator("div.attachment-task")
                            area_upload.wait_for(state="visible")
                                
                            with page.expect_file_chooser() as fc_info:
                                page.locator("button.upload-button").click(force=True)
                            fc_info.value.set_files(imagens)
                            
                            qtd_imagens = str(len(imagens))
                            log_to_ui(f"   ⏳ Aguardando upload ({qtd_imagens} arquivo(s))...")
                            verificar_parada()
                            page.locator(f"xpath=//div[contains(@class, 'number-ball')]/span[text()='{qtd_imagens}']").wait_for(timeout=30000)
                            
                            # ESPERA OBRIGATÓRIA: Delay de 1s após a bolinha
                            page.wait_for_timeout(1000)
                            verificar_parada()

                            if any(k in tipo_form.lower() for k in ["story", "stories", "storie"]):
                                log_to_ui("   ⏳ Processando imagens do Story...")
                                page.wait_for_timeout(2500)
                                verificar_parada()

                        # Usa first.click() também no adicionar por segurança
                        btn_adicionar = page.locator("button.btn-primary:has-text('Adicionar')")
                        if btn_adicionar.is_visible():
                            btn_adicionar.first.click()
                            page.wait_for_timeout(1000)
                    
                    verificar_parada()
                    page.locator("div.button-save button:has-text('Salvar')").click()
                    page.wait_for_timeout(2000)
                    page.locator("a.back-task").click()
                    page.wait_for_timeout(2000)
                
                verificar_parada()

                if not tarefa_tem_carrossel:
                    page.locator("a.next-phase").click()
                    page.wait_for_timeout(1000)
                    page.locator("button:has-text('Continuar sem apontar')").click()
                    log_to_ui(f"✅ {task['nome']} Avançada!")
                else:
                    log_to_ui(f"Tarefa {task['nome']} retida para revisão do carrossel.")
                
                pct = int(((index + 1) / total_tarefas) * 100)
                eel.atualizarProgresso(pct, f"{pct}% ({index + 1}/{total_tarefas})")
                page.wait_for_timeout(2000)

                if index < len(tarefas) - 1:
                    verificar_parada()
                    page.locator("#navigation-next--task").click()
                    page.wait_for_timeout(3000) 

            log_to_ui("\n🎉 AUTOMAÇÃO FINALIZADA COM SUCESSO!")
            browser.close()
    
    except InterruptedError as e:
        log_to_ui(f"🛑 {str(e)}")
    except Exception as e:
        log_to_ui(f"❌ ERRO CRÍTICO: {str(e)}")
    finally:
        is_running = False
        stop_requested = False
        eel.restaurarBotoes()

if __name__ == "__main__":
    if "--preview" in sys.argv:
        eel.start("index.html", mode=False, host="0.0.0.0", port=8765, all_interfaces=True)
    else:
        eel.start("index.html", size=(900, 750), port=0)