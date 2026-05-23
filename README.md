# Telegram Media Forwarder

**Telegram Media Forwarder** é um aplicativo desktop desenvolvido em **Python**
com interface gráfica em **Tkinter**, criado para automatizar o encaminhamento
autorizado de mídias do Telegram usando a biblioteca **Telethon**.

O projeto permite encaminhar fotos, vídeos e documentos de uma origem do Telegram
para um destino configurável, como **Mensagens Salvas**, grupos, canais ou bots,
com controle de limite, delay, pausas automáticas, histórico de mídias já enviadas
e login diretamente pelo próprio aplicativo.

---

## 📌 Status do projeto

Versão atual: **v0.0.1**

Esta é a primeira versão oficial do projeto, já com interface gráfica,
login integrado, histórico de envios, tema claro/escuro e versões
empacotadas para Windows e Linux.

---

## 🚀 Principais recursos

- Interface gráfica moderna em Python/Tkinter
- Tema escuro e tema claro
- Logo integrada ao aplicativo
- Login do Telegram dentro do próprio programa
- Encaminhamento autorizado de mídias
- Suporte a fotos, vídeos e documentos
- Origem e destino configuráveis
- Envio para Mensagens Salvas, grupos, canais ou bots
- Delay configurável entre envios
- Limite total de mídias por execução
- Pausa automática a cada X mídias
- Botões para iniciar, pausar/retomar e parar
- Log em tempo real
- Estatísticas em tempo real
- Histórico para evitar mídias repetidas
- Compatibilidade com histórico antigo
- Botão discreto para futuras atualizações
- Changelog interno
- Scroll vertical para melhor adaptação em telas menores

---

## 🖥️ Tecnologias utilizadas

- Python
- Tkinter
- Telethon
- Git/GitHub
- PyInstaller
- RPM Build
- Debian Package
- AppImage Build

---

## 📷 Interface

O programa possui uma interface organizada em cards:

- **Credenciais**
  - API ID
  - API Hash
  - Teste de campos
  - Login Telegram

- **Configurações**
  - Origem
  - Destino
  - Filtro opcional
  - Delay
  - Limite total
  - Pausa automática

- **Estatísticas**
  - Mídias enviadas
  - Mídias já salvas/ignoradas
  - Erros
  - Tempo decorrido
  - Total processado

- **Log**
  - Registro em tempo real das ações do programa

---

## ⚙️ Como usar

### Windows

Baixe o `TelegramMediaForwarder-v0.0.1.exe` e execute diretamente,
sem precisar instalar nada.

### Fedora

```bash
sudo dnf install telegram-media-forwarder-v0.0.1.rpm
```

### Debian / Ubuntu / Linux Mint

```bash
sudo dpkg -i telegram-media-forwarder-v0.0.1.deb
```

### AppImage (qualquer Linux)

```bash
chmod +x TelegramMediaForwarder-v0.0.1.AppImage
./TelegramMediaForwarder-v0.0.1.AppImage
```

### Rodar pelo código fonte

```bash
pip install telethon
python3 telegram_media_forwarder.py
```

---

## 🔐 Login no Telegram

A versão **v0.0.1** possui login integrado dentro do próprio aplicativo.

O usuário informa:

- API ID
- API Hash
- Telefone
- Código recebido no Telegram
- Senha 2FA, se a conta possuir

Após o login, o programa cria uma sessão local no computador do usuário,
sem necessidade de usar terminal.

> Para obter o API ID e API Hash acesse: https://my.telegram.org

---

## 📁 Arquivos pessoais

O aplicativo cria arquivos locais para cada usuário.

Esses arquivos **não devem ser enviados para o GitHub**:

```text
sessao.session
config.json
historico.txt
```

Eles ficam salvos em:

- **Linux:** `~/.local/share/telegram-media-forwarder/`
- **Windows:** na mesma pasta do executável

---

## ⚠️ Aviso de uso

Use este programa apenas com mídias próprias, autorizadas ou para backup pessoal.
Respeite os termos de uso do Telegram.