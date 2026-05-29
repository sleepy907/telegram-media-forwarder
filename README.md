# Telegram Media Forwarder

<<<<<<< HEAD
**Telegram Media Forwarder** é um aplicativo desktop desenvolvido em **Python** com interface gráfica em **Tkinter**, criado para automatizar o encaminhamento autorizado de mídias do Telegram usando a biblioteca **Telethon**.

O projeto permite encaminhar fotos, vídeos e documentos de uma origem do Telegram para um destino configurável, como **Mensagens Salvas**, grupos, canais ou bots, com controle de limite, delay, pausas automáticas, histórico de mídias já enviadas, login diretamente pelo próprio aplicativo, importação/exportação de histórico, tela de ajuda e sistema real de atualização via GitHub.

---

## 🚀 Versão atual

**Versão atual:** `v0.1.0`

A versão **v0.1.0** marca a primeira versão pública organizada do Telegram Media Forwarder.
=======
**Telegram Media Forwarder** é um aplicativo desktop feito em Python com Tkinter e Telethon para encaminhamento autorizado de mídias do Telegram.

O projeto foi pensado para facilitar backup pessoal, organização de mídias e gerenciamento local, mantendo sessão, histórico e configurações na máquina do usuário.

---

## Versão atual

**v0.1.0**

Esta versão representa a primeira versão pública organizada do projeto, com interface gráfica completa, login integrado, histórico, importação/exportação, tela de ajuda, logs melhorados, estatísticas mais claras e sistema de atualização preparado via GitHub.
>>>>>>> ee5b201 (Atualiza update.json para v0.1.0)

---

## Principais recursos

<<<<<<< HEAD
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
=======
- Interface gráfica com Tkinter.
- Tema escuro e tema claro.
- Login do Telegram dentro do aplicativo.
- Encaminhamento autorizado de mídias entre grupos, canais, conversas ou Mensagens Salvas.
- Suporte ao destino `me`, equivalente a **Mensagens Salvas**.
- Histórico local para evitar reenvio de mídias.
- Importação e exportação de `historico.txt`.
- Estatísticas em tempo real.
- Estimativa de tempo restante.
- Logs mais claros e informativos.
- Tela de Ajuda integrada.
- Changelog dentro do app.
- Sistema real de atualização via `update.json`.
- Filtro para ignorar figurinhas/stickers.
- Processamento em ordem cronológica, da mídia mais antiga para a mais recente.
- Opção para salvar API Hash localmente, caso o usuário permita.
>>>>>>> ee5b201 (Atualiza update.json para v0.1.0)

---

## Requisitos

- Python 3
- Telethon
<<<<<<< HEAD
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
=======
- Tkinter

Instalação da dependência principal:

```bash
pip install telethon
```

Em algumas distribuições Linux, pode ser necessário instalar o Tkinter separadamente.

Exemplo no Fedora:

```bash
sudo dnf install python3-tkinter
```

---

## Como usar

1. Abra o aplicativo.
2. Preencha o **API ID**.
3. Preencha o **API Hash**.
4. Informe a **Origem**, que pode ser um grupo, canal ou conversa.
5. Informe o **Destino**.
6. Use `me` para encaminhar para **Mensagens Salvas**.
7. Clique em **Login Telegram** para gerar a sessão.
8. Depois do login, clique em **Iniciar**.

---

## API ID e API Hash

Para usar o aplicativo, é necessário criar credenciais da API do Telegram.

1. Acesse `https://my.telegram.org`.
2. Faça login com sua conta Telegram.
3. Entre em **API development tools**.
4. Crie um aplicativo.
5. Copie o **API ID** e o **API Hash**.
6. Cole os dados no Telegram Media Forwarder.

Por segurança, o API Hash não é salvo automaticamente.

A partir da v0.1.0, existe a opção:

```text
Salvar API Hash neste computador
```

Use essa opção apenas em computadores pessoais e confiáveis.

---

## Arquivos locais do usuário

Os arquivos pessoais do aplicativo ficam fora do instalador e fora do executável.

No Linux, o caminho padrão é:

```bash
~/.local/share/telegram-media-forwarder
```

Arquivos principais:

```text
sessao.session
historico.txt
config.json
```

### `sessao.session`

Arquivo local que mantém a autenticação da conta Telegram.

Não compartilhe esse arquivo.

### `historico.txt`

Arquivo local que registra as mídias já processadas.

Ele evita que o programa encaminhe a mesma mídia novamente.

Formato atual:

```text
grupo_id:msg_id
```

Também existe compatibilidade com histórico antigo baseado apenas em `msg_id`.

### `config.json`

Arquivo local de configurações do aplicativo.

Pode armazenar:

- API ID;
- origem;
- destino;
- filtro;
- delay;
- limite;
- pausas;
- tema;
- opção de salvar API Hash.

O API Hash só é salvo se o usuário marcar essa opção no aplicativo.

---

## Importar e exportar histórico

A versão v0.1.0 adiciona gerenciamento de histórico.

### Importar histórico

Use para reaproveitar um `historico.txt` antigo.

O aplicativo mescla o histórico antigo com o atual sem duplicar registros.

### Exportar histórico

Use para criar uma cópia de segurança do histórico atual.

Isso facilita migração entre computadores, reinstalações e troca de versões.

---

## Estatísticas

A área de estatísticas mostra:

- mídias enviadas agora;
- mídias já existentes no histórico;
- erros;
- total processado;
- tempo decorrido;
- tempo restante estimado.

O tempo restante é calculado com base nos campos:

- limite total;
- delay;
- pausa a cada X mídias;
- tempo de pausa.

---

## Atualizações

A versão v0.1.0 inclui suporte a atualização real via `update.json`.

O aplicativo pode consultar um arquivo remoto no GitHub para verificar se existe uma nova versão.

Exemplo de `update.json`:

```json
{
    "version": "0.1.0",
    "release_url": "https://github.com/SEU_USUARIO/SEU_REPOSITORIO/releases/tag/v0.1.0",
    "changelog": [
        "Sistema real de atualização via update.json.",
        "Importar/exportar histórico.",
        "Tela de Ajuda dentro do aplicativo.",
        "Logs mais claros e informativos."
    ]
}
```

No código, configure:

```python
UPDATE_URL = "https://raw.githubusercontent.com/SEU_USUARIO/SEU_REPOSITORIO/main/update.json"
```

---

## Segurança e privacidade

O Telegram Media Forwarder foi desenvolvido com foco em controle local.

- O aplicativo não inclui `sessao.session` no instalador.
- O aplicativo não inclui `historico.txt` no instalador.
- O aplicativo não inclui `config.json` no instalador.
- O processamento ocorre localmente.
- A sessão do Telegram é criada na máquina do usuário.
- O histórico fica salvo localmente.
- O API Hash não é salvo por padrão.
- O API Hash só é salvo se o usuário permitir.
- O aplicativo não coleta dados ocultamente.
- O aplicativo não envia arquivos do usuário para servidores externos próprios.

Use apenas com mídias próprias, autorizadas ou para backup pessoal.

---

## Changelog resumido da v0.1.0

### Adicionado

- Sistema real de atualização via `update.json`.
- Importar/exportar histórico.
- Tela de Ajuda.
- Botão Sobre o APP dentro da Ajuda.
- Estimativa de tempo restante.
- Opção para salvar API Hash neste computador.

### Melhorado

- Logs mais claros.
- Estatísticas reorganizadas.
- Tela de Atualizações mais limpa.
- Ordem de processamento das mídias.
- Ajuda interna com boas práticas de segurança.

### Corrigido

- Scroll desnecessário em tela cheia.
- Changelog abrindo atrás da janela de Atualizações.
- Changelog não fechando corretamente.
- Scroll do Changelog interferindo no scroll principal.
- Colagem de texto nos campos.
- Stickers sendo encaminhados indevidamente.
- Processamento agora segue da mídia mais antiga para a mais recente.

---

## Status

```text
Telegram Media Forwarder v0.1.0
Primeira versão pública organizada
```

---

## Licença

Defina aqui a licença do projeto.

Exemplo:

```text
MIT License
```

---

## Aviso

Este projeto é voltado para uso autorizado, organização de mídias e backup pessoal.

O usuário é responsável pelo uso da ferramenta e deve respeitar as regras do Telegram, permissões dos grupos/canais e direitos sobre os conteúdos processados.
>>>>>>> ee5b201 (Atualiza update.json para v0.1.0)
