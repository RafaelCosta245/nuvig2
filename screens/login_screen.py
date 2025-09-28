import flet as ft
from .base_screen import BaseScreen
from database.database_manager import DatabaseManager


class LoginScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "login"
        self.db = DatabaseManager()

    def _show_alert_dialog(self, page: ft.Page, mensagem: str, success: bool = True, on_close=None):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sucesso" if success else "Erro", color=ft.Colors.GREEN if success else ft.Colors.RED),
            content=ft.Text(mensagem),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e: (page.close(dlg), on_close(e) if callable(on_close) else None),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg.on_dismiss = lambda e: (on_close(e) if callable(on_close) else None)
        page.open(dlg)

    def _perform_login(self, page: ft.Page, loader_container: ft.Container):
        """Executa o processo de login: verifica credentials salvas primeiro, se inválidas abre navegador"""
        try:
            loader_container.content = ft.ProgressRing()
            loader_container.update()
            
            # Primeiro: verifica se existem credentials no banco
            existing = self.db.get_google_credentials('credentials')
            
            if existing:
                # Tenta autenticação silenciosa com credentials salvas
                print("[LOGIN] Tentando autenticação com credentials salvas...")
                from utils.google_drive_utils import is_drive_authenticated
                if is_drive_authenticated():
                    print("[LOGIN] Autenticação silenciosa bem-sucedida")
                    self.app.set_authenticated(True)
                    self._show_alert_dialog(page, "Login realizado com sucesso!", success=True, 
                                          on_close=lambda _: self.navigate_to("home"))
                    return True
                else:
                    print("[LOGIN] Credentials salvas são inválidas, abrindo navegador...")
            else:
                print("[LOGIN] Nenhuma credential salva, abrindo navegador...")
            
            # Se chegou aqui, precisa abrir o navegador para autenticação
            from utils.google_drive_utils import authenticate_google_drive
            authenticate_google_drive()  # Abre o navegador para autenticação
            
            # Sucesso: define como autenticado e navega
            self.app.set_authenticated(True)
            self._show_alert_dialog(page, "Login concluído com sucesso!", success=True, 
                                  on_close=lambda _: self.navigate_to("home"))
            return True
            
        except Exception as ex:
            print(f"[LOGIN] Erro de autenticação: {ex}")
            self._show_alert_dialog(page, f"Erro ao autenticar: {str(ex)}", success=False)
            return False
        finally:
            try:
                loader_container.content = None
                loader_container.update()
            except Exception:
                pass

    def get_content(self) -> ft.Control:
        page = self.app.page

        # Loader
        loader = ft.Container(width=50, height=50, alignment=ft.alignment.center)

        # Título e subtítulo no estilo da Home
        logo_img = ft.Image(
            src="assets/icons/logoNUVIG.png",
            width=260,
            height=260,
            fit=ft.ImageFit.CONTAIN,
        )

        title = ft.Text(
            "Bem-vindo ao Sistema NUVIG",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLACK,
            text_align=ft.TextAlign.CENTER,
        )

        subtitle = ft.Text(
            "Faça login para continuar",
            size=18,
            color=ft.Colors.BLACK,
            text_align=ft.TextAlign.CENTER,
        )

        # Ícones/branding do Google (usa Row com ícone colorido)
        google_brand = ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.CIRCLE, color="#4285F4", size=14),
                ft.Icon(name=ft.Icons.CIRCLE, color="#DB4437", size=14),
                ft.Icon(name=ft.Icons.CIRCLE, color="#F4B400", size=14),
                ft.Icon(name=ft.Icons.CIRCLE, color="#0F9D58", size=14),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        # Texto informativo
        info_text = ft.Text(
            "Entrar com o Google",
            size=24,
            color=ft.Colors.BLACK,
            text_align=ft.TextAlign.CENTER,
        )

        # Ação de login
        def do_login(e):
            # Resolve page do evento
            pg = getattr(e, "page", None) or page
            self._perform_login(pg, loader)

        # Botão de login com estilo semelhante aos botões da Home
        btn_login = ft.ElevatedButton(
            text="Continuar com Google",
            icon=ft.Icons.LOGIN,
            bgcolor=ft.Colors.WHITE,
            color=ft.Colors.BLACK,
            width=240,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                side=ft.BorderSide(2, ft.Colors.BLACK),
            ),
            on_click=do_login,
        )

        # Layout da tela
        content = ft.Container(
            content=ft.Column(
                [
                    logo_img,
                    title,
                    ft.Container(height=8),
                    subtitle,
                    ft.Container(height=24),
                    google_brand,
                    ft.Container(height=8),
                    info_text,
                    ft.Container(height=16),
                    btn_login,
                    ft.Container(height=24),
                    loader,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )

        return content

