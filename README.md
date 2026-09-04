# 🤖 Robô eKyte - Automação de Tarefas Desktop

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)
![License](https://img.shields.io/badge/License-MIT-yellow)

Uma aplicação desktop desenvolvida em Python para automatizar a criação de formulários e o upload de imagens em tarefas da plataforma corporativa **eKyte**.

A ferramenta lê o planejamento copiado do Google Docs, identifica datas, descrições e tipos de postagem (Feed, Story, Carrossel) via análise de texto, e executa o fluxo web de forma automatizada.

---

## ✨ Funcionalidades

- **Interface Gráfica Moderna:** Desenvolvida com `CustomTkinter` (Tema escuro e design responsivo).
- **Processamento Dinâmico de Texto:** Identifica parâmetros no texto para categorizar formulários (Feed, Story, Carrossel, Arte Gráfica) e filtrar conteúdos em vídeo.
- **Modo Invisível (Headless):** Execução do navegador em segundo plano para não interferir na rotina do usuário.
- **Instalação Automática do Navegador:** Prepara o motor Chromium do Playwright de forma transparente.

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/):** Linguagem principal.
- **[Playwright](https://playwright.dev/python/):** Automação web e navegação.
- **[CustomTkinter](https://customtkinter.tomschimansky.com/):** Interface gráfica moderna.
- **[PyInstaller](https://pyinstaller.org/):** Compilação e empacotamento para Windows.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

- Python 3.9 ou superior instalado.
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

### 4. Executar a Aplicação

```bash
python app_ekyte.py
```

---

## 📦 Compilando o Executável (.exe)

Para gerar o arquivo `.exe` para distribuição:

```bash
pyinstaller app_ekyte.spec
```

O executável final estará disponível na pasta `dist/app_ekyte.exe`.

> 💡 **Nota de Boas Práticas:** Arquivos compilados (`.exe`), pastas `build/` e `dist/` **não são versionados** no Git. Para disponibilizar a versão executável aos usuários finais, utilize a aba **Releases** do GitHub.

---

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE).
