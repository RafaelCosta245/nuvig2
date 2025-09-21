import flet as ft
from .base_screen import BaseScreen


class HomeScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.app_instance = app_instance
		self.current_nav = "home"

	def get_content(self) -> ft.Control:
		def abrir_email(e):
			self.app_instance.page.launch_url("http://webmail.sap.ce.gov.br/")

		def abrir_suite(e):
			self.app_instance.page.launch_url("http://suite.ce.gov.br")

		def abrir_sigepen(e):
			self.app_instance.page.launch_url("http://sigepen.sap.ce.gov.br/login")

		def abrir_guardiao(e):
			self.app_instance.page.launch_url("https://guardiaov4.seplag.ce.gov.br/auth")

		"""Retorna apenas o conteúdo da tela (sem navbar)"""
		logo_img = ft.Image(
			src="assets/icons/logoNUVIG.png",
			width=360,
			height=360,
			fit=ft.ImageFit.CONTAIN,
		)

		links_text = ft.Text(
			value="Links úteis",
			size=28,
			color=ft.Colors.BLACK,
			text_align=ft.TextAlign.CENTER
		)

		btn_email = ft.ElevatedButton(
			text="E-mail institucional",
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.BLACK,
			width=200,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(2, ft.Colors.BLACK)),
			on_click=abrir_email
		)

		btn_sigepen = ft.ElevatedButton(
			text="SIGEPEN",
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.BLACK,
			width=btn_email.width,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(2, ft.Colors.BLACK)),
			on_click=abrir_sigepen
		)

		btn_guardiao = ft.ElevatedButton(
			text="Guardião",
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.BLACK,
			width=btn_email.width,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(2, ft.Colors.BLACK)),
			on_click=abrir_guardiao
		)

		btn_suite = ft.ElevatedButton(
			text="Suíte",
			bgcolor=ft.Colors.WHITE,
			color=ft.Colors.BLACK,
			width=btn_email.width,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(2, ft.Colors.BLACK)),
			on_click=abrir_suite
		)

		row_btn = ft.Row(
			controls=[btn_email, btn_sigepen, btn_guardiao, btn_suite],
			alignment=ft.MainAxisAlignment.CENTER,
			spacing=20
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
				),
				ft.Container(height=30),
				links_text,
				ft.Container(height=10),
				row_btn,
			],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				alignment=ft.MainAxisAlignment.START),
			alignment=ft.alignment.center,
			expand=True
		)
		return content