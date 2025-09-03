import flet as ft
from .base_screen import BaseScreen

class CadastrarCompensacaoScreen(BaseScreen):
	def __init__(self, app_instance):
		super().__init__(app_instance)
		self.current_nav = "cadastrar_compensacao"

	def get_content(self) -> ft.Control:
		# Função para buscar policial pela matrícula
		def buscar_policial(e):
			valor = matricula.value.strip()
			if valor:
				policial_info = self.app.db.get_policial_by_matricula(valor)
				if policial_info:
					policial.value = policial_info.get("qra", "")
					nome.value = policial_info.get("nome", "")
					# Pega a primeira letra da escala
					escala = policial_info.get("escala", "")
					equipe.value = escala[0] if escala else ""
				else:
					# Limpa os campos se não encontrar o policial
					policial.value = ""
					nome.value = ""
					equipe.value = ""
			else:
				# Limpa os campos se a matrícula estiver vazia
				policial.value = ""
				nome.value = ""
				equipe.value = ""
			e.control.page.update()

		# Campos do formulário
		matricula = ft.TextField(
			label="Matrícula", 
			width=200, 
			input_filter=ft.NumbersOnlyInputFilter(), 
			on_change=buscar_policial
		)
		policial = ft.TextField(label="QRA", width=200, read_only=True)
		nome = ft.TextField(label="Nome", width=200, read_only=True)
		equipe = ft.TextField(label="Equipe", width=200, read_only=True)
		data1 = ft.TextField(label="Compensação", width=200, hint_text="dd/mm/aaaa")
		data2 = ft.TextField(label="A compensar", width=200, hint_text="dd/mm/aaaa")

		import datetime
		# DatePicker para Data Inicial
		datepicker1 = ft.DatePicker(
			first_date=datetime.datetime(2020, 1, 1),
			last_date=datetime.datetime(2030, 12, 31),
		)
		def on_date1_change(e):
			if datepicker1.value:
				data1.value = datepicker1.value.strftime("%d/%m/%Y")
				data1.cursor_position = len(data1.value)
				e.control.page.update()
		datepicker1.on_change = on_date1_change
		def open_date_picker1(e):
			page = e.control.page
			if datepicker1 not in page.overlay:
				page.overlay.append(datepicker1)
				page.update()
			page.open(datepicker1)
		btn_data1 = ft.ElevatedButton(
			text="Compensação",
			icon=ft.Icons.CALENDAR_MONTH,
			color=ft.Colors.BLACK,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
			),
			width=matricula.width,
			height=matricula.height,
			on_click=open_date_picker1
		)
		
		# DatePicker para Data Final
		datepicker2 = ft.DatePicker(
			first_date=datetime.datetime(2020, 1, 1),
			last_date=datetime.datetime(2030, 12, 31),
		)
		def on_date2_change(e):
			if datepicker2.value:
				data2.value = datepicker2.value.strftime("%d/%m/%Y")
				data2.cursor_position = len(data2.value)
				e.control.page.update()
		datepicker2.on_change = on_date2_change
		def open_date_picker2(e):
			page = e.control.page
			if datepicker2 not in page.overlay:
				page.overlay.append(datepicker2)
				page.update()
			page.open(datepicker2)
		btn_data2 = ft.ElevatedButton(
			text="A compensar",
			icon=ft.Icons.CALENDAR_MONTH,
			color=ft.Colors.BLACK,
			style=ft.ButtonStyle(
				shape=ft.RoundedRectangleBorder(radius=8),
				side=ft.BorderSide(width=1, color=ft.Colors.BLACK)
			),
			width=matricula.width,
			height=matricula.height,
			on_click=open_date_picker2
		)

		form_grid = ft.Column([
			ft.Row([
				matricula, policial
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				nome, equipe
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				btn_data1, data1
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
			ft.Row([
				btn_data2, data2
			], spacing=32, alignment=ft.MainAxisAlignment.CENTER),
		], spacing=24, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

		# Botões (sem funcionalidade)
		btn_gravar = ft.ElevatedButton(
			text="Gravar",
			style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
			bgcolor=ft.Colors.BLUE,
			color=ft.Colors.WHITE
		)
		btn_limpar = ft.ElevatedButton(
			text="Limpar",
			style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
			bgcolor=ft.Colors.GREY,
			color=ft.Colors.WHITE
		)
		btn_row = ft.Row([
			btn_gravar,
			btn_limpar
		], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

		return ft.Column([
			ft.Text("Cadastrar Compensação", size=28, weight=ft.FontWeight.BOLD,
					color=ft.Colors.BLACK, text_align=ft.TextAlign.CENTER),
			ft.Container(height=20),
			form_grid,
			ft.Container(height=30),
			btn_row
		], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
