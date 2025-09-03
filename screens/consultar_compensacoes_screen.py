import flet as ft
from .base_screen import BaseScreen

class ConsultarCompensacoesScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "consultar_compensacoes"

	def get_content(self) -> ft.Control:
		return ft.Container(
			content=ft.Text(
				"Tela de Consulta de Compensações",
				size=24,
				color=ft.Colors.BLACK,
				weight=ft.FontWeight.BOLD,
				text_align=ft.TextAlign.CENTER
			),
			alignment=ft.alignment.center,
			expand=True
		)
