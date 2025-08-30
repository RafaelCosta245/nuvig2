import flet as ft
from .base_screen import BaseScreen

class AusenciasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "ausencias"

    def get_content(self) -> ft.Control:
        return ft.Column([
            ft.Text("Tela de Ausencias", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Text("Conteúdo básico de ausencias.")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
