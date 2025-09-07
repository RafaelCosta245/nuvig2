from dataclasses import field

import flet as ft
from .base_screen import BaseScreen

class BancoExtrasScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "banco_extras"

	def get_content(self) -> ft.Control:
		# Dimensões padrão para os campos
		field_width = 250
		field_height = 50

		header = ft.Container(
			content=ft.Text(
				"Banco de Extras",
				size=28,
				color=ft.Colors.BLACK,
				weight=ft.FontWeight.BOLD,
				text_align=ft.TextAlign.CENTER
			),
			padding=ft.padding.only(bottom=20),
			alignment=ft.alignment.center
		)

		row1 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='O que você deseja?', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				ft.Dropdown(
					label="Add/Remover",
					width=field_width,
					#height=field_height,
					options=[ft.dropdown.Option("Adicionar Horas"), ft.dropdown.Option("Remover Horas")]
				)
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

		row2 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='Quantidade de horas:', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				ft.TextField(
					label="Quant. horas",
					width=field_width,
					height=field_height,
					input_filter=ft.InputFilter(
						allow=True, # Permite apenas o que matches o regex
						regex_string=r"^[0-9]*$", # Aceita apenas dígitos (0-9), zero ou mais vezes
						replacement_string="" # Remove caracteres inválidos
					)
				)
			],
			alignment=ft.MainAxisAlignment.CENTER
		)


		row3 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='Intertício:', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				ft.TextField(
					label="Ex.: ago/set-25",
					width=field_width,
					height=field_height,
					)
				],
			alignment=ft.MainAxisAlignment.CENTER
		)

		row4 = ft.Row(controls=[
			ft.Container(
				content=ft.Text(value='Operação:', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
				width=field_width,
				height=field_height,
				alignment=ft.alignment.center
			),
			ft.Dropdown(
				label="Operação",
				width=field_width,
				# height=field_height,
				options=[ft.dropdown.Option("Rotina"),
						 ft.dropdown.Option("OBLL"),
						 ft.dropdown.Option("Outro")])
			],
			alignment=ft.MainAxisAlignment.CENTER)


		# Botão Salvar centralizado
		btn_row = ft.ElevatedButton(
            text="Salvar Alterações",
            icon=ft.Icons.SAVE,
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
            ),
            #on_click=self.salvar_alteracoes,
            visible=True
		)

		return ft.Container(
			content=ft.Column(
				controls=[header,
						  row1,
						  row2,
						  row3,
						  row4,
						  ft.Container(height=10),
						  btn_row],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				alignment=ft.MainAxisAlignment.START,
				spacing=15
			),
			alignment=ft.alignment.center,
			expand=True
		)
