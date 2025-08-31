import flet as ft
from .base_screen import BaseScreen

class HomeScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "home"
        
    def get_content(self) -> ft.Control:
        """Retorna apenas o conteúdo da tela (sem navbar)"""
        logo_img = ft.Image(
            src="assets/icons/logoNUVIG.png",
            width=360,
            height=360,
            fit=ft.ImageFit.CONTAIN,
        )
        content = ft.Container(
            content=ft.Column([
                logo_img,
                ft.Text(
                    "Bem-vindo ao Sistema NUVIG",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK,
                    text_align=ft.TextAlign.CENTER
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            expand=True
        )
        return content
