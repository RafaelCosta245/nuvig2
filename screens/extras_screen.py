import flet as ft
from .base_screen import BaseScreen

class ExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "extras"
        
    def get_content(self) -> ft.Control:
        return ft.Container(
            content=ft.Text(
                "Bem-vindo à tela de Extras",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )


