import flet as ft
from .base_screen import BaseScreen

class PermutasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "permutas"
        
    def get_content(self) -> ft.Control:
        header = ft.Container(
            content=ft.Text("Permutas", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE, text_align=ft.TextAlign.CENTER),
            padding=ft.padding.only(bottom=30),
            alignment=ft.alignment.center
        )
        body = ft.Container(
            content=ft.Text("Bem-vindo à tela de Permutas", size=16, color=ft.Colors.GREY),
            padding=ft.padding.all(20),
            border=ft.border.all(1, ft.Colors.GREY),
            border_radius=8,
            bgcolor=ft.Colors.GREY_100,
            width=400
        )
        return ft.Column(controls=[header, body], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO)


