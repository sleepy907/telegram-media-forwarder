# Changelog — Telegram Media Forwarder v0.1.0

Data: 31/05/2026

## Visão geral

A versão **v0.1.0** marca a primeira versão pública organizada do Telegram Media Forwarder.

Esta atualização transforma o projeto de uma versão inicial funcional em um aplicativo mais completo, com melhorias de usabilidade, segurança, histórico, logs, estatísticas, tela de ajuda e preparação para atualizações reais via GitHub.

---

## Adicionado

- Sistema real de atualização via `update.json`.
- Consulta de versão mais recente a partir de um arquivo hospedado no GitHub.
- Comparação automática entre a versão instalada e a versão mais recente disponível.
- Exibição de status de atualização dentro do aplicativo.
- Changelog carregado a partir do `update.json`, quando disponível.
- Botão para abrir a release oficial no GitHub somente quando houver nova versão disponível.
- Função para importar histórico antigo.
- Função para exportar o histórico atual.
- Mesclagem de histórico sem duplicar registros.
- Tela de Ajuda dentro do aplicativo.
- Explicações internas sobre API ID, API Hash, login, origem, destino, `me`, sessão, histórico, configurações e segurança.
- Botão **Sobre o APP** dentro da tela de Ajuda.
- Opção para salvar o API Hash neste computador.
- Estimativa de tempo restante baseada em limite, delay e pausas configuradas.

---

## Melhorado

- Logs mais claros e fáceis de entender.
- Mensagens técnicas passaram a ser acompanhadas por explicações mais amigáveis.
- Log informa quando a conexão com o Telegram foi realizada com sucesso.
- Log mostra a origem conectada.
- Log mostra o destino configurado.
- Log informa início, pausa, retomada, parada e finalização do encaminhamento.
- Tela de Atualizações reorganizada.
- Botão de release aparece apenas quando há atualização disponível.
- Área de estatísticas reorganizada.
- Estatísticas agora deixam mais claro:
  - mídias enviadas na execução atual;
  - mídias já existentes no histórico;
  - erros;
  - total processado;
  - tempo decorrido;
  - tempo restante estimado.
- A ordem de processamento das mídias foi ajustada para seguir da mais antiga para a mais recente.
- Tela de Ajuda recebeu informações de segurança e boas práticas.
- `config.json` passou a suportar o salvamento opcional do API Hash.
- O API Hash continua não sendo salvo por padrão.

---

## Corrigido

- Corrigido scroll desnecessário em tela cheia.
- Corrigido Changelog abrindo atrás da janela de Atualizações.
- Corrigido Changelog não fechando corretamente.
- Corrigido conflito entre scroll do Changelog e scroll da tela principal.
- Corrigido comportamento de colagem nos campos de entrada.
- Corrigido encaminhamento indevido de figurinhas/stickers do Telegram.
- Corrigida ordem de processamento das mídias, agora da mais antiga para a mais recente.

---

## Segurança e privacidade

- `sessao.session`, `historico.txt` e `config.json` continuam sendo arquivos locais do usuário.
- Dados pessoais continuam fora do instalador, executável e pacotes de distribuição.
- O API Hash não é salvo automaticamente.
- O API Hash só é salvo no `config.json` se o usuário marcar a opção **Salvar API Hash neste computador**.
- O histórico continua sendo usado para evitar reenvio de mídias já processadas.
- O aplicativo continua focado em uso autorizado, backup pessoal e controle local.

---

## Versão

**Telegram Media Forwarder v0.1.0**
