import flet as ft
from screens.home_screen import HomeScreen
from screens.calendario_screen import CalendarioScreen
from screens.cadastro_screen import CadastroScreen
from screens.cadastro_policial_screen import CadastroPolicialScreen
from screens.extras_screen import ExtrasScreen
from screens.permutas_screen import PermutasScreen
from screens.compensacoes_screen import CompensacoesScreen
from database.database_manager import DatabaseManager
from pathlib import Path
import os, sys, shutil

from pathlib import Path
import os, sys, shutil, traceback

APP_NAME = "Nuvig"
DB_NAME  = "nuvig.db"

def _app_root() -> Path:
    # build (exe) => pasta do executável; dev => pasta do main.py
    return Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent

def _seed_candidates() -> list[Path]:
    r = _app_root()
    return [
        # DEV (rodando pelo Python)
        r / "assets" / "db" / DB_NAME,
        # BUILD (caminhos que de fato aparecem nas builds do Flutter/Flet)
        r / "data" / "flutter_assets" / "assets" / "db" / DB_NAME,      # comum
        r / "flutter_assets" / "assets" / "db" / DB_NAME,               # variação
        r / "data" / "flutter_assets" / DB_NAME,                        # fallback extremo
    ]

def _find_seed() -> Path:
    for p in _seed_candidates():
        if p.exists():
            return p
    # devolve o primeiro só pra mensagem ficar clara caso dê erro
    return _seed_candidates()[0]

def _user_db() -> Path:
    base = Path(os.getenv("LOCALAPPDATA", Path.home()))
    data_dir = base / APP_NAME
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / DB_NAME

def ensure_db() -> Path:

    dst = _user_db()
    if not dst.exists():
        src = _find_seed()
        if not src.exists():
            raise FileNotFoundError(
                "Seed DB não encontrado em nenhum dos locais esperados:\n" +
                "\n".join(str(p) for p in _seed_candidates())
            )
        shutil.copy(src, dst)
    return dst



class MainApp:
    def __init__(self):
        self.db = DatabaseManager(db_path=str(Path(__file__).parent / "assets" / "db" / "nuvig.db"))
        self.current_screen = None
        
    def main(self, page: ft.Page):
        try:
            # Configurações da página
            self.page = page
            page.title = "NUVIG - Gestão"
            page.window.icon = os.path.abspath("assets/icons/nuvig.ico")
            page.window_width = 1400
            page.window_height = 900
            page.window_resizable = True
            page.theme_mode = ft.ThemeMode.LIGHT
            page.padding = 0
            page.locale_configuration = ft.Locale(
                                        language_code="pt"
                                        )
            #a = ft.Locale(language_code="pt")

            # Inicializar banco de dados
            self.db.init_database()

            # Dicionário de telas
            self.screens = {
                "home": HomeScreen(self),
                "calendario": CalendarioScreen(self),
                "cadastro": CadastroScreen(self),
                "cadastro_policial": CadastroPolicialScreen(self),
                "extras": ExtrasScreen(self),
                "permutas": PermutasScreen(self),
                "compensacoes": CompensacoesScreen(self),
                "edicao_registros": __import__("screens.edicao_registros_screen", fromlist=["EdicaoRegistrosScreen"]).EdicaoRegistrosScreen(self),
                "ferias": __import__("screens.ferias_screen", fromlist=["FeriasScreen"]).FeriasScreen(self),
                "ausencias": __import__("screens.ausencias_screen", fromlist=["AusenciasScreen"]).AusenciasScreen(self),
                "cadastrar_extra": __import__("screens.cadastrar_extra_screen", fromlist=["CadastrarExtraScreen"]).CadastrarExtraScreen(self),
                "consultar_extras": __import__("screens.consultar_extras_screen", fromlist=["ConsultarExtrasScreen"]).ConsultarExtrasScreen(self),
            }

            # Container para o conteúdo dinâmico
            content_container = ft.Container(
                expand=True,
                padding=20
            )

            # Função para navegar entre telas
            def navigate_to(screen_name: str):
                if screen_name in self.screens:
                    # Atualizar a tela atual
                    self.current_screen = self.screens[screen_name]
                    # Trocar apenas o conteúdo, não a view inteira
                    content_container.content = self.current_screen.get_content()
                    page.update()
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Tela '{screen_name}' em desenvolvimento"),
                        bgcolor=ft.Colors.ORANGE
                    )
                    page.snack_bar.open = True
                    page.update()

            # Configurar navegação para cada tela
            for screen in self.screens.values():
                screen.set_navigation_callback(navigate_to)

            # Layout principal com navbar fixa
            from screens.navbar import NavBar

            navbar = NavBar(
                on_nav=navigate_to,
                selected_nav="home"
            )

            # Layout principal
            main_layout = ft.Column(
                controls=[
                    navbar,  # Navbar fixa
                    ft.Divider(height=1, color=ft.Colors.GREY),
                    content_container  # Container para conteúdo dinâmico
                ],
                spacing=0,
                expand=True
            )

            # Adicionar o layout principal à página
            page.add(main_layout)

            # Iniciar com a tela home
            navigate_to("home")

        except Exception as e:
            page.add(
                ft.Text("Erro ao iniciar o aplicativo:", color=ft.Colors.RED, size=18),
                ft.Text(str(e), selectable=True),
                ft.Text(traceback.format_exc(), selectable=True, size=12),
            )


if __name__ == "__main__":
    app = MainApp()
    ft.app(target=app.main, assets_dir="assets")
