
import asyncio

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError

from .utilidades import app_path, media_eh_sticker, nome_entidade_telegram
from .constantes import SESSION


class ServicoTelegram:
    """Encapsula toda a interação com o Telethon.

    Não possui referência ao Tkinter. Se comunica com a interface
    via callbacks passados nos métodos.
    """

    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None

    async def conectar(self):
        """Cria e conecta o TelegramClient."""
        self.client = TelegramClient(app_path(SESSION), self.api_id, self.api_hash)
        await self.client.connect()

    async def desconectar(self):
        """Desconecta o client se estiver conectado."""
        if self.client:
            await self.client.disconnect()

    async def esta_autorizado(self):
        """Verifica se a sessão está autorizada."""
        return await self.client.is_user_authorized()

    async def enviar_codigo(self, phone):
        """Envia código de login para o telefone.

        Retorna o phone_code_hash necessário para confirmar o login.
        Retorna None se o usuário já estiver autorizado.
        """
        if await self.esta_autorizado():
            return None

        sent = await self.client.send_code_request(phone)
        return sent.phone_code_hash

    async def confirmar_login(self, phone, code, phone_code_hash, password=""):
        """Confirma o login com código e/ou senha 2FA.

        Lança SessionPasswordNeededError se a senha 2FA for necessária
        mas não foi fornecida.
        """
        if await self.esta_autorizado():
            return

        if password and not code:
            await self.client.sign_in(password=password)
            return

        try:
            await self.client.sign_in(
                phone=phone,
                code=code,
                phone_code_hash=phone_code_hash
            )
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
            else:
                raise

    async def verificar_sessao(self):
        """Conecta, verifica se a sessão está autorizada e desconecta.

        Retorna True se autorizada, False caso contrário.
        """
        try:
            await self.conectar()
            return await self.esta_autorizado()
        finally:
            await self.desconectar()

    async def resolver_entidade(self, target):
        """Resolve uma entidade do Telegram.

        Retorna uma tupla (input_entity, entity_full, label).
        """
        input_entity = await self.client.get_input_entity(target)

        if str(target).strip().lower() == "me":
            label = "Mensagens Salvas"
            entity_full = None
        else:
            try:
                entity_full = await self.client.get_entity(target)
                label = nome_entidade_telegram(entity_full, target)
            except Exception:
                entity_full = None
                label = str(target)

        return input_entity, entity_full, label

    async def encaminhar_midias(self, params, historico, callbacks):
        """Loop principal de encaminhamento de mídias.

        Parâmetros:
        - params: dict com 'group', 'dest', 'filter', 'delay', 'batch', 'pause', 'limit'
        - historico: instância de GerenciadorHistorico
        - callbacks: dict com funções de callback:
            - 'on_log': fn(msg, tag)
            - 'on_status': fn(text, color)
            - 'on_progress': fn(value, maximum)
            - 'on_update_stats': fn()
            - 'get_live_config': fn() -> (delay, batch, pause, limit)
            - 'is_stopped': fn() -> bool
            - 'is_paused': fn() -> bool
            - 'get_colors': fn() -> dict
            - 'inc_sent': fn() -> int (incrementa e retorna novo valor)
            - 'inc_skip': fn()
            - 'inc_already_saved': fn()
            - 'inc_ignored': fn()
            - 'inc_error': fn()
            - 'get_sent_count': fn() -> int
        """
        on_log = callbacks["on_log"]
        on_status = callbacks["on_status"]
        on_progress = callbacks["on_progress"]
        on_update_stats = callbacks["on_update_stats"]
        get_live_config = callbacks["get_live_config"]
        is_stopped = callbacks["is_stopped"]
        is_paused = callbacks["is_paused"]
        get_colors = callbacks["get_colors"]
        inc_sent = callbacks["inc_sent"]
        inc_skip = callbacks["inc_skip"]
        inc_already_saved = callbacks["inc_already_saved"]
        inc_ignored = callbacks["inc_ignored"]
        inc_error = callbacks["inc_error"]
        get_sent_count = callbacks["get_sent_count"]

        ja_enviados = historico.carregar()
        on_log(f"Histórico carregado: {len(ja_enviados)} registros.", "info")

        # Resolver destino
        try:
            saved, _, dest_label = await self.resolver_entidade(params["dest"])
        except Exception as e:
            on_log(f"Não foi possível acessar o destino: {params['dest']}", "err")
            on_log("Verifique se o destino existe e se sua conta tem permissão para enviar mensagens nele.", "warn")
            on_log(f"Detalhe técnico: {e}", "muted")
            return

        # Resolver origem
        try:
            group, group_full, group_label = await self.resolver_entidade(params["group"])
            group_id = getattr(group_full, "id", "desconhecido") if group_full else "desconhecido"
        except Exception as e:
            on_log(f"Não foi possível acessar a origem: {params['group']}", "err")
            on_log("Verifique se o link, grupo ou canal está correto e se sua conta tem acesso a ele.", "warn")
            on_log(f"Detalhe técnico: {e}", "muted")
            return

        on_log(f"Conectado à origem: {group_label}", "ok")
        on_log(f"ID interno da origem: {group_id}", "info")
        on_log(f"Destino configurado: {dest_label}", "ok")

        # Resolver filtro
        filter_id = None
        if params.get("filter"):
            try:
                filter_ent = await self.client.get_entity(params["filter"])
                filter_id = filter_ent.id
                filter_label = nome_entidade_telegram(filter_ent, params["filter"])
                on_log(f"Filtro ativo: {filter_label}", "info")
                on_log(f"ID interno do filtro: {filter_id}", "muted")
            except Exception as e:
                on_log("Filtro inválido ou inacessível.", "err")
                on_log("Verifique se o filtro foi preenchido corretamente e se sua conta tem acesso a ele.", "warn")
                on_log(f"Detalhe técnico: {e}", "muted")
                return

        drop_author = params.get("drop_author", False)
        drop_captions = params.get("drop_captions", False)
        if drop_captions:
            drop_author = True

        on_log("Iniciando encaminhamento de mídias...", "ok")
        if drop_author or drop_captions:
            on_log(f"Modo limpo ativo (Ocultar autor: {drop_author} | Sem legenda: {drop_captions})", "info")

        c = get_colors()
        on_status("Encaminhando", c["GREEN"])

        try:
            album_buffer = []
            current_grouped_id = None

            async def _flush_buffer():
                nonlocal album_buffer, current_grouped_id
                if not album_buffer:
                    return False

                delay, batch, pause_secs, limit = get_live_config()
                sent = get_sent_count()
                count = len(album_buffer)

                if sent + count > limit:
                    if count > 1:
                        on_log("Álbum ignorado: excederia o limite total configurado.", "warn")
                    else:
                        on_log("Mídia ignorada: excederia o limite total configurado.", "warn")
                    album_buffer.clear()
                    current_grouped_id = None
                    return True

                try:
                    await self.client.forward_messages(
                        saved, 
                        album_buffer,
                        drop_author=drop_author,
                        drop_media_captions=drop_captions
                    )

                    for m in album_buffer:
                        historico.salvar_id(group_id, m.id)
                        ja_enviados.add(historico.montar_chave(group_id, m.id))

                    sent_count = 0
                    for _ in range(count):
                        sent_count = inc_sent()

                    on_update_stats()
                    on_progress(sent_count, limit)

                    if count > 1:
                        on_log(f"[{sent_count}/{limit}] Álbum encaminhado com sucesso: {count} mídias.", "ok")
                    else:
                        on_log(f"[{sent_count}/{limit}] Mídia encaminhada com sucesso. ID {album_buffer[0].id}", "ok")

                    album_buffer.clear()
                    current_grouped_id = None

                    if sent_count >= limit:
                        on_log(f"Encaminhamento concluído. {sent_count} mídias enviadas nesta execução.", "ok")
                        c = get_colors()
                        on_status("Concluído", c["ACCENT3"])
                        return True

                    if sent_count % batch == 0 or (sent_count - count) // batch < sent_count // batch:
                        on_log(f"Pausa automática iniciada: aguardando {pause_secs}s após {sent_count} mídias enviadas.", "warn")
                        c = get_colors()
                        on_status(f"Pausa {pause_secs}s", c["YELLOW"])

                        for _ in range(pause_secs * 2):
                            if is_stopped():
                                return True
                            if is_paused():
                                break
                            await asyncio.sleep(0.5)

                        if not is_paused() and not is_stopped():
                            c = get_colors()
                            on_status("Encaminhando", c["GREEN"])

                    await asyncio.sleep(delay)
                    return False

                except FloodWaitError as e:
                    inc_error()
                    on_update_stats()
                    on_log(f"O Telegram pediu uma pausa temporária. Aguardando {e.seconds}s antes de continuar.", "warn")
                    c = get_colors()
                    on_status(f"FloodWait {e.seconds}s", c["YELLOW"])
                    await asyncio.sleep(e.seconds + 5)
                    c = get_colors()
                    on_status("Encaminhando", c["GREEN"])
                    album_buffer.clear()
                    current_grouped_id = None
                    return False

                except RPCError as e:
                    inc_error()
                    on_update_stats()
                    on_log("O Telegram recusou o envio do lote/mídia.", "err")
                    on_log("O envio foi pulado e o programa continuará com as próximas mídias.", "warn")
                    on_log(f"Detalhe técnico: {e}", "muted")
                    album_buffer.clear()
                    current_grouped_id = None
                    return False

                except Exception as e:
                    inc_error()
                    on_update_stats()
                    on_log(f"Erro inesperado ao enviar lote/mídia: {e}", "err")
                    album_buffer.clear()
                    current_grouped_id = None
                    return False

            # Processa em ordem cronológica: da mídia mais antiga para a mais recente.
            async for msg in self.client.iter_messages(group, reverse=True):
                if is_stopped():
                    sent = get_sent_count()
                    on_log(f"Execução interrompida pelo usuário. Mídias enviadas nesta execução: {sent}.", "warn")
                    return

                while is_paused():
                    await asyncio.sleep(0.3)
                    if is_stopped():
                        return

                # Descarrega álbum anterior ANTES de aplicar qualquer filtro.
                # Se a mensagem atual pertence a outro álbum (ou é avulsa), o álbum acumulado deve ser enviado.
                if album_buffer:
                    if not msg.grouped_id or msg.grouped_id != current_grouped_id:
                        limit_reached = await _flush_buffer()
                        if limit_reached or is_stopped():
                            return

                if not msg.media:
                    continue

                if not isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                    inc_skip()
                    inc_ignored()
                    on_update_stats()
                    continue

                if media_eh_sticker(msg.media):
                    inc_skip()
                    on_update_stats()
                    on_log("Mídia ignorada: figurinha/sticker.", "info")
                    continue

                chave = historico.montar_chave(group_id, msg.id)

                if chave in ja_enviados or str(msg.id) in ja_enviados:
                    inc_skip()
                    inc_already_saved()
                    on_update_stats()
                    continue

                if filter_id is not None:
                    fwd = msg.fwd_from
                    if not fwd:
                        inc_skip()
                        on_update_stats()
                        continue

                    from_id = (
                        getattr(fwd.from_id, "channel_id", None)
                        or getattr(fwd.from_id, "chat_id", None)
                        or getattr(fwd.from_id, "user_id", None)
                    )

                    if from_id != filter_id:
                        inc_skip()
                        on_update_stats()
                        continue

                # Mídia passou nos filtros. Acumula no buffer.
                if msg.grouped_id:
                    current_grouped_id = msg.grouped_id
                    album_buffer.append(msg)
                else:
                    # Mídia avulsa válida. Envia imediatamente.
                    album_buffer.append(msg)
                    limit_reached = await _flush_buffer()
                    if limit_reached or is_stopped():
                        return

            if album_buffer and not is_stopped():
                await _flush_buffer()
        finally:
            historico.flush()

        sent = get_sent_count()
        skip = callbacks.get("get_skip_count", lambda: 0)()
        errors = callbacks.get("get_error_count", lambda: 0)()
        on_log("Fim da origem. Não há mais mídias para processar dentro do limite configurado.", "ok")
        on_log(f"Resumo final — Enviadas: {sent} | Já salvas/ignoradas: {skip} | Erros: {errors}", "info")
