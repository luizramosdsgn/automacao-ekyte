# 📦 Guia de Configuração e Compilação

Este documento detalha o processo completo para preparar o ambiente de desenvolvimento local, instalar as dependências necessárias e compilar o projeto em arquivos executáveis (`.exe`) para distribuição.

---

## 1. Preparando o Ambiente Local

Abra o terminal (`PowerShell` no Windows) na pasta raiz do projeto e execute os passos abaixo:

> **Opcional (Ambiente Virtual):** Se preferir isolar as dependências para gerar um `.exe` mais enxuto, você pode criar e ativar um ambiente virtual antes dos passos abaixo:
> ```powershell
> python -m venv venv
> .\venv\Scripts\Activate.ps1
> ```
> *(Caso o PowerShell bloqueie o script de ativação ou você já utilize o Python global/IDE, basta pular esta etapa e seguir direto para o Passo 1.1).*

### Passo 1.1: Instalar as Dependências do Projeto
```powershell
pip install -r requirements.txt
```
*(Nota: Se houver erros com a compilação do Eel posteriormente, garanta que o pacote base esteja atualizado rodando: `pip install setuptools`)*

### Passo 1.2: Baixar o Motor do Navegador (Playwright)
```powershell
playwright install chromium
```

---

## 2. Compilando o Executável (.exe)

O processo de compilação transforma o script Python em um programa independente que pode ser executado em computadores que não possuem Python instalado.

Ainda no terminal, siga os passos abaixo:

### Passo 2.1: Variável de Ambiente
Antes de compilar, você deve avisar ao Playwright que o navegador será embutido no executável local. Rode este comando:
```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
```

### Passo 2.2: Compilar a Aplicação Web (Eel)
Para gerar o executável da interface web (HTML/CSS/JS), precisamos dizer ao PyInstaller para incluir a pasta `web` no empacotamento:
```powershell
python -m PyInstaller --noconsole --onefile --add-data "web;web" app_web.py
```

---

## 3. Pós-Compilação e Distribuição

1. Aguarde o terminal exibir a mensagem `Building EXE from EXE-00.toc completed successfully.`.
2. Acesse a pasta **`dist`** que foi criada na raiz do seu projeto.
3. Lá dentro, você encontrará o arquivo `app_web.exe`.
4. **IMPORTANTE:** Para enviar este arquivo para a sua equipe (via WhatsApp, E-mail, Drive), **compacte-o em `.zip` ou `.rar` primeiro**, pois muitos serviços bloqueiam o envio direto de arquivos `.exe` por motivos de segurança.

> **Nota:** É perfeitamente normal o antivírus do Windows (Windows Defender) emitir um alerta na primeira vez que você ou sua equipe executarem o `.exe` em um computador novo. Isso acontece porque o arquivo não possui um "Certificado Digital" pago. Basta clicar em "Mais informações" e depois em "Executar assim mesmo".