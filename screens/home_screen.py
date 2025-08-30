import flet as ft
from .base_screen import BaseScreen

class HomeScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "home"
        
    def get_content(self) -> ft.Control:
        """Retorna apenas o conteúdo da tela (sem navbar)"""
        # Página em branco
        content = ft.Container(
            content=ft.Text(
                "Bem-vindo ao Sistema NUVIG",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.BLUE,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            expand=True
        )
        
        return content
