import flet as ft
from screens.home_screen import HomeScreen
from screens.login_screen import LoginScreen
from screens.calendario_screen import CalendarioScreen
from screens.cadastro_screen import CadastroScreen
from screens.cadastro_policial_screen import CadastroPolicialScreen
from screens.extras_screen import ExtrasScreen
from screens.banco_extras import BancoExtrasScreen
from screens.permutas_screen import PermutasScreen
from screens.compensacoes_screen import CompensacoesScreen
from screens.consultar_compensacoes_screen import ConsultarCompensacoesScreen
from screens.cadastrar_compensacao_screen import CadastrarCompensacaoScreen
from screens.cadastrar_permuta_screen import CadastrarPermutaScreen
from screens.consultar_permutas_screen import ConsultarPermutasScreen
from screens.cadastrar_ferias_screen import CadastrarFeriasScreen
from screens.consultar_ferias_screen import ConsultarFeriasScreen
from screens.edicao_registros_screen import EdicaoRegistrosScreen
from screens.ferias_screen import FeriasScreen
from screens.ausencias_screen import AusenciasScreen
from screens.cadastrar_ausencias_screen import CadastrarAusenciasScreen
from screens.consultar_ausencias_screen import ConsultarAusenciasScreen
from screens.cadastrar_extra_screen import CadastrarExtraScreen
from screens.consultar_extras_screen import ConsultarExtrasScreen
from screens.disponibilidade_ferias_screen import DisponibilidadeFeriasScreen
from screens.disponibilidade_extras_screen import DisponibilidadeExtrasScreen
from screens.tac_screen import TacScreen
from screens.cadastrar_tac_screen import CadastrarTacScreen
from screens.consultar_tac_screen import ConsultarTacScreen
from screens.banco_dados_screen import BancoDadosScreen
from screens.import_db_screen import ImportDBScreen
from database.database_manager import DatabaseManager
from pathlib import Path
import os, sys, shutil, traceback, json, threading, time

APP_NAME = "Nuvig"
DB_NAME  = "nuvig.db"

# ==========================
# Configuração de AUTO-LOGOUT
# Ative/desative aqui e ajuste o horário (formato 24h HH:MM)
AUTO_LOGOUT_ENABLED = False
AUTO_LOGOUT_TIME = "22:30"  # EX.: "21:30" para 21h30
# ==========================

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
        self.output_dir: str | None = None
        self.is_authenticated = False  # Estado global de autenticação
        self.navbar = None  # Referência para atualizar navbar
        # Controle do auto-logout
        self._auto_logout_triggered: bool = False
        self._auto_logout_last_date = None  # type: ignore
        self._auto_logout_timer = None  # não usado com thread, mantido por compatibilidade
        self._auto_logout_thread = None
        
    def set_authenticated(self, authenticated: bool):
        """Define o estado de autenticação e atualiza a navbar"""
        self.is_authenticated = authenticated
        if self.navbar:
            self.navbar.update_auth_state(authenticated)
            
    def logout(self):
        """Realiza logout e volta para tela de login"""
        self.set_authenticated(False)
        # Navegar para login
        if hasattr(self, '_navigate_to_func'):
            self._navigate_to_func("login")

    def _hard_restart(self):
        """Tenta reiniciar o aplicativo (processo Python). Se falhar, faz logout simples."""
        try:
            py = sys.executable
            import subprocess
            # Inicia um novo processo e encerra o atual
            subprocess.Popen([py, *sys.argv])
            os._exit(0)
        except Exception as ex:
            #print(f"[AutoLogout] Hard restart falhou: {ex}. Fazendo logout simples.")
            self.logout()

    def _check_auto_logout(self):
        """Verifica horário configurado e realiza logout automático uma vez por dia."""
        try:
            from datetime import datetime, date, time as dt_time
            now = datetime.now()
            #print(f"[AutoLogout][Check] now={now.strftime('%Y-%m-%d %H:%M:%S')} (local time)")
            # Reset diário do gatilho
            if self._auto_logout_last_date != now.date():
                self._auto_logout_last_date = now.date()
                self._auto_logout_triggered = False
                #print("[AutoLogout][Check] Reset diário aplicado: _auto_logout_triggered=False")

            if self._auto_logout_triggered:
                return

            try:
                hh, mm = map(int, AUTO_LOGOUT_TIME.split(":"))
            except Exception:
                #print(f"[AutoLogout] Horário inválido em AUTO_LOGOUT_TIME='{AUTO_LOGOUT_TIME}'. Use HH:MM")
                return

            target = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
            #print(f"[AutoLogout][Check] target={target.strftime('%Y-%m-%d %H:%M:%S')} | triggered={self._auto_logout_triggered}")
            # Se a hora já passou no dia e ainda não disparou, dispara imediatamente
            if now >= target and not self._auto_logout_triggered:
                #print(f"[AutoLogout] Horário atingido ({AUTO_LOGOUT_TIME}). Executando auto-logout...")
                # 1) Limpa credenciais do banco para forçar re-login
                try:
                    self.db.execute_command("UPDATE roots SET path = NULL WHERE name = ?", ("credentials",))
                    #print("[AutoLogout] Credenciais limpas do banco com sucesso.")
                except Exception as dbex:
                    print(f"[AutoLogout] Falha ao limpar credenciais: {dbex}")

                # 2) Agendar ação de UI de logout no thread principal
                def _ui_action():
                    try:
                        print("[AutoLogout][UI] Executando logout e snackbar na UI thread...")
                        self.logout()
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("Sessão encerrada automaticamente pelo sistema."),
                            bgcolor=ft.Colors.ORANGE,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as uiex:
                        print(f"[AutoLogout][UI] Erro durante UI logout: {uiex}")

                try:
                    if hasattr(self, 'page') and hasattr(self.page, 'invoke_later'):
                        self.page.invoke_later(_ui_action)
                    else:
                        # Fallback: executa direto (pode funcionar dependendo do ambiente)
                        _ui_action()
                except Exception as invex:
                    print(f"[AutoLogout] Falha ao agendar ação de UI: {invex}")
                self._auto_logout_triggered = True
            else:
                print("[AutoLogout][Check] Condições não atendidas para logout automático neste tick.")
        except Exception as ex:
            print(f"[AutoLogout] Erro no verificador: {ex}")

    def _start_auto_logout_thread(self):
        if self._auto_logout_thread is not None:
            return
        print("[AutoLogout] Iniciando thread de monitoramento (intervalo=5s)...")
        def _worker():
            while True:
                try:
                    print(f"[AutoLogout][Tick-Thread] {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')} verificando...")
                    self._check_auto_logout()
                except Exception as ex:
                    print(f"[AutoLogout][Thread] Erro: {ex}")
                time.sleep(5)
        t = threading.Thread(target=_worker, name="AutoLogoutThread", daemon=True)
        t.start()
        self._auto_logout_thread = t
        
    def main(self, page: ft.Page):
        try:
            # Configurações da página
            self.page = page
            page.title = "NUVIG - Gestão"
            page.window.icon = os.path.abspath("assets/icons/nuvig.ico")
            page.window_width = 1792
            page.window_height = 1008
            page.window_resizable = True
            page.theme_mode = ft.ThemeMode.LIGHT
            page.padding = 0
            page.locale_configuration = ft.LocaleConfiguration(
                supported_locales=[
                    ft.Locale("pt", "BR"),  # Português do Brasil
                    ft.Locale("en", "US")   # Inglês como fallback
                ],
                current_locale=ft.Locale("pt", "BR")  # Define pt-BR como padrão
            )


            # Inicializar banco de dados
            self.db.init_database()
            # Limpar credenciais salvas a cada inicialização para exigir login manual
            try:
                self.db.execute_command("UPDATE roots SET path = NULL WHERE name = ?", ("credentials",))
                # Resetar estado de autenticação
                self.set_authenticated(False)
                print("[Init] Credenciais do Google limpas no início da aplicação.")
            except Exception as ex:
                print(f"[Init] Falha ao limpar credenciais no início: {ex}")

            # File picker para escolher diretório de saída (primeira execução)
            def _ensure_output_dir():
                try:
                    # 1) Buscar no banco (tabela roots, name='save_path')
                    existing = self.db.get_root_path("save_path")

                    if existing and os.path.isdir(existing):
                        self.output_dir = existing
                        print(f"[Init] Diretório de saída: {self.output_dir}")
                        return
                except Exception as ex:
                    print(f"[Init] Falha ao ler output_dir: {ex}")

                def on_pick_result(e: ft.FilePickerResultEvent):
                    try:
                        chosen = e.path or ""
                        if not chosen:
                            # fallback: Documents/Nuvig
                            docs = Path(os.path.expanduser("~")) / "Documents" / APP_NAME
                            docs.mkdir(parents=True, exist_ok=True)
                            chosen = str(docs)
                            page.snack_bar = ft.SnackBar(content=ft.Text(f"Pasta não selecionada. Usando padrão: {chosen}"))
                            page.snack_bar.open = True
                            page.update()
                        abs_path = str(Path(chosen).expanduser().resolve())
                        self.output_dir = abs_path
                        # Persistir no banco (tabela roots)
                        self.db.set_root_path("save_path", abs_path)
                        print(f"[Init] Diretório de saída definido: {abs_path}")
                    except Exception as ex2:
                        print(f"[Init] Erro ao definir output_dir: {ex2}")

                picker = ft.FilePicker(on_result=on_pick_result)
                page.overlay.append(picker)
                page.update()
                picker.get_directory_path(dialog_title="Selecione a pasta para salvar relatórios e arquivos do NUVIG")

            _ensure_output_dir()

            # Dicionário de telas
            self.screens = {
                "login": LoginScreen(self),
                "home": HomeScreen(self),
                "calendario": CalendarioScreen(self),
                "cadastro": CadastroScreen(self),
                "cadastro_policial": CadastroPolicialScreen(self),
                "extras": ExtrasScreen(self),
                "banco_extras": BancoExtrasScreen(self),
                "permutas": PermutasScreen(self),
                "compensacoes": CompensacoesScreen(self),
                "cadastrar_compensacao": CadastrarCompensacaoScreen(self),
                "consultar_compensacoes": ConsultarCompensacoesScreen(self),
                "cadastrar_permuta": CadastrarPermutaScreen(self),
                "consultar_permutas": ConsultarPermutasScreen(self),
                "edicao_registros": EdicaoRegistrosScreen(self),
                "ferias": FeriasScreen(self),
                "cadastrar_ferias": CadastrarFeriasScreen(self),
                "consultar_ferias": ConsultarFeriasScreen(self),
                "ausencias": AusenciasScreen(self),
                "cadastrar_extra": CadastrarExtraScreen(self),
                "consultar_extras": ConsultarExtrasScreen(self),
                "disponibilidade_ferias": DisponibilidadeFeriasScreen(self),
                "disponibilidade_extras": DisponibilidadeExtrasScreen(self),
                "cadastrar_ausencia": CadastrarAusenciasScreen(self),
                "consultar_ausencias": ConsultarAusenciasScreen(self),
                "tac": TacScreen(self),
                "cadastrar_tac": CadastrarTacScreen(self),
                "consultar_tac": ConsultarTacScreen(self),
                "banco_dados": BancoDadosScreen(self),
                "import_db": ImportDBScreen(self),
            }

            # Container para o conteúdo dinâmico
            content_container = ft.Container(
                expand=True,
                padding=20
            )

            # Função para navegar entre telas
            def navigate_to(screen_name: str):
                # Gate de autenticação: somente permite sair da tela de login se autenticado
                if screen_name != "login" and not self.is_authenticated:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Você precisa fazer login para acessar o sistema."),
                        bgcolor=ft.Colors.ORANGE,
                    )
                    page.snack_bar.open = True
                    # Garante que a tela de login permaneça ativa
                    self.current_screen = self.screens["login"]
                    content_container.content = self.current_screen.get_content()
                    page.update()
                    return

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

            # Armazenar referência do navigate_to para uso em logout
            self._navigate_to_func = navigate_to
            
            # Configurar navegação para cada tela
            for screen in self.screens.values():
                screen.set_navigation_callback(navigate_to)

            # Layout principal com navbar fixa
            from screens.navbar import NavBar

            self.navbar = NavBar(
                on_nav=navigate_to,
                selected_nav=None,
                authenticated=self.is_authenticated  # Inicialmente desabilitada
            )

            # Layout principal
            main_layout = ft.Column(
                controls=[
                    self.navbar,  # Navbar fixa
                    ft.Divider(height=1, color=ft.Colors.GREY),
                    content_container  # Container para conteúdo dinâmico
                ],
                spacing=0,
                expand=True
            )

            # Adicionar o layout principal à página
            page.add(main_layout)

            # Iniciar monitor de auto-logout (somente se habilitado) via thread
            if AUTO_LOGOUT_ENABLED:
                self._start_auto_logout_thread()

            # Iniciar com a tela de login
            navigate_to("login")

        except Exception as e:
            page.add(
                ft.Text("Erro ao iniciar o aplicativo:", color=ft.Colors.RED, size=18),
                ft.Text(str(e), selectable=True),
                ft.Text(traceback.format_exc(), selectable=True, size=12),
            )


if __name__ == "__main__":
    app = MainApp()
    ft.app(target=app.main, assets_dir="assets")
