import os
from pathlib import Path

class Settings:
    """Configurações do sistema"""
    
    # Configurações da aplicação
    APP_NAME = "NUVIG"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Sistema de Controle de Acesso Desktop"
    
    # Configurações da janela
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    WINDOW_RESIZABLE = True
    WINDOW_MAXIMIZABLE = True
    
    # Configurações do banco de dados
    DATABASE_NAME = "nuvig.db"
    DATABASE_PATH = Path.cwd() / DATABASE_NAME
    
    # Configurações de log
    LOG_LEVEL = "INFO"
    LOG_FILE = "nuvig.log"
    LOG_MAX_SIZE_MB = 10
    LOG_BACKUP_COUNT = 5
    
    # Configurações de tema
    THEME_MODE = "light"  # light, dark, system
    PRIMARY_COLOR = "#1976D2"
    SECONDARY_COLOR = "#424242"
    SUCCESS_COLOR = "#4CAF50"
    WARNING_COLOR = "#FF9800"
    ERROR_COLOR = "#F44336"
    INFO_COLOR = "#2196F3"
    
    # Configurações de interface
    BUTTON_HEIGHT = 45
    TEXT_FIELD_WIDTH = 300
    CARD_ELEVATION = 5
    BORDER_RADIUS = 8
    
    # Configurações de navegação
    DEFAULT_SCREEN = "home"
    HOME_SCREEN = "home"
    
    # Configurações de mensagens
    MESSAGE_DURATION_MS = 3000
    ERROR_MESSAGE_COLOR = "red"
    SUCCESS_MESSAGE_COLOR = "green"
    INFO_MESSAGE_COLOR = "blue"
    WARNING_MESSAGE_COLOR = "orange"
    
    # Configurações de sistema
    AUTO_SAVE_INTERVAL = 30  # segundos
    MAX_LOG_ENTRIES = 1000
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 24
    
    @classmethod
    def get_database_path(cls) -> str:
        """Retorna o caminho completo do banco de dados"""
        return str(cls.DATABASE_PATH)
    
    @classmethod
    def get_log_path(cls) -> str:
        """Retorna o caminho completo do arquivo de log"""
        return str(Path.cwd() / cls.LOG_FILE)
    
    @classmethod
    def ensure_directories(cls):
        """Garante que os diretórios necessários existam"""
        # Criar diretório de logs se não existir
        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Criar diretório de configurações se não existir
        config_dir = Path.cwd() / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Criar diretório de dados se não existir
        data_dir = Path.cwd() / "data"
        data_dir.mkdir(exist_ok=True)
        
        # Criar diretório de backups se não existir
        backup_dir = Path.cwd() / "backups"
        backup_dir.mkdir(exist_ok=True)
    
    @classmethod
    def get_theme_colors(cls) -> dict:
        """Retorna as cores do tema atual"""
        if cls.THEME_MODE == "dark":
            return {
                "primary": "#90CAF9",
                "secondary": "#BDBDBD",
                "background": "#121212",
                "surface": "#1E1E1E",
                "text": "#FFFFFF",
                "text_secondary": "#BDBDBD"
            }
        else:  # light theme
            return {
                "primary": cls.PRIMARY_COLOR,
                "secondary": cls.SECONDARY_COLOR,
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "text": "#212121",
                "text_secondary": "#757575"
            }
