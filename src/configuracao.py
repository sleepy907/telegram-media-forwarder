
import os
import json

from .constantes import CONFIG
from .utilidades import app_path


class GerenciadorConfig:
    """Gerencia leitura e escrita do config.json."""

    def salvar(self, data):
        """Salva configurações no config.json.

        O API Hash não é salvo por segurança, a menos que
        o usuário tenha marcado a opção correspondente.
        """
        with open(app_path(CONFIG), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def carregar(self):
        """Carrega configurações do config.json.

        Retorna um dicionário vazio caso o arquivo não exista ou esteja corrompido.
        """
        path = app_path(CONFIG)
        if not os.path.exists(path):
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
