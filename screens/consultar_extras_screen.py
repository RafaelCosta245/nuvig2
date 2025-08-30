import flet as ft
from .base_screen import BaseScreen

class ConsultarExtrasScreen(BaseScreen):
    def __init__(self, app_instance):
        super().__init__(app_instance)
        self.current_nav = "consultar_extras"

    def get_content(self) -> ft.Control:
        return ft.Column([
            ft.Text("Tela de Consulta de Extras Agendadas", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Text("Aqui você poderá consultar os extras agendados.")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
