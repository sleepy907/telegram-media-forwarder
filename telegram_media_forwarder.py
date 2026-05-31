
import asyncio
import threading
import os
import json
import time
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeSticker
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError, ApiIdInvalidError, PhoneCodeInvalidError, PasswordHashInvalidError

APP_NAME = "Telegram Media Forwarder"
APP_VERSION = "0.1.0"

HISTORICO = "historico.txt"
CONFIG = "config.json"
SESSION = "sessao"
LOGO_FILE = "logo.png"

UPDATE_URL = "https://raw.githubusercontent.com/sleepy907/telegram-media-forwarder/main/update.json"
CHANGELOG_URL = "https://raw.githubusercontent.com/sleepy907/telegram-media-forwarder/main/CHANGELOG.md"
LATEST_VERSION_PLACEHOLDER = "0.1.0"

THEMES = {
    "dark": {
        "BG": "#0f1117",
        "BG2": "#151821",
        "BG3": "#1b2030",
        "BG4": "#242a3a",
        "CARD": "#151821",
        "CARD2": "#1a1f2c",
        "BORDER": "#2a3042",
        "BORDER2": "#4f46e5",
        "TEXT": "#f4f5f7",
        "SUBTEXT": "#a7adbb",
        "MUTED": "#747b8c",
        "ACCENT": "#6d5dfc",
        "ACCENT2": "#7c6dff",
        "ACCENT3": "#9b8cff",
        "GREEN": "#3ddc84",
        "YELLOW": "#f5c542",
        "RED": "#f06f85",
        "BLUE": "#5bbcff",
        "ENTRY": "#10131c",
        "LOG_BG": "#0c0f16"
    },
    "light": {
        "BG": "#f7f5ff",
        "BG2": "#ffffff",
        "BG3": "#f1edff",
        "BG4": "#e8ddff",
        "CARD": "#ffffff",
        "CARD2": "#fbfaff",
        "BORDER": "#ded6f7",
        "BORDER2": "#8b5cf6",
        "TEXT": "#1f1833",
        "SUBTEXT": "#625777",
        "MUTED": "#8a7ca3",
        "ACCENT": "#7c3aed",
        "ACCENT2": "#8b5cf6",
        "ACCENT3": "#a855f7",
        "GREEN": "#16a34a",
        "YELLOW": "#d97706",
        "RED": "#e11d48",
        "BLUE": "#0284c7",
        "ENTRY": "#ffffff",
        "LOG_BG": "#ffffff"
    }
}


FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SUB = ("Segoe UI", 9)
FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_S = ("Segoe UI", 9)
FONT_SECTION = ("Segoe UI", 9, "bold")
FONT_BTN = ("Segoe UI", 12, "bold")
MONO = ("Courier New", 9)


def resource_dir():
    return os.path.dirname(os.path.abspath(__file__))


def resource_path(filename):
    return os.path.join(resource_dir(), filename)


def app_dir():
    base = os.environ.get("XDG_DATA_HOME")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")

    path = os.path.join(base, "telegram-media-forwarder")
    os.makedirs(path, exist_ok=True)
    return path


def app_path(filename):
    return os.path.join(app_dir(), filename)


def salvar_config(data):
    """Salva somente dados não sensíveis.

    O API Hash não é salvo por segurança.
    """
    with open(app_path(CONFIG), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def carregar_config():
    path = app_path(CONFIG)
    if not os.path.exists(path):
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def carregar_historico():
    path = app_path(HISTORICO)
    if not os.path.exists(path):
        return set()

    historico = set()
    with open(path, "r", encoding="utf-8") as f:
        for linha in f:
            item = linha.strip()
            if item:
                historico.add(item)

    return historico


def montar_chave_historico(grupo_id, msg_id):
    return f"{grupo_id}:{msg_id}"


def salvar_id(grupo_id, msg_id):
    with open(app_path(HISTORICO), "a", encoding="utf-8") as f:
        f.write(f"{montar_chave_historico(grupo_id, msg_id)}\n")


def limpar_historico():
    with open(app_path(HISTORICO), "w", encoding="utf-8") as f:
        f.write("")


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


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.theme_name = "dark"
        self.colors = THEMES[self.theme_name]

        self.title(APP_NAME)
        self.geometry("1100x720")
        self.minsize(780, 560)
        self.configure(bg=self.colors["BG"])

        self._paused = False
        self._stopped = False
        self._running = False
        self._start_time = None

        self.sent_count = 0
        self.skip_count = 0
        self.already_saved_count = 0
        self.ignored_count = 0
        self.error_count = 0

        self.logo_img = None
        self.widgets_to_theme = []

        # Estado usado pela tela de login
        self._login_phone = ""
        self._login_phone_code_hash = None

        # Estado usado pela janela de atualizações
        self._latest_release_url = ""
        self._latest_changelog = ""

        # Variáveis
        self.api_id_var = tk.StringVar()
        self.api_hash_var = tk.StringVar()
        self.save_api_hash_var = tk.BooleanVar(value=False)
        self.group_var = tk.StringVar()
        self.dest_var = tk.StringVar(value="me")
        self.filter_var = tk.StringVar()

        self.delay_var = tk.StringVar(value="1.0")
        self.limit_var = tk.StringVar(value="500")
        self.batch_var = tk.StringVar(value="30")
        self.pause_var = tk.StringVar(value="30")

        cfg = carregar_config()
        self.api_id_var.set(cfg.get("api_id", ""))

        save_api_hash = bool(cfg.get("save_api_hash", False))
        self.save_api_hash_var.set(save_api_hash)
        self.api_hash_var.set(cfg.get("api_hash", "") if save_api_hash else "")

        self.group_var.set(cfg.get("group", ""))
        self.dest_var.set(cfg.get("dest", "me"))
        self.filter_var.set(cfg.get("filter", ""))
        self.delay_var.set(cfg.get("delay", "1.0"))
        self.limit_var.set(cfg.get("limit", "500"))
        self.batch_var.set(cfg.get("batch", "30"))
        self.pause_var.set(cfg.get("pause", "30"))
        self.theme_name = cfg.get("theme", "dark") if cfg.get("theme", "dark") in THEMES else "dark"
        self.colors = THEMES[self.theme_name]

        self._setup_style()
        self._build_ui()
        self._register_stats_variable_traces()
        self._apply_theme()
        self._update_stats()
        self._log("Sistema iniciado.", "info")
        self._log("Pronto para iniciar.", "ok")

    # ────────────────────────────────────────────────────────────
    # UI base
    # ────────────────────────────────────────────────────────────
    def _setup_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("default")
        self._style_progress()

    def _style_progress(self):
        c = self.colors
        self.style.configure(
            "Purple.Horizontal.TProgressbar",
            troughcolor=c["BG4"],
            background=c["ACCENT"],
            darkcolor=c["ACCENT"],
            lightcolor=c["ACCENT3"],
            bordercolor=c["BG4"],
            thickness=8
        )

    def _build_ui(self):
        # Interface original, mas dentro de uma área com scroll vertical.
        # Assim o layout permanece igual e o conteúdo não fica cortado em telas menores.
        self.shell = tk.Frame(self, bg=self.colors["BG"])
        self.shell.pack(fill="both", expand=True)
        self.widgets_to_theme.append((self.shell, "BG"))

        self.canvas = tk.Canvas(
            self.shell,
            bg=self.colors["BG"],
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        self.widgets_to_theme.append((self.canvas, "BG"))

        self.v_scroll = ttk.Scrollbar(self.shell, orient="vertical", command=self.canvas.yview)
        self.v_scroll.pack(side="right", fill="y")
        self._v_scroll_visible = True
        self.canvas.configure(yscrollcommand=self.v_scroll.set)

        self.root = tk.Frame(self.canvas, bg=self.colors["BG"])
        self.widgets_to_theme.append((self.root, "BG"))

        self.canvas_window = self.canvas.create_window((0, 0), window=self.root, anchor="nw")

        self.root.bind("<Configure>", self._on_scroll_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel no Linux/Fedora e Windows
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)

        self.content = tk.Frame(self.root, bg=self.colors["BG"])
        self.content.pack(fill="both", expand=True, padx=16, pady=16)
        self.widgets_to_theme.append((self.content, "BG"))

        self._build_header()
        self._build_action_bar()
        self._build_main_area()
        self._build_footer()

    def _on_scroll_frame_configure(self, event=None):
        try:
            self._update_scrollbar_visibility()
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
            self.after_idle(self._update_scrollbar_visibility)
        except Exception:
            pass

    def _content_overflows_canvas(self):
        """Retorna True somente quando o conteúdo ultrapassa a altura visível."""
        try:
            bbox = self.canvas.bbox("all")
            if not bbox:
                return False

            content_height = bbox[3] - bbox[1]
            canvas_height = self.canvas.winfo_height()

            return content_height > canvas_height + 2
        except Exception:
            return True

    def _update_scrollbar_visibility(self):
        """Mostra o scroll apenas quando ele é realmente necessário."""
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

            if self._content_overflows_canvas():
                if not getattr(self, "_v_scroll_visible", True):
                    self.v_scroll.pack(side="right", fill="y")
                    self._v_scroll_visible = True
            else:
                self.canvas.yview_moveto(0)
                if getattr(self, "_v_scroll_visible", True):
                    self.v_scroll.pack_forget()
                    self._v_scroll_visible = False
        except Exception:
            pass

    def _scroll_event_from_main_window(self, event):
        """Evita que o scroll da tela principal seja acionado por janelas secundárias."""
        try:
            return event.widget.winfo_toplevel() == self
        except Exception:
            return True

    def _on_mousewheel(self, event):
        try:
            if not self._scroll_event_from_main_window(event):
                return None

            if not self._content_overflows_canvas():
                self.canvas.yview_moveto(0)
                return "break"

            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            return "break"
        except Exception:
            pass

    def _on_mousewheel_linux(self, event):
        try:
            if not self._scroll_event_from_main_window(event):
                return None

            if not self._content_overflows_canvas():
                self.canvas.yview_moveto(0)
                return "break"

            if event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")

            return "break"
        except Exception:
            pass


    def _build_header(self):
        c = self.colors

        self.header = tk.Frame(self.content, bg=c["CARD"], highlightthickness=0, highlightbackground=c["BORDER"])
        self.header.pack(fill="x", pady=(0, 8))
        self.widgets_to_theme.append((self.header, "CARD", "BORDER"))

        header_inner = tk.Frame(self.header, bg=c["CARD"])
        header_inner.pack(fill="x", padx=18, pady=10)
        self.widgets_to_theme.append((header_inner, "CARD"))

        logo_wrap = tk.Frame(header_inner, bg=c["CARD"])
        logo_wrap.pack(side="left", padx=(0, 14))
        self.widgets_to_theme.append((logo_wrap, "CARD"))

        self.logo_label = tk.Label(logo_wrap, bg=c["CARD"])
        self.logo_label.pack()
        self.widgets_to_theme.append((self.logo_label, "CARD"))
        self._load_logo()

        title_wrap = tk.Frame(header_inner, bg=c["CARD"])
        title_wrap.pack(side="left", fill="x", expand=True)
        self.widgets_to_theme.append((title_wrap, "CARD"))

        self.title_lbl = tk.Label(
            title_wrap,
            text="Telegram Media Forwarder",
            font=("Segoe UI", 16, "bold"),
            fg=c["TEXT"],
            bg=c["CARD"]
        )
        self.title_lbl.pack(anchor="w")
        self.widgets_to_theme.append((self.title_lbl, "CARD", None, "TEXT"))

        self.subtitle_lbl = tk.Label(
            title_wrap,
            text="Automatize o encaminhamento de mídias entre grupos e canais do Telegram.",
            font=FONT_SUB,
            fg=c["SUBTEXT"],
            bg=c["CARD"]
        )
        self.subtitle_lbl.pack(anchor="w", pady=(3, 0))
        self.widgets_to_theme.append((self.subtitle_lbl, "CARD", None, "SUBTEXT"))

        right = tk.Frame(header_inner, bg=c["CARD"])
        right.pack(side="right")
        self.widgets_to_theme.append((right, "CARD"))

        self.status_card = tk.Frame(right, bg=c["BG2"], highlightthickness=0, highlightbackground=c["BORDER"])
        self.status_card.pack(side="left", padx=(0, 10))
        self.widgets_to_theme.append((self.status_card, "BG2", "BORDER"))

        status_inner = tk.Frame(self.status_card, bg=c["BG2"])
        status_inner.pack(padx=16, pady=8)
        self.widgets_to_theme.append((status_inner, "BG2"))

        self.status_dot = tk.Label(status_inner, text="●", font=("Segoe UI", 11), fg=c["GREEN"], bg=c["BG2"])
        self.status_dot.pack(side="left", padx=(0, 8))
        self.widgets_to_theme.append((self.status_dot, "BG2", None, "GREEN"))

        status_texts = tk.Frame(status_inner, bg=c["BG2"])
        status_texts.pack(side="left")
        self.widgets_to_theme.append((status_texts, "BG2"))

        self.status_small = tk.Label(status_texts, text="Status", font=("Segoe UI", 8), fg=c["MUTED"], bg=c["BG2"])
        self.status_small.pack(anchor="w")
        self.widgets_to_theme.append((self.status_small, "BG2", None, "MUTED"))

        self.status_lbl = tk.Label(status_texts, text="Aguardando", font=FONT_B, fg=c["GREEN"], bg=c["BG2"])
        self.status_lbl.pack(anchor="w")
        self.widgets_to_theme.append((self.status_lbl, "BG2", None, "GREEN"))

        self.theme_btn = self._small_btn(right, "☀" if self.theme_name == "dark" else "☾", self._toggle_theme)
        self.theme_btn.pack(side="left", padx=4)

        self.update_btn = self._small_btn(right, "↻", self._open_update_window)
        self.update_btn.pack(side="left", padx=4)

        self.help_btn = self._small_btn(right, "?", self._open_help_window)
        self.help_btn.pack(side="left", padx=4)

    def _build_action_bar(self):
        c = self.colors

        self.action_panel = tk.Frame(self.content, bg=c["CARD"], highlightthickness=0, highlightbackground=c["BORDER"])
        self.action_panel.pack(fill="x", pady=(0, 8))
        self.widgets_to_theme.append((self.action_panel, "CARD", "BORDER"))

        self.btn_row = tk.Frame(self.action_panel, bg=c["CARD"])
        self.btn_row.pack(anchor="center", pady=10)
        self.widgets_to_theme.append((self.btn_row, "CARD"))

        self.btn_start = self._action_btn(self.btn_row, "▶  Iniciar", self._start, active=True)
        self.btn_start.pack(side="left", padx=10)

        self.btn_pause = self._action_btn(self.btn_row, "⏸  Pausar", self._toggle_pause)
        self.btn_pause.config(state="disabled")
        self.btn_pause.pack(side="left", padx=10)

        self.btn_stop = self._action_btn(self.btn_row, "■  Parar", self._stop, danger=True)
        self.btn_stop.config(state="disabled")
        self.btn_stop.pack(side="left", padx=10)

    def _build_main_area(self):
        c = self.colors
        self.main = tk.Frame(self.content, bg=c["BG"])
        self.main.pack(fill="both", expand=True)
        self.widgets_to_theme.append((self.main, "BG"))

        self.left_col = tk.Frame(self.main, bg=c["BG"])
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.widgets_to_theme.append((self.left_col, "BG"))

        self.right_col = tk.Frame(self.main, bg=c["BG"], width=380)
        self.right_col.pack(side="right", fill="both")
        self.right_col.pack_propagate(False)
        self.widgets_to_theme.append((self.right_col, "BG"))

        self._build_credentials_card()
        self._build_config_card()
        self._build_stats_card()
        self._build_log_card()

    def _build_credentials_card(self):
        c = self.colors
        card = self._card(self.left_col)
        card.pack(fill="x", pady=(0, 10))

        self._section_title(card, "🔐  CREDENCIAIS")

        grid = tk.Frame(card, bg=c["CARD"])
        grid.pack(fill="x", padx=16, pady=(0, 8))
        self.widgets_to_theme.append((grid, "CARD"))

        self._field(grid, "API ID", self.api_id_var, row=0, col=0)
        self._field(grid, "API Hash", self.api_hash_var, row=0, col=1, show="●")

        test = self._outline_btn(grid, "🔗  Testar campos", self._test_fields)
        test.grid(row=1, column=0, sticky="ew", pady=(10, 0), padx=(0, 6))

        login_btn = self._outline_btn(grid, "🔑  Login Telegram", self._open_login_window)
        login_btn.grid(row=1, column=1, sticky="ew", pady=(10, 0), padx=(6, 0))

        self.save_hash_check = tk.Checkbutton(
            grid,
            text="Salvar API Hash neste computador",
            variable=self.save_api_hash_var,
            command=self._save_current_config,
            bg=c["CARD"],
            fg=c["SUBTEXT"],
            activebackground=c["CARD"],
            activeforeground=c["TEXT"],
            selectcolor=c["CARD2"],
            font=FONT_S,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.save_hash_check.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 0), padx=(0, 6))
        self.widgets_to_theme.append((self.save_hash_check, "CARD", None, "SUBTEXT"))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        warning = tk.Label(
            card,
            text="⚠ Use apenas com mídias próprias, autorizadas ou para backup pessoal.",
            bg=c["CARD"],
            fg=c["YELLOW"],
            font=FONT_S
        )
        warning.pack(anchor="w", padx=16, pady=(0, 8))
        self.widgets_to_theme.append((warning, "CARD", None, "YELLOW"))

    def _build_config_card(self):
        c = self.colors
        card = self._card(self.left_col)
        card.pack(fill="x", pady=(0, 10))

        self._section_title(card, "⚙  CONFIGURAÇÕES")

        grid = tk.Frame(card, bg=c["CARD"])
        grid.pack(fill="x", padx=16, pady=(0, 8))
        self.widgets_to_theme.append((grid, "CARD"))

        self._field(grid, "Origem (Grupo)", self.group_var, row=0, col=0, width=28)
        self._field(grid, "Destino", self.dest_var, row=0, col=1, width=28)
        self._field(grid, "Filtrar origem (opcional)", self.filter_var, row=1, col=0, width=28)
        self._field(grid, "Delay (seg)", self.delay_var, row=1, col=1, width=12)
        self._field(grid, "Limite total", self.limit_var, row=2, col=0, width=12)
        self._field(grid, "Pausa a cada X", self.batch_var, row=2, col=1, width=12)
        self._field(grid, "Pausa (seg)", self.pause_var, row=3, col=0, width=12)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def _build_stats_card(self):
        c = self.colors
        card = self._card(self.left_col)
        card.pack(fill="x", pady=(0, 10))

        self._section_title(card, "📊  ESTATÍSTICAS")

        row = tk.Frame(card, bg=c["CARD"])
        row.pack(fill="x", padx=16, pady=(0, 8))
        self.widgets_to_theme.append((row, "CARD"))

        self.sent_card, self.sent_value = self._stat_box(row, "✈", "Enviadas agora", "0", "GREEN")
        self.sent_card.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.skip_card, self.skip_value = self._stat_box(row, "⏭", "Já no histórico", "0", "YELLOW")
        self.skip_card.pack(side="left", fill="x", expand=True, padx=8)

        self.err_card, self.err_value = self._stat_box(row, "⚠", "Erros", "0", "RED")
        self.err_card.pack(side="left", fill="x", expand=True, padx=(8, 0))

        bottom = tk.Frame(card, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        bottom.pack(fill="x", padx=16, pady=(0, 10))
        self.widgets_to_theme.append((bottom, "CARD2", "BORDER"))

        stats_line = tk.Frame(bottom, bg=c["CARD2"])
        stats_line.pack(fill="x", padx=12, pady=10)
        self.widgets_to_theme.append((stats_line, "CARD2"))

        self.elapsed_lbl = tk.Label(
            stats_line,
            text="⏱ Tempo decorrido: 00:00:00",
            bg=c["CARD2"],
            fg=c["SUBTEXT"],
            font=FONT_S
        )
        self.elapsed_lbl.grid(row=0, column=0, sticky="w")
        self.widgets_to_theme.append((self.elapsed_lbl, "CARD2", None, "SUBTEXT"))

        self.total_lbl = tk.Label(
            stats_line,
            text="🗂 Total processado: 0",
            bg=c["CARD2"],
            fg=c["TEXT"],
            font=FONT_B
        )
        self.total_lbl.grid(row=0, column=1, sticky="n")
        self.widgets_to_theme.append((self.total_lbl, "CARD2", None, "TEXT"))

        self.remaining_lbl = tk.Label(
            stats_line,
            text="⌛ Tempo restante: --",
            bg=c["CARD2"],
            fg=c["SUBTEXT"],
            font=FONT_S
        )
        self.remaining_lbl.grid(row=0, column=2, sticky="e")
        self.widgets_to_theme.append((self.remaining_lbl, "CARD2", None, "SUBTEXT"))

        stats_line.columnconfigure(0, weight=1)
        stats_line.columnconfigure(1, weight=1)
        stats_line.columnconfigure(2, weight=1)

        self.progress = ttk.Progressbar(card, style="Purple.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", padx=16, pady=(0, 8))

        history_row = tk.Frame(card, bg=c["CARD"])
        history_row.pack(fill="x", padx=16, pady=(0, 10))
        self.widgets_to_theme.append((history_row, "CARD"))

        import_btn = self._outline_btn(history_row, "📥  Importar histórico", self._import_history)
        import_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        export_btn = self._outline_btn(history_row, "📤  Exportar histórico", self._export_history)
        export_btn.pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _build_log_card(self):
        c = self.colors

        card = self._card(self.right_col)
        card.pack(fill="both", expand=True)

        top = tk.Frame(card, bg=c["CARD"])
        top.pack(fill="x", padx=16, pady=(14, 8))
        self.widgets_to_theme.append((top, "CARD"))

        title = tk.Label(top, text="📄  LOG", bg=c["CARD"], fg=c["ACCENT3"], font=FONT_SECTION)
        title.pack(side="left")
        self.widgets_to_theme.append((title, "CARD", None, "ACCENT3"))

        clear = self._outline_btn(top, "🗑 Limpar", self._clear_log)
        clear.pack(side="right")

        log_frame = tk.Frame(card, bg=c["LOG_BG"], highlightthickness=1, highlightbackground=c["BORDER"])
        log_frame.pack(fill="both", expand=True, padx=16, pady=(0, 10))
        self.widgets_to_theme.append((log_frame, "LOG_BG", "BORDER"))

        self.log = scrolledtext.ScrolledText(
            log_frame,
            font=MONO,
            fg=c["TEXT"],
            bg=c["LOG_BG"],
            insertbackground=c["ACCENT3"],
            bd=0,
            state="disabled",
            wrap="word",
            padx=10,
            pady=10,
            highlightthickness=0,
            relief="flat"
        )
        self.log.pack(fill="both", expand=True)

        self.log.tag_config("ok", foreground=c["GREEN"])
        self.log.tag_config("warn", foreground=c["YELLOW"])
        self.log.tag_config("err", foreground=c["RED"])
        self.log.tag_config("info", foreground=c["ACCENT3"])
        self.log.tag_config("muted", foreground=c["SUBTEXT"])

    def _build_footer(self):
        c = self.colors

        self.footer = tk.Frame(self.content, bg=c["BG"])
        self.footer.pack(fill="x", pady=(6, 0))
        self.widgets_to_theme.append((self.footer, "BG"))

        self.footer_left = tk.Label(
            self.footer,
            text=f"↻  Versão {APP_VERSION}",
            bg=c["BG"],
            fg=c["SUBTEXT"],
            font=FONT_S
        )
        self.footer_left.pack(side="left")
        self.widgets_to_theme.append((self.footer_left, "BG", None, "SUBTEXT"))

    # ────────────────────────────────────────────────────────────
    # Componentes visuais
    # ────────────────────────────────────────────────────────────
    def _card(self, parent):
        c = self.colors
        f = tk.Frame(parent, bg=c["CARD"], highlightthickness=0, highlightbackground=c["BORDER"])
        self.widgets_to_theme.append((f, "CARD", "BORDER"))
        return f

    def _section_title(self, parent, text):
        c = self.colors
        lbl = tk.Label(parent, text=text, bg=c["CARD"], fg=c["ACCENT3"], font=FONT_SECTION)
        lbl.pack(anchor="w", padx=16, pady=(10, 6))
        self.widgets_to_theme.append((lbl, "CARD", None, "ACCENT3"))
        return lbl

    def _field(self, parent, text, var, row, col, width=22, show=""):
        c = self.colors

        box = tk.Frame(parent, bg=c["CARD"])
        box.grid(row=row, column=col, sticky="ew", padx=6, pady=6)
        self.widgets_to_theme.append((box, "CARD"))

        lbl = tk.Label(box, text=text, bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        lbl.pack(anchor="w", pady=(0, 4))
        self.widgets_to_theme.append((lbl, "CARD", None, "TEXT"))

        ent = tk.Entry(
            box,
            textvariable=var,
            show=show,
            width=width,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            relief="flat",
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        ent.pack(fill="x", ipady=7)
        self._register_entry_behavior(ent)
        self.widgets_to_theme.append((ent, "ENTRY", "BORDER", "TEXT"))

        return ent

    def _register_entry_behavior(self, entry):
        """Melhora a experiência de colagem nos campos de entrada.

        Quando o usuário cola um novo valor em um campo que já possui texto,
        o conteúdo antigo é substituído automaticamente, evitando textos
        duplicados ou misturados.
        """
        try:
            entry.bind("<Control-v>", self._paste_replace_entry)
            entry.bind("<Control-V>", self._paste_replace_entry)
            entry.bind("<Command-v>", self._paste_replace_entry)
            entry.bind("<Command-V>", self._paste_replace_entry)
        except Exception:
            pass

    def _paste_replace_entry(self, event):
        """Substitui o conteúdo do campo ao colar, mantendo seleção manual se existir."""
        try:
            widget = event.widget
            clipboard_text = self.clipboard_get()
        except Exception:
            return "break"

        try:
            # Se houver seleção, substitui apenas a seleção.
            try:
                start = widget.index("sel.first")
                end = widget.index("sel.last")
                widget.delete(start, end)
                widget.insert(start, clipboard_text)
            except tk.TclError:
                # Se não houver seleção, substitui o campo inteiro.
                widget.delete(0, "end")
                widget.insert(0, clipboard_text)

            return "break"
        except Exception:
            return "break"

    def _small_btn(self, parent, text, cmd):
        c = self.colors
        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=c["BG2"],
            fg=c["TEXT"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            width=3,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=c["BORDER"]
        )
        self.widgets_to_theme.append((btn, "BG2", "BORDER", "TEXT"))
        return btn

    def _action_btn(self, parent, text, cmd, active=False, danger=False):
        c = self.colors
        bg = c["ACCENT"] if active else c["BG3"]
        fg = "#ffffff" if active else c["TEXT"]
        border = c["RED"] if danger else c["BORDER2"]

        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=bg,
            fg=fg,
            activebackground=c["ACCENT2"],
            activeforeground="#ffffff",
            font=FONT_BTN,
            width=14,
            height=1,
            bd=0,
            relief="flat",
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=border
        )
        btn._theme_bg_key = "ACCENT" if active else "BG3"
        btn._theme_fg_key = None if active else "TEXT"
        btn._theme_border_key = "RED" if danger else "BORDER2"
        self.widgets_to_theme.append((btn, btn._theme_bg_key, btn._theme_border_key, btn._theme_fg_key))
        return btn

    def _outline_btn(self, parent, text, cmd):
        c = self.colors
        btn = tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=c["CARD2"],
            fg=c["ACCENT3"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=7,
            highlightthickness=1,
            highlightbackground=c["BORDER2"]
        )
        self.widgets_to_theme.append((btn, "CARD2", "BORDER2", "ACCENT3"))
        return btn

    def _stat_box(self, parent, icon, title, value, color_key):
        c = self.colors

        f = tk.Frame(parent, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        self.widgets_to_theme.append((f, "CARD2", "BORDER"))

        icon_lbl = tk.Label(f, text=icon, bg=c["CARD2"], fg=c[color_key], font=("Segoe UI", 20))
        icon_lbl.pack(side="left", padx=12, pady=12)
        self.widgets_to_theme.append((icon_lbl, "CARD2", None, color_key))

        txt = tk.Frame(f, bg=c["CARD2"])
        txt.pack(side="left", fill="both", expand=True, pady=10)
        self.widgets_to_theme.append((txt, "CARD2"))

        title_lbl = tk.Label(txt, text=title, bg=c["CARD2"], fg=c["SUBTEXT"], font=FONT_S)
        title_lbl.pack(anchor="w")
        self.widgets_to_theme.append((title_lbl, "CARD2", None, "SUBTEXT"))

        val_lbl = tk.Label(txt, text=value, bg=c["CARD2"], fg=c["TEXT"], font=("Segoe UI", 18, "bold"))
        val_lbl.pack(anchor="w")
        self.widgets_to_theme.append((val_lbl, "CARD2", None, "TEXT"))

        return f, val_lbl

    def _load_logo(self):
        logo_path = resource_path(LOGO_FILE)

        if not os.path.exists(logo_path):
            self.logo_label.config(text="✈", font=("Segoe UI", 42), fg=self.colors["ACCENT3"])
            return

        try:
            img = tk.PhotoImage(file=logo_path)

            # Reduz a imagem mantendo-a leve no cabeçalho.
            # A imagem original é grande; subsample reduz sem depender de Pillow.
            w = img.width()
            factor = max(1, w // 82)
            img = img.subsample(factor, factor)

            self.logo_img = img
            self.logo_label.config(image=self.logo_img)
        except Exception:
            self.logo_label.config(text="✈", font=("Segoe UI", 42), fg=self.colors["ACCENT3"])

    # ────────────────────────────────────────────────────────────
    # Tema
    # ────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.colors = THEMES[self.theme_name]
        self.theme_btn.config(text="☀" if self.theme_name == "dark" else "☾")
        self._apply_theme()
        self._save_current_config()
        self._log(f"Tema alterado para: {'Claro' if self.theme_name == 'light' else 'Escuro'}.", "info")

    def _apply_theme(self):
        c = self.colors
        self.configure(bg=c["BG"])
        self._style_progress()

        for item in self.widgets_to_theme:
            widget = item[0]
            bg_key = item[1] if len(item) > 1 else None
            border_key = item[2] if len(item) > 2 else None
            fg_key = item[3] if len(item) > 3 else None

            try:
                if bg_key:
                    widget.config(bg=c[bg_key])
                if fg_key:
                    widget.config(fg=c[fg_key])
                if border_key:
                    widget.config(highlightbackground=c[border_key])
            except Exception:
                pass

        try:
            self.log.config(bg=c["LOG_BG"], fg=c["TEXT"], insertbackground=c["ACCENT3"])
            self.log.tag_config("ok", foreground=c["GREEN"])
            self.log.tag_config("warn", foreground=c["YELLOW"])
            self.log.tag_config("err", foreground=c["RED"])
            self.log.tag_config("info", foreground=c["ACCENT3"])
            self.log.tag_config("muted", foreground=c["SUBTEXT"])
        except Exception:
            pass

        self._set_status(self.status_lbl.cget("text"), self.status_lbl.cget("fg"))

    # ────────────────────────────────────────────────────────────
    # Ações e utilidades
    # ────────────────────────────────────────────────────────────
    def _save_current_config(self):
        data = {
            "api_id": self.api_id_var.get().strip(),
            "group": self.group_var.get().strip(),
            "dest": self.dest_var.get().strip(),
            "filter": self.filter_var.get().strip(),
            "delay": self.delay_var.get().strip(),
            "limit": self.limit_var.get().strip(),
            "batch": self.batch_var.get().strip(),
            "pause": self.pause_var.get().strip(),
            "theme": self.theme_name,
            "save_api_hash": bool(self.save_api_hash_var.get())
        }

        if self.save_api_hash_var.get():
            data["api_hash"] = self.api_hash_var.get().strip()

        salvar_config(data)

    def _clear_log(self):
        self.log.config(state="normal")
        self.log.delete("1.0", "end")
        self.log.config(state="disabled")
        self._log("Log limpo.", "info")

    def _open_login_window(self):
        c = self.colors

        win = tk.Toplevel(self)
        win.title("Login Telegram")
        win.geometry("560x520")
        win.minsize(520, 480)
        win.configure(bg=c["BG"])
        win.transient(self)

        container = tk.Frame(win, bg=c["BG"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(
            container,
            bg=c["CARD"],
            highlightthickness=1,
            highlightbackground=c["BORDER"]
        )
        card.pack(fill="both", expand=True)

        title = tk.Label(
            card,
            text="🔑 Login no Telegram",
            bg=c["CARD"],
            fg=c["ACCENT3"],
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=16, pady=(14, 6))

        desc = tk.Label(
            card,
            text=(
                "Use esta tela para gerar a sessão do Telegram sem precisar abrir o terminal."
                "Primeiro informe seu telefone com DDD, depois digite o código recebido no Telegram."
            ),
            bg=c["CARD"],
            fg=c["SUBTEXT"],
            font=FONT_S,
            justify="left",
            wraplength=500
        )
        desc.pack(anchor="w", padx=16, pady=(0, 12))

        form = tk.Frame(card, bg=c["CARD"])
        form.pack(fill="x", padx=16, pady=(0, 12))

        api_lbl = tk.Label(form, text="API ID", bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        api_lbl.grid(row=0, column=0, sticky="w", pady=(0, 4))
        api_entry = tk.Entry(
            form,
            textvariable=self.api_id_var,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        api_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), ipady=7)
        self._register_entry_behavior(api_entry)

        hash_lbl = tk.Label(form, text="API Hash", bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        hash_lbl.grid(row=0, column=1, sticky="w", pady=(0, 4))
        hash_entry = tk.Entry(
            form,
            textvariable=self.api_hash_var,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            show="●",
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        hash_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), ipady=7)
        self._register_entry_behavior(hash_entry)

        phone_var = tk.StringVar(value=self._login_phone)
        code_var = tk.StringVar()
        password_var = tk.StringVar()

        phone_lbl = tk.Label(form, text="Telefone com DDD", bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        phone_lbl.grid(row=2, column=0, sticky="w", pady=(12, 4))
        phone_entry = tk.Entry(
            form,
            textvariable=phone_var,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        phone_entry.grid(row=3, column=0, sticky="ew", padx=(0, 8), ipady=7)
        self._register_entry_behavior(phone_entry)
        phone_entry.insert(0, "")

        code_lbl = tk.Label(form, text="Código recebido", bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        code_lbl.grid(row=2, column=1, sticky="w", pady=(12, 4))
        code_entry = tk.Entry(
            form,
            textvariable=code_var,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        code_entry.grid(row=3, column=1, sticky="ew", padx=(8, 0), ipady=7)
        self._register_entry_behavior(code_entry)

        pass_lbl = tk.Label(form, text="Senha 2FA, se tiver", bg=c["CARD"], fg=c["TEXT"], font=FONT_S)
        pass_lbl.grid(row=4, column=0, columnspan=2, sticky="w", pady=(12, 4))
        pass_entry = tk.Entry(
            form,
            textvariable=password_var,
            bg=c["ENTRY"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            font=FONT,
            bd=0,
            show="●",
            highlightthickness=1,
            highlightbackground=c["BORDER"],
            highlightcolor=c["ACCENT"]
        )
        pass_entry.grid(row=5, column=0, columnspan=2, sticky="ew", ipady=7)
        self._register_entry_behavior(pass_entry)

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

        status_box = tk.Frame(card, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        status_box.pack(fill="x", padx=16, pady=(0, 12))

        status_lbl = tk.Label(
            status_box,
            text="Status: aguardando envio do código.",
            bg=c["CARD2"],
            fg=c["SUBTEXT"],
            font=FONT_S,
            justify="left",
            wraplength=500
        )
        status_lbl.pack(anchor="w", padx=12, pady=10)

        buttons = tk.Frame(card, bg=c["CARD"])
        buttons.pack(fill="x", padx=16, pady=(0, 14))

        send_btn = tk.Button(
            buttons,
            text="📨 Enviar código",
            command=lambda: self._login_send_code(
                win,
                phone_var.get().strip(),
                status_lbl,
                send_btn,
                confirm_btn
            ),
            bg=c["ACCENT"],
            fg="#ffffff",
            activebackground=c["ACCENT2"],
            activeforeground="#ffffff",
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10
        )
        send_btn.pack(side="left")

        confirm_btn = tk.Button(
            buttons,
            text="✅ Confirmar login",
            command=lambda: self._login_confirm_code(
                win,
                code_var.get().strip(),
                password_var.get().strip(),
                status_lbl,
                confirm_btn
            ),
            bg=c["CARD2"],
            fg=c["ACCENT3"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10,
            state="disabled"
        )
        confirm_btn.pack(side="left", padx=10)

        check_btn = tk.Button(
            buttons,
            text="🔍 Verificar sessão",
            command=lambda: self._login_check_session(status_lbl),
            bg=c["BG3"],
            fg=c["TEXT"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10
        )
        check_btn.pack(side="left", padx=10)

        close_btn = tk.Button(
            buttons,
            text="Fechar",
            command=win.destroy,
            bg=c["BG3"],
            fg=c["TEXT"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10
        )
        close_btn.pack(side="right")

        phone_entry.focus_set()

    def _login_set_status(self, label, text, color_key="SUBTEXT"):
        def do():
            label.config(text=text, fg=self.colors[color_key])
        self.after(0, do)

    def _login_set_button_state(self, button, state):
        def do():
            button.config(state=state)
        self.after(0, do)

    def _login_get_api_credentials(self):
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()

        if not api_id:
            raise ValueError("Preencha o API ID.")
        if not api_hash:
            raise ValueError("Preencha o API Hash.")

        try:
            api_id = int(api_id)
        except ValueError:
            raise ValueError("API ID deve ser um número inteiro.")

        return api_id, api_hash

    def _login_send_code(self, win, phone, status_lbl, send_btn, confirm_btn):
        if not phone:
            messagebox.showwarning("Telefone obrigatório", "Informe o telefone com DDD. Exemplo: +5511999999999", parent=win)
            return

        self._login_phone = phone
        self._login_set_status(status_lbl, "Status: enviando código para o Telegram...", "YELLOW")
        self._login_set_button_state(send_btn, "disabled")

        def worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self._login_send_code_async(phone))
                self._login_set_status(
                    status_lbl,
                    "Status: código enviado. Digite o código recebido no Telegram e clique em Confirmar login.",
                    "GREEN"
                )
                self._login_set_button_state(confirm_btn, "normal")
            except Exception as e:
                self._login_set_status(status_lbl, f"Status: erro ao enviar código — {e}", "RED")
                messagebox.showerror("Erro no login", str(e), parent=win)
            finally:
                self._login_set_button_state(send_btn, "normal")
                loop.close()

        threading.Thread(target=worker, daemon=True).start()

    async def _login_send_code_async(self, phone):
        api_id, api_hash = self._login_get_api_credentials()

        client = TelegramClient(app_path(SESSION), api_id, api_hash)
        await client.connect()

        try:
            if await client.is_user_authorized():
                self._login_phone_code_hash = None
                return

            sent = await client.send_code_request(phone)
            self._login_phone_code_hash = sent.phone_code_hash
            self._save_current_config()
        finally:
            await client.disconnect()

    def _login_confirm_code(self, win, code, password, status_lbl, confirm_btn):
        if not self._login_phone:
            messagebox.showwarning("Telefone ausente", "Envie o código primeiro.", parent=win)
            return

        if not code and not password:
            messagebox.showwarning("Código obrigatório", "Digite o código recebido no Telegram.", parent=win)
            return

        self._login_set_status(status_lbl, "Status: confirmando login...", "YELLOW")
        self._login_set_button_state(confirm_btn, "disabled")

        def worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self._login_confirm_code_async(code, password))
                self._login_set_status(status_lbl, "Status: login concluído. Sessão criada com sucesso.", "GREEN")
                self._log("Login do Telegram concluído. Sessão criada com sucesso.", "ok")
                messagebox.showinfo("Login concluído", "Sessão criada com sucesso. Agora você pode iniciar o encaminhamento.", parent=win)
            except SessionPasswordNeededError:
                self._login_set_status(status_lbl, "Status: sua conta possui 2FA. Digite a senha e confirme novamente.", "YELLOW")
                messagebox.showwarning("Senha 2FA necessária", "Digite sua senha 2FA no campo indicado e clique em Confirmar login.", parent=win)
            except PhoneCodeInvalidError:
                self._login_set_status(status_lbl, "Status: código inválido. Confira e tente novamente.", "RED")
                messagebox.showerror("Código inválido", "O código informado é inválido.", parent=win)
            except PasswordHashInvalidError:
                self._login_set_status(status_lbl, "Status: senha 2FA inválida.", "RED")
                messagebox.showerror("Senha inválida", "A senha 2FA informada é inválida.", parent=win)
            except Exception as e:
                self._login_set_status(status_lbl, f"Status: erro ao confirmar login — {e}", "RED")
                messagebox.showerror("Erro no login", str(e), parent=win)
            finally:
                self._login_set_button_state(confirm_btn, "normal")
                loop.close()

        threading.Thread(target=worker, daemon=True).start()

    async def _login_confirm_code_async(self, code, password):
        api_id, api_hash = self._login_get_api_credentials()

        client = TelegramClient(app_path(SESSION), api_id, api_hash)
        await client.connect()

        try:
            if await client.is_user_authorized():
                return

            if password and not code:
                await client.sign_in(password=password)
                return

            try:
                await client.sign_in(
                    phone=self._login_phone,
                    code=code,
                    phone_code_hash=self._login_phone_code_hash
                )
            except SessionPasswordNeededError:
                if password:
                    await client.sign_in(password=password)
                else:
                    raise

            self._save_current_config()
        finally:
            await client.disconnect()

    def _login_check_session(self, status_lbl):
        self._login_set_status(status_lbl, "Status: verificando sessão...", "YELLOW")

        def worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                authorized = loop.run_until_complete(self._login_check_session_async())
                if authorized:
                    self._login_set_status(status_lbl, "Status: sessão encontrada e autorizada.", "GREEN")
                    self._log("Sessão do Telegram verificada com sucesso.", "ok")
                else:
                    self._login_set_status(status_lbl, "Status: nenhuma sessão autorizada encontrada.", "YELLOW")
            except Exception as e:
                self._login_set_status(status_lbl, f"Status: erro ao verificar sessão — {e}", "RED")
            finally:
                loop.close()

        threading.Thread(target=worker, daemon=True).start()

    async def _login_check_session_async(self):
        api_id, api_hash = self._login_get_api_credentials()

        client = TelegramClient(app_path(SESSION), api_id, api_hash)
        await client.connect()

        try:
            return await client.is_user_authorized()
        finally:
            await client.disconnect()


    def _open_update_window(self):
        c = self.colors

        win = tk.Toplevel(self)
        win.title("Atualizações")
        win.geometry("560x420")
        win.resizable(False, False)
        win.configure(bg=c["BG"])
        win.transient(self)
        win.grab_set()

        container = tk.Frame(win, bg=c["BG"])
        container.pack(fill="both", expand=True, padx=18, pady=18)

        card = tk.Frame(container, bg=c["CARD"], highlightthickness=1, highlightbackground=c["BORDER"])
        card.pack(fill="both", expand=True)

        title = tk.Label(card, text="↻  Checar atualizações", bg=c["CARD"], fg=c["ACCENT3"], font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w", padx=18, pady=(12, 6))

        desc = tk.Label(
            card,
            text="Verifique se existe uma nova versão disponível do Telegram Media Forwarder.",
            bg=c["CARD"],
            fg=c["SUBTEXT"],
            font=FONT,
            justify="left",
            wraplength=500
        )
        desc.pack(anchor="w", padx=18, pady=(0, 10))

        info_box = tk.Frame(card, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        info_box.pack(fill="x", padx=18, pady=(0, 10))

        self.update_window_installed = tk.Label(info_box, text=f"Versão atual: {APP_VERSION}", bg=c["CARD2"], fg=c["TEXT"], font=FONT_B)
        self.update_window_installed.pack(anchor="w", padx=12, pady=(12, 4))

        self.update_window_latest = tk.Label(info_box, text="Última versão: não checado", bg=c["CARD2"], fg=c["SUBTEXT"], font=FONT)
        self.update_window_latest.pack(anchor="w", padx=12, pady=4)

        self.update_window_status = tk.Label(info_box, text="Status: aguardando checagem", bg=c["CARD2"], fg=c["SUBTEXT"], font=FONT)
        self.update_window_status.pack(anchor="w", padx=12, pady=(4, 12))

        btns = tk.Frame(card, bg=c["CARD"])
        btns.pack(fill="x", padx=18, pady=(0, 10))

        check_btn = tk.Button(btns, text="🔎  Checar atualização", command=lambda: self._check_update_in_window(win), bg=c["ACCENT"], fg="#ffffff", activebackground=c["ACCENT2"], activeforeground="#ffffff", font=FONT_B, bd=0, relief="flat", cursor="hand2", padx=14, pady=10)
        check_btn.pack(side="left")

        changelog_btn = tk.Button(btns, text="📄  Changelog", command=lambda: self._show_changelog_placeholder(win), bg=c["CARD2"], fg=c["ACCENT3"], activebackground=c["BG4"], activeforeground=c["TEXT"], font=FONT_B, bd=0, relief="flat", cursor="hand2", padx=14, pady=10)
        changelog_btn.pack(side="left", padx=8)

        close_btn = tk.Button(btns, text="Fechar", command=win.destroy, bg=c["BG3"], fg=c["TEXT"], activebackground=c["BG4"], activeforeground=c["TEXT"], font=FONT_B, bd=0, relief="flat", cursor="hand2", padx=14, pady=10)
        close_btn.pack(side="right")

        # O botão de release fica escondido inicialmente.
        # Ele só aparece quando uma nova versão for encontrada.
        self.release_row = tk.Frame(card, bg=c["CARD"])
        self.release_row.pack(fill="x", padx=18, pady=(0, 10))
        self.release_row.pack_forget()
        self.widgets_to_theme.append((self.release_row, "CARD"))

        self.open_release_btn = tk.Button(
            self.release_row,
            text="⬇  Abrir release oficial no GitHub",
            command=self._open_latest_release,
            bg=c["CARD2"],
            fg=c["ACCENT3"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=10
        )
        self.open_release_btn.pack(anchor="w")

        note_text = "Configure UPDATE_URL no código apontando para o update.json do GitHub."
        if UPDATE_URL:
            note_text = "A checagem usa o update.json configurado no GitHub."

        note = tk.Label(card, text=note_text, bg=c["CARD"], fg=c["MUTED"], font=FONT_S, justify="left", wraplength=500)
        note.pack(anchor="w", padx=18, pady=(0, 8))

    def _version_tuple(self, version):
        parts = []
        for piece in str(version).replace("v", "").split("."):
            try:
                parts.append(int(piece))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    def _fetch_url_text(self, url, timeout=10):
        """Baixa texto puro de uma URL."""
        req = urllib.request.Request(
            url,
            headers={"User-Agent": f"{APP_NAME}/{APP_VERSION}"}
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")

    def _fetch_update_info(self):
        """Consulta o update.json e carrega o CHANGELOG.md completo quando possível."""
        if not UPDATE_URL:
            return {
                "version": LATEST_VERSION_PLACEHOLDER,
                "release_url": "",
                "changelog": "UPDATE_URL ainda não configurado no código."
            }

        raw = self._fetch_url_text(UPDATE_URL)
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
                remote_changelog = self._fetch_url_text(changelog_url).strip()
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

    def _check_update_in_window(self, win=None):
        if hasattr(self, "update_window_status"):
            self.update_window_status.config(text="Status: checando atualização...", fg=self.colors["YELLOW"])

        if hasattr(self, "release_row"):
            self.release_row.pack_forget()

        def worker():
            try:
                info = self._fetch_update_info()
                latest = info["version"]
                current = APP_VERSION
                release_url = info.get("release_url", "")
                changelog = info.get("changelog", "")

                self._latest_release_url = release_url
                self._latest_changelog = changelog

                def do_success():
                    if hasattr(self, "update_window_latest"):
                        self.update_window_latest.config(text=f"Última versão: {latest}")

                    if self._version_tuple(latest) > self._version_tuple(current):
                        if hasattr(self, "update_window_status"):
                            self.update_window_status.config(text="Status: atualização disponível", fg=self.colors["YELLOW"])

                        if hasattr(self, "release_row") and release_url:
                            self.release_row.pack(fill="x", padx=18, pady=(0, 10))

                        messagebox.showinfo("Atualização disponível", f"Existe uma nova versão disponível: {latest}\n\nVersão atual: {current}", parent=win)
                    else:
                        if hasattr(self, "update_window_status"):
                            self.update_window_status.config(text="Status: você está usando a versão mais recente", fg=self.colors["GREEN"])

                        if hasattr(self, "release_row"):
                            self.release_row.pack_forget()

                        messagebox.showinfo("Sem atualizações", f"Você já está usando a versão mais recente.\n\nVersão atual: {current}", parent=win)

                self.after(0, do_success)

            except Exception as e:
                error_detail = str(e)

                def do_error():
                    if hasattr(self, "update_window_latest"):
                        self.update_window_latest.config(text="Última versão: erro ao checar")

                    if hasattr(self, "update_window_status"):
                        self.update_window_status.config(text="Status: erro ao checar atualização", fg=self.colors["RED"])

                    messagebox.showerror(
                        "Erro ao checar atualização",
                        f"Não foi possível consultar atualizações.\n\nDetalhe: {error_detail}",
                        parent=win
                    )

                self.after(0, do_error)

        threading.Thread(target=worker, daemon=True).start()

    def _open_latest_release(self):
        if not self._latest_release_url:
            messagebox.showwarning("Release não disponível", "Nenhum link de release foi carregado ainda.")
            return

        webbrowser.open(self._latest_release_url)

    def _show_changelog_placeholder(self, parent=None):
        win = tk.Toplevel(parent if parent else self)
        win.title("Changelog")
        win.geometry("720x620")
        win.minsize(620, 500)
        win.configure(bg=self.colors["BG"])
        win.transient(parent if parent else self)
        win.lift(parent if parent else self)
        win.focus_force()
        win.grab_set()

        def fechar_changelog():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", fechar_changelog)

        container = tk.Frame(win, bg=self.colors["BG"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(
            container,
            bg=self.colors["CARD"],
            highlightthickness=1,
            highlightbackground=self.colors["BORDER"]
        )
        card.pack(fill="both", expand=True)

        changelog_title_version = "v0.1.0"
        if self._latest_changelog:
            try:
                latest_text = self.update_window_latest.cget("text")
                if ":" in latest_text:
                    changelog_title_version = latest_text.split(":", 1)[1].strip()
            except Exception:
                pass

        title = tk.Label(
            card,
            text=f"📋 Changelog — Telegram Media Forwarder {changelog_title_version}",
            bg=self.colors["CARD"],
            fg=self.colors["ACCENT3"],
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=16, pady=(14, 8))

        text_frame = tk.Frame(
            card,
            bg=self.colors["LOG_BG"],
            highlightthickness=1,
            highlightbackground=self.colors["BORDER"]
        )
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        changelog_box = tk.Text(
            text_frame,
            font=("Segoe UI", 10),
            bg=self.colors["LOG_BG"],
            fg=self.colors["TEXT"],
            insertbackground=self.colors["ACCENT3"],
            bd=0,
            wrap="word",
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set
        )
        changelog_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=changelog_box.yview)

        changelog = """Changelog — Telegram Media Forwarder v0.1.0

ADICIONADO
• Sistema real de atualização via update.json.
• Botão para abrir a release oficial no GitHub quando houver nova versão disponível.
• Importação de histórico antigo.
• Exportação de histórico atual para backup ou migração.
• Tela de Ajuda dentro do aplicativo.
• Botão Sobre o APP dentro da tela de Ajuda.
• Opção para salvar API Hash neste computador.
• Estimativa de tempo restante com base nos dados preenchidos.

MELHORADO
• Mensagens do log mais claras para o usuário.
• Log mostra nome da origem conectada.
• Log mostra destino configurado.
• Log informa início, pausa, retomada, parada e finalização.
• Estatísticas mais claras, com enviadas agora, já no histórico, erros, total processado, tempo decorrido e tempo restante.
• Área de estatísticas com informações melhor alinhadas.
• Janela de Atualizações mais limpa, exibindo release apenas quando houver atualização.
• Tela de Ajuda com informações sobre API ID, API Hash, login, histórico, sessão e segurança.
• API Hash continua sem ser salvo por padrão, mas agora pode ser salvo se o usuário permitir.

CORRIGIDO
• Scroll desnecessário em tela cheia.
• Changelog abrindo atrás da janela de Atualizações.
• Changelog não fechando corretamente.
• Scroll do Changelog interferindo no scroll da tela principal.
• Colagem de texto nos campos.
• Figurinhas/Stickers sendo encaminhados indevidamente.
• Ordem de processamento alterada para ir da mídia mais antiga para a mais recente.

SEGURANÇA
• Dados pessoais continuam fora do instalador e do executável.
• Sessão, histórico e configurações permanecem armazenados localmente.
• API Hash só é salvo no config.json se a opção correspondente estiver marcada.
"""

        if self._latest_changelog:
            changelog = self._latest_changelog
        else:
            try:
                if CHANGELOG_URL:
                    remote_changelog = self._fetch_url_text(CHANGELOG_URL).strip()
                    if remote_changelog:
                        changelog = remote_changelog
            except Exception as e:
                changelog = (
                    f"{changelog}\n\n"
                    f"Aviso: não foi possível carregar o CHANGELOG.md do GitHub.\n"
                    f"Detalhe técnico: {e}"
                )

        changelog_box.insert("1.0", changelog)
        changelog_box.config(state="disabled")

        close_btn = tk.Button(
            card,
            text="Fechar",
            command=fechar_changelog,
            bg=self.colors["BG3"],
            fg=self.colors["TEXT"],
            activebackground=self.colors["BG4"],
            activeforeground=self.colors["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8
        )
        close_btn.pack(anchor="e", padx=16, pady=(0, 14))

    def _open_help_window(self):
        c = self.colors

        win = tk.Toplevel(self)
        win.title("Ajuda")
        win.geometry("780x620")
        win.minsize(680, 520)
        win.configure(bg=c["BG"])
        win.transient(self)

        container = tk.Frame(win, bg=c["BG"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(
            container,
            bg=c["CARD"],
            highlightthickness=1,
            highlightbackground=c["BORDER"]
        )
        card.pack(fill="both", expand=True)

        title = tk.Label(
            card,
            text="❔ Ajuda — Telegram Media Forwarder",
            bg=c["CARD"],
            fg=c["ACCENT3"],
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=16, pady=(14, 8))

        text_frame = tk.Frame(
            card,
            bg=c["LOG_BG"],
            highlightthickness=1,
            highlightbackground=c["BORDER"]
        )
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        scrollbar = ttk.Scrollbar(text_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        help_box = tk.Text(
            text_frame,
            font=("Segoe UI", 10),
            bg=c["LOG_BG"],
            fg=c["TEXT"],
            insertbackground=c["ACCENT3"],
            bd=0,
            wrap="word",
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set
        )
        help_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=help_box.yview)

        help_text = f"""Ajuda — Telegram Media Forwarder

1. Como pegar API ID e API Hash

Para usar o Telegram Media Forwarder, você precisa de um API ID e um API Hash da sua própria conta Telegram.

Passo a passo:
• Acesse: https://my.telegram.org
• Faça login com seu número de telefone.
• Entre em "API development tools".
• Crie um app, se ainda não tiver criado.
• Copie o API ID e o API Hash.
• Cole esses dados nos campos do programa.

Importante:
• O API ID pode ser salvo pelo app.
• O API Hash é sensível.
• Por padrão, ele não é salvo automaticamente.
• Se quiser salvar o API Hash neste computador, marque a opção "Salvar API Hash neste computador".


2. Como fazer login pelo app

O botão "Login Telegram" cria a sessão da sua conta diretamente pelo programa, sem precisar usar terminal.

Passo a passo:
• Preencha API ID e API Hash.
• Clique em "Login Telegram".
• Informe seu telefone com DDD.
• Clique em "Enviar código".
• Digite o código recebido no Telegram.
• Se sua conta tiver senha 2FA, informe a senha.
• Clique em "Confirmar login".

Depois disso, o app cria o arquivo de sessão localmente.


3. Como preencher origem e destino

Origem:
• É o grupo, canal ou conversa de onde as mídias serão lidas.
• Pode ser um link, username ou identificador aceito pelo Telegram.

Destino:
• É para onde as mídias serão encaminhadas.
• Pode ser "me", grupo, canal, bot ou conversa acessível pela sua conta.


4. O que significa destino "me"

O destino "me" significa "Mensagens Salvas" do próprio Telegram.

Use "me" quando quiser encaminhar as mídias para suas Mensagens Salvas.


5. O que é sessao.session

O arquivo sessao.session guarda a autenticação local da sua conta Telegram.

Ele permite que o app conecte sem pedir login toda vez.

Atenção:
• Não compartilhe esse arquivo.
• Não envie esse arquivo para outras pessoas.
• Ele é criado e usado apenas na sua máquina.


6. O que é historico.txt

O historico.txt guarda o registro das mídias já processadas.

Ele evita que o app encaminhe a mesma mídia de novo.

Formato usado:
• grupo_id:msg_id

Também existe compatibilidade com histórico antigo baseado apenas em msg_id.


7. O que é config.json

O config.json guarda configurações simples do aplicativo, como:

• API ID
• origem
• destino
• filtro
• delay
• limite
• pausa
• tema
• opção de salvar API Hash

Por segurança, o API Hash só é salvo se a opção "Salvar API Hash neste computador" estiver marcada.


8. Onde ficam os arquivos pessoais do programa

Os arquivos pessoais ficam fora do instalador e fora do executável.

Pasta atual usada pelo programa:

{app_dir()}

Arquivos principais:
• sessao.session
• historico.txt
• config.json

Esses arquivos pertencem ao usuário e ficam apenas na máquina local.


9. Como importar/exportar histórico

Importar histórico:
• Use quando tiver um historico.txt antigo.
• Clique em "Importar histórico".
• Selecione o arquivo antigo.
• O app mescla os registros sem duplicar linhas.

Exportar histórico:
• Clique em "Exportar histórico".
• Escolha onde salvar uma cópia do historico.txt.
• Use isso para backup ou migração para outro computador.


10. Boas práticas de segurança

• Use o programa apenas com mídias próprias, autorizadas ou para backup pessoal.
• Não compartilhe sessao.session.
• Não compartilhe config.json.
• Não compartilhe historico.txt se ele contiver informações sensíveis.
• Não compartilhe seu API Hash.
• Só marque a opção de salvar API Hash em um computador pessoal e confiável.
• Faça backup do historico.txt antes de trocar de versão ou computador.
• Se algo der errado durante a execução, confira o log do programa.
• Se o computador desligar de repente, o maior risco é duplicar uma mídia recente, não perder o histórico inteiro.


11. Dicas rápidas

• Use destino "me" para salvar no próprio Telegram.
• Use delay para evitar envios rápidos demais.
• Use pausa automática para reduzir risco de limite do Telegram.
• Use exportar histórico antes de reinstalar ou migrar o app.
• Confira o log para saber o que foi enviado, ignorado ou se ocorreu erro.
"""

        help_box.insert("1.0", help_text)
        help_box.config(state="disabled")

        bottom_buttons = tk.Frame(card, bg=c["CARD"])
        bottom_buttons.pack(fill="x", padx=16, pady=(0, 14))
        self.widgets_to_theme.append((bottom_buttons, "CARD"))

        about_btn = tk.Button(
            bottom_buttons,
            text="Sobre o APP",
            command=lambda: self._show_about(win),
            bg=c["BG3"],
            fg=c["TEXT"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8
        )
        about_btn.pack(side="left")
        self.widgets_to_theme.append((about_btn, "BG3", None, "TEXT"))

        close_btn = tk.Button(
            bottom_buttons,
            text="Fechar",
            command=win.destroy,
            bg=c["BG3"],
            fg=c["TEXT"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=8
        )
        close_btn.pack(side="right")
        self.widgets_to_theme.append((close_btn, "BG3", None, "TEXT"))

    def _show_about(self, parent=None):
        try:
            if parent:
                parent.lift()
                parent.focus_force()
        except Exception:
            pass

        messagebox.showinfo(
            "Sobre",
            f"{APP_NAME}\nVersão {APP_VERSION}\n\n"
            "Ferramenta para encaminhamento autorizado de mídias do Telegram.\n"
            "Use apenas com conteúdos próprios, autorizados ou para backup pessoal.",
            parent=parent if parent else self
        )

    def _test_fields(self):
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        group = self.group_var.get().strip()
        dest = self.dest_var.get().strip()

        if not api_id or not api_hash or not group or not dest:
            self._log("Preencha API ID, API Hash, Origem e Destino antes de testar os campos.", "warn")
            return

        try:
            int(api_id)
        except ValueError:
            self._log("API ID deve ser um número inteiro.", "err")
            return

        self._log("Campos principais preenchidos corretamente. Você já pode iniciar ou fazer login.", "ok")

    def _get_live_config(self):
        try:
            delay = max(0.0, float(self.delay_var.get()))
        except Exception:
            delay = 1.0

        try:
            batch = max(1, int(self.batch_var.get()))
        except Exception:
            batch = 30

        try:
            pause = max(0, int(self.pause_var.get()))
        except Exception:
            pause = 30

        try:
            limit = max(1, int(self.limit_var.get()))
        except Exception:
            limit = 500

        return delay, batch, pause, limit

    def _log(self, msg, tag="ok"):
        timestamp = time.strftime("%H:%M:%S")

        prefixes = {
            "ok": "OK",
            "warn": "AVISO",
            "err": "ERRO",
            "info": "INFO",
            "muted": "INFO"
        }

        line = f"[{timestamp}]  {prefixes.get(tag, 'INFO'):<5}  {msg}\n"

        def do():
            self.log.config(state="normal")
            self.log.insert("end", line, tag)
            self.log.see("end")
            self.log.config(state="disabled")

        self.after(0, do)

    def _set_status(self, text, color=None):
        c = self.colors

        # Caso receba uma cor hexadecimal antiga, tentamos manter visual coerente.
        status_color = color if color else c["GREEN"]

        def do():
            self.status_lbl.config(text=text)
            self.status_dot.config(fg=status_color)
            self.status_lbl.config(fg=status_color)

        self.after(0, do)

    def _format_seconds(self, seconds):
        try:
            seconds = max(0, int(seconds))
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}"
        except Exception:
            return "00:00:00"

    def _required_fields_filled(self):
        try:
            return all([
                self.api_id_var.get().strip(),
                self.api_hash_var.get().strip(),
                self.group_var.get().strip(),
                self.dest_var.get().strip()
            ])
        except Exception:
            return False

    def _estimate_configured_total_time(self):
        """Calcula o tempo estimado com base nos campos preenchidos."""
        try:
            if not self._required_fields_filled():
                return "--"

            delay, batch, pause, limit = self._get_live_config()

            # Delay acontece entre envios, então não contamos delay após o último item.
            delay_total = max(0, limit - 1) * delay

            # Pausa automática acontece após cada lote completo, exceto se já chegou no limite final.
            pause_blocks = max(0, (limit - 1) // batch)
            pause_total = pause_blocks * pause

            estimated = delay_total + pause_total
            return self._format_seconds(estimated)
        except Exception:
            return "--"

    def _estimate_remaining_time(self):
        try:
            delay, batch, pause, limit = self._get_live_config()

            if not self._running:
                return self._estimate_configured_total_time()

            if self.sent_count >= limit:
                return "00:00:00"

            if self.sent_count <= 0:
                return self._estimate_configured_total_time()

            elapsed = time.time() - self._start_time
            avg_per_sent = elapsed / max(1, self.sent_count)
            remaining_items = max(0, limit - self.sent_count)
            estimated = int(avg_per_sent * remaining_items)

            return self._format_seconds(estimated)
        except Exception:
            return "--"

    def _register_stats_variable_traces(self):
        """Atualiza o tempo estimado quando o usuário altera os campos."""
        try:
            vars_to_watch = [
                self.api_id_var,
                self.api_hash_var,
                self.group_var,
                self.dest_var,
                self.delay_var,
                self.limit_var,
                self.batch_var,
                self.pause_var
            ]

            for var in vars_to_watch:
                var.trace_add("write", lambda *args: self._update_stats())
        except Exception:
            pass

    def _history_total_count(self):
        try:
            return len(carregar_historico())
        except Exception:
            return 0

    def _update_stats(self):
        total = self.sent_count + self.already_saved_count + self.ignored_count + self.error_count

        def do():
            self.sent_value.config(text=str(self.sent_count))
            self.skip_value.config(text=str(self.already_saved_count))
            self.err_value.config(text=str(self.error_count))
            self.total_lbl.config(text=f"🗂 Total processado: {total}")

            if self._start_time:
                elapsed = int(time.time() - self._start_time)
                self.elapsed_lbl.config(text=f"⏱ Tempo decorrido: {self._format_seconds(elapsed)}")
                self.remaining_lbl.config(text=f"⌛ Tempo restante: {self._estimate_remaining_time()}")
            else:
                self.elapsed_lbl.config(text="⏱ Tempo decorrido: 00:00:00")
                self.remaining_lbl.config(text=f"⌛ Tempo restante: {self._estimate_remaining_time()}")

        self.after(0, do)

    def _set_progress(self, value, maximum):
        def do():
            self.progress["maximum"] = maximum
            self.progress["value"] = value

        self.after(0, do)

    def _reset_stats(self):
        self.sent_count = 0
        self.skip_count = 0
        self.already_saved_count = 0
        self.ignored_count = 0
        self.error_count = 0
        self._start_time = time.time()
        self._update_stats()

    def _normalize_history_lines(self, lines):
        """Normaliza linhas do histórico, mantendo compatibilidade com histórico antigo."""
        normalized = []

        for line in lines:
            item = str(line).strip()
            if not item:
                continue

            # Aceita formato antigo: msg_id
            # Aceita formato novo: grupo_id:msg_id
            normalized.append(item)

        return normalized

    def _read_history_file(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return self._normalize_history_lines(f.readlines())

    def _write_history_file(self, items):
        with open(app_path(HISTORICO), "w", encoding="utf-8") as f:
            for item in items:
                f.write(f"{item}\n")

    def _import_history(self):
        if self._running:
            messagebox.showwarning(
                "Atenção",
                "Pare a execução antes de importar um histórico."
            )
            return

        selected = filedialog.askopenfilename(
            title="Selecionar histórico para importar",
            filetypes=[
                ("Arquivo de histórico", "*.txt"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if not selected:
            return

        try:
            imported_items = self._read_history_file(selected)

            if not imported_items:
                messagebox.showwarning(
                    "Histórico vazio",
                    "O arquivo selecionado não possui registros válidos."
                )
                return

            current_items = []
            current_path = app_path(HISTORICO)

            if os.path.exists(current_path):
                current_items = self._read_history_file(current_path)

            merged = []
            seen = set()

            for item in current_items + imported_items:
                if item not in seen:
                    seen.add(item)
                    merged.append(item)

            self._write_history_file(merged)

            added = len([item for item in imported_items if item not in set(current_items)])
            self._log(
                f"Histórico importado com sucesso. Novos registros: {max(0, added)} | Total: {len(merged)}.",
                "ok"
            )

            self._update_stats()

            messagebox.showinfo(
                "Histórico importado",
                f"Histórico importado com sucesso.\n\n"
                f"Novos registros adicionados: {max(0, added)}\n"
                f"Total no histórico atual: {len(merged)}"
            )

        except Exception as e:
            self._log(f"Erro ao importar histórico: {e}", "err")
            messagebox.showerror(
                "Erro ao importar histórico",
                f"Não foi possível importar o histórico.\n\nDetalhe: {e}"
            )

    def _export_history(self):
        try:
            current_path = app_path(HISTORICO)

            if not os.path.exists(current_path):
                messagebox.showwarning(
                    "Histórico não encontrado",
                    "Nenhum historico.txt foi encontrado para exportar."
                )
                return

            items = self._read_history_file(current_path)

            selected = filedialog.asksaveasfilename(
                title="Exportar histórico",
                defaultextension=".txt",
                initialfile="historico.txt",
                filetypes=[
                    ("Arquivo de histórico", "*.txt"),
                    ("Todos os arquivos", "*.*")
                ]
            )

            if not selected:
                return

            with open(selected, "w", encoding="utf-8") as f:
                for item in items:
                    f.write(f"{item}\n")

            self._log(
                f"Histórico exportado com sucesso. Registros exportados: {len(items)}.",
                "ok"
            )

            messagebox.showinfo(
                "Histórico exportado",
                f"Histórico exportado com sucesso.\n\n"
                f"Registros exportados: {len(items)}"
            )

        except Exception as e:
            self._log(f"Erro ao exportar histórico: {e}", "err")
            messagebox.showerror(
                "Erro ao exportar histórico",
                f"Não foi possível exportar o histórico.\n\nDetalhe: {e}"
            )

    def _confirm_clear_history(self):
        if self._running:
            messagebox.showwarning("Atenção", "Pare a execução antes de limpar o histórico.")
            return

        ok = messagebox.askyesno(
            "Limpar histórico",
            "Tem certeza que deseja limpar o histórico de mídias já enviadas?\n\n"
            "Depois disso, o programa poderá reenviar mídias antigas."
        )

        if ok:
            limpar_historico()
            self._log("Histórico limpo com sucesso.", "warn")

    # ────────────────────────────────────────────────────────────
    # Controles
    # ────────────────────────────────────────────────────────────
    def _start(self):
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        group = self.group_var.get().strip()
        dest = self.dest_var.get().strip()
        filter_ = self.filter_var.get().strip()

        if not api_id:
            self._log("Preencha o API ID.", "err")
            return
        if not api_hash:
            self._log("Preencha o API Hash.", "err")
            return
        if not group:
            self._log("Preencha a Origem.", "err")
            return
        if not dest:
            self._log("Preencha o Destino.", "err")
            return

        try:
            api_id = int(api_id)
        except ValueError:
            self._log("API ID deve ser um número inteiro.", "err")
            return

        delay, batch, pause, limit = self._get_live_config()

        self._paused = False
        self._stopped = False
        self._running = True
        self._reset_stats()
        self._set_progress(0, limit)

        self.btn_start.config(state="disabled")
        self.btn_pause.config(state="normal", text="⏸  Pausar")
        self.btn_stop.config(state="normal")

        self._set_status("Conectando", self.colors["YELLOW"])
        self._save_current_config()

        params = {
            "api_id": api_id,
            "api_hash": api_hash,
            "group": group,
            "dest": dest,
            "filter": filter_
        }

        threading.Thread(target=self._run_async, args=(params,), daemon=True).start()

    def _toggle_pause(self):
        self._paused = not self._paused

        if self._paused:
            self.btn_pause.config(text="▶  Retomar")
            self._set_status("Pausado", self.colors["YELLOW"])
            self._log("Encaminhamento pausado pelo usuário.", "warn")
        else:
            self.btn_pause.config(text="⏸  Pausar")
            self._set_status("Encaminhando", self.colors["GREEN"])
            self._log("Encaminhamento retomado pelo usuário.", "ok")

    def _stop(self):
        self._stopped = True
        self._paused = False
        self._set_status("Parando", self.colors["RED"])
        self._log("Parando encaminhamento com segurança...", "warn")

    def _on_finish(self):
        self._running = False
        self.btn_start.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸  Pausar")
        self.btn_stop.config(state="disabled")
        self._set_status("Aguardando", self.colors["GREEN"])
        self._update_stats()

    # ────────────────────────────────────────────────────────────
    # Core assíncrono
    # ────────────────────────────────────────────────────────────
    def _run_async(self, params):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._forward(params))
        finally:
            loop.close()
            self.after(0, self._on_finish)

    async def _forward(self, p):
        ja_enviados = carregar_historico()
        self._log(f"Histórico carregado: {len(ja_enviados)} registros.", "info")
        self._log("Conectando ao Telegram...", "info")

        try:
            client = TelegramClient(app_path(SESSION), p["api_id"], p["api_hash"])
            await client.connect()

            try:
                if not await client.is_user_authorized():
                    self._log("Sessão não encontrada ou não autorizada.", "err")
                    self._log('Clique em "Login Telegram" para criar sua sessão pelo aplicativo.', "warn")
                    self._set_status("Login necessário", self.colors["YELLOW"])
                    return

                self._log("Conectado ao Telegram com sucesso.", "ok")
                self._set_status("Conectado", self.colors["GREEN"])

                try:
                    saved = await client.get_input_entity(p["dest"])

                    if str(p["dest"]).strip().lower() == "me":
                        dest_label = "Mensagens Salvas"
                    else:
                        try:
                            dest_full = await client.get_entity(p["dest"])
                            dest_label = nome_entidade_telegram(dest_full, p["dest"])
                        except Exception:
                            dest_label = p["dest"]

                except Exception as e:
                    self._log(f"Não foi possível acessar o destino: {p['dest']}", "err")
                    self._log("Verifique se o destino existe e se sua conta tem permissão para enviar mensagens nele.", "warn")
                    self._log(f"Detalhe técnico: {e}", "muted")
                    return

                try:
                    group = await client.get_input_entity(p["group"])
                    group_full = await client.get_entity(p["group"])
                    group_id = getattr(group_full, "id", "desconhecido")
                    group_label = nome_entidade_telegram(group_full, p["group"])
                except Exception as e:
                    self._log(f"Não foi possível acessar a origem: {p['group']}", "err")
                    self._log("Verifique se o link, grupo ou canal está correto e se sua conta tem acesso a ele.", "warn")
                    self._log(f"Detalhe técnico: {e}", "muted")
                    return

                self._log(f"Conectado à origem: {group_label}", "ok")
                self._log(f"ID interno da origem: {group_id}", "info")
                self._log(f"Destino configurado: {dest_label}", "ok")

                filter_id = None
                if p["filter"]:
                    try:
                        filter_ent = await client.get_entity(p["filter"])
                        filter_id = filter_ent.id
                        filter_label = nome_entidade_telegram(filter_ent, p["filter"])
                        self._log(f"Filtro ativo: {filter_label}", "info")
                        self._log(f"ID interno do filtro: {filter_id}", "muted")
                    except Exception as e:
                        self._log("Filtro inválido ou inacessível.", "err")
                        self._log("Verifique se o filtro foi preenchido corretamente e se sua conta tem acesso a ele.", "warn")
                        self._log(f"Detalhe técnico: {e}", "muted")
                        return

                self._log("Iniciando encaminhamento de mídias...", "ok")
                self._set_status("Encaminhando", self.colors["GREEN"])

                # Processa em ordem cronológica: da mídia mais antiga para a mais recente.
                async for msg in client.iter_messages(group, reverse=True):
                    if self._stopped:
                        self._log(f"Execução interrompida pelo usuário. Mídias enviadas nesta execução: {self.sent_count}.", "warn")
                        return

                    while self._paused:
                        await asyncio.sleep(0.3)
                        if self._stopped:
                            return

                    delay, batch, pause_secs, limit = self._get_live_config()

                    if not msg.media:
                        continue

                    if not isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)):
                        self.skip_count += 1
                        self.ignored_count += 1
                        self._update_stats()
                        continue

                    if media_eh_sticker(msg.media):
                        self.skip_count += 1
                        self._update_stats()
                        self._log("Mídia ignorada: figurinha/sticker.", "info")
                        continue

                    chave = montar_chave_historico(group_id, msg.id)

                    # Compatibilidade com histórico antigo: ignora também linhas antigas com só msg.id.
                    if chave in ja_enviados or str(msg.id) in ja_enviados:
                        self.skip_count += 1
                        self.already_saved_count += 1
                        self._update_stats()
                        continue

                    if filter_id is not None:
                        fwd = msg.fwd_from

                        if not fwd:
                            self.skip_count += 1
                            self._update_stats()
                            continue

                        from_id = (
                            getattr(fwd.from_id, "channel_id", None)
                            or getattr(fwd.from_id, "chat_id", None)
                            or getattr(fwd.from_id, "user_id", None)
                        )

                        if from_id != filter_id:
                            self.skip_count += 1
                            self._update_stats()
                            continue

                    try:
                        await client.forward_messages(saved, msg)

                        salvar_id(group_id, msg.id)
                        ja_enviados.add(chave)

                        self.sent_count += 1
                        self._update_stats()
                        self._set_progress(self.sent_count, limit)

                        self._log(f"[{self.sent_count}/{limit}] Mídia encaminhada. ID {msg.id}", "ok")

                        if self.sent_count >= limit:
                            self._log(f"Encaminhamento concluído. {self.sent_count} mídias enviadas nesta execução.", "ok")
                            self._set_status("Concluído", self.colors["ACCENT3"])
                            return

                        if self.sent_count % batch == 0:
                            self._log(f"Pausa automática iniciada: aguardando {pause_secs}s após {self.sent_count} mídias enviadas.", "warn")
                            self._set_status(f"Pausa {pause_secs}s", self.colors["YELLOW"])

                            for _ in range(pause_secs * 2):
                                if self._stopped:
                                    return
                                if self._paused:
                                    break
                                await asyncio.sleep(0.5)

                            if not self._paused:
                                self._set_status("Encaminhando", self.colors["GREEN"])

                        await asyncio.sleep(delay)

                    except FloodWaitError as e:
                        self.error_count += 1
                        self._update_stats()
                        self._log(f"O Telegram pediu uma pausa temporária. Aguardando {e.seconds}s antes de continuar.", "warn")
                        self._set_status(f"FloodWait {e.seconds}s", self.colors["YELLOW"])
                        await asyncio.sleep(e.seconds + 5)
                        self._set_status("Encaminhando", self.colors["GREEN"])

                    except RPCError as e:
                        self.error_count += 1
                        self._update_stats()
                        self._log(f"O Telegram recusou o envio da mídia ID {msg.id}.", "err")
                        self._log("O envio foi pulado e o programa continuará com as próximas mídias.", "warn")
                        self._log(f"Detalhe técnico: {e}", "muted")

                    except Exception as e:
                        self.error_count += 1
                        self._update_stats()
                        self._log(f"Erro inesperado ao processar a mídia ID {msg.id}.", "err")
                        self._log("O programa continuará tentando processar as próximas mídias.", "warn")
                        self._log(f"Detalhe técnico: {e}", "muted")

                self._log("Fim da origem. Não há mais mídias para processar dentro do limite configurado.", "ok")
                self._log(f"Resumo final — Enviadas: {self.sent_count} | Já salvas/ignoradas: {self.skip_count} | Erros: {self.error_count}", "info")

            finally:
                await client.disconnect()

        except ApiIdInvalidError:
            self.error_count += 1
            self._update_stats()
            self._log("API ID ou API Hash inválido.", "err")
            self._log("Confira os dados em https://my.telegram.org e tente novamente.", "warn")
            self._set_status("Erro", self.colors["RED"])

        except SessionPasswordNeededError:
            self.error_count += 1
            self._update_stats()
            self._log("Esta conta exige senha de verificação em duas etapas.", "err")
            self._log('Use o botão "Login Telegram" e informe a senha 2FA no campo indicado.', "warn")
            self._set_status("2FA necessária", self.colors["YELLOW"])

        except ConnectionError:
            self.error_count += 1
            self._update_stats()
            self._log("Não foi possível conectar ao Telegram.", "err")
            self._log("Verifique sua internet e tente novamente em alguns minutos.", "warn")
            self._set_status("Sem conexão", self.colors["RED"])

        except Exception as e:
            self.error_count += 1
            self._update_stats()
            self._log("Erro inesperado durante a execução.", "err")
            self._log("Confira os campos preenchidos, sua conexão e tente novamente.", "warn")
            self._log(f"Detalhe técnico: {e}", "muted")
            self._set_status("Erro", self.colors["RED"])


if __name__ == "__main__":
    app = App()
    app.mainloop()
