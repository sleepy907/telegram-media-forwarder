
APP_NAME = "Telegram Media Forwarder"
APP_VERSION = "0.2.0"

HISTORICO = "historico.txt"
CONFIG = "config.json"
SESSION = "sessao"
import os
LOGO_FILE = os.path.join("assets", "logo.png")

UPDATE_URL = "https://raw.githubusercontent.com/sleepy907/telegram-media-forwarder/main/update.json"
CHANGELOG_URL = "https://raw.githubusercontent.com/sleepy907/telegram-media-forwarder/main/CHANGELOG.md"
LATEST_VERSION_PLACEHOLDER = "0.2.0"

THEMES = {
    "dark": {
        "BG": "#181825",
        "BG2": "#1e1e2e",
        "BG3": "#313244",
        "BG4": "#45475a",
        "CARD": "#1e1e2e",
        "CARD2": "#313244",
        "BORDER": "#181825",
        "BORDER2": "#313244",
        "TEXT": "#cdd6f4",
        "SUBTEXT": "#a6adc8",
        "MUTED": "#7f849c",
        "ACCENT": "#a855f7",
        "ACCENT2": "#9333ea",
        "ACCENT3": "#f38ba8",
        "GREEN": "#a6e3a1",
        "YELLOW": "#f9e2af",
        "RED": "#f38ba8",
        "BLUE": "#89b4fa",
        "ENTRY": "#11111b",
        "LOG_BG": "#11111b"
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
