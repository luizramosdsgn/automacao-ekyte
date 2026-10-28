# 🤖 App eKyte — Documentação Funcional Completa

> Prompt de referência do projeto. Descreve o que o app faz, como faz, o que precisa para funcionar e ideias de features futuras.

---

## 1. Visão Geral

O **Robô eKyte** é uma ferramenta de automação desktop que automatiza a criação de tarefas na plataforma **eKyte** (https://app.ekyte.com), um sistema de gestão de marketing digital. A ferramenta lê planejamentos de redes sociais (copiados do Google Docs), extrai dados estruturados e os insere automaticamente no eKyte via automação de navegador.

### Problema que resolve

O processo manual de cadastrar postagens no eKyte envolve repetição exaustiva:
- Criar tarefas uma a uma
- Preencher data, título, descrição
- Selecionar tipo de formulário (Feed, Story, Carrossel)
- Fazer upload de imagens criativas
- Avançar a fase de cada tarefa

**O robô automatiza 100% desse fluxo**, reduzindo horas de trabalho a minutos.

---

## 2. Arquitetura do Projeto

O projeto possui **duas versões da interface** que compartilham a mesma lógica de automação:

### 2.1 `app_ekyte.py` — Versão Desktop (CustomTkinter)

- Interface nativa com **CustomTkinter** (dark theme)
- Janela fixa: 850×720
- Auto-instalação do Chromium embutida
- Diálogo nativo para input de mês ausente (`CTkInputDialog`)
- Empacotável como `.exe` standalone via PyInstaller

### 2.2 `app_web.py` + `web/` — Versão Web (Eel)

- Interface HTML/CSS/JS servida pelo **Eel** (Python ↔ JavaScript bridge)
- Janela: 900×750
- Frontend em `web/index.html`, `web/style.css`, `web/script.js`
- Comunicação bidirecional: Python expõe funções ao JS e vice-versa
- Empacotável como `.exe` com assets web embutidos

### 2.3 Arquivos Compartilhados

- `config.json` — Persistência de email, senha (base64) e pasta de imagens
- Lógica core idêntica em ambas versões (extração de texto, busca de imagens, automação Playwright)

---

## 3. Fluxo Funcional Completo

### Etapa 1 — Configuração

```
Usuário preenche:
├── E-mail do eKyte
├── Senha do eKyte  
├── Pasta local de imagens (picker nativo)
└── Opções:
    ├── Ocultar Chrome (headless mode)
    └── Vídeo (dev) — modo de teste
```

As credenciais são salvas em `config.json` com senha codificada em base64 (ofuscação básica).

### Etapa 2 — Colagem do Texto do Planejamento

O usuário cola o texto do Google Docs com o planejamento do mês. Formato esperado:

```
DATA DA PUBLICAÇÃO: 05/10
IDEIA/OBJETIVO DO CONTEÚDO: ...
TEMA: ...
HEADLINE: ...
LEGENDA: ...
(tipo: Feed, Story, Feed e Story, Carrossel, etc.)
```

### Etapa 3 — Padronização do Texto (Opcional)

O botão **"Padronizar"** executa sanitização automática:

1. **Normaliza datas:** Converte formatos variados (`Dia 5`, `Post 05`, `05/10`) para `DATA DA PUBLICAÇÃO: DD/MM`
2. **Quebra seções:** Insere quebras de linha antes das tags (TEMA:, HEADLINE:, LEGENDA:, IDEIA/OBJETIVO)
3. **Remove lixo:** Limpa prefixos como "criativo feed:", traços soltos, etc.
4. **Detecção de mês ausente:** Se datas não têm mês:
   - Tenta inferir a partir dos nomes dos arquivos da pasta de imagens (`DD-MM.png`)
   - Pergunta ao usuário via diálogo
   - Fallback: marca como `[MES]` para edição manual

### Etapa 4 — Extração de Tarefas

A função `extrair_dados_do_texto()`:

1. Divide o texto por `"DATA DA PUBLICAÇÃO:"`
2. Para cada bloco:
   - Extrai a data (`DD/MM`)
   - Gera o nome da tarefa (`DD-MM`)
   - Captura a descrição completa
   - **Ignora vídeos** (blocos contendo "vídeo" ou "video")
   - Identifica tipo(s) de formulário:
     - `"feed e story"` → 2 formulários (Feed + Story)
     - `"carrossel"` + `"story"` → Carrossel Story
     - `"carrossel"` → Carrossel Feed
     - `"story/stories"` → Story/Reel/Short/TikTok
     - Default → Feed

### Etapa 5 — Pré-Check de Imagens

Antes de iniciar, o sistema verifica se existem imagens na pasta para cada tarefa:

**Estratégia de busca (por prioridade):**

1. Arquivo com nome `DD-MM` + sufixo de tipo (`-feed.png`, `-story.png`)
2. Arquivo exato `DD-MM.png/jpg/jpeg/webp`
3. Pasta com nome `DD-MM` ou `DD-MM-feed/story` → lista todos os arquivos de imagem dentro

Se faltar imagens, exibe lista detalhada e pergunta se deseja continuar.

### Etapa 6 — Pop-up de Resumo

Antes da execução, exibe resumo:

```
Foram identificadas X postagem(ns).

Formulários gerados:
  • Feed: N
  • Stories/Reels: N
  • Carrossel: N

Deseja iniciar a automação?
```

### Etapa 7 — Automação Playwright

A execução ocorre em **thread separada** para não travar a interface:

```
1. Abre Chromium (headless ou visível)
2. Navega para https://app.ekyte.com
3. Faz login (email + senha)
4. Verifica workspace ativo
   └── Se não for "Audácia Mkt&Co" → troca empresa
5. Navega para Tarefas
6. Ajusta filtro de data para "Todo o período"
7. Clica na tarefa template "[ROBO]"
8. Para cada tarefa extraída:
   ├── Renomeia tarefa (DD-MM)
   ├── Define data de publicação (DD/MM/2026)
   ├── Preenche descrição
   ├── Para cada formulário:
   │   ├── Abre aba "Formulários"
   │   ├── Adiciona novo formulário (tipo selecionado)
   │   ├── Vai para aba "CRIAÇÃO"
   │   ├── Se não for Carrossel:
   │   │   ├── Faz upload de imagem(ns)
   │   │   ├── Aguarda validação do eKyte
   │   │   └── Clica "Adicionar"
   │   ├── Salva formulário
   │   └── Volta para a tarefa
   ├── Se não tem Carrossel → Avança fase
   │   └── "Continuar sem apontar"
   ├── Atualiza barra de progresso
   └── Navega para próxima tarefa
9. Fecha navegador
10. Exibe "AUTOMAÇÃO FINALIZADA"
```

### Mecanismo de Parada

- Flag `stop_requested` verificada em pontos estratégicos (`verificar_parada()`)
- Lança `InterruptedError` para interromper a thread imediatamente
- Interface reflete o estado: botão muda para "CANCELANDO..." → restaura

---

## 4. Comunicação Python ↔ JS (Versão Web)

### Python → JavaScript (eel.js)

| Função JS              | Propósito                         |
|------------------------|-----------------------------------|
| `eel.atualizarLog(msg)` | Adiciona mensagem ao terminal     |
| `eel.atualizarProgresso(pct, texto)` | Atualiza barra de progresso |
| `eel.restaurarBotoes()` | Restaura estado dos botões        |

### JavaScript → Python (@eel.expose)

| Função Python               | Propósito                             |
|-----------------------------|---------------------------------------|
| `carregar_config_py()`      | Carrega config.json                   |
| `selecionar_pasta_py()`     | Abre picker de pasta (tkinter)        |
| `parar_automacao_py()`      | Seta flag de parada                   |
| `padronizar_texto_py(texto, pasta)` | Sanitiza o texto colado       |
| `iniciar_automacao_py(...)` | Dispara a automação em thread         |

---

## 5. Dependências

| Pacote           | Versão Mínima | Uso                                |
|------------------|---------------|------------------------------------|
| `customtkinter`  | ≥ 5.2.0       | GUI desktop (app_ekyte.py)         |
| `playwright`     | ≥ 1.40.0      | Automação de navegador             |
| `pyinstaller`    | ≥ 6.0.0       | Build do .exe                      |
| `eel`            | ≥ 0.18.2      | Bridge Python↔HTML (app_web.py)    |
| `setuptools`     | ≥ 84.0.0      | Build tools                        |

### Requisitos do Sistema

- **Python** 3.9+
- **Windows** (tkinter file dialogs, PyInstaller .exe)
- **Chromium** instalado via Playwright (`playwright install chromium`)
- **Conta no eKyte** com acesso ao workspace "Audácia Mkt&Co"
- **Template de tarefa** nomeado `[ROBO]` cadastrado no eKyte

---

## 6. Estrutura de Arquivos

```
automacao-ekyte/
├── app_ekyte.py          # Versão desktop (CustomTkinter)
├── app_web.py            # Versão web (Eel)
├── web/
│   ├── index.html        # Interface HTML
│   ├── style.css         # Estilos (Dashboard Style)
│   └── script.js         # Lógica frontend
├── config.json           # Configurações salvas do usuário
├── requirements.txt      # Dependências Python
├── app_ekyte.spec        # Build spec do desktop
├── app_web.spec          # Build spec do web
├── design.md             # Guia visual do projeto
├── README.md             # Documentação principal
└── LICENSE               # MIT License
```

---

## 7. Como Compilar

### Versão Desktop

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
python -m playwright install chromium
python -m PyInstaller --noconsole --onefile --collect-all customtkinter app_ekyte.py
```

### Versão Web

```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
python -m playwright install chromium
python -m PyInstaller --noconsole --onefile --collect-all playwright --add-data "web;web" app_web.py
```

---

## 8. Ideias de Features Futuras

### 🔴 Alta Prioridade

- [ ] **Suporte a vídeos:** Atualmente, posts com vídeo são ignorados. Implementar upload de `.mp4`/`.mov` com detecção automática por nome de arquivo
- [ ] **Seleção de workspace dinâmica:** Em vez de hardcode "Audácia Mkt&Co", permitir escolha do workspace na interface
- [ ] **Fila de retentativas:** Se uma tarefa falhar (timeout, elemento não encontrado), registrar e tentar novamente no final
- [ ] **Relatório final exportável:** Gerar PDF/CSV com resumo do que foi feito, quais tarefas passaram, quais falharam

### 🟡 Média Prioridade

- [ ] **Preview visual das tarefas:** Antes de iniciar, mostrar lista editável com cada tarefa, data, tipo e imagem associada
- [ ] **Upload de Carrossel automático:** Detectar pastas com múltiplas imagens ordenadas e fazer upload em sequência
- [ ] **Agendamento de execução:** Timer para rodar automação em horário específico (ex: madrugada)
- [ ] **Dark/Light mode toggle** na versão web
- [ ] **Multi-conta:** Suportar perfis de configuração para diferentes empresas/clientes
- [ ] **Notificações push/desktop** quando automação finaliza

### 🟢 Baixa Prioridade / Nice-to-Have

- [ ] **Dashboard de métricas:** Histórico de execuções, quantas tarefas processadas por dia/mês
- [ ] **Integração com Google Docs API:** Puxar texto direto do documento sem copiar/colar
- [ ] **OCR em imagens:** Extrair texto de imagens para preencher headlines automaticamente
- [ ] **Auto-update:** Verificar nova versão no GitHub Releases e atualizar
- [ ] **Modo batch multi-cliente:** Processar planejamentos de múltiplos clientes em sequência
- [ ] **Templates customizáveis:** Permitir configurar quais campos preencher e como mapear o texto
- [ ] **Logs persistentes:** Salvar histórico de execuções em arquivo local para auditoria
- [ ] **Detecção de duplicatas:** Antes de criar, verificar se a tarefa com mesmo nome/data já existe no eKyte

### 💡 Exploratório

- [ ] **IA para classificação:** Usar LLM para interpretar textos de planejamento em formatos variados (não apenas o padrão atual)
- [ ] **Integração com Figma:** Baixar imagens diretamente do Figma por link do frame
- [ ] **API REST local:** Expor endpoints para integração com outros sistemas (Zapier, Make, n8n)
- [ ] **Plugin de browser:** Extensão Chrome que injeta um botão "Enviar pro Robô" no Google Docs

