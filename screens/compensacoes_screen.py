import flet as ft
from .base_screen import BaseScreen

class CompensacoesScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "compensacoes"

    def get_content(self) -> ft.Control:
        content = ft.Container(
            content=ft.Text(
                "Bem-vindo à tela de Compensações",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        return content


