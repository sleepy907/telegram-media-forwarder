# Telegram Media Forwarder

**Telegram Media Forwarder** é um aplicativo desktop desenvolvido em **Python** com interface gráfica em **Tkinter**, criado para automatizar o encaminhamento autorizado de mídias do Telegram usando a biblioteca **Telethon**.

O projeto permite encaminhar fotos, vídeos e documentos de uma origem do Telegram para um destino configurável, como **Mensagens Salvas**, grupos, canais ou bots, com controle de limite, delay, pausas automáticas, histórico de mídias já enviadas e login diretamente pelo próprio aplicativo.

A versão atual possui arquitetura modular, preservação do layout de álbuns (mosaicos) e opções de "Modo Limpo" para omitir a autoria original ou ocultar legendas das mídias.

---

## 📌 Status do projeto

Versão atual: **v0.2.0**

A versão **v0.2.0** reorganiza o projeto em uma arquitetura modular, melhora o repasse inteligente de álbuns, adiciona recursos de privacidade no encaminhamento e renova a interface com a paleta *Catppuccin Macchiato*.

---

## 📦 Downloads

Baixe a versão mais recente pela página de releases:

👉 [Telegram Media Forwarder v0.2.0]([https://github.com/sleepy907/telegram-media-forwarder/releases/tag/v0.2.0)

Arquivos disponíveis:
- **Windows:** `TelegramMediaForwarder-v0.2.0.exe`
- **Linux x86_64:** `telegram-media-forwarder-0.2.0-linux-x86_64.tar.gz`

---

## 🚀 Principais recursos

- Interface gráfica moderna e limpa (Flat Design - Catppuccin)
- **Modo Álbum (Mosaico):** Identifica e agrupa mídias correlatas para enviá-las agrupadas ao destino.
- **Modo Limpo (Privacidade):** Oculta o autor original ("Encaminhada de...") e permite remover a legenda/texto original.
- Login do Telegram dentro do próprio programa (sem terminal)
- Encaminhamento autorizado de mídias (fotos, vídeos e documentos)
- Origem e destino configuráveis (Mensagens Salvas, grupos, canais ou bots)
- Delay configurável entre envios e pausa automática por lote
- Log e Estatísticas em tempo real com estimativa de tempo restante
- **Segurança de Histórico (`try...finally`):** Operação em lote na memória que garante que o progresso seja gravado mesmo em caso de encerramento forçado.
- Importar e exportar histórico
- Opção para salvar API Hash localmente
- Processamento seguro em ordem cronológica (mais antiga → mais recente)

---

## 🖥️ Tecnologias utilizadas

- Python (Modularizado S.O.L.I.D)
- Tkinter
- Telethon
- Git/GitHub

---

## ⚙️ Como rodar pelo código-fonte

A partir da v0.2.0, o projeto adota uma estrutura profissional (pacote `src/`).

1. Instale a dependência:
```bash
pip install telethon
```

2. Execute através do novo ponto de entrada na raiz do projeto:
```bash
python main.py
```

---

## ▶️ Como usar a versão baixada

### Windows

Baixe o arquivo `TelegramMediaForwarder-v0.2.0.exe` pela página de releases e execute normalmente.

### Linux

Baixe o pacote `.tar.gz`, extraia o arquivo e execute:

```bash
tar -xzf telegram-media-forwarder-0.2.0-linux-x86_64.tar.gz
./TelegramMediaForwarder
```

---

## 🔐 Login no Telegram

O aplicativo possui login integrado, sem necessidade de usar o terminal.

O usuário informa:
- API ID
- API Hash
- Telefone
- Código recebido no Telegram
- Senha 2FA, se a conta possuir

Após o login, o programa cria uma sessão local no computador do usuário.
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

---

🔗 [github.com/sleepy907/telegram-media-forwarder](https://github.com/sleepy907/telegram-media-forwarder)
