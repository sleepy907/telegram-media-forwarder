# Telegram Media Forwarder

**Telegram Media Forwarder** é um aplicativo desktop desenvolvido em **Python** com interface gráfica em **Tkinter**, criado para automatizar o encaminhamento autorizado de mídias do Telegram usando a biblioteca **Telethon**.

O projeto permite encaminhar fotos, vídeos e documentos de uma origem do Telegram para um destino configurável, como **Mensagens Salvas**, grupos, canais ou bots, com controle de limite, delay, pausas automáticas, histórico de mídias já enviadas, login diretamente pelo próprio aplicativo, importação/exportação de histórico, tela de ajuda e sistema real de atualização via GitHub.

---

## 🚀 Versão atual

**Versão atual:** `v0.1.0`

A versão **v0.1.0** marca a primeira versão pública organizada do Telegram Media Forwarder.

---

## 🚀 Principais recursos

- Interface gráfica moderna em Python/Tkinter
- Tema escuro e tema claro
- Logo integrada ao aplicativo
- Login do Telegram dentro do próprio programa
- Encaminhamento autorizado de mídias
- Suporte a fotos, vídeos e documentos
- Ignora figurinhas/stickers automaticamente
- Origem e destino configuráveis
- Envio para Mensagens Salvas, grupos, canais ou bots
- Delay configurável entre envios
- Limite total de mídias por execução
- Pausa automática a cada X mídias
- Botões para iniciar, pausar/retomar e parar
- Log em tempo real com mensagens mais claras
- Estatísticas em tempo real
- Estimativa de tempo restante
- Histórico para evitar mídias repetidas
- Importação e exportação de histórico
- Compatibilidade com histórico antigo
- Tela de Ajuda integrada
- Tela Sobre o APP dentro da Ajuda
- Sistema real de update via `update.json`
- Changelog remoto via `CHANGELOG.md`
- Botão para abrir a release oficial no GitHub quando houver nova versão disponível
- Opção para salvar API Hash neste computador

---

## 🖥️ Tecnologias utilizadas

- Python
- Tkinter
- Telethon
- JSON
- Git/GitHub
- PyInstaller
- Linux installer via `.tar.gz`
- RPM Build
- Debian Package
- AppImage Build

---

## 📷 Interface

O programa possui uma interface organizada em cards:

### Credenciais

- API ID
- API Hash
- Teste de campos
- Login Telegram
- Opção para salvar API Hash neste computador

### Configurações

- Origem
- Destino
- Filtro opcional
- Delay
- Limite total
- Pausa automática
- Tempo de pausa

### Estatísticas

- Mídias enviadas agora
- Mídias já salvas no histórico
- Erros
- Tempo decorrido
- Tempo restante estimado
- Total processado

### Log

- Registro em tempo real das ações do programa
- Mensagens de conexão
- Origem conectada
- Destino configurado
- Início, pausa, retomada, parada e finalização
- Mensagens de erro mais amigáveis

---

## ⚙️ Como usar

### Windows

Baixe o executável da release oficial:

```text
TelegramMediaForwarder-v0.1.0.exe