import flet as ft
from .base_screen import BaseScreen

class FeriasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "ferias"

    def get_content(self) -> ft.Control:
        return ft.Column([
            ft.Text("Tela de Férias", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Text("Conteúdo básico de férias.")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
