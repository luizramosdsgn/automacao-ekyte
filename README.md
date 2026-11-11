# Robô eKyte - Automação de Tarefas (Web & Desktop)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright)
![Eel](https://img.shields.io/badge/GUI-Eel%20(HTML/CSS/JS)-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

Uma aplicação desenvolvida em Python para automatizar a criação de tarefas, formulários e o upload de imagens em lote na plataforma corporativa **eKyte**. 

A ferramenta lê o planejamento copiado do Google Docs, identifica datas, descrições e tipos de postagem (Feed, Story, Carrossel) via análise de texto (RegEx), e executa o fluxo web de forma 100% automatizada através de um navegador oculto.

---

## ✨ Novas Funcionalidades

- **Nova Interface Web Moderna:** Frontend reconstruído em HTML/CSS/JS usando a biblioteca `Eel`, rodando de forma nativa e super leve.
- **Lógica Inteligente de Carrossel:** Upload sequencial automatizado, aguardando validações de servidor arquivo por arquivo.
- **Criação e Duplicação Dinâmica:** Capacidade de criar uma nova tarefa mestre `[ROBO]` do zero, perguntando a Equipe desejada e duplicando-a recursivamente.
- **Workspace Dinâmico:** O robô varre o diretório da pasta de imagens selecionada e extrai automaticamente o cliente correto para preenchimento.
- **Segurança e QoL:** Senha salva localmente com ofuscação (Base64) e pop-up de revisão (Pré-Check) detalhando a quantidade de posts reconhecidos.
- **Modo Invisível (Headless):** Execução da automação em segundo plano sem sequestrar o mouse ou o monitor do usuário.

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/):** Linguagem principal (Backend & Lógica).
- **[Playwright](https://playwright.dev/python/):** Automação web estrutural e manipulação do DOM.
- **[Eel](https://github.com/python-eel/Eel):** Ponte de comunicação assíncrona entre o Python e a interface.
- **HTML, CSS e JS:** Estruturação da nova interface responsiva e interativa.

---

## Como Executar o Projeto Localmente

### Pré-requisitos
- Python 3.9 ou superior.
- Git instalado.

### 1. Clonar o Repositório
```bash
git clone https://github.com/luizramosdsgn/automacao-ekyte.git
cd automacao-ekyte
```

### 2. Criar e Ativar Ambiente Virtual (Recomendado)
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Executar a Aplicação (Versão Web Principal)
```bash
python app_web.py
```
*(Nota: A versão legada em CustomTkinter ainda pode ser acessada via `python app_ekyte.py`).*

---

## Compilando o Executável (.exe)

O processo de compilação foi separado para manter este documento limpo. 

Para gerar o arquivo `.exe` e enviar para a sua equipe sem que eles precisem instalar o Python, consulte o nosso **[Guia de Compilação](compilação.md)**.

---

## Licença

Este projeto está sob a licença [MIT](LICENSE).