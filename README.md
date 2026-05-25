````md
# Telegram Media Forwarder

**Telegram Media Forwarder** é um aplicativo desktop desenvolvido em **Python** com interface gráfica em **Tkinter**, criado para automatizar o encaminhamento autorizado de mídias do Telegram usando a biblioteca **Telethon**.

O projeto permite encaminhar fotos, vídeos e documentos de uma origem do Telegram para um destino configurável, como **Mensagens Salvas**, grupos, canais ou bots, com controle de limite, delay, pausas automáticas, histórico de mídias já enviadas e login diretamente pelo próprio aplicativo.

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

## 🔐 Login no Telegram

A versão **v0.0.1** possui login integrado dentro do próprio aplicativo.

O usuário informa:

- API ID
- API Hash
- Telefone
- Código recebido no Telegram
- Senha 2FA, se a conta possuir

Após o login, o programa cria uma sessão local no computador do usuário, sem necessidade de usar terminal.

---

## 📁 Arquivos pessoais

O aplicativo cria arquivos locais para cada usuário.

Esses arquivos **não devem ser enviados para o GitHub**:

```text
sessao.session
config.json
historico.txt
````

Eles armazenam:

| Arquivo          | Função                              |
| ---------------- | ----------------------------------- |
| `sessao.session` | Sessão local do Telegram            |
| `config.json`    | Configurações do usuário            |
| `historico.txt`  | Histórico de mídias já encaminhadas |

No Linux, esses dados ficam em:

```bash
~/.local/share/telegram-media-forwarder
```

---

## 🔁 Como o histórico funciona

Para evitar reenvio de mídias, o programa salva cada mídia enviada no arquivo `historico.txt`.

A chave usada segue o formato:

```text
grupo_id:msg_id
```

Isso evita conflitos entre mensagens de grupos diferentes.

O projeto também mantém compatibilidade com históricos antigos que usavam apenas o `msg_id`.

---

## 📦 Versões disponíveis

A versão **v0.0.1** possui builds preparados para diferentes sistemas:

### Windows

Arquivo disponível:

```text
TelegramMediaForwarder-v0.0.1.exe
```

O usuário pode abrir o `.exe` diretamente, sem precisar instalar Python.

---

### Fedora/Linux

Pacote de build RPM disponível:

```text
telegram-media-forwarder-rpm-final-v001.tar.gz
```

---

### Debian/Ubuntu/Linux Mint

Pacote disponível:

```text
telegram-media-forwarder-v0.0.1-debian-ubuntu.deb
```

Instalação:

```bash
sudo apt install ./telegram-media-forwarder-v0.0.1-debian-ubuntu.deb
```

---

### AppImage

Também há um pacote de build para gerar versão AppImage em Linux.

---

## 🛡️ Segurança

Este projeto foi pensado para uso autorizado.

O programa:

* Não salva o API Hash automaticamente
* Não inclui sessão do usuário nos pacotes
* Não inclui histórico pessoal nos pacotes
* Não inclui configurações pessoais nos pacotes
* Não tenta burlar restrições do Telegram
* Deve ser usado apenas com mídias próprias, autorizadas ou para backup pessoal

Cada usuário deve fazer login com sua própria conta.

---

## 🧪 Changelog

### v0.0.1

* Interface gráfica profissional com Tkinter
* Tema claro e escuro
* Login Telegram dentro do aplicativo
* Encaminhamento autorizado de mídias
* Histórico para evitar duplicidade
* Estatísticas em tempo real
* Log de execução
* Botões de iniciar, pausar e parar
* Changelog interno
* Preparação para atualizações futuras
* Build Windows `.exe`
* Build Debian/Ubuntu `.deb`
* Build RPM para Fedora
* Build AppImage preparado

---

## 📌 Estrutura do projeto

```text
telegram-media-forwarder/
├── telegram_media_forwarder.py
├── logo.png
├── README.md
├── CHANGELOG.md
├── requirements.txt
├── .gitignore
└── releases/
    ├── TelegramMediaForwarder-v0.0.1.exe
    ├── telegram-media-forwarder-v0.0.1-debian-ubuntu.deb
    └── telegram-media-forwarder-rpm-final-v001.tar.gz
```

---

## 📥 Download

Os arquivos de instalação da versão **v0.0.1** estão disponíveis na pasta `releases/` do repositório.

---

## 👨‍💻 Autor

Desenvolvido por **Bruno Vilela**.

GitHub: [sleepy907](https://github.com/sleepy907)

---

## ⚠️ Aviso

Este projeto é destinado a fins educacionais, automação pessoal.

Use apenas com conteúdos próprios, autorizados ou para backup pessoal, respeitando as permissões e regras do Telegram.
