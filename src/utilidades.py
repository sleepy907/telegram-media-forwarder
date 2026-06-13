import os
import sys

from telethon.tl.types import MessageMediaDocument, DocumentAttributeSticker

from .constantes import HISTORICO, CONFIG, SESSION


def resource_path(relative_path):
    """Retorna o caminho absoluto do recurso, compatível com PyInstaller e dev."""
    try:
        # O PyInstaller cria uma pasta temporária em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Em dev, o arquivo atual está dentro de src/, então voltamos uma pasta
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def app_dir():
    base = os.environ.get("XDG_DATA_HOME")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")

    path = os.path.join(base, "telegram-media-forwarder")
    os.makedirs(path, exist_ok=True)
    return path


def app_path(filename):
    return os.path.join(app_dir(), filename)


def media_eh_sticker(media):
    """Retorna True quando a mídia for figurinha/sticker do Telegram."""
    try:
        if not isinstance(media, MessageMediaDocument):
            return False

        document = getattr(media, "document", None)
        if not document:
            return False

        attributes = getattr(document, "attributes", []) or []
        return any(isinstance(attr, DocumentAttributeSticker) for attr in attributes)
    except Exception:
        return False


def nome_entidade_telegram(entity, fallback="desconhecido"):
    """Retorna um nome amigável para grupos, canais, bots, usuários e destinos."""
    try:
        title = getattr(entity, "title", None)
        if title:
            return str(title)

        first_name = getattr(entity, "first_name", "") or ""
        last_name = getattr(entity, "last_name", "") or ""
        full_name = f"{first_name} {last_name}".strip()
        if full_name:
            return full_name

        username = getattr(entity, "username", None)
        if username:
            return f"@{username}"

        entity_id = getattr(entity, "id", None)
        if entity_id:
            return f"{fallback} ({entity_id})"
    except Exception:
        pass

    return str(fallback)
