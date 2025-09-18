from dataclasses import field

import flet as ft
from .base_screen import BaseScreen


class BancoDadosScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "banco_dados"

	def get_content(self) -> ft.Control:
		# Dimensões padrão para os campos
		field_width = 250
		field_height = 50

		header = ft.Container(
			content=ft.Text(
				"Banco de Dados",
				size=28,
				color=ft.Colors.BLACK,
				weight=ft.FontWeight.BOLD,
				text_align=ft.TextAlign.CENTER
			),
			padding=ft.padding.only(bottom=20),
			alignment=ft.alignment.center
		)

		dropdown_operacao = ft.Dropdown(
			label="Add/Remover",
			width=field_width,
			options=[ft.dropdown.Option("Adicionar Horas"), ft.dropdown.Option("Remover Horas")]
		)
		row1 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='O que você deseja?', text_align=ft.TextAlign.CENTER,
									weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				dropdown_operacao
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

		textfield_horas = ft.TextField(
			label="Quant. horas",
			width=field_width,
			height=field_height,
			input_filter=ft.InputFilter(
				allow=True,
				regex_string=r"^[0-9]*$",
				replacement_string=""
			)
		)
		row2 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='Quantidade de horas:', text_align=ft.TextAlign.CENTER,
									weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				textfield_horas
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

		textfield_interticio = ft.TextField(
			label="Ex.: ago/set-25",
			width=field_width,
			height=field_height,
			on_change=lambda e: buscar_horas_disponiveis()
		)
		row3 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='Intertício:', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				textfield_interticio
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

		dropdown_tipo = ft.Dropdown(
			label="Operação",
			width=field_width,
			options=[ft.dropdown.Option("Rotina"), ft.dropdown.Option("OBLL"), ft.dropdown.Option("Outro")],
			on_change=lambda e: buscar_horas_disponiveis()
		)
		row4 = ft.Row(
			controls=[
				ft.Container(
					content=ft.Text(value='Operação:', text_align=ft.TextAlign.CENTER, weight=ft.FontWeight.BOLD),
					width=field_width,
					height=field_height,
					alignment=ft.alignment.center
				),
				dropdown_tipo
			],
			alignment=ft.MainAxisAlignment.CENTER
		)

		# Containers para mostrar horas disponíveis
		horas_disp_text = ft.Container(
			content=ft.Text(
				value="Horas disponíveis:",
				text_align=ft.TextAlign.CENTER,
				weight=ft.FontWeight.BOLD,
				size=14,
				color=ft.Colors.BLACK
			),
			width=field_width,
			# height=field_height,
			alignment=ft.alignment.center,
			# bgcolor=ft.Colors.BLUE
		)

		horas_disp_number = ft.Container(
			content=ft.Text(
				value="0 horas",
				text_align=ft.TextAlign.CENTER,
				weight=ft.FontWeight.BOLD,
				size=14,
				color=ft.Colors.BLACK
			),
			width=field_width,
			# height=field_height,
			alignment=ft.alignment.center,
			# bgcolor=ft.Colors.ORANGE
		)

		row5 = ft.Row(
			controls=[horas_disp_text, horas_disp_number],
			alignment=ft.MainAxisAlignment.CENTER
		)

		from dialogalert import show_alert_dialog

		def buscar_horas_disponiveis():
			"""Busca e soma as horas disponíveis para o intertício e tipo selecionados"""
			try:
				valor_interticio = textfield_interticio.value
				tipo = dropdown_tipo.value

				if not valor_interticio or not tipo:
					# Resetar valores se campos não estiverem preenchidos
					horas_disp_text.content.value = "Horas disponíveis:"
					horas_disp_number.content.value = "0 horas"
					horas_disp_number.content.color = ft.Colors.BLACK
					if hasattr(self.app, 'page') and self.app.page:
						self.app.page.update()
					return

				# Buscar id do interticio
				query_interticio = "SELECT id FROM interticios WHERE nome = ?"
				result_interticio = self.app.db.execute_query(query_interticio, (valor_interticio,))

				if not result_interticio:
					# Intertício não encontrado
					horas_disp_text.content.value = f"Horas disponíveis para {valor_interticio}:"
					horas_disp_number.content.value = "Intertício não encontrado"
					horas_disp_number.content.color = ft.Colors.RED
					if hasattr(self.app, 'page') and self.app.page:
						self.app.page.update()
					return

				interticio_id = result_interticio[0]["id"]

				# Buscar e somar horas
				query_horas = "SELECT SUM(qty_horas) as total_horas FROM horasextras WHERE interticio_id = ? AND tipo = ?"
				result_horas = self.app.db.execute_query(query_horas, (interticio_id, tipo))

				if result_horas and result_horas[0]["total_horas"] is not None:
					total_horas = result_horas[0]["total_horas"]
				else:
					total_horas = 0

				# Atualizar textos
				horas_disp_text.content.value = f"Horas disponíveis para {valor_interticio}:"
				horas_disp_number.content.value = f"{total_horas} horas"
				horas_disp_number.content.color = ft.Colors.BLACK if total_horas >= 0 else ft.Colors.RED

				# Atualizar a tela
				if hasattr(self.app, 'page') and self.app.page:
					self.app.page.update()

			except Exception as ex:
				print(f"Erro ao buscar horas: {ex}")
				horas_disp_text.content.value = "Erro ao buscar horas"
				horas_disp_number.content.value = "Erro"
				horas_disp_number.content.color = ft.Colors.RED
				if hasattr(self.app, 'page') and self.app.page:
					self.app.page.update()

		def mostrar_alerta(sucesso=True, mensagem=""):
			if hasattr(self.app, 'page') and self.app.page:
				show_alert_dialog(self.app.page, mensagem, sucesso)
			else:
				# Fallback para snackbar se o page não estiver disponível
				if sucesso:
					self.show_success(mensagem)
				else:
					self.show_error(mensagem)

		def salvar_alteracoes(e):
			try:
				valor_operacao = dropdown_operacao.value
				valor_horas = textfield_horas.value
				valor_interticio = textfield_interticio.value
				tipo = dropdown_tipo.value

				if not valor_operacao or not valor_horas or not valor_interticio or not tipo:
					mostrar_alerta(False, "Preencha todos os campos!")
					return

				# Determina valor positivo ou negativo
				qty_horas = int(valor_horas)
				if "Remover" in valor_operacao:
					qty_horas = -qty_horas

				# Buscar id do interticio
				query = "SELECT id FROM interticios WHERE nome = ?"
				result = self.app.db.execute_query(query, (valor_interticio,))
				if not result:
					mostrar_alerta(False, "Intertício não encontrado!")
					return
				interticio_id = result[0]["id"]

				# Data atual dd/mm/aaaa
				from datetime import datetime
				data_entrada = datetime.now().strftime("%d/%m/%Y")

				# Inserir na tabela horasextras
				command = "INSERT INTO horasextras (qty_horas, interticio_id, tipo, data_entrada) VALUES (?, ?, ?, ?)"
				sucesso = self.app.db.execute_command(command, (qty_horas, interticio_id, tipo, data_entrada))

				if sucesso:
					mostrar_alerta(True, "Dados salvos com sucesso!")
					# Atualizar as horas disponíveis após salvar
					buscar_horas_disponiveis()
				else:
					mostrar_alerta(False, "Erro ao salvar no banco!")
			except Exception as ex:
				mostrar_alerta(False, f"Erro: {ex}")

		btn_row = ft.ElevatedButton(
			text="Salvar Alterações",
			width=150,
			bgcolor=ft.Colors.WHITE,
			style=ft.ButtonStyle(
				color=ft.Colors.GREEN,
				text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(1, ft.Colors.GREEN)),
			icon=ft.Icons.SAVE,
			on_click=salvar_alteracoes,
			visible=True
		)

		return ft.Container(
			content=ft.Column(
				controls=[header,
						  row1,
						  row2,
						  row3,
						  row4,
						  # row5,
						  ft.Container(height=10),
						  btn_row,
						  ft.Container(height=10),
						  horas_disp_text,
						  horas_disp_number],
				horizontal_alignment=ft.CrossAxisAlignment.CENTER,
				alignment=ft.MainAxisAlignment.START,
				spacing=15
			),
			alignment=ft.alignment.center,
			expand=True
		)
