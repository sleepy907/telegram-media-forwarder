
import asyncio
import threading
import os
import json
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import FloodWaitError, RPCError, SessionPasswordNeededError, ApiIdInvalidError, PhoneCodeInvalidError, PasswordHashInvalidError


# ────────────────────────────────────────────────────────────────
# Telegram Media Forwarder
# Versão com visual profissional + logo integrado + botões centralizados
# ────────────────────────────────────────────────────────────────

APP_NAME = "Telegram Media Forwarder"
APP_VERSION = "0.0.1"

HISTORICO = "historico.txt"
CONFIG = "config.json"
SESSION = "sessao"
LOGO_FILE = "logo.png"

# URL futura para checagem real de updates.
# Quando publicarmos o projeto no GitHub, basta colocar aqui o link do update.json.
UPDATE_URL = ""

# Enquanto ainda não existe update.json, usamos uma versão local simulada.
LATEST_VERSION_PLACEHOLDER = "0.0.1"


THEMES = {
    "dark": {
        "BG": "#090914",
        "BG2": "#10101f",
        "BG3": "#17172b",
        "BG4": "#22223a",
        "CARD": "#111122",
        "CARD2": "#15152a",
        "BORDER": "#30295f",
        "BORDER2": "#4c2bbf",
        "TEXT": "#f4f1ff",
        "SUBTEXT": "#aaa3c7",
        "MUTED": "#746d91",
        "ACCENT": "#7c3aed",
        "ACCENT2": "#a855f7",
        "ACCENT3": "#c084fc",
        "GREEN": "#4ade80",
        "YELLOW": "#fbbf24",
        "RED": "#fb7185",
        "BLUE": "#38bdf8",
        "ENTRY": "#0c0c1a",
        "LOG_BG": "#080815"
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
        self.error_count = 0

        self.logo_img = None
        self.widgets_to_theme = []

        # Estado usado pela tela de login
        self._login_phone = ""
        self._login_phone_code_hash = None

        # Variáveis
        self.api_id_var = tk.StringVar()
        self.api_hash_var = tk.StringVar()
        self.group_var = tk.StringVar()
        self.dest_var = tk.StringVar(value="me")
        self.filter_var = tk.StringVar()

        self.delay_var = tk.StringVar(value="1.0")
        self.limit_var = tk.StringVar(value="500")
        self.batch_var = tk.StringVar(value="30")
        self.pause_var = tk.StringVar(value="30")

        cfg = carregar_config()
        self.api_id_var.set(cfg.get("api_id", ""))
        self.api_hash_var.set("")
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
        self._apply_theme()
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
        self.content.pack(fill="both", expand=True, padx=12, pady=12)
        self.widgets_to_theme.append((self.content, "BG"))

        self._build_header()
        self._build_action_bar()
        self._build_main_area()
        self._build_footer()

    def _on_scroll_frame_configure(self, event=None):
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        except Exception:
            pass

    def _on_canvas_configure(self, event):
        try:
            self.canvas.itemconfig(self.canvas_window, width=event.width)
        except Exception:
            pass

    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    def _on_mousewheel_linux(self, event):
        try:
            if event.num == 4:
                self.canvas.yview_scroll(-3, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(3, "units")
        except Exception:
            pass


    def _build_header(self):
        c = self.colors

        self.header = tk.Frame(self.content, bg=c["CARD"], highlightthickness=1, highlightbackground=c["BORDER"])
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

        self.status_card = tk.Frame(right, bg=c["BG2"], highlightthickness=1, highlightbackground=c["BORDER"])
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

        self.info_btn = self._small_btn(right, "i", self._show_about)
        self.info_btn.pack(side="left", padx=4)

    def _build_action_bar(self):
        c = self.colors

        self.action_panel = tk.Frame(self.content, bg=c["CARD"], highlightthickness=1, highlightbackground=c["BORDER"])
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

        self.sent_card, self.sent_value = self._stat_box(row, "✈", "Enviadas", "0", "GREEN")
        self.sent_card.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.skip_card, self.skip_value = self._stat_box(row, "⏭", "Já salvas", "0", "YELLOW")
        self.skip_card.pack(side="left", fill="x", expand=True, padx=8)

        self.err_card, self.err_value = self._stat_box(row, "⚠", "Erros", "0", "RED")
        self.err_card.pack(side="left", fill="x", expand=True, padx=(8, 0))

        bottom = tk.Frame(card, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        bottom.pack(fill="x", padx=16, pady=(0, 10))
        self.widgets_to_theme.append((bottom, "CARD2", "BORDER"))

        self.elapsed_lbl = tk.Label(bottom, text="⏱ Tempo decorrido: 00:00:00", bg=c["CARD2"], fg=c["SUBTEXT"], font=FONT_S)
        self.elapsed_lbl.pack(side="left", padx=12, pady=10)
        self.widgets_to_theme.append((self.elapsed_lbl, "CARD2", None, "SUBTEXT"))

        self.total_lbl = tk.Label(bottom, text="🗂 Total processado: 0", bg=c["CARD2"], fg=c["SUBTEXT"], font=FONT_S)
        self.total_lbl.pack(side="right", padx=12, pady=10)
        self.widgets_to_theme.append((self.total_lbl, "CARD2", None, "SUBTEXT"))

        self.progress = ttk.Progressbar(card, style="Purple.Horizontal.TProgressbar", mode="determinate")
        self.progress.pack(fill="x", padx=16, pady=(0, 8))

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
        f = tk.Frame(parent, bg=c["CARD"], highlightthickness=1, highlightbackground=c["BORDER"])
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
        self.widgets_to_theme.append((ent, "ENTRY", "BORDER", "TEXT"))

        return ent

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
            factor = max(1, w // 110)
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
        salvar_config({
            "api_id": self.api_id_var.get().strip(),
            "group": self.group_var.get().strip(),
            "dest": self.dest_var.get().strip(),
            "filter": self.filter_var.get().strip(),
            "delay": self.delay_var.get().strip(),
            "limit": self.limit_var.get().strip(),
            "batch": self.batch_var.get().strip(),
            "pause": self.pause_var.get().strip(),
            "theme": self.theme_name
        })

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
        win.geometry("520x360")
        win.resizable(False, False)
        win.configure(bg=c["BG"])
        win.transient(self)
        win.grab_set()

        container = tk.Frame(win, bg=c["BG"])
        container.pack(fill="both", expand=True, padx=18, pady=18)

        card = tk.Frame(container, bg=c["CARD"], highlightthickness=1, highlightbackground=c["BORDER"])
        card.pack(fill="both", expand=True)

        title = tk.Label(
            card,
            text="↻  Checar atualizações",
            bg=c["CARD"],
            fg=c["ACCENT3"],
            font=("Segoe UI", 14, "bold")
        )
        title.pack(anchor="w", padx=18, pady=(12, 6))

        desc = tk.Label(
            card,
            text="Verifique se existe uma nova versão disponível do Telegram Media Forwarder.",
            bg=c["CARD"],
            fg=c["SUBTEXT"],
            font=FONT,
            justify="left",
            wraplength=460
        )
        desc.pack(anchor="w", padx=18, pady=(0, 10))

        info_box = tk.Frame(card, bg=c["CARD2"], highlightthickness=1, highlightbackground=c["BORDER"])
        info_box.pack(fill="x", padx=18, pady=(0, 10))

        self.update_window_installed = tk.Label(
            info_box,
            text=f"Versão instalada: {APP_VERSION}",
            bg=c["CARD2"],
            fg=c["TEXT"],
            font=FONT_B
        )
        self.update_window_installed.pack(anchor="w", padx=12, pady=(12, 4))

        self.update_window_latest = tk.Label(
            info_box,
            text="Última versão: não checado",
            bg=c["CARD2"],
            fg=c["SUBTEXT"],
            font=FONT
        )
        self.update_window_latest.pack(anchor="w", padx=12, pady=4)

        self.update_window_status = tk.Label(
            info_box,
            text="Status: aguardando checagem",
            bg=c["CARD2"],
            fg=c["SUBTEXT"],
            font=FONT
        )
        self.update_window_status.pack(anchor="w", padx=12, pady=(4, 12))

        btns = tk.Frame(card, bg=c["CARD"])
        btns.pack(fill="x", padx=18, pady=(0, 10))

        check_btn = tk.Button(
            btns,
            text="🔎  Checar atualização",
            command=lambda: self._check_update_in_window(win),
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
        check_btn.pack(side="left")

        changelog_btn = tk.Button(
            btns,
            text="📄  Changelog",
            command=self._show_changelog_placeholder,
            bg=c["CARD2"],
            fg=c["ACCENT3"],
            activebackground=c["BG4"],
            activeforeground=c["TEXT"],
            font=FONT_B,
            bd=0,
            relief="flat",
            cursor="hand2",
            padx=16,
            pady=10
        )
        changelog_btn.pack(side="left", padx=10)

        close_btn = tk.Button(
            btns,
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

        note = tk.Label(
            card,
            text="Por enquanto a checagem é local. Depois vamos conectar ao update.json no GitHub.",
            bg=c["CARD"],
            fg=c["MUTED"],
            font=FONT_S,
            justify="left",
            wraplength=460
        )
        note.pack(anchor="w", padx=18, pady=(0, 8))

    def _version_tuple(self, version):
        parts = []
        for piece in str(version).replace("v", "").split("."):
            try:
                parts.append(int(piece))
            except ValueError:
                parts.append(0)
        return tuple(parts)

    def _check_update_in_window(self, win=None):
        latest = LATEST_VERSION_PLACEHOLDER
        current = APP_VERSION

        if hasattr(self, "update_window_latest"):
            self.update_window_latest.config(text=f"Última versão: {latest}")

        if self._version_tuple(latest) > self._version_tuple(current):
            if hasattr(self, "update_window_status"):
                self.update_window_status.config(text="Status: nova atualização disponível", fg=self.colors["YELLOW"])
            messagebox.showinfo(
                "Atualização disponível",
                f"Existe uma nova versão disponível: {latest}\n\nVersão instalada: {current}",
                parent=win
            )
        else:
            if hasattr(self, "update_window_status"):
                self.update_window_status.config(text="Status: você está usando a versão mais recente", fg=self.colors["GREEN"])
            messagebox.showinfo(
                "Sem atualizações",
                f"Você já está usando a versão mais recente.\n\nVersão instalada: {current}",
                parent=win
            )

    def _show_changelog_placeholder(self):
        win = tk.Toplevel(self)
        win.title("Changelog")
        win.geometry("720x620")
        win.minsize(620, 500)
        win.configure(bg=self.colors["BG"])
        win.transient(self)

        container = tk.Frame(win, bg=self.colors["BG"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        card = tk.Frame(
            container,
            bg=self.colors["CARD"],
            highlightthickness=1,
            highlightbackground=self.colors["BORDER"]
        )
        card.pack(fill="both", expand=True)

        title = tk.Label(
            card,
            text="📋 Changelog — Telegram Media Forwarder v0.0.1",
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

        changelog = """Changelog — Telegram Media Forwarder v0.0.1

ADICIONADO
• Interface gráfica profissional desenvolvida em Python com Tkinter.
• Integração com Telethon para encaminhamento autorizado de mídias do Telegram.
• Suporte a tema escuro e tema claro.
• Logo integrada ao cabeçalho do aplicativo.
• Botões principais centralizados: Iniciar, Pausar/Retomar e Parar.
• Cards visuais para Credenciais, Configurações, Estatísticas e Log.
• Estatísticas em tempo real: mídias enviadas, já salvas/ignoradas, erros, tempo decorrido e total processado.
• Sistema de histórico com historico.txt para evitar reenvio de mídias.
• Compatibilidade com histórico antigo baseado apenas em msg_id.
• Botão discreto de checagem de atualizações com janela própria.
• Tela de login do Telegram dentro do aplicativo, evitando login manual pelo terminal.
• Estrutura preparada para futuro update.json.
• Scroll vertical para evitar corte de conteúdo em telas menores.

MELHORADO
• Layout modernizado com identidade visual roxa/violeta.
• Organização dos dados do aplicativo para uso em versão empacotada.
• Tratamento de erros para conexão, API inválida, FloodWait, RPCError e sessão com 2FA.
• Configurações salvas automaticamente em config.json.
• Suporte a destino configurável, incluindo Mensagens Salvas, grupos, canais ou bots.
• Suporte a delay, limite de envio, pausa automática e filtro por origem.

EMPACOTAMENTO
• Criado pacote RPM para Fedora 44.
• Instalador adiciona executável, logo, ícone e atalho no menu de aplicativos.
• Dados pessoais mantidos fora do pacote, em pasta local do usuário.

SEGURANÇA
• sessao.session, historico.txt e config.json não são incluídos no RPM.
• API Hash não é salvo automaticamente por padrão.
• Programa orientado para uso autorizado, backup pessoal e respeito às permissões do Telegram.
• Sessão do Telegram criada localmente no computador do usuário.
"""

        changelog_box.insert("1.0", changelog)
        changelog_box.config(state="disabled")

        close_btn = tk.Button(
            card,
            text="Fechar",
            command=win.destroy,
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

    def _show_about(self):
        messagebox.showinfo(
            "Sobre",
            f"{APP_NAME}\nVersão {APP_VERSION}\n\n"
            "Ferramenta para encaminhamento autorizado de mídias do Telegram.\n"
            "Use apenas com conteúdos próprios, autorizados ou para backup pessoal."
        )

    def _test_fields(self):
        api_id = self.api_id_var.get().strip()
        api_hash = self.api_hash_var.get().strip()
        group = self.group_var.get().strip()
        dest = self.dest_var.get().strip()

        if not api_id or not api_hash or not group or not dest:
            self._log("Preencha API ID, API Hash, Origem e Destino antes de testar.", "warn")
            return

        try:
            int(api_id)
        except ValueError:
            self._log("API ID deve ser um número inteiro.", "err")
            return

        self._log("Campos principais preenchidos corretamente.", "ok")

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

    def _update_stats(self):
        total = self.sent_count + self.skip_count + self.error_count

        def do():
            self.sent_value.config(text=str(self.sent_count))
            self.skip_value.config(text=str(self.skip_count))
            self.err_value.config(text=str(self.error_count))
            self.total_lbl.config(text=f"🗂 Total processado: {total}")

            if self._start_time:
                elapsed = int(time.time() - self._start_time)
                h = elapsed // 3600
                m = (elapsed % 3600) // 60
                s = elapsed % 60
                self.elapsed_lbl.config(text=f"⏱ Tempo decorrido: {h:02d}:{m:02d}:{s:02d}")

        self.after(0, do)

    def _set_progress(self, value, maximum):
        def do():
            self.progress["maximum"] = maximum
            self.progress["value"] = value

        self.after(0, do)

    def _reset_stats(self):
        self.sent_count = 0
        self.skip_count = 0
        self.error_count = 0
        self._start_time = time.time()
        self._update_stats()

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
            self._log("Execução pausada.", "warn")
        else:
            self.btn_pause.config(text="⏸  Pausar")
            self._set_status("Encaminhando", self.colors["GREEN"])
            self._log("Execução retomada.", "ok")

    def _stop(self):
        self._stopped = True
        self._paused = False
        self._set_status("Parando", self.colors["RED"])
        self._log("Encerrando execução...", "warn")

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
                    self._log("Sessão do Telegram não encontrada ou não autorizada.", "err")
                    self._log("Clique em 🔑 Login Telegram para criar a sessão pelo próprio programa.", "warn")
                    self._set_status("Login necessário", self.colors["YELLOW"])
                    return

                self._log("Conectado ao Telegram com sucesso.", "ok")
                self._set_status("Conectado", self.colors["GREEN"])

                try:
                    saved = await client.get_input_entity(p["dest"])
                except Exception as e:
                    self._log(f"Destino inválido ou inacessível: {p['dest']}", "err")
                    self._log(f"Detalhe: {e}", "err")
                    return

                try:
                    group = await client.get_input_entity(p["group"])
                    group_full = await client.get_entity(p["group"])
                    group_id = getattr(group_full, "id", "desconhecido")
                except Exception as e:
                    self._log(f"Origem inválida ou inacessível: {p['group']}", "err")
                    self._log(f"Detalhe: {e}", "err")
                    return

                dest_label = "Mensagens Salvas" if p["dest"] == "me" else p["dest"]
                self._log(f"Origem: {p['group']} | ID interno: {group_id}", "info")
                self._log(f"Destino: {dest_label}", "info")

                filter_id = None
                if p["filter"]:
                    try:
                        filter_ent = await client.get_entity(p["filter"])
                        filter_id = filter_ent.id
                        self._log(f"Filtro ativo: {p['filter']} | ID {filter_id}", "info")
                    except Exception as e:
                        self._log(f"Filtro inválido: {e}", "err")
                        return

                self._log("Iniciando encaminhamento...", "ok")
                self._set_status("Encaminhando", self.colors["GREEN"])

                async for msg in client.iter_messages(group):
                    if self._stopped:
                        self._log(f"Execução encerrada. Enviadas: {self.sent_count}", "warn")
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
                        self._update_stats()
                        continue

                    chave = montar_chave_historico(group_id, msg.id)

                    # Compatibilidade com histórico antigo: ignora também linhas antigas com só msg.id.
                    if chave in ja_enviados or str(msg.id) in ja_enviados:
                        self.skip_count += 1
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
                            self._log(f"Concluído! {self.sent_count} mídias encaminhadas.", "ok")
                            self._set_status("Concluído", self.colors["ACCENT3"])
                            return

                        if self.sent_count % batch == 0:
                            self._log(f"Pausa automática de {pause_secs}s após {self.sent_count} mídias.", "warn")
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
                        self._log(f"FloodWait: aguardando {e.seconds}s.", "warn")
                        self._set_status(f"FloodWait {e.seconds}s", self.colors["YELLOW"])
                        await asyncio.sleep(e.seconds + 5)
                        self._set_status("Encaminhando", self.colors["GREEN"])

                    except RPCError as e:
                        self.error_count += 1
                        self._update_stats()
                        self._log(f"Erro do Telegram ao enviar ID {msg.id}: {e}", "err")

                    except Exception as e:
                        self.error_count += 1
                        self._update_stats()
                        self._log(f"Erro inesperado no ID {msg.id}: {e}", "err")

                self._log(f"Fim do grupo. Enviadas: {self.sent_count}", "ok")
                self._log(f"Ignoradas: {self.skip_count} | Erros: {self.error_count}", "info")

            finally:
                await client.disconnect()

        except ApiIdInvalidError:
            self.error_count += 1
            self._update_stats()
            self._log("API ID ou API Hash inválido.", "err")
            self._set_status("Erro", self.colors["RED"])

        except SessionPasswordNeededError:
            self.error_count += 1
            self._update_stats()
            self._log("Esta conta exige senha de verificação em duas etapas.", "err")
            self._log("Conclua o login solicitado pelo Telethon no terminal.", "warn")
            self._set_status("2FA necessária", self.colors["YELLOW"])

        except ConnectionError:
            self.error_count += 1
            self._update_stats()
            self._log("Erro de conexão. Verifique sua internet.", "err")
            self._set_status("Sem conexão", self.colors["RED"])

        except Exception as e:
            self.error_count += 1
            self._update_stats()
            self._log(f"Erro geral: {e}", "err")
            self._set_status("Erro", self.colors["RED"])


if __name__ == "__main__":
    app = App()
    app.mainloop()
