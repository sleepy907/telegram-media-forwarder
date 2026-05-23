# Changelog — Telegram Media Forwarder

## v0.0.1

### Adicionado

- Interface gráfica profissional em Python/Tkinter.
- Integração com Telethon.
- Tema claro e escuro.
- Logo integrada ao cabeçalho.
- Botões principais centralizados.
- Tela de login do Telegram dentro do aplicativo.
- Histórico para evitar reenvio de mídias.
- Estatísticas em tempo real.
- Log de execução.
- Changelog interno.
- Scroll vertical para telas menores.
- Estrutura preparada para futuras atualizações.

### Segurança

- API Hash não é salvo automaticamente por padrão.
- Sessão do Telegram criada localmente no computador do usuário.
- `sessao.session`, `config.json` e `historico.txt` não devem ser enviados ao GitHub.