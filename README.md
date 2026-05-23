# Telegram Media Forwarder

Aplicativo desktop em Python/Tkinter para encaminhamento autorizado de mídias do Telegram usando Telethon.

## Recursos

- Interface gráfica moderna
- Tema claro e escuro
- Login do Telegram dentro do aplicativo
- Encaminhamento autorizado de mídias
- Histórico para evitar reenvio de mídias
- Delay, limite e pausa automática configuráveis
- Log e estatísticas em tempo real
- Changelog interno
- Preparado para empacotamento em Windows e Linux

## Segurança

Este projeto não inclui arquivos pessoais como:

- `sessao.session`
- `config.json`
- `historico.txt`

Cada usuário deve gerar sua própria sessão pelo botão **Login Telegram** dentro do aplicativo.

## Como executar pelo código-fonte

Instale as dependências:

```bash
pip install -r requirements.txt

Execute:

python3 telegram_media_forwarder.py