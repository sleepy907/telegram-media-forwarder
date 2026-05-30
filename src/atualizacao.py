
import json
import urllib.request

from .constantes import APP_NAME, APP_VERSION, UPDATE_URL, CHANGELOG_URL, LATEST_VERSION_PLACEHOLDER


class GerenciadorAtualizacao:
    """Gerencia checagem de versão e leitura de changelog remoto."""

    def versao_tupla(self, version):
        """Converte uma string de versão em tupla para comparação."""
        parts = []
        for piece in str(version).replace("v", "").split("."):
            try:
                parts.append(int(piece))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    def comparar_versoes(self, v1, v2):
        """Compara duas versões.

        Retorna:
        -  1 se v1 > v2
        -  0 se v1 == v2
        - -1 se v1 < v2
        """
        t1 = self.versao_tupla(v1)
        t2 = self.versao_tupla(v2)

        if t1 > t2:
            return 1
        elif t1 < t2:
            return -1
        else:
            return 0

    def buscar_texto_url(self, url, timeout=10):
        """Baixa texto puro de uma URL."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"}
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")

    def buscar_info_atualizacao(self):
        """Consulta o update.json e carrega o CHANGELOG.md completo quando possível.

        Retorna um dicionário com:
        - 'version': versão mais recente
        - 'release_url': link da release
        - 'changelog': texto do changelog
        """
        if not UPDATE_URL:
            return {
                "version": LATEST_VERSION_PLACEHOLDER,
                "release_url": "",
                "changelog": "UPDATE_URL ainda não configurado no código."
            }

        raw = self.buscar_texto_url(UPDATE_URL)
        data = json.loads(raw)

        version = str(data.get("version", "")).strip()
        release_url = str(data.get("release_url", "")).strip()

        if not version:
            raise ValueError("O update.json não possui o campo obrigatório: version.")

        # O app deve priorizar o CHANGELOG.md completo.
        # Se o update.json tiver changelog_url, usa ele.
        # Se não tiver, usa a constante CHANGELOG_URL.
        changelog_url = str(data.get("changelog_url", "")).strip() or CHANGELOG_URL
        changelog = data.get("changelog", "")

        try:
            if changelog_url:
                remote_changelog = self.buscar_texto_url(changelog_url).strip()
                if remote_changelog:
                    changelog = remote_changelog
        except Exception as e:
            if isinstance(changelog, list):
                changelog = "\n".join(f"• {item}" for item in changelog)
            else:
                changelog = str(changelog).strip()

            changelog = (
                f"{changelog}\n\n"
                f"Aviso: não foi possível carregar o CHANGELOG.md completo.\n"
                f"Detalhe técnico: {e}"
            )

        if isinstance(changelog, list):
            changelog = "\n".join(f"• {item}" for item in changelog)
        else:
            changelog = str(changelog).strip()

        return {
            "version": version,
            "release_url": release_url,
            "changelog": changelog
        }
