# 📦 Guia de Configuração e Compilação

Este documento detalha o processo completo para preparar o ambiente de desenvolvimento local, instalar as dependências necessárias e compilar o projeto em arquivos executáveis (`.exe`) para distribuição.

---

## 1. Preparando o Ambiente Local

Recomendamos fortemente o uso de um Ambiente Virtual (VENV) para evitar conflitos de versão com outras bibliotecas Python instaladas no seu computador.

Abra o terminal (`PowerShell` no Windows) na pasta raiz do projeto e execute os passos abaixo:

### Passo 1.1: Criar o Ambiente Virtual
```powershell
python -m venv venv
```

### Passo 1.2: Ativar o Ambiente Virtual
```powershell
.\venv\Scripts\Activate.ps1
```
*(Você saberá que deu certo se aparecer um `(venv)` verde no início da linha do seu terminal).*

### Passo 1.3: Instalar as Dependências do Projeto
```powershell
pip install -r requirements.txt
```
*(Nota: Se houver erros com a compilação do Eel posteriormente, garanta que o pacote base esteja atualizado rodando: `pip install setuptools`)*

### Passo 1.4: Baixar o Motor do Navegador (Playwright)
```powershell
playwright install chromium
```

---

## 2. Compilando os Executáveis (.exe)

O processo de compilação transforma os scripts Python em programas independentes que podem ser executados em computadores que não possuem Python instalado.

Ainda no terminal (com o `(venv)` ativado), siga os passos de acordo com a versão que deseja gerar:

### Passo Único Obrigatório: Variável de Ambiente
Antes de compilar **qualquer** versão, você deve avisar ao Playwright que o navegador será embutido no executável local. Rode este comando:
```powershell
$env:PLAYWRIGHT_BROWSERS_PATH="0"
```

### Opção A: Compilar a Versão Desktop (CustomTkinter)
Para gerar o executável da interface clássica, rode o comando do PyInstaller coletando os pacotes do customtkinter:
```powershell
python -m PyInstaller --noconsole --onefile --collect-all customtkinter app_ekyte.py
```

### Opção B: Compilar a Versão Web (Eel)
Para gerar o executável da interface web (HTML/CSS/JS), precisamos dizer ao PyInstaller para incluir a pasta `web` no empacotamento:
```powershell
python -m PyInstaller --noconsole --onefile --add-data "web;web" app_web.py
```

---

## 3. Pós-Compilação e Distribuição

1. Aguarde o terminal exibir a mensagem `Building EXE from EXE-00.toc completed successfully.`.
2. Acesse a pasta **`dist`** que foi criada na raiz do seu projeto.
3. Lá dentro, você encontrará o arquivo `app_ekyte.exe` ou `app_web.exe` (dependendo de qual você compilou).
4. **IMPORTANTE:** Para enviar este arquivo para a sua equipe (via WhatsApp, E-mail, Drive), **compacte-o em `.zip` ou `.rar` primeiro**, pois muitos serviços bloqueiam o envio direto de arquivos `.exe` por motivos de segurança.

> **Nota:** É perfeitamente normal o antivírus do Windows (Windows Defender) emitir um alerta na primeira vez que você ou sua equipe executarem o `.exe` em um computador novo. Isso acontece porque o arquivo não possui um "Certificado Digital" pago. Basta clicar em "Mais informações" e depois em "Executar assim mesmo".