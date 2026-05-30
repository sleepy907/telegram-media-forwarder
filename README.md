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

Versão atual: **v0.1.0**

<<<<<<< Updated upstream
=======
<<<<<<< HEAD
Versão com interface profissional completa, login integrado, sistema de atualização
via GitHub, importar/exportar histórico, tela de ajuda, logs e estatísticas melhorados
e correção de todos os bugs identificados nos testes da versão anterior.
=======
>>>>>>> Stashed changes
A versão v0.1.0 marca a primeira versão pública organizada do Telegram Media Forwarder.
Esta atualização transforma o projeto de uma versão inicial funcional em um aplicativo
mais completo, com melhorias de usabilidade, segurança, histórico, logs, estatísticas,
tela de ajuda e preparação para atualizações reais via GitHub.
<<<<<<< Updated upstream
=======
>>>>>>> 514ee67 (docs: atualiza README para v0.1.0)
>>>>>>> Stashed changes

---

## 🚀 Principais recursos

- Interface gráfica moderna em Python/Tkinter
- Tema escuro e tema claro
- Logo integrada ao aplicativo
- Login do Telegram dentro do próprio programa (sem terminal)
- Encaminhamento autorizado de mídias
- Suporte a fotos, vídeos e documentos
- Origem e destino configuráveis
- Envio para Mensagens Salvas, grupos, canais ou bots
- Delay configurável entre envios
- Limite total de mídias por execução
- Pausa automática a cada X mídias
- Botões para iniciar, pausar/retomar e parar
- Log em tempo real com mensagens claras
- Estatísticas em tempo real com tempo restante estimado
- Histórico para evitar mídias repetidas
- Importar e exportar histórico
- Opção para salvar API Hash localmente
- Sistema de atualização via update.json no GitHub
- Tela de ajuda completa dentro do aplicativo
- Changelog interno
- Scroll vertical para adaptação em telas menores
- Stickers/figurinhas ignorados automaticamente
- Processamento em ordem cronológica (mais antiga → mais recente)

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
  - Opção para salvar API Hash
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
  - Mídias enviadas agora
  - Mídias já no histórico
  - Erros
  - Tempo decorrido
  - Tempo restante estimado
  - Total processado

- **Log**
  - Registro em tempo real das ações do programa

---

## ⚙️ Como usar

### Windows

Baixe o `TelegramMediaForwarder-v0.1.0.exe` e execute diretamente,
sem precisar instalar nada.

### Fedora

```bash
sudo dnf install telegram-media-forwarder-v0.1.0.rpm
```

### Debian / Ubuntu / Linux Mint

```bash
sudo dpkg -i telegram-media-forwarder-v0.1.0.deb
```

### AppImage (qualquer Linux)

```bash
chmod +x TelegramMediaForwarder-v0.1.0.AppImage
./TelegramMediaForwarder-v0.1.0.AppImage
```

### Rodar pelo código fonte

```bash
pip install telethon
python3 telegram_media_forwarder.py
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

## 🔄 Sistema de atualizações

O programa consulta um arquivo `update.json` hospedado no GitHub
para verificar se existe uma nova versão disponível.

Ao clicar em **↻** no cabeçalho do programa:

- A versão instalada é comparada com a versão mais recente
- O changelog da nova versão é exibido
- Um botão para abrir a release oficial aparece quando houver atualização

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

## 📥 Importar e exportar histórico

O programa permite importar um histórico antigo e exportar o histórico atual.

Útil para:

- Backup do histórico
- Migração entre computadores
- Evitar reenvio de mídias já processadas

---

## ⚠️ Aviso de uso

Use este programa apenas com mídias próprias, autorizadas ou para backup pessoal.
Respeite os termos de uso do Telegram.

---

## 📋 Changelog

<<<<<<< Updated upstream
### v0.1.0 — 31/05/2026

**Adicionado**
- Sistema real de atualização via `update.json`
- Consulta de versão mais recente a partir de arquivo hospedado no GitHub
- Comparação automática entre versão instalada e versão disponível
- Exibição de status de atualização dentro do aplicativo
- Changelog carregado a partir do `update.json`, quando disponível
- Botão para abrir a release oficial no GitHub somente quando houver nova versão
- Função para importar histórico antigo
- Função para exportar o histórico atual
- Mesclagem de histórico sem duplicar registros
- Tela de Ajuda dentro do aplicativo
- Explicações internas sobre API ID, API Hash, login, origem, destino, sessão e segurança
- Botão Sobre o APP dentro da tela de Ajuda
- Opção para salvar o API Hash neste computador
- Estimativa de tempo restante baseada em limite, delay e pausas configuradas

**Melhorado**
- Logs mais claros e fáceis de entender
- Log informa conexão, origem conectada, destino configurado, início, pausa, retomada e finalização
- Tela de Atualizações reorganizada — botão de release aparece apenas quando há atualização
- Estatísticas reorganizadas com mídias enviadas, já no histórico, erros, total, tempo decorrido e tempo restante
- Ordem de processamento ajustada da mais antiga para a mais recente
- `config.json` passou a suportar salvamento opcional do API Hash

**Corrigido**
- Scroll desnecessário em tela cheia
- Changelog abrindo atrás da janela de Atualizações
- Changelog não fechando corretamente
- Conflito entre scroll do Changelog e scroll da tela principal
- Comportamento de colagem nos campos de entrada
- Encaminhamento indevido de figurinhas/stickers do Telegram
- Ordem de processamento das mídias

**Segurança**
- Dados pessoais continuam fora do instalador e dos pacotes de distribuição
- API Hash não é salvo automaticamente
- API Hash só é salvo se o usuário marcar a opção correspondente
- Histórico continua sendo usado para evitar reenvio de mídias já processadas

---
=======
<<<<<<< HEAD
### v0.1.0
- Sistema real de atualização via update.json no GitHub
- Importar e exportar histórico
- Tela de ajuda completa dentro do aplicativo
- Opção para salvar API Hash localmente
- Logs mais claros com nome da origem e destino
- Estatísticas com tempo restante estimado
- Stickers/figurinhas ignorados automaticamente
- Processamento em ordem cronológica (mais antiga → mais recente)
- Correção do scroll desnecessário em tela cheia
- Correção do Changelog abrindo atrás da janela de Atualizações
- Correção do scroll do Changelog interferindo na tela principal
- Correção da colagem de texto nos campos
>>>>>>> Stashed changes

### v0.0.1

- Versão inicial com interface gráfica profissional
- Login do Telegram integrado no próprio aplicativo
- Tema escuro e claro
- Histórico local para evitar mídias repetidas
- Builds para Windows e Linux

---

=======
### v0.1.0 — 31/05/2026

**Adicionado**
- Sistema real de atualização via `update.json`
- Consulta de versão mais recente a partir de arquivo hospedado no GitHub
- Comparação automática entre versão instalada e versão disponível
- Exibição de status de atualização dentro do aplicativo
- Changelog carregado a partir do `update.json`, quando disponível
- Botão para abrir a release oficial no GitHub somente quando houver nova versão
- Função para importar histórico antigo
- Função para exportar o histórico atual
- Mesclagem de histórico sem duplicar registros
- Tela de Ajuda dentro do aplicativo
- Explicações internas sobre API ID, API Hash, login, origem, destino, sessão e segurança
- Botão Sobre o APP dentro da tela de Ajuda
- Opção para salvar o API Hash neste computador
- Estimativa de tempo restante baseada em limite, delay e pausas configuradas

**Melhorado**
- Logs mais claros e fáceis de entender
- Log informa conexão, origem conectada, destino configurado, início, pausa, retomada e finalização
- Tela de Atualizações reorganizada — botão de release aparece apenas quando há atualização
- Estatísticas reorganizadas com mídias enviadas, já no histórico, erros, total, tempo decorrido e tempo restante
- Ordem de processamento ajustada da mais antiga para a mais recente
- `config.json` passou a suportar salvamento opcional do API Hash

**Corrigido**
- Scroll desnecessário em tela cheia
- Changelog abrindo atrás da janela de Atualizações
- Changelog não fechando corretamente
- Conflito entre scroll do Changelog e scroll da tela principal
- Comportamento de colagem nos campos de entrada
- Encaminhamento indevido de figurinhas/stickers do Telegram
- Ordem de processamento das mídias

**Segurança**
- Dados pessoais continuam fora do instalador e dos pacotes de distribuição
- API Hash não é salvo automaticamente
- API Hash só é salvo se o usuário marcar a opção correspondente
- Histórico continua sendo usado para evitar reenvio de mídias já processadas

---

### v0.0.1

- Versão inicial com interface gráfica profissional
- Login do Telegram integrado no próprio aplicativo
- Tema escuro e claro
- Histórico local para evitar mídias repetidas
- Builds para Windows e Linux

---

>>>>>>> 514ee67 (docs: atualiza README para v0.1.0)
🔗 github.com/sleepy907/telegram-media-forwarder
