# Changelog — Telegram Media Forwarder

## v0.2.0 — 04/06/2026

### Visão Geral
A versão **v0.2.0** traz um enorme salto tecnológico para o aplicativo. A arquitetura monolítica foi desmembrada em um sistema modular e o repositório agora possui uma organização profissional de diretórios. Esta atualização eleva a ferramenta com melhorias críticas na velocidade, segurança do histórico, repasse inteligente de álbuns e uma drástica evolução visual (Catppuccin).

### Arquitetura e Estrutura
- **Modularização (S.O.L.I.D):** Código-fonte isolado em componentes (`gui`, `servico_telegram`, `historico`, `configuracao`, `atualizacao`).
- **Nova Estrutura:** Ponto de entrada migrado para `main.py`, arquivos lógicos confinados em `src/` e imagens em `assets/`.

### Adicionado
- **Preservação de Álbuns (Mosaico):** Identificação e envelopamento de mídias agrupadas. O Telegram agora recebe lotes unificados ao invés de disparos quebrados.
- **Modo Limpo (Clean Forward):** Opções na tela principal para **Ocultar autor original** e **Remover legenda/texto**.
- **Logs Contextuais de Álbum:** Informes precisos indicando quando as mídias estão sendo estocadas ou processadas por lote.

### Melhorado
- **Segurança Fail-Safe no Histórico:** Salva mídias em memória e só envia ao disco esporadicamente, prolongando a vida útil do hardware e acelerando o aplicativo. Em caso de fechamento abrupto, os blocos `try...finally` garantem o despejo imediato (flush) no disco.
- **Refatoração Visual Extrema:** Fim do design "Neon". Adoção da estética "Flat Design" sem bordas e migração total para a paleta *Catppuccin Macchiato*, com contrastes escuros e elegantes.
- **Pausas por Lote:** Um álbum de várias mídias é contado de uma só vez, aplicando o delay apenas na finalização do bloco.
- **Traces de Interface:** As caixas de Modo Limpo interagem sozinhas (desligar a legenda força o ocultamento do autor, respeitando limitações internas do Telethon).
