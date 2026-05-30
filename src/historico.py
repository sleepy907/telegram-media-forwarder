import os
import shutil

from .constantes import HISTORICO
from .utilidades import app_path


class GerenciadorHistorico:
    """Gerencia o historico.txt para evitar reenvio de mídias."""

    def __init__(self, batch_size=50, backup_interval=1000):
        self.batch_size = batch_size
        self.backup_interval = backup_interval
        self.path = app_path(HISTORICO)
        self.backup_path = self.path + ".bak"
        self.cache = set()
        self.buffer = []
        self.unsaved_for_backup = 0
        self._carregar_cache()

    def _carregar_cache(self):
        """Carrega o histórico para a memória."""
        if not os.path.exists(self.path):
            return

        with open(self.path, "r", encoding="utf-8") as f:
            for linha in f:
                item = linha.strip()
                if item:
                    self.cache.add(item)

    def carregar(self):
        """Retorna o cache atual em memória."""
        return self.cache

    def montar_chave(self, grupo_id, msg_id):
        """Monta a chave no formato grupo_id:msg_id."""
        return f"{grupo_id}:{msg_id}"

    def salvar_id(self, grupo_id, msg_id):
        """Adiciona uma entrada ao buffer e cache. Escreve no disco se atingir o lote."""
        chave = self.montar_chave(grupo_id, msg_id)
        if chave not in self.cache:
            self.cache.add(chave)
            self.buffer.append(chave)

            if len(self.buffer) >= self.batch_size:
                self.flush()

    def flush(self):
        """Escreve o buffer no disco e limpa-o. Pode criar backup se atingir intervalo."""
        if not self.buffer:
            return

        with open(self.path, "a", encoding="utf-8") as f:
            for item in self.buffer:
                f.write(f"{item}\n")

        added = len(self.buffer)
        self.buffer.clear()

        self.unsaved_for_backup += added
        if self.unsaved_for_backup >= self.backup_interval:
            self.backup()
            self.unsaved_for_backup = 0

    def backup(self):
        """Cria uma cópia de segurança do arquivo de histórico."""
        if os.path.exists(self.path):
            try:
                shutil.copy2(self.path, self.backup_path)
            except Exception:
                pass

    def limpar(self):
        """Limpa todo o histórico, cache, buffer e remove backup."""
        self.cache.clear()
        self.buffer.clear()
        self.unsaved_for_backup = 0
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("")
        if os.path.exists(self.backup_path):
            try:
                os.remove(self.backup_path)
            except Exception:
                pass

    def total(self):
        """Retorna a quantidade total de registros no histórico."""
        return len(self.cache)

    def normalizar_linhas(self, lines):
        """Normaliza linhas do histórico, mantendo compatibilidade com formato antigo."""
        normalized = []

        for line in lines:
            item = str(line).strip()
            if not item:
                continue

            # Aceita formato antigo: msg_id
            # Aceita formato novo: grupo_id:msg_id
            normalized.append(item)

        return normalized

    def ler_arquivo(self, path):
        """Lê um arquivo de histórico e retorna as linhas normalizadas."""
        with open(path, "r", encoding="utf-8") as f:
            return self.normalizar_linhas(f.readlines())

    def escrever_arquivo(self, items):
        """Sobrescreve o histórico com a lista de itens fornecida."""
        with open(self.path, "w", encoding="utf-8") as f:
            for item in items:
                f.write(f"{item}\n")
        
        # Atualiza o cache e limpa o buffer
        self.cache.clear()
        self.buffer.clear()
        self.unsaved_for_backup = 0
        for item in items:
            self.cache.add(item)

    def importar(self, caminho_arquivo):
        """Importa histórico de um arquivo externo, mesclando com o atual.

        Retorna um dicionário com estatísticas da importação:
        - 'adicionados': quantidade de registros novos
        - 'total': quantidade total após merge
        - 'erro': None ou mensagem de erro
        """
        try:
            imported_items = self.ler_arquivo(caminho_arquivo)

            if not imported_items:
                return {
                    "adicionados": 0,
                    "total": 0,
                    "erro": "O arquivo selecionado não possui registros válidos."
                }

            current_items = []
            current_path = self.path

            if os.path.exists(current_path):
                current_items = self.ler_arquivo(current_path)

            merged = []
            seen = set()

            for item in current_items + imported_items:
                if item not in seen:
                    seen.add(item)
                    merged.append(item)

            self.escrever_arquivo(merged)

            adicionados = len([item for item in imported_items if item not in set(current_items)])

            return {
                "adicionados": max(0, adicionados),
                "total": len(merged),
                "erro": None
            }

        except Exception as e:
            return {
                "adicionados": 0,
                "total": 0,
                "erro": str(e)
            }

    def exportar(self, caminho_destino):
        """Exporta o histórico atual para um arquivo externo.

        Retorna um dicionário com estatísticas da exportação:
        - 'exportados': quantidade de registros exportados
        - 'erro': None ou mensagem de erro
        """
        try:
            current_path = self.path

            if not os.path.exists(current_path):
                return {
                    "exportados": 0,
                    "erro": "Nenhum historico.txt foi encontrado para exportar."
                }

            items = self.ler_arquivo(current_path)

            with open(caminho_destino, "w", encoding="utf-8") as f:
                for item in items:
                    f.write(f"{item}\n")

            return {
                "exportados": len(items),
                "erro": None
            }

        except Exception as e:
            return {
                "exportados": 0,
                "erro": str(e)
            }
